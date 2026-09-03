# `examples/` — dev-only in-Maya scripts

These run **inside Maya 2026** and are **not** shipped to tool users (excluded from the
install package, like `tests/`). CI only `py_compile`s them.

| Script | What it does |
|---|---|
| `build_example_asset.py` | Builds the fully-skinned production version of `assets/trench_coat_A` — real geometry, smooth bind, `cloth_info` — and exports a clean `.ma`. |
| `build_test_scene.py` | Imports the GenHuman rig and attaches compliant assets through the real tool core (connectAttr-only, transactional), then runs the Genie export-readiness audit. |
| `prep_michaelc_rig.py` | Makes the MichaelC rig registrable: dissolves the asset containers sealing its export skeleton, renames `Skeleton`/`Geo`/`Body` to rig-unique names, clears the pre-bind leftovers off the skin chain, normalizes weights, and audits which joints the body carries no weight on. Dry run by default. |
| `rebind_michaelc.py` | Rebuilds MichaelC's skinCluster so Maya's weight tools work at all (W1). Reads the weights through `MFnSkinCluster`, refuses to run unless the mesh is at bind pose, deletes history, binds classic linear with `removeUnusedInfluence` off, then writes the weights back matched by influence *name* with normalization disabled - so the 27 deliberately under-weighted vertices survive for W5 instead of being silently normalized away. Dry run by default. |

## Use

From Maya's Script Editor (Python), put the repo on `sys.path` once:

```python
import sys; sys.path.append(r"/path/to/maya_clothing_rig")

import examples.build_example_asset as b
b.build()          # regenerate assets/trench_coat_A/trench_coat_A.ma (skinned)

import examples.build_test_scene as t
t.build()          # GenHuman rig + trench_coat_A attached, prints the audit

import examples.prep_michaelc_rig as p
p.prep()               # dry run - report what the MichaelC rig still needs
p.prep(apply=True)     # apply it, then save and Register rig...

import examples.rebind_michaelc as r
r.run()                # dry run - report the rebind it would perform
r.run(apply=True)      # rebind + restore weights + verify, then save as 01.7
```

`build_test_scene.build(assets=[("trench_coat_A", "coat")])` takes a list of
`(asset_name, instance_namespace)` pairs to dress the rig with multiple garments.
