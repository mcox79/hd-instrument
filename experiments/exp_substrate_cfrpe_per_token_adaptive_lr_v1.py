"""
substrate_cfrpe_per_token_adaptive_lr_v1 -- cf-RPE with per-token adaptive learning rate.

HYPOTHESIS: standard cf-RPE uses a global learning rate (LR=0.5) applied uniformly to
all batch samples. Per-token adaptive LR may give a free lift by allocating MORE
plasticity to high-prediction-error samples (surprise-gated learning, neuro-grounded)
and LESS to already-well-predicted samples. Plateau detection variant additionally
damps the global LR when running-mean error stops improving.

A6 audit identified: of N possible cf-RPE variants in this space, ONLY the
fixed-global-LR version was tested. Per-token adaptive schedules are UN-TESTED.

FOUR ARMS:
  ARM_HEBBIAN_BASELINE          -- one-pass rank-1 Hebbian; sanity rail at ~7.3065 BPC.
  ARM_CFRPE_COARSE_5000         -- standard cf-RPE @ 5000 steps, global LR=0.5; reference.
  ARM_CFRPE_PER_TOKEN_ADAPTIVE  -- per-sample LR scales with prediction-error magnitude.
  ARM_CFRPE_PER_TOKEN_PLATEAU   -- per-sample LR + global plateau-detection damping.

PER-TOKEN ADAPTIVE rule (ARM_CFRPE_PER_TOKEN_ADAPTIVE):
  Standard cf-RPE batch step:
    error[i] = Nxt[i] - Ctx[i] @ W^T        # [batch, dim]
    dW = (error^T @ Ctx) / batch            # global LR=0.5 applied uniformly
  Adaptive variant:
    err_norm[i] = ||error[i]|| / sqrt(dim)  # per-sample RMS error (positive scalar)
    median_norm = median(err_norm) + 1e-8
    lr_per[i] = LR * clamp(err_norm[i] / median_norm, ADAPT_LR_FLOOR, ADAPT_LR_CEIL)
    dW = (error * lr_per).t @ Ctx / batch   # samples with high error get higher LR
  Median-normalized so the BATCH-mean update magnitude stays comparable to coarse rule.
  Clamped to [ADAPT_LR_FLOOR, ADAPT_LR_CEIL] to prevent runaway on outliers.

PLATEAU variant (ARM_CFRPE_PER_TOKEN_PLATEAU):
  Same per-token weighting AND tracks exponentially-moving-average of batch_mean_err.
  At each step:
    ema_err = beta * ema_err + (1-beta) * mean(err_norm)   # smoothed running error
    if no improvement over last PLATEAU_WINDOW steps: global_lr *= PLATEAU_DECAY
  Half-life adaptive: damps LR after plateau detected; otherwise full LR.

PRE-REG HARD BANDS:
  Sanity rail:  ARM_HEBBIAN_BASELINE BPC within +/- 0.05 of 7.3065 (full mode only)
  HARD_PASS:    best adaptive arm lift >= 0.40 bits over ARM_HEBBIAN_BASELINE
                AND cv <= 0.10 across seeds
  MIDDLE_BAND:  lift in [0.20, 0.40)
  HARD_FAIL:    lift <= 0.20 bits (per-token does not add over coarse cf-RPE)
  CHAIN_GRADE_BONUS: best adaptive arm BPC <= 6.85 (beats v1 best cf-RPE 7.0386 by >0.18)
  C7 META compliance: LAMBDA_GRID excludes 0.0.

ENCODING: word2vec-google-news-300 projected to N_DIM=8192 sparse-bipolar (f=0.05);
  same encoder as fair_harness baseline (BPC 7.3065 chain-grade).

EXECUTION: remote_cpu_queue (USER refill directive 2026-06-24). torch CPU dispatch.
  Per-seed checkpoint via _seed_checkpoint.

ASCII-only. Fix #14 ONE cell. Fix #26 predispatch_check PROCEED.
Fix #28 per-arm metrics propagation (no cross-arm summary verdicts).

Cites:
  preregs/2026-06-24_substrate_cfrpe_per_token_adaptive_lr_v1.md
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py
  experiments/exp_substrate_cfrpe_n_steps_curve_extension_v2.py
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json (baseline 7.3065 BPC)
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
from collections import Counter, deque
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

ANCHOR_NAME = "substrate_cfrpe_per_token_adaptive_lr_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Pre-reg thresholds (per task spec; HARD bands locked before dispatch)
HARD_PASS_LIFT = 0.40             # best adaptive arm lift vs ARM_HEBBIAN_BASELINE bar
MIDDLE_BAND_LIFT_FLOOR = 0.20     # below this => HARD_FAIL
CHAIN_GRADE_BONUS_BPC = 6.85      # best adaptive arm BPC bar for chain-grade bonus
HEBBIAN_SANITY_REF = 7.3065
HEBBIAN_SANITY_TOL = 0.05
HP_BPC_CV_MAX = 0.10              # cv across seeds (per task spec: <= 0.10)

# Plasticity knobs (EXACT match to fair_harness/n_steps_curve heritage)
CFRPE_LR = 0.5
INGEST_BATCH = 64
SPARSE_BIPOLAR_F = 0.05
COARSE_N_STEPS = 5000             # standard cf-RPE coarse reference

# Per-token adaptive controls
ADAPT_LR_FLOOR = 0.25             # min per-sample LR multiplier (clamped)
ADAPT_LR_CEIL = 4.0               # max per-sample LR multiplier (clamped)

# Plateau-detection controls
PLATEAU_WINDOW = 200              # steps look-back for plateau check
PLATEAU_EMA_BETA = 0.9            # ema smoothing for batch_mean_err
PLATEAU_TOL = 0.001               # relative-improvement floor; below = plateau
PLATEAU_DECAY = 0.5               # multiplicative LR damping when plateau hit

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

# Production config (full mode)
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

# Gensim cache (process-local)
_GENSIM_KV_CACHE: Dict[str, object] = {}

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS_PLASTIC = COARSE_N_STEPS    # 5000 for all cf-RPE arms in full mode
else:
    # Smoke: exercises all 4 arms + plateau-detection + per-token weighting + verdict
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    N_STEPS_PLASTIC = 200               # smoke-scale; enough steps to exercise plateau logic

ARMS = [
    "ARM_HEBBIAN_BASELINE",
    "ARM_CFRPE_COARSE_5000",
    "ARM_CFRPE_PER_TOKEN_ADAPTIVE",
    "ARM_CFRPE_PER_TOKEN_PLATEAU",
]
CFRPE_ARMS = [a for a in ARMS if a != "ARM_HEBBIAN_BASELINE"]
ADAPTIVE_ARMS = ["ARM_CFRPE_PER_TOKEN_ADAPTIVE", "ARM_CFRPE_PER_TOKEN_PLATEAU"]


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

    OOV words fall back to char-trigram encoding so no zero-row degeneracy.
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

def build_W_hebbian(E: torch.Tensor, idx_train_t: torch.Tensor,
                     ingest_chunk: int) -> torch.Tensor:
    """One-pass batched outer-product rank-1 Hebbian.

    Identical to ARM_HEBBIAN_BASELINE / ARM_HEBBIAN_ONLY in heritage cells.
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


