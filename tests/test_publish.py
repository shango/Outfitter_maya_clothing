"""Headless tests for the pure publish core (no Maya)."""
import _bootstrap  # noqa: F401
import _assets

from snap_on_clothing.core import publish as P
from snap_on_clothing.core import library


# --- name + path helpers ------------------------------------------------------
def test_sanitize_asset_name():
    assert P.sanitize_asset_name("Trench Coat A") == "Trench_Coat_A"
    assert P.sanitize_asset_name("  hat/v2  ") == "hat_v2"
    assert P.sanitize_asset_name("3dshirt").startswith("_3")
    assert P.sanitize_asset_name("") == "clothing_asset"


def test_destination_paths_layout(tmp_path):
    paths = P.destination_paths(tmp_path, "trench coat")
    assert paths.folder == tmp_path / "trench_coat"
    assert paths.ma == tmp_path / "trench_coat" / "trench_coat.ma"
    assert paths.sidecar == tmp_path / "trench_coat" / "trench_coat.json"
    assert paths.thumbnail == tmp_path / "trench_coat" / "trench_coat.png"


# --- sidecar assembly + round-trip -------------------------------------------
def test_spec_to_sidecar_keys():
    spec = P.PublishSpec(
        asset_name="coat_a", asset_type="coat", cloth_version="1.0.0",
        genhuman_compat=("v03", "v04"), author="me", description="a coat",
        rig_version="v03", created="2026-06-11", tri_count=1240, vert_count=820)
    data = spec.to_sidecar()
    assert data["assetName"] == "coat_a"
    assert data["genHumanCompat"] == "v03, v04"
    assert data["notes"] == "a coat"
    assert data["created"] == "2026-06-11"
    assert data["rigVersion"] == "v03"
    assert data["triCount"] == 1240 and data["vertCount"] == 820


def test_sidecar_omits_unknown_polycount():
    spec = P.PublishSpec(asset_name="x", asset_type="hat", cloth_version="1.0.0",
                         genhuman_compat=("v03",))
    data = spec.to_sidecar()
    assert "triCount" not in data and "vertCount" not in data
    assert data["created"]  # defaults to today when not supplied


def test_spec_metadata_round_trip():
    spec = P.PublishSpec(
        asset_name="coat_a", asset_type="coat", cloth_version="2.0.0",
        genhuman_compat=("v03",), rig_version="v03", created="2026-06-11",
        tri_count=999, vert_count=500, description="desc")
    meta, errors = spec.metadata()
    assert errors == [] and meta is not None
    assert meta.tri_count == 999 and meta.vert_count == 500
    assert meta.created == "2026-06-11" and meta.rig_version == "v03"
    assert meta.notes == "desc"


def test_spec_metadata_reports_bad_type():
    spec = P.PublishSpec(asset_name="x", asset_type="cape", cloth_version="1.0.0",
                         genhuman_compat=("v03",))
    meta, errors = spec.metadata()
    assert meta is None and any("cape" in e for e in errors)


# --- write + read back through the real loader -------------------------------
def test_write_sidecar_read_by_library(tmp_path):
    # a structurally-valid .ma with no sidecar yet
    paths = P.destination_paths(tmp_path, "coat_a")
    paths.folder.mkdir(parents=True, exist_ok=True)
    _assets.write_asset_ma(
        paths.ma, joints=["cloth_root", "cloth_spine_01"], asset_name="coat_a")
    spec = P.PublishSpec(
        asset_name="coat_a", asset_type="coat", cloth_version="1.0.0",
        genhuman_compat=("v03",), rig_version="v03", created="2026-06-11",
        tri_count=1240, vert_count=820, description="published coat")
    P.write_sidecar(paths, spec)

    asset = library.load_asset(paths.ma)
    assert asset.source == "sidecar" and asset.is_valid
    assert asset.metadata.tri_count == 1240
    assert asset.metadata.created == "2026-06-11"
    assert asset.metadata.rig_version == "v03"


# --- validation reuse ---------------------------------------------------------
def test_validate_published_ma_passes_on_good_asset(tmp_path):
    p = _assets.write_asset_ma(
        tmp_path / "good.ma", joints=["cloth_root", "cloth_spine_01"])
    report = P.validate_published_ma(p)
    assert report.ok, [str(i) for i in report.errors]


def test_validate_published_ma_flags_missing_group(tmp_path):
    p = _assets.write_asset_ma(
        tmp_path / "bad.ma", joints=["cloth_root"], groups=["Mesh_GRP", "Rig_GRP"])
    report = P.validate_published_ma(p)
    assert not report.ok
    assert any(i.code == "missing_group" for i in report.errors)


