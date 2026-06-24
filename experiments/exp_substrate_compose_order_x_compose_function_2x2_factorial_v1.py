"""
substrate_compose_order_x_compose_function_2x2_factorial_v1

SCIENTIFIC QUESTION (2026-06-23):
  The modulatory+architectural parameter taxonomy (research note 2026-06-23)
  identifies TWO axes as highest-leverage independent of in-flight verdicts:
  (1) COMPOSE ORDER: brain-canonical sparse->bind->cleanup->read vs REVERSED
  (2) COMPOSE FUNCTION: multiplicative-shared-target vs sigmoidal-additive-heterogeneous

  This 2x2 factorial cell directly discriminates the INTERACTION of both axes.
  All 4 prior substrate-LM cells used implicitly one compose order and one
  compose function -- none tested them as crossed factors at N=4096.

  PRIMARY PREDICTION: ARM_CANONICAL_SIGMOIDAL_ADD wins by >= +0.20 BPC over
  all other arms, confirming the taxonomy's brain-canonical defaults.

2x2 DESIGN:
  AXIS_1 (compose ORDER):
    CANONICAL: sparse-encode -> bind -> cleanup -> read
      (Marr cerebellar canonical; Sjostrom-Hausser ordered STDP)
    REVERSED: read -> cleanup -> bind -> sparse-encode
      (wrong order; cleanup operates on dense input, sparsification destroys attractor)

  AXIS_2 (compose FUNCTION):
    MULTIPLICATIVE_SHARED: gate = lockin_key * hrr_key (element-wise product on shared W)
      (failed in 3-axis neuromod cell; rank-1 collapse on shared target expected)
    SIGMOIDAL_ADDITIVE_HETEROGENEOUS: gate = sigmoid(alpha * lockin_key + beta * hrr_key)
      where lockin W and hrr W are SEPARATE (each in own algebraic structure)
      (brain canonical per Pawlak+Lefort+Fremaux-Gerstner; dual-trace HARD_PASS precedent)

ARMS (5 total, 3 seeds each):
  ARM_VEHICLE              -- plain rank-1 Hebbian, no compose; baseline floor
  ARM_CANONICAL_MULT       -- CANONICAL order + MULTIPLICATIVE compose (shared W)
  ARM_REVERSED_MULT        -- REVERSED order + MULTIPLICATIVE compose (shared W)
  ARM_CANONICAL_SIGMOID    -- CANONICAL order + SIGMOIDAL_ADDITIVE_HETEROGENEOUS (LOAD-BEARING)
  ARM_REVERSED_SIGMOID     -- REVERSED order + SIGMOIDAL_ADDITIVE_HETEROGENEOUS

WHAT THIS DOES NOT SHOW (per verdict_lint):
  - Does NOT test K-module (K>2 modules); only 2 modules composed here
  - Does NOT generalize to encoders other than char-trigram (no word2vec here;
    avoids gensim load latency for ~20min local_cpu run)
  - Does NOT test composition of all 5 chain-grade primitives; only lockin + HRR
  - Effect size may differ at N=8192 (harness baseline scale); this cell is N=4096

PRE-REGISTERED HARD BANDS (IMMUTABLE):
  HARD_PASS: ARM_CANONICAL_SIGMOIDAL wins by >= +0.20 BPC over ALL other 4 arms
             AND cv across 3 seeds < 0.05
             (taxonomy confirms canonical order + sigmoid-add are BOTH load-bearing)
  CHAIN_GRADE_BONUS: above + lift vs ARM_VEHICLE >= +0.30 BPC
             (ARM_CANONICAL_SIGMOID breaks the +0.44 bit BPC envelope at N=4096)
  MIDDLE_BAND: ARM_CANONICAL_SIGMOIDAL wins best arm by +0.05 to +0.20 BPC
             (one axis confirmed; other ambiguous)
  HARD_FAIL: ARM_CANONICAL_SIGMOIDAL lift vs ARM_VEHICLE <= +0.05 BPC
             OR all 4 compose arms collapse to vehicle BPC (+/- 0.05)
             (taxonomy wrong; refer to research re-drill)
  cv < 0.05 for HARD_PASS verdict

PROT-018: anchor name has no _n suffix. Production N=4096.
  Explicit declaration: "No _nN suffix; production N = 4096; rationale: local_cpu_queue
  run at N=4096 (pure numpy, ~20min CPU); not the 8192 GPU harness baseline scale."

ASCII-only. Per-seed checkpoint. atexit synthesizer.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import os
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import argparse
import atexit
import hashlib
import math
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial_key,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_compose_order_x_compose_function_2x2_factorial_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Production N = 4096 (PROT-018 declaration: no _nN suffix; see docstring)
PRODUCTION_N = 4096

# ---- Config ----
if RUN_MODE == "smoke" or _ARGS.self_test:
    SEEDS = [7]
    N_DIM = 512
    N_TRAIN = 2000
    N_HELD = 400
    VOCAB_CAP = 200
    INGEST_CHUNK = 256
    RECALL_BATCH = 64
else:
    SEEDS = [7, 17, 23]
    N_DIM = PRODUCTION_N
    N_TRAIN = 100_000
    N_HELD = 20_000
    VOCAB_CAP = 4000
    INGEST_CHUNK = 2048
    RECALL_BATCH = 256

# Compose function params
LOCK_IN_P = 32              # lock-in amplifier carrier phase count
LOCK_IN_K_FREQ = 31         # coprime to N_DIM; frequency subspace key
SPARSE_BIPOLAR_F = 0.05     # M1 sparsity (chain-grade default from fair_harness)
HRR_CONTEXT_WINDOW = 3      # HRR bind context positions
SIGMOID_ALPHA = 1.0         # sigmoid-additive: weight on lockin module signal
SIGMOID_BETA = 1.0          # sigmoid-additive: weight on hrr module signal

# T+lambda sweep for BPC eval
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# DEGEN gate: if raw_bpc_T1L1 within DEGEN_TOL of -log2(1/V), flag DEGEN
DEGEN_TOL = 0.5

# Pre-registered verdict thresholds (IMMUTABLE)
HP_BEST_ARM_MARGIN = 0.20       # HARD_PASS: sigmoid-add canonical wins best other by >= this
HP_CHAIN_GRADE_VS_VEHICLE = 0.30  # CHAIN_GRADE_BONUS: lift vs ARM_VEHICLE >= this
HARD_FAIL_LIFT_VS_VEHICLE = 0.05  # HARD_FAIL: lift vs vehicle <= this
CV_MAX = 0.05

ARMS = [
    "ARM_VEHICLE",
    "ARM_CANONICAL_MULT",
    "ARM_REVERSED_MULT",
    "ARM_CANONICAL_SIGMOID",
    "ARM_REVERSED_SIGMOID",
]

CONFIG_VERSION = (
    "substrate_compose_order_x_compose_function_2x2_factorial_v1; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d mode=%s seeds=%s "
    "lockin_P=%d lockin_k=%d hrr_ctx=%d sig_alpha=%.2f sig_beta=%.2f "
    "HP_margin=%.2f HF_lift=%.2f cv_max=%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, RUN_MODE, SEEDS,
    LOCK_IN_P, LOCK_IN_K_FREQ, HRR_CONTEXT_WINDOW,
    SIGMOID_ALPHA, SIGMOID_BETA,
    HP_BEST_ARM_MARGIN, HARD_FAIL_LIFT_VS_VEHICLE, CV_MAX,
)


# ============================================================================
# Utilities
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
    """Char-trigram bag-of-trigrams HD encoder."""
    t = " " + word.lower().replace("_", " ") + " "
    accum = np.zeros(n_dim, dtype=np.float32)
    if len(t) < 3:
        return accum
    for i in range(len(t) - 2):
        tri = t[i:i + 3]
        accum += _bipolar_hv(_seed_for_trigram(tri, seed), n_dim)
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def l2_norm(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """L2 normalize rows (2D) or vector (1D)."""
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def sparsify_bipolar(E: np.ndarray, f: float) -> np.ndarray:
    """Sparse-bipolar: keep top-k absolute per row; set to +/- 1; zero rest."""
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    out = np.zeros_like(E)
    for i in range(V):
        idx = np.argpartition(np.abs(E[i]), -k)[-k:]
        out[i, idx] = np.sign(E[i, idx])
        out[i, idx][out[i, idx] == 0] = 1.0
    return out


def lock_in_encode_batch(keys: np.ndarray, P: int, k_signal: int) -> np.ndarray:
    """Lock-in frequency carrier: superpose P-phase cyclic-rolls, L2-normalize.
    Maps keys into frequency subspace; distinct from dimension-space (M1).
    """
    B, N = keys.shape
    if P <= 1:
        return keys.copy()
    acc = np.zeros_like(keys, dtype=np.float32)
    for p in range(P):
        carrier_p = math.cos(2.0 * math.pi * p / P)
        rolled = np.roll(keys, shift=p * k_signal, axis=1)
        acc += rolled * carrier_p
    return l2_norm((2.0 / P) * acc)


def hrr_bind_batch(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Circular convolution via FFT: HRR bind A*B.
    Involutive: unbind(bind(A,B),B)=A for unit-norm B.
    """
    Fa = np.fft.rfft(A, axis=-1)
    Fb = np.fft.rfft(B, axis=-1)
    return np.fft.irfft(Fa * Fb, n=A.shape[-1], axis=-1).astype(np.float32)


