"""cortex_hippo_dense_layer_M_sweep_v3 -- seed_7. Cross-M expansion of v2 REPLACE.

Extends v2 REPLACE (M=8192 recall~=1.000 3-seed HP at fc47b1bb) to sweep
M in {4096, 8192, 16384} per Skunkworks M3 meta-insight MM_TENTATIVE
expansion criterion (c). Same 3 arms; same adaptive beta ~ log2(M)/margin.

FALSIFIABLE:
  HP: REPLACE ratio>=0.80 AND gap>=0.60 across ALL 3 M values.
  HF: any M fails REPLACE>=0.60 floor (regime-conditional; scale-limited).
  MB: partial rescue -- some M pass, others fall to MIDDLE_BAND.

Smoke runs M=4096 main-arms + FULL_N preview at M=16384 (discriminator
must survive largest scale).

CARDINALITY: 3 M values * 3 arms = 9 arm-outcomes per seed (META_RULE_H).

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

from experiments._substrate_cortex_hippo_dense_layer_M_sweep_v3_core import (
    N_HIPPO_FULL, N_CORTEX_FULL, HIPPO_SPARSITY, ETA_HIPPO_FULL,
    BETA_MIN, BETA_MAX, M_SWEEP_FULL,
    M_SWEEP_SMOKE_MAIN, M_SWEEP_SMOKE_PREVIEW,
    _TORCH_AVAILABLE, _CUDA_AVAILABLE,
    emit_heartbeat, write_start_marker, write_crash_metrics,
    run_arm_numpy, run_one_M, run_all_selftests, compute_verdict,
    _compute_adaptive_beta,
)
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "cortex_hippo_dense_layer_M_sweep_v3_seed_13"
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
    # Smaller substrate; single M value (smallest = fastest); FULL_N preview at
    # largest M so discriminator-must-survive-scale is proven pre-dispatch.
    N_HIPPO = 512
    N_CORTEX = 1024
    HIPPO_SPARSITY_USED = HIPPO_SPARSITY
    M_LIST = [M_SWEEP_SMOKE_MAIN]  # 4096
    RUN_FULL_N_PREVIEW = True
    PREVIEW_M = M_SWEEP_SMOKE_PREVIEW  # 16384
    ETA_HIPPO = ETA_HIPPO_FULL
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    HIPPO_SPARSITY_USED = HIPPO_SPARSITY
    M_LIST = list(M_SWEEP_FULL)  # [4096, 8192, 16384]
    RUN_FULL_N_PREVIEW = False
    PREVIEW_M = None
    ETA_HIPPO = ETA_HIPPO_FULL

USE_TORCH_CUDA = (RUN_MODE == "full") and _TORCH_AVAILABLE and _CUDA_AVAILABLE
COMPUTE_BACKEND = "torch.cuda" if USE_TORCH_CUDA else ("torch.cpu" if _TORCH_AVAILABLE else "numpy")

# ATTN chunk per M for VRAM control
ATTN_CHUNK_FULL = 1024
ATTN_CHUNK_SMOKE = 4096  # smoke uses smaller substrate so full-batch is fine

# Cardinality (META_RULE_H): 3 M * 3 arms = 9 arm outcomes in FULL
EXPECTED_N_UNITS = 3 * 3 if RUN_MODE == "full" else 3

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY_USED},M_LIST={M_LIST},eta_h={ETA_HIPPO},"
    f"beta_range=[{BETA_MIN},{BETA_MAX}],SEED={SEED_THIS_CHUNK},"
    f"RUN_MODE={RUN_MODE},backend={COMPUTE_BACKEND},"
    f"hardening=v3_M_SWEEP+METARULE_AF_hashtest+METARULE_AH+ADAPTIVE_BETA"
)


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  N_h={N_HIPPO}  N_c={N_CORTEX}  "
        f"sparsity={HIPPO_SPARSITY_USED}  M_LIST={M_LIST}  eta_h={ETA_HIPPO}  "
        f"beta_range=[{BETA_MIN},{BETA_MAX}]  "
        f"mode={RUN_MODE}  seed={SEED_THIS_CHUNK}  "
        f"backend={COMPUTE_BACKEND}  torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Per-seed driver: sweep all M
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    per_M: Dict[int, List[Dict]] = {}
    attn_chunk = ATTN_CHUNK_FULL if RUN_MODE == "full" else ATTN_CHUNK_SMOKE

    for m_val in M_LIST:
        arms_at_M = run_one_M(
            seed=seed, m_items=m_val, n_h=N_HIPPO, n_c=N_CORTEX,
            hippo_sparsity=HIPPO_SPARSITY_USED, eta_hippo=ETA_HIPPO,
            attn_chunk=attn_chunk, use_cuda=USE_TORCH_CUDA, out_dir=out_dir,
        )
        per_M[int(m_val)] = arms_at_M

    preview = None
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW and PREVIEW_M is not None:
        print(f"  [seed={seed} PREVIEW_FULL_N M={PREVIEW_M}] running at "
              f"N_h={N_HIPPO_FULL} N_c={N_CORTEX_FULL}...", flush=True)
        rng_p = np.random.RandomState(seed + 101 + PREVIEW_M)
        N_raw = 64
        P_in_p = rng_p.randn(N_HIPPO_FULL, N_raw).astype(np.float64) / np.sqrt(N_raw)
        P_hc_p = rng_p.randn(N_CORTEX_FULL, N_HIPPO_FULL).astype(np.float64) / np.sqrt(N_HIPPO_FULL)
        keys_raw_p = rng_p.choice([-1.0, 1.0], size=(PREVIEW_M, N_raw)).astype(np.float64)
        vals_raw_p = rng_p.choice([-1.0, 1.0], size=(PREVIEW_M, N_raw)).astype(np.float64)
        k_active_p = max(1, int(round(HIPPO_SPARSITY_USED * N_HIPPO_FULL)))
        preview = run_arm_numpy(
            "ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW", seed,
            n_h=N_HIPPO_FULL, n_c=N_CORTEX_FULL, m_items=PREVIEW_M,
            k_active=k_active_p, eta_hippo=ETA_HIPPO_FULL,
            attn_chunk=1024,
            keys_raw=keys_raw_p, vals_raw=vals_raw_p,
            P_in=P_in_p, P_hc=P_hc_p, out_dir=out_dir,
        )
        print(
            f"  [seed={seed} PREVIEW M={PREVIEW_M}] "
            f"recall={preview['recall_cortex']:.3f} "
            f"beta={preview.get('beta_used','NA')} "
            f"margin={preview.get('cosine_margin_used','NA')} "
            f"wall={preview['wall_s']:.1f}s", flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M_LIST": M_LIST,
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
              f"backend={COMPUTE_BACKEND} M_LIST={M_LIST}...", flush=True)
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
            n_arm_outcomes += len([a for a in arms
                                   if a["arm_name"] in ("ARM_STANDARD",
                                                        "ARM_HA_ONLY",
                                                        "ARM_HA_DENSE_REPLACE")])
    cardinality_ok = (n_arm_outcomes == EXPECTED_N_UNITS)

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
            f"M_LIST={M_LIST} eta_h={ETA_HIPPO} "
            f"beta_range=[{BETA_MIN},{BETA_MAX}] "
            f"mode={RUN_MODE} backend={COMPUTE_BACKEND}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M_LIST": M_LIST,
        "eta_h": ETA_HIPPO,
        "hippo_sparsity": HIPPO_SPARSITY_USED,
        "beta_floor": BETA_MIN,
        "beta_ceil": BETA_MAX,
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
        "crlb_floor_computed_M4096": 0.00781,   # sqrt(0.25/4096)
        "crlb_floor_computed_M8192": 0.00552,   # sqrt(0.25/8192)
        "crlb_floor_computed_M16384": 0.00390,  # sqrt(0.25/16384)
        "crlb_formula_reference": "sigma_min = sqrt(0.25/M) binomial-CLT",
        "discriminator_reachability": True,
        "calibration_check": "adaptive_with_discriminator_gate",
        "M_SWEEP_expansion_criterion": "MM_TENTATIVE_criterion_c_verify_other_M",
        "parent_v2_landing": "fc47b1bb_recall_1.000_M8192_3seed",
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
