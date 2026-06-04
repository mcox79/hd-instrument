"""
substrate_resonator_noise_injection_ksweep_v1_n4096_gpu -- noise-injection resonator capacity (GPU).

ROUTING: notes/change_request_mode4_resonator_add_sparse_noise_injection_cells_2026-06-04.md (Cell R5:
  noise-injection extension, arXiv:2412.00354). + notes/routing_mode4_resonator_falsifier_test (baseline K=5).
  GPU, $0. NOTE: the change-request's OTHER cell (R4 sparse-block-code resonator, arXiv:2404.19126) is NOT in
  this script -- sparse block-codes are a distinct architecture (per-block one-hot + block-wise binding);
  implementing it unverified risks a wrong mechanism. Deferred with a note to Research (see shipped note).

CAPABILITY QUESTION:
  Does per-iteration annealed noise-injection (stochastic resonance) let a dense resonator escape spurious
  limit cycles and recover MORE factors than the deterministic baseline at substrate N=4096? Tests the
  "noise-injection extends K_max ~50x for free" claim. Baseline dense resonator saturates ~K=5-8 (our
  dense K-sweep). If noise-injection HPs at K=50, Mode-4 factor capacity jumps massively.

MODEL (batched resonator, dense bipolar): c = elementwise product of K chosen codebook vectors. Decode by
  iterating: unbind_k = c * prod_{j!=k} x_j; sims = unbind_k @ C_k^T; x_k = sign(sims @ C_k + noise_t).
  NOISE-INJECTION: noise_t = sigma_t * randn(B,N), sigma_t = SIGMA0 * (1 - t/T) annealed linearly to 0
  (deterministic in the final iters -> clean convergence). ARM 'baseline' sets SIGMA0=0 (identical code path).

CELLS: arm in {baseline, noise}; K in {5,10,20,30,50}; N=4096; V=512; B=128 trials; T=100 iters; 5 seeds.

PRE-REGISTERED BANDS (recovery = mean frac of trials with ALL K factors recovered):
  Per-K-cell: a cell "passes" if recovery >= thr(K): thr(5)=0.85, thr(10..30)=0.70, thr(50)=0.60.
  K_max(arm) = largest K with recovery >= thr(K) in >=4/5 seeds.
  HARD-PASS: noise K_max >= 20 AND noise K_max > baseline K_max (noise-injection materially extends capacity).
  MIDDLE: noise K_max > baseline K_max but noise K_max < 20.
  HARD-FAIL: noise K_max <= baseline K_max (no benefit from noise-injection).

FORMULA SELF-TESTS (PROT-022):
  1. bipolar bind self-inverse. 2. K=2 baseline recovers both (acc~1). 3. argmax cleanup exact. 4. anneal sigma_t->0 at t=T-1.

PROT-018: anchor _n4096 -> N=4096. PROT-019: _n4096 floor 14400s. PROT-021: per-seed partials.
QUEUE: overnight_queue (GPU). GPU TEMPLATE: assert cuda + device='cuda' + batched matmul. ASCII-only.
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
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda')
print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_resonator_noise_injection_ksweep_v1_n4096_gpu"
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

V = 512
T_ITERS = 100
B_TRIALS = 128
SIGMA0 = 0.6          # initial noise std (relative to sim scale); annealed to 0
K_GRID = [5, 10, 20, 30, 50]
ARMS = ["baseline", "noise"]
THR = {5: 0.85, 10: 0.70, 20: 0.70, 30: 0.70, 50: 0.60}

if RUN_MODE == "smoke":
    N_DIM = 512; SEEDS = [1, 2]; K_GRID = [2, 5, 10]; B_TRIALS = 48; V = 128; T_ITERS = 40
    THR = {2: 0.85, 5: 0.70, 10: 0.50}
else:
    N_DIM = N; SEEDS = [7, 17, 23, 31, 41]


def resonator_recovery(n, K, sigma0, gen, v=None) -> float:
    v = v if v is not None else V
    codebooks = [(torch.randint(0, 2, (v, n), generator=gen, device=DEVICE).float() * 2 - 1) for _ in range(K)]
    true_idx = [torch.randint(0, v, (B_TRIALS,), generator=gen, device=DEVICE) for _ in range(K)]
    chosen = [codebooks[k][true_idx[k]] for k in range(K)]
    c = chosen[0].clone()
    for k in range(1, K):
        c = c * chosen[k]
    x = [codebooks[k].mean(dim=0, keepdim=True).expand(B_TRIALS, n).clone() for k in range(K)]
    for t in range(T_ITERS):
        sigma_t = sigma0 * (1.0 - t / max(1, T_ITERS - 1))   # linear anneal to 0 at t=T-1
        for k in range(K):
            others = torch.ones(B_TRIALS, n, device=DEVICE)
            for j in range(K):
                if j != k:
                    others = others * x[j]
            unbind = c * others
            sims = unbind @ codebooks[k].t()                 # (B,V)
            cleaned = sims @ codebooks[k]                     # (B,n)
            if sigma_t > 0:
                # data-adaptive noise: sigma_t fraction of the per-trial signal std (stochastic resonance)
                scale = cleaned.std(dim=1, keepdim=True) + 1e-8
                cleaned = cleaned + (sigma_t * scale) * torch.randn(B_TRIALS, n, generator=gen, device=DEVICE)
            xk = torch.sign(cleaned); xk[xk == 0] = 1.0
            x[k] = xk
    correct = torch.ones(B_TRIALS, dtype=torch.bool, device=DEVICE)
    for k in range(K):
        idx_hat = (x[k] @ codebooks[k].t()).argmax(dim=1)
        correct = correct & (idx_hat == true_idx[k])
    return float(correct.float().mean())


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    f1 = (torch.randint(0, 2, (256,), generator=gen, device=DEVICE).float() * 2 - 1)
    f2 = (torch.randint(0, 2, (256,), generator=gen, device=DEVICE).float() * 2 - 1)
    assert torch.allclose((f1 * f2) * f1, f2), "bind not self-inverse"
    acc2 = resonator_recovery(256, 2, 0.0, gen, v=24); assert acc2 > 0.5, f"K=2 baseline acc {acc2}"  # mechanism check (V=24 easy load; chance ~1/V^2); V-independent of run mode
    cb = (torch.randint(0, 2, (10, 256), generator=gen, device=DEVICE).float() * 2 - 1)
    assert int((cb @ cb[3]).argmax()) == 3, "cleanup wrong"
    s_end = SIGMA0 * (1.0 - (T_ITERS - 1) / max(1, T_ITERS - 1)); assert abs(s_end) < 1e-9, "anneal not ->0"
    print(f"[selftest] PASS: bind_self_inverse K2_acc={acc2:.3f} anneal_to_0", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    t0 = time.time(); cells = []
    for arm in ARMS:
        sigma0 = 0.0 if arm == "baseline" else SIGMA0
        for K in K_GRID:
            rec = resonator_recovery(n_dim, K, sigma0, gen)
            cells.append({"arm": arm, "K": K, "recovery": rec})
            print(f"    [seed={seed} {arm} K={K}] recovery={rec:.4f}", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9; elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def _kmax(results, arm):
    ks = []
    for K in K_GRID:
        n_pass = sum(1 for r in results
                     if next((c["recovery"] for c in r["cells"] if c["arm"] == arm and c["K"] == K), 0.0) >= THR[K])
        if n_pass >= math.ceil(0.8 * len(results)):
            ks.append(K)
    return max(ks, default=0)


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "no results")
    km_base, km_noise = _kmax(results, "baseline"), _kmax(results, "noise")
    mean_rec = {(arm, K): float(np.mean([next((c["recovery"] for c in r["cells"] if c["arm"] == arm and c["K"] == K), 0.0) for r in results]))
                for arm in ARMS for K in K_GRID}
    summary = ("baseline[" + " ".join(f"K{K}:{mean_rec[('baseline', K)]:.2f}" for K in K_GRID) + "] "
               "noise[" + " ".join(f"K{K}:{mean_rec[('noise', K)]:.2f}" for K in K_GRID) + "] "
               f"K_max base={km_base} noise={km_noise}")
    if km_noise >= 20 and km_noise > km_base:
        return ("HARD_PASS", f"HARD_PASS: noise-injection extends Mode-4 capacity (K_max {km_base}->{km_noise}). {summary}")
    if km_noise > km_base:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: noise-injection helps but K_max<20. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: noise-injection no benefit (K_max noise<=baseline). {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_DIM} V={V} K_grid={K_GRID} arms={ARMS} T={T_ITERS} B={B_TRIALS} sigma0={SIGMA0} mode={RUN_MODE} seeds={SEEDS}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "K_grid": K_GRID, "arms": ARMS, "sigma0": SIGMA0})
print(f"[ckpt] {len(done)} done, {len(remaining)} to run", flush=True)
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed, N_DIM))
per_seed = aggregate_partials(out_dir, SEEDS); all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9; print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg, "N": N_DIM,
           "V": V, "K_grid": K_GRID, "arms": ARMS, "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
           "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells"), "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results]}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
