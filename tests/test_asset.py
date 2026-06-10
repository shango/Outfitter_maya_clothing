"""Headless tests for the asset metadata model."""
import _bootstrap  # noqa: F401

from snap_on_clothing.core.asset import AssetMetadata


def test_from_spec_attr_names():
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "trench_coat_A",
        "assetType": "coat",
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
        "asset_name": "hat_A", "asset_type": "hat",
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
    assert any("clothVersion" in e for e in errors)
    assert any("genHumanCompat" in e for e in errors)


def test_compat_dedup_and_trim():
    meta, _ = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "shirt",
        "clothVersion": "1.0.0", "genHumanCompat": " v03 , v03 , v04 ",
    })
    assert meta is not None and meta.genhuman_compat == ("v03", "v04")
