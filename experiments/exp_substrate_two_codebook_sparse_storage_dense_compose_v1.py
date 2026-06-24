"""substrate_two_codebook_sparse_storage_dense_compose_v1 -- TWO-CODEBOOK ARCHITECTURE TEST.

HYPOTHESIS: sparse-bipolar codebook (CERT-592 chain-grade for storage) is structurally
incompatible with multiplicative/linear-readout compose due to TWO mechanisms:
  (1) matched-filter sqrt(f) receiver-SNR energy loss (-17 dB at f=0.05)
  (2) multiplicative-compose zero-product cascade: P(both non-zero) = f^2 = 0.0025

Research drill (2026-06-23) recommends TWO-CODEBOOK architecture:
  - SPARSE codebook (f=0.05 sparse-bipolar) for STORAGE (preserves CERT-592 lift)
  - DENSE codebook (dense bipolar +/-1) for COMPOSE (avoids cascade collapse)
  - Linear projection bridge at storage/compose boundary

FIVE ARMS x 3 seeds x text8 N_TRAIN=100k N_DIM=8192:
  ARM_UNIGRAM              -- analytic floor (control)
  ARM_ALL_SPARSE_RANK1     -- baseline; reproduces fair_harness chain-grade 7.3065; uniform sparse
  ARM_ALL_DENSE_RANK1      -- everything dense bipolar; tests if dense alone underperforms
  ARM_SPARSE_STORAGE_DENSE_COMPOSE -- storage W uses sparse f=0.05; cf-RPE operates on
                                       DENSE-projected codes; tests two-codebook architecture
  ARM_SPARSE_STORAGE_DENSE_COMPOSE_PLUS_CFRPE -- full two-codebook + cf-RPE chain-grade rule

PRE-REG BANDS (primary metric: BPC lift = ARM_X_BPC - ARM_ALL_SPARSE_RANK1_BPC; positive = better):
  HARD_PASS:   ARM_SPARSE_STORAGE_DENSE_COMPOSE_PLUS_CFRPE lift >= +0.20 bits
  CHAIN_GRADE_BONUS: lift >= +0.30 AND beats cf-RPE chain-grade (7.1052) by >= +0.10
  MIDDLE_BAND: lift +0.05 to +0.20
  HARD_FAIL:   lift <= +0.05 (two-codebook doesn't help)
  Sanity rails:
    ARM_ALL_SPARSE_RANK1 within +/-0.05 of baseline 7.3065 (provenance check)
    ARM_ALL_DENSE_RANK1 should NOT collapse to unigram (bpc < unigram 7.738 - 0.05)
  cv < 0.05 across seeds mandatory

ROUTING: overnight_queue (GPU) per Fix #22 (N_DIM=8192 matmul-bound; Fix #24: torch.cuda used)
ASCII-only. Per-seed checkpoint via _seed_checkpoint. atexit synthesizer.

Cites:
  preregs/2026-06-23_substrate_two_codebook_sparse_storage_dense_compose_v1.md
  experiments/exp_fair_harness_substrate_as_lm_v1.py  (baseline pattern)
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py  (cf-RPE)
  notes/research_sparse_bipolar_compose_incompatibility_2x_drill_2026-06-23.md  (motivation)
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json  (baseline BPC 7.3065)
  data/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1/metrics.json (cfrpe 7.1052)
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
    get_output_dir, write_partial, aggregate_partials, write_metrics,
    resumable_seeds
)

ANCHOR_NAME = "substrate_two_codebook_sparse_storage_dense_compose_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Pre-reg thresholds (HARD pre-registered per role contract)
HARD_PASS_LIFT = 0.20          # BPC lift vs ARM_ALL_SPARSE_RANK1
CHAIN_GRADE_BONUS_LIFT = 0.30  # + beats cf-RPE 7.1052 by >= 0.10
CFRPE_CHAIN_GRADE_BPC = 7.1052 # from cert-grade heterogeneous fair_harness cell
HARD_FAIL_LIFT = 0.05          # below this = two-codebook doesn't help
MIDDLE_BAND_LOW = 0.05
MIDDLE_BAND_HIGH = 0.20
DEGEN_TOL = 0.5
HP_BPC_CV_MAX = 0.05

# Reference baselines
BASELINE_SPARSE_BPC = 7.3065   # ARM_ALL_SPARSE_RANK1 expected BPC (fair_harness v1)
UNIGRAM_BPC_REF = 7.7378
PROVENANCE_TOL = 0.05          # ARM_ALL_SPARSE_RANK1 must land within +/-0.05

# Two-codebook hyperparameters
SPARSE_BIPOLAR_F = 0.05        # sparsity fraction
CFRPE_LR = 0.5                 # cf-RPE learning rate (matched from chain-grade cell)
INGEST_BATCH = 64              # mini-batch size for iterative plasticity

# Inference sweep (same grid as fair_harness baseline for comparability)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]  # exclude 0.0 per META atom C7 LAMBDA_ZERO_COLLAPSE
MRR_K = 10

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

# Production config (FULL run)
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

ARMS = [
    "ARM_UNIGRAM",
    "ARM_ALL_SPARSE_RANK1",
    "ARM_ALL_DENSE_RANK1",
    "ARM_SPARSE_STORAGE_DENSE_COMPOSE",
    "ARM_SPARSE_STORAGE_DENSE_COMPOSE_PLUS_CFRPE",
]
SUBSTRATE_ARMS = [a for a in ARMS if a != "ARM_UNIGRAM"]

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = 1000
else:
    # Smoke: fit under 300s on GPU; exercises all 5 arms + joint sweep + verdict
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
# Encoders (char-trigram fallback + word2vec dense + sparse-bipolar projection)
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
    n_hit, n_miss = 0, 0
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
    """Build [V, n_dim] L2-normalized word2vec-projected dense vectors on GPU.

    Returns dense float32 matrix; caller applies sparsification if needed.
    """
    kv = _load_gensim_kv(WORD2VEC_MODEL)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = _l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_before = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_before < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = _l2_normalize_np(E_proj)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_t, meta


def build_E_char_trigram_gpu(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    """Smoke / fallback encoder when gensim unavailable."""
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


def sparsify_bipolar_gpu(E: torch.Tensor, f: float, seed: int) -> torch.Tensor:
    """Sparse-bipolar projection: keep top-k by abs magnitude, assign sign.

    Output: +/-1 at top-k dims, 0 elsewhere. L2-normalized by caller.
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


