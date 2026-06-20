# TODO — GenHuman Snap-On Clothing Tool

Multi-session build tracker. Source of truth: `Snap-On Clothing Rig System.md` + `prd.md`.
Artist-facing build contract: `Clothing Asset Authoring Spec.md` (handed to the clothing rigger 2026-06-04).
Host: Maya 2026 · Python 3 · PySide6. Convention: `[ ]` todo · `[~]` in progress · `[x]` done · `[!]` blocked/needs decision.

> **Each session:** pick the next unchecked item in the lowest open milestone, update status here,
> and keep `prd.md` in sync if a decision is made. Don't rename body/export skeleton joints (locked contract).

---

## Decisions to lock before/while building  (resolve `[!]` items — they gate real work)
- [x] **NAMESPACE-AWARE + MULTI-RIG ATTACH (done 2026-06-10):** production **imports** the rig (not Open) and has **2+ GenHuman rigs per scene** (each character wears its own clothing). Design landed = **selection-driven, NOT a discovery dropdown** — the user **selects any node of the target rig**; the tool reads that node's top namespace and resolves *that* rig's `EXPORT_SKELETON_GROUP`, so attach binds to the intended rig with zero ambiguity (native Maya "select then act"). Steer users to **"use namespaces" ON** on import (`ns:Node` colon — joints still match `cloth_*` because `descendant_joints` strips `:`; the OFF/`ns_Node` prefix case is unsupported). **Implemented:** (1) `SceneGateway.selected_nodes()` + `resolve_export_group(node)` (MayaScene: `ls("{topNs}:*", recursive=True)` finds the marker across nested namespaces; root rig → bare marker); (2) `ui/window.py::_attach_selected` resolves the rig from selection, shows `Target rig: <ns>` in the prompt, routes the namespaced `export_group` into `attach()`, falls back to a root-level rig when nothing is selected; (3) `validate_scene_preconditions(export_group=…)` rig-present gate now keys off `scene.exists(export_group)` (the *chosen* rig) with a "select the target rig" hint, replacing the bare-`RIG_MARKERS` check; (4) `FakeScene` namespace-aware `build_genhuman(namespace=…)` + `select()`/`selected_nodes`/`resolve_export_group`, and `descendant_joints` now scopes by **exact** ancestor address (fixes cross-rig short-name leakage). **Tests: 109 passing** (+resolve-from-selection, attach-to-namespaced-rig, two-rigs-dressed-independently, missing-vs-empty export group). Supersedes the bare `[!] Dual-skeleton target` item below. **NEXT: resume basic-attach in-Maya testing** (import GenHuman with namespaces ON, select it, Attach the trenchcoat).
- [x] **Connect attrs:** LOCKED — connect `.translate`/`.rotate`/`.scale` compounds; `jointOrient` OFF; `visibility` OFF. **Scale required** (animators scale body joints for matchmove fit → clothing must follow). Asset skinning + fit deformers must hold up under non-uniform joint scale. (PRD §4/§10)
- [!] **Dual-skeleton target:** canonical DAG path of the clothing-target export skeleton under `GenHuman_Joint_GRP` (PRD §4). *Verify in Maya.*
- [!] **GenHuman version id method:** file name / version node / custom attr / external table?
- [!] **Clothing version-compat method** + version table format.
- [x] **Import vs reference** → **import, LOCKED** (handoff scenes must be self-contained; reference would break with no asset access). PRD FR-1.
- [x] **Multi-asset isolation** → **import into a per-instance namespace** (`coat:cloth_*`); resolves name collisions + clean detach. PRD §4.
- [x] **Attach mechanism** → `connectAttr` (vs parentConstraint / offsetParentMatrix / direct-skin); alternatives documented PRD §10.
- [~] **Fit-control attribute convention** (names/ranges) — DEFINED in `Clothing Asset Authoring Spec.md` §8 (`cloth_fit_ctrl`, `fit_*` keyable floats). Proposed; pending Tony sign-off, then fold into Addendum (PRD §7).
- [!] **Required Genie node names** list (get from Genie team).
- [!] **Preset storage:** JSON sidecar vs metadata node.
- [!] **GM_foot_L/R purpose:** redundant with `ik_foot_l/r`? → rename `foot_align_*` or merge.

---

## M0 — Rig hygiene (rename + cleanup)   *(not a blocker for the tool, but do first)*
**RE-BASED 2026-06-04: rename re-applied onto the NEW `GenHuman_rig_v02.ma` → `GenHuman_rig_v03.ma`.**
The rigger delivered a fresh-generation v02 (403,835 lines / 6,710 nodes, ~27.6 MB; old build kept as
`GenHuman_rig_v02_OLD.ma`, 341,042 / 8,451). The new gen is cleaner: gendered eye-mesh nodes (`e_GMan_*`,
`e_Gwoman_*`) and `GM_Body`/`GM_EyeBall` shaders are gone, so the rename collapsed to brand-token unification
+ the body-mesh rename. Script: `/tmp/apply_brand_rename_v2.py`. Verified: swapped tokens → 0 residual;
line/createNode counts identical pre/post; 0 new duplicate node names; **male/female switch wiring asserted present.**
- [x] Backup preserved: `GenHuman_rig_v02_OLD.ma` (original Apr build) **and** `GenHuman_rig_v02.ma` (new, untouched).
- [x] Bulk swaps: `GenMan_`→`GenHuman_` (6,166 hits), `GENHUMAN`→`GenHuman` (4,922 incl. shading nodes `GENHUMAN_SG/TX/SD/P2D`), `GHuman`→`GenHuman` (1 stray).
- [x] Body mesh `Mesh_GRPGENHUMAN_SKM`→`GenHuman_body_mesh` (+Shape/ShapeOrig/ShapeOrig1 follow).
- [x] **Male/female switch RESOLVED.** Switch = `god_m_godnode_anim.GH_Body_morph` (0–1) → blendShape `GH_BLN.w[0]` (body deform chain `GHT→GH_BLN→GH_SKC`). Testers' "no switch in v03" was because the OLD v03 was built from the OLD v02, which had only a *dangling* `GH_Body_morph` attr — no `GH_BLN`, no connection. The functional switch is a NEW-v02 feature; re-basing restores it. (`GH_Body_morph` confirmed by user as the male/female controller.)
- [x] Obsolete rules dropped: eye-mesh + `GM_Body`/`GM_EyeBall` renames no longer apply (nodes gone in new gen).
- [!] **VERIFY in Maya 2026:** open re-based `v03`, confirm it loads clean, no broken connections, body/Epic joints unchanged, **male/female `GH_Body_morph` slider drives the body morph**, Genie export still valid. *(Cannot be done outside Maya — rigger must confirm.)*
- [ ] **GM_foot_L/R** — left as-is (excluded). Real `foot_l`/`foot_r` exist; `GM_foot_*` are extra siblings under `calf_*`. Confirm purpose → rename `foot_align_*` or merge with `ik_foot_*`. (decision item)
- [ ] **GH_* nodes left untouched** — `GH_*_LAYER`, `GH_Body_morph`, `GH_BLN`, `GH_SKC`, `GHT`. These are functional (incl. the male/female switch) — leave names as-is unless a rename is specifically requested. (decision item)
- [ ] DEFER (face module) + KEEP (Epic skeleton + ik_*) — untouched, correct.
- [ ] (Stretch) File generator-fix ticket so re-gen stops reintroducing `GenMan_`/`GHuman`/`GM_`/`Gwoman` tokens (best long-term fix).

---

