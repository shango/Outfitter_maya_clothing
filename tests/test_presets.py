"""Headless tests for fit/placement preset capture, save/load, and re-apply."""
import _bootstrap  # noqa: F401
from _fake_scene import FakeScene

from snap_on_clothing.core import controls as C
from snap_on_clothing.core.placement import Placement, apply_placement, read_placement
from snap_on_clothing.core.presets import FitValue, Preset, apply_preset, capture_preset
from snap_on_clothing.core.registry import AttachedInstance


def _instance(ns="coat"):
    s = FakeScene()
    ctrl = f"{ns}:cloth_fit_ctrl"
    root = f"{ns}:cloth_coat_A"
    s.add_node(ctrl, "transform")
    s.add_node(root, "transform")
    s.define_attr(ctrl, "fit_tightness", min=-1.0, max=1.0, default=0.0)
    s.define_attr(ctrl, "fit_thickness", min=0.0, max=1.0, default=0.0)
    s.namespaces.add(ns)
    inst = AttachedInstance(
        namespace=ns, asset_name="coat_A", asset_type="coat",
        ma_path="/x/coat.ma", cloth_root=f"{ns}:cloth_root",
    )
    return s, inst, ctrl, root


def test_capture_stores_namespace_relative():
    scene, inst, ctrl, root = _instance()
    # dial in some values
    attrs = {a.attr: a for a in C.discover_controls(scene, "coat")[0].attrs}
    C.set_fit_value(scene, attrs["fit_tightness"], 0.5)
    apply_placement(scene, root, Placement(translate=(0.0, 1.0, 0.0)))

    preset = capture_preset("snug", scene, inst, placement_node=root)
    assert preset.asset_type == "coat"
    # addresses are portable (no namespace baked in)
    assert all(fv.control == "cloth_fit_ctrl" for fv in preset.fit)
    assert {fv.attr: fv.value for fv in preset.fit}["fit_tightness"] == 0.5
    assert preset.placement_node == "cloth_coat_A"
    assert preset.placement.translate == (0.0, 1.0, 0.0)


def test_json_roundtrip(tmp_path):
    scene, inst, ctrl, root = _instance()
    preset = capture_preset("base", scene, inst, placement_node=root)
    path = preset.save(tmp_path / "base.json")
    loaded = Preset.load(path)
    assert loaded.to_dict() == preset.to_dict()


def test_apply_reproduces_values_on_fresh_instance():
    scene, inst, ctrl, root = _instance()
    attrs = {a.attr: a for a in C.discover_controls(scene, "coat")[0].attrs}
    C.set_fit_value(scene, attrs["fit_tightness"], 0.7)
    C.set_fit_value(scene, attrs["fit_thickness"], 0.3)
    apply_placement(scene, root, Placement(translate=(2.0, 0.0, 0.0)))
    preset = capture_preset("look", scene, inst, placement_node=root)

    # reset everything, then re-apply
    C.reset_all(scene, C.discover_controls(scene, "coat"))
    apply_placement(scene, root, Placement())
    report = apply_preset(scene, preset, "coat")
    assert report.ok
    assert scene.attr_spec(ctrl, "fit_tightness").value == 0.7
    assert scene.attr_spec(ctrl, "fit_thickness").value == 0.3
    assert read_placement(scene, root).translate == (2.0, 0.0, 0.0)


def test_apply_portable_across_namespaces():
    scene, inst, ctrl, root = _instance("coat")
    C.set_fit_value(scene, C.discover_controls(scene, "coat")[0].attrs[0], 0.4)
    preset = capture_preset("p", scene, inst)

    # a second, independently-attached coat under a different namespace
    scene.add_node("coat1:cloth_fit_ctrl", "transform")
    scene.define_attr("coat1:cloth_fit_ctrl", "fit_tightness", min=-1.0, max=1.0)
    scene.define_attr("coat1:cloth_fit_ctrl", "fit_thickness", min=0.0, max=1.0)
    scene.namespaces.add("coat1")

    apply_preset(scene, preset, "coat1")
    assert scene.attr_spec("coat1:cloth_fit_ctrl", "fit_tightness").value == 0.4


def test_apply_clamps_and_warns_on_missing():
    scene, inst, ctrl, root = _instance()
    preset = Preset(
        name="bad", asset_type="coat",
        fit=(
            FitValue("cloth_fit_ctrl", "fit_thickness", 9.0),  # out-of-range -> clamp to max
            FitValue("cloth_fit_ctrl", "fit_ghost", 1.0),      # missing attr -> warning
        ),
    )
    report = apply_preset(scene, preset, "coat")
    assert report.ok  # warnings only
    assert "preset_attr_missing" in {i.code for i in report.warnings}
    assert scene.attr_spec(ctrl, "fit_thickness").value == 1.0  # clamped to max
