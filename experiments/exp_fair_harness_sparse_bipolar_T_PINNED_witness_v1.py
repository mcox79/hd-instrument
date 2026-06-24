"""fair_harness_sparse_bipolar_T_PINNED_witness_v1 -- T-PINNED defense against cherry-pick critique.

CRITIQUE: fair_harness HARD_PASS used 42-point (T,lambda) grid search on dev to pick
optimal T; critique is that the +0.43 BPC lift is conditional on post-hoc T calibration.

DEFENSE: Skunkworks methodology audit (2026-06-23) predicted T in [0.05, 0.1] from first
principles BEFORE seeing empirical results (cosine-sim variance + Zipfian counts forces
sharpening; softmax over cosine-sims in [-1,1] needs T~0.05 to produce non-uniform
distributions). The fair_harness run confirms all 3 seeds independently chose T=0.05.

This cell pins T at the methodology-audit-predicted values {0.05, 0.10} and sweeps only
lambda (6 values) on dev. If the T-PINNED arms clear unigram by >=0.20 bits BPC and
are within 0.10 bits of the full-grid baseline, the cherry-pick critique is REFUTED:
the predicted T was independent of the empirical sweep.

Four arms:
  ARM_UNIGRAM
      Analytic floor.
  ARM_SUBSTRATE_SPARSE_BIPOLAR_T005
      Sparse-bipolar, T PINNED=0.05, lambda sweep [6 values] on dev only.
  ARM_SUBSTRATE_SPARSE_BIPOLAR_T010
      Sparse-bipolar, T PINNED=0.10, lambda sweep [6 values] on dev only.
  ARM_SUBSTRATE_SPARSE_BIPOLAR_T_FULL_GRID
      Sparse-bipolar, full (T,lambda) joint sweep (7x6=42 combos) -- same as
      fair_harness_v1 baseline arm; included for direct comparison.

Pre-reg HARD bands (pre-registered before running):
  HARD_PASS (T-PINNED defense holds):
      BOTH T005 AND T010 clear unigram by >= 0.20 bits BPC
      AND both are within 0.10 bits of T_FULL_GRID bpc_best.
  HARD_FAIL (cherry-pick critique confirmed):
      T-PINNED arms underperform unigram (bpc_best > unigram_bpc) OR
      are > 0.30 bits worse than T_FULL_GRID.
  MIDDLE_BAND:
      T-PINNED arms beat unigram but by < 0.20 bits, OR beat by >=0.20 but
      are 0.10-0.30 bits behind T_FULL_GRID.

Config (CPU-feasible): N_DIM=8192, N_TRAIN=10000, N_HELD=2000, V=4000, 3 seeds.
No GPU required (pure numpy/cpu path; word2vec fallback to char-trigram on remote).

Cites:
  preregs/2026-06-23_fair_harness_sparse_bipolar_T_PINNED_witness_v1.md
  experiments/exp_fair_harness_substrate_as_lm_v1.py  (harness source)
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json  (T=0.05 convergence)
  notes/skunkworks_to_all_LANDED_VET_META_HARNESS_RIGGED_substrate_as_lm_reclassification_2026-06-23.md
  notes/research_drill_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md

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
import math
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "fair_harness_sparse_bipolar_T_PINNED_witness_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# ============================================================================
# Argument parsing and run-mode detection
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

# No torch.cuda -- CPU-only cell for remote_cpu_queue
DEVICE_STR = "cpu"

# Pre-registered T pins (from methodology audit prediction)
T_PIN_005 = 0.05
T_PIN_010 = 0.10

# Pre-registered HARD bands (verbatim from task spec)
# HARD_PASS: BOTH T-pinned arms clear unigram by >= 0.20 bits BPC AND within 0.10 bits of T_FULL_GRID
PREREG_HARD_PASS_MARGIN_VS_UNIGRAM = 0.20   # both arms must beat unigram by this
PREREG_HARD_PASS_GAP_VS_FULLGRID = 0.10     # both arms must be within this of T_FULL_GRID
# HARD_FAIL: T-PINNED arms underperform unigram OR > 0.30 bits worse than T_FULL_GRID
PREREG_HARD_FAIL_VS_UNIGRAM = 0.0           # bpc_best > unigram_bpc => underperform
PREREG_HARD_FAIL_GAP_VS_FULLGRID = 0.30     # bpc gap to full_grid > this => fail

N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
SPARSE_BIPOLAR_F = 0.05
MRR_K = 10

# Lambda-only sweep for T-PINNED arms
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
# Full (T, lambda) grid for baseline arm (same as fair_harness_v1)
TEMP_GRID_FULL = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]

ARMS = [
    "ARM_UNIGRAM",
    "ARM_SUBSTRATE_SPARSE_BIPOLAR_T005",
    "ARM_SUBSTRATE_SPARSE_BIPOLAR_T010",
    "ARM_SUBSTRATE_SPARSE_BIPOLAR_T_FULL_GRID",
]
SUBSTRATE_ARMS = [a for a in ARMS if a != "ARM_UNIGRAM"]

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 10_000
    N_HELD = 2_000
else:
    # Smoke: small N, exercises all arms + sweep logic
    SEEDS = [0]
    N_TRAIN = 512
    N_HELD = 128
    VOCAB_CAP = 200
    N_DIM = 256

CONFIG_VERSION = (
    "fair_harness_sparse_bipolar_T_PINNED_witness_v1; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
    "seeds=%s mode=%s T_PIN_005=%.3f T_PIN_010=%.3f "
    "lambdas=%s full_temps=%s sparse_f=%.3f "
    "HARD_PASS=margin_uni>=%.2f_gap_grid<=%.2f "
    "HARD_FAIL=underperform_uni_OR_gap_grid>%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
    SEEDS, RUN_MODE, T_PIN_005, T_PIN_010,
    LAMBDA_GRID, TEMP_GRID_FULL, SPARSE_BIPOLAR_F,
    PREREG_HARD_PASS_MARGIN_VS_UNIGRAM, PREREG_HARD_PASS_GAP_VS_FULLGRID,
    PREREG_HARD_FAIL_GAP_VS_FULLGRID,
)

# Reference baselines from fair_harness full run (N_TRAIN=100k)
FAIR_HARNESS_UNIGRAM_BPC = 7.7378
FAIR_HARNESS_SPARSE_BIPOLAR_FULL_GRID_BPC = 7.3065   # from metrics.json detail.by_arm_agg

# ============================================================================
# Char-trigram encoder (OOV fallback for word2vec)
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


def _l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    return rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))


# ============================================================================
# Gensim / word2vec encoder (CPU path)
# ============================================================================
_GENSIM_KV_CACHE: Dict[str, object] = {}
WORD2VEC_MODEL = "word2vec-google-news-300"


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


def build_E_word2vec_cpu(vocab: List[str], n_dim: int, seed: int
                          ) -> Tuple[np.ndarray, Dict]:
    """Build [V, n_dim] L2-normalized word2vec-projected vectors (CPU numpy).

    OOV words fall back to char-trigram so no zero-row degeneracy.
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
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E = _l2_normalize_np(E_proj)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E, meta


