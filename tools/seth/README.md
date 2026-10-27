# tools/seth

Provenance for the Seth rig's Outfitter onboarding.

| script | where it runs | what it does |
|---|---|---|
| `make_v005.py` | plain python3 | `Seth_rig_v00.4.ma` -> `Seth_rig_v00.5.ma`. Renames the generic landmarks: `Skeleton` -> `Seth_Joint_GRP`, `Geo` -> `Seth_Mesh_GRP`, `Seth_body` -> `Seth_body_mesh` (+ shapes). Text surgery, nothing else changed. |
| `verify_v005.py` | `mayapy` | Loads both files and checks the rename changed nothing but names: weights, rest and posed mesh, joint positions, connection count, no dangling DAG-path string attributes. Then captures and validates the Seth profile, runs the Load / connect / pose / Remove test body cycle, and checks the new markers no longer match a garment scene holding `cloth_Skeleton_vis_grp`. Read-only. |

## Why the rename

v00.4 (DI GenHuman tooling, same layout as Jenn v1.5) keeps its export skeleton in `Skeleton`
and its body in `Geo`. `maya_skeleton._find_export_root` resolves the export group by short
name, first match, and the registered markers would have been `Skeleton` / `Seth`, which
`scene_has_rig` matches as substrings: an empty scene holding `cloth_Skeleton_vis_grp` and
`Sethhat_geo` reported the rig as present. Same rename MichaelC 01.6 and Jenn v1.6 got.

## Verified (2026-10-27, Maya 2026)

Identical to v00.4 except for names: 3,553 nodes in a fresh session, 37,824 connections,
weights max diff 0.0, rest and posed mesh max diff 0.0, posed joints max diff 0.0, no load
errors, no dangling DAG-path string attributes. Profile validates clean on `Seth_Joint_GRP`
(89 joints, GenHuman names and skin sets), markers `Seth_Joint_GRP` / `Seth`, none shared
with GenHuman. Test body connects 89 joints (267 plugs) at 0.000 cm drift rest and posed,
and Remove test body leaves zero nodes.

## Not done in v00.5

Left as the rigger delivered: body skin at `maxInfluences` 8, `maintainMaxInfluences` off,
peak 10 influences (Authoring Spec section 6 says 4); `upperarm_l/r` and `thigh_l/r` carry zero weight;
`head` rest scale 0.99; `center_of_mass` at the origin; `DI_Body_Guide_GRP` visible on no
layer; a stray `left` ortho camera; no `Seth_info_GRP` stamp. `detect_rig_version` reads
`v00` from the namespace `Seth_rig_v00_5`. The `Seth` marker still substring-matches nodes
such as `Sethhat_geo`, as `Eric` and `JENN` do for theirs.
