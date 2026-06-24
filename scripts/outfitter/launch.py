"""Launch entry points for the Outfitter browser.

Inside Maya 2026 (Script Editor or a shelf button)::

    import outfitter.launch
    outfitter.launch.run()

Standalone dev preview (needs only PySide6 on PYTHONPATH; no Maya)::

    python -m outfitter.launch
"""
from __future__ import annotations

import sys
from pathlib import Path


def run(roots: list[Path] | None = None):
    """Show the browser window. Use this from Maya."""
    from .ui import window
    return window.show(roots=roots)


def main() -> int:
    """Standalone preview: spin up a QApplication and show the browser."""
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication.instance() or QtWidgets.QApplication(sys.argv)
    from .ui import window

    win = window.show()
    win.show()
    return app.exec()


if __name__ == "__main__":
    # allow `python scripts/outfitter/launch.py` (direct script run; -m already works)
    if __package__ is None:
        sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    raise SystemExit(main())