def build_E_char_trigram_cpu(vocab: List[str], n_dim: int, seed: int) -> np.ndarray:
    """Fallback when gensim unavailable."""
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    return _l2_normalize_np(E_np)


# ============================================================================
# Sparse-bipolar primitive
# ============================================================================

def sparsify_bipolar_np(E: np.ndarray, f: float, seed: int) -> np.ndarray:
    """Apply sparse-bipolar thresholding: keep top-k absolute values, binarize sign."""
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    abs_E = np.abs(E)
    out = np.zeros_like(E)
    # For each row keep top-k by abs; set to +/-1
    top_idx = np.argpartition(-abs_E, kth=k - 1, axis=1)[:, :k]
    rows = np.arange(V)[:, None]
    signs = np.sign(E[rows, top_idx])
    signs[signs == 0] = 1.0
    out[rows, top_idx] = signs
    return out.astype(np.float32)


# ============================================================================
# Hebbian W (CPU numpy, chunked)
# ============================================================================

def build_rank1_W_cpu(idx_train: np.ndarray, E: np.ndarray,
                       chunk: int = 2048) -> np.ndarray:
    """W = sum outer(E[idx[t+1]], E[idx[t]]); rank-1 Hebbian. CPU path."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, chunk):
        end = min(b + chunk, n_pairs)
        src_idx = idx_train[b:end]
        tgt_idx = idx_train[b + 1:end + 1]
        E_src = E[src_idx]
        E_tgt = E[tgt_idx]
        W += E_tgt.T @ E_src
    return W


# ============================================================================
# text8 loader / vocab
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
# BPC / top-1 / MRR evaluation (reused from fair_harness_v1)
# ============================================================================

def softmax_logits_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp_logp(sub_logp: np.ndarray, U_log: np.ndarray,
                            lam: float) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    return -float(np.mean(logp[np.arange(n), nxt])) / math.log(2.0)


def top1_acc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    if len(nxt) == 0:
        return float("nan")
    return float(np.mean(np.argmax(logp, axis=1) == nxt))


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


# ============================================================================
# T-PINNED lambda sweep (core new logic)
# ============================================================================

def lambda_sweep_pinned_T(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                           U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                           T_fixed: float, lambda_grid: list, mrr_k: int) -> Dict:
    """Lambda-only sweep at a FIXED T; T is not varied.

    This is the defense arm: T is pinned at the methodology-audit-predicted value.
    Only lambda is tuned on dev; T was chosen by theory, not by grid search.
    """
    # Raw at (T_fixed, lambda=1.0): pure substrate at pinned T, no unigram blend
    probs_T = softmax_logits_with_T(sub_logits_test, T_fixed)
    logp_T = np.log(np.clip(probs_T, 1e-30, 1.0))
    raw_bpc_at_T_L1 = bpc_from_logp(logp_T, nxt_test)
    raw_top1_at_T_L1 = top1_acc_from_logp(logp_T, nxt_test)
    raw_mrr_at_T_L1 = mrr_at_k(logp_T, nxt_test, mrr_k)

    # Precompute substrate probs at T_fixed on dev
    probs_dev = softmax_logits_with_T(sub_logits_dev, T_fixed)
    logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))

    best_bpc = {"lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"lambda": 1.0, "dev_value": -1.0}

    for lam in lambda_grid:
        logp_dev = log_linear_interp_logp(logp_sub_dev, U_log, lam)
        bd = bpc_from_logp(logp_dev, nxt_dev)
        td = top1_acc_from_logp(logp_dev, nxt_dev)
        md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
        if bd < best_bpc["dev_value"]:
            best_bpc = {"lambda": float(lam), "dev_value": bd}
        if td > best_top1["dev_value"]:
            best_top1 = {"lambda": float(lam), "dev_value": td}
        if md > best_mrr["dev_value"]:
            best_mrr = {"lambda": float(lam), "dev_value": md}

    # Eval on test at each best lambda (T is fixed)
    def _test_at_lam(lam: float, fn) -> float:
        probs_t = softmax_logits_with_T(sub_logits_test, T_fixed)
        logp_s = np.log(np.clip(probs_t, 1e-30, 1.0))
        logp = log_linear_interp_logp(logp_s, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _test_at_lam(best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _test_at_lam(best_top1["lambda"], top1_acc_from_logp)
    mrr_best_test = _test_at_lam(best_mrr["lambda"],
                                   lambda lp, nx: mrr_at_k(lp, nx, mrr_k))

    return {
        "bpc_best": round(bpc_best_test, 4),
        "T_fixed": float(T_fixed),
        "best_lambda_for_bpc": best_bpc["lambda"],
        "best_dev_bpc": round(best_bpc["dev_value"], 4),
        "top1_acc": round(top1_best_test, 4),
        "best_lambda_for_top1": best_top1["lambda"],
        "mrr_at_10": round(mrr_best_test, 4),
        "best_lambda_for_mrr": best_mrr["lambda"],
        "raw_bpc_at_T_L1": round(raw_bpc_at_T_L1, 4),
        "raw_top1_at_T_L1": round(raw_top1_at_T_L1, 4),
        "raw_mrr_at_T_L1": round(raw_mrr_at_T_L1, 4),
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
        "lambda_sweep_size": len(lambda_grid),
    }


# ============================================================================
# Full (T, lambda) joint sweep (same as fair_harness_v1 for comparison arm)
# ============================================================================

def joint_sweep_substrate(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                           U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                           temp_grid: list, lambda_grid: list, mrr_k: int) -> Dict:
    """Full joint (T,lambda) sweep on dev; same logic as fair_harness_v1."""
    # raw at T=1.0, lambda=1.0
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

    def _test_metric(T: float, lam: float, fn) -> float:
        probs_test = softmax_logits_with_T(sub_logits_test, T)
        logp_s = np.log(np.clip(probs_test, 1e-30, 1.0))
        logp = log_linear_interp_logp(logp_s, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _test_metric(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _test_metric(best_top1["T"], best_top1["lambda"], top1_acc_from_logp)
    mrr_best_test = _test_metric(best_mrr["T"], best_mrr["lambda"],
                                   lambda lp, nx: mrr_at_k(lp, nx, mrr_k))

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
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
        "grid_size": int(len(temp_grid) * len(lambda_grid)),
    }


# ============================================================================
# Unigram arm
# ============================================================================

def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray,
                     V: int, mrr_k: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    nxt_eval = nxt[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        return {"bpc_unigram": float("inf"), "top1_unigram": 0.0,
                "mrr_unigram": 0.0, "n_test": 0}
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
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(top1, 4),
            "mrr_unigram": round(mrr, 4), "n_test": int(len(nxt_test))}


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
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, DEVICE_STR), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"],
        uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # Build word2vec E (same as fair_harness_v1; OOV fallback to char-trigram)
    print("\n[seed=%d] building word2vec base E (V=%d, N_DIM=%d)..." % (
        seed, V, N_DIM), flush=True)
    t_enc0 = time.time()
    encoder_meta = {}
    try:
        E_base, encoder_meta = build_E_word2vec_cpu(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d encoder] WORD2VEC LOAD FAIL: %s -- falling back to char-trigram" % (
            seed, err), flush=True)
        E_base = build_E_char_trigram_cpu(vocab, N_DIM, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    t_enc = time.time() - t_enc0
    print("[seed=%d encoder] E built (%.1fs) shape=%s" % (
        seed, t_enc, str(E_base.shape)), flush=True)

    # Apply sparse-bipolar transform ONCE (shared by all substrate arms)
    E_sparse = _l2_normalize_np(sparsify_bipolar_np(E_base, SPARSE_BIPOLAR_F, seed))

    # Split held into dev + test halves (same masking as fair_harness_v1)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    ctx_eval = ctx_full[mask]
    nxt_eval = nxt_full[mask]
    n_eval = len(ctx_eval)

    if n_eval == 0:
        for arm in SUBSTRATE_ARMS:
            by_arm[arm] = {"empty_eval": True}
        return {
            "seed": seed, "by_arm": by_arm, "V": V, "N": N_DIM, "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
            "PRETRAIN_DIM": PRETRAIN_DIM, "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "elapsed_s_seed": round(time.time() - t_seed, 2),
            "device": DEVICE_STR, "encoder_meta": encoder_meta,
        }

    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]
    valid_held_pos = np.where(mask)[0]

    # Build logits ONCE for sparse-bipolar arm (shared across T005/T010/FULL_GRID)
    print("\n[seed=%d] building sparse-bipolar W and logits (CPU)..." % seed, flush=True)
    t_w0 = time.time()
    idx_train_arr = idx_train
    W = build_rank1_W_cpu(idx_train_arr, E_sparse, chunk=2048)
    t_w = time.time() - t_w0
    print("[seed=%d] W built (%.1fs) shape=%s" % (seed, t_w, str(W.shape)), flush=True)

    t_r0 = time.time()
    # Recall: pred[t] = normalize(E_sparse[idx_held[t]] @ W.T)
    # Logits: pred[t] @ E_sparse.T = [V] cosine sims
    n_held_ctx = len(ctx_full)
    RECALL_CHUNK = 512
    logits_full = np.zeros((n_held_ctx, V), dtype=np.float32)
    for b in range(0, n_held_ctx, RECALL_CHUNK):
        end = min(b + RECALL_CHUNK, n_held_ctx)
        src = E_sparse[ctx_full[b:end]]
        pred = src @ W.T
        # L2 normalize pred
        norms = np.linalg.norm(pred, axis=1, keepdims=True).clip(1e-12, None)
        pred = pred / norms
        logits_full[b:end] = pred @ E_sparse.T
    t_r = time.time() - t_r0
    print("[seed=%d] logits computed (%.1fs)" % (seed, t_r), flush=True)
    del W

    # Extract logits for valid positions
    if logits_full.shape[0] >= len(ctx_full):
        logits_eval = logits_full[mask]
    else:
        mask_pos = np.array([p for p in valid_held_pos if p < logits_full.shape[0]], dtype=np.int64)
        logits_eval = logits_full[mask_pos]
        nxt_eval_local = nxt_full[mask_pos]
        ne = len(nxt_eval_local)
        ndev = ne // 2
        nxt_dev = nxt_eval_local[:ndev]
        nxt_test = nxt_eval_local[ndev:]

    logits_dev = logits_eval[:n_dev]
    logits_test = logits_eval[n_dev:]

    # ARM: T_PINNED=0.05
    t_a0 = time.time()
    r005 = lambda_sweep_pinned_T(
        logits_dev, logits_test, U_log, nxt_dev, nxt_test,
        T_fixed=T_PIN_005, lambda_grid=LAMBDA_GRID, mrr_k=MRR_K,
    )
    r005["elapsed_s_arm"] = round(time.time() - t_a0, 2)
    by_arm["ARM_SUBSTRATE_SPARSE_BIPOLAR_T005"] = r005
    print("  [seed=%d arm=T005] bpc_best=%.3f (T=%.3f bestL=%.2f) raw_bpc_at_TL1=%.3f" % (
        seed, r005["bpc_best"], r005["T_fixed"], r005["best_lambda_for_bpc"],
        r005["raw_bpc_at_T_L1"]), flush=True)

    # ARM: T_PINNED=0.10
    t_a0 = time.time()
    r010 = lambda_sweep_pinned_T(
        logits_dev, logits_test, U_log, nxt_dev, nxt_test,
        T_fixed=T_PIN_010, lambda_grid=LAMBDA_GRID, mrr_k=MRR_K,
    )
    r010["elapsed_s_arm"] = round(time.time() - t_a0, 2)
    by_arm["ARM_SUBSTRATE_SPARSE_BIPOLAR_T010"] = r010
    print("  [seed=%d arm=T010] bpc_best=%.3f (T=%.3f bestL=%.2f) raw_bpc_at_TL1=%.3f" % (
        seed, r010["bpc_best"], r010["T_fixed"], r010["best_lambda_for_bpc"],
        r010["raw_bpc_at_T_L1"]), flush=True)

    # ARM: FULL_GRID (same 7x6 as fair_harness_v1)
    t_a0 = time.time()
    rfull = joint_sweep_substrate(
        logits_dev, logits_test, U_log, nxt_dev, nxt_test,
        temp_grid=TEMP_GRID_FULL, lambda_grid=LAMBDA_GRID, mrr_k=MRR_K,
    )
    rfull["elapsed_s_arm"] = round(time.time() - t_a0, 2)
    by_arm["ARM_SUBSTRATE_SPARSE_BIPOLAR_T_FULL_GRID"] = rfull
    print("  [seed=%d arm=T_FULL_GRID] bpc_best=%.3f (bestT=%.4f bestL=%.2f)" % (
        seed, rfull["bpc_best"], rfull["best_T_for_bpc"], rfull["best_lambda_for_bpc"]),
        flush=True)

    del E_sparse, E_base, logits_full, logits_eval

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
        "device": DEVICE_STR,
        "encoder_meta": encoder_meta,
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Aggregate unigram
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    unigram_bpc_mean = float(np.mean(uni_bpc))

    by_arm_agg: Dict[str, Dict] = {}

    def _agg_pinned(arm: str) -> Dict:
        valid_units = [u for u in units if arm in u["by_arm"]
                       and not u["by_arm"][arm].get("compute_failed", False)
                       and math.isfinite(u["by_arm"][arm].get("bpc_best", float("inf")))]
        if not valid_units:
            return {"bpc_best_mean": float("inf"), "n_valid_seeds": 0, "all_seeds_failed": True}
        bpcs = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1s = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrrs = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        lam_bpcs = [u["by_arm"][arm]["best_lambda_for_bpc"] for u in valid_units]
        T_f = [u["by_arm"][arm]["T_fixed"] for u in valid_units]
        raw_bpcs = [u["by_arm"][arm]["raw_bpc_at_T_L1"] for u in valid_units]
        b_m = float(np.mean(bpcs))
        b_s = float(np.std(bpcs))
        return {
            "bpc_best_mean": round(b_m, 4),
            "bpc_best_std": round(b_s, 4),
            "bpc_best_cv": round(b_s / max(abs(b_m), 1e-6), 4),
            "top1_acc_mean": round(float(np.mean(top1s)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrrs)), 4),
            "best_lambda_for_bpc_mean": round(float(np.mean(lam_bpcs)), 4),
            "T_fixed_mean": round(float(np.mean(T_f)), 4),
            "raw_bpc_at_T_L1_mean": round(float(np.mean(raw_bpcs)), 4),
            "n_valid_seeds": int(len(valid_units)),
            "all_seeds_failed": False,
        }

    def _agg_full(arm: str) -> Dict:
        valid_units = [u for u in units if arm in u["by_arm"]
                       and not u["by_arm"][arm].get("compute_failed", False)
                       and math.isfinite(u["by_arm"][arm].get("bpc_best", float("inf")))]
        if not valid_units:
            return {"bpc_best_mean": float("inf"), "n_valid_seeds": 0, "all_seeds_failed": True}
        bpcs = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        bT = [u["by_arm"][arm]["best_T_for_bpc"] for u in valid_units]
        bL = [u["by_arm"][arm]["best_lambda_for_bpc"] for u in valid_units]
        top1s = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrrs = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw = [u["by_arm"][arm]["raw_bpc_at_T1_L1"] for u in valid_units]
        b_m = float(np.mean(bpcs))
        b_s = float(np.std(bpcs))
        return {
            "bpc_best_mean": round(b_m, 4),
            "bpc_best_std": round(b_s, 4),
            "bpc_best_cv": round(b_s / max(abs(b_m), 1e-6), 4),
            "top1_acc_mean": round(float(np.mean(top1s)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrrs)), 4),
            "best_T_for_bpc_mean": round(float(np.mean(bT)), 4),
            "best_lambda_for_bpc_mean": round(float(np.mean(bL)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw)), 4),
            "n_valid_seeds": int(len(valid_units)),
            "all_seeds_failed": False,
        }

    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(unigram_bpc_mean, 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
    }
    a005 = _agg_pinned("ARM_SUBSTRATE_SPARSE_BIPOLAR_T005")
    a010 = _agg_pinned("ARM_SUBSTRATE_SPARSE_BIPOLAR_T010")
    afull = _agg_full("ARM_SUBSTRATE_SPARSE_BIPOLAR_T_FULL_GRID")
    by_arm_agg["ARM_SUBSTRATE_SPARSE_BIPOLAR_T005"] = a005
    by_arm_agg["ARM_SUBSTRATE_SPARSE_BIPOLAR_T010"] = a010
    by_arm_agg["ARM_SUBSTRATE_SPARSE_BIPOLAR_T_FULL_GRID"] = afull

    # Evaluate HARD bands (pre-registered)
    bpc005 = a005.get("bpc_best_mean", float("inf"))
    bpc010 = a010.get("bpc_best_mean", float("inf"))
    bpcfull = afull.get("bpc_best_mean", float("inf"))

    # HARD_FAIL conditions
    # (a) any pinned arm underperforms unigram
    t005_underperforms = bpc005 >= unigram_bpc_mean
    t010_underperforms = bpc010 >= unigram_bpc_mean
    # (b) any pinned arm more than 0.30 bits worse than full grid
    t005_gap_too_large = (bpc005 - bpcfull) > PREREG_HARD_FAIL_GAP_VS_FULLGRID
    t010_gap_too_large = (bpc010 - bpcfull) > PREREG_HARD_FAIL_GAP_VS_FULLGRID

    hard_fail = (
        t005_underperforms or t010_underperforms or
        t005_gap_too_large or t010_gap_too_large
    )

    # HARD_PASS conditions (both T-PINNED arms)
    # (a) both beat unigram by >= 0.20 bits
    t005_clears_unigram = (unigram_bpc_mean - bpc005) >= PREREG_HARD_PASS_MARGIN_VS_UNIGRAM
    t010_clears_unigram = (unigram_bpc_mean - bpc010) >= PREREG_HARD_PASS_MARGIN_VS_UNIGRAM
    # (b) both within 0.10 bits of full-grid
    t005_close_to_full = (bpc005 - bpcfull) <= PREREG_HARD_PASS_GAP_VS_FULLGRID
    t010_close_to_full = (bpc010 - bpcfull) <= PREREG_HARD_PASS_GAP_VS_FULLGRID

    hard_pass = (
        t005_clears_unigram and t010_clears_unigram and
        t005_close_to_full and t010_close_to_full
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "unigram_bpc_mean": round(unigram_bpc_mean, 4),
        "bpc005_vs_unigram": round(unigram_bpc_mean - bpc005, 4),
        "bpc010_vs_unigram": round(unigram_bpc_mean - bpc010, 4),
        "bpc005_vs_fullgrid": round(bpc005 - bpcfull, 4),
        "bpc010_vs_fullgrid": round(bpc010 - bpcfull, 4),
        "t005_clears_unigram_by_020": bool(t005_clears_unigram),
        "t010_clears_unigram_by_020": bool(t010_clears_unigram),
        "t005_within_010_of_fullgrid": bool(t005_close_to_full),
        "t010_within_010_of_fullgrid": bool(t010_close_to_full),
        "t005_underperforms_unigram": bool(t005_underperforms),
        "t010_underperforms_unigram": bool(t010_underperforms),
        "t005_gap_exceeds_030": bool(t005_gap_too_large),
        "t010_gap_exceeds_030": bool(t010_gap_too_large),
        "n_seeds": int(len(units)),
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "T-PINNED cherry-pick defense: T_PINNED at {0.05, 0.10} predicted by "
            "methodology audit BEFORE empirical results. HARD_PASS = both pinned arms "
            "clear unigram by >=%.2f bits AND within %.2f bits of full-grid. "
            "HARD_FAIL = any pinned arm underperforms unigram OR gap to full-grid >%.2f. "
            "N_DIM=%d N_TRAIN=%d N_HELD=%d V=%d." % (
                PREREG_HARD_PASS_MARGIN_VS_UNIGRAM, PREREG_HARD_PASS_GAP_VS_FULLGRID,
                PREREG_HARD_FAIL_GAP_VS_FULLGRID, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP)
        ),
        "cites": [
            "preregs/2026-06-23_fair_harness_sparse_bipolar_T_PINNED_witness_v1.md",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json",
        ],
    }

    summary = (
        "TPIN_WITNESS uni=bpc%.3f | "
        "T005=bpc%.3f(+%.3f_vs_uni,+%.3f_vs_full) | "
        "T010=bpc%.3f(+%.3f_vs_uni,+%.3f_vs_full) | "
        "T_FULL_GRID=bpc%.3f"
    ) % (
        unigram_bpc_mean,
        bpc005, unigram_bpc_mean - bpc005, bpc005 - bpcfull,
        bpc010, unigram_bpc_mean - bpc010, bpc010 - bpcfull,
        bpcfull,
    )

    if hard_fail:
        fail_reasons = []
        if t005_underperforms:
            fail_reasons.append("T005 underperforms unigram (bpc=%.3f >= uni=%.3f)" % (
                bpc005, unigram_bpc_mean))
        if t010_underperforms:
            fail_reasons.append("T010 underperforms unigram (bpc=%.3f >= uni=%.3f)" % (
                bpc010, unigram_bpc_mean))
        if t005_gap_too_large:
            fail_reasons.append("T005 gap_to_full=%.3f > 0.30" % (bpc005 - bpcfull))
        if t010_gap_too_large:
            fail_reasons.append("T010 gap_to_full=%.3f > 0.30" % (bpc010 - bpcfull))
        return ("HARD_FAIL",
                "T_PINNED HARD_FAIL: cherry-pick critique CONFIRMED. %s. %s" % (
                    "; ".join(fail_reasons), summary),
                detail)

    if hard_pass:
        return ("HARD_PASS",
                "T_PINNED HARD_PASS: cherry-pick critique REFUTED. Both T=0.05 and T=0.10 "
                "predicted by methodology audit a priori clear unigram by >=0.20 bits BPC "
                "and are within 0.10 bits of full-grid. %s" % summary,
                detail)

    # MIDDLE_BAND
    mid_reasons = []
    if not t005_clears_unigram:
        mid_reasons.append("T005 beats unigram by <0.20 bits (%.3f)" % (
            unigram_bpc_mean - bpc005))
    if not t010_clears_unigram:
        mid_reasons.append("T010 beats unigram by <0.20 bits (%.3f)" % (
            unigram_bpc_mean - bpc010))
    if not t005_close_to_full and not t005_gap_too_large:
        mid_reasons.append("T005 gap_to_full=%.3f (0.10-0.30 band)" % (bpc005 - bpcfull))
    if not t010_close_to_full and not t010_gap_too_large:
        mid_reasons.append("T010 gap_to_full=%.3f (0.10-0.30 band)" % (bpc010 - bpcfull))
    return ("MIDDLE_BAND",
            "T_PINNED MIDDLE_BAND: partial T-pinned defense. %s. %s" % (
                "; ".join(mid_reasons) if mid_reasons else "marginal", summary),
            detail)


# ============================================================================
# Instrumentation self-test (MANDATORY per role contract)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    import math as _math

    # 1. Test lambda_sweep_pinned_T produces finite BPC
    V_t = 50
    n_samples = 20
    rng_t = np.random.default_rng(0)
    logits_dev_t = rng_t.standard_normal((n_samples, V_t)).astype(np.float32)
    logits_test_t = rng_t.standard_normal((n_samples, V_t)).astype(np.float32)
    U_t = np.ones(V_t, dtype=np.float64) / V_t
    U_log_t = np.log(U_t).astype(np.float32)
    nxt_dev_t = rng_t.integers(0, V_t, size=n_samples).astype(np.int64)
    nxt_test_t = rng_t.integers(0, V_t, size=n_samples).astype(np.int64)

    r = lambda_sweep_pinned_T(
        logits_dev_t, logits_test_t, U_log_t, nxt_dev_t, nxt_test_t,
        T_fixed=0.05, lambda_grid=LAMBDA_GRID, mrr_k=MRR_K,
    )
    assert r["bpc_best"] is not None, "selftest: bpc_best is None"
    assert _math.isfinite(r["bpc_best"]), "selftest: bpc_best not finite: %s" % r["bpc_best"]
    assert r["top1_acc"] is not None, "selftest: top1_acc is None"
    assert r["mrr_at_10"] is not None, "selftest: mrr_at_10 is None"
    assert r["lambda_sweep_size"] == len(LAMBDA_GRID), "selftest: lambda_sweep_size"
    assert r["n_dev"] == n_samples, "selftest: n_dev"
    assert r["n_test"] == n_samples, "selftest: n_test"

    # 2. Test joint_sweep_substrate produces finite BPC
    r2 = joint_sweep_substrate(
        logits_dev_t, logits_test_t, U_log_t, nxt_dev_t, nxt_test_t,
        temp_grid=TEMP_GRID_FULL, lambda_grid=LAMBDA_GRID, mrr_k=MRR_K,
    )
    assert r2["bpc_best"] is not None, "selftest: full_grid bpc_best is None"
    assert _math.isfinite(r2["bpc_best"]), "selftest: full_grid bpc_best not finite"
    assert r2["grid_size"] == len(TEMP_GRID_FULL) * len(LAMBDA_GRID), "selftest: grid_size"

    # 3. Test sparsify_bipolar_np produces correct nnz
    V_s = 10
    dim_s = 100
    E_rand = np.random.default_rng(1).standard_normal((V_s, dim_s)).astype(np.float32)
    sp = sparsify_bipolar_np(E_rand, 0.05, seed=0)
    k_expect = max(1, int(round(0.05 * dim_s)))
    nnz = (sp != 0).sum(axis=1)
    assert all(n == k_expect for n in nnz.tolist()), "selftest: sparse nnz %s" % nnz.tolist()
    uniq = set(sp.flat)
    assert uniq.issubset({-1.0, 0.0, 1.0}), "selftest: sparse not bipolar %s" % uniq

    # 4. Test softmax at T=0.05 is peaked (not degenerate)
    peaked = np.zeros((1, 20), dtype=np.float32)
    peaked[0, 5] = 1.0
    probs = softmax_logits_with_T(peaked, 0.05)
    assert probs.max() > 0.5, "selftest: T=0.05 should be peaked, got max=%.4f" % probs.max()

    # 5. Test compute_verdict classifies HARD_PASS correctly at smoke scale
    def _mk_unit(bpc005, bpc010, bpcfull, unigram_bpc=7.738, V=200):
        def _arm_data_pinned(bpc, T_f):
            return {"bpc_best": bpc, "T_fixed": T_f, "best_lambda_for_bpc": 0.3,
                    "best_dev_bpc": bpc, "top1_acc": 0.20, "best_lambda_for_top1": 0.3,
                    "mrr_at_10": 0.25, "best_lambda_for_mrr": 0.3,
                    "raw_bpc_at_T_L1": bpc - 0.1, "raw_top1_at_T_L1": 0.20,
                    "raw_mrr_at_T_L1": 0.25, "n_dev": 50, "n_test": 50,
                    "lambda_sweep_size": 6, "elapsed_s_arm": 0.01}
        def _arm_data_full(bpc):
            return {"bpc_best": bpc, "best_T_for_bpc": 0.05, "best_lambda_for_bpc": 0.3,
                    "best_dev_bpc": bpc, "top1_acc": 0.20, "best_T_for_top1": 0.05,
                    "best_lambda_for_top1": 0.3, "mrr_at_10": 0.25,
                    "best_T_for_mrr": 0.05, "best_lambda_for_mrr": 0.3,
                    "raw_bpc_at_T1_L1": bpc + 0.5, "n_dev": 50, "n_test": 50,
                    "grid_size": 42, "elapsed_s_arm": 0.01}
        return {
            "seed": 0,
            "by_arm": {
                "ARM_UNIGRAM": {"bpc_unigram": unigram_bpc, "top1_unigram": 0.21,
                                "mrr_unigram": 0.28, "n_test": 50},
                "ARM_SUBSTRATE_SPARSE_BIPOLAR_T005": _arm_data_pinned(bpc005, T_PIN_005),
                "ARM_SUBSTRATE_SPARSE_BIPOLAR_T010": _arm_data_pinned(bpc010, T_PIN_010),
                "ARM_SUBSTRATE_SPARSE_BIPOLAR_T_FULL_GRID": _arm_data_full(bpcfull),
            },
            "V": V, "N": 256, "N_DIM": 256, "N_TRAIN": 512, "N_HELD": 128,
            "VOCAB_CAP": V, "PRETRAIN_DIM": 10,
            "run_mode": "smoke", "config_version": "selftest",
            "elapsed_s_seed": 0.01, "device": "cpu",
        }

    # HARD_PASS: both arms beat unigram by 0.40 and within 0.05 of full_grid
    u_hp = _mk_unit(bpc005=7.338, bpc010=7.338, bpcfull=7.308, unigram_bpc=7.738)
    v, m, d = compute_verdict([u_hp, u_hp, u_hp])
    assert v == "HARD_PASS", "selftest verdict HARD_PASS: got %s msg=%s" % (v, m[:200])

    # HARD_FAIL: T005 underperforms unigram
    u_hf = _mk_unit(bpc005=7.80, bpc010=7.338, bpcfull=7.308, unigram_bpc=7.738)
    v, m, d = compute_verdict([u_hf, u_hf, u_hf])
    assert v == "HARD_FAIL", "selftest verdict HARD_FAIL: got %s msg=%s" % (v, m[:200])

    # MIDDLE_BAND: both beat unigram but by < 0.20 bits
    u_mid = _mk_unit(bpc005=7.60, bpc010=7.60, bpcfull=7.308, unigram_bpc=7.738)
    v, m, d = compute_verdict([u_mid, u_mid, u_mid])
    assert v == "MIDDLE_BAND", "selftest verdict MIDDLE_BAND: got %s msg=%s" % (v, m[:200])

    print("[_instrumentation_selftest] PASS: lambda_sweep + joint_sweep + sparse_bipolar "
          "+ softmax_peaked + verdict_bands (HP/HF/MB)", flush=True)


_instrumentation_selftest()


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
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "detail": detail,
            "per_unit": units,
            "elapsed_s": round(time.time() - (_T0_REF[0] or time.time()), 2),
            "config_version": CONFIG_VERSION,
            "device": DEVICE_STR,
        }
        write_metrics(out_dir, metrics)
        print("[atexit] partial metrics written: verdict=%s n_seeds=%d" % (verdict, len(units)),
              flush=True)
    except Exception as ex:
        print("[atexit] synthesize failed: %s" % ex, flush=True)


atexit.register(_synthesize_on_exit)


# ============================================================================
# Main
# ============================================================================

def main():
    _T0 = time.time()
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    _T0_REF[0] = _T0

    if _ARGS.self_test:
        print("[--self-test] instrumentation_selftest already ran at module scope: PASS",
              flush=True)
        sys.exit(0)

    print("=== %s RUN_MODE=%s SEEDS=%s ===" % (ANCHOR_NAME, RUN_MODE, SEEDS), flush=True)
    print("Config: N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d device=%s" % (
        N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, DEVICE_STR), flush=True)
    print("Pre-reg: HARD_PASS = both T-pinned arms clear unigram by >=%.2f bits AND "
          "within %.2f bits of full-grid" % (
              PREREG_HARD_PASS_MARGIN_VS_UNIGRAM, PREREG_HARD_PASS_GAP_VS_FULLGRID),
          flush=True)
    print("Pre-reg: HARD_FAIL = any T-pinned arm underperforms unigram OR "
          "gap_to_full_grid > %.2f bits" % PREREG_HARD_FAIL_GAP_VS_FULLGRID, flush=True)

    units = []
    for seed in SEEDS:
        unit = run_unit(seed)
        units.append(unit)
        ck = "s%d" % seed
        write_partial_key(out_dir, ck, unit)
        t005 = unit["by_arm"].get("ARM_SUBSTRATE_SPARSE_BIPOLAR_T005", {})
        t010 = unit["by_arm"].get("ARM_SUBSTRATE_SPARSE_BIPOLAR_T010", {})
        tfull = unit["by_arm"].get("ARM_SUBSTRATE_SPARSE_BIPOLAR_T_FULL_GRID", {})
        print("[seed=%d] done -- T005_bpc=%.3f T010_bpc=%.3f TFULL_bpc=%.3f elapsed=%.1fs" % (
            seed,
            t005.get("bpc_best", float("nan")),
            t010.get("bpc_best", float("nan")),
            tfull.get("bpc_best", float("nan")),
            unit.get("elapsed_s_seed", 0.0)), flush=True)

    verdict, msg, detail = compute_verdict(units)
    print("\n=== VERDICT: %s ===" % verdict, flush=True)
    print(msg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "T_PIN_005": T_PIN_005,
        "T_PIN_010": T_PIN_010,
        "LAMBDA_GRID": LAMBDA_GRID,
        "TEMP_GRID_FULL": TEMP_GRID_FULL,
        "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "ARMS": ARMS,
        "n_seeds": int(len(units)),
        "detail": detail,
        "per_unit": units,
        "elapsed_s": round(time.time() - _T0, 2),
        "config_version": CONFIG_VERSION,
        "device": DEVICE_STR,
        "corpus_provenance": "text8 (%s)" % str(TEXT8),
        "prereg": {
            "HARD_PASS": (
                "BOTH T005 AND T010 clear unigram by >= %.2f bits BPC "
                "AND both within %.2f bits of T_FULL_GRID" % (
                    PREREG_HARD_PASS_MARGIN_VS_UNIGRAM, PREREG_HARD_PASS_GAP_VS_FULLGRID)
            ),
            "HARD_FAIL": (
                "any T-PINNED arm underperforms unigram (bpc_best >= unigram_bpc) "
                "OR gap to T_FULL_GRID > %.2f bits" % PREREG_HARD_FAIL_GAP_VS_FULLGRID
            ),
            "MIDDLE_BAND": (
                "T-PINNED arms beat unigram but by < %.2f bits, OR beat by >= %.2f "
                "but within 0.10-0.30 bits of T_FULL_GRID" % (
                    PREREG_HARD_PASS_MARGIN_VS_UNIGRAM, PREREG_HARD_PASS_MARGIN_VS_UNIGRAM)
            ),
        },
    }
    write_metrics(out_dir, metrics)
    _METRICS_WRITTEN[0] = True
    print("[done] metrics written to %s" % out_dir, flush=True)
    sys.exit(0 if verdict in ("HARD_PASS", "MIDDLE_BAND") else 1)


if __name__ == "__main__":
    main()
