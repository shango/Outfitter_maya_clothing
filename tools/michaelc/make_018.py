"""Write MichaelC_rig_01.8.ma from 01.7.

Text surgery, same reason as make_016/make_017: batch Maya cannot register
UsdDefaultSettings or nodeGraphEditorInfo, so saving from mayapy duplicates them.

Two kinds of viewport clutter, both hidden rather than deleted.

  MichaelC_BODY_GUIDE_LYR ships visible and selectable, and all 31 of its
  JOINT_MARKER curves sit at distance 0.000 from an animation control - clicking a
  control is as likely to grab the marker. Hide the layer, the way MichaelC_JNT_LAYER
  is already hidden. The guide comes back by turning the layer on.

  The eight Hive bendy splines run down the limbs, visible and on no display layer,
  so they take clicks too. They are functional - each is read by a curveInfo for arc
  length and two motionPath nodes that ride the bendy joints - so they are hidden,
  not removed. Visibility affects drawing only; worldSpace still evaluates.

  the in-scene version stamp, MichaelC_rig_v01_7 -> _v01_8
"""
SRC = "MichaelC_rig_01.7.ma"
DST = "MichaelC_rig_01.8.ma"

def only(lines, needle):
    hits = [i for i, l in enumerate(lines) if l == needle]
    assert len(hits) == 1, "%r matched %d lines" % (needle, len(hits))
    return hits[0]

out = open(SRC).readlines()

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

stamp = only(out, 'createNode transform -n "MichaelC_rig_v01_7" -p "MichaelC_info_GRP";\n')
out[stamp] = 'createNode transform -n "MichaelC_rig_v01_8" -p "MichaelC_info_GRP";\n'
print("version stamp v01_7 -> v01_8 at line %d" % (stamp + 1))

open(DST, "w").writelines(out)
print("wrote %s (%d lines)" % (DST, len(out)))
