"""Dev-only, in-Maya example scripts (NOT shipped to tool users).

  * ``build_example_asset`` — regenerate the fully-skinned example clothing asset.
  * ``build_test_scene``    — load the GenHuman rig and attach compliant assets.

Both require a running Maya 2026; CI only ``py_compile``s them. They are excluded
from the distributable package (see ``scripts/README.md`` packaging notes).
"""
