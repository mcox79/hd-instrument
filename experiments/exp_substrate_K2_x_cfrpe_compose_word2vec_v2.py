"""
substrate_K2_x_cfrpe_compose_word2vec_v2 -- RESCUE of v1 (char-trigram methodology-confound).

v1 (substrate_K2_x_cfrpe_compose_LM_v1) landed MIDDLE_BAND but used CHAR-TRIGRAM
encoder. ARM_BASELINE_RANK1_K1 came in at 7.6968 BPC, vs fair_harness chain-grade
reference 7.3065 BPC (sparse-bipolar word2vec). The ~0.39 BPC drift IS the encoder;
the v1 result is methodology-confound, not a true K=2 x cf-RPE compose measurement.

This rescue:
  - Uses word2vec-projected sparse-bipolar encoder (matches fair_harness chain-grade)
  - Torch + CUDA (Fix #24: GPU dispatch must actually use GPU)
  - LAMBDA_GRID excludes 0.0 (Skunkworks META C7: lambda=0 ignores substrate)
  - Same 4 arms / 3 seeds / N_DIM_TOTAL=8192 / N_TRAIN=100k as v1
  - Per-context T diagnostic via raw_bpc_at_T1_L1 sanity gate + joint (T,lambda) sweep
  - LLM-call counter asserted == 0 at metrics.json write (substrate-only audit)

FOUR ARMS:
  ARM_BASELINE_RANK1_K1  -- single bank, rank-1 Hebbian; sanity-rail vs 7.3065
  ARM_CFRPE_K1           -- cf-RPE on single bank; chain-grade reference at 7.1052
  ARM_K2_RANK1           -- 2 banks each N=4096, rank-1 Hebbian per bank
  ARM_K2_CFRPE           -- cf-RPE per bank in K=2 architecture; the COMBINED arm

PRE-REG HARD bands:
  Sanity rail: ARM_BASELINE_RANK1_K1 within +/-0.05 of fair_harness 7.3065 (provenance)
  HARD_PASS: ARM_K2_CFRPE beats ARM_CFRPE_K1 by >= +0.10 bits
             AND ARM_K2_CFRPE BPC <= 7.0552 (beats cf-RPE chain-grade ref 7.1052 by +0.05)
  CHAIN_GRADE_BONUS: ARM_K2_CFRPE BPC <= 6.95 (beats all known cf-RPE single-arm)
  MIDDLE_BAND: ARM_K2_CFRPE lift over ARM_CFRPE_K1 in [+0.03, +0.10] bits
  HARD_FAIL: ARM_K2_CFRPE BPC >= max(ARM_CFRPE_K1, ARM_K2_RANK1) BPC (no compose lift)
  cv < 0.05 all arms

WHAT_THIS_DOES_NOT_SHOW:
  - Does not test K > 2 (only K=2 vs K=1 contrast)
  - Does not test cf-RPE with STDP (heterogeneous arm tested in prior cell)
  - Soft gate (softmax) is not hard winner-takes-all as in Drosophila MB
  - Gate parameters not trained end-to-end; gate quality is fixed-random-projection
  - N_DIM_TOTAL=8192 split into 2 banks of 4096; each bank half the resolution of K=1
  - Result at N_TRAIN=100k text8; may not generalize to other corpora

Cites:
  preregs/2026-06-24_substrate_K2_x_cfrpe_compose_word2vec_v2.md
  experiments/exp_substrate_K2_x_cfrpe_compose_LM_v1.py (v1 methodology-confound)
  experiments/exp_fair_harness_substrate_as_lm_v1.py (encoder pipeline; chain-grade ref)
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py
  notes/shotgun_smoke_K_bank_count_sweep_2026-06-23.md (K=2 lift smoke)
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

ANCHOR_NAME = "substrate_K2_x_cfrpe_compose_word2vec_v2"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only audit counter (Skunkworks structural blocker)
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Pre-reg threshold bands (pre-registered; do NOT modify post-smoke)
# ============================================================================
# All "lift" measured as BPC reduction vs ARM_BASELINE_RANK1_K1 (lower BPC is better)
BASELINE_BPC_REF = 7.3065             # fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR
CFRPE_K1_BPC_REF = 7.1052             # cf-RPE chain-grade single-arm reference
BASELINE_TOLERANCE = 0.05             # sanity rail: ARM_BASELINE_RANK1_K1 within +/- this
HARD_PASS_BPC_BAR = 7.0552            # CFRPE_K1_BPC_REF - 0.05 (beat chain-grade by 0.05)
HARD_PASS_LIFT_OVER_CFRPE = 0.10      # ARM_K2_CFRPE beats ARM_CFRPE_K1 by >= +0.10 bits
MIDDLE_BAND_LIFT_LOW = 0.03           # MB lower bound on K2_CFRPE - CFRPE_K1 BPC reduction
MIDDLE_BAND_LIFT_HIGH = 0.10          # MB upper bound (= HARD_PASS_LIFT_OVER_CFRPE)
CHAIN_GRADE_BONUS_BPC = 6.95          # bonus: beat all known cf-RPE single-arm
CV_MAX = 0.05                          # cv across seeds mandatory

# ============================================================================
# Plasticity knob parameters (exact values from cf-RPE chain-grade cell)
# ============================================================================
CFRPE_LR = 0.5
INGEST_BATCH = 64
N_STEPS_PER_SEED = 300

# K-bank config
K_BANKS = 2
GATE_TEMP = 0.5

# Eval hyperparameter grids (LAMBDA_GRID excludes 0.0 per Skunkworks META C7)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Encoder
SPARSE_BIPOLAR_F = 0.05
WORD2VEC_MODEL = "word2vec-google-news-300"
PRETRAIN_DIM = 300

# Arms
ARMS = [
    "ARM_BASELINE_RANK1_K1",
    "ARM_CFRPE_K1",
    "ARM_K2_RANK1",
    "ARM_K2_CFRPE",
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
    # Smoke: must fit under 180s on CPU. Exercises every arm + word2vec encoder
    # + joint sweep + verdict bands. Uses real word2vec (not char-trigram) so
    # smoke ARM_BASELINE_RANK1_K1 reflects the methodology fix.
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
    "substrate_K2_x_cfrpe_compose_word2vec_v2; encoder=word2vec_sparse_bipolar; "
    "N_DIM_TOTAL=%d K_BANKS=%d N_DIM_PER_BANK=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d "
    "arms=%s seeds=%s mode=%s temps=%s lambdas=%s sparse_f=%.3f cfrpe_lr=%.3f "
    "gate_temp=%.3f n_steps=%d batch=%d device=%s"
) % (
    N_DIM_TOTAL, K_BANKS, N_DIM_PER_BANK, N_TRAIN, N_HELD, VOCAB_CAP,
    ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID, SPARSE_BIPOLAR_F, CFRPE_LR,
    GATE_TEMP, N_STEPS, INGEST_BATCH, str(DEVICE),
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
# Encoder: word2vec-projected sparse-bipolar (MATCHES fair_harness chain-grade)
# ============================================================================
# OOV fallback: char-trigram (defensive; small fraction of vocab on text8 V=4000)

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
    """Defensive gensim load via tools.gensim_load_helper. See helper docstring."""
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

    Pipeline: word2vec(300) -> Gaussian-project(300 -> n_dim) -> L2 normalize.
    OOV words: fall back to char-trigram encoding (no zero-row degeneracy).
    Matches fair_harness ARM_SUBSTRATE_WORD2VEC_DENSE / SPARSE_BIPOLAR encoder.
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
# Plasticity rules (torch port of cf-RPE / Hebbian; runs on GPU)
# ============================================================================

def build_W_rank1_hebbian_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                                ingest_chunk: int) -> torch.Tensor:
    """One-pass batched outer-product rank-1 Hebbian.

    W = sum_{t} E[idx[t+1]]^T @ E[idx[t]]  (shape: dim x dim)
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
    """Iterative cf-RPE delta-rule plasticity (torch port).

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


# ============================================================================
# K=1 and K=2 logits builders
# ============================================================================

def _build_W_k1(arm_mode: str, E_full: torch.Tensor,
                idx_train_t: torch.Tensor, n_steps: int,
                batch: int, lr: float, seed: int, arm_idx: int,
                ingest_chunk: int) -> torch.Tensor:
    if arm_mode == "hebbian":
        return build_W_rank1_hebbian_gpu(E_full, idx_train_t, ingest_chunk)
    return build_W_cfrpe_gpu(E_full, idx_train_t, n_steps, batch, lr, seed, arm_idx)


def build_logits_k1_gpu(arm_mode: str, E_full: torch.Tensor,
                         idx_train_t: torch.Tensor, idx_held_t: torch.Tensor,
                         n_steps: int, batch: int, lr: float,
                         seed: int, arm_idx: int,
                         recall_batch: int, ingest_chunk: int) -> Dict:
    """Compute [n_held, V] logits for K=1 arm on GPU."""
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device
    t0 = time.time()
    W = _build_W_k1(arm_mode, E_full, idx_train_t, n_steps, batch, lr,
                    seed, arm_idx, ingest_chunk)
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
    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
    }


def build_logits_k2_gpu(arm_mode: str, E_full: torch.Tensor,
                         idx_train_t: torch.Tensor, idx_held_t: torch.Tensor,
                         n_steps: int, batch: int, lr: float,
                         seed: int, arm_idx: int,
                         recall_batch: int, gate_temp: float,
                         ingest_chunk: int) -> Dict:
    """Compute [n_held, V] logits for K=2 bank arm on GPU.

    Each bank sees its own N_per slice of E_full.
    Gate uses bank-0 slice as gate signal (same as shotgun smoke).
    Write: per-bank W updated with gate-weighted plasticity.
    Read: gate-weighted sum of per-bank predictions.
    """
    V, n_dim = E_full.shape
    K = K_BANKS
    N_per = n_dim // K
    device = E_full.device

    # Bank slices of E
    E_banks = [E_full[:, k * N_per:(k + 1) * N_per].contiguous() for k in range(K)]

    # Gate projection W_gate (K, N_per)
    rng_gate = np.random.default_rng(seed * 7919 + arm_idx * 1013 + 9999)
    W_gate_np = rng_gate.standard_normal((K, N_per)).astype(np.float32)
    W_gate_np /= np.linalg.norm(W_gate_np, axis=1, keepdims=True) + 1e-9
    W_gate = torch.from_numpy(W_gate_np).to(device=device, dtype=TORCH_DTYPE)

    # Per-bank W matrices
    W_banks = [torch.zeros((N_per, N_per), dtype=TORCH_DTYPE, device=device)
               for _ in range(K)]

    t0 = time.time()
    n_pairs = idx_train_t.shape[0] - 1

    if arm_mode == "hebbian":
        # Soft-gate weighted outer-product per bank
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
    else:
        # cf-RPE iterative; gate-weighted update per bank
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
                error_k = Nxt_k - Ctx_k @ W_banks[k].T
                dW_k = (error_k * gw).T @ Ctx_k / float(batch)
                W_banks[k] = W_banks[k] + lr * dW_k

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    # Recall: gate-weighted sum of bank predictions
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
    for k in range(K):
        del E_banks[0]
    del W_banks, W_gate, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
    }


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
    """BPC at T=1, lambda=1 (no temperature, no unigram interp). DEGEN sanity."""
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
    """Joint (T, lambda) sweep on dev; pick best per-metric; report on test.

    Also captures per-context-T diagnostic: best_T per LAMBDA on dev, to expose
    whether the substrate prefers different temperatures at different lambda.
    """
    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}

    # Per-lambda diagnostic: best T at each lambda (DEGEN+T-context probe)
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
            # per-lambda best-T tracker
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
# Instrumentation self-test (MANDATORY)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null / non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    # ST1: cf-RPE delta shrinks prediction error (core plasticity rule)
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

    # ST2: gate-softmax probs sum to 1 (torch)
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
        "ST2 gate probs don't sum to 1: %.6f" % float(probs_st.sum()))
    assert (probs_st >= 0).all().item(), "ST2 gate probs contain negative values"
    print("[selftest] ST2 gate probs sum=%.6f OK" % float(probs_st.sum()), flush=True)

    # ST3: build_logits_k1_gpu produces non-zero logits for tiny synthetic data
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
                              n_steps=5, batch=3, lr=0.5, seed=0, arm_idx=0,
                              recall_batch=4, ingest_chunk=4)
    logits_st = ar["logits"]
    assert logits_st is not None, "ST3 logits is None"
    assert logits_st.shape == (idx_h_st.shape[0], V_st), (
        "ST3 logits shape mismatch: %s" % str(logits_st.shape))
    assert not np.all(logits_st == 0.0), "ST3 logits all zero"
    print("[selftest] ST3 build_logits_k1_gpu shape=%s non-zero OK" % str(logits_st.shape), flush=True)

    # ST4: build_logits_k2_gpu produces non-zero logits for tiny synthetic data
    ar4 = build_logits_k2_gpu("hebbian", E_sb, idx_tr_st, idx_h_st,
                               n_steps=5, batch=3, lr=0.5, seed=0, arm_idx=1,
                               recall_batch=4, gate_temp=GATE_TEMP, ingest_chunk=4)
    logits4 = ar4["logits"]
    assert logits4 is not None, "ST4 K=2 logits is None"
    assert logits4.shape == (idx_h_st.shape[0], V_st), "ST4 K=2 logits shape mismatch"
    assert not np.all(logits4 == 0.0), "ST4 K=2 logits all zero"
    print("[selftest] ST4 build_logits_k2_gpu shape=%s non-zero OK" % str(logits4.shape), flush=True)

    # ST5: K=1 and K=2 logits differ
    diff_st = float(np.abs(logits_st - logits4).mean())
    assert diff_st > 1e-6, "ST5 K=1 and K=2 logits identical (no architecture difference)"
    print("[selftest] ST5 K=1 vs K=2 differ (mean_abs_diff=%.4e) OK" % diff_st, flush=True)

    # ST6: joint_sweep returns finite metrics for small synthetic
    n_tok_st = 30
    n_v_sm = 6
    rng6 = np.random.default_rng(99)
    logits_syn = rng6.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_syn = rng6.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_log_st = np.log(np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32))
    nd = n_tok_st // 2
    jr = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                     nxt_syn[:nd], nxt_syn[nd:])
    assert math.isfinite(jr["bpc_best"]), "ST6 bpc_best not finite"
    assert math.isfinite(jr["top1_acc"]), "ST6 top1_acc not finite"
    assert math.isfinite(jr["mrr_at_10"]), "ST6 mrr_at_10 not finite"
    assert jr["n_dev"] > 0, "ST6 n_dev == 0"
    assert jr["n_test"] > 0, "ST6 n_test == 0"
    # Confirm per-lambda T diagnostic was captured
    assert isinstance(jr["per_lambda_T_summary"], dict) and len(jr["per_lambda_T_summary"]) > 0, (
        "ST6 per_lambda_T_summary not captured")
    print("[selftest] ST6 joint_sweep OK (bpc=%.3f top1=%.4f mrr=%.4f, %d lambdas tracked)" % (
        jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"], len(jr["per_lambda_T_summary"])), flush=True)

    # ST7: sparsify_bipolar_gpu produces correct fraction nonzero
    E_chk = torch.from_numpy(np.random.default_rng(0).standard_normal((20, 100)).astype(np.float32)).to(DEVICE)
    E_sparse = sparsify_bipolar_gpu(E_chk, 0.05)
    nnz_per_row = (E_sparse != 0).sum(dim=1).cpu().numpy()
    expected_nnz = max(1, int(round(0.05 * 100)))
    assert bool((nnz_per_row == expected_nnz).all()), (
        "ST7 sparse nnz mismatch: expected %d, got %s" % (expected_nnz, str(nnz_per_row[:5])))
    print("[selftest] ST7 sparsify_bipolar_gpu nnz=%d OK" % expected_nnz, flush=True)

    # ST8: LAMBDA_GRID excludes 0.0 (Skunkworks META C7)
    assert 0.0 not in LAMBDA_GRID, "ST8 LAMBDA_GRID must exclude 0.0 (Skunkworks META C7)"
    print("[selftest] ST8 LAMBDA_GRID excludes 0.0 OK", flush=True)

    # ST9: LLM-call counter is zero at selftest end (substrate-only invariant)
    assert _LLM_CALL_COUNTER[0] == 0, "ST9 LLM call counter non-zero: %d" % _LLM_CALL_COUNTER[0]
    print("[selftest] ST9 LLM call counter == 0 OK", flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

ARM_CONFIGS = {
    "ARM_BASELINE_RANK1_K1": {"k": 1, "mode": "hebbian"},
    "ARM_CFRPE_K1":           {"k": 1, "mode": "cfrpe"},
    "ARM_K2_RANK1":           {"k": 2, "mode": "hebbian"},
    "ARM_K2_CFRPE":           {"k": 2, "mode": "cfrpe"},
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
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM_TOTAL, str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]), flush=True)

    # Build encoder ONCE per seed: word2vec -> Gaussian-project -> sparse-bipolar -> L2
    print("\n[seed=%d] building word2vec encoder (V=%d, N_DIM=%d)..." % (
        seed, V, N_DIM_TOTAL), flush=True)
    t_enc0 = time.time()
    E_proj_t, w2v_meta = build_E_word2vec(vocab, N_DIM_TOTAL, seed)
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
        print("\n  [seed=%d arm=%s k=%d mode=%s] computing..." % (
            seed, arm, cfg["k"], cfg["mode"]), flush=True)
        try:
            if cfg["k"] == 1:
                ar = build_logits_k1_gpu(
                    cfg["mode"], E_full, idx_train_t, idx_held_t,
                    n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR,
                    seed=seed, arm_idx=arm_idx, recall_batch=RECALL_BATCH,
                    ingest_chunk=INGEST_CHUNK,
                )
            else:
                ar = build_logits_k2_gpu(
                    cfg["mode"], E_full, idx_train_t, idx_held_t,
                    n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR,
                    seed=seed, arm_idx=arm_idx, recall_batch=RECALL_BATCH,
                    gate_temp=GATE_TEMP, ingest_chunk=INGEST_CHUNK,
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
        # Align to ctx_full domain
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
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "n_valid_seeds": len(valid),
            "all_seeds_failed": False,
        }
        arm_bpc[arm] = b_mean
        arm_cv[arm] = b_cv

    # Lifts: positive = better than baseline (lower BPC is better)
    baseline_bpc = arm_bpc.get("ARM_BASELINE_RANK1_K1", float("inf"))
    cfrpe_k1_bpc = arm_bpc.get("ARM_CFRPE_K1", float("inf"))
    k2_rank1_bpc = arm_bpc.get("ARM_K2_RANK1", float("inf"))
    k2_cfrpe_bpc = arm_bpc.get("ARM_K2_CFRPE", float("inf"))

    lift_cfrpe_k1 = baseline_bpc - cfrpe_k1_bpc
    lift_k2_rank1 = baseline_bpc - k2_rank1_bpc
    lift_k2_cfrpe = baseline_bpc - k2_cfrpe_bpc

    # K2_CFRPE vs CFRPE_K1: positive = K2_CFRPE BPC is lower
    k2cfrpe_lift_over_cfrpe = cfrpe_k1_bpc - k2_cfrpe_bpc

    # Sanity rail
    baseline_drift = abs(baseline_bpc - BASELINE_BPC_REF) if math.isfinite(baseline_bpc) else float("inf")
    sanity_rail_ok = baseline_drift <= BASELINE_TOLERANCE

    # cv check
    k2_cfrpe_cv = arm_cv.get("ARM_K2_CFRPE", float("nan"))
    all_cv_ok = all(
        math.isfinite(arm_cv.get(a, float("nan"))) and arm_cv[a] <= CV_MAX
        for a in ARMS
    )

    best_single_knob_bpc = min(cfrpe_k1_bpc, k2_rank1_bpc)

    arm_summary = (
        "uni=%.3f | BASE=%.4f(drift=%+.4f) | CFRPE_K1=%.4f(lift=%+.3f) | "
        "K2_HEB=%.4f(lift=%+.3f) | K2_CFRPE=%.4f(lift=%+.3f, vs_CFRPE_K1=%+.3f) | "
        "cv_K2CFRPE=%.3f | sanity_rail=%s"
    ) % (
        unigram_bpc,
        baseline_bpc, baseline_bpc - BASELINE_BPC_REF,
        cfrpe_k1_bpc, lift_cfrpe_k1,
        k2_rank1_bpc, lift_k2_rank1,
        k2_cfrpe_bpc, lift_k2_cfrpe, k2cfrpe_lift_over_cfrpe,
        k2_cfrpe_cv if math.isfinite(k2_cfrpe_cv) else -1.0,
        str(sanity_rail_ok),
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "lift_cfrpe_k1": round(lift_cfrpe_k1, 4),
        "lift_k2_rank1": round(lift_k2_rank1, 4),
        "lift_k2_cfrpe": round(lift_k2_cfrpe, 4),
        "k2cfrpe_lift_over_cfrpe_k1": round(k2cfrpe_lift_over_cfrpe, 4),
        "best_single_knob_bpc": round(best_single_knob_bpc, 4),
        "hard_pass_bpc_bar": HARD_PASS_BPC_BAR,
        "hard_pass_lift_over_cfrpe": HARD_PASS_LIFT_OVER_CFRPE,
        "middle_band_lift_low": MIDDLE_BAND_LIFT_LOW,
        "middle_band_lift_high": MIDDLE_BAND_LIFT_HIGH,
        "chain_grade_bonus_bpc": CHAIN_GRADE_BONUS_BPC,
        "cv_max": CV_MAX,
        "baseline_bpc": round(baseline_bpc, 4),
        "baseline_bpc_ref": BASELINE_BPC_REF,
        "baseline_drift": round(baseline_drift, 4),
        "baseline_tolerance": BASELINE_TOLERANCE,
        "sanity_rail_ok": bool(sanity_rail_ok),
        "all_cv_ok": bool(all_cv_ok),
        "n_seeds": len(units),
        "unigram_bpc": round(unigram_bpc, 4),
        "honest_scope": (
            "K=2 multi-bank x cf-RPE compose at production scale, "
            "WORD2VEC-PROJECTED sparse-bipolar encoder (RESCUE of v1 char-trigram "
            "methodology-confound). N_DIM_TOTAL=8192 (4096/bank), N_TRAIN=100k "
            "text8, V=4000. LAMBDA_GRID excludes 0.0 (Skunkworks META C7). "
            "WHAT_THIS_DOES_NOT_SHOW: does not test K>2; gate not end-to-end trained; "
            "K=2 arms use N=4096 per bank vs K=1 uses N=8192 (resolution tradeoff); "
            "result at text8 V=4000 may not generalize to other corpora."
        ),
        "cites": [
            "preregs/2026-06-24_substrate_K2_x_cfrpe_compose_word2vec_v2.md",
            "experiments/exp_substrate_K2_x_cfrpe_compose_LM_v1.py",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
            "experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py",
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

    k2_cfrpe_failed = by_arm_agg.get("ARM_K2_CFRPE", {}).get("all_seeds_failed", True)
    if k2_cfrpe_failed:
        return ("HARD_FAIL", "HARD_FAIL: ARM_K2_CFRPE all seeds failed. " + arm_summary, detail)

    # Provenance sanity-rail fires ONLY in run_mode=full (where the V=4000 N_DIM=8192
    # N_TRAIN=100k config matches the fair_harness reference). At smoke scale the V/N
    # differ structurally; baseline absolute BPC will diverge by construction.
    detail["provenance_check_active"] = (RUN_MODE == "full")
    if RUN_MODE == "full" and not sanity_rail_ok:
        return ("HARD_FAIL_PROVENANCE",
                "HARD_FAIL_PROVENANCE: ARM_BASELINE_RANK1_K1=%.4f drifts %.4f from "
                "fair_harness ref %.4f (>tol %.2f). Encoder pipeline mismatch. %s" % (
                    baseline_bpc, baseline_drift, BASELINE_BPC_REF,
                    BASELINE_TOLERANCE, arm_summary),
                detail)

    if math.isfinite(k2_cfrpe_cv) and k2_cfrpe_cv > CV_MAX:
        return ("MIDDLE_BAND_HIGH_CV",
                "MIDDLE_BAND_HIGH_CV: cv=%.3f > %.2f. k2cfrpe_lift_over_cfrpe=%+.3f. %s" % (
                    k2_cfrpe_cv, CV_MAX, k2cfrpe_lift_over_cfrpe, arm_summary),
                detail)

    # CHAIN_GRADE_BONUS check
    if math.isfinite(k2_cfrpe_bpc) and k2_cfrpe_bpc <= CHAIN_GRADE_BONUS_BPC:
        detail["verdict_tier"] = "CHAIN_GRADE_BONUS"
        return ("HARD_PASS",
                "HARD_PASS CHAIN_GRADE_BONUS: ARM_K2_CFRPE=%.4f <= %.3f. "
                "Beats all known cf-RPE single-arm. %s" % (
                    k2_cfrpe_bpc, CHAIN_GRADE_BONUS_BPC, arm_summary),
                detail)

    # HARD_PASS: both (a) K2_CFRPE BPC <= HARD_PASS_BPC_BAR and (b) lift over CFRPE_K1 >= +0.10
    if (math.isfinite(k2_cfrpe_bpc) and k2_cfrpe_bpc <= HARD_PASS_BPC_BAR
            and k2cfrpe_lift_over_cfrpe >= HARD_PASS_LIFT_OVER_CFRPE):
        detail["verdict_tier"] = "HARD_PASS_COMPOSE"
        return ("HARD_PASS",
                "HARD_PASS: ARM_K2_CFRPE=%.4f <= %.4f AND lift_over_CFRPE_K1=%+.3f >= +%.2f. "
                "K=2 x cf-RPE compose super-additively beyond cf-RPE chain-grade single-arm. %s" % (
                    k2_cfrpe_bpc, HARD_PASS_BPC_BAR, k2cfrpe_lift_over_cfrpe,
                    HARD_PASS_LIFT_OVER_CFRPE, arm_summary),
                detail)

    # MIDDLE_BAND: lift in [+0.03, +0.10)
    if (math.isfinite(k2cfrpe_lift_over_cfrpe)
            and MIDDLE_BAND_LIFT_LOW <= k2cfrpe_lift_over_cfrpe < MIDDLE_BAND_LIFT_HIGH):
        detail["verdict_tier"] = "MIDDLE_BAND_COMPOSE"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: lift_over_CFRPE_K1=%+.3f in [%+.2f, %+.2f). "
                "K=2 x cf-RPE compose sub-additively. %s" % (
                    k2cfrpe_lift_over_cfrpe, MIDDLE_BAND_LIFT_LOW,
                    MIDDLE_BAND_LIFT_HIGH, arm_summary),
                detail)

    # HARD_FAIL: K2_CFRPE doesn't beat the better single-knob (no compose lift)
    detail["verdict_tier"] = "INTERFERENCE_OR_NULL"
    return ("HARD_FAIL",
            "HARD_FAIL: lift_over_CFRPE_K1=%+.3f < +%.2f (compose insufficient). "
            "K2_CFRPE_BPC=%.4f vs best_single=%.4f. %s" % (
                k2cfrpe_lift_over_cfrpe, MIDDLE_BAND_LIFT_LOW,
                k2_cfrpe_bpc, best_single_knob_bpc, arm_summary),
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