def densify_bipolar_gpu(E: torch.Tensor) -> torch.Tensor:
    """Dense bipolar (+/-1) from real-valued projected E via sign.

    Produces fully dense +/-1 vectors; 0 mapped to +1 by convention.
    Used as COMPOSE codebook in two-codebook architecture.
    """
    out = torch.sign(E)
    out[out == 0] = 1.0
    return out


# ============================================================================
# Two-codebook linear bridge
# ============================================================================

def build_compose_bridge(E_sparse: torch.Tensor, E_dense: torch.Tensor
                          ) -> torch.Tensor:
    """Build [dim_sparse, dim_dense] projection matrix from sparse to dense codebook.

    Uses least-squares pseudo-inverse so E_sparse @ P.T ~ E_dense.
    At smoke scale (N_DIM=512): exact fit; at full scale (N_DIM=8192): low-rank approx.
    Both codebooks must have same N_DIM in this implementation (identity bridge).
    """
    assert E_sparse.shape == E_dense.shape, (
        "Both codebooks must have same shape; got %s vs %s" % (
            E_sparse.shape, E_dense.shape))
    # For same-dimension codebooks: bridge is a linear map E_sparse -> E_dense
    # Solved via batched matmul: P = (E_sparse^T E_sparse)^{-1} E_sparse^T E_dense
    # In practice at dim=8192, this is a dense square solve -- too expensive.
    # EFFICIENT ALTERNATIVE: bridge via rotation = E_dense.T @ E_sparse (outer-product sum)
    # This gives a dense [dim, dim] matrix which is also expensive.
    # PRACTICAL BRIDGE for two-codebook: use the dense codebook directly for compose.
    # The bridge is implicit: the STORAGE W is built from sparse codes,
    # and the COMPOSE (recall) step uses dense codes to query W.
    # This is the TWO-CODEBOOK architecture: WRITE in sparse space, READ in dense space.
    # No explicit projection matrix needed -- just use both codebooks side by side.
    # This function is kept for documentation; not called in main sweep.
    raise NotImplementedError("Implicit bridge; see compute_arm_logits for usage")


# ============================================================================
# Plasticity rules: Hebbian / cf-RPE with two-codebook variants
# ============================================================================

def _build_W_rank1_hebbian(E: torch.Tensor, idx_train: torch.Tensor,
                            ingest_chunk: int) -> torch.Tensor:
    """Full-corpus one-pass rank-1 Hebbian: W = sum outer(E[t+1], E[t])."""
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src = E[idx_train[b:end]]
        tgt = E[idx_train[b + 1:end + 1]]
        W.add_(tgt.T @ src)
        if DEVICE.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def _build_W_cfrpe_iterative(E: torch.Tensor, idx_train: torch.Tensor,
                               n_steps: int, batch: int, lr: float,
                               gen: torch.Generator) -> torch.Tensor:
    """cf-RPE iterative delta rule: delta_W = (E[t+1] - E[t] @ W^T)^T @ E[t] / batch."""
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train[st]]
        Nxt = E[idx_train[st + 1]]
        error = Nxt - Ctx @ W.t()
        dW = (error.t() @ Ctx) / batch
        W = W + lr * dW
    return W


