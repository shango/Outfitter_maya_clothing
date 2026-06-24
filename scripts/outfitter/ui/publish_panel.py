"""Publish tab — finalize a hand-authored garment into the library (Maya-side).

The rigger opens their authored garment scene, fills in the identity/version fields,
captures a thumbnail, and hits Publish. This widget is the thin Qt shell: every
non-trivial step is delegated to the headless :mod:`core.publish` (path/sidecar
assembly + validation) and the Maya-only :mod:`core.maya_publish` (polycount,
playblast, rig-version sniff, save). Outside Maya it still renders so the layout can
be previewed; Capture/Publish report that they need a running Maya.

UI only — verified by ``py_compile`` (PySide6 ships with Maya 2026, not the headless
test env).
"""
from __future__ import annotations

import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Callable

from PySide6 import QtCore, QtGui, QtWidgets

from .. import config
from ..core import publish as _publish
from ..core import settings as _settings

_PREVIEW_BOX = 140


def _maya_available() -> bool:
    try:
        import maya.cmds  # type: ignore  # noqa: F401
    except Exception:
        return False
    return True


@contextmanager
def _wait_cursor():
    """Show the wait cursor for the duration of the block, restoring it even on error."""
    QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
    try:
        yield
    finally:
        QtWidgets.QApplication.restoreOverrideCursor()


