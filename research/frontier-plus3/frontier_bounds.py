#!/usr/bin/env python3
"""Exact PR129 +3% frontier bound; necessary condition, not a new witness."""
import json
from fractions import Fraction as Q
from pathlib import Path

HERE = Path(__file__).resolve().parent
baseline = Q(64593102899, 500000000000000)
complex_saving = Q(130696544, 10**12)
bit_coarse = Q(129310447, 10**12)
old_ordinary = Q(384599, 10**10)
theta = Q(1, 1000)
bit_stopped = (1 - theta)*bit_coarse + theta*old_ordinary
target = Q(103, 100)*baseline
assert bit_stopped == Q(129219596453, 10**15)
assert 0 < old_ordinary < bit_stopped < bit_coarse < complex_saving
assert baseline < bit_stopped < target
assert target - baseline == baseline*Q(3, 100)

# For the retained assembly: q = a(1-2eta), with eta>0.
# kappa < q < a <= min(stopped_bit, (1-beta)*complex_saving-buffer).
# Hence the current bit supplier alone gives an absolute obstruction.
required_stopped_bit_increase = (target/bit_stopped-1)*100
required_coarse_if_theta_fixed = (target-theta*old_ordinary)/(1-theta)
required_coarse_improvement = (required_coarse_if_theta_fixed/bit_coarse-1)*100
assert required_stopped_bit_increase > 0
assert required_coarse_if_theta_fixed > bit_coarse
assert required_coarse_improvement > 0

def string(x):
    return str(x.numerator)+"/"+str(x.denominator)
def decimal(x):
    return format(float(x), ".17g")

out = {
    "scope": "Exact necessary arithmetic condition only; no new kappa certified",
    "pinned_source": "eumemic/integer-mult-bounds PR129 992a442c10d243eee69bbd20f32ba6fa98fb430e",
    "baseline_kappa": string(baseline),
    "baseline_decimal": decimal(baseline),
    "target_3pct": string(target),
    "target_decimal": decimal(target),
    "complex_saving": string(complex_saving),
    "coarse_bit": string(bit_coarse),
    "ordinary_bit_stopped": string(bit_stopped),
    "stopped_bit_decimal": decimal(bit_stopped),
    "minimum_stopped_bit_increase_pct": decimal(required_stopped_bit_increase),
    "minimum_coarse_bit_at_fixed_theta": string(required_coarse_if_theta_fixed),
    "minimum_coarse_bit_increase_pct": decimal(required_coarse_improvement),
    "limiting_factor": "Current stopped bit supplier strictly below +3% target",
    "complex_only_optimization_can_reach_target": False,
}
print(json.dumps(out,indent=2))
