"""Scene access boundary between the pure attach/validate logic and Maya.

The validation rules, connection planning, transactional attach, and detach in
``validate.py`` / ``attach.py`` are valuable and must be unit-testable without
Maya. They therefore never call ``maya.cmds`` directly - they go through the
``SceneGateway`` Protocol defined here. ``MayaScene`` is the real implementation
(imports ``maya.cmds`` lazily); tests substitute an in-memory fake.

Addressing convention: methods take a node name and an attribute name separately;
attribute strings (``node.attr``) are only assembled where a DG edge is created.
Node names may be namespaced (``coat:cloth_spine_03``) and/or full DAG paths
(``|GenHuman|...|spine_03``) - the gateway is responsible for resolving them.
"""
from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class SceneGateway(Protocol):
    """Minimal scene operations the attach/validate core needs."""

    # --- existence / typing ---------------------------------------------------
    def exists(self, name: str) -> bool: ...
    def node_type(self, name: str) -> str: ...

    def descendant_joints(self, root: str) -> dict[str, str]:
        """Map ``short name -> full DAG path`` for joints under ``root``.

        Resolves the dual-skeleton ambiguity: only joints under the given
        (export-skeleton) group are returned, by full path. Empty if ``root``
        is absent. Raises ``ValueError`` if a short name is ambiguous *within*
        ``root`` (a real authoring error worth surfacing).
        """
        ...

    # --- attribute queries ----------------------------------------------------
    def attr_exists(self, node: str, attr: str) -> bool: ...
    def is_locked(self, node: str, attr: str) -> bool: ...
    def incoming(self, node: str, attr: str) -> str | None:
        """Source plug feeding ``node.attr`` (``'src.attr'``) or ``None``."""
        ...

    # --- DG mutation ----------------------------------------------------------
    def connect(self, src_attr: str, dst_attr: str) -> None: ...
    def disconnect(self, src_attr: str, dst_attr: str) -> None: ...
    def is_connected(self, src_attr: str, dst_attr: str) -> bool: ...

    # --- import / namespace ---------------------------------------------------
    def namespace_exists(self, namespace: str) -> bool: ...
    def import_asset(self, path: str, namespace: str) -> None:
        """Import ``path`` into its own ``namespace`` (no merge on clash)."""
        ...

    def remove_namespace(self, namespace: str) -> None:
        """Delete the namespace and everything in it (used by detach/rollback)."""
        ...

    # --- rig identification ---------------------------------------------------
    def rig_version(self, markers: tuple[str, ...]) -> str | None:
        """Detected version string of the rig in the scene, or ``None`` if undetectable.

        ``markers`` are the node names that identify the rig, from its profile
        (:attr:`core.rigs.RigProfile.markers`) - so this works for any registered rig,
        not just GenHuman.
        """
        ...

    def selected_nodes(self) -> list[str]:
        """Currently selected scene nodes (full DAG paths), or empty."""
        ...

    def resolve_export_group(self, selected_node: str, export_group: str) -> str | None:
        """Resolve the export-skeleton group of the rig that ``selected_node`` belongs to.

        Multi-rig disambiguation (PRD §4): a scene may hold several rigs, each imported
        under its own namespace. Given *any* node of a rig (the top group, the godnode, a
        joint - whatever the user selected), return the full DAG path of that rig's
        ``export_group`` (the short name from the chosen rig's profile), so attach binds
        to the intended rig. Returns ``None`` if no such group is found in the node's
        namespace (caller falls back to a root-level rig / surfaces an error).
        """
        ...

    # --- world placement ------------------------------------------------------
    def world_matrix(self, node: str) -> list[float]:
        """The node's world transform as a flat 16-float row-major matrix."""
        ...

    def set_world_matrix(self, node: str, matrix: list[float]) -> None:
        """Set the node's world transform from a flat 16-float matrix."""
        ...


