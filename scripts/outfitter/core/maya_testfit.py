"""In-scene skinning test — drive the ``cloth_*`` skeleton from the body (Maya-side).

The rigger hits **Load test body**: the tool references in its bundled GenHuman, flips
``GH_Body_morph`` to match the garment's chosen gender (male = base, female = morph),
aligns the garment's ``Rig_GRP`` to the rig's export frame, and ``connectAttr``s each
body joint's ``{translate,rotate,scale}`` onto the matching ``cloth_*`` joint — exactly
production attach, in-scene. They pose the body's controls, confirm the mesh follows,
then hit **Remove test body** to disconnect and delete the rig so the joints go static
and the asset is publish-safe again. (``connect_test_body`` / ``disconnect_test_body``
are the connect/disconnect halves, also usable on a body the rigger placed themselves.)

Lazy ``maya.cmds``; runs only inside Maya. The pure plan (matching + skip rules)
lives in :mod:`core.testfit` and is headless-tested; this module gathers the live
facts, applies the plan, and is ``py_compile``d like the rest of the Maya boundary.
"""
from __future__ import annotations

from dataclasses import dataclass

from .. import config
from . import maya_skeleton as _mskel
from . import testfit as _testfit


def _cmds():
    import maya.cmds as cmds  # type: ignore

    return cmds


@dataclass
class ConnectResult:
    connected: int
    matched: int
    unmatched: list[str]
    skipped_locked: int
    skipped_driven: int

    def summary(self) -> str:
        msg = (
            f"Test body connected: driving {self.matched} cloth_* joint(s) from the "
            f"GenHuman body ({self.connected} channel connection(s)).")
        skips = []
        if self.skipped_driven:
            skips.append(f"{self.skipped_driven} already-driven")
        if self.skipped_locked:
            skips.append(f"{self.skipped_locked} locked")
        if skips:
            msg += f" Skipped {', '.join(skips)} channel(s)."
        return msg + " Pose the body's controls and confirm the garment deforms."


@dataclass
class DisconnectResult:
    broken: int
    joints: list[str]

    def summary(self) -> str:
        n = len(self.joints)
        return (
            f"Test body disconnected: broke {self.broken} connection(s) on {n} "
            f"cloth_* joint{'' if n == 1 else 's'}. The joints are static again and "
            "the asset is publish-safe.")


@dataclass
class LoadBodyResult:
    gender: str
    morph: float
    connect: ConnectResult

    def summary(self) -> str:
        return (
            f"Loaded the {self.gender} GenHuman body (GH_Body_morph = {self.morph:g}). "
            + self.connect.summary())


@dataclass
class RemoveBodyResult:
    deleted: int
    disconnect: DisconnectResult

    def summary(self) -> str:
        return (
            self.disconnect.summary()
            + f" Removed the GenHuman test body ({self.deleted} node group(s) deleted).")


def _scene_cloth_nodes(cmds) -> dict[str, str]:
    """``{short cloth name: full DAG path}`` for every ``cloth_*`` joint in the scene."""
    return {
        _mskel._short(j): j
        for j in (cmds.ls(f"{config.CLOTH_PREFIX}*", type="joint", long=True) or [])
    }


def _body_joints(cmds, export_grp: str) -> dict[str, str]:
    """``{short body name: full DAG path}`` for every joint under the export group."""
    joints = cmds.listRelatives(
        export_grp, allDescendents=True, type="joint", fullPath=True) or []
    return {_mskel._short(j): j for j in joints}


def _align_rig_group(cmds, export_grp: str) -> None:
    """Match the garment's ``Rig_GRP`` world frame to the export group's.

    Attach connects only LOCAL transforms, so the garment's joint group must share the
    export group's world frame or the connected joints reproduce in the wrong frame and
    the garment lands rotated off the body (see ``attach._align_root_group``). Best-effort
    — if either group is missing the connections still drive, just possibly off-frame.
    """
    # Rig_GRP is a transform group, not a joint, so match by name across any namespace.
    matches = cmds.ls(config.RIG_GROUP, long=True) or cmds.ls(
        f"*:{config.RIG_GROUP}", long=True) or []
    rig_group = matches[0] if matches else None
    if not rig_group:
        return
    try:
        m = cmds.xform(export_grp, query=True, worldSpace=True, matrix=True)
        cmds.xform(rig_group, worldSpace=True, matrix=m)
    except Exception:  # noqa: BLE001 — alignment is best-effort, never abort the connect
        pass


