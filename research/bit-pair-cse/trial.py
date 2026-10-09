#!/usr/bin/env python3
"""Research-only full bit graph experiment against PR168 revision 4a3c769.

Rebuilds a NEW signed-free bit graph with the optimized pair + all-but-one
modules, verifies its decoder, recomputes a fresh Hopcroft-Karp carrier
matching, all frames, chronological gauges, shared-core ledger, and estimates
the pre-physical characteristic root. It does NOT carry forward the old
physical word, pairing, prime or assembled kappa certificates.

Contributors: source design/decoder/bit compiler by eumemic and icekylinx,
experimental search and integration prepared with OpenAI GPT-6.
"""
import argparse
from itertools import product
import json
from pathlib import Path
import sys
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
sys.path.insert(0,str(HERE))
sys.path.insert(0,str(ROOT/'research/paired-cube-bit'))
from search import construct, check
import paired_cube_bit_word as bit

def smaller_allbut(n):
    """Binary-addition-only n-input prefix/suffix complement, 3n-6 additions."""
    args=[None]*n
    p=list(range(n));s=list(range(n))
    for k in range(1,n-1):
        p[k]=len(args);args.append([p[k-1],k])
    for k in range(n-2,0,-1):
        s[k]=len(args);args.append([k,s[k+1]])
    roots=[s[1]]
    for k in range(1,n-1):
        roots.append(len(args));args.append([p[k-1],s[k+1]])
    roots.append(p[n-2])
    obj=dict(input_count=n,args=args,roots=roots)
    verify_allbut(obj)
    return obj

def verify_allbut(obj):
    n=obj['input_count'];sup=[1<<i for i in range(n)]
    for x,ab in enumerate(obj['args'][n:],n):
        a,b=ab;assert 0<=a<x and 0<=b<x and not sup[a]&sup[b]
        sup.append(sup[a]|sup[b])
    assert [sup[x] for x in obj['roots']]==[(1<<n)-1-(1<<i) for i in range(n)]
    for data in product((-1,0,1),repeat=n):
        vals=list(data)
        for a,b in obj['args'][n:]:vals.append(vals[a]+vals[b])
        assert [vals[x] for x in obj['roots']]==[sum(data)-data[i] for i in range(n)]
    return len(obj['args'])-n

def make_profile(pair,abo,check_nondegenerate):
    g=bit.BitGraph(12).finish(pair,abo,merge=True,l1=True)
    bit.require(bit.check_decoder(g)==0,'all 1760 binary decoder target identities')
    prof,wit=bit.compile_word(g,frozen=None)
    selected,H,Y,word=bit.select_gauges(g,prof,wit)
    row=bit.profile(prof,selected,H,Y)
    if check_nondegenerate:
        geo=wit['geo'];cache={}
        bad=sum(not bit.nondeg_id(geo,geo.perp(wit['ann'][x]),cache) for x in wit['order'])
        bad+=sum(not bit.nondeg_id(geo,U,cache) for U in wit['rframe'])
        bit.require(bad==0,'nondegenerate used node/root frames')
    return dict(profile=row,nodes=len(g['args']), roots=len(g['roots']),
                unphysical_float_root=bit.float_root(row['child_histogram'],row['W_per_vertex'],row['m']),
                physical_replay='NOT PERFORMED',exact_moment='NOT PERFORMED',
                clean_old_word_reuse='FORBIDDEN')

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--variant',choices=['pair','allbut','both'],default='both')
    ap.add_argument('--no-nondegeneracy',action='store_true')
    a=ap.parse_args()
    pdata=ROOT/'research/paired-cube-bit/data'
    old_pair=json.loads((pdata/'pair_module_p12.json').read_text())
    old_abo=json.loads((pdata/'qmod_p12.json').read_text())
    pair=construct(11,seed=68,temp=0.75,bias=10.0)
    assert check(pair,11)==397
    assert len(old_pair['args'])-55==442
    q=smaller_allbut(10)
    assert len(old_abo['args'])-10==33 and verify_allbut(q)==24
    print('PASS standalone: pair 442 -> 397; allbut 33 -> 24',flush=True)
    if a.variant=='allbut':pair=old_pair
    if a.variant=='pair':q=old_abo
    # Source-pinned baseline is not recomputed/modified; it is an external
    # reference whose exact moment is not transferred to this new graph.
    before=json.loads((ROOT/'research/paired-cube-bit/out/profile_p12.json').read_text())
    baseline=dict(R=before['R'],matched=before['matched'],W=before['W_per_vertex'],
        coarse_float_root=bit.float_root(before['child_histogram'],before['W_per_vertex'],before['m']))
    print('baseline',json.dumps(baseline),flush=True)
    print('compiling NEW entire bit graph and physical geometry (slow)...',flush=True)
    result=make_profile(pair,q,not a.no_nondegeneracy)
    print('PASS graph and decoder; candidate',json.dumps(result,sort_keys=True),flush=True)
    print('WARNING: no kappa is certified until a fresh physical word, exact moments, prime checks and the entire finite bridge pass',flush=True)

if __name__=='__main__':main()
