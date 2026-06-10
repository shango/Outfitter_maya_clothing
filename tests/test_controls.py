"""Headless tests for fit-control discovery + driving (Authoring Spec §8)."""
import _bootstrap  # noqa: F401
from _fake_scene import FakeScene

from snap_on_clothing.core import controls as C


def _instance_with_fit(ns="coat"):
    """A scene holding one imported instance exposing a primary fit control."""
    s = FakeScene()
    node = f"{ns}:cloth_fit_ctrl"
    s.add_node(node, "transform")
    s.define_attr(node, "fit_tightness", min=-1.0, max=1.0, default=0.0, value=0.0)
    s.define_attr(node, "fit_thickness", min=0.0, max=1.0, default=0.0, value=0.2)
    s.define_attr(node, "fit_waist_tightness", min=-1.0, max=1.0, default=0.0, value=0.0)
    s.namespaces.add(ns)
    return s, node


def test_discovers_primary_fit_control():
    scene, node = _instance_with_fit()
    controls = C.discover_controls(scene, "coat")
    assert len(controls) == 1
    ctrl = controls[0]
    assert ctrl.name == "cloth_fit_ctrl"
    assert ctrl.is_primary
    assert {a.attr for a in ctrl.attrs} == {"fit_tightness", "fit_thickness", "fit_waist_tightness"}


def test_attr_metadata_and_label():
    scene, _ = _instance_with_fit()
    attrs = {a.attr: a for a in C.discover_controls(scene, "coat")[0].attrs}
    waist = attrs["fit_waist_tightness"]
    assert waist.label == "Waist Tightness"
    assert waist.is_convention
    assert (waist.slider_min, waist.slider_max) == (-1.0, 1.0)
    thick = attrs["fit_thickness"]
    assert thick.value == 0.2
    assert (thick.slider_min, thick.slider_max) == (0.0, 1.0)


def test_primary_control_sorts_first():
    scene, _ = _instance_with_fit()
    # add a secondary control node, alphabetically before cloth_fit_ctrl
    sec = "coat:aaa_extra_ctrl"
    scene.add_node(sec, "transform")
    scene.define_attr(sec, "fit_extra", min=-1.0, max=1.0)
    controls = C.discover_controls(scene, "coat")
    assert controls[0].name == "cloth_fit_ctrl"  # primary wins despite alpha order


def test_non_ctrl_and_non_numeric_attrs_ignored():
    scene, node = _instance_with_fit()
    # a non-keyable + a string attr should not surface
    scene.define_attr(node, "fit_hidden", keyable=False, min=0.0, max=1.0)
    scene.define_attr(node, "fit_note", type="string")
    # a node that is not a *_ctrl must be skipped entirely
    other = "coat:cloth_mesh"
    scene.add_node(other, "transform")
    scene.define_attr(other, "fit_bogus", min=0.0, max=1.0)
    attrs = {a.attr for c in C.discover_controls(scene, "coat") for a in c.attrs}
    assert "fit_hidden" not in attrs
    assert "fit_note" not in attrs
    assert "fit_bogus" not in attrs


def test_prefer_convention_over_custom():
    scene, node = _instance_with_fit()
    scene.define_attr(node, "myCustomFloat", min=0.0, max=10.0)  # non-fit keyable custom
    surfaced = C.surfaced_fit_attrs(C.discover_controls(scene, "coat"))
    assert all(a.is_convention for a in surfaced)  # custom attr excluded while fit_ exist


def test_fallback_to_custom_when_no_convention():
    s = FakeScene()
    node = "dress:shape_ctrl"
    s.add_node(node, "transform")
    s.define_attr(node, "drape", min=0.0, max=1.0, value=0.5)
    s.namespaces.add("dress")
    surfaced = C.surfaced_fit_attrs(C.discover_controls(s, "dress"))
    assert [a.attr for a in surfaced] == ["drape"]
    assert not surfaced[0].is_convention


def test_set_value_clamps_to_range():
    scene, node = _instance_with_fit()
    attr = next(a for a in C.discover_controls(scene, "coat")[0].attrs if a.attr == "fit_thickness")
    assert C.set_fit_value(scene, attr, 5.0) == 1.0   # clamped to max
    assert scene.attr_spec(node, "fit_thickness").value == 1.0
    assert C.set_fit_value(scene, attr, -3.0) == 0.0  # clamped to min


def test_reset_restores_default():
    scene, node = _instance_with_fit()
    controls = C.discover_controls(scene, "coat")
    thick = next(a for a in controls[0].attrs if a.attr == "fit_thickness")
    C.set_fit_value(scene, thick, 0.9)
    C.reset_all(scene, controls)
    assert scene.attr_spec(node, "fit_thickness").value == 0.0  # back to neutral
