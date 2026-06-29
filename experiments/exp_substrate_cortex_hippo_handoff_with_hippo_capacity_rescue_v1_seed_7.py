"""substrate_cortex_hippo_handoff_with_hippo_capacity_rescue_v1 -- seed_7.

DIAGNOSTIC PROBE.  Default tier MEASURED_MECHANISM (NOT chain-grade promotion).
Identifies whether ANY hippo-readout-fidelity rescue opens up Stage 2 NREM
consolidation at chain-grade M=8192.

LINEAGE:
  v1 standard handoff (CLOSED-negative at M=8192 -- 3 mechanism classes tried)
  v2 replay-fixed (CLOSED-negative -- corrected replay-via-hippo-readout path)
  spaced-rep NREM v1 (SMOKE 3-way COLLAPSE -- gap 0.006 at alpha=1.0)
  ==>  diagnosis: hippo READOUT FIDELITY is the floor, not the consolidation
       schedule.  At M=8192 N_h=4096 the hippo's effective alpha_h is
       ~M/(2*N_h*log(N_h)) ~= 0.137 -- Hopfield-strict regime.  sign(W_h @ cue)
       produces noisy output regardless of replay schedule.

KEY INSIGHT (USER 2026-06-28):
  The spacing curve only matters once the underlying readout SNR is above
  zero.  Vary N_h while holding M=8192 fixed; find regime where DIRECT
  (bypasses hippo readout) and FULL (uses sign(W_h @ cue)) recall meaningfully
  DIVERGE.  THAT regime is where consolidation testing is honest.

ARMS (3 per N_h):
  ARM_DIRECT_NO_HIPPO:
    Cortex writes directly from cue (bypasses hippo readout entirely).
    Reference / no-noise-floor ceiling for given (M, N_c, eta_c).

  ARM_STANDARD_HIPPO:
    Standard `sign(W_h @ cue)` readout (current substrate baseline).
    The noisy-readout path under question.

  ARM_RESCUED_HIPPO:
    Two-step Hopfield-style cleanup: x_clean = sign(W_h @ sign(W_h @ cue))
    THEN project to cortex.  Chosen mechanism for Stage 1 substrate evidence
    because it is (i) substrate-only (no learning-rule changes), (ii) cheap
    (one extra N_h^2 matmul + sign per replay), (iii) classical Hopfield
    one-step cleanup (well-documented; either converges to a better basin or
    oscillates near the saturation regime).

DISCRIMINATOR:
  gap_direct_minus_standard, gap_direct_minus_rescued, and
  rescued_closes_fraction = (gap_direct_minus_standard
                             - gap_direct_minus_rescued)
                            / max(1e-6, gap_direct_minus_standard).
  Where the gap CLOSES (rescued reaches within EPS of direct), THAT N_h is
  the regime where consolidation testing becomes meaningful.

  POTENTIAL_MAJOR_UNLOCK:
    rescued_closes_fraction >= 0.50 at any swept N_h.  This means a
    substrate-only readout-fidelity rescue OPENS a path to Stage 2 NREM
    closure at chain-grade.  Flag MAJOR research signal -- it would re-open
    cortex_hippo_handoff CLOSED-negative with the rescue as the conditional.

SWEEP:
  N_h in {1024, 2048, 4096, 8192, 16384, 32768}  (FULL; 6 N_h values)
  N_h in {512,  2048,        8192}                (SMOKE; 3 N_h values, M=2048)
  M = 8192 (FULL chain-grade) / 2048 (SMOKE).
  Total units per seed: 3 arms * N_NH = 18 (FULL), 9 (SMOKE).

Discriminator-survives-scale (USER 2026-06-26):
  Smoke at M=2048 sweeps SAME-shape N_h grid (scaled).  At any N_h value, we
  expect ARM_DIRECT > ARM_STANDARD by margin > 0.05 (proving readout
  bottleneck is real at smoke scale BEFORE chasing fidelity rescue at FULL).
  If smoke shows DIRECT ~= STANDARD across the full N_h sweep, then the
  readout bottleneck is NOT the failure mode at this regime and the rescue
  hypothesis is moot.

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = N_ARMS * N_NH (3 * len(N_H_GRID)).

GPU (Fix #24):
  FULL run uses torch.cuda.  Largest W_h is N_h=32768 -> 32768^2 fp32 = 4.3 GB.
  Plus W_c (8192^2 fp32 = 268 MB), keys_h (8192*32768 fp32 = 1 GB), and
  scratch buffers.  Per-arm peak ~5-6 GB; fits 8GB cards with batched cleanup
  iteration.  Per-arm streaming: process one N_h at a time, free before next.

ASCII-only; no unicode; no emojis; no em-dashes.
META_RULE_AH atomic-write; META_RULE_AF arms-must-differ.
META_RULE_H cardinality_ok = (n_units == EXPECTED_N_UNITS).

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
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

# Inlined heartbeat helper.
from datetime import datetime as _dt_mod, timezone as _tz_mod
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    row = {
        "ts_iso": _dt_mod.now(_tz_mod.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
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


ANCHOR_NAME = "substrate_cortex_hippo_handoff_with_hippo_capacity_rescue_v1_seed_7"
SEED_THIS_CHUNK = 7
_LLM_CALL_COUNTER = [0]
_HARDENING_MARKER = "v1_hippo_capacity_rescue_diagnostic"

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
# Torch import + cuda selection.
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
# Config: hold M fixed, sweep N_h.
# ---------------------------------------------------------------------------
# FULL: chain-grade.  6 N_h points.
M_ITEMS_FULL = 8192
N_CORTEX_FULL = 8192
N_H_GRID_FULL = [1024, 2048, 4096, 8192, 16384, 32768]
ETA_CORTEX_FULL = 0.01
# All M items replayed once each per arm (we are isolating the READOUT
# fidelity question; one replay per item suffices to expose the bottleneck).
N_REPLAY_PER_ITEM_FULL = 1
# Hippo encode density (matches v2 parent).
HIPPO_SPARSITY = 0.10

# SMOKE: M=2048, N_h sweep small/medium/large.
if RUN_MODE == "smoke":
    M_ITEMS = 2048
    N_CORTEX = 2048
    N_H_GRID = [512, 2048, 8192]
    ETA_CORTEX = 0.005
    SEEDS = [SEED_THIS_CHUNK]
    N_REPLAY_PER_ITEM = 1
else:
    M_ITEMS = M_ITEMS_FULL
    N_CORTEX = N_CORTEX_FULL
    N_H_GRID = N_H_GRID_FULL
    ETA_CORTEX = ETA_CORTEX_FULL
    SEEDS = [SEED_THIS_CHUNK]
    N_REPLAY_PER_ITEM = N_REPLAY_PER_ITEM_FULL


ARM_NAMES: Tuple[str, ...] = (
    "ARM_DIRECT_NO_HIPPO",
    "ARM_STANDARD_HIPPO",
    "ARM_RESCUED_HIPPO",
)

# Cardinality (META_RULE_H): arms x N_h points.
EXPECTED_N_UNITS = len(ARM_NAMES) * len(N_H_GRID)

# Discriminator thresholds.
RESCUE_CLOSES_FRAC_MAJOR_UNLOCK = 0.50
RESCUE_CLOSES_FRAC_HARD_PASS = 0.25
DIRECT_VS_STANDARD_GAP_MIN_FOR_DISCRIM = 0.05  # smoke discriminator: bottleneck must exist


def _alpha_h(M: int, N_h: int) -> float:
    if N_h <= 1:
        return float("inf")
    return float(M) / (2.0 * float(N_h) * math.log(float(N_h)))


def _alpha_simple(M: int, N_h: int) -> float:
    return float(M) / float(N_h)


USE_TORCH_CUDA = (RUN_MODE == "full") and _TORCH_AVAILABLE and _CUDA_AVAILABLE
COMPUTE_BACKEND = "torch.cuda" if USE_TORCH_CUDA else ("torch.cpu" if _TORCH_AVAILABLE else "numpy")

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},M={M_ITEMS},N_c={N_CORTEX},"
    f"N_h_grid={'-'.join(str(n) for n in N_H_GRID)},"
    f"sparsity={HIPPO_SPARSITY},n_replay_per_item={N_REPLAY_PER_ITEM},"
    f"eta_c={ETA_CORTEX},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},chunk_seed={SEED_THIS_CHUNK},"
    f"backend={COMPUTE_BACKEND},"
    f"hardening=L1early+L2perarm+L4importsentinel+METARULE_AF+METARULE_AH+METARULE_H+GPU_PROXY+RESCUE_DIAGNOSTIC"
)


# ---------------------------------------------------------------------------
# Substrate primitives (numpy reference path).
# ---------------------------------------------------------------------------
def pattern_separate_sparse(x: np.ndarray, P: np.ndarray, k: int) -> np.ndarray:
    h_raw = P @ x
    top_k_idx = np.argpartition(-np.abs(h_raw), k - 1)[:k]
    h_sparse = np.zeros(P.shape[0], dtype=np.float64)
    signs = np.sign(h_raw[top_k_idx])
    signs[signs == 0] = 1.0
    h_sparse[top_k_idx] = signs
    return h_sparse


def hippo_readout_standard(W_h: np.ndarray, cue: np.ndarray) -> np.ndarray:
    """Single sign(W_h @ cue) readout (standard substrate baseline)."""
    raw = W_h @ cue
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def hippo_readout_rescued_two_step(W_h: np.ndarray, cue: np.ndarray) -> np.ndarray:
    """Two-step Hopfield-style cleanup: sign(W_h @ sign(W_h @ cue)).

    Reuses the SAME W_h (no extra learning).  Classical Hopfield 1-step
    cleanup: if the readout settles into a basin, the second step refines;
    if it oscillates, second step ~= first step (no help, no harm).
    """
    step1_raw = W_h @ cue
    step1 = np.sign(step1_raw)
    step1[step1 == 0] = 1.0
    step2_raw = W_h @ step1
    step2 = np.sign(step2_raw)
    step2[step2 == 0] = 1.0
    return step2


def cortex_readout(W_c: np.ndarray, key: np.ndarray) -> np.ndarray:
    raw = W_c @ key
    out = np.sign(raw)
    out[out == 0] = 1.0
    return out


def cosine_match(pred: np.ndarray, candidates: np.ndarray) -> int:
    n_p = float(np.linalg.norm(pred))
    if n_p == 0:
        return 0
    p_n = pred / n_p
    sims = candidates @ p_n
    return int(np.argmax(sims))


# ---------------------------------------------------------------------------
# Numpy per-arm runner (smoke + CPU fallback).
# ---------------------------------------------------------------------------
def _l2_normalize(v: np.ndarray) -> np.ndarray:
    n = float(np.linalg.norm(v))
    if n > 0:
        return v / n
    return v


def _batched_l2_normalize(v_batch: np.ndarray) -> np.ndarray:
    """L2-normalize each row of v_batch; zero rows preserved."""
    norms = np.linalg.norm(v_batch, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-12)
    return v_batch / norms


def _batched_sparse_pattern_separator(x_batch: np.ndarray,
                                      P: np.ndarray, k: int) -> np.ndarray:
    """Batched k-WTA sparse pattern separator.

    x_batch: (M, N_raw)
    P:       (N_h, N_raw)
    returns: (M, N_h) sparse bipolar with exactly k non-zero entries per row.

    Equivalent (per-row) to:
        h_raw = P @ x_batch[i]
        top_k = argpartition(-|h_raw|, k-1)[:k]
        h[top_k] = sign(h_raw[top_k]); h[h==0] = 1
    """
    h_raw = x_batch @ P.T                          # (M, N_h)
    abs_h = np.abs(h_raw)
    # Partition along last axis: indices of top-k per row.
    topk_idx = np.argpartition(-abs_h, k - 1, axis=1)[:, :k]  # (M, k)
    rows = np.arange(h_raw.shape[0])[:, None]                  # (M, 1)
    signs_at_topk = np.sign(h_raw[rows, topk_idx])
    signs_at_topk[signs_at_topk == 0] = 1.0
    h_sparse = np.zeros_like(h_raw)
    h_sparse[rows, topk_idx] = signs_at_topk
    return h_sparse


def run_arm_numpy(arm_name: str, N_h: int, seed: int,
                  keys_raw: np.ndarray, vals_raw: np.ndarray,
                  P_in: np.ndarray, P_hc: np.ndarray,
                  out_dir: Path) -> Dict:
    """Numpy single-arm runner for a particular (arm_name, N_h)."""
    t0 = time.time()
    k_active = max(1, int(round(HIPPO_SPARSITY * N_h)))
    try:
        # Shape verification at runtime (META_RULE_AH).
        if P_in.shape != (N_h, keys_raw.shape[1]):
            raise AssertionError(
                f"P_in shape mismatch: got {P_in.shape}, "
                f"want ({N_h}, {keys_raw.shape[1]})"
            )
        if P_hc.shape != (N_CORTEX, N_h):
            raise AssertionError(
                f"P_hc shape mismatch: got {P_hc.shape}, "
                f"want ({N_CORTEX}, {N_h})"
            )

        W_hippo = np.zeros((N_h, N_h), dtype=np.float64)
        W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
        if W_hippo is W_cortex:
            raise AssertionError("ANATOMICAL SEPARATION VIOLATION: W_h is W_c")

        # Encode all items into sparse hippo + dense cortex (BATCHED).
        # keys_h[i] = pattern_separate_sparse(keys_raw[i], P_in, k_active);
        # batched form: h_raw = keys_raw @ P_in.T then per-row top-k.
        keys_h = _batched_sparse_pattern_separator(keys_raw, P_in, k_active)
        vals_h = _batched_sparse_pattern_separator(vals_raw, P_in, k_active)
        # P_hc @ x is shape (N_c, N_h) @ (N_h,) -> (N_c,);
        # batched: x_batch @ P_hc.T -> (M, N_c).
        keys_c_raw = keys_h @ P_hc.T
        vals_c_raw = vals_h @ P_hc.T
        keys_c = _batched_l2_normalize(keys_c_raw)
        vals_c = _batched_l2_normalize(vals_c_raw)
        emit_heartbeat(out_dir, unit_idx=M_ITEMS - 1, total_units=M_ITEMS,
                       elapsed_s=time.time() - t0,
                       extra={"phase": "encode", "arm": arm_name, "N_h": N_h})

        active_per_atom = np.sum(np.abs(keys_h) > 0, axis=1)
        if not np.all(active_per_atom == k_active):
            raise AssertionError(
                f"SPARSITY VIOLATION: keys_h active counts mismatch "
                f"k_active={k_active} N_h={N_h}; got {active_per_atom[:5]}..."
            )

        # Hippo encode (BATCHED): W_hippo = vals_h.T @ keys_h
        # (sum of outer products vals_h_i (X) keys_h_i over all i)
        W_hippo = vals_h.T @ keys_h

        # Replay phase: produces the "consolidated" cortex via the arm's
        # specific readout path (BATCHED matrix form, equivalent to the
        # per-item loop because order-permutation under additive Hebbian is
        # commutative).
        n_total_writes = 0
        rng = np.random.RandomState(seed + 17)
        for rep in range(N_REPLAY_PER_ITEM):
            perm = rng.permutation(M_ITEMS)
            cues_h = keys_h[perm]              # (M, N_h)
            cues_c = keys_c[perm]              # (M, N_c)

            if arm_name == "ARM_DIRECT_NO_HIPPO":
                vals_c_react = vals_c[perm]    # (M, N_c)
            elif arm_name == "ARM_STANDARD_HIPPO":
                step1_raw = cues_h @ W_hippo.T  # (M, N_h)
                vals_react_h = np.sign(step1_raw)
                vals_react_h[vals_react_h == 0] = 1.0
                vals_c_react = _batched_l2_normalize(vals_react_h @ P_hc.T)
            elif arm_name == "ARM_RESCUED_HIPPO":
                step1_raw = cues_h @ W_hippo.T
                step1 = np.sign(step1_raw)
                step1[step1 == 0] = 1.0
                step2_raw = step1 @ W_hippo.T
                step2 = np.sign(step2_raw)
                step2[step2 == 0] = 1.0
                vals_c_react = _batched_l2_normalize(step2 @ P_hc.T)
            else:
                raise ValueError(f"unknown arm: {arm_name}")

            # Batched cortex Hebbian write: W_c += eta * vals_c_react.T @ cues_c
            W_cortex += ETA_CORTEX * (vals_c_react.T @ cues_c)
            n_total_writes += M_ITEMS
            emit_heartbeat(out_dir, unit_idx=rep, total_units=N_REPLAY_PER_ITEM,
                           elapsed_s=time.time() - t0,
                           extra={"phase": "replay", "arm": arm_name,
                                  "N_h": N_h, "writes_so_far": n_total_writes})

        W_hippo[:] = 0.0  # free memory (we no longer need it for recall)

        # Recall test (BATCHED).
        preds_raw = keys_c @ W_cortex.T            # (M, N_c)
        preds = np.sign(preds_raw)
        preds[preds == 0] = 1.0
        preds_n = _batched_l2_normalize(preds)
        sims = preds_n @ vals_c.T                  # (M, M)
        argmax = np.argmax(sims, axis=1)
        n_hits = int(np.sum(argmax == np.arange(M_ITEMS)))
        recall = n_hits / float(M_ITEMS)
        cortex_norm = float(np.linalg.norm(W_cortex))

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "N_h": int(N_h),
            "k_hippo_active": int(k_active),
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "cortex_norm": float(cortex_norm),
            "n_total_writes": int(n_total_writes),
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_h)),
            "alpha_hopfield": float(_alpha_h(M_ITEMS, N_h)),
            "wall_s": float(wall),
            "backend": "numpy",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "N_h": int(N_h),
            "k_hippo_active": int(k_active),
            "recall_cortex": float("nan"),
            "n_items": 0,
            "cortex_norm": float("nan"),
            "n_total_writes": 0,
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_h)),
            "alpha_hopfield": float(_alpha_h(M_ITEMS, N_h)),
            "wall_s": float(wall),
            "backend": "numpy",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Torch/CUDA per-arm runner (FULL on remote GPU).
# ---------------------------------------------------------------------------
def _pattern_separate_sparse_torch(x_batch, P, k):
    h_raw = x_batch @ P.T
    abs_h = h_raw.abs()
    topk_vals, topk_idx = torch.topk(abs_h, k, dim=1)
    signs_at_topk = torch.sign(torch.gather(h_raw, 1, topk_idx))
    signs_at_topk = torch.where(signs_at_topk == 0,
                                torch.ones_like(signs_at_topk),
                                signs_at_topk)
    h_sparse = torch.zeros_like(h_raw)
    h_sparse.scatter_(1, topk_idx, signs_at_topk)
    return h_sparse


def _l2_normalize_batch_torch(v_batch):
    norms = v_batch.norm(dim=1, keepdim=True).clamp_min(1e-12)
    return v_batch / norms


def run_arm_torch_cuda(arm_name: str, N_h: int, seed: int,
                       keys_raw_np: np.ndarray, vals_raw_np: np.ndarray,
                       P_in_np: np.ndarray, P_hc_np: np.ndarray,
                       out_dir: Path) -> Dict:
    t0 = time.time()
    k_active = max(1, int(round(HIPPO_SPARSITY * N_h)))
    dev = torch.device("cuda")
    try:
        torch.cuda.reset_peak_memory_stats(dev)
        mem_start = torch.cuda.memory_allocated(dev)

        keys_raw = torch.from_numpy(keys_raw_np).to(dev, dtype=torch.float32)
        vals_raw = torch.from_numpy(vals_raw_np).to(dev, dtype=torch.float32)
        P_in = torch.from_numpy(P_in_np).to(dev, dtype=torch.float32)
        P_hc = torch.from_numpy(P_hc_np).to(dev, dtype=torch.float32)

        if P_in.shape != (N_h, keys_raw.shape[1]):
            raise AssertionError(
                f"P_in shape mismatch: got {tuple(P_in.shape)}, "
                f"want ({N_h}, {keys_raw.shape[1]})"
            )
        if P_hc.shape != (N_CORTEX, N_h):
            raise AssertionError(
                f"P_hc shape mismatch: got {tuple(P_hc.shape)}, "
                f"want ({N_CORTEX}, {N_h})"
            )

        W_hippo = torch.zeros((N_h, N_h), dtype=torch.float32, device=dev)
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=torch.float32, device=dev)
        if W_hippo is W_cortex:
            raise AssertionError("ANATOMICAL SEPARATION VIOLATION: W_h is W_c")

        # Encode items, batched.
        keys_h = _pattern_separate_sparse_torch(keys_raw, P_in, k_active)
        vals_h = _pattern_separate_sparse_torch(vals_raw, P_in, k_active)
        keys_c = _l2_normalize_batch_torch(keys_h @ P_hc.T)
        vals_c = _l2_normalize_batch_torch(vals_h @ P_hc.T)
        torch.cuda.synchronize(dev)

        active_per_atom = (keys_h.abs() > 0).sum(dim=1)
        if not bool((active_per_atom == k_active).all().item()):
            raise AssertionError(
                f"SPARSITY VIOLATION: keys_h active mismatch k={k_active}; "
                f"got first5={active_per_atom[:5].tolist()}"
            )

        # Hippo encode (one-shot Hebbian).
        W_hippo.addmm_(vals_h.T, keys_h)

        n_total_writes = 0
        gen = torch.Generator(device=dev)
        gen.manual_seed(seed + 17)

        # Replay phase, batched over all M items.
        # Each replay = one permutation of all M items, one write event each.
        # Batched form: for ARM_DIRECT we just compute W_c.addmm(vals_c.T, keys_c).
        # For ARM_STANDARD: vals_react = sign(keys_h @ W_h.T) -> P_hc -> normalize -> write.
        # For ARM_RESCUED:  vals_react = sign(sign(keys_h @ W_h.T) @ W_h.T) -> P_hc -> normalize -> write.
        for rep in range(N_REPLAY_PER_ITEM):
            perm = torch.randperm(M_ITEMS, generator=gen, device=dev)
            cues_h = keys_h[perm]                       # (M, N_h)
            cues_c = keys_c[perm]                       # (M, N_c)

            if arm_name == "ARM_DIRECT_NO_HIPPO":
                vals_c_react = vals_c[perm]             # (M, N_c)
            elif arm_name == "ARM_STANDARD_HIPPO":
                step1 = cues_h @ W_hippo.T              # (M, N_h)
                vals_react_h = torch.sign(step1)
                vals_react_h = torch.where(
                    vals_react_h == 0,
                    torch.ones_like(vals_react_h),
                    vals_react_h,
                )
                vals_c_react = _l2_normalize_batch_torch(vals_react_h @ P_hc.T)
            elif arm_name == "ARM_RESCUED_HIPPO":
                step1_raw = cues_h @ W_hippo.T          # (M, N_h)
                step1 = torch.sign(step1_raw)
                step1 = torch.where(step1 == 0, torch.ones_like(step1), step1)
                step2_raw = step1 @ W_hippo.T           # (M, N_h)
                step2 = torch.sign(step2_raw)
                step2 = torch.where(step2 == 0, torch.ones_like(step2), step2)
                vals_c_react = _l2_normalize_batch_torch(step2 @ P_hc.T)
            else:
                raise ValueError(f"unknown arm: {arm_name}")

            W_cortex.addmm_(vals_c_react.T, cues_c, alpha=ETA_CORTEX)
            n_total_writes += M_ITEMS
            emit_heartbeat(out_dir, unit_idx=rep, total_units=N_REPLAY_PER_ITEM,
                           elapsed_s=time.time() - t0,
                           extra={"phase": "replay", "arm": arm_name, "N_h": N_h,
                                  "writes_so_far": n_total_writes,
                                  "gpu_mem_mb": torch.cuda.memory_allocated(dev) / 1e6})

        W_hippo.zero_()

        # Recall test, batched.
        preds_raw = keys_c @ W_cortex.T
        preds = torch.sign(preds_raw)
        preds = torch.where(preds == 0, torch.ones_like(preds), preds)
        preds_n = _l2_normalize_batch_torch(preds)
        sims = preds_n @ vals_c.T
        argmax = sims.argmax(dim=1)
        n_hits = int((argmax == torch.arange(M_ITEMS, device=dev)).sum().item())
        recall = n_hits / float(M_ITEMS)
        cortex_norm = float(W_cortex.norm().item())

        torch.cuda.synchronize(dev)
        mem_peak = torch.cuda.max_memory_allocated(dev)
        gpu_mem_peak_mb = float((mem_peak - mem_start) / 1e6)

        del keys_raw, vals_raw, P_in, P_hc, keys_h, vals_h, keys_c, vals_c
        del W_hippo, W_cortex, preds_raw, preds, preds_n, sims, argmax
        torch.cuda.empty_cache()

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "N_h": int(N_h),
            "k_hippo_active": int(k_active),
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "cortex_norm": float(cortex_norm),
            "n_total_writes": int(n_total_writes),
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_h)),
            "alpha_hopfield": float(_alpha_h(M_ITEMS, N_h)),
            "wall_s": float(wall),
            "backend": "torch.cuda",
            "gpu_mem_peak_mb": float(gpu_mem_peak_mb),
            "arm_status": "OK",
        }
    except SystemExit:
        raise
    except Exception as exc:
        wall = time.time() - t0
        try:
            torch.cuda.empty_cache()
        except Exception:
            pass
        return {
            "arm_name": arm_name,
            "N_h": int(N_h),
            "k_hippo_active": int(k_active),
            "recall_cortex": float("nan"),
            "n_items": 0,
            "cortex_norm": float("nan"),
            "n_total_writes": 0,
            "alpha_simple": float(_alpha_simple(M_ITEMS, N_h)),
            "alpha_hopfield": float(_alpha_h(M_ITEMS, N_h)),
            "wall_s": float(wall),
            "backend": "torch.cuda",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_anatomical_separation() -> None:
    W_h = np.zeros((128, 128), dtype=np.float64)
    W_c = np.zeros((256, 256), dtype=np.float64)
    if W_h is W_c:
        raise AssertionError("W_h is W_c")
    if W_h.shape == W_c.shape:
        raise AssertionError(f"shapes match: W_h={W_h.shape} W_c={W_c.shape}")


def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_raw = 64
    N_h_test = 128
    k_test = max(1, int(round(HIPPO_SPARSITY * N_h_test)))
    P = rng.randn(N_h_test, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=N_raw).astype(np.float64)
    h = pattern_separate_sparse(x, P, k_test)
    n_active = int(np.sum(np.abs(h) > 0))
    if n_active != k_test:
        raise AssertionError(
            f"k-WTA sparsity wrong: got {n_active} active, want {k_test}"
        )


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS != [SEED_THIS_CHUNK]:
        raise AssertionError(
            f"chunk seed mismatch: SEEDS={SEEDS} != [SEED_THIS_CHUNK={SEED_THIS_CHUNK}]"
        )
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(
            f"anchor name '{ANCHOR_NAME}' does not contain seed_{SEED_THIS_CHUNK}"
        )


def _selftest_n_h_grid_distinct() -> None:
    if len(set(N_H_GRID)) != len(N_H_GRID):
        raise AssertionError(
            f"N_H_GRID has duplicate entries: {N_H_GRID}"
        )
    if not all(n > 0 for n in N_H_GRID):
        raise AssertionError(f"N_H_GRID has non-positive entry: {N_H_GRID}")
    if EXPECTED_N_UNITS != len(ARM_NAMES) * len(N_H_GRID):
        raise AssertionError(
            f"EXPECTED_N_UNITS mismatch: {EXPECTED_N_UNITS} != "
            f"{len(ARM_NAMES)} * {len(N_H_GRID)}"
        )


def _selftest_alpha_formula() -> None:
    # Spot-check the alpha_h formula at a known point.
    # M=8192 N_h=4096 -> alpha_h = 8192 / (2 * 4096 * log(4096))
    # log(4096) = 8.317766..., denom = 68134.9..., alpha_h = 0.12022...
    a = _alpha_h(8192, 4096)
    if not (0.118 < a < 0.122):
        raise AssertionError(
            f"alpha_h(8192,4096)={a:.6f} not in expected range (0.118, 0.122); "
            f"formula may have drifted"
        )


def _selftest_rescued_vs_standard_distinct_when_noisy() -> None:
    """Mini-world: at saturated regime, rescued (2-step) must differ from
    standard (1-step) on SOME inputs.  Catches the bug where the cleanup is
    a no-op (e.g. converges instantly because regime not saturated)."""
    rng = np.random.RandomState(31)
    N_h_t, M_t = 64, 256  # alpha_h = 256/(2*64*log(64)) = 0.481 (saturated)
    k_t = max(1, int(round(HIPPO_SPARSITY * N_h_t)))
    # Build a deliberately-saturated W_h.
    keys_h = np.zeros((M_t, N_h_t))
    vals_h = np.zeros((M_t, N_h_t))
    for i in range(M_t):
        idx_k = rng.choice(N_h_t, size=k_t, replace=False)
        signs_k = rng.choice([-1.0, 1.0], size=k_t)
        keys_h[i, idx_k] = signs_k
        idx_v = rng.choice(N_h_t, size=k_t, replace=False)
        signs_v = rng.choice([-1.0, 1.0], size=k_t)
        vals_h[i, idx_v] = signs_v
    W_h = vals_h.T @ keys_h  # outer-product Hebbian
    # Compare rescued vs standard readout on first 10 cues.
    n_differ = 0
    for i in range(10):
        std_out = hippo_readout_standard(W_h, keys_h[i])
        rsc_out = hippo_readout_rescued_two_step(W_h, keys_h[i])
        if not np.array_equal(std_out, rsc_out):
            n_differ += 1
    if n_differ == 0:
        raise AssertionError(
            "BUG: ARM_STANDARD and ARM_RESCUED produced bit-identical readouts on "
            "all 10 saturated-regime test cues; cleanup is a no-op (META_RULE_AF "
            "violation would occur on real cell)."
        )


def _selftest_torch_batched_matches_numpy() -> None:
    if not _TORCH_AVAILABLE:
        return
    np_rng = np.random.RandomState(3)
    M_t, Nh_t, Nc_t = 8, 16, 32
    keys_np = np_rng.randn(M_t, Nh_t).astype(np.float32)
    vals_np = np_rng.randn(M_t, Nc_t).astype(np.float32)
    eta = 0.1
    W_loop = np.zeros((Nc_t, Nh_t), dtype=np.float32)
    for i in range(M_t):
        W_loop += eta * np.outer(vals_np[i], keys_np[i])
    keys_t = torch.from_numpy(keys_np)
    vals_t = torch.from_numpy(vals_np)
    W_matmul = (vals_t.T @ keys_t) * eta
    diff = float((torch.from_numpy(W_loop) - W_matmul).abs().max().item())
    if diff > 1e-3:
        raise AssertionError(
            f"torch batched Hebbian matmul diverges from numpy loop: maxdiff={diff}"
        )


def _selftest_positive_control_small() -> None:
    """Positive control: at small M=200 / N_h=256 (sub-capacity alpha_h~0.07),
    ARM_DIRECT_NO_HIPPO must reproduce HIGH recall (>= 0.95).  Catches bugs
    in the encode + write + recall pipeline.
    """
    rng = np.random.RandomState(57)
    N_raw = 32
    N_h_t, N_c_t, M_t = 256, 512, 200
    k_t = max(1, int(round(HIPPO_SPARSITY * N_h_t)))
    eta = 0.05

    P_in = rng.randn(N_h_t, N_raw).astype(np.float64) / np.sqrt(N_raw)
    P_hc = rng.randn(N_c_t, N_h_t).astype(np.float64) / np.sqrt(N_h_t)
    keys_raw = rng.choice([-1.0, 1.0], size=(M_t, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(M_t, N_raw)).astype(np.float64)

    keys_h_t = np.zeros((M_t, N_h_t), dtype=np.float64)
    vals_h_t = np.zeros((M_t, N_h_t), dtype=np.float64)
    keys_c_t = np.zeros((M_t, N_c_t), dtype=np.float64)
    vals_c_t = np.zeros((M_t, N_c_t), dtype=np.float64)
    for i in range(M_t):
        keys_h_t[i] = pattern_separate_sparse(keys_raw[i], P_in, k_t)
        vals_h_t[i] = pattern_separate_sparse(vals_raw[i], P_in, k_t)
        keys_c_t[i] = _l2_normalize(P_hc @ keys_h_t[i])
        vals_c_t[i] = _l2_normalize(P_hc @ vals_h_t[i])

    W_c = np.zeros((N_c_t, N_c_t), dtype=np.float64)
    # DIRECT writes only.
    for i in range(M_t):
        W_c += eta * np.outer(vals_c_t[i], keys_c_t[i])

    # Recall.
    n_hits = 0
    for i in range(M_t):
        raw = W_c @ keys_c_t[i]
        out = np.sign(raw); out[out == 0] = 1.0
        n_p = float(np.linalg.norm(out))
        if n_p == 0:
            continue
        out_n = out / n_p
        sims = vals_c_t @ out_n
        if int(np.argmax(sims)) == i:
            n_hits += 1
    recall = n_hits / float(M_t)
    if recall < 0.95:
        raise AssertionError(
            f"POSITIVE CONTROL FAIL: DIRECT at M={M_t} N_h={N_h_t} N_c={N_c_t} "
            f"(sub-capacity) returned recall={recall:.3f}; expected >= 0.95. "
            f"Encode/write/recall pipeline may be broken."
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_anatomical_separation()
        _selftest_sparse_pattern_separator()
        _selftest_chunk_seed_matches_anchor()
        _selftest_n_h_grid_distinct()
        _selftest_alpha_formula()
        _selftest_rescued_vs_standard_distinct_when_noisy()
        _selftest_torch_batched_matches_numpy()
        _selftest_positive_control_small()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    print(
        f"[selftest] PASS  M={M_ITEMS}  N_c={N_CORTEX}  "
        f"N_h_grid={N_H_GRID}  sparsity={HIPPO_SPARSITY}  "
        f"n_replay_per_item={N_REPLAY_PER_ITEM}  eta_c={ETA_CORTEX}  "
        f"expected_n_units={EXPECTED_N_UNITS}  mode={RUN_MODE}  "
        f"chunk_seed={SEED_THIS_CHUNK}  backend={COMPUTE_BACKEND}  "
        f"torch={_TORCH_AVAILABLE}  cuda={_CUDA_AVAILABLE}  "
        f"v1_hippo_capacity_rescue=YES",
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
    keys_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)
    vals_raw = rng.choice([-1.0, 1.0], size=(M_ITEMS, N_raw)).astype(np.float64)

    print(f"  [seed={seed}] M={M_ITEMS} N_c={N_CORTEX} "
          f"N_h_grid={N_H_GRID} arms={list(ARM_NAMES)} "
          f"backend={COMPUTE_BACKEND} hippo_capacity_rescue_v1",
          flush=True)

    arms = []
    for N_h in N_H_GRID:
        # Per-N_h projection matrices (seed-stable).
        rng_nh = np.random.RandomState(seed + 1000 + N_h)
        P_in_nh = rng_nh.randn(N_h, N_raw).astype(np.float64) / np.sqrt(N_raw)
        P_hc_nh = rng_nh.randn(N_CORTEX, N_h).astype(np.float64) / np.sqrt(N_h)

        for arm_name in ARM_NAMES:
            if USE_TORCH_CUDA:
                out = run_arm_torch_cuda(arm_name, N_h, seed,
                                         keys_raw, vals_raw,
                                         P_in_nh, P_hc_nh, out_dir)
            else:
                out = run_arm_numpy(arm_name, N_h, seed,
                                    keys_raw, vals_raw,
                                    P_in_nh, P_hc_nh, out_dir)
            arms.append(out)
            print(
                f"  [seed={seed} N_h={N_h:>5d} {arm_name}] "
                f"recall={out['recall_cortex']:.3f} "
                f"alpha_h={out['alpha_hopfield']:.4f} "
                f"writes={out['n_total_writes']} "
                f"cortex_norm={out['cortex_norm']:.2e} "
                f"backend={out['backend']} "
                f"gpu_mem_peak_mb={out['gpu_mem_peak_mb']:.1f} "
                f"status={out['arm_status']} "
                f"wall={out['wall_s']:.1f}s",
                flush=True,
            )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_CORTEX,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "N_h_grid": list(N_H_GRID),
        "n_arms_per_nh": len(ARM_NAMES),
        "eta_c": ETA_CORTEX,
        "hippo_sparsity": HIPPO_SPARSITY,
        "n_replay_per_item": N_REPLAY_PER_ITEM,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "chunk_seed": SEED_THIS_CHUNK,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _find_arm(arms: List[Dict], name: str, N_h: int) -> Dict:
    for a in arms:
        if a["arm_name"] == name and int(a["N_h"]) == int(N_h):
            return a
    raise KeyError(f"arm name={name} N_h={N_h} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    if len(results) != 1:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    n_arms = len(r["arms"])
    if n_arms != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected {EXPECTED_N_UNITS} units "
                f"(arms x N_h), got {n_arms}")
    for a in r["arms"]:
        if a["arm_status"] != "OK":
            return ("HARD_FAIL",
                    f"Arm {a['arm_name']} N_h={a['N_h']} error: {a['arm_status']}")

    # Per-N_h: compute gap (DIRECT - STANDARD), (DIRECT - RESCUED),
    # rescued_closes_fraction.
    per_nh_rows = []
    best_close_frac = -1e18
    best_close_nh = None
    any_discriminator_fired = False
    any_meta_rule_af_violation = False
    for N_h in N_H_GRID:
        a_direct = _find_arm(r["arms"], "ARM_DIRECT_NO_HIPPO", N_h)
        a_std = _find_arm(r["arms"], "ARM_STANDARD_HIPPO", N_h)
        a_rsc = _find_arm(r["arms"], "ARM_RESCUED_HIPPO", N_h)
        direct = float(a_direct["recall_cortex"])
        standard = float(a_std["recall_cortex"])
        rescued = float(a_rsc["recall_cortex"])
        gap_dir_std = direct - standard
        gap_dir_rsc = direct - rescued
        if abs(gap_dir_std) > DIRECT_VS_STANDARD_GAP_MIN_FOR_DISCRIM:
            any_discriminator_fired = True
        # rescued_closes_fraction: how much of the (direct - standard) gap
        # is closed by the rescued readout.  +1.0 = perfect close; 0.0 = no
        # help; negative = rescued HURTS.  Guard against tiny gap_dir_std.
        if abs(gap_dir_std) >= 1e-6:
            close_frac = (gap_dir_std - gap_dir_rsc) / gap_dir_std
        else:
            close_frac = 0.0
        # META_RULE_AF (bit-exact) check.
        if abs(standard - rescued) < 1e-6 and abs(standard - direct) > 1e-3:
            any_meta_rule_af_violation = True
        per_nh_rows.append({
            "N_h": int(N_h),
            "direct": direct,
            "standard": standard,
            "rescued": rescued,
            "gap_direct_minus_standard": gap_dir_std,
            "gap_direct_minus_rescued": gap_dir_rsc,
            "rescued_closes_fraction": close_frac,
            "alpha_hopfield": float(a_direct["alpha_hopfield"]),
        })
        if close_frac > best_close_frac:
            best_close_frac = close_frac
            best_close_nh = int(N_h)

    summary = "; ".join(
        f"N_h={row['N_h']}: D={row['direct']:.3f}/S={row['standard']:.3f}/"
        f"R={row['rescued']:.3f} closeFrac={row['rescued_closes_fraction']:+.3f}"
        for row in per_nh_rows
    )
    summary_full = (
        f"seed={SEED_THIS_CHUNK} M={M_ITEMS} N_c={N_CORTEX} "
        f"best_close_frac={best_close_frac:+.3f} at N_h={best_close_nh}; "
        f"{summary}"
    )

    # Hard-fail gates.
    if any_meta_rule_af_violation:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: at some N_h, STANDARD and RESCUED "
                f"bit-identical (< 1e-6) while DIFFERING from DIRECT -- "
                f"cleanup mechanism is a no-op. {summary_full}")

    if not any_discriminator_fired:
        return ("MIDDLE_BAND",
                f"INCONCLUSIVE: no N_h had |DIRECT-STANDARD| > "
                f"{DIRECT_VS_STANDARD_GAP_MIN_FOR_DISCRIM} -- the readout "
                f"bottleneck is not the failure mode in this regime, so the "
                f"rescue hypothesis cannot be tested.  {summary_full}")

    # MAJOR_UNLOCK detection.
    major_unlock = best_close_frac >= RESCUE_CLOSES_FRAC_MAJOR_UNLOCK
    unlock_tag = " ***MAJOR_UNLOCK_POTENTIAL***" if major_unlock else ""

    # HARD_PASS criteria for a DIAGNOSTIC PROBE:
    # - discriminator fired (above)
    # - rescued closes >= RESCUE_CLOSES_FRAC_HARD_PASS at SOME N_h
    if best_close_frac >= RESCUE_CLOSES_FRAC_HARD_PASS:
        return ("HARD_PASS",
                f"HARD_PASS (diagnostic): rescued closes "
                f">= {RESCUE_CLOSES_FRAC_HARD_PASS} of DIRECT-STANDARD gap at "
                f"N_h={best_close_nh}.{unlock_tag} {summary_full}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND (diagnostic): discriminator fired but rescued does "
            f"not meaningfully close the gap (best close_frac={best_close_frac:+.3f} "
            f"< {RESCUE_CLOSES_FRAC_HARD_PASS} at N_h={best_close_nh}). "
            f"Honest diagnostic: 2-step cleanup is insufficient.{unlock_tag} "
            f"{summary_full}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    start_marker = out_dir / "_start_marker.txt"
    start_marker.write_text(
        f"start_ts_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
        f"anchor={ANCHOR_NAME} run_mode={RUN_MODE} "
        f"backend={COMPUTE_BACKEND} torch={_TORCH_AVAILABLE} cuda={_CUDA_AVAILABLE} "
        f"v1_hippo_capacity_rescue=YES",
        encoding="utf-8",
    )

    run_config = {
        "N": N_CORTEX,
        "M": M_ITEMS,
        "run_mode": RUN_MODE,
        "anchor": ANCHOR_NAME,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; "
        f"running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME} M={M_ITEMS} N_c={N_CORTEX} "
              f"N_h_grid={N_H_GRID} mode={RUN_MODE} backend={COMPUTE_BACKEND}...",
              flush=True)
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except Exception as exc:
            (out_dir / "fatal.log").write_text(
                f"FATAL during seed={seed}: {type(exc).__name__}: {exc}\n",
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

    # Compose per-N_h diagnostic rows for the metrics output (cell-author cert
    # trail; downstream landed-VET reads these).
    per_nh_rows: List[Dict] = []
    if all_results and len(all_results[0].get("arms", [])) == EXPECTED_N_UNITS:
        r = all_results[0]
        for N_h in N_H_GRID:
            try:
                a_direct = _find_arm(r["arms"], "ARM_DIRECT_NO_HIPPO", N_h)
                a_std = _find_arm(r["arms"], "ARM_STANDARD_HIPPO", N_h)
                a_rsc = _find_arm(r["arms"], "ARM_RESCUED_HIPPO", N_h)
                direct = float(a_direct["recall_cortex"])
                standard = float(a_std["recall_cortex"])
                rescued = float(a_rsc["recall_cortex"])
                gap_dir_std = direct - standard
                gap_dir_rsc = direct - rescued
                close_frac = (
                    (gap_dir_std - gap_dir_rsc) / gap_dir_std
                    if abs(gap_dir_std) >= 1e-6 else 0.0
                )
                per_nh_rows.append({
                    "N_h": int(N_h),
                    "direct": direct,
                    "standard": standard,
                    "rescued": rescued,
                    "gap_direct_minus_standard": gap_dir_std,
                    "gap_direct_minus_rescued": gap_dir_rsc,
                    "rescued_closes_fraction": close_frac,
                    "alpha_hopfield": float(a_direct["alpha_hopfield"]),
                    "alpha_simple": float(a_direct["alpha_simple"]),
                })
            except KeyError:
                continue

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"M={M_ITEMS} N_c={N_CORTEX} N_h_grid={N_H_GRID} "
            f"mode={RUN_MODE} backend={COMPUTE_BACKEND} "
            f"hippo_capacity_rescue_v1"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "M": M_ITEMS,
        "N_c": N_CORTEX,
        "N_h_grid": list(N_H_GRID),
        "eta_c": ETA_CORTEX,
        "hippo_sparsity": HIPPO_SPARSITY,
        "n_replay_per_item": N_REPLAY_PER_ITEM,
        "backend": COMPUTE_BACKEND,
        "torch_available": _TORCH_AVAILABLE,
        "cuda_available": _CUDA_AVAILABLE,
        "n_seeds": len(SEEDS),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (
            len(all_results) == 1
            and len(all_results[0].get("arms", [])) == EXPECTED_N_UNITS
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
        "per_nh_rows": per_nh_rows,
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


if __name__ == "__main__":
    _main()
