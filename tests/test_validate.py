"""Headless tests for validation (file + scene-precondition layers)."""
import _bootstrap  # noqa: F401
import _assets
from _fake_scene import FakeScene

from outfitter.core import ma_parse, library
from outfitter.core.asset import AssetMetadata
from outfitter.core.scene import SceneGateway
from outfitter.core import validate as V


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


# --- export-time cleanliness (Authoring Spec §10 / §13 / §11) -----------------
def test_unknown_node_rejected(tmp_path):
    p = _assets.write_asset_ma(
        tmp_path / "a.ma", joints=["cloth_root", "cloth_spine_01"],
        extra_lines=['createNode unknown -n "lostPluginNode";'])
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert "unknown_node" in _codes(report)


def test_timeline_animation_curve_rejected(tmp_path):
    # animCurveT* are timeline keyframes — banned (assets ship static).
    p = _assets.write_asset_ma(
        tmp_path / "a.ma", joints=["cloth_root", "cloth_spine_01"],
        extra_lines=['createNode animCurveTL -n "cloth_root_translateX";'])
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert "anim_curve" in _codes(report)


def test_set_driven_key_curve_allowed(tmp_path):
    # animCurveU* are set-driven keys (input = a driver attr), an allowed rig mechanism
    # — the shipped example drives its fit lattice with animCurveUU. Must not be flagged.
    p = _assets.write_asset_ma(
        tmp_path / "a.ma", joints=["cloth_root", "cloth_spine_01"],
        extra_lines=['createNode animCurveUU -n "cloth_fit_lattice_scaleX";'])
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert "anim_curve" not in _codes(report)
    assert report.ok, [str(i) for i in report.errors]


def test_display_layer_rejected_but_default_allowed(tmp_path):
    p = _assets.write_asset_ma(
        tmp_path / "a.ma", joints=["cloth_root", "cloth_spine_01"],
        extra_lines=['createNode displayLayer -n "defaultLayer";',
                     'createNode displayLayer -n "garment_layer";'])
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    layer_issues = [i for i in report.issues if i.code == "display_layer"]
    assert [i.node for i in layer_issues] == ["garment_layer"]  # defaultLayer not flagged


def test_renderer_shader_rejected(tmp_path):
    p = _assets.write_asset_ma(
        tmp_path / "a.ma", joints=["cloth_root", "cloth_spine_01"],
        extra_lines=['createNode aiStandardSurface -n "coat_arnold_mtl";'])
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert "renderer_shader" in _codes(report)


def test_generic_shader_allowed(tmp_path):
    # lambert / standardSurface are explicitly permitted (§11) — must not be flagged.
    p = _assets.write_asset_ma(
        tmp_path / "a.ma", joints=["cloth_root", "cloth_spine_01"],
        extra_lines=['createNode lambert -n "coat_lambert";',
                     'createNode standardSurface -n "coat_std";'])
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert report.ok, [str(i) for i in report.errors]
    assert "renderer_shader" not in _codes(report)


def test_no_cloth_joints_error(tmp_path):
    p = _assets.write_asset_ma(tmp_path / "a.ma", joints=[])
    summary = ma_parse.summarize_file(p)
    report = V.validate_asset_summary(summary, _assets.load(p).metadata)
    assert "no_cloth_joints" in _codes(report)
    assert "no_root_joint" in _codes(report)


# --- scene preconditions ------------------------------------------------------
def _meta(compat="v03"):
    m, _ = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0", "genHumanCompat": compat,
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


# --- rig identity (multi-rig safety) -----------------------------------------
def _rig_profile(rig_id="acme_biped", version="v01", export_group="GenHuman_Joint_GRP"):
    """A minimal registered rig, reusing the fake scene's export-group name so the
    rig-present gate passes and the rig-identity gate is what's under test."""
    from outfitter.core import rigs
    from outfitter.core import skeleton as sk

    return rigs.RigProfile(
        rig_id=rig_id, display_name=rig_id.title(), version=version,
        export_group=export_group, markers=(export_group,),
        skeleton=sk.SkeletonSpec(
            root_group="Rig_GRP", root_group_rotate=(-90.0, 0.0, 0.0),
            root_joint="cloth_root",
            joints=(sk.JointSpec(name="cloth_root", parent="Rig_GRP"),)))


def _rig_meta(rig_id="genhuman", versions="v03"):
    m, _ = AssetMetadata.from_mapping({
        "assetName": "x", "assetType": "coat", "gender": "male",
        "clothVersion": "1.0.0", "rigId": rig_id, "rigVersions": versions,
    })
    return m


def test_asset_for_another_rig_is_rejected():
    """The gate that makes a multi-rig library safe: a GenHuman garment must not attach
    to an Acme rig even though both scenes look structurally identical to the tool."""
    scene = FakeScene()
    scene.build_genhuman(["root"])
    scene.version = "v01"
    report = V.validate_scene_preconditions(
        scene, "coat", _rig_meta("genhuman", "v01"), profile=_rig_profile("acme_biped"))
    assert "rig_mismatch" in _codes(report)
    assert not report.ok


def test_matching_rig_passes_the_identity_gate():
    scene = FakeScene()
    scene.build_genhuman(["root"])
    scene.version = "v01"
    report = V.validate_scene_preconditions(
        scene, "coat", _rig_meta("acme_biped", "v01"), profile=_rig_profile("acme_biped"))
    assert "rig_mismatch" not in _codes(report)
    assert report.ok, [str(i) for i in report.errors]


def test_rig_mismatch_message_names_both_rigs():
    """The artist needs to know which rig the asset wants, not just that it failed."""
    scene = FakeScene()
    scene.build_genhuman(["root"])
    scene.version = "v01"
    report = V.validate_scene_preconditions(
        scene, "coat", _rig_meta("genhuman", "v01"), profile=_rig_profile("acme_biped"))
    issue = next(i for i in report.issues if i.code == "rig_mismatch")
    assert "genhuman" in issue.message and "acme_biped" in issue.message
    assert "Retarget" in issue.fix


def test_missing_rig_message_names_the_selected_rig():
    report = V.validate_scene_preconditions(
        FakeScene(), "coat", _rig_meta(), profile=_rig_profile("acme_biped"))
    issue = next(i for i in report.issues if i.code == "no_rig")
    assert "Acme_Biped" in issue.message


def test_version_gate_still_applies_within_the_same_rig():
    scene = FakeScene()
    scene.build_genhuman(["root"])
    scene.version = "v02"
    report = V.validate_scene_preconditions(
        scene, "coat", _rig_meta("acme_biped", "v01"), profile=_rig_profile("acme_biped"))
    assert "version_incompat" in _codes(report)


def test_no_profile_keeps_the_original_single_rig_behaviour():
    """Called without a profile (the pre-rig-agnostic path), validation behaves as before."""
    scene = FakeScene()
    scene.build_genhuman(["root"])
    scene.version = "v03"
    report = V.validate_scene_preconditions(scene, "coat", _meta("v03"))
    assert report.ok, [str(i) for i in report.errors]
