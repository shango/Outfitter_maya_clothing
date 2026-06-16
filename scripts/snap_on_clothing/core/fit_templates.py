"""Per-asset-type fit-rig templates — the *data* behind the scaffolder.

Pure: no Maya, no I/O. Describes, for each asset type, the ``fit_*`` attributes a
scaffolded ``cloth_fit_ctrl`` should carry and — for the transform-level ones — how
each drives the fit lattice via a Set-Driven-Key relationship. The Maya-side
:mod:`core.maya_fitrig` consumes these to build the rig; keeping the recipe here (and
not buried in ``cmds`` code) lets the headless suite verify the contract and lets the
ranges/behaviours be tuned without touching the Maya boundary.

Driver modes (how a key's ``amount`` maps to a lattice channel value):

* ``scale``  — ``neutral_scale[axis] * amount``   (squeeze/stretch the lattice)
* ``offset`` — ``neutral_translate[axis] + amount * neutral_scale[axis]``
               (slide the lattice, as a fraction of its own size — scale-independent)
* ``rotate`` — ``amount``                         (absolute degrees)

``region`` attrs (e.g. ``fit_brim_width``) deform individual lattice *points*, which
needs a per-garment point selection the scaffolder can't sensibly guess — it creates
the attribute but authors no SDK, leaving the rigger to point-key it by hand.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FitDriver:
    """One driven lattice channel for a fit attr (a single SDK relationship)."""

    channel: str  # lattice transform attr, e.g. "scaleX" / "translateY" / "rotateX"
    mode: str  # "scale" | "offset" | "rotate"
    keys: tuple[tuple[float, float], ...]  # (driver_value, amount) pairs, in order

    @property
    def axis(self) -> str:
        """Trailing axis letter of the channel ("X"/"Y"/"Z")."""
        return self.channel[-1]


@dataclass(frozen=True)
class FitAttrDef:
    """A single ``fit_*`` attribute on ``cloth_fit_ctrl``."""

    name: str
    min: float
    max: float
    default: float
    region: bool = False  # point-level: scaffolder creates the attr but authors no SDK
    drivers: tuple[FitDriver, ...] = ()


@dataclass(frozen=True)
class FitTemplate:
    """The full scaffold recipe for one asset type."""

    asset_type: str
    divisions: tuple[int, int, int]  # lattice divisions (S, T, U)
    attrs: tuple[FitAttrDef, ...]


# Reusable driver shapes -------------------------------------------------------
def _squeeze_xz() -> tuple[FitDriver, ...]:
    """Tighten/loosen the garment by scaling the lattice in X and Z."""
    keys = ((-1.0, 1.08), (0.0, 1.0), (1.0, 0.92))
    return (FitDriver("scaleX", "scale", keys), FitDriver("scaleZ", "scale", keys))


def _length_y(short: float = 0.9, long: float = 1.1) -> FitDriver:
    """Shorten/lengthen by scaling the lattice in Y."""
    return FitDriver("scaleY", "scale", ((-1.0, short), (0.0, 1.0), (1.0, long)))


# Per-type templates -----------------------------------------------------------
_HAT = (
    FitAttrDef("fit_tightness", -1.0, 1.0, 0.0, drivers=_squeeze_xz()),
    FitAttrDef("fit_height", -1.0, 1.0, 0.0, drivers=(
        FitDriver("translateY", "offset", ((-1.0, -0.15), (0.0, 0.0), (1.0, 0.15))),
    )),
    FitAttrDef("fit_tilt", -1.0, 1.0, 0.0, drivers=(
        FitDriver("rotateX", "rotate", ((-1.0, -12.0), (0.0, 0.0), (1.0, 12.0))),
    )),
    FitAttrDef("fit_brim_width", -1.0, 1.0, 0.0, region=True),
)

_COAT = (
    FitAttrDef("fit_tightness", -1.0, 1.0, 0.0, drivers=_squeeze_xz()),
    FitAttrDef("fit_length", -1.0, 1.0, 0.0, drivers=(_length_y(),)),
    FitAttrDef("fit_thickness", 0.0, 1.0, 0.0, region=True),
    FitAttrDef("fit_hem_length", -1.0, 1.0, 0.0, region=True),
    FitAttrDef("fit_collar_tightness", -1.0, 1.0, 0.0, region=True),
)

# Anything without a bespoke recipe gets a safe, useful baseline: overall
# tightness + length, both whole-lattice (no region guesswork).
_GENERIC = (
    FitAttrDef("fit_tightness", -1.0, 1.0, 0.0, drivers=_squeeze_xz()),
    FitAttrDef("fit_length", -1.0, 1.0, 0.0, drivers=(_length_y(),)),
)

_TEMPLATES: dict[str, FitTemplate] = {
    "hat": FitTemplate("hat", (2, 4, 2), _HAT),
    "coat": FitTemplate("coat", (2, 6, 2), _COAT),
}

_DEFAULT = FitTemplate("generic", (2, 4, 2), _GENERIC)


def fit_template(asset_type: str) -> FitTemplate:
    """The scaffold recipe for ``asset_type`` (case-insensitive); generic fallback.

    Unknown / blank types get :data:`_GENERIC` so the scaffolder always produces a
    working baseline fit rig the rigger can extend.
    """
    return _TEMPLATES.get((asset_type or "").strip().lower(), _DEFAULT)
