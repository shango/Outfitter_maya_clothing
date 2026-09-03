# MichaelC rig - Outfitter onboarding handoff

Working record for bringing the MichaelC rig into the Outfitter rig repo.
Sessions: 2026-09-02 (onboarding) and 2026-09-03 (verification against a real Maya).
Sibling to `HANDOFF.md` (the rig-agnostic tool work).

## Where things stand

**Rig file: `MichaelC_rig_01.8.ma`** - written by text surgery on 01.7, which was itself
text surgery on 01.6, itself text surgery on 01.5. **Every item in the work order has now
been applied and verified in Maya**: the structural work in 01.6, and R3/R4/W2/W3/W4/W6 in
01.7. See "01.7: the whole work order, applied" below. 01.8 changes exactly two lines - it
hides the body-guide layer (see "01.8: the guide layer off the controls"). `01.7` is kept as
the last guide-visible build, `01.6` as the pre-weights source, `01.5` as the pre-surgery
source, `01.3` / `01.4` are the two earlier (unskinned) drops.

**Outfitter code: v1.2.1**, branch `fix/maya-boundary-nameerrors`, pushed to origin.
Not merged into master. `git checkout master && git merge --ff-only
fix/maya-boundary-nameerrors && git push` when ready - master is a strict ancestor, so it
is a clean fast-forward. 354 tests passing.

**Decided 2026-09-02: Daniel will NOT be registered into Outfitter. MichaelC will.**
So the registered rig set becomes GenHuman (bundled) + MichaelC. Nothing about Daniel needs
fixing - see "Daniel comparison" below for what was found and is deliberately being left.

**Work order** (now a record of what was applied, not a task list):
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

**Since confirmed in Maya**: 01.6 opens with 3,526 nodes and no errors, and 01.7 (below)
opens with the same count.

## 01.8: the guide layer off the controls

Reported from the viewport as "an extra clavicle control". There is no extra control. The
clavicle component has exactly one control per side in every drop, and no node named
`MichaelC_clavicle_l_00_anim1` has ever existed in 01.3 through 01.7 - Maya generates that
`1` suffix on a `Ctrl+D` duplicate, so a node by that literal name lives in someone's working
scene, not in a delivered file.

What is real, and what a click at the clavicle actually finds:

```
MichaelC_BODY_clavicle_l_JOINT_MARKER_CRV   dist 0.000 from MichaelC_clavicle_l_00_anim
```

Distance zero, visible, `displayType 0` (normal, not reference), so it is selectable and it
draws on top of the control. It is not one stray curve either - **all 31** joint markers on
`MichaelC_BODY_GUIDE_LYR` sit exactly on an animation control:

| marker | control it covers |
|---|---|
| `clavicle_l` / `clavicle_r` | `MichaelC_clavicle_*_00_anim` |
| `shoulder_l` / `shoulder_r` | `MichaelC_arm_*_shldr_ik_anim` |
| `elbow_*`, `knee_*` | the `bendy01_bendy_anim` controls |
| `wrist_*`, `forearm_end_*` | `MichaelC_arm_*_hand_fk_anim` |
| `ankle_*`, `ball_*` | `MichaelC_leg_*_foot_fk_anim`, `*_ball_fk_anim` |
| `hip_l` / `hip_r` | `MichaelC_leg_*_hip_ik_anim` |
| `spine_01`..`spine_05`, `pelvis_center` | the spine controls and `spine_m_gimbal_anim` |
| `neck_base`, `neck_top`, `head` | the neck and head controls |
| `palm_*`, `middle_finger_tip_*` | `MichaelC_middle_*_metacarpal_anim`, `*_03_anim` |

**Fix applied in 01.8:** `setAttr "MichaelC_BODY_GUIDE_LYR.v" no;`, written the same way
`MichaelC_JNT_LAYER` is already written. Nothing is deleted - the guide comes back by turning
the layer on in the Display Layer editor. This is item 4 of the animation next steps, now
closed for the markers.

