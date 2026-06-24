"""
substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1
-- LOAD-BEARING joint-compose cell (5 chain-grade primitives stacked).

Per research substrate-mining-drill A1 anchor (notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md):
attacks the 1.5-bit unclaimed gap from current chain-grade rail (fair_harness BPC
7.3065) toward bigram floor (~5.5 BPC). Tests whether the substrate's 5 chain-grade
aliveness primitives compose super-additively (beats single best knob by margin),
additively (>= single best - middle band), or sub-additively (interferes / saturates).

Decisive outcomes:
  HARD_PASS: substrate is alive enough to clear bigram floor; substrate-as-LM
             becomes real product story.
  MIDDLE_BAND: composition is additive-not-super-additive; envelope at +0.30-0.50
             over fair_harness.
  HARD_FAIL: composition saturates at single-knob; substrate has alive PRIMITIVES
             but no compose-stacking - architectural rethink needed.

FIVE ARMS (cumulative-build):
  ARM_BASELINE_fair_harness
      -- single bank, rank-1 Hebbian; reproduces fair_harness sanity rail 7.3065
  ARM_FAIR_HARNESS_PLUS_CFRPE
      -- + cf-RPE delta-rule plasticity (provenance check vs het_plasticity 7.1052)
  ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY
      -- + STDP asymmetric mixed in (heterogeneous plasticity row: ref 7.1654)
  ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY_PLUS_K2
      -- + K=2 multi-bank architecture (each bank N_per=4096)
  ARM_FULL_JOINT_COMPOSE
      -- + modern-Hopfield (Ramsauer 2020) exponential-energy cleanup on logits

PRE-REG HARD bands (per A1 spec):
  Sanity rails (Fix #28 per-arm metrics):
    ARM_BASELINE_fair_harness               within +/-0.05 of 7.3065
    ARM_FAIR_HARNESS_PLUS_CFRPE             within +/-0.05 of 7.1052 (cf-RPE ref)
    ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY  within +/-0.05 of 7.1654 (het-plast ref)
  HARD_PASS chain-grade-eligible:
    ARM_FULL_JOINT_COMPOSE BPC <= 6.85 AND cv <= 0.05
    (super-additive; substrate clears bigram-floor regime)
  MIDDLE_BAND:
    ARM_FULL_JOINT_COMPOSE BPC in [6.85, 7.05]
    (additive but not super-additive; substrate envelope at +0.30-0.50 over fair_harness)
  HARD_FAIL:
    ARM_FULL_JOINT_COMPOSE BPC >= 7.15
    (sub-additive; collapses to single-knob best)
  HARD_FAIL_PROVENANCE:
    Any sanity rail drift > 0.05 from reference
  HARD_FAIL_LLM_CALL:
    _LLM_CALL_COUNTER > 0 (substrate-only invariant)
  cv <= 0.05 across seeds for ARM_FULL_JOINT_COMPOSE mandatory

CONFIG:
  N_DIM_TOTAL=8192, V=4000, text8 N_TRAIN=100k, 3 seeds, word2vec sparse-bipolar f=0.05
  torch + CUDA (Fix #24: GPU dispatch must actually use GPU; matmul + batched ops)
  Routing: overnight_queue (GPU)

CITES:
  notes/exp_dev_handoff_research_substrate_aliveness_FULL_store_mined_2026-06-24.md (A1 anchor)
  notes/research_substrate_aliveness_FULL_store_mined_map_2026-06-24.md (master scour)
  preregs/2026-06-24_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.md
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json (sanity rail 7.3065)
  data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json (het-plast 7.1654; cf-RPE 7.1052)
  data/exp_modern_hopfield_n_sweep_v1/metrics.json (modern-Hopfield chain-grade row 100)
  data/exp_substrate_K2_x_cfrpe_compose_word2vec_v2/metrics.json (encoder pipeline base; provenance gate)
  experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py (this cell's torch+CUDA encoder base)
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py (STDP primitive)
  experiments/exp_modern_hopfield_n_sweep_v1.py (modern-Hopfield primitive)
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

ANCHOR_NAME = "substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only audit counter (Skunkworks structural blocker)
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Pre-reg threshold bands (pre-registered; do NOT modify post-smoke)
# ============================================================================
# All "lift" measured as BPC reduction. Lower BPC is better.

# Sanity rails (each arm in cumulative build must reproduce the prior cert-graded reference)
SANITY_RAIL_BASELINE_REF = 7.3065     # fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR
SANITY_RAIL_CFRPE_REF = 7.1052        # het_plasticity ARM_CFRPE_ONLY
SANITY_RAIL_HETPLAST_REF = 7.1654     # het_plasticity ARM_CFRPE_STDP_HETEROGENEOUS
SANITY_RAIL_TOLERANCE = 0.05          # +/-0.05 around each reference

# Joint compose verdict bands (on ARM_FULL_JOINT_COMPOSE BPC)
HARD_PASS_BPC_CEILING = 6.85          # substrate clears bigram-floor regime
MIDDLE_BAND_BPC_LOWER = 6.85
MIDDLE_BAND_BPC_UPPER = 7.05
HARD_FAIL_BPC_FLOOR = 7.15            # below this floor = HARD_FAIL (sub-additive)
CV_MAX = 0.05                          # cv mandatory across seeds for FULL_JOINT

# ============================================================================
# Primitive knob parameters (frozen from chain-grade source cells)
# ============================================================================
CFRPE_LR = 0.5                        # cf-RPE learning rate (het_plasticity / K2 cell)
STDP_WEIGHT = 0.5                     # STDP asymmetric contribution weight (het_plasticity)
INGEST_BATCH = 64                     # training batch size
N_STEPS_PER_SEED = 1000               # cf-RPE iterative steps (het_plasticity full-scale)

# K-bank config
K_BANKS = 2
GATE_TEMP = 0.5

# Modern-Hopfield cleanup
MH_BETA = 8.0                         # exponential-energy sharpness (modern_hopfield_n_sweep row 100)
MH_ITERS = 3                          # cleanup iterations (modern_hopfield primitive)

# Eval hyperparameter grids (LAMBDA_GRID excludes 0.0 per Skunkworks META C7)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Encoder
SPARSE_BIPOLAR_F = 0.05
WORD2VEC_MODEL = "word2vec-google-news-300"
PRETRAIN_DIM = 300

# Arms (cumulative-build order)
ARMS = [
    "ARM_BASELINE_fair_harness",
    "ARM_FAIR_HARNESS_PLUS_CFRPE",
    "ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY",
    "ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY_PLUS_K2",
    "ARM_FULL_JOINT_COMPOSE",
]

# ============================================================================
# CLI / run-mode
# ============================================================================
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

# ============================================================================
# Production config
# ============================================================================
N_DIM_TOTAL = 8192
N_DIM_PER_BANK = N_DIM_TOTAL // K_BANKS   # 4096 per bank for K=2 arms
VOCAB_CAP = 4000
RECALL_BATCH = 256
INGEST_CHUNK = 4096

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = N_STEPS_PER_SEED
else:
    # Smoke: clean synthetic data + minimal config (per memory rule:
    # smoke tests must use clean synthetic data, NOT substrate state).
    # Goal: fit under 180s on CPU; exercise every arm + word2vec encoder +
    # joint sweep + modern-Hopfield cleanup + verdict bands.
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM_TOTAL = 1024
    N_DIM_PER_BANK = N_DIM_TOTAL // K_BANKS    # 512
    N_STEPS = 80
    RECALL_BATCH = 128
    INGEST_CHUNK = 512

CONFIG_VERSION = (
    "%s; encoder=word2vec_sparse_bipolar_f%.3f; N_DIM_TOTAL=%d K_BANKS=%d "
    "N_DIM_PER_BANK=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s "
    "mode=%s temps=%s lambdas=%s cfrpe_lr=%.3f stdp_w=%.3f gate_temp=%.3f "
    "mh_beta=%.2f mh_iters=%d n_steps=%d batch=%d device=%s"
) % (
    ANCHOR_NAME, SPARSE_BIPOLAR_F, N_DIM_TOTAL, K_BANKS, N_DIM_PER_BANK,
    N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID,
    CFRPE_LR, STDP_WEIGHT, GATE_TEMP, MH_BETA, MH_ITERS, N_STEPS, INGEST_BATCH,
    str(DEVICE),
)


# ============================================================================
# text8 corpus utilities
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
# Encoder: word2vec-projected sparse-bipolar (matches fair_harness chain-grade)
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


def build_E_word2vec(vocab: List[str], n_dim: int, seed: int) -> Tuple[torch.Tensor, Dict]:
    """word2vec(300) -> Gaussian-project(300 -> n_dim) -> L2 normalize. OOV -> char-trigram.

    Matches fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR encoder pipeline EXACTLY.
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


