# PRD — GenHuman Snap-On Clothing Browser & Attach Tool

**Status:** Draft v1 · 2026-06-03
**Owner:** Shannon
**Source of truth:** `Snap-On Clothing Rig System.md` (Tony Hudson, 5/15/2026) + its Addendum.
**Target host:** Maya **2026** (Python 3, PySide6) · GenHuman rig `GenHuman_rig_v02.ma`

> This PRD does **not** invent a new system. It is the implementation plan for the system already
> specified in `Snap-On Clothing Rig System.md`. Where this document and the spec disagree, **the
> spec wins** — flag the conflict here rather than silently diverging.

---

## 1. Goal

A Maya Python tool that lets an artist **browse local clothing assets, snap a chosen asset onto the
animated GenHuman rig, adjust its fit/placement, and detach it cleanly** — with no simulation, no
constraints on the connection, and full Genie-export compatibility.

---

## 2. How the spec constrains the design (read this first)

The spec is opinionated, and it **removes** several things a naive "clothing tool" would do. These are
the deltas that matter:

| Naive assumption | What the spec actually requires |
|---|---|
| Tool auto-binds garment and transfers skin weights from the body mesh. | ❌ No. **Assets are pre-rigged.** The asset author duplicates the required GenHuman joints, smooth-binds the garment to those `cloth_*` joints, and exports `.ma`. The tool only **`connectAttr`s** matching joints. (Addendum: "Smooth bind only. Geometry must be skinned to clothing joints.") |
| Tool builds a deformer stack (shrinkwrap/lattice/push) to create fit. | ❌ Not by the tool. **Deformers are permitted but authored into the asset.** The tool only **surfaces and drives** controls/attributes the asset already exposes. (Connection model forbids the tool from creating "constraints, utility nodes, matrix nodes, expressions, driven keys, or intermediate connection networks.") |
| Fit done with blendshapes / corrective morphs. | ❌ "Blendshapes are not supported." Fit must come from the asset's permitted deformers (lattice, cluster, shrinkWrap, push) driven by its own `cloth_*_ctrl` nodes. |
| Garment follows the body via cloth simulation. | ❌ "No simulation." Garment follows via direct joint connection only. |
| Tool connects to "the skeleton." | ⚠️ There are **two** skeletons (export + rig-internal deform) with identical short names. Connections must target the **export skeleton under `GenHuman_Joint_GRP`** unambiguously (full DAG path / namespace). See §5. |

**Net effect:** the spec makes the tool *thinner* (browse → validate → `connectAttr` → surface controls
→ detach) and pushes the heavy rigging into an **asset-authoring contract** (the Addendum). The tool's
job is matching, validation, connection lifecycle, and a control-surfacing UI — **not** skinning or
deformer construction.

This also reconciles the earlier design conversation:
- *"Skin transfer / rig binding"* → realized as **pre-skinned asset + `connectAttr` joint→joint**, not runtime weight transfer.
- *"Fit sliders + placement transforms"* → realized as **a generic attribute panel that drives the asset's authored fit controls + a top-level placement offset**, not tool-built deformers.

---

## 3. Scope

### In scope
- Local clothing **asset library** browser (scan folders of `.ma` assets + metadata/thumbnails).
- **Validation** of asset compatibility against the current GenHuman rig (hard-stop on failure).
- **Attach**: `connectAttr` matching `cloth_*` joints to GenHuman body joints.
- **Multiple simultaneous** clothing assets, mutually independent.
- **Fit & placement controls**: surface the asset's authored controls + a placement offset (§7).
- **Detach**: remove only the clothing↔GenHuman connections; leave geometry/rig/other assets intact.
- **Presets**: save/load fit + placement values per asset instance.
- **Genie export** compatibility (preserve required node names, keep DG lightweight).
- Shelf-button launcher + drag-and-drop installer.

### Out of scope (per spec)
- Cloth simulation, constraints, expression/driven-key networks on the connection.
- Tool-side skinning or weight transfer.
- Blendshapes / corrective morphs for fit.
- Authoring tools for *making* clothing assets (that's the Addendum's manual workflow; we only **consume** validated assets). A future asset-validator/exporter is a separate deliverable.

---

## 4. The clothing-connection contract

This is the immutable interface between body and clothing. Locked by `rig_naming_rename_map.csv` (Tier 0).

- **Body/export skeleton = Epic/Unreal mannequin skeleton, verbatim.** Names like `root, pelvis,
  spine_01..05, clavicle/upperarm/lowerarm/hand_l|r, [finger chains], neck_01/02, head,
  thigh/calf/foot/ball_l|r, *_twist_01/02_l|r, ik_*`. **Never renamed** — renaming breaks UE
  retargeting and game export.
- **Clothing joint name = `cloth_` + exact body joint name** (no `_jnt` suffix). e.g. body `spine_03`
  → clothing `cloth_spine_03`. This naming is the matching key.
