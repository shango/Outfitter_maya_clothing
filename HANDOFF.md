# Rig-agnostic Outfitter - working handoff

Feature branch work in progress. Task list lives in the session task tool; this file is
the durable record so a context compaction loses nothing.

## Goal

Make the tool rig-agnostic. One JSON profile per registered rig replaces every hard-coded
GenHuman assumption. Users register a rig from the Publish tab, pick a rig before
publishing, and the browser filters clothing to the rig they're dressing. A retarget tool
converts an existing asset to another rig (joints remap + snap; mesh fit stays manual).

## Decisions locked with the user (2026-07-27)

1. **Profile store**: `<remote>/_rigs/*.json`, distributed by the existing Sync to
   `<local>/_rigs/`. Bundled `package/data/rigs/genhuman.json` is the fallback.
2. **Rig files**: registration copies the rig `.ma` into `<remote>/_rigs/<rig_id>/`.
   Profile stores a library-relative path (`_rigs/<rig_id>/<file>.ma`).
   **Sync never pulls rig `.ma` payloads** (they are 25-30 MB each) - it syncs assets and
   the small `_rigs/*.json` profiles only. A rig file is fetched from the remote on
   demand, the first time it is actually needed (Load test body / publishing for that
   rig), with a progress indicator and an explicit "Fetch rig" affordance. Merely
   selecting a rig in a dropdown must not drag 30 MB over the network.
3. **Variants (gender)**: per-rig and optional - `mode: none | morph | files`. GenHuman is
   `morph` (`god_m_godnode_anim.GH_Body_morph`, female=0, male=1).
4. **Skin sets**: auto-derived at registration by a name-pattern heuristic, resolved joint
   lists stored in the profile, editable afterwards.
5. **Browser filtering**: hide incompatible assets, show a hidden count + a
   "show other rigs" toggle.
6. **Migration**: absent `rigId` reads as `genhuman` (zero-touch back-compat), plus an
   optional "Stamp rig metadata" action.
7. **Compat model**: one `rigId` + many `rigVersions` per asset. Cross-rig reuse goes
   through retarget, which produces a second asset.
8. **Conversion**: assisted retarget, one asset at a time.

## Grounding (Maya docs, verified via Autodesk 2025 command reference)

* `skinCluster -e -moveJointsMode True/False` - move skinned joints without deforming the
  mesh; rewrites bindPreMatrix. This is what lets a retarget preserve weights.
* `copySkinWeights -influenceAssociation name|oneToOne -noMirror` - fallback if a rebind
  is ever needed instead of a joint move.

## Honest limitation to keep surfacing in UI text

A retarget remaps joints and preserves weights. It does **not** adapt the garment's mesh
shape. If the two rigs differ in proportion the asset needs a manual refit and likely a
weight repaint. Never imply the conversion is complete.

## Baseline

194 tests passing before any change (`python3 -m pytest tests/ -q`).

## Progress log

Nothing committed yet (user has not asked for commits) - state lives in the working tree.

### Task 1 DONE - rig-profile core + bundled genhuman profile

* New `scripts/outfitter/core/rigs.py`: `RigProfile`, `Variants`, JSON (de)serialization,
  `validate_profile`, discovery (`list_profiles`/`load_profile`/`find_profile`/
  `resolve_profile`) with library roots beating the bundled dir, `write_profile`, and
  rig-file path helpers. Constants: `RIGS_DIRNAME="_rigs"`, `DEFAULT_RIG_ID="genhuman"`,
  `VARIANT_NONE/MORPH/FILES`.
* `core/skeleton.py`: file I/O removed (`skeleton_file`/`load_cloth_skeleton`/
  `write_skeleton`); now a pure model with `from_json_dict`/`to_json_dict`. Profile I/O
  owns the filesystem.
* Added `RigProfile.bundled_file` so the packaged GenHuman `.ma` (in `package/lib/`)
  resolves by data instead of a `if rig_id == "genhuman"` branch.
* Generated `scripts/outfitter/data/rigs/genhuman.json` from the old
  `cloth_skeleton.json` + config constants + `skin_sets._RECOMMENDED`; verified the
  round-trip reproduces the 89-joint skeleton, the 6 skin sets, the morph variants and
  the bundled rig filename exactly.
