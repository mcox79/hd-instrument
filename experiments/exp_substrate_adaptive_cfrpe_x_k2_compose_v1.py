"""
substrate_adaptive_cfrpe_x_k2_compose_v1 -- ADAPTIVE cf-RPE x K=2 multi-bank compose.

STRATEGIC RATIONALE: A1 joint-compose just HARD_FAILed with UNIFORM cf-RPE
(composition sub-additive). But A3 per-token ADAPTIVE cf-RPE achieved 6.9920 BPC
(new substrate-as-LM single-arm record). HYPOTHESIS: per-token weighting may make
composition NON-INTERFERING (the adaptive LR routes plasticity to high-error
samples, which may not all be in the same bank's "expertise" region).

PRIOR RESULTS BEING REPLICATED + EXTENDED:
  A1 K=2 x UNIFORM cf-RPE compose: 7.2690 < cf-RPE alone 7.1540 (SUB-ADDITIVE)
  A3 per-token ADAPTIVE cf-RPE @ K=1: 6.9920 (single-arm best, +0.08 over coarse)
  K=2 single-bank rank-1 Hebbian:    7.3325 (provenance reference)
  ARM_BASELINE_RANK1_K1 Hebbian:     7.3065 (fair_harness chain-grade rail)

FOUR ARMS:
  ARM_BASELINE_RANK1_K1_HEBBIAN -- single bank rank-1 Hebbian; sanity rail 7.3065
  ARM_ADAPTIVE_CFRPE_K1         -- per-token adaptive cf-RPE @ K=1 (A3 reference 6.9920)
  ARM_K2_RANK1_HEBBIAN          -- K=2 rank-1 Hebbian (provenance vs 7.3325)
  ARM_K2_ADAPTIVE_CFRPE         -- THE TEST: K=2 banks each running adaptive cf-RPE

PRE-REG HARD BANDS:
  Sanity rails (Fix #28 per-arm):
    ARM_BASELINE_RANK1_K1_HEBBIAN within +/-0.05 of 7.3065
    ARM_ADAPTIVE_CFRPE_K1        within +/-0.05 of 6.9920 (A3 reproduction)
    ARM_K2_RANK1_HEBBIAN         within +/-0.05 of 7.3325
  HARD_PASS chain-grade-eligible: ARM_K2_ADAPTIVE_CFRPE BPC <= 6.80
                                  AND beats ARM_ADAPTIVE_CFRPE_K1 by >= +0.10 (super-additive)
  MIDDLE_BAND: ARM_K2_ADAPTIVE_CFRPE BPC in [6.80, 6.95] (additive but not super-additive)
  HARD_FAIL: ARM_K2_ADAPTIVE_CFRPE BPC >= 6.99 (no compose benefit from K=2)
  cv < 0.05 across seeds

ADAPTIVE cf-RPE rule (from A3, EXACT match):
  error[i]   = Nxt[i] - Ctx[i] @ W.T            # [batch, dim]
  e_norm[i]  = ||error[i]|| / sqrt(dim)          # per-sample RMS error (scalar)
  med        = median(e_norm) (+ eps)
  lr_per[i]  = base_lr * clamp(e_norm[i] / med, FLOOR=0.25, CEIL=4.0)
  dW         = (error * lr_per).T @ Ctx / batch
  W         += dW

K=2 multi-bank routing (from K2_v2, EXACT match):
  Bank slices: E_banks[k] = E_full[:, k*N_per:(k+1)*N_per]
  Gate signal: probs = softmax(E_banks[0] @ W_gate.T / GATE_TEMP) over K banks
  Per-bank update: gate-weighted cf-RPE step on the bank's slice
  Recall: gate-weighted sum of bank-prediction cosine similarities

K=2 x ADAPTIVE composition (the new compound rule):
  For each step + each bank:
    error_k = Nxt_k - Ctx_k @ W_k.T          # per-bank prediction error
    e_norm_k= ||error_k|| / sqrt(N_per)       # per-bank per-sample RMS
    med_k   = median(e_norm_k)
    lr_per_k= base_lr * clamp(e_norm_k / med_k, FLOOR, CEIL)
    gw_k    = probs[:, k:k+1]                 # bank-k gate weight (scalar per sample)
    dW_k    = ((error_k * gw_k * lr_per_k[:,None]).T @ Ctx_k) / batch
  Each bank gets ADAPTIVE per-token weighting AND gate-weighted routing.

ENCODING: word2vec-google-news-300 projected to N_DIM=8192 sparse-bipolar (f=0.05);
  same encoder as fair_harness baseline (BPC 7.3065 chain-grade).

EXECUTION: overnight_queue (GPU); torch.cuda matmul; Fix #24 GPU dispatch.
  N_DIM_TOTAL=8192 (4096/bank), 3 seeds, N_TRAIN=100k text8 (4hr-est for FULL).

ASCII-only. Fix #14 ONE cell. Fix #26 predispatch_check PROCEED.
Fix #28 per-arm metrics propagation. Fix #24 torch.cuda + batched ops on GPU.

Cites:
  preregs/2026-06-24_substrate_adaptive_cfrpe_x_k2_compose_v1.md
  experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py (A3 6.9920 BPC; ADAPTIVE rule)
  experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py (K=2 routing pattern)
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json (7.3065 baseline)
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

ANCHOR_NAME = "substrate_adaptive_cfrpe_x_k2_compose_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Substrate-only audit
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Pre-reg threshold bands (locked; do NOT modify post-smoke)
# ============================================================================
# Sanity rail references (Fix #28: per-arm; from prior chain-grade landings)
HEBBIAN_K1_BPC_REF = 7.3065        # ARM_BASELINE_RANK1_K1_HEBBIAN provenance
ADAPTIVE_K1_BPC_REF = 6.9920       # ARM_ADAPTIVE_CFRPE_K1 (A3 single-arm best)
HEBBIAN_K2_BPC_REF = 7.3325        # ARM_K2_RANK1_HEBBIAN (prior K=2 Hebbian)
SANITY_TOL = 0.05

# Primary verdict bands on ARM_K2_ADAPTIVE_CFRPE
HARD_PASS_BPC_BAR = 6.80           # chain-grade-eligible: BPC <= this
HARD_PASS_LIFT_OVER_ADAPTIVE_K1 = 0.10  # super-additive: K2_ADAPTIVE beats ADAPTIVE_K1 by >=+0.10
MIDDLE_BAND_BPC_LOW = 6.80         # MB in [6.80, 6.95]
MIDDLE_BAND_BPC_HIGH = 6.95
HARD_FAIL_BPC_FLOOR = 6.99         # HARD_FAIL if K2_ADAPTIVE >= this
CV_MAX = 0.05

# ============================================================================
# Plasticity knob parameters (EXACT from A3 + K2_v2 heritage)
# ============================================================================
CFRPE_LR = 0.5
INGEST_BATCH = 64
SPARSE_BIPOLAR_F = 0.05
PRETRAIN_DIM = 300

# Per-token adaptive controls (EXACT match to A3)
ADAPT_LR_FLOOR = 0.25
ADAPT_LR_CEIL = 4.0

# K-bank routing controls (EXACT match to K2_v2)
K_BANKS = 2
GATE_TEMP = 0.5

# Inference grids (C7 META: LAMBDA_GRID excludes 0.0)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# ============================================================================
# CLI / run-mode (default FULL per [[reference_remote_dispatch...]] item 4)
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
# Production / smoke config
# ============================================================================
N_DIM_TOTAL = 8192
N_DIM_PER_BANK = N_DIM_TOTAL // K_BANKS   # 4096 per bank
VOCAB_CAP = 4000
RECALL_BATCH = 256
INGEST_CHUNK = 4096
N_STEPS_PER_SEED = 5000   # A3 reference: 5000 cf-RPE steps (matches A3 COARSE_N_STEPS)

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = N_STEPS_PER_SEED
else:
    # Smoke: must fit under 180s on the laptop CPU (queue_add SMOKE_TIMEOUT_S).
    # Exercises every arm + word2vec encoder + joint sweep + verdict bands.
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM_TOTAL = 1024
    N_DIM_PER_BANK = N_DIM_TOTAL // K_BANKS
    N_STEPS = 80
    RECALL_BATCH = 128
    INGEST_CHUNK = 512

CONFIG_VERSION = (
    "substrate_adaptive_cfrpe_x_k2_compose_v1; encoder=word2vec_sparse_bipolar; "
    "N_DIM_TOTAL=%d K_BANKS=%d N_DIM_PER_BANK=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
    "seeds=%s mode=%s temps=%s lambdas=%s sparse_f=%.3f cfrpe_lr=%.3f "
    "adapt_floor=%.2f adapt_ceil=%.2f gate_temp=%.3f n_steps=%d batch=%d device=%s"
) % (
    N_DIM_TOTAL, K_BANKS, N_DIM_PER_BANK, N_TRAIN, N_HELD, VOCAB_CAP,
    SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID, SPARSE_BIPOLAR_F, CFRPE_LR,
    ADAPT_LR_FLOOR, ADAPT_LR_CEIL, GATE_TEMP, N_STEPS, INGEST_BATCH, str(DEVICE),
)

ARMS = [
    "ARM_BASELINE_RANK1_K1_HEBBIAN",
    "ARM_ADAPTIVE_CFRPE_K1",
    "ARM_K2_RANK1_HEBBIAN",
    "ARM_K2_ADAPTIVE_CFRPE",
]


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
# Encoder: word2vec-projected sparse-bipolar (MATCHES fair_harness chain-grade)
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
    """Build [V, n_dim] L2-normalized word2vec-projected vectors on DEVICE.

    word2vec(300) -> Gaussian-project(300 -> n_dim) -> L2 normalize.
    OOV: char-trigram fallback.
    """
    try:
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
                "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size),
                "encoder_class": "word2vec_gaussian_projected"}
        return E_t, meta
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[encoder] WORD2VEC LOAD FAIL: %s -- falling back to char-trigram" % err,
              flush=True)
        E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
        E_np = _l2_normalize_np(E_np)
        E_t = torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)
        meta = {"n_hit": 0, "n_miss": int(len(vocab)),
                "n_vocab": int(len(vocab)), "pretrain_dim": 0,
                "encoder_class": "char_trigram_fallback",
                "fallback_reason": err}
        return E_t, meta


def sparsify_bipolar_gpu(E: torch.Tensor, f: float) -> torch.Tensor:
    """Sparse-bipolar projection: keep top-k by abs magnitude, set sign."""
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
# Plasticity rules
# ============================================================================

def build_W_rank1_hebbian_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                               ingest_chunk: int) -> torch.Tensor:
    """One-pass batched outer-product rank-1 Hebbian on a single bank."""
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


def build_W_cfrpe_per_token_adaptive_k1(E: torch.Tensor, idx_train_t: torch.Tensor,
                                          n_steps: int, batch: int, base_lr: float,
                                          gen: torch.Generator) -> Tuple[torch.Tensor, Dict]:
    """Per-token adaptive cf-RPE on a single bank (K=1). EXACT match to A3.

    error[i]   = Nxt[i] - Ctx[i] @ W.T
    e_norm[i]  = ||error[i]|| / sqrt(dim)
    lr_per[i]  = base_lr * clamp(e_norm[i] / median(e_norm), FLOOR, CEIL)
    dW         = (error * lr_per).T @ Ctx / batch
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W, {"per_token_lr_max_min_ratio_max": 1.0, "n_clamped_steps": 0,
                    "final_batch_mean_err": float("nan")}
    sqrt_dim = math.sqrt(float(dim))
    max_min_ratio_max = 1.0
    n_clamped_steps = 0
    last_mean_err = float("nan")
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E[idx_train_t[st]]
        Nxt = E[idx_train_t[st + 1]]
        error = Nxt - Ctx @ W.T
        e_norm = error.norm(dim=1) / sqrt_dim
        med = float(torch.median(e_norm))
        med_safe = med if med > 1e-8 else 1e-8
        ratio = e_norm / med_safe
        ratio_clamped = torch.clamp(ratio, min=ADAPT_LR_FLOOR, max=ADAPT_LR_CEIL)
        if bool(((ratio < ADAPT_LR_FLOOR) | (ratio > ADAPT_LR_CEIL)).any()):
            n_clamped_steps += 1
        lr_per = base_lr * ratio_clamped
        weighted_error = error * lr_per.unsqueeze(1)
        dW = (weighted_error.T @ Ctx) / float(batch)
        W = W + dW
        cur_ratio = float(ratio_clamped.max() / max(float(ratio_clamped.min()), 1e-8))
        if cur_ratio > max_min_ratio_max:
            max_min_ratio_max = cur_ratio
        last_mean_err = float(e_norm.mean())
    return W, {
        "per_token_lr_max_min_ratio_max": round(max_min_ratio_max, 4),
        "n_clamped_steps": int(n_clamped_steps),
        "final_batch_mean_err": round(last_mean_err, 6) if math.isfinite(last_mean_err) else None,
    }


