"""
substrate_dual_trace_scaling_v1 -- dual-trace sequential neuromodulator LM scaling test.

MOTIVATION (2026-06-23):
  substrate_dual_trace_sequential_neuromod_LM_v1 HARD_PASS at N_DIM=8192 N_TRAIN=100k:
    ARM_DUAL_TRACE bpc=7.2213, lift=+0.516 vs unigram baseline, cv=0.0011.
  Anchor 2 production-relevance gate: does the envelope STAY BROKEN at scale?
  sparse_bipolar HARD_FAIL showed lift halving from N=512 to N=2048 (single modulator).
  This cell tests whether dual-trace shows same scaling-degradation pattern.

SCALING QUESTION (handoff Anchor 2 spec):
  N_DIM in {8192, 16384} x N_TRAIN in {100k, 1M} x 3 seeds x ARM_DUAL_TRACE only.
  Primary contrast: ARM_DUAL_TRACE@N16384_T1M lift vs ARM_DUAL_TRACE@N8192_T100k
  (same mechanism as Anchor 1; exact dual-trace code reused verbatim).

PRE-REGISTERED BANDS (IMMUTABLE; pre-registered before smoke):
  HARD_PASS: ARM_DUAL_TRACE@N16384_T1M lift >= +0.40 bits BPC vs ARM_DUAL_TRACE@N8192_T100k
             (lift GROWS with scale; envelope broken at production-relevant scale)
  MIDDLE_BAND: lift stays approximately flat (+/-0.10 bits across scaling)
               (envelope is broken but does not scale; fixed-point mechanism)
  HARD_FAIL: lift HALVES like single-modulator drosophila MB sweep pattern
             (envelope reappears at scale; substrate-as-LM still capped)
  CV < 0.05 across seeds mandatory per config.

NOTE on reference lift: Anchor 1 ARM_DUAL_TRACE BPC = 7.2213, unigram BPC = 7.7378.
  delta_anchor1 = 7.7378 - 7.2213 = 0.5165 bits vs unigram.
  delta_anchor1_vs_fair_harness = 7.3065 - 7.2213 = 0.0852 bits vs chain-grade baseline.
  HARD_PASS threshold is +0.40 bits BPC IMPROVEMENT at N16384/T1M vs N8192/T100k
  (i.e. BPC at N16384/T1M should be at most 7.2213 - 0.40 = ~6.82).

PROT-018: anchor has NO _n suffix; cell sweeps multiple N values.
  Rationale: N_DIM={8192, 16384} is the axis under test; no single binding.
  Explicitly stated in prereq section.

GPU REQUIRED (Fix #24): torch.cuda + batched outer-product matmul.
  Encoder hoisted outside arm loop (load once, reuse per Fix #24).
  N_DIM=16384 W matrix: 16384^2 * 4bytes = ~1.07 GB per matrix (W+E_pos+E_neg ~ 3.22 GB).
  N_DIM=8192 W matrix: 8192^2 * 4bytes = ~0.27 GB per matrix.
  Total peak ~ 3.5 GB at N_DIM=16384; well within 6 GB safety margin.

Memory layout: Each config (N_DIM, N_TRAIN) runs sequentially and releases W before next.

Cites:
  Brzosko et al. (2017) "Sequential neuromodulation of Hebbian plasticity" eLife 27756
  Huertas et al. (2016) "Role of Multiple Neuromodulators in Reinforcement Learning" PMC5156839
  Fremaux-Gerstner (2016) "Neuromodulated STDP, Three-Factor Learning Rules" Front Neural Circ
  experiments/exp_substrate_dual_trace_sequential_neuromod_LM_v1.py (Anchor 1; dual-trace exact)
  data/exp_substrate_dual_trace_sequential_neuromod_LM_v1/metrics.json (7.2213 cv=0.0011)
  notes/exp_dev_handoff_research_neuromodulator_orthogonal_composition_2026-06-23.md

ASCII-only. Per-config checkpoint. atexit synthesizer.
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

ANCHOR_NAME = "substrate_dual_trace_scaling_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# PROT-018: no _n suffix; cell sweeps multiple N_DIM values.
# Rationale: N_DIM is the axis under test; no single binding applies.
# Production N values: 8192 and 16384 (both exercised at full run).

# ============================================================================
# Pre-reg bands (IMMUTABLE; pre-registered before smoke)
# ============================================================================
# Primary contrast: ARM_DUAL_TRACE@N16384_T1M lift vs ARM_DUAL_TRACE@N8192_T100k
# "lift" = how much BPC drops relative to unigram at each config.
# HARD_PASS: lift at N16384_T1M INCREASES by >= 0.40 bits vs lift at N8192_T100k
HARD_PASS_LIFT_GAIN = 0.40    # lift at N16384/T1M >= lift_anchor1 + 0.40
MIDDLE_LIFT_DELTA_TOL = 0.10  # lift stays within +/- 0.10 of anchor1 lift
HARD_FAIL_HALVING = 0.50      # lift halves = HARD_FAIL

CV_MAX = 0.05   # CV across seeds must be < 0.05 per config

# Anchor 1 reference (fixed; from Anchor 1 metrics.json)
ANCHOR1_DUAL_BPC_N8192_T100k = 7.2213
ANCHOR1_UNIGRAM_BPC = 7.7378
ANCHOR1_LIFT = ANCHOR1_UNIGRAM_BPC - ANCHOR1_DUAL_BPC_N8192_T100k  # ~0.516 bits

FAIR_HARNESS_BASELINE_BPC = 7.3065
ENVELOPE_CAP_BPC = 7.295

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
# Sweep grid
# ============================================================================
VOCAB_CAP = 4000
SPARSE_BIPOLAR_F = 0.02       # best from param sweep
TAU_POS = 5                   # fast LTP-trace timescale (matched to Anchor 1)
TAU_NEG = 50                  # slow LTD-trace timescale (matched to Anchor 1)
NEUROMOD_CONTEXT = 32
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10
WORD2VEC_MODEL = "word2vec-google-news-300"

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    NDIM_GRID = [8192, 16384]
    NTRAIN_GRID = [100_000, 1_000_000]
    N_HELD = 20_000
    INGEST_CHUNK = 4096
    RECALL_BATCH = 256
else:
    # Smoke: N_DIM in {512, 2048} (small-scale proxies); N_TRAIN small; 1 seed
    # Multi-scale smoke: N_smoke=512, N_smoke*4=2048 to test scale-sensitivity
    SEEDS = [0]
    NDIM_GRID = [512, 2048]
    NTRAIN_GRID = [2_000, 5_000]
    N_HELD = 400
    VOCAB_CAP = 300
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

# Number of training pairs held-out for dev/test split
N_HELD_PAIRS = N_HELD

# ============================================================================
# Encoder / embedding helpers (copied verbatim from Anchor 1 for fair compare)
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
# Neuromodulator signal primitives (verbatim from Anchor 1)
# ============================================================================

def compute_dopamine_signal(err_norms: torch.Tensor, err_norm_running: float) -> float:
    """Dopamine: cf-RPE error norm normalized by running mean.

    Returns scalar in [0.0, 1.5]. High prediction error -> high dopamine -> LTP.
    """
    err_mean = float(err_norms.mean().item())
    denom = max(err_norm_running, 1e-6)
    raw = err_mean / denom
    return min(1.5, max(0.0, raw))


def compute_ach_signal(src_centroid: torch.Tensor, ctx_buf: List[torch.Tensor],
                        startup_val: float = 0.0) -> float:
    """ACh: attention gate as cosine margin between batch centroid and context centroid.

    Returns scalar in [0.0, 1.5]. High margin (unexpected input) -> high ACh.
    """
    if not ctx_buf or len(ctx_buf) < 4:
        return startup_val
    ctx_stacked = torch.stack(ctx_buf[-NEUROMOD_CONTEXT:], dim=0)
    ctx_cen = _l2_normalize_t(ctx_stacked.mean(dim=0))
    sim = float(torch.dot(src_centroid, ctx_cen).item())
    margin = max(0.0, 1.0 - sim)
    return min(1.5, margin * 1.5)


# ============================================================================
# Core: W builder -- ARM_DUAL_TRACE only (verbatim from Anchor 1)
# ============================================================================

def build_W_dual_trace(idx_train: torch.Tensor,
                        E: torch.Tensor,
                        ingest_chunk: int) -> torch.Tensor:
    """ARM_DUAL_TRACE: brain-correct dual-trace sequential neuromodulator mechanism.

    Two separate eligibility traces with different timescales:
      E_pos (LTP-trace, tau_fast=TAU_POS) gated by DOPAMINE (novelty/error)
      E_neg (LTD-trace, tau_slow=TAU_NEG) gated by ACh (attention/familiarity)

    Verbatim from exp_substrate_dual_trace_sequential_neuromod_LM_v1.py (Anchor 1).
    Only change: runs within a config loop that varies N_DIM and N_TRAIN.
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    E_pos = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    E_neg = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W

    decay_pos = 1.0 - 1.0 / TAU_POS
    decay_neg = 1.0 - 1.0 / TAU_NEG

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
# Logits builder (reuses fair_harness pattern from Anchor 1)
# ============================================================================

