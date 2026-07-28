"""Scan library roots for clothing ``.ma`` assets and build the asset list.

Per asset, metadata resolution order (PRD FR-1):
  1. sidecar ``<asset>.json`` if present (fast, no .ma parse),
  2. else the ``cloth_info`` node string attrs parsed from the ``.ma`` itself.

Thumbnails: ``<asset>.png`` / ``<asset>_thumb.png`` (and .jpg/.jpeg) beside the .ma.

Pure logic: filesystem + json only, no Maya. Safe to run in CI / headless.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .. import config
from . import ma_parse
from . import rigs
from .asset import AssetMetadata, ClothingAsset


@dataclass
class LibraryScanResult:
    assets: list[ClothingAsset] = field(default_factory=list)
    scanned_roots: list[Path] = field(default_factory=list)
    skipped_roots: list[Path] = field(default_factory=list)  # missing/not a dir

    @property
    def valid(self) -> list[ClothingAsset]:
        return [a for a in self.assets if a.is_valid]

    @property
    def invalid(self) -> list[ClothingAsset]:
        return [a for a in self.assets if not a.is_valid]

    def by_type(self, asset_type: str) -> list[ClothingAsset]:
        return [a for a in self.valid if a.asset_type == asset_type]

    def by_gender(self, gender: str) -> list[ClothingAsset]:
        return [a for a in self.valid if a.gender == gender]

    def for_rig(self, rig_id: str, version: str = "") -> list[ClothingAsset]:
        """Assets that can be attached to a rig - what the browser shows when it's selected."""
        return [a for a in self.valid if a.fits_rig(rig_id, version)]


def _find_thumbnail(ma_path: Path) -> Path | None:
    for ext in config.THUMB_EXTS:
        for cand in (ma_path.with_suffix(ext), ma_path.with_name(ma_path.stem + "_thumb" + ext)):
            if cand.is_file():
                return cand
    return None


def _find_turntable(ma_path: Path) -> Path | None:
    """The ``<asset>_turntable.png`` rotatable sprite sheet beside the ``.ma``, if any."""
    cand = ma_path.with_name(ma_path.stem + config.TURNTABLE_SUFFIX)
    return cand if cand.is_file() else None


def _load_sidecar(sidecar: Path) -> tuple[AssetMetadata | None, list[str]]:
    try:
        raw = json.loads(sidecar.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, [f"sidecar unreadable: {exc}"]
    if not isinstance(raw, dict):
        return None, ["sidecar JSON is not an object"]
    return AssetMetadata.from_mapping({str(k): v for k, v in raw.items()})


def load_asset(ma_path: Path) -> ClothingAsset:
    """Resolve one ``.ma`` into a ``ClothingAsset`` (sidecar first, then info node)."""
    ma_path = Path(ma_path)
    thumb = _find_thumbnail(ma_path)
    turntable = _find_turntable(ma_path)
    sidecar = ma_path.with_suffix(config.SIDECAR_EXT)

    if sidecar.is_file():
        meta, errors = _load_sidecar(sidecar)
        if meta is not None:
            return ClothingAsset(ma_path, meta, thumb, sidecar, source="sidecar",
                                 turntable=turntable)
        # sidecar present but bad - fall through to the .ma, keep the reason
        info = ma_parse.read_info_attrs(ma_path, config.INFO_NODE)
        meta2, errors2 = AssetMetadata.from_mapping(info)
        if meta2 is not None:
            return ClothingAsset(ma_path, meta2, thumb, sidecar, source="ma_info",
                                 turntable=turntable)
        return ClothingAsset(
            ma_path, None, thumb, sidecar, source="none",
            errors=tuple(f"sidecar: {e}" for e in errors) + tuple(f"cloth_info: {e}" for e in errors2),
            turntable=turntable,
        )

    info = ma_parse.read_info_attrs(ma_path, config.INFO_NODE)
    meta, errors = AssetMetadata.from_mapping(info)
    if meta is not None:
        return ClothingAsset(ma_path, meta, thumb, None, source="ma_info",
                             turntable=turntable)
    reason = errors if info else ["no cloth_info node and no sidecar .json"]
    return ClothingAsset(ma_path, None, thumb, None, source="none",
                         errors=tuple(reason), turntable=turntable)


def scan_library(roots: list[Path] | None = None) -> LibraryScanResult:
    """Walk ``roots`` recursively for ``*.ma`` assets and resolve each one.

    The ``_rigs`` folder is skipped: it holds registered rig profiles and the rig ``.ma``
    files themselves, and a body rig is emphatically not a garment - scanning it would
    fill the browser with 30 MB "invalid asset" entries.
    """
    if roots is None:
        roots = config.default_library_roots()

    result = LibraryScanResult()
    seen: set[Path] = set()
    for root in roots:
        root = Path(root)
        if not root.is_dir():
            result.skipped_roots.append(root)
            continue
        result.scanned_roots.append(root)
        for ma_path in sorted(root.rglob(f"*{config.ASSET_EXT}")):
            if rigs.RIGS_DIRNAME in ma_path.relative_to(root).parts:
                continue  # a registered rig, not a clothing asset
            resolved = ma_path.resolve()
            if resolved in seen:
                continue  # same asset reachable from two roots
            seen.add(resolved)
            result.assets.append(load_asset(ma_path))

    result.assets.sort(key=lambda a: (a.gender, a.asset_type, a.display_name.lower()))
    return result
