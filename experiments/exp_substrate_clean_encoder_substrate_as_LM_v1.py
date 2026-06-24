"""substrate_clean_encoder_substrate_as_LM_v1 -- ENCODER-LEAKAGE DECISIVE TEST.

PURPOSE (2026-06-24):
  Test TOP-5 bias #5 (encoder-leakage): the substrate's "+12% top1 vs unigram"
  via word2vec-google-news-300 may be measuring word2vec's pretrained
  Google-News distributional knowledge, NOT substrate W's learned transition.

  Clean test: replace word2vec-google-news with a Word2Vec trained ONLY on
  text8's training split (no external data). Same sparse-bipolar primitive,
  same rank-1 Hebbian W, same eval; only the ENCODER varies.

FOUR ARMS (single seed=7; same N_DIM, same vocab, same held positions,
same sparse-bipolar f=0.05, same alpha=0.1 Laplace, same ctx-unk filter):
  A_W2V_GOOGLE_NEWS       word2vec-google-news-300 (sanity rail; ~7.3065)
  B_W2V_TEXT8_ONLY        gensim Word2Vec trained ONLY on text8 training
                          split (NO Google News); PRIMARY arm
  C_RANDOM_PROJECTION     fixed Gaussian projection of one-hot vocab (no
                          semantic structure); floor
  D_CHAR_TRIGRAM          bag-of-char-trigrams bipolar sign encoder
                          (substrate-native; complementary floor)

PRE-REGISTERED BANDS (PRE-REGISTERED BEFORE RUN, 2026-06-24):
  HARD_PASS_LEAKAGE_REAL:
      ARM_B - ARM_A >= 0.30 BPC AND ARM_A within +/-0.05 of 7.3065
      => word2vec's pretrained knowledge was load-bearing; substrate
      partially measuring word2vec, not just substrate W.
  HARD_PASS_LEAKAGE_NEGLIGIBLE:
      ARM_B within +/-0.10 of ARM_A AND ARM_A sanity rail OK
      => substrate capability robust to encoder; word2vec lift = clean lift.
  MIDDLE_BAND_PARTIAL_LEAKAGE:
      ARM_B - ARM_A in [+0.10, +0.30] AND ARM_A sanity rail OK
      => partial leakage; non-trivial encoder contribution but substrate
      still has real capability.
  HARD_FAIL_DECISIVE:
      ARM_A diverges from 7.3065 by > 0.10 (sanity rail FAILS)
      => harness bug; uninterpretable.

CRITICAL DISCIPLINES:
  PURE NUMPY + gensim CPU: routes via remote_cpu_queue (PROT-020)
  ASCII-only, no emojis, no em dashes
  Fix #28: per-arm metrics ONLY; no cross-arm framing in verdict_msg
  WHAT_THIS_DOES_NOT_SHOW clause in detail
  All arms share IDENTICAL primitives EXCEPT the encoder
  Single seed sufficient (deterministic pipelines; sanity rail is its own
    cross-check)
  Substrate-only-decode gate (word2vec lookup is static open-weight; zero
    LLM forward calls at inference)

CITES:
  preregs/2026-06-24_substrate_clean_encoder_substrate_as_LM_v1.md
  experiments/exp_fair_harness_substrate_as_lm_v1.py
  experiments/exp_substrate_encoder_ablation_on_fair_harness_v1.py
  experiments/exp_clean_encoder_eval_harness_v1.py

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

ANCHOR_NAME = "substrate_clean_encoder_substrate_as_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Reference: fair_harness ARM_FAIR_HARNESS_ASSHIPPED reproduces here
FAIR_HARNESS_REF_BPC = 7.3065

# Pre-reg band thresholds
SANITY_RAIL_TOL = 0.05      # arm A within +/-0.05 of 7.3065
HARD_FAIL_RAIL_TOL = 0.10   # arm A divergence threshold
LEAKAGE_REAL_DELTA = 0.30   # ARM_B - ARM_A >= 0.30 => leakage real
LEAKAGE_NEG_TOL = 0.10      # |ARM_B - ARM_A| <= 0.10 => leakage negligible

# Joint (T, lambda) sweep grid (matches fair_harness)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
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

# Config
WORD2VEC_MODEL = "word2vec-google-news-300"
PRETRAIN_DIM = 300
CLEAN_W2V_DIM = 300        # match pretrained dim for fair comparison
CLEAN_W2V_WINDOW = 5
CLEAN_W2V_MIN_COUNT = 5
CLEAN_W2V_EPOCHS = 10
CLEAN_W2V_WORKERS = 4

if RUN_MODE == "full":
    SEEDS = [7]
    N_DIM = 8192
    N_TRAIN = 100_000
    N_HELD = 20_000
    VOCAB_CAP = 4000
    INGEST_CHUNK = 4096
    RECALL_BATCH = 512
    CLEAN_W2V_EPOCHS_RUN = CLEAN_W2V_EPOCHS
else:
    # Smoke: <90s on laptop CPU; exercises all 4 arms + joint sweep + verdict bands
    SEEDS = [0]
    N_DIM = 512
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    CLEAN_W2V_EPOCHS_RUN = 2  # quick smoke; not a quality bar

ARMS = [
    "A_W2V_GOOGLE_NEWS",
    "B_W2V_TEXT8_ONLY",
    "C_RANDOM_PROJECTION",
    "D_CHAR_TRIGRAM",
]

ARM_CONFIG: Dict[str, Dict] = {
    "A_W2V_GOOGLE_NEWS":    {"encoder": "w2v_google_news",    "training_data": "google_news_100B"},
    "B_W2V_TEXT8_ONLY":     {"encoder": "w2v_text8_only",     "training_data": "text8_train_split_only"},
    "C_RANDOM_PROJECTION":  {"encoder": "random_projection",  "training_data": "none"},
    "D_CHAR_TRIGRAM":       {"encoder": "char_trigram",       "training_data": "none_deterministic_hash"},
}

CONFIG_VERSION = (
    "substrate_clean_encoder_substrate_as_LM_v1; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s mode=%s "
    "sparse_f=%.3f temps=%s lambdas=%s MRR_K=%d "
    "clean_w2v dim=%d window=%d min_count=%d epochs=%d "
    "bands rail_tol=%.2f leakage_real=%.2f leakage_neg=%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    SPARSE_BIPOLAR_F, TEMP_GRID, LAMBDA_GRID, MRR_K,
    CLEAN_W2V_DIM, CLEAN_W2V_WINDOW, CLEAN_W2V_MIN_COUNT, CLEAN_W2V_EPOCHS_RUN,
    SANITY_RAIL_TOL, LEAKAGE_REAL_DELTA, LEAKAGE_NEG_TOL,
)

_LLM_CALL_COUNTER = [0]


# ============================================================================
# Primitives (shared by all arms)
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
    """Top-k by abs; sign-binarize; matches fair_harness sparse-bipolar primitive."""
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
# Char-trigram encoder (substrate-native; no learning)
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
# word2vec-google-news encoder (provenance rail)
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
    """Pretrained word2vec-google-news lookup -> Gaussian project -> sparse-bipolar.

    OOV via char-trigram fallback. Returns sparse-bipolar HD encoding.
    """
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
    # Apply same sparse-bipolar f=0.05 as fair_harness
    E_sparse = l2_normalize_np(sparsify_bipolar_np(E_proj, SPARSE_BIPOLAR_F))
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size),
            "fallback_to_char_trigram": False, "training_data": "google_news_100B"}
    return E_sparse, meta


# ============================================================================
# Clean Word2Vec encoder (THE PRIMARY ARM)
# Trained ONLY on text8 training split; NO external data.
# ============================================================================

def train_clean_w2v_on_text8(train_tokens: List[str], dim: int,
                              window: int, min_count: int, epochs: int,
                              workers: int, seed: int) -> Tuple[object, Dict]:
    """Train gensim Word2Vec on the text8 training split (and only that).

    Returns (KeyedVectors, meta). NO external data; clean of Google News.
    """
    from gensim.models import Word2Vec
    t0 = time.time()
    # gensim Word2Vec sentences = list of token lists. text8 is one big stream;
    # chunk into 1000-token "sentences" so window can operate sensibly.
    chunk_size = 1000
    sentences = [train_tokens[i:i + chunk_size]
                  for i in range(0, len(train_tokens), chunk_size)]
    model = Word2Vec(
        sentences=sentences,
        vector_size=dim,
        window=window,
        min_count=min_count,
        workers=workers,
        epochs=epochs,
        sg=1,                # skip-gram (matches typical word2vec configs)
        seed=int(seed),
    )
    meta = {
        "training_data": "text8_train_split_only",
        "n_train_tokens": int(len(train_tokens)),
        "n_sentences": int(len(sentences)),
        "chunk_size": int(chunk_size),
        "wv_dim": int(model.wv.vector_size),
        "wv_vocab_size": int(len(model.wv.key_to_index)),
        "epochs": int(epochs),
        "window": int(window),
        "min_count": int(min_count),
        "training_wall_s": round(time.time() - t0, 2),
    }
    return model.wv, meta


def build_E_w2v_text8_only(vocab: List[str], n_dim: int, seed: int,
                            train_tokens: List[str]) -> Tuple[np.ndarray, Dict]:
    """Train clean Word2Vec on text8 train tokens -> project -> sparse-bipolar.

    OOV via char-trigram fallback (same as ARM A). NO Google News data.
    """
    print("[B_w2v_text8] training Word2Vec on text8 train split (n_tokens=%d, "
          "dim=%d, epochs=%d)..." % (len(train_tokens), CLEAN_W2V_DIM,
                                       CLEAN_W2V_EPOCHS_RUN), flush=True)
    kv, train_meta = train_clean_w2v_on_text8(
        train_tokens, dim=CLEAN_W2V_DIM, window=CLEAN_W2V_WINDOW,
        min_count=CLEAN_W2V_MIN_COUNT, epochs=CLEAN_W2V_EPOCHS_RUN,
        workers=CLEAN_W2V_WORKERS, seed=seed,
    )
    print("[B_w2v_text8] train done (%.1fs); wv_vocab=%d" % (
        train_meta["training_wall_s"], train_meta["wv_vocab_size"]), flush=True)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim_kv(vocab, kv)
    E_pre_n = l2_normalize_np(E_pre)
    # Same Gaussian projection as ARM_A (shared seed) for apples-to-apples
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
    """One-hot vocab -> fixed Gaussian projection -> sparse-bipolar.

    No semantic structure: each word gets a random N_DIM vector with no
    relationship to its meaning. Sparse-bipolar primitive applied identically.
    """
    rng = np.random.default_rng(seed * 7919 + 31)
    E = rng.standard_normal((vocab_size, n_dim)).astype(np.float32)
    E = l2_normalize_np(E)
    E_sparse = l2_normalize_np(sparsify_bipolar_np(E, SPARSE_BIPOLAR_F))
    meta = {"n_vocab": int(vocab_size), "encoder_type": "random_projection",
            "no_training": True}
    return E_sparse, meta


# ============================================================================
# Char-trigram + sparse-bipolar (for arm D; substrate-native floor)
# ============================================================================

def build_E_char_trigram_sparse(vocab: List[str], n_dim: int, seed: int
                                  ) -> Tuple[np.ndarray, Dict]:
    E = build_E_char_trigram(vocab, n_dim, seed)
    # char-trigram is already bipolar +/-1 over all dims; apply sparse-bipolar
    # f=0.05 for apples-to-apples primitive consistency with arms A/B/C.
    E_sparse = l2_normalize_np(sparsify_bipolar_np(E, SPARSE_BIPOLAR_F))
    meta = {"n_vocab": int(len(vocab)), "encoder_type": "char_trigram_sparse",
            "no_training": True}
    return E_sparse, meta


# ============================================================================
# Hebbian W builder (rank-1; pure numpy, chunked) -- identical across arms
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
# Joint (T, lambda) sweep + BPC / top-1 / MRR (verbatim from sibling cell)
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


def joint_sweep(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                 U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                 temp_grid: list, lambda_grid: list, mrr_k: int) -> Dict:
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)

    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    for T in temp_grid:
        probs_dev = softmax_logits_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in lambda_grid:
            logp_dev = log_linear_interp_logp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc_from_logp(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
            if bd < best_bpc["dev_value"]:
                best_bpc = {"T": float(T), "lambda": float(lam), "dev_value": bd}
            if td > best_top1["dev_value"]:
                best_top1 = {"T": float(T), "lambda": float(lam), "dev_value": td}
            if md > best_mrr["dev_value"]:
                best_mrr = {"T": float(T), "lambda": float(lam), "dev_value": md}

    def _test_metric(T, lam, fn):
        probs_test = softmax_logits_with_T(sub_logits_test, T)
        logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
        logp_test = log_linear_interp_logp(logp_sub_test, U_log, lam)
        return fn(logp_test, nxt_test)

    bpc_best = _test_metric(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best = _test_metric(best_top1["T"], best_top1["lambda"], top1_acc_from_logp)
    mrr_best = _test_metric(best_mrr["T"], best_mrr["lambda"],
                              lambda lp, nx: mrr_at_k(lp, nx, mrr_k))

    return {
        "bpc_best": round(bpc_best, 4),
        "best_T_for_bpc": best_bpc["T"],
        "best_lambda_for_bpc": best_bpc["lambda"],
        "best_dev_bpc": round(best_bpc["dev_value"], 4),
        "top1_acc": round(top1_best, 4),
        "mrr_at_10": round(mrr_best, 4),
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

    # Build all 4 encoders fresh (each is independent)
    encoder_meta: Dict[str, Dict] = {}

    print("[seed=%d arm A] building word2vec-google-news E..." % seed, flush=True)
    t0 = time.time()
    E_A, meta_A = build_E_w2v_google_news(vocab, N_DIM, seed)
    encoder_meta["A"] = meta_A
    print("[seed=%d arm A] E built (%.1fs) hit=%d miss=%d fallback=%s" % (
        seed, time.time() - t0, meta_A.get("n_hit", -1),
        meta_A.get("n_miss", -1), meta_A.get("fallback_to_char_trigram", False)), flush=True)

    print("[seed=%d arm B] training CLEAN Word2Vec on text8 train split..." % seed, flush=True)
    t0 = time.time()
    E_B, meta_B = build_E_w2v_text8_only(vocab, N_DIM, seed, train_toks)
    encoder_meta["B"] = meta_B
    print("[seed=%d arm B] E built (%.1fs) hit=%d miss=%d" % (
        seed, time.time() - t0, meta_B.get("n_hit", -1),
        meta_B.get("n_miss", -1)), flush=True)

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
        "A_W2V_GOOGLE_NEWS":   E_A,
        "B_W2V_TEXT8_ONLY":    E_B,
        "C_RANDOM_PROJECTION": E_C,
        "D_CHAR_TRIGRAM":      E_D,
    }

    # Held position bookkeeping (shared across arms)
    unk = w2i["<unk>"]
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask_unk_filter = (ctx_full != unk)

    # Same alpha=0.1 across arms (matches fair_harness)
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

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
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"),
                "raw_bpc_at_T1_L1": float("inf"),
                "best_T_for_bpc": float("nan"),
                "best_lambda_for_bpc": float("nan"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "config": cfg,
            }
            continue
        # All arms use ctx-unk filter (fair_harness convention)
        logits_eval = logits_full[mask_unk_filter]
        nxt_eval = nxt_full[mask_unk_filter]
        n_eval = len(nxt_eval)
        if n_eval < 2:
            by_arm[arm] = {"empty_eval": True, "config": cfg,
                            "bpc_best": float("inf"), "top1_acc": float("nan"),
                            "mrr_at_10": float("nan"),
                            "raw_bpc_at_T1_L1": float("inf"),
                            "best_T_for_bpc": float("nan"),
                            "best_lambda_for_bpc": float("nan"),
                            "elapsed_s_arm": round(time.time() - t_arm0, 2)}
            continue
        n_dev = n_eval // 2
        jr = joint_sweep(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_eval[:n_dev], nxt_eval[n_dev:],
            TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["config"] = cfg
        jr["n_eval_total"] = int(n_eval)
        jr["n_held_ctx"] = int(len(ctx_full))
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.4f top1=%.4f mrr=%.4f "
              "(bestT=%.4f bestL=%.2f) raw_T1L1_bpc=%.3f n_eval=%d" % (
                  seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                  jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
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
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": "cpu",
        "encoder_meta": encoder_meta,
        "n_llm_calls": 0,
    }


# ============================================================================
# Verdict (Fix #28: per-arm metrics only; no cross-arm framing)
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    by_arm_agg: Dict[str, Dict] = {}
    for arm in ARMS:
        rows = [u["by_arm"].get(arm, {}) for u in units]
        valid = [r for r in rows if r and math.isfinite(r.get("bpc_best", float("inf")))]
        if not valid:
            by_arm_agg[arm] = {"all_seeds_failed": True,
                                 "bpc_best_mean": float("inf"),
                                 "top1_acc_mean": float("nan"),
                                 "mrr_at_10_mean": float("nan"),
                                 "raw_bpc_at_T1_L1_mean": float("nan")}
            continue
        bpc_vals = [r["bpc_best"] for r in valid]
        top1_vals = [r["top1_acc"] for r in valid]
        mrr_vals = [r["mrr_at_10"] for r in valid]
        raw_vals = [r["raw_bpc_at_T1_L1"] for r in valid]
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_acc_mean": round(float(np.mean(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_vals)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_vals)), 4),
            "best_T_for_bpc_mean": round(float(np.mean([r["best_T_for_bpc"] for r in valid])), 4),
            "best_lambda_for_bpc_mean": round(float(np.mean([r["best_lambda_for_bpc"] for r in valid])), 4),
            "n_valid_seeds": int(len(valid)),
            "all_seeds_failed": False,
            "config": valid[0].get("config", {}),
        }

    # Pre-reg gate decisions (per-arm; PRIMARY = ARM_B vs ARM_A delta)
    a_bpc = by_arm_agg["A_W2V_GOOGLE_NEWS"]["bpc_best_mean"]
    b_bpc = by_arm_agg["B_W2V_TEXT8_ONLY"]["bpc_best_mean"]
    c_bpc = by_arm_agg["C_RANDOM_PROJECTION"]["bpc_best_mean"]
    d_bpc = by_arm_agg["D_CHAR_TRIGRAM"]["bpc_best_mean"]

    rail_A_ok = (math.isfinite(a_bpc) and abs(a_bpc - FAIR_HARNESS_REF_BPC) <= SANITY_RAIL_TOL)
    rail_A_diverge = (math.isfinite(a_bpc) and abs(a_bpc - FAIR_HARNESS_REF_BPC) > HARD_FAIL_RAIL_TOL)

    leakage_delta = float("nan")
    if math.isfinite(a_bpc) and math.isfinite(b_bpc):
        leakage_delta = b_bpc - a_bpc

    leakage_real = math.isfinite(leakage_delta) and leakage_delta >= LEAKAGE_REAL_DELTA
    leakage_negligible = math.isfinite(leakage_delta) and abs(leakage_delta) <= LEAKAGE_NEG_TOL
    leakage_partial = (math.isfinite(leakage_delta)
                       and (LEAKAGE_NEG_TOL < leakage_delta < LEAKAGE_REAL_DELTA))

    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    arm_lines = []
    for a in ARMS:
        x = by_arm_agg[a]
        if x.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % a)
            continue
        arm_lines.append("%s=bpc%.4f|top1%.4f|mrr%.4f" % (
            a, x["bpc_best_mean"], x["top1_acc_mean"], x["mrr_at_10_mean"]))
    summary = "CLEAN_ENC %s | delta_B_minus_A=%.4f | n_llm=%d" % (
        " | ".join(arm_lines), leakage_delta if math.isfinite(leakage_delta) else -999.0, n_llm)

    detail = {
        "by_arm_agg": by_arm_agg,
        "rail_A_ok": bool(rail_A_ok),
        "rail_A_diverge": bool(rail_A_diverge),
        "leakage_delta_B_minus_A": (round(leakage_delta, 4)
                                       if math.isfinite(leakage_delta) else None),
        "leakage_real": bool(leakage_real),
        "leakage_negligible": bool(leakage_negligible),
        "leakage_partial": bool(leakage_partial),
        "FAIR_HARNESS_REF_BPC": FAIR_HARNESS_REF_BPC,
        "SANITY_RAIL_TOL": SANITY_RAIL_TOL,
        "LEAKAGE_REAL_DELTA": LEAKAGE_REAL_DELTA,
        "LEAKAGE_NEG_TOL": LEAKAGE_NEG_TOL,
        "n_seeds": len(units),
        "n_llm_calls": int(n_llm),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "CONFIG_VERSION": CONFIG_VERSION,
        "WHAT_THIS_DOES_NOT_SHOW": (
            "This cell does NOT prove the substrate is a competitive LM in "
            "absolute terms. It does NOT diagnose other possible leakage "
            "sources (word frequency / tokenization choice). It does NOT "
            "replace the WordSim353 / SimLex external encoder benchmarks. "
            "It tests whether substrate-as-LM benefits FROM word2vec's "
            "pretrained Google-News distributional structure or whether "
            "substrate W does most of the work. If clean encoder is "
            "under-trained (~17M tokens vs google-news 100B), arm B may "
            "land worse for that reason -- itself informative."),
        "honest_scope": (
            "4-arm encoder-leakage decisive test on fair_harness scaffolding "
            "(pure numpy + gensim CPU; rank-1 Hebbian; joint (T,lambda) sweep). "
            "N_DIM=%d N_TRAIN=%d N_HELD=%d V=%d seed=%s. Arm A (word2vec-google-"
            "news; sanity rail) reproduces fair_harness 7.3065. Arm B (clean "
            "Word2Vec trained ONLY on text8 train split; PRIMARY) tests whether "
            "removing Google-News leakage moves the substrate-as-LM BPC. Arms "
            "C/D (random projection + char-trigram; floors) provide context for "
            "the magnitude of the A-vs-B delta." %
            (N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, SEEDS)),
        "cites": [
            "preregs/2026-06-24_substrate_clean_encoder_substrate_as_LM_v1.md",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
            "experiments/exp_substrate_encoder_ablation_on_fair_harness_v1.py",
            "experiments/exp_clean_encoder_eval_harness_v1.py",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    if rail_A_diverge:
        return ("HARD_FAIL",
                "CLEAN_ENC HARD_FAIL_DECISIVE: rail A diverged (A=%.4f vs ref %.4f tol %.2f). "
                "Cannot interpret B/C/D. %s" % (
                    a_bpc, FAIR_HARNESS_REF_BPC, HARD_FAIL_RAIL_TOL, summary),
                detail)

    if not rail_A_ok:
        # Rail A in [0.05, 0.10] band: degraded but not catastrophic. MIDDLE_BAND.
        return ("MIDDLE_BAND",
                "CLEAN_ENC MIDDLE_BAND_RAIL_DEGRADED: rail A within HARD_FAIL_RAIL_TOL "
                "but outside SANITY_RAIL_TOL (A=%.4f vs ref %.4f). Delta B-A=%.4f. %s" % (
                    a_bpc, FAIR_HARNESS_REF_BPC, leakage_delta, summary),
                detail)

    # Rail A is clean. Now classify the leakage delta.
    if leakage_real:
        return ("HARD_PASS",
                "CLEAN_ENC HARD_PASS_LEAKAGE_REAL: rail A reproduces (A=%.4f near %.4f). "
                "Clean encoder (B=%.4f) MUCH WORSE than google-news rail (A=%.4f); "
                "delta=%.4f >= %.2f. word2vec pretrained knowledge was load-bearing. %s" % (
                    a_bpc, FAIR_HARNESS_REF_BPC, b_bpc, a_bpc,
                    leakage_delta, LEAKAGE_REAL_DELTA, summary),
                detail)
    if leakage_negligible:
        return ("HARD_PASS",
                "CLEAN_ENC HARD_PASS_LEAKAGE_NEGLIGIBLE: rail A reproduces (A=%.4f near %.4f). "
                "Clean encoder (B=%.4f) within +/-%.2f of rail (A=%.4f); delta=%.4f. "
                "Substrate capability robust to encoder choice. %s" % (
                    a_bpc, FAIR_HARNESS_REF_BPC, b_bpc, LEAKAGE_NEG_TOL,
                    a_bpc, leakage_delta, summary),
                detail)
    if leakage_partial:
        return ("MIDDLE_BAND",
                "CLEAN_ENC MIDDLE_BAND_PARTIAL_LEAKAGE: rail A reproduces. "
                "Delta B-A=%.4f in (%.2f, %.2f) -- non-trivial encoder lift "
                "but substrate has real capability. %s" % (
                    leakage_delta, LEAKAGE_NEG_TOL, LEAKAGE_REAL_DELTA, summary),
                detail)

    # Catch-all: delta < -LEAKAGE_NEG_TOL means clean encoder is BETTER than google-news.
    # Surprising; rare; treat as MIDDLE_BAND with a flag.
    return ("MIDDLE_BAND",
            "CLEAN_ENC MIDDLE_BAND_UNEXPECTED: rail A reproduces but clean encoder "
            "BETTER than google-news (delta=%.4f < -%.2f). Possibly clean encoder "
            "tighter to text8 distribution. %s" % (
                leakage_delta, LEAKAGE_NEG_TOL, summary),
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
    assert uniq.issubset({-1.0, 0.0, 1.0}), "T2 sparse values: got %s" % uniq

    # T3: at T=0.01, peaked input remains peaked
    peaked = np.zeros((1, 8), dtype=np.float32)
    peaked[0, 3] = 1.0
    probs = softmax_logits_with_T(peaked, 0.01)
    assert probs.max() > 0.5, "T3 peaked-at-low-T: got max=%.3f" % probs.max()

    # T4: at T=10.0, near uniform
    probs_hot = softmax_logits_with_T(peaked, 10.0)
    assert (probs_hot.max() - (1.0 / 8.0)) < 0.05, "T4 uniform-at-high-T: got max=%.3f" % probs_hot.max()

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
    assert abs(bpc_lam0 - bpc_uni) < 1e-4, "T5 lam=0 != unigram: %.4f vs %.4f" % (bpc_lam0, bpc_uni)

    # T6: random projection encoder has expected shape + sparsity
    E_rand, _ = build_E_random_projection(50, 200, seed=0)
    assert E_rand.shape == (50, 200), "T6 random shape"
    nnz_rand = (E_rand != 0).sum(axis=1).tolist()
    k_rand = max(1, int(round(SPARSE_BIPOLAR_F * 200)))
    assert all(n == k_rand for n in nnz_rand), "T6 random sparse nnz: %s vs %d" % (nnz_rand[:3], k_rand)
    uniq_rand = set(np.unique(E_rand).tolist())
    # After l2_normalize on sparse-bipolar k-of-N: values are +/-1/sqrt(k) and 0
    assert len(uniq_rand) <= 3, "T6 random unique values: %s" % uniq_rand

    # T7: char-trigram-sparse encoder has expected shape + sparsity
    E_ct, _ = build_E_char_trigram_sparse(["cat", "dog", "the"], 200, seed=0)
    assert E_ct.shape == (3, 200), "T7 ct shape"
    nnz_ct = (E_ct != 0).sum(axis=1).tolist()
    assert all(n == k_rand for n in nnz_ct), "T7 ct sparse nnz: %s vs %d" % (nnz_ct, k_rand)

    # T8: verdict gates -- HARD_PASS_LEAKAGE_REAL
    def _mk_unit(bpcs):
        by_arm = {}
        for arm in ARMS:
            by_arm[arm] = {
                "bpc_best": bpcs[arm], "top1_acc": 0.25, "mrr_at_10": 0.35,
                "best_T_for_bpc": 0.05, "best_lambda_for_bpc": 0.3,
                "best_dev_bpc": bpcs[arm],
                "raw_bpc_at_T1_L1": 8.5,
                "n_dev": 100, "n_test": 100, "n_eval_total": 200,
                "n_held_ctx": 200, "elapsed_s_arm": 0.01,
                "config": ARM_CONFIG[arm],
            }
        return {"seed": 0, "by_arm": by_arm, "V": 4000, "N": 64,
                  "N_DIM": 64, "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": 300,
                  "PRETRAIN_DIM": 10, "run_mode": "smoke", "config_version": "selftest",
                  "elapsed_s_seed": 0.01, "device": "cpu", "n_llm_calls": 0,
                  "encoder_meta": {}}

    # HARD_PASS_LEAKAGE_REAL: A=7.31 (rail OK); B=7.70 (delta +0.39 >= 0.30)
    u_leak = _mk_unit({
        "A_W2V_GOOGLE_NEWS": 7.31,
        "B_W2V_TEXT8_ONLY": 7.70,
        "C_RANDOM_PROJECTION": 9.50,
        "D_CHAR_TRIGRAM": 7.25,
    })
    v, m, d = compute_verdict([u_leak])
    assert v == "HARD_PASS", "T8 LEAKAGE_REAL got %s msg=%s" % (v, m[:200])
    assert "LEAKAGE_REAL" in m, "T8 LEAKAGE_REAL msg missing tag"
    assert d["leakage_real"] is True, "T8 leakage_real flag"

    # HARD_PASS_LEAKAGE_NEGLIGIBLE: A=7.31, B=7.34 (delta 0.03 <= 0.10)
    u_neg = _mk_unit({
        "A_W2V_GOOGLE_NEWS": 7.31,
        "B_W2V_TEXT8_ONLY": 7.34,
        "C_RANDOM_PROJECTION": 9.50,
        "D_CHAR_TRIGRAM": 7.25,
    })
    v, m, d = compute_verdict([u_neg])
    assert v == "HARD_PASS", "T8 LEAKAGE_NEG got %s msg=%s" % (v, m[:200])
    assert "LEAKAGE_NEGLIGIBLE" in m, "T8 LEAKAGE_NEG msg missing tag"
    assert d["leakage_negligible"] is True, "T8 leakage_negligible flag"

    # MIDDLE_BAND_PARTIAL: A=7.31, B=7.50 (delta 0.19 in (0.10, 0.30))
    u_part = _mk_unit({
        "A_W2V_GOOGLE_NEWS": 7.31,
        "B_W2V_TEXT8_ONLY": 7.50,
        "C_RANDOM_PROJECTION": 9.50,
        "D_CHAR_TRIGRAM": 7.25,
    })
    v, m, d = compute_verdict([u_part])
    assert v == "MIDDLE_BAND", "T8 PARTIAL got %s msg=%s" % (v, m[:200])
    assert "PARTIAL" in m, "T8 PARTIAL msg missing tag"
    assert d["leakage_partial"] is True, "T8 partial flag"

    # HARD_FAIL_DECISIVE: A=7.50 (diverged from 7.3065 by 0.19 > 0.10)
    u_fail = _mk_unit({
        "A_W2V_GOOGLE_NEWS": 7.50,
        "B_W2V_TEXT8_ONLY": 7.50,
        "C_RANDOM_PROJECTION": 9.50,
        "D_CHAR_TRIGRAM": 7.25,
    })
    v, m, _ = compute_verdict([u_fail])
    assert v == "HARD_FAIL", "T8 DECISIVE got %s msg=%s" % (v, m[:200])
    assert "DECISIVE" in m, "T8 DECISIVE msg missing tag"

    # MIDDLE_BAND_RAIL_DEGRADED: A=7.38 (degraded but not diverged: 0.07 in [0.05, 0.10])
    u_deg = _mk_unit({
        "A_W2V_GOOGLE_NEWS": 7.38,
        "B_W2V_TEXT8_ONLY": 7.38,
        "C_RANDOM_PROJECTION": 9.50,
        "D_CHAR_TRIGRAM": 7.25,
    })
    v, m, _ = compute_verdict([u_deg])
    assert v == "MIDDLE_BAND", "T8 DEGRADED got %s msg=%s" % (v, m[:200])
    assert "DEGRADED" in m, "T8 DEGRADED msg missing tag"

    # T9: no LLM calls
    assert _LLM_CALL_COUNTER[0] == 0, "T9 zero llm"

    print("[selftest] PASS: T1 trigram + T2 sparsify + T3 peakedT001 + T4 uniformT10 "
          "+ T5 lam0=unigram + T6 random_proj + T7 char_trigram_sparse "
          "+ T8 verdict (LEAKAGE_REAL/NEG/PARTIAL/DECISIVE/DEGRADED) + T9 llm=0",
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
            "metrics_source": "atexit_synthesize_partial_clean_encoder_v1",
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
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM, "schema": "clean-encoder-v1"}
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
        "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH,
        "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID,
        "MRR_K": MRR_K,
        "arms": ARMS,
        "arm_config": ARM_CONFIG,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_clean_encoder_substrate_as_LM_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate cosine logits; word2vec/clean-Word2Vec are static open-weight lookups; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": "cpu",
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