* Bridged call sites so nothing broke: `maya_skeleton.build_cloth_skeleton` and
  `capture_cloth_skeleton_from_rig` now go through the profile (the latter rewrites the
  profile, writing to the local library when the loaded profile was the bundled one);
  `publish_panel._regen_skeleton` names the profile it will overwrite.
* Tests: new `tests/test_rigs.py` (46 cases). `tests/test_skeleton.py` reworked to source
  the spec from the bundled profile. **237 passing** (was 194).

### Task 2 DONE - skin sets derived for an arbitrary rig

* `core/skin_sets.py` split into two halves:
  - `classify_joint()` + `derive_skin_sets()` - regex role classifier (pelvis, spine, neck,
    head, clavicle, upperarm, upperarm_twist, lowerarm, lowerarm_twist, hand, thigh,
    thigh_twist, calf, calf_twist, foot, ball) plus a per-garment-type **composition table**
    (`_COMPOSITION`) naming body *roles*, not rig joint names. Twist patterns are tested
    before their parent limb; fingers/metacarpals/ik_/interaction/center_of_mass/root are
    excluded; segments sort by numeric index (the real skeleton lists twist_02 before
    twist_01); sided blocks emit the whole left limb then the whole right, matching
    `_both()`.
  - `_RECOMMENDED` kept as the GenHuman seed, exposed as `genhuman_seed_joints()`
    (renamed from `recommended_joints` so nobody mistakes it for a runtime lookup).
* `plan_skin_set(asset_type, present_joints, recommended, set_name=None)` now takes the
  rig's stored recommendation instead of reading the module table.
* `maya_skeleton.build_skin_set` sources it from `profile.skin_set(asset_type)`.
* Deleted the orphaned `scripts/outfitter/data/cloth_skeleton.json` (embedded verbatim in
  `data/rigs/genhuman.json`).
* **Key result**: `derive_skin_sets` over GenHuman's 89 joints reproduces the
  hand-authored table joint-for-joint, in order, for all 6 types. That equality is
  asserted in `tests/test_skin_sets.py` and is the heuristic's regression bar - fix the
  heuristic if it fails, don't relax the test.
* 247 tests passing.

### Task 3 DONE - rig identity in metadata, publish, scan and sync

* `core/asset.py`: `AssetMetadata` gains `rig_id` (defaults to `genhuman`) and
  `rig_versions`. Read order: `rigId`/`rigVersions`, falling back to legacy
  `genHumanCompat` for the version list. `genhuman_compat` kept as a read-only alias
  property. `supports(rig_id, version="")` now gates on **both** - two rigs sharing a
  version string must not read as compatible. `ClothingAsset.rig_id` / `.fits_rig()`.
* `core/publish.py`: `PublishSpec.rig_id`/`rig_versions`; sidecar writes `rigId` +
  `rigVersions`, and additionally `genHumanCompat` **only for genhuman assets** (writing
  it for an Acme asset would be misleading).
* `core/library.py`: `scan_library` skips the `_rigs` folder entirely; new
  `LibraryScanResult.for_rig(rig_id, version="")`.
* `core/sync.py`: new `is_syncable(rel)` - everything outside `_rigs` syncs; inside
  `_rigs` only `*.json` profiles sync, rig `.ma` bodies never do. Applied at the scan
  step so rig files also can't inflate the asset-package counts.
* `core/validate.py`: version check updated to the two-arg `supports` (the rig-identity
  gate itself lands in task 5).
* Tests added across test_asset / test_library / test_sync / test_publish. **268 passing.**

### Task 4 DONE - active rig persisted in path.txt

* `core/settings.py`: third key `rig = <rig_id>`. `Locations.rig`, `set_rig()`,
  `active_rig_id()` (falls back to `genhuman`). `write_locations` keeps its existing
  positional signature and takes `rig` **keyword-only** after `path`, so existing
  positional callers were not broken. All three `set_*` helpers preserve the other slots.
* `rigs.resolve_profile()` now falls back through: explicit id -> user's saved rig ->
  `genhuman` -> any registered rig -> None. So the Maya-side actions that call it with no
  argument pick up whatever the user last selected.
* 275 passing.

### Task 12 CORE DONE (UI wiring deferred to tasks 8/9)

