"""substrate_multi_iter_cleanup_continuous_codebook_LM_v1 -- A2 wrong-closure reverse-or-confirm.

PROVENANCE (2026-06-24):
  v1 (substrate_multi_iteration_cleanup_LM_v1) HARD_FAILed with bpc_1iter == bpc_3iter ==
  bpc_10iter == 7.375 (identical to 4 decimals) -- the sign-based Hopfield update on a
  sign-binarized char-trigram encoder is IDEMPOTENT: sign(W @ sign(...)) = sign(W @ ...)
  reaches a fixed point in 1 step. This was a PRIMITIVE x ENCODER confound, not a clean
  test of multi-iter cleanup.

  Meanwhile modern_hopfield_n_sweep_v1 is chain-grade at N=4096 M/N=0.30 with 100% accuracy
  (CERT row 100): a CONTINUOUS-codebook softmax-based update transfers iterations meaningfully.

  This cell isolates: does multi-iter cleanup transfer to LM regime when the encoder is
  CONTINUOUS (word2vec dense bipolar, L2-normalized, NOT sign-binarized) and the cleanup
  primitive is MODERN-HOPFIELD (softmax over codebook, NOT sign-step)?

A2 INTERPRETATION:
  HARD_PASS  -> v1 wrong-closure REVERSED: multi-iter cleanup DOES transfer to LM when
                encoder + primitive don't trample each other.
  HARD_FAIL  -> v1 wrong-closure CONFIRMED: multi-iter primitive doesn't transfer to
                LM regardless of encoder/primitive combination.

FOUR ARMS (each over text8 N_TRAIN=100k, V=4000, 3 seeds):
  ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED
      char-trigram sign-binarized encoder + sign(W @ q) update; matches v1 prior HARD_FAIL
      setup; sanity rail to verify provenance (expect bpc ~ 7.226 +- 0.05).
  ARM_SINGLE_STEP_CONTINUOUS_CODEBOOK
      word2vec-300d -> N_DIM=8192 Gaussian-projected L2-normalized codebook; modern-Hopfield
      softmax 1-step cleanup. New baseline for continuous-codebook regime.
  ARM_MULTI_ITER_3_CONTINUOUS_CODEBOOK
      Same encoder/codebook; 3 iterations of modern-Hopfield softmax cleanup.
  ARM_MULTI_ITER_10_CONTINUOUS_CODEBOOK
      Same encoder/codebook; 10 iterations of modern-Hopfield softmax cleanup.

PRIMITIVE (continuous-codebook modern-Hopfield, vectorized over batch):
  Iteration k: s_{k+1} = softmax(beta * (s_k @ codebook.T)) @ codebook
               s_{k+1} = l2_normalize(s_{k+1})   # for cosine-comparison consistency
  No sign() -- continuous-valued state stays in the codebook span; iterations actually
  evolve the trajectory (unlike v1's sign-step which idempotent-collapses).
  beta = MH_BETA = 8.0 (matches modern_hopfield_n_sweep_v1 reference).

PRE-REGISTERED BANDS (BEFORE RUN -- DO NOT ADJUST after seeing data):
  Sanity rail:
      ARM_BASELINE within +-0.05 of v1 reference (bpc ~ 7.226). If sanity-rail
      mismatch > 0.05, the cell is FLAGGED as PROVENANCE_DRIFT (not a verdict).

  HARD_PASS:
      ARM_MULTI_ITER_3_CONTINUOUS bpc <= ARM_SINGLE_STEP_CONTINUOUS bpc - 0.05
      AND cv_3 <= 0.05
      (multi-iter HELPS by >= 0.05 bits on continuous codebook -- reverses v1 wrong-closure)

  MIDDLE_BAND:
      ARM_MULTI_ITER_3_CONTINUOUS bpc improves by 0.02 to 0.05 over ARM_SINGLE_STEP_CONTINUOUS
      (partial reversal; not chain-grade)

  HARD_FAIL:
      ARM_MULTI_ITER_3_CONTINUOUS bpc >= ARM_SINGLE_STEP_CONTINUOUS bpc + 0.02
      (multi-iter HURTS or no-effect; v1 wrong-closure CONFIRMED at primitive level)

CRITICAL DISCIPLINES:
  - PROT-018: anchor has no _nN suffix; production N_DIM=8192 stated below + in prereg
  - Fix #14: ONE cell
  - Fix #17: smoke runtime measured + timeout estimated from it
  - Fix #28: per-arm metrics read independently; no cross-arm narrative
  - Fix #26: predispatch_check confirmed no prior landings (PROCEED 2026-06-24)
  - ASCII-only; no torch import (pure numpy + gensim); remote_cpu route
  - atexit synthesizer; per-seed checkpoint; signal handlers

CITES:
  - Ramsauer 2020 (modern Hopfield exponential energy via softmax)
  - Treves-Rolls 1991 (CA3 attractor convergence)
  - data/exp_modern_hopfield_n_sweep_v1/metrics.json (chain-grade primitive ref)
  - data/exp_substrate_multi_iteration_cleanup_LM_v1/metrics.json (HARD_FAIL v1 ref)
  - experiments/exp_encoder_word2vec_substrate_bind_v1.py (gensim w2v loader pattern)
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
    get_output_dir, aggregate_partials, write_metrics,
    resumable_seeds, write_partial,
)

ANCHOR_NAME = "substrate_multi_iter_cleanup_continuous_codebook_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only audit gate (no LLM forward calls anywhere on inference path)
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Pre-reg bands (from spec; DO NOT adjust after data)
# ============================================================================

HP_LIFT_BPC = 0.05            # ARM_MULTI_ITER_3 beats ARM_SINGLE_STEP by >= 0.05 bits
MIDDLE_LOW = 0.02             # MIDDLE_BAND lower bound (also HARD_FAIL upper threshold)
MIDDLE_HIGH = 0.05            # MIDDLE_BAND upper bound (= HP threshold)
HF_NEGATIVE_LIFT = -0.02      # ARM_MULTI_ITER_3 worse than ARM_SINGLE_STEP by >= 0.02 -> HF
CV_MAX = 0.05                 # coefficient of variation ceiling
SANITY_RAIL_REF = 7.226       # v1 ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED reference
SANITY_RAIL_TOL = 0.05        # tolerance for provenance check

# Modern-Hopfield update beta (matches modern_hopfield_n_sweep_v1 reference)
MH_BETA = 8.0

# Joint (T, lambda) calibration sweep (matches fair_harness / v1 grids)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Sparse-receiver amplitude scaling for sign-binarized arm (matches v1)
SPARSITY_F = 0.05
AMPLITUDE_SCALE = 1.0 / math.sqrt(SPARSITY_F)  # ~= 4.47

# ============================================================================
# CLI + run-mode
# ============================================================================

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = (
    "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
    else os.environ.get("HDLAB_RUN_MODE", "full")
)

# ============================================================================
# Config (smoke vs full)
# ============================================================================

VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 512
PRETRAIN_DIM = 300            # word2vec native dim
W2V_MODEL = "word2vec-google-news-300"

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke: tiny scale, fast (<120s on CPU including w2v load)
    SEEDS = [0]
    N_DIM = 512
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

ARMS = [
    "ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED",
    "ARM_SINGLE_STEP_CONTINUOUS_CODEBOOK",
    "ARM_MULTI_ITER_3_CONTINUOUS_CODEBOOK",
    "ARM_MULTI_ITER_10_CONTINUOUS_CODEBOOK",
]

CONFIG_VERSION = (
    "%s; N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s mode=%s "
    "beta=%.1f sparsity_f=%.3f amp_scale=%.3f w2v_model=%s "
    "bands HP>=%.3f mid=[%.3f,%.3f] HF<=%.3f cv_max=%.3f sanity_rail=%.3f+-%.3f"
) % (
    ANCHOR_NAME, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    MH_BETA, SPARSITY_F, AMPLITUDE_SCALE, W2V_MODEL,
    HP_LIFT_BPC, MIDDLE_LOW, MIDDLE_HIGH, HF_NEGATIVE_LIFT, CV_MAX,
    SANITY_RAIL_REF, SANITY_RAIL_TOL,
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
    cnt = Counter(tokens)
    vocab = [w for w, _ in cnt.most_common(cap)]
    return vocab, {w: i for i, w in enumerate(vocab)}


def tokens_to_ids(tokens: List[str], w2i: Dict[str, int]) -> np.ndarray:
    return np.array([w2i.get(t, 0) for t in tokens], dtype=np.int32)


# ============================================================================
# Sign-binarized char-trigram encoder (sanity-rail ARM only)
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv_np(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode_signed(word: str, n_dim: int, seed: int) -> np.ndarray:
    """SIGN-binarized char-trigram (matches v1 ARM_BASELINE encoder; sanity-rail)."""
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


def build_E_signed_trigram(vocab: List[str], n_dim: int, seed: int) -> np.ndarray:
    """[V, n_dim] L2-normalized sign-binarized trigram embeddings (sanity-rail)."""
    E = np.stack([char_trigram_encode_signed(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    norms = np.linalg.norm(E, axis=1, keepdims=True)
    norms = np.where(norms < 1e-12, 1.0, norms)
    return E / norms


# ============================================================================
# Continuous word2vec encoder (3 modern-Hopfield ARMs)
# ============================================================================

_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_kv(model_name: str):
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    import gensim.downloader as gd
    try:
        gd.base_dir = GENSIM_CACHE_DIR
        gd.BASE_DIR = GENSIM_CACHE_DIR
    except Exception:
        pass
    kv = gd.load(model_name)
    _GENSIM_KV_CACHE[model_name] = kv
    return kv


def _embed_vocab_via_gensim(vocab: List[str], kv) -> Tuple[np.ndarray, int, int]:
    dim = kv.vector_size
    V = len(vocab)
    out = np.zeros((V, dim), dtype=np.float32)
    n_hit = 0
    n_miss = 0
    for i, w in enumerate(vocab):
        v = None
        if w in kv.key_to_index:
            v = kv[w]
        elif w.lower() in kv.key_to_index:
            v = kv[w.lower()]
        else:
            try:
                v = kv.get_vector(w, norm=False)
            except Exception:
                v = None
        if v is None:
            n_miss += 1
        else:
            n_hit += 1
            out[i] = v.astype(np.float32)
    return out, n_hit, n_miss


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    return rng.standard_normal((out_dim, in_dim)).astype(np.float32) / math.sqrt(float(in_dim))


def build_E_continuous_w2v(vocab: List[str], n_dim: int, seed: int) -> Tuple[np.ndarray, Dict]:
    """[V, n_dim] L2-normalized word2vec embeddings, Gaussian-projected to n_dim.
    OOV words use sign-binarized char-trigram as fallback (so smoke recall@1 sigma=0 works).
    Returns (E, info_dict)."""
    kv = _load_gensim_kv(W2V_MODEL)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    norms_before = np.linalg.norm(E_pre, axis=1)
    E_pre_n = E_pre / np.where(norms_before[:, None] < 1e-12, 1.0, norms_before[:, None])
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)  # [V, n_dim]
    # OOV fallback: char-trigram for rows where original was zero-vector
    oov_mask = norms_before < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode_signed(vocab[i], n_dim, seed)
    # L2-normalize final
    norms = np.linalg.norm(E_proj, axis=1, keepdims=True)
    norms = np.where(norms < 1e-12, 1.0, norms)
    E_proj = E_proj / norms
    info = {
        "n_hit": int(n_hit), "n_miss": int(n_miss),
        "n_vocab": int(len(vocab)),
        "n_oov_fallback_trigram": int(oov_mask.sum()),
        "pretrain_dim": int(kv.vector_size),
        "w2v_model": W2V_MODEL,
    }
    return E_proj, info


def l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        n = np.linalg.norm(X)
        return X / max(n, eps)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(norms < eps, 1.0, norms)


# ============================================================================
# Hebbian W builder (same as v1; pure numpy chunked outer-product)
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
        src = E[idx_train[b:end]]
        tgt = E[idx_train[b + 1:end + 1]]
        W += tgt.T @ src
    return W


# ============================================================================
# Cleanup primitives
# ============================================================================

def _softmax_rowwise(x: np.ndarray) -> np.ndarray:
    x = x - x.max(axis=1, keepdims=True)
    e = np.exp(x)
    return e / (e.sum(axis=1, keepdims=True) + 1e-30)


def _modern_hopfield_step_batch(states: np.ndarray, codebook: np.ndarray, beta: float) -> np.ndarray:
    """One MODERN-Hopfield update step: s_{k+1} = softmax(beta * s @ codebook.T) @ codebook.

    CONTINUOUS-valued state (no sign). states: [B, dim]; codebook: [V, dim].
    L2-normalize after for cosine-comparison consistency.
    Returns: [B, dim].
    """
    scores = states @ codebook.T              # [B, V]
    weights = _softmax_rowwise(beta * scores) # [B, V]
    updated = weights @ codebook              # [B, dim]
    return l2_normalize_np(updated)


def _sign_hopfield_step_batch(states: np.ndarray, W: np.ndarray) -> np.ndarray:
    """SIGN-based Hopfield update (sanity-rail arm; matches v1)."""
    updated = states @ W.T
    updated = np.sign(updated)
    updated[updated == 0] = 1.0
    return l2_normalize_np(updated)


def apply_continuous_cleanup(queries: np.ndarray, codebook: np.ndarray,
                              n_iter: int, beta: float) -> Tuple[np.ndarray, float]:
    """Apply n_iter modern-Hopfield (softmax) iterations on continuous codebook."""
    state = queries.copy()
    for _ in range(n_iter):
        state = _modern_hopfield_step_batch(state, codebook, beta)
    return state, float(n_iter)


def apply_sign_cleanup(queries: np.ndarray, W: np.ndarray,
                       n_iter: int) -> Tuple[np.ndarray, float]:
    """Apply n_iter sign-based iterations (sanity-rail; n_iter=0 -> no cleanup)."""
    state = queries.copy()
    for _ in range(n_iter):
        state = _sign_hopfield_step_batch(state, W)
    return state, float(n_iter)


# ============================================================================
# Recall + BPC eval
# ============================================================================

def compute_logits_sign_arm(
        idx_held: np.ndarray, E_signed: np.ndarray, W: np.ndarray,
        n_iter: int, amplitude_scale: float, batch: int) -> Tuple[np.ndarray, float]:
    """SIGN-binarized arm: linear W @ src then sign-based cleanup, return logits vs E_signed."""
    V = E_signed.shape[0]
    n_held = len(idx_held) - 1
    logits = np.zeros((n_held, V), dtype=np.float32)
    E_norm = l2_normalize_np(E_signed)
    total_iters = 0.0
    n_batches = 0
    for b in range(0, n_held, batch):
        end = min(b + batch, n_held)
        src = E_signed[idx_held[b:end]]
        query = src @ W.T
        query = l2_normalize_np(query)
        query = query * amplitude_scale
        query = l2_normalize_np(query)
        if n_iter > 0:
            query, mi = apply_sign_cleanup(query, W, n_iter)
            total_iters += mi
            n_batches += 1
        logits[b:end] = query @ E_norm.T
    mean_iters = (total_iters / n_batches) if n_batches > 0 else float(n_iter)
    return logits, mean_iters


def compute_logits_continuous_arm(
        idx_held: np.ndarray, E_cont: np.ndarray, W: np.ndarray,
        n_iter: int, beta: float, batch: int) -> Tuple[np.ndarray, float]:
    """CONTINUOUS-codebook arm: W @ src then modern-Hopfield softmax cleanup on E_cont codebook."""
    V = E_cont.shape[0]
    n_held = len(idx_held) - 1
    logits = np.zeros((n_held, V), dtype=np.float32)
    E_norm = l2_normalize_np(E_cont)
    total_iters = 0.0
    n_batches = 0
    for b in range(0, n_held, batch):
        end = min(b + batch, n_held)
        src = E_cont[idx_held[b:end]]
        query = src @ W.T
        query = l2_normalize_np(query)
        if n_iter > 0:
            query, mi = apply_continuous_cleanup(query, E_norm, n_iter, beta)
            total_iters += mi
            n_batches += 1
        logits[b:end] = query @ E_norm.T
    mean_iters = (total_iters / n_batches) if n_batches > 0 else float(n_iter)
    return logits, mean_iters


def compute_bpc_top1_mrr(logits: np.ndarray, idx_held: np.ndarray,
                          unigram_logprob: np.ndarray,
                          lam: float, temp: float, mrr_k: int) -> Tuple[float, float, float]:
    n_held = logits.shape[0]
    if n_held == 0:
        return float("nan"), float("nan"), float("nan")
    tgt_ids = idx_held[1:n_held + 1].astype(np.int32)
    scaled = logits / max(temp, 1e-9)
    scaled = scaled - scaled.max(axis=1, keepdims=True)
    probs_sub = np.exp(scaled)
    probs_sub = probs_sub / (probs_sub.sum(axis=1, keepdims=True) + 1e-30)
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
            bpc_dev, _, _ = compute_bpc_top1_mrr(dev_logits, dev_idx, unigram_logprob, lam, T, MRR_K)
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
    """Tiny synthetic data; asserts primitives + BPC machinery work end-to-end."""
    print("[selftest] running instrumentation self-test...", flush=True)
    rng = np.random.default_rng(42)

    V_st = 20
    dim_st = 64
    n_train_st = 100
    n_held_st = 30

    # Continuous-style synthetic codebook (NOT sign-binarized)
    E_cont_st = l2_normalize_np(rng.standard_normal((V_st, dim_st)).astype(np.float32))
    # Signed-style synthetic codebook
    E_sign_st = l2_normalize_np(np.sign(rng.standard_normal((V_st, dim_st)).astype(np.float32)))

    idx_train_st = rng.integers(0, V_st, size=n_train_st + 1).astype(np.int32)
    idx_held_st = rng.integers(0, V_st, size=n_held_st + 1).astype(np.int32)

    W_cont_st = build_rank1_W_np(idx_train_st, E_cont_st, chunk=32)
    W_sign_st = build_rank1_W_np(idx_train_st, E_sign_st, chunk=32)
    assert W_cont_st.shape == (dim_st, dim_st), "W shape"
    assert np.isfinite(W_cont_st).all(), "W finite"
    assert np.isfinite(W_sign_st).all(), "W_sign finite"

    # Sign-arm: n_iter=0
    logits_sign, _ = compute_logits_sign_arm(
        idx_held_st, E_sign_st, W_sign_st, n_iter=0,
        amplitude_scale=AMPLITUDE_SCALE, batch=16
    )
    assert logits_sign.shape == (n_held_st, V_st)
    assert np.isfinite(logits_sign).all()

    # Continuous-arm: n_iter=1
    logits_c1, it_c1 = compute_logits_continuous_arm(
        idx_held_st, E_cont_st, W_cont_st, n_iter=1, beta=MH_BETA, batch=16
    )
    assert logits_c1.shape == (n_held_st, V_st)
    assert np.isfinite(logits_c1).all()
    assert it_c1 == 1.0

    # Continuous-arm: n_iter=3 (trajectory should differ from n_iter=1)
    logits_c3, it_c3 = compute_logits_continuous_arm(
        idx_held_st, E_cont_st, W_cont_st, n_iter=3, beta=MH_BETA, batch=16
    )
    assert logits_c3.shape == (n_held_st, V_st)
    assert np.isfinite(logits_c3).all()
    assert it_c3 == 3.0

    # Continuous-arm: n_iter=10
    logits_c10, it_c10 = compute_logits_continuous_arm(
        idx_held_st, E_cont_st, W_cont_st, n_iter=10, beta=MH_BETA, batch=16
    )
    assert it_c10 == 10.0
    assert np.isfinite(logits_c10).all()

    # CORE INSTRUMENTATION CHECK (the v1 wart): on continuous codebook + softmax cleanup,
    # 1-iter vs 3-iter must produce MEASURABLY DIFFERENT logits (the trajectory evolves).
    # On sign-binarized, the sign-step is idempotent; on continuous codebook, it shouldn't be.
    diff_c1_vs_c3 = float(np.mean(np.abs(logits_c1 - logits_c3)))
    assert diff_c1_vs_c3 > 1e-5, (
        "CRITICAL: continuous-codebook softmax cleanup 1-iter vs 3-iter logits are "
        "identical -- the v1 wart reproduces. Primitive choice failed."
    )
    print("[selftest] continuous trajectory ok: |c1-c3|=%.6f" % diff_c1_vs_c3, flush=True)

    # BPC sanity
    unigram_logprob_st = np.log(np.ones(V_st) / V_st)
    for name, lg in [("sign", logits_sign), ("c1", logits_c1),
                     ("c3", logits_c3), ("c10", logits_c10)]:
        bpc, top1, mrr = compute_bpc_top1_mrr(
            lg, idx_held_st, unigram_logprob_st, lam=0.0, temp=0.1, mrr_k=5
        )
        assert math.isfinite(bpc), "BPC not finite [%s]: %s" % (name, bpc)
        assert 0.0 <= top1 <= 1.0
        assert 0.0 <= mrr <= 1.0
        assert 0.5 <= bpc <= 30.0, "BPC out of plausible range [%s]: %s" % (name, bpc)

    # LLM-call counter MUST be zero
    assert _LLM_CALL_COUNTER[0] == 0, "LLM_CALL violation in selftest"

    print("[selftest] PASS", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_one_seed(seed: int, vocab: List[str], w2i: Dict[str, int],
                  idx_train: np.ndarray, idx_held: np.ndarray) -> Dict:
    V = len(vocab)

    # Unigram reference (Laplace-smoothed)
    freq = np.zeros(V, dtype=np.float32)
    for idx in idx_train:
        freq[idx] += 1.0
    freq += 1.0
    freq /= freq.sum()
    unigram_logprob = np.log(freq)

    arm_results: Dict[str, Dict] = {}

    # Unigram floor
    n_held = len(idx_held) - 1
    tgt_ids = idx_held[1:n_held + 1].astype(np.int32)
    bpc_unigram = float(np.mean(-unigram_logprob[tgt_ids] / math.log(2.0)))
    arm_results["ARM_UNIGRAM"] = {
        "bpc": bpc_unigram, "top1": float("nan"), "mrr": float("nan"),
        "best_T": float("nan"), "best_lam": float("nan"),
        "mean_iters": float("nan"),
    }

    # ----- SANITY RAIL: sign-binarized char-trigram encoder + sign(W @ q) (no cleanup) -----
    print("  [s=%d] building E_signed_trigram [V=%d, N_DIM=%d]..." % (seed, V, N_DIM), flush=True)
    t0 = time.time()
    E_signed = build_E_signed_trigram(vocab, N_DIM, seed)
    print("  [s=%d] E_signed built %.1fs" % (seed, time.time() - t0), flush=True)

    print("  [s=%d] building W_signed Hebbian [%dx%d]..." % (seed, N_DIM, N_DIM), flush=True)
    t0 = time.time()
    W_signed = build_rank1_W_np(idx_train, E_signed, INGEST_CHUNK)
    print("  [s=%d] W_signed built %.1fs" % (seed, time.time() - t0), flush=True)

    print("  [s=%d] ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED..." % seed, flush=True)
    t0 = time.time()
    logits_sb, it_sb = compute_logits_sign_arm(
        idx_held, E_signed, W_signed, n_iter=0,
        amplitude_scale=AMPLITUDE_SCALE, batch=RECALL_BATCH
    )
    print("  [s=%d] sign-baseline recall: %.1fs" % (seed, time.time() - t0), flush=True)
    bpc_sb, top1_sb, mrr_sb, bestT_sb, bestL_sb = joint_sweep(logits_sb, idx_held, unigram_logprob)
    arm_results["ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED"] = {
        "bpc": bpc_sb, "top1": top1_sb, "mrr": mrr_sb,
        "best_T": bestT_sb, "best_lam": bestL_sb,
        "mean_iters": it_sb,
    }
    print("  [s=%d] ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED bpc=%.4f top1=%.4f"
          % (seed, bpc_sb, top1_sb), flush=True)
    del logits_sb, W_signed, E_signed

    # ----- CONTINUOUS ARMS: word2vec L2-normalized + modern-Hopfield softmax cleanup -----
    print("  [s=%d] building E_continuous_w2v [V=%d, N_DIM=%d]..." % (seed, V, N_DIM), flush=True)
    t0 = time.time()
    E_cont, w2v_info = build_E_continuous_w2v(vocab, N_DIM, seed)
    print("  [s=%d] E_cont built %.1fs (n_hit=%d n_miss=%d)"
          % (seed, time.time() - t0, w2v_info["n_hit"], w2v_info["n_miss"]), flush=True)

    print("  [s=%d] building W_continuous Hebbian [%dx%d]..." % (seed, N_DIM, N_DIM), flush=True)
    t0 = time.time()
    W_cont = build_rank1_W_np(idx_train, E_cont, INGEST_CHUNK)
    print("  [s=%d] W_continuous built %.1fs" % (seed, time.time() - t0), flush=True)

    # ARM_SINGLE_STEP_CONTINUOUS_CODEBOOK
    print("  [s=%d] ARM_SINGLE_STEP_CONTINUOUS_CODEBOOK..." % seed, flush=True)
    t0 = time.time()
    logits_c1, it_c1 = compute_logits_continuous_arm(
        idx_held, E_cont, W_cont, n_iter=1, beta=MH_BETA, batch=RECALL_BATCH
    )
    print("  [s=%d] cont-1iter recall: %.1fs" % (seed, time.time() - t0), flush=True)
    bpc_c1, top1_c1, mrr_c1, bestT_c1, bestL_c1 = joint_sweep(logits_c1, idx_held, unigram_logprob)
    arm_results["ARM_SINGLE_STEP_CONTINUOUS_CODEBOOK"] = {
        "bpc": bpc_c1, "top1": top1_c1, "mrr": mrr_c1,
        "best_T": bestT_c1, "best_lam": bestL_c1,
        "mean_iters": it_c1,
    }
    print("  [s=%d] ARM_SINGLE_STEP_CONTINUOUS_CODEBOOK bpc=%.4f top1=%.4f"
          % (seed, bpc_c1, top1_c1), flush=True)
    del logits_c1

    # ARM_MULTI_ITER_3_CONTINUOUS_CODEBOOK
    print("  [s=%d] ARM_MULTI_ITER_3_CONTINUOUS_CODEBOOK..." % seed, flush=True)
    t0 = time.time()
    logits_c3, it_c3 = compute_logits_continuous_arm(
        idx_held, E_cont, W_cont, n_iter=3, beta=MH_BETA, batch=RECALL_BATCH
    )
    print("  [s=%d] cont-3iter recall: %.1fs" % (seed, time.time() - t0), flush=True)
    bpc_c3, top1_c3, mrr_c3, bestT_c3, bestL_c3 = joint_sweep(logits_c3, idx_held, unigram_logprob)
    arm_results["ARM_MULTI_ITER_3_CONTINUOUS_CODEBOOK"] = {
        "bpc": bpc_c3, "top1": top1_c3, "mrr": mrr_c3,
        "best_T": bestT_c3, "best_lam": bestL_c3,
        "mean_iters": it_c3,
    }
    print("  [s=%d] ARM_MULTI_ITER_3_CONTINUOUS_CODEBOOK bpc=%.4f top1=%.4f"
          % (seed, bpc_c3, top1_c3), flush=True)
    del logits_c3

    # ARM_MULTI_ITER_10_CONTINUOUS_CODEBOOK
    print("  [s=%d] ARM_MULTI_ITER_10_CONTINUOUS_CODEBOOK..." % seed, flush=True)
    t0 = time.time()
    logits_c10, it_c10 = compute_logits_continuous_arm(
        idx_held, E_cont, W_cont, n_iter=10, beta=MH_BETA, batch=RECALL_BATCH
    )
    print("  [s=%d] cont-10iter recall: %.1fs" % (seed, time.time() - t0), flush=True)
    bpc_c10, top1_c10, mrr_c10, bestT_c10, bestL_c10 = joint_sweep(logits_c10, idx_held, unigram_logprob)
    arm_results["ARM_MULTI_ITER_10_CONTINUOUS_CODEBOOK"] = {
        "bpc": bpc_c10, "top1": top1_c10, "mrr": mrr_c10,
        "best_T": bestT_c10, "best_lam": bestL_c10,
        "mean_iters": it_c10,
    }
    print("  [s=%d] ARM_MULTI_ITER_10_CONTINUOUS_CODEBOOK bpc=%.4f top1=%.4f"
          % (seed, bpc_c10, top1_c10), flush=True)
    del logits_c10, W_cont, E_cont

    return {
        "seed": seed,
        "arms": arm_results,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "w2v_info": w2v_info,
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
    }


# ============================================================================
# Verdict
# ============================================================================

def synthesize_verdict(per_seed: Dict) -> Dict:
    seeds = sorted(per_seed.keys(), key=int)
    n_seeds = len(seeds)
    if n_seeds == 0:
        return {"verdict": "NO_RESULTS",
                "verdict_msg": "no seeds completed",
                "elapsed_s": 0.0,
                "summary": "no_results"}

    arm_metrics: Dict[str, Dict[str, List]] = {
        a: {"bpc": [], "top1": [], "mrr": [], "mean_iters": []}
        for a in ARMS + ["ARM_UNIGRAM"]
    }
    for s in seeds:
        d = per_seed[s]
        for arm in (ARMS + ["ARM_UNIGRAM"]):
            if arm in d.get("arms", {}):
                arm_metrics[arm]["bpc"].append(d["arms"][arm]["bpc"])
                arm_metrics[arm]["top1"].append(d["arms"][arm].get("top1", float("nan")))
                arm_metrics[arm]["mrr"].append(d["arms"][arm].get("mrr", float("nan")))
                arm_metrics[arm]["mean_iters"].append(
                    d["arms"][arm].get("mean_iters", float("nan")))

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

    # Read per-arm metrics independently (Fix #28)
    bpc_sb = summary["ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED"]["bpc_mean"]
    bpc_c1 = summary["ARM_SINGLE_STEP_CONTINUOUS_CODEBOOK"]["bpc_mean"]
    bpc_c3 = summary["ARM_MULTI_ITER_3_CONTINUOUS_CODEBOOK"]["bpc_mean"]
    bpc_c10 = summary["ARM_MULTI_ITER_10_CONTINUOUS_CODEBOOK"]["bpc_mean"]
    cv_c3 = summary["ARM_MULTI_ITER_3_CONTINUOUS_CODEBOOK"]["bpc_cv"]

    # Sanity rail check (does NOT alter verdict band; reported as provenance flag)
    sanity_rail_ok = (math.isfinite(bpc_sb)
                      and abs(bpc_sb - SANITY_RAIL_REF) <= SANITY_RAIL_TOL)

    # Suspect gate
    suspect = False
    for arm in ARMS:
        bpc_m = summary[arm]["bpc_mean"]
        if not math.isfinite(bpc_m) or bpc_m <= 0.0:
            suspect = True
            break

    what_not_shown = (
        "WHAT_THIS_DOES_NOT_SHOW: "
        "(1) whether multi-iter cleanup helps with OTHER continuous encoders (GloVe / fastText); "
        "(2) whether beta=%.1f is optimal; "
        "(3) whether result generalizes beyond word-bigram BPC at V=%d / N_DIM=%d; "
        "(4) the sanity-rail ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED is REPRODUCTION-of-v1, "
        "not a test of multi-iter (its n_iter=0; included only as provenance check)."
    ) % (MH_BETA, VOCAB_CAP, N_DIM)

    if suspect:
        verdict = "INSTRUMENTATION_SUSPECT"
        verdict_msg = (
            "non-finite, zero, or absent BPC in >= 1 arm. "
            "Route back to Strategy for harness repair before interpreting. "
            + what_not_shown
        )
    else:
        # Primary metric: lift of ARM_MULTI_ITER_3 over ARM_SINGLE_STEP (lower BPC = better)
        # Positive lift = multi-iter produces LOWER bpc
        lift_3_vs_1 = bpc_c1 - bpc_c3
        lift_10_vs_1 = bpc_c1 - bpc_c10

        cv_warn = ""
        if math.isfinite(cv_c3) and cv_c3 > CV_MAX:
            cv_warn = " WARN: ARM_MULTI_ITER_3 cv=%.4f > %.3f." % (cv_c3, CV_MAX)

        sanity_warn = ""
        if not sanity_rail_ok:
            sanity_warn = (
                " PROVENANCE_FLAG: sanity-rail ARM_BASELINE_NO_CLEANUP_SIGN_BINARIZED "
                "bpc=%.4f deviates from v1 reference %.3f by > %.3f (drift outside "
                "tolerance; treat reversal/confirmation with caution)."
            ) % (bpc_sb, SANITY_RAIL_REF, SANITY_RAIL_TOL)

        if lift_3_vs_1 >= HP_LIFT_BPC and (math.isnan(cv_c3) or cv_c3 <= CV_MAX):
            verdict = "HARD_PASS"
            verdict_msg = (
                "ARM_MULTI_ITER_3_CONTINUOUS bpc=%.4f beats ARM_SINGLE_STEP_CONTINUOUS "
                "bpc=%.4f by lift=%.4f >= %.3f. v1 HARD_FAIL wrong-closure REVERSED: "
                "multi-iter cleanup DOES transfer to LM regime on continuous codebook "
                "with modern-Hopfield primitive. lift_10_vs_1=%.4f bpc_sign_rail=%.4f "
                "(v1 ref %.3f).%s%s %s"
            ) % (bpc_c3, bpc_c1, lift_3_vs_1, HP_LIFT_BPC, lift_10_vs_1,
                 bpc_sb, SANITY_RAIL_REF, cv_warn, sanity_warn, what_not_shown)
        elif lift_3_vs_1 >= MIDDLE_LOW:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                "ARM_MULTI_ITER_3_CONTINUOUS bpc=%.4f beats ARM_SINGLE_STEP_CONTINUOUS "
                "bpc=%.4f by lift=%.4f in [%.3f, %.3f). Partial reversal of v1 "
                "wrong-closure: multi-iter helps marginally on continuous codebook but "
                "not at HARD_PASS threshold. lift_10_vs_1=%.4f bpc_sign_rail=%.4f.%s%s %s"
            ) % (bpc_c3, bpc_c1, lift_3_vs_1, MIDDLE_LOW, MIDDLE_HIGH, lift_10_vs_1,
                 bpc_sb, cv_warn, sanity_warn, what_not_shown)
        else:
            verdict = "HARD_FAIL"
            verdict_msg = (
                "ARM_MULTI_ITER_3_CONTINUOUS bpc=%.4f vs ARM_SINGLE_STEP_CONTINUOUS "
                "bpc=%.4f; lift=%.4f < %.3f. v1 wrong-closure CONFIRMED at primitive "
                "level: multi-iter cleanup does NOT transfer to LM regime even on "
                "continuous codebook with modern-Hopfield primitive. The Tier-3 "
                "multi-iter-cleanup hypothesis remains rejected for LM tasks. "
                "lift_10_vs_1=%.4f bpc_sign_rail=%.4f (v1 ref %.3f).%s%s %s"
            ) % (bpc_c3, bpc_c1, lift_3_vs_1, MIDDLE_LOW, lift_10_vs_1, bpc_sb,
                 SANITY_RAIL_REF, cv_warn, sanity_warn, what_not_shown)

    return {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg[:300],
        "run_mode": RUN_MODE,
        "n_seeds": n_seeds,
        "arm_summary": summary,
        "lift_3iter_vs_1iter_bpc": (bpc_c1 - bpc_c3
                                    if (math.isfinite(bpc_c1) and math.isfinite(bpc_c3))
                                    else float("nan")),
        "lift_10iter_vs_1iter_bpc": (bpc_c1 - bpc_c10
                                     if (math.isfinite(bpc_c1) and math.isfinite(bpc_c10))
                                     else float("nan")),
        "bpc_sign_rail_mean": bpc_sb,
        "bpc_continuous_1iter_mean": bpc_c1,
        "bpc_continuous_3iter_mean": bpc_c3,
        "bpc_continuous_10iter_mean": bpc_c10,
        "sanity_rail_ok": bool(sanity_rail_ok),
        "sanity_rail_ref": SANITY_RAIL_REF,
        "sanity_rail_tolerance": SANITY_RAIL_TOL,
        "unigram_bpc_mean": summary["ARM_UNIGRAM"]["bpc_mean"],
        "config_version": CONFIG_VERSION,
        "pre_reg": {
            "HARD_PASS": "ARM_MULTI_ITER_3 beats ARM_SINGLE_STEP by >= %.3f bits AND cv <= %.3f"
                        % (HP_LIFT_BPC, CV_MAX),
            "MIDDLE_BAND": "lift in [%.3f, %.3f)" % (MIDDLE_LOW, MIDDLE_HIGH),
            "HARD_FAIL": "lift < %.3f" % MIDDLE_LOW,
            "SANITY_RAIL": "ARM_BASELINE within +-%.3f of v1 ref %.3f"
                          % (SANITY_RAIL_TOL, SANITY_RAIL_REF),
        },
    }


# ============================================================================
# Main + atexit synthesizer
# ============================================================================

_OUT_DIR: Optional[Path] = None
_T_WALL_START: float = 0.0


def _atexit_synthesizer():
    """Write partial metrics.json on any exit (crash recovery)."""
    if _OUT_DIR is None:
        return
    partials = list(_OUT_DIR.glob("partial_metrics_*.json"))
    if not partials:
        return
    try:
        per_seed_raw = aggregate_partials(_OUT_DIR, SEEDS)
        if per_seed_raw:
            verdict_dict = synthesize_verdict(per_seed_raw)
            verdict_dict["elapsed_s"] = float(time.time() - _T_WALL_START) if _T_WALL_START else 0.0
            write_metrics(_OUT_DIR, verdict_dict)
            print("[atexit] wrote partial metrics.json verdict=%s" % verdict_dict["verdict"],
                  flush=True)
    except Exception as exc:
        print("[atexit] ERROR: %s" % exc, flush=True)


atexit.register(_atexit_synthesizer)


def _signal_handler(sig, frame):
    print("[signal] caught %s; atexit will synthesize" % sig, flush=True)
    sys.exit(1)


signal.signal(signal.SIGTERM, _signal_handler)
try:
    signal.signal(signal.SIGINT, _signal_handler)
except Exception:
    pass


def main():
    global _OUT_DIR, _T_WALL_START

    _OUT_DIR = get_output_dir(ANCHOR_NAME)
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    _T_WALL_START = time.time()
    print("[main] output dir: %s" % _OUT_DIR, flush=True)
    print("[main] RUN_MODE=%s N_DIM=%d SPARSITY_F=%.3f AMPLITUDE_SCALE=%.3f MH_BETA=%.1f"
          % (RUN_MODE, N_DIM, SPARSITY_F, AMPLITUDE_SCALE, MH_BETA), flush=True)
    print("[main] SEEDS=%s N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d W2V_MODEL=%s"
          % (SEEDS, N_TRAIN, N_HELD, VOCAB_CAP, W2V_MODEL), flush=True)
    print("[main] CONFIG=%s" % CONFIG_VERSION, flush=True)

    # Load corpus
    print("[main] loading text8...", flush=True)
    t0 = time.time()
    tokens = load_text8_tokens(TEXT8, N_TRAIN + N_HELD + 1000)
    vocab, w2i = build_vocab(tokens[:N_TRAIN], VOCAB_CAP)
    V = len(vocab)
    print("[main] vocab size=%d corpus_tokens=%d (%.1fs)"
          % (V, len(tokens), time.time() - t0), flush=True)

    all_ids = tokens_to_ids(tokens, w2i)
    idx_train = all_ids[:N_TRAIN]
    idx_held = all_ids[N_TRAIN:N_TRAIN + N_HELD + 1]

    # Per-seed checkpoint resume
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, _OUT_DIR, run_config=run_config)
    print("[main] %d/%d seeds complete; running %s"
          % (len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

    for seed in remaining_seeds:
        print("[main] --- seed %d ---" % seed, flush=True)
        t_seed = time.time()
        result = run_one_seed(seed, vocab, w2i, idx_train, idx_held)
        result["N"] = N_DIM
        result["run_mode"] = RUN_MODE
        write_partial(_OUT_DIR, seed, result)
        print("[main] seed %d done in %.1fs" % (seed, time.time() - t_seed), flush=True)

    t_total = time.time() - _T_WALL_START
    print("[main] wall time: %.1fs" % t_total, flush=True)

    per_seed = aggregate_partials(_OUT_DIR, SEEDS, run_config=run_config)
    verdict_dict = synthesize_verdict(per_seed)
    verdict_dict["elapsed_s"] = float(t_total)
    write_metrics(_OUT_DIR, verdict_dict)

    print("\n[VERDICT] %s" % verdict_dict["verdict"], flush=True)
    print("[VERDICT_MSG] %s" % verdict_dict["verdict_msg"], flush=True)
    bpc_sb = verdict_dict.get("bpc_sign_rail_mean", float("nan"))
    bpc_c1 = verdict_dict.get("bpc_continuous_1iter_mean", float("nan"))
    bpc_c3 = verdict_dict.get("bpc_continuous_3iter_mean", float("nan"))
    bpc_c10 = verdict_dict.get("bpc_continuous_10iter_mean", float("nan"))
    lift_3_1 = verdict_dict.get("lift_3iter_vs_1iter_bpc", float("nan"))
    lift_10_1 = verdict_dict.get("lift_10iter_vs_1iter_bpc", float("nan"))
    print("[METRICS] sign_rail=%.4f c1=%.4f c3=%.4f c10=%.4f lift_3vs1=%.4f lift_10vs1=%.4f unigram=%.4f"
          % (bpc_sb, bpc_c1, bpc_c3, bpc_c10, lift_3_1, lift_10_1,
             verdict_dict.get("unigram_bpc_mean", float("nan"))), flush=True)
    print("[ANCHOR] %s" % ANCHOR_NAME, flush=True)


if __name__ == "__main__":
    main()
