"""Apply R3/W2/W3/W4/W6 to MichaelC_rig_01.6 and export the resulting skinCluster.

Nothing is saved from this scene: batch Maya cannot register UsdDefaultSettings or
nodeGraphEditorInfo, and a full save duplicates them. Only skinCluster2 is exported,
for its .wl block to be spliced into the .ma by text surgery.
"""
import maya.standalone
maya.standalone.initialize()
import maya.cmds as cmds
from maya.api import OpenMaya as om, OpenMayaAnim as oma

REPO = r"\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\Outfitter_maya_clothing"
RIG = REPO + r"\MichaelC_rig_01.6.ma"
OUT = r"C:\Windows\Temp\mc\skin_new.ma"
BUDGET = 4

try: cmds.loadPlugin("mayaUsdPlugin", quiet=True)
except Exception: pass
cmds.file(RIG, o=True, f=True)

sl = om.MSelectionList(); sl.add("skinCluster2")
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

PTS = om.MFnMesh(DP).getPoints(om.MSpace.kWorld)
def jpos(short):
    h = [p for p in cmds.ls(short, l=True) if "|MichaelC_Joint_GRP|" in p]
    assert len(h) == 1, (short, h)
    return om.MVector(*cmds.xform(h[0], q=True, ws=True, t=True))

def col(v, name): return W[v*NI + COL[name]]
def setcol(v, name, x): W[v*NI + COL[name]] = x

# ---------------------------------------------------------------- W2
# ball_l holds nothing; the left ball's share was absorbed into GM_foot_L.
# For every left vertex carrying foot weight, re-split that vertex's own
# (GM_foot_L + ball_l) total using the ratio its mirror partner uses on the right.
# Only the pair is touched, so every other influence and the vertex sum survive.
def mirror_partner():
    right = [i for i in range(NV) if PTS[i].x < 0]
    out, worst = {}, 0.0
    for i in range(NV):
        if PTS[i].x <= 0: continue
        tx, ty, tz = -PTS[i].x, PTS[i].y, PTS[i].z
        best, bd = None, 1e9
        for j in right:
            p = PTS[j]
            d = (p.x-tx)**2 + (p.y-ty)**2 + (p.z-tz)**2
            if d < bd: bd, best = d, j
        out[i] = best
        worst = max(worst, bd**0.5)
    return out, worst

lf = [v for v in range(NV) if col(v,"GM_foot_L") > 0 or col(v,"ball_l") > 0]
print("### W2 left foot verts=%d" % len(lf))
MIR, worst = mirror_partner()
print("### W2 mirror worst match distance, whole mesh = %.4f cm" % worst)
foot_d = []
w2n = 0
for v in lf:
    m = MIR.get(v)
    if m is None: continue
    foot_d.append((PTS[v] - om.MPoint(-PTS[m].x, PTS[m].y, PTS[m].z)).length())
    a, b = col(m,"GM_foot_R"), col(m,"ball_r")
    if a + b <= 0: continue
    t = col(v,"GM_foot_L") + col(v,"ball_l")
    setcol(v, "GM_foot_L", t * a/(a+b))
    setcol(v, "ball_l",    t * b/(a+b))
    w2n += 1
