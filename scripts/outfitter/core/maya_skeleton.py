"""Maya-side rebuild of the canonical ``cloth_*`` skeleton - one button, no rig import.

Replays the persisted skeleton (:mod:`core.skeleton`) into the open scene: a framed
``Rig_GRP`` plus the full body-derived ``cloth_*`` joint hierarchy, at the rig's real
rest transforms. The rigger then deletes the joints their garment won't skin to (a hat
keeps ``cloth_head``; a coat keeps the spine/arms) and skins the mesh. This removes the
import-rig / duplicate / rename / prune chore entirely.

Lazy ``maya.cmds``; runs only inside Maya. Headless suite ``py_compile``s this and
unit-tests the pure skeleton data it replays, consistent with the rest of the Maya
boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, replace

from .. import config
from . import maya_publish
from . import rigs as _rigs
from . import skeleton as _skeleton
from . import skin_sets as _skin_sets

# Maya draw-override colour index for highlighted skin joints - a clear green that reads as
# "bind to these" against the default joint colour.
_SKIN_JOINT_COLOR = 14


def _cmds():
    import maya.cmds as cmds  # type: ignore

    return cmds


@dataclass
class SkeletonCaptureResult:
    dest: str
    joint_count: int
    root_group_rotate: tuple

    def summary(self) -> str:
        return (
            f"Regenerated skeleton data: {self.joint_count} joints captured from the "
            f"rig → {self.dest}. 'Create cloth skeleton' now rebuilds this pose.")


@dataclass
class SkeletonBuildResult:
    root_group: str
    root_joint: str
    joint_count: int

    def summary(self) -> str:
        return (
            f"Built the cloth_* skeleton: {self.joint_count} joints under "
            f"{self.root_group}. Bind your garment to the highlighted skin joints, "
            "then test it on the body before publishing.")


@dataclass
class ScaffoldGroupsResult:
    created_groups: list[str]   # required groups newly created this run
    grouped_meshes: list[str]   # loose objects moved under Mesh_GRP (short names)
    mesh_group_empty: bool      # Mesh_GRP holds nothing (geo not found / skipped)

    def summary(self) -> str:
        parts = []
        if self.created_groups:
            parts.append("created " + ", ".join(self.created_groups))
        if self.grouped_meshes:
            n = len(self.grouped_meshes)
            parts.append(
                f"moved {n} object{'' if n == 1 else 's'} into Mesh_GRP "
                f"({', '.join(self.grouped_meshes)})")
        body = ("Asset groups ready - " + "; ".join(parts) + "."
                if parts else "Asset groups already in place.")
        if self.mesh_group_empty:
            body += " Mesh_GRP is empty - put your garment mesh inside it."
        return body


@dataclass
class PruneResult:
    deleted: list[str]
    kept_unweighted: list[str]
    survivors: list[str]

    def summary(self) -> str:
        n = len(self.deleted)
        kept = len(self.kept_unweighted)
        msg = (
            f"Deleted {n} unused joint{'' if n == 1 else 's'}; "
            f"{len(self.survivors)} remain.")
        if kept:
            msg += (
                f" Kept {kept} unweighted interior joint{'' if kept == 1 else 's'} "
                "(they have skinned children - the chain must mirror the body).")
        return msg


def _short(path: str) -> str:
    """DAG-path tail without the namespace ("…|ns:root" -> "root")."""
    return path.rsplit("|", 1)[-1].rsplit(":", 1)[-1]


def _active_export_group() -> str:
    """The export-group name of the rig the user is working with.

    Falls back to the built-in default only when nothing is registered at all, so a fresh
    install with no profiles still finds a GenHuman rather than failing on a lookup.
    """
    profile = _rigs.resolve_profile()
    return profile.export_group if profile is not None else config.EXPORT_SKELETON_GROUP


def _find_export_root(cmds, marker: str | None = None) -> tuple[str, str]:
    """``(root joint, export group)`` full DAG paths for the rig in scene.

    Mirrors ``examples/build_example_asset._find_export_root``: locate the export-skeleton
    group by short name across any namespace, preferring the rig in the current selection's
    namespace. ``marker`` is that group's short name; with none given it comes from the
    active rig profile, so this resolves whichever rig the user is working with. Raises
    clearly if the rig is absent.
    """
    if marker is None:
        marker = _active_export_group()
    groups = [
        t for t in (cmds.ls(type="transform", long=True) or [])
        if _short(t) == marker
    ]
    if not groups:
        raise RuntimeError(
            f"Rig not found (no '{marker}' in the scene). Import the rig "
            "first (File > Import, 'use namespaces' ON), pose it, then regenerate.")
    grp = groups[0]
    sel = cmds.ls(selection=True, long=True) or []
    if sel:
        sel_ns = sel[0].rsplit("|", 1)[-1].split(":", 1)[0] if ":" in sel[0] else ""
        for g in groups:
            g_short = g.rsplit("|", 1)[-1]
            g_ns = g_short.split(":", 1)[0] if ":" in g_short else ""
            if g_ns == sel_ns:
                grp = g
                break
    roots = cmds.listRelatives(grp, children=True, type="joint", fullPath=True) or []
    if not roots:
        raise RuntimeError(f"export group '{grp}' has no child joint (expected 'root').")
    return roots[0], grp


def capture_skeleton_spec(cmds, root_joint: str, export_grp: str) -> _skeleton.SkeletonSpec:
    """Read a rig's export skeleton out of the scene as a persistable ``SkeletonSpec``.

    Walks ``root_joint``'s tree recording each joint's LOCAL transform under a
    ``cloth_<body name>`` identity; the root's parent becomes ``Rig_GRP``, carrying the
    export group's own rotation, so a later rebuild reproduces this pose. Helper joints
    never exist on the rig, so they are naturally excluded.

    Shared by the two capture paths: registering a new rig (:mod:`core.maya_rigs`) and
    re-capturing the skeleton of an already-registered one
    (:func:`capture_cloth_skeleton_from_rig`).
    """
    joints: list[_skeleton.JointSpec] = []

    def _vec(path: str, attr: str, default):
        try:
            return tuple(cmds.getAttr(f"{path}.{attr}")[0])
        except Exception:  # noqa: BLE001 - missing attr -> default
            return default

    def walk(joint_path: str, parent_cloth: str) -> None:
        cloth = f"{config.CLOTH_PREFIX}{_short(joint_path)}"
        joints.append(_skeleton.JointSpec(
            name=cloth,
            parent=parent_cloth,
            translate=_vec(joint_path, "translate", (0.0, 0.0, 0.0)),
            rotate=_vec(joint_path, "rotate", (0.0, 0.0, 0.0)),
            joint_orient=_vec(joint_path, "jointOrient", (0.0, 0.0, 0.0)),
            scale=_vec(joint_path, "scale", (1.0, 1.0, 1.0)),
            radius=float(cmds.getAttr(f"{joint_path}.radius") or 1.0),
            segment_scale_compensate=bool(
                cmds.getAttr(f"{joint_path}.segmentScaleCompensate")),
            rotate_order=int(cmds.getAttr(f"{joint_path}.rotateOrder") or 0),
        ))
        for child in (cmds.listRelatives(
                joint_path, children=True, type="joint", fullPath=True) or []):
            walk(child, cloth)

    walk(root_joint, config.RIG_GROUP)

    return _skeleton.SkeletonSpec(
        root_group=config.RIG_GROUP,
        root_group_rotate=_vec(export_grp, "rotate", (-90.0, 0.0, 0.0)),
        root_joint=f"{config.CLOTH_PREFIX}{_short(root_joint)}",
        joints=tuple(joints),
    )


def capture_cloth_skeleton_from_rig(dest=None) -> SkeletonCaptureResult:
    """Re-capture the rig's export skeleton into its registered rig profile.

    Walks ``EXPORT_SKELETON_GROUP``'s joint tree, recording each joint's LOCAL transform
    under a ``cloth_<body name>`` identity (the root's parent becomes ``Rig_GRP``, whose
    frame is the export group's own rotation - so a later rebuild reproduces this pose).
    Helper joints never exist on the rig, so they're naturally excluded. Requires the rig
    in scene.

    This is the *maintenance* path - re-capturing the skeleton of an already-registered
    rig (e.g. after a new rig build). Registering a brand-new rig goes through
    :mod:`core.maya_rigs`, which captures a whole profile rather than just the skeleton.
    ``dest`` overrides the directory the updated profile is written to.
    """
    cmds = _cmds()
    profile = _rigs.resolve_profile()
    if profile is None:
        raise RuntimeError(
            "No rig is registered, so there is no profile to update. Use 'Register rig' "
            "on the Publish tab to register this rig first.")

    root_joint, export_grp = _find_export_root(cmds, profile.export_group)
    spec = capture_skeleton_spec(cmds, root_joint, export_grp)
    updated = replace(profile, skeleton=spec)
    path = _rigs.write_profile(
        updated, dest if dest is not None else _profile_dest(profile))
    return SkeletonCaptureResult(
        dest=str(path), joint_count=len(joints),
        root_group_rotate=spec.root_group_rotate)


def _profile_dest(profile: _rigs.RigProfile):
    """Where to write an updated profile back to - beside where it was loaded from.

    A profile synced into the local library is updated in place; the bundled one is
    copied out into the local library's ``_rigs`` instead, so an installer upgrade (which
    overwrites the package) can't silently discard a re-captured skeleton.
    """
    from . import settings as _settings

    if profile.source is not None and profile.source.parent != _rigs.bundled_rigs_dir():
        return profile.source.parent
    roots = _settings.effective_library_roots()
    return _rigs.library_rigs_dir(roots[0])


def build_cloth_skeleton(spec: _skeleton.SkeletonSpec | None = None) -> SkeletonBuildResult:
    """Rebuild the canonical ``cloth_*`` skeleton in the current scene.

    Creates ``Rig_GRP`` on the export frame (the ``-90 X`` that keeps joints upright on
    the body) and every joint at its persisted local transform, in hierarchy order.
    Refuses if a ``cloth_root`` is already present, so a second click can't double the
    skeleton. Raises if the persisted data is structurally invalid.
    """
    cmds = _cmds()
    if spec is None:
        profile = _rigs.resolve_profile()
        if profile is None:
            raise RuntimeError(
                "No rig is registered. Use 'Register rig' on the Publish tab to register "
                "the rig you're authoring for, then build the cloth skeleton.")
        spec = profile.skeleton

    errors = _skeleton.validate_skeleton(spec)
    if errors:
        raise RuntimeError("cloth skeleton data is invalid:\n  " + "\n  ".join(errors))

    if cmds.objExists(spec.root_joint):
        raise RuntimeError(
            f"{spec.root_joint!r} already exists - the scene already has a cloth_* "
            "skeleton. Delete it before rebuilding.")

    # Rig_GRP carries the export-group frame; joints are LOCAL beneath it.
    if not cmds.objExists(spec.root_group):
        cmds.group(empty=True, name=spec.root_group)
    cmds.setAttr(f"{spec.root_group}.rotate", *spec.root_group_rotate, type="double3")

    for j in spec.joints:
        # Select the parent so cmds.joint creates the new joint beneath it; joints are
        # listed parent-before-child, so the parent always already exists.
        cmds.select(clear=True)
        if cmds.objExists(j.parent):
            cmds.select(j.parent)
        node = cmds.joint(name=j.name)
        current = (cmds.listRelatives(node, parent=True) or [None])[0]
        if cmds.objExists(j.parent) and current != j.parent:
            node = cmds.parent(node, j.parent)[0]

        cmds.setAttr(f"{node}.rotateOrder", j.rotate_order)
        cmds.setAttr(f"{node}.translate", *j.translate, type="double3")
        cmds.setAttr(f"{node}.jointOrient", *j.joint_orient, type="double3")
        cmds.setAttr(f"{node}.rotate", *j.rotate, type="double3")
        cmds.setAttr(f"{node}.scale", *j.scale, type="double3")
        cmds.setAttr(f"{node}.segmentScaleCompensate", j.segment_scale_compensate)
        cmds.setAttr(f"{node}.radius", j.radius)

    cmds.select(clear=True)
    return SkeletonBuildResult(
        root_group=spec.root_group, root_joint=spec.root_joint,
        joint_count=len(spec.joints))


def _loose_garment_roots(cmds, reserved: set[str]) -> list[str]:
    """Top-level (world-child) transforms holding renderable mesh geometry that aren't one
    of the asset's own groups or a namespaced (referenced rig/body) node."""
    roots: list[str] = []
    for mesh in (cmds.ls(type="mesh", long=True) or []):
        if cmds.getAttr(f"{mesh}.intermediateObject"):
            continue
        top = next((p for p in mesh.split("|") if p), "")  # first non-empty path component
        if not top or ":" in top or top in reserved:       # referenced/rig or own group
            continue
        full = "|" + top
        if full not in roots:
            roots.append(full)
    return roots


