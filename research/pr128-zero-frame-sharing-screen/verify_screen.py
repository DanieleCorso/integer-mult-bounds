#!/usr/bin/env python3
"""Independent exact geometric and arithmetic screen for PR128 h=23 sharing.

This DOES NOT certify a legal bit-core sharing implementation or a new kappa.
The signed physical schedule, local Gaussian normalization, scalar charges
and coupled recurrence proof remain obligations. Standard library only.
"""
import json
import os
import sys
from collections import Counter
from fractions import Fraction as Q
from itertools import combinations
from math import factorial
from pathlib import Path

if sys.flags.optimize or os.environ.get("PYTHONOPTIMIZE"):
    raise RuntimeError("assertions must not be disabled")
HERE = Path(__file__).resolve().parent


def require(ok, why):
    if not ok:
        raise AssertionError(why)


def parity(x):
    return x.bit_count() & 1


def gf_basis(vectors, width):
    piv = {}
    for v in vectors:
        x = v
        while x:
            j = x.bit_length()-1
            if j in piv:
                x ^= piv[j]
            else:
                piv[j] = x
                break
    return piv


def nullspace(vectors, width):
    # Reduced echelon form of the rows of the orthogonality constraints.
    piv = gf_basis(vectors, width)
    for j in sorted(piv):
        for k in piv:
            if j != k and (piv[k] >> j) & 1:
                piv[k] ^= piv[j]
    free = [j for j in range(width) if j not in piv]
    result = []
    for j in free:
        x = 1 << j
        for k, row in piv.items():
            if (row >> j) & 1:
                x ^= 1 << k
        result.append(x)
    require(all(parity(x & row) == 0 for x in result for row in vectors),
            "nullspace mistake")
    return result


def quadratic_signature(B):
    # Exact four-phase Gauss sum: real=cnt[0]-cnt[2],
    # imaginary=cnt[1]-cnt[3]. Enumerate Gray-coded basis vectors.
    counts = [0, 0, 0, 0]
    x = 0
    for k in range(1 << len(B)):
        if k:
            j = (k & -k).bit_length()-1
            x ^= B[j]
        counts[x.bit_count() % 4] += 1
    return (counts[0]-counts[2], counts[1]-counts[3])


def ln_interval(x, terms=48):
    # Normalize 1 <= u < 2; artanh has a rational nonnegative tail bound.
    require(x >= 1, "log argument below one")
    power = 0
    u = x
    while u >= 2:
        power += 1
        u /= 2

    def unit(z):
        y = (z-1)/(z+1)
        termsum = 2*sum((y**(2*j+1)/Q(2*j+1)
                         for j in range(terms)), Q(0))
        rem = 2*y**(2*terms+1)/(Q(2*terms+1)*(1-y*y))
        return (termsum, termsum+rem)

    a,b = unit(u)
    c,d = unit(Q(2))
    return (a+power*c, b+power*d)


def exp_interval(lo, hi, degree=12):
    require(0 <= lo <= hi < 1, "bad exponential argument")
    low = sum((lo**k/Q(factorial(k)) for k in range(degree+1)), Q(0))
    upper = sum((hi**k/Q(factorial(k)) for k in range(degree+1)), Q(0))
    upper += hi**(degree+1)/Q(factorial(degree+1))/(1-hi/Q(degree+2))
    return low, upper


def moment_interval(hist, m, W, saving):
    low = high = Q(0)
    for r, count in sorted(hist.items()):
        if not count:
            continue
        require(0 < r < m and count > 0, "invalid recursive child")
        lglo, lghi = ln_interval(Q(m, r))
        elo, ehi = exp_interval(saving*lglo, saving*lghi)
        factor = Q(r*count, m*W)
        low += factor*elo
        high += factor*ehi
    return low, high