## M1 — Library + read-only browser
**STARTED 2026-06-04: package scaffolded under `scripts/snap_on_clothing/`; pure core built + headless-tested (19 passing).**
Core has zero `maya`/`PySide6` imports at module scope so validators run in CI; Maya/Qt confined to `ui/`.
Run tests: `cd tests && python -m pytest -q`. Dev preview: `PYTHONPATH=scripts python -m snap_on_clothing.launch`.
- [x] `config.py`: taxonomy (`ASSET_TYPES`), structure contract (groups/info/root/fit-ctrl), **CONNECT_ATTRS = translate/rotate/scale** (LOCKED), `EXPORT_SKELETON_GROUP`, install paths.
- [x] `core/asset.py`: `AssetMetadata` (spec §12 fields, compat list parse, validation w/ collected errors) + `ClothingAsset` (path/meta/thumb/sidecar/source/errors, valid/invalid).
- [x] `core/library.py`: recursive scan of roots for `.ma`; sidecar `.json` first then `cloth_info`; thumbnail discovery; invalid assets surfaced not dropped; `LibraryScanResult` (valid/invalid/by_type).
- [x] Lightweight `.ma` metadata read **without importing** — `core/ma_parse.py`: quote-aware statement tokenizer, `createNode`/`setAttr` string extraction, `summarize()` (node names+types, info attrs, cloth-joint list). No Maya.
- [x] `ui/window.py`: PySide6 `ClothingBrowser` (QMainWindow) shell; parents to Maya main window via `MQtUtil`/`wrapInstance` when present, standalone otherwise.
- [x] Library grid: `QListWidget` IconMode thumbnails (placeholder when none), type filter combo, live search, selection → read-only detail panel (name/type/version/compat/author/source/path/issues); status bar.
- [x] Launch via `snap_on_clothing.launch.run()` (Maya) or `python -m snap_on_clothing.launch` (standalone). Temp shelf wiring lands with the installer in M4.
- [x] **Setup tab + configurable library roots (2026-06-04):** user points the browser at one or more asset folders (external drive / shared server) once on a **Setup** tab. The Setup tab **reads and writes a plain-text store, `scripts/path.txt`** (one folder per line) — a tiny hand-editable "db" that sits beside the package and survives installer upgrades. `core/settings.py` (pure, headless-tested — read/write/add/remove, dedup-by-resolved-path, order preserved, comments+blanks ignored, unreadable-file tolerant). `effective_library_roots()` = saved roots else built-in defaults (installed + bundled). Browser scan + status bar use the resolved roots; clearing the file reverts to defaults. `ui/window.py` now a `Library`/`Setup` `QTabWidget`; `path.txt.example` ships beside the package; installer copies the example (never clobbers a real `path.txt`). `tests/test_settings.py` (13 tests).
- [!] **Verify in Maya 2026:** Setup tab — set a Local folder, confirm it writes `path.txt`, persists across relaunch, and its assets appear in the grid; `QFileDialog` folder picker works parented to Maya. *(Needs Maya.)*
- [x] **Local + Remote locations + Sync (2026-06-09):** Setup tab now sets **two** folders — `local` (the only folder scanned/worked from) and `remote` (shared master, never scanned). `path.txt` is now a keyed store (`local = …` / `remote = …`; legacy bare-line files still read, first folder → local). New pure `core/sync.py` `sync_remote_to_local(remote, local)`: one-way, additive (copies new + size/mtime-changed files, `copy2` preserves mtime so re-syncs skip unchanged), **never deletes**, won't clobber a locally-newer file; returns `SyncResult` (added/updated/skipped/errors + `.summary()`). `core/settings.py` rewritten to `Locations`/`read_locations`/`write_locations`/`set_local`/`set_remote`; `effective_library_roots()` → `[local]` else defaults (remote excluded). Setup tab: Local/Remote rows (Browse/Clear) + **Sync from remote ↓** button (wait cursor → summary → auto-refresh). Docs: User Guide §3 + `path.txt.example` updated. Tests: `test_settings.py` rewritten + new `test_sync.py` (9) — **105 headless tests passing.**
- [!] **Verify in Maya 2026:** Setup tab — set Local + Remote, press Sync; confirm new/changed assets land in Local, local-only assets survive, summary is accurate, grid refreshes; check sync of a real network/UNC remote. *(Needs Maya + a real remote share.)*
- [x] **Threaded Sync + progress (2026-06-19):** the *Sync from remote* button now runs the pull on a
  worker `QThread` (`ui/window.py::_SyncWorker`) so a large first pull over a slow network share no longer
  freezes Maya's UI. Pure `core/sync.sync_remote_to_local` gained an optional `progress` callback emitting
  `SyncProgress(phase=scanning|copying|done, done, total, current)` — headless-tested (`test_sync.py` +3).
  The Setup tab shows a `QProgressBar` (indeterminate during the remote walk, determinate `done/total` during
  the copy), disables the button while running, and re-enables + surfaces the summary on the main thread when
  finished. Worker throttles per-file `copying` updates to ~1/percent so a many-file library doesn't flood the
  event loop. Replaces the old synchronous wait-cursor. **169 headless tests passing.** *(In-Maya: confirm the
  bar animates and the UI stays responsive during a real network sync.)*
- [ ] (deferred) Scan cache for large libraries — still premature; revisit if scans get slow. A stale cache
  would risk hiding freshly-synced assets, so not worth it without a real perf problem.
- [!] **Verify in Maya 2026:** confirm `window.show()` parents/launches cleanly and `cmds`-free core imports under Maya's Python. *(Needs Maya.)*

---

## M2 — Validate → Attach → Detach lifecycle
**DONE (logic) 2026-06-04: full lifecycle built + headless-tested (41 tests total passing).**
Introduced `core/scene.py` `SceneGateway` (Protocol) as the Maya boundary — `MayaScene` is the real
`cmds` impl (lazy import); tests run an in-memory `FakeScene`. All attach/validate logic is therefore
unit-tested with no Maya. **Still needs in-Maya smoke (see `[!]` below).**
- [x] `core/validate.py`: `validate_asset_summary` (file-only: info node, required groups, `cloth_root`, ≥1 cloth joint, no `_jnt` suffix, no refs/namespaces, forbidden node types [blendShape/nCloth/nucleus], duplicate names) + `validate_scene_preconditions` (rig present, version compat, namespace free, Genie-required names). `Severity`/`Issue`/`ValidationReport`; **`ok` = no ERROR**.
- [x] Clear error reporting: every `Issue` carries `code` + offending `node` + `fix` hint; `Issue.__str__` renders "ERROR: msg [node] — fix: …".
- [x] `core/attach.py` `AttachEngine.attach`: resolves export-skeleton joints by **full DAG path** via `descendant_joints(EXPORT_SKELETON_GROUP)` (dual-skeleton safe — verified by test); matches `cloth_<name>`→body `<name>`; `connectAttr`s translate/rotate/scale per pair; **no networks created**; helper joints (no body match) left unconnected. **Transactional:** all pre-import checks first (scene byte-unchanged on reject); post-import failure rolls back (break applied edges + delete namespace).
- [x] `core/registry.py`: `Connection`/`AttachedInstance`/`InstanceRegistry`, keyed by namespace, `to_dict`/`from_dict` (ready for preset/scene-node persistence in M3).
- [x] `core/attach.py` `detach`: breaks **only** recorded connections, removes the instance namespace, never touches GenHuman; multi-asset independence proven (detach one keeps the other).
- [x] Import handling: `import_asset` does `file(i=True, namespace=…, mergeNamespacesOnClash=False)` per the import-into-own-namespace decision (no reference path — locked).
- [x] Tests: attach→connected, dual-skeleton path safety, detach→scene identical to pre-attach, multi-asset independence, validation-fail-leaves-scene-untouched, version-mismatch-blocks-pre-import, wrong-export-group rollback, locked-target rollback.
- [x] **UI wiring (2026-06-10):** `ui/window.py` Library tab now has an action bar — **`Attach ▸`** (attaches the grid-selected asset; `QInputDialog` prompts for the instance namespace, default = sanitized assetType; validation/precondition errors shown in a `QMessageBox`, scene untouched on reject) + **`Attached:` combo + `Detach`** (detaches the chosen live instance). The `AttachEngine` (with its in-session registry) is a **module-level singleton** (`_engine_singleton`) so reopening the browser keeps the attached list; created lazily from `MayaScene()`, with a clear "must run inside Maya" message when launched standalone. `py_compile` clean, 105 headless tests still pass (UI itself is not headlessly tested, consistent with the rest of `ui/`).
- [!] **Verify in Maya 2026:** load GenHuman + a real compliant asset; confirm `descendant_joints(EXPORT_SKELETON_GROUP)` resolves (this is the open `EXPORT_SKELETON_GROUP` path question), **the new Attach button** connects + garment follows playback, **Detach** restores. Needs a compliant asset (M5) + Maya.

