# Outfitter

A Maya 2026 tool for dressing character rigs. Browse a shared library of clothing, snap a
garment onto your animated character in one click, take it off just as cleanly, and publish
new garments back to the library for everyone to use.

Outfitter is **rig-agnostic**: register the rig you work with once, from a scene, and the
tool learns its skeleton, its body variants and which joints each garment type should skin
to. Every published asset records which rig it belongs to, and the browser only offers you
clothing that fits the rig you're dressing.

It runs as a single window inside Maya with three tabs: **Library** (browse and attach),
**Publish** (turn a hand-authored garment into a library asset), and **Setup** (point it at
your local and remote folders).

## Requirements

- Autodesk Maya 2026 (ships with Python 3 and PySide6, which is all the UI needs)
- A character rig. **GenHuman v03** ships registered out of the box; any other rig is
  registered from the Publish tab (put it in a scene, click **Register rig…**).
- No external Python packages to install

## Install

Drag `install.py` into a Maya 2026 viewport. That's it. The installer:

1. copies the `outfitter` package into your Maya user script folder,
2. merges a starter set of assets into your local library (never overwriting your own),
3. adds an **Outfitter** button to your active shelf.

Click the shelf button to open the tool. Re-dropping a newer build upgrades in place.

## Usage

See [Outfitter Guide.md](Outfitter%20Guide.md) for the friendly walkthrough. The short
version:

- **Setup tab:** set your local working folder (the one Outfitter scans) and, optionally, a
  remote shared folder to sync from.
- **Library tab:** pick the **rig** you're dressing, filter and search the grid, click an
  asset to spin its turntable preview, then **Attach** it (and **Detach** when done).
  Clothing built for other rigs is hidden, with a count - tick *Show other rigs* to see it.
- **Publish tab:** pick the rig you're authoring for (or **Register rig…** a new one), then
  follow the five numbered steps to build the cloth rig, skin the mesh, capture a turntable,
  and publish.

### Working with more than one rig

- **Register a rig:** put it in a scene, then Publish tab ▸ **Register rig…**. Outfitter
  proposes the export-skeleton group, the body-variant switch and the rig file, you confirm
  them, and it captures the rig's skeleton, derives the per-garment-type skin sets, and
  copies the rig into the shared library so everyone else can fetch it.
- **Rig files aren't synced.** They're 25-30 MB and most people only use one, so Sync
  carries the small rig *profiles* and the rig body itself is fetched on demand - the first
  time you load a test body, or from the **Fetch rig** button beside the rig dropdown.
- **Reusing a garment on another rig:** right-click it in the Library and choose *Retarget
  to…*. It remaps and moves the joints with the skin weights preserved. It does **not**
  reshape the mesh, so check the fit and publish it as a new asset.
- **Older assets** with no rig recorded read as GenHuman, so an existing library keeps
  working untouched. Setup ▸ **Stamp rig metadata** writes it down explicitly.

## Project layout

```
scripts/outfitter/      the tool itself
  core/                 pure logic, no Maya or Qt imports (headless-testable)
  ui/                   PySide6 panels (the Maya-facing layer)
  config.py             paths, constants, version
installer/              drag-and-drop install logic
tests/                  headless pytest suite
install.py              drop this into Maya to install
```

The design rule: nothing under `core/` imports `maya` or `PySide6` at module scope, so the
validation and publish logic runs headlessly in CI. Anything that needs a live Maya scene
lives in the `ui` layer or the `maya_*` modules and is checked with `py_compile`.

## Running the tests

The core suite needs no Maya, just pytest:

```
pytest
```

It covers the library scanner, asset/metadata model, publish assembly and validation, sync,
and the turntable geometry. The Maya-only modules are compile-checked rather than executed.

## Docs

- [Outfitter Guide.md](Outfitter%20Guide.md) - the user walkthrough
- [Clothing Asset Prep.md](Clothing%20Asset%20Prep.md) - how to prepare a garment for publishing
- [Clothing Asset Authoring Spec.md](Clothing%20Asset%20Authoring%20Spec.md) - the full asset contract