def main():
    p = json.loads((HERE/"pr128-bit-profile.json").read_text())
    z = json.loads((HERE/"restricted-groups.json").read_text())
    h,m,v,R,N,W,deficit = (p[k] for k in
                             ("h","m","v","R","N","W","deficit")) if "h" in p else (
                             23,p["m"],p["v"],p["R"],p["N"],p["W"],p["deficit"])
    require((h,m,v,R,N,W,deficit)==
            (23,529,1771,28866,3136441,108516254,1344189),
            "pinned PR128 dimensions changed")
    require(z["h"]==h and len(z["groups"])==87, "group dimensions")
    masks = [sum(1<<i for i in t) for t in combinations(range(h),3)]
    require(len(masks)==v, "triple enumeration")
    groups = z["groups"]
    flat = [i for group in groups for i in group]
    require(Counter(flat)==Counter(range(v)), "partition must cover each triple once")
    require(Counter(map(len, groups))=={21:83,7:4}, "unexpected restricted group sizes")

    signatures = Counter()
    tested_gram = tested_phase = 0
    x_tests = [0]
    x_tests += [1<<i for i in range(h)]
    x_tests += [(1<<i)|(1<<j) for i,j in combinations(range(h),2)]
    for group in groups:
        B = [masks[i] for i in group]
        for a in range(len(B)):
            for b in range(len(B)):
                require(parity(B[a]&B[b]) == (a==b),
                        "group binary Gram matrix not I")
                tested_gram += 1
        C = nullspace(B,h)
        require(len(C)==h-len(B), "complement dimension")
        require(len(gf_basis([sum(parity(a&b)<<j for j,b in enumerate(C))
                              for a in C],len(C)))==len(C),
                "complement Gram matrix singular")
        gauss = quadratic_signature(C)
        signatures[(len(B),len(C),gauss[0],gauss[1])] += 1
        for x in x_tests:
            projected = 0
            for b in B:
                if parity(x&b):
                    projected ^= b
            remaining = x^projected
            require((x.bit_count() - projected.bit_count()
                     - remaining.bit_count())%4==0,
                    "signed Gaussian quadratic phase mismatch")
            tested_phase += 1

    require(signatures=={(21,2,-2,0):83,(7,16,0,-256):4},
            "unexpected signed complement types")
    H = Counter({int(k):int(n) for k,n in p["hist"].items()})
    old_mass = sum(k*n for k,n in H.items())
    require(old_mass == m*W-deficit, "original pinned rank mass")
    ext = {int(k):int(n) for k,n in p["exterior_hist"].items()}
    require(all(H[k]>=n for k,n in ext.items()), "exterior multiplicity")
    count_zero = ext[m-h]
    require(count_zero%(2*v)==0, "zero-frame role count nonintegral")
    roles_zero=count_zero//(2*v)
    require(roles_zero==17597, "unexpected zero-start-role count")

    # Remove exactly the old terminal exteriors of the zero-frame roles.
    # Each candidate shared role instead has one final group complement
    # per stage. Other local and full-frame children remain unchanged.
    H[m-h]-=count_zero
    if not H[m-h]:
        del H[m-h]
    for group in groups:
        H[h*(h-len(group))] += 2*roles_zero
    newW = 2*N+2*v*(R-roles_zero)+2*len(groups)*roles_zero
    new_mass = sum(k*n for k,n in H.items())
    require(newW==49249558, "unexpected candidate allocation")
    require(new_mass==m*newW-deficit, "rank mass/deficit mismatch")
    require(all(0<rank<m and n>0 for rank,n in H.items()), "invalid child")
    # The next tests certify the ARITHMETIC MOMENT of an assumed
    # paid child histogram; they do not show that histogram can be
    # realized by the physical bit-core word.
    lower=Q(1380218257,10**13)
    next_point=lower+Q(1,10**13)
    low,high=moment_interval(H,m,newW,lower)
    nextlow,nexthi=moment_interval(H,m,newW,next_point)
    require(high<1, "candidate moment fails to contract")
    require(nextlow>1, "next moment grid point was not rejected")
    old_saving=Q(384599,10**10)
    stopped=(1-Q(1,1000))*lower+Q(1,1000)*old_saving
    pr128_bit=Q("0.0001244501335381315811393")
    require(stopped*100>pr128_bit*110,
            "less than 10 percent conditional arithmetic saving")
    complex_pr128=Q("0.0001231305483517511358")
    overall_baseline=Q("0.00012310001053253")
    target=overall_baseline*Q(103,100)
    require(complex_pr128<target, "complex bottleneck check changed")

    result = {
        "status":"PASS exact geometry and conditional moment screen; NOT a physical proof",
        "baseline":"PR128 commit 530588a019b4a74f09180680c9e3961bf649ec89",
        "triples":v,"groups":len(groups),
        "group_counts":dict(Counter(map(len,groups))),
        "gram_entries_checked":tested_gram,
        "quadratic_phase_cases":tested_phase,
        "signed_complements":[
          {"group_dimension":d,"complement_dimension":c,
           "gauss_real":re,"gauss_imag":im,"groups":n}
          for (d,c,re,im),n in sorted(signatures.items())
        ],
        "zero_frame_original_roles":roles_zero,
        "original_W":W,"screened_W":newW,
        "original_deficit":deficit,"screened_deficit":m*newW-new_mass,
        "complete_screened_children":{str(k):n for k,n in sorted(H.items())},
        "moment_parameter_lower":str(lower),
        "moment_upper_below_one":str(1-high),
        "next_grid_point_rejected":str(next_point),
        "next_grid_lower_exceeds_one":str(nextlow-1),
        "conditional_stopped_bit_saving_lower":str(stopped),
        "baseline_pr128_stopped_bit":str(pr128_bit),
        "baseline_pr128_kappa":str(overall_baseline),
        "target_plus_three_percent":str(target),
        "pr128_unchanged_complex_ceiling":str(complex_pr128),
        "required_before_final_kappa_claim":[
            "formal independently restored bit-core scratch identity",
            "literal forward/reflected physical frame schedule for shared roles",
            "paid signed Gaussian normal forms for -2 and -256i complements",
            "basis/phase/scalar/semantic precision charges",
            "coupled exact complex+bit recurrence certificate"
        ],
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__=="__main__":
    main()
