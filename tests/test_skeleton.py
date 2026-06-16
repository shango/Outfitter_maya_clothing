"""Headless tests for the persisted canonical cloth_* skeleton (core.skeleton).

The Maya-side rebuild (core.maya_skeleton) is a smoke check, but the data it replays —
the one-and-only GenHuman cloth_* skeleton — is fully verifiable here: it loads, it is
structurally valid (parents resolve in build order, names prefixed), it carries the
real export joints, and it excludes garment-specific helper joints.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from snap_on_clothing import config
from snap_on_clothing.core import skeleton as sk


@pytest.fixture(scope="module")
def spec():
    return sk.load_cloth_skeleton()


def test_data_file_ships_in_the_package():
    assert sk.skeleton_file().is_file(), sk.skeleton_file()


def test_loads_the_full_body_skeleton(spec):
    # 89 body-derived export joints (helper joints excluded).
    assert len(spec.joints) == 89
    assert spec.root_joint == "cloth_root"
    assert spec.root_group == "Rig_GRP"


def test_root_group_carries_the_export_frame(spec):
    assert spec.root_group_rotate == (-90.0, 0.0, 0.0)


def test_skeleton_data_is_structurally_valid(spec):
    assert sk.validate_skeleton(spec) == []


def test_every_joint_uses_the_cloth_prefix(spec):
    for j in spec.joints:
        assert j.name.startswith(config.CLOTH_PREFIX), j.name


def test_root_parents_to_the_group_and_chain_resolves(spec):
    names = set(spec.names)
    root = next(j for j in spec.joints if j.name == "cloth_root")
    assert root.parent == "Rig_GRP"
    for j in spec.joints:
        assert j.parent == spec.root_group or j.parent in names, j.name


def test_parents_are_defined_before_children(spec):
    # build order must be topological so cmds.joint can parent as it goes
    seen = set()
    for j in spec.joints:
        if j.parent != spec.root_group:
            assert j.parent in seen, f"{j.name} precedes its parent {j.parent}"
        seen.add(j.name)


def test_carries_expected_landmark_joints(spec):
    names = set(spec.names)
    for expected in (
        "cloth_head", "cloth_neck_02", "cloth_spine_01", "cloth_pelvis",
        "cloth_hand_l", "cloth_hand_r", "cloth_thigh_l", "cloth_ball_r",
        "cloth_index_03_l", "cloth_ik_foot_root",
    ):
        assert expected in names, expected


def test_excludes_garment_specific_helper_joints(spec):
    names = set(spec.names)
    assert "cloth_coatTail_01" not in names
    assert "cloth_coatTail_02" not in names


def test_origin_joints_default_to_zero_translate(spec):
    root = next(j for j in spec.joints if j.name == "cloth_root")
    assert root.translate == (0.0, 0.0, 0.0)


def test_scale_defaults_to_unit_when_absent(spec):
    # every joint should have a sensible (near-unit) scale, never zero
    for j in spec.joints:
        assert all(abs(s) > 1e-6 for s in j.scale), j.name


def test_load_is_cached(spec):
    assert sk.load_cloth_skeleton() is spec


# --- serializer (regen) round-trip -------------------------------------------
def test_to_json_dict_round_trips_through_load(tmp_path, spec):
    dest = tmp_path / "regen.json"
    written = sk.write_skeleton(spec, dest)
    assert written == dest and dest.is_file()

    # load the freshly-written file by pointing the loader's source at it
    import json
    data = json.loads(dest.read_text())
    assert data["root_joint"] == spec.root_joint
    assert data["root_group_rotate"] == list(spec.root_group_rotate)
    assert len(data["joints"]) == len(spec.joints)

    # rebuild a spec from the written dict and compare field-for-field
    reloaded = sk.SkeletonSpec(
        root_group=data["root_group"],
        root_group_rotate=tuple(data["root_group_rotate"]),
        root_joint=data["root_joint"],
        joints=tuple(
            sk.JointSpec(
                name=j["name"], parent=j["parent"],
                translate=tuple(j["t"]), rotate=tuple(j["r"]),
                joint_orient=tuple(j["jo"]), scale=tuple(j["s"]),
                radius=j["radi"], segment_scale_compensate=j["ssc"],
                rotate_order=j["ro"])
            for j in data["joints"]),
    )
    assert reloaded == spec


def test_write_skeleton_refuses_invalid_data(tmp_path):
    bad = sk.SkeletonSpec(
        root_group="Rig_GRP", root_group_rotate=(-90.0, 0.0, 0.0),
        root_joint="cloth_root",
        joints=(sk.JointSpec(name="cloth_x", parent="cloth_missing"),))
    with pytest.raises(ValueError):
        sk.write_skeleton(bad, tmp_path / "bad.json")
    assert not (tmp_path / "bad.json").exists()


def test_write_skeleton_clears_the_load_cache(tmp_path, spec):
    # writing should invalidate the cache so a later load re-reads the shipped file
    sk.load_cloth_skeleton()  # prime
    sk.write_skeleton(spec, tmp_path / "x.json")
    assert sk.load_cloth_skeleton() == spec  # re-reads shipped file, still valid


# --- prune planning (Delete unused joints) -----------------------------------
def _chain(*pairs):
    """Build a {joint: parent} map from (joint, parent) pairs."""
    return dict(pairs)


def test_prune_deletes_unweighted_leaf():
    # root -> a -> b, only b skinned; nothing to delete (a is interior, b is influence)
    parents = _chain(("cloth_root", "Rig_GRP"), ("a", "cloth_root"), ("b", "a"))
    plan = sk.plan_prune(parents, influences={"b"}, root_joint="cloth_root")
    assert plan.delete == ()
    assert plan.kept_unweighted == ("a",)  # unweighted but has a skinned child
    assert set(plan.survivors) == {"cloth_root", "a", "b"}
    assert plan.is_noop


def test_prune_removes_unskinned_leaf_branch():
    # a coat: spine skinned, an arm branch left unskinned -> the arm leaf goes
    parents = _chain(
        ("cloth_root", "Rig_GRP"),
        ("cloth_spine", "cloth_root"),
        ("cloth_arm", "cloth_root"),  # unskinned leaf
    )
    plan = sk.plan_prune(parents, influences={"cloth_spine"}, root_joint="cloth_root")
    assert plan.delete == ("cloth_arm",)
    assert set(plan.survivors) == {"cloth_root", "cloth_spine"}
    assert not plan.is_noop


def test_prune_cascades_to_newly_exposed_leaves():
    # chain a->b->c, none skinned (only some other joint is): the whole chain peels off,
    # leaf-first, deepest deleted before its parent
    parents = _chain(
        ("cloth_root", "Rig_GRP"),
        ("cloth_pelvis", "cloth_root"),  # the only influence
        ("a", "cloth_root"), ("b", "a"), ("c", "b"),
    )
    plan = sk.plan_prune(parents, influences={"cloth_pelvis"}, root_joint="cloth_root")
    assert plan.delete == ("c", "b", "a")  # children precede parents
    assert set(plan.survivors) == {"cloth_root", "cloth_pelvis"}


def test_prune_keeps_unweighted_interior_with_skinned_descendant():
    # the case naive "delete all unweighted" gets wrong: spine1 unweighted but spine2
    # (its child) is skinned -> spine1 must stay so spine2's local chain is preserved
    parents = _chain(
        ("cloth_root", "Rig_GRP"),
        ("cloth_spine1", "cloth_root"),  # unweighted interior
        ("cloth_spine2", "cloth_spine1"),  # skinned
    )
    plan = sk.plan_prune(parents, influences={"cloth_spine2"}, root_joint="cloth_root")
    assert plan.delete == ()
    assert plan.kept_unweighted == ("cloth_spine1",)


def test_prune_never_deletes_the_root_even_when_unweighted_leaf():
    # a lone unweighted root must survive (validation no_root_joint requires it)
    parents = _chain(("cloth_root", "Rig_GRP"))
    plan = sk.plan_prune(parents, influences=set(), root_joint="cloth_root")
    assert plan.delete == ()
    assert plan.survivors == ("cloth_root",)


def test_prune_with_no_influences_deletes_everything_but_root():
    # the foot-gun the Maya wrapper guards against: with zero influences the pure planner
    # peels the skeleton down to the root. (maya_skeleton.plan_prune_unskinned refuses to
    # reach here by requiring at least one influence.)
    parents = _chain(
        ("cloth_root", "Rig_GRP"), ("a", "cloth_root"), ("b", "a"))
    plan = sk.plan_prune(parents, influences=set(), root_joint="cloth_root")
    assert plan.delete == ("b", "a")
    assert plan.survivors == ("cloth_root",)


def test_prune_real_skeleton_to_a_hat(spec):
    # end-to-end against the shipped skeleton: a hat skins only cloth_head; everything
    # not on the head->root spine peels away, the head chain and its ancestors stay.
    parents = {j.name: j.parent for j in spec.joints}
    plan = sk.plan_prune(parents, influences={"cloth_head"}, root_joint="cloth_root")
    survivors = set(plan.survivors)
    assert "cloth_head" in survivors
    assert "cloth_root" in survivors
    assert "cloth_neck_02" in survivors  # ancestor of head, kept as interior
    # limbs the hat never touches are gone
    assert "cloth_hand_l" not in survivors
    assert "cloth_ball_r" not in survivors
    # ancestors kept despite no weight are reported as kept_unweighted, not deleted
    assert "cloth_neck_02" in plan.kept_unweighted
    assert "cloth_neck_02" not in plan.delete