---

## M3 — Fit / placement controls + presets
- [x] Define + document the **fit-control attribute convention** (tightness/thickness/length/region) — `Clothing Asset Authoring Spec.md` §8. *(Fold into the official Addendum once Tony signs off.)*
- [x] `core/controls.py`: discover `*_ctrl` nodes + keyable numeric user attrs in an instance namespace; `FitAttr`/`FitControl` models read each attr's min/max/default/value via the gateway; `set_fit_value` (clamped) / `reset_fit` / `reset_all`. Tool only writes values — builds no network.
- [x] `ui/controls_panel.py`: `FitControlsPanel` renders surfaced fit attrs as float sliders+spinboxes, placement vec3 rows, and preset save/load; every change calls into the headless core (no fitting logic in the UI). *(py_compile only — PySide6 ships in Maya.)*
- [x] `core/placement.py`: `Placement` value object (translate/rotate/scale + optional rotate-pivot "anchor"); `read`/`apply`/`reset` against a designated transform node; skips locked channels; pure transform, builds no nodes.
- [x] `core/presets.py`: `Preset` (fit values + optional placement), **namespace-relative addresses** so a preset is portable across re-attached instances; JSON sidecar `save`/`load`; `capture_preset`/`apply_preset` (missing controls→warnings, values clamped to target range).
- [x] Fallback: `surfaced_fit_attrs` prefers `fit_`-prefixed convention attrs; surfaces *all* keyable custom attrs on `*_ctrl` nodes only when no `fit_` attrs exist (Authoring Spec §8).
- [x] Gateway extended for M3: `AttrSpec` + `list_namespace_nodes`/`list_keyable_user_attrs`/`attr_spec`/`set_attr`/`get_vector`/`set_vector` on `SceneGateway`, `MayaScene` (lazy `cmds`), and `FakeScene` (custom-attr + vector support).
- [x] Tests: 19 new headless tests (controls discovery + prefer/fallback + clamp/reset, placement roundtrip + locked-skip + pivot, preset capture/JSON-roundtrip/namespace-portable apply/clamp+warn). **60 total passing.**
- [!] **Verify in Maya 2026:** import a real asset exposing `cloth_fit_ctrl` fit attrs; confirm sliders read authored min/max/default, drive the asset's fit deformers live, reset returns to neutral, placement nudges the instance, and a saved preset reproduces the look on a re-attached instance.

---

## M4 — Multi-asset, Genie export, packaging
**DONE (logic) 2026-06-04: multi-asset combos + export audit + installer core built & headless-tested (75 tests total).**
- [x] Multi-asset: shirt+pants+shoes / dress+shoes+hat / coat+pants+shoes; verify independence (detach one ≠ affect others); namespace/instance isolation. → `tests/test_multi_asset.py` (4 tests): realistic per-type joint coverage, all attached at once, detach-one leaves survivors live, detach-all returns scene to bare rig.
- [x] Genie export check: preserve required node names; confirm attach didn't mutate the rig / introduce nodes; DG stays lightweight. → `core/export.py` `audit_export_readiness(scene, registry)`: asserts (a) `GENIE_REQUIRED_NODES` all present (empty list ⇒ INFO, not fail), (b) export skeleton resolves ≥1 joint, (c) **every recorded edge is a transform-channel `connectAttr` whose dst is the instance's own clothing and whose src is a rig joint (never the reverse / never cross-instance)** — proving connectAttr-only + rig-untouched headlessly. `tests/test_export.py` (5 tests). *Live `.ma`/USD/FBX/Alembic export still an in-Maya smoke check (needs Maya + Genie node list).*
- [x] **Drag-and-drop installer (viewport):**
  - [x] `install.py` with `onMayaDroppedPythonFile()` at distribution root; wires Maya paths (`internalVar(userScriptDir)`, `config.user_asset_dir()`) to the pure core, then refreshes the shelf; `confirmDialog` + Script-Editor report.
  - [x] `install/installer_core.py` (pure, no maya): `install_package` copies `snap_on_clothing` → scripts dir (overwrite, skips `__pycache__`); `install_assets` merges bundled `assets/` **without clobbering** user files; `install()` orchestrates + returns `InstallResult`.
  - [x] Copy **bundled `assets/` library** → `~/maya/snap_on_clothing/assets/` (per-user root from `config.user_asset_dir()`); non-clobbering so user assets/paths survive.
  - [x] `installer/shelf.py`: create/refresh "Clothing" shelf button on a `SnapOnClothing` tab; button command imports the package lazily at click time. *(py_compile only — needs Maya.)*
  - [x] Idempotent re-run (upgrade): package re-copied fresh, every existing asset skipped (proven by `test_full_install_idempotent`).
  - [x] Success/failure reporting; `onMayaDroppedPythonFile` catches everything so Maya is never left broken.
  - [x] `tests/test_installer.py` (6 tests): overwrite-on-upgrade, pycache-skip, non-clobber merge, missing-source no-op, idempotent full run, missing-package failure.
  - [ ] Build distributable zip layout (`install.py` + `installer/` + `scripts/` + `assets/`). *(packaging step — do at release; layout already in place at repo root.)*
  - [!] **Verify in Maya 2026:** drop `install.py` into a clean 2026 profile → package lands in scripts dir, assets merge, shelf button appears + launches; re-drop upgrades without clobbering user assets. *(Needs Maya.)*
  - [!] **Verify in Maya 2026:** dress the rig with a real combo, run a `.ma`/USD/FBX/Alembic export, confirm Genie ingests it; supply the real `GENIE_REQUIRED_NODES` list. *(Needs Maya + Genie node list — `GENIE_REQUIRED_NODES` decision item.)*

---

