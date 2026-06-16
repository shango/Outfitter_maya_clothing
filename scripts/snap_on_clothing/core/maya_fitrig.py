"""Maya-side fit-rig scaffolder — auto-build the fit lattice + ``cloth_fit_ctrl`` + SDKs.

Authoring-time helper. The rigger does the creative part (model the garment, skin it
to the ``cloth_*`` joints), then runs this once to get a correctly-wired fit rig: a
*frontOfChain* lattice over the garment plus the Set-Driven-Key curves that turn
``cloth_fit_ctrl.fit_*`` attributes into deformation. They then only have to tune the
keyed extremes for their garment — no need to understand frontOfChain ordering or SDK
driver curves.

Transform-level attrs (tightness / height / tilt / length) are auto-keyed from the
per-type recipe in :mod:`core.fit_templates`. Region attrs (e.g. ``fit_brim_width``)
get the attribute but are left for manual point-level keying — the one piece that
needs the rigger's eye. The build logic mirrors the proven trench-coat rig in
``examples/build_example_asset.py``, generalized to any open, already-skinned garment.

Lazy ``maya.cmds``; runs only inside Maya. The headless suite ``py_compile``s this and
unit-tests the pure templates it consumes, consistent with the rest of the Maya boundary.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from .. import config
from . import fit_templates, maya_publish


def _cmds():
    import maya.cmds as cmds  # type: ignore

    return cmds


@dataclass
class ScaffoldResult:
    """What the scaffolder built, for reporting back to the UI / caller."""

    ctrl: str
    lattice: str
    base: str
    ffd: str
    keyed_attrs: list[str] = field(default_factory=list)
    region_attrs: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def summary(self) -> str:
        keyed = ", ".join(self.keyed_attrs) or "none"
        region = ", ".join(self.region_attrs) or "none"
        msg = (f"Fit rig scaffolded on {self.ctrl}: auto-keyed [{keyed}]")
        if self.region_attrs:
            msg += f"; manual point-key needed for [{region}]"
        return msg + ". Scrub the sliders, tune the extremes, then Publish."


def _any_skinned(cmds, meshes: list[str]) -> bool:
    for m in meshes:
        hist = cmds.listHistory(m, pruneDagObjects=True) or []
        if cmds.ls(hist, type="skinCluster"):
            return True
    return False


def _channel_value(drv: fit_templates.FitDriver, amount: float, neutral: dict) -> float:
    """Resolve a key's ``amount`` to an absolute lattice channel value."""
    axis = drv.axis
    if drv.mode == "scale":
        return neutral[f"scale{axis}"] * amount
    if drv.mode == "offset":
        return neutral[f"translate{axis}"] + amount * neutral[f"scale{axis}"]
    if drv.mode == "rotate":
        return amount
    raise ValueError(f"unknown fit driver mode: {drv.mode!r}")


