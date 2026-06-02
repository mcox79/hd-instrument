"""
deletion_cert_z_ratio_n16384_v1 -- Deletion-cert Z-ratio at N=16384 (intermediate point).

Fills in the N-scaling curve between N=8192 (~2.0 sigma) and N=32768 (HP ~3.6-5.1 sigma).
Theory: Z ~ sqrt(N) -> N=16384 (sqrt factor vs N=8192: sqrt(2) ~ 1.41x) predicts Z ~ 2.83.

GPU IMPLEMENTATION:
  Xi patterns (M x N float32): for N=16384, alpha=0.05 -> M=819 patterns.
  Xi float32: 819 * 16384 * 4 = 53 MB. No W matrix needed (matrix-free).
  deletion_signal and null_signal are matrix-free via batched matmul.

PRE-REGISTERED BANDS:
  HARD-PASS: Z-ratio >= 2.5 (N=16384 should be ~2.83 theory, HP set conservatively).
  MIDDLE: 1.8 <= Z-ratio < 2.5.
  HARD-FAIL: Z-ratio < 1.5 (no scaling signal at N=16384).
  Calibration: N=8192 ~2.0 sigma, N=32768 HP >3.0. N=16384 interpolated.
  Bands: +-30% of midpoint prediction 2.83 = [1.98, 3.68]; HP at 2.5 (conservative).

FORMULA SELF-TESTS:
  1. Z = (mean_signal - mean_null) / std_null; signal > 0.
     [INPUT: N=256, M=13] [EXPECTED: signal > 0.5*sqrt(N)]
  2. sqrt(N) scaling: signal at N=256 / signal at N=64 ~ sqrt(4) = 2.
  3. GPU memory > 0 after Xi alloc.

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
from typing import Dict, List

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

ANCHOR_NAME = "deletion_cert_z_ratio_n16384_v1"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA = 0.05
N_NULL_PROBES = 20

if RUN_MODE == "smoke":
    N_ACTIVE = 2048
    SEEDS = [7, 17]
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]

# Pre-registered bands
HP_Z = 2.5
MID_Z = 1.8
HF_Z = 1.5


def deletion_signal_gpu(Xi: torch.Tensor, n: int, k: int) -> float:
    """Matrix-free deletion signal for pattern k.

    W_pre @ xi_k - W_post @ xi_k = (1/N) xi_k (xi_k^T xi_k) = xi_k.
    Theory: signal magnitude = ||xi_k|| = sqrt(N).
    """
    xi_k = Xi[k]
    # W @ xi_k = Xi.T @ (Xi @ xi_k) / n (full W pre)
    pre = (Xi.t() @ (Xi @ xi_k)) / n
    # W_post = W_pre minus rank-1 contribution of xi_k
    # (Xi without row k) @ xi_k
    mask = torch.ones(Xi.shape[0], dtype=torch.bool, device=DEVICE)
    mask[k] = False
    Xi_post = Xi[mask]
    post = (Xi_post.t() @ (Xi_post @ xi_k)) / n
    return float((pre - post).norm())


def null_signal_gpu(Xi: torch.Tensor, n: int, gen: torch.Generator) -> float:
    """Null: W @ xi_rand for random pattern not in stored set."""
    xi_rand = (torch.randint(0, 2, (n,), generator=gen, device=DEVICE).float() * 2 - 1)
    response = (Xi.t() @ (Xi @ xi_rand)) / n
    return float(response.norm())


def _instrumentation_selftest():
    """Tiny-N selftest: deletion_signal ~ sqrt(N)."""
    N_t = 256
    M_t = 13
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    Xi_t = (torch.randint(0, 2, (M_t, N_t), generator=gen, device=DEVICE).float() * 2 - 1)

    sig = deletion_signal_gpu(Xi_t, N_t, k=0)
    expected = math.sqrt(N_t)
    assert sig > 0.5 * expected and sig < 2.0 * expected, \
        f"deletion_signal selftest: got {sig:.2f}, expected ~{expected:.2f}"

    # sqrt(N) scaling test: N=256 vs N=64
    N_small = 64
    Xi_small = (torch.randint(0, 2, (M_t, N_small), generator=gen, device=DEVICE).float() * 2 - 1)
    sig_small = deletion_signal_gpu(Xi_small, N_small, k=0)
    ratio = sig / sig_small
    expected_ratio = math.sqrt(N_t / N_small)  # sqrt(4) = 2.0
    assert ratio > 0.5 * expected_ratio and ratio < 2.5 * expected_ratio, \
        f"sqrt(N) scaling: ratio={ratio:.2f} expected ~{expected_ratio:.2f}"

    # GPU memory check
    mem = torch.cuda.memory_allocated(0)
    assert mem > 0, f"GPU memory not allocated: {mem}"

    print(f"[selftest] PASS: deletion_signal at N={N_t}={sig:.3f} ~sqrt(N)={expected:.3f}; "
          f"sqrt(N) scaling ratio={ratio:.2f}; gpu_mem_ok", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    M = int(ALPHA * n_dim)
    Xi = (torch.randint(0, 2, (M, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)

    mem_gb = torch.cuda.memory_allocated(0) / 1e9
    print(f"  [seed={seed} N={n_dim} M={M}] GPU memory after Xi alloc: {mem_gb:.3f} GB", flush=True)

    # Signal: for first K patterns
    K_test = min(M, 10)
    signals = [deletion_signal_gpu(Xi, n_dim, k=k) for k in range(K_test)]
    mean_signal = float(sum(signals) / len(signals))

    # Null distribution
    nulls = [null_signal_gpu(Xi, n_dim, gen=gen) for _ in range(N_NULL_PROBES)]
    mean_null = float(sum(nulls) / len(nulls))
    std_null = float((sum((x - mean_null)**2 for x in nulls) / max(len(nulls) - 1, 1))**0.5)

    z_ratio = (mean_signal - mean_null) / max(std_null, 1e-12)

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] signal={mean_signal:.4f} null={mean_null:.4f} std={std_null:.4f} "
          f"Z={z_ratio:.4f} peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "M": M, "run_mode": RUN_MODE,
        "mean_signal": float(mean_signal),
        "mean_null": float(mean_null),
        "std_null": float(std_null),
        "z_ratio": float(z_ratio),
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": elapsed,
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    z_vals = [r["z_ratio"] for r in results if "z_ratio" in r]
    mean_z = float(sum(z_vals) / len(z_vals)) if z_vals else 0.0

    summary = (f"mean_Z={mean_z:.4f} (HP>={HP_Z} MID>={MID_Z} HF<{HF_Z}) "
               f"n_seeds={len(results)}")

    if mean_z < HF_Z:
        return ("HARD_FAIL", f"HARD_FAIL: mean_Z={mean_z:.4f} < {HF_Z}. {summary}")
    if mean_z >= HP_Z:
        return ("HARD_PASS", f"HARD_PASS: mean_Z={mean_z:.4f} >= {HP_Z} at N=16384. {summary}")
    if mean_z >= MID_Z:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} alpha={ALPHA}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N_ACTIVE} M={int(ALPHA*N_ACTIVE)}...", flush=True)
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
z_vals = [r["z_ratio"] for r in all_results if "z_ratio" in r]
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
    "mean_z_ratio": float(sum(z_vals)/len(z_vals)) if z_vals else None,
}
metrics_path = out_dir / "metrics.json"
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