# --- pre-publish sanity check (pure decision logic) --------------------------
def _clean_facts(**over):
    """A scene that should pass: bare names, cloth_root, garment skinned to cloth_*."""
    base = dict(
        has_rig=False,
        namespaces=(),
        present_groups=("Mesh_GRP", "Rig_GRP", "Ctrl_GRP"),
        has_cloth_root=True,
        has_info_node=True,
        has_skincluster=True,
        skin_influences=("cloth_spine_01", "cloth_head"),
        cloth_joint_names=("cloth_root", "cloth_spine_01", "cloth_head"),
    )
    base.update(over)
    return P.SceneFacts(**base)


def _levels(issues, level):
    return [i for i in issues if i.level == level]


def test_root_namespaces_reduces_and_filters():
    assert P.root_namespaces(
        ["jacket_A", "jacket_A:cloth", "jacket_A:cloth:GenHuman_rig", "UI", "shared"]
    ) == ["jacket_A"]
    assert P.root_namespaces([":foo:bar", "baz"]) == ["foo", "baz"]
    assert P.root_namespaces([]) == []


def test_split_influences_by_short_name():
    cloth, other = P.split_influences(
        ["cloth_spine_01", "jacket_A:cloth_head", "ns:GenHuman:spine_01", "thigh_l"],
        "cloth_")
    assert cloth == ["cloth_spine_01", "cloth_head"]
    assert other == ["spine_01", "thigh_l"]


def test_preflight_clean_scene_passes():
    issues = P.assemble_preflight(_clean_facts())
    assert not _levels(issues, "error")
    assert _levels(issues, "ok")  # trailing OK appended when nothing blocks


def test_preflight_flags_rig_in_scene():
    issues = P.assemble_preflight(_clean_facts(has_rig=True))
    errs = _levels(issues, "error")
    assert any("GenHuman rig" in i.message for i in errs)
    assert all(i.fix for i in errs)  # every error carries an actionable fix
    assert not _levels(issues, "ok")  # no OK when something blocks


def test_preflight_flags_namespaces():
    issues = P.assemble_preflight(
        _clean_facts(namespaces=("jacket_A", "jacket_A:cloth")))
    assert any("namespace" in i.message.lower() and i.is_error for i in issues)


def test_preflight_flags_skin_on_non_cloth_joints():
    # the jacket_test.ma failure: garment skinned to the rig's own joints
    issues = P.assemble_preflight(_clean_facts(
        skin_influences=("spine_01", "spine_02", "thigh_l", "thigh_r")))
    bad = [i for i in issues if i.is_error and "non-cloth_*" in i.message]
    assert bad, [i.message for i in issues]
    assert "4 non-cloth_* joint(s)" in bad[0].message


def test_preflight_skin_error_truncates_long_lists():
    issues = P.assemble_preflight(_clean_facts(
        skin_influences=tuple(f"bone_{i:02d}" for i in range(10))))
    msg = next(i.message for i in issues if i.is_error and "non-cloth_*" in i.message)
    assert "10 non-cloth_*" in msg and "+4 more" in msg


def test_preflight_warns_when_unskinned():
    issues = P.assemble_preflight(_clean_facts(
        has_skincluster=False, skin_influences=()))
    assert any("No skinCluster" in i.message and i.level == "warn" for i in issues)
    # unskinned is a warning, not a blocker (matches Scaffold's stance)
    assert not _levels(issues, "error")


def test_preflight_flags_missing_groups_and_root():
    issues = P.assemble_preflight(_clean_facts(
        present_groups=("Mesh_GRP",), has_cloth_root=False))
    assert any("Missing required group" in i.message and i.is_error for i in issues)
    assert any("cloth_root" in i.message and i.is_error for i in issues)
    assert any("Rig_GRP" in i.message for i in issues)


def test_preflight_info_node_is_only_a_warning():
    issues = P.assemble_preflight(_clean_facts(has_info_node=False))
    assert any("cloth_info" in i.message and i.level == "warn" for i in issues)
    assert not _levels(issues, "error")


def test_preflight_warns_when_test_body_still_connected():
    # the skinning-test foot-gun: cloth_* joints left driven by the body at publish time
    issues = P.assemble_preflight(_clean_facts(
        driven_cloth_joints=("cloth_spine_01", "cloth_head")))
    warn = next(i for i in issues if i.level == "warn" and "test body" in i.message)
    assert "2 cloth_* joint(s)" in warn.message
    assert "Disconnect test body" in warn.fix
    assert not _levels(issues, "error")  # advisory — the rig error is the hard blocker


def test_preflight_test_body_warning_truncates_long_lists():
    issues = P.assemble_preflight(_clean_facts(
        driven_cloth_joints=tuple(f"cloth_j{i:02d}" for i in range(10))))
    msg = next(i.message for i in issues if "test body" in i.message)
    assert "10 cloth_*" in msg and "+4 more" in msg


def test_preflight_clean_scene_has_no_test_body_warning():
    issues = P.assemble_preflight(_clean_facts())  # driven_cloth_joints defaults to ()
    assert not any("test body" in i.message for i in issues)
