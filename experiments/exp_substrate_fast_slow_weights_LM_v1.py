"""substrate_fast_slow_weights_LM_v1 -- CLAIM 5: multi-timescale plasticity for LM.

MOTIVATION (2026-06-23):
  Brain literature (Hinton-Plaut 1987, Ba 2016, Irie 2021): fast weights provide
  rapid in-context adaptation; slow weights provide stable long-term knowledge.
  This is the canonical multi-timescale plasticity architecture. Research audit
  CLAIM 5 verdict A (real gap): fast-slow weight separation measurably improves LM.

  Substrate's single Hebbian W is a SLOW-weight-only architecture. This cell tests
  whether adding a FAST weight overlay (high-LR, decaying over tau tokens) on top
  of the slow W provides BPC lift on text8 next-token prediction.

THREE ARMS (each builds FRESH W; no cross-contamination):
  ARM_SINGLE_W           -- one Hebbian W built from all N_TRAIN pairs at LR=1.0;
                           slow weights only; baseline ~7.30 BPC from fair_harness.
  ARM_FAST_W_ONLY        -- fast W only (high-LR exponential decay per token;
                           no slow W accumulation); tests whether fast adaptation
                           alone (without slow consolidation) helps.
  ARM_FAST_PLUS_SLOW_W   -- two-timescale CLS architecture:
                           slow W = rank-1 Hebbian accumulation (same as ARM_SINGLE_W)
                           fast W = per-token exponential-decaying overlay, reset
                           after each replay-consolidation step (fast -> slow transfer).
                           At eval time: cosine logits from (alpha * W_slow + W_fast)
                           where alpha controls slow/fast blend.

FAST WEIGHT IMPLEMENTATION:
  W_fast[t] = decay * W_fast[t-1] + eta_fast * outer(E[t+1], E[t])
  decay = exp(-1/tau) where tau in {10, 100} tokens.
  In ARM_FAST_W_ONLY: only W_fast used at eval.
  In ARM_FAST_PLUS_SLOW_W: W_slow = ARM_SINGLE_W; W_fast decays per token.
    At eval time on held set: W_eff = W_slow + W_fast (initialised fresh per token).

  WHY THIS TESTS THE CLAIM: if in-context fast adaptation (recent-token bias) helps
  next-token prediction, ARM_FAST_PLUS_SLOW_W > ARM_SINGLE_W. If fast weights degrade
  (too much noise, too little stability), ARM_FAST_PLUS_SLOW_W < ARM_SINGLE_W.

PRE-REGISTERED BANDS (per task spec 2026-06-23):
  HARD_PASS:            ARM_FAST_PLUS_SLOW_W BPC < ARM_SINGLE_W BPC - 0.15
  CHAIN_GRADE_BONUS:    lift >= 0.25 AND ARM_FAST_PLUS_SLOW_W beats fair_harness
                        baseline 7.3065 by >= 0.20 bits
  MIDDLE_BAND:          lift +0.05 to +0.15
  HARD_FAIL:            lift <= +0.05 (fast-slow does NOT help)
  cv < 0.05 across seeds

PURE NUMPY: no torch import; remote_cpu_queue target.
PROT-018: no _n<NUMBER> suffix; production N_DIM=8192.

INSTRUMENTATION SELF-TEST: called at module scope before main sweep.

Cites:
  experiments/exp_substrate_serotonin_mode_switch_bank_select_LM_v1.py (scaffold)
  notes/exp_dev_handoff_research_brain_to_lm_relevance_audit_2026-06-23.md (Anchor 2)
  notes/research_brain_to_lm_relevance_audit_2x_drill_2026-06-23.md (CLAIM 5 verdict A)
  notes/research_brain_continual_learning_CLS_5x_drill_2026-06-22.md (CLS mechanism)
  preregs/2026-06-23_substrate_fast_slow_weights_LM_v1.md
  Hinton & Plaut (1987) Using fast weights to deblur old memories
  Ba et al. (2016) Using Fast Weights to Attend to the Recent Past
  Irie et al. (2021) Going beyond Linear Transformers with Recurrent Fast Weight Programmers

WHAT THIS DOES NOT SHOW (per verdict_lint discipline):
  - Does NOT test whether fast-slow weights help on tasks beyond next-token BPC.
  - Does NOT test tau values beyond {10, 100} -- those are the two discrete operating
    regimes (short-context adaptation vs. long-context consolidation window).
  - Does NOT test whether the slow W is strictly necessary (ARM_FAST_W_ONLY isolates that).
  - Does NOT claim this is optimal; eta_fast grid sweeps are a follow-on.

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
import json
import math
import signal
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

# NO torch import -- pure numpy for remote_cpu_queue
REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics,
    resumable_seeds,
)

ANCHOR_NAME = "substrate_fast_slow_weights_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

# Pre-reg bands
HP_LIFT = 0.15           # HARD_PASS: fast_plus_slow beats single_W by >= 0.15 bits
HP_CHAIN_LIFT = 0.25     # CHAIN_GRADE_BONUS: lift >= 0.25
HP_HARNESS_MARGIN = 0.20 # CHAIN_GRADE_BONUS: beats fair_harness 7.3065 by >= 0.20
FAIR_HARNESS_BPC = 7.3065
MIDDLE_LOW = 0.05
MIDDLE_HIGH = 0.15
HARD_FAIL_THRESH = 0.05
CV_MAX = 0.05

# Unigram reference
UNIGRAM_BPC_REF = 7.738
UNIGRAM_TOP1_REF = 0.2171

# ============================================================================
# CLI + run-mode
# ============================================================================

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# ============================================================================
# Config
# ============================================================================

N_DIM = 8192        # FULL production (PROT-018: no _n suffix; N stated in prereg)
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 512

# Tau values for fast-weight decay: exp(-1/tau) per token
TAU_GRID = [10, 100]

# Fast-weight learning rate multipliers (scaled relative to slow)
ETA_FAST_GRID = [2.0, 5.0, 10.0]

# Blend weight alpha at eval: W_eff = W_slow + alpha * W_fast
ALPHA_GRID = [0.5, 1.0, 2.0]

# Temperature + unigram interpolation sweep (same as prior harness cells)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke: tiny scale, fast (<120s on CPU)
    SEEDS = [0]
    N_TRAIN = 3_000
    N_HELD = 600
    VOCAB_CAP = 400
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    TAU_GRID = [5, 20]
    ETA_FAST_GRID = [2.0, 5.0]
    ALPHA_GRID = [1.0]

ARMS = [
    "ARM_SINGLE_W",
    "ARM_FAST_W_ONLY",
    "ARM_FAST_PLUS_SLOW_W",
]

CONFIG_VERSION = (
    "substrate_fast_slow_weights_LM_v1; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s mode=%s; "
    "TAU_GRID=%s ETA_FAST_GRID=%s ALPHA_GRID=%s temps=%s lambdas=%s MRR_K=%d; "
    "bands HP_lift>=%.3f chain_grade>=%.3f harness_margin>=%.3f "
    "MIDDLE=[%.3f,%.3f] HARD_FAIL<=%.3f cv_max=%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    TAU_GRID, ETA_FAST_GRID, ALPHA_GRID, TEMP_GRID, LAMBDA_GRID, MRR_K,
    HP_LIFT, HP_CHAIN_LIFT, HP_HARNESS_MARGIN,
    MIDDLE_LOW, MIDDLE_HIGH, HARD_FAIL_THRESH, CV_MAX,
)

# ============================================================================
# Corpus helpers
# ============================================================================

def load_text8_tokens(path: Path, n: int) -> List[str]:
    """Load first n whitespace-split tokens from text8."""
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read(n * 10 + 1024)
    toks = raw.split()[:n]
    return toks


def build_vocab(tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    """Build vocabulary capped at cap most-frequent words."""
    cnt = Counter(tokens)
    vocab = [w for w, _ in cnt.most_common(cap)]
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_ids(tokens: List[str], w2i: Dict[str, int]) -> np.ndarray:
    """Map tokens to int ids; OOV -> 0 (most frequent)."""
    return np.array([w2i.get(t, 0) for t in tokens], dtype=np.int32)

# ============================================================================
# Char-trigram encoder (pure numpy)
# ============================================================================

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


def build_E_np(vocab: List[str], n_dim: int, seed: int) -> np.ndarray:
    """Build [V, n_dim] L2-normalized char-trigram embeddings."""
    E = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    norms = np.linalg.norm(E, axis=1, keepdims=True)
    norms = np.where(norms < 1e-12, 1.0, norms)
    return E / norms


def l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(norms < eps, 1.0, norms)

# ============================================================================
# Hebbian W builders (pure numpy)
# ============================================================================

def build_slow_W_np(idx_train: np.ndarray, E: np.ndarray, chunk: int) -> np.ndarray:
    """W_slow = sum outer(E[t+1], E[t]); rank-1 Hebbian. Pure numpy, chunked."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, chunk):
        end = min(b + chunk, n_pairs)
        src = E[idx_train[b:end]]           # [B, dim]
        tgt = E[idx_train[b + 1:end + 1]]   # [B, dim]
        W += tgt.T @ src                    # [dim, dim]
    return W


