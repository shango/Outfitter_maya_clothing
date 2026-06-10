"""PySide6 main window — clothing-asset browser + attach/detach.

The window scans the configured library roots and shows a filterable thumbnail
grid with a read-only detail panel (M1), plus an action bar that drives the real
``AttachEngine`` to attach the selected asset onto the GenHuman rig and detach a
live instance (M2). Fit-control sliders (M3) live in ``controls_panel`` and are
not wired here yet.

Runs both inside Maya 2026 (parented to the main window, dockable-ready) and
standalone for dev preview (``python -m`` with PySide6 only — no Maya needed).
Maya is imported lazily, so a standalone launch still browses; only Attach/Detach
require a running Maya (they report this clearly if invoked standalone).
"""
from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from .. import config
from ..core import library
from ..core import settings as _settings
from ..core import sync as _sync
from ..core.asset import ClothingAsset

WINDOW_OBJECT_NAME = "snapOnClothingBrowser"
WINDOW_TITLE = "Snap-On Clothing"
_THUMB_SIZE = 96
_ALL_TYPES = "All types"


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


class ClothingBrowser(QtWidgets.QMainWindow):
    """Read-only library browser: grid of assets + detail panel."""

    def __init__(self, roots: list[Path] | None = None, parent: QtWidgets.QWidget | None = None):
        super().__init__(parent)
        self.setObjectName(WINDOW_OBJECT_NAME)
        self.setWindowTitle(WINDOW_TITLE)
        self.resize(820, 560)

        self._roots = roots
        self._scan: library.LibraryScanResult | None = None

        self._build_ui()
        self.refresh()

    # --- construction ---------------------------------------------------------
    def _build_ui(self) -> None:
        tabs = QtWidgets.QTabWidget(self)
        self.setCentralWidget(tabs)
        tabs.addTab(self._build_library_tab(), "Library")
        tabs.addTab(self._build_setup_tab(), "Setup")

    def _build_library_tab(self) -> QtWidgets.QWidget:
        central = QtWidgets.QWidget()
        outer = QtWidgets.QVBoxLayout(central)
        outer.setContentsMargins(8, 8, 8, 8)

        # top bar: type filter + search + refresh
        top = QtWidgets.QHBoxLayout()
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

        # action bar: attach the selected asset / detach a live instance
        actions = QtWidgets.QHBoxLayout()
        self._attach_btn = QtWidgets.QPushButton("Attach ▸")
        self._attach_btn.setToolTip("Import the selected asset and connect it to the GenHuman rig")
        self._attach_btn.clicked.connect(self._attach_selected)
        actions.addWidget(self._attach_btn)
        actions.addStretch(1)
        actions.addWidget(QtWidgets.QLabel("Attached:"))
        self._attached_combo = QtWidgets.QComboBox()
        self._attached_combo.setMinimumWidth(150)
        actions.addWidget(self._attached_combo)
        self._detach_btn = QtWidgets.QPushButton("Detach")
        self._detach_btn.setToolTip("Break this instance's connections and remove its namespace")
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
        self._sync_btn.setEnabled(loc.local is not None and loc.remote is not None)

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
        loc = _settings.read_locations()
        if loc.local is None or loc.remote is None:
            self._sync_status.setText("Set both a local and a remote folder first.")
            return
        self._sync_status.setText("Syncing…")
        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            result = _sync.sync_remote_to_local(loc.remote, loc.local)
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        self._sync_status.setText(result.summary())
        self._sync_status.setStyleSheet("color: #c0392b;" if not result.ok or result.errors
                                        else "color: gray;")
        if result.changed:
            self._after_locations_changed()  # surface freshly pulled assets

    def _build_detail_panel(self) -> QtWidgets.QWidget:
        panel = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(panel)
        form.setLabelAlignment(QtCore.Qt.AlignRight)
        self._d_name = QtWidgets.QLabel("—")
        self._d_name.setStyleSheet("font-weight: bold;")
        self._d_type = QtWidgets.QLabel("—")
        self._d_version = QtWidgets.QLabel("—")
        self._d_compat = QtWidgets.QLabel("—")
        self._d_author = QtWidgets.QLabel("—")
        self._d_source = QtWidgets.QLabel("—")
        self._d_path = QtWidgets.QLabel("—")
        self._d_path.setWordWrap(True)
        self._d_path.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        self._d_errors = QtWidgets.QLabel("")
        self._d_errors.setWordWrap(True)
        self._d_errors.setStyleSheet("color: #c0392b;")
        form.addRow("Name:", self._d_name)
        form.addRow("Type:", self._d_type)
        form.addRow("Version:", self._d_version)
        form.addRow("GenHuman compat:", self._d_compat)
        form.addRow("Author:", self._d_author)
        form.addRow("Metadata source:", self._d_source)
        form.addRow("File:", self._d_path)
        form.addRow("Issues:", self._d_errors)
        return panel

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
        query = self._search.text().strip().lower()

        self._grid.blockSignals(True)
        self._grid.clear()
        shown = 0
        for asset in self._scan.assets:
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
        meta = asset.metadata
        self._d_name.setText(asset.display_name)
        self._d_type.setText(asset.asset_type)
        self._d_version.setText(meta.cloth_version if meta else "—")
        self._d_compat.setText(", ".join(meta.genhuman_compat) if meta else "—")
        self._d_author.setText((meta.author or "—") if meta else "—")
        self._d_source.setText(asset.source)
        self._d_path.setText(str(asset.ma_path))
        self._d_errors.setText("; ".join(asset.errors))

    def _clear_detail(self) -> None:
        for lbl in (self._d_name, self._d_type, self._d_version, self._d_compat,
                    self._d_author, self._d_source, self._d_path):
            lbl.setText("—")
        self._d_errors.setText("")

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


def show(roots: list[Path] | None = None) -> ClothingBrowser:
    """Create (or re-show) the browser. Inside Maya, parents to the main window."""
    global _window_singleton
    if _window_singleton is not None:
        try:
            _window_singleton.close()
            _window_singleton.deleteLater()
        except RuntimeError:
            pass
        _window_singleton = None

    parent = _maya_main_window()
    _window_singleton = ClothingBrowser(roots=roots, parent=parent)
    _window_singleton.setWindowFlag(QtCore.Qt.Window, True)
    _window_singleton.show()
    _window_singleton.raise_()
    return _window_singleton
