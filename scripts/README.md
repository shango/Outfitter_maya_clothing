# outfitter — developer notes

Maya 2026 tool for browsing/attaching snap-on clothing assets to the GenHuman rig.
Build contract: `../prd.md` + `../Clothing Asset Authoring Spec.md` (spec wins on conflict).

## Layout
```
outfitter/
  config.py        taxonomy, structure contract, connect-attr set, install paths
  core/            PURE logic — no maya / no PySide6 at import (headless-testable)
    ma_parse.py    lightweight Maya-ASCII (.ma) reader
    asset.py       AssetMetadata + ClothingAsset model + validation
    library.py     scan roots -> LibraryScanResult
    scene.py       SceneGateway Protocol (the Maya boundary) + MayaScene + AttrSpec
    validate.py    file + scene-precondition validation
    attach.py      transactional connectAttr-only attach / detach
    registry.py    attached-instance + connection tracking
    controls.py    fit-control discovery + drive (M3)
    placement.py   per-instance placement offset (M3)
    presets.py     fit/placement preset capture / apply / JSON sidecar (M3)
    export.py      Genie export-readiness audit over scene + registry (M4)
    settings.py    library roots stored in scripts/path.txt (Setup tab read/write)
  ui/window.py          PySide6 browser: Library + Setup tabs (M1)
  ui/controls_panel.py  PySide6 fit/placement/preset panel (M3)
  launch.py        entry points
```

Distribution / installer (at the repo root, NOT under `scripts/`):
```
install.py                  onMayaDroppedPythonFile drop handler (Maya) — the file users drag in
installer/installer_core.py pure copy/merge logic — overwrite pkg, non-clobber assets (headless-tested)
installer/shelf.py          create/refresh the "Clothing" shelf button (Maya)
```
The package is `installer/`, NOT `install/`: a package sharing the drop file's stem
(`install`) would shadow `install.py` on `sys.path`, so Maya would import the package
(no `onMayaDroppedPythonFile`) instead of the drop handler.

**Design rule:** nothing under `core/` imports `maya` or `PySide6` at module scope,
so the validation/attach/fit core runs in CI. The single Maya boundary is
`core.scene.SceneGateway` — `MayaScene` wraps `cmds` (lazy import), tests use an
in-memory `FakeScene`. Maya/Qt live only in `ui/`.

## Run

Inside Maya 2026 (Script Editor / shelf button):
```python
import outfitter.launch
outfitter.launch.run()
```

Standalone dev preview (PySide6 only, no Maya):
```bash
PYTHONPATH=scripts python -m outfitter.launch
```

## Tests (headless, no Maya)
```bash
cd tests && python -m pytest -q
```

## Status
- M1 done: config, core (ma_parse/asset/library), read-only browser shell.
- M2 done: validate → attach → detach (`core.scene`/`validate`/`attach`/`registry`), transactional + dual-skeleton safe.
- M3 done: fit controls + placement + presets (`core.controls`/`placement`/`presets`, `ui.controls_panel`).
- M4 done: multi-asset independence combos, Genie export-readiness audit (`core.export`), drag-and-drop installer (`install.py` + `installer/`).
- M5 done: example compliant asset (`assets/trench_coat_A/`), tool-user docs (`../Outfitter — User Guide.md`), in-Maya `examples/` scripts (build the skinned asset + the GenHuman test scene). `tests/test_example_asset.py` re-validates the shipped asset every run.
- Setup tab done: user points the browser at one+ library folders (external drive / server). The Setup tab **reads and writes `scripts/path.txt`** (one folder per line) — that plain-text file is the single store ("db"). When it holds any folder the tool scans exactly those, else falls back to built-in defaults. `path.txt.example` ships beside the package; `path.txt` is hand-editable and survives installer upgrades (installer overwrites the package dir, never `path.txt`).
- **95 headless tests passing.** A handful of `[!]` in-Maya smoke checks remain (see `../todo.md`).

## Packaging (what ships to tool users)
Ship, preserving layout: `install.py`, `installer/` (no `__pycache__`), `scripts/outfitter/`
(no `__pycache__`), `scripts/path.txt.example`, and `assets/` (the starter library,
incl. `assets/trench_coat_A/`). **Exclude** (dev-only): `tests/`, `examples/`, the
`GenHuman_rig_*.ma` files, `prd.md`, `todo.md`, `Outfitter Rig System.md`, the
`rig_naming_*.csv` files, and every `__pycache__`. Optionally bundle the two artist docs
(`Clothing Asset Authoring Spec.md`, `Clothing Asset Quick Guide.*`) and the tool-user
`Outfitter — User Guide.md`.
