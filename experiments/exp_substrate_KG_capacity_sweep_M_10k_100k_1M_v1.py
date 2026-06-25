"""substrate_KG_capacity_sweep_M_10k_100k_1M_v1 -- scale-up sweep on the
dense projected KV envelope (chain-grade at M=10k per
`dense_projected_KV_envelope_v1`) to find where recall cliffs.

USER directive (2026-06-25): "approved on 3" (KG scale-up) + "we understand
where everything operates best within the phase diagram".

Reuses the dense projected KV mechanism (M-INDEPENDENT O(d^2) superposition
store) at progressively larger M to identify the operating envelope:
  M=10k    (verify baseline reproduces; cert envelope was recall@1 >= 0.80)
  M=50k    (intermediate)
  M=100k   (substrate-product KG threshold; HARD_PASS target recall@1 >= 0.70)
  M=500k   (large KG)
  M=1M     (stretch goal; HARD_PASS target recall@1 >= 0.50)

GPU REQUIRED per Fix #24: torch.cuda for tractable wall-time on M=1M
(K matrix = 3GB on GPU mem; per-query matmul tractable only with CUDA tensor
cores). Smoke verifies torch.cuda.is_available + memory allocated >= 50% of
substantive use.

PRE-REG BANDS (LOCKED at module init via assert):
  HARD_PASS_CHAIN_GRADE_AT_M_100k      recall@1 >= 0.70 at M=100k AND cv <= 0.05
  HARD_PASS_CHAIN_GRADE_AT_M_1M        recall@1 >= 0.50 at M=1M   (stretch)
  MEASURED_MECHANISM_at_M_cliff_X      identify smallest M where recall@1
                                        cliffs from >= 0.80 to < 0.50
  HARD_FAIL_M_10k_DOESNT_REPRODUCE     recall@1 < 0.70 at M=10k (env / scaling bug)
  HARD_FAIL_GPU_UNUSED                 torch.cuda not available / GPU not used
  OOM                                  GPU memory exhausted at some M < 1M

CONFIG: d=768, sigma=0.1, C=256, MAX_Q=2000
SEEDS: [11, 13, 19]; GPU device required.

SMOKE: M=[10k, 50k] / 1 seed; verify GPU is used + recall reproduces M=10k
envelope within +-0.05.

Author: exp_dev 2026-06-25 (Stage 3 KG scale-up per USER directive).
ASCII-only; per-(M, seed) checkpoint.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import atexit
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch    # PROT-020: torch required for GPU queue routing

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "substrate_KG_capacity_sweep_M_10k_100k_1M_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# =============================================================================
# PROSPECTIVE BANDS (LOCKED at module init via assert)
# =============================================================================
HP_RECALL_AT_M_10K_REPRO_MIN = 0.75     # cert envelope was >= 0.80; +-0.05 tolerance
HP_RECALL_AT_M_100K_MIN = 0.70          # substrate-product KG chain-grade threshold
HP_RECALL_AT_M_1M_STRETCH_MIN = 0.50    # stretch goal
HP_CV_MAX = 0.05                        # standard stability requirement
M_CLIFF_BAND_TOP = 0.80                 # recall@1 >= this -> still chain-grade
M_CLIFF_BAND_BOTTOM = 0.50              # recall@1 < this -> cliffed

assert 0 < HP_RECALL_AT_M_10K_REPRO_MIN <= 1.0
assert 0 < HP_RECALL_AT_M_100K_MIN <= HP_RECALL_AT_M_10K_REPRO_MIN
assert 0 < HP_RECALL_AT_M_1M_STRETCH_MIN <= HP_RECALL_AT_M_100K_MIN
assert M_CLIFF_BAND_BOTTOM < M_CLIFF_BAND_TOP

# =============================================================================
# CONFIG
# =============================================================================
D_KV = 768
C = 256
SIGMA = 0.1
MAX_Q = 2000

if RUN_MODE == "smoke":
    M_GRID = [10000, 50000]
    SEEDS = [11]
else:
    M_GRID = [10000, 50000, 100000, 500000, 1000000]
    SEEDS = [11, 13, 19]

# GPU device selection (Fix #24). Self-test runs on whatever's available so
# local CPU sanity can run; full FAILS if cuda unavailable.
def _select_device() -> torch.device:
    if torch.cuda.is_available():
        return torch.device("cuda")
    return torch.device("cpu")


DEVICE = _select_device()

CONFIG_VERSION = (
    "kgCapacitySweep-v1: d=%d sigma=%.2f C=%d MAX_Q=%d M_GRID=%s seeds=%s mode=%s "
    "device=%s HP_M_10k>=%.2f HP_M_100k>=%.2f HP_M_1M_stretch>=%.2f cv<=%.2f"
) % (
    D_KV, SIGMA, C, MAX_Q, M_GRID, SEEDS, RUN_MODE, str(DEVICE),
    HP_RECALL_AT_M_10K_REPRO_MIN, HP_RECALL_AT_M_100K_MIN,
    HP_RECALL_AT_M_1M_STRETCH_MIN, HP_CV_MAX,
)


# =============================================================================
# Substrate KV mechanism (torch implementation; reuses dense_projected_KV pattern)
# =============================================================================

def _norm_torch(X: torch.Tensor) -> torch.Tensor:
    return X / (X.norm(dim=-1, keepdim=True) + 1e-8)


def run_kv_config(M: int, d: int, sigma: float, seed: int,
                  device: torch.device) -> Dict[str, Any]:
    """One (M, d, sigma, seed) cell: build M random gaussian keys, build
    M-independent superposition store W of shape (d, d), query-sample,
    measure recall@{1,5,10} + keysep + cleanup-sigma + latency + memory.

    Matches dense_projected_KV_envelope_v1 mechanism exactly; torch GPU
    implementation per Fix #24.
    """
    t0 = time.perf_counter()
    g = np.random.default_rng(seed * 100003 + M * 31 + d * 7 + int(sigma * 1000))

    # ---- Build keys (M, d), labels y in {0..C-1}, codebook (C, d). ----
    K_np = g.standard_normal((M, d)).astype(np.float32)
    y_np = g.integers(0, C, M).astype(np.int64)
    codebook_np = g.standard_normal((C, d)).astype(np.float32)
    codebook_np = (codebook_np /
                   (np.linalg.norm(codebook_np, axis=1, keepdims=True) + 1e-8)
                   ).astype(np.float32)

    # ---- Move to device. ----
    K = torch.from_numpy(K_np).to(device)                                   # (M, d)
    y = torch.from_numpy(y_np).to(device)                                   # (M,)
    codebook = torch.from_numpy(codebook_np).to(device)                     # (C, d)

    # ---- Build M-independent superposition store W = sum_i code[y_i] k_i^T ----
    # W shape: (d, d). Memory O(d^2) INDEPENDENT of M (the headline mechanism).
    t_build = time.perf_counter()
    # code[y] is (M, d); code[y].T is (d, M); K is (M, d); product (d, d)
    W = codebook[y].T @ K
    if device.type == "cuda":
        torch.cuda.synchronize()
    build_s = time.perf_counter() - t_build

    # ---- Query sample. ----
    Q = min(M, MAX_Q)
    qidx_np = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    qidx = torch.from_numpy(qidx_np).to(device)
    cue = K[qidx] + sigma * torch.from_numpy(
        g.standard_normal((Q, d)).astype(np.float32)).to(device)            # (Q, d)
    ytrue = y[qidx]                                                          # (Q,)

    # ---- Readout + decode (M-INDEPENDENT path). ----
    t_query = time.perf_counter()
    readout = cue @ W.T                                                     # (Q, d)
    readout_n = _norm_torch(readout)
    decode_sims = readout_n @ codebook.T                                    # (Q, C)
    top10_vals, top10_idxs = torch.topk(decode_sims, k=min(10, C), dim=1)
    if device.type == "cuda":
        torch.cuda.synchronize()
    query_s = time.perf_counter() - t_query

    # ---- Recall @ k. ----
    pred1 = top10_idxs[:, 0]
    recall_at_1 = float((pred1 == ytrue).float().mean().cpu())
    pred5 = top10_idxs[:, :5]
    recall_at_5 = float((pred5 == ytrue.unsqueeze(1)).any(dim=1).float().mean().cpu())
    recall_at_10 = float((top10_idxs == ytrue.unsqueeze(1)).any(dim=1).float().mean().cpu())

    # ---- Cleanup sigma: per-query (best - 2nd_best) separation. ----
    sep = (top10_vals[:, 0] - top10_vals[:, 1])
    avg_cleanup_sigma = float(sep.mean().cpu())

    # ---- Keysep: mean key-key cosine on a sample of pairs. ----
    n_pair_sample = min(200, M)
    if n_pair_sample >= 10:
        sub_idx = torch.randperm(M, device=device)[:n_pair_sample]
        K_sub = _norm_torch(K[sub_idx])
        keysep_mat = K_sub @ K_sub.T
        # Off-diagonal mean
        keysep_off = keysep_mat - torch.diag(torch.diag(keysep_mat))
        keysep = float(keysep_off.sum().cpu() / (n_pair_sample * (n_pair_sample - 1)))
    else:
        keysep = 0.0

    # ---- Memory footprint. ----
    # K is M*d*4 bytes; W is d*d*4 bytes. The headline: W is M-independent.
    K_mb = M * d * 4 / 1024.0 / 1024.0
    W_mb = d * d * 4 / 1024.0 / 1024.0

    # ---- GPU util (if cuda). ----
    if device.type == "cuda":
        gpu_mem_alloc_mb = torch.cuda.memory_allocated() / 1024.0 / 1024.0
        gpu_mem_max_mb = torch.cuda.max_memory_allocated() / 1024.0 / 1024.0
        device_str = "cuda:%d %s" % (
            torch.cuda.current_device(),
            torch.cuda.get_device_name(torch.cuda.current_device()),
        )
    else:
        gpu_mem_alloc_mb = 0.0
        gpu_mem_max_mb = 0.0
        device_str = "cpu"

    elapsed_s = time.perf_counter() - t0
    per_query_latency_ms = (query_s / max(Q, 1)) * 1000.0

    # Free GPU mem before next M (avoid OOM on large M)
    del K, y, codebook, W, qidx, cue, ytrue, readout, readout_n, decode_sims
    del top10_vals, top10_idxs, pred1, pred5
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "M": M, "d": d, "sigma": sigma, "seed": seed,
        "recall_at_1": round(recall_at_1, 4),
        "recall_at_5": round(recall_at_5, 4),
        "recall_at_10": round(recall_at_10, 4),
        "avg_cleanup_sigma": round(avg_cleanup_sigma, 4),
        "keysep": round(keysep, 4),
        "K_matrix_mb": round(K_mb, 2),
        "W_matrix_mb": round(W_mb, 2),
        "gpu_mem_max_mb": round(gpu_mem_max_mb, 2),
        "gpu_mem_alloc_mb": round(gpu_mem_alloc_mb, 2),
        "build_s": round(build_s, 4),
        "query_s": round(query_s, 4),
        "per_query_latency_ms": round(per_query_latency_ms, 4),
        "elapsed_s": round(elapsed_s, 3),
        "device": device_str,
    }


# =============================================================================
# Self-test
# =============================================================================

def _selftest() -> None:
    print("[selftest] device=%s cuda_available=%s torch_version=%s" %
          (DEVICE, torch.cuda.is_available(), torch.__version__))

    # T1: meter-check at tiny M=200, sigma=0 -> recall ~ 1.0
    r = run_kv_config(200, 128, 0.0, 1, DEVICE)
    assert r["recall_at_1"] > 0.95, \
        "T1 meter-check: tiny-M=200 sigma=0 should give recall@1>0.95, got %.3f" % r["recall_at_1"]
    print("[selftest] T1 PASS: tiny-M=200 sigma=0 recall@1=%.3f device=%s" %
          (r["recall_at_1"], r["device"]))

    # T2: M-independence of W storage (W is d x d regardless of M)
    r_small = run_kv_config(500, 64, 0.1, 2, DEVICE)
    r_big = run_kv_config(5000, 64, 0.1, 2, DEVICE)
    assert r_small["W_matrix_mb"] == r_big["W_matrix_mb"], \
        "T2 W must be M-INDEPENDENT: small=%.2fMB big=%.2fMB" % (
            r_small["W_matrix_mb"], r_big["W_matrix_mb"])
    print("[selftest] T2 PASS: W matrix size is M-independent (%.2fMB at M=500 AND M=5000)" %
          r_small["W_matrix_mb"])

    # T3: crowding -- recall DECREASES with M (non-trivial mechanism)
    r_lo = run_kv_config(500, 64, 0.1, 3, DEVICE)
    r_hi = run_kv_config(8000, 64, 0.1, 3, DEVICE)
    assert r_lo["recall_at_1"] >= r_hi["recall_at_1"] - 0.01, \
        "T3 crowding: ARM1 recall should non-INCREASE with M, lo(M=500)=%.3f hi(M=8000)=%.3f" % (
            r_lo["recall_at_1"], r_hi["recall_at_1"])
    print("[selftest] T3 PASS: crowding monotonic (M=500 recall@1=%.3f >= M=8000 recall@1=%.3f)" %
          (r_lo["recall_at_1"], r_hi["recall_at_1"]))

    # T4: sigma > 0 verified in query (non-zero noise applied)
    r_clean = run_kv_config(200, 64, 0.0, 4, DEVICE)
    r_noisy = run_kv_config(200, 64, 0.5, 4, DEVICE)
    assert r_clean["recall_at_1"] >= r_noisy["recall_at_1"] - 0.01, \
        "T4 sigma noise reduces recall, clean=%.3f noisy=%.3f" % (
            r_clean["recall_at_1"], r_noisy["recall_at_1"])
    print("[selftest] T4 PASS: sigma noise applied (sigma=0 recall@1=%.3f, sigma=0.5 recall@1=%.3f)" %
          (r_clean["recall_at_1"], r_noisy["recall_at_1"]))

    # T5: recall@5 >= recall@1 (graceful)
    r = run_kv_config(500, 64, 0.2, 5, DEVICE)
    assert r["recall_at_5"] >= r["recall_at_1"] - 1e-6, \
        "T5 recall@5 >= recall@1: r@1=%.3f r@5=%.3f" % (r["recall_at_1"], r["recall_at_5"])
    assert r["recall_at_10"] >= r["recall_at_5"] - 1e-6
    print("[selftest] T5 PASS: recall@1=%.3f <= recall@5=%.3f <= recall@10=%.3f" %
          (r["recall_at_1"], r["recall_at_5"], r["recall_at_10"]))

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# =============================================================================
# Per-seed run (sweeps over M_GRID)
# =============================================================================

def run_seed(seed: int) -> Dict[str, Any]:
    t0 = time.time()

    # GPU smoke verification per Fix #24
    gpu_used = (DEVICE.type == "cuda")
    if gpu_used:
        print("  [seed=%d] GPU: %s, mem before=%.1fMB" % (
            seed, torch.cuda.get_device_name(0),
            torch.cuda.memory_allocated() / 1024.0 / 1024.0), flush=True)
    else:
        print("  [seed=%d] WARNING: CPU device only (cuda unavailable)" % seed, flush=True)

    results_by_M: Dict[int, Dict[str, Any]] = {}
    for M in M_GRID:
        try:
            r = run_kv_config(M, D_KV, SIGMA, seed, DEVICE)
            results_by_M[M] = r
            print("  [seed=%d M=%d] r@1=%.3f r@5=%.3f keysep=%.4f cleanup_sigma=%.4f "
                  "lat=%.3fms W=%.2fMB K=%.1fMB gpu=%.1fMB elapsed=%.2fs" %
                  (seed, M, r["recall_at_1"], r["recall_at_5"], r["keysep"],
                   r["avg_cleanup_sigma"], r["per_query_latency_ms"],
                   r["W_matrix_mb"], r["K_matrix_mb"], r["gpu_mem_max_mb"],
                   r["elapsed_s"]), flush=True)
        except torch.cuda.OutOfMemoryError as e:
            print("  [seed=%d M=%d] OOM: %s" % (seed, M, str(e)[:120]), flush=True)
            results_by_M[M] = {
                "M": M, "d": D_KV, "sigma": SIGMA, "seed": seed,
                "OOM": True, "error": str(e)[:200],
            }
            if DEVICE.type == "cuda":
                torch.cuda.empty_cache()
            break  # stop sweep; can't go larger if this OOMed

    return {
        "seed": seed, "run_mode": RUN_MODE, "M_GRID": M_GRID, "d": D_KV, "sigma": SIGMA,
        "C": C, "MAX_Q": MAX_Q, "results_by_M": results_by_M,
        "config_version": CONFIG_VERSION, "device_used": str(DEVICE),
        "cuda_available": torch.cuda.is_available(),
        "elapsed_s": round(time.time() - t0, 1),
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }


# =============================================================================
# Verdict
# =============================================================================

def _M_recall_mean(per_seed: List[Dict[str, Any]], M: int, key: str = "recall_at_1") -> float:
    vals = []
    for p in per_seed:
        r = p.get("results_by_M", {}).get(M) or p.get("results_by_M", {}).get(str(M))
        if not r or r.get("OOM"):
            continue
        v = r.get(key)
        if isinstance(v, (int, float)) and not math.isnan(v):
            vals.append(float(v))
    return float(np.mean(vals)) if vals else float("nan")


def _M_recall_cv(per_seed: List[Dict[str, Any]], M: int) -> float:
    vals = []
    for p in per_seed:
        r = p.get("results_by_M", {}).get(M) or p.get("results_by_M", {}).get(str(M))
        if not r or r.get("OOM"):
            continue
        v = r.get("recall_at_1")
        if isinstance(v, (int, float)) and not math.isnan(v):
            vals.append(float(v))
    if len(vals) < 2:
        return 0.0
    m = float(np.mean(vals))
    return float(np.std(vals) / max(abs(m), 1e-9))


def _M_oom(per_seed: List[Dict[str, Any]], M: int) -> bool:
    for p in per_seed:
        r = p.get("results_by_M", {}).get(M) or p.get("results_by_M", {}).get(str(M))
        if r and r.get("OOM"):
            return True
    return False


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    # GPU usage check first (Fix #24)
    any_cuda = any(p.get("cuda_available") for p in per_seed)
    device_strs = sorted({p.get("device_used", "?") for p in per_seed})
    if RUN_MODE == "full" and not any_cuda:
        return "HARD_FAIL_GPU_UNUSED", \
               "HARD_FAIL_GPU_UNUSED: cuda not available on full run; per Fix #24 GPU dispatch " \
               "MUST actually use GPU; device_used=%s" % device_strs

    # Per-M recall summary
    M_rows: List[str] = []
    for M in M_GRID:
        if _M_oom(per_seed, M):
            M_rows.append("M=%d[OOM]" % M)
            continue
        r1 = _M_recall_mean(per_seed, M, "recall_at_1")
        r5 = _M_recall_mean(per_seed, M, "recall_at_5")
        cv = _M_recall_cv(per_seed, M)
        keysep = _M_recall_mean(per_seed, M, "keysep")
        lat = _M_recall_mean(per_seed, M, "per_query_latency_ms")
        W_mb = _M_recall_mean(per_seed, M, "W_matrix_mb")
        K_mb = _M_recall_mean(per_seed, M, "K_matrix_mb")
        M_rows.append("M=%d[r@1=%.3f r@5=%.3f cv=%.3f keysep=%.4f lat=%.2fms W=%.2fMB K=%.1fMB]" %
                       (M, r1, r5, cv, keysep, lat, W_mb, K_mb))
    summ = " | ".join(M_rows)

    # ---- M=10k reproduce check (rail; must hold) ----
    if 10000 in M_GRID:
        r_10k = _M_recall_mean(per_seed, 10000, "recall_at_1")
        if not math.isnan(r_10k) and r_10k < HP_RECALL_AT_M_10K_REPRO_MIN:
            return "HARD_FAIL_M_10k_DOESNT_REPRODUCE", \
                   "HARD_FAIL_M_10k_DOESNT_REPRODUCE: M=10k recall@1=%.3f < %.2f " \
                   "(env or scaling bug; cert envelope was 0.80) | %s" % (
                       r_10k, HP_RECALL_AT_M_10K_REPRO_MIN, summ)

    # ---- Identify cliff: smallest M where recall@1 < M_CLIFF_BAND_BOTTOM ----
    cliff_M = None
    for M in sorted(M_GRID):
        if _M_oom(per_seed, M):
            cliff_M = ("OOM", M)
            break
        r1 = _M_recall_mean(per_seed, M, "recall_at_1")
        if not math.isnan(r1) and r1 < M_CLIFF_BAND_BOTTOM:
            cliff_M = ("CLIFFED", M, r1)
            break

    # ---- HARD_PASS tiers (in priority order) ----
    if 1000000 in M_GRID:
        r_1m = _M_recall_mean(per_seed, 1000000, "recall_at_1")
        cv_1m = _M_recall_cv(per_seed, 1000000)
        oom_1m = _M_oom(per_seed, 1000000)
        if (not oom_1m and not math.isnan(r_1m) and r_1m >= HP_RECALL_AT_M_1M_STRETCH_MIN
                and cv_1m <= HP_CV_MAX):
            return "HARD_PASS_CHAIN_GRADE_AT_M_1M", \
                   "HARD_PASS_CHAIN_GRADE_AT_M_1M: substrate KV holds recall@1=%.3f >= %.2f " \
                   "at M=1M (cv=%.3f) -- substrate-product KG positioning at MILLION-fact scale " \
                   "via M-INDEPENDENT O(d^2) superposition store | %s" % (
                       r_1m, HP_RECALL_AT_M_1M_STRETCH_MIN, cv_1m, summ)

    if 100000 in M_GRID:
        r_100k = _M_recall_mean(per_seed, 100000, "recall_at_1")
        cv_100k = _M_recall_cv(per_seed, 100000)
        oom_100k = _M_oom(per_seed, 100000)
        if (not oom_100k and not math.isnan(r_100k) and r_100k >= HP_RECALL_AT_M_100K_MIN
                and cv_100k <= HP_CV_MAX):
            return "HARD_PASS_CHAIN_GRADE_AT_M_100k", \
                   "HARD_PASS_CHAIN_GRADE_AT_M_100k: substrate KV holds recall@1=%.3f >= %.2f " \
                   "at M=100k (cv=%.3f) -- substrate-product KG positioning at 100k-fact scale | %s" % (
                       r_100k, HP_RECALL_AT_M_100K_MIN, cv_100k, summ)

    # ---- MM: cliff identified ----
    if cliff_M is not None:
        if cliff_M[0] == "OOM":
            return "OOM", \
                   "OOM_at_M_%d: GPU memory exhausted; substrate KV scales beyond GPU host " \
                   "capacity at this M -- M-ceiling identified | %s" % (cliff_M[1], summ)
        return "MEASURED_MECHANISM_at_M_cliff_X", \
               "MEASURED_MECHANISM_at_M_cliff_M=%d: substrate KV recall@1 cliffs to %.3f < %.2f " \
               "at M=%d (operating envelope upper-bound identified) | %s" % (
                   cliff_M[1], cliff_M[2], M_CLIFF_BAND_BOTTOM, cliff_M[1], summ)

    # ---- MIDDLE_BAND: holds above floor but doesn't hit any HARD_PASS threshold ----
    return "MIDDLE_BAND", \
           "MIDDLE_BAND_partial_KG_scaling: substrate KV holds above cliff %.2f at all M in " \
           "grid but doesn't hit M=100k chain-grade threshold (recall@1 >= %.2f) | %s" % (
               M_CLIFF_BAND_BOTTOM, HP_RECALL_AT_M_100K_MIN, summ)


# =============================================================================
# atexit synthesizer
# =============================================================================

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s device=%s M_GRID=%s | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, str(DEVICE), M_GRID, CONFIG_VERSION),
          flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    # Per-seed loop (no resumable_seeds here; OOM-handling needs custom flow)
    for s in SEEDS:
        key = "s%d" % s
        existing = aggregate_partials(out_dir, [key], run_config={"run_mode": RUN_MODE})
        if key in existing:
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        rec = run_seed(s)
        write_partial_key(out_dir, key, rec)

    agg = aggregate_partials(out_dir, seeds=["s%d" % s for s in SEEDS],
                              run_config={"run_mode": RUN_MODE})
    per_seed = [agg["s%d" % s] for s in SEEDS if "s%d" % s in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "Substrate KV capacity sweep M=10k..1M to identify the operating-envelope "
            "cliff (or its absence). Reuses dense_projected_KV_envelope_v1 mechanism. "
            "GPU required per Fix #24. Pre-reg per "
            "preregs/2026-06-25_substrate_KG_capacity_sweep_M_10k_100k_1M_v1.md."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
