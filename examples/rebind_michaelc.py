r"""Rebuild MichaelC's skinCluster so Maya's weight tools work - W1, INSIDE Maya 2026.

``skinCluster2`` was assembled by connecting nodes rather than created through Bind Skin,
so it has no deformer ``objectSet``. The weights are fine and the mesh deforms correctly,
but Paint Skin Weights resolves what it may touch *through* that set, so it will not open;
``deformer -q -g`` returns nothing; Copy and Mirror Skin Weights lean on the same plumbing.
Nothing in W2-W5 can start until this is fixed.

The fix is a rebind. Doing it in script rather than through the menus is not just
convenience - three things have to be true that the GUI will not give you by default:

* **Normalization stays OFF while the weights are written back.** 8 vertices sum to under
  0.05 and 19 more sit between 0.05 and 0.999. That is the evidence for W5, and it is
  exactly what "normalize" destroys - it scales each vertex to sum 1 while keeping its
  proportions, so vertex 4055 (shoulder height, one trace weight on the left forearm
  twist) would become 100% forearm twist. Import Weights through the menu normalizes.
* **``removeUnusedInfluence`` stays OFF.** 15 of the 89 influences carry zero weight.
  Ten are *correct* at zero (``root``, ``interaction``, ``center_of_mass``, the seven
  ``ik_*``) and GenHuman is the same. The other five are W2 and W3 - ``ball_l`` and the
  four ``calf_twist_*``. Let Maya drop them and the joints someone is about to paint onto
  are gone, and the rig no longer matches GenHuman's 89.
* **The influence order is remapped by name.** A new skinCluster does not reproduce the
  old influence indices, so weights restored positionally land on the wrong joints.

Weights are read and written through ``MFnSkinCluster``, which does not go through the
deformer set - that is why it works on the broken cluster. They are also written to a JSON
file first, so a failed restore can be replayed without re-running the rebind.

Run from Maya's Script Editor (Python), with ``MichaelC_rig_01.6.ma`` open::

    import sys
    sys.path.append(r"\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\Outfitter_maya_clothing")
    import examples.rebind_michaelc as r
    import importlib; importlib.reload(r)

    r.rebind()              # DRY RUN - reports what it would do, changes nothing
    r.rebind(apply=True)    # do it

Then save as ``MichaelC_rig_01.7.ma`` and hand it to the weights artist for W2-W6.

Dev-only, like everything in ``examples/`` - it needs a running Maya and CI only
``py_compile``s it.
"""
from __future__ import annotations

import json
import os
import tempfile

import maya.cmds as cmds

TOP = "MichaelC"
MESH = f"{TOP}_body_mesh"
EXPORT_GROUP = f"{TOP}_Joint_GRP"
OLD_SKIN = "skinCluster2"
NEW_SKIN = f"{TOP}_body_skinCluster"

# R2: classic linear. The rig already carries this on skinCluster2, but a rebind builds a
# NEW node that would silently take Maya's default, so it is passed explicitly.
SKIN_METHOD = 0

# Deviation from the bind shape, in scene units, above which the rig is not at bind pose
# and this script refuses to run. Deleting history bakes whatever is on screen.
BIND_POSE_TOLERANCE = 1e-4

BACKUP = os.path.join(tempfile.gettempdir(), "michaelc_weights_backup.json")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _find(name: str) -> str:
    """The single DAG path whose leaf is ``name``, or ``""`` when absent/ambiguous.

    Short names are not unique in this rig - the export skeleton mirrors the Hive deform
    layer joint-for-joint - so every lookup goes through full paths and refuses to guess.
    """
    found = [p for p in (cmds.ls(name, long=True) or []) if p.rsplit("|", 1)[-1] == name]
    return found[0] if len(found) == 1 else ""


def _shapes(transform: str) -> tuple[str, str]:
    """``(live shape, orig shape)`` under ``transform``; either may be ``""``."""
    live = cmds.listRelatives(
        transform, shapes=True, fullPath=True, noIntermediate=True) or []
    every = cmds.listRelatives(transform, shapes=True, fullPath=True) or []
    orig = [s for s in every if s not in live]
    return (live[0] if live else "", orig[0] if orig else "")


def _skin_fn(skin: str, shape: str):
    """``(MFnSkinCluster, MDagPath, complete-vertex MObject)`` for ``skin`` on ``shape``."""
    from maya.api import OpenMaya as om
    from maya.api import OpenMayaAnim as oma

    sel = om.MSelectionList()
    sel.add(skin)
    sel.add(shape)
    fn = oma.MFnSkinCluster(sel.getDependNode(0))
    dag = sel.getDagPath(1)

    fn_comp = om.MFnSingleIndexedComponent()
    comp = fn_comp.create(om.MFn.kMeshVertComponent)
    fn_comp.setCompleteData(om.MFnMesh(dag).numVertices)
    return fn, dag, comp


