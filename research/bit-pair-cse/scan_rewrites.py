#!/usr/bin/env python3
"""Read-only exact PR168 p12 carrier-matching audit of local pair-module rewires.

All alternative factorizations retain every existing intermediate subset value.
This uses upstream BitGraph, modulo-2 decoder, exact rational frame geometry,
and Hopcroft-Karp matcher without transferring any pinned match/physical word.
No kappa claim. Lineage: icekylinx and eumemic, OpenAI-assisted audit.
"""
import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "research/paired-cube-bit"))
import paired_cube_bit_word as bit


def alternatives(data):
    n = data["input_count"]
    supports = [1 << i for i in range(n)]
    by_support = {s: i for i, s in enumerate(supports)}
    for a, b in data["args"][n:]:
        assert not supports[a] & supports[b]
        supports.append(supports[a] | supports[b])
        assert supports[-1] not in by_support, "Baseline support duplication"
        by_support[supports[-1]] = len(supports)-1
    options = []
    for x in range(n, len(supports)):
        seen = {tuple(sorted(data["args"][x]))}
        for a in range(x):
            if supports[a] & supports[x] != supports[a]:
                continue
            b = by_support.get(supports[x] ^ supports[a])
            if b is None or not a < b < x:
                continue
            ab = (a, b)
            if ab not in seen:
                seen.add(ab)
                options.append((x, a, b))
    assert len(options) == 61, "Frozen pair source changed; re-audit options"
    return options


def check_local(data):
    n = data["input_count"]
    supports = [1 << i for i in range(n)]
    for x, ab in enumerate(data["args"][n:], n):
        a, b = ab
        assert a < x and b < x and not supports[a] & supports[b]
        supports.append(supports[a] | supports[b])
    assert len(data["roots"]) == n == 55
    from itertools import combinations
    labels = list(combinations(range(11), 2))
    expected = [sum(1 << k for k, (u, w) in enumerate(labels)
                    if u not in T and w not in T) for T in labels]
    assert [supports[r] for r in data["roots"]] == expected


def score(pair, q):
    G = bit.BitGraph(12)
    graph = G.finish(pair, q, merge=True, l1=True)
    assert bit.check_decoder(graph) == 0, "Full F2 decoder"
    profile, witness = bit.compile_word(graph, frozen=None)
    assert profile["R"] == profile["c"] + profile["q"] - profile["matched"]
    return {k: profile[k] for k in ("c", "q", "matched", "R", "loss")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true", help="List all local rewrites; fast")
    parser.add_argument("--all", action="store_true", help="Score all 61; expensive")
    parser.add_argument("--node", type=int, help="One module operation index")
    parser.add_argument("--a", type=int)
    parser.add_argument("--b", type=int)
    args = parser.parse_args()
    folder = ROOT / "research/paired-cube-bit/data"
    pair = json.loads((folder / "pair_module_p12.json").read_text())
    q = json.loads((folder / "qmod_p12.json").read_text())
    opts = alternatives(pair)
    if args.list:
        print(json.dumps(opts))
        return
    if args.all:
        candidates = opts
    else:
        assert None not in (args.node, args.a, args.b), "Choose --list, --all, or --node X --a A --b B"
        candidates = [(args.node, args.a, args.b)]
        assert candidates[0] in opts, "Not a support-preserving alternative"
    base = score(pair, q)
    assert base == dict(c=23260,q=6624,matched=10096,R=19788,loss=528), "Positive baseline control"
    print("BASELINE", json.dumps(base), flush=True)
    for x, a, b in candidates:
        mod = dict(pair, args=list(pair["args"]))
        mod["args"][x] = [a, b]
        check_local(mod)
        result = score(mod, q)
        print("REWRITE", x, a, b, "R",result["R"], "delta_R",result["R"]-base["R"],flush=True)
    print("No saved physical certificate can be reused; no assembled kappa asserted.")


if __name__ == "__main__":
    main()
