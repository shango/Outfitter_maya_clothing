"""Drag-and-drop installer package for the Snap-On Clothing tool (M4).

Kept import-light on purpose: ``installer_core`` is pure filesystem logic (no
Maya) so it is unit-tested headlessly, while ``shelf`` imports ``maya.cmds`` and
is only touched at drop time. Importing this package pulls in neither submodule.
"""
