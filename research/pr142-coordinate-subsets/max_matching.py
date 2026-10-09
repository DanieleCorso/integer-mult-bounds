#!/usr/bin/env python3
"""Maximum-cardinality compensated birth-cut donor matching for PR142.

Exact admissibility constraints, but NO claim that additional matches are
physically replayable. The selected pairs must pass PR142's full compiler,
arbitrary-dirty replay, reflected audit and new coupled certificate.
"""
from collections import defaultdict, deque
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research/cyclic-deferred"))
from reuse import basis,contained,nondeg,check_pairs,select_reuse as incumbent_greedy

class Flow:
    def __init__(self,n):
        self.G=[[] for _ in range(n)]
    def add(self,u,v,cap):
        assert type(cap)==int and cap>=0 and u!=v
        idx=len(self.G[u])
        self.G[u].append([v,cap,len(self.G[v])])
        self.G[v].append([u,0,idx])
        return idx
    def maxflow(self,s,t):
        sys.setrecursionlimit(max(sys.getrecursionlimit(),4*len(self.G)+100))
        flow=0
        while True:
            level=[-1]*len(self.G);level[s]=0; q=deque([s])
            while q:
                u=q.popleft()
                for v,cap,_ in self.G[u]:
                    if cap and level[v]<0:
                        level[v]=level[u]+1;q.append(v)
            if level[t]<0:return flow
            nxt=[0]*len(self.G)
            def aug(u,limit):
                if u==t:return limit
                while nxt[u]<len(self.G[u]):
                    e=self.G[u][nxt[u]];v,cap,rev=e
                    if cap and level[v]==level[u]+1:
                        n=aug(v,min(limit,cap))
                        if n:
                            e[1]-=n;self.G[v][rev][1]+=n
                            return n
                    nxt[u]+=1
                return 0
            while True:
                n=aug(s,10**18)
                if not n:break
                flow+=n

def grouped_maximum(donors_raw,births_raw):
    donors=defaultdict(list);births=defaultdict(list)
    for s,F in donors_raw.items():donors[basis(F)].append(s)
    for s,F in births_raw.items():births[basis(F)].append(s)
    for rows in [*donors.values(),*births.values()]:rows.sort()
    D=sorted(donors,key=lambda f:(-len(f),f))
    B=sorted(births,key=lambda f:(len(f),f))
    src,d0,b0=0,1,1+len(D);sink=b0+len(B)
    graph=Flow(sink+1)
    for i,F in enumerate(D):graph.add(src,d0+i,len(donors[F]))
    for j,F in enumerate(B):graph.add(b0+j,sink,len(births[F]))
    edges=[]
    for i,A in enumerate(D):
        for j,F in enumerate(B):
            if len(A)<=len(F) and contained(A,F):
                idx=graph.add(d0+i,b0+j,min(len(donors[A]),len(births[F])))
                edges.append((i,j,idx))
    optimum=graph.maxflow(src,sink)
    pairs=[]
    for i,j,k in edges:
        e=graph.G[d0+i][k]
        used=graph.G[b0+j][e[2]][1]
        for _ in range(used):
            pairs.append((donors[D[i]].pop(),births[B[j]].pop()))
    assert len(pairs)==optimum
    assert len({x for x,y in pairs})==len(pairs)
    assert len({y for x,y in pairs})==len(pairs)
    assert all(contained(basis(donors_raw[a]),basis(births_raw[b]))
               for a,b in pairs)
    return sorted(pairs)

def select_maximum(data):
    anc=set(data["Anc"])
    first={}
    late=set()
    for i,o in enumerate(data["ops"]):
        ss=o[1:2] if o[0]=="src" else o[1:3]
        for s in ss:
            first.setdefault(s,i)
            if i not in anc:late.add(s)
    donors={}
    for a,i in data["last"].items():
        if (i not in anc or a in data["role_root"] or
            a in data["placed"] or a in late):continue
        A=basis(data["op_frames"][i])
        assert nondeg(A),"Degenerate dead donor"
        donors[a]=A
    births={}
    for b,raw in data["placed"].items():
        i=first.get(b)
        if (b in data["leaf_of"] or b in data["touched"]
            or i is None or i in anc):continue
        o=data["ops"][i]
        if o[0]!="copy" or o[2]!=b:continue
        F=basis(raw)
        if contained(F,basis(data["op_frames"][i])):
            births[b]=F
    matched=grouped_maximum(donors,births)
    pairs=[dict(donor=a,recipient=b,donor_frame=donors[a],
                birth_frame=births[b],e=len(donors[a]),s=len(births[b]))
           for a,b in matched]
    check_pairs(data,pairs)
    incumbent=incumbent_greedy(data)
    assert len(pairs)>=len(incumbent),"Matching lost a greedy-eligible pair"
    print("PR142 exact donor matching",dict(greedy=len(incumbent),
          maximum=len(pairs),additional=len(pairs)-len(incumbent),
          donors=len(donors),births=len(births)),flush=True)
    return pairs
