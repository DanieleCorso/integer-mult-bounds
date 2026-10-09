# Prefix/suffix module experiment on PR168 (NOT a new exponent)

This branch starts at `fd25adb7fbaa12ee761d02c733c54d1d2a7687ee`, the current PR168 head.

The replacement nine-input all-but-one module has 21 additions instead of the pinned annealed module's 29. Its additions use disjoint source supports; each root equals the sum of all inputs except its indexed input. On construction there are 110 invocations (two modes for each of 55 coordinate pairs), suggesting up to 880 fewer scalar additions before global deduplication. This is a **local arithmetic result only**, not a certified saving or new multiplication bound.

The full signed graph changes, invalidating the old pinned graph SHA, matching arcs, physical frame witness, sink set and source manifests. The experiment deliberately constructs a fresh open maximum matching, selects gauges and builds physical frames / compensated readouts. It asks the **original** physical checker to replay the resulting word with dirty scratch. An independent comparison of decoder identity, full network assembly and other inherited all-size interfaces is still needed.

Reproduction (Python 3.11+, numpy, scipy):
```sh
python3 -B research/kappa700-prefix/experiment.py
```

The credited open compiler and physical optimizer were copied from GamingPuzzled/CrocSwap PR #167 (`research/paired-cube-open-search/frames_open.py` and `generator.py`), which in turn retains the work of icekylinx and eumemic (Apache-2.0 notices included). The base physical verifier and all original notices remain unchanged. The alternative module and integration are new experimental contributions made with OpenAI assistance.

No certified increase beyond PR168's conditional κ=0.000648912 is claimed. In particular do **not** promote a float discovery score to κ without strict exact moments, bit supplier, all 47 assembly inequalities, seven margins, decoder identity, full chronological and reflected physical replay, and inherited proof obligations.
