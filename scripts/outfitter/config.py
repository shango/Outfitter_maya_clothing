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

# Body variant each garment is pre-fit to (M12: two fixed body states, no unisex).
# Each garment ships as a male and a female asset; gender is a required metadata field.
GENDERS: tuple[str, ...] = ("male", "female")

# --- asset structure contract (Authoring Spec §3) -----------------------------
MESH_GROUP: str = "Mesh_GRP"   # holds the garment meshes
RIG_GROUP: str = "Rig_GRP"     # holds the cloth_* joint hierarchy (frame note below)
CTRL_GROUP: str = "Ctrl_GRP"   # holds controls; often empty since the fit rig was retired
REQUIRED_GROUPS: tuple[str, ...] = (MESH_GROUP, RIG_GROUP, CTRL_GROUP)
INFO_NODE: str = "cloth_info"
ROOT_JOINT: str = "cloth_root"
CLOTH_PREFIX: str = "cloth_"

# Selection set the authoring tool fills with a garment's recommended skin joints, so the
# rigger selects it and binds instead of guessing which of the ~89 body joints to skin to.
# A *set* (+ outliner colour), never a rename — attach matches cloth_ joints by name.
SKIN_SET: str = "cloth_skin_SET"

# --- connection contract (PRD §4 / Authoring Spec §15, LOCKED 2026-06-04) ------
# Transform compounds connected body-joint -> cloth_ joint at attach time.
# jointOrient and visibility are deliberately NOT connected.
CONNECT_ATTRS: tuple[str, ...] = ("translate", "rotate", "scale")

# Export skeleton lives under this group; attach must resolve by full DAG path,
# never short name, because a rig-internal deform skeleton shares short names.
EXPORT_SKELETON_GROUP: str = "GenHuman_Joint_GRP"  # verify-in-Maya (PRD §4 open task)

# RIG_GROUP frame note (defined above): at attach the garment's Rig_GRP is aligned to the
# rig's EXPORT_SKELETON_GROUP world frame, because that group carries a transform
# (GenHuman_Joint_GRP has rotate -90 X) and attach only connects LOCAL joint transforms.

# Any of these existing in the scene identifies the GenHuman rig as present.
# (Post-rename names; verify-in-Maya which is most stable — PRD §9 open task.)
RIG_MARKERS: tuple[str, ...] = (
    "god_m_godnode_anim",
    EXPORT_SKELETON_GROUP,
    "GenHuman",
)

# --- gendered test body (M14) -------------------------------------------------
# The tool ships ONE GenHuman and flips the male/female switch to match the chosen
# gender, because the two genders are the SAME rig differing only by this morph value
# (it moves the body MESH, not the joints — hence one shared cloth_* skeleton).
# The switch is `GH_Body_morph` (0-1) on the godnode. Verified in Maya 2026-06-24:
# female = base (0), male = full morph (1).
BODY_MORPH_NODE: str = "god_m_godnode_anim"
BODY_MORPH_ATTR: str = "GH_Body_morph"
GENDER_BODY_MORPH: dict[str, float] = {"male": 1.0, "female": 0.0}

# The bundled GenHuman the "Load test body" action references. Lives in the package's
# lib/ dir so the installer copytree ships it alongside the code; kept OUT of git (large
# rig, like the root *.ma files) and dropped in at package/release time.
BUNDLED_GENHUMAN_FILE: str = "GenHuman_rig_v03.ma"
# Namespace the test body is referenced under (the file stem, version token kept).
BUNDLED_GENHUMAN_NAMESPACE: str = BUNDLED_GENHUMAN_FILE.rsplit(".", 1)[0]

# Genie export may require specific node names present (PRD §9 open task — TBD).
# Empty = check is a no-op until the export team supplies the list.
GENIE_REQUIRED_NODES: tuple[str, ...] = ()

# Node types forbidden inside a clothing asset (Authoring Spec §10 hard "no" list).
DISALLOWED_ASSET_NODE_TYPES: tuple[str, ...] = ("blendShape", "nCloth", "nucleus")

# --- export-time cleanliness rules (Authoring Spec §10 / §13 / §11) -----------
# The hard "no" list also bans unknown nodes, animation curves and display layers,
# and requires generic shaders only. These are enforced at publish/export time on
# the saved .ma (validate_asset_summary) so a non-compliant asset never ships.

