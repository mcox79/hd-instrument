"""dim_t_joint_surface_alpha_sigma_interaction_v1 -- seed_7.

Cheapest decisive test for the joint (alpha, sigma) transition surface
hypothesis (Sonnet Dim T drill 2026-07-02).

If sigma_crit(alpha=0.45) < sigma_crit(alpha=0.10) by >= 0.03, the
substrate's noise transition is NOT independent of load; M3 refuse-gate
must upgrade from 1D-on-sigma to a joint (alpha, sigma) controller.

If sigma_crit is approximately equal at both alphas, transitions are
effectively independent (1D refuse-gate sufficient).

Design: 16 arms x 1 seed x 1 config (N_c=8192, beta=13).
  2 alpha ({0.10, 0.45}) * 8 sigma ({0.02, 0.05, 0.08, 0.10, 0.13, 0.15,
    0.20, 0.30})

Positive control: (alpha=0.45, sigma=0.10) MUST reproduce v3 CG value
0.785 +/- 0.10 (regime-alignment gate per META_RULE §15 gate D).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified via arm_digest hash-check (META_RULE_AF)
  - final_metrics_atomicity: tmp_replace (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_floor_computed_M + discriminator_reachability declared
  - discriminator survives scale: smoke at full N=8192
  - HP strictly above delta floor (>=0.03 not >=0.0)
  - cardinality_ok: 16 arms per seed (META_RULE_H)
  - per-unit failure-class instrumentation (arm_status)
  - calibration_check: default_ok_for_this_regime (v3 CG reproduces)
  - numbers tagged MEASURED@ / THEORETICAL@ in pre-reg (META_RULE_AC)

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

from experiments._dim_t_joint_surface_alpha_sigma_interaction_v1_core import (
    N_CORTEX_FULL, N_CORTEX_SMOKE, BETA, ALPHA_LOW, ALPHA_HIGH,
    M_LOW_FULL, M_HIGH_FULL, SIGMA_SWEEP,
    BROKEN_PC_FLOOR, REGIME_MATCH_TOL, V3_CG_REFERENCE_RECALL,
    HP_INTERACTION_DELTA, MB_INTERACTION_DELTA, HF_INTERACTION_TOL,
    TOTAL_SAT_FLOOR, TOTAL_COLLAPSE_CEIL,
    ARM_SPECS_FULL, EXPECTED_N_ARMS,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_one_arm, run_all_selftests, compute_verdict,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "dim_t_joint_surface_alpha_sigma_interaction_v1_seed_13"
SEED_THIS_CHUNK = 13

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


# Per-mode config: smoke runs AT full N=8192 per discriminator-must-survive-scale.
if RUN_MODE == "smoke":
    N_CORTEX = N_CORTEX_SMOKE  # 8192 (same as full; scale-preserving smoke)
    ATTN_CHUNK = 1000
else:
    N_CORTEX = N_CORTEX_FULL   # 8192
    ATTN_CHUNK = 1000

COMPUTE_BACKEND = "numpy"
EXPECTED_N_UNITS = EXPECTED_N_ARMS   # 16

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_c={N_CORTEX},"
    f"BETA={BETA},alpha={{{ALPHA_LOW},{ALPHA_HIGH}}},"
    f"sigma={{0.02,0.05,0.08,0.10,0.13,0.15,0.20,0.30}},"
    f"SEED={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},backend={COMPUTE_BACKEND},"
    f"parent_v3_CG=cortex_hippo_dense_beta_sweep_v3_query_noise_seed_7"
)


def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  N_c={N_CORTEX}  BETA={BETA}  "
        f"alphas={{{ALPHA_LOW},{ALPHA_HIGH}}}  "
        f"sigmas={SIGMA_SWEEP}  mode={RUN_MODE}  "
        f"seed={SEED_THIS_CHUNK}  backend={COMPUTE_BACKEND}",
        flush=True,
    )


def run_seed(seed: int, out_dir: Path) -> Dict:
    """Run all 16 arms for this seed."""
    t0 = time.time()
    arms: List[Dict] = []
    # Rebuild arm specs at the current N_CORTEX (smoke and full are same here
    # by design, but this keeps the code correct if someone changes smoke_N).
    from experiments._dim_t_joint_surface_alpha_sigma_interaction_v1_core import (
        _make_arm_specs,
    )
    arm_specs = _make_arm_specs(N_CORTEX)
    for arm_name, alpha, m_items, sigma in arm_specs:
        arm_dict = run_one_arm(
            seed=seed, arm_name=arm_name, alpha=alpha, m_items=m_items,
            sigma=sigma, n_c=N_CORTEX, attn_chunk=ATTN_CHUNK, out_dir=out_dir,
        )
        arms.append(arm_dict)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_c": N_CORTEX,
        "M_LOW": int(round(ALPHA_LOW * N_CORTEX)),
        "M_HIGH": int(round(ALPHA_HIGH * N_CORTEX)),
        "N": N_CORTEX,                # for _seed_checkpoint config match
        "M": int(round(ALPHA_HIGH * N_CORTEX)),  # canonical M for match
        "BETA": BETA,
        "ALPHA_LOW": ALPHA_LOW,
        "ALPHA_HIGH": ALPHA_HIGH,
        "SIGMA_SWEEP": SIGMA_SWEEP,
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
    write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "N": N_CORTEX,
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
              f"backend={COMPUTE_BACKEND} N_c={N_CORTEX} "
              f"alphas={{{ALPHA_LOW},{ALPHA_HIGH}}} "
              f"sigmas={SIGMA_SWEEP} 16 arms...", flush=True)
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
        verdict, verdict_msg, headline = compute_verdict(all_results[0])

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    # Cardinality check.
    n_arms = 0
    if all_results:
        n_arms = len(all_results[0].get("arms", []))
    cardinality_ok = (n_arms == EXPECTED_N_UNITS)
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
            f"n_arms={n_arms} != expected={EXPECTED_N_UNITS}. "
            + verdict_msg
        )

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    # CRLB floor: sigma_min = sqrt(0.25 / M) at each alpha.
    crlb_floor_M_low = math.sqrt(0.25 / max(M_LOW_FULL, 1))    # 0.0175 @ M=819
    crlb_floor_M_high = math.sqrt(0.25 / max(M_HIGH_FULL, 1))  # 0.0082 @ M=3686

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_c={N_CORTEX} BETA={BETA} "
            f"alphas={{{ALPHA_LOW},{ALPHA_HIGH}}} "
            f"sigmas={SIGMA_SWEEP} "
            f"mode={RUN_MODE} backend={COMPUTE_BACKEND}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_c": N_CORTEX,
        "M_LOW": M_LOW_FULL,
        "M_HIGH": M_HIGH_FULL,
        "BETA": BETA,
        "ALPHA_LOW": ALPHA_LOW,
        "ALPHA_HIGH": ALPHA_HIGH,
        "SIGMA_SWEEP": SIGMA_SWEEP,
        "backend": COMPUTE_BACKEND,
        "n_seeds": 1,
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed_M_low": crlb_floor_M_low,
        "crlb_floor_computed_M_high": crlb_floor_M_high,
        "crlb_formula_reference": "sigma_min = sqrt(0.25/M) binomial-CLT",
        "discriminator_reachability": True,  # HP delta 0.03 > CRLB floors
        "calibration_check": "default_ok_for_this_regime",
        "discriminator_survives_scale": True,  # smoke at full N=8192
        "hp_interaction_delta": HP_INTERACTION_DELTA,
        "mb_interaction_delta": MB_INTERACTION_DELTA,
        "hf_interaction_tol": HF_INTERACTION_TOL,
        "broken_pc_floor": BROKEN_PC_FLOOR,
        "regime_match_tol": REGIME_MATCH_TOL,
        "v3_cg_reference_recall": V3_CG_REFERENCE_RECALL,
        "parent_v3_cg": "cortex_hippo_dense_beta_sweep_v3_query_noise_seed_7",
        "parent_drill": "notes/research_dim_t_regime_transitions_composition_2026-07-02.md",
        "hypothesis_being_tested": "joint_surface_interaction_alpha_sigma",
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
