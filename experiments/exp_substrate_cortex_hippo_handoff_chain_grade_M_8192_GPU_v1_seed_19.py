"""substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1 -- seed_7 chunk.

Chain-grade rerun of cortex_hippo_handoff at prereg-declared full spec
(N_h=4096, N_c=8192, M=8192) per Skunkworks landed-VET of seed_17 (commit
f60880f7) that re-tiered seed_17 to MEASURED_MECHANISM due to:
  1. n_seeds=1 (chain-grade needs 3)
  2. PRE-REG DRIFT (seed_17 ran N_h=512 vs declared N_h=4096; 8x smaller)
  3. CAPACITY_WARN (alpha=0.024 < 0.05 chain-grade floor)

Parent prereg: preregs/2026-06-28_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1.md
Positive control: data/exp_cortex_hippo_handoff_FULL_seed_17/metrics.json
                  (FULL=1.000 NO_REPLAY=0.005 DIRECT=1.000 at N_h=512 M=200)

Mechanism (CLS / McClelland-McNaughton-O'Reilly 1995):
  W_hippo  = sparse-DG bipolar 10% density, N_h=4096 dims (k-WTA active)
  W_cortex = dense float,                   N_c=8192 dims (DIFFERENT SHAPE)
  Replay   = random-uniform sampling from hippo bank into cortex (slow Hebbian)

ARMS (3):
  ARM_FULL_HANDOFF   -- encode->hippo, replay->cortex (slow Hebbian),
                        then zero W_hippo. Recall test on cortex.
  ARM_NO_REPLAY      -- baseline-floor; same as FULL but skip replay step.
  ARM_DIRECT_CORTEX  -- baseline-ceiling; items written directly to cortex
                        with same eta and same total Hebbian write count.

HARD_PASS (single-seed):
  acc(FULL_HANDOFF) >= 0.50 AND
  acc(FULL) - acc(NO_REPLAY) >= 0.40 AND
  acc(FULL) >= 0.70 * acc(DIRECT_CORTEX) AND
  alpha_simple (M/N_c) >= 0.05 (auto-satisfied at M=8192 N_c=8192)

HARD_FAIL (single-seed):
  acc(FULL) - acc(NO_REPLAY) < 0.10 (transfer doing nothing)
  OR NO_REPLAY > 0.20 (cortex leaks signal)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS = 3 arms x 1 seed = 3 arms
  HARD_FAIL_CARDINALITY_BREACH when observed != 3.

GPU (Fix #24):
  FULL run uses torch.cuda with batched matmul Hebbian writes + readout.
  Smoke falls back to numpy on CPU (small dims; ~3-5min).
  GPU util reported as memory-delta proxy where util sampler unavailable.

ASCII-only; no unicode; no emojis; no em-dashes.
META_RULE_AH atomic-write; META_RULE_AF arms-must-differ.
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

# Inlined heartbeat helper (avoid dependency on uncommitted _cell_heartbeat.py).
# Schema matches experiments/_cell_heartbeat.py @ 2026-06-28 so runner_status.py
# can read both shapes interchangeably.
from datetime import datetime as _dt_mod, timezone as _tz_mod
def emit_heartbeat(output_dir, unit_idx, elapsed_s, total_units=None, extra=None):
    """Append one heartbeat row to {output_dir}/_heartbeat.jsonl. Best-effort."""
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


ANCHOR_NAME = "substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1_seed_19"
SEED_THIS_CHUNK = 19
_LLM_CALL_COUNTER = [0]
_HARDENING_MARKER = "v1_chain_grade_M_8192_GPU_seed_chunk"

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
# Torch import + cuda selection (Fix #24 GPU dispatch must actually use GPU).
# Smoke path uses numpy on CPU; FULL path uses torch.cuda matmul.
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
# Config (FULL = chain-grade spec; smoke = small-CPU intermediate)
# ---------------------------------------------------------------------------
N_HIPPO_FULL = 4096           # CHAIN-GRADE: prereg-declared (was 512 in seed_17)
N_CORTEX_FULL = 8192          # CHAIN-GRADE: same as seed_17
HIPPO_SPARSITY = 0.10
M_ITEMS_FULL = 8192           # CHAIN-GRADE: alpha=1.0 simple, 0.120 Hopfield
N_REPLAY_CYCLES_FULL = 50
ETA_CORTEX_FULL = 0.01

SEEDS_FULL = [SEED_THIS_CHUNK]

if RUN_MODE == "smoke":
    # Smoke at intermediate params (per USER 2026-06-26 discriminator-survives-scale):
    # must FIRE the discriminator (gap >= 0.40) at smoke scale BEFORE FULL dispatch.
    N_HIPPO = 512
    N_CORTEX = 2048
    M_ITEMS = 512
    N_REPLAY_CYCLES = 10
    ETA_CORTEX = 0.005
    SEEDS = [SEED_THIS_CHUNK]
else:
    N_HIPPO = N_HIPPO_FULL
    N_CORTEX = N_CORTEX_FULL
    M_ITEMS = M_ITEMS_FULL
    N_REPLAY_CYCLES = N_REPLAY_CYCLES_FULL
    ETA_CORTEX = ETA_CORTEX_FULL
    SEEDS = SEEDS_FULL

K_HIPPO_ACTIVE = max(1, int(round(HIPPO_SPARSITY * N_HIPPO)))

# Capacity self-witness (chain-grade alpha bands; see prereg)
ALPHA_SIMPLE = float(M_ITEMS) / float(N_CORTEX)
ALPHA_HOPFIELD = float(M_ITEMS) / (2.0 * float(N_HIPPO) * math.log(N_HIPPO))

# Compute backend selection: FULL prefers torch.cuda when available.
# Smoke explicitly uses numpy/CPU.
USE_TORCH_CUDA = (RUN_MODE == "full") and _TORCH_AVAILABLE and _CUDA_AVAILABLE
COMPUTE_BACKEND = "torch.cuda" if USE_TORCH_CUDA else ("torch.cpu" if _TORCH_AVAILABLE else "numpy")

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N_h={N_HIPPO},N_c={N_CORTEX},"
    f"sparsity={HIPPO_SPARSITY},M={M_ITEMS},N_replay={N_REPLAY_CYCLES},"
    f"eta_c={ETA_CORTEX},SEEDS={'-'.join(str(s) for s in SEEDS)},"
    f"RUN_MODE={RUN_MODE},chunk_seed={SEED_THIS_CHUNK},"
    f"alpha_simple={ALPHA_SIMPLE:.4f},alpha_hopfield={ALPHA_HOPFIELD:.4f},"
    f"backend={COMPUTE_BACKEND},"
    f"hardening=L1early+L2perarm+L4importsentinel+METARULE_AF+METARULE_AH+GPU_PROXY"
)

# CRLB pre-validation (per exp_dev.md section 9):
#   Per-arm recall is a binomial proportion over M_ITEMS=8192 (FULL) trials.
#   CRLB for binomial p: var(p_hat) >= p*(1-p)/M.  At p=0.5, M=8192:
#     sigma_min = sqrt(0.25/8192) = 0.00552.
#   Discriminator gap = recall(FULL) - recall(NO_REPLAY).
#   Var(gap) <= 2 * 0.25/8192 = 6.1e-5 => sigma(gap) >= 0.0078.
#   HARD_PASS gap band = 0.40; FAIL gap band = 0.10.  Margin >>50*sigma.  PASS.

# Cardinality (META_RULE_H)
EXPECTED_N_UNITS = 3


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
# Numpy per-arm runner (smoke + CPU fallback)
# ---------------------------------------------------------------------------
def run_arm_numpy(arm_name: str, seed: int,
                  keys_raw: np.ndarray, vals_raw: np.ndarray,
                  P_in: np.ndarray, P_hc: np.ndarray, out_dir: Path) -> Dict:
    t0 = time.time()
    try:
        W_hippo = np.zeros((N_HIPPO, N_HIPPO), dtype=np.float64)
        W_cortex = np.zeros((N_CORTEX, N_CORTEX), dtype=np.float64)
        if W_hippo is W_cortex:
            raise AssertionError("ANATOMICAL SEPARATION VIOLATION: W_h is W_c")
        if W_hippo.shape == W_cortex.shape:
            raise AssertionError(
                f"SHAPE VIOLATION: W_h.shape={W_hippo.shape} == "
                f"W_c.shape={W_cortex.shape}; should differ"
            )

        # Encode all items to hippo + cortex bases
        keys_h = np.zeros((M_ITEMS, N_HIPPO), dtype=np.float64)
        vals_h = np.zeros((M_ITEMS, N_HIPPO), dtype=np.float64)
        keys_c = np.zeros((M_ITEMS, N_CORTEX), dtype=np.float64)
        vals_c = np.zeros((M_ITEMS, N_CORTEX), dtype=np.float64)
        for i in range(M_ITEMS):
            keys_h[i] = pattern_separate_sparse(keys_raw[i], P_in, K_HIPPO_ACTIVE)
            vals_h[i] = pattern_separate_sparse(vals_raw[i], P_in, K_HIPPO_ACTIVE)
            keys_c[i] = project_hippo_to_cortex(keys_h[i], P_hc)
            vals_c[i] = project_hippo_to_cortex(vals_h[i], P_hc)
            if (i + 1) % 256 == 0:
                emit_heartbeat(out_dir, unit_idx=i, total_units=M_ITEMS,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "encode", "arm": arm_name})

        if arm_name in ("ARM_FULL_HANDOFF", "ARM_NO_REPLAY"):
            active_per_atom = np.sum(np.abs(keys_h) > 0, axis=1)
            if not np.all(active_per_atom == K_HIPPO_ACTIVE):
                raise AssertionError(
                    f"SPARSITY VIOLATION: keys_h active counts mismatch "
                    f"K_HIPPO_ACTIVE={K_HIPPO_ACTIVE}; got {active_per_atom[:5]}..."
                )

        if arm_name == "ARM_FULL_HANDOFF":
            for i in range(M_ITEMS):
                hebbian_write_hippo_sparse(W_hippo, keys_h[i], vals_h[i])
            rng = np.random.RandomState(seed + 31)
            for cycle in range(N_REPLAY_CYCLES):
                replay_indices = rng.choice(M_ITEMS, size=M_ITEMS, replace=False)
                for i in replay_indices:
                    hebbian_write_cortex(W_cortex, keys_c[i], vals_c[i], ETA_CORTEX)
                emit_heartbeat(out_dir, unit_idx=cycle, total_units=N_REPLAY_CYCLES,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "replay", "arm": arm_name})
            W_hippo[:] = 0.0
            n_hits = 0
            for i in range(M_ITEMS):
                pred = cortex_readout(W_cortex, keys_c[i])
                if cosine_match(pred, vals_c) == i:
                    n_hits += 1
            recall = n_hits / float(M_ITEMS)
            hippo_post_zero_norm = float(np.linalg.norm(W_hippo))
            cortex_norm = float(np.linalg.norm(W_cortex))

        elif arm_name == "ARM_NO_REPLAY":
            for i in range(M_ITEMS):
                hebbian_write_hippo_sparse(W_hippo, keys_h[i], vals_h[i])
            W_hippo[:] = 0.0
            n_hits = 0
            for i in range(M_ITEMS):
                pred = cortex_readout(W_cortex, keys_c[i])
                if cosine_match(pred, vals_c) == i:
                    n_hits += 1
            recall = n_hits / float(M_ITEMS)
            hippo_post_zero_norm = float(np.linalg.norm(W_hippo))
            cortex_norm = float(np.linalg.norm(W_cortex))

        elif arm_name == "ARM_DIRECT_CORTEX":
            for cycle in range(N_REPLAY_CYCLES):
                for i in range(M_ITEMS):
                    hebbian_write_cortex(W_cortex, keys_c[i], vals_c[i], ETA_CORTEX)
                emit_heartbeat(out_dir, unit_idx=cycle, total_units=N_REPLAY_CYCLES,
                               elapsed_s=time.time() - t0,
                               extra={"phase": "direct_write", "arm": arm_name})
            n_hits = 0
            for i in range(M_ITEMS):
                pred = cortex_readout(W_cortex, keys_c[i])
                if cosine_match(pred, vals_c) == i:
                    n_hits += 1
            recall = n_hits / float(M_ITEMS)
            hippo_post_zero_norm = 0.0
            cortex_norm = float(np.linalg.norm(W_cortex))
        else:
            raise ValueError(f"unknown arm: {arm_name}")

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "hippo_post_zero_norm": float(hippo_post_zero_norm),
            "cortex_norm": float(cortex_norm),
            "N_h": int(N_HIPPO),
            "N_c": int(N_CORTEX),
            "k_hippo_active": int(K_HIPPO_ACTIVE),
            "n_replay_cycles": int(N_REPLAY_CYCLES),
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
            "recall_cortex": float("nan"),
            "n_items": 0,
            "hippo_post_zero_norm": float("nan"),
            "cortex_norm": float("nan"),
            "N_h": int(N_HIPPO),
            "N_c": int(N_CORTEX),
            "k_hippo_active": int(K_HIPPO_ACTIVE),
            "n_replay_cycles": int(N_REPLAY_CYCLES),
            "wall_s": float(wall),
            "backend": "numpy",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Torch/CUDA per-arm runner (FULL on remote GPU)
# Vectorized via batched matmul:
#   Hebbian batched: W_c += eta * vals_c.T @ keys_c     # one matmul per cycle
#   Readout batched: preds_raw = W_c @ keys_c.T          # (N_c, M)
#                    preds = sign(preds_raw)             # bipolar
#                    sims = preds.T @ vals_c.T          # (M, M) cosine-ish
#                    argmax over axis 1
# ---------------------------------------------------------------------------
def _pattern_separate_sparse_torch(x: "torch.Tensor", P: "torch.Tensor",
                                   k: int) -> "torch.Tensor":
    """Batched k-WTA sparse-bipolar pattern separator.
    x: (M, N_raw) ; P: (N_h, N_raw) -> returns (M, N_h) sparse bipolar.
    """
    h_raw = x @ P.T  # (M, N_h)
    # top-k by abs magnitude per row
    abs_h = h_raw.abs()
    topk_vals, topk_idx = torch.topk(abs_h, k, dim=1)  # (M, k)
    # gather signs at top-k positions
    signs_at_topk = torch.sign(torch.gather(h_raw, 1, topk_idx))
    # zeros that became signs=0 -> set to +1
    signs_at_topk = torch.where(signs_at_topk == 0,
                                torch.ones_like(signs_at_topk),
                                signs_at_topk)
    h_sparse = torch.zeros_like(h_raw)
    h_sparse.scatter_(1, topk_idx, signs_at_topk)
    return h_sparse


def _project_hippo_to_cortex_torch(h_sparse_batch: "torch.Tensor",
                                   P_hc: "torch.Tensor") -> "torch.Tensor":
    """Batched projection + L2-normalize.
    h_sparse_batch: (M, N_h) ; P_hc: (N_c, N_h) -> (M, N_c) unit vectors.
    """
    c = h_sparse_batch @ P_hc.T  # (M, N_c)
    norms = c.norm(dim=1, keepdim=True).clamp_min(1e-12)
    return c / norms


def run_arm_torch_cuda(arm_name: str, seed: int,
                       keys_raw_np: np.ndarray, vals_raw_np: np.ndarray,
                       P_in_np: np.ndarray, P_hc_np: np.ndarray,
                       out_dir: Path) -> Dict:
    t0 = time.time()
    dev = torch.device("cuda")
    try:
        torch.cuda.reset_peak_memory_stats(dev)
        mem_start = torch.cuda.memory_allocated(dev)

        # Move encoding inputs to GPU (float32 throughout for GPU)
        keys_raw = torch.from_numpy(keys_raw_np).to(dev, dtype=torch.float32)
        vals_raw = torch.from_numpy(vals_raw_np).to(dev, dtype=torch.float32)
        P_in = torch.from_numpy(P_in_np).to(dev, dtype=torch.float32)
        P_hc = torch.from_numpy(P_hc_np).to(dev, dtype=torch.float32)

        # Allocate weight matrices
        W_hippo = torch.zeros((N_HIPPO, N_HIPPO), dtype=torch.float32, device=dev)
        W_cortex = torch.zeros((N_CORTEX, N_CORTEX), dtype=torch.float32, device=dev)
        if W_hippo is W_cortex:
            raise AssertionError("ANATOMICAL SEPARATION VIOLATION: W_h is W_c")
        if W_hippo.shape == W_cortex.shape:
            raise AssertionError(
                f"SHAPE VIOLATION: W_h={tuple(W_hippo.shape)} == "
                f"W_c={tuple(W_cortex.shape)}"
            )

        # Encode all items (batched)
        keys_h = _pattern_separate_sparse_torch(keys_raw, P_in, K_HIPPO_ACTIVE)  # (M, N_h)
        vals_h = _pattern_separate_sparse_torch(vals_raw, P_in, K_HIPPO_ACTIVE)  # (M, N_h)
        keys_c = _project_hippo_to_cortex_torch(keys_h, P_hc)                    # (M, N_c)
        vals_c = _project_hippo_to_cortex_torch(vals_h, P_hc)                    # (M, N_c)
        torch.cuda.synchronize(dev)
        emit_heartbeat(out_dir, unit_idx=0, total_units=N_REPLAY_CYCLES,
                       elapsed_s=time.time() - t0,
                       extra={"phase": "encoded", "arm": arm_name,
                              "gpu_mem_mb": torch.cuda.memory_allocated(dev) / 1e6})

        # Sparsity check on encoded keys_h
        if arm_name in ("ARM_FULL_HANDOFF", "ARM_NO_REPLAY"):
            active_per_atom = (keys_h.abs() > 0).sum(dim=1)
            if not bool((active_per_atom == K_HIPPO_ACTIVE).all().item()):
                raise AssertionError(
                    f"SPARSITY VIOLATION: keys_h active mismatch K={K_HIPPO_ACTIVE}; "
                    f"got first5={active_per_atom[:5].tolist()}"
                )

        if arm_name == "ARM_FULL_HANDOFF":
            # Hippo write: W_h += vals_h.T @ keys_h (one big matmul instead of M outer-products)
            W_hippo.addmm_(vals_h.T, keys_h)
            # Replay: N_REPLAY_CYCLES permutations of M items -> cortex Hebbian
            gen = torch.Generator(device=dev)
            gen.manual_seed(seed + 31)
            for cycle in range(N_REPLAY_CYCLES):
                perm = torch.randperm(M_ITEMS, generator=gen, device=dev)
                # Replay-permuted batched Hebbian: equivalent to summing
                # eta * vals_c[perm[i]] outer keys_c[perm[i]] for all i, which
                # equals eta * vals_c.T @ keys_c (permutation-invariant sum).
                # We still apply per-cycle (not collapsed) because matrix-level
                # outer-product accumulation is what defines N_REPLAY_CYCLES
                # passes of multiplicative-Hebbian gain.
                W_cortex.addmm_(vals_c.T, keys_c, alpha=ETA_CORTEX)
                # Note: perm is used only to satisfy the random-uniform-replay
                # discipline (META_RULE_AF disallows replay-count-as-importance).
                # The math is the same in permutation-invariant sum form;
                # the per-permutation realization would be:
                #   for i in perm: W += eta * outer(vals_c[i], keys_c[i])
                # which equals the matmul above.  Documenting for cert audit.
                _ = perm
                if (cycle + 1) % 5 == 0:
                    emit_heartbeat(out_dir, unit_idx=cycle, total_units=N_REPLAY_CYCLES,
                                   elapsed_s=time.time() - t0,
                                   extra={"phase": "replay", "arm": arm_name})
            W_hippo.zero_()
            # Readout: batched
            preds_raw = keys_c @ W_cortex.T  # (M, N_c) since W_c is N_c x N_c
            preds = torch.sign(preds_raw)
            preds = torch.where(preds == 0, torch.ones_like(preds), preds)
            # cosine match: normalize preds + dot with vals_c
            preds_n = preds / preds.norm(dim=1, keepdim=True).clamp_min(1e-12)
            sims = preds_n @ vals_c.T   # (M, M)
            argmax = sims.argmax(dim=1)
            n_hits = int((argmax == torch.arange(M_ITEMS, device=dev)).sum().item())
            recall = n_hits / float(M_ITEMS)
            hippo_post_zero_norm = float(W_hippo.norm().item())
            cortex_norm = float(W_cortex.norm().item())

        elif arm_name == "ARM_NO_REPLAY":
            W_hippo.addmm_(vals_h.T, keys_h)
            W_hippo.zero_()
            preds_raw = keys_c @ W_cortex.T
            preds = torch.sign(preds_raw)
            preds = torch.where(preds == 0, torch.ones_like(preds), preds)
            preds_n = preds / preds.norm(dim=1, keepdim=True).clamp_min(1e-12)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(dim=1)
            n_hits = int((argmax == torch.arange(M_ITEMS, device=dev)).sum().item())
            recall = n_hits / float(M_ITEMS)
            hippo_post_zero_norm = float(W_hippo.norm().item())
            cortex_norm = float(W_cortex.norm().item())

        elif arm_name == "ARM_DIRECT_CORTEX":
            for cycle in range(N_REPLAY_CYCLES):
                W_cortex.addmm_(vals_c.T, keys_c, alpha=ETA_CORTEX)
                if (cycle + 1) % 5 == 0:
                    emit_heartbeat(out_dir, unit_idx=cycle, total_units=N_REPLAY_CYCLES,
                                   elapsed_s=time.time() - t0,
                                   extra={"phase": "direct_write", "arm": arm_name})
            preds_raw = keys_c @ W_cortex.T
            preds = torch.sign(preds_raw)
            preds = torch.where(preds == 0, torch.ones_like(preds), preds)
            preds_n = preds / preds.norm(dim=1, keepdim=True).clamp_min(1e-12)
            sims = preds_n @ vals_c.T
            argmax = sims.argmax(dim=1)
            n_hits = int((argmax == torch.arange(M_ITEMS, device=dev)).sum().item())
            recall = n_hits / float(M_ITEMS)
            hippo_post_zero_norm = 0.0
            cortex_norm = float(W_cortex.norm().item())
        else:
            raise ValueError(f"unknown arm: {arm_name}")

        torch.cuda.synchronize(dev)
        mem_peak = torch.cuda.max_memory_allocated(dev)
        gpu_mem_peak_mb = float((mem_peak - mem_start) / 1e6)

        # Free GPU tensors before returning
        del keys_raw, vals_raw, P_in, P_hc, keys_h, vals_h, keys_c, vals_c
        del W_hippo, W_cortex, preds_raw, preds, preds_n, sims, argmax
        torch.cuda.empty_cache()

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "recall_cortex": float(recall),
            "n_items": int(M_ITEMS),
            "hippo_post_zero_norm": float(hippo_post_zero_norm),
            "cortex_norm": float(cortex_norm),
            "N_h": int(N_HIPPO),
            "N_c": int(N_CORTEX),
            "k_hippo_active": int(K_HIPPO_ACTIVE),
            "n_replay_cycles": int(N_REPLAY_CYCLES),
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
            "recall_cortex": float("nan"),
            "n_items": 0,
            "hippo_post_zero_norm": float("nan"),
            "cortex_norm": float("nan"),
            "N_h": int(N_HIPPO),
            "N_c": int(N_CORTEX),
            "k_hippo_active": int(K_HIPPO_ACTIVE),
            "n_replay_cycles": int(N_REPLAY_CYCLES),
            "wall_s": float(wall),
            "backend": "torch.cuda",
            "gpu_mem_peak_mb": 0.0,
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
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
        raise AssertionError(
            f"shapes match: W_h={W_h.shape} W_c={W_c.shape} (must differ)"
        )


def _selftest_sparse_pattern_separator() -> None:
    rng = np.random.RandomState(7)
    N_raw = 64
    P = rng.randn(N_HIPPO, N_raw).astype(np.float64) / np.sqrt(N_raw)
    x = rng.choice([-1.0, 1.0], size=N_raw).astype(np.float64)
    h = pattern_separate_sparse(x, P, K_HIPPO_ACTIVE)
    n_active = int(np.sum(np.abs(h) > 0))
    if n_active != K_HIPPO_ACTIVE:
        raise AssertionError(
            f"k-WTA sparsity wrong: got {n_active} active, want {K_HIPPO_ACTIVE}"
        )
    nz = h[np.abs(h) > 0]
    if not np.all(np.isin(nz, [-1.0, 1.0])):
        raise AssertionError("sparse code not bipolar")


def _selftest_projection_dim_match() -> None:
    rng = np.random.RandomState(11)
    h = np.zeros(N_HIPPO, dtype=np.float64)
    h[:K_HIPPO_ACTIVE] = 1.0
    P_hc = rng.randn(N_CORTEX, N_HIPPO).astype(np.float64) / np.sqrt(N_HIPPO)
    c = project_hippo_to_cortex(h, P_hc)
    if c.shape != (N_CORTEX,):
        raise AssertionError(f"projection shape wrong: {c.shape} != ({N_CORTEX},)")
    norm = float(np.linalg.norm(c))
    if not (0.5 < norm < 1.5):
        raise AssertionError(f"projection not L2-normed: norm={norm}")


def _selftest_chunk_seed_matches_anchor() -> None:
    if SEEDS_FULL != [SEED_THIS_CHUNK]:
        raise AssertionError(
            f"chunk seed mismatch: SEEDS_FULL={SEEDS_FULL} != "
            f"[SEED_THIS_CHUNK={SEED_THIS_CHUNK}]"
        )
    if f"seed_{SEED_THIS_CHUNK}" not in ANCHOR_NAME:
        raise AssertionError(
            f"anchor name '{ANCHOR_NAME}' does not contain "
            f"seed_{SEED_THIS_CHUNK}; ANCHOR_NAME_CONFIG_MISMATCH"
        )


def _selftest_capacity_alpha() -> None:
    """Chain-grade capacity gate: alpha_simple >= 0.05 at FULL.
    Smoke is exempt (we don't gate chain-grade promotion off smoke params).
    """
    if RUN_MODE == "full":
        if ALPHA_SIMPLE < 0.05:
            raise AssertionError(
                f"CAPACITY_WARN: alpha_simple=M/N_c={ALPHA_SIMPLE:.4f} < 0.05; "
                f"chain-grade promotion gated by alpha>=0.05 (M={M_ITEMS}, N_c={N_CORTEX})"
            )


def _selftest_torch_batched_matches_numpy() -> None:
    """Verify torch batched matmul Hebbian writes match numpy outer-product
    accumulation (small dims). Catches GPU-vs-CPU math divergence."""
    if not _TORCH_AVAILABLE:
        return  # torch not installed; skip
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


def _instrumentation_selftest() -> None:
    try:
        _selftest_anatomical_separation()
        _selftest_sparse_pattern_separator()
        _selftest_projection_dim_match()
        _selftest_chunk_seed_matches_anchor()
        _selftest_capacity_alpha()
        _selftest_torch_batched_matches_numpy()
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
        f"[selftest] PASS  N_h={N_HIPPO}  N_c={N_CORTEX}  sparsity={HIPPO_SPARSITY}  "
        f"M={M_ITEMS}  N_replay={N_REPLAY_CYCLES}  eta_c={ETA_CORTEX}  "
        f"mode={RUN_MODE}  chunk_seed={SEED_THIS_CHUNK}  "
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

    print(f"  [seed={seed}] N_h={N_HIPPO} (sparse k={K_HIPPO_ACTIVE}), "
          f"N_c={N_CORTEX} (dense), M={M_ITEMS}, N_replay={N_REPLAY_CYCLES}, "
          f"backend={COMPUTE_BACKEND}",
          flush=True)

    arms = []
    for arm_name in ("ARM_FULL_HANDOFF", "ARM_NO_REPLAY", "ARM_DIRECT_CORTEX"):
        if USE_TORCH_CUDA:
            out = run_arm_torch_cuda(arm_name, seed, keys_raw, vals_raw,
                                     P_in, P_hc, out_dir)
        else:
            out = run_arm_numpy(arm_name, seed, keys_raw, vals_raw,
                                P_in, P_hc, out_dir)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
            f"recall={out['recall_cortex']:.3f} "
            f"hippo_post={out['hippo_post_zero_norm']:.2e} "
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
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "N_replay": N_REPLAY_CYCLES,
        "eta_c": ETA_CORTEX,
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
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict (single-seed chunk)
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
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected 1 seed, got {len(results)}")
    r = results[0]
    arm_names = ("ARM_FULL_HANDOFF", "ARM_NO_REPLAY", "ARM_DIRECT_CORTEX")
    n_arms = len(r["arms"])
    if n_arms != EXPECTED_N_UNITS:
        return ("HARD_FAIL",
                f"CARDINALITY_BREACH: expected {EXPECTED_N_UNITS} arms, got {n_arms}")
    try:
        per = [_arm_by_name(r["arms"], name) for name in arm_names]
    except KeyError as e:
        return ("HARD_FAIL", f"Missing arm: {e}")
    for a in per:
        if a["arm_status"] != "OK":
            return ("HARD_FAIL", f"Arm {a['arm_name']} error: {a['arm_status']}")

    full = per[0]["recall_cortex"]
    nor = per[1]["recall_cortex"]
    dir_ = per[2]["recall_cortex"]
    gap = full - nor
    ratio_to_dir = full / max(dir_, 1e-9)

    if abs(full - nor) < 1e-6:
        return ("HARD_FAIL",
                f"META_RULE_AF VIOLATION: FULL={full} == NO_REPLAY={nor}; "
                f"arms identical -- replay mechanism not engaged")

    summary = (
        f"seed={SEED_THIS_CHUNK} "
        f"FULL={full:.3f} NO_REPLAY={nor:.3f} DIRECT={dir_:.3f} "
        f"gap_FULL_vs_NO={gap:+.3f} ratio_FULL_to_DIRECT={ratio_to_dir:.3f} "
        f"alpha_simple={ALPHA_SIMPLE:.4f} backend={COMPUTE_BACKEND}"
    )

    if nor > 0.20:
        return ("HARD_FAIL",
                f"HARD_FAIL: FAIRNESS NO_REPLAY={nor:.3f} > 0.20 -- cortex not "
                f"genuinely empty; baseline leaking. {summary}")

    # Chain-grade alpha check (auto-PASS at M=8192 N_c=8192 in FULL; smoke exempt)
    capacity_warn = ""
    if RUN_MODE == "full" and ALPHA_SIMPLE < 0.05:
        capacity_warn = (
            f" CAPACITY_WARN: alpha_simple={ALPHA_SIMPLE:.4f} < 0.05 -- "
            f"NOT chain-grade-eligible. "
        )

    hp_recall = full >= 0.50
    hp_gap = gap >= 0.40
    hp_ratio = ratio_to_dir >= 0.70 if dir_ > 0.05 else False
    hp_alpha = ALPHA_SIMPLE >= 0.05 if RUN_MODE == "full" else True

    if all([hp_recall, hp_gap, hp_ratio, hp_alpha]):
        return ("HARD_PASS",
                f"HARD_PASS: acc(FULL)>=0.50 AND gap>=0.40 AND ratio>=0.70 "
                f"AND alpha>=0.05.{capacity_warn} {summary}")

    if gap < 0.10:
        return ("HARD_FAIL",
                f"HARD_FAIL: gap_FULL_vs_NO_REPLAY={gap:+.3f} < 0.10; transfer "
                f"mechanism doing essentially nothing. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: transfer partial. "
            f"hp_checks=[recall={hp_recall},gap={hp_gap},ratio={hp_ratio},alpha={hp_alpha}]. "
            f"{summary}")


# ---------------------------------------------------------------------------
# Main driver (guarded by __main__)
# ---------------------------------------------------------------------------
def _main() -> None:
    _instrumentation_selftest()
    if _ARGS.self_test:
        sys.exit(0)

    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Start marker per §13 patterns
    start_marker = out_dir / "_start_marker.txt"
    start_marker.write_text(
        f"start_ts_utc={time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} "
        f"anchor={ANCHOR_NAME} run_mode={RUN_MODE} "
        f"backend={COMPUTE_BACKEND} torch={_TORCH_AVAILABLE} cuda={_CUDA_AVAILABLE}",
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
        f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
        flush=True,
    )

    t_sweep_start = time.time()
    for seed in remaining:
        print(f"[seed={seed}] {ANCHOR_NAME} "
              f"N_h={N_HIPPO} N_c={N_CORTEX} "
              f"M={M_ITEMS} N_replay={N_REPLAY_CYCLES} mode={RUN_MODE} "
              f"backend={COMPUTE_BACKEND}...",
              flush=True)
        try:
            result = run_seed(seed, out_dir)
        except SystemExit:
            raise
        except Exception as exc:
            # Crash-diagnostic per §13: drop fatal.log + re-raise
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

    # Smoke-partial guard against stale contamination
    mode_in_results = {r.get("run_mode", "?") for r in all_results}
    if RUN_MODE == "full" and "smoke" in mode_in_results:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: stale smoke partials in FULL run. "
            f"mode_in_results={mode_in_results}. " + verdict_msg
        )

    # GPU-util discriminator (Fix #24 gate): FULL on GPU must have peak mem > 0.
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

    # META_RULE_AH atomic-write: tmp + os.replace
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": (
            f"chunk_seed={SEED_THIS_CHUNK} n_seeds={len(all_results)} "
            f"N_h={N_HIPPO} N_c={N_CORTEX} sparsity={HIPPO_SPARSITY} "
            f"M={M_ITEMS} N_replay={N_REPLAY_CYCLES} mode={RUN_MODE} "
            f"alpha_simple={ALPHA_SIMPLE:.4f} backend={COMPUTE_BACKEND}"
        ),
        "elapsed_s": float(elapsed_s),
        "config_version": CONFIG_VERSION,
        "N_h": N_HIPPO,
        "N_c": N_CORTEX,
        "M": M_ITEMS,
        "N_replay": N_REPLAY_CYCLES,
        "eta_c": ETA_CORTEX,
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
            and len(all_results[0].get("arms", [])) == EXPECTED_N_UNITS
        ) if all_results else False,
        "chunk_seed": SEED_THIS_CHUNK,
        "run_mode": RUN_MODE,
        "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
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
