#!/usr/bin/env python3
"""Necessary-condition scan of PR129's frozen h23 scalar scratch lifetimes.

Reads pinned PR129 bit schedule. It does NOT modify the construction or claim
a valid alias: the frame-inclusion, readout compensation, arbitrary dirty
restore, opposite-bank bit compiler and total cost are separate proof gates.
"""
from __future__ import annotations
import bisect
import gzip
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

if sys.flags.optimize:
    raise RuntimeError("Do not use -O: assertions are essential.")

REPO = Path(__file__).resolve().parents[2]
P = REPO / "research/cyclic-deferred/bit-sharing/inputs/research"
sys.path.insert(0, str(P / "round7-public/tree/independent/deferred-readout"))
import deferred

def readgz(p):
    return json.loads(gzip.decompress(p.read_bytes()))

def main():
    W, D = deferred.load(23)
    S = deferred.Schedule(W, D)
    require = lambda condition, description: condition or (_ for _ in ()).throw(
        AssertionError(description))
    require(S.R == 28866 and S.h == 23 and S.v == 1771, "PR129 bit dimensions")
    word = readgz(P / "round8-foundations-minimal-v-word.json.gz")
    sigma = dict(S.sigma)
    for s in word["removed_original_slots"]:
        require(s in sigma, "Unknown removed readout")
        del sigma[s]
    for s, B in word["new_frames"].items():
        sigma[int(s)] = B
    selected = set(sigma)
    read_events = [s for kind, s in word["events"] if kind == "read" and s in selected]
    require(len(read_events) == len(selected) == len(set(read_events)),
            "Readout events disagree with frozen candidate")

    previous = {}
    pred = [set() for _ in S.ops]
    first, last = {}, {}
    event_roles = defaultdict(list)
    for i, op in enumerate(S.ops):
        roles = S.touch(op)
        for s in roles:
            require(0 <= s < S.R, "scratch index")
            first.setdefault(s, i)
            if s in previous:
                pred[i].add(previous[s])
            previous[s] = i
            last[s] = i
            event_roles[s].append(i)
    # The earliest complete phase is the dependency closure of all retained
    # centre values. This mirrors the compensated complex birth-cut screen,
    # but cannot itself justify reusing physical bit slots.
    phase = set()
    stack = [last[s] for s in S.ret if s in last]
    while stack:
        i = stack.pop()
        if i not in phase:
            phase.add(i)
            stack.extend(pred[i])
    phase_roles = {s for i in phase for s in S.touch(S.ops[i])}

    terminal = set(S.out) | set(S.ret)
    available_donors = []
    for s in range(S.R):
        if s in terminal or s in selected or s not in last:
            continue
        if last[s] not in phase:
            continue
        try:
            end_dimension = S.dim(("n", S.hold[s][-1]))
        except KeyError:
            continue
        # Also inspect the actual role end chain: no dimension inference is
        # ever used as if it established geometric containment.
        chain = S.chain_keys(s)
        chain_dims = [S.dim(key) for key in chain]
        require(all(y >= x for x, y in zip(chain_dims, chain_dims[1:])),
                "Donor original frame chain not monotone")
        available_donors.append((last[s], s, end_dimension))

    recipient = []
    for s in selected:
        if s in terminal or s not in first or s in phase_roles:
            continue
        i = first[s]
        op = S.ops[i]
        if op[0] != "fan" or s not in op[2]:
            continue
        dim = len(sigma[s])
        # Only an optimistic DIMENSION filter: inclusions of the exact
        # rational frames remain unverified. Fan birth must remain protected.
        if dim:
            recipient.append((i, s, dim))
    available_donors.sort()
    recipient.sort()
    pending = []
    cursor = 0
    picked = []
    for when, birth_slot, bound in recipient:
        while cursor < len(available_donors) and available_donors[cursor][0] < when:
            t, donor, edim = available_donors[cursor]
            bisect.insort(pending, (edim, donor, t))
            cursor += 1
        # Choose closest dimension from below. This is only a cardinality
        # screen, not a proof of vector-space inclusion or full simulation.
        chosen = bisect.bisect_right(pending, (bound, S.R+1, len(S.ops)+1))-1
        if chosen >= 0:
            edim, donor, death = pending.pop(chosen)
            picked.append((donor, birth_slot, death, when, edim, bound))
    require(len({r[0] for r in picked}) == len(picked), "donor alias")
    require(len({r[1] for r in picked}) == len(picked), "recipient alias")
    require(all(t<birth and d<=b for _,_,t,birth,d,b in picked),
            "optimistic chronological/dimension filter")

    R = S.R
    g = 161
    m = 529
    N = S.v*S.v
    baseline_W = 2*N+2*g*R
    hypothetical_W=2*N+2*g*(R-len(picked))
    require(baseline_W==15567734, "original bit width")
    summary = dict(
        status="SCREEN ONLY - NO NEW KAPPA OR LEGAL ALIAS CLAIM",
        source="PR129 frozen minimal-V word and deferred_23 schedule",
        original_bit_physical_roles=R,
        original_bit_groups=g,
        original_bit_W=baseline_W,
        centre_closure_operations=len(phase),
        centre_closure_roles=len(phase_roles),
        potential_dead_donors_before_frame_check=len(available_donors),
        deferred_readouts=len(selected),
        untouched_deferred_fan_births=len(recipient),
        optimistically_chronological_and_dimension_compatible_matches=len(picked),
        hypothetical_W_if_all_matches_were_valid=hypothetical_W,
        optimistic_width_reduction_fraction=f"{baseline_W-hypothetical_W}/{baseline_W}",
        donors_by_end_dimension=dict(sorted(Counter(x[2] for x in available_donors).items())),
        recipients_by_sigma_dimension=dict(sorted(Counter(x[2] for x in recipient).items())),
        matched_dimension_pairs=dict(sorted(Counter(f"{row[4]}->{row[5]}" for row in picked).items())),
        sample_matches=[dict(donor=x[0],recipient=x[1],donor_last_op=x[2],
                             recipient_birth_op=x[3],donor_dim=x[4],recipient_dim=x[5])
                        for x in picked[:12]],
        missing_gates=[
            "exact rational source/end-frame containment for all matched pairs",
            "literal candidate-word readout chronology and birth compensation",
            "formal all-column arbitrary-dirty forward and reflected replay",
            "full retained old readout responses after aliasing",
            "corrected physical projectors, grouped complements and paid adapters",
            "complete moment, scalar/semantic and coupled assembly verification",
        ],
    )
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("NOTE: counts measure necessary conditions ONLY.", file=sys.stderr)

if __name__ == "__main__":
    main()
