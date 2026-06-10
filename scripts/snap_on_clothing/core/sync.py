"""One-way pull from the remote master library into the local working library.

The user works from their **local** folder; the **remote** folder is a shared
master (studio server / drive). The Setup tab's *Sync from remote* button calls
:func:`sync_remote_to_local`, which mirrors new and changed files down from the
remote into the local folder.

Semantics (locked with the user, 2026-06-09):

* **Additive / update-changed, never delete.** Every file under ``remote`` is
  copied to the matching path under ``local`` when it is missing there, or when
  it differs by a fast *size + modified-time* check (``rsync``-style quick scan).
  Files that exist only locally — assets the artist authored locally — are always
  left untouched. Nothing is ever deleted.
* **Remote-newer wins.** An existing local file is overwritten only when the
  remote copy is a different size or is *newer* (beyond a small filesystem
  tolerance), so a file the artist just edited locally is not clobbered by an
  older remote copy of the same size.

``shutil.copy2`` preserves the source modified-time, so a file copied in one sync
compares equal on the next and is skipped — repeated syncs only move real changes.

Pure logic: filesystem only, no Maya. Safe to run headless / in CI.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

# Filesystem mtime resolution varies (FAT rounds to 2s); treat times within this
# many seconds as equal so we don't re-copy unchanged files forever.
_MTIME_TOLERANCE_S = 2.0


@dataclass
class SyncResult:
    """Outcome of one :func:`sync_remote_to_local` run (paths are local-relative)."""

    added: list[Path] = field(default_factory=list)      # newly copied files
    updated: list[Path] = field(default_factory=list)    # changed files overwritten
    skipped: int = 0                                       # up-to-date, left alone
    errors: list[str] = field(default_factory=list)       # per-file copy failures
    ok: bool = True                                        # False if the run could not start

    @property
    def copied(self) -> int:
        return len(self.added) + len(self.updated)

    @property
    def changed(self) -> bool:
        return bool(self.added or self.updated)

    def summary(self) -> str:
        """One-line human summary for the Setup tab status."""
        if not self.ok:
            return self.errors[0] if self.errors else "Sync could not run."
        parts = [f"{len(self.added)} added", f"{len(self.updated)} updated",
                 f"{self.skipped} up to date"]
        if self.errors:
            parts.append(f"{len(self.errors)} failed")
        return "Sync complete — " + ", ".join(parts) + "."


def _needs_copy(src: Path, dst: Path) -> bool:
    """True if ``src`` should be copied over ``dst`` (missing / bigger-or-smaller / newer)."""
    try:
        dst_stat = dst.stat()
    except OSError:
        return True  # missing locally
    src_stat = src.stat()
    if src_stat.st_size != dst_stat.st_size:
        return True
    return src_stat.st_mtime - dst_stat.st_mtime > _MTIME_TOLERANCE_S


def sync_remote_to_local(remote: Path | str, local: Path | str,
                         *, dry_run: bool = False) -> SyncResult:
    """Pull new/changed files from ``remote`` into ``local``. Never deletes.

    Returns a :class:`SyncResult`. When ``dry_run`` is True the result reports
    what *would* be copied without touching the local folder.
    """
    remote = Path(remote).expanduser()
    local = Path(local).expanduser()
    result = SyncResult()

    if not remote.is_dir():
        result.ok = False
        result.errors.append(f"Remote folder not found or not a directory: {remote}")
        return result
    if remote.resolve() == local.resolve():
        result.ok = False
        result.errors.append("Local and remote folders are the same.")
        return result

    for src in sorted(remote.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(remote)
        dst = local / rel
        try:
            existed = dst.exists()
            if not _needs_copy(src, dst):
                result.skipped += 1
                continue
            if not dry_run:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
            (result.updated if existed else result.added).append(rel)
        except OSError as exc:
            result.errors.append(f"{rel}: {exc}")
    return result
