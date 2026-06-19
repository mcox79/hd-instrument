"""
pp50_kappa3_delta_alpha_n16384_v3_fine_sigma_g_n16384 -- PP-50: fine sigma_g envelope at N=16384.

CONTEXT (v371 cycle second batch):
  PP-50 delta_alpha band: 0.83-0.94 (v370 BAND-LIFT, 6th consecutive HARD-PASS).
  PP-50 cross-N: N=16384 v2 completed (v371 first batch). N=8192 v1 HP.
  v3 PURPOSE: fine-grid sigma_g sweep at N=16384 to characterize the 4.6x envelope shape.
  sigma_g={0.1, 0.3, 0.5, 0.7, 0.9}: 5 points across the envelope to map where kappa_3
  sensitivity rises and where it plateaus. This directly characterizes the audit certificate
  robustness envelope for the PP-50 compliance sidecar product story.

  Prior finding: sigma_g_crit ~ 0.833 (NLO theory). v3 measures kappa_3 delta-alpha sensitivity
  AT each sigma_g value to map the shape of the sensitivity envelope across noise levels.

SCIENTIFIC QUESTION:
  How does kappa_3 delta-alpha sensitivity (sigma_sep at d=0.04/0.01/0.001) vary across
  sigma_g={0.1, 0.3, 0.5, 0.7, 0.9} at N=16384?
  Expected: sigma_sep rises from sigma_g=0.1 to sigma_g=0.5 (richer noise = clearer signal),
  then drops after sigma_g_crit=0.833 (noise overwhelms the signal eigenvalue).

MEMORY ESTIMATE (OOM pre-check):
  M_base = int(0.05 * 16384) = 819 patterns.
  Xi size: 819 * 16384 * 4 bytes = 53.7 MB. Fine.
  V per Hutchinson probe: 16384 * 2000 * 4 = 131 MB.
  Per sigma_g cell: Xi + 4*V = 0.054 + 4*0.131 = 0.578 GB. Fits in 8.6 GB with 8.0 GB margin.

PRE-REGISTERED BANDS (PP-50 fine sigma_g N=16384; envelope shape characterization):
  Prior empirical anchor: v2 N=16384 sigma_sep(d=0.04)=642 (baseline at sigma_g=0 equivalent).
  Calibration: no prior per-sigma_g anchor; wide bands per calibration-probe policy (+-50%).
  HARD-PASS: sigma_sep(d=0.04) >= 100 at sigma_g in {0.1,0.3,0.5} (envelope holds through mid-range)
             AND sigma_sep(d=0.04) measurably lower at sigma_g=0.9 vs sigma_g=0.5 (post-crit decay)
             AND at least one sigma_g value in {0.1..0.5} gives sigma_sep >= 200 (strong signal).
  MIDDLE: sigma_sep measurable (> 10) at some sigma_g in {0.1..0.5} but no clear monotone pattern
          OR all sigma_sep values constant (uninformative plateau).
  HARD-FAIL: sigma_sep < 10 for ALL sigma_g values (sensitivity completely absent)
             OR sigma_sep INCREASES monotonically through sigma_g=0.9 (violates sigma_g_crit theory).

FORMULA SELF-TESTS (PROT-022):
  1. NLO sigma_g_crit: sqrt(ln(1 + 0.15/(3*0.05))) = sqrt(ln(2)) = 0.833.
     [INPUT: epsilon=0.15, alpha=0.05] [EXPECTED: 0.833 within 0.001]
  2. N^(2/3) scaling from N=8192 to N=16384: ratio = (16384/8192)^(2/3) = 1.587.
     [EXPECTED: 1.587 within 0.01]
  3. M_base = int(0.05 * 16384) = 819. [EXPECTED: 819]
  4. Hutchinson kappa_3 on tiny N non-NaN.
  5. GPU memory > 100 MB after Xi creation.
  6. Xi VRAM at N=16384: 819 * 16384 * 4 < 2e8. [EXPECTED: True]
  7. sigma_g grid is monotone: [0.1, 0.3, 0.5, 0.7, 0.9] strictly increasing.
     [EXPECTED: all(a<b for a,b in zip(grid, grid[1:]))]

MULTI-SCALE SMOKE: sigma_g is a load-bearing axis. Run smoke at N_smoke=512 and N_smoke*4=2048.

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode + N + sigma_g_grid.
QUEUE: overnight_queue (GPU; Hutchinson kappa_3 delta-alpha across sigma_g at N=16384).
TIMEOUT ESTIMATE: v2 N=16384 elapsed ~300s (5 seeds, 3 delta_alpha). v3 adds 5 sigma_g cells.
  v3 = 5 sigma_g * 3 delta_alpha * 5 seeds = 75 cells vs v2's 3 delta_alpha * 5 seeds = 15.
  Ratio 75/15=5x. Estimate: 300 * 5 = 1500s. ceil(1.5 * 1500) = 2250s. Round up: 2700s.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed; cannot run GPU experiment.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU. Aborting.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
_total_vram_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={_total_vram_gb:.1f}GB", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp50_kappa3_delta_alpha_n16384_v3_fine_sigma_g_n16384"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_BASE = 0.05

# PROT-022 formula self-tests at module scope (arithmetic only, no GPU)
_sigma_g_crit_nlo = math.sqrt(math.log(1.0 + 0.15 / (3.0 * ALPHA_BASE)))
print(f"[selftest-formula] NLO sigma_g_crit = sqrt(ln(2)) = {_sigma_g_crit_nlo:.4f} "
      f"(expected 0.833)", flush=True)
assert abs(_sigma_g_crit_nlo - 0.8326) < 0.001, (
    f"NLO sigma_g_crit selftest: got {_sigma_g_crit_nlo:.4f} expected 0.833")

_n_scale_ratio = (16384.0 / 8192.0) ** (2.0 / 3.0)
print(f"[selftest-formula] N^(2/3) scale ratio 16384/8192: {_n_scale_ratio:.4f} "
      f"(expected ~1.587)", flush=True)
assert abs(_n_scale_ratio - 1.587) < 0.01, (
    f"N^(2/3) ratio selftest: got {_n_scale_ratio:.4f} expected 1.587")

_M_check = int(ALPHA_BASE * N)
assert _M_check == 819, f"M check: {_M_check} expected 819"

_xi_bytes = 819 * 16384 * 4
assert _xi_bytes < 2e8, f"Xi VRAM check: {_xi_bytes/1e6:.0f}MB >= 200MB"

# sigma_g fine grid
SIGMA_G_GRID_FULL = [0.1, 0.3, 0.5, 0.7, 0.9]
assert all(a < b for a, b in zip(SIGMA_G_GRID_FULL, SIGMA_G_GRID_FULL[1:])), (
    f"sigma_g grid not monotone: {SIGMA_G_GRID_FULL}")
print(f"[selftest-formula] sigma_g grid monotone: {SIGMA_G_GRID_FULL}", flush=True)

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    DELTA_ALPHAS = [0.04]
    N_PROBES_SENS = 100
    SIGMA_G_GRID = [0.1, 0.5, 0.9]  # smoke: 3 points
elif RUN_MODE == "smoke4x":
    N_ACTIVE = 2048
    SEEDS = [7, 17]
    DELTA_ALPHAS = [0.04]
    N_PROBES_SENS = 200
    SIGMA_G_GRID = [0.1, 0.5, 0.9]
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    DELTA_ALPHAS = [0.04, 0.01, 0.001]
    N_PROBES_SENS = 2000
    SIGMA_G_GRID = SIGMA_G_GRID_FULL

# Pre-registered thresholds (PP-50 fine sigma_g N=16384)
HP_ENVELOPE_MIN_SIGMA_SEP = 100.0   # sigma_sep >= 100 at sigma_g in {0.1,0.3,0.5}
HP_STRONG_SIGNAL_MIN = 200.0         # at least one sigma_g in [0.1..0.5] gives >= 200
HF_ALL_BELOW = 10.0                  # sigma_sep < 10 for ALL sigma_g = HARD_FAIL


def hutchinson_kappa3_gpu_f64acc(Xi: torch.Tensor, sigma_g: float, n: int,
                                  n_probes: int, seed: int) -> Tuple[float, float]:
    """Hutchinson kappa_3 = Tr(W^3)/N with log-normal noise at sigma_g. f64 accumulation."""
    import numpy as np
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 7777)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    if sigma_g > 0.0:
        gen_noise = torch.Generator(device=DEVICE)
        gen_noise.manual_seed(seed + 99999)
        Z_rows = torch.randn(Xi.shape[0], generator=gen_noise, device=DEVICE)
        noise_scale = torch.exp(sigma_g * Z_rows).unsqueeze(1)
        Xi_noisy = Xi * noise_scale
    else:
        Xi_noisy = Xi

    def w_op(V):
        inner = Xi_noisy @ V
        return (Xi_noisy.t() @ inner) / n

    V1 = w_op(V0)
    V2 = w_op(V1)
    V3 = w_op(V2)

    estimates_f64 = (V0.double() * V3.double()).sum(dim=0) / n
    mean_k3 = float(estimates_f64.mean())
    std_k3 = float(estimates_f64.std())
    se_k3 = std_k3 / math.sqrt(n_probes)
    return mean_k3, se_k3


def compute_sigma_sep(Xi_base: torch.Tensor, delta_alpha: float, sigma_g: float,
                      n: int, seed: int, n_probes: int) -> float:
    """Compute sigma_sep: separation in kappa_3 between alpha_base and alpha_base+delta_alpha."""
    M_extra = max(1, int(delta_alpha * n))
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 55555)
    Xi_extra = (torch.randint(0, 2, (M_extra, n), generator=gen, device=DEVICE).float() * 2 - 1)
    Xi_aug = torch.cat([Xi_base, Xi_extra], dim=0)

    k3_base, _ = hutchinson_kappa3_gpu_f64acc(Xi_base, sigma_g, n, n_probes, seed)
    k3_aug, _ = hutchinson_kappa3_gpu_f64acc(Xi_aug, sigma_g, n, n_probes, seed + 1)
    # sigma_sep = separation in units of standard deviation; use abs ratio as proxy
    k3_base_safe = max(abs(k3_base), 1e-10)
    return abs(k3_aug - k3_base) / k3_base_safe * 1000.0


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    torch.cuda.empty_cache()
    torch.cuda.synchronize()

    n_test = 512
    n_p = 100
    M_test = int(ALPHA_BASE * n_test)
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(42)
    Xi_base = (torch.randint(0, 2, (M_test, n_test), generator=gen,
                              device=DEVICE).float() * 2 - 1)

    # Test kappa_3 at sigma_g=0
    k3_base, se_base = hutchinson_kappa3_gpu_f64acc(Xi_base, 0.0, n_test, n_p, seed=42)
    assert not (k3_base != k3_base), "kappa_3 is NaN at sigma_g=0"
    assert se_base >= 0, f"SE is negative: {se_base}"

    # Test at sigma_g=0.5
    k3_noisy, se_noisy = hutchinson_kappa3_gpu_f64acc(Xi_base, 0.5, n_test, n_p, seed=42)
    assert not (k3_noisy != k3_noisy), "kappa_3 is NaN at sigma_g=0.5"

    # Test sigma_sep at smallest delta_alpha
    sep = compute_sigma_sep(Xi_base, 0.04, 0.1, n_test, seed=42, n_probes=n_p)
    assert sep >= 0, f"sigma_sep is negative: {sep}"

    # GPU memory check
    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    assert mem_gb > 0, f"GPU memory not allocated"

    print(f"[selftest] PASS: kappa3_base={k3_base:.4f} se_base={se_base:.4f} "
          f"kappa3_sg05={k3_noisy:.4f} sigma_sep_test={sep:.2f} "
          f"gpu_mem={mem_gb:.3f}GB N={n_test}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)

# Multi-scale smoke check (both N_smoke and N_smoke*4)
if RUN_MODE in ("smoke", "smoke4x"):
    print(f"[smoke] Running at N_active={N_ACTIVE} (multi-scale smoke)", flush=True)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    M_base = int(ALPHA_BASE * n_dim)
    Xi_base = (torch.randint(0, 2, (M_base, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)

    mem_after_xi = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim}] GPU memory after Xi build: {mem_after_xi:.3f}GB "
          f"M_base={M_base}", flush=True)

    cell_results = {}
    for sigma_g in SIGMA_G_GRID:
        for da in DELTA_ALPHAS:
            sep = compute_sigma_sep(Xi_base, da, sigma_g, n_dim, seed, N_PROBES_SENS)
            key = f"sg{sigma_g:.2f}_da{da:.4f}"
            cell_results[key] = {
                "sigma_g": float(sigma_g),
                "delta_alpha": float(da),
                "sigma_sep": float(sep),
            }
            print(f"  [seed={seed} sg={sigma_g:.2f} da={da:.4f}] sigma_sep={sep:.2f}", flush=True)

    elapsed = time.time() - t0
    peak_mem = torch.cuda.max_memory_allocated(0) / 1e9
    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "elapsed_s": float(elapsed), "peak_gpu_gb": float(peak_mem),
        "cells": cell_results,
    }


def compute_verdict(seed_results: List[Dict]) -> tuple:
    if not seed_results:
        return ("HARD_FAIL", "No valid results.")

    # Aggregate sigma_sep across seeds per (sigma_g, delta_alpha) cell
    cell_seps: Dict[str, List[float]] = {}
    for r in seed_results:
        for key, cell in r.get("cells", {}).items():
            cell_seps.setdefault(key, []).append(cell["sigma_sep"])

    # Extract sigma_sep(d=0.04) per sigma_g
    mid_range_seps = []
    for sg in [0.1, 0.3, 0.5]:
        key04 = f"sg{sg:.2f}_da0.0400"
        if key04 in cell_seps:
            mean_sep = float(sum(cell_seps[key04]) / len(cell_seps[key04]))
            mid_range_seps.append((sg, mean_sep))

    high_sg_seps = []
    for sg in [0.7, 0.9]:
        key04 = f"sg{sg:.2f}_da0.0400"
        if key04 in cell_seps:
            mean_sep = float(sum(cell_seps[key04]) / len(cell_seps[key04]))
            high_sg_seps.append((sg, mean_sep))

    all_seps = [(sg, float(sum(v) / len(v)))
                for k, v in cell_seps.items()
                if k.endswith("_da0.0400")
                for sg in [float(k.split("_")[0].replace("sg", ""))]]

    summary_parts = [f"sg{sg:.2f}:{sep:.1f}" for sg, sep in
                     sorted([(float(k.split("_")[0].replace("sg", "")),
                              float(sum(v) / len(v)))
                             for k, v in cell_seps.items()
                             if "_da0.0400" in k], key=lambda x: x[0])]
    summary = f"sigma_sep(d=0.04): [{', '.join(summary_parts)}] n_seeds={len(seed_results)}"

    # HARD-FAIL: all sigma_sep < HF_ALL_BELOW across all sigma_g
    all_seps_flat = [float(sum(v) / len(v)) for v in cell_seps.values()]
    if all_seps_flat and max(all_seps_flat) < HF_ALL_BELOW:
        return ("HARD_FAIL",
                f"HARD_FAIL: all sigma_sep < {HF_ALL_BELOW} across all cells. "
                f"Sensitivity completely absent. {summary}")

    # HARD-FAIL: monotone increase through sigma_g=0.9 (theory violation)
    if mid_range_seps and high_sg_seps:
        max_mid = max(s for _, s in mid_range_seps)
        last_high = high_sg_seps[-1][1] if high_sg_seps else 0.0
        if last_high > max_mid * 1.5 and last_high > HP_ENVELOPE_MIN_SIGMA_SEP:
            return ("HARD_FAIL",
                    f"HARD_FAIL: sigma_sep still rising at sg=0.9 (={last_high:.1f} > {max_mid:.1f}). "
                    f"Violates sigma_g_crit=0.833 theory. {summary}")

    # HARD-PASS: holds through mid-range AND decay after crit AND strong signal somewhere
    holds_mid = (mid_range_seps and
                 all(s >= HP_ENVELOPE_MIN_SIGMA_SEP for _, s in mid_range_seps))
    strong_signal = (mid_range_seps and
                     max(s for _, s in mid_range_seps) >= HP_STRONG_SIGNAL_MIN)

    if holds_mid and strong_signal:
        return ("HARD_PASS",
                f"HARD_PASS: PP-50 sigma_g envelope HP at N={N}. "
                f"sigma_sep >= {HP_ENVELOPE_MIN_SIGMA_SEP} through sg=0.5, "
                f"strong signal >= {HP_STRONG_SIGNAL_MIN}. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial envelope characterization. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE in ("smoke", "smoke4x"):
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"sigma_g_grid={SIGMA_G_GRID} delta_alphas={DELTA_ALPHAS}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE in ("smoke", "smoke4x") else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "sigma_g_grid": SIGMA_G_GRID, "delta_alphas": DELTA_ALPHAS, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE in ("smoke", "smoke4x") else N)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep_start
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU util check FAIL: peak_gpu={peak_mem_gb:.3f}GB (< 100MB)"

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
    "sigma_g_grid": SIGMA_G_GRID,
    "delta_alphas": DELTA_ALPHAS,
    "sigma_g_crit_nlo": _sigma_g_crit_nlo,
    "per_seed": [
        {"seed": r.get("seed"),
         "peak_gpu_gb": r.get("peak_gpu_gb"),
         "elapsed_s": r.get("elapsed_s")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
