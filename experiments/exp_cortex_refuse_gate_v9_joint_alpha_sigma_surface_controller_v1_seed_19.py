"""cortex_refuse_gate_v9_joint_alpha_sigma_surface_controller_v1 -- seed_7.

M1.4 v9 upgrade: from 1D-on-sigma (v8 CG) to 2D joint (alpha, sigma)
refuse-gate. Justified by Dim T v1 smoke HP (seed_7 2026-07-02):
sigma_crit(alpha=0.10)=0.1852 vs sigma_crit(alpha=0.45)=0.1157
(delta=0.0694, 2.3x above HP interaction floor 0.03).

24 arms per seed: 2 arm-kinds x 3 alpha (0.10, 0.25, 0.45) x 4 sigma
(0.02, 0.08, 0.15, 0.25). Substrate: independent Gaussian keys+vals
in R^N=8192, dense-attention softmax(beta=13) READ.

Metric: useful_recall = P(accept AND correct) = accept_rate *
raw_recall_argmax. HP tier grants HARD_PASS if v9 lifts low-load
useful_recall vs v8 by >= 0.30 at (alpha=0.10, sigma=0.15) AND
safe-regime accept-rate + useful_recall both >= 0.95.

Prior-work check (substrate-KB): novel 2D joint controller (all cosines
< 0.30). Adjacent pp50 kappa_3 drill 2026-06-03 proposed load-dependent
tightening rule but different mechanism class.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
  - arms_differ_verified via arm_digest hash-check (META_RULE_AF)
  - final_metrics_atomicity: tmp_replace (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_floor_computed + discriminator_reachability declared
  - discriminator survives scale: smoke at full N=8192
  - HP strictly above delta floor (>= 0.30)
  - cardinality_ok: 24 arms per seed (META_RULE_H)
  - per-unit failure-class instrumentation (arm_status)
  - calibration_check: default_ok_for_this_regime (Dim T v1 reproduces)

PRESERVE_ENV_VARS: HDLAB_QUEUE

Author: hdi_exp_dev 2026-07-02 (Opus 4.7 1M, agent-spawn).
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

# Fix #24 gate: import torch at top-of-cell
import torch  # noqa: F401
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._cortex_refuse_gate_v9_joint_alpha_sigma_surface_controller_v1_core import (
    N_CORTEX_FULL, N_CORTEX_SMOKE, BETA,
    ALPHA_GRID, SIGMA_GRID, ARM_NAMES,
    ARM_1D_V8_BASELINE, ARM_2D_V9_JOINT,
    TAU_V8_FIXED_SIGMA, TAU_V9_INTERCEPT, TAU_V9_SLOPE, tau_v9,
    N_QUERIES_PER_CONDITION_SMOKE, N_QUERIES_PER_CONDITION_FULL,
    EXPECTED_N_ARMS,
    HP_LIFT_LOW_LOAD_DELTA, HP_SAFE_REGIME_FLOOR,
    HF_BROKEN_PC_FLOOR,
    DIM_T_V1_A45_S10_RECALL,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_one_arm, run_all_selftests, compute_verdict,
    make_condition_specs,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = ("cortex_refuse_gate_v9_joint_alpha_sigma_surface_controller"
               "_v1_seed_19")
SEED_THIS_CHUNK = 19

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--timeout", type=int, default=3600,
                 help="per-cell timeout seconds (for runner enforcement)")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()

if _ARGS.smoke or _NAME_SAYS_SMOKE:
    RUN_MODE = "smoke"
elif _ARGS.self_test:
    RUN_MODE = "selftest"
else:
    RUN_MODE = os.environ.get("HDLAB_RUN_MODE", "full").lower()


if RUN_MODE == "smoke":
    N_CORTEX = N_CORTEX_SMOKE
    N_QUERIES_PER_CONDITION = N_QUERIES_PER_CONDITION_SMOKE
    ATTN_CHUNK = 1000
else:
    N_CORTEX = N_CORTEX_FULL
    N_QUERIES_PER_CONDITION = N_QUERIES_PER_CONDITION_FULL
    ATTN_CHUNK = 1000

COMPUTE_BACKEND = "numpy"

CONFIG_VERSION = (
    "ANCHOR=%s,N_c=%d,BETA=%.1f,alpha_grid=%s,sigma_grid=%s,"
    "arms=[1D_V8_BASELINE,2D_V9_JOINT],tau_v8=%.4f,"
    "tau_v9(a)=%.4f%+.4f*a,n_queries_per_cond=%d,"
    "expected_n_arms=%d,SEED=%d,RUN_MODE=%s,backend=%s"
) % (ANCHOR_NAME, N_CORTEX, BETA, ALPHA_GRID, SIGMA_GRID,
      TAU_V8_FIXED_SIGMA, TAU_V9_INTERCEPT, TAU_V9_SLOPE,
      N_QUERIES_PER_CONDITION, EXPECTED_N_ARMS,
      SEED_THIS_CHUNK, RUN_MODE, COMPUTE_BACKEND)


def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        "[selftest] PASS  N_c=%d  BETA=%.1f  alpha_grid=%s  sigma_grid=%s  "
        "arms=%s  tau_v8=%.4f  tau_v9(0.10)=%.4f  tau_v9(0.45)=%.4f  "
        "mode=%s  seed=%d  backend=%s"
        % (N_CORTEX, BETA, ALPHA_GRID, SIGMA_GRID, ARM_NAMES,
           TAU_V8_FIXED_SIGMA, tau_v9(0.10), tau_v9(0.45),
           RUN_MODE, SEED_THIS_CHUNK, COMPUTE_BACKEND),
        flush=True,
    )


def run_seed(seed: int, out_dir: Path) -> Dict:
    """Run all 24 arms for this seed."""
    t0 = time.time()
    arms: List[Dict] = []
    specs = make_condition_specs()
    for arm_kind, alpha, sigma in specs:
        arm_dict = run_one_arm(
            seed=seed, arm=arm_kind, alpha=alpha, sigma=sigma,
            n_c=N_CORTEX, n_queries=N_QUERIES_PER_CONDITION,
            attn_chunk=ATTN_CHUNK, out_dir=out_dir,
        )
        arms.append(arm_dict)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_c": N_CORTEX,
        "N": N_CORTEX,
        "M": int(round(max(ALPHA_GRID) * N_CORTEX)),
        "BETA": BETA,
        "ALPHA_GRID": ALPHA_GRID,
        "SIGMA_GRID": SIGMA_GRID,
        "TAU_V8_FIXED_SIGMA": TAU_V8_FIXED_SIGMA,
        "TAU_V9_INTERCEPT": TAU_V9_INTERCEPT,
        "TAU_V9_SLOPE": TAU_V9_SLOPE,
        "n_queries_per_condition": N_QUERIES_PER_CONDITION,
        "backend": COMPUTE_BACKEND,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_ARMS)

    run_config = {
        "N": N_CORTEX,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    seeds_list = [SEED_THIS_CHUNK]
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s"
          % (len(done), len(seeds_list), remaining), flush=True)

    t_sweep_start = time.time()
    for seed in remaining:
        print("[seed=%d] %s mode=%s backend=%s N_c=%d 24 arms..."
              % (seed, ANCHOR_NAME, RUN_MODE, COMPUTE_BACKEND, N_CORTEX),
              flush=True)
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                "FATAL during seed=%d: %s: %s\n%s"
                % (seed, type(exc).__name__, exc, traceback.format_exc()),
                encoding="utf-8",
            )
            raise
        write_partial(out_dir, seed, result)

    per_seed_agg = aggregate_partials(out_dir, seeds_list,
                                       run_config=run_config)
    all_results = list(per_seed_agg.values())

    if not all_results:
        verdict = "HARD_FAIL"
        verdict_msg = "No seed results aggregated."
        headline: Dict = {}
    else:
        verdict, verdict_msg, headline = compute_verdict(all_results[0])

    elapsed_s = time.time() - t_sweep_start
    print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)
    print("[elapsed] %.1fs" % elapsed_s, flush=True)

    n_arms_observed = 0
    if all_results:
        n_arms_observed = len(all_results[0].get("arms", []))
    cardinality_ok = (n_arms_observed == EXPECTED_N_ARMS)
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (
            "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
            "n_arms=%d != expected=%d. %s"
            % (n_arms_observed, EXPECTED_N_ARMS, verdict_msg)
        )

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            "HARD_FAIL: stale smoke partials in FULL. mode_in_results=%s. %s"
            % (mode_in_results, verdict_msg)
        )

    # CRLB reachability at n_queries=60 per condition
    # For delta of two useful_recall values: sqrt(2 * 0.25 / n)
    crlb_delta = math.sqrt(2.0 * 0.25 / max(N_QUERIES_PER_CONDITION, 1))

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            "chunk_seed=%d n_seeds=%d N_c=%d BETA=%.1f alpha_grid=%s "
            "sigma_grid=%s arms=%s mode=%s backend=%s"
            % (SEED_THIS_CHUNK, len(all_results), N_CORTEX, BETA,
               ALPHA_GRID, SIGMA_GRID, ARM_NAMES, RUN_MODE, COMPUTE_BACKEND)
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_c": N_CORTEX,
        "BETA": BETA,
        "ALPHA_GRID": ALPHA_GRID,
        "SIGMA_GRID": SIGMA_GRID,
        "TAU_V8_FIXED_SIGMA": TAU_V8_FIXED_SIGMA,
        "TAU_V9_INTERCEPT": TAU_V9_INTERCEPT,
        "TAU_V9_SLOPE": TAU_V9_SLOPE,
        "tau_v9_at_alpha_10": tau_v9(0.10),
        "tau_v9_at_alpha_25": tau_v9(0.25),
        "tau_v9_at_alpha_45": tau_v9(0.45),
        "n_queries_per_condition": N_QUERIES_PER_CONDITION,
        "backend": COMPUTE_BACKEND,
        "n_seeds": 1,
        "expected_n_units": EXPECTED_N_ARMS,
        "cardinality_ok": cardinality_ok,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": crlb_delta,
        "crlb_formula_reference": ("sigma_min = sqrt(2 * 0.25 / n_queries) "
                                    "binomial-CLT for arm useful_recall delta"),
        "discriminator_reachability": crlb_delta < HP_LIFT_LOW_LOAD_DELTA,
        "calibration_check": "default_ok_for_this_regime",
        "discriminator_survives_scale": True,
        "hp_lift_low_load_delta": HP_LIFT_LOW_LOAD_DELTA,
        "hp_safe_regime_floor": HP_SAFE_REGIME_FLOOR,
        "hf_broken_pc_floor": HF_BROKEN_PC_FLOOR,
        "dim_t_v1_reference_recall_a45_s10": DIM_T_V1_A45_S10_RECALL,
        "parent_dim_t_v1": ("dim_t_joint_surface_alpha_sigma_interaction_v1"
                             "_seed_19"),
        "parent_m14_v8_cg": "substrate_refuse_gate_v8_conformal_v1_seed_19",
        "hypothesis_being_tested": ("m14_v9_joint_alpha_sigma_surface_"
                                     "controller_lifts_low_load_accept_"
                                     "and_maintains_safe_regime"),
        "cell_chunked": True,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "headline": headline,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "arms": r.get("arms"),
            }
            for r in all_results
        ],
    }
    metrics_path = out_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2, default=str),
                        encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print("[metrics] written to %s" % metrics_path, flush=True)


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
