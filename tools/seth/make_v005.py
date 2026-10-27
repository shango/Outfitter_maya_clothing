"""Produce Seth_rig_v00.5.ma from v00.4: give the generic landmarks Seth's own names.

v00.4 holds its export skeleton in `Skeleton` and its body in `Geo`, the same generic names
MichaelC 01.6 and Jenn v1.6 renamed away from. `maya_skeleton._find_export_root` resolves the
export group by short name and takes the first match, and the registered markers would be
`Skeleton` / `Seth`, which `maya_publish.scene_has_rig` matches as substrings of any node name.
Renaming has to happen before registration: a profile captured against the old names breaks.

Weights are deliberately left as delivered (maxInfluences 8, peak 10).

Text surgery on the .ma, same reason as tools/eric/make_v07.py: a full save from batch Maya
can duplicate nodes it cannot register. Every byte outside the renamed tokens is carried over.
A name is replaced only as a whole node token inside a quoted string, which covers
createNode -n/-p, connectAttr endpoints and full DAG paths (`"|Seth|Skeleton|root|..."`).

    python3 tools/seth/make_v005.py
"""
from __future__ import annotations

import re

SRC = "Seth_rig_v00.4.ma"
DST = "Seth_rig_v00.5.ma"

# Longest first, so Seth_bodyShapeOrig is not eaten by Seth_bodyShape.
RENAME = [
    ("Seth_bodyShapeOrig", "Seth_body_meshShapeOrig"),
    ("Seth_bodyShape", "Seth_body_meshShape"),
    ("Seth_body", "Seth_body_mesh"),
    ("Skeleton", "Seth_Joint_GRP"),
    ("Geo", "Seth_Mesh_GRP"),
]


def ref_re(name: str) -> re.Pattern:
    """``name`` used as a whole node token inside a quoted string."""
    return re.compile(r'(?<=[|"])' + re.escape(name) + r'(?=[."|\[])')


def main() -> int:
    text = open(SRC, encoding="utf-8", errors="surrogateescape").read()
    for _old, new in RENAME:
        assert not ref_re(new).search(text), "%r already in the source" % new

    lines = text.split("\n")
    for old, new in RENAME:
        rx = ref_re(old)
        hits = sum(len(rx.findall(l)) for l in lines)
        assert hits, "rename %r matched nothing" % old
        lines = [rx.sub(new, l) for l in lines]
        print("R: %-20s -> %-24s (%d references)" % (old, new, hits))

    name = [i for i, l in enumerate(lines) if l.startswith("//Name: ")]
    assert name == [1], name
    lines[1] = "//Name: %s" % DST

    out = "\n".join(lines)
    for old, _new in RENAME:
        assert not ref_re(old).search(out), "%r survived" % old
    with open(DST, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
        fh.write(out)
    print("wrote", DST)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
