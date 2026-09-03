import struct
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
from maya.api import OpenMaya as om, OpenMayaAnim as oma

REPO = r"\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\Outfitter_maya_clothing"
RIG = REPO + r"\MichaelC_rig_01.7.ma"
try: cmds.loadPlugin("mayaUsdPlugin", quiet=True)
except Exception: pass
cmds.file(RIG, o=True, f=True)
print("### NODES", len(cmds.ls()))
print("### UNKNOWN", cmds.ls(type="unknown") + cmds.ls(type="unknownDag"))
for n in ("UsdDefaultRenderSettings","hyperShadePrimaryNodeEditorSavedTabsInfo"):
    print("###   %s exists=%s" % (n, cmds.objExists(n)))
print("### ATTRS skm=%s mi=%s mmi=%s nw=%s" % (
    cmds.getAttr("skinCluster2.skinningMethod"), cmds.getAttr("skinCluster2.maxInfluences"),
    cmds.getAttr("skinCluster2.maintainMaxInfluences"), cmds.getAttr("skinCluster2.normalizeWeights")))

sl = om.MSelectionList(); sl.add("skinCluster2"); SC = oma.MFnSkinCluster(sl.getDependNode(0))
sl2 = om.MSelectionList(); sl2.add("MichaelC_body_meshShape"); DP = sl2.getDagPath(0)
NV = cmds.polyEvaluate("MichaelC_body_mesh", v=True)
COMP = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
om.MFnSingleIndexedComponent(COMP).setCompleteData(NV)
paths = SC.influenceObjects(); NI = len(paths)
COL = {p.partialPathName().split("|")[-1]: i for i, p in enumerate(paths)}
W = list(SC.getWeights(DP, COMP)[0])
print("### SHAPE verts=%d infl=%d" % (NV, NI))

ref = list(struct.unpack("<%dd" % (NV*NI), open(r"C:\Windows\Temp\mc\weights.bin","rb").read()))
print("### WEIGHTS_MATCH max_abs_diff=%.3e" % max(abs(a-b) for a, b in zip(W, ref)))

h = {}
bad = 0
for v in range(NV):
    row = W[v*NI:(v+1)*NI]
    c = sum(1 for x in row if x > 0); h[c] = h.get(c,0)+1
    if abs(sum(row) - 1.0) > 1e-6: bad += 1
print("### HIST", sorted(h.items()), "unnormalized=%d" % bad)

for n in ("ball_l","ball_r","calf_twist_01_l","calf_twist_02_l","calf_twist_01_r",
          "calf_twist_02_r","thigh_twist_01_l","thigh_twist_02_l","thigh_twist_01_r","thigh_twist_02_r"):
    i = COL[n]
    print("###   %-18s %9.3f over %4d verts" % (n, sum(W[v*NI+i] for v in range(NV)),
                                                sum(1 for v in range(NV) if W[v*NI+i] > 0)))

# R4
print("### R4")
for k in range(1, 6):
    b = "spine_m_%02d_anim_spaceorientSpace" % k
    print("###   %-36s x%d   %s_in x%d" % (b, len(cmds.ls(b) or []), b, len(cmds.ls(b+"_in") or [])))
oc = cmds.ls("spine_m_01_anim_space_orientConstraint1")
if oc:
    print("### R4 constraint targets:", cmds.orientConstraint(oc[0], q=True, tl=True))

# landmarks + bind pose
for n in ("MichaelC_Joint_GRP","MichaelC_Mesh_GRP","MichaelC_body_mesh"):
    print("### LANDMARK %-22s x%d" % (n, len(cmds.ls(n) or [])))
print("### EXPORT_JOINTS", len(cmds.ls(cmds.listRelatives("MichaelC_Joint_GRP", ad=True, f=True) or [], type="joint")))
orig = [s for s in (cmds.listRelatives("MichaelC_body_mesh", s=True, f=True) or [])
        if cmds.getAttr(s+".intermediateObject")]
if orig:
    sl3 = om.MSelectionList(); sl3.add(orig[0])
    a = om.MFnMesh(sl3.getDagPath(0)).getPoints(om.MSpace.kWorld)
    b = om.MFnMesh(DP).getPoints(om.MSpace.kWorld)
    print("### BIND_POSE worst deviation %.3e cm" % max((a[i]-b[i]).length() for i in range(NV)))
