"""In-Maya checks for the code the headless suite can't run (``maya.cmds`` paths).

Run with Maya's interpreter, not pytest::

    mayapy tests/maya_checks.py

Each check builds a small scene from scratch in ``maya.standalone`` and exits non-zero
on the first failure. Covers the retarget rename pass and the rig-marker matching that
must never count or delete the garment's own nodes.
"""
from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import maya.standalone  # noqa: E402

maya.standalone.initialize()
import maya.cmds as cmds  # noqa: E402

# Maya's startup may already have imported an *installed* Outfitter; test this checkout.
for _name in [n for n in sys.modules if n == "outfitter" or n.startswith("outfitter.")]:
    del sys.modules[_name]
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from outfitter import config  # noqa: E402
from outfitter.core import maya_publish, maya_retarget, maya_testfit, rigs  # noqa: E402

MARKERS = ("MichaelC_Joint_GRP", "MichaelC")


def _joint(name, parent=None):
    cmds.select(clear=True)
    j = cmds.joint(name=name)
    return cmds.parent(j, parent)[0] if parent else j


def _garment():
    """A MichaelC_pantsA-style garment: every node named after the rig's marker."""
    top = cmds.group(empty=True, name="cloth_MichaelC_pantsA")
    mesh_grp = cmds.group(empty=True, name=config.MESH_GROUP, parent=top)
    rig_grp = cmds.group(empty=True, name=config.RIG_GROUP, parent=top)
    cmds.group(empty=True, name=config.CTRL_GROUP, parent=top)
    root = _joint("cloth_root", rig_grp)
    _joint("cloth_MichaelC_hip", root)
    geo = cmds.polyCube(name="MichaelC_pants_geo")[0]
    cmds.parent(geo, mesh_grp)
    cmds.skinCluster(root, geo, name="MichaelC_pants_skin")
    mat = cmds.shadingNode("lambert", asShader=True, name="MichaelC_pants_mat")
    sg = cmds.sets(renderable=True, noSurfaceShader=True, empty=True, name="MichaelC_pants_SG")
    cmds.connectAttr(f"{mat}.outColor", f"{sg}.surfaceShader")
    cmds.sets(geo, edit=True, forceElement=sg)
    cmds.createNode("network", name=config.INFO_NODE)
    return set(cmds.ls(cmds.listRelatives(top, allDescendents=True, fullPath=True) + [top]
                       + ["MichaelC_pants_skin", mat, sg, config.INFO_NODE], uuid=True))


def _rig(top_name="MichaelC_rig"):
    top = cmds.group(empty=True, name=top_name)
    grp = cmds.group(empty=True, name="MichaelC_Joint_GRP", parent=top)
    _joint("root", grp)
    cmds.shadingNode("lambert", asShader=True, name="MichaelC_skin_mat")
    return top


def check_rig_markers_spare_the_garment():
    cmds.file(new=True, force=True)
    garment = _garment()
    _rig()
    assert maya_publish.scene_has_rig(MARKERS), "rig in scene must be detected"

    profile = SimpleNamespace(markers=MARKERS)
    assert maya_testfit._delete_rig(cmds, profile) >= 1, "rig was not deleted"

    survivors = set(cmds.ls(list(cmds.ls(garment, long=True) or []), uuid=True))
    assert survivors == garment, f"garment nodes deleted: {len(garment - survivors)}"
    assert not cmds.objExists("MichaelC_Joint_GRP") and not cmds.objExists("MichaelC_skin_mat")
    assert not maya_publish.scene_has_rig(MARKERS), "garment alone read as a rig"


def check_rig_top_named_like_a_garment_group_is_still_a_rig():
    cmds.file(new=True, force=True)
    garment = _garment()
    _rig(top_name=config.RIG_GROUP)  # |Rig_GRP|MichaelC_Joint_GRP: the rig, not garment

    assert maya_publish.scene_has_rig(MARKERS)
    maya_testfit._delete_rig(cmds, SimpleNamespace(markers=MARKERS))

    assert not cmds.objExists("MichaelC_Joint_GRP"), "rig under a Rig_GRP top survived"
    assert set(cmds.ls(list(cmds.ls(garment, long=True)), uuid=True)) == garment


