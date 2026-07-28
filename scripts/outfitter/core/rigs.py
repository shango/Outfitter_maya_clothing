"""Registered rig profiles - what makes the tool rig-agnostic (pure, headless-testable).

The tool used to hard-code one rig (GenHuman): its export-skeleton group name, its
marker nodes, its gender morph switch, its ``cloth_*`` skeleton, and the per-garment-type
skin sets built from its joint names. All of that now lives in a **rig profile** - one
JSON file per registered rig - so a studio can drop a new rig into a scene, register it
from the Publish tab, and author and attach clothing against it with no code change.

A profile is self-contained: identity, how to find the rig in a scene, how to switch body
variants, the captured ``cloth_*`` rest skeleton, and the recommended skin joints per
garment type. Everything the rest of the tool needs to work with a rig it has never seen.

Where profiles live, in load precedence order::

    <library root>/_rigs/<rig_id>.json    registered rigs, distributed by Sync
    <package>/data/rigs/<rig_id>.json     the bundled GenHuman profile (fallback)

A library-root profile wins over the bundled one of the same id, so a studio can revise
the shipped GenHuman profile without touching the install.

**Rig files are deliberately not part of Sync.** A rig ``.ma`` is 25-30 MB; pulling every
registered rig to every artist on every sync would be wasteful, and most artists work with
one rig at a time. Sync carries the small ``*.json`` profiles; the ``.ma`` itself sits in
``<remote>/_rigs/<rig_id>/`` and is fetched on demand the first time it is actually needed
(see :func:`rig_file_status` and the fetch helpers). ``rig_file`` on a profile is stored
library-relative so it resolves against either root.

Pure logic: filesystem + json only, no Maya. The Maya boundary (:mod:`core.maya_rigs`)
captures a profile from a live scene; this module owns the model and all profile file I/O.
"""
from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path

from .. import config
from . import skeleton as _skeleton
from . import settings as _settings

# Folder name, under a library root, holding rig profiles and rig files. Skipped by the
# asset scanner (a rig .ma is not a garment) and treated specially by Sync.
RIGS_DIRNAME: str = "_rigs"
PROFILE_EXT: str = ".json"

# The rig every pre-existing asset and install implicitly targeted. An asset sidecar with
# no ``rigId`` is read as this rig, which is what makes the change backward-compatible.
DEFAULT_RIG_ID: str = "genhuman"

# --- body-variant switching modes --------------------------------------------
# How a rig exposes its male/female (or other) body variants, if it has any at all.
#   "none"  - a single body; assets for this rig carry no gender.
#   "morph" - one rig, one attribute drives the variant (GenHuman's GH_Body_morph).
#   "files" - a separate rig file per variant.
VARIANT_NONE: str = "none"
VARIANT_MORPH: str = "morph"
VARIANT_FILES: str = "files"
VARIANT_MODES: tuple[str, ...] = (VARIANT_NONE, VARIANT_MORPH, VARIANT_FILES)

_ID_INVALID = re.compile(r"[^a-z0-9_]")

# Attribute names that plausibly drive a body variant, checked when registering a rig so
# the Register dialog can prefill the switch rather than making the user hunt for it. A
# guess to confirm, never an authority - the user can always pick the node/attr by hand.
_VARIANT_ATTR_RE = re.compile(
    r"(morph|gender|sex|male|female|body[_-]?type|body[_-]?shape)", re.IGNORECASE)

_PROFILE_COMMENT = (
    "Outfitter rig profile. Written by the Publish tab's 'Register rig' action "
    "(see core.maya_rigs.capture_profile); regenerate rather than hand-editing the "
    "skeleton transforms. skinSets and jointAliases are safe to edit by hand."
)


def sanitize_rig_id(name: str) -> str:
    """A filesystem- and key-safe rig id from arbitrary text (``"Acme Biped" -> "acme_biped"``)."""
    cleaned = _ID_INVALID.sub("_", name.strip().lower()).strip("_")
    cleaned = re.sub(r"_{2,}", "_", cleaned)
    if cleaned and cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned or "rig"