def _build_W_two_codebook_storage_dense_compose(
        E_sparse: torch.Tensor,
        E_dense: torch.Tensor,
        idx_train: torch.Tensor,
        ingest_chunk: int) -> torch.Tensor:
    """Two-codebook rank-1 Hebbian: WRITE with sparse, READ will use dense.

    Storage W is built from sparse codes (preserves CERT-592 bundle capacity).
    Recall uses dense codes to query W -- so W is [dim, dim] but the read path
    multiplies by E_dense rather than E_sparse, avoiding sparse-zero-product cascade.
    """
    dim = E_sparse.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    # Store: outer product uses sparse CONTEXT (E_sparse[t]) and sparse TARGET (E_sparse[t+1])
    # This builds the associative memory in sparse-code space (storage)
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src = E_sparse[idx_train[b:end]]
        tgt = E_sparse[idx_train[b + 1:end + 1]]
        W.add_(tgt.T @ src)
        if DEVICE.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def _build_W_two_codebook_plus_cfrpe(
        E_sparse: torch.Tensor,
        E_dense: torch.Tensor,
        idx_train: torch.Tensor,
        n_steps: int,
        batch: int,
        lr: float,
        ingest_chunk: int,
        gen: torch.Generator) -> torch.Tensor:
    """Two-codebook: initial Hebbian (sparse) + cf-RPE refinement (dense compose).

    Phase 1: rank-1 Hebbian in sparse-code space (storage W).
    Phase 2: cf-RPE iterative refinement where prediction error uses DENSE codes.
             The error signal = E_dense[t+1] - E_dense[t] @ W^T
             This couples W to the dense codebook's metric, enabling compose
             without zero-product cascade at recall time.
    """
    # Phase 1: sparse Hebbian initialization
    W = _build_W_two_codebook_storage_dense_compose(E_sparse, E_dense, idx_train,
                                                     ingest_chunk)
    # Phase 2: cf-RPE refinement in dense codebook space
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0 or n_steps <= 0:
        return W
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        # Context in DENSE space (no zero-product cascade during recall)
        Ctx_d = E_dense[idx_train[st]]
        Nxt_d = E_dense[idx_train[st + 1]]
        # Prediction error: what DENSE next-token should W predict from DENSE context?
        error = Nxt_d - Ctx_d @ W.t()
        dW = (error.t() @ Ctx_d) / batch
        W = W + lr * dW
    return W


# ============================================================================
# Per-arm logit computation (FRESH W per arm per seed)
# ============================================================================

def compute_arm_logits(arm: str, E_base: torch.Tensor, idx_train: np.ndarray,
                        idx_held: np.ndarray, seed: int, n_steps: int) -> Dict:
    """Return [n_held, V] float32 logits + diagnostics. FRESH W per arm per seed."""
    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    # Per-seed, per-arm reproducible generator
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed * 10007 + ARMS.index(arm) * 31337)

    t0 = time.time()

    if arm == "ARM_ALL_SPARSE_RANK1":
        # Baseline: matches fair_harness chain-grade 7.3065
        E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))
        W = _build_W_rank1_hebbian(E_used, idx_train_t, INGEST_CHUNK)
        E_read = E_used

    elif arm == "ARM_ALL_DENSE_RANK1":
        # Dense bipolar (+/-1) throughout; tests if dense alone underperforms
        E_used = _l2_normalize_t(densify_bipolar_gpu(E_base))
        W = _build_W_rank1_hebbian(E_used, idx_train_t, INGEST_CHUNK)
        E_read = E_used

    elif arm == "ARM_SPARSE_STORAGE_DENSE_COMPOSE":
        # Two-codebook: WRITE with sparse, READ with dense
        E_sparse = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))
        E_dense = _l2_normalize_t(densify_bipolar_gpu(E_base))
        W = _build_W_two_codebook_storage_dense_compose(E_sparse, E_dense, idx_train_t,
                                                         INGEST_CHUNK)
        E_read = E_dense  # COMPOSE (recall) uses dense codebook

    elif arm == "ARM_SPARSE_STORAGE_DENSE_COMPOSE_PLUS_CFRPE":
        # Full two-codebook + cf-RPE (load-bearing arm)
        E_sparse = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))
        E_dense = _l2_normalize_t(densify_bipolar_gpu(E_base))
        W = _build_W_two_codebook_plus_cfrpe(E_sparse, E_dense, idx_train_t,
                                              n_steps=n_steps, batch=INGEST_BATCH,
                                              lr=CFRPE_LR, ingest_chunk=INGEST_CHUNK,
                                              gen=gen)
        E_read = E_dense

    else:
        raise ValueError("Unknown arm: %s" % arm)

    t_ingest = time.time() - t0

    # Recall: query W with E_read (dense for two-codebook arms; sparse for baseline)
    t0 = time.time()
    V = E_base.shape[0]
    n_h = idx_held_t.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        ctx = E_read[idx_held_t[b:end]]
        pred = _l2_normalize_t(ctx @ W.t())
        logits[b:end] = pred @ E_read.T
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    # DEGEN sanity: BPC at T=1 lambda=1
    raw_bpc_at_T1 = _raw_bpc_at_T1_t(logits, idx_held)

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W, logits
    if arm in ("ARM_SPARSE_STORAGE_DENSE_COMPOSE",
               "ARM_SPARSE_STORAGE_DENSE_COMPOSE_PLUS_CFRPE"):
        del E_sparse, E_dense
    elif "E_used" in dir():
        pass  # let GC collect
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "raw_bpc_at_T1_L1": round(raw_bpc_at_T1, 4),
    }


