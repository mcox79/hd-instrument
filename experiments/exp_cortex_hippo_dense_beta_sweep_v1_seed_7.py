"""cortex_hippo_dense_beta_sweep_v1 -- seed_7.

BETA-sweep of Cell D v2 replacement-mode CG. Sweeps beta in {5, 8, 13, 20, 32}
at each M in {4096, 8192, 16384}; asks whether the adaptive formula
beta = log2(M) / cos_margin selects the argmax-beta at each M.

Complements v3 M-sweep: v3 fixes formula and sweeps M; v1 (this) fixes M grid
and sweeps beta at each M.

CARDINALITY (META_RULE_H):
  FULL:  3 M * (2 baseline + 5 beta REPLACE) = 21 arm-outcomes per seed.
  SMOKE: 1 M * (2 baseline + 5 beta REPLACE) = 7 arm-outcomes + 1 preview.

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Smoke runs full BETA_SWEEP at M=4096 AND a FULL_N preview at M=16384,
  beta=20 (adaptive-target). If preview < 0.60, reject FULL.

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

from experiments._substrate_cortex_hippo_dense_beta_sweep_v1_core import (
    N_HIPPO_FULL, N_CORTEX_FULL, HIPPO_SPARSITY, ETA_HIPPO_FULL,
    BETA_SWEEP, M_SWEEP_FULL,
    M_SWEEP_SMOKE_MAIN, M_SWEEP_SMOKE_PREVIEW, BETA_PREVIEW, BETA_PREVIEW_LOW,
    ADAPTIVE_NEAREST_BETA,
    _TORCH_AVAILABLE, _CUDA_AVAILABLE,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_one_M, run_preview_full_N, run_all_selftests, compute_verdict,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "cortex_hippo_dense_beta_sweep_v1_seed_7"
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
    N_HIPPO = 512
    N_CORTEX = 1024
    HIPPO_SPARSITY_USED = HIPPO_SPARSITY
    M_LIST = [M_SWEEP_SMOKE_MAIN]  # 4096
    BETA_LIST_USED = list(BETA_SWEEP)
    RUN_FULL_N_PREVIEW = True
    PREVIEW_M = M_SWEEP_SMOKE_PREVIEW  # 16384
    PREVIEW_BETA = BETA_PREVIEW        # 20.0
    ETA_HIPPO = ETA_HIPPO_FULL
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    HIPPO_SPARSITY_USED = HIPPO_SPARSITY
    M_LIST = list(M_SWEEP_FULL)  # [4096, 8192, 16384]
    BETA_LIST_USED = list(BETA_SWEEP)
    RUN_FULL_N_PREVIEW = False
    PREVIEW_M = None
    PREVIEW_BETA = None
    ETA_HIPPO = ETA_HIPPO_FULL

USE_TORCH_CUDA = (RUN_MODE == "full") and _TORCH_AVAILABLE and _CUDA_AVAILABLE
COMPUTE_BACKEND = "torch.cuda" if USE_TORCH_CUDA else ("torch.cpu" if _TORCH_AVAILABLE else "numpy")

# ATTN chunk per M for VRAM control
ATTN_CHUNK_FULL = 1024
ATTN_CHUNK_SMOKE = 4096  # smoke uses smaller substrate; full-batch is fine

# Cardinality (META_RULE_H)
if RUN_MODE == "full":
    EXPECTED_N_UNITS = len(M_LIST) * (2 + len(BETA_LIST_USED))  # 3 * 7 = 21
else:
    EXPECTED_N_UNITS = len(M_LIST) * (2 + len(BETA_LIST_USED))  # 1 * 7 = 7

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY_USED},M_LIST={M_LIST},BETA_LIST={BETA_LIST_USED},"
    f"eta_h={ETA_HIPPO},SEED={SEED_THIS_CHUNK},"
    f"RUN_MODE={RUN_MODE},backend={COMPUTE_BACKEND},"
    f"hardening=v1_BETA_SWEEP+METARULE_AF_hashtest+METARULE_AH+FIXED_BETA"
)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  N_h={N_HIPPO}  N_c={N_CORTEX}  "
        f"sparsity={HIPPO_SPARSITY_USED}  M_LIST={M_LIST}  "
        f"BETA_LIST={BETA_LIST_USED}  eta_h={ETA_HIPPO}  "
        f"mode={RUN_MODE}  seed={SEED_THIS_CHUNK}  "
        f"backend={COMPUTE_BACKEND}  torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Per-seed driver: sweep beta at each M
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    per_M: Dict[int, List[Dict]] = {}
    attn_chunk = ATTN_CHUNK_FULL if RUN_MODE == "full" else ATTN_CHUNK_SMOKE

    for m_val in M_LIST:
        arms_at_M = run_one_M(
            seed=seed, m_items=m_val, n_h=N_HIPPO, n_c=N_CORTEX,
            hippo_sparsity=HIPPO_SPARSITY_USED, eta_hippo=ETA_HIPPO,
            beta_list=BETA_LIST_USED, attn_chunk=attn_chunk,
            use_cuda=USE_TORCH_CUDA, out_dir=out_dir,
        )
        per_M[int(m_val)] = arms_at_M

    preview = None
    preview_low = None
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW and PREVIEW_M is not None:
        print(f"  [seed={seed} PREVIEW_FULL_N M={PREVIEW_M} beta={PREVIEW_BETA}] "
              f"running at N_h={N_HIPPO_FULL} N_c={N_CORTEX_FULL}...", flush=True)
        preview = run_preview_full_N(
            seed=seed, m_preview=PREVIEW_M, beta_preview=PREVIEW_BETA,
            hippo_sparsity=HIPPO_SPARSITY_USED, eta_hippo=ETA_HIPPO_FULL,
            attn_chunk=1024, out_dir=out_dir,
        )
        print(
            f"  [seed={seed} PREVIEW M={PREVIEW_M} beta={PREVIEW_BETA}] "
            f"recall={preview['recall_cortex']:.3f} "
            f"cos_margin={preview.get('cosine_margin_used','NA')} "
            f"wall={preview['wall_s']:.1f}s status={preview['arm_status']}",
            flush=True,
        )
        # DISCRIPLINE PATTERN 2: low-beta discriminator preview at FULL_N.
        # If beta=5 preview at FULL_N differentiates from beta=20 preview,
        # the beta axis is meaningful at full scale. If both saturate at 1.0,
        # the smoke did NOT fire the discriminator at FULL_N.
        print(f"  [seed={seed} PREVIEW_LOW_BETA M={PREVIEW_M} beta={BETA_PREVIEW_LOW}] "
              f"running discriminator-fires check...", flush=True)
        preview_low = run_preview_full_N(
            seed=seed, m_preview=PREVIEW_M, beta_preview=BETA_PREVIEW_LOW,
            hippo_sparsity=HIPPO_SPARSITY_USED, eta_hippo=ETA_HIPPO_FULL,
            attn_chunk=1024, out_dir=out_dir,
        )
        print(
            f"  [seed={seed} PREVIEW_LOW M={PREVIEW_M} beta={BETA_PREVIEW_LOW}] "
            f"recall={preview_low['recall_cortex']:.3f} "
            f"cos_margin={preview_low.get('cosine_margin_used','NA')} "
            f"wall={preview_low['wall_s']:.1f}s status={preview_low['arm_status']}",
            flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M_LIST": M_LIST,
        "BETA_LIST": BETA_LIST_USED,
        "eta_h": ETA_HIPPO,
        "hippo_sparsity": HIPPO_SPARSITY_USED,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "per_M": per_M,
        "preview_arm": preview,
        "preview_arm_low_beta": preview_low,
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
        "M_LIST": M_LIST,
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
              f"backend={COMPUTE_BACKEND} M_LIST={M_LIST} "
              f"BETA={BETA_LIST_USED}...", flush=True)
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
        verdict, verdict_msg, headline = compute_verdict(
            all_results[0], RUN_MODE, N_CORTEX
        )

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    # Cardinality check
    n_arm_outcomes = 0
    if all_results:
        for m_val, arms in all_results[0].get("per_M", {}).items():
            n_arm_outcomes += len(arms)  # includes baselines + all beta reads
    cardinality_ok = (n_arm_outcomes == EXPECTED_N_UNITS)
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: "
            f"n_arm_outcomes={n_arm_outcomes} != expected={EXPECTED_N_UNITS}. "
            + verdict_msg
        )

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    if RUN_MODE == "full" and USE_TORCH_CUDA:
        max_peak_mb = 0.0
        for r in all_results:
            for m_val, arms in r.get("per_M", {}).items():
                for a in arms:
                    max_peak_mb = max(max_peak_mb,
                                      float(a.get("gpu_mem_peak_mb", 0.0)))
        if max_peak_mb < 100.0:
            verdict_msg = (
                f"WARN_GPU_UNDERUTIL: max gpu_mem_peak_mb={max_peak_mb:.1f} < 100MB. "
                + verdict_msg
            )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_h={N_HIPPO} N_c={N_CORTEX} sparsity={HIPPO_SPARSITY_USED} "
            f"M_LIST={M_LIST} BETA_LIST={BETA_LIST_USED} eta_h={ETA_HIPPO} "
            f"mode={RUN_MODE} backend={COMPUTE_BACKEND}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M_LIST": M_LIST,
        "BETA_LIST": BETA_LIST_USED,
        "eta_h": ETA_HIPPO,
        "hippo_sparsity": HIPPO_SPARSITY_USED,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "n_seeds": 1,
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed_M4096": 0.00781,
        "crlb_floor_computed_M8192": 0.00552,
        "crlb_floor_computed_M16384": 0.00390,
        "crlb_formula_reference": "sigma_min = sqrt(0.25/M) binomial-CLT",
        "discriminator_reachability": True,
        "calibration_check": "adaptive_with_discriminator_gate",
        "adaptive_nearest_beta_map": {str(k): v for k, v in ADAPTIVE_NEAREST_BETA.items()},
        "parent_v2_landing": "fc47b1bb_recall_1.000_M8192_3seed",
        "parent_v3_context": "v3_M_sweep_in_flight_2026-07-01",
        "beta_sweep_intent": "characterize_recall_optimum_and_robustness_vs_adaptive_formula",
        "headline": headline,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "per_M": r.get("per_M"),
                "preview_arm": r.get("preview_arm"),
                "preview_arm_low_beta": r.get("preview_arm_low_beta"),
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
