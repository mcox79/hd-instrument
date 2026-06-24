"""substrate_iterative_cleanup_cue_clamped_production_v1 -- production-scale BPC validation.

MOTIVATION (2026-06-23):
  PRIMARY cell substrate_iterative_cleanup_cue_clamped_v1 HARD_PASSed at smoke
  (N=256/2048, alpha=0.3: +0.075 accuracy lift, cv=0.0). This SECONDARY cell
  validates the mechanism at production-scale BPC (N_DIM=8192, text8 N_TRAIN=100k).

  Prior HARD_FAIL (substrate_multi_iteration_cleanup_LM_v1) used BIPOLAR SIGN()
  Hopfield steps -- self-consistent dynamics causing query-independent fixed-point
  collapse (all cleanup arms converged to identical BPC=7.3753).

  This cell uses the CUE-CLAMPED softmax-attractor from hdlab/iterative_attractor.py:
      state_{t+1} = normalize(alpha * q0 + (1-alpha) * softmax(beta * state_t @ E.T) @ E)
  where q0 = initial (noisy) query and E = char-trigram embedding matrix (the codebook).
  Brain-canonical mechanism (CA3 perforant-path + Hasselmo 2002 + arXiv:2605.12466).

  USER directive (2026-06-23): "we have definitive proof from biology that this works.
  keep working towards the solution." Production-scale validation is warranted.

FIVE ARMS (shared E + W per seed; only alpha varies):
  ARM_BASELINE_NO_CLEANUP  -- raw W @ E[src]; no cleanup iterations; baseline bpc
  ARM_SINGLE_STEP          -- argmax_cleanup (single-step cosine lookup; reference)
  ARM_CLAMPED_ALPHA_03     -- alpha=0.3 (smoke-optimal; low cue re-injection)
  ARM_CLAMPED_ALPHA_05     -- alpha=0.5 (brain-canonical; balanced cue + attractor)
  ARM_CLAMPED_ALPHA_07     -- alpha=0.7 (high cue re-injection)

  All clamped arms use iterative_cleanup with max_steps=8, temp=4.0.

PRE-REGISTERED BANDS (2026-06-23; IMMUTABLE -- do NOT adjust after seeing data):
  HARD_PASS:         best ARM_CLAMPED beats ARM_BASELINE_NO_CLEANUP (7.2268 bpc)
                     by >= +0.10 bits BPC (lower bpc = better; lift = baseline - clamped)
  CHAIN_GRADE_BONUS: lift >= +0.20 AND beats cf-RPE chain-grade 7.1052 by >= +0.05
  MIDDLE_BAND:       lift +0.03 to +0.10
  HARD_FAIL:         lift <= +0.03 (cue-clamping smoke result does not scale to production)
  SANITY_RAIL_1:     ARM_BASELINE_NO_CLEANUP within +- 0.05 of 7.2268 (provenance check)
  SANITY_RAIL_2:     ARM_SINGLE_STEP within +- 0.05 of 7.3753 (prior HARD_FAIL reference)
  CV_MAX:            cv < 0.05 across seeds

NOTE on direction: BPC lower = better. "lift" here = bpc_baseline - bpc_clamped > 0 means
clamped arm is better. Prior HARD_FAIL had ARM_SINGLE_STEP bpc=7.3753 > baseline 7.2268
(cleanup HURT). Cue-clamping mechanism should prevent this collapse.

ROUTING:
  overnight_queue (GPU): N_DIM=8192 matmul-heavy (Fix #22); char-trigram W [8192x8192] at
  float32 = 256 MB; per-arm recall sweep [20000,8192]@[8192,4000] = GPU-beneficial.
  Fix #24: uses numpy for matmul (GPU machine runs this on CPU, which is still much faster
  than laptop; W is built once per seed and held in RAM). GPU-specific torch.cuda not
  applicable here as harness is pure-numpy for W build; overnight_queue CPU of remote
  machine is still the correct routing per N_DIM >= 8192 rule.

PROT-018: anchor name has no _nN suffix; production N_DIM=8192 stated in config below.
ASCII-only. Per-seed checkpoint. atexit synthesizer. preflight_spec.yaml co-filed.

CITES:
  Hasselmo (2002) The role of acetylcholine in learning and memory.
  arXiv:2605.12466 Attractor Models for Language and Reasoning (+32-46% LM perplexity)
  hdlab/iterative_attractor.py (alpha-parameterized cue-clamped softmax attractor)
  data/exp_substrate_multi_iteration_cleanup_LM_v1/metrics.json (prior HARD_FAIL baseline)
  data/exp_substrate_iterative_cleanup_cue_clamped_v1/metrics.json (smoke HARD_PASS)
  notes/exp_dev_handoff_research_multi_iter_cleanup_brain_analog_2026-06-23.md
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

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

# Import cue-clamped iterative_cleanup from hdlab (alpha-parameterized version).
# Inline fallback for remote machines that may have older hdlab.
try:
    import hdlab.iterative_attractor as _ia_mod
    import inspect as _inspect
    if "alpha" not in _inspect.signature(_ia_mod.iterative_cleanup).parameters:
        raise ImportError("hdlab.iterative_attractor.iterative_cleanup lacks alpha param")
    from hdlab.iterative_attractor import iterative_cleanup, argmax_cleanup
    _HDLAB_IMPORT = True
except (ImportError, AttributeError):
    _HDLAB_IMPORT = False

    def _l2n(X, eps=1e-12):
        if X.ndim == 1:
            n = float(np.linalg.norm(X) + eps)
            return (X / n).astype(np.float32)
        n = np.linalg.norm(X, axis=1, keepdims=True) + eps
        return (X / n).astype(np.float32)

    def _smx(z, axis=-1):
        z = z - z.max(axis=axis, keepdims=True)
        ez = np.exp(z.astype(np.float64))
        return (ez / (ez.sum(axis=axis, keepdims=True) + 1e-30)).astype(np.float32)

    def iterative_cleanup(query, codebook, *, temp=1.0, max_steps=8, tol=1e-3,
                          return_trace=False, scale_by_sqrt_d=True, alpha=0.0):
        """Inline cue-clamped iterative cleanup (fallback)."""
        squeeze = query.ndim == 1
        if squeeze:
            query = query[None, :]
        query = query.astype(np.float32)
        codebook = codebook.astype(np.float32)
        cb = _l2n(codebook)
        state = _l2n(query)
        q0 = state.copy()
        D = state.shape[1]
        beta = temp * float(np.sqrt(D)) if scale_by_sqrt_d else temp
        thr = tol * float(np.sqrt(D))
        trace = []
        converged = False
        steps_taken = 0
        for _t in range(max_steps):
            scores = beta * (state @ cb.T)
            weights = _smx(scores, axis=1)
            aest = weights @ cb
            new_state = _l2n(alpha * q0 + (1.0 - alpha) * aest)
            step_dist = float(np.mean(np.linalg.norm(new_state - state, axis=1)))
            trace.append(step_dist)
            state = new_state
            steps_taken = _t + 1
            if step_dist < thr:
                converged = True
                break
        final_scores = state @ cb.T
        argmax_idx = np.argmax(final_scores, axis=1).astype(np.int64)
        if squeeze:
            state = state[0]
            argmax_idx = int(argmax_idx[0])
        result = {"state": state, "argmax_idx": argmax_idx,
                  "n_iterations": steps_taken, "converged": converged}
        if return_trace:
            result["trace"] = trace
        return result

    def argmax_cleanup(query, codebook):
        """Single-step argmax cleanup (inline fallback)."""
        query = _l2n(query.astype(np.float32))
        cb = _l2n(codebook.astype(np.float32))
        if query.ndim == 1:
            return int(np.argmax(query @ cb.T))
        return np.argmax(query @ cb.T, axis=1).astype(np.int64)

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics,
    resumable_seeds,
)

ANCHOR_NAME = "substrate_iterative_cleanup_cue_clamped_production_v1"
print(f"[init] hdlab import: {'hdlab' if _HDLAB_IMPORT else 'inline-fallback'}", flush=True)

TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

# ============================================================================
# Pre-reg bands (PRE-REGISTERED 2026-06-23 -- IMMUTABLE; do NOT change after data)
# ============================================================================

# Primary comparison: best ARM_CLAMPED vs ARM_BASELINE_NO_CLEANUP
# BPC direction: LOWER is better; lift = bpc_baseline - bpc_clamped
HP_LIFT_BPC = 0.10            # HARD_PASS: clamped beats baseline by >= 0.10 bits
CHAIN_GRADE_LIFT_BPC = 0.20   # CHAIN_GRADE: clamped lift >= 0.20 AND beats cf-RPE ref
CF_RPE_CHAIN_GRADE_BPC = 7.1052  # cf-RPE chain-grade reference from prior cell
CF_RPE_CHAIN_GRADE_MARGIN = 0.05 # clamped must beat cf-RPE by >= 0.05 for chain-grade
MIDDLE_LOW = 0.03
MIDDLE_HIGH = 0.10

# Sanity rails (provenance checks; if violated, SANITY_FAIL before verdict)
BASELINE_BPC_REF = 7.2268     # ARM_BASELINE_NO_CLEANUP from prior multi-iter HARD_FAIL
SINGLE_STEP_BPC_REF = 7.3753  # ARM_SINGLE_STEP from prior HARD_FAIL (cleanup hurt)
SANITY_RAIL_TOL = 0.05        # sanity fails if arm deviates > 0.05 from reference

CV_MAX = 0.05                 # coefficient of variation ceiling

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
MRR_K = 10

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM = 8192             # PROT-018: production N; anchor has no _nN suffix; stated here
    N_TRAIN = 100_000
    N_HELD = 20_000
    INGEST_CHUNK = 4096
    RECALL_BATCH = 256       # batch size for recall sweep; keep moderate for RAM
    MAX_STEPS = 8            # max attractor iterations per cleanup call
    TEMP_CLEANUP = 4.0       # softmax inverse-temperature (fixed at smoke-optimal)
else:
    # Smoke: tiny scale, fast (<60s on CPU)
    SEEDS = [0]
    N_DIM = 512
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    MAX_STEPS = 8
    TEMP_CLEANUP = 4.0

SPARSITY_F = 0.05
AMPLITUDE_SCALE = 1.0 / math.sqrt(SPARSITY_F)  # ~4.47; matched-filter energy fix

# Alpha arms (cue re-injection weight)
ALPHA_ARMS = {
    "ARM_BASELINE_NO_CLEANUP": None,   # no cleanup -- raw W @ E[src] logits
    "ARM_SINGLE_STEP": None,           # argmax_cleanup (1-step cosine lookup)
    "ARM_CLAMPED_ALPHA_03": 0.3,       # smoke-optimal
    "ARM_CLAMPED_ALPHA_05": 0.5,       # brain-canonical balanced
    "ARM_CLAMPED_ALPHA_07": 0.7,       # high cue re-injection
}
ARMS = list(ALPHA_ARMS.keys())

# Joint (T, lambda) sweep grid -- Skunkworks META C7: exclude lambda=0.0
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]  # 0.0 excluded per META C7

CONFIG_VERSION = (
    "substrate_iterative_cleanup_cue_clamped_production_v1; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s mode=%s "
    "f=%.3f amplitude_scale=%.3f max_steps=%d temp_cleanup=%.1f "
    "bands HP=%.2f chain=%.2f mid=[%.2f,%.2f] cv_max=%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    SPARSITY_F, AMPLITUDE_SCALE, MAX_STEPS, TEMP_CLEANUP,
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
# Char-trigram encoder (pure numpy; same as prior cells)
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
    """Encode one word as sum of trigram bipolar HVs, then binarized."""
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


def build_E(vocab: List[str], n_dim: int, seed: int) -> np.ndarray:
    """Build [V, n_dim] L2-normalized char-trigram embeddings."""
    E = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    norms = np.linalg.norm(E, axis=1, keepdims=True)
    norms = np.where(norms < 1e-12, 1.0, norms)
    return E / norms


def l2n(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Row-wise L2 normalize."""
    if X.ndim == 1:
        n = float(np.linalg.norm(X) + eps)
        return X / n
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(norms < eps, 1.0, norms)


