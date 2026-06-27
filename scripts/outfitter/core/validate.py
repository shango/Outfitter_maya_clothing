"""Validation - hard-stop checks before any scene mutation (FR-2).

Two layers, both pure (the scene layer talks only to a ``SceneGateway``):

  * :func:`validate_asset_summary` - file-only, from an ``MaSummary`` read off
    disk by ``ma_parse`` (no Maya, no import). Structure / naming / forbidden
    nodes per the Authoring Spec.
  * :func:`validate_scene_preconditions` - scene-side, pre-import: rig present,
    version compatible, target namespace free.

Per FR-2 the caller must treat any ``ERROR`` as a hard stop and leave the scene
unchanged. Issues carry a code + the offending node + a fix hint for clear
reporting ("what failed / which node / how to fix").
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from .. import config
from .asset import AssetMetadata
from .ma_parse import MaSummary
from .scene import SceneGateway


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class Issue:
    severity: Severity
    code: str
    message: str
    node: str = ""
    fix: str = ""

    def __str__(self) -> str:
        loc = f" [{self.node}]" if self.node else ""
        tail = f" - fix: {self.fix}" if self.fix else ""
        return f"{self.severity.value.upper()}: {self.message}{loc}{tail}"


@dataclass
class ValidationReport:
    issues: list[Issue] = field(default_factory=list)

    def add(self, severity: Severity, code: str, message: str, node: str = "", fix: str = "") -> None:
        self.issues.append(Issue(severity, code, message, node, fix))

    def error(self, code: str, message: str, node: str = "", fix: str = "") -> None:
        self.add(Severity.ERROR, code, message, node, fix)

    def warn(self, code: str, message: str, node: str = "", fix: str = "") -> None:
        self.add(Severity.WARNING, code, message, node, fix)

    def info(self, code: str, message: str, node: str = "", fix: str = "") -> None:
        self.add(Severity.INFO, code, message, node, fix)

    def extend(self, other: "ValidationReport") -> None:
        self.issues.extend(other.issues)

    @property
    def errors(self) -> list[Issue]:
        return [i for i in self.issues if i.severity is Severity.ERROR]

    @property
    def warnings(self) -> list[Issue]:
        return [i for i in self.issues if i.severity is Severity.WARNING]

    @property
    def ok(self) -> bool:
        """True when there are no ERROR issues (warnings/info do not block)."""
        return not self.errors

    def summary_line(self) -> str:
        return f"{len(self.errors)} error(s), {len(self.warnings)} warning(s)"


# --------------------------------------------------------------------------- #
# File-only validation (no Maya)
# --------------------------------------------------------------------------- #
def validate_asset_summary(summary: MaSummary, metadata: AssetMetadata | None) -> ValidationReport:
    """Validate an asset's on-disk structure from a parsed ``MaSummary``."""
    report = ValidationReport()

    # --- metadata / info node (Authoring Spec §12) ---
    if metadata is None:
        report.error(
            "no_metadata",
            "asset has no readable metadata (cloth_info or sidecar)",
            node=config.INFO_NODE,
            fix="add a cloth_info node with assetName/assetType/gender/clothVersion/genHumanCompat",
        )
    if not summary.has_node(config.INFO_NODE):
        report.error("no_info_node", "missing info node", node=config.INFO_NODE,
                     fix=f"add a '{config.INFO_NODE}' network node")

    # --- required hierarchy (Authoring Spec §3) ---
    for grp in config.REQUIRED_GROUPS:
        if not summary.has_node(grp):
            report.error("missing_group", f"missing required group '{grp}'", node=grp,
                         fix=f"create {grp} under the asset top group")

    # --- connection skeleton (Authoring Spec §4) ---
    if not summary.has_node(config.ROOT_JOINT):
        report.error("no_root_joint", f"missing root joint '{config.ROOT_JOINT}'",
                     node=config.ROOT_JOINT,
                     fix=f"duplicate body 'root', rename to '{config.ROOT_JOINT}', parent under Rig_GRP")

    cloth_joints = summary.cloth_joints()
    if not cloth_joints:
        report.error("no_cloth_joints", "no cloth_ connection joints found",
                     fix="duplicate the needed body joints and prefix each with 'cloth_'")
    # naming hygiene: the spec forbids a _jnt suffix on connection joints
    for j in cloth_joints:
        if j.endswith("_jnt"):
            report.error("bad_joint_suffix", f"connection joint '{j}' has a '_jnt' suffix",
                         node=j, fix="name = 'cloth_' + EXACT body joint name, no '_jnt'")

    # --- scene-cleanliness hard rules (Authoring Spec §10 / §13) ---
    if summary.has_references:
        report.error("has_references", "asset file contains references",
                     fix="import/remove all references before delivery")
    if summary.has_namespaces:
        report.error("has_namespaces", "asset file contains namespaces",
                     fix="remove all namespaces; the tool applies one at import")
    for node_type in config.DISALLOWED_ASSET_NODE_TYPES:
        for node in summary.nodes_of_type(node_type):
            report.error("forbidden_node_type", f"forbidden node type '{node_type}'", node=node,
                         fix=f"remove {node_type} nodes; blendshapes/sim are not supported")

    # --- unknown / lost-plugin nodes (Authoring Spec §10 / §13) ---
    for node in summary.nodes_of_types(config.UNKNOWN_NODE_TYPES):
        report.error("unknown_node", f"unknown (lost-plugin) node '{node}'", node=node,
                     fix="delete unknown nodes - Edit ▸ Delete All by Type ▸ Unknown Nodes")

    # --- timeline animation curves (Authoring Spec §10 / §13: assets ship static) ---
    # Time-input curves only; set-driven keys (animCurveU*) are an allowed rig mechanism.
    for node in summary.nodes_of_types(config.TIMELINE_ANIM_CURVE_TYPES):
        report.error("anim_curve", f"timeline animation curve '{node}' in asset", node=node,
                     fix="delete all timeline keyframes; a delivered asset must be static "
                         "(set-driven keys are fine - only time-based animation is banned)")

    # --- display layers other than the default (Authoring Spec §10 / §13) ---
    for node in summary.nodes_of_type(config.DISPLAY_LAYER_TYPE):
        if node in config.DEFAULT_DISPLAY_LAYERS:
            continue
        report.error("display_layer", f"display layer '{node}' in asset", node=node,
                     fix="remove all display layers before export")

    # --- render-engine-specific materials (Authoring Spec §11: generic shaders only) ---
    for node in summary.nodes_of_types(config.RENDERER_SHADER_TYPES):
        report.error(
            "renderer_shader",
            f"render-engine shader '{node}' (type '{summary.node_types.get(node)}')",
            node=node,
            fix="use a generic shader (lambert / standardSurface); render-engine-specific "
                "materials aren't allowed and don't survive a clean .ma export")

    # --- duplicate short names (FR-2) ---
    for name, count in summary.duplicate_names.items():
        report.error("duplicate_name", f"node name '{name}' declared {count} times", node=name,
                     fix="make all node names unique within the asset")

    return report


