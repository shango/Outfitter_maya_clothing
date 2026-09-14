"""v2.2 -> v2.3 weights: move ik_foot_r onto GM_foot_R, then prune to 4 influences.

Nothing is saved from this scene - batch Maya cannot register UsdDefaultSettings or
nodeGraphEditorInfo and a full save duplicates them. Only the skinCluster is exported,
for its .wl block to be spliced into the .ma by text surgery. Same method as
tools/michaelc/weights_017.py.
"""
import struct
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
from maya.api import OpenMaya as om, OpenMayaAnim as oma

REPO = r"\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\Outfitter_maya_clothing"
RIG = REPO + r"\MichaelC_rig_v2.2.ma"
OUT = r"C:\Windows\Temp\mc_audit\skin_new_023.ma"
SKIN = "MichaelC_GH_FullSkin_SKC"
BUDGET = 4

try: cmds.loadPlugin("mayaUsdPlugin", quiet=True)
except Exception: pass
cmds.file(RIG, o=True, f=True)

sl = om.MSelectionList(); sl.add(SKIN)
SC = oma.MFnSkinCluster(sl.getDependNode(0))
sl2 = om.MSelectionList(); sl2.add("MichaelC_body_meshShape")
DP = sl2.getDagPath(0)
NV = cmds.polyEvaluate("MichaelC_body_mesh", v=True)
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

# ---------------------------------------------------------------- prove the transfer is free
# ik_foot_r may only absorb GM_foot_R's weight if the two are coincident AND co-moving.
def wm(short):
    h = [p for p in cmds.ls(short, l=True) if "|MichaelC_Joint_GRP|" in p]
    assert len(h) == 1, (short, h)
    return cmds.xform(h[0], q=True, ws=True, m=True)

def worst_matrix_delta():
    return max(abs(a - b) for a, b in zip(wm("ik_foot_r"), wm("GM_foot_R")))

print("### COINCIDENT bind          worst |matrix delta| = %.3e" % worst_matrix_delta())
POSES = [("MichaelC_leg_r_foot_ik_anim", "translateY", 25.0),
         ("MichaelC_leg_r_foot_ik_anim", "rotateX", 35.0),
         ("MichaelC_leg_r_foot_ik_anim", "translateZ", -18.0),
         ("MichaelC_god_m_godnode_anim", "rotateY", 40.0)]
for node, attr, val in POSES:
    if not cmds.objExists(node + "." + attr): continue
    cmds.setAttr(node + "." + attr, val)
    print("### COINCIDENT %-12s %-10s worst |matrix delta| = %.3e"
          % (node.split("_")[-3], attr, worst_matrix_delta()))
    cmds.setAttr(node + "." + attr, 0.0)

# ---------------------------------------------------------------- 4. the transfer
def col(v, n): return W[v * NI + COL[n]]
def setcol(v, n, x): W[v * NI + COL[n]] = x

moved = 0
for v in range(NV):
    w = col(v, "ik_foot_r")
    if w > 0.0:
        setcol(v, "GM_foot_R", col(v, "GM_foot_R") + w)
        setcol(v, "ik_foot_r", 0.0)
        moved += 1
print("### TRANSFER ik_foot_r -> GM_foot_R on %d verts" % moved)
W_XFER = list(W)

# ---------------------------------------------------------------- how symmetric is the foot now?
PTS = om.MFnMesh(DP).getPoints(om.MSpace.kWorld)
foot = [i for i in range(NV) if PTS[i].y < 12.0]
right = [i for i in foot if PTS[i].x < 0]
partner, worst_d = {}, 0.0
for i in foot:
    if PTS[i].x <= 0: continue
    best, bd = None, 1e9
    for j in right:
        d = (PTS[j].x + PTS[i].x) ** 2 + (PTS[j].y - PTS[i].y) ** 2 + (PTS[j].z - PTS[i].z) ** 2
        if d < bd: bd, best = d, j
    partner[i], worst_d = best, max(worst_d, bd ** 0.5)
print("### MIRROR %d foot pairs, worst partner distance %.4f cm" % (len(partner), worst_d))
for L, R in (("GM_foot_L", "GM_foot_R"), ("ball_l", "ball_r"),
             ("calf_twist_01_l", "calf_twist_01_r")):
    d = [abs(col(i, L) - col(partner[i], R)) for i in partner]
    print("###   %-16s vs %-16s max per-vertex |dL-dR| = %.4f  mean %.5f"
          % (L, R, max(d), sum(d) / len(d)))

