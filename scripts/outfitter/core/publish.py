"""Publish a hand-authored garment into the library (pure, headless-testable).

Riggers author garments by hand in Maya; *publish* is the step that finalizes one:
it writes the ``.ma`` plus the ``<asset>.json`` sidecar (the published metadata
file the browser reads) and an ``<asset>.png`` thumbnail into the library, laid out
as ``<dest>/<name>/<name>.{ma,json,png}`` to match the scanner's expectations.

This module is the **pure** half - it assembles the sidecar payload, computes the
destination paths, sanitizes the asset name, and validates a saved ``.ma`` by reusing
the existing file validator. Everything that needs a live Maya scene (polycount,
playblast thumbnail, rig-version detection, saving the file) lives in
:mod:`outfitter.core.maya_publish`. Keeping them apart lets the assembly and
validation logic run in CI with no Maya, exactly like the rest of ``core``.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from .. import config
from . import ma_parse
from . import rigs
from .asset import AssetMetadata
from .validate import ValidationReport, validate_asset_summary

_NAME_INVALID = re.compile(r"[^A-Za-z0-9_-]")


def sanitize_asset_name(name: str) -> str:
    """A filesystem- and Maya-safe asset/folder name from arbitrary text."""
    cleaned = _NAME_INVALID.sub("_", name.strip())
    if cleaned and cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned or "clothing_asset"


def today_iso() -> str:
    """Today's date as ``YYYY-MM-DD`` (the publish/created stamp)."""
    return date.today().isoformat()


@dataclass(frozen=True)
class PublishPaths:
    """Where the published files for one asset land on disk."""

    folder: Path
    ma: Path
    sidecar: Path
    thumbnail: Path
    turntable: Path


def destination_paths(dest_root: Path | str, asset_name: str) -> PublishPaths:
    """``<dest_root>/<name>/<name>.{ma,json,png}`` (+ turntable sheet) for a name."""
    name = sanitize_asset_name(asset_name)
    folder = Path(dest_root) / name
    return PublishPaths(
        folder=folder,
        ma=folder / f"{name}.ma",
        sidecar=folder / f"{name}.json",
        thumbnail=folder / f"{name}.png",
        turntable=folder / f"{name}{config.TURNTABLE_SUFFIX}",
    )


@dataclass
class PublishSpec:
    """The metadata a rigger supplies (plus values captured from the live scene)."""

    asset_name: str
    asset_type: str
    gender: str
    cloth_version: str
    # The rig this garment was authored against, and the versions of it that fit.
    rig_id: str = rigs.DEFAULT_RIG_ID
    rig_versions: tuple[str, ...] = ()
    author: str = ""
    description: str = ""
    rig_version: str = ""
    created: str = ""
    tri_count: int | None = None
    vert_count: int | None = None

    def to_sidecar(self) -> dict[str, object]:
        """Serialize to a sidecar dict using the Authoring Spec §12 attr names.

        Mirrors the keys :meth:`AssetMetadata.from_mapping` reads, so a published
        sidecar round-trips back into the same metadata the browser shows. Optional
        numeric fields are omitted when unknown rather than written as null.

        ``genHumanCompat`` is still written alongside ``rigVersions`` - it costs one line
        and keeps a freshly published GenHuman asset readable by an Outfitter install that
        hasn't been upgraded yet. It is only meaningful for GenHuman assets, so it is
        omitted for every other rig rather than written misleadingly.
        """
        data: dict[str, object] = {
            "assetName": self.asset_name,
            "assetType": self.asset_type,
            "gender": self.gender,
            "clothVersion": self.cloth_version,
            "rigId": self.rig_id,
            "rigVersions": ", ".join(self.rig_versions),
            "author": self.author,
            "notes": self.description,
            "created": self.created or today_iso(),
            "rigVersion": self.rig_version,
        }
        if self.rig_id == rigs.DEFAULT_RIG_ID:
            data["genHumanCompat"] = ", ".join(self.rig_versions)
        if self.tri_count is not None:
            data["triCount"] = self.tri_count
        if self.vert_count is not None:
            data["vertCount"] = self.vert_count
        return data

    def metadata(self) -> tuple[AssetMetadata | None, list[str]]:
        """Validate the supplied fields the same way the loader does."""
        return AssetMetadata.from_mapping(self.to_sidecar())


