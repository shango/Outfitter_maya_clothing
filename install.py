"""Drag-and-drop installer for the Outfitter tool (FR-9 / M4).

Drop this file into a Maya 2026 viewport to install. Maya calls
``onMayaDroppedPythonFile`` automatically. It:

  1. copies the ``outfitter`` package into your Maya user script dir,
  2. merges the bundled starter assets into your clothing library
     (never overwriting assets you already have),
  3. adds/refreshes an "Outfitter" shelf button on your active shelf.

Re-dropping a newer build upgrades in place. All real work lives in
``installer/installer_core.py`` (pure, headless-tested) and ``installer/shelf.py``;
this file only wires Maya paths to them and reports the result.

Note: the package is named ``installer/`` (not ``install/``) on purpose — a package
sharing this file's stem would shadow it on ``sys.path`` and Maya would import the
package instead of this module, so ``onMayaDroppedPythonFile`` would not be found.
"""
from __future__ import annotations

import sys
from pathlib import Path


def _report(lines: list[str], *, ok: bool) -> None:
    """Print to the Script Editor and pop a confirmation dialog when in Maya."""
    text = "\n".join(lines)
    print(text)
    try:
        import maya.cmds as cmds

        cmds.confirmDialog(
            title="Outfitter Installer",
            message=text,
            button=["OK"],
            icon="information" if ok else "critical",
        )
    except Exception:  # noqa: BLE001 — dialog is best-effort (e.g. headless)
        pass


def _do_install(drop_dir: Path) -> None:
    # Make both the distribution root (for `installer/`) and its bundled scripts
    # (for `outfitter.config`) importable for the duration of the install.
    for p in (str(drop_dir), str(drop_dir / "scripts")):
        if p not in sys.path:
            sys.path.insert(0, p)

    # A previous drop in this Maya session leaves installer/* and outfitter/*
    # cached in sys.modules; purge them so THIS drop runs the freshly-dropped code.
    # Without this, re-dropping silently reuses the stale shelf/icon/active-shelf logic.
    for _name in [n for n in list(sys.modules)
                  if n.split(".", 1)[0] in ("installer", "outfitter")]:
        del sys.modules[_name]

    from installer import installer_core
    from outfitter import config

    import maya.cmds as cmds

    scripts_dir = Path(cmds.internalVar(userScriptDir=True))
    assets_target = config.user_asset_dir()

    result = installer_core.install(
        source_root=drop_dir,
        scripts_dir=scripts_dir,
        assets_target=assets_target,
    )

    lines = [result.summary(), ""]
    lines += [f"  • {m}" for m in result.messages]
    if result.errors:
        lines += [""] + [f"  ✗ {e}" for e in result.errors]

    # Shelf button (only if the package landed — it imports lazily at click time).
    if result.ok:
        try:
            # ensure the freshly-installed package is importable now
            sd = str(scripts_dir)
            if sd not in sys.path:
                sys.path.insert(0, sd)
            from installer import shelf

            # point the button at the icon that just shipped inside the package
            icon = result.package_dest / "ui" / "icons" / "outfitter.png"
            btn = shelf.install_button(icon=str(icon))
            lines.append(f"  • shelf button -> {btn}")
        except Exception as exc:  # noqa: BLE001 — install still succeeded
            lines.append(f"  ! shelf button skipped: {exc}")

    if result.ok:
        lines += ["", "Done. Click the 'Outfitter' shelf button to launch."]
    _report(lines, ok=result.ok)


def onMayaDroppedPythonFile(*_args) -> None:  # noqa: N802 — Maya-defined name
    """Entry point Maya calls when this file is dropped into a viewport."""
    drop_dir = Path(__file__).resolve().parent
    try:
        _do_install(drop_dir)
    except Exception as exc:  # noqa: BLE001 — never leave Maya in a broken state
        import traceback

        _report(
            ["Outfitter install FAILED before completion:",
             str(exc), "", traceback.format_exc()],
            ok=False,
        )


if __name__ == "__main__":
    # Allow `mayapy install.py` / manual invocation outside the drop flow.
    onMayaDroppedPythonFile()