def scaffold_asset_groups(
        mesh_group: str = config.MESH_GROUP,
        ctrl_group: str = config.CTRL_GROUP) -> ScaffoldGroupsResult:
    """Create the required Mesh_GRP / Ctrl_GRP and tuck loose garment geo under Mesh_GRP.

    Run straight after the skeleton build (which already makes Rig_GRP) so a single click
    leaves the three-group asset skeleton the publish preflight requires. Mesh grouping is
    skipped when a body rig is in the scene - its body mesh would be ambiguous - so then
    Mesh_GRP is left empty for the rigger to fill. Parenting preserves world position, so the
    garment stays at its authored height.
    """
    cmds = _cmds()
    created: list[str] = []
    for grp in (ctrl_group, mesh_group):
        if not cmds.objExists(grp):
            cmds.group(empty=True, name=grp)
            created.append(grp)

    grouped: list[str] = []
    if not maya_publish.scene_has_rig():
        reserved = {mesh_group, ctrl_group, config.RIG_GROUP}
        for root in _loose_garment_roots(cmds, reserved):
            grouped.append(_short(cmds.parent(root, mesh_group)[0]))

    cmds.select(clear=True)
    mesh_empty = not (cmds.listRelatives(mesh_group, children=True) or [])
    return ScaffoldGroupsResult(created, grouped, mesh_empty)


