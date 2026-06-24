# Hat Sample — structural reference for a publish-ready asset

`hat_sample.ma` is a **hat** authored to the Clothing Asset Authoring Spec. It exists so a
rigger can open it next to their own delivery and see exactly where the structure and
naming need to land. It passes the tool's validator with **0 errors / 0 warnings**.

> **Scope: structure + naming only.** The geometry is a placeholder box and the `cloth_*`
> joints carry **placeholder positions and identity jointOrient**. Do **not** skin or attach
> against this file as-is — see "The one thing this sample can't teach" at the bottom.

---

## What a publish-ready asset must have (the contract)

```
cloth_hat_sample            ← asset top group (one root transform)
├── Mesh_GRP                ← REQUIRED name
│   └── cloth_hat_mesh      ← the garment mesh (clean: no history, no tweaks)
├── Rig_GRP                 ← REQUIRED name — holds the connection skeleton
│   └── cloth_root          ← REQUIRED — duplicate of the body 'root' joint
│       └── cloth_pelvis → cloth_spine_01..05 → cloth_neck_01 → cloth_neck_02 → cloth_head
│                            ← the chain up to the joint(s) the hat binds to (cloth_head)
└── Ctrl_GRP                ← REQUIRED name — holds animator controls
    └── cloth_fit_ctrl      ← carries the fit_* attributes
cloth_info                  ← REQUIRED network node: assetName/assetType/clothVersion/genHumanCompat (+author/notes)
```

Hard rules the validator enforces: the three `*_GRP` names exactly; a `cloth_info` node;
a `cloth_root`; at least one `cloth_`-prefixed connection joint; **no** references, **no**
namespaces, **no** blendShape/nCloth/nucleus, and **no** duplicate node names.

---

## Your delivery → the contract (the diff)

Mapping what was in `GenHuman_HatRig_v01.ma` onto what the asset needs:

| Your node                         | What it should be                       | Why |
|-----------------------------------|-----------------------------------------|-----|
| `GH_Hat_rig`                      | `cloth_hat_sample` (asset top group)    | One clean root transform; name is the asset. |
| `GH_Hatrig_GEO_GRP`               | **`Mesh_GRP`**                          | Required exact name. |
| `GH_Hatrig_GEO`                   | `cloth_hat_mesh`                        | Descriptive `cloth_` mesh name under `Mesh_GRP`. |
| `GH_Hatrig_JNT_GRP`               | **`Rig_GRP`**                           | Required exact name. |
| `Hat_JNT`                         | keep as your **bind** joint, **but add** `cloth_root` + `cloth_head` | The tool snaps the hat on by connecting `cloth_*` joints to the body. Without them there's nothing to attach. Bind the hat to `cloth_head`. |
| `GH_Hatrig_CTR_GRP`               | **`Ctrl_GRP`**                          | Required exact name. |
| `GH_Hatrig_CTR_GRP` (2nd, nested) | rename — **duplicate name**             | Two nodes share this short name; all names must be unique. |
| *(none)*                          | **`cloth_info`** network node           | Metadata the browser reads. Missing entirely. |
| *(none)*                          | **`cloth_fit_ctrl`** with `fit_*` attrs | Optional but expected: the garment's fit controls. |

> No `_jnt` suffix on connection joints. The name is `cloth_` + the **exact** body joint
> name (e.g. `cloth_head`, never `cloth_head_jnt`).

---

## Scene cleanup before delivery (this was the bulk of the problem)

Your file still contained a large amount of the GenHuman body rig. The published asset must
contain **only the garment**. Remove:

- **~93 nodes still carrying the `GenHuman_rig:` namespace** — leftover face/mouth matrix
  nodes, arm/leg squash curves, and `GenHuman_rig:sceneConfigurationScriptNode` (a script
  node that runs on file open). Delete the GenHuman rig and remove its namespaces.
- **Duplicate / namespaced shaders** — the hat material existed twice (`hat_rig:HatSG` and
  `hat_rig1:HatSG`), plus orphan shading groups from the GenHuman demo outfit and a
  `GENHUMAN_*` checker placeholder. Collapse to **one** clean, namespace-free hat material.
- **Leftover rig selection sets** — `GenHuman_rig_set`, `GenHuman_rig_ctrls_set`,
  `god_m_ctrls_set`, every `*_ctrls_set`.
- **Any script nodes.** A clean asset has none.

Rule of thumb: after cleanup, **nothing** in the scene should contain `GenHuman`, a `:`
namespace, or reference another file.

---

## The one thing this sample can't teach: the real skeleton

The `cloth_*` joints here have **placeholder** positions and identity orient, so the figure
reads as a stick standing upright — fine for showing names/hierarchy, wrong for production.

In the real asset, the `cloth_*` skeleton must be a **faithful duplicate of the live
GenHuman export skeleton** — identical joint positions **and** identical `jointOrient`.
Attach connects `translate`/`rotate`/`scale` only (never `jointOrient`), so an invented
"stick" skeleton lies on the ground and crumples the mesh when the rig drives it.

The authoritative way to get this right is `examples/build_example_asset.py`: with the
GenHuman rig in the scene, it duplicates the rig's export-skeleton joints, renames them
`cloth_*`, and skins the garment onto that real-oriented skeleton. Follow that pattern for
the hat — duplicate the rig's `head` (and the spine/neck chain up to it), rename to
`cloth_*`, skin the hat to `cloth_head`, then delete the rig and save.

---

## Check your work

From the repo root, headless (no Maya needed):

```bash
python3 -c "import sys; sys.path.insert(0,'scripts'); \
from outfitter.core.publish import validate_published_ma; \
r=validate_published_ma('path/to/your_hat.ma'); print(r.summary_line()); \
[print(' ', i) for i in r.issues]"
```

`0 error(s)` means the structure/naming/cleanliness contract is met. This sample returns
exactly that.