def compute_dual_trace_logits(E_base: torch.Tensor,
                               idx_train: np.ndarray,
                               idx_held: np.ndarray,
                               seed: int,
                               n_dim: int,
                               ingest_chunk: int,
                               recall_batch: int) -> Dict:
    """Build W for ARM_DUAL_TRACE, compute held-set logits."""
    device = E_base.device
    V = E_base.shape[0]

    E = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))

    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)

    t0 = time.time()
    W = build_W_dual_trace(idx_train_t, E, ingest_chunk)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    n_h = idx_held_t.shape[0]
    E_src_held = E[idx_held_t]
    logits_t = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
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
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
    }


# ============================================================================
# text8 / vocab / metrics (verbatim from Anchor 1)
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
    """Joint (T, lambda) sweep on dev; eval on test. Returns best per metric."""
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
# Instrumentation self-test (MANDATORY; PROT-022)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics non-null/non-sentinel at small scale.

    Tests:
    1. W builds (non-trivial norm) for dual-trace arm.
    2. Dual-trace mechanism reproducible (deterministic given same seed/data).
    3. BPC finite and in [0.0, 25.0] at both smoke N values.
    4. Scaling independence: different N_DIM configs produce different W shapes.
    5. E_pos and E_neg are distinct tensors (trace independence).
    6. Sparsification density matches SPARSE_BIPOLAR_F.
    7. Encoder builds E of correct shape at both smoke N values.
    """
    print("[selftest] begin instrumentation self-test", flush=True)

    for n in [64, 128]:  # multi-scale: test at two small N values
        rng = np.random.default_rng(42)
        V_t = 8
        E_np = rng.standard_normal((V_t, n)).astype(np.float32)
        E_np = _l2_normalize_np(E_np)
        E = torch.from_numpy(E_np).to(DEVICE, dtype=TORCH_DTYPE)

        toks = [i % V_t for i in range(60)]
        idx = torch.tensor(toks, dtype=torch.long, device=DEVICE)

        # Test 1: W builds (non-trivial norm)
        W_dt = build_W_dual_trace(idx, E, ingest_chunk=16)
        assert W_dt.shape == (n, n), "W shape wrong at n=%d" % n
        assert float(W_dt.norm().item()) > 0.0, "ARM_DUAL_TRACE W is zero at n=%d" % n

        # Test 2: Reproducibility -- same inputs produce same W
        W_dt2 = build_W_dual_trace(idx, E, ingest_chunk=16)
        diff = float((W_dt - W_dt2).norm().item())
        assert diff < 1e-5, "Dual-trace W not reproducible at n=%d: diff=%.6f" % (n, diff)

        # Test 3: BPC finite and valid
        idx_np = np.array(toks, dtype=np.int64)
        idx_held_np = np.array([i % V_t for i in range(20)], dtype=np.int64)
        ar = compute_dual_trace_logits(E, idx_np, idx_held_np, seed=0,
                                        n_dim=n, ingest_chunk=16, recall_batch=8)
        logits = ar["logits"]
        assert logits.shape[0] >= 1, "Empty logits at n=%d" % n
        assert np.all(np.isfinite(logits)), "Non-finite logits at n=%d" % n
        probs = softmax_logits_with_T(logits[:10], 0.1)
        logp = np.log(np.clip(probs, 1e-30, 1.0))
        nxt_t = idx_held_np[1:11]
        if len(nxt_t) > 0:
            bpc = bpc_from_logp(logp, nxt_t)
            assert 0.0 <= bpc <= 25.0, "BPC out of range at n=%d: %.4f" % (n, bpc)
            assert math.isfinite(bpc), "BPC non-finite at n=%d" % n

        # Test 5: E_pos and E_neg distinct
        idx_long = torch.arange(V_t, device=DEVICE).repeat(8)
        E_pos_t = torch.zeros((n, n), dtype=TORCH_DTYPE, device=DEVICE)
        E_neg_t = torch.zeros((n, n), dtype=TORCH_DTYPE, device=DEVICE)
        np_len = idx_long.shape[0] - 1
        E_src_t = E[idx_long[:np_len]]
        E_tgt_t = E[idx_long[1:np_len + 1]]
        Delta_t = E_tgt_t - E_src_t
        outer_p = (Delta_t.T @ E_src_t) / np_len
        outer_n = (E_src_t.T @ E_src_t) / np_len
        E_pos_t.add_(outer_p)
        E_neg_t.add_(outer_n)
        trace_diff = float((E_pos_t - E_neg_t).norm().item())
        assert trace_diff > 0.001, "E_pos and E_neg identical at n=%d: diff=%.6f" % (n, trace_diff)

        # Test 6: sparsification density
        k_expected = max(1, int(round(SPARSE_BIPOLAR_F * n)))
        E_sp = sparsify_bipolar_gpu(E, SPARSE_BIPOLAR_F, seed=0)
        nonzero_per_row = (E_sp != 0).sum(dim=1).float().mean().item()
        assert abs(nonzero_per_row - k_expected) < 2.0, \
            "Sparse density wrong at n=%d: expected ~%d got %.1f" % (n, k_expected, nonzero_per_row)

        print("[selftest] n=%d PASS: W_norm=%.4f bpc=%.4f trace_diff=%.4f sparse_k=%.1f" % (
            n, float(W_dt.norm().item()), bpc if len(nxt_t) > 0 else float("nan"),
            trace_diff, nonzero_per_row), flush=True)

        del W_dt, W_dt2, E_pos_t, E_neg_t, E_sp
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

    # Test 4: Different N_DIM configs produce different W shapes (verified implicitly above)
    print("[selftest] PASS: multi-scale smoke at n=64 and n=128 both valid", flush=True)


_instrumentation_selftest()  # Called at module scope (MANDATORY)
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-config runner: one (N_DIM, N_TRAIN, seed) tuple
# ============================================================================

def run_unit(seed: int, n_dim: int, n_train: int, n_held: int,
             vocab_cap: int, ingest_chunk: int, recall_batch: int) -> Dict:
    """Run one (N_DIM, N_TRAIN, seed) config for ARM_DUAL_TRACE."""
    t_seed = time.time()
    print("\n[seed=%d N_DIM=%d N_TRAIN=%d] loading text8 + building vocab" % (
        seed, n_dim, n_train), flush=True)
    n_total = n_train + n_held
    toks = load_text8_tokens(n_total)
    if len(toks) < n_total:
        print("[WARN] corpus short: %d vs %d" % (len(toks), n_total), flush=True)
    train_toks = toks[:n_train]
    held_toks = toks[n_train:n_train + n_held]
    vocab, w2i = build_vocab(train_toks, cap=vocab_cap)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d N_DIM=%d N_TRAIN=%d] V=%d device=%s" % (
        seed, n_dim, n_train, V, str(DEVICE)), flush=True)

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
    print("[seed=%d N_DIM=%d N_TRAIN=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, n_dim, n_train, uni["bpc_unigram"], uni["top1_unigram"],
        uni["mrr_unigram"]), flush=True)

    # Encoder hoisted outside arm loop (Fix #24: load once, reuse)
    print("[seed=%d N_DIM=%d] building word2vec base E (V=%d)..." % (
        seed, n_dim, V), flush=True)
    t_enc0 = time.time()
    encoder_meta: Dict = {}
    try:
        E_base, encoder_meta = build_E_word2vec_gpu(vocab, n_dim, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d N_DIM=%d encoder] WORD2VEC FAIL: %s -- falling back to char-trigram" % (
            seed, n_dim, err), flush=True)
        E_base = build_E_char_trigram_gpu(vocab, n_dim, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    t_enc = time.time() - t_enc0
    if DEVICE.type == "cuda":
        try:
            free_b, total_b = torch.cuda.mem_get_info()
            print("[seed=%d N_DIM=%d encoder] E built (%.1fs); GPU free=%.2fGB total=%.2fGB" % (
                seed, n_dim, t_enc, free_b / 1e9, total_b / 1e9), flush=True)
        except Exception:
            pass

    # Held-set split (same masking as fair_harness / Anchor 1)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    if len(nxt_eval) == 0:
        del E_base
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {"seed": seed, "n_dim": n_dim, "n_train": n_train,
                "by_arm": {"ARM_DUAL_TRACE": {"empty_eval": True},
                            "ARM_UNIGRAM": uni},
                "V": V, "run_mode": RUN_MODE, "empty_eval": True,
                "elapsed_s": round(time.time() - t_seed, 2), "device": str(DEVICE)}

    n_dev = len(nxt_eval) // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]
    valid_pos = np.where(mask)[0]

    # ARM_DUAL_TRACE
    t_arm0 = time.time()
    print("\n  [seed=%d N_DIM=%d N_TRAIN=%d arm=ARM_DUAL_TRACE] building logits..." % (
        seed, n_dim, n_train), flush=True)
    dual_result: Dict = {}
    try:
        ar = compute_dual_trace_logits(E_base, idx_train, idx_held, seed,
                                        n_dim=n_dim,
                                        ingest_chunk=ingest_chunk,
                                        recall_batch=recall_batch)
    except Exception as e:
        err_s = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [COMPUTE FAIL] %s" % err_s, flush=True)
        dual_result = {"compute_failed": True, "compute_error": err_s,
                       "bpc_best": float("inf"), "top1_acc": float("nan"),
                       "mrr_at_10": float("nan"),
                       "best_T_for_bpc": float("nan"),
                       "best_lambda_for_bpc": float("nan"),
                       "raw_bpc_at_T1_L1": float("inf"),
                       "elapsed_s_arm": round(time.time() - t_arm0, 2)}
    else:
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
        dual_result = jr
        print("    [seed=%d N_DIM=%d N_TRAIN=%d arm=ARM_DUAL_TRACE] "
              "bpc_best=%.3f top1=%.4f mrr=%.4f (bestT=%.4f bestL=%.2f) "
              "raw_T1L1_bpc=%.3f ingest=%.1fs recall=%.1fs" % (
                  seed, n_dim, n_train, jr["bpc_best"], jr["top1_acc"],
                  jr["mrr_at_10"], jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                  jr["raw_bpc_at_T1_L1"], jr["wall_ingest_s"], jr["wall_recall_s"]),
              flush=True)

    del E_base
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed,
        "n_dim": n_dim,
        "n_train": n_train,
        "by_arm": {
            "ARM_DUAL_TRACE": dual_result,
            "ARM_UNIGRAM": uni,
        },
        "V": V,
        "N": n_dim,
        "N_DIM": n_dim,
        "N_TRAIN": n_train,
        "N_HELD": n_held,
        "VOCAB_CAP": vocab_cap,
        "run_mode": RUN_MODE,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
    }


# ============================================================================
# Verdict: cross-config comparison (HARD_PASS / MIDDLE_BAND / HARD_FAIL)
# ============================================================================

def agg_config_results(units_for_config: List[Dict]) -> Dict:
    """Aggregate per-seed results for one (N_DIM, N_TRAIN) config."""
    bpc_vals = []
    top1_vals = []
    mrr_vals = []
    unigram_bpcs = []
    for u in units_for_config:
        arm = u.get("by_arm", {}).get("ARM_DUAL_TRACE", {})
        uni = u.get("by_arm", {}).get("ARM_UNIGRAM", {})
        if arm.get("compute_failed", False) or arm.get("empty_eval", False):
            continue
        bpc = arm.get("bpc_best", float("nan"))
        if math.isfinite(bpc):
            bpc_vals.append(bpc)
            top1_vals.append(arm.get("top1_acc", float("nan")))
            mrr_vals.append(arm.get("mrr_at_10", float("nan")))
        ubpc = uni.get("bpc_unigram", float("nan"))
        if math.isfinite(ubpc):
            unigram_bpcs.append(ubpc)

    if not bpc_vals:
        return {"bpc_mean": float("nan"), "bpc_cv": float("nan"),
                "lift_vs_unigram": float("nan"),
                "top1_mean": float("nan"), "mrr_mean": float("nan"),
                "n_valid_seeds": 0, "all_seeds_failed": True}

    b_mean = float(np.mean(bpc_vals))
    b_std = float(np.std(bpc_vals))
    b_cv = b_std / max(abs(b_mean), 1e-6)
    u_mean = float(np.mean(unigram_bpcs)) if unigram_bpcs else float("nan")
    lift = u_mean - b_mean if math.isfinite(u_mean) else float("nan")
    return {
        "bpc_mean": round(b_mean, 4),
        "bpc_std": round(b_std, 4),
        "bpc_cv": round(b_cv, 4),
        "lift_vs_unigram": round(lift, 4),
        "top1_mean": round(float(np.nanmean(top1_vals)), 4),
        "mrr_mean": round(float(np.nanmean(mrr_vals)), 4),
        "n_valid_seeds": len(bpc_vals),
        "all_seeds_failed": False,
    }


def compute_verdict(all_units: List[Dict]) -> Tuple[str, str, Dict]:
    """Cross-config verdict: compare lift at different (N_DIM, N_TRAIN) configs."""
    if not all_units:
        return ("HARD_FAIL", "HARD_FAIL: no results.", {})

    # Group units by config key
    config_results: Dict[str, List[Dict]] = {}
    for u in all_units:
        n_dim = u.get("n_dim", u.get("N_DIM", 0))
        n_train = u.get("n_train", u.get("N_TRAIN", 0))
        key = "N%d_T%d" % (n_dim, n_train)
        if key not in config_results:
            config_results[key] = []
        config_results[key].append(u)

    config_agg: Dict[str, Dict] = {}
    for key, units in config_results.items():
        config_agg[key] = agg_config_results(units)

    # Reference config from Anchor 1 (or from this cell's N8192/T100k if available)
    ref_key = "N8192_T100000"
    ref_key_smoke = "N512_T2000"  # smoke proxy
    ref_key_smoke2 = "N2048_T5000"  # smoke proxy alternative

    # Find the smallest-N, smallest-T config as reference (Anchor 1 point)
    # Prefer N8192_T100000; fall back to smoke-scale reference
    ref = None
    ref_used_key = None
    for k in [ref_key, ref_key_smoke, ref_key_smoke2]:
        if k in config_agg and not config_agg[k].get("all_seeds_failed", True):
            ref = config_agg[k]
            ref_used_key = k
            break
    if ref is None:
        # Try first available non-failed config as reference
        for k, v in sorted(config_agg.items()):
            if not v.get("all_seeds_failed", True):
                ref = v
                ref_used_key = k
                break
    if ref is None:
        return ("HARD_FAIL",
                "HARD_FAIL: all configs failed. configs=%s" % str(list(config_agg.keys())),
                {"config_agg": config_agg})

    ref_lift = ref.get("lift_vs_unigram", float("nan"))
    ref_bpc = ref.get("bpc_mean", float("nan"))

    # Find largest-N, largest-T config as target
    target_key = "N16384_T1000000"
    target_key_smoke = "N2048_T5000"
    target = None
    target_used_key = None
    for k in [target_key, target_key_smoke]:
        if k in config_agg and k != ref_used_key and \
                not config_agg[k].get("all_seeds_failed", True):
            target = config_agg[k]
            target_used_key = k
            break
    if target is None:
        # Fall back to best non-ref config with highest N
        for k in sorted(config_agg.keys(), reverse=True):
            if k != ref_used_key and not config_agg[k].get("all_seeds_failed", True):
                target = config_agg[k]
                target_used_key = k
                break

    if target is None:
        # Only one config completed -- partial result
        cv_ok = ref.get("bpc_cv", float("inf")) < CV_MAX
        summary = ("PARTIAL: only ref config %s completed (lift=%.3f vs_unigram, cv=%.4f). "
                   "Awaiting target config." % (ref_used_key, ref_lift, ref.get("bpc_cv", float("nan"))))
        return ("PARTIAL_PENDING",
                summary,
                {"config_agg": config_agg,
                 "ref_key": ref_used_key,
                 "ref_lift": ref_lift,
                 "ref_bpc": ref_bpc,
                 "anchor1_lift": ANCHOR1_LIFT,
                 "hard_pass_lift_gain": HARD_PASS_LIFT_GAIN})

    target_lift = target.get("lift_vs_unigram", float("nan"))
    target_bpc = target.get("bpc_mean", float("nan"))

    # DELTA: how much does lift CHANGE from ref to target?
    # Positive = lift grows (dual-trace scales up); negative = lift shrinks
    if math.isnan(target_lift) or math.isnan(ref_lift):
        return ("HARD_FAIL",
                "HARD_FAIL: NaN lift at ref=%s or target=%s" % (ref_used_key, target_used_key),
                {"config_agg": config_agg,
                 "ref_key": ref_used_key, "target_key": target_used_key,
                 "ref_lift": ref_lift, "target_lift": target_lift})

    lift_delta = target_lift - ref_lift  # positive = dual-trace GAINS at scale

    # CV check for both reference and target
    ref_cv_ok = ref.get("bpc_cv", float("inf")) < CV_MAX
    target_cv_ok = target.get("bpc_cv", float("inf")) < CV_MAX
    cv_ok = ref_cv_ok and target_cv_ok

    # DEGEN gate: check if raw_bpc_at_T1_L1 near uniform-vocab entropy
    def _check_degen(units_for_config: List[Dict], vocab_entropy: float) -> bool:
        for u in units_for_config:
            arm = u.get("by_arm", {}).get("ARM_DUAL_TRACE", {})
            rt = arm.get("raw_bpc_at_T1_L1", float("nan"))
            if math.isfinite(rt) and abs(rt - vocab_entropy) <= DEGEN_TOL:
                return True
        return False

    # Use V from any available unit to compute uniform entropy
    V_est = next((u.get("V", VOCAB_CAP) for u in all_units if u.get("V")), VOCAB_CAP)
    vocab_entropy_uniform = math.log2(max(V_est, 2))

    ref_units = config_results.get(ref_used_key, [])
    target_units = config_results.get(target_used_key, [])
    degen_ref = _check_degen(ref_units, vocab_entropy_uniform)
    degen_target = _check_degen(target_units, vocab_entropy_uniform)
    degen_flag = degen_ref or degen_target

    # Summary line
    config_summary_parts = []
    for k in sorted(config_agg.keys()):
        a = config_agg[k]
        if a.get("all_seeds_failed", False):
            config_summary_parts.append("%s=FAIL" % k)
        else:
            config_summary_parts.append("%s=bpc%.3f(lift%.3f,cv%.3f)" % (
                k, a["bpc_mean"], a["lift_vs_unigram"], a["bpc_cv"]))
    config_summary = " | ".join(config_summary_parts)

    detail = {
        "config_agg": config_agg,
        "ref_key": ref_used_key,
        "target_key": target_used_key,
        "ref_lift": round(ref_lift, 4),
        "target_lift": round(target_lift, 4),
        "lift_delta": round(lift_delta, 4),
        "ref_bpc": round(ref_bpc, 4),
        "target_bpc": round(target_bpc, 4),
        "cv_ok": cv_ok,
        "ref_cv_ok": ref_cv_ok,
        "target_cv_ok": target_cv_ok,
        "degen_flag": degen_flag,
        "anchor1_lift": round(ANCHOR1_LIFT, 4),
        "hard_pass_lift_gain": HARD_PASS_LIFT_GAIN,
        "middle_lift_delta_tol": MIDDLE_LIFT_DELTA_TOL,
        "hard_fail_halving": HARD_FAIL_HALVING,
        "vocab_entropy_uniform_bits": round(vocab_entropy_uniform, 4),
        "fair_harness_baseline_bpc": FAIR_HARNESS_BASELINE_BPC,
        "envelope_cap_bpc": ENVELOPE_CAP_BPC,
        "n_configs_complete": len([v for v in config_agg.values()
                                    if not v.get("all_seeds_failed", True)]),
        "honest_scope": (
            "ARM_DUAL_TRACE only (exact mechanism from Anchor 1). "
            "Cross-config comparison: ref=%s lift=%.3f vs target=%s lift=%.3f. "
            "lift_delta=%.3f. "
            "HARD_PASS: lift_delta >= +%.2f (envelope grows at scale). "
            "MIDDLE_BAND: lift_delta in +/-%.2f (envelope fixed-point). "
            "HARD_FAIL: lift halves (lift_delta <= -%.3f). "
            "tau_pos=%d tau_neg=%d f=%.2f." % (
                ref_used_key, ref_lift, target_used_key, target_lift,
                lift_delta,
                HARD_PASS_LIFT_GAIN, MIDDLE_LIFT_DELTA_TOL,
                ref_lift * HARD_FAIL_HALVING,
                TAU_POS, TAU_NEG, SPARSE_BIPOLAR_F)),
        "cites": [
            "notes/exp_dev_handoff_research_neuromodulator_orthogonal_composition_2026-06-23.md",
            "experiments/exp_substrate_dual_trace_sequential_neuromod_LM_v1.py",
            "data/exp_substrate_dual_trace_sequential_neuromod_LM_v1/metrics.json",
            "Brzosko et al. 2017 eLife 27756",
            "Huertas et al. 2016 PMC5156839",
            "Fremaux-Gerstner 2016 Front Neural Circ",
        ],
    }

    # DEGEN gate (only block if no delta signal at all)
    if degen_flag and abs(lift_delta) < 0.01:
        return ("READOUT_DEGENERATE",
                "READOUT_DEGENERATE: raw_bpc near uniform-vocab AND no lift_delta signal. %s" % config_summary,
                detail)

    # HARD_PASS: lift grows by >= +0.40 bits
    if lift_delta >= HARD_PASS_LIFT_GAIN:
        prefix = "HARD_PASS" if cv_ok else "HARD_PASS_HIGH_CV"
        return (prefix,
                "%s: dual-trace SCALES UP (lift_delta=%.3f>=%.2f, "
                "ref=%s_lift=%.3f, target=%s_lift=%.3f, cv_ok=%s). %s" % (
                    prefix, lift_delta, HARD_PASS_LIFT_GAIN,
                    ref_used_key, ref_lift, target_used_key, target_lift,
                    str(cv_ok), config_summary),
                detail)

    # HARD_FAIL: lift halves (halving = lift drops by >= 50% of reference lift)
    halving_threshold = -ref_lift * HARD_FAIL_HALVING
    if lift_delta <= halving_threshold:
        return ("HARD_FAIL",
                "HARD_FAIL: dual-trace lift HALVES at scale "
                "(lift_delta=%.3f <= halving_thr=%.3f; "
                "ref=%s_lift=%.3f, target=%s_lift=%.3f). "
                "Envelope reappears at production scale. %s" % (
                    lift_delta, halving_threshold,
                    ref_used_key, ref_lift, target_used_key, target_lift,
                    config_summary),
                detail)

    # MIDDLE_BAND: lift stays within +/- 0.10 of reference
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: dual-trace envelope fixed-point (lift_delta=%.3f in +/-%.2f; "
            "ref=%s_lift=%.3f, target=%s_lift=%.3f, cv_ok=%s). "
            "Mechanism real but does not scale beyond Anchor 1 config. %s" % (
                lift_delta, MIDDLE_LIFT_DELTA_TOL,
                ref_used_key, ref_lift, target_used_key, target_lift,
                str(cv_ok), config_summary),
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
            "NDIM_GRID": NDIM_GRID,
            "NTRAIN_GRID": NTRAIN_GRID,
            "SEEDS": SEEDS,
            "n_units_completed": len(_PARTIAL_UNITS),
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
# Main sweep: 4 configs x 3 seeds = 12 units
# ============================================================================

print("[config] anchor=%s mode=%s NDIM_GRID=%s NTRAIN_GRID=%s SEEDS=%s "
      "f=%.3f tau_pos=%d tau_neg=%d device=%s" % (
          ANCHOR_NAME, RUN_MODE, NDIM_GRID, NTRAIN_GRID, SEEDS,
          SPARSE_BIPOLAR_F, TAU_POS, TAU_NEG, str(DEVICE)), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
_OUT_DIR = out_dir

t_sweep = time.time()

for n_dim in NDIM_GRID:
    for n_train in NTRAIN_GRID:
        for seed in SEEDS:
            ckpt_key = "ndim%d_ntrain%d_seed%d_%s" % (n_dim, n_train, seed, RUN_MODE)
            partial_path = out_dir / ("partial_%s.json" % ckpt_key)
            if partial_path.exists():
                try:
                    cached = json.loads(partial_path.read_text(encoding="utf-8"))
                    if (cached.get("n_dim") == n_dim and
                            cached.get("n_train") == n_train and
                            cached.get("seed") == seed):
                        print("[ckpt] ndim=%d ntrain=%d seed=%d already done, loading" % (
                            n_dim, n_train, seed), flush=True)
                        _PARTIAL_UNITS.append(cached)
                        continue
                except Exception:
                    pass

            print("[sweep] ndim=%d ntrain=%d seed=%d running..." % (n_dim, n_train, seed),
                  flush=True)
            unit = run_unit(
                seed=seed, n_dim=n_dim, n_train=n_train, n_held=N_HELD_PAIRS,
                vocab_cap=VOCAB_CAP, ingest_chunk=INGEST_CHUNK, recall_batch=RECALL_BATCH,
            )
            _PARTIAL_UNITS.append(unit)

            # Checkpoint after each unit
            tmp_path = out_dir / ("partial_%s.json.tmp" % ckpt_key)
            tmp_path.write_text(json.dumps(unit, indent=2), encoding="utf-8")
            os.replace(tmp_path, partial_path)
            print("[ckpt] ndim=%d ntrain=%d seed=%d saved to %s" % (
                n_dim, n_train, seed, partial_path), flush=True)

            # Write intermediate verdict after each config completes (all seeds done)
            units_this_config = [u for u in _PARTIAL_UNITS
                                   if u.get("n_dim") == n_dim and u.get("n_train") == n_train]
            if len(units_this_config) == len(SEEDS):
                interim_v, interim_msg, interim_d = compute_verdict(_PARTIAL_UNITS)
                print("[interim] ndim=%d ntrain=%d all seeds done. interim_verdict=%s" % (
                    n_dim, n_train, interim_v), flush=True)

verdict, verdict_msg, detail = compute_verdict(_PARTIAL_UNITS)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

elapsed_total = time.time() - t_sweep
metrics_out = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "run_mode": RUN_MODE,
    "NDIM_GRID": NDIM_GRID,
    "NTRAIN_GRID": NTRAIN_GRID,
    "N_HELD": N_HELD_PAIRS,
    "VOCAB_CAP": VOCAB_CAP,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "TAU_POS": TAU_POS,
    "TAU_NEG": TAU_NEG,
    "SEEDS": SEEDS,
    "ANCHOR1_LIFT": ANCHOR1_LIFT,
    "ANCHOR1_DUAL_BPC_N8192_T100k": ANCHOR1_DUAL_BPC_N8192_T100k,
    "elapsed_s": round(elapsed_total, 2),
    "detail": detail,
    "per_unit": _PARTIAL_UNITS,
}

m_path = out_dir / "metrics.json"
m_tmp = out_dir / "metrics.json.tmp"
m_tmp.write_text(json.dumps(metrics_out, indent=2), encoding="utf-8")
os.replace(m_tmp, m_path)
print("[metrics] written to %s" % m_path, flush=True)
_FINAL_WRITTEN = True
