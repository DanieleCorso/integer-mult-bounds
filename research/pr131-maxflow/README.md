# Maximum-cardinality frame-compatible reuse on PR #131

Baseline: PR #131, conditional κ = 0.000332205398986.
The +3% target against this baseline is κ >= 0.00034217156095558.

This research tests whether PR131's deterministic greedy birth-cut reuse
selection (2,108 physical role aliases) loses cardinality relative to a
maximum-capacity bipartite flow on exact binary frame inclusions.

The graph has one supply node per donor frame and one demand node per
eligible birth frame, capacity equal to multiplicity, and an edge only if
the donor frame is contained in the destination initial frame. The
whole finite edge set, not just local greedy preference, is optimized.

`research/pr131-maxflow/maxflow_reuse.py` is an optional import, **not
part of the pinned PR131 proof source closure**. Its `compare(data)`
function takes the actual local compiler context before aliasing. It uses
the original PR131 `reuse.check_pairs` to validate every proposed pair.

A larger matching is NOT automatically a better conditional κ: the
physical word must replay with arbitrary dirty scratch, compensation,
chronological inverse, reflection and correctly priced source exteriors.
The exact complex and bit recurrence, scalar bounds, 47 strict
constraints and seven margins must then be regenerated. Until that happens,
**no improved κ is claimed and the inherited PR131 certificate is untouched**.

The maxflow algorithm's elementary matching implementation should also be
unit tested against brute force on small graphs before activation.

Credit: PR131 eumemic, PR130 icekylinx, PR124 jamesyc, and inherited
contributors. Research implementation prepared with OpenAI assistance.