class PublishPanel(QtWidgets.QWidget):
    """Form + capture + publish for the currently-open garment scene."""

    def __init__(self, on_published: Callable[[], None] | None = None, parent=None):
        super().__init__(parent)
        self._on_published = on_published
        self._captured_thumb: Path | None = None
        self._build_ui()
        self._refresh_remote_label()

    # --- construction ---------------------------------------------------------
    def _build_ui(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        self._build_widgets()
        top = QtWidgets.QWidget()
        outer = QtWidgets.QHBoxLayout(top)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(14)
        # Left: steps 1–3 (the in-Maya rig work). Right: steps 4 & 5 side by side,
        # with the asset-details form below them. Splitting the five steps across two
        # columns keeps the window from growing too tall.
        outer.addWidget(self._build_left_column(), 0)
        outer.addWidget(self._build_right_column(), 1)

        # The two-column steps row sizes to its content (every step stays visible); the
        # one-line status sits just beneath it and the log takes the remaining height.
        root.addWidget(top, 0)
        root.addWidget(self._status, 0)
        root.addWidget(self._build_log_panel(), 1)
        self._log("Publish tab ready. Work down the numbered steps, then publish.", "info")

    def _build_widgets(self) -> None:
        """Create every interactive widget once; the layout builders place them."""
        # identity / metadata fields (left form, filled in Step 4)
        self._name = QtWidgets.QLineEdit()
        self._name.setPlaceholderText("e.g. trench_coat_A")
        self._version = QtWidgets.QLineEdit("1.0.0")
        self._compat = QtWidgets.QLineEdit("v03")
        self._compat.setPlaceholderText("comma-separated, e.g. v03, v04")
        self._rigver = QtWidgets.QLineEdit()
        self._rigver.setPlaceholderText("e.g. v03")
        self._author = QtWidgets.QLineEdit()
        self._desc = QtWidgets.QPlainTextEdit()
        self._desc.setPlaceholderText("Brief description shown in the browser…")
        self._desc.setFixedHeight(70)

        # Type / Gender drive Step 1 (skin-set + body variant). Start unset on purpose
        # so the rigger picks them rather than silently defaulting to the first entry.
        self._type = QtWidgets.QComboBox()
        self._type.addItems(list(config.ASSET_TYPES))
        self._type.setCurrentIndex(-1)
        self._type.setPlaceholderText("— set clothing type —")
        self._gender = QtWidgets.QComboBox()
        self._gender.addItems(list(config.GENDERS))
        self._gender.setCurrentIndex(-1)
        self._gender.setPlaceholderText("— set body variant —")
        # keep both dropdowns a comfortable height so they aren't squeezed flat
        for combo in (self._type, self._gender):
            combo.setMinimumHeight(28)

        # step action buttons
        self._skeleton_btn = QtWidgets.QPushButton("Create cloth skeleton")
        self._skeleton_btn.clicked.connect(self._create_skeleton)
        self._connect_btn = QtWidgets.QPushButton("Load test body")
        self._connect_btn.clicked.connect(self._load_test_body)
        self._disconnect_btn = QtWidgets.QPushButton("Remove test body")
        self._disconnect_btn.clicked.connect(self._remove_test_body)
        self._prune_btn = QtWidgets.QPushButton("Delete unused joints (optional)")
        self._prune_btn.clicked.connect(self._prune_joints)
        self._capture_btn = QtWidgets.QPushButton("Capture thumbnail")
        self._capture_btn.clicked.connect(self._capture)
        self._check_btn = QtWidgets.QPushButton("Check scene")
        self._check_btn.clicked.connect(self._check_scene)
        self._publish_btn = QtWidgets.QPushButton("Publish ▸")
        self._publish_btn.setProperty("accent", True)
        self._publish_btn.clicked.connect(self._publish)

        # rare maintenance: re-capture the canonical skeleton data from the rig in-scene
        # (e.g. after a new rig generation). Overwrites the shipped cloth_skeleton.json.
        self._regen_btn = QtWidgets.QToolButton()
        self._regen_btn.setText("Regenerate skeleton data from rig…")
        self._regen_btn.clicked.connect(self._regen_skeleton)

        # thumbnail preview (Step 4)
        self._preview = QtWidgets.QLabel("no thumbnail\ncaptured yet")
        self._preview.setObjectName("previewImage")
        self._preview.setAlignment(QtCore.Qt.AlignCenter)
        self._preview.setFixedSize(_PREVIEW_BOX, _PREVIEW_BOX)

        # publish destination read-out (Step 5) + one-line status strip
        self._dest_label = QtWidgets.QLabel("")
        self._dest_label.setObjectName("stepDest")
        self._dest_label.setWordWrap(True)
        self._status = QtWidgets.QLabel("")
        self._status.setObjectName("muted")
        self._status.setWordWrap(True)

    def _build_details_form(self) -> QtWidgets.QWidget:
        """Right column: asset identity / metadata, filled out during Step 4."""
        box = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(box)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(8)

        heading = QtWidgets.QLabel("ASSET DETAILS")  # QSS can't upper-case; do it here
        heading.setObjectName("sectionHeading")
        v.addWidget(heading)
        hint = QtWidgets.QLabel("Fill these out before you publish (Step 5).")
        hint.setObjectName("muted")
        hint.setWordWrap(True)
        v.addWidget(hint)

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignRight)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)

        rig_row = QtWidgets.QHBoxLayout()
        detect = QtWidgets.QToolButton()
        detect.setText("Detect")
        detect.clicked.connect(self._detect_rig)
        rig_row.addWidget(self._rigver, 1)
        rig_row.addWidget(detect)

        form.addRow("Asset name", self._name)
        form.addRow("Version", self._version)
        form.addRow("GenHuman compat", self._compat)
        form.addRow("Rig version built-for", self._wrap(rig_row))
        form.addRow("Author", self._author)
        form.addRow("Description", self._desc)
        v.addLayout(form)
        return box

    def _build_left_column(self) -> QtWidgets.QWidget:
        """Left column: steps 1–3 — build the rig, skin it, strip the test body."""
        col = QtWidgets.QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(10)
        # The right column (form + steps 4/5) is taller, so this column is stretched to
        # match. Rather than pool that slack into gaps *between* the cards, steps 2 and 3
        # grow to absorb it — uniform card spacing, and step 3 bottom-aligns with steps 4/5.

        # Step 1 — set up the rig (Type + Gender live here, with the build buttons)
        card, body = self._step_card(
            1, "Set up the cloth rig",
            "Choose the garment Type and Gender, build the cloth rig, then load a "
            "test body to pose the garment against.", center=True)
        picks = QtWidgets.QFormLayout()
        picks.setLabelAlignment(QtCore.Qt.AlignRight)
        picks.setContentsMargins(0, 2, 0, 2)
        picks.setHorizontalSpacing(10)
        picks.setVerticalSpacing(8)
        picks.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)
        picks.addRow("Type", self._type)
        picks.addRow("Gender", self._gender)
        body.addLayout(picks)
        body.addWidget(self._skeleton_btn)
        body.addWidget(self._connect_btn)
        col.addWidget(card, 0)  # step 1 keeps its natural height (most content)

        # Step 2 — skin (instruction only, no buttons); grows to share the slack
        card, _ = self._step_card(
            2, "Skin the mesh",
            "Bind the garment mesh to the highlighted (green) joints: "
            "Skin ▸ Bind Skin.", center=True)
        card.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                           QtWidgets.QSizePolicy.MinimumExpanding)
        col.addWidget(card, 1)

        # Step 3 — remove the test body (+ optional joint prune); grows, content centered
        card, body = self._step_card(
            3, "Remove the test body",
            "Delete the test body so the cloth joints go static and the asset is "
            "publish-safe.", center=True)
        card.setSizePolicy(QtWidgets.QSizePolicy.Preferred,
                           QtWidgets.QSizePolicy.MinimumExpanding)
        body.addWidget(self._disconnect_btn)
        body.addWidget(self._prune_btn)
        col.addWidget(card, 1)

        host = QtWidgets.QWidget()
        host.setLayout(col)
        host.setMinimumWidth(300)
        host.setMaximumWidth(360)
        return host

    def _build_right_column(self) -> QtWidgets.QWidget:
        """Right column: the asset-details form, then steps 4 & 5 side by side below."""
        col = QtWidgets.QVBoxLayout()
        col.setContentsMargins(0, 0, 0, 0)
        col.setSpacing(10)

        row = QtWidgets.QHBoxLayout()
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(10)

        # Step 4 — thumbnail: capture button sits *beneath* the preview image
        card, body = self._step_card(
            4, "Capture the thumbnail",
            "Frame the garment in the viewport, then capture a thumbnail.")
        body.addSpacing(2)
        body.addWidget(self._preview, 0, QtCore.Qt.AlignHCenter)
        body.addWidget(self._capture_btn)
        row.addWidget(card, 1)

        # Step 5 — publish (always to the remote library)
        card, body = self._step_card(
            5, "Publish",
            "Fill out the asset details below, run a final scene check, then "
            "publish. The asset is sent to the shared remote library.")
        body.addWidget(self._dest_label)
        body.addStretch(1)
        body.addWidget(self._check_btn)
        body.addWidget(self._publish_btn)
        row.addWidget(card, 1)

        col.addWidget(self._build_details_form())
        col.addLayout(row)
        # No trailing stretch: the steps 4/5 row is the column's bottom, so the left
        # column (steps 1–3) stretches to align step 3 with it. The status strip lives
        # full-width below both columns (see _build_ui).

        host = QtWidgets.QWidget()
        host.setLayout(col)
        return host

    def _step_card(self, number: int, title: str, instruction: str, *,
                   center: bool = False) -> tuple[QtWidgets.QFrame, QtWidgets.QVBoxLayout]:
        """A numbered step card: big number + title + instruction, returns its body layout.

        With ``center=True`` the number and the body content (title, instruction, and any
        buttons the caller appends) sit in the vertical middle of the card, so a card taller
        than its content keeps balanced top/bottom padding. Default top-aligns — steps 4 & 5
        rely on that for their preview image and bottom-pinned Publish button.
        """
        card = QtWidgets.QFrame()
        card.setObjectName("stepCard")
        # Vertically the card hugs its content; horizontally it fills its column slot.
        card.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        row = QtWidgets.QHBoxLayout(card)
        row.setContentsMargins(14, 12, 14, 14)
        row.setSpacing(12)

        num = QtWidgets.QLabel(str(number))
        num.setObjectName("stepNumber")
        num.setFixedWidth(28)
        num_v = QtCore.Qt.AlignVCenter if center else QtCore.Qt.AlignTop
        num.setAlignment(num_v | QtCore.Qt.AlignRight)
        row.addWidget(num, 0)

        body = QtWidgets.QVBoxLayout()
        body.setSpacing(8)
        title_lbl = QtWidgets.QLabel(title)
        title_lbl.setObjectName("stepTitle")
        title_lbl.setWordWrap(True)
        body.addWidget(title_lbl)
        ins = QtWidgets.QLabel(instruction)
        ins.setObjectName("stepInstruction")
        ins.setWordWrap(True)
        # wordWrap labels need their height-for-width respected or they clip; let the
        # label grow vertically to fit the wrapped text in this column width.
        ins.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        ins.setMinimumHeight(ins.fontMetrics().height())
        body.addWidget(ins)

        if center:
            # Sandwich the content between stretches so it stays a block and sits centered;
            # the number is aligned to vertical-centre above to pair with it.
            wrap = QtWidgets.QVBoxLayout()
            wrap.addStretch(1)
            wrap.addLayout(body)
            wrap.addStretch(1)
            row.addLayout(wrap, 1)
        else:
            row.addLayout(body, 1)
        return card, body

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        # The remote folder may be changed on the Setup tab after this panel is built;
        # refresh the Step 5 destination read-out each time the tab is shown.
        super().showEvent(event)
        self._refresh_remote_label()

    @staticmethod
    def _wrap(layout: QtWidgets.QLayout) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        w.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        return w

    # --- log ------------------------------------------------------------------
    _LOG_COLORS = {
        "info": "#9a9a9a",
        "step": "#cdd2d8",
        "ok": "#7ec699",
        "warn": "#e0b057",
        "error": "#e06c75",
    }

    def _build_log_panel(self) -> QtWidgets.QWidget:
        box = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(box)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(4)

        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("LOG")
        title.setObjectName("sectionHeading")
        header.addWidget(title)
        header.addStretch(1)
        # rare maintenance action — parked here, out of the numbered step flow
        header.addWidget(self._regen_btn)
        clear = QtWidgets.QToolButton()
        clear.setText("Clear")
        clear.clicked.connect(self._clear_log)
        header.addWidget(clear)
        v.addLayout(header)

        self._log_view = QtWidgets.QPlainTextEdit()
        self._log_view.setObjectName("logView")
        self._log_view.setReadOnly(True)
        # The log fills the leftover space below the steps; give it a sensible floor
        # and let it grow with the window (it scrolls its own content).
        self._log_view.setMinimumHeight(140)
        mono = QtGui.QFont("Consolas")
        mono.setStyleHint(QtGui.QFont.Monospace)
        mono.setPointSize(9)
        self._log_view.setFont(mono)
        v.addWidget(self._log_view)
        return box

    def _clear_log(self) -> None:
        self._log_view.clear()
        self._log("Log cleared.", "info")

    def _log(self, message: str, level: str = "info") -> None:
        """Append one color-coded, timestamped line to the log (multi-line aware)."""
        color = self._LOG_COLORS.get(level, self._LOG_COLORS["info"])
        stamp = QtCore.QTime.currentTime().toString("HH:mm:ss")
        tag = level.upper().ljust(5).replace(" ", "&nbsp;")

        def esc(s: str) -> str:
            return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))

        # continuation lines indent under the message column for readability
        body = esc(message).replace("\n", "<br>" + "&nbsp;" * 19)
        self._log_view.appendHtml(
            f'<span style="color:#6f7378">[{stamp}]</span> '
            f'<span style="color:{color};font-weight:bold">{tag}</span> '
            f'<span style="color:{color}">{body}</span>')
        sb = self._log_view.verticalScrollBar()
        sb.setValue(sb.maximum())

    def _report(self, message: str, level: str = "info") -> None:
        """Log a headline line and mirror it to the one-line status strip under Publish."""
        self._log(message, level)
        self._status.setText(message)

    def _log_issues(self, issues) -> int:
        """Log each PreflightIssue (with its fix); return the error count."""
        errors = 0
        for issue in issues:
            self._log(issue.message, issue.level)
            if issue.is_error:
                errors += 1
            if issue.fix:
                self._log("→ " + issue.fix, "info")
        return errors

    # --- destination ----------------------------------------------------------
    def _remote_dir(self) -> Path | None:
        """The configured remote library — the one and only publish target."""
        return _settings.read_locations().remote

    def _refresh_remote_label(self) -> None:
        """Update the Step 5 destination read-out (warns when no remote is set)."""
        remote = self._remote_dir()
        if remote is not None:
            self._dest_label.setText(f"Publishes to remote library:\n{remote}")
            self._dest_label.setProperty("warn", False)
        else:
            self._dest_label.setText(
                "⚠ No remote library set — configure it on the Setup tab before "
                "publishing.")
            self._dest_label.setProperty("warn", True)
        # re-polish so the dynamic 'warn' property restyles the label
        self._dest_label.style().unpolish(self._dest_label)
        self._dest_label.style().polish(self._dest_label)

    # --- Maya guard -----------------------------------------------------------
    def _require_maya(self) -> bool:
        if _maya_available():
            return True
        self._log("This action needs a running Maya 2026.", "error")
        QtWidgets.QMessageBox.warning(
            self, "Outfitter",
            "Publishing needs a running Maya 2026 — it captures the thumbnail and "
            "polycount from the open garment scene.")
        return False

    def _require_type(self) -> str | None:
        """Return the chosen asset Type, or warn and return None if it's still unset."""
        asset_type = self._type.currentText().strip()
        if asset_type:
            return asset_type
        self._report("Set the clothing Type first (the dropdown in the form).", "warn")
        QtWidgets.QMessageBox.warning(
            self, "Set clothing type",
            "Choose the garment Type in the form before this step — it decides which "
            "skin joints get highlighted.")
        return None

    def _require_gender(self) -> str | None:
        """Return the chosen gender variant, or warn and return None if still unset."""
        gender = self._gender.currentText().strip()
        if gender:
            return gender
        self._report("Set the Gender first (the dropdown in the form).", "warn")
        QtWidgets.QMessageBox.warning(
            self, "Set gender",
            "Choose the body variant (male / female) the garment is pre-fit to before "
            "publishing — every asset must declare its gender.")
        return None

    # --- actions --------------------------------------------------------------
    def _detect_rig(self) -> None:
        if not self._require_maya():
            return
        from ..core import maya_publish
        version = maya_publish.detect_rig_version()
        if version:
            self._rigver.setText(version)
            self._report(f"Detected rig version: {version}", "ok")
        else:
            self._report("Could not detect a rig version — enter it manually.", "warn")

    def _create_skeleton(self) -> None:
        """Rebuild the cloth_* skeleton and, in the same click, select the skin joints.

        The Type drives the skin-set, so it's required up front. The skeleton is built
        first, then the recommended cloth_skin_SET for the Type is gathered, highlighted
        and left selected, ready for Bind Skin.
        """
        if not self._require_maya():
            return
        asset_type = self._require_type()
        if asset_type is None:
            return
        from ..core import maya_skeleton
        self._log(f"Create cloth skeleton ({asset_type})…", "step")
        try:
            with _wait_cursor():
                skel = maya_skeleton.build_cloth_skeleton()
                self._log(skel.summary(), "ok")
                groups = maya_skeleton.scaffold_asset_groups()
                self._log(groups.summary(),
                          "warn" if groups.mesh_group_empty else "ok")
                skin = maya_skeleton.build_skin_set(asset_type)
        except Exception as exc:  # noqa: BLE001 — surface the Maya error in the UI
            self._report(f"Create cloth skeleton failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Create cloth skeleton failed", str(exc))
            return
        self._report(skin.summary(), "ok")
        if skin.missing:
            self._log(
                "Not in this skeleton (skip): " + ", ".join(skin.missing), "info")
        self._log(
            "Next: bind the mesh to the selected (green) joints — Skin > Bind Skin.",
            "info")

    def _load_test_body(self) -> None:
        if not self._require_maya():
            return
        gender = self._require_gender()
        if gender is None:
            return
        from ..core import maya_testfit
        self._log(f"Load test body ({gender})…", "step")
        try:
            with _wait_cursor():
                result = maya_testfit.load_test_body(gender)
        except Exception as exc:  # noqa: BLE001 — surface the Maya error in the UI
            self._report(f"Load test body failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Load test body failed", str(exc))
            return
        self._report(result.summary(), "ok")
        for j in result.connect.unmatched:
            self._log(f"helper joint not driven (no body match): {j}", "info")
        self._log(
            "Pose the body's controls and watch the garment deform. "
            "Remove test body before publishing.", "info")

    def _remove_test_body(self) -> None:
        if not self._require_maya():
            return
        from ..core import maya_testfit
        self._log("Remove test body…", "step")
        try:
            with _wait_cursor():
                result = maya_testfit.remove_test_body()
        except Exception as exc:  # noqa: BLE001 — surface the Maya error in the UI
            self._report(f"Remove test body failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Remove test body failed", str(exc))
            return
        self._report(result.summary(), "ok")

    def _regen_skeleton(self) -> None:
        if not self._require_maya():
            return
        from ..core import skeleton as _skeleton
        ok = QtWidgets.QMessageBox.question(
            self, "Regenerate skeleton data?",
            "This captures the cloth_* skeleton from the GenHuman rig in the current "
            "scene and OVERWRITES the canonical skeleton data:\n\n"
            f"{_skeleton.skeleton_file()}\n\n"
            "Every future 'Create cloth skeleton' will rebuild this captured pose. "
            "Make sure the rig is the intended build and posed correctly. Continue?")
        if ok != QtWidgets.QMessageBox.Yes:
            self._log("Regenerate skeleton data cancelled.", "info")
            return
        from ..core import maya_skeleton
        self._log("Regenerate skeleton data from rig…", "step")
        try:
            with _wait_cursor():
                result = maya_skeleton.capture_cloth_skeleton_from_rig()
        except Exception as exc:  # noqa: BLE001 — surface the Maya error in the UI
            self._report(f"Regenerate skeleton failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Regenerate skeleton failed", str(exc))
            return
        self._report(result.summary(), "ok")
        QtWidgets.QMessageBox.information(self, "Skeleton data regenerated", result.summary())

    @staticmethod
    def _joint_preview(names: list[str], limit: int = 12) -> str:
        if not names:
            return "  (none)"
        shown = names[:limit]
        out = "\n".join(f"  • {n}" for n in shown)
        if len(names) > limit:
            out += f"\n  …and {len(names) - limit} more"
        return out

    def _prune_joints(self) -> None:
        if not self._require_maya():
            return
        from ..core import maya_skeleton
        self._log("Delete unused joints: planning…", "step")
        try:
            with _wait_cursor():
                plan = maya_skeleton.plan_prune_unskinned()
        except Exception as exc:  # noqa: BLE001 — surface the Maya error in the UI
            self._report(f"Delete unused joints failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Delete unused joints failed", str(exc))
            return

        if plan.is_noop:
            QtWidgets.QMessageBox.information(
                self, "Nothing to delete",
                "Every cloth_* joint is skinned, an interior joint with skinned "
                "children, or the root — there's nothing safe to prune.")
            self._report("No unused joints to delete.", "info")
            return

        self._log(
            f"Plan: delete {len(plan.delete)} leaf joint(s), "
            f"keep {len(plan.kept_unweighted)} unweighted interior joint(s).", "info")

        body = (
            f"Delete {len(plan.delete)} unused joint(s) the garment doesn't skin to?\n\n"
            "DELETE (unweighted leaves):\n"
            f"{self._joint_preview(list(plan.delete))}\n\n")
        if plan.kept_unweighted:
            body += (
                "KEEP (unweighted, but have skinned children — required to mirror the "
                "body):\n"
                f"{self._joint_preview(list(plan.kept_unweighted))}\n\n")
        body += "Skinned joints and cloth_root are always kept. Continue?"

        ok = QtWidgets.QMessageBox.question(self, "Delete unused joints?", body)
        if ok != QtWidgets.QMessageBox.Yes:
            self._log("Delete unused joints cancelled.", "info")
            return

        try:
            with _wait_cursor():
                result = maya_skeleton.apply_prune(plan)
        except Exception as exc:  # noqa: BLE001 — surface the Maya error in the UI
            self._report(f"Delete unused joints failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Delete unused joints failed", str(exc))
            return
        self._report(result.summary(), "ok")

    def _capture(self) -> None:
        if not self._require_maya():
            return
        from ..core import maya_publish
        out = Path(tempfile.gettempdir()) / "outfitter_thumb.png"
        self._log("Capture thumbnail…", "step")
        try:
            with _wait_cursor():
                meshes = maya_publish.find_garment_meshes()
                maya_publish.capture_thumbnail(meshes, str(out))
        except Exception as exc:  # noqa: BLE001 — surface the Maya error in the UI
            self._report(f"Capture failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Capture failed", str(exc))
            return
        self._captured_thumb = out
        self._show_preview(out)
        self._report("Thumbnail captured — review, then Publish.", "ok")

    def _check_scene(self) -> None:
        """Run the pre-publish sanity check and log every finding (no side effects)."""
        if not self._require_maya():
            return
        from ..core import maya_publish
        self._log("Pre-publish check…", "step")
        try:
            with _wait_cursor():
                issues = maya_publish.preflight_scene()
        except Exception as exc:  # noqa: BLE001 — surface the Maya error in the UI
            self._report(f"Pre-publish check failed: {exc}", "error")
            return
        errors = self._log_issues(issues)
        if errors:
            self._report(
                f"Pre-publish check: {errors} blocking issue(s) — fix before Publish.",
                "error")
        else:
            self._report("Pre-publish check passed — ready to Publish.", "ok")

    def _show_preview(self, png: Path) -> None:
        pm = QtGui.QPixmap(str(png))
        if pm.isNull():
            self._preview.setText("preview failed")
            return
        self._preview.setPixmap(pm.scaled(
            self._preview.size(), QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation))

    def _gather_spec(self) -> _publish.PublishSpec | None:
        name = self._name.text().strip()
        if not name:
            self._report("Enter an asset name first.", "warn")
            return None
        asset_type = self._require_type()
        if asset_type is None:
            return None
        gender = self._require_gender()
        if gender is None:
            return None
        compat = tuple(
            t.strip() for t in self._compat.text().replace(";", ",").split(",")
            if t.strip())
        return _publish.PublishSpec(
            asset_name=name,
            asset_type=asset_type,
            gender=gender,
            cloth_version=self._version.text().strip() or "1.0.0",
            genhuman_compat=compat,
            author=self._author.text().strip(),
            description=self._desc.toPlainText().strip(),
            rig_version=self._rigver.text().strip(),
            created=_publish.today_iso(),
        )

    def _publish(self) -> None:
        if not self._require_maya():
            return
        # Publishing always targets the shared remote library; refuse (and warn) if
        # the studio remote folder hasn't been configured on the Setup tab.
        self._refresh_remote_label()
        remote = self._remote_dir()
        if remote is None:
            self._report(
                "No remote library set — configure it on the Setup tab, then publish "
                "again.", "error")
            QtWidgets.QMessageBox.warning(
                self, "No remote library set",
                "Publishing sends the asset to the shared remote library, but no "
                "remote folder is configured.\n\nSet it on the Setup tab, then "
                "publish again.")
            return
        self._log("Publish: validating metadata…", "step")
        spec = self._gather_spec()
        if spec is None:
            return

        meta, errors = spec.metadata()
        if meta is None:
            for err in errors:
                self._log(err, "error")
            self._report("Incomplete metadata — fix the fields above and Publish again.",
                         "error")
            QtWidgets.QMessageBox.warning(
                self, "Incomplete metadata",
                "Fix these before publishing:\n\n" + "\n".join(errors))
            return

        from ..core import maya_publish

        # Pre-publish sanity check: rig still in scene, namespaces, garment skinned to
        # non-cloth_* joints, missing groups — surface them all (with fixes) and block,
        # rather than silently writing a rig-bloated, validation-failing .ma.
        self._log("Publish: pre-publish scene check…", "step")
        try:
            issues = maya_publish.preflight_scene()
        except Exception as exc:  # noqa: BLE001
            self._report(f"Pre-publish check failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Publish failed", str(exc))
            return
        n_errors = self._log_issues(issues)
        if n_errors:
            self._report(
                f"Publish blocked — {n_errors} issue(s) to fix (see log).", "error")
            QtWidgets.QMessageBox.warning(
                self, "Fix these before publishing",
                "The scene isn't publish-ready:\n\n"
                + "\n".join(f"• {i.message}\n   → {i.fix}" for i in issues if i.is_error))
            return

        paths = _publish.destination_paths(remote, spec.asset_name)
        if paths.ma.exists():
            ok = QtWidgets.QMessageBox.question(
                self, "Overwrite?",
                f"'{paths.ma.name}' already exists in the remote library.\nOverwrite it?")
            if ok != QtWidgets.QMessageBox.Yes:
                self._log("Publish cancelled (kept existing file).", "info")
                return

        self._log(f"Publish: writing → {paths.folder}", "step")
        try:
            with _wait_cursor():
                meshes = maya_publish.find_garment_meshes()
                spec.tri_count, spec.vert_count = maya_publish.poly_counts(meshes)
                paths.folder.mkdir(parents=True, exist_ok=True)

                # thumbnail: reuse a captured one, else grab one now
                if self._captured_thumb and self._captured_thumb.is_file():
                    shutil.copyfile(self._captured_thumb, paths.thumbnail)
                else:
                    maya_publish.capture_thumbnail(meshes, str(paths.thumbnail))

                # Embed the metadata in the scene (cloth_info) so the saved .ma is
                # self-describing, then save; the sidecar carries the same data.
                maya_publish.write_info_node(spec.to_sidecar())
                maya_publish.save_ma(str(paths.ma))
                _publish.write_sidecar(paths, spec)
                report = _publish.validate_published_ma(paths.ma)
        except Exception as exc:  # noqa: BLE001
            self._report(f"Publish failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Publish failed", str(exc))
            return

        if report.ok:
            self._report(
                f"Published {spec.asset_name} ({spec.gender} {spec.asset_type}) → "
                f"{paths.folder} ({spec.tri_count:,} tris). {report.summary_line()}.", "ok")
        else:
            for issue in report.errors:
                self._log(str(issue), "error")
            self._report(
                f"Published with issues — {report.summary_line()}.", "warn")
            QtWidgets.QMessageBox.warning(
                self, "Published with validation errors",
                "The files were written, but the asset failed structure validation "
                "and won't attach until fixed:\n\n"
                + "\n".join(str(i) for i in report.errors))

        if self._on_published is not None:
            self._on_published()