## M5 — Docs, example asset, test scene  *(spec Deliverables)*
**DONE (deliverables) 2026-06-04: example asset + tool-user docs + in-Maya test-scene/build scripts. 95 headless tests (6 new).**
- [x] Author one **example compliant clothing asset** (`.ma`) → `assets/trench_coat_A/` (`trench_coat_A.ma` + `.json` sidecar + `README.md`). Hand-authored, **validator-passing**, Maya-loadable: required hierarchy (`Mesh_GRP`/`Rig_GRP`/`Ctrl_GRP` + `cloth_info`), full `cloth_*` connection skeleton (spine/neck/arms/legs, names = `cloth_` + EXACT body name, no `_jnt`), helper coat-tail joints, `cloth_fit_ctrl` with keyable `fit_*` floats (min/max/neutral), real cube geometry. Geometry is placeholder + **no skinCluster** (vertex/skin data can't be hand-authored safely) → the fully-skinned production build is generated in Maya by `examples/build_example_asset.py`. `tests/test_example_asset.py` (6 tests) validates the SHIPPED `.ma` through the real `ma_parse`+`validate`+`library` core every run, so it can't drift.
  - Parser fix: `core/ma_parse.iter_statements` now strips `//` line comments (outside strings) — Maya files use them as inline node dividers; previously a comment merged into the next statement and hid its `createNode`. Existing fixture had comments only at top/bottom so it never surfaced.
- [x] Build a **test scene**: GenHuman rig + clothing attached → `examples/build_test_scene.py` (in-Maya): imports `GenHuman_rig_v03.ma`, attaches asset(s) via the **real tool core** (`AttachEngine`+`MayaScene`, connectAttr-only, transactional), runs `audit_export_readiness`. *(needs Maya — py_compile verified; run as the M5 in-Maya smoke.)*
- [x] Docs: **asset-authoring side** → `Clothing Asset Authoring Spec.md`. **Tool-user side DONE** → `Snap-On Clothing — User Guide.md` (install/drop · Setup tab + `path.txt` · browse→validate→attach→fit→detach · full validation-error reference pulled from `validate.py`/`attach.py` · Genie export notes · supported versions · troubleshooting).
- [x] **Dev-only `examples/`** dir (excluded from the ship package, like `tests/`): `build_example_asset.py` (skinned asset generator + fit lattice driven by `cloth_fit_ctrl` SDK), `build_test_scene.py`, `__init__.py`, `README.md`. py_compile clean.
- [x] **Verify in Maya 2026 — `build_example_asset` DONE (2026-06-10):** ran `examples/build_example_asset.build()` from Windows Maya 2026 importing the script directly over the WSL UNC path (`\\wsl.localhost\Ubuntu-24.04\...`, no copy) → clean skinned `.ma` exported back into the WSL repo (100 KB, 27 joints, 2 skinClusters, ffd+lattice+baseLattice fit deformer, `cloth_info` network, SDK animCurves). Re-validated through the real core: `test_example_asset.py` 6/6 + full suite 105/105 green. *(`build_test_scene.build()` against `GenHuman_rig_v03.ma` — attach/follow/detach + export audit — still pending the M2/M3/M4 in-Maya smoke checks.)*
- [ ] (Future-proofing note) Keep architecture compatible with body-morph propagation.

---

## M6 — UI modernization + asset publish/metadata
**DONE (logic) 2026-06-11: publish core + capture + Publish tab + Library redesign. 122 headless tests (12 new).**
Driver: riggers will author garments **by hand** going forward (the `build_example_asset.py`
generator is now a dev fixture only), so thumbnail/polycount/metadata can only be captured
**in Maya at publish time**; the headless browser only *reads* the sidecar.
- [x] **Metadata model extended** (`core/asset.py`): `AssetMetadata` gains optional, non-validating
  fields `created`, `rig_version`, `tri_count`, `vert_count` (+`_INFO_FIELD_MAP` keys
  `created`/`rigVersion`/`triCount`/`vertCount`, lenient `_opt_int`). Old sidecars stay valid.
- [x] **Pure publish core** (`core/publish.py`, headless-tested): `PublishSpec` (+`to_sidecar()`
  using spec §12 attr names, `metadata()` round-trip), `destination_paths()` →
  `<dest>/<name>/<name>.{ma,json,png}`, `sanitize_asset_name()`, `write_sidecar()`,
  `validate_published_ma()` (reuses `validate_asset_summary` — same checks the browser uses),
  `today_iso()`.
- [x] **Maya capture** (`core/maya_publish.py`, lazy `cmds`, smoke-checked): `find_garment_meshes`
  (under `Mesh_GRP`), `poly_counts` (polyEvaluate tris+verts), `capture_thumbnail` (isolate +
  viewFit + single-frame off-screen playblast to PNG, restores viewport/selection),
  `detect_rig_version` (best-effort `v\d+` from GenHuman namespace), `save_ma` (whole-scene ASCII).
- [x] **Publish tab** (`ui/publish_panel.py`, wired into `window.py`): identity/version form +
  rig-version Detect + destination folder (defaults to Setup *local* lib) + thumbnail preview/Capture
  + Publish (poly_counts → copy/grab thumbnail → save .ma → write sidecar → re-validate → refresh
  Library). Clean "needs Maya" guard standalone. Overwrite confirm. **Pre-save rig block:**
  `maya_publish.scene_has_rig()` (any `GenHuman` node/namespace) → warns "Delete the rig before
  publishing" and aborts before writing, so a forgotten rig never produces a bloated/failing `.ma`.
- [x] **Library redesign** (`ui/window.py` + new `ui/style.py`): scoped dark QSS theme (rounded
  buttons, accent, card grid, type badge). Inspector details panel — **big preview image** on top,
  name + colored type badge, description, metadata grid (version/compat/**polycount**/**created**/
  **rig version**/author/source). **The long `File:` row is gone** — replaced by an elided
  (ElideMiddle, full path in tooltip) one-line row with **Copy** + **Open folder** buttons, so the
  path can never widen/crowd the preview. Larger thumbnail cards.
- [x] **Example builder** (`examples/build_example_asset.py`): after save, best-effort
  `_publish_sidecar_and_thumbnail()` routes through the same `core.publish`/`core.maya_publish`
  helpers, so `trench_coat_A` gets a real thumbnail + polycount + sidecar.
- [!] **Verify in Maya 2026:** open a hand-authored garment → Publish tab → Detect/Capture →
  Publish writes `.ma`+`.json`+`.png` into the local library → Library Refresh shows the new card
  with preview + polycount + created + rig version; Copy/Open path buttons work; theme renders.

---

## M7 — Fit-rig scaffolder (lower the rigger skill bar)
**DONE (logic) 2026-06-12: one-click fit rig so the rigger tunes extremes instead of wiring deformers. 132 headless tests (10 new).**
Driver: hand-authoring the `cloth_fit_ctrl.fit_*` → lattice SDK wiring (frontOfChain ordering,
neutral-relative lattice scale, driven keys) is the hardest part for a non-TD rigger. The fit
attrs are otherwise inert (sliders appear, deform nothing). Scaffolder builds the proven
trench-coat fit rig automatically on any open, already-skinned garment; rigger only tunes poses.
- [x] **Pure templates** (`core/fit_templates.py`, headless-tested): `FitDriver`/`FitAttrDef`/
  `FitTemplate` describe each type's `fit_*` attrs + how transform-level ones drive the lattice
  (modes `scale`/`offset`/`rotate`, neutral-relative). `fit_template(type)` → bespoke `hat`/`coat`,
  generic fallback (tightness+length). Region attrs (e.g. `fit_brim_width`) = attr only, no SDK.
- [x] **Maya scaffolder** (`core/maya_fitrig.py`, lazy `cmds`, smoke-checked): `scaffold_fit_rig(type)`
  creates `cloth_fit_ctrl`+attrs, a **frontOfChain** lattice over `Mesh_GRP` meshes, captures neutral
  lattice scale, authors default SDKs for transform attrs, resets to neutral, parents under `Ctrl_GRP`.
  Guards: refuses if `cloth_fit_ctrl` exists; errors on no mesh; **warns (not errors) on unskinned**.
  Logic mirrors `examples/build_example_asset.py` (single source-of-truth recipe now in templates).
- [x] **Publish-tab button** (`ui/publish_panel.py`): **"Scaffold fit rig"** uses the Type combo,
  wait-cursor, surfaces `ScaffoldResult.summary()` (auto-keyed vs manual point-key attrs) + warnings.
- [x] Tests: `tests/test_fit_templates.py` (16) — bespoke/generic lookup, case-insensitive, `fit_`
  prefix, defaults-in-range, region↔driver coherence, valid channels/modes, neutral-keyed,
  **+driver math (`_channel_value` scale/offset/rotate/unknown) + shared `author_fit_rig` via fake cmds**.
- [x] **Review fixes + dedup (2026-06-12):** (1) **BUG** — `scaffold_fit_rig` post-SDK reset set the
  now-driven lattice channels with `setAttr`, which Maya refuses on a connected plug (would fail the
  scaffold); removed — the ctrl reset already drives every keyed channel to neutral through its SDK
  curve. (2) Extracted shared `maya_fitrig.author_fit_rig(cmds, ctrl, lattice, template)` (the addAttr +
  neutral-relative SDK authoring); **`examples/build_example_asset._build_fit_control_and_lattice` now
  calls it from the `"coat"` template** instead of its own literal key loops, so the example and the
  in-tool scaffolder share ONE recipe and can't drift (`_FIT_ATTRS` deleted; build adds `<repo>/scripts`
  to `sys.path` so the core imports). Behaviour-preserving. (3) UI quick wins (exception-safe wait
  cursor, dead import, QSS no-op props) — see M6.
