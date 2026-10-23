"""Rename a library asset, locally and in the remote, and carry it to everyone's library.

A rename is a renamed copy plus a delete (:mod:`core.delete`): each copy of the asset
(local, and remote when it has one) is copied under the new name with its metadata
updated, then the old one goes through :func:`core.delete.delete_asset` - so the old
files land in the trash and a tombstone makes other artists' Syncs drop the old name
while pulling the new one. Each copy is renamed from its own files, so a rename never
pushes unpublished local edits into the shared library.

The new name is handled as Publish handles it: the metadata (``cloth_info`` in the
``.ma`` and the sidecar) gets the name as typed, the files and folder the sanitized
form. The ``.ma`` is edited as text, not opened in Maya: only the ``assetName`` string
of the ``cloth_info`` node changes. Scene node names, including the
``cloth_<name>`` top group, are left alone - nothing resolves an asset by them.

Works with every library layout :mod:`core.delete` does: a per-asset folder is renamed
with its asset; a loose ``.ma`` has only its own files renamed in place. An asset with
only a sidecar, or only a ``cloth_info`` node, has whichever it carries updated.

Pure logic: filesystem + text only, no Maya. Safe to run headless / in CI.
"""
from __future__ import annotations

import json
import re
import shutil
from dataclasses import dataclass
from pathlib import Path

from .. import config
from . import delete as _delete
from . import publish as _publish

# The cloth_info node's block: its createNode line through its indented statements.
_INFO_BLOCK_RE = re.compile(
    r'^createNode \S+ -n "%s"[^\n]*\n(?:[ \t][^\n]*\n?)*' % re.escape(config.INFO_NODE),
    re.MULTILINE)
_ASSET_NAME_RE = re.compile(
    r'(setAttr\s+"\.assetName"\s+-type\s+"string"\s+)"(?:\\.|[^"\\])*"')


@dataclass
class RenameResult:
    """The renamed asset's ``.ma`` paths, and what happened to the old one."""

    local_ma: Path
    remote_ma: Path | None
    deleted: _delete.DeleteResult


def renamed_path(root: Path | str, ma_path: Path | str, new_name: str) -> Path:
    """Where the asset at ``ma_path`` lands when renamed to ``new_name`` (sanitized)."""
    root, ma_path = Path(root), Path(ma_path)
    stem = _publish.sanitize_asset_name(new_name)
    if _delete.owns_folder(root, ma_path):
        return ma_path.parent.parent / stem / f"{stem}{config.ASSET_EXT}"
    return ma_path.with_name(f"{stem}{config.ASSET_EXT}")


def _ma_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace('"', '\\"')


def set_ma_asset_name(ma_path: Path, name: str) -> bool:
    """Rewrite ``cloth_info.assetName`` in a ``.ma``. False if it carries no such attr."""
    # newline="" + surrogateescape: every byte, line ending included, round-trips as-is.
    with open(ma_path, encoding="utf-8", errors="surrogateescape", newline="") as fh:
        text = fh.read()
    block = _INFO_BLOCK_RE.search(text)
    if block is None:
        return False
    new_block, n = _ASSET_NAME_RE.subn(
        lambda m: f'{m.group(1)}"{_ma_escape(name)}"', block.group(0), count=1)
    if not n:
        return False
    with open(ma_path, "w", encoding="utf-8", errors="surrogateescape", newline="") as fh:
        fh.write(text[:block.start()] + new_block + text[block.end():])
    return True


def set_sidecar_asset_name(sidecar: Path, name: str) -> bool:
    """Rewrite the name in a sidecar, keeping its key style. False if there is none."""
    if not sidecar.is_file():
        return False
    data = json.loads(sidecar.read_text(encoding="utf-8"))
    key = "asset_name" if "asset_name" in data and "assetName" not in data else "assetName"
    data[key] = name
    sidecar.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return True


def _copy_renamed(root: Path, ma_path: Path, new_name: str) -> Path:
    """Copy the asset under ``new_name`` beside the original and update its metadata."""
    new_ma = renamed_path(root, ma_path, new_name)
    if _delete.owns_folder(root, ma_path):
        shutil.copytree(ma_path.parent, new_ma.parent)
        moves = [(f, new_ma.with_name(new_ma.stem + f.name[len(ma_path.stem):]))
                 for f in _delete.asset_files(new_ma.parent / ma_path.name)]
        for src, dst in moves:
            src.rename(dst)
    else:
        for f in _delete.asset_files(ma_path):
            shutil.copy2(f, new_ma.with_name(new_ma.stem + f.name[len(ma_path.stem):]))
    set_ma_asset_name(new_ma, new_name)
    set_sidecar_asset_name(new_ma.with_suffix(config.SIDECAR_EXT), new_name)
    return new_ma


def rename_asset(ma_path: Path | str, new_name: str, local: Path | str,
                 remote: Path | str | None = None, *, by: str = "") -> RenameResult:
    """Rename the asset at ``ma_path`` (inside ``local``) to ``new_name`` everywhere.

    Raises ``ValueError`` for a blank name or one that sanitizes to the current file
    name, and ``FileExistsError`` if the new name is already taken in either library -
    a rename never overwrites another asset.
    """
    ma_path, local = Path(ma_path), Path(local)
    new_name = new_name.strip()
    if not new_name:
        raise ValueError("Enter a new name.")
    new_local = renamed_path(local, ma_path, new_name)
    if new_local.stem == ma_path.stem:
        raise ValueError(f"'{new_name}' gives the same file name as the current one.")

    copies = [(local, ma_path)]
    if remote is not None:
        remote_ma = Path(remote) / _delete.asset_key(local, ma_path)
        if remote_ma.is_file() and remote_ma.resolve() != ma_path.resolve():
            copies.append((Path(remote), remote_ma))
    for root, ma in copies:
        target = renamed_path(root, ma, new_name)
        taken = target.parent if _delete.owns_folder(root, ma) else target
        if taken.exists():
            raise FileExistsError(f"'{target.stem}' already exists in {root}.")

    new_mas = [_copy_renamed(root, ma, new_name) for root, ma in copies]
    deleted = _delete.delete_asset(ma_path, local, remote, by=by)
    if len(new_mas) > 1:
        # The new name may itself have been deleted once; it is live again now.
        _delete.clear_tombstone(remote, _delete.asset_key(remote, new_mas[1]))
    return RenameResult(local_ma=new_mas[0],
                        remote_ma=new_mas[1] if len(new_mas) > 1 else None,
                        deleted=deleted)
