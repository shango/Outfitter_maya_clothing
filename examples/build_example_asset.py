r"""Build the fully-skinned example clothing asset INSIDE Maya 2026.

The shipped ``assets/trench_coat_A/trench_coat_A.ma`` is a hand-authored *structural*
reference (correct hierarchy / joints / fit control / info, placeholder geometry, no
skinCluster). Vertex and skin data cannot be hand-authored reliably, so this script is
the authoritative generator for the *production* version: it builds real geometry,
smooth-binds it to the ``cloth_*`` joints, wires a fit lattice to the ``cloth_fit_ctrl``
``fit_*`` attributes, populates ``cloth_info``, and exports a clean Maya ASCII asset.

IMPORTANT — this build REQUIRES the GenHuman rig in the scene.
------------------------------------------------------------------
Snap-on attach connects ``translate``/``rotate``/``scale`` only — never ``jointOrient``
— so a garment's ``cloth_*`` skeleton must be a *faithful duplicate* of the body's
export skeleton: identical joint positions AND identical jointOrient. (The UE/Epic
skeleton orients every joint, e.g. pelvis jointOrient ``-90 3.6 90``.) An invented
"stick" skeleton with identity orientation will lay on the ground and crumple the mesh
when driven by the real rig. So this script duplicates the live export-skeleton joints
under ``GenHuman_Joint_GRP`` (the exact joints attach connects FROM), renames them
``cloth_*``, then builds and skins the garment onto that real-oriented skeleton.

The repo lives in WSL (Ubuntu-24.04). Windows Maya can import this module directly
over the WSL UNC path — no need to copy the file onto the Windows drive. Because
``_default_out_path()`` resolves relative to ``__file__``, the exported ``.ma`` is
written straight back into the WSL repo's ``assets/`` folder.

Run it from Maya's Script Editor (Python)::

    # 1) Import the GenHuman rig first (File > Import, "use namespaces" ON).
    # 2) Then:
    import sys
    sys.path.append(r"\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\maya_clothing_rig")
    import examples.build_example_asset as b
    import importlib; importlib.reload(b)
    b.build()                       # -> assets/trench_coat_A/trench_coat_A.ma (overwrites)

The asset is exported with *export-selected* (just the garment top group + its info
node), so the GenHuman rig is never written into the asset file, and the duplicated
joints land in the root namespace with clean, namespace-free names.

(If ``\\wsl.localhost`` doesn't resolve on an older Windows build, use the legacy
``\\wsl$\Ubuntu-24.04\...`` prefix instead. From a native Linux Maya, just append the
POSIX path ``/home/sgold/dev/repos/maya_clothing_rig``.)

It is intentionally NOT part of the headless test suite (it needs a running Maya); CI
only ``py_compile``s it. Everything it produces still satisfies
``Clothing Asset Authoring Spec.md`` and the tool's validator.
"""
from __future__ import annotations

import os

import maya.cmds as cmds

ASSET_NAME = "trench_coat_A"
TOP = f"cloth_{ASSET_NAME}"

# The rig's export-skeleton group (matches snap_on_clothing.config.EXPORT_SKELETON_GROUP).
# attach connects FROM these joints, so the garment must duplicate exactly these.
_EXPORT_GROUP = "GenHuman_Joint_GRP"

# Body joints the garment skins to (EXACT body short name, cloth_ prefixed). These are a
# subset of the full duplicated skeleton; the rest of the duplicated joints stay in the
# asset (and connect harmlessly at attach) but carry no skin weight. Missing names are
# skipped, so the script tolerates minor skeleton differences across rig versions.
_SKIN_JOINTS = [
    "cloth_root", "cloth_pelvis",
    "cloth_spine_01", "cloth_spine_02", "cloth_spine_03", "cloth_spine_04", "cloth_spine_05",
    "cloth_neck_01", "cloth_neck_02",
    "cloth_clavicle_l", "cloth_upperarm_l", "cloth_lowerarm_l", "cloth_hand_l",
    "cloth_clavicle_r", "cloth_upperarm_r", "cloth_lowerarm_r", "cloth_hand_r",
    "cloth_thigh_l", "cloth_calf_l", "cloth_foot_l", "cloth_ball_l",
    "cloth_thigh_r", "cloth_calf_r", "cloth_foot_r", "cloth_ball_r",
]

