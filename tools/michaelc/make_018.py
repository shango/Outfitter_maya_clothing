"""Write MichaelC_rig_01.8.ma from 01.7.

Text surgery, same reason as make_016/make_017: batch Maya cannot register
UsdDefaultSettings or nodeGraphEditorInfo, so saving from mayapy duplicates them.

One change. MichaelC_BODY_GUIDE_LYR ships visible and selectable, and all 31 of its
JOINT_MARKER curves sit at distance 0.000 from an animation control - clicking a
control in the viewport is as likely to grab the marker. Hide the layer, the way
MichaelC_JNT_LAYER is already hidden. Nothing is deleted: the guide comes back by
turning the layer on.

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

stamp = only(out, 'createNode transform -n "MichaelC_rig_v01_7" -p "MichaelC_info_GRP";\n')
out[stamp] = 'createNode transform -n "MichaelC_rig_v01_8" -p "MichaelC_info_GRP";\n'
print("version stamp v01_7 -> v01_8 at line %d" % (stamp + 1))

open(DST, "w").writelines(out)
print("wrote %s (%d lines)" % (DST, len(out)))