def author_fit_rig(cmds, ctrl: str, lattice: str, template: "fit_templates.FitTemplate"):
    """Add ``template``'s ``fit_*`` attrs to ``ctrl`` and author the default SDKs onto
    ``lattice``, leaving everything at neutral. Returns ``(keyed_attrs, region_attrs)``.

    The single source of truth for fit wiring: both :func:`scaffold_fit_rig` and
    ``examples/build_example_asset`` call this, so the coat (and every type) stays in
    lockstep with the :mod:`core.fit_templates` recipe. The caller owns node creation
    (the ctrl group + the lattice) and any organizing/parenting afterwards. ``cmds`` is
    passed in so this is testable with a fake.
    """
    for a in template.attrs:
        cmds.addAttr(ctrl, longName=a.name, attributeType="double",
                     minValue=a.min, maxValue=a.max, defaultValue=a.default,
                     keyable=True)

    # objectCentered => the lattice's neutral scale is the garment bbox size (not 1.0);
    # drivers scale/offset relative to this captured neutral, never absolute.
    neutral = {
        f"{kind}{axis}": cmds.getAttr(f"{lattice}.{kind}{axis}")
        for kind in ("scale", "translate") for axis in ("X", "Y", "Z")
    }

    keyed: list[str] = []
    region: list[str] = []
    for a in template.attrs:
        if a.region or not a.drivers:
            region.append(a.name)
            continue
        for drv in a.drivers:
            for driver_val, amount in drv.keys:
                cmds.setAttr(f"{ctrl}.{a.name}", driver_val)
                cmds.setAttr(f"{lattice}.{drv.channel}",
                             _channel_value(drv, amount, neutral))
                cmds.setDrivenKeyframe(f"{lattice}.{drv.channel}",
                                       currentDriver=f"{ctrl}.{a.name}")
        keyed.append(a.name)

    # Reset control to neutral; every keyed channel is driven by an SDK curve, so setting
    # the ctrl attrs to default pulls the lattice back to rest through those curves. Do
    # NOT setAttr the lattice channels directly — they're now connected to animCurve
    # outputs (driven keys) and Maya refuses setAttr on a connected plug.
    for a in template.attrs:
        cmds.setAttr(f"{ctrl}.{a.name}", a.default)

    return keyed, region


def scaffold_fit_rig(
    asset_type: str,
    mesh_group: str = "Mesh_GRP",
    ctrl_group: str = "Ctrl_GRP",
    fit_ctrl_name: str | None = None,
) -> ScaffoldResult:
    """Build a working fit rig on the open, already-skinned garment.

    Creates ``cloth_fit_ctrl`` with the asset type's ``fit_*`` attrs, a frontOfChain
    lattice over the garment meshes, and default SDKs wiring the transform-level attrs
    to the lattice. Leaves everything at neutral and parents the new nodes under
    ``Ctrl_GRP``. Region attrs are created but not keyed (see module docstring).

    Raises if ``cloth_fit_ctrl`` already exists (re-scaffolding would double-wire) or
    no garment mesh is found. An unskinned garment is a warning, not an error — the
    lattice still builds; the rigger is reminded to skin before publishing.
    """
    cmds = _cmds()
    fit_ctrl_name = fit_ctrl_name or config.FIT_CTRL
    warnings: list[str] = []

    if cmds.objExists(fit_ctrl_name):
        raise RuntimeError(
            f"{fit_ctrl_name!r} already exists. Delete it and its 'cloth_fit_ffd' "
            "lattice before scaffolding again.")

    meshes = maya_publish.find_garment_meshes(mesh_group)
    if not meshes:
        raise RuntimeError(
            f"No garment mesh found under {mesh_group!r}. Model the garment first.")

    if not _any_skinned(cmds, meshes):
        warnings.append(
            "Heads up: no skinCluster on the garment yet. The fit lattice is built "
            "frontOfChain to deform the rest shape BEFORE the skin — bind the mesh to "
            "the cloth_* joints before publishing, or the fit won't follow the body.")

    template = fit_templates.fit_template(asset_type)

    # 1) control + frontOfChain lattice (deform the rest shape before the skinCluster)
    ctrl = cmds.group(empty=True, name=fit_ctrl_name)
    ffd, lattice, base = cmds.lattice(
        meshes, divisions=template.divisions, objectCentered=True,
        frontOfChain=True, name="cloth_fit_ffd")

    # 2) add the fit_* attrs + author the default SDKs (shared recipe — see author_fit_rig)
    keyed, region = author_fit_rig(cmds, ctrl, lattice, template)

    # 3) organize under Ctrl_GRP (created empty at origin if missing, like the
    #    asset structure — identity parent keeps the keyed local values intact)
    if not cmds.objExists(ctrl_group):
        cmds.group(empty=True, name=ctrl_group)
    cmds.parent([ctrl, lattice, base], ctrl_group)

    return ScaffoldResult(ctrl=ctrl, lattice=lattice, base=base, ffd=ffd,
                          keyed_attrs=keyed, region_attrs=region, warnings=warnings)
