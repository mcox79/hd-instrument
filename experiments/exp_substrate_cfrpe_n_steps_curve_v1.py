"""
substrate_cfrpe_n_steps_curve_v1 -- cf-RPE N_STEPS convergence curve

HYPOTHESIS: cf-RPE delta rule continues converging past N_STEPS=1000.
Meta-LR cell (N_STEPS=2000) reached BPC=7.0642 vs heterogeneous_plasticity
(N_STEPS=1000) at 7.1052 -- the extra 1000 steps add +0.041 bits.
This cell sweeps N_STEPS in {500, 1000, 1500, 2000, 3000, 5000} to determine:
  (a) asymptote location
  (b) whether cf-RPE @ N_STEPS=5000 lifts >= +0.25 bits over Hebbian baseline
      (beating current chain-grade lift of ~+0.20 by margin)
  (c) whether we should update the chain-grade anchor to the asymptote N_STEPS

TWO ARM TYPES per N_STEPS value:
  ARM_CFRPE_<N>      -- cf-RPE only, N_STEPS=N (EXACT rule from heterogeneous_plasticity)
  ARM_HEBBIAN        -- rank-1 symmetric Hebbian baseline (ONE total, not per-N_STEPS)

Reported as separate arm keys per N_STEPS for peek_arm_metrics compatibility:
  each key = "N<n_steps>_cfrpe" or "ARM_HEBBIAN_BASELINE"

PRE-REG BANDS:
  HARD_PASS_NEW_ANCHOR:  cf-RPE @ max(N_STEPS_GRID) lift over Hebbian >= +0.25 bits
  CHAIN_GRADE_BONUS:     lift @ max(N_STEPS_GRID) >= +0.30 bits (updates chain-grade)
  ASYMPTOTE_CONVERGED:   lift @ max(N_STEPS) within +0.02 of lift @ 2nd-to-max N_STEPS
  ASYMPTOTE_OPEN:        lift @ max(N_STEPS) > lift @ 2nd-to-max by >= +0.03
  HARD_FAIL:             no monotonic increase across N_STEPS grid OR
                         lift @ max_steps <= lift @ min_steps + 0.02
  Sanity: ARM_HEBBIAN_BASELINE BPC = 7.3065 +/- 0.05 (full mode only)
  cv < 0.05 across seeds mandatory (for max-N_STEPS arm)

ENCODING: word2vec-google-news-300 projected to N_DIM=8192 sparse-bipolar (f=0.05)
EXACT cf-RPE from heterogeneous_plasticity: BATCH=64, LR=0.5, sparse-bipolar f=0.05

GPU required: torch.cuda for matmul-heavy W-building at N_DIM=8192.
Falls back to CPU-torch if no CUDA (keeps functional correctness).
Route to overnight_queue (Fix #22: N_DIM=8192 matmul-dominant).

C7 META atom compliance: LAMBDA_GRID excludes 0.0 as a sweep option.
  (lambda=0.0 => pure unigram; collapses to CALIBRATION_GRID_TOO_COARSE pathology)
  If best_lambda equals the minimum of the grid, flag LAMBDA_ZERO_COLLAPSE.

ASCII-only. Per-seed checkpoint via _seed_checkpoint.

Cites:
  preregs/2026-06-23_substrate_cfrpe_n_steps_curve_v1.md
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py
  data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json
  data/exp_substrate_meta_lr_dopamine_analog_v1/metrics.json
  notes/skunkworks_to_all_BATCH_VET_4_recent_negatives_2026-06-23.md (C7 proposal)
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
    get_output_dir, write_partial, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_cfrpe_n_steps_curve_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Pre-reg thresholds (registered before run per role contract)
HARD_PASS_NEW_ANCHOR_LIFT = 0.25    # cf-RPE@max_steps lift over Hebbian >= +0.25
CHAIN_GRADE_BONUS_LIFT = 0.30       # lift >= +0.30 => updates chain-grade anchor
ASYMPTOTE_CONVERGED_DELTA = 0.02    # |lift@max - lift@2nd_max| <= 0.02
ASYMPTOTE_OPEN_DELTA = 0.03         # lift@max - lift@2nd_max >= +0.03
HARD_FAIL_NO_PROGRESS_DELTA = 0.02  # lift@max_steps <= lift@min_steps + 0.02 => HARD_FAIL

# Sanity: Hebbian baseline BPC from fair_harness chain-grade
HEBBIAN_BASELINE_BPC_REF = 7.3065
HEBBIAN_BASELINE_BPC_TOL = 0.05     # within +/- 0.05 of ref (full mode only)

HP_BPC_CV_MAX = 0.05                # cv across seeds mandatory

# Plasticity knobs: EXACT from heterogeneous_plasticity (CFRPE_ONLY arm)
CFRPE_LR = 0.5
INGEST_BATCH = 64
SPARSE_BIPOLAR_F = 0.05

# Inference
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
# C7: LAMBDA_GRID excludes 0.0 (avoids calibration-collapse-to-unigram pathology)
LAMBDA_GRID = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# N_STEPS sweep (production)
N_STEPS_GRID_FULL = [500, 1000, 1500, 2000, 3000, 5000]

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = (
    "smoke"
    if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
    else os.environ.get("HDLAB_RUN_MODE", "full")
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Production config
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

UNIGRAM_BPC_REF = 7.738

# Gensim cache (process-local)
_GENSIM_KV_CACHE: Dict[str, object] = {}

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS_GRID = N_STEPS_GRID_FULL
else:
    # Smoke: exercises all N_STEPS sweep logic + both arm types + verdict
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    N_STEPS_GRID = [50, 100, 200]   # smoke-scale


# ============================================================================
# Char-trigram encoder (OOV fallback + smoke encoder)
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
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.clip(norms, eps, None)


def _l2_normalize_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    if X.dim() == 1:
        return X / (X.norm() + eps)
    return X / (X.norm(dim=1, keepdim=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


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


def build_E_word2vec_gpu(vocab: List[str], n_dim: int, seed: int
                          ) -> Tuple[torch.Tensor, Dict]:
    """Build [V, n_dim] L2-normalized word2vec-projected vectors on DEVICE.

    OOV words fall back to char-trigram encoding.
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
    E_proj = _l2_normalize_np(E_proj)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_t, meta


