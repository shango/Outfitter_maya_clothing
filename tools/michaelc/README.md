# MichaelC headless tools

Written when Maya was not reachable from this shell. **It now is** - see
`memory/maya-runnable-from-wsl.md`. Maya is ground truth; prefer it.

| file | what it does | trust |
|---|---|---|
| `make_016.py` | the authoritative 01.5 -> 01.6 transform recipe | good - Maya loads the result cleanly (3,526 nodes, no errors) |
| `verify_016.py` | referential-integrity diff between two `.ma` files | good - structural only |
| `dag2.py` | full-DAG-path `.ma` parser (short names are not unique here) | good - structural only |
| `wpos.py` | world joint positions from local transforms | limited - the export joints are `parentConstraint`-driven, so it cannot evaluate their live pose |

`wt.py` (vertex positions + skin weights out of a `.ma`) was **deleted on 2026-09-03**.
It mis-parsed the chunked `.wl` weight blocks: Maya writes them as
`setAttr ".wl[a:b].w"` runs whose declared ranges overlap at the boundary
(`[67:151]` is followed by `[151:237]`), and the parser reset its vertex counter at each
chunk, truncating whichever vertex straddled the split. Per-joint totals survived, because
sums are order-independent - which is why the W2/W3/W4 figures were right - but per-vertex
sums were fiction, and they produced a work-order item (W5, "eight vertices need repainting")
for a mesh where all 5,280 vertices sum to exactly 1.0.

Read weights through `MFnSkinCluster.getWeights` in a real Maya instead.