# ============================================================================
# K=1 / K=2 logits builders
# ============================================================================

def build_logits_k1_hebbian(E_full: torch.Tensor, idx_train_t: torch.Tensor,
                              idx_held_t: torch.Tensor,
                              recall_batch: int, ingest_chunk: int) -> Dict:
    """K=1 rank-1 Hebbian: W = sum E_tgt^T @ E_src; recall = cos(E[held]@W.T, E)."""
    device = E_full.device
    V = E_full.shape[0]
    t0 = time.time()
    W = build_W_rank1_hebbian_gpu(E_full, idx_train_t, ingest_chunk)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    n_h = idx_held_t.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred = _l2_normalize_t(ctx_b @ W.T)
        logits[b:end] = pred @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np,
            "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
            "diag": {}}


def build_logits_k1_adaptive_cfrpe(E_full: torch.Tensor, idx_train_t: torch.Tensor,
                                     idx_held_t: torch.Tensor, n_steps: int,
                                     batch: int, lr: float, seed: int, arm_idx: int,
                                     recall_batch: int) -> Dict:
    """K=1 per-token adaptive cf-RPE."""
    device = E_full.device
    V = E_full.shape[0]
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    t0 = time.time()
    W, diag = build_W_cfrpe_per_token_adaptive_k1(
        E_full, idx_train_t, n_steps=n_steps, batch=batch, base_lr=lr, gen=gen)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    n_h = idx_held_t.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred = _l2_normalize_t(ctx_b @ W.T)
        logits[b:end] = pred @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np,
            "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
            "diag": diag}