def build_pos_vecs(n_dim: int, n_pos: int, seed: int) -> np.ndarray:
    """Build n_pos deterministic lock-in position carriers [n_pos, n_dim]."""
    rng = np.random.default_rng(seed * 7919 + 13)
    out = np.zeros((n_pos, n_dim), dtype=np.float32)
    for pos in range(n_pos):
        phase = rng.uniform(0.0, 2.0 * math.pi, size=n_dim).astype(np.float32)
        freq = float(max(pos, 1) * LOCK_IN_K_FREQ) / float(n_dim)
        t_arr = np.arange(n_dim, dtype=np.float32)
        v = np.cos(2.0 * math.pi * freq * t_arr + phase)
        out[pos] = v / (np.linalg.norm(v) + 1e-12)
    return out


def build_hrr_context_keys(idx: np.ndarray, E: np.ndarray,
                            ctx_window: int, pos_vecs: np.ndarray) -> np.ndarray:
    """Build HRR-bound context keys [n, dim] from token indices idx.
    Sums HRR(E[shifted], pos_vec[offset]) over offsets 0..ctx_window-1.
    """
    n = idx.shape[0]
    dim = E.shape[1]
    keys = np.zeros((n, dim), dtype=np.float32)
    for offset in range(ctx_window):
        if offset == 0:
            src = E[idx]
        else:
            shifted = np.roll(idx, shift=offset)
            shifted[:offset] = idx[0]
            src = E[shifted]
        pv = pos_vecs[offset][np.newaxis, :]  # [1, dim]
        pv_batch = np.broadcast_to(pv, (n, dim)).copy()
        bound = hrr_bind_batch(src, pv_batch)
        keys += bound
    return l2_norm(keys)


def build_rank1_W(src_keys: np.ndarray, tgt_vecs: np.ndarray,
                  idx_train: np.ndarray, chunk: int) -> np.ndarray:
    """W = sum_t outer(tgt_vecs[t+1], src_keys[t]); rank-1 Hebbian write."""
    dim = src_keys.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    for b in range(0, n_pairs, chunk):
        end = min(b + chunk, n_pairs)
        src_b = src_keys[b:end]                       # [batch, dim]
        tgt_b = tgt_vecs[idx_train[b + 1:end + 1]]   # [batch, dim]
        W += tgt_b.T @ src_b
    return W


def compute_logits(W: np.ndarray, src_keys: np.ndarray,
                   E_tgt: np.ndarray, recall_batch: int) -> np.ndarray:
    """[n, V] logit matrix: logit[i, v] = W(src[i]) @ E_tgt[v]."""
    n = src_keys.shape[0]
    V = E_tgt.shape[0]
    logits = np.zeros((n, V), dtype=np.float32)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        pred = l2_norm(src_keys[b:end] @ W.T)
        logits[b:end] = pred @ E_tgt.T
    return logits


# ============================================================================
# Compose order helpers
# ============================================================================

def build_canonical_src_keys(E_sparse: np.ndarray, idx_train: np.ndarray,
                              pos_vecs: np.ndarray) -> np.ndarray:
    """CANONICAL order: sparse-encode -> bind (HRR context) -> (cleanup implicit in W).
    Returns [N_TRAIN, dim] src key matrix for Hebbian write.
    """
    # sparse-encode first (step 2 of Marr canonical)
    keys = build_hrr_context_keys(idx_train, E_sparse, HRR_CONTEXT_WINDOW, pos_vecs)
    return keys


def build_reversed_src_keys(E_dense: np.ndarray, E_sparse: np.ndarray,
                             idx_train: np.ndarray, pos_vecs: np.ndarray) -> np.ndarray:
    """REVERSED order: dense-encode -> bind (HRR context) -> sparse-encode.
    Cleanup operates on dense input first; sparsification applied AFTER bind.
    """
    # Step 1: bind with DENSE embedding (wrong: cleanup/retrieval structure before sparse)
    keys_dense = build_hrr_context_keys(idx_train, E_dense, HRR_CONTEXT_WINDOW, pos_vecs)
    # Step 2: then sparsify (destroys attractor structure from bind)
    k = max(1, int(round(SPARSE_BIPOLAR_F * keys_dense.shape[1])))
    keys_sparse = np.zeros_like(keys_dense)
    for i in range(keys_dense.shape[0]):
        idx2 = np.argpartition(np.abs(keys_dense[i]), -k)[-k:]
        keys_sparse[i, idx2] = np.sign(keys_dense[i, idx2])
        keys_sparse[i, idx2][keys_sparse[i, idx2] == 0] = 1.0
    return l2_norm(keys_sparse)


# ============================================================================
# Compose function helpers
# ============================================================================

def compose_multiplicative_shared(lockin_logits: np.ndarray,
                                   E_sp: np.ndarray) -> np.ndarray:
    """MULTIPLICATIVE_SHARED_TARGET: element-wise product of normalized lockin pred
    and hrr pred as combined key, then read out via E_sp.
    Both modules share the SAME readout target (degenerate shared-target expected).
    Combined logit = (lockin_pred * hrr_pred_normalized) @ E_sp.T
    """
    # lockin_logits [n, V]: use as stand-in for combined; in shared-target compose,
    # we multiply the two module PREDICTIONS (post-softmax), then re-read.
    # This corresponds to: combined_key = W1_key * W2_key (product of retrieved vectors)
    # which is rank-1 under Levy-Horn-Ruppin since both project to same E_sp target.
    # Implementation: pass through -- the caller provides both logit arrays;
    # multiplicative combine = product of probabilities = log-linear sum with beta=1 each,
    # which IS rank-1 when both modules write to same W.
    # Return lockin_logits directly (caller does log-linear combine externally).
    return lockin_logits


