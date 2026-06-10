# Snap-On Clothing — User Guide

**For:** the Maya artist using the tool to dress the GenHuman rig
**Host:** Maya 2026 · Python 3 · PySide6
**Companion docs:** `Clothing Asset Authoring Spec.md` (for people *building* clothing),
`prd.md` (product requirements). This guide covers *using* the tool.

---

## 1. What the tool does

It snaps pre-rigged clothing assets onto the GenHuman rig. Attaching a garment does
exactly one thing to bind it to the body: it runs `connectAttr` from each GenHuman
body joint to the garment's matching `cloth_*` joint (translate / rotate / scale). No
constraints, utility nodes, matrix nodes, expressions, or driven keys are ever created
on the body↔clothing link, and **the rig itself is never modified** — so the dressed
scene exports to Genie (`.ma` / USD / FBX / Alembic) exactly as the bare rig would.

You can attach several garments at once, fit each independently, and detach any of them
cleanly — detach breaks only the connections the tool made and removes that garment's
namespace, leaving everything else untouched.

---

## 2. Install

1. Unzip the distribution somewhere (keep its layout intact).
2. In Maya 2026, **drag `install.py` from a file browser into the Maya viewport.**
3. The installer copies the `snap_on_clothing` package into your Maya scripts folder,
   merges the bundled starter library into `~/maya/snap_on_clothing/assets/` (without
   overwriting anything you already have), and adds a **Clothing** button on a
   **SnapOnClothing** shelf tab. A confirmation dialog reports what it did.
4. Click the **Clothing** shelf button to open the browser.

Re-dropping `install.py` later **upgrades** the tool: the package is replaced, but your
assets and your library paths (`path.txt`, see §3) are preserved.

You can also launch it from the Script Editor (Python):

```python
import snap_on_clothing.launch as scl
scl.run()
```

---

## 3. Point the tool at your library (Setup tab)

The window has two tabs: **Library** and **Setup**.

On **Setup** you set two folders:

- **Local (working)** — where your clothing assets live on your machine (a local folder
  or fast external drive). **This is the only folder the tool scans** — you browse and
  attach from here.
- **Remote (master)** — a shared master library on a studio server or network drive
  (UNC path / network mount). It is **never scanned**; it is the source the Sync button
  pulls from.

Use **Browse…** on each row to pick the folder, or **Clear** to unset it. Both are saved
to a plain-text file, `path.txt`, beside the installed package:

```
# Snap-On Clothing — asset library locations (managed by the Setup tab).
local  = D:/clothing_library
remote = //studio-nas/projects/genhuman/clothing
```

- It persists across sessions and **survives tool upgrades**.
- You can hand-edit it instead of using the Setup tab if you prefer.
- When **local** is unset, the tool falls back to its built-in defaults (your installed
  per-user library plus the bundled starter assets). A path shown “(missing)” isn’t
  reachable right now (e.g. the drive/server isn’t mounted).

### Sync from the master library

Press **Sync from remote ↓** to pull the latest assets from the remote master into your
local working folder. Sync is **one-way and additive**:

- New assets on the remote are copied down; assets that changed on the remote (different
  size or newer) overwrite your local copy.
- Assets you authored locally are **always kept** — Sync never deletes anything.
- A file the *you* edited locally more recently than the remote is left alone (your edit
  wins over an older remote copy of the same size).

After a sync you get a one-line summary (e.g. *“Sync complete — 3 added, 1 updated, 12 up
to date.”*) and the Library grid refreshes automatically. The button is disabled until
both a local and a remote folder are set. A large first sync over a slow network can take
a while — Maya will show a wait cursor until it finishes.

---

## 4. Dress the rig (Library tab)

1. Open the GenHuman rig scene (or have it in your current scene).
2. On **Library**, browse the thumbnails. Filter by type (shoes / pants / shirt / dress /
   coat / hat) and search by name. Selecting an asset shows its details (name, type,
   version, GenHuman compatibility, author, source, path, and any issues).
3. **Attach** the selected asset. Give the instance a name if asked — it becomes the
   garment's namespace (e.g. `coat:`), which keeps multiple garments isolated.
4. The tool validates first (see §6). If anything is an **error**, attach is refused and
   **the scene is left exactly as it was**. Warnings don't block.
5. Repeat for more garments — e.g. a shirt, pants, and shoes together.
6. **Detach** removes a garment and its connections cleanly; the rest stay attached.

---

## 5. Fit & placement

After attaching, the fit panel surfaces the garment's authored fit controls as sliders.
The tool reads each `fit_*` attribute's min / max / default from the asset and only
**writes values** — the deformers that respond were built into the asset by its author.

- **Fit sliders** (`fit_tightness`, `fit_thickness`, `fit_length`, and any per-region
  variants like `fit_hem_length`): drag to adjust; **Reset** returns to the authored
  neutral default.
- **Placement**: nudge the whole garment's translate / rotate / scale offset to seat it.
- **Presets**: save a fit + placement combination to a JSON sidecar and re-apply it
  later — presets are stored relative to the garment so they reproduce on a re-attached
  instance.

---

## 6. Validation error reference