Still on: `MichaelC_god_m_godnode_anim.bodyJointLineVis` and `.toggleHeadWire`. Those are
animator-facing toggles on the god node rather than layer state, so they were left for whoever
sets the delivery default. There is no equivalent toggle for the markers, which is why the
layer was the only lever.

`verify_016.py MichaelC_rig_01.7.ma MichaelC_rig_01.8.ma`: 3,404 nodes and 18,107 connections
unchanged, the only node delta the version stamp. Reloaded in Maya: 3,526 nodes, both unknown
nodes present and not duplicated, `skm=0 mi=4 mmi=True`, 89 influences, guide layer `vis=False`
with its 172 members intact, every control still visible and selectable. `diff` between the two
files is two lines.

## 01.7: the whole work order, applied

Written 2026-09-03 by `tools/michaelc/weights_017.py` (computes) + `make_017.py` (splices).
8.49 MB -> 8.37 MB. Reloaded in Maya and checked: **3,526 nodes** (unchanged), both unknown
nodes still present and not duplicated, `skinningMethod` 0, `maxInfluences` 4,
`maintainMaxInfluences` on, all 5,280 vertices sum to 1.0, **peak 4 influences**, mesh still
at bind pose (4.8e-07 cm), 89 export joints, landmarks unique. The weights read back out of
the `.ma` match Maya's computed array to **1.4e-20** - the splice is bit-exact.
`verify_016.py MichaelC_rig_01.6.ma MichaelC_rig_01.7.ma` is clean: 18,107 connections
unchanged, every parent and endpoint resolves, node delta exactly the five R4 renames.

| | What was done | Evidence |
|---|---|---|
| R3 | `maxInfluences` 3 -> **4**, `maintainMaxInfluences` **on** | 4 was measured, not chosen: pruning the original weights to 4 moved 57 verts by at most 0.31 cm. To 8 it is exactly free, to 6 it is 0.01 cm. 4 is the portable answer and it costs nothing |
| R4 | The five duplicated `spine_m_0N_anim_spaceorientSpace` names resolved | The copy under `spine_m_world_in` renamed to `..._in`; 15 full-path `connectAttr` references rewritten. Both orient-constraint targets still resolve. Scene duplicate short names 90 -> 85 |
| W2 | `ball_l` 0.000 -> **41.498 over 342 verts**, against `ball_r`'s 41.893 over 340 | Each left foot vertex's own `GM_foot_L + ball_l` total was re-split using the ratio its mirror partner uses on the right. The foot is mirror-exact: worst partner distance **0.087 cm**, median 0.000 |
| W3 | All four `calf_twist_*` 0.000 -> **73-77** (twist_01) and **51** (twist_02) per side | See "the twist model" below |
| W4 | `thigh_twist_01_*` 0.68 -> **55.6/58.2**, `thigh_twist_02_*` 0.20 -> **39.5/39.9** | same |
| W6 | Pruned to 4 and renormalized: 2,469 verts trimmed, influence histogram now `1:752 2:114 3:960 4:3454` | Prune-only cost, measured against the post-twist weights in an aggressive FK leg pose: max 0.66 cm, p99 0.13 cm, 690 verts. Zero at bind pose |

**Deformation change overall**, W2+W3+W4+W6 together, measured in a pose that twists both
legs in FK and both arms: max 4.36 cm, p99 2.98 cm, 800 verts moved. **Zero at bind pose.**
That 4.36 cm is the fix working - the leg used to twist rigidly and now interpolates.

### The twist model, measured rather than assumed

The twist joints were never dead; they were driven correctly and simply carried no weight.
Rotating a control and reading each twist joint's rotation relative to its parent:

* **Calf twists are distal** - they carry `u x (ankle twist)`. `calf_twist_02_l` sits at
  u = 0.365 along knee -> ankle, `calf_twist_01_l` at u = 0.729. Rotating
  `MichaelC_leg_l_foot_ik_anim` gave them 8.624 deg and 17.253 deg, a ratio of 2.000 against
  the positional ratio of 1.997.