def export_joints() -> list[str]:
    """The 89 export joints under ``MichaelC_Joint_GRP``, in creation order."""
    group = _find(EXPORT_GROUP)
    if not group:
        return []
    return cmds.listRelatives(
        group, allDescendents=True, type="joint", fullPath=True) or []


# --------------------------------------------------------------------------- #
# passes
# --------------------------------------------------------------------------- #
def read_weights() -> dict:
    """Every weight off the existing skinCluster, keyed by influence *name*.

    Goes through ``MFnSkinCluster``, not the deformer set, which is why it works on a
    cluster that has none.
    """
    body = _find(MESH)
    live, _ = _shapes(body) if body else ("", "")
    if not (body and live and cmds.objExists(OLD_SKIN)):
        return {}

    fn, dag, comp = _skin_fn(OLD_SKIN, live)
    flat, n_inf = fn.getWeights(dag, comp)
    names = [p.partialPathName().rsplit("|", 1)[-1] for p in fn.influenceObjects()]
    return {
        "names": names,
        "n_inf": n_inf,
        "n_verts": len(flat) // n_inf,
        "weights": list(flat),
        "skinning_method": cmds.getAttr(f"{OLD_SKIN}.skinningMethod"),
        "max_influences": cmds.getAttr(f"{OLD_SKIN}.maxInfluences"),
    }


def check_bind_pose() -> list[str]:
    """Confirm the live shape still matches the undeformed original. Read-only.

    Deleting construction history bakes whatever is on screen into the mesh. At bind pose
    the skinCluster is an identity deformation, so the live shape and the intermediate
    original are point-for-point equal; any real deviation means the rig is posed and the
    rebind would bake that pose in as the new rest shape.
    """
    from maya.api import OpenMaya as om

    body = _find(MESH)
    if not body:
        return [f"  {MESH}: NOT FOUND"]
    live, orig = _shapes(body)
    if not (live and orig):
        return ["  could not resolve both the live and original shapes"]

    def points(path: str):
        sel = om.MSelectionList()
        sel.add(path)
        return om.MFnMesh(sel.getDagPath(0)).getPoints(om.MSpace.kObject)

    a, b = points(live), points(orig)
    if len(a) != len(b):
        return [f"  vertex count differs: live {len(a)}, orig {len(b)} - ABORT"]

    worst = max(((a[i] - b[i]).length(), i) for i in range(len(a)))
    if worst[0] > BIND_POSE_TOLERANCE:
        return [f"  NOT at bind pose: vertex {worst[1]} is {worst[0]:.6f} off the bind "
                f"shape (tolerance {BIND_POSE_TOLERANCE}) - ABORT, reset the rig first"]
    return [f"  at bind pose (worst vertex deviates {worst[0]:.2e})"]


def rebind(apply: bool = False) -> list[str]:
    """Read weights, delete history, bind properly, write the weights back.

    Every step is reported before anything changes, and the weights are dumped to
    :data:`BACKUP` before the old cluster goes.
    """
    out: list[str] = []

    pose = check_bind_pose()
    out += pose
    if any("ABORT" in line for line in pose):
        return out

    data = read_weights()
    if not data:
        return out + [f"  could not read weights off {OLD_SKIN} - ABORT"]
    out.append(f"  read {data['n_verts']} verts x {data['n_inf']} influences "
               f"from {OLD_SKIN}")

    joints = export_joints()
    if len(joints) != data["n_inf"]:
        out.append(f"  WARNING: {len(joints)} joints under {EXPORT_GROUP} but "
                   f"{data['n_inf']} influences on the cluster")
    missing = set(data["names"]) - {j.rsplit("|", 1)[-1] for j in joints}
    if missing:
        return out + [f"  influences not found under {EXPORT_GROUP}: "
                      f"{sorted(missing)} - ABORT"]

    peak = max(
        sum(1 for w in data["weights"][v * data["n_inf"]:(v + 1) * data["n_inf"]] if w)
        for v in range(data["n_verts"]))

    out.append(f"  would write {BACKUP}")
    out.append(f"  would delete history on {MESH} (removes {OLD_SKIN})")
    out.append(f"  would bind {len(joints)} joints as {NEW_SKIN}, "
               f"skinMethod={SKIN_METHOD} (classic linear), "
               f"removeUnusedInfluence=False, maxInfluences={peak}")
    out.append("  would restore weights by influence NAME, normalization OFF")
    if not apply:
        out.append("  DRY RUN - nothing changed")
        return out

    with open(BACKUP, "w", encoding="utf-8") as fh:
        json.dump(data, fh)
    out.append(f"  wrote {BACKUP}")

    body = _find(MESH)
    cmds.delete(body, constructionHistory=True)
    out.append(f"  deleted history on {MESH}")

    skin = cmds.skinCluster(
        joints, body,
        name=NEW_SKIN,
        toSelectedBones=True,
        bindMethod=0,               # closest joint - deterministic, no heat-map surprises
        skinMethod=SKIN_METHOD,
        normalizeWeights=1,         # interactive; switched off below while writing
        obeyMaxInfluences=False,    # R3 decides the budget; W6 does the pruning
        maximumInfluences=peak,
        removeUnusedInfluence=False)[0]
    out.append(f"  bound {skin}")

    out += restore_weights(data, skin, apply=True)
    return out


