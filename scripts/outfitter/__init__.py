"""Outfitter Rig System — Maya 2026 tool package.

Browse local clothing assets, snap a chosen asset onto the animated GenHuman rig
via direct ``connectAttr`` only, and detach cleanly. See ``prd.md`` and
``Clothing Asset Authoring Spec.md`` at the repo root.

Layout:
    config            library paths, connect-attr set, version table
    core/             pure logic — importable and unit-testable WITHOUT Maya
        ma_parse      lightweight Maya-ASCII (.ma) reader (no maya.cmds)
        asset         asset data model + metadata validation
        library       scan dirs -> ClothingAsset list
    ui/               PySide6 Maya UI (imports Maya/PySide6 lazily)

Design rule: nothing under ``core`` may import ``maya`` or ``PySide6`` at module
scope, so the validation core runs headlessly in CI. Maya-dependent code lives in
``ui`` and (later) ``core.attach`` behind guarded imports.
"""

__version__ = "0.1.0-beta-4"
