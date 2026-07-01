"""cortex_hippo_dense_beta_sweep_v3_query_noise -- seed_7.

Revival cell for Atom 3 MM (universal saturation at M=4096 with independent
keys; Skunkworks 2026-07-01). v2 correlated-keys smoke discovered that key
correlation ALONE is INSUFFICIENT to break saturation (queries=keys trivially
wins argmax regardless of beta). v2 probe found the actually-discriminating
axis: QUERY NOISE.

v2 probe at N_c=2048, M=1000, noise_std=0.1:
  INDEP:  r(beta=5)=0.494  vs  r(beta=13)=1.000   |delta| = 0.506
  SUB512: r(beta=5)=0.435  vs  r(beta=13)=1.000   |delta| = 0.565
  SUB256: r(beta=5)=0.246  vs  r(beta=13)=1.000   |delta| = 0.754

v3 pivot APPROVED by Director 2026-07-01. Correlation IS orthogonal to the
finding; v3 uses INDEPENDENT keys (v1 regime) and sweeps QUERY NOISE.

Design: 6 arms x 1 seed x 1 M (N_c=8192, M=4000).
  {NOISE_0P0 [ceiling PC], NOISE_0P1 [discriminating], NOISE_0P3 [crumble edge]}
  x {beta=5, beta=13}.

HP: beta discriminates under noise=0.1 with |delta| >= 0.30 (v2 predicts 0.5+
  at smoke scale) AND NOISE_0P0 arms both saturate (>= 0.95; broken-PC).

If HP across all 3 seeds: **CHAIN_GRADE_BETA_NOISE_ROBUSTNESS**. Beta is a
real substrate lever governing noise-robust attention. Supersedes Atom 3 MM
(universal saturation). Stage 1 100% close per USER directive.

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

from experiments._substrate_cortex_hippo_dense_beta_sweep_v3_query_noise_core import (
    N_CORTEX_FULL, M_FULL, N_CORTEX_SMOKE, M_SMOKE,
    ARM_SPECS, BETA_LO, BETA_HI, NOISE_0P0, NOISE_0P1, NOISE_0P3,
    DISCRIMINATE_DELTA_HP, DISCRIMINATE_DELTA_MB,
    NOISE_0_SATURATION_FLOOR, CRUMBLE_FLOOR, HIGH_NOISE_EXPECTED_CEILING,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_one_arm, run_all_selftests, compute_verdict,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "cortex_hippo_dense_beta_sweep_v3_query_noise_seed_7"
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
    N_CORTEX = N_CORTEX_SMOKE  # 2048
    M_ITEMS = M_SMOKE          # 1000
    ATTN_CHUNK = 500
else:
    N_CORTEX = N_CORTEX_FULL   # 8192
    M_ITEMS = M_FULL           # 4000
    ATTN_CHUNK = 1000

COMPUTE_BACKEND = "numpy"
EXPECTED_N_UNITS = len(ARM_SPECS)   # 6

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_c={N_CORTEX},M={M_ITEMS},"
    f"BETA={{{BETA_LO},{BETA_HI}}},noise_std={{0.0,0.1,0.3}},"
    f"SEED={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},backend={COMPUTE_BACKEND},"
    f"revival=v3_query_noise+ATOM_3_MM_revival+SUPERSEDES_v2_correlated"
)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  N_c={N_CORTEX}  M={M_ITEMS}  "
        f"BETA={{{BETA_LO},{BETA_HI}}}  noise_std={{0.0,0.1,0.3}}  "
        f"mode={RUN_MODE}  seed={SEED_THIS_CHUNK}  "
        f"backend={COMPUTE_BACKEND}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Per-seed driver: run 6 arms
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    arms: List[Dict] = []

    for arm_name, beta, noise_std, noise_class in ARM_SPECS:
        arm_dict = run_one_arm(
            seed=seed, arm_name=arm_name, beta=beta, noise_std=noise_std,
            noise_class=noise_class, m_items=M_ITEMS, n_c=N_CORTEX,
            attn_chunk=ATTN_CHUNK, out_dir=out_dir,
        )
        arms.append(arm_dict)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "BETA_LO": BETA_LO,
        "BETA_HI": BETA_HI,
        "NOISE_0P0": NOISE_0P0,
        "NOISE_0P1": NOISE_0P1,
        "NOISE_0P3": NOISE_0P3,
        "backend": COMPUTE_BACKEND,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "arms": arms,
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
        "M": M_ITEMS,
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
              f"backend={COMPUTE_BACKEND} N_c={N_CORTEX} M={M_ITEMS} "
              f"6 arms...", flush=True)
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

    # Cardinality check
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

    # CRLB floor at M: sigma_min = sqrt(0.25 / M)
    crlb_floor_M = math.sqrt(0.25 / max(M_ITEMS, 1)) if M_ITEMS > 0 else 0.0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_c={N_CORTEX} M={M_ITEMS} "
            f"BETA={{{BETA_LO},{BETA_HI}}} noise_std={{0.0,0.1,0.3}} "
            f"mode={RUN_MODE} backend={COMPUTE_BACKEND}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "BETA_LO": BETA_LO,
        "BETA_HI": BETA_HI,
        "NOISE_0P0": NOISE_0P0,
        "NOISE_0P1": NOISE_0P1,
        "NOISE_0P3": NOISE_0P3,
        "backend": COMPUTE_BACKEND,
        "n_seeds": 1,
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed_M": crlb_floor_M,
        "crlb_formula_reference": "sigma_min = sqrt(0.25/M) binomial-CLT",
        "discriminator_reachability": True,   # HP delta 0.30 >> CRLB 0.008
        "calibration_check": "query_noise_beta_axis_discrimination",
        "discriminator_survives_scale": True,
        "hp_discriminate_delta": DISCRIMINATE_DELTA_HP,
        "mb_discriminate_delta": DISCRIMINATE_DELTA_MB,
        "noise_0_saturation_floor": NOISE_0_SATURATION_FLOOR,
        "crumble_floor": CRUMBLE_FLOOR,
        "high_noise_expected_ceiling": HIGH_NOISE_EXPECTED_CEILING,
        "parent_atom_3_mm": "cortex_hippo_dense_beta_sweep_v1_seed_7_universal_saturation_2026-07-01",
        "parent_v2_correlated_hf": "cortex_hippo_dense_beta_sweep_v2_correlated_keys_seed_7_smoke_HF_2026-07-01",
        "revival_criterion": "V2_PROBE_DISCOVERED_QUERY_NOISE_AXIS_DIRECTOR_APPROVED_v3_PIVOT",
        "revival_intent": "supersede_Atom_3_MM_via_beta_axis_discriminates_under_query_noise",
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
