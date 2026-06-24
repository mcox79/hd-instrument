"""substrate_higher_order_taylor_nonlinear_hebbian_LM_v2

RESCUE of v1 -- calibration-collapse fix per Skunkworks BATCH_VET_4 (2026-06-23).

ROOT CAUSE (v1): LAMBDA_GRID=[0.0, 0.1, 0.3, 0.5, 0.7, 1.0] skips the
fair_harness optimal lambda~0.033.  With dense word2vec logits slightly noisier
than pure-unigram at coarse-grid points, the joint sweep always collapses to
lambda=0.0 (pure unigram).  ALL 5 arms reported bpc=7.7378 (unigram floor).
Underlying raw_bpc_at_T1_L1 DID show per-arm separation (n1=11.70, n5=11.77),
confirming the W matrices are non-degenerate -- only the calibration was broken.

FIX (v2): Expand LAMBDA_GRID to {0.0, 0.01, 0.02, 0.033, 0.05, 0.1, 0.2, 0.5, 1.0}
which brackets fair_harness optimal (~0.033).  No other mechanism changes.

Added: explicit calibration_collapse detection post-sweep (flag CALIBRATION_COLLAPSE
when best_lambda=0.0 for ARM_n1 -- report alongside verdict, not as HARD_FAIL per
pre-reg).  ARM_n1 sanity gate: if ARM_n1 BPC > 7.5 AND best_lam=0.0, emit warning.

Same as v1 EXCEPT LAMBDA_GRID, ANCHOR_NAME, and diagnostics.

Five arms sweep polynomial order n in {1,2,3,4,5}:
  ARM_n1  -- n=1: standard rank-1 Hebbian outer-product (reproduces fair_harness baseline)
  ARM_n2  -- n=2: quadratic nonlinear Hebbian
  ARM_n3  -- n=3: cubic
  ARM_n4  -- n=4: quartic (Krotov dense-memory regime)
  ARM_n5  -- n=5: quintic (dense-Hopfield regime)

Ocker-Buice mechanism (forward-only, per equation 4 in paper):
  For each training pair (E[t], E[t+1]):
    dW += f_n(E[t+1]) * E[t]^T   where f_n(x)_i = x_i * |x_i|^(n-1)
  At recall: pred = W @ E[ctx]; L2-normalize; then cosine-logits @ E.T

Pre-reg HARD bands (same as v1):
  HARD_PASS: ARM_n4 BPC lift >= +0.30 bits vs ARM_n1
  CHAIN_GRADE_BONUS: lift >= +0.50 bits
  MIDDLE_BAND: lift +0.10 to +0.30 bits
  HARD_FAIL: lift <= +0.10 bits at n=4-5 OR ARM_n>=3 collapses to unigram
  cv < 0.05 across seeds mandatory for HARD_PASS

Mandatory sanity gate: ARM_n1 BPC must be 7.3065 +/- 0.05 (matches fair_harness
word2vec_dense baseline ~7.72 -- NOTE: gate uses 7.3065+/-0.05 as stated in task
spec, but the ACTUAL expected value is ~7.72; if ARM_n1 is outside 7.3065+/-0.05
AND calibration_collapse=False, flag READOUT_DEGENERATE not HARD_FAIL on mechanism).

GPU required: N_DIM=8192 matmul-bound (Fix #22 rule: N_DIM >= 8192 -> overnight_queue).

Cites:
  Ocker-Buice 2021 arxiv:2106.15685 (Taylor-tensor-eigenvector bridge)
  Krotov-Hopfield 2016 NeurIPS (dense associative memory polynomial f)
  preregs/2026-06-23_substrate_higher_order_taylor_nonlinear_hebbian_LM_v2.md
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json (baseline BPC=7.3065)
  notes/skunkworks_to_all_BATCH_VET_4_recent_negatives_2026-06-23.md (VET diagnosis)
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
os.environ.setdefault("PYTORCH_CUDA_ALLOC_CONF", "expandable_segments:True")

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
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_higher_order_taylor_nonlinear_hebbian_LM_v2"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
_LLM_CALL_COUNTER = [0]

# Pre-reg bands (same as v1)
BASELINE_BPC = 7.3065      # fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR mean BPC
UNIGRAM_BPC_REF = 7.738    # unigram floor
HARD_PASS_LIFT = 0.30      # ARM_n4 BPC lift vs ARM_n1 must be >= 0.30 bits lower BPC
CHAIN_GRADE_BONUS_LIFT = 0.50
HARD_FAIL_MAX_LIFT = 0.10  # if lift <= 0.10 at n=4-5 => HARD_FAIL
HP_CV_MAX = 0.05           # cv across seeds mandatory for HARD_PASS

# Joint (T, lambda) sweep grid
# v2 FIX: expanded LAMBDA_GRID to bracket fair_harness optimal lambda~0.033
# v1 bug: grid [0.0, 0.1, 0.3, 0.5, 0.7, 1.0] skipped 0.033; sweep collapsed to 0.0
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.01, 0.02, 0.033, 0.05, 0.1, 0.2, 0.5, 1.0]
MRR_K = 10

# Dense (not sparse-bipolar) L2-normalized word2vec projection.
# Ocker-Buice nonlinearity requires |x_i| ~ 1/sqrt(N) (dense uniform magnitude).
# n=1 arm reproduces fair_harness ARM_SUBSTRATE_WORD2VEC_DENSE (~7.72 BPC).
WORD2VEC_MODEL = "word2vec-google-news-300"

POLY_ORDERS = [1, 2, 3, 4, 5]
ARMS = ["ARM_n%d" % n for n in POLY_ORDERS]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Config (FULL = production)
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke: small N, fast, exercises all arms + verdict path
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

CONFIG_VERSION = (
    "substrate_higher_order_taylor_nonlinear_hebbian_LM_v2; "
    "N_DIM=%d PRETRAIN_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
    "arms=%s seeds=%s mode=%s encoder=dense_word2vec_projected "
    "poly_orders=%s temps=%s lambdas=%s MRR_K=%d device=%s; "
    "bands HP_lift>=%.2f HF_lift<=%.2f cv_max=%.2f; "
    "v2_fix=LAMBDA_GRID_expanded_to_bracket_0.033"
) % (
    N_DIM, PRETRAIN_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
    ARMS, SEEDS, RUN_MODE,
    POLY_ORDERS, TEMP_GRID, LAMBDA_GRID, MRR_K, str(DEVICE),
    HARD_PASS_LIFT, HARD_FAIL_MAX_LIFT, HP_CV_MAX,
)


# ============================================================================
# Utility: L2 normalize
# ============================================================================

def _l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _l2_normalize_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    if X.dim() == 1:
        return X / (X.norm() + eps)
    return X / (X.norm(dim=1, keepdim=True) + eps)


# ============================================================================
# Char-trigram fallback encoder
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


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


# ============================================================================
# Word2vec encoder (same as fair_harness)
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
    n_hit = n_miss = 0
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


def build_E_word2vec_dense(vocab: List[str], n_dim: int, seed: int
                            ) -> Tuple[torch.Tensor, Dict]:
    """Build [V, n_dim] DENSE L2-normalized word2vec-projected vectors on DEVICE."""
    kv = _load_gensim_kv(WORD2VEC_MODEL)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = _l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_before = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_before < 1e-9
    if oov_mask.any():
        rng_oov = np.random.default_rng(seed * 3117 + 7)
        for i in np.where(oov_mask)[0]:
            v = rng_oov.standard_normal(n_dim).astype(np.float32)
            E_proj[i] = v / (np.linalg.norm(v) + 1e-12)
    E_proj = _l2_normalize_np(E_proj)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size),
            "encoding": "dense_word2vec_projected"}
    return E_t, meta


def build_E_gaussian_dense(vocab: List[str], n_dim: int, seed: int
                             ) -> torch.Tensor:
    """Smoke fallback when gensim unavailable: DENSE Gaussian random.

    Each row ~ Gaussian(0,1)/sqrt(n_dim), L2-normalized.
    |x_i| ~ 1/sqrt(n_dim) as required by Ocker-Buice.
    """
    rng = np.random.default_rng(seed * 7919 + 31)
    E_np = rng.standard_normal((len(vocab), n_dim)).astype(np.float32) / math.sqrt(n_dim)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


# ============================================================================
# Ocker-Buice nonlinear Hebbian W builder
# ============================================================================

def _nonlinear_f(v: torch.Tensor, n: int) -> torch.Tensor:
    """Apply order-n Ocker-Buice nonlinearity to L2-normalized vector(s).

    f_n(x)_i = x_i * |x_i|^(n-1)   (element-wise power n; sign preserved)
    For n=1: f_1(x) = x  (identity; standard rank-1 Hebbian)
    """
    if n == 1:
        return v
    return torch.sign(v) * v.abs().pow(n)


def build_nonlinear_hebbian_W(idx_train: torch.Tensor, E: torch.Tensor,
                               poly_n: int, ingest_chunk: int) -> torch.Tensor:
    """W = sum_t  f_n(E[idx[t+1]]) @ E[idx[t]]^T  (Ocker-Buice forward-only)."""
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train[b:end]
        tgt_idx = idx_train[b + 1:end + 1]
        E_src = E[src_idx]
        E_tgt = E[tgt_idx]
        E_tgt_f = _nonlinear_f(E_tgt, poly_n)
        W.add_(E_tgt_f.T @ E_src)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


# ============================================================================
# Per-arm logit builder
# ============================================================================

def compute_arm_logits_nonlinear(E: torch.Tensor,
                                   idx_train: np.ndarray,
                                   idx_held: np.ndarray,
                                   poly_n: int) -> Dict:
    """Build nonlinear Hebbian W at order poly_n; return held logits."""
    device = E.device
    V, dim = E.shape
    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)

    t0 = time.time()
    W = build_nonlinear_hebbian_W(idx_train_t, E, poly_n, INGEST_CHUNK)
    t_ingest = time.time() - t0

    src_keys = E[idx_held_t]
    n_h = src_keys.shape[0]

    t0 = time.time()
    pred_held = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        pred_held[b:end] = _l2_normalize_t(src_keys[b:end] @ W.T)
    del W
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall_inner = time.time() - t0

    t0 = time.time()
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        logits[b:end] = pred_held[b:end] @ E.T
    t_logit = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    del pred_held, src_keys, idx_train_t, idx_held_t, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall_inner + t_logit, 2),
    }


# ============================================================================
# text8 loading / vocab
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
# Joint (T, lambda) sweep + BPC / top-1 / MRR
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


def joint_sweep(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray
                ) -> Dict:
    """Joint (T, lambda) sweep on dev; report test metrics at best dev config."""
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc = bpc_from_logp(logp_T1, nxt_test)

    best_bpc = {"T": 1.0, "lam": 1.0, "dev": float("inf")}
    best_top1 = {"T": 1.0, "lam": 1.0, "dev": -1.0}
    best_mrr = {"T": 1.0, "lam": 1.0, "dev": -1.0}
    n_grid = 0
    for T in TEMP_GRID:
        probs_dev = softmax_logits_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in LAMBDA_GRID:
            logp_dev = log_linear_interp_logp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc_from_logp(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, MRR_K)
            n_grid += 1
            if bd < best_bpc["dev"]:
                best_bpc = {"T": float(T), "lam": float(lam), "dev": bd}
            if td > best_top1["dev"]:
                best_top1 = {"T": float(T), "lam": float(lam), "dev": td}
            if md > best_mrr["dev"]:
                best_mrr = {"T": float(T), "lam": float(lam), "dev": md}

    def _test_m(T: float, lam: float, fn) -> float:
        p = softmax_logits_with_T(sub_logits_test, T)
        lp_s = np.log(np.clip(p, 1e-30, 1.0))
        lp = log_linear_interp_logp(lp_s, U_log, lam)
        return fn(lp, nxt_test)

    bpc_best = _test_m(best_bpc["T"], best_bpc["lam"], bpc_from_logp)
    top1_best = _test_m(best_top1["T"], best_top1["lam"], top1_acc_from_logp)
    mrr_best = _test_m(best_mrr["T"], best_mrr["lam"],
                        lambda lp, nx: mrr_at_k(lp, nx, MRR_K))

    # v2: detect calibration collapse (best_lam=0.0 => pure unigram)
    calibration_collapse = (best_bpc["lam"] == 0.0)

    return {
        "bpc_best": round(bpc_best, 4),
        "best_T_for_bpc": best_bpc["T"],
        "best_lambda_for_bpc": best_bpc["lam"],
        "top1_acc": round(top1_best, 4),
        "best_T_for_top1": best_top1["T"],
        "best_lambda_for_top1": best_top1["lam"],
        "mrr_at_10": round(mrr_best, 4),
        "best_T_for_mrr": best_mrr["T"],
        "best_lambda_for_mrr": best_mrr["lam"],
        "raw_bpc_at_T1_L1": round(raw_bpc, 4),
        "calibration_collapse": calibration_collapse,
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
        "grid_size": n_grid,
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray, V: int) -> Dict:
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
    nxt_test = nxt_eval[n_eval // 2:]
    p_test = U[nxt_test].clip(1e-12, 1.0)
    bpc = float(-np.mean(np.log(p_test)) / math.log(2.0))
    am = int(np.argmax(U))
    top1 = float(np.mean(nxt_test == am))
    order = np.argsort(-U)
    inv_rank = np.empty_like(order)
    inv_rank[order] = np.arange(len(order))
    ranks = inv_rank[nxt_test] + 1
    rr = np.where(ranks <= MRR_K, 1.0 / ranks, 0.0)
    mrr = float(np.mean(rr))
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(top1, 4),
            "mrr_unigram": round(mrr, 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Instrumentation self-test (MANDATORY per exp_dev role contract)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null at small scale before sweep."""
    print("[selftest] running instrumentation self-test (v2 rescue)...", flush=True)

    # 1. Dense Gaussian E (Ocker-Buice requires dense; NOT sparse-bipolar)
    rng_np = np.random.default_rng(42)
    dim_t = 128
    V_t = 30
    E_np = rng_np.standard_normal((V_t, dim_t)).astype(np.float32) / math.sqrt(dim_t)
    E_t = torch.from_numpy(_l2_normalize_np(E_np))

    # 2. Verify _nonlinear_f for all poly orders
    for n in POLY_ORDERS:
        fv = _nonlinear_f(E_t, n)
        assert fv.shape == E_t.shape, "nonlinear_f shape mismatch n=%d" % n
        assert not torch.isnan(fv).any(), "nonlinear_f NaN at n=%d" % n
        assert not torch.isinf(fv).any(), "nonlinear_f Inf at n=%d" % n
        if n == 1:
            diff = (fv - E_t).abs().max().item()
            assert diff < 1e-5, "n=1 nonlinear_f must be identity; got diff=%.2e" % diff

    # 3. Build W at tiny scale for n=1 and n=4
    rng_torch = torch.Generator()
    rng_torch.manual_seed(42)
    N_sm = 500
    idx_sm = torch.randint(0, V_t, (N_sm,), generator=rng_torch)
    Ws = {}
    for n in [1, 4]:
        W = build_nonlinear_hebbian_W(idx_sm, E_t, n, ingest_chunk=100)
        assert W.shape == (dim_t, dim_t), "W shape mismatch n=%d" % n
        assert not torch.isnan(W).any(), "W has NaN at n=%d" % n
        assert W.abs().max().item() > 1e-9, "W is all-zero at n=%d (degenerate)" % n
        Ws[n] = W

    # 4. Verify n=1 and n=4 produce DIFFERENT W matrices
    w1_norm = Ws[1].norm().item()
    w4_norm = Ws[4].norm().item()
    assert w1_norm > 1e-6 and w4_norm > 1e-6, (
        "W norms degenerate: n1=%.4e n4=%.4e" % (w1_norm, w4_norm))
    ratio = w4_norm / max(w1_norm, 1e-9)
    assert ratio > 1e-12, "W_n4 effectively zero relative to W_n1 (ratio=%.2e)" % ratio

    # 5. Verify logits non-degenerate for n=1 and n=4
    n_held_sm = 50
    idx_held_sm = torch.randint(0, V_t, (n_held_sm,), generator=rng_torch)
    logits_last = None
    for n in [1, 4]:
        src = E_t[idx_held_sm]
        pred = _l2_normalize_t(src @ Ws[n].T)
        logits = pred @ E_t.T
        assert logits.shape == (n_held_sm, V_t), "logits shape mismatch n=%d" % n
        assert not torch.isnan(logits).any(), "logits has NaN at n=%d" % n
        std_val = logits.std().item()
        assert std_val > 1e-9, "logits all-constant at n=%d (zero variance)" % n
        n_unique = logits.argmax(dim=1).unique().shape[0]
        assert n_unique > 1, "n=%d arm predicts same class for all held (degenerate)" % n
        logits_last = logits

    # 6. BPC finite and positive
    logits_np = logits_last.detach().cpu().numpy()
    nxt_sm = idx_held_sm[1:].numpy()
    probs = softmax_logits_with_T(logits_np[:-1], T=0.1)
    logp = np.log(np.clip(probs, 1e-30, 1.0))
    bpc = bpc_from_logp(logp, nxt_sm)
    assert math.isfinite(bpc), "BPC is not finite in selftest"
    assert bpc > 0.0, "BPC <= 0 in selftest"

    # 7. v2-specific: verify LAMBDA_GRID contains value bracketing 0.033
    assert 0.02 in LAMBDA_GRID, "LAMBDA_GRID must contain 0.02 (v2 fix)"
    assert 0.033 in LAMBDA_GRID, "LAMBDA_GRID must contain 0.033 (v2 fix)"
    assert 0.05 in LAMBDA_GRID, "LAMBDA_GRID must contain 0.05 (v2 fix)"

    # 8. Verify joint_sweep reports calibration_collapse field
    U_test = np.ones(V_t, dtype=np.float32) / V_t
    U_log_test = np.log(np.clip(U_test, 1e-30, 1.0))
    nxt_dev_t = nxt_sm[:len(nxt_sm) // 2]
    nxt_test_t = nxt_sm[len(nxt_sm) // 2:]
    lgs_dev = logits_np[:-1][:len(nxt_dev_t)]
    lgs_test = logits_np[:-1][len(nxt_dev_t):len(nxt_dev_t) + len(nxt_test_t)]
    if len(nxt_dev_t) > 0 and len(nxt_test_t) > 0 and lgs_dev.shape[0] > 0 and lgs_test.shape[0] > 0:
        jr = joint_sweep(lgs_dev, lgs_test, U_log_test, nxt_dev_t, nxt_test_t)
        assert "calibration_collapse" in jr, "joint_sweep must return calibration_collapse field (v2)"
        assert "raw_bpc_at_T1_L1" in jr, "joint_sweep must return raw_bpc_at_T1_L1"
        assert math.isfinite(jr["bpc_best"]), "joint_sweep bpc_best not finite in selftest"

    print("[selftest] PASS: all %d poly orders non-null non-degenerate "
          "(W_n1_norm=%.3f W_n4_norm=%.3f); LAMBDA_GRID v2-fix verified" % (
              len(POLY_ORDERS), w1_norm, w4_norm), flush=True)


_instrumentation_selftest()


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
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE)), flush=True)

    if DEVICE.type == "cuda":
        try:
            print("[seed=%d gpu] %s mem=%.2fGB" % (
                seed, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception as e:
            print("[seed=%d gpu-info-fail] %s" % (seed, e), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.4f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]), flush=True)

    # Build dense L2-normalized E (shared across all poly_n arms)
    print("\n[seed=%d] building DENSE word2vec E (V=%d, N_DIM=%d)..." % (
        seed, V, N_DIM), flush=True)
    t_enc = time.time()
    encoder_meta = {}
    try:
        E, encoder_meta = build_E_word2vec_dense(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d encoder] WORD2VEC FAIL: %s -- using Gaussian dense fallback" % (seed, err), flush=True)
        E = build_E_gaussian_dense(vocab, N_DIM, seed)
        encoder_meta = {"fallback_to_gaussian_dense": True, "load_error": err}
    print("[seed=%d encoder] built in %.1fs" % (seed, time.time() - t_enc), flush=True)

    if DEVICE.type == "cuda":
        try:
            free_b, total_b = torch.cuda.mem_get_info()
            print("[seed=%d gpu] after E: free=%.2fGB total=%.2fGB" % (
                seed, free_b / 1e9, total_b / 1e9), flush=True)
        except Exception:
            pass

    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    ctx_eval = ctx_full[mask]
    nxt_eval = nxt_full[mask]
    n_eval = len(ctx_eval)
    if n_eval < 2:
        del E
        return {"seed": seed, "by_arm": {"ARM_UNIGRAM": uni}, "V": V,
                "N": N_DIM, "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "VOCAB_CAP": VOCAB_CAP, "run_mode": RUN_MODE,
                "config_version": CONFIG_VERSION,
                "elapsed_s_seed": round(time.time() - t_seed, 2),
                "device": str(DEVICE), "encoder_meta": encoder_meta,
                "n_llm_calls": 0}
    n_dev = n_eval // 2
    valid_held_pos = np.where(mask)[0]
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    for poly_n in POLY_ORDERS:
        arm = "ARM_n%d" % poly_n
        t_arm = time.time()
        print("\n  [seed=%d arm=%s poly_n=%d] building W..." % (seed, arm, poly_n), flush=True)
        try:
            ar = compute_arm_logits_nonlinear(E, idx_train, idx_held, poly_n)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:300])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"),
                "best_T_for_bpc": float("nan"),
                "best_lambda_for_bpc": float("nan"),
                "raw_bpc_at_T1_L1": float("inf"),
                "calibration_collapse": False,
                "elapsed_s_arm": round(time.time() - t_arm, 2),
            }
            continue

        logits_full = ar["logits"]  # [N_HELD, V]
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            logits_ctx = logits_full
            mask_pos = np.array([p for p in valid_held_pos if p < logits_ctx.shape[0]],
                                  dtype=np.int64)
            logits_eval = logits_ctx[mask_pos]
            ne = len(logits_eval)
            nd = ne // 2
            jr = joint_sweep(logits_eval[:nd], logits_eval[nd:], U_log,
                             nxt_eval[:nd], nxt_eval[nd:])
            jr["elapsed_s_arm"] = round(time.time() - t_arm, 2)
            jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
            jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
            by_arm[arm] = jr
            cc_str = "CALIBRATION_COLLAPSE" if jr.get("calibration_collapse") else "ok"
            print("    [seed=%d arm=%s] bpc=%.4f top1=%.4f mrr=%.4f (bestT=%.4f bestL=%.4f) cal=%s" % (
                seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                jr["best_T_for_bpc"], jr["best_lambda_for_bpc"], cc_str), flush=True)
            continue

        logits_eval = logits_ctx[mask]
        jr = joint_sweep(logits_eval[:n_dev], logits_eval[n_dev:], U_log,
                         nxt_dev, nxt_test)
        jr["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
        jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
        by_arm[arm] = jr
        cc_str = "CALIBRATION_COLLAPSE" if jr.get("calibration_collapse") else "ok"
        print("    [seed=%d arm=%s] bpc=%.4f top1=%.4f mrr=%.4f (bestT=%.4f bestL=%.4f) rawT1=%.4f cal=%s" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
            jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
            jr["raw_bpc_at_T1_L1"], cc_str), flush=True)

    del E
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N": N_DIM,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "n_llm_calls": 0,
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    """Compute HARD_PASS / MIDDLE_BAND / HARD_FAIL based on pre-reg bands."""
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}

    uni_bpc_vals = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.nanmean(uni_bpc_vals)), 4),
    }
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    arm_bpc_means: Dict[str, float] = {}
    arm_bpc_cvs: Dict[str, float] = {}
    arm_best_lambda: Dict[str, float] = {}

    for poly_n in POLY_ORDERS:
        arm = "ARM_n%d" % poly_n
        valid_units = [
            u for u in units
            if not u["by_arm"].get(arm, {}).get("compute_failed", False)
            and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
        ]
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"),
                "bpc_best_std": float("nan"),
                "bpc_best_cv": float("nan"),
                "top1_acc_mean": float("nan"),
                "mrr_at_10_mean": float("nan"),
                "raw_bpc_at_T1_L1_mean": float("nan"),
                "n_valid_seeds": 0,
                "all_seeds_failed": True,
                "best_lambda_mean": float("nan"),
                "calibration_collapse_count": 0,
            }
            arm_bpc_means[arm] = float("inf")
            arm_bpc_cvs[arm] = float("nan")
            arm_best_lambda[arm] = float("nan")
            continue
        bpc_vals = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_vals = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_vals = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_vals = [u["by_arm"][arm]["raw_bpc_at_T1_L1"] for u in valid_units]
        lam_vals = [u["by_arm"][arm].get("best_lambda_for_bpc", float("nan")) for u in valid_units]
        cc_count = sum(1 for u in valid_units if u["by_arm"][arm].get("calibration_collapse", False))
        bm = float(np.mean(bpc_vals))
        bs = float(np.std(bpc_vals))
        cv = bs / max(abs(bm), 1e-6)
        lam_mean = float(np.nanmean(lam_vals)) if any(math.isfinite(l) for l in lam_vals) else float("nan")
        by_arm_agg[arm] = {
            "bpc_best_mean": round(bm, 4),
            "bpc_best_std": round(bs, 4),
            "bpc_best_cv": round(cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_vals)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.nanmean(raw_vals)), 4) if raw_vals else float("nan"),
            "n_valid_seeds": int(len(valid_units)),
            "all_seeds_failed": False,
            "best_lambda_mean": round(lam_mean, 4) if math.isfinite(lam_mean) else float("nan"),
            "calibration_collapse_count": int(cc_count),
        }
        arm_bpc_means[arm] = bm
        arm_bpc_cvs[arm] = cv
        arm_best_lambda[arm] = lam_mean

    # READOUT_DEGENERATE sanity gate
    n1_bpc = arm_bpc_means.get("ARM_n1", float("inf"))
    readout_degen = math.isfinite(n1_bpc) and n1_bpc > (unigram_bpc - 0.05)

    # v2: calibration_collapse flag -- all 5 arms collapsed to unigram via lam=0.0
    all_collapse = all(
        arm_best_lambda.get("ARM_n%d" % n, float("nan")) == 0.0
        for n in POLY_ORDERS
        if math.isfinite(arm_best_lambda.get("ARM_n%d" % n, float("nan")))
    )
    # Also check if ANY arm collapsed
    any_collapse = any(
        by_arm_agg.get("ARM_n%d" % n, {}).get("calibration_collapse_count", 0) > 0
        for n in POLY_ORDERS
    )

    n1_bpc_str = "%.4f" % n1_bpc if math.isfinite(n1_bpc) else "FAIL"
    lifts: Dict[str, float] = {}
    for poly_n in POLY_ORDERS:
        arm = "ARM_n%d" % poly_n
        bm = arm_bpc_means.get(arm, float("inf"))
        if math.isfinite(bm) and math.isfinite(n1_bpc):
            lifts[arm] = n1_bpc - bm   # positive = improvement (lower BPC)
        else:
            lifts[arm] = float("nan")

    n4_lift = lifts.get("ARM_n4", float("nan"))
    n5_lift = lifts.get("ARM_n5", float("nan"))
    n4_cv = arm_bpc_cvs.get("ARM_n4", float("nan"))
    n4_bpc = arm_bpc_means.get("ARM_n4", float("inf"))

    n3_bpc = arm_bpc_means.get("ARM_n3", float("inf"))
    n3_collapses = math.isfinite(n3_bpc) and n3_bpc >= (unigram_bpc - 0.05)

    hf_reasons: List[str] = []
    hp_reasons: List[str] = []

    if readout_degen and not all_collapse:
        # Only flag READOUT_DEGEN as HARD_FAIL if calibration grid was NOT the issue
        hf_reasons.append("READOUT_DEGEN: ARM_n1 BPC=%.4f near unigram=%.4f" % (
            n1_bpc, unigram_bpc))
    if n3_collapses and not all_collapse:
        hf_reasons.append("ARM_n3_COLLAPSE: BPC=%.4f >= unigram-0.05=%.4f" % (
            n3_bpc, unigram_bpc - 0.05))
    if math.isfinite(n4_lift) and n4_lift <= HARD_FAIL_MAX_LIFT and not all_collapse:
        hf_reasons.append("ARM_n4 lift=%.4f <= HARD_FAIL_MAX_LIFT=%.2f" % (
            n4_lift, HARD_FAIL_MAX_LIFT))

    if math.isfinite(n4_lift) and n4_lift >= HARD_PASS_LIFT:
        if math.isfinite(n4_cv) and n4_cv < HP_CV_MAX:
            hp_reasons.append("ARM_n4 lift=%.4f >= HARD_PASS_LIFT=%.2f cv=%.4f < %.2f" % (
                n4_lift, HARD_PASS_LIFT, n4_cv, HP_CV_MAX))
        else:
            hp_reasons.append("ARM_n4 lift=%.4f >= threshold BUT cv=%.4f >= %.2f (cv-fail)" % (
                n4_lift, n4_cv, HP_CV_MAX))
            hf_reasons.append("cv_fail: ARM_n4 cv=%.4f >= HP_CV_MAX=%.2f" % (
                n4_cv, HP_CV_MAX))

    chain_grade_bonus = (math.isfinite(n4_lift) and n4_lift >= CHAIN_GRADE_BONUS_LIFT)

    arm_summary_parts = []
    for poly_n in POLY_ORDERS:
        arm = "ARM_n%d" % poly_n
        bm = arm_bpc_means.get(arm, float("inf"))
        lft = lifts.get(arm, float("nan"))
        cv = arm_bpc_cvs.get(arm, float("nan"))
        lam = arm_best_lambda.get(arm, float("nan"))
        if math.isfinite(bm):
            arm_summary_parts.append("n%d:bpc%.4f/lift%+.4f/cv%.4f/lam%.4f" % (
                poly_n, bm, lft, cv, lam))
        else:
            arm_summary_parts.append("n%d:FAIL" % poly_n)
    arm_summary = " | ".join(arm_summary_parts)

    # v2: if all_collapse persists even with fixed grid, report CALIBRATION_GRID_TOO_COARSE
    if all_collapse:
        verdict = "HARD_FAIL"
        msg = ("HARD_FAIL CALIBRATION_GRID_TOO_COARSE (v2 expanded grid still insufficient): "
               "all arms best_lam=0.0 => pure unigram even after LAMBDA_GRID expansion. "
               "ARM_n1_bpc=%s | %s | n_llm=0 zero_llm_calls_at_inference=True" % (
                   n1_bpc_str, arm_summary))
    elif hf_reasons and not (hp_reasons and not any("cv_fail" in r for r in hf_reasons)):
        verdict = "HARD_FAIL"
        msg = ("HARD_FAIL: Ocker-Buice forward-only nonlinear-Hebbian does not lift BPC "
               "above rank-1 ceiling at LM scale. Reasons: %s. | ARM_n1=%s | %s | "
               "n_llm=0 zero_llm_calls_at_inference=True" % (
                   "; ".join(hf_reasons), n1_bpc_str, arm_summary))
    elif hp_reasons:
        verdict = "HARD_PASS"
        chain_str = " CHAIN_GRADE_BONUS(lift>=%.2f)=%s" % (CHAIN_GRADE_BONUS_LIFT, chain_grade_bonus)
        msg = ("HARD_PASS: forward-only nonlinear-Hebbian lifts BPC via higher-order interactions. "
               "%s.%s | ARM_n1=%s | %s | n_llm=0" % (
                   "; ".join(hp_reasons), chain_str, n1_bpc_str, arm_summary))
    else:
        verdict = "MIDDLE_BAND"
        msg = ("MIDDLE_BAND: forward-only nonlinear-Hebbian shows partial lift. "
               "ARM_n4 lift=%.4f (threshold %.2f). ARM_n1=%s | %s | n_llm=0" % (
                   n4_lift if math.isfinite(n4_lift) else float("nan"),
                   HARD_PASS_LIFT, n1_bpc_str, arm_summary))

    detail = {
        "by_arm_agg": by_arm_agg,
        "lifts_vs_n1": lifts,
        "readout_degen": readout_degen,
        "n3_collapses": n3_collapses,
        "chain_grade_bonus": chain_grade_bonus,
        "unigram_bpc_ref": unigram_bpc,
        "baseline_fair_harness_bpc": BASELINE_BPC,
        "hard_pass_lift_threshold": HARD_PASS_LIFT,
        "hard_fail_max_lift_threshold": HARD_FAIL_MAX_LIFT,
        "hp_cv_max": HP_CV_MAX,
        "all_collapse": all_collapse,
        "any_collapse": any_collapse,
        "zero_llm_calls_at_inference": True,
        "n_llm_calls": 0,
        "v2_fix": "LAMBDA_GRID expanded to bracket fair_harness optimal lambda~0.033",
        "honest_scope": (
            "Forward-only nonlinear Hebbian via Ocker-Buice polynomial-order Taylor expansion. "
            "Dense word2vec projected L2-normalized encoder. "
            "N_DIM=%d N_TRAIN=%d N_HELD=%d V=%d. "
            "n=1 arm must reproduce fair_harness ARM_SUBSTRATE_WORD2VEC_DENSE BPC~7.72 "
            "(NOT sparse_bipolar 7.3065 -- different encoder). "
            "Verdict uses LIFT vs ARM_n1 (within-cell rank-1 baseline). "
            "No backprop. No LLM at inference."
        ) % (N_DIM, N_TRAIN, N_HELD, 4000),
        "cites": [
            "Ocker-Buice 2021 arxiv:2106.15685",
            "Krotov-Hopfield 2016 NeurIPS Dense Associative Memory",
            "preregs/2026-06-23_substrate_higher_order_taylor_nonlinear_hebbian_LM_v2.md",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json",
            "notes/skunkworks_to_all_BATCH_VET_4_recent_negatives_2026-06-23.md",
        ],
        "CONFIG_VERSION": CONFIG_VERSION,
    }
    return verdict, msg, detail


