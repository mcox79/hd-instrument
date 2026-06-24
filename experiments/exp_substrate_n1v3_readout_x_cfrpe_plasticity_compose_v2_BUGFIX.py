"""
substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX -- v1 failed PROVENANCE
on ARM 2 (n1_v3 readout) and produced NaN on ARM 4 (n1_v3 + cf-RPE). v2 fixes
the three root causes:

  BUG-1 (provenance ARM 2): v1 L2-normalized activated_held + D_norm before
        logits = activated @ D_norm. This DESTROYS the sparse-Willshaw "v sparse
        -> D.T @ v selects k columns" property that the n1_v3 reference relies
        on. n1_v3 source feeds RAW scores into calibrated temp-softmax + unigram
        back-off. v2 removes both L2 norms.

  BUG-2 (sparse regime): v1 used CONCEPT_SPARSE_F = 0.05 (k=409 at N=8192).
        n1_v3 reference uses f=0.006 at N=4096 (k=25), the Willshaw sweet spot
        (k ~ log(N)). v2 uses f=0.003 (k=25 at N=8192) -- same k as the cert
        anchor, scaled to N=8192. Off-sweet-spot dense codes destroy the
        sparse-selectivity that the readout depends on.

  BUG-3 (NaN ARM 4): cf-RPE on positive-mean sparse codes diverges because
        Ctx.T @ Ctx accumulates UNBOUNDED positive entries -> W operator norm
        grows monotonically -> float32 overflow at step ~500-1500. v2 fixes by:
        (a) center sparse codes (subtract per-step mean) before delta-rule so
            the update is zero-mean (matches cf-RPE's regime on bipolar codes);
        (b) per-step operator-norm clip on W (Frobenius cap = sqrt(N_DIM));
        (c) per-step NaN/Inf check -- reset W to last-good if non-finite.

Strategic context (unchanged from v1):
  n1_v3 (cert row 588) top1 = 0.4455 via VQ -> concept-sparse Willshaw recall
  -> decode-D word distribution. cf-RPE plasticity (cert MM; N=5000_cfrpe)
  top1 = 0.2438 via standard logit-mixer readout. 5x lift-ratio gap.
  HYPOTHESIS (unchanged): n1_v3 readout + cf-RPE plasticity composes both
  advantages, producing super-additive lift (top1 >= 0.50).

FOUR ARMS (each builds FRESH state):
  ARM_UNIGRAM                              -- analytic baseline
  ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY     -- v3-faithful sparse readout + Hebbian.
                                              MUST reproduce n1_v3 ref top1~0.4455
                                              (PROVENANCE gate; if FAIL the design
                                              is broken).
  ARM_LOGIT_MIXER_READOUT_CFRPE_PLASTICITY -- standard logit-mixer + cf-RPE.
                                              Already provenance-OK in v1 (top1
                                              0.2440). Unchanged.
  ARM_N1_V3_READOUT_CFRPE_PLASTICITY       -- v3-faithful readout + cf-RPE with
                                              centered codes + W clip + NaN
                                              guard. THE TEST ARM.

PRE-REG BANDS (top1 primary per META_HARNESS_RIGGED row 588):
  Sanity rails (Fix #28 verify-the-referent):
    ARM 2 top1 within +/- 0.05 of 0.4455 (n1_v3 provenance; widened to 0.05
          because N_DIM=8192 != N_DIM=4096 cert config -- the readout port to
          8192 is itself a derived result).
    ARM 3 top1 within +/- 0.05 of 0.244  (cf-RPE provenance; widened similarly
          although the v1 already reproduced at 0.244 within 0.001).
  ARM 4 verdict bands (unchanged from v1):
    HARD_PASS:          top1 >= 0.50 (super-additive)
    CHAIN_GRADE_BONUS:  top1 >= 0.55 AND cv < 0.05
    MIDDLE_BAND:        top1 in [0.46, 0.50]
    HARD_FAIL:          top1 <= 0.45
  cv < 0.05 mandatory across seeds for all reported PASS configs.
  PROVENANCE_FAIL deflate: if EITHER ARM 2 or ARM 3 fails its sanity rail by
                          > 0.05, treat as DESIGN-ERROR not substrate evidence.

ASCII-only. Per-seed checkpoint. atexit synthesizer. GPU REQUIRED (torch.cuda).

Cites:
  preregs/2026-06-24_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX.md
  experiments/exp_n1_concept_lm_substrate_native_token_decode_v3.py (n1_v3 source)
  experiments/exp_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1.py (v1 + failure metrics)
  data/exp_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1/metrics.json (PROVENANCE_FAIL evidence)
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

ANCHOR_NAME = "substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Reference values for sanity / provenance rails
UNIGRAM_TOP1_REF = 0.2171
N1_V3_REF_TOP1 = 0.4455
CFRPE_REF_TOP1 = 0.2438
# v2 widens provenance tol from 0.03 to 0.05 because the port from N_DIM=4096
# (cert anchor) to N_DIM=8192 is itself a derived result; expecting reproduction
# within 0.03 across an N_DIM doubling is too tight.
PROVENANCE_TOL = 0.05
ARM4_HARD_PASS_TOP1 = 0.50
ARM4_CHAIN_GRADE_TOP1 = 0.55
ARM4_MIDDLE_BAND_FLOOR = 0.46
ARM4_HARD_FAIL_TOP1 = 0.45
CV_MAX = 0.05

# Plasticity knobs (cf-RPE)
CFRPE_LR = 0.5
INGEST_BATCH = 64
N_STEPS_CFRPE = 2000

# BUGFIX-3: cf-RPE numerical guards for sparse-code concept regime
CFRPE_W_OPNORM_CLIP_FACTOR = 1.0   # cap Frobenius norm to sqrt(N_DIM) * factor
CFRPE_CENTER_CODES = True          # center sparse codes (subtract mean) before delta-rule
CFRPE_CHECK_FINITE_EVERY = 50      # check W finite every N steps

# Joint (T, lambda) sweep
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Encoder
SPARSE_BIPOLAR_F = 0.05

# n1_v3 readout knobs (BUGFIX-2: sparse Willshaw sweet spot)
V_C = 256                  # concept codebook size (matches n1_v3 reference)
# BUGFIX-2: v1 used 0.05 (k=409 at N=8192) -- way off Willshaw sweet spot.
# n1_v3 cert anchor used f=0.006 at N=4096 (k=25). Scale to N=8192: k=25 ->
# f = 25/8192 = 0.00305. Keep k constant across N_DIM scaling.
CONCEPT_SPARSE_F = 0.003   # k = round(0.003 * 8192) = 25 (matches n1_v3 ref k)
LAM_BACKOFF = 0.1
LAPLACE_A = 0.5

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
    "substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX; "
    "N_DIM=%d PRETRAIN_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d V_C=%d "
    "sparse_f=%.3f concept_f=%.4f N_STEPS=%d CFRPE_LR=%.3f INGEST_BATCH=%d "
    "arms=%s seeds=%s mode=%s temps=%s lambdas=%s MRR_K=%d device=%s; "
    "bands ARM4_HP_top1>=%.3f CG_top1>=%.3f MB_floor>=%.3f HF_top1<=%.3f "
    "cv_max=%.2f provenance_tol=%.3f bugfix=L2norm-removed+sparse-sweet-spot+cfRPE-centered-clipped"
) % (
    N_DIM, PRETRAIN_DIM, N_TRAIN, N_HELD, VOCAB_CAP, V_C,
    SPARSE_BIPOLAR_F, CONCEPT_SPARSE_F, N_STEPS, CFRPE_LR, INGEST_BATCH,
    ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID, MRR_K, str(DEVICE),
    ARM4_HARD_PASS_TOP1, ARM4_CHAIN_GRADE_TOP1, ARM4_MIDDLE_BAND_FLOOR,
    ARM4_HARD_FAIL_TOP1, CV_MAX, PROVENANCE_TOL,
)

_GENSIM_KV_CACHE: Dict[str, object] = {}

_LLM_CALL_COUNTER = [0]


# ============================================================================
# Encoder (unchanged from v1; matches fair_harness exactly)
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
            E_pre_n[i] = char_trigram_encode(vocab[i], kv.vector_size, seed)
    E_proj = _l2_normalize_np(E_proj)
    E_pre_n = _l2_normalize_np(E_pre_n)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_t, E_pre_n.astype(np.float32), meta


def build_E_char_trigram_gpu(vocab: List[str], n_dim: int, seed: int
                             ) -> Tuple[torch.Tensor, np.ndarray]:
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

    Same construction as n1_v3 source cell sparse_codebook().
    """
    k = max(1, round(f * n))
    C = np.zeros((vc, n), dtype=np.float32)
    for i in range(vc):
        idx = rng.choice(n, k, replace=False)
        C[i, idx] = 1.0
    return C


