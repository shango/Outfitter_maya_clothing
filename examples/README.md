# `examples/` — dev-only in-Maya scripts

These run **inside Maya 2026** and are **not** shipped to tool users (excluded from the
install package, like `tests/`). CI only `py_compile`s them.

| Script | What it does |
|---|---|
| `build_example_asset.py` | Builds the fully-skinned production version of `assets/trench_coat_A` — real geometry, smooth bind, a `cloth_fit_ctrl`-driven fit lattice, `cloth_info` — and exports a clean `.ma`. |
| `build_test_scene.py` | Imports the GenHuman rig and attaches compliant assets through the real tool core (connectAttr-only, transactional), then runs the Genie export-readiness audit. |

## Use

From Maya's Script Editor (Python), put the repo on `sys.path` once:

```python
import sys; sys.path.append(r"/path/to/maya_clothing_rig")

import examples.build_example_asset as b
b.build()          # regenerate assets/trench_coat_A/trench_coat_A.ma (skinned)

import examples.build_test_scene as t
t.build()          # GenHuman rig + trench_coat_A attached, prints the audit
```

`build_test_scene.build(assets=[("trench_coat_A", "coat")])` takes a list of
`(asset_name, instance_namespace)` pairs to dress the rig with multiple garments.