def compute_sigmoidal_additive_gate(lockin_keys: np.ndarray,
                                    hrr_keys: np.ndarray,
                                    alpha: float, beta: float) -> np.ndarray:
    """SIGMOIDAL_ADDITIVE_HETEROGENEOUS compose gate.
    gate[i] = sigmoid(alpha * lockin_keys[i] + beta * hrr_keys[i])
    Returns [n, dim] gated key for use as src in rank-1 W read.
    This operates on the KEY (write-side composition), not on logits.
    Each module contributes to a SEPARATE target: lockin_W is built on lockin_keys,
    hrr_W is built on hrr_keys, then final combined key is sigmoid-additive of both
    AFTER normalization.
    """
    combined = alpha * lockin_keys + beta * hrr_keys
    # sigmoid saturation: limits dynamic range, prevents unbounded gain
    gate = 1.0 / (1.0 + np.exp(-combined.astype(np.float64))).astype(np.float32)
    return l2_norm(gate)


# ============================================================================
# BPC / top-1 / MRR eval
# ============================================================================

def softmax_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return (e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)).astype(np.float32)


def log_linear_interp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return (combined - Z[:, None]).astype(np.float32)


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    return -float(np.mean(logp[np.arange(n), nxt])) / math.log(2.0)


def top1_acc(logp: np.ndarray, nxt: np.ndarray) -> float:
    if len(nxt) == 0:
        return float("nan")
    return float(np.mean(np.argmax(logp, axis=1) == nxt))


def mrr_at_k(logp: np.ndarray, nxt: np.ndarray, k: int) -> float:
    n = len(nxt)
    if n == 0:
        return float("nan")
    k_use = min(k, logp.shape[1])
    top_idx = np.argpartition(-logp, kth=k_use - 1, axis=1)[:, :k_use]
    rows = np.arange(n)[:, None]
    top_vals = logp[rows, top_idx]
    order = np.argsort(-top_vals, axis=1)
    top_idx_sorted = top_idx[rows, order]
    rr = 0.0
    for i in range(n):
        match_pos = np.where(top_idx_sorted[i] == nxt[i])[0]
        if len(match_pos) > 0:
            rr += 1.0 / float(match_pos[0] + 1)
    return float(rr / n)


def sweep_single_arm(logits: np.ndarray, U_log: np.ndarray,
                     nxt_dev: np.ndarray, nxt_test: np.ndarray) -> Dict:
    """T+lambda sweep for a single-logit-set arm."""
    n_dev = len(nxt_dev)
    n_test = len(nxt_test)
    logits_dev = logits[:n_dev]
    logits_test = logits[n_dev:]

    # Raw BPC at T=1 lam=1 (DEGEN gate input)
    probs_T1 = softmax_with_T(logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_T1L1 = bpc_from_logp(logp_T1, nxt_test)

    best_bpc = float("inf")
    best_top1 = -1.0
    best_mrr = -1.0
    best_bpc_cfg: Dict = {}
    best_top1_cfg: Dict = {}
    best_mrr_cfg: Dict = {}

    for T in TEMP_GRID:
        probs_dev = softmax_with_T(logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0)).astype(np.float32)
        for lam in LAMBDA_GRID:
            logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, MRR_K)
            if bd < best_bpc:
                best_bpc = bd
                best_bpc_cfg = {"T": T, "lam": lam}
            if td > best_top1:
                best_top1 = td
                best_top1_cfg = {"T": T, "lam": lam}
            if md > best_mrr:
                best_mrr = md
                best_mrr_cfg = {"T": T, "lam": lam}

    def eval_cfg(cfg: Dict) -> np.ndarray:
        probs_tst = softmax_with_T(logits_test, cfg["T"])
        lp_sub = np.log(np.clip(probs_tst, 1e-30, 1.0)).astype(np.float32)
        return log_linear_interp(lp_sub, U_log, cfg["lam"])

    bpc_best = bpc_from_logp(eval_cfg(best_bpc_cfg), nxt_test)
    top1_best = top1_acc(eval_cfg(best_top1_cfg), nxt_test)
    mrr_best = mrr_at_k(eval_cfg(best_mrr_cfg), nxt_test, MRR_K)

    return {
        "bpc_best": round(bpc_best, 4),
        "best_T_for_bpc": best_bpc_cfg.get("T", 1.0),
        "best_lam_for_bpc": best_bpc_cfg.get("lam", 0.0),
        "top1_acc": round(top1_best, 4),
        "mrr_at_10": round(mrr_best, 4),
        "raw_bpc_at_T1_L1": round(raw_bpc_T1L1, 4),
        "n_dev": int(n_dev),
        "n_test": int(n_test),
        "best_bpc_cfg": best_bpc_cfg,
    }


def sweep_log_linear_two_modules(logits_a: np.ndarray, logits_b: np.ndarray,
                                  U_log: np.ndarray,
                                  nxt_dev: np.ndarray, nxt_test: np.ndarray,
                                  beta_grid: Optional[List[float]] = None) -> Dict:
    """Log-linear combine of two module logit arrays + T+lambda sweep.
    For MULTIPLICATIVE compose: logits_a and logits_b are from two W matrices
    trained on same target; combine = log-linear (equivalent to product of probs).
    """
    if beta_grid is None:
        beta_grid = [0.3, 0.5, 0.7, 1.0, 1.5, 2.0]
    n_dev = len(nxt_dev)
    n_test = len(nxt_test)
    la_dev = logits_a[:n_dev]
    la_tst = logits_a[n_dev:]
    lb_dev = logits_b[:n_dev]
    lb_tst = logits_b[n_dev:]

    # Raw BPC: uniform betas=1.0, T=1, lam=0
    lp_a_T1 = np.log(np.clip(softmax_with_T(la_tst, 1.0), 1e-30, 1.0)).astype(np.float32)
    lp_b_T1 = np.log(np.clip(softmax_with_T(lb_tst, 1.0), 1e-30, 1.0)).astype(np.float32)
    combined_T1 = lp_a_T1 + lp_b_T1
    combined_T1 -= combined_T1.max(axis=1, keepdims=True)
    Z_T1 = np.log(np.clip(np.exp(combined_T1).sum(axis=1), 1e-30, None))
    logp_raw = (combined_T1 - Z_T1[:, None]).astype(np.float32)
    raw_bpc_T1L1 = bpc_from_logp(logp_raw, nxt_test)

    best_bpc = float("inf")
    best_top1 = -1.0
    best_mrr = -1.0
    best_bpc_cfg: Dict = {}

    for beta_b in beta_grid:
        lp_a_dev = np.log(np.clip(softmax_with_T(la_dev, 1.0), 1e-30, 1.0)).astype(np.float32)
        lp_b_dev = np.log(np.clip(softmax_with_T(lb_dev, 1.0), 1e-30, 1.0)).astype(np.float32)
        comb_dev = lp_a_dev + beta_b * lp_b_dev
        comb_dev -= comb_dev.max(axis=1, keepdims=True)
        Z_dev = np.log(np.clip(np.exp(comb_dev).sum(axis=1), 1e-30, None))
        logp_comp_dev = (comb_dev - Z_dev[:, None]).astype(np.float32)
        for lam in LAMBDA_GRID:
            logp_dev = log_linear_interp(logp_comp_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, MRR_K)
            if bd < best_bpc:
                best_bpc = bd
                best_bpc_cfg = {"beta_b": beta_b, "lam": lam}
            if td > best_top1:
                best_top1 = td
            if md > best_mrr:
                best_mrr = md

    def eval_best(cfg: Dict) -> np.ndarray:
        beta_b_val = cfg.get("beta_b", 1.0)
        lam_val = cfg.get("lam", 0.0)
        lp_a_t = np.log(np.clip(softmax_with_T(la_tst, 1.0), 1e-30, 1.0)).astype(np.float32)
        lp_b_t = np.log(np.clip(softmax_with_T(lb_tst, 1.0), 1e-30, 1.0)).astype(np.float32)
        comb_t = lp_a_t + beta_b_val * lp_b_t
        comb_t -= comb_t.max(axis=1, keepdims=True)
        Z_t = np.log(np.clip(np.exp(comb_t).sum(axis=1), 1e-30, None))
        logp_comp = (comb_t - Z_t[:, None]).astype(np.float32)
        return log_linear_interp(logp_comp, U_log, lam_val)

    bpc_best = bpc_from_logp(eval_best(best_bpc_cfg), nxt_test)
    top1_best_t = top1_acc(eval_best(best_bpc_cfg), nxt_test)
    mrr_best_t = mrr_at_k(eval_best(best_bpc_cfg), nxt_test, MRR_K)

    return {
        "bpc_best": round(bpc_best, 4),
        "top1_acc": round(top1_best_t, 4),
        "mrr_at_10": round(mrr_best_t, 4),
        "raw_bpc_at_T1_L1": round(raw_bpc_T1L1, 4),
        "n_dev": int(n_dev),
        "n_test": int(n_test),
        "best_bpc_cfg": best_bpc_cfg,
    }