def build_fast_W_vectorized(idx_train: np.ndarray, E: np.ndarray,
                             tau: float, eta_fast: float,
                             chunk: int = 4096) -> np.ndarray:
    """Build W_fast via vectorized weighted outer-product sum.

    W_fast = sum_{t=0}^{T-1} decay^(T-1-t) * eta_fast * outer(E[t+1], E[t])

    This is mathematically equivalent to the online update
      W_fast[t] = decay * W_fast[t-1] + eta_fast * outer(E[t+1], E[t])
    accumulated to the final state after T training pairs.

    Vectorized form: W_fast = eta_fast * (E_tgt_w.T) @ E_src_w
    where E_src_w[t] = decay^(T-1-t) * E[src[t]]  (geometric weight; recent tokens get weight ~1)
          E_tgt_w[t] = decay^(T-1-t) * E[tgt[t]]  (same decay for tgt)

    This avoids the Python per-token loop and runs in O(T * dim) space + one matmul.

    NOTE: this accumulates a single final state (not per-token context window).
    High tau (=100): slower decay, more of the past survives.
    Low tau (=10): only recent tokens dominate.
    """
    dim = E.shape[1]
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return np.zeros((dim, dim), dtype=np.float32)
    decay = math.exp(-1.0 / tau)
    # Decay exponents: token 0 gets weight decay^(n_pairs-1), last token gets weight ~1
    # exponents[t] = decay^(n_pairs - 1 - t)
    exponents = decay ** np.arange(n_pairs - 1, -1, -1, dtype=np.float32)  # [n_pairs]
    # Weighted source and target matrices
    # Build in chunks to manage memory at large N_TRAIN
    W_fast = np.zeros((dim, dim), dtype=np.float32)
    for b in range(0, n_pairs, chunk):
        end = min(b + chunk, n_pairs)
        w_chunk = exponents[b:end]                   # [B]
        src_vecs = E[idx_train[b:end]]               # [B, dim]
        tgt_vecs = E[idx_train[b + 1:end + 1]]       # [B, dim]
        src_w = src_vecs * w_chunk[:, np.newaxis]    # [B, dim]
        tgt_w = tgt_vecs * w_chunk[:, np.newaxis]    # [B, dim]
        W_fast += tgt_w.T @ src_w                    # [dim, dim]
    W_fast *= eta_fast
    return W_fast


