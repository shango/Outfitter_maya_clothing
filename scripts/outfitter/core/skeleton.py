"""Canonical GenHuman ``cloth_*`` skeleton - pure loader + model.

There is exactly one GenHuman rig, therefore exactly one ``cloth_*`` export skeleton.
Rather than make every rigger import the rig and duplicate / rename / prune it by hand,
that skeleton is persisted once - ``data/cloth_skeleton.json``, extracted from the
verified ``assets/trench_coat_A`` asset (body-derived export joints only; garment helper
joints like ``cloth_coatTail_*`` excluded) - and rebuilt in-scene with one button by
:mod:`core.maya_skeleton`. This module loads and validates that data with no Maya; the
Maya boundary only replays it.

The joints carry their orientation in ``rotate`` (the rig has no ``jointOrient``); the
``Rig_GRP`` frame carries the ``-90 X`` so the joints stand upright on the body and
attach can reproduce the body pose from LOCAL transforms alone.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from .. import config

_Vec3 = tuple[float, float, float]


@dataclass(frozen=True)
class JointSpec:
    """One ``cloth_*`` joint's rest state, relative to its parent."""

    name: str
    parent: str
    translate: _Vec3 = (0.0, 0.0, 0.0)
    rotate: _Vec3 = (0.0, 0.0, 0.0)
    joint_orient: _Vec3 = (0.0, 0.0, 0.0)
    scale: _Vec3 = (1.0, 1.0, 1.0)
    radius: float = 1.0
    segment_scale_compensate: bool = True
    rotate_order: int = 0


@dataclass(frozen=True)
class SkeletonSpec:
    """The whole canonical skeleton: a framed root group + its joint hierarchy."""

    root_group: str
    root_group_rotate: _Vec3
    root_joint: str
    joints: tuple[JointSpec, ...]

    @property
    def names(self) -> tuple[str, ...]:
        return tuple(j.name for j in self.joints)


def skeleton_file() -> Path:
    """Path to the persisted skeleton data (ships inside the package)."""
    return config.package_dir() / "data" / "cloth_skeleton.json"


def _v3(val, default: _Vec3) -> _Vec3:
    if not val:
        return default
    return (float(val[0]), float(val[1]), float(val[2]))


@lru_cache(maxsize=1)
def load_cloth_skeleton() -> SkeletonSpec:
    """Load + cache the canonical skeleton from :func:`skeleton_file`."""
    data = json.loads(skeleton_file().read_text())
    joints = tuple(
        JointSpec(
            name=j["name"],
            parent=j["parent"],
            translate=_v3(j.get("t"), (0.0, 0.0, 0.0)),
            rotate=_v3(j.get("r"), (0.0, 0.0, 0.0)),
            joint_orient=_v3(j.get("jo"), (0.0, 0.0, 0.0)),
            scale=_v3(j.get("s"), (1.0, 1.0, 1.0)),
            radius=float(j.get("radi", 1.0)),
            segment_scale_compensate=bool(j.get("ssc", True)),
            rotate_order=int(j.get("ro", 0)),
        )
        for j in data["joints"]
    )
    return SkeletonSpec(
        root_group=data.get("root_group", "Rig_GRP"),
        root_group_rotate=_v3(data.get("root_group_rotate"), (-90.0, 0.0, 0.0)),
        root_joint=data.get("root_joint", config.ROOT_JOINT),
        joints=joints,
    )


_REGEN_COMMENT = (
    "Canonical GenHuman cloth_* skeleton. Regenerated from the rig in-scene via the "
    "Publish tab ('Regenerate skeleton data'); see core.maya_skeleton. Body-derived "
    "export joints, each at its captured LOCAL transform; rebuilt by "
    "core.maya_skeleton.build_cloth_skeleton. Prefer regenerating over hand-editing."
)


