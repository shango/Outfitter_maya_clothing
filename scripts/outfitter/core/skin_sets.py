"""Per-asset-type recommended skin-joint sets - the data behind "which joints do I bind to?".

Pure: no Maya, no I/O. A rig's ``cloth_*`` skeleton is a full body export (89 joints on
GenHuman), most of which no garment ever skins to: ~40 are finger joints, plus the
``cloth_ik_*`` helpers, ``cloth_interaction`` and ``cloth_center_of_mass``. Worse, the
``*_twist_*`` joints *look* like skippable sub-joints but actually drive limb silhouette -
exactly the ones a rigger unfamiliar with the skeleton tends to miss. This module decides,
per garment type, which joints a rigger should bind to.

The Maya-side :mod:`core.maya_skeleton` consumes the result to build a ``cloth_skin_SET``
selection set and colour those joints in the outliner, so the rigger selects the set and
binds instead of guessing. We never *rename* joints to mark them: attach connects
body→``cloth_`` by matching name, so a rename silently breaks attach. The recommendation is
a selection set + colour only; the rigger stays free to add or drop joints by hand.

Two halves, because the tool is rig-agnostic:

* :func:`derive_skin_sets` classifies an *arbitrary* rig's joint names into body roles
  (spine, clavicle, upperarm twist, calf, …) and composes them per garment type. It runs
  once, when a rig is registered, and the resolved names are stored in that rig's profile
  (:mod:`core.rigs`) - so the runtime reads data, never re-guesses.
* :data:`_RECOMMENDED` is the original hand-authored GenHuman table. It seeded the bundled
  GenHuman profile and now serves as the golden reference the heuristic is tested against:
  :func:`derive_skin_sets` over GenHuman's joint names must reproduce it exactly.

:func:`plan_skin_set` resolves a stored recommendation against the joints actually in the
scene, so a partially-pruned skeleton degrades gracefully instead of erroring.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

from .. import config


# --- region builders (keep both sides in lockstep, avoid copy-paste typos) ----
def _arm(side: str) -> tuple[str, ...]:
    """Clavicle → hand for one side, *including* the upper/lower-arm twist joints."""
    return (
        f"cloth_clavicle_{side}",
        f"cloth_upperarm_{side}",
        f"cloth_upperarm_twist_01_{side}",
        f"cloth_upperarm_twist_02_{side}",
        f"cloth_lowerarm_{side}",
        f"cloth_lowerarm_twist_01_{side}",
        f"cloth_lowerarm_twist_02_{side}",
        f"cloth_hand_{side}",
    )


def _leg(side: str) -> tuple[str, ...]:
    """Thigh → calf for one side, *including* the thigh/calf twist joints."""
    return (
        f"cloth_thigh_{side}",
        f"cloth_thigh_twist_01_{side}",
        f"cloth_thigh_twist_02_{side}",
        f"cloth_calf_{side}",
        f"cloth_calf_twist_01_{side}",
        f"cloth_calf_twist_02_{side}",
    )


def _foot(side: str) -> tuple[str, ...]:
    # GenHuman's foot is upper-cased in the export (cloth_GM_foot_R); ball is lower-case.
    return (f"cloth_GM_foot_{side.upper()}", f"cloth_ball_{side}")


def _shoe(side: str) -> tuple[str, ...]:
    return (f"cloth_calf_{side}", f"cloth_calf_twist_01_{side}") + _foot(side)


def _both(builder) -> tuple[str, ...]:
    return builder("l") + builder("r")


_SPINE = ("cloth_pelvis", "cloth_spine_01", "cloth_spine_02",
          "cloth_spine_03", "cloth_spine_04", "cloth_spine_05")
_NECK = ("cloth_neck_01", "cloth_neck_02")
_HEAD = ("cloth_head",)


# Ordered recommended skin joints per asset type, for GenHuman specifically. Twist joints
# are in on purpose - they are the silhouette sub-joints riggers miss. Anything absent here
# (fingers, cloth_ik_*, cloth_interaction, cloth_center_of_mass) is intentionally excluded:
# garments don't skin to it. Keep keys aligned with config.ASSET_TYPES.
#
# This table is no longer read at runtime - the bundled GenHuman profile carries these exact
# names, and every other rig gets its own set from derive_skin_sets(). It is kept as the
# reference the heuristic is measured against: if derive_skin_sets stops reproducing this
# table over GenHuman's joints, the heuristic has regressed.
_RECOMMENDED: dict[str, tuple[str, ...]] = {
    "shirt": _SPINE + _NECK + _both(_arm),
    "coat": _SPINE + _NECK + _both(_arm) + _both(_leg),
    "dress": _SPINE + _NECK + _both(_arm) + _both(_leg),
    "pants": ("cloth_pelvis", "cloth_spine_01") + _both(_leg) + _both(_foot),
    "shoes": _both(_shoe),
    "hat": _HEAD,
}

# Enforce the "keep keys aligned" note above: a new config.ASSET_TYPES entry without a
# recommendation here (or vice versa) is a developer error, caught at import in dev/CI.
assert set(_RECOMMENDED) == set(config.ASSET_TYPES), (
    f"skin_sets._RECOMMENDED {sorted(_RECOMMENDED)} != "
    f"config.ASSET_TYPES {sorted(config.ASSET_TYPES)}"
)


# --------------------------------------------------------------------------- #
# Deriving a recommendation for a rig we've never seen (registration time)
# --------------------------------------------------------------------------- #
# The composition above is really a statement about *body roles* - "a shirt binds the
# spine, the neck and both arms including their twists" - which holds for any humanoid
# rig. Only the joint *names* are rig-specific. So the heuristic splits the two: classify
# each joint into a role by name pattern, then compose roles per garment type exactly the
# way _RECOMMENDED does. That is what lets a newly registered rig get a sensible skin set
# with no hand-authoring, and why the composition below mirrors the tables above.

# Joints no garment ever binds to. Tested first, so an ``ik_hand_l`` never reads as a hand
# and a ``ring_02_l`` never reads as anything at all. Anchored with (^|_)…(_|$) so a rig
# whose joints merely *contain* one of these words is not caught by accident.
_EXCLUDE_PATTERNS: tuple[str, ...] = (
    r"(^|_)root$",
    r"(^|_)ik(_|$)",
    r"(^|_)interaction(_|$)",
    r"(^|_)center_of_mass(_|$)",
    r"(^|_)metacarpal(_|$)",
    r"(^|_)(index|middle|ring|pinky|thumb|finger)(_|$)",
)

# body role -> name patterns, in priority order (first match wins). A twist pattern must
# precede its parent limb pattern or every twist joint would classify as the limb itself.
# Alternatives beyond GenHuman's own vocabulary (shoulder, forearm, upleg, shin, ankle,
# toe, hips) cover the naming other common humanoid rigs use.
_ROLE_PATTERNS: tuple[tuple[str, str], ...] = (
    ("pelvis", r"(^|_)(pelvis|hips|hip)(_|$)"),
    ("spine", r"(^|_)(spine|torso)"),
    ("neck", r"(^|_)neck"),
    ("head", r"(^|_)head(_|$)"),
    ("clavicle", r"(^|_)(clavicle|collar|shoulder)"),
    ("upperarm_twist", r"(^|_)(upperarm|upper_arm|upperArm|humerus).*twist"),
    ("upperarm", r"(^|_)(upperarm|upper_arm|upperArm|humerus)"),
    ("lowerarm_twist", r"(^|_)(lowerarm|lower_arm|lowerArm|forearm|ulna).*twist"),
    ("lowerarm", r"(^|_)(lowerarm|lower_arm|lowerArm|forearm|ulna)"),
    ("hand", r"(^|_)(hand|wrist)(_|$)"),
    ("thigh_twist", r"(^|_)(thigh|upleg|upperleg|upper_leg|femur).*twist"),
    ("thigh", r"(^|_)(thigh|upleg|upperleg|upper_leg|femur)"),
    ("calf_twist", r"(^|_)(calf|shin|lowerleg|lower_leg|knee|tibia).*twist"),
    ("calf", r"(^|_)(calf|shin|lowerleg|lower_leg|knee|tibia)"),
    ("foot", r"(^|_)(foot|ankle)(_|$)"),
    ("ball", r"(^|_)(ball|toe|toebase)(_|$)"),
)

_EXCLUDE_RE = tuple(re.compile(p, re.IGNORECASE) for p in _EXCLUDE_PATTERNS)
_ROLE_RE = tuple((role, re.compile(p, re.IGNORECASE)) for role, p in _ROLE_PATTERNS)

# Trailing/leading side token, and a numeric segment index (spine_01, twist_02).
_SIDE_SUFFIX_RE = re.compile(r"_(l|r|lf|rt|left|right)$", re.IGNORECASE)
_SIDE_PREFIX_RE = re.compile(r"^(l|r|lf|rt|left|right)_", re.IGNORECASE)
_INDEX_RE = re.compile(r"_(\d+)(?:_|$)")

# Side emission order within a limb block: left limb whole, then right limb whole (which is
# what _both() does above). Any other side token sorts after, and unsided joints last.
_SIDE_ORDER = {"l": 0, "r": 1, "": 99}


@dataclass(frozen=True)
class _Joint:
    """One classified joint: what body role it plays, which side, and its segment index."""

    name: str
    role: str
    side: str
    index: int


def _side_of(body_name: str) -> tuple[str, str]:
    """Split a side token off a joint name -> ``(stem, side)``; side is ``""`` if unsided.

    Normalizes ``left``/``lf`` to ``l`` and ``right``/``rt`` to ``r`` so mixed conventions
    still pair up into two limbs.
    """
    match = _SIDE_SUFFIX_RE.search(body_name) or _SIDE_PREFIX_RE.match(body_name)
    if match is None:
        return body_name, ""
    token = match.group(1).lower()
    side = "l" if token in ("l", "lf", "left") else "r"
    return (body_name[:match.start()] + body_name[match.end():]).strip("_"), side


def classify_joint(name: str, cloth_prefix: str = config.CLOTH_PREFIX) -> _Joint | None:
    """Classify one ``cloth_*`` joint into a body role, or ``None`` if no garment binds it.

    ``None`` covers both the explicitly excluded joints (fingers, IK helpers, the root) and
    anything whose name matches no known role - a rig-specific helper the heuristic has no
    opinion about. Either way it is left out of the recommendation rather than guessed at.
    """
    body = name[len(cloth_prefix):] if name.startswith(cloth_prefix) else name
    if any(rx.search(body) for rx in _EXCLUDE_RE):
        return None
    stem, side = _side_of(body)
    for role, rx in _ROLE_RE:
        if rx.search(stem):
            index_match = _INDEX_RE.search(stem + "_")
            index = int(index_match.group(1)) if index_match else 0
            return _Joint(name=name, role=role, side=side, index=index)
    return None


# One block of a garment's recommendation: the body roles it covers, and whether they are
# emitted per limb (left limb entirely, then right) or once. ``limit`` caps how many
# segments of a role to take - shoes want only the first calf twist, pants only the first
# spine joint, matching the hand-authored tables above.
@dataclass(frozen=True)
class _Block:
    roles: tuple[tuple[str, int | None], ...]
    sided: bool = False


def _unsided(*roles: str) -> _Block:
    return _Block(tuple((r, None) for r in roles))


def _sided(*roles) -> _Block:
    return _Block(
        tuple(r if isinstance(r, tuple) else (r, None) for r in roles), sided=True)


_ARM = _sided("clavicle", "upperarm", "upperarm_twist", "lowerarm", "lowerarm_twist", "hand")
_LEG = _sided("thigh", "thigh_twist", "calf", "calf_twist")
_FOOT = _sided("foot", "ball")
# A shoe reaches up the calf far enough to hold the shaft, but only the first calf twist.
_SHOE = _sided("calf", ("calf_twist", 1), "foot", "ball")

_COMPOSITION: dict[str, tuple[_Block, ...]] = {
    "shirt": (_unsided("pelvis", "spine", "neck"), _ARM),
    "coat": (_unsided("pelvis", "spine", "neck"), _ARM, _LEG),
    "dress": (_unsided("pelvis", "spine", "neck"), _ARM, _LEG),
    "pants": (_Block((("pelvis", None), ("spine", 1))), _LEG, _FOOT),
    "shoes": (_SHOE,),
    "hat": (_unsided("head"),),
}

assert set(_COMPOSITION) == set(config.ASSET_TYPES), (
    f"skin_sets._COMPOSITION {sorted(_COMPOSITION)} != "
    f"config.ASSET_TYPES {sorted(config.ASSET_TYPES)}"
)


def _emit(joints: list[_Joint], roles, sides) -> list[str]:
    """Emit joint names for ``roles`` across ``sides``, in segment order within each role."""
    out: list[str] = []
    for side in sides:
        for role, limit in roles:
            picked = sorted(
                (j for j in joints if j.role == role and j.side == side),
                key=lambda j: (j.index, j.name))
            out.extend(j.name for j in (picked if limit is None else picked[:limit]))
    return out


def derive_skin_sets(joint_names, cloth_prefix: str = config.CLOTH_PREFIX
                     ) -> dict[str, tuple[str, ...]]:
    """Recommend skin joints per garment type for a rig the tool has never seen.

    Classifies every name into a body role (:func:`classify_joint`) and composes the roles
    per type, in the same proximal-to-distal, left-limb-then-right order the hand-authored
    GenHuman table uses. Run once at registration; the result is stored in the rig's
    profile, where a rigger can correct it by hand.

    Types that come out empty (a rig with no legs recommends nothing for pants) are omitted
    rather than stored as empty entries. Unrecognised joints are simply left out - the
    heuristic never guesses a role it cannot name.
    """
    classified = [j for j in (classify_joint(n, cloth_prefix) for n in joint_names) if j]

    derived: dict[str, tuple[str, ...]] = {}
    for asset_type, blocks in _COMPOSITION.items():
        names: list[str] = []
        for block in blocks:
            if block.sided:
                present = {j.side for j in classified
                           if any(j.role == r for r, _ in block.roles)}
                sides = sorted(present, key=lambda s: (_SIDE_ORDER.get(s, 50), s))
            else:
                sides = sorted({j.side for j in classified},
                               key=lambda s: (_SIDE_ORDER.get(s, 50), s))
            names.extend(_emit(classified, block.roles, sides))
        # de-dupe defensively: an unsided block over a rig with sided spine joints would
        # otherwise be able to emit the same joint under two side passes.
        seen: list[str] = []
        for n in names:
            if n not in seen:
                seen.append(n)
        if seen:
            derived[asset_type] = tuple(seen)
    return derived


@dataclass(frozen=True)
class SkinSetPlan:
    """The resolved recommendation: which recommended joints exist, which don't."""

    asset_type: str
    set_name: str
    include: tuple[str, ...]   # recommended joints present in the scene (canonical order)
    missing: tuple[str, ...]   # recommended joints absent (skeleton pruned / revised)

    @property
    def is_empty(self) -> bool:
        return not self.include

    def summary(self) -> str:
        n = len(self.include)
        msg = (f"{self.set_name}: {n} recommended skin joint"
               f"{'' if n == 1 else 's'} for a {self.asset_type}")
        if self.missing:
            k = len(self.missing)
            msg += f" ({k} recommended joint{'' if k == 1 else 's'} not in the scene)"
        return msg + "."


