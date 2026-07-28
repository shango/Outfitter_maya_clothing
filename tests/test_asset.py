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
    assert meta.supports("genhuman", "v04") and not meta.supports("genhuman", "v05")


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


def test_single_body_rig_publishes_gender_none():
    # A registered rig may have one body and no variants at all; its assets say so
    # explicitly rather than leaving gender blank (which reads as "forgot to set it").
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "gender": "none",
        "clothVersion": "1.0.0", "rigId": "acme_biped", "rigVersions": "v01",
    })
    assert errors == [] and meta is not None
    assert meta.gender == "none"


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


# --- rig identity (rig-agnostic metadata) ------------------------------------
def test_legacy_sidecar_with_no_rig_id_reads_as_genhuman():
    """Back-compat contract: every asset published before the tool went rig-agnostic is,
    by definition, a GenHuman asset. Its genHumanCompat list becomes rigVersions, so an
    existing library keeps working with no file rewritten."""
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "old_coat", "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0", "genHumanCompat": "v03, v04",
    })
    assert errors == [] and meta is not None
    assert meta.rig_id == "genhuman"
    assert meta.rig_versions == ("v03", "v04")
    assert meta.supports("genhuman", "v03")


def test_explicit_rig_id_and_versions():
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "acme_coat", "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0", "rigId": "acme_biped", "rigVersions": "v01, v02",
    })
    assert errors == [] and meta is not None
    assert meta.rig_id == "acme_biped"
    assert meta.rig_versions == ("v01", "v02")


def test_rig_versions_wins_over_legacy_genhuman_compat():
    """A re-published GenHuman asset carries both keys; rigVersions is authoritative."""
    meta, _ = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0", "rigVersions": "v05", "genHumanCompat": "v03",
    })
    assert meta is not None and meta.rig_versions == ("v05",)


def test_rig_versions_accepts_a_json_array():
    meta, _ = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0", "rigId": "acme_biped", "rigVersions": ["v01", "v02"],
    })
    assert meta is not None and meta.rig_versions == ("v01", "v02")


def test_missing_version_list_is_still_an_error():
    meta, errors = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0", "rigId": "acme_biped",
    })
    assert meta is None
    assert any("rigVersions" in e for e in errors)


def test_supports_gates_on_the_rig_not_only_the_version():
    """The failure this prevents: two rigs that happen to share a version string. A
    GenHuman v01 garment must never read as compatible with Acme v01 - different
    skeleton, so the cloth_ joints would not match anything."""
    meta, _ = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0", "rigId": "genhuman", "rigVersions": "v01",
    })
    assert meta is not None
    assert meta.supports("genhuman", "v01")
    assert not meta.supports("acme_biped", "v01")


def test_supports_with_no_version_checks_the_rig_alone():
    meta, _ = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0", "rigId": "acme_biped", "rigVersions": "v01",
    })
    assert meta is not None
    assert meta.supports("acme_biped")
    assert not meta.supports("genhuman")


def test_genhuman_compat_alias_still_reads():
    """window.py and older callers read .genhuman_compat; it aliases rig_versions."""
    meta, _ = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0", "rigId": "acme_biped", "rigVersions": "v01",
    })
    assert meta is not None and meta.genhuman_compat == meta.rig_versions
