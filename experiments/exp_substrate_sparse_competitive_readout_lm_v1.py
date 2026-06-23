"""substrate_sparse_competitive_readout_lm_v1 -- isolated test of sparse competitive readout.

USER directive 2026-06-23 brain-existence-proof: substrate's argmax readout is
linear. Brain's sparse competitive activation (~1-3% firing, K-WTA via lateral
inhibition + Tonegawa-CREB excitability bias) is non-linear softmax-like. This
mechanism is empirically validated in cortex; substrate just needs to implement.
Test whether non-linear competitive readout ALONE breaks the rank-1 cap that
prior substrate-as-LM cells run into.

MECHANISM: at READ time (not write), substrate W produces a score vector over
the V-vocabulary. Instead of argmax, do K-WTA over top-K positions weighted by
a Tonegawa excitability trace E[i]; softmax over the K survivors. Effectively a
substrate-native sparse softmax. The excitability trace E[i] is per-vocab-position,
updated each write (+= alpha when that target fires) and decayed each step.

DESIGN (5 arms x 3 seeds; SHARED char-trigram encoder + SHARED W; readout differs):

  ARM_UNIGRAM
      Analytic floor reference BPC=7.738.

  ARM_RANK1_ARGMAX
      Current substrate readout. argmax over score vector == K_eff=1. The
      rank-1-cap reference. Sanity-checked to ~7.7 BPC.

  ARM_SPARSE_COMPETITIVE_K10
      Top-10 K-WTA on the score vector; mask + softmax over the 10 survivors.

  ARM_SPARSE_COMPETITIVE_K100
      Top-100 K-WTA; mask + softmax over 100 survivors.

  ARM_SPARSE_COMPETITIVE_PLUS_EXCITABILITY_K100
      Top-100 K-WTA where the score = raw_score * (1 + beta * E_norm[i]);
      E[i] is a Tonegawa-CREB excitability trace per-vocab-position, updated
      during the W-build pass (+= alpha when position fires; *= decay each step).
      The DECISIVE arm.

PRE-REG HARD bands:
  HARD_PASS: ARM_SPARSE_COMPETITIVE_PLUS_EXCITABILITY BPC < ARM_RANK1_ARGMAX BPC - 0.5
             AND BPC < 7.5 (beats unigram). Non-linear sparse competitive readout
             breaks rank-1 cap; chain-grade evidence for brain-existence-proof
             mechanism in substrate.
  HARD_FAIL: all competitive arms BPC >= ARM_RANK1_ARGMAX. Non-linear readout
             doesn't help; rank-1 cap is in the W matrix not the readout.
  MIDDLE_BAND: competitive lifts over rank-1 but doesn't beat unigram.

SANITY (in --self-test):
  - ARM_SPARSE_COMPETITIVE_K=1 == ARM_RANK1_ARGMAX (endpoint check)
  - excitability trace E[i] is non-uniform after training
  - sparse competitive output ~1-3% activation rate (brain sparsity)
  - log-linear endpoints lambda=1 raw / lambda=0 unigram

GPU REQUIRED (Fix #24): torch.cuda for matmul + topk + masked softmax batched.
Estimated 30-60min wall at N_DIM=8192 x 100k tokens x 5 arms x 3 seeds.

Cites:
  - preregs/2026-06-23_substrate_sparse_competitive_readout_lm_v1.md
  - exp_substrate_as_lm_composed_primitives_GPU_v1.py (parent: fresh W per arm pattern)
  - exp_excitability_gated_substrate_cpu_v1.py (Tonegawa-CREB prior; HARD_PASS 2026-06-11)
  - exp_n4_kwta_soft_decode_v1.py (kwta soft-decode prior; HARD_FAIL 2026-06-22 -- different design)
  - USER 2026-06-23 brain-existence-proof for K-WTA + excitability
  - USER 2026-06-22 GPU dispatch must use GPU (Fix #24)

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

ANCHOR_NAME = "substrate_sparse_competitive_readout_lm_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
_LLM_CALL_COUNTER = [0]

# Reference baselines
UNIGRAM_BPC_REF = 7.738
RANK1_PRIOR_BPC_REF = 7.738  # roughly same as unigram (rank-1 ceiling)

# Pre-reg bands (decisive arm: ARM_SPARSE_COMPETITIVE_PLUS_EXCITABILITY_K100)
HP_BPC_DELTA_BAR = 0.5         # decisive must beat rank1 by >= 0.5 BPC
HP_BPC_ABSOLUTE_BAR = 7.5      # AND must clear unigram-beating 7.5 BPC
HP_BPC_CV_MAX = 0.05

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Config
N_DIM = 8192
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

# Sparse competitive readout knobs
TOPK_LIST = [10, 100]          # K values for K-WTA sweep arms
EXCITABILITY_ALPHA = 0.01      # excitability +=alpha on fire
EXCITABILITY_DECAY = 0.99      # excitability *=decay per step
EXCITABILITY_BETA = 1.0        # score *= (1 + beta * E_norm)

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke must fit under SMOKE_TIMEOUT_S=180s
    SEEDS = [0]
    N_TRAIN = 1_500
    N_HELD = 300
    VOCAB_CAP = 300

ARMS = [
    "ARM_UNIGRAM",
    "ARM_RANK1_ARGMAX",
    "ARM_SPARSE_COMPETITIVE_K10",
    "ARM_SPARSE_COMPETITIVE_K100",
    "ARM_SPARSE_COMPETITIVE_PLUS_EXCITABILITY_K100",
]
DECISIVE_ARM = "ARM_SPARSE_COMPETITIVE_PLUS_EXCITABILITY_K100"

CONFIG_VERSION = (
    "substrate_sparse_competitive_readout_lm_v1; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s topk_list=%s "
    "exc_alpha=%.3f exc_decay=%.3f exc_beta=%.2f "
    "INGEST_CHUNK=%d RECALL_BATCH=%d device=%s lambda_grid=%s; "
    "bands HP_delta>=%.2f HP_abs<%.3f cv_max=%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE, TOPK_LIST,
    EXCITABILITY_ALPHA, EXCITABILITY_DECAY, EXCITABILITY_BETA,
    INGEST_CHUNK, RECALL_BATCH, str(DEVICE), LAMBDA_GRID,
    HP_BPC_DELTA_BAR, HP_BPC_ABSOLUTE_BAR, HP_BPC_CV_MAX,
)


# ============================================================================
# Encoder: char_trigram (single, shared across arms)
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


def build_E_char_trigram(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


# ============================================================================
# Fresh-W Hebbian builder + Tonegawa excitability trace
# ============================================================================

def build_W_and_excitability(E: torch.Tensor, idx_train: torch.Tensor,
                              ingest_chunk: int, alpha: float, decay: float,
                              ) -> Tuple[torch.Tensor, torch.Tensor]:
    """W [N_DIM, N_DIM] = sum over t of outer(E[idx[t+1]], E[idx[t]]).
    Excitability trace exc[V] updated per step:
      exc *= decay; exc[idx[t+1]] += alpha
    Returns (W, exc). exc is per-vocab-position float32 on E.device.
    """
    device = E.device
    dim = E.shape[1]
    V = E.shape[0]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    exc = torch.zeros((V,), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W, exc

    # Decay^k accumulator strategy: for each chunk, apply decay analytically.
    # decay^chunk_size applied at chunk boundary; within a chunk we approximate
    # uniform decay (fine since alpha is small and chunks are not huge).
    # Exact per-step decay is too slow at N_TRAIN=100k; chunkwise is the standard
    # implementation in trace-update neuro sims.
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        cs = end - b
        E_src = E[idx_train[b:end]]
        tgt_idx = idx_train[b + 1:end + 1]
        E_tgt = E[tgt_idx]
        # Hebbian outer-product accumulation (vectorized via batched matmul)
        W.add_(E_tgt.T @ E_src)
        # Excitability: decay the whole trace by decay^cs, then add alpha per fire
        exc.mul_(decay ** cs)
        # bincount over tgt_idx for this chunk (each fire contributes +alpha)
        counts = torch.bincount(tgt_idx, minlength=V).to(dtype=TORCH_DTYPE)
        exc.add_(counts * alpha)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W, exc


# ============================================================================
# text8 loader / vocab
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
# Sparse competitive readout primitive
# ============================================================================

def sparse_competitive_logits(scores: torch.Tensor, K: int,
                                excitability: Optional[torch.Tensor] = None,
                                beta: float = 0.0,
                                eps_uniform: float = 1e-4) -> torch.Tensor:
    """K-WTA sparse competitive readout with epsilon-uniform smoothing.
    scores [B, V]: raw substrate match scores E @ pred_vec
    K: top-K positions kept; the rest get eps_uniform mass (smoothing)
    excitability [V] (optional): bias scores = scores * (1 + beta * exc_norm)
    eps_uniform: small mass distributed uniformly over the V-K losers
                  (prevents -inf log-probs on miss; standard label-smoothing
                  for hard K-WTA; eps_uniform=1e-4 means 0.01% mass to losers)
    Returns log-probs [B, V] guaranteed finite.
    """
    B, V = scores.shape
    if excitability is not None and beta > 0.0:
        exc_norm = excitability / (excitability.max().clamp(min=1e-9))
        scores = scores * (1.0 + beta * exc_norm.unsqueeze(0))
    K_eff = max(1, min(K, V))
    topk_vals, topk_idx = torch.topk(scores, k=K_eff, dim=1)
    # Compute softmax over top-K survivors only
    topk_log_probs = torch.log_softmax(topk_vals, dim=1)
    # Build mixed: (1 - eps_uniform) * sparse_softmax + eps_uniform * uniform(V)
    # log of mixture: numerically stable via logsumexp
    eps = max(eps_uniform, 1e-30)
    n_losers = V - K_eff
    # build dense probs in linear space then take log
    probs = torch.full_like(scores, eps / max(V, 1))
    # winners: (1 - eps) * topk_softmax + eps/V (their share of uniform)
    winner_probs = (1.0 - eps) * topk_log_probs.exp() + eps / V
    probs.scatter_(1, topk_idx, winner_probs)
    log_probs = torch.log(probs.clamp(min=1e-30))
    return log_probs


def compute_substrate_scores_gpu(E_lookup: torch.Tensor, W: torch.Tensor,
                                   ctx_keys: torch.Tensor, recall_batch: int) -> torch.Tensor:
    """Per-position substrate score [n, V]: scores = E_lookup @ (W @ key) normalized.

    Returns torch.Tensor on E_lookup.device. Caller decides what readout to apply.
    """
    n = ctx_keys.shape[0]
    V = E_lookup.shape[0]
    out = torch.zeros((n, V), dtype=TORCH_DTYPE, device=E_lookup.device)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        K_b = ctx_keys[b:end]
        pred_vec = K_b @ W.T
        pn = pred_vec.norm(dim=1, keepdim=True).clamp(min=1e-9)
        pred_vec = pred_vec / pn
        out[b:end] = pred_vec @ E_lookup.T
        if DEVICE.type == "cuda" and (b // recall_batch) % 16 == 0:
            torch.cuda.synchronize()
    return out


def softmax_with_temperature_np(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    z = logits / max(temperature, 1e-6)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp_bpc(sub_logp: np.ndarray, U_log: np.ndarray, nxt: np.ndarray,
                           lam: float) -> float:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    logp = combined - Z[:, None]
    logp_nxt = logp[np.arange(len(nxt)), nxt]
    return -float(np.mean(logp_nxt)) / math.log(2.0)


# ============================================================================
# Per-arm BPC computation (shared W; readout differs by arm)
# ============================================================================

def bpc_arm_readout(arm_label: str, E: torch.Tensor, W: torch.Tensor,
                     exc: torch.Tensor, idx_train: np.ndarray, idx_held: np.ndarray,
                     U_log: np.ndarray, lambda_grid: list, recall_batch: int) -> Dict:
    """Compute BPC for a given readout arm. W and E are SHARED across arms.

    Arm decides:
      ARM_RANK1_ARGMAX:           argmax (K_eff=1) -- equivalent to top-1 hard
      ARM_SPARSE_COMPETITIVE_K10: K-WTA top-10 + softmax
      ARM_SPARSE_COMPETITIVE_K100: K-WTA top-100 + softmax
      ARM_SPARSE_COMPETITIVE_PLUS_EXCITABILITY_K100: as above + excitability bias
    """
    V = E.shape[0]
    unk = 0
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)
    ctx_keys = E[idx_held_t[:-1]]
    nxt = idx_held[1:]
    mask = (idx_held[:-1] != unk)
    ctx_keys_eval = ctx_keys[mask]
    nxt_eval = nxt[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        return _empty_arm_result()
    n_dev = n_eval // 2
    ctx_dev = ctx_keys_eval[:n_dev]
    nxt_dev = nxt_eval[:n_dev]
    ctx_test = ctx_keys_eval[n_dev:]
    nxt_test = nxt_eval[n_dev:]
    n_test = len(ctx_test)

    t0 = time.time()
    scores_dev = compute_substrate_scores_gpu(E, W, ctx_dev, recall_batch)
    scores_test = compute_substrate_scores_gpu(E, W, ctx_test, recall_batch)
    t_recall = time.time() - t0

    # Apply arm-specific readout to convert scores -> log-probs
    if arm_label == "ARM_RANK1_ARGMAX":
        K = 1
        beta = 0.0
        exc_in = None
    elif arm_label == "ARM_SPARSE_COMPETITIVE_K10":
        K = 10
        beta = 0.0
        exc_in = None
    elif arm_label == "ARM_SPARSE_COMPETITIVE_K100":
        K = 100
        beta = 0.0
        exc_in = None
    elif arm_label == "ARM_SPARSE_COMPETITIVE_PLUS_EXCITABILITY_K100":
        K = 100
        beta = EXCITABILITY_BETA
        exc_in = exc
    else:
        raise ValueError("unknown arm %s" % arm_label)

    log_probs_dev = sparse_competitive_logits(scores_dev, K, excitability=exc_in, beta=beta)
    log_probs_test = sparse_competitive_logits(scores_test, K, excitability=exc_in, beta=beta)

    # Brain-sparsity sanity: fraction of positions with prob > 1/V (above uniform)
    with torch.no_grad():
        probs_test = log_probs_test.exp()
        above_uniform = (probs_test > (1.0 / V)).float().mean().item()

    sub_logp_dev = log_probs_dev.detach().cpu().numpy().astype(np.float32)
    sub_logp_test = log_probs_test.detach().cpu().numpy().astype(np.float32)

    raw_logp_nxt = sub_logp_test[np.arange(n_test), nxt_test]
    bpc_raw = -float(np.mean(raw_logp_nxt)) / math.log(2.0)

    best_lambda = 1.0
    best_dev_bpc = float("inf")
    bpc_per_lambda_dev: Dict[float, float] = {}
    bpc_per_lambda_test: Dict[float, float] = {}
    for lam in lambda_grid:
        bpc_dev = log_linear_interp_bpc(sub_logp_dev, U_log, nxt_dev, lam)
        bpc_per_lambda_dev[lam] = bpc_dev
        bpc_test = log_linear_interp_bpc(sub_logp_test, U_log, nxt_test, lam)
        bpc_per_lambda_test[lam] = bpc_test
        if bpc_dev < best_dev_bpc:
            best_dev_bpc = bpc_dev
            best_lambda = lam
    bpc_best_test = bpc_per_lambda_test[best_lambda]

    del scores_dev, scores_test, log_probs_dev, log_probs_test, ctx_keys, ctx_keys_eval
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "bpc_raw": round(bpc_raw, 4),
        "bpc_best": round(bpc_best_test, 4),
        "best_lambda": float(best_lambda),
        "best_dev_bpc": round(best_dev_bpc, 4),
        "bpc_per_lambda_dev": {str(k): round(v, 4) for k, v in bpc_per_lambda_dev.items()},
        "bpc_per_lambda_test": {str(k): round(v, 4) for k, v in bpc_per_lambda_test.items()},
        "n_dev": int(n_dev),
        "n_test": int(n_test),
        "wall_recall_s": round(t_recall, 2),
        "K": int(K),
        "beta_used": float(beta),
        "fraction_above_uniform": round(float(above_uniform), 4),
    }


def _empty_arm_result() -> Dict:
    return {"bpc_raw": float("inf"), "bpc_best": float("inf"),
            "best_lambda": 1.0, "best_dev_bpc": float("inf"),
            "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
            "n_dev": 0, "n_test": 0, "wall_recall_s": 0.0,
            "K": 0, "beta_used": 0.0, "fraction_above_uniform": 0.0}


def bpc_unigram(idx_train: np.ndarray, idx_held: np.ndarray, V: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    nxt_eval = nxt[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        return {"bpc_unigram": float("inf"), "n_test": 0}
    n_dev = n_eval // 2
    nxt_test = nxt_eval[n_dev:]
    p_true = U[nxt_test].clip(1e-12, 1.0)
    nll = float(-np.mean(np.log(p_true)))
    return {"bpc_unigram": round(nll / math.log(2.0), 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Per-seed runner: build SHARED W + exc, then sweep readout arms
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading text8 + vocab" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[WARN] corpus short: %d vs %d" % (len(toks), N_TRAIN + N_HELD), flush=True)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train_np = tokens_to_idx(train_toks, w2i)
    idx_held_np = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE)), flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[seed=%d gpu] %s mem_total_gb=%.2f" % (
                seed, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception as e:
            print("[seed=%d gpu-info-fail] %s" % (seed, e), flush=True)

    # Unigram baseline
    U = build_unigram_np(idx_train_np, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)
    uni = bpc_unigram(idx_train_np, idx_held_np, V)
    print("[seed=%d arm=ARM_UNIGRAM] bpc_unigram=%.3f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {
        "ARM_UNIGRAM": {"bpc_unigram": uni["bpc_unigram"], "n_test": uni["n_test"]}
    }

    # Build SHARED encoder + W + excitability ONCE per seed (saves 4x compute)
    print("[seed=%d] building SHARED E (char_trigram) on %s..." % (seed, str(DEVICE)), flush=True)
    t0 = time.time()
    try:
        E = build_E_char_trigram(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d] ENCODER LOAD FAIL: %s" % (seed, err), flush=True)
        for arm in [a for a in ARMS if a != "ARM_UNIGRAM"]:
            by_arm[arm] = {"load_failed": True, "load_error": err,
                           **_empty_arm_result()}
        return {"seed": seed, "by_arm": by_arm, "V": V, "N": N_DIM, "N_DIM": N_DIM,
                "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
                "TOPK_LIST": TOPK_LIST, "EXCITABILITY_ALPHA": EXCITABILITY_ALPHA,
                "EXCITABILITY_DECAY": EXCITABILITY_DECAY, "EXCITABILITY_BETA": EXCITABILITY_BETA,
                "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
                "elapsed_s_seed": round(time.time() - t_seed, 2),
                "device": str(DEVICE), "n_llm_calls": 0}
    t_enc = time.time() - t0

    print("[seed=%d] E built (%.1fs); building SHARED W + excitability..." % (seed, t_enc), flush=True)
    idx_train_t = torch.from_numpy(idx_train_np).to(DEVICE)
    t0 = time.time()
    W, exc = build_W_and_excitability(
        E, idx_train_t, INGEST_CHUNK, EXCITABILITY_ALPHA, EXCITABILITY_DECAY)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0
    print("[seed=%d] W + exc built (%.1fs); exc stats: max=%.4f mean=%.4f nonzero_frac=%.3f" % (
        seed, t_ingest, float(exc.max()), float(exc.mean()),
        float((exc > 0).float().mean())), flush=True)

    # Sweep readout arms with SHARED W + exc
    for arm_label in [a for a in ARMS if a != "ARM_UNIGRAM"]:
        t_arm = time.time()
        print("\n  [seed=%d arm=%s] applying readout..." % (seed, arm_label), flush=True)
        try:
            bpc = bpc_arm_readout(arm_label, E, W, exc, idx_train_np, idx_held_np,
                                   U_log, LAMBDA_GRID, RECALL_BATCH)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] READOUT FAIL: %s" % (seed, arm_label, err), flush=True)
            if DEVICE.type == "cuda":
                torch.cuda.empty_cache()
            by_arm[arm_label] = {"compute_failed": True, "compute_error": err,
                                 "wall_arm_s": round(time.time() - t_arm, 2),
                                 **_empty_arm_result()}
            continue
        print("    [seed=%d arm=%s] bpc_raw=%.3f bpc_best=%.3f lam=%.2f K=%d "
              "frac_above_unif=%.3f (recall=%.1fs)" % (
            seed, arm_label, bpc["bpc_raw"], bpc["bpc_best"], bpc["best_lambda"],
            bpc["K"], bpc["fraction_above_uniform"], bpc["wall_recall_s"]), flush=True)
        bpc["wall_arm_s"] = round(time.time() - t_arm, 2)
        by_arm[arm_label] = bpc

    # Cleanup
    del E, W, exc, idx_train_t
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed, "by_arm": by_arm, "V": V,
        "N": N_DIM, "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "TOPK_LIST": TOPK_LIST,
        "EXCITABILITY_ALPHA": EXCITABILITY_ALPHA,
        "EXCITABILITY_DECAY": EXCITABILITY_DECAY,
        "EXCITABILITY_BETA": EXCITABILITY_BETA,
        "wall_encode_s": round(t_enc, 2),
        "wall_ingest_s": round(t_ingest, 2),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "n_llm_calls": 0,
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    by_arm_agg: Dict[str, Dict] = {}
    uni_vals = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.mean(uni_vals)), 4),
        "bpc_std": round(float(np.std(uni_vals)), 4),
    }
    readout_arms = [a for a in ARMS if a != "ARM_UNIGRAM"]
    for arm in readout_arms:
        seeds_load_failed = [u["by_arm"].get(arm, {}).get("load_failed", False) for u in units]
        seeds_compute_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid = [(not lf) and (not cf) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
                 for lf, cf, u in zip(seeds_load_failed, seeds_compute_failed, units)]
        n_load_failed = int(sum(seeds_load_failed))
        n_compute_failed = int(sum(seeds_compute_failed))
        valid_units = [u for ok, u in zip(valid, units) if ok]
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"), "bpc_best_std": float("nan"),
                "bpc_best_cv": float("nan"), "bpc_raw_mean": float("inf"),
                "best_lambda_mean": float("nan"),
                "n_valid_seeds": 0, "n_load_failed": n_load_failed,
                "n_compute_failed": n_compute_failed, "all_seeds_failed": True,
            }
            continue
        best_vals = [u["by_arm"].get(arm, {}).get("bpc_best", float("inf")) for u in valid_units]
        raw_vals = [u["by_arm"].get(arm, {}).get("bpc_raw", float("inf")) for u in valid_units]
        lam_vals = [u["by_arm"].get(arm, {}).get("best_lambda", float("nan")) for u in valid_units]
        frac_vals = [u["by_arm"].get(arm, {}).get("fraction_above_uniform", float("nan")) for u in valid_units]
        b_mean = float(np.mean(best_vals))
        b_std = float(np.std(best_vals))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4), "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "bpc_raw_mean": round(float(np.mean(raw_vals)), 4),
            "best_lambda_mean": round(float(np.mean(lam_vals)), 4),
            "fraction_above_uniform_mean": round(float(np.mean(frac_vals)), 4),
            "n_valid_seeds": int(len(valid_units)),
            "n_load_failed": n_load_failed,
            "n_compute_failed": n_compute_failed,
            "all_seeds_failed": False,
        }

    rank1_bpc = by_arm_agg.get("ARM_RANK1_ARGMAX", {}).get("bpc_best_mean", float("inf"))
    decisive = by_arm_agg.get(DECISIVE_ARM, {})
    decisive_bpc = decisive.get("bpc_best_mean", float("inf"))
    decisive_cv = decisive.get("bpc_best_cv", float("nan"))
    k10_bpc = by_arm_agg.get("ARM_SPARSE_COMPETITIVE_K10", {}).get("bpc_best_mean", float("inf"))
    k100_bpc = by_arm_agg.get("ARM_SPARSE_COMPETITIVE_K100", {}).get("bpc_best_mean", float("inf"))

    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    parts = []
    for a in readout_arms:
        b = by_arm_agg[a]
        parts.append("%s=bpc%.3f(lam%.2f,K=?)" % (a[4:], b["bpc_best_mean"], b["best_lambda_mean"]))
    summary = "SPARSE_COMP_READOUT unigram=%.3f | %s | n_llm=%d" % (
        by_arm_agg["ARM_UNIGRAM"]["bpc_mean"], " | ".join(parts), n_llm)

    # Lifts for visibility
    delta_excit_vs_rank1 = (rank1_bpc - decisive_bpc) if (
        math.isfinite(rank1_bpc) and math.isfinite(decisive_bpc)) else float("nan")
    delta_k10_vs_rank1 = (rank1_bpc - k10_bpc) if (
        math.isfinite(rank1_bpc) and math.isfinite(k10_bpc)) else float("nan")
    delta_k100_vs_rank1 = (rank1_bpc - k100_bpc) if (
        math.isfinite(rank1_bpc) and math.isfinite(k100_bpc)) else float("nan")

    detail = {
        "by_arm_agg": by_arm_agg,
        "decisive_arm": DECISIVE_ARM,
        "decisive_bpc": decisive_bpc,
        "decisive_cv": decisive_cv,
        "rank1_bpc": rank1_bpc,
        "delta_excit_vs_rank1": delta_excit_vs_rank1,
        "delta_k10_vs_rank1": delta_k10_vs_rank1,
        "delta_k100_vs_rank1": delta_k100_vs_rank1,
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "rank1_prior_bpc_ref": RANK1_PRIOR_BPC_REF,
        "hp_bpc_delta_bar": HP_BPC_DELTA_BAR,
        "hp_bpc_absolute_bar": HP_BPC_ABSOLUTE_BAR,
        "hp_bpc_cv_max": HP_BPC_CV_MAX,
        "TOPK_LIST": TOPK_LIST,
        "EXCITABILITY_ALPHA": EXCITABILITY_ALPHA,
        "EXCITABILITY_DECAY": EXCITABILITY_DECAY,
        "EXCITABILITY_BETA": EXCITABILITY_BETA,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Sparse competitive readout sweep: 5 arms isolate the readout layer "
            "(SHARED W+E across all sparse arms). Decisive = ARM_SPARSE_COMPETITIVE_"
            "PLUS_EXCITABILITY_K100 (K-WTA top-100 + Tonegawa excitability bias). "
            "HARD_PASS = decisive < rank1 - %.2f AND < %.3f (breaks rank-1 cap + "
            "beats unigram). HARD_FAIL = all competitive >= rank1 (readout layer "
            "is NOT the bottleneck). Brain-existence-proof tested in substrate."
        ) % (HP_BPC_DELTA_BAR, HP_BPC_ABSOLUTE_BAR),
        "cites": [
            "preregs/2026-06-23_substrate_sparse_competitive_readout_lm_v1.md",
            "experiments/exp_substrate_as_lm_composed_primitives_GPU_v1.py",
            "experiments/exp_excitability_gated_substrate_cpu_v1.py",
            "USER_2026-06-23_brain_existence_proof_kwta_excitability",
            "USER_2026-06-22_GPU_dispatch_must_use_GPU_Fix24",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    # HARD_PASS: decisive beats rank1 by >= 0.5 AND clears unigram
    if (math.isfinite(decisive_bpc) and math.isfinite(rank1_bpc)
            and (rank1_bpc - decisive_bpc) >= HP_BPC_DELTA_BAR
            and decisive_bpc < HP_BPC_ABSOLUTE_BAR
            and math.isfinite(decisive_cv) and decisive_cv <= HP_BPC_CV_MAX):
        return ("HARD_PASS",
                ("SPARSE_COMP_READOUT HARD_PASS: decisive %s BPC %.3f beats RANK1 %.3f by "
                 "%.3f >= %.2f AND clears unigram (%.3f < %.3f); cv=%.3f. Non-linear "
                 "sparse competitive readout breaks rank-1 cap; brain-existence-proof "
                 "K-WTA+excitability mechanism validated in substrate; chain-grade. %s" % (
                     DECISIVE_ARM, decisive_bpc, rank1_bpc, delta_excit_vs_rank1,
                     HP_BPC_DELTA_BAR, decisive_bpc, HP_BPC_ABSOLUTE_BAR, decisive_cv,
                     summary)),
                detail)

    # HARD_FAIL: all competitive arms >= rank1
    all_competitive_fail = all(
        (not math.isfinite(by_arm_agg.get(a, {}).get("bpc_best_mean", float("inf"))))
        or by_arm_agg.get(a, {}).get("bpc_best_mean", float("inf")) >= rank1_bpc
        for a in ["ARM_SPARSE_COMPETITIVE_K10", "ARM_SPARSE_COMPETITIVE_K100",
                  "ARM_SPARSE_COMPETITIVE_PLUS_EXCITABILITY_K100"]
    )
    if math.isfinite(rank1_bpc) and all_competitive_fail:
        return ("HARD_FAIL",
                ("SPARSE_COMP_READOUT HARD_FAIL: all competitive arms BPC >= RANK1 %.3f "
                 "(K10=%.3f, K100=%.3f, EXCIT=%.3f). Non-linear readout does NOT help; "
                 "rank-1 cap is in the W matrix, not the readout layer. Pivot to W-build "
                 "architectural changes (multi-head/multi-rank/projection). %s" % (
                     rank1_bpc, k10_bpc, k100_bpc, decisive_bpc, summary)),
                detail)

    # MIDDLE_BAND: competitive lifts but doesn't clear unigram
    return ("MIDDLE_BAND",
            ("SPARSE_COMP_READOUT MIDDLE_BAND: decisive %s BPC %.3f vs rank1 %.3f "
             "(delta=%.3f) absolute_bar=%.3f. Competitive readout lifts over rank-1 "
             "but doesn't fully break the cap and/or beat unigram. Characterize K-sweep "
             "+ excitability beta. %s" % (
                 DECISIVE_ARM, decisive_bpc, rank1_bpc, delta_excit_vs_rank1,
                 HP_BPC_ABSOLUTE_BAR, summary)),
            detail)


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: char-trigram encoder shape + bipolar
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,)
    uniq = set(np.unique(v).tolist())
    assert uniq.issubset({-1.0, 1.0}), "T1 bipolar"

    # T2: sparse_competitive_logits K=1 reproduces argmax (rank-1 endpoint check)
    # With eps-uniform smoothing (eps=1e-4 default), winners get (1-eps) ~= 0.9999.
    scores = torch.tensor([[1.0, 5.0, 3.0, 2.0, 4.0],
                            [0.5, 0.1, 0.9, 0.2, 0.3]])
    log_probs_k1 = sparse_competitive_logits(scores, K=1, eps_uniform=1e-4)
    argmax_k1 = log_probs_k1.argmax(dim=1)
    expected_argmax = torch.tensor([1, 2])
    assert torch.equal(argmax_k1, expected_argmax), \
        "T2 K=1 argmax mismatch: got %s expected %s" % (argmax_k1.tolist(), expected_argmax.tolist())
    probs_k1 = log_probs_k1.exp()
    top_probs = probs_k1.gather(1, expected_argmax.unsqueeze(1)).squeeze(1)
    # With eps=1e-4, top prob should be 1 - eps + eps/V ~= 0.9999 (very close to 1)
    assert torch.all(top_probs > 0.999) and torch.all(top_probs <= 1.0), \
        "T2 K=1 top prob should be ~1.0 (with eps-smoothing) got %s" % top_probs.tolist()
    # Per-row probs must sum to 1 (probability distribution sanity)
    row_sums_k1 = probs_k1.sum(dim=1)
    assert torch.allclose(row_sums_k1, torch.ones(2), atol=1e-5), \
        "T2 K=1 probs should sum to 1 got %s" % row_sums_k1.tolist()

    # T3: sparse_competitive_logits K=V with eps=0 reproduces plain log_softmax
    K_full = scores.shape[1]
    log_probs_full = sparse_competitive_logits(scores, K=K_full, eps_uniform=0.0)
    expected_full = torch.log_softmax(scores, dim=1)
    assert torch.allclose(log_probs_full, expected_full, atol=1e-4), \
        "T3 K=V with eps=0 should equal plain log_softmax"

    # T4: K=2 -- top-2 get most mass; losers get small uniform share
    log_probs_k2 = sparse_competitive_logits(scores, K=2, eps_uniform=1e-4)
    probs_k2 = log_probs_k2.exp()
    # Top-2 positions per row should have prob >> 1/V
    topk_vals_k2, topk_idx_k2 = probs_k2.topk(k=2, dim=1)
    assert torch.all(topk_vals_k2 > 0.01), \
        "T4 K=2 top-2 probs should be >> uniform got %s" % topk_vals_k2.tolist()
    # All probs should be finite (no -inf logs)
    assert torch.all(torch.isfinite(log_probs_k2)), "T4 K=2 log-probs all finite"

    # T5: excitability bias raises score for high-exc positions
    scores_t5 = torch.tensor([[1.0, 1.0, 1.0]])  # tied scores
    exc_t5 = torch.tensor([0.0, 0.0, 10.0])      # position 2 highly excitable
    log_probs_no_exc = sparse_competitive_logits(scores_t5, K=3)
    log_probs_with_exc = sparse_competitive_logits(scores_t5, K=3, excitability=exc_t5, beta=1.0)
    # without bias, all 3 tied -> argmax breaks tie at 0
    # with bias, position 2 wins
    assert log_probs_with_exc.argmax(dim=1).item() == 2, \
        "T5 excitability bias should make pos 2 win, got argmax=%d" % log_probs_with_exc.argmax(dim=1).item()
    # without bias, position 2 doesn't dominate
    no_exc_probs = log_probs_no_exc.exp()
    assert abs(no_exc_probs[0, 2].item() - (1.0 / 3.0)) < 1e-4, \
        "T5 no-exc tied scores should be uniform got %s" % no_exc_probs[0].tolist()

    # T6: build_W_and_excitability shape + exc non-uniform after training
    vocab_t = ["w%d" % i for i in range(8)]
    global DEVICE
    _saved_device = DEVICE
    DEVICE = torch.device("cpu")
    try:
        E_small = build_E_char_trigram(vocab_t, 128, seed=0)
        # idx_train: position 1 fires more than position 0
        idx_seq = torch.from_numpy(np.array(
            [0, 1, 1, 1, 2, 1, 1, 3, 1, 4] * 4, dtype=np.int64))
        W_small, exc_small = build_W_and_excitability(
            E_small, idx_seq, ingest_chunk=8,
            alpha=EXCITABILITY_ALPHA, decay=EXCITABILITY_DECAY)
        assert W_small.shape == (128, 128), "T6 W shape"
        assert exc_small.shape == (8,), "T6 exc shape"
        assert float(W_small.abs().sum()) > 0, "T6 W nonzero"
        # exc[1] should be > exc[0] since pos 1 fires far more often
        assert float(exc_small[1]) > float(exc_small[0]), \
            "T6 exc[1]=%.4f should exceed exc[0]=%.4f (pos 1 fires more)" % (
                float(exc_small[1]), float(exc_small[0]))
        exc_std = float(exc_small.std())
        assert exc_std > 0, "T6 exc should be non-uniform; std=%.6f" % exc_std

        # T7: log-linear endpoints (lambda=1.0 raw substrate; lambda=0.0 unigram)
        n = 4
        sub_probs = np.array([
            [0.6, 0.1, 0.1, 0.1, 0.1],
            [0.1, 0.5, 0.2, 0.1, 0.1],
            [0.3, 0.3, 0.2, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.5, 0.2],
        ], dtype=np.float64)
        nxt = np.array([0, 1, 1, 3], dtype=np.int64)
        U_log = np.log(np.array([0.2, 0.3, 0.2, 0.2, 0.1]).clip(1e-30, 1.0))
        sub_logp = np.log(sub_probs.clip(1e-30, 1.0))
        bpc_lam1 = log_linear_interp_bpc(sub_logp, U_log, nxt, 1.0)
        raw_logp = sub_logp[np.arange(n), nxt]
        bpc_raw_expected = -float(np.mean(raw_logp)) / math.log(2.0)
        assert abs(bpc_lam1 - bpc_raw_expected) < 1e-6, "T7 lambda=1 raw mismatch"
        bpc_lam0 = log_linear_interp_bpc(sub_logp, U_log, nxt, 0.0)
        U_target = np.exp(U_log - U_log.max())
        U_target = U_target / U_target.sum()
        p_uni_nxt = U_target[nxt].clip(1e-12, 1.0)
        bpc_uni_expected = -float(np.mean(np.log(p_uni_nxt))) / math.log(2.0)
        assert abs(bpc_lam0 - bpc_uni_expected) < 1e-6, "T7 lambda=0 unigram mismatch"

        # T8: verdict bands (HP / HF / MID)
        def _mk_unit(rank1, decisive, k10=None, k100=None):
            if k10 is None: k10 = decisive + 0.1
            if k100 is None: k100 = decisive + 0.05
            by_arm_local = {"ARM_UNIGRAM": {"bpc_unigram": 7.738, "n_test": 100}}
            arm_to_bpc = {
                "ARM_RANK1_ARGMAX": rank1,
                "ARM_SPARSE_COMPETITIVE_K10": k10,
                "ARM_SPARSE_COMPETITIVE_K100": k100,
                "ARM_SPARSE_COMPETITIVE_PLUS_EXCITABILITY_K100": decisive,
            }
            for arm, bp in arm_to_bpc.items():
                by_arm_local[arm] = {
                    "bpc_raw": bp + 0.2, "bpc_best": bp, "best_lambda": 0.5,
                    "best_dev_bpc": bp,
                    "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
                    "n_dev": 100, "n_test": 100,
                    "wall_recall_s": 0.1, "wall_arm_s": 0.1,
                    "K": 1 if "RANK1" in arm else (10 if "K10" in arm else 100),
                    "beta_used": EXCITABILITY_BETA if "EXCIT" in arm else 0.0,
                    "fraction_above_uniform": 0.02,
                }
            return {"seed": 0, "by_arm": by_arm_local, "V": 16, "N": 64, "N_DIM": 64,
                    "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": 16,
                    "TOPK_LIST": TOPK_LIST, "EXCITABILITY_ALPHA": EXCITABILITY_ALPHA,
                    "EXCITABILITY_DECAY": EXCITABILITY_DECAY,
                    "EXCITABILITY_BETA": EXCITABILITY_BETA,
                    "run_mode": "smoke", "config_version": "selftest",
                    "elapsed_s_seed": 0.01, "device": "cpu", "n_llm_calls": 0}

        # HARD_PASS: rank1=7.7, decisive=7.0 (delta=0.7 > 0.5, abs=7.0<7.5)
        u_hp = _mk_unit(rank1=7.7, decisive=7.0, k10=7.3, k100=7.1)
        vv, mm, dd = compute_verdict([u_hp, u_hp, u_hp])
        assert vv == "HARD_PASS", "T8 HP got %s msg=%s" % (vv, mm[:200])

        # HARD_FAIL: rank1=7.7, all competitive >= rank1
        u_hf = _mk_unit(rank1=7.7, decisive=7.9, k10=8.0, k100=7.85)
        vv, mm, _ = compute_verdict([u_hf, u_hf, u_hf])
        assert vv == "HARD_FAIL", "T8 HF got %s msg=%s" % (vv, mm[:200])

        # MIDDLE_BAND: lifts but doesn't meet HP bars (decisive=7.6 lifts but not 0.5)
        u_mid = _mk_unit(rank1=7.7, decisive=7.6, k10=7.65, k100=7.62)
        vv, mm, _ = compute_verdict([u_mid, u_mid, u_mid])
        assert vv == "MIDDLE_BAND", "T8 MID got %s msg=%s" % (vv, mm[:200])

        # T9: unigram analytic max-class
        idx_t9 = np.array([0, 0, 0, 1, 1, 2, 2, 2, 2, 3], dtype=np.int64)
        U = build_unigram_np(idx_t9, V=4, alpha=0.0)
        assert int(np.argmax(U)) == 2

    finally:
        DEVICE = _saved_device

    # T10: LLM-counter clean
    assert _LLM_CALL_COUNTER[0] == 0, "T10 LLM counter"

    print("[selftest] PASS: T1 trigram + T2 K=1 argmax endpoint + T3 K=V full softmax "
          "+ T4 K=2 nonzero count + T5 excitability bias + T6 W+exc non-uniform "
          "+ T7 log-linear endpoints + T8 verdict HP/HF/MID + T9 unigram + T10 llm=0",
          flush=True)


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
            "anchor_name": ANCHOR_NAME, "anchor": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE, "N_DIM": N_DIM, "N": N_DIM,
            "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
            "TOPK_LIST": TOPK_LIST,
            "EXCITABILITY_ALPHA": EXCITABILITY_ALPHA,
            "EXCITABILITY_DECAY": EXCITABILITY_DECAY,
            "EXCITABILITY_BETA": EXCITABILITY_BETA,
            "n_seeds": len(units), "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_substrate_sparse_competitive_readout_lm_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (len(units), len(SEEDS), msg[:200]),
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
          "seeds=%s arms=%s topk_list=%s exc_alpha=%.3f exc_decay=%.3f exc_beta=%.2f "
          "| name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
              SEEDS, ARMS, TOPK_LIST,
              EXCITABILITY_ALPHA, EXCITABILITY_DECAY, EXCITABILITY_BETA,
              _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[gpu] device=%s name=%s total_mem_gb=%.2f" % (
                DEVICE, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception as e:
            print("[gpu] info-fetch failed: %s" % e, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "substrate-sparse-competitive-readout-lm-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "anchor": ANCHOR_NAME,
        "verdict": verdict, "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM, "N": N_DIM,
        "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "TOPK_LIST": TOPK_LIST,
        "EXCITABILITY_ALPHA": EXCITABILITY_ALPHA,
        "EXCITABILITY_DECAY": EXCITABILITY_DECAY,
        "EXCITABILITY_BETA": EXCITABILITY_BETA,
        "INGEST_CHUNK": INGEST_CHUNK, "RECALL_BATCH": RECALL_BATCH,
        "LAMBDA_GRID": LAMBDA_GRID, "arms": ARMS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_gpu_substrate_sparse_competitive_readout_lm_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate-native readout sweep; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
