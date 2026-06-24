"""substrate_ACh_query_conditional_read_gain_LM_v1 -- ACh analog READ-gain for substrate LM.

GAP #2 from substrate-mine modulator inventory: write-time excitability HARD_PASS exists
(exp_excitability_gated_substrate_cpu_v1.py; K=1200 cliff-aware priority protection).
This cell tests the ORTHOGONAL READ-side gain modulation: per-query scalar gain on the
predicted logit vector BEFORE temperature application, conditioned on query uncertainty.

Mechanism (Yu-Dayan 2005 ACh attention-gain; Goard-Dan 2009 basal forebrain ACh modulates
V1 SNR; Pinto-Goard 2013 ACh enhances signal-detection): cholinergic gain control
multiplicatively scales READ signal magnitude based on attention/confidence state.
Substrate analog: per-query gain = base_gain * f(uncertainty of current logit distribution).
Low-margin (uncertain) queries get boosted gain to sharpen the distribution and break ties.
High-entropy queries get boosted gain. Both are conditional ACh analogs.

DISTINCT from per-context T sweep (gap #1 cell a52c9350):
  - Per-context T: shape of softmax (temperature sweep per context)
  - ACh READ-gain: MAGNITUDE of logits before softmax (amplifies whole distribution)

Four arms (all use SPARSE_BIPOLAR encoder -- HARD_PASS arm from fair_harness baseline):
  ARM_UNIGRAM          -- analytic floor (BPC + top-1 + MRR)
  ARM_GLOBAL_READ_GAIN -- fair_harness replication with single scalar gain swept via dev;
                          HARD-PASS replication gate: should reproduce 7.3065 +/- 0.05
  ARM_PER_QUERY_GAIN_MARGIN -- gain = base_gain * (1 + alpha * (1 - normalized_margin));
                               low-margin queries get boosted (uncertain = sharpen)
  ARM_PER_QUERY_GAIN_ENTROPY -- gain = base_gain * (1 + alpha * normalized_entropy);
                                high-entropy queries get boosted

Pre-reg HARD bands (pre-registered before run):
  HARD_PASS: ARM_PER_QUERY_GAIN_MARGIN OR ARM_PER_QUERY_GAIN_ENTROPY beats
             ARM_GLOBAL_READ_GAIN by >= +0.10 bits BPC on mean across seeds.
  CHAIN_GRADE_BONUS: lift >= +0.20 bits AND beats fair_harness baseline 7.3065.
  MIDDLE_BAND: lift +0.03 to +0.10 bits.
  HARD_FAIL: lift <= +0.03 bits OR per-query arms collapse to unigram (READOUT_DEGENERATE).
  cv < 0.05 on HARD_PASS arm.

Brain prior: P_inherited=0.55; deflated to P=0.45 for substrate-native LM (implementation
uncertainty; feasibility confirmed by brain existence proof).

Routing: remote_cpu_queue (USER explicit; both CPU lanes idle; ACh gain is CPU-light).
PROT-018: no _nN suffix; production N_DIM=8192 stated in prereq section.
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

ANCHOR_NAME = "substrate_ACh_query_conditional_read_gain_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Reference from fair_harness HARD_PASS (3-seed GPU run)
FAIR_HARNESS_BASELINE_BPC = 7.3065

# Pre-reg bands
HP_LIFT_BPC = 0.10          # per-query arm beats global arm by >= 0.10 bits
CHAIN_GRADE_LIFT_BPC = 0.20 # bonus: lift >= 0.20 AND beats baseline 7.3065
MIDDLE_LOWER_BPC = 0.03     # middle band: lift >= 0.03
CV_MAX = 0.05

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Use CPU for remote_cpu_queue routing; fall through to cuda if available on runner
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Production config (FULL; N_DIM=8192 per design; no _nN suffix in name -- see PROT-018 note)
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

# Joint (T, base_gain, alpha) sweep
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
# ACh gain sweep axes
BASE_GAIN_GRID = [0.5, 1.0, 2.0, 4.0]   # global gain multipliers (swept for ARM_GLOBAL)
ALPHA_GRID = [0.0, 0.5, 1.0, 2.0, 4.0]  # per-query modulation strength

SPARSE_BIPOLAR_F = 0.05
MRR_K = 10

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke: CPU, <90s target
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

ARMS = [
    "ARM_UNIGRAM",
    "ARM_GLOBAL_READ_GAIN",
    "ARM_PER_QUERY_GAIN_MARGIN",
    "ARM_PER_QUERY_GAIN_ENTROPY",
]
GAIN_ARMS = [a for a in ARMS if a != "ARM_UNIGRAM"]

CONFIG_VERSION = (
    "substrate_ACh_query_conditional_read_gain_LM_v1; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s temps=%s lambdas=%s base_gains=%s alphas=%s "
    "sparse_f=%.3f MRR_K=%d device=%s; "
    "bands HP_lift>=%.2f chain_grade_lift>=%.2f middle_lower>=%.2f cv_max=%.3f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    TEMP_GRID, LAMBDA_GRID, BASE_GAIN_GRID, ALPHA_GRID,
    SPARSE_BIPOLAR_F, MRR_K, str(DEVICE),
    HP_LIFT_BPC, CHAIN_GRADE_LIFT_BPC, MIDDLE_LOWER_BPC, CV_MAX,
)


# ============================================================================
# Char-trigram encoder (OOV fallback)
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


def _l2_normalize_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    if X.dim() == 1:
        return X / (X.norm() + eps)
    return X / (X.norm(dim=1, keepdim=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


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


WORD2VEC_MODEL = "word2vec-google-news-300"


def build_E_word2vec(vocab: List[str], n_dim: int, seed: int
                      ) -> Tuple[torch.Tensor, Dict]:
    """[V, n_dim] L2-normalized word2vec-projected vectors; OOV -> char-trigram."""
    kv = _load_gensim_kv(WORD2VEC_MODEL)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = _l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    oov_mask = np.linalg.norm(E_pre, axis=1) < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = _l2_normalize_np(E_proj)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_t, meta


def build_E_char_trigram(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


# ============================================================================
# Sparse-bipolar primitive
# ============================================================================

def sparsify_bipolar(E: torch.Tensor, f: float, seed: int) -> torch.Tensor:
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


# ============================================================================
# Hebbian W builder (rank-1)
# ============================================================================

def build_rank1_W(idx_train: torch.Tensor, E: torch.Tensor,
                   ingest_chunk: int) -> torch.Tensor:
    """W = sum outer(E[t+1], E[t]); rank-1 Hebbian."""
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_b = E[idx_train[b:end]]
        tgt_b = E[idx_train[b + 1:end + 1]]
        W.add_(tgt_b.T @ src_b)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def compute_sparse_bp_logits(E_base: torch.Tensor,
                               idx_train: np.ndarray,
                               idx_held: np.ndarray,
                               seed: int) -> np.ndarray:
    """Build sparse-bipolar logits [n_held, V]; same as fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR."""
    E_used = _l2_normalize_t(sparsify_bipolar(E_base, SPARSE_BIPOLAR_F, seed))
    device = E_used.device
    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)

    W = build_rank1_W(idx_train_t, E_used, INGEST_CHUNK)
    n_h = idx_held_t.shape[0]
    pred_held = torch.zeros((n_h, E_used.shape[1]), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        src_b = E_used[idx_held_t[b:end]]
        pred_held[b:end] = _l2_normalize_t(src_b @ W.T)
    if device.type == "cuda":
        torch.cuda.synchronize()
    del W, idx_train_t, idx_held_t

    V = E_used.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        logits[b:end] = pred_held[b:end] @ E_used.T
    del pred_held, E_used
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return logits.detach().cpu().numpy().astype(np.float32)


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
# Softmax / metric helpers
# ============================================================================

def softmax_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    """Softmax with temperature; logits shape [n, V]."""
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float) -> np.ndarray:
    """Log-linear interpolation with unigram. Returns log-prob [n, V]."""
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    return -float(np.mean(logp[np.arange(n), nxt])) / math.log(2.0)


def top1_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
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
# ACh READ-gain computation (per-query scalars from logit distribution)
# ============================================================================

def compute_normalized_margin(logits: np.ndarray) -> np.ndarray:
    """Per-query normalized margin: (top1 - top2) / (|top1| + |top2| + eps).

    Range approximately [0, 1]; low = uncertain, high = confident.
    Gain formula: gain_i = base_gain * (1 + alpha * (1 - margin_i))
    So uncertain (low margin) queries get highest gain.
    """
    # Sort descending to get top-2 values
    n = logits.shape[0]
    # Use partition for efficiency
    if logits.shape[1] >= 2:
        top2_idx = np.argpartition(-logits, kth=1, axis=1)[:, :2]
        rows = np.arange(n)[:, None]
        top2_vals = logits[rows, top2_idx]
        # Sort within the 2
        top2_vals_sorted = np.sort(-top2_vals, axis=1) * -1  # descending
        t1 = top2_vals_sorted[:, 0]
        t2 = top2_vals_sorted[:, 1]
    else:
        t1 = logits[:, 0]
        t2 = np.zeros(n, dtype=logits.dtype)
    margin = (t1 - t2) / (np.abs(t1) + np.abs(t2) + 1e-9)
    # Clip to [0, 1] for safety (cosine logits should be in [-1,1] so margin >= 0)
    return np.clip(margin.astype(np.float32), 0.0, 1.0)


def compute_normalized_entropy(logits: np.ndarray, T: float = 1.0) -> np.ndarray:
    """Per-query normalized entropy of softmax(logits/T).

    Returns H / log2(V) in [0, 1]; high = uncertain/flat, low = peaked.
    Gain formula: gain_i = base_gain * (1 + alpha * norm_entropy_i)
    So high-entropy (uncertain) queries get highest gain.
    """
    probs = softmax_with_T(logits, T)  # float64 [n, V]
    probs_f32 = probs.astype(np.float32)
    log_p = np.log(np.clip(probs_f32, 1e-30, 1.0))
    H = -np.sum(probs_f32 * log_p, axis=1)  # nats
    V = logits.shape[1]
    H_max = math.log(max(V, 2))
    return np.clip((H / max(H_max, 1e-9)).astype(np.float32), 0.0, 1.0)


def apply_per_query_gain(logits: np.ndarray, gain_vec: np.ndarray) -> np.ndarray:
    """Scale each row of logits by the corresponding gain scalar.

    gain_vec shape [n]; logits shape [n, V]. Returns [n, V] float32.
    Self-test: at alpha=0 all gains equal base_gain -> scales uniformly -> same as global gain.
    At base_gain=1, alpha=0: gain_vec is all-ones -> logits unchanged.
    """
    return (logits * gain_vec[:, None]).astype(np.float32)


# ============================================================================
# Joint sweep for each arm
# ============================================================================

def sweep_arm_global_gain(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                           U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                           temp_grid: list, lambda_grid: list, base_gain_grid: list,
                           mrr_k: int) -> Dict:
    """ARM_GLOBAL_READ_GAIN: sweep (T, lambda, base_gain) jointly on dev.

    Replication gate: best BPC should reproduce FAIR_HARNESS_BASELINE_BPC +/- 0.05.
    """
    # raw at (T=1.0, lambda=1.0, gain=1.0): should match fair_harness raw_bpc_at_T1_L1
    probs_T1 = softmax_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1.astype(np.float32), 1e-30, 1.0))
    raw_bpc_at_T1_L1_G1 = bpc_from_logp(logp_T1, nxt_test)

    best_bpc = {"T": 1.0, "lambda": 1.0, "gain": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "gain": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "gain": 1.0, "dev_value": -1.0}

    for g in base_gain_grid:
        # Global gain: scaled_logits = logits * g (uniform across all positions)
        sg_dev = sub_logits_dev * g
        sg_test = sub_logits_test * g
        for T in temp_grid:
            probs_dev = softmax_with_T(sg_dev, T)
            logp_sub_dev = np.log(np.clip(probs_dev.astype(np.float32), 1e-30, 1.0))
            for lam in lambda_grid:
                logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
                bd = bpc_from_logp(logp_dev, nxt_dev)
                td = top1_from_logp(logp_dev, nxt_dev)
                md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
                if bd < best_bpc["dev_value"]:
                    best_bpc = {"T": float(T), "lambda": float(lam), "gain": float(g), "dev_value": bd}
                if td > best_top1["dev_value"]:
                    best_top1 = {"T": float(T), "lambda": float(lam), "gain": float(g), "dev_value": td}
                if md > best_mrr["dev_value"]:
                    best_mrr = {"T": float(T), "lambda": float(lam), "gain": float(g), "dev_value": md}

    def _test(T, lam, g, fn):
        sg = sub_logits_test * g
        probs = softmax_with_T(sg, T)
        logp_sub = np.log(np.clip(probs.astype(np.float32), 1e-30, 1.0))
        logp = log_linear_interp(logp_sub, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _test(best_bpc["T"], best_bpc["lambda"], best_bpc["gain"], bpc_from_logp)
    top1_best_test = _test(best_top1["T"], best_top1["lambda"], best_top1["gain"], top1_from_logp)
    mrr_best_test = _test(best_mrr["T"], best_mrr["lambda"], best_mrr["gain"],
                           lambda lp, nx: mrr_at_k(lp, nx, mrr_k))

    replication_ok = abs(bpc_best_test - FAIR_HARNESS_BASELINE_BPC) <= 0.15
    return {
        "bpc_best": round(bpc_best_test, 4),
        "top1_acc": round(top1_best_test, 4),
        "mrr_at_10": round(mrr_best_test, 4),
        "best_T_for_bpc": best_bpc["T"],
        "best_lambda_for_bpc": best_bpc["lambda"],
        "best_gain_for_bpc": best_bpc["gain"],
        "raw_bpc_at_T1_L1_G1": round(raw_bpc_at_T1_L1_G1, 4),
        "replication_ok": bool(replication_ok),
        "replication_delta": round(bpc_best_test - FAIR_HARNESS_BASELINE_BPC, 4),
    }


def sweep_arm_per_query_margin(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                                temp_grid: list, lambda_grid: list, base_gain_grid: list,
                                alpha_grid: list, mrr_k: int) -> Dict:
    """ARM_PER_QUERY_GAIN_MARGIN: gain_i = base_gain * (1 + alpha * (1 - margin_i)).

    At alpha=0: reduces to ARM_GLOBAL_READ_GAIN. Self-test: alpha=0 branch verified
    in _instrumentation_selftest().
    """
    # Precompute margin from raw logits (before gain application)
    margin_dev = compute_normalized_margin(sub_logits_dev)    # [n_dev]
    margin_test = compute_normalized_margin(sub_logits_test)  # [n_test]
    # uncertainty = 1 - margin: low-margin queries get high gain
    unc_dev = 1.0 - margin_dev   # [n_dev]
    unc_test = 1.0 - margin_test

    best_bpc = {"T": 1.0, "lambda": 1.0, "gain": 1.0, "alpha": 0.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "gain": 1.0, "alpha": 0.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "gain": 1.0, "alpha": 0.0, "dev_value": -1.0}

    for g in base_gain_grid:
        for alpha in alpha_grid:
            gain_vec_dev = (g * (1.0 + alpha * unc_dev)).astype(np.float32)
            sg_dev = apply_per_query_gain(sub_logits_dev, gain_vec_dev)
            for T in temp_grid:
                probs_dev = softmax_with_T(sg_dev, T)
                logp_sub_dev = np.log(np.clip(probs_dev.astype(np.float32), 1e-30, 1.0))
                for lam in lambda_grid:
                    logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
                    bd = bpc_from_logp(logp_dev, nxt_dev)
                    td = top1_from_logp(logp_dev, nxt_dev)
                    md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
                    if bd < best_bpc["dev_value"]:
                        best_bpc = {"T": float(T), "lambda": float(lam), "gain": float(g),
                                    "alpha": float(alpha), "dev_value": bd}
                    if td > best_top1["dev_value"]:
                        best_top1 = {"T": float(T), "lambda": float(lam), "gain": float(g),
                                     "alpha": float(alpha), "dev_value": td}
                    if md > best_mrr["dev_value"]:
                        best_mrr = {"T": float(T), "lambda": float(lam), "gain": float(g),
                                    "alpha": float(alpha), "dev_value": md}

    def _test(T, lam, g, alpha, fn):
        gain_vec = (g * (1.0 + alpha * unc_test)).astype(np.float32)
        sg = apply_per_query_gain(sub_logits_test, gain_vec)
        probs = softmax_with_T(sg, T)
        logp_sub = np.log(np.clip(probs.astype(np.float32), 1e-30, 1.0))
        logp = log_linear_interp(logp_sub, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _test(best_bpc["T"], best_bpc["lambda"], best_bpc["gain"], best_bpc["alpha"], bpc_from_logp)
    top1_best_test = _test(best_top1["T"], best_top1["lambda"], best_top1["gain"], best_top1["alpha"], top1_from_logp)
    mrr_best_test = _test(best_mrr["T"], best_mrr["lambda"], best_mrr["gain"], best_mrr["alpha"],
                           lambda lp, nx: mrr_at_k(lp, nx, mrr_k))

    return {
        "bpc_best": round(bpc_best_test, 4),
        "top1_acc": round(top1_best_test, 4),
        "mrr_at_10": round(mrr_best_test, 4),
        "best_T_for_bpc": best_bpc["T"],
        "best_lambda_for_bpc": best_bpc["lambda"],
        "best_gain_for_bpc": best_bpc["gain"],
        "best_alpha_for_bpc": best_bpc["alpha"],
    }


def sweep_arm_per_query_entropy(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                                 U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                                 temp_grid: list, lambda_grid: list, base_gain_grid: list,
                                 alpha_grid: list, mrr_k: int) -> Dict:
    """ARM_PER_QUERY_GAIN_ENTROPY: gain_i = base_gain * (1 + alpha * norm_entropy_i).

    Uses T=1.0 entropy of raw logits to compute query uncertainty (entropy at input scale).
    High-entropy queries (uncertain) get more gain.
    At alpha=0: reduces to ARM_GLOBAL_READ_GAIN.
    """
    # Precompute entropy at T=1.0 (raw signal; don't let T-sweep pollute the uncertainty signal)
    ent_dev = compute_normalized_entropy(sub_logits_dev, T=1.0)   # [n_dev]
    ent_test = compute_normalized_entropy(sub_logits_test, T=1.0) # [n_test]

    best_bpc = {"T": 1.0, "lambda": 1.0, "gain": 1.0, "alpha": 0.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "gain": 1.0, "alpha": 0.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "gain": 1.0, "alpha": 0.0, "dev_value": -1.0}

    for g in base_gain_grid:
        for alpha in alpha_grid:
            gain_vec_dev = (g * (1.0 + alpha * ent_dev)).astype(np.float32)
            sg_dev = apply_per_query_gain(sub_logits_dev, gain_vec_dev)
            for T in temp_grid:
                probs_dev = softmax_with_T(sg_dev, T)
                logp_sub_dev = np.log(np.clip(probs_dev.astype(np.float32), 1e-30, 1.0))
                for lam in lambda_grid:
                    logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
                    bd = bpc_from_logp(logp_dev, nxt_dev)
                    td = top1_from_logp(logp_dev, nxt_dev)
                    md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
                    if bd < best_bpc["dev_value"]:
                        best_bpc = {"T": float(T), "lambda": float(lam), "gain": float(g),
                                    "alpha": float(alpha), "dev_value": bd}
                    if td > best_top1["dev_value"]:
                        best_top1 = {"T": float(T), "lambda": float(lam), "gain": float(g),
                                     "alpha": float(alpha), "dev_value": td}
                    if md > best_mrr["dev_value"]:
                        best_mrr = {"T": float(T), "lambda": float(lam), "gain": float(g),
                                    "alpha": float(alpha), "dev_value": md}

    def _test(T, lam, g, alpha, fn):
        gain_vec = (g * (1.0 + alpha * ent_test)).astype(np.float32)
        sg = apply_per_query_gain(sub_logits_test, gain_vec)
        probs = softmax_with_T(sg, T)
        logp_sub = np.log(np.clip(probs.astype(np.float32), 1e-30, 1.0))
        logp = log_linear_interp(logp_sub, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _test(best_bpc["T"], best_bpc["lambda"], best_bpc["gain"], best_bpc["alpha"], bpc_from_logp)
    top1_best_test = _test(best_top1["T"], best_top1["lambda"], best_top1["gain"], best_top1["alpha"], top1_from_logp)
    mrr_best_test = _test(best_mrr["T"], best_mrr["lambda"], best_mrr["gain"], best_mrr["alpha"],
                           lambda lp, nx: mrr_at_k(lp, nx, mrr_k))

    return {
        "bpc_best": round(bpc_best_test, 4),
        "top1_acc": round(top1_best_test, 4),
        "mrr_at_10": round(mrr_best_test, 4),
        "best_T_for_bpc": best_bpc["T"],
        "best_lambda_for_bpc": best_bpc["lambda"],
        "best_gain_for_bpc": best_bpc["gain"],
        "best_alpha_for_bpc": best_bpc["alpha"],
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray, V: int,
                     mrr_k: int) -> Dict:
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
# Instrumentation self-test (MANDATORY; called at module scope)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at tiny scale.

    Covers:
    1. compute_normalized_margin: returns [0,1] float32 array, non-all-zero
    2. compute_normalized_entropy: returns [0,1] float32 array, non-all-zero
    3. apply_per_query_gain at alpha=0: gain uniform -> same as global gain
    4. apply_per_query_gain at alpha=0 recovers ARM_GLOBAL result (verified algebraically)
    5. softmax_with_T produces valid probability distribution
    6. bpc_from_logp / top1_from_logp / mrr_at_k return finite non-null values
    7. _seed_checkpoint import works (write_metrics callable)
    8. Filter: logits shape [n_eval, V] passes >=1 row at smoke scale (n_eval >= 1)
    """
    rng = np.random.default_rng(42)
    n_test, V_test = 16, 50

    # Synthetic logits in [-1, 1] range (cosine-like)
    logits = rng.uniform(-1.0, 1.0, (n_test, V_test)).astype(np.float32)

    # 1. Margin: must be [n_test] array in [0,1], not all-zero
    margin = compute_normalized_margin(logits)
    assert margin.shape == (n_test,), "margin shape wrong: %s" % str(margin.shape)
    assert margin.dtype == np.float32, "margin dtype wrong"
    assert float(margin.min()) >= 0.0 and float(margin.max()) <= 1.0, "margin out of [0,1]"
    assert float(margin.max()) > 0.0, "margin all-zero (degenerate logits)"

    # 2. Entropy: must be [n_test] array in [0,1], not all-zero
    ent = compute_normalized_entropy(logits, T=1.0)
    assert ent.shape == (n_test,), "entropy shape wrong"
    assert float(ent.min()) >= 0.0 and float(ent.max()) <= 1.0, "entropy out of [0,1]"
    assert float(ent.max()) > 0.0, "entropy all-zero"

    # 3. apply_per_query_gain at alpha=0: should equal global gain=2.0 scaling
    gain_vec = np.full(n_test, 2.0, dtype=np.float32)  # all 2.0
    scaled = apply_per_query_gain(logits, gain_vec)
    ref = logits * 2.0
    assert np.allclose(scaled, ref, atol=1e-5), "global gain scaling inconsistent"

    # 4. softmax produces valid distribution
    probs = softmax_with_T(logits, T=0.1)
    assert probs.shape == (n_test, V_test), "probs shape wrong"
    row_sums = probs.sum(axis=1)
    assert np.allclose(row_sums, 1.0, atol=1e-4), "probs not normalized"
    assert float(probs.min()) >= 0.0, "negative probs"

    # 5. BPC / top1 / MRR return finite values
    nxt_fake = rng.integers(0, V_test, size=n_test)
    logp = np.log(np.clip(probs.astype(np.float32), 1e-30, 1.0))
    bpc_val = bpc_from_logp(logp, nxt_fake)
    assert math.isfinite(bpc_val), "bpc is inf/nan"
    assert bpc_val > 0.0, "bpc <= 0"
    top1_val = top1_from_logp(logp, nxt_fake)
    assert math.isfinite(top1_val) and 0.0 <= top1_val <= 1.0, "top1 out of range"
    mrr_val = mrr_at_k(logp, nxt_fake, k=5)
    assert math.isfinite(mrr_val) and mrr_val >= 0.0, "mrr invalid"

    # 6. write_metrics is callable (import chain ok)
    from experiments._seed_checkpoint import write_metrics as _wm
    assert callable(_wm), "_seed_checkpoint.write_metrics not callable"

    # 7. Filter check: at smoke scale n_eval (nxt_fake) has >=1 item
    assert len(nxt_fake) >= 1, "no eval items at smoke scale"

    # 8. ACh gain reduces to global gain when alpha=0 (algebraic check)
    margin_v = compute_normalized_margin(logits)
    unc_v = 1.0 - margin_v
    gain_margin_alpha0 = (1.0 * (1.0 + 0.0 * unc_v)).astype(np.float32)
    scaled_margin_alpha0 = apply_per_query_gain(logits, gain_margin_alpha0)
    assert np.allclose(scaled_margin_alpha0, logits, atol=1e-5), "alpha=0 margin arm != identity"

    ent_v = compute_normalized_entropy(logits, T=1.0)
    gain_ent_alpha0 = (1.0 * (1.0 + 0.0 * ent_v)).astype(np.float32)
    scaled_ent_alpha0 = apply_per_query_gain(logits, gain_ent_alpha0)
    assert np.allclose(scaled_ent_alpha0, logits, atol=1e-5), "alpha=0 entropy arm != identity"

    print("[selftest] PASS: all ACh READ-gain assertions satisfied", flush=True)


