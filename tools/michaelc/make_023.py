"""Write MichaelC_rig_v2.3.ma from v2.2.

Text surgery, same reason as make_016/017/018: batch Maya cannot register
UsdDefaultSettings or nodeGraphEditorInfo, so saving from mayapy duplicates them.
Every byte outside the edited regions is carried over untouched.

v2.2 is the user's Maya-side result of deleting the old MichaelC_Joint_GRP, renaming
foot_l/foot_r back to GM_foot_L/GM_foot_R, and renaming MichaelC_GH_Skin_Joint_GRP to
MichaelC_Joint_GRP. This script finishes the job:

  W   replace the .wl block with the one weights_023.py computed - ik_foot_r's weight
      moved onto GM_foot_R (the two joints are coincident and co-moving to 1e-14, so
      the transfer costs 0.0000 cm at bind and posed), then pruned to 4 influences
  R3  maxInfluences 8 -> 4 (maintainMaxInfluences is already on)
  V   re-apply the 01.8 viewport fixes lost in the v2.1 branch: hide
      MichaelC_BODY_GUIDE_LYR and the eight bendy splines
  J   remove the digital_double_michael_axilla_* turntable lights and cameras that
      came in with the comparison render - 16 nodes, 12 connections, world-root, no
      set membership beyond :lightList1 and :defaultLightSet
      (bindPose4 is NOT junk: it is the only dagPose left and it belongs to the
      surviving skeleton. It stays.)
  S   the in-scene version stamp, MichaelC_rig_v01_7 -> _v2_3
"""
SRC = "MichaelC_rig_v2.2.ma"
DST = "MichaelC_rig_v2.3.ma"
NEW = "/mnt/c/Windows/Temp/mc_audit/skin_new_023.ma"

WL_START = '\tsetAttr -s 5280 ".wl";\n'
WL_END = '\tsetAttr -s 89 ".pm";\n'

def only(lines, needle):
    hits = [i for i, l in enumerate(lines) if l == needle]
    assert len(hits) == 1, "%r matched %d lines" % (needle, len(hits))
    return hits[0]

src = open(SRC).readlines()
new = open(NEW).readlines()

# --- W: splice the recomputed weight block ---------------------------------
a, b = only(src, WL_START), only(src, WL_END)
c, d = only(new, WL_START), only(new, WL_END)
assert a < b and c < d
print("wl block: %d lines -> %d lines" % (b - a, d - c))
out = src[:a] + new[c:d] + src[b:]

# --- R3: influence budget --------------------------------------------------
mi = only(out, '\tsetAttr ".mi" 8;\n')
assert '\tsetAttr ".mmi" yes;\n' in out[mi - 3:mi], "mmi not already set"
out[mi] = '\tsetAttr ".mi" 4;\n'
print("R3: .mi 8 -> 4 at line %d" % (mi + 1))

# --- V: the two 01.8 viewport fixes ----------------------------------------
lyr = only(out, 'createNode displayLayer -n "MichaelC_BODY_GUIDE_LYR";\n')
assert out[lyr + 1].startswith("\trename -uid"), out[lyr + 1]
assert '\tsetAttr ".v" no;\n' not in out[lyr:lyr + 6], "guide layer already hidden"
out.insert(lyr + 2, '\tsetAttr ".v" no;\n')
print("guide layer hidden at line %d" % (lyr + 3))

BENDY = ["%s_%s_bendy%02d_crv" % (limb, side, i)
         for limb in ("arm", "leg") for side in ("l", "r") for i in (0, 1)]
for name in sorted(BENDY):
    i = only(out, 'createNode transform -n "%s" -p "%s_bendy_hrc";\n'
                  % (name, name.rsplit("_bendy", 1)[0]))
    assert out[i + 1].startswith("\trename -uid"), out[i + 1]
    assert '\tsetAttr ".v" no;\n' not in out[i:i + 12], "%s already hidden" % name
    out.insert(i + 2, '\tsetAttr ".v" no;\n')
print("bendy splines hidden: %d" % len(BENDY))

# --- J: drop the turntable lights and cameras ------------------------------
# .ma statements wrap: a connectAttr can continue onto a "\t\t -na;" line, and a
# createNode block owns every indented statement that follows it. Work on whole
# statements, never on single lines, or the tails are left behind as syntax errors.
JUNK = "digital_double_michael_axilla_"

def statements(lines):
    """(start, end) index pairs, one per .ma statement; a statement ends on ';'."""
    spans, i = [], 0
    while i < len(lines):
        j = i
        while j < len(lines) and not lines[j].rstrip().endswith(";"):
            j += 1
        spans.append((i, min(j + 1, len(lines))))
        i = j + 1
    return spans

kept, drop_nodes, drop_conns, in_junk_block = [], 0, 0, False
for a, b in statements(out):
    text = "".join(out[a:b])
    head = out[a]
    if head[:1].isspace():                      # belongs to the node block above
        if in_junk_block:
            continue
    elif head.startswith("createNode "):
        in_junk_block = JUNK in text
        if in_junk_block:
            drop_nodes += 1
            continue
    else:
        in_junk_block = False
        if head.startswith("connectAttr") and JUNK in text:
            drop_conns += 1
            continue
    kept.extend(out[a:b])

assert drop_nodes == 16, drop_nodes
assert drop_conns == 12, drop_conns
print("turntable junk: %d node blocks + %d connections, %d lines removed"
      % (drop_nodes, drop_conns, len(out) - len(kept)))
out = kept
assert not [l for l in out if JUNK in l], "turntable reference survived"
# no statement may BEGIN with a wrapped-flag fragment - that is what an orphaned
# tail looks like. Wrapped "-na;" lines are normal *inside* a statement.
orphans = [a for a, _ in statements(out) if out[a].strip().startswith("-na")]
assert not orphans, "orphaned continuation at lines %s" % [a + 1 for a in orphans[:5]]

# --- S: version stamp ------------------------------------------------------
stamp = only(out, 'createNode transform -n "MichaelC_rig_v01_7" -p "MichaelC_info_GRP";\n')
out[stamp] = 'createNode transform -n "MichaelC_rig_v2_3" -p "MichaelC_info_GRP";\n'
print("version stamp v01_7 -> v2_3 at line %d" % (stamp + 1))

open(DST, "w").writelines(out)
print("wrote %s (%d lines)" % (DST, len(out)))
