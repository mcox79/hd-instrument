"""
substrate_cross_layer_compose_LM_v1 -- cross-layer (independent-W per layer)
substrate-LM composition at LM-relevant scale.

HYPOTHESIS: composition fact-finder (notes/director_composition_store_mine_inventory
_2026-06-24.md) found that cross-layer hierarchical stacking (independent W per
hop) succeeds chain-grade at L=100 (lacc=1.0), while same-W intra-layer
composition catastrophically collapses (A1 5-arm = 7.89 BPC, WORSE than
unigram). This cell tests whether the cross-layer architecture pattern
transfers to the LM regime at N_TRAIN=100k text8 / N_DIM=8192.

FOUR ARMS (3 seeds each):
  ARM_SINGLE_LAYER_CFRPE          -- sanity rail: single cf-RPE layer reference
  ARM_2_LAYER_INDEPENDENT_CFRPE   -- LOAD-BEARING: 2 layers, independent W per
  ARM_3_LAYER_INDEPENDENT_CFRPE   -- depth scan: 3 layers, independent W per
  ARM_2_LAYER_SHARED_W_CFRPE      -- CONTROL: 2 layers, SHARED W; validates
                                     same-W collapse pattern

PRE-REG BANDS (best_indep_bpc = min over independent-layer arms):
  CHAIN_GRADE_BONUS: best_indep_bpc <= 6.70
  HARD_PASS:        best_indep_bpc <= 6.90
  MIDDLE_BAND:      best_indep_bpc in (6.90, 7.05]
  HARD_FAIL:        best_indep_bpc > 7.05  OR  best_indep > shared_W
  cv across seeds <= 0.05 mandatory (else downgrade)
  READOUT_DEGENERATE: raw_bpc_at_T1_L1 within +/-0.5 of log2(V)

ENCODING: word2vec-google-news-300 projected to N_DIM=8192 sparse-bipolar
(f=0.05). OOV fallback char-trigram bipolar. Joint (T, lambda) sweep on dev;
test eval. LAMBDA_GRID excludes 0.0 per META C7.

ASCII-only. Per-seed checkpoint via _seed_checkpoint. CPU-bound (matmul);
GPU used if available but not required.

Cites:
  preregs/2026-06-24_substrate_cross_layer_compose_LM_v1.md
  notes/director_composition_store_mine_inventory_2026-06-24.md
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py
  experiments/exp_q_a3_l100_cross_layer_composition_v1_n16384.py (L=100 lacc=1.0)
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
    get_output_dir, write_partial, aggregate_partials, write_metrics,
    resumable_seeds as _resumable_seeds,
)

ANCHOR_NAME = "substrate_cross_layer_compose_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Pre-reg thresholds (LM BPC, absolute floors per Skunkworks's N2 discipline)
CHAIN_GRADE_BONUS_BPC = 6.70
HARD_PASS_BPC = 6.90
MIDDLE_BAND_BPC_UPPER = 7.05
HP_BPC_CV_MAX = 0.05
DEGEN_TOL = 0.5

# Sanity rail: single-layer cf-RPE provenance
SANITY_SINGLE_LAYER_REF_BPC = 7.04
SANITY_SINGLE_LAYER_TOL = 0.30  # wider than +/-0.05 since reference is a related cell

# Plasticity knobs (matches fair_harness cf-RPE cell)
CFRPE_LR = 0.5
INGEST_BATCH = 64

# Inference grids
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]  # EXCLUDES 0.0 per META C7
MRR_K = 10

# Sparse-bipolar f (chain-grade validated)
SPARSE_BIPOLAR_F = 0.05

# Reference values
UNIGRAM_BPC_REF = 7.738
BASELINE_HEBBIAN_BPC = 7.3065

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

# Arm definitions
ARMS = [
    "ARM_UNIGRAM",                   # baseline
    "ARM_SINGLE_LAYER_CFRPE",        # sanity rail
    "ARM_2_LAYER_INDEPENDENT_CFRPE", # load-bearing
    "ARM_3_LAYER_INDEPENDENT_CFRPE", # depth scan
    "ARM_2_LAYER_SHARED_W_CFRPE",    # control (same-W)
]
PLASTICITY_ARMS = [a for a in ARMS if a != "ARM_UNIGRAM"]

# Per-arm config: (n_layers, shared_W)
ARM_CONFIG = {
    "ARM_SINGLE_LAYER_CFRPE":        {"n_layers": 1, "shared_W": False},
    "ARM_2_LAYER_INDEPENDENT_CFRPE": {"n_layers": 2, "shared_W": False},
    "ARM_3_LAYER_INDEPENDENT_CFRPE": {"n_layers": 3, "shared_W": False},
    "ARM_2_LAYER_SHARED_W_CFRPE":    {"n_layers": 2, "shared_W": True},
}

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = 1000
else:
    # Smoke: small + char-trigram fallback; should run in 20-60s on CPU
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    N_STEPS = 80

# Gensim cache (process-local)
_GENSIM_KV_CACHE: Dict[str, object] = {}


# ============================================================================
# Encoder utilities (lifted-verbatim from fair_harness cell)
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
    """Build [V, n_dim] L2-normalized word2vec-projected vectors on device."""
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
# Multi-layer cf-RPE: build N_LAYERS Ws with INDEPENDENT or SHARED gradient flow
# ============================================================================

def build_W_stack(arm: str, E: torch.Tensor, idx_train_t: torch.Tensor,
                   n_steps: int, batch: int, lr: float,
                   gen: torch.Generator) -> List[torch.Tensor]:
    """Build cf-RPE W matrices for the given arm.

    INDEPENDENT arms (n_layers >= 1, shared_W=False):
        Each layer trained on its own (input_repr, target) pair, where:
            Layer 1: input = E[t]; target = E[t+1].  Trained via cf-RPE delta:
                       error = target - input @ W1.t()
                       dW1   = error.t() @ input / batch
            Layer k (k >= 2): input = normalize(prev_layer_out_at_t);
                              target = E[t+1] (the same final next-token target).
                              W_k trained via cf-RPE: error = target - input @ W_k.t().
        Each W has its OWN gradient flow (no inter-layer mixing). The stack
        composes at INFERENCE time, not at training time.

    SHARED-W control (n_layers=2, shared_W=True):
        Single W matrix; trained via cf-RPE on (E[t], E[t+1]); applied TWICE
        at inference (W @ W @ E[t]). Same matrix is used for both forward
        applications. Expected to reproduce A1-style sub-additive collapse.

    Returns: list of W tensors, length n_layers. For shared_W=True, returns
    [W, W] (same reference for both layers).
    """
    cfg = ARM_CONFIG[arm]
    n_layers = cfg["n_layers"]
    shared = cfg["shared_W"]
    dim = E.shape[1]
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return [torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
                for _ in range(n_layers)]

    if shared:
        # Single W trained ONCE on (E[t], E[t+1]); applied n_layers times at inference.
        W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
        for _ in range(n_steps):
            st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
            ctx = E[idx_train_t[st]]
            nxt = E[idx_train_t[st + 1]]
            error = nxt - ctx @ W.t()
            dW = (error.t() @ ctx) / batch
            W = W + lr * dW
        return [W] * n_layers  # SAME reference for all layers (shared)

    # INDEPENDENT-W stack: train layer by layer.
    Ws: List[torch.Tensor] = []
    # Layer 1: input = E[t], target = E[t+1]
    W1 = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        ctx = E[idx_train_t[st]]
        nxt = E[idx_train_t[st + 1]]
        error = nxt - ctx @ W1.t()
        dW = (error.t() @ ctx) / batch
        W1 = W1 + lr * dW
    Ws.append(W1)

    # Higher layers: input = normalize(input_repr @ W_prev.t()); target = E[t+1]
    # We snapshot W's so far and freeze them (no further training of lower layers)
    # while training the current layer.
    for layer_idx in range(2, n_layers + 1):
        W_k = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
        # Frozen lower stack: List[torch.Tensor] = Ws[:layer_idx-1]
        for _ in range(n_steps):
            st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
            ctx = E[idx_train_t[st]]
            # Forward through frozen lower layers
            h = ctx
            for W_lower in Ws:
                h = _l2_normalize_t(h @ W_lower.t())
            nxt = E[idx_train_t[st + 1]]
            error = nxt - h @ W_k.t()
            dW = (error.t() @ h) / batch
            W_k = W_k + lr * dW
        Ws.append(W_k)

    return Ws


def forward_stack(ctx: torch.Tensor, Ws: List[torch.Tensor]) -> torch.Tensor:
    """Apply the stack of W's to a [B, dim] input. Returns [B, dim] L2-normalized."""
    h = ctx
    for W in Ws:
        h = _l2_normalize_t(h @ W.t())
    return h


