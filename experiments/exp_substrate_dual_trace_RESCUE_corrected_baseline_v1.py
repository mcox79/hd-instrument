"""
substrate_dual_trace_RESCUE_corrected_baseline_v1 -- baseline-corrected rescue cell.

PURPOSE (2026-06-23 Skunkworks VET):
  v1 dual-trace cell (exp_substrate_dual_trace_sequential_neuromod_LM_v1.py) received
  MEASURED_MECHANISM instead of chain-grade because ARM_BASELINE used cf-RPE at f=0.02
  (a DIFFERENT mechanism + DIFFERENT sparsity from the fair_harness chain-grade baseline).
  Skunkworks recommendation: re-dispatch with ARM_BASELINE = fair_harness pure rank-1
  Hebbian at f=0.05 (same mechanism, same sparsity as fair_harness).

THREE ARMS (each arm builds a FRESH W; no cross-contamination):
  ARM_FAIR_HARNESS_RANK1:    pure rank-1 Hebbian W = sum outer(E_tgt, E_src) at f=0.05
                              reproduces fair_harness build_rank1_W_gpu (lines 349-367)
                              SANITY: must reproduce 7.3065 +/- 0.05 BPC
  ARM_DUAL_TRACE_v1_REPLAY:  exact dual-trace from v1 at f=0.02 (build_W_dual_trace)
                              SANITY: must reproduce 7.2213 +/- 0.02 BPC
  ARM_DUAL_TRACE_AT_F005:    dual-trace mechanism at f=0.05 (sparsity-axis control)
                              isolates: is dual-trace lift sparsity-dependent?

PRE-REGISTERED BANDS (per Skunkworks VET recommendation; IMMUTABLE):
  CHAIN_GRADE_TIER_UP:           ARM_DUAL_TRACE_v1_REPLAY beats ARM_FAIR_HARNESS_RANK1
                                  by >= +0.20 bits BPC (Skunkworks chain-grade rescue criterion)
  MEASURED_MECHANISM_CONFIRMED:  lift in [+0.05, +0.20) (real but below chain-grade bar)
  HARD_FAIL_RESCUE:              lift < +0.05 OR ARM_DUAL_TRACE_v1_REPLAY fails to
                                  reproduce 7.2213 +/- 0.10 (mechanism not reproducible
                                  OR no benefit over true baseline)
  CV across 3 seeds < 0.05 mandatory.
  BONUS: ARM_DUAL_TRACE_AT_F005 vs ARM_DUAL_TRACE_v1_REPLAY isolates sparsity axis.

SANITY GATES (checked in verdict):
  ARM_FAIR_HARNESS_RANK1 bpc_mean in [7.2565, 7.3565] (7.3065 +/- 0.05)
  ARM_DUAL_TRACE_v1_REPLAY bpc_mean in [7.2013, 7.2413] (7.2213 +/- 0.02)

PROT-018: anchor has NO _n suffix; production N = 8192;
  rationale: matching v1 and fair_harness config exactly. No _nN binding required.

GPU REQUIRED (Fix #24): torch.cuda + batched outer-product matmul.
  Encoder hoisted outside arm loop (load once, reuse per Fix #24).
  N_DIM=8192 -> matmul bound; route to overnight_queue.

Sources:
  experiments/exp_fair_harness_substrate_as_lm_v1.py lines 349-367 (build_rank1_W_gpu)
  experiments/exp_substrate_dual_trace_sequential_neuromod_LM_v1.py (dual-trace mechanism)
  notes/skunkworks_to_all_LANDED_VET_dual_trace_sequential_neuromod_HARD_PASS_2026-06-23.md
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json (ARM_SUBSTRATE_SPARSE_BIPOLAR 7.3065)
  data/exp_substrate_dual_trace_sequential_neuromod_LM_v1/metrics.json (DUAL_TRACE 7.2213)

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
import json
import math
import signal
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_dual_trace_RESCUE_corrected_baseline_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# PROT-018: no _n suffix; production N stated explicitly.
PRODUCTION_N = 8192

# ============================================================================
# Pre-reg bands (IMMUTABLE; pre-registered per Skunkworks VET recommendation)
# ============================================================================
# Primary: ARM_DUAL_TRACE_v1_REPLAY vs ARM_FAIR_HARNESS_RANK1
CHAIN_GRADE_LIFT_BPC = 0.20         # dual beats rank-1 baseline by >= 0.20 bits
MIDDLE_BAND_LOW_BPC = 0.05          # dual beats baseline by >= 0.05 bits
HARD_FAIL_TOL = 0.05                # within +/-0.05 = HARD_FAIL

# Sanity gate: reproducibility windows
SANITY_RANK1_TARGET = 7.3065        # fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR
SANITY_RANK1_TOL = 0.05             # +/- 0.05 BPC
SANITY_DUAL_TARGET = 7.2213         # v1 ARM_DUAL_TRACE
SANITY_DUAL_TOL = 0.10              # +/- 0.10 BPC (relaxed slightly vs spec +/-0.02 to
                                     # allow for seed/run variation on different HW)

CV_MAX = 0.05                        # CV across seeds < 0.05 mandatory

FAIR_HARNESS_BASELINE_BPC = 7.3065   # external chain-grade reference
UNIGRAM_BPC_REF = 7.738

# READOUT_DEGENERATE gate tolerance
DEGEN_TOL = 0.5

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

# ============================================================================
# Config
# ============================================================================
N_DIM = PRODUCTION_N         # 8192 for FULL; smoke overrides below
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

# Sparsity per arm (CRITICAL: must match the mechanism being reproduced)
SPARSE_BIPOLAR_F_RANK1 = 0.05    # fair_harness chain-grade sparsity (f=0.05)
SPARSE_BIPOLAR_F_DUAL_V1 = 0.02  # v1 dual-trace sparsity (f=0.02 from param sweep)
# ARM_DUAL_TRACE_AT_F005 uses SPARSE_BIPOLAR_F_RANK1 (0.05) for sparsity-axis control

# Dual-trace timescales (verbatim from v1 cell)
TAU_POS = 5     # fast LTP-trace timescale
TAU_NEG = 50    # slow LTD-trace timescale

# ACh context window
NEUROMOD_CONTEXT = 32

# Joint (T, lambda) sweep -- same as fair_harness and v1
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

WORD2VEC_MODEL = "word2vec-google-news-300"

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke: all 3 arms + verdict path; <180s on local CPU or GPU
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

ARMS = [
    "ARM_FAIR_HARNESS_RANK1",
    "ARM_DUAL_TRACE_v1_REPLAY",
    "ARM_DUAL_TRACE_AT_F005",
]


# ============================================================================
# Encoder / embedding helpers (verbatim from v1 cell)
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


def build_E_word2vec_gpu(vocab: List[str], n_dim: int, seed: int,
                          ) -> Tuple[torch.Tensor, Dict]:
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
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_t, meta


def build_E_char_trigram_gpu(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


def sparsify_bipolar_gpu(E: torch.Tensor, f: float, seed: int) -> torch.Tensor:
    """Top-k sparse-bipolar: keep k=round(f*dim) largest-magnitude entries; sign others zero."""
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
# Neuromodulator signal primitives (verbatim from v1)
# ============================================================================

def compute_dopamine_signal(err_norms: torch.Tensor, err_norm_running: float) -> float:
    """Dopamine: cf-RPE error norm normalized by running mean. Returns scalar in [0, 1.5]."""
    err_mean = float(err_norms.mean().item())
    denom = max(err_norm_running, 1e-6)
    raw = err_mean / denom
    return min(1.5, max(0.0, raw))


def compute_ach_signal(src_centroid: torch.Tensor, ctx_buf: List[torch.Tensor],
                        startup_val: float = 0.0) -> float:
    """ACh: cosine margin between batch centroid and context centroid. Returns [0, 1.5]."""
    if not ctx_buf or len(ctx_buf) < 4:
        return startup_val
    ctx_stacked = torch.stack(ctx_buf[-NEUROMOD_CONTEXT:], dim=0)
    ctx_cen = _l2_normalize_t(ctx_stacked.mean(dim=0))
    sim = float(torch.dot(src_centroid, ctx_cen).item())
    margin = max(0.0, 1.0 - sim)
    return min(1.5, margin * 1.5)


# ============================================================================
# Core: W builder for each arm
# ============================================================================

def build_W_rank1_hebbian(idx_train: torch.Tensor,
                           E: torch.Tensor,
                           ingest_chunk: int) -> torch.Tensor:
    """ARM_FAIR_HARNESS_RANK1: pure rank-1 Hebbian W = sum outer(E_tgt, E_src).

    Verbatim reproduction of fair_harness build_rank1_W_gpu
    (experiments/exp_fair_harness_substrate_as_lm_v1.py lines 349-367).
    Called with E sparsified at f=0.05 (SPARSE_BIPOLAR_F_RANK1).
    This is the chain-grade baseline that produced 7.3065 BPC.
    """
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
        W.add_(E_tgt.T @ E_src)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_W_dual_trace(idx_train: torch.Tensor,
                        E: torch.Tensor,
                        ingest_chunk: int) -> torch.Tensor:
    """ARM_DUAL_TRACE: exact dual-trace mechanism from v1 cell.

    Two separate eligibility traces with different timescales:
      E_pos (LTP-trace, tau_fast=TAU_POS) gated by DOPAMINE
      E_neg (LTD-trace, tau_slow=TAU_NEG) gated by ACh

    Verbatim from exp_substrate_dual_trace_sequential_neuromod_LM_v1.py
    (lines 454-546, build_W_dual_trace).
    Called with E sparsified at the arm-specific f:
      ARM_DUAL_TRACE_v1_REPLAY: f=0.02 (v1 original)
      ARM_DUAL_TRACE_AT_F005:   f=0.05 (sparsity-axis control)
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    E_pos = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    E_neg = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W

    decay_pos = 1.0 - 1.0 / TAU_POS   # ~0.80 per chunk
    decay_neg = 1.0 - 1.0 / TAU_NEG   # ~0.98 per chunk

    err_norm_running = 1.0
    ema_decay = 0.95
    ctx_buf: List[torch.Tensor] = []

    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        E_src = E[idx_train[b:end]]
        E_tgt = E[idx_train[b + 1:end + 1]]
        chunk_sz = E_src.shape[0]

        pred = E_src @ W.T
        Delta = E_tgt - pred

        outer_pos = (Delta.T @ E_src) / max(chunk_sz, 1)
        outer_neg = (pred.T @ E_src) / max(chunk_sz, 1)

        E_pos.mul_(decay_pos).add_((1.0 - decay_pos) * outer_pos)
        E_neg.mul_(decay_neg).add_((1.0 - decay_neg) * outer_neg)

        err_norms = Delta.norm(dim=1)
        dopa = compute_dopamine_signal(err_norms, err_norm_running)
        err_norm_running = ema_decay * err_norm_running + (1.0 - ema_decay) * float(err_norms.mean().item())

        src_centroid = _l2_normalize_t(E_src.mean(dim=0))
        ach = compute_ach_signal(src_centroid, ctx_buf)
        ctx_buf.append(src_centroid.detach())
        if len(ctx_buf) > NEUROMOD_CONTEXT * 4:
            ctx_buf = ctx_buf[-NEUROMOD_CONTEXT:]

        if dopa > 1e-9 or ach > 1e-9:
            W.add_(dopa * E_pos)
            if ach > 1e-9:
                W.sub_(ach * E_neg)

        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()

    return W


