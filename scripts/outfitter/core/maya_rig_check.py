"""Rig Check's Maya half: read the open scene into facts, and apply fixes to it.

The decisions live in the pure :mod:`core.rig_check`. Every fix re-scans first, so a report
made before the scene changed cannot act on stale nodes; each runs as one undo step and saves
nothing. It also works from the Script Editor or mayapy::

    from outfitter.core import maya_rig_check
    for issue in maya_rig_check.scan().issues:
        print(issue.level, issue.title)

Weights are written through attributes rather than ``MFnSkinCluster.setWeights``, which Maya's
undo does not cover (20,139 vertices on Eric: 5 s, and undo restores them exactly).
"""
from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass

from .. import config
from . import maya_rigs as _maya_rigs
from . import rig_check as _check
from . import rigs as _rigs
from . import skin_sets as _skin_sets

# Maya's own editor bookkeeping: "unknown" in batch sessions, and harmless everywhere.
_BENIGN_UNKNOWN = "*SavedTabsInfo"
_CONTROL_SUFFIX = "_anim"


def _cmds():
    import maya.cmds as cmds  # type: ignore

    return cmds


@dataclass(frozen=True)
class Scan:
    """One look at the scene. ``groups`` are the export groups the artist can choose from."""

    facts: _check.RigFacts
    issues: list[_check.Issue]
    groups: tuple[str, ...]


# --------------------------------------------------------------------------- #
# Reading the scene
# --------------------------------------------------------------------------- #
def _skinned_clusters(cmds, group: str) -> list[str]:
    """skinClusters with an influence under ``group`` and a mesh to deform."""
    out = []
    for skin in cmds.ls(type="skinCluster") or []:
        influences = cmds.skinCluster(skin, query=True, influence=True) or []
        if not any(path.startswith(group + "|")
                   for inf in influences for path in cmds.ls(inf, long=True)):
            continue
        geometry = cmds.skinCluster(skin, query=True, geometry=True) or []
        if any(cmds.nodeType(g) == "mesh" for g in geometry):
            out.append(skin)
    return out


def _mesh_of(cmds, skin: str) -> str | None:
    """Full path of the one mesh ``skin`` deforms, or None when it deforms several things."""
    geometry = cmds.skinCluster(skin, query=True, geometry=True) or []
    if len(geometry) != 1:
        return None
    return cmds.ls(geometry[0], long=True)[0]


def _weights(skin: str, shape: str):
    """``(MFnSkinCluster, flat weights, influence count)`` for every vertex of ``shape``."""
    from maya.api import OpenMaya as om, OpenMayaAnim as oma  # type: ignore

    sel = om.MSelectionList()
    sel.add(skin)
    sel.add(shape)
    fn = oma.MFnSkinCluster(sel.getDependNode(0))
    dag = sel.getDagPath(1)
    comp = om.MFnSingleIndexedComponent()
    obj = comp.create(om.MFn.kMeshVertComponent)
    comp.setCompleteData(om.MFnMesh(dag).numVertices)
    weights, count = fn.getWeights(dag, obj)
    return fn, weights, count


def _bind_error(cmds, skin: str, fn) -> float:
    """How far this cluster's influences are from where they were bound."""
    from maya.api import OpenMaya as om  # type: ignore

    worst = 0.0
    for path in fn.influenceObjects():
        index = fn.indexForInfluenceObject(path)
        bind = om.MMatrix(cmds.getAttr(f"{skin}.bindPreMatrix[{index}]"))
        delta = bind * path.inclusiveMatrix()
        worst = max(worst, max(abs(delta[i] - om.MMatrix.kIdentity[i]) for i in range(16)))
    return worst


def _skin_facts(cmds, skin: str) -> tuple[_check.SkinFacts, set[str]]:
    """Facts for one cluster, plus the short names of influences that carry weight."""
    settings = {
        "name": skin,
        "method": cmds.getAttr(f"{skin}.skinningMethod"),
        "max_influences": cmds.getAttr(f"{skin}.maxInfluences"),
        "maintain_max": bool(cmds.getAttr(f"{skin}.maintainMaxInfluences")),
        "normalize": cmds.getAttr(f"{skin}.normalizeWeights"),
    }
    shape = _mesh_of(cmds, skin)
    if shape is None:
        return _check.SkinFacts(mesh=skin, readable=False, **settings), set()

    fn, weights, count = _weights(skin, shape)
    vertices = len(weights) // count
    peak = over = off = 0
    used: set[int] = set()
    for vertex in range(vertices):
        row = weights[vertex * count:(vertex + 1) * count]
        nonzero = [i for i, weight in enumerate(row) if weight > 0]
        used.update(nonzero)
        peak = max(peak, len(nonzero))
        over += len(nonzero) > _check.MAX_INFLUENCES
        off += abs(sum(row) - 1.0) > _check.WEIGHT_SUM_TOLERANCE
    paths = fn.influenceObjects()
    return _check.SkinFacts(
        mesh=cmds.listRelatives(shape, parent=True, fullPath=True)[0],
        vertices=vertices, peak=peak, over_budget=over, off_sum=off,
        bind_error=_bind_error(cmds, skin, fn), **settings,
    ), {paths[i].partialPathName().rsplit("|", 1)[-1] for i in used}


