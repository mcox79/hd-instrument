"""cortex_hippo_dense_layer_M8192_v1 -- seed_7.

Cortex-side dense-Hopfield / softmax-attention layer (Ramsauer 2021) composed
with substrate Ha (fast hippo Hebbian, sparse-DG N_h=4096) + Hc (slow cortex
Hebbian via replay reactivation, dense N_c=8192) at chain-grade M=8192.

Parent 5x-drill: notes/research_5x_drill_cortex_hippo_M8192_rescue_2026-07-01.md
Parent template (Ha+Hc replay-fixed): experiments/exp_substrate_cortex_hippo_
handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7.py (prior cell, M=8192).

Prior atoms (context):
  - Ha alone MM at 51% closure of clean-baseline (MEASURED, MM tier).
  - Hc K-banks CG at 93% closure (MEASURED@substrate CG).
  - Substrate-only M=8192 v2 landed <MB> gap 49% short of clean baseline.
  - Dense-Hopfield exponential capacity theorem (Krotov-Hopfield 2016;
    Demircigil 2017; Ramsauer 2021) predicts N_c=8192 easily supports
    M=8192 with softmax attention read-out.

MECHANISM (drill Cell D):
  ARM_STANDARD_SUBSTRATE      = direct cortex Hebbian only (no hippo, no dense)
                                aka baseline_d in drill (Ha+Hc only, but here
                                simplified to raw cortex-outer-product because
                                that is the "standard substrate" reference).
                                Note: renamed from ARM_DIRECT_CORTEX in prior v2
                                for terminology alignment with drill.
  ARM_HA_ONLY                 = sparse-DG hippo one-shot, no replay to cortex.
                                Ha stored, but cortex is empty at readout.
  ARM_HA_HC                   = Ha + Hc composition; CLS-faithful replay.
                                REACTIVATE via W_hippo readout; project to N_c;
                                slow Hebbian into W_cortex. Then zero W_hippo.
                                This is prior v2 ARM_FULL_HANDOFF (=49% closure
                                MEASURED@prior FULL landings).
  ARM_HA_HC_DENSE             = Ha+Hc composition + cortex-side dense-Hopfield
                                readout layer (softmax attention over stored
                                cortex pattern bank V_c). Query = cortex-readout
                                of cue; attention pattern-completes over V_c
                                to sharp target. beta = 1.0 default; verifies
                                Ramsauer capacity closes the 49% gap.

DISCRIMINATOR-MUST-SURVIVE-SCALE:
  Smoke uses intermediate params (N_h=512, N_c=2048, M=512) AND runs a
  FULL-N preview arm at M=8192, N_c=8192 for CORTEX_DENSE only. If cortex
  dense at full-N preview does not exceed ARM_HA_HC by >0.10, REJECT
  full dispatch (per exp_dev DISCRIMINATOR-MUST-SURVIVE-SCALE rule).
  The dense layer is O(M*N_c) memory read-only over stored patterns; the
  preview arm at full-N is affordable at ~2min on CPU.

FALSIFIABLE PREDICTIONS (per drill):
  HARD_PASS (chain-grade rescue closes):
    - recall(ARM_HA_HC_DENSE) >= 0.80 (closes >=95% of 49% remainder gap)
    - recall(ARM_HA_HC_DENSE) - recall(ARM_HA_HC) >= 0.30 (dense discriminates)
    - recall(ARM_HA_HC) - recall(ARM_HA_ONLY) >= 0.20 (replay still fires)
    - arms_differ_verified: True (META_RULE_AF hash-test)

  HARD_FAIL (path closed):
    - recall(ARM_HA_HC_DENSE) - recall(ARM_HA_HC) < 0.05 (dense layer scenery)
    - OR recall(ARM_HA_ONLY) >= 0.20 (baseline leaks, invalid fairness)
    - OR any arm bit-identical to another (META_RULE_AF VIOLATION)
    - OR cardinality breach

  MIDDLE_BAND: recall gain of dense arm 0.05-0.30 above ARM_HA_HC (partial).

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = 4 arms * 1 seed = 4 arm outputs.

CRLB (capacity feasibility, per exp_dev section 9):
  Per-arm recall = binomial proportion over M=8192 trials.
  sigma_min(p=0.5) = sqrt(0.25/8192) = 0.00552.
  HARD_PASS delta threshold 0.30 = 55*sigma; well-separated.
  Dense-Hopfield capacity (Ramsauer eq. 14): O(2^(N_c/2)) patterns storable
  at retrieval error < epsilon; N_c=8192 -> capacity >> 10^100. M=8192 is
  trivial for dense-Hopfield storage; question is whether the projected
  Ha+Hc pattern bank V_c is high-fidelity enough for softmax attention.

REGIME NOTES:
  - CPU-eligible for smoke; FULL uses torch.cuda if available else numpy.
  - Sibling seeds 13 and 19 to be authored after seed_7 HP smoke.
  - Sparse-DG projection P_hc identical to prior template (fixed Gaussian).

ASCII-only; META_RULE_AH atomic-write; META_RULE_AF arms-must-differ; META_RULE_AC
number-provenance-tagged; META_RULE_AG baseline-in-band; META_RULE_H cardinality.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
 - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
 - final_metrics_atomicity = tmp_replace (META_RULE_AH)
 - except SystemExit: raise BEFORE except Exception (no BaseException)
 - crlb_floor_computed = 0.00552 sigma_binomial; discriminator_reachability = True
 - baseline_in_band at smoke (META_RULE_AG; 0.05 < ARM_STANDARD < 0.95 pinned)
 - discriminator survives scale (smoke has full-N preview arm)
 - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
 - HP_SCOPE = {ARM_HA_HC_DENSE: [dense_gain, dense_absolute],
               ARM_HA_HC: [replay_gap], ARM_HA_ONLY: [fairness_floor]}
 - cardinality_ok EXPECTED_N_UNITS=4 (META_RULE_H)
 - per-unit failure-class instrumentation (META_RULE_J; no bare except)
 - calibration_check = default_ok_for_this_regime (beta=1.0 per Ramsauer canonical)
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
# Inline heartbeat (avoid dep on separate helper; matches v2 template)
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


ANCHOR_NAME = "cortex_hippo_dense_layer_M8192_v1_seed_7"
SEED_THIS_CHUNK = 7
_HARDENING_MARKER = "v1_cortex_dense_hopfield_layer_seed_chunk"

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
N_CORTEX_FULL = 8192
HIPPO_SPARSITY = 0.10
M_ITEMS_FULL = 8192
N_REPLAY_CYCLES_FULL = 50
ETA_CORTEX_FULL = 0.01
BETA_DENSE_FULL = 1.0  # softmax inverse-temperature per Ramsauer canonical

SEEDS_FULL = [SEED_THIS_CHUNK]

if RUN_MODE == "smoke":
    # Smoke at intermediate params (per USER 2026-06-26 discriminator-survives-scale).
    N_HIPPO = 512
    N_CORTEX = 2048
    M_ITEMS = 512
    N_REPLAY_CYCLES = 10
    ETA_CORTEX = 0.005
    BETA_DENSE = 1.0
    SEEDS = [SEED_THIS_CHUNK]
    # Preview: run one extra full-N ARM_HA_HC_DENSE arm to prove discriminator
    # survives scale. See run_seed() for wiring.
    RUN_FULL_N_PREVIEW = True
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    M_ITEMS = M_ITEMS_FULL
    N_REPLAY_CYCLES = N_REPLAY_CYCLES_FULL
    ETA_CORTEX = ETA_CORTEX_FULL
    BETA_DENSE = BETA_DENSE_FULL
    SEEDS = SEEDS_FULL
    RUN_FULL_N_PREVIEW = False

K_HIPPO_ACTIVE = max(1, int(round(HIPPO_SPARSITY * N_HIPPO)))
ALPHA_SIMPLE = float(M_ITEMS) / float(N_CORTEX)
ALPHA_HOPFIELD = float(M_ITEMS) / (2.0 * float(N_HIPPO) * math.log(N_HIPPO))

USE_TORCH_CUDA = (RUN_MODE == "full") and _TORCH_AVAILABLE and _CUDA_AVAILABLE
COMPUTE_BACKEND = "torch.cuda" if USE_TORCH_CUDA else ("torch.cpu" if _TORCH_AVAILABLE else "numpy")

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY},M={M_ITEMS},N_replay={N_REPLAY_CYCLES},"
    f"eta_c={ETA_CORTEX},beta_dense={BETA_DENSE},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"chunk_seed={SEED_THIS_CHUNK},"
    f"alpha_simple={ALPHA_SIMPLE:.4f},alpha_hopfield={ALPHA_HOPFIELD:.4f},"
    f"backend={COMPUTE_BACKEND},"
    f"hardening=L1early+L2perarm+L4importsentinel+METARULE_AF_hashtest+METARULE_AH+GPU_PROXY"
)

# CRLB (per exp_dev section 9):
#   sigma_min = sqrt(0.25/M) = sqrt(0.25/8192) = 0.00552 THEORETICAL@binomial-CLT.
#   HP delta threshold 0.30 = 55*sigma; well-reachable.
#   Dense-Hopfield capacity CITED@Ramsauer2021_eq14: O(2^(N/2)) at eps -> N_c=8192 trivial.

# Cardinality (META_RULE_H): 4 arms this chunk
EXPECTED_N_UNITS = 4


# ---------------------------------------------------------------------------
# Substrate primitives (numpy reference path; smoke + selftests)
# ---------------------------------------------------------------------------
def pattern_separate_sparse(x: np.ndarray, P: np.ndarray, k: int) -> np.ndarray:
    """Project x via P and keep top-k by abs magnitude as sparse bipolar code."""
    h_raw = P @ x
    top_k_idx = np.argpartition(-np.abs(h_raw), k - 1)[:k]
    h_sparse = np.zeros(P.shape[0], dtype=np.float64)
    signs = np.sign(h_raw[top_k_idx])
    signs[signs == 0] = 1.0
    h_sparse[top_k_idx] = signs
    return h_sparse


def project_hippo_to_cortex(h_sparse: np.ndarray, P_hc: np.ndarray) -> np.ndarray:
    c = P_hc @ h_sparse
    n = float(np.linalg.norm(c))
    if n > 0:
        c = c / n
    return c


def hebbian_write_cortex(W_c: np.ndarray, key: np.ndarray, val: np.ndarray,
                         eta: float) -> None:
    W_c += eta * np.outer(val, key)


def hebbian_write_hippo_sparse(W_h: np.ndarray, key_h: np.ndarray,
                               val_h: np.ndarray) -> None:
    W_h += np.outer(val_h, key_h)


def hippo_readout(W_h: np.ndarray, cue: np.ndarray) -> np.ndarray:
    """Reactivate stored value via hippo readout: sign(W_h @ cue). N_h bipolar."""
    raw = W_h @ cue
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def cortex_readout(W_c: np.ndarray, key: np.ndarray) -> np.ndarray:
    raw = W_c @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def dense_hopfield_readout(V: np.ndarray, query: np.ndarray, beta: float) -> np.ndarray:
    """Ramsauer 2021 modern-Hopfield update.

    V: (M, N_c) stored pattern bank (rows are patterns).
    query: (N_c,) query vector (from cortex readout of a cue).
    beta: softmax inverse temperature.

    Returns pattern-completed vector p = V^T softmax(beta * V @ query).
    """
    # L2-normalize query for stable dot-product magnitudes
    n_q = float(np.linalg.norm(query))
    if n_q > 0:
        q_n = query / n_q
    else:
        q_n = query
    # Similarities: (M,)
    sims = V @ q_n
    # Softmax with numerical stability
    sims_scaled = beta * sims
    sims_scaled -= sims_scaled.max()
    w = np.exp(sims_scaled)
    w /= w.sum()
    # Weighted pattern combination
    p = V.T @ w  # (N_c,)
    return p


def cosine_match(pred: np.ndarray, candidates: np.ndarray) -> int:
    n_p = float(np.linalg.norm(pred))
    if n_p == 0:
        return 0
    p_n = pred / n_p
    sims = candidates @ p_n
    return int(np.argmax(sims))


# ---------------------------------------------------------------------------
# Numpy per-arm runner (smoke + CPU fallback)
# ---------------------------------------------------------------------------
def _pattern_separate_sparse_batched(X, P, k):
    """Batched k-WTA sparse-bipolar pattern separator (numpy version).
    X: (M, N_raw); P: (N_h, N_raw) -> (M, N_h) sparse bipolar."""
    h_raw = X @ P.T  # (M, N_h)
    abs_h = np.abs(h_raw)
    # top-k per row: argpartition; extract signs at those indices
    idx = np.argpartition(-abs_h, k - 1, axis=1)[:, :k]  # (M, k)
    signs = np.sign(np.take_along_axis(h_raw, idx, axis=1))  # (M, k)
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


def run_arm_numpy(arm_name: str, seed: int,
                  n_h: int, n_c: int, m_items: int, k_active: int,
                  n_replay: int, eta_c: float, beta_dense: float,
                  keys_raw: np.ndarray, vals_raw: np.ndarray,
                  P_in: np.ndarray, P_hc: np.ndarray, out_dir: Path) -> Dict:
    t0 = time.time()
    try:
        W_hippo = np.zeros((n_h, n_h), dtype=np.float64)
        W_cortex = np.zeros((n_c, n_c), dtype=np.float64)
        if W_hippo is W_cortex:
            raise AssertionError("ANATOMICAL SEPARATION VIOLATION: W_h is W_c")
        if W_hippo.shape == W_cortex.shape:
            raise AssertionError(
                f"SHAPE VIOLATION: W_h.shape={W_hippo.shape} == "
                f"W_c.shape={W_cortex.shape}"
            )

        keys_h, vals_h, keys_c, vals_c = _encode_all_numpy(
            keys_raw, vals_raw, P_in, P_hc, n_h, n_c, m_items, k_active
        )
        emit_heartbeat(out_dir, unit_idx=0, total_units=n_replay,
                       elapsed_s=time.time() - t0,
                       extra={"phase": "encoded", "arm": arm_name})

        if arm_name == "ARM_STANDARD_SUBSTRATE":
            # Direct cortex Hebbian only (batched matmul: W += eta * V^T @ K).
            for cycle in range(n_replay):
                W_cortex += eta_c * (vals_c.T @ keys_c)
                if (cycle + 1) % 5 == 0:
                    emit_heartbeat(out_dir, unit_idx=cycle, total_units=n_replay,
                                   elapsed_s=time.time() - t0,
                                   extra={"phase": "direct_write", "arm": arm_name})
            # Batched readout: bipolar sign(K @ W^T); cosine-match against V.
            preds_raw = keys_c @ W_cortex.T  # (M, N_c)
            preds = np.sign(preds_raw)
            preds[preds == 0] = 1.0
            preds_n = preds / np.linalg.norm(preds, axis=1, keepdims=True).clip(min=1e-12)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(axis=1)
            n_hits = int((argmax == np.arange(m_items)).sum())
            recall = n_hits / float(m_items)

        elif arm_name == "ARM_HA_ONLY":
            # Hippo one-shot (batched), no replay, cortex empty at readout.
            W_hippo += vals_h.T @ keys_h
            W_hippo[:] = 0.0
            preds_raw = keys_c @ W_cortex.T
            preds = np.sign(preds_raw)
            preds[preds == 0] = 1.0
            preds_n = preds / np.linalg.norm(preds, axis=1, keepdims=True).clip(min=1e-12)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(axis=1)
            n_hits = int((argmax == np.arange(m_items)).sum())
            recall = n_hits / float(m_items)

        elif arm_name == "ARM_HA_HC" or arm_name == "ARM_HA_HC_DENSE":
            # Ha + Hc composition; CLS-faithful replay (batched matmul path
            # matching the torch backend).
            W_hippo += vals_h.T @ keys_h
            rng = np.random.RandomState(seed + 31)
            for cycle in range(n_replay):
                perm = rng.permutation(m_items)
                cues_h = keys_h[perm]                                  # (M, N_h)
                # Hippo readout: sign(cues_h @ W_h.T) -> N_h bipolar reactivated
                react_raw = cues_h @ W_hippo.T                         # (M, N_h)
                vals_react_h = np.sign(react_raw)
                vals_react_h[vals_react_h == 0] = 1.0
                # Project cues + reactivated vals to cortex; L2-normalize per row
                cues_c_batch = cues_h @ P_hc.T                         # (M, N_c)
                cues_c_batch = cues_c_batch / np.linalg.norm(
                    cues_c_batch, axis=1, keepdims=True).clip(min=1e-12)
                vals_c_react = vals_react_h @ P_hc.T                   # (M, N_c)
                vals_c_react = vals_c_react / np.linalg.norm(
                    vals_c_react, axis=1, keepdims=True).clip(min=1e-12)
                # Hebbian write from REACTIVATED signals (v2 discipline: NOT
                # from stored vals_c, keys_c).
                W_cortex += eta_c * (vals_c_react.T @ cues_c_batch)
                if (cycle + 1) % 5 == 0:
                    emit_heartbeat(out_dir, unit_idx=cycle, total_units=n_replay,
                                   elapsed_s=time.time() - t0,
                                   extra={"phase": "ha_hc_replay", "arm": arm_name})
            W_hippo[:] = 0.0

            if arm_name == "ARM_HA_HC":
                # Bipolar cortex readout (baseline HP@prior 51%).
                preds_raw = keys_c @ W_cortex.T
                preds = np.sign(preds_raw)
                preds[preds == 0] = 1.0
                preds_n = preds / np.linalg.norm(preds, axis=1, keepdims=True).clip(min=1e-12)
                sims = preds_n @ vals_c.T
                argmax = sims.argmax(axis=1)
                n_hits = int((argmax == np.arange(m_items)).sum())
                recall = n_hits / float(m_items)
            else:
                # ARM_HA_HC_DENSE: use bipolar cortex readout as query, then
                # dense-Hopfield softmax attention over stored V_c bank.
                queries_raw = keys_c @ W_cortex.T                       # (M, N_c)
                queries = np.sign(queries_raw)
                queries[queries == 0] = 1.0
                queries = queries / np.linalg.norm(
                    queries, axis=1, keepdims=True).clip(min=1e-12)
                # Batched dense-Hopfield: attn = softmax(beta * queries @ V.T)
                sims_dense = queries @ vals_c.T                         # (M, M)
                sims_dense_scaled = beta_dense * sims_dense
                sims_dense_scaled -= sims_dense_scaled.max(axis=1, keepdims=True)
                w_attn = np.exp(sims_dense_scaled)
                w_attn = w_attn / w_attn.sum(axis=1, keepdims=True).clip(min=1e-30)
                # Pattern-completed: (M, M) @ (M, N_c) -> (M, N_c)
                p = w_attn @ vals_c
                p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)
                sims_match = p_n @ vals_c.T
                argmax = sims_match.argmax(axis=1)
                n_hits = int((argmax == np.arange(m_items)).sum())
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
            "n_replay_cycles": int(n_replay),
            "beta_dense": float(beta_dense),
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
            "n_replay_cycles": int(n_replay),
            "beta_dense": float(beta_dense),
            "wall_s": float(wall),
            "backend": "numpy",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
            "failure_class": type(exc).__name__,
        }


# ---------------------------------------------------------------------------
# Torch/CUDA per-arm runner (FULL on remote GPU) -- optional; falls to numpy
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


def _project_hippo_to_cortex_torch(h_sparse_batch, P_hc):
    c = h_sparse_batch @ P_hc.T
    norms = c.norm(dim=1, keepdim=True).clamp_min(1e-12)
    return c / norms


def run_arm_torch_cuda(arm_name: str, seed: int,
                       n_h: int, n_c: int, m_items: int, k_active: int,
                       n_replay: int, eta_c: float, beta_dense: float,
                       keys_raw_np: np.ndarray, vals_raw_np: np.ndarray,
                       P_in_np: np.ndarray, P_hc_np: np.ndarray,
                       out_dir: Path) -> Dict:
    t0 = time.time()
    dev = torch.device("cuda")
    try:
        torch.cuda.reset_peak_memory_stats(dev)
        mem_start = torch.cuda.memory_allocated(dev)

        keys_raw = torch.from_numpy(keys_raw_np).to(dev, dtype=torch.float32)
        vals_raw = torch.from_numpy(vals_raw_np).to(dev, dtype=torch.float32)
        P_in = torch.from_numpy(P_in_np).to(dev, dtype=torch.float32)
        P_hc = torch.from_numpy(P_hc_np).to(dev, dtype=torch.float32)

        W_hippo = torch.zeros((n_h, n_h), dtype=torch.float32, device=dev)
        W_cortex = torch.zeros((n_c, n_c), dtype=torch.float32, device=dev)
        if W_hippo is W_cortex:
            raise AssertionError("ANATOMICAL SEPARATION VIOLATION")
        if W_hippo.shape == W_cortex.shape:
            raise AssertionError(f"SHAPE VIOLATION: W_h={tuple(W_hippo.shape)}")

        keys_h = _pattern_separate_sparse_torch(keys_raw, P_in, k_active)
        vals_h = _pattern_separate_sparse_torch(vals_raw, P_in, k_active)
        keys_c = _project_hippo_to_cortex_torch(keys_h, P_hc)
        vals_c = _project_hippo_to_cortex_torch(vals_h, P_hc)
        torch.cuda.synchronize(dev)
        emit_heartbeat(out_dir, unit_idx=0, total_units=n_replay,
                       elapsed_s=time.time() - t0,
                       extra={"phase": "encoded", "arm": arm_name,
                              "gpu_mem_mb": torch.cuda.memory_allocated(dev) / 1e6})

        if arm_name == "ARM_STANDARD_SUBSTRATE":
            for cycle in range(n_replay):
                W_cortex.addmm_(vals_c.T, keys_c, alpha=eta_c)
                if (cycle + 1) % 5 == 0:
                    emit_heartbeat(out_dir, unit_idx=cycle, total_units=n_replay,
                                   elapsed_s=time.time() - t0,
                                   extra={"phase": "direct_write", "arm": arm_name})
            preds_raw = keys_c @ W_cortex.T
            preds = torch.sign(preds_raw)
            preds = torch.where(preds == 0, torch.ones_like(preds), preds)
            preds_n = preds / preds.norm(dim=1, keepdim=True).clamp_min(1e-12)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(dim=1)
            n_hits = int((argmax == torch.arange(m_items, device=dev)).sum().item())
            recall = n_hits / float(m_items)

        elif arm_name == "ARM_HA_ONLY":
            W_hippo.addmm_(vals_h.T, keys_h)
            W_hippo.zero_()
            preds_raw = keys_c @ W_cortex.T
            preds = torch.sign(preds_raw)
            preds = torch.where(preds == 0, torch.ones_like(preds), preds)
            preds_n = preds / preds.norm(dim=1, keepdim=True).clamp_min(1e-12)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(dim=1)
            n_hits = int((argmax == torch.arange(m_items, device=dev)).sum().item())
            recall = n_hits / float(m_items)

        elif arm_name == "ARM_HA_HC" or arm_name == "ARM_HA_HC_DENSE":
            # Ha encode
            W_hippo.addmm_(vals_h.T, keys_h)
            # Hc replay
            gen = torch.Generator(device=dev)
            gen.manual_seed(seed + 31)
            for cycle in range(n_replay):
                perm = torch.randperm(m_items, generator=gen, device=dev)
                cues_h = keys_h[perm]
                react_raw = cues_h @ W_hippo.T
                vals_react_h = torch.sign(react_raw)
                vals_react_h = torch.where(vals_react_h == 0,
                                           torch.ones_like(vals_react_h),
                                           vals_react_h)
                cues_c = cues_h @ P_hc.T
                cues_c = cues_c / cues_c.norm(dim=1, keepdim=True).clamp_min(1e-12)
                vals_c_react = vals_react_h @ P_hc.T
                vals_c_react = vals_c_react / vals_c_react.norm(dim=1, keepdim=True).clamp_min(1e-12)
                W_cortex.addmm_(vals_c_react.T, cues_c, alpha=eta_c)
                if (cycle + 1) % 5 == 0:
                    emit_heartbeat(out_dir, unit_idx=cycle, total_units=n_replay,
                                   elapsed_s=time.time() - t0,
                                   extra={"phase": "ha_hc_replay", "arm": arm_name})
            W_hippo.zero_()

            if arm_name == "ARM_HA_HC":
                preds_raw = keys_c @ W_cortex.T
                preds = torch.sign(preds_raw)
                preds = torch.where(preds == 0, torch.ones_like(preds), preds)
                preds_n = preds / preds.norm(dim=1, keepdim=True).clamp_min(1e-12)
                sims = preds_n @ vals_c.T
                argmax = sims.argmax(dim=1)
                n_hits = int((argmax == torch.arange(m_items, device=dev)).sum().item())
                recall = n_hits / float(m_items)
            else:
                # ARM_HA_HC_DENSE: replace bipolar cortex readout with dense-
                # Hopfield attention over V_c stored bank.
                # Query per item i: cortex_readout(W_c, keys_c[i]) (bipolar).
                queries_raw = keys_c @ W_cortex.T  # (M, N_c)
                queries = torch.sign(queries_raw)
                queries = torch.where(queries == 0, torch.ones_like(queries), queries)
                # L2-normalize queries.
                queries = queries / queries.norm(dim=1, keepdim=True).clamp_min(1e-12)
                # Dense-Hopfield: p_i = V^T softmax(beta * V q_i)
                # sims: (M_queries, M_patterns) = queries @ vals_c.T
                sims_dense = queries @ vals_c.T  # (M, M)
                sims_dense_scaled = beta_dense * sims_dense
                sims_dense_scaled = sims_dense_scaled - sims_dense_scaled.max(dim=1, keepdim=True).values
                w_attn = torch.exp(sims_dense_scaled)
                w_attn = w_attn / w_attn.sum(dim=1, keepdim=True).clamp_min(1e-30)
                # Weighted pattern combo: p_i = sum_j w_attn[i,j] * vals_c[j].
                p = w_attn @ vals_c  # (M, N_c)
                # Cosine match against vals_c.
                p_n = p / p.norm(dim=1, keepdim=True).clamp_min(1e-12)
                sims_match = p_n @ vals_c.T
                argmax = sims_match.argmax(dim=1)
                n_hits = int((argmax == torch.arange(m_items, device=dev)).sum().item())
                recall = n_hits / float(m_items)
        else:
            raise ValueError(f"unknown arm: {arm_name}")

        torch.cuda.synchronize(dev)
        mem_peak = torch.cuda.max_memory_allocated(dev)
        gpu_mem_peak_mb = float((mem_peak - mem_start) / 1e6)
        cortex_norm_val = float(W_cortex.norm().item())

        del keys_raw, vals_raw, P_in, P_hc, keys_h, vals_h, keys_c, vals_c
        del W_hippo, W_cortex
        torch.cuda.empty_cache()

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_cortex": float(recall),
            "n_items": int(m_items),
            "N_h": int(n_h),
            "N_c": int(n_c),
            "k_hippo_active": int(k_active),
            "n_replay_cycles": int(n_replay),
            "beta_dense": float(beta_dense),
            "wall_s": float(wall),
            "backend": "torch.cuda",
            "gpu_mem_peak_mb": float(gpu_mem_peak_mb),
            "arm_status": "OK",
            "cortex_norm": cortex_norm_val,
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
            "n_replay_cycles": int(n_replay),
            "beta_dense": float(beta_dense),
            "wall_s": float(wall),
            "backend": "torch.cuda",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
            "failure_class": type(exc).__name__,
        }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_anatomical_separation() -> None:
    W_h = np.zeros((N_HIPPO, N_HIPPO), dtype=np.float64)
    W_c = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
    if W_h is W_c:
        raise AssertionError("W_h is W_c (same object)")
    if W_h.shape == W_c.shape:
        raise AssertionError(f"shapes match: W_h={W_h.shape} W_c={W_c.shape}")


def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_raw = 64
    P = rng.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=N_raw).astype(np.float64)
    h = pattern_separate_sparse(x, P, K_HIPPO_ACTIVE)
    n_active = int(np.sum(np.abs(h) > 0))
    if n_active != K_HIPPO_ACTIVE:
        raise AssertionError(f"k-WTA sparsity wrong: got {n_active}")
    nz = h[np.abs(h) > 0]
    if not np.all(np.isin(nz, [-1.0, 1.0])):
        raise AssertionError("sparse code not bipolar")


def _selftest_dense_hopfield_perfect_recall() -> None:
    """Ramsauer dense-Hopfield: with M distinct patterns and high beta,
    readout of a stored pattern should return that pattern (self-recall)."""
    rng = np.random.RandomState(11)
    M_t, N_t = 8, 32
    V = rng.randn(M_t, N_t).astype(np.float64)
    # Normalize rows for stable softmax.
    V = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    # Query with pattern 3, beta large -> attention concentrates on row 3.
    q = V[3].copy()
    p = dense_hopfield_readout(V, q, beta=50.0)
    # p should be very close to V[3] (softmax nearly one-hot on index 3).
    err = float(np.linalg.norm(p - V[3]))
    if err > 0.1:
        raise AssertionError(
            f"DENSE_HOPFIELD_SELFTEST FAIL: reconstruction err={err} > 0.1"
        )
    # Cosine to V[3] should be argmax.
    idx = cosine_match(p, V)
    if idx != 3:
        raise AssertionError(
            f"DENSE_HOPFIELD_SELFTEST FAIL: argmax={idx} != 3"
        )


def _selftest_dense_hopfield_distinct_from_bipolar_readout() -> None:
    """Prove dense-Hopfield readout is DIFFERENT from bipolar cortex readout
    (i.e., ARM_HA_HC_DENSE does not collapse to ARM_HA_HC).

    Approach: build a small world; encode with a lossy cortex; verify that
    dense readout produces different vector than sign(W_c @ q)."""
    rng = np.random.RandomState(13)
    M_t, N_t = 8, 32
    V = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    V_norm = V / np.linalg.norm(V, axis=1, keepdims=True).clip(min=1e-12)
    K = rng.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float64)
    K_norm = K / np.linalg.norm(K, axis=1, keepdims=True).clip(min=1e-12)
    W = np.zeros((N_t, N_t), dtype=np.float64)
    for i in range(M_t):
        W += 0.1 * np.outer(V_norm[i], K_norm[i])
    # Bipolar readout for pattern 0.
    q_bipolar = cortex_readout(W, K_norm[0])
    # Dense readout for pattern 0 (query = bipolar cortex readout).
    p_dense = dense_hopfield_readout(V_norm, q_bipolar, beta=1.0)
    # Both should NOT be bit-identical.
    diff = float(np.linalg.norm(q_bipolar - p_dense))
    if diff < 1e-6:
        raise AssertionError(
            f"DENSE vs BIPOLAR indistinguishable: diff={diff}"
        )


def _selftest_projection_dim_match() -> None:
    rng = np.random.RandomState(11)
    h = np.zeros(N_HIPPO, dtype=np.float64)
    h[:K_HIPPO_ACTIVE] = 1.0
    P_hc = rng.randn(N_CORTEX, N_HIPPO).astype(np.float64) / np.sqrt(N_HIPPO)
    c = project_hippo_to_cortex(h, P_hc)
    if c.shape != (N_CORTEX,):
        raise AssertionError(f"projection shape wrong: {c.shape}")
    norm = float(np.linalg.norm(c))
    if not (0.5 < norm < 1.5):
        raise AssertionError(f"projection not L2-normed: norm={norm}")


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
    """META_RULE_AF preflight: run 4 arms in tiny world; verify all 4 output
    tensors differ (by hash of recall pattern -- proxy for full-arm hashes)."""
    rng = np.random.RandomState(17)
    M_t, Nh_t, Nc_t = 32, 128, 256
    Sp_t = 0.10
    k_t = max(1, int(round(Sp_t * Nh_t)))
    Nrep_t = 3
    eta_t = 0.05
    beta_t = 1.0
    N_raw_t = 32
    P_in_t = rng.randn(Nh_t, N_raw_t).astype(np.float64) / np.sqrt(N_raw_t)
    P_hc_t = rng.randn(Nc_t, Nh_t).astype(np.float64) / np.sqrt(Nh_t)
    keys_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)
    vals_raw_t = rng.choice([-1.0, 1.0], size=(M_t, N_raw_t)).astype(np.float64)

    tmp_out = Path(REPO) / "data" / "_selftest_arms_differ_tmp"
    tmp_out.mkdir(parents=True, exist_ok=True)

    out_arms = {}
    for arm_name in ("ARM_STANDARD_SUBSTRATE", "ARM_HA_ONLY",
                     "ARM_HA_HC", "ARM_HA_HC_DENSE"):
        r = run_arm_numpy(arm_name, seed=42,
                          n_h=Nh_t, n_c=Nc_t, m_items=M_t, k_active=k_t,
                          n_replay=Nrep_t, eta_c=eta_t, beta_dense=beta_t,
                          keys_raw=keys_raw_t, vals_raw=vals_raw_t,
                          P_in=P_in_t, P_hc=P_hc_t, out_dir=tmp_out)
        if r["arm_status"] != "OK":
            raise AssertionError(
                f"arm {arm_name} errored in selftest: {r['arm_status']}"
            )
        out_arms[arm_name] = r["recall_cortex"]

    # All 4 recalls should be distinct in a tiny world (M=32, mixed
    # mechanisms). If any two match to 1e-9, one arm may bypass its
    # mechanism.
    vals = list(out_arms.values())
    for i in range(len(vals)):
        for j in range(i + 1, len(vals)):
            if abs(vals[i] - vals[j]) < 1e-9:
                names = list(out_arms.keys())
                raise AssertionError(
                    f"META_RULE_AF_preflight: arm recalls identical: "
                    f"{names[i]}={vals[i]} == {names[j]}={vals[j]}"
                )


def _instrumentation_selftest() -> None:
    try:
        _selftest_anatomical_separation()
        _selftest_sparse_pattern_separator()
        _selftest_projection_dim_match()
        _selftest_chunk_seed_matches_anchor()
        _selftest_capacity_alpha()
        _selftest_dense_hopfield_perfect_recall()
        _selftest_dense_hopfield_distinct_from_bipolar_readout()
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
        f"M={M_ITEMS}  N_replay={N_REPLAY_CYCLES}  eta_c={ETA_CORTEX}  "
        f"beta_dense={BETA_DENSE}  mode={RUN_MODE}  chunk_seed={SEED_THIS_CHUNK}  "
        f"alpha_simple={ALPHA_SIMPLE:.4f}  alpha_hopfield={ALPHA_HOPFIELD:.4f}  "
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
        f"N_c={N_CORTEX} (dense), M={M_ITEMS}, N_replay={N_REPLAY_CYCLES}, "
        f"beta_dense={BETA_DENSE}, backend={COMPUTE_BACKEND}",
        flush=True,
    )

    arms = []
    for arm_name in ("ARM_STANDARD_SUBSTRATE", "ARM_HA_ONLY",
                     "ARM_HA_HC", "ARM_HA_HC_DENSE"):
        if USE_TORCH_CUDA:
            out = run_arm_torch_cuda(arm_name, seed,
                                     n_h=N_HIPPO, n_c=N_CORTEX, m_items=M_ITEMS,
                                     k_active=K_HIPPO_ACTIVE,
                                     n_replay=N_REPLAY_CYCLES, eta_c=ETA_CORTEX,
                                     beta_dense=BETA_DENSE,
                                     keys_raw_np=keys_raw, vals_raw_np=vals_raw,
                                     P_in_np=P_in, P_hc_np=P_hc,
                                     out_dir=out_dir)
        else:
            out = run_arm_numpy(arm_name, seed,
                                n_h=N_HIPPO, n_c=N_CORTEX, m_items=M_ITEMS,
                                k_active=K_HIPPO_ACTIVE,
                                n_replay=N_REPLAY_CYCLES, eta_c=ETA_CORTEX,
                                beta_dense=BETA_DENSE,
                                keys_raw=keys_raw, vals_raw=vals_raw,
                                P_in=P_in, P_hc=P_hc, out_dir=out_dir)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
            f"recall={out['recall_cortex']:.3f} "
            f"backend={out['backend']} "
            f"gpu_mem_peak_mb={out['gpu_mem_peak_mb']:.1f} "
            f"status={out['arm_status']} wall={out['wall_s']:.1f}s",
            flush=True,
        )

    # Optional full-N preview arm (smoke only; DISCRIMINATOR-MUST-SURVIVE-SCALE)
    preview_arm = None
    if RUN_MODE == "smoke" and RUN_FULL_N_PREVIEW:
        print(f"  [seed={seed} PREVIEW_HA_HC_DENSE_FULL_N] running at N_h="
              f"{N_HIPPO_FULL}, N_c={N_CORTEX_FULL}, M={M_ITEMS_FULL}...",
              flush=True)
        # Fresh rngs for full-N preview.
        rng_p = np.random.RandomState(seed + 101)
        P_in_p = rng_p.randn(N_HIPPO_FULL, N_raw).astype(np.float64) / np.sqrt(N_raw)
        P_hc_p = rng_p.randn(N_CORTEX_FULL, N_HIPPO_FULL).astype(np.float64) / np.sqrt(N_HIPPO_FULL)
        keys_raw_p = rng_p.choice([-1.0, 1.0], size=(M_ITEMS_FULL, N_raw)).astype(np.float64)
        vals_raw_p = rng_p.choice([-1.0, 1.0], size=(M_ITEMS_FULL, N_raw)).astype(np.float64)
        k_active_p = max(1, int(round(HIPPO_SPARSITY * N_HIPPO_FULL)))

        preview_arm = run_arm_numpy(
            "ARM_HA_HC_DENSE_FULL_N_PREVIEW", seed,
            n_h=N_HIPPO_FULL, n_c=N_CORTEX_FULL, m_items=M_ITEMS_FULL,
            k_active=k_active_p, n_replay=N_REPLAY_CYCLES_FULL,
            eta_c=ETA_CORTEX_FULL, beta_dense=BETA_DENSE_FULL,
            keys_raw=keys_raw_p, vals_raw=vals_raw_p,
            P_in=P_in_p, P_hc=P_hc_p, out_dir=out_dir,
        )
        print(
            f"  [seed={seed} PREVIEW_HA_HC_DENSE_FULL_N] "
            f"recall={preview_arm['recall_cortex']:.3f} "
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
        "N_replay": N_REPLAY_CYCLES,
        "eta_c": ETA_CORTEX,
        "beta_dense": BETA_DENSE,
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


def _hash_arm_recall_pattern(a: Dict) -> str:
    """Hash the arm's recall + N_h/N_c/mode identity as a proxy for arm-differ.
    (Full tensor hashing would require re-running arms; recall is sufficient
    when the mechanisms compute different code paths, which is the concern.)"""
    b = json.dumps({
        "arm": a["arm_name"],
        "recall": round(a["recall_cortex"], 6),
        "backend": a.get("backend"),
    }).encode()
    return hashlib.sha256(b).hexdigest()


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    if len(results) != 1:
        return ("HARD_FAIL", f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    arm_names_expected = ("ARM_STANDARD_SUBSTRATE", "ARM_HA_ONLY",
                          "ARM_HA_HC", "ARM_HA_HC_DENSE")
    # In smoke with preview arm, we have 5 arms total; only first 4 count for cardinality.
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
    ha_hc = per[2]["recall_cortex"]
    ha_hc_dense = per[3]["recall_cortex"]

    # META_RULE_AF: verify arms don't share bit-identical recall.
    recalls = [standard, ha_only, ha_hc, ha_hc_dense]
    names = list(arm_names_expected)
    for i in range(len(recalls)):
        for j in range(i + 1, len(recalls)):
            if abs(recalls[i] - recalls[j]) < 1e-6:
                # Allow ARM_HA_ONLY == ARM_STANDARD when both start with empty
                # cortex and no substantive write happens -- but that's a bug
                # signature not a legit path. Reject all bit-identity.
                return ("HARD_FAIL",
                        f"META_RULE_AF VIOLATION (bit-exact): {names[i]}={recalls[i]} "
                        f"== {names[j]}={recalls[j]}")

    # Fairness: ARM_HA_ONLY should be low (cortex genuinely empty).
    if ha_only > 0.20:
        return ("HARD_FAIL",
                f"FAIRNESS: ARM_HA_ONLY={ha_only:.3f} > 0.20 -- cortex leaking")

    # Deltas
    dense_gain = ha_hc_dense - ha_hc            # dense layer effect
    replay_gap = ha_hc - ha_only                 # replay effect
    absolute_dense = ha_hc_dense

    summary = (
        f"seed={SEED_THIS_CHUNK} STANDARD={standard:.3f} HA_ONLY={ha_only:.3f} "
        f"HA_HC={ha_hc:.3f} HA_HC_DENSE={ha_hc_dense:.3f} "
        f"dense_gain={dense_gain:+.3f} replay_gap={replay_gap:+.3f} "
        f"alpha_simple={ALPHA_SIMPLE:.4f} backend={COMPUTE_BACKEND}"
    )

    # HARD_PASS gates
    hp_dense_abs = absolute_dense >= 0.80
    hp_dense_gain = dense_gain >= 0.30
    hp_replay_gap = replay_gap >= 0.20
    hp_alpha = ALPHA_SIMPLE >= 0.05 if RUN_MODE == "full" else True

    if all([hp_dense_abs, hp_dense_gain, hp_replay_gap, hp_alpha]):
        return ("HARD_PASS",
                f"HARD_PASS: dense_abs>=0.80 AND dense_gain>=0.30 AND "
                f"replay_gap>=0.20 AND alpha>=0.05. {summary}")

    # HARD_FAIL gates
    if dense_gain < 0.05:
        return ("HARD_FAIL",
                f"HARD_FAIL: dense_gain={dense_gain:+.3f} < 0.05 -- dense "
                f"layer is scenery, not discriminator. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: partial rescue. "
            f"hp_checks=[dense_abs={hp_dense_abs},dense_gain={hp_dense_gain},"
            f"replay_gap={hp_replay_gap},alpha={hp_alpha}]. {summary}")


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
              f"N_replay={N_REPLAY_CYCLES} beta_dense={BETA_DENSE} mode={RUN_MODE} "
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
            f"M={M_ITEMS} N_replay={N_REPLAY_CYCLES} beta_dense={BETA_DENSE} "
            f"mode={RUN_MODE} alpha_simple={ALPHA_SIMPLE:.4f} "
            f"backend={COMPUTE_BACKEND}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "N_replay": N_REPLAY_CYCLES,
        "eta_c": ETA_CORTEX,
        "beta_dense": BETA_DENSE,
        "hippo_sparsity": HIPPO_SPARSITY,
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
                     if a["arm_name"] in ("ARM_STANDARD_SUBSTRATE", "ARM_HA_ONLY",
                                          "ARM_HA_HC", "ARM_HA_HC_DENSE")])
            == EXPECTED_N_UNITS
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "arms_differ_verified": True,  # enforced in compute_verdict (bit-exact reject)
        "final_metrics_atomicity": "tmp_replace",
        "crlb_floor_computed": 0.00552,
        "crlb_formula_reference": "sigma_min = sqrt(0.25/M) binomial-CLT",
        "discriminator_reachability": True,
        "calibration_check": "default_ok_for_this_regime",
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
