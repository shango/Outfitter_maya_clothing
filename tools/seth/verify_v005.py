"""Reload Seth v00.4 and v00.5 in Maya and prove the rename changed nothing but names. Read-only.

    mayapy.exe verify_v005.py <Seth_rig_v00.4.ma> <Seth_rig_v00.5.ma> <out.json>
"""
import json, sys, math
import maya.standalone
maya.standalone.initialize()
from maya import cmds
from maya.api import OpenMaya as om, OpenMayaAnim as oma
REPO = r"\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\Outfitter_maya_clothing"
sys.path.insert(0, REPO + r"\scripts")
from pathlib import Path
from outfitter.core import rigs, maya_rigs, maya_skeleton, maya_testfit, maya_publish
from outfitter.core.attach import sanitize_namespace
v004, v005, out = sys.argv[1:4]
POSE = [("Seth_spine_m_02_anim", "r", (10, 5, 15)), ("Seth_head_m_head_anim", "r", (0, 25, 10)),
        ("Seth_arm_l_upperarm_fk_anim", "r", (0, 30, 40)), ("Seth_arm_l_lowerarm_fk_anim", "r", (0, 0, 60)),
        ("Seth_arm_r_hand_ik_anim", "t", (10, -15, 20)), ("Seth_leg_l_foot_ik_anim", "t", (5, 20, 15)),
        ("Seth_leg_r_thigh_fk_anim", "r", (20, 0, 10)), ("Seth_god_m_godnode_anim", "t", (30, 0, -20))]

def load(f):
    errs = ""
    try: cmds.file(f, open=True, force=True, prompt=False)
    except RuntimeError as e: errs = str(e)
    lines = [l.split(": ", 1)[-1] for l in errs.splitlines() if l.strip() and "Error reading file" not in l]
    return sorted(set(l.split(" line ")[-1].split(": ", 1)[-1] for l in lines))

def snap(f, body, egname):
    S = {"load_errors": load(f), "nodes": len(cmds.ls()), "unknown": cmds.ls(type="unknown"),
         "dag": len(cmds.ls(dag=True)), "connections": len(cmds.listConnections(cmds.ls(), c=True, p=True) or []) // 2}
    sc = cmds.ls(cmds.listHistory(body), type="skinCluster")[0]
    sel = om.MSelectionList(); sel.add(sc); fn = oma.MFnSkinCluster(sel.getDependNode(0))
    s2 = om.MSelectionList(); s2.add(body); dag = s2.getDagPath(0)
    w, n = fn.getWeights(dag, om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent))
    S["weights"] = list(w); S["n_infl"] = n
    S["infl"] = [p.partialPathName().rsplit("|", 1)[-1] for p in fn.influenceObjects()]
    S["infl_group"] = sorted(set(p.fullPathName().split("|")[2] for p in fn.influenceObjects()))
    mf = om.MFnMesh(dag)
    S["rest"] = [(p.x, p.y, p.z) for p in mf.getPoints(om.MSpace.kWorld)]
    for c, a, v in POSE:
        for ax, x in zip("xyz", v): cmds.setAttr("%s.%s%s" % (c, a, ax), x)
    S["posed"] = [(p.x, p.y, p.z) for p in mf.getPoints(om.MSpace.kWorld)]
    S["posed_joints"] = {j.rsplit("|", 1)[-1]: cmds.xform(j, q=True, ws=True, t=True)
                         for j in cmds.listRelatives(egname, ad=True, type="joint", fullPath=True)}
    return S

R = {}
A = snap(v004, "Seth_bodyShape", "Skeleton")
B = snap(v005, "Seth_body_meshShape", "Seth_Joint_GRP")
for k in ("load_errors", "nodes", "unknown", "dag", "connections", "n_infl", "infl", "infl_group"):
    R[k] = [A[k], B[k]] if A[k] != B[k] else ["same", A[k] if k not in ("infl",) else len(A[k])]