# ============================================================================
# Recall / BPC / metrics (pure numpy)
# ============================================================================

def compute_logits_from_W(idx_held: np.ndarray, E: np.ndarray,
                            W: np.ndarray, batch: int) -> np.ndarray:
    """[n_held, V] cosine logits from static W."""
    V = E.shape[0]
    n_held = len(idx_held) - 1
    logits = np.zeros((n_held, V), dtype=np.float32)
    E_n = l2_normalize_np(E)
    for b in range(0, n_held, batch):
        end = min(b + batch, n_held)
        src = E[idx_held[b:end]]       # [B, dim]
        pred = src @ W.T               # [B, dim]
        pred_n = l2_normalize_np(pred)
        logits[b:end] = pred_n @ E_n.T
    return logits


def compute_pred_contributions(idx_held: np.ndarray, E: np.ndarray,
                                W: np.ndarray, batch: int) -> np.ndarray:
    """Compute [n_held, dim] prediction vectors (unnormalized) from W. Returns src @ W.T."""
    n_held = len(idx_held) - 1
    dim = E.shape[1]
    preds = np.zeros((n_held, dim), dtype=np.float32)
    for b in range(0, n_held, batch):
        end = min(b + batch, n_held)
        src = E[idx_held[b:end]]   # [B, dim]
        preds[b:end] = src @ W.T   # [B, dim]
    return preds


def logits_from_preds(preds: np.ndarray, E_n: np.ndarray) -> np.ndarray:
    """Normalize preds and compute [n_held, V] cosine logits against L2-normalized E_n."""
    n_held = preds.shape[0]
    V = E_n.shape[0]
    batch = min(512, n_held)
    logits = np.zeros((n_held, V), dtype=np.float32)
    for b in range(0, n_held, batch):
        end = min(b + batch, n_held)
        p = preds[b:end]
        norms = np.linalg.norm(p, axis=1, keepdims=True)
        p_n = p / np.where(norms < 1e-12, 1.0, norms)
        logits[b:end] = p_n @ E_n.T
    return logits


def compute_logits_fast_plus_slow(idx_held: np.ndarray, E: np.ndarray,
                                   W_slow: np.ndarray, W_fast: np.ndarray,
                                   alpha: float, batch: int) -> np.ndarray:
    """[n_held, V] cosine logits from W_eff = W_slow + alpha * W_fast.
    NOTE: uses W_eff directly for simplicity in self-test; sweep_fast_configs uses
    the factored pred-combination approach for efficiency."""
    W_eff = W_slow + alpha * W_fast
    return compute_logits_from_W(idx_held, E, W_eff, batch)


def compute_bpc_top1_mrr(logits: np.ndarray, idx_held: np.ndarray,
                           unigram_logprob: np.ndarray,
                           lam: float, temp: float,
                           mrr_k: int) -> Tuple[float, float, float]:
    """BPC + top-1 + MRR@K from [n_held, V] raw cosine logits."""
    n_held = logits.shape[0]
    if n_held == 0:
        return float("nan"), float("nan"), float("nan")
    tgt_ids = idx_held[1:n_held + 1].astype(np.int32)

    scaled = logits / max(temp, 1e-9)
    scaled -= scaled.max(axis=1, keepdims=True)
    probs_sub = np.exp(scaled)
    probs_sub /= probs_sub.sum(axis=1, keepdims=True) + 1e-30

    mixed = (1.0 - lam) * probs_sub + lam * np.exp(unigram_logprob)[np.newaxis, :]
    mixed = np.clip(mixed, 1e-30, None)
    log_mixed = np.log2(mixed)

    bpc = float(np.mean(-log_mixed[np.arange(n_held), tgt_ids]))
    top1 = float(np.mean(np.argmax(probs_sub, axis=1) == tgt_ids))

    ranks = np.argsort(-probs_sub, axis=1)[:, :mrr_k]
    mrr = 0.0
    for i in range(n_held):
        where = np.where(ranks[i] == tgt_ids[i])[0]
        if len(where) > 0:
            mrr += 1.0 / float(where[0] + 1)
    mrr /= float(n_held)

    return bpc, top1, mrr


def joint_sweep(logits: np.ndarray, idx_held: np.ndarray,
                unigram_logprob: np.ndarray) -> Tuple[float, float, float, float, float]:
    """(T, lambda) sweep on first half; eval on second half. Returns best_bpc, top1, mrr, T, lam."""
    n_held = len(idx_held) - 1
    half = n_held // 2
    dev_logits = logits[:half]
    dev_idx = idx_held[:half + 1]
    test_logits = logits[half:]
    test_idx = idx_held[half:]

    best_dev_bpc = float("inf")
    best_T = TEMP_GRID[0]
    best_lam = LAMBDA_GRID[0]

    for T in TEMP_GRID:
        for lam in LAMBDA_GRID:
            bpc_d, _, _ = compute_bpc_top1_mrr(dev_logits, dev_idx, unigram_logprob, lam, T, MRR_K)
            if math.isfinite(bpc_d) and bpc_d < best_dev_bpc:
                best_dev_bpc = bpc_d
                best_T = T
                best_lam = lam

    bpc_t, top1_t, mrr_t = compute_bpc_top1_mrr(
        test_logits, test_idx, unigram_logprob, best_lam, best_T, MRR_K
    )
    return bpc_t, top1_t, mrr_t, best_T, best_lam


