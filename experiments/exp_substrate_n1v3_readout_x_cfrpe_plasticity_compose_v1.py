"""
substrate_n1_v3_readout_x_cfrpe_plasticity_compose_v1 -- compose the n1_v3
nearest-neighbor HD readout with cf-RPE plasticity at production scale.

Strategic context (Skunkworks VET 2026-06-23/24):
  n1_v3 (cert row 588) top1 = 0.4455 via VQ -> concept-sparse Willshaw recall
  -> decode-D word distribution. cf-RPE plasticity (cert MM; N=5000_cfrpe)
  top1 = 0.2438 via standard logit-mixer readout. 5x lift-ratio gap. cf-RPE
  improves STORED reps but logit-mixer doesn't extract the gain. The chain-
  grade bottleneck is the READOUT, not the plasticity.

HYPOTHESIS: combining the n1_v3 readout with cf-RPE plasticity composes both
advantages, producing super-additive lift (top1 >= 0.50).

FOUR ARMS (each builds FRESH W / fresh concept state, no contamination):
  ARM_UNIGRAM                              -- analytic baseline
  ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY     -- n1_v3 readout + Hebbian-ish W_C
                                              (one-pass concept transitions).
                                              Reproduces n1_v3 ref top1 ~ 0.4455.
  ARM_LOGIT_MIXER_READOUT_CFRPE_PLASTICITY -- logit-mixer readout + cf-RPE
                                              word-W (N_STEPS=2000). Reproduces
                                              cf-RPE ref top1 ~ 0.2438.
  ARM_N1_V3_READOUT_CFRPE_PLASTICITY       -- n1_v3 readout + cf-RPE plasticity
                                              applied at concept-transition level
                                              (N_STEPS=2000). THE TEST ARM.

PRE-REG BANDS (top1 primary per META_HARNESS_RIGGED row 588):
  Sanity rails (Fix #28 verify-the-referent):
    ARM 2 top1 within +/- 0.03 of 0.4455 (n1_v3 provenance).
    ARM 3 top1 within +/- 0.03 of 0.2438 (cf-RPE provenance).
  ARM 4 verdict bands:
    HARD_PASS:          top1 >= 0.50 (super-additive)
    CHAIN_GRADE_BONUS:  top1 >= 0.55 AND cv < 0.05 (substantial new chain-grade)
    MIDDLE_BAND:        top1 in [0.46, 0.50] (additive not super-additive)
    HARD_FAIL:          top1 <= 0.45 (no super-additive; n1_v3 dominates)
  cv < 0.05 mandatory across seeds for all reported PASS configs.
  PROVENANCE_FAIL deflate: if EITHER ARM 2 or ARM 3 fails its sanity rail by
                          > 0.03, treat as DESIGN-ERROR not substrate evidence.

METHODOLOGY (matched to fair_harness + cf-RPE chain-grade):
  Encoder: word2vec-google-news-300 projected to N_DIM=8192 sparse-bipolar f=0.05.
  TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0].
  LAMBDA_GRID = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0] (excludes 0.0; META C7).
  cf-RPE: N_STEPS = 2000 (plateau per N_STEPS_curve audit).
  V_C = 256 (matches n1_v3 reference); f_sparse = 0.05 concept codes.
  SEEDS = [7, 17, 23].
  Zero LLM forward calls at inference (word2vec lookup at ingest only).

ASCII-only. Per-seed checkpoint. atexit synthesizer. GPU REQUIRED (torch.cuda).

Cites:
  preregs/2026-06-24_substrate_n1_v3_readout_x_cfrpe_plasticity_compose_v1.md
  experiments/exp_n1_concept_lm_substrate_native_token_decode_v3.py (n1_v3 source)
  experiments/exp_substrate_cfrpe_n_steps_curve_v1.py (cf-RPE source)
  experiments/exp_fair_harness_substrate_as_lm_v1.py (logit-mixer + joint sweep)
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py
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
from typing import Dict, List, Tuple, Optional

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Reference values for sanity / provenance rails
UNIGRAM_TOP1_REF = 0.2171
N1_V3_REF_TOP1 = 0.4455
CFRPE_REF_TOP1 = 0.2438
PROVENANCE_TOL = 0.03
ARM4_HARD_PASS_TOP1 = 0.50
ARM4_CHAIN_GRADE_TOP1 = 0.55
ARM4_MIDDLE_BAND_FLOOR = 0.46
ARM4_HARD_FAIL_TOP1 = 0.45
CV_MAX = 0.05

# Plasticity knobs (cf-RPE; matches cf-RPE N_STEPS_curve N=2000 plateau)
CFRPE_LR = 0.5
INGEST_BATCH = 64
N_STEPS_CFRPE = 2000

# Joint (T, lambda) sweep
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]   # excludes 0.0 per META C7
MRR_K = 10

# Encoder
SPARSE_BIPOLAR_F = 0.05

# n1_v3 readout knobs
V_C = 256                  # concept codebook size (matches n1_v3 reference)
CONCEPT_SPARSE_F = 0.05    # sparse concept code active fraction (k = round(f*N_DIM) per row)
LAM_BACKOFF = 0.1          # unigram back-off weight in n1_v3-style decode
LAPLACE_A = 0.5            # Laplace smoothing for D distribution

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

ARMS = [
    "ARM_UNIGRAM",
    "ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY",
    "ARM_LOGIT_MIXER_READOUT_CFRPE_PLASTICITY",
    "ARM_N1_V3_READOUT_CFRPE_PLASTICITY",
]
SUBSTRATE_ARMS = [a for a in ARMS if a != "ARM_UNIGRAM"]

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = N_STEPS_CFRPE
else:
    # Smoke: small but exercises EVERY path (4 arms, both readouts, cf-RPE iter,
    # joint sweep, provenance rail). Must stay under ~3min on laptop CPU.
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    V_C = 32
    N_STEPS = 80

CONFIG_VERSION = (
    "substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1; "
    "N_DIM=%d PRETRAIN_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d V_C=%d "
    "sparse_f=%.3f concept_f=%.3f N_STEPS=%d CFRPE_LR=%.3f INGEST_BATCH=%d "
    "arms=%s seeds=%s mode=%s temps=%s lambdas=%s MRR_K=%d device=%s; "
    "bands ARM4_HP_top1>=%.3f CG_top1>=%.3f MB_floor>=%.3f HF_top1<=%.3f "
    "cv_max=%.2f provenance_tol=%.3f"
) % (
    N_DIM, PRETRAIN_DIM, N_TRAIN, N_HELD, VOCAB_CAP, V_C,
    SPARSE_BIPOLAR_F, CONCEPT_SPARSE_F, N_STEPS, CFRPE_LR, INGEST_BATCH,
    ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID, MRR_K, str(DEVICE),
    ARM4_HARD_PASS_TOP1, ARM4_CHAIN_GRADE_TOP1, ARM4_MIDDLE_BAND_FLOOR,
    ARM4_HARD_FAIL_TOP1, CV_MAX, PROVENANCE_TOL,
)

_GENSIM_KV_CACHE: Dict[str, object] = {}

# Substrate-only invariant: count any unexpected LLM forward calls at inference.
_LLM_CALL_COUNTER = [0]


# ============================================================================
# Encoder (matches fair_harness exactly)
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
                         ) -> Tuple[torch.Tensor, np.ndarray, Dict]:
    """Build [V, n_dim] L2-normalized word2vec-projected vectors on GPU.

    Also returns the PRE-PROJECTION word2vec matrix (V, PRETRAIN_DIM) so the
    n1_v3-style readout can cluster on the original semantic space (the
    projected sparse-bipolar space is intentionally orthogonalized, which
    would confuse k-means).
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
            # Use char-trigram in pre-space too (for VQ)
            E_pre_n[i] = char_trigram_encode(vocab[i], kv.vector_size, seed)
    E_proj = _l2_normalize_np(E_proj)
    E_pre_n = _l2_normalize_np(E_pre_n)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_t, E_pre_n.astype(np.float32), meta


