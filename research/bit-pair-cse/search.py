#!/usr/bin/env python3
"""Search valid disjoint-pair query modules. Research only: NO exponent claim.
Candidate compilation / G-geometry / physical replay are not checked here.
Prepared with OpenAI GPT-6 assistance. Apache-2.0; upstream sources credited.
"""
from itertools import combinations
from collections import Counter
from heapq import heappush, heappop
from pathlib import Path
import random, json, argparse

def construct(n=11, seed=68, temp=0.5, bias=-1.0):
    rng=random.Random(seed)
    labels=list(combinations(range(n),2))
    v=len(labels)
    rows=[set(i for i,(u,w) in enumerate(labels) if u not in ab and w not in ab) for ab in labels]
    args=[None]*v
    support=[1<<i for i in range(v)]
    counts=Counter()
    for row in rows:counts.update(combinations(sorted(row),2))
    heap=[]
    def score(p,count):
        a,b=p
        size=support[a].bit_count()+support[b].bit_count()
        return (-count+temp*rng.random()+bias*size*0.001,rng.random())
    for p,count in counts.items():
        if count>1:heappush(heap,(*score(p,count),p,count))
    while heap:
        _,_,p,old=heappop(heap)
        count=counts.get(p,0)
        if count!=old or count<=1:continue
        a,b=p
        impacted=[row for row in rows if a in row and b in row]
        assert len(impacted)==count and not support[a]&support[b]
        x=len(args);args.append([a,b]);support.append(support[a]|support[b])
        delta=Counter()
        for row in impacted:
            row.remove(a);row.remove(b)
            for y in row:
                delta[tuple(sorted((a,y)))]-=1
                delta[tuple(sorted((b,y)))]-=1
                delta[tuple(sorted((x,y)))]+=1
            row.add(x);delta[p]-=1
        for edge,change in delta.items():
            new=counts.get(edge,0)+change
            if new<=0:counts.pop(edge,None)
            else:
                counts[edge]=new
                if new>1:heappush(heap,(*score(edge,new),edge,new))
    roots=[]
    for row in rows:
        row=sorted(row)
        while len(row)>1:
            a,b=row.pop(0),row.pop(0)
            assert not support[a]&support[b]
            x=len(args);args.append([a,b]);support.append(support[a]|support[b]);row.insert(0,x)
        roots.append(row[0])
    obj=dict(input_count=v,args=args,roots=roots)
    check(obj,n)
    return obj

def check(obj,n):
    labels=list(combinations(range(n),2))
    v=len(labels)
    assert obj['input_count']==v and len(obj['roots'])==v
    sup=[1<<i for i in range(v)]
    assert obj['args'][:v]==[None]*v
    for i,pair in enumerate(obj['args'][v:],v):
        a,b=pair
        assert 0<=a<i and 0<=b<i and not sup[a]&sup[b]
        sup.append(sup[a]|sup[b])
    expected=[sum(1<<j for j,(u,w) in enumerate(labels) if u not in ab and w not in ab) for ab in labels]
    assert [sup[x] for x in obj['roots']]==expected
    # Binary masks also establish exact coefficient-1 output identity over Z
    return len(obj['args'])-v

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--trials',type=int,default=180)
    p.add_argument('--n',type=int,default=11)
    p.add_argument('--limit',type=int,default=442)
    a=p.parse_args()
    best=None
    for seed in range(a.trials):
        obj=construct(a.n,seed)
        if best is None or len(obj['args'])<len(best['args']):
            best=obj
            print('improved seed',seed,'additions',check(best,a.n),flush=True)
    assert check(best,a.n)<a.limit,'No local improvement'
    print('PASS pair-disjoint support, all roots, local additions',check(best,a.n),'baseline',a.limit)
    if a.n==11:
        out=Path('research/paired-cube-bit/data/pair_module_p12_research.json')
        out.write_text(json.dumps(best,separators=(',',':'))+'\n')
        print('Unpinned research artifact:',out)
