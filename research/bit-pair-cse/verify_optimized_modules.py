#!/usr/bin/env python3
"""Independent reproducibility of two optimized pair-disjoint scalar modules.

No multiplication exponent is claimed. Exact support identities and signed
integer tests are the only admission criteria. Source: experimental RePair
search with OpenAI assistance; upstream paired-cube lineage retained.
"""
from itertools import combinations
import json
import random
from pathlib import Path
from search import construct, check

def independent(n,seed,temp,bias,expected):
    module=construct(n,seed,temp,bias)
    assert check(module,n)==expected
    labels=list(combinations(range(n),2))
    args=module['args']
    live=set()
    todo=list(module['roots'])
    while todo:
        x=todo.pop()
        if x in live:continue
        live.add(x)
        if args[x] is not None:todo.extend(args[x])
    assert len(live)==len(args),('dead nodes',len(args)-len(live))
    rng=random.Random(72549)
    for _ in range(25):
        x=[rng.randrange(-999,1000) for _ in labels]
        values=x[:]
        for a,b in args[len(labels):]:values.append(values[a]+values[b])
        wanted=[sum(x[i] for i,(u,v) in enumerate(labels) if u not in pair and v not in pair) for pair in labels]
        assert [values[t] for t in module['roots']]==wanted
    print('PASS',n,'coordinates',len(labels),'roots',expected,'additions; 25 signed integer trials; all DAG nodes live')
    return module

if __name__=='__main__':
    a=independent(10,306,0.75,10.0,301)
    b=independent(11,68,0.75,10.0,397)
    for n,obj in ((10,a),(11,b)):
        name=Path(__file__).with_name('pair_disjoint_n%d.json'%n)
        if name.exists(): assert obj==json.loads(name.read_text())
    print('PASS complete')
