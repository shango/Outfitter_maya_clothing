"""Audit a rig .ma against what Outfitter registration needs. Run under mayapy.

    mayapy.exe rig_audit.py <rig.ma> <out.json>
"""
import json
import sys

import maya.standalone
maya.standalone.initialize()

from maya import cmds
from maya.api import OpenMaya as om, OpenMayaAnim as oma

REPO = r"\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\Outfitter_maya_clothing"
sys.path.insert(0, REPO + r"\scripts")

try:
    cmds.loadPlugin("mayaUsdPlugin", quiet=True)
except Exception:
    pass

rig_ma, out_json = sys.argv[1], sys.argv[2]
cmds.file(rig_ma, open=True, force=True, ignoreVersion=True, prompt=False)

R = {"file": rig_ma}
R["node_count"] = len(cmds.ls())
R["unknown_nodes"] = cmds.ls(type="unknown") or []
R["unknown_plugins"] = cmds.unknownPlugin(query=True, list=True) or []
R["references"] = cmds.file(query=True, reference=True) or []
R["namespaces"] = [n for n in (cmds.namespaceInfo(listOnlyNamespaces=True) or [])
                   if n not in ("UI", "shared")]

# --- what Outfitter would see -------------------------------------------------
from outfitter.core import maya_rigs, rigs, skin_sets

cands = maya_rigs.candidate_export_groups()
R["candidates"] = [{"name": c.name, "path": c.path, "joints": c.joint_count,
                    "root": c.root_joint} for c in cands[:6]]

top = cands[0].name if cands else ""
R["variant_candidates"] = [{"node": v.node, "attr": v.attr}
                           for v in maya_rigs.detect_variant_switches()]

try:
    prof = maya_rigs.capture_profile(
        rig_id="audit", display_name="Audit", version="x", export_group=top)
    R["capture"] = "ok"
    R["validate_errors"] = rigs.validate_profile(prof)
    R["skeleton_joints"] = len(prof.skeleton.joints)
    R["root_group_rotate"] = list(prof.skeleton.root_group_rotate)
    R["markers"] = list(prof.markers)
    R["skin_sets"] = {k: len(v) for k, v in prof.skin_sets.items()}
    R["shoe_set"] = list(prof.skin_sets.get("shoes", ()))
    R["cloth_names"] = list(prof.skeleton.names)
except Exception as exc:
    R["capture"] = "FAILED: %s" % exc
    R["validate_errors"] = ["capture failed"]

# marker uniqueness, the way _find_export_root resolves (short name, whole scene)
R["marker_matches"] = {m: len(cmds.ls(m) or []) for m in R.get("markers", [])}

# --- skinCluster --------------------------------------------------------------
skins = cmds.ls(type="skinCluster") or []
R["skin_clusters"] = skins
sk = []
for sc in skins:
    geo = cmds.skinCluster(sc, query=True, geometry=True) or []
    infl = cmds.skinCluster(sc, query=True, influence=True) or []
    d = {"name": sc, "geometry": geo, "influences": len(infl),
         "skinningMethod": cmds.getAttr(sc + ".skinningMethod"),
         "maxInfluences": cmds.getAttr(sc + ".maxInfluences"),
         "maintainMaxInfluences": cmds.getAttr(sc + ".maintainMaxInfluences"),
         "normalizeWeights": cmds.getAttr(sc + ".normalizeWeights")}
    if geo:
        shape = cmds.listRelatives(geo[0], shapes=True, noIntermediate=True,
                                   fullPath=True) or [geo[0]]
        sel = om.MSelectionList()
        sel.add(sc)
        fn = oma.MFnSkinCluster(sel.getDependNode(0))
        sel2 = om.MSelectionList()
        sel2.add(shape[0])
        dag = sel2.getDagPath(0)
        comp = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
        weights, n_infl = fn.getWeights(dag, comp)
        nv = len(weights) // n_infl
        peak, bad_sum, hist = 0, 0, {}
        for v in range(nv):
            row = weights[v * n_infl:(v + 1) * n_infl]
            k = sum(1 for w in row if w > 1e-6)
            peak = max(peak, k)
            hist[k] = hist.get(k, 0) + 1
            if abs(sum(row) - 1.0) > 1e-4:
                bad_sum += 1
        d.update(vertices=nv, peak_influences=peak,
                 influence_histogram=dict(sorted(hist.items())),
                 vertices_not_summing_to_one=bad_sum)
    sk.append(d)
R["skins"] = sk

# --- controls at default ------------------------------------------------------
off = []
for t in cmds.ls(type="transform", long=True) or []:
    if not (cmds.listRelatives(t, shapes=True, type="nurbsCurve") or []):
        continue
    tr = cmds.getAttr(t + ".t")[0]
    ro = cmds.getAttr(t + ".r")[0]
    sc_ = cmds.getAttr(t + ".s")[0]
    if (max(abs(x) for x in tr + ro) > 1e-6
            or max(abs(x - 1.0) for x in sc_) > 1e-6):
        off.append(t.rsplit("|", 1)[-1])
R["controls_total"] = len(cmds.ls(type="transform", long=True) or [])
R["controls_off_default"] = off

# --- display layers -----------------------------------------------------------
layers = []
for L in cmds.ls(type="displayLayer") or []:
    if L == "defaultLayer":
        continue
    layers.append({"name": L, "visible": cmds.getAttr(L + ".visibility"),
                   "displayType": cmds.getAttr(L + ".displayType"),
                   "members": len(cmds.editDisplayLayerMembers(L, query=True) or [])})
R["display_layers"] = layers

# --- guide markers sitting on controls ---------------------------------------
anims = [t for t in (cmds.ls("*_anim", long=True) or [])
         if cmds.listRelatives(t, shapes=True, type="nurbsCurve")]
on_top = []
for L in [l["name"] for l in layers if "GUIDE" in l["name"].upper()]:
    for m in (cmds.editDisplayLayerMembers(L, query=True, fullNames=True) or []):
        if cmds.nodeType(m) != "transform":
            continue
        p = cmds.xform(m, query=True, worldSpace=True, translation=True)
        best, bd = "", 1e9
        for a in anims:
            q = cmds.xform(a, query=True, worldSpace=True, translation=True)
            dd = sum((p[i] - q[i]) ** 2 for i in range(3)) ** 0.5
            if dd < bd:
                best, bd = a.rsplit("|", 1)[-1], dd
        if bd < 0.001:
            on_top.append([m.rsplit("|", 1)[-1], best, round(bd, 6)])
R["guide_markers_on_controls"] = on_top

# --- joint world positions (proportion comparison) ---------------------------
pos = {}
if cands:
    for j in (cmds.listRelatives(cands[0].path, allDescendents=True,
                                 type="joint", fullPath=True) or []):
        pos[j.rsplit("|", 1)[-1]] = cmds.xform(j, query=True, worldSpace=True,
                                               translation=True)
R["joint_world_pos"] = pos

# --- mesh extent --------------------------------------------------------------
meshes = cmds.ls(type="mesh", noIntermediate=True, long=True) or []
R["meshes"] = [m.rsplit("|", 1)[-1] for m in meshes]
if meshes:
    bb = cmds.exactWorldBoundingBox(cmds.listRelatives(meshes[0], parent=True,
                                                       fullPath=True)[0])
    R["body_height_cm"] = round(bb[4] - bb[1], 3)
    R["body_bbox"] = [round(v, 3) for v in bb]

with open(out_json, "w") as fh:
    json.dump(R, fh, indent=1)
print("WROTE", out_json)
