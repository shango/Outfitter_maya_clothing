"""The Rig Check tab: find what stops a rig working in Outfitter, and fix it.

A worklist rather than a console: the left side lists findings, most serious first, and the
right side explains the selected one and offers whatever can be done about it. Everything
that needs a decision happens beside the issue it belongs to, with the affected nodes one
click from being selected in the scene.

The checks live in :mod:`core.rig_check` and the scene work in :mod:`core.maya_rig_check`.
"""
from __future__ import annotations

from PySide6 import QtCore, QtGui, QtWidgets

from ..core import rig_check as _check

_LEVEL_COLORS = {_check.ERROR: "#e06c75", _check.WARN: "#e5c07b",
                 _check.INFO: "#7fb2e5", "ok": "#7ec699"}
_LEVEL_NAMES = {_check.ERROR: "Must fix", _check.WARN: "Review", _check.INFO: "Note"}
_FIX_NAMES = {_check.FIX_SAFE: "safe fix", _check.FIX_REVIEW: "fix after review",
              _check.FIX_INPUT: "needs a name", _check.FIX_MANUAL: "by hand"}
_FIX_BUTTONS = {_check.FIX_SAFE: "Fix", _check.FIX_REVIEW: "Apply fix",
                _check.FIX_INPUT: "Rename"}
_NOT_SAVED = "Nothing is saved: Ctrl+Z undoes it, File > Save As keeps it."
_START = ("Open the rig file itself, then Scan scene. Nothing changes until you press a fix, "
          "and each fix is one Ctrl+Z.")


def _dot(color: str) -> QtGui.QIcon:
    pixmap = QtGui.QPixmap(12, 12)
    pixmap.fill(QtCore.Qt.transparent)
    painter = QtGui.QPainter(pixmap)
    painter.setRenderHint(QtGui.QPainter.Antialiasing)
    painter.setPen(QtCore.Qt.NoPen)
    painter.setBrush(QtGui.QColor(color))
    painter.drawEllipse(1, 1, 10, 10)
    painter.end()
    return QtGui.QIcon(pixmap)


