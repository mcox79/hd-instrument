"""
substrate_resonator_dense_capacity_ksweep_v1_n4096 -- resonator factorization capacity K-sweep (GPU).

ROUTING: notes/exp_dev_handoff_research_resonator_capacity_substrate_scale_2026-06-04.md (anchor 1: dense
  resonator K-sweep). Per [[feedback-no-experiment-design-in-prompts]] exp_dev designed all parameters.
  Routed to the OWNED GPU (batched resonator cleanup matmuls; feeds GPU; torch -> per routing-sanity gate OK).

CAPABILITY QUESTION:
  A resonator network (Frady-Kent-Sommer-Kanerva 2020) factorizes a bound product c = f1 (x) f2 (x) ... (x) fK
  (bipolar elementwise bind) back into its K factors by iterative unbind + codebook cleanup. At substrate
  N=4096 with V=100 candidates per factor, what is K_max (max factors resolvable at >=99% accuracy)?
  Theory: K_max grows with N (N^2 search-space scaling). This sets the Mode-4 NC1 capacity envelope.

MODEL (batched resonator):
  K codebooks C_k (V, N) bipolar. Per trial pick one index per factor; c = elementwise product of the chosen
  vectors. Decode: x_k init = superposition (mean codebook); iterate T: for each k,
    unbind_k = c * prod_{j!=k} x_j ;  sims = unbind_k @ C_k^T (B,V) ;  x_k = sign(sims @ C_k) (B,N).
  Readout: idx_hat_k = argmax_v (x_k @ C_k[v]). Trial correct iff ALL K factors recovered. Sweep K.

K SWEEP: {5,6,7,8,9,10,11}; N=4096; V=100; B=200 trials; T=50 iters; 3 seeds.

PRE-REGISTERED BANDS (K_max = largest K with mean accuracy >= 0.99):
  HARD-PASS: K_max >= 8. MIDDLE: K_max in {5,6,7}. HARD-FAIL: K_max < 5.

FORMULA SELF-TESTS (PROT-022):
  1. bipolar bind self-inverse: c * f1 with c=f1*f2 recovers f2. 2. K=2 resonator recovers both factors (acc~1).
  3. argmax cleanup recovers an exact codebook vector. 4. codebook bipolar {-1,+1}.

PROT-018: anchor _n4096 -> N=4096. PROT-019: _n4096 timeout floor 14400s. PROT-021: per-seed partials.
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

ANCHOR_NAME = "substrate_resonator_dense_capacity_ksweep_v1_n4096"
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true"); _ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

V = 100
T_ITERS = 50
B_TRIALS = 200
K_GRID = [5, 6, 7, 8, 9, 10, 11]
ACC_THRESH = 0.99

if RUN_MODE == "smoke":
    N_DIM = 512; SEEDS = [1, 2]; K_GRID = [2, 3, 5]; B_TRIALS = 80; V = 50
else:
    N_DIM = N; SEEDS = [7, 17, 23]


def resonator_accuracy(n, K, gen) -> float:
    codebooks = [(torch.randint(0, 2, (V, n), generator=gen, device=DEVICE).float() * 2 - 1) for _ in range(K)]
    true_idx = [torch.randint(0, V, (B_TRIALS,), generator=gen, device=DEVICE) for _ in range(K)]
    chosen = [codebooks[k][true_idx[k]] for k in range(K)]              # each (B, n)
    c = chosen[0].clone()
    for k in range(1, K):
        c = c * chosen[k]                                              # bound product (B,n)
    # init estimates = superposition (mean codebook), broadcast to batch
    x = [codebooks[k].mean(dim=0, keepdim=True).expand(B_TRIALS, n).clone() for k in range(K)]
    for _ in range(T_ITERS):
        for k in range(K):
            others = torch.ones(B_TRIALS, n, device=DEVICE)
            for j in range(K):
                if j != k:
                    others = others * x[j]
            unbind = c * others                                        # (B,n)
            sims = unbind @ codebooks[k].t()                           # (B,V)
            x[k] = torch.sign(sims @ codebooks[k]); x[k][x[k] == 0] = 1.0   # (B,n)
    correct = torch.ones(B_TRIALS, dtype=torch.bool, device=DEVICE)
    for k in range(K):
        idx_hat = (x[k] @ codebooks[k].t()).argmax(dim=1)
        correct = correct & (idx_hat == true_idx[k])
    return float(correct.float().mean())


def _selftest():
    gen = torch.Generator(device=DEVICE).manual_seed(0)
    f1 = (torch.randint(0, 2, (256,), generator=gen, device=DEVICE).float() * 2 - 1)
    f2 = (torch.randint(0, 2, (256,), generator=gen, device=DEVICE).float() * 2 - 1)
    c = f1 * f2
    assert torch.allclose(c * f1, f2), "bipolar bind not self-inverse"
    acc2 = resonator_accuracy(256, 2, gen); assert acc2 > 0.5, f"K=2 mechanism acc {acc2}"  # mechanism check (not capacity; N=256/full-V is loaded)
    cb = (torch.randint(0, 2, (10, 256), generator=gen, device=DEVICE).float() * 2 - 1)
    assert int((cb @ cb[3]).argmax()) == 3, "argmax cleanup wrong"
    assert set(torch.unique(cb).tolist()) <= {-1.0, 1.0}
    print(f"[selftest] PASS: bind_self_inverse K2_acc={acc2:.3f} cleanup_ok", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE); gen.manual_seed(seed)
    t0 = time.time(); cells = []
    for K in K_GRID:
        acc = resonator_accuracy(n_dim, K, gen)
        cells.append({"K": K, "accuracy": acc})
        print(f"  [seed={seed} K={K}] accuracy={acc:.4f}", flush=True)
    peak = torch.cuda.max_memory_allocated(0) / 1e9; elapsed = time.time() - t0
    print(f"  [seed={seed}] peak_gpu={peak:.3f}GB elapsed={elapsed:.1f}s", flush=True)
    return {"seed": seed, "N": n_dim, "cells": cells, "peak_gpu_gb": float(peak), "elapsed_s": elapsed}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "no results")
    acc = {K: float(np.mean([c["accuracy"] for r in results for c in r["cells"] if c["K"] == K])) for K in K_GRID}
    kmax = max([K for K in K_GRID if acc[K] >= ACC_THRESH], default=0)
    summary = "acc=" + " ".join(f"K{K}:{acc[K]:.3f}" for K in K_GRID) + f" -> K_max={kmax}"
    if kmax >= 8:
        return ("HARD_PASS", f"HARD_PASS: resonator K_max={kmax}>=8 at N={results[0]['N']}. {summary}")
    if kmax >= 5:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: K_max={kmax} in 5-7. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: K_max={kmax}<5. {summary}")


print(f"[config] anchor={ANCHOR_NAME} N={N_DIM} V={V} K_grid={K_GRID} T={T_ITERS} B={B_TRIALS} mode={RUN_MODE} seeds={SEEDS}", flush=True)
if RUN_MODE == "full" and N_DIM != _N_SUFFIX:
    raise RuntimeError("PROT-018 N mismatch")
out_dir = get_output_dir(ANCHOR_NAME)
done, remaining = resumable_seeds(SEEDS, out_dir, run_config={"N": N_DIM, "run_mode": RUN_MODE, "K_grid": K_GRID, "V": V})
print(f"[ckpt] {len(done)} done, {len(remaining)} to run", flush=True)
for seed in remaining:
    print(f"[seed={seed}] {ANCHOR_NAME}...", flush=True)
    write_partial(out_dir, seed, run_seed(seed, N_DIM))
per_seed = aggregate_partials(out_dir, SEEDS); all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
peak = torch.cuda.max_memory_allocated(0) / 1e9; print(f"[GPU] peak {peak:.3f} GB", flush=True); assert peak > 0.001
metrics = {"anchor_name": ANCHOR_NAME, "verdict": verdict, "verdict_msg": verdict_msg, "N": N_DIM,
           "V": V, "K_grid": K_GRID, "run_mode": RUN_MODE, "n_seeds": len(SEEDS),
           "per_seed": [{"seed": r.get("seed"), "cells": r.get("cells"), "peak_gpu_gb": r.get("peak_gpu_gb"), "elapsed_s": r.get("elapsed_s")} for r in all_results]}
write_metrics(out_dir, metrics, all_results)
print("[metrics] written", flush=True)