* **Thigh twists are proximal** - they carry `(1-u) x (hip twist)`. `thigh_twist_01_l` at
  u = 0.331, `thigh_twist_02_l` at u = 0.662. Rotating `MichaelC_leg_l_thigh_fk_anim` 50 deg
  gave -16.966 deg and -8.483 deg: ratio exactly 2.000, and the joint nearer the hip counters
  more. (The leg defaults to IK, so the FK controls do nothing until `.ikfk` is set to 1 -
  that is why an earlier sweep found only IK controls driving anything.)

So each vertex's parent-bone weight was split between the two twist nodes bracketing its own
u, which is exactly linear twist interpolation and exactly what the rig computes. Bending is
unaffected: the twist joints are children of the parent bone and inherit its bend.

This is a procedural falloff, not a painted one. It is correct in the sense that it matches
the rig's own twist math, and it is what a rigger would paint as a starting point, but the
shape of the falloff near the knee and ankle is a taste call that a human should look at.

### Not done: the arms have the same defect

Not in the work order, so not fixed, but found while measuring. The arm twists are weighted
too lightly by the same margin the legs were:

| joint | total | against |
|---|---|---|
| `lowerarm_twist_01_l` (distal) | 4.207 | `lowerarm_l` 168.831 |
| `lowerarm_twist_02_l` (proximal) | 0.044 | same |
| `upperarm_twist_01_l` (proximal) | 0.810 | `upperarm_l` 227.943 |
| `upperarm_twist_02_l` (distal) | 0.385 | same |

A linear split would give each twist joint roughly a third of its parent's weight, the way
the legs now have. They escaped the work order only because they are not *exactly* zero.
`weights_017.py`'s `redistribute()` handles them unchanged - it takes the parent joint, the
two ends of the bone, and the twist nodes with their u parameters.

### Lane R - the rest

| | Item | Kind |
|---|---|---|
| R1 | ~~Rig at bind pose~~ **CLOSED**: user confirms current pose is bind pose, all 213 controls verified at default. Nothing to zero | Done |
| R2 | ~~Pick one skinning method~~ **DONE**: `skinningMethod` set 2 -> 0 in 01.6 | Done |
| R5 | Known and deliberately left: empty `MichaelC_geo_hrc` / `MichaelC_Anatomical_Bone_Contour_GRP`, locked `UsdDefaultRenderSettings`, Hive body-guide viz | No action |

### W1 and W5 were withdrawn 2026-09-03 - neither was a real defect

**W1** claimed `skinCluster2` lacks a deformer `objectSet`, so Paint Skin Weights would not
open. A **textbook `Skin > Bind Skin` in an empty scene** produces the identical signature:
Maya 2026 does not build that plumbing for skinClusters any more. `deformer -q -g` returns
`MichaelC_body_meshShape`, `deformerWeights -export` writes a 906 KB file, `skinPercent`
reads and writes, `findRelatedSkinCluster` resolves. This also retroactively justifies
removing `groupId1`/`groupId2`/`groupParts1` in 01.6 - those really were dead.

**W5** claimed eight vertices carried only trace weight. **Every one of the 5,280 vertices
sums to exactly 1.0.** The cause was `tools/michaelc/wt.py` mis-parsing the chunked `.wl`
blocks, whose declared ranges overlap at the boundary (`[67:151]` then `[151:237]`); the
parser reset its vertex counter at each chunk and truncated whichever vertex straddled the
split. Per-joint *totals* were unaffected, because sums are order-independent - which is
exactly why W2/W3/W4 were right and W5 was not. `wt.py` is deleted; see
`tools/michaelc/README.md`.

### R1 closed - the rig is already zeroed

The user confirms the saved pose is the bind pose, and the earlier phrasing "only 2 controls
off default" was wrong in a way worth recording:

* **All 213 animation controls are at default.** Defining a control properly - a transform
  carrying a `nurbsCurve` shape - **zero** of them deviate from `t=0, r=0, s=1`.
* **`leg_[lr]_primaryLegIkDistanceEnd_anim` are not controls.** They are bare `transform`
  nodes with *no shape*, whose `.worldMatrix` feeds `leg_[lr]_startEnd_dist` and
  `leg_[lr]_endPv_dist`, both `distanceBetween` nodes. They are the measuring end of the leg
  IK stretch and their offsets are the measured geometry. **Zeroing them would break leg IK
  stretch and pole-vector behaviour.** Do not touch them.