- [!] **Verify in Maya 2026:** skinned hat garment → Publish tab → **Scaffold fit rig** → confirm
  `cloth_fit_ctrl` gets `fit_*` sliders that deform via the lattice, fit follows body on playback
  (frontOfChain correct), neutral at 0; then point-key `fit_brim_width` by hand. **Also re-run
  `examples/build_example_asset.build()`** (now sources the fit rig from the shared core recipe) to
  re-confirm the coat exports identically (M5 re-verify).

---

## M8 — One-click cloth_* skeleton (no rig-import chore)
**DONE (logic) 2026-06-12: persist the one canonical skeleton + rebuild it with a button. 144 headless tests (12 new).**
Driver: there's exactly one GenHuman rig ⇒ one `cloth_*` export skeleton. Instead of
import-rig → duplicate → rename → prune every time, ship the skeleton as data and rebuild
it in-scene. Rigger then deletes the joints their garment won't skin to (per user: "we'll
let the rigger delete the joints that aren't relevant"), skins, and scaffolds the fit rig.
- [x] **Persisted data** (`scripts/snap_on_clothing/data/cloth_skeleton.json`): the canonical
  skeleton extracted from the verified `assets/trench_coat_A/trench_coat_A.ma` — **89 body-derived
  export joints** (full body chain + both arms incl. finger hierarchies + legs + twists + Epic
  `ik_*`/`interaction`/`center_of_mass` virtuals). Garment helper joints (`cloth_coatTail_*`)
  **excluded**. Per joint: local `t`/`r`/`s` (orientation is in `r` — rig has no `jointOrient`),
  `radi`, `ssc`. `Rig_GRP` frame = `-90 X`. Ships via installer `copytree` (data/ travels with pkg).
- [x] **Pure loader** (`core/skeleton.py`, headless-tested): `JointSpec`/`SkeletonSpec`,
  `load_cloth_skeleton()` (lru-cached), `validate_skeleton()` (unique names, parents defined-before-
  child = topological build order, `cloth_` prefix, root present). `skeleton_file()` = `package_dir/data`.
- [x] **Maya rebuild** (`core/maya_skeleton.py`, lazy `cmds`, smoke-checked): `build_cloth_skeleton()`
  creates framed `Rig_GRP` + every joint at its rest transform in hierarchy order; refuses if
  `cloth_root` exists; validates data first. `SkeletonBuildResult.summary()`.
- [x] **Publish-tab button**: **"Create cloth skeleton"** (above Scaffold fit rig — natural order:
  skeleton → skin → fit rig → publish). Wait-cursor, surfaces summary / errors.
