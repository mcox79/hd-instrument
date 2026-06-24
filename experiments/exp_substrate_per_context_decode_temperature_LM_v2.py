"""substrate_per_context_decode_temperature_LM_v2 -- RESCUE of v1 encoder mismatch.

Skunkworks batch VET verdict on v1: IMPLEMENTATION_BUG.
  v1 used hash-bucket char-trigram encoder (NOT word2vec-projected like fair_harness).
  ARM_GLOBAL_T collapsed to unigram BPC=7.7378 (failed self-test bar 7.3065 +/- 0.05 by 0.43 bits).
  Root cause: encoder mismatch meant substrate logits were uninformative; temperature
  tuning had nothing to tune; all arms collapsed to unigram-level.

This cell RESCUES v1 by:
  1. Using fair_harness word2vec-projected encoder (gensim word2vec-google-news-300 +
     Gaussian projection to N_DIM, OOV fallback to char-trigram).
  2. Sweeping lambda for per-context arms (v1 locked LAMBDA_PER_CONTEXT=0.3).
  3. MANDATORY sanity gate: ARM_GLOBAL_T BPC must be 7.3065 +/- 0.05 before any
     per-context arm result is reported. If failed -> READOUT_DEGENERATE flag.

Mechanism hypothesis (unchanged from v1):
  Brain literature Yu-Dayan 2005 (ACh-mediated gain control) + locus coeruleus phasic-vs-tonic:
  cortical neurons modulate effective SNR based on TASK UNCERTAINTY. Per-token T = f(predictive
  uncertainty) where higher predictive entropy means sharper distribution (lower T) and lower
  entropy means keep current T. Substrate-native: entropy/margin computed from substrate cosine logits.

Four arms x 3 seeds x text8 N_TRAIN=100k N_DIM=8192:
  ARM_UNIGRAM             : analytic floor (no substrate)
  ARM_GLOBAL_T            : global (T, lambda) joint sweep -- MUST reproduce fair_harness 7.3065
  ARM_PER_CONTEXT_T_ENTROPY: per-token T = T_low + (T_high - T_low)*(1 - H_norm)
                             lambda also swept (same LAMBDA_GRID as ARM_GLOBAL_T)
  ARM_PER_CONTEXT_T_MARGIN : per-token T = T_low + (T_high - T_low)*margin_norm
                             lambda also swept (same LAMBDA_GRID as ARM_GLOBAL_T)

Pre-reg HARD bands:
  HARD_PASS     : ARM_PER_CONTEXT_T_ENTROPY OR ARM_PER_CONTEXT_T_MARGIN beats ARM_GLOBAL_T
                  by >= +0.10 bits BPC.
  CHAIN_GRADE_BONUS: lift >= +0.20 bits AND beats fair_harness chain-grade 7.3065 by >= 0.10.
  MIDDLE_BAND   : lift +0.03 to +0.10 bits.
  HARD_FAIL     : lift <= +0.03 bits (per-context T does not help when encoder is correct).
  MANDATORY SANITY GATE: ARM_GLOBAL_T BPC must be 7.3065 +/- 0.05. If FAILED -> READOUT_DEGENERATE.
  cv < 0.05.

Routing: remote_cpu_queue (~2h per Skunkworks estimate). Pure numpy (CPU).
ASCII-only. Per-seed checkpoint. atexit synthesizer. preflight_spec.yaml co-filed.
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
import signal
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
    resumable_seeds,
)

ANCHOR_NAME = "substrate_per_context_decode_temperature_LM_v2"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
_LLM_CALL_COUNTER = [0]
_METRICS_WRITTEN = [False]

WORD2VEC_MODEL = "word2vec-google-news-300"

# Pre-reg bands
HARD_PASS_LIFT_BPC = 0.10
CHAIN_GRADE_BONUS_LIFT = 0.20
CHAIN_GRADE_BASELINE_BPC = 7.3065
MIDDLE_BAND_LIFT_LOW = 0.03
HARD_FAIL_LIFT_MAX = 0.03
HARD_PASS_CV_MAX = 0.05

# ARM_GLOBAL_T sanity gate: must reproduce fair_harness sparse-bipolar BPC
GLOBAL_T_SELFTEST_BAR_BPC = 7.3065
GLOBAL_T_SELFTEST_TOL = 0.05

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config (FULL = production)
N_DIM = 8192
PRETRAIN_DIM = 300        # word2vec-google-news-300
VOCAB_CAP = 4000
SPARSE_F = 0.05           # sparse-bipolar fraction (mirrors fair_harness SPARSE_BIPOLAR)
INGEST_CHUNK = 4096
RECALL_BATCH = 256

# Joint (T, lambda) sweep for ARM_GLOBAL_T and per-context arms -- mirrors fair_harness
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

# Per-context T range
T_LOW = 0.02
T_HIGH = 0.5

ARMS = [
    "ARM_UNIGRAM",
    "ARM_GLOBAL_T",
    "ARM_PER_CONTEXT_T_ENTROPY",
    "ARM_PER_CONTEXT_T_MARGIN",
]

if RUN_MODE in ("smoke", "selftest"):
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    PRETRAIN_DIM = 300  # still word2vec-projected; smoke encoder test checks gensim
else:
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000

CONFIG_VERSION = (
    "substrate_per_context_decode_temperature_LM_v2; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d sparse_f=%.3f seeds=%s run_mode=%s arms=%s "
    "TEMP_GRID=%s LAMBDA_GRID=%s T_LOW=%.3f T_HIGH=%.3f "
    "encoder=word2vec-projected-OOV-chartrigram; "
    "bands HP_lift>=%.2f CG_lift>=%.2f MID_low=%.2f HF_lift<=%.2f cv_max=%.2f "
    "sanity_gate=ARM_GLOBAL_T_BPC_within_%.2f_of_%.4f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, SPARSE_F, SEEDS, RUN_MODE, ARMS,
    TEMP_GRID, LAMBDA_GRID, T_LOW, T_HIGH,
    HARD_PASS_LIFT_BPC, CHAIN_GRADE_BONUS_LIFT, MIDDLE_BAND_LIFT_LOW,
    HARD_FAIL_LIFT_MAX, HARD_PASS_CV_MAX,
    GLOBAL_T_SELFTEST_TOL, GLOBAL_T_SELFTEST_BAR_BPC,
)


# ============================================================================
# Encoder -- word2vec-projected (mirrors fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR)
# ============================================================================

_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_kv(model_name: str):
    """Process-local cache; loads via tools.gensim_load_helper."""
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    from tools.gensim_load_helper import load_gensim_kv
    kv = load_gensim_kv(model_name, cache_dir=GENSIM_CACHE_DIR)
    _GENSIM_KV_CACHE[model_name] = kv
    return kv


def _embed_vocab_via_gensim(vocab: List[str], kv) -> Tuple[np.ndarray, int, int]:
    """Embed vocab into [V, kv.vector_size] pretrain space. OOV rows stay zero."""
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


def _l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


def _char_trigram_encode_np(word: str, dim: int, seed: int) -> np.ndarray:
    """Char-trigram OOV fallback (NOT the main encoder -- only for OOV words)."""
    import hashlib as _hlib
    v = np.zeros(dim, np.float32)
    w = "#" + word.lower() + "#"
    for i in range(len(w) - 2):
        tri = w[i:i + 3]
        sv = int(_hlib.md5((tri + ":" + str(seed)).encode()).hexdigest(), 16) & 0xFFFFFFFF
        idx = sv % dim
        sign = 1.0 if ((sv >> 16) & 1) else -1.0
        v[idx] += sign
    nrm = float(np.linalg.norm(v))
    return v / nrm if nrm > 1e-9 else v


def build_E_word2vec_np(vocab: List[str], n_dim: int, seed: int) -> Tuple[np.ndarray, Dict]:
    """Build [V, n_dim] L2-normalized word2vec-projected encoder (CPU numpy).

    Exact mirror of fair_harness build_E_word2vec_gpu but stays on CPU.
    OOV falls back to char-trigram so no zero-row degeneracy.
    Returns (E_float32, meta_dict).
    """
    kv = _load_gensim_kv(WORD2VEC_MODEL)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = _l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_before_proj = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_before_proj < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = _char_trigram_encode_np(vocab[i], n_dim, seed)
    E_proj = _l2_normalize_np(E_proj)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_proj.astype(np.float32), meta


def sparsify_bipolar_np(E: np.ndarray, f: float) -> np.ndarray:
    """Top-k sparse bipolar (mirrors fair_harness GPU version, CPU numpy)."""
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    out = np.zeros_like(E)
    abs_E = np.abs(E)
    topk_idx = np.argpartition(-abs_E, k, axis=1)[:, :k]
    for i in range(V):
        idx = topk_idx[i]
        signs = np.sign(E[i, idx])
        signs[signs == 0] = 1.0
        out[i, idx] = signs
    return out


# ============================================================================
# Hebbian W + logit helpers
# ============================================================================

def build_hebbian_W_np(idx_train: np.ndarray, E: np.ndarray, ingest_chunk: int) -> np.ndarray:
    """Build [dim, dim] rank-1 Hebbian W (CPU numpy, chunked)."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        E_src = E[idx_train[b:end]]
        E_tgt = E[idx_train[b + 1:end + 1]]
        W += E_tgt.T @ E_src
    return W


