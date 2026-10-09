#!/usr/bin/env python3
"""Deterministic brute-force checks for the independent flow engine."""
import importlib.util,random,sys,types
stub=types.ModuleType("reuse")
stub.basis=lambda b:tuple(b)
stub.contained=lambda a,b:set(a).issubset(b)
stub.nondeg=lambda b:True
stub.check_pairs=lambda data,p:True
stub.select_reuse=lambda data:[]
sys.modules["reuse"]=stub
from pathlib import Path
p=Path(__file__).with_name("maxflow_reuse.py")
spec=importlib.util.spec_from_file_location("flow_candidate",p)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def brute(edges,n,m):
    def run(i,mask):
        if i==n:return 0
        best=run(i+1,mask)
        for j in range(m):
            if edges[i][j] and not(mask>>j&1):
                best=max(best,1+run(i+1,mask|(1<<j)))
        return best
    return run(0,0)

checked=0
for n in range(1,7):
 for m in range(1,7):
  for seed in range(20):
   rng=random.Random(seed*500+n*47+m)
   edges=[[rng.randrange(3)==0 for _ in range(m)]for _ in range(n)]
   src=0;u0=1;v0=u0+n;sink=v0+m
   graph=mod.Flow(sink+1)
   for i in range(n):graph.add(src,u0+i,1)
   for j in range(m):graph.add(v0+j,sink,1)
   for i in range(n):
    for j in range(m):
     if edges[i][j]:graph.add(u0+i,v0+j,1)
   assert graph.solve(src,sink)==brute(edges,n,m)
   checked+=1
print('PASS',checked,'independent brute-force bipartite matching comparisons')
