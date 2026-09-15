# Jenn rig - Outfitter onboarding handoff

Working record for bringing the Jenn rig into the Outfitter rig repo.
Session: 2026-09-15 (audit against `MichaelC_rig_v3.ma`).
Sibling to `HANDOFF_MichaelC.md` (the MichaelC onboarding) and `HANDOFF.md` (rig-agnostic tool work).

## Where things stand

**Rig file: `Jenn_rig_v1.6.ma`** (2026-09-15), written from the rigger's `Jenn_rig_v1.5.ma`
drop by `tools/jenn/make_v16.py`. It is Outfitter-ready and at MichaelC v3 parity: see
"What v1.6 changed" below for what was applied and the evidence. `v1.5` is kept as the
rigger's original.

**Ready to register**, subject to the same two tooling prerequisites MichaelC has (install
Outfitter 1.2.1 over the machine's 1.2.0, and confirm the remote resolves from the Setup tab).

**Reference rig: `MichaelC_rig_v3.ma`** (2026-09-15). Byte-identical to the file still on disk as
`MichaelC_rig_v2.2.ma`, and that file carries the **v2.3** content (in-scene stamp
`MichaelC_rig_v2_3`, `maxInfluences` 4, no turntable nodes, guide layer hidden). So the release
`v3` is the finished v2.3 build described in `HANDOFF_MichaelC.md`. There is no separate
`MichaelC_rig_v2.3.ma` on disk any more, and the true v2.2 intermediate is gone.

## Headline: Jenn already validates clean

Run in Maya 2026 (`mayapy`, fresh session) against `Jenn_rig_v1.5.ma` as delivered:

* `maya_rigs.capture_profile(...)` succeeds and `rigs.validate_profile(...)` returns **no errors**.
* **89 export joints**, names matching GenHuman/MichaelC exactly, so `derive_skin_sets` reproduces
  the standard sets with no hand-editing: **8/18/24/36/36/1** (shoes/pants/shirt/dress/coat/hat),
  shoe set on `cloth_GM_foot_L` / `cloth_GM_foot_R`.
* **One 89-joint export-group candidate** (`|JENN|Skeleton`); the next is the 87-joint deform
  layer. No repeat of the v2.1 two-skeleton tie that flipped MichaelC's registration default.
* Markers `Skeleton` / `JENN`, both resolving to exactly one node in the scene.
* No references, no namespaces, no unknown nodes, no containers.
* **Rig is at bind pose**: zero `*_anim` controls deviate from `t=0, r=0, s=1`.
* Body mesh bound **directly to the export skeleton** (`|JENN|Skeleton|root|...`), 79 influences
  (the 89 minus the 10 non-deforming: `root`, `interaction`, `center_of_mass`, the 6 `ik_*`
  markers and `ik_*_root`). Same shape as MichaelC v2.3.
* `skinningMethod` **0** (classic linear) already. All 25,266 vertices sum to 1.0.
* Variants: no morph or gender attribute anywhere, so `variants.mode = "none"` and its garments
  publish `gender: none`, exactly like MichaelC.

So registration is not blocked on structure. What is left is the same clean-up pass MichaelC got
between 01.5 and v2.3.

## Jenn v1.5 against MichaelC v3, as both were delivered

This table is the **as-delivered** comparison, kept as the record of what was wrong. Everything
in bold on the Jenn side is fixed in v1.6, and the MichaelC geo-layer row is fixed in the
regenerated v3; see the two sections after it.

| | Jenn v1.5 | MichaelC v3 |
|---|---|---|
| Nodes | 3,541 | 3,525 |
| `validate_profile` | clean | clean |
| Export joints | 89, GenHuman names | 89, GenHuman names |
| Export group | **`Skeleton`** (generic) | `MichaelC_Joint_GRP` |
| Mesh group / mesh | **`Geo`** / **`Jennifer_Geo1`** | `MichaelC_Mesh_GRP` / `MichaelC_body_mesh` |
| Markers | `Skeleton`, `JENN` | `MichaelC_Joint_GRP`, `MichaelC` |
| The -90 X | on the export **group** (GenHuman's way) | on `root.jointOrient` |
| Skin sets | 8/18/24/36/36/1 | 8/18/24/36/36/1 |
| Body vertices | **25,266** | 5,280 |
| `skinningMethod` | 0 | 0 |
| `maxInfluences` | **5** | 4 |
| `maintainMaxInfluences` | on | on |
| Peak influences/vertex | **10** | 4 |
| Vertices summing to 1.0 | all | all |
| Body height | 172.5 cm | 187.9 cm |
| Guide layer | **visible**, 66 members | hidden, 172 members |
| Joint layer | **visible**, displayType 1 (template) | hidden, displayType 2 |
| Geo layer displayType | 0 (selectable) | 0 (selectable - a v2.x regression, 01.8 had 2) |
| Bendy splines | **8 visible** | 8 hidden |
| Arnold nodes | **5** (`requires mtoa 5.5.5.2`) | 0 |
| Version stamp node | **none** | `MichaelC_rig_v2_3` under `MichaelC_info_GRP` |
| dagPose nodes | 3 (`bindPose1/2/14`) | 1 (`bindPose4`) |

### Proportions, measured from world joint positions in Maya

| Pair | Median | Max |
|---|---|---|
| Jenn <-> GenHuman | **4.60 cm** | 7.6 cm |
| MichaelC <-> GenHuman | 8.83 cm | 11.2 cm |
| Jenn <-> MichaelC | 9.27 cm | 14.1 cm |

**Jenn is roughly twice as close to GenHuman as MichaelC is.** Existing GenHuman garments should
retarget onto Jenn with materially less refitting than onto MichaelC. Biggest Jenn/MichaelC
deltas are `spine_05` 14.1, `head` 13.3, `neck_01` 13.0.

`center_of_mass` reports 99.5 cm against GenHuman for **both** Jenn and MichaelC: it sits at
y=0 in both rigs and at 99.5 in GenHuman's captured profile. That is GenHuman's own outlier, not
a Jenn defect. Ignore it.

## What v1.6 changed

`python3 tools/jenn/make_v16.py` writes the structural file; `weights_v16.py` under `mayapy`
computes the pruned weights; `make_v16.py <export>` regenerates from v1.5 and splices them in,
so the result is deterministic from the rigger's drop. `verify_v16.py` reloads and checks it.

| | What was done | Evidence |
|---|---|---|
| A | The 5 Arnold render-settings nodes, their 4 connections, the 18 `.ai_*` attribute lines mtoa adds to the two shading groups, and the `requires ... "mtoa"` declaration, all removed | Reloads with **zero unknown nodes** (MichaelC v3 still has two). The `.ai_*` lines are not optional: dropping the `requires` alone makes Maya reject the file with *"The shadingEngine 'initialShadingGroup' has no '.ai_override' attribute"* |
| R | `Skeleton` -> `Jenn_Joint_GRP` (2,516 refs), `Geo` -> `Jenn_Mesh_GRP`, `Jennifer_Geo1` -> `Jenn_body_mesh` (+ both shapes) | Markers are now `Jenn_Joint_GRP` / `JENN`, each resolving to exactly one node. Every `createNode -p` parent and every `connectAttr` endpoint still resolves |
| V | Guide layer hidden, 8 bendy splines hidden, joint layer displayType 1 -> 2 and hidden, geo layer displayType -> 2 | Layers read back `Jenn_BODY_GUIDE_LYR(vis=False)`, `Jenn_GH_JNT_LAYER(vis=False,dt=2)`, `Jenn_GH_GEO_LAYER(dt=2)`, no bendy curve visible |
| S | `Jenn_info_GRP` added with `Jenn_rig_v1_6` and `Jenn_rig_Maya2026` | |
| W | `maxInfluences` 5 -> **4**; 4,740 vertices pruned and renormalized | Cost measured, not assumed: **0.0000 cm at bind**, and in an aggressive FK/IK pose max **0.3978 cm**, p99 0.0398, mean 0.0016, 708 vertices moved. Histogram now `1:13408 2:3255 3:1894 4:6709` |

Reloaded from a fresh `mayapy` session: **3,539 nodes** (3,541 - 5 Arnold + 3 info), no errors,
no unknown nodes, `validate_profile` clean, peak **4** influences, all 25,266 vertices sum to
1.0, `skm=0 mi=4 mmi=True`, 79 influences, god-node 2x still moves the mesh 172.391 cm. The
weights read back out of the `.ma` match Maya's computed array to **1.355e-20** - the splice is
bit-exact.

## Left for the rigger: four joints carry no weight

Found while measuring, pre-existing in the v1.5 drop and **not** caused by the prune. Read
through `MFnSkinCluster.getWeights`, so this is Maya's own array, not a `.ma` text parse (the
mistake that produced the withdrawn MichaelC W5):

| joint | total weight in v1.5 | over |
|---|---|---|
| `upperarm_l` / `upperarm_r` | **0.000** | 0 verts |
| `thigh_l` / `thigh_r` | **0.000** | 0 verts |
| `spine_05` | **0.105** | 1,906 verts (trace only) |

All the arm and leg weight sits on the twist children instead - `upperarm_twist_01_l` 141.4,
`thigh_twist_02_l` 206.5, and so on. That is a defensible authoring choice, since the twists are
children of the parent bone and inherit its bend. It is recorded because of what it means
downstream, not because it is obviously wrong.

**Why it matters for Outfitter:** `derive_skin_sets` picks joints by **name**, not by weight, so
a shirt's recommended set still contains `cloth_upperarm_l` and `cloth_spine_05` and a pair of
trousers still contains `cloth_thigh_l`. A garment bound to those joints follows them correctly -
they do move - but the **body** does not use them, so garment and body will not deform
identically around the shoulder, hip and upper chest. Either the rigger redistributes some weight
onto the parent bones, or the skin sets for this rig get hand-corrected in the profile (which
`RigProfile.skin_sets` explicitly supports). Not fixed here: redistributing would overwrite the
rigger's authoring, the same reason MichaelC's foot mirror-asymmetry was left alone.

**Not a defect:** `head` carries 16,204 over 17,775 vertices, 64% of the mesh. Those vertices all
sit between y=149.9 and y=172.4 cm on a 172.5 cm character - it is a dense face, not a weighting
error.

## The work list

Ordered by whether it blocks registration. **A through E below are all applied in v1.6**; the
section is kept as the record of why each was done.

### A. Generic landmark names (the one real risk)

`Skeleton` and `Geo` are the exact names 01.6 renamed away from on MichaelC, for a reason that
still applies: `maya_skeleton._find_export_root` resolves the export group **by short name across
the whole scene and takes the first match**, and the same names become the profile's `markers`.
A garment scene containing anything called `Skeleton` resolves the wrong node. `Geo` is less
dangerous than Daniel's `Mesh_GRP` (which is literally `config.MESH_GROUP`) but is generic in the
same way.

Precedent from MichaelC 01.6: `Skeleton` -> `MichaelC_Joint_GRP`, `Geo` -> `MichaelC_Mesh_GRP`,
`Body` -> `MichaelC_body_mesh`. `Rig` was left generic on MichaelC and still is on Jenn.

**Renaming invalidates any profile already captured against the old names**, so it must happen
before registration, not after.

### B. Weights: peak 10 influences, `maxInfluences` 5

The spec is classic linear at 4 influences (`HANDOFF_MichaelC.md`, R2/R3). Jenn's histogram:

```
1:14176  2:3658  3:2034  4:2207  5:2687  6:262  7:110  8:100  9:30  10:2
```

3,191 vertices exceed 4. Needs the same prune-and-renormalize MichaelC got (R3/W6), with the
cost measured in an aggressive pose before and after, not assumed. `maintainMaxInfluences` is
already on, so this only affects the authored weights, not future painting.

### C. Viewport clutter (the 01.8 pass, unapplied on this branch)

* `Jenn_BODY_GUIDE_LYR` is **visible**. **28 `*_JOINT_MARKER_CRV` curves sit at distance 0.000
  from an animation control** and are selectable, so a click at the clavicle finds the marker,
  not the control. Same defect, same fix: `setAttr "Jenn_BODY_GUIDE_LYR.v" no;`. The layer's
  other 34 members are `*_LINE_CRV` anatomy curves whose transform pivots are at the origin (the
  god node is there too, which is why a naive nearest-control check flags them); hiding the layer
  covers both.
* The **8 bendy splines** (`arm_l/arm_r/leg_l/leg_r` x `bendy00_crv`/`bendy01_crv`) are visible
  and on no display layer, so they take clicks down the limbs. MichaelC hides them rather than
  deleting them, because each is read by a `curveInfo` and two `motionPath` nodes.
* `Jenn_GH_JNT_LAYER` is visible at displayType 1 (template). MichaelC hides its joint layer at
  displayType 2.
* `Jenn_GH_GEO_LAYER` is displayType 0, so the body mesh is selectable in the viewport. MichaelC
  01.8 used displayType 2. **Note the v2.x line lost that**, so MichaelC v3 is also at 0 - worth
  fixing on both or deciding it deliberately.

### D. Arnold dependency

Jenn carries `requires -nodeType "aiOptions" ... "mtoa" "5.5.5.2"` and 5 shared Arnold nodes
(`defaultArnoldRenderOptions`, `defaultArnoldFilter`, `defaultArnoldDriver`,
`defaultArnoldDisplayDriver`, `defaultArnoldDenoiser`). MichaelC carries none. On a machine
without mtoa loaded these arrive as **unknown nodes**, and the standing rule is never to save a
scene from a session where anything is unknown. They are default render settings and carry no rig
data.

### E. Cosmetic / convention

* No `Jenn_info_GRP` version stamp. MichaelC has one. It does not reach Outfitter
  (`maya_publish.detect_rig_version` never reads it) but it is the convention and it tells whoever
  opens the scene what they have.
* 3 `dagPose` nodes against MichaelC's 1. Not yet checked for orphans.

## Also fixed: two things about the MichaelC v3 release itself

Both were about the release file being honest rather than about rig behaviour, and both are now
applied by `tools/michaelc/make_v3.py`, which regenerates `MichaelC_rig_v3.ma` from
`MichaelC_rig_v2.2.ma` (byte-identical to what shipped as v3, so no backup was needed):

1. **The in-scene stamp said `MichaelC_rig_v2_3`** and the `.ma` header `//Name:` line said
   `MichaelC_rig_v2.2.ma`, while the file ships as `MichaelC_rig_v3.ma`. Stamp is now
   `MichaelC_rig_v3`.
2. **`MichaelC_GEO_LAYER` had lost `displayType 2`** somewhere in the v2.x branch. 01.8 had it
   (body mesh not selectable); v3 had 0. Restored. The v2.3 pass re-applied the guide-layer and
   bendy-spline fixes from 01.8 but not this one.

Verified: v3 still reloads at **3,525 nodes**, `validate_profile` clean, one 89-joint candidate,
`mi=4 mmi=True skm=0` peak 4. Its two unknown nodes (`UsdDefaultRenderSettings`,
`hyperShadePrimaryNodeEditorSavedTabsInfo`) are unchanged from before the edit - pre-existing,
and the reason the standing rule is never to save MichaelC from a batch session.

## Next steps

**The rig itself is done.** What is left is the same tooling checklist MichaelC is waiting on,
plus the two Jenn-specific decisions:

1. **Install Outfitter 1.2.1** over the machine's 1.2.0. Blocking for both rigs - 1.2.1 is the
   build that fixes `capture_cloth_skeleton_from_rig` raising `NameError` after doing all its
   work, which is the same code path registration uses.
2. **Confirm the remote resolves** on the Setup tab in Maya. Cannot be checked from WSL.
3. **Merge `fix/maya-boundary-nameerrors` into master** (clean fast-forward).
4. **Register**: Publish tab > Register rig..., export group `Jenn_Joint_GRP`, body-variant
   switch left empty. There is one 89-joint candidate, so the top entry is right - but read the
   dropdown rather than accept it, the way the v2.1 episode taught.
5. **Decide the four unweighted joints** (see above) before garments are authored against Jenn,
   since it affects whether the derived skin sets are usable as-is.
6. **Someone should open v1.6 in a GUI Maya and move it.** Every check here is headless or
   `mayapy`. Nobody has posed this rig since the prune.

## Method notes

* Audit script: `tools/jenn/rig_audit.py` (run under `mayapy`, takes a `.ma` and writes JSON).
  It reports node counts, export-group candidates as Outfitter ranks them, a full
  `capture_profile` + `validate_profile` pass, per-skinCluster influence histograms read through
  `MFnSkinCluster.getWeights`, display-layer state, guide-markers-on-controls distances, and joint
  world positions for proportion comparison.
* Structural pre-pass headless: `tools/jenn/profile_rig.py`, reusing `tools/michaelc/dag2.py`
  (full-DAG-path parser; short names are not unique in these rigs).
* The standing warnings from `HANDOFF_MichaelC.md` all still apply: run Maya rather than infer it,
  keep `mayapy` scripts off stdlib names, never `cmds.file(save=True)` from batch, and count nodes
  from a fresh session.