* `core/rigs.py`: `rig_file_status()` returning `STATUS_BUNDLED/LOCAL/REMOTE_ONLY/
  MISSING/NO_FILE` (stat only - opening the rig dropdown must never download), and
  `ensure_rig_file(profile, local, remote, variant, progress)` which copies the body down
  in 4 MB chunks through a `.part` file renamed on success, so an interrupted fetch never
  leaves a truncated rig that would later read as "local". Distinct actionable errors for
  "rig declares no file" / "no remote configured" / "never uploaded" / "no local folder".
* 289 passing.

### Task 5 DONE - validation, scene gateway and attach are rig-driven

* `core/scene.py`: `genhuman_version()` -> `rig_version(markers)` (accepts a `rigVersion`
  or legacy `genHumanVersion` attr, namespaced rigs included);
  `resolve_export_group(node, export_group)` takes the group name from the profile.
* `core/validate.py`: `validate_scene_preconditions(..., profile=None, export_group=None)`.
  New **`rig_mismatch` hard error** - a garment built for rig X must never attach to rig
  Y, because two rigs can share joint names and the garment would deform into nonsense.
  Messages name both rigs and point at Retarget. Version gate still applies within a rig.
  Calling without a profile keeps the original single-rig behaviour.
* `core/attach.py`: `attach(asset, namespace, profile=None, export_group=None)`.
* `ui/window.py`: `_attach_selected` resolves the profile, uses its export group, and
  passes the profile into attach (the selector UI itself is task 9).
* `tests/_fake_scene.py` updated for the new gateway shape.
* Tests: cross-rig rejection **leaves the scene byte-identical** (nodes, connections,
  namespaces, registry all unchanged) - the FR-2 guarantee on the new gate.
* **299 passing.**

### Task 6 DONE - Maya-side rig registration