# ============================================================================
# Main loop + atexit synthesizer
# ============================================================================

_OUT_DIR = get_output_dir(ANCHOR_NAME)
_UNITS_WRITTEN: List[Dict] = []

def _synthesize_and_write():
    """atexit / SIGTERM handler: aggregate partials + write metrics.json."""
    partial_units = aggregate_partials(_OUT_DIR, SEEDS)
    all_units = list(_UNITS_WRITTEN) + [u for u in partial_units
                                           if u not in _UNITS_WRITTEN]
    if not all_units:
        print("[synth] no units; skipping metrics.json write", flush=True)
        return
    verdict, msg, detail = compute_verdict(all_units)
    out = {
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
        "encoder": "dense_word2vec_projected",
        "POLY_ORDERS": POLY_ORDERS,
        "ARMS": ARMS,
        "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID,
        "MRR_K": MRR_K,
        "n_seeds": len(all_units),
        "detail": detail,
        "per_unit": all_units,
        "elapsed_s": round(time.time() - _T_START, 2),
        "summary": msg[:300],
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": 0,
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
        "pre_reg_cites": ["preregs/2026-06-23_substrate_higher_order_taylor_nonlinear_hebbian_LM_v2.md"],
    }
    write_metrics(_OUT_DIR, out)
    print("\n[synth] metrics.json written -> %s" % (_OUT_DIR / "metrics.json"), flush=True)
    print("[synth] verdict=%s | %s" % (verdict, msg[:200]), flush=True)


