"""substrate_sequence_modeling_production_v1 -- production sequence-modeling harness.

USER directive 2026-06-24: "sequence modelling - I think we could get very good
here too." Substrate has c3 sequence-binding chain-grade (atom 586) + g1b auto-
regressive generation chain-grade (atom 587), but has NEVER been scaled to a
production word-level LM harness with a real-LM baseline comparison.

HONEST RE-CAST (Step 0):
  Task brief mentioned char-bigram BPC ~6.5, but the established LM harness in
  this repo (fair_harness_substrate_as_lm_v1) operates on text8 at WORD level
  (UNIGRAM_BPC_REF=7.738 word-BPC; landed substrate fair_harness 7.31 word-BPC).
  The honest comparable real-LM baseline at word-level is the ADD-ALPHA SMOOTHED
  WORD-BIGRAM (a real n-gram LM that beats unigram with order info). USER intent
  ("substrate beats a real-LM baseline at sequence modeling") is preserved at
  the word level so apples-to-apples with the established harness.

QUESTION:
  Does adding the c3 sequence-binding primitive (S matrix that Hebbian-binds
  HRR-position-tagged last-K word keys to next-word) lift substrate-as-LM from
  the context-free rank-1 W floor (~7.31 word-BPC) to clear word-bigram (a real
  LM baseline)? Does adding cf-RPE online delta-rule learning further close the
  gap?

ARMS (5; all share same encoder + same eval split for apples-to-apples):
  ARM_UNIGRAM
      Analytic word-unigram floor (alpha-smoothed). Reference; ~7.74 word-BPC.
  ARM_WORD_BIGRAM
      Add-alpha smoothed word-bigram LM. Real-LM baseline; should beat unigram.
      Approximated via row-conditional bigram count table; alpha=0.1.
  ARM_CONTEXT_FREE_SUBSTRATE
      word2vec-projected encoder + rank-1 Hebbian W; matches fair_harness
      ARM_SUBSTRATE_WORD2VEC_DENSE. Sanity rail: bpc_best within +/-0.10 of 7.31.
  ARM_SEQUENCE_BIND_K8
      c3 SequenceMatrix S over last K=8 words: each step writes
      outer(E[w_t], k_ctx_t) where k_ctx_t = sum_{i=1..K} HRR(E[w_{t-i}], P_i).
      Predict: pred_t = S @ k_ctx_t; logits_t = pred_t @ E.T.
  ARM_SEQUENCE_BIND_K16_CFRPE
      K=16 + cf-RPE: during eval, after observing true w_t, apply
      S += eta * (E[w_t] - S @ k_ctx_t) @ k_ctx_t.T  (delta-rule online update).

Shared eval: same joint (T, lambda) sweep on dev half, BPC + top-1 + MRR@10
reported per arm on test half. lambda interp is against unigram (same as
fair_harness convention; honest substrate-only-decode gate -- bigram is NOT
mixed into the substrate arms; bigram is its own arm).

PRE-REG HARD BANDS (cell-author 2026-06-24; word-level on text8):

  Sanity rail (smoke gate + full):
    ARM_CONTEXT_FREE_SUBSTRATE bpc_best within +/-0.10 of fair_harness landed
    7.3065 (i.e. [7.21, 7.41]); deviation = harness mis-spec.

  ARM_WORD_BIGRAM calibration:
    Expected bpc_best in [6.30, 6.90] word-BPC (real LM beats unigram by
    ~1-1.4 bits at this scale; literature: kneser-ney bigram on text8 word-level
    is ~6.0 bits, but add-alpha smoothing is weaker so 6.3-6.9 expected).
    If bpc_word_bigram > 7.40 -> baseline broken (harness mis-spec).

  HARD_PASS (substrate sequence-modeling clears real-LM baseline):
    ARM_SEQUENCE_BIND_K16_CFRPE bpc_best mean across seeds
        <= ARM_WORD_BIGRAM bpc_best mean - 0.10
    AND cv across seeds <= 0.05
    AND zero_llm_calls_at_inference == True
    AND ARM_CONTEXT_FREE_SUBSTRATE sanity rail satisfied
    AND ARM_WORD_BIGRAM calibration satisfied

  CHAIN_GRADE_BONUS:
    ARM_SEQUENCE_BIND_K16_CFRPE bpc_best mean
        <= ARM_WORD_BIGRAM bpc_best mean - 0.30
    (substrate sequence-modeling DECISIVELY beats word-bigram)

  MIDDLE_BAND:
    ARM_SEQUENCE_BIND_K16_CFRPE bpc_best mean in
        (ARM_WORD_BIGRAM bpc_best mean, ARM_WORD_BIGRAM bpc_best mean - 0.10]
    (i.e. substrate seq-bind beats word-bigram by <0.10 bits) OR
    ARM_SEQUENCE_BIND_K8 beats word-bigram but K16+cfRPE does not.

  HARD_FAIL:
    ARM_SEQUENCE_BIND_K16_CFRPE bpc_best mean > ARM_WORD_BIGRAM bpc_best mean
    (sequence-binding + cf-RPE does NOT beat word-bigram on word-level LM)
    OR substrate-only-decode gate violated (n_llm_calls > 0)
    OR sanity rail violated.

  DISCRIMINATING REGIME:
    The 5-arm contrast IS the discriminator. If all substrate arms collapse to
    each other within 0.05 bits, sequence-binding mechanism is NULL (honest
    negative). If ARM_SEQUENCE_BIND_K16_CFRPE clears word-bigram, the mechanism
    is the load-bearing factor.

FORMULA SELF-TESTS:
  T1: word-bigram add-alpha smoothing -- on V=5 toy, P(w|prev) sums to 1.0.
  T2: HRR bind: irfft(rfft(A) * rfft(B)) yields shape-matching vector;
      binding is associative-ish (norm-preserving in expectation).
  T3: SequenceMatrix bind_pair -> predict_next round-trip: after bind_pair(a,b),
      predict_next(a) has higher cosine to b than to a random vector.
  T4: cf-RPE delta-rule shrinks error: after one update, |true - pred|_2
      decreases by >= 0.0 (assert non-increase under positive eta).
  T5: K=8 context vector: roll-and-bind produces a non-zero contextual key
      (norm > 0); zero-context fallback handled.
  T6: bpc_from_logp on planted logp -- exact unigram BPC reproduced at lambda=0.
  T7: verdict bands: HARD_PASS / MIDDLE / HARD_FAIL classification on planted
      arm-data (subset, focused on word-bigram comparison logic).
  T8: _LLM_CALL_COUNTER remains 0 throughout.

ASCII-only. CPU. Single file. Resumable via _seed_checkpoint. atexit synthesize.
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
import signal
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_sequence_modeling_production_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only-decode gate (Skunkworks structural blocker)
_LLM_CALL_COUNTER = [0]

# Reference baselines (word-level text8)
UNIGRAM_BPC_REF = 7.738
SUBSTRATE_CONTEXT_FREE_REF = 7.3065  # fair_harness landed (word-level rank-1 W)

# Pre-reg bands
HP_DELTA_VS_BIGRAM = 0.10       # K16+cfRPE must beat word-bigram by >= 0.10 bits
CG_DELTA_VS_BIGRAM = 0.30       # chain-grade bonus delta
SANITY_RAIL_TOL = 0.10           # CONTEXT_FREE within +/-0.10 of 7.3065
BIGRAM_BPC_MIN = 6.30
BIGRAM_BPC_MAX = 6.90
BIGRAM_BPC_HARD_CAP = 7.40       # above this -> baseline broken
HP_CV_MAX = 0.05

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Joint (T, lambda) sweep (mirrors fair_harness; lambda interp vs unigram)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Sequence-binding context windows
K_SHORT = 8
K_LONG = 16
LOCK_IN_FREQ_STEP = 31
CFRPE_ETA = 0.05                 # cf-RPE online learning rate (delta-rule)
BIGRAM_ALPHA = 0.1               # add-alpha smoothing

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 40_000
    N_HELD = 8_000
    VOCAB_CAP = 4000
    N_DIM = 8192
    PRETRAIN_DIM = 300
    INGEST_CHUNK = 2048
else:
    # Smoke: must finish under 180s on laptop CPU
    SEEDS = [0]
    N_TRAIN = 1_500
    N_HELD = 300
    VOCAB_CAP = 200
    N_DIM = 256
    PRETRAIN_DIM = 64  # used only by w2v fallback to char-trigram in smoke
    INGEST_CHUNK = 512

ARMS = [
    "ARM_UNIGRAM",
    "ARM_WORD_BIGRAM",
    "ARM_CONTEXT_FREE_SUBSTRATE",
    "ARM_SEQUENCE_BIND_K8",
    "ARM_SEQUENCE_BIND_K16_CFRPE",
]
SUBSTRATE_ARMS = [
    "ARM_CONTEXT_FREE_SUBSTRATE",
    "ARM_SEQUENCE_BIND_K8",
    "ARM_SEQUENCE_BIND_K16_CFRPE",
]
WORD2VEC_MODEL = "word2vec-google-news-300"

CONFIG_VERSION = (
    "substrate_sequence_modeling_production_v1; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s K_short=%d K_long=%d cfrpe_eta=%.3f "
    "alpha=%.2f temps=%s lambdas=%s MRR_K=%d "
    "hp_delta_vs_bigram>=%.2f cg_delta>=%.2f sanity_tol=%.2f cv_max=%.2f "
    "bigram_min=%.2f bigram_max=%.2f bigram_hardcap=%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE, K_SHORT, K_LONG,
    CFRPE_ETA, BIGRAM_ALPHA, TEMP_GRID, LAMBDA_GRID, MRR_K,
    HP_DELTA_VS_BIGRAM, CG_DELTA_VS_BIGRAM, SANITY_RAIL_TOL, HP_CV_MAX,
    BIGRAM_BPC_MIN, BIGRAM_BPC_MAX, BIGRAM_BPC_HARD_CAP,
)


# ============================================================================
# Encoder (numpy-only; CPU)
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
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


def _l2_normalize(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    return rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))


# Gensim cache
_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_kv(model_name: str):
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    from tools.gensim_load_helper import load_gensim_kv
    kv = load_gensim_kv(model_name, cache_dir=GENSIM_CACHE_DIR)
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


def build_encoder(vocab: List[str], n_dim: int, seed: int) -> Tuple[np.ndarray, Dict]:
    """word2vec projection + char-trigram OOV fallback. CPU; returns float32 [V, n_dim].

    In smoke (or if gensim load fails) falls back entirely to char-trigram.
    """
    try:
        kv = _load_gensim_kv(WORD2VEC_MODEL)
        E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
        E_pre_n = _l2_normalize(E_pre)
        P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
        E_proj = (E_pre_n @ P.T).astype(np.float32)
        oov_mask = np.linalg.norm(E_pre, axis=1) < 1e-9
        if oov_mask.any():
            for i in np.where(oov_mask)[0]:
                E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
        E_proj = _l2_normalize(E_proj)
        meta = {"encoder": "word2vec_proj", "n_hit": int(n_hit), "n_miss": int(n_miss),
                "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
        return E_proj, meta
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
        E_np = _l2_normalize(E_np)
        return E_np, {"encoder": "char_trigram_fallback", "load_error": err,
                        "n_vocab": int(len(vocab))}


# ============================================================================
# HRR bind + lock-in position vectors (numpy)
# ============================================================================

def hrr_bind(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    """Circular convolution via FFT. A, B shape [..., n_dim] -> same shape."""
    Fa = np.fft.rfft(A, axis=-1)
    Fb = np.fft.rfft(B, axis=-1)
    out = np.fft.irfft(Fa * Fb, n=A.shape[-1], axis=-1)
    return out.astype(np.float32)


def lock_in_position_vec(n_dim: int, pos: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 7919 + 13 + pos * 101)
    phase = rng.uniform(0.0, 2.0 * math.pi, size=n_dim).astype(np.float32)
    freq = float(max(pos, 1) * LOCK_IN_FREQ_STEP) / float(n_dim)
    t = np.arange(n_dim, dtype=np.float32)
    v = np.cos(2.0 * math.pi * freq * t + phase).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-12)
    return v


def build_context_keys(idx: np.ndarray, E: np.ndarray, K: int, seed: int) -> np.ndarray:
    """For each position p, return k_ctx_p = sum_{i=1..K} HRR(E[idx[p-i]], P_i).

    Positions where p-i < 0 use E[idx[0]] (defensive padding; same as
    fair_harness convention via torch.roll).
    Output: [N, n_dim] L2-normalized.
    """
    n = idx.shape[0]
    dim = E.shape[1]
    keys = np.zeros((n, dim), dtype=np.float32)
    pos_vecs = [lock_in_position_vec(dim, i, seed) for i in range(K + 1)]
    for offset in range(1, K + 1):
        # source index at position p-offset; clamp at 0
        shifted = np.maximum(np.arange(n) - offset, 0)
        src = E[idx[shifted]]
        pos_b = np.broadcast_to(pos_vecs[offset], src.shape).copy()
        bound = hrr_bind(src, pos_b)
        keys += bound
    keys = _l2_normalize(keys)
    return keys


# ============================================================================
# Hebbian W builders
# ============================================================================

def build_rank1_W(idx_train: np.ndarray, E: np.ndarray, ingest_chunk: int) -> np.ndarray:
    """W = sum outer(E[idx[t+1]], E[idx[t]]); rank-1 Hebbian. Context-free."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        E_src = E[idx_train[b:end]]
        E_tgt = E[idx_train[b + 1:end + 1]]
        W += E_tgt.T @ E_src
    return W


