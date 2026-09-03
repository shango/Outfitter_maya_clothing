"""Write MichaelC_rig_01.7.ma from 01.6.

Text surgery, for the same reason make_016.py used it: batch Maya cannot register
UsdDefaultSettings or nodeGraphEditorInfo, so saving the scene from mayapy duplicates
them. Every byte outside the four edited regions is carried over untouched.

  R3  maxInfluences 3 -> 4, maintainMaxInfluences on
  R4  rename the input-layer half of the five duplicated spine space-switch nodes
  W2/W3/W4/W6  replace the .wl weight block with the one Maya computed in mc_apply.py
"""
import sys

SRC = "MichaelC_rig_01.6.ma"
DST = "MichaelC_rig_01.7.ma"
NEW = "/mnt/c/Windows/Temp/mc/skin_new.ma"

WL_START = '\tsetAttr -s 5280 ".wl";\n'
WL_END   = '\tsetAttr -s 89 ".pm";\n'

def only(lines, needle):
    hits = [i for i, l in enumerate(lines) if l == needle]
    assert len(hits) == 1, "%r matched %d lines" % (needle, len(hits))
    return hits[0]

src = open(SRC).readlines()
new = open(NEW).readlines()

a, b = only(src, WL_START), only(src, WL_END)
c, d = only(new, WL_START), only(new, WL_END)
assert a < b and c < d
block = new[c:d]
print("wl block: %d lines -> %d lines" % (b - a, len(block)))
out = src[:a] + block + src[b:]

# R3
mi = only(out, '\tsetAttr ".mi" 3;\n')
assert not [l for l in out if l.strip() == 'setAttr ".mmi" yes;'], "mmi already set"
out[mi:mi+1] = ['\tsetAttr ".mmi" yes;\n', '\tsetAttr ".mi" 4;\n']
print("R3: .mi 3 -> 4, .mmi added at line %d" % (mi + 1))

# R4 - rename only the copy under spine_m_world_in, and only its full-path references
INPUT_PATH = "|MichaelC|Rig|MichaelC_componentLayer_hrc|spine_m_hrc|spine_m_inputLayer_hrc|spine_m_world_in|"
renamed = refs = 0
for i, l in enumerate(out):
    for n in range(1, 6):
        old = "spine_m_%02d_anim_spaceorientSpace" % n
        decl = 'createNode transform -n "%s" -p "spine_m_world_in";\n' % old
        if l == decl:
            out[i] = 'createNode transform -n "%s_in" -p "spine_m_world_in";\n' % old
            renamed += 1
        elif INPUT_PATH + old + "." in l:
            out[i] = l.replace(INPUT_PATH + old + ".", INPUT_PATH + old + "_in.")
            refs += 1
assert renamed == 5, renamed
assert refs == 15, refs
print("R4: renamed %d nodes, rewrote %d path references" % (renamed, refs))

open(DST, "w").writelines(out)
print("wrote %s (%d lines)" % (DST, len(out)))
