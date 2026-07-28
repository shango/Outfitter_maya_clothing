"""Rig selector - the "which rig am I working with?" control, shared by both tabs.

Every rig-aware action starts with this question: the Publish tab authors *for* a rig, the
Library tab dresses *a* rig and filters clothing to it. Both use this widget so the answer
is one thing in one place, persisted to the settings file
(:func:`core.settings.set_rig`) and therefore the same after a restart.

It also owns the rig **body**, because that is where the cost lives. Rig ``.ma`` files are
25-30 MB and deliberately excluded from Sync (see :mod:`core.rigs`), so the widget shows
where the body currently is - bundled, downloaded, or still only on the shared library -
and offers an explicit *Fetch rig* button. Choosing a rig in the dropdown is always free;
nothing is ever downloaded until someone asks for it.

UI only - verified by ``py_compile`` (PySide6 ships with Maya 2026, not the headless
test env).
"""
from __future__ import annotations

from pathlib import Path
from typing import Callable

from PySide6 import QtCore, QtWidgets

from ..core import rigs as _rigs
from ..core import settings as _settings

_MB = 1024 * 1024


def _size_text(nbytes: int) -> str:
    if nbytes <= 0:
        return ""
    return f" ({nbytes / _MB:.0f} MB)" if nbytes >= _MB else f" ({nbytes / 1024:.0f} KB)"


class _FetchWorker(QtCore.QObject):
    """Copies one rig body down from the shared library, off the UI thread.

    A 30 MB copy over a studio share takes long enough to freeze Maya's event loop, so it
    runs on a worker ``QThread``; byte progress arrives on the pure copy's callback (worker
    thread) and is re-emitted as a queued signal so the slots run on the main thread.
    """

    progressed = QtCore.Signal(int, int)  # copied bytes, total bytes
    finished = QtCore.Signal(object, str)  # local Path (or None), error message

    def __init__(self, profile, local, remote, variant: str = ""):
        super().__init__()
        self._profile = profile
        self._local = local
        self._remote = remote
        self._variant = variant

    def run(self) -> None:
        try:
            path = _rigs.ensure_rig_file(
                self._profile, self._local, self._remote, self._variant,
                progress=lambda done, total: self.progressed.emit(done, total))
        except Exception as exc:  # noqa: BLE001 - never let the worker die silently
            self.finished.emit(None, str(exc))
            return
        self.finished.emit(path, "")


def fetch_rig_file(parent: QtWidgets.QWidget, profile, variant: str = "",
                   on_done: Callable[[Path | None, str], None] | None = None) -> None:
    """Fetch ``profile``'s body from the shared library, with a cancellable progress dialog.

    Returns immediately - ``on_done(path, error)`` fires on the UI thread when the copy
    finishes, is cancelled (both ``None`` path), or fails. Callers that need the body
    *before* continuing (Load test body) should do their work in ``on_done``.
    """
    loc = _settings.read_locations()
    local = loc.local or _settings.effective_library_roots()[0]

    dialog = QtWidgets.QProgressDialog(
        f"Fetching the {profile.label} rig body…", "Cancel", 0, 100, parent)
    dialog.setWindowTitle("Fetch rig")
    dialog.setWindowModality(QtCore.Qt.WindowModal)
    dialog.setMinimumDuration(0)
    dialog.setAutoClose(False)
    dialog.setValue(0)

    thread = QtCore.QThread(parent)
    worker = _FetchWorker(profile, local, loc.remote, variant)
    worker.moveToThread(thread)
    thread.started.connect(worker.run)

    def _on_progress(done: int, total: int) -> None:
        dialog.setValue(int(done * 100 / total) if total else 0)
        dialog.setLabelText(
            f"Fetching the {profile.label} rig body…\n"
            f"{done / _MB:.0f} of {total / _MB:.0f} MB")

    def _on_finished(path, error: str) -> None:
        dialog.close()
        thread.quit()
        thread.wait()
        # Keep the pair alive until the thread has actually stopped, then let Qt reap them.
        worker.deleteLater()
        thread.deleteLater()
        if on_done is not None:
            on_done(path, error)

    worker.progressed.connect(_on_progress)
    worker.finished.connect(_on_finished)
    # Cancel is best-effort: the copy is a chunked loop with no abort hook, so the dialog
    # goes away and the (atomic) copy finishes in the background rather than leaving a
    # half-written rig. Better a wasted copy than a truncated one.
    dialog.canceled.connect(dialog.close)
    thread.start()


