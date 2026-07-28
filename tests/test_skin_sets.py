"""Tests for the pure recommended-skin-joint logic (core.skin_sets).

Two subjects:

* :func:`derive_skin_sets` - the heuristic that gives a *newly registered* rig a skin set
  with no hand-authoring. Its correctness bar is exact: run over GenHuman's joint names it
  must reproduce the hand-authored table joint-for-joint, in order.
* :func:`plan_skin_set` - resolving a rig's stored recommendation against the joints
  actually in a scene.
"""
from __future__ import annotations

import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from outfitter import config
from outfitter.core import rigs, skin_sets


@pytest.fixture(scope="module")
def genhuman():
    # roots=[] pins the lookup to the bundled profile.
    return rigs.load_profile("genhuman", roots=[])


@pytest.fixture(scope="module")
def canonical_names(genhuman):
    return set(genhuman.skeleton.names)


# --- the GenHuman seed table --------------------------------------------------
def test_every_asset_type_has_a_seed_set():
    for t in config.ASSET_TYPES:
        assert skin_sets.genhuman_seed_joints(t)  # non-empty


def test_unknown_type_raises():
    with pytest.raises(ValueError):
        skin_sets.genhuman_seed_joints("cape")


def test_seed_names_all_exist_in_the_genhuman_skeleton(canonical_names):
    """Guards against a typo'd joint name that would never resolve in Maya."""
    for t in config.ASSET_TYPES:
        for name in skin_sets.genhuman_seed_joints(t):
            assert name in canonical_names, f"{t}: {name!r} not a real cloth_* joint"


def test_twist_joints_are_included_for_garments_with_limbs():
    """The silhouette sub-joints the rigger flagged must be in the set, not dropped."""
    shirt = skin_sets.genhuman_seed_joints("shirt")
    assert "cloth_upperarm_twist_01_l" in shirt
    assert "cloth_lowerarm_twist_02_r" in shirt
    coat = skin_sets.genhuman_seed_joints("coat")
    assert "cloth_thigh_twist_01_l" in coat
    assert "cloth_calf_twist_02_r" in coat


def test_fingers_and_ik_helpers_excluded():
    for t in config.ASSET_TYPES:
        for name in skin_sets.genhuman_seed_joints(t):
            assert "metacarpal" not in name
            assert "_ik_" not in name
            assert name not in ("cloth_interaction", "cloth_center_of_mass")
    # explicitly: no finger segment joints leaked into any set
    flat = {n for t in config.ASSET_TYPES for n in skin_sets.genhuman_seed_joints(t)}
    for finger in ("index", "middle", "ring", "pinky", "thumb"):
        assert not any(finger in n for n in flat)


def test_foot_uppercase_handled():
    """GenHuman exports cloth_GM_foot_R/L upper-cased; pants/shoes must match exactly."""
    pants = skin_sets.genhuman_seed_joints("pants")
    assert "cloth_GM_foot_R" in pants and "cloth_GM_foot_L" in pants
    assert "cloth_ball_r" in pants


def test_hat_is_head_only():
    assert skin_sets.genhuman_seed_joints("hat") == ("cloth_head",)


# --- the heuristic, measured against the seed table ---------------------------
def test_derive_reproduces_the_hand_authored_genhuman_table(genhuman):
    """The heuristic's correctness bar. Every type, every joint, in order.

    If this fails, derive_skin_sets has regressed and every newly registered rig would get
    a worse recommendation than GenHuman's - fix the heuristic, don't relax the test.
    """
    derived = skin_sets.derive_skin_sets(genhuman.skeleton.names)
    for t in config.ASSET_TYPES:
        assert derived.get(t, ()) == skin_sets.genhuman_seed_joints(t), t


def test_derive_handles_a_differently_named_rig():
    """A rig using the other common humanoid vocabulary must still classify correctly."""
    names = [
        "cloth_hips", "cloth_spine_01", "cloth_spine_02", "cloth_neck_01", "cloth_head",
        "cloth_shoulder_l", "cloth_upperArm_l", "cloth_forearm_l", "cloth_hand_l",
        "cloth_shoulder_r", "cloth_upperArm_r", "cloth_forearm_r", "cloth_hand_r",
        "cloth_upLeg_l", "cloth_shin_l", "cloth_ankle_l", "cloth_toeBase_l",
        "cloth_upLeg_r", "cloth_shin_r", "cloth_ankle_r", "cloth_toeBase_r",
    ]
    derived = skin_sets.derive_skin_sets(names)
    assert derived["hat"] == ("cloth_head",)
    assert derived["shirt"] == (
        "cloth_hips", "cloth_spine_01", "cloth_spine_02", "cloth_neck_01",
        "cloth_shoulder_l", "cloth_upperArm_l", "cloth_forearm_l", "cloth_hand_l",
        "cloth_shoulder_r", "cloth_upperArm_r", "cloth_forearm_r", "cloth_hand_r",
    )
    assert derived["shoes"] == (
        "cloth_shin_l", "cloth_ankle_l", "cloth_toeBase_l",
        "cloth_shin_r", "cloth_ankle_r", "cloth_toeBase_r",
    )
    # pants takes the pelvis + only the first spine joint, then legs, then feet
    assert derived["pants"][:2] == ("cloth_hips", "cloth_spine_01")