def _scene_cloth_joints(cmds) -> dict[str, str]:
    """``{short name: short parent name}`` for every ``cloth_*`` joint in the scene.

    Short names match how the persisted skeleton and the skinCluster influences are
    referenced; a joint parented to ``Rig_GRP`` maps to that group (a non-joint), which
    :func:`core.skeleton.plan_prune` simply treats as "not a deletable joint".
    """
    parents: dict[str, str] = {}
    for j in (cmds.ls(f"{config.CLOTH_PREFIX}*", type="joint", long=True) or []):
        par = (cmds.listRelatives(j, parent=True, fullPath=True) or [None])[0]
        parents[_short(j)] = _short(par) if par else ""
    return parents


def _skin_influences(cmds, meshes: list[str]) -> set[str]:
    """Short names of every joint actually bound by a skinCluster on ``meshes``."""
    infl: set[str] = set()
    for m in meshes:
        hist = cmds.listHistory(m, pruneDagObjects=True) or []
        for sc in (cmds.ls(hist, type="skinCluster") or []):
            for inf in (cmds.skinCluster(sc, query=True, influence=True) or []):
                infl.add(_short(inf))
    return infl


def plan_prune_unskinned(mesh_group: str = "Mesh_GRP") -> _skeleton.PrunePlan:
    """Compute (without deleting anything) which ``cloth_*`` joints are safe to prune.

    Gathers the in-scene joint hierarchy and the garment's skin influences, then defers
    the selection to the pure :func:`core.skeleton.plan_prune`. Refuses if there are no
    joints (nothing built yet) or no influences at all - pruning a *zero-influence* scene
    would delete the whole skeleton, exactly the foot-gun this button must never trigger,
    so the rigger is told to skin first. Call :func:`apply_prune` to replay the plan.
    """
    cmds = _cmds()
    parents = _scene_cloth_joints(cmds)
    if not parents:
        raise RuntimeError(
            "No cloth_* joints in the scene. Run 'Create cloth skeleton' first.")

    meshes = maya_publish.find_garment_meshes(mesh_group)
    influences = _skin_influences(cmds, meshes)
    if not influences:
        raise RuntimeError(
            "No skinned influences found on the garment. Skin the mesh to the cloth_* "
            "joints before pruning - otherwise every joint would count as unused and be "
            "deleted.")

    return _skeleton.plan_prune(parents, influences)