- [x] **Regenerate from rig (UI, 2026-06-12):** **"Regenerate skeleton data from rig…"** button
  (confirm dialog — overwrites shipped data). `core/maya_skeleton.capture_cloth_skeleton_from_rig()`
  walks `EXPORT_SKELETON_GROUP`'s joint tree (rig-discovery mirrors `build_example._find_export_root`,
  selection-aware, namespace-robust), records each joint's LOCAL `t/r/jo/s/radi/ssc/ro` under a
  `cloth_<body>` identity (root parent → `Rig_GRP`, frame = export group's rotate), and writes via the
  pure `skeleton.write_skeleton()`. Helper joints excluded naturally (absent on the rig). Refreshes the
  canonical `cloth_skeleton.json` after a new rig gen with no hand-parsing.
- [x] **Pure serializer** (`core/skeleton.py`): `to_json_dict()` (full transforms, no zero-omission →
  deterministic), `write_skeleton(spec, dest=None)` (validates first, refuses invalid, clears the
  lru cache). Symmetric inverse of `load_cloth_skeleton()`.
- [x] Tests: `tests/test_skeleton.py` (15) — ships, 89 joints, valid, prefix, topo order, frame,
  landmarks, helpers excluded, defaults, cache, **+serializer round-trip / refuse-invalid / cache-clear**.
- [!] **Verify in Maya 2026:** empty scene → Publish tab → **Create cloth skeleton** → confirm
  framed `Rig_GRP` + full `cloth_*` chain appears at correct body rest pose; delete irrelevant joints,
  skin a mesh, Scaffold fit rig, Publish. Sanity-check joints sit on the imported GenHuman body.
- [!] **Verify in Maya 2026:** import GenHuman rig → **Regenerate skeleton data from rig** → confirm
  `cloth_skeleton.json` rewrites with 89 joints at the rig's pose; a subsequent **Create cloth skeleton**
  reproduces that pose. (Round-trip: regen from a freshly-built skeleton == original.)

---

## M9 — One-click "Delete unused joints" (post-skin prune)
**DONE (logic) 2026-06-15: replace the manual "delete the joints your garment won't skin to" chore
with a safe, explicit button. 160 headless tests (8 new).**
Driver: M8 rebuilds the full 89-joint skeleton; the rigger then hand-deletes the joints their garment
doesn't skin to. That's tedious and error-prone. Automate it — but **only the provably safe deletions**.
Hard invariant: attach `connectAttr`s each body joint's LOCAL `t/r/s` into the matching `cloth_*` joint,
so the `cloth_*` hierarchy must mirror the body exactly. Reparenting an interior joint changes its
children's local transforms and breaks that mirror — so interior joints are never touched.
- [x] **Pure planner** (`core/skeleton.py`, headless-tested): `plan_prune(parents, influences, root_joint)`
  → `PrunePlan(delete, kept_unweighted, survivors)`. The only sound rule: iteratively remove a joint that
  is a **leaf AND not a skin influence AND not `cloth_root`**, repeating until stable (deleting a leaf can
  expose its parent). Unweighted **interior** joints (skinned descendants) are reported in `kept_unweighted`
  and never deleted. `delete` is leaf-first (children precede parents). `is_noop` for "nothing to prune".
- [x] **Maya wrapper** (`core/maya_skeleton.py`, lazy `cmds`, smoke-checked): `plan_prune_unskinned(mesh_group)`
  gathers in-scene `cloth_*` joints + parents (`_scene_cloth_joints`) and skinCluster influences across
  `Mesh_GRP` meshes (`_skin_influences`, via `skinCluster -q -influence`), defers selection to the pure
  planner. **Refuses with zero joints or zero influences** — pruning a zero-influence scene would peel the
  whole skeleton (the foot-gun). `apply_prune(plan)` is the destructive half: deletes leaf-first, tolerates
  already-gone nodes. `PruneResult.summary()`.
- [x] **Publish-tab button**: **"Delete unused joints"** placed **before Scaffold fit rig** (order:
  skeleton → skin → **prune** → fit rig → publish). Two-phase confirm dialog (mirrors `_regen_skeleton`):
  computes the plan, shows DELETE vs KEEP (truncated previews) before any deletion, applies on Yes.
- [x] Tests: `tests/test_skeleton.py` (+8) — leaf delete, unskinned-branch removal, cascade (leaf-first
  order), keep-unweighted-interior, never-delete-root, zero-influence peels-to-root (documents the guard),
  and a real-skeleton "hat keeps head+ancestors, drops limbs" end-to-end.
- [!] **Verify in Maya 2026:** Create cloth skeleton → skin a hat mesh to `cloth_head` → **Delete unused
  joints** → confirm the dialog lists the limb leaves for deletion and the neck/spine as kept-unweighted,
  the head chain + `cloth_root` survive, then Scaffold fit rig + Publish succeed.

---

## M10 — Publish-tab log window + pre-publish sanity check
**DONE (logic) 2026-06-15: a full-width console log on the Publish tab, and a scene preflight that
catches the common authoring mistakes with actionable fixes. 170 headless tests (10 new).**
Driver: the single-line status strip got overwritten and couldn't explain *why* a publish was blocked.
A real test asset (`jacket_test.ma`, 350MB) exposed the gap: the rigger built a parallel setup and
**skinned the garment to the rig's own deform joints, not the `cloth_*` joints**, plus left the whole
asset inside namespaces (`jacket_A:…`) and the GenHuman rig in-scene — Publish only said "GenHuman in
scene", not the deeper problems.
- [x] **Full-width log** (`ui/publish_panel.py`): `QPlainTextEdit#logView` (styled in `ui/style.py`),
  spans the tab under the form/actions. `_log(msg, level)` → timestamped, color-coded (info/step/ok/
  warn/error), multi-line-aware, autoscrolls; `_report()` mirrors a headline to the kept status strip;
  `_clear_log()` button. Every action handler (skeleton/regen/prune/scaffold/capture/publish) now logs
  start + ok/warn/error instead of silently overwriting one label.
- [x] **Pure preflight** (`core/publish.py`, headless-tested): `SceneFacts` (gathered facts),
  `PreflightIssue(level, message, fix)`, and `assemble_preflight(facts)` → ordered issues. Checks: rig in
  scene, namespaces present (`root_namespaces`), missing required groups, no `cloth_root`, **garment
  skinned to non-`cloth_*` joints** (`split_influences` — the jacket_test failure), empty skinCluster,
  missing `cloth_info`. Errors block; unskinned / no-info-node are warnings; trailing `ok` when clean.
- [x] **Maya gatherer** (`core/maya_publish.py`): `gather_scene_facts()` (presence by short name so a
  namespaced asset isn't double-flagged as "missing groups") + `preflight_scene()` → pure `assemble_preflight`.
- [x] **Wiring**: new **"Check scene"** button (runs preflight, logs findings, no side effects). `_publish()`
  runs the preflight first — replaces the lone `scene_has_rig()` check — logs every issue with its fix and
  blocks on any error; on success/validation-failure it logs the outcome.
- [x] Tests: `tests/test_publish.py` (+10) — `root_namespaces`/`split_influences` helpers, clean-scene
  pass, rig flagged, namespaces flagged, **skin-on-non-cloth flagged** (+truncation), unskinned-is-warning,
  missing groups/root, info-node-is-warning.
- [!] **Verify in Maya 2026:** open a namespaced/rigged scene → **Check scene** → confirm the log lists
  rig + namespaces + (if applicable) non-`cloth_*` skinning, each with a fix; clean it up → Check scene
  passes → Publish succeeds and logs the destination.
- [ ] **Bug fixed alongside (M-misc):** `maya_publish.capture_thumbnail` passed the panel name as the
  `viewFit` object → "No object matches name: modelPanel4". Now `cmds.viewFit(meshes, panel=panel, …)`.

---

## M11 — Recommended skin-joint sets ("which joints do I bind to?")
Rigger feedback (2026-06-16): the full 89-joint body skeleton gives no signal which joints a garment
skins to — ~40 are fingers, plus `cloth_ik_*`/`cloth_interaction`/`cloth_center_of_mass`, and the
`*_twist_*` silhouette joints look skippable but aren't. Renaming joints to mark them is off the table
(attach matches `cloth_` by name). Solution: per-type recommended set + outliner colour, names untouched.
- [x] **Pure data** (`core/skin_sets.py`, headless-tested): `_RECOMMENDED` per asset type built from
  `_arm`/`_leg`/`_foot`/`_shoe` region helpers (twist joints **in** on purpose; fingers/IK/com **out**).
  `recommended_joints(type)`, `plan_skin_set(type, present_joints)` → `SkinSetPlan(include, missing)`
  intersecting recommendation with scene joints (graceful on a pruned/revised skeleton).
- [x] **Maya builder** (`core/maya_skeleton.build_skin_set`): resolves the plan against scene joints,
  rebuilds `cloth_skin_SET`, clears prior highlight off all `cloth_*` joints + paints the set green
  (override colour 14), leaves them selected for Bind Skin. Refuses if no skeleton / none recommended present.
- [x] **Wiring**: new **"Select skin joints"** button (uses the Type combo); Create-skeleton success now
  points the rigger to it. **Type combo starts unset** (placeholder, `currentIndex == -1`); Scaffold /
  Select-skin-joints / Publish all route through `_require_type()` and warn if the Type is still unset.
- [x] Tests: `tests/test_skin_sets.py` (+11) — every type non-empty, names all exist in the canonical
  skeleton (typo guard), twists included, fingers/IK excluded, foot upper-case match, order preserved,
  empty/missing handling, full-skeleton completeness.
- [!] **Verify in Maya 2026:** Create cloth skeleton → set Type → **Select skin joints** → confirm the
  recommended joints go green + into `cloth_skin_SET` + are selected; re-run with a different Type and
  confirm the old highlight clears; on a pruned skeleton confirm "not in scene" joints are logged, not errored.
- [x] **BUG — green highlight bleeds onto non-members (`_set_skin_highlight`, `core/maya_skeleton.py:321`).**
  FIXED 2026-06-18 (Option A) — clear now holds `overrideEnabled = 1` + `overrideColor = 0`. Live-in-Maya
  green-only display still to confirm (`[!]` in M13 Phase C).
  Verified 2026-06-17 against `m_ski_jacket_geo_skel.ma` (coat): the set + colour data are *correct* (exactly
  the 36 coat joints painted, none extra), but the **whole skeleton appears green in the viewport.** Cause:
  Maya draw-override colour **inherits down the DAG**, and the "clear" path sets `overrideEnabled = 0`, which
  makes a non-member *inherit its parent's* green instead of reverting to default. So non-member children of
  members go green: `cloth_head` (under green `cloth_neck_02`), all fingers (under green `cloth_hand_*`),
  feet/toes (under green `cloth_calf_*`). The `cloth_ik_*` branch is the one exception — it hangs off
  `cloth_root` (no override), so it correctly stays default-coloured and is *not* in the set.
  **Fix (Option A, minimal):** in `_set_skin_highlight`, on clear keep `overrideEnabled = 1` and set
  `overrideColor = 0` (default) instead of disabling the override — breaks the inheritance so non-members
  read as default. Boundary module = `py_compile`-only; verify the green-only display live in Maya.

## M12 — Male/female variants; retire the fit rig
**PLAN 2026-06-16; BUILT (logic) 2026-06-19 — Phases A–D done, 162 headless tests passing; in-Maya
verify (`[!]` below) still pending.** New direction (user): production uses only **two fixed body states — pure male and
pure female** (`GH_Body_morph` is only ever 0 or 1; no intermediate blends, no other morph axes). So the
runtime *fit* layer (M3 fit controls + M7 lattice scaffolder) is pure overhead — there's no shape variation
to compensate for. Instead the **modeler hand-fits each garment once** on the male body and once on the
female body; those two `.ma`s are the raw assets. The closet gets **Male / Female tabs**. Attach (pose) and
skinning are unchanged. The proper long-term answer to shape variation remains **body-morph propagation**
(backlog) — dropping the lattice rig doesn't burn that bridge. Taxonomy: **male / female only** (no unisex).

> **Two facts confirmed by the user (2026-06-16) that shape this milestone:**
> 1. **`GH_Body_morph` moves only the body MESH, not the joints.** ⇒ the `cloth_*` skeleton rest pose is
>    identical for male and female — **one skeleton serves both; no per-gender skeleton (Phase C dropped).**
>    This also *justifies* the two-mesh model: because joints don't move, a single garment skinned to them
>    can't follow the male↔female mesh difference, so two pre-fit garment meshes are the only thing that works.
> 2. **Tool unreleased, no complete assets exist yet.** ⇒ no asset migration; `gender` can be a clean
>    **required** field with zero legacy tolerance — only the dev fixture (`trench_coat_A`) needs tagging.

### Phase A — remove the fit rig (retires M3 + M7)   *(DONE 2026-06-19; 156 headless tests passing)*
- [x] Delete pure modules: `core/fit_templates.py`, `core/maya_fitrig.py`, `core/controls.py`,
  `core/placement.py`, `core/presets.py`.
- [x] Delete UI: `ui/controls_panel.py`. (It was never wired into `ui/window.py` — only a stale docstring
  line, now removed.)
- [x] Delete tests: `tests/test_fit_templates.py`, `test_controls.py`, `test_placement.py`, `test_presets.py`.
- [x] `ui/publish_panel.py`: removed the **"Scaffold fit rig"** button + `_scaffold` handler (kept Create-
  skeleton / Delete-unused / Connect/Disconnect-test-body / Check-scene / Publish). Trimmed stale
  "before Scaffold fit rig" / "joints and fit rig" tooltips.
- [x] `config.py`: removed `FIT_CTRL`, `FIT_ATTR_PREFIX` (grep-confirmed no residual refs).
- [x] **Trimmed `core/scene.py` + `tests/_fake_scene.py`:** removed the M3-only gateway methods
  (`AttrSpec` dataclass, `list_namespace_nodes`, `list_keyable_user_attrs`, `attr_spec`, `set_attr`,
  `get_vector`/`set_vector`) — all had zero callers after the deletes. Kept `is_locked` (attach) +
  `world_matrix`/`set_world_matrix` (attach align). Also dropped the fake's `define_attr`/`_CustomAttr`/
  `custom`/`vectors` plumbing.
- [x] `examples/build_example_asset.py`: stripped the fit-lattice / `cloth_fit_ctrl` generation
  (`_build_fit_control_and_lattice` → `_build_controls`, keeps only the `cloth_coatTail_ctrl` secondary
  control). Builder stays a skinned-asset fixture only.
- [x] **Decision RESOLVED — stay silent.** `validate_asset_summary` is unchanged; further, the dead
  `SceneFacts.has_fit_ctrl` field (set in `maya_publish`, never read by `assemble_preflight`) was removed.
  The shipped `trench_coat_A.ma` still contains a `cloth_fit_ctrl` (regenerable only in Maya) and stays
  valid; the `test_example_asset` assertion that required it was dropped.
- [x] Docs: dropped the fit-control + Scaffold workflow from `Snap-On Clothing — User Guide.md` (§5 is now
  "Male / female variants") and `Clothing Asset Authoring Spec.md` (§8 rewritten to the two-variant model;
  intro TL;DR / Ctrl_GRP tree / §15 note / §16 checklist / §17 workflow updated). Noted the male/female
  model throughout. `__init__.py` docstring de-fit-ed.

### Phase B — gender as a first-class asset dimension   *(DONE 2026-06-19)*
- [x] `config.py`: `GENDERS: tuple[str, ...] = ("male", "female")`.
- [x] `core/asset.py`: **required, validated** `gender` field on `AssetMetadata` (must be in `GENDERS`,
  case-normalized to lower); `_INFO_FIELD_MAP["gender"]`; `ClothingAsset.gender` property. Sidecars/cloth_info
  without gender → invalid with "missing 'gender'"; bad value → "gender 'x' not one of …".
- [x] `core/publish.py`: `PublishSpec` carries `gender`; `to_sidecar()`/`metadata()` round-trip it.
- [x] `core/library.py`: `by_gender(gender)` + gender first in the sort key (`(gender, type, name)`).
- [x] `ui/publish_panel.py`: **Gender combo** (unset default + placeholder, `_require_gender()` mirroring
  `_require_type()`); `_gather_spec` requires it; publish summary logs `(<gender> <type>)`.
- [x] `ui/window.py`: **Gender filter combo** beside the Type filter ("All genders" + male/female);
  `_apply_filter` honours it; gender shown in the inspector detail grid.
- [x] Tagged the dev fixture: `gender` added to `assets/trench_coat_A/{trench_coat_A.json,trench_coat_A.ma}`,
  the static `tests/fixtures/sample_coat.ma`, the `_assets.write_asset_ma` builder, and example builder
  (`_build_info_node` + publish spec). All test fixtures updated for the required field.
- [x] **Decision (user 2026-06-19):** library layout for a pair = two sibling folders sharing
  `assetName`+`assetType`, **prefix-named `m_<name>` / `f_<name>`** (e.g. `m_trench_coat_A` /
  `f_trench_coat_A`), distinct files/sidecars. No scanner change; the gender tabs do the split.

### Phase C — skeleton stays gender-agnostic  *(DONE 2026-06-19 — guard test only)*
- [x] `GH_Body_morph` doesn't move joints, so the single shipped `cloth_skeleton.json` serves both
  genders; M8/M11 unchanged. Added `test_skin_set_joints_are_gender_independent` (asserts `recommended_joints`
  / `plan_skin_set` take no `gender` param and are stable per type).

### Phase D — tests, suite, docs   *(DONE 2026-06-19)*
- [x] New headless tests: gender-required + bad-gender + case-normalize (`test_asset.py`), `by_gender` +
  sort-order (`test_library.py`), gender survives publish sidecar round-trip (`test_publish.py`), Phase C
  guard (`test_skin_sets.py`). **162 headless tests passing.**
- [x] Updated all fixtures for the required field; `py_compile` clean on the Maya-boundary modules
  (`publish_panel`, `window`, `maya_publish`, builder).
- [x] Synced `prd.md` (M12 amendment banner superseding FR-4/FR-7/§7 + controls/placement/presets) +
  `Snap-On Clothing Rig System.md` (two-variant note); Authoring Spec §12 + validator hint + User Guide
  validation row now list `gender`. Memory updated (`m12-…`, `publish-tab-authoring-helpers`,
  `recommended-skin-joint-sets`).
- [!] **Verify in Maya 2026 (end-to-end):** with the single shared skeleton, author one garment's male
  variant (Create skeleton → Select skin joints → bind → prune → Publish[gender=male]) on the male body and
  its female variant on the female body; confirm both attach + follow playback on the matching body, and the
  browser shows them under the right tab.

## M13 — In-scene skinning test + Create-skeleton consolidation
**PLAN 2026-06-17.** Two coupled changes to the authoring workflow. (a) Drop the standalone "Select skin
joints" button — fold the skin set into "Create cloth skeleton" so one click (after the Type is chosen)
builds the skeleton *and* the recommended `cloth_skin_SET`. (b) New **skinning test**: let the rigger drive
the `cloth_*` skeleton from the GenHuman body already in the authoring scene so they can pose the rig and
confirm the garment deforms before publishing. This is authoring-time `attach()` — same `connectAttr`
body→`cloth_*` plugs as production, minus the import.

> **Decisions locked (user, 2026-06-17):** body is **already in the authoring scene** → connect the existing
> `GenHuman_Joint_GRP` export skeleton, **no import / no namespace management**. **Body only** — no canned
> range-of-motion clip.

### Phase A — fold skin set into Create-skeleton (adjusts M11)
- [x] `publish_panel._create_skeleton`: add the `_require_type()` guard up front, then after
  `build_cloth_skeleton()` also call `maya_skeleton.build_skin_set(asset_type)` in the same click; report
  both results (skeleton built + N skin joints highlighted). Update the "Next:" log to point at Bind Skin.
- [x] Remove the `_skin_set_btn` widget + `_select_skin_joints` handler; retitle the Create-skeleton tooltip
  ("…builds the skeleton and selects the joints to bind to"). `core.maya_skeleton.build_skin_set` stays — it's
  just no longer a separate user step (still covered by `tests/test_skin_sets.py`).
- [x] Fix the green-highlight inheritance bug here (the M11 entry above): in `_set_skin_highlight`, on clear
  keep `overrideEnabled = 1` + `overrideColor = 0` instead of disabling the override.

### Phase B — skinning test (connect/disconnect in-scene body)
- [x] New Maya-boundary module (`core/maya_testfit.py`, or extend `maya_skeleton.py`): `connect_test_body()`
  — locate `GenHuman_Joint_GRP` via the existing `_find_export_root`; align cloth `Rig_GRP` to its world
  frame (the `attach._align_root_group` logic); `connectAttr` body→`cloth_*` `{translate,rotate,scale}`
  (`config.CONNECT_ATTRS`) for every joint whose base name matches (same matching as
  `attach.plan_connections`). Skip locked / already-driven plugs with clear messaging. Returns a count +
  any skips.
- [x] `disconnect_test_body()` — break exactly those connections so the `cloth_*` joints go static and
  publish-safe again. Idempotent / tolerant of already-broken edges.
- [x] Two buttons on the authoring tab ("Connect test body" / "Disconnect test body"), wired like the other
  helpers (`_require_maya`, wait cursor, log + status, message box on error). Connect refuses clearly if no
  cloth skeleton or no GenHuman in scene; points the rigger to pose the body's controls and watch the garment.
- [x] Preflight guard: add a check to `maya_publish.preflight_scene()` for `cloth_*` joints with **incoming
  connections** → warn ("disconnect the test body before publishing"). The existing `scene_has_rig()` blocker
  already catches a leftover body; this catches the connection specifically.

### Phase C — tests + docs
- [x] Headless: the connect/disconnect planning/matching is pure-able — unit-test the name-matching + the
  skip-locked/already-connected rules against a fake scene (mirror `tests/_fake_scene.py`); `py_compile` the
  boundary module.
- [x] Update docs (User Guide authoring workflow: Create skeleton → bind → **test on body** → prune →
  publish) and memory (`recommended-skin-joint-sets` — button folded in; `publish-tab-authoring-helpers`).
- [!] **Verify in Maya 2026:** with a GenHuman + a skinned garment in scene, Connect test body → pose the
  body → confirm the garment deforms; Disconnect → confirm cloth joints static again and Publish no longer
  blocks on the connection.

## M14 — Tool-provided gendered test body (load the matching GenHuman)
**BUILT (logic) 2026-06-19.** Direction (user): the tool should *provide* the correct-gender body for
skinning/test-fit, not assume the rigger placed one. Since male/female are the **same rig** differing only
by `GH_Body_morph` (0 = male base, 1 = female morph; the morph moves the MESH, not the joints), the tool
ships **one** GenHuman and flips the switch to match the garment's chosen Gender. Supersedes the M13
"body already in scene, no import" assumption (Connect/Disconnect remain as the connect/disconnect halves).
- [x] **Config** (`config.py`): `BODY_MORPH_NODE`/`BODY_MORPH_ATTR` (`god_m_godnode_anim.GH_Body_morph`),
  `GENDER_BODY_MORPH = {"male":0.0,"female":1.0}` (**values verify-in-Maya**), `BUNDLED_GENHUMAN_FILE`,
  `bundled_genhuman_path()` → `data/genhuman/<file>` (ships via installer copytree).
- [x] **Pure** (`core/testfit.py`): `body_morph_value(gender)` (case-insensitive, raises on unknown) —
  headless-tested.
- [x] **Maya** (`core/maya_testfit.py`): `load_test_body(gender)` — refuses if a GenHuman is already in
  scene / no cloth skeleton / bundled file missing; imports the rig at root, sets the morph, then runs the
  existing `connect_test_body`. `remove_test_body()` = `disconnect_test_body` + robust `_delete_genhuman`.
  `LoadBodyResult`/`RemoveBodyResult` summaries. (`_genhuman_present`, `_set_body_morph` helpers.)
- [x] **UI** (`ui/publish_panel.py`): the two M13 buttons become **"Load test body"** (`_require_gender`
  → `load_test_body`) / **"Remove test body"** (`remove_test_body`); tooltips explain the morph flip.
- [x] **Bundle**: `data/genhuman/` with a tracked `README.md`; the rig `.ma` is **gitignored** (large, like
  the root rigs) — copied in for local dev, included at package/release time. No installer change (data/
  already copytree'd).
- [x] Tests: `tests/test_testfit.py` (+4) — per-gender morph value, case-insensitive, rejects unknown,
  every `config.GENDERS` maps. **166 headless tests passing.** Docs: Authoring Spec §17 workflow (Load/Remove
  + set Gender) updated.
- [!] **Verify in Maya 2026:** pick Gender=female → **Load test body** → confirm the bundled GenHuman
  imports, `GH_Body_morph` reads 1 (female), the body drives the `cloth_*` skeleton; **confirm 0=male /
  1=female is correct** (flip `GENDER_BODY_MORPH` if reversed); **Remove test body** → rig gone, joints
  static, Publish unblocked. Confirm the bundled `data/genhuman/GenHuman_rig_v03.ma` is present in the build.

## Backlog / future
- [~] Asset **validator/exporter** tool for authors (enforce Addendum at export time).
  **Export-time cleanliness rules added 2026-06-20:** the publish/export path already validated
  structure (groups, `cloth_root`, info node, refs/namespaces, blendShape/sim, dup names). Added the
  rest of the Authoring Spec §10/§13/§11 hard-"no" list to `validate_asset_summary` (runs on the saved
  `.ma` via `validate_published_ma`, and in the browser): **unknown/lost-plugin nodes** (`unknown_node`),
  **timeline animation curves** (`anim_curve` — `animCurveT*` only; set-driven keys `animCurveU*` stay
  allowed, the example asset drives its fit lattice with `animCurveUU`), **non-default display layers**
  (`display_layer`), and **render-engine shaders** (`renderer_shader` — curated denylist of Arnold/
  Redshift/V-Ray/RenderMan/mental-ray material types; generic lambert/standardSurface pass). New
  `config` constants (`UNKNOWN_NODE_TYPES`, `TIMELINE_ANIM_CURVE_TYPES`, `DISPLAY_LAYER_TYPE` +
  `DEFAULT_DISPLAY_LAYERS`, `RENDERER_SHADER_TYPES`) + `MaSummary.nodes_of_types`. Mirrored as
  in-scene **preflight** errors so authors catch them before the save: 4 new `SceneFacts` fields +
  `assemble_preflight` blocks, gathered in `maya_publish._cleanliness_facts` (tolerates unregistered
  renderer types via per-type `ls`). Publish-tab UI renders them with no change (generic issue list).
  **181 headless tests passing** (+12). *(In-Maya: confirm a scene with a renderer shader / leftover
  display layer / baked keys is blocked by the Publish preflight, and a clean garment still publishes.)*
  REMAINING (need connection/attr graph that `ma_parse` doesn't capture — a future in-Maya check):
  **unused materials**, **leftover construction history on meshes**, **frozen-scale (=1)** verification,
  and **valid-UVs**. These are best gathered live in `maya_publish` (deferred until needed).
- [ ] Body-morph propagation to attached clothing. **DEFERRED to a later phase (reaffirmed
  2026-06-20).** Staying with two pure variants (male + female); an in-between body shape is a
  **manual hand-adjustment by the artist**, not tool interpolation. Don't start without a fresh go-ahead.
- [x] ~~Migrate GenHuman materials to generic shaders~~ — **CUT 2026-06-20 (executive decision).**
  The tool does **not** touch GenHuman shaders: GenHuman is leveraged only as (a) the body the artist
  fits/skins the garment against and (b) the attach target. Its materials are a **different department's**
  concern — out of scope. The generic-shader material rule (Authoring Spec §11) is still **enforced on
  published clothing** (done — `renderer_shader` check in `validate_asset_summary` + Publish preflight).
- [ ] Deferred facial-module naming standardization pass (Tier 3).