# Helper joints (secondary motion — coat tails). NOT body joints, so the tool never
# wires them to the rig. Built as children with a parent-relative offset (down + back),
# so they sit correctly regardless of the real spine's world position/orientation.
_HELPER_JOINTS = [
    ("cloth_coatTail_01", "cloth_spine_01", (0, -6, -10)),
    ("cloth_coatTail_02", "cloth_coatTail_01", (0, -28, -2)),
]

# fit attrs on cloth_fit_ctrl: (name, min, max, default)
_FIT_ATTRS = [
    ("fit_tightness", -1.0, 1.0, 0.0),
    ("fit_thickness", 0.0, 1.0, 0.0),
    ("fit_length", -1.0, 1.0, 0.0),
    ("fit_hem_length", -1.0, 1.0, 0.0),
    ("fit_collar_tightness", -1.0, 1.0, 0.0),
]

# Names the build authors, cleared at the start of a run so re-running is idempotent.
_BUILD_ROOTS = ("cloth_*", "Mesh_GRP", "Rig_GRP", "Ctrl_GRP", TOP)


def _default_out_path() -> str:
    try:
        here = os.path.dirname(os.path.abspath(__file__))
    except NameError:
        # __file__ is undefined when the script body is pasted straight into the
        # Script Editor instead of imported. We can't locate the repo, so tell the
        # user how to run it (import it, or pass an explicit out_path).
        raise RuntimeError(
            "Can't find the repo automatically — run this by importing it rather than "
            "pasting the code into the Script Editor:\n"
            "    import sys\n"
            "    sys.path.append(r'\\\\wsl.localhost\\Ubuntu-24.04\\home\\sgold\\dev"
            "\\repos\\maya_clothing_rig')\n"
            "    import examples.build_example_asset as b; b.build()\n"
            "…or pass the output path explicitly:\n"
            "    b.build(out_path=r'\\\\wsl.localhost\\Ubuntu-24.04\\home\\sgold\\dev"
            f"\\repos\\maya_clothing_rig\\assets\\{ASSET_NAME}\\{ASSET_NAME}.ma')"
        )
    repo = os.path.dirname(here)
    return os.path.join(repo, "assets", ASSET_NAME, f"{ASSET_NAME}.ma")


# --------------------------------------------------------------------------- #
# Skeleton — duplicated from the live GenHuman export skeleton
# --------------------------------------------------------------------------- #
def _find_export_root() -> tuple[str, str]:
    """``(root joint, export group)`` full DAG paths, in any namespace.

    Finds the ``GenHuman_Joint_GRP`` transform by SHORT name across every namespace
    (root, single, or nested) — robust where namespace-wildcard ``ls`` patterns are
    not — and returns its child root joint together with the group itself. Prefers a
    selected rig when the user has one of its nodes selected; otherwise takes the
    first rig found. Raises with a clear message if the rig is absent.
    """
    def _short(path: str) -> str:
        return path.rsplit("|", 1)[-1].rsplit(":", 1)[-1]

    groups = [
        t for t in (cmds.ls(type="transform", long=True) or [])
        if _short(t) == _EXPORT_GROUP
    ]
    if not groups:
        raise RuntimeError(
            f"GenHuman rig not found (no '{_EXPORT_GROUP}' in the scene). "
            "Import the GenHuman rig first (File > Import, 'use namespaces' ON), "
            "then run build()."
        )
    # If a rig node is selected, prefer the group in that selection's namespace.
    grp = groups[0]
    sel = cmds.ls(selection=True, long=True) or []
    if sel:
        sel_short = sel[0].rsplit("|", 1)[-1]
        sel_ns = sel_short.split(":", 1)[0] if ":" in sel_short else ""
        for g in groups:
            g_short = g.rsplit("|", 1)[-1]
            g_ns = g_short.split(":", 1)[0] if ":" in g_short else ""
            if g_ns == sel_ns:
                grp = g
                break
    roots = cmds.listRelatives(grp, children=True, type="joint", fullPath=True) or []
    if not roots:
        raise RuntimeError(f"export group '{grp}' has no child joint (expected 'root').")
    return roots[0], grp


