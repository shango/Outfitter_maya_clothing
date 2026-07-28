"""Headless tests for the retarget mapping (core.retarget).

Retargeting is the one operation that reaches across rigs, so the mapping is where it can
go quietly wrong: a joint mapped to the wrong counterpart moves geometry onto the wrong
body part, and a joint silently dropped leaves part of the garment unfollowed. Both must
be visible in the plan before anything touches a scene - the Maya half (core.maya_retarget)
only replays what is decided here.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from outfitter.core import retarget
from outfitter.core import rigs
from outfitter.core import skeleton as sk

BUNDLED_ONLY: list = []


@pytest.fixture(scope="module")
def genhuman():
    return rigs.load_profile("genhuman", roots=BUNDLED_ONLY)


def _skeleton(*names):
    joints = [sk.JointSpec(name="cloth_root", parent="Rig_GRP")]
    joints += [sk.JointSpec(name=n, parent="cloth_root") for n in names]
    return sk.SkeletonSpec(
        root_group="Rig_GRP", root_group_rotate=(-90.0, 0.0, 0.0),
        root_joint="cloth_root", joints=tuple(joints))


def _profile(*names, **overrides):
    base = dict(
        rig_id="acme_biped", display_name="Acme Biped", version="v01",
        export_group="Acme_Joint_GRP", skeleton=_skeleton(*names),
        markers=("Acme_Joint_GRP",),
    )
    base.update(overrides)
    return rigs.RigProfile(**base)


# --- exact-name matching ------------------------------------------------------
def test_retargeting_a_rig_onto_itself_maps_everything_and_renames_nothing(genhuman):
    plan = retarget.plan_retarget(genhuman.joint_names, genhuman, genhuman)

    assert len(plan.matches) == len(genhuman.joint_names)
    assert plan.unmatched == ()
    assert plan.renames == ()
    assert all(m.how == retarget.MATCH_NAME for m in plan.matches)


def test_shared_names_between_rig_generations_match_by_name():
    target = _profile("cloth_spine_01", "cloth_head")
    plan = retarget.plan_retarget(["cloth_root", "cloth_head"], target)

    assert {m.target for m in plan.matches} == {"cloth_root", "cloth_head"}
    assert plan.unmatched == ()


# --- role matching (the interesting half) -------------------------------------
def test_differently_named_joints_match_by_body_role():
    # GenHuman calls it cloth_GM_foot_R; another rig calls it cloth_foot_r. Same joint.
    target = _profile("cloth_foot_r", "cloth_upperarm_l")
    plan = retarget.plan_retarget(["cloth_GM_foot_R", "cloth_upperarm_L"], target)

    by_source = {m.source: m for m in plan.matches}
    assert by_source["cloth_GM_foot_R"].target == "cloth_foot_r"
    assert by_source["cloth_upperarm_L"].target == "cloth_upperarm_l"
    assert all(m.how == retarget.MATCH_ROLE for m in plan.matches)
    assert len(plan.renames) == 2


def test_role_matching_keeps_sides_apart():
    target = _profile("cloth_foot_l", "cloth_foot_r")
    plan = retarget.plan_retarget(["cloth_GM_foot_R"], target)

    assert [m.target for m in plan.matches] == ["cloth_foot_r"]


def test_role_matching_keeps_twist_segments_in_order():
    target = _profile("cloth_upperarm_twist_01_l", "cloth_upperarm_twist_02_l")
    plan = retarget.plan_retarget(
        ["cloth_upperarm_twist_02_L", "cloth_upperarm_twist_01_L"], target)

    by_source = {m.source: m.target for m in plan.matches}
    assert by_source["cloth_upperarm_twist_01_L"] == "cloth_upperarm_twist_01_l"
    assert by_source["cloth_upperarm_twist_02_L"] == "cloth_upperarm_twist_02_l"


# --- aliases ------------------------------------------------------------------
def test_a_declared_alias_beats_the_heuristic():
    # The rigger knows this rig's 'cloth_belly' is where the other rig's spine_02 goes.
    target = _profile("cloth_spine_01", "cloth_belly",
                      joint_aliases={"cloth_spine_02": "cloth_belly"})
    plan = retarget.plan_retarget(["cloth_spine_02"], target)

    assert plan.matches[0].target == "cloth_belly"
    assert plan.matches[0].how == retarget.MATCH_ALIAS


def test_an_alias_pointing_at_a_joint_the_rig_does_not_have_is_ignored():
    target = _profile("cloth_foot_r",
                      joint_aliases={"cloth_GM_foot_R": "cloth_nope"})
    plan = retarget.plan_retarget(["cloth_GM_foot_R"], target)

    # a stale alias falls through to role matching rather than dropping the joint
    assert plan.matches[0].target == "cloth_foot_r"
    assert plan.matches[0].how == retarget.MATCH_ROLE


def test_a_different_segment_index_is_not_treated_as_the_same_joint():
    # A garment weighted to spine_02 on a rig that has only spine_01 is a real mismatch.
    # Mapping it anyway would move that part of the garment to the wrong height, so it is
    # reported instead.
    target = _profile("cloth_spine_01")
    plan = retarget.plan_retarget(["cloth_spine_02"], target)

    assert plan.matches == ()
    assert plan.unmatched == ("cloth_spine_02",)


# --- what can't be mapped -----------------------------------------------------
def test_helper_joints_are_reported_not_guessed_at():
    target = _profile("cloth_spine_01")
    plan = retarget.plan_retarget(["cloth_spine_01", "cloth_hem_flare_A"], target)

    assert [m.source for m in plan.matches] == ["cloth_spine_01"]
    assert plan.unmatched == ("cloth_hem_flare_A",)
    assert "not mapped" in plan.summary()


def test_two_joints_never_collapse_onto_one_target():
    # Both of these want cloth_foot_r: one by exact name, one by role. Mapping both would
    # rename them to the same name and lose one, so only one can have it.
    target = _profile("cloth_foot_r")
    plan = retarget.plan_retarget(["cloth_GM_foot_R", "cloth_foot_r"], target)

    assert len(plan.matches) == 1
    assert plan.unmatched == ("cloth_GM_foot_R",)


def test_an_exact_name_match_wins_over_a_role_guess_whatever_the_order():
    # The role heuristic must never claim a joint that another garment joint names
    # outright - and which of them arrives first must not decide it.
    target = _profile("cloth_foot_r")
    for order in (["cloth_GM_foot_R", "cloth_foot_r"], ["cloth_foot_r", "cloth_GM_foot_R"]):
        plan = retarget.plan_retarget(order, target)
        assert [(m.source, m.how) for m in plan.matches] == [
            ("cloth_foot_r", retarget.MATCH_NAME)]


def test_a_plan_that_maps_nothing_is_not_ok():
    target = _profile("cloth_spine_01")
    plan = retarget.plan_retarget(["cloth_wibble", "cloth_wobble"], target)

    assert not plan.ok
    assert plan.matches == ()


# --- the move order the Maya half depends on ----------------------------------
def test_moves_come_back_in_parent_before_child_order(genhuman):
    plan = retarget.plan_retarget(genhuman.joint_names, genhuman)
    moves = plan.ordered_moves(genhuman)

    # Local transforms only land correctly if a joint's parent moved first.
    seen = {"Rig_GRP"}
    for _source, spec in moves:
        assert spec.parent in seen, f"{spec.name} moved before its parent {spec.parent}"
        seen.add(spec.name)


def test_moves_are_keyed_by_the_joint_as_it_exists_now():
    # The Maya half looks the joint up by its CURRENT name, then renames it afterwards.
    target = _profile("cloth_foot_r")
    plan = retarget.plan_retarget(["cloth_GM_foot_R"], target)
    moves = plan.ordered_moves(target)

    assert [source for source, _ in moves] == ["cloth_GM_foot_R"]
    assert [spec.name for _, spec in moves] == ["cloth_foot_r"]


def test_summary_always_names_the_target_rig(genhuman):
    plan = retarget.plan_retarget(["cloth_root"], genhuman)
    assert "genhuman" in plan.summary()