def build_E_char_trigram_gpu(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    """Smoke / fallback when gensim unavailable."""
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


def sparsify_bipolar_gpu(E: torch.Tensor, f: float, seed: int) -> torch.Tensor:
    """Sparse-bipolar: keep top-k by abs magnitude, set sign."""
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
# cf-RPE delta rule (torch, GPU/CPU)
# EXACT from heterogeneous_plasticity ARM_CFRPE_ONLY (lines 322-326)
# ============================================================================

def build_W_cfrpe_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                       n_steps: int, batch: int, lr: float,
                       gen: torch.Generator) -> torch.Tensor:
    """Build W via cf-RPE delta rule (torch, GPU/CPU).

    delta_W = (E[t+1] - E[t] @ W^T)^T @ E[t] / batch
    W_{t+1} = W_t + lr * delta_W

    EXACT rule from heterogeneous_plasticity ARM_CFRPE_ONLY.
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W

    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train_t[st]]          # [batch, dim]
        Nxt = E[idx_train_t[st + 1]]      # [batch, dim]
        error = Nxt - Ctx @ W.t()         # [batch, dim]
        dW = (error.t() @ Ctx) / batch    # [dim, dim]
        W = W + lr * dW

    return W


def build_W_hebbian_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                         ingest_chunk: int) -> torch.Tensor:
    """One-pass batched outer-product Hebbian W (same as fair_harness rank-1 build).

    Matches ARM_HEBBIAN_ONLY from heterogeneous_plasticity (lines 303-314).
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W

    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train_t[b:end]
        tgt_idx = idx_train_t[b + 1:end + 1]
        E_src = E[src_idx]
        E_tgt = E[tgt_idx]
        W.add_(E_tgt.T @ E_src)
        if DEVICE.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()

    return W


# ============================================================================
# Recall + eval pipeline
# ============================================================================

def compute_logits_gpu(E: torch.Tensor, W: torch.Tensor, idx_held_t: torch.Tensor,
                        recall_batch: int) -> np.ndarray:
    """Compute [n_held, V] cosine similarity logits, return as numpy."""
    n_h = idx_held_t.shape[0]
    V = E.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx = E[idx_held_t[b:end]]
        pred = _l2_normalize_t(ctx @ W.t())
        logits[b:end] = pred @ E.T
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    return logits.detach().cpu().numpy().astype(np.float32)


def _raw_bpc_at_T1(logits: np.ndarray, idx_held: np.ndarray) -> float:
    """BPC at T=1, for DEGEN sanity gate."""
    n_h = logits.shape[0]
    nxt_np = idx_held[1:] if len(idx_held) > 1 else idx_held
    n_eval = min(n_h, len(nxt_np))
    if n_eval == 0:
        return float("inf")
    z = logits[:n_eval] - logits[:n_eval].max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / np.clip(e.sum(axis=1, keepdims=True), 1e-30, None)
    p_nxt = p[np.arange(n_eval), nxt_np[:n_eval]].clip(1e-12, 1.0)
    return float(-np.mean(np.log(p_nxt)) / math.log(2.0))


# ============================================================================
# text8 corpus + vocab utilities
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
# Joint (T, lambda) sweep + 3 metrics
# C7: LAMBDA_GRID excludes 0.0; post-hoc LAMBDA_ZERO_COLLAPSE flag
# ============================================================================

def softmax_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    return -float(np.mean(logp[np.arange(n), nxt])) / math.log(2.0)


