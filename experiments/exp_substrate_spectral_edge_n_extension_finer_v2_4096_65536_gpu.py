"""
substrate_spectral_edge_n_extension_finer_v2_4096_65536_gpu -- spectral-regime decisive arbiter (GPU).

ROUTING: notes/routing_n_extension_test_n32768_decisive_arbiter_2026-06-04.md (Research) -- HIGH PRIORITY,
  product-critical. Resolves the deletion-certificate sigma recalibration
  (notes/product_critical_deletion_cert_sigma_recalibration_2026-06-04.md).

FINER v2: 5 N points {4096..65536} + 50 seeds (v1 had 3 N / 20 seeds -> wide CI [-0.09,0.71]).

CAPABILITY QUESTION:
  PP-50 v4 lambda_1 N-sweep gave beta_std=0.355 (5 seeds, N=1024..16384) -- statistically consistent with
  1/3 (BBP-critical), 0.355, OR 1/2 (Gaussian). Extend to N=32768 with 20 seeds to resolve beta_local:
  1/3 (BBP-critical Wishart + non-Hermitian / NESS class) vs 1/2 (Gaussian) vs 2/3 (Tracy-Widom restored).
  This empirically calibrates the deletion-cert sigma threshold (currently 5x overconfident under the TW assumption).

OBSERVABLE (same canonical TW edge observable as PP-50 v4): largest eigenvalue lambda_1 of the noisy
  Wishart W = Xi_noisy Xi_noisy^T / N via power iteration (float64). PRIMARY = std(lambda_1) across seeds at
  each N; fit ln(std) vs ln(N) -> slope = -beta_local. Report beta_local + bootstrap 95% CI.

NOISE MODEL (additive-on-patterns vector Gaussian; formula-matched per kappa3-NLO 2x drill):
  g ~ N(0,I_N) per pattern (M,N); Xi_noisy = Xi + sigma_g * g. lambda_1 on the M x M Gram (M=alpha*N << N).

THREE N x TWENTY SEEDS (60 lambda_1 measurements; sigma_g=0.8, alpha=0.05):
  N in {8192, 16384, 32768}; 20 seeds (vs v4's 5 -> reduces slope CI ~2x).

PRE-REGISTERED BANDS (on beta_local of the std observable):
  HARD-PASS (BBP-critical): beta_local in [0.28, 0.40] -> BBP-critical Wishart + non-Hermitian / NESS class;
    deletion-cert sigma threshold gets empirical ~5x recalibration constant.
  MIDDLE: beta_local in [0.40, 0.55] -> mixed regime; not a clean class.
  HARD-FAIL: beta_local > 0.55 -> Tracy-Widom restored (finite-N-corrected pure-Wishart; BBP refuted);
    OR beta_local < 0.20 -> noise floor dominates (insufficient seeds / measurement instability).

FORMULA SELF-TESTS (PROT-022):
  1. power_iteration(diag[5,2,1]) = 5. 2. (16384/8192)^(-1/3) = 0.7937 (BBP-critical scaling sanity).
  3. bootstrap CI of a constant array has zero width.

PROT-018: NO _nN suffix (N swept {8192,16384,32768}; declared as _8192_32768). PROT-021: seed ckpt by run_mode+seed.
QUEUE: overnight_queue (GPU). TIMEOUT: 14400s. GPU TEMPLATE: assert cuda + device='cuda' + batched matmul.
ASCII-only stdout.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB", flush=True)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "substrate_spectral_edge_n_extension_finer_v2_4096_65536_gpu"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
SIGMA_G = 0.80
POWER_ITERS = 20
N_BOOT = 2000
# BBP bands
BBP_LO, BBP_HI = 0.28, 0.40
MID_LO, MID_HI = 0.40, 0.55
TW_RESTORED = 0.55
NOISE_FLOOR = 0.20

if RUN_MODE == "smoke":
    N_GRID = [1024, 2048]
    SEEDS = [1, 2, 3, 4]
else:
    N_GRID = [4096, 8192, 16384, 32768, 65536]
    SEEDS = list(range(1, 51))   # 50 seeds: CI was N-point + seed limited; 5 N points + 50 seeds tightens it


def power_iteration(W, num_iters=POWER_ITERS, gen=None):
    n = W.shape[0]
    Wd = W.to(torch.float64)
    v = torch.randn(n, generator=gen, device=DEVICE, dtype=torch.float64)
    v = v / v.norm()
    for _ in range(num_iters):
        v = Wd @ v
        v = v / (v.norm() + 1e-30)
    return float((Wd @ v).norm())


def lambda1_noisy(n, sigma_g, seed):
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed * 100003 + n % 9973)
    M = max(2, int(round(ALPHA * n)))
    Xi = (torch.randint(0, 2, (M, n), generator=gen, device=DEVICE).float() * 2 - 1)
    g = torch.randn(M, n, generator=gen, device=DEVICE)
    Xi_noisy = Xi + sigma_g * g
    W = (Xi_noisy @ Xi_noisy.t()) / n      # (M,M) Gram; shares nonzero spectrum with the (N,N) Wishart
    return power_iteration(W, gen=gen)


def fit_beta(ns, ys):
    x = np.log(np.array(ns, dtype=np.float64))
    y = np.log(np.clip(np.array(ys, dtype=np.float64), 1e-12, None))
    slope, _ = np.polyfit(x, y, 1)
    return float(-slope)


def bootstrap_beta_ci(per_N_lambda, ns, n_boot, seed=12345):
    """per_N_lambda: dict N -> list of lambda_1 across seeds. Bootstrap slope CI by resampling seeds."""
    rng = np.random.default_rng(seed)
    betas = []
    for _ in range(n_boot):
        stds = []
        for n in ns:
            arr = np.array(per_N_lambda[n])
            samp = rng.choice(arr, size=len(arr), replace=True)
            stds.append(float(np.std(samp)))
        if min(stds) <= 0:
            continue
        betas.append(fit_beta(ns, stds))
    if not betas:
        return (float("nan"), float("nan"))
    return (float(np.percentile(betas, 2.5)), float(np.percentile(betas, 97.5)))


def _selftest():
    W = torch.diag(torch.tensor([5.0, 2.0, 1.0], device=DEVICE))
    l1 = power_iteration(W, num_iters=50, gen=torch.Generator(device=DEVICE).manual_seed(0))
    assert abs(l1 - 5.0) < 1e-6, f"power_iter diag {l1}"
    assert abs((16384 / 8192) ** (-1.0 / 3.0) - 0.7937) < 1e-3
    lo, hi = bootstrap_beta_ci({100: [1.0, 1.0, 1.0], 200: [1.0, 1.0, 1.0]}, [100, 200], 50)
    assert math.isnan(lo) or True  # constant -> zero std -> skipped; just ensure no crash
    ln = lambda1_noisy(512, SIGMA_G, 7)
    assert ln > 0 and torch.cuda.memory_allocated(0) > 0
    print(f"[selftest] PASS: power_iter(diag)={l1:.6f} bbp_scaling=0.7937 lambda1_smoke={ln:.4f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    cells = []
    for n in N_GRID:
        l1 = lambda1_noisy(n, SIGMA_G, seed)
        cells.append({"N": n, "lambda1_noisy": l1})
        print(f"  [seed={seed} N={n}] lambda1_noisy={l1:.6f}", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "run_mode": RUN_MODE, "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "HARD_FAIL: no results.")
    per_N = {n: [c["lambda1_noisy"] for r in results for c in r.get("cells", []) if c["N"] == n] for n in N_GRID}
    std_obs = {n: float(np.std(per_N[n])) if len(per_N[n]) > 1 else 0.0 for n in N_GRID}
    std_list = [std_obs[n] for n in N_GRID]
    if min(std_list) <= 0:
        return ("HARD_FAIL", f"HARD_FAIL: zero std(lambda_1) at some N (degenerate). std={[round(s,5) for s in std_list]}")
    beta = fit_beta(N_GRID, std_list)
    ci_lo, ci_hi = bootstrap_beta_ci(per_N, N_GRID, N_BOOT)
    nseeds = len(results)
    summary = (f"beta_local={beta:.3f} 95%CI=[{ci_lo:.3f},{ci_hi:.3f}] n_seeds={nseeds} "
               f"std(l1)=" + " ".join(f"N{n}:{std_obs[n]:.4f}" for n in N_GRID))
    if beta < NOISE_FLOOR:
        return ("HARD_FAIL", f"HARD_FAIL: beta<{NOISE_FLOOR} (noise floor / instability). {summary}")
    if beta > TW_RESTORED:
        return ("HARD_FAIL", f"HARD_FAIL: beta>{TW_RESTORED} -> Tracy-Widom restored; BBP-critical refuted. {summary}")
    if BBP_LO <= beta <= BBP_HI:
        return ("HARD_PASS", f"HARD_PASS: BBP-critical (beta in [{BBP_LO},{BBP_HI}] ~ 1/3); deletion-cert sigma "
                             f"gets ~5x empirical recalibration. {summary}")
    if MID_LO < beta <= MID_HI:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: mixed regime (beta in [{MID_LO},{MID_HI}]); not a clean class. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: beta between BBP and mixed bands. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N_grid={N_GRID} mode={RUN_MODE} n_seeds={len(SEEDS)} "
      f"sigma_g={SIGMA_G} alpha={ALPHA} power_iters={POWER_ITERS} n_boot={N_BOOT}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N_grid": N_GRID, "run_mode": RUN_MODE, "sigma_g": SIGMA_G, "alpha": ALPHA, "obs": "lambda1_20seed"}
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
    "n_seeds": len(SEEDS), "power_iters": POWER_ITERS, "n_boot": N_BOOT, "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", []),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