def build_W_cfrpe_coarse(E: torch.Tensor, idx_train_t: torch.Tensor,
                          n_steps: int, batch: int, lr: float,
                          gen: torch.Generator) -> torch.Tensor:
    """Standard cf-RPE: GLOBAL LR applied uniformly to all batch samples.

    EXACT rule from heterogeneous_plasticity ARM_CFRPE_ONLY / n_steps_curve.
      error = Nxt - Ctx @ W^T
      dW = (error.t @ Ctx) / batch
      W = W + lr * dW
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train_t[st]]
        Nxt = E[idx_train_t[st + 1]]
        error = Nxt - Ctx @ W.t()
        dW = (error.t() @ Ctx) / batch
        W = W + lr * dW
    return W


def build_W_cfrpe_per_token_adaptive(E: torch.Tensor, idx_train_t: torch.Tensor,
                                       n_steps: int, batch: int, base_lr: float,
                                       gen: torch.Generator) -> Tuple[torch.Tensor, Dict]:
    """Per-token adaptive cf-RPE: per-sample LR scales with error magnitude.

    For each batch step:
      error[i]   = Nxt[i] - Ctx[i] @ W^T               # [batch, dim]
      e_norm[i]  = ||error[i]|| / sqrt(dim)             # per-sample RMS error (scalar)
      med        = median(e_norm)                       # batch reference
      lr_per[i]  = base_lr * clamp(e_norm[i] / (med+eps), FLOOR, CEIL)
      dW         = ((error * lr_per[:,None]).t @ Ctx) / batch
      W          = W + dW

    Median-normalization preserves the BATCH-MEAN update magnitude near the
    coarse rule; clamping prevents runaway on outliers.

    Returns (W, diagnostics) where diagnostics tracks the running ratio of
    max-to-min per-token-LR and the mean batch error trajectory.
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
        # per-sample RMS error norm (scalar per sample)
        e_norm = error.norm(dim=1) / sqrt_dim
        med = float(torch.median(e_norm))
        med_safe = med if med > 1e-8 else 1e-8
        ratio = e_norm / med_safe
        # Clamp to [FLOOR, CEIL]
        ratio_clamped = torch.clamp(ratio, min=ADAPT_LR_FLOOR, max=ADAPT_LR_CEIL)
        if bool(((ratio < ADAPT_LR_FLOOR) | (ratio > ADAPT_LR_CEIL)).any()):
            n_clamped_steps += 1
        lr_per = base_lr * ratio_clamped       # [batch] positive
        # weighted error rows
        weighted_error = error * lr_per.unsqueeze(1)
        dW = (weighted_error.t() @ Ctx) / batch
        W = W + dW
        # diagnostics
        cur_ratio = float(ratio_clamped.max() / max(float(ratio_clamped.min()), 1e-8))
        if cur_ratio > max_min_ratio_max:
            max_min_ratio_max = cur_ratio
        last_mean_err = float(e_norm.mean())
    return W, {
        "per_token_lr_max_min_ratio_max": round(max_min_ratio_max, 4),
        "n_clamped_steps": int(n_clamped_steps),
        "final_batch_mean_err": round(last_mean_err, 6) if math.isfinite(last_mean_err) else None,
    }