def build_E_char_trigram_gpu(vocab: List[str], n_dim: int, seed: int
                             ) -> Tuple[torch.Tensor, np.ndarray]:
    """Smoke / fallback when gensim unavailable.

    Returns (E_proj_gpu, E_pre_np) where E_pre is a smaller semantic surrogate
    used for VQ clustering in the n1_v3 readout.
    """
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_pre = np.stack(
        [char_trigram_encode(w, PRETRAIN_DIM, seed) for w in vocab], 0
    ).astype(np.float32)
    E_pre = _l2_normalize_np(E_pre)
    E_t = torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)
    return E_t, E_pre


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
# n1_v3 readout helpers: VQ + sparse codebook + Willshaw + decode-D
# ============================================================================

def sparse_codebook_np(vc: int, n: int, f: float, rng: np.random.Generator) -> np.ndarray:
    """Build sparse binary codebook (V_C, N_DIM), k = round(f * n) active per row.

    Same construction as n1_v3 source cell sparse_codebook(). Willshaw-style
    sparse codes; pairwise overlap k^2/n << k at f << 1.
    """
    k = max(1, round(f * n))
    C = np.zeros((vc, n), dtype=np.float32)
    for i in range(vc):
        idx = rng.choice(n, k, replace=False)
        C[i, idx] = 1.0
    return C


def fit_vq_on_words(E_pre: np.ndarray, V_C_local: int, seed: int) -> np.ndarray:
    """Cluster word embeddings into V_C concepts; return concept_id per word.

    E_pre: (V, PRETRAIN_DIM) L2-normalized word2vec (or char-trigram surrogate).
    Returns: (V,) int64 array of concept_ids.
    """
    try:
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=V_C_local, random_state=seed,
                             batch_size=4096, n_init=3, max_iter=100, verbose=0)
        km.fit(E_pre)
        return km.predict(E_pre).astype(np.int64)
    except ImportError:
        # numpy fallback (slower; ok for smoke / no-sklearn envs)
        rng = np.random.default_rng(seed)
        centers = E_pre[rng.choice(len(E_pre), size=V_C_local, replace=False)]
        # one-pass nearest centroid
        d = np.linalg.norm(
            E_pre[:, None, :] - centers[None, :, :], axis=-1
        )
        return np.argmin(d, axis=1).astype(np.int64)