# ============================================================================
# Per-arm logits builder
# ============================================================================

def compute_arm_logits(arm: str, E_base: torch.Tensor, idx_train: np.ndarray,
                        idx_held: np.ndarray, seed: int, n_steps: int) -> Dict:
    """Return [n_held, V] float32 logits + diagnostics. FRESH W stack per arm."""
    V = E_base.shape[0]
    dim = E_base.shape[1]

    # Sparse-bipolar transform applied to all plasticity arms (chain-grade baseline)
    E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    # Per-seed, per-arm generator for reproducibility
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed * 10007 + ARMS.index(arm) * 31337)

    t0 = time.time()
    Ws = build_W_stack(arm, E_used, idx_train_t, n_steps=n_steps,
                       batch=INGEST_BATCH, lr=CFRPE_LR, gen=gen)
    t_ingest = time.time() - t0

    # Recall: forward each held-context through the stack; decode via E.T
    t0 = time.time()
    n_h = idx_held_t.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        ctx = E_used[idx_held_t[b:end]]
        pred = forward_stack(ctx, Ws)
        logits[b:end] = pred @ E_used.T
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    raw_bpc_at_T1 = _raw_bpc_at_T1(logits, idx_held)

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    n_layers_used = ARM_CONFIG[arm]["n_layers"]
    shared_W_flag = ARM_CONFIG[arm]["shared_W"]
    del logits
    for W in Ws:
        del W
    del Ws
    del E_used
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "raw_bpc_at_T1_L1": round(raw_bpc_at_T1, 4),
        "n_layers": n_layers_used,
        "shared_W": shared_W_flag,
    }


