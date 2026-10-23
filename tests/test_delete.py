"""Headless tests for deleting assets and carrying the delete through Sync. No Maya."""
import _bootstrap  # noqa: F401

import json
import os
import time
from pathlib import Path

from outfitter.core import delete, library, sync


def _write(path, text="x", *, mtime=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


def _asset(root, name, *, mtime=None):
    """A published-layout asset: <root>/<name>/<name>.{ma,json,png} + turntable."""
    folder = root / name
    for fname in (f"{name}.ma", f"{name}.json", f"{name}.png", f"{name}_turntable.png"):
        _write(folder / fname, mtime=mtime)
    return folder / f"{name}.ma"


def _old_client_sees(root):
    """What a pre-delete Outfitter would show: every .ma outside _rigs."""
    return sorted(p.relative_to(root).as_posix() for p in root.rglob("*.ma")
                  if "_rigs" not in p.relative_to(root).parts)


# --- delete_asset -------------------------------------------------------------------

def test_delete_trashes_local_and_remote_and_writes_tombstone(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    ma = _asset(local, "coat")
    _asset(remote, "coat")

    result = delete.delete_asset(ma, local, remote, by="artist")

    assert not (local / "coat").exists() and not (remote / "coat").exists()
    assert (result.local_trash / "coat.ma").is_file()
    assert (result.remote_trash / "coat_turntable.png").is_file()
    assert delete.read_tombstones(remote).keys() == {"coat/coat.ma"}
    assert json.loads(result.tombstone.read_text())["by"] == "artist"


def test_trash_is_invisible_to_scanner_and_old_clients(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    ma = _asset(local, "coat")
    _asset(local, "hat")
    _asset(remote, "coat")

    delete.delete_asset(ma, local, remote)

    names = [a.ma_path.name for a in library.scan_library([local]).assets]
    assert names == ["hat.ma"]
    assert _old_client_sees(local) == ["hat/hat.ma"]
    assert _old_client_sees(remote) == []


def test_unpublished_asset_leaves_no_tombstone(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    remote.mkdir()
    ma = _asset(local, "draft")

    result = delete.delete_asset(ma, local, remote)

    assert result.local_trash is not None
    assert result.remote_trash is None and result.tombstone is None
    assert delete.read_tombstones(remote) == {}


def test_no_remote_deletes_local_only(tmp_path):
    local = tmp_path / "local"
    ma = _asset(local, "coat")

    result = delete.delete_asset(ma, local, None)

    assert not ma.exists() and result.tombstone is None


def test_loose_asset_moves_only_its_own_files(tmp_path):
    # Older libraries can hold .ma files straight in the root, beside other assets.
    local = tmp_path / "local"
    _write(local / "coat.ma")
    _write(local / "coat.json")
    _write(local / "coat_thumb.jpg")
    _write(local / "hat.ma")
    _write(local / "hat.json")

    result = delete.delete_asset(local / "coat.ma", local)

    assert sorted(p.name for p in result.local_trash.iterdir()) == [
        "coat.json", "coat.ma", "coat_thumb.jpg"]
    assert (local / "hat.ma").is_file() and (local / "hat.json").is_file()


def test_shared_folder_moves_only_the_asset(tmp_path):
    local = tmp_path / "local"
    _write(local / "jackets" / "a.ma")
    _write(local / "jackets" / "b.ma")

    delete.delete_asset(local / "jackets" / "a.ma", local)

    assert (local / "jackets" / "b.ma").is_file()
    assert not (local / "jackets" / "a.ma").exists()


def test_repeat_delete_of_same_name_does_not_collide(tmp_path):
    local = tmp_path / "local"
    first = delete.delete_asset(_asset(local, "coat"), local).local_trash
    second = delete.delete_asset(_asset(local, "coat"), local).local_trash

    assert first != second and first.is_dir() and second.is_dir()


def test_malformed_or_escaping_tombstones_are_ignored(tmp_path):
    remote = tmp_path / "remote"
    _write(remote / "_deleted" / "bad.json", "not json")
    _write(remote / "_deleted" / "partial.json", json.dumps({"path": "a/a.ma"}))
    _write(remote / "_deleted" / "escape.json",
           json.dumps({"path": "../outside/x.ma", "deleted": 1}))
    delete.write_tombstone(remote, "ok/ok.ma")

    assert delete.read_tombstones(remote).keys() == {"ok/ok.ma"}


def test_clear_tombstone(tmp_path):
    remote = tmp_path / "remote"
    delete.write_tombstone(remote, "coat/coat.ma")

    assert delete.clear_tombstone(remote, "coat/coat.ma") is True
    assert delete.clear_tombstone(remote, "coat/coat.ma") is False
    assert delete.read_tombstones(remote) == {}


# --- Sync ---------------------------------------------------------------------------

def test_sync_trashes_an_asset_deleted_elsewhere(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    old = time.time() - 3600
    _asset(local, "coat", mtime=old)   # pulled by an earlier sync (remote mtimes)
    _asset(remote, "hat")
    delete.write_tombstone(remote, "coat/coat.ma")

    result = sync.sync_remote_to_local(remote, local)

    assert result.removed == [Path("coat/coat.ma")] and result.changed
    assert not (local / "coat").exists()
    assert (delete.trash_dir(local)).is_dir()
    assert "1 removed" in result.summary()


def test_sync_dry_run_reports_without_trashing(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    _asset(local, "coat", mtime=time.time() - 3600)
    remote.mkdir()
    delete.write_tombstone(remote, "coat/coat.ma")

    result = sync.sync_remote_to_local(remote, local, dry_run=True)

    assert len(result.removed) == 1 and (local / "coat" / "coat.ma").is_file()


def test_sync_keeps_asset_edited_after_the_delete(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    remote.mkdir()
    delete.write_tombstone(remote, "coat/coat.ma")
    _asset(local, "coat", mtime=time.time() + 60)  # local work newer than the delete

    result = sync.sync_remote_to_local(remote, local)

    assert not result.removed and (local / "coat" / "coat.ma").is_file()


def test_sync_ignores_tombstone_when_remote_has_asset_again(tmp_path):
    # e.g. re-published by an older install, which doesn't clear tombstones
    local, remote = tmp_path / "local", tmp_path / "remote"
    delete.write_tombstone(remote, "coat/coat.ma")
    _asset(remote, "coat")
    _asset(local, "coat", mtime=time.time() - 3600)

    result = sync.sync_remote_to_local(remote, local)

    assert not result.removed and (local / "coat" / "coat.ma").is_file()


def test_sync_never_pulls_trash_or_tombstones(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    delete.delete_asset(_asset(remote, "coat"), remote)  # trash inside the remote
    delete.write_tombstone(remote, "coat/coat.ma")
    _write(remote / "_rigs" / "genhuman.json", "{}")    # a rig profile still syncs
    local.mkdir()

    result = sync.sync_remote_to_local(remote, local)

    assert [p.as_posix() for p in result.added] == ["_rigs/genhuman.json"]


def test_sync_without_tombstones_is_unchanged(tmp_path):
    # An existing library (no _deleted folder) syncs exactly as before.
    local, remote = tmp_path / "local", tmp_path / "remote"
    _asset(remote, "coat")
    _write(local / "mine" / "mine.ma")

    result = sync.sync_remote_to_local(remote, local)

    assert not result.removed and result.assets_added == 1
    assert (local / "mine" / "mine.ma").is_file()
    assert "removed" not in result.summary()
