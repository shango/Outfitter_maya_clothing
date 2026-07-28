"""Registering a rig from a live Maya scene - the capture half of rig-agnosticism.

The artist drops a new rig into a scene, opens the Publish tab and hits **Register rig**.
This module reads that scene and produces a complete :class:`core.rigs.RigProfile`: which
group holds the export skeleton, the ``cloth_*`` rest skeleton captured from it, the
per-garment-type skin sets derived from its joint names, how the rig switches body
variants, and the marker nodes that identify it in a scene later. It then copies the rig
``.ma`` into the shared rig repo (``<remote>/_rigs/<rig_id>/``) so every other artist can
fetch it on demand, and writes the profile beside it.

Everything here is a *suggestion the user confirms* - candidate export groups are ranked,
not chosen; the variant switch is name-matched, not divined. The dialog (task 8) presents
what this module found and lets the user correct it before anything is written.

Lazy ``maya.cmds``; runs only inside Maya. The pure halves it delegates to - profile
model and file I/O (:mod:`core.rigs`), skin-set derivation (:mod:`core.skin_sets`),
skeleton model (:mod:`core.skeleton`) - are headless-tested; this module gathers the live
facts and is ``py_compile``d like the rest of the Maya boundary.
"""
from __future__ import annotations

import datetime
import getpass
from dataclasses import dataclass, replace
from pathlib import Path

from . import maya_skeleton as _mskel
from . import rigs as _rigs
from . import settings as _settings
from . import skin_sets as _skin_sets


def _cmds():
    import maya.cmds as cmds  # type: ignore

    return cmds


def _namespace_of(path: str) -> str:
    """Namespace token of a DAG path's leaf, or ``""`` at the root namespace."""
    leaf = path.rsplit("|", 1)[-1]
    return leaf.split(":", 1)[0] if ":" in leaf else ""


# --------------------------------------------------------------------------- #
# Finding the export skeleton
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class ExportGroupCandidate:
    """A transform in the scene that could be a rig's export-skeleton group."""

    path: str          # full DAG path, e.g. "|GenHuman|GenHuman_Joint_GRP"
    name: str          # short name without namespace - what the profile stores
    joint_count: int   # joints anywhere below it
    root_joint: str    # short name of its first direct child joint
    namespace: str = ""

    @property
    def label(self) -> str:
        """``"GenHuman_Joint_GRP (89 joints, root: root)"`` - the dropdown entry."""
        return (f"{self.name} ({self.joint_count} joints, root: {self.root_joint})"
                + (f" [{self.namespace}]" if self.namespace else ""))


def candidate_export_groups() -> list[ExportGroupCandidate]:
    """Every group in the scene that directly parents a joint, best guess first.

    The export skeleton is the joint hierarchy a garment binds to, and on every rig the
    tool has seen it hangs under a plain transform (GenHuman's ``GenHuman_Joint_GRP``).
    Rather than guess by name - which is exactly the hard-coding being removed - this
    lists the structural candidates and lets the user pick.

    Ranked by: the current selection's namespace first (the user selects the rig they mean
    when several are in the scene), then most joints, then path. A rig with a separate
    internal deform skeleton therefore offers both, with the bigger export group on top.
    """
    cmds = _cmds()
    selection = cmds.ls(selection=True, long=True) or []
    sel_ns = _namespace_of(selection[0]) if selection else None

    out: list[ExportGroupCandidate] = []
    for grp in (cmds.ls(exactType="transform", long=True) or []):
        children = cmds.listRelatives(grp, children=True, type="joint", fullPath=True) or []
        if not children:
            continue
        descendants = cmds.listRelatives(
            grp, allDescendents=True, type="joint", fullPath=True) or []
        out.append(ExportGroupCandidate(
            path=grp,
            name=_mskel._short(grp),
            joint_count=len(descendants),
            root_joint=_mskel._short(children[0]),
            namespace=_namespace_of(grp),
        ))

    out.sort(key=lambda c: (
        sel_ns is not None and c.namespace != sel_ns, -c.joint_count, c.path))
    return out


def suggested_markers(candidate: ExportGroupCandidate,
                      variant_node: str = "") -> tuple[str, ...]:
    """Node names that identify this rig in a scene later (export group + landmarks).

    The markers are how the tool answers "is this rig in the scene, and at what version"
    without importing anything. The export group is always one; the rig's top-level DAG
    root (``GenHuman`` above ``GenHuman_Joint_GRP``) and the node carrying the variant
    switch are added when they exist, so detection survives one of them being renamed.
    """
    cmds = _cmds()
    markers = [candidate.name]
    top = next((p for p in candidate.path.split("|") if p), "")
    top_short = top.rsplit(":", 1)[-1]
    if top_short and top_short != candidate.name:
        markers.append(top_short)
    if variant_node and variant_node not in markers:
        markers.append(variant_node)
    # Drop anything that has since vanished, so a profile never ships a dead marker.
    return tuple(m for m in markers if cmds.objExists(m) or cmds.ls(f"*:{m}"))


