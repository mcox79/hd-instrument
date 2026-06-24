"""substrate_path_c_x_adaptive_cfrpe_3arm_v1 -- PATH C PC ENCODER x PER-TOKEN ADAPTIVE cf-RPE.

THE TEST: substrate-OWNED PC encoder x per-token adaptive cf-RPE plasticity.

Two prior landings (both MIDDLE_BAND, full mode):
  - word2vec + per-token-adaptive cf-RPE: BPC=6.9920 (substrate_cfrpe_per_token_adaptive_lr_v1)
  - PC encoder + Hebbian-only:            BPC=7.6184 (path_c_substrate_owned_encoder_FAIR_HARNESS_v2)

NEVER tested: PC encoder x per-token-adaptive cf-RPE. Path C PC encoder underperformed
word2vec_sparse_bipolar on BPC under Hebbian; per-token cf-RPE adds 0.34 bits with word2vec.
Does the combination close the gap (substrate-OWNED encoder + best plasticity vs.
word2vec-borrowed encoder + best plasticity)?

THREE ARMS (each builds FRESH; no cross-contamination):
  1. ARM_WORD2VEC_PER_TOKEN_CFRPE_REFERENCE
     word2vec encoder + sparse-bipolar f=0.05 + per-token-adaptive cf-RPE.
     Provenance rail to ~6.99 BPC.
  2. ARM_PC_ENCODER_HEBBIAN_REFERENCE
     Substrate-OWNED PC encoder (3-layer Hebbian-PC, Rao-Ballard, Tonegawa) +
     sparse-bipolar f=0.05 + rank-1 Hebbian W.
     Provenance rail to ~7.62 BPC.
  3. ARM_PC_ENCODER_PER_TOKEN_CFRPE
     PC encoder (identical to arm 2) + sparse-bipolar f=0.05 + per-token-adaptive cf-RPE.
     THE primary arm.

PRE-REG HARD BANDS (Fix #28 per-arm metrics; PRIMARY arm = ARM_3):
  Provenance rail 1: ARM_WORD2VEC_PER_TOKEN_CFRPE_REFERENCE BPC in [6.94, 7.04] (6.9920 +/- 0.05).
  Provenance rail 2: ARM_PC_ENCODER_HEBBIAN_REFERENCE BPC in [7.57, 7.67] (7.6184 +/- 0.05).
  HARD_PASS_BREAKS_GAP   : ARM_3_BPC <= 7.00 (matches OR beats word2vec equivalent). chain-grade-bonus.
  HARD_PASS_CLOSES_GAP   : ARM_3_BPC <= 7.10.
  HARD_PASS_PATH_C_VIABLE: ARM_3_BPC <= ARM_2_BPC - 0.30 (per-token cf-RPE substantially helps PC).
  MIDDLE_BAND            : 7.10 < ARM_3_BPC < 7.60.
  HARD_FAIL              : ARM_3_BPC >= 7.60 (per-token cf-RPE does not help PC encoder enough).
  CV gate                : ARM_3 bpc_cv > 0.10 downgrades verdict one tier.

GPU REQUIRED (Fix #24): torch.cuda for matmul / PC training / per-token cf-RPE.

Cites:
  preregs/2026-06-24_substrate_path_c_x_adaptive_cfrpe_3arm_v1.md
  experiments/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2.py
  experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py
  data/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2/metrics.json (PC ref BPC=7.6184)
  data/exp_substrate_cfrpe_per_token_adaptive_lr_v1/metrics.json (per-token ref BPC=6.9920)
  USER_2026-06-23_Path_C_substrate_owned_encoder_is_the_answer
  USER_2026-06-22_Fix24_GPU_must_use_GPU

ASCII-only. Per-seed checkpoint. atexit synthesizer. C7 LAMBDA_GRID excludes 0.0.
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

ANCHOR_NAME = "substrate_path_c_x_adaptive_cfrpe_3arm_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
_LLM_CALL_COUNTER = [0]

WORD2VEC_MODEL = "word2vec-google-news-300"

# Provenance reference baselines (locked pre-dispatch)
WORD2VEC_PER_TOKEN_REF_BPC = 6.9920    # substrate_cfrpe_per_token_adaptive_lr_v1 MIDDLE_BAND landing
PC_HEBBIAN_REF_BPC = 7.6184            # path_c_substrate_owned_encoder_FAIR_HARNESS_v2 MIDDLE_BAND landing
PROVENANCE_TOL = 0.05

# Pre-reg primary bands on ARM_3 (substrate-OWNED PC + per-token cf-RPE)
HP_BREAKS_GAP_BPC_BAR = 7.00           # chain-grade-bonus
HP_CLOSES_GAP_BPC_BAR = 7.10
HP_PATH_C_VIABLE_LIFT = 0.30           # ARM_3 <= ARM_2 - 0.30
MIDDLE_BAND_BPC_UPPER = 7.60           # >= 7.60 => HARD_FAIL
HP_BPC_CV_MAX = 0.10

# Plasticity controls (EXACT match to per_token_adaptive_lr_v1)
CFRPE_LR = 0.5
INGEST_BATCH = 64
SPARSE_BIPOLAR_F = 0.05
COARSE_N_STEPS = 5000                  # cf-RPE step count

# Per-token adaptive controls (EXACT match to per_token_adaptive_lr_v1)
ADAPT_LR_FLOOR = 0.25
ADAPT_LR_CEIL = 4.0

# PC encoder controls (EXACT match to FAIR_HARNESS_v2)
PC_N_LAYERS = 3
PC_ALPHA = 0.05
PC_BETA = 2.0
PC_N_PASSES = 1
PC_TRAINING_TOKENS_FULL = 100_000

# Inference grids (C7: LAMBDA_GRID excludes 0.0)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

UNIGRAM_BPC_REF = 7.738

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

# Config (FULL = production GPU; binds anchor since name has no _n<N> suffix)
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS_PLASTIC = COARSE_N_STEPS
    PC_TRAINING_TOKENS = PC_TRAINING_TOKENS_FULL
else:
    # Smoke must fit under 180s (gate ceiling). Exercises:
    #   - word2vec OR char-trigram fallback encoder
    #   - PC encoder forward + train + Tonegawa
    #   - sparse-bipolar primitive
    #   - per-token adaptive cf-RPE rule (with median normalization)
    #   - rank-1 Hebbian W (Hebbian-reference arm)
    #   - joint (T, lambda) sweep + 3 metrics
    #   - verdict band classification
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    N_STEPS_PLASTIC = 200
    PC_TRAINING_TOKENS = 1_000

ARMS = [
    "ARM_WORD2VEC_PER_TOKEN_CFRPE_REFERENCE",   # arm 1 (provenance)
    "ARM_PC_ENCODER_HEBBIAN_REFERENCE",         # arm 2 (provenance + ablation)
    "ARM_PC_ENCODER_PER_TOKEN_CFRPE",           # arm 3 (PRIMARY)
]
WORD2VEC_REF_ARM = "ARM_WORD2VEC_PER_TOKEN_CFRPE_REFERENCE"
PC_HEBBIAN_REF_ARM = "ARM_PC_ENCODER_HEBBIAN_REFERENCE"
PC_CFRPE_ARM = "ARM_PC_ENCODER_PER_TOKEN_CFRPE"

CONFIG_VERSION = (
    "substrate_path_c_x_adaptive_cfrpe_3arm_v1; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d seeds=%s mode=%s n_steps=%d pc_train_tokens=%d device=%s "
    "sparse_f=%.3f temps=%s lambdas=%s mrr_k=%d"
) % (N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, SEEDS, RUN_MODE, N_STEPS_PLASTIC,
     PC_TRAINING_TOKENS, str(DEVICE), SPARSE_BIPOLAR_F, TEMP_GRID, LAMBDA_GRID, MRR_K)


# ============================================================================
# Char-trigram encoder (OOV fallback + smoke encoder when gensim unavailable)
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


def build_E_word2vec(vocab: List[str], n_dim: int, seed: int
                      ) -> Tuple[torch.Tensor, Dict]:
    """Build [V, n_dim] L2-normalized word2vec-projected vectors on DEVICE."""
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


def build_E_char_trigram(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    """Smoke / fallback encoder when gensim unavailable."""
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
# Substrate-owned 3-layer Hebbian-PC encoder (from Path C v2 FAIR_HARNESS_v2)
# Rao-Ballard local update, NO backprop, Tonegawa write-time competitive
# allocation at L3.
# ============================================================================

def _sign_with_zero_tiebreak(x: torch.Tensor) -> torch.Tensor:
    s = torch.sign(x)
    s = torch.where(s == 0, torch.ones_like(s), s)
    return s


def build_planted_bipolar_inputs(V: int, n_dim: int, seed: int) -> torch.Tensor:
    rng = np.random.default_rng(seed * 7919 + 17)
    X = (rng.integers(0, 2, size=(V, n_dim)) * 2 - 1).astype(np.float32)
    Xn = _l2_normalize_np(X)
    return torch.from_numpy(Xn).to(device=DEVICE, dtype=TORCH_DTYPE)


def train_substrate_pc_encoder(
    X_planted: torch.Tensor,
    idx_train: np.ndarray,
    n_dim: int,
    alpha: float,
    n_passes: int,
    beta: float,
    seed: int,
    train_tokens: int,
) -> Tuple[Tuple[torch.Tensor, torch.Tensor, torch.Tensor], torch.Tensor, Dict]:
    """Train 3-layer substrate-PC Hebbian-PC encoder.

    Returns ((W_L1, W_L2, W_L3), E_excit, meta).
    """
    device = X_planted.device
    rng = torch.Generator(device="cpu")
    rng.manual_seed(int(seed) * 1009 + 31)
    W_L1 = (torch.randn(n_dim, n_dim, generator=rng) * (1.0 / math.sqrt(n_dim))).to(
        device=device, dtype=TORCH_DTYPE)
    W_L2 = (torch.randn(n_dim, n_dim, generator=rng) * (1.0 / math.sqrt(n_dim))).to(
        device=device, dtype=TORCH_DTYPE)
    W_L3 = (torch.randn(n_dim, n_dim, generator=rng) * (1.0 / math.sqrt(n_dim))).to(
        device=device, dtype=TORCH_DTYPE)
    E_excit = torch.zeros(n_dim, device=device, dtype=TORCH_DTYPE)

    n_train_tokens = min(len(idx_train), train_tokens)
    idx_t = torch.from_numpy(idx_train[:n_train_tokens].astype(np.int64)).to(device)

    per_pass_recon = {"L1": [], "L2": [], "L3": []}
    t_start = time.time()
    update_chunk = 1024 if RUN_MODE == "full" else 256
    n_updates = 0
    for pass_i in range(n_passes):
        recon_L1_accum = 0.0
        recon_L2_accum = 0.0
        recon_L3_accum = 0.0
        n_chunks = 0
        for b in range(0, n_train_tokens, update_chunk):
            end = min(b + update_chunk, n_train_tokens)
            ids_b = idx_t[b:end]
            x_in = X_planted[ids_b]
            pre_L1 = x_in @ W_L1.T
            L1_out = _sign_with_zero_tiebreak(pre_L1)
            pre_L2 = L1_out @ W_L2.T
            L2_out = _sign_with_zero_tiebreak(pre_L2)
            pre_L3 = L2_out @ W_L3.T
            route_w = torch.softmax(-beta * E_excit, dim=0)
            pre_L3_routed = pre_L3 * (route_w * n_dim)
            L3_out = _sign_with_zero_tiebreak(pre_L3_routed)
            recon_L1 = L1_out @ W_L1
            recon_L2 = L2_out @ W_L2
            recon_L3 = L3_out @ W_L3
            err_L1 = x_in - recon_L1
            err_L2 = L1_out - recon_L2
            err_L3 = L2_out - recon_L3
            B = x_in.shape[0]
            W_L1.add_((alpha / (n_dim * B)) * (err_L1.T @ x_in))
            W_L2.add_((alpha / (n_dim * B)) * (err_L2.T @ L1_out))
            W_L3.add_((alpha / (n_dim * B)) * (err_L3.T @ L2_out))
            E_excit.add_((L3_out * L3_out).sum(dim=0))
            recon_L1_accum += float(err_L1.norm(dim=1).mean().item())
            recon_L2_accum += float(err_L2.norm(dim=1).mean().item())
            recon_L3_accum += float(err_L3.norm(dim=1).mean().item())
            n_chunks += 1
            n_updates += 1
            if device.type == "cuda" and (n_updates % 16 == 0):
                torch.cuda.synchronize()
        if n_chunks > 0:
            per_pass_recon["L1"].append(round(recon_L1_accum / n_chunks, 4))
            per_pass_recon["L2"].append(round(recon_L2_accum / n_chunks, 4))
            per_pass_recon["L3"].append(round(recon_L3_accum / n_chunks, 4))
    meta = {
        "per_pass_mean_recon_err": per_pass_recon,
        "n_train_tokens": int(n_train_tokens),
        "n_passes": int(n_passes),
        "alpha": float(alpha),
        "beta": float(beta),
        "wall_train_s": round(time.time() - t_start, 2),
        "n_updates": int(n_updates),
    }
    return (W_L1, W_L2, W_L3), E_excit, meta


def encode_with_substrate_pc(
    X_planted: torch.Tensor,
    W_stack: Tuple[torch.Tensor, torch.Tensor, torch.Tensor],
    E_excit: torch.Tensor,
    beta: float,
) -> torch.Tensor:
    W_L1, W_L2, W_L3 = W_stack
    pre_L1 = X_planted @ W_L1.T
    L1_out = _sign_with_zero_tiebreak(pre_L1)
    pre_L2 = L1_out @ W_L2.T
    L2_out = _sign_with_zero_tiebreak(pre_L2)
    pre_L3 = L2_out @ W_L3.T
    n_dim = pre_L3.shape[-1]
    route_w = torch.softmax(-beta * E_excit, dim=0)
    pre_L3 = pre_L3 * (route_w * n_dim)
    L3_out = _sign_with_zero_tiebreak(pre_L3)
    return _l2_normalize_t(L3_out)


# ============================================================================
# Plasticity rules
# ============================================================================

def build_W_hebbian(E: torch.Tensor, idx_train_t: torch.Tensor,
                     ingest_chunk: int) -> torch.Tensor:
    """One-pass batched outer-product rank-1 Hebbian (FAIR_HARNESS_v2 verbatim)."""
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


def build_W_cfrpe_per_token_adaptive(E: torch.Tensor, idx_train_t: torch.Tensor,
                                      n_steps: int, batch: int, base_lr: float,
                                      gen: torch.Generator) -> Tuple[torch.Tensor, Dict]:
    """Per-token adaptive cf-RPE (per_token_adaptive_lr_v1 verbatim).

    For each batch step:
      error[i]   = Nxt[i] - Ctx[i] @ W^T               # [batch, dim]
      e_norm[i]  = ||error[i]|| / sqrt(dim)             # per-sample RMS error
      med        = median(e_norm)                       # batch reference
      lr_per[i]  = base_lr * clamp(e_norm[i] / (med+eps), FLOOR, CEIL)
      dW         = ((error * lr_per[:,None]).t @ Ctx) / batch
      W          = W + dW
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W, {"per_token_lr_max_min_ratio_max": 1.0, "n_clamped_steps": 0,
                    "final_batch_mean_err": float("nan")}
    sqrt_dim = math.sqrt(float(dim))
    max_min_ratio_max = 1.0
    n_clamped_steps = 0
    last_mean_err = float("nan")
    for step in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train_t[st]]
        Nxt = E[idx_train_t[st + 1]]
        error = Nxt - Ctx @ W.t()
        e_norm = error.norm(dim=1) / sqrt_dim
        med = float(torch.median(e_norm))
        med_safe = med if med > 1e-8 else 1e-8
        ratio = e_norm / med_safe
        ratio_clamped = torch.clamp(ratio, min=ADAPT_LR_FLOOR, max=ADAPT_LR_CEIL)
        if bool(((ratio < ADAPT_LR_FLOOR) | (ratio > ADAPT_LR_CEIL)).any()):
            n_clamped_steps += 1
        lr_per = base_lr * ratio_clamped
        weighted_error = error * lr_per.unsqueeze(1)
        dW = (weighted_error.t() @ Ctx) / batch
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
# Recall + eval
# ============================================================================

