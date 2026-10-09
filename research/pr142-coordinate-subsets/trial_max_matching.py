#!/usr/bin/env python3
"""Opt-in FULL h22 PR142 physical compiler with maximum birth-cut matching.

Requires the inherited complete PR142 source package. In a disposable
checkout only: regenerates complex-profile.json and reuse-pairs.json.
It does NOT update the frozen pinned PR142 certificate or claim new kappa.
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

# Original producer / finite arithmetic and local reflection dependencies
# are left byte-identical. Only the donor-choice algorithm changes.
runpy.run_path(str(LOCAL/"complex_deferred.py"),run_name="__main__")
profile=json.loads((LOCAL/"complex-profile.json").read_text())
print("MAX-FLOW COMPLETE PHYSICAL COMPILER TRIAL",json.dumps({
    "role_stock":profile["R"],
    "logical_roles":profile["virtual_R"],
    "reuses":profile["reused_roles"],
    "profile_rank_mass":profile["total_rank"],
    "deficit":profile["deficit"],
    "scratch_replay":profile["replay"],
    "claim":"NO new kappa until independent literal reflection and paid cover are regenerated"
},sort_keys=True))
assert profile["replay"]["scratch_restored"] is True
assert profile["replay"]["y_plus_x"] is True
assert profile["reused_roles"]>=1703
