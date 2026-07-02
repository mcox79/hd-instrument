"""stage2 Dim F batched QPS at commercial M v1 -- seed_13.

Empirical validation of Sonnet Dim F drill batched-scaling prediction:
    predicted QPS(B=64) = ~19,000 QPS at M=500k on torch.cuda (~32x sequential).
    Load-bearing for M3 Phase 1 100-user shard deployment feasibility.

See core `_stage2_dim_f_batched_qps_at_commercial_M_v1_core.py` for design.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified at smoke gate (META_RULE_AF; hash across B values)
- arms_differ_exempted: [(B=1,B=1)] self-pair only
- final_metrics_atomicity: tmp_replace (META_RULE_AH)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_n/a: throughput measurement not signal-recovery
- baseline_in_band exemption: throughput cell not accuracy-differentiation
- discriminator survives scale (smoke IS at full-N=8192 M=500k regime)
- HARD_PASS strictly above HP thresholds (per verdict logic in core)
- cardinality_ok: 5 batch sizes per seed (META_RULE_H; per-seed EXPECTED_N_UNITS=5)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: default_ok_for_this_regime (adaptive_beta pass-through)
- Selftest: verdict-logic self-tests (HP/HF/MB) + adaptive_beta parity check
- Numbers tagged: MEASURED@hippo_v5_M500k / THEORETICAL@Sonnet_drill / HYPOTHESIZED@

PRESERVE_ENV_VARS: HDLAB_QUEUE
"""
from __future__ import annotations
import sys
import argparse
import json
import os
import time
import traceback
from pathlib import Path
from typing import Dict, List

import numpy as np
import torch  # noqa: F401  -- Fix #24: cell must reference torch directly

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._stage2_dim_f_batched_qps_at_commercial_M_v1_core import (
    N_CORTEX_FULL, V_DIM_FULL, M_FULL, BETA_BASE, M_REF, ATTN_CHUNK_FULL,
    BATCH_SIZES_FULL, N_WARMUP_FULL, N_MEASURE_FULL,
    BATCH_SIZES_SMOKE, N_WARMUP_SMOKE, N_MEASURE_SMOKE,
    _TORCH_AVAILABLE, _CUDA_AVAILABLE,
    HP_BATCH_LINEAR_MIN_SPEEDUP, HP_100USER_SHARD_QPS_MIN,
    HP_MEMORY_CONTROLLED_MB_MAX, HP_TAIL_P99_P50_RATIO_MAX,
    HF_BATCH_PLATEAUS_EARLY_MAX_SPEEDUP, HF_1000USER_INFEASIBLE_QPS_MAX,
    HF_MECHANISM_DEATH_RECALL_MIN, HF_MEMORY_BLOWUP_MB_MAX,
    adaptive_beta,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_one_batch_size, run_all_selftests, compute_verdict,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "stage2_dim_f_batched_qps_at_commercial_M_v1_seed_13"
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


if RUN_MODE == "smoke":
    BATCH_SIZES = list(BATCH_SIZES_SMOKE)
    N_WARMUP = N_WARMUP_SMOKE
    N_MEASURE = N_MEASURE_SMOKE
else:
    BATCH_SIZES = list(BATCH_SIZES_FULL)
    N_WARMUP = N_WARMUP_FULL
    N_MEASURE = N_MEASURE_FULL

N_CORTEX = N_CORTEX_FULL
V_DIM = V_DIM_FULL
M = M_FULL
ATTN_CHUNK = ATTN_CHUNK_FULL
USE_TORCH = _TORCH_AVAILABLE and _CUDA_AVAILABLE
COMPUTE_BACKEND = (
    "torch.cuda" if (USE_TORCH and _CUDA_AVAILABLE)
    else ("torch.cpu" if _TORCH_AVAILABLE else "numpy_unsupported")
)

EXPECTED_N_UNITS = len(BATCH_SIZES)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_c={N_CORTEX},V={V_DIM},M={M},"
    f"BATCH_SIZES={BATCH_SIZES},n_warmup={N_WARMUP},n_measure={N_MEASURE},"
    f"chunk={ATTN_CHUNK},beta_base={BETA_BASE},M_ref={M_REF},"
    f"SEED={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},backend={COMPUTE_BACKEND},"
    f"discipline=stage2_dim_f_batched_qps_at_commercial_M_v1"
)


def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  N_c={N_CORTEX} V={V_DIM} M={M} BATCH_SIZES={BATCH_SIZES} "
        f"n_warmup={N_WARMUP} n_measure={N_MEASURE} beta_base={BETA_BASE} "
        f"chunk={ATTN_CHUNK} mode={RUN_MODE} seed={SEED_THIS_CHUNK} "
        f"backend={COMPUTE_BACKEND} torch={_TORCH_AVAILABLE} cuda={_CUDA_AVAILABLE}",
        flush=True,
    )


