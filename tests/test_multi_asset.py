"""M4 multi-asset independence: realistic garment combos attached simultaneously,
each detaching without disturbing the others. Headless (no Maya)."""
import _bootstrap  # noqa: F401
import _assets
from _fake_scene import FakeScene

from snap_on_clothing.core.attach import AttachEngine
from snap_on_clothing.core.export import audit_export_readiness

# A body with enough joints for tops, bottoms and shoes.
BODY = [
    "root", "pelvis", "spine_01", "spine_02", "spine_03",
    "clavicle_l", "upperarm_l", "clavicle_r", "upperarm_r",
    "thigh_l", "calf_l", "foot_l", "thigh_r", "calf_r", "foot_r",
    "neck_01", "head",
]
GROUP = "GenHuman_Joint_GRP"

# realistic per-type joint coverage (cloth_ + exact body name)
COVER = {
    "shirt": ["cloth_root", "cloth_pelvis", "cloth_spine_01", "cloth_spine_02",
              "cloth_spine_03", "cloth_clavicle_l", "cloth_upperarm_l",
              "cloth_clavicle_r", "cloth_upperarm_r"],
    "pants": ["cloth_root", "cloth_pelvis", "cloth_thigh_l", "cloth_calf_l",
              "cloth_thigh_r", "cloth_calf_r"],
    "shoes": ["cloth_root", "cloth_pelvis", "cloth_thigh_l", "cloth_calf_l",
              "cloth_foot_l", "cloth_thigh_r", "cloth_calf_r", "cloth_foot_r"],
    "dress": ["cloth_root", "cloth_pelvis", "cloth_spine_01", "cloth_spine_02",
              "cloth_spine_03", "cloth_thigh_l", "cloth_thigh_r"],
    "hat": ["cloth_root", "cloth_pelvis", "cloth_spine_01", "cloth_spine_02",
            "cloth_spine_03", "cloth_neck_01", "cloth_head"],
    "coat": ["cloth_root", "cloth_pelvis", "cloth_spine_01", "cloth_spine_02",
             "cloth_spine_03", "cloth_clavicle_l", "cloth_clavicle_r"],
}


def _scene():
    s = FakeScene()
    s.build_genhuman(BODY)
    s.version = "v03"
    return s


def _attach_all(scene, tmp_path, combo):
    eng = AttachEngine(scene)
    for atype in combo:
        ns = atype
        p = _assets.write_asset_ma(
            tmp_path / f"{ns}.ma",
            joints=COVER[atype], helper_joints=[f"cloth_{atype}_helper_01"],
            asset_name=f"{atype}_A", asset_type=atype,
        )
        res = eng.attach(_assets.load(p), ns)
        assert res.ok, [str(i) for i in res.report.errors]
    return eng


def _combo_test(tmp_path, combo):
    scene = _scene()
    eng = _attach_all(scene, tmp_path, combo)
    assert len(eng.registry) == len(combo)
    # whole dressed scene is export-ready
    assert audit_export_readiness(scene, eng.registry).ok

    # detach the first; the rest stay fully intact
    first, *rest = combo
    eng.detach(first)
    assert first not in eng.registry
    assert not scene.namespace_exists(first)
    for atype in rest:
        assert atype in eng.registry
        assert scene.namespace_exists(atype)
        # a representative connection of each survivor is still live
        a_joint = COVER[atype][1][len("cloth_"):]  # pelvis
        assert scene.is_connected(f"|{GROUP}|{a_joint}.translate", f"{atype}:cloth_pelvis.translate")
    # survivors still export-ready after the detach
    assert audit_export_readiness(scene, eng.registry).ok


def test_shirt_pants_shoes(tmp_path):
    _combo_test(tmp_path, ["shirt", "pants", "shoes"])


def test_dress_shoes_hat(tmp_path):
    _combo_test(tmp_path, ["dress", "shoes", "hat"])


def test_coat_pants_shoes(tmp_path):
    _combo_test(tmp_path, ["coat", "pants", "shoes"])


def test_detach_all_returns_scene_to_bare_rig(tmp_path):
    scene = _scene()
    combo = ["shirt", "pants", "shoes"]
    eng = _attach_all(scene, tmp_path, combo)
    for atype in combo:
        eng.detach(atype)
    assert len(eng.registry) == 0
    assert scene.connections == set()  # every edge broken
    for j in BODY:  # rig joints all survive
        assert scene.exists(f"|{GROUP}|{j}")
