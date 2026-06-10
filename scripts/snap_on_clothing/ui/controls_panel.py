"""PySide6 fit / placement panel for one attached garment instance (M3).

Renders the fit attributes discovered by ``core.controls`` as float sliders, a
placement offset block, and preset save/load — all driving the live scene through
the same ``SceneGateway`` the headless core uses. The panel holds **no** fitting
logic of its own: every value change calls into ``core.controls`` / ``core.placement``
/ ``core.presets`` so behaviour is identical to (and tested by) the headless layer.

UI only — verified by ``py_compile``; live behaviour is an in-Maya smoke check
(PySide6 ships with Maya 2026 and is not installed in the headless test env).
"""
from __future__ import annotations

from pathlib import Path

from PySide6 import QtCore, QtWidgets

from ..core import controls as _controls
from ..core import placement as _placement
from ..core import presets as _presets
from ..core.registry import AttachedInstance
from ..core.scene import SceneGateway

_SLIDER_STEPS = 1000  # integer resolution a float range is mapped onto


class _FloatSlider(QtWidgets.QWidget):
    """A labelled slider + spinbox bound to one :class:`core.controls.FitAttr`."""

    def __init__(self, scene: SceneGateway, attr: _controls.FitAttr, parent=None):
        super().__init__(parent)
        self._scene = scene
        self._attr = attr
        self._lo = attr.slider_min
        self._hi = attr.slider_max

        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        self._label = QtWidgets.QLabel(attr.label)
        self._label.setMinimumWidth(120)
        self._slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self._slider.setRange(0, _SLIDER_STEPS)
        self._spin = QtWidgets.QDoubleSpinBox()
        self._spin.setRange(self._lo, self._hi)
        self._spin.setDecimals(3)
        self._spin.setSingleStep((self._hi - self._lo) / 100.0)
        row.addWidget(self._label)
        row.addWidget(self._slider, 1)
        row.addWidget(self._spin)

        self._slider.valueChanged.connect(self._on_slider)
        self._spin.valueChanged.connect(self._on_spin)
        self.set_value(attr.value)

    # value <-> slider-tick mapping -------------------------------------------
    def _to_tick(self, value: float) -> int:
        if self._hi <= self._lo:
            return 0
        frac = (value - self._lo) / (self._hi - self._lo)
        return int(round(max(0.0, min(1.0, frac)) * _SLIDER_STEPS))

    def _from_tick(self, tick: int) -> float:
        return self._lo + (tick / _SLIDER_STEPS) * (self._hi - self._lo)

    def set_value(self, value: float) -> None:
        value = self._attr.clamp(value)
        for w in (self._slider, self._spin):
            w.blockSignals(True)
        self._slider.setValue(self._to_tick(value))
        self._spin.setValue(value)
        for w in (self._slider, self._spin):
            w.blockSignals(False)

    def _commit(self, value: float) -> None:
        applied = _controls.set_fit_value(self._scene, self._attr, value)
        self.set_value(applied)

    def _on_slider(self, tick: int) -> None:
        self._commit(self._from_tick(tick))

    def _on_spin(self, value: float) -> None:
        self._commit(value)

    def reset(self) -> None:
        self._commit(_controls.reset_fit(self._scene, self._attr))


class _Vec3Row(QtWidgets.QWidget):
    """Three spinboxes for a translate/rotate/scale channel."""

    edited = QtCore.Signal()

    def __init__(self, label: str, default, parent=None):
        super().__init__(parent)
        row = QtWidgets.QHBoxLayout(self)
        row.setContentsMargins(0, 0, 0, 0)
        cap = QtWidgets.QLabel(label)
        cap.setMinimumWidth(80)
        row.addWidget(cap)
        self._boxes: list[QtWidgets.QDoubleSpinBox] = []
        for d in default:
            box = QtWidgets.QDoubleSpinBox()
            box.setRange(-1e6, 1e6)
            box.setDecimals(3)
            box.setValue(d)
            box.valueChanged.connect(lambda *_: self.edited.emit())
            self._boxes.append(box)
            row.addWidget(box)

    def value(self) -> tuple[float, float, float]:
        return (self._boxes[0].value(), self._boxes[1].value(), self._boxes[2].value())

    def set_value(self, v) -> None:
        for box, comp in zip(self._boxes, v):
            box.blockSignals(True)
            box.setValue(comp)
            box.blockSignals(False)


