"""Asset data model + metadata validation (pure, headless-testable).

An asset's identity/version metadata can come from two places:
  1. a sidecar ``<asset>.json`` next to the ``.ma`` (fast path, browser-friendly),
  2. the ``cloth_info`` node string attrs inside the ``.ma`` (Authoring Spec §12).

The sidecar is authoritative for the browser when present; the ``.ma`` info node
is the fallback and the ground truth at validation time. Field names below mirror
the Authoring Spec §12 attribute names so a sidecar can be a verbatim dump of them.

**Rig identity.** A garment is skinned to one rig's skeleton, so it declares one
``rigId`` plus the versions of that rig it is compatible with (``rigVersions``). Assets
published before the tool went rig-agnostic carry neither - they carry ``genHumanCompat``
and were, by definition, GenHuman assets. Those are read as ``rigId = "genhuman"`` with
``genHumanCompat`` as the version list, so an existing library keeps working untouched.
Reusing a garment on a different rig is a *conversion* (see :mod:`core.retarget`), which
produces a second asset - never a second rig id on the same one.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ..config import ASSET_TYPES, GENDER_NONE, GENDERS
from .rigs import DEFAULT_RIG_ID

# cloth_info attr name -> AssetMetadata field name
_INFO_FIELD_MAP = {
    "assetName": "asset_name",
    "assetType": "asset_type",
    "gender": "gender",
    "clothVersion": "cloth_version",
    "rigId": "rig_id",
    "rigVersions": "rig_versions",
    "genHumanCompat": "genhuman_compat",  # legacy: pre-rig-agnostic version list
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


def _as_versions(value: object) -> tuple[str, ...]:
    """Normalize a version list written either as a JSON array or a comma string."""
    if isinstance(value, (list, tuple)):
        return tuple(str(x).strip() for x in value if str(x).strip())
    return _split_compat(str(value or ""))


@dataclass(frozen=True)
class AssetMetadata:
    """Identity + version metadata for one clothing asset (Authoring Spec §12)."""

    asset_name: str
    asset_type: str
    gender: str
    cloth_version: str
    # The rig this garment is skinned to, and which of its versions it fits. An asset
    # with no declared rig predates rig-agnostic publishing and is a GenHuman asset.
    rig_id: str = DEFAULT_RIG_ID
    rig_versions: tuple[str, ...] = ()
    author: str = ""
    notes: str = ""
    # Informational extras captured at publish (Maya-side: polycount, date, the
    # exact rig version authored against). Optional - absent/garbage values default
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
        raises - invalid input yields ``None`` plus human-readable error strings.
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
        elif gender not in GENDERS and gender != GENDER_NONE:
            # A rig with a single body publishes GENDER_NONE; anything else must be one of
            # the known variants, so a typo can't quietly become a new body type.
            errors.append(
                f"gender '{gender}' not one of {', '.join(GENDERS)}, {GENDER_NONE}"
            )
        if not cloth_version:
            errors.append("missing 'clothVersion'")

        # Rig identity, with the pre-rig-agnostic fallback: no rigId means a GenHuman
        # asset, and 'genHumanCompat' is where its version list lives.
        rig_id = str(norm.get("rig_id", "")).strip() or DEFAULT_RIG_ID
        versions = _as_versions(norm.get("rig_versions"))
        if not versions:
            versions = _as_versions(norm.get("genhuman_compat"))
        if not versions:
            errors.append("missing 'rigVersions' (or legacy 'genHumanCompat')")

        if errors:
            return None, errors

        return (
            cls(
                asset_name=asset_name,
                asset_type=asset_type,
                gender=gender,
                cloth_version=cloth_version,
                rig_id=rig_id,
                rig_versions=versions,
                author=str(norm.get("author", "")).strip(),
                notes=str(norm.get("notes", "")).strip(),
                created=str(norm.get("created", "")).strip(),
                rig_version=str(norm.get("rig_version", "")).strip(),
                tri_count=_opt_int(norm.get("tri_count")),
                vert_count=_opt_int(norm.get("vert_count")),
            ),
            [],
        )

    @property
    def genhuman_compat(self) -> tuple[str, ...]:
        """Legacy alias for :attr:`rig_versions` (the field's name before rig profiles)."""
        return self.rig_versions

    def supports(self, rig_id: str, version: str = "") -> bool:
        """True if this garment fits ``rig_id`` (and ``version``, when one is given).

        Both gates matter and neither implies the other: a different rig means a different
        skeleton, so the joints simply won't match; a different *version* of the same rig
        may have moved joints the garment is fitted to. A blank ``version`` checks the rig
        alone, for callers that only need to know which browser bucket an asset belongs in.
        """
        if rig_id.strip() != self.rig_id.strip():
            return False
        return not version.strip() or version.strip() in self.rig_versions


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
    turntable: Path | None = None  # rotatable sprite sheet beside the still thumbnail

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

    @property
    def rig_id(self) -> str:
        return self.metadata.rig_id if self.metadata else "unknown"

    def fits_rig(self, rig_id: str, version: str = "") -> bool:
        """True if this asset can be attached to that rig. Invalid assets never fit."""
        return self.metadata is not None and self.metadata.supports(rig_id, version)