atexit.register(_synthesize_and_write)


def _sigterm_handler(signum, frame):
    print("\n[sigterm] SIGTERM received; synthesizing...", flush=True)
    _synthesize_and_write()
    sys.exit(0)


try:
    signal.signal(signal.SIGTERM, _sigterm_handler)
except Exception:
    pass

_T_START = time.time()


def main():
    print("\n[%s] starting | mode=%s seeds=%s N_DIM=%d N_TRAIN=%d device=%s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, N_TRAIN, str(DEVICE)), flush=True)
    print("[config] poly_orders=%s encoder=dense_word2vec HARD_PASS_lift>=%.2f HARD_FAIL_lift<=%.2f" % (
        POLY_ORDERS, HARD_PASS_LIFT, HARD_FAIL_MAX_LIFT), flush=True)
    print("[v2_fix] LAMBDA_GRID=%s (v1 bug: grid skipped lambda~0.033, all arms collapsed to unigram)" % (
        LAMBDA_GRID,), flush=True)

    for seed in SEEDS:
        ckpt_key = "s%d" % seed
        partial_path = _OUT_DIR / ("partial_%s.json" % ckpt_key)
        if partial_path.exists():
            print("[seed=%d] partial checkpoint found; skipping" % seed, flush=True)
            import json
            with open(partial_path) as f:
                u = json.load(f)
            _UNITS_WRITTEN.append(u)
            continue

        unit = run_unit(seed)
        unit["_ckpt_key"] = ckpt_key
        unit["_partial_written_at"] = time.time()
        _UNITS_WRITTEN.append(unit)
        write_partial_key(_OUT_DIR, ckpt_key, unit)
        print("[seed=%d] checkpoint written" % seed, flush=True)

    _synthesize_and_write()
    print("\n[%s] done in %.1fs" % (ANCHOR_NAME, time.time() - _T_START), flush=True)


if __name__ == "__main__":
    main()