def top1_acc(logp: np.ndarray, nxt: np.ndarray) -> float:
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
                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                temp_grid: list, lambda_grid: list, mrr_k: int) -> Dict:
    """Joint (T, lambda) sweep on dev; pick best; report on test.

    C7: lambda_grid must NOT include 0.0. Post-hoc check: if best_lambda is
    the minimum value in lambda_grid, flag LAMBDA_ZERO_COLLAPSE warning.
    """
    # Raw BPC at T=1, lambda=1 (pure substrate, no unigram blend)
    probs_T1 = softmax_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)

    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}

    for T in temp_grid:
        probs_dev = softmax_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in lambda_grid:
            logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
            if bd < best_bpc["dev_value"]:
                best_bpc = {"T": float(T), "lambda": float(lam), "dev_value": bd}
            if td > best_top1["dev_value"]:
                best_top1 = {"T": float(T), "lambda": float(lam), "dev_value": td}
            if md > best_mrr["dev_value"]:
                best_mrr = {"T": float(T), "lambda": float(lam), "dev_value": md}

    def _eval_test(T: float, lam: float, fn) -> float:
        probs = softmax_with_T(sub_logits_test, T)
        logp_sub = np.log(np.clip(probs, 1e-30, 1.0))
        logp = log_linear_interp(logp_sub, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _eval_test(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _eval_test(best_top1["T"], best_top1["lambda"], top1_acc)
    mrr_best_test = _eval_test(best_mrr["T"], best_mrr["lambda"],
                                lambda lp, nx: mrr_at_k(lp, nx, mrr_k))

    # C7 LAMBDA_ZERO_COLLAPSE detection: flag if best_lambda is at grid minimum
    lambda_min = min(lambda_grid) if lambda_grid else 0.0
    lambda_zero_collapse = bool(
        abs(best_bpc["lambda"] - lambda_min) < 1e-6 and
        math.isfinite(bpc_best_test) and
        bpc_best_test > 7.5  # near-unigram territory (unigram ~ 7.74)
    )

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
        "lambda_zero_collapse": lambda_zero_collapse,
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray,
                     V: int, mrr_k: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != 0)
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
# Instrumentation self-test (MANDATORY per role contract)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    _dev = DEVICE

    # ST1: cf-RPE error shrinks after 1 step (torch)
    n_dim_st = 64
    gen_st = torch.Generator(device=_dev)
    gen_st.manual_seed(42)
    Ctx1 = torch.randn(1, n_dim_st, device=_dev)
    Nxt1 = torch.randn(1, n_dim_st, device=_dev)
    Ctx1 = Ctx1 / (Ctx1.norm() + 1e-8)
    Nxt1 = Nxt1 / (Nxt1.norm() + 1e-8)
    W1 = torch.zeros(n_dim_st, n_dim_st, device=_dev)
    error_before = float((Nxt1 - Ctx1 @ W1.t()).norm())
    dW1 = (Nxt1 - Ctx1 @ W1.t()).t() @ Ctx1
    W1 = W1 + 0.9 * dW1
    error_after = float((Nxt1 - Ctx1 @ W1.t()).norm())
    assert error_after < error_before, (
        "ST1 cf-RPE should shrink error: before=%.4f after=%.4f" % (error_before, error_after))
    print("[selftest] ST1 cf-RPE shrinks error: %.4f -> %.4f" % (error_before, error_after), flush=True)

    # ST2: build_W_cfrpe_gpu returns non-zero W after N_STEPS=10
    n_v_st = 8
    E_st = torch.randn(n_v_st, n_dim_st, device=_dev)
    E_st = _l2_normalize_t(E_st)
    idx_st = torch.randint(0, n_v_st, (21,), device=_dev)
    gen_st2 = torch.Generator(device=_dev)
    gen_st2.manual_seed(7)
    W2 = build_W_cfrpe_gpu(E_st, idx_st, n_steps=10, batch=4, lr=0.5, gen=gen_st2)
    assert W2 is not None, "ST2 build_W_cfrpe_gpu returned None"
    assert float(W2.norm()) > 1e-6, "ST2 W from cf-RPE is all-zero after 10 steps"
    print("[selftest] ST2 build_W_cfrpe_gpu non-zero W (norm=%.4f)" % float(W2.norm()), flush=True)

    # ST3: build_W_hebbian_gpu returns non-zero W
    W3 = build_W_hebbian_gpu(E_st, idx_st, ingest_chunk=10)
    assert W3 is not None, "ST3 build_W_hebbian_gpu returned None"
    assert float(W3.norm()) > 1e-6, "ST3 Hebbian W is all-zero"
    print("[selftest] ST3 build_W_hebbian_gpu non-zero W (norm=%.4f)" % float(W3.norm()), flush=True)

    # ST4: cf-RPE W differs from Hebbian W
    diff_cf_heb = float((W2 - W3).norm())
    assert diff_cf_heb > 1e-6, "ST4 cf-RPE and Hebbian W should differ: diff=%.2e" % diff_cf_heb
    print("[selftest] ST4 cf-RPE != Hebbian W (diff=%.4f)" % diff_cf_heb, flush=True)

    # ST5: compute_logits_gpu returns [n_held, V] shaped array with finite values
    n_held_st = 10
    idx_held_st = torch.randint(0, n_v_st, (n_held_st,), device=_dev)
    logits5 = compute_logits_gpu(E_st, W2, idx_held_st, recall_batch=5)
    assert logits5.shape == (n_held_st, n_v_st), (
        "ST5 logits shape mismatch: %s vs (%d, %d)" % (logits5.shape, n_held_st, n_v_st))
    assert np.all(np.isfinite(logits5)), "ST5 logits contain non-finite values"
    print("[selftest] ST5 compute_logits_gpu shape=%s finite=True" % str(logits5.shape), flush=True)

    # ST6: sparsify_bipolar_gpu produces sparse +/-1 vectors
    E_dense = torch.randn(4, 32, device=_dev)
    E_sparse = sparsify_bipolar_gpu(E_dense, f=0.25, seed=0)
    n_nonzero = int((E_sparse != 0).sum())
    expected_k = max(1, int(round(0.25 * 32)))
    assert n_nonzero == 4 * expected_k, (
        "ST6 sparsify_bipolar_gpu: expected %d nonzero, got %d" % (4 * expected_k, n_nonzero))
    print("[selftest] ST6 sparsify_bipolar_gpu OK (k=%d nonzero per row)" % expected_k, flush=True)

    # ST7: joint_sweep returns finite BPC + C7 assertion (0.0 not in LAMBDA_GRID)
    n_tok_st = 30
    n_v_sm = 6
    rng_jt = np.random.default_rng(99)
    logits_st = rng_jt.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_st = rng_jt.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_st = np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32)
    U_log_st = np.log(U_st)
    nd = n_tok_st // 2
    assert 0.0 not in LAMBDA_GRID, "ST7 C7 violation: 0.0 found in LAMBDA_GRID"
    jr = joint_sweep(logits_st[:nd], logits_st[nd:], U_log_st, nxt_st[:nd], nxt_st[nd:],
                      TEMP_GRID, LAMBDA_GRID, MRR_K)
    assert math.isfinite(jr["bpc_best"]), "ST7 joint_sweep bpc_best not finite: %s" % jr["bpc_best"]
    assert math.isfinite(jr["top1_acc"]), "ST7 joint_sweep top1_acc not finite"
    assert math.isfinite(jr["mrr_at_10"]), "ST7 joint_sweep mrr_at_10 not finite"
    assert jr["n_dev"] > 0, "ST7 n_dev == 0"
    assert jr["n_test"] > 0, "ST7 n_test == 0"
    print("[selftest] ST7 joint_sweep OK (bpc=%.3f top1=%.4f C7_ok=True)" % (
        jr["bpc_best"], jr["top1_acc"]), flush=True)

    # ST8: N_STEPS_GRID has >= 2 values (needed for monotonicity check)
    assert len(N_STEPS_GRID) >= 2, "ST8 N_STEPS_GRID must have >= 2 values: got %s" % N_STEPS_GRID
    print("[selftest] ST8 N_STEPS_GRID len=%d OK" % len(N_STEPS_GRID), flush=True)

    # ST9: monotone lifts would pass (synthetic: cf-RPE beats Hebbian at small scale)
    # Quick sanity: W from 50 cf-RPE steps has lower BPC proxy than Hebbian W
    # on random sequences at tiny scale -- just asserts functions callable w/o error
    n_v_sm2 = 6
    E_sm = torch.randn(n_v_sm2, n_dim_st, device=_dev)
    E_sm = _l2_normalize_t(E_sm)
    idx_sm = torch.randint(0, n_v_sm2, (51,), device=_dev)
    gen_sm = torch.Generator(device=_dev)
    gen_sm.manual_seed(13)
    W_cf_sm = build_W_cfrpe_gpu(E_sm, idx_sm, n_steps=5, batch=4, lr=0.5, gen=gen_sm)
    W_hb_sm = build_W_hebbian_gpu(E_sm, idx_sm, ingest_chunk=50)
    idx_eval_sm = torch.randint(0, n_v_sm2, (10,), device=_dev)
    logits_cf = compute_logits_gpu(E_sm, W_cf_sm, idx_eval_sm, recall_batch=5)
    logits_hb = compute_logits_gpu(E_sm, W_hb_sm, idx_eval_sm, recall_batch=5)
    assert logits_cf.shape == logits_hb.shape == (10, n_v_sm2), (
        "ST9 logits shape mismatch: cf=%s hb=%s" % (logits_cf.shape, logits_hb.shape))
    print("[selftest] ST9 cf-RPE vs Hebbian eval shapes OK", flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict:
    """Run full N_STEPS sweep for one seed.

    Returns dict with:
      - "ARM_UNIGRAM": unigram baseline
      - "ARM_HEBBIAN_BASELINE": Hebbian arm result (single W, evaluated once)
      - "N<n>_cfrpe": cf-RPE arm at N_STEPS=n for each n in N_STEPS_GRID
    """
    t_seed = time.time()
    print("\n[seed=%d] loading text8 + building vocab" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[WARN] corpus short: %d tokens loaded" % len(toks), flush=True)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s mode=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE), RUN_MODE), flush=True)
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
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # Hoist encoder outside arm loop (Fix #24: encoder loaded once, reused per arm)
    print("\n[seed=%d] building encoder (V=%d N_DIM=%d) on %s..." % (
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
    else:
        print("[seed=%d encoder] E built (%.1fs)" % (seed, t_enc), flush=True)

    # Apply sparse-bipolar transform (same as fair_harness)
    E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, f=SPARSE_BIPOLAR_F, seed=seed))
    del E_base
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    # Build eval split: dev + test halves
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    valid_held_pos = np.where(mask)[0]
    n_eval = len(nxt_eval)

    if n_eval == 0:
        del E_used
        return {"seed": seed, "by_arm": by_arm, "V": V, "N_DIM": N_DIM,
                "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2),
                "device": str(DEVICE), "encoder_meta": encoder_meta}

    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    def _eval_W_on_arm(arm_name: str, W: torch.Tensor, t_arm0: float) -> None:
        """Compute logits + joint sweep + store into by_arm."""
        logits = compute_logits_gpu(E_used, W, idx_held_t, RECALL_BATCH)
        raw_bpc = _raw_bpc_at_T1(logits, idx_held)

        # Align to ctx_full domain
        if logits.shape[0] >= len(ctx_full):
            logits_ctx = logits[:len(ctx_full)]
        else:
            logits_ctx = logits
            mask_pos = np.array([p for p in valid_held_pos if p < logits_ctx.shape[0]],
                                  dtype=np.int64)
            logits_eval = logits_ctx[mask_pos]
            nxt_eval_local = nxt_full[mask_pos]
            ne = len(nxt_eval_local)
            ndev = ne // 2
            jr = joint_sweep(
                logits_eval[:ndev], logits_eval[ndev:], U_log,
                nxt_eval_local[:ndev], nxt_eval_local[ndev:],
                TEMP_GRID, LAMBDA_GRID, MRR_K,
            )
            jr["raw_bpc_at_T1_L1"] = round(raw_bpc, 4)
            jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
            by_arm[arm_name] = jr
            print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f (bestT=%.4f bestL=%.2f) "
                  "raw_T1L1_bpc=%.3f lzc=%s" % (
                      seed, arm_name, jr["bpc_best"], jr["top1_acc"],
                      jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                      jr["raw_bpc_at_T1_L1"], jr.get("lambda_zero_collapse", False)), flush=True)
            return

        logits_eval = logits_ctx[mask]
        jr = joint_sweep(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["raw_bpc_at_T1_L1"] = round(raw_bpc, 4)
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        by_arm[arm_name] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f (bestT=%.4f bestL=%.2f) "
              "raw_T1L1_bpc=%.3f lzc=%s" % (
                  seed, arm_name, jr["bpc_best"], jr["top1_acc"],
                  jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                  jr["raw_bpc_at_T1_L1"], jr.get("lambda_zero_collapse", False)), flush=True)

    # ARM_HEBBIAN_BASELINE: one-pass rank-1 Hebbian
    t_heb = time.time()
    print("\n  [seed=%d arm=ARM_HEBBIAN_BASELINE] building W..." % seed, flush=True)
    try:
        W_heb = build_W_hebbian_gpu(E_used, idx_train_t, ingest_chunk=INGEST_CHUNK)
        _eval_W_on_arm("ARM_HEBBIAN_BASELINE", W_heb, t_heb)
        del W_heb
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=ARM_HEBBIAN_BASELINE] COMPUTE FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_HEBBIAN_BASELINE"] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
            "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "elapsed_s_arm": round(time.time() - t_heb, 2),
        }

    # cf-RPE arms: sweep N_STEPS_GRID
    for n_steps in N_STEPS_GRID:
        arm_name = "N%d_cfrpe" % n_steps
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building W (n_steps=%d)..." % (seed, arm_name, n_steps), flush=True)
        # Per-arm seed for reproducibility (same convention as prior cells)
        arm_seed = seed * 10007 + n_steps * 31337
        gen = torch.Generator(device=DEVICE)
        gen.manual_seed(arm_seed)
        try:
            W_cf = build_W_cfrpe_gpu(E_used, idx_train_t, n_steps=n_steps,
                                      batch=INGEST_BATCH, lr=CFRPE_LR, gen=gen)
            _eval_W_on_arm(arm_name, W_cf, t_arm0)
            del W_cf
            if DEVICE.type == "cuda":
                torch.cuda.empty_cache()
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm_name, err), flush=True)
            by_arm[arm_name] = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
                "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
            }

    del E_used
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "N_STEPS_GRID": N_STEPS_GRID,
        "run_mode": RUN_MODE,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
    }


