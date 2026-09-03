# MichaelC rig - Outfitter onboarding handoff

Working record for bringing the MichaelC rig into the Outfitter rig repo.
Session date: 2026-09-02. Sibling to `HANDOFF.md` (the rig-agnostic tool work).

## Where things stand

**Rig file: `MichaelC_rig_01.6.ma`** - written this session by text surgery on 01.5.
All *structural* Outfitter-readiness work is done. It has **not been opened in Maya**;
that is the one outstanding verification. `01.5` is kept as the pre-surgery source, and
`01.3` / `01.4` are the two earlier (unskinned) drops.

**Outfitter code: v1.2.1**, branch `fix/maya-boundary-nameerrors`, pushed to origin.
Not merged into master. `git checkout master && git merge --ff-only
fix/maya-boundary-nameerrors && git push` when ready - master is a strict ancestor, so it
is a clean fast-forward. 354 tests passing.

**Decided 2026-09-02: Daniel will NOT be registered into Outfitter. MichaelC will.**
So the registered rig set becomes GenHuman (bundled) + MichaelC. Nothing about Daniel needs
fixing - see "Daniel comparison" below for what was found and is deliberately being left.

**Work order for the two artists** (rigging lane + skin-weights lane):
https://claude.ai/code/artifact/0851a776-5c1e-48f7-9f9a-c75d460fe43d

## What the rig is

Hive 1.4.25 (Zoo Tools), UE5 naming preset, Maya 2026, cm/degrees. No references, no
namespaces, no unknown nodes; only `matrixNodes` and `quatNodes` required.

* **Export skeleton**: 89 joints under `MichaelC_Joint_GRP`, driven by 89 parentConstraints
  + 88 scaleConstraints off the Hive deform layer (`MichaelC_deformLayer_hrc`, 87 joints).
  Same dual-skeleton shape as GenHuman.
* **Joint names match GenHuman's 89 exactly** - `GM_foot_L`/`GM_foot_R`, `interaction`,
  `center_of_mass` included. `derive_skin_sets` therefore reproduces GenHuman's sets
  (8/18/24/36/36/1 for shoes/pants/shirt/dress/coat/hat) with no hand-editing.
* **Single body**: no morph or gender attribute anywhere. Registers `variants.mode = "none"`;
  its garments publish `gender: none`.
* **Proportions differ from GenHuman** - head +6.9 cm, `spine_05` +11.1, `clavicle_l` +8.9,
  pelvis +2.9, median joint delta ~8.7 cm (measured from `.bps` bind matrices). GenHuman
  garments retarget by name but need a real refit.
* **The `-90 X` sits on `root.jointOrient`**, not on the export group the way GenHuman does
  it. Both round-trip correctly (`capture_skeleton_spec` reads `root_group_rotate` off the
  group and `jointOrient` per joint; `build_cloth_skeleton` writes `jointOrient` back).
  **Do not "fix" this to match GenHuman** - no benefit, and it invalidates any captured profile.

Simulated registration passes: `rigs.validate_profile` returns no errors,
`MichaelC_Joint_GRP` is the top-ranked export-group candidate (89 joints), and all four
landmark short names are unique in the scene.

## What 01.6 changed vs 01.5

10.07 MB -> 8.49 MB; 142,557 -> 117,945 lines. 8 node blocks and 183 connections removed,
3 transforms added.

**Removed**: `PAO_Skeleton_CNT`, `Hive_Solver_CNT` (the second was black-boxed; between them
they contained both skeletons, and container contents are restricted so Outfitter could not
read or connect to the joints), their `hyperLayout1`/`hyperLayout2` member lists,
`BodyShapeOrig2` (orphan intermediate shape, ~20% of the file, different topology from the
live original), and `groupParts1`/`groupId1`/`groupId2` (pre-bind leftovers).

