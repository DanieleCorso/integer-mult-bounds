#!/usr/bin/env python3
"""Search all 276 ways to restrict PR117's pinned h24 DAG to h22.

Read-only structural research: root supports and scalar DAG metrics are
checked exhaustively; no physical frame, scratch, or kappa improvements
are inferred from a smaller DAG. PR142's [22,23] restriction is an
exact pinned regression baseline.
"""
import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
import gzip
import json
import sys

if sys.flags.optimize:
    raise ValueError("Never optimize away invariant checks")
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCES = ROOT / "research/cyclic-deferred"
DAG_PIN = "3c034d0aae388ef567a454826f4f48b26fd8a94c71e8ffed4835271b349a783b"
OLD_TRIP = list(combinations(range(24),3))
OLD_TID = {t:i for i,t in enumerate(OLD_TRIP)}
OLD_STAR = [(a,b,i) for a,b in combinations(range(24),2)
            for i in range(24) if i not in(a,b)]

def canonical(o):
    return json.dumps(o, separators=(",",":")).encode()

def candidate(w, omit, verify_roots=True):
    omit = tuple(sorted(omit))
    assert len(omit)==2 and len(set(omit))==2
    keep = tuple(i for i in range(24) if i not in omit)
    h = len(keep)
    triples = list(combinations(keep,3))
    v = len(triples)
    assert h==22 and v==1540
    ids = {t:i+1 for i,t in enumerate(triples)}
    remap = {0:0}
    support = [0]+[1<<i for i in range(v)]
    args = [(0,0)]*(v+1)
    lookup = {x:i for i,x in enumerate(support)}
    for i,t in enumerate(OLD_TRIP,1):
        remap[i]=ids.get(t,0)
    vanished=unary=dedup=0
    for j in range(0,len(w["args"]),2):
        old = len(OLD_TRIP)+1+j//2
        a,b = (remap[k] for k in w["args"][j:j+2])
        if not a or not b:
            remap[old]=a or b
            vanished += not (a or b)
            unary += bool(a or b)
            continue
        assert not support[a] & support[b], ("Overlapping original DAG supports",omit,old)
        s = support[a] | support[b]
        if s in lookup:
            remap[old] = lookup[s]
            dedup += 1
            continue
        node = len(support)
        support.append(s)
        lookup[s] = node
        args.append((a,b))
        remap[old] = node

    D=[remap[w["D"][OLD_TID[t]]] for t in triples]
    P=[remap[n] for old,n in zip(OLD_STAR,w["P"])
       if not any(i in omit for i in old)]
    A=[remap[w["A"][i]] for i in keep]
    assert len(D)==v and len(P)==3*v and len(A)==h
    assert len(support)==len(args)

    if verify_roots:
        point = [sum(1<<j for j,t in enumerate(triples) if i in t) for i in keep]
        full=(1<<v)-1
        for t,node in zip(combinations(range(h),3),D):
            assert support[node] == full & ~(point[t[0]]|point[t[1]]|point[t[2]]),(
                "Incorrect D-support",omit,t)
        stars = [(a,b,i) for a,b in combinations(range(h),2)
                 for i in range(h) if i not in(a,b)]
        for (a,b,i),node in zip(stars,P):
            assert support[node]==point[a]&point[b]&~point[i],(
                "Incorrect P-support",omit,(a,b,i))
        for i,node in enumerate(A):
            assert support[node]==full&~point[i],("Incorrect A-support",omit,i)

    # Backwards exact DAG liveness, not an estimate based only on total nodes.
    live=set(D+P+A)
    todo=list(live)
    while todo:
        k=todo.pop()
        if k<=v:
            continue
        a,b=args[k]
        assert a!=0 and b!=0
        for s in (a,b):
            if s not in live:
                live.add(s)
                todo.append(s)
    live_additions=sum(k>v for k in live)
    record=dict(h=h,v=v,central_disjoint=h,center_denominator=h-3,
                args=[s for ab in args[v+1:] for s in ab],
                D=D,P=P,A=A)
    assert (len(record["args"])//2)==len(args)-v-1
    result=dict(omitted=list(omit),coordinates_kept=list(keep),
                additions_created=len(args)-v-1,
                additions_live=live_additions,
                additions_dead=len(args)-v-1-live_additions,
                zero_nodes_removed=vanished,
                unary_nodes_collapsed=unary,
                supports_deduplicated=dedup,
                unique_roots=len(set(D+P+A)),
                root_supports_verified=bool(verify_roots),
                candidate_canonical_sha256=sha256(canonical(record)).hexdigest())
    return record,result

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--top",type=int,default=20)
    p.add_argument("--output",type=Path)
    p.add_argument("--skip-roots",action="store_true",
                   help="For speed only; cannot be used to claim validated roots")
    ns=p.parse_args()
    source = SOURCES / "inputs/complex-dag.json.gz"
    assert sha256(source.read_bytes()).hexdigest()==DAG_PIN
    w=json.loads(gzip.decompress(source.read_bytes()))
    assert (w["h"],w["v"])==(24,2024)
    rows=[]
    for idx,omitted in enumerate(combinations(range(24),2),1):
        record,stats=candidate(w,omitted,not ns.skip_roots)
        if omitted==(22,23):
            frozen=json.loads(gzip.decompress(
                (SOURCES/"inputs/restricted-dag.json.gz").read_bytes()))
            assert record==frozen, "PR142 baseline restriction changed"
            baseline=stats
        rows.append(stats)
        if idx%24==0:
            print("Structural subsets screened",idx,"/",276,
                  "best live additions",min(r["additions_live"] for r in rows),
                  file=sys.stderr,flush=True)
    assert len(rows)==276 and baseline is not None
    assert baseline["additions_created"]==66234,"PR142 h22 baseline metric changed"
    # The LIVE metric is preliminary. Full physical R, gauges, exact child
    # histogram, reflected dirty replay, and aggregate certificate are required.
    ranked=sorted(rows,key=lambda s:(s["additions_live"],s["additions_created"],s["omitted"]))
    out=dict(status="Exact h22 scalar DAG screen ONLY; no new kappa",
             source_sha256=DAG_PIN,baseline_pr142=baseline,
             examined_subsets=len(rows),valid_root_checks=not ns.skip_roots,
             best=ranked[:ns.top],baseline_live_rank=1+next(
                 i for i,item in enumerate(ranked) if item["omitted"]==[22,23]),
             minimum_live_additions=min(x["additions_live"] for x in rows),
             scored_by="backward-live scalar DAG additions (not a physical cost)",
             all_cases=rows,
             followup_gates=[
               "Recompile candidate PR117 physical word for selected omitted pair",
               "Validate compensated donor reuse, source gauge nesting and arbitrary dirty input replay",
               "Audit signed forward/reflected frames and scalar work",
               "Rebuild full paid 3-stage sequential triples, moments and coupled kappa",
               "Run complete 37 mutation controls, source closure and Python CI"])
    encoded=json.dumps(out,indent=2,sort_keys=True)+"\n"
    if ns.output:
        ns.output.write_text(encoded)
    else:
        print(encoded)
    print("PASS 276 exact structural restrictions; best",ranked[0]["omitted"],
          "live additions",ranked[0]["additions_live"],
          "PR142 live rank",out["baseline_live_rank"],file=sys.stderr,flush=True)

if __name__=="__main__":main()