def looks_like_variant_attr(attr: str) -> bool:
    """True when an attribute name reads like a body-variant switch (``GH_Body_morph``).

    Used at registration to prefill the variant switch from the rig in the scene. Name
    matching is all that is available - nothing about a float attribute says "this is the
    gender control" - so the result is a suggestion the user confirms, and a rig whose
    switch is named something unguessable is set up by hand instead.
    """
    return bool(_VARIANT_ATTR_RE.search(attr.rsplit(".", 1)[-1]))


@dataclass(frozen=True)
class Variants:
    """How a rig switches between body variants (male/female), if it does at all.

    ``values`` maps a variant name to the morph attribute value that selects it;
    ``files`` maps a variant name to a library-relative rig file. Only the mapping for
    the declared :attr:`mode` is meaningful - the other is empty.
    """

    mode: str = VARIANT_NONE
    node: str = ""                                          # morph: node carrying the attr
    attr: str = ""                                          # morph: the driving attribute
    values: dict[str, float] = field(default_factory=dict)  # morph: variant -> value
    files: dict[str, str] = field(default_factory=dict)     # files: variant -> rig .ma

    @property
    def names(self) -> tuple[str, ...]:
        """The variant names this rig offers, or ``()`` when it has a single body."""
        if self.mode == VARIANT_MORPH:
            return tuple(self.values)
        if self.mode == VARIANT_FILES:
            return tuple(self.files)
        return ()

    @property
    def is_gendered(self) -> bool:
        """True when the rig offers a choice of bodies (drives the UI's Gender field)."""
        return bool(self.names)

    def value_for(self, variant: str) -> float | None:
        """The morph value selecting ``variant``, or ``None`` if not a morph rig."""
        if self.mode != VARIANT_MORPH:
            return None
        return self.values.get(variant.strip().lower())


@dataclass(frozen=True)
class RigProfile:
    """One registered rig: everything the tool needs to author and attach clothing for it.

    Frozen for the same reason the rest of ``core`` is - a profile is loaded data, not
    mutable state. (The two mapping fields are shallow-frozen; treat them as read-only.)
    """

    rig_id: str
    display_name: str
    version: str
    export_group: str                 # short name of the group holding the export skeleton
    skeleton: _skeleton.SkeletonSpec  # the captured cloth_* rest skeleton
    markers: tuple[str, ...] = ()     # node short names that identify this rig in a scene
    variants: Variants = field(default_factory=Variants)
    # asset type -> recommended cloth_* skin joints, derived at registration (core.skin_sets)
    skin_sets: dict[str, tuple[str, ...]] = field(default_factory=dict)
    # old cloth_* joint name -> this rig's cloth_* joint name; fills the gaps exact-name
    # matching leaves when retargeting an asset from another rig (core.retarget).
    joint_aliases: dict[str, str] = field(default_factory=dict)
    rig_file: str = ""                # library-relative, e.g. "_rigs/acme/acme_v01.ma"
    # A rig file shipped inside the package's own lib/ dir instead of the library. Only
    # the bundled GenHuman uses this (it has always shipped with the installer); it keeps
    # rig-file resolution data-driven rather than special-casing that one rig id.
    bundled_file: str = ""
    author: str = ""
    created: str = ""
    source: Path | None = None        # the file it was loaded from (None if constructed)

    @property
    def label(self) -> str:
        """``"GenHuman v03"`` - how a rig is named in dropdowns and messages."""
        return f"{self.display_name} {self.version}".strip()

    @property
    def joint_names(self) -> tuple[str, ...]:
        """Every ``cloth_*`` joint name in this rig's skeleton."""
        return self.skeleton.names

    def skin_set(self, asset_type: str) -> tuple[str, ...]:
        """Recommended skin joints for ``asset_type`` (empty when none were derived)."""
        return self.skin_sets.get(asset_type, ())

    def supports_version(self, version: str) -> bool:
        return version.strip() == self.version.strip()