def restore_weights(data: dict, skin: str, apply: bool = False) -> list[str]:
    """Write ``data``'s weights onto ``skin``, matching influences by name.

    Normalization is disabled for the write and restored afterwards: the under-weighted
    vertices are W5's evidence, and normalizing would silently repair-and-corrupt them.
    """
    from maya.api import OpenMaya as om

    body = _find(MESH)
    live, _ = _shapes(body) if body else ("", "")
    if not live:
        return ["  body shape not found - weights NOT restored"]
    if not apply:
        return ["  DRY RUN - weights not restored"]

    fn, dag, comp = _skin_fn(skin, live)
    new_names = [p.partialPathName().rsplit("|", 1)[-1] for p in fn.influenceObjects()]
    old_at = {n: i for i, n in enumerate(data["names"])}

    n_old, n_new = data["n_inf"], len(new_names)
    src = data["weights"]
    values = om.MDoubleArray()
    values.setLength(data["n_verts"] * n_new)
    for v in range(data["n_verts"]):
        base_new, base_old = v * n_new, v * n_old
        for j, name in enumerate(new_names):
            i = old_at.get(name)
            values[base_new + j] = src[base_old + i] if i is not None else 0.0

    idx = om.MIntArray([fn.indexForInfluenceObject(p) for p in fn.influenceObjects()])

    was = cmds.getAttr(f"{skin}.normalizeWeights")
    cmds.setAttr(f"{skin}.normalizeWeights", 0)
    try:
        fn.setWeights(dag, comp, idx, values, False)
    finally:
        cmds.setAttr(f"{skin}.normalizeWeights", was)
    return [f"  restored {data['n_verts']} x {n_new} weights onto {skin} "
            f"(normalization off during the write)"]


def verify(skin: str = NEW_SKIN) -> list[str]:
    """Confirm the rebind achieved what W1 is for. Read-only."""
    out: list[str] = []
    if not cmds.objExists(skin):
        return [f"  {skin}: NOT FOUND"]

    sets = cmds.listConnections(skin, type="objectSet") or []
    geo = cmds.deformer(skin, query=True, geometry=True) or []
    out.append(f"  deformer set: {sets[0] if sets else 'STILL MISSING'}")
    out.append(f"  deformer -q -g: {geo or 'STILL EMPTY'}")
    out.append(f"  skinningMethod: {cmds.getAttr(f'{skin}.skinningMethod')} "
               f"(0 = classic linear)")
    out.append(f"  influences: {len(cmds.skinCluster(skin, query=True, influence=True) or [])}")

    if os.path.exists(BACKUP):
        with open(BACKUP, encoding="utf-8") as fh:
            data = json.load(fh)
        body = _find(MESH)
        live, _ = _shapes(body) if body else ("", "")
        fn, dag, comp = _skin_fn(skin, live)
        flat, n_new = fn.getWeights(dag, comp)
        names = [p.partialPathName().rsplit("|", 1)[-1] for p in fn.influenceObjects()]
        old_at = {n: i for i, n in enumerate(data["names"])}
        n_old = data["n_inf"]
        worst = 0.0
        for v in range(data["n_verts"]):
            for j, name in enumerate(names):
                i = old_at.get(name)
                want = data["weights"][v * n_old + i] if i is not None else 0.0
                worst = max(worst, abs(flat[v * n_new + j] - want))
        out.append(f"  max weight deviation from the backup: {worst:.3e}")

        sums = [sum(flat[v * n_new:(v + 1) * n_new]) for v in range(data["n_verts"])]
        out.append(f"  vertex sums preserved - {sum(1 for s in sums if s >= 0.999)} at 1.0, "
                   f"{sum(1 for s in sums if 0.05 <= s < 0.999)} partial, "
                   f"{sum(1 for s in sums if s < 0.05)} near-zero "
                   f"(expected 5253 / 19 / 8 - W5 is still there to fix)")
    return out


def run(apply: bool = False) -> None:
    """W1 end to end, with a report. Dry run by default."""
    print(f"\n=== rebind MichaelC ({'APPLY' if apply else 'DRY RUN'}) ===")
    for line in rebind(apply=apply):
        print(line)
    if apply:
        print("\n--- verify ---")
        for line in verify():
            print(line)
        print(f"\nNow save as {TOP}_rig_01.7.ma. W2-W6 are still open.")