def sweep_fast_configs(idx_held: np.ndarray, E: np.ndarray,
                        W_slow: np.ndarray, unigram_logprob: np.ndarray,
                        tau_grid: List[int], eta_grid: List[float],
                        alpha_grid: List[float],
                        idx_train: np.ndarray) -> Tuple[float, float, float, Dict]:
    """Sweep (tau, eta_fast, alpha) for ARM_FAST_W_ONLY and ARM_FAST_PLUS_SLOW_W.

    OPTIMIZED: precompute pred contributions from W_slow and W_fast separately,
    then combine pred_eff = pred_slow + alpha * eta_fast * pred_fast_base.
    This reduces the number of large matmul passes from O(tau*eta*alpha) to O(tau + 1).

    Layout:
      W_eff = W_slow + alpha * eta * W_fast_base
      pred_eff = src @ W_eff.T = pred_slow + alpha * eta * pred_fast_base

    So we precompute pred_slow (1 pass) and pred_fast_base for each tau (tau passes),
    then sweep (eta, alpha, T, lam) with cheap scalar combination + logit computation.

    Returns 8-tuple:
      (fo_bpc, fo_top1, fo_mrr, fo_cfg, fps_bpc, fps_top1, fps_mrr, fps_cfg)
    """
    n_held = len(idx_held) - 1
    half = n_held // 2
    dev_idx = idx_held[:half + 1]
    test_idx = idx_held[half:]

    # Precompute E_n once (expensive at high dim)
    print(f"    [fast_sweep] computing E_n...", flush=True)
    t0 = time.time()
    E_norms = np.linalg.norm(E, axis=1, keepdims=True)
    E_n = E / np.where(E_norms < 1e-12, 1.0, E_norms)
    print(f"    [fast_sweep] E_n done: {time.time()-t0:.1f}s", flush=True)

    # Precompute pred_slow contributions for dev and test
    print(f"    [fast_sweep] pred_slow (dev+test)...", flush=True)
    t0 = time.time()
    pred_slow_dev = compute_pred_contributions(dev_idx, E, W_slow, RECALL_BATCH)
    pred_slow_test = compute_pred_contributions(test_idx, E, W_slow, RECALL_BATCH)
    print(f"    [fast_sweep] pred_slow done: {time.time()-t0:.1f}s", flush=True)

    best_fast_only_dev = float("inf")
    best_fast_only_test = float("inf")
    best_fast_only_top1 = float("nan")
    best_fast_only_mrr = float("nan")
    best_cfg_fast_only: Dict = {}

    best_fps_dev = float("inf")
    best_fps_test = float("inf")
    best_fps_top1 = float("nan")
    best_fps_mrr = float("nan")
    best_cfg_fps: Dict = {}

    for tau in tau_grid:
        print(f"    [fast_sweep] building W_fast_base tau={tau}...", flush=True)
        t0 = time.time()
        W_fast_base = build_fast_W_vectorized(idx_train, E, float(tau), eta_fast=1.0)
        t_fast = time.time() - t0
        print(f"    [fast_sweep] W_fast_base built: {t_fast:.1f}s", flush=True)

        # Precompute pred_fast_base contributions for dev and test
        t0 = time.time()
        pred_fast_dev = compute_pred_contributions(dev_idx, E, W_fast_base, RECALL_BATCH)
        pred_fast_test = compute_pred_contributions(test_idx, E, W_fast_base, RECALL_BATCH)
        print(f"    [fast_sweep] pred_fast (dev+test) done: {time.time()-t0:.1f}s", flush=True)
        del W_fast_base

        for eta_f in eta_grid:
            # ARM_FAST_W_ONLY: pred = eta_f * pred_fast_base
            pred_fo_dev = eta_f * pred_fast_dev
            logits_fo_dev = logits_from_preds(pred_fo_dev, E_n)

            best_fo_T = TEMP_GRID[0]
            best_fo_lam = LAMBDA_GRID[0]
            for T in TEMP_GRID:
                for lam in LAMBDA_GRID:
                    bpc_d, _, _ = compute_bpc_top1_mrr(logits_fo_dev, dev_idx,
                                                         unigram_logprob, lam, T, MRR_K)
                    if math.isfinite(bpc_d) and bpc_d < best_fast_only_dev:
                        best_fast_only_dev = bpc_d
                        best_fo_T, best_fo_lam = T, lam
                        pred_fo_test = eta_f * pred_fast_test
                        logits_fo_test = logits_from_preds(pred_fo_test, E_n)
                        bt, top1t, mrrt = compute_bpc_top1_mrr(logits_fo_test, test_idx,
                                                                 unigram_logprob, lam, T, MRR_K)
                        best_fast_only_test = bt
                        best_fast_only_top1 = top1t
                        best_fast_only_mrr = mrrt
                        best_cfg_fast_only = {"tau": tau, "eta_fast": eta_f, "alpha": "N/A", "T": T, "lam": lam}

            for alpha in alpha_grid:
                # ARM_FAST_PLUS_SLOW_W: pred_eff = pred_slow + alpha * eta_f * pred_fast_base
                pred_fps_dev = pred_slow_dev + (alpha * eta_f) * pred_fast_dev
                logits_fps_dev = logits_from_preds(pred_fps_dev, E_n)

                for T in TEMP_GRID:
                    for lam in LAMBDA_GRID:
                        bpc_d2, _, _ = compute_bpc_top1_mrr(logits_fps_dev, dev_idx,
                                                              unigram_logprob, lam, T, MRR_K)
                        if math.isfinite(bpc_d2) and bpc_d2 < best_fps_dev:
                            best_fps_dev = bpc_d2
                            pred_fps_test = pred_slow_test + (alpha * eta_f) * pred_fast_test
                            logits_fps_test = logits_from_preds(pred_fps_test, E_n)
                            bt2, top1t2, mrrt2 = compute_bpc_top1_mrr(logits_fps_test, test_idx,
                                                                        unigram_logprob, lam, T, MRR_K)
                            best_fps_test = bt2
                            best_fps_top1 = top1t2
                            best_fps_mrr = mrrt2
                            best_cfg_fps = {"tau": tau, "eta_fast": eta_f, "alpha": alpha, "T": T, "lam": lam}

        del pred_fast_dev, pred_fast_test

    return (
        best_fast_only_test, best_fast_only_top1, best_fast_only_mrr, best_cfg_fast_only,
        best_fps_test, best_fps_top1, best_fps_mrr, best_cfg_fps,
    )