# --------------------------------------------------------------------------- #
# Serialization
# --------------------------------------------------------------------------- #
def _variants_from_json(data: dict) -> Variants:
    mode = str(data.get("mode", VARIANT_NONE)).strip().lower() or VARIANT_NONE
    values = {
        str(k).strip().lower(): float(v)
        for k, v in (data.get("values") or {}).items()
    }
    files = {
        str(k).strip().lower(): str(v)
        for k, v in (data.get("files") or {}).items()
    }
    return Variants(
        mode=mode,
        node=str(data.get("node", "")).strip(),
        attr=str(data.get("attr", "")).strip(),
        values=values,
        files=files,
    )


def _variants_to_json(variants: Variants) -> dict:
    out: dict[str, object] = {"mode": variants.mode}
    if variants.mode == VARIANT_MORPH:
        out.update({"node": variants.node, "attr": variants.attr,
                    "values": dict(variants.values)})
    elif variants.mode == VARIANT_FILES:
        out["files"] = dict(variants.files)
    return out


def from_json_dict(data: dict, source: Path | None = None) -> RigProfile:
    """Build a :class:`RigProfile` from the on-disk JSON shape.

    Lenient about absent optional blocks (a rig with no variants, no skin sets, no rig
    file is still a usable profile); :func:`validate_profile` is what judges a profile fit
    for use. Raises ``KeyError``/``ValueError`` only on structurally unusable input.
    """
    skin_sets = {
        str(k): tuple(str(j) for j in (v or ()))
        for k, v in (data.get("skinSets") or {}).items()
    }
    aliases = {
        str(k): str(v) for k, v in (data.get("jointAliases") or {}).items()
    }
    return RigProfile(
        rig_id=str(data["rigId"]).strip(),
        display_name=str(data.get("displayName", "")).strip() or str(data["rigId"]).strip(),
        version=str(data.get("version", "")).strip(),
        export_group=str(data.get("exportGroup", "")).strip(),
        skeleton=_skeleton.from_json_dict(data.get("skeleton") or {"joints": []}),
        markers=tuple(str(m).strip() for m in (data.get("markers") or ()) if str(m).strip()),
        variants=_variants_from_json(data.get("variants") or {}),
        skin_sets=skin_sets,
        joint_aliases=aliases,
        rig_file=str(data.get("rigFile", "")).strip(),
        bundled_file=str(data.get("bundledFile", "")).strip(),
        author=str(data.get("author", "")).strip(),
        created=str(data.get("created", "")).strip(),
        source=source,
    )


def to_json_dict(profile: RigProfile) -> dict:
    """Serialize a :class:`RigProfile` to its on-disk JSON shape (inverse of the loader).

    ``source`` is deliberately not written - it records where a profile came from, which
    is a property of the load, not of the rig.
    """
    return {
        "_comment": _PROFILE_COMMENT,
        "rigId": profile.rig_id,
        "displayName": profile.display_name,
        "version": profile.version,
        "exportGroup": profile.export_group,
        "markers": list(profile.markers),
        "rigFile": profile.rig_file,
        "bundledFile": profile.bundled_file,
        "author": profile.author,
        "created": profile.created,
        "variants": _variants_to_json(profile.variants),
        "skinSets": {k: list(v) for k, v in profile.skin_sets.items()},
        "jointAliases": dict(profile.joint_aliases),
        "skeleton": _skeleton.to_json_dict(profile.skeleton),
    }