# ============================================================================
# Verdict (per pre-reg bands; Fix #28 per-arm metrics only)
# ============================================================================

def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    vocab_entropy = math.log2(max(units[0].get("V", 4000), 2))

    # Aggregate per-arm across seeds
    by_arm_agg: Dict[str, Dict] = {}

    # ARM_UNIGRAM aggregation
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
    }
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    def _agg_arm(arm: str) -> Dict:
        seeds_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid = [(not cf) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
                 for cf, u in zip(seeds_failed, units)]
        n_failed = int(sum(seeds_failed))
        valid_units = [u for ok, u in zip(valid, units) if ok]
        if not valid_units:
            return {
                "bpc_best_mean": float("inf"), "top1_acc_mean": float("nan"),
                "mrr_at_10_mean": float("nan"), "raw_bpc_at_T1_L1_mean": float("nan"),
                "n_valid_seeds": 0, "n_compute_failed": n_failed, "all_seeds_failed": True,
            }
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_v = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid_units]
        raw_v_finite = [x for x in raw_v if math.isfinite(x)]
        lzc_any = any(u["by_arm"][arm].get("lambda_zero_collapse", False) for u in valid_units)
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        return {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "top1_acc_std": round(float(np.std(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
            "raw_bpc_at_T1_L1_mean": (round(float(np.mean(raw_v_finite)), 4)
                                        if raw_v_finite else float("nan")),
            "lambda_zero_collapse_any_seed": bool(lzc_any),
            "n_valid_seeds": int(len(valid_units)),
            "n_compute_failed": n_failed,
            "all_seeds_failed": False,
        }

    by_arm_agg["ARM_HEBBIAN_BASELINE"] = _agg_arm("ARM_HEBBIAN_BASELINE")
    for n_steps in N_STEPS_GRID:
        arm = "N%d_cfrpe" % n_steps
        by_arm_agg[arm] = _agg_arm(arm)

    # Hebbian baseline BPC
    heb_bpc = by_arm_agg["ARM_HEBBIAN_BASELINE"].get("bpc_best_mean", float("inf"))
    heb_failed = by_arm_agg["ARM_HEBBIAN_BASELINE"].get("all_seeds_failed", True)

    # Sanity check: Hebbian ~ 7.3065 +/- 0.05 (full mode only; smoke uses smaller N_DIM/V)
    hebbian_sanity_ok = (
        math.isfinite(heb_bpc) and
        abs(heb_bpc - HEBBIAN_BASELINE_BPC_REF) <= HEBBIAN_BASELINE_BPC_TOL
    )

    # Per-N_STEPS lift values (positive = cf-RPE better than Hebbian)
    lifts: Dict[int, float] = {}
    for n_steps in N_STEPS_GRID:
        arm = "N%d_cfrpe" % n_steps
        cfrpe_bpc = by_arm_agg[arm].get("bpc_best_mean", float("inf"))
        if math.isfinite(heb_bpc) and math.isfinite(cfrpe_bpc):
            lifts[n_steps] = round(heb_bpc - cfrpe_bpc, 4)
        else:
            lifts[n_steps] = float("nan")

    # Primary arms: max and min in N_STEPS_GRID
    _max_steps = max(N_STEPS_GRID)
    _min_steps = min(N_STEPS_GRID)
    lift_at_max = lifts.get(_max_steps, float("nan"))
    lift_at_min = lifts.get(_min_steps, float("nan"))

    # cv of highest N_STEPS arm
    max_arm = "N%d_cfrpe" % _max_steps
    max_arm_cv = by_arm_agg[max_arm].get("bpc_best_cv", float("nan"))
    max_arm_failed = by_arm_agg[max_arm].get("all_seeds_failed", True)

    # Monotonicity check: lifts should be non-decreasing over N_STEPS_GRID
    valid_lifts = [(n, lifts[n]) for n in N_STEPS_GRID if math.isfinite(lifts.get(n, float("nan")))]
    is_monotone = True
    if len(valid_lifts) >= 2:
        for i in range(len(valid_lifts) - 1):
            if valid_lifts[i + 1][1] < valid_lifts[i][1] - 0.01:  # allow small noise
                is_monotone = False
                break

    # Summary line for all N_STEPS arms
    arms_summary_parts = ["ARM_HEBBIAN_BASELINE=bpc%.4f" % heb_bpc]
    for n_steps in N_STEPS_GRID:
        arm = "N%d_cfrpe" % n_steps
        bpc_v = by_arm_agg[arm].get("bpc_best_mean", float("inf"))
        lift_v = lifts.get(n_steps, float("nan"))
        arms_summary_parts.append("N%d_cfrpe=bpc%.4f(lift%.4f)" % (n_steps, bpc_v, lift_v))
    arms_summary = " | ".join(arms_summary_parts)

    detail = {
        "by_arm_agg": by_arm_agg,
        "lifts_per_n_steps": {str(k): v for k, v in lifts.items()},
        "lift_at_max_steps": round(lift_at_max, 4) if math.isfinite(lift_at_max) else None,
        "lift_at_min_steps": round(lift_at_min, 4) if math.isfinite(lift_at_min) else None,
        "hebbian_bpc": round(heb_bpc, 4) if math.isfinite(heb_bpc) else None,
        "unigram_bpc": round(unigram_bpc, 4),
        "is_monotone_lifts": bool(is_monotone),
        "max_n_steps_cv": round(max_arm_cv, 4) if math.isfinite(max_arm_cv) else None,
        "n_seeds": len(units),
        "n_steps_grid": N_STEPS_GRID,
        "hebbian_baseline_bpc_ref": HEBBIAN_BASELINE_BPC_REF,
        "hebbian_sanity_ok": bool(hebbian_sanity_ok),
        "hard_pass_new_anchor_lift_bar": HARD_PASS_NEW_ANCHOR_LIFT,
        "chain_grade_bonus_lift_bar": CHAIN_GRADE_BONUS_LIFT,
        "asymptote_converged_delta": ASYMPTOTE_CONVERGED_DELTA,
        "asymptote_open_delta": ASYMPTOTE_OPEN_DELTA,
        "hard_fail_no_progress_delta": HARD_FAIL_NO_PROGRESS_DELTA,
        "honest_scope": (
            "cf-RPE N_STEPS convergence curve at production scale "
            "(N_DIM=8192 N_TRAIN=100k text8 V=4000). "
            "Tests cf-RPE delta-rule BPC as function of N_STEPS grid %s. "
            "HARD_PASS = cf-RPE@%d lift over Hebbian >= %.2f bits. "
            "CHAIN_GRADE_BONUS = lift >= %.2f bits. "
            "HARD_FAIL = no monotonic increase OR lift@%d <= lift@%d + %.2f. "
            "ARM_HEBBIAN_BASELINE sanity: %.4f +/- %.2f (full only). cv < %.2f for max arm. "
            "C7 LAMBDA_GRID excludes 0.0 (anti-calibration-collapse). "
            "WHAT_THIS_DOES_NOT_SHOW: does not test STDP composition, "
            "generalization beyond text8, or encoder sensitivity." % (
                N_STEPS_GRID, _max_steps,
                HARD_PASS_NEW_ANCHOR_LIFT, CHAIN_GRADE_BONUS_LIFT,
                _max_steps, _min_steps, HARD_FAIL_NO_PROGRESS_DELTA,
                HEBBIAN_BASELINE_BPC_REF, HEBBIAN_BASELINE_BPC_TOL, HP_BPC_CV_MAX)),
        "cites": [
            "preregs/2026-06-23_substrate_cfrpe_n_steps_curve_v1.md",
            "experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py",
            "data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json",
            "data/exp_substrate_meta_lr_dopamine_analog_v1/metrics.json",
            "notes/skunkworks_to_all_BATCH_VET_4_recent_negatives_2026-06-23.md",
        ],
    }

    # Gate 1: Hebbian arm failed entirely
    if heb_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_HEBBIAN_BASELINE all seeds failed. Cannot compute lifts. %s" % arms_summary,
                detail)

    # Gate 2: max-N_STEPS arm failed entirely
    if max_arm_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: N%d_cfrpe all seeds failed. %s" % (_max_steps, arms_summary),
                detail)

    # Gate 3: Hebbian sanity check (full mode only)
    if RUN_MODE == "full" and not hebbian_sanity_ok and math.isfinite(heb_bpc):
        return ("HARD_FAIL",
                ("HARD_FAIL: ARM_HEBBIAN_BASELINE bpc=%.4f deviates from ref %.4f by > %.2f bits. "
                 "Methodology issue (encoder mismatch?). %s" % (
                     heb_bpc, HEBBIAN_BASELINE_BPC_REF, HEBBIAN_BASELINE_BPC_TOL, arms_summary)),
                detail)

    # Gate 4: cv gate for max-N_STEPS arm
    if math.isfinite(max_arm_cv) and max_arm_cv > HP_BPC_CV_MAX:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_HIGH_CV: N%d_cfrpe cv=%.3f > %.2f. "
                 "High variance across seeds at max N_STEPS. lift=%.4f. %s" % (
                     _max_steps, max_arm_cv, HP_BPC_CV_MAX, lift_at_max, arms_summary)),
                detail)

    # Gate 5: HARD_FAIL -- no progress (lift@max_steps <= lift@min_steps + epsilon)
    if math.isfinite(lift_at_max) and math.isfinite(lift_at_min):
        if lift_at_max <= lift_at_min + HARD_FAIL_NO_PROGRESS_DELTA:
            return ("HARD_FAIL",
                    ("HARD_FAIL: no meaningful progress. "
                     "lift@%d=%.4f lift@%d=%.4f (delta=%.4f <= %.2f). "
                     "cf-RPE converges early; extra steps not helpful. "
                     "monotone=%s. %s" % (
                         _min_steps, lift_at_min, _max_steps, lift_at_max,
                         lift_at_max - lift_at_min, HARD_FAIL_NO_PROGRESS_DELTA,
                         is_monotone, arms_summary)),
                    detail)

    # Gate 6: HARD_FAIL -- no monotone increase (non-monotone lifts)
    if not is_monotone:
        return ("HARD_FAIL",
                ("HARD_FAIL: lift values NOT monotonically increasing over N_STEPS grid. "
                 "lifts=%s. cf-RPE may be unstable with training steps at this scale. %s" % (
                     {k: lifts[k] for k in N_STEPS_GRID}, arms_summary)),
                detail)

    # Asymptote classification (uses two highest N_STEPS values in grid)
    asymptote_msg = ""
    _sorted_n = sorted(N_STEPS_GRID)
    if len(_sorted_n) >= 2:
        _n_hi = _sorted_n[-1]
        _n_lo = _sorted_n[-2]
        _lift_hi = lifts.get(_n_hi, float("nan"))
        _lift_lo = lifts.get(_n_lo, float("nan"))
        if math.isfinite(_lift_hi) and math.isfinite(_lift_lo):
            delta_hi_lo = _lift_hi - _lift_lo
            if delta_hi_lo >= ASYMPTOTE_OPEN_DELTA:
                asymptote_msg = ("ASYMPTOTE_OPEN: lift@%d-lift@%d=%.4f >= %.2f "
                                 "(needs bigger sweep)" % (
                                     _n_hi, _n_lo, delta_hi_lo, ASYMPTOTE_OPEN_DELTA))
            elif abs(delta_hi_lo) <= ASYMPTOTE_CONVERGED_DELTA:
                asymptote_msg = ("ASYMPTOTE_CONVERGED: lift@%d-lift@%d=%.4f within +/-%.2f" % (
                    _n_hi, _n_lo, delta_hi_lo, ASYMPTOTE_CONVERGED_DELTA))
            else:
                asymptote_msg = ("ASYMPTOTE_PARTIAL: lift@%d-lift@%d=%.4f" % (
                    _n_hi, _n_lo, delta_hi_lo))
    detail["asymptote_msg"] = asymptote_msg

    # Primary verdict: based on lift@max_n_steps vs Hebbian
    if not math.isfinite(lift_at_max):
        return ("HARD_FAIL",
                ("HARD_FAIL: lift at N_STEPS=%d is not finite (arm failed or missing). %s" % (
                    _max_steps, arms_summary)),
                detail)

    if lift_at_max >= CHAIN_GRADE_BONUS_LIFT:
        detail["chain_grade_bonus"] = True
        return ("HARD_PASS",
                ("HARD_PASS CHAIN_GRADE_BONUS: cf-RPE@N_STEPS=%d lift=%.4f >= %.2f bits over Hebbian. "
                 "%s. %s. hebbian_sanity=%s" % (
                     _max_steps, lift_at_max, CHAIN_GRADE_BONUS_LIFT,
                     asymptote_msg, arms_summary, hebbian_sanity_ok)),
                detail)
    elif lift_at_max >= HARD_PASS_NEW_ANCHOR_LIFT:
        detail["chain_grade_bonus"] = False
        return ("HARD_PASS",
                ("HARD_PASS: cf-RPE@N_STEPS=%d lift=%.4f >= %.2f bits over Hebbian. "
                 "%s. %s. hebbian_sanity=%s" % (
                     _max_steps, lift_at_max, HARD_PASS_NEW_ANCHOR_LIFT,
                     asymptote_msg, arms_summary, hebbian_sanity_ok)),
                detail)
    else:
        # Lift is positive but below HARD_PASS_NEW_ANCHOR bar
        detail["chain_grade_bonus"] = False
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND: cf-RPE@N_STEPS=%d lift=%.4f in (%.2f, %.2f). "
                 "cf-RPE converges but below new-anchor bar. %s. %s. hebbian_sanity=%s" % (
                     _max_steps, lift_at_max, HARD_FAIL_NO_PROGRESS_DELTA,
                     HARD_PASS_NEW_ANCHOR_LIFT, asymptote_msg, arms_summary,
                     hebbian_sanity_ok)),
                detail)


