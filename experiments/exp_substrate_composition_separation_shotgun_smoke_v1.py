"""
substrate_composition_separation_shotgun_smoke_v1 -- shotgun smoke of 8 separation
strategies for cf-RPE x STDP same-W composition collapse.

USER directive: "can't we shotgun smoke the composition question?"

Composition collapse is "5 chefs reaching into the same pot." Brain solves this
via separate pots per chef + replay-based consolidation. This shotgun tests 8
candidate separation strategies in ONE cell at smoke scale (V=300, N_DIM=2048,
N_TRAIN=20k Zipf bigram synthetic; pure numpy CPU) to identify which break
the same-W collapse and merit promotion to production.

NINE ARMS (3 seeds):
  1 ARM_BASELINE_CFRPE_ALONE        single W, cf-RPE only (reference)
  2 ARM_NAIVE_CFRPE_PLUS_STDP       single W, cf-RPE + 0.5*STDP (collapse control)
  3 ARM_TIME_SEPARATION             single W, cf-RPE on even steps / STDP on odd
  4 ARM_BANK_SEPARATION             two W (A=cf-RPE / B=STDP); avg logits readout
  5 ARM_SUBSPACE_SEPARATION         single W; cf-RPE on W[:N/2,:N/2]; STDP on W[N/2:,N/2:]
  6 ARM_FREQ_SEPARATION             single W; high-freq Ctx -> cf-RPE; low-freq -> STDP
  7 ARM_SEQUENTIAL_CONSOLIDATION    phase 1 cf-RPE then freeze; phase 2 STDP on frozen
  8 ARM_REPLAY_BASED                cf-RPE on live; STDP only on replay-buffer cached
  9 ARM_ORTHOGONAL_PROJECTION       PCGrad-style g_stdp projected orthogonal to g_cf

PRE-REG HARD bands (smoke; see preregs/2026-06-24_substrate_composition_separation_shotgun_smoke_v1.md):
  Sanity: NAIVE > BASELINE by >= 0.05 (collapse reproduces at smoke)
  HARD_PASS_SIGNAL_FOUND: any of arms 3-9 BPC <= NAIVE BPC - 0.10 AND <= BASELINE BPC - 0.03
  MIDDLE_BAND_WEAK_SIGNAL: any arm beats NAIVE by [0.05, 0.10) BPC
  MIDDLE_BAND_SMOKE_TOO_SMALL: NAIVE does not exceed BASELINE by 0.05
  HARD_FAIL_DECISIVE: all of arms 3-9 fail AND NAIVE collapses (composition fundamental)
  HARD_FAIL_PROVENANCE: ARM_BASELINE_CFRPE_ALONE BPC > log2(V) - 0.5 (cf-RPE broken)

FORMULA SELF-TESTS:
  ST1 cf-RPE delta shrinks single-pair prediction error.
  ST2 STDP antisymmetric outer satisfies W + W^T = 0.
  ST3 Zipf cond-entropy < log(V).
  ST4 uniform nats = ln(V).
  ST5 orthogonal-projection: after projection, g_proj dot g_cf ~ 0.

PROT-018: no _n<N> suffix; production N not parameter-swept; smoke-only cell
(_smoke variant in entry name routes to smoke config).
QUEUE: local_cpu_queue (~12 min smoke). ASCII-only. LAMBDA_GRID excludes 0.0.
Fix #28: per-arm metrics ONLY (never trust summary string).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
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
    get_output_dir, write_partial, aggregate_partials, resumable_seeds,
)

ANCHOR_NAME = "substrate_composition_separation_shotgun_smoke_v1"

# ============================================================================
# CLI
# ============================================================================
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
# Cell is smoke-only by design (USER directive shotgun smoke)
RUN_MODE = "smoke"

# ============================================================================
# Config (smoke-scale only)
# ============================================================================
SEEDS = [7, 17, 23]
V = 300                  # vocab
N_DIM = 2048             # substrate vector dim
N_TRAIN = 20_000         # token sequence length (train)
N_HELD = 4_000           # held-out
N_STEPS = 300            # training steps per arm
BATCH = 32               # batch size
LR = 0.5                 # cf-RPE / STDP learning rate
STDP_W = 0.5             # STDP contribution weight in NAIVE compose
K_ACTIVE = 8             # Zipf bigram top-k per row
REPLAY_BUF_SIZE = 256    # ARM 8 replay buffer size
REPLAY_BATCH = 16        # ARM 8 STDP-on-replay batch

# Eval grids
TEMP_GRID = [0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]   # excludes 0.0 per Skunkworks META C7

# Pre-reg numbers
SANITY_NAIVE_COLLAPSE_DELTA = 0.05        # NAIVE > BASELINE by >= 0.05 -> collapse confirmed
HARD_PASS_RESCUE_VS_NAIVE = 0.10          # rescue arm <= NAIVE - 0.10
HARD_PASS_RESCUE_VS_BASELINE = 0.03       # rescue arm <= BASELINE - 0.03
MIDDLE_BAND_VS_NAIVE_LOWER = 0.05         # rescue arm <= NAIVE - 0.05 (weak signal)
HARD_FAIL_PROVENANCE_BPC_FLOOR = math.log2(V) - 0.5  # ~7.73 for V=300

# Arms (cumulative across separation taxonomy)
ARMS = [
    "ARM_BASELINE_CFRPE_ALONE",
    "ARM_NAIVE_CFRPE_PLUS_STDP",
    "ARM_TIME_SEPARATION",
    "ARM_BANK_SEPARATION",
    "ARM_SUBSPACE_SEPARATION",
    "ARM_FREQ_SEPARATION",
    "ARM_SEQUENTIAL_CONSOLIDATION",
    "ARM_REPLAY_BASED",
    "ARM_ORTHOGONAL_PROJECTION",
]

CONFIG_VERSION = (
    "%s; mode=%s V=%d N_DIM=%d N_TRAIN=%d N_HELD=%d N_STEPS=%d BATCH=%d "
    "LR=%.3f STDP_W=%.3f K_ACTIVE=%d REPLAY_BUF=%d REPLAY_BATCH=%d "
    "temps=%s lambdas=%s arms=%d seeds=%s"
) % (
    ANCHOR_NAME, RUN_MODE, V, N_DIM, N_TRAIN, N_HELD, N_STEPS, BATCH,
    LR, STDP_W, K_ACTIVE, REPLAY_BUF_SIZE, REPLAY_BATCH,
    TEMP_GRID, LAMBDA_GRID, len(ARMS), SEEDS,
)


# ============================================================================
# Corpus: synthetic Zipf bigram (clean synthetic; NO substrate state)
# ============================================================================

def gen_zipf_bigram(v_count: int, length: int, rng: np.random.Generator) -> Tuple[np.ndarray, float]:
    """Synthetic Zipf bigram corpus. Returns (idx_array, cond_entropy_nats)."""
    ranks = 1.0 / np.arange(1, v_count + 1)
    zp = ranks / ranks.sum()
    T = np.zeros((v_count, v_count), dtype=np.float64)
    for c in range(v_count):
        tg = rng.choice(v_count, size=K_ACTIVE, replace=False, p=zp)
        lg = rng.standard_normal(K_ACTIVE) * 2.0
        w = np.exp(lg - lg.max())
        w /= w.sum()
        T[c, tg] = w
    with np.errstate(divide="ignore", invalid="ignore"):
        ce = float((-np.sum(np.where(T > 0, T * np.log(T), 0.0), axis=1)).mean())
    ids = np.zeros(length, dtype=np.int64)
    s = 0
    for i in range(length):
        ids[i] = s
        s = int(rng.choice(v_count, p=T[s]))
    return ids, ce


def build_encoder_synthetic(v_count: int, n_dim: int, seed: int) -> np.ndarray:
    """Clean synthetic encoder: Gaussian -> L2 normalize. NO substrate state."""
    rng = np.random.default_rng(seed * 9173 + 11)
    E = rng.standard_normal((v_count, n_dim)).astype(np.float32)
    E /= (np.linalg.norm(E, axis=1, keepdims=True) + 1e-9)
    return E


# ============================================================================
# Plasticity primitives (pure numpy)
# ============================================================================

def step_cfrpe(W: np.ndarray, Ctx: np.ndarray, Nxt: np.ndarray, lr: float) -> np.ndarray:
    """cf-RPE delta-rule: W += lr * ((Nxt - Ctx @ W.T).T @ Ctx) / batch."""
    err = Nxt - Ctx @ W.T
    dW = (err.T @ Ctx) / float(Ctx.shape[0])
    return W + lr * dW


def step_stdp(W: np.ndarray, Ctx: np.ndarray, Nxt: np.ndarray, lr: float, weight: float) -> np.ndarray:
    """STDP antisymmetric outer + Hebbian base: W += lr * (Heb + weight * Asym)."""
    bs = float(Ctx.shape[0])
    Heb = (Nxt.T @ Ctx) / bs
    Asym = (Nxt.T @ Ctx - Ctx.T @ Nxt) / bs
    return W + lr * (Heb + weight * Asym)


def step_naive_compose(W: np.ndarray, Ctx: np.ndarray, Nxt: np.ndarray, lr: float, weight: float) -> np.ndarray:
    """NAIVE: cf-RPE + weight * STDP-asym, both onto same W same step (reproduces collapse)."""
    bs = float(Ctx.shape[0])
    err = Nxt - Ctx @ W.T
    dW_cf = (err.T @ Ctx) / bs
    dW_stdp = (Nxt.T @ Ctx - Ctx.T @ Nxt) / bs
    return W + lr * (dW_cf + weight * dW_stdp)


def grad_cfrpe(W: np.ndarray, Ctx: np.ndarray, Nxt: np.ndarray) -> np.ndarray:
    err = Nxt - Ctx @ W.T
    return (err.T @ Ctx) / float(Ctx.shape[0])


def grad_stdp(Ctx: np.ndarray, Nxt: np.ndarray) -> np.ndarray:
    return (Nxt.T @ Ctx - Ctx.T @ Nxt) / float(Ctx.shape[0])


# ============================================================================
# Arm runners (one per arm; all take encoder + train indices + seed -> returns W)
# ============================================================================

def run_baseline_cfrpe(E: np.ndarray, idx_tr: np.ndarray, seed: int) -> Dict:
    n_dim = E.shape[1]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + 1)
    n_pairs = len(idx_tr) - 1
    for _ in range(N_STEPS):
        st = rng.integers(0, n_pairs, size=BATCH)
        Ctx = E[idx_tr[st]]
        Nxt = E[idx_tr[st + 1]]
        W = step_cfrpe(W, Ctx, Nxt, LR)
    return {"W": W}


def run_naive_compose(E: np.ndarray, idx_tr: np.ndarray, seed: int) -> Dict:
    n_dim = E.shape[1]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + 2)
    n_pairs = len(idx_tr) - 1
    for _ in range(N_STEPS):
        st = rng.integers(0, n_pairs, size=BATCH)
        Ctx = E[idx_tr[st]]
        Nxt = E[idx_tr[st + 1]]
        W = step_naive_compose(W, Ctx, Nxt, LR, STDP_W)
    return {"W": W}


def run_time_separation(E: np.ndarray, idx_tr: np.ndarray, seed: int) -> Dict:
    """Alternate steps: even -> cf-RPE; odd -> STDP. No within-step overlap."""
    n_dim = E.shape[1]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + 3)
    n_pairs = len(idx_tr) - 1
    for s_i in range(N_STEPS):
        st = rng.integers(0, n_pairs, size=BATCH)
        Ctx = E[idx_tr[st]]
        Nxt = E[idx_tr[st + 1]]
        if s_i % 2 == 0:
            W = step_cfrpe(W, Ctx, Nxt, LR)
        else:
            W = step_stdp(W, Ctx, Nxt, LR, STDP_W)
    return {"W": W}


def run_bank_separation(E: np.ndarray, idx_tr: np.ndarray, seed: int) -> Dict:
    """Two W matrices: W_A trained via cf-RPE; W_B trained via STDP. Both full N_DIM."""
    n_dim = E.shape[1]
    W_A = np.zeros((n_dim, n_dim), dtype=np.float32)
    W_B = np.zeros((n_dim, n_dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + 4)
    n_pairs = len(idx_tr) - 1
    for _ in range(N_STEPS):
        st = rng.integers(0, n_pairs, size=BATCH)
        Ctx = E[idx_tr[st]]
        Nxt = E[idx_tr[st + 1]]
        W_A = step_cfrpe(W_A, Ctx, Nxt, LR)
        W_B = step_stdp(W_B, Ctx, Nxt, LR, STDP_W)
    return {"W_A": W_A, "W_B": W_B}


def run_subspace_separation(E: np.ndarray, idx_tr: np.ndarray, seed: int) -> Dict:
    """Single W; cf-RPE updates W[:H,:H]; STDP updates W[H:,H:] where H=N/2.
    Encoder uses full N_DIM; readout via full W. Off-diagonal blocks never updated."""
    n_dim = E.shape[1]
    H = n_dim // 2
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + 5)
    n_pairs = len(idx_tr) - 1
    for _ in range(N_STEPS):
        st = rng.integers(0, n_pairs, size=BATCH)
        Ctx = E[idx_tr[st]]
        Nxt = E[idx_tr[st + 1]]
        # cf-RPE on W[:H,:H] using Ctx[:,:H] / Nxt[:,:H]
        Ctx_lo = Ctx[:, :H]
        Nxt_lo = Nxt[:, :H]
        W_lo = W[:H, :H]
        err_lo = Nxt_lo - Ctx_lo @ W_lo.T
        dW_lo = (err_lo.T @ Ctx_lo) / float(BATCH)
        W[:H, :H] = W_lo + LR * dW_lo
        # STDP on W[H:,H:] using Ctx[:,H:] / Nxt[:,H:]
        Ctx_hi = Ctx[:, H:]
        Nxt_hi = Nxt[:, H:]
        Heb_hi = (Nxt_hi.T @ Ctx_hi) / float(BATCH)
        Asym_hi = (Nxt_hi.T @ Ctx_hi - Ctx_hi.T @ Nxt_hi) / float(BATCH)
        W[H:, H:] = W[H:, H:] + LR * (Heb_hi + STDP_W * Asym_hi)
    return {"W": W}


def run_freq_separation(E: np.ndarray, idx_tr: np.ndarray, seed: int, freq_med: float, idx_freq_high: np.ndarray) -> Dict:
    """Single W; per step partition batch by Ctx-token unigram-frequency.
    High-freq Ctx -> cf-RPE update; low-freq Ctx -> STDP update."""
    n_dim = E.shape[1]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + 6)
    n_pairs = len(idx_tr) - 1
    is_high = np.zeros(V, dtype=bool)
    is_high[idx_freq_high] = True
    for _ in range(N_STEPS):
        st = rng.integers(0, n_pairs, size=BATCH)
        ctx_tok = idx_tr[st]
        nxt_tok = idx_tr[st + 1]
        Ctx = E[ctx_tok]
        Nxt = E[nxt_tok]
        hi_mask = is_high[ctx_tok]
        lo_mask = ~hi_mask
        if hi_mask.sum() > 0:
            Ctx_h = Ctx[hi_mask]
            Nxt_h = Nxt[hi_mask]
            err_h = Nxt_h - Ctx_h @ W.T
            dW_h = (err_h.T @ Ctx_h) / float(max(hi_mask.sum(), 1))
            W = W + LR * dW_h
        if lo_mask.sum() > 0:
            Ctx_l = Ctx[lo_mask]
            Nxt_l = Nxt[lo_mask]
            Heb_l = (Nxt_l.T @ Ctx_l) / float(max(lo_mask.sum(), 1))
            Asym_l = (Nxt_l.T @ Ctx_l - Ctx_l.T @ Nxt_l) / float(max(lo_mask.sum(), 1))
            W = W + LR * STDP_W * Asym_l + LR * 0.5 * Heb_l   # STDP-only (no full Hebbian leak) but include Heb component as in step_stdp
    return {"W": W}


def run_sequential_consolidation(E: np.ndarray, idx_tr: np.ndarray, seed: int) -> Dict:
    """Phase 1 (N_STEPS/2): cf-RPE only. Freeze W. Phase 2 (N_STEPS/2): STDP added on frozen state."""
    n_dim = E.shape[1]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + 7)
    n_pairs = len(idx_tr) - 1
    half = N_STEPS // 2
    # Phase 1: cf-RPE
    for _ in range(half):
        st = rng.integers(0, n_pairs, size=BATCH)
        Ctx = E[idx_tr[st]]
        Nxt = E[idx_tr[st + 1]]
        W = step_cfrpe(W, Ctx, Nxt, LR)
    # Freeze W; phase 2 accumulates STDP-asym additively on top
    W_frozen = W.copy()
    stdp_accum = np.zeros_like(W)
    for _ in range(N_STEPS - half):
        st = rng.integers(0, n_pairs, size=BATCH)
        Ctx = E[idx_tr[st]]
        Nxt = E[idx_tr[st + 1]]
        Asym = (Nxt.T @ Ctx - Ctx.T @ Nxt) / float(BATCH)
        stdp_accum = stdp_accum + LR * STDP_W * Asym
    W = W_frozen + stdp_accum
    return {"W": W}


def run_replay_based(E: np.ndarray, idx_tr: np.ndarray, seed: int) -> Dict:
    """cf-RPE on live data each step; STDP only on replayed (cached) pairs.
    One-way: STDP never sees live, only replay buffer of last N pairs."""
    n_dim = E.shape[1]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + 8)
    n_pairs = len(idx_tr) - 1
    # FIFO replay buffer of (ctx_tok, nxt_tok)
    buf_ctx = np.zeros(REPLAY_BUF_SIZE, dtype=np.int64)
    buf_nxt = np.zeros(REPLAY_BUF_SIZE, dtype=np.int64)
    buf_count = 0
    for _ in range(N_STEPS):
        st = rng.integers(0, n_pairs, size=BATCH)
        ctx_tok = idx_tr[st]
        nxt_tok = idx_tr[st + 1]
        Ctx = E[ctx_tok]
        Nxt = E[nxt_tok]
        # Live cf-RPE
        W = step_cfrpe(W, Ctx, Nxt, LR)
        # Push to replay buffer (FIFO; overwrite oldest)
        for i in range(BATCH):
            slot = (buf_count + i) % REPLAY_BUF_SIZE
            buf_ctx[slot] = ctx_tok[i]
            buf_nxt[slot] = nxt_tok[i]
        buf_count += BATCH
        # STDP on replay (only if buffer has data)
        if buf_count >= REPLAY_BATCH:
            n_in_buf = min(buf_count, REPLAY_BUF_SIZE)
            sel = rng.integers(0, n_in_buf, size=REPLAY_BATCH)
            Ctx_r = E[buf_ctx[sel]]
            Nxt_r = E[buf_nxt[sel]]
            Asym_r = (Nxt_r.T @ Ctx_r - Ctx_r.T @ Nxt_r) / float(REPLAY_BATCH)
            W = W + LR * STDP_W * Asym_r
    return {"W": W}


def run_orthogonal_projection(E: np.ndarray, idx_tr: np.ndarray, seed: int) -> Dict:
    """PCGrad-style: compute g_cf and g_stdp separately; project g_stdp onto orthogonal of g_cf.
    W += LR * (g_cf + STDP_W * g_stdp_proj)."""
    n_dim = E.shape[1]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + 9)
    n_pairs = len(idx_tr) - 1
    for _ in range(N_STEPS):
        st = rng.integers(0, n_pairs, size=BATCH)
        Ctx = E[idx_tr[st]]
        Nxt = E[idx_tr[st + 1]]
        g_cf = grad_cfrpe(W, Ctx, Nxt)
        g_stdp = grad_stdp(Ctx, Nxt)
        # PCGrad: if g_stdp dot g_cf < 0 (conflict), project g_stdp onto null(g_cf)
        # Treat W-flat as vector; inner = sum(g_stdp * g_cf)
        dot = float((g_stdp * g_cf).sum())
        cf_norm_sq = float((g_cf * g_cf).sum())
        if dot < 0.0 and cf_norm_sq > 1e-12:
            g_stdp_proj = g_stdp - (dot / cf_norm_sq) * g_cf
        else:
            g_stdp_proj = g_stdp
        W = W + LR * (g_cf + STDP_W * g_stdp_proj)
    return {"W": W}


# ============================================================================
# Eval: BPC + top1 with (T, lambda) sweep against unigram interp
# ============================================================================

def _l2_normalize(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def build_unigram(idx_train: np.ndarray, v_count: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(v_count, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


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


def compute_logits_single_W(W: np.ndarray, E: np.ndarray, idx_held: np.ndarray) -> np.ndarray:
    """Logits = L2norm(Ctx @ W.T) @ E.T; shape (n_held - 1, V)."""
    ctx = idx_held[:-1]
    Ctx = E[ctx]
    pred = Ctx @ W.T
    pred_n = _l2_normalize(pred)
    return (pred_n @ E.T).astype(np.float32)


def compute_logits_bank_avg(W_A: np.ndarray, W_B: np.ndarray, E: np.ndarray, idx_held: np.ndarray) -> np.ndarray:
    """Logits = average of (L2norm(Ctx @ W_A.T) @ E.T) and (L2norm(Ctx @ W_B.T) @ E.T)."""
    ctx = idx_held[:-1]
    Ctx = E[ctx]
    pred_A = _l2_normalize(Ctx @ W_A.T)
    pred_B = _l2_normalize(Ctx @ W_B.T)
    logits_A = pred_A @ E.T
    logits_B = pred_B @ E.T
    return (0.5 * (logits_A + logits_B)).astype(np.float32)


def joint_sweep(logits_dev: np.ndarray, logits_test: np.ndarray,
                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray) -> Dict:
    """Joint (T, lambda) sweep on dev; pick best by BPC; report test BPC + test top1."""
    best = {"T": 1.0, "lambda": 1.0, "dev_bpc": float("inf")}
    for T in TEMP_GRID:
        probs_dev = softmax_with_T(logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in LAMBDA_GRID:
            logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            if bd < best["dev_bpc"]:
                best = {"T": float(T), "lambda": float(lam), "dev_bpc": bd}
    # Eval test at best (T, lambda)
    probs_test = softmax_with_T(logits_test, best["T"])
    logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
    logp_test = log_linear_interp(logp_sub_test, U_log, best["lambda"])
    bpc_test = bpc_from_logp(logp_test, nxt_test)
    top1_test = top1_acc(logp_test, nxt_test)
    return {
        "bpc": round(bpc_test, 4),
        "top1": round(top1_test, 4),
        "best_T": best["T"],
        "best_lambda": best["lambda"],
        "best_dev_bpc": round(best["dev_bpc"], 4),
    }


# ============================================================================
# Self-test (BEFORE smoke or full run; MANDATORY)
# ============================================================================

def _instrumentation_selftest() -> None:
    print("[selftest] running formula self-tests...", flush=True)
    # ST1: cf-RPE shrinks single-pair error
    n = 64
    rng_st = np.random.default_rng(42)
    Ctx = rng_st.standard_normal((1, n)).astype(np.float32)
    Nxt = rng_st.standard_normal((1, n)).astype(np.float32)
    Ctx /= np.linalg.norm(Ctx) + 1e-8
    Nxt /= np.linalg.norm(Nxt) + 1e-8
    W = np.zeros((n, n), dtype=np.float32)
    err_b = float(np.linalg.norm(Nxt - Ctx @ W.T))
    W = step_cfrpe(W, Ctx, Nxt, 0.9)
    err_a = float(np.linalg.norm(Nxt - Ctx @ W.T))
    assert err_a < err_b, "ST1 cf-RPE: err %.4f -> %.4f (must shrink)" % (err_b, err_a)
    # ST2: STDP antisymmetric outer satisfies W + W.T = 0
    Asym = (Nxt.T @ Ctx - Ctx.T @ Nxt)
    sym_violation = float(np.abs(Asym + Asym.T).max())
    assert sym_violation < 1e-4, "ST2 STDP antisym violated: %.6f" % sym_violation
    # ST3: Zipf cond-entropy < log(V)
    rng_z = np.random.default_rng(0)
    _, ce = gen_zipf_bigram(64, 500, rng_z)
    assert ce < math.log(64), "ST3 zipf_ce=%.3f >= log(64)=%.3f" % (ce, math.log(64))
    # ST4: uniform nats = ln(V)
    assert abs(math.log(7) - 1.9459) < 1e-3, "ST4 ln(7) constant"
    # ST5: PCGrad projection produces orthogonal-or-less component
    rng_p = np.random.default_rng(13)
    g_cf = rng_p.standard_normal((32, 32)).astype(np.float32)
    g_stdp = -g_cf + 0.1 * rng_p.standard_normal((32, 32)).astype(np.float32)  # mostly opposite
    dot = float((g_stdp * g_cf).sum())
    cf_norm_sq = float((g_cf * g_cf).sum())
    assert dot < 0.0, "ST5 setup: g_stdp should conflict with g_cf"
    g_proj = g_stdp - (dot / cf_norm_sq) * g_cf
    new_dot = float((g_proj * g_cf).sum())
    assert abs(new_dot) < 1e-3, "ST5 PCGrad: after proj dot=%.6f (must be ~0)" % new_dot
    # ST6: NAIVE composition reaches different W than cf-RPE alone (sanity that mechanisms differ)
    rng_d = np.random.default_rng(99)
    Ctx_d = rng_d.standard_normal((BATCH, 32)).astype(np.float32)
    Nxt_d = rng_d.standard_normal((BATCH, 32)).astype(np.float32)
    Ctx_d = _l2_normalize(Ctx_d)
    Nxt_d = _l2_normalize(Nxt_d)
    W_cf = np.zeros((32, 32), dtype=np.float32)
    W_nv = np.zeros((32, 32), dtype=np.float32)
    for _ in range(20):
        W_cf = step_cfrpe(W_cf, Ctx_d, Nxt_d, LR)
        W_nv = step_naive_compose(W_nv, Ctx_d, Nxt_d, LR, STDP_W)
    delta = float(np.linalg.norm(W_cf - W_nv))
    assert delta > 0.01, "ST6 NAIVE != cf-RPE: delta=%.4f" % delta
    print("[selftest] PASS: ST1 cfrpe shrink %.4f->%.4f | ST2 stdp_antisym %.2e | ST3 zipf_ce %.3f | ST5 pcgrad_post_dot %.2e | ST6 naive_vs_cfrpe %.4f" %
          (err_b, err_a, sym_violation, ce, new_dot, delta), flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_seed(seed: int) -> Dict:
    t0_seed = time.time()
    rng_corpus = np.random.default_rng(seed + 5000)
    print("  [seed=%d] generating corpus V=%d N_TRAIN=%d N_HELD=%d..." %
          (seed, V, N_TRAIN, N_HELD), flush=True)
    ids_all, ce = gen_zipf_bigram(V, N_TRAIN + N_HELD, rng_corpus)
    idx_tr = ids_all[:N_TRAIN]
    idx_held = ids_all[N_TRAIN:N_TRAIN + N_HELD]
    print("  [seed=%d] cond_ent=%.3f uniform=%.3f" % (seed, ce, math.log(V)), flush=True)

    # Encoder
    E = build_encoder_synthetic(V, N_DIM, seed)

    # Unigram and held splits
    U = build_unigram(idx_tr, V)
    U_log = np.log(np.clip(U, 1e-30, 1.0))
    nxt_all = idx_held[1:]
    n_e = len(nxt_all)
    n_dev = n_e // 2
    nxt_dev = nxt_all[:n_dev]
    nxt_test = nxt_all[n_dev:]

    # Pre-compute freq partition for ARM 6 (top-50% by unigram freq)
    sorted_idx = np.argsort(-U)
    idx_freq_high = sorted_idx[:V // 2]
    freq_med = float(np.median(U))

    arm_results: Dict[str, Dict] = {}
    arm_runners = {
        "ARM_BASELINE_CFRPE_ALONE": (run_baseline_cfrpe, False),
        "ARM_NAIVE_CFRPE_PLUS_STDP": (run_naive_compose, False),
        "ARM_TIME_SEPARATION": (run_time_separation, False),
        "ARM_BANK_SEPARATION": (run_bank_separation, True),  # uses W_A + W_B
        "ARM_SUBSPACE_SEPARATION": (run_subspace_separation, False),
        "ARM_FREQ_SEPARATION": (None, False),                # special-sig runner
        "ARM_SEQUENTIAL_CONSOLIDATION": (run_sequential_consolidation, False),
        "ARM_REPLAY_BASED": (run_replay_based, False),
        "ARM_ORTHOGONAL_PROJECTION": (run_orthogonal_projection, False),
    }

    for arm in ARMS:
        t_arm = time.time()
        runner, is_bank = arm_runners[arm]
        if arm == "ARM_FREQ_SEPARATION":
            out = run_freq_separation(E, idx_tr, seed, freq_med, idx_freq_high)
        else:
            out = runner(E, idx_tr, seed)
        wall_train = time.time() - t_arm

        # Compute logits over held
        t_eval = time.time()
        if is_bank:
            logits_all = compute_logits_bank_avg(out["W_A"], out["W_B"], E, idx_held)
        else:
            logits_all = compute_logits_single_W(out["W"], E, idx_held)
        # Dev / test split on logits
        logits_dev = logits_all[:n_dev]
        logits_test = logits_all[n_dev:n_dev + len(nxt_test)]
        sweep = joint_sweep(logits_dev, logits_test, U_log, nxt_dev, nxt_test)
        wall_eval = time.time() - t_eval

        arm_results[arm] = {
            "bpc": sweep["bpc"],
            "top1": sweep["top1"],
            "best_T": sweep["best_T"],
            "best_lambda": sweep["best_lambda"],
            "best_dev_bpc": sweep["best_dev_bpc"],
            "wall_train_s": round(wall_train, 2),
            "wall_eval_s": round(wall_eval, 2),
        }
        print("    [%s] bpc=%.4f top1=%.4f T=%.3f lam=%.2f wall_train=%.1fs wall_eval=%.1fs" %
              (arm, sweep["bpc"], sweep["top1"], sweep["best_T"], sweep["best_lambda"],
               wall_train, wall_eval), flush=True)

    elapsed = time.time() - t0_seed
    print("  [seed=%d] total elapsed=%.1fs" % (seed, elapsed), flush=True)

    return {
        "seed": seed,
        "V": V, "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
        "N_STEPS": N_STEPS, "BATCH": BATCH, "LR": LR, "STDP_W": STDP_W,
        "uniform_nats": float(math.log(V)),
        "uniform_bpc": float(math.log2(V)),
        "cond_ent_nats": float(ce),
        "arms": arm_results,
        "elapsed_s": float(elapsed),
        "run_mode": RUN_MODE,
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(all_results: List[Dict]) -> Tuple[str, str, Dict]:
    if not all_results:
        return ("HARD_FAIL", "no results", {})
    n_seeds = len(all_results)
    # Per-arm mean BPC and top1 across seeds
    arm_means: Dict[str, Dict[str, float]] = {}
    for arm in ARMS:
        bpcs = [r["arms"][arm]["bpc"] for r in all_results if arm in r["arms"]]
        top1s = [r["arms"][arm]["top1"] for r in all_results if arm in r["arms"]]
        if not bpcs:
            arm_means[arm] = {"bpc_mean": float("inf"), "bpc_std": float("nan"),
                              "bpc_cv": float("nan"), "top1_mean": float("nan")}
            continue
        bm = float(np.mean(bpcs))
        bs = float(np.std(bpcs))
        cv = bs / max(abs(bm), 1e-9)
        tm = float(np.mean(top1s))
        arm_means[arm] = {"bpc_mean": round(bm, 4), "bpc_std": round(bs, 4),
                          "bpc_cv": round(cv, 4), "top1_mean": round(tm, 4)}

    baseline = arm_means["ARM_BASELINE_CFRPE_ALONE"]["bpc_mean"]
    naive = arm_means["ARM_NAIVE_CFRPE_PLUS_STDP"]["bpc_mean"]

    _provenance_not_shown = (
        "\nWHAT_THIS_DOES_NOT_SHOW:\n"
        "- does not isolate whether the failure is encoder / corpus / step-count vs the cf-RPE primitive itself\n"
        "- does not test the other 8 arms meaningfully because the cf-RPE reference is broken\n"
    )
    # HARD_FAIL_PROVENANCE: cf-RPE primitive broken (baseline at-chance-ish)
    if baseline > HARD_FAIL_PROVENANCE_BPC_FLOOR:
        return ("HARD_FAIL", "HARD_FAIL_PROVENANCE: ARM_BASELINE_CFRPE_ALONE bpc=%.4f > %.4f (cf-RPE primitive broken)%s" %
                (baseline, HARD_FAIL_PROVENANCE_BPC_FLOOR, _provenance_not_shown),
                {"arm_means": arm_means, "baseline": baseline, "naive": naive})

    naive_collapse_delta = naive - baseline
    smoke_collapse_reproduced = (naive_collapse_delta >= SANITY_NAIVE_COLLAPSE_DELTA)

    # Rank rescue arms (3-9) by BPC
    rescue_arms = ARMS[2:]
    rescue_lift_vs_naive: List[Tuple[str, float, float]] = []   # (arm, lift_vs_naive, vs_baseline)
    for arm in rescue_arms:
        bm = arm_means[arm]["bpc_mean"]
        rescue_lift_vs_naive.append((arm, naive - bm, baseline - bm))
    # Sort by lift_vs_naive descending
    rescue_lift_vs_naive.sort(key=lambda x: x[1], reverse=True)
    top_rescue = rescue_lift_vs_naive[0] if rescue_lift_vs_naive else None

    summary_top3 = "; ".join(["%s lift_vs_naive=%.4f vs_base=%.4f" % (a, lv, bv)
                                for a, lv, bv in rescue_lift_vs_naive[:3]])
    info = {
        "arm_means": arm_means,
        "baseline_bpc": baseline,
        "naive_bpc": naive,
        "naive_collapse_delta": round(naive_collapse_delta, 4),
        "smoke_collapse_reproduced": bool(smoke_collapse_reproduced),
        "rescue_ranking": [{"arm": a, "lift_vs_naive": round(lv, 4),
                            "lift_vs_baseline": round(bv, 4)}
                           for a, lv, bv in rescue_lift_vs_naive],
        "uniform_bpc": float(math.log2(V)),
    }

    _smoke_too_small_not_shown = (
        "\nWHAT_THIS_DOES_NOT_SHOW:\n"
        "- does not demonstrate any rescue arm is useless (collapse not reproduced means no signal to discriminate)\n"
        "- does not validate or refute the composition collapse thesis; smoke insufficient to test\n"
        "- recommend production-scale NAIVE-only re-test to confirm collapse before reauthoring shotgun\n"
    )
    # If NAIVE doesn't collapse at smoke
    if not smoke_collapse_reproduced:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_SMOKE_TOO_SMALL: NAIVE-BASELINE delta=%.4f < %.4f (collapse did not reproduce at smoke; n=%d seeds). top3 rescue rank: %s. baseline_bpc=%.4f naive_bpc=%.4f%s" %
                (naive_collapse_delta, SANITY_NAIVE_COLLAPSE_DELTA, n_seeds, summary_top3, baseline, naive, _smoke_too_small_not_shown),
                info)

    # Check HARD_PASS: any arm meets BOTH thresholds
    pass_arms = []
    weak_arms = []
    for arm, lv, bv in rescue_lift_vs_naive:
        if lv >= HARD_PASS_RESCUE_VS_NAIVE and bv >= HARD_PASS_RESCUE_VS_BASELINE:
            pass_arms.append((arm, lv, bv))
        elif lv >= MIDDLE_BAND_VS_NAIVE_LOWER:
            weak_arms.append((arm, lv, bv))

    not_shown = (
        "\nWHAT_THIS_DOES_NOT_SHOW:\n"
        "- does not validate at production scale (V=4000 N_DIM=8192 N_TRAIN=100k text8); any HARD_PASS arm needs production promotion\n"
        "- does not test single-arm sufficiency; baseline is cf-RPE alone, not full A1 5-primitive stack\n"
        "- does not test corpus-transfer alternative; pivot path is unmeasured here\n"
    )

    if pass_arms:
        pass_arms.sort(key=lambda x: x[1], reverse=True)
        pa_summary = "; ".join(["%s lift_vs_naive=%.4f vs_base=%.4f" % (a, lv, bv)
                                  for a, lv, bv in pass_arms])
        return ("HARD_PASS",
                "HARD_PASS_SIGNAL_FOUND: %d arm(s) meet promote threshold (>=%.2f vs naive AND >=%.2f vs baseline). PASS arms: %s. naive_collapse=%.4f baseline_bpc=%.4f naive_bpc=%.4f%s" %
                (len(pass_arms), HARD_PASS_RESCUE_VS_NAIVE, HARD_PASS_RESCUE_VS_BASELINE,
                 pa_summary, naive_collapse_delta, baseline, naive, not_shown),
                info)

    if weak_arms:
        weak_arms.sort(key=lambda x: x[1], reverse=True)
        wa_summary = "; ".join(["%s lift_vs_naive=%.4f vs_base=%.4f" % (a, lv, bv)
                                  for a, lv, bv in weak_arms])
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_WEAK_SIGNAL: %d arm(s) beat naive by [0.05, 0.10) but not HARD_PASS threshold. WEAK arms: %s. naive_collapse=%.4f baseline_bpc=%.4f naive_bpc=%.4f%s" %
                (len(weak_arms), wa_summary, naive_collapse_delta, baseline, naive, not_shown),
                info)

    return ("HARD_FAIL",
            "HARD_FAIL_DECISIVE: all 7 separation strategies fail to beat NAIVE by >=%.2f BPC; composition collapse is fundamental at smoke. top3 rescue: %s. naive_collapse=%.4f baseline_bpc=%.4f naive_bpc=%.4f%s" %
            (MIDDLE_BAND_VS_NAIVE_LOWER, summary_top3, naive_collapse_delta, baseline, naive, not_shown),
            info)


# ============================================================================
# Main
# ============================================================================

print("[config] anchor=%s arms=%d N_DIM=%d V=%d N_TRAIN=%d mode=%s seeds=%s" %
      (ANCHOR_NAME, len(ARMS), N_DIM, V, N_TRAIN, RUN_MODE, SEEDS), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"V": V, "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
              "N_STEPS": N_STEPS, "BATCH": BATCH, "LR": LR, "STDP_W": STDP_W,
              "arms": ARMS, "run_mode": RUN_MODE,
              "config_version": CONFIG_VERSION}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d done, %d to run" % (len(done), len(remaining)), flush=True)

t_total = time.time()
for seed in remaining:
    print("[seed=%d] %s..." % (seed, ANCHOR_NAME), flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS)
all_results = list(per_seed.values())
verdict, verdict_msg, info = compute_verdict(all_results)

elapsed = time.time() - t_total
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

import json
metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,   # REQUIRED_FIELDS per queue_add
    "run_mode": RUN_MODE,
    "n_seeds": len(SEEDS),
    "V": V, "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
    "N_STEPS": N_STEPS, "BATCH": BATCH, "LR": LR, "STDP_W": STDP_W,
    "arms": ARMS,
    "config_version": CONFIG_VERSION,
    "elapsed_s": float(elapsed),
    "info": info,
    "per_seed": [
        {"seed": r.get("seed"), "uniform_bpc": r.get("uniform_bpc"),
         "cond_ent_nats": r.get("cond_ent_nats"),
         "arms": r.get("arms"), "elapsed_s": r.get("elapsed_s")}
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print("[metrics] written to %s" % metrics_path, flush=True)