def build_E_synthetic_smoke(V: int, n_dim: int, seed: int) -> Tuple[torch.Tensor, Dict]:
    """Clean synthetic encoder for smoke: gaussian -> L2 norm. NO substrate state.

    Used in smoke mode per memory rule: smoke tests must use clean synthetic data,
    NOT substrate's existing atoms/labels/encoding.
    """
    rng = np.random.default_rng(seed * 9173 + 11)
    E_np = rng.standard_normal((V, n_dim)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(V), "n_miss": 0, "n_vocab": int(V),
            "pretrain_dim": int(n_dim), "synthetic_smoke": True}
    return E_t, meta


def sparsify_bipolar_gpu(E: torch.Tensor, f: float) -> torch.Tensor:
    """Sparse-bipolar projection on GPU: top-k by abs, sign-encode.

    Identical to fair_harness sparsify_bipolar_gpu primitive.
    """
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
# Plasticity rules (torch + CUDA; Fix #24)
# ============================================================================

def build_W_hebbian_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                          ingest_chunk: int) -> torch.Tensor:
    """One-pass batched outer-product rank-1 Hebbian (sanity-rail baseline).

    W = sum_{t} E[idx[t+1]]^T @ E[idx[t]]   (dim x dim)
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
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
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_W_cfrpe_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                       n_steps: int, batch: int, lr: float,
                       seed: int, arm_idx: int) -> torch.Tensor:
    """Iterative cf-RPE delta-rule plasticity.

    delta_W = (E[t+1] - E[t] @ W^T)^T @ E[t] / batch
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E[idx_train_t[st]]
        Nxt = E[idx_train_t[st + 1]]
        error = Nxt - Ctx @ W.T
        dW = (error.T @ Ctx) / float(batch)
        W = W + lr * dW
    return W