# ============================================================================
# Main loop with per-seed checkpoint
# ============================================================================

print("[config] anchor=%s N_DIM=%d mode=%s seeds=%s N_STEPS_GRID=%s device=%s" % (
    ANCHOR_NAME, N_DIM, RUN_MODE, SEEDS, N_STEPS_GRID, str(DEVICE)), flush=True)

if DEVICE.type == "cuda":
    print("[gpu] %s" % torch.cuda.get_device_name(0), flush=True)
else:
    print("[device] CPU (no CUDA available)", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)

from experiments._seed_checkpoint import resumable_seeds as _resumable_seeds
try:
    done_seeds, remaining_seeds = _resumable_seeds(SEEDS, out_dir)
    print("[ckpt] %d done, %d remaining: %s" % (len(done_seeds), len(remaining_seeds),
                                                  remaining_seeds), flush=True)
except Exception as e:
    print("[ckpt] resumable_seeds failed (%s); running all seeds" % e, flush=True)
    remaining_seeds = SEEDS[:]

for seed in remaining_seeds:
    print("\n[run] seed=%d starting..." % seed, flush=True)
    result = run_unit(seed)
    write_partial(out_dir, seed, result)
    print("[ckpt] seed=%d partial written" % seed, flush=True)

per_seed = aggregate_partials(out_dir, SEEDS)
all_units = list(per_seed.values())

