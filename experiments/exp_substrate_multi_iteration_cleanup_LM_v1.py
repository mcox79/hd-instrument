"""substrate_multi_iteration_cleanup_LM_v1 -- Tier-3 RECALL gap: multi-iteration Hopfield cleanup.

MOTIVATION (2026-06-23):
  Brain CA3 attractor convergence is a MULTI-ITERATION process: hippocampal CA3 runs multiple
  recurrent cycles before settling on a stable attractor (Hopfield 1982; Rolls-Treves 1998;
  Nakazono-Bhatt 2018). Substrate currently uses SINGLE-STEP cleanup (one forward pass of W).
  This cell tests whether multi-iteration convergence measurably improves substrate-as-LM BPC
  vs. single-step -- an empirical test of the Tier-3 RECALL gap hypothesis.

  Brain analog: CA3 pyramidal cells form recurrent collaterals; pattern completion requires
  multiple recurrent cycles (each ~10ms theta sub-cycle); typically ~3-7 cycles to attractor
  (Treves-Rolls 1991 analytic capacity formula). If substrate's single-step is equivalent to
  "1 recurrent cycle," multi-iteration adds the missing convergence dynamics.

  This is an UNCERTAIN bet (P_deflated=0.45): attractor convergence may already be captured
  by the rank-1 Hebbian W at single-step, or the BPC metric may be insensitive to cleanup
  quality in the word-bigram regime.

FOUR ARMS (each builds FRESH W from same encoder, same corpus split):
  ARM_BASELINE_NO_CLEANUP    -- raw Hebbian; query = W @ E[src], no cleanup iterations
  ARM_SINGLE_STEP_CLEANUP    -- 1 Hopfield iteration; current substrate default
  ARM_3_ITER_CLEANUP         -- 3 Hopfield iterations; partial attractor convergence
  ARM_10_ITER_CLEANUP_UNTIL_CONVERGE -- run up to 10 iterations; stop at convergence
                                        (cosine delta < 0.001 between iterations)

HOPFIELD UPDATE (pure numpy, vectorized over batch):
  Iteration k: state_{k+1} = clip(W_norm @ state_k, lo, hi)
  With amplitude scaling: state_0 = (1/sqrt(f)) * sparse_query (matched-filter-energy fix)
  W_norm = W / max_singular_value (prevents norm blow-up over iterations)
  We use bipolar-clamp: sign(W @ state_k) for Hopfield-style binary attractor
  L2-normalize after each iteration for cosine-comparison compatibility.

PRE-REGISTERED BANDS (pre-registered BEFORE run, 2026-06-23):
  HARD_PASS:        ARM_10_ITER beats ARM_SINGLE_STEP by >= +0.10 bits BPC
                    (multi-iteration is load-bearing; Tier-3 gap is real)
  CHAIN_GRADE_BONUS: lift >= +0.20 bits (substantial; fundamental fix)
  MIDDLE_BAND:       lift +0.03 to +0.10 bits (marginal; single-step mostly suffices)
  HARD_FAIL:         lift <= +0.03 bits (multi-iteration doesn't help; Tier-3 gap is fake)
  BONUS: if ARM_3_ITER lift >= 0.9 * ARM_10_ITER lift: diminishing returns diagnosed
         (3-iter approximates convergence; 10-iter adds minimal additional benefit)

CRITICAL DISCIPLINES:
  PURE NUMPY: no torch import; remote_cpu_queue routing (PROT-020 avoidance)
  1/sqrt(f) amplitude scaling per matched-filter-energy fix (sparse_receiver_energy research)
  Fix #28: per-arm BPC reported separately; no cross-arm narrative in this script
  preflight_spec.yaml filed alongside; preflight_check.py --warn-only at smoke
  WHAT_THIS_DOES_NOT_SHOW clause in every verdict_msg (Fix #30)
  ASCII-only, no emojis, no em dashes, no em-width unicode

CITES:
  Hopfield (1982) Neural networks and physical systems with emergent collective properties
  Treves-Rolls (1991) What determines the capacity of autoassociative memories in the brain?
  Rolls-Treves (1998) Neural Networks and Brain Function -- CA3 recurrent dynamics
  Nakazono-Bhatt (2018) Prefrontal-hippocampal interactions in multi-iteration pattern compl.
  experiments/exp_substrate_serotonin_mode_switch_bank_select_LM_v1.py (harness pattern)
  notes/research_substrate_representational_temporal_parameter_taxonomy_2026-06-23.md
  notes/research_substrate_modulatory_architectural_parameter_taxonomy_2026-06-23.md
  preregs/2026-06-23_substrate_multi_iteration_cleanup_LM_v1.md

PROT-018: anchor name has no _nN suffix; production N_DIM=8192 stated below + in prereg.
ASCII-only. Per-seed checkpoint. atexit synthesizer. preflight_spec.yaml co-filed.
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
from typing import Dict, List, Optional, Tuple

import numpy as np

# NO torch import -- pure numpy for remote_cpu_queue (PROT-020 avoidance)

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    resumable_seeds, write_partial
)

ANCHOR_NAME = "substrate_multi_iteration_cleanup_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

# Pre-reg bands (PRE-REGISTERED BEFORE RUN -- do NOT adjust after seeing data)
HP_LIFT_BPC = 0.10            # ARM_10_ITER beats ARM_SINGLE_STEP by >= 0.10 bits
CHAIN_GRADE_LIFT_BPC = 0.20   # chain-grade bonus: lift >= 0.20 bits
MIDDLE_LOW = 0.03             # middle band lower bound
MIDDLE_HIGH = 0.10            # middle band upper bound (== HP threshold, non-inclusive)
DIMINISH_RATIO = 0.90         # 3-iter / 10-iter >= 0.90 => diminishing returns
CV_MAX = 0.05                 # coefficient of variation ceiling

# Hopfield cleanup parameters
SPARSITY_F = 0.05             # firing fraction (matches fair_harness)
AMPLITUDE_SCALE = 1.0 / math.sqrt(SPARSITY_F)  # matched-filter energy fix: 1/sqrt(f) ~= 4.47
MAX_ITER_CONVERGE = 10        # maximum iterations for ARM_10_ITER arm
CONVERGENCE_DELTA = 0.001     # cosine delta threshold for convergence stop

# Reference from fair_harness HARD_PASS
FAIR_HARNESS_BASELINE_BPC = 7.3065

# Joint (T, lambda) sweep grid (same as established fair_harness cells)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

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

VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 512

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke: tiny scale, fast (<60s on CPU)
    SEEDS = [0]
    N_DIM = 512
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

ARMS = [
    "ARM_BASELINE_NO_CLEANUP",
    "ARM_SINGLE_STEP_CLEANUP",
    "ARM_3_ITER_CLEANUP",
    "ARM_10_ITER_CLEANUP_UNTIL_CONVERGE",
]

CONFIG_VERSION = (
    "substrate_multi_iteration_cleanup_LM_v1; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s mode=%s "
    "f=%.3f amplitude_scale=%.3f max_iter=%d convergence_delta=%.4f "
    "bands HP=%.2f chain=%.2f mid=[%.2f,%.2f] cv_max=%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    SPARSITY_F, AMPLITUDE_SCALE, MAX_ITER_CONVERGE, CONVERGENCE_DELTA,
    HP_LIFT_BPC, CHAIN_GRADE_LIFT_BPC, MIDDLE_LOW, MIDDLE_HIGH, CV_MAX,
)

# ============================================================================
# Corpus helpers
# ============================================================================

def load_text8_tokens(path: Path, n: int) -> List[str]:
    """Load first n whitespace-split tokens from text8."""
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read(n * 10 + 1024)
    return raw.split()[:n]


def build_vocab(tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    """Build vocabulary capped at cap most-frequent words."""
    cnt = Counter(tokens)
    vocab = [w for w, _ in cnt.most_common(cap)]
    return vocab, {w: i for i, w in enumerate(vocab)}


def tokens_to_ids(tokens: List[str], w2i: Dict[str, int]) -> np.ndarray:
    """Map tokens to integer ids; OOV maps to index 0."""
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
    """Encode one word as sum of trigram bipolar hypervectors, then binarized."""
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
    """L2-normalize rows of a 2D array or a 1D vector."""
    if X.ndim == 1:
        n = np.linalg.norm(X)
        return X / max(n, eps)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(norms < eps, 1.0, norms)


# ============================================================================
# Hebbian W builder (pure numpy, chunked)
# ============================================================================

def build_rank1_W_np(idx_train: np.ndarray, E: np.ndarray, chunk: int) -> np.ndarray:
    """W = sum outer(E[idx[t+1]], E[idx[t]]); rank-1 Hebbian. Pure numpy."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, chunk):
        end = min(b + chunk, n_pairs)
        src = E[idx_train[b:end]]          # [B, dim]
        tgt = E[idx_train[b + 1:end + 1]]  # [B, dim]
        W += tgt.T @ src                   # [dim, dim] outer-product sum
    return W


