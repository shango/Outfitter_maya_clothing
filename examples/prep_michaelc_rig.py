r"""Finish making the MichaelC rig Outfitter-ready, INSIDE Maya 2026.

MichaelC is a Hive 1.4.25 rig (Zoo Tools, UE5 naming preset). Its export skeleton -
89 joints under a group the rigger added by hand - matches GenHuman's joint names
exactly, and its body mesh is skinned to that skeleton.

**Every structural fix below is already applied in ``MichaelC_rig_01.6.ma``**, which was
produced by text surgery on 01.5 (same approach as the GenHuman->Daniel rename). Against
that file every pass here reports "already done" and the script's remaining job is the
part text surgery cannot do: normalizing the skin weights and reporting the joints the
body carries no weight on. Run it against 01.5 and it performs the structural work too,
so it stays the fallback if the rewritten file is ever mistrusted.

The structural passes exist because ``core.maya_skeleton._find_export_root`` resolves a
rig's export group by *short name* across the whole scene and takes the first match, and
``core.rigs.RigProfile.markers`` uses the same names to answer "is this rig in the
scene". Both want names unique to this rig - which is why GenHuman ships
``GenHuman_Joint_GRP`` / ``GenHuman_Mesh_GRP`` / ``GenHuman_body_mesh`` rather than bare
nouns like ``Skeleton`` / ``Geo`` / ``Body``. The asset containers matter for the same
reason: container contents are restricted, and Outfitter has to read and connect to the
joints inside them.

What this script does NOT do: repaint skin weights, or rebuild the skinCluster's missing
deformer set. :func:`audit_weights` reports both; filling them in is an artist job.

Run it from Maya's Script Editor (Python), with the rig open::

    import sys
    sys.path.append(r"\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\Outfitter_maya_clothing")
    import examples.prep_michaelc_rig as p
    import importlib; importlib.reload(p)

    p.prep()                # DRY RUN - prints every change it would make
    p.prep(apply=True)      # actually change the scene
    p.prep(apply=True, rename_legacy=True, add_info=True)   # + the optional passes

Then save the scene and register it: Publish tab > Register rig..., picking
``MichaelC_Joint_GRP`` as the export skeleton group.

Dry run is the default on purpose: the structural passes delete nodes in an 8 MB
production rig, and the deletions are not undoable across a save. Read the report first.

Every pass is idempotent, so re-running is safe.

Dev-only, like everything else in ``examples/`` - it needs a running Maya and CI only
``py_compile``s it.
"""
from __future__ import annotations

import maya.cmds as cmds

TOP = "MichaelC"

# Asset containers added to the rig 2026-08-28. ``Hive_Solver_CNT`` is black-boxed and
# holds the Hive deform layer; ``PAO_Skeleton_CNT`` holds the 89 export joints Outfitter
# has to read and connect to. Container contents are restricted, so both are dissolved -
# the nodes inside are kept, only the container wrapper goes.
CONTAINERS: tuple[str, ...] = ("PAO_Skeleton_CNT", "Hive_Solver_CNT")

# (current name, Outfitter/GenHuman-convention name). Order matters only in that each
# lookup re-resolves from the scene, so a renamed parent never strands a child.
RENAMES: tuple[tuple[str, str], ...] = (
    ("Skeleton", f"{TOP}_Joint_GRP"),
    ("Geo", f"{TOP}_Mesh_GRP"),
    ("Body", f"{TOP}_body_mesh"),
)

SKIN_CLUSTER = "skinCluster2"

# Leftovers from the pre-bind state of the mesh: the skinCluster was spliced in front of
# a groupParts that used to pass geometry straight through, so the output still detours
# through a two-vertex component group that nothing consumes.
STALE_SKIN_NODES: tuple[str, ...] = ("groupParts1", "groupId1", "groupId2")

# Intermediate shape left behind under the body transform. Its UV count (7195) doesn't
# match the live original (5972), so it is not a stale copy of the current body - it is a
# different mesh entirely, and it is ~20% of the file.
ORPHAN_SHAPE = "BodyShapeOrig2"

LEGACY_PREFIX = "Michael_Hive2"