def apply_prune(plan: _skeleton.PrunePlan) -> PruneResult:
    """Delete the joints a :func:`plan_prune_unskinned` plan selected, leaves first.

    Deletes in plan order (children before parents) and tolerates already-gone nodes, so
    re-applying a stale plan is harmless. Pair with :func:`plan_prune_unskinned` and a
    user confirmation between the two - this function is the destructive half.
    """
    cmds = _cmds()
    deleted: list[str] = []
    for name in plan.delete:
        if cmds.objExists(name):
            cmds.delete(name)
            deleted.append(name)
    cmds.select(clear=True)
    return PruneResult(
        deleted=deleted,
        kept_unweighted=list(plan.kept_unweighted),
        survivors=[s for s in plan.survivors if cmds.objExists(s)],
    )


@dataclass
class SkinSetResult:
    set_name: str
    asset_type: str
    joints: list[str]
    missing: list[str]

    def summary(self) -> str:
        n = len(self.joints)
        msg = (
            f"{self.set_name}: {n} recommended skin joint{'' if n == 1 else 's'} for a "
            f"{self.asset_type} selected and highlighted green.")
        if self.missing:
            k = len(self.missing)
            msg += (
                f" {k} recommended joint{'' if k == 1 else 's'} not in this skeleton "
                "(already pruned, or a different skeleton revision).")
        return msg + " Bind your mesh to the selection (Skin > Bind Skin)."