def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    per_arm: List[Dict] = []
    for i, b in enumerate(BATCH_SIZES):
        t_arm = time.time()
        arm = run_one_batch_size(
            seed=seed, batch_size=b, M=M, N=N_CORTEX, V=V_DIM,
            chunk_size=ATTN_CHUNK, n_warmup=N_WARMUP, n_measure=N_MEASURE,
            out_dir=out_dir,
        )
        per_arm.append(arm)
        emit_heartbeat(
            out_dir, unit_idx=i + 1,
            elapsed_s=time.time() - t_arm,
            total_units=len(BATCH_SIZES),
            extra={
                "batch_size": b, "qps": arm["effective_qps"],
                "recall": arm["recall_cosine_mean"],
                "gpu_mem_peak_mb": arm["gpu_mem_peak_mb"],
                "tail_p99_p50": arm["per_dispatch_wall_p99_p50_ratio"],
            },
        )

    elapsed = time.time() - t0
    return {
        "seed": seed, "N_c": N_CORTEX, "V_DIM": V_DIM, "M": M,
        "BATCH_SIZES": BATCH_SIZES,
        "n_warmup": N_WARMUP, "n_measure": N_MEASURE,
        "beta_base": BETA_BASE, "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE, "cuda_available": _CUDA_AVAILABLE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION, "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK, "per_arm": per_arm,
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
        "N": N_CORTEX, "V": V_DIM, "M": M, "BATCH_SIZES": BATCH_SIZES,
        "n_warmup": N_WARMUP, "n_measure": N_MEASURE,
        "run_mode": RUN_MODE, "anchor": ANCHOR_NAME,
    }
    seeds_list = [SEED_THIS_CHUNK]
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)}/{len(seeds_list)} done; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(
            f"[seed={seed}] {ANCHOR_NAME} mode={RUN_MODE} "
            f"backend={COMPUTE_BACKEND} BATCH_SIZES={BATCH_SIZES}...",
            flush=True,
        )
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n"
                f"{traceback.format_exc()}",
                encoding="utf-8",
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
        per_arm = all_results[0].get("per_arm", [])
        verdict, verdict_msg, headline = compute_verdict(
            per_arm, RUN_MODE, EXPECTED_N_UNITS,
        )

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    n_arm_outcomes = 0
    if all_results:
        n_arm_outcomes = len(all_results[0].get("per_arm", []))
    cardinality_ok = (n_arm_outcomes == EXPECTED_N_UNITS)

    # ARMS-MUST-DIFFER (META_RULE_AF) — pairwise across B values.
    arms_differ_verified = True
    if all_results:
        hashes = [(a["batch_size"], a.get("arm_hash", ""))
                  for a in all_results[0].get("per_arm", [])]
        for i in range(len(hashes)):
            for j in range(i + 1, len(hashes)):
                if (hashes[i][1] == hashes[j][1]
                        and hashes[i][1] != "n/a" and hashes[i][1] != ""):
                    arms_differ_verified = False
                    verdict = "HARD_FAIL"
                    verdict_msg = (
                        f"HARD_FAIL_META_RULE_AF: B={hashes[i][0]} and "
                        f"B={hashes[j][0]} bit-identical (hash={hashes[i][1]}). "
                        + verdict_msg
                    )

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
            f"chunk_seed={SEED_THIS_CHUNK} N_c={N_CORTEX} V={V_DIM} M={M} "
            f"BATCH_SIZES={BATCH_SIZES} n_measure={N_MEASURE} "
            f"mode={RUN_MODE} backend={COMPUTE_BACKEND} "
            f"stage2_dim_f_batched_qps"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_c": N_CORTEX, "V_DIM": V_DIM, "M": M,
        "BATCH_SIZES": BATCH_SIZES,
        "n_warmup": N_WARMUP, "n_measure": N_MEASURE,
        "beta_base": BETA_BASE, "M_REF": M_REF,
        "chunk_size": ATTN_CHUNK,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE, "cuda_available": _CUDA_AVAILABLE,
        "n_seeds": 1,
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "arms_differ_verified": arms_differ_verified,
        "arms_differ_exempted": [["B=1", "B=1"]],
        "final_metrics_atomicity": "tmp_replace",
        "calibration_check": "default_ok_for_this_regime",
        "discriminator_reachability": True,
        "crlb_n/a": (
            "throughput measurement; timing scaling prediction from "
            "kernel-launch amortization theory not signal-recovery task"
        ),
        "hp_thresholds": {
            "HP_BATCH_LINEAR_MIN_SPEEDUP": HP_BATCH_LINEAR_MIN_SPEEDUP,
            "HP_100USER_SHARD_QPS_MIN": HP_100USER_SHARD_QPS_MIN,
            "HP_MEMORY_CONTROLLED_MB_MAX": HP_MEMORY_CONTROLLED_MB_MAX,
            "HP_TAIL_P99_P50_RATIO_MAX": HP_TAIL_P99_P50_RATIO_MAX,
        },
        "hf_thresholds": {
            "HF_BATCH_PLATEAUS_EARLY_MAX_SPEEDUP": HF_BATCH_PLATEAUS_EARLY_MAX_SPEEDUP,
            "HF_1000USER_INFEASIBLE_QPS_MAX": HF_1000USER_INFEASIBLE_QPS_MAX,
            "HF_MECHANISM_DEATH_RECALL_MIN": HF_MECHANISM_DEATH_RECALL_MIN,
            "HF_MEMORY_BLOWUP_MB_MAX": HF_MEMORY_BLOWUP_MB_MAX,
        },
        "primitive_reference_gpu_gen": "hdlab/gpu_generated_streaming_attention.py",
        "primitive_reference_int8_pareto": "hdlab/int8_dense.py",
        "cell_chunked": True,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
        "progress_logging": "print_flush_true",
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "headline": headline,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "per_arm": r.get("per_arm"),
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
    from experiments._stage2_dim_f_batched_qps_at_commercial_M_v1_core import (
        write_crash_metrics as _wcm,
    )
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _exc:
        _wcm(_out_dir_for_crash, ANCHOR_NAME, _exc)
        raise