def _rename_tree(orig: str, dup: str) -> None:
    """Rename a duplicated joint subtree to ``cloth_<body name>``, mirroring ``orig``.

    Walks the original and duplicate trees in lockstep (duplicate preserves child
    order), so each cloth joint gets the exact body short name regardless of how
    Maya mangled the duplicate's names.
    """
    short = orig.rsplit("|", 1)[-1].rsplit(":", 1)[-1]
    dup = cmds.rename(dup, f"cloth_{short}")
    orig_children = cmds.listRelatives(orig, children=True, type="joint", fullPath=True) or []
    dup_children = cmds.listRelatives(dup, children=True, type="joint", fullPath=True) or []
    for o, d in zip(orig_children, dup_children):
        _rename_tree(o, d)


def _build_skeleton_from_rig() -> str:
    """Duplicate the live export skeleton into a clean ``cloth_*`` skeleton on ``Rig_GRP``.

    The duplicate inherits every joint's real LOCAL transform and jointOrient unchanged
    (never baked), and ``Rig_GRP`` is aligned to the rig's export-skeleton group world
    frame — which carries a -90 X rotation. So at skin time the cloth skeleton sits
    upright on the body, and at attach the same frame alignment lets the local-transform
    connections reproduce the body pose exactly. The rig itself is untouched.
    """
    orig_root, export_grp = _find_export_root()
    dup = cmds.duplicate(orig_root, returnRootsOnly=True, renameChildren=True)[0]
    # Detach into world space but KEEP local values (relative=True): never bake the
    # group's -90 X into the joints, or attach (which overwrites translate/rotate but
    # not jointOrient) can't reproduce the body and the garment lands on the ground.
    if cmds.listRelatives(dup, parent=True, fullPath=True):
        dup = cmds.parent(dup, world=True, relative=True)[0]
    _rename_tree(orig_root, dup)
    # drop anything non-joint the duplicate dragged along (end effectors, shapes, etc.)
    extras = [
        n for n in (cmds.listRelatives("cloth_root", allDescendents=True, fullPath=True) or [])
        if cmds.nodeType(n) != "joint"
    ]
    if extras:
        cmds.delete(extras)
    # Build Rig_GRP on the export group's world frame, then re-parent the skeleton
    # under it keeping local values — restoring the joints to their real body pose.
    cmds.group(empty=True, name="Rig_GRP")
    m = cmds.xform(export_grp, query=True, worldSpace=True, matrix=True)
    cmds.xform("Rig_GRP", worldSpace=True, matrix=m)
    cmds.parent("cloth_root", "Rig_GRP", relative=True)
    # secondary-motion helper joints (not body joints; never auto-connected)
    for name, parent, rel in _HELPER_JOINTS:
        if not cmds.objExists(parent):
            continue
        cmds.select(parent)
        cmds.joint(name=name, relative=True, position=rel)
    cmds.select(clear=True)
    return export_grp


def _build_geometry():
    # Trench-coat-length body: from the shoulders (~152) down past the knees to
    # mid-calf (~48), so the coat drapes the torso and upper legs (skinned to spine/
    # pelvis/thigh/calf) rather than reading as a small box at the waist.
    jacket = cmds.polyCube(name="cloth_jacket_mesh", w=52, h=92, d=32)[0]
    collar = cmds.polyCube(name="cloth_collar_mesh", w=28, h=10, d=24)[0]
    meshes = [jacket, collar]

    # Position each garment then FREEZE the translate into the vertices, so the geometry
    # truly lives there in object space with an identity transform — no stray ``.pnts``
    # tweak, no transform offset for the skinCluster to lock around (spec §9: no history,
    # no tweaks). Order matters: delete the polyCube construction node FIRST, otherwise
    # the live creator regenerates the verts at the origin and defeats the freeze (the
    # reason an earlier xform()+makeIdentity left everything at the origin). Freezing also
    # only works while the mesh is still unbound — once skinCluster locks the transform
    # channels makeIdentity refuses (see _organize), so this must run before _bind.
    cmds.delete(meshes, constructionHistory=True)
    cmds.move(0, 94, 0, jacket)    # spans y=48..140: mid-calf up to the shoulders
    cmds.move(0, 146, -1, collar)  # spans y=141..151: neck base, below the head
    cmds.makeIdentity(meshes, apply=True, translate=True, rotate=True, scale=True)
    return meshes


def _bind(meshes) -> None:
    # Skin only to the joints that actually exist in this rig's skeleton (tolerate
    # minor cross-version differences); the rest of the duplicated joints carry no skin.
    skin_joints = [j for j in _SKIN_JOINTS if cmds.objExists(j)]
    for mesh in meshes:
        cmds.skinCluster(
            skin_joints, mesh,
            toSelectedBones=True, bindMethod=0, skinMethod=0,
            name=f"{mesh}_skinCluster",
        )


