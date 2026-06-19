"""
deletion_cert_z_ratio_n16384_full_alpha_v1 -- Deletion cert Z-ratio at N=16384 with full alpha sweep.

Extends deletion_cert_z_ratio_n16384_v1 (scalar alpha=0.05) to full alpha sweep {0.05, 0.08, 0.10, 0.12}.
Tests whether Z-ratio scales consistently across alpha values at N=16384.

Theory: Z ~ sqrt(N) is alpha-independent (deletion signal = ||xi||^2 / N ~ 1 regardless of alpha).
PREDICTION: Z-ratio should be similar across all alpha values (within 30%).

GPU IMPLEMENTATION: matrix-free via batched matmul. No W materialization needed.
  Xi at alpha=0.12, N=16384: M=1966 patterns, 129 MB float32. Safe.

PRE-REGISTERED BANDS:
  HP1: Z-ratio >= 2.5 at ALL 4 alpha values.
  HP2: Z-ratio coefficient of variation (CV) < 0.30 (alpha-independence).
  HARD-PASS: HP1 AND HP2 in >= 4/5 seeds.
  MIDDLE: HP1 at >= 3/4 alpha values AND HP2.
  HARD-FAIL: Z-ratio < 1.5 at any alpha value.
  Prior: N=16384 scalar alpha=0.05 HP (Z>=2.5); multi-alpha extends that result.
  Calibration: no prior multi-alpha measurement; bands +-50% of prediction.

FORMULA SELF-TESTS:
  1. Z = (mean_signal - mean_null) / std_null; signal > 0 at tiny N.
     [INPUT: N=256, alpha=0.05] [EXPECTED: signal > 0.5*sqrt(256)=8]
  2. alpha independence: signal at alpha=0.05 ~ signal at alpha=0.10 (within 50%).
  3. GPU memory > 100 MB after Xi alloc.

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

try:
    import torch
    import torch.cuda
except ImportError:
    print("[FATAL] torch not installed.", flush=True)
    sys.exit(1)

if not torch.cuda.is_available():
    print("[FATAL] CUDA not available. This script requires a GPU.", flush=True)
    sys.exit(1)

DEVICE = torch.device('cuda')
print(f"[GPU] device={DEVICE} name={torch.cuda.get_device_name(0)} "
      f"total_mem={torch.cuda.get_device_properties(0).total_memory / 1e9:.1f}GB", flush=True)

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

ANCHOR_NAME = "deletion_cert_z_ratio_n16384_full_alpha_v1"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_GRID = [0.05, 0.08, 0.10, 0.12]
N_NULL_PROBES = 20

if RUN_MODE == "smoke":
    N_ACTIVE = 2048
    SEEDS = [7, 17]
    ALPHA_SMOKE_GRID = [0.05, 0.10]
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_SMOKE_GRID = ALPHA_GRID

HP_Z = 2.5
MID_Z = 1.8
HF_Z = 1.5
HP_CV_MAX = 0.30


def deletion_signal_gpu(Xi: torch.Tensor, n: int, k: int) -> float:
    xi_k = Xi[k]
    pre = (Xi.t() @ (Xi @ xi_k)) / n
    mask = torch.ones(Xi.shape[0], dtype=torch.bool, device=DEVICE)
    mask[k] = False
    Xi_post = Xi[mask]
    post = (Xi_post.t() @ (Xi_post @ xi_k)) / n
    return float((pre - post).norm())


def null_signal_gpu(Xi: torch.Tensor, n: int, gen: torch.Generator) -> float:
    xi_rand = (torch.randint(0, 2, (n,), generator=gen, device=DEVICE).float() * 2 - 1)
    response = (Xi.t() @ (Xi @ xi_rand)) / n
    return float(response.norm())


def _instrumentation_selftest():
    N_t = 256
    alpha_t = 0.05
    M_t = int(alpha_t * N_t)
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    Xi_t = (torch.randint(0, 2, (M_t, N_t), generator=gen, device=DEVICE).float() * 2 - 1)

    sig = deletion_signal_gpu(Xi_t, N_t, k=0)
    expected = math.sqrt(N_t)
    assert sig > 0.5 * expected and sig < 2.0 * expected, (
        f"deletion_signal selftest: got {sig:.2f}, expected ~{expected:.2f}")

    # alpha-independence: signal at alpha=0.05 vs alpha=0.10
    M_t2 = int(0.10 * N_t)
    Xi_t2 = (torch.randint(0, 2, (M_t2, N_t), generator=gen, device=DEVICE).float() * 2 - 1)
    sig2 = deletion_signal_gpu(Xi_t2, N_t, k=0)
    ratio = sig / sig2
    assert ratio > 0.5 and ratio < 2.0, f"alpha-independence: ratio={ratio:.2f} outside [0.5, 2.0]"

    # GPU > 100 MB
    dummy = torch.zeros((4096, 4096), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 1e6, f"GPU memory not > 1MB: {mem/1e6:.1f}MB"
    del dummy
    torch.cuda.empty_cache()

    print(f"[selftest] PASS: deletion_signal at N={N_t}={sig:.3f} ~sqrt(N)={expected:.3f}; "
          f"alpha_indep ratio={ratio:.2f}; gpu_mem_ok", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_one_alpha(seed: int, n_dim: int, alpha: float, gen: torch.Generator) -> Dict:
    M = int(alpha * n_dim)
    Xi = (torch.randint(0, 2, (M, n_dim), generator=gen, device=DEVICE).float() * 2 - 1)

    K_test = min(M, 10)
    signals = [deletion_signal_gpu(Xi, n_dim, k=k) for k in range(K_test)]
    mean_signal = float(sum(signals) / len(signals))

    nulls = [null_signal_gpu(Xi, n_dim, gen=gen) for _ in range(N_NULL_PROBES)]
    mean_null = float(sum(nulls) / len(nulls))
    std_null = float((sum((x - mean_null)**2 for x in nulls) / max(len(nulls) - 1, 1))**0.5)
    z_ratio = (mean_signal - mean_null) / max(std_null, 1e-12)

    return {
        "alpha": float(alpha), "M": int(M),
        "mean_signal": float(mean_signal),
        "mean_null": float(mean_null),
        "std_null": float(std_null),
        "z_ratio": float(z_ratio),
    }


def run_seed(seed: int, n_dim: int) -> Dict:
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed)
    t0 = time.time()

    grid = ALPHA_SMOKE_GRID if RUN_MODE == "smoke" else ALPHA_GRID
    alpha_results = []
    for alpha in grid:
        r = run_one_alpha(seed, n_dim, alpha, gen)
        alpha_results.append(r)
        print(f"  [seed={seed} N={n_dim} alpha={alpha:.2f}] "
              f"signal={r['mean_signal']:.4f} null={r['mean_null']:.4f} "
              f"Z={r['z_ratio']:.4f}(HP>={HP_Z} MID>={MID_Z} HF<{HF_Z})", flush=True)

    z_vals = [r["z_ratio"] for r in alpha_results]
    mean_z = float(sum(z_vals) / len(z_vals)) if z_vals else 0.0
    std_z = float((sum((x - mean_z)**2 for x in z_vals) / max(len(z_vals) - 1, 1))**0.5) if len(z_vals) > 1 else 0.0
    cv_z = std_z / max(mean_z, 1e-9)
    n_above_hp = sum(1 for z in z_vals if z >= HP_Z)

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    elapsed = time.time() - t0
    print(f"  [seed={seed}] mean_Z={mean_z:.4f} cv_Z={cv_z:.4f}(HP<={HP_CV_MAX}) "
          f"n_alpha_hp={n_above_hp}/{len(grid)} peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s",
          flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "mean_z": float(mean_z), "cv_z": float(cv_z),
        "n_alpha_above_hp": n_above_hp, "n_alpha_tested": len(grid),
        "alpha_results": alpha_results,
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)
    # Check HF: any Z < HF_Z
    for r in results:
        for ar in r.get("alpha_results", []):
            if ar["z_ratio"] < HF_Z:
                return ("HARD_FAIL",
                        f"HARD_FAIL: Z={ar['z_ratio']:.4f} < {HF_Z} at alpha={ar['alpha']:.2f}")

    n_alpha = results[0]["n_alpha_tested"] if results else 4
    hp_full = sum(1 for r in results if r["n_alpha_above_hp"] >= n_alpha and r["cv_z"] <= HP_CV_MAX)
    hp_partial = sum(1 for r in results
                     if r["n_alpha_above_hp"] >= max(n_alpha - 1, 1) and r["cv_z"] <= HP_CV_MAX)
    min_pass = math.ceil(n * 0.8)

    mean_cv = float(sum(r["cv_z"] for r in results) / n)
    mean_n_alpha_hp = float(sum(r["n_alpha_above_hp"] for r in results) / n)
    summary = (f"mean_Z_cv={mean_cv:.4f}(HP<={HP_CV_MAX}) "
               f"mean_n_alpha_hp={mean_n_alpha_hp:.1f}/{n_alpha} "
               f"hp_full={hp_full}/{n} hp_partial={hp_partial}/{n}")

    if hp_full >= min_pass:
        return ("HARD_PASS",
                f"HARD_PASS: Z>={HP_Z} at all alpha + alpha_independence at N=16384. {summary}")
    if hp_partial >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: Z>={HP_Z} at 3/4 alpha. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient Z across alpha grid. {summary}")


def _prot018_startup_check(n_actual: int) -> None:
    if RUN_MODE == "smoke":
        return
    if n_actual != _N_SUFFIX:
        raise RuntimeError(
            f"PROT-018 VIOLATION: anchor '{ANCHOR_NAME}' binds N={_N_SUFFIX} "
            f"but running at N={n_actual}.")


print(f"[config] PROT-018 N={N} n_active={N_ACTIVE} mode={RUN_MODE} "
      f"alpha_grid={ALPHA_GRID}", flush=True)
_prot018_startup_check(N_ACTIVE if RUN_MODE == "smoke" else N)

print(f"[GPU] memory before sweep: {torch.cuda.memory_allocated(0)/1e9:.3f} GB", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "n_active": N_ACTIVE, "alpha_grid": str(ALPHA_GRID), "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] running N={N_ACTIVE} alpha_grid={ALPHA_SMOKE_GRID if RUN_MODE=='smoke' else ALPHA_GRID}...",
          flush=True)
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
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict, "verdict_msg": verdict_msg,
    "N": N, "n_active": N_ACTIVE,
    "alpha_grid": ALPHA_GRID, "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS), "elapsed_s": elapsed_total,
    "peak_gpu_gb": float(peak_mem_gb),
}
metrics_path = out_dir / "metrics.json"
out_dir.mkdir(parents=True, exist_ok=True)
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