def test_derive_normalizes_left_right_spellings():
    names = ["cloth_head", "cloth_hand_left", "cloth_hand_right",
             "cloth_upperarm_left", "cloth_upperarm_right"]
    derived = skin_sets.derive_skin_sets(names)
    # left limb entirely, then right - the same order _both() produces
    assert derived["shirt"] == ("cloth_upperarm_left", "cloth_hand_left",
                                "cloth_upperarm_right", "cloth_hand_right")


def test_derive_omits_types_with_nothing_to_bind():
    """A head-and-neck-only rig recommends nothing for pants rather than an empty entry."""
    derived = skin_sets.derive_skin_sets(["cloth_head", "cloth_neck_01"])
    assert derived["hat"] == ("cloth_head",)
    assert "pants" not in derived
    assert "shoes" not in derived


def test_derive_excludes_fingers_ik_and_the_root():
    names = ["cloth_root", "cloth_hand_l", "cloth_index_01_l", "cloth_thumb_02_l",
             "cloth_ring_metacarpal_l", "cloth_ik_hand_l", "cloth_ik_foot_root",
             "cloth_interaction", "cloth_center_of_mass"]
    derived = skin_sets.derive_skin_sets(names)
    assert derived["shirt"] == ("cloth_hand_l",)


def test_derive_ignores_joints_it_cannot_name():
    """A rig-specific helper the heuristic has no opinion about is left out, not guessed."""
    derived = skin_sets.derive_skin_sets(
        ["cloth_head", "cloth_cape_flap_01", "cloth_jiggle_a"])
    assert derived["hat"] == ("cloth_head",)
    assert not any("cape" in n or "jiggle" in n
                   for joints in derived.values() for n in joints)


def test_derive_orders_segments_numerically_not_alphabetically():
    """Skeleton order is arbitrary - twist_02 sits before twist_01 in the real GenHuman
    data - so the recommendation must sort by segment number."""
    derived = skin_sets.derive_skin_sets([
        "cloth_upperarm_l", "cloth_upperarm_twist_02_l", "cloth_upperarm_twist_01_l"])
    assert derived["shirt"] == ("cloth_upperarm_l", "cloth_upperarm_twist_01_l",
                                "cloth_upperarm_twist_02_l")


def test_derive_puts_twists_with_their_limb_not_as_the_limb():
    """A twist pattern must win over its parent limb pattern, or every twist joint would
    classify as the limb itself and the ordering would collapse."""
    joint = skin_sets.classify_joint("cloth_lowerarm_twist_01_r")
    assert joint is not None and joint.role == "lowerarm_twist"
    assert joint.side == "r" and joint.index == 1


def test_classify_returns_none_for_excluded_joints():
    for name in ("cloth_root", "cloth_ik_hand_l", "cloth_index_03_l",
                 "cloth_interaction", "cloth_center_of_mass"):
        assert skin_sets.classify_joint(name) is None, name


# --- resolving a stored recommendation against a scene ------------------------
def test_plan_intersects_with_present_and_preserves_order():
    recommended = skin_sets.genhuman_seed_joints("shirt")
    present = {"cloth_pelvis", "cloth_spine_01", "cloth_neck_01", "cloth_head"}
    plan = skin_sets.plan_skin_set("shirt", present, recommended)
    # included joints appear in canonical (recommended) order, present-only
    assert plan.include == ("cloth_pelvis", "cloth_spine_01", "cloth_neck_01")
    assert "cloth_head" not in plan.include  # present but not recommended for a shirt
    assert "cloth_spine_05" in plan.missing  # recommended but absent
    assert not plan.is_empty


def test_plan_empty_when_no_recommended_joints_present():
    plan = skin_sets.plan_skin_set(
        "hat", {"cloth_pelvis", "cloth_spine_01"}, ("cloth_head",))
    assert plan.is_empty
    assert plan.missing == ("cloth_head",)


def test_plan_default_set_name_from_config():
    plan = skin_sets.plan_skin_set("hat", {"cloth_head"}, ("cloth_head",))
    assert plan.set_name == config.SKIN_SET
    assert "cloth_skin_SET" in plan.summary()


def test_plan_uses_the_recommendation_it_is_given_not_a_builtin_table():
    """The runtime reads the rig's profile - a rig whose hat set is head+neck gets that."""
    plan = skin_sets.plan_skin_set(
        "hat", {"cloth_head", "cloth_neck_01"}, ("cloth_head", "cloth_neck_01"))
    assert plan.include == ("cloth_head", "cloth_neck_01")
    assert plan.missing == ()


def test_full_skeleton_includes_all_recommended(genhuman, canonical_names):
    """With the real skeleton present, nothing recommended is reported missing."""
    for t in config.ASSET_TYPES:
        recommended = genhuman.skin_set(t)
        plan = skin_sets.plan_skin_set(t, canonical_names, recommended)
        assert plan.missing == ()
        assert plan.include == recommended


def test_skin_set_joints_are_gender_independent():
    """M12 Phase C: one shared cloth_skeleton serves both male and female, so the
    recommended skin-joint names must not depend on gender. skin_sets has no gender
    axis at all - this guards against a per-gender fork sneaking in (and documents the
    intent of the single shared skeleton)."""
    import inspect

    for fn in (skin_sets.genhuman_seed_joints, skin_sets.plan_skin_set,
               skin_sets.derive_skin_sets):
        params = inspect.signature(fn).parameters
        assert "gender" not in params, f"{fn.__name__} must stay gender-agnostic"
    # The names are a stable function of asset type alone.
    for t in config.ASSET_TYPES:
        assert skin_sets.genhuman_seed_joints(t) == skin_sets.genhuman_seed_joints(t)
