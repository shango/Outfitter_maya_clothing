"""Maya-side capture for publish — the half that needs a live scene.

Everything here imports ``maya.cmds`` lazily and only runs inside Maya: count the
garment polys, playblast a thumbnail, sniff the rig version, and save the ``.ma``.
The pure assembly/validation lives in :mod:`snap_on_clothing.core.publish`. This
module is exercised by the in-Maya smoke check, never the headless suite (which only
``py_compile``s it), consistent with the rest of the Maya boundary.
"""
from __future__ import annotations

import os
import re

from .. import config
from . import publish as _publish


def _cmds():
    import maya.cmds as cmds  # type: ignore

    return cmds


def _short(name: str) -> str:
    """DAG-path tail without namespace ("…|ns:Mesh_GRP" -> "Mesh_GRP")."""
    return name.rsplit("|", 1)[-1].rsplit(":", 1)[-1]


# --------------------------------------------------------------------------- #
# Scene introspection
# --------------------------------------------------------------------------- #
def find_garment_meshes(mesh_group: str = "Mesh_GRP") -> list[str]:
    """Mesh transforms making up the garment (everything under ``Mesh_GRP``).

    Falls back to all mesh transforms in the scene if the group is absent, so the
    rigger can still capture a thumbnail before the hierarchy is fully assembled.
    """
    cmds = _cmds()

    def _transforms(shapes: list[str]) -> list[str]:
        out: list[str] = []
        for shp in shapes:
            parent = cmds.listRelatives(shp, parent=True, fullPath=True) or []
            for p in parent:
                if p not in out:
                    out.append(p)
        return out

    if cmds.objExists(mesh_group):
        shapes = cmds.listRelatives(
            mesh_group, allDescendents=True, type="mesh", fullPath=True) or []
        if shapes:
            return _transforms(shapes)
    return _transforms(cmds.ls(type="mesh", long=True) or [])


def poly_counts(meshes: list[str]) -> tuple[int, int]:
    """``(triangles, vertices)`` summed across ``meshes`` via ``polyEvaluate``."""
    cmds = _cmds()
    tris = verts = 0
    for m in meshes:
        try:
            tris += int(cmds.polyEvaluate(m, triangle=True) or 0)
            verts += int(cmds.polyEvaluate(m, vertex=True) or 0)
        except Exception:  # noqa: BLE001 — non-poly or empty selection
            continue
    return tris, verts


def scene_has_rig() -> bool:
    """True if a GenHuman rig is still in the scene.

    The published asset must contain only the garment (no rig / namespaces / refs),
    but the rigger authors *with* the rig in scene (to duplicate its skeleton and fit
    the mesh). Publish uses this to warn them to delete the rig first rather than
    silently writing a bloated, validation-failing ``.ma``. Matches any node carrying
    the GenHuman name or a leftover GenHuman namespace.
    """
    cmds = _cmds()
    if any("GenHuman" in n.rsplit("|", 1)[-1] for n in (cmds.ls(long=True) or [])):
        return True
    return any(
        "GenHuman" in ns
        for ns in (cmds.namespaceInfo(":", listOnlyNamespaces=True, recurse=True) or [])
    )


def detect_rig_version() -> str:
    """Best-effort exact rig version (e.g. ``v03``) from the scene; ``""`` if unknown.

    Prefilled into the Publish form for the rigger to confirm/override — never an
    authority. Looks at GenHuman namespaces first (imports name them, e.g.
    ``GenHuman_rig_v03``), then the export group's own namespace token.
    """
    cmds = _cmds()
    for ns in (cmds.namespaceInfo(":", listOnlyNamespaces=True, recurse=True) or []):
        if "GenHuman" in ns:
            m = re.search(r"v\d+", ns)
            if m:
                return m.group(0)
    marker = config.EXPORT_SKELETON_GROUP
    for t in (cmds.ls(type="transform", long=True) or []):
        short = t.rsplit("|", 1)[-1]
        if short.rsplit(":", 1)[-1] == marker and ":" in short:
            m = re.search(r"v\d+", short.split(":", 1)[0])
            if m:
                return m.group(0)
    return ""


# --------------------------------------------------------------------------- #
# Pre-publish scene sanity check (gather live facts; pure decision in core.publish)
# --------------------------------------------------------------------------- #
def _skin_influences(cmds, meshes: list[str]) -> tuple[list[str], bool]:
    """``(influence names, any skinCluster found)`` across the garment meshes."""
    influences: list[str] = []
    found = False
    for m in meshes:
        hist = cmds.listHistory(m, pruneDagObjects=True) or []
        for sc in (cmds.ls(hist, type="skinCluster") or []):
            found = True
            influences.extend(cmds.skinCluster(sc, query=True, influence=True) or [])
    return influences, found


