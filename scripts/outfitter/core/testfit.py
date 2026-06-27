"""In-scene skinning test - plan the body→``cloth_*`` connections (pure, headless).

Before publishing, the rigger needs to confirm the garment deforms correctly. They
already fit it on the GenHuman body that is *still in the authoring scene*, so the
test is simply: drive the ``cloth_*`` skeleton from that body, pose it, watch the
mesh follow - then disconnect so the joints go static and publish-safe again.

This is authoring-time :mod:`core.attach`: the **same** ``connectAttr`` body→cloth
``{translate,rotate,scale}`` plugs as production attach, by the **same** name match
(``cloth_<base>`` connects iff ``<base>`` is a body joint), minus the import and
namespace management (the body is already here, in the root namespace). The matching
and the skip rules (locked / already-driven plugs) are pure and decided here; the
live-Maya half (:mod:`core.maya_testfit`) gathers the facts and applies the plan.
"""
from __future__ import annotations

from dataclasses import dataclass

from .. import config


def body_morph_value(gender: str) -> float:
    """The ``GH_Body_morph`` value that puts the GenHuman body into ``gender`` (M14).

    The tool ships one rig and flips this switch (female = base, male = full morph), so
    the loaded test body matches the garment variant being authored. Raises ``ValueError``
    on an unknown gender so the caller surfaces it rather than silently loading the base.
    """
    key = gender.strip().lower()
    try:
        return config.GENDER_BODY_MORPH[key]
    except KeyError:
        valid = ", ".join(config.GENDER_BODY_MORPH)
        raise ValueError(f"unknown gender '{gender}' - expected one of: {valid}") from None


@dataclass(frozen=True)
class TestFitConnection:
    """One planned edge: a body joint plug drives a cloth joint plug."""

    src: str  # body joint plug, e.g. "|GenHuman_Joint_GRP|spine_01.translate"
    dst: str  # cloth joint plug, e.g. "cloth_spine_01.translate"


@dataclass(frozen=True)
class TestFitSkip:
    """A cloth plug that couldn't be connected, with why."""

    plug: str
    reason: str  # "locked" | "driven"


@dataclass(frozen=True)
class TestFitPlan:
    """The decided connect plan: edges to make, plus what was skipped / unmatched."""

    connections: tuple[TestFitConnection, ...]
    skipped: tuple[TestFitSkip, ...]
    matched_joints: tuple[str, ...]    # cloth joints with a body match
    unmatched_joints: tuple[str, ...]  # cloth joints with no body match (helper joints)

    @property
    def is_empty(self) -> bool:
        return not self.connections


def plan_test_fit(
    cloth_nodes: dict[str, str],
    body_joints: dict[str, str],
    *,
    locked: frozenset[str] | set[str] = frozenset(),
    driven: frozenset[str] | set[str] = frozenset(),
    connect_attrs: tuple[str, ...] = config.CONNECT_ATTRS,
    cloth_prefix: str = config.CLOTH_PREFIX,
) -> TestFitPlan:
    """Decide which body→cloth connections the skinning test should make.

    ``cloth_nodes`` maps each in-scene cloth joint's short name (``cloth_spine_01``) to
    its node address; ``body_joints`` maps each body joint's *base* name (``spine_01``)
    to its node address. A ``cloth_<base>`` joint is driven iff ``<base>`` is a body
    joint - identical to attach's matching. ``locked`` / ``driven`` are the cloth plugs
    (``"node.attr"``) to skip: a locked plug can't be connected, an already-driven plug
    must not be stolen (it's how re-running stays idempotent). Cloth joints with no body
    match are helper joints, reported as ``unmatched`` and left animator-accessible.
    """
    connections: list[TestFitConnection] = []
    skipped: list[TestFitSkip] = []
    matched: list[str] = []
    unmatched: list[str] = []

    for short in sorted(cloth_nodes):
        if not short.startswith(cloth_prefix):
            continue
        base = short[len(cloth_prefix):]
        body = body_joints.get(base)
        if body is None:
            unmatched.append(short)
            continue
        matched.append(short)
        dst_node = cloth_nodes[short]
        for attr in connect_attrs:
            dst_plug = f"{dst_node}.{attr}"
            if dst_plug in locked:
                skipped.append(TestFitSkip(dst_plug, "locked"))
                continue
            if dst_plug in driven:
                skipped.append(TestFitSkip(dst_plug, "driven"))
                continue
            connections.append(TestFitConnection(f"{body}.{attr}", dst_plug))

    return TestFitPlan(
        connections=tuple(connections),
        skipped=tuple(skipped),
        matched_joints=tuple(matched),
        unmatched_joints=tuple(unmatched),
    )