def build_W_cfrpe_per_token_plateau(E: torch.Tensor, idx_train_t: torch.Tensor,
                                      n_steps: int, batch: int, base_lr: float,
                                      gen: torch.Generator) -> Tuple[torch.Tensor, Dict]:
    """Per-token adaptive + global plateau-detection damping.

    Combines:
      - Per-sample LR scaling (same as ARM_CFRPE_PER_TOKEN_ADAPTIVE)
      - Global LR multiplier decays by PLATEAU_DECAY whenever the EMA of
        batch_mean_err stops improving over a PLATEAU_WINDOW look-back.

    Plateau detection:
      ema_err = beta * ema_err + (1-beta) * mean(err_norm)
      if step >= PLATEAU_WINDOW:
        rel_improvement = (ema_window_ago - ema_err) / max(ema_window_ago, 1e-8)
        if rel_improvement < PLATEAU_TOL:
          global_lr *= PLATEAU_DECAY
          (record plateau hit; do not retrigger for next PLATEAU_WINDOW steps)
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W, {"per_token_lr_max_min_ratio_max": 1.0, "n_clamped_steps": 0,
                    "n_plateau_hits": 0, "final_global_lr": base_lr,
                    "final_batch_mean_err": float("nan")}
    sqrt_dim = math.sqrt(float(dim))
    global_lr = base_lr
    ema_err = float("nan")
    ema_window: deque = deque(maxlen=PLATEAU_WINDOW)
    max_min_ratio_max = 1.0
    n_clamped_steps = 0
    n_plateau_hits = 0
    steps_since_plateau = PLATEAU_WINDOW         # allow first detect after window
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
        lr_per = global_lr * ratio_clamped
        weighted_error = error * lr_per.unsqueeze(1)
        dW = (weighted_error.t() @ Ctx) / batch
        W = W + dW
        # Plateau detection
        mean_e = float(e_norm.mean())
        last_mean_err = mean_e
        if not math.isfinite(ema_err):
            ema_err = mean_e
        else:
            ema_err = PLATEAU_EMA_BETA * ema_err + (1.0 - PLATEAU_EMA_BETA) * mean_e
        ema_window.append(ema_err)
        steps_since_plateau += 1
        if (step >= PLATEAU_WINDOW
                and steps_since_plateau >= PLATEAU_WINDOW
                and len(ema_window) == PLATEAU_WINDOW):
            ema_window_ago = ema_window[0]
            if ema_window_ago > 1e-8:
                rel_improvement = (ema_window_ago - ema_err) / ema_window_ago
                if rel_improvement < PLATEAU_TOL:
                    global_lr *= PLATEAU_DECAY
                    n_plateau_hits += 1
                    steps_since_plateau = 0
        cur_ratio = float(ratio_clamped.max() / max(float(ratio_clamped.min()), 1e-8))
        if cur_ratio > max_min_ratio_max:
            max_min_ratio_max = cur_ratio
    return W, {
        "per_token_lr_max_min_ratio_max": round(max_min_ratio_max, 4),
        "n_clamped_steps": int(n_clamped_steps),
        "n_plateau_hits": int(n_plateau_hits),
        "final_global_lr": round(global_lr, 6),
        "final_batch_mean_err": round(last_mean_err, 6) if math.isfinite(last_mean_err) else None,
    }


# ============================================================================
# Recall + eval pipeline (identical to n_steps_curve / fair_harness)
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

    lambda_min = min(lambda_grid) if lambda_grid else 0.0
    lambda_zero_collapse = bool(
        abs(best_bpc["lambda"] - lambda_min) < 1e-6 and
        math.isfinite(bpc_best_test) and
        bpc_best_test > 7.5
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
    """Assert mechanisms work + metrics are finite at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    _dev = DEVICE

    # ST1: coarse cf-RPE shrinks error single-pair (sanity rule check)
    n_dim_st = 64
    Ctx1 = torch.randn(1, n_dim_st, device=_dev)
    Nxt1 = torch.randn(1, n_dim_st, device=_dev)
    Ctx1 = Ctx1 / (Ctx1.norm() + 1e-8)
    Nxt1 = Nxt1 / (Nxt1.norm() + 1e-8)
    W1 = torch.zeros(n_dim_st, n_dim_st, device=_dev)
    error_before = float((Nxt1 - Ctx1 @ W1.t()).norm())
    dW1 = (Nxt1 - Ctx1 @ W1.t()).t() @ Ctx1
    W1 = W1 + 0.9 * dW1
    error_after = float((Nxt1 - Ctx1 @ W1.t()).norm())
    assert error_after < error_before, "ST1 cf-RPE failed to shrink error"
    print("[selftest] ST1 cf-RPE shrinks error: %.4f -> %.4f" % (error_before, error_after), flush=True)

    # ST2: build_W_cfrpe_coarse returns non-zero W after 10 steps
    n_v_st = 8
    E_st = torch.randn(n_v_st, n_dim_st, device=_dev)
    E_st = _l2_normalize_t(E_st)
    idx_st = torch.randint(0, n_v_st, (21,), device=_dev)
    gen_st = torch.Generator(device=_dev); gen_st.manual_seed(7)
    W_coarse = build_W_cfrpe_coarse(E_st, idx_st, n_steps=10, batch=4, lr=0.5, gen=gen_st)
    assert W_coarse is not None
    assert float(W_coarse.norm()) > 1e-6, "ST2 coarse W is all-zero"
    print("[selftest] ST2 build_W_cfrpe_coarse non-zero W norm=%.4f" % float(W_coarse.norm()),
          flush=True)

    # ST3: per-token adaptive rule -- different output per sample (lr_per is per-sample)
    # Manually construct a case where two samples have very different error norms.
    b_st = 4
    Ctx3 = torch.randn(b_st, n_dim_st, device=_dev)
    Ctx3 = _l2_normalize_t(Ctx3)
    Nxt3 = torch.randn(b_st, n_dim_st, device=_dev)
    Nxt3 = _l2_normalize_t(Nxt3)
    # Sample 0 has 5x larger error than sample 3 (artificial via Nxt scale)
    Nxt3[0] = Nxt3[0] * 5.0
    Nxt3[3] = Nxt3[3] * 0.2
    W3 = torch.zeros(n_dim_st, n_dim_st, device=_dev)
    error3 = Nxt3 - Ctx3 @ W3.t()
    sqrt_dim = math.sqrt(float(n_dim_st))
    e_norm3 = error3.norm(dim=1) / sqrt_dim
    med3 = float(torch.median(e_norm3))
    ratio3 = e_norm3 / max(med3, 1e-8)
    ratio_clamped3 = torch.clamp(ratio3, min=ADAPT_LR_FLOOR, max=ADAPT_LR_CEIL)
    # Sample 0 should get MORE LR than sample 3
    assert float(ratio_clamped3[0]) > float(ratio_clamped3[3]), (
        "ST3 per-token: high-error sample should get higher LR (s0=%.4f s3=%.4f)" % (
            float(ratio_clamped3[0]), float(ratio_clamped3[3])))
    print("[selftest] ST3 per-token LR ordering OK (high-err=%.3f low-err=%.3f)" % (
        float(ratio_clamped3[0]), float(ratio_clamped3[3])), flush=True)

    # ST4: adaptive variant callable + returns non-zero W
    gen_st2 = torch.Generator(device=_dev); gen_st2.manual_seed(11)
    W_adapt, diag_adapt = build_W_cfrpe_per_token_adaptive(
        E_st, idx_st, n_steps=10, batch=4, base_lr=0.5, gen=gen_st2)
    assert W_adapt is not None
    assert float(W_adapt.norm()) > 1e-6, "ST4 adaptive W is all-zero"
    assert "per_token_lr_max_min_ratio_max" in diag_adapt, "ST4 diag missing key"
    print("[selftest] ST4 adaptive arm W non-zero norm=%.4f, max/min lr ratio=%.4f" % (
        float(W_adapt.norm()), diag_adapt["per_token_lr_max_min_ratio_max"]), flush=True)

    # ST5: plateau variant callable + tracks plateau hits
    gen_st3 = torch.Generator(device=_dev); gen_st3.manual_seed(13)
    # Use enough steps to trigger plateau logic at smoke scale
    W_plat, diag_plat = build_W_cfrpe_per_token_plateau(
        E_st, idx_st, n_steps=PLATEAU_WINDOW * 2 + 10, batch=4, base_lr=0.5, gen=gen_st3)
    assert W_plat is not None
    assert float(W_plat.norm()) > 1e-6, "ST5 plateau W is all-zero"
    assert "n_plateau_hits" in diag_plat, "ST5 diag missing plateau key"
    assert "final_global_lr" in diag_plat, "ST5 diag missing final_global_lr"
    # final_global_lr should be <= base_lr (can never increase)
    assert diag_plat["final_global_lr"] <= 0.5 + 1e-6, (
        "ST5 final_global_lr=%.4f > base_lr=0.5 (decay-only invariant violated)" % (
            diag_plat["final_global_lr"]))
    print("[selftest] ST5 plateau W non-zero (norm=%.4f); plateau_hits=%d final_lr=%.4f" % (
        float(W_plat.norm()), diag_plat["n_plateau_hits"], diag_plat["final_global_lr"]), flush=True)

    # ST6: adaptive W differs from coarse W (otherwise per-token weighting is null)
    gen_st4 = torch.Generator(device=_dev); gen_st4.manual_seed(7)
    W_coarse_v2 = build_W_cfrpe_coarse(E_st, idx_st, n_steps=10, batch=4, lr=0.5, gen=gen_st4)
    diff_adapt_coarse = float((W_adapt - W_coarse_v2).norm())
    # Note: same seed used for both gens (7 vs 11 -- different batches sampled);
    # so this isn't a controlled comparison. We just assert the magnitudes are
    # in the same order (sanity), and that adaptive isn't degenerate.
    assert float(W_adapt.norm()) > 0.01 * float(W_coarse_v2.norm()), (
        "ST6 adaptive W norm too small vs coarse W (degenerate update)")
    print("[selftest] ST6 adaptive vs coarse W norms: %.4f vs %.4f (diff=%.4f)" % (
        float(W_adapt.norm()), float(W_coarse_v2.norm()), diff_adapt_coarse), flush=True)

    # ST7: sparsify_bipolar produces sparse +/-1 vectors
    E_dense = torch.randn(4, 32, device=_dev)
    E_sparse = sparsify_bipolar_gpu(E_dense, f=0.25, seed=0)
    n_nonzero = int((E_sparse != 0).sum())
    expected_k = max(1, int(round(0.25 * 32)))
    assert n_nonzero == 4 * expected_k, "ST7 sparsify_bipolar count mismatch"
    print("[selftest] ST7 sparsify_bipolar_gpu OK (k=%d nonzero/row)" % expected_k, flush=True)

    # ST8: compute_logits returns shape + finite
    n_held_st = 10
    idx_held_st = torch.randint(0, n_v_st, (n_held_st,), device=_dev)
    logits8 = compute_logits_gpu(E_st, W_coarse, idx_held_st, recall_batch=5)
    assert logits8.shape == (n_held_st, n_v_st), "ST8 logits shape mismatch"
    assert np.all(np.isfinite(logits8)), "ST8 logits non-finite"
    print("[selftest] ST8 compute_logits shape=%s finite=True" % str(logits8.shape), flush=True)

    # ST9: joint_sweep returns finite + C7 (0.0 not in LAMBDA_GRID)
    n_tok_st = 30
    n_v_sm = 6
    rng_jt = np.random.default_rng(99)
    logits_st = rng_jt.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_st = rng_jt.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_st = np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32)
    U_log_st = np.log(U_st)
    nd = n_tok_st // 2
    assert 0.0 not in LAMBDA_GRID, "ST9 C7 violation: 0.0 in LAMBDA_GRID"
    jr = joint_sweep(logits_st[:nd], logits_st[nd:], U_log_st, nxt_st[:nd], nxt_st[nd:],
                      TEMP_GRID, LAMBDA_GRID, MRR_K)
    assert math.isfinite(jr["bpc_best"]) and math.isfinite(jr["top1_acc"]), "ST9 joint_sweep finite check"
    print("[selftest] ST9 joint_sweep OK (bpc=%.3f top1=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"]), flush=True)

    # ST10: pre-reg constants are sane (HARD bands satisfy MIDDLE < HARD_PASS)
    assert MIDDLE_BAND_LIFT_FLOOR < HARD_PASS_LIFT, "ST10 band ordering violated"
    assert ADAPT_LR_FLOOR < ADAPT_LR_CEIL, "ST10 per-token bounds violated"
    print("[selftest] ST10 pre-reg band ordering OK (MID=%.2f < HP=%.2f)" % (
        MIDDLE_BAND_LIFT_FLOOR, HARD_PASS_LIFT), flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict:
    """Run all 4 arms for one seed."""
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

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # Hoist encoder outside arm loop (Fix #24 even on CPU: amortize gensim load)
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
    print("[seed=%d encoder] E built (%.1fs)" % (seed, t_enc), flush=True)

    # Sparse-bipolar transform (same as fair_harness)
    E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, f=SPARSE_BIPOLAR_F, seed=seed))
    del E_base
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    # Build eval split
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

    def _eval_W_on_arm(arm_name: str, W: torch.Tensor, t_arm0: float,
                        extra_diag: Dict = None) -> None:
        logits = compute_logits_gpu(E_used, W, idx_held_t, RECALL_BATCH)
        raw_bpc = _raw_bpc_at_T1(logits, idx_held)
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
            if extra_diag:
                jr.update(extra_diag)
            by_arm[arm_name] = jr
            print("    [seed=%d arm=%s] bpc_best=%.4f top1=%.4f (bestT=%.4f bestL=%.2f) raw_T1L1=%.3f" % (
                seed, arm_name, jr["bpc_best"], jr["top1_acc"],
                jr["best_T_for_bpc"], jr["best_lambda_for_bpc"], jr["raw_bpc_at_T1_L1"]), flush=True)
            return
        logits_eval = logits_ctx[mask]
        jr = joint_sweep(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["raw_bpc_at_T1_L1"] = round(raw_bpc, 4)
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        if extra_diag:
            jr.update(extra_diag)
        by_arm[arm_name] = jr
        print("    [seed=%d arm=%s] bpc_best=%.4f top1=%.4f (bestT=%.4f bestL=%.2f) raw_T1L1=%.3f" % (
            seed, arm_name, jr["bpc_best"], jr["top1_acc"],
            jr["best_T_for_bpc"], jr["best_lambda_for_bpc"], jr["raw_bpc_at_T1_L1"]), flush=True)

    # ARM_HEBBIAN_BASELINE
    t_heb = time.time()
    print("\n  [seed=%d arm=ARM_HEBBIAN_BASELINE] building W..." % seed, flush=True)
    try:
        W_heb = build_W_hebbian(E_used, idx_train_t, ingest_chunk=INGEST_CHUNK)
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

    # ARM_CFRPE_COARSE_5000
    t_coarse = time.time()
    print("\n  [seed=%d arm=ARM_CFRPE_COARSE_5000] building W (n_steps=%d)..." % (
        seed, N_STEPS_PLASTIC), flush=True)
    arm_seed_coarse = seed * 10007 + 1 * 31337
    gen_coarse = torch.Generator(device=DEVICE); gen_coarse.manual_seed(arm_seed_coarse)
    try:
        W_coarse = build_W_cfrpe_coarse(E_used, idx_train_t, n_steps=N_STEPS_PLASTIC,
                                          batch=INGEST_BATCH, lr=CFRPE_LR, gen=gen_coarse)
        _eval_W_on_arm("ARM_CFRPE_COARSE_5000", W_coarse, t_coarse,
                        extra_diag={"n_steps": int(N_STEPS_PLASTIC),
                                     "rule_class": "global_lr_uniform"})
        del W_coarse
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=ARM_CFRPE_COARSE_5000] COMPUTE FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_CFRPE_COARSE_5000"] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
            "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "elapsed_s_arm": round(time.time() - t_coarse, 2),
        }

    # ARM_CFRPE_PER_TOKEN_ADAPTIVE
    t_adapt = time.time()
    print("\n  [seed=%d arm=ARM_CFRPE_PER_TOKEN_ADAPTIVE] building W (n_steps=%d)..." % (
        seed, N_STEPS_PLASTIC), flush=True)
    arm_seed_adapt = seed * 10007 + 2 * 31337
    gen_adapt = torch.Generator(device=DEVICE); gen_adapt.manual_seed(arm_seed_adapt)
    try:
        W_adapt, diag_adapt = build_W_cfrpe_per_token_adaptive(
            E_used, idx_train_t, n_steps=N_STEPS_PLASTIC,
            batch=INGEST_BATCH, base_lr=CFRPE_LR, gen=gen_adapt)
        diag_adapt["n_steps"] = int(N_STEPS_PLASTIC)
        diag_adapt["rule_class"] = "per_token_median_normalized_adaptive"
        diag_adapt["adapt_lr_floor"] = ADAPT_LR_FLOOR
        diag_adapt["adapt_lr_ceil"] = ADAPT_LR_CEIL
        _eval_W_on_arm("ARM_CFRPE_PER_TOKEN_ADAPTIVE", W_adapt, t_adapt,
                        extra_diag=diag_adapt)
        del W_adapt
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=ARM_CFRPE_PER_TOKEN_ADAPTIVE] COMPUTE FAIL: %s" % (seed, err),
              flush=True)
        by_arm["ARM_CFRPE_PER_TOKEN_ADAPTIVE"] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
            "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "elapsed_s_arm": round(time.time() - t_adapt, 2),
        }

    # ARM_CFRPE_PER_TOKEN_PLATEAU
    t_plat = time.time()
    print("\n  [seed=%d arm=ARM_CFRPE_PER_TOKEN_PLATEAU] building W (n_steps=%d)..." % (
        seed, N_STEPS_PLASTIC), flush=True)
    arm_seed_plat = seed * 10007 + 3 * 31337
    gen_plat = torch.Generator(device=DEVICE); gen_plat.manual_seed(arm_seed_plat)
    try:
        W_plat, diag_plat = build_W_cfrpe_per_token_plateau(
            E_used, idx_train_t, n_steps=N_STEPS_PLASTIC,
            batch=INGEST_BATCH, base_lr=CFRPE_LR, gen=gen_plat)
        diag_plat["n_steps"] = int(N_STEPS_PLASTIC)
        diag_plat["rule_class"] = "per_token_plus_plateau_decay"
        diag_plat["plateau_window"] = PLATEAU_WINDOW
        diag_plat["plateau_decay"] = PLATEAU_DECAY
        diag_plat["plateau_ema_beta"] = PLATEAU_EMA_BETA
        diag_plat["adapt_lr_floor"] = ADAPT_LR_FLOOR
        diag_plat["adapt_lr_ceil"] = ADAPT_LR_CEIL
        _eval_W_on_arm("ARM_CFRPE_PER_TOKEN_PLATEAU", W_plat, t_plat,
                        extra_diag=diag_plat)
        del W_plat
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=ARM_CFRPE_PER_TOKEN_PLATEAU] COMPUTE FAIL: %s" % (seed, err),
              flush=True)
        by_arm["ARM_CFRPE_PER_TOKEN_PLATEAU"] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
            "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "elapsed_s_arm": round(time.time() - t_plat, 2),
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
        "N_STEPS_PLASTIC": N_STEPS_PLASTIC,
        "run_mode": RUN_MODE,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
    }


