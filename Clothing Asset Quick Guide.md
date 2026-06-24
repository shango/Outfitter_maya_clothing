# Clothing Asset — Quick Guide (Simple)

**For:** the rigger building clothing for the GenHuman rig
**Make in:** Maya 2026 · **Save as:** Maya ASCII (`.ma`) only

This is the short version. Full details are in `Clothing Asset Authoring Spec.md`.
If the two disagree, the full spec wins.

---

## 1. What the tool does

You build the clothing. You rig it. You skin it. **You finish everything.**

The tool only does **one** thing:
it connects each **body joint** to your **`cloth_` joint** with the same name.

```
   body joint              your joint            your mesh
   spine_03   ──connect──►  cloth_spine_03  ──skin──►  cloth_jacket_mesh
```

That is all. So:

- Your `cloth_` joints must be **copies of the body joints** (same place, same rotation).
- The match is **by name**. One wrong letter = no connection. (Silent. No error.)
- Your **helper joints, controls, and deformers are NOT connected.** They stay free for the animator. Good for coat tails, skirts, straps, and fit.

---

## 2. The 3 most important rules

### ✅ Rule 1 — Joint name = `cloth_` + the EXACT body name

| Body joint | Your joint |
|---|---|
| `spine_03` | `cloth_spine_03` |
| `upperarm_l` | `cloth_upperarm_l` |
| `foot_r` | `cloth_foot_r` |

- ❌ NO `_jnt` at the end.
- ❌ NO `l_` / `r_` at the front. Side is at the **end**: `_l` `_r` (small letters).
- **Best way:** open the GenHuman rig, **duplicate** the joints, then add `cloth_` in front. Do not type names by hand.

### ✅ Rule 2 — Copy the full chain up to the root

Copy the joint you need **and all its parents up to the root.**
Rename the root copy to **`cloth_root`**.

Example for a hat (you still need the whole chain):
```
cloth_root → cloth_pelvis → cloth_spine_01 ... → cloth_neck_01 → cloth_head
```
Do **not** change the joints' rotation or `jointOrient` after you copy them.

### ✅ Rule 3 — 3 groups + 1 info node

```
cloth_<assetName>        ← top group, at origin, transforms frozen (0,0,0 / scale 1)
├── Mesh_GRP             ← only meshes
├── Rig_GRP              ← only joints (under cloth_root)
├── Ctrl_GRP             ← only controls + fit control
└── cloth_info           ← name / type / version
```
Keep mesh, joints, and controls in **separate** groups. Do not add an extra offset group on top.

---

## 3. Fit control (so the tool can show sliders)

Make one control named **`cloth_fit_ctrl`** inside `Ctrl_GRP`.
Add **keyable float** attributes that start with `fit_`. Give each a **min, max, and default = 0** (neutral).

| Attribute | Min … Max | Default |
|---|---|---|
| `fit_tightness` | -1 … 1 | 0 |
| `fit_thickness` | 0 … 1 | 0 |
| `fit_length` | -1 … 1 | 0 |

**You** connect each `fit_` attribute to **your own deformer** (lattice, cluster, push…).
The tool only **moves the slider** = sets the value. It does **not** build the deformer.

At default (0) the clothing must look normal. ✅

---

## 4. DO and DON'T

**DO** ✅
- Smooth bind only.
- Use any deformer **inside** your asset (lattice, cluster, wire, push, deltaMush).
- Valid UVs on every mesh. Mesh name = `cloth_<part>_mesh`.
- Generic shader only (`lambert` / `standardSurface`).
- Freeze transforms. Delete history.

**DON'T** ❌
- ❌ No blendShape / morph / corrective shape. Anywhere.
- ❌ No nCloth / simulation.
- ❌ No `shrinkWrap` to the body (no deformer may use the body mesh).
- ❌ No references, no namespaces, no unknown nodes, no anim curves, no display layers.
- ❌ Do not connect to `ik_*` joints or face joints.

