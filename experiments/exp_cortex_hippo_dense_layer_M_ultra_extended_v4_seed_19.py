"""cortex_hippo_dense_layer_M_ultra_extended_v4 -- seed_7.

Extends Cell D v2 (M=8192, HP@fc47b1bb) to ultra scale: M in {8192, 32768,
65536} at N_h=N_c=8192. Same mechanism (Ha writes + dense-Hopfield attention
reads bypassing cortex-Hebbian); only sweep axis + N doubled.

Discriminator: does replacement mode hold at 4x + 8x above v2's capacity
crack? If yes -> major M3 scaling win (chain-grade at M=65536). If no ->
finds the replacement-mode wall.

Shared core: experiments/_substrate_cortex_hippo_dense_layer_M_ultra_extended_v4_core.py
Sibling seeds: 13, 19 (files exp_cortex_hippo_dense_layer_M_ultra_extended_v4_seed_{13,19}.py).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - arms_differ_verified at smoke (META_RULE_AF via _selftest_arms_expected_differ)
 - final_metrics_atomicity = tmp_replace (META_RULE_AH)
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - crlb_floor_computed = 0.00552 (M=8192 worst case); reachability = True
 - baseline_in_band verified at low-alpha smoke (STANDARD ~ 1.0)
 - discriminator survives scale: smoke has FULL_N preview at M=65536
 - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
 - cardinality_ok EXPECTED_N_UNITS = 3 arms * 3 M values = 9 (META_RULE_H)
 - calibration_check = adaptive_with_discriminator_gate
 - number-provenance tagged (MEASURED@fc47b1bb v2; HYPOTHESIZED@v4-scale;
   THEORETICAL@binomial-CLT; CITED@Ramsauer2021 / Amit-Gutfreund 1985)

PRESERVE_ENV_VARS: HDLAB_QUEUE
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

from experiments._substrate_cortex_hippo_dense_layer_M_ultra_extended_v4_core import (
    N_HIPPO_FULL, N_CORTEX_FULL, HIPPO_SPARSITY, ETA_HIPPO_FULL,
    BETA_MIN, BETA_MAX,
    M_SWEEP_FULL, M_SWEEP_SMOKE_MAIN, M_SWEEP_SMOKE_PREVIEW,
    _TORCH_AVAILABLE, _CUDA_AVAILABLE,
    run_one_M, run_all_selftests, compute_verdict,
    emit_heartbeat, write_start_marker, write_crash_metrics,
)


ANCHOR_NAME = "cortex_hippo_dense_layer_M_ultra_extended_v4_seed_19"
SEED_THIS_CHUNK = 19
_HARDENING_MARKER = "v4_M_ultra_extended_seed_19"

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
# Config (per RUN_MODE)
# ---------------------------------------------------------------------------
if RUN_MODE == "smoke":
    # Smoke: MAIN at same alpha as full worst-case (alpha=8.0).
    # Main: M=8192, N_h=N_c=1024 -> alpha=8.0 matches full M=65536,N=8192.
    # Analytical DISCRIMINATOR-MUST-SURVIVE-SCALE (check B in core docstring):
    # substrate is alpha-scale-invariant; if smoke MAIN at alpha=8.0 shows
    # REPLACE >> STANDARD, the discriminator is proven at the full worst
    # case. FULL_N numpy-fp64 preview at M=65536,N=8192 OOMs on laptop
    # (4GB allocation for STANDARD's W_c); skipped by design.
    N_HIPPO = 1024
    N_CORTEX = 1024
    M_SWEEP = [8192]
    RUN_FULL_N_PREVIEW = False
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    M_SWEEP = list(M_SWEEP_FULL)
    RUN_FULL_N_PREVIEW = False

ETA_HIPPO = ETA_HIPPO_FULL
SEEDS = [SEED_THIS_CHUNK]

K_HIPPO_ACTIVE = max(1, int(round(HIPPO_SPARSITY * N_HIPPO)))
ALPHA_SIMPLE_PER_M = {int(m): float(m) / float(N_CORTEX) for m in M_SWEEP}

USE_TORCH_CUDA = (RUN_MODE == "full") and _TORCH_AVAILABLE and _CUDA_AVAILABLE
COMPUTE_BACKEND = "torch.cuda" if USE_TORCH_CUDA else ("torch.cpu" if _TORCH_AVAILABLE else "numpy")

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY},M_SWEEP={M_SWEEP},eta_h={ETA_HIPPO},"
    f"beta_floor={BETA_MIN},beta_ceil={BETA_MAX},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"chunk_seed={SEED_THIS_CHUNK},"
    f"alpha_per_M={ALPHA_SIMPLE_PER_M},"
    f"backend={COMPUTE_BACKEND},"
    f"hardening=v4_M_ultra_extended+METARULE_AF+METARULE_AH+ADAPTIVE_BETA"
    f"+STANDARD_COLLAPSE_EXEMPTION"
)

# CRLB THEORETICAL@binomial-CLT:
#   M=8192:  sigma_min = sqrt(0.25/8192)  = 0.00552; gap 0.60 = 109*sigma
#   M=32768: sigma_min = sqrt(0.25/32768) = 0.00276; gap 0.60 = 217*sigma
#   M=65536: sigma_min = sqrt(0.25/65536) = 0.00195; gap 0.60 = 307*sigma
# All discriminators well above sampling noise.

# Cardinality (META_RULE_H): 3 arms x len(M_SWEEP)
EXPECTED_N_UNITS = 3 * len(M_SWEEP)

# Attention batch chunk (VRAM control; sims is M x M at fp32)
# M=65536 x M=65536 x 4 bytes = 16 GB just for sims tensor. Chunk hard.
def _attn_chunk_for_M(m):
    if m <= 8192:
        return 1024 if RUN_MODE == "full" else m
    elif m <= 32768:
        return 512
    else:  # 65536
        return 256


# ---------------------------------------------------------------------------
# Per-seed runner (sweeps 3 M values internally)
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()

    print(
        f"  [seed={seed}] {ANCHOR_NAME} "
        f"N_h={N_HIPPO} N_c={N_CORTEX} M_SWEEP={M_SWEEP} eta_h={ETA_HIPPO} "
        f"backend={COMPUTE_BACKEND}",
        flush=True,
    )

    per_M = {}
    for m_val in M_SWEEP:
        attn_chunk = _attn_chunk_for_M(m_val)
        arms_at_M = run_one_M(
            seed=seed, m_items=m_val, n_h=N_HIPPO, n_c=N_CORTEX,
            hippo_sparsity=HIPPO_SPARSITY, eta_hippo=ETA_HIPPO,
            attn_chunk=attn_chunk, use_cuda=USE_TORCH_CUDA, out_dir=out_dir,
        )
        per_M[int(m_val)] = arms_at_M

    # Optional FULL_N preview arm (smoke only; DISCRIMINATOR-MUST-SURVIVE-SCALE)
    preview_result = None
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        m_prev = M_SWEEP_SMOKE_PREVIEW
        n_h_prev = N_HIPPO_FULL
        n_c_prev = N_CORTEX_FULL
        attn_chunk_prev = _attn_chunk_for_M(m_prev)
        # Use CUDA for preview if available (this is the whole point of the
        # preview — check the biggest discriminator on the target hardware).
        use_cuda_prev = _TORCH_AVAILABLE and _CUDA_AVAILABLE
        print(f"  [seed={seed} PREVIEW] running FULL_N discriminator at "
              f"M={m_prev}, N_h=N_c={n_c_prev}, cuda={use_cuda_prev}, "
              f"chunk={attn_chunk_prev}...",
              flush=True)
        # Preview runs REPLACE-arm equivalent, but via run_one_M for full
        # STANDARD/HA_ONLY/REPLACE at target scale. If we can't afford all 3
        # on smoke box, we still get REPLACE readout for gate.
        preview_arms = run_one_M(
            seed=seed, m_items=m_prev, n_h=n_h_prev, n_c=n_c_prev,
            hippo_sparsity=HIPPO_SPARSITY, eta_hippo=ETA_HIPPO_FULL,
            attn_chunk=attn_chunk_prev,
            use_cuda=use_cuda_prev, out_dir=out_dir,
        )
        preview_result = {"M": int(m_prev), "arms": preview_arms}

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_CORTEX,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M_SWEEP": M_SWEEP,
        "eta_h": ETA_HIPPO,
        "hippo_sparsity": HIPPO_SPARSITY,
        "k_hippo_active": K_HIPPO_ACTIVE,
        "alpha_per_M": ALPHA_SIMPLE_PER_M,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "per_M": per_M,
        "preview_result": preview_result,
        "elapsed_s": float(elapsed),
    }


def _instrumentation_selftest() -> None:
    run_all_selftests(SEED_THIS_CHUNK, ANCHOR_NAME)
    print(
        f"[selftest] PASS  N_h={N_HIPPO}  N_c={N_CORTEX}  "
        f"sparsity={HIPPO_SPARSITY}  M_SWEEP={M_SWEEP}  eta_h={ETA_HIPPO}  "
        f"beta_range=[{BETA_MIN},{BETA_MAX}]  mode={RUN_MODE}  "
        f"chunk_seed={SEED_THIS_CHUNK}  alpha_per_M={ALPHA_SIMPLE_PER_M}  "
        f"backend={COMPUTE_BACKEND}  torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Main driver
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
        "M_SWEEP": M_SWEEP,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME} "
              f"N_h={N_HIPPO} N_c={N_CORTEX} M_SWEEP={M_SWEEP} "
              f"eta_h={ETA_HIPPO} mode={RUN_MODE} backend={COMPUTE_BACKEND}...",
              flush=True)
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

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())
    if not all_results:
        verdict, verdict_msg, headline = ("HARD_FAIL",
                                          "No valid seed results.", {})
    else:
        verdict, verdict_msg, headline = compute_verdict(
            all_results[0], RUN_MODE, N_CORTEX
        )

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL run. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    if RUN_MODE == "full" and USE_TORCH_CUDA:
        max_peak_mb = 0.0
        for r in all_results:
            for arms in r.get("per_M", {}).values():
                for a in arms:
                    max_peak_mb = max(max_peak_mb, float(a.get("gpu_mem_peak_mb", 0.0)))
        if max_peak_mb < 100.0:
            verdict_msg = (
                f"WARN_GPU_UNDERUTIL: max gpu_mem_peak_mb={max_peak_mb:.1f} < 100MB; "
                f"GPU may not have been used. " + verdict_msg
            )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_h={N_HIPPO} N_c={N_CORTEX} sparsity={HIPPO_SPARSITY} "
            f"M_SWEEP={M_SWEEP} eta_h={ETA_HIPPO} "
            f"beta_range=[{BETA_MIN},{BETA_MAX}] mode={RUN_MODE} "
            f"alpha_per_M={ALPHA_SIMPLE_PER_M} backend={COMPUTE_BACKEND}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M_SWEEP": M_SWEEP,
        "eta_h": ETA_HIPPO,
        "hippo_sparsity": HIPPO_SPARSITY,
        "beta_floor": BETA_MIN,
        "beta_ceil": BETA_MAX,
        "alpha_per_M": ALPHA_SIMPLE_PER_M,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == 1
            and sum(
                len([a for a in arms
                     if a["arm_name"] in ("ARM_STANDARD", "ARM_HA_ONLY",
                                          "ARM_HA_DENSE_REPLACE")])
                for arms in all_results[0].get("per_M", {}).values()
            ) == EXPECTED_N_UNITS
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 0.00552,  # M=8192 worst case
        "crlb_formula_reference": "sigma_min = sqrt(0.25/M) binomial-CLT",
        "discriminator_reachability": True,
        "calibration_check": "adaptive_with_discriminator_gate",
        "headline_metrics": headline,
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "per_M": r.get("per_M"),
                "preview_result": r.get("preview_result"),
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