class RigSelector(QtWidgets.QWidget):
    """Dropdown of registered rigs + body status, and optionally a Register button.

    Emits :attr:`rigChanged` with the new rig id after the choice is persisted, so tabs
    can re-filter or re-label. Selecting never downloads anything.
    """

    rigChanged = QtCore.Signal(str)
    registerRequested = QtCore.Signal()

    def __init__(self, *, show_register: bool = False,
                 variant_provider: Callable[[], str] | None = None, parent=None):
        super().__init__(parent)
        self._profiles: list = []
        self._loading = False
        # A files-mode rig has one body per variant, so status and fetch depend on which
        # variant the host tab has chosen; tabs that don't care leave this unset.
        self._variant_provider = variant_provider

        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        row.setSpacing(8)

        caption = QtWidgets.QLabel("Rig")
        caption.setObjectName("muted")
        row.addWidget(caption)

        self._combo = QtWidgets.QComboBox()
        self._combo.setMinimumHeight(28)
        self._combo.setMinimumWidth(180)
        self._combo.setToolTip(
            "The registered rig you're working with. Publishing tags assets with it; "
            "the Library filters clothing to it.")
        self._combo.currentIndexChanged.connect(self._on_changed)
        row.addWidget(self._combo, 1)

        self._status = QtWidgets.QLabel("")
        self._status.setObjectName("muted")
        row.addWidget(self._status, 0)

        self._fetch_btn = QtWidgets.QToolButton()
        self._fetch_btn.setText("Fetch rig")
        self._fetch_btn.setToolTip(
            "Download this rig's body from the shared library. Rig files aren't synced "
            "(they're large), so they're fetched only when you need one.")
        self._fetch_btn.clicked.connect(self._fetch)
        row.addWidget(self._fetch_btn, 0)

        if show_register:
            register = QtWidgets.QToolButton()
            register.setText("Register rig…")
            register.setToolTip(
                "Register the rig in the current scene so the tool can author and attach "
                "clothing for it.")
            register.clicked.connect(self.registerRequested.emit)
            row.addWidget(register, 0)

        self.reload()

    # --- state ----------------------------------------------------------------
    def reload(self, select: str = "") -> None:
        """Rebuild the list from the library; keep (or set) the active selection."""
        self._loading = True
        try:
            wanted = select or self.rig_id() or _settings.active_rig_id()
            self._profiles = _rigs.list_profiles()
            self._combo.clear()
            for profile in self._profiles:
                self._combo.addItem(profile.label, profile.rig_id)
            index = self._combo.findData(wanted)
            self._combo.setCurrentIndex(index if index >= 0 else
                                        (0 if self._profiles else -1))
            if not self._profiles:
                self._combo.setPlaceholderText("- no rig registered -")
        finally:
            self._loading = False
        self._refresh_status()

    def select(self, rig_id: str) -> bool:
        """Switch to ``rig_id`` as if the user had picked it (persists, emits, restatuses).

        Returns False when that rig isn't registered here - the caller decides whether
        that's worth reporting (loading an asset built for a rig you don't have is).
        """
        index = self._combo.findData(rig_id)
        if index < 0:
            return False
        self._combo.setCurrentIndex(index)  # _on_changed persists and emits
        return True

    def profile(self):
        """The selected :class:`core.rigs.RigProfile`, or ``None`` if nothing is registered."""
        index = self._combo.currentIndex()
        return self._profiles[index] if 0 <= index < len(self._profiles) else None

    def rig_id(self) -> str:
        return self._combo.currentData() or ""

    def variant(self) -> str:
        """Body variant to fetch, from the host tab (empty when it has no opinion)."""
        return self._variant_provider() if self._variant_provider is not None else ""

    # --- behaviour ------------------------------------------------------------
    def _on_changed(self, _index: int) -> None:
        if self._loading:
            return
        rig_id = self.rig_id()
        if rig_id:
            _settings.set_rig(rig_id)
        self._refresh_status()
        self.rigChanged.emit(rig_id)

    def refresh_status(self) -> None:
        """Show where this rig's body is - a stat only, never a download."""
        profile = self.profile()
        if profile is None:
            self._status.setText("")
            self._fetch_btn.setVisible(False)
            return
        loc = _settings.read_locations()
        local = loc.local or _settings.effective_library_roots()[0]
        status = _rigs.rig_file_status(profile, local, loc.remote, self.variant())

        text, fetchable = {
            _rigs.STATUS_BUNDLED: ("body: bundled", False),
            _rigs.STATUS_LOCAL: ("body: ready", False),
            _rigs.STATUS_REMOTE_ONLY: (
                "body: not downloaded"
                + _size_text(_rigs.rig_file_size(profile, loc.remote, self.variant())),
                True),
            _rigs.STATUS_MISSING: ("body: missing from the library", False),
            _rigs.STATUS_NO_FILE: ("no test body registered", False),
        }.get(status, ("", False))
        self._status.setText(text)
        self._fetch_btn.setVisible(fetchable)

    def _fetch(self) -> None:
        profile = self.profile()
        if profile is None:
            return

        def done(path, error: str) -> None:
            if error:
                QtWidgets.QMessageBox.warning(self, "Fetch rig failed", error)
            self._refresh_status()

        fetch_rig_file(self, profile, self.variant(), done)
