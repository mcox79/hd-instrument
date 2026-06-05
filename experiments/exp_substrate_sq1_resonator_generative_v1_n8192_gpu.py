"""
substrate_sq1_resonator_generative_v1_n8192_gpu -- compositional generation via resonator factorization (GPU).

ROUTING: research_to_exp_dev_pure_bio_revised_orthogonal_axes_plus_exploration (SQ1; P_drill=0.68). Per drill:
  substrate-direct LANGUAGE-class generation is RESONATOR-GENERATIVE (combinatorial composition of stored
  vocabulary factors, V^K distinct generations) -- NOT Hebbian n-gram. A resonator resolves ANY bound product
  c = f1 (x) f2 (x) ... (x) fK into its factors, so it can GENERATE + decode any of V^K novel combinations.
  torch GPU (resonator cleanup matmuls; feeds idle GPU; N=8192). $0.

CAPABILITY QUESTION: at substrate N=8192, V=100 factors/codebook, how many factors K can be composed + resolved
  at >=95% on NOVEL (never-stored) random products? The resolvable generative space = V^K.

MODEL (noise-injection resonator, best K_max per round-1): K codebooks (V,N) bipolar; novel product = elementwise
  bind of one chosen factor per codebook; decode by iterated unbind + codebook cleanup with annealed data-adaptive
  noise (escapes limit cycles). Trial correct iff ALL K factors recovered. Sweep K.

CELLS (3 seeds): K in {4,6,8,10}; V=100; N=8192; B=128 trials; T=100 iters. generative space = V^Kmax.
PRE-REGISTERED bands (Kmax = max K with mean recovery>=0.95): HARD-PASS V^Kmax >= 1e12 (Kmax>=6 at V=100);
  MIDDLE V^Kmax in [1e8, 1e12) (Kmax 4-5); HARD-FAIL Kmax<4.

FORMULA SELF-TESTS (PROT-022): 1. bind self-inverse. 2. K=2 resolves both (acc>0.5). 3. codebook bipolar. 4. N=8192.
PROT-018: _n8192 -> N=8192. PROT-019 floor 21600s. GPU TEMPLATE: assert cuda + device='cuda'. ASCII-only. write_metrics.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace'); sys.stderr.reconfigure(encoding='utf-8', errors='replace')
import os, argparse, time, json, math
from pathlib import Path
from typing import Dict, List, Tuple
REPO = Path(__file__).resolve().parent.parent; sys.path.insert(0, str(REPO))
try:
    import torch
except ImportError:
    print("[FATAL] torch not installed.", flush=True); sys.exit(1)
if not torch.cuda.is_available():
    print("[FATAL] CUDA not available.", flush=True); sys.exit(1)
DEVICE = torch.device('cuda'); print(f"[GPU] {torch.cuda.get_device_name(0)}", flush=True)
import numpy as np
from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_sq1_resonator_generative_v1_n8192_gpu"
_N_SUFFIX = 8192; N = 8192; assert N == _N_SUFFIX
RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser(); _ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true"); _ARGS, _ = _ap.parse_known_args()
V = 100; T_ITERS = 100; B = 128; SIGMA0 = 0.6; K_GRID = [4, 6, 8, 10]; ACC = 0.95
if RUN_MODE == "smoke":
    N_DIM = 512; SEEDS = [1, 2]; K_GRID = [2, 4]; B = 64; V = 50
else:
    N_DIM = N; SEEDS = [7, 17, 23]


def recovery(n, K, gen):
    cbs = [(torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1) for _ in range(K)]
    tidx = [torch.randint(0, V, (B,), generator=gen, device=DEVICE) for _ in range(K)]
    chosen = [cbs[k][tidx[k]] for k in range(K)]
    c = chosen[0].clone()
    for k in range(1, K):
        c = c * chosen[k]
    x = [cbs[k].mean(0, keepdim=True).expand(B, n).clone() for k in range(K)]
    for t in range(T_ITERS):
        sig = SIGMA0 * (1.0 - t / max(1, T_ITERS - 1))
        for k in range(K):
            others = torch.ones(B, n, device=DEVICE)
            for j in range(K):
                if j != k:
                    others = others * x[j]
            cleaned = (c * others @ cbs[k].t()) @ cbs[k]
            if sig > 0:
                cleaned = cleaned + (sig * (cleaned.std(dim=1, keepdim=True) + 1e-8)) * torch.randn(B, n, generator=gen, device=DEVICE)
            xk = torch.sign(cleaned); xk[xk == 0] = 1.0; x[k] = xk
    correct = torch.ones(B, dtype=torch.bool, device=DEVICE)
    for k in range(K):
        correct = correct & ((x[k] @ cbs[k].t()).argmax(1) == tidx[k])
    return float(correct.float().mean())


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    f1 = (torch.randint(0, 2, (256,), generator=gen, device=DEVICE).float() * 2 - 1)
    f2 = (torch.randint(0, 2, (256,), generator=gen, device=DEVICE).float() * 2 - 1)
    assert torch.allclose((f1 * f2) * f1, f2), "bind not self-inverse"
    a = recovery(256, 2, gen); assert a > 0.5, f"K=2 acc {a}"
    cb = (torch.randint(0, 2, (4, 64), generator=gen, device=DEVICE).float() * 2 - 1); assert set(torch.unique(cb).tolist()) <= {-1.0, 1.0}
    assert N == 8192; print(f"[selftest] PASS: bind_self_inverse K2_acc={a:.2f}", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE).manual_seed(seed); t0 = time.time(); cells = []
    for K in K_GRID:
        acc = recovery(n_dim, K, gen); cells.append({"K": K, "recovery": acc})
        print(f"  [seed={seed} K={K}] recovery={acc:.3f}", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9
    return {"seed": seed, "N": n_dim, "V": V, "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": time.time() - t0}


def compute_verdict(rs) -> Tuple[str, str]:
    if not rs:
        return ("HARD_FAIL", "no results")
    acc = {K: float(np.mean([c["recovery"] for r in rs for c in r["cells"] if c["K"] == K])) for K in K_GRID}
    kmax = max([K for K in K_GRID if acc[K] >= ACC], default=0)
    space = V ** kmax if kmax else 0
    summary = "acc " + " ".join(f"K{K}:{acc[K]:.2f}" for K in K_GRID) + f" | Kmax={kmax} generative_space=V^{kmax}={space:.2e}" if kmax else "acc " + " ".join(f"K{K}:{acc[K]:.2f}" for K in K_GRID) + " | Kmax=0"
    if kmax >= 6:
        return ("HARD_PASS", f"HARD_PASS: resonator generates+resolves V^{kmax}>=1e12 novel combinations. {summary}")
    if kmax >= 4:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: generative space V^{kmax}. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: Kmax<4. {summary}")


print(f"[config] anchor={ANCHOR_NAME} mode={RUN_MODE} seeds={SEEDS} N={N_DIM} V={V} K_grid={K_GRID}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "K_grid": K_GRID, "V": V})
for seed in remaining:
    print(f"[seed={seed}] ...", flush=True); write_partial(out_dir, seed, run_seed(seed, N_DIM))
all_results = list(aggregate_partials(out_dir, SEEDS).values())
verdict, vmsg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9; print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": vmsg, "N": N_DIM, "V": V,
           "run_mode": RUN_MODE, "n_seeds": len(SEEDS), "per_seed": all_results}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