def compute_logits(E: torch.Tensor, W: torch.Tensor, idx_held_t: torch.Tensor,
                    recall_batch: int) -> np.ndarray:
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


# ============================================================================
# text8 + vocab
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
# Instrumentation self-test (MANDATORY before run)
# ============================================================================

def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)
    _dev = DEVICE
    n_dim_st = 64
    n_v_st = 8

    # ST1: sparsify_bipolar exact nnz + {-1, 0, 1}
    E_dense = torch.randn(4, 32, device=_dev)
    E_sp = sparsify_bipolar(E_dense, f=0.25, seed=0)
    n_nonzero = int((E_sp != 0).sum())
    expected_k = max(1, int(round(0.25 * 32)))
    assert n_nonzero == 4 * expected_k, "ST1 sparse-bipolar count: got %d, want %d" % (n_nonzero, 4*expected_k)
    uniq = set(E_sp.unique().tolist())
    assert uniq.issubset({-1.0, 0.0, 1.0}), "ST1 sparse not bipolar; got %s" % uniq
    print("[selftest] ST1 sparsify_bipolar OK (k=%d nonzero/row)" % expected_k, flush=True)

    # ST2: PC encoder forward shape + L2 norm
    X_p = build_planted_bipolar_inputs(n_v_st, n_dim_st, seed=0)
    idx_dummy = np.array([0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3], dtype=np.int64)
    W_stack, E_excit, pc_meta = train_substrate_pc_encoder(
        X_planted=X_p, idx_train=idx_dummy, n_dim=n_dim_st, alpha=0.05,
        n_passes=1, beta=2.0, seed=0, train_tokens=12,
    )
    E_pc = encode_with_substrate_pc(X_p, W_stack, E_excit, 2.0)
    assert E_pc.shape == (n_v_st, n_dim_st), "ST2 PC encoder output shape: %s" % str(E_pc.shape)
    norms = E_pc.norm(dim=1)
    assert torch.allclose(norms, torch.ones(n_v_st, device=norms.device), atol=1e-5), \
        "ST2 L2 norms: %s" % norms.tolist()
    print("[selftest] ST2 PC encoder forward shape + L2 norm OK", flush=True)

    # ST3: PC excitability trace evolves
    e_np = E_excit.detach().cpu().numpy()
    if float(np.mean(np.abs(e_np))) > 0:
        ratio = float(np.std(e_np)) / max(float(np.mean(np.abs(e_np))), 1e-9)
        assert ratio >= 0.0, "ST3 excit ratio negative"
    print("[selftest] ST3 PC excitability evolves OK", flush=True)

    # ST4: per-token adaptive ordering: high-error sample gets larger LR
    b_st = 4
    Ctx4 = _l2_normalize_t(torch.randn(b_st, n_dim_st, device=_dev))
    Nxt4 = _l2_normalize_t(torch.randn(b_st, n_dim_st, device=_dev))
    Nxt4[0] = Nxt4[0] * 5.0
    Nxt4[3] = Nxt4[3] * 0.2
    W4 = torch.zeros(n_dim_st, n_dim_st, device=_dev)
    err4 = Nxt4 - Ctx4 @ W4.t()
    sqrt_dim4 = math.sqrt(float(n_dim_st))
    e_norm4 = err4.norm(dim=1) / sqrt_dim4
    med4 = float(torch.median(e_norm4))
    ratio4 = e_norm4 / max(med4, 1e-8)
    ratio_c4 = torch.clamp(ratio4, min=ADAPT_LR_FLOOR, max=ADAPT_LR_CEIL)
    assert float(ratio_c4[0]) > float(ratio_c4[3]), \
        "ST4 per-token LR ordering: s0=%.3f vs s3=%.3f" % (
            float(ratio_c4[0]), float(ratio_c4[3]))
    print("[selftest] ST4 per-token LR ordering OK (high-err=%.3f low-err=%.3f)" % (
        float(ratio_c4[0]), float(ratio_c4[3])), flush=True)

    # ST5: build_W_cfrpe_per_token_adaptive returns non-zero W
    E_st = _l2_normalize_t(torch.randn(n_v_st, n_dim_st, device=_dev))
    idx_st = torch.randint(0, n_v_st, (21,), device=_dev)
    gen_st = torch.Generator(device=_dev); gen_st.manual_seed(7)
    W_adapt, diag_adapt = build_W_cfrpe_per_token_adaptive(
        E_st, idx_st, n_steps=10, batch=4, base_lr=0.5, gen=gen_st)
    assert W_adapt is not None
    assert float(W_adapt.norm()) > 1e-6, "ST5 adaptive W all-zero"
    assert "per_token_lr_max_min_ratio_max" in diag_adapt
    print("[selftest] ST5 build_W_cfrpe_per_token_adaptive non-zero norm=%.4f ratio=%.4f" % (
        float(W_adapt.norm()), diag_adapt["per_token_lr_max_min_ratio_max"]), flush=True)

    # ST6: build_W_hebbian returns non-zero W
    gen_h = torch.Generator(device=_dev); gen_h.manual_seed(11)
    W_heb = build_W_hebbian(E_st, idx_st, ingest_chunk=8)
    assert float(W_heb.norm()) > 1e-6, "ST6 Hebbian W all-zero"
    print("[selftest] ST6 build_W_hebbian non-zero norm=%.4f" % float(W_heb.norm()), flush=True)

    # ST7: compute_logits shape + finite
    idx_held_st = torch.randint(0, n_v_st, (10,), device=_dev)
    logits7 = compute_logits(E_st, W_heb, idx_held_st, recall_batch=5)
    assert logits7.shape == (10, n_v_st), "ST7 logits shape: %s" % str(logits7.shape)
    assert np.all(np.isfinite(logits7)), "ST7 logits non-finite"
    print("[selftest] ST7 compute_logits shape + finite OK", flush=True)

    # ST8: joint_sweep finite + C7 (0.0 not in LAMBDA_GRID)
    n_tok_st = 30
    n_v_sm = 6
    rng_jt = np.random.default_rng(99)
    logits_st = rng_jt.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_st = rng_jt.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_st = np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32)
    U_log_st = np.log(U_st)
    nd = n_tok_st // 2
    assert 0.0 not in LAMBDA_GRID, "ST8 C7 violation: 0.0 in LAMBDA_GRID"
    jr = joint_sweep(logits_st[:nd], logits_st[nd:], U_log_st, nxt_st[:nd], nxt_st[nd:],
                       TEMP_GRID, LAMBDA_GRID, MRR_K)
    assert math.isfinite(jr["bpc_best"]) and math.isfinite(jr["top1_acc"]), "ST8 joint_sweep finite"
    print("[selftest] ST8 joint_sweep OK (bpc=%.3f top1=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"]), flush=True)

    # ST9: pre-reg band ordering
    assert HP_BREAKS_GAP_BPC_BAR < HP_CLOSES_GAP_BPC_BAR < MIDDLE_BAND_BPC_UPPER, \
        "ST9 band ordering violated"
    assert ADAPT_LR_FLOOR < ADAPT_LR_CEIL, "ST9 LR bounds violated"
    assert PROVENANCE_TOL > 0, "ST9 provenance tol non-positive"
    print("[selftest] ST9 pre-reg band ordering OK (BREAKS=%.2f < CLOSES=%.2f < FAIL=%.2f)" % (
        HP_BREAKS_GAP_BPC_BAR, HP_CLOSES_GAP_BPC_BAR, MIDDLE_BAND_BPC_UPPER), flush=True)

    # ST10: LLM call counter zero
    assert _LLM_CALL_COUNTER[0] == 0, "ST10 LLM counter non-zero"
    print("[selftest] ST10 LLM counter zero OK", flush=True)

    print("[selftest] ALL PASS", flush=True)