**Renamed**: `Skeleton` -> `MichaelC_Joint_GRP`, `Geo` -> `MichaelC_Mesh_GRP`,
`Body` -> `MichaelC_body_mesh` (+ shapes), and all 637 `Michael_Hive2_*` nodes -> `MichaelC_*`.
The landmark renames matter: `maya_skeleton._find_export_root` resolves the export group by
*short name* across the whole scene and takes the first match, and the same names become the
profile's `markers`. `Skeleton` / `Geo` / `Body` would collide with a garment scene.
**Nobody should rename these back.**

**Rewired**: `skinCluster2.outputGeometry[0]` -> `MichaelC_body_meshShape.inMesh`, direct.

**Added**: `MichaelC_info_GRP` with `MichaelC_rig_v01_6` / `MichaelC_rig_Maya2026`.

### Verification done (headless only)

`tools/michaelc/verify_016.py` plus ad-hoc checks, all passing: DAG parents resolve *and*
are created before their children (3,489 nodes); 18,107 connectAttr endpoints with zero
dangling; no residual references to removed nodes; quotes balanced in every statement; file
trailer intact; skin chain and 89 influences intact; node-type deltas exactly the intended
ones (container -2, hyperLayout -2, mesh -1, groupId -2, groupParts -1, transform +3);
display-layer connection accounting exact (3 -> 2, the dropped one being the deleted shape).

**Not verified: that Maya loads it.** Do this before it goes in the shared rig repo.

## Outstanding work

Full detail, with vertex IDs and weight figures, is in the artifact linked above. Summary:

### Lane R - rigging (5 items, none are weights)

| | Item | Kind |
|---|---|---|
| R1 | ~~Rig at bind pose~~ **CLOSED 2026-09-03**: user confirms current pose is bind pose, and all 213 controls verified at default. Nothing to zero | Done |
| R2 | ~~Pick one skinning method~~ **DONE 2026-09-03**: `skinningMethod` set 2 -> 0 in 01.6. Rigger only needs to keep it at 0 when rebinding | Done |
| R3 | Set the real influence budget (`maxInfluences` says 3, peak is 8, 824 verts over 4) | Decision |
| R4 | Five duplicate `spine_m_01..05_anim_spaceorientSpace` node names | Nuisance |
| R5 | Known and deliberately left: empty `MichaelC_geo_hrc` / `MichaelC_Anatomical_Bone_Contour_GRP`, locked `UsdDefaultRenderSettings`, Hive body-guide viz | No action |

### W5 withdrawn 2026-09-03 - a parser artifact, verified against Maya

**Every one of the 5,280 vertices sums to exactly 1.0.** W5 claimed eight carried only trace
weight and needed hand-repainting; they do not. v859, described as "a right-side vertex whose
only trace weight is on the left thigh", is **91.9% `calf_r`** and sits at X = -18.81, the same
side as `thigh_r` (X = -11.04). v4055, "a shoulder vertex with its only weight on the left
forearm twist", is 86.5% `lowerarm_l`, 6.4 units away.

Cause: `tools/michaelc/wt.py` mis-parsed the chunked `.wl` blocks. Maya writes them as
`setAttr ".wl[a:b].w"` runs whose declared ranges *overlap* at the boundary - `[67:151]` is
followed by `[151:237]` - and the parser reset its vertex counter at each chunk, truncating
whichever vertex straddled the split. Per-joint **totals** were unaffected, because sums are
order-independent. That is precisely why W2/W3/W4 were right and W5 was not, and why the error
was invisible until Maya could be asked. `wt.py` is deleted; see `tools/michaelc/README.md`.

The "W6 last, always" rule goes with it - there is no under-weighting evidence left to erase.

### What survives, all confirmed against `MFnSkinCluster` on 2026-09-03

| | Finding | Status |
|---|---|---|
| W2 | `ball_l` 0.000 over 0 verts; `ball_r` 41.893 over 339, max 0.4961; 144 left verts above 0.99 on `GM_foot_L` | **real** |
| W3 | all four `calf_twist_*` exactly 0.000 over 0 verts | **real** |
| W4 | `thigh_twist_01_l` 0.678 over 13 verts vs `thigh_l` 136.636 over 575 | **real** |
| W6 | prune only: peak 12 influences, 2,218 verts over 4 (831 above 0.0001) | **real, halved** |
| R3 | `maxInfluences` 3, `maintainMaxInfluences` off, real peak 12 | **real** |
| R4 | all five spine space-switch names resolve to 2 nodes each; the export group's 89 stay unique | **real** |
| W1 | no deformer set | withdrawn |
| W5 | eight under-weighted vertices | withdrawn |

