"""Headless tests for the attach/detach lifecycle (transactional, no Maya)."""
import _bootstrap  # noqa: F401
import _assets
from _fake_scene import FakeScene

from outfitter.core.attach import AttachEngine, sanitize_namespace

BODY = ["root", "pelvis", "spine_01", "spine_02", "neck_01", "head"]
GROUP = "GenHuman_Joint_GRP"


def _scene(version="v03"):
    s = FakeScene()
    s.build_genhuman(BODY)
    s.version = version
    return s


def _coat(tmp_path):
    p = _assets.write_asset_ma(
        tmp_path / "coat.ma",
        joints=["cloth_root", "cloth_pelvis", "cloth_spine_01", "cloth_spine_02"],
        helper_joints=["cloth_coatTail_01"],
        asset_name="coat_A", asset_type="coat",
    )
    return _assets.load(p)


def test_attach_connects_matched_joints(tmp_path):
    scene = _scene()
    eng = AttachEngine(scene)
    res = eng.attach(_coat(tmp_path), "coat")
    assert res.ok, [str(i) for i in res.report.errors]
    # 4 matched joints x 3 attrs (translate/rotate/scale) = 12 edges
    assert len(res.instance.connections) == 12
    assert scene.is_connected(f"|{GROUP}|spine_01.translate", "coat:cloth_spine_01.translate")
    assert scene.is_connected(f"|{GROUP}|root.scale", "coat:cloth_root.scale")
    # helper joint stays unconnected
    assert scene.incoming("coat:cloth_coatTail_01", "translate") is None


def test_attach_uses_full_dag_path_dual_skeleton(tmp_path):
    scene = _scene()
    scene.add_second_skeleton(BODY)  # rig-internal skeleton, same short names
    eng = AttachEngine(scene)
    res = eng.attach(_coat(tmp_path), "coat")
    assert res.ok
    # every src plug must come from the export group, never the deform layer
    for c in res.instance.connections:
        assert c.src.startswith(f"|{GROUP}|")


def test_detach_breaks_only_recorded_and_removes_namespace(tmp_path):
    scene = _scene()
    eng = AttachEngine(scene)
    eng.attach(_coat(tmp_path), "coat")
    res = eng.detach("coat")
    assert res.ok
    assert res.broken == 12
    assert "coat" not in eng.registry
    assert not scene.namespace_exists("coat")
    assert scene.connections == set()  # scene back to pre-attach
    # GenHuman joints untouched
    assert scene.exists(f"|{GROUP}|spine_01")


def test_multi_asset_independent_detach(tmp_path):
    scene = _scene()
    eng = AttachEngine(scene)
    coat = _coat(tmp_path)
    pants_p = _assets.write_asset_ma(
        tmp_path / "pants.ma",
        joints=["cloth_root", "cloth_pelvis"],
        asset_name="pants_A", asset_type="pants",
    )
    pants = _assets.load(pants_p)
    assert eng.attach(coat, "coat").ok
    assert eng.attach(pants, "pants").ok
    assert len(eng.registry) == 2

    eng.detach("coat")
    assert "coat" not in eng.registry
    assert "pants" in eng.registry
    # pants connections survive
    assert scene.is_connected(f"|{GROUP}|pelvis.rotate", "pants:cloth_pelvis.rotate")
    assert not scene.namespace_exists("coat")
    assert scene.namespace_exists("pants")


def test_validation_failure_leaves_scene_untouched(tmp_path):
    scene = _scene()
    before_nodes = set(scene.nodes)
    eng = AttachEngine(scene)
    bad = _assets.write_asset_ma(
        tmp_path / "bad.ma", joints=["cloth_root"], groups=["Mesh_GRP"],  # missing Rig/Ctrl
    )
    res = eng.attach(_assets.load(bad), "bad")
    assert not res.ok
    assert "missing_group" in {i.code for i in res.report.errors}
    assert set(scene.nodes) == before_nodes  # nothing imported
    assert not scene.namespace_exists("bad")


def test_version_mismatch_blocks_before_import(tmp_path):
    scene = _scene(version="v05")
    before = set(scene.nodes)
    eng = AttachEngine(scene)
    res = eng.attach(_coat(tmp_path), "coat")
    assert not res.ok
    assert "version_incompat" in {i.code for i in res.report.errors}
    assert set(scene.nodes) == before


def test_missing_export_group_blocks_before_import(tmp_path):
    # A non-existent export group means the chosen rig isn't there: caught as a
    # precondition, so the asset is never even imported (scene byte-identical).
    scene = _scene()
    before = set(scene.nodes)
    eng = AttachEngine(scene)
    res = eng.attach(_coat(tmp_path), "coat", export_group="DoesNotExist_GRP")
    assert not res.ok
    assert "no_rig" in {i.code for i in res.report.errors}
    assert set(scene.nodes) == before
    assert not scene.namespace_exists("coat")


