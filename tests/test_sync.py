"""Headless tests for the remote->local one-way sync. Filesystem only, no Maya."""
import _bootstrap  # noqa: F401

import os

from outfitter.core import sync


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


def test_progress_reports_scan_then_each_file_then_done(tmp_path):
    remote, local = tmp_path / "remote", tmp_path / "local"
    _write(remote / "a.ma", "a")
    _write(remote / "b.ma", "b")
    _write(remote / "c.ma", "c")
    local.mkdir()

    events = []
    result = sync.sync_remote_to_local(remote, local, progress=events.append)

    assert result.ok
    assert events[0].phase == "scanning"
    assert events[-1].phase == "done"
    copying = [e for e in events if e.phase == "copying"]
    assert len(copying) == 3
    # total is known once scanning is over; done counts up to total
    assert all(e.total == 3 for e in copying)
    assert [e.done for e in copying] == [1, 2, 3]
    assert {str(e.current) for e in copying} == {"a.ma", "b.ma", "c.ma"}
    assert events[-1].done == 3 and events[-1].total == 3


def test_progress_emits_done_even_on_error_exit(tmp_path):
    # A missing remote fails before any scan, but progress still terminates.
    events = []
    result = sync.sync_remote_to_local(tmp_path / "nope", tmp_path / "local",
                                       progress=events.append)
    assert result.ok is False
    assert events and events[-1].phase == "done"


def test_sync_works_without_progress_callback(tmp_path):
    remote, local = tmp_path / "remote", tmp_path / "local"
    _write(remote / "a.ma", "a")
    local.mkdir()
    # Default (no callback) path must stay identical.
    result = sync.sync_remote_to_local(remote, local)
    assert result.ok and len(result.added) == 1