### W1 withdrawn 2026-09-03 - it was never a real defect

**`skinCluster2` is fine. W1 has been deleted from the work order, not downgraded.**

The claim was that the cluster lacks a deformer `objectSet`, so Paint Skin Weights would not
open and `deformer -q -g` would return nothing. Verified against a real Maya 2026 via
`mayapy`, every part of that is wrong:

* A **textbook `Skin > Bind Skin` in an empty scene** produces the identical signature -
  no `objectSet` connection, no `.message` consumer, no `groupId`, no `groupParts`. Maya 2026
  simply does not build that plumbing for skinClusters any more. The diagnosis was looking for
  nodes modern Maya never creates.
* `deformer -q -g` **returns** `MichaelC_body_meshShape`.
* `deformerWeights -export` writes a 906 KB file. `skinPercent` reads *and writes*.
  `skinCluster -e -forceNormalizeWeights` runs. `findRelatedSkinCluster` resolves to
  `skinCluster2`, which is how Paint Skin Weights bootstraps.
* An FBX round-trip carries all **89 influences** through with weights intact, so the engine
  path was never at risk either.

**Consequences:** the weights artist is unblocked immediately - W2-W5 need nothing first.
The ordering constraints collapse to just "R3 before W6, and W6 last". `examples/rebind_michaelc.py`
has been deleted rather than kept: it solved a non-problem, and leaving it invited a
destructive rebind for no reason.

This also retroactively justifies removing `groupId1`/`groupId2`/`groupParts1` in 01.6 - those
genuinely were dead nodes, since modern binds do not use them.

### 01.6 confirmed to load in Maya, 2026-09-03

Opened headlessly in `mayapy` 2026: **3,526 nodes, no errors.** All four landmarks resolve,
`skinningMethod` reads back 0, and the mesh is confirmed **at bind pose** - the live shape
deviates from the intermediate original by 2.39e-07 at worst. Two nodes come in as `unknown`
(`UsdDefaultRenderSettings`, `hyperShadePrimaryNodeEditorSavedTabsInfo`); both are cosmetic
scene-state nodes and both resolve when their plugins load. **Do not save the scene from a
session where they are unknown** - that is the one way to lose them.

### R1 closed 2026-09-03 - the rig is already zeroed

The user confirms the saved pose is the bind pose. Verified against the file, and the earlier
phrasing "only 2 controls off default" was wrong in a way worth recording:

* **All 213 animation controls are at default.** Defining a control properly - a transform carrying
  a `nurbsCurve` shape - **zero** of them deviate from `t=0, r=0, s=1`.
* **`leg_[lr]_primaryLegIkDistanceEnd_anim` are not controls.** They are bare `transform` nodes with
  *no shape at all*, whose `.worldMatrix` feeds `leg_[lr]_startEnd_dist` and `leg_[lr]_endPv_dist`,
  both `distanceBetween` nodes. They are the measuring end of the leg IK stretch, parented under
  `MichaelC_leg_[lr]_ball_ik_anim`, and their offsets are the measured geometry.
  **Zeroing them would break leg IK stretch and pole-vector behaviour.** Do not touch them.
* The other 43 off-default transforms are all rig machinery, never poses: `*_ik_jnt` (bone lengths),
  `*_ikhandle` (solver placement), `*_in` (rig input plugs), `*RoundAimTarget_target` (unit aim
  vectors at exactly +/-1), `*_srtTwistServer_jnt` (twist bone lengths), `SCALE_PROXY`,
  `Head_Reference_Wire_GRP`. The `_srt` and `_spaceorientSpace` nodes excluded above are offset
  groups that place the rig in space; zeroing those would collapse it to the origin.