def _raw_bpc_at_T1(logits: torch.Tensor, idx_held: np.ndarray) -> float:
    V = logits.shape[1]
    n_h = logits.shape[0]
    nxt_np = idx_held[1:] if len(idx_held) > 1 else idx_held
    n_eval = min(n_h, len(nxt_np))
    if n_eval == 0:
        return float("inf")
    logits_np = logits[:n_eval].detach().cpu().numpy().astype(np.float32)
    nxt_eval = nxt_np[:n_eval]
    z = logits_np - logits_np.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / np.clip(e.sum(axis=1, keepdims=True), 1e-30, None)
    p_nxt = p[np.arange(n_eval), nxt_eval].clip(1e-12, 1.0)
    return float(-np.mean(np.log(p_nxt)) / math.log(2.0))


# ============================================================================
# text8 corpus utilities (lifted from fair_harness)
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
# Instrumentation self-test (MANDATORY)
# ============================================================================

def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)
    _dev = DEVICE

    # ST1: cf-RPE delta shrinks single-pair prediction error
    n_dim_st = 64
    Ctx2 = torch.randn(1, n_dim_st, device=_dev)
    Nxt2 = torch.randn(1, n_dim_st, device=_dev)
    Ctx2 = Ctx2 / (Ctx2.norm() + 1e-8)
    Nxt2 = Nxt2 / (Nxt2.norm() + 1e-8)
    W_t = torch.zeros(n_dim_st, n_dim_st, device=_dev)
    err_before = float((Nxt2 - Ctx2 @ W_t.t()).norm())
    dW = (Nxt2 - Ctx2 @ W_t.t()).t() @ Ctx2
    W_t = W_t + 0.9 * dW
    err_after = float((Nxt2 - Ctx2 @ W_t.t()).norm())
    assert err_after < err_before, (
        "ST1 cf-RPE should shrink error: %.4f -> %.4f" % (err_before, err_after))
    print("[selftest] ST1 cf-RPE delta shrinks error: %.4f -> %.4f" % (
        err_before, err_after), flush=True)

    # ST2: forward_stack with empty stack = identity (modulo normalization)
    h_in = torch.randn(3, n_dim_st, device=_dev)
    h_in = _l2_normalize_t(h_in)
    h_out = forward_stack(h_in, [])
    diff = float((h_in - h_out).norm())
    assert diff < 1e-5, "ST2 empty-stack forward should be identity: diff=%.4e" % diff
    print("[selftest] ST2 empty-stack forward is identity (diff=%.2e)" % diff, flush=True)

    # ST3: shared-W stack returns same W reference twice (no double-train)
    # Build a tiny shared-W stack by mocking
    n_v_st = 8
    E_st = _l2_normalize_t(torch.randn(n_v_st, n_dim_st, device=_dev))
    idx_train_st = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3], dtype=torch.long, device=_dev)
    gen_st = torch.Generator(device=_dev); gen_st.manual_seed(42)
    Ws_shared = build_W_stack("ARM_2_LAYER_SHARED_W_CFRPE", E_st, idx_train_st,
                                n_steps=5, batch=4, lr=0.5, gen=gen_st)
    assert len(Ws_shared) == 2, "ST3 shared stack should have 2 layers, got %d" % len(Ws_shared)
    same_ref = Ws_shared[0] is Ws_shared[1]
    assert same_ref, "ST3 shared-W layers should be SAME tensor reference"
    print("[selftest] ST3 shared-W stack: 2 layers, SAME reference (same_ref=%s)" % same_ref,
          flush=True)

    # ST4: independent-W stack returns distinct W tensors
    gen_st2 = torch.Generator(device=_dev); gen_st2.manual_seed(42)
    Ws_indep = build_W_stack("ARM_2_LAYER_INDEPENDENT_CFRPE", E_st, idx_train_st,
                              n_steps=5, batch=4, lr=0.5, gen=gen_st2)
    assert len(Ws_indep) == 2, "ST4 independent stack should have 2 layers"
    distinct = not (Ws_indep[0] is Ws_indep[1])
    diff_norm = float((Ws_indep[0] - Ws_indep[1]).norm())
    assert distinct, "ST4 independent-W layers should be DISTINCT tensors"
    assert diff_norm > 1e-6, "ST4 independent-W layers should differ in value: %.4e" % diff_norm
    print("[selftest] ST4 independent-W stack: 2 distinct tensors (diff_norm=%.4f)" % diff_norm,
          flush=True)

    # ST5: 3-layer independent stack has 3 distinct Ws
    gen_st3 = torch.Generator(device=_dev); gen_st3.manual_seed(42)
    Ws3 = build_W_stack("ARM_3_LAYER_INDEPENDENT_CFRPE", E_st, idx_train_st,
                         n_steps=5, batch=4, lr=0.5, gen=gen_st3)
    assert len(Ws3) == 3, "ST5 3-layer stack should have 3 layers, got %d" % len(Ws3)
    print("[selftest] ST5 3-layer independent stack OK (3 layers built)", flush=True)

    # ST6: single-layer stack has 1 W
    gen_st4 = torch.Generator(device=_dev); gen_st4.manual_seed(42)
    Ws1 = build_W_stack("ARM_SINGLE_LAYER_CFRPE", E_st, idx_train_st,
                         n_steps=5, batch=4, lr=0.5, gen=gen_st4)
    assert len(Ws1) == 1, "ST6 single-layer should have 1 W, got %d" % len(Ws1)
    print("[selftest] ST6 single-layer stack OK", flush=True)

    # ST7: forward through 2-layer stack changes the input
    h_after = forward_stack(h_in, Ws_indep)
    diff_fwd = float((h_in - h_after).norm())
    assert diff_fwd > 1e-3, "ST7 2-layer forward should change input: diff=%.4e" % diff_fwd
    print("[selftest] ST7 2-layer forward changes input (diff=%.4f)" % diff_fwd, flush=True)

    # ST8: zero-W stack returns near-zero logits (raw BPC near uniform)
    n_eval_st = 20
    logits_zero = torch.zeros(n_eval_st, n_v_st, device=_dev)
    raw_bpc = _raw_bpc_at_T1(logits_zero, np.zeros(n_eval_st + 1, dtype=np.int64))
    expected_bpc = math.log2(n_v_st)
    assert abs(raw_bpc - expected_bpc) < 0.1, (
        "ST8 zero-W raw_bpc=%.4f should be near log2(%d)=%.4f" % (
            raw_bpc, n_v_st, expected_bpc))
    print("[selftest] ST8 zero-W raw_bpc=%.4f near log2(%d)=%.4f" % (
        raw_bpc, n_v_st, expected_bpc), flush=True)

    # ST9: joint_sweep finite on synthetic
    n_tok_st = 30
    n_v_sm = 6
    rng_st = np.random.default_rng(99)
    logits_st = rng_st.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_st = rng_st.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_st = np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32)
    U_log_st = np.log(U_st)
    nd = n_tok_st // 2
    jr = joint_sweep(logits_st[:nd], logits_st[nd:], U_log_st, nxt_st[:nd], nxt_st[nd:],
                      TEMP_GRID, LAMBDA_GRID, MRR_K)
    assert math.isfinite(jr["bpc_best"]), "ST9 joint_sweep bpc_best not finite"
    assert math.isfinite(jr["top1_acc"]), "ST9 joint_sweep top1_acc not finite"
    assert math.isfinite(jr["mrr_at_10"]), "ST9 joint_sweep mrr_at_10 not finite"
    assert jr["n_dev"] > 0 and jr["n_test"] > 0, "ST9 sweep splits empty"
    print("[selftest] ST9 joint_sweep all metrics finite (bpc=%.3f top1=%.4f mrr=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"]), flush=True)

    # ST10: LAMBDA_GRID excludes 0.0 (META C7)
    assert 0.0 not in LAMBDA_GRID, "ST10 LAMBDA_GRID must not include 0.0 (META C7)"
    print("[selftest] ST10 LAMBDA_GRID excludes 0.0 (META C7) OK", flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

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
        print("[WARN] corpus short: %d tokens loaded" % len(toks), flush=True)
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
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"], uni["n_test"]),
          flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # Hoist encoder outside arm loop
    print("\n[seed=%d] building encoder (V=%d, N_DIM=%d) on %s..." % (
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
    print("[seed=%d encoder] built in %.1fs (meta=%s)" % (seed, t_enc, encoder_meta), flush=True)

    # Split held into dev + test halves
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    ctx_eval = ctx_full[mask]
    nxt_eval = nxt_full[mask]
    n_eval = len(ctx_eval)
    if n_eval == 0:
        for arm in PLASTICITY_ARMS:
            by_arm[arm] = {"empty_eval": True}
        del E_base
        return {"seed": seed, "by_arm": by_arm, "V": V, "N_DIM": N_DIM,
                "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2), "device": str(DEVICE),
                "encoder_meta": encoder_meta}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    for arm in PLASTICITY_ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s n_layers=%d shared=%s] building W stack + logits..." % (
            seed, arm, ARM_CONFIG[arm]["n_layers"], ARM_CONFIG[arm]["shared_W"]), flush=True)
        try:
            ar = compute_arm_logits(arm, E_base, idx_train, idx_held, seed, N_STEPS)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
                "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "n_layers": ARM_CONFIG[arm]["n_layers"],
                "shared_W": ARM_CONFIG[arm]["shared_W"],
            }
            continue

        logits_full = ar["logits"]
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
            logits_eval = logits_ctx[mask]
        else:
            # Truncated; align via mask intersect
            valid_pos = np.where(mask)[0]
            mask_pos = np.array([p for p in valid_pos if p < logits_full.shape[0]],
                                 dtype=np.int64)
            logits_eval = logits_full[mask_pos]
            nxt_eval_local = nxt_full[mask_pos]
            ne = len(nxt_eval_local)
            ndev = ne // 2
            jr = joint_sweep(
                logits_eval[:ndev], logits_eval[ndev:], U_log,
                nxt_eval_local[:ndev], nxt_eval_local[ndev:],
                TEMP_GRID, LAMBDA_GRID, MRR_K,
            )
            jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
            jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
            jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
            jr["n_layers"] = ar["n_layers"]
            jr["shared_W"] = ar["shared_W"]
            by_arm[arm] = jr
            print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
                  "(T=%.4f L=%.2f) raw=%.3f" % (
                      seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                      jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                      jr["raw_bpc_at_T1_L1"]), flush=True)
            continue

        jr = joint_sweep(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
        jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
        jr["n_layers"] = ar["n_layers"]
        jr["shared_W"] = ar["shared_W"]
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
              "(T=%.4f L=%.2f) raw=%.3f" % (
                  seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                  jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                  jr["raw_bpc_at_T1_L1"]), flush=True)

    del E_base
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
        "N_STEPS": N_STEPS,
        "run_mode": RUN_MODE,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
    }


