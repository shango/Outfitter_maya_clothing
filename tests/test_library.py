"""Headless tests for the library scanner."""
import json

import _bootstrap  # noqa: F401

from outfitter import config
from outfitter.core import library


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
    assert res.valid[0].turntable is None  # no sheet -> no turntable


def test_turntable_discovered(tmp_path):
    ma = tmp_path / "thing.ma"
    _write_ma(ma)
    (tmp_path / "thing.png").write_bytes(b"\x89PNG")
    sheet = tmp_path / ("thing" + config.TURNTABLE_SUFFIX)
    sheet.write_bytes(b"\x89PNG")
    res = library.scan_library([tmp_path])
    # the still stays the grid thumbnail; the sheet is offered separately as turntable
    assert res.valid[0].thumbnail == tmp_path / "thing.png"
    assert res.valid[0].turntable == sheet


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


# --- rig awareness ------------------------------------------------------------
def _write_rig_ma(path):
    """A registered rig's own .ma - a body rig, emphatically not a garment."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('//Maya ASCII 2026 scene\ncreateNode transform -n "Acme_Joint_GRP";')


def test_scan_skips_the_rigs_folder(tmp_path):
    """A 30 MB body rig must never show up in the browser as an invalid asset."""
    ma = tmp_path / "coat" / "thing.ma"
    ma.parent.mkdir(parents=True)
    _write_ma(ma)
    _write_rig_ma(tmp_path / "_rigs" / "acme_biped" / "acme_v01.ma")
    (tmp_path / "_rigs" / "acme_biped.json").write_text('{"rigId": "acme_biped"}')

    res = library.scan_library([tmp_path])

    assert len(res.assets) == 1
    assert res.assets[0].ma_path == ma
    assert res.invalid == []


def _write_asset(tmp_path, folder, rig_id=None, versions="v03", name=None):
    ma = tmp_path / folder / f"{folder}.ma"
    ma.parent.mkdir(parents=True, exist_ok=True)
    _write_ma(ma, name=name or folder)
    sidecar = ma.with_suffix(".json")
    data = {"assetName": name or folder, "assetType": "pants", "gender": "male",
            "clothVersion": "1.0.0"}
    if rig_id is None:
        data["genHumanCompat"] = versions          # legacy asset, no rig id
    else:
        data.update({"rigId": rig_id, "rigVersions": versions})
    sidecar.write_text(json.dumps(data))
    return ma


def test_for_rig_selects_only_compatible_assets(tmp_path):
    _write_asset(tmp_path, "gh_coat", rig_id="genhuman", versions="v03")
    _write_asset(tmp_path, "acme_coat", rig_id="acme_biped", versions="v01")
    res = library.scan_library([tmp_path])

    assert [a.display_name for a in res.for_rig("acme_biped", "v01")] == ["acme_coat"]
    assert [a.display_name for a in res.for_rig("genhuman", "v03")] == ["gh_coat"]


def test_for_rig_excludes_a_version_mismatch(tmp_path):
    _write_asset(tmp_path, "acme_coat", rig_id="acme_biped", versions="v01")
    res = library.scan_library([tmp_path])
    assert res.for_rig("acme_biped", "v02") == []
    assert len(res.for_rig("acme_biped")) == 1  # rig matches, version unchecked


def test_for_rig_treats_legacy_assets_as_genhuman(tmp_path):
    """An untouched pre-existing library must still be fully visible under GenHuman."""
    _write_asset(tmp_path, "old_coat", rig_id=None, versions="v03")
    res = library.scan_library([tmp_path])
    assert [a.display_name for a in res.for_rig("genhuman", "v03")] == ["old_coat"]
    assert res.for_rig("acme_biped", "v01") == []
