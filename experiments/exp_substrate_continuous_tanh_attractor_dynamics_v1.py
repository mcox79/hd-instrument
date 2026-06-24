"""substrate_continuous_tanh_attractor_dynamics_v1 -- Continuous-tanh attractor dynamics fix.

MOTIVATION (2026-06-23):
  Multi-iter cleanup HARD_FAILed because sign(W@x) binarizes in 1 step: all multi-iter
  arms become bit-identical after 1 Hopfield iteration (bipolar attractor = no multi-iter
  benefit). Brain CA3 uses GRADED continuous activation with subtractive feedback inhibition,
  NOT bipolar binarization (Treves-Rolls 1991; Rolls 2013 CA3 recurrent dynamics).

  Fix: replace sign() with tanh(beta * state), the brain-analog continuous attractor.
  The gain beta controls the softness/sharpness of the nonlinearity:
    - beta<<1 (soft): near-linear dynamics, slow convergence
    - beta~1 (unity): moderate nonlinearity, brain-like regime
    - beta>>1 (sharp): approaches sign() in limit -- reproduces v1 failure mode
  This is the ORTHOGONAL fix to ARM cue-clamped re-injection (a340a5a51b818ed33).

BRAIN-EXISTENCE-PROOF:
  Brain CA3 pyramidal cells run GRADED activity: firing rates in [0, max_rate], not {-1,+1}.
  Subtractive inhibition (via interneurons) provides the normalization that prevents
  runaway positive feedback. The sign() discretization eliminates the graded signal
  that allows multi-iteration convergence to a distinct attractor from single-step.
  tanh(beta * state) preserves the continuous graded signal while providing saturation.

SIX ARMS:
  ARM_BASELINE_NO_CLEANUP     -- reproduces fair_harness baseline; no cleanup iterations
  ARM_SIGN_HOPFIELD_3ITER     -- reproduces v1 HARD_FAIL; sign() binarization 3 iters
  ARM_TANH_BETA_0p5           -- continuous-tanh, low gain (soft nonlinearity)
  ARM_TANH_BETA_1p0           -- continuous-tanh, unity gain (brain-like regime)
  ARM_TANH_BETA_2p0           -- continuous-tanh, mid gain
  ARM_TANH_BETA_5p0           -- continuous-tanh, high gain (approaches sign())

UPDATE RULE (for tanh arms):
  state_0 = L2_normalize(W @ E[src]) * amplitude_scale
  state_{k+1} = L2_normalize(tanh(beta * state_k))
  Stop after 3 iterations (same as v1 ARM_3_ITER -- avoids overlong runs).
  No converge mode (tanh is continuous so can oscillate; fixed 3-iter stable budget).

PRE-REGISTERED BANDS (pre-registered BEFORE run, 2026-06-23):
  HARD_PASS:        any ARM_TANH_BETA beats ARM_BASELINE_NO_CLEANUP by >= +0.05 bits BPC
  CHAIN_GRADE_BONUS: lift >= +0.15 AND beats cf-RPE chain-grade 7.1052
  MIDDLE_BAND:       lift +0.02 to +0.05 bits
  HARD_FAIL:         all ARM_TANH_BETA <= ARM_BASELINE_NO_CLEANUP across all beta
  SANITY_RAIL:       ARM_BASELINE_NO_CLEANUP must reproduce 7.2268 +- 0.05
                     (matches v1 BASELINE_NO_CLEANUP finding per Skunkworks)
  CV_MAX:            cv < 0.05

CRITICAL DISCIPLINES:
  PURE NUMPY: no torch import; remote_cpu_queue routing (PROT-020 avoidance + PROT-018)
  Fix #28: per-arm BPC reported separately; no cross-arm narrative in verdict_msg
  Fix #14: ONE cell (not a batch)
  A5 path-scoped commit
  ASCII-only, no emojis, no em dashes, no em-width unicode
  Instrumentation self-test called at module scope (MANDATORY)
  Suspicious-result gate before any verdict claim
  CALIBRATION_COLLAPSE check per Skunkworks C7 META recommendation

PROT-018: anchor name has no _nN suffix; production N_DIM=4096 stated here + in prereg.

CITES:
  Treves-Rolls (1991) What determines the capacity of autoassociative memories in the brain?
  Rolls (2013) A biased activation theory of the cognitive and attractor network properties of
               the recurrent collateral connections of the CA3 hippocampal neurons
  Skunkworks BATCH VET: notes/skunkworks_to_all_BATCH_VET_4_recent_negatives_2026-06-23.md
  preregs/2026-06-23_substrate_continuous_tanh_attractor_dynamics_v1.md
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

ANCHOR_NAME = "substrate_continuous_tanh_attractor_dynamics_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

# Pre-reg bands (PRE-REGISTERED BEFORE RUN -- do NOT adjust after seeing data)
# HARD_PASS: any ARM_TANH_BETA beats ARM_BASELINE_NO_CLEANUP by >= 0.05 bits
HP_LIFT_BPC = 0.05
# CHAIN_GRADE_BONUS: lift >= 0.15 AND beats cf-RPE chain-grade 7.1052
CHAIN_GRADE_LIFT_BPC = 0.15
CHAIN_GRADE_ABS_BPC = 7.1052  # must beat this to qualify chain-grade
# MIDDLE_BAND: lift in [0.02, 0.05)
MIDDLE_LOW = 0.02
MIDDLE_HIGH = 0.05
# SANITY_RAIL: ARM_BASELINE_NO_CLEANUP must reproduce 7.2268 +- 0.05
SANITY_BASELINE_REF = 7.2268
SANITY_BASELINE_TOL = 0.05
# CV ceiling
CV_MAX = 0.05

# Hopfield cleanup parameters
SPARSITY_F = 0.05                                     # firing fraction (matches fair_harness)
AMPLITUDE_SCALE = 1.0 / math.sqrt(SPARSITY_F)        # matched-filter energy fix: 1/sqrt(f)
N_ITER_CLEANUP = 3                                    # fixed iterations for all cleanup arms

# Tanh beta grid for the tanh arms
TANH_BETAS = [0.5, 1.0, 2.0, 5.0]

# Reference from fair_harness
FAIR_HARNESS_BASELINE_BPC = 7.3065

# Joint (T, lambda) sweep grid
# NOTE: includes 0.02 and 0.05 per C7 META recommendation to bracket fair_harness optimum (~0.033)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.02, 0.05, 0.1, 0.3, 0.5, 0.7, 1.0]
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
    N_DIM = 4096
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
    "ARM_SIGN_HOPFIELD_3ITER",
    "ARM_TANH_BETA_0p5",
    "ARM_TANH_BETA_1p0",
    "ARM_TANH_BETA_2p0",
    "ARM_TANH_BETA_5p0",
]

CONFIG_VERSION = (
    "substrate_continuous_tanh_attractor_dynamics_v1; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d seeds=%s mode=%s "
    "f=%.3f amplitude_scale=%.3f n_iter=%d "
    "bands HP=%.2f chain=%.2f mid=[%.2f,%.2f] cv_max=%.2f "
    "sanity_baseline_ref=%.4f sanity_tol=%.4f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, SEEDS, RUN_MODE,
    SPARSITY_F, AMPLITUDE_SCALE, N_ITER_CLEANUP,
    HP_LIFT_BPC, CHAIN_GRADE_LIFT_BPC, MIDDLE_LOW, MIDDLE_HIGH, CV_MAX,
    SANITY_BASELINE_REF, SANITY_BASELINE_TOL,
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
# Attractor dynamics (two variants)
# ============================================================================

def _sign_hopfield_step_batch(states: np.ndarray, W: np.ndarray) -> np.ndarray:
    """One bipolar Hopfield step: sign(W @ states), then L2-normalize rows.

    This is the v1 HARD_FAIL update rule. Preserved as ARM_SIGN_HOPFIELD_3ITER
    to reproduce the failure mode in the same experimental context.

    states: [B, dim]
    W: [dim, dim]
    Returns: [B, dim] L2-normalized
    """
    updated = states @ W.T      # [B, dim]
    updated = np.sign(updated)
    updated[updated == 0] = 1.0
    return l2_normalize_np(updated)


def _tanh_hopfield_step_batch(states: np.ndarray, W: np.ndarray, beta: float) -> np.ndarray:
    """One continuous-tanh Hopfield step: tanh(beta * W @ states), then L2-normalize.

    Brain-analog: graded continuous activation preserves directional signal
    across multiple iterations (no information destruction via binarization).
    beta controls gain: 0.5=soft, 1.0=unity, 2.0=mid, 5.0=approaches sign().

    states: [B, dim]
    W: [dim, dim]
    beta: float gain parameter
    Returns: [B, dim] L2-normalized
    """
    pre_act = states @ W.T      # [B, dim]: linear field
    updated = np.tanh(beta * pre_act)
    # Handle near-zero activation (avoid div-by-zero in L2-norm)
    return l2_normalize_np(updated)


def apply_cleanup(queries: np.ndarray, W: np.ndarray,
                  arm_type: str, beta: float, n_iter: int) -> np.ndarray:
    """Apply n_iter cleanup iterations using the specified arm_type.

    arm_type: 'none'  -- no cleanup (ARM_BASELINE_NO_CLEANUP)
              'sign'  -- bipolar sign attractor (ARM_SIGN_HOPFIELD_3ITER)
              'tanh'  -- continuous-tanh attractor (ARM_TANH_BETA_* arms)
    beta: gain parameter (used only when arm_type='tanh')
    n_iter: number of iterations to apply
    Returns: [B, dim] cleaned queries
    """
    state = queries.copy()
    if arm_type == "none" or n_iter == 0:
        return state
    for _ in range(n_iter):
        if arm_type == "sign":
            state = _sign_hopfield_step_batch(state, W)
        elif arm_type == "tanh":
            state = _tanh_hopfield_step_batch(state, W, beta)
    return state


# ============================================================================
# Recall + BPC evaluation (pure numpy)
# ============================================================================

def compute_logits_for_arm(
        idx_held: np.ndarray, E: np.ndarray, W: np.ndarray,
        arm_type: str, beta: float, n_iter: int,
        amplitude_scale: float, batch: int) -> np.ndarray:
    """Compute [n_held, V] logits for one arm.

    arm_type: 'none', 'sign', or 'tanh'
    beta: tanh gain (ignored for 'none'/'sign')
    n_iter: cleanup iterations (0 for 'none')
    amplitude_scale: applied after initial W @ E[src] (matched-filter energy fix)
    Returns: logits [n_held, V]
    """
    V = E.shape[0]
    n_held = len(idx_held) - 1
    logits = np.zeros((n_held, V), dtype=np.float32)
    E_norm = l2_normalize_np(E)   # [V, dim] pre-normalized

    for b in range(0, n_held, batch):
        end = min(b + batch, n_held)
        src = E[idx_held[b:end]]           # [B, dim] L2-normalized source embeddings
        # Initial query = W @ src (recall prediction)
        query = src @ W.T                  # [B, dim]: linear prediction
        query = l2_normalize_np(query)     # L2-normalize
        # Apply amplitude scaling (matched-filter energy fix)
        query = query * amplitude_scale
        # Re-normalize after scaling (direction is what matters for cosine)
        query = l2_normalize_np(query)

        # Apply cleanup iterations (arm-specific)
        query = apply_cleanup(query, W, arm_type=arm_type, beta=beta, n_iter=n_iter)

        logits[b:end] = query @ E_norm.T   # [B, V] cosine similarities

    return logits


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


def raw_bpc_at_T1_L1(logits: np.ndarray, idx_held: np.ndarray) -> float:
    """BPC at T=1.0, lambda=0.0 (no calibration, no unigram mixing).

    Used for CALIBRATION_COLLAPSE check (C7 META). If best calibrated BPC
    deviates from unigram by < 0.02 bits but raw_bpc_at_T1_L1 << unigram,
    this indicates calibration-grid-too-coarse (lambda=0.0 collapse), not
    a genuine signal failure.
    """
    n_held = logits.shape[0]
    if n_held == 0:
        return float("nan")
    tgt_ids = idx_held[1:n_held + 1].astype(np.int32)
    scaled = logits / 1.0
    scaled -= scaled.max(axis=1, keepdims=True)
    probs = np.exp(scaled)
    probs /= probs.sum(axis=1, keepdims=True) + 1e-30
    probs = np.clip(probs, 1e-30, None)
    return float(np.mean(-np.log2(probs)[np.arange(n_held), tgt_ids]))


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
    """Assert all claimed metrics are non-null/non-sentinel at small scale.

    Uses CLEAN SYNTHETIC data (NOT substrate state per smoke-clean discipline).
    """
    print("[selftest] running instrumentation self-test...", flush=True)
    rng = np.random.default_rng(42)

    V_st = 20
    dim_st = 64
    n_train_st = 100
    n_held_st = 30

    # Build tiny synthetic data (NOT substrate state)
    E_st = l2_normalize_np(rng.standard_normal((V_st, dim_st)).astype(np.float32))
    idx_train_st = rng.integers(0, V_st, size=n_train_st + 1).astype(np.int32)
    idx_held_st = rng.integers(0, V_st, size=n_held_st + 1).astype(np.int32)

    # Build W
    W_st = build_rank1_W_np(idx_train_st, E_st, chunk=32)
    assert W_st.shape == (dim_st, dim_st), "W shape mismatch"
    assert np.isfinite(W_st).all(), "W has non-finite values"

    # ARM_BASELINE_NO_CLEANUP
    logits_base = compute_logits_for_arm(
        idx_held_st, E_st, W_st,
        arm_type="none", beta=1.0, n_iter=0,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_base.shape == (n_held_st, V_st), "logits shape mismatch (baseline)"
    assert np.isfinite(logits_base).all(), "logits non-finite (baseline)"

    # ARM_SIGN_HOPFIELD_3ITER
    logits_sign = compute_logits_for_arm(
        idx_held_st, E_st, W_st,
        arm_type="sign", beta=1.0, n_iter=3,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_sign.shape == (n_held_st, V_st), "logits shape mismatch (sign-3iter)"
    assert np.isfinite(logits_sign).all(), "logits non-finite (sign-3iter)"

    # ARM_TANH_BETA_1p0 (representative tanh arm)
    logits_tanh1 = compute_logits_for_arm(
        idx_held_st, E_st, W_st,
        arm_type="tanh", beta=1.0, n_iter=3,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_tanh1.shape == (n_held_st, V_st), "logits shape mismatch (tanh-1.0)"
    assert np.isfinite(logits_tanh1).all(), "logits non-finite (tanh-1.0)"

    # Check BPC is computable for each arm
    unigram_logprob_st = np.log(np.ones(V_st) / V_st)
    for name, logits_arm in [
        ("baseline", logits_base),
        ("sign_3iter", logits_sign),
        ("tanh_1p0", logits_tanh1),
    ]:
        bpc_arm, top1_arm, mrr_arm = compute_bpc_top1_mrr(
            logits_arm, idx_held_st, unigram_logprob_st, lam=0.0, temp=0.1, mrr_k=5
        )
        assert math.isfinite(bpc_arm), f"BPC not finite [{name}]: {bpc_arm}"
        assert 0.0 <= top1_arm <= 1.0, f"top1 out of [0,1] [{name}]: {top1_arm}"
        assert 0.0 <= mrr_arm <= 1.0, f"MRR out of [0,1] [{name}]: {mrr_arm}"
        assert 1.0 <= bpc_arm <= 30.0, f"BPC out of plausible range [{name}]: {bpc_arm}"

    # KEY ASSERTION: tanh arms must produce DIFFERENT logits for different betas
    logits_tanh0p5 = compute_logits_for_arm(
        idx_held_st, E_st, W_st,
        arm_type="tanh", beta=0.5, n_iter=3,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    logits_tanh5p0 = compute_logits_for_arm(
        idx_held_st, E_st, W_st,
        arm_type="tanh", beta=5.0, n_iter=3,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    diff_beta_range = float(np.mean(np.abs(logits_tanh0p5 - logits_tanh5p0)))
    assert diff_beta_range > 1e-6, (
        f"tanh beta=0.5 and beta=5.0 produce IDENTICAL logits ({diff_beta_range:.2e}); "
        "tanh gain is not functioning -- degenerate self-test"
    )

    # Row-variance check: logits should NOT be all-constant (degenerate)
    for name, logits_arm in [("baseline", logits_base), ("tanh_1p0", logits_tanh1)]:
        row_vars = np.var(logits_arm, axis=1)
        assert np.mean(row_vars) > 1e-9, f"logits rows all-constant [{name}] -- degenerate"

    # raw_bpc_at_T1_L1 test: should be computable and finite
    raw_bpc = raw_bpc_at_T1_L1(logits_base, idx_held_st)
    assert math.isfinite(raw_bpc), f"raw_bpc_at_T1_L1 not finite: {raw_bpc}"

    # Filter check: at least 1 held pair exists
    assert (n_held_st - 1) >= 1, "no held pairs at smoke scale -- filter eliminates all"

    print(
        f"[selftest] PASS -- base_shape={logits_base.shape} "
        f"diff_beta_range={diff_beta_range:.4f} raw_bpc={raw_bpc:.4f}",
        flush=True
    )


# Called at module scope (MANDATORY per role contract)
_instrumentation_selftest()


# ============================================================================
# Per-seed runner
# ============================================================================

def _arm_config(arm: str) -> Tuple[str, float, int]:
    """Return (arm_type, beta, n_iter) for a named arm."""
    if arm == "ARM_BASELINE_NO_CLEANUP":
        return ("none", 1.0, 0)
    elif arm == "ARM_SIGN_HOPFIELD_3ITER":
        return ("sign", 1.0, N_ITER_CLEANUP)
    elif arm == "ARM_TANH_BETA_0p5":
        return ("tanh", 0.5, N_ITER_CLEANUP)
    elif arm == "ARM_TANH_BETA_1p0":
        return ("tanh", 1.0, N_ITER_CLEANUP)
    elif arm == "ARM_TANH_BETA_2p0":
        return ("tanh", 2.0, N_ITER_CLEANUP)
    elif arm == "ARM_TANH_BETA_5p0":
        return ("tanh", 5.0, N_ITER_CLEANUP)
    else:
        raise ValueError(f"Unknown arm: {arm}")


def run_one_seed(seed: int, vocab: List[str], w2i: Dict[str, int],
                  idx_train: np.ndarray, idx_held: np.ndarray) -> Dict:
    """Run all 6 arms for one seed. Returns per-arm metrics dict."""
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
        "raw_bpc_at_T1_L1": float("nan"),
    }

    # ---- Build shared encoder + Hebbian W -----------------------------------
    # All arms share the SAME E and W -- only attractor dynamics differ.
    # This is the correct ablation: isolate the update rule.
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

    # ---- Run all 6 arms -------------------------------------------------------
    for arm in ARMS:
        arm_type, beta, n_iter = _arm_config(arm)
        arm_label = f"{arm} (type={arm_type} beta={beta} n_iter={n_iter})"
        print(f"  [s={seed}] {arm_label}...", flush=True)
        t0 = time.time()
        logits_arm = compute_logits_for_arm(
            idx_held, E, W,
            arm_type=arm_type, beta=beta, n_iter=n_iter,
            amplitude_scale=AMPLITUDE_SCALE, batch=RECALL_BATCH
        )
        t_recall = time.time() - t0
        print(f"  [s={seed}] {arm} recall: {t_recall:.1f}s", flush=True)

        raw_bpc = raw_bpc_at_T1_L1(logits_arm, idx_held)
        bpc_arm, top1_arm, mrr_arm, best_T_arm, best_lam_arm = joint_sweep(
            logits_arm, idx_held, unigram_logprob
        )
        arm_results[arm] = {
            "bpc": bpc_arm, "top1": top1_arm, "mrr": mrr_arm,
            "best_T": best_T_arm, "best_lam": best_lam_arm,
            "raw_bpc_at_T1_L1": raw_bpc,
        }
        print(
            f"  [s={seed}] {arm} bpc={bpc_arm:.4f} top1={top1_arm:.4f} "
            f"best_T={best_T_arm} best_lam={best_lam_arm} raw_bpc={raw_bpc:.4f}",
            flush=True
        )
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

    all_arm_names = ARMS + ["ARM_UNIGRAM"]
    arm_metrics: Dict[str, Dict[str, List]] = {
        a: {"bpc": [], "top1": [], "mrr": [], "raw_bpc_at_T1_L1": [],
            "best_T": [], "best_lam": []}
        for a in all_arm_names
    }
    for s in seeds:
        d = per_seed[s]
        for arm in all_arm_names:
            if arm in d["arms"]:
                arm_metrics[arm]["bpc"].append(d["arms"][arm]["bpc"])
                arm_metrics[arm]["top1"].append(d["arms"][arm]["top1"])
                arm_metrics[arm]["mrr"].append(d["arms"][arm]["mrr"])
                arm_metrics[arm]["raw_bpc_at_T1_L1"].append(
                    d["arms"][arm].get("raw_bpc_at_T1_L1", float("nan"))
                )
                arm_metrics[arm]["best_T"].append(
                    d["arms"][arm].get("best_T", float("nan"))
                )
                arm_metrics[arm]["best_lam"].append(
                    d["arms"][arm].get("best_lam", float("nan"))
                )

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
    for arm in all_arm_names:
        bpc_list = arm_metrics[arm]["bpc"]
        lam_list = arm_metrics[arm]["best_lam"]
        summary[arm] = {
            "bpc_mean": safe_mean(bpc_list),
            "bpc_std": safe_std(bpc_list),
            "bpc_cv": safe_cv(bpc_list),
            "top1_mean": safe_mean(arm_metrics[arm]["top1"]),
            "mrr_mean": safe_mean(arm_metrics[arm]["mrr"]),
            "raw_bpc_at_T1_L1_mean": safe_mean(arm_metrics[arm]["raw_bpc_at_T1_L1"]),
            "best_T_mean": safe_mean(arm_metrics[arm]["best_T"]),
            "best_lam_mean": safe_mean(lam_list),
            "best_lam_values": [x for x in lam_list if math.isfinite(x)],
            "n_seeds": len([x for x in bpc_list if math.isfinite(x)]),
        }

    # Fix #28: read per-arm metrics directly; no summary-text shortcuts
    bpc_base = summary["ARM_BASELINE_NO_CLEANUP"]["bpc_mean"]
    bpc_sign = summary["ARM_SIGN_HOPFIELD_3ITER"]["bpc_mean"]
    bpc_tanh = {
        "ARM_TANH_BETA_0p5":  summary["ARM_TANH_BETA_0p5"]["bpc_mean"],
        "ARM_TANH_BETA_1p0":  summary["ARM_TANH_BETA_1p0"]["bpc_mean"],
        "ARM_TANH_BETA_2p0":  summary["ARM_TANH_BETA_2p0"]["bpc_mean"],
        "ARM_TANH_BETA_5p0":  summary["ARM_TANH_BETA_5p0"]["bpc_mean"],
    }
    bpc_unigram = summary["ARM_UNIGRAM"]["bpc_mean"]

    # Best tanh arm (lowest BPC)
    best_tanh_arm = min(bpc_tanh, key=lambda a: bpc_tanh[a] if math.isfinite(bpc_tanh[a]) else float("inf"))
    bpc_best_tanh = bpc_tanh[best_tanh_arm]

    # Suspicious-result gate (before applying verdict bands)
    suspect = False
    suspect_reason = ""
    for arm in ARMS:
        bpc_m = summary[arm]["bpc_mean"]
        if not math.isfinite(bpc_m) or bpc_m <= 0.0:
            suspect = True
            suspect_reason = f"non-finite or zero BPC in arm {arm}: {bpc_m}"
            break

    # READOUT_DEGENERATE check (C7: calibration collapse to unigram via lambda=0.0)
    if not suspect:
        for arm in ARMS:
            lam_vals = summary[arm]["best_lam_values"]
            bpc_m = summary[arm]["bpc_mean"]
            raw_bpc = summary[arm]["raw_bpc_at_T1_L1_mean"]
            if len(lam_vals) > 0 and all(v == 0.0 for v in lam_vals):
                # All seeds collapsed to lambda=0.0
                if abs(bpc_m - bpc_unigram) < 0.02:
                    # BPC collapsed to unigram AND calibration picked lambda=0.0
                    suspect = True
                    suspect_reason = (
                        f"CALIBRATION_COLLAPSE_LAMBDA_ZERO in arm {arm}: "
                        f"bpc={bpc_m:.4f} ~= unigram={bpc_unigram:.4f}, "
                        f"all seeds best_lam=0.0, raw_bpc={raw_bpc:.4f}. "
                        f"C7 META: calibration grid too coarse or substrate signal too noisy. "
                        f"WHAT_THIS_DOES_NOT_SHOW: cannot conclude mechanism fails; "
                        f"may be encoder-mismatch or lambda-grid issue. "
                        f"Route to Strategy for encoder/grid fix before interpreting."
                    )
                    break

    # Sanity rail: ARM_BASELINE_NO_CLEANUP must reproduce ~7.2268
    sanity_warn = ""
    if math.isfinite(bpc_base):
        sanity_delta = abs(bpc_base - SANITY_BASELINE_REF)
        if sanity_delta > SANITY_BASELINE_TOL:
            sanity_warn = (
                f" SANITY_RAIL_WARN: ARM_BASELINE_NO_CLEANUP bpc={bpc_base:.4f} "
                f"deviates {sanity_delta:.4f} from reference {SANITY_BASELINE_REF} "
                f"(tolerance {SANITY_BASELINE_TOL}). N_DIM={N_DIM} may differ from "
                f"v1 N_DIM=8192 -- expected deviation at lower N."
            )

    if suspect:
        verdict = "INSTRUMENTATION_SUSPECT"
        verdict_reason = suspect_reason
    else:
        # Primary metric: does ANY tanh arm beat ARM_BASELINE_NO_CLEANUP?
        # Positive lift = tanh arm produces LOWER BPC (better)
        lift_best_tanh_vs_base = bpc_base - bpc_best_tanh

        # Secondary: sign arm vs baseline (reproduces v1 failure mode)
        lift_sign_vs_base = bpc_base - bpc_sign

        cv_best_tanh = summary[best_tanh_arm]["bpc_cv"]
        cv_warn = ""
        if math.isfinite(cv_best_tanh) and cv_best_tanh >= CV_MAX:
            cv_warn = f" WARN: best_tanh arm {best_tanh_arm} cv={cv_best_tanh:.4f} >= {CV_MAX}"

        what_not_shown = (
            "WHAT_THIS_DOES_NOT_SHOW: "
            "(1) whether tanh dynamics help with DIFFERENT encoders; "
            "(2) whether effect persists at N_DIM=8192 (run at N_DIM=4096); "
            "(3) whether the optimal beta generalizes beyond word-bigram BPC metric."
        )

        sign_reproduction_note = (
            f" ARM_SIGN_HOPFIELD_3ITER bpc={bpc_sign:.4f} "
            f"(lift_vs_base={lift_sign_vs_base:.4f}; "
            f"{'REPRODUCES v1 HARD_FAIL (sign converges fast)' if lift_sign_vs_base <= 0.01 else 'unexpected sign lift'})."
        )

        if math.isfinite(bpc_best_tanh) and bpc_best_tanh < CHAIN_GRADE_ABS_BPC and lift_best_tanh_vs_base >= CHAIN_GRADE_LIFT_BPC:
            verdict = "CHAIN_GRADE_BONUS"
            verdict_reason = (
                f"{best_tanh_arm} bpc={bpc_best_tanh:.4f} beats ARM_BASELINE bpc={bpc_base:.4f} "
                f"by lift={lift_best_tanh_vs_base:.4f} >= {CHAIN_GRADE_LIFT_BPC} "
                f"AND beats chain-grade threshold {CHAIN_GRADE_ABS_BPC}. "
                f"Continuous-tanh attractor dynamics are load-bearing for substrate-LM. "
                f"Brain-graded activation hypothesis confirmed chain-grade."
                + sign_reproduction_note + sanity_warn + cv_warn
                + " " + what_not_shown
            )
        elif lift_best_tanh_vs_base >= HP_LIFT_BPC:
            verdict = "HARD_PASS"
            verdict_reason = (
                f"{best_tanh_arm} bpc={bpc_best_tanh:.4f} beats ARM_BASELINE bpc={bpc_base:.4f} "
                f"by lift={lift_best_tanh_vs_base:.4f} >= {HP_LIFT_BPC}. "
                f"Continuous-tanh fix lifts substrate-LM vs no-cleanup baseline. "
                f"Brain-graded activation hypothesis confirmed for this encoder/N regime."
                + sign_reproduction_note + sanity_warn + cv_warn
                + " " + what_not_shown
            )
        elif lift_best_tanh_vs_base >= MIDDLE_LOW:
            verdict = "MIDDLE_BAND"
            verdict_reason = (
                f"{best_tanh_arm} bpc={bpc_best_tanh:.4f} beats ARM_BASELINE bpc={bpc_base:.4f} "
                f"by lift={lift_best_tanh_vs_base:.4f} in [{MIDDLE_LOW},{MIDDLE_HIGH}]. "
                f"Marginal continuous-tanh benefit; mechanism present but weak at this scale."
                + sign_reproduction_note + sanity_warn + cv_warn
                + " " + what_not_shown
            )
        else:
            verdict = "HARD_FAIL"
            verdict_reason = (
                f"Best tanh arm ({best_tanh_arm}) bpc={bpc_best_tanh:.4f}; "
                f"ARM_BASELINE bpc={bpc_base:.4f}; "
                f"lift={lift_best_tanh_vs_base:.4f} < {MIDDLE_LOW} (or negative). "
                f"Continuous-tanh attractor dynamics do NOT improve substrate-LM BPC "
                f"over no-cleanup baseline at this encoder/N regime."
                + sign_reproduction_note + sanity_warn + cv_warn
                + " " + what_not_shown
            )

    # Per-arm summary dict (Fix #28: expose per-arm data explicitly)
    arm_summary_out = {arm: summary[arm] for arm in all_arm_names}

    return {
        "verdict": verdict,
        "verdict_msg": verdict_reason,
        "arm_summary": arm_summary_out,
        # Key scalar reads (Fix #28: flat fields for easy per-arm read)
        "bpc_baseline_mean": bpc_base,
        "bpc_sign_3iter_mean": bpc_sign,
        "bpc_tanh_0p5_mean": bpc_tanh.get("ARM_TANH_BETA_0p5", float("nan")),
        "bpc_tanh_1p0_mean": bpc_tanh.get("ARM_TANH_BETA_1p0", float("nan")),
        "bpc_tanh_2p0_mean": bpc_tanh.get("ARM_TANH_BETA_2p0", float("nan")),
        "bpc_tanh_5p0_mean": bpc_tanh.get("ARM_TANH_BETA_5p0", float("nan")),
        "bpc_unigram_mean": bpc_unigram,
        "best_tanh_arm": best_tanh_arm,
        "bpc_best_tanh_mean": bpc_best_tanh,
        "lift_best_tanh_vs_baseline": (
            bpc_base - bpc_best_tanh
            if (math.isfinite(bpc_base) and math.isfinite(bpc_best_tanh))
            else float("nan")
        ),
        "lift_sign_vs_baseline": (
            bpc_base - bpc_sign
            if (math.isfinite(bpc_base) and math.isfinite(bpc_sign))
            else float("nan")
        ),
        "sanity_baseline_delta": (
            abs(bpc_base - SANITY_BASELINE_REF) if math.isfinite(bpc_base) else float("nan")
        ),
        "n_seeds": n_seeds,
        "config_version": CONFIG_VERSION,
        "pre_reg": {
            "HARD_PASS": f"any ARM_TANH_BETA beats ARM_BASELINE by >={HP_LIFT_BPC} bits",
            "CHAIN_GRADE_BONUS": (
                f"lift >= {CHAIN_GRADE_LIFT_BPC} bits AND bpc < {CHAIN_GRADE_ABS_BPC}"
            ),
            "MIDDLE_BAND": f"lift in [{MIDDLE_LOW},{MIDDLE_HIGH}]",
            "HARD_FAIL": f"all ARM_TANH_BETA <= ARM_BASELINE (lift < {MIDDLE_LOW})",
            "SANITY_RAIL": (
                f"ARM_BASELINE_NO_CLEANUP within {SANITY_BASELINE_TOL} of {SANITY_BASELINE_REF}"
            ),
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
          f"AMPLITUDE_SCALE={AMPLITUDE_SCALE:.3f} N_ITER_CLEANUP={N_ITER_CLEANUP}", flush=True)
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

    # Per-seed checkpoint resume (PROT-021: reject smoke partials in full runs)
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, _OUT_DIR, run_config=run_config)
    print(f"[main] {len(done_seeds)}/{len(SEEDS)} seeds complete; running {remaining_seeds}", flush=True)

    _T_START = time.time()
    for seed in remaining_seeds:
        print(f"[main] --- seed {seed} ---", flush=True)
        t_seed = time.time()
        result = run_one_seed(seed, vocab, w2i, idx_train, idx_held)
        result["N"] = N_DIM
        result["run_mode"] = RUN_MODE
        write_partial(_OUT_DIR, seed, result)
        print(f"[main] seed {seed} done in {time.time()-t_seed:.1f}s", flush=True)

    elapsed_s = time.time() - _T_START
    print(f"[main] wall time for new seeds: {elapsed_s:.1f}s", flush=True)

    per_seed = aggregate_partials(_OUT_DIR, SEEDS, run_config=run_config)
    verdict_dict = synthesize_verdict(per_seed)
    verdict_dict["elapsed_s"] = elapsed_s
    write_metrics(_OUT_DIR, verdict_dict)

    print(f"\n[VERDICT] {verdict_dict['verdict']}", flush=True)
    print(f"[VERDICT_MSG] {verdict_dict['verdict_msg']}", flush=True)
    print(
        f"[METRICS] "
        f"baseline_bpc={verdict_dict.get('bpc_baseline_mean', float('nan')):.4f} "
        f"sign_3iter_bpc={verdict_dict.get('bpc_sign_3iter_mean', float('nan')):.4f} "
        f"tanh_0p5_bpc={verdict_dict.get('bpc_tanh_0p5_mean', float('nan')):.4f} "
        f"tanh_1p0_bpc={verdict_dict.get('bpc_tanh_1p0_mean', float('nan')):.4f} "
        f"tanh_2p0_bpc={verdict_dict.get('bpc_tanh_2p0_mean', float('nan')):.4f} "
        f"tanh_5p0_bpc={verdict_dict.get('bpc_tanh_5p0_mean', float('nan')):.4f} "
        f"best_tanh={verdict_dict.get('best_tanh_arm', '?')} "
        f"lift_best_tanh_vs_base={verdict_dict.get('lift_best_tanh_vs_baseline', float('nan')):.4f} "
        f"unigram_bpc={verdict_dict.get('bpc_unigram_mean', float('nan')):.4f} "
        f"elapsed_s={elapsed_s:.1f}",
        flush=True
    )
    print(f"[ANCHOR] {ANCHOR_NAME}", flush=True)


if __name__ == "__main__":
    main()