def _pick_group(cmds, candidates, chosen: str | None):
    """The candidate to check: the artist's choice, else the one the body is skinned to.

    GenHuman-derived rigs carry a bigger internal deform skeleton that nothing is skinned to,
    so the biggest group is not necessarily the export skeleton.
    """
    for candidate in candidates:
        if candidate.path == chosen:
            return candidate
    return next((c for c in candidates if _skinned_clusters(cmds, c.path)), candidates[0])


def _genhuman_names() -> set[str]:
    profile = _rigs.find_profile("genhuman")
    if profile is None:
        return set()
    return {j.name[len(config.CLOTH_PREFIX):] for j in profile.skeleton.joints}


def _profile_errors(group_name: str) -> tuple[str, ...]:
    try:
        _maya_rigs.capture_profile("rig_check", "Rig check", "check", export_group=group_name)
    except Exception as exc:  # noqa: BLE001 - whatever stops capture is the finding itself
        return tuple(line.strip() for line in str(exc).splitlines() if line.strip())
    return ()


def _controls_off_default(cmds) -> tuple[str, ...]:
    out = []
    for node in cmds.ls(f"*{_CONTROL_SUFFIX}", type="transform", long=True) or []:
        if not cmds.listRelatives(node, shapes=True, type="nurbsCurve"):
            continue
        translate, rotate, scale = (cmds.getAttr(f"{node}.{a}")[0] for a in "trs")
        if (max(abs(v) for v in translate + rotate) > 1e-6
                or max(abs(v - 1.0) for v in scale) > 1e-6):
            out.append(_check.short(node))
    return tuple(out)


def _dead_switches(cmds) -> tuple[str, ...]:
    return tuple(
        f"{s.node}.{s.attr}" for s in _maya_rigs.detect_variant_switches()
        if not cmds.listConnections(f"{s.node}.{s.attr}", source=False, destination=True))


def _orphan_shapes(cmds) -> tuple[str, ...]:
    return tuple(
        mesh for mesh in cmds.ls(type="mesh", long=True) or []
        if cmds.getAttr(f"{mesh}.intermediateObject")
        and not cmds.referenceQuery(mesh, isNodeReferenced=True)
        and not cmds.listConnections(mesh, source=False, destination=True))


def _requires_arnold(scene_file: str) -> bool:
    """True when the saved ``.ma`` declares mtoa.

    The ``defaultArnold*`` nodes can't answer this: they appear in every scene once mtoa is
    loaded, whatever the file says. Only the file's own header knows.
    """
    if not scene_file.lower().endswith(".ma"):
        return False
    with open(scene_file, encoding="utf-8", errors="ignore") as fh:
        return _check.requires_arnold(fh)


def _plan(cmds, group: str, body: str, rig_name: str):
    """``(renames, taken)``: :func:`rig_check.landmark_renames`, split by what is free."""
    renames, taken = [], []
    for path, new in _check.landmark_renames(group, body, rig_name):
        (taken if cmds.objExists(new) else renames).append((path, new))
    return tuple(renames), tuple(taken)