---

## 5. Full example — a coat named `trench_coat_A`

This is a complete, correct asset. Copy this shape.

```
cloth_trench_coat_A                         (top group · at origin · frozen)
│
├── Mesh_GRP
│   ├── cloth_jacket_mesh                    (smooth bound)
│   └── cloth_collar_mesh                    (smooth bound)
│
├── Rig_GRP
│   └── cloth_root                           (copy of body: root)
│       └── cloth_pelvis                     (copy of: pelvis)
│           ├── cloth_spine_01               (copy of: spine_01)
│           │   └── cloth_spine_02           (copy of: spine_02)
│           │       └── cloth_spine_03       (copy of: spine_03)
│           │           ├── cloth_clavicle_l → cloth_upperarm_l → cloth_lowerarm_l
│           │           ├── cloth_clavicle_r → cloth_upperarm_r → cloth_lowerarm_r
│           │           └── cloth_coatTail_01            ← HELPER joint (not connected)
│           │               └── cloth_coatTail_02        ← HELPER joint (not connected)
│           ├── cloth_thigh_l
│           └── cloth_thigh_r
│
├── Ctrl_GRP
│   ├── cloth_fit_ctrl          attrs:  fit_tightness (-1..1=0)
│   │                                   fit_thickness ( 0..1=0)
│   │                                   fit_length    (-1..1=0)
│   └── cloth_coatTail_ctrl     ← animator control for the tail (free after attach)
│
└── cloth_info
        assetName      = "trench_coat_A"
        assetType      = "coat"            (one of: shoes pants shirt dress coat hat)
        clothVersion   = "1.0.0"
        genHumanCompat = "v03"
```

Notes on the example:
- This tree shows the **idea**. The **real** parent of each joint comes from the rig when you **duplicate** it (Rule 1). Trust the rig, not this drawing.
- `cloth_jacket_mesh` and `cloth_collar_mesh` are **smooth bound** to the `cloth_*` joints.
- `cloth_coatTail_01/02` are **helper joints** → the body does NOT drive them → the animator drives them with `cloth_coatTail_ctrl`.
- The arm and leg joints are included because the coat covers them. Shoes would **not** include arm joints.

---

## 6. Final check before you export

- [ ] Top group `cloth_<assetName>` at origin, frozen.
- [ ] Has `Mesh_GRP`, `Rig_GRP`, `Ctrl_GRP`, `cloth_info`.
- [ ] `cloth_root` under `Rig_GRP`. Every joint = `cloth_` + exact body name. No `_jnt`.
- [ ] Full parent chain up to `cloth_root` for every skinned joint.
- [ ] Smooth bind. No blendShape. No simulation. No shrinkWrap-to-body.
- [ ] `cloth_fit_ctrl` has `fit_` attrs with min / max / default 0, and each drives a deformer.
- [ ] Meshes under `Mesh_GRP`, named `cloth_<part>_mesh`, valid UVs, no history.
- [ ] Generic shader only. No references / namespaces / unknown nodes.
- [ ] `cloth_info` filled in.
- [ ] Saved as Maya ASCII (`.ma`).

---

## 7. Work order (easy steps)

1. Build the garment mesh (UVs). Put it in `Mesh_GRP`.
2. Open GenHuman rig → duplicate the joints you need + their parents → rename to `cloth_*` → make `cloth_root`. Put in `Rig_GRP`.
3. Add helper joints for tails / skirt / straps.
4. Smooth bind the mesh to the joints.
5. Build your controls + fit deformers. Make `cloth_fit_ctrl` with `fit_` attrs. Put in `Ctrl_GRP`.
6. Make `cloth_info` and fill it.
7. Clean scene. Freeze transforms. Delete history.
8. Check the list in part 6.
9. Save `.ma` → give to the Outfitter tool.

**Remember:** name = `cloth_` + exact body name. This is the most important thing. ✅
