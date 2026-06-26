"""Headless tests for the pure turntable geometry (no Maya, no Qt)."""
import math

import _bootstrap  # noqa: F401

from outfitter import config
from outfitter.core import turntable as T


def test_frame_count_is_full_grid():
    assert T.frame_count(6, 4) == 24
    assert T.frame_count() == config.TURNTABLE_COLS * config.TURNTABLE_ROWS


def test_orbit_eyes_count_and_first_frame():
    center = (0.0, 1.0, 0.0)
    eye0 = (10.0, 5.0, 0.0)
    eyes = T.orbit_eyes(center, eye0, 24)
    assert len(eyes) == 24
    # frame 0 is eye0 itself (start of the sweep)
    assert eyes[0][0] == 10.0 and eyes[0][2] == 0.0


def test_orbit_eyes_preserves_height_and_radius():
    center = (2.0, 1.0, -3.0)
    eye0 = (12.0, 7.0, -3.0)  # radius 10 in XZ, height 7
    eyes = T.orbit_eyes(center, eye0, 8)
    for x, y, z in eyes:
        assert y == 7.0  # height never changes
        r = math.hypot(x - center[0], z - center[2])
        assert math.isclose(r, 10.0, abs_tol=1e-9)


def test_orbit_eyes_quarter_turn():
    # a full 360° over 4 frames -> frame 1 is a +90° rotation about Y
    center = (0.0, 0.0, 0.0)
    eyes = T.orbit_eyes(center, (10.0, 0.0, 0.0), 4)
    x, _, z = eyes[1]
    assert math.isclose(x, 0.0, abs_tol=1e-9)
    assert math.isclose(z, 10.0, abs_tol=1e-9)


def test_cell_rect_row_major():
    assert T.cell_rect(0, cols=6, cell=256) == (0, 0, 256, 256)
    assert T.cell_rect(5, cols=6, cell=256) == (5 * 256, 0, 256, 256)
    assert T.cell_rect(6, cols=6, cell=256) == (0, 256, 256, 256)  # wraps to row 1
    assert T.cell_rect(7, cols=6, cell=256) == (256, 256, 256, 256)


def test_frame_at_maps_and_clamps():
    assert T.frame_at(0.0, 24) == 0
    assert T.frame_at(0.999, 24) == 23
    assert T.frame_at(1.0, 24) == 23   # right edge clamps in-range
    assert T.frame_at(-0.5, 24) == 0   # left overshoot clamps to 0
    assert T.frame_at(0.5, 24) == 12
    assert T.frame_at(0.5, 0) == 0     # no frames -> 0, no crash