"""Pure turntable geometry — orbit-camera positions + sprite-sheet cell layout.

No Maya, no Qt, so it runs in the headless suite. Two consumers:

* capture (``core.maya_publish.capture_turntable``) calls :func:`orbit_eyes` to place
  the viewport camera once per frame around the garment, then tiles the frames into a
  sprite sheet;
* the browser scrub widget (``ui.turntable.TurntableView``) calls :func:`cell_rect` to
  slice that sheet back into frames and :func:`frame_at` to map the cursor to a frame.

Keeping the math here (and out of the Maya/Qt boundary modules) makes it unit-testable.
"""
from __future__ import annotations

import math

from .. import config


def frame_count(cols: int = config.TURNTABLE_COLS,
                rows: int = config.TURNTABLE_ROWS) -> int:
    """Number of frames in a full ``cols`` x ``rows`` sheet (no blank cells)."""
    return cols * rows


def orbit_eyes(
    center: tuple[float, float, float],
    eye0: tuple[float, float, float],
    frames: int,
) -> list[tuple[float, float, float]]:
    """``frames`` camera eye positions orbiting ``center`` about the Y axis.

    Frame 0 is ``eye0`` itself; the rest sweep a full 360° at even steps, so the last
    frame leads seamlessly back into the first. ``eye0``'s height (Y) and its horizontal
    distance from ``center`` are preserved — only the azimuth changes.
    """
    cx, cy, cz = center
    ex, ey, ez = eye0
    dx, dz = ex - cx, ez - cz
    radius = math.hypot(dx, dz)
    base = math.atan2(dz, dx)
    eyes: list[tuple[float, float, float]] = []
    for i in range(max(0, frames)):
        angle = base + (2.0 * math.pi) * (i / frames)
        eyes.append((cx + radius * math.cos(angle), ey, cz + radius * math.sin(angle)))
    return eyes


def cell_rect(
    index: int,
    cols: int = config.TURNTABLE_COLS,
    cell: int = config.TURNTABLE_CELL,
) -> tuple[int, int, int, int]:
    """``(x, y, w, h)`` of frame ``index`` in a row-major sprite sheet."""
    row, col = divmod(index, cols)
    return (col * cell, row * cell, cell, cell)


def frame_at(fraction: float, frames: int) -> int:
    """Frame index for a horizontal position ``fraction`` (0..1) across the widget.

    Clamped to ``[0, frames - 1]`` so cursor positions exactly at the edges are valid.
    """
    if frames <= 0:
        return 0
    return max(0, min(frames - 1, int(fraction * frames)))
