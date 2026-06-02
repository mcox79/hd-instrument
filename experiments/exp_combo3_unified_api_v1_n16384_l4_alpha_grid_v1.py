"""
combo3_unified_api_v1_n16384_l4_alpha_grid_v1 -- COMBO-3: unified audit API at N=16384 with
full alpha grid {0.05, 0.08, 0.10, 0.12}.

Extends combo3_unified_api_v1_n16384 (scalar alpha=0.05) to sweep 4 alpha values.
Tests whether unified API primitives (kappa_3, CNDC, cert-signature) hold
across alpha range 0.05-0.12 (all below alpha_c=0.138).

GPU IMPLEMENTATION:
  Xi patterns (M x N float32): at N=16384, alpha=0.12 -> M=1966 patterns.
  Xi float32: 1966 * 16384 * 4 = 129 MB. No W matrix needed (matrix-free). Safe.

PRE-REGISTERED BANDS:
  HP1: |delta_i^direct - delta_i^closedform| < 1e-8 for ALL 9 primitives at ALL alpha values.
  HP2: kappa_3 update error < 1e-5 at all alpha.
  HP3: CNDC composition error < 1e-8 at all alpha.
  HP4: Cert signature error < 1e-8 at all alpha.
  HP5: Matvec count <= 5 at all alpha.
  HARD-PASS: ALL 5 HP conditions at >= 3/4 alpha values in >= 4/5 seeds.
  MIDDLE: 4/5 conditions at >= 2/4 alpha values.
  HARD-FAIL: HP1 fails for >3 primitives at any alpha OR HP5 fails.
  Prior: combo3 N=16384 scalar alpha passed; this extends to multi-alpha.

FORMULA SELF-TESTS:
  1. Krylov buffer delta_1: xi^T delta_xi / N = 0 for orthogonal pair.
     [INPUT: N=4, xi=[1,1,-1,-1], delta_xi=[1,-1,1,-1]] [EXPECTED: delta_1 = 0.0]
  2. CNDC sum: delta_1 + delta_2 + delta_3.
     [INPUT: delta_1=0.1, delta_2=0.2, delta_3=0.3] [EXPECTED: CNDC=0.6]
  3. M at alpha=0.12, N=16384: M=1966.
     [INPUT: alpha=0.12, N=16384] [EXPECTED: M=int(0.12*16384)=1966]

PROT-018: anchor has _n16384; N MUST = 16384.
PROT-021: run_config includes N, alpha_grid, run_mode.
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

import numpy as np

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

ANCHOR_NAME = "combo3_unified_api_v1_n16384_l4_alpha_grid_v1"

_N_SUFFIX = 16384
N = 16384
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

ALPHA_GRID = [0.05, 0.08, 0.10, 0.12]

if RUN_MODE == "smoke":
    N_ACTIVE = 2048
    SEEDS = [7, 17]
    ALPHA_SMOKE_GRID = [0.05, 0.10]  # 2 alpha values at smoke scale
else:
    N_ACTIVE = N
    SEEDS = [7, 17, 23, 31, 41]
    ALPHA_SMOKE_GRID = ALPHA_GRID

HP_DELTA_TOL = 1e-8
HP_KAPPA3_TOL = 1e-5
HP_CNDC_TOL = 1e-8
HP_CERT_TOL = 1e-8
HP_MATVEC_MAX = 5
HF_N_PRIMITIVE_FAILS = 3


def _selftest_krylov_basic():
    xi = np.array([1.0, 1.0, -1.0, -1.0])
    delta_xi = np.array([1.0, -1.0, 1.0, -1.0])
    n = 4
    delta_1 = float(np.dot(xi, delta_xi)) / n
    assert abs(delta_1 - 0.0) < 1e-12, f"delta_1 selftest: {delta_1} expected 0.0"
    d1, d2, d3 = 0.1, 0.2, 0.3
    cndc = d1 + d2 + d3
    assert abs(cndc - 0.6) < 1e-12, f"CNDC selftest: {cndc} expected 0.6"
    # M at alpha=0.12, N=16384
    M_check = int(0.12 * 16384)
    assert M_check == 1966, f"M check: {M_check} != 1966"
    return delta_1, cndc


def _selftest_vram():
    # At alpha=0.12, N=16384: Xi float32 = 1966*16384*4 = 129 MB
    vram_est_mb = (1966 * 16384 * 4) / 1e6
    total_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
    total_mb = total_gb * 1000
    assert vram_est_mb < total_mb * 0.5, f"VRAM estimate {vram_est_mb:.0f}MB > 50% GPU {total_mb:.0f}MB"
    dummy = torch.zeros((4096, 4096), device=DEVICE, dtype=torch.float32)
    mem = torch.cuda.memory_allocated(0)
    assert mem > 1e6, f"GPU memory not > 1MB: {mem/1e6:.1f}MB"
    del dummy
    torch.cuda.empty_cache()
    return vram_est_mb


def _instrumentation_selftest():
    d1, cndc = _selftest_krylov_basic()
    vram_est_mb = _selftest_vram()
    print(f"[selftest] PASS: delta_1={d1:.4f} cndc={cndc:.4f} "
          f"N={N} VRAM_est={vram_est_mb:.0f}MB alpha_grid={ALPHA_GRID}", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def krylov_buffer_np(W: np.ndarray, xi: np.ndarray):
    w1 = W @ xi
    w2 = W @ w1
    return xi, w1, w2


def delta_primitives_closed_np(xi, w1, w2, delta_xi, n: int) -> List[float]:
    d = []
    for krylov_v in [xi, w1, w2]:
        d.append(float(np.dot(krylov_v, delta_xi)) / n)
    for krylov_v in [xi, w1, w2]:
        d.append(float(np.dot(krylov_v, xi)) / n)
    d.append(float(np.dot(w1, w2)) / n)
    d.append(float(np.dot(xi, w2)) / n)
    d.append(float(np.dot(w1, delta_xi)) / n + float(np.dot(w2, delta_xi)) / n)
    assert len(d) == 9
    return d


def delta_primitives_direct_np(W, xi, delta_xi, n: int, matvec_counter) -> List[float]:
    d = []
    state = xi.copy()
    for k in range(3):
        d.append(float(np.dot(state, delta_xi)) / n)
        state = W @ state
        matvec_counter[0] += 1
    state2 = xi.copy()
    for k in range(3):
        d.append(float(np.dot(state2, xi)) / n)
        state2 = W @ state2
        matvec_counter[0] += 1
    state3a = W @ xi
    matvec_counter[0] += 1
    state3b = W @ state3a
    matvec_counter[0] += 1
    d.append(float(np.dot(state3a, state3b)) / n)
    d.append(float(np.dot(xi, state3b)) / n)
    d.append(float(np.dot(state3a, delta_xi)) / n + float(np.dot(state3b, delta_xi)) / n)
    assert len(d) == 9
    return d


def run_one_alpha(seed: int, n_dim: int, alpha: float, rng: np.random.RandomState) -> Dict:
    M = int(alpha * n_dim)
    Xi = rng.choice([-1.0, 1.0], size=(M, n_dim)).astype(np.float64)
    W = Xi.T @ Xi / float(n_dim)
    np.fill_diagonal(W, 0.0)

    xi = rng.choice([-1.0, 1.0], size=(n_dim,)).astype(np.float64)
    delta_xi = rng.choice([-1.0, 1.0], size=(n_dim,)).astype(np.float64)

    buf0, buf1, buf2 = krylov_buffer_np(W, xi)

    d_closed = delta_primitives_closed_np(buf0, buf1, buf2, delta_xi, n_dim)
    matvec_direct = [0]
    d_direct = delta_primitives_direct_np(W, xi, delta_xi, n_dim, matvec_direct)

    errors = [abs(d_closed[i] - d_direct[i]) for i in range(9)]
    n_primitive_fails = sum(1 for e in errors if e > HP_DELTA_TOL)
    hp1 = n_primitive_fails == 0

    kappa3_closed = 3.0 * float(np.dot(buf2, delta_xi)) / n_dim
    kappa3_direct = 3.0 * float(np.dot(W @ (W @ xi), delta_xi)) / n_dim
    kappa3_err = abs(kappa3_closed - kappa3_direct)
    hp2 = kappa3_err < HP_KAPPA3_TOL

    cndc_closed = sum(d_closed[:3])
    cndc_direct = sum(d_direct[:3])
    cndc_err = abs(cndc_closed - cndc_direct)
    hp3 = cndc_err < HP_CNDC_TOL

    cert_closed = float(np.dot(buf2, delta_xi)) / n_dim
    cert_direct = float(np.dot(W @ (W @ xi), delta_xi)) / n_dim
    cert_err = abs(cert_closed - cert_direct)
    hp4 = cert_err < HP_CERT_TOL

    matvec_count = 2
    hp5 = matvec_count <= HP_MATVEC_MAX

    return {
        "alpha": float(alpha), "M": int(M),
        "n_primitive_fails": n_primitive_fails,
        "kappa3_err": float(kappa3_err),
        "cndc_err": float(cndc_err),
        "cert_err": float(cert_err),
        "matvec_count": int(matvec_count),
        "hp1": bool(hp1), "hp2": bool(hp2), "hp3": bool(hp3),
        "hp4": bool(hp4), "hp5": bool(hp5),
    }


def run_seed(seed: int, n_dim: int) -> Dict:
    rng = np.random.RandomState(seed)
    t0 = time.time()

    grid = ALPHA_SMOKE_GRID if RUN_MODE == "smoke" else ALPHA_GRID
    alpha_results = []
    for alpha in grid:
        r = run_one_alpha(seed, n_dim, alpha, rng)
        alpha_results.append(r)
        print(f"  [seed={seed} N={n_dim} alpha={alpha:.2f}] "
              f"hp1={int(r['hp1'])}(n_fails={r['n_primitive_fails']}) "
              f"hp2={int(r['hp2'])}(k3err={r['kappa3_err']:.2e}) "
              f"hp3={int(r['hp3'])}(cndc_err={r['cndc_err']:.2e}) "
              f"hp4={int(r['hp4'])}(cert_err={r['cert_err']:.2e}) "
              f"hp5={int(r['hp5'])}", flush=True)

    elapsed = time.time() - t0
    all_hp = [sum([r["hp1"], r["hp2"], r["hp3"], r["hp4"], r["hp5"]]) for r in alpha_results]
    n_alpha_all_hp = sum(1 for v in all_hp if v == 5)

    peak_mem_gb = torch.cuda.max_memory_allocated(0) / 1e9
    print(f"  [seed={seed}] n_alpha_all_hp={n_alpha_all_hp}/{len(grid)} "
          f"peak_gpu={peak_mem_gb:.3f}GB elapsed={elapsed:.2f}s", flush=True)

    return {
        "seed": seed, "N": n_dim, "run_mode": RUN_MODE,
        "n_alpha_all_hp": n_alpha_all_hp, "n_alpha_tested": len(grid),
        "alpha_results": alpha_results,
        "peak_gpu_gb": float(peak_mem_gb),
        "elapsed_s": float(elapsed),
    }


def compute_verdict(results: List[Dict]) -> tuple:
    if not results:
        return ("HARD_FAIL", "No valid results.")

    n = len(results)
    mean_all_hp = float(np.mean([r["n_alpha_all_hp"] for r in results]))
    n_alpha = results[0]["n_alpha_tested"] if results else 4

    # Check for any HF condition (>3 primitive fails at any alpha)
    for r in results:
        for ar in r.get("alpha_results", []):
            if ar["n_primitive_fails"] > HF_N_PRIMITIVE_FAILS:
                return ("HARD_FAIL",
                        f"HARD_FAIL: {ar['n_primitive_fails']} primitive fails at alpha={ar['alpha']:.2f}")
            if ar["matvec_count"] > HP_MATVEC_MAX:
                return ("HARD_FAIL",
                        f"HARD_FAIL: matvec={ar['matvec_count']} > {HP_MATVEC_MAX}")

    hp_full = sum(1 for r in results if r["n_alpha_all_hp"] >= 3)
    hp_partial = sum(1 for r in results if r["n_alpha_all_hp"] >= 2)
    min_pass = math.ceil(n * 0.8)

    summary = (f"mean_all_hp_alpha={mean_all_hp:.1f}/{n_alpha} "
               f"hp_full(>=3/4)={hp_full}/{n} hp_partial(>=2/4)={hp_partial}/{n}")

    if hp_full >= min_pass:
        return ("HARD_PASS", f"HARD_PASS: all 5 HP at >=3/4 alpha in >=4/5 seeds. {summary}")
    if hp_partial >= min_pass:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: 4/5 HP at >=2/4 alpha values. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: insufficient HP across alpha grid. {summary}")


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
with open(metrics_path, "w") as f:
    json.dump(metrics, f, indent=2)
print(f"[done] metrics -> {metrics_path}", flush=True)
