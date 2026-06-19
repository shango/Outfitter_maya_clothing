"""The shipped example asset must stay spec-compliant (headless, no Maya).

`assets/trench_coat_A/` is the bundled starter asset. These tests parse and validate
it through the *real* tool core (the same ma_parse + validate + library code the
browser uses) so it can never silently drift out of compliance with the Authoring Spec.
"""
import _bootstrap  # noqa: F401

from snap_on_clothing import config
from snap_on_clothing.core import library, ma_parse
from snap_on_clothing.core.asset import AssetMetadata
from snap_on_clothing.core.validate import validate_asset_summary

EXAMPLE_DIR = config.bundled_asset_dir() / "trench_coat_A"
EXAMPLE_MA = EXAMPLE_DIR / "trench_coat_A.ma"


def test_example_ma_exists():
    assert EXAMPLE_MA.is_file(), f"missing bundled example asset: {EXAMPLE_MA}"


def test_example_passes_file_validation():
    summary = ma_parse.summarize_file(EXAMPLE_MA, config.INFO_NODE)
    meta, errors = AssetMetadata.from_mapping(summary.info_attrs)
    assert meta is not None, f"cloth_info metadata did not parse: {errors}"
    report = validate_asset_summary(summary, meta)
    assert report.ok, "example asset failed validation: " + "; ".join(
        str(i) for i in report.errors
    )


def test_example_metadata_fields():
    meta, _ = AssetMetadata.from_mapping(
        ma_parse.read_info_attrs(EXAMPLE_MA, config.INFO_NODE)
    )
    assert meta is not None
    assert meta.asset_name == "trench_coat_A"
    assert meta.asset_type == "coat"
    assert meta.asset_type in config.ASSET_TYPES
    assert meta.gender == "male" and meta.gender in config.GENDERS
    assert "v03" in meta.genhuman_compat


def test_example_structure_contract():
    summary = ma_parse.summarize_file(EXAMPLE_MA, config.INFO_NODE)
    # required groups + info + root joint
    for node in (*config.REQUIRED_GROUPS, config.INFO_NODE, config.ROOT_JOINT):
        assert summary.has_node(node), f"missing required node: {node}"
    # connection joints present, correctly named, no _jnt suffix
    joints = summary.cloth_joints()
    assert config.ROOT_JOINT in joints
    assert "cloth_spine_03" in joints
    assert all(not j.endswith("_jnt") for j in joints)
    # helper joints are still cloth_ prefixed
    assert "cloth_coatTail_01" in joints


def test_example_is_clean():
    summary = ma_parse.summarize_file(EXAMPLE_MA, config.INFO_NODE)
    assert not summary.has_references
    assert not summary.has_namespaces
    assert summary.duplicate_names == {}
    for node_type in config.DISALLOWED_ASSET_NODE_TYPES:
        assert summary.nodes_of_type(node_type) == [], f"forbidden {node_type} present"


def test_example_discovered_by_library_scan():
    result = library.scan_library([config.bundled_asset_dir()])
    names = {a.display_name for a in result.valid}
    assert "trench_coat_A" in names
    asset = next(a for a in result.valid if a.display_name == "trench_coat_A")
    # sidecar is the browser fast-path and should win
    assert asset.source == "sidecar"
    assert asset.asset_type == "coat"