def build_W_cfrpe_stdp_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                              n_steps: int, batch: int, lr: float, stdp_w: float,
                              seed: int, arm_idx: int) -> torch.Tensor:
    """Heterogeneous compose: cf-RPE delta (task axis) + STDP asymmetric (temporal axis).

    dW_cf  = (Nxt - Ctx @ W^T)^T @ Ctx / batch     (cf-RPE)
    dW_stdp = (Nxt^T @ Ctx - Ctx^T @ Nxt) / batch  (STDP antisymmetric)
    dW = dW_cf + stdp_w * dW_stdp
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E[idx_train_t[st]]
        Nxt = E[idx_train_t[st + 1]]
        error = Nxt - Ctx @ W.T
        dW_cf = (error.T @ Ctx) / float(batch)
        dW_stdp = (Nxt.T @ Ctx - Ctx.T @ Nxt) / float(batch)
        dW = dW_cf + stdp_w * dW_stdp
        W = W + lr * dW
    return W


# ============================================================================
# K=1 logits builder (single bank)
# ============================================================================

def build_logits_k1_gpu(plasticity_mode: str, E_full: torch.Tensor,
                          idx_train_t: torch.Tensor, idx_held_t: torch.Tensor,
                          n_steps: int, batch: int, lr: float, stdp_w: float,
                          seed: int, arm_idx: int,
                          recall_batch: int, ingest_chunk: int) -> Dict:
    """Compute [n_held, V] logits for K=1 arm on GPU.

    plasticity_mode in {"hebbian", "cfrpe", "cfrpe_stdp"}.
    """
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    t0 = time.time()
    if plasticity_mode == "hebbian":
        W = build_W_hebbian_gpu(E_full, idx_train_t, ingest_chunk)
    elif plasticity_mode == "cfrpe":
        W = build_W_cfrpe_gpu(E_full, idx_train_t, n_steps, batch, lr, seed, arm_idx)
    elif plasticity_mode == "cfrpe_stdp":
        W = build_W_cfrpe_stdp_gpu(E_full, idx_train_t, n_steps, batch, lr,
                                      stdp_w, seed, arm_idx)
    else:
        raise ValueError("unknown plasticity_mode: %s" % plasticity_mode)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    pred = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred[b:end] = _l2_normalize_t(ctx_b @ W.T)
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        logits[b:end] = pred[b:end] @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W, pred, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np, "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2)}


# ============================================================================
# K=2 logits builder (multi-bank with cf-RPE+STDP plasticity per bank)
# ============================================================================

def build_logits_k2_cfrpe_stdp_gpu(E_full: torch.Tensor,
                                       idx_train_t: torch.Tensor,
                                       idx_held_t: torch.Tensor,
                                       n_steps: int, batch: int, lr: float,
                                       stdp_w: float,
                                       seed: int, arm_idx: int,
                                       recall_batch: int, gate_temp: float,
                                       ingest_chunk: int) -> Dict:
    """Compute [n_held, V] logits for K=2 bank arm using cf-RPE+STDP per bank.

    Per-bank W with gate-weighted heterogeneous plasticity:
      dW_cf_k  = (Nxt_k - Ctx_k @ W_k^T) error per bank
      dW_stdp_k = (Nxt_k^T @ Ctx_k - Ctx_k^T @ Nxt_k) / batch per bank
      dW_k = dW_cf_k + stdp_w * dW_stdp_k
    Gate uses bank-0 slice as gate signal. Read: gate-weighted sum of per-bank predictions.
    """
    V, n_dim = E_full.shape
    K = K_BANKS
    N_per = n_dim // K
    device = E_full.device

    # Bank slices
    E_banks = [E_full[:, k * N_per:(k + 1) * N_per].contiguous() for k in range(K)]

    # Gate projection
    rng_gate = np.random.default_rng(seed * 7919 + arm_idx * 1013 + 9999)
    W_gate_np = rng_gate.standard_normal((K, N_per)).astype(np.float32)
    W_gate_np /= np.linalg.norm(W_gate_np, axis=1, keepdims=True) + 1e-9
    W_gate = torch.from_numpy(W_gate_np).to(device=device, dtype=TORCH_DTYPE)

    # Per-bank W
    W_banks = [torch.zeros((N_per, N_per), dtype=TORCH_DTYPE, device=device)
               for _ in range(K)]

    t0 = time.time()
    n_pairs = idx_train_t.shape[0] - 1

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        gate_inputs = E_banks[0][idx_train_t[st]]
        raw = gate_inputs @ W_gate.T
        raw = raw / gate_temp
        raw = raw - raw.max(dim=1, keepdim=True).values
        probs_b = torch.exp(raw)
        probs_b = probs_b / (probs_b.sum(dim=1, keepdim=True) + 1e-30)
        for k in range(K):
            Ctx_k = E_banks[k][idx_train_t[st]]
            Nxt_k = E_banks[k][idx_train_t[st + 1]]
            gw = probs_b[:, k:k + 1]
            # cf-RPE (task axis)
            error_k = Nxt_k - Ctx_k @ W_banks[k].T
            dW_cf_k = (error_k * gw).T @ Ctx_k / float(batch)
            # STDP asymmetric (temporal axis): weighted by gw on the asymmetric outer
            Ctx_kw = Ctx_k * gw
            Nxt_kw = Nxt_k * gw
            dW_stdp_k = (Nxt_kw.T @ Ctx_k - Ctx_kw.T @ Nxt_k) / float(batch)
            dW_k = dW_cf_k + stdp_w * dW_stdp_k
            W_banks[k] = W_banks[k] + lr * dW_k

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    # Recall
    t0 = time.time()
    n_h = idx_held_t.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        held_idx = idx_held_t[b:end]
        gate_in = E_banks[0][held_idx]
        raw = gate_in @ W_gate.T
        raw = raw / gate_temp
        raw = raw - raw.max(dim=1, keepdim=True).values
        probs_r = torch.exp(raw)
        probs_r = probs_r / (probs_r.sum(dim=1, keepdim=True) + 1e-30)
        logit_chunk = torch.zeros((end - b, V), dtype=TORCH_DTYPE, device=device)
        for k in range(K):
            ctx_k = E_banks[k][held_idx]
            pred_k = _l2_normalize_t(ctx_k @ W_banks[k].T)
            bank_scores = pred_k @ E_banks[k].T
            logit_chunk = logit_chunk + probs_r[:, k:k + 1] * bank_scores
        logits[b:end] = logit_chunk
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    for _ in range(K):
        del E_banks[0]
    del W_banks, W_gate, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np, "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2)}


# ============================================================================
# Modern-Hopfield cleanup (Ramsauer 2020 exponential-energy retrieval)
# ============================================================================

def modern_hopfield_cleanup_gpu(logits_np: np.ndarray, E_full: torch.Tensor,
                                   beta: float, n_iters: int,
                                   recall_batch: int) -> np.ndarray:
    """Apply modern-Hopfield (exponential-energy) cleanup to per-query logits.

    Procedure (Ramsauer 2020):
      For each held query, treat the logits as similarities to vocab patterns
      (rows of E_full). Sharpen via softmax(beta * sim) and remap via E:
        s_new = softmax(beta * s @ E^T) @ E -> normalize to bipolar -> rescore.
      Repeat for n_iters.

    Input:  logits_np [n_h, V] (substrate's per-vocab predictions, real-valued)
    Output: cleaned logits [n_h, V] (sharpened toward vocab attractors)

    The cleanup interprets logits as soft pattern-assignments over V vocab
    "stored patterns" (rows of E). It sharpens by softmax(beta) iterating
    against E. The output logits = (cleaned pattern) @ E.T per row.
    """
    device = E_full.device
    V, dim = E_full.shape
    n_h = logits_np.shape[0]

    logits_t = torch.from_numpy(logits_np).to(device=device, dtype=TORCH_DTYPE)

    cleaned = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)

    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        # Start from the substrate's per-query soft assignment over vocab patterns:
        # interpret current logits row as similarity-to-each-vocab; build a pattern
        # by mixing E weighted by softmax(beta * logits)
        cur_logits = logits_t[b:end]                       # [chunk, V]
        for _ in range(n_iters):
            # Sharpen via softmax(beta * logits)
            z = beta * cur_logits
            z = z - z.max(dim=1, keepdim=True).values
            p = torch.exp(z)
            p = p / (p.sum(dim=1, keepdim=True) + 1e-30)   # [chunk, V]
            # Mix vocab patterns: state = p @ E         [chunk, dim]
            state = p @ E_full
            state = _l2_normalize_t(state)
            # Re-score against all vocab patterns: new logits = state @ E.T
            cur_logits = state @ E_full.T                    # [chunk, V]
        cleaned[b:end] = cur_logits
        if device.type == "cuda" and (b // recall_batch) % 8 == 0:
            torch.cuda.synchronize()

    out = cleaned.detach().cpu().numpy().astype(np.float32)
    del logits_t, cleaned
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return out


# ============================================================================
# BPC / eval utilities (exact from fair_harness v1)
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


def raw_bpc_at_T1(logits_np: np.ndarray, nxt_eval: np.ndarray) -> float:
    """BPC at T=1, no unigram interp. DEGEN sanity."""
    n_h = logits_np.shape[0]
    n_eval = min(n_h, len(nxt_eval))
    if n_eval == 0:
        return float("inf")
    sub = logits_np[:n_eval]
    nxt_e = nxt_eval[:n_eval]
    z = sub - sub.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / np.clip(e.sum(axis=1, keepdims=True), 1e-30, None)
    p_nxt = p[np.arange(n_eval), nxt_e].clip(1e-12, 1.0)
    return float(-np.mean(np.log(p_nxt)) / math.log(2.0))


def joint_sweep(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray) -> Dict:
    """Joint (T, lambda) sweep on dev; pick best per-metric; report on test."""
    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}

    per_lambda_best_T_bpc: Dict[float, Dict] = {}

    for T in TEMP_GRID:
        probs_dev = softmax_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in LAMBDA_GRID:
            logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, MRR_K)
            if bd < best_bpc["dev_value"]:
                best_bpc = {"T": float(T), "lambda": float(lam), "dev_value": bd}
            if td > best_top1["dev_value"]:
                best_top1 = {"T": float(T), "lambda": float(lam), "dev_value": td}
            if md > best_mrr["dev_value"]:
                best_mrr = {"T": float(T), "lambda": float(lam), "dev_value": md}
            cur = per_lambda_best_T_bpc.get(float(lam),
                                              {"T": float(T), "bpc_dev": bd})
            if bd < cur["bpc_dev"]:
                per_lambda_best_T_bpc[float(lam)] = {"T": float(T), "bpc_dev": bd}
            else:
                per_lambda_best_T_bpc.setdefault(float(lam), cur)

    def _eval_test(T: float, lam: float, fn) -> float:
        probs = softmax_with_T(sub_logits_test, T)
        logp_sub = np.log(np.clip(probs, 1e-30, 1.0))
        logp = log_linear_interp(logp_sub, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _eval_test(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _eval_test(best_top1["T"], best_top1["lambda"], top1_acc)
    mrr_best_test = _eval_test(best_mrr["T"], best_mrr["lambda"],
                                lambda lp, nx: mrr_at_k(lp, nx, MRR_K))

    per_lambda_T_summary = {
        str(round(lam, 3)): {"best_T": v["T"], "bpc_dev": round(v["bpc_dev"], 4)}
        for lam, v in sorted(per_lambda_best_T_bpc.items())
    }

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
        "per_lambda_T_summary": per_lambda_T_summary,
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray, V: int) -> Dict:
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
    rr = np.where(ranks <= MRR_K, 1.0 / ranks, 0.0)
    mrr = float(np.mean(rr))
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(top1, 4),
            "mrr_unigram": round(mrr, 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Arm config (cumulative-build)
# ============================================================================
# Each arm specifies: k (banks), plasticity_mode, mh_cleanup (bool).

ARM_CONFIGS = {
    "ARM_BASELINE_fair_harness": {
        "k": 1, "plasticity": "hebbian", "mh_cleanup": False,
    },
    "ARM_FAIR_HARNESS_PLUS_CFRPE": {
        "k": 1, "plasticity": "cfrpe", "mh_cleanup": False,
    },
    "ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY": {
        "k": 1, "plasticity": "cfrpe_stdp", "mh_cleanup": False,
    },
    "ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY_PLUS_K2": {
        "k": 2, "plasticity": "cfrpe_stdp", "mh_cleanup": False,
    },
    "ARM_FULL_JOINT_COMPOSE": {
        "k": 2, "plasticity": "cfrpe_stdp", "mh_cleanup": True,
    },
}


# ============================================================================
# Instrumentation self-test (MANDATORY)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null / non-sentinel at small scale.

    Per memory rule: self-test must verify expected values BEFORE dispatch.
    """
    print("[selftest] running instrumentation self-test...", flush=True)

    # ST1: cf-RPE delta shrinks prediction error (single pair)
    n_dim_st = 64
    rng_st = np.random.default_rng(42)
    Ctx_np = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Nxt_np = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Ctx_np /= np.linalg.norm(Ctx_np) + 1e-8
    Nxt_np /= np.linalg.norm(Nxt_np) + 1e-8
    W_test = np.zeros((n_dim_st, n_dim_st), dtype=np.float32)
    err_before = float(np.linalg.norm(Nxt_np - Ctx_np @ W_test.T))
    dW = (Nxt_np - Ctx_np @ W_test.T).T @ Ctx_np
    W_test = W_test + 0.9 * dW
    err_after = float(np.linalg.norm(Nxt_np - Ctx_np @ W_test.T))
    assert err_after < err_before, (
        "ST1 cf-RPE should shrink error: before=%.4f after=%.4f" % (err_before, err_after))
    print("[selftest] ST1 cf-RPE shrinks error: %.4f -> %.4f" % (err_before, err_after), flush=True)

    # ST2: STDP antisymmetry: dW_stdp + dW_stdp^T == 0
    b_st = 4
    Ctx_t = torch.randn(b_st, n_dim_st, device=DEVICE)
    Nxt_t = torch.randn(b_st, n_dim_st, device=DEVICE)
    dW_stdp = (Nxt_t.T @ Ctx_t - Ctx_t.T @ Nxt_t) / float(b_st)
    antisym_err = float((dW_stdp + dW_stdp.T).abs().max())
    assert antisym_err < 1e-4, "ST2 STDP antisymmetry failed: %.4e" % antisym_err
    print("[selftest] ST2 STDP antisymmetry OK (err=%.2e)" % antisym_err, flush=True)

    # ST3: heterogeneous compose W differs from pure Hebbian
    W_heb = (Nxt_t.T @ Ctx_t) / float(b_st)
    W_cf_zero_init = (Nxt_t.T @ Ctx_t) / float(b_st)   # W=0 init -> error=Nxt
    W_hetero = W_cf_zero_init + 0.5 * dW_stdp
    diff = float((W_hetero - W_heb).norm())
    assert diff > 1e-6, "ST3 heterogeneous W should differ from Hebbian: %.2e" % diff
    print("[selftest] ST3 heterogeneous W differs from Hebbian (diff=%.4f)" % diff, flush=True)

    # ST4: gate-softmax probs sum to 1 (torch)
    n_per_st = 32
    K_st = 2
    rng2 = np.random.default_rng(7)
    W_gate_st_np = rng2.standard_normal((K_st, n_per_st)).astype(np.float32)
    W_gate_st_np /= np.linalg.norm(W_gate_st_np, axis=1, keepdims=True) + 1e-9
    W_gate_st = torch.from_numpy(W_gate_st_np).to(DEVICE)
    v_st = torch.randn(n_per_st, device=DEVICE)
    v_st = v_st / (v_st.norm() + 1e-8)
    raw = (W_gate_st @ v_st) / GATE_TEMP
    raw = raw - raw.max()
    probs_st = torch.exp(raw)
    probs_st = probs_st / probs_st.sum()
    assert abs(float(probs_st.sum()) - 1.0) < 1e-5, (
        "ST4 gate probs don't sum to 1: %.6f" % float(probs_st.sum()))
    assert (probs_st >= 0).all().item(), "ST4 gate probs contain negative values"
    print("[selftest] ST4 gate probs sum=%.6f OK" % float(probs_st.sum()), flush=True)

    # ST5: build_logits_k1_gpu produces non-zero logits (hebbian path)
    V_st = 10
    n_dim_s2 = 128
    rng3 = np.random.default_rng(0)
    E_np = rng3.standard_normal((V_st, n_dim_s2)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(DEVICE)
    E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F))
    idx_tr_st = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=torch.long, device=DEVICE)
    idx_h_st = torch.tensor([3, 4, 5, 6], dtype=torch.long, device=DEVICE)
    ar = build_logits_k1_gpu("hebbian", E_sb, idx_tr_st, idx_h_st,
                              n_steps=5, batch=3, lr=0.5, stdp_w=0.5,
                              seed=0, arm_idx=0, recall_batch=4, ingest_chunk=4)
    logits_st = ar["logits"]
    assert logits_st is not None, "ST5 logits is None"
    assert logits_st.shape == (idx_h_st.shape[0], V_st), (
        "ST5 logits shape mismatch: %s" % str(logits_st.shape))
    assert not np.all(logits_st == 0.0), "ST5 logits all zero"
    print("[selftest] ST5 K1 hebbian logits shape=%s non-zero OK" % str(logits_st.shape), flush=True)

    # ST6: build_logits_k1_gpu produces non-zero logits (cfrpe + cfrpe_stdp paths)
    ar_cf = build_logits_k1_gpu("cfrpe", E_sb, idx_tr_st, idx_h_st,
                                  n_steps=5, batch=3, lr=0.5, stdp_w=0.5,
                                  seed=0, arm_idx=1, recall_batch=4, ingest_chunk=4)
    ar_het = build_logits_k1_gpu("cfrpe_stdp", E_sb, idx_tr_st, idx_h_st,
                                    n_steps=5, batch=3, lr=0.5, stdp_w=0.5,
                                    seed=0, arm_idx=2, recall_batch=4, ingest_chunk=4)
    assert not np.all(ar_cf["logits"] == 0.0), "ST6 cfrpe logits all zero"
    assert not np.all(ar_het["logits"] == 0.0), "ST6 cfrpe_stdp logits all zero"
    diff_cf_het = float(np.abs(ar_cf["logits"] - ar_het["logits"]).mean())
    assert diff_cf_het > 1e-6, "ST6 cfrpe vs cfrpe_stdp logits identical: %.2e" % diff_cf_het
    print("[selftest] ST6 K1 cfrpe vs cfrpe_stdp differ (mean_abs_diff=%.4e) OK" % diff_cf_het,
          flush=True)

    # ST7: build_logits_k2_cfrpe_stdp_gpu produces non-zero logits (K2 het-plasticity)
    ar4 = build_logits_k2_cfrpe_stdp_gpu(E_sb, idx_tr_st, idx_h_st,
                                            n_steps=5, batch=3, lr=0.5, stdp_w=0.5,
                                            seed=0, arm_idx=3, recall_batch=4,
                                            gate_temp=GATE_TEMP, ingest_chunk=4)
    logits4 = ar4["logits"]
    assert logits4 is not None, "ST7 K2 logits is None"
    assert logits4.shape == (idx_h_st.shape[0], V_st), "ST7 K2 logits shape mismatch"
    assert not np.all(logits4 == 0.0), "ST7 K2 logits all zero"
    # K1 vs K2 with cfrpe_stdp must differ
    diff_k_st = float(np.abs(ar_het["logits"] - logits4).mean())
    assert diff_k_st > 1e-6, "ST7 K1 vs K2 het-plasticity logits identical: %.2e" % diff_k_st
    print("[selftest] ST7 K2 cfrpe_stdp shape=%s non-zero diff_K1K2=%.4e OK" % (
        str(logits4.shape), diff_k_st), flush=True)

    # ST8: modern-Hopfield cleanup changes logits (cleanup non-identity) + finite
    cleaned = modern_hopfield_cleanup_gpu(logits4, E_sb, beta=MH_BETA, n_iters=MH_ITERS,
                                            recall_batch=4)
    assert cleaned.shape == logits4.shape, "ST8 cleanup shape mismatch"
    assert np.all(np.isfinite(cleaned)), "ST8 cleanup contains non-finite values"
    diff_clean = float(np.abs(logits4 - cleaned).mean())
    assert diff_clean > 1e-6, "ST8 modern-Hopfield cleanup is identity: %.2e" % diff_clean
    print("[selftest] ST8 modern-Hopfield cleanup non-identity (mean_abs_diff=%.4e) OK" % diff_clean,
          flush=True)

    # ST9: modern-Hopfield retrieves clean patterns from corrupted query
    # With well-separated patterns and a corrupted query, MH should converge toward
    # the clean pattern (Ramsauer 2020 exponential energy guarantees this for separable patterns).
    rng_mh = np.random.default_rng(99)
    n_pat = 5
    n_dim_mh = 64
    P_np = (rng_mh.integers(0, 2, size=(n_pat, n_dim_mh)) * 2 - 1).astype(np.float32)
    P_t = torch.from_numpy(_l2_normalize_np(P_np)).to(DEVICE)
    # Query: pattern 0 corrupted by 10% flip
    flip_mask = rng_mh.random(n_dim_mh) < 0.10
    q_np = P_np[0].copy()
    q_np[flip_mask] = -q_np[flip_mask]
    q_np = q_np / (np.linalg.norm(q_np) + 1e-8)
    # Build raw logits: q @ P^T  ->  similarity row
    q_logits = (q_np[None, :] @ P_np.T).astype(np.float32)
    # Note: q_logits is the substrate's "best guess" -- top1 may still be 0
    # since 10% flip preserves most similarity.
    # Run MH cleanup; expect cleaned top1 to be 0 (the original pattern)
    cleaned_mh = modern_hopfield_cleanup_gpu(q_logits, P_t, beta=MH_BETA,
                                                n_iters=MH_ITERS, recall_batch=1)
    cleaned_top1 = int(np.argmax(cleaned_mh[0]))
    assert cleaned_top1 == 0, (
        "ST9 MH cleanup should retrieve pattern 0; got pattern %d" % cleaned_top1)
    print("[selftest] ST9 MH cleanup retrieves pattern 0 from 10%-corrupted query OK", flush=True)

    # ST10: joint_sweep returns finite metrics for small synthetic
    n_tok_st = 30
    n_v_sm = 6
    rng6 = np.random.default_rng(99)
    logits_syn = rng6.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_syn = rng6.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_log_st = np.log(np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32))
    nd = n_tok_st // 2
    jr = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                     nxt_syn[:nd], nxt_syn[nd:])
    assert math.isfinite(jr["bpc_best"]), "ST10 bpc_best not finite"
    assert math.isfinite(jr["top1_acc"]), "ST10 top1_acc not finite"
    assert math.isfinite(jr["mrr_at_10"]), "ST10 mrr_at_10 not finite"
    assert jr["n_dev"] > 0, "ST10 n_dev == 0"
    assert jr["n_test"] > 0, "ST10 n_test == 0"
    assert isinstance(jr["per_lambda_T_summary"], dict) and len(jr["per_lambda_T_summary"]) > 0, (
        "ST10 per_lambda_T_summary not captured")
    print("[selftest] ST10 joint_sweep OK (bpc=%.3f top1=%.4f mrr=%.4f, %d lambdas tracked)" % (
        jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"], len(jr["per_lambda_T_summary"])), flush=True)

    # ST11: sparsify_bipolar_gpu produces correct fraction nonzero
    E_chk = torch.from_numpy(
        np.random.default_rng(0).standard_normal((20, 100)).astype(np.float32)
    ).to(DEVICE)
    E_sparse = sparsify_bipolar_gpu(E_chk, 0.05)
    nnz_per_row = (E_sparse != 0).sum(dim=1).cpu().numpy()
    expected_nnz = max(1, int(round(0.05 * 100)))
    assert bool((nnz_per_row == expected_nnz).all()), (
        "ST11 sparse nnz mismatch: expected %d, got %s" % (expected_nnz, str(nnz_per_row[:5])))
    print("[selftest] ST11 sparsify_bipolar_gpu nnz=%d OK" % expected_nnz, flush=True)

    # ST12: LAMBDA_GRID excludes 0.0 (Skunkworks META C7)
    assert 0.0 not in LAMBDA_GRID, "ST12 LAMBDA_GRID must exclude 0.0 (Skunkworks META C7)"
    print("[selftest] ST12 LAMBDA_GRID excludes 0.0 OK", flush=True)

    # ST13: LLM-call counter is zero at selftest end (substrate-only invariant)
    assert _LLM_CALL_COUNTER[0] == 0, "ST13 LLM call counter non-zero: %d" % _LLM_CALL_COUNTER[0]
    print("[selftest] ST13 LLM call counter == 0 OK", flush=True)

    # ST14: ARM_CONFIGS keys match ARMS list (no drift between configs and named arms)
    for arm in ARMS:
        assert arm in ARM_CONFIGS, "ST14 ARMS entry %r missing from ARM_CONFIGS" % arm
    for arm in ARM_CONFIGS:
        assert arm in ARMS, "ST14 ARM_CONFIGS key %r missing from ARMS" % arm
    print("[selftest] ST14 ARMS/ARM_CONFIGS consistent (%d arms) OK" % len(ARMS), flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()

    # Smoke uses clean synthetic data (per memory rule); full uses real text8 + word2vec.
    if RUN_MODE == "smoke":
        print("\n[seed=%d] SMOKE: clean synthetic corpus (V=%d N_TRAIN=%d N_HELD=%d)" % (
            seed, VOCAB_CAP, N_TRAIN, N_HELD), flush=True)
        rng_corp = np.random.default_rng(seed * 7727 + 41)
        # Synthetic markov-bigram with slight structure: about 50% of tokens follow
        # a transition rule, 50% uniform.
        bigram_targets = rng_corp.integers(0, VOCAB_CAP, size=VOCAB_CAP).astype(np.int64)
        idx_train = np.empty(N_TRAIN, dtype=np.int64)
        idx_train[0] = rng_corp.integers(0, VOCAB_CAP)
        for i in range(1, N_TRAIN):
            if rng_corp.random() < 0.5:
                idx_train[i] = bigram_targets[idx_train[i - 1]]
            else:
                idx_train[i] = rng_corp.integers(0, VOCAB_CAP)
        idx_held = np.empty(N_HELD, dtype=np.int64)
        idx_held[0] = rng_corp.integers(0, VOCAB_CAP)
        for i in range(1, N_HELD):
            if rng_corp.random() < 0.5:
                idx_held[i] = bigram_targets[idx_held[i - 1]]
            else:
                idx_held[i] = rng_corp.integers(0, VOCAB_CAP)
        V = VOCAB_CAP
        encoder_meta = {"smoke_synthetic": True, "V": V, "N_TRAIN": N_TRAIN}
    else:
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
        encoder_meta = {}

    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM_TOTAL, str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]), flush=True)

    # Build encoder ONCE per seed
    print("\n[seed=%d] building encoder (V=%d, N_DIM=%d)..." % (seed, V, N_DIM_TOTAL), flush=True)
    t_enc0 = time.time()
    if RUN_MODE == "smoke":
        E_proj_t, w2v_meta = build_E_synthetic_smoke(V, N_DIM_TOTAL, seed)
    else:
        E_proj_t, w2v_meta = build_E_word2vec(vocab, N_DIM_TOTAL, seed)
    encoder_meta.update(w2v_meta)
    E_full = _l2_normalize_t(sparsify_bipolar_gpu(E_proj_t, SPARSE_BIPOLAR_F))
    sparsity = float((E_full != 0).float().mean().item())
    print("[seed=%d] encoder built in %.1fs; w2v_hit=%d/%d sparsity=%.3f" % (
        seed, time.time() - t_enc0, w2v_meta["n_hit"], w2v_meta["n_vocab"], sparsity), flush=True)
    del E_proj_t

    # Move indices once
    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    # Build eval-pair domain (ctx != UNK)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    ctx_eval = ctx_full[mask]
    nxt_eval = nxt_full[mask]
    n_eval = len(ctx_eval)
    if n_eval == 0:
        print("[WARN seed=%d] no valid eval pairs" % seed, flush=True)
        return {"seed": seed, "by_arm": {"ARM_UNIGRAM": uni}, "V": V,
                "N_DIM_TOTAL": N_DIM_TOTAL, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2)}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni, "w2v_meta": w2v_meta}

    for arm_idx, arm in enumerate(ARMS):
        cfg = ARM_CONFIGS[arm]
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s k=%d plast=%s mh=%s] computing..." % (
            seed, arm, cfg["k"], cfg["plasticity"], cfg["mh_cleanup"]), flush=True)
        try:
            if cfg["k"] == 1:
                ar = build_logits_k1_gpu(
                    cfg["plasticity"], E_full, idx_train_t, idx_held_t,
                    n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR, stdp_w=STDP_WEIGHT,
                    seed=seed, arm_idx=arm_idx, recall_batch=RECALL_BATCH,
                    ingest_chunk=INGEST_CHUNK,
                )
            else:
                # K=2 only supports cfrpe_stdp in this cell (cumulative-build)
                if cfg["plasticity"] != "cfrpe_stdp":
                    raise ValueError(
                        "K=2 arm %s requires plasticity=cfrpe_stdp; got %s" % (
                            arm, cfg["plasticity"]))
                ar = build_logits_k2_cfrpe_stdp_gpu(
                    E_full, idx_train_t, idx_held_t,
                    n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR, stdp_w=STDP_WEIGHT,
                    seed=seed, arm_idx=arm_idx, recall_batch=RECALL_BATCH,
                    gate_temp=GATE_TEMP, ingest_chunk=INGEST_CHUNK,
                )
            # Apply modern-Hopfield cleanup IF requested for this arm
            t_clean0 = time.time()
            if cfg["mh_cleanup"]:
                ar["logits"] = modern_hopfield_cleanup_gpu(
                    ar["logits"], E_full, beta=MH_BETA, n_iters=MH_ITERS,
                    recall_batch=RECALL_BATCH,
                )
            t_clean = time.time() - t_clean0
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
            }
            continue

        logits_full = ar["logits"]
        if logits_full.shape[0] >= len(ctx_full):
            logits_eval = logits_full[:len(ctx_full)][mask]
        else:
            valid_pos = np.where(mask)[0]
            valid_pos = valid_pos[valid_pos < logits_full.shape[0]]
            logits_eval = logits_full[valid_pos]
            nxt_eval_local = nxt_full[valid_pos]
            n_eval_l = len(nxt_eval_local)
            n_dev_l = n_eval_l // 2
            nxt_dev_l = nxt_eval_local[:n_dev_l]
            nxt_test_l = nxt_eval_local[n_dev_l:]
            jr = joint_sweep(logits_eval[:n_dev_l], logits_eval[n_dev_l:],
                              U_log, nxt_dev_l, nxt_test_l)
            rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval_local)
            jr.update({
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
                "wall_recall_s": ar.get("wall_recall_s", 0.0),
                "wall_cleanup_s": round(t_clean, 2),
                "raw_bpc_at_T1_L1": round(rbt1, 4),
                "mh_cleanup_applied": bool(cfg["mh_cleanup"]),
                "plasticity": cfg["plasticity"],
                "k_banks": int(cfg["k"]),
            })
            by_arm[arm] = jr
            print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f rawT1=%.3f elapsed=%.1fs" % (
                seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)
            continue

        jr = joint_sweep(logits_eval[:n_dev], logits_eval[n_dev:],
                         U_log, nxt_dev, nxt_test)
        rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval)
        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "wall_cleanup_s": round(t_clean, 2),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "mh_cleanup_applied": bool(cfg["mh_cleanup"]),
            "plasticity": cfg["plasticity"],
            "k_banks": int(cfg["k"]),
        })
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f rawT1=%.3f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
            jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)

    del E_full
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N_DIM_TOTAL": N_DIM_TOTAL,
        "N_DIM_PER_BANK": N_DIM_PER_BANK,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "N_STEPS": N_STEPS,
        "run_mode": RUN_MODE,
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "elapsed_s_seed": round(time.time() - t_seed, 2),
    }


