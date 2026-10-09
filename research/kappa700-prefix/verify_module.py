#!/usr/bin/env python3
"""Independent exhaustive arithmetic verification of the local candidate module."""
import itertools
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
old = json.loads((HERE.parent.parent / "references/paired-cube/sources/qmod_anneal_best01.json").read_text())
new = json.loads((HERE / "qmod_prefix_suffix_n9.json").read_text())

def check(d):
    n = d["input_count"]
    a = d["args"]
    assert a[:n] == [None] * n
    assert len(d["roots"]) == n
    masks = [1 << i for i in range(n)]
    for j, pair in enumerate(a[n:], n):
        assert len(pair) == 2
        x, y = pair
        assert 0 <= x < j and 0 <= y < j
        assert masks[x] & masks[y] == 0, ("overlapping supports", j)
        masks.append(masks[x] | masks[y])
    for i, r in enumerate(d["roots"]):
        assert masks[r] == ((1 << n) - 1) ^ (1 << i)
    for values in itertools.product((-1, 0, 1), repeat=n):
        z = list(values)
        for x,y in a[n:]:
            z.append(z[x] + z[y])
        assert [z[r] for r in d["roots"]] == [sum(values)-values[i] for i in range(n)]
    return len(a)-n

if __name__ == "__main__":
    a,b=check(old),check(new)
    assert (a,b)==(29,21)
    print("PASS: 3**9 all-input assignments, both module identities, support disjointness, and node DAG ordering")
    print("old additions:",a,"new additions:",b,"saved:",a-b)
