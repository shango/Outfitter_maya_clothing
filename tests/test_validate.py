"""Headless tests for validation (file + scene-precondition layers)."""
import _bootstrap  # noqa: F401
import _assets
from _fake_scene import FakeScene

from snap_on_clothing.core import ma_parse, library
from snap_on_clothing.core.asset import AssetMetadata
from snap_on_clothing.core.scene import SceneGateway
from snap_on_clothing.core import validate as V


def _codes(report):
    return {i.code for i in report.issues}


# --- file-only validation -----------------------------------------------------
def test_good_fixture_passes():
    asset = library.load_asset(_bootstrap.FIXTURES / "sample_coat.ma")
    summary = ma_parse.summarize_file(asset.ma_path)
    report = V.validate_asset_summary(summary, asset.metadata)
    assert report.ok, [str(i) for i in report.errors]


def test_missing_group_is_error(tmp_path):
    p = _assets.write_asset_ma(tmp_path / "a.ma", joints=["cloth_root"], groups=["Mesh_GRP", "Rig_GRP"])
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert not report.ok
    assert "missing_group" in _codes(report)


def test_blendshape_forbidden(tmp_path):
    p = _assets.write_asset_ma(
        tmp_path / "a.ma", joints=["cloth_root", "cloth_spine_01"],
        extra_lines=['createNode blendShape -n "fit_blend";'],
    )
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert "forbidden_node_type" in _codes(report)


def test_references_and_namespaces_blocked(tmp_path):
    p = tmp_path / "a.ma"
    _assets.write_asset_ma(p, joints=["cloth_root"])
    text = p.read_text() + '\nfile -r -ns "ref" "/x.ma";\nnamespace -add "foo";\n'
    p.write_text(text)
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert "has_references" in _codes(report)
    assert "has_namespaces" in _codes(report)


def test_jnt_suffix_rejected(tmp_path):
    p = _assets.write_asset_ma(tmp_path / "a.ma", joints=["cloth_root", "cloth_spine_01_jnt"])
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert "bad_joint_suffix" in _codes(report)


def test_duplicate_name_detected(tmp_path):
    p = tmp_path / "a.ma"
    _assets.write_asset_ma(p, joints=["cloth_root", "cloth_spine_01"])
    p.write_text(p.read_text() + '\ncreateNode joint -n "cloth_spine_01";\n')
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert "duplicate_name" in _codes(report)


def test_no_cloth_joints_error(tmp_path):
    p = _assets.write_asset_ma(tmp_path / "a.ma", joints=[])
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert "no_cloth_joints" in _codes(report)
    assert "no_root_joint" in _codes(report)


# --- scene preconditions ------------------------------------------------------
def _meta(compat="v03"):
    m, _ = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "clothVersion": "1.0.0", "genHumanCompat": compat,
    })
    return m


def test_fake_scene_satisfies_protocol():
    assert isinstance(FakeScene(), SceneGateway)


def test_no_rig_is_error():
    scene = FakeScene()
    report = V.validate_scene_preconditions(scene, "coat", _meta())
    assert "no_rig" in _codes(report)


def test_version_incompat_errors():
    scene = FakeScene()
    scene.build_genhuman(["root"])
    scene.version = "v05"
    report = V.validate_scene_preconditions(scene, "coat", _meta("v03"))
    assert "version_incompat" in _codes(report)
    assert not report.ok


def test_version_unknown_warns_not_blocks():
    scene = FakeScene()
    scene.build_genhuman(["root"])
    scene.version = None
    report = V.validate_scene_preconditions(scene, "coat", _meta("v03"))
    assert "version_unknown" in _codes(report)
    assert report.ok  # warning does not block


def test_namespace_conflict_errors():
    scene = FakeScene()
    scene.build_genhuman(["root"])
    scene.version = "v03"
    scene.namespaces.add("coat")
    report = V.validate_scene_preconditions(scene, "coat", _meta("v03"))
    assert "ns_exists" in _codes(report)