# ============================================================================
# Verdict (per pre-reg bands)
# ============================================================================

def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}

    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
    }
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    arm_bpc: Dict[str, float] = {}
    arm_cv: Dict[str, float] = {}
    for arm in ARMS:
        valid = [u for u in units
                 if not u["by_arm"].get(arm, {}).get("compute_failed", False)
                 and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))]
        if not valid:
            by_arm_agg[arm] = {"bpc_best_mean": float("inf"), "n_valid_seeds": 0,
                               "all_seeds_failed": True}
            arm_bpc[arm] = float("inf")
            arm_cv[arm] = float("nan")
            continue
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid]
        raw_v = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "top1_acc_std": round(float(np.std(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_v)), 4),
            "n_valid_seeds": len(valid),
            "all_seeds_failed": False,
        }
        arm_bpc[arm] = b_mean
        arm_cv[arm] = b_cv

    # ARM_FULL_JOINT_COMPOSE is the load-bearing arm
    full_joint_bpc = arm_bpc.get("ARM_FULL_JOINT_COMPOSE", float("inf"))
    full_joint_cv = arm_cv.get("ARM_FULL_JOINT_COMPOSE", float("nan"))

    # Compute lifts vs the cumulative-prior arm (cumulative super-additivity probe)
    baseline_bpc = arm_bpc.get("ARM_BASELINE_fair_harness", float("inf"))
    cfrpe_bpc = arm_bpc.get("ARM_FAIR_HARNESS_PLUS_CFRPE", float("inf"))
    hetplast_bpc = arm_bpc.get("ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY", float("inf"))
    k2_bpc = arm_bpc.get(
        "ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY_PLUS_K2", float("inf"))

    lift_cfrpe_over_baseline = baseline_bpc - cfrpe_bpc
    lift_hetplast_over_cfrpe = cfrpe_bpc - hetplast_bpc
    lift_k2_over_hetplast = hetplast_bpc - k2_bpc
    lift_mh_over_k2 = k2_bpc - full_joint_bpc
    total_lift_over_baseline = baseline_bpc - full_joint_bpc

    # Provenance / sanity rails (each cumulative arm reproduces its reference)
    baseline_drift = abs(baseline_bpc - SANITY_RAIL_BASELINE_REF) if math.isfinite(baseline_bpc) else float("inf")
    cfrpe_drift = abs(cfrpe_bpc - SANITY_RAIL_CFRPE_REF) if math.isfinite(cfrpe_bpc) else float("inf")
    hetplast_drift = abs(hetplast_bpc - SANITY_RAIL_HETPLAST_REF) if math.isfinite(hetplast_bpc) else float("inf")

    baseline_rail_ok = baseline_drift <= SANITY_RAIL_TOLERANCE
    cfrpe_rail_ok = cfrpe_drift <= SANITY_RAIL_TOLERANCE
    hetplast_rail_ok = hetplast_drift <= SANITY_RAIL_TOLERANCE

    arm_summary = (
        "uni=%.3f | BASE=%.4f(drift=%+.4f,rail=%s) | +cfRPE=%.4f(drift=%+.4f,lift=%+.3f,rail=%s) | "
        "+hetPlast=%.4f(drift=%+.4f,lift=%+.3f,rail=%s) | +K2=%.4f(lift=%+.3f) | "
        "FULL_JOINT=%.4f(lift=%+.3f,cv=%.3f) | total_lift=%+.3f"
    ) % (
        unigram_bpc,
        baseline_bpc, baseline_bpc - SANITY_RAIL_BASELINE_REF, str(baseline_rail_ok),
        cfrpe_bpc, cfrpe_bpc - SANITY_RAIL_CFRPE_REF, lift_cfrpe_over_baseline, str(cfrpe_rail_ok),
        hetplast_bpc, hetplast_bpc - SANITY_RAIL_HETPLAST_REF, lift_hetplast_over_cfrpe, str(hetplast_rail_ok),
        k2_bpc, lift_k2_over_hetplast,
        full_joint_bpc, lift_mh_over_k2,
        full_joint_cv if math.isfinite(full_joint_cv) else -1.0,
        total_lift_over_baseline,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "lifts": {
            "cfrpe_over_baseline": round(lift_cfrpe_over_baseline, 4),
            "hetplast_over_cfrpe": round(lift_hetplast_over_cfrpe, 4),
            "k2_over_hetplast": round(lift_k2_over_hetplast, 4),
            "mh_over_k2": round(lift_mh_over_k2, 4),
            "total_full_joint_over_baseline": round(total_lift_over_baseline, 4),
        },
        "sanity_rails": {
            "baseline_ref": SANITY_RAIL_BASELINE_REF,
            "baseline_drift": round(baseline_drift, 4),
            "baseline_rail_ok": bool(baseline_rail_ok),
            "cfrpe_ref": SANITY_RAIL_CFRPE_REF,
            "cfrpe_drift": round(cfrpe_drift, 4),
            "cfrpe_rail_ok": bool(cfrpe_rail_ok),
            "hetplast_ref": SANITY_RAIL_HETPLAST_REF,
            "hetplast_drift": round(hetplast_drift, 4),
            "hetplast_rail_ok": bool(hetplast_rail_ok),
            "tolerance": SANITY_RAIL_TOLERANCE,
        },
        "bands": {
            "hard_pass_bpc_ceiling": HARD_PASS_BPC_CEILING,
            "middle_band_bpc_lower": MIDDLE_BAND_BPC_LOWER,
            "middle_band_bpc_upper": MIDDLE_BAND_BPC_UPPER,
            "hard_fail_bpc_floor": HARD_FAIL_BPC_FLOOR,
            "cv_max": CV_MAX,
        },
        "full_joint_bpc": round(full_joint_bpc, 4),
        "full_joint_cv": round(full_joint_cv, 4) if math.isfinite(full_joint_cv) else None,
        "n_seeds": len(units),
        "unigram_bpc": round(unigram_bpc, 4),
        "honest_scope": (
            "joint-compose of 5 chain-grade substrate primitives "
            "(Hebbian baseline + cf-RPE + STDP + K=2 multi-bank + modern-Hopfield cleanup) "
            "at production scale (N_DIM=8192, N_TRAIN=100k text8, V=4000, word2vec sparse-bipolar f=0.05). "
            "Tests super-additivity (joint BPC <= 6.85) vs additive (6.85-7.05) vs sub-additive (>=7.15). "
            "WHAT_THIS_DOES_NOT_SHOW: K>2 not tested; gate not end-to-end trained; "
            "modern-Hopfield cleanup acts on logits post-W, not on E directly; "
            "result at text8 V=4000 may not generalize to other corpora."
        ),
        "cites": [
            "notes/exp_dev_handoff_research_substrate_aliveness_FULL_store_mined_2026-06-24.md (A1 anchor)",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json (baseline rail 7.3065)",
            "data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json (cfRPE 7.1052 / hetPlast 7.1654)",
            "data/exp_modern_hopfield_n_sweep_v1/metrics.json (modern-Hopfield row 100)",
            "experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py (encoder + K2 base)",
        ],
    }

    # Substrate-only audit gate
    total_llm_calls = sum(int(u.get("llm_forward_calls_at_inference", 0)) for u in units)
    detail["llm_forward_calls_total"] = total_llm_calls
    if total_llm_calls != 0:
        return ("HARD_FAIL",
                "HARD_FAIL_LLM_CALL: llm_calls=%d (substrate-only invariant). %s" % (
                    total_llm_calls, arm_summary),
                detail)

    full_joint_failed = by_arm_agg.get("ARM_FULL_JOINT_COMPOSE", {}).get("all_seeds_failed", True)
    if full_joint_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_FULL_JOINT_COMPOSE all seeds failed. %s" % arm_summary,
                detail)

    # Provenance rails only fire in run_mode=full (smoke uses synthetic scale; refs don't apply)
    detail["provenance_check_active"] = (RUN_MODE == "full")
    if RUN_MODE == "full":
        if not baseline_rail_ok:
            return ("HARD_FAIL_PROVENANCE",
                    "HARD_FAIL_PROVENANCE_BASELINE: ARM_BASELINE_fair_harness=%.4f drifts %.4f "
                    "from fair_harness ref %.4f (>tol %.2f). Encoder/Hebbian pipeline mismatch. %s" % (
                        baseline_bpc, baseline_drift, SANITY_RAIL_BASELINE_REF,
                        SANITY_RAIL_TOLERANCE, arm_summary),
                    detail)
        if not cfrpe_rail_ok:
            return ("HARD_FAIL_PROVENANCE",
                    "HARD_FAIL_PROVENANCE_CFRPE: ARM_FAIR_HARNESS_PLUS_CFRPE=%.4f drifts %.4f "
                    "from cfRPE ref %.4f (>tol %.2f). cf-RPE primitive mismatch. %s" % (
                        cfrpe_bpc, cfrpe_drift, SANITY_RAIL_CFRPE_REF,
                        SANITY_RAIL_TOLERANCE, arm_summary),
                    detail)
        if not hetplast_rail_ok:
            return ("HARD_FAIL_PROVENANCE",
                    "HARD_FAIL_PROVENANCE_HETPLAST: ARM_..._PLUS_HETPLASTICITY=%.4f drifts %.4f "
                    "from het-plast ref %.4f (>tol %.2f). STDP primitive mismatch. %s" % (
                        hetplast_bpc, hetplast_drift, SANITY_RAIL_HETPLAST_REF,
                        SANITY_RAIL_TOLERANCE, arm_summary),
                    detail)

    # cv gate on the load-bearing arm
    if math.isfinite(full_joint_cv) and full_joint_cv > CV_MAX:
        return ("MIDDLE_BAND_HIGH_CV",
                "MIDDLE_BAND_HIGH_CV: ARM_FULL_JOINT_COMPOSE cv=%.3f > %.2f mandatory. "
                "full_joint_bpc=%.4f. %s" % (
                    full_joint_cv, CV_MAX, full_joint_bpc, arm_summary),
                detail)

    # Joint-compose verdict bands
    if math.isfinite(full_joint_bpc) and full_joint_bpc <= HARD_PASS_BPC_CEILING:
        detail["verdict_tier"] = "HARD_PASS_SUPER_ADDITIVE"
        return ("HARD_PASS",
                "HARD_PASS SUPER_ADDITIVE: ARM_FULL_JOINT_COMPOSE BPC=%.4f <= %.3f "
                "(substrate clears bigram-floor regime). 5-primitive compose super-additive. "
                "Total lift over baseline = %+.3f. %s" % (
                    full_joint_bpc, HARD_PASS_BPC_CEILING, total_lift_over_baseline,
                    arm_summary),
                detail)

    if math.isfinite(full_joint_bpc) and MIDDLE_BAND_BPC_LOWER <= full_joint_bpc <= MIDDLE_BAND_BPC_UPPER:
        detail["verdict_tier"] = "MIDDLE_BAND_ADDITIVE"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_ADDITIVE: ARM_FULL_JOINT_COMPOSE BPC=%.4f in [%.2f, %.2f] "
                "(additive but not super-additive). Substrate envelope at +%.3f over baseline. %s" % (
                    full_joint_bpc, MIDDLE_BAND_BPC_LOWER, MIDDLE_BAND_BPC_UPPER,
                    total_lift_over_baseline, arm_summary),
                detail)

    if math.isfinite(full_joint_bpc) and full_joint_bpc >= HARD_FAIL_BPC_FLOOR:
        detail["verdict_tier"] = "HARD_FAIL_SUB_ADDITIVE"
        return ("HARD_FAIL",
                "HARD_FAIL_SUB_ADDITIVE: ARM_FULL_JOINT_COMPOSE BPC=%.4f >= %.2f "
                "(collapses to single-knob best; compose-saturation). Substrate has alive "
                "PRIMITIVES but no compose-stacking - architectural rethink needed. %s" % (
                    full_joint_bpc, HARD_FAIL_BPC_FLOOR, arm_summary),
                detail)

    # Else: BPC in (MIDDLE_BAND_BPC_UPPER, HARD_FAIL_BPC_FLOOR) -> still MIDDLE_BAND (between bands)
    detail["verdict_tier"] = "MIDDLE_BAND_INTER_GAP"
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_INTER_GAP: ARM_FULL_JOINT_COMPOSE BPC=%.4f between MB ceiling %.2f "
            "and HARD_FAIL floor %.2f. Marginal sub-additive compose. %s" % (
                full_joint_bpc, MIDDLE_BAND_BPC_UPPER, HARD_FAIL_BPC_FLOOR, arm_summary),
            detail)