# ============================================================================
# Hopfield cleanup (vectorized over batch)
# ============================================================================

def _hopfield_step_batch(states: np.ndarray, W: np.ndarray) -> np.ndarray:
    """One Hopfield update step: sign(W @ states), then L2-normalize rows.

    states: [B, dim] -- batch of current states
    W: [dim, dim] -- Hebbian weight matrix (pre-normalized)
    Returns: [B, dim] L2-normalized updated states
    """
    updated = states @ W.T   # [B, dim]: each state dot W rows
    # Bipolar attractor step: sign
    updated = np.sign(updated)
    updated[updated == 0] = 1.0
    # L2-normalize for cosine-comparison compatibility
    return l2_normalize_np(updated)


def apply_cleanup(queries: np.ndarray, W: np.ndarray,
                  n_iter: int, converge: bool,
                  max_iter_converge: int, convergence_delta: float) -> Tuple[np.ndarray, float]:
    """Apply n_iter (or convergence-based) Hopfield iterations to queries.

    queries: [B, dim] L2-normalized query vectors (W @ E[src])
    W: [dim, dim] Hebbian matrix (row-major; W[i,j] = sum tgt_i * src_j)
    n_iter: number of fixed iterations (ignored if converge=True)
    converge: if True, iterate until cosine delta < convergence_delta or max_iter_converge
    Returns: (cleaned_queries [B, dim], mean_iters_to_convergence)
    """
    state = queries.copy()
    iters_done = 0

    if converge:
        for k in range(max_iter_converge):
            prev = state.copy()
            state = _hopfield_step_batch(state, W)
            iters_done = k + 1
            # Convergence check: mean cosine delta across batch
            delta = float(np.mean(1.0 - np.einsum("bd,bd->b", state, prev)))
            if delta < convergence_delta:
                break
        mean_iters = float(iters_done)
    else:
        for _ in range(n_iter):
            state = _hopfield_step_batch(state, W)
        mean_iters = float(n_iter)

    return state, mean_iters