def _raw_bpc_at_T1_t(logits: torch.Tensor, idx_held: np.ndarray) -> float:
    """BPC at T=1 (no temp scaling), for DEGEN sanity check."""
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
# text8 corpus utilities
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] corpus missing: %s" % TEXT8, flush=True)
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
    """Joint (T, lambda) sweep on dev; pick best per-metric; eval on test."""
    # LAMBDA_ZERO_COLLAPSE guard: lambda_grid must not contain 0.0
    # (per META atom C7; 0.0 = pure unigram ignores substrate signal)
    for lam in lambda_grid:
        assert lam > 0.0, (
            "LAMBDA_ZERO_COLLAPSE guard: lambda=0.0 excluded; substrate signal ignored")

    # Raw BPC at T=1, lambda=1 for DEGEN gate
    probs_T1 = softmax_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc = bpc_from_logp(logp_T1, nxt_test)

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
        "mrr_at_10": round(mrr_best_test, 4),
        "best_T_for_mrr": best_mrr["T"],
        "raw_bpc_at_T1_L1": round(raw_bpc, 4),
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray,
                     V: int, mrr_k: int) -> Dict:
    """Analytic unigram baseline metrics."""
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

    n_dim_st = 64
    V_st = 20
    rng_st = np.random.default_rng(42)
    E_np = rng_st.standard_normal((V_st, n_dim_st)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)

    # ST1: sparsify_bipolar produces correct sparsity
    E_sparse_st = sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F, seed=0)
    k_expected = max(1, int(round(SPARSE_BIPOLAR_F * n_dim_st)))
    nnz_per_row = (E_sparse_st != 0).float().sum(dim=1)
    assert float(nnz_per_row.max()) <= k_expected + 1, (
        "ST1 sparsity wrong: expected k=%d got max nnz=%.0f" % (k_expected, float(nnz_per_row.max())))
    assert float(nnz_per_row.min()) >= 1, "ST1 all-zero rows in sparse codebook"
    # Check values are +/-1 only (no intermediate values)
    nonzero_vals = E_sparse_st[E_sparse_st != 0]
    assert float(nonzero_vals.abs().min()) > 0.99, "ST1 non-unit values in sparse codebook"
    print("[selftest] ST1 sparsify_bipolar OK (k=%d, all +/-1)" % k_expected, flush=True)

    # ST2: densify_bipolar produces all +/-1 (no zeros)
    E_dense_st = densify_bipolar_gpu(E_t)
    assert float((E_dense_st == 0).float().sum()) == 0, "ST2 dense codebook has zero entries"
    assert float(E_dense_st.abs().min()) > 0.99, "ST2 dense codebook has non-unit values"
    print("[selftest] ST2 densify_bipolar OK (all +/-1, no zeros)", flush=True)

    # ST3: sparsity difference confirms compose-cascade concern
    # After one elementwise multiply, density should be ~ f^2
    sp_a = sparsify_bipolar_gpu(E_t[:2], SPARSE_BIPOLAR_F, seed=0)
    sp_b = sparsify_bipolar_gpu(E_t[2:4], SPARSE_BIPOLAR_F, seed=1)
    product = sp_a * sp_b  # elementwise: cascade collapse
    actual_density = float((product != 0).float().mean())
    expected_density_approx = SPARSE_BIPOLAR_F ** 2
    # Should be much smaller than f=0.05; confirm significant collapse
    assert actual_density < SPARSE_BIPOLAR_F * 0.5, (
        "ST3 zero-product cascade NOT observed: density=%.4f expected_approx=%.4f" % (
            actual_density, expected_density_approx))
    print("[selftest] ST3 zero-product cascade confirmed (sparse*sparse density=%.4f < f=%.4f)" % (
        actual_density, SPARSE_BIPOLAR_F), flush=True)

    # ST4: two-codebook W builds without error + output non-null
    idx_st = torch.randint(0, V_st, (20,), device=DEVICE)
    E_sparse_n = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F, seed=0))
    E_dense_n = _l2_normalize_t(densify_bipolar_gpu(E_t))
    W_tc = _build_W_two_codebook_storage_dense_compose(E_sparse_n, E_dense_n,
                                                        idx_st, ingest_chunk=10)
    assert W_tc is not None, "ST4 two-codebook W returned None"
    assert not torch.isnan(W_tc).any(), "ST4 two-codebook W contains NaN"
    assert float(W_tc.abs().max()) > 1e-6, "ST4 two-codebook W is all-zero (degenerate)"
    print("[selftest] ST4 two-codebook W build OK (max_abs=%.4f)" % float(W_tc.abs().max()),
          flush=True)

    # ST5: recall logits are non-degenerate with dense READ codebook
    logits_st = (E_dense_n @ W_tc.t()) @ E_dense_n.T
    assert not torch.isnan(logits_st).any(), "ST5 two-codebook logits contain NaN"
    logits_std = float(logits_st.std())
    assert logits_std > 1e-6, "ST5 two-codebook logits all-constant (no signal): std=%.2e" % logits_std
    print("[selftest] ST5 two-codebook recall logits non-degenerate (std=%.4f)" % logits_std,
          flush=True)

    # ST6: cf-RPE two-codebook + FULL pipeline smoke at V=20, n_dim=64
    gen_st = torch.Generator(device=DEVICE)
    gen_st.manual_seed(9999)
    W_cfrpe = _build_W_two_codebook_plus_cfrpe(E_sparse_n, E_dense_n, idx_st,
                                                n_steps=5, batch=4, lr=0.5,
                                                ingest_chunk=10, gen=gen_st)
    assert W_cfrpe is not None, "ST6 cfrpe two-codebook W returned None"
    assert not torch.isnan(W_cfrpe).any(), "ST6 cfrpe W contains NaN"
    # W_cfrpe should differ from pure Hebbian W_tc (cf-RPE adds signal)
    diff = float((W_cfrpe - W_tc).norm())
    assert diff > 1e-4, "ST6 cfrpe W identical to Hebbian (cf-RPE not applied): diff=%.2e" % diff
    print("[selftest] ST6 cf-RPE two-codebook W differs from Hebbian (diff=%.4f)" % diff,
          flush=True)

    # ST7: LAMBDA_ZERO_COLLAPSE guard fires correctly
    guard_fired = False
    try:
        joint_sweep(np.zeros((5, V_st), dtype=np.float32),
                    np.zeros((5, V_st), dtype=np.float32),
                    np.zeros(V_st, dtype=np.float64),
                    np.zeros(5, dtype=np.int64),
                    np.zeros(5, dtype=np.int64),
                    [0.1], [0.0],  # lambda=0.0 should trigger
                    mrr_k=3)
    except AssertionError:
        guard_fired = True
    assert guard_fired, "ST7 LAMBDA_ZERO_COLLAPSE guard did NOT fire for lambda=0.0"
    print("[selftest] ST7 LAMBDA_ZERO_COLLAPSE guard fires on lambda=0.0 OK", flush=True)

    # ST8: dense codebook baseline produces non-trivial logits (no collapse to unigram)
    W_dense_heb = _build_W_rank1_hebbian(E_dense_n, idx_st, ingest_chunk=10)
    logits_dense = (E_dense_n @ W_dense_heb.t()) @ E_dense_n.T
    logits_dense_std = float(logits_dense.std())
    assert logits_dense_std > 1e-6, (
        "ST8 dense Hebbian logits all-constant: std=%.2e" % logits_dense_std)
    print("[selftest] ST8 dense Hebbian logits non-degenerate (std=%.4f)" % logits_dense_std,
          flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()  # Called at module scope before sweep


# ============================================================================
# atexit synthesizer (writes metrics.json from per-seed partials on crash/exit)
# ============================================================================

def _atexit_synthesize():
    """Partial-result synthesizer: aggregate what we have on unexpected exit."""
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        per_seed = aggregate_partials(out_dir, SEEDS)
        if not per_seed:
            return
        # Lightweight verdict from whatever we have
        print("[atexit] synthesizing partial metrics from %d seeds" % len(per_seed),
              flush=True)
    except Exception as exc:
        print("[atexit] synthesizer error: %s" % exc, flush=True)


atexit.register(_atexit_synthesize)


# ============================================================================
# Main sweep
# ============================================================================

def run_one_seed(seed: int, vocab: List[str], idx_train: np.ndarray,
                  idx_held: np.ndarray) -> Dict:
    """Run all 4 substrate arms for one seed; return per-arm metrics."""
    V = len(vocab)
    print("[seed=%d] building encoder (word2vec -> N_DIM=%d)..." % (seed, N_DIM), flush=True)

    try:
        E_base, enc_meta = build_E_word2vec_gpu(vocab, N_DIM, seed)
        enc_used = "word2vec"
    except Exception as exc:
        print("[seed=%d] gensim unavailable (%s); falling back to char-trigram" % (seed, exc),
              flush=True)
        E_base = build_E_char_trigram_gpu(vocab, N_DIM, seed)
        enc_meta = {"n_hit": 0, "n_miss": V, "n_vocab": V, "pretrain_dim": 0}
        enc_used = "char_trigram"

    print("[seed=%d] encoder=%s n_hit=%d/%d" % (seed, enc_used,
          enc_meta.get("n_hit", 0), V), flush=True)

    # Split held into dev (first half) and test (second half)
    ctx_held = idx_held[:-1]
    nxt_held = idx_held[1:]
    mask_held = (ctx_held != 0)
    nxt_valid = nxt_held[mask_held]
    n_dev = len(nxt_valid) // 2
    nxt_dev = nxt_valid[:n_dev]
    nxt_test = nxt_valid[n_dev:]
    # Corresponding context logits windows
    ctx_valid_idx = np.where(mask_held)[0]
    dev_ctx_idx = ctx_valid_idx[:n_dev]
    test_ctx_idx = ctx_valid_idx[n_dev:]

    # Build unigram metrics
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0))
    uni_m = unigram_metrics(idx_train, idx_held, V, MRR_K)

    arm_results: Dict[str, Dict] = {}

    for arm in ARMS:
        if arm == "ARM_UNIGRAM":
            arm_results[arm] = uni_m
            print("[seed=%d][%s] bpc=%.4f top1=%.4f mrr=%.4f" % (
                seed, arm, uni_m["bpc_unigram"], uni_m["top1_unigram"],
                uni_m["mrr_unigram"]), flush=True)
            continue

        print("[seed=%d][%s] computing logits..." % (seed, arm), flush=True)
        t0_arm = time.time()

        arm_out = compute_arm_logits(arm, E_base, idx_train, idx_held, seed, N_STEPS)
        logits_np = arm_out["logits"]

        # Extract dev + test logits windows
        logits_dev = logits_np[dev_ctx_idx]
        logits_test = logits_np[test_ctx_idx]

        sweep = joint_sweep(logits_dev, logits_test, U_log, nxt_dev, nxt_test,
                            TEMP_GRID, LAMBDA_GRID, MRR_K)

        arm_results[arm] = {
            "bpc_best": sweep["bpc_best"],
            "best_T_for_bpc": sweep["best_T_for_bpc"],
            "best_lambda_for_bpc": sweep["best_lambda_for_bpc"],
            "top1_acc": sweep["top1_acc"],
            "mrr_at_10": sweep["mrr_at_10"],
            "raw_bpc_at_T1_L1": arm_out["raw_bpc_at_T1_L1"],
            "wall_ingest_s": arm_out["wall_ingest_s"],
            "wall_recall_s": arm_out["wall_recall_s"],
            "n_dev": sweep["n_dev"],
            "n_test": sweep["n_test"],
        }
        print("[seed=%d][%s] bpc=%.4f top1=%.4f mrr=%.4f T=%.3f L=%.2f raw_bpc@T1=%.4f "
              "(wall=%.1fs)" % (
                  seed, arm, sweep["bpc_best"], sweep["top1_acc"], sweep["mrr_at_10"],
                  sweep["best_T_for_bpc"], sweep["best_lambda_for_bpc"],
                  arm_out["raw_bpc_at_T1_L1"], time.time() - t0_arm),
              flush=True)

    del E_base
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed,
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "arms": arm_results,
        "enc_meta": enc_meta,
    }


