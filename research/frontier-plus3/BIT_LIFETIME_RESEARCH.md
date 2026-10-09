# Birth-cut reuse screening on the PR129 bit supplier

This scan investigates whether the PR124-style compensated birth-cut
optimization used successfully on the **complex** side of PR129 has a
potential analogue in PR129's **bit** core.

The unchanged source is the pinned 23-coordinate stopped bit supplier and
its minimal-V word, included in the PR129 package. Run:

```bash
python3 research/frontier-plus3/bit_lifetime_scan.py
```

The script traces chronological source DAG operations, builds the dependency
closure of retained centres, enumerates roles dying inside that closure and
late deferred readouts born by an untouched fan, and greedily counts
time-ordered pairs satisfying only the **necessary dimension condition**.

It deliberately does **not** claim a legal alias or an improved exponent.
The PR129 bit word also includes physical V-gate schedules, specific rational
frames, scalar readouts, a reversed orientation, and arbitrary dirty
auxiliary inputs. Those must all be checked exactly with a modified
compiler/word if any candidate pair is ever used. Unlike the complex
producer, both tensor orientations must preserve the bit PR104 endpoint and
stopped-product contracts.

If there are q actual legal pairs, a first *allocation-only* book value is
W = 2v² + 2·161·(28866−q), but the recursive child histogram and moment
cannot be inferred from W alone. Frame and readout compensation charges
must be rebuilt. In particular, **dimension containment is not
vector-subspace containment**.

The target is κ ≥ 0.00013306179197194, at least 3% above PR129's conditional
κ=0.000129186205798, and its bit saving must improve accordingly.
No result should be called a new κ until every prior audit passes.

PR129 and its full source/licensing lineage remain the starting point.
This preliminary tool was written with OpenAI assistance.