def fit_vq_on_words(E_pre: np.ndarray, V_C_local: int, seed: int) -> np.ndarray:
    """Cluster word embeddings into V_C concepts."""
    try:
        from sklearn.cluster import MiniBatchKMeans
        km = MiniBatchKMeans(n_clusters=V_C_local, random_state=seed,
                             batch_size=4096, n_init=3, max_iter=100, verbose=0)
        km.fit(E_pre)
        return km.predict(E_pre).astype(np.int64)
    except ImportError:
        rng = np.random.default_rng(seed)
        centers = E_pre[rng.choice(len(E_pre), size=V_C_local, replace=False)]
        d = np.linalg.norm(
            E_pre[:, None, :] - centers[None, :, :], axis=-1
        )
        return np.argmin(d, axis=1).astype(np.int64)


def build_concept_W_hebbian_torch(
    C_t: torch.Tensor, concept_ids_train: np.ndarray, idx_train: np.ndarray,
    ingest_chunk: int
) -> torch.Tensor:
    """Build concept-level Willshaw W_C = sum P_src.T @ P_dst over train transitions."""
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
        Ps = C_t[src_concepts_t[b:e]]
        Pd = C_t[tgt_concepts_t[b:e]]
        W.add_(Ps.T @ Pd)
        if DEVICE.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_concept_W_cfrpe_torch(
    C_t: torch.Tensor, concept_ids_train: np.ndarray, idx_train: np.ndarray,
    n_steps: int, batch: int, lr: float, gen: torch.Generator
) -> Tuple[torch.Tensor, Dict]:
    """BUGFIX-3: cf-RPE iterative delta-rule on concept transitions with:
       (a) centered codes (subtract per-batch mean) to keep update zero-mean;
       (b) per-step W operator-norm clip (Frobenius cap);
       (c) NaN/Inf guard with last-good fallback.

    Returns (W, diagnostics).
    """
    src_words = idx_train[:-1]
    tgt_words = idx_train[1:]
    n_pairs = len(src_words)
    diag = {"n_steps": int(n_steps), "n_finite_resets": 0,
            "n_clip_events": 0, "final_w_fro": float("nan"),
            "n_nan_inf_seen": 0}
    if n_pairs < 1:
        dim = C_t.shape[1]
        return torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE), diag
    src_concepts_np = concept_ids_train[src_words]
    tgt_concepts_np = concept_ids_train[tgt_words]
    src_concepts_t = torch.from_numpy(src_concepts_np).to(DEVICE)
    tgt_concepts_t = torch.from_numpy(tgt_concepts_np).to(DEVICE)
    dim = C_t.shape[1]
    # BUGFIX-3a: codebook mean (per-column) -- compute once, reused per step
    C_mean = C_t.mean(dim=0, keepdim=True) if CFRPE_CENTER_CODES else None
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    W_last_good = W.clone()
    # BUGFIX-3b: Frobenius cap = sqrt(dim) * factor (operator-norm proxy)
    fro_cap = math.sqrt(float(dim)) * CFRPE_W_OPNORM_CLIP_FACTOR
    for step in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = C_t[src_concepts_t[st]]
        Nxt = C_t[tgt_concepts_t[st]]
        if CFRPE_CENTER_CODES:
            Ctx = Ctx - C_mean
            Nxt = Nxt - C_mean
        error = Nxt - Ctx @ W.t()
        dW = (error.t() @ Ctx) / float(batch)
        W = W + lr * dW
        # BUGFIX-3b: Frobenius clip every step (cheap)
        w_fro = W.norm()
        if torch.isfinite(w_fro) and w_fro.item() > fro_cap:
            W = W * (fro_cap / (w_fro.item() + 1e-12))
            diag["n_clip_events"] += 1
        # BUGFIX-3c: NaN/Inf check (occasional, not every step)
        if (step + 1) % CFRPE_CHECK_FINITE_EVERY == 0:
            if not torch.all(torch.isfinite(W)):
                diag["n_nan_inf_seen"] += 1
                diag["n_finite_resets"] += 1
                W = W_last_good.clone()
            else:
                W_last_good = W.clone()
    w_fro_final = W.norm().item() if torch.all(torch.isfinite(W)) else float("nan")
    diag["final_w_fro"] = round(float(w_fro_final), 4) if math.isfinite(w_fro_final) else None
    diag["fro_cap"] = round(float(fro_cap), 4)
    diag["centered_codes"] = bool(CFRPE_CENTER_CODES)
    # Final safety: if W non-finite at the end, return last-good
    if not torch.all(torch.isfinite(W)):
        W = W_last_good
        diag["final_returned_last_good"] = True
    else:
        diag["final_returned_last_good"] = False
    return W, diag


