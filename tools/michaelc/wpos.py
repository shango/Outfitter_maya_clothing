"""World joint positions from local t/r/jo/ro, Maya row-vector convention."""
import math

def _m(): return [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
def mul(A,B):
    return [[sum(A[i][k]*B[k][j] for k in range(4)) for j in range(4)] for i in range(4)]
def rot(axis,deg):
    a=math.radians(deg); c,s=math.cos(a),math.sin(a); M=_m()
    if axis==0: M[1][1]=c;M[1][2]=s;M[2][1]=-s;M[2][2]=c
    elif axis==1: M[0][0]=c;M[0][2]=-s;M[2][0]=s;M[2][2]=c
    else: M[0][0]=c;M[0][1]=s;M[1][0]=-s;M[1][1]=c
    return M
_ORDER={0:(0,1,2),1:(1,2,0),2:(2,0,1),3:(0,2,1),4:(1,0,2),5:(2,1,0)}
def euler(r,ro=0):
    o=_ORDER.get(ro,(0,1,2)); M=_m()
    for ax in o: M=mul(M,rot(ax,r[ax]))
    return M
def trans(t):
    M=_m(); M[3][0],M[3][1],M[3][2]=t; return M
def local(t,r,jo,ro=0):
    return mul(mul(euler(r,ro),euler(jo,0)),trans(t))
def world_positions(joints, root_group_rot=(0,0,0)):
    """joints: ordered list of dicts(name,parent,t,r,jo,ro). Returns {name: (x,y,z)}."""
    W={"__root__": euler(root_group_rot,0)}
    pos={}
    for j in joints:
        pw=W.get(j["parent"], W["__root__"])
        w=mul(local(j["t"],j["r"],j["jo"],j.get("ro",0)), pw)
        W[j["name"]]=w
        pos[j["name"]]=(w[3][0],w[3][1],w[3][2])
    return pos
