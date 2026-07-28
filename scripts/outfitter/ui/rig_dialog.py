"""Register rig dialog - turn the rig in the current scene into a registered rig.

The artist drops a new rig into a scene and opens this: it reads the scene
(:mod:`core.maya_rigs`), proposes an export-skeleton group, a body-variant switch and the
rig file to publish, and lets the artist correct every one of them before anything is
written. On OK it captures the profile, copies the rig ``.ma`` into the shared rig repo and
makes the new rig active.

Nothing here guesses silently: each proposal says where it came from, because a wrong
export group produces a garment skeleton that is subtly wrong rather than obviously broken.

Needs a running Maya (it reads the open scene). UI only - verified by ``py_compile``.
"""
from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtGui, QtWidgets

from ..core import rigs as _rigs

_NO_VARIANTS = "- single body (no variants) -"


class RegisterRigDialog(QtWidgets.QDialog):
    """Collect the facts needed to register the rig in the current scene."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Register rig")
        self.setModal(True)
        self.setMinimumWidth(560)
        self.result_summary: str = ""
        self._registered = None  # core.maya_rigs.RegisterResult once it succeeds

        from ..core import maya_rigs

        self._maya_rigs = maya_rigs
        self._candidates = maya_rigs.candidate_export_groups()
        self._switches = maya_rigs.detect_variant_switches()
        self._source = maya_rigs.rig_source_file()

        self._build_ui()
        self._prefill()

    # --- construction ---------------------------------------------------------
    def _build_ui(self) -> None:
        root = QtWidgets.QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        blurb = QtWidgets.QLabel(
            "Registering a rig captures its skeleton, works out which joints each garment "
            "type should skin to, and copies the rig file into the shared library so "
            "everyone can fetch it. The rig must be in this scene, at its bind pose.")
        blurb.setWordWrap(True)
        blurb.setObjectName("muted")
        root.addWidget(blurb)

        form = QtWidgets.QFormLayout()
        form.setLabelAlignment(QtCore.Qt.AlignRight)
        form.setHorizontalSpacing(10)
        form.setVerticalSpacing(8)
        form.setFieldGrowthPolicy(QtWidgets.QFormLayout.AllNonFixedFieldsGrow)

        self._name = QtWidgets.QLineEdit()
        self._name.setPlaceholderText("e.g. Acme Biped")
        self._name.textChanged.connect(self._sync_id)
        form.addRow("Rig name", self._name)

        self._id = QtWidgets.QLineEdit()
        self._id.setPlaceholderText("acme_biped")
        self._id.setToolTip(
            "Stored in every asset published for this rig. Keep it stable - changing it "
            "later orphans the assets already tagged with the old id.")
        form.addRow("Rig id", self._id)

        self._version = QtWidgets.QLineEdit()
        self._version.setPlaceholderText("e.g. v01")
        self._version.setToolTip(
            "The rig build this profile was captured from. Assets record which versions "
            "they fit.")
        form.addRow("Version", self._version)

        self._group = QtWidgets.QComboBox()
        self._group.setToolTip(
            "The group holding the skeleton a garment binds to. Everything below it is "
            "captured as the cloth_* skeleton.")
        for c in self._candidates:
            self._group.addItem(c.label, c.name)
        form.addRow("Export skeleton", self._group)

        self._switch = QtWidgets.QComboBox()
        self._switch.addItem(_NO_VARIANTS, None)
        for s in self._switches:
            self._switch.addItem(s.label, s)
        self._switch.currentIndexChanged.connect(self._refresh_mapping)
        form.addRow("Body variants", self._switch)

        mapping_row = QtWidgets.QHBoxLayout()
        self._mapping = QtWidgets.QLabel("")
        self._mapping.setObjectName("muted")
        self._swap = QtWidgets.QToolButton()
        self._swap.setText("Swap")
        self._swap.setToolTip(
            "Nothing in the rig says which end of the range is which body - if the male "
            "and female bodies come out the wrong way round, swap them.")
        self._swap.clicked.connect(self._do_swap)
        mapping_row.addWidget(self._mapping, 1)
        mapping_row.addWidget(self._swap, 0)
        form.addRow("", self._wrap(mapping_row))

        file_row = QtWidgets.QHBoxLayout()
        self._file = QtWidgets.QLineEdit()
        self._file.setPlaceholderText("(optional) the rig .ma to share")
        browse = QtWidgets.QToolButton()
        browse.setText("Browse…")
        browse.clicked.connect(self._browse)
        file_row.addWidget(self._file, 1)
        file_row.addWidget(browse, 0)
        form.addRow("Rig file", self._wrap(file_row))

        self._file_note = QtWidgets.QLabel("")
        self._file_note.setObjectName("muted")
        self._file_note.setWordWrap(True)
        form.addRow("", self._file_note)

        self._author = QtWidgets.QLineEdit()
        form.addRow("Registered by", self._author)

        root.addLayout(form)

        self._problem = QtWidgets.QLabel("")
        self._problem.setWordWrap(True)
        self._problem.setStyleSheet("color:#e06c75;")
        root.addWidget(self._problem)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.button(QtWidgets.QDialogButtonBox.Ok).setText("Register")
        buttons.accepted.connect(self._register)
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)

    @staticmethod
    def _wrap(layout: QtWidgets.QLayout) -> QtWidgets.QWidget:
        w = QtWidgets.QWidget()
        w.setLayout(layout)
        layout.setContentsMargins(0, 0, 0, 0)
        return w

    # --- prefill --------------------------------------------------------------
    def _prefill(self) -> None:
        if not self._candidates:
            self._problem.setText(
                "No export skeleton found in this scene - no group has a joint directly "
                "under it. Import the rig you want to register, then reopen this dialog.")
        self._low, self._high = "female", "male"
        self._switch.setCurrentIndex(1 if self._switches else 0)
        self._refresh_mapping()

        if self._source is not None:
            self._file.setText(str(self._source.path))
            self._file_note.setText(
                f"Taken from {self._source.label}. "
                + ("Confirm this is the rig itself and not the scene you imported it into."
                   if self._source.origin == "scene" else
                   "This is the file the rig was referenced from."))
        else:
            self._file_note.setText(
                "This scene isn't saved and the rig isn't referenced, so the rig file "
                "can't be worked out - browse to it, or register without one (the rig "
                "will have no test body to load).")

        from ..core import maya_rigs

        self._author.setText(maya_rigs._default_author())

    def _sync_id(self, text: str) -> None:
        """Keep the id in step with the name until the user edits the id themselves."""
        if not self._id.isModified():
            self._id.setText(_rigs.sanitize_rig_id(text))

    def _current_switch(self):
        return self._switch.currentData()

    def _refresh_mapping(self) -> None:
        switch = self._current_switch()
        enabled = switch is not None
        self._swap.setEnabled(enabled)
        if not enabled:
            self._mapping.setText("Assets for this rig won't carry a body variant.")
            return
        self._mapping.setText(
            f"{self._low} = {switch.minimum:g},  {self._high} = {switch.maximum:g}")

    def _do_swap(self) -> None:
        self._low, self._high = self._high, self._low
        self._refresh_mapping()

    def _browse(self) -> None:
        start = self._file.text().strip() or str(Path.home())
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Choose the rig file", start, "Maya scenes (*.ma *.mb)")
        if path:
            self._file.setText(path)
            self._file_note.setText("Chosen by hand.")

    # --- register -------------------------------------------------------------
    def _register(self) -> None:
        rig_id = _rigs.sanitize_rig_id(self._id.text() or self._name.text())
        display = self._name.text().strip() or rig_id
        version = self._version.text().strip()
        if not rig_id or not version:
            self._problem.setText("A rig id and a version are both required.")
            return
        if not self._candidates:
            self._problem.setText("There is no rig in this scene to register.")
            return

        existing = _rigs.find_profile(rig_id)
        if existing is not None and not self._confirm_overwrite(existing):
            return

        switch = self._current_switch()
        variants = (switch.as_variants(self._low, self._high) if switch is not None
                    else _rigs.Variants())
        source = self._file.text().strip() or None

        QtWidgets.QApplication.setOverrideCursor(QtGui.QCursor(QtCore.Qt.WaitCursor))
        try:
            result = self._maya_rigs.register_rig(
                rig_id, display, version, self._group.currentData(),
                variants=variants, author=self._author.text().strip(),
                rig_source=source)
        except Exception as exc:  # noqa: BLE001 - surface the failure in the dialog
            self._problem.setText(str(exc))
            return
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()

        self._registered = result
        self.result_summary = result.summary()
        self.accept()

    def _confirm_overwrite(self, existing) -> bool:
        answer = QtWidgets.QMessageBox.question(
            self, "Rig already registered",
            f"'{existing.rig_id}' is already registered as {existing.label}.\n\n"
            "Registering again replaces its profile - the captured skeleton, the skin "
            "sets and the variant switch - for everyone who syncs. Assets already "
            "published for this rig keep working, but they were built against the old "
            "skeleton.\n\nReplace it?")
        return answer == QtWidgets.QMessageBox.Yes

    @property
    def registered(self):
        """The :class:`core.maya_rigs.RegisterResult`, or ``None`` if nothing was written."""
        return self._registered
