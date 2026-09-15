"""Produce Jenn_rig_v1.6.ma from v1.5: Outfitter-readiness + MichaelC v3 parity.

Text surgery on the .ma, same reason as tools/michaelc/make_016.py and make_023.py:
batch Maya cannot register every node type in these files, so a full save from mayapy
duplicates nodes. Every byte outside the edited regions is carried over untouched.

What it does, in the order it does it:

  A   remove the 5 Arnold render-settings nodes, the 4 connectAttr statements that wire
      them, the 18 `.ai_*` attribute lines mtoa adds to the two shading groups, and the
      `requires ... "mtoa"` declaration. Without mtoa loaded these arrive as unknown
      nodes, and the standing rule is never to save from a session where anything is
      unknown. They carry no rig data. (The rig's own notes attribute claims GenRig 1.2
      already "removed unused Arnold render settings" - it did not.)

      The `.ai_*` lines are not optional extras: dropping the `requires` without them
      makes Maya reject the file at load with "The shadingEngine 'initialShadingGroup'
      has no '.ai_override' attribute". mtoa registers those as dynamic attributes on
      stock node types, so the plugin declaration and the attributes go together.
  R   rename the generic landmarks. `maya_skeleton._find_export_root` resolves the export
      group by SHORT NAME across the whole scene and takes the first match, and the same
      names become the profile's markers, so `Skeleton` and `Geo` would collide with a
      garment scene. Same rename MichaelC 01.6 applied. Nobody should rename these back.
  V   the viewport pass MichaelC got in 01.8, never applied on this branch: hide the body
      guide layer (28 of its JOINT_MARKER curves sit at distance 0.000 from an animation
      control and take its clicks), hide the 8 bendy splines (kept, not deleted - each is
      read by a curveInfo and two motionPath nodes), and set the joint and geo layers to
      reference so neither takes clicks.
  S   add Jenn_info_GRP with the version stamp, matching MichaelC's convention.
  W   maxInfluences 5 -> 4, and splice in the pruned weight block if one is given.

Run it twice: once with no argument to produce a file Maya can load, then
`weights_v16.py` under mayapy to compute the pruned weights, then again passing that
export to splice them in. The second run regenerates from v1.5, so it is deterministic.

    python3 tools/jenn/make_v16.py [path/to/skin_new_v16.ma]
"""
from __future__ import annotations

import re
import sys

SRC = "Jenn_rig_v1.5.ma"
DST = "Jenn_rig_v1.6.ma"

# --- A: Arnold ---------------------------------------------------------------
ARNOLD_NODES = {
    "defaultArnoldRenderOptions", "defaultArnoldFilter", "defaultArnoldDriver",
    "defaultArnoldDisplayDriver", "defaultArnoldDenoiser",
}
ARNOLD_REQUIRES = 'requires -nodeType "aiOptions"'
# mtoa registers these as dynamic attributes on stock node types (the shading groups).
AI_ATTR = re.compile(r'^\s*setAttr\b.*"\.ai_')

# --- R: renames, longest first so Jennifer_Geo1Shape is not eaten by Jennifer_Geo1 ---
RENAME = [
    ("Jennifer_Geo1ShapeOrig", "Jenn_body_meshShapeOrig"),
    ("Jennifer_Geo1Shape", "Jenn_body_meshShape"),
    ("Jennifer_Geo1", "Jenn_body_mesh"),
    ("Skeleton", "Jenn_Joint_GRP"),
    ("Geo", "Jenn_Mesh_GRP"),
]

# --- V: viewport -------------------------------------------------------------
BENDY = ["%s_%s_bendy%02d_crv" % (limb, side, i)
         for limb in ("arm", "leg") for side in ("l", "r") for i in (0, 1)]

# --- S: version stamp --------------------------------------------------------
INFO_GROUP = [
    'createNode transform -n "Jenn_info_GRP" -p "JENN";',
    'createNode transform -n "Jenn_rig_v1_6" -p "Jenn_info_GRP";',
    'createNode transform -n "Jenn_rig_Maya2026" -p "Jenn_info_GRP";',
]

