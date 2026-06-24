"""PySide6 main window — clothing-asset browser + attach/detach.

The window scans the configured library roots and shows a filterable thumbnail
grid with a read-only detail panel (M1), plus an action bar that drives the real
``AttachEngine`` to attach the selected asset onto the GenHuman rig and detach a
live instance (M2).

Runs both inside Maya 2026 (parented to the main window, dockable-ready) and
standalone for dev preview (``python -m`` with PySide6 only — no Maya needed).
Maya is imported lazily, so a standalone launch still browses; only Attach/Detach
require a running Maya (they report this clearly if invoked standalone).
"""
from __future__ import annotations

import sys
from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from .. import __version__, config
from ..core import library
from ..core import settings as _settings
from ..core import sync as _sync
from ..core.asset import ClothingAsset
from . import style
from .publish_panel import PublishPanel

WINDOW_OBJECT_NAME = "snapOnClothingBrowser"
WINDOW_TITLE = "Outfitter"
_THUMB_SIZE = 120
_PREVIEW_MAX = 260
_ALL_TYPES = "All types"
_ALL_GENDERS = "All genders"

# Per-type badge colour (falls back to the theme accent for anything unlisted).
_TYPE_COLORS = {
    "shoes": "#c0795a", "pants": "#5a8fc0", "shirt": "#5ab0a0",
    "dress": "#b05a9a", "coat": "#9a7ac0", "hat": "#c0a85a",
}


def _rig_label(export_group: str) -> str:
    """Human-friendly name for a resolved rig: its namespace, or '(root)'."""
    short = export_group.rsplit("|", 1)[-1]
    return short.split(":", 1)[0] if ":" in short else "(root, no namespace)"


def _maya_main_window() -> QtWidgets.QWidget | None:
    """Return Maya's main window as a QWidget, or None when running standalone."""
    try:
        import maya.OpenMayaUI as omui  # type: ignore
        from shiboken6 import wrapInstance  # type: ignore
    except Exception:
        return None
    ptr = omui.MQtUtil.mainWindow()
    if ptr is None:
        return None
    return wrapInstance(int(ptr), QtWidgets.QWidget)


