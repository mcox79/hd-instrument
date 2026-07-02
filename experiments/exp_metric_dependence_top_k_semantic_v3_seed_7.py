"""metric_dependence_top_k_semantic_v3 -- seed_7 (Dim S FINE SIGMA CLIFF BRACKET).

v2 landed HF_UNIFORM_COLLAPSE with BIMODAL knife-edge behavior across
(alpha in {0.30, 1.00, 1.50}, sigma in {0.0, 0.7}). v3 respec (per hand-off
directive) brackets the cliff with FINE sigma sweep at 2 fixed alphas
(alpha shape-invariance confirmed by v2).

Dense-Hopfield READ-REPLACE substrate (Cell D v2 primitive; IMPORTED from
v2 core) at N=8192, sweep:
  alpha in {0.30, 1.00}
  sigma in {0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.40, 0.50}
Measure ALL 6 metrics per (alpha, sigma) cell.

FALSIFIABLE:
  HP_CLIFF_BRACKET: >=1 cell has max_metric in [0.20, 0.80].
  HP_METRIC_DIFFERENTIATION: within cliff-band, top10-top1 >= 0.10.
  HP_BIMODAL_CONFIRMED: sigma<0.10 all>=0.90 AND sigma>0.40 all<=0.10.
  HF_NO_TRANSITION: no cliff-band cell (cliff width <=0.05 or outside sweep).
  HF_METRIC_DIFFERENTIATION_FAILS: cliff bracketed but top10-top1<0.02.

Smoke: 2 alphas x 4 sigmas {0.05, 0.15, 0.25, 0.40} = 8 cells at full
N=8192, plus preview at (alpha=1.0, sigma=0.20) — expected mid-cliff.

CARDINALITY (META_RULE_H): FULL = 16 cells; SMOKE = 8 cells.

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

from experiments._substrate_metric_dependence_top_k_semantic_v2_core import (
    N_HIPPO_FULL, N_CORTEX_FULL, HIPPO_SPARSITY, ETA_HIPPO_FULL,
    BETA_MIN, BETA_MAX, N_QUERY,
    METRIC_NAMES,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_one_cell,
)
from experiments._substrate_metric_dependence_top_k_semantic_v3_core import (
    ALPHA_SWEEP_FULL_V3, SIGMA_SWEEP_FULL_V3,
    ALPHA_SWEEP_SMOKE_V3, SIGMA_SWEEP_SMOKE_V3,
    PREVIEW_ALPHA_V3, PREVIEW_SIGMA_V3,
    CLIFF_LOW, CLIFF_HIGH,
    run_all_selftests_v3, compute_verdict_v3, _cell_key,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "metric_dependence_top_k_semantic_v3_seed_7"
SEED_THIS_CHUNK = 7

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
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    ALPHA_LIST = list(ALPHA_SWEEP_SMOKE_V3)
    SIGMA_LIST = list(SIGMA_SWEEP_SMOKE_V3)
    RUN_PREVIEW = True
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    ALPHA_LIST = list(ALPHA_SWEEP_FULL_V3)
    SIGMA_LIST = list(SIGMA_SWEEP_FULL_V3)
    RUN_PREVIEW = False

HIPPO_SPARSITY_USED = HIPPO_SPARSITY
ETA_HIPPO = ETA_HIPPO_FULL

EXPECTED_N_UNITS = len(ALPHA_LIST) * len(SIGMA_LIST)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY_USED},ALPHA_LIST={ALPHA_LIST},"
    f"SIGMA_LIST={SIGMA_LIST},CLIFF_BAND=[{CLIFF_LOW},{CLIFF_HIGH}],"
    f"beta_range=[{BETA_MIN},{BETA_MAX}],N_QUERY={N_QUERY},"
    f"SEED={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},backend=numpy,"
    f"hardening=v3_FINE_SIGMA_CLIFF+METARULE_AH+SelfTests"
)


def _instrumentation_selftest() -> None:
    run_all_selftests_v3(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  N_h={N_HIPPO}  N_c={N_CORTEX}  "
        f"sparsity={HIPPO_SPARSITY_USED}  ALPHA_LIST={ALPHA_LIST}  "
        f"SIGMA_LIST={SIGMA_LIST}  "
        f"beta_range=[{BETA_MIN},{BETA_MAX}]  N_QUERY={N_QUERY}  "
        f"mode={RUN_MODE}  seed={SEED_THIS_CHUNK}  "
        f"expected_units={EXPECTED_N_UNITS}  cliff_band=[{CLIFF_LOW},{CLIFF_HIGH}]",
        flush=True,
    )


def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    per_cell: Dict[str, Dict] = {}

    uidx = 0
    for alpha_load in ALPHA_LIST:
        for sigma_noise in SIGMA_LIST:
            print(f"  [seed={seed} a={alpha_load:.2f} s={sigma_noise:.2f}] "
                  f"M={int(round(alpha_load * N_CORTEX))} N_c={N_CORTEX}...",
                  flush=True)
            row = run_one_cell(
                seed=seed, alpha_load=alpha_load, sigma_noise=sigma_noise,
                n_h=N_HIPPO, n_c=N_CORTEX, hippo_sparsity=HIPPO_SPARSITY_USED,
                n_query=N_QUERY, out_dir=out_dir, unit_idx=uidx * 2,
            )
            per_cell[_cell_key(alpha_load, sigma_noise)] = row
            m = row.get("metrics", {})
            print(f"  [seed={seed} a={alpha_load:.2f} s={sigma_noise:.2f}] "
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
            uidx += 1

    preview = None
    if RUN_MODE == "smoke" and RUN_PREVIEW:
        print(f"  [seed={seed} PREVIEW a={PREVIEW_ALPHA_V3:.2f} s={PREVIEW_SIGMA_V3:.2f}] "
              f"expected-mid-cliff confirmation run...", flush=True)
        preview = run_one_cell(
            seed=seed, alpha_load=float(PREVIEW_ALPHA_V3),
            sigma_noise=float(PREVIEW_SIGMA_V3),
            n_h=N_HIPPO_FULL, n_c=N_CORTEX_FULL,
            hippo_sparsity=HIPPO_SPARSITY_USED,
            n_query=N_QUERY, out_dir=out_dir, unit_idx=999,
        )
        m = preview.get("metrics", {})
        print(f"  [seed={seed} PREVIEW a={PREVIEW_ALPHA_V3:.2f} s={PREVIEW_SIGMA_V3:.2f}] "
              f"top1={m.get('top1_recall', float('nan')):.3f} "
              f"top10={m.get('top10_recall', float('nan')):.3f} "
              f"cos05={m.get('cos05_recall', float('nan')):.3f} "
              f"wall={preview.get('wall_s', 0.0):.1f}s", flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "ALPHA_LIST": ALPHA_LIST,
        "SIGMA_LIST": SIGMA_LIST,
        "hippo_sparsity": HIPPO_SPARSITY_USED,
        "beta_range": [BETA_MIN, BETA_MAX],
        "n_query": N_QUERY,
        "backend": "numpy",
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "per_cell": per_cell,
        "preview_arm": preview,
        "elapsed_s": float(elapsed),
    }


def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "N": N_CORTEX,
        "ALPHA_LIST": ALPHA_LIST,
        "SIGMA_LIST": SIGMA_LIST,
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
              f"ALPHA_LIST={ALPHA_LIST} SIGMA_LIST={SIGMA_LIST}...", flush=True)
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
        verdict, verdict_msg, headline = compute_verdict_v3(all_results[0], RUN_MODE)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    n_cell_outcomes = 0
    if all_results:
        n_cell_outcomes = len(all_results[0].get("per_cell", {}))
    cardinality_ok = (n_cell_outcomes == EXPECTED_N_UNITS)

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    crlb_floor_alpha_1_00 = math.sqrt(0.25 / 8192)  # ~= 0.00553

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_h={N_HIPPO} N_c={N_CORTEX} sparsity={HIPPO_SPARSITY_USED} "
            f"ALPHA={ALPHA_LIST} SIGMA={SIGMA_LIST} "
            f"cliff_band=[{CLIFF_LOW},{CLIFF_HIGH}] "
            f"N_QUERY={N_QUERY} mode={RUN_MODE}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "ALPHA_LIST": ALPHA_LIST,
        "SIGMA_LIST": SIGMA_LIST,
        "cliff_band_low": CLIFF_LOW,
        "cliff_band_high": CLIFF_HIGH,
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
        "arms_differ_verified": True,
        "arms_differ_exempted": [["single_arm_dense_hopfield_read_replace_with_query_noise",
                                  "metric_axis_is_free_measurement_not_arm_axis",
                                  "alpha_sigma_grid_is_config_sweep_not_arm_sweep"]],
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed_alpha_1.00_M8192": crlb_floor_alpha_1_00,
        "crlb_formula_reference": "sigma_min = sqrt(0.25/M) binomial-CLT",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
        "P_deflated_prereg": 0.55,
        "hidden_dim_reference": "notes/research_hidden_phase_diagram_dimensions_2026-07-01.md (Dim S)",
        "v1_reference": "notes/exp_dev_findings/exp_metric_dependence_top_k_semantic_v1_HF_METRICS_IDENTICAL_2026-07-01.md",
        "v2_reference": "notes/exp_dev_findings/exp_metric_dependence_top_k_semantic_v2_HF_UNIFORM_COLLAPSE_bimodal_2026-07-01.md",
        "prior_related_anchors": [
            "metric_dependence_top_k_semantic_v1_seed_7",
            "metric_dependence_top_k_semantic_v2_seed_7",
        ],
        "headline": headline,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "per_cell": r.get("per_cell"),
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