# --------------------------------------------------------------------------- #
# Validation
# --------------------------------------------------------------------------- #
def validate_profile(profile: RigProfile) -> list[str]:
    """Problems that would stop a profile being usable (empty list ⇒ OK).

    Checked before a profile is written, so a half-captured rig never lands in the shared
    library, and available to the UI so a bad hand-edit is reported rather than silently
    producing broken skeletons.
    """
    errors: list[str] = []

    if not profile.rig_id:
        errors.append("missing 'rigId'")
    elif sanitize_rig_id(profile.rig_id) != profile.rig_id:
        errors.append(
            f"rigId {profile.rig_id!r} is not a safe id "
            f"(expected {sanitize_rig_id(profile.rig_id)!r}: lower-case, digits, underscore)")
    if not profile.display_name:
        errors.append("missing 'displayName'")
    if not profile.version:
        errors.append("missing 'version'")
    if not profile.export_group:
        errors.append("missing 'exportGroup' - the group holding the rig's export skeleton")
    if not profile.markers:
        errors.append("missing 'markers' - at least one node name identifying this rig in a scene")

    if not profile.skeleton.joints:
        errors.append("skeleton has no joints - capture it from the rig in a scene")
    else:
        errors.extend(f"skeleton: {e}" for e in _skeleton.validate_skeleton(profile.skeleton))

    errors.extend(_validate_variants(profile.variants))
    errors.extend(_validate_skin_sets(profile))

    if profile.rig_file:
        rig_path = Path(profile.rig_file)
        if rig_path.is_absolute():
            errors.append(
                f"rigFile {profile.rig_file!r} must be library-relative, not an absolute path")
        elif rig_path.parts[:1] != (RIGS_DIRNAME,):
            errors.append(
                f"rigFile {profile.rig_file!r} must live under {RIGS_DIRNAME}/")

    return errors


def _validate_variants(variants: Variants) -> list[str]:
    errors: list[str] = []
    if variants.mode not in VARIANT_MODES:
        errors.append(
            f"variants.mode {variants.mode!r} not one of {', '.join(VARIANT_MODES)}")
        return errors
    if variants.mode == VARIANT_MORPH:
        if not variants.node:
            errors.append("variants: morph mode needs a 'node' carrying the switch attribute")
        if not variants.attr:
            errors.append("variants: morph mode needs an 'attr' to drive")
        if not variants.values:
            errors.append("variants: morph mode needs at least one variant -> value entry")
    elif variants.mode == VARIANT_FILES:
        if not variants.files:
            errors.append("variants: files mode needs at least one variant -> rig file entry")
        for variant, rel in variants.files.items():
            if Path(rel).is_absolute():
                errors.append(
                    f"variants.files[{variant}] must be library-relative, not an absolute path")
    return errors


def _validate_skin_sets(profile: RigProfile) -> list[str]:
    errors: list[str] = []
    known_joints = set(profile.joint_names)
    for asset_type, joints in profile.skin_sets.items():
        if asset_type not in config.ASSET_TYPES:
            errors.append(
                f"skinSets: unknown asset type {asset_type!r} "
                f"(known: {', '.join(config.ASSET_TYPES)})")
        stray = [j for j in joints if j not in known_joints]
        if stray:
            head = ", ".join(sorted(stray)[:5])
            more = "" if len(stray) <= 5 else f" (+{len(stray) - 5} more)"
            errors.append(
                f"skinSets[{asset_type}]: {len(stray)} joint(s) not in this rig's "
                f"skeleton: {head}{more}")
    return errors


# --------------------------------------------------------------------------- #
# Discovery + file I/O
# --------------------------------------------------------------------------- #
def bundled_rigs_dir() -> Path:
    """The profiles shipped inside the package (the GenHuman fallback)."""
    return config.package_dir() / "data" / "rigs"


def library_rigs_dir(root: Path | str) -> Path:
    """The ``_rigs`` folder under a library root."""
    return Path(root) / RIGS_DIRNAME


