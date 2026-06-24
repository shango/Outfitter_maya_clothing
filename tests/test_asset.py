"""Headless tests for the asset metadata model."""
import _bootstrap  # noqa: F401

from outfitter.core.asset import AssetMetadata


def test_from_spec_attr_names():
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "trench_coat_A",
        "assetType": "coat",
        "gender": "male",
        "clothVersion": "1.0.0",
        "genHumanCompat": "v03, v04",
    })
    assert errors == []
    assert meta is not None
    assert meta.asset_name == "trench_coat_A"
    assert meta.genhuman_compat == ("v03", "v04")
    assert meta.supports("v04") and not meta.supports("v05")


def test_from_snake_case_names():
    meta, errors = AssetMetadata.from_mapping({
        "asset_name": "hat_A", "asset_type": "hat", "gender": "female",
        "cloth_version": "2.1.0", "genhuman_compat": ["v03"],
    })
    assert errors == [] and meta is not None
    assert meta.asset_type == "hat" and meta.genhuman_compat == ("v03",)


def test_invalid_type_reported():
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "cape",
        "clothVersion": "1.0.0", "genHumanCompat": "v03",
    })
    assert meta is None
    assert any("cape" in e for e in errors)


def test_missing_fields_collected_not_raised():
    meta, errors = AssetMetadata.from_mapping({"assetName": "x"})
    assert meta is None
    assert any("assetType" in e for e in errors)
    assert any("gender" in e for e in errors)
    assert any("clothVersion" in e for e in errors)
    assert any("genHumanCompat" in e for e in errors)


def test_gender_is_required():
    # M12 Phase B: gender is a required, validated field — a sidecar without it is invalid.
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat",
        "clothVersion": "1.0.0", "genHumanCompat": "v03",
    })
    assert meta is None
    assert any("gender" in e for e in errors)


def test_bad_gender_rejected():
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "gender": "unisex",
        "clothVersion": "1.0.0", "genHumanCompat": "v03",
    })
    assert meta is None
    assert any("unisex" in e for e in errors)


def test_gender_normalized_case_insensitive():
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "gender": "Female",
        "clothVersion": "1.0.0", "genHumanCompat": "v03",
    })
    assert errors == [] and meta is not None
    assert meta.gender == "female"


def test_compat_dedup_and_trim():
    meta, _ = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "shirt", "gender": "male",
        "clothVersion": "1.0.0", "genHumanCompat": " v03 , v03 , v04 ",
    })
    assert meta is not None and meta.genhuman_compat == ("v03", "v04")


def test_optional_publish_fields_read():
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "coat", "assetType": "coat", "gender": "male", "clothVersion": "1.0.0",
        "genHumanCompat": "v03", "created": "2026-06-11", "rigVersion": "v03",
        "triCount": "1,240", "vertCount": 820,
    })
    assert errors == [] and meta is not None
    assert meta.created == "2026-06-11" and meta.rig_version == "v03"
    assert meta.tri_count == 1240 and meta.vert_count == 820


def test_optional_fields_default_when_absent():
    meta, _ = AssetMetadata.from_mapping({
        "assetName": "coat", "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0", "genHumanCompat": "v03",
    })
    assert meta is not None
    assert meta.created == "" and meta.rig_version == ""
    assert meta.tri_count is None and meta.vert_count is None


def test_garbage_polycount_ignored_not_fatal():
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "coat", "assetType": "coat", "gender": "male", "clothVersion": "1.0.0",
        "genHumanCompat": "v03", "triCount": "lots", "vertCount": "",
    })
    assert errors == [] and meta is not None
    assert meta.tri_count is None and meta.vert_count is None