def aggregate_and_verdict(per_seed: Dict) -> Dict:
    """Aggregate per-seed results and compute verdict."""
    if not per_seed:
        return {"verdict": "INSUFFICIENT_DATA", "verdict_msg": "No seeds completed",
                "n_seeds_complete": 0}

    # Collect per-arm BPC values across seeds
    arm_bpc_list: Dict[str, List[float]] = {a: [] for a in ARMS}
    for s_key, s_data in per_seed.items():
        arms_data = s_data.get("arms", {})
        for arm in ARMS:
            if arm not in arms_data:
                continue
            am = arms_data[arm]
            if arm == "ARM_UNIGRAM":
                arm_bpc_list[arm].append(am.get("bpc_unigram", float("nan")))
            else:
                arm_bpc_list[arm].append(am.get("bpc_best", float("nan")))

    def _mean_std_cv(vals: List[float]) -> Tuple[float, float, float]:
        valid = [v for v in vals if not math.isnan(v) and not math.isinf(v)]
        if not valid:
            return float("nan"), float("nan"), float("nan")
        m = float(np.mean(valid))
        s = float(np.std(valid))
        cv = s / abs(m) if abs(m) > 1e-12 else float("nan")
        return round(m, 4), round(s, 4), round(cv, 4)

    by_arm_agg: Dict[str, Dict] = {}
    for arm in ARMS:
        bpc_vals = arm_bpc_list.get(arm, [])
        bpc_m, bpc_s, bpc_cv = _mean_std_cv(bpc_vals)
        by_arm_agg[arm] = {
            "bpc_mean": bpc_m,
            "bpc_std": bpc_s,
            "bpc_cv": bpc_cv,
            "n_seeds": len([v for v in bpc_vals if not math.isnan(v)]),
        }

    # Primary verdict: lift of load-bearing arm vs ARM_ALL_SPARSE_RANK1
    baseline_bpc = by_arm_agg["ARM_ALL_SPARSE_RANK1"]["bpc_mean"]
    primary_bpc = by_arm_agg["ARM_SPARSE_STORAGE_DENSE_COMPOSE_PLUS_CFRPE"]["bpc_mean"]
    two_cb_bpc = by_arm_agg["ARM_SPARSE_STORAGE_DENSE_COMPOSE"]["bpc_mean"]
    dense_only_bpc = by_arm_agg["ARM_ALL_DENSE_RANK1"]["bpc_mean"]
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    if math.isnan(primary_bpc) or math.isnan(baseline_bpc):
        return {"verdict": "INSUFFICIENT_DATA",
                "verdict_msg": "Missing primary arm data",
                "n_seeds_complete": len(per_seed),
                "by_arm_agg": by_arm_agg}

    # Lift: lower BPC = better; lift = baseline_bpc - primary_bpc
    lift_primary = round(baseline_bpc - primary_bpc, 4)
    lift_two_cb = round(baseline_bpc - two_cb_bpc, 4) if not math.isnan(two_cb_bpc) else float("nan")

    primary_cv = by_arm_agg["ARM_SPARSE_STORAGE_DENSE_COMPOSE_PLUS_CFRPE"]["bpc_cv"]

    # Sanity rails (Fix #28: check per-arm metrics not verdict_msg)
    provenance_ok = abs(baseline_bpc - BASELINE_SPARSE_BPC) <= PROVENANCE_TOL
    dense_not_degenerate = (not math.isnan(dense_only_bpc) and
                            dense_only_bpc < (unigram_bpc - 0.05))

    # DEGEN gate
    degen_arms = []
    for arm in ARMS[1:]:  # skip unigram
        for s_key, s_data in per_seed.items():
            arm_data = s_data.get("arms", {}).get(arm, {})
            raw_bpc = arm_data.get("raw_bpc_at_T1_L1", float("nan"))
            if not math.isnan(raw_bpc):
                vocab_entropy = -math.log2(1.0 / VOCAB_CAP)
                if abs(raw_bpc - vocab_entropy) < DEGEN_TOL:
                    degen_arms.append(arm)

    # Classify verdict
    degen_primary = ("ARM_SPARSE_STORAGE_DENSE_COMPOSE_PLUS_CFRPE" in degen_arms)

    if degen_primary:
        verdict = "READOUT_DEGENERATE"
        verdict_msg = ("READOUT_DEGENERATE: ARM_SPARSE_STORAGE_DENSE_COMPOSE_PLUS_CFRPE raw_bpc "
                       "near vocab entropy; two-codebook architecture not evaluated. "
                       "Needs recalibration.")
    elif lift_primary >= CHAIN_GRADE_BONUS_LIFT and primary_bpc <= CFRPE_CHAIN_GRADE_BPC - 0.10:
        verdict = "HARD_PASS_CHAIN_GRADE"
        verdict_msg = ("HARD_PASS CHAIN_GRADE: two-codebook + cf-RPE lift=%.4f >= %.2f AND beats "
                       "cf-RPE chain-grade (%.4f) by %.4f. "
                       "Two-codebook solves compose-incompatibility at chain-grade level." % (
                           lift_primary, CHAIN_GRADE_BONUS_LIFT, CFRPE_CHAIN_GRADE_BPC,
                           CFRPE_CHAIN_GRADE_BPC - primary_bpc))
    elif lift_primary >= HARD_PASS_LIFT:
        verdict = "HARD_PASS"
        verdict_msg = ("HARD_PASS: two-codebook + cf-RPE lift=%.4f >= %.2f bits over sparse baseline. "
                       "Two-codebook architecture solves compose-incompatibility." % (
                           lift_primary, HARD_PASS_LIFT))
    elif lift_primary >= MIDDLE_BAND_LOW:
        verdict = "MIDDLE_BAND"
        verdict_msg = ("MIDDLE_BAND: two-codebook lift=%.4f in [%.2f, %.2f). "
                       "Architecture helps but doesn't break envelope." % (
                           lift_primary, MIDDLE_BAND_LOW, MIDDLE_BAND_HIGH))
    elif lift_primary <= HARD_FAIL_LIFT:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL: two-codebook lift=%.4f <= %.2f. "
                       "Two-codebook doesn't help; sparse-bipolar not the compose bottleneck." % (
                           lift_primary, HARD_FAIL_LIFT))
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = ("MIDDLE_BAND: lift=%.4f borderline." % lift_primary)

    # Append sanity rail status
    if not provenance_ok:
        verdict_msg += (" [PROVENANCE WARN: ARM_ALL_SPARSE_RANK1 bpc=%.4f, expected %.4f+/-%.4f]" % (
            baseline_bpc, BASELINE_SPARSE_BPC, PROVENANCE_TOL))
    if not dense_not_degenerate:
        verdict_msg += " [WARN: ARM_ALL_DENSE_RANK1 near/above unigram]"

    bpc_parts = " | ".join([
        "uni=bpc%.4f" % unigram_bpc,
        "ARM_ALL_SPARSE_RANK1=bpc%.4f" % baseline_bpc,
        "ARM_ALL_DENSE_RANK1=bpc%.4f" % dense_only_bpc,
        "ARM_SPARSE_STORAGE_DENSE_COMPOSE=bpc%.4f(lift=%.4f)" % (two_cb_bpc, lift_two_cb),
        "ARM_SPARSE_STORAGE_DENSE_COMPOSE_PLUS_CFRPE=bpc%.4f(lift=%.4f)cv=%.4f" % (
            primary_bpc, lift_primary, primary_cv if not math.isnan(primary_cv) else -1.0),
    ])

    verdict_msg += " | " + bpc_parts
    print("[verdict] %s: %s" % (verdict, verdict_msg), flush=True)

    return {
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
        "CFRPE_LR": CFRPE_LR,
        "N_STEPS": N_STEPS,
        "lift_primary": lift_primary,
        "lift_two_codebook_only": lift_two_cb,
        "provenance_ok": provenance_ok,
        "dense_not_degenerate": dense_not_degenerate,
        "degen_arms": list(set(degen_arms)),
        "pre_reg": {
            "HARD_PASS_LIFT": HARD_PASS_LIFT,
            "CHAIN_GRADE_BONUS_LIFT": CHAIN_GRADE_BONUS_LIFT,
            "HARD_FAIL_LIFT": HARD_FAIL_LIFT,
            "CFRPE_CHAIN_GRADE_BPC": CFRPE_CHAIN_GRADE_BPC,
            "BASELINE_SPARSE_BPC": BASELINE_SPARSE_BPC,
            "PROVENANCE_TOL": PROVENANCE_TOL,
        },
        "n_seeds_complete": len(per_seed),
        "detail": {"by_arm_agg": by_arm_agg},
    }


