#!/usr/bin/env python3
"""Experimental legal all-but-one module replacement on PR168. NO new kappa claim."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(HERE))
from paired_cube.graph import Graph
from paired_cube.modules import triple_module_from, pair_module_from, all_but_one_from, merge_outputs
from paired_cube.gauges import select
import frames_open
import generator

SRC = ROOT / "references/paired-cube/sources"

def main():
    # Replacing any query module invalidates frozen graph pins and carrier arcs.
    # Therefore compute a fresh matching and gauge word: do NOT reuse the old certificate.
    gmaker = Graph(11, local=json.loads((SRC / "local_L1.json").read_text()))
    g = gmaker.finish(
        triple_module_from(SRC / "tmod_TB31_L1f8_5.9717259e-4.json", 11),
        pair_module_from(SRC / "pmod_H56snap_w02_5.6251423e-4.json", 10),
        all_but_one_from(HERE / "qmod_prefix_suffix_n9.json", 9))
    g = merge_outputs(g, gmaker, "f8:00111100")
    g["matching_frames"] = "coordinate"
    baseline, witness = frames_open.compile_graph(g, None)
    record, word = select(g, baseline, witness)
    for k in ("numerical_complex_root", "status", "gauge_selection", "gauge_cost_rejections", "gauge_trial_saving"):
        record.pop(k, None)
    print("NEW CARRIER MATCHING", record["R"], record["matched"], flush=True)
    saving, checked = generator.optimize(g, witness, word, record, passes=4, replay=True, log=lambda *a:print(*a,flush=True))
    print(json.dumps(dict(status="physical-experiment-not-end-to-end-certificate",
        complex_float_root=saving, R=record["R"], W=checked["W_per_vertex"],
        pairs=checked["pairs"], deficit=checked["deficit_per_vertex"],
        checks=checked["checks"]), indent=2))
    # No numerical kappa declared until a complete bit/complex/assembly recomputation
    # and inherited proof interfaces are audited.

if __name__ == "__main__":
    main()
