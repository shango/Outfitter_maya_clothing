"""Create/refresh the Maya shelf button that launches the browser (M4).

Maya-only (imports ``maya.cmds``/``maya.mel`` at call time) — exercised by the
in-Maya smoke check, not the headless suite, which only ``py_compile``s it. Kept
free of any package import so it can run before ``snap_on_clothing`` is on the
path; the button's command imports the package lazily when clicked.
"""
from __future__ import annotations

SHELF_NAME = "SnapOnClothing"
BUTTON_LABEL = "Clothing"
BUTTON_ANNOTATION = "Snap-On Clothing — browse / attach / detach garments"

# Run when the shelf button is pressed. First purge every cached ``snap_on_clothing``
# module so edits on disk (e.g. a live repo checkout on sys.path) take effect without
# restarting Maya, then (re)import and launch — ``show()`` rebuilds the window and
# re-scans the library, so one click = reload code + refresh assets. Imports lazily so
# the shelf survives even if the package is moved, and reports clearly on failure.
BUTTON_COMMAND = (
    "import sys\n"
    "for _name in [n for n in list(sys.modules) "
    "if n == 'snap_on_clothing' or n.startswith('snap_on_clothing.')]:\n"
    "    del sys.modules[_name]\n"
    "try:\n"
    "    import snap_on_clothing.launch as scl\n"
    "    scl.run()\n"
    "except Exception as exc:\n"
    "    import maya.cmds as cmds\n"
    "    cmds.warning('Snap-On Clothing failed to launch: %s' % exc)\n"
)


def _shelf_layout(mel) -> str:
    """Return the top-level shelf layout name (the tabbed shelf container)."""
    return mel.eval("$tmpShelfTopLevel = $gShelfTopLevel")


def ensure_shelf(cmds, mel) -> str:
    """Return the ``SHELF_NAME`` shelf tab, creating it if absent."""
    parent = _shelf_layout(mel)
    # The shelf top level is a tabLayout; its children are the per-tab shelfLayouts,
    # whose control names match the tab labels.
    shelves = cmds.tabLayout(parent, query=True, childArray=True) or []
    if SHELF_NAME not in shelves:
        # addNewShelfTab creates the tab and makes it the active shelf.
        mel.eval(f'addNewShelfTab "{SHELF_NAME}";')
    return SHELF_NAME


def _existing_button(cmds, shelf: str) -> str | None:
    """The launcher button on ``shelf`` (matched by label), or ``None``."""
    for child in cmds.shelfLayout(shelf, query=True, childArray=True) or []:
        if cmds.objectTypeUI(child) == "shelfButton" and \
                cmds.shelfButton(child, query=True, label=True) == BUTTON_LABEL:
            return child
    return None


def install_button() -> str:
    """Create or refresh the launcher button; returns the button's control name."""
    import maya.cmds as cmds
    import maya.mel as mel

    shelf = ensure_shelf(cmds, mel)
    existing = _existing_button(cmds, shelf)
    if existing is not None:
        cmds.shelfButton(existing, edit=True, command=BUTTON_COMMAND,
                         annotation=BUTTON_ANNOTATION, sourceType="python")
        return existing
    return cmds.shelfButton(
        parent=shelf, label=BUTTON_LABEL, annotation=BUTTON_ANNOTATION,
        image="pythonFamily.png", imageOverlayLabel="cloth",
        command=BUTTON_COMMAND, sourceType="python",
    )