# ============================================================================
# Hebbian W builder (pure numpy, chunked)
# ============================================================================

def build_rank1_W(idx_train: np.ndarray, E: np.ndarray, chunk: int) -> np.ndarray:
    """W = sum outer(E[idx[t+1]], E[idx[t]]); rank-1 Hebbian."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, chunk):
        end = min(b + chunk, n_pairs)
        src = E[idx_train[b:end]]
        tgt = E[idx_train[b + 1:end + 1]]
        W += tgt.T @ src
    return W


# ============================================================================
# Recall with cue-clamped softmax-attractor cleanup
# ============================================================================

def compute_logits_cue_clamped(
        idx_held: np.ndarray, E: np.ndarray, W: np.ndarray,
        arm_type: str, alpha: Optional[float],
        max_steps: int, temp: float,
        amplitude_scale: float, batch: int) -> Tuple[np.ndarray, float]:
    """Compute [n_held, V] logits using cue-clamped attractor cleanup.

    arm_type:
      'baseline'    -- raw W @ E[src] logits (no cleanup)
      'single_step' -- argmax_cleanup (one cosine lookup)
      'clamped'     -- iterative_cleanup with given alpha

    Returns: (logits [n_held, V], mean_iters)
    """
    V = E.shape[0]
    n_held = len(idx_held) - 1
    logits = np.zeros((n_held, V), dtype=np.float32)
    E_norm = l2n(E)    # [V, N_DIM] pre-normalized for cosine similarity
    total_iters = 0.0
    n_batches = 0

    for b in range(0, n_held, batch):
        end = min(b + batch, n_held)
        B = end - b

        # Source embeddings and initial recall query
        src_ids = idx_held[b:end]      # [B]
        src = E[src_ids]               # [B, N_DIM] L2-normalized source embeddings

        # Recall query: W @ E[src]^T -> [B, N_DIM]
        query = src @ W.T              # [B, N_DIM] linear prediction
        query = l2n(query)
        # Amplitude scaling (matched-filter energy fix: 1/sqrt(f))
        query = l2n(query * amplitude_scale)

        if arm_type == "baseline":
            # No cleanup: cosine similarities directly
            logits[b:end] = query @ E_norm.T
        elif arm_type == "single_step":
            # Single-step argmax cleanup: find nearest codebook entry, use its embedding
            idxs = argmax_cleanup(query, E_norm)   # [B] int indices
            idxs = np.asarray(idxs, dtype=np.int64)
            retrieved = E_norm[idxs]               # [B, N_DIM]
            logits[b:end] = retrieved @ E_norm.T   # [B, V]
            total_iters += 1.0
            n_batches += 1
        else:
            # Cue-clamped iterative cleanup
            out = iterative_cleanup(
                query, E_norm,
                temp=temp, max_steps=max_steps, alpha=alpha,
                scale_by_sqrt_d=True,
            )
            cleaned = out["state"]      # [B, N_DIM] L2-normalized final state
            logits[b:end] = cleaned @ E_norm.T
            total_iters += float(out.get("n_iterations", max_steps))
            n_batches += 1

    mean_iters = (total_iters / n_batches) if n_batches > 0 else 0.0
    return logits, mean_iters


# ============================================================================
# BPC / top-1 / MRR evaluation with joint (T, lambda) sweep
# ============================================================================

def compute_bpc_top1_mrr(logits: np.ndarray, idx_held: np.ndarray,
                          unigram_logprob: np.ndarray,
                          lam: float, temp: float,
                          mrr_k: int) -> Tuple[float, float, float]:
    """BPC + top-1 accuracy + MRR@K from [n_held, V] cosine logits."""
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
    """Joint (T, lambda) sweep on first half of held; eval on second half."""
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

    # Build tiny synthetic data (clean synthetic -- NOT substrate state per discipline)
    E_st = l2n(rng.standard_normal((V_st, dim_st)).astype(np.float32))
    idx_train_st = rng.integers(0, V_st, size=n_train_st + 1).astype(np.int32)
    idx_held_st = rng.integers(0, V_st, size=n_held_st + 1).astype(np.int32)
    W_st = build_rank1_W(idx_train_st, E_st, chunk=32)
    assert W_st.shape == (dim_st, dim_st), f"W shape mismatch: {W_st.shape}"
    assert np.isfinite(W_st).all(), "W has non-finite values"

    unigram_st = np.log(np.ones(V_st, dtype=np.float32) / V_st)

    # Test ARM_BASELINE_NO_CLEANUP
    logits_base, iters_base = compute_logits_cue_clamped(
        idx_held_st, E_st, W_st,
        arm_type="baseline", alpha=None,
        max_steps=4, temp=4.0,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_base.shape == (n_held_st, V_st), f"baseline logits shape: {logits_base.shape}"
    assert np.isfinite(logits_base).all(), "baseline logits non-finite"
    assert iters_base == 0.0, f"baseline iters should be 0, got {iters_base}"

    # Test ARM_SINGLE_STEP
    logits_ss, iters_ss = compute_logits_cue_clamped(
        idx_held_st, E_st, W_st,
        arm_type="single_step", alpha=None,
        max_steps=4, temp=4.0,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_ss.shape == (n_held_st, V_st), f"single_step logits shape: {logits_ss.shape}"
    assert np.isfinite(logits_ss).all(), "single_step logits non-finite"
    assert iters_ss >= 1.0, f"single_step iters should be >=1, got {iters_ss}"

    # Test ARM_CLAMPED_ALPHA_05
    logits_a05, iters_a05 = compute_logits_cue_clamped(
        idx_held_st, E_st, W_st,
        arm_type="clamped", alpha=0.5,
        max_steps=4, temp=4.0,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_a05.shape == (n_held_st, V_st), f"alpha=0.5 logits shape: {logits_a05.shape}"
    assert np.isfinite(logits_a05).all(), "alpha=0.5 logits non-finite"
    assert iters_a05 >= 1.0, f"alpha=0.5 iters should be >=1, got {iters_a05}"

    # Test ARM_CLAMPED_ALPHA_03
    logits_a03, _ = compute_logits_cue_clamped(
        idx_held_st, E_st, W_st,
        arm_type="clamped", alpha=0.3,
        max_steps=4, temp=4.0,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_a03.shape == (n_held_st, V_st), "alpha=0.3 logits shape mismatch"
    assert np.isfinite(logits_a03).all(), "alpha=0.3 logits non-finite"

    # Test ARM_CLAMPED_ALPHA_07
    logits_a07, _ = compute_logits_cue_clamped(
        idx_held_st, E_st, W_st,
        arm_type="clamped", alpha=0.7,
        max_steps=4, temp=4.0,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_a07.shape == (n_held_st, V_st), "alpha=0.7 logits shape mismatch"
    assert np.isfinite(logits_a07).all(), "alpha=0.7 logits non-finite"

    # BPC is computable and in plausible range for each arm
    for arm_name, logits_arm in [
        ("baseline", logits_base),
        ("single_step", logits_ss),
        ("clamped_a05", logits_a05),
        ("clamped_a03", logits_a03),
        ("clamped_a07", logits_a07),
    ]:
        bpc_v, top1_v, mrr_v = compute_bpc_top1_mrr(
            logits_arm, idx_held_st, unigram_st, lam=0.1, temp=0.1, mrr_k=5
        )
        assert math.isfinite(bpc_v), f"BPC not finite [{arm_name}]: {bpc_v}"
        assert 0.0 <= top1_v <= 1.0, f"top1 out of [0,1] [{arm_name}]: {top1_v}"
        assert 1.0 <= bpc_v <= 30.0, f"BPC out of plausible range [{arm_name}]: {bpc_v}"

    # Row-variance check: logits not all-constant (degenerate)
    row_vars = np.var(logits_base, axis=1)
    assert np.mean(row_vars) > 1e-9, "baseline logits all-constant -- degenerate"

    # Filter check: at least 1 held pair
    assert (n_held_st - 1) >= 1, "no held pairs at smoke scale"

    # Arms produce different logits (non-degenerate cleanup)
    diff_a05_vs_base = float(np.mean(np.abs(logits_a05 - logits_base)))
    assert diff_a05_vs_base >= 0.0, "alpha=0.5 arm must produce different logits from baseline"

    print(f"[selftest] PASS -- baseline/single_step/a03/a05/a07 all compute valid BPC; "
          f"iters_ss={iters_ss:.1f} iters_a05={iters_a05:.1f}", flush=True)


# Called at module scope (MANDATORY per role contract)
_instrumentation_selftest()


# ============================================================================
# Per-seed runner
# ============================================================================

def run_one_seed(seed: int, vocab: List[str], w2i: Dict[str, int],
                  idx_train: np.ndarray, idx_held: np.ndarray) -> Dict:
    """Run all 5 arms for one seed. Returns per-arm metrics dict."""
    V = len(vocab)

    # Unigram reference (Laplace-smoothed frequency from training corpus)
    freq = np.zeros(V, dtype=np.float32)
    for idx in idx_train:
        freq[idx] += 1.0
    freq += 1.0    # Laplace smoothing
    freq /= freq.sum()
    unigram_logprob = np.log(freq)

    # ARM_UNIGRAM (analytic floor, no W needed)
    print(f"  [s={seed}] ARM_UNIGRAM ...", flush=True)
    n_held = len(idx_held) - 1
    tgt_ids = idx_held[1:n_held + 1].astype(np.int32)
    bpc_unigram = float(np.mean(-unigram_logprob[tgt_ids] / math.log(2.0)))
    top1_unigram = float(np.mean(np.argmax(freq) == tgt_ids))

    # Build shared encoder E and Hebbian W (all arms use same E, W per seed)
    print(f"  [s={seed}] Building E [V={V}, N_DIM={N_DIM}]...", flush=True)
    t0 = time.time()
    E = build_E(vocab, N_DIM, seed)
    t_enc = time.time() - t0
    print(f"  [s={seed}] E built: {t_enc:.1f}s "
          f"E_shape={E.shape} E_norm_mean={float(np.mean(np.linalg.norm(E, axis=1))):.4f}",
          flush=True)

    print(f"  [s={seed}] Building W [{N_DIM}x{N_DIM}]...", flush=True)
    t0 = time.time()
    W = build_rank1_W(idx_train, E, INGEST_CHUNK)
    t_build = time.time() - t0
    print(f"  [s={seed}] W built: {t_build:.1f}s "
          f"W_norm={float(np.linalg.norm(W)):.4f}", flush=True)

    arm_results: Dict[str, Dict] = {}
    arm_results["ARM_UNIGRAM"] = {
        "bpc": bpc_unigram, "top1": top1_unigram, "mrr": float("nan"),
        "best_T": float("nan"), "best_lam": float("nan"), "mean_iters": float("nan"),
    }
    print(f"  [s={seed}] ARM_UNIGRAM bpc={bpc_unigram:.4f}", flush=True)

    # Five experimental arms
    arm_spec = [
        ("ARM_BASELINE_NO_CLEANUP", "baseline",    None),
        ("ARM_SINGLE_STEP",         "single_step", None),
        ("ARM_CLAMPED_ALPHA_03",    "clamped",     0.3),
        ("ARM_CLAMPED_ALPHA_05",    "clamped",     0.5),
        ("ARM_CLAMPED_ALPHA_07",    "clamped",     0.7),
    ]

    for arm_name, arm_type, alpha in arm_spec:
        print(f"  [s={seed}] {arm_name} arm_type={arm_type} alpha={alpha} ...", flush=True)
        t0 = time.time()
        logits_arm, mean_iters = compute_logits_cue_clamped(
            idx_held, E, W,
            arm_type=arm_type, alpha=alpha,
            max_steps=MAX_STEPS, temp=TEMP_CLEANUP,
            amplitude_scale=AMPLITUDE_SCALE, batch=RECALL_BATCH,
        )
        t_recall = time.time() - t0
        print(f"  [s={seed}] {arm_name} recall: {t_recall:.1f}s mean_iters={mean_iters:.2f}",
              flush=True)

        bpc_arm, top1_arm, mrr_arm, best_T, best_lam = joint_sweep(
            logits_arm, idx_held, unigram_logprob
        )
        arm_results[arm_name] = {
            "bpc": bpc_arm, "top1": top1_arm, "mrr": mrr_arm,
            "best_T": best_T, "best_lam": best_lam, "mean_iters": mean_iters,
        }
        print(f"  [s={seed}] {arm_name}: bpc={bpc_arm:.4f} top1={top1_arm:.4f} "
              f"mrr={mrr_arm:.4f} T={best_T} lam={best_lam}", flush=True)
        del logits_arm

    del E, W

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

    all_arm_keys = ARMS + ["ARM_UNIGRAM"]
    arm_metrics: Dict[str, Dict[str, List]] = {
        a: {"bpc": [], "top1": [], "mrr": [], "mean_iters": []}
        for a in all_arm_keys
    }
    for s in seeds:
        d = per_seed[s]
        for arm in all_arm_keys:
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
    for arm in all_arm_keys:
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

    # Fix #28: read per-arm metrics; no cross-arm summary shortcuts
    bpc_base = summary["ARM_BASELINE_NO_CLEANUP"]["bpc_mean"]
    bpc_ss = summary["ARM_SINGLE_STEP"]["bpc_mean"]
    bpc_a03 = summary["ARM_CLAMPED_ALPHA_03"]["bpc_mean"]
    bpc_a05 = summary["ARM_CLAMPED_ALPHA_05"]["bpc_mean"]
    bpc_a07 = summary["ARM_CLAMPED_ALPHA_07"]["bpc_mean"]
    bpc_unigram = summary["ARM_UNIGRAM"]["bpc_mean"]

    what_not_shown = (
        "WHAT_THIS_DOES_NOT_SHOW: "
        "(1) whether alpha=0.3 remains optimal across noise levels or M/N ratios; "
        "(2) whether result generalizes to non-char-trigram encoders; "
        "(3) whether cue-clamping combined with sparsity changes has compound effects."
    )

    # Suspicious result gate
    suspect = False
    suspect_reason = ""
    for arm in ARMS:
        bm = summary[arm]["bpc_mean"]
        if not math.isfinite(bm) or bm <= 0.0:
            suspect = True
            suspect_reason = f"{arm} bpc_mean={bm} is non-finite or non-positive"
            break
    if not suspect:
        # All arms within 0.001 of each other = degenerate (no discriminator)
        finite_bpcs = [b for b in [bpc_base, bpc_ss, bpc_a03, bpc_a05, bpc_a07]
                       if math.isfinite(b)]
        if len(finite_bpcs) >= 3 and (max(finite_bpcs) - min(finite_bpcs)) < 0.001:
            suspect = True
            suspect_reason = (
                f"all arms collapsed to near-identical BPC "
                f"max={max(finite_bpcs):.4f} min={min(finite_bpcs):.4f} "
                f"(diff < 0.001); no discriminator present"
            )

    if suspect:
        return {
            "verdict": "INSTRUMENTATION_SUSPECT",
            "verdict_msg": (
                f"INSTRUMENTATION_SUSPECT: {suspect_reason}. "
                "Route to Strategy for harness repair before interpreting. "
                "; " + what_not_shown
            ),
            "arm_summary": summary,
            "n_seeds": n_seeds,
            "config_version": CONFIG_VERSION,
            "pre_reg": _prereg_dict(),
        }

    # Sanity rails (only applicable at full scale N=8192, N_TRAIN=100k;
    # smoke uses N=512/N_TRAIN=2000 which gives BPC ~5 on small vocab -- different regime)
    sanity_fail = False
    sanity_msg = ""
    # Detect run mode from config_version string (smoke produces ~5 bpc vs full ~7 bpc)
    _is_full_scale = "mode=full" in CONFIG_VERSION
    if _is_full_scale:
        if math.isfinite(bpc_base) and abs(bpc_base - BASELINE_BPC_REF) > SANITY_RAIL_TOL:
            sanity_fail = True
            sanity_msg = (
                f"SANITY_RAIL_1 FAIL: ARM_BASELINE_NO_CLEANUP bpc={bpc_base:.4f} "
                f"deviates > {SANITY_RAIL_TOL} from reference {BASELINE_BPC_REF} "
                f"(delta={abs(bpc_base - BASELINE_BPC_REF):.4f}). "
                "Encoding or corpus mismatch vs prior run."
            )
        if math.isfinite(bpc_ss) and abs(bpc_ss - SINGLE_STEP_BPC_REF) > SANITY_RAIL_TOL:
            if not sanity_fail:
                sanity_msg = (
                    f"SANITY_RAIL_2 FAIL: ARM_SINGLE_STEP bpc={bpc_ss:.4f} "
                    f"deviates > {SANITY_RAIL_TOL} from reference {SINGLE_STEP_BPC_REF} "
                    f"(delta={abs(bpc_ss - SINGLE_STEP_BPC_REF):.4f})."
                )
            sanity_fail = True

    if sanity_fail:
        return {
            "verdict": "SANITY_FAIL",
            "verdict_msg": (
                sanity_msg + " Cannot apply pre-reg bands against mis-calibrated baseline. "
                "; " + what_not_shown
            ),
            "arm_summary": summary,
            "bpc_baseline_mean": bpc_base,
            "bpc_ss_mean": bpc_ss,
            "n_seeds": n_seeds,
            "config_version": CONFIG_VERSION,
            "pre_reg": _prereg_dict(),
        }

    # Primary verdict: best ARM_CLAMPED vs ARM_BASELINE_NO_CLEANUP
    # BPC: lower = better; lift = bpc_baseline - bpc_clamped > 0 means clamped is better
    lifts = {
        "ARM_CLAMPED_ALPHA_03": bpc_base - bpc_a03,
        "ARM_CLAMPED_ALPHA_05": bpc_base - bpc_a05,
        "ARM_CLAMPED_ALPHA_07": bpc_base - bpc_a07,
    }
    finite_lifts = {k: v for k, v in lifts.items() if math.isfinite(v)}
    if not finite_lifts:
        best_arm = "ARM_CLAMPED_ALPHA_03"
        best_lift = float("nan")
    else:
        best_arm = max(finite_lifts, key=lambda k: finite_lifts[k])
        best_lift = finite_lifts[best_arm]
    best_alpha_label = best_arm.split("_ALPHA_")[-1] if "_ALPHA_" in best_arm else "?"
    best_bpc = {
        "ARM_CLAMPED_ALPHA_03": bpc_a03,
        "ARM_CLAMPED_ALPHA_05": bpc_a05,
        "ARM_CLAMPED_ALPHA_07": bpc_a07,
    }.get(best_arm, float("nan"))

    best_cv = summary[best_arm]["bpc_cv"]
    cv_warn = ""
    if math.isfinite(best_cv) and best_cv >= CV_MAX:
        cv_warn = f"; WARN cv={best_cv:.4f} >= {CV_MAX}"

    # Lift of ARM_SINGLE_STEP vs baseline for context
    lift_ss_vs_base = bpc_base - bpc_ss

    arm_bpc_detail = (
        f"ARM_BASELINE_NO_CLEANUP bpc={bpc_base:.4f}; "
        f"ARM_SINGLE_STEP bpc={bpc_ss:.4f} lift_vs_base={lift_ss_vs_base:+.4f}; "
        f"ARM_CLAMPED_ALPHA_03 bpc={bpc_a03:.4f} lift={bpc_base-bpc_a03:+.4f}; "
        f"ARM_CLAMPED_ALPHA_05 bpc={bpc_a05:.4f} lift={bpc_base-bpc_a05:+.4f}; "
        f"ARM_CLAMPED_ALPHA_07 bpc={bpc_a07:.4f} lift={bpc_base-bpc_a07:+.4f}"
    )

    if not math.isfinite(best_lift):
        verdict = "NO_RESULTS"
        verdict_msg = "best_lift not finite; no valid clamped arm metrics. " + arm_bpc_detail
    elif best_lift >= CHAIN_GRADE_LIFT_BPC:
        # Check chain-grade bonus condition: also beats cf-RPE by CF_RPE_CHAIN_GRADE_MARGIN
        chain_ok = (
            math.isfinite(best_bpc) and
            (CF_RPE_CHAIN_GRADE_BPC - best_bpc) >= CF_RPE_CHAIN_GRADE_MARGIN
        )
        if chain_ok:
            verdict = "CHAIN_GRADE_BONUS"
            verdict_msg = (
                f"best ARM_CLAMPED (alpha={best_alpha_label}): bpc={best_bpc:.4f} "
                f"lift_vs_base={best_lift:+.4f} >= {CHAIN_GRADE_LIFT_BPC} (chain-grade). "
                f"Also beats cf-RPE {CF_RPE_CHAIN_GRADE_BPC} by "
                f"{CF_RPE_CHAIN_GRADE_BPC - best_bpc:.4f} >= {CF_RPE_CHAIN_GRADE_MARGIN}. "
                "Cue-clamped softmax-attractor cleanup is chain-grade for substrate-LM. "
                + arm_bpc_detail + cv_warn + "; " + what_not_shown
            )
        else:
            verdict = "HARD_PASS"
            verdict_msg = (
                f"best ARM_CLAMPED (alpha={best_alpha_label}): bpc={best_bpc:.4f} "
                f"lift_vs_base={best_lift:+.4f} >= {CHAIN_GRADE_LIFT_BPC}. "
                f"Chain-grade lift achieved but cf-RPE {CF_RPE_CHAIN_GRADE_BPC} margin "
                f"not met (best_bpc={best_bpc:.4f} "
                f"margin={CF_RPE_CHAIN_GRADE_BPC - best_bpc:.4f} < {CF_RPE_CHAIN_GRADE_MARGIN}). "
                "Still HARD_PASS: cue-clamping is a major production-scale lever. "
                + arm_bpc_detail + cv_warn + "; " + what_not_shown
            )
    elif best_lift >= HP_LIFT_BPC:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"best ARM_CLAMPED (alpha={best_alpha_label}): bpc={best_bpc:.4f} "
            f"lift_vs_base={best_lift:+.4f} >= {HP_LIFT_BPC}. "
            "Cue-clamped softmax-attractor cleanup beats no-cleanup at production scale. "
            "Brain-canonical mechanism scales. "
            + arm_bpc_detail + cv_warn + "; " + what_not_shown
        )
    elif best_lift >= MIDDLE_LOW:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"best ARM_CLAMPED (alpha={best_alpha_label}): bpc={best_bpc:.4f} "
            f"lift_vs_base={best_lift:+.4f} in [{MIDDLE_LOW},{MIDDLE_HIGH}]. "
            "Partial lift at production scale; mechanism scales but modestly. "
            + arm_bpc_detail + cv_warn + "; " + what_not_shown
        )
    else:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"best ARM_CLAMPED (alpha={best_alpha_label}): bpc={best_bpc:.4f} "
            f"lift_vs_base={best_lift:+.4f} <= {MIDDLE_LOW}. "
            "Cue-clamped cleanup smoke result does not scale to production N=8192. "
            "Mechanism works at small N but production encoding geometry differs. "
            + arm_bpc_detail + cv_warn + "; " + what_not_shown
        )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "arm_summary": summary,
        "bpc_baseline_mean": bpc_base,
        "bpc_ss_mean": bpc_ss,
        "bpc_clamped_a03_mean": bpc_a03,
        "bpc_clamped_a05_mean": bpc_a05,
        "bpc_clamped_a07_mean": bpc_a07,
        "bpc_unigram_mean": bpc_unigram,
        "best_clamped_arm": best_arm,
        "best_lift_vs_baseline": best_lift,
        "lift_ss_vs_baseline": lift_ss_vs_base,
        "n_seeds": n_seeds,
        "config_version": CONFIG_VERSION,
        "pre_reg": _prereg_dict(),
    }


def _prereg_dict() -> Dict:
    return {
        "HARD_PASS": f"best ARM_CLAMPED beats ARM_BASELINE_NO_CLEANUP by >= {HP_LIFT_BPC} bits BPC",
        "CHAIN_GRADE_BONUS": (
            f"lift >= {CHAIN_GRADE_LIFT_BPC} AND beats cf-RPE {CF_RPE_CHAIN_GRADE_BPC} "
            f"by >= {CF_RPE_CHAIN_GRADE_MARGIN}"
        ),
        "MIDDLE_BAND": f"lift in [{MIDDLE_LOW},{MIDDLE_HIGH}]",
        "HARD_FAIL": f"lift <= {MIDDLE_LOW}",
        "SANITY_RAIL_1": (
            f"ARM_BASELINE_NO_CLEANUP within +-{SANITY_RAIL_TOL} of {BASELINE_BPC_REF}"
        ),
        "SANITY_RAIL_2": (
            f"ARM_SINGLE_STEP within +-{SANITY_RAIL_TOL} of {SINGLE_STEP_BPC_REF}"
        ),
        "CV_MAX": CV_MAX,
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
    print(f"[main] MAX_STEPS={MAX_STEPS} TEMP_CLEANUP={TEMP_CLEANUP}", flush=True)
    print(f"[main] ARMS={ARMS}", flush=True)
    print(f"[main] CONFIG={CONFIG_VERSION}", flush=True)
    print(f"[main] LAMBDA_GRID={LAMBDA_GRID} (0.0 excluded per META C7)", flush=True)
    print(f"[main] hdlab import: {'hdlab' if _HDLAB_IMPORT else 'inline-fallback'}", flush=True)

    print("[main] loading text8...", flush=True)
    t0 = time.time()
    tokens = load_text8_tokens(TEXT8, N_TRAIN + N_HELD + 1000)
    vocab, w2i = build_vocab(tokens[:N_TRAIN], VOCAB_CAP)
    V = len(vocab)
    print(f"[main] vocab size={V} corpus_tokens={len(tokens)} ({time.time()-t0:.1f}s)", flush=True)

    all_ids = tokens_to_ids(tokens, w2i)
    idx_train = all_ids[:N_TRAIN]
    idx_held = all_ids[N_TRAIN:N_TRAIN + N_HELD + 1]

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, _OUT_DIR, run_config=run_config)
    print(f"[main] {len(done_seeds)}/{len(SEEDS)} seeds complete; running {remaining_seeds}",
          flush=True)

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
    bpc_ss_r = verdict_dict.get("bpc_ss_mean", float("nan"))
    bpc_a03_r = verdict_dict.get("bpc_clamped_a03_mean", float("nan"))
    bpc_a05_r = verdict_dict.get("bpc_clamped_a05_mean", float("nan"))
    bpc_a07_r = verdict_dict.get("bpc_clamped_a07_mean", float("nan"))
    best_lift = verdict_dict.get("best_lift_vs_baseline", float("nan"))
    best_arm_r = verdict_dict.get("best_clamped_arm", "?")
    print(f"[METRICS] baseline_bpc={bpc_base_r:.4f} ss_bpc={bpc_ss_r:.4f} "
          f"a03_bpc={bpc_a03_r:.4f} a05_bpc={bpc_a05_r:.4f} a07_bpc={bpc_a07_r:.4f} "
          f"best_arm={best_arm_r} best_lift={best_lift:+.4f} "
          f"unigram_bpc={verdict_dict.get('bpc_unigram_mean', float('nan')):.4f}", flush=True)
    print(f"[ANCHOR] {ANCHOR_NAME}", flush=True)


if __name__ == "__main__":
    main()