def scan(group: str | None = None) -> Scan:
    """Check the rig in the open scene. ``group`` is a full path from :attr:`Scan.groups`."""
    cmds = _cmds()
    candidates = _maya_rigs.candidate_export_groups()
    if not candidates:
        facts = _check.RigFacts()
        return Scan(facts, _check.assemble_issues(facts), ())

    picked = _pick_group(cmds, candidates, group)
    groups = tuple(c.path for c in candidates)
    default = candidates[0]
    tied = next((c.path for c in candidates
                 if c.path != picked.path and c.joint_count == picked.joint_count), "")
    referenced = cmds.referenceQuery(picked.path, isNodeReferenced=True)
    if picked.namespace or referenced:
        facts = _check.RigFacts(group=picked.path, namespace=picked.namespace,
                                referenced=referenced)
        return Scan(facts, _check.assemble_issues(facts), groups)

    skins, weighted = [], set()
    for skin in _skinned_clusters(cmds, picked.path):
        skin_facts, used = _skin_facts(cmds, skin)
        skins.append(skin_facts)
        weighted |= used
    body_skin = max(skins, key=lambda s: s.vertices, default=None)
    body = body_skin.mesh if body_skin and body_skin.readable else ""

    scene_file = cmds.file(query=True, sceneName=True) or ""
    rig_name = _check.guess_rig_name(scene_file, picked.path)
    renames, taken = _plan(cmds, picked.path, body, rig_name)

    joints = {_check.short(j) for j in cmds.listRelatives(
        picked.path, allDescendents=True, type="joint", fullPath=True) or []}
    genhuman = _genhuman_names()
    garment_joints = {j for names in _skin_sets.derive_skin_sets(joints).values() for j in names}
    registered = next((p.label for p in _rigs.list_profiles()
                       if p.export_group == picked.name), "")
    namespaces = cmds.namespaceInfo(":", listOnlyNamespaces=True, recurse=True) or []
    unknown = [n for n in cmds.ls(type="unknown") or []
               if not fnmatch.fnmatch(n, _BENIGN_UNKNOWN)]

    facts = _check.RigFacts(
        group=picked.path,
        group_joints=picked.joint_count,
        register_default=default.name,
        tied_group=tied,
        rig_name=rig_name,
        renames=renames,
        taken=taken,
        registered_as=registered,
        missing_joints=tuple(sorted(genhuman - joints)) if genhuman else (),
        extra_joints=tuple(sorted(joints - genhuman)) if genhuman else (),
        profile_errors=_profile_errors(picked.name),
        skins=tuple(skins),
        unweighted_joints=tuple(sorted(garment_joints - weighted)) if skins else (),
        controls_off_default=_controls_off_default(cmds),
        dead_switches=_dead_switches(cmds),
        stray_namespaces=tuple(n for n in namespaces if n not in ("UI", "shared")),
        orphan_shapes=_orphan_shapes(cmds),
        unknown_nodes=tuple(unknown),
        unknown_plugins=tuple(cmds.unknownPlugin(query=True, list=True) or ()),
        requires_arnold=bool(scene_file) and _requires_arnold(scene_file),
    )
    return Scan(facts, _check.assemble_issues(facts), groups)


# --------------------------------------------------------------------------- #
# Applying fixes
# --------------------------------------------------------------------------- #
def _repath_strings(cmds, moved: list[tuple[str, str]]) -> int:
    """Rewrite DAG paths of renamed nodes inside string attributes. Returns the count.

    Maya's rename leaves these behind (Seth v00.4 has 125). A path is matched anywhere in the
    value, so paths inside JSON are covered, but only as a whole path: not as the tail of a
    longer path or the head of a longer name.
    """
    patterns = [(re.compile(r"(?<![\w:|])" + re.escape(old) + r"(?![\w:])"), new)
                for old, new in sorted(moved, key=lambda m: -len(m[0]))]  # deepest first
    changed = 0
    for node in cmds.ls(long=True) or []:
        for attr in cmds.listAttr(node, userDefined=True) or []:
            plug = f"{node}.{attr}"
            try:
                if cmds.getAttr(plug, type=True) != "string":
                    continue
                value = cmds.getAttr(plug)
            except (RuntimeError, ValueError):  # multi/compound parents can't be read whole
                continue
            if not value or "|" not in value:
                continue
            new_value = value
            for pattern, new in patterns:
                new_value = pattern.sub(lambda _m, new=new: new, new_value)
            if new_value == value:
                continue
            locked = cmds.getAttr(plug, lock=True)
            if locked:
                cmds.setAttr(plug, lock=False)
            cmds.setAttr(plug, new_value, type="string")
            if locked:
                cmds.setAttr(plug, lock=True)
            changed += 1
    return changed


def _fix_rename(cmds, scanned: Scan, rig_name: str) -> str:
    rig_name = rig_name.strip()
    if not _check.valid_rig_name(rig_name):
        raise ValueError(f"'{rig_name}' can't be used in a node name. Use letters, digits "
                         "and underscores, not starting with a digit.")
    facts = scanned.facts
    body_skin = max(facts.skins, key=lambda s: s.vertices, default=None)
    body = body_skin.mesh if body_skin and body_skin.readable else ""
    renames, taken = _plan(cmds, facts.group, body, rig_name)
    if taken:
        raise ValueError(f"'{taken[0][1]}' already exists. Nothing was renamed.")

    # UUIDs survive the renames; paths below a renamed group do not.
    todo = [(cmds.ls(path, uuid=True)[0], path, new) for path, new in renames]
    for uuid, old_path, new in todo:
        node = cmds.ls(uuid, long=True)[0]
        old = _check.short(old_path)
        cmds.rename(node, new)
        for shape in cmds.listRelatives(cmds.ls(uuid, long=True)[0], shapes=True,
                                        fullPath=True) or []:
            name = _check.short(shape)
            if name.startswith(old) and not name.startswith(new):
                cmds.rename(shape, new + name[len(old):])
    moved = [(old_path, cmds.ls(uuid, long=True)[0]) for uuid, old_path, _new in todo]
    count = _repath_strings(cmds, moved)
    return (f"Renamed {_check.count(len(todo), 'node')} and updated "
            f"{_check.count(count, 'string attribute')}.")


