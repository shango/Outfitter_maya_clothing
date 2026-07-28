"""Retarget a garment onto another rig in a live scene - the apply half (Maya-side).

Replays a :class:`core.retarget.RetargetPlan` on the open asset: move every mapped joint
onto the destination rig's rest pose, rename it to that rig's joint name, and reframe the
garment's ``Rig_GRP`` to the destination export-group frame - all **without deforming the
mesh**, so the skin weights the rigger painted survive the move.

That last part is the whole trick, and it is one Maya flag::

    cmds.skinCluster(sc, edit=True, moveJointsMode=True)
    ...move the joints...
    cmds.skinCluster(sc, edit=True, moveJointsMode=False)

In move-joints mode the skinCluster stops driving the geometry while the influences are
repositioned, and recomputes its bind matrices when the mode is switched off - the same
mechanism as Maya's *Move Skinned Joints Tool*. Without it, every joint moved would drag
the mesh with it and the garment would be destroyed. The mode is switched off in a
``finally``: leaving a scene stuck in move-joints mode is a far worse outcome than a failed
retarget. Afterwards the skeleton's stored bind pose is reset (``dagPose -reset
-bindPose``) so a later "go to bind pose" doesn't snap it back onto the old rig.

**This does not refit the mesh.** Joints move; vertices don't. If the two rigs differ in
proportion the garment needs a manual refit and probably a weight touch-up - which is why
every result string here says so.

Lazy ``maya.cmds``; runs only inside Maya. The mapping decision is pure and headless-tested
in :mod:`core.retarget`; this module applies it.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .. import config
from . import maya_publish
from . import retarget as _retarget
from . import rigs as _rigs

# Prefix used while renaming, so a plan that *swaps* two joint names (rigs whose left/right
# conventions differ) can't have the first rename collide with the second's target.
_TEMP_PREFIX = "__outfitter_retarget__"


def _cmds():
    import maya.cmds as cmds  # type: ignore

    return cmds


def _short(path: str) -> str:
    return path.rsplit("|", 1)[-1].rsplit(":", 1)[-1]


@dataclass
class RetargetResult:
    target_rig: str
    moved: int = 0
    renamed: int = 0
    skin_clusters: int = 0
    unmatched: tuple[str, ...] = ()
    missing: tuple[str, ...] = ()  # planned joints that aren't in this scene
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        msg = (
            f"Retargeted to {self.target_rig}: moved {self.moved} joint"
            f"{'' if self.moved == 1 else 's'} onto the new rest pose "
            f"({self.renamed} renamed), weights preserved across "
            f"{self.skin_clusters} skinCluster{'' if self.skin_clusters == 1 else 's'}.")
        if self.unmatched:
            msg += (f" {len(self.unmatched)} joint(s) had no counterpart on the new rig "
                    "and were left as they are - anything weighted to them will not "
                    "follow the body.")
        # Always said, never conditional: the conversion is not finished here.
        return msg + (" Check the fit on the new body before publishing - retargeting "
                      "moves joints, it does not reshape the mesh.")


def scene_cloth_joints() -> dict[str, str]:
    """``{short cloth name: full DAG path}`` for every ``cloth_*`` joint in the scene."""
    cmds = _cmds()
    return {
        _short(j): j
        for j in (cmds.ls(f"{config.CLOTH_PREFIX}*", type="joint", long=True) or [])
    }


def _garment_skin_clusters(cmds, mesh_group: str) -> list[str]:
    clusters: list[str] = []
    for mesh in maya_publish.find_garment_meshes(mesh_group):
        hist = cmds.listHistory(mesh, pruneDagObjects=True) or []
        for sc in (cmds.ls(hist, type="skinCluster") or []):
            if sc not in clusters:
                clusters.append(sc)
    return clusters


def plan_for_scene(target, source=None) -> _retarget.RetargetPlan:
    """Plan the retarget of the garment in the open scene onto ``target``.

    Raises if there is no cloth skeleton to retarget - there is nothing useful to say
    about an empty scene.
    """
    joints = scene_cloth_joints()
    if not joints:
        raise RuntimeError(
            "No cloth_* joints in this scene, so there is nothing to retarget. Open the "
            "garment asset you want to convert first.")
    return _retarget.plan_retarget(sorted(joints), target, source)


def apply_retarget(plan: _retarget.RetargetPlan, target,
                   mesh_group: str = config.MESH_GROUP) -> RetargetResult:
    """Move and rename the garment's joints onto ``target``'s rest skeleton.

    ``plan`` comes from :func:`plan_for_scene` (or the pure planner) and ``target`` is the
    destination :class:`core.rigs.RigProfile`. Everything that moves the skeleton happens
    inside move-joints mode so the mesh is untouched; renaming happens after, in two passes
    so a name swap between the two rigs can't collide.
    """
    cmds = _cmds()
    if not plan.ok:
        raise RuntimeError(
            "None of this garment's joints map onto the target rig, so a retarget would "
            "produce nothing usable. The two skeletons may be unrelated, or the target "
            "rig's profile may need jointAliases for this rig's names.")

    in_scene = scene_cloth_joints()
    moves = [(src, spec) for src, spec in plan.ordered_moves(target) if src in in_scene]
    missing = tuple(src for src, _ in plan.ordered_moves(target) if src not in in_scene)

    result = RetargetResult(
        target_rig=target.label, unmatched=plan.unmatched, missing=missing)
    if not moves:
        raise RuntimeError(
            "The planned joints aren't in this scene. Open the garment asset itself "
            "before retargeting.")

    clusters = _garment_skin_clusters(cmds, mesh_group)
    result.skin_clusters = len(clusters)
    if not clusters:
        result.warnings.append(
            "No skinCluster found on the garment - the joints were moved, but nothing "
            "was bound to them, so check the mesh is skinned.")

    for sc in clusters:
        cmds.skinCluster(sc, edit=True, moveJointsMode=True)
    try:
        # The Rig_GRP frame belongs to the rig too: it carries the export group's own
        # rotation, and attach reproduces LOCAL joint transforms under it. Moving it here,
        # inside move-joints mode, keeps the mesh still.
        rig_group = plan_group = config.RIG_GROUP
        if cmds.objExists(rig_group):
            cmds.setAttr(f"{rig_group}.rotate",
                         *target.skeleton.root_group_rotate, type="double3")
        else:
            result.warnings.append(
                f"No '{plan_group}' in the scene - the garment's joint group could not be "
                "reframed to the new rig, so the fit may be rotated.")

        for source, spec in moves:  # parent-before-child (see RetargetPlan.ordered_moves)
            node = in_scene[source]
            # rotateOrder first: it changes how the rotate values below are interpreted.
            cmds.setAttr(f"{node}.rotateOrder", spec.rotate_order)
            cmds.setAttr(f"{node}.translate", *spec.translate, type="double3")
            cmds.setAttr(f"{node}.jointOrient", *spec.joint_orient, type="double3")
            cmds.setAttr(f"{node}.rotate", *spec.rotate, type="double3")
            cmds.setAttr(f"{node}.scale", *spec.scale, type="double3")
            cmds.setAttr(f"{node}.segmentScaleCompensate", spec.segment_scale_compensate)
            cmds.setAttr(f"{node}.radius", spec.radius)
            result.moved += 1
    finally:
        # Never leave the scene in move-joints mode, even if a setAttr failed part-way.
        for sc in clusters:
            try:
                cmds.skinCluster(sc, edit=True, moveJointsMode=False)
            except Exception as exc:  # noqa: BLE001
                result.warnings.append(f"could not leave move-joints mode on {sc}: {exc}")

    result.renamed = _rename_joints(cmds, plan, in_scene)
    _reset_bind_pose(cmds, result)
    _stamp_rig_identity(cmds, target, result)
    cmds.select(clear=True)
    return result


def _stamp_rig_identity(cmds, target, result: RetargetResult) -> None:
    """Point the scene's ``cloth_info`` at the new rig.

    The asset now fits a different rig, so leaving the old ``rigId`` embedded would make
    the retargeted garment claim to be something it no longer is - and the Publish tab
    reads this node to prefill its form. The legacy ``genHumanCompat`` is cleared when it
    is there and no longer true, rather than left to be believed by an older install.
    """
    info = maya_publish.read_info_node()
    if not info:
        result.warnings.append(
            "No cloth_info node in this scene, so the rig identity couldn't be stamped - "
            "set the rig and versions by hand on the Publish tab.")
        return
    attrs: dict[str, str] = {"rigId": target.rig_id, "rigVersions": target.version}
    if target.rig_id != _rigs.DEFAULT_RIG_ID and info.get("genHumanCompat", "").strip():
        attrs["genHumanCompat"] = ""
    maya_publish.write_info_node(attrs)


def _rename_joints(cmds, plan: _retarget.RetargetPlan, in_scene: dict[str, str]) -> int:
    """Rename mapped joints to the destination rig's names, swap-safe.

    Two passes through a temporary prefix: renaming ``a->b`` while another joint still
    holds ``b`` would make Maya silently uniquify the name (``b1``), and attach matches by
    exact name - so the joint would quietly never connect.
    """
    staged: list[tuple[str, str]] = []
    for match in plan.renames:
        node = in_scene.get(match.source)
        if node is None or not cmds.objExists(node):
            continue
        staged.append((cmds.rename(node, _TEMP_PREFIX + match.target), match.target))
    renamed = 0
    for node, final in staged:
        cmds.rename(node, final)
        renamed += 1
    return renamed


def _reset_bind_pose(cmds, result: RetargetResult) -> None:
    """Re-record the bind pose at the new rest pose (best-effort).

    The skinCluster's dagPose still holds the *old* rig's pose after the joints move, so
    a later 'go to bind pose' would snap the skeleton back onto the rig the garment no
    longer targets. ``dagPose -reset -bindPose`` re-records it here.
    """
    joints = list(scene_cloth_joints().values())
    if not joints:
        return
    try:
        cmds.dagPose(joints, reset=True, bindPose=True)
    except Exception as exc:  # noqa: BLE001 - no bindPose node is fine, just say so
        result.warnings.append(
            f"could not reset the bind pose ({exc}) - use Skin > Go to Bind Pose with "
            "care on this asset.")