def build_concept_W_hebbian_torch(
    C_t: torch.Tensor, concept_ids_train: np.ndarray, idx_train: np.ndarray,
    ingest_chunk: int
) -> torch.Tensor:
    """Build concept-level Willshaw W_C = sum P_src.T @ P_dst over train transitions.

    GPU-resident matmul (Fix #24). C_t: (V_C, N_DIM) sparse codebook on DEVICE.
    """
    n = idx_train.shape[0]
    dim = C_t.shape[1]
    if n < 2:
        return torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=DEVICE)
    src_words = idx_train[:-1]
    tgt_words = idx_train[1:]
    src_concepts = concept_ids_train[src_words]
    tgt_concepts = concept_ids_train[tgt_words]
    src_concepts_t = torch.from_numpy(src_concepts.astype(np.int64)).to(DEVICE)
    tgt_concepts_t = torch.from_numpy(tgt_concepts.astype(np.int64)).to(DEVICE)
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = len(src_concepts)
    for b in range(0, n_pairs, ingest_chunk):
        e = min(b + ingest_chunk, n_pairs)
        Ps = C_t[src_concepts_t[b:e]]    # (chunk, N_DIM)
        Pd = C_t[tgt_concepts_t[b:e]]    # (chunk, N_DIM)
        W.add_(Ps.T @ Pd)
        if DEVICE.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_concept_W_cfrpe_torch(
    C_t: torch.Tensor, concept_ids_train: np.ndarray, idx_train: np.ndarray,
    n_steps: int, batch: int, lr: float, gen: torch.Generator
) -> torch.Tensor:
    """Build concept-level W_C via cf-RPE iterative delta-rule on concept transitions.

    Update: error = C[c_t+1] - C[c_t] @ W^T ; dW = error.T @ C[c_t] / batch.
    """
    src_words = idx_train[:-1]
    tgt_words = idx_train[1:]
    n_pairs = len(src_words)
    if n_pairs < 1:
        dim = C_t.shape[1]
        return torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    src_concepts_np = concept_ids_train[src_words]
    tgt_concepts_np = concept_ids_train[tgt_words]
    src_concepts_t = torch.from_numpy(src_concepts_np).to(DEVICE)
    tgt_concepts_t = torch.from_numpy(tgt_concepts_np).to(DEVICE)
    dim = C_t.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = C_t[src_concepts_t[st]]    # (batch, N_DIM)
        Nxt = C_t[tgt_concepts_t[st]]    # (batch, N_DIM)
        error = Nxt - Ctx @ W.t()
        dW = (error.t() @ Ctx) / float(batch)
        W = W + lr * dW
    return W


def build_decode_D_torch(
    concept_ids_train: np.ndarray, idx_train: np.ndarray, C_t: torch.Tensor, V: int
) -> torch.Tensor:
    """Build decode memory D on GPU (Fix #24).

    D: (N_DIM, V) -- Hebbian accumulation D[:, word_j] = sum C[concept_t] over
       (concept_t, word_t = j) train occurrences. Vectorized via index_add_.
    """
    dim = C_t.shape[1]
    D = torch.zeros((dim, V), dtype=TORCH_DTYPE, device=DEVICE)
    # For each train token (concept_id, word_id), accumulate C[concept_id] -> D[:, word_id].
    # Vectorize: D.T (V, N_DIM) += scatter_add over (word_id) of C[concept_id].
    words_t = torch.from_numpy(idx_train.astype(np.int64)).to(DEVICE)
    concept_for_word = concept_ids_train  # (V,) static map word->concept_id
    concepts_t = torch.from_numpy(
        concept_for_word[idx_train].astype(np.int64)
    ).to(DEVICE)
    # codes_per_pos: (n_train, N_DIM) = C[concepts]; D.T.index_add_ accumulates each row
    # to D.T[word_t]. To keep memory bounded, chunk.
    D_T = torch.zeros((V, dim), dtype=TORCH_DTYPE, device=DEVICE)
    n = len(idx_train)
    chunk = 8192
    for b in range(0, n, chunk):
        e = min(b + chunk, n)
        codes = C_t[concepts_t[b:e]]                # (chunk, N_DIM)
        D_T.index_add_(0, words_t[b:e], codes)
    return D_T.T.contiguous()


def batched_concept_recall_t(W: torch.Tensor, Q: torch.Tensor, C: torch.Tensor) -> torch.Tensor:
    """Predict next concept_id batched.

    Q: (n, N_DIM) source concept codes.
    Returns: (n,) int64 predicted concept ids.
    """
    activated = Q @ W       # (n, N_DIM)
    sims = activated @ C.T  # (n, V_C)
    return torch.argmax(sims, dim=1).to(torch.int64)


def n1v3_logits_from_concept_codes_t(
    C_pred: torch.Tensor, D: torch.Tensor, uni_dist: torch.Tensor, lam: float
) -> torch.Tensor:
    """Calibrated log-prob over vocab per the n1_v3 decode pattern.

    C_pred: (n, N_DIM) predicted concept codes.
    D: (N_DIM, V) decode memory.
    uni_dist: (V,) unigram distribution for back-off.
    Returns logits = log( (1-lam) * softmax(C_pred @ D) + lam * uni_dist ).
    """
    scores = C_pred @ D                                  # (n, V)
    scores = scores - scores.max(dim=1, keepdim=True).values
    exp_s = torch.exp(scores)
    probs = exp_s / (exp_s.sum(dim=1, keepdim=True) + 1e-30)
    if lam > 0.0:
        probs = (1.0 - lam) * probs + lam * uni_dist.unsqueeze(0)
    return torch.log(probs + 1e-30)


# ============================================================================
# Logit-mixer readout (fair_harness style)
# ============================================================================

def build_rank1_W_gpu(idx_train: torch.Tensor, E: torch.Tensor,
                      ingest_chunk: int) -> torch.Tensor:
    """W = sum outer(E[idx[t+1]], E[idx[t]]); rank-1 Hebbian."""
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train[b:end]
        tgt_idx = idx_train[b + 1:end + 1]
        E_src = E[src_idx]
        E_tgt = E[tgt_idx]
        W.add_(E_tgt.T @ E_src)
        if DEVICE.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_W_cfrpe_word_torch(
    E: torch.Tensor, idx_train_t: torch.Tensor, n_steps: int, batch: int,
    lr: float, gen: torch.Generator
) -> torch.Tensor:
    """cf-RPE plasticity over word-level transitions; matches cf-RPE source cell."""
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
        dW = (error.t() @ Ctx) / float(batch)
        W = W + lr * dW
    return W


