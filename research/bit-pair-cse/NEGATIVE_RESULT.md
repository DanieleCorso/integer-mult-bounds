# Exact matching audit: smaller modules do not improve the bit supplier

**Scope:** upstream PR168 at `4a3c769e5c5430e7114c4d3e099ff34664677f17` (conditional κ=0.0006558894), bit p=12 graph. This is a research result, **not a new κ or an exponent theorem**.

The n=11 disjoint-pair module uses 397 additions instead of the original 442; the n=10 all-but-one module uses 24 instead of 33. Exact local checks passed, including every output support and signed-integer replays. Rebuilding the complete graph with both replacements passed the binary decoder for all 1,760 ports, 8,800 side-target frame compatibility checks, and found no dead additions. Mutating a pair or complement root is rejected by the decoder (80 and 440 wrong output ports).

**The exact carrier matching reverses the apparent gain:**

| Bit graph | Live additions c | Query roots q | Matched arcs | R = c + q − matched |
|---|---:|---:|---:|---:|
| PR168 original | 23,260 | 6,624 | 10,096 | **19,788** |
| 397 pair, original complement | 22,588 | 6,624 | 5,632 | 23,580 |
| Original pair, 24 complement | 22,072 | 6,624 | 7,720 | 20,976 |
| 397 pair, 24 complement | 21,400 | 6,624 | 3,256 | 24,768 |

The original graph and matching profile are reproduced exactly. Each candidate is compiled with a **fresh** maximum matching; old arcs are never transferred. Lower additions do **not** mean lower virtual role stock. It would be invalid to copy the original physical reuse, prime certificates, or assembled κ certificate to these changed graphs.

**Research direction:** Optimize `c − matched` rather than `c`; preserve carrier-friendly internal subexpressions and investigate full-word physical frame savings. None of the current candidates qualifies for a +3% κ claim. Do not merge as an exponent improvement.

Original paired-cube graph, decoder and matching lineage: icekylinx/eumemic. Independent reproduction and candidate research with OpenAI assistance. Original licenses and notices retained.