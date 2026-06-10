"""Save / load fit + placement presets for an attached garment instance.

A preset is a portable snapshot of the *artist-tunable* state of one instance: the
value of every surfaced fit attribute plus an optional placement offset. It does
**not** capture the snap connections (those are deterministic from the asset +
rig) — only the values an artist dialled in, so a look can be reproduced or shared.

Portability across instances: node addresses are stored **namespace-relative**
(``cloth_fit_ctrl``, not ``coat:cloth_fit_ctrl``). Applying a preset re-prefixes
with the target instance's namespace, so a preset captured from ``coat`` applies
cleanly to a re-attached ``coat1``. Persisted as a small JSON sidecar.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from . import controls as _controls
from .placement import Placement
from .registry import AttachedInstance
from .scene import SceneGateway
from .validate import ValidationReport

SCHEMA_VERSION = 1


def _local(addr: str, namespace: str) -> str:
    """Strip a leading ``namespace:`` so the address is portable across instances."""
    prefix = f"{namespace}:"
    return addr[len(prefix):] if addr.startswith(prefix) else addr.rsplit(":", 1)[-1]


@dataclass(frozen=True)
class FitValue:
    """One captured fit attribute value, addressed namespace-relative."""

    control: str  # local control node name, e.g. "cloth_fit_ctrl"
    attr: str     # "fit_tightness"
    value: float

    def to_dict(self) -> dict:
        return {"control": self.control, "attr": self.attr, "value": self.value}

    @classmethod
    def from_dict(cls, data: dict) -> "FitValue":
        return cls(control=data["control"], attr=data["attr"], value=float(data["value"]))


@dataclass(frozen=True)
class Preset:
    """A reproducible fit/placement snapshot for one asset."""

    name: str
    asset_type: str
    fit: tuple[FitValue, ...]
    placement: Placement | None = None
    placement_node: str | None = None  # local name of the placement transform
    schema: int = SCHEMA_VERSION

    def to_dict(self) -> dict:
        d: dict = {
            "schema": self.schema,
            "name": self.name,
            "assetType": self.asset_type,
            "fit": [fv.to_dict() for fv in self.fit],
        }
        if self.placement is not None:
            d["placement"] = self.placement.to_dict()
            d["placementNode"] = self.placement_node
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Preset":
        placement = data.get("placement")
        return cls(
            name=data.get("name", "preset"),
            asset_type=data.get("assetType", "unknown"),
            fit=tuple(FitValue.from_dict(f) for f in data.get("fit", [])),
            placement=Placement.from_dict(placement) if placement is not None else None,
            placement_node=data.get("placementNode"),
            schema=int(data.get("schema", SCHEMA_VERSION)),
        )

    def save(self, path: Path) -> Path:
        path = Path(path)
        path.write_text(json.dumps(self.to_dict(), indent=2))
        return path

    @classmethod
    def load(cls, path: Path) -> "Preset":
        return cls.from_dict(json.loads(Path(path).read_text()))


def capture_preset(
    name: str,
    scene: SceneGateway,
    instance: AttachedInstance,
    *,
    placement_node: str | None = None,
) -> Preset:
    """Snapshot the surfaced fit values (and optional placement) of an instance."""
    namespace = instance.namespace
    found = _controls.discover_controls(scene, namespace)
    fit = tuple(
        FitValue(_local(a.node, namespace), a.attr, a.value)
        for a in _controls.surfaced_fit_attrs(found)
    )
    placement: Placement | None = None
    local_node: str | None = None
    if placement_node is not None and scene.exists(placement_node):
        from .placement import read_placement

        placement = read_placement(scene, placement_node)
        local_node = _local(placement_node, namespace)
    return Preset(
        name=name,
        asset_type=instance.asset_type,
        fit=fit,
        placement=placement,
        placement_node=local_node,
    )


def apply_preset(
    scene: SceneGateway,
    preset: Preset,
    namespace: str,
    *,
    report: ValidationReport | None = None,
) -> ValidationReport:
    """Re-apply a preset's values to the instance in ``namespace``.

    Missing controls/attrs become warnings (the asset may have changed) rather
    than hard errors, so a partially-matching preset still applies what it can.
    """
    report = report or ValidationReport()
    applied = 0
    for fv in preset.fit:
        node = f"{namespace}:{fv.control}"
        if not scene.exists(node):
            report.warn("preset_control_missing",
                        f"control '{fv.control}' not in instance '{namespace}'", node=node)
            continue
        if not scene.attr_exists(node, fv.attr):
            report.warn("preset_attr_missing",
                        f"attr '{fv.attr}' not on '{node}'", node=f"{node}.{fv.attr}")
            continue
        spec = scene.attr_spec(node, fv.attr)
        value = fv.value
        if spec.min is not None:
            value = max(spec.min, value)
        if spec.max is not None:
            value = min(spec.max, value)
        scene.set_attr(node, fv.attr, value)
        applied += 1

    if preset.placement is not None and preset.placement_node is not None:
        from .placement import apply_placement

        node = f"{namespace}:{preset.placement_node}"
        if scene.exists(node):
            apply_placement(scene, node, preset.placement)
            applied += 1
        else:
            report.warn("preset_placement_missing",
                        f"placement node '{preset.placement_node}' not in '{namespace}'",
                        node=node)

    report.info("preset_applied", f"applied {applied} value(s) from preset '{preset.name}'")
    return report
