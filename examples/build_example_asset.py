r"""Build the fully-skinned example clothing asset INSIDE Maya 2026.

The shipped ``assets/trench_coat_A/trench_coat_A.ma`` is a hand-authored *structural*
reference (correct hierarchy / joints / fit control / info, placeholder geometry, no
skinCluster). Vertex and skin data cannot be hand-authored reliably, so this script is
the authoritative generator for the *production* version: it builds real geometry,
smooth-binds it to the ``cloth_*`` joints, wires a fit lattice to the ``cloth_fit_ctrl``
``fit_*`` attributes, populates ``cloth_info``, and exports a clean Maya ASCII asset.

The repo lives in WSL (Ubuntu-24.04). Windows Maya can import this module directly
over the WSL UNC path — no need to copy the file onto the Windows drive. Because
``_default_out_path()`` resolves relative to ``__file__``, the exported ``.ma`` is
written straight back into the WSL repo's ``assets/`` folder.

Run it from Maya's Script Editor (Python)::

    import sys
    sys.path.append(r"\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\maya_clothing_rig")
    import examples.build_example_asset as b
    b.build()                       # -> assets/trench_coat_A/trench_coat_A.ma (overwrites)

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

# (joint name, parent joint name, world translate). Names are EXACT body names with a
# cloth_ prefix; coatTail_* are helper joints (the tool never wires them to the body).
_JOINTS = [
    ("cloth_root", None, (0, 0, 0)),
    ("cloth_pelvis", "cloth_root", (0, 97, 0)),
    ("cloth_spine_01", "cloth_pelvis", (0, 102, 0)),
    ("cloth_spine_02", "cloth_spine_01", (0, 108, 0)),
    ("cloth_spine_03", "cloth_spine_02", (0, 114, 0)),
    ("cloth_spine_04", "cloth_spine_03", (0, 120, 0)),
    ("cloth_spine_05", "cloth_spine_04", (0, 126, 0)),
    ("cloth_neck_01", "cloth_spine_05", (0, 150, 0)),
    ("cloth_neck_02", "cloth_neck_01", (0, 154, 0)),
    ("cloth_clavicle_l", "cloth_spine_05", (3, 144, 0)),
    ("cloth_upperarm_l", "cloth_clavicle_l", (18, 144, 0)),
    ("cloth_lowerarm_l", "cloth_upperarm_l", (45, 144, 0)),
    ("cloth_hand_l", "cloth_lowerarm_l", (71, 144, 0)),
    ("cloth_clavicle_r", "cloth_spine_05", (-3, 144, 0)),
    ("cloth_upperarm_r", "cloth_clavicle_r", (-18, 144, 0)),
    ("cloth_lowerarm_r", "cloth_upperarm_r", (-45, 144, 0)),
    ("cloth_hand_r", "cloth_lowerarm_r", (-71, 144, 0)),
    ("cloth_thigh_l", "cloth_pelvis", (9, 95, 0)),
    ("cloth_calf_l", "cloth_thigh_l", (9, 53, 0)),
    ("cloth_foot_l", "cloth_calf_l", (9, 11, 2)),   # ankle, near the ground
    ("cloth_ball_l", "cloth_foot_l", (9, 3, 12)),   # toe, forward (+Z)
    ("cloth_thigh_r", "cloth_pelvis", (-9, 95, 0)),
    ("cloth_calf_r", "cloth_thigh_r", (-9, 53, 0)),
    ("cloth_foot_r", "cloth_calf_r", (-9, 11, 2)),
    ("cloth_ball_r", "cloth_foot_r", (-9, 3, 12)),
    # helper joints (secondary motion — coat tails), parented under a cloth_ joint
    ("cloth_coatTail_01", "cloth_spine_01", (0, 94, -10)),
    ("cloth_coatTail_02", "cloth_coatTail_01", (0, 64, -12)),
]

# fit attrs on cloth_fit_ctrl: (name, min, max, default)
_FIT_ATTRS = [
    ("fit_tightness", -1.0, 1.0, 0.0),
    ("fit_thickness", 0.0, 1.0, 0.0),
    ("fit_length", -1.0, 1.0, 0.0),
    ("fit_hem_length", -1.0, 1.0, 0.0),
    ("fit_collar_tightness", -1.0, 1.0, 0.0),
]

_SKIN_JOINTS = [j[0] for j in _JOINTS if not j[0].startswith("cloth_coatTail")]


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


def _build_skeleton() -> None:
    for name, parent, pos in _JOINTS:
        cmds.select(clear=True)
        if parent is not None:
            cmds.select(parent)
        cmds.joint(name=name, position=pos)  # absolute world position


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
    for mesh in meshes:
        cmds.skinCluster(
            _SKIN_JOINTS, mesh,
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
    ffd, lattice, base = cmds.lattice(
        meshes, divisions=(2, 6, 2), objectCentered=True, name="cloth_fit_ffd")
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
    cmds.group(empty=True, name="Mesh_GRP")
    cmds.group(empty=True, name="Rig_GRP")
    cmds.group(empty=True, name="Ctrl_GRP")
    cmds.parent(meshes, "Mesh_GRP")
    cmds.parent("cloth_root", "Rig_GRP")
    cmds.parent([ctrl, tail, lattice, base], "Ctrl_GRP")
    cmds.group("Mesh_GRP", "Rig_GRP", "Ctrl_GRP", name=TOP)
    # The groups are created empty at the origin, so their transforms are already
    # identity (spec §3/§14) — nothing to freeze. Don't makeIdentity the hierarchy:
    # it cascades into the skinned meshes, whose transform channels skinCluster locks,
    # and Maya raises "Freeze Transform was not applied because … is locked".


def build(out_path: str | None = None) -> str:
    """Build the asset in a fresh scene and export it to ``out_path`` (Maya ASCII)."""
    out_path = out_path or _default_out_path()
    cmds.file(new=True, force=True)

    _build_skeleton()
    meshes = _build_geometry()
    _bind(meshes)
    lattice_nodes = _build_fit_control_and_lattice(meshes)
    _build_info_node()
    _organize(meshes, lattice_nodes)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cmds.file(rename=out_path)
    cmds.file(save=True, type="mayaAscii", force=True)
    print(f"[build_example_asset] exported {out_path}")
    return out_path


if __name__ == "__main__":
    build()
