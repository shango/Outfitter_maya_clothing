"""Track attached clothing instances and exactly which connections each made.

Detach must break **only** the edges attach created (FR-5) and detaching one
instance must never affect another (FR-6). Both guarantees rest on recording the
precise ``(src, dst)`` plug pairs per instance, keyed by its import namespace.

Pure data (no Maya).
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Connection:
    """One directed DG edge created at attach time."""

    src: str  # e.g. "GenHuman|...|spine_03.translate"
    dst: str  # e.g. "coat:cloth_spine_03.translate"


@dataclass
class AttachedInstance:
    """One attached clothing asset, identified by its import namespace."""

    namespace: str
    asset_name: str
    asset_type: str
    ma_path: str
    cloth_root: str
    connections: list[Connection] = field(default_factory=list)


class InstanceRegistry:
    """In-session record of attached instances, keyed by namespace."""

    def __init__(self) -> None:
        self._instances: dict[str, AttachedInstance] = {}

    def __contains__(self, namespace: str) -> bool:
        return namespace in self._instances

    def __len__(self) -> int:
        return len(self._instances)

    def add(self, instance: AttachedInstance) -> None:
        if instance.namespace in self._instances:
            raise KeyError(f"instance namespace already registered: {instance.namespace}")
        self._instances[instance.namespace] = instance

    def get(self, namespace: str) -> AttachedInstance | None:
        return self._instances.get(namespace)

    def remove(self, namespace: str) -> AttachedInstance | None:
        return self._instances.pop(namespace, None)

    def namespaces(self) -> list[str]:
        return sorted(self._instances)

    def instances(self) -> list[AttachedInstance]:
        return [self._instances[ns] for ns in self.namespaces()]