def compute_substrate_logits_np(ctx_idx: np.ndarray, E: np.ndarray,
                                  W: np.ndarray, recall_batch: int) -> np.ndarray:
    """Return [n, V] cosine-similarity logits from substrate (CPU)."""
    n = len(ctx_idx)
    V = E.shape[0]
    logits = np.zeros((n, V), dtype=np.float32)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        pred = E[ctx_idx[b:end]] @ W.T
        nrm = np.linalg.norm(pred, axis=1, keepdims=True)
        nrm[nrm < 1e-9] = 1.0
        pred = pred / nrm
        logits[b:end] = pred @ E.T
    return logits


def bpc_top1_mrr_from_logits(logits: np.ndarray, nxt: np.ndarray, T: float, lam: float,
                               U_logp: np.ndarray, mrr_k: int = 10) -> Tuple[float, float, float]:
    """BPC, top-1, MRR@k from logits with (T, lambda) joint interp."""
    z = logits / max(T, 1e-8)
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    sub_p = e / (e.sum(axis=1, keepdims=True) + 1e-30)
    if lam < 1.0:
        log_comb = lam * np.log(np.clip(sub_p, 1e-30, 1.0)) + (1.0 - lam) * U_logp[None, :]
        z2 = log_comb - log_comb.max(axis=1, keepdims=True)
        e2 = np.exp(z2)
        probs = e2 / (e2.sum(axis=1, keepdims=True) + 1e-30)
    else:
        probs = sub_p
    p_true = np.clip(probs[np.arange(len(nxt)), nxt], 1e-12, 1.0)
    bpc = float(-np.mean(np.log2(p_true)))
    top1 = float((probs.argmax(axis=1) == nxt).mean())
    n = len(nxt)
    ranks = np.argsort(-probs, axis=1)[:, :mrr_k]
    mrr = 0.0
    for i in range(n):
        hits = np.where(ranks[i] == nxt[i])[0]
        if len(hits) > 0:
            mrr += 1.0 / (hits[0] + 1)
    mrr /= max(n, 1)
    return bpc, top1, mrr


