"""Headless tests for the pure install logic (no Maya). Verifies overwrite of the
package, non-clobbering asset merge, and idempotent re-run."""
import sys
from pathlib import Path

import _bootstrap  # noqa: F401  (puts scripts/ on path)

# the `installer/` package lives at the distribution root, one up from tests/
_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from installer import installer_core  # noqa: E402


def _make_distribution(root: Path) -> Path:
    """Build a fake distribution tree: scripts/snap_on_clothing + assets/."""
    pkg = root / "scripts" / "snap_on_clothing"
    (pkg / "core").mkdir(parents=True)
    (pkg / "__init__.py").write_text("# v1\n")
    (pkg / "core" / "asset.py").write_text("# asset v1\n")
    (pkg / "__pycache__").mkdir()
    (pkg / "__pycache__" / "stale.pyc").write_text("junk")
    (root / "scripts" / "path.txt.example").write_text("# example\n")
    assets = root / "assets"
    (assets / "coats").mkdir(parents=True)
    (assets / "coats" / "trench.ma").write_text("//coat\n")
    (assets / "library.json").write_text("{}\n")
    return root


def test_install_package_copies_and_skips_pycache(tmp_path):
    dist = _make_distribution(tmp_path / "dist")
    scripts_dir = tmp_path / "maya" / "scripts"
    dest = installer_core.install_package(dist / "scripts", scripts_dir)
    assert (dest / "__init__.py").read_text() == "# v1\n"
    assert (dest / "core" / "asset.py").exists()
    assert not (dest / "__pycache__").exists()  # ignored


def test_install_package_overwrites_on_upgrade(tmp_path):
    dist = _make_distribution(tmp_path / "dist")
    scripts_dir = tmp_path / "maya" / "scripts"
    installer_core.install_package(dist / "scripts", scripts_dir)
    # simulate a newer build
    (dist / "scripts" / "snap_on_clothing" / "__init__.py").write_text("# v2\n")
    dest = installer_core.install_package(dist / "scripts", scripts_dir)
    assert (dest / "__init__.py").read_text() == "# v2\n"


def test_install_assets_merges_without_clobbering(tmp_path):
    dist = _make_distribution(tmp_path / "dist")
    target = tmp_path / "userassets"
    # pre-existing user asset with the SAME relative path must be preserved
    (target / "coats").mkdir(parents=True)
    (target / "coats" / "trench.ma").write_text("//MY edited coat\n")

    copied, skipped = installer_core.install_assets(dist / "assets", target)
    assert copied == 1  # library.json is new
    assert skipped == 1  # trench.ma already present
    assert (target / "coats" / "trench.ma").read_text() == "//MY edited coat\n"
    assert (target / "library.json").exists()


def test_install_assets_missing_source_is_noop(tmp_path):
    copied, skipped = installer_core.install_assets(tmp_path / "nope", tmp_path / "t")
    assert (copied, skipped) == (0, 0)


def test_full_install_idempotent(tmp_path):
    dist = _make_distribution(tmp_path / "dist")
    scripts_dir = tmp_path / "maya" / "scripts"
    target = tmp_path / "userassets"

    r1 = installer_core.install(
        source_root=dist, scripts_dir=scripts_dir, assets_target=target)
    assert r1.ok, r1.errors
    assert r1.assets_copied == 2 and r1.assets_skipped == 0
    assert (scripts_dir / "snap_on_clothing" / "__init__.py").exists()

    # second run: package re-copied, every asset already present -> all skipped
    r2 = installer_core.install(
        source_root=dist, scripts_dir=scripts_dir, assets_target=target)
    assert r2.ok
    assert r2.assets_copied == 0 and r2.assets_skipped == 2


def test_install_ships_path_example_without_clobbering_real_path_txt(tmp_path):
    dist = _make_distribution(tmp_path / "dist")
    scripts_dir = tmp_path / "maya" / "scripts"
    scripts_dir.mkdir(parents=True)
    # a user's real path.txt must survive the install untouched
    (scripts_dir / "path.txt").write_text("/my/drive/clothing\n")

    installer_core.install(
        source_root=dist, scripts_dir=scripts_dir, assets_target=tmp_path / "a")
    assert (scripts_dir / "path.txt.example").exists()
    assert (scripts_dir / "path.txt").read_text() == "/my/drive/clothing\n"


def test_full_install_missing_package_fails(tmp_path):
    empty = tmp_path / "empty"
    (empty / "scripts").mkdir(parents=True)
    r = installer_core.install(
        source_root=empty, scripts_dir=tmp_path / "s", assets_target=tmp_path / "a")
    assert not r.ok
    assert any("package copy failed" in e for e in r.errors)