# ============================================================================
# Per-arm compute
# ============================================================================

def compute_arm_logits(
    arm: str, E_base: torch.Tensor, E_pre: np.ndarray, idx_train: np.ndarray,
    idx_held: np.ndarray, seed: int, n_steps: int, V: int
) -> Dict:
    """Build per-arm [n_held, V] logits + diagnostics. FRESH state per arm.

    Readout x plasticity matrix:
        ARM 2 (N1V3 + Hebbian):   n1_v3 readout (concept VQ + sparse codebook
                                  + Willshaw W_C Hebbian + decode-D).
        ARM 3 (LogitMixer + cfRPE): word-level W via cf-RPE iterative; logits
                                    = pred @ E.T.
        ARM 4 (N1V3 + cfRPE):     n1_v3 readout but W_C built via cf-RPE on
                                  concept transitions.
    """
    V_total = E_base.shape[0]
    dim = E_base.shape[1]

    # Always apply sparse-bipolar to the encoder (fair_harness convention)
    E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed * 10007 + ARMS.index(arm) * 31337)

    if arm == "ARM_LOGIT_MIXER_READOUT_CFRPE_PLASTICITY":
        t0 = time.time()
        W = build_W_cfrpe_word_torch(E_used, idx_train_t, n_steps=n_steps,
                                     batch=INGEST_BATCH, lr=CFRPE_LR, gen=gen)
        t_ingest = time.time() - t0

        # Recall: ctx -> pred = norm(ctx @ W^T); logits = pred @ E^T
        t0 = time.time()
        n_h = idx_held_t.shape[0]
        logits = torch.zeros((n_h, V_total), dtype=TORCH_DTYPE, device=DEVICE)
        for b in range(0, n_h, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_h)
            ctx = E_used[idx_held_t[b:end]]
            pred = _l2_normalize_t(ctx @ W.t())
            logits[b:end] = pred @ E_used.T
        if DEVICE.type == "cuda":
            torch.cuda.synchronize()
        t_recall = time.time() - t0

        logits_np = logits.detach().cpu().numpy().astype(np.float32)
        del W, logits, E_used
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "logits": logits_np,
            "readout": "logit_mixer",
            "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
        }

    # ----- n1_v3 readout arms (ARM 2 / ARM 4) -----
    t_total = time.time()

    # Step 1: VQ on word2vec pre-space -> concept_id per word (V,)
    t0 = time.time()
    concept_ids = fit_vq_on_words(E_pre, V_C, seed)
    t_vq = time.time() - t0
    n_unique_concepts = int(np.unique(concept_ids).size)
    utilization = n_unique_concepts / float(V_C)

    # Step 2: sparse concept codebook (V_C, N_DIM) k = round(f * N_DIM)
    rng = np.random.default_rng(seed + 1000)
    C_np = sparse_codebook_np(V_C, dim, CONCEPT_SPARSE_F, rng)
    C_t = torch.from_numpy(C_np).to(DEVICE)

    # Step 3: build concept-level W (Hebbian or cf-RPE) -- GPU resident
    t0 = time.time()
    if arm == "ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY":
        W_C_t = build_concept_W_hebbian_torch(
            C_t, concept_ids, idx_train, INGEST_CHUNK,
        )
    else:
        # ARM_N1_V3_READOUT_CFRPE_PLASTICITY
        W_C_t = build_concept_W_cfrpe_torch(
            C_t, concept_ids, idx_train,
            n_steps=n_steps, batch=INGEST_BATCH, lr=CFRPE_LR, gen=gen,
        )
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_ingest_w = time.time() - t0

    # Step 4: decode memory D -- GPU resident (Fix #24)
    t0 = time.time()
    D_t = build_decode_D_torch(concept_ids, idx_train, C_t, V_total)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_decode = time.time() - t0

    # Step 5: predict next concept code for held positions
    t0 = time.time()
    # Map held words -> source concept_id -> source concept code
    held_src_concepts = concept_ids[idx_held]
    held_src_concepts_t = torch.from_numpy(held_src_concepts).to(DEVICE)
    Q_t = C_t[held_src_concepts_t]              # (n_held, N_DIM)
    # activated = Q @ W_C; L2-normalize per row so the subsequent D matmul
    # yields bounded logits in [-1, 1] range (cosine-similarity-style).
    # Without this, the joint (T, lambda) sweep underflows at T < 0.1 because
    # raw activated @ D values scale with sum-of-train-occurrences (~thousands).
    activated_held = Q_t @ W_C_t                # (n_held, N_DIM)
    activated_held = _l2_normalize_t(activated_held)
    # Also L2-normalize D columns (per-vocab) so logits = activated @ D_norm
    # are cosine-similarity values between predicted concept-vector and per-
    # vocab decode column. This makes the (T, lambda) sweep meaningful across
    # arms (logit_mixer + n1_v3 both produce cosine-like logits).
    D_norm = D_t / (D_t.norm(dim=0, keepdim=True) + 1e-12)

    n_h = activated_held.shape[0]
    logits = torch.zeros((n_h, V_total), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        logits[b:end] = activated_held[b:end] @ D_norm
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    del W_C_t, D_t, D_norm, C_t, activated_held, Q_t, held_src_concepts_t, logits, E_used
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "readout": "n1_v3",
        "vq_utilization": float(round(utilization, 4)),
        "n_unique_concepts": int(n_unique_concepts),
        "wall_vq_s": round(t_vq, 2),
        "wall_ingest_s": round(t_ingest_w, 2),
        "wall_decode_s": round(t_decode, 2),
        "wall_recall_s": round(t_recall, 2),
        "wall_total_s": round(time.time() - t_total, 2),
    }


