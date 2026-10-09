#!/usr/bin/env python3
"""Exact full p=12 bit decoder, side-root frame geometry, and DAG-use checks.

Reuses the original PR168 BitGraph and decoder (eumemic, icekylinx) without
modifying upstream source; replaces only the two modules under experiment.
This is NOT a matching, physical frame, characteristic, or kappa certificate.
Prepared with OpenAI GPT-6 assistance. Apache-2.0, upstream credits retained.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "research/paired-cube-bit"))
from search import check, construct
from trial import smaller_allbut, verify_allbut
import paired_cube_bit_word as bit


def examine(pair, complement):
    G = bit.BitGraph(12)
    graph = G.finish(pair, complement, merge=True, l1=True)
    v, args = graph["v"], graph["args"]
    assert v == 1760 and len(graph["roots"]) == 6624
    assert bit.check_decoder(graph) == 0, "Full F2 decoder identity"
    supports = G.s
    assert len(supports) == len(args)
    labels = [set(t) for t in graph["labels"]]
    compatible = []
    for t in labels:
        mask = 0
        for i, s in enumerate(labels):
            if len(t.intersection(s)) == 1:
                mask |= 1 << i
        compatible.append(mask)
    checked = 0
    for root in graph["roots"]:
        if root["kind"] != "side":
            continue
        support = supports[root["node"]]
        for target in root["targets"]:
            assert support & ~compatible[target] == 0, (
                "Side-root target-cap incompatibility", root["channel"], target
            )
            checked += 1
    assert checked == 8800
    active = set(range(v))
    stack = [root["node"] for root in graph["roots"]]
    while stack:
        x = stack.pop()
        if x in active:
            continue
        active.add(x)
        if args[x] is not None:
            stack.extend(args[x])
    stats = dict(
        p=12, v=v, total_roots=len(graph["roots"]), geometry_checks=checked,
        graph_additions=len(args) - v,
        active_additions=len(active) - v,
        dead_additions=len(args) - len(active),
    )
    assert stats["dead_additions"] == 0, "No dead arithmetic nodes"
    return stats


def main():
    pair = construct(11, seed=68, temp=0.75, bias=10.0)
    complement = smaller_allbut(10)
    assert check(pair, 11) == 397 and verify_allbut(complement) == 24
    result = examine(pair, complement)
    # Mutation controls: wrong local roots must fail the full 1760-port decoder.
    wrong_pair = dict(pair, roots=list(pair["roots"]))
    wrong_pair["roots"][0] = wrong_pair["roots"][1]
    bad_pair = bit.BitGraph(12).finish(wrong_pair, complement, merge=True, l1=True)
    assert bit.check_decoder(bad_pair) == 80
    wrong_q = dict(complement, roots=list(complement["roots"]))
    wrong_q["roots"][0] = wrong_q["roots"][1]
    bad_q = bit.BitGraph(12).finish(pair, wrong_q, merge=True, l1=True)
    assert bit.check_decoder(bad_q) == 440
    result["mutation_controls_rejected"] = ["wrong_pair_root", "wrong_complement_root"]
    baseline = json.loads(
        (ROOT / "research/paired-cube-bit/out/profile_p12.json").read_text()
    )
    assert baseline["c"] == 23260, "Source-pinned baseline drift"
    result["baseline_live_additions"] = baseline["c"]
    result["saved_live_additions"] = baseline["c"] - result["active_additions"]
    assert result["saved_live_additions"] == 1860
    print("PASS EXACT P12 DECODER / SIDE GEOMETRY / DAG:", json.dumps(result))
    print("NOT A KAPPA CLAIM: matching, physical bit word and full bridge pending")


if __name__ == "__main__":
    main()