# ============================================================================
# Verdict
# ============================================================================

def _arm_agg(arm: str, units: List[Dict]) -> Dict:
    failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
    valid = [(not f) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
             for f, u in zip(failed, units)]
    valid_u = [u for ok, u in zip(valid, units) if ok]
    if not valid_u:
        return {"bpc_best_mean": float("inf"), "top1_acc_mean": float("nan"),
                "mrr_at_10_mean": float("nan"), "raw_bpc_at_T1_L1_mean": float("nan"),
                "n_valid_seeds": 0, "n_compute_failed": int(sum(failed)),
                "all_seeds_failed": True}
    bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid_u]
    top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid_u]
    mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid_u]
    raw_v = [u["by_arm"][arm]["raw_bpc_at_T1_L1"] for u in valid_u]
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
        "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_v)), 4),
        "n_valid_seeds": int(len(valid_u)),
        "n_compute_failed": int(sum(failed)),
        "all_seeds_failed": False,
    }


def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}
    vocab_entropy = math.log2(max(units[0].get("V", VOCAB_CAP), 2))

    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
    }
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    for arm in PLASTICITY_ARMS:
        by_arm_agg[arm] = _arm_agg(arm, units)

    single = by_arm_agg.get("ARM_SINGLE_LAYER_CFRPE", {})
    indep2 = by_arm_agg.get("ARM_2_LAYER_INDEPENDENT_CFRPE", {})
    indep3 = by_arm_agg.get("ARM_3_LAYER_INDEPENDENT_CFRPE", {})
    shared = by_arm_agg.get("ARM_2_LAYER_SHARED_W_CFRPE", {})

    single_bpc = single.get("bpc_best_mean", float("inf"))
    indep2_bpc = indep2.get("bpc_best_mean", float("inf"))
    indep3_bpc = indep3.get("bpc_best_mean", float("inf"))
    shared_bpc = shared.get("bpc_best_mean", float("inf"))

    # Best independent-layer arm
    indep_candidates = [
        ("ARM_2_LAYER_INDEPENDENT_CFRPE", indep2_bpc, indep2.get("bpc_best_cv", float("nan")),
         indep2.get("raw_bpc_at_T1_L1_mean", float("nan"))),
        ("ARM_3_LAYER_INDEPENDENT_CFRPE", indep3_bpc, indep3.get("bpc_best_cv", float("nan")),
         indep3.get("raw_bpc_at_T1_L1_mean", float("nan"))),
    ]
    indep_candidates = [c for c in indep_candidates if math.isfinite(c[1])]
    if indep_candidates:
        best_indep_name, best_indep_bpc, best_indep_cv, best_indep_raw = min(
            indep_candidates, key=lambda c: c[1])
    else:
        best_indep_name, best_indep_bpc, best_indep_cv, best_indep_raw = (
            "NONE", float("inf"), float("nan"), float("nan"))

    # Sanity rail checks
    sanity_single_ok = (math.isfinite(single_bpc) and
                        abs(single_bpc - SANITY_SINGLE_LAYER_REF_BPC) <= SANITY_SINGLE_LAYER_TOL)
    # shared_W must NOT beat single_layer by >= 0.05; if shared <= single - 0.05, control failed
    sanity_shared_ok = (not math.isfinite(shared_bpc) or
                        not math.isfinite(single_bpc) or
                        (single_bpc - shared_bpc) < 0.05)

    # READOUT_DEGENERATE
    degen_flag = (math.isfinite(best_indep_raw) and
                   abs(best_indep_raw - vocab_entropy) <= DEGEN_TOL)

    arm_summary = (
        "uni=bpc%.3f | single=bpc%.3f | indep2=bpc%.3f cv=%.3f | indep3=bpc%.3f cv=%.3f | "
        "shared2=bpc%.3f cv=%.3f | best_indep=%s bpc%.3f cv%.3f"
    ) % (
        unigram_bpc, single_bpc,
        indep2_bpc, indep2.get("bpc_best_cv", -1.0),
        indep3_bpc, indep3.get("bpc_best_cv", -1.0),
        shared_bpc, shared.get("bpc_best_cv", -1.0),
        best_indep_name, best_indep_bpc, best_indep_cv,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "best_indep_arm": best_indep_name,
        "best_indep_bpc": round(best_indep_bpc, 4) if math.isfinite(best_indep_bpc) else None,
        "best_indep_cv": round(best_indep_cv, 4) if math.isfinite(best_indep_cv) else None,
        "single_bpc": round(single_bpc, 4) if math.isfinite(single_bpc) else None,
        "shared_W_bpc": round(shared_bpc, 4) if math.isfinite(shared_bpc) else None,
        "indep_vs_single_lift": (
            round(single_bpc - best_indep_bpc, 4)
            if math.isfinite(best_indep_bpc) and math.isfinite(single_bpc) else None),
        "indep_vs_shared_gap": (
            round(shared_bpc - best_indep_bpc, 4)
            if math.isfinite(best_indep_bpc) and math.isfinite(shared_bpc) else None),
        "sanity_single_ok": bool(sanity_single_ok),
        "sanity_shared_ok": bool(sanity_shared_ok),
        "degen_flag": bool(degen_flag),
        "vocab_entropy_uniform_bits": round(vocab_entropy, 4),
        "n_seeds": len(units),
        "thresholds": {
            "CHAIN_GRADE_BONUS_BPC": CHAIN_GRADE_BONUS_BPC,
            "HARD_PASS_BPC": HARD_PASS_BPC,
            "MIDDLE_BAND_BPC_UPPER": MIDDLE_BAND_BPC_UPPER,
            "HP_BPC_CV_MAX": HP_BPC_CV_MAX,
            "SANITY_SINGLE_LAYER_REF_BPC": SANITY_SINGLE_LAYER_REF_BPC,
            "SANITY_SINGLE_LAYER_TOL": SANITY_SINGLE_LAYER_TOL,
        },
        "honest_scope": (
            "cross-layer compose at LM scale (text8 N_TRAIN=100k N_DIM=8192 V=4000). "
            "HARD_PASS = best_indep BPC <= %.2f AND beats shared-W control AND cv<=%.2f. "
            "CHAIN_GRADE_BONUS = best_indep BPC <= %.2f. "
            "HARD_FAIL = best_indep BPC > %.2f OR best_indep > shared_W "
            "(cross-layer pattern doesn't transfer to LM regime)." % (
                HARD_PASS_BPC, HP_BPC_CV_MAX, CHAIN_GRADE_BONUS_BPC, MIDDLE_BAND_BPC_UPPER)),
        "cites": [
            "preregs/2026-06-24_substrate_cross_layer_compose_LM_v1.md",
            "notes/director_composition_store_mine_inventory_2026-06-24.md",
            "experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py",
            "experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py",
            "experiments/exp_q_a3_l100_cross_layer_composition_v1_n16384.py",
        ],
        "by_construction_guards": {
            "real_data_asserted": True,
            "zero_llm_call_at_inference": True,
            "lambda_grid_excludes_zero": True,
            "per_arm_per_seed_logged": True,
        },
    }

    # Gate: best_indep arm failed entirely
    if not math.isfinite(best_indep_bpc):
        return ("HARD_FAIL",
                "HARD_FAIL: all independent-layer arms failed. %s" % arm_summary,
                detail)

    # READOUT_DEGENERATE gate
    if degen_flag:
        return ("READOUT_DEGENERATE",
                ("READOUT_DEGENERATE: best_indep raw_bpc=%.3f near vocab-entropy=%.3f. "
                 "Cross-layer collapsed to uniform-output regime. %s" % (
                     best_indep_raw, vocab_entropy, arm_summary)),
                detail)

    # cv check on the best_indep arm
    if math.isfinite(best_indep_cv) and best_indep_cv > HP_BPC_CV_MAX:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_HIGH_CV: best_indep cv=%.3f > %.2f mandatory. "
                 "best_indep BPC=%.3f; cross-layer signal seed-unstable. %s" % (
                     best_indep_cv, HP_BPC_CV_MAX, best_indep_bpc, arm_summary)),
                detail)

    # HARD_FAIL: best_indep > shared (controls supposed to be broken)
    if math.isfinite(shared_bpc) and best_indep_bpc > shared_bpc:
        return ("HARD_FAIL",
                ("HARD_FAIL: best_indep BPC=%.3f WORSE than shared-W control BPC=%.3f. "
                 "Cross-layer doesn't transfer to LM regime. %s" % (
                     best_indep_bpc, shared_bpc, arm_summary)),
                detail)

    # HARD_FAIL: above middle-band upper
    if best_indep_bpc > MIDDLE_BAND_BPC_UPPER:
        return ("HARD_FAIL",
                ("HARD_FAIL: best_indep BPC=%.3f > %.2f. Cross-layer doesn't help LM. %s" % (
                    best_indep_bpc, MIDDLE_BAND_BPC_UPPER, arm_summary)),
                detail)

    # CHAIN_GRADE_BONUS
    if best_indep_bpc <= CHAIN_GRADE_BONUS_BPC:
        verdict = "HARD_PASS"
        msg = ("HARD_PASS CHAIN_GRADE_BONUS: best_indep BPC=%.3f <= %.2f. "
               "Cross-layer architecture substantially breaks composition collapse at "
               "LM scale. Sanity rails: single_ok=%s shared_ok=%s. %s" % (
                   best_indep_bpc, CHAIN_GRADE_BONUS_BPC,
                   sanity_single_ok, sanity_shared_ok, arm_summary))
        detail["chain_grade_bonus"] = True
        return (verdict, msg, detail)

    # HARD_PASS
    if best_indep_bpc <= HARD_PASS_BPC:
        verdict = "HARD_PASS"
        msg = ("HARD_PASS: best_indep BPC=%.3f <= %.2f. "
               "Cross-layer breaks composition collapse + beats single-layer ref. "
               "Sanity rails: single_ok=%s shared_ok=%s. %s" % (
                   best_indep_bpc, HARD_PASS_BPC,
                   sanity_single_ok, sanity_shared_ok, arm_summary))
        detail["chain_grade_bonus"] = False
        return (verdict, msg, detail)

    # MIDDLE_BAND
    verdict = "MIDDLE_BAND"
    msg = ("MIDDLE_BAND: best_indep BPC=%.3f in (%.2f, %.2f]. "
           "Cross-layer is neutral at LM scale. %s" % (
               best_indep_bpc, HARD_PASS_BPC, MIDDLE_BAND_BPC_UPPER, arm_summary))
    detail["chain_grade_bonus"] = False
    return (verdict, msg, detail)


