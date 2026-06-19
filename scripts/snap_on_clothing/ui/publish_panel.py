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

import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Callable

from PySide6 import QtCore, QtGui, QtWidgets

from .. import config
from ..core import publish as _publish
from ..core import settings as _settings

_PREVIEW_BOX = 220


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
        self._reset_dest_to_default()

    # --- construction ---------------------------------------------------------
    def _build_ui(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        top = QtWidgets.QWidget()
        outer = QtWidgets.QHBoxLayout(top)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(14)

        # left: identity / version form
        form_box = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(form_box)
        form.setLabelAlignment(QtCore.Qt.AlignRight)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)

        self._name = QtWidgets.QLineEdit()
        self._name.setPlaceholderText("e.g. trench_coat_A")
        self._type = QtWidgets.QComboBox()
        self._type.addItems(list(config.ASSET_TYPES))
        # Start unset on purpose: the type drives scaffold/skin-set/publish, so make the
        # rigger choose it rather than silently defaulting to the first type.
        self._type.setCurrentIndex(-1)
        self._type.setPlaceholderText("— set clothing type —")
        self._version = QtWidgets.QLineEdit("1.0.0")
        self._compat = QtWidgets.QLineEdit("v03")
        self._compat.setPlaceholderText("comma-separated, e.g. v03, v04")

        rig_row = QtWidgets.QHBoxLayout()
        self._rigver = QtWidgets.QLineEdit()
        self._rigver.setPlaceholderText("e.g. v03")
        detect = QtWidgets.QToolButton()
        detect.setText("Detect")
        detect.setToolTip("Read the rig version from the current scene")
        detect.clicked.connect(self._detect_rig)
        rig_row.addWidget(self._rigver, 1)
        rig_row.addWidget(detect)

        self._author = QtWidgets.QLineEdit()
        self._desc = QtWidgets.QPlainTextEdit()
        self._desc.setPlaceholderText("Brief description shown in the browser…")
        self._desc.setFixedHeight(70)

        form.addRow("Asset name", self._name)
        form.addRow("Type", self._type)
        form.addRow("Version", self._version)
        form.addRow("GenHuman compat", self._compat)
        form.addRow("Rig version built-for", self._wrap(rig_row))
        form.addRow("Author", self._author)
        form.addRow("Description", self._desc)

        # destination folder
        dest_row = QtWidgets.QHBoxLayout()
        self._dest = QtWidgets.QLineEdit()
        self._dest.setReadOnly(True)
        dest_browse = QtWidgets.QToolButton()
        dest_browse.setText("Browse…")
        dest_browse.clicked.connect(self._choose_dest)
        dest_row.addWidget(self._dest, 1)
        dest_row.addWidget(dest_browse)
        form.addRow("Library folder", self._wrap(dest_row))

        outer.addWidget(form_box, 1)

        # right: preview + actions
        right = QtWidgets.QVBoxLayout()
        right.setSpacing(8)

        # authoring helper: rebuild the canonical cloth_* skeleton in-scene (skipping the
        # import-rig / duplicate / rename chore) AND, in the same click, gather the
        # recommended skin joints for the chosen Type into cloth_skin_SET. One button.
        self._skeleton_btn = QtWidgets.QPushButton("Create cloth skeleton")
        self._skeleton_btn.setToolTip(
            "Rebuild the canonical GenHuman cloth_* skeleton in the scene (no rig "
            "import needed) and select + highlight (green) the joints to bind to for the "
            "chosen Type, gathered into 'cloth_skin_SET'. Set the Type first. Then skin "
            "the mesh to the selection (Skin > Bind Skin).")
        self._skeleton_btn.clicked.connect(self._create_skeleton)
        right.addWidget(self._skeleton_btn)

        # skinning test: drive the cloth_* skeleton from the GenHuman body already in the
        # scene so the rigger can pose the rig and confirm the garment deforms, then break
        # the connections again so the asset is publish-safe. Authoring-time attach().
        test_row = QtWidgets.QHBoxLayout()
        test_row.setContentsMargins(0, 0, 0, 0)
        self._connect_btn = QtWidgets.QPushButton("Connect test body")
        self._connect_btn.setToolTip(
            "After binding: drive the cloth_* skeleton from the GenHuman body in the "
            "scene. Pose the body's controls and watch the garment deform to verify the "
            "skinning. Disconnect before publishing.")
        self._connect_btn.clicked.connect(self._connect_test_body)
        self._disconnect_btn = QtWidgets.QPushButton("Disconnect test body")
        self._disconnect_btn.setToolTip(
            "Break the test-body connections so the cloth_* joints go static again and "
            "the asset is publish-safe. Run before Publish.")
        self._disconnect_btn.clicked.connect(self._disconnect_test_body)
        test_row.addWidget(self._connect_btn)
        test_row.addWidget(self._disconnect_btn)
        right.addWidget(self._wrap(test_row))

        # maintenance: re-capture the canonical skeleton data from the rig in-scene
        # (e.g. after a new rig generation). Overwrites the shipped cloth_skeleton.json.
        self._regen_btn = QtWidgets.QToolButton()
        self._regen_btn.setText("Regenerate skeleton data from rig…")
        self._regen_btn.setToolTip(
            "Capture a fresh cloth_skeleton.json from the GenHuman rig currently in the "
            "scene. Use after a new rig build; 'Create cloth skeleton' then rebuilds "
            "this pose. Overwrites the shipped skeleton data.")
        self._regen_btn.clicked.connect(self._regen_skeleton)
        right.addWidget(self._regen_btn)

        # authoring helper (post-skin): delete the cloth_* joints the garment doesn't
        # skin to, replacing the manual prune chore. Safe — only leaf non-influence
        # joints go; unweighted interior joints are kept (the chain mirrors the body).
        self._prune_btn = QtWidgets.QPushButton("Delete unused joints")
        self._prune_btn.setToolTip(
            "After skinning: delete the cloth_* joints your garment doesn't skin to. "
            "Only safe leaf joints are removed — unweighted joints that still have "
            "skinned children are kept, because the cloth hierarchy must mirror the "
            "body. Run after skinning, before Scaffold fit rig.")
        self._prune_btn.clicked.connect(self._prune_joints)
        right.addWidget(self._prune_btn)

        # authoring helper: build the fit rig (lattice + cloth_fit_ctrl + SDKs) so the
        # rigger only has to tune the keyed extremes, not wire deformers by hand.
        self._scaffold_btn = QtWidgets.QPushButton("Scaffold fit rig")
        self._scaffold_btn.setToolTip(
            "Build cloth_fit_ctrl + a frontOfChain fit lattice + default fit SDKs for "
            "the selected Type. Run after modelling + skinning the garment, then tune "
            "the keyed extremes (and point-key any region attrs).")
        self._scaffold_btn.clicked.connect(self._scaffold)
        right.addWidget(self._scaffold_btn)

        heading = QtWidgets.QLabel("THUMBNAIL")  # QSS can't upper-case; do it here
        heading.setObjectName("sectionHeading")
        right.addWidget(heading)
        self._preview = QtWidgets.QLabel("no thumbnail\ncaptured yet")
        self._preview.setObjectName("previewImage")
        self._preview.setAlignment(QtCore.Qt.AlignCenter)
        self._preview.setFixedSize(_PREVIEW_BOX, _PREVIEW_BOX)
        right.addWidget(self._preview, 0, QtCore.Qt.AlignHCenter)

        self._capture_btn = QtWidgets.QPushButton("Capture thumbnail")
        self._capture_btn.setToolTip("Playblast a framed shot of the garment")
        self._capture_btn.clicked.connect(self._capture)
        right.addWidget(self._capture_btn)

        right.addStretch(1)

        # pre-publish sanity check: surface the common authoring mistakes (rig left in,
        # namespaces, garment skinned to non-cloth_* joints) with fixes, before Publish.
        self._check_btn = QtWidgets.QPushButton("Check scene")
        self._check_btn.setToolTip(
            "Run the pre-publish sanity check: rig present, namespaces, required groups, "
            "cloth_root, and whether the garment is skinned to the cloth_* joints. "
            "Results go to the log below.")
        self._check_btn.clicked.connect(self._check_scene)
        right.addWidget(self._check_btn)

        self._publish_btn = QtWidgets.QPushButton("Publish ▸")
        self._publish_btn.setProperty("accent", True)
        self._publish_btn.setToolTip("Save the .ma + sidecar + thumbnail into the library")
        self._publish_btn.clicked.connect(self._publish)
        right.addWidget(self._publish_btn)

        self._status = QtWidgets.QLabel("")
        self._status.setObjectName("muted")
        self._status.setWordWrap(True)
        right.addWidget(self._status)

        outer.addLayout(right, 0)

        root.addWidget(top)
        root.addWidget(self._build_log_panel(), 1)
        self._log("Publish tab ready. Run 'Check scene' before publishing.", "info")

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
        clear = QtWidgets.QToolButton()
        clear.setText("Clear")
        clear.setToolTip("Clear the log")
        clear.clicked.connect(self._clear_log)
        header.addWidget(clear)
        v.addLayout(header)

        self._log_view = QtWidgets.QPlainTextEdit()
        self._log_view.setObjectName("logView")
        self._log_view.setReadOnly(True)
        self._log_view.setMinimumHeight(150)
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
    def _reset_dest_to_default(self) -> None:
        loc = _settings.read_locations()
        default = loc.local or config.bundled_asset_dir()
        self._dest.setText(str(default))

    def _choose_dest(self) -> None:
        folder = QtWidgets.QFileDialog.getExistingDirectory(
            self, "Choose library folder to publish into", self._dest.text())
        if folder:
            self._dest.setText(folder)

    # --- Maya guard -----------------------------------------------------------
    def _require_maya(self) -> bool:
        if _maya_available():
            return True
        self._log("This action needs a running Maya 2026.", "error")
        QtWidgets.QMessageBox.warning(
            self, "Snap-On Clothing",
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
            "joints and fit rig get built.")
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

    def _connect_test_body(self) -> None:
        if not self._require_maya():
            return
        from ..core import maya_testfit
        self._log("Connect test body…", "step")
        try:
            with _wait_cursor():
                result = maya_testfit.connect_test_body()
        except Exception as exc:  # noqa: BLE001 — surface the Maya error in the UI
            self._report(f"Connect test body failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Connect test body failed", str(exc))
            return
        self._report(result.summary(), "ok")
        self._log(
            "Pose the body's controls and watch the garment deform. "
            "Disconnect test body before publishing.", "info")

    def _disconnect_test_body(self) -> None:
        if not self._require_maya():
            return
        from ..core import maya_testfit
        self._log("Disconnect test body…", "step")
        try:
            with _wait_cursor():
                result = maya_testfit.disconnect_test_body()
        except Exception as exc:  # noqa: BLE001 — surface the Maya error in the UI
            self._report(f"Disconnect test body failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Disconnect test body failed", str(exc))
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

    def _scaffold(self) -> None:
        if not self._require_maya():
            return
        asset_type = self._require_type()
        if asset_type is None:
            return
        from ..core import maya_fitrig
        self._log(f"Scaffold fit rig ({asset_type})…", "step")
        try:
            with _wait_cursor():
                result = maya_fitrig.scaffold_fit_rig(asset_type)
        except Exception as exc:  # noqa: BLE001 — surface the Maya error in the UI
            self._report(f"Scaffold fit rig failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Scaffold fit rig failed", str(exc))
            return
        self._report(result.summary(), "ok")
        for warning in result.warnings:
            self._log(warning, "warn")
        if result.warnings:
            QtWidgets.QMessageBox.information(
                self, "Fit rig scaffolded",
                result.summary() + "\n\n" + "\n".join(result.warnings))

    def _capture(self) -> None:
        if not self._require_maya():
            return
        from ..core import maya_publish
        out = Path(tempfile.gettempdir()) / "snap_on_clothing_thumb.png"
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
        compat = tuple(
            t.strip() for t in self._compat.text().replace(";", ",").split(",")
            if t.strip())
        return _publish.PublishSpec(
            asset_name=name,
            asset_type=asset_type,
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

        paths = _publish.destination_paths(self._dest.text(), spec.asset_name)
        if paths.ma.exists():
            ok = QtWidgets.QMessageBox.question(
                self, "Overwrite?",
                f"'{paths.ma.name}' already exists in the library.\nOverwrite it?")
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

                maya_publish.save_ma(str(paths.ma))
                _publish.write_sidecar(paths, spec)
                report = _publish.validate_published_ma(paths.ma)
        except Exception as exc:  # noqa: BLE001
            self._report(f"Publish failed: {exc}", "error")
            QtWidgets.QMessageBox.critical(self, "Publish failed", str(exc))
            return

        if report.ok:
            self._report(
                f"Published {spec.asset_name} → {paths.folder} "
                f"({spec.tri_count:,} tris). {report.summary_line()}.", "ok")
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