def build_sequence_S(idx_train: np.ndarray, E: np.ndarray, K: int, seed: int,
                       ingest_chunk: int) -> Tuple[np.ndarray, np.ndarray]:
    """c3-style SequenceMatrix: S = sum_t outer(E[idx_train[t]], k_ctx_t).

    k_ctx_t is the K-tap HRR-position-bound context vector ending at t-1.
    Returns (S, k_ctx_train) for diagnostic + reuse.
    """
    dim = E.shape[1]
    n = idx_train.shape[0]
    if n <= K + 1:
        return np.zeros((dim, dim), dtype=np.float32), np.zeros((n, dim), dtype=np.float32)
    k_ctx_train = build_context_keys(idx_train, E, K, seed)
    S = np.zeros((dim, dim), dtype=np.float32)
    # bind pair (k_ctx_t, E[idx_train[t]]) -- predicts E[w_t] given context
    # context at position t looks back over previous K; target = E[w_t]
    # iterate t in [K, n)
    for b in range(K, n, ingest_chunk):
        end = min(b + ingest_chunk, n)
        kc = k_ctx_train[b:end]
        tgt = E[idx_train[b:end]]
        S += tgt.T @ kc
    return S, k_ctx_train


# ============================================================================
# Word-bigram add-alpha LM
# ============================================================================