def profile_dirs(roots: list[Path] | None = None) -> list[Path]:
    """Folders searched for profiles, highest precedence first.

    The user's library roots come first so a studio-registered rig overrides a bundled
    profile of the same id; the package's own ``data/rigs`` is the last resort.
    """
    if roots is None:
        roots = _settings.effective_library_roots()
    return [library_rigs_dir(r) for r in roots] + [bundled_rigs_dir()]


def _read_profile_file(path: Path) -> RigProfile | None:
    """Load one profile file, or ``None`` if it is unreadable/not a profile.

    Never raises: a stray or half-written JSON file in a shared ``_rigs`` folder must not
    stop the tool listing the rigs that *are* valid.
    """
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(raw, dict) or not str(raw.get("rigId", "")).strip():
        return None
    try:
        return from_json_dict(raw, source=path)
    except (KeyError, TypeError, ValueError):
        return None


def list_profiles(roots: list[Path] | None = None) -> list[RigProfile]:
    """Every registered rig, de-duplicated by id with the highest-precedence copy winning.

    Sorted by display label so the UI order is stable. Unreadable files are skipped
    silently - :func:`validate_profile` is where a caller judges a profile it loaded.
    """
    found: dict[str, RigProfile] = {}
    for directory in profile_dirs(roots):
        if not directory.is_dir():
            continue
        for path in sorted(directory.glob(f"*{PROFILE_EXT}")):
            profile = _read_profile_file(path)
            if profile is not None and profile.rig_id not in found:
                found[profile.rig_id] = profile
    return sorted(found.values(), key=lambda p: p.label.lower())


def load_profile(rig_id: str, roots: list[Path] | None = None) -> RigProfile:
    """Load one rig profile by id. Raises ``LookupError`` when no such rig is registered."""
    for directory in profile_dirs(roots):
        path = directory / f"{rig_id}{PROFILE_EXT}"
        if path.is_file():
            profile = _read_profile_file(path)
            if profile is not None:
                return profile
    known = ", ".join(p.rig_id for p in list_profiles(roots)) or "(none)"
    raise LookupError(f"no registered rig {rig_id!r}; known rigs: {known}")


def find_profile(rig_id: str, roots: list[Path] | None = None) -> RigProfile | None:
    """:func:`load_profile` that returns ``None`` instead of raising."""
    try:
        return load_profile(rig_id, roots)
    except LookupError:
        return None


def resolve_profile(rig_id: str | None = None,
                    roots: list[Path] | None = None) -> RigProfile | None:
    """The profile to work with, in order: ``rig_id``, the user's saved rig, the default
    rig, then any registered rig.

    Used wherever the tool needs *a* rig - the Maya-side actions call it with no argument
    and get whatever the user last selected. Each fallback covers a real situation: a
    saved rig that has since been removed from the library, a library with no GenHuman in
    it, a fresh install. ``None`` only when nothing at all is registered, which the UI
    reports rather than guessing around.
    """
    for candidate in (rig_id, _settings.active_rig_id(), DEFAULT_RIG_ID):
        if candidate:
            profile = find_profile(candidate, roots)
            if profile is not None:
                return profile
    available = list_profiles(roots)
    return available[0] if available else None


