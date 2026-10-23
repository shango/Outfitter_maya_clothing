"""Headless tests for the rig-identity migration (core.migrate).

The migration exists to remove an assumption, so the things that matter are: it only
touches assets that don't already declare a rig, it never reassigns one that does, and it
preserves whatever else was in the sidecar. A migration that quietly edits the wrong file
is worse than no migration.
"""
import json

import pytest
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from outfitter.core import migrate
from outfitter.core.asset import AssetMetadata


def _sidecar(tmp_path, name, **fields):
    data = {
        "assetName": name, "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0",
    }
    data.update(fields)
    path = tmp_path / f"{name}.json"
    path.write_text(json.dumps(data, indent=1), encoding="utf-8")
    return path


def test_a_legacy_sidecar_is_planned_with_its_versions_carried_over(tmp_path):
    path = _sidecar(tmp_path, "old_coat", genHumanCompat="v03, v04")

    plan = migrate.plan_stamp([path])

    assert len(plan.candidates) == 1
    assert plan.candidates[0].asset_name == "old_coat"
    assert plan.candidates[0].versions == ("v03", "v04")
    assert plan.rig_id == "genhuman"


def test_an_asset_that_already_declares_a_rig_is_left_alone(tmp_path):
    path = _sidecar(tmp_path, "acme_coat", rigId="acme_biped", rigVersions="v01")

    plan = migrate.plan_stamp([path])

    assert plan.is_empty
    assert plan.already_stamped == 1


def test_stamping_never_reassigns_an_asset_to_another_rig(tmp_path):
    # Even asked to stamp 'genhuman', an Acme asset must not be touched - moving an asset
    # between rigs is a retarget, not a metadata edit.
    path = _sidecar(tmp_path, "acme_coat", rigId="acme_biped", rigVersions="v01")

    migrate.apply_stamp(migrate.plan_stamp([path]))

    assert json.loads(path.read_text())["rigId"] == "acme_biped"


def test_applying_writes_the_identity_and_keeps_every_other_field(tmp_path):
    path = _sidecar(tmp_path, "old_coat", genHumanCompat="v03",
                    author="rigger", notes="hand-added note")

    result = migrate.apply_stamp(migrate.plan_stamp([path]))

    raw = json.loads(path.read_text())
    assert result.stamped == ["old_coat"]
    assert raw["rigId"] == "genhuman"
    assert raw["rigVersions"] == "v03"
    assert raw["notes"] == "hand-added note"  # nothing else was disturbed
    assert raw["genHumanCompat"] == "v03"     # legacy key left readable by old installs


def test_a_stamped_asset_reads_back_with_the_same_identity_it_had_implied(tmp_path):
    # The whole point: making the assumption explicit must not change what the asset means.
    path = _sidecar(tmp_path, "old_coat", genHumanCompat="v03")
    before, _ = AssetMetadata.from_mapping(json.loads(path.read_text()))

    migrate.apply_stamp(migrate.plan_stamp([path]))
    after, _ = AssetMetadata.from_mapping(json.loads(path.read_text()))

    assert (before.rig_id, before.rig_versions) == (after.rig_id, after.rig_versions)


def test_an_asset_with_no_versions_at_all_is_stamped_and_flagged(tmp_path):
    path = _sidecar(tmp_path, "vague_coat")

    result = migrate.apply_stamp(migrate.plan_stamp([path]))

    assert result.stamped == ["vague_coat"]
    assert any("no rig versions" in w for w in result.warnings)


def test_unreadable_sidecars_are_reported_not_crashed_on(tmp_path):
    broken = tmp_path / "broken.json"
    broken.write_text("{not json", encoding="utf-8")

    plan = migrate.plan_stamp([broken, tmp_path / "missing.json"])

    assert plan.is_empty
    assert len(plan.unreadable) == 2


def test_the_result_always_says_the_ma_files_were_not_touched(tmp_path):
    path = _sidecar(tmp_path, "old_coat", genHumanCompat="v03")

    result = migrate.apply_stamp(migrate.plan_stamp([path]))

    assert any("Sidecars only" in w for w in result.warnings)


def test_legacy_assets_are_stamped_genhuman_whatever_rig_is_selected(tmp_path):
    # 1.3.0 passed the UI's selected rig in here; there is no longer a way to.
    path = _sidecar(tmp_path, "old_coat", genHumanCompat="v03")

    with pytest.raises(TypeError):
        migrate.plan_stamp([path], rig_id="eric")
    migrate.apply_stamp(migrate.plan_stamp([path]))

    assert json.loads(path.read_text())["rigId"] == "genhuman"


def test_find_misstamped_matches_only_the_old_stamp_fingerprint(tmp_path):
    wrong = _sidecar(tmp_path, "old_coat", genHumanCompat="v03, v04",
                     rigId="eric", rigVersions="v03, v04")
    wrong_no_versions = _sidecar(tmp_path, "old_hat", genHumanCompat="",
                                 rigId="eric", rigVersions="")
    published_eric = _sidecar(tmp_path, "eric_coat", rigId="eric", rigVersions="v08")
    genhuman = _sidecar(tmp_path, "gh_coat", genHumanCompat="v03",
                        rigId="genhuman", rigVersions="v03")
    hand_edited = _sidecar(tmp_path, "edited", genHumanCompat="v03",
                           rigId="eric", rigVersions="v08")
    legacy = _sidecar(tmp_path, "legacy", genHumanCompat="v03")

    found = migrate.find_misstamped(
        [wrong, wrong_no_versions, published_eric, genhuman, hand_edited, legacy])

    assert found == [wrong, wrong_no_versions]


def test_repair_misstamped_restores_genhuman_and_keeps_fields(tmp_path):
    path = _sidecar(tmp_path, "old_coat", genHumanCompat="v03", rigId="eric",
                    rigVersions="v03", author="someone")

    migrate.repair_misstamped(path)

    data = json.loads(path.read_text())
    assert data["rigId"] == "genhuman" and data["rigVersions"] == "v03"
    assert data["author"] == "someone" and migrate.find_misstamped([path]) == []
