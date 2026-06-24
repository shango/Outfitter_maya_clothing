# Example asset — `trench_coat_A`

A spec-compliant **example clothing asset** for the GenHuman Outfitter tool,
built to `Clothing Asset Authoring Spec.md`. It ships in the bundled starter library
so the tool always has something to browse, validate, attach, and detach.

## What it demonstrates

- The required hierarchy: `cloth_trench_coat_A` → `Mesh_GRP` / `Rig_GRP` / `Ctrl_GRP` + `cloth_info`.
- A real connection skeleton: `cloth_root` plus the full parent chain, every joint named
  `cloth_` + the **exact** GenHuman body joint name (spine/neck/arms/legs), no `_jnt` suffix.
- Helper joints for secondary motion (`cloth_coatTail_01/02`) parented under a `cloth_` joint —
  these are **not** wired to the body at attach time.
- A fit control `cloth_fit_ctrl` exposing keyable `fit_*` floats with min/max and neutral
  defaults (`fit_tightness`, `fit_thickness`, `fit_length`, `fit_hem_length`,
  `fit_collar_tightness`), plus a secondary animator control `cloth_coatTail_ctrl`.
- A populated `cloth_info` node and a matching `trench_coat_A.json` sidecar.
- A clean file: no references, no namespaces, none of the forbidden node types
  (`blendShape` / `nCloth` / `nucleus`).

`tests/test_example_asset.py` validates this shipped `.ma` through the real tool core on
every test run, so it can never silently drift out of compliance.

## What it does NOT include (and why)

The garment geometry is **two placeholder cubes** and there is **no `skinCluster`** or fit
deformer in this `.ma`. A correct smooth bind and the fit-driving deformers must be created
in Maya (vertex/skin data can't be hand-authored reliably). To produce the fully skinned,
fit-driven production version, open Maya 2026 and run:

```python
# In Maya's Script Editor (Python):
import examples.build_example_asset as b
b.build()          # builds geometry + joints + smooth bind + fit lattice, exports the .ma
```

See `examples/build_example_asset.py` at the repo root. That script is the authoritative
generator; this `.ma` is the lightweight, always-valid structural reference.

## Files

| File | Purpose |
|---|---|
| `trench_coat_A.ma` | the asset (Maya ASCII) |
| `trench_coat_A.json` | sidecar metadata (browser fast-path; mirrors `cloth_info`) |
| `README.md` | this file |
