"""Jenn v1.6 weights: prune to 4 influences and renormalize, measuring what it costs.

Run under mayapy against the structural Jenn_rig_v1.6.ma (the output of
`make_v16.py` with no argument). Nothing is saved from this scene - batch Maya
cannot register every node type in these files and a full save duplicates them.
Only the skinCluster is exported, for its .wl block to be spliced back by
`make_v16.py <export>`. Same method as tools/michaelc/weights_017.py and _023.py.

The rig is delivered at peak 10 influences with maxInfluences 5. The authoring spec
is classic linear at 4 (see HANDOFF_MichaelC.md R2/R3), so garments can match the
body exactly. skinningMethod is already 0, so only the influence count moves.

The cost is measured, not asserted: the mesh is compared before and after at bind
and in an aggressive FK/IK pose.
"""
import struct

import maya.standalone
maya.standalone.initialize()

import maya.cmds as cmds
from maya.api import OpenMaya as om, OpenMayaAnim as oma

REPO = r"\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\Outfitter_maya_clothing"
RIG = REPO + r"\Jenn_rig_v1.6.ma"
OUT = r"C:\Windows\Temp\jenn_audit\skin_new_v16.ma"
DUMP = r"C:\Windows\Temp\jenn_audit\weights_v16.bin"
SKIN = "skinCluster1"
MESH = "Jenn_body_mesh"
SHAPE = "Jenn_body_meshShape"
BUDGET = 4

try:
    cmds.loadPlugin("mayaUsdPlugin", quiet=True)
except Exception:
    pass
cmds.file(RIG, o=True, f=True)

sl = om.MSelectionList()
sl.add(SKIN)
SC = oma.MFnSkinCluster(sl.getDependNode(0))
sl2 = om.MSelectionList()
sl2.add(SHAPE)
DP = sl2.getDagPath(0)
NV = cmds.polyEvaluate(MESH, v=True)
COMP = om.MFnSingleIndexedComponent().create(om.MFn.kMeshVertComponent)
om.MFnSingleIndexedComponent(COMP).setCompleteData(NV)

paths = SC.influenceObjects()
NI = len(paths)
LOGICAL = om.MIntArray([SC.indexForInfluenceObject(p) for p in paths])
COL = {p.partialPathName().split("|")[-1]: i for i, p in enumerate(paths)}
assert len(COL) == NI, "influence short names not unique"
W = list(SC.getWeights(DP, COMP)[0])
W0 = list(W)
print("### VERTS %d INFL %d" % (NV, NI))

# ---------------------------------------------------------------- prune + renormalize
hist_before = {}
for v in range(NV):
    c = sum(1 for i in range(NI) if W[v * NI + i] > 0)
    hist_before[c] = hist_before.get(c, 0) + 1
print("### HIST_BEFORE", sorted(hist_before.items()))

pruned = 0
for v in range(NV):
    row = [(W[v * NI + i], i) for i in range(NI) if W[v * NI + i] > 0]
    if len(row) <= BUDGET:
        continue
    row.sort(reverse=True)
    for _, i in row[BUDGET:]:
        W[v * NI + i] = 0.0
    s = sum(W[v * NI + i] for _, i in row[:BUDGET])
    for _, i in row[:BUDGET]:
        W[v * NI + i] /= s
    pruned += 1
print("### PRUNED %d verts to %d influences" % (pruned, BUDGET))

hist_after, bad = {}, 0
for v in range(NV):
    c = sum(1 for i in range(NI) if W[v * NI + i] > 0)
    hist_after[c] = hist_after.get(c, 0) + 1
    if abs(sum(W[v * NI + i] for i in range(NI)) - 1.0) > 1e-9:
        bad += 1
print("### HIST_AFTER", sorted(hist_after.items()))
print("### SUM_CHECK off-by-more-than-1e-9: %d" % bad)

# ---------------------------------------------------------------- what it cost, measured
def pose(on):
    for c in cmds.ls("*leg_*_anim", type="transform") or []:
        if cmds.objExists(c + ".ikfk"):
            try:
                cmds.setAttr(c + ".ikfk", 1 if on else 0)
            except Exception:
                pass
    for c, vals in [("Jenn_leg_l_foot_ik_anim", (35, 25, 20)),
                    ("Jenn_leg_r_foot_ik_anim", (-30, 20, -15)),
                    ("Jenn_leg_l_thigh_fk_anim", (50, 20, 15)),
                    ("Jenn_leg_r_thigh_fk_anim", (-40, -25, 10)),
                    ("Jenn_arm_l_hand_fk_anim", (50, 30, 25)),
                    ("Jenn_arm_r_hand_fk_anim", (-45, -30, 20)),
                    ("Jenn_spine_m_03_anim", (20, 15, 10))]:
        for a, v in zip(("rotateX", "rotateY", "rotateZ"), vals):
            pl = c + "." + a
            if cmds.objExists(pl) and cmds.getAttr(pl, se=True):
                cmds.setAttr(pl, v if on else 0)


def delta(tag, A, B):
    SC.setWeights(DP, COMP, LOGICAL, om.MDoubleArray(A), False)
    a = om.MFnMesh(DP).getPoints(om.MSpace.kWorld)
    SC.setWeights(DP, COMP, LOGICAL, om.MDoubleArray(B), False)
    b = om.MFnMesh(DP).getPoints(om.MSpace.kWorld)
    d = sorted((a[i] - b[i]).length() for i in range(NV))
    print("### %-24s max=%.4f cm  p99=%.4f  mean=%.5f  moved=%d"
          % (tag, d[-1], d[int(NV * 0.99)], sum(d) / NV, sum(1 for x in d if x > 1e-6)))


for tag, on in (("bind", False), ("posed", True)):
    pose(on)
    delta("DELTA_PRUNE_%s" % tag, W0, W)
pose(False)

# ---------------------------------------------------------------- write back and export
SC.setWeights(DP, COMP, LOGICAL, om.MDoubleArray(W), False)
after = list(SC.getWeights(DP, COMP)[0])
print("### WRITEBACK max delta %.3e" % max(abs(a - b) for a, b in zip(W, after)))

print("### TOTALS (after, was)")
for n in ["GM_foot_L", "GM_foot_R", "ball_l", "ball_r", "calf_l", "calf_r",
          "thigh_twist_01_l", "calf_twist_01_l", "upperarm_twist_01_l",
          "lowerarm_twist_02_l", "spine_05", "head"]:
    if n not in COL:
        continue
    i = COL[n]
    s = sum(W[v * NI + i] for v in range(NV))
    c = sum(1 for v in range(NV) if W[v * NI + i] > 0)
    b = sum(W0[v * NI + i] for v in range(NV))
    print("   %-22s %9.3f over %5d verts   (was %9.3f)" % (n, s, c, b))

cmds.setAttr(SKIN + ".maxInfluences", BUDGET)
cmds.setAttr(SKIN + ".maintainMaxInfluences", True)
cmds.select(SKIN, r=True)
cmds.file(OUT, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
print("### EXPORTED", OUT)
with open(DUMP, "wb") as fh:
    fh.write(struct.pack("<%dd" % len(W), *W))
print("### DUMPED", DUMP, len(W))
