# Clothing Asset Authoring Specification

**For:** Clothing artist / rigger building snap-on assets for the GenHuman rig
**Host:** Maya 2026 · deliver Maya ASCII (`.ma`) only
**Status:** v1 · 2026-06-04
**Authority:** This document is the build contract. It consolidates the *Addendum — Snap-On
Clothing Rig Preparation Specification* and resolves the items it left open or stated incorrectly.
Where this document and the original Addendum examples disagree, **this document wins** (the
differences are called out explicitly below and were confirmed against the real GenHuman rig).

> **TL;DR for the rigger:** Build the garment. Duplicate the GenHuman joints you need (with their
> full parent chain up to a single root), rename each to `cloth_` + the *exact* body joint name,
> smooth-bind the garment to those joints. Add any helper joints / control rig / deformers you want
> for fit and secondary motion — **inside the asset you may use any Maya nodes**. Expose fit controls
> using the naming convention in §8. Organize into `Mesh_GRP / Rig_GRP / Ctrl_GRP`, add a `cloth_info`
> node, run the checklist in §16, export clean `.ma`. The snap-on tool does the rest.

---

## 1. How the snap-on works (so you know what you're building for)

The snap-on tool does **not** skin your garment, build deformers, or transfer weights. Your asset
arrives **fully rigged**. At attach time the tool does exactly one thing to bind your garment to the
body: it runs `connectAttr` from each GenHuman body joint to your matching `cloth_*` joint. That's it.

```
GenHuman body joint   --connectAttr-->   your cloth_ joint   --skinCluster-->   your garment
   (e.g. spine_03)                          (cloth_spine_03)                       cloth_jacket_mesh
```

Consequences for you:

- Your `cloth_*` connection joints **must be exact duplicates** of the GenHuman joints (same position,
  orientation, hierarchy) so that when the body's transforms drive them, the garment lands correctly.
- The match is **by name**. If a name is off by one character, that joint silently won't connect.
- **Helper joints, controls, and deformers you add are NOT connected to the body** — they stay fully
  artist-/animator-accessible after attach. That's where coat-tail swing, skirt control, and fit
  adjustment live.

---

## 2. Naming correction (read before you name anything)

The original Addendum showed these examples — **do not follow them, they are wrong:**

| Addendum example (WRONG) | Correct name |
|---|---|
| `cloth_spine_01_jnt` | `cloth_spine_01` |
| `cloth_l_arm_01_jnt` | `cloth_upperarm_l` |
| `cloth_r_foot_jnt` | `cloth_foot_r` |

**The rule:** a clothing connection joint name = `cloth_` + the **exact** GenHuman body joint name.

- **No `_jnt` suffix.**
- **Do not flip the side token.** GenHuman uses a *trailing* lowercase `_l` / `_r` (e.g. `upperarm_l`,
  `foot_r`), never a leading `l_` / `r_`.
- Case-sensitive. Copy the body name verbatim, then prefix `cloth_`.

The easiest way to get this right is to **duplicate the joints from the GenHuman rig itself** and then
add the `cloth_` prefix — don't hand-type the names.

---

## 3. Required asset hierarchy

Every asset is a single top group named after the asset, containing exactly three sub-groups plus the
info node:

```
cloth_<assetName>                 (top transform, at origin, all transforms zeroed/frozen)
├── Mesh_GRP                      garment geometry (skinned meshes)
├── Rig_GRP                       all joints (connection joints + helper joints) under cloth_root
├── Ctrl_GRP                      control rig (controls, fit control, control-rig deformer drivers)
└── cloth_info                    version / metadata node (see §12)
```

Rules:
- Geometry, skeleton, and controls must stay in **separate** groups (no joints under `Mesh_GRP`, etc.).
- The top group `cloth_<assetName>` and all three sub-groups must have **clean, frozen transforms**
  (translate 0, rotate 0, scale 1).
- Do **not** add a placement / offset group above the garment — the tool creates its own placement
  offset at attach time. Deliver the asset zeroed at origin.

---

## 4. Connection skeleton (the `cloth_*` joints)

These are the joints the tool wires to the body.

1. In the GenHuman scene, **duplicate** every joint your garment needs to follow, **plus its full
   parent chain up to the root**. (A hat still needs `root → pelvis → spine_01..05 → neck_01/02 →
   head` so the head's world motion composes correctly — it's only a handful of joints and stays
   lightweight.)
2. Keep them as a single chain under one root joint named **`cloth_root`** (duplicate of `root`,
   at origin).