class MayaScene:
    """Real ``maya.cmds`` implementation of :class:`SceneGateway`.

    ``maya.cmds`` is imported lazily so this module stays importable headlessly;
    only instantiating/using ``MayaScene`` requires a running Maya.
    """

    def __init__(self) -> None:
        import maya.cmds as cmds  # noqa: import guarded to keep core headless

        self._cmds = cmds

    def exists(self, name: str) -> bool:
        return bool(self._cmds.objExists(name))

    def node_type(self, name: str) -> str:
        return str(self._cmds.nodeType(name))

    def descendant_joints(self, root: str) -> dict[str, str]:
        if not self._cmds.objExists(root):
            return {}
        full_paths = self._cmds.listRelatives(
            root, allDescendents=True, type="joint", fullPath=True
        ) or []
        out: dict[str, str] = {}
        for path in full_paths:
            short = path.rsplit("|", 1)[-1].rsplit(":", 1)[-1]
            if short in out:
                raise ValueError(
                    f"ambiguous joint short name '{short}' under '{root}': "
                    f"{out[short]} and {path}"
                )
            out[short] = path
        return out

    def attr_exists(self, node: str, attr: str) -> bool:
        return bool(self._cmds.attributeQuery(attr, node=node, exists=True))

    def is_locked(self, node: str, attr: str) -> bool:
        return bool(self._cmds.getAttr(f"{node}.{attr}", lock=True))

    def incoming(self, node: str, attr: str) -> str | None:
        conns = self._cmds.listConnections(
            f"{node}.{attr}", source=True, destination=False, plugs=True
        )
        return conns[0] if conns else None

    def connect(self, src_attr: str, dst_attr: str) -> None:
        self._cmds.connectAttr(src_attr, dst_attr, force=False)

    def disconnect(self, src_attr: str, dst_attr: str) -> None:
        self._cmds.disconnectAttr(src_attr, dst_attr)

    def is_connected(self, src_attr: str, dst_attr: str) -> bool:
        return bool(self._cmds.isConnected(src_attr, dst_attr))

    def namespace_exists(self, namespace: str) -> bool:
        return bool(self._cmds.namespace(exists=namespace))

    def import_asset(self, path: str, namespace: str) -> None:
        self._cmds.file(
            path, i=True, namespace=namespace,
            mergeNamespacesOnClash=False, preserveReferences=False,
        )

    def remove_namespace(self, namespace: str) -> None:
        # delete the namespace AND its content (the imported asset nodes)
        self._cmds.namespace(removeNamespace=namespace, deleteNamespaceContent=True)

    def rig_version(self, markers: tuple[str, ...]) -> str | None:
        # PRD §9 open task: version-id method undefined. Best-effort: look for a
        # version string attr on any of the rig's marker nodes. Returns None when not
        # found so callers degrade to a warning rather than hard-failing.
        #
        # Two attribute names are accepted: 'rigVersion' (what a rig registered with this
        # tool should carry) and 'genHumanVersion' (what GenHuman rigs in the wild already
        # carry). Namespaced rigs are matched too, so an imported rig is still identified.
        for marker in markers:
            for node in ([marker] if self._cmds.objExists(marker) else
                         (self._cmds.ls(f"*:{marker}") or [])):
                for attr in ("rigVersion", "genHumanVersion"):
                    if self._cmds.attributeQuery(attr, node=node, exists=True):
                        val = self._cmds.getAttr(f"{node}.{attr}")
                        if val:
                            return str(val)
        return None

    def selected_nodes(self) -> list[str]:
        return list(self._cmds.ls(selection=True, long=True) or [])

    def world_matrix(self, node: str) -> list[float]:
        return [float(v) for v in self._cmds.xform(node, query=True, worldSpace=True, matrix=True)]

    def set_world_matrix(self, node: str, matrix: list[float]) -> None:
        self._cmds.xform(node, worldSpace=True, matrix=list(matrix))

    def resolve_export_group(self, selected_node: str, export_group: str) -> str | None:
        marker = export_group
        short = selected_node.rsplit("|", 1)[-1]
        if ":" in short:
            # Search the rig's top namespace, recursing into nested namespaces
            # (e.g. 'GenHuman_rig_v03:' contains 'GenHuman_rig_v03:GenHuman_rig:').
            top_ns = short.split(":", 1)[0]
            candidates = self._cmds.ls(
                f"{top_ns}:*", recursive=True, type="transform", long=True
            ) or []
        else:
            # Root-level rig (no namespace): the bare marker, if present.
            candidates = self._cmds.ls(marker, type="transform", long=True) or []
        for path in candidates:
            if path.rsplit("|", 1)[-1].rsplit(":", 1)[-1] == marker:
                return path
        return None
