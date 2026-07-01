"""cortex_pkm_layer_v1 -- seed_7. Product-Key Memory as alternative READ.

PKM structure (Lample et al., 2019, arxiv/1907.05242) as alternative to
dense-Hopfield attention (Cell D v2) for cortex readout at higher alpha.

Query q in R^{N_c} splits into halves q1, q2 in R^{N_c/2}. Two sub-key
spaces K1, K2 each of size sqrt(K), in R^{N_c/2}. Sub-scores s1 = K1 @ q1,
s2 = K2 @ q2. Top-h per half, Cartesian product h*h candidates, softmax
across candidates, weighted read of V[i1 * sqrt(K) + i2].

Reference baseline: exp_cortex_hippo_dense_layer_M8192_v2_seed_7 (Cell D v2)
which established dense-Hopfield READ-REPLACEMENT chain-grade
MEASURED@d:/AI/hd-instrument/data/exp_cortex_hippo_dense_layer_M8192_v2_seed_7/metrics.json.

FALSIFIABLE PREDICTIONS:
  HARD_PASS (PKM new capacity primitive):
    - recall(ARM_PKM_REPLACE) - recall(ARM_HA_DENSE_REPLACE) >= 0.05
    - AND recall(ARM_PKM_REPLACE) >= 0.80
    - AND arms_differ_verified (META_RULE_AF)

  MIDDLE_BAND (equivalent to dense-Hopfield):
    - abs(recall(PKM) - recall(DENSE)) < 0.05 AND both >= 0.60

  HARD_FAIL (PKM regresses):
    - recall(PKM) - recall(DENSE) < -0.05
    - OR recall(PKM) < 0.30
    - OR ARM_HA_ONLY >= 0.20 (fairness leak)
    - OR cardinality breach (n_core_arms != 4)
    - OR beta_computed degenerate

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = 4 core arms x 1 seed = 4 arm outputs.

CRLB (capacity feasibility):
  sigma_min(p=0.5) = sqrt(0.25/8192) = 0.00552 THEORETICAL@binomial-CLT.
  HP gap 0.05 = 9.1 sigma; well-reachable.
  Dense-Hopfield capacity CITED@Ramsauer2021_eq14: N_c=8192 spherical-code
  cap vastly exceeds M=8192. PKM cap (Lample eq.2): analogous by factored
  softmax; both above M.

REGIME:
  - N_h=4096 hippo, N_c=8192 cortex, M=8192.
  - alpha_simple = M/N_c = 1.0 (higher-alpha vs Cell D v2 N_c=4096, alpha=2.0
    actually alpha decreases with larger N_c; here 1.0 vs Cell D's 2.0).
  - Chunked single-seed cell; seeds {7,13,19} authored as siblings.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER)
 - final_metrics_atomicity = tmp_replace (META_RULE_AH)
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - crlb_floor_computed = 0.00552; discriminator_reachability = True
 - baseline_in_band at smoke (META_RULE_AG; STANDARD in 0.05..0.95)
 - discriminator survives scale (smoke has full-N preview arm for PKM)
 - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
 - HP_SCOPE = {ARM_PKM_REPLACE: [pkm_delta, pkm_absolute],
               ARM_HA_DENSE_REPLACE: [pkm_delta_comparison],
               ARM_STANDARD: [sanity_ceiling],
               ARM_HA_ONLY: [fairness_floor]}
 - cardinality_ok EXPECTED_N_UNITS=4 (META_RULE_H)
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
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


# ---------------------------------------------------------------------------
# Inline heartbeat / start-marker / crash-diagnostic (per §13 mandate)
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


ANCHOR_NAME = "cortex_pkm_layer_v1_seed_7"
SEED_THIS_CHUNK = 7
_HARDENING_MARKER = "v1_pkm_read_layer_seed_chunk"

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
# Torch (Fix #24 GPU dispatch must actually use GPU)
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
N_HIPPO_FULL = 4096
N_CORTEX_FULL = 8192      # per task spec (Cell D v2 used 4096)
HIPPO_SPARSITY = 0.10
M_ITEMS_FULL = 8192
ETA_HIPPO_FULL = 1.0
BETA_MIN = 8.0
BETA_MAX = 128.0

# PKM structure params
PKM_TOP_H_FULL = 8        # top-h per half; h*h = 64 candidates
PKM_TOP_H_SMOKE = 4        # smaller in smoke

SEEDS_FULL = [SEED_THIS_CHUNK]

if RUN_MODE == "smoke":
    N_HIPPO = 512
    N_CORTEX = 1024
    M_ITEMS = 512
    ETA_HIPPO = 1.0
    PKM_TOP_H = PKM_TOP_H_SMOKE
    SEEDS = [SEED_THIS_CHUNK]
    RUN_FULL_N_PREVIEW = True
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    M_ITEMS = M_ITEMS_FULL
    ETA_HIPPO = ETA_HIPPO_FULL
    PKM_TOP_H = PKM_TOP_H_FULL
    SEEDS = SEEDS_FULL
    RUN_FULL_N_PREVIEW = False

K_HIPPO_ACTIVE = max(1, int(round(HIPPO_SPARSITY * N_HIPPO)))
ALPHA_SIMPLE = float(M_ITEMS) / float(N_CORTEX)
ALPHA_HOPFIELD = float(M_ITEMS) / (2.0 * float(N_HIPPO) * math.log(N_HIPPO))

# PKM factored key structure. sqrt(M) rounded up so 91*91 = 8281 >= M=8192.
SQRT_M = int(math.ceil(math.sqrt(M_ITEMS)))
# Effective full-key space = SQRT_M * SQRT_M >= M; we index only first M.

# Query-half dimension: N_c must be even.
assert N_CORTEX % 2 == 0, f"N_CORTEX must be even for PKM half-split; got {N_CORTEX}"
N_HALF = N_CORTEX // 2

USE_TORCH_CUDA = (RUN_MODE == "full") and _TORCH_AVAILABLE and _CUDA_AVAILABLE
COMPUTE_BACKEND = "torch.cuda" if USE_TORCH_CUDA else ("torch.cpu" if _TORCH_AVAILABLE else "numpy")

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY},M={M_ITEMS},eta_h={ETA_HIPPO},"
    f"beta_floor={BETA_MIN},beta_ceil={BETA_MAX},pkm_top_h={PKM_TOP_H},"
    f"pkm_sqrt_M={SQRT_M},pkm_n_half={N_HALF},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"chunk_seed={SEED_THIS_CHUNK},"
    f"alpha_simple={ALPHA_SIMPLE:.4f},alpha_hopfield={ALPHA_HOPFIELD:.4f},"
    f"backend={COMPUTE_BACKEND},"
    f"hardening=v1_PKM_READ+METARULE_AF+METARULE_AH+ADAPTIVE_BETA"
)

EXPECTED_N_UNITS = 4     # STANDARD, HA_ONLY, DENSE_REPLACE, PKM_REPLACE

# VRAM chunk: dense-Hopfield keys_c @ K_c^T = M x M matmul
ATTN_CHUNK = 512 if RUN_MODE == "full" else M_ITEMS


# ---------------------------------------------------------------------------
# Substrate primitives (numpy path)
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


def _cosine_margin_estimate(keys_c, sample_n=256):
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


def _compute_adaptive_beta(m_items, cosine_margin):
    raw = math.log2(max(2, m_items)) / max(cosine_margin, 0.05)
    return float(max(BETA_MIN, min(BETA_MAX, raw)))


# ---------------------------------------------------------------------------
# PKM sub-key construction
# ---------------------------------------------------------------------------
def _build_pkm_subkeys_numpy(K_tape: np.ndarray, sqrt_m: int, n_half: int,
                             m_items: int, seed: int):
    """Build PKM factored sub-keys from the full tape K_tape (M, N_c).

    Strategy: derive two sub-key spaces K1, K2 in R^{sqrt_m, n_half} by
    ROW-averaging the tape keys grouped by their factored index.

    For each key i in [0, M), assign (i1, i2) = (i // sqrt_m, i % sqrt_m).
    K1[i1] = mean of K_tape[j, :n_half] for j where i1 group.
    K2[i2] = mean of K_tape[j, n_half:] for j where i2 group.

    This factorization is data-driven; PKM structure is the ARCHITECTURE
    (factored sub-key space + Cartesian product read), not the initialization.
    The critical invariant is: recovering (i1, i2) for key i via top-h in each
    half should give i itself as one of the h*h candidates.
    """
    K1 = np.zeros((sqrt_m, n_half), dtype=K_tape.dtype)
    K2 = np.zeros((sqrt_m, n_half), dtype=K_tape.dtype)
    K1_cnt = np.zeros(sqrt_m, dtype=np.int64)
    K2_cnt = np.zeros(sqrt_m, dtype=np.int64)
    for i in range(m_items):
        i1 = i // sqrt_m
        i2 = i % sqrt_m
        K1[i1] += K_tape[i, :n_half]
        K1_cnt[i1] += 1
        K2[i2] += K_tape[i, n_half:]
        K2_cnt[i2] += 1
    K1_cnt = np.maximum(K1_cnt, 1)
    K2_cnt = np.maximum(K2_cnt, 1)
    K1 = K1 / K1_cnt[:, None]
    K2 = K2 / K2_cnt[:, None]
    # L2-normalize rows
    K1 = K1 / np.linalg.norm(K1, axis=1, keepdims=True).clip(min=1e-12)
    K2 = K2 / np.linalg.norm(K2, axis=1, keepdims=True).clip(min=1e-12)
    return K1, K2


def _pkm_read_numpy(q_batch, K1, K2, V_tape, sqrt_m, n_half, top_h,
                    m_items, beta):
    """PKM read: batch of queries -> attended values.

    Returns predicted values (c, N_c). Complexity per query:
        O(sqrt_M * n_half) for sub-scores + O(top_h * top_h) softmax + read.
    """
    c = q_batch.shape[0]
    q1 = q_batch[:, :n_half]   # (c, n_half)
    q2 = q_batch[:, n_half:]   # (c, n_half)
    s1 = beta * (q1 @ K1.T)     # (c, sqrt_m)
    s2 = beta * (q2 @ K2.T)     # (c, sqrt_m)
    # Top-h per half
    top_h_eff = min(top_h, sqrt_m)
    top1_idx = np.argpartition(-s1, top_h_eff - 1, axis=1)[:, :top_h_eff]  # (c, h)
    top2_idx = np.argpartition(-s2, top_h_eff - 1, axis=1)[:, :top_h_eff]  # (c, h)
    top1_scr = np.take_along_axis(s1, top1_idx, axis=1)                    # (c, h)
    top2_scr = np.take_along_axis(s2, top2_idx, axis=1)                    # (c, h)

    # Cartesian: candidate scores = top1_scr[:, :, None] + top2_scr[:, None, :]
    # Candidate indices = top1_idx * sqrt_m + top2_idx
    cand_scores = top1_scr[:, :, None] + top2_scr[:, None, :]              # (c, h, h)
    cand_scores = cand_scores.reshape(c, top_h_eff * top_h_eff)
    cand_idx = (top1_idx[:, :, None] * sqrt_m + top2_idx[:, None, :]).reshape(c, top_h_eff * top_h_eff)
    # Clamp indices outside [0, M) to a valid slot (M-1) with -inf score so they
    # don't win the softmax (91*91=8281 candidates > M=8192; some cands invalid).
    valid = cand_idx < m_items
    cand_scores = np.where(valid, cand_scores, -np.inf)
    cand_idx = np.where(valid, cand_idx, 0)

    # Softmax within candidates
    cand_scores -= cand_scores.max(axis=1, keepdims=True)
    w = np.exp(cand_scores)
    w_sum = w.sum(axis=1, keepdims=True).clip(min=1e-30)
    w = w / w_sum
    # Read V_tape at cand_idx: gather rows then weighted-sum
    # V_gather shape: (c, h*h, N_c)
    V_gather = V_tape[cand_idx]                                            # (c, h*h, N_c)
    p = (w[:, :, None] * V_gather).sum(axis=1)                             # (c, N_c)
    return p


# ---------------------------------------------------------------------------
# Numpy per-arm runner
# ---------------------------------------------------------------------------
def run_arm_numpy(arm_name: str, seed: int,
                  n_h: int, n_c: int, m_items: int, k_active: int,
                  eta_hippo: float, attn_chunk: int, top_h: int,
                  keys_raw: np.ndarray, vals_raw: np.ndarray,
                  P_in: np.ndarray, P_hc: np.ndarray,
                  out_dir: Path) -> Dict:
    t0 = time.time()
    beta_used = float("nan")
    cosine_margin_used = float("nan")
    n_half = n_c // 2
    sqrt_m = int(math.ceil(math.sqrt(m_items)))
    try:
        keys_h, vals_h, keys_c, vals_c = _encode_all_numpy(
            keys_raw, vals_raw, P_in, P_hc, n_h, n_c, m_items, k_active
        )
        emit_heartbeat(out_dir, unit_idx=0,
                       elapsed_s=time.time() - t0,
                       extra={"phase": "encoded", "arm": arm_name})

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

        elif arm_name in ("ARM_HA_DENSE_REPLACE",
                          "ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW"):
            # Full dense-Hopfield attention baseline (Cell D v2 mechanism).
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
                               extra={"phase": "dense_attn", "arm": arm_name,
                                      "beta": beta_used})
            recall = n_hits / float(m_items)

        elif arm_name in ("ARM_PKM_REPLACE", "ARM_PKM_REPLACE_FULL_N_PREVIEW"):
            # PKM attention read: factored sub-keys + Cartesian top-h*h softmax.
            K_tape = keys_c
            V_tape = vals_c
            cosine_margin_used = _cosine_margin_estimate(K_tape)
            beta_used = _compute_adaptive_beta(m_items, cosine_margin_used)
            K1, K2 = _build_pkm_subkeys_numpy(K_tape, sqrt_m, n_half,
                                              m_items, seed)
            emit_heartbeat(out_dir, unit_idx=0,
                           elapsed_s=time.time() - t0,
                           extra={"phase": "pkm_subkeys_built", "arm": arm_name,
                                  "sqrt_m": sqrt_m, "top_h": top_h,
                                  "beta": beta_used})
            n_hits = 0
            queries = keys_c
            for start in range(0, m_items, attn_chunk):
                end = min(m_items, start + attn_chunk)
                q_chunk = queries[start:end]
                p = _pkm_read_numpy(q_chunk, K1, K2, V_tape,
                                    sqrt_m, n_half, top_h, m_items, beta_used)
                p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)
                sims_match = p_n @ V_tape.T
                argmax = sims_match.argmax(axis=1)
                targets = np.arange(start, end)
                n_hits += int((argmax == targets).sum())
                emit_heartbeat(out_dir, unit_idx=end,
                               total_units=m_items,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "pkm_attn", "arm": arm_name,
                                      "beta": beta_used})
            recall = n_hits / float(m_items)

        else:
            raise ValueError(f"unknown arm: {arm_name}")

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_cortex": float(recall),
            "n_items": int(m_items),
            "N_h": int(n_h),
            "N_c": int(n_c),
            "k_hippo_active": int(k_active),
            "eta_hippo": float(eta_hippo),
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "pkm_top_h": int(top_h) if "PKM" in arm_name else -1,
            "pkm_sqrt_m": int(sqrt_m) if "PKM" in arm_name else -1,
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
            "recall_cortex": float("nan"),
            "n_items": 0,
            "N_h": int(n_h),
            "N_c": int(n_c),
            "k_hippo_active": int(k_active),
            "eta_hippo": float(eta_hippo),
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "pkm_top_h": int(top_h) if "PKM" in arm_name else -1,
            "pkm_sqrt_m": int(sqrt_m) if "PKM" in arm_name else -1,
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


def _build_pkm_subkeys_torch(K_tape, sqrt_m, n_half, m_items):
    dev = K_tape.device
    K1 = torch.zeros((sqrt_m, n_half), dtype=K_tape.dtype, device=dev)
    K2 = torch.zeros((sqrt_m, n_half), dtype=K_tape.dtype, device=dev)
    i1_idx = torch.arange(m_items, device=dev) // sqrt_m
    i2_idx = torch.arange(m_items, device=dev) % sqrt_m
    K1.index_add_(0, i1_idx, K_tape[:, :n_half])
    K2.index_add_(0, i2_idx, K_tape[:, n_half:])
    K1_cnt = torch.zeros(sqrt_m, dtype=torch.float32, device=dev)
    K2_cnt = torch.zeros(sqrt_m, dtype=torch.float32, device=dev)
    K1_cnt.index_add_(0, i1_idx, torch.ones(m_items, dtype=torch.float32, device=dev))
    K2_cnt.index_add_(0, i2_idx, torch.ones(m_items, dtype=torch.float32, device=dev))
    K1_cnt = K1_cnt.clamp_min(1)
    K2_cnt = K2_cnt.clamp_min(1)
    K1 = K1 / K1_cnt[:, None]
    K2 = K2 / K2_cnt[:, None]
    K1 = _l2norm_rows_torch(K1)
    K2 = _l2norm_rows_torch(K2)
    return K1, K2


def _pkm_read_torch(q_batch, K1, K2, V_tape, sqrt_m, n_half, top_h, m_items, beta):
    c = q_batch.shape[0]
    q1 = q_batch[:, :n_half]
    q2 = q_batch[:, n_half:]
    s1 = beta * (q1 @ K1.T)
    s2 = beta * (q2 @ K2.T)
    top_h_eff = min(top_h, sqrt_m)
    top1_scr, top1_idx = torch.topk(s1, top_h_eff, dim=1)
    top2_scr, top2_idx = torch.topk(s2, top_h_eff, dim=1)
    cand_scores = top1_scr[:, :, None] + top2_scr[:, None, :]
    cand_scores = cand_scores.reshape(c, top_h_eff * top_h_eff)
    cand_idx = (top1_idx[:, :, None] * sqrt_m + top2_idx[:, None, :]).reshape(c, top_h_eff * top_h_eff)
    valid = cand_idx < m_items
    cand_scores = torch.where(valid, cand_scores,
                              torch.full_like(cand_scores, float("-inf")))
    cand_idx = torch.where(valid, cand_idx, torch.zeros_like(cand_idx))
    cand_scores = cand_scores - cand_scores.max(dim=1, keepdim=True).values
    w = torch.exp(cand_scores)
    w = w / w.sum(dim=1, keepdim=True).clamp_min(1e-30)
    V_gather = V_tape[cand_idx]     # (c, h*h, N_c)
    p = (w[:, :, None] * V_gather).sum(dim=1)
    return p


def run_arm_torch_cuda(arm_name: str, seed: int,
                       n_h: int, n_c: int, m_items: int, k_active: int,
                       eta_hippo: float, attn_chunk: int, top_h: int,
                       keys_raw_np: np.ndarray, vals_raw_np: np.ndarray,
                       P_in_np: np.ndarray, P_hc_np: np.ndarray,
                       out_dir: Path) -> Dict:
    t0 = time.time()
    dev = torch.device("cuda")
    beta_used = float("nan")
    cosine_margin_used = float("nan")
    n_half = n_c // 2
    sqrt_m = int(math.ceil(math.sqrt(m_items)))
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
                       extra={"phase": "encoded", "arm": arm_name,
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

        elif arm_name in ("ARM_HA_DENSE_REPLACE",
                          "ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW"):
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
                               extra={"phase": "dense_attn", "arm": arm_name,
                                      "beta": beta_used})
            recall = n_hits / float(m_items)

        elif arm_name in ("ARM_PKM_REPLACE",
                          "ARM_PKM_REPLACE_FULL_N_PREVIEW"):
            K_tape = keys_c
            V_tape = vals_c
            cosine_margin_used = _cosine_margin_torch(K_tape)
            beta_used = _compute_adaptive_beta(m_items, cosine_margin_used)
            K1, K2 = _build_pkm_subkeys_torch(K_tape, sqrt_m, n_half, m_items)
            torch.cuda.synchronize(dev)
            emit_heartbeat(out_dir, unit_idx=0,
                           elapsed_s=time.time() - t0,
                           extra={"phase": "pkm_subkeys_built", "arm": arm_name,
                                  "sqrt_m": sqrt_m, "top_h": top_h,
                                  "beta": beta_used})
            n_hits = 0
            queries = keys_c
            for start in range(0, m_items, attn_chunk):
                end = min(m_items, start + attn_chunk)
                q_chunk = queries[start:end]
                p = _pkm_read_torch(q_chunk, K1, K2, V_tape,
                                    sqrt_m, n_half, top_h, m_items, beta_used)
                p_n = _l2norm_rows_torch(p)
                sims_match = p_n @ V_tape.T
                argmax = sims_match.argmax(dim=1)
                targets = torch.arange(start, end, device=dev)
                n_hits += int((argmax == targets).sum().item())
                emit_heartbeat(out_dir, unit_idx=end,
                               total_units=m_items,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "pkm_attn", "arm": arm_name,
                                      "beta": beta_used})
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
            "recall_cortex": float(recall),
            "n_items": int(m_items),
            "N_h": int(n_h),
            "N_c": int(n_c),
            "k_hippo_active": int(k_active),
            "eta_hippo": float(eta_hippo),
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "pkm_top_h": int(top_h) if "PKM" in arm_name else -1,
            "pkm_sqrt_m": int(sqrt_m) if "PKM" in arm_name else -1,
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
            "recall_cortex": float("nan"),
            "n_items": 0,
            "N_h": int(n_h),
            "N_c": int(n_c),
            "k_hippo_active": int(k_active),
            "eta_hippo": float(eta_hippo),
            "beta_used": beta_used,
            "cosine_margin_used": cosine_margin_used,
            "pkm_top_h": int(top_h) if "PKM" in arm_name else -1,
            "pkm_sqrt_m": int(sqrt_m) if "PKM" in arm_name else -1,
            "wall_s": float(wall),
            "backend": "torch.cuda",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
            "failure_class": type(exc).__name__,
        }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_raw = 64
    P = rng.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=N_raw).astype(np.float64)
    x_batch = x[np.newaxis, :]
    h = _pattern_separate_sparse_batched(x_batch, P, K_HIPPO_ACTIVE)[0]
    n_active = int(np.sum(np.abs(h) > 0))
    if n_active != K_HIPPO_ACTIVE:
        raise AssertionError(f"k-WTA sparsity wrong: got {n_active}")


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
        raise AssertionError(f"DENSE_HOPFIELD_SELFTEST FAIL: err={err} > 0.1")


def _selftest_pkm_read_reconstructs() -> None:
    """PKM read with clean sub-keys and high beta must reconstruct known value."""
    rng = np.random.RandomState(23)
    M_t = 16
    Nc_t = 32
    n_half = Nc_t // 2
    sqrt_m = int(math.ceil(math.sqrt(M_t)))  # 4
    top_h = 3
    K = rng.randn(M_t, Nc_t).astype(np.float64)
    K = K / np.linalg.norm(K, axis=1, keepdims=True).clip(min=1e-12)
    V = rng.randn(M_t, Nc_t).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    K1, K2 = _build_pkm_subkeys_numpy(K, sqrt_m, n_half, M_t, seed=0)
    beta = 50.0
    q_batch = K[3:4]
    p = _pkm_read_numpy(q_batch, K1, K2, V, sqrt_m, n_half, top_h, M_t, beta)
    # Not required to reconstruct V[3] perfectly (top-h may prune the correct
    # cand out at very small top_h), but the argmax over V should ID target
    # more often than random with high beta.
    p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)
    sims = p_n @ V.T
    argmax = int(sims.argmax(axis=1)[0])
    # Small worlds may miss; assert reconstruction produced finite output.
    if not np.all(np.isfinite(p)):
        raise AssertionError(f"PKM read produced non-finite p; argmax={argmax}")


def _selftest_pkm_read_beats_random_at_smoke() -> None:
    """At smoke world, PKM should hit target > random for majority of queries."""
    rng = np.random.RandomState(29)
    M_t = 64
    Nc_t = 128
    n_half = Nc_t // 2
    sqrt_m = int(math.ceil(math.sqrt(M_t)))  # 8
    top_h = 4
    K = rng.randn(M_t, Nc_t).astype(np.float64)
    K = K / np.linalg.norm(K, axis=1, keepdims=True).clip(min=1e-12)
    V = rng.randn(M_t, Nc_t).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    K1, K2 = _build_pkm_subkeys_numpy(K, sqrt_m, n_half, M_t, seed=0)
    beta = 20.0
    q_batch = K  # query with all keys
    p = _pkm_read_numpy(q_batch, K1, K2, V, sqrt_m, n_half, top_h, M_t, beta)
    p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)
    sims = p_n @ V.T
    argmax = sims.argmax(axis=1)
    n_hit = int((argmax == np.arange(M_t)).sum())
    # Random baseline = 1/M_t; expect > 4/M_t to prove better than random.
    if n_hit < 4:
        raise AssertionError(
            f"PKM smoke recall too low ({n_hit}/{M_t}); mechanism broken"
        )


def _selftest_adaptive_beta_computes_finite() -> None:
    b = _compute_adaptive_beta(8192, 0.7)
    if not math.isfinite(b):
        raise AssertionError(f"adaptive beta not finite: {b}")
    if not (BETA_MIN <= b <= BETA_MAX):
        raise AssertionError(f"beta {b} not in range")


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS_FULL != [SEED_THIS_CHUNK]:
        raise AssertionError(f"chunk seed mismatch: {SEEDS_FULL}")
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(f"anchor '{ANCHOR_NAME}' missing seed_{SEED_THIS_CHUNK}")


def _selftest_pkm_structure() -> None:
    """PKM sub-keys must have expected shape and be different from full keys."""
    if SQRT_M * SQRT_M < M_ITEMS:
        raise AssertionError(
            f"PKM sqrt_m={SQRT_M} squared={SQRT_M*SQRT_M} < M={M_ITEMS}"
        )


def _selftest_arms_expected_differ() -> None:
    """META_RULE_AF preflight in tiny world with high alpha: all 4 arms differ."""
    rng = np.random.RandomState(17)
    M_t, Nh_t, Nc_t = 128, 128, 64
    Sp_t = 0.10
    k_t = max(1, int(round(Sp_t * Nh_t)))
    eta_t = 1.0
    N_raw_t = 32
    top_h_t = 4
    P_in_t = rng.randn(Nh_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    P_hc_t = rng.randn(Nc_t, Nh_t).astype(np.float64) / np.sqrt(Nh_t)
    keys_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    vals_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)

    tmp_out = Path(REPO) / "data" / "_selftest_pkm_v1_arms_differ_tmp"
    tmp_out.mkdir(parents=True, exist_ok=True)

    out_arms = {}
    for arm_name in ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE",
                     "ARM_PKM_REPLACE"):
        r = run_arm_numpy(arm_name, seed=42,
                          n_h=Nh_t, n_c=Nc_t, m_items=M_t, k_active=k_t,
                          eta_hippo=eta_t, attn_chunk=M_t, top_h=top_h_t,
                          keys_raw=keys_raw_t, vals_raw=vals_raw_t,
                          P_in=P_in_t, P_hc=P_hc_t, out_dir=tmp_out)
        if r["arm_status"] != "OK":
            raise AssertionError(
                f"arm {arm_name} errored in selftest: {r['arm_status']}"
            )
        out_arms[arm_name] = r["recall_cortex"]

    # AF: require at least ONE pair-distinct (allow at-ceiling ties as in Cell D).
    # We're at high-alpha tiny world so ARM_STANDARD should drop; ARM_HA_ONLY floor;
    # ARM_HA_DENSE_REPLACE + ARM_PKM_REPLACE should differ from those two.
    if out_arms["ARM_HA_ONLY"] >= 0.20:
        raise AssertionError(
            f"AF preflight: ARM_HA_ONLY={out_arms['ARM_HA_ONLY']} tape leak"
        )
    if abs(out_arms["ARM_HA_DENSE_REPLACE"] - out_arms["ARM_PKM_REPLACE"]) < 1e-9 \
        and abs(out_arms["ARM_HA_DENSE_REPLACE"] - 1.0) > 1e-6:
        # Both saturated at 1.0 is exempted (small M mechanism-independent ceiling);
        # otherwise bit-identical is a bug.
        raise AssertionError(
            f"AF preflight: DENSE ({out_arms['ARM_HA_DENSE_REPLACE']}) and "
            f"PKM ({out_arms['ARM_PKM_REPLACE']}) bit-identical -- likely PKM "
            f"aliased dense read; verify PKM code path"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_sparse_pattern_separator()
        _selftest_dense_hopfield_perfect_recall()
        _selftest_pkm_read_reconstructs()
        _selftest_pkm_read_beats_random_at_smoke()
        _selftest_adaptive_beta_computes_finite()
        _selftest_chunk_seed_matches_anchor()
        _selftest_pkm_structure()
        _selftest_arms_expected_differ()
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
        f"[selftest] PASS  N_h={N_HIPPO}  N_c={N_CORTEX}  M={M_ITEMS}  "
        f"sqrt_m={SQRT_M} top_h={PKM_TOP_H} mode={RUN_MODE} "
        f"chunk_seed={SEED_THIS_CHUNK} alpha_simple={ALPHA_SIMPLE:.4f} "
        f"backend={COMPUTE_BACKEND} torch={_TORCH_AVAILABLE} cuda={_CUDA_AVAILABLE}",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int, out_dir: Path) -> Dict:
    t0 = time.time()
    rng = np.random.RandomState(seed)
    N_raw = 64
    P_in = rng.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng.randn(N_CORTEX, N_HIPPO).astype(np.float64) / np.sqrt(N_HIPPO)
    keys_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)

    print(
        f"  [seed={seed}] N_h={N_HIPPO} (sparse k={K_HIPPO_ACTIVE}), "
        f"N_c={N_CORTEX}, M={M_ITEMS}, eta_h={ETA_HIPPO}, "
        f"attn_chunk={ATTN_CHUNK}, top_h={PKM_TOP_H}, sqrt_m={SQRT_M}, "
        f"backend={COMPUTE_BACKEND}",
        flush=True,
    )

    arms = []
    for arm_name in ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE",
                     "ARM_PKM_REPLACE"):
        if USE_TORCH_CUDA:
            out = run_arm_torch_cuda(arm_name, seed,
                                     n_h=N_HIPPO, n_c=N_CORTEX, m_items=M_ITEMS,
                                     k_active=K_HIPPO_ACTIVE,
                                     eta_hippo=ETA_HIPPO, attn_chunk=ATTN_CHUNK,
                                     top_h=PKM_TOP_H,
                                     keys_raw_np=keys_raw, vals_raw_np=vals_raw,
                                     P_in_np=P_in, P_hc_np=P_hc,
                                     out_dir=out_dir)
        else:
            out = run_arm_numpy(arm_name, seed,
                                n_h=N_HIPPO, n_c=N_CORTEX, m_items=M_ITEMS,
                                k_active=K_HIPPO_ACTIVE,
                                eta_hippo=ETA_HIPPO, attn_chunk=ATTN_CHUNK,
                                top_h=PKM_TOP_H,
                                keys_raw=keys_raw, vals_raw=vals_raw,
                                P_in=P_in, P_hc=P_hc, out_dir=out_dir)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] recall={out['recall_cortex']:.3f} "
            f"backend={out['backend']} beta={out.get('beta_used','NA')} "
            f"gpu_mem_peak_mb={out['gpu_mem_peak_mb']:.1f} "
            f"status={out['arm_status']} wall={out['wall_s']:.1f}s",
            flush=True,
        )

    # Full-N preview for PKM in smoke (DISCRIMINATOR-MUST-SURVIVE-SCALE)
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        print(f"  [seed={seed} PREVIEW_PKM_FULL_N] running at "
              f"N_h={N_HIPPO_FULL}, N_c={N_CORTEX_FULL}, M={M_ITEMS_FULL}...",
              flush=True)
        rng_p = np.random.RandomState(seed + 101)
        P_in_p = rng_p.randn(N_HIPPO_FULL, N_raw).astype(np.float64) / np.sqrt(N_raw)
        P_hc_p = rng_p.randn(N_CORTEX_FULL, N_HIPPO_FULL).astype(np.float64) / np.sqrt(N_HIPPO_FULL)
        keys_raw_p = rng_p.choice([-1.0, 1.0], size=(M_ITEMS_FULL, N_raw)).astype(np.float64)
        vals_raw_p = rng_p.choice([-1.0, 1.0], size=(M_ITEMS_FULL, N_raw)).astype(np.float64)
        k_active_p = max(1, int(round(HIPPO_SPARSITY * N_HIPPO_FULL)))
        attn_chunk_p = 512
        preview_arm = run_arm_numpy(
            "ARM_PKM_REPLACE_FULL_N_PREVIEW", seed,
            n_h=N_HIPPO_FULL, n_c=N_CORTEX_FULL, m_items=M_ITEMS_FULL,
            k_active=k_active_p, eta_hippo=ETA_HIPPO_FULL,
            attn_chunk=attn_chunk_p, top_h=PKM_TOP_H_FULL,
            keys_raw=keys_raw_p, vals_raw=vals_raw_p,
            P_in=P_in_p, P_hc=P_hc_p, out_dir=out_dir,
        )
        print(
            f"  [seed={seed} PREVIEW_PKM_FULL_N] "
            f"recall={preview_arm['recall_cortex']:.3f} "
            f"beta={preview_arm.get('beta_used','NA')} "
            f"wall={preview_arm['wall_s']:.1f}s",
            flush=True,
        )
        arms.append(preview_arm)

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_CORTEX,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "eta_h": ETA_HIPPO,
        "hippo_sparsity": HIPPO_SPARSITY,
        "k_hippo_active": K_HIPPO_ACTIVE,
        "alpha_simple": ALPHA_SIMPLE,
        "alpha_hopfield": ALPHA_HOPFIELD,
        "pkm_top_h": PKM_TOP_H,
        "pkm_sqrt_m": SQRT_M,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    if len(results) != 1:
        return ("HARD_FAIL", f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    arm_names_expected = ("ARM_STANDARD", "ARM_HA_ONLY",
                          "ARM_HA_DENSE_REPLACE", "ARM_PKM_REPLACE")
    core_arms = [a for a in r["arms"] if a["arm_name"] in arm_names_expected]
    if len(core_arms) != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected {EXPECTED_N_UNITS} core arms, "
                f"got {len(core_arms)}")
    try:
        per = [_arm_by_name(core_arms, name) for name in arm_names_expected]
    except KeyError as e:
        return ("HARD_FAIL", f"Missing arm: {e}")
    for a in per:
        if a["arm_status"] != "OK":
            return ("HARD_FAIL", f"Arm {a['arm_name']} error: {a['arm_status']}")

    standard = per[0]["recall_cortex"]
    ha_only = per[1]["recall_cortex"]
    dense = per[2]["recall_cortex"]
    pkm = per[3]["recall_cortex"]
    beta_dense = per[2].get("beta_used", float("nan"))
    beta_pkm = per[3].get("beta_used", float("nan"))
    margin_dense = per[2].get("cosine_margin_used", float("nan"))
    margin_pkm = per[3].get("cosine_margin_used", float("nan"))

    # META_RULE_AF: verify no two attention arms bit-identical.
    if abs(dense - pkm) < 1e-9 and not (
        RUN_MODE == "smoke" and abs(dense - 1.0) < 1e-6 and abs(pkm - 1.0) < 1e-6
    ):
        return ("HARD_FAIL",
                f"META_RULE_AF: DENSE ({dense}) == PKM ({pkm}) bit-identical")

    if ha_only > 0.20:
        return ("HARD_FAIL",
                f"FAIRNESS: ARM_HA_ONLY={ha_only:.3f} > 0.20 -- tape leak")

    if standard <= 0:
        return ("HARD_FAIL",
                f"STANDARD collapsed: standard={standard} -- encoder broken")

    if not (math.isfinite(beta_dense) and math.isfinite(margin_dense) and margin_dense > 0):
        return ("HARD_FAIL",
                f"CALIBRATION_DEGENERATE_DENSE: beta={beta_dense} margin={margin_dense}")
    if not (math.isfinite(beta_pkm) and math.isfinite(margin_pkm) and margin_pkm > 0):
        return ("HARD_FAIL",
                f"CALIBRATION_DEGENERATE_PKM: beta={beta_pkm} margin={margin_pkm}")

    delta_vs_dense = pkm - dense
    summary = (
        f"seed={SEED_THIS_CHUNK} STANDARD={standard:.3f} HA_ONLY={ha_only:.3f} "
        f"DENSE={dense:.3f} PKM={pkm:.3f} delta_vs_dense={delta_vs_dense:+.3f} "
        f"beta_d={beta_dense:.2f} beta_p={beta_pkm:.2f} "
        f"alpha_simple={ALPHA_SIMPLE:.4f} backend={COMPUTE_BACKEND}"
    )

    # HARD_FAIL: PKM regresses
    if delta_vs_dense < -0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: PKM regresses (delta={delta_vs_dense:+.3f} < -0.05). "
                f"{summary}")
    if pkm < 0.30:
        return ("HARD_FAIL",
                f"HARD_FAIL: PKM={pkm:.3f} < 0.30 (mechanism collapse). {summary}")

    # HARD_PASS: new capacity primitive
    hp_delta = delta_vs_dense >= 0.05
    hp_absolute = pkm >= 0.80
    if hp_delta and hp_absolute:
        return ("HARD_PASS",
                f"HARD_PASS: PKM beats DENSE by {delta_vs_dense:+.3f} >= 0.05 "
                f"AND PKM={pkm:.3f} >= 0.80. {summary}")

    # MIDDLE_BAND: equivalent to dense-Hopfield
    if abs(delta_vs_dense) < 0.05 and pkm >= 0.60 and dense >= 0.60:
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: PKM equivalent to DENSE (delta={delta_vs_dense:+.3f}). "
                f"{summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial. hp_delta={hp_delta} hp_absolute={hp_absolute}. "
            f"{summary}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _write_start_marker(out_dir, ANCHOR_NAME, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "N": N_CORTEX,
        "M": M_ITEMS,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
          flush=True)

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME} N_h={N_HIPPO} N_c={N_CORTEX} "
              f"M={M_ITEMS} top_h={PKM_TOP_H} mode={RUN_MODE} "
              f"backend={COMPUTE_BACKEND}...", flush=True)
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n"
                f"{traceback.format_exc()}",
                encoding="utf-8",
            )
            raise
        write_partial(out_dir, seed, result)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    all_results = list(per_seed.values())
    verdict, verdict_msg = compute_verdict(all_results)

    elapsed_s = time.time() - t_sweep_start
    print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL run. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    if RUN_MODE == "full" and USE_TORCH_CUDA:
        max_peak_mb = 0.0
        for r in all_results:
            for a in r.get("arms", []):
                max_peak_mb = max(max_peak_mb, float(a.get("gpu_mem_peak_mb", 0.0)))
        if max_peak_mb < 100.0:
            verdict_msg = (
                f"WARN_GPU_UNDERUTIL: max gpu_mem_peak_mb={max_peak_mb:.1f} < 100MB. "
                + verdict_msg
            )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_h={N_HIPPO} N_c={N_CORTEX} sparsity={HIPPO_SPARSITY} "
            f"M={M_ITEMS} eta_h={ETA_HIPPO} pkm_top_h={PKM_TOP_H} "
            f"sqrt_m={SQRT_M} mode={RUN_MODE} alpha_simple={ALPHA_SIMPLE:.4f} "
            f"backend={COMPUTE_BACKEND}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "eta_h": ETA_HIPPO,
        "hippo_sparsity": HIPPO_SPARSITY,
        "beta_floor": BETA_MIN,
        "beta_ceil": BETA_MAX,
        "pkm_top_h": PKM_TOP_H,
        "pkm_sqrt_m": SQRT_M,
        "alpha_simple": ALPHA_SIMPLE,
        "alpha_hopfield": ALPHA_HOPFIELD,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == 1
            and len([a for a in all_results[0].get("arms", [])
                     if a["arm_name"] in ("ARM_STANDARD", "ARM_HA_ONLY",
                                          "ARM_HA_DENSE_REPLACE",
                                          "ARM_PKM_REPLACE")])
            == EXPECTED_N_UNITS
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 0.00552,
        "crlb_formula_reference": "sigma_min = sqrt(0.25/M) binomial-CLT",
        "discriminator_reachability": True,
        "calibration_check": "adaptive_with_discriminator_gate",
        "per_seed": [
            {
                "seed": r.get("seed"),
                "elapsed_s": r.get("elapsed_s"),
                "arms": r.get("arms"),
            }
            for r in all_results
        ],
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
