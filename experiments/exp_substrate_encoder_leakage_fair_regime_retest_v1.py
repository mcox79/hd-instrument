"""substrate_encoder_leakage_fair_regime_retest_v1 -- FAIR-REGIME RETEST.

PURPOSE (2026-06-24):
  v1 (substrate_clean_encoder_substrate_as_LM_v1) returned HARD_PASS_LEAKAGE_REAL
  with delta(B-A) = +0.4376 BPC. Research flagged the verdict as potentially a
  measurement-regime artifact, not a substrate property:
    (a) V=4000 forced unigram-floor pinning across all 4 arms (top1 0.215..0.219
        nearly identical -- BPC delta driven by softmax T+lambda calibration,
        NOT by actual ranking improvement; arm B in fact had the HIGHEST top1).
    (b) Arm B (W2V trained on text8 only) ran 1.82s on 100k tokens = severely
        UNDER-CONVERGED vs Google News 100B-token baseline; 6000x training-data
        gap was the dominant confound.

  Fix: re-test under a FAIR regime:
    - V=20000 (5x v1) to escape unigram-floor pinning regime
    - Arm B trained on FULL ~17M-token text8 (not just first 100k)
    - TEMP_GRID extended down to 0.001 to catch sharper softmax regime
    - Report BOTH unigram-conditional BPC (raw bpc_best) AND bigram-conditional
      BPC (= substrate's lift over a proper word-bigram backoff model;
      load-bearing metric per drill)
    - 3 seeds [7, 13, 29] for proper variance

FOUR ARMS (3 seeds [7, 13, 29]; V=20000; N_TRAIN=100k for Hebbian; full text8
~17M for word2vec arm-B training):
  A_W2V_GOOGLE_NEWS_FAIR     word2vec-google-news-300 (rail; reproduces v1
                              arm A on V=20k bigram-conditional metric)
  B_W2V_TEXT8_FULL_17M       gensim Word2Vec PROPERLY converged on full
                              ~17M-token text8 (epochs=5; PRIMARY arm)
  C_RANDOM_PROJECTION_FAIR   fixed Gaussian projection (no semantic; floor)
  D_CHAR_TRIGRAM_FAIR        bag-of-char-trigrams (substrate-native floor)

PRE-REGISTERED BANDS (PRE-REGISTERED BEFORE RUN; load-bearing metric =
bigram-conditional BPC; sacrosanct both directions):
  HARD_PASS_LEAKAGE_REFUTED:
      leakage_delta_B_minus_A on bigram-conditional metric at V=20k
      < 0.10 BPC AND arm B BPC <= unigram floor by >= 0.5 BPC margin
      => v1 verdict REFUTED; encoder-leakage was a V=4000 + under-trained-B
      artifact. Substrate capability robust to encoder choice in fair regime.

  HARD_PASS_LEAKAGE_CONFIRMED:
      leakage_delta on bigram-conditional metric at V=20k >= 0.30 BPC
      AND arm B BPC > unigram floor by < 0.2 BPC
      => v1 verdict confirmed; properly-converged clean encoder still much
      worse than google-news. Path C substrate-owned encoder becomes load-
      bearing for chain-grade substrate-as-LM claims.

  MIDDLE_BAND:
      leakage_delta in [0.10, 0.30) on bigram-conditional metric
      => partial leakage; smaller than v1 estimated. Route to Research for
      decision on Path C priority.

  HARD_FAIL_REGIME:
      all 4 arms still cluster within 0.10 BPC on bigram-conditional metric
      at V=20k => measurement regime STILL not discriminating; ANCHOR 3
      calibration cell needed.

  HARD_FAIL_PROVENANCE:
      arm A on FAIR regime fails to reproduce within 0.20 BPC of the expected
      text8-V=20k word2vec-google-news rail (cell methodology bug; halt).
      NOTE: rail-reference value will be computed FRESH from arm A on V=20k
      bigram-conditional metric (no prior fair_harness reference at V=20k
      bigram-conditional exists; the v1 reference 7.3065 was V=4000 unigram-
      conditional). The provenance check compares arm A across the 3 seeds:
      if seed-CV > 0.10 BPC, that itself flags HARD_FAIL_PROVENANCE.

CRITICAL DISCIPLINES:
  PURE NUMPY + gensim CPU: routes via remote_cpu_queue (PROT-020)
  ASCII-only, no emojis, no em dashes
  Fix #28: per-arm metrics ONLY; no cross-arm framing in verdict_msg
  WHAT_THIS_DOES_NOT_SHOW clause in detail
  All arms share IDENTICAL primitives EXCEPT the encoder
  3 seeds for cross-seed variance check
  Substrate-only-decode gate (word2vec is static open-weight lookup)
  Bigram-conditional metric = PRIMARY (per drill ANCHOR 1)
  Unigram-conditional metric = SECONDARY (kept for v1 comparability)

CITES:
  preregs/2026-06-24_substrate_encoder_leakage_fair_regime_retest_v1.md
  experiments/exp_substrate_clean_encoder_substrate_as_LM_v1.py (v1 base)
  experiments/exp_substrate_brain_word_level_prediction_v2_production_config.py (bigram floor pattern)

PROT-018: no _nN suffix; N_DIM=8192 stated below + in prereg.
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
from typing import Dict, List, Optional, Tuple

import numpy as np

# NO torch import -- pure numpy + gensim for remote_cpu_queue (PROT-020)

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "substrate_encoder_leakage_fair_regime_retest_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Pre-reg band thresholds (FAIR-REGIME bands; load-bearing metric =
# bigram-conditional BPC)
LEAKAGE_REFUTED_DELTA = 0.10          # |B - A| < 0.10 => v1 REFUTED
LEAKAGE_CONFIRMED_DELTA = 0.30        # B - A >= 0.30 => v1 CONFIRMED
ARM_B_FLOOR_MARGIN_REFUTED = 0.50     # B <= unigram_floor - 0.50 => clean encoder real
ARM_B_FLOOR_MARGIN_CONFIRMED = 0.20   # B > unigram_floor - 0.20 => clean encoder failed
ARM_A_SEED_CV_TOL = 0.10              # seed-CV on arm A > 0.10 => HARD_FAIL_PROVENANCE
ARM_A_RAIL_REPRO_TOL = 0.20           # used post-hoc against v1 if applicable

# Joint (T, lambda) sweep grid -- extended TEMP_GRID down to 0.001 per drill fix
TEMP_GRID = [0.001, 0.003, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Sparse-bipolar fraction (matched across all 4 arms)
SPARSE_BIPOLAR_F = 0.05

# CLI
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config -- FAIR REGIME
WORD2VEC_MODEL = "word2vec-google-news-300"
PRETRAIN_DIM = 300
CLEAN_W2V_DIM = 300
CLEAN_W2V_WINDOW = 5
CLEAN_W2V_MIN_COUNT = 5
CLEAN_W2V_EPOCHS_FULL = 5   # FULL text8 ~17M tokens; 5 epochs ~ standard text8 W2V
CLEAN_W2V_WORKERS = 4

if RUN_MODE == "full":
    SEEDS = [7, 13, 29]                # 3 seeds per drill
    N_DIM = 8192
    N_TRAIN = 100_000                  # tokens for Hebbian W and bigram floor
    N_HELD = 20_000
    VOCAB_CAP = 20_000                 # V=20k per drill fix (5x v1)
    INGEST_CHUNK = 4096
    RECALL_BATCH = 256                 # smaller batch; V=20k means logits row=20k floats
    W2V_TRAIN_TOKEN_BUDGET = 17_000_000  # FULL text8 for arm B (~17M tokens)
    CLEAN_W2V_EPOCHS_RUN = CLEAN_W2V_EPOCHS_FULL
else:
    # Smoke: <120s on laptop CPU; exercises all 4 arms + joint sweep + verdict bands
    # Smaller V to keep bigram matrix tractable and run-time low.
    SEEDS = [0]
    N_DIM = 512
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    W2V_TRAIN_TOKEN_BUDGET = 5_000     # tiny smoke-only
    CLEAN_W2V_EPOCHS_RUN = 2           # quick smoke; not a quality bar

ARMS = [
    "A_W2V_GOOGLE_NEWS_FAIR",
    "B_W2V_TEXT8_FULL_17M",
    "C_RANDOM_PROJECTION_FAIR",
    "D_CHAR_TRIGRAM_FAIR",
]

ARM_CONFIG: Dict[str, Dict] = {
    "A_W2V_GOOGLE_NEWS_FAIR":     {"encoder": "w2v_google_news",
                                     "training_data": "google_news_100B"},
    "B_W2V_TEXT8_FULL_17M":       {"encoder": "w2v_text8_full",
                                     "training_data": "text8_full_~17M_tokens"},
    "C_RANDOM_PROJECTION_FAIR":   {"encoder": "random_projection",
                                     "training_data": "none"},
    "D_CHAR_TRIGRAM_FAIR":        {"encoder": "char_trigram",
                                     "training_data": "none_deterministic_hash"},
}

CONFIG_VERSION = (
    "substrate_encoder_leakage_fair_regime_retest_v1; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s mode=%s "
    "sparse_f=%.3f temps=%s lambdas=%s MRR_K=%d "
    "clean_w2v dim=%d window=%d min_count=%d epochs=%d w2v_train_budget=%d "
    "bands refuted_delta=%.2f confirmed_delta=%.2f "
    "floor_margin_refuted=%.2f floor_margin_confirmed=%.2f cv_tol=%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    SPARSE_BIPOLAR_F, TEMP_GRID, LAMBDA_GRID, MRR_K,
    CLEAN_W2V_DIM, CLEAN_W2V_WINDOW, CLEAN_W2V_MIN_COUNT,
    CLEAN_W2V_EPOCHS_RUN, W2V_TRAIN_TOKEN_BUDGET,
    LEAKAGE_REFUTED_DELTA, LEAKAGE_CONFIRMED_DELTA,
    ARM_B_FLOOR_MARGIN_REFUTED, ARM_B_FLOOR_MARGIN_CONFIRMED,
    ARM_A_SEED_CV_TOL,
)

_LLM_CALL_COUNTER = [0]


# ============================================================================
# Primitives (shared across arms; identical to v1)
# ============================================================================

def l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        n = np.linalg.norm(X)
        return X / max(n, eps)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(norms < eps, 1.0, norms)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    return rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))


def sparsify_bipolar_np(E: np.ndarray, f: float) -> np.ndarray:
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    abs_E = np.abs(E)
    topk_idx = np.argpartition(-abs_E, kth=k - 1, axis=1)[:, :k]
    out = np.zeros_like(E)
    rows = np.arange(V)[:, None]
    signs = np.sign(E[rows, topk_idx])
    signs = np.where(signs == 0, 1.0, signs)
    out[rows, topk_idx] = signs.astype(E.dtype)
    return out


# ============================================================================
# Char-trigram encoder (substrate-native)
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


def build_E_char_trigram(vocab: List[str], n_dim: int, seed: int) -> np.ndarray:
    E = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    return l2_normalize_np(E)


# ============================================================================
# word2vec-google-news encoder
# ============================================================================

_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_kv(model_name: str):
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    from tools.gensim_load_helper import load_gensim_kv
    kv = load_gensim_kv(model_name, cache_dir=GENSIM_CACHE_DIR)
    _GENSIM_KV_CACHE[model_name] = kv
    return kv


def _embed_vocab_via_gensim_kv(vocab: List[str], kv) -> Tuple[np.ndarray, int, int]:
    dim = kv.vector_size
    V = len(vocab)
    out = np.zeros((V, dim), dtype=np.float32)
    n_hit, n_miss = 0, 0
    for i, w in enumerate(vocab):
        v = None
        if w in kv.key_to_index:
            v = kv[w]
        elif w.lower() in kv.key_to_index:
            v = kv[w.lower()]
        if v is None:
            n_miss += 1
        else:
            n_hit += 1
            out[i] = v.astype(np.float32)
    return out, n_hit, n_miss


def build_E_w2v_google_news(vocab: List[str], n_dim: int, seed: int
                             ) -> Tuple[np.ndarray, Dict]:
    try:
        kv = _load_gensim_kv(WORD2VEC_MODEL)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[A_w2v_google] LOAD FAIL: %s -- char-trigram fallback" % err, flush=True)
        E = build_E_char_trigram(vocab, n_dim, seed)
        E = l2_normalize_np(sparsify_bipolar_np(E, SPARSE_BIPOLAR_F))
        return E, {"fallback_to_char_trigram": True, "load_error": err,
                   "n_hit": 0, "n_miss": len(vocab), "pretrain_dim": -1}
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim_kv(vocab, kv)
    E_pre_n = l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_pre = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_pre < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = l2_normalize_np(E_proj)
    E_sparse = l2_normalize_np(sparsify_bipolar_np(E_proj, SPARSE_BIPOLAR_F))
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size),
            "fallback_to_char_trigram": False, "training_data": "google_news_100B"}
    return E_sparse, meta


# ============================================================================
# Clean Word2Vec encoder -- FULL ~17M text8 (THE PRIMARY ARM)
# Trained PROPERLY on full text8 corpus; NO external data.
# ============================================================================

def train_clean_w2v_on_text8_full(train_tokens: List[str], dim: int,
                                    window: int, min_count: int, epochs: int,
                                    workers: int, seed: int) -> Tuple[object, Dict]:
    """Train gensim Word2Vec on the FULL text8 corpus (~17M tokens).

    Returns (KeyedVectors, meta). NO external data; clean of Google News.
    Converged training (~5 epochs over 17M tokens is the standard text8 W2V
    bar; takes ~10-30 min CPU depending on workers).
    """
    from gensim.models import Word2Vec
    t0 = time.time()
    # gensim Word2Vec sentences = list of token lists. text8 is one big stream;
    # chunk into 1000-token "sentences" so window can operate sensibly.
    chunk_size = 1000
    sentences = [train_tokens[i:i + chunk_size]
                  for i in range(0, len(train_tokens), chunk_size)]
    n_sent = len(sentences)
    print("[clean_w2v_full] training on %d tokens (%d sentences) "
          "dim=%d window=%d min_count=%d epochs=%d workers=%d seed=%d" % (
              len(train_tokens), n_sent, dim, window, min_count, epochs,
              workers, seed), flush=True)
    model = Word2Vec(
        sentences=sentences,
        vector_size=dim,
        window=window,
        min_count=min_count,
        workers=workers,
        epochs=epochs,
        sg=1,                # skip-gram
        seed=int(seed),
    )
    wall = round(time.time() - t0, 2)
    # Convergence check: training_wall_s should be substantial for full corpus
    # (<10s on 17M tokens = failure to actually load+train).
    meta = {
        "training_data": "text8_full_~17M_tokens",
        "n_train_tokens": int(len(train_tokens)),
        "n_sentences": int(n_sent),
        "chunk_size": int(chunk_size),
        "wv_dim": int(model.wv.vector_size),
        "wv_vocab_size": int(len(model.wv.key_to_index)),
        "epochs": int(epochs),
        "window": int(window),
        "min_count": int(min_count),
        "training_wall_s": wall,
        # Convergence sentinel: full-corpus 5-epoch training should take
        # >>1.82s (the v1 under-trained value); flag if suspiciously fast.
        "convergence_sentinel_OK": bool(wall >= 60.0 or len(train_tokens) < 100_000),
    }
    return model.wv, meta


def build_E_w2v_text8_full(vocab: List[str], n_dim: int, seed: int,
                            w2v_train_tokens: List[str]) -> Tuple[np.ndarray, Dict]:
    """Train clean Word2Vec on FULL text8 train tokens -> project -> sparse-bipolar.

    Arm B uses the FULL text8 corpus (separate from the Hebbian N_TRAIN=100k
    sub-stream) so that word2vec convergence is fair vs google-news rail.
    """
    kv, train_meta = train_clean_w2v_on_text8_full(
        w2v_train_tokens, dim=CLEAN_W2V_DIM, window=CLEAN_W2V_WINDOW,
        min_count=CLEAN_W2V_MIN_COUNT, epochs=CLEAN_W2V_EPOCHS_RUN,
        workers=CLEAN_W2V_WORKERS, seed=seed,
    )
    print("[B_w2v_text8_full] train done (%.1fs); wv_vocab=%d convergence_OK=%s" % (
        train_meta["training_wall_s"], train_meta["wv_vocab_size"],
        train_meta["convergence_sentinel_OK"]), flush=True)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim_kv(vocab, kv)
    E_pre_n = l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_pre = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_pre < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = l2_normalize_np(E_proj)
    E_sparse = l2_normalize_np(sparsify_bipolar_np(E_proj, SPARSE_BIPOLAR_F))
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size),
            "fallback_to_char_trigram": False,
            "training_meta": train_meta}
    return E_sparse, meta


# ============================================================================
# Random projection encoder (no semantic structure; floor)
# ============================================================================

def build_E_random_projection(vocab_size: int, n_dim: int, seed: int
                                ) -> Tuple[np.ndarray, Dict]:
    rng = np.random.default_rng(seed * 7919 + 31)
    E = rng.standard_normal((vocab_size, n_dim)).astype(np.float32)
    E = l2_normalize_np(E)
    E_sparse = l2_normalize_np(sparsify_bipolar_np(E, SPARSE_BIPOLAR_F))
    meta = {"n_vocab": int(vocab_size), "encoder_type": "random_projection",
            "no_training": True}
    return E_sparse, meta


# ============================================================================
# Char-trigram + sparse-bipolar (arm D; substrate-native floor)
# ============================================================================

def build_E_char_trigram_sparse(vocab: List[str], n_dim: int, seed: int
                                  ) -> Tuple[np.ndarray, Dict]:
    E = build_E_char_trigram(vocab, n_dim, seed)
    E_sparse = l2_normalize_np(sparsify_bipolar_np(E, SPARSE_BIPOLAR_F))
    meta = {"n_vocab": int(len(vocab)), "encoder_type": "char_trigram_sparse",
            "no_training": True}
    return E_sparse, meta


# ============================================================================
# Hebbian W builder (rank-1; identical across arms)
# ============================================================================

def build_rank1_W_np(idx_train: np.ndarray, E: np.ndarray, chunk: int) -> np.ndarray:
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
# text8 + vocab
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    """Load up to n_total tokens. Use a large n_total to load full corpus."""
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


def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


# ============================================================================
# Word-bigram floor (for bigram-conditional BPC metric)
# Per drill ANCHOR 1: substrate's lift OVER bigram backoff = load-bearing metric.
# Dense numpy bigram table: V=20k * V=20k * 4 bytes = 1.6 GB (tractable on
# remote_cpu with 32GB+ RAM); smoke V=300 * 300 = 360 KB.
# ============================================================================

def build_bigram_np(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    """Add-alpha bigram table P[i,j] = P(j | prev=i). Float32 dense.

    Memory: V*V*4 bytes. V=20k -> 1.6 GB; V=300 -> 360 KB.
    """
    counts = np.full((V, V), alpha, dtype=np.float64)
    if len(idx_train) >= 2:
        prev = idx_train[:-1]
        nxt = idx_train[1:]
        np.add.at(counts, (prev, nxt), 1.0)
    row_sum = counts.sum(axis=1, keepdims=True)
    P_bi = (counts / row_sum).astype(np.float32)
    return P_bi


def bigram_logp_for_contexts(idx_ctx: np.ndarray, P_bi: np.ndarray,
                              P_uni: np.ndarray, train_seen_prev: np.ndarray,
                              backoff_lambda: float = 0.3) -> np.ndarray:
    """Return (n_ctx, V) logp under add-alpha bigram with unigram backoff."""
    n = idx_ctx.shape[0]
    V = P_uni.shape[0]
    out = np.empty((n, V), dtype=np.float64)
    for i in range(n):
        p = P_bi[idx_ctx[i]]
        if train_seen_prev[idx_ctx[i]]:
            mix = backoff_lambda * P_uni + (1.0 - backoff_lambda) * p
        else:
            mix = P_uni
        mix = mix / mix.sum()
        out[i] = mix
    return np.log(np.clip(out, 1e-30, None))


# ============================================================================
# Joint (T, lambda) sweep + BPC / top-1 / MRR
# ============================================================================

def softmax_logits_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp_logp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float) -> np.ndarray:
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
    top_sorted = top_idx[rows, order]
    rr = 0.0
    for i in range(n):
        match = np.where(top_sorted[i] == nxt[i])[0]
        if len(match) > 0:
            rr += 1.0 / float(match[0] + 1)
    return float(rr / n)


def joint_sweep_two_baselines(
    sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
    U_log: np.ndarray, BI_log_dev: np.ndarray, BI_log_test: np.ndarray,
    nxt_dev: np.ndarray, nxt_test: np.ndarray,
    temp_grid: list, lambda_grid: list, mrr_k: int) -> Dict:
    """Joint (T, lambda) sweep with TWO baselines (unigram + bigram).

    Returns BOTH unigram-conditional bpc_best (substrate vs unigram backoff;
    matches v1 metric) AND bigram-conditional bpc_best (substrate vs proper
    word-bigram backoff; PRIMARY metric per drill).
    """
    # Raw T=1, lambda=1 (pure substrate, no backoff)
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)

    # ---- UNIGRAM-CONDITIONAL sweep (matches v1 metric) ----
    best_bpc_uni = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1_uni = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr_uni = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    for T in temp_grid:
        probs_dev = softmax_logits_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in lambda_grid:
            logp_dev = log_linear_interp_logp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc_from_logp(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
            if bd < best_bpc_uni["dev_value"]:
                best_bpc_uni = {"T": float(T), "lambda": float(lam), "dev_value": bd}
            if td > best_top1_uni["dev_value"]:
                best_top1_uni = {"T": float(T), "lambda": float(lam), "dev_value": td}
            if md > best_mrr_uni["dev_value"]:
                best_mrr_uni = {"T": float(T), "lambda": float(lam), "dev_value": md}

    # ---- BIGRAM-CONDITIONAL sweep (PRIMARY per drill) ----
    # log-linear mix substrate with BIGRAM baseline (per-row); replaces U_log.
    best_bpc_bi = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1_bi = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr_bi = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    for T in temp_grid:
        probs_dev = softmax_logits_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in lambda_grid:
            # Per-row bigram log-linear mix
            combined = lam * logp_sub_dev + (1.0 - lam) * BI_log_dev
            combined = combined - combined.max(axis=1, keepdims=True)
            Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
            logp_dev = combined - Z[:, None]
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc_from_logp(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
            if bd < best_bpc_bi["dev_value"]:
                best_bpc_bi = {"T": float(T), "lambda": float(lam), "dev_value": bd}
            if td > best_top1_bi["dev_value"]:
                best_top1_bi = {"T": float(T), "lambda": float(lam), "dev_value": td}
            if md > best_mrr_bi["dev_value"]:
                best_mrr_bi = {"T": float(T), "lambda": float(lam), "dev_value": md}

    # ---- TEST evaluation at best dev hyperparams ----
    def _test_uni(T, lam, fn):
        probs_test = softmax_logits_with_T(sub_logits_test, T)
        logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
        logp_test = log_linear_interp_logp(logp_sub_test, U_log, lam)
        return fn(logp_test, nxt_test)

    def _test_bi(T, lam, fn):
        probs_test = softmax_logits_with_T(sub_logits_test, T)
        logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
        combined = lam * logp_sub_test + (1.0 - lam) * BI_log_test
        combined = combined - combined.max(axis=1, keepdims=True)
        Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
        logp_test = combined - Z[:, None]
        return fn(logp_test, nxt_test)

    # Pure baselines on test (for floor reference)
    uni_only_test = bpc_from_logp(np.broadcast_to(U_log, (len(nxt_test), U_log.shape[0])).copy(), nxt_test)
    bi_only_test = bpc_from_logp(BI_log_test, nxt_test)

    bpc_uni_best = _test_uni(best_bpc_uni["T"], best_bpc_uni["lambda"], bpc_from_logp)
    top1_uni_best = _test_uni(best_top1_uni["T"], best_top1_uni["lambda"], top1_acc_from_logp)
    mrr_uni_best = _test_uni(best_mrr_uni["T"], best_mrr_uni["lambda"],
                              lambda lp, nx: mrr_at_k(lp, nx, mrr_k))

    bpc_bi_best = _test_bi(best_bpc_bi["T"], best_bpc_bi["lambda"], bpc_from_logp)
    top1_bi_best = _test_bi(best_top1_bi["T"], best_top1_bi["lambda"], top1_acc_from_logp)
    mrr_bi_best = _test_bi(best_mrr_bi["T"], best_mrr_bi["lambda"],
                            lambda lp, nx: mrr_at_k(lp, nx, mrr_k))

    return {
        # PRIMARY: bigram-conditional
        "bpc_bigram_best": round(bpc_bi_best, 4),
        "top1_bigram_best": round(top1_bi_best, 4),
        "mrr_at_10_bigram_best": round(mrr_bi_best, 4),
        "best_T_bigram": best_bpc_bi["T"],
        "best_lambda_bigram": best_bpc_bi["lambda"],
        "best_dev_bpc_bigram": round(best_bpc_bi["dev_value"], 4),
        # SECONDARY: unigram-conditional (matches v1)
        "bpc_unigram_best": round(bpc_uni_best, 4),
        "top1_unigram_best": round(top1_uni_best, 4),
        "mrr_at_10_unigram_best": round(mrr_uni_best, 4),
        "best_T_unigram": best_bpc_uni["T"],
        "best_lambda_unigram": best_bpc_uni["lambda"],
        "best_dev_bpc_unigram": round(best_bpc_uni["dev_value"], 4),
        # Floors (test set)
        "unigram_floor_bpc_test": round(uni_only_test, 4),
        "bigram_floor_bpc_test": round(bi_only_test, 4),
        # Diagnostics
        "raw_bpc_at_T1_L1": round(raw_bpc_at_T1_L1, 4),
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
    }


# ============================================================================
# Per-arm runner
# ============================================================================

def compute_arm_logits(E_used: np.ndarray, idx_train: np.ndarray,
                        idx_held: np.ndarray) -> np.ndarray:
    V, dim = E_used.shape
    W = build_rank1_W_np(idx_train, E_used, INGEST_CHUNK)
    n_ctx = len(idx_held) - 1
    logits = np.zeros((n_ctx, V), dtype=np.float32)
    E_norm = l2_normalize_np(E_used)
    for b in range(0, n_ctx, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_ctx)
        src = E_used[idx_held[b:end]]
        query = src @ W.T
        query = l2_normalize_np(query)
        logits[b:end] = query @ E_norm.T
    return logits


def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading text8 + building vocab (V=%d)" % (seed, VOCAB_CAP),
          flush=True)
    # Load enough tokens for both Hebbian + held substream
    toks_sub = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks_sub) < N_TRAIN + N_HELD:
        print("[WARN] corpus short for Hebbian: %d vs %d" % (
            len(toks_sub), N_TRAIN + N_HELD), flush=True)
    train_toks = toks_sub[:N_TRAIN]
    held_toks = toks_sub[N_TRAIN:N_TRAIN + N_HELD]

    # Arm B w2v training: FULL corpus -- separate load, larger token budget
    # Skip in smoke (smoke uses train_toks).
    if RUN_MODE == "full":
        print("[seed=%d] loading FULL text8 for w2v arm B training "
              "(budget=%d tokens)..." % (seed, W2V_TRAIN_TOKEN_BUDGET), flush=True)
        t0 = time.time()
        w2v_train_tokens = load_text8_tokens(W2V_TRAIN_TOKEN_BUDGET)
        print("[seed=%d] loaded %d tokens for w2v arm B (%.1fs)" % (
            seed, len(w2v_train_tokens), time.time() - t0), flush=True)
    else:
        w2v_train_tokens = train_toks  # smoke: reuse small train_toks

    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d w2v_budget=%d" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, len(w2v_train_tokens)), flush=True)

    # Build 4 encoders
    encoder_meta: Dict[str, Dict] = {}

    print("[seed=%d arm A] building word2vec-google-news E..." % seed, flush=True)
    t0 = time.time()
    E_A, meta_A = build_E_w2v_google_news(vocab, N_DIM, seed)
    encoder_meta["A"] = meta_A
    print("[seed=%d arm A] E built (%.1fs) hit=%d miss=%d" % (
        seed, time.time() - t0, meta_A.get("n_hit", -1),
        meta_A.get("n_miss", -1)), flush=True)

    print("[seed=%d arm B] training CLEAN W2V on FULL text8 (~17M)..." % seed,
          flush=True)
    t0 = time.time()
    E_B, meta_B = build_E_w2v_text8_full(vocab, N_DIM, seed, w2v_train_tokens)
    encoder_meta["B"] = meta_B
    print("[seed=%d arm B] E built (%.1fs) hit=%d miss=%d "
          "training_wall_s=%.2f convergence_OK=%s" % (
              seed, time.time() - t0, meta_B.get("n_hit", -1),
              meta_B.get("n_miss", -1),
              meta_B.get("training_meta", {}).get("training_wall_s", -1),
              meta_B.get("training_meta", {}).get("convergence_sentinel_OK")),
          flush=True)

    print("[seed=%d arm C] building random-projection E..." % seed, flush=True)
    t0 = time.time()
    E_C, meta_C = build_E_random_projection(V, N_DIM, seed)
    encoder_meta["C"] = meta_C
    print("[seed=%d arm C] E built (%.1fs)" % (seed, time.time() - t0), flush=True)

    print("[seed=%d arm D] building char-trigram sparse E..." % seed, flush=True)
    t0 = time.time()
    E_D, meta_D = build_E_char_trigram_sparse(vocab, N_DIM, seed)
    encoder_meta["D"] = meta_D
    print("[seed=%d arm D] E built (%.1fs)" % (seed, time.time() - t0), flush=True)

    encoder_by_arm = {
        "A_W2V_GOOGLE_NEWS_FAIR":   E_A,
        "B_W2V_TEXT8_FULL_17M":     E_B,
        "C_RANDOM_PROJECTION_FAIR": E_C,
        "D_CHAR_TRIGRAM_FAIR":      E_D,
    }

    # Shared eval scaffolding
    unk = w2i["<unk>"]
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask_unk_filter = (ctx_full != unk)

    # Unigram baseline (alpha=0.1)
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    # Bigram baseline (alpha=0.1) -- LOAD-BEARING METRIC per drill
    print("[seed=%d] building bigram floor (V=%d -> V*V=%d cells, "
          "%.1f MB float32)..." % (
              seed, V, V * V, V * V * 4 / 1e6), flush=True)
    t0 = time.time()
    P_bi = build_bigram_np(idx_train, V=V, alpha=0.1)
    train_seen_prev = np.zeros(V, dtype=bool)
    train_seen_prev[idx_train[:-1]] = True
    print("[seed=%d] bigram built (%.1fs)" % (seed, time.time() - t0), flush=True)

    by_arm: Dict[str, Dict] = {}
    for arm in ARMS:
        cfg = ARM_CONFIG[arm]
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] cfg=%s" % (seed, arm, cfg), flush=True)
        E_used = encoder_by_arm[arm]
        try:
            logits_full = compute_arm_logits(E_used, idx_train, idx_held)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {
                "compute_failed": True, "compute_error": err,
                "bpc_bigram_best": float("inf"), "bpc_unigram_best": float("inf"),
                "top1_bigram_best": float("nan"), "top1_unigram_best": float("nan"),
                "mrr_at_10_bigram_best": float("nan"),
                "mrr_at_10_unigram_best": float("nan"),
                "raw_bpc_at_T1_L1": float("inf"),
                "best_T_bigram": float("nan"), "best_lambda_bigram": float("nan"),
                "best_T_unigram": float("nan"), "best_lambda_unigram": float("nan"),
                "unigram_floor_bpc_test": float("nan"),
                "bigram_floor_bpc_test": float("nan"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "config": cfg,
            }
            continue
        # ctx-unk filter (fair_harness convention)
        logits_eval = logits_full[mask_unk_filter]
        nxt_eval = nxt_full[mask_unk_filter]
        ctx_eval = ctx_full[mask_unk_filter]
        n_eval = len(nxt_eval)
        if n_eval < 2:
            by_arm[arm] = {
                "empty_eval": True, "config": cfg,
                "bpc_bigram_best": float("inf"), "bpc_unigram_best": float("inf"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
            }
            continue
        n_dev = n_eval // 2
        # Compute per-row bigram logp for dev + test contexts (shared across arms)
        BI_log_dev = bigram_logp_for_contexts(
            ctx_eval[:n_dev], P_bi, U, train_seen_prev,
            backoff_lambda=0.3,
        ).astype(np.float32)
        BI_log_test = bigram_logp_for_contexts(
            ctx_eval[n_dev:], P_bi, U, train_seen_prev,
            backoff_lambda=0.3,
        ).astype(np.float32)
        jr = joint_sweep_two_baselines(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            BI_log_dev, BI_log_test,
            nxt_eval[:n_dev], nxt_eval[n_dev:],
            TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["config"] = cfg
        jr["n_eval_total"] = int(n_eval)
        jr["n_held_ctx"] = int(len(ctx_full))
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] BIGRAM bpc=%.4f top1=%.4f | "
              "UNIGRAM bpc=%.4f top1=%.4f | floors bi=%.4f uni=%.4f | "
              "best_T_bi=%.4f best_L_bi=%.2f raw_T1L1=%.3f n_eval=%d" % (
                  seed, arm, jr["bpc_bigram_best"], jr["top1_bigram_best"],
                  jr["bpc_unigram_best"], jr["top1_unigram_best"],
                  jr["bigram_floor_bpc_test"], jr["unigram_floor_bpc_test"],
                  jr["best_T_bigram"], jr["best_lambda_bigram"],
                  jr["raw_bpc_at_T1_L1"], n_eval), flush=True)

    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N": N_DIM,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "W2V_TRAIN_TOKEN_BUDGET": len(w2v_train_tokens),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": "cpu",
        "encoder_meta": encoder_meta,
        "n_llm_calls": 0,
    }


# ============================================================================
# Verdict (Fix #28: per-arm metrics ONLY; PRIMARY metric = bigram-conditional)
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    by_arm_agg: Dict[str, Dict] = {}
    for arm in ARMS:
        rows = [u["by_arm"].get(arm, {}) for u in units]
        valid = [r for r in rows if r and math.isfinite(r.get("bpc_bigram_best", float("inf")))]
        if not valid:
            by_arm_agg[arm] = {"all_seeds_failed": True,
                                 "bpc_bigram_mean": float("inf"),
                                 "bpc_unigram_mean": float("inf"),
                                 "top1_bigram_mean": float("nan"),
                                 "top1_unigram_mean": float("nan")}
            continue
        bpc_bi = [r["bpc_bigram_best"] for r in valid]
        bpc_uni = [r["bpc_unigram_best"] for r in valid]
        top1_bi = [r["top1_bigram_best"] for r in valid]
        top1_uni = [r["top1_unigram_best"] for r in valid]
        mrr_bi = [r["mrr_at_10_bigram_best"] for r in valid]
        bi_floor = [r["bigram_floor_bpc_test"] for r in valid]
        uni_floor = [r["unigram_floor_bpc_test"] for r in valid]
        b_mean = float(np.mean(bpc_bi))
        b_std = float(np.std(bpc_bi))
        by_arm_agg[arm] = {
            # PRIMARY (bigram-conditional)
            "bpc_bigram_mean": round(b_mean, 4),
            "bpc_bigram_std": round(b_std, 4),
            "bpc_bigram_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_bigram_mean": round(float(np.mean(top1_bi)), 4),
            "mrr_at_10_bigram_mean": round(float(np.mean(mrr_bi)), 4),
            # SECONDARY (unigram-conditional; v1 comparability)
            "bpc_unigram_mean": round(float(np.mean(bpc_uni)), 4),
            "bpc_unigram_std": round(float(np.std(bpc_uni)), 4),
            "top1_unigram_mean": round(float(np.mean(top1_uni)), 4),
            # Floors (per-seed mean)
            "bigram_floor_mean": round(float(np.mean(bi_floor)), 4),
            "unigram_floor_mean": round(float(np.mean(uni_floor)), 4),
            # Hyperparam means (diagnostic)
            "best_T_bigram_mean": round(float(np.mean([r["best_T_bigram"] for r in valid])), 4),
            "best_lambda_bigram_mean": round(float(np.mean([r["best_lambda_bigram"] for r in valid])), 4),
            "n_valid_seeds": int(len(valid)),
            "all_seeds_failed": False,
            "config": valid[0].get("config", {}),
        }

    # ---- Pre-reg gate decisions (PRIMARY = bigram-conditional B vs A delta) ----
    a_bi = by_arm_agg["A_W2V_GOOGLE_NEWS_FAIR"]["bpc_bigram_mean"]
    b_bi = by_arm_agg["B_W2V_TEXT8_FULL_17M"]["bpc_bigram_mean"]
    c_bi = by_arm_agg["C_RANDOM_PROJECTION_FAIR"]["bpc_bigram_mean"]
    d_bi = by_arm_agg["D_CHAR_TRIGRAM_FAIR"]["bpc_bigram_mean"]

    a_uni = by_arm_agg["A_W2V_GOOGLE_NEWS_FAIR"]["bpc_unigram_mean"]
    b_uni = by_arm_agg["B_W2V_TEXT8_FULL_17M"]["bpc_unigram_mean"]

    # Arm B floor margin: B vs unigram_floor (under fair, B should be << floor)
    uni_floor_mean = by_arm_agg["B_W2V_TEXT8_FULL_17M"]["unigram_floor_mean"]
    b_floor_margin = float("nan")
    if math.isfinite(b_bi) and math.isfinite(uni_floor_mean):
        b_floor_margin = uni_floor_mean - b_bi   # positive = B BEATS floor

    leakage_delta_bi = float("nan")
    if math.isfinite(a_bi) and math.isfinite(b_bi):
        leakage_delta_bi = b_bi - a_bi

    leakage_delta_uni = float("nan")
    if math.isfinite(a_uni) and math.isfinite(b_uni):
        leakage_delta_uni = b_uni - a_uni

    # Arm A seed-CV check (HARD_FAIL_PROVENANCE if too volatile)
    a_seed_std = by_arm_agg["A_W2V_GOOGLE_NEWS_FAIR"]["bpc_bigram_std"]
    a_seed_cv_fail = math.isfinite(a_seed_std) and a_seed_std > ARM_A_SEED_CV_TOL

    # All-arms-cluster check (HARD_FAIL_REGIME)
    finite_bpc = [x for x in [a_bi, b_bi, c_bi, d_bi] if math.isfinite(x)]
    arms_cluster = (len(finite_bpc) >= 3 and
                     (max(finite_bpc) - min(finite_bpc)) < 0.10)

    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    # Convergence sentinel from arm B training meta
    b_convergence_OK_all = True
    b_training_walls = []
    for u in units:
        em_b = u.get("encoder_meta", {}).get("B", {})
        tm = em_b.get("training_meta", {})
        b_convergence_OK_all = b_convergence_OK_all and bool(
            tm.get("convergence_sentinel_OK", True))
        if "training_wall_s" in tm:
            b_training_walls.append(tm["training_wall_s"])

    # Summary line: per-arm bigram + unigram bpc + floor + delta
    arm_lines = []
    for a in ARMS:
        x = by_arm_agg[a]
        if x.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % a)
            continue
        arm_lines.append("%s=bi%.4f|uni%.4f|t1bi%.4f" % (
            a, x["bpc_bigram_mean"], x["bpc_unigram_mean"],
            x["top1_bigram_mean"]))
    summary = ("FAIR_REGIME %s | delta_bi=%.4f delta_uni=%.4f | "
                "floor_bi=%.4f floor_uni=%.4f b_floor_margin=%.4f | n_llm=%d") % (
                    " | ".join(arm_lines),
                    leakage_delta_bi if math.isfinite(leakage_delta_bi) else -999.0,
                    leakage_delta_uni if math.isfinite(leakage_delta_uni) else -999.0,
                    by_arm_agg["B_W2V_TEXT8_FULL_17M"]["bigram_floor_mean"],
                    uni_floor_mean,
                    b_floor_margin if math.isfinite(b_floor_margin) else -999.0,
                    n_llm)

    detail = {
        "by_arm_agg": by_arm_agg,
        "leakage_delta_B_minus_A_bigram": (
            round(leakage_delta_bi, 4) if math.isfinite(leakage_delta_bi) else None),
        "leakage_delta_B_minus_A_unigram": (
            round(leakage_delta_uni, 4) if math.isfinite(leakage_delta_uni) else None),
        "arm_B_floor_margin": (
            round(b_floor_margin, 4) if math.isfinite(b_floor_margin) else None),
        "arm_A_seed_std_bigram": (
            round(a_seed_std, 4) if math.isfinite(a_seed_std) else None),
        "arm_A_seed_cv_fail": bool(a_seed_cv_fail),
        "arms_cluster_within_0_10": bool(arms_cluster),
        "arm_B_convergence_OK": bool(b_convergence_OK_all),
        "arm_B_training_walls_s": b_training_walls,
        "LEAKAGE_REFUTED_DELTA": LEAKAGE_REFUTED_DELTA,
        "LEAKAGE_CONFIRMED_DELTA": LEAKAGE_CONFIRMED_DELTA,
        "ARM_B_FLOOR_MARGIN_REFUTED": ARM_B_FLOOR_MARGIN_REFUTED,
        "ARM_B_FLOOR_MARGIN_CONFIRMED": ARM_B_FLOOR_MARGIN_CONFIRMED,
        "ARM_A_SEED_CV_TOL": ARM_A_SEED_CV_TOL,
        "n_seeds": len(units),
        "n_llm_calls": int(n_llm),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "CONFIG_VERSION": CONFIG_VERSION,
        "WHAT_THIS_DOES_NOT_SHOW": (
            "This cell does NOT prove the substrate is a competitive LM in "
            "absolute terms. It does NOT eliminate ALL leakage sources (word "
            "frequency drift between google-news and text8 still applies). "
            "It does NOT replace WordSim353/SimLex external encoder benchmarks. "
            "The bigram-conditional metric is substrate's lift OVER a proper "
            "word-bigram backoff, not over an n-gram LM with smoothing or a "
            "tuned KN. If arm B is still ABOVE the unigram floor, this means "
            "the W2V text8-full encoder + substrate W still don't beat a naive "
            "baseline, which itself is informative -- not a regime failure."),
        "honest_scope": (
            "4-arm encoder-leakage FAIR-REGIME RETEST. V=20000 (5x v1) to "
            "escape unigram-floor pinning; arm B W2V trained on FULL text8 "
            "(~17M tokens, %d epochs) vs v1 100k tokens. Bigram-conditional "
            "BPC = PRIMARY metric per drill (substrate lift over word-bigram "
            "backoff). Unigram-conditional BPC reported as SECONDARY for v1 "
            "comparability. 3 seeds [7, 13, 29]. TEMP_GRID extended to 0.001 "
            "to catch sharper softmax regime. Pure numpy + gensim CPU; "
            "remote_cpu_queue." % CLEAN_W2V_EPOCHS_FULL),
        "cites": [
            "preregs/2026-06-24_substrate_encoder_leakage_fair_regime_retest_v1.md",
            "experiments/exp_substrate_clean_encoder_substrate_as_LM_v1.py",
            "experiments/exp_substrate_brain_word_level_prediction_v2_production_config.py",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    if not b_convergence_OK_all:
        return ("HARD_FAIL",
                "FAIR_REGIME HARD_FAIL_PROVENANCE: arm B training wall too short "
                "(walls=%s) -- convergence sentinel FAILED. Suspect under-converged "
                "W2V again. %s" % (b_training_walls, summary),
                detail)

    if a_seed_cv_fail:
        return ("HARD_FAIL",
                "FAIR_REGIME HARD_FAIL_PROVENANCE: arm A seed-std=%.4f > %.2f BPC "
                "tolerance. Cell methodology unstable across seeds; cannot interpret "
                "delta. %s" % (a_seed_std, ARM_A_SEED_CV_TOL, summary),
                detail)

    if arms_cluster:
        return ("HARD_FAIL",
                "FAIR_REGIME HARD_FAIL_REGIME: all 4 arms cluster within 0.10 BPC "
                "on bigram-conditional metric (range=%.4f). V=20k STILL not "
                "discriminating; ANCHOR 3 calibration needed. %s" % (
                    max(finite_bpc) - min(finite_bpc), summary),
                detail)

    # Classify leakage delta (bigram-conditional = PRIMARY)
    if not math.isfinite(leakage_delta_bi):
        return ("HARD_FAIL",
                "FAIR_REGIME HARD_FAIL: arms A or B failed to produce finite "
                "bigram-conditional bpc. %s" % summary, detail)

    leakage_refuted_delta = abs(leakage_delta_bi) < LEAKAGE_REFUTED_DELTA
    leakage_confirmed_delta = leakage_delta_bi >= LEAKAGE_CONFIRMED_DELTA
    floor_margin_refuted_ok = (math.isfinite(b_floor_margin)
                                 and b_floor_margin >= ARM_B_FLOOR_MARGIN_REFUTED)
    floor_margin_confirmed_ok = (math.isfinite(b_floor_margin)
                                   and b_floor_margin < ARM_B_FLOOR_MARGIN_CONFIRMED)

    if leakage_refuted_delta and floor_margin_refuted_ok:
        return ("HARD_PASS",
                "FAIR_REGIME HARD_PASS_LEAKAGE_REFUTED: bigram-conditional "
                "delta_bi=%.4f (< %.2f) AND arm B beats unigram floor by %.4f "
                "(>= %.2f). v1 verdict REFUTED -- the +0.44 delta was a V=4000 "
                "+ under-trained-B artifact. Substrate capability robust to "
                "encoder. %s" % (
                    leakage_delta_bi, LEAKAGE_REFUTED_DELTA,
                    b_floor_margin, ARM_B_FLOOR_MARGIN_REFUTED, summary),
                detail)

    if leakage_confirmed_delta and floor_margin_confirmed_ok:
        return ("HARD_PASS",
                "FAIR_REGIME HARD_PASS_LEAKAGE_CONFIRMED: bigram-conditional "
                "delta_bi=%.4f (>= %.2f) AND arm B still fails floor (margin=%.4f "
                "< %.2f). v1 verdict CONFIRMED on fair regime -- properly-"
                "converged clean encoder still much worse than google-news. "
                "Path C substrate-owned encoder load-bearing. %s" % (
                    leakage_delta_bi, LEAKAGE_CONFIRMED_DELTA,
                    b_floor_margin, ARM_B_FLOOR_MARGIN_CONFIRMED, summary),
                detail)

    # Default classification: MIDDLE_BAND (partial leakage or floor mismatch)
    if LEAKAGE_REFUTED_DELTA <= abs(leakage_delta_bi) < LEAKAGE_CONFIRMED_DELTA:
        return ("MIDDLE_BAND",
                "FAIR_REGIME MIDDLE_BAND: bigram-conditional delta_bi=%.4f in "
                "[%.2f, %.2f) -- partial leakage smaller than v1's +0.44 "
                "estimate. Floor margin=%.4f. Route to Research. %s" % (
                    leakage_delta_bi, LEAKAGE_REFUTED_DELTA,
                    LEAKAGE_CONFIRMED_DELTA, b_floor_margin, summary),
                detail)

    # Mixed case: delta_bi extreme but floor_margin doesn't match the canonical
    # band. Treat as MIDDLE_BAND with explicit flag.
    return ("MIDDLE_BAND",
            "FAIR_REGIME MIDDLE_BAND_MIXED: delta_bi=%.4f but floor_margin=%.4f "
            "doesn't match canonical refuted/confirmed pattern. %s" % (
                leakage_delta_bi, b_floor_margin, summary),
            detail)


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: char-trigram bipolar
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,) and set(np.unique(v).tolist()).issubset({-1.0, 1.0}), "T1 trigram"

    # T2: sparsify primitive: exactly k=round(f*dim) nonzeros, bipolar values
    E = np.random.default_rng(0).standard_normal((4, 100)).astype(np.float32)
    sp = sparsify_bipolar_np(E, 0.05)
    k_expect = max(1, int(round(0.05 * 100)))
    nnz = (sp != 0).sum(axis=1).tolist()
    assert all(n == k_expect for n in nnz), "T2 sparse nnz: got %s expected %d" % (nnz, k_expect)
    uniq = set(sp.flatten().tolist())
    assert uniq.issubset({-1.0, 0.0, 1.0}), "T2 sparse values"

    # T3: peaked-at-low-T
    peaked = np.zeros((1, 8), dtype=np.float32)
    peaked[0, 3] = 1.0
    probs = softmax_logits_with_T(peaked, 0.001)
    assert probs.max() > 0.99, "T3 peaked-at-T0.001: max=%.4f" % probs.max()

    # T4: uniform-at-high-T
    probs_hot = softmax_logits_with_T(peaked, 10.0)
    assert (probs_hot.max() - (1.0 / 8.0)) < 0.05, "T4 uniform-at-T10"

    # T5: lambda=0 reproduces unigram-only BPC
    U = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
    U_log = np.log(np.clip(U, 1e-30, 1.0))
    nxt = np.array([0, 1, 2, 0, 1])
    n_test = len(nxt)
    sub_logits = np.zeros((n_test, 5), dtype=np.float32)
    probs_sub = softmax_logits_with_T(sub_logits, 1.0)
    logp_sub = np.log(np.clip(probs_sub, 1e-30, 1.0))
    logp_lam0 = log_linear_interp_logp(logp_sub, U_log, 0.0)
    bpc_lam0 = bpc_from_logp(logp_lam0, nxt)
    bpc_uni = -float(np.mean(np.log(U[nxt]))) / math.log(2.0)
    assert abs(bpc_lam0 - bpc_uni) < 1e-4, "T5 lam=0 != unigram"

    # T6: random-projection encoder shape + sparsity
    E_rand, _ = build_E_random_projection(50, 200, seed=0)
    assert E_rand.shape == (50, 200), "T6 random shape"
    nnz_rand = (E_rand != 0).sum(axis=1).tolist()
    k_rand = max(1, int(round(SPARSE_BIPOLAR_F * 200)))
    assert all(n == k_rand for n in nnz_rand), "T6 random sparse nnz"

    # T7: char-trigram-sparse
    E_ct, _ = build_E_char_trigram_sparse(["cat", "dog", "the"], 200, seed=0)
    assert E_ct.shape == (3, 200), "T7 ct shape"
    nnz_ct = (E_ct != 0).sum(axis=1).tolist()
    assert all(n == k_rand for n in nnz_ct), "T7 ct sparse nnz"

    # T8: bigram floor build + per-row lookup
    idx_t = np.array([1, 2, 3, 1, 2, 4, 1, 3], dtype=np.int64)
    V_t = 5
    P_bi_t = build_bigram_np(idx_t, V=V_t, alpha=0.1)
    assert P_bi_t.shape == (V_t, V_t), "T8 bigram shape"
    # Row sums ~ 1
    assert np.allclose(P_bi_t.sum(axis=1), 1.0, atol=1e-5), "T8 bigram rows normalized"
    U_t = build_unigram_np(idx_t, V_t, alpha=0.1)
    train_seen_t = np.zeros(V_t, dtype=bool)
    train_seen_t[idx_t[:-1]] = True
    ctx_t = np.array([1, 2, 4], dtype=np.int64)
    bi_log = bigram_logp_for_contexts(ctx_t, P_bi_t, U_t, train_seen_t,
                                       backoff_lambda=0.3)
    assert bi_log.shape == (3, V_t), "T8 bigram_logp shape"
    # Each row should be normalized log-probs
    row_sums = np.exp(bi_log).sum(axis=1)
    assert np.allclose(row_sums, 1.0, atol=1e-5), "T8 bigram rows logp sum to 1"

    # T9: verdict gates -- HARD_PASS_LEAKAGE_REFUTED
    def _mk_unit(bpcs_bi, bpcs_uni, uni_floor=12.0, bi_floor=10.0,
                 b_train_wall=120.0, b_convergence_ok=True):
        by_arm = {}
        for arm in ARMS:
            by_arm[arm] = {
                "bpc_bigram_best": bpcs_bi[arm],
                "bpc_unigram_best": bpcs_uni[arm],
                "top1_bigram_best": 0.25, "top1_unigram_best": 0.24,
                "mrr_at_10_bigram_best": 0.35, "mrr_at_10_unigram_best": 0.34,
                "best_T_bigram": 0.05, "best_lambda_bigram": 0.3,
                "best_T_unigram": 0.05, "best_lambda_unigram": 0.3,
                "best_dev_bpc_bigram": bpcs_bi[arm],
                "best_dev_bpc_unigram": bpcs_uni[arm],
                "unigram_floor_bpc_test": uni_floor,
                "bigram_floor_bpc_test": bi_floor,
                "raw_bpc_at_T1_L1": 11.5,
                "n_dev": 100, "n_test": 100, "n_eval_total": 200,
                "n_held_ctx": 200, "elapsed_s_arm": 0.01,
                "config": ARM_CONFIG[arm],
            }
        return {"seed": 0, "by_arm": by_arm, "V": 20000, "N": 64,
                 "N_DIM": 64, "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": 20000,
                 "PRETRAIN_DIM": 10, "W2V_TRAIN_TOKEN_BUDGET": 1000,
                 "run_mode": "smoke", "config_version": "selftest",
                 "elapsed_s_seed": 0.01, "device": "cpu", "n_llm_calls": 0,
                 "encoder_meta": {"B": {"training_meta": {
                     "training_wall_s": b_train_wall,
                     "convergence_sentinel_OK": b_convergence_ok}}}}

    # HARD_PASS_LEAKAGE_REFUTED: delta_bi=0.05 (<0.10) AND b_margin=2.0 (uni_floor=12, B=10) >= 0.5
    u_refuted = _mk_unit(
        bpcs_bi={"A_W2V_GOOGLE_NEWS_FAIR": 9.95, "B_W2V_TEXT8_FULL_17M": 10.00,
                 "C_RANDOM_PROJECTION_FAIR": 11.50, "D_CHAR_TRIGRAM_FAIR": 10.40},
        bpcs_uni={"A_W2V_GOOGLE_NEWS_FAIR": 11.55, "B_W2V_TEXT8_FULL_17M": 11.60,
                  "C_RANDOM_PROJECTION_FAIR": 11.80, "D_CHAR_TRIGRAM_FAIR": 11.50},
        uni_floor=12.0, bi_floor=10.0,
    )
    v, m, d = compute_verdict([u_refuted])
    assert v == "HARD_PASS", "T9 REFUTED got %s msg=%s" % (v, m[:200])
    assert "LEAKAGE_REFUTED" in m, "T9 REFUTED msg missing tag: %s" % m[:200]

    # HARD_PASS_LEAKAGE_CONFIRMED: delta_bi=0.40 (>=0.30) AND b_margin=0.10 (uni_floor=12, B=11.9) < 0.20
    u_confirmed = _mk_unit(
        bpcs_bi={"A_W2V_GOOGLE_NEWS_FAIR": 11.50, "B_W2V_TEXT8_FULL_17M": 11.90,
                 "C_RANDOM_PROJECTION_FAIR": 11.70, "D_CHAR_TRIGRAM_FAIR": 11.40},
        bpcs_uni={"A_W2V_GOOGLE_NEWS_FAIR": 11.55, "B_W2V_TEXT8_FULL_17M": 11.95,
                  "C_RANDOM_PROJECTION_FAIR": 11.80, "D_CHAR_TRIGRAM_FAIR": 11.50},
        uni_floor=12.0, bi_floor=11.4,
    )
    v, m, d = compute_verdict([u_confirmed])
    assert v == "HARD_PASS", "T9 CONFIRMED got %s msg=%s" % (v, m[:200])
    assert "LEAKAGE_CONFIRMED" in m, "T9 CONFIRMED msg missing tag: %s" % m[:200]

    # MIDDLE_BAND_PARTIAL: delta_bi=0.20 in [0.10, 0.30)
    u_partial = _mk_unit(
        bpcs_bi={"A_W2V_GOOGLE_NEWS_FAIR": 9.80, "B_W2V_TEXT8_FULL_17M": 10.00,
                 "C_RANDOM_PROJECTION_FAIR": 11.50, "D_CHAR_TRIGRAM_FAIR": 10.40},
        bpcs_uni={"A_W2V_GOOGLE_NEWS_FAIR": 11.55, "B_W2V_TEXT8_FULL_17M": 11.75,
                  "C_RANDOM_PROJECTION_FAIR": 11.80, "D_CHAR_TRIGRAM_FAIR": 11.50},
        uni_floor=12.0, bi_floor=10.0,
    )
    v, m, _ = compute_verdict([u_partial])
    assert v == "MIDDLE_BAND", "T9 PARTIAL got %s msg=%s" % (v, m[:200])

    # HARD_FAIL_REGIME: all 4 arms within 0.05 BPC range
    u_regime = _mk_unit(
        bpcs_bi={"A_W2V_GOOGLE_NEWS_FAIR": 10.00, "B_W2V_TEXT8_FULL_17M": 10.02,
                 "C_RANDOM_PROJECTION_FAIR": 10.04, "D_CHAR_TRIGRAM_FAIR": 10.03},
        bpcs_uni={"A_W2V_GOOGLE_NEWS_FAIR": 11.55, "B_W2V_TEXT8_FULL_17M": 11.55,
                  "C_RANDOM_PROJECTION_FAIR": 11.80, "D_CHAR_TRIGRAM_FAIR": 11.50},
        uni_floor=12.0, bi_floor=10.0,
    )
    v, m, _ = compute_verdict([u_regime])
    assert v == "HARD_FAIL", "T9 REGIME got %s msg=%s" % (v, m[:200])
    assert "HARD_FAIL_REGIME" in m, "T9 REGIME msg missing tag: %s" % m[:200]

    # HARD_FAIL_PROVENANCE (convergence sentinel): training_wall_s = 2.0 (too short)
    u_underconv = _mk_unit(
        bpcs_bi={"A_W2V_GOOGLE_NEWS_FAIR": 9.95, "B_W2V_TEXT8_FULL_17M": 10.50,
                 "C_RANDOM_PROJECTION_FAIR": 11.50, "D_CHAR_TRIGRAM_FAIR": 10.40},
        bpcs_uni={"A_W2V_GOOGLE_NEWS_FAIR": 11.55, "B_W2V_TEXT8_FULL_17M": 11.60,
                  "C_RANDOM_PROJECTION_FAIR": 11.80, "D_CHAR_TRIGRAM_FAIR": 11.50},
        uni_floor=12.0, bi_floor=10.0,
        b_train_wall=2.0, b_convergence_ok=False,
    )
    v, m, _ = compute_verdict([u_underconv])
    assert v == "HARD_FAIL", "T9 UNDERCONV got %s msg=%s" % (v, m[:200])
    assert "PROVENANCE" in m, "T9 UNDERCONV msg missing tag: %s" % m[:200]

    # T10: no LLM calls
    assert _LLM_CALL_COUNTER[0] == 0, "T10 zero llm"

    # T11: extended TEMP_GRID includes 0.001
    assert 0.001 in TEMP_GRID, "T11 TEMP_GRID missing 0.001"
    assert min(TEMP_GRID) == 0.001, "T11 TEMP_GRID min should be 0.001"

    # T12: V=20000 in full config (production-binding)
    if RUN_MODE == "full":
        assert VOCAB_CAP == 20000, "T12 VOCAB_CAP must be 20000 in full"
        assert SEEDS == [7, 13, 29], "T12 SEEDS must be [7, 13, 29] in full"
        assert N_DIM == 8192, "T12 N_DIM must be 8192 in full"
        assert W2V_TRAIN_TOKEN_BUDGET >= 17_000_000, "T12 W2V budget must be >= 17M"

    print("[selftest] PASS: T1 trigram + T2 sparsify + T3 peakedT0001 + "
          "T4 uniformT10 + T5 lam0=unigram + T6 random_proj + T7 char_trigram + "
          "T8 bigram_floor + T9 verdict (REFUTED/CONFIRMED/PARTIAL/REGIME/PROVENANCE) "
          "+ T10 llm=0 + T11 TEMP_GRID + T12 fair-regime-config",
          flush=True)


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
                                     "atexit synthesize: compute_verdict failed: %s" % e,
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
            "metrics_source": "atexit_synthesize_partial_fair_regime_retest_v1",
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
          "seeds=%s arms=%s | name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
              SEEDS, ARMS, _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
                "schema": "encoder-leakage-fair-regime-retest-v1"}
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
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "W2V_TRAIN_TOKEN_BUDGET": W2V_TRAIN_TOKEN_BUDGET,
        "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH,
        "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID,
        "MRR_K": MRR_K,
        "arms": ARMS,
        "arm_config": ARM_CONFIG,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_encoder_leakage_fair_regime_retest_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate cosine logits; word2vec/clean-W2V are static open-weight lookups; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": "cpu",
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