verdict, verdict_msg, detail = compute_verdict(all_units)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

if DEVICE.type == "cuda":
    peak_gb = torch.cuda.max_memory_allocated(0) / 1e9
    print("[gpu] peak memory %.3f GB" % peak_gb, flush=True)
    if RUN_MODE == "full":
        assert peak_gb > 0.001, "GPU peak memory should be > 0.001 GB (GPU not used?)"

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "SEEDS": SEEDS,
    "N_STEPS_GRID": N_STEPS_GRID,
    "CFRPE_LR": CFRPE_LR,
    "INGEST_BATCH": INGEST_BATCH,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "LAMBDA_GRID": LAMBDA_GRID,
    "detail": detail,
    "per_seed": [
        {"seed": u.get("seed"), "by_arm": u.get("by_arm"),
         "V": u.get("V"), "N_DIM": u.get("N_DIM"), "N_TRAIN": u.get("N_TRAIN"),
         "elapsed_s_seed": u.get("elapsed_s_seed"), "device": u.get("device"),
         "encoder_meta": u.get("encoder_meta", {})}
        for u in all_units
    ],
    "elapsed_s": round(sum(u.get("elapsed_s_seed", 0.0) for u in all_units), 2),
}

write_metrics(out_dir, metrics, all_units)
print("[metrics] written to %s" % out_dir, flush=True)