def _fix_settings(cmds, skin: str) -> str:
    cmds.setAttr(f"{skin}.skinningMethod", _check.SKIN_METHOD)
    cmds.setAttr(f"{skin}.maxInfluences", _check.MAX_INFLUENCES)
    cmds.setAttr(f"{skin}.maintainMaxInfluences", True)
    cmds.setAttr(f"{skin}.normalizeWeights", _check.NORMALIZE_INTERACTIVE)
    return f"Set {skin} to spec."


def _fix_weights(cmds, skin: str) -> str:
    fn, weights, count = _weights(skin, _mesh_of(cmds, skin))
    logical = [fn.indexForInfluenceObject(path) for path in fn.influenceObjects()]
    touched = 0
    for vertex in range(len(weights) // count):
        flat = weights[vertex * count:(vertex + 1) * count]
        row = [(weight, i) for i, weight in enumerate(flat) if weight > 0]
        if (len(row) <= _check.MAX_INFLUENCES
                and abs(sum(flat) - 1.0) <= _check.WEIGHT_SUM_TOLERANCE):
            continue
        keep, drop = _check.budget_row(row)
        plug = f"{skin}.weightList[{vertex}].weights"
        for i in drop:
            cmds.removeMultiInstance(f"{plug}[{logical[i]}]", b=True)
        for weight, i in keep:
            cmds.setAttr(f"{plug}[{logical[i]}]", weight)
        touched += 1
    return f"Rewrote weights on {touched} vertices of {skin}."


def _fix_orphans(cmds, scanned: Scan) -> str:
    cmds.delete(list(scanned.facts.orphan_shapes))
    return f"Deleted {_check.count(len(scanned.facts.orphan_shapes), 'unconnected shape')}."


def _fix_unknown(cmds, scanned: Scan) -> str:
    facts = scanned.facts
    for node in facts.unknown_nodes:
        cmds.lockNode(node, lock=False)
    if facts.unknown_nodes:
        cmds.delete(list(facts.unknown_nodes))
    for plugin in facts.unknown_plugins:
        cmds.unknownPlugin(plugin, remove=True)
    return (f"Deleted {_check.count(len(facts.unknown_nodes), 'unknown node')} and forgot "
            f"{_check.count(len(facts.unknown_plugins), 'plugin')}.")


def _apply(cmds, issue: _check.Issue, scanned: Scan, value: str) -> str:
    kind, _, target = issue.key.partition(":")
    if kind == "rename":
        return _fix_rename(cmds, scanned, value)
    if kind == "skin_settings":
        return _fix_settings(cmds, target)
    if kind == "skin_weights":
        return _fix_weights(cmds, target)
    if kind == "orphans":
        return _fix_orphans(cmds, scanned)
    if kind == "unknown":
        return _fix_unknown(cmds, scanned)
    raise ValueError(f"{issue.title}: Rig Check has no fix for this.")


def apply_fix(key: str, value: str = "", group: str | None = None) -> str:
    """Apply one issue's fix as a single undo step. Returns what was done.

    Raises ``ValueError`` when the issue is gone from the scene or ``value`` is unusable.
    """
    cmds = _cmds()
    scanned = scan(group)
    issue = next((i for i in scanned.issues if i.key == key), None)
    if issue is None:
        raise ValueError("That issue is no longer in the scene.")
    cmds.undoInfo(openChunk=True, chunkName=f"Outfitter Rig Check: {issue.title}")
    try:
        return _apply(cmds, issue, scanned, value)
    finally:
        cmds.undoInfo(closeChunk=True)


def apply_safe_fixes(group: str | None = None) -> list[str]:
    """Apply every ``FIX_SAFE`` issue as one undo step. Returns what was done."""
    cmds = _cmds()
    scanned = scan(group)
    cmds.undoInfo(openChunk=True, chunkName="Outfitter Rig Check: fix all safe")
    try:
        return [_apply(cmds, issue, scanned, "") for issue in scanned.issues
                if issue.fix == _check.FIX_SAFE]
    finally:
        cmds.undoInfo(closeChunk=True)


def select_nodes(nodes: tuple[str, ...]) -> int:
    """Select those of ``nodes`` still in the scene. Returns how many."""
    cmds = _cmds()
    found = [n for n in nodes if cmds.objExists(n)]
    cmds.select(found, replace=True)
    return len(found)
