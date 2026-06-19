"""Headless tests for the library scanner."""
import json

import _bootstrap  # noqa: F401

from snap_on_clothing.core import library


def _write_ma(path, info_node=True, name="x", gender="male"):
    lines = ['//Maya ASCII 2026 scene', 'createNode transform -n "cloth_x";']
    if info_node:
        lines += [
            'createNode network -n "cloth_info";',
            f'setAttr ".assetName" -type "string" "{name}";',
            'setAttr ".assetType" -type "string" "pants";',
            f'setAttr ".gender" -type "string" "{gender}";',
            'setAttr ".clothVersion" -type "string" "1.0.0";',
            'setAttr ".genHumanCompat" -type "string" "v03";',
        ]
    path.write_text("\n".join(lines))


def test_scan_skips_missing_roots(tmp_path):
    res = library.scan_library([tmp_path / "nope"])
    assert res.assets == []
    assert (tmp_path / "nope") in res.skipped_roots


def test_load_from_ma_info(tmp_path):
    ma = tmp_path / "coat" / "thing.ma"
    ma.parent.mkdir(parents=True)
    _write_ma(ma)
    res = library.scan_library([tmp_path])
    assert len(res.valid) == 1
    a = res.valid[0]
    assert a.source == "ma_info"
    assert a.metadata.asset_type == "pants"


def test_sidecar_wins_over_ma(tmp_path):
    ma = tmp_path / "thing.ma"
    _write_ma(ma)
    (tmp_path / "thing.json").write_text(json.dumps({
        "assetName": "sidecar_name", "assetType": "coat", "gender": "male",
        "clothVersion": "9.9.9", "genHumanCompat": "v03",
    }))
    res = library.scan_library([tmp_path])
    a = res.valid[0]
    assert a.source == "sidecar"
    assert a.metadata.asset_name == "sidecar_name"
    assert a.metadata.cloth_version == "9.9.9"


def test_invalid_asset_is_listed_not_dropped(tmp_path):
    ma = tmp_path / "broken.ma"
    _write_ma(ma, info_node=False)
    res = library.scan_library([tmp_path])
    assert len(res.assets) == 1
    assert len(res.invalid) == 1
    assert res.invalid[0].display_name == "broken"
    assert res.invalid[0].errors


def test_thumbnail_discovered(tmp_path):
    ma = tmp_path / "thing.ma"
    _write_ma(ma)
    (tmp_path / "thing.png").write_bytes(b"\x89PNG")
    res = library.scan_library([tmp_path])
    assert res.valid[0].thumbnail == tmp_path / "thing.png"


def test_by_type_filter(tmp_path):
    a = tmp_path / "a.ma"; _write_ma(a)
    res = library.scan_library([tmp_path])
    assert len(res.by_type("pants")) == 1
    assert res.by_type("coat") == []


def test_by_gender_filter(tmp_path):
    _write_ma(tmp_path / "m.ma", name="m_a", gender="male")
    _write_ma(tmp_path / "f.ma", name="f_a", gender="female")
    res = library.scan_library([tmp_path])
    assert {a.display_name for a in res.by_gender("male")} == {"m_a"}
    assert {a.display_name for a in res.by_gender("female")} == {"f_a"}
    # sort key is (gender, type, name): female sorts before male
    assert [a.gender for a in res.valid] == ["female", "male"]


def test_fixture_asset_loads():
    res = library.scan_library([_bootstrap.FIXTURES])
    names = {a.display_name for a in res.valid}
    assert "sample_coat_A" in names