# ---------------------------------------------------------------- 5. prune to 4 + renormalize
hist_before = {}
for v in range(NV):
    c = sum(1 for i in range(NI) if W[v * NI + i] > 0)
    hist_before[c] = hist_before.get(c, 0) + 1
print("### HIST_BEFORE", sorted(hist_before.items()))

pruned = 0
for v in range(NV):
    row = [(W[v * NI + i], i) for i in range(NI) if W[v * NI + i] > 0]
    if len(row) <= BUDGET: continue
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
    if abs(sum(W[v * NI + i] for i in range(NI)) - 1.0) > 1e-9: bad += 1
print("### HIST_AFTER", sorted(hist_after.items()))
print("### SUM_CHECK off-by-more-than-1e-9: %d" % bad)

# ---------------------------------------------------------------- what it cost, measured
def pose(on):
    for c in cmds.ls("*leg_*_anim", type="transform"):
        if cmds.objExists(c + ".ikfk"):
            try: cmds.setAttr(c + ".ikfk", 1 if on else 0)
            except Exception: pass
    for c, vals in [("MichaelC_leg_l_foot_ik_anim", (35, 25, 20)),
                    ("MichaelC_leg_r_foot_ik_anim", (-30, 20, -15)),
                    ("MichaelC_leg_l_thigh_fk_anim", (50, 20, 15)),
                    ("MichaelC_leg_r_thigh_fk_anim", (-40, -25, 10)),
                    ("MichaelC_arm_l_hand_fk_anim", (50, 30, 25)),
                    ("MichaelC_arm_r_hand_fk_anim", (-45, -30, 20))]:
        for a, v in zip(("rotateX", "rotateY", "rotateZ"), vals):
            pl = c + "." + a
            if cmds.objExists(pl) and cmds.getAttr(pl, se=True): cmds.setAttr(pl, v if on else 0)

def delta(tag, A, B):
    SC.setWeights(DP, COMP, LOGICAL, om.MDoubleArray(A), False)
    a = om.MFnMesh(DP).getPoints(om.MSpace.kWorld)
    SC.setWeights(DP, COMP, LOGICAL, om.MDoubleArray(B), False)
    b = om.MFnMesh(DP).getPoints(om.MSpace.kWorld)
    d = sorted((a[i] - b[i]).length() for i in range(NV))
    print("### %-30s max=%.4f cm  p99=%.4f  mean=%.5f  moved=%d"
          % (tag, d[-1], d[int(NV * 0.99)], sum(d) / NV, sum(1 for x in d if x > 1e-6)))

for tag, on in (("bind", False), ("posed", True)):
    pose(on)
    delta("DELTA_TRANSFER_%s" % tag, W0, W_XFER)
    delta("DELTA_PRUNE_%s" % tag, W_XFER, W)
    delta("DELTA_TOTAL_%s" % tag, W0, W)
pose(False)

# ---------------------------------------------------------------- write back and export
SC.setWeights(DP, COMP, LOGICAL, om.MDoubleArray(W), False)
after = list(SC.getWeights(DP, COMP)[0])
print("### WRITEBACK max delta %.3e" % max(abs(a - b) for a, b in zip(W, after)))

print("### TOTALS_AFTER")
for n in ["GM_foot_L", "GM_foot_R", "ik_foot_l", "ik_foot_r", "ball_l", "ball_r",
          "calf_l", "calf_r", "upperarm_twist_01_l", "lowerarm_twist_02_l", "spine_05"]:
    i = COL[n]
    s = sum(W[v * NI + i] for v in range(NV))
    c = sum(1 for v in range(NV) if W[v * NI + i] > 0)
    b = sum(W0[v * NI + i] for v in range(NV))
    print("   %-22s %9.3f over %4d verts   (was %9.3f)" % (n, s, c, b))

cmds.setAttr(SKIN + ".maxInfluences", BUDGET)
cmds.setAttr(SKIN + ".maintainMaxInfluences", True)
cmds.select(SKIN, r=True)
cmds.file(OUT, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
print("### EXPORTED", OUT)
with open(r"C:\Windows\Temp\mc_audit\weights_023.bin", "wb") as fh:
    fh.write(struct.pack("<%dd" % len(W), *W))
print("### DUMPED weights_023.bin", len(W))
