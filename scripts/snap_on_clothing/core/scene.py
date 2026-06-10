"""Scene access boundary between the pure attach/validate logic and Maya.

The validation rules, connection planning, transactional attach, and detach in
``validate.py`` / ``attach.py`` are valuable and must be unit-testable without
Maya. They therefore never call ``maya.cmds`` directly — they go through the
``SceneGateway`` Protocol defined here. ``MayaScene`` is the real implementation
(imports ``maya.cmds`` lazily); tests substitute an in-memory fake.

Addressing convention: methods take a node name and an attribute name separately;
attribute strings (``node.attr``) are only assembled where a DG edge is created.
Node names may be namespaced (``coat:cloth_spine_03``) and/or full DAG paths
(``|GenHuman|...|spine_03``) — the gateway is responsible for resolving them.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class AttrSpec:
    """Snapshot of one attribute's UI-relevant metadata (M3 fit controls).

    ``min``/``max``/``default`` are ``None`` when the attribute declares no such
    bound (the tool falls back to convention ranges). ``value`` is the current
    value, ``None`` if it could not be read.
    """

    name: str
    type: str
    keyable: bool
    min: float | None
    max: float | None
    default: float | None
    value: float | None


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
    def genhuman_version(self) -> str | None:
        """Detected GenHuman rig version string, or ``None`` if undetectable."""
        ...

    def selected_nodes(self) -> list[str]:
        """Currently selected scene nodes (full DAG paths), or empty."""
        ...

    def resolve_export_group(self, selected_node: str) -> str | None:
        """Resolve the export-skeleton group of the rig that ``selected_node`` belongs to.

        Multi-rig disambiguation (PRD §4): a scene may hold several GenHuman rigs,
        each imported under its own namespace. Given *any* node of a rig (the top
        group, the godnode, a joint — whatever the user selected), return the full
        DAG path of that rig's ``EXPORT_SKELETON_GROUP``, so attach binds to the
        intended rig. Returns ``None`` if no such group is found in the node's
        namespace (caller falls back to a root-level rig / surfaces an error).
        """
        ...

    # --- control / fit-attr discovery + placement (M3) ------------------------
    def list_namespace_nodes(self, namespace: str) -> list[str]:
        """All node names belonging to ``namespace`` (addressable as returned)."""
        ...

    def list_keyable_user_attrs(self, node: str) -> list[str]:
        """User-defined keyable attribute names on ``node`` (declaration order)."""
        ...

    def attr_spec(self, node: str, attr: str) -> AttrSpec:
        """Type / keyable / min / max / default / current value of one attr."""
        ...

    def set_attr(self, node: str, attr: str, value: float) -> None:
        """Set a scalar attribute value."""
        ...

    def get_vector(self, node: str, attr: str) -> tuple[float, float, float]:
        """Read a 3-float compound (translate / rotate / scale / pivot)."""
        ...

    def set_vector(self, node: str, attr: str, value: tuple[float, float, float]) -> None:
        """Set a 3-float compound."""
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

    def genhuman_version(self) -> str | None:
        # PRD §9 open task: version-id method undefined. Best-effort: look for a
        # 'genHumanVersion' string attr on any rig marker node. Returns None when
        # not found so callers degrade to a warning rather than hard-failing.
        from .. import config

        for marker in config.RIG_MARKERS:
            if self._cmds.objExists(marker) and self._cmds.attributeQuery(
                "genHumanVersion", node=marker, exists=True
            ):
                val = self._cmds.getAttr(f"{marker}.genHumanVersion")
                return str(val) if val else None
        return None

    def selected_nodes(self) -> list[str]:
        return list(self._cmds.ls(selection=True, long=True) or [])

    def resolve_export_group(self, selected_node: str) -> str | None:
        from .. import config

        marker = config.EXPORT_SKELETON_GROUP
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

    # --- control / fit-attr discovery + placement (M3) ------------------------
    def list_namespace_nodes(self, namespace: str) -> list[str]:
        return list(self._cmds.ls(f"{namespace}:*", long=False) or [])

    def list_keyable_user_attrs(self, node: str) -> list[str]:
        return list(self._cmds.listAttr(node, userDefined=True, keyable=True) or [])

    def attr_spec(self, node: str, attr: str) -> AttrSpec:
        cmds = self._cmds
        plug = f"{node}.{attr}"
        try:
            atype = str(cmds.getAttr(plug, type=True))
        except Exception:  # noqa: BLE001 — degrade to empty type
            atype = ""
        try:
            keyable = bool(cmds.getAttr(plug, keyable=True))
        except Exception:  # noqa: BLE001
            keyable = False
        mn = (
            cmds.attributeQuery(attr, node=node, minimum=True)[0]
            if cmds.attributeQuery(attr, node=node, minExists=True)
            else None
        )
        mx = (
            cmds.attributeQuery(attr, node=node, maximum=True)[0]
            if cmds.attributeQuery(attr, node=node, maxExists=True)
            else None
        )
        try:
            dv = cmds.attributeQuery(attr, node=node, listDefault=True)
            default = float(dv[0]) if dv else None
        except Exception:  # noqa: BLE001
            default = None
        try:
            value: float | None = float(cmds.getAttr(plug))
        except Exception:  # noqa: BLE001 — non-scalar / unreadable
            value = None
        return AttrSpec(attr, atype, keyable,
                        None if mn is None else float(mn),
                        None if mx is None else float(mx),
                        default, value)

    def set_attr(self, node: str, attr: str, value: float) -> None:
        self._cmds.setAttr(f"{node}.{attr}", value)

    def get_vector(self, node: str, attr: str) -> tuple[float, float, float]:
        v = self._cmds.getAttr(f"{node}.{attr}")[0]
        return (float(v[0]), float(v[1]), float(v[2]))

    def set_vector(self, node: str, attr: str, value: tuple[float, float, float]) -> None:
        self._cmds.setAttr(f"{node}.{attr}", value[0], value[1], value[2], type="double3")
