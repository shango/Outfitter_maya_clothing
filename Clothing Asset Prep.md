# Clothing Asset Prep — Quick Start

**Make in:** Maya 2026 · **Save as:** Maya ASCII (`.ma`) · **Tool:** Outfitter ▸ *Publish* tab

The short, practical version of getting a garment ready for the Outfitter tool.

---

## What you're making

A clothing asset is your garment mesh skinned to a copy of the GenHuman skeleton — the
`cloth_*` joints. The tool's whole job is to connect each **body joint** to your matching
**`cloth_` joint** by name, so the clothing follows the body.

- The match is **by name**: `cloth_spine_03` follows the body's `spine_03`. (The tool
  builds these joints for you — you don't hand-name them.)
- **Helper joints** you add (coat tails, skirts, straps) are *not* connected. They stay
  free for the animator.
- Each garment is authored **twice** — once on the **male** body, once on the **female**
  body. Same garment, fit to each. They publish as `m_<name>` and `f_<name>`.

---

## Prep the mesh

- **Pivot at world origin (on the ground), transforms frozen, with the geo sitting at its
  correct height.** (Pivot-at-origin is also a handy height check — a non-zero pivot Y
  means the garment isn't sitting right on the rig.)
- Clean **UVs** on every mesh. Name meshes `cloth_<part>_mesh`.
- **Smooth bind** only. **Delete history.**
- **Generic shader** (`lambert` / `standardSurface`).
- ❌ No blendShapes, no nCloth / simulation, no shrinkWrap to the body.

## Prep the scene

Most of the structure is built for you — **Create cloth skeleton** makes the three required
groups (**`Mesh_GRP`** for meshes, **`Rig_GRP`** for the `cloth_*` joints, **`Ctrl_GRP`**
for controls) and tucks your garment geo into `Mesh_GRP`. Your job is to keep the scene
**clean** so it publishes:

- **Bare names** — no namespaces, no references, no GenHuman rig left in the scene at publish.
- Skin to the **`cloth_*` joints**, never the GenHuman rig joints.
- Extra controls (for tails, skirts, straps) go in **`Ctrl_GRP`**.

*(If you already have the GenHuman rig in the scene when you build, the tool can't tell your
geo from the body mesh, so it leaves `Mesh_GRP` empty for you to fill.)*

---

## Step by step (Publish tab)

Work straight down the numbered steps:

1. **Set up the cloth rig** — choose the **Type** and **Gender**, click **Create cloth
   skeleton**. This builds the `cloth_*` joints, creates the `Mesh_GRP` / `Rig_GRP` /
   `Ctrl_GRP` groups (moving your garment geo into `Mesh_GRP`), and turns the recommended
   skin joints **green**. Then **Load test body** brings in the matching male/female
   GenHuman to pose against.
2. **Skin the mesh** — bind your garment to the green joints: **Skin ▸ Bind Skin**.
3. **Remove the test body** — pose the body to confirm the garment follows, then
   **Remove test body** so the joints go static. *(Optional: **Delete unused joints**.)*
4. **Capture the turntable** — frame the garment in the viewport and capture. The
   tool orbits it and bakes a clean **shaded** preview you can spin in the browser (it
   also saves a still for the grid thumbnail — no more flat wireframe shots).
5. **Publish** — fill in the asset details (name, version, author…), run **Check scene**,
   then **Publish**. It writes the metadata into the `.ma` (a `cloth_info` node) and sends
   the asset to the shared remote library.

---

## Final checklist

- [ ] Pivot at world origin (on the ground), transforms frozen, geo at correct height; history deleted, clean UVs.
- [ ] `Mesh_GRP`, `Rig_GRP`, `Ctrl_GRP` at the root (Create cloth skeleton makes these); bare names; no namespaces or references.
- [ ] Skinned to `cloth_*` joints (smooth bind). No blendShapes / sim / body shrinkWrap.
- [ ] Generic shader only.
- [ ] Test body removed — no GenHuman rig left in the scene.
- [ ] **Type** and **Gender** set; asset details filled in.
- [ ] **Check scene** passes.
- [ ] Saved as `.ma`.

> **Golden rule:** the tool matches **by name** and flags problems in **Check scene** — if
> something doesn't follow the body, check the joint names first.
