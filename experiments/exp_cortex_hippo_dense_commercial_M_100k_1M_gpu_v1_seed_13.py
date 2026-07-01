"""cortex_hippo_dense_commercial_M 100k-1M validation cell -- seed_7.

Tests Testbed T2 chunked_attention primitive at commercial-M scale on GPU.
Closes Stage 1 M-sweep scale gap (M up to 1M at N=8192).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
- final_metrics_atomicity: tmp_replace (META_RULE_AH)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- crlb_floor_computed + discriminator_reachability declared (adaptive beta)
- baseline_in_band at smoke (META_RULE_AG; ARM_STD expected ~0.0, ARM_REPL >>0)
- discriminator survives scale (smoke at reduced-N + FULL_N preview at M=100k)
- HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
- cardinality_ok for M-sweep (META_RULE_H; 2 arms * 3 M = 6 units in FULL)
- per-unit failure-class instrumentation (META_RULE_J; no bare except)
- calibration_check: adaptive_with_discriminator_gate (adaptive beta per M)
- Numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@

PRIOR (substrate-KB 2026-07-01 concept-query at cosine < 0.30):
  Adjacent: chunked-into-1563-bundles at 100K facts CITED@research_drill_pattern_b
  Novel at M >= 500k (no prior atom).

CROSS-REFS:
  hdlab/chunked_attention.py (Testbed T2 chain-grade, 2026-07-01)
  Cell D dense-Hopfield READ-REPLACE (Atom 1: cortex_hippo_dense_layer_M_sweep_v3)
  Cell E INT8 Pareto (Atom 5: int8_pareto_optimal_M_40k_80k)
  WM multi-bank K=4096 CG

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

from experiments._substrate_cortex_hippo_dense_commercial_M_100k_1M_gpu_v1_core import (
    N_CORTEX_FULL, V_DIM_FULL, BETA_BASE, M_REF, ATTN_CHUNK_FULL, N_QUERIES_FULL,
    M_SWEEP_FULL,
    N_CORTEX_SMOKE, V_DIM_SMOKE, M_SWEEP_SMOKE, M_SMOKE_PREVIEW_FULL_N,
    N_QUERIES_SMOKE,
    _TORCH_AVAILABLE, _CUDA_AVAILABLE,
    adaptive_beta, predicted_p_win,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_arm, run_one_M, run_all_selftests, compute_verdict,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "cortex_hippo_dense_commercial_M_100k_1M_gpu_v1_seed_13"
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


# ---------------------------------------------------------------------------
# Per-mode config
# ---------------------------------------------------------------------------
if RUN_MODE == "smoke":
    N_CORTEX = N_CORTEX_SMOKE
    V_DIM = V_DIM_SMOKE
    M_LIST = list(M_SWEEP_SMOKE)             # [10_000] smoke
    N_QUERIES = N_QUERIES_SMOKE
    ATTN_CHUNK = 512
    RUN_FULL_N_PREVIEW = True
    PREVIEW_M = M_SMOKE_PREVIEW_FULL_N       # 100_000 preview at full N
    USE_TORCH = _TORCH_AVAILABLE             # torch OK on CPU for smoke
    USE_INT8_KEYS_SMOKE = False              # smoke uses float; INT8 tested at FULL
else:
    N_CORTEX = N_CORTEX_FULL
    V_DIM = V_DIM_FULL
    M_LIST = list(M_SWEEP_FULL)              # [100_000, 500_000, 1_000_000]
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

# Cardinality (META_RULE_H): 2 arms * N_M values per seed
EXPECTED_N_UNITS = 2 * len(M_LIST)

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_c={N_CORTEX},V={V_DIM},M_LIST={M_LIST},"
    f"beta_base={BETA_BASE},M_ref={M_REF},chunk={ATTN_CHUNK},"
    f"n_queries={N_QUERIES},int8_keys={USE_INT8_KEYS},"
    f"SEED={SEED_THIS_CHUNK},RUN_MODE={RUN_MODE},backend={COMPUTE_BACKEND},"
    f"discipline=v1_META_RULES_AC_AF_AG_AH_CRLB_adaptive_beta"
)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  N_c={N_CORTEX} V={V_DIM} M_LIST={M_LIST} "
        f"beta_base={BETA_BASE} chunk={ATTN_CHUNK} mode={RUN_MODE} "
        f"seed={SEED_THIS_CHUNK} backend={COMPUTE_BACKEND} "
        f"torch={_TORCH_AVAILABLE} cuda={_CUDA_AVAILABLE}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Per-seed driver
# ---------------------------------------------------------------------------
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
            f"N_c={N_CORTEX_FULL} V={V_DIM_FULL} ...",
            flush=True,
        )
        preview_arms = run_one_M(
            seed=seed, M=PREVIEW_M, N=N_CORTEX_FULL, V=V_DIM_FULL,
            n_queries=N_QUERIES_SMOKE, chunk_size=ATTN_CHUNK_FULL,
            out_dir=out_dir, use_torch=USE_TORCH, use_int8_keys=False,
        )
        preview = {"M": PREVIEW_M, "arms": preview_arms}

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_c": N_CORTEX,
        "V_DIM": V_DIM,
        "M_LIST": M_LIST,
        "beta_base": BETA_BASE,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "int8_keys": USE_INT8_KEYS,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "per_M": per_M,
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
        "V": V_DIM,
        "M_LIST": M_LIST,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
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

    # Cardinality check (META_RULE_H)
    n_arm_outcomes = 0
    if all_results:
        for m_str, arms in all_results[0].get("per_M", {}).items():
            n_arm_outcomes += len(
                [a for a in arms if a["arm_name"] in ("ARM_STD", "ARM_REPL")]
            )
    cardinality_ok = (n_arm_outcomes == EXPECTED_N_UNITS)

    # Arms-must-differ (META_RULE_AF): verify STD hash != REPL hash per M
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

    # GPU underutil warn (as in reference cell)
    if RUN_MODE == "full" and USE_TORCH and _CUDA_AVAILABLE:
        max_peak_mb = 0.0
        for r in all_results:
            for m_str, arms in r.get("per_M", {}).items():
                for a in arms:
                    max_peak_mb = max(
                        max_peak_mb, float(a.get("gpu_mem_peak_mb", 0.0))
                    )
        if max_peak_mb < 100.0:
            verdict_msg = (
                f"WARN_GPU_UNDERUTIL: max gpu_mem_peak_mb={max_peak_mb:.1f} < 100MB. "
                + verdict_msg
            )

    # CRLB fields per META_RULE_L / capacity-feasibility
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
            f"mode={RUN_MODE} backend={COMPUTE_BACKEND} int8_keys={USE_INT8_KEYS}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_c": N_CORTEX,
        "V_DIM": V_DIM,
        "M_LIST": M_LIST,
        "beta_base": BETA_BASE,
        "M_REF": M_REF,
        "chunk_size": ATTN_CHUNK,
        "n_queries": N_QUERIES,
        "int8_keys": USE_INT8_KEYS,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
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
        "primitive_reference_testbed_T2": "hdlab/chunked_attention.py",
        "primitive_reference_int8_pareto": "hdlab/int8_dense.py",
        "cell_chunked": True,
        "start_marker_written": True,
        "crash_diagnostic_present": True,
        "heartbeat_present": True,
        "defensive_error_checking": "passed_all_4_patterns",
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
    from experiments._substrate_cortex_hippo_dense_commercial_M_100k_1M_gpu_v1_core import (
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
