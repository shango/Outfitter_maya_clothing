"""Load body vertex positions + skin weights out of the MichaelC .ma."""
import re

def load(path="MichaelC_rig_01.6.ma", shape="MichaelC_body_meshShapeOrig",
         skin="skinCluster2"):
    lines = open(path, encoding="utf-8", errors="surrogateescape").read().split("\n")

    def block(pred):
        s = next(i for i, L in enumerate(lines) if pred(L))
        e = next(i for i in range(s + 1, len(lines)) if lines[i].startswith("createNode"))
        return s, e

    # --- vertices ---
    s, e = block(lambda L: L.startswith(f'createNode mesh -n "{shape}"'))
    verts = []
    grab = False
    for L in lines[s:e]:
        t = L.strip()
        m = re.match(r'^setAttr(?: -s \d+)? "\.vt\[\d+(?::\d+)?\]"(?: -type "float3")?(.*)$', t)
        if m:
            grab = True
            buf = m.group(1).rstrip(";").split()
        elif grab and (t.startswith("setAttr") or t.startswith("connectAttr")):
            grab = False
            buf = []
        elif grab:
            buf = t.rstrip(";").split()
        else:
            continue
        for i in range(0, len(buf) - 2, 3):
            verts.append(tuple(float(x) for x in buf[i:i + 3]))

    # --- influences (physical index -> joint short name) ---
    inf = {}
    for L in lines:
        m = re.match(r'connectAttr "([^"]+)\.wm" "%s\.ma\[(\d+)\]"' % skin, L.strip())
        if m:
            inf[int(m.group(2))] = m.group(1).rsplit("|", 1)[-1]

    # --- weights ---
    s, e = block(lambda L: L.startswith(f'createNode skinCluster -n "{skin}"'))
    hdr = re.compile(r'^setAttr(?: -s \d+)? "\.wl\[(\d+)(?::(\d+))?\]\.w"\s*$')
    W, lo, buf = {}, None, []

    def flush(lo, toks):
        k = off = 0
        while k < len(toks):
            n = int(float(toks[k])); k += 1
            p = []
            for _ in range(n):
                p.append((int(float(toks[k])), float(toks[k + 1]))); k += 2
            W[lo + off] = p; off += 1

    for L in lines[s:e]:
        t = L.strip()
        m = hdr.match(t)
        if m:
            if lo is not None: flush(lo, buf)
            lo, buf = int(m.group(1)), []
            continue
        if lo is not None:
            if t.startswith("setAttr") or t.startswith("connectAttr"):
                flush(lo, buf); lo, buf = None, []
                continue
            buf.extend(t.rstrip(";").split())
    if lo is not None: flush(lo, buf)
    return verts, inf, W