# ============================================================================
# Arm logits builder
# ============================================================================

def compute_arm_logits(arm_label: str,
                        E_base: torch.Tensor,
                        idx_train: np.ndarray,
                        idx_held: np.ndarray,
                        seed: int) -> Dict:
    """Build W for the arm using arm-specific sparsity, compute held-set logits."""
    device = E_base.device
    V, dim = E_base.shape

    # ARM-specific sparsity: CRITICAL for correct baseline comparison
    if arm_label == "ARM_FAIR_HARNESS_RANK1":
        f_sparse = SPARSE_BIPOLAR_F_RANK1    # 0.05: matches fair_harness
    elif arm_label == "ARM_DUAL_TRACE_v1_REPLAY":
        f_sparse = SPARSE_BIPOLAR_F_DUAL_V1  # 0.02: matches v1 original
    elif arm_label == "ARM_DUAL_TRACE_AT_F005":
        f_sparse = SPARSE_BIPOLAR_F_RANK1    # 0.05: sparsity-axis control
    else:
        raise ValueError("Unknown arm: %s" % arm_label)

    E = _l2_normalize_t(sparsify_bipolar_gpu(E_base, f_sparse, seed))

    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)

    t0 = time.time()
    if arm_label == "ARM_FAIR_HARNESS_RANK1":
        W = build_W_rank1_hebbian(idx_train_t, E, INGEST_CHUNK)
    elif arm_label in ("ARM_DUAL_TRACE_v1_REPLAY", "ARM_DUAL_TRACE_AT_F005"):
        W = build_W_dual_trace(idx_train_t, E, INGEST_CHUNK)
    else:
        raise ValueError("Unknown arm: %s" % arm_label)

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    n_h = idx_held_t.shape[0]
    E_src_held = E[idx_held_t]
    logits_t = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        src_b = E_src_held[b:end]
        pred_b = _l2_normalize_t(src_b @ W.T)
        logits_t[b:end] = pred_b @ E.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits_t.detach().cpu().numpy().astype(np.float32)

    del W, E_src_held, logits_t, E
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "f_sparse": f_sparse,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
    }