def check_retarget_renames_parents_and_children():
    cmds.file(new=True, force=True)
    rig_grp = cmds.group(empty=True, name=config.RIG_GROUP)
    a = _joint("cloth_GM_spine_01", rig_grp)
    b = _joint("cloth_GM_spine_02", a)
    _joint("cloth_GM_spine_03", b)
    _joint("cloth_l_arm", a)
    _joint("cloth_r_arm", a)

    renames = [("cloth_GM_spine_01", "cloth_spine_01"), ("cloth_GM_spine_02", "cloth_spine_02"),
               ("cloth_GM_spine_03", "cloth_spine_03"),
               ("cloth_l_arm", "cloth_r_arm"), ("cloth_r_arm", "cloth_l_arm")]  # a swap
    plan = SimpleNamespace(renames=[SimpleNamespace(source=s, target=t) for s, t in renames])
    in_scene = maya_retarget.scene_cloth_joints()

    assert maya_retarget._rename_joints(cmds, plan, in_scene) == len(renames)
    names = set(maya_retarget.scene_cloth_joints())
    assert names == {"cloth_spine_01", "cloth_spine_02", "cloth_spine_03",
                     "cloth_l_arm", "cloth_r_arm"}, names
    assert cmds.listRelatives("cloth_spine_02", parent=True) == ["cloth_spine_01"]


def check_attach_then_detach_with_the_real_rig_and_asset():
    """Same session (registry) and a fresh engine (after a reload) must both detach.

    A scene with no poseInterpolatorManager/shapeEditorManager of its own adopts the
    garment's copies, which Maya won't delete - that used to fail every detach.
    """
    from outfitter.core import library
    from outfitter.core.attach import AttachEngine
    from outfitter.core.scene import MayaScene

    repo = Path(__file__).resolve().parents[1]
    asset = library.load_asset(repo / "assets" / "trench_coat_A" / "trench_coat_A.ma")
    profile = rigs.find_profile("genhuman")
    for fresh_engine in (False, True):
        cmds.file(new=True, force=True)
        cmds.file(str(repo / "scripts" / "outfitter" / "lib" / "GenHuman_rig_v03.ma"), i=True)
        engine = AttachEngine(MayaScene())
        res = engine.attach(asset, "coat", profile=profile)
        assert res.ok, [str(i) for i in res.report.errors]
        if fresh_engine:
            engine = AttachEngine(MayaScene())
        assert engine.attached_namespaces() == ["coat"]
        res = engine.detach("coat")
        assert res.ok, [str(i) for i in res.report.errors]
        assert not cmds.namespace(exists="coat") and not cmds.ls("coat:*", recursive=True)
        assert cmds.objExists(profile.export_group), "detach touched the rig"


def check_root_joint_for_registered_rigs():
    assert rigs.root_joint(rigs.find_profile("genhuman")) == config.ROOT_JOINT


CHECKS = [check_rig_markers_spare_the_garment,
          check_rig_top_named_like_a_garment_group_is_still_a_rig,
          check_retarget_renames_parents_and_children,
          check_attach_then_detach_with_the_real_rig_and_asset,
          check_root_joint_for_registered_rigs]

if __name__ == "__main__":
    failed = 0
    for check in CHECKS:
        try:
            check()
            print(f"PASS {check.__name__}")
        except Exception as exc:  # noqa: BLE001 - report every check, then fail
            failed += 1
            print(f"FAIL {check.__name__}: {type(exc).__name__}: {exc}")
    import outfitter
    print(f"{len(CHECKS) - failed}/{len(CHECKS)} passed (outfitter from {outfitter.__file__})")
    maya.standalone.uninitialize()
    sys.exit(1 if failed else 0)
