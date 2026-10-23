"""Headless tests for renaming library assets (built on delete). Filesystem only, no Maya."""
import _bootstrap  # noqa: F401

import json
import shutil
from pathlib import Path

import pytest

from outfitter.core import delete, library, ma_parse, rename, sync

REPO = Path(__file__).resolve().parents[1]
STARTER = REPO / "assets" / "trench_coat_A"


def _starter(root):
    """A copy of the real starter asset (README, sidecar, .ma) under ``root``."""
    shutil.copytree(STARTER, root / STARTER.name)
    return root / STARTER.name / f"{STARTER.name}.ma"


def _write(path, text="x"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_rename_real_asset_locally_and_remotely(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    ma = _starter(local)
    _starter(remote)

    result = rename.rename_asset(ma, "Long Coat", local, remote, by="artist")

    assert result.local_ma == local / "Long_Coat" / "Long_Coat.ma"
    assert result.remote_ma == remote / "Long_Coat" / "Long_Coat.ma"
    for root in (local, remote):
        assert sorted(p.name for p in (root / "Long_Coat").iterdir()) == [
            "Long_Coat.json", "Long_Coat.ma", "README.md"]
        assert not (root / STARTER.name).exists()
    # the library shows the name as typed, from either metadata source
    assert library.load_asset(result.local_ma).display_name == "Long Coat"
    assert ma_parse.read_info_attrs(result.local_ma)["assetName"] == "Long Coat"
    # old name tombstoned for other artists; the old files are in the trash
    assert delete.read_tombstones(remote).keys() == {"trench_coat_A/trench_coat_A.ma"}
    assert (result.deleted.local_trash / "trench_coat_A.ma").is_file()


def test_ma_changes_only_the_asset_name(tmp_path):
    ma = _starter(tmp_path)
    before = ma.read_bytes()

    assert rename.set_ma_asset_name(ma, "Long Coat")

    after = ma.read_bytes()
    assert after.replace(b'"Long Coat"', b'"trench_coat_A"') == before
    assert after.count(b'"Long Coat"') == 1   # top group etc. untouched


def test_ma_crlf_and_odd_bytes_round_trip(tmp_path):
    ma = tmp_path / "a.ma"
    ma.write_bytes(b'//Maya ASCII\r\ncreateNode transform -n "x";\r\n\tsetAttr ".n" -type '
                   b'"string" "caf\xe9";\r\ncreateNode network -n "cloth_info";\r\n'
                   b'\tsetAttr ".assetName" -type "string" "a";\r\n')

    assert rename.set_ma_asset_name(ma, 'b "q"')

    assert ma.read_bytes().endswith(
        b'\tsetAttr ".assetName" -type "string" "b \\"q\\"";\r\n')
    assert b'"caf\xe9"' in ma.read_bytes()
    assert ma_parse.read_info_attrs(ma)["assetName"] == 'b "q"'


def test_ma_without_cloth_info_is_left_alone(tmp_path):
    ma = _write(tmp_path / "a.ma", 'createNode transform -n "x";\n')

    assert rename.set_ma_asset_name(ma, "b") is False
    assert ma.read_text() == 'createNode transform -n "x";\n'


def test_sidecar_keeps_its_key_style(tmp_path):
    snake = _write(tmp_path / "s.json", json.dumps({"asset_name": "a", "gender": "male"}))
    camel = _write(tmp_path / "c.json", json.dumps({"assetName": "a"}))

    rename.set_sidecar_asset_name(snake, "b")
    rename.set_sidecar_asset_name(camel, "b")

    assert json.loads(snake.read_text()) == {"asset_name": "b", "gender": "male"}
    assert json.loads(camel.read_text()) == {"assetName": "b"}


def test_loose_asset_renamed_in_place(tmp_path):
    local = tmp_path / "local"
    _write(local / "coat.ma")
    _write(local / "coat.json", json.dumps({"assetName": "coat"}))
    _write(local / "coat_thumb.jpg")
    _write(local / "hat.ma")

    result = rename.rename_asset(local / "coat.ma", "parka", local)

    assert sorted(p.name for p in local.iterdir() if p.is_file()) == [
        "hat.ma", "parka.json", "parka.ma", "parka_thumb.jpg"]
    assert json.loads(result.local_ma.with_suffix(".json").read_text()) == {
        "assetName": "parka"}


def test_unpublished_asset_renames_locally_only(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    remote.mkdir()
    ma = _starter(local)

    result = rename.rename_asset(ma, "draft2", local, remote)

    assert result.remote_ma is None and result.deleted.tombstone is None
    assert list(remote.iterdir()) == []


def test_each_copy_keeps_its_own_content(tmp_path):
    # unpublished local edits must not reach the shared library through a rename
    local, remote = tmp_path / "local", tmp_path / "remote"
    ma = _starter(local)
    _starter(remote)
    (local / STARTER.name / "README.md").write_text("local edit")

    result = rename.rename_asset(ma, "parka", local, remote)

    assert (result.remote_ma.parent / "README.md").read_text() != "local edit"
    assert (result.local_ma.parent / "README.md").read_text() == "local edit"


@pytest.mark.parametrize("where", ["local", "remote"])
def test_refuses_a_taken_name(tmp_path, where):
    local, remote = tmp_path / "local", tmp_path / "remote"
    ma = _starter(local)
    _starter(remote)
    _write(tmp_path / where / "parka" / "parka.ma")

    with pytest.raises(FileExistsError):
        rename.rename_asset(ma, "parka", local, remote)
    assert ma.is_file() and (remote / STARTER.name).is_dir()  # nothing touched


@pytest.mark.parametrize("name", ["", "   ", "trench_coat_A", "trench coat A"])
def test_refuses_blank_or_same_name(tmp_path, name):
    ma = _starter(tmp_path)
    with pytest.raises(ValueError):
        rename.rename_asset(ma, name, tmp_path)


def test_renaming_onto_a_deleted_name_revives_it(tmp_path):
    local, remote = tmp_path / "local", tmp_path / "remote"
    ma = _starter(local)
    _starter(remote)
    delete.write_tombstone(remote, "parka/parka.ma")

    rename.rename_asset(ma, "parka", local, remote)

    assert "parka/parka.ma" not in delete.read_tombstones(remote)


def test_other_artist_sync_follows_the_rename(tmp_path):
    local, remote, other = tmp_path / "local", tmp_path / "remote", tmp_path / "other"
    _starter(remote)
    other.mkdir()
    sync.sync_remote_to_local(remote, other)      # the other artist has the old name
    ma = _starter(local)

    rename.rename_asset(ma, "parka", local, remote)
    result = sync.sync_remote_to_local(remote, other)

    names = [a.display_name for a in library.scan_library([other]).assets]
    assert names == ["parka"]
    assert result.removed == [Path("trench_coat_A/trench_coat_A.ma")]


def test_lone_asset_in_category_folder_renamed_in_place(tmp_path):
    local = tmp_path / "local"
    _write(local / "hats" / "beanie.ma")
    _write(local / "hats" / "notes.txt")

    result = rename.rename_asset(local / "hats" / "beanie.ma", "wool_beanie", local)

    assert result.local_ma == local / "hats" / "wool_beanie.ma"
    assert sorted(p.name for p in (local / "hats").iterdir()) == [
        "notes.txt", "wool_beanie.ma"]


def test_failed_remote_copy_leaves_nothing_behind(tmp_path, monkeypatch):
    local, remote = tmp_path / "local", tmp_path / "remote"
    ma = _starter(local)
    _starter(remote)
    real_copy = rename._copy_renamed

    def copy_then_fail_on_remote(root, ma_path, new_name):
        if root == remote:
            real_copy(root, ma_path, new_name)  # partly written, then the share fails
            raise OSError("share went away")
        return real_copy(root, ma_path, new_name)

    monkeypatch.setattr(rename, "_copy_renamed", copy_then_fail_on_remote)
    with pytest.raises(OSError):
        rename.rename_asset(ma, "parka", local, remote)

    for root in (local, remote):
        assert sorted(p.name for p in root.iterdir()) == [STARTER.name]
    assert delete.read_tombstones(remote) == {}


def test_corrupt_sidecar_rolls_back_loose_rename(tmp_path):
    local = tmp_path / "local"
    _write(local / "coat.ma")
    _write(local / "coat.json", "{not json")
    _write(local / "hat.ma")

    with pytest.raises(ValueError):
        rename.rename_asset(local / "coat.ma", "parka", local)

    assert sorted(p.name for p in local.iterdir()) == ["coat.json", "coat.ma", "hat.ma"]