# --- W: skin -----------------------------------------------------------------
WL_START = '\tsetAttr -s 25266 ".wl";'
WL_END = '\tsetAttr -s 79 ".pm";'
MI_FROM, MI_TO = '\tsetAttr ".mi" 5;', '\tsetAttr ".mi" 4;'

VERBS = ("createNode", "connectAttr", "lockNode", "select", "requires",
         "relationship", "fileInfo", "currentUnit")


def statements(lines: list[str]) -> list[tuple[int, int]]:
    """(start, end) index pairs, one per .ma statement; a statement ends on ';'.

    .ma statements wrap: a connectAttr can continue onto a "\t\t -na;" line. Work on
    whole statements, never single lines, or removal leaves orphaned tails that Maya
    rejects at load (the mistake make_023.py records).
    """
    spans, i = [], 0
    while i < len(lines):
        j = i
        while j < len(lines) and not lines[j].rstrip().endswith(";"):
            j += 1
        spans.append((i, min(j + 1, len(lines))))
        i = j + 1
    return spans


def only(lines: list[str], needle: str) -> int:
    hits = [i for i, l in enumerate(lines) if l == needle]
    assert len(hits) == 1, "%r matched %d lines" % (needle, len(hits))
    return hits[0]


def ref_re(name: str) -> re.Pattern:
    """``name`` used as a whole node token inside a quoted string."""
    return re.compile(r'(?<=[|"])' + re.escape(name) + r'(?=[."|\[])')


