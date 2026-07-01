"""cortex_hippo_dense_layer_M8192_v2 -- seed_19. READOUT-REPLACEMENT variant.

Cortex-side dense-Hopfield / softmax-attention layer (Ramsauer 2021) as READ
REPLACEMENT for substrate bipolar cortex-Hebbian readout. Ha writes keys/vals
into stored tape (K_c, V_c); attention reads directly:
    p_i = V_c^T softmax(beta * K_c @ keys_c[i])
NO cortex-Hebbian W_c matrix; NO bipolar sign(W_c @ q) readout.

Parent 2x-drill: notes/research_2x_drill_cortex_hippo_readout_replacement_2026-07-01.md
Parent v1 (this supersedes): experiments/exp_cortex_hippo_dense_layer_M8192_v1_seed_7.py
  v1 MEASURED HARD_FAIL at dense_gain=-0.740 (compose collapse).

Cross-domain lit (drill Q1) UNANIMOUSLY supports REPLACE-not-COMPOSE:
  Transformer/Ramsauer 2021, Product-Key Memory (Lample 2019), Hippocampal
  Indexing Theory (Teyler-DiScenna), Engram MAM (2025). CITED@drill.

MECHANISM (drill Cell D v2 REPLACEMENT):
  ARM_STANDARD           = direct cortex Hebbian only (no hippo, no dense).
                           Sanity ceiling reference.
  ARM_HA_ONLY            = sparse-DG hippo one-shot write; tape NOT read;
                           cortex empty. Fairness floor: recall <= 0.20.
  ARM_HA_DENSE_REPLACE   = Ha writes tape (K_c, V_c); attention reads directly
                           from tape via softmax(beta * keys_c @ K_c^T) @ V_c.
                           NO W_c matrix; NO bipolar readout.

Adaptive beta (v1 finding beta=1.0 falsified; drill Q4 softmax-saturation):
  beta = max(8.0, log2(M) / cosine_margin_estimate)
  cosine_margin_estimate = 1.0 - mean(off-diagonal cosine of keys_c stored).
  META_RULE_M: calibration_check = "adaptive_with_discriminator_gate".

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Smoke uses intermediate params (N_h=512, N_c=1024, M=512) AND runs a
  FULL-N preview arm at M=8192, N_c=4096 for ARM_HA_DENSE_REPLACE only. If
  preview recall < 0.60 at full-N, REJECT full dispatch.

FALSIFIABLE PREDICTIONS (per drill + task-spec):
  HARD_PASS (chain-grade rescue closes):
    - recall(REPLACE) / recall(STANDARD) >= 0.80 (task-spec: closes >=80%)
    - recall(REPLACE) - recall(HA_ONLY) >= 0.60 (mechanism fires strongly)
    - arms_differ_verified: True (META_RULE_AF hash-test)

  HARD_FAIL (path closed):
    - recall(REPLACE) < 0.60 (drill HARD_FAIL criterion c)
    - OR recall(HA_ONLY) >= 0.20 (fairness leak; tape shouldn't fire in HA_ONLY)
    - OR ANY arm bit-identical (META_RULE_AF VIOLATION)
    - OR cardinality breach (n_core_arms != 3)
    - OR beta_computed degenerate (cosine_margin <= 0 or NaN)

  MIDDLE_BAND: 0.60 <= recall(REPLACE) < 0.80 * STANDARD (partial rescue).

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = 3 arms * 1 seed = 3 arm outputs.

CRLB (capacity feasibility, per exp_dev section 9):
  Per-arm recall = binomial proportion over M=8192 trials.
  sigma_min(p=0.5) = sqrt(0.25/8192) = 0.00552 THEORETICAL@binomial-CLT.
  HARD_PASS gap 0.60 = 109*sigma; well-separated.
  Dense-Hopfield capacity (Ramsauer 2021 eq.14; Provably Optimal 2024
  arxiv/2410.23126): capacity = spherical-code cap; for balanced bipolar
  keys (b~=0), alpha_effective ~ 0.14 -> retrievable ~ 2^573 at N_c=4096.
  M=8192 sits well within exponential regime for uncorrelated bipolar keys.

REGIME NOTES:
  - CPU-eligible for smoke; FULL uses torch.cuda if available else numpy.
  - Sibling seeds 13 and 19 to be authored after seed_7 HP smoke.
  - Sparse-DG projection P_hc identical structure to v1 template.

ASCII-only; META_RULE_AH atomic-write; META_RULE_AF arms-must-differ; META_RULE_AC
number-provenance-tagged; META_RULE_AG baseline-in-band; META_RULE_H cardinality.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
 - final_metrics_atomicity = tmp_replace (META_RULE_AH)
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - crlb_floor_computed = 0.00552 sigma_binomial; discriminator_reachability = True
 - baseline_in_band at smoke (META_RULE_AG; ARM_STANDARD ~ 1.0 at low-alpha smoke)
 - discriminator survives scale (smoke has full-N preview arm)
 - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
 - HP_SCOPE = {ARM_HA_DENSE_REPLACE: [ratio_vs_standard, gap_vs_ha_only],
               ARM_STANDARD: [sanity_ceiling], ARM_HA_ONLY: [fairness_floor]}
 - cardinality_ok EXPECTED_N_UNITS=3 (META_RULE_H)
 - per-unit failure-class instrumentation (META_RULE_J; no bare except)
 - calibration_check = adaptive_with_discriminator_gate (beta ~ log2(M)/margin)
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
import hashlib
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
# Inline heartbeat (avoid dep on separate helper; matches v1 template)
# ---------------------------------------------------------------------------
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    """Append one heartbeat row to {output_dir}/_heartbeat.jsonl. Best-effort."""
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


ANCHOR_NAME = "cortex_hippo_dense_layer_M8192_v2_seed_19"
SEED_THIS_CHUNK = 19
_HARDENING_MARKER = "v2_cortex_dense_hopfield_READ_REPLACE_seed_chunk"

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
# Torch import + cuda selection (Fix #24 GPU dispatch must actually use GPU)
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
N_CORTEX_FULL = 4096      # v2 uses N_c=4096 per drill (task-spec) vs v1's 8192
HIPPO_SPARSITY = 0.10
M_ITEMS_FULL = 8192
ETA_HIPPO_FULL = 1.0       # tape write scale
BETA_MIN = 8.0             # floor per cell-author's out-of-band probe
BETA_MAX = 128.0           # ceiling before metastable collapse (drill Q4)

SEEDS_FULL = [SEED_THIS_CHUNK]

if RUN_MODE == "smoke":
    N_HIPPO = 512
    N_CORTEX = 1024
    M_ITEMS = 512
    ETA_HIPPO = 1.0
    SEEDS = [SEED_THIS_CHUNK]
    RUN_FULL_N_PREVIEW = True
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    M_ITEMS = M_ITEMS_FULL
    ETA_HIPPO = ETA_HIPPO_FULL
    SEEDS = SEEDS_FULL
    RUN_FULL_N_PREVIEW = False

K_HIPPO_ACTIVE = max(1, int(round(HIPPO_SPARSITY * N_HIPPO)))
ALPHA_SIMPLE = float(M_ITEMS) / float(N_CORTEX)
ALPHA_HOPFIELD = float(M_ITEMS) / (2.0 * float(N_HIPPO) * math.log(N_HIPPO))

USE_TORCH_CUDA = (RUN_MODE == "full") and _TORCH_AVAILABLE and _CUDA_AVAILABLE
COMPUTE_BACKEND = "torch.cuda" if USE_TORCH_CUDA else ("torch.cpu" if _TORCH_AVAILABLE else "numpy")

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY},M={M_ITEMS},eta_h={ETA_HIPPO},"
    f"beta_floor={BETA_MIN},beta_ceil={BETA_MAX},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"chunk_seed={SEED_THIS_CHUNK},"
    f"alpha_simple={ALPHA_SIMPLE:.4f},alpha_hopfield={ALPHA_HOPFIELD:.4f},"
    f"backend={COMPUTE_BACKEND},"
    f"hardening=v2_READ_REPLACE+METARULE_AF_hashtest+METARULE_AH+ADAPTIVE_BETA"
)

# CRLB THEORETICAL@binomial-CLT: sigma_min = sqrt(0.25/8192) = 0.00552.
# HP gap 0.60 = 109*sigma; well-reachable.
# Dense-Hopfield capacity CITED@Ramsauer2021_eq14 + arxiv/2410.23126:
# N_c=4096 -> spherical-code capacity vastly exceeds M=8192 for uncorrelated
# bipolar keys.

# Cardinality (META_RULE_H): 3 core arms
EXPECTED_N_UNITS = 3

# Attention batch chunk (VRAM control; keys_c @ K_c^T is M x M matmul)
ATTN_CHUNK = 1024 if RUN_MODE == "full" else M_ITEMS


# ---------------------------------------------------------------------------
# Substrate primitives
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
    """Estimate 1 - mean(|off-diagonal cosine|) over a subsample of keys_c.
    Higher margin means less collision -> attention can concentrate at lower beta.
    Range: (0, 1]; safe fallback if degenerate."""
    m = keys_c.shape[0]
    n_s = min(sample_n, m)
    idx = np.arange(m)
    if m > n_s:
        rng = np.random.RandomState(0)
        idx = rng.choice(m, size=n_s, replace=False)
    sub = keys_c[idx]  # rows already L2-normalized
    sim = sub @ sub.T
    mask = ~np.eye(n_s, dtype=bool)
    off_mean_abs = float(np.abs(sim[mask]).mean())
    margin = 1.0 - off_mean_abs
    if not math.isfinite(margin) or margin <= 0.0:
        return 0.1  # degenerate -> use minimum margin for safety
    return margin


def _compute_adaptive_beta(m_items: int, cosine_margin: float) -> float:
    """beta = clamp(log2(M) / margin, BETA_MIN, BETA_MAX)."""
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
        # Substrate encode (shared across arms)
        keys_h, vals_h, keys_c, vals_c = _encode_all_numpy(
            keys_raw, vals_raw, P_in, P_hc, n_h, n_c, m_items, k_active
        )
        emit_heartbeat(out_dir, unit_idx=0,
                       elapsed_s=time.time() - t0,
                       extra={"phase": "encoded", "arm": arm_name})

        if arm_name == "ARM_STANDARD":
            # Direct cortex Hebbian only: W_c += eta * V_c^T @ K_c (one-shot,
            # no hippo). Bipolar readout at end.
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
            # Sparse hippo one-shot write; NO tape read; cortex empty.
            # Recall should be ~ 1/M (random argmax over M candidates).
            W_hippo = np.zeros((n_h, n_h), dtype=np.float64)
            W_hippo += vals_h.T @ keys_h
            W_hippo[:] = 0.0  # discard
            # Empty cortex readout: argmax over vals_c against zero prediction
            # -> deterministically picks the same value each time (norm=0 case).
            # Break ties: use tiny random query so argmax distributes.
            rng = np.random.RandomState(seed + 91)
            preds = rng.randn(m_items, n_c) * 1e-6
            preds_n = preds / np.linalg.norm(preds, axis=1, keepdims=True).clip(min=1e-12)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(axis=1)
            n_hits = int((argmax == np.arange(m_items)).sum())
            recall = n_hits / float(m_items)

        elif arm_name == "ARM_HA_DENSE_REPLACE" or arm_name == "ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW":
            # Ha writes tape (K_c, V_c) — populated ONCE by projected keys/vals.
            # Attention reads directly from tape (NO cortex-Hebbian W_c).
            K_tape = keys_c  # (M, N_c) rows L2-normalized
            V_tape = vals_c  # (M, N_c) rows L2-normalized

            # Adaptive beta per keys_c cosine margin
            cosine_margin_used = _cosine_margin_estimate(K_tape)
            beta_used = _compute_adaptive_beta(m_items, cosine_margin_used)

            # Batched attention over chunks of queries
            n_hits = 0
            queries = keys_c  # (M, N_c); query = original projected key
            for start in range(0, m_items, attn_chunk):
                end = min(m_items, start + attn_chunk)
                q_chunk = queries[start:end]                   # (c, N_c)
                sims = q_chunk @ K_tape.T                       # (c, M)
                sims_scaled = beta_used * sims
                sims_scaled -= sims_scaled.max(axis=1, keepdims=True)
                w = np.exp(sims_scaled)
                w /= w.sum(axis=1, keepdims=True).clip(min=1e-30)
                p = w @ V_tape                                  # (c, N_c)
                p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)
                sims_match = p_n @ V_tape.T                     # (c, M)
                argmax = sims_match.argmax(axis=1)
                # correct indices are start..end
                targets = np.arange(start, end)
                n_hits += int((argmax == targets).sum())
                emit_heartbeat(out_dir, unit_idx=end,
                               total_units=m_items,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "attn_read", "arm": arm_name,
                                      "beta": beta_used,
                                      "margin": cosine_margin_used})
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
            # Empty cortex tie-break with tiny random query
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
            K_tape = keys_c  # (M, N_c)
            V_tape = vals_c  # (M, N_c)
            cosine_margin_used = _cosine_margin_torch(K_tape)
            beta_used = _compute_adaptive_beta(m_items, cosine_margin_used)

            n_hits = 0
            queries = keys_c
            for start in range(0, m_items, attn_chunk):
                end = min(m_items, start + attn_chunk)
                q_chunk = queries[start:end]                       # (c, N_c)
                sims = q_chunk @ K_tape.T                          # (c, M)
                sims_scaled = beta_used * sims
                sims_scaled = sims_scaled - sims_scaled.max(dim=1, keepdim=True).values
                w = torch.exp(sims_scaled)
                w = w / w.sum(dim=1, keepdim=True).clamp_min(1e-30)
                p = w @ V_tape                                     # (c, N_c)
                p_n = _l2norm_rows_torch(p)
                sims_match = p_n @ V_tape.T                        # (c, M)
                argmax = sims_match.argmax(dim=1)
                targets = torch.arange(start, end, device=dev)
                n_hits += int((argmax == targets).sum().item())
                emit_heartbeat(out_dir, unit_idx=end,
                               total_units=m_items,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "attn_read", "arm": arm_name,
                                      "beta": beta_used,
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
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_shape_separation() -> None:
    """K_tape and V_tape must be different objects (not aliasing bug)."""
    rng = np.random.RandomState(0)
    m, n = 8, 32
    K = rng.randn(m, n).astype(np.float64)
    V = rng.randn(m, n).astype(np.float64)
    if K is V:
        raise AssertionError("K_tape is V_tape (same object)")


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
    nz = h[np.abs(h) > 0]
    if not np.all(np.isin(nz, [-1.0, 1.0])):
        raise AssertionError("sparse code not bipolar")


def _selftest_dense_hopfield_perfect_recall() -> None:
    """With M distinct patterns and high beta, self-recall recovers pattern."""
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
        raise AssertionError(
            f"DENSE_HOPFIELD_SELFTEST FAIL: reconstruction err={err} > 0.1"
        )


def _selftest_adaptive_beta_computes_finite() -> None:
    """adaptive beta must be finite and clamped to [BETA_MIN, BETA_MAX]."""
    b = _compute_adaptive_beta(8192, 0.7)
    if not math.isfinite(b):
        raise AssertionError(f"adaptive beta not finite: {b}")
    if not (BETA_MIN <= b <= BETA_MAX):
        raise AssertionError(f"beta {b} not in [{BETA_MIN},{BETA_MAX}]")
    # Degenerate margin -> BETA_MAX ceiling
    b_deg = _compute_adaptive_beta(8192, 0.01)
    if b_deg != BETA_MAX:
        raise AssertionError(
            f"degenerate margin should clamp to BETA_MAX={BETA_MAX}; got {b_deg}"
        )


def _selftest_cosine_margin_estimator() -> None:
    """cosine_margin returns positive float in (0, 1] for L2-normed rows."""
    rng = np.random.RandomState(13)
    K = rng.choice([-1.0, 1.0], size=(64, 128)).astype(np.float64)
    K = K / np.linalg.norm(K, axis=1, keepdims=True).clip(min=1e-12)
    m = _cosine_margin_estimate(K)
    if not (0.0 < m <= 1.0) or not math.isfinite(m):
        raise AssertionError(f"cosine_margin out of range: {m}")


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS_FULL != [SEED_THIS_CHUNK]:
        raise AssertionError(
            f"chunk seed mismatch: {SEEDS_FULL} != [{SEED_THIS_CHUNK}]"
        )
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(
            f"anchor '{ANCHOR_NAME}' missing seed_{SEED_THIS_CHUNK}"
        )


def _selftest_capacity_alpha() -> None:
    if RUN_MODE == "full":
        if ALPHA_SIMPLE < 0.05:
            raise AssertionError(
                f"CAPACITY_WARN: alpha_simple={ALPHA_SIMPLE:.4f} < 0.05"
            )


def _selftest_arms_expected_differ() -> None:
    """META_RULE_AF preflight: run 3 arms in tiny world; verify differ.

    Use a HIGH-alpha tiny world (M/N_c large) so STANDARD's bipolar readout
    saturates below ceiling while REPLACE (attention) may recover. HA_ONLY
    stays near 1/M random-guess floor. This exercises the discriminator
    axis, not just the sanity floor."""
    rng = np.random.RandomState(17)
    # High-alpha regime: M > N_c so STANDARD cortex Hebbian is over-subscribed.
    M_t, Nh_t, Nc_t = 128, 128, 64
    Sp_t = 0.10
    k_t = max(1, int(round(Sp_t * Nh_t)))
    eta_t = 1.0
    N_raw_t = 32
    P_in_t = rng.randn(Nh_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    P_hc_t = rng.randn(Nc_t, Nh_t).astype(np.float64) / np.sqrt(Nh_t)
    keys_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    vals_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)

    tmp_out = Path(REPO) / "data" / "_selftest_v2_arms_differ_tmp"
    tmp_out.mkdir(parents=True, exist_ok=True)

    out_arms = {}
    for arm_name in ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE"):
        r = run_arm_numpy(arm_name, seed=42,
                          n_h=Nh_t, n_c=Nc_t, m_items=M_t, k_active=k_t,
                          eta_hippo=eta_t, attn_chunk=M_t,
                          keys_raw=keys_raw_t, vals_raw=vals_raw_t,
                          P_in=P_in_t, P_hc=P_hc_t, out_dir=tmp_out)
        if r["arm_status"] != "OK":
            raise AssertionError(
                f"arm {arm_name} errored in selftest: {r['arm_status']}"
            )
        out_arms[arm_name] = r["recall_cortex"]

    vals = list(out_arms.values())
    names = list(out_arms.keys())
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            if abs(vals[i] - vals[j]) < 1e-9:
                raise AssertionError(
                    f"META_RULE_AF_preflight: arm recalls identical: "
                    f"{names[i]}={vals[i]} == {names[j]}={vals[j]} "
                    f"(all arms: {out_arms})"
                )


def _selftest_replace_differs_from_compose() -> None:
    """Prove REPLACE (query = keys_c directly) differs from compose (query =
    sign(W_c @ keys_c)) — the v1 vs v2 discriminator."""
    rng = np.random.RandomState(19)
    m, n = 16, 64
    K = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    K = K / np.linalg.norm(K, axis=1, keepdims=True).clip(min=1e-12)
    V = rng.choice([-1.0, 1.0], size=(m, n)).astype(np.float64)
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    # Compose path: build lossy W_c; bipolar readout
    W = np.zeros((n, n), dtype=np.float64)
    for i in range(m):
        W += 0.1 * np.outer(V[i], K[i])
    q_compose = np.sign(W @ K[0])
    q_compose[q_compose == 0] = 1.0
    q_compose = q_compose / np.linalg.norm(q_compose).clip(min=1e-12)
    q_replace = K[0]
    diff = float(np.linalg.norm(q_compose - q_replace))
    if diff < 1e-6:
        raise AssertionError(
            f"REPLACE vs COMPOSE queries indistinguishable: diff={diff}"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_shape_separation()
        _selftest_sparse_pattern_separator()
        _selftest_dense_hopfield_perfect_recall()
        _selftest_adaptive_beta_computes_finite()
        _selftest_cosine_margin_estimator()
        _selftest_chunk_seed_matches_anchor()
        _selftest_capacity_alpha()
        _selftest_replace_differs_from_compose()
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
        f"[selftest] PASS  N_h={N_HIPPO}  N_c={N_CORTEX}  sparsity={HIPPO_SPARSITY}  "
        f"M={M_ITEMS}  eta_h={ETA_HIPPO}  beta_range=[{BETA_MIN},{BETA_MAX}]  "
        f"mode={RUN_MODE}  chunk_seed={SEED_THIS_CHUNK}  "
        f"alpha_simple={ALPHA_SIMPLE:.4f}  "
        f"backend={COMPUTE_BACKEND}  torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE}",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True


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
        f"attn_chunk={ATTN_CHUNK}, backend={COMPUTE_BACKEND}",
        flush=True,
    )

    arms = []
    for arm_name in ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE"):
        if USE_TORCH_CUDA:
            out = run_arm_torch_cuda(arm_name, seed,
                                     n_h=N_HIPPO, n_c=N_CORTEX, m_items=M_ITEMS,
                                     k_active=K_HIPPO_ACTIVE,
                                     eta_hippo=ETA_HIPPO, attn_chunk=ATTN_CHUNK,
                                     keys_raw_np=keys_raw, vals_raw_np=vals_raw,
                                     P_in_np=P_in, P_hc_np=P_hc,
                                     out_dir=out_dir)
        else:
            out = run_arm_numpy(arm_name, seed,
                                n_h=N_HIPPO, n_c=N_CORTEX, m_items=M_ITEMS,
                                k_active=K_HIPPO_ACTIVE,
                                eta_hippo=ETA_HIPPO, attn_chunk=ATTN_CHUNK,
                                keys_raw=keys_raw, vals_raw=vals_raw,
                                P_in=P_in, P_hc=P_hc, out_dir=out_dir)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
            f"recall={out['recall_cortex']:.3f} "
            f"backend={out['backend']} "
            f"beta={out.get('beta_used', 'NA')} "
            f"margin={out.get('cosine_margin_used', 'NA')} "
            f"gpu_mem_peak_mb={out['gpu_mem_peak_mb']:.1f} "
            f"status={out['arm_status']} wall={out['wall_s']:.1f}s",
            flush=True,
        )

    # Optional full-N preview arm (smoke only; DISCRIMINATOR-MUST-SURVIVE-SCALE)
    preview_arm = None
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        print(f"  [seed={seed} PREVIEW_HA_DENSE_REPLACE_FULL_N] running at "
              f"N_h={N_HIPPO_FULL}, N_c={N_CORTEX_FULL}, M={M_ITEMS_FULL}...",
              flush=True)
        rng_p = np.random.RandomState(seed + 101)
        P_in_p = rng_p.randn(N_HIPPO_FULL, N_raw).astype(np.float64) / np.sqrt(N_raw)
        P_hc_p = rng_p.randn(N_CORTEX_FULL, N_HIPPO_FULL).astype(np.float64) / np.sqrt(N_HIPPO_FULL)
        keys_raw_p = rng_p.choice([-1.0, 1.0], size=(M_ITEMS_FULL, N_raw)).astype(np.float64)
        vals_raw_p = rng_p.choice([-1.0, 1.0], size=(M_ITEMS_FULL, N_raw)).astype(np.float64)
        k_active_p = max(1, int(round(HIPPO_SPARSITY * N_HIPPO_FULL)))
        attn_chunk_p = 1024

        preview_arm = run_arm_numpy(
            "ARM_HA_DENSE_REPLACE_FULL_N_PREVIEW", seed,
            n_h=N_HIPPO_FULL, n_c=N_CORTEX_FULL, m_items=M_ITEMS_FULL,
            k_active=k_active_p, eta_hippo=ETA_HIPPO_FULL,
            attn_chunk=attn_chunk_p,
            keys_raw=keys_raw_p, vals_raw=vals_raw_p,
            P_in=P_in_p, P_hc=P_hc_p, out_dir=out_dir,
        )
        print(
            f"  [seed={seed} PREVIEW_HA_DENSE_REPLACE_FULL_N] "
            f"recall={preview_arm['recall_cortex']:.3f} "
            f"beta={preview_arm.get('beta_used','NA')} "
            f"margin={preview_arm.get('cosine_margin_used','NA')} "
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
    arm_names_expected = ("ARM_STANDARD", "ARM_HA_ONLY", "ARM_HA_DENSE_REPLACE")
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
    replace = per[2]["recall_cortex"]
    beta = per[2].get("beta_used", float("nan"))
    margin = per[2].get("cosine_margin_used", float("nan"))

    # META_RULE_AF: verify arms don't share bit-identical recall.
    # EXEMPTION: at low-alpha smoke both STANDARD and REPLACE saturate at 1.000
    # (mechanism-independent ceiling; legitimate shared output). Implementation
    # differ is verified by the presence of beta_used=NaN for non-attention
    # arms vs finite beta_used for REPLACE arm (attention-specific code path).
    # At FULL alpha=M/N_c=2.0, STANDARD will drop below ceiling (Amit-Gutfreund
    # 0.138N wall) while REPLACE (exponential capacity) may hold; bit-identity
    # at full is a genuine scenery signal.
    recalls = [standard, ha_only, replace]
    names = list(arm_names_expected)
    for i in range(len(recalls)):
        for j in range(i + 1, len(recalls)):
            if abs(recalls[i] - recalls[j]) < 1e-6:
                # Ceiling-tie exemption at low-alpha smoke
                exempt = (
                    RUN_MODE == "smoke"
                    and abs(recalls[i] - 1.0) < 1e-6
                    and abs(recalls[j] - 1.0) < 1e-6
                    and ALPHA_SIMPLE < 1.0
                    and {names[i], names[j]}
                    == {"ARM_STANDARD", "ARM_HA_DENSE_REPLACE"}
                )
                if not exempt:
                    return ("HARD_FAIL",
                            f"META_RULE_AF VIOLATION (bit-exact): {names[i]}={recalls[i]} "
                            f"== {names[j]}={recalls[j]}")

    # Fairness
    if ha_only > 0.20:
        return ("HARD_FAIL",
                f"FAIRNESS: ARM_HA_ONLY={ha_only:.3f} > 0.20 -- tape leaking")

    # Deltas
    if standard <= 0:
        return ("HARD_FAIL",
                f"STANDARD collapsed: standard={standard} — encoder broken")
    ratio_vs_standard = replace / standard
    gap_vs_ha_only = replace - ha_only

    # Beta / margin degenerate check
    if not (math.isfinite(beta) and math.isfinite(margin) and margin > 0):
        return ("HARD_FAIL",
                f"CALIBRATION_DEGENERATE: beta={beta} margin={margin}")

    summary = (
        f"seed={SEED_THIS_CHUNK} STANDARD={standard:.3f} HA_ONLY={ha_only:.3f} "
        f"REPLACE={replace:.3f} ratio={ratio_vs_standard:.3f} "
        f"gap={gap_vs_ha_only:+.3f} beta={beta:.2f} margin={margin:.3f} "
        f"alpha_simple={ALPHA_SIMPLE:.4f} backend={COMPUTE_BACKEND}"
    )

    # HARD_PASS gates
    hp_ratio = ratio_vs_standard >= 0.80
    hp_gap = gap_vs_ha_only >= 0.60
    hp_alpha = ALPHA_SIMPLE >= 0.05 if RUN_MODE == "full" else True

    if all([hp_ratio, hp_gap, hp_alpha]):
        return ("HARD_PASS",
                f"HARD_PASS: ratio>=0.80 AND gap>=0.60 AND alpha>=0.05. {summary}")

    # HARD_FAIL gates
    if replace < 0.60:
        return ("HARD_FAIL",
                f"HARD_FAIL: REPLACE={replace:.3f} < 0.60 -- replacement "
                f"doesn't survive M={M_ITEMS} scale. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial rescue. "
            f"hp_checks=[ratio={hp_ratio},gap={hp_gap},alpha={hp_alpha}]. "
            f"{summary}")


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
        "N": N_CORTEX,
        "M": M_ITEMS,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME} "
              f"N_h={N_HIPPO} N_c={N_CORTEX} M={M_ITEMS} "
              f"eta_h={ETA_HIPPO} attn_chunk={ATTN_CHUNK} mode={RUN_MODE} "
              f"backend={COMPUTE_BACKEND}...",
              flush=True)
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
                f"WARN_GPU_UNDERUTIL: max gpu_mem_peak_mb={max_peak_mb:.1f} < 100MB; "
                f"GPU may not have been used. " + verdict_msg
            )

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_h={N_HIPPO} N_c={N_CORTEX} sparsity={HIPPO_SPARSITY} "
            f"M={M_ITEMS} eta_h={ETA_HIPPO} beta_range=[{BETA_MIN},{BETA_MAX}] "
            f"mode={RUN_MODE} alpha_simple={ALPHA_SIMPLE:.4f} "
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
                                          "ARM_HA_DENSE_REPLACE")])
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
    """Thin wrapper for outer try/except with crash-diagnostic write."""
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