# ============================================================================
# Main loop with per-seed checkpoint
# ============================================================================

print("[config] %s" % CONFIG_VERSION, flush=True)
print("[config] device=%s torch_cuda_available=%s" % (str(DEVICE), torch.cuda.is_available()),
      flush=True)

out_dir = get_output_dir(ANCHOR_NAME)

done_seeds_init: List[int] = []
remaining_seeds_init: List[int] = SEEDS[:]
try:
    done_seeds_init, remaining_seeds_init = _resumable_seeds(SEEDS, out_dir)
    print("[ckpt] %d done, %d remaining: %s" % (
        len(done_seeds_init), len(remaining_seeds_init), remaining_seeds_init), flush=True)
except Exception as e:
    print("[ckpt] resumable_seeds failed (%s); running all seeds" % e, flush=True)
    remaining_seeds_init = SEEDS[:]

for seed in remaining_seeds_init:
    print("\n[run] seed=%d starting..." % seed, flush=True)
    result = run_unit(seed)
    write_partial(out_dir, seed, result)
    print("[ckpt] seed=%d partial written to %s" % (seed, out_dir), flush=True)

per_seed = aggregate_partials(out_dir, SEEDS)
all_units = list(per_seed.values())

verdict, verdict_msg, detail = compute_verdict(all_units)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