def build_logits_k2_hebbian(E_full: torch.Tensor, idx_train_t: torch.Tensor,
                              idx_held_t: torch.Tensor,
                              recall_batch: int, gate_temp: float,
                              ingest_chunk: int, seed: int, arm_idx: int) -> Dict:
    """K=2 multi-bank rank-1 Hebbian with soft-gate routing (K2_v2 pattern)."""
    device = E_full.device
    V, n_dim = E_full.shape
    K = K_BANKS
    N_per = n_dim // K

    E_banks = [E_full[:, k * N_per:(k + 1) * N_per].contiguous() for k in range(K)]
    rng_gate = np.random.default_rng(seed * 7919 + arm_idx * 1013 + 9999)
    W_gate_np = rng_gate.standard_normal((K, N_per)).astype(np.float32)
    W_gate_np /= np.linalg.norm(W_gate_np, axis=1, keepdims=True) + 1e-9
    W_gate = torch.from_numpy(W_gate_np).to(device=device, dtype=TORCH_DTYPE)

    W_banks = [torch.zeros((N_per, N_per), dtype=TORCH_DTYPE, device=device)
               for _ in range(K)]

    t0 = time.time()
    n_pairs = idx_train_t.shape[0] - 1
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train_t[b:end]
        tgt_idx = idx_train_t[b + 1:end + 1]
        gate_inputs = E_banks[0][src_idx]
        raw = gate_inputs @ W_gate.T
        raw = raw / gate_temp
        raw = raw - raw.max(dim=1, keepdim=True).values
        probs = torch.exp(raw)
        probs = probs / (probs.sum(dim=1, keepdim=True) + 1e-30)
        for k in range(K):
            E_src_k = E_banks[k][src_idx]
            E_tgt_k = E_banks[k][tgt_idx]
            gw = probs[:, k:k + 1]
            W_banks[k].add_((E_tgt_k * gw).T @ E_src_k)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

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
    del E_banks, W_banks, W_gate, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np,
            "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
            "diag": {}}


