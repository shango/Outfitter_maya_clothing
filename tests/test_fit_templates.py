"""Headless tests for the pure fit-rig templates (core.fit_templates).

The Maya-side scaffolder (core.maya_fitrig) can only be smoke-checked in Maya, but the
recipe it consumes lives here and is fully verifiable: every type yields a coherent set
of fit attrs, transform drivers reference real lattice channels, region attrs carry no
SDK, and unknown types fall back to a working generic baseline.
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

from snap_on_clothing import config
from snap_on_clothing.core import fit_templates as ft

_VALID_CHANNELS = {
    f"{kind}{axis}" for kind in ("scale", "translate", "rotate") for axis in "XYZ"
}
_VALID_MODES = {"scale", "offset", "rotate"}


def _all_templates():
    return [ft.fit_template(t) for t in config.ASSET_TYPES] + [ft.fit_template("nope")]


def test_known_types_get_bespoke_templates():
    assert ft.fit_template("hat").asset_type == "hat"
    assert ft.fit_template("coat").asset_type == "coat"


def test_unknown_or_blank_type_falls_back_to_generic():
    assert ft.fit_template("balaclava").asset_type == "generic"
    assert ft.fit_template("").asset_type == "generic"
    assert ft.fit_template(None).asset_type == "generic"


def test_lookup_is_case_insensitive():
    assert ft.fit_template("HAT").asset_type == "hat"
    assert ft.fit_template("  Coat ").asset_type == "coat"


def test_every_attr_name_uses_the_fit_prefix():
    for tpl in _all_templates():
        for a in tpl.attrs:
            assert a.name.startswith(config.FIT_ATTR_PREFIX), a.name


def test_defaults_lie_within_range():
    for tpl in _all_templates():
        for a in tpl.attrs:
            assert a.min <= a.default <= a.max, a.name


def test_region_attrs_have_no_drivers_and_transform_attrs_do():
    for tpl in _all_templates():
        for a in tpl.attrs:
            if a.region:
                assert a.drivers == (), f"{a.name} is region but carries drivers"
            else:
                assert a.drivers, f"{a.name} is transform-level but has no driver"


def test_drivers_reference_valid_channels_and_modes():
    for tpl in _all_templates():
        for a in tpl.attrs:
            for drv in a.drivers:
                assert drv.channel in _VALID_CHANNELS, drv.channel
                assert drv.mode in _VALID_MODES, drv.mode
                assert drv.axis in "XYZ"


def test_driver_keys_span_the_neutral_default():
    # Each driver must key the attr's own default value (so neutral has a defined pose).
    for tpl in _all_templates():
        for a in tpl.attrs:
            for drv in a.drivers:
                driver_vals = [k[0] for k in drv.keys]
                assert a.default in driver_vals, (a.name, drv.channel)
                assert len(drv.keys) >= 2, "need at least two keys to interpolate"


def test_hat_template_shape():
    hat = ft.fit_template("hat")
    names = [a.name for a in hat.attrs]
    assert names == ["fit_tightness", "fit_height", "fit_tilt", "fit_brim_width"]
    brim = next(a for a in hat.attrs if a.name == "fit_brim_width")
    assert brim.region is True
    assert len(hat.divisions) == 3 and all(d >= 2 for d in hat.divisions)


def test_generic_template_is_usable_baseline():
    gen = ft.fit_template("shoes")  # no bespoke recipe -> generic
    assert gen.asset_type == "generic"
    assert any(a.drivers for a in gen.attrs)  # at least one working knob


# --- driver math (core.maya_fitrig._channel_value is pure; cmds is lazy) ------
# A neutral lattice with a non-unit, off-origin bbox, to prove the math is
# relative to neutral (not absolute) for scale/offset and absolute for rotate.
_NEUTRAL = {
    "scaleX": 50.0, "scaleY": 100.0, "scaleZ": 30.0,
    "translateX": 5.0, "translateY": 80.0, "translateZ": -2.0,
}


def _channel_value(channel, mode, amount):
    from snap_on_clothing.core import maya_fitrig
    return maya_fitrig._channel_value(ft.FitDriver(channel, mode, ()), amount, _NEUTRAL)


def test_scale_driver_is_neutral_times_amount():
    # squeeze: factor 0.92 against a neutral scaleX of 50 -> 46.0
    assert _channel_value("scaleX", "scale", 0.92) == 50.0 * 0.92
    assert _channel_value("scaleY", "scale", 1.0) == 100.0  # neutral preserved at factor 1


def test_offset_driver_slides_as_a_fraction_of_neutral_scale():
    # translateY = neutral_translate + amount * neutral_scale; scale-independent slide
    assert _channel_value("translateY", "offset", 0.15) == 80.0 + 0.15 * 100.0
    assert _channel_value("translateY", "offset", 0.0) == 80.0  # neutral at amount 0


def test_rotate_driver_is_absolute_degrees():
    assert _channel_value("rotateX", "rotate", 12.0) == 12.0
    assert _channel_value("rotateX", "rotate", 0.0) == 0.0


def test_unknown_driver_mode_raises():
    with pytest.raises(ValueError):
        _channel_value("scaleX", "warp", 1.0)


# --- shared SDK authoring (maya_fitrig.author_fit_rig, via a fake cmds) --------
class _FakeCmds:
    """Minimal cmds stand-in recording the calls author_fit_rig makes."""

    def __init__(self, seed):
        self.attrs = dict(seed)   # plug -> value (seed the lattice's neutral scale)
        self.added = []           # (node, longName)
        self.sdk = []             # (driven_plug, driver_plug)

    def addAttr(self, node, longName=None, **kw):
        self.added.append((node, longName))
        self.attrs[f"{node}.{longName}"] = kw.get("defaultValue", 0.0)

    def getAttr(self, plug):
        return self.attrs.get(plug, 0.0)

    def setAttr(self, plug, value):
        self.attrs[plug] = value

    def setDrivenKeyframe(self, plug, currentDriver=None):
        self.sdk.append((plug, currentDriver))


def _seed_neutral():
    # a non-unit, off-origin objectCentered lattice (bbox-sized neutral scale)
    seed = {f"lat.scale{a}": s for a, s in zip("XYZ", (50.0, 100.0, 30.0))}
    seed.update({f"lat.translate{a}": 0.0 for a in "XYZ"})
    return seed


def test_author_fit_rig_keys_transform_attrs_and_skips_region():
    from snap_on_clothing.core import maya_fitrig
    fake = _FakeCmds(_seed_neutral())
    tpl = ft.fit_template("coat")
    keyed, region = maya_fitrig.author_fit_rig(fake, "ctrl", "lat", tpl)

    assert keyed == ["fit_tightness", "fit_length"]
    assert region == ["fit_thickness", "fit_hem_length", "fit_collar_tightness"]
    # every attr was added to the control
    assert {n for _, n in fake.added} == {a.name for a in tpl.attrs}
    # SDKs authored on the squeeze + length channels, driven by the right attr
    driven = {(p.split(".")[1], d) for p, d in fake.sdk}
    assert ("scaleX", "ctrl.fit_tightness") in driven
    assert ("scaleZ", "ctrl.fit_tightness") in driven
    assert ("scaleY", "ctrl.fit_length") in driven
    # values are driven RELATIVE to neutral (50 * 0.92 squeeze on the last tightness key)
    assert fake.attrs["lat.scaleX"] == 50.0 * 0.92
    # the control is left at neutral defaults
    assert fake.attrs["ctrl.fit_tightness"] == 0.0
    assert fake.attrs["ctrl.fit_length"] == 0.0


def test_author_fit_rig_region_only_template_authors_no_sdk():
    from snap_on_clothing.core import maya_fitrig
    from snap_on_clothing.core.fit_templates import FitAttrDef, FitTemplate
    tpl = FitTemplate("regiony", (2, 2, 2), (FitAttrDef("fit_only", 0.0, 1.0, 0.0, region=True),))
    fake = _FakeCmds(_seed_neutral())
    keyed, region = maya_fitrig.author_fit_rig(fake, "ctrl", "lat", tpl)
    assert keyed == [] and region == ["fit_only"]
    assert fake.sdk == []  # nothing keyed