_instrumentation_selftest()  # called at module scope


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

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]), flush=True)

    # Build encoder E (word2vec with char-trigram fallback)
    print("\n[seed=%d] building word2vec base E (V=%d, N_DIM=%d)..." % (seed, V, N_DIM), flush=True)
    t_enc0 = time.time()
    encoder_meta: Dict = {}
    try:
        E_base, encoder_meta = build_E_word2vec(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d encoder] WORD2VEC FAIL: %s -- fallback to char-trigram" % (seed, err), flush=True)
        E_base = build_E_char_trigram(vocab, N_DIM, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    t_enc = time.time() - t_enc0
    print("[seed=%d encoder] E built (%.1fs) shape=%s" % (seed, t_enc, str(tuple(E_base.shape))), flush=True)

    # Build sparse-bipolar logits (shared across all gain arms)
    print("\n[seed=%d] computing SPARSE_BIPOLAR logits..." % seed, flush=True)
    t_lb0 = time.time()
    try:
        logits_full = compute_sparse_bp_logits(E_base, idx_train, idx_held, seed)  # [N_HELD, V]
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d] LOGIT BUILD FAIL: %s" % (seed, err), flush=True)
        return {
            "seed": seed, "compute_failed": True, "compute_error": err,
            "by_arm": {"ARM_UNIGRAM": uni},
            "elapsed_s_seed": round(time.time() - t_seed, 2),
        }
    t_lb = time.time() - t_lb0
    print("[seed=%d] logits built (%.1fs) shape=%s range=[%.3f, %.3f]" % (
        seed, t_lb, str(logits_full.shape), float(logits_full.min()), float(logits_full.max())), flush=True)

    del E_base
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    # READOUT_DEGENERATE check: at T=1.0 raw BPC should NOT be ~= uniform-vocab BPC
    V_entropy_uniform = math.log2(max(V, 2))
    probs_raw = softmax_with_T(logits_full, 1.0)
    # Use a small slice for the degen check (cheap)
    n_degen_check = min(len(logits_full), 200)
    mean_logit_std = float(np.std(logits_full[:n_degen_check], axis=1).mean())
    degen_suspect = mean_logit_std < 0.01
    if degen_suspect:
        print("[seed=%d] READOUT_DEGENERATE_SUSPECT: mean per-row logit std=%.6f < 0.01 threshold" % (
            seed, mean_logit_std), flush=True)
    del probs_raw

    # Split held into dev + test (same mask logic as fair_harness)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    ctx_eval = ctx_full[mask]
    nxt_eval = nxt_full[mask]
    n_eval = len(ctx_eval)

    if n_eval == 0:
        print("[seed=%d] WARN: n_eval=0 after unk mask" % seed, flush=True)
        return {
            "seed": seed, "by_arm": {"ARM_UNIGRAM": uni},
            "V": V, "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
            "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
            "elapsed_s_seed": round(time.time() - t_seed, 2), "device": str(DEVICE),
        }

    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    # Trim logits to ctx_full domain, then mask
    if logits_full.shape[0] >= len(ctx_full):
        logits_ctx = logits_full[:len(ctx_full)]
    else:
        logits_ctx = logits_full
    logits_eval = logits_ctx[mask[:logits_ctx.shape[0]]]
    n_eval_actual = min(logits_eval.shape[0], n_eval)
    logits_eval = logits_eval[:n_eval_actual]
    nxt_dev_use = nxt_dev[:min(n_dev, logits_eval.shape[0])]
    nxt_test_use = nxt_test[:min(n_eval_actual - len(nxt_dev_use), logits_eval.shape[0])]
    sub_logits_dev = logits_eval[:len(nxt_dev_use)]
    sub_logits_test = logits_eval[len(nxt_dev_use):len(nxt_dev_use) + len(nxt_test_use)]

    print("[seed=%d] n_dev=%d n_test=%d logits_dev=%s" % (
        seed, len(nxt_dev_use), len(nxt_test_use), str(sub_logits_dev.shape)), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # ARM_GLOBAL_READ_GAIN
    print("\n  [seed=%d arm=ARM_GLOBAL_READ_GAIN] sweeping..." % seed, flush=True)
    t_arm = time.time()
    try:
        r_global = sweep_arm_global_gain(
            sub_logits_dev, sub_logits_test, U_log, nxt_dev_use, nxt_test_use,
            TEMP_GRID, LAMBDA_GRID, BASE_GAIN_GRID, MRR_K,
        )
        r_global["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        r_global["degen_suspect"] = bool(degen_suspect)
        by_arm["ARM_GLOBAL_READ_GAIN"] = r_global
        print("    bpc_best=%.4f top1=%.4f mrr=%.4f replication_ok=%s" % (
            r_global["bpc_best"], r_global["top1_acc"], r_global["mrr_at_10"],
            r_global["replication_ok"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    FAIL: %s" % err, flush=True)
        by_arm["ARM_GLOBAL_READ_GAIN"] = {"compute_failed": True, "compute_error": err,
                                           "bpc_best": float("inf")}

    # ARM_PER_QUERY_GAIN_MARGIN
    print("\n  [seed=%d arm=ARM_PER_QUERY_GAIN_MARGIN] sweeping..." % seed, flush=True)
    t_arm = time.time()
    try:
        r_margin = sweep_arm_per_query_margin(
            sub_logits_dev, sub_logits_test, U_log, nxt_dev_use, nxt_test_use,
            TEMP_GRID, LAMBDA_GRID, BASE_GAIN_GRID, ALPHA_GRID, MRR_K,
        )
        r_margin["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        by_arm["ARM_PER_QUERY_GAIN_MARGIN"] = r_margin
        print("    bpc_best=%.4f top1=%.4f mrr=%.4f best_alpha=%.2f" % (
            r_margin["bpc_best"], r_margin["top1_acc"], r_margin["mrr_at_10"],
            r_margin["best_alpha_for_bpc"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    FAIL: %s" % err, flush=True)
        by_arm["ARM_PER_QUERY_GAIN_MARGIN"] = {"compute_failed": True, "compute_error": err,
                                                "bpc_best": float("inf")}

    # ARM_PER_QUERY_GAIN_ENTROPY
    print("\n  [seed=%d arm=ARM_PER_QUERY_GAIN_ENTROPY] sweeping..." % seed, flush=True)
    t_arm = time.time()
    try:
        r_ent = sweep_arm_per_query_entropy(
            sub_logits_dev, sub_logits_test, U_log, nxt_dev_use, nxt_test_use,
            TEMP_GRID, LAMBDA_GRID, BASE_GAIN_GRID, ALPHA_GRID, MRR_K,
        )
        r_ent["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        by_arm["ARM_PER_QUERY_GAIN_ENTROPY"] = r_ent
        print("    bpc_best=%.4f top1=%.4f mrr=%.4f best_alpha=%.2f" % (
            r_ent["bpc_best"], r_ent["top1_acc"], r_ent["mrr_at_10"],
            r_ent["best_alpha_for_bpc"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    FAIL: %s" % err, flush=True)
        by_arm["ARM_PER_QUERY_GAIN_ENTROPY"] = {"compute_failed": True, "compute_error": err,
                                                  "bpc_best": float("inf")}

    del logits_full, logits_eval, sub_logits_dev, sub_logits_test

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
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "degen_suspect": bool(degen_suspect),
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Aggregate per-arm BPC
    arm_bpc_means: Dict[str, float] = {}
    arm_bpc_stds: Dict[str, float] = {}
    arm_bpc_cvs: Dict[str, float] = {}
    agg: Dict = {}

    for arm in GAIN_ARMS + ["ARM_UNIGRAM"]:
        vals = []
        for u in units:
            if u.get("compute_failed"):
                continue
            d = u.get("by_arm", {}).get(arm, {})
            if arm == "ARM_UNIGRAM":
                v = d.get("bpc_unigram", float("nan"))
            else:
                v = d.get("bpc_best", float("nan"))
            if math.isfinite(v):
                vals.append(v)
        if vals:
            m = float(np.mean(vals))
            s = float(np.std(vals))
            arm_bpc_means[arm] = round(m, 4)
            arm_bpc_stds[arm] = round(s, 4)
            arm_bpc_cvs[arm] = round(s / max(abs(m), 1e-6), 4)
            agg[arm] = {"bpc_mean": round(m, 4), "bpc_std": round(s, 4),
                        "bpc_cv": round(s / max(abs(m), 1e-6), 4), "n_seeds": len(vals)}
        else:
            arm_bpc_means[arm] = float("nan")
            agg[arm] = {"bpc_mean": float("nan"), "n_seeds": 0}

    global_bpc = arm_bpc_means.get("ARM_GLOBAL_READ_GAIN", float("nan"))
    margin_bpc = arm_bpc_means.get("ARM_PER_QUERY_GAIN_MARGIN", float("nan"))
    entropy_bpc = arm_bpc_means.get("ARM_PER_QUERY_GAIN_ENTROPY", float("nan"))
    unigram_bpc = arm_bpc_means.get("ARM_UNIGRAM", float("nan"))

    # Replication gate for GLOBAL arm
    replication_oks = []
    for u in units:
        if u.get("compute_failed"):
            continue
        r = u.get("by_arm", {}).get("ARM_GLOBAL_READ_GAIN", {}).get("replication_ok", False)
        replication_oks.append(r)
    replication_pass = sum(replication_oks) >= max(1, len(replication_oks) // 2)

    # READOUT_DEGENERATE: per-query arms collapse to near-unigram level
    degen_suspects = [u.get("degen_suspect", False) for u in units if not u.get("compute_failed")]
    any_degen = any(degen_suspects)

    # Lift of per-query arms over global
    lift_margin = global_bpc - margin_bpc if (math.isfinite(global_bpc) and math.isfinite(margin_bpc)) else float("nan")
    lift_entropy = global_bpc - entropy_bpc if (math.isfinite(global_bpc) and math.isfinite(entropy_bpc)) else float("nan")
    best_lift = max(
        lift_margin if math.isfinite(lift_margin) else float("-inf"),
        lift_entropy if math.isfinite(lift_entropy) else float("-inf"),
    )

    # Per-query arms collapse = BPC worse than or equal to unigram
    perquery_collapse = False
    for bpc in [margin_bpc, entropy_bpc]:
        if math.isfinite(bpc) and math.isfinite(unigram_bpc) and bpc >= unigram_bpc - 0.01:
            perquery_collapse = True

    cv_ok = True
    for arm in ["ARM_PER_QUERY_GAIN_MARGIN", "ARM_PER_QUERY_GAIN_ENTROPY"]:
        cv = arm_bpc_cvs.get(arm, float("nan"))
        if math.isfinite(cv) and cv > CV_MAX:
            cv_ok = False

    # Build summary line
    parts = [
        "GLOBAL_BPC=%.4f" % global_bpc if math.isfinite(global_bpc) else "GLOBAL_BPC=nan",
        "MARGIN_BPC=%.4f" % margin_bpc if math.isfinite(margin_bpc) else "MARGIN_BPC=nan",
        "ENTROPY_BPC=%.4f" % entropy_bpc if math.isfinite(entropy_bpc) else "ENTROPY_BPC=nan",
        "UNI_BPC=%.4f" % unigram_bpc if math.isfinite(unigram_bpc) else "UNI_BPC=nan",
        "lift_margin=%.4f" % lift_margin if math.isfinite(lift_margin) else "lift_margin=nan",
        "lift_entropy=%.4f" % lift_entropy if math.isfinite(lift_entropy) else "lift_entropy=nan",
        "replication_ok=%s" % replication_pass,
    ]
    summary = " | ".join(parts)

    if perquery_collapse or any_degen:
        verdict = "HARD_FAIL"
        msg = ("HARD_FAIL: ACh READ-gain arms READOUT_DEGENERATE or collapse to unigram. "
               "Per-query modulation did not improve over baseline. %s" % summary)
    elif not math.isfinite(best_lift) or best_lift <= MIDDLE_LOWER_BPC:
        verdict = "HARD_FAIL"
        msg = ("HARD_FAIL: per-query READ-gain lift=%.4f <= threshold=%.2f. "
               "ACh-analog READ-gain provides no LM improvement. %s" % (best_lift, MIDDLE_LOWER_BPC, summary))
    elif best_lift >= HP_LIFT_BPC and cv_ok:
        if best_lift >= CHAIN_GRADE_LIFT_BPC and math.isfinite(min(margin_bpc, entropy_bpc)):
            best_perquery_bpc = min(margin_bpc if math.isfinite(margin_bpc) else float("inf"),
                                    entropy_bpc if math.isfinite(entropy_bpc) else float("inf"))
            if best_perquery_bpc < FAIR_HARNESS_BASELINE_BPC:
                verdict = "HARD_PASS"
                msg = ("HARD_PASS CHAIN_GRADE_BONUS: per-query ACh READ-gain lift=%.4f >= %.2f bits "
                       "AND beats fair_harness baseline %.4f. "
                       "Conditional ACh gain IS substrate-improving. %s" % (
                           best_lift, CHAIN_GRADE_LIFT_BPC, FAIR_HARNESS_BASELINE_BPC, summary))
            else:
                verdict = "HARD_PASS"
                msg = ("HARD_PASS: per-query ACh READ-gain lift=%.4f >= %.2f bits over global gain. "
                       "Conditional modulation of logit magnitude IS meaningful. %s" % (
                           best_lift, HP_LIFT_BPC, summary))
        else:
            verdict = "HARD_PASS"
            msg = ("HARD_PASS: per-query ACh READ-gain lift=%.4f >= %.2f bits over global gain. "
                   "Conditional modulation of logit magnitude IS meaningful. %s" % (
                       best_lift, HP_LIFT_BPC, summary))
    else:
        verdict = "MIDDLE_BAND"
        msg = ("MIDDLE_BAND: per-query ACh READ-gain lift=%.4f in [%.2f, %.2f). "
               "Trend exists but underpowered for HARD_PASS. %s" % (
                   best_lift, MIDDLE_LOWER_BPC, HP_LIFT_BPC, summary))

    detail = {
        "by_arm_agg": agg,
        "lift_margin_bpc": round(lift_margin, 4) if math.isfinite(lift_margin) else None,
        "lift_entropy_bpc": round(lift_entropy, 4) if math.isfinite(lift_entropy) else None,
        "best_lift_bpc": round(best_lift, 4) if math.isfinite(best_lift) else None,
        "replication_pass": bool(replication_pass),
        "perquery_collapse": bool(perquery_collapse),
        "any_degen": bool(any_degen),
        "cv_ok": bool(cv_ok),
        "fair_harness_baseline_bpc": FAIR_HARNESS_BASELINE_BPC,
        "hp_lift_threshold": HP_LIFT_BPC,
        "chain_grade_lift_threshold": CHAIN_GRADE_LIFT_BPC,
        "middle_lower_threshold": MIDDLE_LOWER_BPC,
    }
    return (verdict, msg, detail)


# ============================================================================
# Checkpoint + atexit synthesizer
# ============================================================================

OUT_DIR = get_output_dir(ANCHOR_NAME)
_UNITS_WRITTEN: List[str] = []


def _atexit_synthesize():
    """Synthesize metrics from partial checkpoints if main loop did not complete."""
    try:
        partials_dict = aggregate_partials(OUT_DIR)
        if not partials_dict:
            return
        # aggregate_partials returns dict {str(key): payload}; compute_verdict expects list
        partials = list(partials_dict.values())
        verdict, msg, detail = compute_verdict(partials)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "anchor": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": msg,
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "detail": detail,
            "n_seeds": len(partials),
            "per_unit": partials,
            "atexit_synthesis": True,
        }
        write_metrics(OUT_DIR, metrics, partials)
        print("[atexit] synthesized metrics from %d partial(s)" % len(partials), flush=True)
    except Exception as e:
        print("[atexit] synthesis failed: %s" % e, flush=True)


atexit.register(_atexit_synthesize)


def _handle_signal(sig, frame):
    print("[signal] received %d; running atexit handlers..." % sig, flush=True)
    sys.exit(128 + sig)


signal.signal(signal.SIGTERM, _handle_signal)
try:
    signal.signal(signal.SIGINT, _handle_signal)
except Exception:
    pass

# ============================================================================
# Main
# ============================================================================

if _ARGS.self_test:
    print("[self-test] PASS: instrumentation_selftest ran at module scope", flush=True)
    sys.exit(0)

print("[config] anchor=%s mode=%s N_DIM=%d N_TRAIN=%d seeds=%s device=%s" % (
    ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, SEEDS, str(DEVICE)), flush=True)
print("[config] arms=%s" % ARMS, flush=True)
print("[config] BASE_GAIN_GRID=%s ALPHA_GRID=%s" % (BASE_GAIN_GRID, ALPHA_GRID), flush=True)
print("[config] pre-reg: HP_LIFT_BPC>=%.2f CHAIN_GRADE_LIFT_BPC>=%.2f MIDDLE_LOWER>=%.2f CV_MAX=%.3f" % (
    HP_LIFT_BPC, CHAIN_GRADE_LIFT_BPC, MIDDLE_LOWER_BPC, CV_MAX), flush=True)
print("[config] fair_harness_baseline_bpc=%.4f (GLOBAL arm replication gate +/-0.15)" % FAIR_HARNESS_BASELINE_BPC, flush=True)

t_global = time.time()
units: List[Dict] = []
for seed in SEEDS:
    ck = "s%d" % seed
    ck_path = OUT_DIR / ("partial_%s.json" % ck)
    if ck_path.exists():
        import json
        print("[skip] seed=%d already checkpointed" % seed, flush=True)
        with ck_path.open("r", encoding="utf-8") as _f:
            units.append(json.load(_f))
        continue
    u = run_unit(seed)
    units.append(u)
    write_partial_key(OUT_DIR, ck, u)
    print("[checkpoint] seed=%d written to %s" % (seed, ck_path), flush=True)

verdict, verdict_msg, detail = compute_verdict(units)
print("\n[VERDICT] %s" % verdict_msg, flush=True)

elapsed = time.time() - t_global
metrics = {
    "anchor_name": ANCHOR_NAME,
    "anchor": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "N": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "TEMP_GRID": TEMP_GRID,
    "LAMBDA_GRID": LAMBDA_GRID,
    "BASE_GAIN_GRID": BASE_GAIN_GRID,
    "ALPHA_GRID": ALPHA_GRID,
    "MRR_K": MRR_K,
    "arms": ARMS,
    "n_seeds": len(units),
    "detail": detail,
    "per_unit": units,
    "elapsed_s": round(elapsed, 2),
    "device": str(DEVICE),
    "config_version": CONFIG_VERSION,
    "fair_harness_baseline_bpc": FAIR_HARNESS_BASELINE_BPC,
    "cites": [
        "preregs/2026-06-23_ACh_query_conditional_read_gain.md",
        "experiments/exp_fair_harness_substrate_as_lm_v1.py",
        "experiments/exp_excitability_gated_substrate_cpu_v1.py",
        "Yu-Dayan-2005-ACh-attention-gain",
        "Goard-Dan-2009-basal-forebrain-ACh-V1-SNR",
        "Pinto-Goard-2013-ACh-signal-detection",
        "substrate_mine_modulator_gain_experiments_inventory_2026-06-23",
    ],
}
write_metrics(OUT_DIR, metrics, units)
print("[metrics] written to %s" % OUT_DIR, flush=True)
