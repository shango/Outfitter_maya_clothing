"""Tests for the pure recommended-skin-joint sets (core.skin_sets)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from snap_on_clothing import config
from snap_on_clothing.core import skin_sets


def _canonical_joint_names() -> set[str]:
    data = json.loads(
        (Path(__file__).resolve().parents[1]
         / "scripts/snap_on_clothing/data/cloth_skeleton.json").read_text())
    return {j["name"] for j in data["joints"]}


def test_every_asset_type_has_a_set():
    for t in config.ASSET_TYPES:
        assert skin_sets.recommended_joints(t)  # non-empty


def test_unknown_type_raises():
    with pytest.raises(ValueError):
        skin_sets.recommended_joints("cape")


def test_recommended_names_all_exist_in_canonical_skeleton():
    """Guards against a typo'd joint name that would never resolve in Maya."""
    canonical = _canonical_joint_names()
    for t in config.ASSET_TYPES:
        for name in skin_sets.recommended_joints(t):
            assert name in canonical, f"{t}: {name!r} not a real cloth_* joint"


def test_twist_joints_are_included_for_garments_with_limbs():
    """The silhouette sub-joints the rigger flagged must be in the set, not dropped."""
    shirt = skin_sets.recommended_joints("shirt")
    assert "cloth_upperarm_twist_01_l" in shirt
    assert "cloth_lowerarm_twist_02_r" in shirt
    coat = skin_sets.recommended_joints("coat")
    assert "cloth_thigh_twist_01_l" in coat
    assert "cloth_calf_twist_02_r" in coat


def test_fingers_and_ik_helpers_excluded():
    for t in config.ASSET_TYPES:
        for name in skin_sets.recommended_joints(t):
            assert "metacarpal" not in name
            assert "_ik_" not in name
            assert name not in ("cloth_interaction", "cloth_center_of_mass")
    # explicitly: no finger segment joints leaked into any set
    flat = {n for t in config.ASSET_TYPES for n in skin_sets.recommended_joints(t)}
    for finger in ("index", "middle", "ring", "pinky", "thumb"):
        assert not any(finger in n for n in flat)


def test_foot_uppercase_handled():
    """GenHuman exports cloth_GM_foot_R/L upper-cased; pants/shoes must match exactly."""
    pants = skin_sets.recommended_joints("pants")
    assert "cloth_GM_foot_R" in pants and "cloth_GM_foot_L" in pants
    assert "cloth_ball_r" in pants


def test_hat_is_head_only():
    assert skin_sets.recommended_joints("hat") == ("cloth_head",)


def test_plan_intersects_with_present_and_preserves_order():
    present = {"cloth_pelvis", "cloth_spine_01", "cloth_neck_01", "cloth_head"}
    plan = skin_sets.plan_skin_set("shirt", present)
    # included joints appear in canonical (recommended) order, present-only
    assert plan.include == ("cloth_pelvis", "cloth_spine_01", "cloth_neck_01")
    assert "cloth_head" not in plan.include  # present but not recommended for a shirt
    assert "cloth_spine_05" in plan.missing  # recommended but absent
    assert not plan.is_empty


def test_plan_empty_when_no_recommended_joints_present():
    plan = skin_sets.plan_skin_set("hat", {"cloth_pelvis", "cloth_spine_01"})
    assert plan.is_empty
    assert plan.missing == ("cloth_head",)


def test_plan_default_set_name_from_config():
    plan = skin_sets.plan_skin_set("hat", {"cloth_head"})
    assert plan.set_name == config.SKIN_SET
    assert "cloth_skin_SET" in plan.summary()


def test_full_skeleton_includes_all_recommended():
    """With the real skeleton present, nothing recommended is reported missing."""
    present = _canonical_joint_names()
    for t in config.ASSET_TYPES:
        plan = skin_sets.plan_skin_set(t, present)
        assert plan.missing == ()
        assert plan.include == skin_sets.recommended_joints(t)
