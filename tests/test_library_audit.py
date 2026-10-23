"""tools/library_audit.py finds both kinds of damage, and repairs only rig stamps."""
import _bootstrap  # noqa: F401
import _assets

import importlib.util
import json
from pathlib import Path

from outfitter.core import rigs

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("library_audit",
                                               REPO / "tools" / "library_audit.py")
audit_tool = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(audit_tool)


def _library(tmp_path):
    root = tmp_path / "lib"
    # A second rig whose skeleton has GenHuman's names plus one of its own.
    gh = rigs.find_profile("genhuman")
    data = rigs.to_json_dict(gh)
    data.update(rigId="acme", displayName="Acme", exportGroup="Acme_GRP", markers=["Acme_GRP"])
    data["skeleton"]["joints"].append({**data["skeleton"]["joints"][-1],
                                       "name": "cloth_acme_only"})
    for sub in ("_rigs", "old", "half"):
        (root / sub).mkdir(parents=True)
    (root / "_rigs" / "acme.json").write_text(json.dumps(data))
    return root


def test_reports_both_and_repairs_only_the_stamp(tmp_path, capsys):
    root = _library(tmp_path)
    # Legacy GenHuman coat wrongly stamped as acme.
    stamped = _assets.write_asset_ma(root / "old" / "old.ma", joints=["cloth_root"],
                                     asset_name="old")
    stamped.with_suffix(".json").write_text(json.dumps({
        "assetName": "old", "assetType": "coat", "gender": "male", "clothVersion": "1",
        "genHumanCompat": "v03", "rigId": "acme", "rigVersions": "v03"}))
    # GenHuman coat still carrying a joint only the acme rig has: a half-done retarget.
    _assets.write_asset_ma(root / "half" / "half.ma", joints=["cloth_root", "cloth_acme_only"],
                           asset_name="half")

    assert audit_tool.audit(root, repair=False) == 2
    out = capsys.readouterr().out
    assert "WRONG RIG STAMP" in out and "UNFINISHED RETARGET" in out and "cloth_acme_only" in out
    assert json.loads(stamped.with_suffix(".json").read_text())["rigId"] == "acme"  # read-only

    assert audit_tool.audit(root, repair=True) == 2
    assert json.loads(stamped.with_suffix(".json").read_text())["rigId"] == "genhuman"
    assert len(list((root / "old").glob("old.json.bak-*"))) == 1
    assert audit_tool.audit(root, repair=False) == 1  # the retarget needs Maya, not us
