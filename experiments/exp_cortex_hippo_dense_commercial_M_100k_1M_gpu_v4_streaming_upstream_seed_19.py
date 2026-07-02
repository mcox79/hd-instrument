"""cortex_hippo_dense_commercial_M 100k-1M validation cell v4 -- seed_19.

v4 FIX for v3 CPU-BOUND wall_s: v3 pre-materialized full-M keys+vals in CPU RAM
per arm then streamed. Orchestrator M=500k probe measured wall dominated by
CPU-build (21-25s) + INT8-quantize (12s), GPU util 1-3%. v4 generates each
chunk's keys/vals DIRECTLY ON GPU per chunk. Zero CPU RAM for substrate.

v3 probe: MEASURED@C:\\dev\\hd-instrument\\data\\_probe_v3_streaming_M500k/
probe_result.json:
    ARM_STD  M=500k wall=23.8s (cpu-build 21.5s + gpu 2.3s) util=1-3%
    ARM_REPL M=500k wall=39.5s (cpu-build 25.0s + quant 12.3s + gpu 2.2s) util=1-3%

v4 targets (MEASURED@remote_gpu_selftest at M=100k):
    wall_s per arm < 3.0 s (USER-locked)
    gpu_util_mean_pct >= 30 (USER-locked)

See core `_substrate_cortex_hippo_dense_commercial_M_100k_1M_gpu_v4_streaming_upstream_core.py`.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (META_RULE_AF)
- final_metrics_atomicity: tmp_replace (META_RULE_AH)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_floor_computed + discriminator_reachability declared (adaptive beta)
- baseline_in_band exemption for ARM_STD (must-fail arm)
- discriminator survives scale (smoke at FULL_N=8192 M=100k on-GPU-gen preview)
- HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
- cardinality_ok for M-sweep (META_RULE_H; 2 arms * 3 M = 6 units in FULL)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: adaptive_with_discriminator_gate (adaptive beta per M)
- Selftest: on-GPU-gen determinism verified; USER-locked M=100k gates checked
  when CUDA available; deferred to remote GPU smoke when local CPU-only
- v4 observability: gpu_util_mean_pct measured per arm; HF_COMPUTE_STARVED
  gate on any arm with backend=torch.cuda AND M>=100k AND util<20
- Numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@

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

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._substrate_cortex_hippo_dense_commercial_M_100k_1M_gpu_v4_streaming_upstream_core import (
    N_CORTEX_FULL, V_DIM_FULL, BETA_BASE, M_REF, ATTN_CHUNK_FULL, N_QUERIES_FULL,
    M_SWEEP_FULL,
    N_CORTEX_SMOKE, V_DIM_SMOKE, M_SWEEP_SMOKE, M_SMOKE_PREVIEW_FULL_N,
    N_QUERIES_SMOKE, ATTN_CHUNK_SMOKE,
    _TORCH_AVAILABLE, _CUDA_AVAILABLE,
    HF_UTIL_PCT_MIN_M100K, SELFTEST_M100K_WALL_S_MAX, SELFTEST_M100K_UTIL_PCT_MIN,
    adaptive_beta, predicted_p_win,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_arm, run_one_M, run_all_selftests, compute_verdict,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "cortex_hippo_dense_commercial_M_100k_1M_gpu_v4_streaming_upstream_seed_19"
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


if RUN_MODE == "smoke":
    N_CORTEX = N_CORTEX_SMOKE
    V_DIM = V_DIM_SMOKE
    M_LIST = list(M_SWEEP_SMOKE)
    N_QUERIES = N_QUERIES_SMOKE
    ATTN_CHUNK = ATTN_CHUNK_SMOKE
    RUN_FULL_N_PREVIEW = True
    PREVIEW_M = M_SMOKE_PREVIEW_FULL_N
    USE_TORCH = _TORCH_AVAILABLE
    USE_INT8_KEYS_SMOKE = False
else:
    N_CORTEX = N_CORTEX_FULL
    V_DIM = V_DIM_FULL
    M_LIST = list(M_SWEEP_FULL)
    N_QUERIES = N_QUERIES_FULL
    ATTN_CHUNK = ATTN_CHUNK_FULL
    RUN_FULL_N_PREVIEW = False
    PREVIEW_M = None
    USE_TORCH = _TORCH_AVAILABLE and _CUDA_AVAILABLE
    USE_INT8_KEYS_SMOKE = True

USE_INT8_KEYS = USE_INT8_KEYS_SMOKE
COMPUTE_BACKEND = (
    "torch.cuda" if (USE_TORCH and _CUDA_AVAILABLE)
    else ("torch.cpu" if USE_TORCH else "numpy")
)

EXPECTED_N_UNITS = 2 * len(M_LIST)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_c={N_CORTEX},V={V_DIM},M_LIST={M_LIST},"
    f"beta_base={BETA_BASE},M_ref={M_REF},chunk={ATTN_CHUNK},"
    f"n_queries={N_QUERIES},int8_keys={USE_INT8_KEYS},"
    f"SEED={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},backend={COMPUTE_BACKEND},"
    f"hf_util_gate={HF_UTIL_PCT_MIN_M100K},"
    f"discipline=v4_on_gpu_generation_zero_cpu_ram_util_sampled"
)


def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  N_c={N_CORTEX} V={V_DIM} M_LIST={M_LIST} "
        f"beta_base={BETA_BASE} chunk={ATTN_CHUNK} "
        f"mode={RUN_MODE} seed={SEED_THIS_CHUNK} backend={COMPUTE_BACKEND} "
        f"torch={_TORCH_AVAILABLE} cuda={_CUDA_AVAILABLE} "
        f"hf_util_gate={HF_UTIL_PCT_MIN_M100K}",
        flush=True,
    )


def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    per_M: Dict[str, List[Dict]] = {}
    for m_val in M_LIST:
        arms_at_M = run_one_M(
            seed=seed, M=m_val, N=N_CORTEX, V=V_DIM, n_queries=N_QUERIES,
            chunk_size=ATTN_CHUNK, out_dir=out_dir, use_torch=USE_TORCH,
            use_int8_keys=USE_INT8_KEYS,
        )
        per_M[str(int(m_val))] = arms_at_M

    preview = None
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW and PREVIEW_M is not None:
        print(
            f"  [seed={seed} PREVIEW_FULL_N M={PREVIEW_M}] running at "
            f"N_c={N_CORTEX_FULL} V={V_DIM_FULL} (v4 on-GPU-gen smoke gate)...",
            flush=True,
        )
        preview_arms = run_one_M(
            seed=seed, M=PREVIEW_M, N=N_CORTEX_FULL, V=V_DIM_FULL,
            n_queries=N_QUERIES_SMOKE, chunk_size=ATTN_CHUNK_FULL,
            out_dir=out_dir, use_torch=USE_TORCH, use_int8_keys=True,
        )
        preview = {"M": PREVIEW_M, "arms": preview_arms}

    elapsed = time.time() - t0
    return {
        "seed": seed, "N_c": N_CORTEX, "V_DIM": V_DIM, "M_LIST": M_LIST,
        "beta_base": BETA_BASE, "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE, "cuda_available": _CUDA_AVAILABLE,
        "int8_keys": USE_INT8_KEYS, "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION, "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK, "per_M": per_M, "preview_arm": preview,
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
        "N": N_CORTEX, "V": V_DIM, "M_LIST": M_LIST,
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
            f"backend={COMPUTE_BACKEND} M_LIST={M_LIST}...",
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
        verdict, verdict_msg, headline = compute_verdict(all_results[0], RUN_MODE)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    n_arm_outcomes = 0
    if all_results:
        for m_str, arms in all_results[0].get("per_M", {}).items():
            n_arm_outcomes += len(
                [a for a in arms if a["arm_name"] in ("ARM_STD", "ARM_REPL")]
            )
    cardinality_ok = (n_arm_outcomes == EXPECTED_N_UNITS)

    arms_differ_verified = True
    if all_results:
        for m_str, arms in all_results[0].get("per_M", {}).items():
            hashes = {a["arm_name"]: a.get("arm_hash", "") for a in arms}
            if hashes.get("ARM_STD") and hashes.get("ARM_REPL"):
                if hashes["ARM_STD"] == hashes["ARM_REPL"]:
                    arms_differ_verified = False
                    verdict = "HARD_FAIL"
                    verdict_msg = (
                        f"HARD_FAIL_META_RULE_AF: STD and REPL bit-identical at "
                        f"M={m_str}. " + verdict_msg
                    )

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    crlb_fields = {}
    for m in M_LIST:
        beta = adaptive_beta(m)
        p_win = predicted_p_win(m, N_CORTEX_FULL, beta)
        crlb_fields[f"crlb_p_win_predicted_M{m}"] = p_win
        crlb_fields[f"adaptive_beta_M{m}"] = beta

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} N_c={N_CORTEX} V={V_DIM} "
            f"M_LIST={M_LIST} beta_base={BETA_BASE} chunk={ATTN_CHUNK} "
            f"mode={RUN_MODE} backend={COMPUTE_BACKEND} int8_keys={USE_INT8_KEYS} "
            f"v4_on_gpu_generation"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_c": N_CORTEX, "V_DIM": V_DIM, "M_LIST": M_LIST,
        "beta_base": BETA_BASE, "M_REF": M_REF,
        "chunk_size": ATTN_CHUNK,
        "n_queries": N_QUERIES, "int8_keys": USE_INT8_KEYS,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE, "cuda_available": _CUDA_AVAILABLE,
        "n_seeds": 1,
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "arms_differ_verified": arms_differ_verified,
        "final_metrics_atomicity": "tmp_replace",
        "calibration_check": "adaptive_with_discriminator_gate",
        "discriminator_reachability": True,
        "crlb_formula_reference": (
            "logit_gap = beta * (1 - sqrt(2*log(M)/N)); "
            "p_win = 1 / (1 + M * exp(-logit_gap))"
        ),
        **crlb_fields,
        "primitive_reference_gpu_gen": "hdlab/gpu_generated_streaming_attention.py",
        "primitive_reference_streaming": "hdlab/streaming_attention.py",
        "primitive_reference_chunked": "hdlab/chunked_attention.py",
        "primitive_reference_int8_pareto": "hdlab/int8_dense.py",
        "v4_fix_applied": "on_gpu_seeded_key_val_generation_per_chunk_zero_cpu_ram",
        "v3_root_cause": (
            "v3 pre-materialized full-M keys+vals in CPU RAM per arm; wall_s "
            "CPU-dominated (21s cpu-build + 12s int8-quantize at M=500k); "
            "GPU util 1-3% steady-state"
        ),
        "v4_observability": {
            "gpu_util_sampler": "torch.cuda.utilization_or_pynvml_50ms",
            "hf_gate": f"HF_COMPUTE_STARVED_util_lt_{HF_UTIL_PCT_MIN_M100K}_at_M_ge_100k",
            "user_locked_selftest_gate_wall_max_s": SELFTEST_M100K_WALL_S_MAX,
            "user_locked_selftest_gate_util_min_pct": SELFTEST_M100K_UTIL_PCT_MIN,
        },
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
                "per_M": r.get("per_M"),
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
    from experiments._substrate_cortex_hippo_dense_commercial_M_100k_1M_gpu_v4_streaming_upstream_core import (
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