* The other 43 off-default transforms are all rig machinery, never poses: `*_ik_jnt`,
  `*_ikhandle`, `*_in`, `*RoundAimTarget_target`, `*_srtTwistServer_jnt`, `SCALE_PROXY`,
  `Head_Reference_Wire_GRP`. The `_srt` and `_spaceorientSpace` nodes are offset groups that
  place the rig in space; zeroing those would collapse it to the origin.

### R2, restated - `skinningMethod` 2 was never dual quaternion

It is Maya's *weighted blend* mode, in which a per-vertex `blendWeights` array (0 = linear,
1 = DQ) mixes the two. **That array was never authored** - absent from the `.ma` entirely -
so every vertex sat at the default and the mesh deformed as classic linear inside a mode that
claimed to blend. Weighted blend is wrong for this pipeline regardless of taste: a garment
author can match a single setting, but not a per-vertex blend map, and FBX to UE5 does not
carry it. Set to **0** in 01.6; deformation was bit-identical, because weighted blend with an
unauthored `blendWeights` array already computed pure linear.

Garments must therefore bind **classic linear at 4 influences**, and
`Clothing Asset Authoring Spec.md` still needs that line.

## Tooling written this session

* `examples/prep_michaelc_rig.py` - in-Maya prep pass. Idempotent: against 01.6 the structural
  passes report "already done" and it does the weight audit + normalize. Dry run by default
  (`p.prep()`), `p.prep(apply=True)` to act. Run it against 01.5 and it performs the structural
  work too, so it is the fallback if 01.6 is ever mistrusted.
* `tests/test_maya_boundary_names.py` - AST undefined-name check over `core/maya_*.py` and
  `examples/*.py`, the modules CI can only `py_compile`. Both bugs fixed this session were of
  exactly that class. Verified non-vacuous against re-introduced copies of both.
* `tools/michaelc/` - already run, kept for provenance. `make_016.py` (01.5 -> 01.6, the
  authoritative recipe), `weights_017.py` (in `mayapy`: computes W2/W3/W4/W6, exports the new
  skinCluster and a `weights.bin` reference dump), `make_017.py` (splices that in, plus R3 and
  R4, to write 01.7), `verify_017.py` (in `mayapy`: reloads 01.7 and checks it against the
  dump), `verify_016.py` (referential-integrity diff between two .ma files), `dag2.py`
  (full-DAG-path .ma parser - short names are not unique in this rig), `wpos.py` (world joint
  positions from local transforms). `wt.py` was deleted; see that directory's README.

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

## Setup and install, before registering

**Correcting an earlier note in this file.** It said no remote was configured and called that
"the real blocker". That was read off the repo's `scripts/path.txt`, which is **gitignored** -
a per-machine dev file, not what the artists' tool reads. The installed copy at
`~/Documents/maya/2026/scripts/path.txt` has both:

```
local  = C:\Users\shann\Documents\clothing_assets
remote = G:\Shared drives\VFX_Assets_Artists_Library\...\clothing_asset_remote_closet
```

**Unverified:** a process spawned from WSL cannot see `G:` at all (Google Drive streaming
mounts are per-session), so "does that remote resolve" has to be answered from the Setup tab
in Maya. Do that before registering, but do not assume it is broken.

The repo's own `scripts/path.txt` still points at the old repo name
(`maya_clothing_rig\assets`). It only affects headless runs from the repo. Harmless to the
artists; worth fixing for whoever runs `prep_michaelc_rig.py` outside Maya.

### The installed Outfitter is a version behind

`~/Documents/maya/2026/scripts/outfitter/__init__.py` reports **1.2.0**. The repo and the
`fix/maya-boundary-nameerrors` branch are **1.2.1**. 1.2.1 is the build that fixes
`capture_cloth_skeleton_from_rig` raising `NameError` after doing all its work - which is the
Publish tab's 'Regenerate skeleton' button, on the same code path registration uses.
**Install 1.2.1 before registering MichaelC**, or the register will look like it worked and
then throw.