def build_logits_k2_adaptive_cfrpe(E_full: torch.Tensor, idx_train_t: torch.Tensor,
                                      idx_held_t: torch.Tensor, n_steps: int,
                                      batch: int, lr: float,
                                      recall_batch: int, gate_temp: float,
                                      seed: int, arm_idx: int) -> Dict:
    """K=2 multi-bank x per-token adaptive cf-RPE compose (THE TEST ARM).

    For each step:
      sample batch of (Ctx, Nxt) index pairs
      gate_inputs = E_banks[0][st]
      probs       = softmax(gate_inputs @ W_gate.T / GATE_TEMP)        # [batch, K]
      For each bank k:
        Ctx_k = E_banks[k][st]; Nxt_k = E_banks[k][st+1]
        error_k = Nxt_k - Ctx_k @ W_banks[k].T                          # [batch, N_per]
        e_norm_k= ||error_k|| / sqrt(N_per)
        med_k   = median(e_norm_k); ratio_k = clamp(e_norm_k/med_k, FLOOR, CEIL)
        lr_per_k= lr * ratio_k                                          # [batch]
        gw_k    = probs[:, k:k+1]                                       # [batch, 1]
        dW_k    = ((error_k * gw_k * lr_per_k[:,None]).T @ Ctx_k) / batch
        W_banks[k] += dW_k
    """
    device = E_full.device
    V, n_dim = E_full.shape
    K = K_BANKS
    N_per = n_dim // K
    sqrt_n_per = math.sqrt(float(N_per))

    E_banks = [E_full[:, k * N_per:(k + 1) * N_per].contiguous() for k in range(K)]
    rng_gate = np.random.default_rng(seed * 7919 + arm_idx * 1013 + 9999)
    W_gate_np = rng_gate.standard_normal((K, N_per)).astype(np.float32)
    W_gate_np /= np.linalg.norm(W_gate_np, axis=1, keepdims=True) + 1e-9
    W_gate = torch.from_numpy(W_gate_np).to(device=device, dtype=TORCH_DTYPE)

    W_banks = [torch.zeros((N_per, N_per), dtype=TORCH_DTYPE, device=device)
               for _ in range(K)]

    n_pairs = idx_train_t.shape[0] - 1
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    # Track per-bank adaptive diagnostics
    per_bank_diag: Dict[int, Dict] = {k: {"max_min_ratio_max": 1.0,
                                            "n_clamped_steps": 0,
                                            "final_batch_mean_err": float("nan")}
                                       for k in range(K)}

    t0 = time.time()
    if n_pairs > 0:
        for step in range(n_steps):
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
                error_k = Nxt_k - Ctx_k @ W_banks[k].T
                e_norm_k = error_k.norm(dim=1) / sqrt_n_per
                med_k = float(torch.median(e_norm_k))
                med_safe_k = med_k if med_k > 1e-8 else 1e-8
                ratio_k = e_norm_k / med_safe_k
                ratio_clamped_k = torch.clamp(ratio_k, min=ADAPT_LR_FLOOR, max=ADAPT_LR_CEIL)
                if bool(((ratio_k < ADAPT_LR_FLOOR) | (ratio_k > ADAPT_LR_CEIL)).any()):
                    per_bank_diag[k]["n_clamped_steps"] += 1
                lr_per_k = lr * ratio_clamped_k                  # [batch]
                gw_k = probs_b[:, k:k + 1]                       # [batch, 1]
                # Combine adaptive LR (per-sample scalar) AND gate weight
                weighted_error_k = error_k * gw_k * lr_per_k.unsqueeze(1)
                dW_k = (weighted_error_k.T @ Ctx_k) / float(batch)
                W_banks[k] = W_banks[k] + dW_k
                cur_ratio = float(ratio_clamped_k.max()
                                    / max(float(ratio_clamped_k.min()), 1e-8))
                if cur_ratio > per_bank_diag[k]["max_min_ratio_max"]:
                    per_bank_diag[k]["max_min_ratio_max"] = cur_ratio
                per_bank_diag[k]["final_batch_mean_err"] = float(e_norm_k.mean())
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

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

    # Round diagnostic floats for JSON cleanliness
    diag_clean = {}
    for k, d in per_bank_diag.items():
        diag_clean["bank_%d_max_min_ratio_max" % k] = round(d["max_min_ratio_max"], 4)
        diag_clean["bank_%d_n_clamped_steps" % k] = int(d["n_clamped_steps"])
        fbe = d["final_batch_mean_err"]
        diag_clean["bank_%d_final_batch_mean_err" % k] = (
            round(fbe, 6) if math.isfinite(fbe) else None)

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del E_banks, W_banks, W_gate, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np,
            "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
            "diag": diag_clean}


