"""One-off library migration: make an old asset's rig identity explicit (pure, headless).

Assets published before the tool went rig-agnostic carry no ``rigId``: they say
``genHumanCompat: "v03"`` and nothing about which rig that is, because at the time there
was only one. Reading them is already handled - no ``rigId`` means GenHuman
(:class:`core.asset.AssetMetadata`), so an existing library keeps working untouched and
nobody *has* to run this.

What the implied default cannot do is survive a second rig arriving in the same library
with the same version string. This action writes the identity down: it adds
``rigId``/``rigVersions`` to the sidecars that lack them, so every asset states which rig
it belongs to instead of inheriting an assumption.

Sidecars only. The ``cloth_info`` node embedded in each ``.ma`` is refreshed the next time
that asset is published (rewriting a ``.ma`` here would mean opening every file in Maya,
and the sidecar is what the browser reads). :attr:`StampResult.warnings` says so when the
distinction matters.

Pure logic: filesystem + json only, no Maya.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from .. import config
from . import rigs as _rigs


@dataclass(frozen=True)
class StampCandidate:
    """One sidecar that doesn't declare a rig, and what would be written to it."""

    sidecar: Path
    asset_name: str
    versions: tuple[str, ...]  # taken from the legacy genHumanCompat


@dataclass(frozen=True)
class StampPlan:
    rig_id: str
    candidates: tuple[StampCandidate, ...] = ()
    already_stamped: int = 0
    unreadable: tuple[Path, ...] = ()

    @property
    def is_empty(self) -> bool:
        return not self.candidates

    def summary(self) -> str:
        n = len(self.candidates)
        if not n:
            return (f"Nothing to stamp - all {self.already_stamped} asset(s) already "
                    "declare which rig they're for.")
        return (f"{n} asset(s) don't declare a rig and would be stamped as "
                f"'{self.rig_id}'; {self.already_stamped} already do.")


@dataclass
class StampResult:
    stamped: list[str] = field(default_factory=list)
    failed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        n = len(self.stamped)
        msg = f"Stamped {n} asset{'' if n == 1 else 's'} with their rig identity."
        if self.failed:
            msg += f" {len(self.failed)} could not be written."
        return msg


def _versions_from(raw: dict) -> tuple[str, ...]:
    """Version list from a legacy sidecar (``genHumanCompat``), split on , or ;."""
    text = str(raw.get("genHumanCompat", "") or "")
    return tuple(v.strip() for v in text.replace(";", ",").split(",") if v.strip())


def plan_stamp(sidecars, rig_id: str = _rigs.DEFAULT_RIG_ID) -> StampPlan:
    """Work out which sidecars are missing a rig identity, without writing anything.

    ``sidecars`` is any iterable of sidecar paths (the library scan's
    ``asset.sidecar``). A sidecar that already names a rig is left alone even if it names
    a *different* one - this migration records what was always implied, it never
    reassigns an asset to another rig (that is what retargeting is for).
    """
    candidates: list[StampCandidate] = []
    already = 0
    unreadable: list[Path] = []

    for path in sidecars:
        path = Path(path)
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            unreadable.append(path)
            continue
        if not isinstance(raw, dict):
            unreadable.append(path)
            continue
        if str(raw.get("rigId", "")).strip():
            already += 1
            continue
        candidates.append(StampCandidate(
            sidecar=path,
            asset_name=str(raw.get("assetName", "")).strip() or path.stem,
            versions=_versions_from(raw),
        ))

    return StampPlan(rig_id=rig_id, candidates=tuple(candidates),
                     already_stamped=already, unreadable=tuple(unreadable))


def apply_stamp(plan: StampPlan) -> StampResult:
    """Write ``rigId``/``rigVersions`` into every sidecar the plan listed.

    Each file is rewritten with its existing keys preserved and the two new ones added, so
    hand-added fields survive. An asset whose legacy sidecar listed no versions at all is
    stamped with the rig id and reported - it has nothing to say about which builds it
    fits, and the rigger needs to fill that in.
    """
    result = StampResult()
    for candidate in plan.candidates:
        try:
            raw = json.loads(candidate.sidecar.read_text(encoding="utf-8"))
            raw["rigId"] = plan.rig_id
            raw["rigVersions"] = ", ".join(candidate.versions)
            candidate.sidecar.write_text(
                json.dumps(raw, indent=1) + "\n", encoding="utf-8")
        except (OSError, json.JSONDecodeError, TypeError) as exc:
            result.failed.append(f"{candidate.asset_name}: {exc}")
            continue
        result.stamped.append(candidate.asset_name)
        if not candidate.versions:
            result.warnings.append(
                f"{candidate.asset_name} lists no rig versions - set them on the Publish "
                "tab, or it will fail the version check against any versioned rig.")

    if result.stamped:
        result.warnings.append(
            f"Sidecars only: the {config.INFO_NODE} node inside each .ma still says what "
            "it said before, and is refreshed the next time that asset is published.")
    return result
