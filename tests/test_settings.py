"""Headless tests for the path.txt local/remote location store (the tool's tiny db). No Maya.

The Setup tab writes the user's local + remote folders into a plain-text file and
reads them back; these tests exercise that store directly via an explicit file path.
"""
import _bootstrap  # noqa: F401

from pathlib import Path

from snap_on_clothing import config
from snap_on_clothing.core import settings as st


def test_read_missing_file_is_empty(tmp_path):
    loc = st.read_locations(tmp_path / "path.txt")
    assert loc.local is None and loc.remote is None


def test_write_then_read_roundtrip(tmp_path):
    pf = tmp_path / "path.txt"
    st.write_locations(tmp_path / "work", tmp_path / "server", pf)
    loc = st.read_locations(pf)
    assert loc.local == tmp_path / "work"
    assert loc.remote == tmp_path / "server"


def test_write_includes_header_comment(tmp_path):
    pf = tmp_path / "path.txt"
    st.write_locations(tmp_path / "work", None, pf)
    text = pf.read_text()
    assert text.startswith("#")  # header present
    # header lines are comments, so they round-trip to nothing but the local slot
    loc = st.read_locations(pf)
    assert loc.local == tmp_path / "work" and loc.remote is None


def test_set_local_keeps_remote(tmp_path):
    pf = tmp_path / "path.txt"
    st.write_locations(tmp_path / "work", tmp_path / "server", pf)
    st.set_local(tmp_path / "work2", pf)
    loc = st.read_locations(pf)
    assert loc.local == tmp_path / "work2"
    assert loc.remote == tmp_path / "server"  # untouched


def test_set_remote_keeps_local(tmp_path):
    pf = tmp_path / "path.txt"
    st.write_locations(tmp_path / "work", tmp_path / "server", pf)
    st.set_remote(tmp_path / "server2", pf)
    loc = st.read_locations(pf)
    assert loc.local == tmp_path / "work"  # untouched
    assert loc.remote == tmp_path / "server2"


def test_clear_local_falls_back_to_defaults(tmp_path):
    pf = tmp_path / "path.txt"
    st.write_locations(tmp_path / "work", tmp_path / "server", pf)
    st.set_local(None, pf)
    loc = st.read_locations(pf)
    assert loc.local is None
    assert loc.remote == tmp_path / "server"  # remote survives
    assert st.effective_library_roots(pf) == config.default_library_roots()


def test_comments_and_blanks_ignored(tmp_path):
    pf = tmp_path / "path.txt"
    pf.write_text(
        "# studio library\n"
        "local = /mnt/drive/clothing\n"
        "\n"
        "   remote =   /server/share/assets  \n"
        "# trailing comment\n"
    )
    loc = st.read_locations(pf)
    assert loc.local == Path("/mnt/drive/clothing")
    assert loc.remote == Path("/server/share/assets")


def test_legacy_bare_line_format_migrates_to_local(tmp_path):
    # old format: bare folder lines, no key -> first becomes local
    pf = tmp_path / "path.txt"
    pf.write_text("# old store\n/mnt/drive/clothing\n/server/share/assets\n")
    loc = st.read_locations(pf)
    assert loc.local == Path("/mnt/drive/clothing")
    assert loc.remote is None


def test_unreadable_dir_as_file_is_empty(tmp_path):
    # a directory where a file is expected -> read fails gracefully -> empty
    (tmp_path / "path.txt").mkdir()
    loc = st.read_locations(tmp_path / "path.txt")
    assert loc.local is None and loc.remote is None


def test_is_configured(tmp_path):
    pf = tmp_path / "path.txt"
    assert st.is_configured(pf) is False
    st.set_local(tmp_path / "work", pf)
    assert st.is_configured(pf) is True


def test_remote_only_is_not_configured(tmp_path):
    pf = tmp_path / "path.txt"
    st.set_remote(tmp_path / "server", pf)
    assert st.is_configured(pf) is False  # local drives "configured", not remote


def test_effective_uses_local_only(tmp_path):
    pf = tmp_path / "path.txt"
    st.write_locations(tmp_path / "work", tmp_path / "server", pf)
    # remote is a sync source, never scanned
    assert st.effective_library_roots(pf) == [tmp_path / "work"]


def test_effective_falls_back_to_defaults_when_empty(tmp_path):
    assert st.effective_library_roots(tmp_path / "path.txt") == config.default_library_roots()


def test_path_file_env_override(tmp_path, monkeypatch):
    pf = tmp_path / "custom.txt"
    monkeypatch.setenv(config.PATH_FILE_ENV, str(pf))
    # no explicit path -> uses config.path_file() -> the override
    st.set_local(tmp_path / "work", None)
    assert pf.exists()
    assert st.effective_library_roots() == [tmp_path / "work"]
