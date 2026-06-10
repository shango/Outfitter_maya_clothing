"""Track attached clothing instances and exactly which connections each made.

Detach must break **only** the edges attach created (FR-5) and detaching one
instance must never affect another (FR-6). Both guarantees rest on recording the
precise ``(src, dst)`` plug pairs per instance, keyed by its import namespace.

Pure data + serialization (no Maya). Serializes to plain dicts so the registry
can later be persisted into a scene node or a sidecar without code changes.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict


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

    def to_dict(self) -> dict:
        d = asdict(self)
        d["connections"] = [asdict(c) for c in self.connections]
        return d

    @classmethod
    def from_dict(cls, data: dict) -> "AttachedInstance":
        conns = [Connection(**c) for c in data.get("connections", [])]
        return cls(
            namespace=data["namespace"],
            asset_name=data["asset_name"],
            asset_type=data["asset_type"],
            ma_path=data["ma_path"],
            cloth_root=data["cloth_root"],
            connections=conns,
        )


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

    def to_dict(self) -> dict:
        return {ns: inst.to_dict() for ns, inst in self._instances.items()}

    @classmethod
    def from_dict(cls, data: dict) -> "InstanceRegistry":
        reg = cls()
        for inst in data.values():
            reg.add(AttachedInstance.from_dict(inst))
        return reg
