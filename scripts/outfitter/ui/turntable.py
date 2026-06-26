"""Interactive turntable preview — a shaded thumbnail you can spin.

``TurntableView`` is a ``QLabel`` that loads a turntable sprite sheet (the layout from
:mod:`core.turntable`), slices it into frames, and lets the user rotate the garment:
it auto-spins while the cursor is over it and scrubs to an exact angle as the cursor
moves left↔right. With only a single still it behaves like a plain image label.

UI only — verified by ``py_compile`` (PySide6 ships with Maya 2026, not the headless
test env), like the rest of ``outfitter.ui``.
"""
from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from .. import config
from ..core import turntable as _tt


class TurntableView(QtWidgets.QLabel):
    """A spinnable/scrubbable preview backed by a turntable sprite sheet."""

    def __init__(self, parent=None, *, hint: str = "no preview"):
        super().__init__(parent)
        self._hint = hint
        self._frames: list[QtGui.QPixmap] = []
        self._still: QtGui.QPixmap | None = None
        self._index = 0
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setMouseTracking(True)  # scrub without a button held down
        self._spin = QtCore.QTimer(self)
        self._spin.setInterval(60)  # ~16 fps idle spin
        self._spin.timeout.connect(self._advance)
        self.setText(hint)

    # --- content --------------------------------------------------------------
    def clear_content(self) -> None:
        self._frames = []
        self._still = None
        self._index = 0
        self._spin.stop()
        self.setPixmap(QtGui.QPixmap())
        self.setText(self._hint)

    def set_still(self, pixmap: QtGui.QPixmap | None) -> None:
        """Show a single (non-rotatable) image — used when no turntable sheet exists."""
        self._frames = []
        self._still = pixmap if pixmap is not None and not pixmap.isNull() else None
        self._index = 0
        self._spin.stop()
        self._render()

    def set_sheet(self, sheet_path: Path | str, *, cols: int = config.TURNTABLE_COLS,
                  rows: int = config.TURNTABLE_ROWS) -> bool:
        """Load a sprite sheet and slice it into frames. Returns False if unreadable.

        The per-cell size is derived from the loaded sheet (not assumed), so a sheet
        saved or scaled at any resolution still slices into a clean ``cols`` x ``rows``.
        """
        sheet = QtGui.QPixmap(str(sheet_path))
        if sheet.isNull() or cols <= 0 or rows <= 0:
            self.clear_content()
            return False
        cw = sheet.width() // cols
        ch = sheet.height() // rows
        frames: list[QtGui.QPixmap] = []
        for i in range(cols * rows):
            row, col = divmod(i, cols)
            frames.append(sheet.copy(col * cw, row * ch, cw, ch))
        self._frames = frames
        self._still = frames[0] if frames else None
        self._index = 0
        self._render()
        return True

    @property
    def has_turntable(self) -> bool:
        return bool(self._frames)

    # --- interaction ----------------------------------------------------------
    def enterEvent(self, event) -> None:
        if self._frames:
            self._spin.start()
        super().enterEvent(event)

    def leaveEvent(self, event) -> None:
        self._spin.stop()
        super().leaveEvent(event)

    def mouseMoveEvent(self, event) -> None:
        if self._frames:
            self._spin.stop()  # hand control to the cursor while it's moving
            frac = event.position().x() / max(1, self.width())
            self._index = _tt.frame_at(frac, len(self._frames))
            self._render()
        super().mouseMoveEvent(event)

    def _advance(self) -> None:
        if self._frames:
            self._index = (self._index + 1) % len(self._frames)
            self._render()

    # --- paint ----------------------------------------------------------------
    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._render()

    def _render(self) -> None:
        pm = self._frames[self._index] if self._frames else self._still
        if pm is None or pm.isNull():
            self.setText(self._hint)
            self.setPixmap(QtGui.QPixmap())
            return
        target = self.size()
        if target.width() < 2 or target.height() < 2:
            return
        self.setPixmap(pm.scaled(
            target, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))
