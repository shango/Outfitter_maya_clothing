"""Rig Check: what is wrong with a body rig, and what can be done about each finding.

The pure half of the Rig Check tab. :mod:`core.maya_rig_check` gathers :class:`RigFacts` from
the open scene and applies fixes; this module decides what the facts mean. Every rule here
came out of onboarding a real rig (MichaelC, Jenn, Eric, Seth, GenHuman 3.6).

Each :class:`Issue` says how it can be resolved, and that is what the tab offers:

  * ``FIX_SAFE``: cannot change how the rig deforms. One click, and "Fix all safe" includes it.
  * ``FIX_REVIEW``: a real fix with a cost the artist should read first, so it is never batched.
  * ``FIX_INPUT``: needs a value from the artist (the rig's name).
  * ``FIX_MANUAL``: a decision or an edit the tool must not make.

The tab shows ``detail`` as the cause and ``action`` as the fix. Keep both to one short sentence
that names the exact node or control: the artist acts on them without further explanation.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

ERROR = "error"   # registering now gives a broken or misidentified rig
WARN = "warn"     # works, but off spec or a known source of trouble
INFO = "info"

FIX_SAFE = "safe"
FIX_REVIEW = "review"
FIX_INPUT = "input"
FIX_MANUAL = "manual"

JOINT_GRP = "_Joint_GRP"
MESH_GRP = "_Mesh_GRP"
BODY_MESH = "_body_mesh"

# Clothing Asset Authoring Spec section 6, which applies to body rigs too.
SKIN_METHOD = 0
MAX_INFLUENCES = 4
NORMALIZE_INTERACTIVE = 1

# Largest difference between bindPreMatrix * worldMatrix and identity that still counts as
# at bind. Healthy rigs measure under 1e-5; a rig off its bind pose measures above 1.
BIND_TOLERANCE = 1e-3
WEIGHT_SUM_TOLERANCE = 1e-4

_LEVEL_ORDER = {ERROR: 0, WARN: 1, INFO: 2}


@dataclass(frozen=True)
class Issue:
    """One finding. ``key`` is stable across scans, so a fix can be re-validated by it."""

    key: str
    level: str
    category: str
    title: str
    detail: str           # the cause: one short sentence, then any data lines
    action: str           # the fix: one short instruction naming the exact control to use
    fix: str = FIX_MANUAL
    nodes: tuple[str, ...] = ()
    default: str = ""     # prefill for FIX_INPUT


@dataclass(frozen=True)
class SkinFacts:
    """One skinCluster bound to the export skeleton."""

    name: str
    mesh: str
    vertices: int = 0
    method: int = SKIN_METHOD
    max_influences: int = MAX_INFLUENCES
    maintain_max: bool = True
    normalize: int = NORMALIZE_INTERACTIVE
    peak: int = 0                 # most influences on any vertex
    over_budget: int = 0          # vertices above MAX_INFLUENCES
    off_sum: int = 0              # vertices whose weights do not sum to 1
    bind_error: float = 0.0       # see BIND_TOLERANCE
    readable: bool = True         # False: not one mesh, so its weights were not read


@dataclass(frozen=True)
class RigFacts:
    """Everything the checks need to know about the open scene."""

    group: str = ""                         # full path of the export group, "" when none
    group_joints: int = 0
    register_default: str = ""              # short name the Register dialog will preselect
    tied_group: str = ""                    # another group the same size as the chosen one
    namespace: str = ""
    referenced: bool = False
    rig_name: str = ""
    renames: tuple[tuple[str, str], ...] = ()   # (full path, new short name)
    taken: tuple[tuple[str, str], ...] = ()     # renames blocked by an existing node
    registered_as: str = ""                 # label of a profile using this export group
    missing_joints: tuple[str, ...] = ()    # GenHuman joints this rig lacks
    extra_joints: tuple[str, ...] = ()      # joints GenHuman does not have
    profile_errors: tuple[str, ...] = ()
    skins: tuple[SkinFacts, ...] = ()
    unweighted_joints: tuple[str, ...] = ()  # garment-set joints with no body weight
    controls_off_default: tuple[str, ...] = ()
    dead_switches: tuple[str, ...] = ()     # "node.attr" offered as a variant, driving nothing
    stray_namespaces: tuple[str, ...] = ()
    orphan_shapes: tuple[str, ...] = ()
    unknown_nodes: tuple[str, ...] = ()
    unknown_plugins: tuple[str, ...] = ()
    requires_arnold: bool = False


def short(path: str) -> str:
    return path.rsplit("|", 1)[-1]


def valid_rig_name(name: str) -> bool:
    """True when ``name`` can prefix a Maya node name."""
    return bool(re.fullmatch(r"[A-Za-z_]\w*", name))


def guess_rig_name(scene_file: str, group: str) -> str:
    """Best guess at the rig's name, for the artist to confirm.

    The file name comes first: ``Eric_rig_v0.6.ma`` knows it is Eric even though every node
    inside it still says GenHuman. Then an existing ``*_Joint_GRP`` prefix, then the top node.
    """
    stem = re.split(r"[\\/]", scene_file)[-1]
    match = re.match(r"([A-Za-z_]\w*?)_rig", stem, re.IGNORECASE)
    if match:
        return match.group(1)
    name = short(group)
    if name.endswith(JOINT_GRP):
        return name[:-len(JOINT_GRP)]
    return next((p for p in group.split("|") if p), "")


def landmark_renames(group: str, body: str, rig_name: str) -> list[tuple[str, str]]:
    """``[(full path, new short name)]`` for the landmarks not yet on the convention.

    Registration stores the top node as a marker, so a top node carrying the old rig's name
    (``GenHuman`` above ``GenHuman_Joint_GRP``) moves with the group: left alone, a rig built
    from GenHuman still reads as GenHuman. Any other top node is a usable marker as it is.
    """
    want = [(group, rig_name + JOINT_GRP)]
    top = "|" + next((p for p in group.split("|") if p), "")
    if short(group) == short(top) + JOINT_GRP:
        want.append((top, rig_name))
    if body:
        mesh_grp = body.rsplit("|", 1)[0]
        if mesh_grp and mesh_grp != top:
            want.append((mesh_grp, rig_name + MESH_GRP))
        want.append((body, rig_name + BODY_MESH))
    return [(path, new) for path, new in want if short(path) != new]


def budget_row(row: list[tuple[float, int]], budget: int = MAX_INFLUENCES,
               ) -> tuple[list[tuple[float, int]], list[int]]:
    """Fit one vertex's ``[(weight, influence)]`` to ``budget``: ``(kept, dropped indices)``.

    Keeps the heaviest and renormalizes them, which is the method measured on Eric: no change
    at bind, 0.64 cm at worst in an aggressive pose. A row of all zeros is returned untouched.
    """
    ordered = sorted((pair for pair in row if pair[0] > 0), reverse=True)
    keep = ordered[:budget]
    total = sum(weight for weight, _ in keep)
    if not total:
        return [], []
    return [(weight / total, i) for weight, i in keep], [i for _, i in ordered[budget:]]


def requires_arnold(lines) -> bool:
    """True when the header of a ``.ma`` (an iterable of lines) declares mtoa.

    Maya wraps a long ``requires`` across lines, with the plugin name on the last one, so
    this reads the whole header rather than matching ``requires`` lines.
    """
    for line in lines:
        if line.startswith("createNode"):
            return False  # the header is over
        if '"mtoa"' in line:
            return True
    return False


def count(number: int, noun: str) -> str:
    return f"{number} {noun}" + ("" if number == 1 else "s")


def _sample(names, limit: int = 6) -> str:
    uniq = sorted(set(names))
    head = ", ".join(uniq[:limit])
    return head if len(uniq) <= limit else f"{head} (+{len(uniq) - limit} more)"


def _body_skin(facts: RigFacts) -> SkinFacts | None:
    return max(facts.skins, key=lambda s: s.vertices, default=None)


def _structure_issues(facts: RigFacts) -> list[Issue]:
    issues: list[Issue] = []
    group = short(facts.group)
    if facts.tied_group:
        issues.append(Issue(
            "tied_group", ERROR, "Structure",
            "Two groups could be the export skeleton",
            f"{group} and {short(facts.tied_group)} both hold {facts.group_joints} joints.",
            "In Export group above, choose the one the body is skinned to."))
    elif facts.register_default and facts.register_default != group:
        issues.append(Issue(
            "register_default", WARN, "Structure",
            "Register rig will preselect the wrong group",
            f"Register rig defaults to {facts.register_default}, the biggest group. The body "
            f"is skinned to {group}.",
            f"In Register rig, set Export skeleton to {group}.",
            nodes=(facts.group,)))
    if facts.profile_errors:
        issues.append(Issue(
            "profile", ERROR, "Structure",
            "Outfitter can't build a profile from this rig",
            "Capturing the rig failed:\n" + "\n".join(facts.profile_errors),
            "Correct each error listed, then press Scan scene.",
            nodes=(facts.group,)))
    if facts.missing_joints or facts.extra_joints:
        issues.append(Issue(
            "joint_names", WARN, "Structure",
            "Export joints differ from GenHuman",
            "These joints don't match GenHuman's names, so skin sets and retargeting skip "
            f"them.\nMissing: {_sample(facts.missing_joints) or 'none'}\n"
            f"Extra: {_sample(facts.extra_joints) or 'none'}",
            "Ask the rigger to rename them, unless the difference is intended."))
    return issues


def _name_issues(facts: RigFacts) -> list[Issue]:
    plan = "\n".join(f"{short(path)} -> {new}" for path, new in facts.renames)
    issues: list[Issue] = []
    if facts.taken:
        issues.append(Issue(
            "names_taken", ERROR, "Names",
            "A landmark's name is already in use",
            "Other nodes already have the names these landmarks need:\n"
            + "\n".join(f"{short(path)} needs {new}" for path, new in facts.taken),
            "Rename the other nodes, then press Scan scene.",
            nodes=tuple(new for _, new in facts.taken)))
    if facts.renames:
        registered = facts.registered_as
        issues.append(Issue(
            "rename", ERROR, "Names",
            "Landmark names are off convention",
            (f"These nodes use the names of registered rig {registered}.\n{plan}" if registered
             else f"Outfitter can't reliably find this rig by these names.\n{plan}"),
            ("New character: confirm its name, press Rename. Same rig: don't, it breaks "
             "its profile." if registered
             else "Confirm the rig name below, then press Rename. Do this before registering."),
            FIX_INPUT, tuple(path for path, _ in facts.renames), facts.rig_name))
    elif facts.registered_as:
        issues.append(Issue(
            "rename", INFO, "Names",
            f"Already registered as {facts.registered_as}",
            f"This rig uses the same names as registered rig {facts.registered_as}.",
            "Same rig: do nothing. Different character: enter its name, press Rename.",
            FIX_INPUT, (facts.group,)))
    return issues


def _skin_issues(facts: RigFacts) -> list[Issue]:
    issues: list[Issue] = []
    body = _body_skin(facts)
    for skin in facts.skins:
        if not skin.readable:
            issues.append(Issue(
                f"skin_unread:{skin.name}", INFO, "Skin",
                f"{skin.name} was not checked",
                "It deforms more than one mesh, so its weights were not read.",
                f"Check {skin.name} by hand: at most {MAX_INFLUENCES} influences per vertex.",
                nodes=(skin.name,)))
            continue
        if skin.bind_error > BIND_TOLERANCE:
            if skin is body:
                issues.append(Issue(
                    f"bind:{skin.name}", ERROR, "Skin", "The body is off its bind pose",
                    "The joints are not where the body was bound, and registering captures "
                    "them as they are now.",
                    "Reopen the file without saving. If it opens posed, return it to the rigger.",
                    nodes=(skin.mesh,)))
            else:
                issues.append(Issue(
                    f"bind:{skin.name}", WARN, "Skin", f"{skin.name} is off its bind pose",
                    f"{skin.name} was bound in a different pose from the body.",
                    "Press Select in scene. Delete the mesh if nothing uses it, else tell the "
                    "rigger.", nodes=(skin.mesh,)))
        settings = []
        if skin.method != SKIN_METHOD:
            settings.append(f"skinningMethod {skin.method} -> {SKIN_METHOD} (classic linear)")
        if skin.max_influences != MAX_INFLUENCES:
            settings.append(f"maxInfluences {skin.max_influences} -> {MAX_INFLUENCES}")
        if not skin.maintain_max:
            settings.append("maintainMaxInfluences on")
        if skin.normalize != NORMALIZE_INTERACTIVE:
            settings.append(f"normalizeWeights {skin.normalize} -> {NORMALIZE_INTERACTIVE}")
        if settings:
            changes_method = skin.method != SKIN_METHOD
            issues.append(Issue(
                f"skin_settings:{skin.name}", WARN, "Skin",
                f"{skin.name} settings are off spec",
                f"{skin.name} doesn't match the skin spec:\n" + "\n".join(settings),
                "Press Apply fix, then pose the rig: the method change can move the mesh."
                if changes_method else "Press Fix. The mesh does not move.",
                FIX_REVIEW if changes_method else FIX_SAFE, (skin.name,)))
        if skin.over_budget or skin.off_sum:
            parts = []
            if skin.over_budget:
                parts.append(f"{skin.over_budget} of {skin.vertices} vertices exceed "
                             f"{MAX_INFLUENCES} influences (peak {skin.peak})")
            if skin.off_sum:
                parts.append(f"{skin.off_sum} vertices don't sum to 1")
            issues.append(Issue(
                f"skin_weights:{skin.name}", WARN, "Skin",
                f"{skin.name} weights are off spec",
                f"{skin.name}: {'; '.join(parts)}.",
                f"Press Apply fix to keep the {MAX_INFLUENCES} heaviest, then check a pose. "
                "Skip if the rigger wants this.",
                FIX_REVIEW, (skin.name,)))
    if facts.unweighted_joints:
        issues.append(Issue(
            "unweighted", INFO, "Skin",
            "Garment joints carry no body weight",
            f"{_sample(facts.unweighted_joints)} have no weight, usually because it sits on "
            "the twist joints.",
            "No action needed on GenHuman-based rigs. Don't repaint them.",
            nodes=facts.unweighted_joints))
    return issues


def _pose_issues(facts: RigFacts) -> list[Issue]:
    issues: list[Issue] = []
    if facts.controls_off_default:
        issues.append(Issue(
            "controls", INFO, "Rig",
            "Controls hold values at rest",
            f"{count(len(facts.controls_off_default), 'control')} not at zero: "
            f"{_sample(facts.controls_off_default)}.",
            "Don't zero them: they may be holding the rest pose.",
            nodes=facts.controls_off_default))
    if facts.dead_switches:
        issues.append(Issue(
            "dead_switch", WARN, "Rig",
            "A body variant switch drives nothing",
            f"{_sample(facts.dead_switches)} looks like a variant switch but connects to "
            "nothing.",
            "In Register rig, set Body variants to '- single body (no variants) -'."))
    return issues


def _scene_issues(facts: RigFacts) -> list[Issue]:
    issues: list[Issue] = []
    if facts.stray_namespaces:
        versioned = [ns for ns in facts.stray_namespaces if re.search(r"v\d+", ns)]
        issues.append(Issue(
            "namespaces", WARN if versioned else INFO, "Scene",
            "Leftover namespaces in the rig file",
            (f"{_sample(versioned)} holds a version token that can be misread as the rig's "
             "version." if versioned else
             f"{_sample(facts.stray_namespaces)} left in the file. They are harmless."),
            "Remove unused ones in Windows > General Editors > Namespace Editor."
            if versioned else "No action needed."))
    if facts.requires_arnold:
        issues.append(Issue(
            "arnold", WARN, "Scene",
            "The rig file requires Arnold",
            "The saved file declares mtoa, which leaks Arnold nodes into garment scenes.",
            "Can't be fixed in Maya. Have the .ma cleaned as text (see tools/eric/make_v08.py)."))
    if facts.orphan_shapes:
        issues.append(Issue(
            "orphans", WARN, "Scene",
            "Unconnected mesh copies",
            f"{count(len(facts.orphan_shapes), 'intermediate shape')} feeding nothing: "
            f"{_sample(short(n) for n in facts.orphan_shapes)}.",
            "Press Fix to delete them. The rig doesn't change.",
            FIX_SAFE, facts.orphan_shapes))
    if facts.unknown_nodes or facts.unknown_plugins:
        found = [f"{count(len(facts.unknown_nodes), 'node')}: {_sample(facts.unknown_nodes)}"
                 ] if facts.unknown_nodes else []
        if facts.unknown_plugins:
            found.append(f"plugins: {_sample(facts.unknown_plugins)}")
        issues.append(Issue(
            "unknown", INFO, "Scene",
            "Nodes or plugins Maya doesn't recognise",
            f"Maya has no plugin loaded for these. {'; '.join(found)}.",
            "Press Apply fix to remove them, unless the rig needs that plugin: then load it.",
            FIX_REVIEW, facts.unknown_nodes))
    return issues


def assemble_issues(facts: RigFacts) -> list[Issue]:
    """Turn gathered :class:`RigFacts` into issues, most serious first."""
    if not facts.group:
        return [Issue(
            "no_rig", ERROR, "Structure", "No rig found in this scene",
            "No group in this scene has a joint directly under it.",
            "Open the rig file, then press Scan scene.")]
    if facts.namespace or facts.referenced:
        how = f"in namespace '{facts.namespace}'" if facts.namespace else "referenced"
        return [Issue(
            "not_the_rig_file", ERROR, "Structure", f"The rig is {how}",
            "Changes made here wouldn't be saved into the rig file.",
            "Open the rig .ma with File > Open Scene, then press Scan scene.",
            nodes=(facts.group,))]
    issues = (_structure_issues(facts) + _name_issues(facts) + _skin_issues(facts)
              + _pose_issues(facts) + _scene_issues(facts))
    return sorted(issues, key=lambda issue: _LEVEL_ORDER[issue.level])


def verdict(issues: list[Issue]) -> tuple[str, str]:
    """``(level, headline)`` for the banner above the issue list."""
    errors = sum(issue.level == ERROR for issue in issues)
    warnings = sum(issue.level == WARN for issue in issues)
    if errors:
        return ERROR, f"Not ready to register: {errors} must be fixed, {warnings} to review."
    if warnings:
        return WARN, f"Can be registered, with {warnings} to review first."
    return "ok", "Ready to register."
