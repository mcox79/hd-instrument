"""substrate_brain_word_level_prediction_v2_production_config -- v1 rescue at production config.

v1 HARD_FAILed (S_K5 top1=0.201 vs B2 word-bigram 0.243). BUT v1 was config-degraded:
char-trigram-meanpool encoder + N_DIM=2048. ALL substrate arms collapsed to identical
metrics matching B1 word-unigram because the joint sweep picked lambda_star=0.0 (i.e.
"substrate logits useless; ignore them, use unigram alone"). top1_raw was ~0.02
(essentially random), proving the v1 substrate had no signal at all.

This rescue runs the SAME 5-arm word-grain protocol but at production-config:
  - Encoder: word2vec-google-news-300 -> Gaussian projection to N_DIM=8192 -> sparse-bipolar f=0.05
  - N_DIM: 8192 (vs 2048 in v1)
  - LAMBDA_GRID: excludes 0.0 (META C7; lambda=0 lets substrate "cheat" by zero-weighting itself)
  - GPU: torch.cuda matmul (Fix #24)
  - Per-arm BPW + top1; verdict bands UNCHANGED vs v1 prereg

Discriminates config-confound from genuine word-grain failure:
  - HARD_PASS at production -> word-grain reframe valid; glass-box LM has a real path
  - HARD_FAIL at production -> deeper LM gap; drill what next

5 arms x 3 seeds x text8 V_word=4000:
  B1   word-unigram (sanity floor)
  B2   word-bigram (THE real threshold)
  S_K1  substrate K=1 word context
  S_K5  substrate K=5 word context (PRIMARY)
  S_K10 substrate K=10 word context

Pre-reg HARD bands (same as v1):
  HARD_PASS:   S_K5 top1 >= 1.30 * B2_top1 AND S_K5 BPW <= B2_BPW - 0.4 bits
  MIDDLE_BAND: top1 in [1.10x, 1.30x] B2 OR BPW margin in [B2-0.4, B2-0.1]
  HARD_FAIL:   S_K5 top1 <= B2 OR BPW >= B2

Cites:
  experiments/exp_substrate_brain_word_level_prediction_v1.py (parent; HARD_FAIL config-degraded)
  experiments/exp_fair_harness_substrate_as_lm_v1.py (production-config GPU template)
  preregs/2026-06-24_substrate_brain_word_level_prediction_v2_production_config.md
  feedback_clean_encoder_tests_no_contamination_USER_2026-06-23
  feedback_smoke_clean_synthetic_data_not_substrate_state_USER_2026-06-23
  feedback_fix24_gpu_dispatch_must_actually_use_gpu_USER_2026-06-22
  feedback_fix28_verify_per_arm_metrics_not_summary_verdict_text_2026-06-22

ASCII-only. Per-seed checkpoint. Fix #17 elapsed_s. Fix #28 per-arm metrics.
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
import hashlib
import math
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_brain_word_level_prediction_v2_production_config"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
WORD2VEC_MODEL = "word2vec-google-news-300"

# ----------------------------------------------------------------------------
# Pre-reg bands (same as v1; rescue tests config not bands)
# ----------------------------------------------------------------------------
HP_TOP1_LIFT = 1.30          # S_K5 top1 >= 1.30 * B2_top1
HP_BPW_MARGIN = 0.4          # S_K5 BPW <= B2_BPW - 0.4
MID_TOP1_LIFT = 1.10
MID_BPW_MARGIN_LOW = 0.1
MID_BPW_MARGIN_HIGH = 0.4

# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else \
           os.environ.get("HDLAB_RUN_MODE", "full")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# ----------------------------------------------------------------------------
# Config: FULL vs smoke
# ----------------------------------------------------------------------------
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN_WORDS = 200_000
    N_HELD_WORDS = 20_000
    VOCAB_CAP = 4000
    N_DIM = 8192                # PRODUCTION (v1 was 2048)
    TEMP_GRID = [0.05, 0.1, 0.2, 0.5, 1.0]
    # META C7: exclude lambda=0.0; lambda=0 lets sweep ignore substrate by
    # zero-weighting it (v1 collapse mode). Substrate must contribute >0 weight.
    LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7]
    CONTEXT_K_VALUES = [1, 5, 10]
    SPARSE_BIPOLAR_F = 0.05     # PRODUCTION sparse-bipolar density
    INGEST_CHUNK = 4096
else:
    # Smoke: synthetic Zipfian + small config. <180s on laptop CPU.
    # No gensim load attempt in smoke (falls back to char-trigram for sanity-only).
    SEEDS = [0]
    N_TRAIN_WORDS = 8_000
    N_HELD_WORDS = 2_000
    VOCAB_CAP = 400
    N_DIM = 512
    TEMP_GRID = [0.1, 0.5, 1.0]
    LAMBDA_GRID = [0.1, 0.5]    # also excludes 0.0 (C7)
    CONTEXT_K_VALUES = [1, 5, 10]
    SPARSE_BIPOLAR_F = 0.05
    INGEST_CHUNK = 512

ARMS = ["B1_word_unigram", "B2_word_bigram"] + \
       [f"S_K{k}" for k in CONTEXT_K_VALUES]

CONFIG_VERSION = (
    "substrate_brain_word_level_prediction_v2_production_config; mode=%s "
    "seeds=%s N_TRAIN=%d N_HELD=%d V=%d N_DIM=%d K=%s temps=%s lambdas=%s "
    "sparse_f=%.3f device=%s encoder=word2vec->proj->sparse_bipolar "
    "HP_TOP1_LIFT=%.2f HP_BPW_MARGIN=%.2f"
) % (RUN_MODE, SEEDS, N_TRAIN_WORDS, N_HELD_WORDS, VOCAB_CAP, N_DIM,
     CONTEXT_K_VALUES, TEMP_GRID, LAMBDA_GRID, SPARSE_BIPOLAR_F, str(DEVICE),
     HP_TOP1_LIFT, HP_BPW_MARGIN)


# ============================================================================
# Char-trigram fallback encoder (OOV + smoke when gensim unavailable)
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"),
                        digest_size=4).digest()
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


def _l2_normalize_np(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _l2_normalize_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    if X.dim() == 1:
        return X / (X.norm() + eps)
    return X / (X.norm(dim=1, keepdim=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


# ============================================================================
# word2vec -> projection -> sparse-bipolar encoder
# ============================================================================

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


def sparsify_bipolar_gpu(E: torch.Tensor, f: float, seed: int) -> torch.Tensor:
    """Top-k absolute -> bipolar sign; sparse density f."""
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    abs_E = E.abs()
    _, topk_idx = torch.topk(abs_E, k=k, dim=1)
    out = torch.zeros_like(E)
    row_idx = torch.arange(V, device=E.device).unsqueeze(1).expand(-1, k)
    signs = torch.sign(E.gather(1, topk_idx))
    signs = torch.where(signs == 0, torch.ones_like(signs), signs)
    out[row_idx, topk_idx] = signs
    return out


def build_E_production(vocab: List[str], n_dim: int, seed: int
                         ) -> Tuple[torch.Tensor, Dict]:
    """Build [V, n_dim] sparse-bipolar encoder via word2vec -> Gaussian-proj -> top-k sparsify.

    Production config (Fix #24 GPU). Falls back to char-trigram in smoke if gensim
    fails to load (keeps smoke path functional; production fails loudly if word2vec
    missing).
    """
    encoder_meta: Dict = {}
    if RUN_MODE == "smoke":
        # Smoke: skip gensim, use char-trigram so smoke runs everywhere.
        E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
        E_np = _l2_normalize_np(E_np)
        E_t = torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)
        E_sparse = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F, seed))
        encoder_meta = {"smoke_fallback": "char_trigram_then_sparse_bipolar",
                        "n_hit": 0, "n_miss": 0, "n_vocab": len(vocab),
                        "pretrain_dim": 0, "sparse_f": SPARSE_BIPOLAR_F}
        return E_sparse, encoder_meta

    # FULL: production word2vec -> projection -> sparse-bipolar
    kv = _load_gensim_kv(WORD2VEC_MODEL)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = _l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_before_proj = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_before_proj < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = _l2_normalize_np(E_proj)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    # Sparsify to bipolar at f=0.05 (production VSA primitive)
    E_sparse = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F, seed))
    encoder_meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
                    "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size),
                    "sparse_f": SPARSE_BIPOLAR_F,
                    "n_oov_filled_via_chartrigram": int(oov_mask.sum())}
    return E_sparse, encoder_meta


# ============================================================================
# HRR bind + lock-in position vectors (GPU)
# ============================================================================

def hrr_bind_batch_gpu(A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
    if not A.is_contiguous():
        A = A.contiguous()
    if not B.is_contiguous():
        B = B.contiguous()
    Fa = torch.fft.rfft(A, dim=-1)
    Fb = torch.fft.rfft(B, dim=-1)
    return torch.fft.irfft(Fa * Fb, n=A.shape[-1], dim=-1)


def lock_in_position_vec_gpu(n_dim: int, pos: int, seed: int) -> torch.Tensor:
    rng = np.random.default_rng(seed * 7919 + 13 + pos * 101)
    phase = rng.uniform(0.0, 2.0 * math.pi, size=n_dim).astype(np.float32)
    freq = float(max(pos, 1) * 31) / float(n_dim)
    t = np.arange(n_dim, dtype=np.float32)
    v = np.cos(2.0 * math.pi * freq * t + phase).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-12)
    return torch.from_numpy(v).to(device=DEVICE, dtype=TORCH_DTYPE)


def build_context_keys_gpu(idx_t: torch.Tensor, E: torch.Tensor, K: int,
                            seed: int) -> torch.Tensor:
    """For each position i in idx, sum_j bind(E[idx[i-j]], pos_j). L2-norm."""
    n = idx_t.shape[0]
    dim = E.shape[1]
    pos_vecs = [lock_in_position_vec_gpu(dim, j, seed) for j in range(K)]
    keys = torch.zeros((n, dim), dtype=TORCH_DTYPE, device=E.device)
    for j in range(K):
        if j == 0:
            src = E[idx_t]
        else:
            shifted = torch.roll(idx_t, shifts=j, dims=0)
            shifted[:j] = idx_t[0]
            src = E[shifted]
        pos_b = pos_vecs[j].unsqueeze(0).expand(n, -1).contiguous()
        bound = hrr_bind_batch_gpu(src, pos_b)
        keys.add_(bound)
    return _l2_normalize_t(keys)


# ============================================================================
# Hebbian accumulator W (rank-1)
# ============================================================================

def build_W_rank1_gpu(keys_train: torch.Tensor, idx_next: torch.Tensor,
                       V: int) -> torch.Tensor:
    """A[v] = sum_{i: idx_next[i]==v} keys_train[i]; returns [V, dim] L2-norm."""
    dim = keys_train.shape[1]
    A = torch.zeros((V, dim), dtype=TORCH_DTYPE, device=keys_train.device)
    A.index_add_(0, idx_next, keys_train)
    return _l2_normalize_t(A)


# ============================================================================
# Corpus / vocab
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] text8 corpus missing at %s" % TEXT8, flush=True)
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


def synthetic_zipfian_tokens(n_total: int, vocab_size: int, seed: int) -> List[str]:
    """CLEAN synthetic Zipfian corpus for smoke (per USER 2026-06-23: clean smoke,
    NOT substrate state)."""
    rng = np.random.default_rng(seed)
    ranks = np.arange(1, vocab_size + 1, dtype=np.float64)
    weights = 1.0 / np.power(ranks, 1.1)
    weights = weights / weights.sum()
    idx = rng.choice(vocab_size, size=n_total, p=weights)
    return ["w%04d" % i for i in idx]


def build_vocab(train_tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    c = Counter(train_tokens)
    top = [w for w, _ in c.most_common(cap - 1)]
    vocab = ["<unk>"] + top
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_idx(toks: List[str], w2i: Dict[str, int]) -> np.ndarray:
    unk = w2i["<unk>"]
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


# ============================================================================
# B1 word-unigram + B2 word-bigram (add-alpha + backoff)
# ============================================================================

def build_unigram(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


def build_bigram(idx_train: np.ndarray, V: int, alpha: float = 0.1
                  ) -> Tuple[np.ndarray, np.ndarray]:
    counts = np.full((V, V), alpha, dtype=np.float64)
    if len(idx_train) >= 2:
        prev = idx_train[:-1]
        nxt = idx_train[1:]
        np.add.at(counts, (prev, nxt), 1.0)
    row_sum = counts.sum(axis=1, keepdims=True)
    P_bi = counts / row_sum
    P_uni = build_unigram(idx_train, V, alpha)
    return P_bi.astype(np.float32), P_uni.astype(np.float64)


def bigram_predict_logp(idx_ctx: np.ndarray, P_bi: np.ndarray,
                         P_uni: np.ndarray, train_seen_prev: np.ndarray,
                         backoff_lambda: float = 0.3) -> np.ndarray:
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


def unigram_predict_logp(n: int, P_uni: np.ndarray) -> np.ndarray:
    log_uni = np.log(np.clip(P_uni, 1e-30, None))
    return np.broadcast_to(log_uni, (n, P_uni.shape[0])).copy()


# ============================================================================
# Substrate scoring: cosine logits + (T, lambda) joint sweep
# ============================================================================

def substrate_logits_gpu(query_keys: torch.Tensor, A: torch.Tensor) -> torch.Tensor:
    q = _l2_normalize_t(query_keys)
    a = _l2_normalize_t(A)
    return q @ a.T


def softmax_T(logits: np.ndarray, T: float) -> np.ndarray:
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


def bpw_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    logp_nxt = logp[np.arange(n), nxt]
    return -float(np.mean(logp_nxt)) / math.log(2.0)


def top1_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    if len(nxt) == 0:
        return float("nan")
    pred = np.argmax(logp, axis=1)
    return float((pred == nxt).mean())


def sweep_substrate_TL(sub_logits_dev: np.ndarray, nxt_dev: np.ndarray,
                        sub_logits_test: np.ndarray, nxt_test: np.ndarray,
                        P_uni: np.ndarray) -> Dict[str, float]:
    U_log = np.log(np.clip(P_uni, 1e-30, None))
    best = None
    for T in TEMP_GRID:
        sub_p_dev = softmax_T(sub_logits_dev, T)
        sub_logp_dev = np.log(np.clip(sub_p_dev, 1e-30, None))
        for lam in LAMBDA_GRID:
            comb = log_linear_interp_logp(sub_logp_dev, U_log, lam)
            bpw = bpw_from_logp(comb, nxt_dev)
            if best is None or bpw < best[0]:
                best = (bpw, T, lam)
    _, T_star, lam_star = best
    sub_p_test = softmax_T(sub_logits_test, T_star)
    sub_logp_test = np.log(np.clip(sub_p_test, 1e-30, None))
    comb_test = log_linear_interp_logp(sub_logp_test, U_log, lam_star)
    bpw_test = bpw_from_logp(comb_test, nxt_test)
    top1_test = top1_from_logp(comb_test, nxt_test)
    top1_raw = top1_from_logp(sub_logits_test.astype(np.float64), nxt_test)
    return {"bpw": bpw_test, "top1": top1_test, "top1_raw": top1_raw,
            "T_star": T_star, "lambda_star": lam_star}


# ============================================================================
# Self-tests
# ============================================================================

def _selftest_hrr_bind_invertible_gpu():
    rng = np.random.default_rng(0)
    a = torch.from_numpy(rng.standard_normal(64).astype(np.float32)).to(DEVICE)
    b = torch.from_numpy(rng.standard_normal(64).astype(np.float32)).to(DEVICE)
    c = hrr_bind_batch_gpu(a.unsqueeze(0), b.unsqueeze(0)).squeeze(0)
    diff = (c - a).norm().item()
    assert diff > 1e-3, "hrr_bind no-op (diff=%.6f)" % diff


def _selftest_unigram_normalized():
    idx = np.array([0, 1, 2, 0, 1, 0], dtype=np.int64)
    P = build_unigram(idx, 4, alpha=0.1)
    assert abs(P.sum() - 1.0) < 1e-6, "unigram not normalized: sum=%.6f" % P.sum()
    assert P[0] > P[1] > P[2], "unigram order wrong"


def _selftest_bigram_normalized():
    idx = np.array([0, 1, 0, 1, 2, 0], dtype=np.int64)
    P_bi, P_uni = build_bigram(idx, 4, alpha=0.1)
    row_sums = P_bi.sum(axis=1)
    assert np.allclose(row_sums, 1.0, atol=1e-5), \
        "bigram rows not normalized: %s" % row_sums
    assert P_bi[0, 1] > P_bi[0, 2], "bigram order wrong"


def _selftest_bpw_top1_sanity():
    V = 4
    logp = np.full((3, V), -10.0)
    nxt = np.array([0, 1, 2], dtype=np.int64)
    logp[np.arange(3), nxt] = math.log(1.0 - 1e-9)
    assert top1_from_logp(logp, nxt) == 1.0
    assert bpw_from_logp(logp, nxt) < 0.01, "perfect bpw not near 0"


def _selftest_sparsify_bipolar():
    """Sparse-bipolar should produce exactly k = round(f * dim) non-zero entries per row."""
    dim = 100
    f = 0.05
    V = 8
    rng = np.random.default_rng(0)
    E = torch.from_numpy(rng.standard_normal((V, dim)).astype(np.float32)).to(DEVICE)
    E_sp = sparsify_bipolar_gpu(E, f, 0)
    k_expected = max(1, int(round(f * dim)))
    nnz_per_row = (E_sp != 0).sum(dim=1)
    assert torch.all(nnz_per_row == k_expected), \
        "sparse-bipolar nnz mismatch: got %s expected %d" % (nnz_per_row.tolist(), k_expected)
    # All non-zero entries must be +/-1
    nz = E_sp[E_sp != 0]
    assert torch.all((nz == 1.0) | (nz == -1.0)), "sparse-bipolar non-bipolar values"


def _selftest_lambda_grid_excludes_zero():
    """META C7: LAMBDA_GRID must NOT contain 0.0; lambda=0 lets sweep ignore substrate."""
    assert 0.0 not in LAMBDA_GRID, \
        "LAMBDA_GRID contains 0.0 -- violates META C7 (substrate cheat). Grid=%s" % LAMBDA_GRID


def _selftest_verdict_bands_fire():
    """HP/MID/HF classifier fires correctly on synthetic numbers."""
    b2 = {"top1": 0.10, "bpw": 8.0}
    # HP: lift 1.5x, BPW margin 0.5
    sk5 = {"top1": 0.15, "bpw": 7.5}
    v, _ = classify_verdict(b2, sk5)
    assert v == "HARD_PASS", "HP synth failed: %s" % v
    # MIDDLE: lift 1.20x
    sk5 = {"top1": 0.12, "bpw": 7.8}
    v, _ = classify_verdict(b2, sk5)
    assert v == "MIDDLE_BAND", "MID synth failed: %s" % v
    # HF: top1 below B2
    sk5 = {"top1": 0.09, "bpw": 8.1}
    v, _ = classify_verdict(b2, sk5)
    assert v == "HARD_FAIL", "HF synth failed: %s" % v


def _run_all_selftests():
    _selftest_hrr_bind_invertible_gpu()
    _selftest_unigram_normalized()
    _selftest_bigram_normalized()
    _selftest_bpw_top1_sanity()
    _selftest_sparsify_bipolar()
    _selftest_lambda_grid_excludes_zero()
    _selftest_verdict_bands_fire()
    print("[selftest] PASS: hrr+unigram+bigram+bpw+sparse_bipolar+lambda_grid+verdict_bands",
          flush=True)


# ============================================================================
# Verdict classifier (Fix #28: per-arm metrics)
# ============================================================================

def classify_verdict(b2: Dict[str, float], sk5: Dict[str, float]) -> Tuple[str, str]:
    b2_top1 = float(b2["top1"]); b2_bpw = float(b2["bpw"])
    sk5_top1 = float(sk5["top1"]); sk5_bpw = float(sk5["bpw"])
    lift = sk5_top1 / max(b2_top1, 1e-9)
    bpw_margin = b2_bpw - sk5_bpw

    summary = (
        "S_K5 top1=%.3f vs B2_top1=%.3f (lift %.3fx). "
        "S_K5 BPW=%.3f vs B2_BPW=%.3f (margin %.3f bits)."
    ) % (sk5_top1, b2_top1, lift, sk5_bpw, b2_bpw, bpw_margin)

    if sk5_top1 <= b2_top1 or sk5_bpw >= b2_bpw:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate at K=5 does NOT beat word-bigram. " + summary)

    if lift >= HP_TOP1_LIFT and bpw_margin >= HP_BPW_MARGIN:
        return ("HARD_PASS",
                "HARD_PASS: substrate at K=5 beats word-bigram on BOTH top1 lift "
                "(>=%.2fx) AND BPW margin (>=%.2f bits). " % (HP_TOP1_LIFT, HP_BPW_MARGIN)
                + summary)

    if (MID_TOP1_LIFT <= lift < HP_TOP1_LIFT) or \
       (MID_BPW_MARGIN_LOW <= bpw_margin < MID_BPW_MARGIN_HIGH):
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: substrate at K=5 partially beats word-bigram. "
                + summary)

    return ("HARD_FAIL",
            "HARD_FAIL: substrate at K=5 does not clear MID thresholds. " + summary)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_one_seed(seed: int) -> Dict:
    t0 = time.time()
    gpu_util_samples: List[float] = []
    gpu_mem_used_gb_peak = 0.0

    # Corpus
    if RUN_MODE == "smoke":
        tokens = synthetic_zipfian_tokens(N_TRAIN_WORDS + N_HELD_WORDS,
                                           VOCAB_CAP, seed)
    else:
        tokens = load_text8_tokens(N_TRAIN_WORDS + N_HELD_WORDS)

    train_toks = tokens[:N_TRAIN_WORDS]
    held_toks = tokens[N_TRAIN_WORDS:N_TRAIN_WORDS + N_HELD_WORDS]

    vocab, w2i = build_vocab(train_toks, VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)

    n_held = idx_held.shape[0]
    n_dev = n_held // 2
    idx_dev_ctx = idx_held[:n_dev - 1] if n_dev > 1 else idx_held[:0]
    idx_dev_nxt = idx_held[1:n_dev] if n_dev > 1 else idx_held[:0]
    idx_test_ctx = idx_held[n_dev:-1]
    idx_test_nxt = idx_held[n_dev + 1:]

    print("[seed=%d] V=%d idx_train=%d idx_dev_nxt=%d idx_test_nxt=%d device=%s"
          % (seed, V, idx_train.shape[0], idx_dev_nxt.shape[0], idx_test_nxt.shape[0],
             str(DEVICE)), flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[seed=%d gpu] %s mem_total_gb=%.2f" % (
                seed, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception as e:
            print("[seed=%d gpu-info-fail] %s" % (seed, e), flush=True)

    # ---------- B1 word-unigram ----------
    P_uni = build_unigram(idx_train, V, alpha=0.1)
    log_uni_test = unigram_predict_logp(idx_test_nxt.shape[0], P_uni)
    b1 = {"bpw": bpw_from_logp(log_uni_test, idx_test_nxt),
          "top1": top1_from_logp(log_uni_test, idx_test_nxt)}
    print("  [B1 word-unigram] BPW=%.3f top1=%.3f" % (b1["bpw"], b1["top1"]), flush=True)

    # ---------- B2 word-bigram ----------
    P_bi, P_uni_dbl = build_bigram(idx_train, V, alpha=0.1)
    seen_prev = np.zeros(V, dtype=bool)
    seen_prev[np.unique(idx_train[:-1])] = True
    log_bi_test = bigram_predict_logp(idx_test_ctx, P_bi, P_uni_dbl, seen_prev,
                                       backoff_lambda=0.3)
    b2 = {"bpw": bpw_from_logp(log_bi_test, idx_test_nxt),
          "top1": top1_from_logp(log_bi_test, idx_test_nxt)}
    print("  [B2 word-bigram]  BPW=%.3f top1=%.3f" % (b2["bpw"], b2["top1"]), flush=True)

    # ---------- Substrate arms ----------
    t_enc0 = time.time()
    E, encoder_meta = build_E_production(vocab, N_DIM, seed)
    t_enc = time.time() - t_enc0
    print("  [encoder] built (%.1fs) meta=%s" % (t_enc, encoder_meta), flush=True)

    if DEVICE.type == "cuda":
        try:
            free_b, total_b = torch.cuda.mem_get_info()
            mem_used_gb = (total_b - free_b) / 1e9
            gpu_mem_used_gb_peak = max(gpu_mem_used_gb_peak, mem_used_gb)
            print("  [gpu] post-encoder mem_used_gb=%.2f / total=%.2f" % (
                mem_used_gb, total_b / 1e9), flush=True)
        except Exception:
            pass

    # Train context: positions 0..len(train)-2 conditioning on prev-K, predicting train[i+1]
    train_ctx_idx = idx_train[:-1]
    train_next_idx = idx_train[1:]
    train_ctx_idx_t = torch.from_numpy(train_ctx_idx).to(DEVICE)
    train_next_idx_t = torch.from_numpy(train_next_idx).to(DEVICE)
    idx_dev_ctx_t = torch.from_numpy(idx_dev_ctx).to(DEVICE) \
                     if idx_dev_ctx.shape[0] > 0 else None
    idx_test_ctx_t = torch.from_numpy(idx_test_ctx).to(DEVICE)

    sub_metrics: Dict[str, Dict] = {}
    for K in CONTEXT_K_VALUES:
        t_arm0 = time.time()
        keys_train = build_context_keys_gpu(train_ctx_idx_t, E, K, seed)
        A = build_W_rank1_gpu(keys_train, train_next_idx_t, V)
        keys_test = build_context_keys_gpu(idx_test_ctx_t, E, K, seed)
        sub_logits_test_t = substrate_logits_gpu(keys_test, A)

        if idx_dev_ctx_t is not None and idx_dev_ctx_t.shape[0] > 0:
            keys_dev = build_context_keys_gpu(idx_dev_ctx_t, E, K, seed)
            sub_logits_dev_t = substrate_logits_gpu(keys_dev, A)
            idx_dev_nxt_K = idx_dev_nxt
        else:
            sub_logits_dev_t = sub_logits_test_t
            idx_dev_nxt_K = idx_test_nxt

        if DEVICE.type == "cuda":
            torch.cuda.synchronize()
            try:
                free_b, total_b = torch.cuda.mem_get_info()
                gpu_mem_used_gb_peak = max(gpu_mem_used_gb_peak, (total_b - free_b) / 1e9)
            except Exception:
                pass

        sub_logits_dev = sub_logits_dev_t.cpu().numpy().astype(np.float32)
        sub_logits_test = sub_logits_test_t.cpu().numpy().astype(np.float32)
        del keys_train, A, keys_test, sub_logits_dev_t, sub_logits_test_t
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

        m = sweep_substrate_TL(sub_logits_dev, idx_dev_nxt_K,
                                sub_logits_test, idx_test_nxt, P_uni)
        t_arm = time.time() - t_arm0
        m["elapsed_s_arm"] = t_arm
        sub_metrics[f"S_K{K}"] = m
        print("  [S_K%d] BPW=%.3f top1=%.3f top1_raw=%.3f (T*=%.3f lam*=%.2f) arm_s=%.1fs"
              % (K, m["bpw"], m["top1"], m["top1_raw"], m["T_star"], m["lambda_star"], t_arm),
              flush=True)

    elapsed = time.time() - t0

    sk1_b1_delta = abs(sub_metrics["S_K1"]["top1"] - b1["top1"])
    print("  [sanity] |S_K1.top1 - B1.top1| = %.3f" % sk1_b1_delta, flush=True)

    result = {
        "seed": seed,
        "run_mode": RUN_MODE,
        "elapsed_s": elapsed,
        "V": V,
        "N_DIM": N_DIM,
        "N_TRAIN": int(N_TRAIN_WORDS),
        "N_HELD": int(N_HELD_WORDS),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "gpu_mem_used_gb_peak": float(gpu_mem_used_gb_peak),
        "B1_word_unigram": b1,
        "B2_word_bigram": b2,
        **sub_metrics,
        "sk1_b1_top1_delta": float(sk1_b1_delta),
    }
    return result


# ============================================================================
# Aggregator / verdict
# ============================================================================

def aggregate_and_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    def avg_arm(arm: str, field: str) -> float:
        return float(np.mean([p[arm][field] for p in per_seed]))

    arms_avg: Dict[str, Dict[str, float]] = {}
    for arm in ARMS:
        arms_avg[arm] = {
            "bpw": avg_arm(arm, "bpw"),
            "top1": avg_arm(arm, "top1"),
        }

    b2 = arms_avg["B2_word_bigram"]
    sk5 = arms_avg["S_K5"]
    verdict, vmsg = classify_verdict(b2, sk5)

    honest_scope = {
        "what_this_shows": (
            "Whether substrate at word-grain (V=%d) with PRODUCTION-CONFIG "
            "(word2vec->proj->sparse-bipolar f=%.2f, N_DIM=%d) beats word-bigram. "
            "This rescue tests whether v1 HARD_FAIL was config-confound or genuine "
            "word-grain failure."
        ) % (VOCAB_CAP, SPARSE_BIPOLAR_F, N_DIM),
        "what_this_does_NOT_show": [
            "Substrate behavior at V_word > 4000 (this cell caps at V=%d)" % VOCAB_CAP,
            "Encoder learning (word2vec frozen + Gaussian proj; no backprop)",
            "Sequence > K=10 word context",
            "Cross-corpus (text8-only)",
            "Brain compose stack interactions (no PC top-down, no WM register, no DA-LR)",
        ],
        "primary_arm": "S_K5",
        "real_baseline": "B2_word_bigram (NOT B1_word_unigram)",
        "v1_comparison": (
            "v1 was char-trigram-meanpool + N_DIM=2048: S_K5 top1=0.201 BPW=7.814 "
            "(collapsed to unigram via lambda_star=0.0). v2 production: word2vec + "
            "sparse-bipolar + N_DIM=8192 + LAMBDA_GRID excludes 0.0."
        ),
        "arms_avg": arms_avg,
        "per_arm_metrics_path": "per_seed[*].{arm} for all arms in ARMS",
        "lambda_grid": LAMBDA_GRID,
        "lambda_grid_excludes_zero": (0.0 not in LAMBDA_GRID),
    }

    return verdict, vmsg, honest_scope


# ============================================================================
# Main
# ============================================================================

_run_all_selftests()
if _ARGS.self_test:
    sys.exit(0)

print("[config] " + CONFIG_VERSION, flush=True)
if DEVICE.type == "cuda":
    try:
        print("[device] CUDA %s mem_total_gb=%.2f" % (
            torch.cuda.get_device_name(0),
            torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
    except Exception:
        pass
else:
    print("[device] CPU (no CUDA)", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_DIM, "M": VOCAB_CAP, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds complete; running %s" % (len(done), len(SEEDS), remaining),
      flush=True)

t_start = time.time()
for seed in remaining:
    r = run_one_seed(seed)
    write_partial(out_dir, seed, r)

per_seed = aggregate_partials(out_dir, SEEDS)
per_seed_list = [per_seed[str(s)] for s in SEEDS if str(s) in per_seed]
verdict, vmsg, honest_scope = aggregate_and_verdict(per_seed_list)
elapsed_total = time.time() - t_start

print("\n[VERDICT] " + vmsg, flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": vmsg,
    "run_mode": RUN_MODE,
    "config_version": CONFIG_VERSION,
    "n_seeds": len(per_seed_list),
    "seeds": SEEDS,
    "arms": ARMS,
    "per_seed": per_seed_list,
    "honest_scope": honest_scope,
    "elapsed_s": elapsed_total,
    "summary": vmsg,
}
write_metrics(out_dir, metrics, per_seed_list)
print("[metrics] written to %s/metrics.json" % out_dir, flush=True)
