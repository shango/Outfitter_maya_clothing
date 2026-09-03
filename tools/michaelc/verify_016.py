"""Referential-integrity + structure verification of a rewritten .ma."""
from __future__ import annotations

import re
import sys
import collections

sys.path.insert(0, "/home/sgold/dev/repos/Outfitter_maya_clothing/scripts")
from outfitter.core import ma_parse  # noqa: E402

CN = re.compile(r'^createNode\s+(\S+)\s+(.*)$')
NAME = re.compile(r'-n\s+"((?:\\.|[^"\\])*)"')
PARENT = re.compile(r'-p\s+"((?:\\.|[^"\\])*)"')
CONN = re.compile(r'^connectAttr\s+(?:-\S+\s+)*"([^"]+)"\s+"([^"]+)"')


def plug_node(plug: str) -> str:
    """Node short name from a plug string ('|a|b|n.attr[0].sub' -> 'n')."""
    node = plug.split(".", 1)[0]
    return node.rsplit("|", 1)[-1]


def load(path: str):
    text = open(path, encoding="utf-8", errors="surrogateescape").read()
    names: set[str] = set()
    types: dict[str, str] = {}
    parents: list[tuple[str, str]] = []
    conns: list[tuple[str, str]] = []
    for stmt in ma_parse.iter_statements(text):
        if stmt.startswith("createNode "):
            m = CN.match(stmt)
            if not m:
                continue
            nm = NAME.search(m.group(2))
            if not nm:
                continue
            n = nm.group(1)
            names.add(n)
            types[n] = m.group(1)
            pm = PARENT.search(m.group(2))
            if pm:
                parents.append((n, pm.group(1).rsplit("|", 1)[-1]))
        elif stmt.startswith("connectAttr "):
            m = CONN.match(stmt)
            if m:
                conns.append((m.group(1), m.group(2)))
    return text, names, types, parents, conns


def main() -> int:
    src, dst = sys.argv[1], sys.argv[2]
    _, n0, t0, _, c0 = load(src)
    text, names, types, parents, conns = load(dst)
    bad = 0

    print(f"nodes: {len(n0)} -> {len(names)}  ({len(names) - len(n0):+d})")
    print(f"connections: {len(c0)} -> {len(conns)}  ({len(conns) - len(c0):+d})")
    print(f"removed: {sorted(n0 - names)}")
    print(f"added:   {sorted(names - n0)}")
    print()

    # 1) DAG parents resolve
    missing_p = sorted({p for _, p in parents if p not in names})
    print(f"[{'FAIL' if missing_p else 'ok'}] createNode -p parents resolve"
          + (f" -- missing: {missing_p[:10]}" if missing_p else ""))
    bad += bool(missing_p)

    # 2) connectAttr endpoints resolve
    dangling = collections.Counter()
    for a, b in conns:
        for plug in (a, b):
            if plug.startswith(":") or plug.split(".", 1)[0].startswith(":"):
                continue
            n = plug_node(plug)
            if n and n not in names:
                dangling[n] += 1
    print(f"[{'FAIL' if dangling else 'ok'}] connectAttr endpoints resolve"
          + (f" -- dangling: {dict(list(dangling.items())[:10])}" if dangling else ""))
    bad += bool(dangling)

    # 3) no residual text references to deleted node names
    gone = sorted(n0 - names)
    residual = {g: len(re.findall(r'(?<=[|"])' + re.escape(g) + r'(?=[."|\[])', text))
                for g in gone}
    residual = {k: v for k, v in residual.items() if v}
    print(f"[{'FAIL' if residual else 'ok'}] no residual references to removed nodes"
          + (f" -- {residual}" if residual else ""))
    bad += bool(residual)

    # 4) node-type census unchanged except for the intended edits
    a = collections.Counter(t0.values())
    b = collections.Counter(types.values())
    delta = {k: b[k] - a[k] for k in set(a) | set(b) if b[k] != a[k]}
    print(f"[info] node-type deltas: {delta}")

    # 5) old names fully gone / new names present
    for old in ("Skeleton", "Geo", "Body", "BodyShape", "BodyShapeOrig"):
        hits = len(re.findall(r'(?<=[|"])' + re.escape(old) + r'(?=[."|\[])', text))
        if hits:
            print(f"[FAIL] old name still referenced: {old} x{hits}")
            bad += 1
    for new in ("MichaelC_Joint_GRP", "MichaelC_Mesh_GRP", "MichaelC_body_mesh",
                "MichaelC_body_meshShape", "MichaelC_body_meshShapeOrig",
                "MichaelC_info_GRP"):
        if new not in names:
            print(f"[FAIL] expected node absent: {new}")
            bad += 1
    print(f"[{'ok' if not bad else 'FAIL'}] landmark renames applied")

    # 6) legacy prefix gone
    legacy = sorted(n for n in names if n.startswith("Michael_Hive2"))
    print(f"[{'FAIL' if legacy else 'ok'}] Michael_Hive2 prefix cleared"
          + (f" -- {len(legacy)} left" if legacy else ""))
    bad += bool(legacy)

    # 7) duplicate node names
    dup = [n for n, c in collections.Counter(
        re.findall(r'^createNode \S+ (?:-s )?-n "([^"]*)"', text, re.M)).items() if c > 1]
    print(f"[info] duplicate short names: {len(dup)} {sorted(dup)[:8]}")

    # 8) skin chain
    m = [b for a, b in conns if a == "skinCluster2.og[0]"]
    print(f"[{'ok' if m == ['MichaelC_body_meshShape.i'] else 'FAIL'}] "
          f"skinCluster2.og[0] -> {m}")
    bad += m != ["MichaelC_body_meshShape.i"]
    infl = [a for a, b in conns if b.startswith("skinCluster2.ma[")]
    print(f"[{'ok' if len(infl) == 89 else 'FAIL'}] skinCluster influences: {len(infl)}")
    bad += len(infl) != 89
    orig = [a for a, b in conns if b == "skinCluster2.ip[0].ig"]
    print(f"[{'ok' if orig else 'FAIL'}] skinCluster input geometry: {orig}")
    bad += not orig

    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