def _build_fit_control_and_lattice(meshes) -> str:
    ctrl = cmds.group(empty=True, name="cloth_fit_ctrl")
    for name, lo, hi, dv in _FIT_ATTRS:
        cmds.addAttr(ctrl, longName=name, attributeType="double",
                     minValue=lo, maxValue=hi, defaultValue=dv, keyable=True)

    # one self-contained lattice over the garment, driven by the fit attrs (spec §7/§8:
    # fit is normal/lattice based, never shrinkWrap-to-body). SDK so the rig responds
    # to the attrs the tool writes; the tool only sets values, it builds none of this.
    # frontOfChain: the lattice must deform the garment's REST shape BEFORE the
    # skinCluster, so the skin then carries the fitted shape onto the animated body.
    # As an end-of-chain (post-skin) deformer it only lines up at the bind pose and is
    # left behind once the rig animates.
    ffd, lattice, base = cmds.lattice(
        meshes, divisions=(2, 6, 2), objectCentered=True, frontOfChain=True,
        name="cloth_fit_ffd")
    # objectCentered sizes the lattice transform to the garment bounding box, so its
    # NEUTRAL scale is the bbox dimensions (e.g. ~52×108×32), NOT 1.0 — and the base
    # lattice carries the same scale as the undeformed reference. The fit attrs must
    # therefore drive the lattice scale *relative to that neutral*; writing an absolute
    # scaleX of ~1.0 collapses the lattice to a unit cube against its bbox-sized base
    # and crushes the whole garment into a ~1-unit blob. Capture neutral, drive by factor.
    sx0 = cmds.getAttr(f"{lattice}.scaleX")
    sy0 = cmds.getAttr(f"{lattice}.scaleY")
    sz0 = cmds.getAttr(f"{lattice}.scaleZ")
    # tightness: squeeze the lattice in X/Z toward the body
    for val, factor in ((-1.0, 1.08), (0.0, 1.0), (1.0, 0.92)):
        cmds.setAttr(f"{ctrl}.fit_tightness", val)
        cmds.setAttr(f"{lattice}.scaleX", sx0 * factor)
        cmds.setAttr(f"{lattice}.scaleZ", sz0 * factor)
        cmds.setDrivenKeyframe(f"{lattice}.scaleX", currentDriver=f"{ctrl}.fit_tightness")
        cmds.setDrivenKeyframe(f"{lattice}.scaleZ", currentDriver=f"{ctrl}.fit_tightness")
    # length: scale the lattice along Y (hem / sleeve length)
    for val, factor in ((-1.0, 0.9), (0.0, 1.0), (1.0, 1.1)):
        cmds.setAttr(f"{ctrl}.fit_length", val)
        cmds.setAttr(f"{lattice}.scaleY", sy0 * factor)
        cmds.setDrivenKeyframe(f"{lattice}.scaleY", currentDriver=f"{ctrl}.fit_length")
    for name, _lo, _hi, dv in _FIT_ATTRS:
        cmds.setAttr(f"{ctrl}.{name}", dv)  # leave everything neutral

    # secondary animator control (stays accessible after attach)
    tail = cmds.group(empty=True, name="cloth_coatTail_ctrl")
    cmds.addAttr(tail, longName="swing", attributeType="double",
                 minValue=-10, maxValue=10, defaultValue=0, keyable=True)
    return lattice, base, ctrl, tail


def _build_info_node() -> str:
    info = cmds.createNode("network", name="cloth_info")
    strings = {
        "assetName": ASSET_NAME,
        "assetType": "coat",
        "clothVersion": "1.0.0",
        "genHumanCompat": "v03",
        "author": "Snap-On Clothing (example)",
        "notes": "Generated by examples/build_example_asset.py — skinned + fit lattice.",
    }
    for attr, value in strings.items():
        cmds.addAttr(info, longName=attr, dataType="string")
        cmds.setAttr(f"{info}.{attr}", value, type="string")
    return info