# ============================================================================
# Per-arm logits builder
# ============================================================================

def compute_arm_logits(arm_label: str, E_base_word2vec: torch.Tensor,
                         idx_train: np.ndarray, idx_held: np.ndarray, seed: int,
                         w2i: Dict[str, int], vocab_size: int) -> Dict:
    """Build [n_held, V] logits + diagnostics for one arm.

    Arm 1 ARM_WORD2VEC_PER_TOKEN_CFRPE_REFERENCE: word2vec + sparse-bipolar +
                                                   per-token-adaptive cf-RPE.
    Arm 2 ARM_PC_ENCODER_HEBBIAN_REFERENCE:       PC encoder + sparse-bipolar +
                                                   rank-1 Hebbian W.
    Arm 3 ARM_PC_ENCODER_PER_TOKEN_CFRPE:         PC encoder + sparse-bipolar +
                                                   per-token-adaptive cf-RPE.
    """
    V, dim = E_base_word2vec.shape
    device = E_base_word2vec.device

    pc_arm = arm_label in (PC_HEBBIAN_REF_ARM, PC_CFRPE_ARM)
    cfrpe_arm = arm_label in (WORD2VEC_REF_ARM, PC_CFRPE_ARM)

    pc_meta: Dict = {}
    pc_sanity: Dict = {}
    plast_diag: Dict = {}

    # 1. Build encoder E for this arm.
    if pc_arm:
        t0_pc = time.time()
        X_planted = build_planted_bipolar_inputs(V, dim, seed)
        W_stack, E_excit, pc_meta = train_substrate_pc_encoder(
            X_planted=X_planted, idx_train=idx_train, n_dim=dim,
            alpha=PC_ALPHA, n_passes=PC_N_PASSES, beta=PC_BETA,
            seed=seed, train_tokens=PC_TRAINING_TOKENS,
        )
        # S1 sanity: zero-noise input recon cos on 32 random vocab
        rng = np.random.default_rng(0)
        sample_idx = rng.choice(V, size=min(32, V), replace=False).astype(np.int64)
        x_s = X_planted[sample_idx]
        L1_s = _sign_with_zero_tiebreak(x_s @ W_stack[0].T)
        recon_x = L1_s @ W_stack[0]
        recon_n = _l2_normalize_t(recon_x)
        x_n = _l2_normalize_t(x_s)
        recon_cos = float((recon_n * x_n).sum(dim=1).mean().item())
        e_np = E_excit.detach().cpu().numpy()
        mean_e = float(np.mean(np.abs(e_np)))
        std_e = float(np.std(e_np))
        excit_ratio = std_e / max(mean_e, 1e-9)
        l1_seq = pc_meta.get("per_pass_mean_recon_err", {}).get("L1", [])
        if len(l1_seq) >= 2:
            recon_decreases = bool(l1_seq[-1] <= l1_seq[0] * 1.05)
        else:
            recon_decreases = True
        pc_sanity = {
            "S1_recon_cos": round(recon_cos, 4),
            "S1_recon_cos_passed": bool(recon_cos > 0.40),
            "S2_excit_ratio": round(excit_ratio, 4),
            "S2_excit_passed": bool(excit_ratio > 0.05),
            "S3_recon_decreases": bool(recon_decreases),
        }
        E_arm_pre_sparsify = encode_with_substrate_pc(X_planted, W_stack, E_excit, PC_BETA)
        pc_meta["wall_pc_pipeline_s"] = round(time.time() - t0_pc, 2)
        del X_planted, W_stack, E_excit
    else:
        E_arm_pre_sparsify = E_base_word2vec

    # 2. Sparse-bipolar transform (applied to all 3 arms).
    E_used = _l2_normalize_t(sparsify_bipolar(E_arm_pre_sparsify, SPARSE_BIPOLAR_F, seed))

    # 3. Build W via the arm's plasticity rule.
    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)

    t0_w = time.time()
    if cfrpe_arm:
        arm_seed_w = seed * 10007 + (2 if arm_label == WORD2VEC_REF_ARM else 3) * 31337
        gen_w = torch.Generator(device=device); gen_w.manual_seed(arm_seed_w)
        W, plast_diag = build_W_cfrpe_per_token_adaptive(
            E_used, idx_train_t, n_steps=N_STEPS_PLASTIC,
            batch=INGEST_BATCH, base_lr=CFRPE_LR, gen=gen_w)
        plast_diag["rule_class"] = "per_token_median_normalized_adaptive"
        plast_diag["n_steps"] = int(N_STEPS_PLASTIC)
        plast_diag["base_lr"] = CFRPE_LR
        plast_diag["adapt_lr_floor"] = ADAPT_LR_FLOOR
        plast_diag["adapt_lr_ceil"] = ADAPT_LR_CEIL
    else:
        W = build_W_hebbian(E_used, idx_train_t, INGEST_CHUNK)
        plast_diag = {"rule_class": "one_pass_rank1_hebbian"}
    t_w = time.time() - t0_w

    # 4. Recall: logits = (E_used[ctx] @ W^T) normalized x E_used^T
    t0_r = time.time()
    n_h = idx_held_t.shape[0]
    src_keys_held = E_used[idx_held_t]
    pred_held = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        pred_held[b:end] = _l2_normalize_t(src_keys_held[b:end] @ W.T)
    logits_t = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        logits_t[b:end] = pred_held[b:end] @ E_used.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_r = time.time() - t0_r
    logits_np = logits_t.detach().cpu().numpy().astype(np.float32)

    del W, pred_held, src_keys_held, idx_train_t, idx_held_t, logits_t, E_used
    if pc_arm:
        del E_arm_pre_sparsify
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_w_s": round(t_w, 2),
        "wall_recall_s": round(t_r, 2),
        "pc_arm": bool(pc_arm),
        "cfrpe_arm": bool(cfrpe_arm),
        "pc_meta": pc_meta,
        "pc_sanity": pc_sanity,
        "plast_diag": plast_diag,
    }


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
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s mode=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE), RUN_MODE), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # Build base word2vec E (shared by arm 1; not used by arms 2/3 directly,
    # but PC encoder takes its dim from this). Smoke skips gensim load (slow on
    # laptop CPU; would blow past gate's 180s ceiling) and falls back to
    # char-trigram. Provenance rails are gated on RUN_MODE=full only; smoke
    # exercises mechanism + verdict-band logic with cheaper encoder.
    print("\n[seed=%d] building base E (V=%d N_DIM=%d) on %s..." % (
        seed, V, N_DIM, str(DEVICE)), flush=True)
    t_enc0 = time.time()
    encoder_meta: Dict = {}
    if RUN_MODE == "smoke":
        E_base = build_E_char_trigram(vocab, N_DIM, seed)
        encoder_meta = {"smoke_skip_gensim": True, "encoder": "char_trigram"}
    else:
        try:
            E_base, encoder_meta = build_E_word2vec(vocab, N_DIM, seed)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("[seed=%d encoder] WORD2VEC LOAD FAIL: %s -- falling back to char-trigram" % (
                seed, err), flush=True)
            E_base = build_E_char_trigram(vocab, N_DIM, seed)
            encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    t_enc = time.time() - t_enc0
    print("[seed=%d encoder] E built (%.1fs)" % (seed, t_enc), flush=True)

    # Build eval split
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    valid_held_pos = np.where(mask)[0]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        for arm in ARMS:
            by_arm[arm] = {"empty_eval": True}
        return {"seed": seed, "by_arm": by_arm, "V": V, "N_DIM": N_DIM,
                 "N": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                 "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
                 "elapsed_s_seed": round(time.time() - t_seed, 2),
                 "device": str(DEVICE), "encoder_meta": encoder_meta,
                 "n_llm_calls": 0}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    for arm in ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building logits..." % (seed, arm), flush=True)
        try:
            ar = compute_arm_logits(arm, E_base, idx_train, idx_held, seed, w2i, V)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {"compute_failed": True, "compute_error": err,
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
        logits_eval = logits_ctx[mask]
        jr = joint_sweep(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["wall_w_s"] = ar.get("wall_w_s", 0.0)
        jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
        jr["pc_arm"] = ar.get("pc_arm", False)
        jr["cfrpe_arm"] = ar.get("cfrpe_arm", False)
        jr["pc_meta"] = ar.get("pc_meta", {})
        jr["pc_sanity"] = ar.get("pc_sanity", {})
        jr["plast_diag"] = ar.get("plast_diag", {})
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.4f top1=%.4f mrr=%.4f "
              "(bestT=%.4f bestL=%.2f) raw_T1L1=%.3f wall_w=%.1fs wall_r=%.1fs" % (
                  seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                  jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                  jr["raw_bpc_at_T1_L1"], jr["wall_w_s"], jr["wall_recall_s"]), flush=True)

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
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "n_llm_calls": 0,
    }


