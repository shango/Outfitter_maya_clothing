"""Per-asset-type recommended skin-joint sets - the data behind "which joints do I bind to?".

Pure: no Maya, no I/O. The full ``cloth_*`` skeleton is a body export of ~89 joints, most
of which no garment ever skins to: ~40 are finger joints, plus the ``cloth_ik_*`` helpers,
``cloth_interaction`` and ``cloth_center_of_mass``. Worse, the ``*_twist_*`` joints *look*
like skippable sub-joints but actually drive limb silhouette - exactly the ones a rigger
unfamiliar with the skeleton tends to miss. This module names, per garment type, the joints
a rigger should bind to.

The Maya-side :mod:`core.maya_skeleton` consumes it to build a ``cloth_skin_SET`` selection
set and colour those joints in the outliner, so the rigger selects the set and binds instead
of guessing. We never *rename* joints to mark them: attach connects body→``cloth_`` by
matching name, so a rename silently breaks attach. The recommendation is a selection set +
colour only; the rigger stays free to add or drop joints by hand.

Names are the canonical short names from ``data/cloth_skeleton.json``. The resolver
intersects them with whatever joints are actually in the scene, so a partially-pruned
skeleton (or a future skeleton revision) degrades gracefully instead of erroring.
"""
from __future__ import annotations

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


# Ordered recommended skin joints per asset type. Twist joints are in on purpose - they are
# the silhouette sub-joints riggers miss. Anything absent here (fingers, cloth_ik_*,
# cloth_interaction, cloth_center_of_mass) is intentionally excluded: garments don't skin to
# it. Keep keys aligned with config.ASSET_TYPES.
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


def recommended_joints(asset_type: str) -> tuple[str, ...]:
    """Canonical recommended skin-joint names for ``asset_type`` (some may not exist)."""
    try:
        return _RECOMMENDED[asset_type]
    except KeyError:
        raise ValueError(
            f"no recommended skin set for asset type {asset_type!r}; "
            f"known: {', '.join(asset_types())}") from None


def plan_skin_set(asset_type: str, present_joints, set_name: str | None = None) -> SkinSetPlan:
    """Resolve the recommendation against the joints actually in the scene.

    ``present_joints`` is any iterable of the ``cloth_*`` joint short names currently in the
    scene. Returns a :class:`SkinSetPlan` listing the recommended joints that exist (to put
    in the set, in canonical order) and those that don't (informational - the skeleton was
    pruned or revised). Pure: the Maya side passes in the scene joints and replays the result.
    """
    present = set(present_joints)
    rec = recommended_joints(asset_type)
    include = tuple(j for j in rec if j in present)
    missing = tuple(j for j in rec if j not in present)
    return SkinSetPlan(
        asset_type=asset_type, set_name=set_name or config.SKIN_SET,
        include=include, missing=missing)
