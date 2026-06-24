"""Create/refresh the Maya shelf button that launches the browser (M4).

Maya-only (imports ``maya.cmds``/``maya.mel`` at call time) — exercised by the
in-Maya smoke check, not the headless suite, which only ``py_compile``s it. Kept
free of any package import so it can run before ``outfitter`` is on the
path; the button's command imports the package lazily when clicked.
"""
from __future__ import annotations

SHELF_NAME = "Outfitter"  # fallback only — the button normally lands on the active shelf
BUTTON_LABEL = "Outfitter"
BUTTON_ANNOTATION = "Outfitter — browse / attach / detach garments"

# Run when the shelf button is pressed. First purge every cached ``outfitter``
# module so edits on disk (e.g. a live repo checkout on sys.path) take effect without
# restarting Maya, then (re)import and launch — ``show()`` rebuilds the window and
# re-scans the library, so one click = reload code + refresh assets. Imports lazily so
# the shelf survives even if the package is moved, and reports clearly on failure.
BUTTON_COMMAND = (
    "import sys\n"
    "for _name in [n for n in list(sys.modules) "
    "if n == 'outfitter' or n.startswith('outfitter.')]:\n"
    "    del sys.modules[_name]\n"
    "try:\n"
    "    import outfitter.launch\n"
    "    outfitter.launch.run()\n"
    "except Exception as exc:\n"
    "    import maya.cmds as cmds\n"
    "    cmds.warning('Outfitter failed to launch: %s' % exc)\n"
)


def _shelf_layout(mel) -> str:
    """Return the top-level shelf layout name (the tabbed shelf container)."""
    return mel.eval("$tmpShelfTopLevel = $gShelfTopLevel")


def active_shelf(cmds, mel) -> str:
    """Return the shelf tab the user currently has open — the button lands here.

    Honours whichever shelf is in front (modeling, animation, a custom shelf, …)
    rather than forcing a dedicated tab. Falls back to the first shelf, and only as a
    last resort creates ``SHELF_NAME`` (e.g. a session with no shelves at all).
    """
    parent = _shelf_layout(mel)
    current = cmds.tabLayout(parent, query=True, selectTab=True)
    if current:
        return current
    shelves = cmds.tabLayout(parent, query=True, childArray=True) or []
    if shelves:
        return shelves[0]
    mel.eval(f'addNewShelfTab "{SHELF_NAME}";')
    return SHELF_NAME


# Labels a previous install may have used — matched so re-dropping refreshes the same
# button (and migrates the old name) instead of leaving a stale duplicate behind.
# "Clothing" is the pre-rename (snap_on_clothing-era) label; keep until users have
# re-dropped at least once.
_KNOWN_LABELS = (BUTTON_LABEL, "Clothing")


def _matching_buttons(cmds, mel) -> list[str]:
    """Every launcher button on every shelf (matched by known label)."""
    parent = _shelf_layout(mel)
    found: list[str] = []
    for shelf in cmds.tabLayout(parent, query=True, childArray=True) or []:
        for child in cmds.shelfLayout(shelf, query=True, childArray=True) or []:
            if cmds.objectTypeUI(child) == "shelfButton" and \
                    cmds.shelfButton(child, query=True, label=True) in _KNOWN_LABELS:
                found.append(child)
    return found


def _remove_empty_default_shelf(cmds, mel) -> None:
    """Delete the dedicated ``SHELF_NAME`` tab if a prior install left it empty.

    Only touches our own auto-created tab, and only when it holds no buttons — never a
    shelf the user has populated. Best-effort: ``deleteShelfTab`` also updates prefs.
    """
    parent = _shelf_layout(mel)
    if SHELF_NAME not in (cmds.tabLayout(parent, query=True, childArray=True) or []):
        return
    if cmds.shelfLayout(SHELF_NAME, query=True, childArray=True):
        return  # not empty — leave it alone
    try:
        mel.eval(f'deleteShelfTab "{SHELF_NAME}";')
    except Exception:  # noqa: BLE001 — cleanup is best-effort
        pass


def install_button(icon: str | None = None) -> str:
    """(Re)create the launcher button on the shelf the user currently has open.

    Deletes any prior button (any shelf, current or old label) first, so a re-install
    moves the button to the active shelf instead of leaving it on a previous one; then
    cleans up the empty ``SHELF_NAME`` tab an older installer may have created. ``icon``
    is the absolute path to the shelf image (the installed ``outfitter.png``); if it's
    missing the button falls back to Maya's generic Python icon with a text overlay.
    """
    import os

    import maya.cmds as cmds
    import maya.mel as mel

    if icon and os.path.isfile(icon):
        image, overlay = icon, ""
    else:
        image, overlay = "pythonFamily.png", "Outfit"

    # Resolve the active shelf BEFORE deleting anything, then clear old buttons so the
    # new one lands where the user is looking (not refreshed in place on an old shelf).
    shelf = active_shelf(cmds, mel)
    for old in _matching_buttons(cmds, mel):
        try:
            cmds.deleteUI(old)
        except Exception:  # noqa: BLE001
            pass

    button = cmds.shelfButton(
        parent=shelf, label=BUTTON_LABEL, annotation=BUTTON_ANNOTATION,
        image=image, imageOverlayLabel=overlay, command=BUTTON_COMMAND,
        sourceType="python",
    )
    _remove_empty_default_shelf(cmds, mel)
    return button