def connect_test_body(mesh_group: str = "Mesh_GRP") -> ConnectResult:
    """Drive the in-scene ``cloth_*`` skeleton from the GenHuman body for a skinning test.

    Locates the export skeleton (``EXPORT_SKELETON_GROUP``) already in the scene, aligns
    the garment's ``Rig_GRP`` to its frame, then connects each body joint's TRS onto the
    matching ``cloth_<base>`` joint. Already-driven or locked plugs are skipped so the
    call is idempotent and never steals an existing connection. Raises clearly if there's
    no cloth skeleton (build it first) or no GenHuman body (nothing to drive from).
    """
    cmds = _cmds()

    cloth_nodes = _scene_cloth_nodes(cmds)
    if not cloth_nodes:
        raise RuntimeError(
            "No cloth_* joints in the scene. Run 'Create cloth skeleton' first.")

    # _find_export_root raises a clear "GenHuman rig not found" if the body is absent.
    _root_joint, export_grp = _mskel._find_export_root(cmds)
    body_joints = _body_joints(cmds, export_grp)
    if not body_joints:
        raise RuntimeError(
            f"Export group '{_mskel._short(export_grp)}' has no joints to drive from.")

    _align_rig_group(cmds, export_grp)

    # Probe each candidate cloth plug's live state for the pure planner.
    locked: set[str] = set()
    driven: set[str] = set()
    for node in cloth_nodes.values():
        for attr in config.CONNECT_ATTRS:
            plug = f"{node}.{attr}"
            try:
                if cmds.getAttr(plug, lock=True):
                    locked.add(plug)
                elif cmds.connectionInfo(plug, isDestination=True):
                    driven.add(plug)
            except Exception:  # noqa: BLE001 — a missing attr just isn't connected
                pass

    plan = _testfit.plan_test_fit(
        cloth_nodes, body_joints, locked=locked, driven=driven)

    connected = 0
    for conn in plan.connections:
        try:
            cmds.connectAttr(conn.src, conn.dst, force=False)
            connected += 1
        except Exception:  # noqa: BLE001 — skip a plug Maya refuses, keep going
            pass

    cmds.select(clear=True)
    return ConnectResult(
        connected=connected,
        matched=len(plan.matched_joints),
        unmatched=list(plan.unmatched_joints),
        skipped_locked=sum(1 for s in plan.skipped if s.reason == "locked"),
        skipped_driven=sum(1 for s in plan.skipped if s.reason == "driven"),
    )


def disconnect_test_body() -> DisconnectResult:
    """Break the test-body connections so the ``cloth_*`` joints go static again.

    Walks every ``cloth_*`` joint and disconnects any incoming ``{translate,rotate,
    scale}`` connection whose source is *outside* the cloth skeleton (i.e. a body
    joint) — exactly the edges :func:`connect_test_body` makes. Idempotent and tolerant
    of already-broken edges, so it's safe to run before publishing even if nothing is
    connected.
    """
    cmds = _cmds()
    broken = 0
    touched: list[str] = []
    for short, node in _scene_cloth_nodes(cmds).items():
        joint_touched = False
        for attr in config.CONNECT_ATTRS:
            dst = f"{node}.{attr}"
            try:
                src = cmds.connectionInfo(dst, sourceFromDestination=True)
            except Exception:  # noqa: BLE001
                src = ""
            if not src:
                continue
            # only break body-driven edges; never touch a cloth-internal connection
            if _mskel._short(src).startswith(config.CLOTH_PREFIX):
                continue
            try:
                cmds.disconnectAttr(src, dst)
                broken += 1
                joint_touched = True
            except Exception:  # noqa: BLE001 — best-effort; a stubborn edge isn't fatal
                pass
        if joint_touched:
            touched.append(short)
    cmds.select(clear=True)
    return DisconnectResult(broken=broken, joints=touched)


def _genhuman_present(cmds) -> bool:
    """True if a GenHuman rig (any marker node) is already in the scene."""
    for marker in config.RIG_MARKERS:
        if cmds.objExists(marker) or cmds.ls(f"*:{marker}"):
            return True
    return False


def _set_body_morph(cmds, gender: str) -> float:
    """Drive ``GH_Body_morph`` to the value for ``gender``; tolerate an absent attr."""
    value = _testfit.body_morph_value(gender)
    # Resolve the godnode whether imported at root or under a namespace.
    node = config.BODY_MORPH_NODE
    if not cmds.objExists(node):
        matches = cmds.ls(f"*:{config.BODY_MORPH_NODE}") or []
        node = matches[0] if matches else node
    plug = f"{node}.{config.BODY_MORPH_ATTR}"
    try:
        cmds.setAttr(plug, value)
    except Exception:  # noqa: BLE001 — surface as a warning at the UI, don't abort load
        pass
    return value