def to_json_dict(spec: SkeletonSpec) -> dict:
    """Serialize a :class:`SkeletonSpec` to the on-disk JSON shape (inverse of load).

    Every joint carries its full transform explicitly (no zero-omission) so a captured
    skeleton round-trips deterministically through :func:`load_cloth_skeleton`.
    """
    joints = [
        {
            "name": j.name,
            "parent": j.parent,
            "t": list(j.translate),
            "r": list(j.rotate),
            "jo": list(j.joint_orient),
            "s": list(j.scale),
            "radi": j.radius,
            "ssc": j.segment_scale_compensate,
            "ro": j.rotate_order,
        }
        for j in spec.joints
    ]
    return {
        "_comment": _REGEN_COMMENT,
        "root_group": spec.root_group,
        "root_group_rotate": list(spec.root_group_rotate),
        "root_joint": spec.root_joint,
        "joints": joints,
    }


def write_skeleton(spec: SkeletonSpec, dest: Path | None = None) -> Path:
    """Write ``spec`` to ``dest`` (defaults to the shipped :func:`skeleton_file`) as JSON.

    Clears the :func:`load_cloth_skeleton` cache so the next load reflects the new data.
    The spec is validated first; an invalid skeleton is never written.
    """
    errors = validate_skeleton(spec)
    if errors:
        raise ValueError("refusing to write invalid skeleton:\n  " + "\n  ".join(errors))
    path = Path(dest) if dest is not None else skeleton_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_json_dict(spec), indent=1))
    load_cloth_skeleton.cache_clear()
    return path


@dataclass(frozen=True)
class PrunePlan:
    """What pruning the unweighted ``cloth_*`` joints would do - computed with no Maya.

    ``delete`` is in deletion order (a joint always precedes its parent), so replaying it
    only ever removes leaves. ``kept_unweighted`` are the interior joints that carry no
    skin weight but are kept anyway because they have skinned descendants - deleting and
    reparenting them would change their children's LOCAL transforms and break the
    body-mirrored chain attach depends on.
    """

    delete: tuple[str, ...]
    kept_unweighted: tuple[str, ...]
    survivors: tuple[str, ...]

    @property
    def is_noop(self) -> bool:
        return not self.delete


def plan_prune(parents: dict, influences, root_joint: str = config.ROOT_JOINT) -> PrunePlan:
    """Select the ``cloth_*`` joints that are safe to delete after skinning.

    ``parents`` maps each in-scene ``cloth_*`` joint (short name) to its parent's short
    name; ``influences`` is the set of joints actually bound by a skinCluster. Pure - no
    Maya: the wrapper in :mod:`core.maya_skeleton` gathers both from the scene and
    replays the returned :class:`PrunePlan`.

    The one sound rule (see the attach invariant in the module docstring): remove only a
    **leaf** joint that is neither a skin influence nor ``root_joint``; deleting it may
    expose its parent as a new leaf, so repeat until stable. Interior joints are kept
    regardless of weight. A naive "delete everything unweighted" instead would tear holes
    in the hierarchy - this never does.
    """
    influences = set(influences)
    alive = set(parents)
    delete: list[str] = []

    changed = True
    while changed:
        changed = False
        # parents referenced by a surviving joint => those names are interior (have a child)
        interior = {parents[n] for n in alive}
        for n in sorted(alive):
            if n == root_joint or n in influences or n in interior:
                continue
            delete.append(n)
            alive.discard(n)
            changed = True

    kept_unweighted = tuple(
        sorted(n for n in alive if n != root_joint and n not in influences))
    return PrunePlan(
        delete=tuple(delete),
        kept_unweighted=kept_unweighted,
        survivors=tuple(sorted(alive)),
    )


def validate_skeleton(spec: SkeletonSpec) -> list[str]:
    """Structural problems with the skeleton data (empty list ⇒ OK).

    Guards the build order + naming contract: unique names, every parent resolves to
    the root group or an earlier joint, the root joint is present, and every joint
    carries the ``cloth_`` prefix.
    """
    errors: list[str] = []
    seen: set[str] = set()
    for j in spec.joints:
        if j.name in seen:
            errors.append(f"duplicate joint: {j.name}")
        if not j.name.startswith(config.CLOTH_PREFIX):
            errors.append(f"{j.name}: missing {config.CLOTH_PREFIX!r} prefix")
        # parent must already exist (root group or a joint defined before this one)
        if j.parent != spec.root_group and j.parent not in seen:
            errors.append(f"{j.name}: parent {j.parent!r} not defined before it")
        seen.add(j.name)
    if spec.root_joint not in seen:
        errors.append(f"root joint {spec.root_joint!r} missing")
    return errors
