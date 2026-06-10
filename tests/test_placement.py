"""Headless tests for the placement offset (pure transform on one node)."""
import _bootstrap  # noqa: F401
from _fake_scene import FakeScene

from snap_on_clothing.core.placement import (
    Placement, apply_placement, read_placement, reset_placement,
)


def _scene():
    s = FakeScene()
    s.add_node("coat:cloth_coat_A", "transform")
    return s


def test_identity_default():
    p = Placement()
    assert p.is_identity()
    assert p.scale == (1.0, 1.0, 1.0)
    assert not Placement(translate=(0.0, 1.0, 0.0)).is_identity()


def test_apply_and_read_roundtrip():
    scene = _scene()
    p = Placement(translate=(1.0, 2.0, 3.0), rotate=(0.0, 90.0, 0.0), scale=(1.0, 1.0, 1.1))
    apply_placement(scene, "coat:cloth_coat_A", p)
    back = read_placement(scene, "coat:cloth_coat_A")
    assert back == p


def test_apply_skips_locked_channel():
    scene = _scene()
    scene.lock("coat:cloth_coat_A", "scale")
    apply_placement(scene, "coat:cloth_coat_A",
                    Placement(translate=(5.0, 0.0, 0.0), scale=(2.0, 2.0, 2.0)))
    back = read_placement(scene, "coat:cloth_coat_A")
    assert back.translate == (5.0, 0.0, 0.0)
    assert back.scale == (1.0, 1.0, 1.0)  # locked scale untouched -> identity default


def test_pivot_applied_only_when_set():
    scene = _scene()
    apply_placement(scene, "coat:cloth_coat_A", Placement(pivot=(0.0, 10.0, 0.0)))
    assert scene.get_vector("coat:cloth_coat_A", "rotatePivot") == (0.0, 10.0, 0.0)


def test_reset_returns_identity():
    scene = _scene()
    apply_placement(scene, "coat:cloth_coat_A", Placement(translate=(9.0, 9.0, 9.0)))
    reset_placement(scene, "coat:cloth_coat_A")
    assert read_placement(scene, "coat:cloth_coat_A").is_identity()


def test_dict_roundtrip_with_and_without_pivot():
    p = Placement(translate=(1.0, 0.0, 0.0), pivot=(0.0, 2.0, 0.0))
    assert Placement.from_dict(p.to_dict()) == p
    q = Placement(rotate=(0.0, 45.0, 0.0))
    d = q.to_dict()
    assert "pivot" not in d
    assert Placement.from_dict(d) == q