3. Rename every duplicated joint to `cloth_` + its exact body name (see §2).
4. **Do not** re-orient, freeze, or alter the duplicated joints' transforms or `jointOrient` after
   duplication — they must remain identical to the body joints.
5. Put the whole chain under `Rig_GRP`.

**Only the joints you actually skin to need to exist as leaves** — but every ancestor up to `cloth_root`
must be present so the chain transforms correctly. Don't include joints the garment doesn't use
(e.g. shoes don't need arm joints).

### Joint name quick reference (prefix each with `cloth_`)
Authoritative source is the GenHuman rig (`GenHuman_rig_v03.ma`) — duplicate from it. Common names:

| Region | Body joints (add `cloth_` prefix) |
|---|---|
| Root/spine | `root`, `pelvis`, `spine_01`, `spine_02`, `spine_03`, `spine_04`, `spine_05` |
| Neck/head | `neck_01`, `neck_02`, `head` |
| Arm L/R | `clavicle_l/r`, `upperarm_l/r`, `lowerarm_l/r`, `hand_l/r` |
| Arm twist | `upperarm_twist_01_l/r`, `lowerarm_twist_01_l/r` (+ `_02_` if present) |
| Fingers | `thumb_01..03_l/r`, `index_01..03_l/r`, `middle_…`, `ring_…`, `pinky_…` |
| Leg L/R | `thigh_l/r`, `calf_l/r`, `foot_l/r`, `ball_l/r` |
| Leg twist | `thigh_twist_01_l/r`, `calf_twist_01_l/r` |

> Do **not** duplicate or connect to `ik_*` joints or the facial-module joints — clothing never binds
> there. Connect only to the standard deform joints listed above.

---

## 5. Helper / secondary joints

- Permitted and encouraged for secondary motion (coat tails, skirt panels, straps, hanging cloth).
- Parent them **under** the relevant `cloth_*` connection joint so they inherit body motion.
- These are **not** connected to the body by the tool — drive them with your own control rig.
- Naming: keep the `cloth_` prefix and a descriptive name, e.g. `cloth_coatTail_01`,
  `cloth_skirtFront_02`, `cloth_strap_l_01`. No `_jnt` suffix.

---

## 6. Skinning

- **Smooth bind only.** No rigid bind, no alternative skinning.
- Garment meshes bind to the `cloth_*` joints (connection joints and/or helper joints).
- SkinClusters must be valid and evaluate in realtime (keep influence counts reasonable).
- No blendshapes / corrective morphs anywhere (see §10).

---

## 7. Deformers & internal rigging (this is how "fit" and secondary motion are built)

**Important distinction:** The "no constraints / utility nodes / matrix nodes / expressions / driven
keys / networks" rule from the main spec applies **only to the snap-on connection between the body and
your clothing** (the `connectAttr` joint→joint links). **Inside your asset you may use any Maya nodes**
— the Addendum explicitly allows "any Maya deformers" and "any Maya node types within the control rig."

So you *may* use, inside the asset:
- Deformers (**self-contained only** — see warning): lattice (FFD), cluster, wire, `push`/displacement,
  nonlinear (bend/squash/etc.), `deltaMush`.
- Drivers: direct attribute connections, set-driven keys, utility/math nodes.

> **No deformer may depend on the body mesh.** `shrinkWrap` (and any deformer that takes an external
> target surface) is **not allowed** for fit — it would make the asset depend on the GenHuman body
> geometry, which breaks standalone authoring/validation and clean export. Fit must be achieved with
> deformers that live entirely inside the asset (lattice / cluster / normal-based push).

Constraints:
- No **blendshapes** (hard rule — see §10).
- No **simulation** (nCloth, etc.) — not supported, breaks realtime.
- Avoid **expressions** where a direct connection or SDK will do (expression eval is a playback cost).
- Everything must survive `.ma` export and keep **realtime playback** acceptable with multiple
  garments in-scene.

---

## 8. Fit-control convention (NEW — build your fit controls to this)

Fit (tightness, thickness, length, per-region adjustment) is delivered by **deformers you author into
the asset, driven by attributes on a fit control**. The snap-on tool discovers these attributes and
renders them as sliders in the UI — but the tool only *sets the values*; you build the rig that
responds to them.

### Where
- Create one control transform named **`cloth_fit_ctrl`** under `Ctrl_GRP`. (Per-region controls are
  allowed too — see below.)

### Attributes
Add **keyable, user-defined float** attributes using the `fit_` prefix. Set sensible **min/max** on
each (the tool reads the attr's min/max for the slider range) and a **neutral default** so a freshly
attached garment looks exactly as you authored it.

| Attribute | Range | Default (neutral) | Should drive |
|---|---|---|---|
| `fit_tightness` | -1.0 … 1.0 | 0.0 | overall garment toward(+) / away(−) from body (normal-based `push` / lattice — **not** `shrinkWrap`-to-body, see §7) |
| `fit_thickness` | 0.0 … 1.0 | 0.0 | outward push / material thickness |
| `fit_length` | -1.0 … 1.0 | 0.0 | hem / sleeve length (lattice or cluster scale along length) |

### Per-region variants (optional, recommended for complex garments)
Same parameters, scoped to a region: **`fit_<region>_<param>`**, region in lowerCamel.

```
fit_waist_tightness     fit_chest_tightness     fit_hips_tightness
fit_sleeveL_length      fit_sleeveR_length      fit_hem_length
fit_collar_tightness    fit_cuffL_tightness     fit_cuffR_tightness
```

### Rules
- Attributes must be **keyable** and **custom** (user-defined). The tool surfaces keyable custom float
  attrs found on `*_ctrl` nodes in `Ctrl_GRP`, preferring `fit_`-prefixed ones on `cloth_fit_ctrl`.
- **Default = neutral** (no visible change). Moving an attr off default applies your authored fit
  deformation.
- Each attr drives a deformer **inside the asset** via direct connection / SDK / utility nodes (§7).
  The tool never builds this — it only writes the attr value.
- If an asset exposes no `fit_*` attrs, the tool falls back to surfacing whatever keyable custom attrs
  exist on your `*_ctrl` nodes — but please build to the convention above.

### Secondary-motion / animator controls
Coat-tail, skirt, strap controls are separate and follow the existing convention:
`cloth_<name>_ctrl` (e.g. `cloth_coatTail_ctrl`, `cloth_skirtFront_ctrl`). Place under `Ctrl_GRP`.
These remain animator-accessible after attach.

---

## 9. Geometry

- Multiple meshes allowed; **all garment meshes go under `Mesh_GRP`**.
- Mesh naming: `cloth_<part>_mesh` (e.g. `cloth_jacket_mesh`, `cloth_collar_mesh`). (Prefix `cloth_`
  + suffix `_mesh`.)
- **Valid UVs required** on every mesh before export.
- No construction history on the meshes at delivery (delete history; deformers re-applied cleanly).

---

## 10. Hard "no" list

- **Blendshapes / morph targets / corrective shapes** — not supported, anywhere.
- **Simulation** (nCloth / nucleus / any sim).
- **References / namespaces** in the asset file.
- **Unknown nodes, unused materials, animation curves, display layers, extra construction history.**
- Connecting your own asset to `ik_*` or facial joints.
- Renaming or duplicating-and-renaming the body skeleton in a way that breaks the `cloth_` = exact
  body-name rule.

---

## 11. Materials

- **Generic shaders only** (e.g. `lambert` / `standardSurface`). No specialized render shaders, no
  render-engine-specific networks. Materials must survive `.ma` export cleanly.

---

## 12. Version / info node (`cloth_info`)

Each asset must contain a metadata node so the browser and validator can identify and version-check it.

- Create a node named **`cloth_info`** (a `network` node, or a transform parented at asset top level).
- Add these **string** custom attributes:

| Attribute | Example | Meaning |
|---|---|---|
| `assetName` | `"trench_coat_A"` | unique asset name |
| `assetType` | `"coat"` | one of: `shoes` `pants` `shirt` `dress` `coat` `hat` |
| `clothVersion` | `"1.0.0"` | this asset's own version |
| `genHumanCompat` | `"v03"` | supported GenHuman rig version(s); comma-separated if multiple |
| `author` | `"Jane R."` | optional |
| `notes` | `""` | optional |

> The exact GenHuman version string and any **Genie-required node names** are still being finalized by
> the pipeline team (see §15). For now set `genHumanCompat` to the rig version you authored against
> (`v03`) — we'll confirm the canonical value before you ship final assets.

---

## 13. Scene cleanliness

The delivered scene must **not** contain: unknown nodes, references, namespaces, leftover construction
history, unused materials, animation curves, or display layers. Validation hard-stops on any of these.

---

## 14. Transforms & scale

- Match GenHuman world scale **exactly** (same unit settings as the GenHuman pipeline).
- **Freeze scale** (and translate/rotate) on the asset groups and meshes before export: scale = 1,
  clean transform values.
- Do **not** freeze/alter the `cloth_*` joints' orientation (they must mirror the body joints, §4).

---

## 15. Still being finalized by the pipeline team (may change)

These won't block you starting, but flag if they affect your build:

1. **Transform attributes the tool connects** — LOCKED: **translate + rotate + scale** are connected;
   `jointOrient` and `visibility` are **not**. (So: don't rely on joint visibility for anything, and keep
   joints' jointOrient as-duplicated.) **Scale is connected on purpose** — animators scale body joints to
   seat the character into a matchmove, so your `cloth_*` joints will receive non-uniform scale.
   **Build and test for it:** your skinning and fit deformers must deform cleanly when connection joints
   are scaled non-uniformly (scrub a body-joint scale while attached and confirm no collapse/shearing).
2. **Genie-required node names** — the export team may require specific node names present; TBD.
3. **GenHuman version-id string** and **clothing version-compat method** — set `genHumanCompat="v03"`
   for now (§12).
4. **Import vs reference** of assets into the shot — default is **import**; either way your file must be
   self-contained and namespace-free.

The fit-control convention (§8) is **proposed** and pending sign-off, but is stable enough to build to —
if it changes, attr **names** might shift; the rig structure won't.

---

## 16. Pre-delivery validation checklist

Before exporting, confirm:

**Structure**
- [ ] Single top group `cloth_<assetName>` at origin, transforms frozen.
- [ ] Contains `Mesh_GRP`, `Rig_GRP`, `Ctrl_GRP`, and `cloth_info`.
- [ ] Geometry / skeleton / controls cleanly separated.

**Skeleton & naming**
- [ ] Single root joint `cloth_root` (duplicate of `root` at origin) under `Rig_GRP`.
- [ ] Every connection joint = `cloth_` + exact body name (no `_jnt`, trailing `_l`/`_r`).
- [ ] Full parent chain to `cloth_root` present for every skinned joint.
- [ ] Joints' orientation/jointOrient unchanged from duplication.
- [ ] No `ik_*` / facial joints included.
- [ ] Helper joints parented under their `cloth_*` parent, `cloth_`-prefixed.

**Skin & deform**
- [ ] Smooth bind only; skinClusters valid; realtime playback OK.
- [ ] No blendshapes; no simulation.
- [ ] Deformers survive `.ma` export.

**Controls / fit**
- [ ] `cloth_fit_ctrl` present with `fit_*` keyable float attrs, min/max set, neutral defaults.
- [ ] Each fit attr drives an authored deformer (verify by scrubbing each attr).
- [ ] Secondary controls named `cloth_<name>_ctrl`, under `Ctrl_GRP`.

**Geometry & materials**
- [ ] Meshes under `Mesh_GRP`, named `cloth_<part>_mesh`, valid UVs, no history.
- [ ] Generic shaders only; no unused materials.

**Scene & file**
- [ ] No references, namespaces, unknown nodes, anim curves, display layers.
- [ ] Scale frozen (=1), clean transforms.
- [ ] `cloth_info` populated (assetName / assetType / clothVersion / genHumanCompat).
- [ ] Delivered as Maya ASCII (`.ma`).

---

## 17. Authoring workflow (recommended order)

The Publish tab automates the skeleton/skin/prune chores — the order below is the
button sequence, not a manual one.

1. Build garment geometry (UVs, under `Mesh_GRP`, `cloth_<part>_mesh`).
2. Set the **Type**, then **Create cloth skeleton** — rebuilds the canonical `cloth_*`
   skeleton under `Rig_GRP` *and* selects + highlights (green) the recommended skin
   joints for the Type, gathered into `cloth_skin_SET`. (Replaces the manual duplicate /
   rename / pick-influences chore.)
3. Add helper joints for secondary motion (optional).
4. Smooth-bind geometry to the selected (green) joints — Skin ▸ Bind Skin.
5. **Connect test body** — drive the `cloth_*` skeleton from the GenHuman body already
   in the scene; pose the body's controls and confirm the garment deforms. Then
   **Disconnect test body** so the joints go static and the asset is publish-safe.
6. **Delete unused joints** — prune the `cloth_*` joints the garment doesn't skin to
   (safe leaf-only; unweighted interior joints with skinned children are kept).
7. Build control rig + fit deformers; expose `cloth_fit_ctrl` `fit_*` attrs (§8); put
   controls in `Ctrl_GRP`.
8. Add and populate `cloth_info`.
9. Clean the scene; freeze transforms; delete history. Confirm the test body is
   disconnected (Check scene warns if any `cloth_*` joint is still driven).
10. Run the §16 checklist.
11. **Publish ▸** — writes the `.ma` + sidecar + thumbnail into the library.
```