# Joints no garment or body ever binds - zero weight on these is correct, not a defect.
# Mirrors core.skin_sets._EXCLUDE_PATTERNS for this rig's actual joint names.
EXPECTED_UNWEIGHTED: frozenset[str] = frozenset({
    "root", "interaction", "center_of_mass",
    "ik_hand_root", "ik_hand_gun", "ik_hand_l", "ik_hand_r",
    "ik_foot_root", "ik_foot_l", "ik_foot_r",
})


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #
def _find(name: str) -> str:
    """The single DAG path whose leaf is ``name``, or ``""`` when absent/ambiguous.

    Short names in this rig are not unique (the export skeleton mirrors the Hive deform
    layer joint-for-joint), so every lookup goes through full paths and refuses to guess
    when two nodes share a leaf.
    """
    found = [p for p in (cmds.ls(name, long=True) or []) if p.rsplit("|", 1)[-1] == name]
    return found[0] if len(found) == 1 else ""


def _shape_of(transform_path: str) -> str:
    """The non-intermediate shape under ``transform_path``, or ``""``."""
    for shape in (cmds.listRelatives(
            transform_path, shapes=True, fullPath=True, noIntermediate=True) or []):
        return shape
    return ""


# --------------------------------------------------------------------------- #
# passes
# --------------------------------------------------------------------------- #
def dissolve_containers(apply: bool = False) -> list[str]:
    """Remove the asset containers, keeping every node inside them.

    ``container -e -removeContainer`` deletes only the container node. A plain
    ``delete`` would take the whole skeleton with it, which is why that is never used
    here. Black-box and node locks are cleared first, since a locked or black-boxed
    container refuses edits.
    """
    out: list[str] = []
    for name in CONTAINERS:
        if not cmds.objExists(name):
            out.append(f"  {name}: already gone")
            continue
        members = cmds.container(name, query=True, nodeList=True) or []
        black = bool(cmds.getAttr(f"{name}.blackBox"))
        out.append(f"  {name}: dissolve, keeping {len(members)} member node(s)"
                   + (" [blackBox on]" if black else ""))
        if apply:
            cmds.lockNode(name, lock=False)
            if black:
                cmds.setAttr(f"{name}.blackBox", 0)
            cmds.container(name, edit=True, removeContainer=True)
    return out


def rename_landmarks(apply: bool = False) -> list[str]:
    """Give the export group, mesh group and body mesh rig-unique names."""
    out: list[str] = []
    for old, new in RENAMES:
        if cmds.objExists(new):
            out.append(f"  {old} -> {new}: already named")
            continue
        path = _find(old)
        if not path:
            out.append(f"  {old} -> {new}: NOT FOUND (or ambiguous) - skipped")
            continue
        out.append(f"  {path} -> {new}")
        if apply:
            path = cmds.rename(path, new)
            shape = _shape_of(path)
            if shape and shape.rsplit("|", 1)[-1] != f"{new}Shape":
                cmds.rename(shape, f"{new}Shape")
    return out


def delete_orphan_shape(apply: bool = False) -> list[str]:
    """Delete the stray intermediate body shape, if nothing reads its geometry."""
    if not cmds.objExists(ORPHAN_SHAPE):
        return [f"  {ORPHAN_SHAPE}: already gone"]
    readers = cmds.listConnections(
        f"{ORPHAN_SHAPE}.worldMesh", source=False, destination=True) or []
    readers += cmds.listConnections(
        f"{ORPHAN_SHAPE}.outMesh", source=False, destination=True) or []
    if readers:
        return [f"  {ORPHAN_SHAPE}: KEPT - geometry still read by {sorted(set(readers))}"]
    out = [f"  {ORPHAN_SHAPE}: delete (orphan intermediate shape)"]
    if apply:
        cmds.delete(ORPHAN_SHAPE)
    return out


def clean_skin_chain(apply: bool = False) -> list[str]:
    """Wire the skinCluster straight into the body shape and drop the stale group nodes."""
    out: list[str] = []
    if not cmds.objExists(SKIN_CLUSTER):
        return [f"  {SKIN_CLUSTER}: NOT FOUND - has the body been bound?"]

    body = _find(f"{TOP}_body_mesh") or _find("Body")
    shape = _shape_of(body) if body else ""
    if not shape:
        return ["  body shape not found - run rename_landmarks first"]

    src = f"{SKIN_CLUSTER}.outputGeometry[0]"
    current = cmds.listConnections(f"{shape}.inMesh", source=True, plugs=True) or []
    if current and current[0].split(".")[0] != SKIN_CLUSTER:
        out.append(f"  {shape}.inMesh: {current[0]} -> {src}")
        if apply:
            cmds.connectAttr(src, f"{shape}.inMesh", force=True)
    else:
        out.append(f"  {shape}.inMesh: already driven by {SKIN_CLUSTER}")

    for node in STALE_SKIN_NODES:
        if not cmds.objExists(node):
            out.append(f"  {node}: already gone")
            continue
        out.append(f"  {node}: delete (leftover from the unbound mesh)")
        if apply:
            cmds.delete(node)

    # The bind carries no deformer objectSet, which the paint-weights tool needs. That is
    # a rebind, not a rewire, so it is reported rather than attempted.
    sets = [s for s in (cmds.listConnections(f"{SKIN_CLUSTER}.message", type="objectSet") or [])]
    if not sets:
        out.append(f"  NOTE {SKIN_CLUSTER} has no deformer set - Paint Skin Weights and "
                   "'deformer -q -g' will not see it. Fix by exporting weights "
                   "(Deform > Export Weights), deleting the skinCluster, re-binding with "
                   "Skin > Bind Skin, then importing the weights back.")
    return out


