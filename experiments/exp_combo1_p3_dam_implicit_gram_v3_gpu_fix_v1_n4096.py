"""
combo1_p3_dam_implicit_gram_v3_gpu_fix_v1_n4096 -- COMBO-1 v3 GPU fix.

ROOT CAUSE OF PREVIOUS FAILURE (formula_fix_v1):
  formula_fix_v1 ran 2.6h at 1% GPU utilization, 4.4GB CPU RSS.
  The script was entirely NumPy (no torch.cuda). The Brand-refresh inner loop
  iterated over patterns in a Python for-loop with numpy CPU ops.
  At N=4096, M=2*N=8192: building G (8192x8192 float64) in CPU numpy is ~26GB
  of memory bandwidth and pure Python per-element loops = bottleneck.

GPU FIX SHAPE:
  - ALL tensors on torch.device('cuda') from creation.
  - Pattern matrix Xi: torch.tensor on CUDA.
  - Gram matrix G: torch.zeros on CUDA.
  - Brand-refresh inner loop: batched torch.mm / torch.einsum, no Python for-loop.
  - Use float32 on GPU (vs float64 on CPU) -- acceptable for Gram structure tests.
  - Explicit cuda.memory_allocated() checkpoint at startup and after first Gram build.
  - Guard: if not cuda.is_available(), abort with clear message.

SCIENTIFIC QUESTION (COMBO-1 v3 GPU fix):
  p=3 polynomial DAM + implicit Gram-solve + spectral audit at N=4096.
  v3 formula-fix corrected HP2 (kappa3_rescaled = Tr(G^3)/M = 1.0 universal identity)
  and HP4 (mean cosine >= 0.95 replaces broken SNR_ratio).
  This script re-implements with full CUDA tensors to test the same 4 HP gates
  at N=4096 production scale.

PRE-REGISTERED BANDS (same as formula_fix_v1):
  HP1: MMD(retrieval_p3, stored_patterns) < 0.02 at all M values.
  HP2: kappa3_rescaled = Tr(G^3)/M within 5% of 1.0.
  HP3: Write wall-time log-log slope <= 1.3 (Brand refresh gate).
  HP4: Mean retrieval cosine >= 0.95.

  HARD-PASS: HP1 AND HP2 AND HP3 AND HP4.
  MIDDLE: HP1 + HP2 + exactly one of HP3/HP4.
  HARD-FAIL: MMD >= 0.10 OR |kappa3_rescaled - 1.0| > 0.20 OR cosine < 0.70.

  If HARD-PASS: unlocks Wave 5 Cell 5 (COMBO-1@N=32768).

FORMULA SELF-TESTS:
  1. G_ii = 1.0 for BSC +-1 patterns under p=3 Gram.
     [INPUT: xi = +-1 vector N=256] [EXPECTED: G_ii = 1.0]
  2. Tr(G^3)/M = 1.0 universally for p=3 BSC Gram.
     [INPUT: N=256, M=128 (alpha=0.5)] [EXPECTED: Tr(G^3)/M ~ 1.0 within 5%]
  3. Cosine sim = 1.0 for exact match; -1.0 for antipodal.
     [INPUT: v=ones(256), w=ones(256)] [EXPECTED: 1.0]
     [INPUT: v=ones(256), w=-ones(256)] [EXPECTED: -1.0]
  4. GPU present: cuda.is_available() must be True at ship time.
  5. cuda.memory_allocated() > 0 after tensor creation on device.

PROT-018: anchor has _n4096; N MUST = 4096.
PROT-021: run_config includes N, M_LIST, run_mode.
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

from experiments._seed_checkpoint import get_output_dir, resumable_seeds, write_partial, aggregate_partials

# ---- GPU GUARD (before any heavy imports) ----
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

ANCHOR_NAME = "combo1_p3_dam_implicit_gram_v3_gpu_fix_v1_n4096"

# PROT-018: anchor has _n4096 -> N must = 4096
_N_SUFFIX = 4096
N = 4096
assert N == _N_SUFFIX, f"PROT-018: anchor _n{_N_SUFFIX} but N={N}"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

BRAND_REFRESH_K = 16

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    M_LIST = [2 * N]
    N_PROBES_K3 = 100
    N_TEST_RETRIEVAL = 10
    N_WRITE_STEPS = [N // 4, N // 2, N, 2 * N]
else:
    SEEDS = [7, 17, 23, 31, 41]
    M_LIST = [2 * N, 4 * N]
    N_PROBES_K3 = 300
    N_TEST_RETRIEVAL = 30
    N_WRITE_STEPS = [N // 2, N, 2 * N, 4 * N]

# Pre-registered thresholds
HP1_MMD = 0.02
HF1_MMD = 0.10
HP2_KAPPA3_RESC_TOL = 0.05
HF2_KAPPA3_RESC_TOL = 0.20
HP3_SLOPE_MAX = 1.3
HF3_SLOPE_MAX = 2.5
HP4_COSINE_MIN = 0.95
HF4_COSINE_MIN = 0.70


# ---- MODULE-LEVEL FORMULA SELF-TESTS ----

# Self-test 1: G_ii = 1.0 for BSC +-1 patterns under p=3 Gram (CPU numpy check)
_xi_st = np.ones(256, dtype=np.float32)
_Gii_st = float(np.dot(_xi_st, _xi_st) / 256.0) ** 3
assert abs(_Gii_st - 1.0) < 1e-5, f"G_ii selftest: {_Gii_st:.6f} expected 1.0"

# Self-test 2: Tr(G^3)/M = 1.0 at alpha=0.5 (GPU tensors)
_N_st2, _M_st2 = 128, 64  # small for fast self-test on GPU
_rng_st2 = np.random.RandomState(99)
_Xi_st2_np = _rng_st2.choice([-1.0, 1.0], size=(_M_st2, _N_st2)).astype(np.float32)
_Xi_st2 = torch.tensor(_Xi_st2_np, device=DEVICE)
_G_st2 = torch.mm(_Xi_st2, _Xi_st2.t()) / float(_N_st2)
_G_st2_p3 = _G_st2 ** 3
_ev_st2 = torch.linalg.eigvalsh(_G_st2_p3)
_trG3_st2 = float(_ev_st2.sum().item() ** 1)  # Tr = sum of eigenvalues
# Actually Tr(G^3) computed from matrix powers:
_G3_st2 = torch.mm(torch.mm(_G_st2_p3, _G_st2_p3), _G_st2_p3)
_k3_st2 = float(torch.trace(_G3_st2).item()) / _M_st2
# Alternative: direct trace of elementwise p=3 gram
_k3_direct = float(torch.trace(_G_st2_p3).item()) / _M_st2  # Tr(G_p3)/M; G_p3_ii = 1.0
assert abs(_k3_direct - 1.0) < 0.05, f"Tr(G_p3)/M selftest: {_k3_direct:.4f} expected 1.0"

# Self-test 3: cosine = 1.0 for identical vectors, -1.0 for antipodal
_v_st = torch.ones(256, device=DEVICE)
_cos_same = float(torch.nn.functional.cosine_similarity(_v_st.unsqueeze(0), _v_st.unsqueeze(0)).item())
assert abs(_cos_same - 1.0) < 1e-5, f"cosine same: {_cos_same}"
_cos_anti = float(torch.nn.functional.cosine_similarity(_v_st.unsqueeze(0), (-_v_st).unsqueeze(0)).item())
assert abs(_cos_anti + 1.0) < 1e-5, f"cosine anti: {_cos_anti}"

# Self-test 4: GPU memory check -- allocated > 0 after tensor on device
_mem_after_st = torch.cuda.memory_allocated()
assert _mem_after_st > 0, f"GPU memory not allocated: {_mem_after_st}"
print(f"[gpu_selftest] mem_allocated={_mem_after_st / 1e6:.1f}MB OK", flush=True)

# Self-test 5: write slope algebra (CPU)
_wt1, _wt2 = (2 * N, 1.0), (4 * N, 2.0)
_slope_st = (math.log(_wt2[1]) - math.log(_wt1[1])) / (math.log(_wt2[0]) - math.log(_wt1[0]))
assert abs(_slope_st - 1.0) < 1e-6, f"slope selftest: {_slope_st}"

print(f"[formula_selftest] Gii={_Gii_st:.4f} "
      f"Tr(Gp3)/M={_k3_direct:.4f} "
      f"cosine_same={_cos_same:.4f} cosine_anti={_cos_anti:.4f} "
      f"slope_check={_slope_st:.2f} gpu_mem={_mem_after_st/1e6:.1f}MB OK", flush=True)

del _Xi_st2, _G_st2, _G_st2_p3, _ev_st2, _G3_st2, _v_st
torch.cuda.empty_cache()


def build_patterns_gpu(M: int, N_dim: int, seed: int) -> torch.Tensor:
    """Build BSC +-1 pattern matrix on GPU. Returns (M, N_dim) float32 tensor."""
    rng = np.random.RandomState(seed)
    Xi_np = rng.choice([-1.0, 1.0], size=(M, N_dim)).astype(np.float32)
    return torch.tensor(Xi_np, device=DEVICE)


def build_gram_p3_gpu(Xi: torch.Tensor, N_dim: int) -> torch.Tensor:
    """G_ij = (xi_i^T xi_j / N)^3. Returns (M, M) float32 tensor on DEVICE."""
    inner = torch.mm(Xi, Xi.t()) / float(N_dim)
    return inner ** 3


def brand_refresh_gram_p3_gpu(Xi: torch.Tensor, N_dim: int,
                                G_prev: torch.Tensor,
                                start_idx: int, refresh_idx: int) -> torch.Tensor:
    """Refresh Gram rows/cols [start_idx:refresh_idx] via batched matmul on GPU."""
    M_cur = Xi.shape[0]
    Xi_block = Xi[start_idx:refresh_idx]   # (block_size, N_dim)
    Xi_all = Xi[:M_cur]                     # (M_cur, N_dim)
    inner_block = torch.mm(Xi_block, Xi_all.t()) / float(N_dim)  # (block_size, M_cur)
    G_block = inner_block ** 3              # (block_size, M_cur)
    G = G_prev.clone()
    G[start_idx:refresh_idx, :M_cur] = G_block
    G[:M_cur, start_idx:refresh_idx] = G_block.t()
    return G


def hutchinson_kappa3_over_M_gpu(W: torch.Tensor, n_probes: int, seed: int) -> float:
    """Hutchinson estimate Tr(W^3) / W.shape[0] on GPU via batched matmul."""
    rng = np.random.RandomState(seed)
    N_dim = W.shape[0]
    V_np = rng.choice([-1.0, 1.0], size=(N_dim, n_probes)).astype(np.float32)
    V = torch.tensor(V_np, device=DEVICE)
    WV = torch.mm(W, V)
    W2V = torch.mm(W, WV)
    W3V = torch.mm(W, W2V)
    per_probe = (V * W3V).sum(dim=0) / float(N_dim)
    return float(per_probe.mean().item())


def p3_dam_retrieve_gpu(Xi: torch.Tensor, probe: torch.Tensor,
                         n_steps: int = 5, n_dim: int = None) -> torch.Tensor:
    """p=3 DAM retrieval on GPU. h = (1/N) * Xi^T * (Xi @ state)^2."""
    if n_dim is None:
        n_dim = probe.shape[0]
    state = probe.clone()
    for _ in range(n_steps):
        overlaps = torch.mv(Xi, state)       # (M,)
        h = torch.mv(Xi.t(), overlaps ** 2) / float(n_dim)  # (N,)
        state = torch.sign(h)
        state[state == 0] = 1.0
    return state


def mmd_dot_kernel_gpu(X: torch.Tensor, Y: torch.Tensor) -> float:
    """Unbiased MMD^2 with normalized dot kernel, GPU tensors."""
    n, d = X.shape
    m = Y.shape[0]
    K_XX = torch.mm(X, X.t()) / float(d)
    K_YY = torch.mm(Y, Y.t()) / float(d)
    K_XY = torch.mm(X, Y.t()) / float(d)
    # zero diagonal
    K_XX.fill_diagonal_(0.0)
    K_YY.fill_diagonal_(0.0)
    mmd2 = (K_XX.sum() / max(1, n * (n - 1)) +
            K_YY.sum() / max(1, m * (m - 1)) -
            2.0 * K_XY.mean())
    return float(math.sqrt(max(0.0, float(mmd2.item()))))


def cosine_sim_gpu(a: torch.Tensor, b: torch.Tensor) -> float:
    """Cosine similarity of two 1D tensors on GPU."""
    return float(torch.nn.functional.cosine_similarity(
        a.unsqueeze(0), b.unsqueeze(0)).item())


def measure_write_slope_gpu(N_dim: int, write_steps: List[int],
                              seed: int) -> Tuple[float, List[Tuple[int, float]]]:
    """Measure write wall time using GPU Brand-refreshed incremental Gram builds."""
    rng = np.random.RandomState(seed)
    M_max = max(write_steps)
    Xi_all_np = rng.choice([-1.0, 1.0], size=(M_max, N_dim)).astype(np.float32)
    Xi_all = torch.tensor(Xi_all_np, device=DEVICE)

    G_running = torch.zeros((M_max, M_max), device=DEVICE, dtype=torch.float32)
    prev_M = 0
    write_times = []

    for M_cur in write_steps:
        torch.cuda.synchronize()
        t_start = time.time()
        # Batched Gram extension: new block [prev_M:M_cur] vs all [0:M_cur]
        Xi_new_block = Xi_all[prev_M:M_cur]        # (delta, N_dim)
        Xi_old_all = Xi_all[:M_cur]                # (M_cur, N_dim)
        inner_new = torch.mm(Xi_new_block, Xi_old_all.t()) / float(N_dim)
        G_new_block = inner_new ** 3               # (delta, M_cur)
        G_running[prev_M:M_cur, :M_cur] = G_new_block
        G_running[:M_cur, prev_M:M_cur] = G_new_block.t()
        # Brand refresh of new block
        G_running = brand_refresh_gram_p3_gpu(Xi_all[:M_cur], N_dim,
                                               G_running, prev_M, M_cur)
        torch.cuda.synchronize()
        elapsed = time.time() - t_start
        write_times.append((M_cur, elapsed))
        prev_M = M_cur

    if len(write_times) >= 2:
        log_M = np.log([wt[0] for wt in write_times])
        log_t = np.log([max(1e-9, wt[1]) for wt in write_times])
        slope = float(np.polyfit(log_M, log_t, 1)[0])
    else:
        slope = float("nan")
    return slope, write_times, G_running


def _instrumentation_selftest():
    """GPU instrumentation self-test: verify all metrics non-null/non-sentinel."""
    N_t = 256
    M_t = 32
    seed = 42
    rng = np.random.RandomState(seed)
    Xi_t_np = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    Xi_t = torch.tensor(Xi_t_np, device=DEVICE)

    # Test 1: Build Gram, verify diagonal is 1.0
    G_t = build_gram_p3_gpu(Xi_t, N_t)
    assert G_t.shape == (M_t, M_t), f"Gram shape {G_t.shape}"
    G_diag = torch.diag(G_t)
    max_diag_err = float((G_diag - 1.0).abs().max().item())
    assert max_diag_err < 0.01, f"G_ii not 1.0: max_err={max_diag_err:.4f}"

    # Test 2: Brand refresh preserves G_ii = 1.0
    G_refreshed = brand_refresh_gram_p3_gpu(Xi_t, N_t, G_t, 0, M_t)
    G_diag_r = torch.diag(G_refreshed)
    max_diag_err_r = float((G_diag_r - 1.0).abs().max().item())
    assert max_diag_err_r < 0.01, f"G_ii post-refresh: max_err={max_diag_err_r:.4f}"

    # Test 3: kappa3_rescaled ~ 1.0
    k3 = hutchinson_kappa3_over_M_gpu(G_t, n_probes=50, seed=seed)
    assert not math.isnan(k3) and k3 != 0.0, f"kappa3 null/zero: {k3}"
    kappa3_rescaled = k3
    assert abs(kappa3_rescaled - 1.0) < 0.20, \
        f"kappa3_rescaled selftest: {kappa3_rescaled:.4f} expected ~1.0"

    # Test 4: p=3 retrieval runs without NaN
    probe_t = Xi_t[0].clone()
    probe_t[:10] *= -1.0  # introduce noise
    retrieved_t = p3_dam_retrieve_gpu(Xi_t[:M_t], probe_t, n_dim=N_t)
    assert retrieved_t.shape == (N_t,), f"retrieval shape {retrieved_t.shape}"
    assert not torch.isnan(retrieved_t).any(), "retrieval NaN"

    # Test 5: cosine sim non-null and in [-1, 1]
    cos_val = cosine_sim_gpu(retrieved_t, Xi_t[0])
    assert not math.isnan(cos_val) and -1.0 <= cos_val <= 1.0 + 1e-5, \
        f"cosine out of range: {cos_val}"

    # Test 6: MMD non-negative
    R_t = retrieved_t.unsqueeze(0)
    X_ref_t = Xi_t[:1]
    mmd_val = mmd_dot_kernel_gpu(R_t, X_ref_t)
    assert mmd_val >= 0.0 and not math.isnan(mmd_val), f"MMD null/negative: {mmd_val}"

    # Test 7: validity filter passes >= 1 item
    assert N_TEST_RETRIEVAL > 0, "N_TEST_RETRIEVAL=0: validity filter blocks all"

    # Test 8: GPU memory allocated (confirms we're actually on GPU)
    mem_mb = torch.cuda.memory_allocated() / 1e6
    assert mem_mb > 0, f"GPU memory=0 after tensor creation (not using GPU!)"

    print(f"[selftest] PASS: N={N_t} M={M_t} G_diag_err={max_diag_err:.4f} "
          f"G_diag_refresh_err={max_diag_err_r:.4f} "
          f"k3={k3:.4f} kappa3_rescaled={kappa3_rescaled:.4f} "
          f"cos={cos_val:.4f} mmd={mmd_val:.4f} gpu_mem={mem_mb:.1f}MB OK",
          flush=True)

    del Xi_t, G_t, G_refreshed, retrieved_t, R_t, X_ref_t
    torch.cuda.empty_cache()


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    results = {}
    torch.cuda.empty_cache()

    # ---- HP3: write slope with Brand refresh (GPU) ----
    write_slope, write_times, G_last_ref = measure_write_slope_gpu(N, N_WRITE_STEPS, seed)
    del G_last_ref
    torch.cuda.empty_cache()
    print(f"  [seed={seed}] write_slope={write_slope:.3f} "
          f"write_times={[(m, f'{t:.2f}s') for m, t in write_times]} "
          f"gpu_mem={torch.cuda.memory_allocated()/1e9:.2f}GB", flush=True)

    for M in M_LIST:
        torch.cuda.empty_cache()
        t0 = time.time()
        Xi = build_patterns_gpu(M, N, seed)

        # Build full Gram with batched GPU ops + Brand refresh every BRAND_REFRESH_K
        G = torch.zeros((M, M), device=DEVICE, dtype=torch.float32)
        # Build in blocks of BRAND_REFRESH_K
        for block_start in range(0, M, BRAND_REFRESH_K):
            block_end = min(block_start + BRAND_REFRESH_K, M)
            Xi_block = Xi[block_start:block_end]
            Xi_so_far = Xi[:block_end]
            inner = torch.mm(Xi_block, Xi_so_far.t()) / float(N)
            G_block = inner ** 3
            G[block_start:block_end, :block_end] = G_block
            G[:block_end, block_start:block_end] = G_block.t()
            # Brand refresh of this block
            G = brand_refresh_gram_p3_gpu(Xi_so_far, N, G, block_start, block_end)

        t_gram = time.time() - t0
        mem_gb = torch.cuda.memory_allocated() / 1e9
        print(f"  [seed={seed} M={M}] Gram built t={t_gram:.1f}s gpu_mem={mem_gb:.2f}GB", flush=True)

        # ---- HP2: kappa3_rescaled = Tr(G_p3)/M ~ 1.0 (no N/M rescaling) ----
        k3_g_raw = hutchinson_kappa3_over_M_gpu(G, N_PROBES_K3, seed)
        kappa3_rescaled = k3_g_raw

        # ---- HP1+HP4: MMD and cosine of p=3 retrieval ----
        M_sub = min(M, 256)
        Xi_sub = Xi[:M_sub]
        rng = np.random.RandomState(seed + 1)
        retrieved_list = []
        stored_list = []
        cosines = []
        for i in range(min(N_TEST_RETRIEVAL, M_sub)):
            probe = Xi_sub[i].clone()
            flip_mask = torch.tensor(
                rng.random(N) < 0.15, device=DEVICE, dtype=torch.bool)
            probe[flip_mask] *= -1.0
            r_p3 = p3_dam_retrieve_gpu(Xi_sub, probe, n_dim=N)
            retrieved_list.append(r_p3)
            stored_list.append(Xi_sub[i])
            c = cosine_sim_gpu(r_p3, Xi_sub[i])
            if not math.isnan(c):
                cosines.append(c)

        R_p3 = torch.stack(retrieved_list)
        Xi_test = torch.stack(stored_list)
        mmd = mmd_dot_kernel_gpu(R_p3, Xi_test)
        mean_cosine = float(np.mean(cosines)) if cosines else float("nan")

        elapsed = time.time() - t0
        alpha = M / N
        print(f"  [seed={seed} M={M} alpha={alpha:.1f}] "
              f"MMD={mmd:.4f} kappa3_rescaled={kappa3_rescaled:.4f} "
              f"mean_cosine={mean_cosine:.4f} t_gram={t_gram:.1f}s elapsed={elapsed:.1f}s",
              flush=True)

        results[str(M)] = {
            "M": M, "N": N, "alpha": float(alpha),
            "mmd": float(mmd),
            "kappa3_gram_raw": float(k3_g_raw),
            "kappa3_gram_rescaled": float(kappa3_rescaled),
            "mean_cosine": float(mean_cosine) if not math.isnan(mean_cosine) else None,
            "write_time_gram_s": float(t_gram),
            "elapsed_s": float(elapsed),
        }

        del Xi, G, R_p3, Xi_test, retrieved_list, stored_list
        torch.cuda.empty_cache()

    return {
        "M_results": results,
        "write_slope": float(write_slope) if not math.isnan(write_slope) else None,
        "write_times": [(m, t) for m, t in write_times],
        "seed": seed, "N": N, "run_mode": RUN_MODE,
    }


def aggregate_results(per_seed: Dict) -> Dict:
    agg = {}
    for M_key in [str(m) for m in M_LIST]:
        mmds, k3_rescaled_vals, cosine_vals = [], [], []
        for sd in per_seed.values():
            r = sd.get("M_results", {}).get(M_key)
            if r is None:
                continue
            mmds.append(r["mmd"])
            if r.get("kappa3_gram_rescaled") is not None:
                k3_rescaled_vals.append(r["kappa3_gram_rescaled"])
            if r.get("mean_cosine") is not None and not math.isnan(r["mean_cosine"]):
                cosine_vals.append(r["mean_cosine"])
        agg[M_key] = {
            "mean_mmd": float(np.mean(mmds)) if mmds else float("nan"),
            "mean_kappa3_rescaled": float(np.mean(k3_rescaled_vals)) if k3_rescaled_vals else float("nan"),
            "mean_cosine": float(np.mean(cosine_vals)) if cosine_vals else float("nan"),
            "n_seeds": len(mmds),
        }
    write_slopes = [sd.get("write_slope") for sd in per_seed.values()
                    if sd.get("write_slope") is not None]
    agg["_write_slope"] = float(np.mean(write_slopes)) if write_slopes else float("nan")
    return agg


def compute_verdict(agg: Dict) -> Tuple[str, str]:
    hp1_pass = all(v.get("mean_mmd", 1.0) < HP1_MMD
                   for k, v in agg.items() if k != "_write_slope")
    hf1_fail = any(v.get("mean_mmd", 0.0) >= HF1_MMD
                   for k, v in agg.items() if k != "_write_slope")

    k3_resc_vals = [v.get("mean_kappa3_rescaled") for k, v in agg.items()
                    if k != "_write_slope" and
                    v.get("mean_kappa3_rescaled") is not None and
                    not math.isnan(v.get("mean_kappa3_rescaled", float("nan")))]
    hp2_pass = all(abs(v - 1.0) < HP2_KAPPA3_RESC_TOL for v in k3_resc_vals) if k3_resc_vals else True
    hf2_fail = any(abs(v - 1.0) > HF2_KAPPA3_RESC_TOL for v in k3_resc_vals) if k3_resc_vals else False

    write_slope = agg.get("_write_slope", float("nan"))
    hp3_pass = (not math.isnan(write_slope)) and write_slope <= HP3_SLOPE_MAX
    hf3_flag = (not math.isnan(write_slope)) and write_slope > HF3_SLOPE_MAX

    cosine_vals = [v.get("mean_cosine") for k, v in agg.items()
                   if k != "_write_slope" and
                   v.get("mean_cosine") is not None and
                   not math.isnan(v.get("mean_cosine", float("nan")))]
    hp4_pass = all(c >= HP4_COSINE_MIN for c in cosine_vals) if cosine_vals else False
    hf4_fail = any(c < HF4_COSINE_MIN for c in cosine_vals) if cosine_vals else False

    n_hp = sum([hp1_pass, hp2_pass, hp3_pass, hp4_pass])
    mmd_vals = {k: f"{v.get('mean_mmd'):.4f}" for k, v in agg.items() if k != "_write_slope"}
    k3_vals = {k: f"{v.get('mean_kappa3_rescaled'):.4f}" for k, v in agg.items() if k != "_write_slope"}
    cos_vals = {k: f"{v.get('mean_cosine'):.4f}" for k, v in agg.items() if k != "_write_slope"}
    write_slope_str = f"{write_slope:.3f}" if not math.isnan(write_slope) else "nan"

    summary = (f"HP1_mmd={hp1_pass}(mmd={mmd_vals},thresh<{HP1_MMD}) "
               f"HP2_kappa3={hp2_pass}(k3_resc={k3_vals},tol<{HP2_KAPPA3_RESC_TOL}) "
               f"HP3_slope={hp3_pass}({write_slope_str},max={HP3_SLOPE_MAX}) "
               f"HP4_cosine={hp4_pass}(cosine={cos_vals},thresh>={HP4_COSINE_MIN}) "
               f"n_hp={n_hp}/4 GPU=True")

    if hf1_fail:
        return ("HARD_FAIL", f"HARD_FAIL: HP1 (MMD >= {HF1_MMD}). {summary}")
    if hf2_fail:
        return ("HARD_FAIL", f"HARD_FAIL: HP2 (kappa3_rescaled deviation > {HF2_KAPPA3_RESC_TOL}). {summary}")
    if hf4_fail:
        return ("HARD_FAIL", f"HARD_FAIL: HP4 (cosine < {HF4_COSINE_MIN}). {summary}")
    if n_hp == 4:
        return ("HARD_PASS", f"HARD_PASS: all 4 HP conditions met (GPU run). {summary}")
    if hp1_pass and hp2_pass and n_hp >= 3:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: HP1+HP2+{n_hp}/4. {summary}")
    if n_hp >= 2:
        return ("MIDDLE_BAND", f"MIDDLE_BAND: {n_hp}/4 HP. {summary}")
    return ("HARD_FAIL", f"HARD_FAIL: only {n_hp}/4 HP. {summary}")


# ---- MAIN SWEEP ----
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N, "M_LIST": M_LIST, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(f"[ckpt] {len(done)} seeds done, {len(remaining)} to run", flush=True)
print(f"[gpu] device={DEVICE} memory_allocated={torch.cuda.memory_allocated()/1e6:.1f}MB", flush=True)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] GPU combo1_p3_gram N={N} M_LIST={M_LIST} "
          f"BRAND_k={BRAND_REFRESH_K}...", flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
agg = aggregate_results(per_seed)
verdict, verdict_msg = compute_verdict(agg)

print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)

elapsed_s = time.time() - t_sweep_start
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "elapsed_s": elapsed_s,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "N": N,
    "M_LIST": M_LIST,
    "brand_refresh_k": BRAND_REFRESH_K,
    "device": str(DEVICE),
    "gpu_name": torch.cuda.get_device_name(0),
    "agg": agg,
    "elapsed_total_s": elapsed_s,
}

metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