def write_sidecar(paths: PublishPaths, spec: PublishSpec) -> Path:
    """Write the sidecar ``.json`` (creating the asset folder); returns its path."""
    paths.folder.mkdir(parents=True, exist_ok=True)
    paths.sidecar.write_text(
        json.dumps(spec.to_sidecar(), indent=2) + "\n", encoding="utf-8")
    return paths.sidecar


# --------------------------------------------------------------------------- #
# Pre-publish scene sanity check (pure decision logic)
# --------------------------------------------------------------------------- #
# The published .ma is validated *after* it's written (validate_published_ma), but by
# then a bad scene has already cost a save. The preflight catches the common authoring
# mistakes up front, in-scene, with an actionable fix for each - the live-Maya half
# (core.maya_publish.gather_scene_facts) gathers the facts, this pure half decides.

@dataclass(frozen=True)
class PreflightIssue:
    """One finding from the pre-publish scene check."""

    level: str  # "error" (blocks publish) | "warn" | "info" | "ok"
    message: str
    fix: str = ""

    @property
    def is_error(self) -> bool:
        return self.level == "error"


@dataclass(frozen=True)
class SceneFacts:
    """Everything the preflight needs to know about the open scene (gathered in Maya)."""

    has_rig: bool
    namespaces: tuple[str, ...]
    present_groups: tuple[str, ...]
    has_cloth_root: bool
    has_skincluster: bool
    skin_influences: tuple[str, ...]
    cloth_joint_names: tuple[str, ...]
    driven_cloth_joints: tuple[str, ...] = ()
    # §10/§13/§11 cleanliness facts (short node names; empty = clean):
    unknown_nodes: tuple[str, ...] = ()
    anim_curves: tuple[str, ...] = ()
    display_layers: tuple[str, ...] = ()
    renderer_materials: tuple[str, ...] = ()


def root_namespaces(namespaces, ignore=("UI", "shared")) -> list[str]:
    """Distinct top-level namespace tokens, minus Maya's built-ins. Order-preserving."""
    roots: list[str] = []
    for ns in namespaces:
        root = ns.lstrip(":").split(":", 1)[0]
        if root and root not in ignore and root not in roots:
            roots.append(root)
    return roots


def split_influences(influences, cloth_prefix: str) -> tuple[list[str], list[str]]:
    """``(cloth_* influences, other influences)`` by short name.

    "Other" means the garment is skinned to joints outside the cloth skeleton (typically
    the rig's own deform joints) - those vanish when the rig is deleted and break attach,
    so they're the single most important thing the preflight flags.
    """
    cloth: list[str] = []
    other: list[str] = []
    for inf in influences:
        short = inf.rsplit("|", 1)[-1].rsplit(":", 1)[-1]
        (cloth if short.startswith(cloth_prefix) else other).append(short)
    return cloth, other


def _sample(names, limit: int = 6) -> str:
    """``"a, b, c (+N more)"`` - a short, sorted, de-duped preview of node names."""
    uniq = sorted(set(names))
    head = ", ".join(uniq[:limit])
    return head if len(uniq) <= limit else f"{head} (+{len(uniq) - limit} more)"


