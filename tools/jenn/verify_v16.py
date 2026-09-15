"""Reload Jenn v1.6 and check its weights against the weights_v16.bin dump. Read-only."""
import struct, sys
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
from maya.api import OpenMaya as om, OpenMayaAnim as oma
cmds.loadPlugin("mayaUsdPlugin", quiet=True)
REPO = r"\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\Outfitter_maya_clothing"
cmds.file(REPO + r"\Jenn_rig_v1.6.ma", o=True, f=True)
SKIN = "skinCluster1"

sl = om.MSelectionList(); sl.add(SKIN)
SC = oma.MFnSkinCluster(sl.getDependNode(0))
sl2 = om.MSelectionList(); sl2.add("Jenn_body_meshShape")
DP = sl2.getDagPath(0)
NV = cmds.polyEvaluate("Jenn_body_mesh", v=True)
COMP = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
om.MFnSingleIndexedComponent(COMP).setCompleteData(NV)
W = list(SC.getWeights(DP, COMP)[0])

with open(r"C:\Windows\Temp\jenn_audit\weights_v16.bin", "rb") as fh:
    raw = fh.read()
REF = list(struct.unpack("<%dd" % (len(raw) // 8), raw))
print("### LEN file=%d dump=%d  %s" % (len(W), len(REF), "match" if len(W) == len(REF) else "MISMATCH"))
print("### WEIGHTS worst |file - dump| = %.3e" % max(abs(a - b) for a, b in zip(W, REF)))

paths = SC.influenceObjects()
NI = len(paths)
COL = {p.partialPathName().split("|")[-1]: i for i, p in enumerate(paths)}
peak = max(sum(1 for i in range(NI) if W[v * NI + i] > 0) for v in range(NV))
bad = sum(1 for v in range(NV) if abs(sum(W[v * NI + i] for i in range(NI)) - 1.0) > 1e-6)
print("### PEAK_INFLUENCES %d   VERTS_NOT_SUMMING_TO_1 %d" % (peak, bad))
print("### maxInfluences=%s maintainMax=%s skinningMethod=%s" % (
    cmds.getAttr(SKIN + ".maxInfluences"), cmds.getAttr(SKIN + ".maintainMaxInfluences"),
    cmds.getAttr(SKIN + ".skinningMethod")))
print("### TOTALS")
for n in ("GM_foot_L", "GM_foot_R", "ball_l", "ball_r", "calf_twist_01_l",
          "thigh_twist_01_l", "upperarm_twist_01_l", "spine_05"):
    i = COL[n]
    print("###   %-12s %9.3f over %4d verts" % (
        n, sum(W[v * NI + i] for v in range(NV)),
        sum(1 for v in range(NV) if W[v * NI + i] > 0)))
print("### NODES %d" % len(cmds.ls()))
print("### guide_layer_vis %s" % cmds.getAttr("Jenn_BODY_GUIDE_LYR.visibility"))
print("### bendy_visible %s" % [t for t in cmds.ls(type="transform")
                                if t.endswith(("bendy00_crv", "bendy01_crv"))
                                and cmds.getAttr(t + ".visibility")])
print("### stamp %s" % cmds.ls("Jenn_rig_v*"))
print("### dagPose %s" % cmds.ls(type="dagPose"))
print("### arnold_leftovers %s" % (cmds.ls("defaultArnold*") + (cmds.unknownPlugin(q=True, list=True) or [])))
# god-node scale still intact?
pts = lambda: cmds.xform("Jenn_body_mesh.vtx[0:%d]" % (NV - 1), q=True, ws=True, t=True)
before = pts()
for ax in "XYZ": cmds.setAttr("Jenn_god_m_godnode_anim.scale" + ax, 2.0)
after = pts()
print("### GOD_SCALE_2x max vertex travel %.3f cm" % max(
    ((after[i*3]-before[i*3])**2 + (after[i*3+1]-before[i*3+1])**2
     + (after[i*3+2]-before[i*3+2])**2) ** 0.5 for i in range(NV)))
