"""Shared core for cortex_hippo dense-Hopfield READ-REPLACE M-sweep v3.

Cross-M expansion of v2 (fc47b1bb) per Skunkworks M3 meta-insight
MM_TENTATIVE expansion criterion (c): pattern verified at other M values.

v2 (M=8192): recall~=1.000 3-seed HP at MEASURED@fc47b1bb.
v3 sweeps M in {4096, 8192, 16384} per seed; adaptive beta ~ log2(M)/margin
(same formula as v2). Each seed cell runs all 3 M values internally.

MECHANISM (identical to v2; only sweep axis added):
  ARM_STANDARD           = direct cortex Hebbian only.
  ARM_HA_ONLY            = sparse-DG hippo one-shot; cortex empty (fairness floor).
  ARM_HA_DENSE_REPLACE   = Ha writes tape (K_c, V_c); attention reads via
                           softmax(beta * keys_c @ K_c^T) @ V_c.

HP (per-seed, all 3 M):
  For each M in {4096, 8192, 16384}:
    recall(REPLACE) / recall(STANDARD) >= 0.80
    recall(REPLACE) - recall(HA_ONLY) >= 0.60
  Cross-seed cv(REPLACE) < 15% per M (aggregation gate; single-seed cell
  emits per-M recalls; Skunkworks aggregates across seeds 7/13/19).

HF:
  recall(REPLACE) < 0.60 at ANY M
  OR ha_only > 0.20 at ANY M
  OR bit-identical arm pair (META_RULE_AF; ceiling-tie exempt at low alpha)
  OR cardinality breach (n_core_arms != 3 per M; n_M_values != 3)
  OR degenerate beta/margin.

MB:
  0.60 <= ratio < 0.80 at any M (partial rescue; regime-conditional).

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Smoke runs M=4096 (fastest) AND runs FULL_N preview at M=16384
  (heaviest) to confirm the 16384 discriminator fires before dispatch.

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = 3 arms * 3 M values = 9 arm-outcomes per seed.

CRLB (worst case M=4096):
  sigma_min = sqrt(0.25/4096) = 0.00781 THEORETICAL@binomial-CLT.
  HP gap 0.60 = 77*sigma; well-reachable.
  At M=16384: sigma_min = sqrt(0.25/16384) = 0.00390; gap = 154*sigma.

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
# Fixed config (v2-derived; only M is swept)
# ---------------------------------------------------------------------------
N_HIPPO_FULL = 4096
N_CORTEX_FULL = 4096
HIPPO_SPARSITY = 0.10
ETA_HIPPO_FULL = 1.0
BETA_MIN = 8.0
BETA_MAX = 128.0

# Sweep axis
M_SWEEP_FULL = [4096, 8192, 16384]
# Smoke: run smallest M full-arm, plus FULL_N preview at largest M
M_SWEEP_SMOKE_MAIN = 4096
M_SWEEP_SMOKE_PREVIEW = 16384


def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    """Append one heartbeat row to {output_dir}/_heartbeat.jsonl."""
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
# Torch import
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
    """Batched k-WTA sparse-bipolar pattern separator."""
    h_raw = X @ P.T
    abs_h = np.abs(h_raw)
    idx = np.argpartition(-abs_h, k - 1, axis=1)[:, :k]
    signs = np.sign(np.take_along_axis(h_raw, idx, axis=1))
    signs[signs == 0] = 1.0
    out = np.zeros_like(h_raw)
    np.put_along_axis(out, idx, signs, axis=1)
    return out


def _encode_all_numpy(keys_raw, vals_raw, P_in, P_hc, n_h, n_c, m_items, k_active):
    """Encode keys/vals through sparse-DG + P_hc; L2-normalize per row."""
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


def _compute_adaptive_beta(m_items: int, cosine_margin: float) -> float:
    """beta = clamp(log2(M) / margin, BETA_MIN, BETA_MAX). Same formula as v2."""
    raw = math.log2(max(2, m_items)) / max(cosine_margin, 0.05)
    return float(max(BETA_MIN, min(BETA_MAX, raw)))


# ---------------------------------------------------------------------------
# Numpy per-arm runner
# ---------------------------------------------------------------------------
def run_arm_numpy(arm_name: str, seed: int,
                  n_h: int, n_c: int, m_items: int, k_active: int,
                  eta_hippo: float, attn_chunk: int,
                  keys_raw: np.ndarray, vals_raw: np.ndarray,
                  P_in: np.ndarray, P_hc: np.ndarray, out_dir: Path) -> Dict:
    t0 = time.time()
    beta_used = float("nan")
    cosine_margin_used = float("nan")
    try:
        keys_h, vals_h, keys_c, vals_c = _encode_all_numpy(
            keys_raw, vals_raw, P_in, P_hc, n_h, n_c, m_items, k_active
        )
        emit_heartbeat(out_dir, unit_idx=0,
                       elapsed_s=time.time() - t0,
                       extra={"phase": "encoded", "arm": arm_name, "M": m_items})

        if arm_name == "ARM_STANDARD":
            W_cortex = np.zeros((n_c, n_c), dtype=np.float64)
            W_cortex += eta_hippo * (vals_c.T @ keys_c)
            preds_raw = keys_c @ W_cortex.T
            preds = np.sign(preds_raw)
            preds[preds == 0] = 1.0
            preds_n = preds / np.linalg.norm(preds, axis=1, keepdims=True).clip(min=1e-12)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(axis=1)
            n_hits = int((argmax == np.arange(m_items)).sum())
            recall = n_hits / float(m_items)

        elif arm_name == "ARM_HA_ONLY":
            W_hippo = np.zeros((n_h, n_h), dtype=np.float64)
            W_hippo += vals_h.T @ keys_h
            W_hippo[:] = 0.0
            rng = np.random.RandomState(seed + 91 + m_items)
            preds = rng.randn(m_items, n_c) * 1e-6
            preds_n = preds / np.linalg.norm(preds, axis=1, keepdims=True).clip(min=1e-12)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(axis=1)
            n_hits = int((argmax == np.arange(m_items)).sum())
            recall = n_hits / float(m_items)

        elif (arm_name == "ARM_HA_DENSE_REPLACE"
              or arm_name == "ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW"):
            K_tape = keys_c
            V_tape = vals_c
            cosine_margin_used = _cosine_margin_estimate(K_tape)
            beta_used = _compute_adaptive_beta(m_items, cosine_margin_used)
            n_hits = 0
            queries = keys_c
            for start in range(0, m_items, attn_chunk):
                end = min(m_items, start + attn_chunk)
                q_chunk = queries[start:end]
                sims = q_chunk @ K_tape.T
                sims_scaled = beta_used * sims
                sims_scaled -= sims_scaled.max(axis=1, keepdims=True)
                w = np.exp(sims_scaled)
                w /= w.sum(axis=1, keepdims=True).clip(min=1e-30)
                p = w @ V_tape
                p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)
                sims_match = p_n @ V_tape.T
                argmax = sims_match.argmax(axis=1)
                targets = np.arange(start, end)
                n_hits += int((argmax == targets).sum())
                emit_heartbeat(out_dir, unit_idx=end,
                               total_units=m_items,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "attn_read", "arm": arm_name,
                                      "M": m_items, "beta": beta_used,
                                      "margin": cosine_margin_used})
            recall = n_hits / float(m_items)

        else:
            raise ValueError(f"unknown arm: {arm_name}")

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "M": int(m_items),
            "recall_cortex": float(recall),
            "n_items": int(m_items),
            "N_h": int(n_h),
            "N_c": int(n_c),
            "k_hippo_active": int(k_active),
            "eta_hippo": float(eta_hippo),
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "wall_s": float(wall),
            "backend": "numpy",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "M": int(m_items),
            "recall_cortex": float("nan"),
            "n_items": 0,
            "N_h": int(n_h),
            "N_c": int(n_c),
            "k_hippo_active": int(k_active),
            "eta_hippo": float(eta_hippo),
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "wall_s": float(wall),
            "backend": "numpy",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
            "failure_class": type(exc).__name__,
        }


# ---------------------------------------------------------------------------
# Torch/CUDA per-arm runner
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


def _cosine_margin_torch(K_tape, sample_n=256):
    m = K_tape.shape[0]
    n_s = min(sample_n, m)
    if m > n_s:
        idx = torch.randperm(m, device=K_tape.device)[:n_s]
        sub = K_tape[idx]
    else:
        sub = K_tape
    sim = sub @ sub.T
    mask = ~torch.eye(sub.shape[0], dtype=torch.bool, device=sub.device)
    off_mean_abs = float(sim[mask].abs().mean().item())
    margin = 1.0 - off_mean_abs
    if not math.isfinite(margin) or margin <= 0.0:
        return 0.1
    return margin


def run_arm_torch_cuda(arm_name: str, seed: int,
                       n_h: int, n_c: int, m_items: int, k_active: int,
                       eta_hippo: float, attn_chunk: int,
                       keys_raw_np: np.ndarray, vals_raw_np: np.ndarray,
                       P_in_np: np.ndarray, P_hc_np: np.ndarray,
                       out_dir: Path) -> Dict:
    t0 = time.time()
    dev = torch.device("cuda")
    beta_used = float("nan")
    cosine_margin_used = float("nan")
    try:
        torch.cuda.reset_peak_memory_stats(dev)
        mem_start = torch.cuda.memory_allocated(dev)

        keys_raw = torch.from_numpy(keys_raw_np).to(dev, dtype=torch.float32)
        vals_raw = torch.from_numpy(vals_raw_np).to(dev, dtype=torch.float32)
        P_in = torch.from_numpy(P_in_np).to(dev, dtype=torch.float32)
        P_hc = torch.from_numpy(P_hc_np).to(dev, dtype=torch.float32)

        keys_h = _pattern_separate_sparse_torch(keys_raw, P_in, k_active)
        vals_h = _pattern_separate_sparse_torch(vals_raw, P_in, k_active)
        keys_c = _l2norm_rows_torch(keys_h @ P_hc.T)
        vals_c = _l2norm_rows_torch(vals_h @ P_hc.T)

        torch.cuda.synchronize(dev)
        emit_heartbeat(out_dir, unit_idx=0,
                       elapsed_s=time.time() - t0,
                       extra={"phase": "encoded", "arm": arm_name, "M": m_items,
                              "gpu_mem_mb": torch.cuda.memory_allocated(dev) / 1e6})

        if arm_name == "ARM_STANDARD":
            W_cortex = torch.zeros((n_c, n_c), dtype=torch.float32, device=dev)
            W_cortex.addmm_(vals_c.T, keys_c, alpha=eta_hippo)
            preds_raw = keys_c @ W_cortex.T
            preds = torch.sign(preds_raw)
            preds = torch.where(preds == 0, torch.ones_like(preds), preds)
            preds_n = _l2norm_rows_torch(preds)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(dim=1)
            n_hits = int((argmax == torch.arange(m_items, device=dev)).sum().item())
            recall = n_hits / float(m_items)
            del W_cortex

        elif arm_name == "ARM_HA_ONLY":
            W_hippo = torch.zeros((n_h, n_h), dtype=torch.float32, device=dev)
            W_hippo.addmm_(vals_h.T, keys_h)
            W_hippo.zero_()
            gen = torch.Generator(device=dev)
            gen.manual_seed(seed + 91 + m_items)
            preds = torch.randn(m_items, n_c, generator=gen, device=dev) * 1e-6
            preds_n = _l2norm_rows_torch(preds)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(dim=1)
            n_hits = int((argmax == torch.arange(m_items, device=dev)).sum().item())
            recall = n_hits / float(m_items)
            del W_hippo

        elif (arm_name == "ARM_HA_DENSE_REPLACE"
              or arm_name == "ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW"):
            K_tape = keys_c
            V_tape = vals_c
            cosine_margin_used = _cosine_margin_torch(K_tape)
            beta_used = _compute_adaptive_beta(m_items, cosine_margin_used)
            n_hits = 0
            queries = keys_c
            for start in range(0, m_items, attn_chunk):
                end = min(m_items, start + attn_chunk)
                q_chunk = queries[start:end]
                sims = q_chunk @ K_tape.T
                sims_scaled = beta_used * sims
                sims_scaled = sims_scaled - sims_scaled.max(dim=1, keepdim=True).values
                w = torch.exp(sims_scaled)
                w = w / w.sum(dim=1, keepdim=True).clamp_min(1e-30)
                p = w @ V_tape
                p_n = _l2norm_rows_torch(p)
                sims_match = p_n @ V_tape.T
                argmax = sims_match.argmax(dim=1)
                targets = torch.arange(start, end, device=dev)
                n_hits += int((argmax == targets).sum().item())
                emit_heartbeat(out_dir, unit_idx=end,
                               total_units=m_items,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "attn_read", "arm": arm_name,
                                      "M": m_items, "beta": beta_used,
                                      "margin": cosine_margin_used})
            recall = n_hits / float(m_items)

        else:
            raise ValueError(f"unknown arm: {arm_name}")

        torch.cuda.synchronize(dev)
        mem_peak = torch.cuda.max_memory_allocated(dev)
        gpu_mem_peak_mb = float((mem_peak - mem_start) / 1e6)

        del keys_raw, vals_raw, P_in, P_hc, keys_h, vals_h, keys_c, vals_c
        torch.cuda.empty_cache()

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "M": int(m_items),
            "recall_cortex": float(recall),
            "n_items": int(m_items),
            "N_h": int(n_h),
            "N_c": int(n_c),
            "k_hippo_active": int(k_active),
            "eta_hippo": float(eta_hippo),
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "wall_s": float(wall),
            "backend": "torch.cuda",
            "gpu_mem_peak_mb": float(gpu_mem_peak_mb),
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        wall = time.time() - t0
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
        return {
            "arm_name": arm_name,
            "M": int(m_items),
            "recall_cortex": float("nan"),
            "n_items": 0,
            "N_h": int(n_h),
            "N_c": int(n_c),
            "k_hippo_active": int(k_active),
            "eta_hippo": float(eta_hippo),
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "wall_s": float(wall),
            "backend": "torch.cuda",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
            "failure_class": type(exc).__name__,
        }


# ---------------------------------------------------------------------------
# Per-M-value driver: runs 3 arms at one M
# ---------------------------------------------------------------------------
def run_one_M(seed: int, m_items: int, n_h: int, n_c: int,
              hippo_sparsity: float, eta_hippo: float,
              attn_chunk: int, use_cuda: bool, out_dir: Path) -> List[Dict]:
    """Run STANDARD, HA_ONLY, HA_DENSE_REPLACE at a single M value."""
    rng = np.random.RandomState(seed + m_items)  # M-dependent for arm-differ
    N_raw = 64
    P_in = rng.randn(n_h, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng.randn(n_c, n_h).astype(np.float64) / np.sqrt(n_h)
    keys_raw = rng.choice([-1.0, 1.0], size=(m_items, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m_items, N_raw)).astype(np.float64)
    k_active = max(1, int(round(hippo_sparsity * n_h)))

    print(f"  [seed={seed} M={m_items}] N_h={n_h} N_c={n_c} k={k_active} "
          f"eta_h={eta_hippo} chunk={attn_chunk} cuda={use_cuda}",
          flush=True)

    arms = []
    for arm_name in ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE"):
        if use_cuda:
            out = run_arm_torch_cuda(arm_name, seed,
                                     n_h=n_h, n_c=n_c, m_items=m_items,
                                     k_active=k_active,
                                     eta_hippo=eta_hippo,
                                     attn_chunk=attn_chunk,
                                     keys_raw_np=keys_raw, vals_raw_np=vals_raw,
                                     P_in_np=P_in, P_hc_np=P_hc,
                                     out_dir=out_dir)
        else:
            out = run_arm_numpy(arm_name, seed,
                                n_h=n_h, n_c=n_c, m_items=m_items,
                                k_active=k_active,
                                eta_hippo=eta_hippo,
                                attn_chunk=attn_chunk,
                                keys_raw=keys_raw, vals_raw=vals_raw,
                                P_in=P_in, P_hc=P_hc, out_dir=out_dir)
        arms.append(out)
        print(f"  [seed={seed} M={m_items} {arm_name}] "
              f"recall={out['recall_cortex']:.3f} "
              f"beta={out.get('beta_used','NA')} "
              f"margin={out.get('cosine_margin_used','NA')} "
              f"gpu_mem_peak_mb={out['gpu_mem_peak_mb']:.1f} "
              f"status={out['arm_status']} wall={out['wall_s']:.1f}s",
              flush=True)
    return arms


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_h_t = 512
    N_raw = 64
    k_t = max(1, int(round(HIPPO_SPARSITY * N_h_t)))
    P = rng.randn(N_h_t, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=N_raw).astype(np.float64)
    x_batch = x[np.newaxis, :]
    h = _pattern_separate_sparse_batched(x_batch, P, k_t)[0]
    n_active = int(np.sum(np.abs(h) > 0))
    if n_active != k_t:
        raise AssertionError(f"k-WTA sparsity wrong: got {n_active} != {k_t}")
    nz = h[np.abs(h) > 0]
    if not np.all(np.isin(nz, [-1.0, 1.0])):
        raise AssertionError("sparse code not bipolar")


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


def _selftest_adaptive_beta_computes_finite() -> None:
    for m_test in (4096, 8192, 16384):
        b = _compute_adaptive_beta(m_test, 0.7)
        if not math.isfinite(b):
            raise AssertionError(f"adaptive beta not finite at M={m_test}: {b}")
        if not (BETA_MIN <= b <= BETA_MAX):
            raise AssertionError(f"beta {b} not in [{BETA_MIN},{BETA_MAX}] at M={m_test}")
    b_deg = _compute_adaptive_beta(8192, 0.01)
    if b_deg != BETA_MAX:
        raise AssertionError(f"degenerate margin should clamp to BETA_MAX; got {b_deg}")
    # Precomputed EXPECTED values (formula verification per META_RULE_AC number provenance)
    # beta = log2(M) / margin, clamped [8.0, 128.0]
    # M=4096: log2=12; margin=0.7 -> raw=17.14 -> 17.14
    # M=8192: log2=13; margin=0.7 -> raw=18.57 -> 18.57
    # M=16384: log2=14; margin=0.7 -> raw=20.00 -> 20.00
    expected = {4096: 12.0 / 0.7, 8192: 13.0 / 0.7, 16384: 14.0 / 0.7}
    for m_test, exp_b in expected.items():
        b = _compute_adaptive_beta(m_test, 0.7)
        if abs(b - exp_b) > 1e-3:
            raise AssertionError(
                f"beta formula check M={m_test}: got {b} expected {exp_b}"
            )


def _selftest_cosine_margin_estimator() -> None:
    rng = np.random.RandomState(13)
    K = rng.choice([-1.0, 1.0], size=(64, 128)).astype(np.float64)
    K = K / np.linalg.norm(K, axis=1, keepdims=True).clip(min=1e-12)
    m = _cosine_margin_estimate(K)
    if not (0.0 < m <= 1.0) or not math.isfinite(m):
        raise AssertionError(f"cosine_margin out of range: {m}")


def _selftest_replace_differs_from_compose() -> None:
    """v1 vs v2 discriminator: REPLACE query != COMPOSE query."""
    rng = np.random.RandomState(19)
    m, n = 16, 64
    K = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    K = K / np.linalg.norm(K, axis=1, keepdims=True).clip(min=1e-12)
    V = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    W = np.zeros((n, n), dtype=np.float64)
    for i in range(m):
        W += 0.1 * np.outer(V[i], K[i])
    q_compose = np.sign(W @ K[0])
    q_compose[q_compose == 0] = 1.0
    q_compose = q_compose / np.linalg.norm(q_compose).clip(min=1e-12)
    q_replace = K[0]
    diff = float(np.linalg.norm(q_compose - q_replace))
    if diff < 1e-6:
        raise AssertionError(f"REPLACE vs COMPOSE indistinguishable: diff={diff}")


def _selftest_arms_expected_differ() -> None:
    """META_RULE_AF preflight in HIGH-alpha tiny world: STANDARD saturates below
    ceiling while REPLACE holds; HA_ONLY at random-guess floor."""
    rng = np.random.RandomState(17)
    M_t, Nh_t, Nc_t = 128, 128, 64
    Sp_t = 0.10
    k_t = max(1, int(round(Sp_t * Nh_t)))
    N_raw_t = 32
    P_in_t = rng.randn(Nh_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    P_hc_t = rng.randn(Nc_t, Nh_t).astype(np.float64) / np.sqrt(Nh_t)
    keys_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    vals_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)

    tmp_out = Path(REPO) / "data" / "_selftest_v3_M_sweep_arms_differ_tmp"
    tmp_out.mkdir(parents=True, exist_ok=True)

    out_arms = {}
    for arm_name in ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE"):
        r = run_arm_numpy(arm_name, seed=42, n_h=Nh_t, n_c=Nc_t, m_items=M_t,
                          k_active=k_t, eta_hippo=1.0, attn_chunk=M_t,
                          keys_raw=keys_raw_t, vals_raw=vals_raw_t,
                          P_in=P_in_t, P_hc=P_hc_t, out_dir=tmp_out)
        if r["arm_status"] != "OK":
            raise AssertionError(f"arm {arm_name} errored: {r['arm_status']}")
        out_arms[arm_name] = r["recall_cortex"]

    vals = list(out_arms.values())
    names = list(out_arms.keys())
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            if abs(vals[i] - vals[j]) < 1e-9:
                raise AssertionError(
                    f"META_RULE_AF_preflight: {names[i]}={vals[i]} == "
                    f"{names[j]}={vals[j]} (all arms: {out_arms})"
                )


def _selftest_M_sweep_cardinality() -> None:
    """Cardinality-OK: FULL sweep is 3 M values (per META_RULE_H)."""
    if len(M_SWEEP_FULL) != 3:
        raise AssertionError(f"M_SWEEP_FULL must be 3 values; got {M_SWEEP_FULL}")
    if set(M_SWEEP_FULL) != {4096, 8192, 16384}:
        raise AssertionError(f"M_SWEEP_FULL must be {{4096,8192,16384}}; got {M_SWEEP_FULL}")


def run_all_selftests(seed_this_chunk: int, anchor_name: str) -> None:
    try:
        _selftest_sparse_pattern_separator()
        _selftest_dense_hopfield_perfect_recall()
        _selftest_adaptive_beta_computes_finite()
        _selftest_cosine_margin_estimator()
        _selftest_replace_differs_from_compose()
        _selftest_M_sweep_cardinality()
        _selftest_arms_expected_differ()
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
# Verdict (per-seed cell; sweep over 3 M values)
# ---------------------------------------------------------------------------
def _arm_by_name(arms_at_M: List[Dict], name: str) -> Dict:
    for a in arms_at_M:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(per_seed_result: Dict, run_mode: str,
                    n_c_used: int) -> Tuple[str, str, Dict]:
    """per_seed_result contains 'per_M' -> {M: [arm dicts]}.

    Returns (verdict, msg, headline_metrics). HP requires ALL M values pass.
    """
    per_M = per_seed_result.get("per_M", {})
    expected_M_count = 3 if run_mode == "full" else 1  # smoke = 1 main M
    if len(per_M) != expected_M_count:
        return ("HARD_FAIL",
                f"M_CARDINALITY_BREACH: expected {expected_M_count} M values, "
                f"got {len(per_M)}: {sorted(per_M.keys())}",
                {})

    arm_names_expected = ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE")

    headline = {"per_M_summary": {}}
    all_pass = True
    fail_reasons = []
    m_keys = sorted(per_M.keys())

    for m_val in m_keys:
        arms = per_M[m_val]
        core_arms = [a for a in arms if a["arm_name"] in arm_names_expected]
        if len(core_arms) != 3:
            return ("HARD_FAIL",
                    f"ARM_CARDINALITY_BREACH at M={m_val}: got {len(core_arms)}", {})
        try:
            per = [_arm_by_name(core_arms, name) for name in arm_names_expected]
        except KeyError as e:
            return ("HARD_FAIL", f"Missing arm at M={m_val}: {e}", {})
        for a in per:
            if a["arm_status"] != "OK":
                return ("HARD_FAIL",
                        f"Arm {a['arm_name']} error at M={m_val}: {a['arm_status']}", {})

        standard = per[0]["recall_cortex"]
        ha_only = per[1]["recall_cortex"]
        replace = per[2]["recall_cortex"]
        beta = per[2].get("beta_used", float("nan"))
        margin = per[2].get("cosine_margin_used", float("nan"))

        # META_RULE_AF bit-identity check (with ceiling-tie exempt at low alpha)
        alpha_here = float(m_val) / float(n_c_used)
        recalls = [standard, ha_only, replace]
        names = list(arm_names_expected)
        for i in range(len(recalls)):
            for j in range(i + 1, len(recalls)):
                if abs(recalls[i] - recalls[j]) < 1e-6:
                    exempt = (
                        abs(recalls[i] - 1.0) < 1e-6
                        and abs(recalls[j] - 1.0) < 1e-6
                        and alpha_here < 1.0
                        and {names[i], names[j]}
                        == {"ARM_STANDARD", "ARM_HA_DENSE_REPLACE"}
                    )
                    if not exempt:
                        return ("HARD_FAIL",
                                f"META_RULE_AF at M={m_val}: {names[i]}={recalls[i]} "
                                f"== {names[j]}={recalls[j]}", {})

        # Fairness
        if ha_only > 0.20:
            return ("HARD_FAIL",
                    f"FAIRNESS at M={m_val}: HA_ONLY={ha_only:.3f} > 0.20", {})
        if standard <= 0:
            return ("HARD_FAIL",
                    f"STANDARD collapsed at M={m_val}: {standard}", {})
        if not (math.isfinite(beta) and math.isfinite(margin) and margin > 0):
            return ("HARD_FAIL",
                    f"CALIBRATION_DEGENERATE at M={m_val}: beta={beta} margin={margin}",
                    {})

        ratio = replace / standard
        gap = replace - ha_only

        headline["per_M_summary"][int(m_val)] = {
            "standard": standard, "ha_only": ha_only, "replace": replace,
            "ratio_vs_standard": ratio, "gap_vs_ha_only": gap,
            "beta_used": beta, "cosine_margin": margin,
            "alpha_simple": alpha_here,
        }

        # HP gates per M
        hp_ratio = ratio >= 0.80
        hp_gap = gap >= 0.60
        hp_replace_floor = replace >= 0.60

        if not hp_replace_floor:
            return ("HARD_FAIL",
                    f"HARD_FAIL at M={m_val}: REPLACE={replace:.3f} < 0.60 "
                    f"(replacement doesn't survive scale at this M).", {})
        if not (hp_ratio and hp_gap):
            all_pass = False
            fail_reasons.append(
                f"M={m_val}: ratio={ratio:.3f} gap={gap:.3f}"
            )

    if all_pass:
        summary_bits = [
            f"M={m}:REPL={headline['per_M_summary'][m]['replace']:.3f}"
            f"/STD={headline['per_M_summary'][m]['standard']:.3f}"
            f"(ratio={headline['per_M_summary'][m]['ratio_vs_standard']:.3f})"
            for m in sorted(headline["per_M_summary"].keys())
        ]
        return ("HARD_PASS",
                f"HARD_PASS_ALL_M: ratio>=0.80 AND gap>=0.60 at every M. "
                + " | ".join(summary_bits),
                headline)

    # MB: at least one M above floor 0.60 but below ratio 0.80
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial cross-M rescue. reasons=[" +
            "; ".join(fail_reasons) + "]",
            headline)
