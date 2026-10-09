#!/usr/bin/env python3
"""Exact local certificates for PR168 complex/bit pair-disjoint modules.
No physical or asymptotic exponent claim. OpenAI-assisted experiment.
Original decoder/module constructions belong to icekylinx/eumemic.
"""
import json, random
from itertools import combinations
from pathlib import Path
from search import construct,check

ROOT=Path(__file__).resolve().parents[2]
def validate(m,n,seeds=25):
    pairs=list(combinations(range(n),2))
    v=len(pairs)
    assert check(m,n)==len(m['args'])-v
    alive=set();todo=list(m['roots'])
    while todo:
        i=todo.pop()
        if i in alive:continue
        alive.add(i)
        if m['args'][i] is not None:todo.extend(m['args'][i])
    assert len(alive)==len(m['args']),'dead operations'
    rng=random.Random(20261009)
    for _ in range(seeds):
        sources=[rng.randint(-997,997) for _ in range(v)]
        registers=sources[:]
        for a,b in m['args'][v:]:registers.append(registers[a]+registers[b])
        expected=[sum(sources[j] for j,(a,b) in enumerate(pairs) if a not in t and b not in t) for t in pairs]
        assert [registers[r] for r in m['roots']]==expected,'wrong signed integer decoder'
    return len(m['args'])-v

def run():
    # Use explicit provenance parameters: same deterministic compiler, two dimensions.
    for n,seed,baseline in ((10,306,356),(11,68,442)):
        m=construct(n,seed=seed,temp=.75,bias=10.0)
        count=validate(m,n)
        assert count<baseline,(n,count,baseline)
        print(f'PASS pair-disjoint n={n}: {baseline} -> {count} additions; 25 signed-integer replays; no dead nodes',flush=True)
        path=Path(__file__).parent/f'pair_n{n}_candidate.json'
        path.write_text(json.dumps(m,separators=(',',':'))+'\n')
    print('IMPORTANT: full Graph, matching, physical frames and paid assembly NOT proved',flush=True)

if __name__=='__main__':run()
