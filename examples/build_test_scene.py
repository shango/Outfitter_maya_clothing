"""Build the M5 test scene INSIDE Maya 2026: GenHuman rig + attached clothing.

Loads the GenHuman rig, then drives the *real* tool core (``AttachEngine`` over the
live ``MayaScene``) to attach one or more compliant assets — the same connectAttr-only,
transactional path the browser's Attach button uses. Use it to smoke-test attach /
detach / Genie export against the real rig.

Run from Maya's Script Editor (Python)::

    import sys; sys.path.append(r"/path/to/maya_clothing_rig")
    import examples.build_test_scene as t
    t.build()                                  # rig + trench_coat_A attached as "coat"
    # or attach several:
    # t.build(assets=[("trench_coat_A", "coat")])

Not part of the headless suite (needs Maya + the rig file); CI only ``py_compile``s it.
"""
from __future__ import annotations

import os
import sys

try:
    _HERE = os.path.dirname(os.path.abspath(__file__))
    _REPO = os.path.dirname(_HERE)
except NameError:
    # __file__ is undefined when the script body is pasted into the Script Editor
    # instead of imported. Import it as a module so this resolves (see module docstring).
    raise RuntimeError(
        "Run this by importing it, not by pasting the code into the Script Editor:\n"
        "    import sys; sys.path.append(r'/path/to/maya_clothing_rig')\n"
        "    import examples.build_test_scene as t; t.build()"
    )
_SCRIPTS = os.path.join(_REPO, "scripts")
if _SCRIPTS not in sys.path:
    sys.path.insert(0, _SCRIPTS)

import maya.cmds as cmds  # noqa: E402

from snap_on_clothing.core import library  # noqa: E402
from snap_on_clothing.core.attach import AttachEngine  # noqa: E402
from snap_on_clothing.core.export import audit_export_readiness  # noqa: E402
from snap_on_clothing.core.scene import MayaScene  # noqa: E402

DEFAULT_RIG = "GenHuman_rig_v03.ma"
DEFAULT_ASSETS = [("trench_coat_A", "coat")]


def _rig_path(rig: str) -> str:
    return rig if os.path.isabs(rig) else os.path.join(_REPO, rig)


def _asset_ma(asset_name: str) -> str:
    return os.path.join(_REPO, "assets", asset_name, f"{asset_name}.ma")


def build(rig: str = DEFAULT_RIG, assets=None):
    """Open ``rig`` and attach each ``(asset_name, instance_namespace)`` in ``assets``."""
    assets = DEFAULT_ASSETS if assets is None else assets

    rig_path = _rig_path(rig)
    if not os.path.isfile(rig_path):
        raise FileNotFoundError(f"GenHuman rig not found: {rig_path}")

    cmds.file(new=True, force=True)
    print(f"[build_test_scene] importing rig {rig_path}")
    cmds.file(rig_path, i=True, force=True)

    engine = AttachEngine(MayaScene())
    for asset_name, namespace in assets:
        ma = _asset_ma(asset_name)
        if not os.path.isfile(ma):
            print(f"[build_test_scene] SKIP — missing asset {ma}")
            continue
        asset = library.load_asset(ma)
        result = engine.attach(asset, namespace)
        status = "OK" if result.ok else "FAILED"
        print(f"[build_test_scene] attach {asset_name} as '{namespace}': {status}")
        for issue in result.report.issues:
            print(f"    {issue}")

    audit = audit_export_readiness(MayaScene(), engine.registry)
    print(f"[build_test_scene] export audit: "
          f"{'READY' if audit.ok else 'NOT READY'} ({audit.report.summary_line()})")
    for issue in audit.report.issues:
        print(f"    {issue}")
    return engine


if __name__ == "__main__":
    build()