class FitControlsPanel(QtWidgets.QWidget):
    """Fit sliders + placement + presets for a single attached instance."""

    def __init__(
        self,
        scene: SceneGateway,
        instance: AttachedInstance,
        *,
        placement_node: str | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._scene = scene
        self._instance = instance
        self._placement_node = placement_node
        self._sliders: list[_FloatSlider] = []
        self._build_ui()

    def _build_ui(self) -> None:
        outer = QtWidgets.QVBoxLayout(self)
        title = QtWidgets.QLabel(f"{self._instance.asset_name}  ({self._instance.asset_type})")
        title.setStyleSheet("font-weight: bold;")
        outer.addWidget(title)

        # --- fit controls -----------------------------------------------------
        fit_box = QtWidgets.QGroupBox("Fit")
        fit_layout = QtWidgets.QVBoxLayout(fit_box)
        controls = _controls.discover_controls(self._scene, self._instance.namespace)
        surfaced = _controls.surfaced_fit_attrs(controls)
        if surfaced:
            for attr in surfaced:
                slider = _FloatSlider(self._scene, attr)
                self._sliders.append(slider)
                fit_layout.addWidget(slider)
            reset_btn = QtWidgets.QPushButton("Reset fit to neutral")
            reset_btn.clicked.connect(self._reset_fit)
            fit_layout.addWidget(reset_btn)
        else:
            fit_layout.addWidget(QtWidgets.QLabel("No fit controls exposed by this asset."))
        outer.addWidget(fit_box)

        # --- placement --------------------------------------------------------
        if self._placement_node is not None:
            outer.addWidget(self._build_placement_box())

        # --- presets ----------------------------------------------------------
        preset_row = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("Save preset…")
        save_btn.clicked.connect(self._save_preset)
        load_btn = QtWidgets.QPushButton("Load preset…")
        load_btn.clicked.connect(self._load_preset)
        preset_row.addWidget(save_btn)
        preset_row.addWidget(load_btn)
        preset_row.addStretch(1)
        outer.addLayout(preset_row)
        outer.addStretch(1)

    def _build_placement_box(self) -> QtWidgets.QWidget:
        box = QtWidgets.QGroupBox("Placement offset")
        layout = QtWidgets.QVBoxLayout(box)
        current = _placement.read_placement(self._scene, self._placement_node)
        self._t_row = _Vec3Row("Translate", current.translate)
        self._r_row = _Vec3Row("Rotate", current.rotate)
        self._s_row = _Vec3Row("Scale", current.scale)
        for r in (self._t_row, self._r_row, self._s_row):
            r.edited.connect(self._apply_placement)
            layout.addWidget(r)
        reset_btn = QtWidgets.QPushButton("Reset placement")
        reset_btn.clicked.connect(self._reset_placement)
        layout.addWidget(reset_btn)
        return box

    # --- actions --------------------------------------------------------------
    def _reset_fit(self) -> None:
        for slider in self._sliders:
            slider.reset()

    def _apply_placement(self) -> None:
        p = _placement.Placement(
            translate=self._t_row.value(),
            rotate=self._r_row.value(),
            scale=self._s_row.value(),
        )
        _placement.apply_placement(self._scene, self._placement_node, p)

    def _reset_placement(self) -> None:
        _placement.reset_placement(self._scene, self._placement_node)
        ident = _placement.Placement()
        self._t_row.set_value(ident.translate)
        self._r_row.set_value(ident.rotate)
        self._s_row.set_value(ident.scale)

    def _save_preset(self) -> None:
        path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save preset", "", "Preset (*.json)")
        if not path:
            return
        name = Path(path).stem
        preset = _presets.capture_preset(
            name, self._scene, self._instance, placement_node=self._placement_node)
        preset.save(Path(path))

    def _load_preset(self) -> None:
        path, _ = QtWidgets.QFileDialog.getOpenFileName(
            self, "Load preset", "", "Preset (*.json)")
        if not path:
            return
        preset = _presets.Preset.load(Path(path))
        _presets.apply_preset(self._scene, preset, self._instance.namespace)
        self._refresh_from_scene()

    def _refresh_from_scene(self) -> None:
        """Pull current scene values back into the widgets after a preset load."""
        controls = _controls.discover_controls(self._scene, self._instance.namespace)
        by_key = {(a.node, a.attr): a for a in _controls.surfaced_fit_attrs(controls)}
        for slider in self._sliders:
            fresh = by_key.get((slider._attr.node, slider._attr.attr))
            if fresh is not None:
                slider.set_value(fresh.value)
        if self._placement_node is not None:
            p = _placement.read_placement(self._scene, self._placement_node)
            self._t_row.set_value(p.translate)
            self._r_row.set_value(p.rotate)
            self._s_row.set_value(p.scale)
