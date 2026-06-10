"""Headless tests for the Genie export-readiness audit (M4, no Maya)."""
import _bootstrap  # noqa: F401
import _assets
from _fake_scene import FakeScene

from snap_on_clothing.core.attach import AttachEngine
from snap_on_clothing.core.export import audit_export_readiness
from snap_on_clothing.core.registry import Connection

BODY = ["root", "pelvis", "spine_01", "spine_02", "neck_01", "head"]
GROUP = "GenHuman_Joint_GRP"


def _scene(version="v03"):
    s = FakeScene()
    s.build_genhuman(BODY)
    s.version = version
    return s


def _attach(scene, tmp_path, name, ns, *, joints=None, atype="coat"):
    p = _assets.write_asset_ma(
        tmp_path / f"{name}.ma",
        joints=joints or ["cloth_root", "cloth_pelvis", "cloth_spine_01"],
        asset_name=name, asset_type=atype,
    )
    eng = AttachEngine(scene)
    return eng


def test_clean_dressed_scene_is_export_ready(tmp_path):
    scene = _scene()
    eng = AttachEngine(scene)
    p = _assets.write_asset_ma(
        tmp_path / "coat.ma",
        joints=["cloth_root", "cloth_pelvis", "cloth_spine_01"],
        asset_name="coat_A", asset_type="coat",
    )
    assert eng.attach(_assets.load(p), "coat").ok
    audit = audit_export_readiness(scene, eng.registry)
    assert audit.ok, [str(i) for i in audit.report.errors]
    codes = {i.code for i in audit.report.issues}
    assert "export_ready" in codes
    assert "genie_names_unset" in codes  # empty required list -> info, not error


def test_missing_required_genie_node_fails(tmp_path):
    scene = _scene()
    eng = AttachEngine(scene)
    p = _assets.write_asset_ma(
        tmp_path / "coat.ma", joints=["cloth_root", "cloth_pelvis"],
        asset_name="coat_A", asset_type="coat",
    )
    eng.attach(_assets.load(p), "coat")
    audit = audit_export_readiness(scene, eng.registry, required_nodes=("god_m_godnode_anim", "Genie_root"))
    assert not audit.ok
    bad = {i.code: i.node for i in audit.report.errors}
    assert bad.get("genie_node_missing") == "Genie_root"  # the present one passes


def test_missing_export_skeleton_fails():
    scene = FakeScene()  # no GenHuman at all
    scene.version = "v03"
    audit = audit_export_readiness(scene, AttachEngine(scene).registry)
    assert not audit.ok
    assert "export_skeleton_missing" in {i.code for i in audit.report.errors}


def test_multi_asset_namespaces_isolated(tmp_path):
    scene = _scene()
    eng = AttachEngine(scene)
    for name, ns, atype in (("coat_A", "coat", "coat"), ("pants_A", "pants", "pants")):
        p = _assets.write_asset_ma(
            tmp_path / f"{ns}.ma", joints=["cloth_root", "cloth_pelvis"],
            asset_name=name, asset_type=atype,
        )
        assert eng.attach(_assets.load(p), ns).ok
    audit = audit_export_readiness(scene, eng.registry)
    assert audit.ok, [str(i) for i in audit.report.errors]


def test_audit_flags_a_rig_targeting_edge(tmp_path):
    """A (hypothetical) edge that drives a rig joint must be caught."""
    scene = _scene()
    eng = AttachEngine(scene)
    p = _assets.write_asset_ma(
        tmp_path / "coat.ma", joints=["cloth_root", "cloth_pelvis"],
        asset_name="coat_A", asset_type="coat",
    )
    eng.attach(_assets.load(p), "coat")
    inst = eng.registry.get("coat")
    # Inject a malformed edge: clothing source driving a rig destination.
    inst.connections.append(
        Connection(src="coat:cloth_root.translate", dst=f"|{GROUP}|root.translate"))
    audit = audit_export_readiness(scene, eng.registry)
    assert not audit.ok
    codes = {i.code for i in audit.report.errors}
    assert "edge_dst_not_owned" in codes
    assert "edge_src_clothing" in codes
