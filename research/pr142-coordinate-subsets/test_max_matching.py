#!/usr/bin/env python3
"""Brute-force maximum-flow regression on small GF(2) frame families."""
import random
import sys
from itertools import combinations
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/"research/cyclic-deferred"))
from reuse import basis,contained
from max_matching import grouped_maximum
def brute(donors,births):
    n=len(donors);m=len(births)
    def rec(i,mask):
        if i==n:return 0
        best=rec(i+1,mask)
        for j in range(m):
            if not(mask>>j & 1) and contained(donors[i],births[j]):
                best=max(best,1+rec(i+1,mask|(1<<j)))
        return best
    return rec(0,0)
subspaces=sorted({basis(c) for d in range(1,4)
                  for c in combinations(range(1,16),d)},
                 key=lambda f:(len(f),f))
rng=random.Random(20261009)
total=0
for n in range(1,7):
    for m in range(1,7):
        for _ in range(22):
            D=[rng.choice(subspaces) for j in range(n)]
            B=[rng.choice(subspaces) for j in range(m)]
            actual=grouped_maximum(dict(enumerate(D)),dict(enumerate(B)))
            assert len(actual)==brute(D,B)
            total+=1
D=[(4,2,1),(14,1),(12,),(9,),(10,),(13,)]
B=[(8,3),(4,),(8,1),(12,2),(10,7),(9,5,3)]
assert len(grouped_maximum(dict(enumerate(D)),dict(enumerate(B))))==4
print("PASS",total,"independent brute-force matching trials plus nontrivial greedy-gap regression")
