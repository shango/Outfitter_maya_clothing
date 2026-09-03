"""Full-DAG-path parse of a .ma (handles duplicate short names)."""
import re, sys
sys.path.insert(0,"/home/sgold/dev/repos/Outfitter_maya_clothing/scripts")
from outfitter.core import ma_parse

CN=re.compile(r'^createNode\s+(\S+)\s+(.*)$')
NAME=re.compile(r'-n\s+"((?:\\.|[^"\\])*)"')
PARENT=re.compile(r'-p\s+"((?:\\.|[^"\\])*)"')
SHARED=re.compile(r'(?:^|\s)-s(?:\s|$)')
DAG={"transform","joint","mesh","nurbsCurve","bezierCurve","camera","ikEffector",
     "ikHandle","container","locator","clusterHandle","pointConstraint",
     "orientConstraint","scaleConstraint","parentConstraint","aimConstraint",
     "poleVectorConstraint"}

def parse(path):
    text=open(path,encoding="utf-8",errors="replace").read()
    paths=[]            # every DAG full path, creation order
    types={}            # full path -> node type
    for stmt in ma_parse.iter_statements(text):
        if not stmt.startswith("createNode "): continue
        m=CN.match(stmt)
        if not m: continue
        ntype,rest=m.group(1),m.group(2)
        nm=NAME.search(rest)
        if not nm: continue
        name=nm.group(1)
        if ntype not in DAG:
            continue
        pm=PARENT.search(rest)
        if pm:
            praw=pm.group(1)
            if praw.startswith("|"):
                parent=praw
            else:
                cands=[p for p in paths if p.rsplit("|",1)[-1]==praw]
                if len(cands)!=1:
                    # ambiguous or missing: take the most recent match
                    parent=cands[-1] if cands else "|"+praw
                else:
                    parent=cands[0]
            full=f"{parent}|{name}"
        else:
            full=f"|{name}"
        paths.append(full); types[full]=ntype
    kids={}
    for p in paths:
        kids.setdefault(p.rsplit("|",1)[0] or "|", []).append(p)
    return paths, types, kids