def asset_types() -> tuple[str, ...]:
    """Asset types that have a recommended skin set (sorted, for messages)."""
    return tuple(sorted(_RECOMMENDED))


def genhuman_seed_joints(asset_type: str) -> tuple[str, ...]:
    """The hand-authored GenHuman skin set for ``asset_type``.

    Not the runtime lookup - a rig's recommendation lives in its profile. This is the
    original table, kept as the seed the bundled GenHuman profile was generated from and
    the reference :func:`derive_skin_sets` is tested against.
    """
    try:
        return _RECOMMENDED[asset_type]
    except KeyError:
        raise ValueError(
            f"no recommended skin set for asset type {asset_type!r}; "
            f"known: {', '.join(asset_types())}") from None


def plan_skin_set(asset_type: str, present_joints, recommended,
                  set_name: str | None = None) -> SkinSetPlan:
    """Resolve a rig's stored recommendation against the joints actually in the scene.

    ``recommended`` is the joint list from the rig's profile (``profile.skin_set(type)``);
    ``present_joints`` is any iterable of the ``cloth_*`` joint short names currently in the
    scene. Returns a :class:`SkinSetPlan` listing the recommended joints that exist (to put
    in the set, in canonical order) and those that don't (informational - the skeleton was
    pruned, or the rig profile is a revision ahead of this scene). Pure: the Maya side
    passes in the scene joints and replays the result.
    """
    present = set(present_joints)
    rec = tuple(recommended)
    include = tuple(j for j in rec if j in present)
    missing = tuple(j for j in rec if j not in present)
    return SkinSetPlan(
        asset_type=asset_type, set_name=set_name or config.SKIN_SET,
        include=include, missing=missing)
