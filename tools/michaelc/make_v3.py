"""Write MichaelC_rig_v3.ma, the release file, from the v2.3 build.

`MichaelC_rig_v2.2.ma` on disk is byte-identical to the file that shipped as
`MichaelC_rig_v3.ma`, and both carry the finished **v2.3** content (stamp
`MichaelC_rig_v2_3`, maxInfluences 4, no turntable nodes, guide layer hidden). It is
therefore the honest source to regenerate the release from, and doing it this way means
no backup is needed: the input is still on disk.

Two things the v2.x line left wrong, both about the file being honest rather than about
rig behaviour:

  S   the in-scene stamp still said `MichaelC_rig_v2_3` and the header `//Name:` still
      said `MichaelC_rig_v2.2.ma`, while the file ships as v3.
  V   `MichaelC_GEO_LAYER` lost `displayType 2` somewhere in the v2.x branch. 01.8 had
      it, so the body mesh was not selectable in the viewport; v3 had it back at 0 and
      the mesh took clicks again. The v2.3 pass re-applied 01.8's guide-layer and
      bendy-spline fixes but not this one.

Nothing else is touched - no weights, no nodes, no connections.
"""
from __future__ import annotations

import re
import sys

SRC = "MichaelC_rig_v2.2.ma"
DST = "MichaelC_rig_v3.ma"

STAMP_FROM = 'createNode transform -n "MichaelC_rig_v2_3" -p "MichaelC_info_GRP";'
STAMP_TO = 'createNode transform -n "MichaelC_rig_v3" -p "MichaelC_info_GRP";'
GEO_LAYER = 'createNode displayLayer -n "MichaelC_GEO_LAYER";'


def only(lines: list[str], needle: str) -> int:
    hits = [i for i, l in enumerate(lines) if l == needle]
    assert len(hits) == 1, "%r matched %d lines" % (needle, len(hits))
    return hits[0]


def main() -> int:
    lines = open(SRC, encoding="utf-8", errors="surrogateescape").read().split("\n")

    stamp = only(lines, STAMP_FROM)
    lines[stamp] = STAMP_TO
    print("S: stamp MichaelC_rig_v2_3 -> MichaelC_rig_v3 at line %d" % (stamp + 1))

    gl = only(lines, GEO_LAYER)
    assert lines[gl + 1].startswith("\trename -uid"), lines[gl + 1]
    assert '\tsetAttr ".dt" 2;' not in lines[gl:gl + 8], "geo layer already reference"
    lines.insert(gl + 2, '\tsetAttr ".dt" 2;')
    print("V: MichaelC_GEO_LAYER displayType -> 2 (body mesh not selectable, as 01.8)")

    lines = [re.sub(r"^//Name: .*$", "//Name: %s" % DST, l) for l in lines]
    lines = [re.sub(r"^// End of .*$", "// End of %s" % DST, l) for l in lines]

    open(DST, "w", encoding="utf-8", errors="surrogateescape").write("\n".join(lines))
    print("wrote %s (%d lines)" % (DST, len(lines)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
