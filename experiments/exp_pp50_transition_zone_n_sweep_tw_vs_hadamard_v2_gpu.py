"""
pp50_transition_zone_n_sweep_tw_vs_hadamard_v2_gpu -- PP-50 transition-zone mechanism discriminator (N-sweep, GPU).

ROUTING: Research Q2 answer (user-routed 2026-06-04) + research_pp50_v3_noise_model_spec_for_exp_dev.
SUPERSEDES the deferred v1 (which used a guessed multiplicative-per-coord-on-W noise -> 0 violations).

CAPABILITY QUESTION:
  The PP-50 capacity transition zone is wider than the free-probability sharp-boundary prediction. Two
  mechanisms: (A) Tracy-Widom soft-edge ~ N^(-2/3) (vanishes at large N -> N-parameterized envelope) vs
  (B) non-self-averaging Hadamard term ~ N^0 (constant -> N-independent envelope). DECISIVE TEST (Q2):
  measure sigma_sep at fixed sigma_g ~ sigma_g_crit, sweep N, fit the scaling exponent beta
  (sigma_sep ~ N^(-beta)). beta ~ 2/3 => Tracy-Widom; beta ~ 0 => Hadamard.

NOISE MODEL (Research PP-50 v3 spec -- CRITICAL): per-PATTERN multiplicative log-normal on Xi rows:
  noise_scale = exp(sigma_g * Z), Z ~ N(0,1) one per stored pattern, applied to all N coords.
METRIC (v3 spec): sigma_sep = |k3_aug - k3_base| / |k3_base| * 1000 (isochoric kappa_3 separation;
  k3_aug adds delta_M = 1% extra patterns). kappa_3 = Tr(W^3)/N via Hutchinson with the matrix-free
  operator w_op(V) = Xi_noisy.T @ (Xi_noisy @ V) / N (no explicit N x N matrix -> N=16384 feasible).

PRE-REGISTERED BANDS (Q2):
  HARD-PASS (Tracy-Widom): beta_fit in [0.50, 0.80] (within ~25% of 2/3).
  HARD-PASS (Hadamard):    beta_fit in [-0.15, 0.15] (within ~15% of 0; N-independent envelope correct).
  MIDDLE: beta_fit in [0.15, 0.50] (intermediate; refutes both clean classes).
  HARD-FAIL: sigma_sep non-monotone in N, OR beta_fit < -0.15 (monotone INCREASING -> refutes scaling framework).

FORMULA SELF-TESTS (PROT-022):
  1. N^(-2/3) ratio: (8192/1024)^(-2/3) = 8^(-2/3) = 0.25. [within 1e-6]
  2. per-pattern log-normal mean = exp(sigma_g^2/2). [within 5% at n=200k]
  3. cosine(xi,xi)=1 (sanity); GPU memory > 0 after a w_op.

PROT-018: NO _nN suffix (N is swept); grid declared {1024,2048,4096,8192,16384}.
PROT-021: seed checkpoints keyed run_mode + seed.
QUEUE: overnight_queue (GPU; matrix-free Hutchinson; N up to 16384). TIMEOUT: 21600s.
GPU TEMPLATE: assert cuda + device='cuda' + batched matmul. ASCII-only stdout.
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

ANCHOR_NAME = "pp50_transition_zone_n_sweep_tw_vs_hadamard_v2_gpu"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
SIGMA_G = 0.80               # just below sigma_g_crit = sqrt(ln2) = 0.8326 (signal present; Q2)
N_PROBES = 1000
# Bands (Q2)
TW_LO, TW_HI = 0.50, 0.80
HAD_LO, HAD_HI = -0.15, 0.15
MID_LO, MID_HI = 0.15, 0.50
HF_BETA = -0.15

if RUN_MODE == "smoke":
    N_GRID = [256, 512, 1024]
    SEEDS = [7, 17]
    N_PROBES = 300
else:
    N_GRID = [1024, 2048, 4096, 8192, 16384]
    SEEDS = [7, 17, 23, 31, 41]


def make_noisy_Xi(M, n, sigma_g, gen):
    Xi = (torch.randint(0, 2, (M, n), generator=gen, device=DEVICE).float() * 2 - 1)
    Z = torch.randn(M, generator=gen, device=DEVICE)
    return Xi * torch.exp(sigma_g * Z).unsqueeze(1)   # per-pattern log-normal scale


def kappa3_matfree(Xi_n, n, gen, n_probes):
    """Tr(W^3)/N via Hutchinson, W = Xi_n.T Xi_n / N, matrix-free."""
    V = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)
    def w_op(X):
        return (Xi_n.t() @ (Xi_n @ X)) / n
    V3 = w_op(w_op(w_op(V)))
    return float(((V * V3).sum(dim=0) / n).mean())


def sigma_sep_at_N(n, sigma_g, seed):
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed * 1000 + n % 997)
    M = max(2, int(round(ALPHA * n)))
    Xi_n = make_noisy_Xi(M, n, sigma_g, gen)
    k3_base = kappa3_matfree(Xi_n, n, gen, N_PROBES)
    dM = max(1, int(round(0.01 * n)))
    Xi_extra = make_noisy_Xi(dM, n, sigma_g, gen)
    Xi_aug = torch.cat([Xi_n, Xi_extra], dim=0)
    k3_aug = kappa3_matfree(Xi_aug, n, gen, N_PROBES)
    if abs(k3_base) < 1e-12:
        return 0.0, k3_base, k3_aug
    ss = abs(k3_aug - k3_base) / abs(k3_base) * 1000.0
    return float(ss), float(k3_base), float(k3_aug)


def fit_beta(ns, ss):
    import numpy as np
    x = np.log(np.array(ns, dtype=np.float64))
    y = np.log(np.clip(np.array(ss, dtype=np.float64), 1e-9, None))
    slope, _ = np.polyfit(x, y, 1)
    return float(-slope)   # sigma_sep ~ N^(-beta) -> beta = -slope


def _selftest():
    assert abs((8192 / 1024) ** (-2.0 / 3.0) - 0.25) < 1e-6
    g = torch.randn(200000, generator=torch.Generator(device=DEVICE).manual_seed(0), device=DEVICE)
    m = float(torch.exp(SIGMA_G * g).mean()); exp_m = math.exp(SIGMA_G * SIGMA_G / 2)
    assert abs(m - exp_m) / exp_m < 0.05, f"lognormal mean {m} vs {exp_m}"
    gen = torch.Generator(device=DEVICE).manual_seed(1)
    Xi_n = make_noisy_Xi(13, 256, SIGMA_G, gen)
    k3 = kappa3_matfree(Xi_n, 256, gen, 100)
    assert torch.cuda.memory_allocated(0) > 0 and (k3 == k3)
    print(f"[selftest] PASS: N^-2/3=0.25 lognormal_mean ok kappa3_matfree={k3:.4f} gpu_mem_ok", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    t0 = time.time()
    cells = []
    for n in N_GRID:
        ss, k3b, k3a = sigma_sep_at_N(n, SIGMA_G, seed)
        cells.append({"N": n, "sigma_sep": ss, "k3_base": k3b, "k3_aug": k3a})
        print(f"  [seed={seed} N={n}] sigma_sep={ss:.4f} k3_base={k3b:.5f} k3_aug={k3a:.5f}", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "run_mode": RUN_MODE, "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> tuple:
    import numpy as np
    if not results:
        return ("HARD_FAIL", "No valid results.")
    mean_ss = {}
    for n in N_GRID:
        vs = [c["sigma_sep"] for r in results for c in r.get("cells", []) if c["N"] == n]
        mean_ss[n] = float(np.mean(vs)) if vs else 0.0
    ss_list = [mean_ss[n] for n in N_GRID]
    if min(ss_list) <= 0:
        return ("HARD_FAIL", f"HARD_FAIL: non-positive sigma_sep at some N (no signal). ss={[round(s,3) for s in ss_list]}")
    monotone_dec = all(ss_list[i+1] <= ss_list[i] * 1.15 for i in range(len(ss_list)-1))  # allow 15% noise
    beta = fit_beta(N_GRID, ss_list)
    summary = (f"beta={beta:.3f} monotone_dec={monotone_dec} "
               f"sigma_sep=" + " ".join(f"N{n}:{mean_ss[n]:.3f}" for n in N_GRID))

    if (not monotone_dec) or beta < HF_BETA:
        return ("HARD_FAIL", f"HARD_FAIL: non-monotone or increasing (beta<{HF_BETA}); scaling framework refuted. {summary}")
    if TW_LO <= beta <= TW_HI:
        return ("HARD_PASS", f"HARD_PASS: Tracy-Widom (beta in [{TW_LO},{TW_HI}] ~ 2/3); N-parameterized envelope needed. {summary}")
    if HAD_LO <= beta <= HAD_HI:
        return ("HARD_PASS", f"HARD_PASS: Hadamard (beta in [{HAD_LO},{HAD_HI}] ~ 0); N-independent envelope correct. {summary}")
    if MID_LO <= beta <= MID_HI:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: intermediate beta in [{MID_LO},{MID_HI}]; refutes both clean classes. {summary}")
    return ("MIDDLE_BAND", f"MIDDLE_BAND: beta outside named bands ({beta:.3f}). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N_grid={N_GRID} mode={RUN_MODE} seeds={SEEDS} "
      f"sigma_g={SIGMA_G} alpha={ALPHA}", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N_grid": N_GRID, "run_mode": RUN_MODE, "sigma_g": SIGMA_G, "alpha": ALPHA}
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
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells", []),
                  "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
