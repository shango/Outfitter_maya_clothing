"""In-scene skinning test — drive the ``cloth_*`` skeleton from the body (Maya-side).

The rigger hits **Connect test body**: this finds the GenHuman body already in the
authoring scene, aligns the garment's ``Rig_GRP`` to the rig's export frame, and
``connectAttr``s each body joint's ``{translate,rotate,scale}`` onto the matching
``cloth_*`` joint — exactly production attach, in-scene, no import. They pose the
body's controls, confirm the mesh follows, then hit **Disconnect test body** to
break those edges so the joints go static and the asset is publish-safe again.

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
    rig_group = _mskel._resolve_joint(cmds, config.RIG_GROUP)
    if rig_group is None:
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
