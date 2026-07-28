"""In-scene skinning test - drive the ``cloth_*`` skeleton from the body (Maya-side).

The rigger hits **Load test body**: the tool references in the active rig's body, switches
it to the garment's chosen variant (GenHuman flips ``GH_Body_morph``; female = base, male
= morph), aligns the garment's ``Rig_GRP`` to the rig's export frame, and ``connectAttr``s
each body joint's ``{translate,rotate,scale}`` onto the matching ``cloth_*`` joint -
exactly production attach, in-scene. They pose the body's controls, confirm the mesh
follows, then hit **Remove test body** to disconnect and delete the rig so the joints go
static and the asset is publish-safe again. (``connect_test_body`` /
``disconnect_test_body`` are the connect/disconnect halves, also usable on a body the
rigger placed themselves.)

Which body, where it lives and how its variants switch all come from the registered rig
profile (:mod:`core.rigs`), so this works for a rig the tool has never seen. The rig file
itself is fetched from the shared library on first use - it is deliberately not synced.

Lazy ``maya.cmds``; runs only inside Maya. The pure plan (matching + skip rules)
lives in :mod:`core.testfit` and is headless-tested; this module gathers the live
facts, applies the plan, and is ``py_compile``d like the rest of the Maya boundary.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .. import config
from . import maya_skeleton as _mskel
from . import rigs as _rigs
from . import settings as _settings
from . import testfit as _testfit
from .attach import sanitize_namespace


def _cmds():
    import maya.cmds as cmds  # type: ignore

    return cmds


@dataclass
class ConnectResult:
    connected: int
    matched: int
    unmatched: list[str]
    skipped_locked: int
    skipped_driven: int

    def summary(self) -> str:
        msg = (
            f"Test body connected: driving {self.matched} cloth_* joint(s) from the "
            f"rig body ({self.connected} channel connection(s)).")
        skips = []
        if self.skipped_driven:
            skips.append(f"{self.skipped_driven} already-driven")
        if self.skipped_locked:
            skips.append(f"{self.skipped_locked} locked")
        if skips:
            msg += f" Skipped {', '.join(skips)} channel(s)."
        return msg + " Pose the body's controls and confirm the garment deforms."


@dataclass
class DisconnectResult:
    broken: int
    joints: list[str]

    def summary(self) -> str:
        n = len(self.joints)
        return (
            f"Test body disconnected: broke {self.broken} connection(s) on {n} "
            f"cloth_* joint{'' if n == 1 else 's'}. The joints are static again and "
            "the asset is publish-safe.")


@dataclass
class LoadBodyResult:
    gender: str
    morph: float | None      # None when the rig has a single body or a per-variant file
    connect: ConnectResult
    rig_label: str = ""
    switch: str = ""         # "node.attr" that was driven, when the rig switches by morph
    namespace: str = ""      # namespace the body was referenced under

    def summary(self) -> str:
        body = f"Loaded the {self.gender} {self.rig_label} body".rstrip()
        if self.morph is not None and self.switch:
            body += f" ({self.switch} = {self.morph:g})"
        return body + ". " + self.connect.summary()


@dataclass
class RemoveBodyResult:
    deleted: int
    disconnect: DisconnectResult

    def summary(self) -> str:
        return (
            self.disconnect.summary()
            + f" Removed the test body ({self.deleted} node group(s) deleted).")


def _scene_cloth_nodes(cmds) -> dict[str, str]:
    """``{short cloth name: full DAG path}`` for every ``cloth_*`` joint in the scene."""
    return {
        _mskel._short(j): j
        for j in (cmds.ls(f"{config.CLOTH_PREFIX}*", type="joint", long=True) or [])
    }


def _body_joints(cmds, export_grp: str) -> dict[str, str]:
    """``{short body name: full DAG path}`` for every joint under the export group."""
    joints = cmds.listRelatives(
        export_grp, allDescendents=True, type="joint", fullPath=True) or []
    return {_mskel._short(j): j for j in joints}


def _align_rig_group(cmds, export_grp: str) -> None:
    """Match the garment's ``Rig_GRP`` world frame to the export group's.

    Attach connects only LOCAL transforms, so the garment's joint group must share the
    export group's world frame or the connected joints reproduce in the wrong frame and
    the garment lands rotated off the body (see ``attach._align_root_group``). Best-effort
    - if either group is missing the connections still drive, just possibly off-frame.
    """
    # Rig_GRP is a transform group, not a joint, so match by name across any namespace.
    matches = cmds.ls(config.RIG_GROUP, long=True) or cmds.ls(
        f"*:{config.RIG_GROUP}", long=True) or []
    rig_group = matches[0] if matches else None
    if not rig_group:
        return
    try:
        m = cmds.xform(export_grp, query=True, worldSpace=True, matrix=True)
        cmds.xform(rig_group, worldSpace=True, matrix=m)
    except Exception:  # noqa: BLE001 - alignment is best-effort, never abort the connect
        pass


def connect_test_body(mesh_group: str = "Mesh_GRP",
                      profile: _rigs.RigProfile | None = None) -> ConnectResult:
    """Drive the in-scene ``cloth_*`` skeleton from the rig body for a skinning test.

    Locates the rig's export-skeleton group already in the scene, aligns the garment's
    ``Rig_GRP`` to its frame, then connects each body joint's TRS onto the matching
    ``cloth_<base>`` joint. Already-driven or locked plugs are skipped so the call is
    idempotent and never steals an existing connection. Raises clearly if there's no cloth
    skeleton (build it first) or no body in the scene (nothing to drive from). ``profile``
    defaults to the rig the user is working with.
    """
    cmds = _cmds()

    cloth_nodes = _scene_cloth_nodes(cmds)
    if not cloth_nodes:
        raise RuntimeError(
            "No cloth_* joints in the scene. Run 'Create cloth skeleton' first.")

    # _find_export_root raises a clear "rig not found" if the body is absent.
    export_group = profile.export_group if profile is not None else None
    _root_joint, export_grp = _mskel._find_export_root(cmds, export_group)
    body_joints = _body_joints(cmds, export_grp)
    if not body_joints:
        raise RuntimeError(
            f"Export group '{_mskel._short(export_grp)}' has no joints to drive from.")

    _align_rig_group(cmds, export_grp)

    # Probe each candidate cloth plug's live state for the pure planner.
    locked: set[str] = set()
    driven: set[str] = set()
    for node in cloth_nodes.values():
        for attr in config.CONNECT_ATTRS:
            plug = f"{node}.{attr}"
            try:
                if cmds.getAttr(plug, lock=True):
                    locked.add(plug)
                elif cmds.connectionInfo(plug, isDestination=True):
                    driven.add(plug)
            except Exception:  # noqa: BLE001 - a missing attr just isn't connected
                pass

    plan = _testfit.plan_test_fit(
        cloth_nodes, body_joints, locked=locked, driven=driven)

    connected = 0
    for conn in plan.connections:
        try:
            cmds.connectAttr(conn.src, conn.dst, force=False)
            connected += 1
        except Exception:  # noqa: BLE001 - skip a plug Maya refuses, keep going
            pass

    cmds.select(clear=True)
    return ConnectResult(
        connected=connected,
        matched=len(plan.matched_joints),
        unmatched=list(plan.unmatched_joints),
        skipped_locked=sum(1 for s in plan.skipped if s.reason == "locked"),
        skipped_driven=sum(1 for s in plan.skipped if s.reason == "driven"),
    )


def disconnect_test_body() -> DisconnectResult:
    """Break the test-body connections so the ``cloth_*`` joints go static again.

    Walks every ``cloth_*`` joint and disconnects any incoming ``{translate,rotate,
    scale}`` connection whose source is *outside* the cloth skeleton (i.e. a body
    joint) - exactly the edges :func:`connect_test_body` makes. Idempotent and tolerant
    of already-broken edges, so it's safe to run before publishing even if nothing is
    connected.
    """
    cmds = _cmds()
    broken = 0
    touched: list[str] = []
    for short, node in _scene_cloth_nodes(cmds).items():
        joint_touched = False
        for attr in config.CONNECT_ATTRS:
            dst = f"{node}.{attr}"
            try:
                src = cmds.connectionInfo(dst, sourceFromDestination=True)
            except Exception:  # noqa: BLE001
                src = ""
            if not src:
                continue
            # only break body-driven edges; never touch a cloth-internal connection
            if _mskel._short(src).startswith(config.CLOTH_PREFIX):
                continue
            try:
                cmds.disconnectAttr(src, dst)
                broken += 1
                joint_touched = True
            except Exception:  # noqa: BLE001 - best-effort; a stubborn edge isn't fatal
                pass
        if joint_touched:
            touched.append(short)
    cmds.select(clear=True)
    return DisconnectResult(broken=broken, joints=touched)


def _rig_present(cmds, markers: tuple[str, ...]) -> bool:
    """True if a rig (any of its marker nodes) is already in the scene."""
    for marker in markers:
        if cmds.objExists(marker) or cmds.ls(f"*:{marker}"):
            return True
    return False


def _set_body_morph(cmds, gender: str, variants: _rigs.Variants) -> tuple[float, str]:
    """Drive the rig's variant switch to ``gender``; return ``(value on the rig, plug)``.

    Reads the morph back after setting it, so the caller reports what the body is *really*
    at - not just what we asked for. Tolerates a genuinely-absent node/attr (returns the
    requested value), but if the plug exists and the set silently doesn't take (the attr is
    locked or driven by the rig), the read-back exposes that instead of masking it.
    """
    value = _testfit.body_morph_value(gender, variants)
    # Resolve the switch node whether referenced at root or under a namespace.
    node = variants.node
    if not cmds.objExists(node):
        matches = cmds.ls(f"*:{variants.node}") or []
        node = matches[0] if matches else node
    plug = f"{node}.{variants.attr}"
    if not cmds.objExists(plug):
        return value, plug  # attr genuinely absent - nothing to set or read back
    try:
        cmds.setAttr(plug, value)
    except Exception:  # noqa: BLE001 - locked/driven; the read-back below tells the truth
        pass
    try:
        return float(cmds.getAttr(plug)), plug
    except Exception:  # noqa: BLE001
        return value, plug


def load_test_body(gender: str, mesh_group: str = "Mesh_GRP",
                   profile: _rigs.RigProfile | None = None,
                   progress=None) -> LoadBodyResult:
    """Reference in the active rig's body, switch it to ``gender``, and connect it.

    The rig profile says which body to load and how to switch variants: GenHuman ships one
    rig and sets ``GH_Body_morph`` (female = base, male = full morph), while another rig
    may keep one file per variant, or a single body with no variants at all. Either way the
    rigger skins and poses the garment against the correct body without hand-importing one.

    The body file is fetched from the shared library on first use (rig ``.ma`` files are
    not synced - see :func:`core.rigs.ensure_rig_file`), which can take a while over a
    share, so ``progress`` is passed straight through to the copy and callers should run
    this off the UI thread.

    Refuses if that rig is already in the scene (avoid a double body) or if there's no
    cloth skeleton to drive. After loading it sets the variant then runs
    :func:`connect_test_body`.

    The body is brought in as a *file reference* (not an import) so that 'Remove test body'
    can drop it with ``removeReference`` - which deletes every node it brought in, including
    leftover selection sets, plus its namespace, leaving zero remnants for publish. (An
    import has to be torn down by name-sweeping, which strands sets and blocks publish.)
    Downstream matching is namespace-insensitive (see ``maya_skeleton._short`` /
    ``_find_export_root``), so the rig living under its own namespace is transparent.
    """
    cmds = _cmds()
    if profile is None:
        profile = _rigs.resolve_profile()
    if profile is None:
        raise RuntimeError(
            "No rig is registered, so there is no test body to load. Use 'Register rig' "
            "on the Publish tab first.")

    if not _scene_cloth_nodes(cmds):
        raise RuntimeError(
            "No cloth_* joints in the scene. Run 'Create cloth skeleton' first.")
    if _rig_present(cmds, profile.markers):
        raise RuntimeError(
            f"A {profile.label} rig is already in the scene. Use 'Remove test body' (or "
            "delete it) before loading a fresh body.")

    variants = profile.variants
    # A per-variant-file rig needs the right file fetched; a morph rig has just the one.
    variant = gender if variants.mode == _rigs.VARIANT_FILES else ""
    loc = _settings.read_locations()
    local = loc.local or _settings.effective_library_roots()[0]
    body_file = _rigs.ensure_rig_file(profile, local, loc.remote, variant, progress)

    # Reference (don't import) under the file-stem namespace, e.g. 'GenHuman_rig_v03' - this
    # carries the version token so detect_rig_version still reads it, and removeReference
    # later wipes the rig cleanly. _short strips the namespace, so the cloth_<base> -> body
    # <base> match and the switch-attr path still resolve as connect expects.
    namespace = sanitize_namespace(body_file.stem)
    cmds.file(str(body_file), reference=True, namespace=namespace)

    morph: float | None = None
    switch = ""
    if variants.mode == _rigs.VARIANT_MORPH:
        morph, switch = _set_body_morph(cmds, gender, variants)

    connect = connect_test_body(mesh_group, profile)
    return LoadBodyResult(
        gender=gender.strip().lower(), morph=morph, connect=connect,
        rig_label=profile.label, switch=switch, namespace=namespace)


def _rig_file_stems(profile: _rigs.RigProfile) -> tuple[str, ...]:
    """Filename stems of every body file this rig can load (bundled, shared, per-variant).

    A reference is matched by its *filename*, so this is what identifies "the rig's own
    reference" no matter which variant was loaded or where it was fetched from.
    """
    names = [profile.rig_file, profile.bundled_file, *profile.variants.files.values()]
    return tuple({Path(n).stem for n in names if n})


def _remove_rig_references(cmds, profile: _rigs.RigProfile) -> int:
    """Drop any file reference belonging to this rig; returns how many were removed.

    ``removeReference`` deletes every node the reference brought in - joints, shaders,
    utility nodes *and selection sets* - and removes its now-empty namespace, so nothing
    is stranded to trip the publish "rig still in scene" gate. Reference nodes are matched
    by their referenced filename so this survives a save/reopen (we don't rely on a handle
    captured at load time). Best-effort per reference; a stubborn one never blocks the rest.
    """
    needles = [*_rig_file_stems(profile), *profile.markers]
    removed = 0
    for ref in (cmds.ls(type="reference") or []):
        try:
            filename = cmds.referenceQuery(ref, filename=True)
        except Exception:  # noqa: BLE001 - e.g. an unloaded/own-scene reference node
            continue
        if not any(needle in filename for needle in needles):
            continue
        try:
            cmds.file(removeReference=True, referenceNode=ref)
            removed += 1
        except Exception:  # noqa: BLE001 - keep going; the name-sweep fallback covers leftovers
            pass
    return removed


def _delete_rig(cmds, profile: _rigs.RigProfile) -> int:
    """Robustly delete an *imported* rig; returns how many top nodes were removed.

    A rig is ~thousands of DG 'guts' nodes plus DAG roots. Delete the DAG roots first
    (cascades to children), then sweep any leftover marker-named DG nodes, tolerating
    failures throughout (a stubborn node must never block the rest). Only the rig's own
    markers are swept, so a rig registered with sloppy markers can't take the garment with
    it.
    """
    deleted = 0
    # DAG roots whose name marks the rig (its export group, godnode, top group...).
    roots: list[str] = []
    for marker in profile.markers:
        roots += cmds.ls(marker, long=True) or []
        roots += cmds.ls(f"*{marker}*", long=True, type="transform", recursive=True) or []
    for node in sorted(set(roots), key=len, reverse=True):
        if not cmds.objExists(node):
            continue
        try:
            cmds.delete(node)
            deleted += 1
        except Exception:  # noqa: BLE001 - keep deleting the rest
            pass
    # Sweep stray rig-named DG nodes left behind (materials/utility/etc.).
    for marker in profile.markers:
        for node in (cmds.ls(f"*{marker}*", recursive=True) or []):
            if cmds.objExists(node):
                try:
                    cmds.delete(node)
                except Exception:  # noqa: BLE001
                    pass
    return deleted


def remove_test_body(profile: _rigs.RigProfile | None = None) -> RemoveBodyResult:
    """Disconnect the test body and remove the rig so publish isn't blocked.

    Pairs with :func:`load_test_body`: first breaks the body->cloth connections
    (:func:`disconnect_test_body`), then removes the rig. The body is removed by dropping
    its file reference (:func:`_remove_rig_references`), which wipes every node it brought
    in - including selection sets - leaving no remnants. A scene where the rig was
    *imported* (no reference) falls back to the name-sweep delete. The count returned is
    references removed plus any swept import nodes. Idempotent - safe to run with nothing
    loaded (it just reports zero).
    """
    cmds = _cmds()
    disc = disconnect_test_body()
    if profile is None:
        profile = _rigs.resolve_profile()
    deleted = 0
    if profile is not None:
        deleted = _remove_rig_references(cmds, profile)
        deleted += _delete_rig(cmds, profile)  # fallback: sweep an imported rig
    cmds.select(clear=True)
    return RemoveBodyResult(deleted=deleted, disconnect=disc)
