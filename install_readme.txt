Outfitter — Install
===================

Requires Maya 2026 (ships with PySide6).

Install
-------
1. Open the shelf you want the button on (e.g. your modeling shelf).
2. Drag-and-drop "install.py" from this folder into a Maya 2026 viewport.
3. The installer copies the tool into your Maya scripts dir, merges the
   starter assets into your library (existing assets are never overwritten),
   and adds an "Outfitter" button to the shelf you currently have open.
4. Click OK on the confirmation dialog.

Launch
------
Click the "Outfitter" shelf button.
(Or, in the Script Editor: import outfitter.launch as scl; scl.run())

Upgrade
-------
Drag-and-drop "install.py" again — it upgrades in place.

Notes
-----
- Keep the whole folder together; install.py needs "scripts/" and
  "installer/" beside it.
- The shelf button reloads the tool's code on each click, so re-clicking
  picks up updates without restarting Maya.