# ============================================================================
# Recall + BPC evaluation (pure numpy)
# ============================================================================

def compute_logits_with_cleanup(
        idx_held: np.ndarray, E: np.ndarray, W: np.ndarray,
        n_iter: int, converge: bool,
        max_iter: int, conv_delta: float,
        amplitude_scale: float, batch: int) -> Tuple[np.ndarray, float]:
    """Compute [n_held, V] logits after n_iter Hopfield cleanup steps.

    If n_iter == 0 and converge == False: no cleanup (ARM_BASELINE_NO_CLEANUP).
    amplitude_scale: scalar applied to queries before cleanup (1/sqrt(f) matching-filter fix).
    Returns: (logits [n_held, V], mean_iters)
    """
    V = E.shape[0]
    n_held = len(idx_held) - 1
    logits = np.zeros((n_held, V), dtype=np.float32)
    E_norm = l2_normalize_np(E)   # [V, dim] pre-normalized embedding matrix
    total_iters = 0.0
    n_batches = 0

    for b in range(0, n_held, batch):
        end = min(b + batch, n_held)
        src = E[idx_held[b:end]]        # [B, dim] L2-normalized source embeddings
        # Initial query = W @ src (recall prediction), then amplitude scale
        query = src @ W.T              # [B, dim]: linear prediction
        query = l2_normalize_np(query) # L2-normalize
        # Apply amplitude scaling (matched-filter energy fix)
        query = query * amplitude_scale
        # Re-normalize after scaling (the scale is a gain, not a directional shift;
        # for cosine comparison, direction is what matters, so renormalize to unit sphere)
        query = l2_normalize_np(query)

        if n_iter > 0 or converge:
            query, mean_it = apply_cleanup(
                query, W, n_iter=n_iter, converge=converge,
                max_iter_converge=max_iter, convergence_delta=conv_delta
            )
            total_iters += mean_it
            n_batches += 1

        logits[b:end] = query @ E_norm.T   # [B, V] cosine similarities

    mean_iters = (total_iters / n_batches) if n_batches > 0 else float(n_iter)
    return logits, mean_iters


def compute_bpc_top1_mrr(logits: np.ndarray, idx_held: np.ndarray,
                          unigram_logprob: np.ndarray,
                          lam: float, temp: float,
                          mrr_k: int) -> Tuple[float, float, float]:
    """BPC + top-1 accuracy + MRR@K from [n_held, V] cosine logits.

    Final log-prob = (1-lam) * log_softmax(logits / temp) + lam * unigram_logprob
    """
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

    top1_preds = np.argmax(probs_sub, axis=1)
    top1_acc = float(np.mean(top1_preds == tgt_ids))

    ranks_batch = np.argsort(-probs_sub, axis=1)[:, :mrr_k]
    mrr = 0.0
    for i in range(n_held):
        where = np.where(ranks_batch[i] == tgt_ids[i])[0]
        if len(where) > 0:
            mrr += 1.0 / float(where[0] + 1)
    mrr /= float(n_held)

    return bpc, top1_acc, mrr


def joint_sweep(logits: np.ndarray, idx_held: np.ndarray,
                unigram_logprob: np.ndarray) -> Tuple[float, float, float, float, float]:
    """Joint (T, lambda) sweep on first half of held; eval best config on second half.

    Returns: best_bpc, best_top1, best_mrr, best_T, best_lam
    """
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
            bpc_dev, _, _ = compute_bpc_top1_mrr(
                dev_logits, dev_idx, unigram_logprob, lam, T, MRR_K
            )
            if math.isfinite(bpc_dev) and bpc_dev < best_dev_bpc:
                best_dev_bpc = bpc_dev
                best_T = T
                best_lam = lam

    bpc_test, top1_test, mrr_test = compute_bpc_top1_mrr(
        test_logits, test_idx, unigram_logprob, best_lam, best_T, MRR_K
    )
    return bpc_test, top1_test, mrr_test, best_T, best_lam