# ============================================================================
# BPC / eval utilities
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
    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}

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

    def _eval_test(T: float, lam: float, fn) -> float:
        probs = softmax_with_T(sub_logits_test, T)
        logp_sub = np.log(np.clip(probs, 1e-30, 1.0))
        logp = log_linear_interp(logp_sub, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _eval_test(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _eval_test(best_top1["T"], best_top1["lambda"], top1_acc)
    mrr_best_test = _eval_test(best_mrr["T"], best_mrr["lambda"],
                                lambda lp, nx: mrr_at_k(lp, nx, MRR_K))

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
# Instrumentation self-test (MANDATORY; verify mechanism + ordering INVARIANTS)
# ============================================================================

def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)

    # ST1: cf-RPE rule shrinks single-pair prediction error
    n_dim_st = 64
    Ctx1 = torch.randn(1, n_dim_st, device=DEVICE)
    Nxt1 = torch.randn(1, n_dim_st, device=DEVICE)
    Ctx1 = Ctx1 / (Ctx1.norm() + 1e-8)
    Nxt1 = Nxt1 / (Nxt1.norm() + 1e-8)
    W1 = torch.zeros(n_dim_st, n_dim_st, device=DEVICE)
    err_before = float((Nxt1 - Ctx1 @ W1.T).norm())
    dW1 = (Nxt1 - Ctx1 @ W1.T).T @ Ctx1
    W1 = W1 + 0.9 * dW1
    err_after = float((Nxt1 - Ctx1 @ W1.T).norm())
    assert err_after < err_before, "ST1 cf-RPE failed to shrink error"
    print("[selftest] ST1 cf-RPE shrinks error: %.4f -> %.4f" % (err_before, err_after), flush=True)

    # ST2: per-token LR ORDERING (high-error sample gets higher LR than low-error sample)
    b_st = 4
    Ctx3 = torch.randn(b_st, n_dim_st, device=DEVICE)
    Ctx3 = _l2_normalize_t(Ctx3)
    Nxt3 = torch.randn(b_st, n_dim_st, device=DEVICE)
    Nxt3 = _l2_normalize_t(Nxt3)
    Nxt3[0] = Nxt3[0] * 5.0    # high-error
    Nxt3[3] = Nxt3[3] * 0.2    # low-error
    W3 = torch.zeros(n_dim_st, n_dim_st, device=DEVICE)
    error3 = Nxt3 - Ctx3 @ W3.T
    sqrt_dim = math.sqrt(float(n_dim_st))
    e_norm3 = error3.norm(dim=1) / sqrt_dim
    med3 = float(torch.median(e_norm3))
    ratio3 = e_norm3 / max(med3, 1e-8)
    ratio_clamped3 = torch.clamp(ratio3, min=ADAPT_LR_FLOOR, max=ADAPT_LR_CEIL)
    assert float(ratio_clamped3[0]) > float(ratio_clamped3[3]), (
        "ST2 per-token LR ordering wrong: high=%.3f low=%.3f" % (
            float(ratio_clamped3[0]), float(ratio_clamped3[3])))
    print("[selftest] ST2 per-token LR ordering OK (high=%.3f low=%.3f)" % (
        float(ratio_clamped3[0]), float(ratio_clamped3[3])), flush=True)

    # ST3: gate-softmax probs sum to 1 across K banks
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
        "ST3 gate probs sum != 1: %.6f" % float(probs_st.sum()))
    assert (probs_st >= 0).all().item(), "ST3 gate probs contain negative"
    print("[selftest] ST3 gate probs sum=%.6f OK" % float(probs_st.sum()), flush=True)

    # ST4: K=1 adaptive cf-RPE produces non-zero W norm
    V_st = 10
    n_dim_s2 = 128
    rng3 = np.random.default_rng(0)
    E_np = rng3.standard_normal((V_st, n_dim_s2)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(DEVICE)
    E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F))
    idx_tr_st = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=torch.long, device=DEVICE)
    idx_h_st = torch.tensor([3, 4, 5, 6], dtype=torch.long, device=DEVICE)
    gen_st = torch.Generator(device=DEVICE); gen_st.manual_seed(7)
    W_ad, diag_ad = build_W_cfrpe_per_token_adaptive_k1(
        E_sb, idx_tr_st, n_steps=10, batch=3, base_lr=0.5, gen=gen_st)
    assert float(W_ad.norm()) > 1e-6, "ST4 adaptive K=1 W zero"
    assert "per_token_lr_max_min_ratio_max" in diag_ad, "ST4 diag missing key"
    print("[selftest] ST4 adaptive K=1 W norm=%.4f max/min ratio=%.4f OK" % (
        float(W_ad.norm()), diag_ad["per_token_lr_max_min_ratio_max"]), flush=True)

    # ST5: K=1 vs K=2 ADAPTIVE differ (architecture difference must produce different logits)
    ar_k1 = build_logits_k1_adaptive_cfrpe(
        E_sb, idx_tr_st, idx_h_st, n_steps=5, batch=3, lr=0.5, seed=0, arm_idx=0,
        recall_batch=4)
    ar_k2 = build_logits_k2_adaptive_cfrpe(
        E_sb, idx_tr_st, idx_h_st, n_steps=5, batch=3, lr=0.5,
        recall_batch=4, gate_temp=GATE_TEMP, seed=0, arm_idx=1)
    diff_st = float(np.abs(ar_k1["logits"] - ar_k2["logits"]).mean())
    assert diff_st > 1e-6, "ST5 K=1 vs K=2 adaptive logits identical (architecture is null)"
    print("[selftest] ST5 K=1 vs K=2 adaptive logits differ (mean_abs=%.4e) OK" % diff_st,
          flush=True)

    # ST6: K=2 adaptive diagnostics carry per-bank fields
    diag_k2 = ar_k2["diag"]
    assert "bank_0_max_min_ratio_max" in diag_k2 and "bank_1_max_min_ratio_max" in diag_k2, (
        "ST6 K=2 diag missing per-bank fields")
    print("[selftest] ST6 K=2 diag per-bank fields present OK", flush=True)

    # ST7: joint_sweep returns finite metrics
    n_tok_st = 30
    n_v_sm = 6
    rng6 = np.random.default_rng(99)
    logits_syn = rng6.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_syn = rng6.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_log_st = np.log(np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32))
    nd = n_tok_st // 2
    jr = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                     nxt_syn[:nd], nxt_syn[nd:])
    assert math.isfinite(jr["bpc_best"]) and math.isfinite(jr["top1_acc"]), "ST7 joint_sweep nan"
    print("[selftest] ST7 joint_sweep OK (bpc=%.3f top1=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"]), flush=True)

    # ST8: sparsify_bipolar_gpu correct fraction nonzero
    E_chk = torch.from_numpy(np.random.default_rng(0).standard_normal((20, 100)).astype(np.float32)).to(DEVICE)
    E_sparse = sparsify_bipolar_gpu(E_chk, 0.05)
    nnz_per_row = (E_sparse != 0).sum(dim=1).cpu().numpy()
    expected_nnz = max(1, int(round(0.05 * 100)))
    assert bool((nnz_per_row == expected_nnz).all()), "ST8 sparse nnz mismatch"
    print("[selftest] ST8 sparsify_bipolar_gpu nnz=%d OK" % expected_nnz, flush=True)

    # ST9: C7 META compliance — LAMBDA_GRID excludes 0.0
    assert 0.0 not in LAMBDA_GRID, "ST9 LAMBDA_GRID must exclude 0.0 (C7 META)"
    print("[selftest] ST9 LAMBDA_GRID excludes 0.0 OK", flush=True)

    # ST10: pre-reg band ordering (HARD_PASS_BPC_BAR < MIDDLE high < HARD_FAIL floor)
    assert HARD_PASS_BPC_BAR < MIDDLE_BAND_BPC_HIGH < HARD_FAIL_BPC_FLOOR, (
        "ST10 pre-reg band ordering violated")
    assert ADAPT_LR_FLOOR < ADAPT_LR_CEIL, "ST10 adaptive LR bounds violated"
    print("[selftest] ST10 pre-reg band ordering OK (HP=%.2f < MB_hi=%.2f < HF=%.2f)" % (
        HARD_PASS_BPC_BAR, MIDDLE_BAND_BPC_HIGH, HARD_FAIL_BPC_FLOOR), flush=True)

    # ST11: LLM-call counter zero at selftest end
    assert _LLM_CALL_COUNTER[0] == 0, "ST11 LLM call counter non-zero: %d" % _LLM_CALL_COUNTER[0]
    print("[selftest] ST11 LLM call counter == 0 OK", flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    # --self-test writes NOTHING (pure wiring check; avoids stale-metrics masquerade)
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

ARM_CONFIGS = {
    "ARM_BASELINE_RANK1_K1_HEBBIAN": {"k": 1, "mode": "hebbian"},
    "ARM_ADAPTIVE_CFRPE_K1":          {"k": 1, "mode": "adaptive_cfrpe"},
    "ARM_K2_RANK1_HEBBIAN":           {"k": 2, "mode": "hebbian"},
    "ARM_K2_ADAPTIVE_CFRPE":          {"k": 2, "mode": "adaptive_cfrpe"},
}


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
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s mode=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM_TOTAL, str(DEVICE), RUN_MODE), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]), flush=True)

    # Encoder ONCE per seed (amortize gensim load)
    print("\n[seed=%d] building word2vec encoder (V=%d, N_DIM=%d)..." % (
        seed, V, N_DIM_TOTAL), flush=True)
    t_enc0 = time.time()
    E_proj_t, w2v_meta = build_E_word2vec(vocab, N_DIM_TOTAL, seed)
    E_full = _l2_normalize_t(sparsify_bipolar_gpu(E_proj_t, SPARSE_BIPOLAR_F))
    sparsity = float((E_full != 0).float().mean().item())
    print("[seed=%d] encoder built in %.1fs; w2v_hit=%d/%d sparsity=%.3f" % (
        seed, time.time() - t_enc0, w2v_meta["n_hit"], w2v_meta["n_vocab"], sparsity), flush=True)
    del E_proj_t
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    ctx_eval = ctx_full[mask]
    nxt_eval = nxt_full[mask]
    n_eval = len(ctx_eval)
    if n_eval == 0:
        print("[WARN seed=%d] no valid eval pairs" % seed, flush=True)
        return {"seed": seed, "by_arm": {"ARM_UNIGRAM": uni, "w2v_meta": w2v_meta},
                "V": V, "N_DIM_TOTAL": N_DIM_TOTAL, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2)}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni, "w2v_meta": w2v_meta}

    for arm_idx, arm in enumerate(ARMS):
        cfg = ARM_CONFIGS[arm]
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s k=%d mode=%s] computing..." % (
            seed, arm, cfg["k"], cfg["mode"]), flush=True)
        try:
            if cfg["k"] == 1 and cfg["mode"] == "hebbian":
                ar = build_logits_k1_hebbian(
                    E_full, idx_train_t, idx_held_t,
                    recall_batch=RECALL_BATCH, ingest_chunk=INGEST_CHUNK,
                )
            elif cfg["k"] == 1 and cfg["mode"] == "adaptive_cfrpe":
                ar = build_logits_k1_adaptive_cfrpe(
                    E_full, idx_train_t, idx_held_t,
                    n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR,
                    seed=seed, arm_idx=arm_idx, recall_batch=RECALL_BATCH,
                )
            elif cfg["k"] == 2 and cfg["mode"] == "hebbian":
                ar = build_logits_k2_hebbian(
                    E_full, idx_train_t, idx_held_t,
                    recall_batch=RECALL_BATCH, gate_temp=GATE_TEMP,
                    ingest_chunk=INGEST_CHUNK, seed=seed, arm_idx=arm_idx,
                )
            else:
                # K=2 adaptive cf-RPE  -- THE TEST ARM
                ar = build_logits_k2_adaptive_cfrpe(
                    E_full, idx_train_t, idx_held_t,
                    n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR,
                    recall_batch=RECALL_BATCH, gate_temp=GATE_TEMP,
                    seed=seed, arm_idx=arm_idx,
                )
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
            nxt_eval = nxt_full[valid_pos]
            n_eval = len(nxt_eval)
            n_dev = n_eval // 2
            nxt_dev = nxt_eval[:n_dev]
            nxt_test = nxt_eval[n_dev:]

        jr = joint_sweep(logits_eval[:n_dev], logits_eval[n_dev:],
                         U_log, nxt_dev, nxt_test)
        rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval)
        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "rule_class": cfg["mode"] + ("_k1" if cfg["k"] == 1 else "_k2"),
        })
        jr.update(ar.get("diag", {}))
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
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "elapsed_s_seed": round(time.time() - t_seed, 2),
    }