## Outfitter: verified end to end, not just validated

Run against 01.7 in Maya 2026 on 2026-09-03. Four stages, the whole authoring path a garment
actually takes:

| | Stage | Result |
|---|---|---|
| A | `capture_profile` + `validate_profile` | **CLEAN.** 89 joints, root `cloth_root`, group `Rig_GRP`, `root_group_rotate` (0,0,0), markers resolve, `scene_has_rig` true |
| B | `build_cloth_skeleton` from the captured spec, in an empty scene | **89 joints rebuilt, worst world-position drift 0.000000 cm.** Nothing missing |
| C | `plan_for_scene` + `apply_retarget`, bundled `trench_coat_A` onto MichaelC | **89 joints moved, 2 skinClusters, no warnings.** The retargeted joints land 0.0000 cm from MichaelC's rest pose, and the **garment mesh moves 0.000000 cm** - `moveJointsMode` preserved the weights exactly |
| D | `preflight_scene` on the retargeted garment | `level='ok'`, *"Scene looks publish-ready."* |

**The two unmatched joints are correct.** `cloth_coatTail_01` and `cloth_coatTail_02` are the
coat's own custom joints; no body rig has a counterpart, and the retarget reports them rather
than inventing one.

**Console noise to expect, and to ignore.** The retarget prints a wall of
`Error: Joint cloth_X is not in the pose.` That is the garment asset, not MichaelC: the trench
coat's `bindPose1` holds **23 of its 91** cloth joints, because it only binds 23. Verified by
opening the untouched asset and querying `dagPose -members` before any retarget. It will happen
against any target rig. Cosmetic.

**`mayapy` crashes on interpreter shutdown** (`PyThreadState_Get: the function must be called
with the GIL held`) after all output is produced, while Arnold unloads its plugins. A
standalone teardown artefact, not a pipeline failure - every stage above had already passed.

**The version stamp does not reach Outfitter.** `maya_publish.detect_rig_version` looks for a
version token in a rig *namespace*, then in the export group's namespace token, then falls back
to the registered profile's version. It never reads `MichaelC_info_GRP`. MichaelC is imported
with no namespace, so it will always take the profile fallback. The `MichaelC_rig_v01_7` node
is a human-readable marker for whoever opens the scene, and nothing more - keep it honest, but
do not expect it to drive anything.

## Animation readiness

Audited against 01.7 on 2026-09-03. Most of this is already right, and is recorded so nobody
re-does it.

**Working, leave alone:** 145 `_anim` controls, 101 with every channel open. The 44 that are
restricted are restricted correctly - 28 bendy/tangent controls are translate-only, and 16
foot-roll and shoulder pivots are rotate-only. Selection sets are organised (`all_sSet`,
`MichaelC_ctrls_set`, per-limb `*_sSet`). `MichaelC_GEO_LAYER` is display type 2, so the mesh
is not selectable in the viewport; `MichaelC_JNT_LAYER` is hidden. `ikfk` and the space
switches are proxied onto the animation controls, so nobody has to select a `network` node.
Arms default to FK, legs to IK. The god node scales the whole rig (2x moves the mesh 187 cm).

**No Zoo Tools or Hive dependency to animate.** Only `matrixNodes` and `quatNodes` are in
use, and the only script nodes are Maya's own `sceneConfigurationScriptNode` /
`uiConfigurationScriptNode`. The rig opens and evaluates on a clean Maya.

**Open items, in priority order:**

1. **Watch the legs twist.** The W3/W4 falloff is procedural. It matches the rig's own twist
   math, but no human has seen it move.
2. **The head has no space switch.** `head_m_controlPanel_settings` has zero keyable
   attributes and no head or neck control carries a space attribute, while
   `head_m_rigLayer_meta.zooSpaceSwitching` exists in the meta network. Hive knows about it;
   nothing was built. The spine, clavicles and every finger have spaces. Head-follows-world is
   the most used space switch there is, so this will be the first thing an animator asks for.
