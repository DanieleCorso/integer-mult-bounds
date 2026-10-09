#!/usr/bin/env python3
"""Experimental exact max-flow matcher for PR131's frame/role eligibility.

This replaces ONLY the greedy pairing objective, not proof obligations.
Output is NOT a verified kappa. Requires full physical compiler/replay.
"""
from collections import defaultdict, deque
from reuse import basis, contained, nondeg, check_pairs, select_reuse

class Flow:
    def __init__(self,n):self.g=[[] for _ in range(n)]
    def add(self,u,v,cap):
        i=len(self.g[u]);j=len(self.g[v])
        self.g[u].append([v,cap,j]);self.g[v].append([u,0,i]);return i
    def solve(self,s,t):
        import sys
        sys.setrecursionlimit(max(sys.getrecursionlimit(),2*len(self.g)+100))
        total=0
        while True:
            depth=[-1]*len(self.g);depth[s]=0;q=deque([s])
            while q:
                u=q.popleft()
                for v,c,_ in self.g[u]:
                    if c and depth[v]<0:depth[v]=depth[u]+1;q.append(v)
            if depth[t]<0:return total
            at=[0]*len(self.g)
            def dfs(u,lim):
                if u==t:return lim
                while at[u]<len(self.g[u]):
                    e=self.g[u][at[u]];v,c,rev=e
                    if c and depth[v]==depth[u]+1:
                        k=dfs(v,min(lim,c))
                        if k:
                            e[1]-=k;self.g[v][rev][1]+=k;return k
                    at[u]+=1
                return 0
            while True:
                k=dfs(s,10**18)
                if not k:break
                total+=k

def maximum_pairs(data):
    early=set(data['Anc']);first={};late=set()
    for i,op in enumerate(data['ops']):
        if op[0]=='src':first.setdefault(op[1],i);continue
        for s in op[1:3]:first.setdefault(s,i)
        if i not in early:late.update(op[1:3])
    donors=defaultdict(list)
    for a,i in sorted(data['last'].items()):
        if i not in early or a in data['role_root'] or a in data['placed'] or a in late:continue
        A=basis(data['op_frames'][i])
        if nondeg(A):donors[A].append(a)
    births=defaultdict(list)
    for b,F in sorted(data['placed'].items()):
        i=first.get(b)
        if b in data['leaf_of'] or b in data['touched'] or i is None or i in early:continue
        op=data['ops'][i]
        if op[0]!='copy' or op[2]!=b:continue
        X=basis(F);B=basis(data['op_frames'][i])
        if nondeg(X) and nondeg(B) and contained(X,B):births[X].append(b)
    A=sorted(donors,key=lambda x:(-len(x),x))
    B=sorted(births,key=lambda x:(len(x),x))
    start=0;lo=1;ro=lo+len(A);end=ro+len(B)
    net=Flow(end+1)
    for j,x in enumerate(A):net.add(start,lo+j,len(donors[x]))
    for j,x in enumerate(B):net.add(ro+j,end,len(births[x]))
    arcs=[]
    for j,x in enumerate(A):
        for k,y in enumerate(B):
            if len(x)<=len(y) and contained(x,y):
                edge=net.add(lo+j,ro+k,min(len(donors[x]),len(births[y])))
                arcs.append((j,k,edge))
    total=net.solve(start,end);out=[]
    for j,k,eidx in arcs:
        e=net.g[lo+j][eidx]
        amount=net.g[e[0]][e[2]][1]
        for _ in range(amount):
            donor=donors[A[j]].pop();recipient=births[B[k]].pop()
            out.append(dict(donor=donor,recipient=recipient,
                            donor_frame=A[j],birth_frame=B[k],e=len(A[j]),s=len(B[k])))
    assert len(out)==total
    check_pairs(data,out)
    return out

def compare(data):
    old=select_reuse(data)
    new=maximum_pairs(data)
    assert len(new)>=len(old)
    return dict(greedy=len(old),maximum=len(new),additional=len(new)-len(old),
                status='candidate only: physical replay and exact κ certificate REQUIRED')