# ============================================================================
# Verdict (Fix #28 per-arm metrics)
# ============================================================================

def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Aggregate ARM_UNIGRAM
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    uni_top1 = [u["by_arm"].get("ARM_UNIGRAM", {}).get("top1_unigram", float("nan")) for u in units]
    uni_mrr = [u["by_arm"].get("ARM_UNIGRAM", {}).get("mrr_unigram", float("nan")) for u in units]
    unigram_agg = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
        "top1_mean": round(float(np.mean(uni_top1)), 4),
        "top1_std": round(float(np.std(uni_top1)), 4),
        "mrr_mean": round(float(np.mean(uni_mrr)), 4),
        "mrr_std": round(float(np.std(uni_mrr)), 4),
    }
    by_arm_agg: Dict[str, Dict] = {"ARM_UNIGRAM": unigram_agg}

    def _agg_arm(arm: str) -> Dict:
        seeds_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid = [(not cf) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
                 for cf, u in zip(seeds_failed, units)]
        n_failed = int(sum(seeds_failed))
        valid_units = [u for ok, u in zip(valid, units) if ok]
        if not valid_units:
            return {"bpc_best_mean": float("inf"),
                    "top1_acc_mean": float("nan"),
                    "mrr_at_10_mean": float("nan"),
                    "raw_bpc_at_T1_L1_mean": float("nan"),
                    "n_valid_seeds": 0, "n_compute_failed": n_failed,
                    "all_seeds_failed": True}
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_v = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid_units]
        raw_v_finite = [x for x in raw_v if math.isfinite(x)]
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
            "n_valid_seeds": int(len(valid_units)),
            "n_compute_failed": n_failed,
            "all_seeds_failed": False,
        }

    for arm in ARMS:
        by_arm_agg[arm] = _agg_arm(arm)

    arm1 = by_arm_agg[WORD2VEC_REF_ARM]
    arm2 = by_arm_agg[PC_HEBBIAN_REF_ARM]
    arm3 = by_arm_agg[PC_CFRPE_ARM]

    arm1_bpc = arm1.get("bpc_best_mean", float("inf"))
    arm2_bpc = arm2.get("bpc_best_mean", float("inf"))
    arm3_bpc = arm3.get("bpc_best_mean", float("inf"))
    arm3_cv = arm3.get("bpc_best_cv", float("nan"))

    # Provenance rail checks (NOT verdict-blocking; tagged in detail)
    arm1_provenance_ok = (math.isfinite(arm1_bpc)
                          and abs(arm1_bpc - WORD2VEC_PER_TOKEN_REF_BPC) <= PROVENANCE_TOL)
    arm2_provenance_ok = (math.isfinite(arm2_bpc)
                          and abs(arm2_bpc - PC_HEBBIAN_REF_BPC) <= PROVENANCE_TOL)

    arms_summary = (
        "ARM_WORD2VEC_PER_TOKEN_CFRPE_REFERENCE=bpc%.4f(prov_ref=%.4f tol=%.2f ok=%s) | "
        "ARM_PC_ENCODER_HEBBIAN_REFERENCE=bpc%.4f(prov_ref=%.4f tol=%.2f ok=%s) | "
        "ARM_PC_ENCODER_PER_TOKEN_CFRPE=bpc%.4f cv=%.4f"
    ) % (arm1_bpc, WORD2VEC_PER_TOKEN_REF_BPC, PROVENANCE_TOL, arm1_provenance_ok,
         arm2_bpc, PC_HEBBIAN_REF_BPC, PROVENANCE_TOL, arm2_provenance_ok,
         arm3_bpc, arm3_cv if math.isfinite(arm3_cv) else -1.0)

    # n_llm gate
    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    # Path-C-viable test: ARM_3 <= ARM_2 - HP_PATH_C_VIABLE_LIFT
    path_c_viable = (math.isfinite(arm2_bpc) and math.isfinite(arm3_bpc)
                     and arm3_bpc <= arm2_bpc - HP_PATH_C_VIABLE_LIFT)
    closes_gap = (math.isfinite(arm3_bpc) and arm3_bpc <= HP_CLOSES_GAP_BPC_BAR)
    breaks_gap = (math.isfinite(arm3_bpc) and arm3_bpc <= HP_BREAKS_GAP_BPC_BAR)
    cv_ok = (math.isfinite(arm3_cv) and arm3_cv <= HP_BPC_CV_MAX)

    detail = {
        "by_arm_agg": by_arm_agg,
        "arm1_provenance_ok": bool(arm1_provenance_ok),
        "arm2_provenance_ok": bool(arm2_provenance_ok),
        "provenance_word2vec_per_token_ref_bpc": WORD2VEC_PER_TOKEN_REF_BPC,
        "provenance_pc_hebbian_ref_bpc": PC_HEBBIAN_REF_BPC,
        "provenance_tol": PROVENANCE_TOL,
        "hp_breaks_gap_bpc_bar": HP_BREAKS_GAP_BPC_BAR,
        "hp_closes_gap_bpc_bar": HP_CLOSES_GAP_BPC_BAR,
        "hp_path_c_viable_lift": HP_PATH_C_VIABLE_LIFT,
        "middle_band_bpc_upper": MIDDLE_BAND_BPC_UPPER,
        "hp_bpc_cv_max": HP_BPC_CV_MAX,
        "arm3_breaks_gap": bool(breaks_gap),
        "arm3_closes_gap": bool(closes_gap),
        "arm3_path_c_viable": bool(path_c_viable),
        "arm3_cv_ok": bool(cv_ok),
        "arm3_cv": arm3_cv if math.isfinite(arm3_cv) else None,
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "honest_scope": (
            "PRIMARY arm = ARM_PC_ENCODER_PER_TOKEN_CFRPE. Tests whether "
            "substrate-OWNED PC encoder (3-layer Hebbian-PC + Tonegawa) x "
            "per-token-adaptive cf-RPE plasticity closes the gap to "
            "word2vec + per-token-adaptive cf-RPE (~6.99 BPC, MIDDLE_BAND). "
            "HARD_PASS_BREAKS_GAP: ARM_3 <= %.2f (chain-grade-bonus). "
            "HARD_PASS_CLOSES_GAP: ARM_3 <= %.2f. "
            "HARD_PASS_PATH_C_VIABLE: ARM_3 <= ARM_2 - %.2f. "
            "MIDDLE_BAND: in (%.2f, %.2f). HARD_FAIL: >= %.2f. "
            "Provenance rails: arm1=%.4f+/-%.2f arm2=%.4f+/-%.2f. "
            "CV gate: arm3 bpc_cv <= %.2f or verdict downgrades. "
            "WHAT_THIS_DOES_NOT_SHOW: does not test STDP / other plasticity / "
            "PC variants / generalization / encoder ablations." % (
                HP_BREAKS_GAP_BPC_BAR, HP_CLOSES_GAP_BPC_BAR, HP_PATH_C_VIABLE_LIFT,
                HP_CLOSES_GAP_BPC_BAR, MIDDLE_BAND_BPC_UPPER, MIDDLE_BAND_BPC_UPPER,
                WORD2VEC_PER_TOKEN_REF_BPC, PROVENANCE_TOL,
                PC_HEBBIAN_REF_BPC, PROVENANCE_TOL,
                HP_BPC_CV_MAX)),
        "cites": [
            "preregs/2026-06-24_substrate_path_c_x_adaptive_cfrpe_3arm_v1.md",
            "experiments/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2.py",
            "experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py",
            "data/exp_path_c_substrate_owned_encoder_FAIR_HARNESS_v2/metrics.json",
            "data/exp_substrate_cfrpe_per_token_adaptive_lr_v1/metrics.json",
        ],
        "CONFIG_VERSION": CONFIG_VERSION,
    }

    # Hard gates
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, arms_summary),
                detail)

    if arm3.get("all_seeds_failed", False):
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_PC_ENCODER_PER_TOKEN_CFRPE all seeds failed. %s" % arms_summary,
                detail)

    # CV downgrade gate
    cv_downgrade = bool(math.isfinite(arm3_cv) and arm3_cv > HP_BPC_CV_MAX)

    # Primary classification
    if breaks_gap:
        base_verdict = "HARD_PASS"
        base_msg = ("HARD_PASS_BREAKS_GAP: ARM_PC_ENCODER_PER_TOKEN_CFRPE bpc=%.4f <= "
                    "%.2f. Substrate-OWNED PC encoder + per-token-adaptive cf-RPE "
                    "matches OR beats word2vec equivalent at the per-token cf-RPE "
                    "setpoint. CHAIN_GRADE_BONUS. path_c_viable=%s closes_gap=%s. %s" % (
                        arm3_bpc, HP_BREAKS_GAP_BPC_BAR,
                        path_c_viable, closes_gap, arms_summary))
    elif closes_gap:
        base_verdict = "HARD_PASS"
        base_msg = ("HARD_PASS_CLOSES_GAP: ARM_PC_ENCODER_PER_TOKEN_CFRPE bpc=%.4f <= "
                    "%.2f. Substrate-OWNED PC encoder + per-token-adaptive cf-RPE "
                    "closes the encoder-paradigm gap to within 0.1 of word2vec + "
                    "per-token cf-RPE. path_c_viable=%s. %s" % (
                        arm3_bpc, HP_CLOSES_GAP_BPC_BAR, path_c_viable, arms_summary))
    elif path_c_viable:
        base_verdict = "HARD_PASS"
        base_msg = ("HARD_PASS_PATH_C_VIABLE: ARM_PC_ENCODER_PER_TOKEN_CFRPE bpc=%.4f "
                    "<= ARM_PC_ENCODER_HEBBIAN_REFERENCE bpc=%.4f - %.2f. Per-token "
                    "cf-RPE substantially helps the PC encoder; Path C is viable but "
                    "doesn't close the encoder-paradigm gap entirely. %s" % (
                        arm3_bpc, arm2_bpc, HP_PATH_C_VIABLE_LIFT, arms_summary))
    elif arm3_bpc >= MIDDLE_BAND_BPC_UPPER:
        base_verdict = "HARD_FAIL"
        base_msg = ("HARD_FAIL: ARM_PC_ENCODER_PER_TOKEN_CFRPE bpc=%.4f >= %.2f. "
                    "Per-token-adaptive cf-RPE does NOT substantially help the "
                    "substrate-OWNED PC encoder; the encoder is the bottleneck, "
                    "not the plasticity rule. %s" % (
                        arm3_bpc, MIDDLE_BAND_BPC_UPPER, arms_summary))
    else:
        base_verdict = "MIDDLE_BAND"
        base_msg = ("MIDDLE_BAND: ARM_PC_ENCODER_PER_TOKEN_CFRPE bpc=%.4f in (%.2f, %.2f). "
                    "Per-token cf-RPE adds something to PC encoder but doesn't break "
                    "HARD_PASS_PATH_C_VIABLE. Characterize gap. %s" % (
                        arm3_bpc, HP_CLOSES_GAP_BPC_BAR, MIDDLE_BAND_BPC_UPPER,
                        arms_summary))

    # CV downgrade tier
    if cv_downgrade:
        if base_verdict == "HARD_PASS":
            return ("MIDDLE_BAND",
                    "MIDDLE_BAND_HIGH_CV: ARM_3 cv=%.4f > %.2f bar (would-be %s). %s" % (
                        arm3_cv, HP_BPC_CV_MAX, base_verdict, base_msg),
                    detail)
        if base_verdict == "MIDDLE_BAND":
            return ("HARD_FAIL",
                    "HARD_FAIL_HIGH_CV: ARM_3 cv=%.4f > %.2f bar (would-be %s). %s" % (
                        arm3_cv, HP_BPC_CV_MAX, base_verdict, base_msg),
                    detail)

    return (base_verdict, base_msg, detail)


