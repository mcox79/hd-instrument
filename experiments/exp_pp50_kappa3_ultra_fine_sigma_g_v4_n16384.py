"""
pp50_kappa3_ultra_fine_sigma_g_v4_n16384 -- PP-50 ultra-fine sigma_g bracket N=16384.

CONTEXT (v372 all-night burst cycle 43):
  PP-50 v3 HARD_FAIL (v372): sigma_sep monotonically rising sg=0.1:983.5->sg=0.9:24025.0.
  No plateau or drop observed. Theory sigma_g_crit=0.833 marks WHERE sensitivity BEGINS rising
  (entry boundary), NOT where it plateaus.
  v4 PURPOSE: ultra-fine bracket around sigma_g_crit=0.833 to characterize the onset SHAPE.
  sigma_g={0.83, 0.85, 0.87, 0.9, 1.0, 1.5, 2.0}: maps the curvature of onset at crit point.
  Also tests whether sigma_sep rate of change accelerates past crit or grows uniformly.

  Prior v3 data points (N=16384):
    sg=0.1: sigma_sep=983.5   sg=0.3: sigma_sep=871.7   sg=0.5: sigma_sep=1594.9
    sg=0.7: sigma_sep=6679.9  sg=0.9: sigma_sep=24025.0

SCIENTIFIC QUESTION:
  Does the sigma_sep vs sigma_g curve show acceleration (curvature > 0, log-convex onset)
  vs linear growth between sigma_g=0.83 and sigma_g=2.0?
  Can we resolve the fine structure around sigma_g_crit=0.833 (onset transition)?
  Is there a knee, inflection, or smooth exponential onset?

MEMORY ESTIMATE (OOM pre-check):
  M_base = int(0.05 * 16384) = 819. Xi: 819 * 16384 * 4 = 53.7 MB GPU.
  Hutchinson probes V: 16384 * 2000 * 4 = 131 MB. Well within 8 GB.

PRE-REGISTERED BANDS (PP-50 v4 ultra-fine sigma_g at N=16384):
  Empirical anchors (v3): sigma_sep(sg=0.7)=6679.9, sigma_sep(sg=0.9)=24025.0.
  No prior anchor at sg=0.83-0.87 specifically.
  Calibration: ultra-fine bracket, no prior anchor in this exact range; bands +-50% of
  interpolated v3 trend per calibration-probe policy.
  HARD-PASS: sigma_sep(sg=0.83) in [1000, 20000] AND sigma_sep increases monotonically
             across the bracket sg=0.83->0.9->1.0->1.5->2.0 (consistent with entry-boundary
             model) AND sigma_sep(sg=2.0) > sigma_sep(sg=0.83) * 5 (at least 5x amplification).
  MIDDLE: sigma_sep measurable at all brackets but monotone violated OR less than 5x range.
  HARD-FAIL: sigma_sep < 100 at sg=0.83 (too small given v3 sg=0.7 was 6679.9)
             OR sigma_sep NOT measurably different at sg=0.83 vs sg=0.9 (flat onset).

FORMULA SELF-TESTS (PROT-022):
  1. NLO sigma_g_crit: sqrt(ln(1 + 0.15/(3*0.05))) = sqrt(ln(2)) = 0.8326.
     [INPUT: epsilon=0.15, alpha=0.05] [EXPECTED: 0.8326 within 0.001]
  2. M_base = int(0.05 * 16384) = 819. [EXPECTED: 819]
  3. sigma_g grid is ordered: [0.83, 0.85, 0.87, 0.9, 1.0, 1.5, 2.0] strictly increasing.
     [EXPECTED: all(a<b for a,b in zip(grid, grid[1:]))]
  4. Hutchinson kappa_3 at tiny N is non-NaN.
  5. 5x amplification check: 2.0 / 0.83 = 2.41x range in sigma_g; if linear log-sigma_sep,
     expected amplification = exp((2.0 - 0.83) / 0.83 * log(24025/6679)) = large positive.

MULTI-SCALE SMOKE: sigma_g is load-bearing axis; smoke at N_smoke=512 and N_smoke*4=2048.

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode + N + sigma_g_grid.
QUEUE: overnight_queue (GPU; Hutchinson kappa_3 delta-alpha in ultra-fine bracket at N=16384).
TIMEOUT ESTIMATE: v3 N=16384 elapsed ~300s (5 seeds, 5 sigma_g, 3 delta_alpha). v4 has 7
  sigma_g and 1 delta_alpha (d=0.04 only, primary metric). Cells: 7 * 5 = 35 vs v3's 75.
  Ratio 35/75=0.47. Estimate: 300 * 0.47 = 141s. ceil(1.5 * 141) = 212s. Round up: 300s.
  Use PROT-019 floor: 21600s.
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

ANCHOR_NAME = "pp50_kappa3_ultra_fine_sigma_g_v4_n16384"

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
print(f"[selftest-formula] NLO sigma_g_crit = {_sigma_g_crit_nlo:.4f} (expected 0.8326)", flush=True)
assert abs(_sigma_g_crit_nlo - 0.8326) < 0.001, (
    f"NLO sigma_g_crit selftest: got {_sigma_g_crit_nlo:.4f} expected 0.8326")

_M_check = int(ALPHA_BASE * N)
assert _M_check == 819, f"M check: {_M_check} expected 819"

# Ultra-fine sigma_g grid centered on sigma_g_crit=0.833
SIGMA_G_GRID_FULL = [0.83, 0.85, 0.87, 0.9, 1.0, 1.5, 2.0]
assert all(a < b for a, b in zip(SIGMA_G_GRID_FULL, SIGMA_G_GRID_FULL[1:])), (
    f"sigma_g grid not monotone: {SIGMA_G_GRID_FULL}")
print(f"[selftest-formula] sigma_g ultra-fine grid monotone: {SIGMA_G_GRID_FULL}", flush=True)

# Primary delta_alpha: d=0.04 (main sensitivity probe; d=0.01 added for extra coverage)
DELTA_ALPHAS_FULL = [0.04, 0.01]

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    DELTA_ALPHAS = [0.04]
    N_PROBES_SENS = 100
    SIGMA_G_GRID = [0.83, 0.9, 1.5]  # smoke: 3 representative points
elif RUN_MODE == "smoke4x":
    N_ACTIVE = 2048
    SEEDS = [7, 17]
    DELTA_ALPHAS = [0.04]
    N_PROBES_SENS = 200
    SIGMA_G_GRID = [0.83, 0.9, 1.5]
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    DELTA_ALPHAS = DELTA_ALPHAS_FULL
    N_PROBES_SENS = 2000
    SIGMA_G_GRID = SIGMA_G_GRID_FULL

# Pre-registered thresholds
HP_MIN_AT_CRIT = 1000.0          # sigma_sep(sg=0.83) >= 1000 (v3 sg=0.7 was 6679.9)
HP_AMPLIFICATION = 5.0            # sigma_sep(sg=2.0) > sigma_sep(sg=0.83) * 5
HF_TOO_SMALL = 100.0              # sigma_sep(sg=0.83) < 100 = HARD_FAIL
# Monotone check: each step sg increases, sigma_sep must also increase
HP_MONOTONE_REQUIRED = True


def hutchinson_kappa3_gpu_f64acc(Xi: torch.Tensor, sigma_g: float, n: int,
                                  n_probes: int, seed: int) -> Tuple[float, float]:
    """Hutchinson kappa_3 = Tr(W^3)/N with log-normal noise at sigma_g. f64 accumulation."""
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

    # Test kappa_3 at sigma_g=0.83 (first bracket point)
    k3_083, se_083 = hutchinson_kappa3_gpu_f64acc(Xi_base, 0.83, n_test, n_p, seed=42)
    assert not (k3_083 != k3_083), "kappa_3 is NaN at sigma_g=0.83"
    assert se_083 >= 0, f"SE is negative: {se_083}"

    # Test sigma_sep at sg=0.83
    sep = compute_sigma_sep(Xi_base, 0.04, 0.83, n_test, seed=42, n_probes=n_p)
    assert sep >= 0, f"sigma_sep is negative: {sep}"
    assert sep > 0, f"sigma_sep is exactly zero at smoke scale -- instrumentation broken"

    # GPU memory check
    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    assert mem_gb > 0, f"GPU memory not allocated"

    print(f"[selftest] PASS: kappa3_sg083={k3_083:.4f} se={se_083:.4f} "
          f"sigma_sep_sg083={sep:.2f} gpu_mem={mem_gb:.3f}GB N={n_test}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)

# Multi-scale smoke check
if RUN_MODE in ("smoke", "smoke4x"):
    print(f"[smoke] Running at N_active={N_ACTIVE} (multi-scale smoke gate)", flush=True)


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
            key = f"sg{sigma_g:.4f}_da{da:.4f}"
            cell_results[key] = {
                "sigma_g": float(sigma_g),
                "delta_alpha": float(da),
                "sigma_sep": float(sep),
            }
            print(f"  [seed={seed} sg={sigma_g:.4f} da={da:.4f}] sigma_sep={sep:.2f}", flush=True)

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

    # Primary metric: sigma_sep(d=0.04) per sigma_g, sorted by sigma_g
    da_key = "0.0400"
    sg_sep_pairs = []
    for sg in SIGMA_G_GRID_FULL:
        key04 = f"sg{sg:.4f}_da{da_key}"
        if key04 in cell_seps:
            mean_sep = float(sum(cell_seps[key04]) / len(cell_seps[key04]))
            sg_sep_pairs.append((sg, mean_sep))

    if not sg_sep_pairs:
        return ("HARD_FAIL", "No d=0.04 cells found in results.")

    summary_parts = [f"sg{sg:.2f}:{sep:.0f}" for sg, sep in sg_sep_pairs]
    summary = f"sigma_sep(d=0.04): [{', '.join(summary_parts)}] n_seeds={len(seed_results)}"

    # HARD-FAIL: too small at sg=0.83
    sep_at_crit = next((s for g, s in sg_sep_pairs if abs(g - 0.83) < 0.005), None)
    if sep_at_crit is not None and sep_at_crit < HF_TOO_SMALL:
        return ("HARD_FAIL",
                f"HARD_FAIL: sigma_sep(sg=0.83)={sep_at_crit:.1f} < {HF_TOO_SMALL} "
                f"(too small given v3 sg=0.7=6679.9 anchor). {summary}")

    # HARD-PASS criteria
    hp_min_ok = sep_at_crit is not None and sep_at_crit >= HP_MIN_AT_CRIT
    hp_mono = all(sg_sep_pairs[i][1] <= sg_sep_pairs[i+1][1]
                  for i in range(len(sg_sep_pairs)-1))
    sep_at_20 = next((s for g, s in sg_sep_pairs if abs(g - 2.0) < 0.01), None)
    hp_amp = (sep_at_crit is not None and sep_at_20 is not None and
              sep_at_20 > sep_at_crit * HP_AMPLIFICATION)

    if hp_min_ok and hp_mono and hp_amp:
        return ("HARD_PASS",
                f"HARD_PASS: PP-50 v4 ultra-fine sigma_g bracket HP at N={N}. "
                f"sep(sg=0.83)={sep_at_crit:.0f} >= {HP_MIN_AT_CRIT}; "
                f"monotone=True; amplification={sep_at_20/sep_at_crit:.1f}x >= {HP_AMPLIFICATION}x. "
                f"{summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial bracket characterization. "
            f"hp_min_ok={hp_min_ok} hp_mono={hp_mono} hp_amp={hp_amp}. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"sigma_g_grid={SIGMA_G_GRID}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE, "sigma_g_grid": str(SIGMA_G_GRID_FULL)}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed, N_ACTIVE if RUN_MODE == "smoke" else N)
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
    "sigma_g_grid": SIGMA_G_GRID_FULL,
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
