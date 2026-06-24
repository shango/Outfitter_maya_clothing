"""Pure install logic — copy the package + starter assets into a Maya profile.

No ``maya`` import: every path is passed in, so the whole installer is unit-tested
headlessly with temp dirs. ``install.py`` (the drop handler) supplies the real
Maya paths and then calls :func:`install`.

Policy (FR-9):
  * The ``outfitter`` package is **overwritten** on every run so re-dropping
    a newer build upgrades cleanly (``__pycache__`` is never copied).
  * Bundled starter assets are **merged, never clobbered**: a file is copied only
    when the target does not already exist, so a user's own/edited assets and any
    files they added survive an upgrade.
  * The whole thing is idempotent — a second run copies the package again and
    skips every asset that is already present.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path

PACKAGE_NAME = "outfitter"
_IGNORE = shutil.ignore_patterns("__pycache__", "*.pyc", ".pytest_cache")


@dataclass
class InstallResult:
    ok: bool = True
    package_dest: Path | None = None
    assets_copied: int = 0
    assets_skipped: int = 0
    messages: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def log(self, msg: str) -> None:
        self.messages.append(msg)

    def fail(self, msg: str) -> None:
        self.ok = False
        self.errors.append(msg)

    def summary(self) -> str:
        head = "Outfitter installed" if self.ok else "Outfitter install FAILED"
        return (f"{head}: package -> {self.package_dest}; "
                f"assets {self.assets_copied} copied / {self.assets_skipped} kept; "
                f"{len(self.errors)} error(s)")


def install_package(source_scripts: Path, scripts_dir: Path) -> Path:
    """Copy ``<source_scripts>/outfitter`` into ``scripts_dir`` (overwrite).

    Returns the destination package dir. Raises ``FileNotFoundError`` if the
    source package is missing.
    """
    src = Path(source_scripts) / PACKAGE_NAME
    if not src.is_dir():
        raise FileNotFoundError(f"source package not found: {src}")
    dest = Path(scripts_dir) / PACKAGE_NAME
    Path(scripts_dir).mkdir(parents=True, exist_ok=True)
    shutil.copytree(src, dest, ignore=_IGNORE, dirs_exist_ok=True)
    return dest


def install_path_example(source_scripts: Path, scripts_dir: Path) -> bool:
    """Ship ``path.txt.example`` beside the package so the format is discoverable.

    The template is safe to overwrite on upgrade. The user's real ``path.txt`` (if
    any) is never touched. Returns ``True`` when an example was copied.
    """
    src = Path(source_scripts) / "path.txt.example"
    if not src.is_file():
        return False
    Path(scripts_dir).mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, Path(scripts_dir) / "path.txt.example")
    return True


def install_assets(bundled_assets: Path, assets_target: Path) -> tuple[int, int]:
    """Merge ``bundled_assets`` into ``assets_target`` without clobbering.

    Returns ``(copied, skipped)``. A bundled file is copied only when no file
    already exists at the target path, so user assets are never overwritten.
    Missing source dir is a no-op ``(0, 0)``.
    """
    src_root = Path(bundled_assets)
    if not src_root.is_dir():
        return (0, 0)
    target_root = Path(assets_target)
    copied = skipped = 0
    for src in sorted(src_root.rglob("*")):
        if src.is_dir() or "__pycache__" in src.parts:
            continue
        rel = src.relative_to(src_root)
        dst = target_root / rel
        if dst.exists():
            skipped += 1
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        copied += 1
    return (copied, skipped)


def install(
    *,
    source_root: Path,
    scripts_dir: Path,
    assets_target: Path,
    bundled_assets: Path | None = None,
) -> InstallResult:
    """Run the full install: package then starter assets.

    ``source_root`` is the distribution root (the dir holding ``scripts/`` and
    ``assets/``). ``scripts_dir`` is Maya's user script dir; ``assets_target`` is
    the per-user clothing library root.
    """
    result = InstallResult()
    source_root = Path(source_root)
    if bundled_assets is None:
        bundled_assets = source_root / "assets"

    try:
        dest = install_package(source_root / "scripts", scripts_dir)
        result.package_dest = dest
        result.log(f"package -> {dest}")
        if install_path_example(source_root / "scripts", scripts_dir):
            result.log(f"path.txt.example -> {scripts_dir}")
    except Exception as exc:  # noqa: BLE001 — report, never raise into Maya
        result.fail(f"package copy failed: {exc}")
        return result

    try:
        copied, skipped = install_assets(bundled_assets, assets_target)
        result.assets_copied = copied
        result.assets_skipped = skipped
        result.log(f"assets -> {assets_target} ({copied} copied, {skipped} kept)")
    except Exception as exc:  # noqa: BLE001
        result.fail(f"asset copy failed: {exc}")

    return result
