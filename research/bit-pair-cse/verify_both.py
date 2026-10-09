#!/usr/bin/env python3
"""Reproduce and independently check both pair-disjoint module candidates.

No claim about the physical word, finite network or multiplication exponent.
The n=10 network is intended as a rational/complex-side *module candidate*,
whereas n=11 is the bit-side module candidate. Since source DAGs change,
the frozen global carrier/physical certificate cannot be reused.
"""
import hashlib
from itertools import combinations
import json
from pathlib import Path
import random
from search import construct,check

CASES=((10,306,301,"d1ad00bcf005b9a7a150a0902bd1356396590da197aca31105c667e443af0b36"),
       (11,68,397,"95757be86076e4a17138bde1397f398b12f9c79e135bfb966501614845fecc15"))

def independent(d,n):
    labels=list(combinations(range(n),2))
    v=len(labels)
    assert len(d["roots"])==d["input_count"]==v
    sup=[1<<i for i in range(v)]
    assert d["args"][:v]==[None]*v
    for j,pair in enumerate(d["args"][v:],v):
        a,b=pair
        assert 0<=a<j and 0<=b<j and not sup[a]&sup[b]
        sup.append(sup[a]|sup[b])
    for i,port in enumerate(labels):
        want=sum(1<<j for j,(a,b) in enumerate(labels) if a not in port and b not in port)
        assert sup[d["roots"][i]]==want,("wrong root",i)
    todo=list(d["roots"]);visited=set()
    while todo:
        x=todo.pop()
        if x not in visited:
            visited.add(x)
            if d["args"][x] is not None:todo.extend(d["args"][x])
    assert len(visited)==len(d["args"]),("dead nodes",len(d["args"])-len(visited))
    rng=random.Random(72549)
    for _ in range(25):
        x=[rng.randrange(-999,1000) for _ in range(v)]
        y=x[:]
        for a,b in d["args"][v:]:y.append(y[a]+y[b])
        expected=[sum(x[k] for k,(a,b) in enumerate(labels) if a not in port and b not in port)
                  for port in labels]
        assert [y[k] for k in d["roots"]]==expected
    return len(d["args"])-v

def main():
    for n,seed,expected,digest in CASES:
        d=construct(n,seed=seed,temp=.75,bias=10.0)
        assert check(d,n)==expected
        assert independent(d,n)==expected
        # Check SHA256 of compact JSON serialization for reproducible exact DAG witness.
        blob=json.dumps(d,separators=(",",":")).encode()+b"\n"
        assert hashlib.sha256(blob).hexdigest()==digest
        print("PASS: n=%d roots=%d active_additions=%d signed_replays=25 sha256=%s" %
              (n,len(d["roots"]),expected,digest),flush=True)
    print("LOCAL MODULES ONLY: no certified kappa or full physical replay",flush=True)

if __name__=="__main__":main()