class RigCheckPanel(QtWidgets.QWidget):
    def __init__(self, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self._issues: list[_check.Issue] = []
        self._build_ui()
        self._show_issue(None)

    # --- construction ---------------------------------------------------------
    def _build_ui(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(8, 8, 8, 8)

        bar = QtWidgets.QHBoxLayout()
        self._scan_btn = QtWidgets.QPushButton("Scan scene")
        self._scan_btn.setProperty("accent", True)
        self._scan_btn.clicked.connect(self._scan)
        bar.addWidget(self._scan_btn)
        bar.addWidget(QtWidgets.QLabel("Export group:"))
        self._group = QtWidgets.QComboBox()
        self._group.setToolTip("The skeleton to check. Scan picks the one the body is skinned to.")
        self._group.activated.connect(self._scan)
        bar.addWidget(self._group, 1)
        root.addLayout(bar)

        self._verdict = QtWidgets.QLabel(_START)
        self._verdict.setWordWrap(True)
        self._verdict.setObjectName("muted")
        root.addWidget(self._verdict)

        split = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._list = QtWidgets.QListWidget()
        self._list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self._list.currentRowChanged.connect(self._on_row)
        split.addWidget(self._list)
        split.addWidget(self._build_detail())
        split.setStretchFactor(0, 2)
        split.setStretchFactor(1, 3)
        root.addWidget(split, 1)

        foot = QtWidgets.QHBoxLayout()
        self._safe_btn = QtWidgets.QPushButton("Fix all safe")
        self._safe_btn.setToolTip("Applies every fix that can't change how the rig deforms, "
                                  "as one undo step.")
        self._safe_btn.clicked.connect(self._fix_safe)
        foot.addWidget(self._safe_btn)
        self._status = QtWidgets.QLabel("")
        self._status.setWordWrap(True)
        self._status.setObjectName("muted")
        foot.addWidget(self._status, 1)
        root.addLayout(foot)

    def _build_detail(self) -> QtWidgets.QWidget:
        self._detail = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(self._detail)
        v.setContentsMargins(10, 0, 0, 0)

        self._title = QtWidgets.QLabel("")
        self._title.setObjectName("assetName")
        self._title.setWordWrap(True)
        v.addWidget(self._title)
        self._kind = QtWidgets.QLabel("")
        self._kind.setObjectName("muted")
        v.addWidget(self._kind)
        cause_head = QtWidgets.QLabel("CAUSE")
        cause_head.setObjectName("sectionHeading")
        v.addWidget(cause_head)
        self._body = QtWidgets.QLabel("")
        self._body.setWordWrap(True)
        self._body.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        v.addWidget(self._body)

        fix_head = QtWidgets.QLabel("FIX")
        fix_head.setObjectName("sectionHeading")
        v.addWidget(fix_head)
        self._action = QtWidgets.QLabel("")
        self._action.setWordWrap(True)
        v.addWidget(self._action)

        self._name = QtWidgets.QLineEdit()
        self._name.setPlaceholderText("Rig name, e.g. Eric")
        self._name.returnPressed.connect(self._fix_current)
        v.addWidget(self._name)

        buttons = QtWidgets.QHBoxLayout()
        self._fix_btn = QtWidgets.QPushButton("Fix")
        self._fix_btn.setProperty("accent", True)
        self._fix_btn.clicked.connect(self._fix_current)
        buttons.addWidget(self._fix_btn)
        self._select_btn = QtWidgets.QPushButton("Select in scene")
        self._select_btn.clicked.connect(self._select_nodes)
        buttons.addWidget(self._select_btn)
        buttons.addStretch(1)
        v.addLayout(buttons)
        v.addStretch(1)
        return self._detail

    # --- report ---------------------------------------------------------------
    def _current(self) -> _check.Issue | None:
        row = self._list.currentRow()
        return self._issues[row] if 0 <= row < len(self._issues) else None

    def _on_row(self, _row: int) -> None:
        self._show_issue(self._current())

    def _show_issue(self, issue: _check.Issue | None) -> None:
        self._detail.setVisible(issue is not None)
        if issue is None:
            return
        fixable = issue.fix != _check.FIX_MANUAL
        self._title.setText(issue.title)
        self._kind.setText(f"{_LEVEL_NAMES[issue.level]} - {issue.category}")
        self._body.setText(issue.detail)
        self._action.setText(issue.action)
        self._name.setVisible(issue.fix == _check.FIX_INPUT)
        self._name.setText(issue.default)
        self._fix_btn.setVisible(fixable)
        self._fix_btn.setText(_FIX_BUTTONS.get(issue.fix, ""))
        self._select_btn.setVisible(bool(issue.nodes))

    def _show_scan(self, scanned) -> None:
        self._issues = scanned.issues
        self._group.clear()
        for path in scanned.groups:
            self._group.addItem(_check.short(path), path)
        self._group.setCurrentIndex(self._group.findData(scanned.facts.group))

        self._list.clear()
        for issue in self._issues:
            item = QtWidgets.QListWidgetItem(
                _dot(_LEVEL_COLORS[issue.level]),
                f"{issue.title}\n{issue.category} - {_FIX_NAMES[issue.fix]}")
            self._list.addItem(item)

        level, headline = _check.verdict(self._issues)
        self._verdict.setText(headline)
        self._verdict.setStyleSheet(f"color: {_LEVEL_COLORS[level]}; font-weight: 600;")
        safe = sum(issue.fix == _check.FIX_SAFE for issue in self._issues)
        self._safe_btn.setText(f"Fix all safe ({safe})")
        self._safe_btn.setEnabled(safe > 0)
        self._list.setCurrentRow(0)
        self._show_issue(self._current())

    # --- actions --------------------------------------------------------------
    def _run(self, action):
        """Run ``action`` under a wait cursor. Returns None after reporting any failure."""
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        try:
            return action()
        except ImportError:
            self._status.setText("Rig Check needs Maya: open Outfitter inside Maya.")
        except Exception as exc:  # noqa: BLE001 - shown to the artist, never lost in a slot
            self._status.setText(str(exc))
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        return None

    def _rescan(self) -> bool:
        from ..core import maya_rig_check

        scanned = self._run(lambda: maya_rig_check.scan(self._group.currentData()))
        if scanned is None:
            return False
        self._show_scan(scanned)
        return True

    def _scan(self) -> None:
        self._status.setText("")
        self._rescan()

    def _fix_current(self) -> None:
        from ..core import maya_rig_check

        issue = self._current()
        if issue is None or issue.fix == _check.FIX_MANUAL:
            return
        done = self._run(lambda: maya_rig_check.apply_fix(
            issue.key, self._name.text(), self._group.currentData()))
        if done is not None and self._rescan():
            self._status.setText(f"{done} {_NOT_SAVED}")

    def _fix_safe(self) -> None:
        from ..core import maya_rig_check

        done = self._run(lambda: maya_rig_check.apply_safe_fixes(self._group.currentData()))
        if done is not None and self._rescan():
            self._status.setText(f"{' '.join(done)} {_NOT_SAVED}")

    def _select_nodes(self) -> None:
        from ..core import maya_rig_check

        issue = self._current()
        if issue is None:
            return
        count = self._run(lambda: maya_rig_check.select_nodes(issue.nodes))
        if count is not None:
            self._status.setText(f"Selected {count} of {len(issue.nodes)} nodes.")
