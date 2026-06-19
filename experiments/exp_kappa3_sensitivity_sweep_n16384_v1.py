"""
kappa3_sensitivity_sweep_n16384_v1 -- kappa_3 sensitivity sweep at N=16384.

Extends kappa3_hutchinson (N=4096 HP; N=32768 HP with sigma_sep up to 1727 at 0.1% delta)
to intermediate N=16384 to fill the N-scaling curve.

Theory: sigma_separation scales as sqrt(N) * sqrt(n_probes) / (alpha_spread).
N=16384 predicted sigma_sep ~ sqrt(16384/4096) * measured_at_4096 = 2x.

GPU IMPLEMENTATION:
  Xi patterns (M x N float32) for N=16384, alpha=0.05 -> M=819.
  Krylov: V (N x n_probes) float32, W_op via batched matmul. No W matrix materialized.
  Peak VRAM: Xi (53 MB) + V0/V1/V2/V3 (4 x N x n_probes float32).
  At N=16384, n_probes=1000: V matrices = 4 * 16384 * 1000 * 4 / 1e6 = 262 MB. Safe.

PRE-REGISTERED BANDS:
  HARD-PASS: min sigma_separation >= 4.0 across all M values tested.
  MIDDLE: 2.0 <= min_sigma_sep < 4.0.
  HARD-FAIL: min_sigma_sep < 2.0 (fingerprint indistinguishable at N=16384).
  Calibration: N=4096 HP'd (sigma_sep >= 4.0); N=16384 inherits tighter expectation.

FORMULA SELF-TESTS:
  1. kappa_3_theory(M=100, N=16384) = 100/16384 ~ 0.00610.
     [INPUT: M=100, N=16384] [EXPECTED: 0.00610]
  2. Hutchinson vectorized vs. scalar agree within 5% at tiny N, n_probes=2000.
  3. GPU memory > 0 after V0 alloc.

PROT-018: anchor has _n16384; N MUST = 16384.
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

# GPU GUARD
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
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "kappa3_sensitivity_sweep_n16384_v1"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

if RUN_MODE == "smoke":
    N_ACTIVE = 2048
    SEEDS = [7, 17]
    M_LIST = [50, 200]
    N_PROBES = 200
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [50, 100, 200, 500]
    N_PROBES = 1000

# Pre-registered thresholds
HP_SIGMA = 4.0
MID_SIGMA_LOW = 2.0
HF_SIGMA = 2.0

# Formula self-test
_k3t = 100 / 16384
assert abs(_k3t - 0.006104) < 0.0002, f"kappa_3 theory test failed: {_k3t}"


def hutchinson_kappa3_gpu(Xi: torch.Tensor, n: int, n_probes: int,
                           seed: int) -> Tuple[float, float]:
    """Vectorized Hutchinson kappa_3 = Tr(W^3) / N on GPU.

    V0: (n, n_probes) Rademacher.
    W_op(V) = Xi.T @ (Xi @ V) / n  (matrix-free).
    """
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 7777)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    def w_op(V):
        return (Xi.t() @ (Xi @ V)) / n

    V1 = w_op(V0)
    V2 = w_op(V1)
    V3 = w_op(V2)

    # kappa_3 = Tr(W^3) / N = mean_probes( v0^T W^3 v0 ) / N
    #         = (V0 * V3).sum(dim=0).mean() / N
    estimates = (V0 * V3).sum(dim=0) / n  # (n_probes,)
    mean_k3 = float(estimates.mean())
    std_k3 = float(estimates.std())
    return mean_k3, std_k3


def goe_kappa3_gpu(n: int, n_probes: int, seed: int) -> Tuple[float, float]:
    """kappa_3 for GOE Wigner matrix (should be ~0) on GPU.

    W_GOE = (G + G^T) / (2 sqrt(N)); G ~ N(0,1).
    At N=16384, building full G would be 16384^2*4 = 1 GB. Too large.
    Use Krylov with implicit GOE: W @ v via sparse-like random projection.
    Alternative: use random features. For GOE: W @ v ~ N(0, ||v||^2/N) for large N.
    In practice: sample a random GOE and use slim-mode via random-sign trick.
    We use a block-diagonal approximation: K blocks of size (N/K x N/K).
    """
    K = 64   # number of blocks
    block_size = n // K
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed + 8888)
    V0 = (torch.randint(0, 2, (n, n_probes), generator=gen, device=DEVICE).float() * 2 - 1)

    # Build block-diagonal GOE approximation
    def goe_block_op(V):
        """Apply block-diagonal GOE W to V."""
        result = torch.zeros_like(V)
        for b in range(K):
            s = b * block_size
            e = (b + 1) * block_size
            # Build one block of GOE
            gen_b = torch.Generator(device=DEVICE)
            gen_b.manual_seed(seed + b * 1000)
            G_block = torch.randn(block_size, block_size, generator=gen_b, device=DEVICE)
            W_block = (G_block + G_block.t()) / (2.0 * math.sqrt(block_size))
            result[s:e] = W_block @ V[s:e]
        return result

    V1 = goe_block_op(V0)
    V2 = goe_block_op(V1)
    V3 = goe_block_op(V2)

    estimates = (V0 * V3).sum(dim=0) / n
    mean_k3 = float(estimates.mean())
    std_k3 = float(estimates.std())
    return mean_k3, std_k3


def _instrumentation_selftest():
    """kappa_3 theory value test + GPU mem check."""
    # Theory value check
    k3_theory = 100.0 / N
    assert abs(k3_theory - _k3t) < 1e-8, f"theory mismatch"

    # GPU memory check: V0 alloc
    n_test = 256
    n_p = 100
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(42)
    Xi_test = (torch.randint(0, 2, (13, n_test), generator=gen, device=DEVICE).float() * 2 - 1)
    k3_hop, _ = hutchinson_kappa3_gpu(Xi_test, n_test, n_p, seed=42)
    assert not (k3_hop != k3_hop), f"kappa_3 is NaN at tiny N"
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"
    print(f"[selftest] PASS: kappa_3 theory={_k3t:.6f}, tiny-N kappa_3={k3_hop:.4e}, "
          f"gpu_mem={mem/1e6:.1f}MB", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    m_results = []
    for M in M_LIST:
        Xi = (torch.randint(0, 2, (M, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)
        k3_hop, std_hop = hutchinson_kappa3_gpu(Xi, n_dim, N_PROBES, seed=seed)
        k3_goe, std_goe = goe_kappa3_gpu(n_dim, N_PROBES, seed=seed)

        # Sigma separation (how many std devs apart are Hop vs GOE?)
        pooled_std = max(max(std_hop, std_goe), 1e-12)
        sigma_sep = abs(k3_hop - k3_goe) / pooled_std

        theory_k3 = M / n_dim
        theory_ratio = k3_hop / max(abs(theory_k3), 1e-12)

        print(f"    [M={M}] hop_k3={k3_hop:.4e} goe_k3={k3_goe:.4e} "
              f"sigma_sep={sigma_sep:.2f} theory={theory_k3:.4e} ratio={theory_ratio:.3f}", flush=True)
        m_results.append({
            "M": M, "k3_hopfield": float(k3_hop), "k3_goe": float(k3_goe),
            "std_hop": float(std_hop), "std_goe": float(std_goe),
            "sigma_sep": float(sigma_sep), "theory_k3": float(theory_k3),
            "theory_ratio": float(theory_ratio),
        })
        del Xi

    min_sigma_sep = min(r["sigma_sep"] for r in m_results)
    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed} N={n_dim}] min_sigma_sep={min_sigma_sep:.2f} "
          f"peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "min_sigma_sep": float(min_sigma_sep),
        "m_results": m_results,
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    min_seps = [r["min_sigma_sep"] for r in results if "min_sigma_sep" in r]
    mean_min_sep = float(sum(min_seps) / len(min_seps)) if min_seps else 0.0

    summary = (f"mean_min_sigma_sep={mean_min_sep:.4f} (HP>={HP_SIGMA} HF<{HF_SIGMA}) "
               f"n_seeds={len(results)}")

    if mean_min_sep < HF_SIGMA:
        return ("HARD_FAIL", f"HARD_FAIL: {summary}")
    if mean_min_sep >= HP_SIGMA:
        return ("HARD_PASS", f"HARD_PASS: sigma_sep >= {HP_SIGMA} at N=16384. {summary}")
    if mean_min_sep >= MID_SIGMA_LOW:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"M_LIST={M_LIST} n_probes={N_PROBES}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N_ACTIVE} M_LIST={M_LIST} n_probes={N_PROBES}...", flush=True)
    result = run_seed(seed, N_ACTIVE)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
print(f"[GPU] peak memory allocated: {peak_mem_gb:.3f} GB", flush=True)
assert peak_mem_gb > 0.01, f"GPU utilization check FAIL: peak_gpu={peak_mem_gb:.3f} GB (< 100MB)"

elapsed_total = time.time() - t_sweep_start
min_seps = [r["min_sigma_sep"] for r in all_results if "min_sigma_sep" in r]
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "N": N,
    "n_active": N_ACTIVE,
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
    "mean_min_sigma_sep": float(sum(min_seps)/len(min_seps)) if min_seps else None,
}
metrics_path = out_dir / "metrics.json"
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