def _organize(meshes, lattice_nodes) -> None:
    lattice, base, ctrl, tail = lattice_nodes
    # Rig_GRP already exists (built on the rig's frame in _build_skeleton_from_rig);
    # grouping preserves its world transform.
    cmds.group(empty=True, name="Mesh_GRP")
    cmds.group(empty=True, name="Ctrl_GRP")
    cmds.parent(meshes, "Mesh_GRP")
    cmds.parent([ctrl, tail, lattice, base], "Ctrl_GRP")
    cmds.group("Mesh_GRP", "Rig_GRP", "Ctrl_GRP", name=TOP)
    # The groups are created empty at the origin, so their transforms are already
    # identity (spec §3/§14) — nothing to freeze. Don't makeIdentity the hierarchy:
    # it cascades into the skinned meshes, whose transform channels skinCluster locks,
    # and Maya raises "Freeze Transform was not applied because … is locked".


def _clear_previous_build() -> None:
    """Delete any nodes a prior run authored, so build() is idempotent in a live scene."""
    for node in (cmds.ls(*_BUILD_ROOTS) or []):
        if cmds.objExists(node):
            try:
                cmds.delete(node)
            except Exception:  # noqa: BLE001 — already removed with an ancestor
                pass


def _rig_nodes() -> list[str]:
    """Every node still carrying the GenHuman rig name (DAG or DG, any namespace)."""
    return [n for n in (cmds.ls(long=True) or []) if "GenHuman" in n.rsplit("|", 1)[-1]]


def _delete_rig(export_grp: str) -> None:
    """Remove the GenHuman rig from the scene so a whole-scene save writes only the asset.

    The cloth skeleton is a standalone duplicate (never connected to the rig before
    attach), so deleting the rig is safe — and a plain whole-scene save then round-trips
    the skinned + lattice-deformed meshes cleanly, where ``exportSelected`` corrupts the
    deformer chain ('invalid components' / data-loss on re-import).

    Deletes the rig in three robust passes (the rig has ~2400 DG 'guts' nodes — matrix /
    condition / set / material / controller — and nested namespaces, on which
    ``deleteNamespaceContent`` silently throws and leaks the lot): drop the DAG, then
    sweep every node whose name carries 'GenHuman' (unlocking first; a few passes, since
    deleting some frees others), then drop the now-empty rig namespaces. Finally it
    HARD-FAILS if anything rig-shaped survives, so a polluted asset is never saved.
    """
    top = export_grp
    while True:
        parent = cmds.listRelatives(top, parent=True, fullPath=True)
        if not parent:
            break
        top = parent[0]
    if cmds.objExists(top):
        cmds.delete(top)

    for _ in range(4):  # deleting some nodes frees others held by connections
        nodes = _rig_nodes()
        if not nodes:
            break
        for n in nodes:
            try:
                cmds.lockNode(n, lock=False)
            except Exception:  # noqa: BLE001
                pass
        try:
            cmds.delete(nodes)
        except Exception:  # noqa: BLE001 — keep sweeping; the final check guards us
            pass

    for ns in sorted((cmds.namespaceInfo(":", listOnlyNamespaces=True, recurse=True) or []),
                     key=len, reverse=True):  # deepest namespace first
        if ns.lstrip(":").split(":", 1)[0].startswith("GenHuman") and cmds.namespace(exists=ns):
            try:
                cmds.namespace(removeNamespace=ns)
            except Exception:  # noqa: BLE001
                pass

    leftover = _rig_nodes()
    if leftover:
        raise RuntimeError(
            f"rig cleanup incomplete: {len(leftover)} GenHuman node(s) remain "
            f"(e.g. {leftover[:3]}) — aborting before save to avoid a polluted asset."
        )


def build(out_path: str | None = None) -> str:
    """Build the asset onto the in-scene GenHuman rig and export it (Maya ASCII).

    Requires the GenHuman rig in the current scene. Does NOT new-scene (it needs the
    rig); instead it clears any previous build, authors the garment onto a duplicate of
    the rig's skeleton, deletes the rig, and saves the whole (now asset-only) scene.
    """
    out_path = out_path or _default_out_path()

    _clear_previous_build()
    export_grp = _build_skeleton_from_rig()
    meshes = _build_geometry()
    _bind(meshes)
    lattice_nodes = _build_fit_control_and_lattice(meshes)
    _build_info_node()
    _organize(meshes, lattice_nodes)

    # Drop the rig, then save the whole scene — now just the asset (+ Maya defaults).
    # A plain scene save round-trips the deformer chain cleanly; exportSelected does not.
    _delete_rig(export_grp)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cmds.file(rename=out_path)
    cmds.file(save=True, type="mayaAscii", force=True)
    print(f"[build_example_asset] exported {out_path}")
    return out_path


if __name__ == "__main__":
    build()