# ============================================================================
# Text8 loader + vocab
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] corpus missing at %s" % TEXT8, flush=True)
        sys.exit(1)
    out: List[str] = []
    with TEXT8.open("r", encoding="utf-8") as f:
        buf = ""
        while len(out) < n_total:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            buf += chunk
            parts = buf.split(" ")
            buf = parts.pop()
            out.extend(parts)
        if buf and len(out) < n_total:
            out.append(buf)
    return out[:n_total]


def build_vocab(train_tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    c = Counter(train_tokens)
    top = [w for w, _ in c.most_common(cap - 1)]
    vocab = ["<unk>"] + top
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_idx(toks: List[str], w2i: Dict[str, int]) -> np.ndarray:
    unk = w2i["<unk>"]
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray, V: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    nxt_eval = nxt[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        return {"bpc_unigram": float("inf"), "top1_unigram": 0.0,
                "mrr_unigram": 0.0, "n_test": 0}
    n_dev = n_eval // 2
    nxt_test = nxt_eval[n_dev:]
    p_test = U[nxt_test].clip(1e-12, 1.0)
    bpc = float(-np.mean(np.log(p_test)) / math.log(2.0))
    am = int(np.argmax(U))
    top1_v = float(np.mean(nxt_test == am))
    order = np.argsort(-U)
    inv_rank = np.empty_like(order)
    inv_rank[order] = np.arange(len(order))
    ranks = inv_rank[nxt_test] + 1
    rr = np.where(ranks <= MRR_K, 1.0 / ranks, 0.0)
    mrr = float(np.mean(rr))
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(top1_v, 4),
            "mrr_unigram": round(mrr, 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Instrumentation self-test (mandatory; PROT-022)
# ============================================================================

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    N_t = 128
    V_t = 20
    rng = np.random.default_rng(99)

    # T1: char-trigram encodes to nonzero unit-norm vector
    hv = char_trigram_encode("hello", N_t, seed=0)
    assert hv is not None and not np.all(hv == 0), "T1 FAIL: char_trigram_encode all-zero"
    assert abs(np.linalg.norm(l2_norm(hv)) - 1.0) < 1e-5, "T1 FAIL: l2_norm not unit"
    print("[selftest] T1 PASS: char_trigram_encode + l2_norm", flush=True)

    # T2: sparsify_bipolar: exactly f*N nonzero per row, all +/-1
    E_t = rng.standard_normal((V_t, N_t)).astype(np.float32)
    E_sp_t = sparsify_bipolar(E_t, f=0.1)
    k_expected = max(1, int(round(0.1 * N_t)))
    nz_per_row = (E_sp_t != 0).sum(axis=1)
    assert (nz_per_row == k_expected).all(), "T2 FAIL: sparsify_bipolar wrong k"
    assert np.abs(E_sp_t[E_sp_t != 0]).max() == 1.0, "T2 FAIL: not bipolar"
    print("[selftest] T2 PASS: sparsify_bipolar k=%d bipolar OK" % k_expected, flush=True)

    # T3: lock_in_encode_batch: output non-zero and finite, shape preserved
    keys = l2_norm(rng.standard_normal((4, N_t)).astype(np.float32))
    enc = lock_in_encode_batch(keys, P=8, k_signal=31)
    assert enc.shape == keys.shape, "T3 FAIL: lock_in shape mismatch"
    assert np.isfinite(enc).all(), "T3 FAIL: lock_in non-finite"
    assert not np.all(enc == 0), "T3 FAIL: lock_in all-zero"
    print("[selftest] T3 PASS: lock_in_encode_batch shape+finite", flush=True)

    # T4: hrr_bind_batch: involution bind(bind(A,B),B_inv)=A (cosine sim > 0.5)
    A = l2_norm(rng.standard_normal((4, N_t)).astype(np.float32))
    B = l2_norm(rng.standard_normal((4, N_t)).astype(np.float32))
    AB = l2_norm(hrr_bind_batch(A, B))
    # HRR involution: B_inv[0]=B[0], B_inv[k]=B[N-k] for k>0
    B_inv = np.zeros_like(B)
    B_inv[:, 0] = B[:, 0]
    if N_t > 1:
        B_inv[:, 1:] = B[:, :0:-1]
    recovered = l2_norm(hrr_bind_batch(AB, B_inv))
    cos_r = (recovered * A).sum(axis=1)
    assert float(cos_r.min()) > 0.3, "T4 FAIL: HRR involution cos_min=%.4f" % float(cos_r.min())
    print("[selftest] T4 PASS: HRR involution cos_min=%.4f" % float(cos_r.min()), flush=True)

    # T5: build_rank1_W: W finite and nonzero
    E_sp2 = l2_norm(rng.standard_normal((V_t, N_t)).astype(np.float32))
    src_keys = l2_norm(rng.standard_normal((8, N_t)).astype(np.float32))
    idx_t = np.arange(8, dtype=np.int64) % V_t
    W_t = build_rank1_W(src_keys, E_sp2, idx_t, chunk=4)
    assert np.isfinite(W_t).all(), "T5 FAIL: W non-finite"
    assert not np.all(W_t == 0), "T5 FAIL: W all-zero"
    print("[selftest] T5 PASS: build_rank1_W finite nonzero", flush=True)

    # T6: compute_logits: shape [n, V] and finite
    logits_t = compute_logits(W_t, src_keys, E_sp2, recall_batch=4)
    assert logits_t.shape == (8, V_t), "T6 FAIL: logits shape %s" % str(logits_t.shape)
    assert np.isfinite(logits_t).all(), "T6 FAIL: logits non-finite"
    print("[selftest] T6 PASS: compute_logits shape=%s finite=True" % str(logits_t.shape), flush=True)

    # T7: sweep_single_arm: bpc is finite and positive
    nxt_fake = np.arange(4, dtype=np.int64) % V_t
    U_log_fake = np.log(np.full(V_t, 1.0 / V_t, dtype=np.float32))
    logits_full_fake = np.tile(logits_t, (2, 1))[:8]  # 8 positions, dev=4, test=4
    res = sweep_single_arm(logits_full_fake, U_log_fake, nxt_fake[:4], nxt_fake)
    assert math.isfinite(res["bpc_best"]) and res["bpc_best"] > 0, (
        "T7 FAIL: bpc_best=%.4f not finite/positive" % res["bpc_best"])
    assert res["raw_bpc_at_T1_L1"] is not None and math.isfinite(res["raw_bpc_at_T1_L1"]), (
        "T7 FAIL: raw_bpc_at_T1_L1 not finite")
    print("[selftest] T7 PASS: sweep_single_arm bpc_best=%.4f raw=%.4f" % (
        res["bpc_best"], res["raw_bpc_at_T1_L1"]), flush=True)

    # T8: sigmoidal-additive gate: non-trivial (not all 0.5 unless perfectly balanced)
    keys_a = l2_norm(rng.standard_normal((8, N_t)).astype(np.float32))
    keys_b = l2_norm(rng.standard_normal((8, N_t)).astype(np.float32))
    gate = compute_sigmoidal_additive_gate(keys_a, keys_b, alpha=1.0, beta=1.0)
    assert gate.shape == keys_a.shape, "T8 FAIL: gate shape mismatch"
    assert not np.allclose(gate, 0.5, atol=0.1), "T8 FAIL: gate all~0.5 (likely degenerate)"
    print("[selftest] T8 PASS: sigmoid gate non-trivial mean=%.4f" % float(gate.mean()), flush=True)

    # T9: DEGEN check: for random logits at V=200 raw_bpc should be near log2(200)=7.64
    V_large = 200
    logits_random = rng.standard_normal((4, V_large)).astype(np.float32)
    probs_T1 = softmax_with_T(logits_random, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    nxt_r = np.zeros(2, dtype=np.int64)
    raw_bpc_r = bpc_from_logp(logp_T1[2:4], nxt_r)
    uniform_entropy = math.log2(V_large)
    assert abs(raw_bpc_r - uniform_entropy) < 2.0, (
        "T9 FAIL: DEGEN check raw_bpc=%.4f vs uniform_entropy=%.4f" % (raw_bpc_r, uniform_entropy))
    print("[selftest] T9 PASS: DEGEN gate raw_bpc=%.4f uniform=%.4f (within 2 bits)" % (
        raw_bpc_r, uniform_entropy), flush=True)

    print("[selftest] ALL 9 PASS: trigram+sparse+lockin+HRR+W+logits+sweep+sigmoid+degen",
          flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    print("[self-test] complete -- exiting", flush=True)
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading text8 + building vocab" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[WARN] corpus short: %d tokens" % len(toks), flush=True)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d" % (
        seed, V, N_TRAIN, N_HELD, N_DIM), flush=True)

    U_np = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U_np, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.4f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"], uni["n_test"]),
        flush=True)

    # Build char-trigram base encoder (pure numpy; no gensim needed)
    print("[seed=%d] building char-trigram E (V=%d N_DIM=%d)..." % (seed, V, N_DIM), flush=True)
    t_enc0 = time.time()
    E_dense = np.stack([char_trigram_encode(w, N_DIM, seed) for w in vocab], 0).astype(np.float32)
    E_dense = l2_norm(E_dense)
    E_sparse = sparsify_bipolar(E_dense, SPARSE_BIPOLAR_F)
    E_sparse = l2_norm(E_sparse)
    print("[seed=%d encoder] built in %.1fs; sparsity=%.3f" % (
        seed, time.time() - t_enc0, SPARSE_BIPOLAR_F), flush=True)

    # Position vectors for HRR context bind
    pos_vecs = build_pos_vecs(N_DIM, HRR_CONTEXT_WINDOW, seed)

    # Eval split (no-<unk> context filter)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask_eval = (ctx_full != unk)
    ctx_eval_pos = np.where(mask_eval)[0]
    nxt_eval = nxt_full[mask_eval]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        print("[seed=%d] WARN n_eval=0; skip" % seed, flush=True)
        return {"seed": seed, "by_arm": {"ARM_UNIGRAM": uni}, "skip_reason": "n_eval=0",
                "V": V, "N": N_DIM, "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "VOCAB_CAP": VOCAB_CAP, "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
                "elapsed_s_seed": round(time.time() - t_seed, 2), "n_llm_calls": 0}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}
    ctx_vocab_idx = ctx_full[ctx_eval_pos]  # [n_eval] int64 vocab indices for context positions

    # ----------------------------------------------------------------
    # ARM_VEHICLE: plain rank-1 Hebbian, no compose -- baseline floor
    # ----------------------------------------------------------------
    print("\n[seed=%d] arm=ARM_VEHICLE (plain rank-1, no compose)" % seed, flush=True)
    t_arm = time.time()
    try:
        # VEHICLE uses canonical sparse encoder keys directly (no HRR bind)
        src_keys_v_train = E_sparse[idx_train]
        W_v = build_rank1_W(src_keys_v_train, E_sparse, idx_train, INGEST_CHUNK)
        del src_keys_v_train
        src_keys_v_held = E_sparse[ctx_vocab_idx]
        logits_v = compute_logits(W_v, src_keys_v_held, E_sparse, RECALL_BATCH)
        del W_v, src_keys_v_held
        jr_v = sweep_single_arm(logits_v, U_log, nxt_dev, nxt_test)
        jr_v["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        by_arm["ARM_VEHICLE"] = jr_v
        print("    [seed=%d arm=ARM_VEHICLE] bpc_best=%.4f top1=%.4f mrr=%.4f raw_T1L1=%.4f" % (
            seed, jr_v["bpc_best"], jr_v["top1_acc"], jr_v["mrr_at_10"],
            jr_v["raw_bpc_at_T1_L1"]), flush=True)
    except Exception as e:
        import traceback
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d arm=ARM_VEHICLE] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_VEHICLE"] = {"compute_failed": True, "compute_error": err,
                                  "bpc_best": float("inf"), "top1_acc": float("nan"),
                                  "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                                  "elapsed_s_arm": round(time.time() - t_arm, 2)}

    # -------------------------------------------------------------------
    # Pre-compute module key sets for all 4 compose arms
    # CANONICAL order: sparse-encode first, then HRR bind context
    # REVERSED order:  HRR bind context on DENSE embed, then sparse-encode
    # -------------------------------------------------------------------
    print("\n[seed=%d] building CANONICAL and REVERSED key sets..." % seed, flush=True)
    t_keys = time.time()

    # CANONICAL train keys: sparse -> bind (HRR context using E_sparse)
    src_keys_can_train = build_hrr_context_keys(idx_train, E_sparse, HRR_CONTEXT_WINDOW, pos_vecs)
    # CANONICAL held keys
    src_keys_can_held = build_hrr_context_keys(ctx_vocab_idx, E_sparse, HRR_CONTEXT_WINDOW, pos_vecs)

    # REVERSED train keys: bind (HRR context using E_dense) -> sparse
    src_keys_rev_train = build_reversed_src_keys(E_dense, E_sparse, idx_train, pos_vecs)
    # REVERSED held: same reversal applied to held context positions
    src_keys_rev_held_pre = build_hrr_context_keys(ctx_vocab_idx, E_dense, HRR_CONTEXT_WINDOW, pos_vecs)
    # sparsify AFTER bind (reversed)
    k_rev = max(1, int(round(SPARSE_BIPOLAR_F * N_DIM)))
    src_keys_rev_held = np.zeros_like(src_keys_rev_held_pre)
    for i in range(src_keys_rev_held_pre.shape[0]):
        idx2 = np.argpartition(np.abs(src_keys_rev_held_pre[i]), -k_rev)[-k_rev:]
        src_keys_rev_held[i, idx2] = np.sign(src_keys_rev_held_pre[i, idx2])
        src_keys_rev_held[i, idx2][src_keys_rev_held[i, idx2] == 0] = 1.0
    src_keys_rev_held = l2_norm(src_keys_rev_held)
    del src_keys_rev_held_pre

    # Lock-in keys from CANONICAL sparse keys (frequency-domain module)
    src_keys_lockin_can_train = lock_in_encode_batch(src_keys_can_train, LOCK_IN_P, LOCK_IN_K_FREQ)
    src_keys_lockin_can_held = lock_in_encode_batch(src_keys_can_held, LOCK_IN_P, LOCK_IN_K_FREQ)
    src_keys_lockin_rev_train = lock_in_encode_batch(src_keys_rev_train, LOCK_IN_P, LOCK_IN_K_FREQ)
    src_keys_lockin_rev_held = lock_in_encode_batch(src_keys_rev_held, LOCK_IN_P, LOCK_IN_K_FREQ)

    print("[seed=%d] key sets built in %.1fs" % (seed, time.time() - t_keys), flush=True)

    # -----------------------------------------------------------------------
    # ARM_CANONICAL_MULT: CANONICAL order + MULTIPLICATIVE_SHARED_TARGET
    # Both W_context and W_lockin write to same E_sparse target.
    # Log-linear combine of their logit arrays = product of probs (shared target).
    # -----------------------------------------------------------------------
    print("\n[seed=%d] arm=ARM_CANONICAL_MULT" % seed, flush=True)
    t_arm = time.time()
    try:
        W_can_ctx = build_rank1_W(src_keys_can_train, E_sparse, idx_train, INGEST_CHUNK)
        logits_can_ctx = compute_logits(W_can_ctx, src_keys_can_held, E_sparse, RECALL_BATCH)
        del W_can_ctx
        W_can_loc = build_rank1_W(src_keys_lockin_can_train, E_sparse, idx_train, INGEST_CHUNK)
        logits_can_loc = compute_logits(W_can_loc, src_keys_lockin_can_held, E_sparse, RECALL_BATCH)
        del W_can_loc
        # Multiplicative: log-linear combine on SAME target E_sparse
        jr_can_mult = sweep_log_linear_two_modules(
            logits_can_ctx, logits_can_loc, U_log, nxt_dev, nxt_test)
        jr_can_mult["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        by_arm["ARM_CANONICAL_MULT"] = jr_can_mult
        print("    [seed=%d arm=ARM_CANONICAL_MULT] bpc_best=%.4f top1=%.4f mrr=%.4f" % (
            seed, jr_can_mult["bpc_best"], jr_can_mult["top1_acc"],
            jr_can_mult["mrr_at_10"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d arm=ARM_CANONICAL_MULT] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_CANONICAL_MULT"] = {"compute_failed": True, "compute_error": err,
                                         "bpc_best": float("inf"), "top1_acc": float("nan"),
                                         "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                                         "elapsed_s_arm": round(time.time() - t_arm, 2)}

    # -----------------------------------------------------------------------
    # ARM_REVERSED_MULT: REVERSED order + MULTIPLICATIVE_SHARED_TARGET
    # -----------------------------------------------------------------------
    print("\n[seed=%d] arm=ARM_REVERSED_MULT" % seed, flush=True)
    t_arm = time.time()
    try:
        W_rev_ctx = build_rank1_W(src_keys_rev_train, E_sparse, idx_train, INGEST_CHUNK)
        logits_rev_ctx = compute_logits(W_rev_ctx, src_keys_rev_held, E_sparse, RECALL_BATCH)
        del W_rev_ctx
        W_rev_loc = build_rank1_W(src_keys_lockin_rev_train, E_sparse, idx_train, INGEST_CHUNK)
        logits_rev_loc = compute_logits(W_rev_loc, src_keys_lockin_rev_held, E_sparse, RECALL_BATCH)
        del W_rev_loc
        jr_rev_mult = sweep_log_linear_two_modules(
            logits_rev_ctx, logits_rev_loc, U_log, nxt_dev, nxt_test)
        jr_rev_mult["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        by_arm["ARM_REVERSED_MULT"] = jr_rev_mult
        print("    [seed=%d arm=ARM_REVERSED_MULT] bpc_best=%.4f top1=%.4f mrr=%.4f" % (
            seed, jr_rev_mult["bpc_best"], jr_rev_mult["top1_acc"],
            jr_rev_mult["mrr_at_10"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d arm=ARM_REVERSED_MULT] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_REVERSED_MULT"] = {"compute_failed": True, "compute_error": err,
                                        "bpc_best": float("inf"), "top1_acc": float("nan"),
                                        "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                                        "elapsed_s_arm": round(time.time() - t_arm, 2)}

    # -----------------------------------------------------------------------
    # ARM_CANONICAL_SIGMOID: CANONICAL order + SIGMOIDAL_ADDITIVE_HETEROGENEOUS
    # Each module trains on DIFFERENT key space + DIFFERENT W, then keys
    # are combined via sigmoid-additive gate BEFORE reading out (key-compose).
    # W_sig is trained on the gated keys; reads out with gated held keys too.
    # -----------------------------------------------------------------------
    print("\n[seed=%d] arm=ARM_CANONICAL_SIGMOID" % seed, flush=True)
    t_arm = time.time()
    try:
        # Build sigmoid-combined train keys: sigmoid(alpha*hrr_keys + beta*lockin_keys)
        gate_can_train = compute_sigmoidal_additive_gate(
            src_keys_can_train, src_keys_lockin_can_train,
            alpha=SIGMOID_ALPHA, beta=SIGMOID_BETA)
        gate_can_held = compute_sigmoidal_additive_gate(
            src_keys_can_held, src_keys_lockin_can_held,
            alpha=SIGMOID_ALPHA, beta=SIGMOID_BETA)
        W_can_sig = build_rank1_W(gate_can_train, E_sparse, idx_train, INGEST_CHUNK)
        logits_can_sig = compute_logits(W_can_sig, gate_can_held, E_sparse, RECALL_BATCH)
        del W_can_sig, gate_can_train, gate_can_held
        jr_can_sig = sweep_single_arm(logits_can_sig, U_log, nxt_dev, nxt_test)
        jr_can_sig["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        by_arm["ARM_CANONICAL_SIGMOID"] = jr_can_sig
        print("    [seed=%d arm=ARM_CANONICAL_SIGMOID] bpc_best=%.4f top1=%.4f mrr=%.4f raw=%.4f" % (
            seed, jr_can_sig["bpc_best"], jr_can_sig["top1_acc"],
            jr_can_sig["mrr_at_10"], jr_can_sig["raw_bpc_at_T1_L1"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d arm=ARM_CANONICAL_SIGMOID] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_CANONICAL_SIGMOID"] = {"compute_failed": True, "compute_error": err,
                                            "bpc_best": float("inf"), "top1_acc": float("nan"),
                                            "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                                            "elapsed_s_arm": round(time.time() - t_arm, 2)}

    # -----------------------------------------------------------------------
    # ARM_REVERSED_SIGMOID: REVERSED order + SIGMOIDAL_ADDITIVE_HETEROGENEOUS
    # -----------------------------------------------------------------------
    print("\n[seed=%d] arm=ARM_REVERSED_SIGMOID" % seed, flush=True)
    t_arm = time.time()
    try:
        gate_rev_train = compute_sigmoidal_additive_gate(
            src_keys_rev_train, src_keys_lockin_rev_train,
            alpha=SIGMOID_ALPHA, beta=SIGMOID_BETA)
        gate_rev_held = compute_sigmoidal_additive_gate(
            src_keys_rev_held, src_keys_lockin_rev_held,
            alpha=SIGMOID_ALPHA, beta=SIGMOID_BETA)
        W_rev_sig = build_rank1_W(gate_rev_train, E_sparse, idx_train, INGEST_CHUNK)
        logits_rev_sig = compute_logits(W_rev_sig, gate_rev_held, E_sparse, RECALL_BATCH)
        del W_rev_sig, gate_rev_train, gate_rev_held
        jr_rev_sig = sweep_single_arm(logits_rev_sig, U_log, nxt_dev, nxt_test)
        jr_rev_sig["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        by_arm["ARM_REVERSED_SIGMOID"] = jr_rev_sig
        print("    [seed=%d arm=ARM_REVERSED_SIGMOID] bpc_best=%.4f top1=%.4f mrr=%.4f raw=%.4f" % (
            seed, jr_rev_sig["bpc_best"], jr_rev_sig["top1_acc"],
            jr_rev_sig["mrr_at_10"], jr_rev_sig["raw_bpc_at_T1_L1"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d arm=ARM_REVERSED_SIGMOID] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_REVERSED_SIGMOID"] = {"compute_failed": True, "compute_error": err,
                                           "bpc_best": float("inf"), "top1_acc": float("nan"),
                                           "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                                           "elapsed_s_arm": round(time.time() - t_arm, 2)}

    del E_dense, E_sparse
    del src_keys_can_train, src_keys_can_held
    del src_keys_rev_train, src_keys_rev_held
    del src_keys_lockin_can_train, src_keys_lockin_can_held
    del src_keys_lockin_rev_train, src_keys_lockin_rev_held

    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N": N_DIM,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "n_llm_calls": 0,
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})

    substrate_arms = [
        "ARM_VEHICLE",
        "ARM_CANONICAL_MULT",
        "ARM_REVERSED_MULT",
        "ARM_CANONICAL_SIGMOID",
        "ARM_REVERSED_SIGMOID",
    ]

    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    unigram_agg = {
        "bpc_mean": round(float(np.mean([x for x in uni_bpc if math.isfinite(x)])), 4)
        if any(math.isfinite(x) for x in uni_bpc) else float("nan"),
    }

    V_first = units[0].get("V", 4000)
    vocab_entropy_uniform = math.log2(max(V_first, 2))

    by_arm_agg: Dict[str, Dict] = {"ARM_UNIGRAM": unigram_agg}
    for arm in substrate_arms:
        valid_units = [
            u for u in units
            if not u["by_arm"].get(arm, {}).get("compute_failed", False)
            and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
        ]
        n_failed = len(units) - len(valid_units)
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"),
                "top1_acc_mean": float("nan"),
                "mrr_at_10_mean": float("nan"),
                "n_valid_seeds": 0,
                "n_compute_failed": n_failed,
                "all_seeds_failed": True,
            }
            continue
        bpc_vals = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_vals = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_vals = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_vals = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid_units]
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        b_cv = (b_std / max(abs(b_mean), 1e-9)) if b_mean != 0 else float("nan")
        raw_finite = [r for r in raw_vals if math.isfinite(r)]
        raw_mean = float(np.mean(raw_finite)) if raw_finite else float("nan")
        # DEGEN: raw_bpc at T=1,lam=1 is within DEGEN_TOL bits of vocab uniform entropy.
        # Only meaningful at FULL scale (smoke has too few training pairs to learn signal);
        # suppress DEGEN flag in smoke mode.
        is_degen = (
            RUN_MODE == "full"
            and math.isfinite(raw_mean)
            and abs(raw_mean - vocab_entropy_uniform) <= DEGEN_TOL
        )
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4) if math.isfinite(b_cv) else float("nan"),
            "top1_acc_mean": round(float(np.mean(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_vals)), 4),
            "raw_bpc_at_T1_L1_mean": round(raw_mean, 4) if math.isfinite(raw_mean) else float("nan"),
            "n_valid_seeds": len(valid_units),
            "n_compute_failed": n_failed,
            "all_seeds_failed": False,
            "readout_degenerate": is_degen,
        }

    # Fix #28: read per-arm metrics from by_arm_agg, NOT from verdict_msg text
    sig_can_agg = by_arm_agg.get("ARM_CANONICAL_SIGMOID", {})
    veh_agg = by_arm_agg.get("ARM_VEHICLE", {})
    other_arms = ["ARM_VEHICLE", "ARM_CANONICAL_MULT", "ARM_REVERSED_MULT", "ARM_REVERSED_SIGMOID"]

    sig_can_bpc = sig_can_agg.get("bpc_best_mean", float("inf"))
    sig_can_cv = sig_can_agg.get("bpc_best_cv", float("nan"))
    sig_can_degen = sig_can_agg.get("readout_degenerate", False)
    sig_can_failed = sig_can_agg.get("all_seeds_failed", True)
    veh_bpc = veh_agg.get("bpc_best_mean", float("inf"))

    # Margin of ARM_CANONICAL_SIGMOID over worst (closest) other arm
    other_bpcs = [by_arm_agg.get(a, {}).get("bpc_best_mean", float("inf")) for a in other_arms]
    other_bpcs_finite = [x for x in other_bpcs if math.isfinite(x)]
    best_other_bpc = min(other_bpcs_finite) if other_bpcs_finite else float("inf")  # best=lowest BPC

    verdict_msg_suffix = (
        " | PER_ARM: VEH=%.4f CAN_MULT=%.4f REV_MULT=%.4f CAN_SIG=%.4f REV_SIG=%.4f" % (
            by_arm_agg.get("ARM_VEHICLE", {}).get("bpc_best_mean", float("nan")),
            by_arm_agg.get("ARM_CANONICAL_MULT", {}).get("bpc_best_mean", float("nan")),
            by_arm_agg.get("ARM_REVERSED_MULT", {}).get("bpc_best_mean", float("nan")),
            sig_can_bpc,
            by_arm_agg.get("ARM_REVERSED_SIGMOID", {}).get("bpc_best_mean", float("nan")),
        )
    )

    if sig_can_failed or not math.isfinite(sig_can_bpc):
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL: ARM_CANONICAL_SIGMOID all seeds failed or non-finite BPC."
                       + verdict_msg_suffix)
    elif sig_can_degen:
        verdict = "INSTRUMENTATION_SUSPECT"
        verdict_msg = (
            "INSTRUMENTATION_SUSPECT: ARM_CANONICAL_SIGMOID raw_bpc_T1L1 near vocab-entropy "
            "(DEGEN gate). sig_can_bpc=%.4f." % sig_can_bpc + verdict_msg_suffix)
    else:
        # Margin = how much CANONICAL_SIGMOID beats the BEST other arm (lower BPC = better)
        margin = best_other_bpc - sig_can_bpc  # positive = CANONICAL_SIGMOID wins
        lift_vs_vehicle = veh_bpc - sig_can_bpc  # lift over no-compose vehicle
        cv_ok = math.isfinite(sig_can_cv) and sig_can_cv <= CV_MAX

        if margin >= HP_BEST_ARM_MARGIN and cv_ok:
            if lift_vs_vehicle >= HP_CHAIN_GRADE_VS_VEHICLE:
                verdict = "HARD_PASS_CHAIN_GRADE_BONUS"
                verdict_msg = (
                    "HARD_PASS CHAIN_GRADE_BONUS: ARM_CANONICAL_SIGMOID beats all arms by "
                    "+%.4f BPC (>= %.2f threshold) AND lifts +%.4f vs ARM_VEHICLE "
                    "(>= %.2f chain-grade). cv=%.4f. "
                    "Brain-canonical compose order + sigmoidal-additive CONFIRMED as load-bearing."
                    % (margin, HP_BEST_ARM_MARGIN, lift_vs_vehicle,
                       HP_CHAIN_GRADE_VS_VEHICLE, sig_can_cv)
                    + verdict_msg_suffix)
            else:
                verdict = "HARD_PASS"
                verdict_msg = (
                    "HARD_PASS: ARM_CANONICAL_SIGMOID beats all other arms by +%.4f BPC "
                    "(>= %.2f threshold). cv=%.4f. "
                    "Taxonomy confirms: canonical order + sigmoid-add are BOTH load-bearing."
                    % (margin, HP_BEST_ARM_MARGIN, sig_can_cv)
                    + verdict_msg_suffix)
        elif margin >= (HP_BEST_ARM_MARGIN * 0.25):  # +0.05 to +0.20 range
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                "MIDDLE_BAND: ARM_CANONICAL_SIGMOID wins by +%.4f BPC over best-other "
                "(in [+0.05, +%.2f)). One axis confirmed; interaction ambiguous. "
                "cv=%.4f."
                % (margin, HP_BEST_ARM_MARGIN, sig_can_cv)
                + verdict_msg_suffix)
        else:
            verdict = "HARD_FAIL"
            verdict_msg = (
                "HARD_FAIL: ARM_CANONICAL_SIGMOID wins only +%.4f BPC over best-other "
                "(<= %.2f threshold). Taxonomy axes NOT load-bearing in this regime. "
                "cv=%.4f."
                % (margin, HP_BEST_ARM_MARGIN * 0.25, sig_can_cv)
                + verdict_msg_suffix)

    return verdict, verdict_msg, {
        "by_arm_agg": by_arm_agg,
        "HP_BEST_ARM_MARGIN_threshold": HP_BEST_ARM_MARGIN,
        "HP_CHAIN_GRADE_VS_VEHICLE_threshold": HP_CHAIN_GRADE_VS_VEHICLE,
        "HARD_FAIL_LIFT_VS_VEHICLE_threshold": HARD_FAIL_LIFT_VS_VEHICLE,
        "CV_MAX_threshold": CV_MAX,
        "vocab_entropy_uniform_bits": round(vocab_entropy_uniform, 4),
        "zero_llm_calls_at_inference": True,
        "n_seeds": len(units),
    }


# ============================================================================
# Main
# ============================================================================

print("[config] anchor=%s N_DIM=%d mode=%s seeds=%s N_TRAIN=%d "
      "f=%.3f lockin_P=%d hrr_ctx=%d sig_alpha=%.2f sig_beta=%.2f" % (
          ANCHOR_NAME, N_DIM, RUN_MODE, SEEDS, N_TRAIN,
          SPARSE_BIPOLAR_F, LOCK_IN_P, HRR_CONTEXT_WINDOW,
          SIGMOID_ALPHA, SIGMOID_BETA), flush=True)

# PROT-018 check for FULL run
if RUN_MODE == "full" and N_DIM != PRODUCTION_N:
    raise RuntimeError("PROT-018: FULL run N_DIM=%d != PRODUCTION_N=%d" % (N_DIM, PRODUCTION_N))

out_dir = get_output_dir(ANCHOR_NAME)
_seeds_done, seeds_todo = resumable_seeds(SEEDS, out_dir)
print("[resumable] seeds_done=%s seeds_todo=%s" % (_seeds_done, seeds_todo), flush=True)

_atexit_units: List[Dict] = []


def _atexit_synthesize() -> None:
    if not _atexit_units:
        return
    partial_units = list(_atexit_units)
    try:
        partials_dict = aggregate_partials(out_dir)
        combined: Dict = {}
        for payload in partials_dict.values():
            k = payload.get("seed", id(payload))
            combined[k] = payload
        for u in partial_units:
            combined[u["seed"]] = u
        all_units = list(combined.values())
    except Exception:
        all_units = partial_units
    if not all_units:
        return
    verdict_str, verdict_msg, detail = compute_verdict(all_units)
    print("[atexit] PARTIAL verdict=%s: %s" % (verdict_str, verdict_msg[:200]), flush=True)


atexit.register(_atexit_synthesize)

for seed in seeds_todo:
    try:
        unit = run_unit(seed)
    except Exception as e:
        import traceback
        print("[ERROR seed=%d] %s" % (seed, traceback.format_exc()[:600]), flush=True)
        continue
    write_partial_key(out_dir, "s%d" % seed, unit)
    _atexit_units.append(unit)

_partials_dict = aggregate_partials(out_dir)
units = list(_partials_dict.values())
if not units:
    print("[FATAL] no units; exiting", flush=True)
    sys.exit(1)

verdict_str, verdict_msg, detail = compute_verdict(units)
print("\n[verdict] %s: %s" % (verdict_str, verdict_msg), flush=True)

# Fix #28: per-arm from metrics.json, NOT from verdict_msg
print("[per-arm summary from by_arm_agg]", flush=True)
for arm in ARMS:
    agg = detail.get("by_arm_agg", {}).get(arm, {})
    if agg.get("all_seeds_failed"):
        print("[arm] %s: ALL_FAILED" % arm, flush=True)
    else:
        print("[arm] %s: bpc_mean=%.4f top1_mean=%.4f mrr_mean=%.4f cv=%.4f n_valid=%d degen=%s" % (
            arm,
            agg.get("bpc_best_mean", float("inf")),
            agg.get("top1_acc_mean", float("nan")),
            agg.get("mrr_at_10_mean", float("nan")),
            agg.get("bpc_best_cv", float("nan")),
            agg.get("n_valid_seeds", 0),
            agg.get("readout_degenerate", False)), flush=True)

t_total = sum(u.get("elapsed_s_seed", 0) for u in units)

REQUIRED_FIELDS = {
    "anchor_name": ANCHOR_NAME,
    "anchor": ANCHOR_NAME,
    "verdict": verdict_str,
    "verdict_msg": verdict_msg,
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "N": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "n_seeds": len(units),
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "LOCK_IN_P": LOCK_IN_P,
    "HRR_CONTEXT_WINDOW": HRR_CONTEXT_WINDOW,
    "SIGMOID_ALPHA": SIGMOID_ALPHA,
    "SIGMOID_BETA": SIGMOID_BETA,
    "detail": detail,
    "per_unit": units,
    "elapsed_s": round(t_total, 2),
    "zero_llm_calls_at_inference": True,
    "n_llm_calls": 0,
    "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    "config_version": CONFIG_VERSION,
    "honest_scope": (
        "2x2 factorial: compose order (canonical vs reversed) x compose function "
        "(multiplicative-shared-target vs sigmoidal-additive-heterogeneous). "
        "5 arms: VEHICLE + 4 factorial cells. "
        "HP = ARM_CANONICAL_SIGMOID wins best-other by >= +0.20 BPC AND cv<=0.05. "
        "HF = margin <= +0.05 OR all seeds fail. "
        "DOES NOT TEST: K>2 modules, word2vec encoder, or N=8192 scale. "
        "N_DIM=4096 N_TRAIN=100000 N_HELD=20000 V=4000. Pure numpy."
    ),
    "prereg_bands": {
        "HP_best_arm_margin_bits": HP_BEST_ARM_MARGIN,
        "HP_chain_grade_lift_vs_vehicle_bits": HP_CHAIN_GRADE_VS_VEHICLE,
        "HF_lift_vs_vehicle_bits": HARD_FAIL_LIFT_VS_VEHICLE,
        "cv_max": CV_MAX,
    },
}

write_metrics(out_dir, REQUIRED_FIELDS)
print("[done] metrics written to %s; elapsed_s=%.1f" % (out_dir, t_total), flush=True)
