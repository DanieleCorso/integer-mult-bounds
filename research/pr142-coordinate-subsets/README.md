# PR142 sequential cover: h22/h21/h20 structural restriction search

**Scope:** Exhaustive deterministic **structural** exploration only, not a
proved multiplication improvement. The best published live result as of the
branch fork is [PR #142](https://github.com/CrocSwap/integer-mult-bounds/pull/142):
conditional κ = **0.000420151003347** (inherited written analytic contracts
and full CI pending).

PR142 restricts PR117's 24-coordinate scalar DAG by omitting coordinates
22 and 23, but there are exactly C(24,2)=276 possible omitted pairs.
For each, `coordinate_search.py` reconstructs the restricted binary-sum DAG
from the **immutable, SHA256-pinned** PR117 witness. It checks every
remaining D/P/A root against the actual 22-coordinate triple incidence
supports, rejects overlaps/cancellations, computes full surviving
addition count, and reverse-traces *live* additions reachable from roots.
The omitted pair {22,23} must reproduce PR142's exact frozen restricted
DAG and its 66,234 created additions, byte-for-byte as a JSON object.

A smaller scalar DAG is only a **screening heuristic**: it does not imply
fewer physical scratch roles, a lower paid characteristic moment, or
valid compensated birth reuse. All potential winners need a complete
fresh PR142 producer/frame/gauge compilation with exact arbitrary-dirty
forward/reflected replay and the full padded-cover 47 constraints, seven
margins, scalar/semantic charges, and input/source manifests before a new
κ can be claimed. **Never substitute guessed complexity exponents.**

Run from the repository root:

```sh
python3 research/pr142-coordinate-subsets/coordinate_search.py --top 20 --output /tmp/coordinate-search.json
```

The sweep does not modify any PR142 source, profile, certificate or pin.
A CI workflow runs the search independently and checks its JSON results.
The branch inherits PR142 with all its contributors and source notices:
eumemic, icekylinx, an664, jamesyc, ikeboy, Zhihao Chen, Swapnil Jain,
and the historic PR117 witness. Exploration prepared with OpenAI
assistance.

## Additional h21 and h20 search

The same branch now includes `nested_restrictions.py`. It reads
**PR142's immutable, SHA256-pinned h22 restricted scalar DAG** and
tries all 22 choices of one additional omitted coordinate and all 231
choices of two additional omitted coordinates. Each derived 21- or
20-coordinate DAG undergoes the same exact disjoint-addition and
D/P/A-support tests as h22. It backward-traces all surviving roots
and counts only additions that are *actually live*.

The source h22 live-addition count is required to equal **64,140**;
its original generated-addition count is required to equal 66,234.
These are **structural** statistics, not paid recursive moments or
multiplication exponents. Moving to ambient dimension 63 or 60 would
also change the complete group geometry, bit/complex balance,
normalizers, and every interface described above.

```sh
python3 research/pr142-coordinate-subsets/nested_restrictions.py --top 25 --output /tmp/nested-search.json
```

The +3% target over PR142 is
`κ >= 0.00043275553344741`. Even a statistically smaller h21/h20
DAG is **not a new record** until its full independent physical
compiler, literal readout/inverse replay, paid sequential cover and
exact 47-constraint certificate exist. We explicitly reject merging
cores in parallel on one dirty role, as disproved in PR132/PR139.