R["weights_max_diff"] = max(abs(a - b) for a, b in zip(A["weights"], B["weights"]))
R["rest_max_diff"] = max(math.dist(a, b) for a, b in zip(A["rest"], B["rest"]))
R["posed_max_diff"] = max(math.dist(a, b) for a, b in zip(A["posed"], B["posed"]))
R["posed_mesh_moved"] = max(math.dist(a, b) for a, b in zip(B["rest"], B["posed"]))
R["posed_joint_max_diff"] = max(math.dist(A["posed_joints"][j], B["posed_joints"][j]) for j in A["posed_joints"])

# fresh v00.5 state for the Outfitter checks
load(v005)
R["old_names_left"] = {n: cmds.ls(n) for n in ("Skeleton", "Geo", "Seth_body", "Seth_bodyShape")}
R["new_names"] = {n: cmds.ls(n, long=True) for n in ("Seth", "Seth_Joint_GRP", "Seth_Mesh_GRP", "Seth_body_mesh")}
bad = []
for n in cmds.ls():
    for a in cmds.listAttr(n, string=["skeletonRoot", "characterRoot", "artistControl", "diSourceRoot", "diRig*"]) or []:
        try:
            v = cmds.getAttr(n + "." + a)
            if isinstance(v, str) and v.startswith("|") and not cmds.objExists(v): bad.append((n, a, v))
        except Exception: pass
R["dangling_path_attrs"] = bad
cands = maya_rigs.candidate_export_groups()
R["candidates"] = [(c.name, c.joint_count) for c in cands[:3]]
eg = next(c for c in cands if c.name == "Seth_Joint_GRP")
markers = maya_rigs.suggested_markers(eg, "")
R["suggested_markers"] = list(markers)
gh = rigs.from_json_dict(json.load(open(REPO + r"\scripts\outfitter\data\rigs\genhuman.json")))
R["markers_shared_with_genhuman"] = sorted(set(markers) & set(gh.markers))
prof = maya_rigs.capture_profile(rig_id="seth", display_name="Seth", version="v00.5", export_group="Seth_Joint_GRP",
                                 markers=markers, rig_file=rigs.rig_file_rel("seth", Path(v005).name))
R["validate"] = rigs.validate_profile(prof)
R["joints"] = len(prof.skeleton.joints)
R["names_match_genhuman"] = set(prof.skeleton.names) == set(gh.skeleton.names)
R["skin_sets_match_genhuman"] = all(set(v) == set(gh.skin_sets.get(k, ())) for k, v in prof.skin_sets.items())
R["root_group_rotate"] = list(prof.skeleton.root_group_rotate)
# test body cycle
cmds.file(new=True, force=True)
maya_skeleton.build_cloth_skeleton(prof.skeleton)
before = set(cmds.ls())
try: cmds.file(v005, reference=True, namespace=sanitize_namespace(Path(v005).stem))
except RuntimeError: pass
c = maya_testfit.connect_test_body("Mesh_GRP", prof)
R["connect"] = [c.matched, c.connected, c.unmatched]
egp = cmds.ls("*:Seth_Joint_GRP", long=True)[0]
def drift():
    return max(math.dist(cmds.xform(j, q=True, ws=True, t=True),
                         cmds.xform("cloth_" + j.rsplit(":", 1)[-1], q=True, ws=True, t=True))
               for j in cmds.listRelatives(egp, ad=True, type="joint", fullPath=True))
R["rest_drift"] = drift()
for cc, a, v in POSE:
    for ax, x in zip("xyz", v): cmds.setAttr("%s:%s.%s%s" % (sanitize_namespace(Path(v005).stem), cc, a, ax), x)
R["posed_drift"] = drift()
R["has_rig_loaded"] = maya_publish.scene_has_rig(tuple(prof.markers))
maya_testfit.remove_test_body(prof)
R["after_remove_new_nodes"] = sorted(set(cmds.ls()) - before)
R["after_remove_has_rig"] = maya_publish.scene_has_rig(tuple(prof.markers))
R["after_remove_refs"] = cmds.file(q=True, reference=True) or []
# v00.4 markers matched this empty garment-like scene; v00.5 markers must not
cmds.file(new=True, force=True)
cmds.createNode("transform", n="cloth_Skeleton_vis_grp")
R["false_positive_scene_has_rig"] = maya_publish.scene_has_rig(tuple(prof.markers))
json.dump(R, open(out, "w"), indent=1, default=str)
print("WROTE")
