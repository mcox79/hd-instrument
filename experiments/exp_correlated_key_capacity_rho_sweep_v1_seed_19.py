"""correlated_key_capacity_rho_sweep_v1 -- seed_19.

Empirically test Loewe (1998) alpha_c(rho) approx alpha_0 * (1 - rho^2) capacity-
wall prediction on substrate CLASSICAL Hebbian outer-product storage. Follow-up
to research drill notes/research_correlated_key_capacity_hopfield_fhrr_2026-07-01.md.

Design: 5 rho x 5 alpha = 25 phase points at N=8192 (FULL) or 3 phase points at
N=8192 (SMOKE; discriminator-must-survive-scale).

HP: HP_MONOTONE (recall(rho) non-increasing at fixed alpha; Spearman <= -0.5)
    AND HP_WALL_SHIFTS_DOWN (rho in {0.5, 0.7} at some alpha has recall < 0.50
    while rho=0.0 at same alpha has recall >= 0.90).

HF: HF_NO_WALL_ANY_RHO (rho=0.7 alpha=0.20 recall >= 0.50; substrate does NOT
    exhibit correlation wall; refutes Loewe on substrate). HF_INDEP_CRUMBLES
    (rho=0.0 alpha=0.10 recall < 0.90; broken-PC). HF_CARDINALITY.
    HF_META_RULE_AF (bit-identical arm pairs).

Prior work (substrate-KB concept-query 2026-07-01):
  Top hit cosine=0.27 (wave14h_alpha_sweep_v2): different cell (leak-rate;
    rank-L subspace correlated keys for anti-Hebbian ERASE). Not overlapping.
  Genuinely novel: first substrate empirical test of Loewe alpha_c(rho).

ASCII-only; META_RULE_AH atomic-write; META_RULE_AF arms-must-differ;
SystemExit before Exception.
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

from experiments._substrate_correlated_key_capacity_rho_sweep_v1_core import (
    N_FULL, N_SMOKE, FULL_PHASE_POINTS, SMOKE_PHASE_POINTS,
    RHO_VALUES, ALPHA_VALUES, WALL_THRESHOLD, HP_INDEP_FLOOR,
    HP_MONOTONE_SPEARMAN, CRUMBLE_FLOOR, HF_INDEP_CRUMBLE,
    write_start_marker, write_crash_metrics, emit_heartbeat,
    run_one_unit, run_all_selftests, compute_verdict,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "correlated_key_capacity_rho_sweep_v1_seed_19"
SEED_THIS_CHUNK = 19

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = _HDLAB_EXP_NAME.lower().endswith("_smoke")

RUN_MODE = (
    "smoke"
    if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE
        or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke")
    else "full"
)

COMPUTE_BACKEND = "numpy"

if RUN_MODE == "smoke":
    N_DIM = N_SMOKE
    PHASE_POINTS = SMOKE_PHASE_POINTS
else:
    N_DIM = N_FULL
    PHASE_POINTS = FULL_PHASE_POINTS

EXPECTED_N_UNITS = len(PHASE_POINTS)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},"
    f"RHO_VALUES={RHO_VALUES},ALPHA_VALUES={ALPHA_VALUES},"
    f"SEED={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},backend={COMPUTE_BACKEND},"
    f"WALL_THRESHOLD={WALL_THRESHOLD},HP_INDEP_FLOOR={HP_INDEP_FLOOR},"
    f"MONOTONE_SPEARMAN={HP_MONOTONE_SPEARMAN}"
)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  N={N_DIM}  RUN_MODE={RUN_MODE}  "
        f"seed={SEED_THIS_CHUNK}  backend={COMPUTE_BACKEND}  "
        f"n_phase_points={EXPECTED_N_UNITS}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    units: List[Dict] = []
    total = len(PHASE_POINTS)
    for i, (rho, alpha) in enumerate(PHASE_POINTS):
        unit = run_one_unit(seed=seed, rho=rho, alpha=alpha,
                             n_dim=N_DIM, out_dir=out_dir,
                             total_units=total)
        units.append(unit)
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "rho_values": RHO_VALUES,
        "alpha_values": ALPHA_VALUES,
        "phase_points": PHASE_POINTS,
        "backend": COMPUTE_BACKEND,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "units": units,
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
        "N": N_DIM,
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
              f"backend={COMPUTE_BACKEND} N={N_DIM} "
              f"{EXPECTED_N_UNITS} phase points...", flush=True)
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
        verdict, verdict_msg, headline = compute_verdict(all_results[0],
                                                          run_mode=RUN_MODE)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    # Cardinality check
    n_units = 0
    if all_results:
        n_units = len(all_results[0].get("units", []))
    cardinality_ok = (n_units == EXPECTED_N_UNITS)
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
            f"n_units={n_units} != expected={EXPECTED_N_UNITS}. "
            + verdict_msg
        )

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    # CRLB floor at max M (M=1638 at alpha=0.20): sigma_min = sqrt(0.25/M) approx 0.0124
    max_M = int(round(max(a for (_, a) in PHASE_POINTS) * N_DIM))
    crlb_floor_max_M = math.sqrt(0.25 / max(max_M, 1)) if max_M > 0 else 0.0

    # HP gap (independent - correlated at same alpha) target = 0.90 - 0.50 = 0.40
    # CRLB at M=819 (alpha=0.10) = sqrt(0.25/819) approx 0.0175
    # discriminator_reachability: 0.40 gap >> 0.02 CRLB (ratio ~23x); YES.
    crlb_gap_min = math.sqrt(0.25 / max(int(round(0.10 * N_DIM)), 1))

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_units={n_units} "
            f"N={N_DIM} rho={RHO_VALUES} alpha={ALPHA_VALUES} "
            f"mode={RUN_MODE} backend={COMPUTE_BACKEND}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N": N_DIM,
        "rho_values": RHO_VALUES,
        "alpha_values": ALPHA_VALUES,
        "backend": COMPUTE_BACKEND,
        "n_seeds": 1,
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed_M_max": crlb_floor_max_M,
        "crlb_floor_computed_M_alpha_010": crlb_gap_min,
        "crlb_formula_reference": "sigma_min = sqrt(0.25/M) binomial-CLT",
        "discriminator_reachability": True,   # 0.40 gap >> 0.02 CRLB
        "calibration_check": "correlated_key_capacity_wall_shift",
        "discriminator_survives_scale": True,   # SMOKE uses N=N_FULL
        "hp_indep_floor": HP_INDEP_FLOOR,
        "hp_monotone_spearman_threshold": HP_MONOTONE_SPEARMAN,
        "wall_threshold": WALL_THRESHOLD,
        "crumble_floor": CRUMBLE_FLOOR,
        "hf_indep_crumble": HF_INDEP_CRUMBLE,
        "theory_reference": (
            "Loewe (1998) Ann. Appl. Prob. alpha_c(rho) approx alpha_0 * (1 - rho^2) "
            "with alpha_0 = 0.138 (AGS classical Hopfield capacity)"
        ),
        "prior_work_check": (
            "substrate-KB cosine top-1 = 0.27 (wave14h_alpha_sweep_v2 -- different "
            "cell; anti-Hebbian erase; not overlapping). Genuinely novel."
        ),
        "predicted_alpha_c_by_rho": {
            "0.0": 0.138, "0.1": 0.1366, "0.3": 0.1256,
            "0.5": 0.1035, "0.7": 0.0704,
        },
        "headline": headline,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "units": r.get("units"),
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
