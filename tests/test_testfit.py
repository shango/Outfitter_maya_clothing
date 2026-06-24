"""Headless tests for the pure in-scene skinning-test planner (core.testfit).

The Maya half (core.maya_testfit) is a smoke check, but the decision it replays — which
body→cloth connections to make, and which plugs to skip — is fully verifiable here. The
matching mirrors attach: ``cloth_<base>`` is driven iff ``<base>`` is a body joint; helper
joints with no body match are left unconnected; locked / already-driven plugs are skipped.
"""
import _bootstrap  # noqa: F401

from outfitter import config
from outfitter.core import testfit as T


def _cloth(*shorts):
    """{short: node-address} for cloth joints, addressed by their own short name."""
    return {s: s for s in shorts}


def _body(*shorts):
    """{base: node-address} for body joints under the export group."""
    return {s: f"|GenHuman_Joint_GRP|{s}" for s in shorts}


def test_matches_cloth_to_body_by_base_name():
    plan = T.plan_test_fit(
        _cloth("cloth_spine_01", "cloth_head"),
        _body("spine_01", "head"))
    assert set(plan.matched_joints) == {"cloth_spine_01", "cloth_head"}
    assert plan.unmatched_joints == ()
    # one connection per channel per matched joint
    assert len(plan.connections) == 2 * len(config.CONNECT_ATTRS)
    dsts = {c.dst for c in plan.connections}
    assert "cloth_spine_01.translate" in dsts
    assert "cloth_head.rotate" in dsts


def test_connection_wires_body_plug_to_cloth_plug():
    plan = T.plan_test_fit(_cloth("cloth_spine_01"), _body("spine_01"))
    by_attr = {c.dst.rsplit(".", 1)[1]: c for c in plan.connections}
    conn = by_attr["translate"]
    assert conn.src == "|GenHuman_Joint_GRP|spine_01.translate"
    assert conn.dst == "cloth_spine_01.translate"


def test_helper_joints_with_no_body_match_are_unmatched():
    # cloth_ik_hand_gun / cloth_coatTail have no body joint -> left animator-accessible
    plan = T.plan_test_fit(
        _cloth("cloth_spine_01", "cloth_ik_hand_gun", "cloth_coatTail_01"),
        _body("spine_01"))
    assert plan.matched_joints == ("cloth_spine_01",)
    assert set(plan.unmatched_joints) == {"cloth_ik_hand_gun", "cloth_coatTail_01"}
    assert all(c.dst.startswith("cloth_spine_01") for c in plan.connections)


def test_skips_locked_plugs():
    plan = T.plan_test_fit(
        _cloth("cloth_spine_01"), _body("spine_01"),
        locked={"cloth_spine_01.rotate"})
    dsts = {c.dst for c in plan.connections}
    assert "cloth_spine_01.rotate" not in dsts
    assert "cloth_spine_01.translate" in dsts
    assert [s.reason for s in plan.skipped] == ["locked"]
    assert plan.skipped[0].plug == "cloth_spine_01.rotate"


def test_skips_already_driven_plugs_for_idempotency():
    # re-running after a first connect: the already-driven plugs aren't stolen
    driven = {f"cloth_spine_01.{a}" for a in config.CONNECT_ATTRS}
    plan = T.plan_test_fit(
        _cloth("cloth_spine_01", "cloth_head"), _body("spine_01", "head"),
        driven=driven)
    assert all(c.dst.startswith("cloth_head") for c in plan.connections)
    assert {s.reason for s in plan.skipped} == {"driven"}
    assert len(plan.skipped) == len(config.CONNECT_ATTRS)


def test_empty_when_nothing_matches():
    plan = T.plan_test_fit(_cloth("cloth_coatTail_01"), _body("spine_01"))
    assert plan.is_empty
    assert plan.connections == ()
    assert plan.unmatched_joints == ("cloth_coatTail_01",)


def test_non_cloth_nodes_are_ignored():
    # only cloth_-prefixed nodes are considered (a stray group in the dict is skipped)
    plan = T.plan_test_fit(
        {"cloth_spine_01": "cloth_spine_01", "Rig_GRP": "Rig_GRP"},
        _body("spine_01"))
    assert plan.matched_joints == ("cloth_spine_01",)
    assert plan.unmatched_joints == ()


# --- gendered test body (M14) -----------------------------------------------
def test_body_morph_value_per_gender():
    # The tool ships ONE rig and flips GH_Body_morph: female = base (0), male = full morph (1).
    assert T.body_morph_value("male") == config.GENDER_BODY_MORPH["male"]
    assert T.body_morph_value("female") == config.GENDER_BODY_MORPH["female"]
    assert T.body_morph_value("male") != T.body_morph_value("female")


def test_body_morph_value_case_insensitive():
    assert T.body_morph_value("Female") == T.body_morph_value("female")


def test_body_morph_value_rejects_unknown_gender():
    import pytest

    with pytest.raises(ValueError):
        T.body_morph_value("unisex")


def test_every_gender_has_a_morph_value():
    for g in config.GENDERS:
        # each declared gender must map to a concrete switch value
        assert isinstance(T.body_morph_value(g), float)
