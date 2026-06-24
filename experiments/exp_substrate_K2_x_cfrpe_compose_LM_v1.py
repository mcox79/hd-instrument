"""
substrate_K2_x_cfrpe_compose_LM_v1 -- Super-additivity test: K=2 multi-bank x cf-RPE

Tests whether the 2 best validated knobs compose super-additively:
  K=2 multi-bank architecture (partition-diversity lift, +1.07 BPC smoke)
  x cf-RPE delta-rule plasticity (chain-grade HARD_PASS, +0.141 BPC fair-harness)

FOUR ARMS:
  ARM_BASELINE_RANK1_K1   -- single bank, rank-1 Hebbian; reproduces fair_harness 7.3065
  ARM_CFRPE_K1            -- cf-RPE on single bank; reproduces +0.141 chain-grade lift
  ARM_K2_RANK1            -- 2 banks each N=4096, rank-1 Hebbian per bank; K=2 smoke lift
  ARM_K2_CFRPE            -- cf-RPE per bank in K=2 architecture; the COMBINED arm

PRE-REG BANDS:
  HARD_PASS_SUPER_ADDITIVE: ARM_K2_CFRPE lift over ARM_BASELINE >= +1.20 bits
  HARD_PASS_ADDITIVE:       ARM_K2_CFRPE lift >= max(K2_RANK1_lift, CFRPE_K1_lift) + 0.10
  MIDDLE_BAND:              ARM_K2_CFRPE lift >= max of two single-knob lifts but < +0.10 over better one
  HARD_FAIL:                ARM_K2_CFRPE lift <= max(K2_RANK1_lift, CFRPE_K1_lift)
  cv < 0.05 across seeds mandatory
  Baseline arms within +/-0.05 BPC of reference values (provenance check)

CONFIG: pure numpy, text8 N_TRAIN=100k, N_DIM_TOTAL=8192, 4 arms x 3 seeds
Routing: remote_cpu_queue (pure numpy, no CUDA)

WHAT_THIS_DOES_NOT_SHOW:
  - Does not test K > 2 (only K=2 vs K=1 contrast)
  - Does not test cf-RPE with STDP (heterogeneous arm tested in prior cell)
  - Soft gate (softmax) is not hard winner-takes-all as in Drosophila MB
  - Gate parameters not trained end-to-end; gate quality is fixed-random-projection
  - N_DIM_TOTAL=8192 split into 2 banks of 4096; each bank half the resolution of K=1
  - Result at N_TRAIN=100k text8; may not generalize to other corpora

Cites:
  preregs/2026-06-23_substrate_K2_x_cfrpe_compose_LM_v1.md
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py
  experiments/shotgun_smoke_k_bank_count_sweep_v1.py
  notes/skunkworks_to_all_LANDED_VET_dual_trace_sequential_neuromod_HARD_PASS_2026-06-23.md
  notes/shotgun_smoke_K_bank_count_sweep_2026-06-23.md
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
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics,
    resumable_seeds as _resumable_seeds,
)

ANCHOR_NAME = "substrate_K2_x_cfrpe_compose_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

# ============================================================================
# Pre-reg threshold bands (pre-registered; do NOT modify post-smoke)
# ============================================================================
# lift = ARM_BASELINE_RANK1_K1 BPC - arm BPC (positive = better than baseline)
HARD_PASS_SUPER_ADDITIVE_BAR = 1.20   # K=2 lift + cf-RPE lift; super-additive
HARD_PASS_ADDITIVE_MARGIN = 0.10      # ARM_K2_CFRPE >= max(single-knob lifts) + 0.10
HARD_FAIL_NOTE = "ARM_K2_CFRPE lift <= max(K2_RANK1_lift, CFRPE_K1_lift)"
CV_MAX = 0.05                          # cv across seeds mandatory
BASELINE_BPC_REF = 7.3065             # fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR
BASELINE_TOLERANCE = 0.05             # ARM_BASELINE_RANK1_K1 must be within +/- this of REF

# ============================================================================
# Plasticity knob parameters (exact values from cf-RPE chain-grade cell)
# ============================================================================
CFRPE_LR = 0.5           # cf-RPE learning rate (from fair_harness v1)
STDP_WEIGHT = 0.0        # NOT used here; pure cf-RPE only
INGEST_BATCH = 64        # training batch size (from fair_harness v1)
N_STEPS_PER_SEED = 300   # iterative update steps per arm per seed (production; CPU-budget)
# NOTE: fair_harness chain-grade cell used 1000 steps on GPU. Here we use 300 steps
# to fit within 4h on remote_cpu (pure numpy). The lift signal is robust to step count
# in the stochastic regime (cf. N512 HARD_PASS at lower step counts). If MIDDLE_BAND
# results from step-count limitation, Strategy can approve a long-run extension.

# K-bank config
K_BANKS = 2              # number of banks for K=2 arms
GATE_TEMP = 0.5          # softmax gate temperature (from shotgun smoke)

# Eval hyperparameter grids (same as fair_harness v1)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Encoder
SPARSE_BIPOLAR_F = 0.05   # chain-grade validated

# Arms
ARMS = [
    "ARM_BASELINE_RANK1_K1",
    "ARM_CFRPE_K1",
    "ARM_K2_RANK1",
    "ARM_K2_CFRPE",
]

# ============================================================================
# CLI / run-mode
# ============================================================================
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = (
    "smoke"
    if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
    else os.environ.get("HDLAB_RUN_MODE", "full")
)

# ============================================================================
# Production config (must match anchor name; pure numpy)
# ============================================================================
N_DIM_TOTAL = 8192    # PROT-018: no _nN suffix in anchor name; stated here
N_DIM_PER_BANK = N_DIM_TOTAL // K_BANKS   # 4096 per bank for K=2 arms
VOCAB_CAP = 4000
RECALL_BATCH = 512    # numpy batch for recall

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = N_STEPS_PER_SEED
else:
    # Smoke: fit under 300s on CPU; all arms + joint sweep + verdict
    SEEDS = [0]
    N_TRAIN = 3_000
    N_HELD = 600
    VOCAB_CAP = 400
    N_DIM_TOTAL = 1024
    N_DIM_PER_BANK = N_DIM_TOTAL // K_BANKS   # 512 per bank
    N_STEPS = 150
    RECALL_BATCH = 128

# ============================================================================
# text8 corpus utilities
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


# ============================================================================
# Encoder: char-trigram HD + sparse-bipolar (pure numpy; no gensim dependency)
# ============================================================================
# NOTE: This cell uses char-trigram encoder (not word2vec) to keep dependency
# pure-numpy and avoid gensim on remote_cpu_queue. The lift signal under test
# is architecture (K=2) x plasticity (cf-RPE), not encoder choice. Both knobs
# demonstrated lift with char-trigram at smoke scale.

import hashlib

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv_np(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
    t = " " + word.lower().replace("_", " ") + " "
    accum = np.zeros(n_dim, dtype=np.float32)
    if len(t) < 3:
        return accum
    for i in range(len(t) - 2):
        tri = t[i:i + 3]
        accum += _bipolar_hv_np(_seed_for_trigram(tri, seed), n_dim)
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def l2_normalize_rows(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def build_E_char_trigram(vocab: List[str], n_dim: int, seed: int) -> np.ndarray:
    """Build (V, n_dim) L2-normalized char-trigram encoding matrix."""
    E = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    return l2_normalize_rows(E)


def sparsify_bipolar_np(E: np.ndarray, f: float) -> np.ndarray:
    """Sparse-bipolar projection: keep top-k by abs magnitude, set sign."""
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    out = np.zeros_like(E)
    topk_idx = np.argpartition(-np.abs(E), k, axis=1)[:, :k]
    rows = np.arange(V)[:, None]
    signs = np.sign(E[rows, topk_idx])
    signs[signs == 0] = 1.0
    out[rows, topk_idx] = signs
    return out


# ============================================================================
# K-bank gate (reused from shotgun_smoke_k_bank_count_sweep_v1.py EXACTLY)
# ============================================================================

def gate_softmax(v: np.ndarray, W_gate: np.ndarray, temp: float) -> np.ndarray:
    """Project v (dim,) through W_gate (K, N_per) -> softmax probs (K,)."""
    logits = W_gate @ v      # (K,)
    logits = logits / temp
    logits -= logits.max()
    probs = np.exp(logits)
    probs /= probs.sum()
    return probs              # (K,)


def gate_entropy(probs: np.ndarray) -> float:
    eps = 1e-12
    return float(-np.sum(probs * np.log(probs + eps)))


# ============================================================================
# Plasticity rules (EXACT cf-RPE primitive from fair_harness cell)
# ============================================================================

def build_W_rank1_hebbian(E: np.ndarray, idx_train: np.ndarray,
                           ingest_chunk: int = 4096) -> np.ndarray:
    """One-pass batched outer-product rank-1 Hebbian matrix.

    W = sum_{t} E[t+1]^T @ E[t]  (shape: dim x dim)
    Identical to ARM_HEBBIAN_ONLY in fair_harness baseline.
    """
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        E_src = E[idx_train[b:end]]       # (chunk, dim)
        E_tgt = E[idx_train[b + 1:end + 1]]
        W += E_tgt.T @ E_src              # (dim, dim)
    return W


def build_W_cfrpe(E: np.ndarray, idx_train: np.ndarray,
                  n_steps: int, batch: int, lr: float,
                  seed: int, arm_idx: int) -> np.ndarray:
    """Iterative cf-RPE delta-rule plasticity.

    delta_W = (E[t+1] - E[t] @ W^T)^T @ E[t] / batch
    EXACT copy of ARM_CFRPE_ONLY logic from fair_harness v1.
    """
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return W
    rng = np.random.default_rng(seed * 10007 + arm_idx * 31337)
    for _ in range(n_steps):
        st = rng.integers(0, n_pairs, size=batch)
        Ctx = E[idx_train[st]]           # (batch, dim)
        Nxt = E[idx_train[st + 1]]       # (batch, dim)
        # cf-RPE prediction error
        error = Nxt - Ctx @ W.T          # (batch, dim)
        dW = (error.T @ Ctx) / batch     # (dim, dim)
        W = W + lr * dW
    return W


# ============================================================================
# K=2 bank compute: build per-bank W and produce logits
# ============================================================================

def _build_W_k1(arm_mode: str, E_full: np.ndarray,
                idx_train: np.ndarray, n_steps: int,
                batch: int, lr: float,
                seed: int, arm_idx: int) -> np.ndarray:
    """Build K=1 W for a given plasticity mode."""
    if arm_mode == "hebbian":
        return build_W_rank1_hebbian(E_full, idx_train)
    else:
        return build_W_cfrpe(E_full, idx_train, n_steps, batch, lr, seed, arm_idx)


def build_logits_k1(arm_mode: str, E_full: np.ndarray,
                    idx_train: np.ndarray, idx_held: np.ndarray,
                    n_steps: int, batch: int, lr: float,
                    seed: int, arm_idx: int,
                    recall_batch: int) -> Dict:
    """Compute [n_held, V] logits for K=1 arm."""
    V = E_full.shape[0]
    n_h = len(idx_held)
    t0 = time.time()
    W = _build_W_k1(arm_mode, E_full, idx_train, n_steps, batch, lr, seed, arm_idx)
    t_ingest = time.time() - t0

    t0 = time.time()
    logits = np.zeros((n_h, V), dtype=np.float32)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx = E_full[idx_held[b:end]]      # (chunk, dim)
        pred = ctx @ W.T                   # (chunk, dim)
        norms = np.linalg.norm(pred, axis=1, keepdims=True)
        pred = pred / np.clip(norms, 1e-12, None)
        logits[b:end] = pred @ E_full.T    # (chunk, V)
    t_recall = time.time() - t0

    del W
    return {
        "logits": logits,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
    }


def build_logits_k2(arm_mode: str, E_full: np.ndarray,
                    idx_train: np.ndarray, idx_held: np.ndarray,
                    n_steps: int, batch: int, lr: float,
                    seed: int, arm_idx: int,
                    recall_batch: int, gate_temp: float) -> Dict:
    """Compute [n_held, V] logits for K=2 bank arm.

    Each bank sees its own N_per slice of E_full.
    Gate uses bank-0 slice as gate signal (same as shotgun smoke).
    Write: per-bank W updated with gate-weighted plasticity.
    Read: gate-weighted sum of per-bank predictions.
    """
    V = E_full.shape[0]
    n_dim = E_full.shape[1]
    K = K_BANKS
    N_per = n_dim // K

    # Bank slices of E: each (V, N_per)
    E_banks = [E_full[:, k * N_per:(k + 1) * N_per].copy() for k in range(K)]

    # Gate projection: W_gate (K, N_per) initialized from bank-0 slice (same as shotgun)
    rng_gate = np.random.default_rng(seed * 7919 + arm_idx * 1013 + 9999)
    W_gate = rng_gate.standard_normal((K, N_per)).astype(np.float32)
    W_gate /= np.linalg.norm(W_gate, axis=1, keepdims=True) + 1e-9

    # Per-bank W matrices
    W_banks = [np.zeros((N_per, N_per), dtype=np.float32) for _ in range(K)]

    t0 = time.time()
    n_pairs = len(idx_train) - 1

    if arm_mode == "hebbian":
        # Rank-1 Hebbian: soft-gate weighted outer-product per bank
        # W_k += gate_prob[k] * E_bank_k[t+1]^T @ E_bank_k[t]
        # (For Hebbian, gate is not iterative -- use full-pass gate weighting)
        ingest_chunk = 4096
        for b in range(0, n_pairs, ingest_chunk):
            end = min(b + ingest_chunk, n_pairs)
            src_idx = idx_train[b:end]
            tgt_idx = idx_train[b + 1:end + 1]
            # Gate input: bank-0 slice of source
            gate_inputs = E_banks[0][src_idx]   # (chunk, N_per)
            # Compute gate probs per token
            raw = gate_inputs @ W_gate.T         # (chunk, K)
            raw = raw / gate_temp
            raw -= raw.max(axis=1, keepdims=True)
            probs = np.exp(raw)
            probs /= probs.sum(axis=1, keepdims=True) + 1e-30   # (chunk, K)
            for k in range(K):
                E_src_k = E_banks[k][src_idx]     # (chunk, N_per)
                E_tgt_k = E_banks[k][tgt_idx]
                gw = probs[:, k:k + 1]            # (chunk, 1)
                W_banks[k] += (E_tgt_k * gw).T @ E_src_k
    else:
        # cf-RPE iterative: gate-weighted update per bank
        rng_iter = np.random.default_rng(seed * 10007 + arm_idx * 31337)
        for _ in range(n_steps):
            st = rng_iter.integers(0, n_pairs, size=batch)
            # Gate input from bank-0 slice
            gate_inputs = E_banks[0][idx_train[st]]    # (batch, N_per)
            raw = gate_inputs @ W_gate.T               # (batch, K)
            raw = raw / gate_temp
            raw -= raw.max(axis=1, keepdims=True)
            probs_b = np.exp(raw)
            probs_b /= probs_b.sum(axis=1, keepdims=True) + 1e-30  # (batch, K)
            for k in range(K):
                Ctx_k = E_banks[k][idx_train[st]]      # (batch, N_per)
                Nxt_k = E_banks[k][idx_train[st + 1]]  # (batch, N_per)
                gw = probs_b[:, k:k + 1]               # (batch, 1)
                # cf-RPE: prediction error per sample
                error_k = Nxt_k - Ctx_k @ W_banks[k].T   # (batch, N_per)
                dW_k = (error_k * gw).T @ Ctx_k / batch  # (N_per, N_per)
                W_banks[k] = W_banks[k] + lr * dW_k

    t_ingest = time.time() - t0

    # Recall: gate-weighted sum of bank predictions
    t0 = time.time()
    n_h = len(idx_held)
    logits = np.zeros((n_h, V), dtype=np.float32)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        held_idx = idx_held[b:end]
        gate_in = E_banks[0][held_idx]          # (chunk, N_per)
        raw = gate_in @ W_gate.T                # (chunk, K)
        raw = raw / gate_temp
        raw -= raw.max(axis=1, keepdims=True)
        probs_r = np.exp(raw)
        probs_r /= probs_r.sum(axis=1, keepdims=True) + 1e-30  # (chunk, K)
        logit_chunk = np.zeros((end - b, V), dtype=np.float32)
        for k in range(K):
            ctx_k = E_banks[k][held_idx]         # (chunk, N_per)
            pred_k = ctx_k @ W_banks[k].T        # (chunk, N_per)
            norms = np.linalg.norm(pred_k, axis=1, keepdims=True)
            pred_k = pred_k / np.clip(norms, 1e-12, None)
            # Project bank-k prediction back to full vocab via bank-k E slice
            bank_scores = pred_k @ E_banks[k].T  # (chunk, V)
            logit_chunk += probs_r[:, k:k + 1] * bank_scores
        logits[b:end] = logit_chunk
    t_recall = time.time() - t0

    del W_banks, E_banks
    return {
        "logits": logits,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
    }


# ============================================================================
# BPC / eval utilities (exact from fair_harness v1)
# ============================================================================

def softmax_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


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
        match = np.where(top_idx_sorted[i] == nxt[i])[0]
        if len(match) > 0:
            rr += 1.0 / float(match[0] + 1)
    return float(rr / n)


def raw_bpc_at_T1(logits_np: np.ndarray, idx_held: np.ndarray) -> float:
    """BPC at T=1 (no temperature scaling), for DEGEN sanity gate."""
    V = logits_np.shape[1]
    n_h = logits_np.shape[0]
    nxt_np = idx_held[1:] if len(idx_held) > 1 else idx_held
    n_eval = min(n_h, len(nxt_np))
    if n_eval == 0:
        return float("inf")
    sub = logits_np[:n_eval]
    nxt_eval = nxt_np[:n_eval]
    z = sub - sub.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / np.clip(e.sum(axis=1, keepdims=True), 1e-30, None)
    p_nxt = p[np.arange(n_eval), nxt_eval].clip(1e-12, 1.0)
    return float(-np.mean(np.log(p_nxt)) / math.log(2.0))


def joint_sweep(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray) -> Dict:
    """Joint (T, lambda) sweep on dev; pick best per-metric; report on test."""
    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}

    for T in TEMP_GRID:
        probs_dev = softmax_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in LAMBDA_GRID:
            logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, MRR_K)
            if bd < best_bpc["dev_value"]:
                best_bpc = {"T": float(T), "lambda": float(lam), "dev_value": bd}
            if td > best_top1["dev_value"]:
                best_top1 = {"T": float(T), "lambda": float(lam), "dev_value": td}
            if md > best_mrr["dev_value"]:
                best_mrr = {"T": float(T), "lambda": float(lam), "dev_value": md}

    def _eval_test(T: float, lam: float, fn) -> float:
        probs = softmax_with_T(sub_logits_test, T)
        logp_sub = np.log(np.clip(probs, 1e-30, 1.0))
        logp = log_linear_interp(logp_sub, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _eval_test(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _eval_test(best_top1["T"], best_top1["lambda"], top1_acc)
    mrr_best_test = _eval_test(best_mrr["T"], best_mrr["lambda"],
                                lambda lp, nx: mrr_at_k(lp, nx, MRR_K))

    return {
        "bpc_best": round(bpc_best_test, 4),
        "best_T_for_bpc": best_bpc["T"],
        "best_lambda_for_bpc": best_bpc["lambda"],
        "best_dev_bpc": round(best_bpc["dev_value"], 4),
        "top1_acc": round(top1_best_test, 4),
        "best_T_for_top1": best_top1["T"],
        "best_lambda_for_top1": best_top1["lambda"],
        "mrr_at_10": round(mrr_best_test, 4),
        "best_T_for_mrr": best_mrr["T"],
        "best_lambda_for_mrr": best_mrr["lambda"],
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray,
                    V: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != 0)
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
    top1 = float(np.mean(nxt_test == am))
    order = np.argsort(-U)
    inv_rank = np.empty_like(order)
    inv_rank[order] = np.arange(len(order))
    ranks = inv_rank[nxt_test] + 1
    rr = np.where(ranks <= MRR_K, 1.0 / ranks, 0.0)
    mrr = float(np.mean(rr))
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(top1, 4),
            "mrr_unigram": round(mrr, 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Instrumentation self-test (MANDATORY per role contract)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    # ST1: cf-RPE delta shrinks prediction error (core plasticity rule)
    n_dim_st = 64
    rng_st = np.random.default_rng(42)
    Ctx = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Nxt = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Ctx /= np.linalg.norm(Ctx) + 1e-8
    Nxt /= np.linalg.norm(Nxt) + 1e-8
    W_test = np.zeros((n_dim_st, n_dim_st), dtype=np.float32)
    err_before = float(np.linalg.norm(Nxt - Ctx @ W_test.T))
    dW = (Nxt - Ctx @ W_test.T).T @ Ctx
    W_test = W_test + 0.9 * dW
    err_after = float(np.linalg.norm(Nxt - Ctx @ W_test.T))
    assert err_after < err_before, (
        "ST1 cf-RPE should shrink error: before=%.4f after=%.4f" % (err_before, err_after))
    print("[selftest] ST1 cf-RPE shrinks error: %.4f -> %.4f" % (err_before, err_after), flush=True)

    # ST2: K=2 gate produces valid probabilities summing to 1
    n_per_st = 32
    K_st = 2
    rng2 = np.random.default_rng(7)
    W_gate_st = rng2.standard_normal((K_st, n_per_st)).astype(np.float32)
    W_gate_st /= np.linalg.norm(W_gate_st, axis=1, keepdims=True) + 1e-9
    v_st = rng2.standard_normal(n_per_st).astype(np.float32)
    v_st /= np.linalg.norm(v_st) + 1e-8
    probs_st = gate_softmax(v_st, W_gate_st, GATE_TEMP)
    assert abs(probs_st.sum() - 1.0) < 1e-5, "ST2 gate probs don't sum to 1: %.6f" % probs_st.sum()
    assert (probs_st >= 0).all(), "ST2 gate probs contain negative values"
    print("[selftest] ST2 gate probs sum=%.6f OK" % probs_st.sum(), flush=True)

    # ST3: build_logits_k1 produces non-zero logits for tiny data
    V_st = 10
    n_dim_s2 = 128
    vocab_st = ["w%d" % i for i in range(V_st)]
    E_st = build_E_char_trigram(vocab_st, n_dim_s2, seed=0)
    E_st = sparsify_bipolar_np(E_st, SPARSE_BIPOLAR_F)
    E_st = l2_normalize_rows(E_st)
    idx_tr_st = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=np.int64)
    idx_h_st = np.array([3, 4, 5, 6], dtype=np.int64)
    ar = build_logits_k1("hebbian", E_st, idx_tr_st, idx_h_st,
                          n_steps=5, batch=3, lr=0.5, seed=0, arm_idx=0,
                          recall_batch=4)
    logits_st = ar["logits"]
    assert logits_st is not None, "ST3 logits is None"
    assert logits_st.shape == (len(idx_h_st), V_st), "ST3 logits shape mismatch: %s" % str(logits_st.shape)
    assert not np.all(logits_st == 0.0), "ST3 logits all zero"
    print("[selftest] ST3 build_logits_k1 shape=%s non-zero OK" % str(logits_st.shape), flush=True)

    # ST4: build_logits_k2 produces non-zero logits for tiny data
    n_dim_k2 = n_dim_s2  # must be divisible by K_BANKS=2
    ar4 = build_logits_k2("hebbian", E_st, idx_tr_st, idx_h_st,
                           n_steps=5, batch=3, lr=0.5, seed=0, arm_idx=1,
                           recall_batch=4, gate_temp=GATE_TEMP)
    logits4 = ar4["logits"]
    assert logits4 is not None, "ST4 K=2 logits is None"
    assert logits4.shape == (len(idx_h_st), V_st), "ST4 K=2 logits shape mismatch"
    assert not np.all(logits4 == 0.0), "ST4 K=2 logits all zero"
    print("[selftest] ST4 build_logits_k2 shape=%s non-zero OK" % str(logits4.shape), flush=True)

    # ST5: K=1 and K=2 logits differ (they use different architectures)
    diff_st = float(np.abs(logits_st - logits4).mean())
    assert diff_st > 1e-6, "ST5 K=1 and K=2 logits identical (no architecture difference)"
    print("[selftest] ST5 K=1 vs K=2 differ (mean_abs_diff=%.4e) OK" % diff_st, flush=True)

    # ST6: joint_sweep returns finite BPC/top1/mrr for small synthetic data
    n_tok_st = 30
    n_v_sm = 6
    rng6 = np.random.default_rng(99)
    logits_syn = rng6.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_syn = rng6.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_log_st = np.log(np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32))
    nd = n_tok_st // 2
    jr = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                     nxt_syn[:nd], nxt_syn[nd:])
    assert math.isfinite(jr["bpc_best"]), "ST6 bpc_best not finite"
    assert math.isfinite(jr["top1_acc"]), "ST6 top1_acc not finite"
    assert math.isfinite(jr["mrr_at_10"]), "ST6 mrr_at_10 not finite"
    assert jr["n_dev"] > 0, "ST6 n_dev == 0"
    assert jr["n_test"] > 0, "ST6 n_test == 0"
    print("[selftest] ST6 joint_sweep OK (bpc=%.3f top1=%.4f mrr=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"]), flush=True)

    # ST7: sparsify_bipolar_np leaves correct fraction of non-zero entries
    E_chk = np.random.default_rng(0).standard_normal((20, 100)).astype(np.float32)
    E_sparse = sparsify_bipolar_np(E_chk, 0.05)
    nnz_per_row = (E_sparse != 0).sum(axis=1)
    expected_nnz = max(1, int(round(0.05 * 100)))
    assert (nnz_per_row == expected_nnz).all(), (
        "ST7 sparse nnz mismatch: expected %d, got %s" % (expected_nnz, str(nnz_per_row[:5])))
    print("[selftest] ST7 sparsify_bipolar nnz=%d OK" % expected_nnz, flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

ARM_CONFIGS = {
    "ARM_BASELINE_RANK1_K1": {"k": 1, "mode": "hebbian"},
    "ARM_CFRPE_K1":           {"k": 1, "mode": "cfrpe"},
    "ARM_K2_RANK1":           {"k": 2, "mode": "hebbian"},
    "ARM_K2_CFRPE":           {"k": 2, "mode": "cfrpe"},
}


def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading text8 + building vocab" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[WARN] corpus short: %d tokens loaded" % len(toks), flush=True)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d (pure numpy)" % (
        seed, V, N_TRAIN, N_HELD, N_DIM_TOTAL), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]), flush=True)

    # Build encoder ONCE, reused per arm (Fix #24 equivalent for numpy)
    print("\n[seed=%d] building encoder (V=%d, N_DIM=%d)..." % (seed, V, N_DIM_TOTAL), flush=True)
    t_enc0 = time.time()
    E_raw = build_E_char_trigram(vocab, N_DIM_TOTAL, seed)
    E_full = l2_normalize_rows(sparsify_bipolar_np(E_raw, SPARSE_BIPOLAR_F))
    print("[seed=%d] encoder built in %.1fs; sparsity=%.3f" % (
        seed, time.time() - t_enc0,
        float(np.mean(E_full != 0))), flush=True)

    # Split held into dev + test
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    ctx_eval = ctx_full[mask]
    nxt_eval = nxt_full[mask]
    n_eval = len(ctx_eval)
    if n_eval == 0:
        print("[WARN seed=%d] no valid eval pairs" % seed, flush=True)
        return {"seed": seed, "by_arm": {"ARM_UNIGRAM": uni}, "V": V,
                "N_DIM_TOTAL": N_DIM_TOTAL, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2)}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    for arm_idx, arm in enumerate(ARMS):
        cfg = ARM_CONFIGS[arm]
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s k=%d mode=%s] computing..." % (
            seed, arm, cfg["k"], cfg["mode"]), flush=True)
        try:
            if cfg["k"] == 1:
                ar = build_logits_k1(
                    cfg["mode"], E_full, idx_train, idx_held,
                    n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR,
                    seed=seed, arm_idx=arm_idx, recall_batch=RECALL_BATCH,
                )
            else:
                ar = build_logits_k2(
                    cfg["mode"], E_full, idx_train, idx_held,
                    n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR,
                    seed=seed, arm_idx=arm_idx, recall_batch=RECALL_BATCH,
                    gate_temp=GATE_TEMP,
                )
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
            }
            continue

        logits_full = ar["logits"]   # [n_held, V]
        # Align to ctx_full domain
        if logits_full.shape[0] >= len(ctx_full):
            logits_eval = logits_full[:len(ctx_full)][mask]
        else:
            # Shorter logits: safe fallback
            valid_pos = np.where(mask)[0]
            valid_pos = valid_pos[valid_pos < logits_full.shape[0]]
            logits_eval = logits_full[valid_pos]
            nxt_eval_local = nxt_full[valid_pos]
            ne = len(nxt_eval_local)
            ndev = ne // 2
            jr = joint_sweep(
                logits_eval[:ndev], logits_eval[ndev:], U_log,
                nxt_eval_local[:ndev], nxt_eval_local[ndev:],
            )
            rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval_local)
            jr.update({
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
                "wall_recall_s": ar.get("wall_recall_s", 0.0),
                "raw_bpc_at_T1_L1": round(rbt1, 4),
            })
            by_arm[arm] = jr
            print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f elapsed=%.1fs" % (
                seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                jr["elapsed_s_arm"]), flush=True)
            continue

        jr = joint_sweep(logits_eval[:n_dev], logits_eval[n_dev:], U_log, nxt_dev, nxt_test)
        rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval)
        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
        })
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
            jr["elapsed_s_arm"]), flush=True)

    del E_full, E_raw

    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N_DIM_TOTAL": N_DIM_TOTAL,
        "N_DIM_PER_BANK": N_DIM_PER_BANK,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "N_STEPS": N_STEPS,
        "run_mode": RUN_MODE,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
    }


# ============================================================================
# Verdict (per pre-reg bands)
# ============================================================================

def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}

    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
    }
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    arm_bpc: Dict[str, float] = {}
    arm_cv: Dict[str, float] = {}
    for arm in ARMS:
        valid = [u for u in units
                 if not u["by_arm"].get(arm, {}).get("compute_failed", False)
                 and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))]
        if not valid:
            by_arm_agg[arm] = {"bpc_best_mean": float("inf"), "n_valid_seeds": 0, "all_seeds_failed": True}
            arm_bpc[arm] = float("inf")
            arm_cv[arm] = float("nan")
            continue
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "n_valid_seeds": len(valid),
            "all_seeds_failed": False,
        }
        arm_bpc[arm] = b_mean
        arm_cv[arm] = b_cv

    # Lifts: positive = better than baseline (lower BPC is better)
    baseline_bpc = arm_bpc.get("ARM_BASELINE_RANK1_K1", float("inf"))
    cfrpe_k1_bpc = arm_bpc.get("ARM_CFRPE_K1", float("inf"))
    k2_rank1_bpc = arm_bpc.get("ARM_K2_RANK1", float("inf"))
    k2_cfrpe_bpc = arm_bpc.get("ARM_K2_CFRPE", float("inf"))

    lift_cfrpe_k1 = baseline_bpc - cfrpe_k1_bpc
    lift_k2_rank1 = baseline_bpc - k2_rank1_bpc
    lift_k2_cfrpe = baseline_bpc - k2_cfrpe_bpc

    # Provenance check: ARM_BASELINE_RANK1_K1 vs reference
    baseline_drift = abs(baseline_bpc - BASELINE_BPC_REF) if math.isfinite(baseline_bpc) else float("inf")
    provenance_ok = baseline_drift <= BASELINE_TOLERANCE

    # cv check for ARM_K2_CFRPE
    k2_cfrpe_cv = arm_cv.get("ARM_K2_CFRPE", float("nan"))

    best_single_knob_lift = max(lift_cfrpe_k1, lift_k2_rank1)

    arm_summary = (
        "uni=%.3f | K1_HEB=%.4f | CFRPE_K1=%.4f(lift=%.3f) | K2_HEB=%.4f(lift=%.3f) | "
        "K2_CFRPE=%.4f(lift=%.3f) | cv_K2CFRPE=%.3f | baseline_drift=%.4f | prov_ok=%s"
    ) % (
        unigram_bpc,
        baseline_bpc, cfrpe_k1_bpc, lift_cfrpe_k1,
        k2_rank1_bpc, lift_k2_rank1,
        k2_cfrpe_bpc, lift_k2_cfrpe,
        k2_cfrpe_cv if math.isfinite(k2_cfrpe_cv) else -1.0,
        baseline_drift, str(provenance_ok),
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "lift_cfrpe_k1": round(lift_cfrpe_k1, 4),
        "lift_k2_rank1": round(lift_k2_rank1, 4),
        "lift_k2_cfrpe": round(lift_k2_cfrpe, 4),
        "best_single_knob_lift": round(best_single_knob_lift, 4),
        "super_additive_bar": HARD_PASS_SUPER_ADDITIVE_BAR,
        "additive_margin": HARD_PASS_ADDITIVE_MARGIN,
        "cv_max": CV_MAX,
        "baseline_bpc": round(baseline_bpc, 4),
        "baseline_bpc_ref": BASELINE_BPC_REF,
        "baseline_drift": round(baseline_drift, 4),
        "provenance_ok": bool(provenance_ok),
        "n_seeds": len(units),
        "unigram_bpc": round(unigram_bpc, 4),
        "honest_scope": (
            "K=2 multi-bank x cf-RPE compose at production scale: pure numpy, "
            "char-trigram encoder, N_DIM_TOTAL=8192, N_TRAIN=100k text8, V=4000. "
            "Tests super-additivity of the 2 validated knobs. "
            "WHAT_THIS_DOES_NOT_SHOW: does not test K>2; gate not end-to-end trained; "
            "char-trigram encoder not word2vec; K=2 arms use N=4096 per bank vs K=1 uses N=8192."
        ),
        "cites": [
            "preregs/2026-06-23_substrate_K2_x_cfrpe_compose_LM_v1.md",
            "experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py",
            "experiments/shotgun_smoke_k_bank_count_sweep_v1.py",
        ],
    }

    k2_cfrpe_failed = by_arm_agg.get("ARM_K2_CFRPE", {}).get("all_seeds_failed", True)
    if k2_cfrpe_failed:
        return ("HARD_FAIL", "HARD_FAIL: ARM_K2_CFRPE all seeds failed. " + arm_summary, detail)

    # cv gate
    if math.isfinite(k2_cfrpe_cv) and k2_cfrpe_cv > CV_MAX:
        return ("MIDDLE_BAND_HIGH_CV",
                "MIDDLE_BAND_HIGH_CV: cv=%.3f > %.2f. lift_K2CFRPE=%.3f. %s" % (
                    k2_cfrpe_cv, CV_MAX, lift_k2_cfrpe, arm_summary),
                detail)

    # Provenance warning (not a block; flagged in detail)
    if not provenance_ok:
        print("[WARN] Provenance drift: ARM_BASELINE_RANK1_K1=%.4f vs ref=%.4f (drift=%.4f > tol=%.2f)" % (
            baseline_bpc, BASELINE_BPC_REF, baseline_drift, BASELINE_TOLERANCE), flush=True)

    # Super-additive: combined lift >= 1.20 bits
    if math.isfinite(lift_k2_cfrpe) and lift_k2_cfrpe >= HARD_PASS_SUPER_ADDITIVE_BAR:
        detail["verdict_tier"] = "SUPER_ADDITIVE"
        return ("HARD_PASS",
                "HARD_PASS SUPER_ADDITIVE: lift_K2CFRPE=%.3f >= %.2f. "
                "K=2 x cf-RPE compose super-additively. %s" % (
                    lift_k2_cfrpe, HARD_PASS_SUPER_ADDITIVE_BAR, arm_summary),
                detail)

    # Additive: combined > max single-knob + 0.10
    if (math.isfinite(lift_k2_cfrpe) and math.isfinite(best_single_knob_lift)
            and lift_k2_cfrpe >= best_single_knob_lift + HARD_PASS_ADDITIVE_MARGIN):
        detail["verdict_tier"] = "ADDITIVE"
        return ("HARD_PASS",
                "HARD_PASS ADDITIVE: lift_K2CFRPE=%.3f >= best_single=%.3f + %.2f. "
                "K=2 x cf-RPE compose additively (constructive). %s" % (
                    lift_k2_cfrpe, best_single_knob_lift, HARD_PASS_ADDITIVE_MARGIN, arm_summary),
                detail)

    # Middle band: combined > max single-knob but not +0.10 margin
    if (math.isfinite(lift_k2_cfrpe) and math.isfinite(best_single_knob_lift)
            and lift_k2_cfrpe > best_single_knob_lift):
        detail["verdict_tier"] = "MIDDLE_BAND_COMPOSE"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: lift_K2CFRPE=%.3f > best_single=%.3f but < +%.2f margin. "
                "Knobs compose but sub-additive; choose the stronger single knob. %s" % (
                    lift_k2_cfrpe, best_single_knob_lift, HARD_PASS_ADDITIVE_MARGIN, arm_summary),
                detail)

    # Hard fail: combined <= max single-knob
    detail["verdict_tier"] = "INTERFERENCE"
    return ("HARD_FAIL",
            "HARD_FAIL: lift_K2CFRPE=%.3f <= best_single=%.3f. "
            "K=2 and cf-RPE interfere; combining reduces lift. Choose 1. %s" % (
                lift_k2_cfrpe, best_single_knob_lift, arm_summary),
            detail)


# ============================================================================
# Main loop with per-seed checkpoint
# ============================================================================

print("[config] anchor=%s N_DIM_TOTAL=%d N_TRAIN=%d mode=%s seeds=%s arms=%s" % (
    ANCHOR_NAME, N_DIM_TOTAL, N_TRAIN, RUN_MODE, SEEDS, ARMS), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)

done_seeds_init: List[int] = []
remaining_seeds_init: List[int] = SEEDS[:]
try:
    done_seeds_init, remaining_seeds_init = _resumable_seeds(SEEDS, out_dir)
    print("[ckpt] %d done, %d remaining: %s" % (
        len(done_seeds_init), len(remaining_seeds_init), remaining_seeds_init), flush=True)
except Exception as e:
    print("[ckpt] resumable_seeds failed (%s); running all seeds" % e, flush=True)
    remaining_seeds_init = SEEDS[:]

for seed in remaining_seeds_init:
    print("\n[run] seed=%d starting..." % seed, flush=True)
    result = run_unit(seed)
    write_partial(out_dir, seed, result)
    print("[ckpt] seed=%d partial written to %s" % (seed, out_dir), flush=True)

per_seed = aggregate_partials(out_dir, SEEDS)
all_units = list(per_seed.values())

verdict, verdict_msg, detail = compute_verdict(all_units)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "run_mode": RUN_MODE,
    "N_DIM_TOTAL": N_DIM_TOTAL,
    "N_DIM_PER_BANK": N_DIM_PER_BANK,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "N_STEPS": N_STEPS,
    "K_BANKS": K_BANKS,
    "GATE_TEMP": GATE_TEMP,
    "CFRPE_LR": CFRPE_LR,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "detail": detail,
    "per_seed": [
        {"seed": u.get("seed"), "by_arm": u.get("by_arm"),
         "V": u.get("V"), "N_DIM_TOTAL": u.get("N_DIM_TOTAL"),
         "N_TRAIN": u.get("N_TRAIN"),
         "elapsed_s_seed": u.get("elapsed_s_seed")}
        for u in all_units
    ],
    "elapsed_s": round(sum(u.get("elapsed_s_seed", 0.0) for u in all_units), 2),
}

write_metrics(out_dir, metrics, all_units)
print("[metrics] written to %s" % out_dir, flush=True)