* New `scripts/outfitter/core/maya_rigs.py` - the capture half of rig-agnosticism:
  - `candidate_export_groups()` - every transform that directly parents a joint, ranked
    (current selection's namespace first, then most descendant joints). **Structural, not
    name-based** - guessing by name is the hard-coding being removed. The UI offers the
    list; the user picks.
  - `detect_variant_switches()` - user-defined keyable attrs on transforms whose *name*
    reads like a body switch, "morph" ranked first. `VariantCandidate.as_variants()` maps
    range min/max to female/male (GenHuman's convention), swappable in the dialog.
  - `suggested_markers()` - export group + the rig's top DAG root + the variant node,
    filtered to what actually exists.
  - `rig_source_file(node)` -> `RigSource(path, origin)`; `origin` is `"reference"` (the
    reliable case) or `"scene"` (the open file - right if they opened the rig, wrong if
    they imported it into a garment scene, so the UI must ask).
  - `capture_profile(...)` - full profile from the live scene: skeleton via the shared
    walk, skin sets via `derive_skin_sets`, markers, author, created date. Validates and
    raises before anything is written.
  - `register_rig(...)` - capture (fails fast, *before* any 30 MB copy), install the rig
    `.ma` into remote then local, write the profile into both `_rigs` folders, set it
    active. Warns when no remote is configured (registered on this machine only).
* `core/maya_skeleton.py`: extracted `capture_skeleton_spec(cmds, root_joint, export_grp)`
  from `capture_cloth_skeleton_from_rig` so both capture paths share one walk;
  `_find_export_root(cmds, marker=None)` now takes the group name, defaulting to the
  active profile's via `_active_export_group()` (error text no longer says "GenHuman").
* `core/rigs.py` (pure, tested): `rig_file_rel()`, `install_rig_file()` (atomic, progress,
  no-op when installing a rig onto itself), `looks_like_variant_attr()`.
* Verified the heuristics reproduce the hand-authored GenHuman profile: detection yields
  `god_m_godnode_anim.GH_Body_morph` with female=0/male=1, and `suggested_markers` yields
  the same three markers.
* **318 passing.** `maya_rigs.py` itself is `py_compile`-only (Maya boundary convention) -
  it needs an in-Maya smoke test: register a rig, confirm the profile + `.ma` land in
  `<remote>/_rigs/<rig_id>/`.

### Task 7 DONE - GenHuman literals purged from the Maya boundary

* `core/testfit.py`: `body_morph_value(gender, variants)` - the switch value now comes
  from the rig's profile. Raises for a variant the rig doesn't offer, **including any
  gender on a single-body rig** (silently returning 0.0 would load the wrong body).
* `core/maya_testfit.py` is fully profile-driven:
  - `_genhuman_present` -> `_rig_present(cmds, markers)`;
    `_set_body_morph(cmds, gender, variants)` returns `(value, plug)`.
  - `load_test_body(gender, mesh_group, profile=None, progress=None)` resolves the
    profile, picks the variant file for a `files`-mode rig, and gets the body through
    **`rigs.ensure_rig_file`** (this is the task-12 fetch, wired at last) - so it fetches
    from the shared library on first use. References under
    `sanitize_namespace(body_file.stem)`.
  - `_remove_genhuman_references`/`_delete_genhuman` -> `_remove_rig_references`/
    `_delete_rig`, matching by the rig's own file stems + markers.
  - `LoadBodyResult.morph` is now `float | None` (None = single-body / files-mode rig) and
    carries `rig_label`, `switch`, `namespace`.
* `core/maya_publish.py`: `scene_has_rig(markers=None)` and `detect_rig_version(profile=
  None)`, both defaulting to the active profile. Marker matching uses
  **`cmds.ls(pattern, recursive=True)`** - confirmed against the Maya 2025 `ls` command
  reference ("searches for name matches in all namespaces") - so the loose substring match
  the old GenHuman check had is preserved across namespaces. `detect_rig_version` now
  falls back to `profile.version`, which is the right prefill for a rig whose scene names
  carry no version token.
* `core/publish.py`: preflight/pre-check messages say "A rig is still in the scene."
* `config.py`: the GenHuman block is now explicitly labelled **seed values, not the
  runtime authority**, each constant annotated with the profile field that supersedes it.
  Deleted `bundled_genhuman_path()` and `BUNDLED_GENHUMAN_NAMESPACE`, orphaned by the
  `ensure_rig_file` switch (`rigs.bundled_rig_file(profile)` replaces them).
* Behaviour note: `_delete_rig`'s DG sweep is now marker-scoped, so it no longer sweeps
  `*GH_*` / `god_m_*`. Slightly less aggressive on an *imported* GenHuman, but the
  reference path (the one `load_test_body` uses) is complete, and a marker-scoped sweep
  can't eat a garment node.
* **319 passing.**

### Task 8 DONE - Publish tab rig selector + Register rig dialog (and task 12's UI half)

* New `ui/rig_bar.py` - **shared by both tabs** (task 9 reuses it):
  - `RigSelector` - rig dropdown + body-status label + "Fetch rig" + optional
    "Register rig…". Selecting persists via `settings.set_rig` and emits `rigChanged`.
    `select(rig_id)` switches as if the user had (persists + emits); `reload(select=)`
    rebuilds the list without persisting. **Selecting never downloads anything** - status
    is a stat.
  - `_FetchWorker` + `fetch_rig_file(parent, profile, variant, on_done)` - the 30 MB copy
    on a `QThread` with a progress dialog; `on_done` runs on the UI thread. Cancel closes
    the dialog and lets the (atomic) copy finish rather than risk a truncated rig.
  - `variant_provider` callback so a files-mode rig's status/fetch follow the chosen
    gender.
* New `ui/rig_dialog.py` - `RegisterRigDialog`. Prefills from `maya_rigs`: export-group
  candidates, detected variant switch (with a **Swap** button, since nothing in a rig says
  which end of the range is which body), rig file + where it came from, author. Confirms
  before replacing an already-registered rig. Registration runs on the main thread (it
  reads the scene through `cmds`) with a wait cursor.
* `ui/publish_panel.py`: selector above the steps; Gender combo now populated from
  `profile.variants.names` and **disabled with "- single body -"** for a rig with none;
  "GenHuman compat" -> "Rig versions" (defaults to the rig's registered version);
  `_gather_spec` sets `rig_id`; `_load_test_body` fetches off-thread first when the body
  is remote-only, then loads with the selected profile; `remove_test_body(profile)`;
  `_apply_info_to_form` switches the rig from the asset's `rigId` and warns when that rig
  isn't registered here; `showEvent` reloads the rig list (a Sync may have brought new
  ones in).
* **Bug found and fixed**: `_gather_spec` still passed `genhuman_compat=` to `PublishSpec`,
  which lost that field in task 3 - publishing would have raised `TypeError`. `py_compile`
  can't catch a bad kwarg; grep the UI for renamed fields after every core rename.
* `config.GENDER_NONE = "none"` + `asset.py` accepts it: a single-body rig's assets record
  "none" rather than leaving gender blank (blank reads as "forgot to set it").
* **320 passing.**

### Task 9 DONE - Library tab is rig-aware

* `ui/window.py`: `RigSelector` (no Register button - the Publish tab owns that) sits above
  the filter bar with a **"Show other rigs"** checkbox.
* `_apply_filter` checks the rig **first** (a garment built for another rig can't attach at
  all, so offering it and then rejecting it is worse than hiding it), counts what it hid,
  and appends `"· N for other rigs (hidden)"` to the status line - "my asset vanished" must
  never be a mystery. With the toggle on they appear greyed, suffixed `[rig_id]`, with a
  tooltip saying why.
* Gender filter is repopulated from the selected rig's variants
  (`_reload_gender_filter`), so a single-body rig doesn't offer male/female.
* Detail panel: new **Rig** row (amber "- not the selected rig" when it differs);
  "GenHuman compat" -> "Rig versions", now reading `meta.rig_versions`.
* `_attach_selected` takes the profile from the selector and **refuses a cross-rig attach
  up front** with an explanation pointing at Retarget (the `validate.rig_mismatch` gate
  would catch it anyway; this explains it before the attempt).
* `refresh()` reloads the rig list too - a rig someone else registered arrives with Sync.
* **320 passing** (UI is `py_compile`-only; PySide6 isn't in the headless env).

### Task 10 DONE - asset retarget

* New pure `core/retarget.py`: `plan_retarget(asset_joints, target, source=None)` matching
  in three named ways - **name**, **alias** (`profile.joint_aliases`), **role** (reusing
  `skin_sets.classify_joint`, so `cloth_GM_foot_R` -> `cloth_foot_r`). `JointMatch.how`
  records which, so the user sees *how* a joint was matched, not just that it was.
  - **Two passes** (certain matches first, guesses second): otherwise a role guess could
    steal a joint another garment joint names outright, and the outcome depended on input
    order. A test asserts both orders give the same answer.
  - Never maps two garment joints onto one target (that would rename both to the same
    name and lose one); segment index and side are part of the role key, so `spine_02`
    does not silently become `spine_01`.
  - `ordered_moves(target)` returns `(garment joint, rest transform)` **parent before
    child** - the stored transforms are local, so a joint only lands right if its parent
    moved first. Asserted in a test.
* New `core/maya_retarget.py`: `plan_for_scene()` + `apply_retarget()`.
  - Everything that moves the skeleton happens inside `skinCluster -e -moveJointsMode
    True`, switched off in a **`finally`** (a scene stuck in move-joints mode is worse
    than a failed retarget). The `Rig_GRP` reframe happens inside that window too - it
    moves joints in world space and would otherwise drag the mesh.
  - Renames in **two passes through a temp prefix**, so two rigs with swapped left/right
    conventions can't have Maya silently uniquify a name to `foo1` - attach matches
    exactly, so that joint would quietly never connect.
  - `dagPose -reset -bindPose` afterwards (verified in the 2025 command reference) so
    "go to bind pose" doesn't snap the skeleton back onto the old rig.
  - Stamps `rigId`/`rigVersions` onto `cloth_info` and clears a now-untrue legacy
    `genHumanCompat`.
  - Every result string ends with the caveat that the mesh was **not** reshaped.
* `ui/window.py`: grid right-click "Retarget to <rig>…" - confirms (naming both rigs and
  the limitation), opens the asset (asking before discarding an unsaved scene), shows the
  plan **including what won't map**, applies, then tells the user to check the fit and
  publish under a new name.
* `tests/test_retarget.py` (15 cases). **335 passing.**

### Task 11 DONE - migration action, docs, version

* New pure `core/migrate.py`: `plan_stamp(sidecars, rig_id)` / `apply_stamp(plan)` writes
  `rigId`/`rigVersions` into sidecars that lack them, carrying the legacy `genHumanCompat`
  list over as the versions. **Never reassigns** an asset that already names a rig (moving
  an asset between rigs is a retarget, not a metadata edit) - asserted in a test. Other
  sidecar keys are preserved; unreadable files are reported, not crashed on. Always warns
  that it touched sidecars only (the `.ma`'s `cloth_info` is refreshed on next publish).
  `tests/test_migrate.py`, 8 cases - including that a stamped asset reads back with exactly
  the identity it previously implied.
* `ui/window.py`: Setup tab **"Stamp rig metadata…"** - plans, lists what it would change,
  confirms, applies, then rescans.
* Docs updated: `README.md` (rig-agnostic intro + a "Working with more than one rig"
  section), `Outfitter Guide.md` (new "Working with rigs" walkthrough: registering,
  fetching a body, retargeting, plus the filter/step-1 changes), `Outfitter — User Guide.md`
  (§1, §4, the validation tables incl. the new `rig_mismatch` row, §8 rewritten as "Rigs and
  versions", troubleshooting rows for the new failure modes), `Clothing Asset Authoring
  Spec.md` (§12 now documents `rigId`/`rigVersions` + the legacy fallback; checklist row).
* `__version__` -> **1.2.0**.
* **343 passing**, `py_compile` clean across package + installer.

## Next up

Nothing outstanding in the plan - tasks 1-12 are complete. What remains is verification in
Maya, which the headless suite cannot do (see below).

## Needs verifying in Maya (the headless suite cannot)

1. **Register a rig** end to end: a non-GenHuman rig in a scene -> Publish ▸ Register rig…
   -> profile + `.ma` land in `<remote>/_rigs/<rig_id>/`, skin sets look sane.
2. **Fetch a rig body** on a second machine/library: status reads "not downloaded", Fetch
   pulls it, Load test body works. Confirm the dropdown alone never downloads.
3. **Load/Remove test body** on both a morph rig (GenHuman) and, if available, a
   single-body rig (Gender field disabled, `gender: none` published).
4. **Retarget** a real GenHuman garment onto another rig: weights must survive the move
   (this is the `moveJointsMode` claim), joints must land on the new rest pose, and the
   renames must be exact (no `foo1` uniquified names).
5. **Attach** on a scene with two different rigs present, selecting one of them.

## How to resume

* Full task list with per-task detail lives in the session task tool (tasks 1-12; 1-5
  completed, 12 part-done, 6-11 pending). This file mirrors the outcomes.
* Run the suite: `python3 -m pytest tests/ -q` from the repo root. **299 passing** at the
  end of task 5. Also `python3 -m py_compile scripts/outfitter/core/*.py
  scripts/outfitter/ui/*.py` for the Maya-boundary modules the headless suite can't run.
* **Nothing is committed** - the user has not asked for commits. All work is in the
  working tree on branch `master`.
* `git status` also shows changes that pre-date this session: the Step-1 "clean room"
  pre-check across `core/maya_publish.py`, `core/publish.py`, `ui/publish_panel.py`,
  `tests/test_publish.py`, plus untracked `README.md` and `Outfitter Guide.md`. Those are
  **not** part of the rig-agnostic work - leave them alone.
* Files created this session: `scripts/outfitter/core/rigs.py`,
  `scripts/outfitter/data/rigs/genhuman.json`, `tests/test_rigs.py`, this file.
* File deleted this session: `scripts/outfitter/data/cloth_skeleton.json` (embedded
  verbatim in `data/rigs/genhuman.json`; verified equal before deletion).
* The one-shot generator that produced `genhuman.json` lives in the session scratchpad
  (`gen_genhuman_profile.py`). It has already run; the profile is the source of truth now.
  It is only worth re-running if the seed data in `config.py` / `skin_sets._RECOMMENDED`
  changes.

## Watch out for (things a fresh context would get wrong)

* `core/rigs.py` imports `core/settings.py`; `settings.active_rig_id()` imports
  `rigs.DEFAULT_RIG_ID` **lazily inside the function** to avoid a circular import. Keep it
  lazy.
* `settings.write_locations(local, remote, path=None, *, rig=None)` - `rig` is
  keyword-only *after* `path` on purpose, so existing positional callers still work.
* `skin_sets.plan_skin_set` now requires the recommendation to be passed in; there is no
  built-in table fallback by design (that fallback would be the hard-coding being removed).
* `skin_sets.genhuman_seed_joints()` is the old `recommended_joints()`, renamed so nobody
  mistakes it for a runtime lookup. It is a test reference, not production data.
* `validate.validate_scene_preconditions` and `attach.attach` both still work with no
  `profile` argument (original single-rig behaviour) - tests cover that path, don't drop it.
