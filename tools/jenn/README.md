# tools/jenn

Provenance for the Jenn rig's Outfitter onboarding. Already run; kept so the result can be
regenerated from the rigger's drop rather than trusted. See `HANDOFF_Jenn.md` for the findings.

| script | where it runs | what it does |
|---|---|---|
| `profile_rig.py` | plain python3 | Headless structural pre-pass on a `.ma`: export-group candidates ranked the way `maya_rigs.candidate_export_groups()` ranks them, top-level DAG roots, duplicate short names. Reuses `tools/michaelc/dag2.py`, because short names are not unique in these rigs. |
| `rig_audit.py` | `mayapy` | The authoritative audit. Takes a `.ma` and writes JSON: node/unknown counts, a full `capture_profile` + `validate_profile` pass, derived skin sets, per-skinCluster influence histograms read through `MFnSkinCluster.getWeights`, display-layer state, guide-markers-sitting-on-controls distances, and joint world positions for proportion comparison. Works on any rig, not just Jenn. |
| `weights_v16.py` | `mayapy` | Prunes the skinCluster to 4 influences and renormalizes, measures the cost at bind and in an aggressive FK/IK pose, exports the skinCluster and dumps the weight array to `weights_v16.bin`. |
| `make_v16.py` | plain python3 | `Jenn_rig_v1.5.ma` -> `Jenn_rig_v1.6.ma`. The authoritative recipe. |
| `verify_v16.py` | `mayapy` | Reloads v1.6 and checks it against the `.bin` dump. Read-only. |

## The two-pass run

`make_v16.py` takes an optional skinCluster export. Run it three times:

```bash
python3 tools/jenn/make_v16.py                       # structural only, loadable by Maya
mayapy.exe weights_v16.py                            # computes against that file
python3 tools/jenn/make_v16.py <skin_new_v16.ma>     # regenerates from v1.5, splices weights
```

The third run starts from v1.5 again rather than editing the second run's output, so the result
is deterministic from the rigger's drop and the script stays idempotent.

## Things that cost time here

**Removing a plugin means removing its attributes too.** Dropping the 5 Arnold nodes and the
`requires ... "mtoa"` line was not enough: mtoa registers `.ai_*` as **dynamic attributes on
stock node types**, and 18 of those setAttr lines sat on the two shading groups. Maya rejected
the file at load with *"The shadingEngine 'initialShadingGroup' has no '.ai_override'
attribute"*. The plugin declaration and its attributes go together.

**Text surgery must work on whole statements.** A `connectAttr` can wrap onto a `"\t\t -na;"`
line. Removing single lines leaves orphaned tails that Maya rejects. `make_v16.py` asserts that
no statement begins with a flag fragment, which is what an orphan looks like.

**`verify_016.py` is MichaelC-specific.** Run against Jenn it reports FAILs for absent
`MichaelC_*` nodes, an influence count of 79 rather than 89, and the `groupParts3` skin chain.
Its referential-integrity checks (parents resolve, connection endpoints resolve, no residual
references, node-type deltas) are rig-agnostic and are the part worth reading.

**Read weights through the API, never by parsing `.wl`.** The chunked `.wl` blocks have
overlapping declared ranges and that is exactly what produced the withdrawn MichaelC W5. Every
weight number in `HANDOFF_Jenn.md` came from `MFnSkinCluster.getWeights`.