# Unknown / lost-plugin nodes — Maya parks them as these types when a plugin that
# created a node is missing; they bloat the file and break a clean re-open.
UNKNOWN_NODE_TYPES: tuple[str, ...] = ("unknown", "unknownDag", "unknownTransform")

# Timeline animation curves — keyframes driven by *time* (animCurveT*). Assets ship
# static, so these are banned. Set-driven keys (animCurveU*, driven by another attr)
# are NOT included: they're a legitimate control-rig mechanism the spec allows ("any
# Maya node types within the control rig"), and the example asset drives its fit
# lattice with animCurveUU. Only the time-input subtypes are flagged.
TIMELINE_ANIM_CURVE_TYPES: tuple[str, ...] = (
    "animCurveTL", "animCurveTA", "animCurveTU", "animCurveTT",
)

# Display layers other than Maya's built-in defaultLayer are not allowed in an asset.
DISPLAY_LAYER_TYPE: str = "displayLayer"
DEFAULT_DISPLAY_LAYERS: tuple[str, ...] = ("defaultLayer",)

# §11 Materials: generic shaders only (e.g. lambert / standardSurface). Render-engine-
# specific shaders don't survive a clean .ma export into the pipeline, so a curated
# denylist of the renderer materials studios actually use is flagged at export time.
# Extensible — add a type string here as new renderers appear. (A denylist of exact
# types is used rather than prefix matching to avoid false positives like aimConstraint.)
RENDERER_SHADER_TYPES: tuple[str, ...] = (
    # Arnold
    "aiStandardSurface", "aiToon", "aiStandardHair", "aiLambert", "aiFlat",
    "aiCarPaint", "aiSkin", "aiMatte", "aiAmbientOcclusion",
    # Redshift
    "RedshiftMaterial", "RedshiftArchitectural", "RedshiftCarPaint",
    "RedshiftSkin", "RedshiftHair", "RedshiftSubSurfaceScatter",
    # V-Ray
    "VRayMtl", "VRayCarPaintMtl", "VRayFastSSS2", "VRayBlendMtl",
    "VRayLightMtl", "VRayHairNextMtl",
    # RenderMan
    "PxrSurface", "PxrLayerSurface", "PxrDisney", "PxrHair",
    # mental ray (legacy)
    "mia_material", "mia_material_x", "mia_material_x_passes",
)

# --- sidecar metadata file extensions ----------------------------------------
SIDECAR_EXT: str = ".json"
THUMB_EXTS: tuple[str, ...] = (".png", ".jpg", ".jpeg")
ASSET_EXT: str = ".ma"

# --- turntable thumbnail ------------------------------------------------------
# Publish bakes a rotatable preview as a sprite sheet beside the still <asset>.png:
# COLS*ROWS frames orbiting the garment, tiled row-major, CELL px each. The grid is
# full (no blank trailing cells) so the layout is derivable from the image alone.
TURNTABLE_SUFFIX: str = "_turntable.png"  # <asset>_turntable.png next to <asset>.png
TURNTABLE_COLS: int = 6
TURNTABLE_ROWS: int = 4                    # 6*4 = 24 frames = 15° per step
TURNTABLE_CELL: int = 256                  # px per frame in the sheet

# --- install locations (FR-9) -------------------------------------------------
USER_ASSET_DIR_ENV: str = "OUTFITTER_ASSETS"
PATH_FILE_ENV: str = "OUTFITTER_PATH_FILE"


def _repo_root() -> Path:
    # config.py -> outfitter -> scripts -> <repo root>
    return Path(__file__).resolve().parents[2]


def package_dir() -> Path:
    """Directory of the installed ``outfitter`` package."""
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


def bundled_genhuman_path() -> Path:
    """The GenHuman rig the 'Load test body' action references (under the package lib dir).

    Ships inside the package's ``lib/`` dir so the installer's package copytree carries it
    alongside the code, but kept out of git (large rig). May not exist in a fresh checkout
    until the file is dropped in / the bundle is built; callers must handle absence with a
    clear message.
    """
    return package_dir() / "lib" / BUNDLED_GENHUMAN_FILE


def user_config_dir() -> Path:
    """Per-user tool config/data dir (holds settings + the installed library)."""
    return Path.home() / "maya" / "outfitter"


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