**Limit of this check:** the export skeleton's joints carry *no* static `.t`/`.r` in the file - they
are `parentConstraint`-driven off the deform layer - so "current world pose equals bind pose" cannot
be evaluated headlessly. Every control sitting at default is the strongest available file-side
evidence, and it agrees with the user's statement. Each joint's `.bps` bind matrix is intact and
readable (`head` at Y = 169.43) if it ever needs checking in Maya.

R2 needs restating, because `skinningMethod` 2 is not dual quaternion. It is Maya's
*weighted blend* mode, in which a per-vertex `blendWeights` array (0 = linear, 1 = DQ) mixes the
two. **That array was never authored - it is absent from the .ma entirely** - so every vertex sits
at the default and the mesh deforms as classic linear inside a mode that claims to blend.

Weighted blend is the wrong answer for this pipeline regardless of taste: a garment author can
match a single setting, but not a per-vertex blend map that would have to be transferred onto every
garment, and FBX to UE5 does not carry the map. So set `skinningMethod` explicitly to 0 or 1.
Choosing 0 matches how the mesh already behaves and changes nothing visually. Choosing 1 is a real
quality gain at twists, but note the rig already has twist joints for exactly that problem - once
W3/W4 weight them, classic linear is adequate and is the engine-friendly pick. Whichever is chosen
goes into `Clothing Asset Authoring Spec.md`, or garments bind classic linear by default and deform
differently against the body at the same joints.

**Resolved 2026-09-03**: `skinningMethod` is now **0** in `MichaelC_rig_01.6.ma` (single edit at
line 57100, `".skm" 2;` -> `".skm" 0;`). Deformation is bit-identical, because weighted blend with
an unauthored `blendWeights` array already computed pure linear. Verified: file diff is that one
line, byte count unchanged, `verify_016.py` reports the same clean result, and the weight
distribution is untouched (5,253 verts at 1.0 / 19 partial / 8 near-zero).

Two things this does **not** settle, both still on the rigger:

* **The W1 rebind must specify it.** Detach-and-rebind creates a *new* skinCluster and this
  attribute does not survive. Bind with `-skinMethod 0` (or set it again afterwards).
* **`Clothing Asset Authoring Spec.md` still needs the line**, so garment authors bind linear
  deliberately rather than by coincidence of Maya's default.

### Lane W - skin weights (6 items)

| | Item | Kind |
|---|---|---|
| W2 | `ball_l` at zero - the left toe is 99% ankle while the right is a proper ankle/ball blend across 286 verts. Mirror right -> left below the knee | Blocking |
| W3 | All four `calf_twist_*` at exactly zero, both sides | Blocking |
| W4 | `thigh_twist_*` negligible (9 and 4 verts against ~460 on the parent thigh) | Quality |
| W6 | Prune to R3's budget. The `forceNormalizeWeights` half is a no-op - every vertex already sums to 1.0 | Quality |

W2/W3/W4 matter to Outfitter specifically: those joints are in the recommended skin sets the
tool hands a garment rigger, so a garment deforms correctly while the body under it does not,
and it reads as an Outfitter bug.

### Ordering constraints (the lanes are not independent)

Only one constraint survives: **R3 before W6**, because W6 prunes to the budget R3 sets.
W2, W3 and W4 can start immediately and in any order.

Also: Outfitter captures the skeleton at the rig's **current scene pose**, so the rig must be
at bind/rest when Register rig runs.

## Tooling written this session

* `examples/prep_michaelc_rig.py` - in-Maya prep pass. Idempotent: against 01.6 the structural
  passes report "already done" and it does the weight audit + normalize. Dry run by default
  (`p.prep()`), `p.prep(apply=True)` to act. Run it against 01.5 and it performs the structural
  work too, so it is the fallback if 01.6 is ever mistrusted.
* `tests/test_maya_boundary_names.py` - AST undefined-name check over `core/maya_*.py` and
  `examples/*.py`, the modules CI can only `py_compile`. Both bugs fixed this session were of
  exactly that class. Verified non-vacuous against re-introduced copies of both.
