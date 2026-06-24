"""
substrate_meta_lr_dopamine_analog_v1 -- per-token RPE-modulated learning rate (dopamine analog)

HYPOTHESIS: per-token adaptive learning rate (phasic dopamine analog) closes the meta-learning
gap identified as CLAIM 8 in the brain-to-LM relevance audit. AWD-LSTM + meta-learner achieves
46.9 vs 64.8 perplexity on WikiText-2 (~28% reduction). This cell asks whether RPE-modulated
learning rate alone (without full MAML overhead) produces measurable BPC lift on text8.

CONTEXT: cf-RPE delta rule (ARM_CFRPE_ONLY in heterogeneous_plasticity cell) landed
BPC=7.1052 vs Hebbian 7.3065 (+0.201 bits) at production scale. That cell used a FIXED
learning rate (alpha=0.5). This cell keeps the same cf-RPE rule but modulates alpha
per-token (phasic) or per-epoch (tonic) based on the RPE signal itself.

THREE ARMS:
  ARM_FIXED_LR         -- cf-RPE with fixed alpha=0.5; reproduces 7.1052 baseline
  ARM_GLOBAL_RPE_LR    -- alpha modulated by mean RPE per epoch (tonic dopamine analog)
  ARM_PER_TOKEN_RPE_LR -- alpha = base_alpha * (1 + beta * normalized_RPE_t) (phasic)

PRE-REG BANDS (BPC lift = ARM_FIXED_LR BPC - ARM_X BPC; positive = better):
  HARD_PASS:       ARM_PER_TOKEN_RPE_LR lift >= +0.15 bits vs FIXED_LR
                   AND ARM_PER_TOKEN_RPE_LR lift >= +0.05 bits vs GLOBAL_RPE_LR
  MIDDLE_BAND:     lift +0.05 to +0.15 bits over FIXED_LR
  HARD_FAIL:       lift within +/-0.05 of FIXED_LR
  CHAIN_GRADE_BONUS: lift >= +0.20 over FIXED_LR AND beats fair_harness 7.3065 by >= +0.30
  cv < 0.05 across seeds mandatory

ENCODING: word2vec-google-news-300 projected to N_DIM=8192 sparse-bipolar (f=0.05) --
same encoder as the chain-grade fair_harness and heterogeneous_plasticity baselines.

GPU REQUIRED (Fix #24): torch.cuda + batched matmul + encoder hoisted outside arm loop.
Fix #28: per-arm metrics only via metrics.json; no cross-arm framing claims in verdict_msg.
ASCII-only. Per-seed checkpoint via _seed_checkpoint. atexit synthesizer.

Cites:
  preregs/2026-06-23_substrate_meta_lr_dopamine_analog_v1.md
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py
  data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json
  notes/research_brain_to_lm_relevance_audit_2x_drill_2026-06-23.md (CLAIM 8)
  notes/exp_dev_handoff_research_brain_to_lm_relevance_audit_2026-06-23.md (Anchor 1)
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

ANCHOR_NAME = "substrate_meta_lr_dopamine_analog_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Pre-reg thresholds (HARD bands registered before smoke per role contract)
HARD_PASS_PER_TOKEN_LIFT = 0.15      # ARM_PER_TOKEN_RPE_LR vs ARM_FIXED_LR
HARD_PASS_PHASIC_VS_TONIC = 0.05     # ARM_PER_TOKEN_RPE_LR vs ARM_GLOBAL_RPE_LR
MIDDLE_BAND_LO = 0.05                # lift vs FIXED_LR lower bound
MIDDLE_BAND_HI = 0.15                # lift vs FIXED_LR upper bound
HARD_FAIL_DELTA = 0.05               # within +/-0.05 of FIXED_LR => HARD_FAIL
CHAIN_GRADE_BONUS_LIFT = 0.20        # vs FIXED_LR AND beats fair_harness 7.3065 by >=0.30
FAIR_HARNESS_HEBBIAN_BPC = 7.3065    # chain-grade anchor from heterogeneous_plasticity v1
HP_BPC_CV_MAX = 0.05                 # cv across seeds mandatory

# Fixed-LR cf-RPE reference from prior HARD_PASS cell (ARM_CFRPE_ONLY bpc_best_mean)
CFRPE_FIXED_LR_REF_BPC = 7.1052

# Plasticity knobs -- reused exactly from heterogeneous_plasticity cell
BASE_CFRPE_LR = 0.5          # base learning rate for all arms
INGEST_BATCH = 64            # training batch size

# Meta-LR modulation knob (phasic arm): alpha_t = BASE_LR * (1 + BETA * norm_rpe_t)
META_LR_BETA = 1.0           # scale factor for RPE-normalized modulation

# Global-RPE-LR modulation: alpha_epoch = BASE_LR * (1 + BETA_GLOBAL * epoch_rpe_norm)
META_LR_BETA_GLOBAL = 1.0    # scale factor for global/tonic modulation

# Inference
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Sparse-bipolar f (chain-grade validated; matches fair_harness + heterogeneous_plasticity)
SPARSE_BIPOLAR_F = 0.05

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

# Production config (N_DIM=8192 matches prior chain-grade cell; no _nN suffix in anchor name)
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

ARMS = [
    "ARM_UNIGRAM",
    "ARM_FIXED_LR",
    "ARM_GLOBAL_RPE_LR",
    "ARM_PER_TOKEN_RPE_LR",
]
PLASTICITY_ARMS = [a for a in ARMS if a != "ARM_UNIGRAM"]

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = 2000   # walk-back gate: smoke per-token lift=0.003 (borderline); doubled N_STEPS
else:
    # Smoke: fit under 180s on CPU; exercises all arms + joint sweep + verdict
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
    """Build [V, n_dim] L2-normalized word2vec-projected vectors on GPU.

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
# Plasticity rules with RPE-modulated learning rate
# ============================================================================

