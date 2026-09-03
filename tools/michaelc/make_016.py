"""Produce MichaelC_rig_01.6.ma from 01.5: structural Outfitter-readiness fixes.

Text surgery on the .ma (same approach as the GenHuman->Daniel rename). Structure only -
skin weights are untouched, because normalizing them and rebuilding the missing deformer
set are Maya operations, not text edits.
"""
from __future__ import annotations

import re
import sys

SRC = "MichaelC_rig_01.5.ma"
DST = "MichaelC_rig_01.6.ma"

# Nodes removed entirely (block + every statement referencing them).
DELETE = {
    "PAO_Skeleton_CNT", "Hive_Solver_CNT",   # asset containers sealing the skeletons
    "hyperLayout1", "hyperLayout2",          # their member lists
    "BodyShapeOrig2",                        # orphan intermediate shape (~20% of the file)
    "groupParts1", "groupId1", "groupId2",   # pre-bind leftovers on the skin chain
}

# Whole-node renames, longest name first so BodyShapeOrig is not eaten by BodyShape.
RENAME = [
    ("BodyShapeOrig", "MichaelC_body_meshShapeOrig"),
    ("BodyShape", "MichaelC_body_meshShape"),
    ("Skeleton", "MichaelC_Joint_GRP"),
    ("Geo", "MichaelC_Mesh_GRP"),
    ("Body", "MichaelC_body_mesh"),
]
PREFIX_FROM, PREFIX_TO = "Michael_Hive2", "MichaelC"

# The skin chain: skinCluster2 -> groupParts1 -> BodyShape.inMesh becomes direct.
REWIRE = (
    'connectAttr "groupParts1.og" "BodyShape.i";',
    'connectAttr "skinCluster2.og[0]" "BodyShape.i";',
)
# instObjGroups size hint for the two groupIds being deleted.
DROP_IN_BLOCK = {"BodyShape": ['\tsetAttr -s 2 ".iog[0].og";']}

INFO_GROUP = [
    'createNode transform -n "MichaelC_info_GRP" -p "MichaelC";',
    'createNode transform -n "MichaelC_rig_v01_6" -p "MichaelC_info_GRP";',
    'createNode transform -n "MichaelC_rig_Maya2026" -p "MichaelC_info_GRP";',
]

VERBS = ("createNode", "connectAttr", "select", "relationship", "fileInfo",
         "requires", "currentUnit", "lockNode", "setAttr", "addAttr", "rename")


def ref_re(name: str) -> re.Pattern:
    """``name`` used as a whole node token inside a quoted string."""
    return re.compile(r'(?<=[|"])' + re.escape(name) + r'(?=[."|\[])')


def chunk(lines: list[str]) -> list[tuple[str | None, list[str]]]:
    """Split into (owning node name | None, lines). A createNode block owns its indented
    continuation lines plus any column-0 ``lockNode`` that trails it."""
    out: list[tuple[str | None, list[str]]] = []
    cur_owner: str | None = None
    cur: list[str] = []
    for line in lines:
        if line.startswith("createNode "):
            if cur:
                out.append((cur_owner, cur))
            m = re.search(r'-n "((?:\\.|[^"\\])*)"', line)
            cur_owner = m.group(1) if m else None
            cur = [line]
            continue
        indented = line[:1] in (" ", "\t")
        if cur_owner is not None and (indented or line.startswith("lockNode ")):
            cur.append(line)
            continue
        if cur:
            out.append((cur_owner, cur))
        cur_owner, cur = None, [line]
    if cur:
        out.append((cur_owner, cur))
    return out


def main() -> int:
    text = open(SRC, encoding="utf-8", errors="surrogateescape").read()
    lines = text.split("\n")

    # sanity: every column-0 line must start with a known verb or be a comment/blank
    for i, line in enumerate(lines, 1):
        if not line or line[:1] in (" ", "\t") or line.startswith("//"):
            continue
        if not line.startswith(VERBS):
            print(f"UNEXPECTED column-0 statement at line {i}: {line[:80]!r}")
            return 1

    # 1) rewire the skin chain before deleting groupParts1
    hits = sum(1 for L in lines if L.strip() == REWIRE[0])
    if hits != 1:
        print(f"expected exactly 1 rewire line, found {hits}")
        return 1
    lines = [REWIRE[1] if L.strip() == REWIRE[0] else L for L in lines]

    # 2) drop deleted node blocks and every statement that references them
    refs = {n: ref_re(n) for n in DELETE}
    kept: list[str] = []
    dropped_blocks = dropped_stmts = 0
    for owner, block in chunk(lines):
        if owner in DELETE:
            dropped_blocks += 1
            continue
        if owner is None:
            body = "\n".join(block)
            if any(rx.search(body) for rx in refs.values()):
                dropped_stmts += len(block)
                continue
        if owner in DROP_IN_BLOCK:
            block = [L for L in block if L not in DROP_IN_BLOCK[owner]]
        kept.extend(block)
    lines = kept

    # 3) renames
    for old, new in RENAME:
        rx = ref_re(old)
        lines = [rx.sub(new, L) for L in lines]
    prx = re.compile(r'(?<=[|"])' + re.escape(PREFIX_FROM))
    lines = [prx.sub(PREFIX_TO, L) for L in lines]

    # 4) info group, inserted straight after the |MichaelC top transform's block
    out: list[str] = []
    inserted = False
    for owner, block in chunk(lines):
        out.extend(block)
        if owner == "MichaelC" and not inserted:
            out.extend(INFO_GROUP)
            inserted = True
    if not inserted:
        print("could not find the MichaelC top node to insert the info group after")
        return 1
    lines = out

    # 5) header
    lines = [re.sub(r'^//Name: .*$', f"//Name: {DST}", L) for L in lines]
    lines = [re.sub(r'^// End of .*$', f"// End of {DST}", L) for L in lines]

    open(DST, "w", encoding="utf-8", errors="surrogateescape").write("\n".join(lines))
    print(f"wrote {DST}: dropped {dropped_blocks} node blocks, "
          f"{dropped_stmts} referencing statements")
    return 0


if __name__ == "__main__":
    sys.exit(main())
