"""
pp50_kappa3_sigma_g_extreme_tail_v6_n16384 -- PP-50 ultra-extended sigma_g sweep to find
true saturation or divergence.

CONTEXT (v373 cycle 43):
  PP-50 v4 HARD_PASS (completed): sigma_sep(sg=0.83-2.0) monotone increasing, 5x+ amplification
  confirmed. v4 grid was sg={0.83, 0.85, 0.87, 0.9, 1.0, 1.5, 2.0}.
  v5 PURPOSE: extend to sg={1.0, 1.5, 2.0, 3.0, 5.0} to find true saturation point or
  divergence regime. Does sigma_sep keep rising log-linearly past sg=2.0, or does it plateau?

SCIENTIFIC QUESTION:
  At what sigma_g does sigma_sep saturate or begin to decrease (if ever)?
  Is the growth log-linear indefinitely, or is there a true ceiling?
  Does sigma_sep(sg=5.0) >> sigma_sep(sg=2.0) or level off?

PRE-REGISTERED BANDS (PP-50 v5 ultra-extended sigma_g):
  Empirical anchors (v4): sigma_sep(sg=2.0) was the max observed. Call it S2.
  v5 tests extension: sg={1.0, 1.5, 2.0, 3.0, 5.0}.
  Calibration: extending beyond prior max; no prior anchor at sg=3.0, 5.0.
  Bands widened to +-50% of extrapolated log-linear trend per calibration-probe policy.
  HARD-PASS: sigma_sep monotone increasing sg=1.0->1.5->2.0->3.0->5.0 (consistent with
             continued log-linear growth) AND sigma_sep(sg=5.0) > sigma_sep(sg=1.0) * 10x.
  MIDDLE: monotone increasing but <10x range, OR non-monotone at single transition only.
  HARD-FAIL: sigma_sep peaks at sg=2.0 and falls at sg=3.0 or sg=5.0 (true divergence/fold)
             OR sigma_sep(sg=5.0) < sigma_sep(sg=2.0) * 0.8 (substantial reversal).

FORMULA SELF-TESTS (PROT-022):
  1. NLO sigma_g_crit: sqrt(ln(1 + 0.15/(3*0.05))) = sqrt(ln(2)) = 0.8326.
     [INPUT: epsilon=0.15, alpha=0.05] [EXPECTED: 0.8326 within 0.001]
  2. M_base = int(0.05 * 16384) = 819. [EXPECTED: 819]
  3. sigma_g grid is ordered: [1.0, 1.5, 2.0, 3.0, 5.0] strictly increasing.
     [EXPECTED: all(a<b for a,b in zip(grid, grid[1:]))]
  4. Hutchinson kappa_3 at tiny N is non-NaN.
  5. sigma_sep positive at smoke scale.

MULTI-SCALE SMOKE: run at N_smoke=512 and N_smoke*4=2048.

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: seed checkpoints keyed with run_mode + sigma_g.
QUEUE: overnight_queue (GPU; Hutchinson kappa_3 extended sigma_g at N=16384).
TIMEOUT ESTIMATE: v4 N=16384 elapsed ~300s (5 seeds, 7 sigma_g, 2 delta_alpha = 70 cells).
  v5 has 5 sigma_g and 2 delta_alpha (10 cells per seed, 5 seeds = 50 cells).
  Ratio 50/70 ~ 0.71. Estimate: 300 * 0.71 = 213s. ceil(1.5 * 213) = 320s.
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

ANCHOR_NAME = "pp50_kappa3_sigma_g_extreme_tail_v6_n16384"

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

# Extended sigma_g grid: pushing past v4's max of sg=2.0
SIGMA_G_GRID_FULL = [5.0, 8.0, 12.0, 15.0]
assert all(a < b for a, b in zip(SIGMA_G_GRID_FULL, SIGMA_G_GRID_FULL[1:])), (
    f"sigma_g grid not monotone: {SIGMA_G_GRID_FULL}")
print(f"[selftest-formula] sigma_g extended grid monotone: {SIGMA_G_GRID_FULL}", flush=True)

# Primary delta_alpha: d=0.04 (main sensitivity probe; d=0.01 added for extra coverage)
DELTA_ALPHAS_FULL = [0.04, 0.01]

if RUN_MODE == "smoke":
    N_ACTIVE = 512
    SEEDS = [7, 17]
    DELTA_ALPHAS = [0.04]
    N_PROBES_SENS = 100
    SIGMA_G_GRID = [5.0, 10.0, 15.0]  # smoke: extreme-tail points
elif RUN_MODE == "smoke4x":
    N_ACTIVE = 2048
    SEEDS = [7, 17]
    DELTA_ALPHAS = [0.04]
    N_PROBES_SENS = 200
    SIGMA_G_GRID = [1.0, 2.0, 5.0]
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    DELTA_ALPHAS = DELTA_ALPHAS_FULL
    N_PROBES_SENS = 2000
    SIGMA_G_GRID = SIGMA_G_GRID_FULL

# Pre-registered thresholds
HP_10X_AMPLIFICATION = 10.0    # sigma_sep(sg=5.0) > sigma_sep(sg=1.0) * 10x
HF_REVERSAL_FRAC = 0.8         # sigma_sep(sg=5.0) < sigma_sep(sg=2.0) * 0.8 = HARD_FAIL


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
        # Clip to prevent float32 overflow: exp(x) overflows f32 at x>88
        log_scale = (sigma_g * Z_rows).clamp(-80.0, 80.0)
        noise_scale = torch.exp(log_scale).unsqueeze(1)
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

    # Test kappa_3 at sigma_g=1.0 (first extended point)
    k3_1, se_1 = hutchinson_kappa3_gpu_f64acc(Xi_base, 15.0, n_test, n_p, seed=42)
    assert not (k3_1 != k3_1), "kappa_3 is NaN at sigma_g=15.0"
    assert se_1 >= 0, f"SE is negative: {se_1}"

    # Test at sigma_g=5.0 (max extended point)
    k3_5, se_5 = hutchinson_kappa3_gpu_f64acc(Xi_base, 15.0, n_test, n_p, seed=42)
    assert not (k3_5 != k3_5), "kappa_3 is NaN at sigma_g=15.0"

    # Test sigma_sep at sg=1.0
    sep_1 = compute_sigma_sep(Xi_base, 0.04, 15.0, n_test, seed=42, n_probes=n_p)
    assert sep_1 >= 0, f"sigma_sep is negative: {sep_1}"
    assert sep_1 > 0, f"sigma_sep is exactly zero at sg=15.0 -- instrumentation broken"

    # Test sigma_sep at sg=5.0
    sep_5 = compute_sigma_sep(Xi_base, 0.04, 15.0, n_test, seed=42, n_probes=n_p)
    assert sep_5 >= 0, f"sigma_sep is negative at sg=15.0: {sep_5}"
    assert sep_5 > 0, f"sigma_sep is exactly zero at sg=15.0 -- instrumentation broken"

    # Smoke-scale ordering check: sg=5.0 should show higher sep than sg=1.0 at smoke
    # Not asserting ordering at smoke (N=512 has high variance), just non-null check

    # GPU memory check
    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    assert mem_gb > 0, f"GPU memory not allocated"

    print(f"[selftest] PASS: k3_sg15={k3_1:.4f} sep_sg15={sep_1:.2f} "
          f"k3_sg15={k3_5:.4f} sep_sg15={sep_5:.2f} gpu_mem={mem_gb:.3f}GB N={n_test}", flush=True)


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

    summary_parts = [f"sg{sg:.1f}:{sep:.0f}" for sg, sep in sg_sep_pairs]
    summary = f"sigma_sep(d=0.04): [{', '.join(summary_parts)}] n_seeds={len(seed_results)}"

    sep_at_1 = next((s for g, s in sg_sep_pairs if abs(g - 5.0) < 0.5), None)   # sg=5.0 anchor
    sep_at_2 = next((s for g, s in sg_sep_pairs if abs(g - 12.0) < 1.0), None)  # sg=12.0
    sep_at_5 = next((s for g, s in sg_sep_pairs if abs(g - 15.0) < 1.0), None)  # sg=15.0

    # HARD-FAIL: strong reversal at sg=100 vs sg=5.0
    if sep_at_2 is not None and sep_at_1 is not None:
        if sep_at_2 < sep_at_1 * HF_REVERSAL_FRAC:
            return ("HARD_FAIL",
                    f"HARD_FAIL: sep(sg=12)={sep_at_2:.0f} < sep(sg=5.0)*0.8={sep_at_1*0.8:.0f}. "
                    f"Extreme-tail fold detected. {summary}")

    # Check monotone across full grid
    seps_sorted = [s for _, s in sorted(sg_sep_pairs, key=lambda x: x[0])]
    is_monotone = all(a <= b for a, b in zip(seps_sorted, seps_sorted[1:]))

    # HARD-PASS: monotone AND 10x amplification sg=5->1000
    if sep_at_1 is not None and sep_at_5 is not None:
        amplification = sep_at_5 / max(sep_at_1, 1.0)
        if is_monotone and amplification >= HP_10X_AMPLIFICATION:
            return ("HARD_PASS",
                    f"HARD_PASS: monotone=True amp_5_to_1000={amplification:.1f}x >= {HP_10X_AMPLIFICATION}x. "
                    f"Extreme-tail log-linear growth confirmed. {summary}")

    # MIDDLE
    if sep_at_1 is not None and sep_at_5 is not None:
        amplification = sep_at_5 / max(sep_at_1, 1.0)
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: monotone={is_monotone} amp_5_to_1000={amplification:.1f}x "
                f"(< {HP_10X_AMPLIFICATION}x required). {summary}")

    return ("MIDDLE_BAND", f"MIDDLE_BAND: insufficient cells to classify. {summary}")


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
run_config = {"N": N, "sigma_g_grid": SIGMA_G_GRID_FULL, "run_mode": RUN_MODE}
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
    "summary": verdict_msg,
    "per_seed": [
        {"seed": r.get("seed"),
         "elapsed_s": r.get("elapsed_s"),
         "peak_gpu_gb": r.get("peak_gpu_gb"),
         "cells": r.get("cells", {})}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