def assemble_preflight(
    facts: SceneFacts,
    required_groups=config.REQUIRED_GROUPS,
    cloth_prefix: str = config.CLOTH_PREFIX,
    root_joint: str = config.ROOT_JOINT,
) -> list[PreflightIssue]:
    """Turn gathered :class:`SceneFacts` into an ordered list of :class:`PreflightIssue`.

    Pure and fully unit-testable. Any ``error``-level issue means publish should be
    blocked; ``warn`` is advisory; a trailing ``ok`` is appended when nothing blocks.
    """
    issues: list[PreflightIssue] = []

    if facts.has_rig:
        issues.append(PreflightIssue(
            "error", "A rig is still in the scene.",
            "Delete the rig and remove its namespace so the asset contains only the "
            "garment (no rig, namespaces, or references)."))

    roots = root_namespaces(facts.namespaces)
    if roots:
        issues.append(PreflightIssue(
            "error", f"Asset is inside namespace(s): {', '.join(roots)}.",
            "Remove all namespaces (Window ▸ Namespace Editor) so node names are bare - "
            "e.g. 'Mesh_GRP', not 'jacket_A:Mesh_GRP'."))

    missing = [g for g in required_groups if g not in facts.present_groups]
    if missing:
        issues.append(PreflightIssue(
            "error", f"Missing required group(s): {', '.join(missing)}.",
            "The asset needs Mesh_GRP, Rig_GRP and Ctrl_GRP at the scene root."))

    if not facts.has_cloth_root:
        issues.append(PreflightIssue(
            "error", f"No '{root_joint}' joint in the scene.",
            "Run 'Create cloth skeleton' and skin to those joints before publishing."))

    if not facts.has_skincluster:
        issues.append(PreflightIssue(
            "warn", "No skinCluster found on the garment.",
            "Skin the mesh to the cloth_* joints, or the garment won't follow the body."))
    else:
        cloth_infl, other = split_influences(facts.skin_influences, cloth_prefix)
        uniq_other = sorted(set(other))
        if uniq_other:
            issues.append(PreflightIssue(
                "error",
                f"Garment is skinned to {len(uniq_other)} non-{cloth_prefix}* "
                f"joint(s): {_sample(uniq_other)}.",
                f"Re-skin the garment to the {cloth_prefix}* joints. Influences outside "
                "the cloth skeleton are deleted with the rig and break attach."))
        elif not cloth_infl:
            issues.append(PreflightIssue(
                "error", "The garment skinCluster has no influences.",
                f"Bind the mesh to the {cloth_prefix}* joints."))

    if facts.driven_cloth_joints:
        n = len(facts.driven_cloth_joints)
        sample = ", ".join(sorted(facts.driven_cloth_joints)[:6])
        more = "" if n <= 6 else f" (+{n - 6} more)"
        issues.append(PreflightIssue(
            "warn",
            f"{n} {cloth_prefix}* joint(s) are still driven by the test body: "
            f"{sample}{more}.",
            "Click 'Disconnect test body' so the joints go static before publishing - "
            "the connections (and the body that drives them) must not ship in the asset."))

    # §10/§13/§11 cleanliness - the same hard "no" list validate_asset_summary enforces
    # on the saved .ma, surfaced here in-scene so the author fixes it before the save.
    if facts.unknown_nodes:
        issues.append(PreflightIssue(
            "error", f"Unknown (lost-plugin) node(s): {_sample(facts.unknown_nodes)}.",
            "Delete unknown nodes - Edit ▸ Delete All by Type ▸ Unknown Nodes."))

    if facts.anim_curves:
        issues.append(PreflightIssue(
            "error", f"Animation curve(s) in the scene: {_sample(facts.anim_curves)}.",
            "Delete all keyframes/animation - a delivered asset must be static."))

    if facts.display_layers:
        issues.append(PreflightIssue(
            "error", f"Display layer(s) present: {_sample(facts.display_layers)}.",
            "Remove all display layers before publishing."))

    if facts.renderer_materials:
        issues.append(PreflightIssue(
            "error",
            f"Render-engine shader(s): {_sample(facts.renderer_materials)}.",
            "Use generic shaders only (lambert / standardSurface). Render-engine-specific "
            "materials aren't allowed and don't survive a clean .ma export."))

    # No cloth_info check here: publish writes the node from the form before saving
    # (see maya_publish.write_info_node), so the saved .ma is always self-describing.

    if not any(i.is_error for i in issues):
        issues.append(PreflightIssue("ok", "Scene looks publish-ready.", ""))

    return issues