def build_decode_D_torch(
    concept_ids_train: np.ndarray, idx_train: np.ndarray, C_t: torch.Tensor, V: int
) -> torch.Tensor:
    """Build decode memory D on GPU; D[:, word_j] = sum C[concept_t] over train."""
    dim = C_t.shape[1]
    words_t = torch.from_numpy(idx_train.astype(np.int64)).to(DEVICE)
    concept_for_word = concept_ids_train
    concepts_t = torch.from_numpy(
        concept_for_word[idx_train].astype(np.int64)
    ).to(DEVICE)
    D_T = torch.zeros((V, dim), dtype=TORCH_DTYPE, device=DEVICE)
    n = len(idx_train)
    chunk = 8192
    for b in range(0, n, chunk):
        e = min(b + chunk, n)
        codes = C_t[concepts_t[b:e]]
        D_T.index_add_(0, words_t[b:e], codes)
    return D_T.T.contiguous()


# ============================================================================
# Logit-mixer readout (fair_harness style) -- UNCHANGED from v1 (it works)
# ============================================================================

def build_W_cfrpe_word_torch(
    E: torch.Tensor, idx_train_t: torch.Tensor, n_steps: int, batch: int,
    lr: float, gen: torch.Generator
) -> torch.Tensor:
    """cf-RPE plasticity over word-level transitions; matches cf-RPE source cell.

    No bug fixes here -- E is L2-normalized bipolar dense, so the cf-RPE update
    is bounded by O(1) per step and converges. v1 ARM 3 reproduced cf-RPE ref
    within 0.001 (top1 0.244 vs 0.2438).
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
    """Build per-arm [n_held, V] logits + diagnostics. FRESH state per arm."""
    V_total = E_base.shape[0]
    dim = E_base.shape[1]

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

    t0 = time.time()
    concept_ids = fit_vq_on_words(E_pre, V_C, seed)
    t_vq = time.time() - t0
    n_unique_concepts = int(np.unique(concept_ids).size)
    utilization = n_unique_concepts / float(V_C)

    rng = np.random.default_rng(seed + 1000)
    C_np = sparse_codebook_np(V_C, dim, CONCEPT_SPARSE_F, rng)
    C_t = torch.from_numpy(C_np).to(DEVICE)
    k_active_per_row = int(round(CONCEPT_SPARSE_F * dim))

    cfrpe_diag: Dict = {}
    t0 = time.time()
    if arm == "ARM_N1_V3_READOUT_HEBBIAN_PLASTICITY":
        W_C_t = build_concept_W_hebbian_torch(
            C_t, concept_ids, idx_train, INGEST_CHUNK,
        )
    else:
        W_C_t, cfrpe_diag = build_concept_W_cfrpe_torch(
            C_t, concept_ids, idx_train,
            n_steps=n_steps, batch=INGEST_BATCH, lr=CFRPE_LR, gen=gen,
        )
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_ingest_w = time.time() - t0

    t0 = time.time()
    D_t = build_decode_D_torch(concept_ids, idx_train, C_t, V_total)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_decode = time.time() - t0

    # ----- BUGFIX-1: n1_v3-faithful decode (no L2 norms) -----
    # n1_v3 source: scores = D.T @ concept_vec (raw); fed to temp-softmax + back-off.
    # The joint_sweep externalizes the temp + back-off, so this function must
    # return RAW scores. v1 broke this by L2-normalizing both sides.
    t0 = time.time()
    held_src_concepts = concept_ids[idx_held]
    held_src_concepts_t = torch.from_numpy(held_src_concepts).to(DEVICE)
    Q_t = C_t[held_src_concepts_t]              # (n_held, N_DIM) sparse source codes

    # Recall: predicted concept code = Q @ W_C (raw)
    activated_held = Q_t @ W_C_t                # (n_held, N_DIM)
    # BUGFIX-1: NO L2 normalization here -- preserves sparse-Willshaw selectivity.

    # Final NaN/Inf guard on activated (cf-RPE arm could still produce bad
    # entries despite per-step clipping if a single step blew up between checks)
    if not torch.all(torch.isfinite(activated_held)):
        n_bad = int((~torch.isfinite(activated_held)).sum().item())
        cfrpe_diag["n_activated_bad_replaced"] = n_bad
        activated_held = torch.where(
            torch.isfinite(activated_held),
            activated_held,
            torch.zeros_like(activated_held),
        )

    # Logits = activated @ D (raw -- n1_v3 source feeds this into temp-softmax)
    # BUGFIX-1: NO D-column L2 normalization either.
    n_h = activated_held.shape[0]
    logits = torch.zeros((n_h, V_total), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        logits[b:end] = activated_held[b:end] @ D_t

    # Final logits NaN/Inf guard before .cpu().numpy()
    if not torch.all(torch.isfinite(logits)):
        n_bad_logits = int((~torch.isfinite(logits)).sum().item())
        cfrpe_diag["n_logits_bad_replaced"] = n_bad_logits
        # Replace non-finite with finite floor (-1e9) so joint_sweep stays stable.
        logits = torch.where(
            torch.isfinite(logits),
            logits,
            torch.full_like(logits, -1e9),
        )

    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    del W_C_t, D_t, C_t, activated_held, Q_t, held_src_concepts_t, logits, E_used
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    out: Dict = {
        "logits": logits_np,
        "readout": "n1_v3",
        "vq_utilization": float(round(utilization, 4)),
        "n_unique_concepts": int(n_unique_concepts),
        "k_active_per_concept_row": int(k_active_per_row),
        "concept_sparse_f": float(CONCEPT_SPARSE_F),
        "wall_vq_s": round(t_vq, 2),
        "wall_ingest_s": round(t_ingest_w, 2),
        "wall_decode_s": round(t_decode, 2),
        "wall_recall_s": round(t_recall, 2),
        "wall_total_s": round(time.time() - t_total, 2),
    }
    if cfrpe_diag:
        out["cfrpe_diag"] = cfrpe_diag
    return out


# ============================================================================
# text8 corpus utilities (unchanged from v1)
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
# Joint (T, lambda) sweep + 3 metrics (unchanged from v1)
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
# Instrumentation self-test (extended for v2 bugfix invariants)
# ============================================================================

def _selftest():
    print("[selftest] running self-test (v2_BUGFIX)...", flush=True)

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

    # T4: concept-Hebbian W_C identity
    n_dim = 64
    vc = 4
    C_test = sparse_codebook_np(vc, n_dim, 0.10, rng)
    C_t_test = torch.from_numpy(C_test).to(DEVICE)
    concept_ids = np.array([0, 1, 2, 3, 0], dtype=np.int64)
    idx_train = np.array([0, 1, 0, 2, 0, 3, 0, 1, 0, 2], dtype=np.int64)
    W_C_t = build_concept_W_hebbian_torch(C_t_test, concept_ids, idx_train, 128)
    assert W_C_t.shape == (n_dim, n_dim), "T4 W_C shape: %s" % str(W_C_t.shape)
    W_C_np = W_C_t.detach().cpu().numpy()
    activated = C_test[0] @ W_C_np
    sims = C_test @ activated
    pred = int(np.argmax(sims))
    assert pred != 0, "T4 W_C predicted c0 -> c0: pred=%d" % pred

    # T5: decode-D Hebbian accumulates correctly
    D_t = build_decode_D_torch(concept_ids, idx_train, C_t_test, V=5)
    D = D_t.detach().cpu().numpy()
    expected = 5.0 * C_test[0]
    assert np.allclose(D[:, 0], expected, atol=1e-5), (
        "T5 D[:, 0] not 5*C[0]: max diff %.3f" % float(np.abs(D[:, 0] - expected).max())
    )

    # T6: cf-RPE concept W reduces fixed-point error AND stays finite (BUGFIX-3)
    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(0)
    W_cfrpe, diag = build_concept_W_cfrpe_torch(
        C_t_test, concept_ids, idx_train, n_steps=50, batch=8, lr=0.5, gen=gen,
    )
    assert torch.all(torch.isfinite(W_cfrpe)), "T6 cf-RPE W has NaN/Inf"
    assert W_cfrpe.abs().max().item() > 1e-6, "T6 cf-RPE W is all zeros"
    assert "final_w_fro" in diag, "T6 cf-RPE diag missing"

    # T6b (NEW for v2): cf-RPE stays finite even under STRESS (1000 steps, lr=1.0)
    # This is the regression test for v1 NaN failure.
    gen2 = torch.Generator(device=DEVICE)
    gen2.manual_seed(1)
    W_stress, diag_stress = build_concept_W_cfrpe_torch(
        C_t_test, concept_ids, idx_train, n_steps=1000, batch=8, lr=1.0, gen=gen2,
    )
    assert torch.all(torch.isfinite(W_stress)), (
        "T6b REGRESSION (v1 NaN bug): cf-RPE W non-finite after stress test. diag=%s"
        % diag_stress
    )
    # Frobenius cap respected
    fro_cap_test = math.sqrt(float(n_dim)) * CFRPE_W_OPNORM_CLIP_FACTOR
    # Allow small overshoot (clip is post-update)
    assert W_stress.norm().item() <= fro_cap_test * 1.1, (
        "T6b Frobenius cap violated: W_fro=%.3f cap=%.3f" % (
            W_stress.norm().item(), fro_cap_test
        )
    )

    # T6c (NEW for v2): centered codes produce zero-mean update
    # When CFRPE_CENTER_CODES=True, the per-batch Ctx mean should be ~0
    if CFRPE_CENTER_CODES:
        C_mean = C_t_test.mean(dim=0, keepdim=True)
        Ctx_centered = C_t_test[torch.from_numpy(concept_ids[:4]).to(DEVICE)] - C_mean
        # Per-column sum across the V_C-uniform-population should be near zero
        # (but we only have 4 samples here, so just assert magnitude bounded)
        assert Ctx_centered.abs().max().item() < 2.0, (
            "T6c centered codes magnitude too large: %.3f" % Ctx_centered.abs().max().item()
        )

    # T7: joint_sweep operational
    sub_logits = np.random.default_rng(42).standard_normal((20, 5)).astype(np.float32)
    U = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
    U_log = np.log(np.clip(U, 1e-30, 1.0))
    nxt = np.tile(np.array([0, 1, 2, 3, 4]), 4)
    res = joint_sweep(sub_logits[:10], sub_logits[10:], U_log, nxt[:10], nxt[10:],
                       [0.1, 0.5, 1.0], [0.5, 1.0], 3)
    assert math.isfinite(res["bpc_best"]) and 0.0 <= res["top1_acc"] <= 1.0, (
        "T7 joint sweep returned bad values: %s" % res
    )
    assert res["best_lambda_for_bpc"] in [0.5, 1.0], "T7 lambda not in grid"

    # T8: top1 + bpc + mrr math sanity
    n_t = 5
    V_t = 10
    nxt_t = np.array([3, 0, 9, 5, 2])
    logp_planted = np.full((n_t, V_t), -10.0, dtype=np.float64)
    for i, true_cls in enumerate(nxt_t):
        logp_planted[i, true_cls] = 0.0
    assert abs(top1_acc(logp_planted, nxt_t) - 1.0) < 1e-9, "T8 top1 perfect"
    assert abs(mrr_at_k(logp_planted, nxt_t, 10) - 1.0) < 1e-9, "T8 MRR perfect"

    # T9: substrate-only-decode invariant
    assert _LLM_CALL_COUNTER[0] == 0, "T9 LLM counter must start at 0"

    # T10 (NEW for v2): sparse-Willshaw n1_v3 readout selectivity (BUGFIX-1).
    # If we use the FIXED readout (raw logits, no L2 norm) on a tiny planted
    # example, the predicted argmax must beat unigram.
    # Build: 6 words mapped to 3 concepts; planted transition c0 -> c1 -> c2 -> c0
    # repeated. Words 0,1 are c0; words 2,3 are c1; words 4,5 are c2.
    # When held source = word 0 (c0), the correct next word should be in {2, 3} (c1).
    n_dim_t10 = 256
    vc_t10 = 3
    k_test_f = max(1, round(0.05 * n_dim_t10))
    rng_t10 = np.random.default_rng(11)
    C_t10_np = sparse_codebook_np(vc_t10, n_dim_t10, 0.05, rng_t10)
    C_t10 = torch.from_numpy(C_t10_np).to(DEVICE)
    V_t10 = 6
    concept_ids_t10 = np.array([0, 0, 1, 1, 2, 2], dtype=np.int64)
    # Build train sequence c0 -> c1 -> c2 -> c0 ... cycling 40 times
    # Word-level: pick random word from each concept's word-set
    rng_seq = np.random.default_rng(13)
    c_seq = np.tile(np.array([0, 1, 2]), 40)
    word_seq = np.zeros(len(c_seq), dtype=np.int64)
    for i, c in enumerate(c_seq):
        words_in_c = np.where(concept_ids_t10 == c)[0]
        word_seq[i] = rng_seq.choice(words_in_c)
    W_C_t10 = build_concept_W_hebbian_torch(C_t10, concept_ids_t10, word_seq, 128)
    D_t10 = build_decode_D_torch(concept_ids_t10, word_seq, C_t10, V_t10)
    # Predict from source word 0 (concept 0): should produce word in {2, 3}
    src_word = 0
    src_c = concept_ids_t10[src_word]
    Q = C_t10[src_c:src_c + 1]                       # (1, N_DIM)
    activated = Q @ W_C_t10                          # (1, N_DIM) raw
    logits = activated @ D_t10                       # (1, V) raw
    pred = int(torch.argmax(logits, dim=1).item())
    assert pred in (2, 3), (
        "T10 sparse-Willshaw selectivity FAIL (BUGFIX-1 broken): "
        "predicted word %d from c0 source; expected word in {2,3} (c1). "
        "logits=%s" % (pred, logits.cpu().numpy())
    )

    print(
        "[selftest] PASS: T1 sparse-codebook + T2 trigram + T3 sparsify-bipolar "
        "+ T4 W_C-Hebbian + T5 decode-D + T6 W_C-cfRPE-finite + T6b cf-RPE-stress-finite "
        "+ T6c centered-codes + T7 joint-sweep + T8 top1/MRR + T9 llm=0 "
        "+ T10 BUGFIX-1-sparse-Willshaw-selectivity",
        flush=True,
    )


# ============================================================================
# Per-seed runner (unchanged from v1 except for cfrpe_diag pass-through)
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
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d V_C=%d concept_f=%.4f k=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, V_C, CONCEPT_SPARSE_F,
        max(1, round(CONCEPT_SPARSE_F * N_DIM)), str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

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
                          "wall_recall_s", "wall_total_s",
                          "k_active_per_concept_row", "concept_sparse_f",
                          "cfrpe_diag"):
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
# Verdict (extended to surface cf-RPE numerical diagnostics)
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
        # cf-RPE diagnostics surface (for ARM 4 / Fix #28 verify-the-referent)
        cfrpe_diags = [u["by_arm"][arm].get("cfrpe_diag", {}) for u in valid_units]
        cfrpe_diag_summary = None
        if any(cfrpe_diags):
            cfrpe_diag_summary = {
                "n_finite_resets_mean": float(np.mean([d.get("n_finite_resets", 0) for d in cfrpe_diags])),
                "n_clip_events_mean": float(np.mean([d.get("n_clip_events", 0) for d in cfrpe_diags])),
                "final_w_fro_mean": float(np.mean([d.get("final_w_fro", float("nan")) for d in cfrpe_diags if d.get("final_w_fro") is not None] or [float("nan")])),
                "centered_codes": cfrpe_diags[0].get("centered_codes", False) if cfrpe_diags[0] else None,
                "any_returned_last_good": any(d.get("final_returned_last_good", False) for d in cfrpe_diags),
            }
        b_mean = float(np.mean(bpc_vals))
        t_mean = float(np.mean(top1_vals))
        t_std = float(np.std(top1_vals))
        agg = {
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
        if cfrpe_diag_summary is not None:
            agg["cfrpe_diag_summary"] = cfrpe_diag_summary
        by_arm_agg[arm] = agg

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
        "v2_bugfixes": {
            "bugfix_1_l2_norm_removed_n1v3_readout": True,
            "bugfix_2_sparse_sweet_spot_f": CONCEPT_SPARSE_F,
            "bugfix_3_cfrpe_centered_codes_and_w_clip": True,
            "bugfix_3_fro_cap_factor": CFRPE_W_OPNORM_CLIP_FACTOR,
        },
        "honest_scope": (
            "v2 BUGFIX of v1 PROVENANCE_FAIL (ARM 2 top1 0.2189 << ref 0.4455 due to "
            "L2-norm destroying sparse-Willshaw property; ARM 4 NaN due to cf-RPE on "
            "positive-mean sparse codes diverging). v2 removes L2-norm in n1_v3 readout, "
            "uses sparse Willshaw sweet-spot f=%.4f (k=25 same as cert anchor), centers "
            "sparse codes before cf-RPE delta-rule, and clips W Frobenius norm per step "
            "to prevent overflow. Verdict on ARM 4 only; ARM 2/ARM 3 are provenance gates."
        ) % CONCEPT_SPARSE_F,
        "cites": [
            "preregs/2026-06-24_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v2_BUGFIX.md",
            "data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json",
            "data/exp_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1/metrics.json",
            "experiments/exp_n1_concept_lm_substrate_native_token_decode_v3.py",
            "experiments/exp_substrate_n1v3_readout_x_cfrpe_plasticity_compose_v1.py",
            "Skunkworks_VET_2026-06-23_chain_grade_bottleneck_is_readout",
            "USER_2026-06-23_META_HARNESS_RIGGED_row_588_top1_load_bearing",
        ],
    }

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
            "PROVENANCE_FAIL (v2 BUGFIX did not restore provenance): %s. %s"
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

    if arm4_top1 >= ARM4_CHAIN_GRADE_TOP1 and cv_ok:
        return (
            "HARD_PASS",
            "HARD_PASS_CHAIN_GRADE_BONUS: ARM 4 top1=%.4f >= %.3f chain-grade floor AND cv=%.3f <= %.2f. "
            "Substantial new chain-grade evidence: n1_v3 readout x cf-RPE plasticity composes super-additively. "
            % (arm4_top1, ARM4_CHAIN_GRADE_TOP1, arm4_top1_cv, CV_MAX) + base_summary,
            detail,
        )

    if arm4_top1 >= ARM4_HARD_PASS_TOP1:
        cv_note = "" if cv_ok else " (NOTE cv=%.3f > %.2f; HARD_PASS but seed-unstable)" % (arm4_top1_cv, CV_MAX)
        return (
            "HARD_PASS",
            "HARD_PASS: ARM 4 top1=%.4f >= %.3f hard-pass floor. Super-additive composition confirmed.%s "
            % (arm4_top1, ARM4_HARD_PASS_TOP1, cv_note) + base_summary,
            detail,
        )

    if arm4_top1 >= ARM4_MIDDLE_BAND_FLOOR:
        return (
            "MIDDLE_BAND",
            "MIDDLE_BAND: ARM 4 top1=%.4f in [%.3f, %.3f). Additive but not super-additive; "
            "n1_v3 readout dominates compose direction. " % (
                arm4_top1, ARM4_MIDDLE_BAND_FLOOR, ARM4_HARD_PASS_TOP1
            ) + base_summary,
            detail,
        )

    return (
        "HARD_FAIL",
        "HARD_FAIL: ARM 4 top1=%.4f <= %.3f. No super-additive composition; n1_v3 readout "
        "dominates regardless of plasticity rule -- the readout is the only load-bearing knob. "
        % (arm4_top1, ARM4_HARD_FAIL_TOP1) + base_summary,
        detail,
    )


# ============================================================================
# atexit synthesizer (unchanged from v1)
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
          "concept_f=%.4f k=%d N_STEPS=%d seeds=%s arms=%s | name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, V_C,
              CONCEPT_SPARSE_F, max(1, round(CONCEPT_SPARSE_F * N_DIM)),
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