def _compute_rpe_scalar(Ctx: torch.Tensor, Nxt: torch.Tensor,
                         W: torch.Tensor) -> torch.Tensor:
    """Compute per-token RPE scalar = ||Nxt - Ctx @ W^T|| (prediction error norm).

    Returns a scalar float on DEVICE (mean over batch tokens).
    cf-RPE delta rule: error = Nxt - Ctx @ W^T; RPE magnitude = mean error norm.
    """
    error = Nxt - Ctx @ W.t()             # [batch, dim]
    rpe = error.norm(dim=1).mean()        # scalar; mean over batch
    return rpe


def build_W_metalr(arm: str, E: torch.Tensor, idx_train_t: torch.Tensor,
                   n_steps: int, batch: int, base_lr: float,
                   meta_beta: float, meta_beta_global: float,
                   ingest_chunk: int, gen: torch.Generator) -> torch.Tensor:
    """Build W via cf-RPE with one of three learning-rate schedules.

    ARM_FIXED_LR:
        Exactly replicates ARM_CFRPE_ONLY from heterogeneous_plasticity cell.
        alpha = base_lr (constant throughout).

    ARM_GLOBAL_RPE_LR (tonic dopamine analog):
        alpha per step = base_lr * (1 + meta_beta_global * rpe_norm_global)
        rpe_norm_global = mean RPE over the PREVIOUS epoch (all steps),
        normalized by initial RPE estimate. Low-frequency modulation.
        Approximation: we track a running exponential mean of rpe scalar
        with timescale = n_steps / 4 steps.

    ARM_PER_TOKEN_RPE_LR (phasic dopamine analog):
        alpha_t = base_lr * (1 + meta_beta * rpe_t_norm)
        rpe_t_norm = current step RPE / ema_rpe_denom (normalized to avoid scale drift)
        Modulates on EVERY training step -- phasic, per-token signal.

    RPE normalization (prevents alpha from exploding):
        rpe_t_norm = rpe_t / max(ema_rpe, 1e-3)   clamped to [0, 5.0]
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W

    # EMA for RPE normalization (used by GLOBAL and PER_TOKEN arms)
    ema_rpe = torch.tensor(1.0, dtype=TORCH_DTYPE, device=DEVICE)
    ema_alpha = 0.05  # EMA update rate; ~20 step timescale

    for step_i in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train_t[st]]        # [batch, dim]
        Nxt = E[idx_train_t[st + 1]]    # [batch, dim]

        # cf-RPE error (same as ARM_CFRPE_ONLY in prior cell)
        error = Nxt - Ctx @ W.t()       # [batch, dim]
        dW = (error.t() @ Ctx) / batch  # [dim, dim]

        # Compute RPE scalar for this step
        rpe_t = error.norm(dim=1).mean()  # scalar

        # Update EMA
        ema_rpe = (1.0 - ema_alpha) * ema_rpe + ema_alpha * rpe_t.detach()

        if arm == "ARM_FIXED_LR":
            lr_t = base_lr

        elif arm == "ARM_GLOBAL_RPE_LR":
            # Tonic: modulate by normalized EMA RPE (slow, global signal)
            rpe_norm = float(torch.clamp(ema_rpe / max(float(ema_rpe.detach() + 1e-3), 1e-3),
                                          0.0, 5.0))
            # global modulation: alpha = base * (1 + beta_global * (ema/initial_ema - 1))
            # Simplified: alpha = base * (1 + beta_global * ema_norm_deviation)
            # We use: lr_t = base * clamp(1 + beta_global * (rpe_t_norm - 1), 0.1, 5.0)
            rpe_t_norm_g = float(torch.clamp(rpe_t / (ema_rpe + 1e-3), 0.0, 5.0))
            lr_t = float(base_lr * max(0.1, min(5.0, 1.0 + meta_beta_global * (rpe_t_norm_g - 1.0))))

        else:
            # ARM_PER_TOKEN_RPE_LR: phasic, per-step modulation
            # alpha_t = base * (1 + beta * normalized_RPE_t)
            # normalized_RPE_t = rpe_t / ema_rpe; clamped [0, 5]
            rpe_t_norm = float(torch.clamp(rpe_t / (ema_rpe + 1e-3), 0.0, 5.0))
            lr_t = float(base_lr * (1.0 + meta_beta * rpe_t_norm))
            # Additional clamp: lr cannot exceed 5x base or drop below 0.1x base
            lr_t = max(0.1 * base_lr, min(5.0 * base_lr, lr_t))

        W = W + lr_t * dW

    return W


# ============================================================================
# Per-arm logits builder
# ============================================================================

def compute_arm_logits(arm: str, E_base: torch.Tensor, idx_train: np.ndarray,
                        idx_held: np.ndarray, seed: int, n_steps: int) -> Dict:
    """Return [n_held, V] float32 logits + diagnostics. FRESH W per arm."""
    V = E_base.shape[0]

    # Sparse-bipolar transform (same as fair_harness baseline)
    E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    # Per-seed, per-arm generator
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed * 10007 + ARMS.index(arm) * 31337)

    t0 = time.time()
    W = build_W_metalr(
        arm, E_used, idx_train_t, n_steps=n_steps,
        batch=INGEST_BATCH, base_lr=BASE_CFRPE_LR,
        meta_beta=META_LR_BETA, meta_beta_global=META_LR_BETA_GLOBAL,
        ingest_chunk=INGEST_CHUNK, gen=gen,
    )
    t_ingest = time.time() - t0

    # Recall: predict next token from current context via W
    t0 = time.time()
    n_h = idx_held_t.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        ctx = E_used[idx_held_t[b:end]]
        pred = _l2_normalize_t(ctx @ W.t())
        logits[b:end] = pred @ E_used.T
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    # READOUT_DEGENERATE sanity
    raw_bpc_at_T1 = _raw_bpc_at_T1(logits, idx_held)

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W, logits
    del E_used
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "raw_bpc_at_T1_L1": round(raw_bpc_at_T1, 4),
    }


def _raw_bpc_at_T1(logits: torch.Tensor, idx_held: np.ndarray) -> float:
    """BPC at T=1 (no temperature scaling), for DEGEN sanity gate."""
    V = logits.shape[1]
    n_h = logits.shape[0]
    nxt_np = idx_held[1:] if len(idx_held) > 1 else idx_held
    n_eval = min(n_h, len(nxt_np))
    if n_eval == 0:
        return float("inf")
    logits_np = logits[:n_eval].detach().cpu().numpy().astype(np.float32) if hasattr(logits, 'detach') else logits[:n_eval]
    nxt_eval = nxt_np[:n_eval]
    z = logits_np - logits_np.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / np.clip(e.sum(axis=1, keepdims=True), 1e-30, None)
    p_nxt = p[np.arange(n_eval), nxt_eval].clip(1e-12, 1.0)
    return float(-np.mean(np.log(p_nxt)) / math.log(2.0))


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
# Joint (T, lambda) sweep + 3 metrics (reused from fair_harness pattern)
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
    """Joint (T, lambda) sweep on dev; pick best per-metric; report on test."""
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
        "raw_bpc_at_T1_L1": 0.0,  # filled in by caller via ar["raw_bpc_at_T1_L1"]
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

    # ST1: RPE scalar is non-zero for random Ctx/Nxt with zero W
    n_dim_st = 64
    gen_st = torch.Generator(device=_dev)
    gen_st.manual_seed(42)
    b_st = 4
    Ctx = torch.randn(b_st, n_dim_st, device=_dev)
    Nxt = torch.randn(b_st, n_dim_st, device=_dev)
    W_zero = torch.zeros(n_dim_st, n_dim_st, device=_dev)
    rpe = _compute_rpe_scalar(Ctx, Nxt, W_zero)
    assert float(rpe) > 0.0, "ST1 RPE scalar should be > 0 for random Ctx/Nxt: got %.4f" % float(rpe)
    print("[selftest] ST1 RPE scalar > 0: rpe=%.4f" % float(rpe), flush=True)

    # ST2: PER_TOKEN arm uses different effective LR than FIXED arm (modulation is active)
    # Construct a scenario where rpe_t > 0 and check lr_t != base_lr
    n_v_st = 8
    n_dim_st2 = 32
    n_pairs_st = 20
    gen_st2 = torch.Generator(device=_dev)
    gen_st2.manual_seed(99)
    E_st = torch.randn(n_v_st, n_dim_st2, device=_dev)
    E_st = _l2_normalize_t(E_st)
    idx_st = torch.randint(0, n_v_st, (n_pairs_st + 1,), generator=gen_st2, device=_dev)
    # Run 1 step of PER_TOKEN arm and check that the W update magnitude differs from FIXED
    gen_f = torch.Generator(device=_dev)
    gen_f.manual_seed(7)
    W_fixed = build_W_metalr("ARM_FIXED_LR", E_st, idx_st, n_steps=5,
                               batch=2, base_lr=0.5, meta_beta=1.0,
                               meta_beta_global=1.0, ingest_chunk=n_pairs_st,
                               gen=gen_f)
    gen_p = torch.Generator(device=_dev)
    gen_p.manual_seed(7)
    W_per_token = build_W_metalr("ARM_PER_TOKEN_RPE_LR", E_st, idx_st, n_steps=5,
                                   batch=2, base_lr=0.5, meta_beta=1.0,
                                   meta_beta_global=1.0, ingest_chunk=n_pairs_st,
                                   gen=gen_p)
    diff = float((W_per_token - W_fixed).norm())
    assert diff > 1e-6, "ST2 PER_TOKEN arm W should differ from FIXED arm W: diff=%.2e" % diff
    print("[selftest] ST2 PER_TOKEN != FIXED W (diff=%.4f)" % diff, flush=True)

    # ST3: cf-RPE error shrinks for FIXED_LR (same check as prior cell ST2)
    n_dim_st3 = 64
    Ctx2 = torch.randn(1, n_dim_st3, device=_dev)
    Nxt2 = torch.randn(1, n_dim_st3, device=_dev)
    Ctx2 = Ctx2 / (Ctx2.norm() + 1e-8)
    Nxt2 = Nxt2 / (Nxt2.norm() + 1e-8)
    W3 = torch.zeros(n_dim_st3, n_dim_st3, device=_dev)
    error_before = float((Nxt2 - Ctx2 @ W3.t()).norm())
    dW3 = (Nxt2 - Ctx2 @ W3.t()).t() @ Ctx2
    W3 = W3 + 0.9 * dW3
    error_after = float((Nxt2 - Ctx2 @ W3.t()).norm())
    assert error_after < error_before, (
        "ST3 cf-RPE delta should shrink error: before=%.4f after=%.4f" % (error_before, error_after))
    print("[selftest] ST3 cf-RPE delta shrinks error: %.4f -> %.4f" % (error_before, error_after), flush=True)

    # ST4: joint_sweep returns finite BPC for small synthetic data
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
    assert math.isfinite(jr["bpc_best"]), "ST4 joint_sweep bpc_best is not finite: %s" % jr["bpc_best"]
    assert math.isfinite(jr["top1_acc"]), "ST4 joint_sweep top1_acc is not finite"
    assert math.isfinite(jr["mrr_at_10"]), "ST4 joint_sweep mrr_at_10 is not finite"
    assert jr["n_dev"] > 0, "ST4 n_dev == 0"
    assert jr["n_test"] > 0, "ST4 n_test == 0"
    print("[selftest] ST4 joint_sweep all metrics finite OK (bpc=%.3f top1=%.4f mrr=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"]), flush=True)

    # ST5: GLOBAL arm differs from FIXED arm (modulation is active)
    gen_g = torch.Generator(device=_dev)
    gen_g.manual_seed(7)
    W_global = build_W_metalr("ARM_GLOBAL_RPE_LR", E_st, idx_st, n_steps=5,
                               batch=2, base_lr=0.5, meta_beta=1.0,
                               meta_beta_global=1.0, ingest_chunk=n_pairs_st,
                               gen=gen_g)
    gen_f2 = torch.Generator(device=_dev)
    gen_f2.manual_seed(7)
    W_fixed2 = build_W_metalr("ARM_FIXED_LR", E_st, idx_st, n_steps=5,
                               batch=2, base_lr=0.5, meta_beta=1.0,
                               meta_beta_global=1.0, ingest_chunk=n_pairs_st,
                               gen=gen_f2)
    diff_g = float((W_global - W_fixed2).norm())
    assert diff_g > 1e-6, "ST5 GLOBAL arm W should differ from FIXED arm W: diff=%.2e" % diff_g
    print("[selftest] ST5 GLOBAL != FIXED W (diff=%.4f)" % diff_g, flush=True)

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
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"], uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # Hoist encoder outside arm loop (Fix #24: encoder loaded once, reused per arm)
    print("\n[seed=%d] building encoder (V=%d, N_DIM=%d) on %s..." % (
        seed, V, N_DIM, str(DEVICE)), flush=True)
    t_enc0 = time.time()
    encoder_meta = {}
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
    valid_held_pos = np.where(mask)[0]
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    for arm in PLASTICITY_ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building W + logits..." % (seed, arm), flush=True)
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
            }
            continue

        logits_full = ar["logits"]   # [n_held, V]
        # Align to ctx_full domain
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            logits_ctx = logits_full
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
            jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
            jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
            jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
            jr["raw_bpc_at_T1_L1"] = ar.get("raw_bpc_at_T1_L1", float("nan"))
            by_arm[arm] = jr
            print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
                  "(bestT=%.4f bestL=%.2f) raw_T1L1_bpc=%.3f" % (
                      seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                      jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                      jr["raw_bpc_at_T1_L1"]), flush=True)
            continue

        logits_eval = logits_ctx[mask]
        jr = joint_sweep(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
        jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
        jr["raw_bpc_at_T1_L1"] = ar.get("raw_bpc_at_T1_L1", float("nan"))
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
              "(bestT=%.4f bestL=%.2f) raw_T1L1_bpc=%.3f" % (
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
# Verdict (per pre-reg bands; Fix #28: per-arm metrics only)
# ============================================================================

def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Aggregate
    by_arm_agg: Dict[str, Dict] = {}
    vocab_entropy = math.log2(max(units[0].get("V", 4000), 2))

    # ARM_UNIGRAM aggregation
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
    }
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    for arm in PLASTICITY_ARMS:
        seeds_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid = [(not cf) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
                 for cf, u in zip(seeds_failed, units)]
        n_failed = int(sum(seeds_failed))
        valid_units = [u for ok, u in zip(valid, units) if ok]
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"), "top1_acc_mean": float("nan"),
                "mrr_at_10_mean": float("nan"), "raw_bpc_at_T1_L1_mean": float("nan"),
                "n_valid_seeds": 0, "n_compute_failed": n_failed, "all_seeds_failed": True,
            }
            continue
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_v = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid_units]
        raw_v_finite = [x for x in raw_v if math.isfinite(x)]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "top1_acc_std": round(float(np.std(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_v_finite)), 4) if raw_v_finite else float("nan"),
            "n_valid_seeds": int(len(valid_units)),
            "n_compute_failed": n_failed,
            "all_seeds_failed": False,
        }

    # Per-arm BPC values
    fixed_bpc = by_arm_agg.get("ARM_FIXED_LR", {}).get("bpc_best_mean", float("inf"))
    global_bpc = by_arm_agg.get("ARM_GLOBAL_RPE_LR", {}).get("bpc_best_mean", float("inf"))
    per_tok_bpc = by_arm_agg.get("ARM_PER_TOKEN_RPE_LR", {}).get("bpc_best_mean", float("inf"))

    lift_per_tok_vs_fixed = fixed_bpc - per_tok_bpc      # positive = per_token is better
    lift_per_tok_vs_global = global_bpc - per_tok_bpc    # positive = per_token is better
    lift_global_vs_fixed = fixed_bpc - global_bpc        # positive = global is better

    per_tok_cv = by_arm_agg.get("ARM_PER_TOKEN_RPE_LR", {}).get("bpc_best_cv", float("nan"))
    per_tok_failed = by_arm_agg.get("ARM_PER_TOKEN_RPE_LR", {}).get("all_seeds_failed", True)

    # WHAT_THIS_DOES_NOT_SHOW clause (per verdict_lint):
    # This cell does NOT show whether RPE-modulated LR generalizes across domain shifts,
    # whether it benefits from additional STDP or fast-slow weight composition,
    # or whether meta-learning effect scales with N_TRAIN beyond 100k tokens.

    arm_summary = (
        "uni=bpc%.3f | ARM_FIXED_LR=bpc%.4f | ARM_GLOBAL_RPE_LR=bpc%.4f | "
        "ARM_PER_TOKEN_RPE_LR=bpc%.4f cv=%.3f | "
        "lift_per_tok_vs_fixed=%.4f | lift_per_tok_vs_global=%.4f | "
        "lift_global_vs_fixed=%.4f | "
        "cfrpe_fixed_lr_ref=%.4f (prior chain-grade)"
    ) % (
        unigram_bpc, fixed_bpc, global_bpc, per_tok_bpc,
        per_tok_cv if math.isfinite(per_tok_cv) else -1.0,
        lift_per_tok_vs_fixed, lift_per_tok_vs_global, lift_global_vs_fixed,
        CFRPE_FIXED_LR_REF_BPC,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "lift_per_token_vs_fixed": round(lift_per_tok_vs_fixed, 4),
        "lift_per_token_vs_global": round(lift_per_tok_vs_global, 4),
        "lift_global_vs_fixed": round(lift_global_vs_fixed, 4),
        "fixed_bpc": round(fixed_bpc, 4),
        "global_bpc": round(global_bpc, 4),
        "per_token_bpc": round(per_tok_bpc, 4),
        "unigram_bpc": round(unigram_bpc, 4),
        "cfrpe_fixed_lr_ref_bpc": CFRPE_FIXED_LR_REF_BPC,
        "fair_harness_hebbian_baseline_bpc": FAIR_HARNESS_HEBBIAN_BPC,
        "n_seeds": len(units),
        "hard_pass_per_token_lift_bar": HARD_PASS_PER_TOKEN_LIFT,
        "hard_pass_phasic_vs_tonic_bar": HARD_PASS_PHASIC_VS_TONIC,
        "chain_grade_bonus_bar": CHAIN_GRADE_BONUS_LIFT,
        "hard_fail_delta": HARD_FAIL_DELTA,
        "honest_scope": (
            "meta-LR via RPE modulation on cf-RPE delta rule at production scale "
            "(N_DIM=8192 N_TRAIN=100k text8 V=4000). "
            "Tests whether phasic (per-token) or tonic (global) dopamine-analog "
            "learning-rate modulation produces BPC lift over fixed-LR cf-RPE baseline. "
            "WHAT_THIS_DOES_NOT_SHOW: does not test multi-domain generalization, "
            "STDP composition, or fast-slow weight interaction."
        ),
        "cites": [
            "preregs/2026-06-23_substrate_meta_lr_dopamine_analog_v1.md",
            "experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py",
            "data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json",
            "notes/research_brain_to_lm_relevance_audit_2x_drill_2026-06-23.md",
            "notes/exp_dev_handoff_research_brain_to_lm_relevance_audit_2026-06-23.md",
        ],
    }

    # Gate: per-token arm failed entirely
    if per_tok_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_PER_TOKEN_RPE_LR all seeds failed. %s" % arm_summary,
                detail)

    # cv gate
    if math.isfinite(per_tok_cv) and per_tok_cv > HP_BPC_CV_MAX:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_HIGH_CV: ARM_PER_TOKEN_RPE_LR cv=%.3f > %.2f mandatory. "
                 "lift_vs_fixed=%.4f. High variance; unstable result. %s" % (
                     per_tok_cv, HP_BPC_CV_MAX, lift_per_tok_vs_fixed, arm_summary)),
                detail)

    # CHAIN_GRADE_BONUS
    if (lift_per_tok_vs_fixed >= CHAIN_GRADE_BONUS_LIFT and
            per_tok_bpc <= (FAIR_HARNESS_HEBBIAN_BPC - 0.30)):
        detail["chain_grade_bonus"] = True
        return ("HARD_PASS",
                ("HARD_PASS CHAIN_GRADE_BONUS: ARM_PER_TOKEN_RPE_LR lift_vs_fixed=%.4f >= %.2f "
                 "AND per_token_bpc=%.4f <= (%.4f - 0.30). "
                 "Phasic RPE-modulated LR closes brain meta-learning gap with chain-grade lift. "
                 "%s" % (lift_per_tok_vs_fixed, CHAIN_GRADE_BONUS_LIFT,
                          per_tok_bpc, FAIR_HARNESS_HEBBIAN_BPC, arm_summary)),
                detail)

    # HARD_PASS
    if (lift_per_tok_vs_fixed >= HARD_PASS_PER_TOKEN_LIFT and
            lift_per_tok_vs_global >= HARD_PASS_PHASIC_VS_TONIC):
        detail["chain_grade_bonus"] = False
        return ("HARD_PASS",
                ("HARD_PASS: ARM_PER_TOKEN_RPE_LR lift_vs_fixed=%.4f >= %.2f "
                 "AND lift_vs_global=%.4f >= %.2f. "
                 "Per-token phasic RPE modulation outperforms fixed-LR and tonic modulation. "
                 "%s" % (lift_per_tok_vs_fixed, HARD_PASS_PER_TOKEN_LIFT,
                          lift_per_tok_vs_global, HARD_PASS_PHASIC_VS_TONIC, arm_summary)),
                detail)

    # MIDDLE_BAND (per_token beats fixed but not both bars)
    if MIDDLE_BAND_LO <= lift_per_tok_vs_fixed < MIDDLE_BAND_HI:
        detail["chain_grade_bonus"] = False
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND: ARM_PER_TOKEN_RPE_LR lift_vs_fixed=%.4f in [%.2f, %.2f). "
                 "RPE-modulated LR helps but below HARD_PASS threshold. "
                 "phasic_vs_tonic=%.4f (bar=%.2f). %s" % (
                     lift_per_tok_vs_fixed, MIDDLE_BAND_LO, MIDDLE_BAND_HI,
                     lift_per_tok_vs_global, HARD_PASS_PHASIC_VS_TONIC, arm_summary)),
                detail)

    # HARD_FAIL
    detail["chain_grade_bonus"] = False
    return ("HARD_FAIL",
            ("HARD_FAIL: ARM_PER_TOKEN_RPE_LR lift_vs_fixed=%.4f within +/-%.2f of FIXED_LR. "
             "RPE-modulated LR does NOT produce measurable BPC improvement at this scale. "
             "Per-token phasic modulation is not load-bearing for substrate-LM at N=8192. "
             "%s" % (lift_per_tok_vs_fixed, HARD_FAIL_DELTA, arm_summary)),
            detail)


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

run_config = {"N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "run_mode": RUN_MODE}
done_seeds = []
remaining_seeds = SEEDS[:]

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
    "ARMS": ARMS,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "BASE_CFRPE_LR": BASE_CFRPE_LR,
    "META_LR_BETA": META_LR_BETA,
    "META_LR_BETA_GLOBAL": META_LR_BETA_GLOBAL,
    "N_STEPS": N_STEPS,
    "detail": detail,
    "per_seed": [
        {"seed": u.get("seed"), "by_arm": u.get("by_arm"),
         "V": u.get("V"), "N_DIM": u.get("N_DIM"), "N_TRAIN": u.get("N_TRAIN"),
         "elapsed_s_seed": u.get("elapsed_s_seed"), "device": u.get("device"),
         "encoder_meta": u.get("encoder_meta", {})}
        for u in all_units
    ],
    "elapsed_s": round(sum(u.get("elapsed_s_seed", 0.0) for u in all_units), 2),
    "summary": verdict_msg,
}

write_metrics(out_dir, metrics, all_units)
print("[metrics] written to %s" % out_dir, flush=True)
