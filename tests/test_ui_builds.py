"""Smoke test: the UI can actually be built, checked against a stubbed PySide6.

Maya ships PySide6; this test environment does not, so until now the `ui` package was
never imported by the suite and was covered only by `py_compile`. That catches syntax
errors and nothing else - a rename that updates a method definition but not its call sites
compiles perfectly and then fails at launch inside Maya. Exactly that shipped once
(`RigSelector._refresh_status` -> `refresh_status`), which is why this exists.

So Qt is stubbed just well enough to run `_build_ui()` on every panel, and the stub is
deliberately asymmetric - that asymmetry is the whole point:

  * **Qt's own API** (camelCase) resolves to a permissive stub. We are not testing Qt.
  * **our API** (snake_case, contains ``_``) is never faked. A missing ``self._foo`` or
    ``self.refresh_status`` raises AttributeError here exactly as it would in Maya.

What this proves: every widget is constructed, every signal is wired to a slot that
exists, and the ordering between them works (a panel that reads a widget it hasn't created
yet fails here). What it does not prove: that anything *looks* right, or that any handler
behaves correctly once clicked. It is a launch check, not a UI test.

The stub is installed in a **subprocess** so a fake ``PySide6`` never leaks into
``sys.modules`` for the rest of the suite.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def test_every_panel_can_be_built():
    """Import and construct each panel; any AttributeError/TypeError fails the test."""
    result = subprocess.run(
        [sys.executable, str(Path(__file__).resolve()), "--build"],
        capture_output=True, text=True, cwd=str(REPO))
    assert result.returncode == 0, (
        "the UI could not be built - this is what a launch failure in Maya looks like:\n"
        + result.stdout + result.stderr)


# --------------------------------------------------------------------------- #
# The stub + build run, executed as a subprocess by the test above.
# --------------------------------------------------------------------------- #
def _is_ours(name: str) -> bool:
    """True for our own snake_case API, which the stub must NOT fake."""
    return not name.startswith("__") and "_" in name.lstrip("_")


def _install_qt_stub() -> None:
    import types

    class _StubMeta(type):
        """Class-level access (Qt.AlignCenter, QMessageBox.Yes) yields a stub."""

        def __getattr__(cls, name):
            if _is_ours(name):
                raise AttributeError(name)
            value = QtStub()
            setattr(cls, name, value)
            return value

    class QtStub(metaclass=_StubMeta):
        def __init__(self, *args, **kwargs):
            pass

        def __getattr__(self, name):
            if _is_ours(name):
                raise AttributeError(name)  # ours - let the real error through
            return QtStub()

        def __call__(self, *args, **kwargs):
            return QtStub()

        def __or__(self, other):
            return self

        __ror__ = __or__

        # Qt getters feed real arithmetic in our code (findData() >= 0, count());
        # behave like a harmless 0 rather than exploding.
        def __index__(self):
            return 0

        __int__ = __index__

        def __lt__(self, other):
            return False

        __gt__ = __le__ = __ge__ = __lt__

        def __len__(self):
            return 0

        def __iter__(self):
            return iter(())

        def __bool__(self):
            return False

        def __eq__(self, other):
            return False

        __hash__ = object.__hash__

    class Signal:
        """Class-level Qt signal; every instance access yields a connectable stub."""

        def __init__(self, *types_):
            pass

        def __get__(self, obj, objtype=None):
            return QtStub()

    class _QtModule(types.ModuleType):
        def __getattr__(self, name):
            if name == "Signal":
                return Signal
            cls = type(name, (QtStub,), {})
            setattr(self, name, cls)
            return cls

    pyside = types.ModuleType("PySide6")
    for sub in ("QtCore", "QtGui", "QtWidgets"):
        module = _QtModule(f"PySide6.{sub}")
        setattr(pyside, sub, module)
        sys.modules[f"PySide6.{sub}"] = module
    sys.modules["PySide6"] = pyside
    sys.modules["shiboken6"] = types.ModuleType("shiboken6")


def _build_all() -> int:
    _install_qt_stub()
    sys.path.insert(0, str(REPO / "scripts"))

    from outfitter.ui import publish_panel, rig_bar, window

    failures = []
    for label, build in (
        ("RigSelector", lambda: rig_bar.RigSelector(show_register=True)),
        ("PublishPanel", lambda: publish_panel.PublishPanel()),
        ("OutfitterBrowser", lambda: window.OutfitterBrowser()),
    ):
        try:
            build()
        except Exception as exc:  # noqa: BLE001 - report everything, hide nothing
            failures.append(f"{label}: {type(exc).__name__}: {exc}")
        else:
            print(f"built: {label}")
    for line in failures:
        print(f"FAILED: {line}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(_build_all())