Validation runs in two stages. Any **ERROR** is a hard stop and leaves the scene
unchanged; **WARNING**/**INFO** are advisory. Each message names the offending node and
a fix hint.

### Stage A — the asset file (runs before anything touches the scene)

| Code | Meaning | Fix |
|---|---|---|
| `no_metadata` | No readable `cloth_info` or sidecar `.json`. | Add a `cloth_info` node with `assetName` / `assetType` / `clothVersion` / `genHumanCompat`. |
| `no_info_node` | The `cloth_info` node is missing. | Add a `cloth_info` network node. |
| `missing_group` | A required group (`Mesh_GRP` / `Rig_GRP` / `Ctrl_GRP`) is absent. | Create the missing group under the asset top group. |
| `no_root_joint` | No `cloth_root` joint. | Duplicate body `root`, rename to `cloth_root`, parent under `Rig_GRP`. |
| `no_cloth_joints` | No `cloth_` connection joints found. | Duplicate the needed body joints and prefix each with `cloth_`. |
| `bad_joint_suffix` | A connection joint has a `_jnt` suffix. | Name = `cloth_` + EXACT body joint name, no `_jnt`. |
| `has_references` | The asset contains references. | Import/remove all references before delivery. |
| `has_namespaces` | The asset contains namespaces. | Remove all namespaces; the tool applies one at import. |
| `forbidden_node_type` | A `blendShape` / `nCloth` / `nucleus` node is present. | Remove it — blendshapes and simulation aren't supported. |
| `duplicate_name` | A node name is declared more than once. | Make all node names unique within the asset. |

### Stage B — the scene, just before import

| Code | Sev. | Meaning | Fix |
|---|---|---|---|
| `no_rig` | error | GenHuman rig not found in the scene. | Load the GenHuman rig first. |
| `version_unknown` | warn | Couldn't detect the scene's GenHuman version. | Set a `genHumanVersion` attr on a rig marker node (compat check is skipped). |
| `version_incompat` | error | Asset doesn't list the scene's GenHuman version in `genHumanCompat`. | Use an asset compatible with this rig version. |
| `ns_in_use` / `ns_exists` | error | The instance name/namespace is already taken. | Choose a different instance name. |
| `genie_missing` | error | A Genie-required node name is absent. | Ensure the export-required node exists (list is TBD — see §7). |

### Stage C — connecting joints (during attach; failure rolls back automatically)

| Code | Meaning |
|---|---|
| `no_joint_match` | No `cloth_*` joint matched a body joint under the export skeleton (check exact names). |
| `cloth_joint_missing` | A matched joint wasn't found after import. |
| `attr_missing` / `attr_locked` / `attr_connected` | A target `translate`/`rotate`/`scale` channel is missing, locked, or already driven — unlock/free it first. |
| `no_body_joints` / `ambiguous_body_joint` | The export-skeleton group resolved to no joints, or a joint name is ambiguous within it. |
| `import_failed` / `attach_failed` | Maya couldn't import the asset / a connection failed; the scene was rolled back. |

> If attach fails for any reason, the tool rolls back to a byte-unchanged scene — you
> never end up with a half-attached garment.

---

## 7. Genie export

Attach is `connectAttr`-only and never adds nodes to or modifies the GenHuman rig, so you
**export the dressed scene normally** (`.ma` / USD / FBX / Alembic) — required GenHuman
node names are preserved and the export skeleton is intact. The tool includes an
export-readiness audit that confirms, before you export, that every connection it made is
a transform-channel `connectAttr` driving the garment (never the rig) and that the
export skeleton still resolves.

> **Pending from the pipeline team:** the exact list of Genie-required node names
> (`GENIE_REQUIRED_NODES`) and the canonical GenHuman version string. Until the export
> team supplies the node list, that check is a no-op (it never blocks you).

---

## 8. Supported GenHuman versions

Author and attach against **`v03`** for now (`genHumanCompat="v03"` in the asset). The
canonical version string and the version-detection method are being finalized; when a
scene's version can't be detected, the compatibility check is skipped with a warning
rather than blocking attach.

---

## 9. Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| Asset shows as **invalid** in the browser | Open its detail panel — the issues list names the validation codes (§6). Usually missing `cloth_info` fields or a structural group. |
| Attach says **no GenHuman rig** | Load the rig scene before attaching. |
| Attach says **no_joint_match** | A `cloth_*` joint name doesn't exactly match a body joint name (case, trailing `_l`/`_r`, no `_jnt`). |
| Garment doesn't follow the body | The matching joints didn't connect — re-check names; confirm the asset was attached (not just imported). |
| Library is empty | On **Setup**, set your **Local (working)** folder to where your `.ma` assets live (§3), or **Sync from remote** to pull them down. |
| A folder shows **(missing)** | The drive / server isn't mounted; reconnect it, or set a reachable folder. |
| **Sync** button is greyed out | Set both a **Local** and a **Remote** folder on Setup (§3). |
| Sync reports failures | The remote path isn't reachable (server/drive offline) or some files are locked/permission-denied; the summary names the count, and any files it could copy still came down. |
| Fit sliders are empty | The asset exposes no `fit_*` attrs on a `*_ctrl` node — fit must be authored into the asset (see the Authoring Spec §8). |
