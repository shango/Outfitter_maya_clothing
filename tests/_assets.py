"""Helpers to synthesize clothing-asset .ma files for tests."""
from __future__ import annotations

from pathlib import Path

import _bootstrap  # noqa: F401

from outfitter.core import library
from outfitter.core.asset import ClothingAsset


def write_asset_ma(
    path: Path,
    *,
    joints: list[str],
    helper_joints: list[str] = (),
    asset_name: str = "test_asset",
    asset_type: str = "coat",
    gender: str = "male",
    compat: str = "v03",
    groups: list[str] = ("Mesh_GRP", "Rig_GRP", "Ctrl_GRP"),
    info: bool = True,
    extra_lines: list[str] = (),
) -> Path:
    lines = ["//Maya ASCII 2026 scene", f'createNode transform -n "cloth_{asset_name}";']
    for g in groups:
        lines.append(f'createNode transform -n "{g}";')
    for j in joints:
        lines.append(f'createNode joint -n "{j}";')
    for h in helper_joints:
        lines.append(f'createNode joint -n "{h}";')
    if info:
        lines += [
            'createNode network -n "cloth_info";',
            f'setAttr ".assetName" -type "string" "{asset_name}";',
            f'setAttr ".assetType" -type "string" "{asset_type}";',
            f'setAttr ".gender" -type "string" "{gender}";',
            'setAttr ".clothVersion" -type "string" "1.0.0";',
            f'setAttr ".genHumanCompat" -type "string" "{compat}";',
        ]
    lines += list(extra_lines)
    path.write_text("\n".join(lines))
    return path


def load(path: Path) -> ClothingAsset:
    return library.load_asset(path)