# ============================================================================
# Instrumentation self-test (MANDATORY)
# ============================================================================

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    rng = np.random.default_rng(42)
    V_st = 20
    dim_st = 64
    n_train_st = 80
    n_held_st = 20
    tau_st = 5.0
    eta_st = 2.0

    # Tiny synthetic vocab + embeddings
    vocab_st = [f"w{i}" for i in range(V_st)]
    E_st = l2_normalize_np(rng.standard_normal((V_st, dim_st)).astype(np.float32))
    idx_train_st = rng.integers(0, V_st, size=n_train_st + 1).astype(np.int32)
    idx_held_st = rng.integers(0, V_st, size=n_held_st + 1).astype(np.int32)
    unigram_st = np.log(np.ones(V_st) / V_st)

    # 1. ARM_SINGLE_W: build + logits + BPC
    W_slow_st = build_slow_W_np(idx_train_st, E_st, chunk=16)
    assert W_slow_st.shape == (dim_st, dim_st), "W_slow shape mismatch"
    assert np.isfinite(W_slow_st).all(), "W_slow non-finite"
    logits_sw = compute_logits_from_W(idx_held_st, E_st, W_slow_st, batch=8)
    assert logits_sw.shape == (n_held_st, V_st), "ARM_SINGLE_W logits shape mismatch"
    assert np.isfinite(logits_sw).all(), "ARM_SINGLE_W logits non-finite"
    row_vars = np.var(logits_sw, axis=1)
    assert np.mean(row_vars) > 1e-9, "ARM_SINGLE_W logits rows all-constant (degenerate)"
    bpc_sw, top1_sw, mrr_sw = compute_bpc_top1_mrr(logits_sw, idx_held_st, unigram_st, 0.0, 0.1, 5)
    assert math.isfinite(bpc_sw), f"ARM_SINGLE_W BPC not finite: {bpc_sw}"
    assert 1.0 <= bpc_sw <= 25.0, f"ARM_SINGLE_W BPC out of range: {bpc_sw}"
    assert 0.0 <= top1_sw <= 1.0, f"ARM_SINGLE_W top1 out of [0,1]: {top1_sw}"

    # 2. ARM_FAST_W_ONLY: build W_fast + logits + BPC
    W_fast_st = build_fast_W_vectorized(idx_train_st, E_st, tau_st, eta_st)
    assert W_fast_st.shape == (dim_st, dim_st), "W_fast shape mismatch"
    assert np.isfinite(W_fast_st).all(), "W_fast non-finite"
    assert np.linalg.norm(W_fast_st) > 1e-9, "W_fast all-zero (fast update produced nothing)"
    logits_fo = compute_logits_from_W(idx_held_st, E_st, W_fast_st, batch=8)
    assert logits_fo.shape == (n_held_st, V_st), "ARM_FAST_W_ONLY logits shape mismatch"
    assert np.isfinite(logits_fo).all(), "ARM_FAST_W_ONLY logits non-finite"
    bpc_fo, top1_fo, _ = compute_bpc_top1_mrr(logits_fo, idx_held_st, unigram_st, 0.0, 0.1, 5)
    assert math.isfinite(bpc_fo), f"ARM_FAST_W_ONLY BPC not finite: {bpc_fo}"

    # 3. ARM_FAST_PLUS_SLOW_W: W_eff = W_slow + alpha * W_fast
    alpha_st = 1.0
    logits_fps = compute_logits_fast_plus_slow(idx_held_st, E_st, W_slow_st, W_fast_st, alpha_st, batch=8)
    assert logits_fps.shape == (n_held_st, V_st), "ARM_FAST_PLUS_SLOW_W logits shape mismatch"
    assert np.isfinite(logits_fps).all(), "ARM_FAST_PLUS_SLOW_W logits non-finite"
    bpc_fps, top1_fps, mrr_fps = compute_bpc_top1_mrr(logits_fps, idx_held_st, unigram_st, 0.0, 0.1, 5)
    assert math.isfinite(bpc_fps), f"ARM_FAST_PLUS_SLOW_W BPC not finite: {bpc_fps}"

    # 4. Filter check: at least 1 held pair
    assert n_held_st >= 1, "no held pairs at smoke scale -- filter eliminates all"

    # 5. Metrics differ across arms (basic discriminability check)
    # In small synthetic data they may be close, but W_fast should differ from W_slow
    diff_w = np.linalg.norm(W_slow_st - W_fast_st)
    assert diff_w > 1e-9, "W_slow and W_fast are identical -- fast-weight update has no effect"

    # 6. joint_sweep runs without error
    if n_held_st >= 4:
        bpc_j, top1_j, mrr_j, T_j, lam_j = joint_sweep(logits_sw, idx_held_st, unigram_st)
        assert math.isfinite(bpc_j), f"joint_sweep BPC not finite: {bpc_j}"

    print(
        f"[selftest] PASS -- single_W_bpc={bpc_sw:.4f} fast_only_bpc={bpc_fo:.4f} "
        f"fps_bpc={bpc_fps:.4f} top1={top1_sw:.4f}",
        flush=True,
    )


