"""substrate_pc_hierarchy_fair_harness_v1 -- PC HIERARCHY under FAIR HARNESS.

Resolves A12 contradiction (meta-skepticism drill Anchor 1):
  - PC hierarchy chain-grade for 5-corpus aggregation BUT degraded capacity 0.25x.
  - Prior cells exp_substrate_pc_hierarchy_text8_lm_v1+v2 HARD_FAILed under
    META_HARNESS_RIGGED methodology (cosine-similarity logits + T=1 softmax =
    near-uniform; coarse TEMP_GRID; BPC-only metric).
  - Skunkworks methodology audit 2026-06-23 reclassified those to SUSPENDED METHCONF.
  - This cell re-tests PC hierarchy under the fair_harness rail (joint (T,lambda)
    sweep, 3 metrics: BPC + top-1 + MRR, selection-mixer harness).

USER directive 2026-06-24: hierarchy may have COMPUTATIONAL reasons beyond biology -- TEST IT.

Four arms (each builds FRESH W on word2vec sparse-bipolar f=0.05 encoder; no cross-contamination):
  ARM_RANK_1_BASELINE
      Fair-harness reference; sparse-bipolar f=0.05 + rank-1 Hebbian W.
      Sanity rail at ~7.3065 BPC (per ARM_SUBSTRATE_SPARSE_BIPOLAR in fair_harness_v1).
  ARM_PC_HIERARCHY_2LEVEL
      Rao-Ballard 2-level PC with top-down feedback (n_layers=2 + W_pred predictor).
  ARM_PC_HIERARCHY_3LEVEL
      3-level PC (n_layers=3 + W_pred predictor).
  ARM_PC_HIERARCHY_2LEVEL_PLUS_CFRPE
      2-level PC + cf-RPE plasticity on the predictor layer (heterogeneity test).

Pre-reg HARD bands (per Anchor 1):
  Sanity rail: ARM_RANK_1_BASELINE within +/- 0.05 of 7.3065 BPC ref.
  HARD_PASS: any PC arm beats RANK_1 by >= +0.05 top-1 OR >= +0.05 BPC under
             selection-mixer (joint (T,lambda) sweep).
  MIDDLE_BAND: any PC arm beats RANK_1 by [0.02, 0.05] on top-1.
  HARD_FAIL: ALL PC arms <= RANK_1 on ALL 3 metrics under revised harness.
  CHAIN_GRADE_BONUS: any PC arm achieves top-1 >= 0.55 (substantial new chain-grade).

What this DOES show:
  - Whether PC hierarchy adds LM lift under the fair harness that exposed
    substrate-as-LM as methodology-confound.
  - Whether 2-vs-3 level hierarchy is the right depth.
  - Whether heterogeneous plasticity (cf-RPE) compounds with PC hierarchy.

What this does NOT show:
  - This is f=0.05; doesn't test phase-shift modes or other f values
    (separate cell for f=0.02 if needed for direct N1 comparison).
  - Doesn't test 5-corpus aggregation (text8 only).
  - Doesn't test capacity (no M-sweep; this is an LM lift test).

GPU REQUIRED (Fix #24): torch.cuda for matmul / PC training / sparse-bipolar.

Cites:
  preregs/2026-06-24_substrate_pc_hierarchy_fair_harness_v1.md
  experiments/exp_fair_harness_substrate_as_lm_v1.py  (parent fair-harness pattern)
  experiments/exp_substrate_pc_hierarchy_text8_lm_v2.py  (PC layer build_pc_layers_gpu)
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py  (cf-RPE)
  cert_ledger.jsonl row 588 META_HARNESS_RIGGED reclassification
  USER_2026-06-24_anchor1_test_PC_hierarchy_computational_reasons_beyond_biology
  USER_2026-06-23_audit_ratification (V2 LM gap)
  USER_2026-06-22_Fix24 (GPU dispatch must use GPU)

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

ANCHOR_NAME = "substrate_pc_hierarchy_fair_harness_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
_LLM_CALL_COUNTER = [0]

# Reference baselines (from fair_harness_substrate_as_lm_v1 production)
UNIGRAM_BPC_REF = 7.738
UNIGRAM_TOP1_REF = 0.2171
RANK1_BPC_REF = 7.3065   # ARM_SUBSTRATE_SPARSE_BIPOLAR from fair_harness_v1 production
SANITY_TOL = 0.05        # rail: ARM_RANK_1_BASELINE within +/- SANITY_TOL of 7.3065

# Pre-reg bands (PC vs RANK_1 baseline, per USER Anchor 1)
HP_TOP1_LIFT = 0.05      # PC top-1 - RANK_1 top-1 >= 0.05 => HARD_PASS
HP_BPC_LIFT = 0.05       # RANK_1 bpc - PC bpc >= 0.05 bits => HARD_PASS
MB_TOP1_LIFT_MIN = 0.02  # MIDDLE_BAND if lift in [0.02, 0.05)
CHAIN_GRADE_TOP1_BAR = 0.55  # CHAIN_GRADE_BONUS if any PC arm achieves top-1 >= 0.55
DEGEN_TOL = 0.5          # raw_bpc_at_T1_L1 within +/- DEGEN_TOL of -log2(1/V) => DEGEN
HP_BPC_CV_MAX = 0.10

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Config (FULL = production GPU)
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

# Joint (T, lambda) sweep (per META C7: exclude 0.0 from LAMBDA)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]   # META C7: 0.0 excluded (full-unigram is degenerate selector)

# Sparse-bipolar f
SPARSE_BIPOLAR_F = 0.05

# PC hierarchy knobs
PC_INIT_SCALE = 0.01   # variance-scaled Gaussian init (V2 bugfix from pc_hierarchy_v2)
PC_ALPHA = 0.05        # PC update rate (mid of v2 ALPHA_GRID=[0.01, 0.05, 0.1])

# cf-RPE knobs (for ARM_PC_HIERARCHY_2LEVEL_PLUS_CFRPE)
CFRPE_LR = 0.5
CFRPE_N_STEPS = 200
CFRPE_BATCH = 256

# MRR @ K
MRR_K = 10

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke must fit under 180s on laptop CPU. Exercises all 4 arms + joint sweep
    # + 3 metrics + 7x5=35 (T,L) combos + verdict bands.
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    CFRPE_N_STEPS = 50

ARMS = [
    "ARM_RANK_1_BASELINE",
    "ARM_PC_HIERARCHY_2LEVEL",
    "ARM_PC_HIERARCHY_3LEVEL",
    "ARM_PC_HIERARCHY_2LEVEL_PLUS_CFRPE",
]
PC_ARMS = [a for a in ARMS if a != "ARM_RANK_1_BASELINE"]
WORD2VEC_MODEL = "word2vec-google-news-300"

CONFIG_VERSION = (
    "substrate_pc_hierarchy_fair_harness_v1; N_DIM=%d PRETRAIN_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s temps=%s lambdas=%s sparse_f=%.3f "
    "pc_init_scale=%.3f pc_alpha=%.3f cfrpe_lr=%.2f cfrpe_steps=%d cfrpe_batch=%d "
    "MRR_K=%d device=%s; bands HP_TOP1_LIFT>=%.3f HP_BPC_LIFT>=%.3f MB_TOP1_LIFT>=%.3f "
    "CHAIN_GRADE_TOP1>=%.2f SANITY_TOL=%.3f DEGEN_tol=%.2f cv_max=%.2f"
) % (
    N_DIM, PRETRAIN_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    TEMP_GRID, LAMBDA_GRID, SPARSE_BIPOLAR_F, PC_INIT_SCALE, PC_ALPHA,
    CFRPE_LR, CFRPE_N_STEPS, CFRPE_BATCH, MRR_K, str(DEVICE),
    HP_TOP1_LIFT, HP_BPC_LIFT, MB_TOP1_LIFT_MIN, CHAIN_GRADE_TOP1_BAR,
    SANITY_TOL, DEGEN_TOL, HP_BPC_CV_MAX,
)


# ============================================================================
# Char-trigram encoder (defensive; only used as OOV fallback for word2vec)
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


def _safe_sign_t(X: torch.Tensor) -> torch.Tensor:
    """sign() that maps 0 -> +1 (avoid degenerate zero columns)."""
    s = torch.sign(X)
    s = torch.where(s == 0, torch.ones_like(s), s)
    return s


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


# Gensim cache (process-local)
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


def build_E_word2vec_gpu(vocab: List[str], n_dim: int, seed: int
                           ) -> Tuple[torch.Tensor, Dict]:
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
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


# ============================================================================
# Sparse-bipolar primitive
# ============================================================================

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
# Rank-1 Hebbian W (baseline)
# ============================================================================

def build_rank1_W_gpu(idx_train_t: torch.Tensor, E: torch.Tensor,
                       ingest_chunk: int) -> torch.Tensor:
    """W = sum outer(E[idx[t+1]], E[idx[t]]); rank-1 Hebbian."""
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


# ============================================================================
# PC hierarchy (Rao-Ballard 2-level / 3-level)
# ============================================================================
# Implementation forked from exp_substrate_pc_hierarchy_text8_lm_v2.py with the
# v2 bugfixes preserved (variance-scaled init; sign(0)->+1; quarter+last 10%
# recon-err tracking with last-chunk fallback for tiny n_pairs).

def build_pc_layers_gpu(E: torch.Tensor, idx_train_t: torch.Tensor, n_layers: int,
                          alpha: float, ingest_chunk: int
                          ) -> Tuple[List[torch.Tensor], List[float]]:
    """Build n_layers PC stack on GPU + W_pred predictor.

    Per training token (chunked):
      L_0_in = E[idx_train[t]]
      For each layer li in 0..n_layers-1:
        L_i_in_n = L_i_in / sqrt(dim)
        L_i_out = sign(W_i @ L_i_in_n)
        error_i = L_i_in_n - (L_i_out @ W_i) / sqrt(dim)   (top-down recon)
        W_i += alpha * (error_i.T @ L_i_in_n) / dim
        L_(i+1)_in = L_i_out  (cleaned bipolar signal upward)
      W_pred += outer(E[idx_train[t+1]], L_top_out)

    Returns (Ws_pc + [W_pred], [recon_err_quarter, recon_err_end]) for selftest.
    """
    device = E.device
    dim = E.shape[1]
    init_gen = torch.Generator(device=device)
    init_gen.manual_seed(int(idx_train_t.shape[0]) % (2**31 - 1) + n_layers * 100003)
    init_scale = PC_INIT_SCALE / float(math.sqrt(dim))
    Ws = [
        torch.randn(dim, dim, generator=init_gen, dtype=TORCH_DTYPE, device=device).mul_(init_scale)
        for _ in range(n_layers)
    ]
    W_pred = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    inv_dim = 1.0 / float(dim)

    if n_pairs <= 0:
        return Ws + [W_pred], [1.0, 1.0]

    quarter_mark = max(1, n_pairs // 4)
    recon_err_quarter = float("nan")
    recon_err_end_accum = 0.0
    recon_err_end_count = 0

    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        chunk_size = end - b
        layer_in = E[idx_train_t[b:end]]
        # Forward pass through n_layers PC stack
        for li in range(n_layers):
            layer_in_n = layer_in / float(math.sqrt(dim))
            layer_out = _safe_sign_t(layer_in_n @ Ws[li].T)
            recon = (layer_out @ Ws[li]) / float(math.sqrt(dim))
            error = layer_in_n - recon
            Ws[li].add_(error.T @ layer_in_n, alpha=alpha * inv_dim)
            layer_in = layer_out

        # Predictor: outer(target, top_out)
        tgt_idx = idx_train_t[b + 1:end + 1]
        E_tgt = E[tgt_idx]
        W_pred.add_(E_tgt.T @ layer_in)

        # Track recon error of final layer
        if b <= quarter_mark < end and math.isnan(recon_err_quarter):
            err_norms = error.norm(dim=1)
            in_norms = layer_in_n.norm(dim=1).clamp(min=1e-12)
            recon_err_quarter = float((err_norms / in_norms).mean())
        is_last_chunk = (end >= n_pairs)
        if b >= int(n_pairs * 0.9) or is_last_chunk:
            err_norms = error.norm(dim=1)
            in_norms = layer_in_n.norm(dim=1).clamp(min=1e-12)
            recon_err_end_accum += float((err_norms / in_norms).sum())
            recon_err_end_count += int(chunk_size)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()

    recon_err_end = (recon_err_end_accum / max(recon_err_end_count, 1)
                     ) if recon_err_end_count > 0 else float("nan")
    return Ws + [W_pred], [recon_err_quarter, recon_err_end]


def build_pc_layers_plus_cfrpe_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                                    n_layers: int, alpha: float,
                                    ingest_chunk: int, cfrpe_lr: float,
                                    cfrpe_n_steps: int, cfrpe_batch: int,
                                    gen: torch.Generator
                                    ) -> Tuple[List[torch.Tensor], List[float]]:
    """Build n_layers PC stack + cf-RPE predictor refinement.

    Phase 1: build PC layers exactly like build_pc_layers_gpu (Hebbian W_pred).
    Phase 2: refine W_pred via cf-RPE iterative stochastic update on (top_out, tgt) pairs:
      error = E_tgt - top_out @ W_pred.T
      W_pred += cfrpe_lr * (error.T @ top_out) / batch
    """
    Ws_full, rec = build_pc_layers_gpu(E, idx_train_t, n_layers, alpha, ingest_chunk)
    Ws_pc = Ws_full[:-1]
    # Discard the Hebbian-init W_pred; cf-RPE refinement requires W_pred = 0 init
    # (per reference cell exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1).
    # With Hebbian-init the error `tgt - top @ W_pred.T` is large-magnitude (W_pred
    # is raw-outer-accumulator) and cf-RPE updates diverge. The HYPOTHESIS here is
    # that PC layers provide a BETTER FEATURE REPRESENTATION; cf-RPE learns the
    # predictor on that representation from scratch.
    device = E.device
    dim = E.shape[1]
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0 or cfrpe_n_steps <= 0:
        return Ws_full, rec
    W_pred = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    sqrt_dim = float(math.sqrt(dim))

    # Pre-compute top_out for all training pairs (chunked; reuses PC forward).
    # L2-normalize top_out so cf-RPE updates stay bounded. Without this, bipolar
    # top_out has norm sqrt(dim) (~22.6 for dim=512) and cf-RPE error grows
    # geometrically per step (W_pred norm doubles ~ every 2 steps).
    top_out_all = torch.zeros((n_pairs, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        layer_in = E[idx_train_t[b:end]]
        for li in range(n_layers):
            layer_in_n = layer_in / sqrt_dim
            layer_in = _safe_sign_t(layer_in_n @ Ws_pc[li].T)
        top_out_all[b:end] = _l2_normalize_t(layer_in)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()

    # cf-RPE stochastic refinement of W_pred
    for _ in range(cfrpe_n_steps):
        st = torch.randint(0, n_pairs, (cfrpe_batch,), generator=gen, device=device)
        top_b = top_out_all[st]
        tgt_b = E[idx_train_t[st + 1]]
        # cf-RPE: error = tgt - top_b @ W_pred.T; update drives error to zero
        error = tgt_b - top_b @ W_pred.t()
        dW = (error.t() @ top_b) / float(cfrpe_batch)
        W_pred.add_(dW, alpha=cfrpe_lr)
    if device.type == "cuda":
        torch.cuda.synchronize()
    del top_out_all
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return Ws_pc + [W_pred], rec


def forward_pc_layers_gpu(Ws_full: List[torch.Tensor], E: torch.Tensor,
                            idx_ctx_t: torch.Tensor, recall_batch: int,
                            l2_top: bool = False) -> torch.Tensor:
    """Forward pass: logits = E @ normalize(W_pred @ top_layer_out(idx_ctx)).

    l2_top: if True, L2-normalize the top-layer bipolar output before applying
    W_pred. Required when W_pred was trained on L2-normalized top_out (e.g.
    in build_pc_layers_plus_cfrpe_gpu). Defaults to False for the Hebbian-
    trained PC arms (W_pred is raw outer accumulator; cosine similarity
    invariant to scale after final L2-normalize of pred_vec).
    """
    n_pc_layers = len(Ws_full) - 1
    W_pred = Ws_full[-1]
    V = E.shape[0]
    n = idx_ctx_t.shape[0]
    device = E.device
    dim = E.shape[1]
    sqrt_dim = float(math.sqrt(dim))
    logits_out = torch.zeros((n, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        layer_in = E[idx_ctx_t[b:end]]
        for li in range(n_pc_layers):
            layer_in_n = layer_in / sqrt_dim
            layer_in = _safe_sign_t(layer_in_n @ Ws_full[li].T)
        if l2_top:
            layer_in = _l2_normalize_t(layer_in)
        pred_vec = layer_in @ W_pred.T
        pred_vec = _l2_normalize_t(pred_vec)
        logits_out[b:end] = pred_vec @ E.T
        if device.type == "cuda" and (b // recall_batch) % 16 == 0:
            torch.cuda.synchronize()
    return logits_out


# ============================================================================
# Per-arm logits builder (each arm: FRESH W on sparse-bipolar E)
# ============================================================================

def compute_arm_logits(arm_label: str, E_base: torch.Tensor, idx_train: np.ndarray,
                         idx_held: np.ndarray, seed: int) -> Dict:
    """Return [n_held, V] float32 logits + diagnostics.

    All arms use sparse-bipolar f=0.05 transform of word2vec base E (validated).
    """
    V, dim = E_base.shape
    device = E_base.device

    # All arms apply sparse-bipolar f=0.05 transform (validated baseline)
    E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))

    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_ctx_t = torch.from_numpy(idx_held[:-1] if len(idx_held) > 1 else idx_held).to(device)
    n_ctx = idx_ctx_t.shape[0]

    pc_rec = [float("nan"), float("nan")]

    t0 = time.time()
    if arm_label == "ARM_RANK_1_BASELINE":
        W = build_rank1_W_gpu(idx_train_t, E_used, INGEST_CHUNK)
        pred_held = torch.zeros((n_ctx, dim), dtype=TORCH_DTYPE, device=device)
        for b in range(0, n_ctx, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_ctx)
            pred_held[b:end] = _l2_normalize_t(E_used[idx_ctx_t[b:end]] @ W.T)
        logits = torch.zeros((n_ctx, V), dtype=TORCH_DTYPE, device=device)
        for b in range(0, n_ctx, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_ctx)
            logits[b:end] = pred_held[b:end] @ E_used.T
        del W, pred_held
    elif arm_label == "ARM_PC_HIERARCHY_2LEVEL":
        Ws_full, pc_rec = build_pc_layers_gpu(E_used, idx_train_t, n_layers=2,
                                                alpha=PC_ALPHA, ingest_chunk=INGEST_CHUNK)
        logits = forward_pc_layers_gpu(Ws_full, E_used, idx_ctx_t, RECALL_BATCH)
        for W in Ws_full:
            del W
    elif arm_label == "ARM_PC_HIERARCHY_3LEVEL":
        Ws_full, pc_rec = build_pc_layers_gpu(E_used, idx_train_t, n_layers=3,
                                                alpha=PC_ALPHA, ingest_chunk=INGEST_CHUNK)
        logits = forward_pc_layers_gpu(Ws_full, E_used, idx_ctx_t, RECALL_BATCH)
        for W in Ws_full:
            del W
    elif arm_label == "ARM_PC_HIERARCHY_2LEVEL_PLUS_CFRPE":
        gen = torch.Generator(device=device)
        gen.manual_seed(seed * 10007 + 31337)
        Ws_full, pc_rec = build_pc_layers_plus_cfrpe_gpu(
            E_used, idx_train_t, n_layers=2, alpha=PC_ALPHA,
            ingest_chunk=INGEST_CHUNK, cfrpe_lr=CFRPE_LR,
            cfrpe_n_steps=CFRPE_N_STEPS, cfrpe_batch=CFRPE_BATCH, gen=gen,
        )
        # cfrpe trained on L2-normalized top_out -> inference must match
        logits = forward_pc_layers_gpu(Ws_full, E_used, idx_ctx_t, RECALL_BATCH, l2_top=True)
        for W in Ws_full:
            del W
    else:
        raise ValueError("unknown arm: %s" % arm_label)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    del logits, idx_train_t, idx_ctx_t, E_used
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "pc_recon_err_quarter": pc_rec[0],
        "pc_recon_err_end": pc_rec[1],
    }


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
# Joint (T, lambda) sweep + 3 metrics
# ============================================================================

def softmax_logits_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp_logp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float
                            ) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    logp_nxt = logp[np.arange(n), nxt]
    return -float(np.mean(logp_nxt)) / math.log(2.0)


def top1_acc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    if len(nxt) == 0:
        return float("nan")
    pred = np.argmax(logp, axis=1)
    return float(np.mean(pred == nxt))


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


def joint_sweep_substrate(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                            U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                            temp_grid: list, lambda_grid: list, mrr_k: int
                            ) -> Dict:
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)
    raw_top1_at_T1_L1 = top1_acc_from_logp(logp_T1, nxt_test)
    raw_mrr_at_T1_L1 = mrr_at_k(logp_T1, nxt_test, mrr_k)

    grid: Dict[str, Dict] = {}
    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    for T in temp_grid:
        probs_dev = softmax_logits_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in lambda_grid:
            logp_dev = log_linear_interp_logp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc_from_logp(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
            key = "T%.4f_L%.2f" % (T, lam)
            grid[key] = {"bpc_dev": round(bd, 4), "top1_dev": round(td, 4),
                          "mrr_dev": round(md, 4)}
            if bd < best_bpc["dev_value"]:
                best_bpc = {"T": float(T), "lambda": float(lam), "dev_value": bd}
            if td > best_top1["dev_value"]:
                best_top1 = {"T": float(T), "lambda": float(lam), "dev_value": td}
            if md > best_mrr["dev_value"]:
                best_mrr = {"T": float(T), "lambda": float(lam), "dev_value": md}

    def _test_metric(T: float, lam: float, fn) -> float:
        probs_test = softmax_logits_with_T(sub_logits_test, T)
        logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
        logp_test = log_linear_interp_logp(logp_sub_test, U_log, lam)
        return fn(logp_test, nxt_test)

    bpc_best_test = _test_metric(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _test_metric(best_top1["T"], best_top1["lambda"], top1_acc_from_logp)
    mrr_best_test = _test_metric(best_mrr["T"], best_mrr["lambda"],
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
        "raw_mrr_at_T1_L1": round(raw_mrr_at_T1_L1, 4),
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
        "grid_size": len(grid),
    }


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
    print("[seed=%d UNIGRAM_REF] bpc=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"],
        uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM_REF": uni}

    # Build one common word2vec E (reused for all arms; per-arm sparse-bipolar inside compute_arm_logits)
    print("\n[seed=%d] building word2vec base E (V=%d, N_DIM=%d) on %s..." % (
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
        for arm in ARMS:
            by_arm[arm] = {"empty_eval": True}
        return {"seed": seed, "by_arm": by_arm, "V": V, "N": N_DIM,
                  "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                  "VOCAB_CAP": VOCAB_CAP, "PRETRAIN_DIM": PRETRAIN_DIM,
                  "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
                  "elapsed_s_seed": round(time.time() - t_seed, 2),
                  "device": str(DEVICE), "encoder_meta": encoder_meta,
                  "n_llm_calls": 0}
    n_dev = n_eval // 2
    valid_held_pos = np.where(mask)[0]
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    for arm in ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building logits..." % (seed, arm), flush=True)
        try:
            ar = compute_arm_logits(arm, E_base, idx_train, idx_held, seed)
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
        # logits shape: [len(ctx_full), V] -- one logits row per ctx position
        logits_full = ar["logits"]
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
            jr = joint_sweep_substrate(
                logits_eval[:ndev], logits_eval[ndev:], U_log,
                nxt_eval_local[:ndev], nxt_eval_local[ndev:],
                TEMP_GRID, LAMBDA_GRID, MRR_K,
            )
            jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
            jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
            jr["pc_recon_err_quarter"] = ar.get("pc_recon_err_quarter", float("nan"))
            jr["pc_recon_err_end"] = ar.get("pc_recon_err_end", float("nan"))
            by_arm[arm] = jr
            print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
                  "(bestT=%.4f bestL=%.2f) raw_T1L1_bpc=%.3f" % (
                      seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                      jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                      jr["raw_bpc_at_T1_L1"]), flush=True)
            continue
        # Normal path: logits_ctx aligns with ctx_full
        logits_eval = logits_ctx[mask]
        jr = joint_sweep_substrate(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
        jr["pc_recon_err_quarter"] = ar.get("pc_recon_err_quarter", float("nan"))
        jr["pc_recon_err_end"] = ar.get("pc_recon_err_end", float("nan"))
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
        "N": N_DIM,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "PRETRAIN_DIM": PRETRAIN_DIM,
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

    # Aggregate unigram ref (informational only; not load-bearing for bands)
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM_REF", {}).get("bpc_unigram", float("nan")) for u in units]
    uni_top1 = [u["by_arm"].get("ARM_UNIGRAM_REF", {}).get("top1_unigram", float("nan")) for u in units]
    uni_mrr = [u["by_arm"].get("ARM_UNIGRAM_REF", {}).get("mrr_unigram", float("nan")) for u in units]
    unigram_agg = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
        "top1_mean": round(float(np.mean(uni_top1)), 4),
        "top1_std": round(float(np.std(uni_top1)), 4),
        "mrr_mean": round(float(np.mean(uni_mrr)), 4),
        "mrr_std": round(float(np.std(uni_mrr)), 4),
    }

    by_arm_agg: Dict[str, Dict] = {"ARM_UNIGRAM_REF": unigram_agg}
    V_first = units[0].get("V", VOCAB_CAP)
    vocab_entropy_uniform = math.log2(max(V_first, 2))

    for arm in ARMS:
        seeds_compute_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid = [(not cf) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
                 for cf, u in zip(seeds_compute_failed, units)]
        n_compute_failed = int(sum(seeds_compute_failed))
        valid_units = [u for ok, u in zip(valid, units) if ok]
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"),
                "top1_acc_mean": float("nan"),
                "mrr_at_10_mean": float("nan"),
                "raw_bpc_at_T1_L1_mean": float("nan"),
                "n_valid_seeds": 0,
                "n_compute_failed": n_compute_failed,
                "all_seeds_failed": True,
            }
            continue
        bpc_vals = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_vals = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_vals = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_t1l1_vals = [u["by_arm"][arm]["raw_bpc_at_T1_L1"] for u in valid_units]
        bT_bpc = [u["by_arm"][arm]["best_T_for_bpc"] for u in valid_units]
        bL_bpc = [u["by_arm"][arm]["best_lambda_for_bpc"] for u in valid_units]
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        t_mean = float(np.mean(top1_vals))
        t_std = float(np.std(top1_vals))
        m_mean = float(np.mean(mrr_vals))
        m_std = float(np.std(mrr_vals))
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_acc_mean": round(t_mean, 4),
            "top1_acc_std": round(t_std, 4),
            "top1_acc_cv": round(t_std / max(abs(t_mean), 1e-6), 4),
            "mrr_at_10_mean": round(m_mean, 4),
            "mrr_at_10_std": round(m_std, 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_t1l1_vals)), 4),
            "best_T_for_bpc_mean": round(float(np.mean(bT_bpc)), 4),
            "best_lambda_for_bpc_mean": round(float(np.mean(bL_bpc)), 4),
            "n_valid_seeds": int(len(valid_units)),
            "n_compute_failed": n_compute_failed,
            "all_seeds_failed": False,
        }

    # Sanity rail: ARM_RANK_1_BASELINE within +/- SANITY_TOL of RANK1_BPC_REF
    rank1 = by_arm_agg.get("ARM_RANK_1_BASELINE", {})
    sanity_ok = (not rank1.get("all_seeds_failed", True) and
                 math.isfinite(rank1.get("bpc_best_mean", float("inf"))) and
                 abs(rank1["bpc_best_mean"] - RANK1_BPC_REF) <= SANITY_TOL)

    # Substrate-only decode gate
    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    # DEGEN gate
    degen_arms = []
    for arm in ARMS:
        a = by_arm_agg[arm]
        if a.get("all_seeds_failed", False):
            continue
        rt = a.get("raw_bpc_at_T1_L1_mean", float("nan"))
        if math.isfinite(rt) and abs(rt - vocab_entropy_uniform) <= DEGEN_TOL:
            degen_arms.append(arm)

    # Lift computations (PC arm vs RANK_1)
    rank1_bpc = rank1.get("bpc_best_mean", float("inf"))
    rank1_top1 = rank1.get("top1_acc_mean", -1.0)
    rank1_mrr = rank1.get("mrr_at_10_mean", -1.0)
    hp_arms = []          # HARD_PASS (top1 lift >= 0.05 OR bpc lift >= 0.05)
    mb_arms = []          # MIDDLE_BAND (top1 lift in [0.02, 0.05))
    chain_grade_arms = [] # CHAIN_GRADE_BONUS (top1 >= 0.55)
    pc_lifts: Dict[str, Dict] = {}
    for arm in PC_ARMS:
        a = by_arm_agg[arm]
        if a.get("all_seeds_failed", False):
            pc_lifts[arm] = {"all_seeds_failed": True}
            continue
        a_bpc = a["bpc_best_mean"]
        a_top1 = a["top1_acc_mean"]
        a_mrr = a["mrr_at_10_mean"]
        bpc_lift = float(rank1_bpc - a_bpc)    # positive = PC better (lower bpc)
        top1_lift = float(a_top1 - rank1_top1)  # positive = PC better
        mrr_lift = float(a_mrr - rank1_mrr)
        pc_lifts[arm] = {
            "bpc_lift": round(bpc_lift, 4),
            "top1_lift": round(top1_lift, 4),
            "mrr_lift": round(mrr_lift, 4),
        }
        # HARD_PASS: top1 lift >= HP_TOP1_LIFT OR bpc lift >= HP_BPC_LIFT
        if top1_lift >= HP_TOP1_LIFT or bpc_lift >= HP_BPC_LIFT:
            hp_arms.append(arm)
        elif top1_lift >= MB_TOP1_LIFT_MIN:
            mb_arms.append(arm)
        if a_top1 >= CHAIN_GRADE_TOP1_BAR:
            chain_grade_arms.append(arm)

    # Compose summary
    arm_lines = ["RANK_1=bpc%.3f|top1%.4f|mrr%.4f" % (
        rank1.get("bpc_best_mean", float("nan")) if not rank1.get("all_seeds_failed", False) else float("nan"),
        rank1.get("top1_acc_mean", float("nan")) if not rank1.get("all_seeds_failed", False) else float("nan"),
        rank1.get("mrr_at_10_mean", float("nan")) if not rank1.get("all_seeds_failed", False) else float("nan"),
    )]
    for a in PC_ARMS:
        x = by_arm_agg[a]
        if x.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % a)
            continue
        pl = pc_lifts.get(a, {})
        arm_lines.append("%s=bpc%.3f|top1%.4f|mrr%.4f|d_bpc%+.3f|d_top1%+.4f|d_mrr%+.4f" % (
            a, x["bpc_best_mean"], x["top1_acc_mean"], x["mrr_at_10_mean"],
            pl.get("bpc_lift", float("nan")), pl.get("top1_lift", float("nan")),
            pl.get("mrr_lift", float("nan"))))
    summary = "PC_HIERARCHY_FAIR uni=bpc%.3f|top1%.4f | %s | sanity_rail=%s | n_llm=%d" % (
        unigram_agg["bpc_mean"], unigram_agg["top1_mean"],
        " | ".join(arm_lines),
        "PASS" if sanity_ok else "FAIL(bpc=%.3f vs ref=%.3f tol=%.3f)" % (
            rank1.get("bpc_best_mean", float("nan")), RANK1_BPC_REF, SANITY_TOL),
        n_llm)

    detail = {
        "by_arm_agg": by_arm_agg,
        "pc_lifts": pc_lifts,
        "hp_arms": list(hp_arms),
        "mb_arms": list(mb_arms),
        "chain_grade_arms": list(chain_grade_arms),
        "degen_arms": list(degen_arms),
        "sanity_rail_ok": bool(sanity_ok),
        "sanity_rail_target_bpc": RANK1_BPC_REF,
        "sanity_rail_tol": SANITY_TOL,
        "rank1_bpc_observed": rank1.get("bpc_best_mean", float("nan")),
        "vocab_entropy_uniform_bits": round(vocab_entropy_uniform, 4),
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "unigram_top1_ref": UNIGRAM_TOP1_REF,
        "rank1_bpc_ref": RANK1_BPC_REF,
        "hp_top1_lift": HP_TOP1_LIFT,
        "hp_bpc_lift": HP_BPC_LIFT,
        "mb_top1_lift_min": MB_TOP1_LIFT_MIN,
        "chain_grade_top1_bar": CHAIN_GRADE_TOP1_BAR,
        "degen_tol": DEGEN_TOL,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "PC hierarchy under fair_harness rail (joint (T,lambda) sweep on dev; "
            "3 metrics: BPC + top-1 + MRR@%d). Tests USER hypothesis (2026-06-24) "
            "that hierarchy has computational reasons beyond biology. Sanity rail: "
            "ARM_RANK_1_BASELINE clears within +/- %.3f of %.4f BPC ref. "
            "HARD_PASS = any PC arm beats RANK_1 by >= %.3f top-1 OR >= %.3f BPC. "
            "MIDDLE_BAND = top-1 lift in [%.3f, %.3f). HARD_FAIL = all PC arms <= "
            "RANK_1 on all 3 metrics. CHAIN_GRADE_BONUS = any PC top-1 >= %.2f. "
            "N_DIM=%d N_TRAIN=%d N_HELD=%d V=%d sparse_f=%.3f. "
            "Resolves A12 (PC chain-grade for 5-corpus aggregation BUT degraded "
            "capacity 0.25x): tests which regime is right for LM." % (
                MRR_K, SANITY_TOL, RANK1_BPC_REF, HP_TOP1_LIFT, HP_BPC_LIFT,
                MB_TOP1_LIFT_MIN, HP_TOP1_LIFT, CHAIN_GRADE_TOP1_BAR,
                N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, SPARSE_BIPOLAR_F)),
        "what_this_does_NOT_show": (
            "f=0.05 only (doesn't test phase-shift modes; separate cell for f=0.02 "
            "if needed for direct N1 comparison). text8 only (doesn't test 5-corpus "
            "aggregation). LM lift only (no M-sweep; doesn't test capacity)."),
        "cites": [
            "preregs/2026-06-24_substrate_pc_hierarchy_fair_harness_v1.md",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
            "experiments/exp_substrate_pc_hierarchy_text8_lm_v2.py",
            "experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py",
            "cert_ledger_row_588_META_HARNESS_RIGGED_reclass",
            "USER_2026-06-24_anchor1_test_PC_hierarchy_computational",
            "USER_2026-06-23_audit_ratification_V2_LM_gap",
            "USER_2026-06-22_Fix24_GPU_must_use_GPU",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    if not sanity_ok:
        return ("HARD_FAIL",
                ("SANITY_RAIL_FAIL: ARM_RANK_1_BASELINE bpc=%.4f outside +/-%.3f of "
                 "%.4f ref. Harness drift detected -- PC arm lifts not interpretable. %s" % (
                     rank1.get("bpc_best_mean", float("nan")), SANITY_TOL,
                     RANK1_BPC_REF, summary)),
                detail)

    # Build chain-grade bonus string
    cg_str = ""
    if chain_grade_arms:
        cg_str = " CHAIN_GRADE_BONUS: arms %s achieve top1>=%.2f." % (
            chain_grade_arms, CHAIN_GRADE_TOP1_BAR)

    if hp_arms:
        hp_descr = []
        for a in hp_arms:
            pl = pc_lifts[a]
            hp_descr.append("%s d_top1=%+.3f d_bpc=%+.3f" % (
                a, pl["top1_lift"], pl["bpc_lift"]))
        return ("HARD_PASS",
                ("PC_HIERARCHY_FAIR HARD_PASS: %s clear lift bar (top1>=%.3f OR bpc>=%.3f) "
                 "vs RANK_1 baseline under fair-harness rail. PC hierarchy HAS computational "
                 "reasons beyond biology -- A12 contradiction resolved (hierarchy = LM lift "
                 "regime here, not capacity degradation regime).%s %s" % (
                     "; ".join(hp_descr), HP_TOP1_LIFT, HP_BPC_LIFT, cg_str, summary)),
                detail)

    if degen_arms:
        return ("MIDDLE_BAND",
                ("READOUT_DEGENERATE_NOT_PC_FAILURE: raw_bpc_at_T1_L1 within +/-%.2f of "
                 "uniform-vocab %.3f bits for arms=%s; PC arms not beating RANK_1 baseline "
                 "but failure is readout-degeneracy NOT PC mechanism. Requires harness "
                 "re-calibration.%s %s" % (
                     DEGEN_TOL, vocab_entropy_uniform, degen_arms, cg_str, summary)),
                detail)

    if mb_arms:
        mb_descr = []
        for a in mb_arms:
            pl = pc_lifts[a]
            mb_descr.append("%s d_top1=%+.3f" % (a, pl["top1_lift"]))
        return ("MIDDLE_BAND",
                ("PC_HIERARCHY_FAIR MIDDLE_BAND: %s top1 lift in [%.3f, %.3f) "
                 "vs RANK_1 baseline. Partial PC signal but not chain-grade.%s %s" % (
                     "; ".join(mb_descr), MB_TOP1_LIFT_MIN, HP_TOP1_LIFT, cg_str, summary)),
                detail)

    return ("HARD_FAIL",
            ("PC_HIERARCHY_FAIR HARD_FAIL: ALL PC arms fail to beat RANK_1 baseline by "
             ">=%.3f top-1 OR >=%.3f BPC under fair-harness rail. PC hierarchy DOES NOT "
             "have computational reasons beyond biology (in this regime: text8 LM lift "
             "with sparse-bipolar f=%.3f). A12 contradiction resolved DOWNWARD: hierarchy "
             "is the capacity-degradation regime, not the LM-lift regime.%s %s" % (
                 HP_TOP1_LIFT, HP_BPC_LIFT, SPARSE_BIPOLAR_F, cg_str, summary)),
            detail)


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: char-trigram bipolar
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,) and set(np.unique(v).tolist()).issubset({-1.0, 1.0})

    # T2: sparse-bipolar primitive
    E_t = torch.randn(4, 100, generator=torch.Generator().manual_seed(0))
    sp = sparsify_bipolar_gpu(E_t, 0.05, seed=0)
    k_expect = max(1, int(round(0.05 * 100)))
    nnz_per_row = (sp != 0).sum(dim=1).tolist()
    assert all(n == k_expect for n in nnz_per_row), "T2 sparse nnz; got %s" % nnz_per_row
    uniq = set(sp.unique().tolist())
    assert uniq.issubset({-1.0, 0.0, 1.0}), "T2 sparse not bipolar; got %s" % uniq

    # T3: rank-1 W builder shape + nonzero
    E_small = torch.randn(8, 16, generator=torch.Generator().manual_seed(0)).to(TORCH_DTYPE)
    idx_train_t = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 0, 1], dtype=torch.long)
    W_r1 = build_rank1_W_gpu(idx_train_t, E_small, ingest_chunk=8)
    assert W_r1.shape == (16, 16), "T3 rank-1 shape"
    assert float(W_r1.abs().sum()) > 0.0, "T3 rank-1 nonzero"

    # T4: PC layers builder shape + Ws_full = n_layers + W_pred
    Ws_full, rec = build_pc_layers_gpu(E_small, idx_train_t, n_layers=2, alpha=0.05, ingest_chunk=8)
    assert len(Ws_full) == 3, "T4 PC 2-layer should return 2 + 1 = 3 matrices, got %d" % len(Ws_full)
    for W in Ws_full:
        assert W.shape == (16, 16), "T4 PC W shape"
    # recon_err should be in [0, ~2] (normalized; >0 nontrivial)
    assert math.isfinite(rec[0]) or math.isfinite(rec[1]), "T4 PC recon_err computed"

    # T5: PC forward shape + non-degenerate (not all zeros)
    logits_t = forward_pc_layers_gpu(Ws_full, E_small, idx_train_t, recall_batch=8)
    assert logits_t.shape == (10, 8), "T5 PC fwd shape; got %s" % (logits_t.shape,)
    assert float(logits_t.abs().sum()) > 0.0, "T5 PC fwd nonzero"

    # T6: PC + cf-RPE builder runs without error
    gen6 = torch.Generator(device=torch.device("cpu"))
    gen6.manual_seed(42)
    Ws_full_cf, rec_cf = build_pc_layers_plus_cfrpe_gpu(
        E_small, idx_train_t, n_layers=2, alpha=0.05, ingest_chunk=8,
        cfrpe_lr=0.5, cfrpe_n_steps=10, cfrpe_batch=4, gen=gen6,
    )
    assert len(Ws_full_cf) == 3, "T6 PC+cfRPE should return 3 matrices"

    # T7: softmax with T peaked vs uniform
    n, V = 1, 8
    peaked_logits = np.zeros((n, V), dtype=np.float32)
    peaked_logits[0, 3] = 1.0
    probs = softmax_logits_with_T(peaked_logits, 0.01)
    assert probs.max() > 0.5, "T7 at T=0.01 should be peaked"
    probs_hot = softmax_logits_with_T(peaked_logits, 10.0)
    assert probs_hot.max() < 0.145, "T7 at T=10 should be near-uniform"

    # T8: MRR@10 planted (rank=1, 2, 3, 4, 5 -> mean reciprocal rank)
    V_t = 10
    n_t = 5
    logp_planted = np.full((n_t, V_t), -10.0, dtype=np.float64)
    nxt_t = np.array([3, 0, 9, 5, 2])
    expected_ranks = [1, 2, 3, 4, 5]
    for i, (true_cls, want_rank) in enumerate(zip(nxt_t, expected_ranks)):
        scores = np.arange(V_t, dtype=np.float64)
        np.random.default_rng(i).shuffle(scores)
        sorted_idx = np.argsort(-scores)
        cur_top_at_rank = sorted_idx[want_rank - 1]
        tmp = scores[true_cls]
        scores[true_cls] = scores[cur_top_at_rank]
        scores[cur_top_at_rank] = tmp
        logp_planted[i] = scores
    mrr_val = mrr_at_k(logp_planted, nxt_t, 10)
    expected_mrr = float(np.mean([1.0 / r for r in expected_ranks]))
    assert abs(mrr_val - expected_mrr) < 1e-6, "T8 MRR: %.4f vs %.4f" % (mrr_val, expected_mrr)

    # T9: verdict band classification (HP / MB / HF / SANITY_FAIL / DEGEN)
    def _mk_unit(by_arm_data, V=4000, sanity_bpc=RANK1_BPC_REF):
        by_arm = {"ARM_UNIGRAM_REF": {"bpc_unigram": 7.738, "top1_unigram": 0.2171,
                                         "mrr_unigram": 0.30, "n_test": 100}}
        # RANK_1 at sanity_bpc by default
        if "ARM_RANK_1_BASELINE" not in by_arm_data:
            by_arm_data["ARM_RANK_1_BASELINE"] = {
                "bpc_best": sanity_bpc, "top1_acc": 0.40, "mrr_at_10": 0.45,
                "best_T_for_bpc": 0.1, "best_lambda_for_bpc": 0.3, "best_dev_bpc": sanity_bpc,
                "best_T_for_top1": 0.1, "best_lambda_for_top1": 0.3,
                "best_T_for_mrr": 0.1, "best_lambda_for_mrr": 0.3,
                "raw_bpc_at_T1_L1": sanity_bpc, "raw_top1_at_T1_L1": 0.40,
                "raw_mrr_at_T1_L1": 0.45, "n_dev": 100, "n_test": 100, "grid_size": 35,
            }
        for arm in ARMS:
            if arm not in by_arm_data:
                # Default: PC arm tied with RANK_1 (no lift => HF)
                by_arm_data[arm] = {
                    "bpc_best": sanity_bpc, "top1_acc": 0.40, "mrr_at_10": 0.45,
                    "best_T_for_bpc": 0.1, "best_lambda_for_bpc": 0.3, "best_dev_bpc": sanity_bpc,
                    "best_T_for_top1": 0.1, "best_lambda_for_top1": 0.3,
                    "best_T_for_mrr": 0.1, "best_lambda_for_mrr": 0.3,
                    "raw_bpc_at_T1_L1": sanity_bpc, "raw_top1_at_T1_L1": 0.40,
                    "raw_mrr_at_T1_L1": 0.45, "n_dev": 100, "n_test": 100, "grid_size": 35,
                }
            by_arm[arm] = by_arm_data[arm]
        return {"seed": 0, "by_arm": by_arm, "V": V, "N": 64, "N_DIM": 64,
                  "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": V, "PRETRAIN_DIM": 10,
                  "run_mode": "smoke", "config_version": "selftest",
                  "elapsed_s_seed": 0.01, "device": "cpu", "n_llm_calls": 0}

    # HARD_PASS: PC_2LEVEL top1 lift = 0.46 - 0.40 = 0.06 (>= HP_TOP1_LIFT=0.05)
    u_hp = _mk_unit({"ARM_PC_HIERARCHY_2LEVEL": {
        "bpc_best": RANK1_BPC_REF, "top1_acc": 0.46, "mrr_at_10": 0.45,
        "best_T_for_bpc": 0.1, "best_lambda_for_bpc": 0.3, "best_dev_bpc": RANK1_BPC_REF,
        "best_T_for_top1": 0.1, "best_lambda_for_top1": 0.3,
        "best_T_for_mrr": 0.1, "best_lambda_for_mrr": 0.3,
        "raw_bpc_at_T1_L1": RANK1_BPC_REF, "raw_top1_at_T1_L1": 0.46,
        "raw_mrr_at_T1_L1": 0.45, "n_dev": 100, "n_test": 100, "grid_size": 35,
    }})
    v, m, d = compute_verdict([u_hp, u_hp, u_hp])
    assert v == "HARD_PASS", "T9 HP got %s msg=%s" % (v, m[:200])
    assert "ARM_PC_HIERARCHY_2LEVEL" in d["hp_arms"], "T9 HP arm"

    # MIDDLE_BAND: PC_2LEVEL top1 lift = 0.43 - 0.40 = 0.03 (in [0.02, 0.05))
    u_mb = _mk_unit({"ARM_PC_HIERARCHY_2LEVEL": {
        "bpc_best": RANK1_BPC_REF, "top1_acc": 0.43, "mrr_at_10": 0.45,
        "best_T_for_bpc": 0.1, "best_lambda_for_bpc": 0.3, "best_dev_bpc": RANK1_BPC_REF,
        "best_T_for_top1": 0.1, "best_lambda_for_top1": 0.3,
        "best_T_for_mrr": 0.1, "best_lambda_for_mrr": 0.3,
        "raw_bpc_at_T1_L1": RANK1_BPC_REF, "raw_top1_at_T1_L1": 0.43,
        "raw_mrr_at_T1_L1": 0.45, "n_dev": 100, "n_test": 100, "grid_size": 35,
    }})
    v, m, d = compute_verdict([u_mb, u_mb, u_mb])
    assert v == "MIDDLE_BAND", "T9 MB got %s msg=%s" % (v, m[:200])
    assert "ARM_PC_HIERARCHY_2LEVEL" in d["mb_arms"], "T9 MB arm"

    # SANITY_RAIL_FAIL: RANK_1 bpc 7.40 (outside +/- 0.05 of 7.3065)
    u_san = _mk_unit({}, sanity_bpc=7.40)
    v, m, _ = compute_verdict([u_san, u_san, u_san])
    assert v == "HARD_FAIL" and "SANITY_RAIL_FAIL" in m, "T9 SANITY got %s msg=%s" % (v, m[:200])

    # HARD_FAIL: all PC tied with RANK_1 (sanity OK, all lifts = 0)
    u_hf = _mk_unit({})
    v, m, _ = compute_verdict([u_hf, u_hf, u_hf])
    assert v == "HARD_FAIL" and "PC_HIERARCHY_FAIR HARD_FAIL" in m, "T9 HF got %s msg=%s" % (v, m[:200])

    # CHAIN_GRADE_BONUS: PC top1 = 0.60 (>= 0.55)
    u_cg = _mk_unit({"ARM_PC_HIERARCHY_2LEVEL": {
        "bpc_best": RANK1_BPC_REF - 0.10, "top1_acc": 0.60, "mrr_at_10": 0.65,
        "best_T_for_bpc": 0.1, "best_lambda_for_bpc": 0.3, "best_dev_bpc": RANK1_BPC_REF - 0.10,
        "best_T_for_top1": 0.1, "best_lambda_for_top1": 0.3,
        "best_T_for_mrr": 0.1, "best_lambda_for_mrr": 0.3,
        "raw_bpc_at_T1_L1": RANK1_BPC_REF - 0.10, "raw_top1_at_T1_L1": 0.60,
        "raw_mrr_at_T1_L1": 0.65, "n_dev": 100, "n_test": 100, "grid_size": 35,
    }})
    v, m, d = compute_verdict([u_cg, u_cg, u_cg])
    assert v == "HARD_PASS", "T9 CG got %s msg=%s" % (v, m[:200])
    assert "ARM_PC_HIERARCHY_2LEVEL" in d["chain_grade_arms"], "T9 CG bonus"

    # T10: LLM call counter zero
    assert _LLM_CALL_COUNTER[0] == 0, "T10 llm counter"

    print("[selftest] PASS: T1 trigram + T2 sparse-bipolar + T3 rank-1 W "
          "+ T4 PC layers + T5 PC fwd + T6 PC+cfRPE + T7 softmax T "
          "+ T8 MRR planted + T9 verdict bands (HP/MB/SANITY/HF/CG) + T10 llm=0",
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
            "anchor_name": ANCHOR_NAME,
            "anchor": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "N": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "PRETRAIN_DIM": PRETRAIN_DIM,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_substrate_pc_hierarchy_fair_harness_v1",
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
          "seeds=%s arms=%s | name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
              SEEDS, ARMS, _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
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
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM, "schema": "pc-hierarchy-fair-v1"}
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
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "N_DIM": N_DIM,
        "N": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH,
        "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID,
        "MRR_K": MRR_K,
        "arms": ARMS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_gpu_substrate_pc_hierarchy_fair_harness_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate cosine logits; word2vec is static open-weight lookup; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
