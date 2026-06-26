"""Maya-side capture for publish — the half that needs a live scene.

Everything here imports ``maya.cmds`` lazily and only runs inside Maya: count the
garment polys, playblast a thumbnail, sniff the rig version, and save the ``.ma``.
The pure assembly/validation lives in :mod:`outfitter.core.publish`. This
module is exercised by the in-Maya smoke check, never the headless suite (which only
``py_compile``s it), consistent with the rest of the Maya boundary.
"""
from __future__ import annotations

import os
import re
import shutil
import tempfile
from contextlib import contextmanager

from .. import config
from . import publish as _publish
from . import turntable as _turntable


def _cmds():
    import maya.cmds as cmds  # type: ignore

    return cmds


def _qt():
    """PySide6 image classes — ships with Maya 2026 (lazy, like ``_cmds``).

    Only the playblast compositor needs Qt; importing it lazily keeps this module's
    top level free of the Maya/Qt boundary, consistent with the rest of ``core``.
    """
    from PySide6 import QtCore, QtGui  # type: ignore

    return QtCore, QtGui


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


def _cleanliness_facts(cmds) -> tuple[tuple[str, ...], ...]:
    """Scan the scene for the §10/§13/§11 hard-"no" node types.

    Returns ``(unknown, anim_curves, display_layers, renderer_materials)`` as tuples
    of short names. ``defaultLayer`` is excluded — every scene has it. ``ls(type=…)``
    tolerates a missing renderer type, so the renderer denylist is queried as a batch.
    """
    def _ls_types(types) -> tuple[str, ...]:
        """Short names of nodes of any of ``types``, tolerating unregistered types.

        A renderer-specific type isn't registered unless its plugin is loaded, and
        ``cmds.ls(type=…)`` raises on an unknown type — so query type-by-type and skip
        the ones Maya doesn't know in this session.
        """
        found: set[str] = set()
        for t in types:
            try:
                found.update(_short(n) for n in (cmds.ls(type=t, long=True) or []))
            except (RuntimeError, ValueError):
                continue  # type not registered in this session — nothing of it can exist
        return tuple(sorted(found))

    unknown = _ls_types(config.UNKNOWN_NODE_TYPES)
    anim_curves = _ls_types(config.TIMELINE_ANIM_CURVE_TYPES)  # time-input keys only
    display_layers = tuple(
        n for n in _ls_types((config.DISPLAY_LAYER_TYPE,))
        if n not in config.DEFAULT_DISPLAY_LAYERS)
    renderer_mats = _ls_types(config.RENDERER_SHADER_TYPES)
    return unknown, anim_curves, display_layers, renderer_mats


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

    unknown, anim_curves, display_layers, renderer_mats = _cleanliness_facts(cmds)

    return _publish.SceneFacts(
        has_rig=scene_has_rig(),
        namespaces=tuple(namespaces),
        present_groups=tuple(g for g in config.REQUIRED_GROUPS if g in shorts),
        has_cloth_root=config.ROOT_JOINT in shorts,
        has_skincluster=has_skin,
        skin_influences=tuple(influences),
        cloth_joint_names=cloth_joint_names,
        driven_cloth_joints=driven_cloth_joints,
        unknown_nodes=unknown,
        anim_curves=anim_curves,
        display_layers=display_layers,
        renderer_materials=renderer_mats,
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


def _panel_camera(cmds, panel: str) -> str:
    """The transform of ``panel``'s camera (so ``xform``/``viewPlace`` have a node)."""
    cam = cmds.modelPanel(panel, query=True, camera=True)
    if cmds.objectType(cam) == "camera":
        parent = cmds.listRelatives(cam, parent=True, fullPath=True) or [cam]
        cam = parent[0]
    return cam


@contextmanager
def _clean_shaded_view(panel: str):
    """Force a clean *shaded* look on ``panel`` for the block, restoring it after.

    Thumbnails were capturing whatever display mode the viewport happened to be in —
    wireframe shows only the silhouette. This switches the panel to smooth-shaded with
    textures (and best-effort viewport-2.0 anti-aliasing + ambient occlusion), and hides
    the grid / wireframe-on-shaded / HUD for a clean shot. Every changed setting is saved
    and restored, so the rigger's viewport looks the same afterwards.
    """
    cmds = _cmds()
    saved = {
        flag: cmds.modelEditor(panel, query=True, **{flag: True})
        for flag in ("displayAppearance", "displayTextures", "wireframeOnShaded",
                     "grid", "headsUpDisplay")
    }
    # Viewport 2.0 quality knobs live on a scene singleton; toggling them is best-effort
    # (attrs vary by Maya build), so each is guarded and only restored if it was read.
    hw = "hardwareRenderingGlobals"
    hw_saved: dict[str, int] = {}
    for attr in ("multiSampleEnable", "ssaoEnable"):
        plug = f"{hw}.{attr}"
        try:
            hw_saved[attr] = cmds.getAttr(plug)
            cmds.setAttr(plug, 1)
        except Exception:  # noqa: BLE001 — attr absent on this build; skip it
            continue
    try:
        cmds.modelEditor(
            panel, edit=True, displayAppearance="smoothShaded",
            displayTextures=True, wireframeOnShaded=False, grid=False,
            headsUpDisplay=False)
        yield
    finally:
        cmds.modelEditor(panel, edit=True, **saved)
        for attr, was in hw_saved.items():
            try:
                cmds.setAttr(f"{hw}.{attr}", was)
            except Exception:  # noqa: BLE001
                continue


def capture_thumbnail(meshes: list[str], out_png: str, size: int = 512) -> str:
    """Playblast a single clean *shaded* frame of ``meshes`` to ``out_png`` (square PNG).

    Frames the garment in the active model panel, forces a smooth-shaded view (see
    :func:`_clean_shaded_view`), blits one frame off-screen, then restores the viewport
    state and the user's selection. Returns the written path. Raises if there is no model
    panel.
    """
    cmds = _cmds()
    panel = _model_panel()
    if panel is None:
        raise RuntimeError("no model panel available to capture a thumbnail")

    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
    prev_selection = cmds.ls(selection=True, long=True) or []
    isolated = False
    with _clean_shaded_view(panel):
        try:
            if meshes:
                cmds.select(meshes, replace=True)
                cmds.isolateSelect(panel, state=1)
                cmds.isolateSelect(panel, addSelected=True)
                isolated = True
                # panel is a flag, not the object to frame — pass the meshes as the
                # objects and target the panel via panel=, or Maya tries to resolve the
                # panel name as a scene node ("No object matches name: modelPanel4").
                cmds.viewFit(meshes, panel=panel, fitFactor=0.9)
            frame = cmds.currentTime(query=True)
            cmds.playblast(
                frame=frame, format="image", compression="png",
                completeFilename=out_png, widthHeight=(size, size), percent=100,
                showOrnaments=False, offScreen=True, viewer=False, forceOverwrite=True,
            )
        finally:
            if isolated:
                cmds.isolateSelect(panel, state=0)
            if prev_selection:
                cmds.select(prev_selection, replace=True)
            else:
                cmds.select(clear=True)
    return out_png


def _composite_sheet(cell_pngs: list[str], out_png: str, cols: int, rows: int,
                     cell: int) -> str:
    """Tile per-frame PNGs ``cell_pngs`` row-major into one ``cols`` x ``rows`` sheet."""
    QtCore, QtGui = _qt()
    sheet = QtGui.QImage(cols * cell, rows * cell, QtGui.QImage.Format_ARGB32)
    sheet.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(sheet)
    try:
        for i, png in enumerate(cell_pngs):
            img = QtGui.QImage(png)
            if img.isNull():
                continue
            if img.width() != cell or img.height() != cell:
                img = img.scaled(cell, cell, QtCore.Qt.KeepAspectRatio,
                                 QtCore.Qt.SmoothTransformation)
            x, y, _, _ = _turntable.cell_rect(i, cols=cols, cell=cell)
            painter.drawImage(x, y, img)
    finally:
        painter.end()
    os.makedirs(os.path.dirname(out_png) or ".", exist_ok=True)
    sheet.save(out_png, "PNG")
    return out_png


def _crop_cell(sheet_png: str, out_png: str, index: int, cols: int, cell: int) -> str:
    """Write frame ``index`` of ``sheet_png`` to ``out_png`` (the still thumbnail)."""
    _, QtGui = _qt()
    x, y, w, h = _turntable.cell_rect(index, cols=cols, cell=cell)
    QtGui.QImage(sheet_png).copy(x, y, w, h).save(out_png, "PNG")
    return out_png


def capture_turntable(
    meshes: list[str],
    out_png: str,
    *,
    cols: int = config.TURNTABLE_COLS,
    rows: int = config.TURNTABLE_ROWS,
    cell: int = config.TURNTABLE_CELL,
    still_png: str | None = None,
) -> str:
    """Orbit the garment and bake a clean-shaded turntable sprite sheet to ``out_png``.

    Captures ``cols * rows`` smooth-shaded frames evenly around the asset (about Y) and
    tiles them row-major into one PNG (see :mod:`core.turntable` for the layout the
    browser scrub widget reads back). When ``still_png`` is given, frame 0 is also written
    there as the single representative thumbnail — the backward-compatible ``<asset>.png``
    that the grid icon and older viewers use. Restores the camera and selection afterwards.
    Returns the sheet path. Raises if there is no model panel or no meshes.
    """
    cmds = _cmds()
    panel = _model_panel()
    if panel is None:
        raise RuntimeError("no model panel available to capture a turntable")
    if not meshes:
        raise RuntimeError("no garment meshes to capture")

    frames = cols * rows
    camera = _panel_camera(cmds, panel)
    bbox = cmds.exactWorldBoundingBox(meshes)  # [xmin ymin zmin xmax ymax zmax]
    center = ((bbox[0] + bbox[3]) / 2.0, (bbox[1] + bbox[4]) / 2.0,
              (bbox[2] + bbox[5]) / 2.0)

    prev_selection = cmds.ls(selection=True, long=True) or []
    cam_matrix = cmds.xform(camera, query=True, worldSpace=True, matrix=True)
    tmp_dir = tempfile.mkdtemp(prefix="outfitter_tt_")
    cells: list[str] = []
    isolated = False
    with _clean_shaded_view(panel):
        try:
            cmds.select(meshes, replace=True)
            cmds.isolateSelect(panel, state=1)
            cmds.isolateSelect(panel, addSelected=True)
            isolated = True
            cmds.viewFit(meshes, panel=panel, fitFactor=0.9)
            eye0 = cmds.xform(camera, query=True, worldSpace=True, translation=True)
            frame = cmds.currentTime(query=True)
            for i, eye in enumerate(_turntable.orbit_eyes(center, eye0, frames)):
                cmds.viewPlace(camera, eye=eye, la=center, up=(0, 1, 0))
                cell_png = os.path.join(tmp_dir, f"f{i:03d}.png")
                cmds.playblast(
                    frame=frame, format="image", compression="png",
                    completeFilename=cell_png, widthHeight=(cell, cell), percent=100,
                    showOrnaments=False, offScreen=True, viewer=False,
                    forceOverwrite=True)
                cells.append(cell_png)
        finally:
            if isolated:
                cmds.isolateSelect(panel, state=0)
            cmds.xform(camera, worldSpace=True, matrix=cam_matrix)  # restore the view
            if prev_selection:
                cmds.select(prev_selection, replace=True)
            else:
                cmds.select(clear=True)
    try:
        _composite_sheet(cells, out_png, cols=cols, rows=rows, cell=cell)
        if still_png:
            _crop_cell(out_png, still_png, 0, cols=cols, cell=cell)
    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    return out_png


# --------------------------------------------------------------------------- #
# Embed metadata + save
# --------------------------------------------------------------------------- #
def write_info_node(attrs: dict, node: str = config.INFO_NODE) -> str:
    """Create/refresh the ``cloth_info`` node so the saved ``.ma`` is self-describing.

    ``attrs`` is the published metadata as ``cloth_info`` attribute names → values (use
    :meth:`core.publish.PublishSpec.to_sidecar`, so the embedded node mirrors the sidecar
    exactly). Every value is stored as a string ``addAttr`` (the browser's ``ma_parse``
    reads string attrs and coerces numbers). Idempotent — re-publishing refreshes the same
    node's attributes rather than duplicating it.
    """
    cmds = _cmds()
    if not cmds.objExists(node):
        node = cmds.createNode("network", name=node)
    for attr, value in attrs.items():
        plug = f"{node}.{attr}"
        if not cmds.objExists(plug):
            cmds.addAttr(node, longName=attr, dataType="string")
        cmds.setAttr(plug, str(value), type="string")
    return node


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