# ============================================================================
# text8 corpus utilities (same as fair_harness)
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
    """Joint (T, lambda) sweep on dev; pick best per-metric; report on test."""
    probs_T1 = softmax_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)
    raw_top1_at_T1_L1 = top1_acc(logp_T1, nxt_test)

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
        "raw_top1_at_T1_L1": round(raw_top1_at_T1_L1, 4),
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
# Instrumentation self-test
# ============================================================================

def _selftest():
    """Mandatory self-test: assert all claimed metrics + mechanisms operational."""
    print("[selftest] running self-test...", flush=True)

    # T1: sparse codebook
    rng = np.random.default_rng(0)
    C = sparse_codebook_np(8, 100, 0.05, rng)
    k_expect = max(1, round(0.05 * 100))
    nnz_per_row = (C != 0).sum(axis=1).tolist()
    assert all(n == k_expect for n in nnz_per_row), "T1 sparse nnz: %s" % nnz_per_row

    # T2: char-trigram bipolar
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,) and set(np.unique(v).tolist()).issubset({-1.0, 1.0})

    # T3: sparsify_bipolar_gpu primitive
    E_t = torch.randn(4, 100, generator=torch.Generator().manual_seed(0))
    sp = sparsify_bipolar_gpu(E_t, 0.05, seed=0)
    nnz = (sp != 0).sum(dim=1).tolist()
    assert all(n == k_expect for n in nnz), "T3 sparse nnz: %s" % nnz

    # T4: concept-Hebbian W_C identity on synthetic data (torch GPU/CPU)
    # 5 words map to 4 concepts; one-pass Hebbian recall of (c0 -> non-c0).
    n_dim = 64
    vc = 4
    C_test = sparse_codebook_np(vc, n_dim, 0.10, rng)
    C_t_test = torch.from_numpy(C_test).to(DEVICE)
    concept_ids = np.array([0, 1, 2, 3, 0], dtype=np.int64)   # 5 words
    idx_train = np.array([0, 1, 0, 2, 0, 3, 0, 1, 0, 2], dtype=np.int64)
    W_C_t = build_concept_W_hebbian_torch(C_t_test, concept_ids, idx_train, 128)
    assert W_C_t.shape == (n_dim, n_dim), "T4 W_C shape: %s" % str(W_C_t.shape)
    # Probe: source = c0 (word 0); activated = C[0] @ W_C; argmax over C @ activated
    # should NOT be c0 (c0 always transitions to non-c0 in our test).
    W_C_np = W_C_t.detach().cpu().numpy()
    activated = C_test[0] @ W_C_np
    sims = C_test @ activated
    pred = int(np.argmax(sims))
    assert pred != 0, "T4 W_C predicted c0 -> c0 (no transition learned): pred=%d" % pred

    # T5: decode-D Hebbian accumulates correctly (torch)
    D_t = build_decode_D_torch(concept_ids, idx_train, C_t_test, V=5)
    D = D_t.detach().cpu().numpy()
    # word 0 appears 5 times with c0; D[:, 0] should have weight 5 * C[0]
    expected = 5.0 * C_test[0]
    assert np.allclose(D[:, 0], expected, atol=1e-5), (
        "T5 D[:, 0] not 5*C[0]: max diff %.3f" % float(np.abs(D[:, 0] - expected).max())
    )

    # T6: cf-RPE concept W reduces fixed-point error (no NaN; non-trivial output)
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    W_cfrpe = build_concept_W_cfrpe_torch(
        C_t_test, concept_ids, idx_train, n_steps=50, batch=8, lr=0.5, gen=gen,
    )
    assert torch.all(torch.isfinite(W_cfrpe)), "T6 cf-RPE W has NaN/Inf"
    assert W_cfrpe.abs().max().item() > 1e-6, "T6 cf-RPE W is all zeros"

    # T7: joint_sweep operational on synthetic; lambda=1.0 reproduces raw substrate
    sub_logits = np.random.default_rng(42).standard_normal((20, 5)).astype(np.float32)
    U = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
    U_log = np.log(np.clip(U, 1e-30, 1.0))
    nxt = np.tile(np.array([0, 1, 2, 3, 4]), 4)
    res = joint_sweep(sub_logits[:10], sub_logits[10:], U_log, nxt[:10], nxt[10:],
                       [0.1, 0.5, 1.0], [0.5, 1.0], 3)
    assert math.isfinite(res["bpc_best"]) and 0.0 <= res["top1_acc"] <= 1.0, (
        "T7 joint sweep returned bad values: %s" % res
    )
    assert res["best_lambda_for_bpc"] in [0.5, 1.0], "T7 lambda not in grid: %s" % res

    # T8: top1 + bpc + mrr math sanity
    n_t = 5
    V_t = 10
    nxt_t = np.array([3, 0, 9, 5, 2])
    logp_planted = np.full((n_t, V_t), -10.0, dtype=np.float64)
    # plant true class at top: rank=1 -> 1/1=1.0
    for i, true_cls in enumerate(nxt_t):
        logp_planted[i, true_cls] = 0.0
    assert abs(top1_acc(logp_planted, nxt_t) - 1.0) < 1e-9, "T8 top1 perfect"
    assert abs(mrr_at_k(logp_planted, nxt_t, 10) - 1.0) < 1e-9, "T8 MRR perfect"

    # T9: substrate-only-decode invariant initially zero
    assert _LLM_CALL_COUNTER[0] == 0, "T9 LLM counter must start at 0"

    print(
        "[selftest] PASS: T1 sparse-codebook + T2 trigram + T3 sparsify-bipolar "
        "+ T4 W_C-Hebbian + T5 decode-D + T6 W_C-cfRPE + T7 joint-sweep "
        "+ T8 top1/MRR planted + T9 llm=0",
        flush=True,
    )


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
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d V_C=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, V_C, str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)
    U_t = torch.from_numpy(U.astype(np.float32)).to(DEVICE)  # for n1_v3 backoff

    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"],
        uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    print("\n[seed=%d] building word2vec base E (V=%d, N_DIM=%d) on %s..." % (
        seed, V, N_DIM, str(DEVICE)), flush=True)
    t_enc0 = time.time()
    encoder_meta = {}
    try:
        E_base, E_pre, encoder_meta = build_E_word2vec_gpu(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d encoder] WORD2VEC LOAD FAIL: %s -- falling back to char-trigram" % (
            seed, err), flush=True)
        E_base, E_pre = build_E_char_trigram_gpu(vocab, N_DIM, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    t_enc = time.time() - t_enc0
    print("[seed=%d encoder] built in %.1fs" % (seed, t_enc), flush=True)

    # Split held into dev + test halves
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        for arm in SUBSTRATE_ARMS:
            by_arm[arm] = {"empty_eval": True}
        return {"seed": seed, "by_arm": by_arm, "V": V, "N": N_DIM,
                "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "VOCAB_CAP": VOCAB_CAP, "PRETRAIN_DIM": PRETRAIN_DIM,
                "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
                "elapsed_s_seed": round(time.time() - t_seed, 2),
                "device": str(DEVICE), "encoder_meta": encoder_meta,
                "n_llm_calls": 0}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    for arm in SUBSTRATE_ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building logits..." % (seed, arm), flush=True)
        try:
            ar = compute_arm_logits(arm, E_base, E_pre, idx_train, idx_held,
                                    seed, N_STEPS, V)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            import traceback
            traceback.print_exc()
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"),
                "best_T_for_bpc": float("nan"),
                "best_lambda_for_bpc": float("nan"),
                "raw_bpc_at_T1_L1": float("inf"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
            }
            continue

        logits_full = ar["logits"]
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            logits_ctx = logits_full
        logits_eval = logits_ctx[mask[:logits_ctx.shape[0]]] if logits_ctx.shape[0] < len(mask) else logits_ctx[mask]
        n_eval_arm = logits_eval.shape[0]
        n_dev_arm = min(n_dev, n_eval_arm // 2)
        # Align dev/test with logits availability
        nxt_dev_arm = nxt_eval[:n_dev_arm]
        nxt_test_arm = nxt_eval[n_dev_arm:n_eval_arm]
        jr = joint_sweep(
            logits_eval[:n_dev_arm], logits_eval[n_dev_arm:n_eval_arm],
            U_log, nxt_dev_arm, nxt_test_arm,
            TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        for diag_key in ("readout", "vq_utilization", "n_unique_concepts",
                          "wall_vq_s", "wall_ingest_s", "wall_decode_s",
                          "wall_recall_s", "wall_total_s"):
            if diag_key in ar:
                jr[diag_key] = ar[diag_key]
        by_arm[arm] = jr
        print(
            "    [seed=%d arm=%s] readout=%s bpc=%.3f top1=%.4f mrr=%.4f "
            "(bestT=%.4f bestL=%.2f) elapsed=%.1fs"
            % (
                seed, arm, ar.get("readout", "?"), jr["bpc_best"], jr["top1_acc"],
                jr["mrr_at_10"], jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                jr["elapsed_s_arm"],
            ),
            flush=True,
        )

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
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "V_C": V_C,
        "N_STEPS": N_STEPS,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "n_llm_calls": 0,
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})

    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    uni_top1 = [u["by_arm"].get("ARM_UNIGRAM", {}).get("top1_unigram", float("nan")) for u in units]
    uni_mrr = [u["by_arm"].get("ARM_UNIGRAM", {}).get("mrr_unigram", float("nan")) for u in units]
    unigram_agg = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "top1_mean": round(float(np.mean(uni_top1)), 4),
        "top1_std": round(float(np.std(uni_top1)), 4),
        "mrr_mean": round(float(np.mean(uni_mrr)), 4),
    }

    by_arm_agg: Dict[str, Dict] = {"ARM_UNIGRAM": unigram_agg}

    for arm in SUBSTRATE_ARMS:
        seeds_compute_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid_units = [u for cf, u in zip(seeds_compute_failed, units) if not cf]
        n_compute_failed = int(sum(seeds_compute_failed))
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"),
                "top1_acc_mean": float("nan"),
                "mrr_at_10_mean": float("nan"),
                "n_valid_seeds": 0,
                "n_compute_failed": n_compute_failed,
                "all_seeds_failed": True,
            }
            continue
        bpc_vals = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_vals = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_vals = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        b_mean = float(np.mean(bpc_vals))
        t_mean = float(np.mean(top1_vals))
        t_std = float(np.std(top1_vals))
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(float(np.std(bpc_vals)), 4),
            "bpc_best_cv": round(
                float(np.std(bpc_vals)) / max(abs(b_mean), 1e-6), 4
            ),
            "top1_acc_mean": round(t_mean, 4),
            "top1_acc_std": round(t_std, 4),
            "top1_acc_cv": round(t_std / max(abs(t_mean), 1e-6), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_vals)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_vals)), 4),
            "n_valid_seeds": int(len(valid_units)),
            "n_compute_failed": n_compute_failed,
            "all_seeds_failed": False,
        }

    # Provenance rails (Fix #28)
    arm2 = by_arm_agg.get("ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY", {})
    arm3 = by_arm_agg.get("ARM_LOGIT_MIXER_READOUT_CFRPE_PLASTICITY", {})
    arm4 = by_arm_agg.get("ARM_N1_V3_READOUT_CFRPE_PLASTICITY", {})

    arm2_top1 = arm2.get("top1_acc_mean", float("nan"))
    arm3_top1 = arm3.get("top1_acc_mean", float("nan"))
    arm4_top1 = arm4.get("top1_acc_mean", float("nan"))
    arm4_top1_cv = arm4.get("top1_acc_cv", float("nan"))

    provenance_arm2_ok = (
        math.isfinite(arm2_top1)
        and abs(arm2_top1 - N1_V3_REF_TOP1) <= PROVENANCE_TOL
    )
    provenance_arm3_ok = (
        math.isfinite(arm3_top1)
        and abs(arm3_top1 - CFRPE_REF_TOP1) <= PROVENANCE_TOL
    )
    provenance_check_passes = provenance_arm2_ok and provenance_arm3_ok

    arm_lines = []
    for a in SUBSTRATE_ARMS:
        x = by_arm_agg[a]
        if x.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % a)
            continue
        arm_lines.append(
            "%s=top1%.4f|bpc%.3f|mrr%.4f|cv%.3f"
            % (a, x["top1_acc_mean"], x["bpc_best_mean"], x["mrr_at_10_mean"],
               x.get("top1_acc_cv", 0.0))
        )
    base_summary = "uni=top1%.4f|bpc%.3f | %s" % (
        unigram_agg["top1_mean"], unigram_agg["bpc_mean"], " | ".join(arm_lines)
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "provenance_arm2_top1": float(arm2_top1) if math.isfinite(arm2_top1) else None,
        "provenance_arm2_ref": N1_V3_REF_TOP1,
        "provenance_arm2_ok": bool(provenance_arm2_ok),
        "provenance_arm3_top1": float(arm3_top1) if math.isfinite(arm3_top1) else None,
        "provenance_arm3_ref": CFRPE_REF_TOP1,
        "provenance_arm3_ok": bool(provenance_arm3_ok),
        "provenance_check_passes": bool(provenance_check_passes),
        "provenance_tolerance": PROVENANCE_TOL,
        "arm4_test_top1": float(arm4_top1) if math.isfinite(arm4_top1) else None,
        "arm4_test_top1_cv": float(arm4_top1_cv) if math.isfinite(arm4_top1_cv) else None,
        "arm4_hard_pass_floor": ARM4_HARD_PASS_TOP1,
        "arm4_chain_grade_floor": ARM4_CHAIN_GRADE_TOP1,
        "arm4_middle_band_floor": ARM4_MIDDLE_BAND_FLOOR,
        "arm4_hard_fail_ceiling": ARM4_HARD_FAIL_TOP1,
        "cv_max": CV_MAX,
        "n_seeds": len(units),
        "honest_scope": (
            "n1_v3 readout x cf-RPE plasticity compose test at production scale "
            "(N_DIM=8192 N_TRAIN=100k text8 V=4000 V_C=256 N_STEPS=2000). top1 is "
            "the load-bearing metric per META_HARNESS_RIGGED row 588. ARM 4 "
            "(N1_V3_READOUT x CFRPE_PLASTICITY) is the test arm. Sanity rails: "
            "ARM 2 must reproduce n1_v3 ref (top1~0.4455 +/- %.3f); ARM 3 must "
            "reproduce cf-RPE ref (top1~0.2438 +/- %.3f). Verdict on ARM 4 only."
        ) % (PROVENANCE_TOL, PROVENANCE_TOL),
        "cites": [
            "preregs/2026-06-24_substrate_n1_v3_readout_x_cfrpe_plasticity_compose_v1.md",
            "data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json",
            "data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
            "experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py",
            "Skunkworks_VET_2026-06-23_chain_grade_bottleneck_is_readout",
            "USER_2026-06-23_META_HARNESS_RIGGED_row_588_top1_load_bearing",
        ],
    }

    # PROVENANCE_FAIL: if components don't reproduce, the composition is undefined.
    if not provenance_check_passes:
        prov_msg = []
        if not provenance_arm2_ok:
            prov_msg.append(
                "ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY top1=%.4f off n1_v3 ref %.4f by %.4f > %.3f tol"
                % (arm2_top1, N1_V3_REF_TOP1,
                   abs(arm2_top1 - N1_V3_REF_TOP1) if math.isfinite(arm2_top1) else float("nan"),
                   PROVENANCE_TOL)
            )
        if not provenance_arm3_ok:
            prov_msg.append(
                "ARM_LOGIT_MIXER_READOUT_CFRPE_PLASTICITY top1=%.4f off cf-RPE ref %.4f by %.4f > %.3f tol"
                % (arm3_top1, CFRPE_REF_TOP1,
                   abs(arm3_top1 - CFRPE_REF_TOP1) if math.isfinite(arm3_top1) else float("nan"),
                   PROVENANCE_TOL)
            )
        return (
            "PROVENANCE_FAIL",
            "PROVENANCE_FAIL (design-error): composition components do not reproduce "
            "references; composition verdict is undefined. %s. %s"
            % ("; ".join(prov_msg), base_summary),
            detail,
        )

    if arm4.get("all_seeds_failed", False):
        return (
            "HARD_FAIL",
            "HARD_FAIL: ARM_N1_V3_READOUT_CFRPE_PLASTICITY all seeds compute_failed. " + base_summary,
            detail,
        )

    if not math.isfinite(arm4_top1):
        return (
            "HARD_FAIL",
            "HARD_FAIL: ARM_N1_V3_READOUT_CFRPE_PLASTICITY top1 not finite. " + base_summary,
            detail,
        )

    cv_ok = math.isfinite(arm4_top1_cv) and arm4_top1_cv <= CV_MAX

    # CHAIN_GRADE_BONUS: top1 >= 0.55 AND cv ok
    if arm4_top1 >= ARM4_CHAIN_GRADE_TOP1 and cv_ok:
        return (
            "HARD_PASS",
            "HARD_PASS_CHAIN_GRADE_BONUS: ARM 4 top1=%.4f >= %.3f chain-grade floor AND cv=%.3f <= %.2f. "
            "Substantial new chain-grade evidence: n1_v3 readout x cf-RPE plasticity composes super-additively. "
            % (arm4_top1, ARM4_CHAIN_GRADE_TOP1, arm4_top1_cv, CV_MAX) + base_summary,
            detail,
        )

    # HARD_PASS: top1 >= 0.50
    if arm4_top1 >= ARM4_HARD_PASS_TOP1:
        cv_note = "" if cv_ok else " (NOTE cv=%.3f > %.2f; HARD_PASS but seed-unstable)" % (arm4_top1_cv, CV_MAX)
        return (
            "HARD_PASS",
            "HARD_PASS: ARM 4 top1=%.4f >= %.3f hard-pass floor. Super-additive composition confirmed.%s "
            % (arm4_top1, ARM4_HARD_PASS_TOP1, cv_note) + base_summary,
            detail,
        )

    # MIDDLE_BAND: top1 in [0.46, 0.50]
    if arm4_top1 >= ARM4_MIDDLE_BAND_FLOOR:
        return (
            "MIDDLE_BAND",
            "MIDDLE_BAND: ARM 4 top1=%.4f in [%.3f, %.3f). Additive but not super-additive; "
            "n1_v3 readout dominates compose direction. " % (
                arm4_top1, ARM4_MIDDLE_BAND_FLOOR, ARM4_HARD_PASS_TOP1
            ) + base_summary,
            detail,
        )

    # HARD_FAIL: top1 <= 0.45 (no super-additive lift)
    return (
        "HARD_FAIL",
        "HARD_FAIL: ARM 4 top1=%.4f <= %.3f. No super-additive composition; n1_v3 readout "
        "dominates regardless of plasticity rule -- the readout is the only load-bearing knob. "
        % (arm4_top1, ARM4_HARD_FAIL_TOP1) + base_summary,
        detail,
    )


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
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict == "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "N": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "V_C": V_C,
            "N_STEPS": N_STEPS,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_" + ANCHOR_NAME,
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (
                len(units), len(SEEDS), msg[:200]),
            "_synthesized_by_atexit": True,
            "config_version": CONFIG_VERSION,
            "device": str(DEVICE),
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
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

    print("[config] %s mode=%s N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d V_C=%d "
          "N_STEPS=%d seeds=%s arms=%s | name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, V_C,
              N_STEPS, SEEDS, ARMS, _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[gpu] device=%s name=%s total_mem_gb=%.2f" % (
                DEVICE, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception as e:
            print("[gpu] info-fetch failed: %s" % e, flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    _T0_REF[0] = time.time()
    atexit.register(_synthesize_on_exit)

    units: List[Dict] = []
    # Per-seed sequential (encoder hoisted inside run_unit; cache survives via _GENSIM_KV_CACHE)
    for seed in SEEDS:
        partial_key = "s%d" % seed
        partial_path = out_dir / ("partial_metrics_%s.json" % partial_key)
        if partial_path.exists() and RUN_MODE == "full":
            try:
                import json as _json
                with open(partial_path, "r", encoding="utf-8") as f:
                    prior = _json.load(f)
                if prior.get("config_version") == CONFIG_VERSION:
                    print("[seed=%d] reusing prior partial" % seed, flush=True)
                    units.append(prior)
                    continue
            except Exception:
                pass
        try:
            unit = run_unit(seed)
            units.append(unit)
            write_partial(out_dir, partial_key, unit)
            print("\n[seed=%d] DONE in %.1fs" % (seed, unit["elapsed_s_seed"]), flush=True)
        except Exception as e:
            import traceback
            traceback.print_exc()
            print("\n[seed=%d] FAIL: %s" % (seed, e), flush=True)

    if not units:
        print("[main] NO seeds completed; writing empty verdict", flush=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "anchor": ANCHOR_NAME,
            "verdict": "HARD_FAIL",
            "verdict_msg": "HARD_FAIL: no seeds completed",
            "run_mode": RUN_MODE,
            "n_seeds": 0,
            "n_seeds_expected": len(SEEDS),
            "config_version": CONFIG_VERSION,
            "elapsed_s": time.time() - _T0_REF[0],
            "summary": "no seeds",
            "per_unit": [],
            "device": str(DEVICE),
        }
        write_metrics(out_dir, metrics, [])
        _METRICS_WRITTEN[0] = True
        raise SystemExit(1)

    verdict, msg, detail = compute_verdict(units)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg[:400],
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "N": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "V_C": V_C,
        "N_STEPS": N_STEPS,
        "SEEDS": SEEDS,
        "ARMS": ARMS,
        "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "CONCEPT_SPARSE_F": CONCEPT_SPARSE_F,
        "CFRPE_LR": CFRPE_LR,
        "INGEST_BATCH": INGEST_BATCH,
        "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID,
        "MRR_K": MRR_K,
        "detail": detail,
        "per_unit": units,
        "per_seed": units,
        "n_seeds": len(units),
        "n_seeds_expected": len(SEEDS),
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "elapsed_s": time.time() - _T0_REF[0],
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("\n[main] VERDICT=%s" % verdict, flush=True)
    print("[main] MSG=%s" % msg, flush=True)
    print("[main] wrote metrics to %s" % out_dir, flush=True)
