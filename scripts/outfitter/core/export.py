"""Genie export-readiness audit (FR-7 / M4).

Attach binds a garment to the body rig through ``connectAttr`` only: it
creates no DG nodes and never makes a rig attribute a *destination*. That is what
keeps a dressed scene exportable to Genie (.ma / USD / FBX / Alembic) with the
required node names preserved and the dependency graph lightweight.

This module *proves* that invariant on the live scene so the artist can confirm
export safety without leaving the tool. It is pure logic over a ``SceneGateway``
plus the attach :class:`InstanceRegistry`, so it runs headlessly in CI alongside
the rest of the core.

Audited (each failure is an ERROR unless noted):

  * **Genie node names preserved** - every name in ``required_nodes`` still
    exists. Empty list (the current default) ⇒ a single INFO note, no failure.
  * **Export skeleton intact** - ``export_group`` resolves to ≥1 joint.
  * **Connections are clothing-only** - every recorded edge has both attrs in
    ``CONNECT_ATTRS``, a destination inside its own instance namespace, and a
    source that is *not* inside any instance namespace (the rig drives clothing,
    never the reverse). Anything else means attach touched the rig.
  * **Namespace isolation** - no instance references a node living in another
    instance's namespace (multi-asset independence, FR-6).
"""
from __future__ import annotations

from dataclasses import dataclass

from .. import config
from .registry import InstanceRegistry
from .scene import SceneGateway
from .validate import ValidationReport

_CONNECT_ATTRS = frozenset(config.CONNECT_ATTRS)


@dataclass
class ExportAudit:
    """Outcome of :func:`audit_export_readiness`."""

    report: ValidationReport

    @property
    def ok(self) -> bool:
        return self.report.ok


def _split_plug(plug: str) -> tuple[str, str]:
    """Split ``node.attr`` into ``(node, attr)`` (attr = last dotted token)."""
    node, _, attr = plug.rpartition(".")
    return (node, attr) if node else (plug, "")


def _namespace_of(node: str, namespaces: set[str]) -> str | None:
    """The instance namespace owning ``node``, or ``None`` if it is a rig node."""
    for ns in namespaces:
        if node.startswith(f"{ns}:"):
            return ns
    return None


def audit_export_readiness(
    scene: SceneGateway,
    registry: InstanceRegistry,
    *,
    required_nodes: tuple[str, ...] = config.GENIE_REQUIRED_NODES,
    export_group: str = config.EXPORT_SKELETON_GROUP,
) -> ExportAudit:
    """Verify a dressed scene is still safe to export to Genie.

    ``export_group`` is the dressed rig's export-skeleton group: pass
    ``profile.export_group`` for the rig actually in the scene. The default is the seed
    GenHuman name, which is only right for a scene dressed with that rig.
    """
    report = ValidationReport()

    # 1) required Genie node names preserved
    if not required_nodes:
        report.info("genie_names_unset",
                    "no Genie-required node list configured - name-preservation "
                    "check skipped (GENIE_REQUIRED_NODES is empty)")
    else:
        for name in required_nodes:
            if not scene.exists(name):
                report.error("genie_node_missing",
                             f"required Genie node '{name}' is absent", node=name,
                             fix="attach must not rename/delete export nodes")

    # 2) export skeleton intact
    try:
        body_joints = scene.descendant_joints(export_group)
    except ValueError as exc:
        report.error("export_skeleton_ambiguous", str(exc), node=export_group)
        body_joints = {}
    if not body_joints:
        report.error("export_skeleton_missing",
                     f"no joints resolve under export group '{export_group}'",
                     node=export_group,
                     fix="verify the rig's export-skeleton group path")

    # 3) + 4) connection invariants per instance
    namespaces = set(registry.namespaces())
    for inst in registry.instances():
        ns = inst.namespace
        for conn in inst.connections:
            src_node, src_attr = _split_plug(conn.src)
            dst_node, dst_attr = _split_plug(conn.dst)

            if src_attr not in _CONNECT_ATTRS or dst_attr not in _CONNECT_ATTRS:
                report.error("non_transform_edge",
                             f"edge is not a transform-channel connection: "
                             f"{conn.src} -> {conn.dst}", node=inst.namespace,
                             fix="attach must connect only translate/rotate/scale")

            # destination must be this instance's clothing
            if _namespace_of(dst_node, namespaces) != ns:
                report.error("edge_dst_not_owned",
                             f"connection target '{dst_node}' is not in namespace "
                             f"'{ns}'", node=dst_node,
                             fix="attach must only drive its own clothing joints")

            # source must be a rig node, never another instance's clothing
            src_ns = _namespace_of(src_node, namespaces)
            if src_ns is not None:
                code = "edge_src_clothing" if src_ns == ns else "edge_cross_instance"
                report.error(code,
                             f"connection source '{src_node}' is clothing, not a "
                             f"rig joint (owner='{src_ns}')", node=src_node,
                             fix="rig joints drive clothing, never the reverse")

    if report.ok:
        report.info("export_ready",
                    f"{len(registry)} instance(s) bound by connectAttr only; "
                    f"rig + export node names intact")
    return ExportAudit(report)
