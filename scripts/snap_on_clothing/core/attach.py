"""Attach / detach lifecycle — ``connectAttr`` only, transactional (FR-3 / FR-5).

Attach is the one place that mutates the scene to bind a garment, and it does so
through exactly one mechanism: ``connectAttr`` from each GenHuman export-skeleton
joint to the asset's matching ``cloth_*`` joint (PRD §4/§10). No constraints,
utility, matrix, expression, or driven-key nodes are ever created.

The whole operation is transactional: all validation that can run before touching
the scene runs first (so a rejected asset leaves the scene byte-identical); after
import, any failure rolls back (break applied edges, delete the namespace),
honouring FR-2's "scene unchanged on failure".

Joint matching: a ``cloth_<name>`` joint connects iff ``<name>`` resolves to a
joint under the export-skeleton group (full DAG path — dual-skeleton safe, PRD §4).
Joints that don't resolve are treated as helper/secondary joints and left
unconnected and animator-accessible (Authoring Spec §5).
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from .. import config
from . import ma_parse
from .asset import ClothingAsset
from .registry import AttachedInstance, Connection, InstanceRegistry
from .scene import SceneGateway
from .validate import (
    ValidationReport,
    validate_asset_summary,
    validate_scene_preconditions,
)


@dataclass(frozen=True)
class PlannedConnection:
    src: str  # body joint plug, e.g. "<full path>.translate"
    dst: str  # cloth joint plug, e.g. "coat:cloth_spine_03.translate"


@dataclass
class AttachResult:
    ok: bool
    report: ValidationReport
    instance: AttachedInstance | None = None


@dataclass
class DetachResult:
    ok: bool
    report: ValidationReport
    broken: int = 0


_NS_INVALID = re.compile(r"[^A-Za-z0-9_]")


def sanitize_namespace(name: str) -> str:
    """Make a Maya-legal namespace token from an arbitrary instance name."""
    cleaned = _NS_INVALID.sub("_", name.strip())
    if cleaned and cleaned[0].isdigit():
        cleaned = "_" + cleaned
    return cleaned or "clothing"


class _Abort(Exception):
    """Internal: signal a post-import validation failure to trigger rollback."""


def plan_connections(
    summary: ma_parse.MaSummary,
    body_joints: dict[str, str],
    namespace: str,
    scene: SceneGateway,
) -> tuple[list[PlannedConnection], ValidationReport]:
    """Match ``cloth_*`` joints to body joints and validate each target plug."""
    report = ValidationReport()
    plan: list[PlannedConnection] = []
    matched = 0
    helpers: list[str] = []

    for cloth_joint in summary.cloth_joints():
        base = cloth_joint[len(config.CLOTH_PREFIX):]
        body_full = body_joints.get(base)
        if body_full is None:
            helpers.append(cloth_joint)  # secondary/helper joint, intentionally unconnected
            continue
        matched += 1
        dst_node = f"{namespace}:{cloth_joint}"
        if not scene.exists(dst_node):
            report.error("cloth_joint_missing",
                         f"imported joint '{dst_node}' not found after import", node=dst_node)
            continue
        for attr in config.CONNECT_ATTRS:
            dst_plug = f"{dst_node}.{attr}"
            if not scene.attr_exists(dst_node, attr):
                report.error("attr_missing", f"'{attr}' missing on '{dst_node}'", node=dst_plug)
                continue
            if scene.is_locked(dst_node, attr):
                report.error("attr_locked", f"'{attr}' is locked on '{dst_node}'", node=dst_plug,
                             fix=f"unlock {attr} on the cloth joint before attach")
                continue
            existing = scene.incoming(dst_node, attr)
            if existing is not None:
                report.error("attr_connected",
                             f"'{attr}' on '{dst_node}' already driven by '{existing}'",
                             node=dst_plug, fix="detach the existing connection first")
                continue
            plan.append(PlannedConnection(f"{body_full}.{attr}", dst_plug))

    if matched == 0:
        report.error("no_joint_match",
                     "no cloth_ joint matched a body joint under the export skeleton",
                     fix="ensure cloth joint names = 'cloth_' + exact body joint name")
    else:
        report.info("match_summary",
                    f"matched {matched} joint(s); {len(helpers)} helper joint(s) left unconnected")
    return plan, report


class AttachEngine:
    """Stateful attach/detach driver bound to a scene + an instance registry."""

    def __init__(self, scene: SceneGateway, registry: InstanceRegistry | None = None) -> None:
        self.scene = scene
        self.registry = registry or InstanceRegistry()

    # --- attach ---------------------------------------------------------------
    def attach(
        self,
        asset: ClothingAsset,
        namespace: str,
        *,
        export_group: str = config.EXPORT_SKELETON_GROUP,
    ) -> AttachResult:
        report = ValidationReport()
        namespace = sanitize_namespace(namespace)

        # 1) pre-scene validation — failure here means the scene is untouched
        summary = ma_parse.summarize_file(asset.ma_path)
        report.extend(validate_asset_summary(summary, asset.metadata))
        report.extend(validate_scene_preconditions(
            self.scene, namespace, asset.metadata,
            registered_namespaces=tuple(self.registry.namespaces()),
            export_group=export_group,
        ))
        if not report.ok:
            return AttachResult(False, report)

        # 2) import into the instance namespace
        try:
            self.scene.import_asset(str(asset.ma_path), namespace)
        except Exception as exc:  # noqa: BLE001 — surface any Maya import error
            report.error("import_failed", f"import failed: {exc}", node=str(asset.ma_path))
            return AttachResult(False, report)

        # 3) plan + apply connections, rolling back on any failure
        applied: list[PlannedConnection] = []
        try:
            self._align_root_group(namespace, export_group)
            body_joints = self._resolve_body_joints(export_group, report)
            plan, plan_report = plan_connections(summary, body_joints, namespace, self.scene)
            report.extend(plan_report)
            if not report.ok:
                raise _Abort()
            for pc in plan:
                self.scene.connect(pc.src, pc.dst)
                applied.append(pc)
        except _Abort:
            self._rollback(applied, namespace)
            return AttachResult(False, report)
        except Exception as exc:  # noqa: BLE001
            report.error("attach_failed", f"attach failed, rolled back: {exc}")
            self._rollback(applied, namespace)
            return AttachResult(False, report)

        # 4) record the instance
        meta = asset.metadata
        instance = AttachedInstance(
            namespace=namespace,
            asset_name=meta.asset_name if meta else asset.display_name,
            asset_type=meta.asset_type if meta else "unknown",
            ma_path=str(asset.ma_path),
            cloth_root=f"{namespace}:{config.ROOT_JOINT}",
            connections=[Connection(pc.src, pc.dst) for pc in applied],
        )
        self.registry.add(instance)
        report.info("attached", f"attached '{namespace}' with {len(applied)} connection(s)")
        return AttachResult(True, report, instance)

    def _align_root_group(self, namespace: str, export_group: str) -> None:
        """Place the garment's joint group on the rig's export-skeleton group frame.

        The export skeleton sits under a transformed group (``GenHuman_Joint_GRP`` is
        rotated -90 X to flip the FBX skeleton into Maya's Y-up). Attach connects only
        LOCAL joint transforms, so unless the garment's ``Rig_GRP`` shares that group's
        world frame, every connected joint is reproduced in the wrong frame and the
        whole garment lands rotated off the body. Matching the frame once, here, makes
        the local-transform connections reproduce the body pose exactly — and adapts to
        wherever this particular rig instance sits in the scene.
        """
        rig_group = f"{namespace}:{config.RIG_GROUP}"
        if self.scene.exists(rig_group) and self.scene.exists(export_group):
            self.scene.set_world_matrix(rig_group, self.scene.world_matrix(export_group))

    def _resolve_body_joints(self, export_group: str, report: ValidationReport) -> dict[str, str]:
        try:
            body_joints = self.scene.descendant_joints(export_group)
        except ValueError as exc:
            report.error("ambiguous_body_joint", str(exc), node=export_group)
            raise _Abort() from exc
        if not body_joints:
            report.error("no_body_joints",
                         f"no joints found under export group '{export_group}'",
                         node=export_group,
                         fix="verify EXPORT_SKELETON_GROUP is the correct export-skeleton path")
            raise _Abort()
        return body_joints

    def _rollback(self, applied: list[PlannedConnection], namespace: str) -> None:
        for pc in reversed(applied):
            try:
                if self.scene.is_connected(pc.src, pc.dst):
                    self.scene.disconnect(pc.src, pc.dst)
            except Exception:  # noqa: BLE001 — best-effort cleanup
                pass
        try:
            self.scene.remove_namespace(namespace)
        except Exception:  # noqa: BLE001
            pass

    # --- detach ---------------------------------------------------------------
    def detach(self, namespace: str) -> DetachResult:
        report = ValidationReport()
        namespace = sanitize_namespace(namespace)
        instance = self.registry.get(namespace)
        if instance is None:
            report.error("not_attached", f"no attached instance for namespace '{namespace}'",
                         node=namespace)
            return DetachResult(False, report)

        broken = 0
        for conn in instance.connections:
            try:
                if self.scene.is_connected(conn.src, conn.dst):
                    self.scene.disconnect(conn.src, conn.dst)
                    broken += 1
            except Exception as exc:  # noqa: BLE001
                report.warn("disconnect_failed",
                            f"could not break {conn.src} -> {conn.dst}: {exc}")

        try:
            self.scene.remove_namespace(namespace)
        except Exception as exc:  # noqa: BLE001
            report.error("ns_remove_failed", f"could not remove namespace '{namespace}': {exc}",
                         node=namespace)
            return DetachResult(False, report, broken)

        self.registry.remove(namespace)
        report.info("detached", f"detached '{namespace}', broke {broken} connection(s)")
        return DetachResult(True, report, broken)
