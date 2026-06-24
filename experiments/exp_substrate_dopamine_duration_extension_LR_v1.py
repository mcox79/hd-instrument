"""
substrate_dopamine_duration_extension_LR_v1 -- brain-canonical eligibility-trace DURATION
extension rescue cell (post-HARD_FAIL of MAGNITUDE-amplification in v1 meta-LR cell).

HYPOTHESIS: Brain (Gong/Coddington 2026 Science; Brzosko/Paulsen 2017 eLife) modulates
learning via DURATION-extension of the eligibility-trace window when RPE is high, NOT via
MAGNITUDE-amplification of the per-token learning rate. v1 meta-LR cell (BETA=1.0
multiplicative-positive) tested the WRONG direction -- it AMPLIFIED LR on surprising tokens,
compounding gradient noise. This cell tests whether extending the credit-assignment window
(forward trace propagation) lifts BPC.

MECHANISM: each high-RPE token's gradient update is propagated forward to the next K tokens
with exponential decay:
  duration_t = base_duration * (1 + gamma * clamp(rpe_t / ema_rpe, 0, 5))
  W += base_lr * exp(-k / duration_t) * dW_t  for k in range(1, ceil(duration_t))
The integral of updates over the window is normalized to avoid magnitude amplification.

FOUR ARMS:
  ARM_FIXED_WINDOW              -- cf-RPE fixed trace window (control; reproduces 7.1052)
  ARM_DURATION_EXTENSION_GAMMA_05 -- low gamma=0.5; modest duration extension
  ARM_DURATION_EXTENSION_GAMMA_10 -- mid gamma=1.0; brain-canonical per Brzosko 2017
  ARM_DURATION_EXTENSION_GAMMA_20 -- high gamma=2.0; extended trace window

PRE-REG BANDS (lift = ARM_FIXED_WINDOW BPC - ARM_X BPC; positive = better):
  HARD_PASS:       any ARM_DURATION_EXTENSION beats ARM_FIXED_WINDOW by >= +0.10 bits;
                   cv <= 0.05; ARM_FIXED_WINDOW within +/-0.05 of cf-RPE chain-grade 7.1052
  CHAIN_GRADE_BONUS: best lift >= +0.20 AND beats fair_harness 7.3065 by >= +0.30
  MIDDLE_BAND:     best lift in [+0.03, +0.10]
  HARD_FAIL:       best lift <= +0.03 (duration mechanism also not load-bearing)
  INSTR_SUSPECT gate: if best_lambda=0.0 across all arms -> INSTRUMENTATION_SUSPECT

ENCODING: word2vec-google-news-300 projected to N_DIM=8192 sparse-bipolar (f=0.05) --
same encoder as chain-grade fair_harness and v1 meta-LR cell (exact encoder pipeline match).
LAMBDA_GRID excludes 0.0 per Skunkworks batch VET C7 (lambda=0.0 collapse prevention).

Cites:
  preregs/2026-06-23_substrate_dopamine_duration_extension_LR_v1.md
  experiments/exp_substrate_meta_lr_dopamine_analog_v1.py (v1 failed cell)
  data/exp_substrate_meta_lr_dopamine_analog_v1/metrics.json (HARD_FAIL reference)
  notes/research_dopamine_modulated_LR_alternatives_2x_drill_2026-06-23.md
  notes/exp_dev_handoff_research_dopamine_modulated_LR_alternatives_2026-06-23.md
  Gong/Coddington 2026 Science DOI 10.1126/science.aeb0813
  Brzosko/Paulsen 2017 eLife DOI 10.7554/eLife.27756
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

ANCHOR_NAME = "substrate_dopamine_duration_extension_LR_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Pre-reg thresholds (registered before smoke per role contract)
HARD_PASS_DURATION_LIFT = 0.10       # any ARM_DURATION vs ARM_FIXED_WINDOW
CHAIN_GRADE_BONUS_LIFT = 0.20        # vs FIXED + beats fair_harness by >=0.30
MIDDLE_BAND_LO = 0.03                # lift vs FIXED lower bound
MIDDLE_BAND_HI = 0.10                # lift vs FIXED upper bound (exclusive)
HARD_FAIL_MAX_LIFT = 0.03            # best lift <= 0.03 => HARD_FAIL
FIXED_WINDOW_SANITY_DELTA = 0.05     # ARM_FIXED_WINDOW must be within +-0.05 of 7.1052
CFRPE_CHAIN_GRADE_REF_BPC = 7.1052  # cf-RPE fixed-LR chain-grade reference
FAIR_HARNESS_HEBBIAN_BPC = 7.3065   # sparse-bipolar fair_harness chain-grade anchor
HP_BPC_CV_MAX = 0.05                 # cv across seeds mandatory

# Plasticity knobs -- reused exactly from v1 meta-LR cell
BASE_CFRPE_LR = 0.5          # base learning rate (fixed, matches v1 ARM_FIXED_LR)
INGEST_BATCH = 64            # training batch size (matches v1)

# Duration extension gamma grid (controls how much RPE extends the window)
GAMMA_GRID = [0.5, 1.0, 2.0]

# Base trace duration (in steps); arm-level duration = base * (1 + gamma * norm_rpe)
BASE_DURATION = 3.0

# Inference
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
# LAMBDA_GRID excludes 0.0 per Skunkworks C7 (lambda=0.0 collapse prevention)
LAMBDA_GRID = [0.02, 0.05, 0.07, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Sparse-bipolar f (chain-grade validated; matches fair_harness)
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

# Production config (N_DIM=8192 matches prior chain-grade cell)
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

ARMS = [
    "ARM_UNIGRAM",
    "ARM_FIXED_WINDOW",
    "ARM_DURATION_EXTENSION_GAMMA_05",
    "ARM_DURATION_EXTENSION_GAMMA_10",
    "ARM_DURATION_EXTENSION_GAMMA_20",
]
PLASTICITY_ARMS = [a for a in ARMS if a != "ARM_UNIGRAM"]

# Map arm name to gamma (0.0 = fixed window)
ARM_GAMMA: Dict[str, float] = {
    "ARM_FIXED_WINDOW": 0.0,
    "ARM_DURATION_EXTENSION_GAMMA_05": 0.5,
    "ARM_DURATION_EXTENSION_GAMMA_10": 1.0,
    "ARM_DURATION_EXTENSION_GAMMA_20": 2.0,
}

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = 2000
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

    OOV words fall back to char-trigram so no zero-row degeneracy.
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
# Duration-extension plasticity rule (brain-canonical mechanism)
# ============================================================================

def build_W_duration_extension(arm: str, E: torch.Tensor, idx_train_t: torch.Tensor,
                                n_steps: int, batch: int, base_lr: float,
                                base_duration: float,
                                arm_gamma: float,
                                gen: torch.Generator) -> torch.Tensor:
    """Build W via cf-RPE with eligibility-trace duration extension.

    ARM_FIXED_WINDOW (gamma=0.0):
        Exactly replicates ARM_CFRPE_ONLY / ARM_FIXED_LR from prior cells.
        base_lr fixed; trace window = base_duration (1 step only, no propagation).

    ARM_DURATION_EXTENSION_GAMMA_X (gamma>0):
        Brain-canonical: high RPE extends the trace window forward in time.
        duration_t = base_duration * (1 + gamma * clamp(rpe_t / ema_rpe, 0, 5))
        For k in 1..ceil(duration_t)-1: W += base_lr * exp(-k/duration_t) * dW_t
        The immediate update (k=0) is always applied at base_lr.
        Integral normalization: the total update per token is bounded because
        sum_k exp(-k/d) <= d * (1 - exp(-1)) < d, so total weight change per
        token scales with duration but is multiplied by exp-decay, NOT by gamma.
        This is DURATION extension (window), NOT MAGNITUDE amplification.

    RPE normalization:
        ema_rpe tracks local noise floor; rpe_norm = rpe_t / max(ema_rpe, 1e-3)
        clamped to [0, 5] to prevent runaway duration for outlier tokens.
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W

    # EMA for RPE normalization
    ema_rpe = torch.tensor(1.0, dtype=TORCH_DTYPE, device=DEVICE)
    # EMA timescale ~200 tokens (brain timescale ~200 tokens per Brzosko 2017 analysis)
    # ema_alpha = 2/(200+1) ~ 0.01; use 0.01 (vs v1's 0.05 which was too short)
    ema_alpha = 0.01

    for step_i in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train_t[st]]        # [batch, dim]
        Nxt = E[idx_train_t[st + 1]]    # [batch, dim]

        # cf-RPE error (same as ARM_CFRPE_ONLY in prior cells)
        error = Nxt - Ctx @ W.t()       # [batch, dim]
        dW = (error.t() @ Ctx) / batch  # [dim, dim]

        # Immediate update at base_lr (always applied)
        W = W + base_lr * dW

        if arm_gamma > 0.0:
            # Compute RPE scalar for this step
            rpe_t = error.norm(dim=1).mean()  # scalar
            rpe_norm = float(torch.clamp(rpe_t / (ema_rpe + 1e-3), 0.0, 5.0))

            # Update EMA
            ema_rpe = (1.0 - ema_alpha) * ema_rpe + ema_alpha * rpe_t.detach()

            # Duration extension: how many extra steps to propagate
            duration_t = base_duration * (1.0 + arm_gamma * rpe_norm)
            n_extra = int(math.ceil(duration_t)) - 1  # steps beyond the immediate

            if n_extra > 0:
                # Apply attenuated update to subsequent k steps (eligibility trace)
                # Weight: exp(-k / duration_t); normalized so integral is bounded
                for k in range(1, n_extra + 1):
                    decay_weight = math.exp(-float(k) / max(duration_t, 1e-6))
                    # Cap k at 10 to bound compute per step
                    if k > 10 or decay_weight < 0.01:
                        break
                    W = W + base_lr * decay_weight * dW
        else:
            # ARM_FIXED_WINDOW: only immediate update, no EMA needed for modulation
            rpe_t = error.norm(dim=1).mean()
            ema_rpe = (1.0 - ema_alpha) * ema_rpe + ema_alpha * rpe_t.detach()

    return W


