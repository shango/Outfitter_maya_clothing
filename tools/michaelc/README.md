# MichaelC headless tools

Written when Maya was not reachable from this shell. **It now is** - see
`memory/maya-runnable-from-wsl.md`. Maya is ground truth; prefer it.

| file | what it does | trust |
|---|---|---|
| `make_016.py` | the authoritative 01.5 -> 01.6 transform recipe | good - Maya loads the result cleanly (3,526 nodes, no errors) |
| `weights_017.py` | runs in `mayapy`: computes W2/W3/W4/W6 and exports the new skinCluster | good - result verified back through Maya bit-exactly |
| `make_017.py` | splices that skinCluster into 01.6, plus R3 and R4, to write 01.7 | good - text surgery, `verify_017.py` confirms the result |
| `verify_017.py` | runs in `mayapy`: reloads 01.7 and checks it against `weights.bin` | good |
| `make_018.py` | 01.7 -> 01.8: hides `MichaelC_BODY_GUIDE_LYR` and the eight bendy splines, bumps the version stamp | good - ten changed lines, `verify_016.py` shows no node or connection delta |
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

## The 01.6 -> 01.7 pipeline

Three steps, in order. Keep the script **outside** the repo when `mayapy` runs it, and never
name it after a stdlib module: `mayapy` puts the script's directory on `sys.path`, so a file
called `inspect.py` shadows the stdlib `inspect` and crashes `maya.standalone.initialize()`
with a bare stack trace that names none of this.

```bash
cp tools/michaelc/weights_017.py /mnt/c/Windows/Temp/mc/
cd /mnt/c/Windows/Temp/mc
"/mnt/c/Program Files/Autodesk/Maya2026/bin/mayapy.exe" weights_017.py   # -> skin_new.ma, weights.bin
python3 tools/michaelc/make_017.py                                       # -> MichaelC_rig_01.7.ma
"/mnt/c/Program Files/Autodesk/Maya2026/bin/mayapy.exe" verify_017.py    # reload and check
python3 tools/michaelc/verify_016.py MichaelC_rig_01.6.ma MichaelC_rig_01.7.ma
```

## 01.7 -> 01.8

One change, no Maya needed:

```bash
python3 tools/michaelc/make_018.py                                       # -> MichaelC_rig_01.8.ma
python3 tools/michaelc/verify_016.py MichaelC_rig_01.7.ma MichaelC_rig_01.8.ma
```

Two sets of curves took viewport clicks off the animation controls. The body-guide layer
shipped visible, and all 31 of its `JOINT_MARKER` curves sit at distance 0.000 from a control.
The eight Hive bendy splines run down the limbs on no display layer at all. `make_018.py` hides
both. Nothing is deleted - turning the layer back on restores the guide, and the bendy splines
still feed their `curveInfo` and `motionPath` readers, which was verified by posing 01.7 and
01.8 identically: same 8 joints moved, same 4.000000 cm, worst difference 0.000e+00 cm.

**Why text surgery rather than saving the scene.** Batch Maya cannot register
`UsdDefaultSettings` or `nodeGraphEditorInfo`; no plugin on this machine provides them
(`mayaUsdPlugin`, `mtoa`, `LookdevXMaya`, `MASH`, `Type`, `bifrostGraph` and `mayaHIK` were
all tried). They load as `unknown`, and a `cmds.file(save=True)` writes them back **twice** -
a round trip through save/reload gives 3,528 nodes instead of 3,526, with "UUID already in
use" on the second read. Exporting only `skinCluster2` avoids them entirely, and splicing
that node's `.wl` block leaves every other byte of the file untouched.