def _resolve_joint(cmds, short: str) -> str | None:
    """Map a short ``cloth_*`` joint name to its full DAG path in the scene (or None).

    Tries the bare name first, then any namespace, mirroring how the skeleton is normally
    built in the root namespace but tolerating an imported/namespaced one.
    """
    for pattern in (short, f"*:{short}"):
        matches = cmds.ls(pattern, type="joint", long=True) or []
        if matches:
            return matches[0]
    return None


def _set_skin_highlight(cmds, joint: str, on: bool) -> None:
    """Enable/disable the green draw override on one joint (best-effort).

    Clearing must keep ``overrideEnabled = 1`` (colour back to the default index 0), NOT
    disable the override: Maya inherits draw-override colour *down* the DAG, so a joint
    with ``overrideEnabled = 0`` shows its parent's colour rather than the default. With
    the override left disabled, every non-member under a green member (head under neck,
    fingers under hand, feet under calf) bled green - the whole skeleton looked selected.
    Holding the override on with colour 0 breaks that inheritance so non-members read as
    default-coloured.
    """
    try:
        cmds.setAttr(f"{joint}.overrideEnabled", 1)
        cmds.setAttr(f"{joint}.overrideColor", _SKIN_JOINT_COLOR if on else 0)
    except Exception:  # noqa: BLE001 - a locked/connected override attr must not abort
        pass


def build_skin_set(asset_type: str) -> SkinSetResult:
    """Build (or rebuild) ``cloth_skin_SET`` with the recommended skin joints for a type.

    Answers the rigger's "which of these ~89 joints do I bind to?": resolves the per-type
    recommendation (:mod:`core.skin_sets`) against the joints actually in the scene, drops
    them into a Maya selection set, clears any prior highlight off every ``cloth_*`` joint
    and paints the recommended ones green, then leaves them selected so the next action is
    Bind Skin. Non-destructive - the set + colour never touch joint names, so attach is
    unaffected, and the rigger can still add/remove influences by hand.

    Raises if no skeleton is present, or if none of the type's recommended joints exist
    (e.g. a hat skeleton asked for a coat's set) - nothing to select would only confuse.
    """
    cmds = _cmds()
    parents = _scene_cloth_joints(cmds)
    if not parents:
        raise RuntimeError(
            "No cloth_* joints in the scene. Run 'Create cloth skeleton' first.")

    profile = _rigs.resolve_profile()
    if profile is None:
        raise RuntimeError(
            "No rig is registered, so there is no skin-set recommendation to apply. "
            "Use 'Register rig' on the Publish tab first.")
    recommended = profile.skin_set(asset_type)
    if not recommended:
        raise RuntimeError(
            f"The {profile.label} rig has no recommended skin joints for a "
            f"{asset_type!r}. Add them to skinSets in {profile.source}, or select the "
            "joints by hand and bind.")

    plan = _skin_sets.plan_skin_set(asset_type, set(parents), recommended)
    if plan.is_empty:
        raise RuntimeError(
            f"None of the recommended skin joints for a {asset_type!r} are in this "
            "skeleton. Check the Type, or rebuild the skeleton before selecting.")

    nodes = [n for n in (_resolve_joint(cmds, j) for j in plan.include) if n]
    if not nodes:
        raise RuntimeError(
            f"Recommended joints for {asset_type!r} resolved to nothing in the scene.")

    # Clear any previous highlight off the whole cloth_ skeleton so re-running for a
    # different Type doesn't leave stale-green joints behind, then paint this set.
    for short in parents:
        node = _resolve_joint(cmds, short)
        if node:
            _set_skin_highlight(cmds, node, on=False)
    for node in nodes:
        _set_skin_highlight(cmds, node, on=True)

    if cmds.objExists(plan.set_name):
        cmds.delete(plan.set_name)
    cmds.sets(nodes, name=plan.set_name)
    cmds.select(nodes, replace=True)

    return SkinSetResult(
        set_name=plan.set_name, asset_type=asset_type,
        joints=[_short(n) for n in nodes], missing=list(plan.missing))