# --------------------------------------------------------------------------- #
# Step-1 "clean room" pre-check (pure decision logic)
# --------------------------------------------------------------------------- #
# Before the cloth rig is built, the scene should hold only the garment geo. Riggers
# commonly *import* the body rig to fit the garment to height, then delete it -
# which leaves namespaces, unknown nodes, empty groups and orphaned joints behind, and
# building the rig on top of that junk bakes it into the asset. This scans first and
# reports anything that isn't the garment, so it's cleaned before Step 1 proceeds.

@dataclass(frozen=True)
class ScenePrecheckFacts:
    """What the Step-1 clean-room pre-check needs from the open scene (gathered in Maya).

    Every field but ``has_rig`` lists short names of nodes that shouldn't be there before
    the cloth rig is built (empty = clean).
    """

    has_rig: bool
    namespaces: tuple[str, ...] = ()
    extra_root_nodes: tuple[str, ...] = ()
    unknown_nodes: tuple[str, ...] = ()
    anim_curves: tuple[str, ...] = ()
    display_layers: tuple[str, ...] = ()


def assemble_scene_precheck(facts: ScenePrecheckFacts) -> list[PreflightIssue]:
    """Turn Step-1 scene facts into cleanup findings (pure, fully unit-testable).

    Findings are advisory (``warn``): the pre-check guides the rigger to a clean scene, it
    doesn't hard-block. A trailing ``ok`` is appended when nothing was found.
    """
    issues: list[PreflightIssue] = []

    if facts.has_rig:
        issues.append(PreflightIssue(
            "warn", "A rig is still in the scene.",
            "Remove the rig and its namespace - build the cloth skeleton against the bare "
            "garment, then load the test body afterwards."))

    roots = root_namespaces(facts.namespaces)
    if roots:
        issues.append(PreflightIssue(
            "warn", f"Leftover namespace(s): {', '.join(roots)}.",
            "Remove them (Window > Namespace Editor) - a namespace usually means an "
            "imported/referenced rig wasn't fully cleaned up."))

    if facts.extra_root_nodes:
        issues.append(PreflightIssue(
            "warn", f"Node(s) besides the garment geo: {_sample(facts.extra_root_nodes)}.",
            "Delete everything except the garment mesh - loose groups, orphaned joints, "
            "locators and constraints left behind by a deleted rig import."))

    if facts.unknown_nodes:
        issues.append(PreflightIssue(
            "warn", f"Unknown (lost-plugin) node(s): {_sample(facts.unknown_nodes)}.",
            "Delete them - Edit > Delete All by Type > Unknown Nodes."))

    if facts.anim_curves:
        issues.append(PreflightIssue(
            "warn", f"Animation curve(s): {_sample(facts.anim_curves)}.",
            "Delete all keys - a rig import often drags posed animation in with it."))

    if facts.display_layers:
        issues.append(PreflightIssue(
            "warn", f"Display layer(s): {_sample(facts.display_layers)}.",
            "Remove them - they don't belong in a delivered asset."))

    if not issues:
        issues.append(PreflightIssue(
            "ok", "Scene is clean - only the garment geo is present.", ""))

    return issues


def validate_published_ma(ma_path: Path | str) -> ValidationReport:
    """Re-validate a saved asset ``.ma`` with the same file checks the browser uses.

    Run after the scene is saved so publish enforces the structure contract
    (info node, required groups, cloth_root, clean of refs/namespaces/forbidden
    nodes). Reuses :func:`validate_asset_summary` - no publish-specific rules.
    """
    summary = ma_parse.summarize_file(ma_path)
    meta, _ = AssetMetadata.from_mapping(summary.info_attrs)
    return validate_asset_summary(summary, meta)