# ============================================================================
# Verdict (per pre-reg bands; Fix #28 per-arm metrics propagation)
# ============================================================================

def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})
    vocab_entropy = math.log2(max(units[0].get("V", 4000), 2))

    by_arm_agg: Dict[str, Dict] = {}

    # ARM_UNIGRAM aggregation
    uni_bpc_list = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan"))
                     for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.mean(uni_bpc_list)), 4),
        "bpc_std": round(float(np.std(uni_bpc_list)), 4),
    }
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    def _agg_arm(arm: str) -> Dict:
        seeds_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid = [(not cf) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
                 for cf, u in zip(seeds_failed, units)]
        n_failed = int(sum(seeds_failed))
        valid_units = [u for ok, u in zip(valid, units) if ok]
        if not valid_units:
            return {"bpc_best_mean": float("inf"), "top1_acc_mean": float("nan"),
                    "mrr_at_10_mean": float("nan"), "raw_bpc_at_T1_L1_mean": float("nan"),
                    "n_valid_seeds": 0, "n_compute_failed": n_failed, "all_seeds_failed": True}
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

    heb_bpc = by_arm_agg["ARM_HEBBIAN_BASELINE"].get("bpc_best_mean", float("inf"))
    heb_failed = by_arm_agg["ARM_HEBBIAN_BASELINE"].get("all_seeds_failed", True)
    coarse_bpc = by_arm_agg["ARM_CFRPE_COARSE_5000"].get("bpc_best_mean", float("inf"))
    adapt_bpc = by_arm_agg["ARM_CFRPE_PER_TOKEN_ADAPTIVE"].get("bpc_best_mean", float("inf"))
    plateau_bpc = by_arm_agg["ARM_CFRPE_PER_TOKEN_PLATEAU"].get("bpc_best_mean", float("inf"))

    # Lifts vs Hebbian baseline (positive = better than baseline)
    lifts = {
        "ARM_CFRPE_COARSE_5000": (heb_bpc - coarse_bpc) if math.isfinite(coarse_bpc) and math.isfinite(heb_bpc) else float("nan"),
        "ARM_CFRPE_PER_TOKEN_ADAPTIVE": (heb_bpc - adapt_bpc) if math.isfinite(adapt_bpc) and math.isfinite(heb_bpc) else float("nan"),
        "ARM_CFRPE_PER_TOKEN_PLATEAU": (heb_bpc - plateau_bpc) if math.isfinite(plateau_bpc) and math.isfinite(heb_bpc) else float("nan"),
    }

    # Hebbian sanity (full mode only)
    hebbian_sanity_ok = (
        math.isfinite(heb_bpc) and
        abs(heb_bpc - HEBBIAN_SANITY_REF) <= HEBBIAN_SANITY_TOL
    )

    # Best ADAPTIVE arm (which of the 2 per-token arms gives biggest lift)
    best_adapt_arm = None
    best_adapt_lift = float("-inf")
    best_adapt_bpc = float("inf")
    for arm in ADAPTIVE_ARMS:
        lift_v = lifts.get(arm, float("nan"))
        if math.isfinite(lift_v) and lift_v > best_adapt_lift:
            best_adapt_lift = lift_v
            best_adapt_arm = arm
            best_adapt_bpc = by_arm_agg[arm].get("bpc_best_mean", float("inf"))

    # cv of best adaptive arm
    best_adapt_cv = float("nan")
    if best_adapt_arm:
        best_adapt_cv = by_arm_agg[best_adapt_arm].get("bpc_best_cv", float("nan"))

    arms_summary = (
        "ARM_HEBBIAN_BASELINE=bpc%.4f | ARM_CFRPE_COARSE_5000=bpc%.4f(lift%.4f) | "
        "ARM_CFRPE_PER_TOKEN_ADAPTIVE=bpc%.4f(lift%.4f) | "
        "ARM_CFRPE_PER_TOKEN_PLATEAU=bpc%.4f(lift%.4f) | best_adapt=%s lift=%.4f cv=%.4f"
    ) % (heb_bpc, coarse_bpc, lifts["ARM_CFRPE_COARSE_5000"],
         adapt_bpc, lifts["ARM_CFRPE_PER_TOKEN_ADAPTIVE"],
         plateau_bpc, lifts["ARM_CFRPE_PER_TOKEN_PLATEAU"],
         best_adapt_arm if best_adapt_arm else "none", best_adapt_lift,
         best_adapt_cv if math.isfinite(best_adapt_cv) else -1.0)

    chain_grade_bonus = bool(
        math.isfinite(best_adapt_bpc) and best_adapt_bpc <= CHAIN_GRADE_BONUS_BPC
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "lifts_vs_hebbian": {k: round(v, 4) if math.isfinite(v) else None
                              for k, v in lifts.items()},
        "best_adaptive_arm": best_adapt_arm,
        "best_adaptive_lift": round(best_adapt_lift, 4) if math.isfinite(best_adapt_lift) else None,
        "best_adaptive_bpc": round(best_adapt_bpc, 4) if math.isfinite(best_adapt_bpc) else None,
        "best_adaptive_cv": round(best_adapt_cv, 4) if math.isfinite(best_adapt_cv) else None,
        "hebbian_bpc": round(heb_bpc, 4) if math.isfinite(heb_bpc) else None,
        "coarse_cfrpe_bpc": round(coarse_bpc, 4) if math.isfinite(coarse_bpc) else None,
        "unigram_bpc": round(unigram_bpc, 4),
        "hebbian_sanity_ok": bool(hebbian_sanity_ok),
        "hebbian_baseline_bpc_ref": HEBBIAN_SANITY_REF,
        "hebbian_baseline_bpc_tol": HEBBIAN_SANITY_TOL,
        "hard_pass_lift_bar": HARD_PASS_LIFT,
        "middle_band_lift_floor": MIDDLE_BAND_LIFT_FLOOR,
        "chain_grade_bonus_bpc_bar": CHAIN_GRADE_BONUS_BPC,
        "chain_grade_bonus": chain_grade_bonus,
        "cv_bar": HP_BPC_CV_MAX,
        "n_seeds": len(units),
        "n_steps_plastic": N_STEPS_PLASTIC,
        "rule_classes": {
            "ARM_HEBBIAN_BASELINE": "one_pass_rank1_hebbian",
            "ARM_CFRPE_COARSE_5000": "global_lr_uniform",
            "ARM_CFRPE_PER_TOKEN_ADAPTIVE": "per_token_median_normalized_adaptive",
            "ARM_CFRPE_PER_TOKEN_PLATEAU": "per_token_plus_plateau_decay",
        },
        "per_token_controls": {
            "ADAPT_LR_FLOOR": ADAPT_LR_FLOOR,
            "ADAPT_LR_CEIL": ADAPT_LR_CEIL,
            "PLATEAU_WINDOW": PLATEAU_WINDOW,
            "PLATEAU_EMA_BETA": PLATEAU_EMA_BETA,
            "PLATEAU_DECAY": PLATEAU_DECAY,
            "PLATEAU_TOL": PLATEAU_TOL,
        },
        "honest_scope": (
            "cf-RPE per-token adaptive LR vs coarse uniform LR at production scale "
            "(N_DIM=8192 N_TRAIN=100k text8 V=4000). Tests A6-audit-identified "
            "untested variant: does per-sample LR weighting + plateau detection lift "
            "BPC over coarse cf-RPE (best=7.0386 at N=5000)? "
            "HARD_PASS: best adaptive lift >= %.2f bits over ARM_HEBBIAN_BASELINE "
            "AND cv <= %.2f. MIDDLE_BAND: lift in [%.2f, %.2f). HARD_FAIL: lift <= %.2f. "
            "CHAIN_GRADE_BONUS: best adaptive BPC <= %.2f. "
            "ARM_HEBBIAN_BASELINE sanity: %.4f +/- %.2f (full only). "
            "C7 LAMBDA_GRID excludes 0.0 (anti-calibration-collapse). "
            "WHAT_THIS_DOES_NOT_SHOW: does not test STDP / generalization / "
            "vs. SGD-style decay schedules without per-token weighting / "
            "encoder sensitivity. Routed remote_cpu_queue per USER 2026-06-24 refill." % (
                HARD_PASS_LIFT, HP_BPC_CV_MAX, MIDDLE_BAND_LIFT_FLOOR, HARD_PASS_LIFT,
                MIDDLE_BAND_LIFT_FLOOR, CHAIN_GRADE_BONUS_BPC,
                HEBBIAN_SANITY_REF, HEBBIAN_SANITY_TOL)),
        "cites": [
            "preregs/2026-06-24_substrate_cfrpe_per_token_adaptive_lr_v1.md",
            "experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py",
            "experiments/exp_substrate_cfrpe_n_steps_curve_extension_v2.py",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json",
        ],
    }

    # Gate 1: Hebbian baseline failed entirely
    if heb_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_HEBBIAN_BASELINE all seeds failed. Cannot compute lifts. %s" % arms_summary,
                detail)

    # Gate 2: Hebbian sanity (full mode)
    if RUN_MODE == "full" and not hebbian_sanity_ok and math.isfinite(heb_bpc):
        return ("HARD_FAIL",
                ("HARD_FAIL: ARM_HEBBIAN_BASELINE bpc=%.4f deviates from ref %.4f by > %.2f. "
                 "Methodology issue. %s" % (
                     heb_bpc, HEBBIAN_SANITY_REF, HEBBIAN_SANITY_TOL, arms_summary)),
                detail)

    # Gate 3: best adaptive arm failed entirely
    if best_adapt_arm is None or not math.isfinite(best_adapt_lift):
        return ("HARD_FAIL",
                ("HARD_FAIL: both adaptive arms failed; cannot compute lift. %s" % arms_summary),
                detail)

    # Gate 4: cv gate for best adaptive arm
    if math.isfinite(best_adapt_cv) and best_adapt_cv > HP_BPC_CV_MAX:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_HIGH_CV: best_adapt=%s cv=%.4f > %.2f bar. "
                 "lift=%.4f. High variance across seeds. %s" % (
                     best_adapt_arm, best_adapt_cv, HP_BPC_CV_MAX, best_adapt_lift,
                     arms_summary)),
                detail)

    # Primary verdict by lift
    if best_adapt_lift >= HARD_PASS_LIFT:
        msg = ("HARD_PASS: best_adapt=%s lift=%.4f >= %.2f bar (vs Hebbian baseline). "
               "Per-token adaptive LR adds real lift over coarse cf-RPE at production scale. "
               "%s. hebbian_sanity=%s. chain_grade_bonus=%s" % (
                   best_adapt_arm, best_adapt_lift, HARD_PASS_LIFT,
                   arms_summary, hebbian_sanity_ok, chain_grade_bonus))
        return ("HARD_PASS", msg, detail)
    if best_adapt_lift >= MIDDLE_BAND_LIFT_FLOOR:
        msg = ("MIDDLE_BAND: best_adapt=%s lift=%.4f in [%.2f, %.2f). "
               "Per-token adaptive helps but does not break HARD_PASS bar. "
               "%s. hebbian_sanity=%s" % (
                   best_adapt_arm, best_adapt_lift, MIDDLE_BAND_LIFT_FLOOR, HARD_PASS_LIFT,
                   arms_summary, hebbian_sanity_ok))
        return ("MIDDLE_BAND", msg, detail)
    msg = ("HARD_FAIL: best_adapt=%s lift=%.4f <= %.2f bar. "
           "Per-token adaptive does NOT add measurable lift over coarse cf-RPE at "
           "production scale. %s. hebbian_sanity=%s" % (
               best_adapt_arm, best_adapt_lift, MIDDLE_BAND_LIFT_FLOOR,
               arms_summary, hebbian_sanity_ok))
    return ("HARD_FAIL", msg, detail)