* `tools/michaelc/` - headless, already run, kept for provenance:
  `make_016.py` (01.5 -> 01.6 transform, the authoritative recipe), `verify_016.py`
  (referential-integrity check), `dag2.py` (full-DAG-path .ma parser - short names are not
  unique in this rig), `wt.py` (vertex positions + skin weights out of a .ma), `wpos.py`
  (world joint positions from local transforms).

## Bugs fixed in the tool (in `84e9b1f`)

* `core/maya_skeleton.py` `capture_cloth_skeleton_from_rig` returned `len(joints)`, a local of
  a *different* function. The Publish tab's 'Regenerate skeleton' button did all its work,
  wrote the profile, then raised `NameError`.
* `core/skeleton.py` `write_skeleton` referenced `Path`, `json`, `skeleton_file` and
  `load_cloth_skeleton`, none of which exist there. Dead since rig-agnosticism moved skeleton
  persistence into `rigs.write_profile`; removed rather than repaired.

## Daniel comparison (for context; no action)

Measured against `Daniel_rig_v03-RENAMED.ma`, since both derive from the same export
contract:

* **Export skeletons are identical** across Daniel, MichaelC and GenHuman - same 89 joints,
  same names, same parent-child hierarchy. Only difference is each root's parent (its own
  export group). Child creation order differs (Daniel emits `clavicle_l` first, MichaelC
  `clavicle_r`), which Outfitter does not care about.
* **Proportions differ**, from the `.bps` bind matrices:

  | Pair | Median | Max |
  |---|---|---|
  | Daniel ↔ GenHuman | 2.48 cm | 3.58 cm |
  | MichaelC ↔ Daniel | 6.82 cm | 10.62 cm |
  | MichaelC ↔ GenHuman | 8.71 cm | 11.21 cm |

  Daniel is GenHuman-sized; MichaelC is a distinctly bigger character. **Consequence for the
  library:** existing GenHuman garments retarget onto MichaelC by *exact name* (no
  `jointAliases`, no role heuristic) and `moveJointsMode` preserves the weights - but every
  one needs a real refit afterwards. Retarget converts the binding, never the shape.
* Daniel also differs structurally: mesh group named `Mesh_GRP`, `Daniel_Body_morph`
  (gendered, so its garments carry male/female where MichaelC's carry `gender: none`), a
  230-joint deform layer including a `mouth_M` face rig, and 14 skinClusters. It is *not* a
  pure rename of GenHuman whatever `genhuman_to_daniel_rename.json` implies.
* **Known and deliberately unfixed:** Daniel's mesh group is literally `Mesh_GRP`, which is
  `config.MESH_GROUP` - the name a *garment* must use. With Daniel in a scene,
  `scaffold_asset_groups` sees it already exists, skips creating the garment's own, and
  reports "already in place"; a garment mesh parented under it would be deleted along with
  the rig. Moot while Daniel stays unregistered. If that ever changes, the fix is the same
  one-line rename applied to MichaelC, using `tools/michaelc/make_016.py` as the template.

## Blocking on the Setup tab, before registering

`scripts/path.txt` currently reads:

```
local = \\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\maya_clothing_rig\assets
```

Two problems: that path uses the repo's **old** name (this repo is
`Outfitter_maya_clothing`), and **no remote is configured**. Registration writes the profile
to the remote first - that is the copy other artists fetch - so with no remote set, MichaelC
registers on this machine only and reaches nobody. Fix both on the Setup tab first.

## Next steps

1. Open `MichaelC_rig_01.6.ma` in Maya, confirm it loads with no script-editor errors.
   (Never yet verified in Maya - the only outstanding check on the file itself.)
2. Fix the local path and set a remote on the Setup tab (see above).
3. Hand the artifact to the two artists; R2/R3 decisions first.
4. On completion: save as `MichaelC_rig_01.7.ma`, run `p.prep()` for a clean audit, then
   Publish tab > **Register rig...** with export group `MichaelC_Joint_GRP` and the
   body-variant switch left empty.
5. Merge `fix/maya-boundary-nameerrors` into master.