# --------------------------------------------------------------------------- #
# Body-variant switch
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class VariantCandidate:
    """An attribute that looks like it drives the rig's body variant (male/female)."""

    node: str            # short name without namespace - what the profile stores
    attr: str
    minimum: float = 0.0
    maximum: float = 1.0

    @property
    def label(self) -> str:
        return f"{self.node}.{self.attr} ({self.minimum:g} - {self.maximum:g})"

    def as_variants(self, low: str = "female", high: str = "male") -> _rigs.Variants:
        """Build the profile's :class:`~core.rigs.Variants` from this switch.

        Which end of the range is which body is *not* discoverable - the defaults follow
        GenHuman's convention (female = base, male = full morph, verified in Maya
        2026-06-24). The Register dialog shows the mapping so the user can swap it.
        """
        return _rigs.Variants(
            mode=_rigs.VARIANT_MORPH, node=self.node, attr=self.attr,
            values={low: self.minimum, high: self.maximum},
        )


def _attr_range(cmds, node: str, attr: str) -> tuple[float, float]:
    """``(min, max)`` of a numeric attribute, defaulting to ``(0, 1)`` when unbounded."""
    lo, hi = 0.0, 1.0
    try:
        if cmds.attributeQuery(attr, node=node, minExists=True):
            lo = float(cmds.attributeQuery(attr, node=node, minimum=True)[0])
        if cmds.attributeQuery(attr, node=node, maxExists=True):
            hi = float(cmds.attributeQuery(attr, node=node, maximum=True)[0])
    except Exception:  # noqa: BLE001 - non-numeric or odd attr: keep the 0-1 default
        pass
    return lo, hi


def detect_variant_switches() -> list[VariantCandidate]:
    """Attributes in the scene that plausibly switch the body variant, best guess first.

    Scans the rig's controls (transforms only - the switch is always on an animatable
    control, never on a shape) for user-defined keyable attributes whose *name* reads like
    a body switch (:func:`core.rigs.looks_like_variant_attr`). Name matching is the only
    signal available; a rig whose switch is named unguessably is simply configured by
    hand, and a rig with a single body has none at all.
    """
    cmds = _cmds()
    found: list[VariantCandidate] = []
    seen: set[tuple[str, str]] = set()
    for node in (cmds.ls(exactType="transform", long=True) or []):
        attrs = cmds.listAttr(node, userDefined=True, keyable=True) or []
        for attr in attrs:
            if "." in attr or not _rigs.looks_like_variant_attr(attr):
                continue  # skip compound children; keep the parent attr only
            short = _mskel._short(node)
            key = (short, attr)
            if key in seen:
                continue
            seen.add(key)
            lo, hi = _attr_range(cmds, node, attr)
            found.append(VariantCandidate(node=short, attr=attr, minimum=lo, maximum=hi))

    # "morph" is the strongest signal (GenHuman's GH_Body_morph); the rest sort by name so
    # the order is stable between runs.
    found.sort(key=lambda c: (0 if "morph" in c.attr.lower() else 1, c.node, c.attr))
    return found


# --------------------------------------------------------------------------- #
# The rig file itself
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class RigSource:
    """Where the rig in this scene came from on disk, and how confident that is."""

    path: Path
    origin: str  # "reference" (definitely the rig) | "scene" (the open file - confirm it)

    @property
    def label(self) -> str:
        where = ("referenced into this scene" if self.origin == "reference"
                 else "the currently open scene")
        return f"{self.path.name} ({where})"


def rig_source_file(node: str = "") -> RigSource | None:
    """The rig ``.ma`` to copy into the rig repo, or ``None`` if it can't be determined.

    A referenced rig knows its own file, which is the reliable case. Otherwise the open
    scene is offered as a candidate - right when the user opened the rig itself to
    register it, wrong when they imported the rig into a garment scene - so the origin is
    reported and the dialog asks the user to confirm or browse. An imported rig in an
    unsaved scene yields ``None``: there is nothing honest to copy.
    """
    cmds = _cmds()
    if node:
        try:
            if cmds.referenceQuery(node, isNodeReferenced=True):
                path = cmds.referenceQuery(node, filename=True, withoutCopyNumber=True)
                return RigSource(Path(path), "reference")
        except Exception:  # noqa: BLE001 - not referenced, or a node type that can't be
            pass
    scene = cmds.file(query=True, sceneName=True) or ""
    return RigSource(Path(scene), "scene") if scene else None


