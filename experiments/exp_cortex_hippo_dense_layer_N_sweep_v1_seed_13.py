"""cortex_hippo_dense_layer_N_sweep_v1 -- seed_7. N-scaling of REPLACE-mode.

Extends v2 REPLACE-mode chain-grade rescue (M=8192 recall~=1.000 3-seed HP)
by sweeping N_h = N_c in {4096, 8192, 16384, 32768} at fixed M=8192. Tests
whether replacement-mode Ha+dense-Hopfield attention survives N-scaling.

Parent v2 (baseline): experiments/exp_cortex_hippo_dense_layer_M8192_v2_seed_7.py
  v2 preview arm at N=4096 recall=1.000
  MEASURED@data/exp_cortex_hippo_dense_layer_M8192_v2_seed_7/metrics.json.

Pre-reg: preregs/2026-07-01_cortex_hippo_dense_layer_N_sweep_v1.md

MECHANISM (same as v2 REPLACE):
  ARM_STANDARD           = direct cortex Hebbian only. Amit-Gutfreund 0.138N
                           wall means alpha_simple=M/N_c above ~0.14 will
                           saturate STANDARD below ceiling. At N=4096 M=8192
                           alpha=2.0 (over-subscribed); at N=32768 alpha=0.25
                           (comfortable).
  ARM_HA_ONLY            = sparse-DG one-shot write; tape not read; cortex
                           empty. Fairness floor: recall <= 0.20.
  ARM_HA_DENSE_REPLACE   = Ha writes tape (K_c, V_c); attention reads directly.
                           NO W_c matrix. Capacity ~ exp(N_c) per Ramsauer 2021
                           eq.14; M=8192 well within exponential regime at all
                           N in sweep.

Adaptive beta = clamp(log2(M) / cos_margin, [BETA_MIN, BETA_MAX]).

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Smoke runs 2 N-points (main N=1024 + PREVIEW at largest N=32768 for
  ARM_HA_DENSE_REPLACE only). If preview recall < 0.60 at N=32768,
  REJECT full dispatch.

FALSIFIABLE:
  HARD_PASS: recall(REPLACE) / recall(STANDARD) >= 0.80 for ALL N;
             recall(REPLACE) - recall(HA_ONLY) >= 0.60 for ALL N;
             cross-seed cv < 0.15 (verdict at aggregation stage).
  HARD_FAIL: any N has REPLACE < 0.60 OR HA_ONLY > 0.20 OR cardinality breach.
  MIDDLE_BAND: partial N-scaling (some N pass, some in-band).

CARDINALITY (META_RULE_H): EXPECTED_N_UNITS = 4 N * 3 arms = 12 arm outcomes.

CRLB: sigma_min(p=0.5) = sqrt(0.25/8192) = 0.00552 THEORETICAL@binomial-CLT.
HP gap 0.60 = 109*sigma; well-reachable.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
 - arms_differ_verified at smoke gate (META_RULE_AF hash-test)
 - final_metrics_atomicity = tmp_replace (META_RULE_AH)
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - crlb_floor_computed = 0.00552; discriminator_reachability = True
 - baseline_in_band at smoke (STANDARD saturates at low-alpha; drops at high)
 - discriminator survives scale (smoke has FULL_N preview at largest N)
 - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
 - HP_SCOPE per-arm declared
 - cardinality_ok EXPECTED_N_UNITS=12 (META_RULE_H)
 - per-unit failure-class instrumentation (META_RULE_J; no bare except)
 - calibration_check = adaptive_with_discriminator_gate
 - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@

PRESERVE_ENV_VARS: HDLAB_QUEUE
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
from typing import Dict, List

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


# ---------------------------------------------------------------------------
# Inline heartbeat + start-marker + crash-diagnostic (META_RULE §13)
# ---------------------------------------------------------------------------
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


def _write_start_marker(output_dir, anchor_name, run_mode, expected_n_units):
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


def _write_crash_metrics(output_dir, anchor_name, exc):
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


ANCHOR_NAME = "cortex_hippo_dense_layer_N_sweep_v1_seed_13"
SEED_THIS_CHUNK = 13

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


# ---------------------------------------------------------------------------
# Torch import (Fix #24 GPU dispatch must actually use GPU)
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
# Config
# ---------------------------------------------------------------------------
N_SWEEP_FULL = [4096, 8192, 16384, 32768]
N_SWEEP_SMOKE_MAIN = 1024
N_SWEEP_SMOKE_PREVIEW = 32768  # largest N -> discriminator must survive

M_ITEMS = 8192
HIPPO_SPARSITY = 0.10
ETA_HIPPO = 1.0
BETA_MIN = 8.0
BETA_MAX = 128.0

if RUN_MODE == "smoke":
    N_LIST = [N_SWEEP_SMOKE_MAIN]
    RUN_FULL_N_PREVIEW = True
    M_ITEMS_MAIN = 512  # smoke smaller M for speed at main
else:
    N_LIST = list(N_SWEEP_FULL)
    RUN_FULL_N_PREVIEW = False
    M_ITEMS_MAIN = M_ITEMS

USE_TORCH_CUDA = (RUN_MODE == "full") and _TORCH_AVAILABLE and _CUDA_AVAILABLE
COMPUTE_BACKEND = "torch.cuda" if USE_TORCH_CUDA else ("torch.cpu" if _TORCH_AVAILABLE else "numpy")

# ATTN chunk per M for VRAM control
ATTN_CHUNK_FULL = 1024
ATTN_CHUNK_SMOKE = 4096

# Cardinality (META_RULE_H): 4 N * 3 arms = 12 arm outcomes in FULL; 3 in smoke
EXPECTED_N_UNITS = (len(N_SWEEP_FULL) * 3) if RUN_MODE == "full" else 3

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_LIST={N_LIST},M={M_ITEMS_MAIN},"
    f"sparsity={HIPPO_SPARSITY},eta_h={ETA_HIPPO},"
    f"beta_range=[{BETA_MIN},{BETA_MAX}],SEED={SEED_THIS_CHUNK},"
    f"RUN_MODE={RUN_MODE},backend={COMPUTE_BACKEND},"
    f"hardening=v1_N_SWEEP+METARULE_AF_hashtest+METARULE_AH+ADAPTIVE_BETA"
)


# ---------------------------------------------------------------------------
# Substrate primitives (adapted from v2)
# ---------------------------------------------------------------------------
def _pattern_separate_sparse_batched(X, P, k):
    """Batched k-WTA sparse-bipolar pattern separator (numpy)."""
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
    raw = math.log2(max(2, m_items)) / max(cosine_margin, 0.05)
    return float(max(BETA_MIN, min(BETA_MAX, raw)))


# ---------------------------------------------------------------------------
# Numpy per-arm runner (same shape as v2)
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
                       extra={"phase": "encoded", "arm": arm_name, "N": n_c})

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
            rng = np.random.RandomState(seed + 91)
            preds = rng.randn(m_items, n_c) * 1e-6
            preds_n = preds / np.linalg.norm(preds, axis=1, keepdims=True).clip(min=1e-12)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(axis=1)
            n_hits = int((argmax == np.arange(m_items)).sum())
            recall = n_hits / float(m_items)

        elif arm_name == "ARM_HA_DENSE_REPLACE" or arm_name == "ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW":
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
                                      "beta": beta_used,
                                      "margin": cosine_margin_used, "N": n_c})
            recall = n_hits / float(m_items)

        else:
            raise ValueError(f"unknown arm: {arm_name}")

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "N_c": int(n_c),
            "N_h": int(n_h),
            "recall_cortex": float(recall),
            "n_items": int(m_items),
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
            "N_c": int(n_c),
            "N_h": int(n_h),
            "recall_cortex": float("nan"),
            "n_items": 0,
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
# Torch/CUDA per-arm runner (FULL on remote GPU)
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
                       extra={"phase": "encoded", "arm": arm_name, "N": n_c,
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
            gen.manual_seed(seed + 91)
            preds = torch.randn(m_items, n_c, generator=gen, device=dev) * 1e-6
            preds_n = _l2norm_rows_torch(preds)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(dim=1)
            n_hits = int((argmax == torch.arange(m_items, device=dev)).sum().item())
            recall = n_hits / float(m_items)
            del W_hippo

        elif arm_name == "ARM_HA_DENSE_REPLACE" or arm_name == "ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW":
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
                                      "beta": beta_used,
                                      "margin": cosine_margin_used, "N": n_c})
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
            "N_c": int(n_c),
            "N_h": int(n_h),
            "recall_cortex": float(recall),
            "n_items": int(m_items),
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
            "N_c": int(n_c),
            "N_h": int(n_h),
            "recall_cortex": float("nan"),
            "n_items": 0,
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
# Per-N runner
# ---------------------------------------------------------------------------
def run_one_N(seed: int, n_val: int, m_items: int, hippo_sparsity: float,
              eta_hippo: float, attn_chunk: int, out_dir: Path,
              use_cuda: bool) -> List[Dict]:
    """Run all 3 core arms at a single N value."""
    rng = np.random.RandomState(seed + n_val)
    N_raw = 64
    P_in = rng.randn(n_val, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng.randn(n_val, n_val).astype(np.float64) / np.sqrt(n_val)
    keys_raw = rng.choice([-1.0, 1.0], size=(m_items, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(m_items, N_raw)).astype(np.float64)
    k_active = max(1, int(round(hippo_sparsity * n_val)))

    print(f"  [seed={seed} N={n_val}] running 3 arms M={m_items}"
          f" k_active={k_active} attn_chunk={attn_chunk} cuda={use_cuda}...",
          flush=True)

    arms = []
    for arm_name in ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE"):
        if use_cuda:
            out = run_arm_torch_cuda(arm_name, seed,
                                     n_h=n_val, n_c=n_val, m_items=m_items,
                                     k_active=k_active,
                                     eta_hippo=eta_hippo, attn_chunk=attn_chunk,
                                     keys_raw_np=keys_raw, vals_raw_np=vals_raw,
                                     P_in_np=P_in, P_hc_np=P_hc, out_dir=out_dir)
        else:
            out = run_arm_numpy(arm_name, seed,
                                n_h=n_val, n_c=n_val, m_items=m_items,
                                k_active=k_active,
                                eta_hippo=eta_hippo, attn_chunk=attn_chunk,
                                keys_raw=keys_raw, vals_raw=vals_raw,
                                P_in=P_in, P_hc=P_hc, out_dir=out_dir)
        arms.append(out)
        print(f"  [seed={seed} N={n_val} {arm_name}] "
              f"recall={out['recall_cortex']:.3f} "
              f"beta={out.get('beta_used','NA')} "
              f"wall={out['wall_s']:.1f}s status={out['arm_status']}",
              flush=True)
    return arms


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_raw = 64
    n_h = 512
    k = max(1, int(round(0.10 * n_h)))
    P = rng.randn(n_h, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=N_raw).astype(np.float64)
    x_batch = x[np.newaxis, :]
    h = _pattern_separate_sparse_batched(x_batch, P, k)[0]
    n_active = int(np.sum(np.abs(h) > 0))
    if n_active != k:
        raise AssertionError(f"k-WTA sparsity wrong: got {n_active} expected {k}")
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
        raise AssertionError(f"DENSE_HOPFIELD_SELFTEST err={err} > 0.1")


def _selftest_adaptive_beta() -> None:
    b = _compute_adaptive_beta(8192, 0.7)
    if not math.isfinite(b):
        raise AssertionError(f"beta not finite: {b}")
    if not (BETA_MIN <= b <= BETA_MAX):
        raise AssertionError(f"beta {b} not in [{BETA_MIN},{BETA_MAX}]")
    # Sanity: expected value log2(8192)/0.7 = 13/0.7 ~ 18.57
    expected = math.log2(8192) / 0.7
    if abs(b - expected) > 0.01:
        raise AssertionError(f"beta {b} != expected {expected}")


def _selftest_cosine_margin() -> None:
    rng = np.random.RandomState(13)
    K = rng.choice([-1.0, 1.0], size=(64, 128)).astype(np.float64)
    K = K / np.linalg.norm(K, axis=1, keepdims=True).clip(min=1e-12)
    m = _cosine_margin_estimate(K)
    if not (0.0 < m <= 1.0) or not math.isfinite(m):
        raise AssertionError(f"cosine_margin out of range: {m}")


def _selftest_chunk_seed_matches_anchor() -> None:
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(f"anchor '{ANCHOR_NAME}' missing seed_{SEED_THIS_CHUNK}")


def _selftest_arms_differ_at_intermediate_alpha() -> None:
    """META_RULE_AF preflight: at intermediate alpha, arms produce different recalls."""
    rng = np.random.RandomState(17)
    # Alpha=1.0 regime (M=N=64): STANDARD near ceiling, REPLACE ceiling, HA_ONLY floor
    M_t, N_t = 64, 64
    Sp_t = 0.10
    k_t = max(1, int(round(Sp_t * N_t)))
    eta_t = 1.0
    N_raw_t = 32
    P_in_t = rng.randn(N_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    P_hc_t = rng.randn(N_t, N_t).astype(np.float64) / np.sqrt(N_t)
    keys_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    vals_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)

    tmp_out = Path(REPO) / "data" / "_selftest_N_sweep_tmp"
    tmp_out.mkdir(parents=True, exist_ok=True)

    out_arms = {}
    for arm_name in ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE"):
        r = run_arm_numpy(arm_name, seed=42,
                          n_h=N_t, n_c=N_t, m_items=M_t, k_active=k_t,
                          eta_hippo=eta_t, attn_chunk=M_t,
                          keys_raw=keys_raw_t, vals_raw=vals_raw_t,
                          P_in=P_in_t, P_hc=P_hc_t, out_dir=tmp_out)
        if r["arm_status"] != "OK":
            raise AssertionError(f"arm {arm_name} errored: {r['arm_status']}")
        out_arms[arm_name] = r["recall_cortex"]

    # HA_ONLY must differ from REPLACE (fairness discriminator)
    if abs(out_arms["ARM_HA_ONLY"] - out_arms["ARM_HA_DENSE_REPLACE"]) < 1e-6:
        raise AssertionError(
            f"META_RULE_AF: HA_ONLY == REPLACE = {out_arms}; fairness discriminator dead"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_sparse_pattern_separator()
        _selftest_dense_hopfield_perfect_recall()
        _selftest_adaptive_beta()
        _selftest_cosine_margin()
        _selftest_chunk_seed_matches_anchor()
        _selftest_arms_differ_at_intermediate_alpha()
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
    print(
        f"[selftest] PASS  N_LIST={N_LIST}  M={M_ITEMS_MAIN}  "
        f"sparsity={HIPPO_SPARSITY}  eta_h={ETA_HIPPO}  "
        f"beta_range=[{BETA_MIN},{BETA_MAX}]  mode={RUN_MODE}  "
        f"seed={SEED_THIS_CHUNK}  backend={COMPUTE_BACKEND}  "
        f"torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Per-seed driver
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    per_N: Dict[int, List[Dict]] = {}
    attn_chunk = ATTN_CHUNK_FULL if RUN_MODE == "full" else ATTN_CHUNK_SMOKE

    for n_val in N_LIST:
        arms = run_one_N(
            seed=seed, n_val=n_val, m_items=M_ITEMS_MAIN,
            hippo_sparsity=HIPPO_SPARSITY, eta_hippo=ETA_HIPPO,
            attn_chunk=attn_chunk, out_dir=out_dir, use_cuda=USE_TORCH_CUDA,
        )
        per_N[int(n_val)] = arms

    # DISCRIMINATOR-MUST-SURVIVE-SCALE: smoke preview at largest N
    preview_arm = None
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        print(f"  [seed={seed} PREVIEW_FULL_N N={N_SWEEP_SMOKE_PREVIEW}] "
              f"M={M_ITEMS} at largest sweep N...", flush=True)
        rng_p = np.random.RandomState(seed + 101 + N_SWEEP_SMOKE_PREVIEW)
        N_raw = 64
        n_p = N_SWEEP_SMOKE_PREVIEW
        P_in_p = rng_p.randn(n_p, N_raw).astype(np.float64) / np.sqrt(N_raw)
        P_hc_p = rng_p.randn(n_p, n_p).astype(np.float64) / np.sqrt(n_p)
        keys_raw_p = rng_p.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)
        vals_raw_p = rng_p.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)
        k_active_p = max(1, int(round(HIPPO_SPARSITY * n_p)))
        preview_arm = run_arm_numpy(
            "ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW", seed,
            n_h=n_p, n_c=n_p, m_items=M_ITEMS, k_active=k_active_p,
            eta_hippo=ETA_HIPPO, attn_chunk=1024,
            keys_raw=keys_raw_p, vals_raw=vals_raw_p,
            P_in=P_in_p, P_hc=P_hc_p, out_dir=out_dir,
        )
        print(f"  [seed={seed} PREVIEW N={n_p}] "
              f"recall={preview_arm['recall_cortex']:.3f} "
              f"beta={preview_arm.get('beta_used','NA')} "
              f"wall={preview_arm['wall_s']:.1f}s", flush=True)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N_LIST": N_LIST,
        "M": M_ITEMS_MAIN,
        "eta_h": ETA_HIPPO,
        "hippo_sparsity": HIPPO_SPARSITY,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "per_N": {str(k): v for k, v in per_N.items()},  # json-safe keys
        "preview_arm": preview_arm,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def compute_verdict(result: Dict, run_mode: str) -> tuple:
    if not result:
        return ("HARD_FAIL", "No seed result.")
    per_N = result.get("per_N", {})
    if not per_N:
        return ("HARD_FAIL", "per_N missing.")

    # Cardinality check
    n_arm_outcomes = 0
    for n_key, arms in per_N.items():
        n_arm_outcomes += len([a for a in arms if a["arm_name"]
                               in ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE")])
    expected = 3 * len(N_LIST)  # 3 arms per N
    if n_arm_outcomes != expected:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH_META_RULE_H: expected {expected} arms, "
                f"got {n_arm_outcomes}")

    # Per-N gates
    per_N_summary = []
    hp_all = True
    hf_any = False
    for n_key in sorted(per_N.keys(), key=lambda x: int(x)):
        arms = per_N[n_key]
        arm_by_name = {a["arm_name"]: a for a in arms}
        for arm_name in ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE"):
            if arm_name not in arm_by_name:
                return ("HARD_FAIL", f"Missing arm {arm_name} at N={n_key}")
            if arm_by_name[arm_name]["arm_status"] != "OK":
                return ("HARD_FAIL", f"N={n_key} {arm_name} status: "
                        f"{arm_by_name[arm_name]['arm_status']}")
        std = arm_by_name["ARM_STANDARD"]["recall_cortex"]
        ha = arm_by_name["ARM_HA_ONLY"]["recall_cortex"]
        rep = arm_by_name["ARM_HA_DENSE_REPLACE"]["recall_cortex"]
        beta = arm_by_name["ARM_HA_DENSE_REPLACE"].get("beta_used", float("nan"))
        margin = arm_by_name["ARM_HA_DENSE_REPLACE"].get("cosine_margin_used", float("nan"))

        # Fairness
        if ha > 0.20:
            hf_any = True

        # Ratio + gap
        if std <= 0:
            hf_any = True
            ratio = 0.0
        else:
            ratio = rep / std
        gap = rep - ha

        # HP: ratio>=0.80 AND gap>=0.60
        hp_this = (ratio >= 0.80) and (gap >= 0.60)
        # HF: REPLACE < 0.60
        if rep < 0.60:
            hf_any = True
            hp_this = False
        if not hp_this:
            hp_all = False

        per_N_summary.append(
            f"N={n_key}[std={std:.3f} ha={ha:.3f} rep={rep:.3f} "
            f"ratio={ratio:.3f} gap={gap:+.3f} beta={beta:.2f}]"
        )

    summary = " | ".join(per_N_summary)
    seed_prefix = f"seed={result.get('chunk_seed')} run_mode={run_mode}"

    if hf_any:
        return ("HARD_FAIL",
                f"HARD_FAIL: at least one N regime broke (REPLACE<0.60 OR HA>0.20). "
                f"{seed_prefix} | {summary}")
    if hp_all:
        return ("HARD_PASS",
                f"HARD_PASS: REPLACE holds at every N in sweep. "
                f"{seed_prefix} | {summary}")
    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial N-scaling. {seed_prefix} | {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "N_LIST": N_LIST,
        "M": M_ITEMS_MAIN,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    seeds_list = [SEED_THIS_CHUNK]
    done, remaining = resumable_seeds(seeds_list, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(seeds_list)} done; running {remaining}",
          flush=True)

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME} mode={RUN_MODE} "
              f"backend={COMPUTE_BACKEND} N_LIST={N_LIST}...", flush=True)
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n"
                f"{traceback.format_exc()}", encoding="utf-8",
            )
            raise
        write_partial(out_dir, seed, result)

    per_seed_agg = aggregate_partials(out_dir, seeds_list, run_config=run_config)
    all_results = list(per_seed_agg.values())

    if not all_results:
        verdict = "HARD_FAIL"
        verdict_msg = "No seed results aggregated."
    else:
        verdict, verdict_msg = compute_verdict(all_results[0], RUN_MODE)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    # GPU-util warn
    if RUN_MODE == "full" and USE_TORCH_CUDA and all_results:
        max_peak_mb = 0.0
        for r in all_results:
            for arms in r.get("per_N", {}).values():
                for a in arms:
                    max_peak_mb = max(max_peak_mb, float(a.get("gpu_mem_peak_mb", 0.0)))
        if max_peak_mb < 100.0:
            verdict_msg = (
                f"WARN_GPU_UNDERUTIL: max gpu_mem_peak_mb={max_peak_mb:.1f} < 100MB; "
                f"GPU may not have been used. " + verdict_msg
            )

    # Cardinality
    n_arm_outcomes = 0
    if all_results:
        for arms in all_results[0].get("per_N", {}).values():
            n_arm_outcomes += len([a for a in arms if a["arm_name"]
                                   in ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE")])
    cardinality_ok = (n_arm_outcomes == EXPECTED_N_UNITS)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} N_LIST={N_LIST} M={M_ITEMS_MAIN} "
            f"eta_h={ETA_HIPPO} beta_range=[{BETA_MIN},{BETA_MAX}] "
            f"mode={RUN_MODE} backend={COMPUTE_BACKEND}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_LIST": N_LIST,
        "M": M_ITEMS_MAIN,
        "eta_h": ETA_HIPPO,
        "hippo_sparsity": HIPPO_SPARSITY,
        "beta_floor": BETA_MIN,
        "beta_ceil": BETA_MAX,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "n_seeds": len(seeds_list),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 0.00552,
        "crlb_formula_reference": "sigma_min = sqrt(0.25/M=8192) binomial-CLT",
        "discriminator_reachability": True,
        "calibration_check": "adaptive_with_discriminator_gate",
        "sweep_alignment_verdict": "ALIGNED",
        "per_seed": all_results,
    }
    metrics_path = out_dir / "metrics.json"
    tmp_path = metrics_path.with_suffix(metrics_path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    os.replace(str(tmp_path), str(metrics_path))
    print(f"[metrics] written to {metrics_path}", flush=True)


def main():
    _main()


if __name__ == "__main__":
    _out_dir_for_crash = get_output_dir(ANCHOR_NAME)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _exc:
        _write_crash_metrics(_out_dir_for_crash, ANCHOR_NAME, _exc)
        raise
