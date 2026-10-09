#!/usr/bin/env python3
"""Exhaustive nested h21/h20 structural restrictions of the pinned PR142 h22 DAG.

No new physical word or kappa is claimed. All retained roots and leaf
supports must be checked; all 253 candidates are scored by live additions.
"""
import argparse, gzip, hashlib, itertools, json, sys
from pathlib import Path
from collections import Counter

if sys.flags.optimize:
    raise RuntimeError("Assertions are mandatory")

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SRC=ROOT/"research/cyclic-deferred/inputs/restricted-dag.json.gz"
SHA="2647e6a0e5beafd651feddcab1a210da87d131fe578ccb792aee00b2cd056adb"

def pack(rec):
    return json.dumps(rec,separators=(",",":")).encode()

def build(record,omitted,verify=True):
    n=record["h"]
    oldv=record["v"]
    omit=set(omitted)
    kept=tuple(i for i in range(n) if i not in omit)
    m=len(kept)
    assert m in (20,21)
    old_triples=list(itertools.combinations(range(n),3))
    new_triples=list(itertools.combinations(kept,3))
    newv=len(new_triples)
    assert len(old_triples)==oldv
    old_stars=[(a,b,i) for a,b in itertools.combinations(range(n),2)
               for i in range(n) if i not in(a,b)]
    kept_stars=[(a,b,i) for a,b in itertools.combinations(kept,2)
                for i in kept if i not in(a,b)]
    assert len(record["P"])==len(old_stars)
    leaves={t:i+1 for i,t in enumerate(new_triples)}
    alias={0:0}
    support=[0]+[1<<i for i in range(newv)]
    args=[(0,0)]*(newv+1)
    by_support={s:i for i,s in enumerate(support)}
    for i,t in enumerate(old_triples,1):
        alias[i]=leaves.get(t,0)
    vanish=collapse=dedup=0
    for j in range(0,len(record["args"]),2):
        a,b=(alias[x] for x in record["args"][j:j+2])
        old=oldv+1+j//2
        if not a or not b:
            alias[old]=a or b
            vanish+=not(a or b)
            collapse+=bool(a or b)
            continue
        assert not support[a]&support[b],"Overlapping source supports"
        s=support[a]|support[b]
        if s in by_support:
            alias[old]=by_support[s]
            dedup+=1
        else:
            k=len(support)
            support.append(s)
            by_support[s]=k
            args.append((a,b))
            alias[old]=k

    oldtid={t:i for i,t in enumerate(old_triples)}
    D=[alias[record["D"][oldtid[t]]] for t in new_triples]
    P=[alias[oldid]for star,oldid in zip(old_stars,record["P"])
       if set(star).isdisjoint(omit)]
    A=[alias[record["A"][i]]for i in kept]
    assert len(D)==newv and len(P)==3*newv and len(A)==m
    assert len(P)==len(kept_stars)
    if verify:
        point=[sum(1<<j for j,t in enumerate(new_triples)if i in t)
               for i in kept]
        full=(1<<newv)-1
        renumber={i:j for j,i in enumerate(kept)}
        for t,k in zip(new_triples,D):
            assert support[k]==full&~(point[t[0]]|point[t[1]]|point[t[2]]),("D",omitted,t)
        for (a,b,i),k in zip(kept_stars,P):
            assert support[k]==point[a]&point[b]&~point[i],("P",omitted,(a,b,i))
        for i,k in zip(kept,A):
            assert support[k]==full&~point[i],("A",omitted,i)
    else:
        renumber={i:j for j,i in enumerate(kept)}

    live=set(D+P+A)
    todo=list(live)
    while todo:
        k=todo.pop()
        if k<=newv:
            continue
        l,r=args[k]
        assert l and r
        for child in (l,r):
            if child not in live:
                live.add(child)
                todo.append(child)
    full_rec=dict(h=m,v=newv,central_disjoint=m,
        center_denominator=m-3,
        args=[i for pair in args[newv+1:]for i in pair],
        D=D,P=P,A=A)
    stats=dict(h=m, omitted_from_h22=list(sorted(omitted)),
        omitted_from_original_h24=list(sorted((*omitted,22,23))),
        additions_created=len(args)-newv-1,
        additions_live=sum(k>newv for k in live),
        zero_nodes_removed=vanish,unary_collapses=collapse,
        duplicate_supports=dedup,
        unique_roots=len(set(D+P+A)),
        root_supports_verified=verify,
        canonical_sha256=hashlib.sha256(pack(full_rec)).hexdigest())
    return stats

def live_source(w):
    v=w["v"]
    assert v==1540 and w["h"]==22
    roots=set(w["D"]+w["P"]+w["A"])
    live=set(roots)
    todo=list(roots)
    while todo:
        k=todo.pop()
        if k<=v:continue
        a,b=w["args"][2*(k-v-1):2*(k-v-1)+2]
        for j in (a,b):
            if j not in live:
                live.add(j);todo.append(j)
    return sum(x>v for x in live)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--top",type=int,default=25)
    ap.add_argument("--output",type=Path)
    cfg=ap.parse_args()
    assert hashlib.sha256(SRC.read_bytes()).hexdigest()==SHA
    w=json.loads(gzip.decompress(SRC.read_bytes()))
    assert (w["h"],w["v"],len(w["args"])//2)==(22,1540,66234)
    old_live=live_source(w)
    assert old_live==64140,("Unexpected PR142 scalar-live baseline",old_live)
    all_rows=[]
    for dropped in (1,2):
        for i,subset in enumerate(itertools.combinations(range(22),dropped),1):
            all_rows.append(build(w,subset))
        print("Completed nested",22 if dropped==1 else 231,
              "candidate restrictions to h",22-dropped,file=sys.stderr,flush=True)
    assert len(all_rows)==253
    ranked21=sorted([x for x in all_rows if x["h"]==21],
                    key=lambda x:(x["additions_live"],x["additions_created"],x["omitted_from_h22"]))
    ranked20=sorted([x for x in all_rows if x["h"]==20],
                    key=lambda x:(x["additions_live"],x["additions_created"],x["omitted_from_h22"]))
    out=dict(status="Exact scalar DAG structural research only: no physical or kappa claims",
      pinned_h22_sha256=SHA,baseline_h22_live_additions=old_live,
      h21_count=len(ranked21),h20_count=len(ranked20),
      best_h21=ranked21[:cfg.top],best_h20=ranked20[:cfg.top],
      all_h21=ranked21,all_h20=ranked20,
      next_steps=[
       "Adapt PR142 physical producer/readout coefficient and target labels to h21 and h20",
       "Recompile the entire scalar word for chosen candidates; recertify physical R",
       "Regenerate generalized frame/gauge compiler and scratch compensation",
       "Audit every literal signed reflected scalar step, no lockstep and no uncharged frames",
       "Rebuild paid sequential padded cover, moment, 47 constraints, seven margins",
       "Verify source closure and corruption controls and run independent CI"])
    s=json.dumps(out,indent=2,sort_keys=True)+"\n"
    if cfg.output:cfg.output.write_text(s)
    else:print(s)
    print("PASS nested restrictions, best h21:",ranked21[0]["omitted_from_original_h24"],
          "best h20:",ranked20[0]["omitted_from_original_h24"],file=sys.stderr,flush=True)

if __name__=="__main__":main()
