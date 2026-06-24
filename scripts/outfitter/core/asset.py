"""Asset data model + metadata validation (pure, headless-testable).

An asset's identity/version metadata can come from two places:
  1. a sidecar ``<asset>.json`` next to the ``.ma`` (fast path, browser-friendly),
  2. the ``cloth_info`` node string attrs inside the ``.ma`` (Authoring Spec §12).

The sidecar is authoritative for the browser when present; the ``.ma`` info node
is the fallback and the ground truth at validation time. Field names below mirror
the Authoring Spec §12 attribute names so a sidecar can be a verbatim dump of them.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..config import ASSET_TYPES, GENDERS

# cloth_info attr name -> AssetMetadata field name
_INFO_FIELD_MAP = {
    "assetName": "asset_name",
    "assetType": "asset_type",
    "gender": "gender",
    "clothVersion": "cloth_version",
    "genHumanCompat": "genhuman_compat",
    "author": "author",
    "notes": "notes",
    # informational extras (captured at publish; never affect validity)
    "created": "created",
    "rigVersion": "rig_version",
    "triCount": "tri_count",
    "vertCount": "vert_count",
}


def _opt_int(value: object) -> int | None:
    """Best-effort int; ``None`` when blank/garbage so it never blocks an asset."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    try:
        return int(float(str(value).replace(",", "").strip()))
    except (TypeError, ValueError):
        return None


def _split_compat(raw: str) -> tuple[str, ...]:
    """``"v03, v04"`` -> ``("v03", "v04")``; order-preserving, de-duped, trimmed."""
    seen: list[str] = []
    for part in raw.replace(";", ",").split(","):
        tok = part.strip()
        if tok and tok not in seen:
            seen.append(tok)
    return tuple(seen)


@dataclass(frozen=True)
class AssetMetadata:
    """Identity + version metadata for one clothing asset (Authoring Spec §12)."""

    asset_name: str
    asset_type: str
    gender: str
    cloth_version: str
    genhuman_compat: tuple[str, ...] = ()
    author: str = ""
    notes: str = ""
    # Informational extras captured at publish (Maya-side: polycount, date, the
    # exact rig version authored against). Optional — absent/garbage values default
    # and never produce a validation error. ``notes`` doubles as the description.
    created: str = ""
    rig_version: str = ""
    tri_count: int | None = None
    vert_count: int | None = None

    @classmethod
    def from_mapping(cls, data: dict[str, str]) -> tuple["AssetMetadata | None", list[str]]:
        """Build from a sidecar/info dict. Returns ``(meta_or_None, errors)``.

        Accepts both spec attr names (``assetName``) and snake_case field names
        (``asset_name``) so a hand-written JSON sidecar works either way. Never
        raises — invalid input yields ``None`` plus human-readable error strings.
        """
        norm: dict[str, object] = {}
        for key, value in data.items():
            field_name = _INFO_FIELD_MAP.get(key, key)
            norm[field_name] = value

        errors: list[str] = []
        asset_name = str(norm.get("asset_name", "")).strip()
        asset_type = str(norm.get("asset_type", "")).strip()
        gender = str(norm.get("gender", "")).strip().lower()
        cloth_version = str(norm.get("cloth_version", "")).strip()

        if not asset_name:
            errors.append("missing 'assetName'")
        if not asset_type:
            errors.append("missing 'assetType'")
        elif asset_type not in ASSET_TYPES:
            errors.append(
                f"assetType '{asset_type}' not one of {', '.join(ASSET_TYPES)}"
            )
        if not gender:
            errors.append("missing 'gender'")
        elif gender not in GENDERS:
            errors.append(
                f"gender '{gender}' not one of {', '.join(GENDERS)}"
            )
        if not cloth_version:
            errors.append("missing 'clothVersion'")

        compat_raw = norm.get("genhuman_compat", "")
        if isinstance(compat_raw, (list, tuple)):
            compat = tuple(str(x).strip() for x in compat_raw if str(x).strip())
        else:
            compat = _split_compat(str(compat_raw))
        if not compat:
            errors.append("missing 'genHumanCompat'")

        if errors:
            return None, errors

        return (
            cls(
                asset_name=asset_name,
                asset_type=asset_type,
                gender=gender,
                cloth_version=cloth_version,
                genhuman_compat=compat,
                author=str(norm.get("author", "")).strip(),
                notes=str(norm.get("notes", "")).strip(),
                created=str(norm.get("created", "")).strip(),
                rig_version=str(norm.get("rig_version", "")).strip(),
                tri_count=_opt_int(norm.get("tri_count")),
                vert_count=_opt_int(norm.get("vert_count")),
            ),
            [],
        )

    def supports(self, genhuman_version: str) -> bool:
        return genhuman_version in self.genhuman_compat


@dataclass(frozen=True)
class ClothingAsset:
    """A discovered, browsable clothing asset on disk.

    ``metadata`` is ``None`` when the asset could not be identified; ``errors``
    then explains why so the browser can show it as invalid rather than hide it.
    """

    ma_path: Path
    metadata: AssetMetadata | None
    thumbnail: Path | None = None
    sidecar: Path | None = None
    source: str = "none"  # "sidecar" | "ma_info" | "none"
    errors: tuple[str, ...] = ()

    @property
    def is_valid(self) -> bool:
        return self.metadata is not None

    @property
    def display_name(self) -> str:
        if self.metadata is not None:
            return self.metadata.asset_name
        return self.ma_path.stem

    @property
    def asset_type(self) -> str:
        return self.metadata.asset_type if self.metadata else "unknown"

    @property
    def gender(self) -> str:
        return self.metadata.gender if self.metadata else "unknown"