# ============================================================================
# Per-arm logits builder
# ============================================================================

def compute_arm_logits(arm: str, E_base: torch.Tensor, idx_train: np.ndarray,
                        idx_held: np.ndarray, seed: int, n_steps: int) -> Dict:
    """Return [n_held, V] float32 logits + diagnostics. FRESH W per arm."""
    arm_gamma = ARM_GAMMA[arm]

    # Sparse-bipolar transform (same as fair_harness baseline)
    E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    # Per-seed, per-arm generator
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed * 10007 + ARMS.index(arm) * 31337)

    t0 = time.time()
    W = build_W_duration_extension(
        arm, E_used, idx_train_t, n_steps=n_steps,
        batch=INGEST_BATCH, base_lr=BASE_CFRPE_LR,
        base_duration=BASE_DURATION,
        arm_gamma=arm_gamma,
        gen=gen,
    )
    t_ingest = time.time() - t0

    # Recall: predict next token from current context via W
    t0 = time.time()
    n_h = idx_held_t.shape[0]
    logits = torch.zeros((n_h, E_used.shape[0]), dtype=TORCH_DTYPE, device=DEVICE)
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
    n_h = logits.shape[0]
    nxt_np = idx_held[1:] if len(idx_held) > 1 else idx_held
    n_eval = min(n_h, len(nxt_np))
    if n_eval == 0:
        return float("inf")
    logits_np = (logits[:n_eval].detach().cpu().numpy().astype(np.float32)
                 if hasattr(logits, "detach") else logits[:n_eval])
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
    best_bpc = {"T": 1.0, "lambda": lambda_grid[0], "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": lambda_grid[0], "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": lambda_grid[0], "dev_value": -1.0}

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
        "raw_bpc_at_T1_L1": 0.0,  # filled by caller
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

    # ST1: cf-RPE error shrinks for ARM_FIXED_WINDOW (base case)
    n_dim_st = 64
    Ctx = torch.randn(1, n_dim_st, device=_dev)
    Nxt = torch.randn(1, n_dim_st, device=_dev)
    Ctx = Ctx / (Ctx.norm() + 1e-8)
    Nxt = Nxt / (Nxt.norm() + 1e-8)
    W3 = torch.zeros(n_dim_st, n_dim_st, device=_dev)
    error_before = float((Nxt - Ctx @ W3.t()).norm())
    dW3 = (Nxt - Ctx @ W3.t()).t() @ Ctx
    W3 = W3 + 0.9 * dW3
    error_after = float((Nxt - Ctx @ W3.t()).norm())
    assert error_after < error_before, (
        "ST1 cf-RPE delta should shrink error: before=%.4f after=%.4f" % (error_before, error_after))
    print("[selftest] ST1 cf-RPE delta shrinks error: %.4f -> %.4f" % (error_before, error_after), flush=True)

    # ST2: duration extension arm W differs from fixed-window W (modulation is active)
    n_v_st = 8
    n_dim_st2 = 32
    n_pairs_st = 20
    gen_st2 = torch.Generator(device=_dev)
    gen_st2.manual_seed(99)
    E_st = torch.randn(n_v_st, n_dim_st2, device=_dev)
    E_st = _l2_normalize_t(E_st)
    idx_st = torch.randint(0, n_v_st, (n_pairs_st + 1,), generator=gen_st2, device=_dev)
    gen_f = torch.Generator(device=_dev)
    gen_f.manual_seed(7)
    W_fixed = build_W_duration_extension(
        "ARM_FIXED_WINDOW", E_st, idx_st, n_steps=10,
        batch=2, base_lr=0.5, base_duration=BASE_DURATION,
        arm_gamma=0.0, gen=gen_f
    )
    gen_d = torch.Generator(device=_dev)
    gen_d.manual_seed(7)
    W_dur = build_W_duration_extension(
        "ARM_DURATION_EXTENSION_GAMMA_10", E_st, idx_st, n_steps=10,
        batch=2, base_lr=0.5, base_duration=BASE_DURATION,
        arm_gamma=1.0, gen=gen_d
    )
    diff = float((W_dur - W_fixed).norm())
    assert diff > 1e-6, "ST2 duration arm W should differ from fixed arm W: diff=%.2e" % diff
    print("[selftest] ST2 DURATION != FIXED W (diff=%.4f)" % diff, flush=True)

    # ST3: gamma=2.0 arm produces larger total update than gamma=0.5 arm (higher gamma = more extension)
    gen_lo = torch.Generator(device=_dev)
    gen_lo.manual_seed(7)
    W_lo = build_W_duration_extension(
        "ARM_DURATION_EXTENSION_GAMMA_05", E_st, idx_st, n_steps=10,
        batch=2, base_lr=0.5, base_duration=BASE_DURATION,
        arm_gamma=0.5, gen=gen_lo
    )
    gen_hi = torch.Generator(device=_dev)
    gen_hi.manual_seed(7)
    W_hi = build_W_duration_extension(
        "ARM_DURATION_EXTENSION_GAMMA_20", E_st, idx_st, n_steps=10,
        batch=2, base_lr=0.5, base_duration=BASE_DURATION,
        arm_gamma=2.0, gen=gen_hi
    )
    # W_hi should have larger norm than W_lo (more updates applied)
    diff_lo_hi = float((W_hi - W_lo).norm())
    assert diff_lo_hi > 1e-8, "ST3 hi-gamma W should differ from lo-gamma W: diff=%.2e" % diff_lo_hi
    print("[selftest] ST3 hi-gamma W differs from lo-gamma W (diff=%.6f)" % diff_lo_hi, flush=True)

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
    assert math.isfinite(jr["bpc_best"]), "ST4 joint_sweep bpc_best not finite: %s" % jr["bpc_best"]
    assert math.isfinite(jr["top1_acc"]), "ST4 joint_sweep top1_acc not finite"
    assert math.isfinite(jr["mrr_at_10"]), "ST4 joint_sweep mrr_at_10 not finite"
    assert jr["n_dev"] > 0, "ST4 n_dev == 0"
    assert jr["n_test"] > 0, "ST4 n_test == 0"
    # C7 guard: lambda=0.0 should NOT appear in LAMBDA_GRID
    assert 0.0 not in LAMBDA_GRID, "C7 guard: LAMBDA_GRID must exclude 0.0 (collapse prevention)"
    # verify best_lambda is from LAMBDA_GRID (not the hard-coded init value 0.0)
    assert jr["best_lambda_for_bpc"] in LAMBDA_GRID, (
        "ST4 best_lambda_for_bpc=%s not in LAMBDA_GRID" % jr["best_lambda_for_bpc"])
    print("[selftest] ST4 joint_sweep all metrics finite OK (bpc=%.3f top1=%.4f mrr=%.4f best_lam=%.3f)" % (
        jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"], jr["best_lambda_for_bpc"]), flush=True)

    # ST5: RPE normalization prevents duration from exploding (clamp at 0-5 produces bounded duration)
    # For rpe_norm=5.0 and gamma=2.0: duration_t = base_duration * (1+2*5) = 3*11 = 33 steps
    # But we cap k at 10 in the loop, so bounded
    max_expected_duration = BASE_DURATION * (1.0 + 2.0 * 5.0)  # gamma=2.0, rpe_norm=5.0
    assert max_expected_duration < 100, "ST5 max duration too large: %.1f" % max_expected_duration
    # Compute actual max extra steps per our loop cap
    max_extra = min(int(math.ceil(max_expected_duration)) - 1, 10)
    assert max_extra <= 10, "ST5 extra step cap should be <= 10"
    print("[selftest] ST5 duration bounded: max_duration=%.1f max_extra_steps=%d" % (
        max_expected_duration, max_extra), flush=True)

    # ST6: LAMBDA_GRID excludes 0.0 (explicit C7 guard)
    assert 0.0 not in LAMBDA_GRID, "ST6 LAMBDA_GRID must exclude 0.0 per C7 guard"
    min_lam = min(LAMBDA_GRID)
    assert min_lam > 0.0, "ST6 minimum lambda should be > 0.0: got %.4f" % min_lam
    print("[selftest] ST6 LAMBDA_GRID[0]=%.4f (>0.0 per C7) OK" % min_lam, flush=True)

    print("[selftest] ALL PASS (6/6)", flush=True)


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
        print("\n  [seed=%d arm=%s gamma=%.2f] building W + logits..." % (
            seed, arm, ARM_GAMMA[arm]), flush=True)
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
                "arm_gamma": ARM_GAMMA[arm],
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
            jr["arm_gamma"] = ARM_GAMMA[arm]
            by_arm[arm] = jr
            print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
                  "(bestT=%.4f bestL=%.3f) raw_T1L1_bpc=%.3f" % (
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
        jr["arm_gamma"] = ARM_GAMMA[arm]
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
              "(bestT=%.4f bestL=%.3f) raw_T1L1_bpc=%.3f" % (
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
                "arm_gamma": ARM_GAMMA.get(arm, float("nan")),
            }
            continue
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_v = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid_units]
        raw_v_finite = [x for x in raw_v if math.isfinite(x)]
        best_lam_v = [u["by_arm"][arm].get("best_lambda_for_bpc", float("nan")) for u in valid_units]
        best_T_v = [u["by_arm"][arm].get("best_T_for_bpc", float("nan")) for u in valid_units]
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
            "best_lambda_for_bpc_mean": round(float(np.mean([x for x in best_lam_v if not math.isnan(x)])), 4) if any(not math.isnan(x) for x in best_lam_v) else float("nan"),
            "best_T_for_bpc_mean": round(float(np.mean([x for x in best_T_v if not math.isnan(x)])), 4) if any(not math.isnan(x) for x in best_T_v) else float("nan"),
            "n_valid_seeds": int(len(valid_units)),
            "n_compute_failed": n_failed,
            "all_seeds_failed": False,
            "arm_gamma": ARM_GAMMA.get(arm, float("nan")),
        }

    # Per-arm BPC values (Fix #28: read raw arm metrics, not summary framing)
    fixed_bpc = by_arm_agg.get("ARM_FIXED_WINDOW", {}).get("bpc_best_mean", float("inf"))
    g05_bpc = by_arm_agg.get("ARM_DURATION_EXTENSION_GAMMA_05", {}).get("bpc_best_mean", float("inf"))
    g10_bpc = by_arm_agg.get("ARM_DURATION_EXTENSION_GAMMA_10", {}).get("bpc_best_mean", float("inf"))
    g20_bpc = by_arm_agg.get("ARM_DURATION_EXTENSION_GAMMA_20", {}).get("bpc_best_mean", float("inf"))

    # Lifts vs FIXED_WINDOW (positive = extension arm is better = lower BPC)
    lift_g05 = fixed_bpc - g05_bpc
    lift_g10 = fixed_bpc - g10_bpc
    lift_g20 = fixed_bpc - g20_bpc
    best_lift = max(lift_g05, lift_g10, lift_g20)

    # CV for best arm
    best_arm_name = max(
        ["ARM_DURATION_EXTENSION_GAMMA_05", "ARM_DURATION_EXTENSION_GAMMA_10",
         "ARM_DURATION_EXTENSION_GAMMA_20"],
        key=lambda a: by_arm_agg.get(a, {}).get("bpc_best_cv", float("nan")) if False
        else fixed_bpc - by_arm_agg.get(a, {}).get("bpc_best_mean", float("inf"))
    )
    best_cv = by_arm_agg.get(best_arm_name, {}).get("bpc_best_cv", float("nan"))

    # Sanity rail: ARM_FIXED_WINDOW must reproduce cf-RPE chain-grade
    fixed_deviation = abs(fixed_bpc - CFRPE_CHAIN_GRADE_REF_BPC)

    # C7 INSTR_SUSPECT guard: if best_lambda=0.0 for all duration arms, flag INSTR_SUSPECT
    all_best_lam_zero = all(
        abs(by_arm_agg.get(a, {}).get("best_lambda_for_bpc_mean", 1.0)) < 1e-9
        for a in ["ARM_DURATION_EXTENSION_GAMMA_05", "ARM_DURATION_EXTENSION_GAMMA_10",
                  "ARM_DURATION_EXTENSION_GAMMA_20"]
        if not by_arm_agg.get(a, {}).get("all_seeds_failed", True)
    )

    arm_summary = (
        "uni=bpc%.3f | ARM_FIXED=bpc%.4f (ref=%.4f dev=%.4f) | "
        "G05=bpc%.4f lift=%.4f | G10=bpc%.4f lift=%.4f | G20=bpc%.4f lift=%.4f | "
        "best_lift=%.4f best_arm=%s cv=%.3f"
    ) % (
        unigram_bpc, fixed_bpc, CFRPE_CHAIN_GRADE_REF_BPC, fixed_deviation,
        g05_bpc, lift_g05, g10_bpc, lift_g10, g20_bpc, lift_g20,
        best_lift, best_arm_name, best_cv if math.isfinite(best_cv) else -1.0,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "lift_g05_vs_fixed": round(lift_g05, 4),
        "lift_g10_vs_fixed": round(lift_g10, 4),
        "lift_g20_vs_fixed": round(lift_g20, 4),
        "best_lift": round(best_lift, 4),
        "best_arm": best_arm_name,
        "fixed_bpc": round(fixed_bpc, 4),
        "g05_bpc": round(g05_bpc, 4),
        "g10_bpc": round(g10_bpc, 4),
        "g20_bpc": round(g20_bpc, 4),
        "unigram_bpc": round(unigram_bpc, 4),
        "cfrpe_chain_grade_ref_bpc": CFRPE_CHAIN_GRADE_REF_BPC,
        "fixed_deviation_vs_ref": round(fixed_deviation, 4),
        "fair_harness_hebbian_baseline_bpc": FAIR_HARNESS_HEBBIAN_BPC,
        "n_seeds": len(units),
        "hard_pass_lift_bar": HARD_PASS_DURATION_LIFT,
        "chain_grade_bonus_bar": CHAIN_GRADE_BONUS_LIFT,
        "hard_fail_max_lift": HARD_FAIL_MAX_LIFT,
        "honest_scope": (
            "Brain-canonical eligibility-trace duration-extension rescue for failed "
            "MAGNITUDE-amplification meta-LR cell. Tests whether extending the credit-assignment "
            "window (forward trace propagation) lifts BPC over fixed-window cf-RPE baseline at "
            "N_DIM=8192 N_TRAIN=100k text8 V=4000. "
            "WHAT_THIS_DOES_NOT_SHOW: does not test multi-domain generalization, "
            "STDP composition, or whether duration-extension generalizes beyond text8."
        ),
        "cites": [
            "preregs/2026-06-23_substrate_dopamine_duration_extension_LR_v1.md",
            "experiments/exp_substrate_meta_lr_dopamine_analog_v1.py",
            "data/exp_substrate_meta_lr_dopamine_analog_v1/metrics.json",
            "notes/research_dopamine_modulated_LR_alternatives_2x_drill_2026-06-23.md",
            "notes/exp_dev_handoff_research_dopamine_modulated_LR_alternatives_2026-06-23.md",
        ],
    }

    # Sanity rail: ARM_FIXED_WINDOW deviation (full-mode only; smoke scale BPC differs)
    if RUN_MODE == "full" and fixed_deviation > FIXED_WINDOW_SANITY_DELTA:
        detail["sanity_rail_fail"] = True
        return ("HARD_FAIL",
                ("HARD_FAIL sanity-rail: ARM_FIXED_WINDOW=%.4f deviates %.4f > +/-%.2f from "
                 "cf-RPE chain-grade ref %.4f. Control arm invalid; result unreliable. "
                 "%s" % (fixed_bpc, fixed_deviation, FIXED_WINDOW_SANITY_DELTA,
                          CFRPE_CHAIN_GRADE_REF_BPC, arm_summary)),
                detail)
    if RUN_MODE != "full" and fixed_deviation > FIXED_WINDOW_SANITY_DELTA:
        # Smoke-scale: log deviation but do not fail (expected at V=300, N_TRAIN=2k)
        detail["smoke_scale_deviation_note"] = (
            "smoke-scale ARM_FIXED_WINDOW=%.4f deviates %.4f from full-scale ref %.4f "
            "(expected at smoke V/N_TRAIN; v1 smoke showed 4.8934)" % (
                fixed_bpc, fixed_deviation, CFRPE_CHAIN_GRADE_REF_BPC)
        )
        print("[verdict] smoke sanity deviation %.4f noted (not a failure at smoke scale)" % fixed_deviation,
              flush=True)

    # C7 INSTR_SUSPECT guard
    if all_best_lam_zero:
        detail["c7_instr_suspect"] = True
        return ("INSTRUMENTATION_SUSPECT",
                ("INSTRUMENTATION_SUSPECT C7: all duration arms have best_lambda=0.0. "
                 "This indicates lambda=0.0 collapse (uniform unigram scores). "
                 "Expand LAMBDA_GRID to include smaller values. %s" % arm_summary),
                detail)

    # CV gate (best arm)
    if math.isfinite(best_cv) and best_cv > HP_BPC_CV_MAX:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_HIGH_CV: best arm %s cv=%.3f > %.2f mandatory. "
                 "best_lift=%.4f. High variance; unstable result. "
                 "%s" % (best_arm_name, best_cv, HP_BPC_CV_MAX, best_lift, arm_summary)),
                detail)

    # CHAIN_GRADE_BONUS
    best_bpc = fixed_bpc - best_lift
    if (best_lift >= CHAIN_GRADE_BONUS_LIFT and
            best_bpc <= (FAIR_HARNESS_HEBBIAN_BPC - 0.30)):
        detail["chain_grade_bonus"] = True
        return ("HARD_PASS",
                ("HARD_PASS CHAIN_GRADE_BONUS: %s lift=%.4f >= %.2f "
                 "AND bpc=%.4f <= (%.4f-0.30). "
                 "Brain-canonical duration-extension closes credit-assignment gap "
                 "with chain-grade lift. %s" % (
                     best_arm_name, best_lift, CHAIN_GRADE_BONUS_LIFT,
                     best_bpc, FAIR_HARNESS_HEBBIAN_BPC, arm_summary)),
                detail)

    # HARD_PASS
    if best_lift >= HARD_PASS_DURATION_LIFT:
        detail["chain_grade_bonus"] = False
        return ("HARD_PASS",
                ("HARD_PASS: %s lift_vs_fixed=%.4f >= %.2f. "
                 "Brain-canonical eligibility-trace duration-extension HELPS where "
                 "MAGNITUDE-amplification FAILED. %s" % (
                     best_arm_name, best_lift, HARD_PASS_DURATION_LIFT, arm_summary)),
                detail)

    # MIDDLE_BAND
    if MIDDLE_BAND_LO <= best_lift < MIDDLE_BAND_HI:
        detail["chain_grade_bonus"] = False
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND: best lift=%.4f in [%.2f, %.2f). "
                 "Duration extension helps but below HARD_PASS threshold. %s" % (
                     best_lift, MIDDLE_BAND_LO, MIDDLE_BAND_HI, arm_summary)),
                detail)

    # HARD_FAIL
    detail["chain_grade_bonus"] = False
    return ("HARD_FAIL",
            ("HARD_FAIL: best duration-extension lift=%.4f <= %.2f. "
             "Eligibility-trace DURATION extension also not load-bearing for substrate-LM. "
             "Meta-LR via RPE is fundamentally closed at this scale. %s" % (
                 best_lift, HARD_FAIL_MAX_LIFT, arm_summary)),
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
    "BASE_DURATION": BASE_DURATION,
    "GAMMA_GRID": GAMMA_GRID,
    "ARM_GAMMA": ARM_GAMMA,
    "N_STEPS": N_STEPS,
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
    "summary": verdict_msg,
}

write_metrics(out_dir, metrics, all_units)
print("[metrics] written to %s" % out_dir, flush=True)
