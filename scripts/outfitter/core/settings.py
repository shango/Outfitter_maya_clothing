"""Tool settings, stored as a plain-text path file (the tool's tiny "db").

The user sets two folders on the Setup tab:

* **local**  - their working library. This is the *only* folder the tool scans.
* **remote** - a shared master library (studio server / drive). It is never
  scanned; it is the source the **Sync** button pulls new/changed assets from
  into the local folder (see :mod:`outfitter.core.sync`).

Plus one more remembered choice:

* **rig** - the id of the registered rig the user is currently working with
  (:mod:`outfitter.core.rigs`). Both tabs share it: the Publish tab authors against
  it, the Library tab filters clothing to it. Persisted so reopening the tool - or
  Maya - doesn't silently drop the user back onto a different rig.

All three are written to a small text file as ``key = value`` lines that is read back
on launch. That text file is the single source of truth::

    local  = /mnt/work/clothing_assets
    remote = //studio-nas/genhuman/clothing
    rig    = genhuman

Location: ``scripts/path.txt``, beside the package (``config.path_file()``). Easy
to find and hand-edit, ships with a studio install, and survives installer
upgrades (the installer overwrites the package dir, never ``path.txt``).

Pure logic (filesystem only, no Maya). Reads are defensive - a missing or garbled
file yields empty slots rather than raising, so a bad file can never stop the tool
opening.

**Backward compatibility:** older path files listed bare folder lines (no key),
one library root per line. Those are still read - the first bare folder becomes
``local`` - so an existing install keeps working and is migrated to the keyed
format on the next write.

:func:`effective_library_roots` returns ``[local]`` when a local folder is set,
otherwise the built-in defaults (installed library + bundled starter assets).
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from .. import config

_HEADER = (
    "# Outfitter - settings (managed by the tool's Setup and Publish tabs).\n"
    "#   local  = your working library (the tool scans this folder)\n"
    "#   remote = shared master library the Sync button pulls new/changed assets from\n"
    "#   rig    = id of the registered rig you're currently working with\n"
    "# Blank lines and lines starting with '#' are ignored.\n"
)

_LOCAL_KEY = "local"
_REMOTE_KEY = "remote"
_RIG_KEY = "rig"


def _resolve(path: Path | str) -> Path:
    return Path(str(path).strip()).expanduser()


def _file(path: Path | None) -> Path:
    return Path(path) if path is not None else config.path_file()


@dataclass(frozen=True)
class Locations:
    """The saved settings: two library folders and the chosen rig (any may be unset)."""

    local: Path | None = None
    remote: Path | None = None
    rig: str | None = None


def read_locations(path: Path | None = None) -> Locations:
    """Read the saved settings. Missing/unreadable file ⇒ empty slots.

    Tolerates the legacy bare-line format (one folder per line, no key): the first
    such line is taken as ``local``.
    """
    try:
        text = _file(path).read_text(encoding="utf-8")
    except OSError:
        return Locations()

    local: Path | None = None
    remote: Path | None = None
    rig: str | None = None
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        key, sep, value = line.partition("=")
        if sep:  # keyed line: "local = ..." / "remote = ..." / "rig = ..."
            key = key.strip().lower()
            value = value.strip()
            if not value:
                continue
            if key == _LOCAL_KEY and local is None:
                local = _resolve(value)
            elif key == _REMOTE_KEY and remote is None:
                remote = _resolve(value)
            elif key == _RIG_KEY and rig is None:
                rig = value
        elif local is None:  # legacy bare folder line → local (first wins)
            local = _resolve(line)
    return Locations(local=local, remote=remote, rig=rig)


def write_locations(local: Path | str | None, remote: Path | str | None,
                    path: Path | None = None, *, rig: str | None = None) -> Path:
    """Write the settings to the path file (creating parent dirs).

    Passing ``None`` for a slot leaves it unset. Writing all as ``None`` leaves
    just the header, so :func:`effective_library_roots` falls back to defaults.

    Callers that change one setting should go through the ``set_*`` helpers below,
    which read the current file first so the other slots survive.
    """
    dest = _file(path)
    dest.parent.mkdir(parents=True, exist_ok=True)
    lines = [_HEADER]
    if local is not None:
        lines.append(f"{_LOCAL_KEY} = {_resolve(local)}")
    if remote is not None:
        lines.append(f"{_REMOTE_KEY} = {_resolve(remote)}")
    if rig:
        lines.append(f"{_RIG_KEY} = {rig.strip()}")
    dest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dest


def set_local(value: Path | str | None, path: Path | None = None) -> Path:
    """Set (or clear, with ``None``) the local working folder; keep the other settings."""
    loc = read_locations(path)
    return write_locations(value, loc.remote, path, rig=loc.rig)


def set_remote(value: Path | str | None, path: Path | None = None) -> Path:
    """Set (or clear, with ``None``) the remote sync source; keep the other settings."""
    loc = read_locations(path)
    return write_locations(loc.local, value, path, rig=loc.rig)


def set_rig(value: str | None, path: Path | None = None) -> Path:
    """Set (or clear, with ``None``) the rig being worked with; keep the folders."""
    loc = read_locations(path)
    return write_locations(loc.local, loc.remote, path, rig=value)


def active_rig_id(path: Path | None = None) -> str:
    """The rig id the user last chose, or the default rig when they never have.

    Returns an id, not a profile - resolving it to a registered rig is
    :func:`core.rigs.resolve_profile`'s job, and it degrades gracefully if the saved
    rig has since been removed from the library.
    """
    from .rigs import DEFAULT_RIG_ID

    return read_locations(path).rig or DEFAULT_RIG_ID


def is_configured(path: Path | None = None) -> bool:
    """True when a local working folder is set (i.e. the tool won't use defaults)."""
    return read_locations(path).local is not None


def effective_library_roots(path: Path | None = None) -> list[Path]:
    """Folders to scan: the local working folder, else the built-in defaults.

    The remote folder is deliberately excluded - it is a sync source, not a scan
    root (the user works from the local copy).
    """
    local = read_locations(path).local
    if local is not None:
        return [local]
    return config.default_library_roots()
