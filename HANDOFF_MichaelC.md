# MichaelC rig - Outfitter onboarding handoff

Working record for bringing the MichaelC rig into the Outfitter rig repo.
Session date: 2026-09-02. Sibling to `HANDOFF.md` (the rig-agnostic tool work).

## Where things stand

**Rig file: `MichaelC_rig_01.6.ma`** - written this session by text surgery on 01.5.
All *structural* Outfitter-readiness work is done. It has **not been opened in Maya**;
that is the one outstanding verification. `01.5` is kept as the pre-surgery source, and
`01.3` / `01.4` are the two earlier (unskinned) drops.

**Outfitter code: v1.2.1**, commit `84e9b1f` on branch `fix/maya-boundary-nameerrors`.
Not merged. `git checkout master && git merge --ff-only fix/maya-boundary-nameerrors`
when ready. 354 tests passing.

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
| R1 | Rig at bind pose; confirm `leg_[lr]_primaryLegIkDistanceEnd_anim` are by-design measure locators (only 2 controls off default) | Blocking |
| R2 | Decide dual quaternion vs classic linear (`skinningMethod` is 2) | Decision |
| R3 | Set the real influence budget (`maxInfluences` says 3, peak is 8, 824 verts over 4) | Decision |
| R4 | Five duplicate `spine_m_01..05_anim_spaceorientSpace` node names | Nuisance |
| R5 | Known and deliberately left: empty `MichaelC_geo_hrc` / `MichaelC_Anatomical_Bone_Contour_GRP`, locked `UsdDefaultRenderSettings`, Hive body-guide viz | No action |

R2 has a knock-on outside this rig: if DQ stays, it must go into
`Clothing Asset Authoring Spec.md`, or garments bind classic linear by default and deform
differently against the body at the same joints.

### Lane W - skin weights (6 items)

| | Item | Kind |
|---|---|---|
| W1 | Rebind so the deformer set exists (`skinCluster2` has none - Paint Skin Weights won't open, `deformer -q -g` returns nothing). **Plumbing, not weights** | Blocking |
| W2 | `ball_l` at zero - the left toe is 99% ankle while the right is a proper ankle/ball blend across 286 verts. Mirror right -> left below the knee | Blocking |
| W3 | All four `calf_twist_*` at exactly zero, both sides | Blocking |
| W4 | `thigh_twist_*` negligible (9 and 4 verts against ~460 on the parent thigh) | Quality |
| W5 | Eight vertices repainted by hand: `859, 1183, 1304, 2980, 3349, 3907, 4055, 4979` | Blocking |
| W6 | Prune to R3's budget, then `skinCluster -e -forceNormalizeWeights` | Quality |

W2/W3/W4 matter to Outfitter specifically: those joints are in the recommended skin sets the
tool hands a garment rigger, so a garment deforms correctly while the body under it does not,
and it reads as an Outfitter bug.

On W5: 859 and 2980 sum to zero (859 is a *right*-side vertex whose only trace weight is on
the *left* thigh - corrupted, not thin). The other six carry only trace weight, and
normalizing would hand each entirely to whatever holds the trace - 4055 sits at shoulder
height with its only weight on the left forearm twist. **Normalizing is the wrong fix for
all eight.**

### Ordering constraints (the lanes are not independent)

1. **R2 and R3 before W1** - the rebind sets the skinning method, and pruning is a weight edit.
2. **R1 before W1** - the mesh has to be rebound at bind pose.
3. **W1 before W2-W5** - Maya's weight tools don't work on this mesh until the deformer set exists.
4. **W6 last, always** - normalizing makes every vertex sum to 1 and erases the evidence for
   everything above it.

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

## Next steps

1. Open `MichaelC_rig_01.6.ma` in Maya, confirm it loads with no script-editor errors.
2. Hand the artifact to the two artists; R2/R3 decisions first.
3. On completion: save as `MichaelC_rig_01.7.ma`, run `p.prep()` for a clean audit, then
   Publish tab > **Register rig...** with export group `MichaelC_Joint_GRP` and the
   body-variant switch left empty.
4. Merge `fix/maya-boundary-nameerrors` into master.