# REQUIRED_FIELDS: verdict, verdict_msg, elapsed_s, summary
summary_str = (
    "%s | arms=%d seeds=%d N_DIM=%d N_TRAIN=%d encoder=word2vec_sparse_bipolar mh_beta=%.2f mh_iters=%d" % (
        verdict, len(ARMS), len(SEEDS), N_DIM_TOTAL, N_TRAIN, MH_BETA, MH_ITERS)
)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": summary_str,
    "config_version": CONFIG_VERSION,
    "run_mode": RUN_MODE,
    "device": str(DEVICE),
    "N_DIM_TOTAL": N_DIM_TOTAL,
    "N_DIM_PER_BANK": N_DIM_PER_BANK,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "N_STEPS": N_STEPS,
    "K_BANKS": K_BANKS,
    "GATE_TEMP": GATE_TEMP,
    "CFRPE_LR": CFRPE_LR,
    "STDP_WEIGHT": STDP_WEIGHT,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "MH_BETA": MH_BETA,
    "MH_ITERS": MH_ITERS,
    "TEMP_GRID": TEMP_GRID,
    "LAMBDA_GRID": LAMBDA_GRID,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "detail": detail,
    "per_seed": [
        {"seed": u.get("seed"), "by_arm": u.get("by_arm"),
         "V": u.get("V"), "N_DIM_TOTAL": u.get("N_DIM_TOTAL"),
         "N_TRAIN": u.get("N_TRAIN"),
         "llm_forward_calls_at_inference": u.get("llm_forward_calls_at_inference", 0),
         "encoder_meta": u.get("encoder_meta", {}),
         "elapsed_s_seed": u.get("elapsed_s_seed")}
        for u in all_units
    ],
    "elapsed_s": round(sum(u.get("elapsed_s_seed", 0.0) for u in all_units), 2),
}

if DEVICE.type == "cuda":
    try:
        peak_gb = torch.cuda.max_memory_allocated(0) / 1e9
        print("[gpu] peak memory %.3f GB" % peak_gb, flush=True)
        metrics["gpu_peak_mem_gb"] = round(peak_gb, 3)
    except Exception:
        pass

write_metrics(out_dir, metrics, all_units)
print("[metrics] written to %s" % out_dir, flush=True)