# ============================================================================
# Main loop with per-seed checkpoint
# ============================================================================

print("[config] anchor=%s N_DIM=%d mode=%s seeds=%s N_STEPS_PLASTIC=%d device=%s" % (
    ANCHOR_NAME, N_DIM, RUN_MODE, SEEDS, N_STEPS_PLASTIC, str(DEVICE)), flush=True)

if DEVICE.type == "cuda":
    print("[gpu] %s" % torch.cuda.get_device_name(0), flush=True)
else:
    print("[device] CPU (no CUDA available; remote_cpu route)", flush=True)

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
    "ARMS": ARMS,
    "N_STEPS_PLASTIC": N_STEPS_PLASTIC,
    "CFRPE_LR": CFRPE_LR,
    "INGEST_BATCH": INGEST_BATCH,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "LAMBDA_GRID": LAMBDA_GRID,
    "TEMP_GRID": TEMP_GRID,
    "ADAPT_LR_FLOOR": ADAPT_LR_FLOOR,
    "ADAPT_LR_CEIL": ADAPT_LR_CEIL,
    "PLATEAU_WINDOW": PLATEAU_WINDOW,
    "PLATEAU_EMA_BETA": PLATEAU_EMA_BETA,
    "PLATEAU_DECAY": PLATEAU_DECAY,
    "PLATEAU_TOL": PLATEAU_TOL,
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
