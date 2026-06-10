"""Headless tests for the remote->local one-way sync. Filesystem only, no Maya."""
import _bootstrap  # noqa: F401

import os

from snap_on_clothing.core import sync


def _write(path, text, *, mtime=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    if mtime is not None:
        os.utime(path, (mtime, mtime))
    return path


def test_adds_new_assets(tmp_path):
    remote, local = tmp_path / "remote", tmp_path / "local"
    _write(remote / "coat_A" / "coat_A.ma", "geo")
    _write(remote / "coat_A" / "coat_A.json", "{}")
    local.mkdir()

    result = sync.sync_remote_to_local(remote, local)

    assert result.ok and result.changed
    assert len(result.added) == 2 and not result.updated
    assert (local / "coat_A" / "coat_A.ma").read_text() == "geo"
    assert (local / "coat_A" / "coat_A.json").read_text() == "{}"


def test_skips_unchanged(tmp_path):
    remote, local = tmp_path / "remote", tmp_path / "local"
    _write(remote / "a.ma", "same", mtime=1000)
    _write(local / "a.ma", "same", mtime=1000)

    result = sync.sync_remote_to_local(remote, local)

    assert result.skipped == 1 and not result.changed


def test_updates_changed_when_remote_differs(tmp_path):
    remote, local = tmp_path / "remote", tmp_path / "local"
    _write(remote / "a.ma", "new version is longer", mtime=2000)
    _write(local / "a.ma", "old", mtime=1000)  # different size + older

    result = sync.sync_remote_to_local(remote, local)

    assert len(result.updated) == 1 and not result.added
    assert (local / "a.ma").read_text() == "new version is longer"


def test_keeps_locally_authored_assets(tmp_path):
    remote, local = tmp_path / "remote", tmp_path / "local"
    _write(remote / "shared.ma", "shared")
    _write(local / "my_local_only.ma", "mine")

    result = sync.sync_remote_to_local(remote, local)

    # remote file pulled in, local-only file untouched (never deleted)
    assert (local / "shared.ma").exists()
    assert (local / "my_local_only.ma").read_text() == "mine"
    assert len(result.added) == 1


def test_does_not_clobber_newer_local(tmp_path):
    remote, local = tmp_path / "remote", tmp_path / "local"
    _write(remote / "a.ma", "remote", mtime=1000)  # same size, older
    _write(local / "a.ma", "local!", mtime=5000)   # newer local edit

    result = sync.sync_remote_to_local(remote, local)

    assert result.skipped == 1
    assert (local / "a.ma").read_text() == "local!"


def test_dry_run_reports_without_writing(tmp_path):
    remote, local = tmp_path / "remote", tmp_path / "local"
    _write(remote / "a.ma", "geo")
    local.mkdir()

    result = sync.sync_remote_to_local(remote, local, dry_run=True)

    assert len(result.added) == 1
    assert not (local / "a.ma").exists()  # nothing written


def test_missing_remote_is_error(tmp_path):
    result = sync.sync_remote_to_local(tmp_path / "nope", tmp_path / "local")
    assert result.ok is False and result.errors
    assert "not found" in result.summary().lower()


def test_same_folder_is_error(tmp_path):
    (tmp_path / "lib").mkdir()
    result = sync.sync_remote_to_local(tmp_path / "lib", tmp_path / "lib")
    assert result.ok is False and result.errors


def test_summary_counts(tmp_path):
    remote, local = tmp_path / "remote", tmp_path / "local"
    _write(remote / "new.ma", "n")
    _write(remote / "changed.ma", "longer now", mtime=2000)
    _write(remote / "same.ma", "s", mtime=1000)
    _write(local / "changed.ma", "x", mtime=1000)
    _write(local / "same.ma", "s", mtime=1000)

    result = sync.sync_remote_to_local(remote, local)

    assert len(result.added) == 1 and len(result.updated) == 1 and result.skipped == 1
    assert "1 added" in result.summary() and "1 updated" in result.summary()