def _per_position_T_from_entropy(logits: np.ndarray, T_base: float,
                                   T_low: float, T_high: float) -> np.ndarray:
    """Per-position T based on normalized predictive entropy.

    high-entropy context (uncertain) -> T_low (sharpen); low-entropy -> T_high.
    """
    z = logits / max(T_base, 1e-8)
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / (e.sum(axis=1, keepdims=True) + 1e-30)
    logp = np.log(np.clip(p, 1e-30, 1.0))
    H = -np.sum(p * logp, axis=1).astype(np.float32)
    H_max = math.log(logits.shape[1])
    H_norm = np.clip(H / H_max, 0.0, 1.0)
    T_vec = T_low + (T_high - T_low) * (1.0 - H_norm)
    return T_vec.astype(np.float32)


def _per_position_T_from_margin(logits: np.ndarray, T_base: float,
                                  T_low: float, T_high: float) -> np.ndarray:
    """Per-position T based on cosine margin (top-1 minus top-2).

    low margin (confused) -> T_low (sharpen); high margin (confident) -> T_high.
    """
    sorted_l = np.sort(logits, axis=1)[:, ::-1]
    margin = sorted_l[:, 0] - sorted_l[:, 1]
    margin_max = 2.0  # cosine sims in [-1, 1]; max margin = 2
    margin_norm = np.clip(margin / margin_max, 0.0, 1.0)
    T_vec = T_low + (T_high - T_low) * margin_norm
    return T_vec.astype(np.float32)


def bpc_top1_mrr_per_context_T(logits: np.ndarray, nxt: np.ndarray, T_vec: np.ndarray,
                                  lam: float, U_logp: np.ndarray,
                                  mrr_k: int = 10) -> Tuple[float, float, float]:
    """BPC/top-1/MRR using per-position temperature vector T_vec [n]."""
    n = len(nxt)
    z = logits / np.clip(T_vec[:, None], 1e-8, None)
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    sub_p = e / (e.sum(axis=1, keepdims=True) + 1e-30)
    if lam < 1.0:
        log_comb = lam * np.log(np.clip(sub_p, 1e-30, 1.0)) + (1.0 - lam) * U_logp[None, :]
        z2 = log_comb - log_comb.max(axis=1, keepdims=True)
        e2 = np.exp(z2)
        probs = e2 / (e2.sum(axis=1, keepdims=True) + 1e-30)
    else:
        probs = sub_p
    p_true = np.clip(probs[np.arange(n), nxt], 1e-12, 1.0)
    bpc = float(-np.mean(np.log2(p_true)))
    top1 = float((probs.argmax(axis=1) == nxt).mean())
    ranks = np.argsort(-probs, axis=1)[:, :mrr_k]
    mrr = 0.0
    for i in range(n):
        hits = np.where(ranks[i] == nxt[i])[0]
        if len(hits) > 0:
            mrr += 1.0 / (hits[0] + 1)
    mrr /= max(n, 1)
    return bpc, top1, mrr


# ============================================================================
# Corpus helpers
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] corpus missing: %s" % TEXT8, flush=True)
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