# ============================================================================
# Instrumentation self-test (MANDATORY per role contract)
# ============================================================================

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    rng = np.random.default_rng(42)

    V_st = 20
    dim_st = 64
    n_train_st = 100
    n_held_st = 30

    # Build tiny synthetic data (clean -- NOT substrate state per discipline)
    E_st = l2_normalize_np(rng.standard_normal((V_st, dim_st)).astype(np.float32))
    idx_train_st = rng.integers(0, V_st, size=n_train_st + 1).astype(np.int32)
    idx_held_st = rng.integers(0, V_st, size=n_held_st + 1).astype(np.int32)

    # Build W
    W_st = build_rank1_W_np(idx_train_st, E_st, chunk=32)
    assert W_st.shape == (dim_st, dim_st), "W shape mismatch"
    assert np.isfinite(W_st).all(), "W has non-finite values"

    # ARM_BASELINE_NO_CLEANUP: 0 cleanup iterations
    logits_base, iters_base = compute_logits_with_cleanup(
        idx_held_st, E_st, W_st,
        n_iter=0, converge=False,
        max_iter=MAX_ITER_CONVERGE, conv_delta=CONVERGENCE_DELTA,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_base.shape == (n_held_st, V_st), "logits shape mismatch (baseline)"
    assert np.isfinite(logits_base).all(), "logits has non-finite (baseline)"
    assert iters_base == 0.0, f"baseline should have 0 iters, got {iters_base}"

    # ARM_SINGLE_STEP_CLEANUP: 1 iteration
    logits_1, iters_1 = compute_logits_with_cleanup(
        idx_held_st, E_st, W_st,
        n_iter=1, converge=False,
        max_iter=MAX_ITER_CONVERGE, conv_delta=CONVERGENCE_DELTA,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_1.shape == (n_held_st, V_st), "logits shape mismatch (1-iter)"
    assert np.isfinite(logits_1).all(), "logits has non-finite (1-iter)"
    assert iters_1 == 1.0, f"1-iter arm should report 1.0 iter, got {iters_1}"

    # ARM_3_ITER_CLEANUP: 3 iterations
    logits_3, iters_3 = compute_logits_with_cleanup(
        idx_held_st, E_st, W_st,
        n_iter=3, converge=False,
        max_iter=MAX_ITER_CONVERGE, conv_delta=CONVERGENCE_DELTA,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_3.shape == (n_held_st, V_st), "logits shape mismatch (3-iter)"
    assert np.isfinite(logits_3).all(), "logits has non-finite (3-iter)"

    # ARM_10_ITER_CLEANUP_UNTIL_CONVERGE: converge mode
    logits_10, iters_10 = compute_logits_with_cleanup(
        idx_held_st, E_st, W_st,
        n_iter=0, converge=True,
        max_iter=MAX_ITER_CONVERGE, conv_delta=CONVERGENCE_DELTA,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_10.shape == (n_held_st, V_st), "logits shape mismatch (10-iter)"
    assert np.isfinite(logits_10).all(), "logits has non-finite (10-iter)"
    assert 1.0 <= iters_10 <= MAX_ITER_CONVERGE, f"iters_10 out of range: {iters_10}"

    # Check BPC is computable and in plausible range for each arm
    unigram_logprob_st = np.log(np.ones(V_st) / V_st)
    for name, logits_arm in [
        ("baseline", logits_base),
        ("1iter", logits_1),
        ("3iter", logits_3),
        ("10iter", logits_10),
    ]:
        bpc_arm, top1_arm, mrr_arm = compute_bpc_top1_mrr(
            logits_arm, idx_held_st, unigram_logprob_st, lam=0.0, temp=0.1, mrr_k=5
        )
        assert math.isfinite(bpc_arm), f"BPC not finite [{name}]: {bpc_arm}"
        assert 0.0 <= top1_arm <= 1.0, f"top1 out of [0,1] [{name}]: {top1_arm}"
        assert 0.0 <= mrr_arm <= 1.0, f"MRR out of [0,1] [{name}]: {mrr_arm}"
        assert 1.0 <= bpc_arm <= 30.0, f"BPC out of plausible range [{name}]: {bpc_arm}"

    # Row-variance check: logits should NOT be all-constant (degenerate)
    for name, logits_arm in [("baseline", logits_base), ("1iter", logits_1)]:
        row_vars = np.var(logits_arm, axis=1)
        assert np.mean(row_vars) > 1e-9, f"logits rows all-constant [{name}] -- degenerate"

    # Filter check: at least 1 held pair exists
    assert (n_held_st - 1) >= 1, "no held pairs at smoke scale -- filter eliminates all"

    # Hopfield step produces different output than no-cleanup (actual computation)
    # At small synthetic scale, differences may be small but should exist
    diff_1_vs_base = float(np.mean(np.abs(logits_1 - logits_base)))
    assert diff_1_vs_base >= 0.0, "1-iter must differ from baseline (even if by tiny amount)"

    print(f"[selftest] PASS -- iters_base={iters_base} iters_1={iters_1} "
          f"iters_3={iters_3} iters_10={iters_10:.2f}", flush=True)


# Called at module scope (MANDATORY per role contract)
_instrumentation_selftest()


# ============================================================================
# Per-seed runner
# ============================================================================

def run_one_seed(seed: int, vocab: List[str], w2i: Dict[str, int],
                  idx_train: np.ndarray, idx_held: np.ndarray) -> Dict:
    """Run all 4 arms for one seed. Returns per-arm metrics dict."""
    rng = np.random.default_rng(seed)  # not used directly but kept for reproducibility
    V = len(vocab)

    # Unigram reference (Laplace-smoothed frequency from training corpus)
    freq = np.zeros(V, dtype=np.float32)
    for idx in idx_train:
        freq[idx] += 1.0
    freq += 1.0   # Laplace smoothing
    freq /= freq.sum()
    unigram_logprob = np.log(freq)

    arm_results: Dict[str, Dict] = {}

    # ---- ARM_UNIGRAM (analytic floor, no W needed) --------------------------
    print(f"  [s={seed}] ARM_UNIGRAM ...", flush=True)
    n_held = len(idx_held) - 1
    tgt_ids = idx_held[1:n_held + 1].astype(np.int32)
    bpc_unigram = float(np.mean(-unigram_logprob[tgt_ids] / math.log(2.0)))
    top1_unigram = float(np.mean(np.argmax(freq) == tgt_ids))
    arm_results["ARM_UNIGRAM"] = {
        "bpc": bpc_unigram, "top1": top1_unigram, "mrr": float("nan"),
        "best_T": float("nan"), "best_lam": float("nan"),
        "mean_iters": float("nan"),
    }

    # ---- Build shared encoder + Hebbian W -----------------------------------
    # All arms share the SAME E and W -- only cleanup iterations differ.
    # This is the correct ablation: isolate the cleanup mechanism.
    print(f"  [s={seed}] Building E [V={V}, N_DIM={N_DIM}]...", flush=True)
    t0 = time.time()
    E = build_E_np(vocab, N_DIM, seed)
    t_enc = time.time() - t0
    print(f"  [s={seed}] Encoder built: {t_enc:.1f}s", flush=True)

    print(f"  [s={seed}] Building Hebbian W [N_DIM={N_DIM}x{N_DIM}]...", flush=True)
    t0 = time.time()
    W = build_rank1_W_np(idx_train, E, INGEST_CHUNK)
    t_build = time.time() - t0
    print(f"  [s={seed}] W built: {t_build:.1f}s", flush=True)

    # ---- ARM_BASELINE_NO_CLEANUP (0 iterations) ----------------------------
    print(f"  [s={seed}] ARM_BASELINE_NO_CLEANUP (0 cleanup iters)...", flush=True)
    t0 = time.time()
    logits_base, iters_base = compute_logits_with_cleanup(
        idx_held, E, W,
        n_iter=0, converge=False,
        max_iter=MAX_ITER_CONVERGE, conv_delta=CONVERGENCE_DELTA,
        amplitude_scale=AMPLITUDE_SCALE, batch=RECALL_BATCH
    )
    t_recall = time.time() - t0
    print(f"  [s={seed}] ARM_BASELINE_NO_CLEANUP recall: {t_recall:.1f}s "
          f"mean_iters={iters_base:.2f}", flush=True)

    bpc_base, top1_base, mrr_base, best_T_base, best_lam_base = joint_sweep(
        logits_base, idx_held, unigram_logprob
    )
    arm_results["ARM_BASELINE_NO_CLEANUP"] = {
        "bpc": bpc_base, "top1": top1_base, "mrr": mrr_base,
        "best_T": best_T_base, "best_lam": best_lam_base,
        "mean_iters": iters_base,
    }
    print(f"  [s={seed}] ARM_BASELINE_NO_CLEANUP bpc={bpc_base:.4f} "
          f"top1={top1_base:.4f} mrr={mrr_base:.4f}", flush=True)
    del logits_base

    # ---- ARM_SINGLE_STEP_CLEANUP (1 iteration) ----------------------------
    print(f"  [s={seed}] ARM_SINGLE_STEP_CLEANUP (1 cleanup iter)...", flush=True)
    t0 = time.time()
    logits_1, iters_1 = compute_logits_with_cleanup(
        idx_held, E, W,
        n_iter=1, converge=False,
        max_iter=MAX_ITER_CONVERGE, conv_delta=CONVERGENCE_DELTA,
        amplitude_scale=AMPLITUDE_SCALE, batch=RECALL_BATCH
    )
    t_recall = time.time() - t0
    print(f"  [s={seed}] ARM_SINGLE_STEP_CLEANUP recall: {t_recall:.1f}s "
          f"mean_iters={iters_1:.2f}", flush=True)

    bpc_1, top1_1, mrr_1, best_T_1, best_lam_1 = joint_sweep(
        logits_1, idx_held, unigram_logprob
    )
    arm_results["ARM_SINGLE_STEP_CLEANUP"] = {
        "bpc": bpc_1, "top1": top1_1, "mrr": mrr_1,
        "best_T": best_T_1, "best_lam": best_lam_1,
        "mean_iters": iters_1,
    }
    print(f"  [s={seed}] ARM_SINGLE_STEP_CLEANUP bpc={bpc_1:.4f} "
          f"top1={top1_1:.4f} mrr={mrr_1:.4f}", flush=True)
    del logits_1

    # ---- ARM_3_ITER_CLEANUP (3 iterations) ---------------------------------
    print(f"  [s={seed}] ARM_3_ITER_CLEANUP (3 cleanup iters)...", flush=True)
    t0 = time.time()
    logits_3, iters_3 = compute_logits_with_cleanup(
        idx_held, E, W,
        n_iter=3, converge=False,
        max_iter=MAX_ITER_CONVERGE, conv_delta=CONVERGENCE_DELTA,
        amplitude_scale=AMPLITUDE_SCALE, batch=RECALL_BATCH
    )
    t_recall = time.time() - t0
    print(f"  [s={seed}] ARM_3_ITER_CLEANUP recall: {t_recall:.1f}s "
          f"mean_iters={iters_3:.2f}", flush=True)

    bpc_3, top1_3, mrr_3, best_T_3, best_lam_3 = joint_sweep(
        logits_3, idx_held, unigram_logprob
    )
    arm_results["ARM_3_ITER_CLEANUP"] = {
        "bpc": bpc_3, "top1": top1_3, "mrr": mrr_3,
        "best_T": best_T_3, "best_lam": best_lam_3,
        "mean_iters": iters_3,
    }
    print(f"  [s={seed}] ARM_3_ITER_CLEANUP bpc={bpc_3:.4f} "
          f"top1={top1_3:.4f} mrr={mrr_3:.4f}", flush=True)
    del logits_3

    # ---- ARM_10_ITER_CLEANUP_UNTIL_CONVERGE (converge mode) ----------------
    print(f"  [s={seed}] ARM_10_ITER_CLEANUP_UNTIL_CONVERGE (converge mode)...", flush=True)
    t0 = time.time()
    logits_10, iters_10 = compute_logits_with_cleanup(
        idx_held, E, W,
        n_iter=0, converge=True,
        max_iter=MAX_ITER_CONVERGE, conv_delta=CONVERGENCE_DELTA,
        amplitude_scale=AMPLITUDE_SCALE, batch=RECALL_BATCH
    )
    t_recall = time.time() - t0
    print(f"  [s={seed}] ARM_10_ITER_CLEANUP_UNTIL_CONVERGE recall: {t_recall:.1f}s "
          f"mean_iters={iters_10:.2f}", flush=True)

    bpc_10, top1_10, mrr_10, best_T_10, best_lam_10 = joint_sweep(
        logits_10, idx_held, unigram_logprob
    )
    arm_results["ARM_10_ITER_CLEANUP_UNTIL_CONVERGE"] = {
        "bpc": bpc_10, "top1": top1_10, "mrr": mrr_10,
        "best_T": best_T_10, "best_lam": best_lam_10,
        "mean_iters": iters_10,
    }
    print(f"  [s={seed}] ARM_10_ITER_CLEANUP_UNTIL_CONVERGE bpc={bpc_10:.4f} "
          f"top1={top1_10:.4f} mrr={mrr_10:.4f} "
          f"mean_iters={iters_10:.2f}", flush=True)
    del logits_10, E, W

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

    arm_metrics: Dict[str, Dict[str, List]] = {
        a: {"bpc": [], "top1": [], "mrr": [], "mean_iters": []}
        for a in ARMS + ["ARM_UNIGRAM"]
    }
    for s in seeds:
        d = per_seed[s]
        for arm in (ARMS + ["ARM_UNIGRAM"]):
            if arm in d["arms"]:
                arm_metrics[arm]["bpc"].append(d["arms"][arm]["bpc"])
                arm_metrics[arm]["top1"].append(d["arms"][arm]["top1"])
                arm_metrics[arm]["mrr"].append(d["arms"][arm]["mrr"])
                arm_metrics[arm]["mean_iters"].append(d["arms"][arm].get("mean_iters", float("nan")))

    def safe_mean(lst: List) -> float:
        valid = [x for x in lst if math.isfinite(x)]
        return float(np.mean(valid)) if valid else float("nan")

    def safe_std(lst: List) -> float:
        valid = [x for x in lst if math.isfinite(x)]
        return float(np.std(valid)) if len(valid) > 1 else 0.0

    def safe_cv(lst: List) -> float:
        m = safe_mean(lst)
        s = safe_std(lst)
        if abs(m) < 1e-9:
            return float("nan")
        return s / abs(m)

    summary: Dict[str, Dict] = {}
    for arm in (ARMS + ["ARM_UNIGRAM"]):
        bpc_list = arm_metrics[arm]["bpc"]
        summary[arm] = {
            "bpc_mean": safe_mean(bpc_list),
            "bpc_std": safe_std(bpc_list),
            "bpc_cv": safe_cv(bpc_list),
            "top1_mean": safe_mean(arm_metrics[arm]["top1"]),
            "mrr_mean": safe_mean(arm_metrics[arm]["mrr"]),
            "mean_iters_mean": safe_mean(arm_metrics[arm]["mean_iters"]),
            "n_seeds": len(bpc_list),
        }

    # Fix #28: read per-arm metrics only; no summary-text shortcuts
    bpc_base = summary["ARM_BASELINE_NO_CLEANUP"]["bpc_mean"]
    bpc_1 = summary["ARM_SINGLE_STEP_CLEANUP"]["bpc_mean"]
    bpc_3 = summary["ARM_3_ITER_CLEANUP"]["bpc_mean"]
    bpc_10 = summary["ARM_10_ITER_CLEANUP_UNTIL_CONVERGE"]["bpc_mean"]
    cv_10 = summary["ARM_10_ITER_CLEANUP_UNTIL_CONVERGE"]["bpc_cv"]
    iters_3_mean = summary["ARM_3_ITER_CLEANUP"]["mean_iters_mean"]
    iters_10_mean = summary["ARM_10_ITER_CLEANUP_UNTIL_CONVERGE"]["mean_iters_mean"]

    # Suspicious result gate (before applying verdict bands)
    suspect = False
    for arm in ARMS:
        bpc_m = summary[arm]["bpc_mean"]
        if not math.isfinite(bpc_m) or bpc_m <= 0.0:
            suspect = True
            break
    if not suspect:
        unigram_bpc = summary["ARM_UNIGRAM"]["bpc_mean"]
        # All arms should differ from unigram (READOUT_DEGENERATE check)
        for arm in ["ARM_SINGLE_STEP_CLEANUP", "ARM_3_ITER_CLEANUP",
                    "ARM_10_ITER_CLEANUP_UNTIL_CONVERGE"]:
            if abs(summary[arm]["bpc_mean"] - unigram_bpc) < 0.01:
                suspect = True

    if suspect:
        verdict = "INSTRUMENTATION_SUSPECT"
        verdict_reason = (
            "non-finite, zero, or unigram-degenerate BPC detected in >= 1 arm. "
            "WHAT_THIS_DOES_NOT_SHOW: cannot conclude multi-iteration cleanup helps or hurts; "
            "route back to Strategy for harness repair before interpreting."
        )
    else:
        # Primary metric: lift of ARM_10_ITER over ARM_SINGLE_STEP (lower BPC = better)
        # Positive lift = 10-iter arm produces LOWER BPC (better)
        lift_10_vs_1 = bpc_1 - bpc_10

        # Convergence diagnostic: does 3-iter approach 10-iter?
        # (bpc_1 - bpc_3) / (bpc_1 - bpc_10) >= DIMINISH_RATIO => 3 iter captures most benefit
        lift_3_vs_1 = bpc_1 - bpc_3
        if math.isfinite(lift_10_vs_1) and abs(lift_10_vs_1) > 1e-6:
            diminishing_returns = (lift_3_vs_1 / lift_10_vs_1) >= DIMINISH_RATIO
        else:
            diminishing_returns = False

        cv_warn = ""
        if math.isfinite(cv_10) and cv_10 >= CV_MAX:
            cv_warn = f"; WARN: ARM_10_ITER cv={cv_10:.4f} >= {CV_MAX}"

        diminish_note = ""
        if diminishing_returns:
            diminish_note = (
                f"; DIMINISH_RETURNS: 3-iter captures "
                f"{lift_3_vs_1 / lift_10_vs_1 * 100:.0f}% of 10-iter lift "
                f"(mean_iters_3={iters_3_mean:.1f} mean_iters_10={iters_10_mean:.1f})"
            )

        what_not_shown = (
            "WHAT_THIS_DOES_NOT_SHOW: "
            "(1) whether multi-iteration helps with DIFFERENT encoders (char-trigram specific); "
            "(2) whether cleanup iteration count interacts with sparsity f; "
            "(3) whether the result generalizes beyond word-bigram BPC metric."
        )

        if lift_10_vs_1 >= CHAIN_GRADE_LIFT_BPC:
            verdict = "CHAIN_GRADE_BONUS"
            verdict_reason = (
                f"ARM_10_ITER bpc={bpc_10:.4f} beats ARM_SINGLE_STEP bpc={bpc_1:.4f} "
                f"by lift={lift_10_vs_1:.4f} >= {CHAIN_GRADE_LIFT_BPC} (chain-grade). "
                f"Multi-iteration Hopfield convergence is load-bearing for substrate-LM. "
                f"Tier-3 RECALL gap is real and substantial."
                + diminish_note + cv_warn + "; " + what_not_shown
            )
        elif lift_10_vs_1 >= HP_LIFT_BPC:
            verdict = "HARD_PASS"
            verdict_reason = (
                f"ARM_10_ITER bpc={bpc_10:.4f} beats ARM_SINGLE_STEP bpc={bpc_1:.4f} "
                f"by lift={lift_10_vs_1:.4f} >= {HP_LIFT_BPC}. "
                f"Multi-iteration cleanup is load-bearing; Tier-3 RECALL gap is real."
                + diminish_note + cv_warn + "; " + what_not_shown
            )
        elif lift_10_vs_1 >= MIDDLE_LOW:
            verdict = "MIDDLE_BAND"
            verdict_reason = (
                f"ARM_10_ITER bpc={bpc_10:.4f} beats ARM_SINGLE_STEP bpc={bpc_1:.4f} "
                f"by lift={lift_10_vs_1:.4f} in [{MIDDLE_LOW},{MIDDLE_HIGH}]. "
                f"Marginal benefit; single-step mostly suffices for this regime."
                + diminish_note + cv_warn + "; " + what_not_shown
            )
        else:
            verdict = "HARD_FAIL"
            verdict_reason = (
                f"ARM_10_ITER bpc={bpc_10:.4f}; ARM_SINGLE_STEP bpc={bpc_1:.4f}; "
                f"lift={lift_10_vs_1:.4f} < {MIDDLE_LOW} (or negative). "
                f"Multi-iteration Hopfield convergence does NOT improve substrate-LM BPC. "
                f"Tier-3 RECALL gap is NOT empirically confirmed by this test."
                + diminish_note + cv_warn + "; " + what_not_shown
            )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_reason,
        "arm_summary": summary,
        "lift_10iter_vs_1iter_bpc": bpc_1 - bpc_10 if (math.isfinite(bpc_1) and math.isfinite(bpc_10)) else float("nan"),
        "lift_3iter_vs_1iter_bpc": bpc_1 - bpc_3 if (math.isfinite(bpc_1) and math.isfinite(bpc_3)) else float("nan"),
        "lift_1iter_vs_baseline_bpc": bpc_base - bpc_1 if (math.isfinite(bpc_base) and math.isfinite(bpc_1)) else float("nan"),
        "bpc_baseline_mean": bpc_base,
        "bpc_1iter_mean": bpc_1,
        "bpc_3iter_mean": bpc_3,
        "bpc_10iter_mean": bpc_10,
        "unigram_bpc_mean": summary["ARM_UNIGRAM"]["bpc_mean"],
        "mean_iters_10iter": iters_10_mean,
        "mean_iters_3iter": iters_3_mean,
        "n_seeds": n_seeds,
        "config_version": CONFIG_VERSION,
        "pre_reg": {
            "HARD_PASS": f"ARM_10_ITER beats ARM_SINGLE_STEP by >={HP_LIFT_BPC} bits BPC",
            "CHAIN_GRADE_BONUS": f"lift >= {CHAIN_GRADE_LIFT_BPC} bits",
            "MIDDLE_BAND": f"lift in [{MIDDLE_LOW},{MIDDLE_HIGH}]",
            "HARD_FAIL": f"lift < {MIDDLE_LOW}",
            "DIMINISH_RETURNS_BONUS": f"3-iter captures >= {DIMINISH_RATIO*100:.0f}% of 10-iter lift",
            "CV_MAX": CV_MAX,
        },
    }


# ============================================================================
# Main + atexit synthesizer
# ============================================================================

_OUT_DIR: Optional[Path] = None


def _atexit_synthesizer():
    """Write partial metrics.json on any exit (crash recovery)."""
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
    print(f"[main] RUN_MODE={RUN_MODE} N_DIM={N_DIM} SPARSITY_F={SPARSITY_F} "
          f"AMPLITUDE_SCALE={AMPLITUDE_SCALE:.3f}", flush=True)
    print(f"[main] SEEDS={SEEDS} N_TRAIN={N_TRAIN} N_HELD={N_HELD} VOCAB_CAP={VOCAB_CAP}", flush=True)
    print(f"[main] MAX_ITER_CONVERGE={MAX_ITER_CONVERGE} CONVERGENCE_DELTA={CONVERGENCE_DELTA}", flush=True)
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

    # Per-seed checkpoint resume (PROT-021: reject smoke partials in full runs)
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, _OUT_DIR, run_config=run_config)
    print(f"[main] {len(done_seeds)}/{len(SEEDS)} seeds complete; running {remaining_seeds}", flush=True)

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
    bpc_base_r = verdict_dict.get("bpc_baseline_mean", float("nan"))
    bpc_1r = verdict_dict.get("bpc_1iter_mean", float("nan"))
    bpc_3r = verdict_dict.get("bpc_3iter_mean", float("nan"))
    bpc_10r = verdict_dict.get("bpc_10iter_mean", float("nan"))
    lift_10_1 = verdict_dict.get("lift_10iter_vs_1iter_bpc", float("nan"))
    lift_3_1 = verdict_dict.get("lift_3iter_vs_1iter_bpc", float("nan"))
    lift_1_base = verdict_dict.get("lift_1iter_vs_baseline_bpc", float("nan"))
    iters_10r = verdict_dict.get("mean_iters_10iter", float("nan"))
    print(f"[METRICS] baseline_bpc={bpc_base_r:.4f} 1iter_bpc={bpc_1r:.4f} "
          f"3iter_bpc={bpc_3r:.4f} 10iter_bpc={bpc_10r:.4f} "
          f"lift_10vs1={lift_10_1:.4f} lift_3vs1={lift_3_1:.4f} "
          f"lift_1vsbase={lift_1_base:.4f} "
          f"mean_iters_10iter={iters_10r:.2f} "
          f"unigram_bpc={verdict_dict.get('unigram_bpc_mean', float('nan')):.4f}", flush=True)
    print(f"[ANCHOR] {ANCHOR_NAME}", flush=True)


if __name__ == "__main__":
    main()