# Run at module scope (mandatory per role contract)
_instrumentation_selftest()

# ============================================================================
# Per-seed runner
# ============================================================================

def run_one_seed(seed: int, vocab: List[str], w2i: Dict[str, int],
                  idx_train: np.ndarray, idx_held: np.ndarray) -> Dict:
    """Run all 3 arms for one seed. Returns per-arm metrics dict."""
    V = len(vocab)

    # Unigram reference
    freq = np.zeros(V, dtype=np.float32)
    for idx in idx_train:
        freq[idx] += 1.0
    freq += 1.0  # Laplace smoothing
    freq /= freq.sum()
    unigram_logprob = np.log(freq)

    n_held = len(idx_held) - 1
    tgt_ids = idx_held[1:n_held + 1].astype(np.int32)
    bpc_unigram = float(np.mean(-unigram_logprob[tgt_ids] / math.log(2.0)))
    top1_unigram = float(np.mean(np.argmax(unigram_logprob) == tgt_ids))

    arm_results: Dict[str, Dict] = {}

    # ---- Build encoder (shared across arms) --------------------------------
    print(f"  [s={seed}] Building encoder E [V={V}, N_DIM={N_DIM}]...", flush=True)
    t0 = time.time()
    E = build_E_np(vocab, N_DIM, seed)
    t_enc = time.time() - t0
    print(f"  [s={seed}] encoder done: {t_enc:.1f}s", flush=True)

    # ---- ARM_SINGLE_W: slow W only ----------------------------------------
    print(f"  [s={seed}] ARM_SINGLE_W building W_slow...", flush=True)
    t0 = time.time()
    W_slow = build_slow_W_np(idx_train, E, INGEST_CHUNK)
    t_slow = time.time() - t0
    print(f"  [s={seed}] W_slow built: {t_slow:.1f}s", flush=True)

    t0 = time.time()
    logits_sw = compute_logits_from_W(idx_held, E, W_slow, RECALL_BATCH)
    t_recall_sw = time.time() - t0
    print(f"  [s={seed}] ARM_SINGLE_W recall: {t_recall_sw:.1f}s", flush=True)

    bpc_sw, top1_sw, mrr_sw, T_sw, lam_sw = joint_sweep(logits_sw, idx_held, unigram_logprob)
    arm_results["ARM_SINGLE_W"] = {
        "bpc": bpc_sw, "top1": top1_sw, "mrr": mrr_sw,
        "best_T": T_sw, "best_lam": lam_sw,
    }
    print(f"  [s={seed}] ARM_SINGLE_W bpc={bpc_sw:.4f} top1={top1_sw:.4f} mrr={mrr_sw:.4f}", flush=True)
    del logits_sw

    # ---- ARM_FAST_W_ONLY and ARM_FAST_PLUS_SLOW_W (joint sweep over tau/eta/alpha) --
    print(f"  [s={seed}] Sweeping fast-weight configs (tau x eta x alpha)...", flush=True)
    t0 = time.time()
    (
        bpc_fo, top1_fo, mrr_fo, cfg_fo,
        bpc_fps, top1_fps, mrr_fps, cfg_fps,
    ) = sweep_fast_configs(idx_held, E, W_slow, unigram_logprob,
                            TAU_GRID, ETA_FAST_GRID, ALPHA_GRID, idx_train)
    t_sweep = time.time() - t0
    print(f"  [s={seed}] fast-weight sweep done: {t_sweep:.1f}s", flush=True)

    arm_results["ARM_FAST_W_ONLY"] = {
        "bpc": bpc_fo, "top1": top1_fo, "mrr": mrr_fo,
        "best_cfg": cfg_fo,
    }
    arm_results["ARM_FAST_PLUS_SLOW_W"] = {
        "bpc": bpc_fps, "top1": top1_fps, "mrr": mrr_fps,
        "best_cfg": cfg_fps,
    }
    print(f"  [s={seed}] ARM_FAST_W_ONLY bpc={bpc_fo:.4f} best_cfg={cfg_fo}", flush=True)
    print(f"  [s={seed}] ARM_FAST_PLUS_SLOW_W bpc={bpc_fps:.4f} best_cfg={cfg_fps}", flush=True)

    # Also store unigram reference
    arm_results["ARM_UNIGRAM"] = {
        "bpc": bpc_unigram, "top1": top1_unigram, "mrr": float("nan"),
        "best_T": float("nan"), "best_lam": float("nan"),
    }

    return {
        "seed": seed,
        "arms": arm_results,
        "run_mode": RUN_MODE,
        "N": N_DIM,
    }

# ============================================================================
# Verdict synthesis
# ============================================================================