def build_word_bigram(idx_train: np.ndarray, V: int, alpha: float) -> np.ndarray:
    """Add-alpha smoothed word-bigram conditional table.

    Returns P[prev, next] of shape [V, V] -- row-normalized conditional.
    Memory: V=4000 -> 16M floats * 4B = 64MB. OK for CPU.
    """
    counts = np.full((V, V), alpha, dtype=np.float64)
    if idx_train.shape[0] >= 2:
        prev = idx_train[:-1]
        nxt = idx_train[1:]
        np.add.at(counts, (prev, nxt), 1.0)
    counts /= counts.sum(axis=1, keepdims=True)
    return counts.astype(np.float32)


def word_bigram_metrics(P_bigram: np.ndarray, idx_held: np.ndarray, V: int,
                         mrr_k: int) -> Dict:
    """Compute BPC + top-1 + MRR@K under add-alpha smoothed word-bigram."""
    if idx_held.shape[0] < 2:
        return {"bpc_best": float("inf"), "top1_acc": 0.0, "mrr_at_10": 0.0,
                "best_T_for_bpc": 1.0, "best_lambda_for_bpc": 1.0,
                "raw_bpc_at_T1_L1": float("inf"), "n_test": 0}
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    # match other arms' eval-split logic for apples-to-apples
    unk = 0
    mask = (ctx != unk)
    ctx_eval = ctx[mask]
    nxt_eval = nxt[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        return {"bpc_best": float("inf"), "top1_acc": 0.0, "mrr_at_10": 0.0,
                "best_T_for_bpc": 1.0, "best_lambda_for_bpc": 1.0,
                "raw_bpc_at_T1_L1": float("inf"), "n_test": 0}
    n_dev = n_eval // 2
    nxt_test = nxt_eval[n_dev:]
    ctx_test = ctx_eval[n_dev:]
    p_test = P_bigram[ctx_test, nxt_test].clip(1e-12, 1.0)
    bpc = float(-np.mean(np.log(p_test)) / math.log(2.0))
    # top-1: argmax over conditional row
    pred = np.argmax(P_bigram[ctx_test], axis=1)
    top1 = float(np.mean(pred == nxt_test))
    # MRR@K
    rows = P_bigram[ctx_test]
    k_use = min(mrr_k, V)
    top_idx = np.argpartition(-rows, kth=k_use - 1, axis=1)[:, :k_use]
    row_arange = np.arange(len(ctx_test))[:, None]
    top_vals = rows[row_arange, top_idx]
    order = np.argsort(-top_vals, axis=1)
    top_idx_sorted = top_idx[row_arange, order]
    rr = 0.0
    for i in range(len(ctx_test)):
        m = np.where(top_idx_sorted[i] == nxt_test[i])[0]
        if len(m) > 0:
            rr += 1.0 / float(m[0] + 1)
    mrr = float(rr / len(ctx_test))
    return {"bpc_best": round(bpc, 4), "top1_acc": round(top1, 4),
            "mrr_at_10": round(mrr, 4), "best_T_for_bpc": 1.0,
            "best_lambda_for_bpc": 1.0, "raw_bpc_at_T1_L1": round(bpc, 4),
            "n_test": int(len(nxt_test))}


# ============================================================================
# text8 loader (mirrors fair_harness)
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
# Joint (T, lambda) sweep + 3 metrics (numpy; mirrors fair_harness)
# ============================================================================

def softmax_logits_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp_logp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float
                             ) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    logp_nxt = logp[np.arange(n), nxt]
    return -float(np.mean(logp_nxt)) / math.log(2.0)


def top1_acc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    if len(nxt) == 0:
        return float("nan")
    pred = np.argmax(logp, axis=1)
    return float(np.mean(pred == nxt))


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


