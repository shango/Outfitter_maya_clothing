"""Static configuration + small enums shared across the tool.

Pure data only — no Maya, no PySide6, no I/O at import. The installer (FR-9) is
responsible for writing the user's library roots; until then ``default_library_roots``
returns the bundled ``assets/`` dir if present plus the per-user install location.
"""
from __future__ import annotations

import os
from pathlib import Path

# --- asset taxonomy (Authoring Spec §12: assetType) ---------------------------
ASSET_TYPES: tuple[str, ...] = ("shoes", "pants", "shirt", "dress", "coat", "hat")

# --- asset structure contract (Authoring Spec §3) -----------------------------
REQUIRED_GROUPS: tuple[str, ...] = ("Mesh_GRP", "Rig_GRP", "Ctrl_GRP")
INFO_NODE: str = "cloth_info"
ROOT_JOINT: str = "cloth_root"
CLOTH_PREFIX: str = "cloth_"
FIT_CTRL: str = "cloth_fit_ctrl"
FIT_ATTR_PREFIX: str = "fit_"

# --- connection contract (PRD §4 / Authoring Spec §15, LOCKED 2026-06-04) ------
# Transform compounds connected body-joint -> cloth_ joint at attach time.
# jointOrient and visibility are deliberately NOT connected.
CONNECT_ATTRS: tuple[str, ...] = ("translate", "rotate", "scale")

# Export skeleton lives under this group; attach must resolve by full DAG path,
# never short name, because a rig-internal deform skeleton shares short names.
EXPORT_SKELETON_GROUP: str = "GenHuman_Joint_GRP"  # verify-in-Maya (PRD §4 open task)

# Any of these existing in the scene identifies the GenHuman rig as present.
# (Post-rename names; verify-in-Maya which is most stable — PRD §9 open task.)
RIG_MARKERS: tuple[str, ...] = (
    "god_m_godnode_anim",
    EXPORT_SKELETON_GROUP,
    "GenHuman",
)

# Genie export may require specific node names present (PRD §9 open task — TBD).
# Empty = check is a no-op until the export team supplies the list.
GENIE_REQUIRED_NODES: tuple[str, ...] = ()

# Node types forbidden inside a clothing asset (Authoring Spec §10 hard "no" list).
DISALLOWED_ASSET_NODE_TYPES: tuple[str, ...] = ("blendShape", "nCloth", "nucleus")

# --- sidecar metadata file extensions ----------------------------------------
SIDECAR_EXT: str = ".json"
THUMB_EXTS: tuple[str, ...] = (".png", ".jpg", ".jpeg")
ASSET_EXT: str = ".ma"

# --- install locations (FR-9) -------------------------------------------------
USER_ASSET_DIR_ENV: str = "SNAP_ON_CLOTHING_ASSETS"
PATH_FILE_ENV: str = "SNAP_ON_CLOTHING_PATH_FILE"


def _repo_root() -> Path:
    # config.py -> snap_on_clothing -> scripts -> <repo root>
    return Path(__file__).resolve().parents[2]


def package_dir() -> Path:
    """Directory of the installed ``snap_on_clothing`` package."""
    return Path(__file__).resolve().parent


def path_file() -> Path:
    """The library-roots store: a plain-text file beside the package, in the scripts dir.

    One folder per line (blank lines and ``#`` comments ignored). The Setup tab
    reads and writes this file, and it can equally be hand-edited or shipped with a
    studio install. Lives *beside* the package, never inside it, so an installer
    upgrade (which overwrites the package dir) leaves it untouched. Overridable via
    env for tests.
    """
    override = os.environ.get(PATH_FILE_ENV)
    if override:
        return Path(override)
    return package_dir().parent / "path.txt"


def bundled_asset_dir() -> Path:
    """The starter library shipped in the repo / installer bundle."""
    return _repo_root() / "assets"


def user_config_dir() -> Path:
    """Per-user tool config/data dir (holds settings + the installed library)."""
    return Path.home() / "maya" / "snap_on_clothing"


def user_asset_dir() -> Path:
    """Per-user installed library root (overridable via env for tests)."""
    override = os.environ.get(USER_ASSET_DIR_ENV)
    if override:
        return Path(override)
    return user_config_dir() / "assets"


def default_library_roots() -> list[Path]:
    """Library roots scanned when the user has configured none.

    Order matters: user dir first (their installed/added assets win), bundled
    starter library second. Non-existent paths are kept; the scanner skips them.
    """
    return [user_asset_dir(), bundled_asset_dir()]