def load_test_body(gender: str, mesh_group: str = "Mesh_GRP") -> LoadBodyResult:
    """Reference in the bundled GenHuman, flip it to ``gender``, and connect it for a test.

    The tool ships one GenHuman and sets ``GH_Body_morph`` to match the chosen gender
    (male = base, female = full morph), so the rigger skins/poses the garment against the
    correct body without hand-importing one. Refuses if a GenHuman is already in the scene
    (avoid a double body), if there's no cloth skeleton to drive, or if the bundled rig
    file isn't installed. After loading it sets the morph then runs :func:`connect_test_body`.

    The body is brought in as a *file reference* (not an import) so that 'Remove test body'
    can drop it with ``removeReference`` — which deletes every node it brought in, including
    leftover selection sets, plus its namespace, leaving zero remnants for publish. (An
    import has to be torn down by name-sweeping, which strands sets and blocks publish.)
    Downstream matching is namespace-insensitive (see ``maya_skeleton._short`` /
    ``_find_export_root``), so the rig living under its own namespace is transparent.
    """
    cmds = _cmds()

    if not _scene_cloth_nodes(cmds):
        raise RuntimeError(
            "No cloth_* joints in the scene. Run 'Create cloth skeleton' first.")
    if _genhuman_present(cmds):
        raise RuntimeError(
            "A GenHuman rig is already in the scene. Use 'Remove test body' (or delete it) "
            "before loading a fresh gendered body.")

    body_file = config.bundled_genhuman_path()
    if not body_file.is_file():
        raise RuntimeError(
            f"Bundled GenHuman body not found at {body_file}. It ships in the tool's "
            "lib/ folder; reinstall or place the rig file there.")

    # Reference (don't import) under the file-stem namespace, e.g. 'GenHuman_rig_v03' — this
    # carries the version token so detect_rig_version still reads it, and removeReference
    # later wipes the rig cleanly. _short strips the namespace, so the cloth_<base> -> body
    # <base> match and the godnode/morph attr path still resolve as connect expects.
    cmds.file(str(body_file), reference=True, namespace=config.BUNDLED_GENHUMAN_NAMESPACE)
    morph = _set_body_morph(cmds, gender)
    connect = connect_test_body(mesh_group)
    return LoadBodyResult(gender=gender.strip().lower(), morph=morph, connect=connect)


def _remove_genhuman_references(cmds) -> int:
    """Drop any GenHuman file reference; returns how many references were removed.

    ``removeReference`` deletes every node the reference brought in — joints, shaders,
    utility nodes *and selection sets* — and removes its now-empty namespace, so nothing
    is stranded to trip the publish "rig still in scene" gate. Reference nodes are matched
    by their referenced filename so this survives a save/reopen (we don't rely on a handle
    captured at load time). Best-effort per reference; a stubborn one never blocks the rest.
    """
    stem = config.BUNDLED_GENHUMAN_FILE.rsplit(".", 1)[0]
    removed = 0
    for ref in (cmds.ls(type="reference") or []):
        try:
            filename = cmds.referenceQuery(ref, filename=True)
        except Exception:  # noqa: BLE001 — e.g. an unloaded/own-scene reference node
            continue
        if "GenHuman" not in filename and stem not in filename:
            continue
        try:
            cmds.file(removeReference=True, referenceNode=ref)
            removed += 1
        except Exception:  # noqa: BLE001 — keep going; the name-sweep fallback covers leftovers
            pass
    return removed


def _delete_genhuman(cmds) -> int:
    """Robustly delete the imported GenHuman rig; returns how many top nodes were removed.

    The rig is ~thousands of DG 'guts' nodes plus DAG roots. Delete the DAG roots first
    (cascades to children), then sweep any leftover GenHuman-named DG nodes, tolerating
    failures throughout (a stubborn node must never block the rest). Finally drop any now
    -empty namespaces the import created.
    """
    deleted = 0
    # DAG roots whose short name marks the rig (the export group, godnode, GenHuman_*).
    roots: list[str] = []
    for marker in config.RIG_MARKERS:
        roots += cmds.ls(marker, long=True) or []
        roots += cmds.ls(f"*{marker}*", long=True, type="transform") or []
    for node in sorted(set(roots), key=len, reverse=True):
        if not cmds.objExists(node):
            continue
        try:
            cmds.delete(node)
            deleted += 1
        except Exception:  # noqa: BLE001 — keep deleting the rest
            pass
    # Sweep stray GenHuman-named DG nodes left behind (materials/utility/etc.).
    for node in cmds.ls("*GenHuman*", "*GH_*", "god_m_*") or []:
        if cmds.objExists(node):
            try:
                cmds.delete(node)
            except Exception:  # noqa: BLE001
                pass
    return deleted


def remove_test_body() -> RemoveBodyResult:
    """Disconnect the test body and remove the GenHuman so publish isn't blocked.

    Pairs with :func:`load_test_body`: first breaks the body->cloth connections
    (:func:`disconnect_test_body`), then removes the GenHuman rig. The body is removed by
    dropping its file reference (:func:`_remove_genhuman_references`), which wipes every
    node it brought in — including selection sets — leaving no remnants. A legacy scene
    where the rig was *imported* (no reference) falls back to the name-sweep delete. The
    count returned is references removed plus any swept import nodes. Idempotent — safe to
    run with nothing loaded (it just reports zero).
    """
    cmds = _cmds()
    disc = disconnect_test_body()
    deleted = _remove_genhuman_references(cmds)
    deleted += _delete_genhuman(cmds)  # fallback: sweep any imported (non-referenced) rig
    cmds.select(clear=True)
    return RemoveBodyResult(deleted=deleted, disconnect=disc)