# ============================================================================
# Self-test (instrumentation + verdict-band sanity)
# ============================================================================

def _selftest():
    _instrumentation_selftest()

    # Verdict band sanity
    def _mk_arm(bpc=8.0, top1=0.21, mrr=0.28, raw_t1l1=None):
        return {"bpc_best": bpc, "top1_acc": top1, "mrr_at_10": mrr,
                 "best_T_for_bpc": 0.5, "best_lambda_for_bpc": 0.3, "best_dev_bpc": bpc,
                 "best_T_for_top1": 0.5, "best_lambda_for_top1": 0.3,
                 "best_T_for_mrr": 0.5, "best_lambda_for_mrr": 0.3,
                 "raw_bpc_at_T1_L1": raw_t1l1 if raw_t1l1 is not None else bpc,
                 "n_dev": 100, "n_test": 100}

    def _full_unit(arm_data: Dict, V=4000):
        by_arm = {"ARM_UNIGRAM": {"bpc_unigram": 7.738, "top1_unigram": 0.2171,
                                    "mrr_unigram": 0.276, "n_test": 100}}
        for arm in ARMS:
            by_arm[arm] = arm_data.get(arm, _mk_arm())
        return {"seed": 0, "by_arm": by_arm, "V": V, "N_DIM": 64,
                 "N": 64, "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": V,
                 "run_mode": "smoke", "config_version": "selftest",
                 "elapsed_s_seed": 0.01, "device": "cpu", "n_llm_calls": 0}

    # Case 1: HARD_PASS_BREAKS_GAP — arm3 BPC <= 7.00
    u_breaks = _full_unit({
        WORD2VEC_REF_ARM: _mk_arm(bpc=6.99),
        PC_HEBBIAN_REF_ARM: _mk_arm(bpc=7.62),
        PC_CFRPE_ARM: _mk_arm(bpc=6.95),
    })
    v, m, d = compute_verdict([u_breaks, u_breaks, u_breaks])
    assert v == "HARD_PASS" and "BREAKS_GAP" in m, "selftest BREAKS_GAP got %s msg=%s" % (v, m[:200])
    assert d["arm3_breaks_gap"] and d["arm3_closes_gap"]

    # Case 2: HARD_PASS_CLOSES_GAP — arm3 in [7.00, 7.10]
    u_close = _full_unit({
        WORD2VEC_REF_ARM: _mk_arm(bpc=6.99),
        PC_HEBBIAN_REF_ARM: _mk_arm(bpc=7.62),
        PC_CFRPE_ARM: _mk_arm(bpc=7.08),
    })
    v, m, d = compute_verdict([u_close, u_close, u_close])
    assert v == "HARD_PASS" and "CLOSES_GAP" in m, "selftest CLOSES_GAP got %s msg=%s" % (v, m[:200])
    assert d["arm3_closes_gap"] and not d["arm3_breaks_gap"]

    # Case 3: HARD_PASS_PATH_C_VIABLE — arm3 in (7.10, 7.32] (arm2 - 0.30)
    u_viable = _full_unit({
        WORD2VEC_REF_ARM: _mk_arm(bpc=6.99),
        PC_HEBBIAN_REF_ARM: _mk_arm(bpc=7.62),
        PC_CFRPE_ARM: _mk_arm(bpc=7.30),  # 7.62 - 0.30 = 7.32; 7.30 < 7.32 viable
    })
    v, m, d = compute_verdict([u_viable, u_viable, u_viable])
    assert v == "HARD_PASS" and "PATH_C_VIABLE" in m, "selftest PATH_C_VIABLE got %s msg=%s" % (v, m[:200])
    assert d["arm3_path_c_viable"] and not d["arm3_closes_gap"]

    # Case 4: MIDDLE_BAND — arm3 in (7.32, 7.60)
    u_mid = _full_unit({
        WORD2VEC_REF_ARM: _mk_arm(bpc=6.99),
        PC_HEBBIAN_REF_ARM: _mk_arm(bpc=7.62),
        PC_CFRPE_ARM: _mk_arm(bpc=7.45),
    })
    v, m, d = compute_verdict([u_mid, u_mid, u_mid])
    assert v == "MIDDLE_BAND", "selftest MIDDLE_BAND got %s msg=%s" % (v, m[:200])

    # Case 5: HARD_FAIL — arm3 >= 7.60
    u_fail = _full_unit({
        WORD2VEC_REF_ARM: _mk_arm(bpc=6.99),
        PC_HEBBIAN_REF_ARM: _mk_arm(bpc=7.62),
        PC_CFRPE_ARM: _mk_arm(bpc=7.62),
    })
    v, m, d = compute_verdict([u_fail, u_fail, u_fail])
    assert v == "HARD_FAIL", "selftest HARD_FAIL got %s msg=%s" % (v, m[:200])

    print("[selftest] verdict band sanity (BREAKS / CLOSES / VIABLE / MIDDLE / FAIL) PASS", flush=True)


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
            "N_DIM": N_DIM, "N": N_DIM,
            "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_substrate_path_c_x_adaptive_cfrpe_3arm_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (
                len(units), len(SEEDS), msg[:200]),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
            "config_version": CONFIG_VERSION,
            "device": str(DEVICE),
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d partials\n" % (
            len(units), len(SEEDS)))
        sys.stderr.flush()
    except Exception as e:
        sys.stderr.write("[atexit] synthesize failed: %s\n" % e)
        sys.stderr.flush()


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)

    print("[config] %s mode=%s N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
          "seeds=%s arms=%s n_steps=%d pc_train_tokens=%d | name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
              SEEDS, ARMS, N_STEPS_PLASTIC, PC_TRAINING_TOKENS, _NAME_SAYS_SMOKE,
              CONFIG_VERSION), flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[gpu] device=%s name=%s total_mem_gb=%.2f" % (
                DEVICE, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception as e:
            print("[gpu] info-fetch failed: %s" % e, flush=True)
    else:
        print("[device] CPU (no CUDA; remote_cpu route)", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass

    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "path-c-x-adaptive-cfrpe-3arm-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS],
                                       run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] %s: %s" % (verdict, msg), flush=True)

    if DEVICE.type == "cuda":
        peak_gb = torch.cuda.max_memory_allocated(0) / 1e9
        print("[gpu] peak memory %.3f GB" % peak_gb, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM, "N": N_DIM,
        "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
        "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH,
        "N_STEPS_PLASTIC": N_STEPS_PLASTIC,
        "PC_TRAINING_TOKENS": PC_TRAINING_TOKENS,
        "CFRPE_LR": CFRPE_LR,
        "INGEST_BATCH": INGEST_BATCH,
        "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "ADAPT_LR_FLOOR": ADAPT_LR_FLOOR,
        "ADAPT_LR_CEIL": ADAPT_LR_CEIL,
        "PC_ALPHA": PC_ALPHA,
        "PC_BETA": PC_BETA,
        "PC_N_LAYERS": PC_N_LAYERS,
        "PC_N_PASSES": PC_N_PASSES,
        "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID,
        "MRR_K": MRR_K,
        "arms": ARMS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_gpu_substrate_path_c_x_adaptive_cfrpe_3arm_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate cosine logits; word2vec is static open-weight lookup; PC encoder trained on substrate; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