# ============================================================================
# Verdict (per pre-reg bands; Fix #28 per-arm metrics propagation)
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
        raw_v_finite = [x for x in raw_v if math.isfinite(x)]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "raw_bpc_at_T1_L1_mean": (round(float(np.mean(raw_v_finite)), 4)
                                        if raw_v_finite else None),
            "n_valid_seeds": len(valid),
            "all_seeds_failed": False,
        }
        arm_bpc[arm] = b_mean
        arm_cv[arm] = b_cv

    # Pull per-arm BPCs by name
    heb_k1 = arm_bpc.get("ARM_BASELINE_RANK1_K1_HEBBIAN", float("inf"))
    ad_k1 = arm_bpc.get("ARM_ADAPTIVE_CFRPE_K1", float("inf"))
    heb_k2 = arm_bpc.get("ARM_K2_RANK1_HEBBIAN", float("inf"))
    ad_k2 = arm_bpc.get("ARM_K2_ADAPTIVE_CFRPE", float("inf"))

    # Sanity-rail provenance checks (Fix #28; full mode only)
    heb_k1_drift = abs(heb_k1 - HEBBIAN_K1_BPC_REF) if math.isfinite(heb_k1) else float("inf")
    ad_k1_drift = abs(ad_k1 - ADAPTIVE_K1_BPC_REF) if math.isfinite(ad_k1) else float("inf")
    heb_k2_drift = abs(heb_k2 - HEBBIAN_K2_BPC_REF) if math.isfinite(heb_k2) else float("inf")
    rails_ok = (heb_k1_drift <= SANITY_TOL
                and ad_k1_drift <= SANITY_TOL
                and heb_k2_drift <= SANITY_TOL)

    # Compose lift: K2_ADAPTIVE vs ADAPTIVE_K1
    compose_lift = (ad_k1 - ad_k2) if (math.isfinite(ad_k1) and math.isfinite(ad_k2)) else float("nan")

    # cv on the TEST arm
    ad_k2_cv = arm_cv.get("ARM_K2_ADAPTIVE_CFRPE", float("nan"))
    all_cv_ok = all(
        math.isfinite(arm_cv.get(a, float("nan"))) and arm_cv[a] <= CV_MAX
        for a in ARMS
    )

    arm_summary = (
        "uni=%.3f | HEB_K1=%.4f(drift=%+.4f) | ADAPT_K1=%.4f(drift=%+.4f) | "
        "HEB_K2=%.4f(drift=%+.4f) | ADAPT_K2=%.4f(compose_lift=%+.4f, cv=%.4f) | rails=%s"
    ) % (
        unigram_bpc,
        heb_k1, heb_k1 - HEBBIAN_K1_BPC_REF,
        ad_k1, ad_k1 - ADAPTIVE_K1_BPC_REF,
        heb_k2, heb_k2 - HEBBIAN_K2_BPC_REF,
        ad_k2, compose_lift,
        ad_k2_cv if math.isfinite(ad_k2_cv) else -1.0,
        str(rails_ok),
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "compose_lift_adaptive_k2_over_k1": (round(compose_lift, 4)
                                                if math.isfinite(compose_lift) else None),
        "sanity_rails": {
            "heb_k1_drift": round(heb_k1_drift, 4) if math.isfinite(heb_k1_drift) else None,
            "adaptive_k1_drift": round(ad_k1_drift, 4) if math.isfinite(ad_k1_drift) else None,
            "heb_k2_drift": round(heb_k2_drift, 4) if math.isfinite(heb_k2_drift) else None,
            "tol": SANITY_TOL,
            "all_ok": bool(rails_ok),
        },
        "refs": {
            "heb_k1": HEBBIAN_K1_BPC_REF,
            "adaptive_k1": ADAPTIVE_K1_BPC_REF,
            "heb_k2": HEBBIAN_K2_BPC_REF,
        },
        "hard_pass_bpc_bar": HARD_PASS_BPC_BAR,
        "hard_pass_lift_over_adaptive_k1": HARD_PASS_LIFT_OVER_ADAPTIVE_K1,
        "middle_band_bpc_low": MIDDLE_BAND_BPC_LOW,
        "middle_band_bpc_high": MIDDLE_BAND_BPC_HIGH,
        "hard_fail_bpc_floor": HARD_FAIL_BPC_FLOOR,
        "cv_max": CV_MAX,
        "all_cv_ok": bool(all_cv_ok),
        "ad_k2_cv": (round(ad_k2_cv, 4) if math.isfinite(ad_k2_cv) else None),
        "unigram_bpc": round(unigram_bpc, 4),
        "n_seeds": len(units),
        "honest_scope": (
            "ADAPTIVE cf-RPE x K=2 multi-bank compose at production scale "
            "(N_DIM_TOTAL=8192, 4096/bank, N_TRAIN=100k text8, V=4000, "
            "word2vec sparse-bipolar f=0.05). HARD_PASS: ARM_K2_ADAPTIVE_CFRPE "
            "BPC <= %.2f AND beats ARM_ADAPTIVE_CFRPE_K1 by >= +%.2f. "
            "MIDDLE_BAND: BPC in [%.2f, %.2f]. HARD_FAIL: BPC >= %.2f. "
            "cv <= %.2f. Sanity rails (Fix #28): heb_k1=%.4f ad_k1=%.4f heb_k2=%.4f, "
            "tol +/-%.2f. WHAT_THIS_DOES_NOT_SHOW: K>2; STDP composition; "
            "soft-gate end-to-end training; alternative LR schedules. "
            "Strategic question: does per-token ADAPTIVE LR rescue the K=2 "
            "compose-sub-additivity observed with UNIFORM cf-RPE in A1?" % (
                HARD_PASS_BPC_BAR, HARD_PASS_LIFT_OVER_ADAPTIVE_K1,
                MIDDLE_BAND_BPC_LOW, MIDDLE_BAND_BPC_HIGH, HARD_FAIL_BPC_FLOOR,
                CV_MAX, HEBBIAN_K1_BPC_REF, ADAPTIVE_K1_BPC_REF, HEBBIAN_K2_BPC_REF,
                SANITY_TOL)),
        "cites": [
            "preregs/2026-06-24_substrate_adaptive_cfrpe_x_k2_compose_v1.md",
            "experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py",
            "experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json",
        ],
    }

    # Substrate-only audit
    total_llm_calls = sum(int(u.get("llm_forward_calls_at_inference", 0)) for u in units)
    detail["llm_forward_calls_total"] = total_llm_calls
    if total_llm_calls != 0:
        return ("HARD_FAIL",
                "HARD_FAIL: LLM_CALL_VIOLATION llm_calls=%d (substrate-only invariant). %s" % (
                    total_llm_calls, arm_summary),
                detail)

    # Gate: TEST arm failed entirely
    if by_arm_agg.get("ARM_K2_ADAPTIVE_CFRPE", {}).get("all_seeds_failed", True):
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_K2_ADAPTIVE_CFRPE all seeds failed. " + arm_summary,
                detail)

    # Provenance gate (full mode only -- smoke uses tiny N + V so rails do not apply)
    detail["provenance_check_active"] = (RUN_MODE == "full")
    if RUN_MODE == "full" and not rails_ok:
        return ("HARD_FAIL_PROVENANCE",
                ("HARD_FAIL_PROVENANCE: sanity rails violated. "
                 "heb_k1_drift=%+.4f ad_k1_drift=%+.4f heb_k2_drift=%+.4f (tol +/-%.2f). "
                 "Encoder/methodology mismatch -- result not comparable to A3/K2_v2. %s" % (
                     heb_k1 - HEBBIAN_K1_BPC_REF,
                     ad_k1 - ADAPTIVE_K1_BPC_REF,
                     heb_k2 - HEBBIAN_K2_BPC_REF,
                     SANITY_TOL, arm_summary)),
                detail)

    # cv gate on the test arm
    if math.isfinite(ad_k2_cv) and ad_k2_cv > CV_MAX:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_HIGH_CV: cv=%.4f > %.2f. compose_lift=%+.4f BPC=%.4f. %s" % (
                    ad_k2_cv, CV_MAX, compose_lift, ad_k2, arm_summary),
                detail)

    # HARD_PASS: both BPC <= bar AND super-additive over ADAPTIVE_K1
    if (math.isfinite(ad_k2) and ad_k2 <= HARD_PASS_BPC_BAR
            and math.isfinite(compose_lift)
            and compose_lift >= HARD_PASS_LIFT_OVER_ADAPTIVE_K1):
        detail["verdict_tier"] = "HARD_PASS_SUPERADDITIVE"
        return ("HARD_PASS",
                ("HARD_PASS: ARM_K2_ADAPTIVE_CFRPE BPC=%.4f <= %.2f AND "
                 "compose_lift=%+.4f >= +%.2f over ARM_ADAPTIVE_CFRPE_K1. "
                 "ADAPTIVE composition SUPER-ADDITIVE (rescues K=2 from uniform-cf-RPE "
                 "sub-additivity). %s" % (
                     ad_k2, HARD_PASS_BPC_BAR, compose_lift,
                     HARD_PASS_LIFT_OVER_ADAPTIVE_K1, arm_summary)),
                detail)

    # MIDDLE_BAND: BPC in [LOW, HIGH]
    if (math.isfinite(ad_k2)
            and MIDDLE_BAND_BPC_LOW <= ad_k2 <= MIDDLE_BAND_BPC_HIGH):
        detail["verdict_tier"] = "MIDDLE_BAND_ADDITIVE"
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND: ARM_K2_ADAPTIVE_CFRPE BPC=%.4f in [%.2f, %.2f]. "
                 "ADAPTIVE composition additive but not super-additive over A3 K=1. "
                 "compose_lift=%+.4f. %s" % (
                     ad_k2, MIDDLE_BAND_BPC_LOW, MIDDLE_BAND_BPC_HIGH,
                     compose_lift, arm_summary)),
                detail)

    # HARD_FAIL: BPC at/above HARD_FAIL floor
    detail["verdict_tier"] = "NO_COMPOSE_BENEFIT"
    return ("HARD_FAIL",
            ("HARD_FAIL: ARM_K2_ADAPTIVE_CFRPE BPC=%.4f >= %.2f (no compose benefit). "
             "Even ADAPTIVE primitives DO NOT compose K=2; sub-additivity is "
             "mechanistic not LR-specific. compose_lift=%+.4f. %s" % (
                 ad_k2, HARD_FAIL_BPC_FLOOR, compose_lift, arm_summary)),
            detail)