class _SyncWorker(QtCore.QObject):
    """Runs :func:`sync.sync_remote_to_local` off the UI thread.

    Lives on a worker ``QThread`` so a large first pull over a slow network share
    doesn't freeze Maya. Progress arrives on the pure sync's callback (worker
    thread) and is re-emitted as a queued Qt signal, so the slots run on the main
    thread. Per-file ``copying`` updates are throttled to ~one per percent so a
    library with thousands of files doesn't flood the event loop.
    """

    progressed = QtCore.Signal(object)   # core.sync.SyncProgress
    finished = QtCore.Signal(object)     # core.sync.SyncResult

    def __init__(self, remote, local):
        super().__init__()
        self._remote = remote
        self._local = local
        self._last_emitted = -1

    def _on_progress(self, p) -> None:
        if p.phase == "copying" and p.total > 0:
            step = max(1, p.total // 100)
            if p.done != p.total and p.done - self._last_emitted < step:
                return  # throttle mid-run; always let the final file through
            self._last_emitted = p.done
        self.progressed.emit(p)

    def run(self) -> None:
        try:
            result = _sync.sync_remote_to_local(
                self._remote, self._local, progress=self._on_progress)
        except Exception as exc:  # never let the worker die silently
            result = _sync.SyncResult()
            result.ok = False
            result.errors.append(str(exc))
        self.finished.emit(result)


class ClothingBrowser(QtWidgets.QMainWindow):
    """Read-only library browser: grid of assets + detail panel."""

    def __init__(self, roots: list[Path] | None = None, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setObjectName(WINDOW_OBJECT_NAME)
        self.setWindowTitle(f"{WINDOW_TITLE}  v{__version__}")
        # Comfortable default; the Publish tab now spreads its five steps across two
        # columns (steps 1–3 left, 4–5 + details right), so it no longer forces the
        # window unusually tall.
        self.resize(1040, 760)

        self._roots = roots
        self._scan: library.LibraryScanResult | None = None
        self._preview_pixmap: QtGui.QPixmap | None = None

        self.setStyleSheet(style.stylesheet())
        self._build_ui()
        self.refresh()

    # --- construction ---------------------------------------------------------
    def _build_ui(self) -> None:
        central = QtWidgets.QWidget()
        root = QtWidgets.QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        root.addWidget(self._build_header())

        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._build_library_tab(), "Library")
        tabs.addTab(PublishPanel(on_published=self.refresh), "Publish")
        tabs.addTab(self._build_setup_tab(), "Setup")
        root.addWidget(tabs, 1)
        self.setCentralWidget(central)

    def _build_header(self) -> QtWidgets.QWidget:
        """Branded header bar: 'Outfitter' wordmark with the version beside it."""
        bar = QtWidgets.QWidget()
        bar.setObjectName("appHeader")
        h = QtWidgets.QHBoxLayout(bar)
        h.setContentsMargins(16, 14, 16, 14)
        h.setSpacing(10)

        # Size/family/weight are set in QSS (#appName); a programmatic QFont here would
        # be overridden by the stylesheet's global "QWidget { font-size }" rule.
        name = QtWidgets.QLabel("Outfitter")
        name.setObjectName("appName")

        version = QtWidgets.QLabel(f"v{__version__}")
        version.setObjectName("appVersion")
        version.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        h.addWidget(name)
        h.addWidget(version)
        h.addStretch(1)
        return bar

    def _build_library_tab(self) -> QtWidgets.QWidget:
        central = QtWidgets.QWidget()
        outer = QtWidgets.QVBoxLayout(central)
        outer.setContentsMargins(8, 8, 8, 8)

        # top bar: gender filter + type filter + search + refresh
        top = QtWidgets.QHBoxLayout()
        self._gender_combo = QtWidgets.QComboBox()
        self._gender_combo.addItem(_ALL_GENDERS)
        self._gender_combo.addItems(list(config.GENDERS))
        self._gender_combo.currentIndexChanged.connect(self._apply_filter)
        self._type_combo = QtWidgets.QComboBox()
        self._type_combo.addItem(_ALL_TYPES)
        self._type_combo.addItems(list(config.ASSET_TYPES))
        self._type_combo.currentIndexChanged.connect(self._apply_filter)
        self._search = QtWidgets.QLineEdit()
        self._search.setPlaceholderText("Search assets…")
        self._search.setClearButtonEnabled(True)
        self._search.textChanged.connect(self._apply_filter)
        self._refresh_btn = QtWidgets.QPushButton("Refresh")
        self._refresh_btn.clicked.connect(self.refresh)
        top.addWidget(QtWidgets.QLabel("Gender:"))
        top.addWidget(self._gender_combo)
        top.addWidget(QtWidgets.QLabel("Type:"))
        top.addWidget(self._type_combo)
        top.addWidget(self._search, 1)
        top.addWidget(self._refresh_btn)
        outer.addLayout(top)

        # splitter: grid | detail
        splitter = QtWidgets.QSplitter(QtCore.Qt.Horizontal)
        self._grid = QtWidgets.QListWidget()
        self._grid.setViewMode(QtWidgets.QListWidget.IconMode)
        self._grid.setIconSize(QtCore.QSize(_THUMB_SIZE, _THUMB_SIZE))
        self._grid.setResizeMode(QtWidgets.QListWidget.Adjust)
        self._grid.setSpacing(10)
        self._grid.setMovement(QtWidgets.QListWidget.Static)
        self._grid.setUniformItemSizes(True)
        self._grid.currentItemChanged.connect(self._on_selection)
        splitter.addWidget(self._grid)
        splitter.addWidget(self._build_detail_panel())
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)
        outer.addWidget(splitter, 1)

        # action bar: attach the selected asset (left) / detach a live instance (right).
        actions = QtWidgets.QHBoxLayout()
        self._attach_btn = QtWidgets.QPushButton("Attach ▸")
        self._attach_btn.setProperty("positive", True)
        self._attach_btn.clicked.connect(self._attach_selected)
        actions.addWidget(self._attach_btn)
        actions.addStretch(1)
        actions.addWidget(QtWidgets.QLabel("Attached:"))
        self._attached_combo = QtWidgets.QComboBox()
        self._attached_combo.setMinimumWidth(150)
        actions.addWidget(self._attached_combo)
        self._detach_btn = QtWidgets.QPushButton("Detach")
        self._detach_btn.clicked.connect(self._detach_selected)
        actions.addWidget(self._detach_btn)
        outer.addLayout(actions)

        self._status = QtWidgets.QLabel()
        self._status.setStyleSheet("color: gray;")
        outer.addWidget(self._status)
        self._refresh_attached()
        return central

    # --- setup tab ------------------------------------------------------------
    def _build_setup_tab(self) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(w)
        v.setContentsMargins(8, 8, 8, 8)

        intro = QtWidgets.QLabel(
            "Set two library folders. You work from the local folder — the tool "
            "scans only that. The remote folder is a shared master library; press "
            "Sync to pull new and changed assets down into your local folder."
        )
        intro.setWordWrap(True)
        v.addWidget(intro)

        form = QtWidgets.QFormLayout()
        self._local_field, local_row = self._make_folder_row(self._choose_local)
        self._remote_field, remote_row = self._make_folder_row(self._choose_remote)
        form.addRow("Local (working):", local_row)
        form.addRow("Remote (master):", remote_row)
        v.addLayout(form)

        sync_row = QtWidgets.QHBoxLayout()
        self._sync_btn = QtWidgets.QPushButton("Sync from remote  ↓")
        self._sync_btn.clicked.connect(self._sync_now)
        sync_row.addWidget(self._sync_btn)
        self._sync_status = QtWidgets.QLabel("")
        self._sync_status.setWordWrap(True)
        self._sync_status.setStyleSheet("color: gray;")
        sync_row.addWidget(self._sync_status, 1)
        v.addLayout(sync_row)

        self._sync_progress = QtWidgets.QProgressBar()
        self._sync_progress.setTextVisible(True)
        self._sync_progress.hide()  # shown only while a sync runs
        v.addWidget(self._sync_progress)
        # Worker thread handles for an in-flight sync (None when idle).
        self._sync_thread: QtCore.QThread | None = None
        self._sync_worker: _SyncWorker | None = None

        v.addStretch(1)
        note = QtWidgets.QLabel(
            "Sync copies new and changed assets from the remote into the local "
            "folder. It never deletes — assets you authored locally are always kept. "
            "Leave the local folder unset to fall back to the default library."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: gray;")
        v.addWidget(note)

        self._reload_setup_fields()
        return w

    def _make_folder_row(self, on_browse) -> tuple[QtWidgets.QLabel, QtWidgets.QWidget]:
        row = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout(row)
        h.setContentsMargins(0, 0, 0, 0)
        field = QtWidgets.QLabel()
        field.setWordWrap(True)
        field.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        browse = QtWidgets.QPushButton("Browse…")
        browse.clicked.connect(lambda: on_browse(set_to=True))
        clear = QtWidgets.QPushButton("Clear")
        clear.clicked.connect(lambda: on_browse(set_to=False))
        h.addWidget(field, 1)
        h.addWidget(browse)
        h.addWidget(clear)
        return field, row

    def _reload_setup_fields(self) -> None:
        loc = _settings.read_locations()
        self._set_field_path(self._local_field, loc.local)
        self._set_field_path(self._remote_field, loc.remote)
        # Stay disabled while a sync is in flight (re-enabled in _on_sync_finished).
        syncing = self._sync_thread is not None
        self._sync_btn.setEnabled(
            not syncing and loc.local is not None and loc.remote is not None)

    def _set_field_path(self, field: QtWidgets.QLabel, path: Path | None) -> None:
        if path is None:
            field.setText("(not set)")
            field.setStyleSheet("color: gray; font-style: italic;")
            return
        missing = not Path(path).is_dir()
        field.setText(str(path) + ("   (missing)" if missing else ""))
        field.setStyleSheet("color: #c0392b;" if missing else "")

    def _after_locations_changed(self) -> None:
        self._roots = None  # the saved path file now drives the scan
        self._reload_setup_fields()
        self.refresh()

    def _choose_local(self, set_to: bool) -> None:
        if set_to:
            folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose local working folder")
            if not folder:
                return
            _settings.set_local(folder)
        else:
            _settings.set_local(None)
        self._after_locations_changed()

    def _choose_remote(self, set_to: bool) -> None:
        if set_to:
            folder = QtWidgets.QFileDialog.getExistingDirectory(self, "Choose remote master folder")
            if not folder:
                return
            _settings.set_remote(folder)
        else:
            _settings.set_remote(None)
        self._reload_setup_fields()  # remote isn't scanned — no library refresh needed

    def _sync_now(self) -> None:
        if self._sync_thread is not None:
            return  # a sync is already running
        loc = _settings.read_locations()
        if loc.local is None or loc.remote is None:
            self._sync_status.setText("Set both a local and a remote folder first.")
            return

        self._sync_btn.setEnabled(False)
        self._sync_status.setText("Scanning remote…")
        self._sync_status.setStyleSheet("color: gray;")
        self._sync_progress.setRange(0, 0)  # indeterminate until the scan finishes
        self._sync_progress.setFormat("")
        self._sync_progress.show()

        self._sync_thread = QtCore.QThread(self)
        self._sync_worker = _SyncWorker(loc.remote, loc.local)
        self._sync_worker.moveToThread(self._sync_thread)
        self._sync_thread.started.connect(self._sync_worker.run)
        self._sync_worker.progressed.connect(self._on_sync_progress)
        self._sync_worker.finished.connect(self._on_sync_finished)
        self._sync_thread.start()

    def _on_sync_progress(self, progress) -> None:
        if progress.phase == "scanning":
            self._sync_progress.setRange(0, 0)  # busy/indeterminate
            self._sync_status.setText("Scanning remote…")
        elif progress.phase == "copying" and progress.total > 0:
            self._sync_progress.setRange(0, progress.total)
            self._sync_progress.setValue(progress.done)
            self._sync_progress.setFormat(f"%v / %m  (%p%)")
            self._sync_status.setText(f"Copying {progress.done} of {progress.total}…")

    def _on_sync_finished(self, result) -> None:
        thread = self._sync_thread
        if thread is not None:
            thread.quit()
            thread.wait()
        if self._sync_worker is not None:
            self._sync_worker.deleteLater()
        if thread is not None:
            thread.deleteLater()
        self._sync_thread = None
        self._sync_worker = None

        self._sync_progress.hide()
        self._sync_btn.setEnabled(True)
        self._sync_status.setText(result.summary())
        self._sync_status.setStyleSheet("color: #c0392b;" if not result.ok or result.errors
                                        else "color: gray;")
        if result.changed:
            self._after_locations_changed()  # surface freshly pulled assets

    def _build_detail_panel(self) -> QtWidgets.QWidget:
        panel = QtWidgets.QWidget()
        v = QtWidgets.QVBoxLayout(panel)
        v.setContentsMargins(12, 8, 8, 8)
        v.setSpacing(8)

        # --- preview image ----------------------------------------------------
        self._preview = QtWidgets.QLabel()
        self._preview.setObjectName("previewImage")
        self._preview.setAlignment(QtCore.Qt.AlignCenter)
        self._preview.setMinimumHeight(200)
        self._preview.setMaximumHeight(_PREVIEW_MAX)
        self._preview.setSizePolicy(
            QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        v.addWidget(self._preview)

        # --- name + type badge ------------------------------------------------
        header = QtWidgets.QHBoxLayout()
        self._d_name = QtWidgets.QLabel("—")
        self._d_name.setObjectName("assetName")
        self._d_name.setWordWrap(True)
        self._d_badge = QtWidgets.QLabel("")
        self._d_badge.setObjectName("typeBadge")
        self._d_badge.setAlignment(QtCore.Qt.AlignCenter)
        header.addWidget(self._d_name, 1)
        header.addWidget(self._d_badge, 0, QtCore.Qt.AlignTop)
        v.addLayout(header)

        # --- description ------------------------------------------------------
        self._d_desc = QtWidgets.QLabel("")
        self._d_desc.setObjectName("description")
        self._d_desc.setWordWrap(True)
        v.addWidget(self._d_desc)

        v.addWidget(self._hline())

        # --- metadata grid ----------------------------------------------------
        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignRight)
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(6)
        self._d_gender = self._value_label()
        self._d_version = self._value_label()
        self._d_compat = self._value_label()
        self._d_polys = self._value_label()
        self._d_created = self._value_label()
        self._d_rigver = self._value_label()
        self._d_author = self._value_label()
        self._d_source = self._value_label()
        for caption, widget in (
            ("Gender", self._d_gender),
            ("Version", self._d_version),
            ("GenHuman compat", self._d_compat),
            ("Polycount", self._d_polys),
            ("Created", self._d_created),
            ("Rig version", self._d_rigver),
            ("Author", self._d_author),
            ("Source", self._d_source),
        ):
            form.addRow(self._field_caption(caption), widget)
        v.addLayout(form)

        # --- compact file row (elided, never widens the panel) ----------------
        v.addWidget(self._hline())
        path_row = QtWidgets.QHBoxLayout()
        path_row.setSpacing(4)
        self._d_path = QtWidgets.QLabel("—")
        self._d_path.setObjectName("muted")
        self._d_path.setMinimumWidth(0)
        self._d_path.setSizePolicy(
            QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Preferred)
        self._copy_btn = QtWidgets.QToolButton()
        self._copy_btn.setText("Copy")
        self._copy_btn.clicked.connect(self._copy_path)
        self._open_btn = QtWidgets.QToolButton()
        self._open_btn.setText("Open ▸")
        self._open_btn.clicked.connect(self._open_folder)
        path_row.addWidget(self._d_path, 1)
        path_row.addWidget(self._copy_btn)
        path_row.addWidget(self._open_btn)
        v.addLayout(path_row)

        # --- issues (invalid assets) ------------------------------------------
        self._d_errors = QtWidgets.QLabel("")
        self._d_errors.setWordWrap(True)
        self._d_errors.setStyleSheet("color: #e06c5a;")
        v.addWidget(self._d_errors)

        v.addStretch(1)
        return panel

    def _hline(self) -> QtWidgets.QFrame:
        line = QtWidgets.QFrame()
        line.setFrameShape(QtWidgets.QFrame.HLine)
        line.setStyleSheet("color: #1d1d1f; background: #1d1d1f; max-height: 1px;")
        return line

    def _field_caption(self, text: str) -> QtWidgets.QLabel:
        lbl = QtWidgets.QLabel(text)
        lbl.setObjectName("fieldLabel")
        return lbl

    def _value_label(self) -> QtWidgets.QLabel:
        lbl = QtWidgets.QLabel("—")
        lbl.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        return lbl

    # --- data -----------------------------------------------------------------
    def _effective_roots(self) -> list[Path]:
        """Explicit roots if the caller passed any, else the user's saved roots."""
        if self._roots is not None:
            return self._roots
        return _settings.effective_library_roots()

    def refresh(self) -> None:
        self._scan = library.scan_library(self._effective_roots())
        self._apply_filter()

    def _apply_filter(self) -> None:
        if self._scan is None:
            return
        wanted_type = self._type_combo.currentText()
        wanted_gender = self._gender_combo.currentText()
        query = self._search.text().strip().lower()

        self._grid.blockSignals(True)
        self._grid.clear()
        shown = 0
        for asset in self._scan.assets:
            if wanted_gender != _ALL_GENDERS and asset.gender != wanted_gender:
                continue
            if wanted_type != _ALL_TYPES and asset.asset_type != wanted_type:
                continue
            if query and query not in asset.display_name.lower():
                continue
            self._grid.addItem(self._make_item(asset))
            shown += 1
        self._grid.blockSignals(False)

        if self._grid.count():
            self._grid.setCurrentRow(0)
        else:
            self._clear_detail()

        total = len(self._scan.assets)
        invalid = len(self._scan.invalid)
        roots = ", ".join(str(r) for r in self._scan.scanned_roots) or "(no readable roots)"
        suffix = f" · {invalid} invalid" if invalid else ""
        self._status.setText(f"Showing {shown}/{total} assets{suffix}  —  roots: {roots}")

    def _make_item(self, asset: ClothingAsset) -> QtWidgets.QListWidgetItem:
        label = asset.display_name if asset.is_valid else f"⚠ {asset.display_name}"
        item = QtWidgets.QListWidgetItem(self._icon_for(asset), label)
        item.setData(QtCore.Qt.UserRole, asset)
        item.setSizeHint(QtCore.QSize(_THUMB_SIZE + 28, _THUMB_SIZE + 36))
        tip = asset.asset_type if asset.is_valid else "; ".join(asset.errors)
        item.setToolTip(f"{asset.ma_path}\n{tip}")
        if not asset.is_valid:
            item.setForeground(QtGui.QColor("#c0392b"))
        return item

    def _icon_for(self, asset: ClothingAsset) -> QtGui.QIcon:
        if asset.thumbnail is not None and asset.thumbnail.is_file():
            pm = QtGui.QPixmap(str(asset.thumbnail))
            if not pm.isNull():
                return QtGui.QIcon(pm)
        return self._placeholder_icon(asset)

    def _placeholder_icon(self, asset: ClothingAsset) -> QtGui.QIcon:
        pm = QtGui.QPixmap(_THUMB_SIZE, _THUMB_SIZE)
        pm.fill(QtGui.QColor("#3a3a3a") if asset.is_valid else QtGui.QColor("#5a2a2a"))
        painter = QtGui.QPainter(pm)
        painter.setPen(QtGui.QColor("#bbbbbb"))
        painter.drawText(pm.rect(), QtCore.Qt.AlignCenter, asset.asset_type[:6])
        painter.end()
        return QtGui.QIcon(pm)

    # --- selection / detail ---------------------------------------------------
    def _on_selection(self, current: QtWidgets.QListWidgetItem | None, _prev=None) -> None:
        if current is None:
            self._clear_detail()
            return
        asset: ClothingAsset = current.data(QtCore.Qt.UserRole)
        self._current_asset = asset
        meta = asset.metadata

        self._set_preview(asset)
        self._d_name.setText(asset.display_name)
        self._set_badge(asset.asset_type if asset.is_valid else "invalid")
        self._d_desc.setText((meta.notes if meta and meta.notes else ""))
        self._d_desc.setVisible(bool(meta and meta.notes))

        self._d_gender.setText((meta.gender or "—") if meta else "—")
        self._d_version.setText(meta.cloth_version if meta else "—")
        self._d_compat.setText(", ".join(meta.genhuman_compat) if meta and meta.genhuman_compat else "—")
        self._d_polys.setText(self._poly_text(meta))
        self._d_created.setText((meta.created or "—") if meta else "—")
        self._d_rigver.setText((meta.rig_version or "—") if meta else "—")
        self._d_author.setText((meta.author or "—") if meta else "—")
        self._d_source.setText(asset.source)

        self._set_path(asset.ma_path)
        self._d_errors.setText("; ".join(asset.errors))
        self._d_errors.setVisible(bool(asset.errors))

    @staticmethod
    def _poly_text(meta) -> str:
        if meta is None or (meta.tri_count is None and meta.vert_count is None):
            return "—"
        parts = []
        if meta.tri_count is not None:
            parts.append(f"{meta.tri_count:,} tris")
        if meta.vert_count is not None:
            parts.append(f"{meta.vert_count:,} verts")
        return " · ".join(parts)

    def _set_badge(self, asset_type: str) -> None:
        self._d_badge.setText(asset_type.upper())
        color = _TYPE_COLORS.get(asset_type, "#4a90d9")
        self._d_badge.setStyleSheet(
            f"background: {color}; color: #ffffff; border-radius: 9px;"
            "padding: 2px 10px; font-size: 11px; font-weight: 600;")

    def _set_preview(self, asset: ClothingAsset) -> None:
        pm = None
        if asset.thumbnail is not None and asset.thumbnail.is_file():
            loaded = QtGui.QPixmap(str(asset.thumbnail))
            if not loaded.isNull():
                pm = loaded
        self._preview_pixmap = pm
        self._rescale_preview()

    def _rescale_preview(self) -> None:
        if not hasattr(self, "_preview"):  # resize() can fire before the panel exists
            return
        if self._preview_pixmap is None:
            self._preview.setText("no preview")
            self._preview.setPixmap(QtGui.QPixmap())
            return
        target = self._preview.size()
        if target.width() < 2 or target.height() < 2:
            return
        self._preview.setPixmap(self._preview_pixmap.scaled(
            target, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation))

    def _set_path(self, path: Path) -> None:
        text = str(path)
        metrics = QtGui.QFontMetrics(self._d_path.font())
        avail = max(60, self._d_path.width() - 4)
        self._d_path.setText(metrics.elidedText(text, QtCore.Qt.ElideMiddle, avail))
        self._d_path.setToolTip(text)

    def _copy_path(self) -> None:
        asset = getattr(self, "_current_asset", None)
        if asset is not None:
            QtWidgets.QApplication.clipboard().setText(str(asset.ma_path))
            self._status.setText(f"Copied path: {asset.ma_path}")

    def _open_folder(self) -> None:
        asset = getattr(self, "_current_asset", None)
        if asset is None:
            return
        folder = Path(asset.ma_path).parent
        QtGui.QDesktopServices.openUrl(QtCore.QUrl.fromLocalFile(str(folder)))

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        self._rescale_preview()
        asset = getattr(self, "_current_asset", None)
        if asset is not None and hasattr(self, "_d_path"):
            self._set_path(asset.ma_path)

    def _clear_detail(self) -> None:
        self._current_asset = None
        self._preview_pixmap = None
        self._rescale_preview()
        self._d_name.setText("—")
        self._d_badge.setText("")
        self._d_badge.setStyleSheet("")
        self._d_desc.setText("")
        self._d_desc.setVisible(False)
        for lbl in (self._d_gender, self._d_version, self._d_compat, self._d_polys,
                    self._d_created, self._d_rigver, self._d_author, self._d_source):
            lbl.setText("—")
        self._d_path.setText("—")
        self._d_path.setToolTip("")
        self._d_errors.setText("")
        self._d_errors.setVisible(False)

    # --- attach / detach ------------------------------------------------------
    def _selected_asset(self) -> ClothingAsset | None:
        item = self._grid.currentItem()
        return item.data(QtCore.Qt.UserRole) if item is not None else None

    def _attach_selected(self) -> None:
        asset = self._selected_asset()
        if asset is None:
            QtWidgets.QMessageBox.information(self, WINDOW_TITLE, "Select an asset to attach.")
            return
        if not asset.is_valid:
            QtWidgets.QMessageBox.warning(
                self, WINDOW_TITLE,
                "This asset failed validation and can't be attached:\n\n"
                + "\n".join(asset.errors))
            return
        engine = _ensure_engine(self)
        if engine is None:
            return

        # Multi-rig: the user selects any node of the target rig; we resolve that
        # rig's export-skeleton group from the selection's namespace. With nothing
        # selected we fall back to a root-level rig (single-rig / no-namespace case).
        export_group = config.EXPORT_SKELETON_GROUP
        rig_label = "root-level rig"
        selection = engine.scene.selected_nodes()
        if selection:
            resolved = engine.scene.resolve_export_group(selection[0])
            if resolved is not None:
                export_group = resolved
                rig_label = _rig_label(resolved)

        from ..core.attach import sanitize_namespace
        suggested = sanitize_namespace(asset.asset_type or asset.display_name)
        namespace, ok = QtWidgets.QInputDialog.getText(
            self, "Attach clothing",
            f"Target rig: {rig_label}\n\n"
            "Instance name (namespace) — use a unique name per garment:",
            text=suggested)
        if not ok or not namespace.strip():
            return

        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            result = engine.attach(asset, namespace, export_group=export_group)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        if result.ok and result.instance is not None:
            self._status.setText(
                f"Attached '{result.instance.namespace}' — {asset.display_name} "
                f"({len(result.instance.connections)} connection(s)).")
            self._refresh_attached(select=result.instance.namespace)
        else:
            QtWidgets.QMessageBox.critical(
                self, "Attach failed",
                "Attach was rejected — the scene is unchanged:\n\n"
                + "\n".join(str(i) for i in result.report.errors))

    def _detach_selected(self) -> None:
        namespace = self._attached_combo.currentText()
        if not namespace:
            return
        engine = _ensure_engine(self)
        if engine is None:
            return

        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            result = engine.detach(namespace)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        if result.ok:
            self._status.setText(
                f"Detached '{namespace}' — broke {result.broken} connection(s).")
            self._refresh_attached()
        else:
            QtWidgets.QMessageBox.critical(
                self, "Detach failed",
                "\n".join(str(i) for i in result.report.errors))

    def _refresh_attached(self, select: str | None = None) -> None:
        """Repopulate the attached-instance dropdown from the live registry."""
        engine = _existing_engine()
        names = engine.registry.namespaces() if engine is not None else []
        self._attached_combo.blockSignals(True)
        self._attached_combo.clear()
        self._attached_combo.addItems(names)
        if select and select in names:
            self._attached_combo.setCurrentText(select)
        self._attached_combo.blockSignals(False)
        self._detach_btn.setEnabled(bool(names))


_window_singleton: ClothingBrowser | None = None

# The attach engine carries the in-session registry of what's currently attached
# (which connections each instance made), so detach can break exactly those edges.
# It lives at module scope, not on the window, so reopening the browser within the
# same Maya session keeps the attached-instance list intact.
_engine_singleton = None  # type: ignore[var-annotated]  # core.attach.AttachEngine | None


def _existing_engine():
    """Return the live engine if one was already created this session, else None.

    Never constructs one (so opening the browser standalone — no Maya — and just
    browsing doesn't trip the ``maya.cmds`` import). Used to populate the UI.
    """
    return _engine_singleton


def _ensure_engine(parent: QtWidgets.QWidget):
    """Get-or-create the attach engine; show a message and return None outside Maya."""
    global _engine_singleton
    if _engine_singleton is None:
        try:
            from ..core.attach import AttachEngine
            from ..core.scene import MayaScene
            _engine_singleton = AttachEngine(MayaScene())
        except Exception as exc:  # noqa: BLE001 — no Maya / cmds unavailable
            QtWidgets.QMessageBox.warning(
                parent, WINDOW_TITLE,
                "Attach and Detach must run inside Maya 2026 (they need a live "
                "scene and the GenHuman rig).\n\nDetails: " + str(exc))
            return None
    return _engine_singleton


def _delete_existing_windows() -> None:
    """Close every prior browser instance found in the live Qt tree, by objectName.

    The module-level ``_window_singleton`` is the fast path, but the shelf button purges
    all ``outfitter`` modules on each click (to hot-reload code), which resets that
    global to ``None`` and orphans the previous window — leaving it parented to Maya and
    visible. Sweeping top-level widgets by :data:`WINDOW_OBJECT_NAME` survives the reload,
    so repeated clicks replace the window instead of stacking new ones.
    """
    app = QtWidgets.QApplication.instance()
    if app is None:
        return
    for w in app.topLevelWidgets():
        try:
            if w.objectName() == WINDOW_OBJECT_NAME:
                w.close()
                w.deleteLater()
        except RuntimeError:
            # already-deleted C++ object — ignore
            pass


def show(roots: list[Path] | None = None) -> ClothingBrowser:
    """Create (or re-show) the browser. Inside Maya, parents to the main window."""
    global _window_singleton
    _window_singleton = None
    _delete_existing_windows()

    parent = _maya_main_window()
    _window_singleton = ClothingBrowser(roots=roots, parent=parent)
    # Keep the tool above Maya. On Windows a parented top-level already stacks
    # above the main window with the plain Qt.Window flag. On macOS (Cocoa) that
    # same window falls *behind* Maya whenever Maya takes focus, so use Qt.Tool
    # instead — a utility window that floats above its parent without pinning
    # itself over every other app the way WindowStaysOnTopHint would.
    if sys.platform == "darwin" and parent is not None:
        _window_singleton.setWindowFlag(QtCore.Qt.Tool, True)
    else:
        _window_singleton.setWindowFlag(QtCore.Qt.Window, True)
    _window_singleton.show()
    _window_singleton.raise_()
    return _window_singleton