def test_empty_export_group_rolls_back_import(tmp_path):
    # The group exists (rig present) but holds no joints: this we only learn after
    # import, so the import must be rolled back.
    scene = _scene()
    scene.add_node("Empty_GRP", "transform")
    before = set(scene.nodes)
    eng = AttachEngine(scene)
    res = eng.attach(_coat(tmp_path), "coat", export_group="Empty_GRP")
    assert not res.ok
    assert "no_body_joints" in {i.code for i in res.report.errors}
    assert set(scene.nodes) == before  # imported then rolled back
    assert not scene.namespace_exists("coat")


# --- multi-rig / namespace-aware attach (selection-driven) -------------------
def test_resolve_export_group_from_selection():
    scene = FakeScene()
    a = scene.build_genhuman(BODY, namespace="charA")
    b = scene.build_genhuman(BODY, namespace="charB")
    # any node of charB resolves to charB's export group, not charA's
    assert scene.resolve_export_group("charB:god_m_godnode_anim") == b
    assert scene.resolve_export_group(f"|{b}|charB:spine_01") == b
    assert scene.resolve_export_group("charA:god_m_godnode_anim") == a
    # a root-level selection with no namespace resolves nothing here
    assert scene.resolve_export_group("someRandomNode") is None


def test_attach_aligns_rig_group_to_export_frame(tmp_path):
    # The export group carries a transform (real rig: GenHuman_Joint_GRP rotate -90 X).
    # Attach must copy that world frame onto the garment's Rig_GRP, else the local-only
    # joint connections reproduce the body in the wrong frame (garment on the ground).
    scene = _scene()
    rot90x = [1, 0, 0, 0, 0, 0, 1, 0, 0, -1, 0, 0, 0, 0, 0, 1]  # -90° about X
    scene.matrices[GROUP] = rot90x
    eng = AttachEngine(scene)
    res = eng.attach(_coat(tmp_path), "coat")
    assert res.ok, [str(i) for i in res.report.errors]
    assert scene.world_matrix("coat:Rig_GRP") == rot90x  # frame copied onto the garment


def test_attach_to_namespaced_rig(tmp_path):
    scene = FakeScene()
    grp = scene.build_genhuman(BODY, namespace="charB")
    scene.version = "v03"
    eng = AttachEngine(scene)
    res = eng.attach(_coat(tmp_path), "coatB", export_group=grp)
    assert res.ok, [str(i) for i in res.report.errors]
    # connection sources are the namespaced rig's joints; dsts the garment namespace
    for c in res.instance.connections:
        assert "charB:" in c.src and c.src.startswith(f"|{grp}|")
        assert c.dst.startswith("coatB:cloth_")


def test_two_rigs_dressed_independently(tmp_path):
    scene = FakeScene()
    a = scene.build_genhuman(BODY, namespace="charA")
    b = scene.build_genhuman(BODY, namespace="charB")
    scene.version = "v03"
    eng = AttachEngine(scene)
    assert eng.attach(_coat(tmp_path), "coatA", export_group=a).ok
    assert eng.attach(_coat(tmp_path), "coatB", export_group=b).ok
    assert len(eng.registry) == 2

    # each garment is driven only by its own rig
    assert scene.is_connected(f"|{a}|charA:spine_01.translate", "coatA:cloth_spine_01.translate")
    assert scene.is_connected(f"|{b}|charB:spine_01.translate", "coatB:cloth_spine_01.translate")

    eng.detach("coatA")
    assert "coatA" not in eng.registry and "coatB" in eng.registry
    assert not scene.namespace_exists("coatA")
    # charB's garment survives untouched
    assert scene.is_connected(f"|{b}|charB:spine_01.translate", "coatB:cloth_spine_01.translate")
    assert "coat" not in eng.registry


def test_locked_target_aborts_and_rolls_back(tmp_path):
    scene = _scene()
    before = set(scene.nodes)
    eng = AttachEngine(scene)

    # lock a target attr right after import by wrapping import_asset
    orig_import = scene.import_asset

    def locking_import(path, namespace):
        orig_import(path, namespace)
        scene.lock(f"{namespace}:cloth_spine_01", "rotate")

    scene.import_asset = locking_import  # type: ignore[assignment]
    res = eng.attach(_coat(tmp_path), "coat")
    assert not res.ok
    assert "attr_locked" in {i.code for i in res.report.errors}
    assert set(scene.nodes) == before  # fully rolled back
    assert scene.connections == set()


def test_detach_unknown_namespace_errors():
    eng = AttachEngine(_scene())
    res = eng.detach("ghost")
    assert not res.ok
    assert "not_attached" in {i.code for i in res.report.errors}


def test_sanitize_namespace():
    assert sanitize_namespace("Trench Coat #2") == "Trench_Coat__2"
    assert sanitize_namespace("3coat")[0] == "_"
    assert sanitize_namespace("  ") == "clothing"
