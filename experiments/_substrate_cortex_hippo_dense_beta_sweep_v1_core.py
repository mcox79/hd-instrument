"""Shared core for cortex_hippo dense-Hopfield READ-REPLACE BETA SWEEP v1.

Purpose: characterize the beta-recall curve at fixed M for cortex-side dense
Hopfield READ-REPLACE mechanism (Cell D v2 replacement-mode). Complements the
v3 M-sweep which uses ADAPTIVE beta ~ log2(M)/margin.

Design:
- Sweep beta in {5.0, 8.0, 13.0, 20.0, 32.0} at M in {4096, 8192, 16384}.
- Encoded tape SHARED across beta arms within one (seed, M) pair (encode once,
  read 5 times) to isolate the READ-side beta effect from encoder noise.

MECHANISM (identical READ; SWEPT beta):
  ARM_STANDARD               = direct cortex Hebbian only (per M; 1 outcome).
  ARM_HA_ONLY                = sparse-DG hippo one-shot; cortex empty (per M).
  ARM_HA_DENSE_REPLACE_betaX = same tape; attention read at beta=X (fixed).
                               Runs 5 times per M (X in {5, 8, 13, 20, 32}).

HP (per-seed, all 3 M):
  For each M in {4096, 8192, 16384}:
    max_beta recall(REPLACE) >= 0.80        # SOME beta hits high recall
    recall(nearest-adaptive-beta) >= 0.95 * max_beta_recall   # formula near-optimal

HF:
  max_beta recall(REPLACE) < 0.60 at ANY M (mechanism cannot reach floor).
  OR nearest-adaptive recall < 0.60 at ANY M.
  OR HA_ONLY > 0.20 at ANY M.
  OR ANY arm-pair bit-identical at any (M, beta) (META_RULE_AF; ceiling-tie exempt).
  OR CARDINALITY_BREACH.

MB:
  0.60 <= max_beta recall < 0.80 at any M, OR
  adaptive / star ratio in [0.80, 0.95) at any M.

CARDINALITY (META_RULE_H):
  FULL: 3 M * (2 baseline arms + 5 beta arms) = 21 arm-outcomes per seed cell.
  SMOKE: 1 M * 7 arm outcomes = 7 arm-outcomes.

ASCII-only; META_RULE_AH atomic-write; META_RULE_AF arms-must-differ;
META_RULE_AG baseline-in-band; META_RULE_H cardinality; SystemExit before
Exception (no BaseException).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


# ---------------------------------------------------------------------------
# Fixed config
# ---------------------------------------------------------------------------
N_HIPPO_FULL = 4096
N_CORTEX_FULL = 4096
HIPPO_SPARSITY = 0.10
ETA_HIPPO_FULL = 1.0

# Sweep axes
BETA_SWEEP = [5.0, 8.0, 13.0, 20.0, 32.0]   # PRIMARY axis
M_SWEEP_FULL = [4096, 8192, 16384]          # SECONDARY axis

# Smoke: 1 M (fastest) + full BETA_SWEEP + FULL_N preview at largest M
# Preview runs BOTH beta=20 (adaptive-target) AND beta=5 (below BETA_MIN clamp)
# so we can VERIFY the beta axis actually differentiates at full scale (per
# Discipline Pattern 2: smoke must fire the discriminator).
M_SWEEP_SMOKE_MAIN = 4096
M_SWEEP_SMOKE_PREVIEW = 16384
BETA_PREVIEW = 20.0     # adaptive-target for M=16384, margin=0.7
BETA_PREVIEW_LOW = 5.0  # below BETA_MIN clamp; probes low-beta collapse

# For "nearest-adaptive" mapping (from formula log2(M)/measured_margin).
# CORRECTED 2026-07-01 after reading v2 landed metrics.json (fc47b1bb):
# measured cos_margin at v2 M=8192 = 0.94 (NOT 0.7 as pre-reg first assumed).
# At margin=0.94:
#   M=4096  -> raw=12/0.94=12.77 -> nearest swept in {5,8,13,20,32} = 13.0
#   M=8192  -> raw=13/0.94=13.83 -> nearest swept = 13.0
#   M=16384 -> raw=14/0.94=14.89 -> nearest swept = 13.0
# HYPOTHESIZED@formula (verified against MEASURED@data/exp_cortex_hippo_dense_layer_M8192_v2_seed_7/metrics.json)
ADAPTIVE_NEAREST_BETA = {4096: 13.0, 8192: 13.0, 16384: 13.0}


def _adaptive_beta_formula(m_items: int, cosine_margin: float = 0.7) -> float:
    return math.log2(max(2, m_items)) / max(cosine_margin, 0.05)


def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    row = {
        "ts_iso": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "unit_idx": int(unit_idx),
        "total_units": int(total_units) if total_units is not None else None,
        "elapsed_s": round(float(elapsed_s), 2),
    }
    if extra:
        row["extra"] = extra
    try:
        out = Path(output_dir)
        out.mkdir(parents=True, exist_ok=True)
        with (out / "_heartbeat.jsonl").open("a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except OSError:
        pass


def write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
    import platform
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": anchor_name,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "_start_marker.json.tmp"
    final = out / "_start_marker.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(str(tmp), str(final))


def write_crash_metrics(output_dir, anchor_name, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": anchor_name,
    }
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    tmp = out / "metrics.json.tmp"
    final = out / "metrics.json"
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(str(tmp), str(final))


# ---------------------------------------------------------------------------
# Torch import (optional)
# ---------------------------------------------------------------------------
_TORCH_AVAILABLE = False
_CUDA_AVAILABLE = False
torch = None  # type: ignore
try:
    import torch as _torch
    torch = _torch
    _TORCH_AVAILABLE = True
    _CUDA_AVAILABLE = bool(torch.cuda.is_available())
except Exception as _exc:
    print(f"[torch] import failed: {type(_exc).__name__}: {_exc}", flush=True)


# ---------------------------------------------------------------------------
# Substrate primitives (numpy)
# ---------------------------------------------------------------------------
def _pattern_separate_sparse_batched(X, P, k):
    h_raw = X @ P.T
    abs_h = np.abs(h_raw)
    idx = np.argpartition(-abs_h, k - 1, axis=1)[:, :k]
    signs = np.sign(np.take_along_axis(h_raw, idx, axis=1))
    signs[signs == 0] = 1.0
    out = np.zeros_like(h_raw)
    np.put_along_axis(out, idx, signs, axis=1)
    return out


def _encode_all_numpy(keys_raw, vals_raw, P_in, P_hc, n_h, n_c, m_items, k_active):
    keys_h = _pattern_separate_sparse_batched(keys_raw, P_in, k_active)
    vals_h = _pattern_separate_sparse_batched(vals_raw, P_in, k_active)
    keys_c_raw = keys_h @ P_hc.T
    keys_c = keys_c_raw / np.linalg.norm(keys_c_raw, axis=1, keepdims=True).clip(min=1e-12)
    vals_c_raw = vals_h @ P_hc.T
    vals_c = vals_c_raw / np.linalg.norm(vals_c_raw, axis=1, keepdims=True).clip(min=1e-12)
    return keys_h, vals_h, keys_c, vals_c


def _cosine_margin_estimate(keys_c: np.ndarray, sample_n: int = 256) -> float:
    m = keys_c.shape[0]
    n_s = min(sample_n, m)
    idx = np.arange(m)
    if m > n_s:
        rng = np.random.RandomState(0)
        idx = rng.choice(m, size=n_s, replace=False)
    sub = keys_c[idx]
    sim = sub @ sub.T
    mask = ~np.eye(n_s, dtype=bool)
    off_mean_abs = float(np.abs(sim[mask]).mean())
    margin = 1.0 - off_mean_abs
    if not math.isfinite(margin) or margin <= 0.0:
        return 0.1
    return margin


# ---------------------------------------------------------------------------
# Numpy per-arm runners
# ---------------------------------------------------------------------------
def _replace_read_numpy(keys_c: np.ndarray, vals_c: np.ndarray,
                        beta: float, attn_chunk: int) -> float:
    """One dense-attention READ pass at fixed beta. Returns recall."""
    K_tape = keys_c
    V_tape = vals_c
    m_items = K_tape.shape[0]
    queries = keys_c
    n_hits = 0
    for start in range(0, m_items, attn_chunk):
        end = min(m_items, start + attn_chunk)
        q_chunk = queries[start:end]
        sims = q_chunk @ K_tape.T
        sims_scaled = float(beta) * sims
        sims_scaled -= sims_scaled.max(axis=1, keepdims=True)
        w = np.exp(sims_scaled)
        w /= w.sum(axis=1, keepdims=True).clip(min=1e-30)
        p = w @ V_tape
        p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)
        sims_match = p_n @ V_tape.T
        argmax = sims_match.argmax(axis=1)
        targets = np.arange(start, end)
        n_hits += int((argmax == targets).sum())
    return n_hits / float(m_items)


def _standard_recall_numpy(keys_c, vals_c, n_c, eta_hippo) -> float:
    m_items = keys_c.shape[0]
    W_cortex = np.zeros((n_c, n_c), dtype=np.float64)
    W_cortex += eta_hippo * (vals_c.T @ keys_c)
    preds_raw = keys_c @ W_cortex.T
    preds = np.sign(preds_raw)
    preds[preds == 0] = 1.0
    preds_n = preds / np.linalg.norm(preds, axis=1, keepdims=True).clip(min=1e-12)
    sims = preds_n @ vals_c.T
    argmax = sims.argmax(axis=1)
    return int((argmax == np.arange(m_items)).sum()) / float(m_items)


def _ha_only_recall_numpy(seed, m_items, n_c, vals_c) -> float:
    rng = np.random.RandomState(seed + 91 + m_items)
    preds = rng.randn(m_items, n_c) * 1e-6
    preds_n = preds / np.linalg.norm(preds, axis=1, keepdims=True).clip(min=1e-12)
    sims = preds_n @ vals_c.T
    argmax = sims.argmax(axis=1)
    return int((argmax == np.arange(m_items)).sum()) / float(m_items)


# ---------------------------------------------------------------------------
# Torch/CUDA per-arm runners
# ---------------------------------------------------------------------------
def _pattern_separate_sparse_torch(x, P, k):
    h_raw = x @ P.T
    abs_h = h_raw.abs()
    _, topk_idx = torch.topk(abs_h, k, dim=1)
    signs_at_topk = torch.sign(torch.gather(h_raw, 1, topk_idx))
    signs_at_topk = torch.where(signs_at_topk == 0,
                                torch.ones_like(signs_at_topk),
                                signs_at_topk)
    h_sparse = torch.zeros_like(h_raw)
    h_sparse.scatter_(1, topk_idx, signs_at_topk)
    return h_sparse


def _l2norm_rows_torch(x):
    return x / x.norm(dim=1, keepdim=True).clamp_min(1e-12)


def _replace_read_torch(keys_c, vals_c, beta: float, attn_chunk: int, dev) -> float:
    K_tape = keys_c
    V_tape = vals_c
    m_items = int(K_tape.shape[0])
    queries = keys_c
    n_hits = 0
    for start in range(0, m_items, attn_chunk):
        end = min(m_items, start + attn_chunk)
        q_chunk = queries[start:end]
        sims = q_chunk @ K_tape.T
        sims_scaled = float(beta) * sims
        sims_scaled = sims_scaled - sims_scaled.max(dim=1, keepdim=True).values
        w = torch.exp(sims_scaled)
        w = w / w.sum(dim=1, keepdim=True).clamp_min(1e-30)
        p = w @ V_tape
        p_n = _l2norm_rows_torch(p)
        sims_match = p_n @ V_tape.T
        argmax = sims_match.argmax(dim=1)
        targets = torch.arange(start, end, device=dev)
        n_hits += int((argmax == targets).sum().item())
    return n_hits / float(m_items)


# ---------------------------------------------------------------------------
# Per-(seed, M) driver: encode ONCE, run baselines, sweep beta
# ---------------------------------------------------------------------------
def run_one_M(seed: int, m_items: int, n_h: int, n_c: int,
              hippo_sparsity: float, eta_hippo: float,
              beta_list: List[float], attn_chunk: int,
              use_cuda: bool, out_dir: Path) -> List[Dict]:
    """Encode once; run STANDARD + HA_ONLY + REPLACE at each beta. Returns arm dicts."""
    rng = np.random.RandomState(seed + m_items)
    N_raw = 64
    P_in = rng.randn(n_h, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng.randn(n_c, n_h).astype(np.float64) / np.sqrt(n_h)
    keys_raw = rng.choice([-1.0, 1.0], size=(m_items, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m_items, N_raw)).astype(np.float64)
    k_active = max(1, int(round(hippo_sparsity * n_h)))

    print(f"  [seed={seed} M={m_items}] N_h={n_h} N_c={n_c} k={k_active} "
          f"eta_h={eta_hippo} beta_list={beta_list} chunk={attn_chunk} cuda={use_cuda}",
          flush=True)

    arms: List[Dict] = []
    t_M_start = time.time()

    if use_cuda:
        dev = torch.device("cuda")
        torch.cuda.reset_peak_memory_stats(dev)
        mem_start = torch.cuda.memory_allocated(dev)

        keys_raw_t = torch.from_numpy(keys_raw).to(dev, dtype=torch.float32)
        vals_raw_t = torch.from_numpy(vals_raw).to(dev, dtype=torch.float32)
        P_in_t = torch.from_numpy(P_in).to(dev, dtype=torch.float32)
        P_hc_t = torch.from_numpy(P_hc).to(dev, dtype=torch.float32)
        keys_h_t = _pattern_separate_sparse_torch(keys_raw_t, P_in_t, k_active)
        vals_h_t = _pattern_separate_sparse_torch(vals_raw_t, P_in_t, k_active)
        keys_c_t = _l2norm_rows_torch(keys_h_t @ P_hc_t.T)
        vals_c_t = _l2norm_rows_torch(vals_h_t @ P_hc_t.T)
        cos_margin_val = _cosine_margin_estimate(keys_c_t.cpu().numpy())
        adaptive_beta_val = _adaptive_beta_formula(m_items, cos_margin_val)
        emit_heartbeat(out_dir, unit_idx=0, elapsed_s=time.time() - t_M_start,
                       extra={"phase": "encoded_cuda", "M": m_items,
                              "gpu_mem_mb": torch.cuda.memory_allocated(dev) / 1e6,
                              "cos_margin": cos_margin_val,
                              "adaptive_beta_HYPOTHESIZED": adaptive_beta_val})

        # STANDARD (once per M)
        t0 = time.time()
        try:
            W_cortex = torch.zeros((n_c, n_c), dtype=torch.float32, device=dev)
            W_cortex.addmm_(vals_c_t.T, keys_c_t, alpha=eta_hippo)
            preds_raw = keys_c_t @ W_cortex.T
            preds = torch.sign(preds_raw)
            preds = torch.where(preds == 0, torch.ones_like(preds), preds)
            preds_n = _l2norm_rows_torch(preds)
            sims = preds_n @ vals_c_t.T
            argmax = sims.argmax(dim=1)
            n_hits = int((argmax == torch.arange(m_items, device=dev)).sum().item())
            recall_std = n_hits / float(m_items)
            del W_cortex
            arm_status = "OK"
        except Exception as exc:
            recall_std = float("nan")
            arm_status = f"ERROR: {type(exc).__name__}: {exc}"
        wall = time.time() - t0
        arms.append({"arm_name": "ARM_STANDARD", "M": int(m_items),
                     "beta_used": float("nan"), "recall_cortex": float(recall_std),
                     "n_items": int(m_items), "N_h": int(n_h), "N_c": int(n_c),
                     "k_hippo_active": int(k_active), "eta_hippo": float(eta_hippo),
                     "cosine_margin_used": float(cos_margin_val),
                     "wall_s": float(wall), "backend": "torch.cuda",
                     "gpu_mem_peak_mb": float(torch.cuda.max_memory_allocated(dev) / 1e6),
                     "arm_status": arm_status})
        print(f"  [seed={seed} M={m_items} ARM_STANDARD] recall={recall_std:.3f} "
              f"wall={wall:.1f}s status={arm_status}", flush=True)

        # HA_ONLY (once per M)
        t0 = time.time()
        try:
            gen = torch.Generator(device=dev)
            gen.manual_seed(seed + 91 + m_items)
            preds = torch.randn(m_items, n_c, generator=gen, device=dev) * 1e-6
            preds_n = _l2norm_rows_torch(preds)
            sims = preds_n @ vals_c_t.T
            argmax = sims.argmax(dim=1)
            n_hits = int((argmax == torch.arange(m_items, device=dev)).sum().item())
            recall_ha = n_hits / float(m_items)
            arm_status = "OK"
        except Exception as exc:
            recall_ha = float("nan")
            arm_status = f"ERROR: {type(exc).__name__}: {exc}"
        wall = time.time() - t0
        arms.append({"arm_name": "ARM_HA_ONLY", "M": int(m_items),
                     "beta_used": float("nan"), "recall_cortex": float(recall_ha),
                     "n_items": int(m_items), "N_h": int(n_h), "N_c": int(n_c),
                     "k_hippo_active": int(k_active), "eta_hippo": float(eta_hippo),
                     "cosine_margin_used": float(cos_margin_val),
                     "wall_s": float(wall), "backend": "torch.cuda",
                     "gpu_mem_peak_mb": 0.0, "arm_status": arm_status})
        print(f"  [seed={seed} M={m_items} ARM_HA_ONLY] recall={recall_ha:.3f} "
              f"wall={wall:.1f}s status={arm_status}", flush=True)

        # REPLACE_beta_X (5 times per M)
        for beta in beta_list:
            t0 = time.time()
            try:
                recall = _replace_read_torch(keys_c_t, vals_c_t, beta,
                                             attn_chunk, dev)
                arm_status = "OK"
            except Exception as exc:
                recall = float("nan")
                arm_status = f"ERROR: {type(exc).__name__}: {exc}"
            wall = time.time() - t0
            gpu_peak = float(torch.cuda.max_memory_allocated(dev) / 1e6)
            arm_name = f"ARM_HA_DENSE_REPLACE_beta{int(beta)}"
            arms.append({"arm_name": arm_name, "M": int(m_items),
                         "beta_used": float(beta),
                         "recall_cortex": float(recall),
                         "n_items": int(m_items), "N_h": int(n_h), "N_c": int(n_c),
                         "k_hippo_active": int(k_active), "eta_hippo": float(eta_hippo),
                         "cosine_margin_used": float(cos_margin_val),
                         "wall_s": float(wall), "backend": "torch.cuda",
                         "gpu_mem_peak_mb": gpu_peak, "arm_status": arm_status})
            emit_heartbeat(out_dir, unit_idx=int(beta), total_units=len(beta_list),
                           elapsed_s=time.time() - t_M_start,
                           extra={"phase": "beta_read", "arm": arm_name,
                                  "M": m_items, "beta": beta, "recall": recall})
            print(f"  [seed={seed} M={m_items} {arm_name}] "
                  f"recall={recall:.3f} wall={wall:.1f}s status={arm_status}",
                  flush=True)

        del keys_raw_t, vals_raw_t, P_in_t, P_hc_t
        del keys_h_t, vals_h_t, keys_c_t, vals_c_t
        torch.cuda.empty_cache()

    else:
        # numpy path
        keys_h, vals_h, keys_c, vals_c = _encode_all_numpy(
            keys_raw, vals_raw, P_in, P_hc, n_h, n_c, m_items, k_active,
        )
        cos_margin_val = _cosine_margin_estimate(keys_c)
        adaptive_beta_val = _adaptive_beta_formula(m_items, cos_margin_val)
        emit_heartbeat(out_dir, unit_idx=0, elapsed_s=time.time() - t_M_start,
                       extra={"phase": "encoded_numpy", "M": m_items,
                              "cos_margin": cos_margin_val,
                              "adaptive_beta_HYPOTHESIZED": adaptive_beta_val})

        # STANDARD
        t0 = time.time()
        try:
            recall_std = _standard_recall_numpy(keys_c, vals_c, n_c, eta_hippo)
            arm_status = "OK"
        except Exception as exc:
            recall_std = float("nan")
            arm_status = f"ERROR: {type(exc).__name__}: {exc}"
        wall = time.time() - t0
        arms.append({"arm_name": "ARM_STANDARD", "M": int(m_items),
                     "beta_used": float("nan"), "recall_cortex": float(recall_std),
                     "n_items": int(m_items), "N_h": int(n_h), "N_c": int(n_c),
                     "k_hippo_active": int(k_active), "eta_hippo": float(eta_hippo),
                     "cosine_margin_used": float(cos_margin_val),
                     "wall_s": float(wall), "backend": "numpy",
                     "gpu_mem_peak_mb": 0.0, "arm_status": arm_status})
        print(f"  [seed={seed} M={m_items} ARM_STANDARD] recall={recall_std:.3f} "
              f"wall={wall:.1f}s status={arm_status}", flush=True)

        # HA_ONLY
        t0 = time.time()
        try:
            recall_ha = _ha_only_recall_numpy(seed, m_items, n_c, vals_c)
            arm_status = "OK"
        except Exception as exc:
            recall_ha = float("nan")
            arm_status = f"ERROR: {type(exc).__name__}: {exc}"
        wall = time.time() - t0
        arms.append({"arm_name": "ARM_HA_ONLY", "M": int(m_items),
                     "beta_used": float("nan"), "recall_cortex": float(recall_ha),
                     "n_items": int(m_items), "N_h": int(n_h), "N_c": int(n_c),
                     "k_hippo_active": int(k_active), "eta_hippo": float(eta_hippo),
                     "cosine_margin_used": float(cos_margin_val),
                     "wall_s": float(wall), "backend": "numpy",
                     "gpu_mem_peak_mb": 0.0, "arm_status": arm_status})
        print(f"  [seed={seed} M={m_items} ARM_HA_ONLY] recall={recall_ha:.3f} "
              f"wall={wall:.1f}s status={arm_status}", flush=True)

        # REPLACE_beta_X
        for beta in beta_list:
            t0 = time.time()
            try:
                recall = _replace_read_numpy(keys_c, vals_c, beta, attn_chunk)
                arm_status = "OK"
            except Exception as exc:
                recall = float("nan")
                arm_status = f"ERROR: {type(exc).__name__}: {exc}"
            wall = time.time() - t0
            arm_name = f"ARM_HA_DENSE_REPLACE_beta{int(beta)}"
            arms.append({"arm_name": arm_name, "M": int(m_items),
                         "beta_used": float(beta),
                         "recall_cortex": float(recall),
                         "n_items": int(m_items), "N_h": int(n_h), "N_c": int(n_c),
                         "k_hippo_active": int(k_active), "eta_hippo": float(eta_hippo),
                         "cosine_margin_used": float(cos_margin_val),
                         "wall_s": float(wall), "backend": "numpy",
                         "gpu_mem_peak_mb": 0.0, "arm_status": arm_status})
            emit_heartbeat(out_dir, unit_idx=int(beta), total_units=len(beta_list),
                           elapsed_s=time.time() - t_M_start,
                           extra={"phase": "beta_read", "arm": arm_name,
                                  "M": m_items, "beta": beta, "recall": recall})
            print(f"  [seed={seed} M={m_items} {arm_name}] "
                  f"recall={recall:.3f} wall={wall:.1f}s status={arm_status}",
                  flush=True)

    return arms


# ---------------------------------------------------------------------------
# FULL_N preview arm (smoke-time; validates discriminator survives scale)
# ---------------------------------------------------------------------------
def run_preview_full_N(seed: int, m_preview: int, beta_preview: float,
                       hippo_sparsity: float, eta_hippo: float,
                       attn_chunk: int, out_dir: Path) -> Dict:
    """Preview arm at N_h=N_c=4096, single beta, single M (largest)."""
    n_h = N_HIPPO_FULL
    n_c = N_CORTEX_FULL
    rng = np.random.RandomState(seed + 101 + m_preview)
    N_raw = 64
    P_in = rng.randn(n_h, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng.randn(n_c, n_h).astype(np.float64) / np.sqrt(n_h)
    keys_raw = rng.choice([-1.0, 1.0], size=(m_preview, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m_preview, N_raw)).astype(np.float64)
    k_active = max(1, int(round(hippo_sparsity * n_h)))

    t0 = time.time()
    try:
        keys_h, vals_h, keys_c, vals_c = _encode_all_numpy(
            keys_raw, vals_raw, P_in, P_hc, n_h, n_c, m_preview, k_active,
        )
        cos_margin = _cosine_margin_estimate(keys_c)
        recall = _replace_read_numpy(keys_c, vals_c, beta_preview, attn_chunk)
        arm_status = "OK"
    except Exception as exc:
        recall = float("nan")
        cos_margin = float("nan")
        arm_status = f"ERROR: {type(exc).__name__}: {exc}"
    wall = time.time() - t0
    return {"arm_name": "ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW",
            "M": int(m_preview),
            "beta_used": float(beta_preview),
            "recall_cortex": float(recall),
            "cosine_margin_used": float(cos_margin),
            "wall_s": float(wall),
            "backend": "numpy",
            "arm_status": arm_status}


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_h_t, N_raw = 512, 64
    k_t = max(1, int(round(HIPPO_SPARSITY * N_h_t)))
    P = rng.randn(N_h_t, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=N_raw).astype(np.float64)
    h = _pattern_separate_sparse_batched(x[np.newaxis, :], P, k_t)[0]
    n_active = int(np.sum(np.abs(h) > 0))
    if n_active != k_t:
        raise AssertionError(f"k-WTA sparsity wrong: got {n_active} != {k_t}")


def _selftest_dense_hopfield_perfect_recall() -> None:
    rng = np.random.RandomState(11)
    M_t, N_t = 8, 32
    V = rng.randn(M_t, N_t).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    q = V[3].copy()
    sims = 50.0 * (V @ q)
    sims -= sims.max()
    w = np.exp(sims)
    w /= w.sum()
    p = V.T @ w
    err = float(np.linalg.norm(p - V[3]))
    if err > 0.1:
        raise AssertionError(f"DENSE_HOPFIELD_SELFTEST FAIL: err={err}")


def _selftest_adaptive_beta_formula_matches_prereg() -> None:
    """META_RULE_AC + formula-provenance check: EXPECTED adaptive-nearest-beta
    at MEASURED cos_margin=0.94 (v2 landed regime)."""
    # At margin=0.94 (from MEASURED@data/exp_cortex_hippo_dense_layer_M8192_v2_seed_7/metrics.json):
    # M=4096  -> raw=12.77 -> nearest swept in {5,8,13,20,32} = 13.0
    # M=8192  -> raw=13.83 -> nearest swept = 13.0
    # M=16384 -> raw=14.89 -> nearest swept = 13.0
    for m in (4096, 8192, 16384):
        raw = _adaptive_beta_formula(m, 0.94)
        expected_raw = math.log2(m) / 0.94
        if abs(raw - expected_raw) > 1e-6:
            raise AssertionError(
                f"adaptive formula mismatch at M={m}: got {raw} exp {expected_raw}"
            )
        # nearest in BETA_SWEEP
        nearest = min(BETA_SWEEP, key=lambda b: abs(b - raw))
        if nearest != ADAPTIVE_NEAREST_BETA[m]:
            raise AssertionError(
                f"nearest-adaptive mismatch at M={m}: computed {nearest} "
                f"vs ADAPTIVE_NEAREST_BETA[{m}]={ADAPTIVE_NEAREST_BETA[m]}"
            )


def _selftest_beta_sweep_cardinality() -> None:
    if len(BETA_SWEEP) != 5:
        raise AssertionError(f"BETA_SWEEP must be 5 values; got {BETA_SWEEP}")
    if set(BETA_SWEEP) != {5.0, 8.0, 13.0, 20.0, 32.0}:
        raise AssertionError(f"BETA_SWEEP set mismatch; got {BETA_SWEEP}")
    if len(M_SWEEP_FULL) != 3:
        raise AssertionError(f"M_SWEEP_FULL must be 3 values; got {M_SWEEP_FULL}")


def _selftest_beta_effect_on_recall_tiny_world() -> None:
    """Discriminator-fires selftest: at tiny M and beta=5 vs beta=32,
    recall values should NOT be bit-identical (verifies beta enters the
    computation)."""
    rng = np.random.RandomState(23)
    M_t, N_t = 64, 128
    V = rng.randn(M_t, N_t).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    K = V.copy()
    r_lo = _replace_read_numpy(K, V, beta=1.0, attn_chunk=M_t)
    r_hi = _replace_read_numpy(K, V, beta=50.0, attn_chunk=M_t)
    if abs(r_lo - r_hi) < 1e-9:
        raise AssertionError(
            f"beta has no effect on recall in selftest: r_lo=r_hi={r_lo}; "
            f"discriminator BROKEN"
        )


def run_all_selftests(seed_this_chunk: int, anchor_name: str) -> None:
    try:
        _selftest_sparse_pattern_separator()
        _selftest_dense_hopfield_perfect_recall()
        _selftest_adaptive_beta_formula_matches_prereg()
        _selftest_beta_sweep_cardinality()
        _selftest_beta_effect_on_recall_tiny_world()
        if f"seed_{seed_this_chunk}" not in anchor_name:
            raise AssertionError(
                f"anchor '{anchor_name}' missing seed_{seed_this_chunk}"
            )
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)


# ---------------------------------------------------------------------------
# Verdict (per-seed cell)
# ---------------------------------------------------------------------------
def _arms_of_M(arms_at_M: List[Dict], predicate) -> List[Dict]:
    return [a for a in arms_at_M if predicate(a)]


def _arm_by_name(arms_at_M: List[Dict], name: str) -> Dict:
    for a in arms_at_M:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(per_seed_result: Dict, run_mode: str,
                    n_c_used: int) -> Tuple[str, str, Dict]:
    """per_seed_result contains 'per_M' -> {M: [arm dicts]}."""
    per_M = per_seed_result.get("per_M", {})
    expected_M_count = 3 if run_mode == "full" else 1
    if len(per_M) != expected_M_count:
        return ("HARD_FAIL",
                f"M_CARDINALITY_BREACH: expected {expected_M_count} M values, "
                f"got {len(per_M)}: {sorted(per_M.keys())}",
                {})

    headline = {"per_M_summary": {}}
    m_keys = sorted(per_M.keys())
    all_pass = True
    fail_reasons: List[str] = []
    warn_reasons: List[str] = []

    for m_val in m_keys:
        arms = per_M[m_val]
        try:
            std = _arm_by_name(arms, "ARM_STANDARD")
            ha = _arm_by_name(arms, "ARM_HA_ONLY")
        except KeyError as e:
            return ("HARD_FAIL",
                    f"ARM_CARDINALITY_BREACH at M={m_val}: missing baseline arm {e}",
                    {})
        beta_arms = _arms_of_M(arms,
                               lambda a: a["arm_name"].startswith(
                                   "ARM_HA_DENSE_REPLACE_beta"))
        if len(beta_arms) != len(BETA_SWEEP):
            return ("HARD_FAIL",
                    f"BETA_CARDINALITY_BREACH at M={m_val}: got {len(beta_arms)}, "
                    f"expected {len(BETA_SWEEP)}",
                    {})

        for a in [std, ha] + beta_arms:
            if a["arm_status"] != "OK":
                fail_reasons.append(
                    f"M={m_val} {a['arm_name']} error: {a['arm_status']}"
                )
                all_pass = False

        # Fairness
        if ha["recall_cortex"] > 0.20:
            fail_reasons.append(
                f"FAIRNESS at M={m_val}: HA_ONLY={ha['recall_cortex']:.3f} > 0.20"
            )
            all_pass = False

        # META_RULE_AF bit-identity across ALL arm outcomes at this M
        # Ceiling-tie exemption widened for beta-sweep: multiple REPLACE_betaX
        # arms tying at 1.000 is a legitimate substrate saturation of the
        # dense-Hopfield READ mechanism (same primitive, different read
        # parameter). The sweep is DESIGNED to characterize the beta band
        # where recall is at ceiling; if all 5 beta land at 1.0 that IS the
        # answer (broad optimum). Bit-identity across REPLACE_betaX pairs is
        # ONLY suspect if it happens at low recall (both = 0.0 = tape not read).
        recalls = [std["recall_cortex"], ha["recall_cortex"]] + \
                  [a["recall_cortex"] for a in beta_arms]
        names = ["ARM_STANDARD", "ARM_HA_ONLY"] + \
                [a["arm_name"] for a in beta_arms]
        m_val_int_for_alpha = int(m_val) if not isinstance(m_val, int) else m_val
        alpha_here = float(m_val_int_for_alpha) / float(n_c_used)
        for i in range(len(recalls)):
            for j in range(i + 1, len(recalls)):
                if abs(recalls[i] - recalls[j]) < 1e-6:
                    # Ceiling-tie exempt: both at 1.0 (substrate saturation).
                    is_ceiling = (abs(recalls[i] - 1.0) < 1e-6
                                  and abs(recalls[j] - 1.0) < 1e-6)
                    both_replace_beta = (
                        "REPLACE_beta" in names[i] and "REPLACE_beta" in names[j]
                    )
                    involves_ha_only = ("HA_ONLY" in names[i]
                                        or "HA_ONLY" in names[j])
                    # Exempt if:
                    #  (a) Both at 1.0 AND both REPLACE_betaX (multi-beta ceiling
                    #      = designed sweep result), OR
                    #  (b) Both at 1.0 AND one STANDARD one REPLACE at low-alpha
                    #      (v2/v3-inherited exemption).
                    #  (c) Both at 0.0 AND ha_only pair (fairness both fail).
                    exempt = False
                    if is_ceiling and both_replace_beta:
                        exempt = True
                    elif is_ceiling and alpha_here < 1.0 and not involves_ha_only:
                        exempt = True
                    # HA_ONLY pair ties at 0.0 not exempt: it's a single arm not paired
                    if not exempt:
                        fail_reasons.append(
                            f"META_RULE_AF at M={m_val}: {names[i]}={recalls[i]:.6f} "
                            f"== {names[j]}={recalls[j]:.6f}"
                        )
                        all_pass = False

        # Beta-sweep primary discriminator
        beta_recalls = {a["beta_used"]: a["recall_cortex"] for a in beta_arms}
        recall_star = max(beta_recalls.values())
        beta_star = max(beta_recalls, key=lambda b: beta_recalls[b])
        m_val_int = int(m_val) if not isinstance(m_val, int) else m_val
        nearest_beta = ADAPTIVE_NEAREST_BETA.get(
            m_val_int,
            min(BETA_SWEEP,
                key=lambda b: abs(b - _adaptive_beta_formula(m_val_int, 0.94)))
        )
        recall_adaptive = beta_recalls[nearest_beta]

        if recall_star < 0.60:
            fail_reasons.append(
                f"REPLACE_BELOW_FLOOR at M={m_val}: recall_star={recall_star:.3f} "
                f"(beta_star={beta_star}) < 0.60"
            )
            all_pass = False
        elif recall_star < 0.80:
            warn_reasons.append(
                f"MB at M={m_val}: recall_star={recall_star:.3f} "
                f"(beta_star={beta_star}) in [0.60, 0.80)"
            )
            all_pass = False

        if recall_adaptive < 0.60:
            fail_reasons.append(
                f"ADAPTIVE_MISALIGN at M={m_val}: recall_adaptive={recall_adaptive:.3f} "
                f"(beta={nearest_beta}) < 0.60"
            )
            all_pass = False
        else:
            ratio = recall_adaptive / max(recall_star, 1e-9)
            if ratio < 0.95:
                warn_reasons.append(
                    f"MB at M={m_val}: adaptive/star={ratio:.3f} "
                    f"(adaptive={recall_adaptive:.3f} @ beta={nearest_beta}, "
                    f"star={recall_star:.3f} @ beta={beta_star})"
                )
                all_pass = False

        headline["per_M_summary"][str(m_val)] = {
            "recall_standard": std["recall_cortex"],
            "recall_ha_only": ha["recall_cortex"],
            "beta_recalls": {str(k): v for k, v in beta_recalls.items()},
            "beta_star": beta_star,
            "recall_star": recall_star,
            "nearest_adaptive_beta": nearest_beta,
            "recall_adaptive": recall_adaptive,
            "adaptive_over_star_ratio": recall_adaptive / max(recall_star, 1e-9),
            "cosine_margin": std.get("cosine_margin_used", float("nan")),
        }

    if fail_reasons:
        return ("HARD_FAIL", "; ".join(fail_reasons)[:800], headline)
    if warn_reasons and not all_pass:
        return ("MIDDLE_BAND", "; ".join(warn_reasons)[:800], headline)
    return ("HARD_PASS",
            "beta-sweep HP: max_beta recall>=0.80 AND adaptive/star>=0.95 at ALL M",
            headline)