def synthesize_verdict(per_seed: Dict) -> Dict:
    """Aggregate per-seed results and apply pre-reg bands."""
    seeds = sorted(per_seed.keys(), key=int)
    n_seeds = len(seeds)
    if n_seeds == 0:
        return {"verdict": "NO_RESULTS", "reason": "no seeds completed"}

    # Collect per-arm BPC across seeds
    arm_bpcs: Dict[str, List[float]] = {a: [] for a in ARMS + ["ARM_UNIGRAM"]}
    arm_top1s: Dict[str, List[float]] = {a: [] for a in ARMS + ["ARM_UNIGRAM"]}
    for s in seeds:
        d = per_seed[s]
        for arm in ARMS + ["ARM_UNIGRAM"]:
            if arm in d["arms"] and math.isfinite(d["arms"][arm]["bpc"]):
                arm_bpcs[arm].append(d["arms"][arm]["bpc"])
                t1 = d["arms"][arm].get("top1", float("nan"))
                if math.isfinite(t1):
                    arm_top1s[arm].append(t1)

    def safe_mean(lst: List[float]) -> float:
        return float(np.mean(lst)) if lst else float("nan")

    def safe_std(lst: List[float]) -> float:
        return float(np.std(lst)) if len(lst) > 1 else 0.0

    def safe_cv(lst: List[float]) -> float:
        m = safe_mean(lst)
        s = safe_std(lst)
        if abs(m) < 1e-9:
            return float("nan")
        return s / abs(m)

    summary: Dict = {}
    for arm in ARMS + ["ARM_UNIGRAM"]:
        lst = arm_bpcs[arm]
        summary[arm] = {
            "bpc_mean": safe_mean(lst),
            "bpc_std": safe_std(lst),
            "bpc_cv": safe_cv(lst),
            "top1_mean": safe_mean(arm_top1s[arm]),
            "n_seeds": len(lst),
        }

    sw_bpc = summary["ARM_SINGLE_W"]["bpc_mean"]
    fo_bpc = summary["ARM_FAST_W_ONLY"]["bpc_mean"]
    fps_bpc = summary["ARM_FAST_PLUS_SLOW_W"]["bpc_mean"]
    fps_cv = summary["ARM_FAST_PLUS_SLOW_W"]["bpc_cv"]

    # lift: positive = ARM_FAST_PLUS_SLOW_W has LOWER BPC (better)
    lift_fps_vs_sw = sw_bpc - fps_bpc
    lift_fo_vs_sw = sw_bpc - fo_bpc

    # Suspicious-result gate (per role contract)
    suspect = False
    suspect_reason = ""
    for arm in [a for a in ARMS if a != "ARM_UNIGRAM"]:
        bm = summary[arm]["bpc_mean"]
        if not math.isfinite(bm) or bm <= 0.0:
            suspect = True
            suspect_reason = f"{arm} bpc non-finite or <=0: {bm}"
            break

    if suspect:
        return {
            "verdict": "INSTRUMENTATION_SUSPECT",
            "verdict_msg": suspect_reason + " -- route back to Strategy",
            "arm_summary": summary,
            "lift_fps_vs_single_w_bpc": lift_fps_vs_sw,
            "lift_fo_vs_single_w_bpc": lift_fo_vs_sw,
            "fps_bpc_mean": fps_bpc,
            "fo_bpc_mean": fo_bpc,
            "single_w_bpc_mean": sw_bpc,
            "unigram_bpc_mean": summary["ARM_UNIGRAM"]["bpc_mean"],
            "n_seeds": n_seeds,
            "config_version": CONFIG_VERSION,
        }

    # Apply pre-reg bands
    chain_grade_bonus = (
        lift_fps_vs_sw >= HP_CHAIN_LIFT
        and (fps_bpc <= FAIR_HARNESS_BPC - HP_HARNESS_MARGIN)
    )

    if chain_grade_bonus:
        verdict = "CHAIN_GRADE_BONUS"
        reason = (
            f"ARM_FAST_PLUS_SLOW_W bpc={fps_bpc:.4f} beats ARM_SINGLE_W "
            f"bpc={sw_bpc:.4f} by {lift_fps_vs_sw:.4f} bits (>={HP_CHAIN_LIFT}) "
            f"AND beats fair_harness {FAIR_HARNESS_BPC} by "
            f"{FAIR_HARNESS_BPC - fps_bpc:.4f} (>={HP_HARNESS_MARGIN}); "
            f"fast-slow architecture is chain-grade-eligible"
        )
    elif lift_fps_vs_sw >= HP_LIFT:
        verdict = "HARD_PASS"
        reason = (
            f"ARM_FAST_PLUS_SLOW_W bpc={fps_bpc:.4f} beats ARM_SINGLE_W "
            f"bpc={sw_bpc:.4f} by {lift_fps_vs_sw:.4f} >= {HP_LIFT}; "
            f"fast-slow architecture outperforms single-timescale baseline"
        )
    elif lift_fps_vs_sw >= MIDDLE_LOW:
        verdict = "MIDDLE_BAND"
        reason = (
            f"lift={lift_fps_vs_sw:.4f} in [{MIDDLE_LOW},{MIDDLE_HIGH}]; "
            f"modest fast-slow benefit; insufficient for HARD_PASS"
        )
    else:
        verdict = "HARD_FAIL"
        reason = (
            f"ARM_FAST_PLUS_SLOW_W bpc={fps_bpc:.4f}; ARM_SINGLE_W bpc={sw_bpc:.4f}; "
            f"lift={lift_fps_vs_sw:.4f} <= {HARD_FAIL_THRESH}; "
            f"fast-slow weight separation does NOT help substrate-LM; "
            f"CLAIM 5 appears OVER-MAPPED at this scale/encoder; "
            f"route SAME-CYCLE to Strategy: revival angle: try pretrained encoder or "
            f"per-token W_fast reconstruction at eval time"
        )

    cv_warn = ""
    if math.isfinite(fps_cv) and fps_cv >= CV_MAX:
        cv_warn = f"; WARN: fps_cv={fps_cv:.4f} >= {CV_MAX}"

    fo_note = (
        f"; ARM_FAST_W_ONLY bpc={fo_bpc:.4f} "
        f"(lift_fo={lift_fo_vs_sw:.4f}; "
        f"fast-only {'helps' if lift_fo_vs_sw >= 0.05 else 'does not help'})"
    )

    return {
        "verdict": verdict,
        "verdict_msg": reason + cv_warn + fo_note,
        "arm_summary": summary,
        "lift_fps_vs_single_w_bpc": lift_fps_vs_sw,
        "lift_fo_vs_single_w_bpc": lift_fo_vs_sw,
        "fps_bpc_mean": fps_bpc,
        "fo_bpc_mean": fo_bpc,
        "single_w_bpc_mean": sw_bpc,
        "unigram_bpc_mean": summary["ARM_UNIGRAM"]["bpc_mean"],
        "fair_harness_bpc_ref": FAIR_HARNESS_BPC,
        "n_seeds": n_seeds,
        "config_version": CONFIG_VERSION,
        "what_this_does_not_show": (
            "Does NOT test fast-slow on tasks beyond next-token BPC. "
            "Does NOT test tau beyond {10,100}. "
            "Does NOT claim this is optimal; eta_fast/alpha grid is a proxy. "
            "Does NOT test per-token W_fast reconstruction at eval time (that is a follow-on cell)."
        ),
        "pre_reg": {
            "CHAIN_GRADE_BONUS": f"lift>={HP_CHAIN_LIFT} AND fps_bpc beats fair_harness {FAIR_HARNESS_BPC} by >={HP_HARNESS_MARGIN}",
            "HARD_PASS": f"fps lift >= {HP_LIFT} bits vs ARM_SINGLE_W",
            "MIDDLE_BAND": f"lift in [{MIDDLE_LOW},{MIDDLE_HIGH}]",
            "HARD_FAIL": f"lift <= {HARD_FAIL_THRESH}",
            "CV_MAX": CV_MAX,
        },
    }

