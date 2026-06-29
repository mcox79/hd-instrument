"""Post-hoc pooled aggregator for substrate_task_vector_K_cliff_phase_diagram_v3.

Reads per-sibling partial_metrics_<seed>.json from the 3 v3 sibling output
directories, POOLS the per-query correctness vectors across all 3 seeds,
runs the bootstrap-CI cliff analysis, and writes a single pooled metrics.json
to data/exp_substrate_task_vector_K_cliff_phase_diagram_v3_POOLED/.

Usage:
    python tools/aggregate_task_vector_K_cliff_v3_pooled.py

The 3 sibling anchors (FULL run):
    substrate_task_vector_K_cliff_phase_diagram_v3_seed_7_FULL
    substrate_task_vector_K_cliff_phase_diagram_v3_seed_13_FULL
    substrate_task_vector_K_cliff_phase_diagram_v3_seed_19_FULL

ASCII-only.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._substrate_task_vector_K_cliff_phase_diagram_v3_core import (
    aggregate_and_verdict,
)


SEEDS = (7, 13, 19)
SIBLING_ANCHORS = tuple(
    f"substrate_task_vector_K_cliff_phase_diagram_v3_seed_{s}_FULL"
    for s in SEEDS
)
POOLED_OUT_DIR = REPO / "data" / "exp_substrate_task_vector_K_cliff_phase_diagram_v3_POOLED"


def main() -> int:
    per_seed: Dict[str, Dict[str, Any]] = {}
    missing = []
    for s, anchor in zip(SEEDS, SIBLING_ANCHORS):
        partial = REPO / "data" / ("exp_" + anchor) / f"partial_metrics_{s}.json"
        if not partial.exists():
            missing.append((s, str(partial)))
            continue
        body = json.loads(partial.read_text(encoding="utf-8"))
        per_seed[str(s)] = body

    if missing:
        print(f"MISSING {len(missing)}/3 sibling partials:", file=sys.stderr)
        for s, p in missing:
            print(f"  seed={s}: {p}", file=sys.stderr)
        return 2

    print(f"Loaded {len(per_seed)} sibling partials.", flush=True)

    # Sanity check: every per_seed body must have per_query correctness vectors
    for sid, body in per_seed.items():
        for pt in body.get("phase_map", []):
            for arm_field in (
                "TASK_VECTOR_per_query_correct",
                "RANDOM_VECTOR_per_query_correct",
                "ORACLE_per_query_correct",
            ):
                if arm_field not in pt:
                    print(f"seed={sid} (K={pt.get('K')}, V={pt.get('V_tasks')}, "
                          f"ov={pt.get('overlap')}): missing {arm_field}", file=sys.stderr)
                    return 3

    t0 = time.time()
    pooled = aggregate_and_verdict(per_seed, run_mode="full", do_bootstrap=True)
    elapsed = time.time() - t0

    pooled["anchor_name"] = "substrate_task_vector_K_cliff_phase_diagram_v3_POOLED"
    pooled["pooled_from_seeds"] = list(SEEDS)
    pooled["pooled_from_anchors"] = list(SIBLING_ANCHORS)
    pooled["aggregation_elapsed_s"] = round(elapsed, 2)
    pooled["aggregation_ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    pooled["run_mode"] = "full"

    POOLED_OUT_DIR.mkdir(parents=True, exist_ok=True)
    (POOLED_OUT_DIR / "metrics.json").write_text(
        json.dumps(pooled, indent=2, default=str), encoding="utf-8")
    print(f"POOLED metrics written to {POOLED_OUT_DIR/'metrics.json'}", flush=True)
    print(f"verdict: {pooled.get('verdict')}", flush=True)
    print(f"verdict_msg: {pooled.get('verdict_msg')}", flush=True)
    b = pooled.get("bootstrap_ci", {})
    print(f"bootstrap: top_slice={b.get('top_slice')} "
          f"freq={b.get('top_slice_freq', 0.0):.3f} "
          f"K_cliff_min CI=[{b.get('K_cliff_min_ci_lo')}-{b.get('K_cliff_min_ci_hi')}] "
          f"width_steps={b.get('K_cliff_min_ci_width_steps')}", flush=True)
    print(f"chain_grade_eligible: {pooled.get('chain_grade_eligible')}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
