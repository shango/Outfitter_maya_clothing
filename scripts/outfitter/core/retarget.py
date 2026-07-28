"""Retarget a garment from one rig to another - the decision half (pure, headless).

A garment is skinned to one rig's skeleton: its ``cloth_*`` joints carry that rig's joint
names and sit at that rig's rest pose. Attach matches by *exact name*, so the same asset
cannot be attached to a different rig - and if two rigs happen to share joint names, it
would attach and then deform into nonsense, which is worse.

Converting one is a real operation with a real limit:

  * **What it does** - work out which of the destination rig's joints each of the garment's
    joints corresponds to, rename them, and move them onto the destination rig's rest pose
    *without deforming the mesh* (the Maya half uses ``skinCluster -e -moveJointsMode``,
    which rewrites bindPreMatrix rather than pushing the geometry around). Skin weights
    survive.
  * **What it does not do** - change the garment's *shape*. If the two rigs have different
    proportions, the mesh will intersect or float and needs a manual refit, and probably a
    weight touch-up. Never describe a retarget as finished conversion.

This module decides the mapping and reports exactly what it couldn't map;
:mod:`core.maya_retarget` applies it in a live scene.

Joint matching, in order (each named in the plan so the user can see how a joint was
matched, not just that it was):

  1. **exact name** - the two rigs use the same joint name. The common case between rig
     generations.
  2. **alias** - the destination rig's profile declares ``jointAliases`` mapping a foreign
     joint name onto one of its own. Hand-authored, always wins over the heuristic.
  3. **role** - both names classify to the same body role, side and segment index via
     :func:`core.skin_sets.classify_joint` (``cloth_GM_foot_R`` -> ``cloth_foot_r``). The
     same vocabulary that derives skin sets, reused: if it can name the role, it can pair
     it up.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Iterable

from .. import config
from . import skin_sets as _skin_sets

if TYPE_CHECKING:  # import for typing only - core.rigs is data, not a runtime dependency
    from .rigs import RigProfile
    from .skeleton import JointSpec

MATCH_NAME: str = "name"
MATCH_ALIAS: str = "alias"
MATCH_ROLE: str = "role"


@dataclass(frozen=True)
class JointMatch:
    """One garment joint paired with the destination rig's joint it becomes."""

    source: str  # the joint as it exists in the asset now
    target: str  # what it must be called (and where it must sit) on the destination rig
    how: str     # MATCH_NAME | MATCH_ALIAS | MATCH_ROLE

    @property
    def renamed(self) -> bool:
        return self.source != self.target


@dataclass(frozen=True)
class RetargetPlan:
    """The decided mapping from a garment's joints onto a destination rig's."""

    target_rig: str
    matches: tuple[JointMatch, ...] = ()
    unmatched: tuple[str, ...] = ()   # garment joints with no counterpart on the target
    source_rig: str = ""

    @property
    def renames(self) -> tuple[JointMatch, ...]:
        return tuple(m for m in self.matches if m.renamed)

    @property
    def ok(self) -> bool:
        """True when at least one joint maps - below that there is nothing to retarget."""
        return bool(self.matches)

    def target_map(self) -> dict[str, str]:
        """``{destination joint name: the garment joint that becomes it}``."""
        return {m.target: m.source for m in self.matches}

    def ordered_moves(self, target: "RigProfile") -> list[tuple[str, "JointSpec"]]:
        """``(garment joint, destination rest transform)`` in parent-before-child order.

        Hierarchy order matters: the stored transforms are *local*, so a joint only lands
        at the destination rest pose if its parent was moved there first.
        """
        by_source = self.target_map()
        moves: list[tuple[str, "JointSpec"]] = []
        for spec in target.skeleton.joints:
            source = by_source.get(spec.name)
            if source is not None:
                moves.append((source, spec))
        return moves

    def summary(self) -> str:
        n = len(self.matches)
        msg = (f"Retarget to {self.target_rig}: {n} joint"
               f"{'' if n == 1 else 's'} mapped ({len(self.renames)} renamed)")
        if self.unmatched:
            msg += f", {len(self.unmatched)} not mapped"
        return msg + "."


def _role_key(name: str, cloth_prefix: str) -> tuple[str, str, int] | None:
    joint = _skin_sets.classify_joint(name, cloth_prefix)
    return None if joint is None else (joint.role, joint.side, joint.index)


def plan_retarget(
    asset_joints: Iterable[str],
    target: "RigProfile",
    source: "RigProfile | None" = None,
    cloth_prefix: str = config.CLOTH_PREFIX,
) -> RetargetPlan:
    """Map a garment's ``cloth_*`` joints onto ``target``'s, without touching a scene.

    ``asset_joints`` is the garment's joint names as they are now (short names, including
    the ``cloth_`` prefix). ``source`` is only used to label the plan.

    Joints that don't map are reported rather than guessed at: they keep their names and
    will simply not be driven by the destination rig. That is the honest outcome - a
    garment part weighted to such a joint won't follow the body, and the user needs to
    know which ones before they decide the conversion was worth it.
    """
    target_names = set(target.joint_names)
    aliases = {str(k): str(v) for k, v in target.joint_aliases.items()}

    # Role signature -> destination joint. First one wins: a rig with two joints of the
    # same role, side and index is ambiguous by definition, and picking either is a guess
    # we'd rather make deterministically than randomly.
    by_role: dict[tuple[str, str, int], str] = {}
    for name in target.joint_names:
        key = _role_key(name, cloth_prefix)
        if key is not None and key not in by_role:
            by_role[key] = name

    joints = list(asset_joints)
    assigned: dict[str, JointMatch] = {}
    claimed: set[str] = set()  # destination joints already spoken for

    def claim(joint: str, target_name: str, how: str) -> None:
        # Two garment joints must never collapse onto one destination joint - that would
        # rename them to the same thing and lose one.
        if target_name in claimed:
            return
        claimed.add(target_name)
        assigned[joint] = JointMatch(joint, target_name, how)

    # Pass 1: the certain matches. Doing these first means a heuristic role match can
    # never steal a joint that some other garment joint names outright, whatever order
    # the joints arrive in.
    for joint in joints:
        if joint in target_names:
            claim(joint, joint, MATCH_NAME)
        elif joint in aliases and aliases[joint] in target_names:
            claim(joint, aliases[joint], MATCH_ALIAS)

    # Pass 2: the guesses, over what's left.
    for joint in joints:
        if joint in assigned:
            continue
        key = _role_key(joint, cloth_prefix)
        candidate = by_role.get(key) if key is not None else None
        if candidate is not None:
            claim(joint, candidate, MATCH_ROLE)

    return RetargetPlan(
        target_rig=target.rig_id,
        matches=tuple(assigned[j] for j in joints if j in assigned),
        unmatched=tuple(j for j in joints if j not in assigned),
        source_rig=source.rig_id if source is not None else "",
    )