- **Connection = direct `connectAttr` only.** Transform attributes to connect — LOCKED 2026-06-04:
  connect the `.translate` / `.rotate` / `.scale` compounds; `jointOrient` OFF (static, identical on the
  duplicate — connecting double-applies orientation); `visibility` not connected. **Scale is required**
  (not optional): animators scale body joints to seat the character into a matchmove, and the clothing
  must scale with them or it floats/clips. Consequence for asset authors: clothing skinning + fit
  deformers must deform cleanly under non-uniform joint scale.
- **Helper/secondary joints and controls stay UNconnected** and remain animator-accessible — this is
  where "movement control" of coat tails, skirts, straps lives.

### Per-instance namespace contract (RESOLVED 2026-06-04)
Each asset is **imported into its own namespace** at attach time:
`cmds.file(path, i=True, namespace="<instance>", mergeNamespacesOnClash=False)` → `coat:cloth_spine_03`,
`coat:cloth_root`, etc. This is independent of the import-vs-reference choice (we import — see FR-1) and
is what makes "multiple simultaneous assets" actually work: a shirt and a coat both contain
`cloth_spine_03` / `cloth_root` / `cloth_info` / `Mesh_GRP`, which would silently collide-and-rename in
the root namespace and break both name-matching and the `connectAttr` targets. The asset **file** stays
namespace-free (Addendum rule preserved); the namespace is applied at import and bakes into the
handed-off scene. Detach = break recorded connections then delete the instance namespace. The tool
resolves clothing joints as `<namespace>:cloth_<bodyJointName>`.

### Dual-skeleton caveat (new finding — must verify in Maya)
The rig contains the export skeleton **and** a rig-internal deform skeleton sharing identical short
names (confirmed: `root`, `pelvis`, `spine_01`, `clavicle_l`, `thigh_r` each appear twice in the `.ma`).
Attach logic **must** resolve the **export skeleton under `GenHuman_Joint_GRP`** by full DAG path, never
by short name, or it risks wiring clothing to the wrong skeleton. **Open task:** confirm which skeleton
is the intended clothing target and document the canonical path.

---

## 5. Functional requirements

### FR-1 Asset library browser
- Scan one or more configured local directories for clothing `.ma` assets.
- Read each asset's **version "info" node** + metadata (type, supported GenHuman versions, thumbnail).
- Display as a browsable, filterable grid (by type: shoes/pants/shirt/dress/coat/hat).
- **Import (not reference) — LOCKED 2026-06-04.** Rationale: scenes are handed off to artists who may
  not have access to the clothing asset files; a reference would resolve to missing geometry/broken
  paths on their machine, while import bakes the garment into the scene so it travels self-contained.
  Reference's only edge (master-edit propagation) is moot once a scene is handed off. Import into a
  **per-instance namespace** (see §4) for multi-asset isolation.

### FR-2 Validation (hard stop, scene-unchanged on failure)
Mirror the spec's two validation lists. Before attach, verify:
- GenHuman rig present in scene; version compatible.
- Asset structure valid: `Mesh_GRP` / `Rig_GRP` / `Ctrl_GRP`, valid root joint, version info node.
- Required `cloth_*` joint names match the convention; required attrs exist; types compatible.
- Targets not locked / not already invalidly connected.
- No duplicate node names; no namespace conflicts; Genie-required names present.
- Multiple assets can coexist without collision.
- On any failure: **hard stop**, clear error (what failed / which node / how to fix), **no partial connections**.

### FR-3 Attach
- For each matching joint pair, `connectAttr` the agreed transform attributes (export skeleton → `cloth_*`).
- No constraints/utility/expression nodes created.
- Idempotent and reversible; record what was connected for clean detach.

### FR-4 Fit & placement controls (see §7)
- Surface the asset's authored fit controls as a generic attribute panel (sliders).
- Provide a **placement offset** transform above the garment for translate/rotate/scale nudge + anchor.

### FR-5 Detach
- Break **only** clothing↔GenHuman connections recorded at attach.
- Do not delete geometry/joints/controls; do not modify GenHuman; do not affect other assets.

### FR-6 Multiple assets
- Track each attached asset instance independently via its **import namespace** (§4) backed by an
  instance registry recording what was connected.