def normalize_weights(apply: bool = False) -> list[str]:
    """Force-normalize the body's skin weights.

    Scales each vertex's weights up to sum 1.0. That is the right fix for a vertex that
    is merely short (0.05-0.999 - it has real influences in sensible proportion), and the
    wrong one for a vertex carrying only trace weight: scaling 0.00002 up to 1.0 hands the
    vertex entirely to whichever influence happens to hold that trace, wherever it is on
    the body. :func:`audit_weights` lists those separately and runs first, because
    normalizing destroys the evidence - afterwards every vertex sums to 1 and there is no
    way to tell which ones were guessed at.
    """
    if not cmds.objExists(SKIN_CLUSTER):
        return [f"  {SKIN_CLUSTER}: NOT FOUND"]
    out = [f"  {SKIN_CLUSTER}: forceNormalizeWeights",
           "  (repaint the trace-weight vertices the audit listed afterwards - "
           "normalizing gives them a plausible-looking but arbitrary owner)"]
    if apply:
        cmds.skinCluster(SKIN_CLUSTER, edit=True, forceNormalizeWeights=True)
    return out


def audit_weights(_apply: bool = False) -> list[str]:
    """Report influences the body carries no meaningful weight on. Read-only.

    Zero weight on a joint Outfitter recommends for a garment is not an Outfitter
    problem, but it looks like one: the garment joint moves (the rig drives it), the
    body under it does not, so the two separate on any bend. The twist joints and
    ``ball_*`` are in the shoes / pants / dress / coat skin sets
    (``core.skin_sets._COMPOSITION``), which is why they are called out here.
    """
    if not cmds.objExists(SKIN_CLUSTER):
        return [f"  {SKIN_CLUSTER}: NOT FOUND"]

    from maya.api import OpenMaya as om
    from maya.api import OpenMayaAnim as oma

    body = _find(f"{TOP}_body_mesh") or _find("Body")
    shape = _shape_of(body) if body else ""
    if not shape:
        return ["  body shape not found"]

    sel = om.MSelectionList()
    sel.add(SKIN_CLUSTER)
    sel.add(shape)
    fn = oma.MFnSkinCluster(sel.getDependNode(0))
    dag = sel.getDagPath(1)

    fn_comp = om.MFnSingleIndexedComponent()
    comp = fn_comp.create(om.MFn.kMeshVertComponent)
    fn_comp.setCompleteData(om.MFnMesh(dag).numVertices)

    weights, n_inf = fn.getWeights(dag, comp)
    names = [p.partialPathName().rsplit("|", 1)[-1] for p in fn.influenceObjects()]

    totals = [0.0] * n_inf
    per_vert = [0.0] * (len(weights) // n_inf)
    for i, w in enumerate(weights):
        totals[i % n_inf] += w
        per_vert[i // n_inf] += w

    out: list[str] = []
    empty = [names[i] for i, t in enumerate(totals)
             if t < 1e-4 and names[i] not in EXPECTED_UNWEIGHTED]
    faint = [(names[i], t) for i, t in enumerate(totals) if 1e-4 <= t < 1.0]
    if empty:
        out.append(f"  {len(empty)} influence(s) with NO weight: {', '.join(sorted(empty))}")
    if faint:
        out.append("  influence(s) with negligible weight (<1.0 total): "
                   + ", ".join(f"{n} ({t:.3f})" for n, t in sorted(faint)))
    # Three tiers, because they need three different fixes.
    dead = [v for v, t in enumerate(per_vert) if t < 1e-6]
    trace = [v for v, t in enumerate(per_vert) if 1e-6 <= t < 0.05]
    short = [v for v, t in enumerate(per_vert) if 0.05 <= t < 0.999]
    if dead:
        out.append(f"  {len(dead)} vertex/vertices with ZERO total weight - they will not "
                   f"move at all, and normalizing cannot rescue them (nothing to scale). "
                   f"Repaint: {dead[:20]}")
    if trace:
        out.append(f"  {len(trace)} vertex/vertices carrying only trace weight (<0.05). "
                   "Normalizing would hand each one entirely to whatever influence holds "
                   f"the trace - repaint instead: {trace[:20]}")
    if short:
        out.append(f"  {len(short)} vertex/vertices merely short of 1.0 (>=0.05) - "
                   "normalize_weights fixes these safely")
    if dead or trace:
        verts = ", ".join(f'"{shape}.vtx[{v}]"' for v in sorted(dead + trace)[:40])
        out.append(f"  select them with:  cmds.select([{verts}])")
    if not out:
        out.append("  weights look clean")
    return out


def rename_legacy_prefix(apply: bool = False) -> list[str]:
    """Finish the ``Michael_Hive2`` -> ``MichaelC`` rename (optional, cosmetic).

    637 nodes still carry the rig's former name, including the 178 constraints that drive
    the export skeleton. Outfitter never reads these names; this is for whoever works on
    the rig next. Renames are skipped where the target name is taken.
    """
    out: list[str] = []
    stale = [n for n in (cmds.ls(f"{LEGACY_PREFIX}*") or [])]
    if not stale:
        return ["  no Michael_Hive2* nodes left"]
    renamed = skipped = 0
    for node in stale:
        new = TOP + node[len(LEGACY_PREFIX):]
        if cmds.objExists(new):
            skipped += 1
            continue
        renamed += 1
        if apply:
            cmds.rename(node, new)
    out.append(f"  {renamed} node(s) {LEGACY_PREFIX}* -> {TOP}*"
               + (f"; {skipped} skipped (name taken)" if skipped else ""))
    return out


def add_info_group(apply: bool = False, version: str = "v01_6") -> list[str]:
    """Add the ``<rig>_info_GRP`` version markers GenHuman carries (optional).

    Pipeline convention, not something Outfitter reads - the profile's version is typed
    into the Register dialog.
    """
    grp = f"{TOP}_info_GRP"
    markers = (f"{TOP}_rig_{version}", f"{TOP}_rig_Maya2026")
    out: list[str] = []
    if cmds.objExists(grp):
        return [f"  {grp}: already present"]
    out.append(f"  create {grp} under |{TOP} with {', '.join(markers)}")
    if apply:
        cmds.group(empty=True, name=grp, parent=TOP)
        for marker in markers:
            cmds.group(empty=True, name=marker, parent=grp)
    return out


# --------------------------------------------------------------------------- #
# driver
# --------------------------------------------------------------------------- #
def prep(apply: bool = False, rename_legacy: bool = False,
         add_info: bool = False) -> None:
    """Run the passes and print a report. Dry run unless ``apply=True``."""
    if not cmds.objExists(TOP):
        raise RuntimeError(
            f"'{TOP}' is not in this scene. Open MichaelC_rig_01.5.ma (or later) first.")

    passes: list[tuple[str, object]] = [
        ("Dissolve asset containers", dissolve_containers),
        ("Rename landmark groups", rename_landmarks),
        ("Delete orphan body shape", delete_orphan_shape),
        ("Clean the skin chain", clean_skin_chain),
        # Audit BEFORE normalizing: normalizing makes every vertex sum to 1, which erases
        # the only signal distinguishing a repaired vertex from a guessed-at one.
        ("Weight audit (read-only)", audit_weights),
        ("Normalize skin weights", normalize_weights),
    ]
    if rename_legacy:
        passes.append(("Finish the Michael_Hive2 rename", rename_legacy_prefix))
    if add_info:
        passes.append(("Add the info group", add_info_group))

    mode = "APPLYING CHANGES" if apply else "DRY RUN - nothing is being changed"
    print(f"\n=== prep_michaelc_rig: {mode} ===")
    for title, fn in passes:
        print(f"\n{title}")
        for line in fn(apply):  # type: ignore[operator]
            print(line)

    print("\n=== next steps ===")
    if not apply:
        print("  Re-run with prep(apply=True) to make these changes.")
    else:
        print("  1. Save the scene.")
        print(f"  2. Publish tab > Register rig..., export group '{TOP}_Joint_GRP'.")
        print("  3. Leave the body-variant switch empty - this rig has a single body,")
        print("     so its garments publish with gender 'none'.")