def gather_scene_facts(mesh_group: str = "Mesh_GRP") -> "_publish.SceneFacts":
    """Collect the facts the pure preflight needs from the open scene.

    Presence is tested by *short* name (namespace-insensitive) so a namespaced asset
    isn't also reported as "missing groups" — the namespace itself is flagged separately.
    """
    cmds = _cmds()
    nodes = ((cmds.ls(type="transform", long=True) or [])
             + (cmds.ls(type="joint", long=True) or []))
    shorts = {_short(n) for n in nodes}

    namespaces = [
        ns for ns in (cmds.namespaceInfo(
            ":", listOnlyNamespaces=True, recurse=True) or [])
        if ns not in ("UI", "shared")
    ]

    cloth_joints = cmds.ls(
        f"{config.CLOTH_PREFIX}*", type="joint", long=True) or []
    cloth_joint_names = tuple(sorted({_short(j) for j in cloth_joints}))
    driven_cloth_joints = tuple(sorted({
        _short(j) for j in cloth_joints
        if any(cmds.connectionInfo(f"{j}.{attr}", isDestination=True)
               for attr in config.CONNECT_ATTRS)}))

    meshes = find_garment_meshes(mesh_group)
    influences, has_skin = _skin_influences(cmds, meshes)

    return _publish.SceneFacts(
        has_rig=scene_has_rig(),
        namespaces=tuple(namespaces),
        present_groups=tuple(g for g in config.REQUIRED_GROUPS if g in shorts),
        has_cloth_root=config.ROOT_JOINT in shorts,
        has_info_node=config.INFO_NODE in shorts,
        has_skincluster=has_skin,
        skin_influences=tuple(influences),
        cloth_joint_names=cloth_joint_names,
        has_fit_ctrl=config.FIT_CTRL in shorts,
        driven_cloth_joints=driven_cloth_joints,
    )


def preflight_scene(mesh_group: str = "Mesh_GRP") -> list:
    """Run the pre-publish sanity check on the open scene. List of ``PreflightIssue``."""
    return _publish.assemble_preflight(gather_scene_facts(mesh_group))


# --------------------------------------------------------------------------- #
# Thumbnail
# --------------------------------------------------------------------------- #
def _model_panel() -> str | None:
    cmds = _cmds()
    panel = cmds.getPanel(withFocus=True)
    if panel and cmds.getPanel(typeOf=panel) == "modelPanel":
        return panel
    panels = cmds.getPanel(type="modelPanel") or []
    return panels[0] if panels else None


def capture_thumbnail(meshes: list[str], out_png: str, size: int = 512) -> str:
    """Playblast a single framed frame of ``meshes`` to ``out_png`` (square PNG).

    Frames the garment in the active model panel, hides the grid and ornaments for a
    clean shot, blits one frame off-screen, then restores the viewport state and the
    user's selection. Returns the written path. Raises if there is no model panel.
    """
    cmds = _cmds()
    panel = _model_panel()
    if panel is None:
        raise RuntimeError("no model panel available to capture a thumbnail")

    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
    prev_selection = cmds.ls(selection=True, long=True) or []
    grid_was = cmds.grid(query=True, toggle=True)
    isolated = False
    try:
        if meshes:
            cmds.select(meshes, replace=True)
            cmds.isolateSelect(panel, state=1)
            cmds.isolateSelect(panel, addSelected=True)
            isolated = True
            # panel is a flag, not the object to frame — pass the meshes as the objects
            # and target the panel via panel=, or Maya tries to resolve the panel name
            # as a scene node ("No object matches name: modelPanel4").
            cmds.viewFit(meshes, panel=panel, fitFactor=0.9)
        cmds.grid(toggle=False)
        frame = cmds.currentTime(query=True)
        cmds.playblast(
            frame=frame, format="image", compression="png",
            completeFilename=out_png, widthHeight=(size, size), percent=100,
            showOrnaments=False, offScreen=True, viewer=False, forceOverwrite=True,
        )
    finally:
        if isolated:
            cmds.isolateSelect(panel, state=0)
        cmds.grid(toggle=grid_was)
        if prev_selection:
            cmds.select(prev_selection, replace=True)
        else:
            cmds.select(clear=True)
    return out_png


# --------------------------------------------------------------------------- #
# Save
# --------------------------------------------------------------------------- #
def save_ma(out_path: str) -> str:
    """Rename the current scene to ``out_path`` and save it as Maya ASCII.

    A whole-scene save round-trips skin + lattice deformer chains cleanly (where
    ``exportSelected`` corrupts them). The garment scene should already be clean of
    the rig/namespaces/references — :func:`core.publish.validate_published_ma` is run
    on the result to enforce that.
    """
    cmds = _cmds()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    cmds.file(rename=out_path)
    cmds.file(save=True, type="mayaAscii", force=True)
    return out_path
