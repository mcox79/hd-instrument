"""metric_dependence_top_k_semantic_v1 -- seed_7 (Dim S from hidden-dim
research 2026-07-01; P_deflated=0.45).

Dense-Hopfield READ-REPLACE substrate (Cell D v2 primitive) at N=8192,
sweep M/N load in {0.10, 0.15, 0.20, 0.25, 0.30}, measure ALL 6 metrics
simultaneously per query:
  top1 / top5 / top10 / top50 / cos>=0.5 / cos>=0.8.

FALSIFIABLE:
  HP_TOP1_WALL:       top1 recall >= 0.80 at alpha=0.15 (reproduces prior CG).
  HP_TOPK_HIGHER:     top10 - top1 >= 0.15 at alpha=0.20.
  HP_SEMANTIC_HIGHER: cos05 - top1 >= 0.20 at alpha=0.20.
  HF_METRICS_IDENTICAL: max metric spread < 0.05 at any load.
  HF_TOPK_CATASTROPHIC: top1<0.30 AND top50<0.60 at alpha=0.30.

Smoke: loads {0.10, 0.20, 0.30} at full N=8192 (discriminator survives scale)
plus explicit preview arm at alpha=0.30 confirming saturation regime.

CARDINALITY (META_RULE_H): FULL = 5 loads per seed; SMOKE = 3 loads.

PRESERVE_ENV_VARS: HDLAB_QUEUE
"""
from __future__ import annotations
import sys
import argparse
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._substrate_metric_dependence_top_k_semantic_v1_core import (
    N_HIPPO_FULL, N_CORTEX_FULL, HIPPO_SPARSITY, ETA_HIPPO_FULL,
    BETA_MIN, BETA_MAX, N_QUERY,
    LOAD_SWEEP_FULL, LOAD_SWEEP_SMOKE, LOAD_SWEEP_PREVIEW_ALPHA,
    METRIC_NAMES,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_one_load, run_all_selftests, compute_verdict,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "metric_dependence_top_k_semantic_v1_seed_19"
SEED_THIS_CHUNK = 19

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


# ---------------------------------------------------------------------------
# Per-mode config
# ---------------------------------------------------------------------------
if RUN_MODE == "smoke":
    # Full N (discriminator survives scale); reduced load-sweep resolution.
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    LOAD_LIST = list(LOAD_SWEEP_SMOKE)
    RUN_PREVIEW = True
    PREVIEW_ALPHA = LOAD_SWEEP_PREVIEW_ALPHA  # alpha=0.30 heaviest
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    LOAD_LIST = list(LOAD_SWEEP_FULL)
    RUN_PREVIEW = False
    PREVIEW_ALPHA = None

HIPPO_SPARSITY_USED = HIPPO_SPARSITY
ETA_HIPPO = ETA_HIPPO_FULL

# CARDINALITY (META_RULE_H): 1 arm x N loads = N units in this cell
EXPECTED_N_UNITS = len(LOAD_LIST)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY_USED},LOAD_LIST={LOAD_LIST},"
    f"beta_range=[{BETA_MIN},{BETA_MAX}],N_QUERY={N_QUERY},"
    f"SEED={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},backend=numpy,"
    f"hardening=v1_METRIC_AXIS+METARULE_AH+SelfTests"
)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  N_h={N_HIPPO}  N_c={N_CORTEX}  "
        f"sparsity={HIPPO_SPARSITY_USED}  LOAD_LIST={LOAD_LIST}  "
        f"beta_range=[{BETA_MIN},{BETA_MAX}]  N_QUERY={N_QUERY}  "
        f"mode={RUN_MODE}  seed={SEED_THIS_CHUNK}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    per_load: Dict[int, Dict] = {}

    for uidx, alpha_load in enumerate(LOAD_LIST):
        print(f"  [seed={seed} alpha={alpha_load:.2f}] M/N={alpha_load} "
              f"M={int(round(alpha_load * N_CORTEX))} N_c={N_CORTEX}...",
              flush=True)
        row = run_one_load(
            seed=seed, alpha_load=alpha_load,
            n_h=N_HIPPO, n_c=N_CORTEX, hippo_sparsity=HIPPO_SPARSITY_USED,
            n_query=N_QUERY, out_dir=out_dir, unit_idx=uidx * 2,
        )
        per_load[int(round(alpha_load * 10000))] = row
        m = row.get("metrics", {})
        print(f"  [seed={seed} alpha={alpha_load:.2f}] "
              f"top1={m.get('top1_recall', float('nan')):.3f} "
              f"top5={m.get('top5_recall', float('nan')):.3f} "
              f"top10={m.get('top10_recall', float('nan')):.3f} "
              f"top50={m.get('top50_recall', float('nan')):.3f} "
              f"cos05={m.get('cos05_recall', float('nan')):.3f} "
              f"cos08={m.get('cos08_recall', float('nan')):.3f} "
              f"beta={row.get('beta_used', float('nan'))} "
              f"status={row.get('arm_status', '?')} "
              f"wall={row.get('wall_s', 0.0):.1f}s",
              flush=True)

    preview = None
    if RUN_MODE == "smoke" and RUN_PREVIEW and PREVIEW_ALPHA is not None:
        print(f"  [seed={seed} PREVIEW alpha={PREVIEW_ALPHA:.2f}] "
              f"discriminator-survives-scale confirmation run...", flush=True)
        preview = run_one_load(
            seed=seed, alpha_load=float(PREVIEW_ALPHA),
            n_h=N_HIPPO_FULL, n_c=N_CORTEX_FULL,
            hippo_sparsity=HIPPO_SPARSITY_USED,
            n_query=N_QUERY, out_dir=out_dir, unit_idx=999,
        )
        m = preview.get("metrics", {})
        print(f"  [seed={seed} PREVIEW alpha={PREVIEW_ALPHA:.2f}] "
              f"top1={m.get('top1_recall', float('nan')):.3f} "
              f"top10={m.get('top10_recall', float('nan')):.3f} "
              f"cos05={m.get('cos05_recall', float('nan')):.3f} "
              f"wall={preview.get('wall_s', 0.0):.1f}s", flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "LOAD_LIST": LOAD_LIST,
        "hippo_sparsity": HIPPO_SPARSITY_USED,
        "beta_range": [BETA_MIN, BETA_MAX],
        "n_query": N_QUERY,
        "backend": "numpy",
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "per_load": per_load,
        "preview_arm": preview,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "N": N_CORTEX,
        "LOAD_LIST": LOAD_LIST,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    seeds_list = [SEED_THIS_CHUNK]
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(seeds_list)} done; running {remaining}",
          flush=True)

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME} mode={RUN_MODE} "
              f"LOAD_LIST={LOAD_LIST}...", flush=True)
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n"
                f"{traceback.format_exc()}", encoding="utf-8",
            )
            raise
        write_partial(out_dir, seed, result)

    per_seed_agg = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    all_results = list(per_seed_agg.values())

    if not all_results:
        verdict = "HARD_FAIL"
        verdict_msg = "No seed results aggregated."
        headline = {}
    else:
        verdict, verdict_msg, headline = compute_verdict(all_results[0], RUN_MODE)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    # Cardinality check
    n_load_outcomes = 0
    if all_results:
        n_load_outcomes = len(all_results[0].get("per_load", {}))
    cardinality_ok = (n_load_outcomes == EXPECTED_N_UNITS)

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_h={N_HIPPO} N_c={N_CORTEX} sparsity={HIPPO_SPARSITY_USED} "
            f"LOAD_LIST={LOAD_LIST} N_QUERY={N_QUERY} mode={RUN_MODE}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "LOAD_LIST": LOAD_LIST,
        "hippo_sparsity": HIPPO_SPARSITY_USED,
        "beta_floor": BETA_MIN,
        "beta_ceil": BETA_MAX,
        "n_query": N_QUERY,
        "metric_names": list(METRIC_NAMES),
        "backend": "numpy",
        "n_seeds": 1,
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,        # META_RULE_AF; single arm; 6-metric family verified per selftest_metrics_family_arms_differ
        "arms_differ_exempted": [["single_arm_dense_hopfield_read_replace",
                                  "metric_axis_is_free_measurement_not_arm_axis"]],
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed_alpha_0.30_M2458": 0.01009,  # sqrt(0.25/2458)
        "crlb_formula_reference": "sigma_min = sqrt(0.25/M) binomial-CLT",
        "discriminator_reachability": True,   # HP gaps 0.15 / 0.20 >> sigma
        "calibration_check": "default_ok_for_this_regime",
        "P_deflated_prereg": 0.45,
        "hidden_dim_reference": "notes/research_hidden_phase_diagram_dimensions_2026-07-01.md (Dim S)",
        "prior_related_anchors": [
            "g6_semantic_similar_fabrication_khop_v1",     # fixed-cosine adversarial (not sweep)
            "gap4v2_semantic_A_eval_gpu_v1",               # BGE-encoder recall (not metric-axis sweep)
        ],
        "headline": headline,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "per_load": r.get("per_load"),
                "preview_arm": r.get("preview_arm"),
            }
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print(f"[metrics] written to {metrics_path}", flush=True)


def main():
    _main()


if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _exc:
        write_crash_metrics(_out_dir_for_crash, ANCHOR_NAME, _exc)
        raise