# ============================================================================
# Main loop with per-seed checkpoint
# ============================================================================

print("[config] %s" % CONFIG_VERSION, flush=True)
print("[config] device=%s torch_cuda_available=%s" % (
    str(DEVICE), torch.cuda.is_available()), flush=True)
if DEVICE.type == "cuda":
    print("[gpu] %s" % torch.cuda.get_device_name(0), flush=True)
else:
    print("[device] CPU (no CUDA available; expected only on laptop smoke)", flush=True)

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

if DEVICE.type == "cuda":
    try:
        peak_gb = torch.cuda.max_memory_allocated(0) / 1e9
        print("[gpu] peak memory %.3f GB" % peak_gb, flush=True)
    except Exception:
        pass

# REQUIRED_FIELDS (PROT-020 + queue_add validate_metrics)
summary_str = (
    "%s | arms=%d seeds=%d N_DIM=%d N_TRAIN=%d encoder=word2vec_sparse_bipolar" % (
        verdict, len(ARMS), len(SEEDS), N_DIM_TOTAL, N_TRAIN)
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
    "ADAPT_LR_FLOOR": ADAPT_LR_FLOOR,
    "ADAPT_LR_CEIL": ADAPT_LR_CEIL,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
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
         "elapsed_s_seed": u.get("elapsed_s_seed")}
        for u in all_units
    ],
    "elapsed_s": round(sum(u.get("elapsed_s_seed", 0.0) for u in all_units), 2),
}

write_metrics(out_dir, metrics, all_units)
print("[metrics] written to %s" % out_dir, flush=True)