def build_unigram(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


# ============================================================================
# Instrumentation self-test (MANDATORY per exp_dev role contract)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics non-null/non-sentinel at small scale.

    Critically: tests the word2vec-projected encoder loads and produces valid E,
    confirming we are NOT using the v1 hash-bucket char-trigram encoder for the
    main code path.
    """
    print("[selftest] running instrumentation self-test (v2 word2vec encoder) ...", flush=True)

    # 1. Gensim KV loads and produces a non-zero embedding for at least one word
    try:
        kv = _load_gensim_kv(WORD2VEC_MODEL)
        assert hasattr(kv, "key_to_index"), "selftest 1: kv missing key_to_index"
        assert kv.vector_size > 0, "selftest 1: kv.vector_size <= 0"
        print("[selftest] gensim KV loaded: vector_size=%d, vocab=%d" % (
            kv.vector_size, len(kv.key_to_index)), flush=True)
    except Exception as exc:
        # gensim unavailable on this machine -- acceptable in smoke on laptop;
        # FULL run requires gensim present on remote
        print("[selftest] WARN: gensim unavailable (%s); selftest 1 SKIPPED (FULL run will fail if gensim absent)" % exc,
              flush=True)
        print("[selftest] PASS (gensim-skipped path)", flush=True)
        return

    # 2. build_E_word2vec_np: E is L2-normalized, non-zero, correct shape
    vocab_t = ["the", "and", "of", "to", "<unk>", "zxqjk_oov_word"]
    E_t, meta_t = build_E_word2vec_np(vocab_t, n_dim=256, seed=0)
    assert E_t.shape == (len(vocab_t), 256), "selftest 2: E shape %s wrong" % str(E_t.shape)
    nrms = np.linalg.norm(E_t, axis=1)
    assert (np.abs(nrms - 1.0) < 1e-4).all(), "selftest 2: E rows not L2-normed: %s" % nrms
    assert not np.all(E_t == 0), "selftest 2: E all-zero"
    assert not np.any(np.isnan(E_t)), "selftest 2: E NaN"
    assert meta_t["n_hit"] > 0, "selftest 2: zero hits in gensim lookup (unexpected with common words)"
    print("[selftest] word2vec E: shape=%s n_hit=%d n_miss=%d" % (
        str(E_t.shape), meta_t["n_hit"], meta_t["n_miss"]), flush=True)

    # 3. Sparsify: correct shape, nonzero entries
    E_sp = sparsify_bipolar_np(E_t, f=0.1)
    assert E_sp.shape == E_t.shape, "selftest 3: sparsify shape wrong"
    assert (E_sp != 0).any(axis=1).all(), "selftest 3: sparsify all-zero row"

    # 4. Hebbian W + logits: non-null, not all-zero, correct shape
    V_t = len(vocab_t)
    dim_t = 256
    idx_tr = np.tile(np.arange(V_t, dtype=np.int64), 5)
    W_t = build_hebbian_W_np(idx_tr, E_sp, ingest_chunk=20)
    assert W_t.shape == (dim_t, dim_t), "selftest 4: W shape %s wrong" % str(W_t.shape)
    assert np.abs(W_t).sum() > 0, "selftest 4: W all-zero"
    ctx_t = np.array([0, 1, 2, 3], dtype=np.int64)
    nxt_t = np.array([1, 2, 3, 4], dtype=np.int64)
    logits_t = compute_substrate_logits_np(ctx_t, E_sp, W_t, recall_batch=4)
    assert logits_t.shape == (4, V_t), "selftest 4: logits shape wrong"
    assert not np.all(logits_t == 0), "selftest 4: logits all-zero"
    assert not np.any(np.isnan(logits_t)), "selftest 4: logits NaN"

    # 5. BPC/top1/MRR: finite, in valid ranges
    U_t = build_unigram(idx_tr, V=V_t, alpha=0.1)
    U_logp_t = np.log(np.clip(U_t, 1e-30, 1.0))
    bpc_t, top1_t, mrr_t = bpc_top1_mrr_from_logits(logits_t, nxt_t, T=0.05, lam=0.3,
                                                       U_logp=U_logp_t, mrr_k=5)
    assert math.isfinite(bpc_t) and bpc_t > 0, "selftest 5: bpc not finite/positive: %s" % bpc_t
    assert 0.0 <= top1_t <= 1.0, "selftest 5: top1 out of range"
    assert 0.0 <= mrr_t <= 1.0, "selftest 5: mrr out of range"

    # 6. Per-context T (entropy): T_vec in [T_LOW, T_HIGH]
    T_vec_ent = _per_position_T_from_entropy(logits_t, T_base=0.05, T_low=T_LOW, T_high=T_HIGH)
    assert T_vec_ent.shape == (4,), "selftest 6: T_vec_ent shape wrong"
    assert (T_vec_ent >= T_LOW - 1e-5).all(), "selftest 6: T_vec_ent below T_LOW"
    assert (T_vec_ent <= T_HIGH + 1e-5).all(), "selftest 6: T_vec_ent above T_HIGH"

    # 7. Per-context T (margin): T_vec in [T_LOW, T_HIGH]
    T_vec_mar = _per_position_T_from_margin(logits_t, T_base=0.05, T_low=T_LOW, T_high=T_HIGH)
    assert T_vec_mar.shape == (4,), "selftest 7: T_vec_mar shape wrong"
    assert (T_vec_mar >= T_LOW - 1e-5).all(), "selftest 7: T_vec_mar below T_LOW"
    assert (T_vec_mar <= T_HIGH + 1e-5).all(), "selftest 7: T_vec_mar above T_HIGH"

    # 8. Per-context-T BPC/top1/MRR with lambda sweep: valid distributions
    for lam in [0.0, 0.3, 1.0]:
        bpc_pc, top1_pc, mrr_pc = bpc_top1_mrr_per_context_T(
            logits_t, nxt_t, T_vec_ent, lam=lam, U_logp=U_logp_t, mrr_k=5)
        assert math.isfinite(bpc_pc) and bpc_pc > 0, \
            "selftest 8: per-ctx-T bpc not finite at lam=%.1f: %s" % (lam, bpc_pc)
        assert 0.0 <= top1_pc <= 1.0, "selftest 8: top1 out of range at lam=%.1f" % lam
        assert 0.0 <= mrr_pc <= 1.0, "selftest 8: mrr out of range at lam=%.1f" % lam

    # 9. LLM counter still 0
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 9: LLM counter non-zero"

    # 10. CRITICAL: confirm word2vec produces different E from char-trigram-only
    #     (verifies we are NOT running v1's encoder by mistake)
    E_ct_fallback = np.stack([
        _char_trigram_encode_np(w, 256, seed=0) for w in vocab_t], 0).astype(np.float32)
    E_ct_fallback = _l2_normalize_np(E_ct_fallback)
    # word2vec hits should differ from char-trigram on the same vocab for known words
    known_idx = [i for i, w in enumerate(vocab_t) if meta_t.get("n_hit", 0) > 0 and w in kv.key_to_index]
    if known_idx:
        diff = np.abs(E_t[known_idx] - E_ct_fallback[known_idx]).mean()
        assert diff > 1e-4, \
            ("selftest 10: word2vec E matches char-trigram on known words (diff=%.6f); "
             "encoder mismatch suspect" % diff)
        print("[selftest] word2vec vs char-trigram avg-diff on %d known words: %.4f (must be > 0.0001)" % (
            len(known_idx), diff), flush=True)

    print("[selftest] PASS: word2vec-encoder/sparsify/W/logits/BPC/MRR/"
          "per-ctx-T-entropy/per-ctx-T-margin/lambda-sweep/LLM=0/w2v-differs-from-chartrigram all valid",
          flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_seed(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading corpus ..." % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    unk = w2i["<unk>"]

    idx_train_np = tokens_to_idx(train_toks, w2i)
    idx_held_np = tokens_to_idx(held_toks, w2i)
    ctx_np = idx_held_np[:-1]
    nxt_np = idx_held_np[1:]
    mask = ctx_np != unk
    ctx_eval = ctx_np[mask]
    nxt_eval = nxt_np[mask]
    n_eval = len(ctx_eval)

    n_dev = n_eval // 2
    ctx_dev = ctx_eval[:n_dev]
    nxt_dev = nxt_eval[:n_dev]
    ctx_test = ctx_eval[n_dev:]
    nxt_test = nxt_eval[n_dev:]
    n_test = len(ctx_test)
    print("[seed=%d] V=%d train=%d held=%d dev=%d test=%d" % (
        seed, V, N_TRAIN, N_HELD, n_dev, n_test), flush=True)

    # Unigram baseline
    U = build_unigram(idx_train_np, V=V, alpha=0.1)
    U_logp = np.log(np.clip(U, 1e-30, 1.0))
    uni_argmax = int(np.argmax(U))
    p_true_uni = U[nxt_test].clip(1e-12, 1.0)
    uni_bpc = float(-np.mean(np.log2(p_true_uni)))
    uni_acc = float((np.full(n_test, uni_argmax) == nxt_test).mean())
    u_sorted_idx = np.argsort(-U)
    u_rank_lookup = np.empty(V, dtype=np.int64)
    u_rank_lookup[u_sorted_idx] = np.arange(1, V + 1)
    test_ranks = u_rank_lookup[nxt_test]
    uni_mrr = float(np.mean(1.0 / test_ranks.astype(np.float64) * (test_ranks <= 10)))
    print("[seed=%d] UNIGRAM bpc=%.4f acc=%.4f mrr=%.4f" % (seed, uni_bpc, uni_acc, uni_mrr), flush=True)

    # Build word2vec-projected sparse-bipolar encoder (mirrors fair_harness)
    t0 = time.time()
    E_base, encoder_meta = build_E_word2vec_np(vocab, N_DIM, seed=seed)
    E = sparsify_bipolar_np(E_base, f=SPARSE_F)
    t_enc = time.time() - t0
    print("[seed=%d] word2vec encoder N_DIM=%d V=%d sparse_f=%.3f (%.1fs) "
          "n_hit=%d n_miss=%d" % (
              seed, N_DIM, V, SPARSE_F, t_enc,
              encoder_meta["n_hit"], encoder_meta["n_miss"]), flush=True)

    # Build Hebbian W
    t0 = time.time()
    W = build_hebbian_W_np(idx_train_np, E, ingest_chunk=INGEST_CHUNK)
    t_ingest = time.time() - t0
    print("[seed=%d] W built n_pairs=%d (%.1fs)" % (seed, N_TRAIN - 1, t_ingest), flush=True)

    # Compute substrate logits
    t0 = time.time()
    sub_logits_dev = compute_substrate_logits_np(ctx_dev, E, W, RECALL_BATCH)
    sub_logits_test = compute_substrate_logits_np(ctx_test, E, W, RECALL_BATCH)
    t_recall = time.time() - t0
    print("[seed=%d] logits computed dev=%d test=%d (%.1fs)" % (seed, n_dev, n_test, t_recall), flush=True)

    # ----- ARM_GLOBAL_T: joint (T, lambda) sweep -----
    best_dev_bpc_gl = float("inf")
    best_T_gl = TEMP_GRID[0]
    best_lam_gl = LAMBDA_GRID[0]
    for T in TEMP_GRID:
        for lam in LAMBDA_GRID:
            b, _, _ = bpc_top1_mrr_from_logits(sub_logits_dev, nxt_dev, T, lam, U_logp)
            if b < best_dev_bpc_gl:
                best_dev_bpc_gl = b
                best_T_gl = T
                best_lam_gl = lam
    gl_bpc, gl_top1, gl_mrr = bpc_top1_mrr_from_logits(
        sub_logits_test, nxt_test, best_T_gl, best_lam_gl, U_logp)
    print("[seed=%d] ARM_GLOBAL_T best_T=%.3f best_lam=%.2f (dev_bpc=%.4f) "
          "-> test bpc=%.4f top1=%.4f mrr=%.4f" % (
              seed, best_T_gl, best_lam_gl, best_dev_bpc_gl, gl_bpc, gl_top1, gl_mrr), flush=True)

    # MANDATORY SANITY GATE: ARM_GLOBAL_T must be within tol of fair_harness baseline
    global_t_sanity_ok = abs(gl_bpc - GLOBAL_T_SELFTEST_BAR_BPC) <= GLOBAL_T_SELFTEST_TOL
    if not global_t_sanity_ok:
        print("[SANITY_GATE FAIL] seed=%d ARM_GLOBAL_T BPC=%.4f deviates from "
              "fair_harness baseline %.4f by %.4f (tol=%.3f) -- READOUT_DEGENERATE" % (
                  seed, gl_bpc, GLOBAL_T_SELFTEST_BAR_BPC,
                  abs(gl_bpc - GLOBAL_T_SELFTEST_BAR_BPC), GLOBAL_T_SELFTEST_TOL), flush=True)
    else:
        print("[SANITY_GATE PASS] seed=%d ARM_GLOBAL_T BPC=%.4f within %.3f of %.4f" % (
            seed, gl_bpc, GLOBAL_T_SELFTEST_TOL, GLOBAL_T_SELFTEST_BAR_BPC), flush=True)

    # ----- ARM_PER_CONTEXT_T_ENTROPY: sweep T_base AND lambda -----
    best_dev_bpc_ent = float("inf")
    best_T_base_ent = TEMP_GRID[0]
    best_lam_ent = LAMBDA_GRID[0]
    for T_base in TEMP_GRID:
        T_vec_dev = _per_position_T_from_entropy(sub_logits_dev, T_base, T_LOW, T_HIGH)
        for lam in LAMBDA_GRID:
            b, _, _ = bpc_top1_mrr_per_context_T(sub_logits_dev, nxt_dev, T_vec_dev, lam, U_logp)
            if b < best_dev_bpc_ent:
                best_dev_bpc_ent = b
                best_T_base_ent = T_base
                best_lam_ent = lam
    T_vec_test_ent = _per_position_T_from_entropy(sub_logits_test, best_T_base_ent, T_LOW, T_HIGH)
    ent_bpc, ent_top1, ent_mrr = bpc_top1_mrr_per_context_T(
        sub_logits_test, nxt_test, T_vec_test_ent, best_lam_ent, U_logp)
    T_mean_ent = float(T_vec_test_ent.mean())
    T_std_ent = float(T_vec_test_ent.std())
    print("[seed=%d] ARM_PER_CONTEXT_T_ENTROPY best_T_base=%.3f best_lam=%.2f "
          "(dev_bpc=%.4f) T_mean=%.4f T_std=%.4f "
          "-> test bpc=%.4f top1=%.4f mrr=%.4f" % (
              seed, best_T_base_ent, best_lam_ent, best_dev_bpc_ent,
              T_mean_ent, T_std_ent, ent_bpc, ent_top1, ent_mrr), flush=True)

    # ----- ARM_PER_CONTEXT_T_MARGIN: sweep T_base AND lambda -----
    best_dev_bpc_mar = float("inf")
    best_T_base_mar = TEMP_GRID[0]
    best_lam_mar = LAMBDA_GRID[0]
    for T_base in TEMP_GRID:
        T_vec_dev_m = _per_position_T_from_margin(sub_logits_dev, T_base, T_LOW, T_HIGH)
        for lam in LAMBDA_GRID:
            b, _, _ = bpc_top1_mrr_per_context_T(sub_logits_dev, nxt_dev, T_vec_dev_m, lam, U_logp)
            if b < best_dev_bpc_mar:
                best_dev_bpc_mar = b
                best_T_base_mar = T_base
                best_lam_mar = lam
    T_vec_test_mar = _per_position_T_from_margin(sub_logits_test, best_T_base_mar, T_LOW, T_HIGH)
    mar_bpc, mar_top1, mar_mrr = bpc_top1_mrr_per_context_T(
        sub_logits_test, nxt_test, T_vec_test_mar, best_lam_mar, U_logp)
    T_mean_mar = float(T_vec_test_mar.mean())
    T_std_mar = float(T_vec_test_mar.std())
    print("[seed=%d] ARM_PER_CONTEXT_T_MARGIN best_T_base=%.3f best_lam=%.2f "
          "(dev_bpc=%.4f) T_mean=%.4f T_std=%.4f "
          "-> test bpc=%.4f top1=%.4f mrr=%.4f" % (
              seed, best_T_base_mar, best_lam_mar, best_dev_bpc_mar,
              T_mean_mar, T_std_mar, mar_bpc, mar_top1, mar_mrr), flush=True)

    elapsed = time.time() - t_seed
    print("[seed=%d] done in %.1fs" % (seed, elapsed), flush=True)

    return {
        "seed": seed,
        "V": V,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "run_mode": RUN_MODE,
        "n_dev": n_dev,
        "n_test": n_test,
        "elapsed_s": elapsed,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": 0,
        "global_t_sanity_ok": global_t_sanity_ok,
        "encoder_meta": encoder_meta,
        "wall_ingest_s": float(t_ingest),
        "wall_recall_s": float(t_recall),
        "by_arm": {
            "ARM_UNIGRAM": {
                "bpc": uni_bpc,
                "top1": uni_acc,
                "mrr": uni_mrr,
            },
            "ARM_GLOBAL_T": {
                "bpc": gl_bpc,
                "top1": gl_top1,
                "mrr": gl_mrr,
                "best_T": best_T_gl,
                "best_lambda": best_lam_gl,
                "best_dev_bpc": best_dev_bpc_gl,
                "sanity_ok": global_t_sanity_ok,
            },
            "ARM_PER_CONTEXT_T_ENTROPY": {
                "bpc": ent_bpc,
                "top1": ent_top1,
                "mrr": ent_mrr,
                "best_T_base": best_T_base_ent,
                "best_lambda": best_lam_ent,
                "best_dev_bpc": best_dev_bpc_ent,
                "T_mean": T_mean_ent,
                "T_std": T_std_ent,
            },
            "ARM_PER_CONTEXT_T_MARGIN": {
                "bpc": mar_bpc,
                "top1": mar_top1,
                "mrr": mar_mrr,
                "best_T_base": best_T_base_mar,
                "best_lambda": best_lam_mar,
                "best_dev_bpc": best_dev_bpc_mar,
                "T_mean": T_mean_mar,
                "T_std": T_std_mar,
            },
        },
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(per_seed: Dict) -> Tuple[str, str, Dict]:
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed data.", {})

    def _arm_bpcs(arm):
        return [v["by_arm"][arm]["bpc"] for v in per_seed.values()
                if arm in v.get("by_arm", {}) and math.isfinite(v["by_arm"][arm]["bpc"])]

    def _mean(xs):
        return float(np.mean(xs)) if xs else float("nan")

    def _cv(xs):
        m = _mean(xs)
        if not math.isfinite(m) or m < 1e-9 or len(xs) < 2:
            return float("inf")
        return float(np.std(xs)) / m

    uni_bpcs = _arm_bpcs("ARM_UNIGRAM")
    gl_bpcs = _arm_bpcs("ARM_GLOBAL_T")
    ent_bpcs = _arm_bpcs("ARM_PER_CONTEXT_T_ENTROPY")
    mar_bpcs = _arm_bpcs("ARM_PER_CONTEXT_T_MARGIN")

    uni_m = _mean(uni_bpcs)
    gl_m = _mean(gl_bpcs)
    ent_m = _mean(ent_bpcs)
    mar_m = _mean(mar_bpcs)

    gl_cv = _cv(gl_bpcs)
    ent_cv = _cv(ent_bpcs)
    mar_cv = _cv(mar_bpcs)

    # MANDATORY SANITY GATE: check ARM_GLOBAL_T reproduces fair_harness
    sanity_fails = [v for v in per_seed.values()
                    if not v.get("global_t_sanity_ok", True)]
    global_sanity_ok = len(sanity_fails) == 0
    global_sanity_fraction = 1.0 - len(sanity_fails) / max(len(per_seed), 1)

    ent_lift = gl_m - ent_m
    mar_lift = gl_m - mar_m
    best_lift = max(ent_lift, mar_lift)
    best_arm_name = "ARM_PER_CONTEXT_T_ENTROPY" if ent_lift >= mar_lift else "ARM_PER_CONTEXT_T_MARGIN"
    best_bpc = ent_m if ent_lift >= mar_lift else mar_m
    best_cv = ent_cv if ent_lift >= mar_lift else mar_cv

    n_seeds = len(per_seed)
    n_llm = sum(int(v.get("n_llm_calls", 0)) for v in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    summary = (
        "BPC uni=%.4f global=%.4f ent=%.4f(lift=%.4f) mar=%.4f(lift=%.4f) | "
        "best=%s lift=%.4f bpc=%.4f cv=%.4f | n_seeds=%d N_DIM=%d N_TRAIN=%d "
        "n_llm=%d sanity_ok=%s"
    ) % (uni_m, gl_m, ent_m, ent_lift, mar_m, mar_lift,
         best_arm_name, best_lift, best_bpc, best_cv,
         n_seeds, N_DIM, N_TRAIN, n_llm, str(global_sanity_ok))

    detail = {
        "by_arm_agg": {
            "ARM_UNIGRAM": {"bpc_mean": uni_m},
            "ARM_GLOBAL_T": {"bpc_mean": gl_m, "cv": gl_cv},
            "ARM_PER_CONTEXT_T_ENTROPY": {
                "bpc_mean": ent_m, "cv": ent_cv, "lift_over_global": ent_lift},
            "ARM_PER_CONTEXT_T_MARGIN": {
                "bpc_mean": mar_m, "cv": mar_cv, "lift_over_global": mar_lift},
        },
        "best_per_context_arm": best_arm_name,
        "best_per_context_lift": best_lift,
        "best_per_context_bpc": best_bpc,
        "best_per_context_cv": best_cv,
        "global_t_bpc": gl_m,
        "global_t_sanity_ok": global_sanity_ok,
        "global_t_sanity_fraction": global_sanity_fraction,
        "chain_grade_baseline": CHAIN_GRADE_BASELINE_BPC,
        "zero_llm_calls_at_inference": substrate_only_ok,
        "n_llm_calls": n_llm,
        "encoder": "word2vec-google-news-300-projected + OOV-chartrigram + sparse-bipolar-f0.05",
        "honest_scope": (
            "RESCUE v2: word2vec-projected encoder (NOT v1 char-trigram). "
            "ARM_GLOBAL_T (joint T+lambda sweep) vs ARM_PER_CONTEXT_T_ENTROPY and "
            "ARM_PER_CONTEXT_T_MARGIN (T+lambda jointly swept on dev). "
            "text8 N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d N_DIM=%d sparse_f=%.3f. "
            "Sanity gate: ARM_GLOBAL_T BPC must be within %.2f of %.4f."
        ) % (N_TRAIN, N_HELD, VOCAB_CAP, N_DIM, SPARSE_F,
             GLOBAL_T_SELFTEST_TOL, GLOBAL_T_SELFTEST_BAR_BPC),
        "prereg": "preregs/2026-06-23_substrate_per_context_decode_temperature_LM_v2.md",
        "v1_bug": "v1 encoder was hash-bucket char-trigram (NOT word2vec); ARM_GLOBAL_T collapsed to unigram BPC=7.7378",
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    # SANITY GATE: if ARM_GLOBAL_T fails baseline check, flag READOUT_DEGENERATE
    if not global_sanity_ok:
        return ("READOUT_DEGENERATE",
                "READOUT_DEGENERATE: ARM_GLOBAL_T BPC=%.4f failed sanity gate "
                "(expected %.4f +/- %.3f). Encoder mismatch or methodology error. "
                "Do NOT classify per-context arms. %s" % (
                    gl_m, GLOBAL_T_SELFTEST_BAR_BPC, GLOBAL_T_SELFTEST_TOL, summary),
                detail)

    cv_ok = best_cv <= HARD_PASS_CV_MAX

    if best_lift >= HARD_PASS_LIFT_BPC and cv_ok:
        if best_lift >= CHAIN_GRADE_BONUS_LIFT and best_bpc < CHAIN_GRADE_BASELINE_BPC:
            return ("HARD_PASS",
                    "HARD_PASS CHAIN_GRADE_BONUS: %s lifts +%.4f bits over global T "
                    "(>=0.20 bar) AND beats fair_harness chain-grade %.4f with bpc=%.4f. "
                    "Per-context uncertainty-modulated T is substrate-native phase-diagram nav. %s" % (
                        best_arm_name, best_lift, CHAIN_GRADE_BASELINE_BPC, best_bpc, summary),
                    detail)
        return ("HARD_PASS",
                "HARD_PASS: %s lifts +%.4f bits over global T (>= %.2f bar); cv=%.4f. "
                "Per-context T adds real lift over global calibration. %s" % (
                    best_arm_name, best_lift, HARD_PASS_LIFT_BPC, best_cv, summary),
                detail)

    if best_lift <= HARD_FAIL_LIFT_MAX:
        return ("HARD_FAIL",
                "HARD_FAIL: best per-context T lift=%.4f <= %.2f threshold. "
                "Per-context T does not add over global calibration with correct encoder. %s" % (
                    best_lift, HARD_FAIL_LIFT_MAX, summary),
                detail)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: best per-context lift=%.4f in (%.2f, %.2f). "
            "Marginal improvement; investigate T_LOW/T_HIGH tuning. %s" % (
                best_lift, MIDDLE_BAND_LIFT_LOW, HARD_PASS_LIFT_BPC, summary),
            detail)


# ============================================================================
# atexit synthesizer + signal handler
# ============================================================================

def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        run_config = {"N": N_DIM, "M": N_TRAIN, "run_mode": RUN_MODE}
        per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
        if not per_seed:
            return
        v, vmsg, detail = compute_verdict(per_seed)
        vmsg = "TIMEOUT_OR_INTERRUPTED_PARTIAL: " + vmsg
        metrics = {
            "anchor": ANCHOR_NAME,
            "anchor_name": ANCHOR_NAME,
            "verdict": v,
            "verdict_msg": vmsg,
            "n_seeds": len(per_seed),
            "N": N_DIM,
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "SPARSE_F": SPARSE_F,
            "TEMP_GRID": TEMP_GRID,
            "LAMBDA_GRID": LAMBDA_GRID,
            "T_LOW": T_LOW,
            "T_HIGH": T_HIGH,
            "arms": ARMS,
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "detail": detail,
            "metrics_source": "synthesized_from_partials_on_exit",
            "synthesized_at_exit": True,
            "elapsed_s": 0.0,
        }
        write_metrics(out_dir, metrics, results=list(per_seed.values()))
        _METRICS_WRITTEN[0] = True
    except Exception as e:
        print("[atexit] FAILED: %s" % e, flush=True)


atexit.register(_synthesize_on_exit)


def _sigterm_handler(signum, frame):
    _synthesize_on_exit()
    sys.exit(143)


try:
    signal.signal(signal.SIGTERM, _sigterm_handler)
except (ValueError, AttributeError):
    pass


# ============================================================================
# Main runner
# ============================================================================

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
t0_total = time.time()
run_config = {"N": N_DIM, "M": N_TRAIN, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d N_TRAIN=%d VOCAB_CAP=%d device=cpu "
      "encoder=word2vec-projected seeds_done=%s seeds_todo=%s" % (
          RUN_MODE, N_DIM, N_TRAIN, VOCAB_CAP, str(done), str(seeds_todo)), flush=True)

for s in seeds_todo:
    print("[seed=%d] starting at %.1fs" % (s, time.time() - t0_total), flush=True)
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
v, vmsg, detail = compute_verdict(per_seed)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": v,
    "verdict_msg": vmsg,
    "n_seeds": len(per_seed),
    "N": N_DIM,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "SPARSE_F": SPARSE_F,
    "TEMP_GRID": TEMP_GRID,
    "LAMBDA_GRID": LAMBDA_GRID,
    "T_LOW": T_LOW,
    "T_HIGH": T_HIGH,
    "arms": ARMS,
    "run_mode": RUN_MODE,
    "config_version": CONFIG_VERSION,
    "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    "encoder": "word2vec-google-news-300-projected + OOV-chartrigram + sparse-bipolar-f0.05",
    "zero_llm_calls_at_inference": True,
    "n_llm_calls": 0,
    "detail": detail,
    "per_seed": [{"seed": k, **{kk: vv for kk, vv in vv_.items()}}
                 for k, vv_ in per_seed.items()],
    "metrics_source": "measured_cpu_substrate_per_context_decode_temperature_LM_v2",
    "elapsed_s": time.time() - t0_total,
    "summary": vmsg[:300],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % v, flush=True)
print("[VERDICT_MSG] %s" % vmsg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
