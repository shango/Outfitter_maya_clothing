"""Per-instance placement offset — a pure transform nudge above the garment.

After a garment is snapped on, an artist may need to nudge the whole asset to
fine-tune fit (a hat sitting a touch high, a coat rotated slightly). Placement is
just translate/rotate/scale (and an optional rotate pivot / "anchor") written to a
single transform node — the asset's offset/root transform. It builds no network
and creates no nodes; it only reads and writes that transform through the
``SceneGateway`` so it is unit-testable headlessly.

The placement node is chosen by the caller (UI/engine); this module is agnostic
about which transform it is, which keeps it a pure value-object + apply/read pair.
"""
from __future__ import annotations

from dataclasses import dataclass

from .scene import SceneGateway

Vec3 = tuple[float, float, float]

_ZERO: Vec3 = (0.0, 0.0, 0.0)
_ONE: Vec3 = (1.0, 1.0, 1.0)


def _vec(value) -> Vec3:
    return (float(value[0]), float(value[1]), float(value[2]))


@dataclass(frozen=True)
class Placement:
    """A transform offset applied to a garment instance's placement node."""

    translate: Vec3 = _ZERO
    rotate: Vec3 = _ZERO
    scale: Vec3 = _ONE
    pivot: Vec3 | None = None  # rotate pivot ("anchor"); None = leave untouched

    def is_identity(self) -> bool:
        return (
            self.translate == _ZERO
            and self.rotate == _ZERO
            and self.scale == _ONE
            and (self.pivot is None or self.pivot == _ZERO)
        )

    def to_dict(self) -> dict:
        d: dict = {
            "translate": list(self.translate),
            "rotate": list(self.rotate),
            "scale": list(self.scale),
        }
        if self.pivot is not None:
            d["pivot"] = list(self.pivot)
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "Placement":
        pivot = data.get("pivot")
        return cls(
            translate=_vec(data.get("translate", _ZERO)),
            rotate=_vec(data.get("rotate", _ZERO)),
            scale=_vec(data.get("scale", _ONE)),
            pivot=_vec(pivot) if pivot is not None else None,
        )


def read_placement(scene: SceneGateway, node: str) -> Placement:
    """Snapshot the current transform of ``node`` as a :class:`Placement`."""
    return Placement(
        translate=_vec(scene.get_vector(node, "translate")),
        rotate=_vec(scene.get_vector(node, "rotate")),
        scale=_vec(scene.get_vector(node, "scale")),
    )


def apply_placement(scene: SceneGateway, node: str, placement: Placement) -> None:
    """Write a :class:`Placement` onto ``node``. Skips any locked channel.

    Locked channels are silently skipped rather than erroring: placement is a
    convenience nudge, and an author may legitimately lock e.g. scale.
    """
    for attr, value in (
        ("translate", placement.translate),
        ("rotate", placement.rotate),
        ("scale", placement.scale),
    ):
        if not scene.is_locked(node, attr):
            scene.set_vector(node, attr, value)
    if placement.pivot is not None and not scene.is_locked(node, "rotatePivot"):
        scene.set_vector(node, "rotatePivot", placement.pivot)


def reset_placement(scene: SceneGateway, node: str) -> None:
    """Return ``node`` to the identity transform (no offset)."""
    apply_placement(scene, node, Placement())