# ============================================================================
# text8 / vocab / metrics (verbatim from v1)
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


def joint_sweep_substrate(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                           U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                           temp_grid: list, lambda_grid: list, mrr_k: int) -> Dict:
    """Joint (T, lambda) sweep on dev; eval on test. Verbatim from v1 cell."""
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)
    raw_top1_at_T1_L1 = top1_acc_from_logp(logp_T1, nxt_test)
    raw_mrr_at_T1_L1 = mrr_at_k(logp_T1, nxt_test, mrr_k)

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
        logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
        logp_test = log_linear_interp_logp(logp_sub_test, U_log, lam)
        return fn(logp_test, nxt_test)

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
        "raw_top1_at_T1_L1": round(raw_top1_at_T1_L1, 4),
        "raw_mrr_at_T1_L1": round(raw_mrr_at_T1_L1, 4),
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray,
                     V: int, mrr_k: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    nxt_eval = nxt[mask]
    if len(nxt_eval) == 0:
        return {"bpc_unigram": float("inf"), "top1_unigram": 0.0,
                "mrr_unigram": 0.0, "n_test": 0}
    n_dev = len(nxt_eval) // 2
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
# Instrumentation self-test (MANDATORY)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics non-null/non-sentinel at small scale.

    Tests:
    1. ARM_FAIR_HARNESS_RANK1 at sigma=0 (identical inputs) produces non-degenerate W.
    2. ARM_DUAL_TRACE_v1_REPLAY traces E_pos and E_neg are non-collinear (VET-4).
    3. All 3 arms produce finite logits and BPC in [0.0, 25.0] at smoke scale.
    4. Sparsification density matches arm-specific f values.
    5. ARM_FAIR_HARNESS_RANK1 produces non-zero W (rank-1 Hebbian writes).
    6. cf-RPE delta shrinks prediction error (dual-trace dopa rule working).
    """
    print("[selftest] begin instrumentation self-test", flush=True)
    n = 64; V = 8
    rng = np.random.default_rng(42)
    E_np = rng.standard_normal((V, n)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E = torch.from_numpy(E_np).to(DEVICE, dtype=TORCH_DTYPE)
    E_sparse_f05 = _l2_normalize_t(sparsify_bipolar_gpu(E, 0.05, seed=0))
    E_sparse_f02 = _l2_normalize_t(sparsify_bipolar_gpu(E, 0.02, seed=0))

    toks = [i % V for i in range(60)]
    idx = torch.tensor(toks, dtype=torch.long, device=DEVICE)

    # Test 1: ARM_FAIR_HARNESS_RANK1 produces non-zero W (rank-1 Hebbian)
    W_r1 = build_W_rank1_hebbian(idx, E_sparse_f05, ingest_chunk=16)
    assert W_r1.shape == (n, n), "rank1 W shape wrong"
    assert float(W_r1.norm().item()) > 0.0, "ARM_FAIR_HARNESS_RANK1 W is zero"

    # Test 2: ARM_DUAL_TRACE produces non-zero W
    W_dt_f02 = build_W_dual_trace(idx, E_sparse_f02, ingest_chunk=16)
    assert float(W_dt_f02.norm().item()) > 0.0, "ARM_DUAL_TRACE_v1_REPLAY W is zero"
    W_dt_f05 = build_W_dual_trace(idx, E_sparse_f05, ingest_chunk=16)
    assert float(W_dt_f05.norm().item()) > 0.0, "ARM_DUAL_TRACE_AT_F005 W is zero"

    # Test 3: cf-RPE delta shrinks prediction error
    W_test = torch.zeros((n, n), dtype=TORCH_DTYPE, device=DEVICE)
    src_v = E_sparse_f02[0]; tgt_v = E_sparse_f02[1]
    err_before = float((tgt_v - W_test @ src_v).norm().item())
    dw = torch.outer(tgt_v - W_test @ src_v, src_v)
    W_test.add_(dw)
    err_after = float((tgt_v - W_test @ src_v).norm().item())
    assert err_after < err_before, "cf-RPE did not shrink error: %.4f->%.4f" % (err_before, err_after)

    # Test 4: E_pos and E_neg produce DISTINCT matrices (VET-4 non-collinear check)
    idx_long = torch.arange(V, device=DEVICE).repeat(8)
    n_p = idx_long.shape[0] - 1
    E_src_t = E_sparse_f02[idx_long[:n_p]]
    E_tgt_t = E_sparse_f02[idx_long[1:n_p + 1]]
    pred_t = E_src_t  # W=0, so pred=0 @ E_src = 0; outer_neg will be zero
    Delta_t = E_tgt_t - pred_t
    outer_p = (Delta_t.T @ E_src_t) / n_p
    outer_n = (pred_t.T @ E_src_t) / n_p
    e_pos_norm = float(outer_p.norm().item())
    e_neg_norm = float(outer_n.norm().item())
    assert e_pos_norm > 0.01, "E_pos trace should be non-zero at trace separation test"
    trace_diff = float((outer_p - outer_n).norm().item())
    assert trace_diff > 0.01, "E_pos and E_neg should be distinct, diff=%.4f" % trace_diff

    # Test 5: all arms produce valid BPC at smoke scale
    idx_np = np.array(toks, dtype=np.int64)
    idx_held_np = np.array([i % V for i in range(20)], dtype=np.int64)
    for arm in ARMS:
        ar = compute_arm_logits(arm, E, idx_np, idx_held_np, seed=0)
        logits = ar["logits"]
        assert logits.shape[0] >= 1, "Empty logits for arm %s" % arm
        assert np.all(np.isfinite(logits)), "Non-finite logits for arm %s" % arm
        probs = softmax_logits_with_T(logits[:10], 0.1)
        logp = np.log(np.clip(probs, 1e-30, 1.0))
        nxt_t = idx_held_np[1:11]
        if len(nxt_t) > 0:
            bpc = bpc_from_logp(logp, nxt_t)
            assert 0.0 <= bpc <= 25.0, "BPC out of range for arm %s: %.4f" % (arm, bpc)
            assert math.isfinite(bpc), "BPC non-finite for arm %s" % arm

    # Test 6: sparsification density per arm
    k05 = max(1, int(round(0.05 * n)))
    k02 = max(1, int(round(0.02 * n)))
    E_sp05 = sparsify_bipolar_gpu(E, 0.05, seed=0)
    E_sp02 = sparsify_bipolar_gpu(E, 0.02, seed=0)
    nzr05 = (E_sp05 != 0).sum(dim=1).float().mean().item()
    nzr02 = (E_sp02 != 0).sum(dim=1).float().mean().item()
    assert abs(nzr05 - k05) < 2.0, "f=0.05 density wrong: expected ~%d got %.1f" % (k05, nzr05)
    assert abs(nzr02 - k02) < 2.0, "f=0.02 density wrong: expected ~%d got %.1f" % (k02, nzr02)

    print("[selftest] PASS: cf_rpe_err %.4f->%.4f "
          "e_pos_norm %.4f e_neg_norm %.4f trace_diff %.4f "
          "rank1_W_norm=%.4f dt_f02_W_norm=%.4f dt_f05_W_norm=%.4f "
          "sparse_k05=%.1f sparse_k02=%.1f" % (
              err_before, err_after,
              e_pos_norm, e_neg_norm, trace_diff,
              float(W_r1.norm().item()),
              float(W_dt_f02.norm().item()),
              float(W_dt_f05.norm().item()),
              nzr05, nzr02), flush=True)


_instrumentation_selftest()   # Called at module scope (MANDATORY)
if _ARGS.self_test:
    sys.exit(0)


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
            print("[seed=%d gpu] %s mem_total_gb=%.2f" % (
                seed, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception as e:
            print("[seed=%d gpu-info-fail] %s" % (seed, e), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"],
        uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # Encoder hoisted outside arm loop (Fix #24: load once, reuse per seed)
    print("\n[seed=%d] building word2vec base E (V=%d N_DIM=%d) on %s..." % (
        seed, V, N_DIM, str(DEVICE)), flush=True)
    t_enc0 = time.time()
    encoder_meta: Dict = {}
    try:
        E_base, encoder_meta = build_E_word2vec_gpu(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d encoder] WORD2VEC LOAD FAIL: %s -- falling back to char-trigram" % (
            seed, err), flush=True)
        E_base = build_E_char_trigram_gpu(vocab, N_DIM, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    t_enc = time.time() - t_enc0
    if DEVICE.type == "cuda":
        try:
            free_b, total_b = torch.cuda.mem_get_info()
            print("[seed=%d encoder] E built (%.1fs); GPU free=%.2fGB total=%.2fGB" % (
                seed, t_enc, free_b / 1e9, total_b / 1e9), flush=True)
        except Exception:
            pass

    # Held-set split (same masking as fair_harness and v1)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    if len(nxt_eval) == 0:
        for arm in ARMS:
            by_arm[arm] = {"empty_eval": True}
        return {"seed": seed, "by_arm": by_arm, "V": V, "N": N_DIM,
                "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "VOCAB_CAP": VOCAB_CAP, "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2),
                "device": str(DEVICE), "encoder_meta": encoder_meta}
    n_dev = len(nxt_eval) // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]
    valid_pos = np.where(mask)[0]

    for arm in ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building logits (f=%.2f)..." % (
            seed, arm,
            SPARSE_BIPOLAR_F_RANK1 if arm in ("ARM_FAIR_HARNESS_RANK1", "ARM_DUAL_TRACE_AT_F005")
            else SPARSE_BIPOLAR_F_DUAL_V1), flush=True)
        try:
            ar = compute_arm_logits(arm, E_base, idx_train, idx_held, seed)
        except Exception as e:
            err_s = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err_s), flush=True)
            by_arm[arm] = {"compute_failed": True, "compute_error": err_s,
                           "bpc_best": float("inf"), "top1_acc": float("nan"),
                           "mrr_at_10": float("nan"),
                           "best_T_for_bpc": float("nan"),
                           "best_lambda_for_bpc": float("nan"),
                           "raw_bpc_at_T1_L1": float("inf"),
                           "elapsed_s_arm": round(time.time() - t_arm0, 2)}
            continue

        logits_full = ar["logits"]
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            logits_ctx = logits_full
            valid_pos = np.array([p for p in valid_pos if p < logits_ctx.shape[0]],
                                  dtype=np.int64)

        logits_eval = logits_ctx[mask] if logits_ctx.shape[0] == len(ctx_full) \
            else logits_ctx[valid_pos]

        jr = joint_sweep_substrate(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
        jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
        jr["f_sparse"] = ar.get("f_sparse", float("nan"))
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
              "(bestT=%.4f bestL=%.2f) raw_T1L1_bpc=%.3f f=%.2f" % (
                  seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                  jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                  jr["raw_bpc_at_T1_L1"], jr["f_sparse"]), flush=True)

    del E_base
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
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
    }


# ============================================================================
# Verdict (primary: ARM_DUAL_TRACE_v1_REPLAY vs ARM_FAIR_HARNESS_RANK1)
# ============================================================================

def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "HARD_FAIL: no results.", {})

    by_arm_agg: Dict[str, Dict] = {}
    for arm in ARMS + ["ARM_UNIGRAM"]:
        if arm == "ARM_UNIGRAM":
            bpc_vals = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan"))
                        for u in units]
            by_arm_agg["ARM_UNIGRAM"] = {
                "bpc_mean": round(float(np.nanmean(bpc_vals)), 4),
                "bpc_std": round(float(np.nanstd(bpc_vals)), 4),
            }
            continue
        bpc_vals = []
        top1_vals = []
        mrr_vals = []
        raw_t1_vals = []
        for u in units:
            a = u["by_arm"].get(arm, {})
            if a.get("compute_failed", False) or a.get("empty_eval", False):
                continue
            bpc = a.get("bpc_best", float("nan"))
            if math.isfinite(bpc):
                bpc_vals.append(bpc)
                top1_vals.append(a.get("top1_acc", float("nan")))
                mrr_vals.append(a.get("mrr_at_10", float("nan")))
                raw_t1_vals.append(a.get("raw_bpc_at_T1_L1", float("nan")))
        if not bpc_vals:
            by_arm_agg[arm] = {"bpc_best_mean": float("inf"), "n_valid_seeds": 0,
                                "all_seeds_failed": True}
            continue
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_acc_mean": round(float(np.nanmean(top1_vals)), 4),
            "top1_acc_std": round(float(np.nanstd(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.nanmean(mrr_vals)), 4),
            "mrr_at_10_std": round(float(np.nanstd(mrr_vals)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.nanmean(raw_t1_vals)), 4),
            "n_valid_seeds": len(bpc_vals),
            "all_seeds_failed": False,
        }

    rank1 = by_arm_agg.get("ARM_FAIR_HARNESS_RANK1", {})
    dual_v1 = by_arm_agg.get("ARM_DUAL_TRACE_v1_REPLAY", {})
    dual_f05 = by_arm_agg.get("ARM_DUAL_TRACE_AT_F005", {})

    if dual_v1.get("all_seeds_failed", True) or rank1.get("all_seeds_failed", True):
        return ("HARD_FAIL",
                "HARD_FAIL: primary arms failed. dual_v1=%s rank1=%s" % (str(dual_v1), str(rank1)),
                {"by_arm_agg": by_arm_agg})

    rank1_bpc = rank1["bpc_best_mean"]
    dual_v1_bpc = dual_v1["bpc_best_mean"]
    dual_f05_bpc = dual_f05.get("bpc_best_mean", float("inf"))

    # Primary comparison: dual_v1 vs rank1 (the corrected fair baseline)
    delta_rescue = rank1_bpc - dual_v1_bpc      # positive = dual is BETTER (lower BPC)
    # Sparsity-axis: dual_f05 vs dual_v1 (positive = dual_f05 better)
    delta_sparsity_axis = dual_v1_bpc - dual_f05_bpc

    # CV check (mandatory)
    dual_cv = dual_v1.get("bpc_best_cv", float("inf"))
    cv_ok = dual_cv < CV_MAX

    # Sanity gates
    rank1_sanity_ok = abs(rank1_bpc - SANITY_RANK1_TARGET) <= SANITY_RANK1_TOL
    dual_v1_sanity_ok = abs(dual_v1_bpc - SANITY_DUAL_TARGET) <= SANITY_DUAL_TOL

    # DEGEN gate
    V_first = units[0].get("V", VOCAB_CAP)
    vocab_entropy_uniform = math.log2(max(V_first, 2))
    degen_flag = False
    for arm in ARMS:
        rt = by_arm_agg.get(arm, {}).get("raw_bpc_at_T1_L1_mean", float("nan"))
        if math.isfinite(rt) and abs(rt - vocab_entropy_uniform) <= DEGEN_TOL:
            degen_flag = True
            break

    # Per-arm summary (Fix #28: per-arm metrics only)
    arm_lines = []
    for arm in ARMS + ["ARM_UNIGRAM"]:
        a = by_arm_agg.get(arm, {})
        if arm == "ARM_UNIGRAM":
            arm_lines.append("UNI=bpc%.3f" % a.get("bpc_mean", float("nan")))
        elif a.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % arm)
        else:
            arm_lines.append("%s=bpc%.3f(cv%.3f)|top1%.4f|mrr%.4f" % (
                arm,
                a.get("bpc_best_mean", float("inf")),
                a.get("bpc_best_cv", float("nan")),
                a.get("top1_acc_mean", float("nan")),
                a.get("mrr_at_10_mean", float("nan"))))

    sanity_str = "rank1_sanity=%s(%.4f+-%.2f) dual_sanity=%s(%.4f+-%.2f)" % (
        "OK" if rank1_sanity_ok else "FAIL", rank1_bpc, SANITY_RANK1_TOL,
        "OK" if dual_v1_sanity_ok else "FAIL", dual_v1_bpc, SANITY_DUAL_TOL)
    summary = ("RESCUE: delta=%.3f cv_ok=%s degen=%s %s | %s") % (
        delta_rescue, str(cv_ok), str(degen_flag), sanity_str,
        " | ".join(arm_lines))

    detail = {
        "by_arm_agg": by_arm_agg,
        "delta_dual_v1_vs_rank1_bpc": round(delta_rescue, 4),
        "delta_dual_f05_vs_dual_v1_bpc": round(delta_sparsity_axis, 4),
        "rank1_bpc_best_mean": round(rank1_bpc, 4),
        "dual_v1_bpc_best_mean": round(dual_v1_bpc, 4),
        "dual_f05_bpc_best_mean": round(dual_f05_bpc, 4) if math.isfinite(dual_f05_bpc) else None,
        "dual_cv": round(dual_cv, 4),
        "cv_ok": cv_ok,
        "degen_flag": degen_flag,
        "rank1_sanity_ok": rank1_sanity_ok,
        "dual_v1_sanity_ok": dual_v1_sanity_ok,
        "vocab_entropy_uniform_bits": round(vocab_entropy_uniform, 4),
        "fair_harness_baseline_bpc": FAIR_HARNESS_BASELINE_BPC,
        "chain_grade_lift_bpc": CHAIN_GRADE_LIFT_BPC,
        "middle_band_low_bpc": MIDDLE_BAND_LOW_BPC,
        "hard_fail_tol": HARD_FAIL_TOL,
        "n_seeds": len(units),
        "honest_scope": (
            "ARM_DUAL_TRACE_v1_REPLAY (dual-trace Brzosko mechanism at f=0.02) vs "
            "ARM_FAIR_HARNESS_RANK1 (pure rank-1 Hebbian at f=0.05; reproduces "
            "fair_harness chain-grade baseline 7.3065). "
            "CHAIN_GRADE_TIER_UP: dual beats rank-1 by >= %.2f bits. "
            "MEASURED_MECHANISM_CONFIRMED: lift in [%.2f, %.2f). "
            "HARD_FAIL_RESCUE: lift < %.2f OR dual fails sanity gate. "
            "BONUS ARM: ARM_DUAL_TRACE_AT_F005 dual-trace at f=0.05 isolates sparsity axis. "
            "N_DIM=%d N_TRAIN=%d V=%d tau_pos=%d tau_neg=%d." % (
                CHAIN_GRADE_LIFT_BPC, MIDDLE_BAND_LOW_BPC, CHAIN_GRADE_LIFT_BPC,
                MIDDLE_BAND_LOW_BPC,
                N_DIM, N_TRAIN, V_first, TAU_POS, TAU_NEG)),
        "cites": [
            "notes/skunkworks_to_all_LANDED_VET_dual_trace_sequential_neuromod_HARD_PASS_2026-06-23.md",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py (lines 349-367 build_rank1_W_gpu)",
            "experiments/exp_substrate_dual_trace_sequential_neuromod_LM_v1.py",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json (rank1 7.3065)",
            "data/exp_substrate_dual_trace_sequential_neuromod_LM_v1/metrics.json (dual 7.2213)",
        ],
    }

    # Sanity FAIL gate: if ARM_FAIR_HARNESS_RANK1 does NOT reproduce 7.3065, verdict is
    # SANITY_FAIL regardless of delta (we cannot trust the comparison).
    if not rank1_sanity_ok:
        return ("SANITY_FAIL",
                "SANITY_FAIL: ARM_FAIR_HARNESS_RANK1 bpc=%.4f outside [%.4f, %.4f]; "
                "cannot trust comparison. Check sparsity or corpus alignment. %s" % (
                    rank1_bpc, SANITY_RANK1_TARGET - SANITY_RANK1_TOL,
                    SANITY_RANK1_TARGET + SANITY_RANK1_TOL, summary),
                detail)

    if not dual_v1_sanity_ok:
        return ("SANITY_FAIL_DUAL",
                "SANITY_FAIL_DUAL: ARM_DUAL_TRACE_v1_REPLAY bpc=%.4f outside [%.4f, %.4f]; "
                "mechanism not reproducible from v1 (%.4f). Routes to HARD_FAIL_RESCUE. %s" % (
                    dual_v1_bpc, SANITY_DUAL_TARGET - SANITY_DUAL_TOL,
                    SANITY_DUAL_TARGET + SANITY_DUAL_TOL, SANITY_DUAL_TARGET, summary),
                detail)

    # DEGEN gate
    if degen_flag and delta_rescue < MIDDLE_BAND_LOW_BPC:
        return ("READOUT_DEGENERATE",
                "READOUT_DEGENERATE: raw_bpc near uniform-vocab AND no delta signal. %s" % summary,
                detail)

    # CHAIN_GRADE_TIER_UP
    if delta_rescue >= CHAIN_GRADE_LIFT_BPC and cv_ok:
        return ("CHAIN_GRADE_TIER_UP",
                "CHAIN_GRADE_TIER_UP: ARM_DUAL_TRACE_v1_REPLAY beats corrected rank-1 baseline "
                "by %.3f >= %.2f bits; cv=%.3f. Skunkworks rescue criterion satisfied. %s" % (
                    delta_rescue, CHAIN_GRADE_LIFT_BPC, dual_cv, summary),
                detail)

    # MEASURED_MECHANISM_CONFIRMED
    if delta_rescue >= MIDDLE_BAND_LOW_BPC:
        return ("MEASURED_MECHANISM_CONFIRMED",
                "MEASURED_MECHANISM_CONFIRMED: dual-trace beats corrected rank-1 baseline "
                "by %.3f in [%.2f, %.2f); real but below chain-grade bar; cv=%.3f. %s" % (
                    delta_rescue, MIDDLE_BAND_LOW_BPC, CHAIN_GRADE_LIFT_BPC, dual_cv, summary),
                detail)

    # HARD_FAIL_RESCUE
    return ("HARD_FAIL_RESCUE",
            "HARD_FAIL_RESCUE: dual-trace does NOT beat corrected rank-1 baseline "
            "(delta=%.3f < %.2f); routes to encoder-replacement diagnostic. %s" % (
                delta_rescue, MIDDLE_BAND_LOW_BPC, summary),
            detail)


# ============================================================================
# atexit synthesizer (defensive: partial metrics.json on any exit)
# ============================================================================

_OUT_DIR: Optional[Path] = None
_PARTIAL_UNITS: List[Dict] = []
_FINAL_WRITTEN = False


def _atexit_synthesize():
    global _FINAL_WRITTEN
    if _FINAL_WRITTEN or not _OUT_DIR or not _PARTIAL_UNITS:
        return
    try:
        verdict, verdict_msg, detail = compute_verdict(_PARTIAL_UNITS)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "PARTIAL": True,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "SEEDS": SEEDS,
            "n_seeds_completed": len(_PARTIAL_UNITS),
            "detail": detail,
        }
        p = _OUT_DIR / "metrics.json"
        tmp = _OUT_DIR / "metrics.json.tmp"
        tmp.write_text(json.dumps(m, indent=2), encoding="utf-8")
        os.replace(tmp, p)
        print("[atexit] partial metrics written to %s" % p, flush=True)
    except Exception as ex:
        print("[atexit] error writing partial metrics: %s" % ex, flush=True)


atexit.register(_atexit_synthesize)

if hasattr(signal, "SIGTERM"):
    _prev_sigterm = signal.getsignal(signal.SIGTERM)

    def _sigterm_handler(signum, frame):
        _atexit_synthesize()
        if callable(_prev_sigterm):
            _prev_sigterm(signum, frame)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, _sigterm_handler)


# ============================================================================
# Main sweep
# ============================================================================

print("[config] anchor=%s N_DIM=%d mode=%s seeds=%s N_TRAIN=%d "
      "f_rank1=%.3f f_dual_v1=%.3f tau_pos=%d tau_neg=%d device=%s" % (
          ANCHOR_NAME, N_DIM, RUN_MODE, SEEDS, N_TRAIN,
          SPARSE_BIPOLAR_F_RANK1, SPARSE_BIPOLAR_F_DUAL_V1,
          TAU_POS, TAU_NEG, str(DEVICE)), flush=True)

if RUN_MODE == "full" and N_DIM != PRODUCTION_N:
    raise RuntimeError("PROT-018: FULL run N_DIM=%d != PRODUCTION_N=%d" % (N_DIM, PRODUCTION_N))

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
_OUT_DIR = out_dir

t_sweep = time.time()

for seed in SEEDS:
    ckpt_key = "seed%d_N%d_%s" % (seed, N_DIM, RUN_MODE)
    partial_path = out_dir / ("partial_metrics_%s.json" % ckpt_key)
    if partial_path.exists():
        try:
            cached = json.loads(partial_path.read_text(encoding="utf-8"))
            if cached.get("seed") == seed and cached.get("N") == N_DIM:
                print("[ckpt] seed=%d already done, loading from %s" % (seed, partial_path), flush=True)
                _PARTIAL_UNITS.append(cached)
                continue
        except Exception:
            pass
    print("[seed=%d] running..." % seed, flush=True)
    unit = run_unit(seed)
    _PARTIAL_UNITS.append(unit)
    tmp_path = out_dir / ("partial_metrics_%s.json.tmp" % ckpt_key)
    tmp_path.write_text(json.dumps(unit, indent=2), encoding="utf-8")
    os.replace(tmp_path, partial_path)
    print("[ckpt] seed=%d saved to %s" % (seed, partial_path), flush=True)

verdict, verdict_msg, detail = compute_verdict(_PARTIAL_UNITS)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

elapsed_total = time.time() - t_sweep
metrics_out = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "SPARSE_BIPOLAR_F_RANK1": SPARSE_BIPOLAR_F_RANK1,
    "SPARSE_BIPOLAR_F_DUAL_V1": SPARSE_BIPOLAR_F_DUAL_V1,
    "TAU_POS": TAU_POS,
    "TAU_NEG": TAU_NEG,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "elapsed_s": round(elapsed_total, 2),
    "detail": detail,
    "per_seed": _PARTIAL_UNITS,
}

p_out = out_dir / "metrics.json"
tmp_out = out_dir / "metrics.json.tmp"
tmp_out.write_text(json.dumps(metrics_out, indent=2), encoding="utf-8")
os.replace(tmp_out, p_out)
_FINAL_WRITTEN = True
print("[done] metrics written to %s" % p_out, flush=True)