- Detaching one never affects another (break that instance's recorded connections, delete its namespace).

### FR-7 Presets
- Save/load fit + placement values per attached instance (JSON sidecar or asset metadata).

### FR-8 Genie export compatibility
- Preserve required node names; keep connection graph lightweight (`connectAttr` only).
- Validate exportability to `.ma` / USD / FBX / Alembic is not broken by attach.

### FR-9 Packaging & drag-and-drop install
- **Single drag-and-drop installer dropped into the Maya viewport.** A top-level `install.py`
  implementing `onMayaDroppedPythonFile(obj)` (Maya's viewport-drop entry point) that runs the install
  with zero manual steps.
- The installer must be **self-contained / bundle everything**: the `snap_on_clothing` Python package,
  all lib files, **and** the starter clothing **asset library** (example assets + thumbnails/metadata).
- On drop it must:
  1. Copy the package to the user's Maya scripts dir (e.g. `~/maya/2026/scripts/snap_on_clothing/`).
  2. Copy the bundled **asset library** to a known location (e.g. `~/maya/snap_on_clothing/assets/`)
     and register that path as a default library root in `config.py` (don't clobber user-added paths).
  3. Create/refresh the **shelf button** that launches the UI.
  4. Be **re-runnable** (idempotent upgrade — overwrite package, merge config, keep user assets/paths).
  5. Report success/failure in the Script Editor; leave Maya usable on failure.
- Distribution form: a single folder/zip the artist unzips, then drags `install.py` into the viewport.

---

## 6. Architecture (proposed, spec-aligned)

```
maya_clothing_rig/
  scripts/snap_on_clothing/
    __init__.py
    ui/
      window.py          # PySide6 main window: library grid + controls panel
      controls_panel.py  # generic attribute-surfacing sliders for asset controls
    core/
      library.py         # scan dirs, read info node + metadata + thumbnails
      asset.py           # asset model: type, version, joints, controls, root/info nodes
      validate.py        # spec's hard-stop validation checks
      attach.py          # connectAttr lifecycle (export-skeleton path resolution)
      placement.py       # top-level offset group + anchor handling (no networks)
      controls.py        # discover + drive asset-authored fit controls
      presets.py         # save/load fit + placement per instance
      registry.py        # track attached instances for independent detach
    config.py            # library paths, attr-connect set, version table
  install.py             # DRAG INTO VIEWPORT → onMayaDroppedPythonFile(); self-contained installer
  installer/             # package name != drop-file stem, else it shadows install.py on sys.path
    installer_core.py    # copy package, copy asset library, build shelf button, idempotent upgrade
    shelf.py             # shelf-button creation/refresh
  assets/                # BUNDLED starter clothing library shipped with the installer
    <type>/<asset>.ma + <asset>.json + <asset>_thumb.png
  tools/
    rename_genhuman.py   # rig hygiene script (§8), run INSIDE Maya
  prd.md  todo.md  Snap-On Clothing Rig System.md  rig_naming_rename_*.csv
```

---

## 7. Fit & shape controls — how they work *within* the spec

Because the tool may not build deformers or blendshapes, fit is a **contract + surfacing** feature:

1. **Asset-authoring contract (Addendum extension):** a compliant asset *may* expose a
   `cloth_fit_ctrl` (or per-region controls) whose custom attributes drive **permitted deformers**
   authored inside the asset:
   - *tightness/looseness* → `shrinkWrap` weight or `push`/displacement offset toward the body
   - *thickness* → `push` amount
   - *length / region scale* → `cluster` / `lattice (FFD)` deformer
   These live in `Ctrl_GRP`, follow `cloth_*` naming, survive `.ma` export, and stay realtime-light.
2. **Tool surfacing:** `controls.py` discovers these attributes (by naming/metadata convention) and
   `controls_panel.py` renders them as sliders. The tool **drives existing attrs**; it does not create the network.
3. **Placement:** `placement.py` adds/uses a single top-level offset transform above the garment for
   translate/rotate/scale nudge and optional anchor. This is a transform, not a connection network.

**RESOLVED (2026-06-04):** the fit-control attribute convention is defined in
`Clothing Asset Authoring Spec.md` §8 — a `cloth_fit_ctrl` under `Ctrl_GRP` exposing keyable `fit_*`
float attrs (`fit_tightness` −1..1, `fit_thickness` 0..1, `fit_length` −1..1, plus `fit_<region>_<param>`
variants), neutral at default, driven by deformers authored inside the asset. The tool reads each attr's
min/max for slider ranges and only *sets values* (never builds the network). Status: proposed, pending
Tony sign-off → then fold into the official Addendum. Until an asset exposes `fit_*` attrs, the panel
falls back to surfacing whatever keyable custom attrs exist on `*_ctrl` nodes in `Ctrl_GRP`.

---

## 8. Rig hygiene workstream (rename + cleanup)

Driven by `rig_naming_rename_map.csv` / `rig_naming_rename_simple.csv`. This is **brand/typo hygiene on
the rig wrapper + solver nodes**, not on the clothing contract — the body contract joints are already
correct and **locked**. So this workstream is **not a blocker** for the clothing tool, but it should be
done first to keep names consistent for export and future re-gen.

**Findings (verified against `GenHuman_rig_v02.ma`):**
- `GenMan_` typo prefix → `GenHuman_`: **4592** refs, **679** `createNode` decls. Unique substring → safe global swap.
- `GENHUMAN` (allcaps top group) → `GenHuman`: **4778** refs. Confirmed **no** `GENHUMAN_*` substrings → safe.
- `GHuman_mesh_02` → `GenHuman_body_mesh`; `e_Gman_EYE*` / `e_GMan_EYE*` → `GenHuman_eye_*`; `GM_Body`/`GM_EyeBall` → `*_mat`. Specific named nodes; no stray `GM_` collisions found.
- `GM_foot_L/R` → `foot_align_l/r`: **rename-VERIFY** — may be redundant with `ik_foot_l/r`; confirm purpose before renaming. **Do not auto-apply.**
- Constraint followers (`*_parentConstraint1`, `*_scaleConstraint1`) → derive from renamed parent.
- **DEFER:** ~228 facial-module joints (different internally-consistent convention; clothing never connects there; high risk).
- **KEEP:** body/export Epic skeleton + `ik_*` (the contract).

**Method (safety):** The spec-prescribed approach is a **script run inside Maya** (`cmds.rename()`), so
Maya auto-updates the ~3300 connection references and resolves dual-skeleton short-name ambiguity. A
direct text edit of the `.ma` is *possible* for the unambiguous global swaps (`GenMan_`, `GENHUMAN`)
but cannot safely handle the verify/structural items or DAG disambiguation. **Plan: ship
`tools/rename_genhuman.py` (CSV-driven, in-Maya, dry-run first, backup, verify-items gated behind a
flag).** Best long-term fix is correcting the token in the **rig generator** so re-gen stops
reintroducing `GenMan_`.

---

## 9. Open questions (from spec "Open Items" + new)

From the spec, still undefined:
- Exact transform attributes to `connectAttr` (translate/rotate/scale/jointOrient/visibility?).
- GenHuman version identification method (file name / version node / custom attr / external table).
- Clothing version-compatibility method.
- Import vs reference for clothing assets.
- Whether clothing controls stay artist-accessible after connect (likely **yes**, per §4).
- Required top-level group name; how multiple assets are identified without metadata.
- Required Genie node names.

**Resolved since draft:** ~~Import vs reference~~ → **import**, per-instance namespace (FR-1 / §4).

New (this PRD):
- **Dual-skeleton target:** canonical DAG path for the clothing-target export skeleton (§4).
- ~~Fit-control attribute convention to add to the Addendum (§7).~~ **RESOLVED** → `Clothing Asset Authoring Spec.md` §8 (pending Tony sign-off to fold into Addendum).
- Preset storage location (JSON sidecar vs metadata node).

**Asset-authoring contract delivered (2026-06-04):** `Clothing Asset Authoring Spec.md` is the
self-contained build spec handed to the clothing rigger. It consolidates the Addendum, corrects the
Addendum's wrong naming examples (`cloth_` + exact body name, no `_jnt`), formalizes the §8 fit-control
convention, and clarifies that the no-network rule applies only to the body↔clothing snap (asset-internal
rigging may use any Maya nodes/deformers/SDKs).

---

## 10. Tech stack & constraints
- Maya 2026, Python 3, **PySide6** (`maya.cmds` for rig ops; avoid PyMEL).
- No third-party runtime deps in the shipped tool (studio portability).
- Performance: `connectAttr`-only, multiple assets must not degrade playback (spec).

### Attach mechanism — considered alternatives (why `connectAttr`)
- **`parentConstraint` per joint** — rejected: adds a constraint node per joint (hundreds across multiple
  garments), heavier eval, offset state, clutters export. `connectAttr` is one direct edge per channel.
- **`offsetParentMatrix` (matrix rigging, Maya 2020+)** — the modern lightweight attach: one
  `body.worldMatrix → cloth.offsetParentMatrix` connection per joint, no constraint nodes, no double
  transform. **Deliberately NOT taken:** the spec bans matrix/utility nodes, it typically needs a
  `multMatrix` for offsets, and plain t/r/s `connectAttr` bakes most predictably to FBX/Alembic/USD for
  Genie. Documented here so the choice is intentional, not accidental.
- **Skin garment directly to the body joints (no duplicate skeleton)** — rejected: kills standalone
  authoring/validation and swappability; asset would require the body scene present.

## 11. Milestones (high level — detail in `todo.md`)
1. **M0 Rig hygiene** — rename/cleanup script + applied clean rig.
2. **M1 Library + read** — scan/parse assets, browser UI (read-only).
3. **M2 Validate + Attach + Detach** — connection lifecycle with hard-stop validation.
4. **M3 Fit/placement controls + presets** — control surfacing + offset + save/load.
5. **M4 Multi-asset + Genie export + packaging** — independence, export checks, installer/shelf.
6. **M5 Docs + example asset + test scene** — per spec Deliverables.