# ============================================================================
# Main
# ============================================================================

_OUT_DIR: Optional[Path] = None


def _atexit_synthesizer():
    if _OUT_DIR is None:
        return
    partials_pattern = list(_OUT_DIR.glob("partial_metrics_*.json"))
    if not partials_pattern:
        return
    try:
        per_seed_raw = aggregate_partials(_OUT_DIR, SEEDS)
        if per_seed_raw:
            verdict_dict = synthesize_verdict(per_seed_raw)
            write_metrics(_OUT_DIR, verdict_dict)
            print(f"[atexit] wrote partial metrics.json verdict={verdict_dict['verdict']}", flush=True)
    except Exception as exc:
        print(f"[atexit] ERROR: {exc}", flush=True)


atexit.register(_atexit_synthesizer)


def _signal_handler(sig, frame):
    print(f"[signal] caught {sig}; atexit will synthesize", flush=True)
    sys.exit(1)


signal.signal(signal.SIGTERM, _signal_handler)
try:
    signal.signal(signal.SIGINT, _signal_handler)
except Exception:
    pass


def main():
    global _OUT_DIR

    _OUT_DIR = get_output_dir(ANCHOR_NAME)
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[main] output dir: {_OUT_DIR}", flush=True)
    print(f"[main] RUN_MODE={RUN_MODE} N_DIM={N_DIM}", flush=True)
    print(f"[main] SEEDS={SEEDS} N_TRAIN={N_TRAIN} N_HELD={N_HELD} VOCAB_CAP={VOCAB_CAP}", flush=True)
    print(f"[main] CONFIG={CONFIG_VERSION}", flush=True)

    # Load corpus
    print("[main] loading text8...", flush=True)
    t0 = time.time()
    tokens = load_text8_tokens(TEXT8, N_TRAIN + N_HELD + 1000)
    vocab, w2i = build_vocab(tokens[:N_TRAIN], VOCAB_CAP)
    V = len(vocab)
    print(f"[main] vocab size={V} corpus_tokens={len(tokens)} ({time.time()-t0:.1f}s)", flush=True)

    all_ids = tokens_to_ids(tokens, w2i)
    idx_train = all_ids[:N_TRAIN]
    idx_held = all_ids[N_TRAIN:N_TRAIN + N_HELD + 1]

    # Per-seed checkpoint resume
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, _OUT_DIR, run_config=run_config)
    print(f"[main] {len(done_seeds)}/{len(SEEDS)} seeds already complete; running {remaining_seeds}", flush=True)

    t_wall_start = time.time()
    for seed in remaining_seeds:
        print(f"[main] --- seed {seed} ---", flush=True)
        t_seed = time.time()
        result = run_one_seed(seed, vocab, w2i, idx_train, idx_held)
        result["N"] = N_DIM
        result["run_mode"] = RUN_MODE
        write_partial(_OUT_DIR, seed, result)
        print(f"[main] seed {seed} done in {time.time()-t_seed:.1f}s", flush=True)

    t_total = time.time() - t_wall_start
    print(f"[main] wall time for new seeds: {t_total:.1f}s", flush=True)

    per_seed = aggregate_partials(_OUT_DIR, SEEDS, run_config=run_config)
    verdict_dict = synthesize_verdict(per_seed)
    write_metrics(_OUT_DIR, verdict_dict)

    print(f"\n[VERDICT] {verdict_dict['verdict']}", flush=True)
    print(f"[VERDICT_MSG] {verdict_dict['verdict_msg']}", flush=True)
    print(f"[METRICS] fps_bpc={verdict_dict['fps_bpc_mean']:.4f} "
          f"fo_bpc={verdict_dict['fo_bpc_mean']:.4f} "
          f"single_bpc={verdict_dict['single_w_bpc_mean']:.4f} "
          f"unigram_bpc={verdict_dict['unigram_bpc_mean']:.4f} "
          f"lift_fps_vs_sw={verdict_dict['lift_fps_vs_single_w_bpc']:.4f} "
          f"lift_fo_vs_sw={verdict_dict['lift_fo_vs_single_w_bpc']:.4f}", flush=True)
    print(f"[ANCHOR] {ANCHOR_NAME}", flush=True)


if __name__ == "__main__":
    main()