def joint_sweep_substrate(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                            U_log: np.ndarray, nxt_dev: np.ndarray,
                            nxt_test: np.ndarray, temps: List[float],
                            lambdas: List[float], mrr_k: int) -> Dict:
    """Joint sweep + 3 metrics; mirrors fair_harness convention."""
    logp_T1 = log_linear_interp_logp(np.log(softmax_logits_with_T(sub_logits_test, 1.0)),
                                       U_log, 1.0)
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)
    raw_top1_at_T1_L1 = top1_acc_from_logp(logp_T1, nxt_test)
    raw_mrr_at_T1_L1 = mrr_at_k(logp_T1, nxt_test, mrr_k)

    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    grid = {}
    for T in temps:
        sub_probs_dev = softmax_logits_with_T(sub_logits_dev, T)
        sub_logp_dev = np.log(np.clip(sub_probs_dev, 1e-30, 1.0))
        for lam in lambdas:
            logp_dev = log_linear_interp_logp(sub_logp_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc_from_logp(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
            key = "T%.3f_L%.2f" % (T, lam)
            grid[key] = {"bpc_dev": round(bd, 4), "top1_dev": round(td, 4),
                          "mrr_dev": round(md, 4)}
            if bd < best_bpc["dev_value"]:
                best_bpc = {"T": float(T), "lambda": float(lam), "dev_value": bd}
            if td > best_top1["dev_value"]:
                best_top1 = {"T": float(T), "lambda": float(lam), "dev_value": td}
            if md > best_mrr["dev_value"]:
                best_mrr = {"T": float(T), "lambda": float(lam), "dev_value": md}

    def _test_metric(T: float, lam: float, fn) -> float:
        sub_probs_test = softmax_logits_with_T(sub_logits_test, T)
        sub_logp_test = np.log(np.clip(sub_probs_test, 1e-30, 1.0))
        logp_test = log_linear_interp_logp(sub_logp_test, U_log, lam)
        if fn == bpc_from_logp:
            return fn(logp_test, nxt_test)
        if fn == top1_acc_from_logp:
            return fn(logp_test, nxt_test)
        return mrr_at_k(logp_test, nxt_test, mrr_k)

    bpc_best_test = _test_metric(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _test_metric(best_top1["T"], best_top1["lambda"], top1_acc_from_logp)
    mrr_best_test = _test_metric(best_mrr["T"], best_mrr["lambda"], mrr_at_k)

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
        "raw_bpc_at_T1_L1": round(raw_bpc_at_T1_L1, 4),
        "raw_top1_at_T1_L1": round(raw_top1_at_T1_L1, 4),
        "raw_mrr_at_T1_L1": round(raw_mrr_at_T1_L1, 4),
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
        "grid_size": int(len(grid)),
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray, V: int,
                      mrr_k: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != 0)
    nxt_eval = nxt[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        return {"bpc_best": float("inf"), "top1_acc": 0.0, "mrr_at_10": 0.0,
                "best_T_for_bpc": 1.0, "best_lambda_for_bpc": 0.0,
                "raw_bpc_at_T1_L1": float("inf"), "n_test": 0}
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
    rr = np.where(ranks <= mrr_k, 1.0 / ranks, 0.0)
    mrr = float(np.mean(rr))
    return {"bpc_best": round(bpc, 4), "top1_acc": round(top1, 4),
            "mrr_at_10": round(mrr, 4), "best_T_for_bpc": 1.0,
            "best_lambda_for_bpc": 0.0, "raw_bpc_at_T1_L1": round(bpc, 4),
            "n_test": int(len(nxt_test))}


# ============================================================================
# Per-arm logits builder (substrate arms)
# ============================================================================

def compute_substrate_arm_logits(arm_label: str, E: np.ndarray,
                                    idx_train: np.ndarray, idx_held: np.ndarray,
                                    seed: int) -> Dict:
    """Returns logits over the FULL held set (cos similarity to vocab E)."""
    V, dim = E.shape
    t0 = time.time()
    if arm_label == "ARM_CONTEXT_FREE_SUBSTRATE":
        W = build_rank1_W(idx_train, E, INGEST_CHUNK)
        src_keys_held = E[idx_held]
        pred_held = src_keys_held @ W.T
        pred_held = _l2_normalize(pred_held)
        del W
    elif arm_label == "ARM_SEQUENCE_BIND_K8":
        S, _ = build_sequence_S(idx_train, E, K_SHORT, seed, INGEST_CHUNK)
        k_ctx_held = build_context_keys(idx_held, E, K_SHORT, seed)
        pred_held = k_ctx_held @ S.T
        pred_held = _l2_normalize(pred_held)
        del S, k_ctx_held
    elif arm_label == "ARM_SEQUENCE_BIND_K16_CFRPE":
        S, _ = build_sequence_S(idx_train, E, K_LONG, seed, INGEST_CHUNK)
        k_ctx_held = build_context_keys(idx_held, E, K_LONG, seed)
        # cf-RPE online delta-rule: predict, observe, update S.
        # During eval: for each t in held, predict using current S; AFTER scoring,
        # apply delta = E[true_w_t] - pred; S += eta * outer(delta, k_ctx_t).
        # IMPORTANT: prediction at position t uses S BEFORE the t-th update
        # (no test-set leakage into the t-th prediction).
        n_h = idx_held.shape[0]
        pred_held = np.zeros((n_h, dim), dtype=np.float32)
        for t in range(n_h):
            k = k_ctx_held[t]
            p = S @ k
            p_n = p / (np.linalg.norm(p) + 1e-12)
            pred_held[t] = p_n
            # delta-rule update using ground truth at t (online; cf-RPE
            # mirrors heterogeneous-plasticity drill; eta small)
            tgt = E[idx_held[t]]
            delta = tgt - p_n
            S += CFRPE_ETA * np.outer(delta, k)
        del S, k_ctx_held
    else:
        raise ValueError("unknown substrate arm: %s" % arm_label)
    t_compute = time.time() - t0
    # logits = pred_held @ E.T
    logits = (pred_held @ E.T).astype(np.float32)
    return {"logits": logits, "wall_compute_s": round(t_compute, 2),
            "arm_label": arm_label}


# ============================================================================
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading text8 + building vocab" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[WARN] corpus short: %d vs %d" % (len(toks), N_TRAIN + N_HELD), flush=True)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d" % (
        seed, V, N_TRAIN, N_HELD, N_DIM), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    # ARM_UNIGRAM
    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_best"], uni["top1_acc"], uni["mrr_at_10"], uni["n_test"]),
        flush=True)
    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # ARM_WORD_BIGRAM
    t_bg0 = time.time()
    P_bigram = build_word_bigram(idx_train, V, BIGRAM_ALPHA)
    bg = word_bigram_metrics(P_bigram, idx_held, V, MRR_K)
    bg["wall_build_s"] = round(time.time() - t_bg0, 2)
    by_arm["ARM_WORD_BIGRAM"] = bg
    del P_bigram
    print("[seed=%d arm=ARM_WORD_BIGRAM] bpc=%.3f top1=%.4f mrr=%.4f (build=%.1fs)" % (
        seed, bg["bpc_best"], bg["top1_acc"], bg["mrr_at_10"], bg["wall_build_s"]),
        flush=True)

    # Build encoder once; reuse across substrate arms (apples-to-apples)
    print("\n[seed=%d] building encoder (V=%d, N_DIM=%d)..." % (seed, V, N_DIM),
          flush=True)
    t_enc0 = time.time()
    E_base, encoder_meta = build_encoder(vocab, N_DIM, seed)
    t_enc = time.time() - t_enc0
    print("[seed=%d encoder=%s] E built (%.1fs); shape=%s" % (
        seed, encoder_meta.get("encoder", "?"), t_enc, E_base.shape), flush=True)

    # Substrate arms (all share E; each builds its own W or S)
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != 0)
    nxt_eval = nxt_full[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        for arm in SUBSTRATE_ARMS:
            by_arm[arm] = {"empty_eval": True, "bpc_best": float("inf"),
                            "top1_acc": float("nan"), "mrr_at_10": float("nan")}
        return {"seed": seed, "by_arm": by_arm, "V": V, "N_DIM": N_DIM,
                 "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
                 "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
                 "elapsed_s_seed": round(time.time() - t_seed, 2),
                 "encoder_meta": encoder_meta, "n_llm_calls": 0}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]
    valid_pos = np.where(mask)[0]

    for arm in SUBSTRATE_ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building logits..." % (seed, arm), flush=True)
        try:
            ar = compute_substrate_arm_logits(arm, E_base, idx_train, idx_held, seed)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {"compute_failed": True, "compute_error": err,
                            "bpc_best": float("inf"), "top1_acc": float("nan"),
                            "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
                            "best_lambda_for_bpc": float("nan"),
                            "raw_bpc_at_T1_L1": float("inf"),
                            "elapsed_s_arm": round(time.time() - t_arm0, 2)}
            continue
        logits_full = ar["logits"]  # [n_held, V]
        # logits at position p predicts NEXT token given context-up-to-p.
        # That's idx_held[p+1] = nxt_full[p]. Use positions p < len(ctx_full).
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            logits_ctx = logits_full
        # Apply mask + split
        if len(logits_ctx) == len(ctx_full):
            logits_eval = logits_ctx[mask]
        else:
            mask_pos = np.array([p for p in valid_pos if p < logits_ctx.shape[0]],
                                  dtype=np.int64)
            logits_eval = logits_ctx[mask_pos]
            nxt_eval_local = nxt_full[mask_pos]
            ne = len(nxt_eval_local)
            ndev = ne // 2
            nxt_dev_l = nxt_eval_local[:ndev]
            nxt_test_l = nxt_eval_local[ndev:]
            jr = joint_sweep_substrate(logits_eval[:ndev], logits_eval[ndev:],
                                        U_log, nxt_dev_l, nxt_test_l,
                                        TEMP_GRID, LAMBDA_GRID, MRR_K)
            jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
            jr["wall_compute_s"] = ar["wall_compute_s"]
            by_arm[arm] = jr
            print("    [seed=%d arm=%s] bpc=%.3f top1=%.4f mrr=%.4f rawT1L1=%.3f" % (
                seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                jr["raw_bpc_at_T1_L1"]), flush=True)
            continue
        jr = joint_sweep_substrate(logits_eval[:n_dev], logits_eval[n_dev:],
                                    U_log, nxt_dev, nxt_test,
                                    TEMP_GRID, LAMBDA_GRID, MRR_K)
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["wall_compute_s"] = ar["wall_compute_s"]
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc=%.3f top1=%.4f mrr=%.4f rawT1L1=%.3f" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
            jr["raw_bpc_at_T1_L1"]), flush=True)

    del E_base
    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "encoder_meta": encoder_meta,
        "n_llm_calls": 0,
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Aggregate per-arm bpc_best across seeds
    by_arm_agg = {}
    for arm in ARMS:
        bpcs = []
        top1s = []
        mrrs = []
        for u in units:
            a = u["by_arm"].get(arm, {})
            b = a.get("bpc_best", float("inf"))
            t1 = a.get("top1_acc", float("nan"))
            mr = a.get("mrr_at_10", float("nan"))
            if isinstance(b, float) and math.isfinite(b):
                bpcs.append(b)
                top1s.append(t1)
                mrrs.append(mr)
        if not bpcs:
            by_arm_agg[arm] = {"all_seeds_failed": True}
            continue
        by_arm_agg[arm] = {
            "bpc_best_mean": round(float(np.mean(bpcs)), 4),
            "bpc_best_std": round(float(np.std(bpcs)), 4),
            "bpc_best_cv": round(float(np.std(bpcs) / max(abs(np.mean(bpcs)), 1e-9)), 4),
            "top1_mean": round(float(np.mean(top1s)), 4),
            "mrr_mean": round(float(np.mean(mrrs)), 4),
            "n_seeds": len(bpcs),
        }

    # Substrate-only-decode gate
    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    # Sanity rail: CONTEXT_FREE within +/- SANITY_RAIL_TOL of SUBSTRATE_CONTEXT_FREE_REF.
    # Reference is FULL-mode V=4000 word-level landed (fair_harness 7.3065). Smoke
    # runs at V=200 -> different vocab-entropy floor -> sanity rail is FULL-MODE ONLY.
    is_full_mode = (units and units[0].get("run_mode", "full") == "full"
                     and units[0].get("VOCAB_CAP", 0) >= 2000)
    cf = by_arm_agg.get("ARM_CONTEXT_FREE_SUBSTRATE", {})
    sanity_ok = True  # default OK (deferred check) when not full-mode
    sanity_value = float("nan")
    if not cf.get("all_seeds_failed", False):
        sanity_value = cf["bpc_best_mean"]
        if is_full_mode:
            sanity_ok = abs(sanity_value - SUBSTRATE_CONTEXT_FREE_REF) <= SANITY_RAIL_TOL

    # Word-bigram calibration: bpc <= HARD_CAP (full-mode only -- smoke runs at
    # V=200 and naturally has a much lower-entropy bigram baseline).
    bg = by_arm_agg.get("ARM_WORD_BIGRAM", {})
    bigram_ok = True
    bigram_bpc = float("nan")
    if not bg.get("all_seeds_failed", False):
        bigram_bpc = bg["bpc_best_mean"]
        if is_full_mode:
            bigram_ok = bigram_bpc <= BIGRAM_BPC_HARD_CAP

    # K16+cfRPE deltas vs word-bigram
    k16 = by_arm_agg.get("ARM_SEQUENCE_BIND_K16_CFRPE", {})
    k8 = by_arm_agg.get("ARM_SEQUENCE_BIND_K8", {})
    k16_bpc = k16.get("bpc_best_mean", float("inf"))
    k16_cv = k16.get("bpc_best_cv", float("inf"))
    k8_bpc = k8.get("bpc_best_mean", float("inf"))
    cv_ok = k16_cv <= HP_CV_MAX

    delta_k16_vs_bigram = bigram_bpc - k16_bpc  # positive = substrate better
    delta_k8_vs_bigram = bigram_bpc - k8_bpc

    summary = (
        "uni=bpc%.3f|bigram=bpc%.3f|cf_sub=bpc%.3f|K8=bpc%.3f|K16cfRPE=bpc%.3f|"
        "deltaK16_vs_bigram=%+.3f|deltaK8_vs_bigram=%+.3f|cv_K16=%.3f|sanity=%s|bg_cal=%s|n_llm=%d"
    ) % (
        by_arm_agg.get("ARM_UNIGRAM", {}).get("bpc_best_mean", float("nan")),
        bigram_bpc, sanity_value, k8_bpc, k16_bpc,
        delta_k16_vs_bigram, delta_k8_vs_bigram, k16_cv,
        "OK" if sanity_ok else "FAIL", "OK" if bigram_ok else "FAIL", n_llm,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "sanity_rail_ok": bool(sanity_ok),
        "sanity_value": float(sanity_value) if math.isfinite(sanity_value) else None,
        "sanity_ref": SUBSTRATE_CONTEXT_FREE_REF,
        "sanity_tol": SANITY_RAIL_TOL,
        "bigram_calibration_ok": bool(bigram_ok),
        "bigram_bpc": float(bigram_bpc) if math.isfinite(bigram_bpc) else None,
        "bigram_min_expected": BIGRAM_BPC_MIN,
        "bigram_max_expected": BIGRAM_BPC_MAX,
        "bigram_hard_cap": BIGRAM_BPC_HARD_CAP,
        "delta_K16_vs_bigram": float(delta_k16_vs_bigram) if math.isfinite(delta_k16_vs_bigram) else None,
        "delta_K8_vs_bigram": float(delta_k8_vs_bigram) if math.isfinite(delta_k8_vs_bigram) else None,
        "k16_cv": float(k16_cv) if math.isfinite(k16_cv) else None,
        "hp_delta_vs_bigram": HP_DELTA_VS_BIGRAM,
        "cg_delta_vs_bigram": CG_DELTA_VS_BIGRAM,
        "hp_cv_max": HP_CV_MAX,
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Word-level text8 sequence-modeling harness. ARM_WORD_BIGRAM is the "
            "real-LM baseline (add-alpha=%.2f). HARD_PASS = K16+cfRPE beats "
            "word-bigram by >=%.2f bits with cv<=%.2f, sanity rail satisfied "
            "(CF_SUBSTRATE within +/-%.2f of %.4f), bigram calibration satisfied "
            "(bpc<=%.2f), substrate-only-decode (n_llm==0). CHAIN_GRADE_BONUS "
            "= K16+cfRPE beats word-bigram by >=%.2f. N_DIM=%d N_TRAIN=%d "
            "N_HELD=%d V=%d K8=%d K16=%d."
        ) % (
            BIGRAM_ALPHA, HP_DELTA_VS_BIGRAM, HP_CV_MAX, SANITY_RAIL_TOL,
            SUBSTRATE_CONTEXT_FREE_REF, BIGRAM_BPC_HARD_CAP, CG_DELTA_VS_BIGRAM,
            N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, K_SHORT, K_LONG,
        ),
        "cites": [
            "preregs/2026-06-24_substrate_sequence_modeling_production_v1.md",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
            "experiments/exp_c3_compressed_sequence_replay_v1.py",
            "experiments/exp_g1b_capacity_sweep_v1.py",
            "hdlab/sequence_memory.py",
            "USER_2026-06-24_sequence_modelling_we_could_get_very_good",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    if not sanity_ok:
        return ("HARD_FAIL",
                ("HARD_FAIL: sanity rail violated -- ARM_CONTEXT_FREE_SUBSTRATE "
                 "bpc_best=%.4f outside [%.4f +/- %.2f] (expected near fair_harness "
                 "landed). Harness mis-spec; cannot interpret sequence arms. %s") % (
                    sanity_value, SUBSTRATE_CONTEXT_FREE_REF, SANITY_RAIL_TOL, summary),
                detail)

    if not bigram_ok:
        return ("HARD_FAIL",
                ("HARD_FAIL: word-bigram baseline broken -- bpc=%.4f > hard-cap %.2f "
                 "(expected [%.2f, %.2f] for add-alpha=%.2f). Baseline mis-spec; "
                 "cannot evaluate HP. %s") % (
                    bigram_bpc, BIGRAM_BPC_HARD_CAP, BIGRAM_BPC_MIN, BIGRAM_BPC_MAX,
                    BIGRAM_ALPHA, summary),
                detail)

    if k16.get("all_seeds_failed", False):
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_SEQUENCE_BIND_K16_CFRPE all-seeds failed. %s" % summary,
                detail)

    # HARD_PASS path
    if delta_k16_vs_bigram >= HP_DELTA_VS_BIGRAM and cv_ok:
        if delta_k16_vs_bigram >= CG_DELTA_VS_BIGRAM:
            return ("HARD_PASS",
                    ("HARD_PASS_CHAIN_GRADE_BONUS: substrate K16+cfRPE bpc=%.4f "
                     "beats word-bigram bpc=%.4f by %.3f bits (>= %.2f bonus bar) "
                     "with cv=%.3f<=%.2f. Substrate sequence-modeling DECISIVELY "
                     "clears real-LM baseline. %s") % (
                        k16_bpc, bigram_bpc, delta_k16_vs_bigram,
                        CG_DELTA_VS_BIGRAM, k16_cv, HP_CV_MAX, summary),
                    detail)
        return ("HARD_PASS",
                ("HARD_PASS: substrate K16+cfRPE bpc=%.4f beats word-bigram bpc=%.4f "
                 "by %.3f bits (>= %.2f) with cv=%.3f<=%.2f. Sequence-binding "
                 "primitive + cf-RPE delta-rule lifts substrate past real-LM "
                 "baseline. %s") % (
                    k16_bpc, bigram_bpc, delta_k16_vs_bigram, HP_DELTA_VS_BIGRAM,
                    k16_cv, HP_CV_MAX, summary),
                detail)

    # MIDDLE_BAND
    k16_beats_bigram_any = delta_k16_vs_bigram > 0
    k8_beats_bigram = delta_k8_vs_bigram > 0
    if k16_beats_bigram_any or k8_beats_bigram:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND: substrate beats word-bigram but does NOT clear "
                 "HP bar (deltaK16=%.3f vs HP %.2f; deltaK8=%.3f; cv_K16=%.3f). "
                 "Sequence-modeling shows partial signal. %s") % (
                    delta_k16_vs_bigram, HP_DELTA_VS_BIGRAM, delta_k8_vs_bigram,
                    k16_cv, summary),
                detail)

    return ("HARD_FAIL",
            ("HARD_FAIL: substrate sequence-modeling (K16+cfRPE) does NOT beat "
             "word-bigram (deltaK16=%+.3f). Sequence-binding + cf-RPE insufficient "
             "to clear real-LM baseline on word-level text8. %s") % (
                delta_k16_vs_bigram, summary),
            detail)


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: word-bigram add-alpha smoothing -- row-stochastic
    V_t = 5
    idx_t = np.array([1, 2, 1, 3, 4, 1, 2], dtype=np.int64)
    P = build_word_bigram(idx_t, V_t, alpha=0.1)
    assert P.shape == (V_t, V_t), "T1 shape"
    assert np.allclose(P.sum(axis=1), 1.0, atol=1e-5), "T1 row-stochastic: %s" % P.sum(axis=1)

    # T2: HRR bind: shape preserved + non-trivial output
    A = np.random.default_rng(0).standard_normal(64).astype(np.float32)
    B = np.random.default_rng(1).standard_normal(64).astype(np.float32)
    AB = hrr_bind(A, B)
    assert AB.shape == (64,), "T2 shape"
    assert np.linalg.norm(AB) > 1e-6, "T2 nonzero norm"

    # T3: SequenceMatrix bind_pair semantics via outer-product
    a = _l2_normalize(np.random.default_rng(2).standard_normal(32).astype(np.float32))
    b = _l2_normalize(np.random.default_rng(3).standard_normal(32).astype(np.float32))
    c = _l2_normalize(np.random.default_rng(4).standard_normal(32).astype(np.float32))
    S = np.outer(b, a)  # bind_pair(a, b): S += outer(b, a)
    pred = S @ a
    pred_n = pred / (np.linalg.norm(pred) + 1e-12)
    cos_pred_b = float(pred_n @ b)
    cos_pred_c = float(pred_n @ c)
    assert cos_pred_b > cos_pred_c, "T3 round-trip: cos(pred,b)=%.3f vs cos(pred,c)=%.3f" % (
        cos_pred_b, cos_pred_c)

    # T4: cf-RPE delta-rule reduces error
    k = _l2_normalize(np.random.default_rng(5).standard_normal(32).astype(np.float32))
    tgt = _l2_normalize(np.random.default_rng(6).standard_normal(32).astype(np.float32))
    S2 = np.zeros((32, 32), dtype=np.float32)
    pred_before = S2 @ k
    err_before = np.linalg.norm(tgt - pred_before)
    eta = 0.5
    delta = tgt - pred_before
    S2 += eta * np.outer(delta, k)
    pred_after = S2 @ k
    err_after = np.linalg.norm(tgt - pred_after)
    assert err_after <= err_before + 1e-6, "T4 delta-rule must not increase error: %.4f -> %.4f" % (
        err_before, err_after)

    # T5: K=8 context key is non-zero
    n_smoke = 30
    V_s = 10
    n_dim_s = 64
    idx_s = np.random.default_rng(7).integers(0, V_s, size=n_smoke).astype(np.int64)
    E_s = _l2_normalize(np.random.default_rng(8).standard_normal((V_s, n_dim_s)).astype(np.float32))
    keys = build_context_keys(idx_s, E_s, K=8, seed=0)
    assert keys.shape == (n_smoke, n_dim_s), "T5 shape"
    assert np.linalg.norm(keys, axis=1).max() > 0.01, "T5 non-zero keys"

    # T6: bpc_from_logp on planted: unigram BPC reproduced at lambda=0
    U_t = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
    U_log_t = np.log(np.clip(U_t, 1e-30, 1.0))
    nxt_t = np.array([0, 1, 2, 0, 1])
    sub_logits = np.zeros((5, 5), dtype=np.float32)
    logp_lam0 = log_linear_interp_logp(np.log(np.full_like(sub_logits, 1.0 / 5.0)),
                                        U_log_t, 0.0)
    bpc_lam0 = bpc_from_logp(logp_lam0, nxt_t)
    bpc_uni = -float(np.mean(np.log(U_t[nxt_t]))) / math.log(2.0)
    assert abs(bpc_lam0 - bpc_uni) < 1e-4, "T6 lam=0=uni: %.4f vs %.4f" % (bpc_lam0, bpc_uni)

    # T7: verdict bands -- planted HARD_PASS / MIDDLE / HARD_FAIL
    def _u(bpc_uni, bpc_bigram, bpc_cf, bpc_k8, bpc_k16):
        return {"seed": 0, "by_arm": {
            "ARM_UNIGRAM": {"bpc_best": bpc_uni, "top1_acc": 0.21, "mrr_at_10": 0.30},
            "ARM_WORD_BIGRAM": {"bpc_best": bpc_bigram, "top1_acc": 0.30, "mrr_at_10": 0.40},
            "ARM_CONTEXT_FREE_SUBSTRATE": {"bpc_best": bpc_cf, "top1_acc": 0.20,
                                              "mrr_at_10": 0.30, "raw_bpc_at_T1_L1": bpc_cf},
            "ARM_SEQUENCE_BIND_K8": {"bpc_best": bpc_k8, "top1_acc": 0.25,
                                       "mrr_at_10": 0.35, "raw_bpc_at_T1_L1": bpc_k8},
            "ARM_SEQUENCE_BIND_K16_CFRPE": {"bpc_best": bpc_k16, "top1_acc": 0.28,
                                              "mrr_at_10": 0.38, "raw_bpc_at_T1_L1": bpc_k16},
        }, "n_llm_calls": 0}

    # Patch unit factory with full-mode marker so verdict applies sanity + calibration
    def _u_full(bpc_uni, bpc_bigram, bpc_cf, bpc_k8, bpc_k16):
        u = _u(bpc_uni, bpc_bigram, bpc_cf, bpc_k8, bpc_k16)
        u["run_mode"] = "full"
        u["VOCAB_CAP"] = 4000
        return u

    # HARD_PASS: K16 beats bigram by 0.15 (>= 0.10)
    units_hp = [_u_full(7.74, 6.80, 7.30, 6.70, 6.65),
                  _u_full(7.74, 6.80, 7.31, 6.70, 6.65),
                  _u_full(7.74, 6.80, 7.30, 6.70, 6.65)]
    v, m, d = compute_verdict(units_hp)
    assert v == "HARD_PASS", "T7a HP got %s; msg=%s" % (v, m[:250])

    # CHAIN_GRADE_BONUS: K16 beats bigram by 0.35
    units_cg = [_u_full(7.74, 6.80, 7.30, 6.70, 6.45),
                  _u_full(7.74, 6.80, 7.31, 6.70, 6.45),
                  _u_full(7.74, 6.80, 7.30, 6.70, 6.45)]
    v, m, d = compute_verdict(units_cg)
    assert v == "HARD_PASS" and "CHAIN_GRADE_BONUS" in m, \
        "T7b CG got %s; msg=%s" % (v, m[:250])

    # MIDDLE: K16 beats bigram by 0.05 only (< 0.10)
    units_mid = [_u_full(7.74, 6.80, 7.30, 6.78, 6.75),
                   _u_full(7.74, 6.80, 7.31, 6.78, 6.75),
                   _u_full(7.74, 6.80, 7.30, 6.78, 6.75)]
    v, m, _ = compute_verdict(units_mid)
    assert v == "MIDDLE_BAND", "T7c MIDDLE got %s; msg=%s" % (v, m[:250])

    # HARD_FAIL: K16 fails to beat bigram
    units_hf = [_u_full(7.74, 6.80, 7.30, 6.90, 6.95),
                  _u_full(7.74, 6.80, 7.31, 6.90, 6.95),
                  _u_full(7.74, 6.80, 7.30, 6.90, 6.95)]
    v, m, _ = compute_verdict(units_hf)
    assert v == "HARD_FAIL", "T7d HF got %s; msg=%s" % (v, m[:250])

    # Sanity rail violation (full mode): CF outside +/- 0.10 of 7.3065
    units_sanity = [_u_full(7.74, 6.80, 7.80, 6.70, 6.65),
                      _u_full(7.74, 6.80, 7.80, 6.70, 6.65),
                      _u_full(7.74, 6.80, 7.80, 6.70, 6.65)]
    v, m, _ = compute_verdict(units_sanity)
    assert v == "HARD_FAIL" and "sanity rail" in m, "T7e sanity got %s; msg=%s" % (v, m[:250])

    # Smoke-mode bypass: sanity rail deferred when VOCAB_CAP<2000; K16 beats bigram
    # by 0.15 should still classify HARD_PASS even with CF=4.5 (smoke value).
    units_smoke = [_u(7.74, 6.80, 4.50, 6.70, 6.65),
                     _u(7.74, 6.80, 4.50, 6.70, 6.65),
                     _u(7.74, 6.80, 4.50, 6.70, 6.65)]
    for u in units_smoke:
        u["run_mode"] = "smoke"
        u["VOCAB_CAP"] = 200
    v, m, _ = compute_verdict(units_smoke)
    assert v == "HARD_PASS", "T7f smoke-bypass got %s; msg=%s" % (v, m[:250])

    # T8: LLM counter zero
    assert _LLM_CALL_COUNTER[0] == 0, "T8 llm counter"

    print("[selftest] PASS: T1 word-bigram + T2 HRR bind + T3 seq round-trip "
          "+ T4 cf-RPE shrinks error + T5 K=8 ctx + T6 bpc unigram + T7 verdict "
          "bands (HP/CG/MID/HF/sanity) + T8 llm=0", flush=True)


# ============================================================================
# atexit synthesizer
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF: List[Optional[Path]] = [None]
_T0_REF: List[Optional[float]] = [None]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                     "atexit synthesize compute_verdict failed: %s" % e,
                                     {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "anchor": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "N": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_substrate_sequence_modeling_production_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (
                len(units), len(SEEDS), msg[:200]),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
            "config_version": CONFIG_VERSION,
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
          "seeds=%s arms=%s K_SHORT=%d K_LONG=%d cfrpe_eta=%.3f | name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
              SEEDS, ARMS, K_SHORT, K_LONG, CFRPE_ETA, _NAME_SAYS_SMOKE,
              CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
                "schema": "substrate-seq-modeling-prod-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS],
                                       run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "N": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "INGEST_CHUNK": INGEST_CHUNK,
        "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID,
        "MRR_K": MRR_K,
        "K_SHORT": K_SHORT,
        "K_LONG": K_LONG,
        "CFRPE_ETA": CFRPE_ETA,
        "BIGRAM_ALPHA": BIGRAM_ALPHA,
        "arms": ARMS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_substrate_sequence_modeling_production_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate cosine logits; encoder is static; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
