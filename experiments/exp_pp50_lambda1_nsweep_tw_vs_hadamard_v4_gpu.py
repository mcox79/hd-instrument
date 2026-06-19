"""
pp50_lambda1_nsweep_tw_vs_hadamard_v4_gpu -- PP-50 transition-zone discriminator, lambda_1 observable (GPU).

ROUTING: notes/research_pp50_metric_reformulation_lambda1_power_iteration_2026-06-04.md
  (Research's replacement for the numerically-unstable sigma_sep ratio that Exp-Dev flagged: v2+v3 were
   non-monotone because the isochoric kappa_3 ratio has a near-zero denominator k3_base).
SUPERSEDES v2 + v3 (sigma_sep ratio confounded by metric instability, NOT by the TW-vs-Hadamard physics).

CAPABILITY QUESTION:
  The PP-50 capacity transition zone is wider than the free-probability sharp-boundary prediction. Two
  mechanisms: (A) Tracy-Widom soft-edge ~ N^(-2/3) (vanishes at large N -> N-parameterized envelope) vs
  (B) non-self-averaging Hadamard term ~ N^0 (constant -> N-independent envelope). DECISIVE TEST:
  measure the largest eigenvalue lambda_1 of the noisy Wishart W = Xi_noisy Xi_noisy^T / N, sweep N, fit
  the scaling exponent beta of the lambda_1 FLUCTUATION across seeds. beta ~ 2/3 => Tracy-Widom; beta ~ 0
  => Hadamard. lambda_1 is the CANONICAL Tracy-Widom edge observable -- no near-zero-denominator blowup.

OBSERVABLES (Research lambda_1 spec):
  PRIMARY  (Research-recommended): std(lambda_1_noisy across seeds) at each N. Direct TW scale parameter;
           needs no clean baseline. ~ N^(-2/3) under TW, ~ N^0 under Hadamard.
  SECONDARY (robust): mean(edge_correction) = mean(lambda_1_noisy - lambda_1_clean across seeds) at each N.
           Stronger N-dependence; requires a sigma_g=0 baseline. Reported alongside; verdict uses primary.

NOISE MODEL (Research lambda_1 spec; additive-on-patterns, formula-matched per kappa3-NLO 2x drill):
  g_per_pattern ~ N(0, I_N), shape (M, N); Xi_noisy = Xi + sigma_g * g_per_pattern.

LAMBDA_1: power iteration (float64, 20 iters) on the M x M Gram W = Xi_noisy @ Xi_noisy.T / N. The M x M
  Gram shares all nonzero eigenvalues with the N x N W = Xi_noisy.T Xi_noisy / N, so lambda_1 is identical
  and M=int(0.05 N) << N makes it cheap even at N=16384.

PRE-REGISTERED BANDS (on beta of PRIMARY std observable; unchanged from prior PP-50):
  HARD-PASS (Tracy-Widom): beta_std in [0.50, 0.80] (within ~25% of 2/3); N-parameterized envelope needed.
  HARD-PASS (Hadamard):    beta_std in [-0.15, 0.15] (within ~15% of 0); N-independent envelope correct.
  MIDDLE: beta_std in [0.15, 0.50] (intermediate; refutes both clean classes).
  HARD-FAIL: beta_std < -0.15 (fluctuation INCREASES with N) -- refutes both clean classes.

FORMULA SELF-TESTS (PROT-022):
  1. N^(-2/3) ratio: (8192/1024)^(-2/3) = 8^(-2/3) = 0.25. [within 1e-6]
  2. power iteration on diag([5,2,1]) recovers lambda_1 = 5. [within 1e-6]
  3. additive noise is mean-preserving: E[Xi_noisy] ~ Xi (||mean(g)|| small at large M*N).

PROT-018: NO _nN suffix (N is swept); grid declared {1024,2048,4096,8192,16384}.
PROT-021: seed checkpoints keyed run_mode + seed (each seed stores per-N lambda_1_noisy + lambda_1_clean).
QUEUE: overnight_queue (GPU). TIMEOUT: 7200s (Research est <5 min wall; generous floor). ASCII-only stdout.
GPU TEMPLATE: assert cuda + device='cuda' + batched matmul.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import torch, torch.cuda
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB", flush=True)
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "pp50_lambda1_nsweep_tw_vs_hadamard_v4_gpu"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
SIGMA_G = 0.80               # just below sigma_g_crit = sqrt(ln2) = 0.8326 (signal present)
POWER_ITERS = 20
# Bands (on beta of primary std observable)
TW_LO, TW_HI = 0.50, 0.80
HAD_LO, HAD_HI = -0.15, 0.15
MID_LO, MID_HI = 0.15, 0.50
HF_BETA = -0.15

if RUN_MODE == "smoke":
    N_GRID = [256, 512, 1024]
    SEEDS = [1, 2, 3, 4, 5, 6]
else:
    N_GRID = [1024, 2048, 4096, 8192, 16384]
    # 12 seeds: std-of-lambda_1 across seeds needs enough samples to be a stable observable
    SEEDS = [7, 17, 23, 31, 41, 53, 61, 73, 83, 97, 101, 113]


def power_iteration(W, num_iters=POWER_ITERS, gen=None):
    """Largest eigenvalue of symmetric PSD W (float64) via power iteration."""
    n = W.shape[0]
    Wd = W.to(torch.float64)
    v = torch.randn(n, generator=gen, device=DEVICE, dtype=torch.float64)
    v = v / v.norm()
    for _ in range(num_iters):
        v = Wd @ v
        v = v / (v.norm() + 1e-30)
    return float((Wd @ v).norm())


def lambda1_at(n, sigma_g, seed):
    """Return (lambda_1_noisy, lambda_1_clean) for the M x M Gram of Xi_noisy / Xi at dim n."""
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed * 100003 + n % 9973)
    M = max(2, int(round(ALPHA * n)))
    Xi = (torch.randint(0, 2, (M, n), generator=gen, device=DEVICE).float() * 2 - 1)   # bipolar base
    g = torch.randn(M, n, generator=gen, device=DEVICE)                                # additive-on-patterns
    Xi_noisy = Xi + sigma_g * g
    W_noisy = (Xi_noisy @ Xi_noisy.t()) / n      # (M,M) Gram; shares nonzero spectrum with (N,N) Wishart
    W_clean = (Xi @ Xi.t()) / n
    l_noisy = power_iteration(W_noisy, gen=gen)
    l_clean = power_iteration(W_clean, gen=gen)
    return l_noisy, l_clean


def fit_beta(ns, ys):
    import numpy as np
    x = np.log(np.array(ns, dtype=np.float64))
    y = np.log(np.clip(np.array(ys, dtype=np.float64), 1e-12, None))
    slope, _ = np.polyfit(x, y, 1)
    return float(-slope)    # observable ~ N^(-beta) -> beta = -slope


def _selftest():
    assert abs((8192 / 1024) ** (-2.0 / 3.0) - 0.25) < 1e-6
    W = torch.diag(torch.tensor([5.0, 2.0, 1.0], device=DEVICE))
    l1 = power_iteration(W, num_iters=50,
                         gen=torch.Generator(device=DEVICE).manual_seed(0))
    assert abs(l1 - 5.0) < 1e-6, f"power_iteration diag lambda_1={l1}"
    gen = torch.Generator(device=DEVICE).manual_seed(1)
    g = torch.randn(200, 4000, generator=gen, device=DEVICE)
    assert float(g.mean().abs()) < 0.05, "additive noise not ~zero-mean"
    ln, lc = lambda1_at(256, SIGMA_G, 7)
    assert ln > 0 and lc > 0 and torch.cuda.memory_allocated(0) > 0
    print(f"[selftest] PASS: N^-2/3=0.25 power_iter(diag)={l1:.6f} lambda1_noisy={ln:.4f} clean={lc:.4f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    cells = []
    for n in N_GRID:
        l_noisy, l_clean = lambda1_at(n, SIGMA_G, seed)
        cells.append({"N": n, "lambda1_noisy": l_noisy, "lambda1_clean": l_clean,
                      "edge_correction": l_noisy - l_clean})
        print(f"  [seed={seed} N={n}] lambda1_noisy={l_noisy:.5f} clean={l_clean:.5f} "
              f"edge={l_noisy - l_clean:.5f}", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "run_mode": RUN_MODE, "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> tuple:
    import numpy as np
    if not results:
        return ("HARD_FAIL", "No valid results.")
    std_obs, mean_shift = {}, {}
    for n in N_GRID:
        noisy = [c["lambda1_noisy"] for r in results for c in r.get("cells", []) if c["N"] == n]
        edge = [c["edge_correction"] for r in results for c in r.get("cells", []) if c["N"] == n]
        std_obs[n] = float(np.std(noisy)) if len(noisy) > 1 else 0.0
        mean_shift[n] = float(np.mean(edge)) if edge else 0.0
    std_list = [std_obs[n] for n in N_GRID]
    shift_list = [abs(mean_shift[n]) for n in N_GRID]
    if min(std_list) <= 0:
        return ("HARD_FAIL", f"HARD_FAIL: zero std(lambda_1) at some N (degenerate). std={[round(s,5) for s in std_list]}")
    beta_std = fit_beta(N_GRID, std_list)
    beta_shift = fit_beta(N_GRID, shift_list) if min(shift_list) > 0 else float('nan')
    summary = (f"beta_std={beta_std:.3f} beta_shift={beta_shift:.3f} "
               f"std(l1)=" + " ".join(f"N{n}:{std_obs[n]:.4f}" for n in N_GRID) +
               " | mean_edge=" + " ".join(f"N{n}:{mean_shift[n]:.4f}" for n in N_GRID))

    if beta_std < HF_BETA:
        return ("HARD_FAIL", f"HARD_FAIL: std(lambda_1) increases with N (beta<{HF_BETA}); refutes both clean classes. {summary}")
    if TW_LO <= beta_std <= TW_HI:
        return ("HARD_PASS", f"HARD_PASS: Tracy-Widom (beta_std in [{TW_LO},{TW_HI}] ~ 2/3); N-parameterized envelope needed. {summary}")
    if HAD_LO <= beta_std <= HAD_HI:
        return ("HARD_PASS", f"HARD_PASS: Hadamard (beta_std in [{HAD_LO},{HAD_HI}] ~ 0); N-independent envelope correct. {summary}")
    if MID_LO <= beta_std <= MID_HI:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: intermediate beta_std in [{MID_LO},{MID_HI}]; refutes both clean classes. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: beta_std outside named bands ({beta_std:.3f}). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N_grid={N_GRID} mode={RUN_MODE} seeds={SEEDS} "
      f"sigma_g={SIGMA_G} alpha={ALPHA} power_iters={POWER_ITERS}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N_grid": N_GRID, "run_mode": RUN_MODE, "sigma_g": SIGMA_G, "alpha": ALPHA, "obs": "lambda1"}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep = time.time()
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_total = time.time() - t_sweep
peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.001, f"GPU util check FAIL: {peak_mem_gb:.3f}GB"
metrics = {
    "anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg,
    "N_grid": N_GRID, "run_mode": RUN_MODE, "sigma_g": SIGMA_G, "alpha": ALPHA,
    "n_seeds": len(SEEDS), "power_iters": POWER_ITERS, "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", []),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