# --------------------------------------------------------------------------- #
# Capture + register
# --------------------------------------------------------------------------- #
def capture_profile(
    rig_id: str,
    display_name: str,
    version: str,
    export_group: str | None = None,
    *,
    variants: _rigs.Variants | None = None,
    markers: tuple[str, ...] = (),
    author: str = "",
    rig_file: str = "",
) -> _rigs.RigProfile:
    """Build a complete rig profile from the rig currently in the scene.

    ``export_group`` is the group's short name (from :func:`candidate_export_groups`);
    with none given the top-ranked candidate is used. The skeleton is captured at the
    rig's *current* pose, so the rig must be at bind/rest - same requirement the existing
    'Regenerate skeleton' action has always had.

    Skin sets are derived from the captured joint names (:func:`core.skin_sets.
    derive_skin_sets`) and stored in the profile, where a rigger can correct them by hand.
    Nothing is written to disk - see :func:`register_rig`.
    """
    cmds = _cmds()
    rig_id = _rigs.sanitize_rig_id(rig_id)

    if export_group is None:
        candidates = candidate_export_groups()
        if not candidates:
            raise RuntimeError(
                "No export skeleton found in this scene: no group has a joint directly "
                "under it. Import the rig you want to register, then try again.")
        export_group = candidates[0].name

    root_joint, export_grp = _mskel._find_export_root(cmds, export_group)
    spec = _mskel.capture_skeleton_spec(cmds, root_joint, export_grp)
    if not spec.joints:
        raise RuntimeError(
            f"'{export_group}' has no joints to capture. Pick the group that holds the "
            "rig's export skeleton.")

    if not markers:
        candidate = ExportGroupCandidate(
            path=export_grp, name=export_group, joint_count=len(spec.joints),
            root_joint=_mskel._short(root_joint), namespace=_namespace_of(export_grp))
        markers = suggested_markers(candidate, variants.node if variants else "")

    profile = _rigs.RigProfile(
        rig_id=rig_id,
        display_name=display_name.strip() or rig_id,
        version=version.strip(),
        export_group=export_group,
        skeleton=spec,
        markers=markers,
        variants=variants or _rigs.Variants(),
        skin_sets=_skin_sets.derive_skin_sets(spec.names),
        rig_file=rig_file,
        author=author.strip() or _default_author(),
        created=datetime.date.today().isoformat(),
    )
    errors = _rigs.validate_profile(profile)
    if errors:
        raise RuntimeError(
            "This rig can't be registered yet:\n  " + "\n  ".join(errors))
    return profile


def _default_author() -> str:
    try:
        return getpass.getuser()
    except Exception:  # noqa: BLE001 - no login name available; not worth failing over
        return ""


@dataclass
class RegisterResult:
    profile: _rigs.RigProfile
    profile_paths: list[Path]   # every _rigs folder the profile was written to
    rig_file_paths: list[Path]  # every library the rig .ma was installed into
    warnings: list[str]

    def summary(self) -> str:
        p = self.profile
        types = len(p.skin_sets)
        msg = (
            f"Registered {p.label}: {len(p.skeleton.joints)} joints captured, skin sets "
            f"derived for {types} garment type{'' if types == 1 else 's'}. "
            f"Profile written to {len(self.profile_paths)} librar"
            f"{'y' if len(self.profile_paths) == 1 else 'ies'}.")
        if self.rig_file_paths:
            msg += f" Rig file installed as {p.rig_file}."
        for warning in self.warnings:
            msg += f" {warning}"
        return msg


def register_rig(
    rig_id: str,
    display_name: str,
    version: str,
    export_group: str | None = None,
    *,
    variants: _rigs.Variants | None = None,
    markers: tuple[str, ...] = (),
    author: str = "",
    rig_source: Path | str | None = None,
    make_active: bool = True,
    progress=None,
) -> RegisterResult:
    """Capture the rig, publish it to the rig repo, and make it the active rig.

    The whole registration in one call:

    1. capture the profile (:func:`capture_profile`) - fails fast on an unusable rig,
       *before* any 30 MB copy;
    2. copy ``rig_source`` into ``<remote>/_rigs/<rig_id>/`` (the shared rig repo every
       other artist fetches from) and into the local library too, so the artist who
       registered it never downloads back their own upload;
    3. write the profile into both ``_rigs`` folders - remote so Sync distributes it,
       local so this Maya session can use the rig immediately without a sync;
    4. select the rig, so the next publish targets it.

    ``progress`` is an optional ``callable(copied, total)`` for the rig-file copy. A rig
    registered with no ``rig_source`` is perfectly usable for authoring and attaching -
    it just has no test body to load.
    """
    profile = capture_profile(
        rig_id, display_name, version, export_group,
        variants=variants, markers=markers, author=author)

    loc = _settings.read_locations()
    local = loc.local or _settings.effective_library_roots()[0]
    warnings: list[str] = []
    if loc.remote is None:
        warnings.append(
            "No remote library is configured, so this rig is registered on this machine "
            "only - set the remote folder on the Setup tab and register again to share it.")

    # Remote first: it is the copy other artists fetch, and the one worth failing on.
    roots = [r for r in (loc.remote, local) if r is not None]
    rig_file_paths: list[Path] = []
    if rig_source is not None:
        rel = ""
        for root in roots:
            rel = _rigs.install_rig_file(profile.rig_id, rig_source, root, progress)
            rig_file_paths.append(Path(root) / rel)
        profile = replace(profile, rig_file=rel)

    profile_paths = [_rigs.write_profile(profile, _rigs.library_rigs_dir(root))
                     for root in roots]

    if make_active:
        _settings.set_rig(profile.rig_id)

    return RegisterResult(
        profile=profile, profile_paths=profile_paths,
        rig_file_paths=rig_file_paths, warnings=warnings)