def main() -> int:
    skin_export = sys.argv[1] if len(sys.argv) > 1 else ""
    lines = open(SRC, encoding="utf-8", errors="surrogateescape").read().split("\n")

    for i, line in enumerate(lines, 1):
        if not line or line[:1] in (" ", "\t") or line.startswith("//"):
            continue
        if not line.startswith(VERBS):
            print("UNEXPECTED column-0 statement at line %d: %r" % (i, line[:80]))
            return 1

    # --- A: drop the Arnold nodes, their connections, attrs and the mtoa requires ---
    kept, drop_nodes, drop_conns, drop_req, drop_attrs, in_arnold = [], 0, 0, 0, 0, False
    for a, b in statements(lines):
        text = "\n".join(lines[a:b])
        head = lines[a]
        hit = any(n in text for n in ARNOLD_NODES)
        if head[:1].isspace():                    # belongs to the block above
            if in_arnold:
                continue
            if AI_ATTR.search(head):              # mtoa's dynamic attrs on stock nodes
                drop_attrs += 1
                continue
        elif head.startswith("createNode "):
            in_arnold = hit
            if in_arnold:
                drop_nodes += 1
                continue
        else:
            in_arnold = False
            if head.startswith("connectAttr") and hit:
                drop_conns += 1
                continue
            if head.startswith(ARNOLD_REQUIRES):
                drop_req += 1
                continue
        kept.extend(lines[a:b])
    assert (drop_nodes, drop_conns, drop_req, drop_attrs) == (5, 4, 1, 18), \
        (drop_nodes, drop_conns, drop_req, drop_attrs)
    print("A: removed %d Arnold nodes, %d connections, %d ai_ attrs, %d requires "
          "(%d lines)" % (drop_nodes, drop_conns, drop_attrs, drop_req,
                          len(lines) - len(kept)))
    lines = kept
    assert not [l for l in lines if "defaultArnold" in l or '"mtoa"' in l
                or AI_ATTR.search(l)], "Arnold reference survived"
    orphans = [a for a, _ in statements(lines) if lines[a].strip().startswith("-")]
    assert not orphans, "orphaned continuation at lines %s" % [a + 1 for a in orphans[:5]]

    # --- R: renames -----------------------------------------------------------
    for old, new in RENAME:
        rx = ref_re(old)
        hits = sum(len(rx.findall(l)) for l in lines)
        assert hits, "rename %r matched nothing" % old
        lines = [rx.sub(new, l) for l in lines]
        print("R: %-24s -> %-24s (%d references)" % (old, new, hits))

    # --- V: viewport ----------------------------------------------------------
    lyr = only(lines, 'createNode displayLayer -n "Jenn_BODY_GUIDE_LYR";')
    assert lines[lyr + 1].startswith("\trename -uid"), lines[lyr + 1]
    assert '\tsetAttr ".v" no;' not in lines[lyr:lyr + 8], "guide layer already hidden"
    lines.insert(lyr + 2, '\tsetAttr ".v" no;')
    print("V: Jenn_BODY_GUIDE_LYR hidden")

    for name in sorted(BENDY):
        i = only(lines, 'createNode transform -n "%s" -p "%s_bendy_hrc";'
                        % (name, name.rsplit("_bendy", 1)[0]))
        assert lines[i + 1].startswith("\trename -uid"), lines[i + 1]
        assert '\tsetAttr ".v" no;' not in lines[i:i + 12], "%s already hidden" % name
        lines.insert(i + 2, '\tsetAttr ".v" no;')
    print("V: %d bendy splines hidden" % len(BENDY))

    # joint layer: template + visible -> reference + hidden, as MichaelC has it
    jl = only(lines, 'createNode displayLayer -n "Jenn_GH_JNT_LAYER";')
    dt = only(lines[jl:jl + 8], '\tsetAttr ".dt" 1;') + jl
    lines[dt] = '\tsetAttr ".dt" 2;'
    lines.insert(dt + 1, '\tsetAttr ".v" no;')
    print("V: Jenn_GH_JNT_LAYER displayType 1 -> 2, hidden")

    # geo layer: make the body mesh unselectable, as MichaelC 01.8 had it
    gl = only(lines, 'createNode displayLayer -n "Jenn_GH_GEO_LAYER";')
    assert lines[gl + 1].startswith("\trename -uid"), lines[gl + 1]
    assert '\tsetAttr ".dt" 2;' not in lines[gl:gl + 8], "geo layer already reference"
    lines.insert(gl + 2, '\tsetAttr ".dt" 2;')
    print("V: Jenn_GH_GEO_LAYER displayType -> 2")

    # --- S: info group, straight after the |JENN top transform's block --------
    jenn = only(lines, 'createNode transform -n "JENN";')
    nxt = next(i for i in range(jenn + 1, len(lines))
               if lines[i].startswith("createNode "))
    lines[nxt:nxt] = INFO_GROUP
    print("S: Jenn_info_GRP + Jenn_rig_v1_6 stamp inserted")

    # --- W: influence budget and, if given, the pruned weights ---------------
    mi = only(lines, MI_FROM)
    assert '\tsetAttr ".mmi" yes;' in lines[mi - 3:mi], "mmi not already set"
    lines[mi] = MI_TO
    print("W: maxInfluences 5 -> 4")

    if skin_export:
        new = open(skin_export, encoding="utf-8", errors="surrogateescape").read().split("\n")
        a, b = only(lines, WL_START), only(lines, WL_END)
        c, d = only(new, WL_START), only(new, WL_END)
        assert a < b and c < d
        print("W: wl block %d lines -> %d lines" % (b - a, d - c))
        lines = lines[:a] + new[c:d] + lines[b:]
    else:
        print("W: no skin export given, weights left as delivered")

    # --- header ---------------------------------------------------------------
    lines = [re.sub(r"^//Name: .*$", "//Name: %s" % DST, l) for l in lines]
    lines = [re.sub(r"^// End of .*$", "// End of %s" % DST, l) for l in lines]

    open(DST, "w", encoding="utf-8", errors="surrogateescape").write("\n".join(lines))
    print("wrote %s (%d lines)" % (DST, len(lines)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
