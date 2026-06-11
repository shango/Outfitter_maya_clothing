"""In-memory SceneGateway for headless attach/validate tests (no Maya).

Models just enough of a Maya DG: typed nodes addressed by string, a parent link
for descendant-joint resolution, per-attr locks, directed connections, and
namespace import/remove. Node addresses are whatever the engine uses — full DAG
paths for body joints (so the dual-skeleton case is testable) and ``ns:name`` for
imported asset nodes.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import _bootstrap  # noqa: F401

from snap_on_clothing.core import ma_parse
from snap_on_clothing.core.scene import AttrSpec

_TRANSFORM_TYPES = {"joint", "transform"}
_DEFAULT_ATTRS = {"translate", "rotate", "scale"}


def _short(addr: str) -> str:
    return addr.rsplit("|", 1)[-1].rsplit(":", 1)[-1]


@dataclass
class _CustomAttr:
    type: str = "double"
    keyable: bool = True
    min: float | None = None
    max: float | None = None
    default: float = 0.0
    value: float = 0.0


@dataclass
class _Node:
    node_type: str
    parent: str | None = None
    attrs: set[str] = field(default_factory=set)
    locked: set[str] = field(default_factory=set)
    custom: dict[str, "_CustomAttr"] = field(default_factory=dict)
    vectors: dict[str, tuple[float, float, float]] = field(default_factory=dict)


class FakeScene:
    def __init__(self) -> None:
        self.nodes: dict[str, _Node] = {}
        self.namespaces: set[str] = set()
        self.connections: set[tuple[str, str]] = set()
        self.version: str | None = None
        self.selection: list[str] = []
        self.matrices: dict[str, list[float]] = {}

    # --- test construction helpers -------------------------------------------
    def add_node(self, addr: str, node_type: str = "transform", parent: str | None = None) -> None:
        attrs = set(_DEFAULT_ATTRS) if node_type in _TRANSFORM_TYPES else set()
        self.nodes[addr] = _Node(node_type, parent, attrs)

    def build_genhuman(
        self, joint_names: list[str], *,
        group: str = "GenHuman_Joint_GRP", namespace: str = "",
    ) -> str:
        """Author a GenHuman rig; with ``namespace`` set, models an imported rig.

        Returns the export-group address (namespaced when applicable) so multi-rig
        tests can target a specific rig.
        """
        ns = f"{namespace}:" if namespace else ""
        self.add_node(f"{ns}god_m_godnode_anim", "transform")
        grp = f"{ns}{group}"
        self.add_node(grp, "transform")
        for name in joint_names:
            self.add_node(f"|{grp}|{ns}{name}", "joint", parent=grp)
        if namespace:
            self.namespaces.add(namespace)
        return grp

    def select(self, *nodes: str) -> None:
        self.selection = list(nodes)

    def add_second_skeleton(self, joint_names: list[str], group: str = "GenHuman_rig_deformLayer") -> None:
        self.add_node(group, "transform")
        for name in joint_names:
            self.add_node(f"|{group}|{name}", "joint", parent=group)

    def lock(self, node: str, attr: str) -> None:
        self.nodes[node].locked.add(attr)

    def define_attr(
        self, node: str, attr: str, *,
        type: str = "double", keyable: bool = True,
        min: float | None = None, max: float | None = None,
        default: float = 0.0, value: float | None = None,
    ) -> None:
        """Author a user-defined attr on a node (models an imported fit attr)."""
        self.nodes[node].custom[attr] = _CustomAttr(
            type=type, keyable=keyable, min=min, max=max,
            default=default, value=default if value is None else value,
        )

    # --- SceneGateway ---------------------------------------------------------
    def exists(self, name: str) -> bool:
        return name in self.nodes

    def node_type(self, name: str) -> str:
        return self.nodes[name].node_type

    def descendant_joints(self, root: str) -> dict[str, str]:
        out: dict[str, str] = {}
        for addr, node in self.nodes.items():
            if node.node_type != "joint":
                continue
            cur = node.parent
            under = False
            while cur is not None:
                if cur == root:  # exact address — scopes to ONE rig (multi-rig safe)
                    under = True
                    break
                cur = self.nodes[cur].parent if cur in self.nodes else None
            if under:
                s = _short(addr)
                if s in out:
                    raise ValueError(f"ambiguous joint short name '{s}' under '{root}'")
                out[s] = addr
        return out

    def attr_exists(self, node: str, attr: str) -> bool:
        if node not in self.nodes:
            return False
        n = self.nodes[node]
        return attr in n.attrs or attr in n.custom

    def is_locked(self, node: str, attr: str) -> bool:
        return attr in self.nodes[node].locked

    def incoming(self, node: str, attr: str) -> str | None:
        plug = f"{node}.{attr}"
        for src, dst in self.connections:
            if dst == plug:
                return src
        return None

    def connect(self, src_attr: str, dst_attr: str) -> None:
        self.connections.add((src_attr, dst_attr))

    def disconnect(self, src_attr: str, dst_attr: str) -> None:
        self.connections.discard((src_attr, dst_attr))

    def is_connected(self, src_attr: str, dst_attr: str) -> bool:
        return (src_attr, dst_attr) in self.connections

    def namespace_exists(self, namespace: str) -> bool:
        return namespace in self.namespaces

    def import_asset(self, path: str, namespace: str) -> None:
        summary = ma_parse.summarize_file(path)
        for name in summary.node_names:
            ntype = summary.node_types.get(name, "transform")
            self.add_node(f"{namespace}:{name}", ntype)
        self.namespaces.add(namespace)

    def remove_namespace(self, namespace: str) -> None:
        prefix = f"{namespace}:"
        for addr in [a for a in self.nodes if a.startswith(prefix)]:
            del self.nodes[addr]
        self.connections = {
            (s, d) for s, d in self.connections
            if not s.startswith(prefix) and not d.startswith(prefix)
        }
        self.namespaces.discard(namespace)

    def genhuman_version(self) -> str | None:
        return self.version

    def selected_nodes(self) -> list[str]:
        return list(self.selection)

    _IDENTITY = [1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0, 0, 0, 0, 0, 1.0]

    def world_matrix(self, node: str) -> list[float]:
        return list(self.matrices.get(node, self._IDENTITY))

    def set_world_matrix(self, node: str, matrix: list[float]) -> None:
        self.matrices[node] = list(matrix)

    def resolve_export_group(self, selected_node: str) -> str | None:
        from snap_on_clothing import config

        marker = config.EXPORT_SKELETON_GROUP
        short = selected_node.rsplit("|", 1)[-1]
        top_ns = short.split(":", 1)[0] if ":" in short else ""
        for addr, node in self.nodes.items():
            if node.node_type != "transform" or _short(addr) != marker:
                continue
            addr_short = addr.rsplit("|", 1)[-1]
            addr_ns = addr_short.split(":", 1)[0] if ":" in addr_short else ""
            if addr_ns == top_ns:
                return addr
        return None

    # --- control / fit-attr discovery + placement (M3) ------------------------
    def list_namespace_nodes(self, namespace: str) -> list[str]:
        prefix = f"{namespace}:"
        return [a for a in self.nodes if a.startswith(prefix)]

    def list_keyable_user_attrs(self, node: str) -> list[str]:
        if node not in self.nodes:
            return []
        return [a for a, c in self.nodes[node].custom.items() if c.keyable]

    def attr_spec(self, node: str, attr: str) -> AttrSpec:
        c = self.nodes[node].custom.get(attr)
        if c is None:
            # built-in scalar fallback (e.g. a translateX-style component)
            return AttrSpec(attr, "double", True, None, None, 0.0, 0.0)
        return AttrSpec(attr, c.type, c.keyable, c.min, c.max, c.default, c.value)

    def set_attr(self, node: str, attr: str, value: float) -> None:
        c = self.nodes[node].custom.get(attr)
        if c is None:
            self.nodes[node].custom[attr] = _CustomAttr(value=value)
        else:
            c.value = value

    def get_vector(self, node: str, attr: str) -> tuple[float, float, float]:
        default = (1.0, 1.0, 1.0) if attr == "scale" else (0.0, 0.0, 0.0)
        return self.nodes[node].vectors.get(attr, default)

    def set_vector(self, node: str, attr: str, value: tuple[float, float, float]) -> None:
        self.nodes[node].vectors[attr] = (float(value[0]), float(value[1]), float(value[2]))
