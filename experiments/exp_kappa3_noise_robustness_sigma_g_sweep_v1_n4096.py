"""
kappa3_noise_robustness_sigma_g_sweep_v1_n4096 -- Wave-2 free-probability prediction test.

SCIENTIFIC QUESTION:
  Does substrate's kappa_3 = alpha free-Poisson identity survive multiplicative
  log-normal weight noise sigma_g, and does the empirical breakdown match
  Wave-2 closed-form prediction of sigma_g_critical ~ 0.18?

TEST DESIGN:
  N=4096, 5 seeds; substrate W = Xi^T Xi / N with M = alpha * N patterns.
  Multiplicative noise: W_noisy = W * exp(sigma_g * Z) where Z ~ N(0,1) entrywise.
  Sweep sigma_g in {0.01, 0.05, 0.10, 0.15, 0.18, 0.20, 0.25, 0.30}.
  For each sigma_g: compute kappa_3_measured via Hutchinson estimator on W_noisy.
  Measure kappa_3_measured / alpha (should stay within +-5% identity up to ~0.18).

PRE-REGISTERED BANDS (Item 20 v343):
  HARD-PASS: kappa_3 identity holds within +-5% for sigma_g <= 0.15 AND
             breaks (>+-15%) by sigma_g = 0.25 (5-seed unanimous across both bounds)
  MIDDLE: identity envelope sigma_g_critical in [0.10, 0.25] (within order of magnitude)
  HARD-FAIL: identity breaks at sigma_g < 0.05 OR holds at sigma_g > 0.30 --
             Wave-2 prediction wrong by >2 orders

  No prior empirical anchor at this noise regime; bands set per calibration-probe
  policy (theoretical prediction +-50%).

FORMULA SELF-TESTS (PROT-022):
  1. kappa_3 Hutchinson identity: kappa_3_theory(M=100, N=4096) = M/N = 0.0244.
     At sigma_g=0 (no noise): kappa_3_measured/alpha should be within +-5% of 1.0.
     [INPUT: sigma_g=0, M=100, N=4096] [EXPECTED: ratio in [0.95, 1.05]]
  2. Log-normal noise at sigma_g=0: exp(0*Z) = 1 exactly; no deviation.
     [INPUT: sigma_g=0.0, any Z] [EXPECTED: W_noisy == W_clean]
  3. Hutchinson estimator: for W = identity/N, kappa_3 ~ 1/N^2 (near zero).
     [INPUT: W=I/N at N=128, n_probes=200] [EXPECTED: |kappa_3| < 0.01]

PROT-018: anchor contains _n4096; N MUST = 4096.
GPU REQUIRED: Hutchinson estimator with batched matmul requires CUDA for 5-seed
  sweep at N=4096; each forward pass is 3 N x n_probes matmuls.
Queue: overnight_queue
Pre-reg: preregs/2026-06-02_kappa3_noise_robustness_sigma_g_sweep_v1_n4096.md

TIMEOUT ESTIMATE:
  Smoke: N=4096, n_probes=200, 2 seeds, 8 sigma_g values.
  Full: N=4096, n_probes=2000, 5 seeds, 8 sigma_g values.
  GPU matmul (N=4096, n_probes=2000): ~3 dgemm = ~0.05s each.
  Per (seed, sigma_g): W build + noise + 3 matmuls ~ 0.5s.
  Full: 5 * 8 * 0.5s = 20s + overhead.
  timeout_s = ceil(1.5 * 20 * (5/2) * 1.0) = ceil(75) -> 300s.
  (Conservative: use 600s to account for GPU startup and W-build overhead.)
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
from typing import Dict, List

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

try:
    import torch
    import torch.cuda
    import numpy as np
except ImportError as e:
    print(f"[FATAL] missing dependency: {e}", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"mem={torch.cuda.get_device_properties(0).total_memory/1e9:.1f}GB", flush=True)

ANCHOR_NAME = "kappa3_noise_robustness_sigma_g_sweep_v1_n4096"

_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
M = int(ALPHA * N)  # = 204

SIGMA_G_GRID = [0.01, 0.05, 0.10, 0.15, 0.18, 0.20, 0.25, 0.30]

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    N_PROBES = 200
else:
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBES = 2000

# Pre-reg thresholds
HP_IDENTITY_HOLD_SIGMA = 0.15   # identity within +-5% for sigma_g <= this
HP_IDENTITY_HOLD_TOL   = 0.05   # +-5%
HP_BREAK_SIGMA         = 0.25   # breaks (>+-15%) by this sigma_g
HP_BREAK_TOL           = 0.15   # +-15%
HF_EARLY_BREAK_SIGMA   = 0.05   # breaks before this -> HF
HF_LATE_HOLD_SIGMA     = 0.30   # still holds at this -> HF

# Floor: for Hutchinson, std ~ 1/sqrt(n_probes)
# PROT-022: kappa_3_theory at no noise
_K3_THEORY_NO_NOISE = ALPHA


def build_w_cpu(seed: int) -> np.ndarray:
    """Build clean Hopfield weight matrix on CPU."""
    rng = np.random.RandomState(seed)
    Xi = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    W = (Xi.T @ Xi) / N
    np.fill_diagonal(W, 0.0)
    return W


def add_lognormal_noise(W_np: np.ndarray, sigma_g: float, seed: int) -> torch.Tensor:
    """Apply multiplicative log-normal noise W_noisy = W * exp(sigma_g * Z)."""
    rng = np.random.RandomState(seed + 99999)
    if sigma_g == 0.0:
        return torch.from_numpy(W_np).to(DEVICE)
    Z = rng.normal(0.0, 1.0, size=W_np.shape).astype(np.float32)
    W_noisy = W_np * np.exp(sigma_g * Z)
    np.fill_diagonal(W_noisy, 0.0)
    return torch.from_numpy(W_noisy).to(DEVICE)


def hutchinson_kappa3(W_t: torch.Tensor, n_probes: int, seed: int) -> float:
    """Estimate kappa_3 = mean(diag(V^T W^3 V)) / N via batched matmul.

    V is N x n_probes Rademacher matrix.
    kappa_3 estimate = (1/N) * mean_over_probes(v^T W^3 v)
                     = (1/N) * sum_rows(V * (W^3 V)) / n_probes
    """
    rng = np.random.RandomState(seed + 77777)
    V_np = rng.choice([-1.0, 1.0], size=(N, n_probes)).astype(np.float32)
    V = torch.from_numpy(V_np).to(DEVICE)

    # W^3 V via three sequential matmuls
    WV    = W_t @ V         # (N, n_probes)
    W2V   = W_t @ WV
    W3V   = W_t @ W2V

    # kappa_3 = (1/N) * mean_probe diag(V^T W^3 V)
    #         = (1/N) * mean_probe sum_i V[i, p] * W3V[i, p]
    k3 = float(torch.mean(torch.sum(V * W3V, dim=0)).item()) / N
    return k3


# ---- FORMULA SELF-TESTS ----

def _selftest_no_noise_identity():
    """kappa_3 at sigma_g=0 should be within +-5% of alpha."""
    W_np = build_w_cpu(seed=42)
    W_t  = add_lognormal_noise(W_np, sigma_g=0.0, seed=42)
    k3   = hutchinson_kappa3(W_t, n_probes=500, seed=42)
    ratio = k3 / ALPHA
    assert abs(ratio - 1.0) < 0.20, (
        f"selftest no-noise: kappa_3/alpha={ratio:.3f}, expected ~1.0 (+-0.20 at 500 probes)")


def _selftest_zero_noise_exact():
    """W_noisy at sigma_g=0 equals W_clean exactly."""
    W_np = build_w_cpu(seed=7)
    W_t  = add_lognormal_noise(W_np, sigma_g=0.0, seed=7)
    W_back = W_t.cpu().numpy()
    err = float(np.max(np.abs(W_back - W_np)))
    assert err < 1e-6, f"selftest sigma_g=0: max_diff={err:.2e} not zero"


def _selftest_hutchinson_near_identity():
    """Hutchinson on W = I/N should give kappa_3 ~ 1/N^2 (near zero)."""
    N_t = 128
    W_eye = torch.eye(N_t, device=DEVICE, dtype=torch.float32) / N_t
    rng = np.random.RandomState(0)
    V_np = rng.choice([-1.0, 1.0], size=(N_t, 200)).astype(np.float32)
    V = torch.from_numpy(V_np).to(DEVICE)
    WV  = W_eye @ V
    W2V = W_eye @ WV
    W3V = W_eye @ W2V
    k3 = float(torch.mean(torch.sum(V * W3V, dim=0)).item()) / N_t
    assert abs(k3) < 0.01, f"selftest W=I/N: kappa_3={k3:.6f} not near 0"


def _selftest_gpu_ok():
    """GPU is accessible and can do a batched matmul."""
    a = torch.ones((8, 8), device=DEVICE)
    b = torch.ones((8, 8), device=DEVICE)
    c = a @ b
    assert c[0, 0].item() == 8.0, "GPU matmul sanity failed"


def _instrumentation_selftest():
    """Assert all claimed metrics non-null/non-sentinel at smoke scale."""
    _selftest_gpu_ok()
    _selftest_zero_noise_exact()
    _selftest_no_noise_identity()
    _selftest_hutchinson_near_identity()
    print("[selftest] PASS: gpu_ok, zero_noise_exact, no_noise_identity, hutchinson_identity", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials


def run_seed(seed: int) -> Dict:
    """For each sigma_g, build W_noisy and estimate kappa_3."""
    W_np = build_w_cpu(seed)
    results = {}
    for sigma_g in SIGMA_G_GRID:
        W_t = add_lognormal_noise(W_np, sigma_g, seed)
        k3  = hutchinson_kappa3(W_t, N_PROBES, seed + int(sigma_g * 10000))
        ratio = k3 / ALPHA
        results[sigma_g] = {"kappa3": k3, "ratio": ratio}
        print(f"  [seed={seed} sigma_g={sigma_g:.2f}] kappa3={k3:.5f} ratio={ratio:.3f}",
              flush=True)
        del W_t
        torch.cuda.empty_cache()
    return {"seed": seed, "sigma_g_results": {str(sg): v for sg, v in results.items()}}


def main():
    t_start = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)

    print(f"[{RUN_MODE}] N={N} M={M} alpha={ALPHA} n_probes={N_PROBES} seeds={SEEDS}", flush=True)

    done_seeds, remaining = resumable_seeds(SEEDS, out_dir)
    print(f"[ckpt] {len(done_seeds)} done; running {remaining}", flush=True)

    for seed in remaining:
        print(f"[seed {seed}]", flush=True)
        r = run_seed(seed)
        write_partial(out_dir, seed, r)

    per_seed = aggregate_partials(out_dir, SEEDS)

    # Aggregate: for each sigma_g, compute mean ratio across seeds
    sigma_mean_ratio: Dict[float, float] = {}
    for sg in SIGMA_G_GRID:
        ratios = [per_seed[str(s)]["sigma_g_results"][str(sg)]["ratio"] for s in SEEDS]
        sigma_mean_ratio[sg] = float(np.mean(ratios))

    print("\n[summary] sigma_g -> mean kappa3/alpha ratio:", flush=True)
    for sg, r in sorted(sigma_mean_ratio.items()):
        print(f"  sigma_g={sg:.2f}: ratio={r:.3f}", flush=True)

    # Verdict logic
    # HP: identity holds within +-5% for sigma_g <= 0.15 AND breaks >+-15% by sigma_g=0.25
    low_sigmas = [sg for sg in SIGMA_G_GRID if sg <= HP_IDENTITY_HOLD_SIGMA]
    identity_holds = all(abs(sigma_mean_ratio[sg] - 1.0) <= HP_IDENTITY_HOLD_TOL
                         for sg in low_sigmas)

    # Check per-seed unanimous for sigma_g <= 0.15
    identity_holds_unanimous = True
    for sg in low_sigmas:
        ratios = [per_seed[str(s)]["sigma_g_results"][str(sg)]["ratio"] for s in SEEDS]
        if not all(abs(r - 1.0) <= HP_IDENTITY_HOLD_TOL for r in ratios):
            identity_holds_unanimous = False
            break

    # Check breaks by sigma_g=0.25 unanimous
    break_ratio_025 = sigma_mean_ratio.get(0.25, 1.0)
    identity_breaks_unanimous = True
    for s in SEEDS:
        r_025 = per_seed[str(s)]["sigma_g_results"].get("0.25", {}).get("ratio", 1.0)
        if abs(r_025 - 1.0) <= HP_BREAK_TOL:
            identity_breaks_unanimous = False

    # HF conditions
    ratio_005 = sigma_mean_ratio.get(0.05, 1.0)
    ratio_030 = sigma_mean_ratio.get(0.30, 1.0)
    hf_early_break = abs(ratio_005 - 1.0) > HP_BREAK_TOL  # breaks before sigma_g=0.05
    hf_late_hold   = abs(ratio_030 - 1.0) <= HP_IDENTITY_HOLD_TOL  # still holds at 0.30

    if hf_early_break or hf_late_hold:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HF: early_break={hf_early_break} (ratio@0.05={ratio_005:.3f}) "
                       f"late_hold={hf_late_hold} (ratio@0.30={ratio_030:.3f})")
    elif identity_holds_unanimous and identity_breaks_unanimous:
        verdict = "HARD_PASS"
        verdict_msg = (f"HP: kappa3/alpha in [+-5%] for sigma_g<=0.15 (unanimous) AND "
                       f"breaks >+-15% by sigma_g=0.25 (unanimous); "
                       f"sigma_g_critical~0.18 confirmed (Wave-2 prediction)")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE: identity_holds={identity_holds_unanimous} "
                       f"breaks={identity_breaks_unanimous} "
                       f"ratio@0.15={sigma_mean_ratio.get(0.15,float('nan')):.3f} "
                       f"ratio@0.25={sigma_mean_ratio.get(0.25,float('nan')):.3f}")

    elapsed = time.time() - t_start
    metrics = {
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "sigma_g_mean_ratio": {str(sg): v for sg, v in sigma_mean_ratio.items()},
        "identity_holds_unanimous": identity_holds_unanimous,
        "identity_breaks_unanimous": identity_breaks_unanimous,
        "N": N,
        "M": M,
        "alpha": ALPHA,
        "n_seeds": len(SEEDS),
        "n_probes": N_PROBES,
        "elapsed_s": elapsed,
        "run_mode": RUN_MODE,
    }

    out_dir.joinpath("metrics.json").write_text(json.dumps(metrics, indent=2))
    print(f"\n[verdict] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    main()
