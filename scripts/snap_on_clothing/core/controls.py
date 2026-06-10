"""Discover an attached garment's fit controls and drive them (Authoring Spec §8).

Fit is delivered by deformers the *asset author* builds, driven by keyable,
user-defined float attributes on control nodes. This tool never builds that rig —
it only discovers the attributes (reading each one's min/max/default off the live
imported node) and writes values. Discovery is therefore a pure read over the
``SceneGateway``: it works on the in-memory test scene exactly as it does in Maya.

Convention (Authoring Spec §8):
- Control nodes are transforms whose short name ends in ``_ctrl`` under ``Ctrl_GRP``.
- The primary fit control is ``cloth_fit_ctrl``; its ``fit_``-prefixed attrs are the
  preferred surface (``fit_tightness``/``fit_thickness``/``fit_length`` + region variants).
- If an asset exposes no ``fit_`` attrs at all, fall back to surfacing every keyable
  custom numeric attr found on its ``*_ctrl`` nodes.
"""
from __future__ import annotations

from dataclasses import dataclass

from .. import config
from .scene import SceneGateway

# Attribute types we render as a slider. Anything else (bool/enum/string) is skipped.
_NUMERIC_TYPES = frozenset({"double", "float", "doubleLinear", "doubleAngle", "long", "short"})

# Fallback slider bounds when an attr declares no min/max (Authoring Spec §8 ranges).
_FALLBACK_MIN = -1.0
_FALLBACK_MAX = 1.0


def _short(addr: str) -> str:
    return addr.rsplit("|", 1)[-1].rsplit(":", 1)[-1]


def _label(attr: str) -> str:
    """``fit_waist_tightness`` -> ``Waist Tightness`` (drop the ``fit_`` prefix)."""
    base = attr[len(config.FIT_ATTR_PREFIX):] if attr.startswith(config.FIT_ATTR_PREFIX) else attr
    return " ".join(w[:1].upper() + w[1:] for w in base.split("_") if w) or attr


@dataclass(frozen=True)
class FitAttr:
    """One drivable fit attribute discovered on a control node."""

    node: str            # addressable node, e.g. "coat:cloth_fit_ctrl"
    attr: str            # "fit_tightness"
    label: str           # "Tightness"
    min: float | None    # declared minimum (None if unbounded)
    max: float | None    # declared maximum (None if unbounded)
    default: float       # neutral value (Authoring Spec §8: default == neutral)
    value: float         # current value
    is_convention: bool  # True iff fit_-prefixed (the preferred surface)

    @property
    def slider_min(self) -> float:
        return self.min if self.min is not None else _FALLBACK_MIN

    @property
    def slider_max(self) -> float:
        lo = self.slider_min
        hi = self.max if self.max is not None else _FALLBACK_MAX
        return hi if hi > lo else lo + 1.0

    def clamp(self, value: float) -> float:
        return max(self.slider_min, min(self.slider_max, value))


@dataclass(frozen=True)
class FitControl:
    """A control node and the fit attributes it exposes."""

    node: str                       # addressable, e.g. "coat:cloth_fit_ctrl"
    name: str                       # short name, e.g. "cloth_fit_ctrl"
    is_primary: bool                # True for cloth_fit_ctrl
    attrs: tuple[FitAttr, ...]


def discover_controls(scene: SceneGateway, namespace: str) -> list[FitControl]:
    """Find every ``*_ctrl`` node in ``namespace`` and its keyable numeric attrs.

    The primary ``cloth_fit_ctrl`` sorts first; remaining controls sort by name.
    Controls with no surfaceable attrs are dropped.
    """
    controls: list[FitControl] = []
    for node in scene.list_namespace_nodes(namespace):
        short = _short(node)
        if not short.endswith("_ctrl"):
            continue
        attrs: list[FitAttr] = []
        for attr in scene.list_keyable_user_attrs(node):
            spec = scene.attr_spec(node, attr)
            if spec.type not in _NUMERIC_TYPES:
                continue
            attrs.append(FitAttr(
                node=node,
                attr=attr,
                label=_label(attr),
                min=spec.min,
                max=spec.max,
                default=0.0 if spec.default is None else spec.default,
                value=0.0 if spec.value is None else spec.value,
                is_convention=attr.startswith(config.FIT_ATTR_PREFIX),
            ))
        if not attrs:
            continue
        is_primary = short == config.FIT_CTRL
        controls.append(FitControl(node=node, name=short, is_primary=is_primary,
                                   attrs=tuple(attrs)))

    controls.sort(key=lambda c: (not c.is_primary, c.name))
    return controls


def surfaced_fit_attrs(controls: list[FitControl]) -> list[FitAttr]:
    """The attrs the tool actually exposes, applying the prefer/fallback rule.

    Authoring Spec §8: prefer ``fit_``-prefixed convention attrs; only when none
    exist anywhere does the tool fall back to *all* keyable custom attrs.
    """
    convention = [a for c in controls for a in c.attrs if a.is_convention]
    if convention:
        return convention
    return [a for c in controls for a in c.attrs]


def set_fit_value(scene: SceneGateway, attr: FitAttr, value: float) -> float:
    """Write a fit value (clamped to the attr's range). Returns the applied value."""
    applied = attr.clamp(value)
    scene.set_attr(attr.node, attr.attr, applied)
    return applied


def reset_fit(scene: SceneGateway, attr: FitAttr) -> float:
    """Restore a fit attr to its authored neutral default. Returns that default."""
    scene.set_attr(attr.node, attr.attr, attr.default)
    return attr.default


def reset_all(scene: SceneGateway, controls: list[FitControl]) -> None:
    """Restore every surfaced fit attr to neutral."""
    for attr in surfaced_fit_attrs(controls):
        reset_fit(scene, attr)