foot_d.sort()
print("### W2 mirror match on the %d foot verts: max=%.4f cm  median=%.4f"
      % (len(foot_d), foot_d[-1], foot_d[len(foot_d)//2]))
print("### W2 rebalanced %d verts" % w2n)

# ------------------------------------------------------------- W3 / W4
# The rig drives twists linearly, measured: calf twists carry u x ankle twist,
# thigh twists carry (1-u) x hip twist. So a vertex at parameter u along the
# bone belongs on the node whose twist factor equals u; split its parent weight
# between the two nodes that bracket it.
def redistribute(parent, start, end, nodes):
    """nodes: [(param, influence_name)] sorted by param, covering `parent`'s weight."""
    a, b = jpos(start), jpos(end)
    axis = b - a
    L2 = axis * axis
    params = [p for p, _ in nodes]
    names  = [n for _, n in nodes]
    moved = 0
    for v in range(NV):
        w = col(v, parent)
        if w <= 0: continue
        u = ((PTS[v] - om.MPoint(a)) * axis) / L2
        u = max(params[0], min(params[-1], u))
        k = 0
        while k < len(params)-2 and u > params[k+1]: k += 1
        lo, hi = params[k], params[k+1]
        t = 0.0 if hi == lo else (u - lo)/(hi - lo)
        setcol(v, parent, 0.0)
        setcol(v, names[k],   col(v, names[k])   + w*(1.0-t))
        setcol(v, names[k+1], col(v, names[k+1]) + w*t)
        moved += 1
    return moved

for side, up in (("l","L"), ("r","R")):
    n = redistribute("calf_"+side, "calf_"+side, "GM_foot_"+up,
                     [(0.0, "calf_"+side), (0.365, "calf_twist_02_"+side),
                      (0.729, "calf_twist_01_"+side)])
    print("### W3 calf_%s redistributed %d verts" % (side, n))
for side in ("l","r"):
    n = redistribute("thigh_"+side, "thigh_"+side, "calf_"+side,
                     [(0.331, "thigh_twist_01_"+side), (0.662, "thigh_twist_02_"+side),
                      (1.0, "thigh_"+side)])
    print("### W4 thigh_%s redistributed %d verts" % (side, n))

# ---------------------------------------------------------------- W6
W_NOPRUNE = list(W)
pre = {}
for v in range(NV):
    c = sum(1 for i in range(NI) if W[v*NI+i] > 0)
    pre[c] = pre.get(c,0)+1
print("### W6 influence hist before prune", sorted(pre.items()))
trimmed = 0
for v in range(NV):
    row = W[v*NI:(v+1)*NI]
    if sum(1 for x in row if x > 0) <= BUDGET:
        s = sum(row)
        if abs(s-1.0) > 1e-9 and s > 0:
            for i in range(NI): W[v*NI+i] = row[i]/s
        continue
    keep = set(sorted(range(NI), key=lambda i: -row[i])[:BUDGET])
    s = sum(row[i] for i in keep)
    for i in range(NI):
        W[v*NI+i] = row[i]/s if i in keep else 0.0
    trimmed += 1
print("### W6 pruned %d verts to %d influences" % (trimmed, BUDGET))

bad = [v for v in range(NV) if abs(sum(W[v*NI:(v+1)*NI]) - 1.0) > 1e-6]
print("### SUM_CHECK off-by-more-than-1e-6: %d" % len(bad))

# ------------------------------------------------------- report + export
SC.setWeights(DP, COMP, LOGICAL, om.MDoubleArray(W), False)
after = list(SC.getWeights(DP, COMP)[0])
print("### WRITEBACK max delta %.3e" % max(abs(a-b) for a,b in zip(W, after)))

print("### TOTALS_AFTER (joints the work order names)")
for n in ["ball_l","ball_r","GM_foot_L","GM_foot_R","calf_l","calf_r",
          "calf_twist_01_l","calf_twist_02_l","calf_twist_01_r","calf_twist_02_r",
          "thigh_l","thigh_r","thigh_twist_01_l","thigh_twist_02_l",
          "thigh_twist_01_r","thigh_twist_02_r"]:
    i = COL[n]
    s = sum(W[v*NI+i] for v in range(NV))
    c = sum(1 for v in range(NV) if W[v*NI+i] > 0)
    b = sum(W0[v*NI+i] for v in range(NV))
    print("   %-18s %9.3f over %4d verts   (was %9.3f)" % (n, s, c, b))

h = {}
for v in range(NV):
    c = sum(1 for i in range(NI) if W[v*NI+i] > 0)
    h[c] = h.get(c,0)+1
print("### HIST_AFTER", sorted(h.items()))

def pose(on):
    for c in cmds.ls("*leg_*_anim", type="transform"):
        if cmds.objExists(c+".ikfk"):
            try: cmds.setAttr(c+".ikfk", 1 if on else 0)
            except Exception: pass
    for c, vals in [("MichaelC_leg_l_foot_ik_anim",(35,25,20)),
                    ("MichaelC_leg_r_foot_ik_anim",(-30,20,-15)),
                    ("MichaelC_leg_l_thigh_fk_anim",(50,20,15)),
                    ("MichaelC_leg_r_thigh_fk_anim",(-40,-25,10)),
                    ("MichaelC_arm_l_hand_fk_anim",(50,30,25)),
                    ("MichaelC_arm_r_hand_fk_anim",(-45,-30,20))]:
        for a, v in zip(("rotateX","rotateY","rotateZ"), vals):
            pl = c+"."+a
            if cmds.objExists(pl) and cmds.getAttr(pl, se=True): cmds.setAttr(pl, v if on else 0)

def delta(tag, A, B):
    SC.setWeights(DP, COMP, LOGICAL, om.MDoubleArray(A), False)
    a = om.MFnMesh(DP).getPoints(om.MSpace.kWorld)
    SC.setWeights(DP, COMP, LOGICAL, om.MDoubleArray(B), False)
    b = om.MFnMesh(DP).getPoints(om.MSpace.kWorld)
    d = sorted((a[i]-b[i]).length() for i in range(NV))
    print("### %-34s max=%.4f cm  p99=%.4f  mean=%.5f  moved=%d"
          % (tag, d[-1], d[int(NV*0.99)], sum(d)/NV, sum(1 for x in d if x > 1e-6)))
for tag, on in (("bind", False), ("posed", True)):
    pose(on)
    delta("DELTA_TOTAL_%s" % tag, W0, W)
    delta("DELTA_PRUNE_ONLY_%s" % tag, W_NOPRUNE, W)
pose(False)

cmds.setAttr("skinCluster2.maxInfluences", BUDGET)
cmds.setAttr("skinCluster2.maintainMaxInfluences", True)
cmds.select("skinCluster2", r=True)
cmds.file(OUT, force=True, options="v=0;", type="mayaAscii", pr=True, es=True)
print("### EXPORTED", OUT)
import struct
with open(r"C:\Windows\Temp\mc\weights.bin","wb") as fh:
    fh.write(struct.pack("<%dd" % len(W), *W))
print("### DUMPED weights.bin", len(W))