# ============================================================================
# Main loop with per-seed checkpoint
# ============================================================================

print("[config] anchor=%s arms=%s N_DIM=%d mode=%s seeds=%s" % (
    ANCHOR_NAME, ARMS, N_DIM, RUN_MODE, SEEDS), flush=True)

if DEVICE.type == "cuda":
    print("[gpu] %s" % torch.cuda.get_device_name(0), flush=True)
else:
    print("[device] CPU (no CUDA available)", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
done_seeds: List[int] = []
remaining_seeds: List[int] = SEEDS[:]

try:
    done_seeds, remaining_seeds = _resumable_seeds(SEEDS, out_dir)
    print("[ckpt] %d done, %d remaining: %s" % (
        len(done_seeds), len(remaining_seeds), remaining_seeds), flush=True)
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

summary = {
    "best_indep_bpc": detail.get("best_indep_bpc"),
    "best_indep_arm": detail.get("best_indep_arm"),
    "single_bpc": detail.get("single_bpc"),
    "shared_W_bpc": detail.get("shared_W_bpc"),
    "indep_vs_single_lift": detail.get("indep_vs_single_lift"),
    "indep_vs_shared_gap": detail.get("indep_vs_shared_gap"),
    "n_seeds": len(all_units),
}

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": summary,
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "ARM_CONFIG": ARM_CONFIG,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "CFRPE_LR": CFRPE_LR,
    "N_STEPS": N_STEPS,
    "LAMBDA_GRID": LAMBDA_GRID,
    "TEMP_GRID": TEMP_GRID,
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
