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
- [ ] (deferred) Run Sync on a worker thread so a large first pull over a slow network doesn't block Maya's UI; show progress. Synchronous wait-cursor is fine for now.
- [ ] (deferred) Scan cache for large libraries — premature now; revisit if scans get slow.
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

## Backlog / future
- [ ] Asset **validator/exporter** tool for authors (enforce Addendum at export time).
- [ ] Body-morph propagation to attached clothing.
- [ ] Migrate GenHuman materials to generic shaders (per Addendum material rule).
- [ ] Deferred facial-module naming standardization pass (Tier 3).
