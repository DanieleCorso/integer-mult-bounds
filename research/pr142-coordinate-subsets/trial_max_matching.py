#!/usr/bin/env python3
"""Opt-in FULL h22 PR142 physical compiler with maximum birth-cut matching.

Requires the complete pinned PR142 source package. Uses PR142's own
read-only reflection_audit.capture to obtain the compiled state before
writing output files, then executes the complete literal reflection
audit on that state. It does NOT modify any pinned certificate or claim kappa.
"""
import json
import runpy
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
LOCAL=ROOT/"research/cyclic-deferred"
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(LOCAL))
sys.path.insert(0,str(HERE))
from max_matching import select_maximum
import reuse

# IMPORTANT: max_matching captured the original greedy method before
# this patch. Every selected pair is independently run through the
# original PR142 reuse.check_pairs including exact binary subspace
# inclusion and all birth/last-use eligibility conditions.
original=reuse.select_reuse
assert original is not select_maximum
reuse.select_reuse=select_maximum

# The inherited PR142 literal auditor captures the original producer state
# read-only (AST before its output write), using the new maximum selector
# through Python's original import module. It then validates signed readouts,
# arbitrary dirty cancellation, exact reflected frame chronology and child
# histograms. No certificates on disk are modified.
from reflection_audit import capture, audit
d=capture(LOCAL/"complex_deferred.py")
candidate=d["out"]
receipt=audit(d)
original_profile=json.loads((LOCAL/"complex-profile.json").read_text())
assert original_profile["reused_roles"]==1703
assert candidate["reused_roles"]>=original_profile["reused_roles"]
assert candidate["replay"]["scratch_restored"] is True
assert candidate["replay"]["y_plus_x"] is True
assert receipt["reused_roles"]==candidate["reused_roles"]
assert receipt["reflected_residual_rank_histogram_equal"]
assert receipt["exact_arbitrary_dirty_cancellation_by_dependency_cut"]
assert receipt["bounded_chunk_coefficients"]
assert receipt["child_multiplicities"]==candidate["child_multiplicities"]

print("MAX-FLOW PR142 COMPLETE PHYSICAL AUDIT",json.dumps({
    "original_greedy_roles":original_profile["R"],
    "new_maxflow_roles":candidate["R"],
    "original_greedy_reuses":original_profile["reused_roles"],
    "maxflow_reuses":candidate["reused_roles"],
    "additional_legal_reuses":candidate["reused_roles"]-original_profile["reused_roles"],
    "source_gauge_types":len(candidate["physical_auxiliary_source_frames"]),
    "literal_scalar_operations_per_stage":receipt["expanded_scalar_operations_per_stage"],
    "reflection_audit":True,
    "new_kappa_certified":False
},sort_keys=True))
