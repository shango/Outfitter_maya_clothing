"""Delete library assets, and carry the delete to every artist's local library.

A delete never hard-deletes: the asset is moved into the library's trash (local and
remote), so a mistake can be undone by moving it back. When the asset was in the
remote, a *tombstone* is left there too: ``<remote>/_deleted/<key>.json``. Sync is
otherwise strictly additive; a tombstone is the one thing that lets it remove an asset
from an artist's local library (see :func:`core.sync.sync_remote_to_local`).
Re-publishing the asset clears its tombstone.

Backwards compatibility with existing libraries and older Outfitter installs:

* An asset is keyed by its ``.ma`` path relative to the library root
  (``coat/coat.ma``, or ``coat.ma`` for a loose file), so any layout works. An asset in
  its own folder (named after it, as Publish lays it out) moves as the whole folder; any
  other asset moves only its own files, so a shared or category folder is never taken.
* The trash lives at ``<library>/_rigs/_trash/``. Older installs already skip ``_rigs``
  when scanning and pull only ``.json`` from it when syncing (rig profiles, read from
  the top level only), so a trashed garment can never reappear in their browser.
* Older installs copy tombstones down but ignore them (they only scan ``.ma``), and a
  tombstone stays put until the name is re-published, so an artist who upgrades later
  still gets the delete on their next Sync.

Pure logic: filesystem + json only, no Maya. Safe to run headless / in CI.
"""
from __future__ import annotations

import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path

from .. import config
from . import rigs

TRASH_DIRNAME: str = "_trash"
DELETED_DIRNAME: str = "_deleted"


def trash_dir(root: Path | str) -> Path:
    return Path(root) / rigs.RIGS_DIRNAME / TRASH_DIRNAME


def asset_files(ma_path: Path | str) -> list[Path]:
    """The asset's own files beside it: ``.ma``, sidecar, thumbnails, turntable."""
    ma_path = Path(ma_path)
    names = [ma_path.name, ma_path.stem + config.SIDECAR_EXT,
             ma_path.stem + config.TURNTABLE_SUFFIX]
    for ext in config.THUMB_EXTS:
        names += [ma_path.stem + ext, ma_path.stem + "_thumb" + ext]
    return [ma_path.with_name(n) for n in names if ma_path.with_name(n).is_file()]


def owns_folder(root: Path, ma_path: Path) -> bool:
    """True if ``ma_path`` is in its own folder: ``<name>/<name>.ma``, no other asset.

    Requiring the folder to be named after the asset keeps a category folder that
    happens to hold one asset (``hats/beanie.ma``) from being moved or renamed with it.
    """
    folder = ma_path.parent
    if folder.resolve() == root.resolve() or folder.name != ma_path.stem:
        return False
    return all(p.resolve() == ma_path.resolve()
               for p in folder.rglob(f"*{config.ASSET_EXT}"))


def trash_asset(root: Path | str, ma_path: Path | str) -> Path:
    """Move the asset at ``ma_path`` into ``root``'s trash; return the folder it went to."""
    root, ma_path = Path(root), Path(ma_path)
    base = trash_dir(root) / f"{ma_path.stem}_{time.strftime('%Y%m%d-%H%M%S')}"
    dest, n = base, 1
    while dest.exists():  # two deletes of one name inside the same second
        dest = base.with_name(f"{base.name}_{n}")
        n += 1
    dest.parent.mkdir(parents=True, exist_ok=True)
    if owns_folder(root, ma_path):
        shutil.move(str(ma_path.parent), str(dest))
    else:
        files = asset_files(ma_path)
        dest.mkdir()
        for f in files:
            shutil.move(str(f), str(dest / f.name))
    return dest


def asset_key(root: Path | str, ma_path: Path | str) -> str:
    """The library-relative ``.ma`` path that identifies an asset across libraries."""
    return Path(ma_path).resolve().relative_to(Path(root).resolve()).as_posix()


def tombstone_path(remote: Path | str, key: str) -> Path:
    return Path(remote) / DELETED_DIRNAME / (key.replace("/", "__") + ".json")


def write_tombstone(remote: Path | str, key: str, *, by: str = "") -> Path:
    """Record in the remote that the asset ``key`` was deleted (now, by ``by``)."""
    path = tombstone_path(remote, key)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"path": key, "deleted": time.time(), "by": by},
                               indent=2), encoding="utf-8")
    return path


def clear_tombstone(remote: Path | str, key: str) -> bool:
    """Remove ``key``'s tombstone (it was published again). True if one existed."""
    path = tombstone_path(remote, key)
    if not path.is_file():
        return False
    path.unlink()
    return True


def read_tombstones(remote: Path | str) -> dict[str, float]:
    """``{asset key: deleted epoch seconds}`` for every readable tombstone in ``remote``."""
    found: dict[str, float] = {}
    for path in sorted((Path(remote) / DELETED_DIRNAME).glob("*.json")):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            key, deleted = str(raw["path"]), float(raw["deleted"])
        except (OSError, ValueError, TypeError, KeyError):
            continue  # a malformed marker must never cause a delete
        if Path(key).is_absolute() or ".." in Path(key).parts:
            continue  # nor one pointing outside the library
        found[key] = deleted
    return found


@dataclass
class DeleteResult:
    """Where a deleted asset went (``None`` = that copy didn't exist)."""

    local_trash: Path | None = None
    remote_trash: Path | None = None
    tombstone: Path | None = None


def delete_asset(ma_path: Path | str, local: Path | str,
                 remote: Path | str | None = None, *, by: str = "") -> DeleteResult:
    """Delete the asset at ``ma_path`` (inside the ``local`` library) everywhere.

    The local copy goes to the local trash. When ``remote`` is set and holds the same
    asset, that copy goes to the remote trash and a tombstone is written so other
    artists' Syncs remove it too. An asset that was never published leaves no
    tombstone - it would only threaten other people's unrelated local work.
    """
    ma_path = Path(ma_path)
    key = asset_key(local, ma_path)
    result = DeleteResult()
    if remote is not None:
        remote_ma = Path(remote) / key
        if remote_ma.is_file() and remote_ma.resolve() != ma_path.resolve():
            result.remote_trash = trash_asset(remote, remote_ma)
            result.tombstone = write_tombstone(remote, key, by=by)
    if ma_path.is_file():
        result.local_trash = trash_asset(local, ma_path)
    return result
