"""Structural profile of a rig .ma, headless: export-group candidates, joints, collisions.

Mirrors what maya_rigs.candidate_export_groups() / _find_export_root() would see.
"""
import sys, collections
sys.path.insert(0, "/home/sgold/dev/repos/Outfitter_maya_clothing/scripts")
sys.path.insert(0, "/home/sgold/dev/repos/Outfitter_maya_clothing/tools/michaelc")
import dag2

path = sys.argv[1]
paths, types, kids = dag2.parse(path)

def short(p):
    return p.rsplit("|", 1)[-1]

# every transform that DIRECTLY parents a joint = an export-group candidate
cands = []
for p in paths:
    if types[p] != "transform":
        continue
    direct = [c for c in kids.get(p, []) if types[c] == "joint"]
    if not direct:
        continue
    # all joints anywhere below
    stack, n = list(kids.get(p, [])), 0
    first_joint = None
    while stack:
        c = stack.pop()
        if types.get(c) == "joint":
            n += 1
        stack.extend(kids.get(c, []))
    cands.append((n, p, short(direct[0])))

cands.sort(key=lambda c: (-c[0], c[1]))
print("=== export-group candidates (rank order Outfitter uses) ===")
for n, p, rj in cands:
    print(f"  {n:4d} joints  root:{rj:<12} {p}")

print()
print("=== top-level DAG roots ===")
for p in paths:
    if p.count("|") == 1:
        print("  ", p, types[p])

print()
print("=== duplicate short names (DAG) ===")
c = collections.Counter(short(p) for p in paths)
dupes = {k: v for k, v in c.items() if v > 1}
print(f"  {len(dupes)} short names used more than once (total extra nodes: {sum(dupes.values())-len(dupes)})")
for k, v in sorted(dupes.items(), key=lambda kv: -kv[1])[:15]:
    print(f"    {k} x{v}")

print()
print("=== joints under each candidate's top pick ===")
if cands:
    n, top, rj = cands[0]
    stack, js = list(kids.get(top, [])), []
    while stack:
        cc = stack.pop()
        if types.get(cc) == "joint":
            js.append(short(cc))
        stack.extend(kids.get(cc, []))
    print(f"  {top}: {len(js)} joints")
    print("  " + " ".join(sorted(js)))