def write_profile(profile: RigProfile, dest_dir: Path | str) -> Path:
    """Write ``profile`` to ``<dest_dir>/<rig_id>.json``; returns the path.

    Validated first - an incomplete capture is never published into a shared library,
    where it would break every artist who synced it.
    """
    errors = validate_profile(profile)
    if errors:
        raise ValueError(
            "refusing to write an invalid rig profile:\n  " + "\n  ".join(errors))
    directory = Path(dest_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"{profile.rig_id}{PROFILE_EXT}"
    path.write_text(json.dumps(to_json_dict(profile), indent=1) + "\n", encoding="utf-8")
    return path


# --------------------------------------------------------------------------- #
# Rig file location (the .ma itself - fetched on demand, never synced)
# --------------------------------------------------------------------------- #
def rig_file_path(profile: RigProfile, root: Path | str | None) -> Path | None:
    """Where this rig's ``.ma`` would sit under ``root``, or ``None`` if either is unset."""
    if root is None or not profile.rig_file:
        return None
    return Path(root) / profile.rig_file


def variant_file_path(profile: RigProfile, variant: str,
                      root: Path | str | None) -> Path | None:
    """Where the rig file for one body ``variant`` would sit under ``root``.

    Only meaningful for a ``files``-mode rig; falls back to the profile's single
    :attr:`RigProfile.rig_file` for every other mode.
    """
    if root is None:
        return None
    rel = profile.variants.files.get(variant.strip().lower())
    if rel:
        return Path(root) / rel
    return rig_file_path(profile, root)


def bundled_rig_file(profile: RigProfile) -> Path | None:
    """The rig file this profile ships inside the package, if it declares one.

    Only the bundled GenHuman does; every registered rig keeps its ``.ma`` in the shared
    library instead. Returned even when absent from disk (a fresh checkout has no rig
    binaries) so the caller can report the missing path rather than a bare "not found".
    """
    if not profile.bundled_file:
        return None
    return config.package_dir() / "lib" / profile.bundled_file


# --- fetching a rig body on demand -------------------------------------------
# Sync deliberately skips rig ``.ma`` files (see core.sync): they are 25-30 MB and most
# artists only ever open one rig. Instead a rig body is copied down the first time it is
# actually needed - loading a test body, or publishing for that rig - so switching rigs
# costs one fetch rather than every artist paying for every rig on every sync.

STATUS_BUNDLED: str = "bundled"        # ships in the package (GenHuman); nothing to fetch
STATUS_LOCAL: str = "local"            # already downloaded; ready to use
STATUS_REMOTE_ONLY: str = "remote_only"  # on the shared library, needs fetching
STATUS_MISSING: str = "missing"        # declared but not found in either place
STATUS_NO_FILE: str = "no_file"        # this rig declares no file at all


def rig_file_status(profile: RigProfile, local: Path | str | None,
                    remote: Path | str | None, variant: str = "") -> str:
    """Where this rig's body currently is - one of the ``STATUS_*`` constants.

    Lets the UI say "Fetch rig (28 MB)" versus "ready" *without* touching the network
    beyond a stat, so merely opening the rig dropdown never triggers a download.
    """
    bundled = bundled_rig_file(profile)
    if bundled is not None and bundled.is_file():
        return STATUS_BUNDLED
    if not profile.rig_file and not profile.variants.files:
        return STATUS_NO_FILE
    local_path = variant_file_path(profile, variant, local) if variant else \
        rig_file_path(profile, local)
    if local_path is not None and local_path.is_file():
        return STATUS_LOCAL
    remote_path = variant_file_path(profile, variant, remote) if variant else \
        rig_file_path(profile, remote)
    if remote_path is not None and remote_path.is_file():
        return STATUS_REMOTE_ONLY
    return STATUS_MISSING


def rig_file_size(profile: RigProfile, root: Path | str | None,
                  variant: str = "") -> int:
    """Bytes of this rig's body under ``root``, or ``0`` when it isn't there.

    Lets the UI say "Fetch rig (28 MB)" before starting a copy the user may not want to
    wait for. A stat, never a read.
    """
    path = (variant_file_path(profile, variant, root) if variant
            else rig_file_path(profile, root))
    if path is None:
        return 0
    try:
        return path.stat().st_size
    except OSError:
        return 0


def ensure_rig_file(profile: RigProfile, local: Path | str | None,
                    remote: Path | str | None, variant: str = "",
                    progress=None) -> Path:
    """Return a local path to this rig's body, copying it down from the remote if needed.

    ``progress`` is an optional ``callable(copied_bytes, total_bytes)`` so a 30 MB copy
    over a share can drive a progress bar; it is called on the calling thread, so the UI
    runs this on a worker.

    Raises ``FileNotFoundError`` with an actionable message when the rig body can't be
    found - the artist needs to know whether the fix is "configure your remote library",
    "ask whoever registered this rig to re-register it", or "this rig has no test body".
    Copies via a temporary file so an interrupted fetch never leaves a truncated rig
    behind that would look local on the next call.
    """
    bundled = bundled_rig_file(profile)
    if bundled is not None and bundled.is_file():
        return bundled

    if not profile.rig_file and not profile.variants.files:
        raise FileNotFoundError(
            f"The {profile.label} rig has no rig file registered, so there is no test "
            "body to load. Re-register the rig with its .ma file to add one.")

    local_path = (variant_file_path(profile, variant, local) if variant
                  else rig_file_path(profile, local))
    if local_path is not None and local_path.is_file():
        return local_path

    remote_path = (variant_file_path(profile, variant, remote) if variant
                   else rig_file_path(profile, remote))
    if remote_path is None:
        raise FileNotFoundError(
            f"The {profile.label} rig file has not been downloaded yet and no remote "
            "library is configured to fetch it from. Set the remote folder on the Setup "
            "tab, then try again.")
    if not remote_path.is_file():
        raise FileNotFoundError(
            f"The {profile.label} rig file is missing from the shared library:\n"
            f"  {remote_path}\n"
            "Whoever registered this rig may not have finished uploading it - ask them "
            "to register it again.")
    if local_path is None:
        raise FileNotFoundError(
            f"No local library folder is set, so the {profile.label} rig file has "
            "nowhere to download to. Set the local folder on the Setup tab.")

    return _copy_with_progress(remote_path, local_path, progress)


def rig_file_rel(rig_id: str, filename: str) -> str:
    """The library-relative slot a rig's ``.ma`` occupies: ``_rigs/<rig_id>/<filename>``.

    One place defines the layout, so registration (which writes there) and
    :func:`rig_file_path` (which reads) can never drift apart.
    """
    return f"{RIGS_DIRNAME}/{rig_id}/{filename}"


def install_rig_file(rig_id: str, source: Path | str, dest_root: Path | str,
                     progress=None) -> str:
    """Copy a rig ``.ma`` into ``<dest_root>/_rigs/<rig_id>/``; return its relative path.

    The returned string is what goes in :attr:`RigProfile.rig_file` - library-relative, so
    the same profile resolves against the shared library and against each artist's local
    copy. Registration installs into the *remote* library (that is the rig repo everyone
    fetches from) and, when one is configured, the local library too, so the artist who
    registered the rig never downloads back their own upload.

    Re-installing the same file onto itself is a no-op rather than an error, so
    re-registering a rig to update its profile doesn't need the rig file to move.
    """
    src = Path(source)
    if not src.is_file():
        raise FileNotFoundError(
            f"Rig file not found: {src}. Pick the rig's .ma file to register it, or "
            "register the rig without a file (no test body will be available).")
    rel = rig_file_rel(rig_id, src.name)
    dst = Path(dest_root) / rel
    if dst.is_file() and dst.samefile(src):
        return rel
    _copy_with_progress(src, dst, progress)
    return rel


def _copy_with_progress(src: Path, dst: Path, progress=None,
                        chunk: int = 4 * 1024 * 1024) -> Path:
    """Copy ``src`` to ``dst`` in chunks, reporting progress; atomic on success.

    Written to a ``.part`` file and renamed at the end, so an interrupted or failed fetch
    leaves no half-copied rig that later calls would mistake for a complete download.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    total = src.stat().st_size
    partial = dst.with_name(dst.name + ".part")
    copied = 0
    try:
        with src.open("rb") as fsrc, partial.open("wb") as fdst:
            while True:
                block = fsrc.read(chunk)
                if not block:
                    break
                fdst.write(block)
                copied += len(block)
                if progress is not None:
                    progress(copied, total)
        shutil.copystat(src, partial)  # keep mtime so a later sync-style check matches
        partial.replace(dst)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
    return dst