3. **Decide the arm twists** (see "Not done" above).
4. **Body-guide viz: markers done, toggles left.** `MichaelC_BODY_GUIDE_LYR` is hidden in
   01.8, which takes all 31 joint markers off the controls they were sitting on. Still on:
   `MichaelC_god_m_godnode_anim.bodyJointLineVis` and `.toggleHeadWire`, which draw 34 anatomy
   curves over the character. They are god-node attributes rather than layer state, so decide
   the delivery default and flip them.
5. **IK/FK matching is not in the file.** The rig blends fine on the `ikfk` attribute, but
   snapping a pose across the switch is a Zoo Tools command. Either the animators install Zoo,
   or someone writes a small match script. A decision, not a defect.
6. **12 expressions** drive IK stretch and twist volume preservation
   (`*_ikStretch_expression`, `*TwistVolumePreservation_expression`). They evaluate without any
   plugin, but expressions serialise evaluation, so check playback speed before committing to
   this rig for shot work.
7. **Channel-box clutter on the hands.** Hive proxies a whole component's attributes onto each
   of its controls, so every finger control carries `fk00_space` through `fk03_space` whether
   or not they apply, all of them `parent:world`. Cosmetic, but it makes the channel box hard
   to use on a hand.
8. **Nobody has animated on this rig.** A short test shot is the only real acceptance test.

## Next steps

**Outfitter compliance - the rig itself is done.** `capture_profile` + `validate_profile` run
clean against 01.7 in a real Maya: 89 joints, markers `MichaelC_Joint_GRP` / `MichaelC`,
variants `none`, skin sets 8/18/24/36/36/1, identical to 01.6. What is left is tooling:

1. **Install Outfitter 1.2.1** over the machine's 1.2.0 (see above). Blocking.
2. **Confirm the remote resolves** on the Setup tab in Maya. Cannot be checked from WSL.
3. **Merge `fix/maya-boundary-nameerrors` into master** (clean fast-forward) - that is where
   1.2.1 lives.
4. **Add the line to `Clothing Asset Authoring Spec.md`**: garments bind **classic linear at
   4 influences** to match the body. Still unowned.
5. **Register**: `p.prep()` against 01.7 for a clean audit, then Publish tab >
   **Register rig...**, export group `MichaelC_Joint_GRP`, body-variant switch left empty.

**Animation** - see "Animation readiness" above. Items 1 (watch the legs), 2 (no head space
switch) and 4 (guide viz on by default) are the ones that need a rigger.

## Maya is reachable from this shell - use it

Two work-order items (W1, W5) were fiction produced by reasoning from the `.ma` text. Both
died the moment a real Maya was asked. Do not infer Maya behaviour; test it:

```bash
"/mnt/c/Program Files/Autodesk/Maya2026/bin/mayapy.exe" script.py
```

Keep the script under `/mnt/c/Windows/Temp/...` (cmd.exe refuses a UNC working directory) and
reach repo files by UNC:
`\\wsl.localhost\Ubuntu-24.04\home\sgold\dev\repos\Outfitter_maya_clothing`.
`maya.standalone.initialize()` costs ~35s, loading the rig ~4s. Load `mayaUsdPlugin` first or
`UsdDefaultRenderSettings` arrives as an unknown node - and **never save the scene from a
session where anything is unknown**. Baseline unfamiliar behaviour in an empty scene first;
that is what exposed W1.

**Never name a `mayapy` script after a stdlib module.** `mayapy` puts the script's own
directory on `sys.path`, so a file called `inspect.py` shadows the stdlib `inspect`, and
`maya.standalone.initialize()` dies inside `TrunTimeCommandManager::load` with a bare stack
trace naming nothing relevant. That cost most of an hour and looked exactly like a broken
Maya install.

**Do not `cmds.file(save=True)` from batch.** No plugin on this machine registers
`UsdDefaultSettings` or `nodeGraphEditorInfo`, so they load as `unknown` and a save writes
them back twice: a save/reload round trip gives 3,528 nodes instead of 3,526, with "UUID
already in use". Export just the node you changed and splice its block into the `.ma`.