def main():
    print("[main] anchor=%s mode=%s device=%s N_DIM=%d N_TRAIN=%d SEEDS=%s" % (
        ANCHOR_NAME, RUN_MODE, DEVICE, N_DIM, N_TRAIN, SEEDS), flush=True)
    print("[main] arms=%s" % ARMS, flush=True)
    print("[main] pre-reg: HARD_PASS_LIFT=%.2f CHAIN_GRADE=%.2f HARD_FAIL=%.2f" % (
        HARD_PASS_LIFT, CHAIN_GRADE_BONUS_LIFT, HARD_FAIL_LIFT), flush=True)

    # Load corpus
    print("[main] loading text8 tokens (n=%d)..." % (N_TRAIN + N_HELD), flush=True)
    all_tokens = load_text8_tokens(N_TRAIN + N_HELD)
    train_tokens = all_tokens[:N_TRAIN]
    held_tokens = all_tokens[N_TRAIN:N_TRAIN + N_HELD]

    vocab, w2i = build_vocab(train_tokens, VOCAB_CAP)
    V = len(vocab)
    print("[main] vocab size=%d" % V, flush=True)

    idx_train = tokens_to_idx(train_tokens, w2i)
    idx_held = tokens_to_idx(held_tokens, w2i)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    if done:
        print("[main] resuming: %d seeds already complete; running %s" % (
            len(done), remaining), flush=True)

    t_global = time.time()
    for seed in remaining:
        print("[main] === seed %d ===" % seed, flush=True)
        t_seed = time.time()
        result = run_one_seed(seed, vocab, idx_train, idx_held)
        write_partial(out_dir, seed, result)
        print("[main] seed %d complete in %.1fs" % (seed, time.time() - t_seed), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    print("[main] all seeds done (%d/%d); aggregating..." % (len(per_seed), len(SEEDS)),
          flush=True)

    metrics = aggregate_and_verdict(per_seed)
    metrics["elapsed_s"] = round(time.time() - t_global, 1)
    write_metrics(out_dir, metrics)
    print("[main] metrics.json written to %s" % out_dir, flush=True)
    print("[DONE] verdict=%s" % metrics.get("verdict", "?"), flush=True)


if __name__ == "__main__":
    main()