# --------------------------------------------------------------------------- #
# Scene-side validation (via SceneGateway, pre-import)
# --------------------------------------------------------------------------- #
def validate_scene_preconditions(
    scene: SceneGateway,
    namespace: str,
    metadata: AssetMetadata | None,
    *,
    registered_namespaces: tuple[str, ...] = (),
    export_group: str = config.EXPORT_SKELETON_GROUP,
) -> ValidationReport:
    """Checks that must pass against the live scene *before* importing the asset.

    ``export_group`` is the resolved export-skeleton group of the *chosen* rig
    (multi-rig: derived from the user's selection). The rig-present gate keys off
    it directly, so a namespaced rig validates iff the user actually targeted it.
    """
    report = ValidationReport()

    # --- GenHuman rig present (FR-2) ---
    # The chosen rig is identified by its export-skeleton group; if that resolves,
    # the rig is present and is the one attach will bind to (multi-rig safe, §4).
    if not scene.exists(export_group):
        report.error(
            "no_rig", "GenHuman rig not found in scene",
            node=export_group,
            fix="select any node of the target GenHuman rig, then Attach "
                f"(looked for export group '{export_group}')",
        )

    # --- version compatibility (FR-2; detection is best-effort, PRD §9) ---
    if metadata is not None:
        scene_version = scene.genhuman_version()
        if scene_version is None:
            report.warn("version_unknown",
                        "could not detect the scene's GenHuman version; skipping compat check",
                        fix="set a genHumanVersion attr on a rig marker node")
        elif not metadata.supports(scene_version):
            report.error(
                "version_incompat",
                f"asset supports {', '.join(metadata.genhuman_compat)} but scene is {scene_version}",
                fix="use an asset whose genHumanCompat includes the scene version",
            )

    # --- target namespace must be free (FR-2 / §4) ---
    if namespace in registered_namespaces:
        report.error("ns_in_use", f"namespace '{namespace}' already has an attached asset",
                     node=namespace, fix="choose a different instance name")
    elif scene.namespace_exists(namespace):
        report.error("ns_exists", f"namespace '{namespace}' already exists in the scene",
                     node=namespace, fix="choose a different instance name")

    # --- Genie-required node names (FR-8; list TBD, PRD §9) ---
    for required in config.GENIE_REQUIRED_NODES:
        if not scene.exists(required):
            report.error("genie_missing", f"Genie-required node '{required}' not present",
                         node=required, fix="ensure the export-required node exists before attach")

    return report
