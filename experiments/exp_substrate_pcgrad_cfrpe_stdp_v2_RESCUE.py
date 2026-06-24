"""
substrate_pcgrad_cfrpe_stdp_v2_RESCUE
-- Rescue of v1 which TIMED OUT at 5400s without producing metrics (full scope:
   N_DIM=8192, N_TRAIN=100k, 3 seeds, 4 arms x 1000 steps was ~6-9h matmul-bound).

   Scope reduction (Option A per dispatch spec): N_DIM=4096, N_TRAIN=50k,
   N_HELD=10k. N_STEPS=1000 PRESERVED (PCGrad/GCond projection convergence
   bound). 3 seeds, 4 arms unchanged. Provenance rails to A1 (calibrated at
   N_DIM=8192/N_TRAIN=100k) DISABLED at this scope - intra-cell PCGRAD-vs-NAIVE
   delta IS the discriminator.

ANCHOR 1 (MH beta-sweep) HARD_FAIL_STRUCTURAL. H1 (gradient conflict between
cf-RPE and STDP heterogeneous plasticity) elevated to load-bearing hypothesis.

PCGrad (Yu et al. 2020, arxiv 2001.06782): cf-RPE and STDP have conflicting
gradients on the same W; projection of STDP onto orthogonal component of cf-RPE
may rescue the -0.116 reversal observed in A1 (ARM_+STDP arm reversed ARM_+CFRPE
gain, 3/3 seeds).

GCond variant (arXiv:2509.07252): accumulation-based stabilization.
Discriminates PCGrad-class (projection) vs broader gradient-conflict-class.

FOUR ARMS (3 seeds, text8 N_TRAIN=50k, N_DIM=4096):
  ARM_CFRPE_ONLY                -- cf-RPE delta-rule only (intra-cell control)
  ARM_CFRPE_PLUS_STDP_NAIVE     -- additive composition (reproduces A1 collapse)
  ARM_CFRPE_PLUS_STDP_PCGRAD    -- PCGrad surgery: if <g_cf, g_stdp> < 0, project
                                   g_stdp onto orthogonal complement of g_cf
  ARM_CFRPE_PLUS_STDP_GCOND     -- GCond stabilization: accumulated-magnitude
                                   reweighting of g_stdp when conflicting

PRE-REG HARD bands (USER-spec; held identical to v1):

  HARD_PASS chain-grade-eligible:
    ARM_PCGRAD or ARM_GCOND BPC <= 7.05
    -> PCGrad/GCond rescues hetplast collapse; gradient-conflict IS first-order
       cause; fixable without architecture change

  MIDDLE_BAND:
    ARM_PCGRAD BPC in (7.05, 7.20)
    -> partial PCGrad help; conflict is contributing but not sole

  HARD_FAIL:
    ARM_PCGRAD BPC >= 7.20
    -> gradient projection doesn't help; H1 refuted; structural diagnosis stands

  cv <= 0.05 across seeds for PCGRAD arm mandatory (Fix #28 cv discipline)

  NOTE: absolute bands calibrated to v1 scope (N_DIM=8192/N_TRAIN=100k).
  At v2_RESCUE scope these absolute floors may not be the right threshold -
  surface absolute BPC AND relative lift PCGRAD-vs-NAIVE so cert-owner can tier
  with full per-arm visibility. Provenance rails to A1 (7.0888 / 7.2044) are
  DISABLED at this scope - intra-cell PCGRAD-vs-NAIVE delta is load-bearing.

GRADIENT-COSINE INSTRUMENTATION (Fix #28 per-arm metrics + verify conflict):
  Per arm with STDP, log cosine(g_cf, g_stdp) per step (sampled at strides of 50
  for SNR/storage tradeoff). Per-arm: mean cosine, frac_conflicting (cos<0),
  accumulated magnitudes, PCGrad-projection-norm.

CONFIG:
  N_DIM=4096, V=4000, text8 N_TRAIN=50k, 3 seeds, word2vec sparse-bipolar f=0.05.
  Routing: remote_cpu_queue (matmul-bound numpy; remote CPU has slot).

CITES:
  notes/research_composition_collapse_critical_drill_2026-06-24.md (ANCHOR 2 spec)
  experiments/exp_substrate_pcgrad_cfrpe_stdp_v1.py (timed out at 5400s; same arms)
  experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py (A1 reference)
  arxiv.org/abs/2001.06782 (Yu et al. PCGrad)
  arXiv:2509.07252 (GCond gradient conflict resolution)
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

import argparse
import hashlib
import math
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics,
    resumable_seeds as _resumable_seeds,
)

ANCHOR_NAME = "substrate_pcgrad_cfrpe_stdp_v2_RESCUE"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only audit counter
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Pre-reg threshold bands (pre-registered; do NOT modify post-smoke)
# ============================================================================
# Provenance rails (cumulative-check: each arm reproduces its A1 reference)
SANITY_RAIL_CFRPE_REF = 7.0888         # A1 ARM_+CFRPE / cf-RPE-only baseline
SANITY_RAIL_HETPLAST_REF = 7.2044      # A1 ARM_+STDP / NAIVE hetplast collapse
SANITY_RAIL_TOLERANCE = 0.05

# PCGrad / GCond verdict bands (on ARM_PCGRAD / ARM_GCOND BPC)
HARD_PASS_BPC_CEILING = 7.05           # rescue threshold
MIDDLE_BAND_BPC_LOWER = 7.05
MIDDLE_BAND_BPC_UPPER = 7.20
HARD_FAIL_BPC_FLOOR = 7.20             # at/above this floor = HARD_FAIL
CV_MAX = 0.05                          # cv mandatory across seeds

# ============================================================================
# Primitive knob parameters (frozen from A1 cell for provenance)
# ============================================================================
CFRPE_LR = 0.5
STDP_WEIGHT = 0.5
INGEST_BATCH = 64
N_STEPS_PER_SEED = 1000

# Gradient-cosine instrumentation
COSINE_STRIDE = 50                     # sample every 50 steps

# Modern-Hopfield cleanup -- OMITTED in this cell (per ANCHOR 2 design):
# ANCHOR 1 already HARD_FAIL_STRUCTURAL on MH; we isolate cf-RPE + STDP only.

# Eval hyperparameter grids
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Encoder
SPARSE_BIPOLAR_F = 0.05
WORD2VEC_MODEL = "word2vec-google-news-300"
PRETRAIN_DIM = 300

# Arms (4-arm ANCHOR 2)
ARMS = [
    "ARM_CFRPE_ONLY",
    "ARM_CFRPE_PLUS_STDP_NAIVE",
    "ARM_CFRPE_PLUS_STDP_PCGRAD",
    "ARM_CFRPE_PLUS_STDP_GCOND",
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

# ============================================================================
# Production config (v2_RESCUE scope reduction: 1/8 cost vs v1)
# ============================================================================
N_DIM = 4096                     # was 8192 in v1 (matmul cost ~1/4)
VOCAB_CAP = 4000
RECALL_BATCH = 256
INGEST_CHUNK = 4096

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 50_000             # was 100_000 in v1 (1/2 pool)
    N_HELD = 10_000              # was 20_000 in v1 (1/2 recall cost)
    N_STEPS = N_STEPS_PER_SEED   # 1000 steps PRESERVED - PCGrad/GCond
                                  # projection convergence is step-count-bound,
                                  # not corpus-size-bound
else:
    # Smoke: clean synthetic data + minimal config (per memory rule:
    # smoke tests must use clean synthetic data, NOT substrate state).
    # Goal: fit under 180s on CPU; exercise every arm + PCGrad + GCond paths.
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 1024
    N_STEPS = 80
    RECALL_BATCH = 128
    INGEST_CHUNK = 512

CONFIG_VERSION = (
    "%s; encoder=word2vec_sparse_bipolar_f%.3f; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s temps=%s lambdas=%s "
    "cfrpe_lr=%.3f stdp_w=%.3f n_steps=%d batch=%d cosine_stride=%d"
) % (
    ANCHOR_NAME, SPARSE_BIPOLAR_F, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
    ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID,
    CFRPE_LR, STDP_WEIGHT, N_STEPS, INGEST_BATCH, COSINE_STRIDE,
)


# ============================================================================
# text8 corpus utilities (verbatim from A1 cell)
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
# Encoder: word2vec-projected sparse-bipolar (matches A1 chain-grade)
# ============================================================================

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


def build_E_word2vec(vocab: List[str], n_dim: int, seed: int) -> Tuple[np.ndarray, Dict]:
    """word2vec(300) -> Gaussian-project(300 -> n_dim) -> L2 normalize. OOV -> char-trigram.

    Matches A1 encoder pipeline EXACTLY (provenance).
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
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_proj, meta


def build_E_synthetic_smoke(V: int, n_dim: int, seed: int) -> Tuple[np.ndarray, Dict]:
    """Clean synthetic encoder for smoke (per memory rule: NO substrate state)."""
    rng = np.random.default_rng(seed * 9173 + 11)
    E_np = rng.standard_normal((V, n_dim)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    meta = {"n_hit": int(V), "n_miss": 0, "n_vocab": int(V),
            "pretrain_dim": int(n_dim), "synthetic_smoke": True}
    return E_np, meta


def sparsify_bipolar_np(E: np.ndarray, f: float) -> np.ndarray:
    """Sparse-bipolar projection (top-k by abs, sign-encode). Numpy port of A1 GPU primitive."""
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    abs_E = np.abs(E)
    # top-k indices per row
    topk_idx = np.argpartition(-abs_E, kth=k - 1, axis=1)[:, :k]
    out = np.zeros_like(E)
    row_idx = np.arange(V)[:, None]
    signs = np.sign(E[row_idx, topk_idx])
    signs[signs == 0] = 1.0
    out[row_idx, topk_idx] = signs
    return out


# ============================================================================
# Plasticity gradient computers (per-step, numpy)
# ============================================================================
# Each computes dW from a single batch sample. cf-RPE = delta-rule (task axis),
# STDP = antisymmetric outer (temporal axis). Returns gradients NOT applied.

def cfrpe_gradient(W: np.ndarray, Ctx: np.ndarray, Nxt: np.ndarray,
                   batch: int) -> np.ndarray:
    """cf-RPE gradient: dW = (Nxt - Ctx @ W^T)^T @ Ctx / batch"""
    error = Nxt - Ctx @ W.T
    return (error.T @ Ctx) / float(batch)


def stdp_gradient(Ctx: np.ndarray, Nxt: np.ndarray, batch: int) -> np.ndarray:
    """STDP antisymmetric gradient: dW = (Nxt^T @ Ctx - Ctx^T @ Nxt) / batch"""
    return (Nxt.T @ Ctx - Ctx.T @ Nxt) / float(batch)


def grad_cosine(g1: np.ndarray, g2: np.ndarray, eps: float = 1e-12) -> float:
    """Cosine between two gradient matrices (flatten Frobenius inner product)."""
    f1 = g1.ravel()
    f2 = g2.ravel()
    n1 = float(np.linalg.norm(f1))
    n2 = float(np.linalg.norm(f2))
    if n1 < eps or n2 < eps:
        return 0.0
    return float(np.dot(f1, f2) / (n1 * n2))


def pcgrad_project(g_stdp: np.ndarray, g_cf: np.ndarray,
                   eps: float = 1e-12) -> Tuple[np.ndarray, bool, float]:
    """PCGrad (Yu et al. 2020): project g_stdp onto orthogonal complement of g_cf
    IFF they conflict (cosine < 0).

    Returns (g_stdp_proj, was_projected, projection_norm).
    """
    f_stdp = g_stdp.ravel()
    f_cf = g_cf.ravel()
    cf_norm_sq = float(np.dot(f_cf, f_cf))
    if cf_norm_sq < eps:
        return g_stdp, False, 0.0
    inner = float(np.dot(f_stdp, f_cf))
    if inner >= 0.0:
        # No conflict; STDP keeps its full gradient
        return g_stdp, False, 0.0
    # Conflict: subtract projection onto g_cf
    proj_coef = inner / cf_norm_sq
    g_stdp_proj = g_stdp - proj_coef * g_cf
    proj_norm = float(abs(proj_coef) * np.linalg.norm(f_cf))
    return g_stdp_proj, True, proj_norm


def gcond_stabilize(g_stdp: np.ndarray, g_cf: np.ndarray,
                    accum_mag_stdp: float, accum_mag_cf: float,
                    eps: float = 1e-12) -> Tuple[np.ndarray, bool, float]:
    """GCond (arXiv:2509.07252): accumulation-based stabilization.

    Variant tested here: when conflicting (cos<0), rescale g_stdp by
    min(1, accum_mag_cf / accum_mag_stdp) so STDP's effective magnitude
    cannot dominate when its accumulated contribution already exceeds cf-RPE's.
    This prevents the STDP signal from overpowering cf-RPE when accumulation
    has unbalanced the two streams.

    Returns (g_stdp_stabilized, was_rescaled, rescale_factor).
    """
    f_stdp = g_stdp.ravel()
    f_cf = g_cf.ravel()
    inner = float(np.dot(f_stdp, f_cf))
    if inner >= 0.0:
        return g_stdp, False, 1.0
    if accum_mag_stdp < eps:
        return g_stdp, False, 1.0
    # Rescale STDP gradient to not exceed cf-RPE's accumulated magnitude
    factor = min(1.0, accum_mag_cf / max(accum_mag_stdp, eps))
    return g_stdp * factor, True, factor


# ============================================================================
# Arm trainers (each returns W + per-arm instrumentation)
# ============================================================================

def train_W_cfrpe_only(E: np.ndarray, idx_train: np.ndarray, n_steps: int,
                       batch: int, lr: float, seed: int, arm_idx: int) -> Dict:
    """ARM_CFRPE_ONLY: cf-RPE delta-rule only. Provenance rail for 7.0888."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + arm_idx * 31337)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return {"W": W, "cosine_samples": [], "n_conflict": 0, "n_steps_logged": 0}
    for s in range(n_steps):
        st = rng.integers(0, n_pairs, size=batch)
        Ctx = E[idx_train[st]]
        Nxt = E[idx_train[st + 1]]
        g_cf = cfrpe_gradient(W, Ctx, Nxt, batch)
        W = W + lr * g_cf
    return {"W": W, "cosine_samples": [], "n_conflict": 0, "n_steps_logged": 0,
            "accum_mag_cf": float(np.linalg.norm(W)),
            "accum_mag_stdp": 0.0}


def train_W_cfrpe_stdp_naive(E: np.ndarray, idx_train: np.ndarray, n_steps: int,
                              batch: int, lr: float, stdp_w: float,
                              seed: int, arm_idx: int) -> Dict:
    """ARM_CFRPE_PLUS_STDP_NAIVE: dW = dW_cf + stdp_w * dW_stdp; provenance for 7.2044."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + arm_idx * 31337)
    n_pairs = idx_train.shape[0] - 1
    cosine_samples: List[float] = []
    n_conflict = 0
    n_steps_logged = 0
    accum_mag_cf = 0.0
    accum_mag_stdp = 0.0
    if n_pairs <= 0:
        return {"W": W, "cosine_samples": [], "n_conflict": 0, "n_steps_logged": 0,
                "accum_mag_cf": 0.0, "accum_mag_stdp": 0.0}
    for s in range(n_steps):
        st = rng.integers(0, n_pairs, size=batch)
        Ctx = E[idx_train[st]]
        Nxt = E[idx_train[st + 1]]
        g_cf = cfrpe_gradient(W, Ctx, Nxt, batch)
        g_stdp = stdp_gradient(Ctx, Nxt, batch)
        accum_mag_cf += float(np.linalg.norm(g_cf))
        accum_mag_stdp += float(np.linalg.norm(g_stdp))
        if s % COSINE_STRIDE == 0:
            cos = grad_cosine(g_cf, g_stdp)
            cosine_samples.append(cos)
            n_steps_logged += 1
            if cos < 0.0:
                n_conflict += 1
        dW = g_cf + stdp_w * g_stdp
        W = W + lr * dW
    return {"W": W, "cosine_samples": cosine_samples,
            "n_conflict": n_conflict, "n_steps_logged": n_steps_logged,
            "accum_mag_cf": accum_mag_cf, "accum_mag_stdp": accum_mag_stdp}


def train_W_cfrpe_stdp_pcgrad(E: np.ndarray, idx_train: np.ndarray, n_steps: int,
                                batch: int, lr: float, stdp_w: float,
                                seed: int, arm_idx: int) -> Dict:
    """ARM_CFRPE_PLUS_STDP_PCGRAD: PCGrad surgery (Yu et al. 2020).

    For each step: compute g_cf and g_stdp; if conflicting, project g_stdp
    onto orthogonal complement of g_cf. Apply g_cf + stdp_w * g_stdp_proj.
    """
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + arm_idx * 31337)
    n_pairs = idx_train.shape[0] - 1
    cosine_samples: List[float] = []
    n_conflict = 0
    n_projected = 0
    n_steps_logged = 0
    sum_proj_norm = 0.0
    accum_mag_cf = 0.0
    accum_mag_stdp = 0.0
    if n_pairs <= 0:
        return {"W": W, "cosine_samples": [], "n_conflict": 0, "n_projected": 0,
                "n_steps_logged": 0, "sum_proj_norm": 0.0,
                "accum_mag_cf": 0.0, "accum_mag_stdp": 0.0}
    for s in range(n_steps):
        st = rng.integers(0, n_pairs, size=batch)
        Ctx = E[idx_train[st]]
        Nxt = E[idx_train[st + 1]]
        g_cf = cfrpe_gradient(W, Ctx, Nxt, batch)
        g_stdp = stdp_gradient(Ctx, Nxt, batch)
        accum_mag_cf += float(np.linalg.norm(g_cf))
        accum_mag_stdp += float(np.linalg.norm(g_stdp))
        g_stdp_proj, was_projected, proj_norm = pcgrad_project(g_stdp, g_cf)
        if was_projected:
            n_projected += 1
            sum_proj_norm += proj_norm
        if s % COSINE_STRIDE == 0:
            cos = grad_cosine(g_cf, g_stdp)
            cosine_samples.append(cos)
            n_steps_logged += 1
            if cos < 0.0:
                n_conflict += 1
        dW = g_cf + stdp_w * g_stdp_proj
        W = W + lr * dW
    return {"W": W, "cosine_samples": cosine_samples,
            "n_conflict": n_conflict, "n_projected": n_projected,
            "n_steps_logged": n_steps_logged, "sum_proj_norm": sum_proj_norm,
            "accum_mag_cf": accum_mag_cf, "accum_mag_stdp": accum_mag_stdp}


def train_W_cfrpe_stdp_gcond(E: np.ndarray, idx_train: np.ndarray, n_steps: int,
                              batch: int, lr: float, stdp_w: float,
                              seed: int, arm_idx: int) -> Dict:
    """ARM_CFRPE_PLUS_STDP_GCOND: GCond stabilization variant.

    For each step: compute g_cf, g_stdp; if conflicting, rescale g_stdp by
    min(1, accum_mag_cf / accum_mag_stdp) so STDP cannot overpower cf-RPE.
    """
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    rng = np.random.default_rng(seed * 10007 + arm_idx * 31337)
    n_pairs = idx_train.shape[0] - 1
    cosine_samples: List[float] = []
    n_conflict = 0
    n_rescaled = 0
    n_steps_logged = 0
    accum_mag_cf = 0.0
    accum_mag_stdp = 0.0
    rescale_factors: List[float] = []
    if n_pairs <= 0:
        return {"W": W, "cosine_samples": [], "n_conflict": 0, "n_rescaled": 0,
                "n_steps_logged": 0, "mean_rescale": 1.0,
                "accum_mag_cf": 0.0, "accum_mag_stdp": 0.0}
    for s in range(n_steps):
        st = rng.integers(0, n_pairs, size=batch)
        Ctx = E[idx_train[st]]
        Nxt = E[idx_train[st + 1]]
        g_cf = cfrpe_gradient(W, Ctx, Nxt, batch)
        g_stdp = stdp_gradient(Ctx, Nxt, batch)
        accum_mag_cf += float(np.linalg.norm(g_cf))
        accum_mag_stdp += float(np.linalg.norm(g_stdp))
        g_stdp_stab, was_rescaled, factor = gcond_stabilize(
            g_stdp, g_cf, accum_mag_stdp, accum_mag_cf)
        if was_rescaled:
            n_rescaled += 1
            rescale_factors.append(factor)
        if s % COSINE_STRIDE == 0:
            cos = grad_cosine(g_cf, g_stdp)
            cosine_samples.append(cos)
            n_steps_logged += 1
            if cos < 0.0:
                n_conflict += 1
        dW = g_cf + stdp_w * g_stdp_stab
        W = W + lr * dW
    mean_rescale = (float(np.mean(rescale_factors)) if rescale_factors else 1.0)
    return {"W": W, "cosine_samples": cosine_samples,
            "n_conflict": n_conflict, "n_rescaled": n_rescaled,
            "n_steps_logged": n_steps_logged, "mean_rescale": mean_rescale,
            "accum_mag_cf": accum_mag_cf, "accum_mag_stdp": accum_mag_stdp}


# ============================================================================
# Logits builder (numpy, chunked)
# ============================================================================

def compute_logits(W: np.ndarray, E: np.ndarray, idx_held: np.ndarray,
                   recall_batch: int) -> np.ndarray:
    """Compute [n_h, V] logits: pred = E[ctx] @ W^T (L2 normed); logits = pred @ E^T."""
    V, dim = E.shape
    n_h = idx_held.shape[0]
    logits = np.zeros((n_h, V), dtype=np.float32)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E[idx_held[b:end]]
        pred = ctx_b @ W.T
        pred_n = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-12)
        logits[b:end] = (pred_n @ E.T).astype(np.float32)
    return logits


# ============================================================================
# BPC / eval utilities (verbatim from A1)
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
    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
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
# Arm dispatch
# ============================================================================

ARM_TRAINERS = {
    "ARM_CFRPE_ONLY": train_W_cfrpe_only,
    "ARM_CFRPE_PLUS_STDP_NAIVE": train_W_cfrpe_stdp_naive,
    "ARM_CFRPE_PLUS_STDP_PCGRAD": train_W_cfrpe_stdp_pcgrad,
    "ARM_CFRPE_PLUS_STDP_GCOND": train_W_cfrpe_stdp_gcond,
}


# ============================================================================
# Instrumentation self-test (MANDATORY; per memory rule: assert measured values
# match expected BEFORE dispatch)
# ============================================================================

def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)

    # ST1: cf-RPE delta shrinks prediction error
    n_dim_st = 64
    rng_st = np.random.default_rng(42)
    Ctx_np = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Nxt_np = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Ctx_np /= np.linalg.norm(Ctx_np) + 1e-8
    Nxt_np /= np.linalg.norm(Nxt_np) + 1e-8
    W_test = np.zeros((n_dim_st, n_dim_st), dtype=np.float32)
    err_before = float(np.linalg.norm(Nxt_np - Ctx_np @ W_test.T))
    g_cf = cfrpe_gradient(W_test, Ctx_np, Nxt_np, batch=1)
    W_test = W_test + 0.9 * g_cf
    err_after = float(np.linalg.norm(Nxt_np - Ctx_np @ W_test.T))
    assert err_after < err_before, (
        "ST1 cf-RPE should shrink error: before=%.4f after=%.4f" % (err_before, err_after))
    print("[selftest] ST1 cf-RPE shrinks error: %.4f -> %.4f" % (err_before, err_after), flush=True)

    # ST2: STDP antisymmetry: dW_stdp + dW_stdp^T == 0
    b_st = 4
    rng2 = np.random.default_rng(7)
    Ctx2 = rng2.standard_normal((b_st, n_dim_st)).astype(np.float32)
    Nxt2 = rng2.standard_normal((b_st, n_dim_st)).astype(np.float32)
    g_stdp = stdp_gradient(Ctx2, Nxt2, batch=b_st)
    antisym_err = float(np.abs(g_stdp + g_stdp.T).max())
    assert antisym_err < 1e-4, "ST2 STDP antisymmetry failed: %.4e" % antisym_err
    print("[selftest] ST2 STDP antisymmetry OK (err=%.2e)" % antisym_err, flush=True)

    # ST3: cosine of identical gradients = 1.0
    g_self_cos = grad_cosine(Ctx2, Ctx2)
    assert abs(g_self_cos - 1.0) < 1e-5, "ST3 self-cosine should be 1.0: %.4f" % g_self_cos
    # Cosine of orthogonal: build pair
    A = np.zeros((4, 4), dtype=np.float32)
    A[0, 0] = 1.0
    B = np.zeros((4, 4), dtype=np.float32)
    B[1, 1] = 1.0
    orth_cos = grad_cosine(A, B)
    assert abs(orth_cos) < 1e-5, "ST3 orthogonal cosine should be 0: %.4f" % orth_cos
    print("[selftest] ST3 cosine sanity (self=%.4f, orth=%.4f) OK" % (g_self_cos, orth_cos), flush=True)

    # ST4: PCGrad projects iff conflicting; after projection, cosine with g_cf >= 0
    g_cf_t = np.array([[1.0, 0.0], [0.0, 0.0]], dtype=np.float32)
    g_stdp_conflict = np.array([[-0.5, 0.0], [0.0, 1.0]], dtype=np.float32)
    g_proj, was_projected, proj_norm = pcgrad_project(g_stdp_conflict, g_cf_t)
    assert was_projected, "ST4 PCGrad should project on conflict"
    cos_after = grad_cosine(g_proj, g_cf_t)
    assert cos_after >= -1e-5, "ST4 after projection cosine with g_cf should be >= 0: %.4f" % cos_after
    print("[selftest] ST4 PCGrad project on conflict OK (cos_after=%.4f, proj_norm=%.4f)" % (
        cos_after, proj_norm), flush=True)

    # ST4b: PCGrad does NOT project when not conflicting
    g_stdp_aligned = np.array([[0.5, 0.0], [0.0, 1.0]], dtype=np.float32)
    g_proj_a, was_projected_a, _ = pcgrad_project(g_stdp_aligned, g_cf_t)
    assert not was_projected_a, "ST4b PCGrad should NOT project when aligned"
    assert np.allclose(g_proj_a, g_stdp_aligned), "ST4b non-projected should be identity"
    print("[selftest] ST4b PCGrad no-op when aligned OK", flush=True)

    # ST5: GCond rescales iff conflicting + STDP magnitude exceeds cf-RPE
    g_stdp_big = np.array([[-2.0, 0.0], [0.0, 1.0]], dtype=np.float32)
    g_stab, was_rescaled, factor = gcond_stabilize(
        g_stdp_big, g_cf_t, accum_mag_stdp=10.0, accum_mag_cf=1.0)
    assert was_rescaled, "ST5 GCond should rescale on conflict"
    assert 0.0 < factor < 1.0, "ST5 GCond factor should be in (0, 1): %.4f" % factor
    print("[selftest] ST5 GCond rescales on conflict OK (factor=%.4f)" % factor, flush=True)

    # ST5b: GCond no-op when aligned
    _, was_rescaled_a, _ = gcond_stabilize(
        g_stdp_aligned, g_cf_t, accum_mag_stdp=10.0, accum_mag_cf=1.0)
    assert not was_rescaled_a, "ST5b GCond no-op when aligned"
    print("[selftest] ST5b GCond no-op when aligned OK", flush=True)

    # ST6: each arm trainer returns non-zero W for non-trivial training
    V_st = 10
    n_dim_s2 = 64
    rng3 = np.random.default_rng(0)
    E_np = rng3.standard_normal((V_st, n_dim_s2)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_sb = _l2_normalize_np(sparsify_bipolar_np(E_np, SPARSE_BIPOLAR_F))
    idx_tr_st = np.array([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=np.int64)
    for arm_name, trainer in ARM_TRAINERS.items():
        res = trainer(E_sb, idx_tr_st, n_steps=10, batch=3,
                      lr=0.5, **({"stdp_w": 0.5}
                                  if arm_name != "ARM_CFRPE_ONLY" else {}),
                      seed=0, arm_idx=0)
        W_arm = res["W"]
        assert W_arm.shape == (n_dim_s2, n_dim_s2), (
            "ST6 %s W shape mismatch: %s" % (arm_name, str(W_arm.shape)))
        assert not np.all(W_arm == 0.0), "ST6 %s W all zero" % arm_name
        print("[selftest] ST6 %s W shape=%s non-zero OK" % (arm_name, str(W_arm.shape)),
              flush=True)

    # ST7: PCGrad arm cos_samples track conflict (rough check: at least one sample)
    res_pc = train_W_cfrpe_stdp_pcgrad(E_sb, idx_tr_st, n_steps=COSINE_STRIDE + 5,
                                          batch=3, lr=0.5, stdp_w=0.5, seed=0, arm_idx=0)
    assert res_pc["n_steps_logged"] >= 1, "ST7 PCGrad should log at least 1 cosine sample"
    print("[selftest] ST7 PCGrad logs cosine samples: n_logged=%d, n_conflict=%d, n_projected=%d" % (
        res_pc["n_steps_logged"], res_pc["n_conflict"], res_pc["n_projected"]), flush=True)

    # ST8: compute_logits produces non-zero logits + correct shape
    W_st = res_pc["W"]
    idx_h_st = np.array([3, 4, 5, 6], dtype=np.int64)
    logits_st = compute_logits(W_st, E_sb, idx_h_st, recall_batch=4)
    assert logits_st.shape == (4, V_st), (
        "ST8 logits shape mismatch: %s" % str(logits_st.shape))
    assert not np.all(logits_st == 0.0), "ST8 logits all zero"
    print("[selftest] ST8 compute_logits shape=%s non-zero OK" % str(logits_st.shape),
          flush=True)

    # ST9: joint_sweep returns finite metrics
    n_tok_st = 30
    n_v_sm = 6
    rng6 = np.random.default_rng(99)
    logits_syn = rng6.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_syn = rng6.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_log_st = np.log(np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32))
    nd = n_tok_st // 2
    jr = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                     nxt_syn[:nd], nxt_syn[nd:])
    assert math.isfinite(jr["bpc_best"]), "ST9 bpc_best not finite"
    print("[selftest] ST9 joint_sweep OK (bpc=%.3f top1=%.4f mrr=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"]), flush=True)

    # ST10: sparsify_bipolar_np produces correct fraction nonzero
    E_chk = np.random.default_rng(0).standard_normal((20, 100)).astype(np.float32)
    E_sparse = sparsify_bipolar_np(E_chk, 0.05)
    nnz_per_row = (E_sparse != 0).sum(axis=1)
    expected_nnz = max(1, int(round(0.05 * 100)))
    assert (nnz_per_row == expected_nnz).all(), (
        "ST10 sparse nnz mismatch: expected %d, got %s" % (expected_nnz, str(nnz_per_row[:5])))
    print("[selftest] ST10 sparsify_bipolar_np nnz=%d OK" % expected_nnz, flush=True)

    # ST11: LAMBDA_GRID excludes 0.0 (Skunkworks META C7)
    assert 0.0 not in LAMBDA_GRID, "ST11 LAMBDA_GRID must exclude 0.0"
    print("[selftest] ST11 LAMBDA_GRID excludes 0.0 OK", flush=True)

    # ST12: LLM-call counter is zero
    assert _LLM_CALL_COUNTER[0] == 0, "ST12 LLM call counter non-zero: %d" % _LLM_CALL_COUNTER[0]
    print("[selftest] ST12 LLM call counter == 0 OK", flush=True)

    # ST13: ARM_TRAINERS keys match ARMS list
    for arm in ARMS:
        assert arm in ARM_TRAINERS, "ST13 ARMS entry %r missing from ARM_TRAINERS" % arm
    for arm in ARM_TRAINERS:
        assert arm in ARMS, "ST13 ARM_TRAINERS key %r missing from ARMS" % arm
    print("[selftest] ST13 ARMS/ARM_TRAINERS consistent (%d arms) OK" % len(ARMS), flush=True)

    # ST14: PCGrad arm and NAIVE arm produce DIFFERENT W under known-conflict setup
    # Build a tiny case where g_cf and g_stdp conflict consistently
    V_c = 4
    dim_c = 16
    rng_c = np.random.default_rng(123)
    E_c = _l2_normalize_np(rng_c.standard_normal((V_c, dim_c)).astype(np.float32))
    idx_c = np.array([0, 1, 2, 3, 0, 1, 2, 3, 0, 1], dtype=np.int64)
    res_naive = train_W_cfrpe_stdp_naive(E_c, idx_c, n_steps=20, batch=2,
                                          lr=0.5, stdp_w=0.5, seed=0, arm_idx=1)
    res_pcgrad = train_W_cfrpe_stdp_pcgrad(E_c, idx_c, n_steps=20, batch=2,
                                              lr=0.5, stdp_w=0.5, seed=0, arm_idx=2)
    diff_naive_pcgrad = float(np.abs(res_naive["W"] - res_pcgrad["W"]).mean())
    # NAIVE and PCGrad differ ONLY when projection fires; require at least one projection
    # If n_projected == 0, NAIVE and PCGrad are identical, which is correct behavior.
    if res_pcgrad["n_projected"] > 0:
        assert diff_naive_pcgrad > 1e-9, (
            "ST14 NAIVE and PCGrad should differ when projections fire: "
            "diff=%.3e n_projected=%d" % (diff_naive_pcgrad, res_pcgrad["n_projected"]))
        print("[selftest] ST14 NAIVE vs PCGrad differ (diff=%.4e, n_proj=%d) OK" % (
            diff_naive_pcgrad, res_pcgrad["n_projected"]), flush=True)
    else:
        print("[selftest] ST14 NAIVE vs PCGrad: n_projected=0 (no conflict observed; arms identical -- OK)",
              flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()

    if RUN_MODE == "smoke":
        print("\n[seed=%d] SMOKE: clean synthetic corpus (V=%d N_TRAIN=%d N_HELD=%d)" % (
            seed, VOCAB_CAP, N_TRAIN, N_HELD), flush=True)
        rng_corp = np.random.default_rng(seed * 7727 + 41)
        # Synthetic markov-bigram with slight structure
        bigram_targets = rng_corp.integers(0, VOCAB_CAP, size=VOCAB_CAP).astype(np.int64)
        idx_train = np.empty(N_TRAIN, dtype=np.int64)
        idx_train[0] = rng_corp.integers(0, VOCAB_CAP)
        for i in range(1, N_TRAIN):
            if rng_corp.random() < 0.5:
                idx_train[i] = bigram_targets[idx_train[i - 1]]
            else:
                idx_train[i] = rng_corp.integers(0, VOCAB_CAP)
        idx_held = np.empty(N_HELD, dtype=np.int64)
        idx_held[0] = rng_corp.integers(0, VOCAB_CAP)
        for i in range(1, N_HELD):
            if rng_corp.random() < 0.5:
                idx_held[i] = bigram_targets[idx_held[i - 1]]
            else:
                idx_held[i] = rng_corp.integers(0, VOCAB_CAP)
        V = VOCAB_CAP
        encoder_meta = {"smoke_synthetic": True, "V": V, "N_TRAIN": N_TRAIN}
    else:
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
        encoder_meta = {}

    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d" % (
        seed, V, N_TRAIN, N_HELD, N_DIM), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]), flush=True)

    print("\n[seed=%d] building encoder (V=%d, N_DIM=%d)..." % (seed, V, N_DIM), flush=True)
    t_enc0 = time.time()
    if RUN_MODE == "smoke":
        E_proj, w2v_meta = build_E_synthetic_smoke(V, N_DIM, seed)
    else:
        E_proj, w2v_meta = build_E_word2vec(vocab, N_DIM, seed)
    encoder_meta.update(w2v_meta)
    E_full = _l2_normalize_np(sparsify_bipolar_np(E_proj, SPARSE_BIPOLAR_F))
    sparsity = float((E_full != 0).mean())
    print("[seed=%d] encoder built in %.1fs; w2v_hit=%d/%d sparsity=%.3f" % (
        seed, time.time() - t_enc0, w2v_meta["n_hit"], w2v_meta["n_vocab"], sparsity), flush=True)
    del E_proj

    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != 0)
    nxt_eval = nxt_full[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        print("[WARN seed=%d] no valid eval pairs" % seed, flush=True)
        return {"seed": seed, "by_arm": {"ARM_UNIGRAM": uni}, "V": V,
                "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2)}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni, "w2v_meta": w2v_meta}

    for arm_idx, arm in enumerate(ARMS):
        t_arm0 = time.time()
        trainer = ARM_TRAINERS[arm]
        print("\n  [seed=%d arm=%s] training..." % (seed, arm), flush=True)
        try:
            t_ing0 = time.time()
            if arm == "ARM_CFRPE_ONLY":
                res = trainer(E_full, idx_train, n_steps=N_STEPS, batch=INGEST_BATCH,
                              lr=CFRPE_LR, seed=seed, arm_idx=arm_idx)
            else:
                res = trainer(E_full, idx_train, n_steps=N_STEPS, batch=INGEST_BATCH,
                              lr=CFRPE_LR, stdp_w=STDP_WEIGHT, seed=seed, arm_idx=arm_idx)
            t_ingest = time.time() - t_ing0
            W = res["W"]
            t_rec0 = time.time()
            logits_full = compute_logits(W, E_full, idx_held, RECALL_BATCH)
            t_recall = time.time() - t_rec0
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

        if logits_full.shape[0] >= len(ctx_full):
            logits_eval = logits_full[:len(ctx_full)][mask]
        else:
            valid_pos = np.where(mask)[0]
            valid_pos = valid_pos[valid_pos < logits_full.shape[0]]
            logits_eval = logits_full[valid_pos]
            nxt_eval_local = nxt_full[valid_pos]
            n_eval_l = len(nxt_eval_local)
            n_dev_l = n_eval_l // 2
            nxt_dev_l = nxt_eval_local[:n_dev_l]
            nxt_test_l = nxt_eval_local[n_dev_l:]
            jr = joint_sweep(logits_eval[:n_dev_l], logits_eval[n_dev_l:],
                              U_log, nxt_dev_l, nxt_test_l)
            rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval_local)
            grad_diag = _gradient_diagnostics(res, arm)
            jr.update({
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "wall_ingest_s": round(t_ingest, 2),
                "wall_recall_s": round(t_recall, 2),
                "raw_bpc_at_T1_L1": round(rbt1, 4),
                "grad_diagnostics": grad_diag,
            })
            by_arm[arm] = jr
            print("    [seed=%d arm=%s] bpc=%.3f top1=%.4f mrr=%.4f rawT1=%.3f elapsed=%.1fs grad=%s" % (
                seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"], str(grad_diag)), flush=True)
            continue

        jr = joint_sweep(logits_eval[:n_dev], logits_eval[n_dev:],
                         U_log, nxt_dev, nxt_test)
        rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval)
        grad_diag = _gradient_diagnostics(res, arm)
        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "grad_diagnostics": grad_diag,
        })
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc=%.3f top1=%.4f mrr=%.4f rawT1=%.3f elapsed=%.1fs grad=%s" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
            jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"], str(grad_diag)), flush=True)

    del E_full

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
        "encoder_meta": encoder_meta,
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "elapsed_s_seed": round(time.time() - t_seed, 2),
    }


def _gradient_diagnostics(res: Dict, arm: str) -> Dict:
    """Extract gradient-cosine + projection stats from arm trainer result."""
    cs = res.get("cosine_samples", [])
    n_logged = int(res.get("n_steps_logged", 0))
    n_conflict = int(res.get("n_conflict", 0))
    diag = {
        "n_logged": n_logged,
        "n_conflict": n_conflict,
        "frac_conflict": round(n_conflict / n_logged, 4) if n_logged > 0 else 0.0,
        "mean_cosine": round(float(np.mean(cs)), 4) if cs else 0.0,
        "median_cosine": round(float(np.median(cs)), 4) if cs else 0.0,
        "accum_mag_cf": round(float(res.get("accum_mag_cf", 0.0)), 4),
        "accum_mag_stdp": round(float(res.get("accum_mag_stdp", 0.0)), 4),
    }
    if arm == "ARM_CFRPE_PLUS_STDP_PCGRAD":
        diag["n_projected"] = int(res.get("n_projected", 0))
        diag["sum_proj_norm"] = round(float(res.get("sum_proj_norm", 0.0)), 4)
    elif arm == "ARM_CFRPE_PLUS_STDP_GCOND":
        diag["n_rescaled"] = int(res.get("n_rescaled", 0))
        diag["mean_rescale"] = round(float(res.get("mean_rescale", 1.0)), 4)
    return diag


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
    arm_grad: Dict[str, Dict] = {}
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
        raw_v = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        # Aggregate gradient diagnostics across seeds
        grad_diags = [u["by_arm"][arm].get("grad_diagnostics", {}) for u in valid]
        agg_grad = {}
        if grad_diags:
            for k in ("mean_cosine", "frac_conflict", "accum_mag_cf", "accum_mag_stdp"):
                vals = [g.get(k, 0.0) for g in grad_diags if isinstance(g.get(k), (int, float))]
                if vals:
                    agg_grad[k + "_mean"] = round(float(np.mean(vals)), 4)
            if arm == "ARM_CFRPE_PLUS_STDP_PCGRAD":
                proj_vals = [g.get("n_projected", 0) for g in grad_diags]
                agg_grad["n_projected_mean"] = round(float(np.mean(proj_vals)), 4)
            elif arm == "ARM_CFRPE_PLUS_STDP_GCOND":
                resc_vals = [g.get("n_rescaled", 0) for g in grad_diags]
                resc_factor = [g.get("mean_rescale", 1.0) for g in grad_diags]
                agg_grad["n_rescaled_mean"] = round(float(np.mean(resc_vals)), 4)
                agg_grad["mean_rescale_mean"] = round(float(np.mean(resc_factor)), 4)
        arm_grad[arm] = agg_grad
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "top1_acc_std": round(float(np.std(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_v)), 4),
            "n_valid_seeds": len(valid),
            "all_seeds_failed": False,
            "grad_diagnostics_agg": agg_grad,
        }
        arm_bpc[arm] = b_mean
        arm_cv[arm] = b_cv

    cfrpe_bpc = arm_bpc.get("ARM_CFRPE_ONLY", float("inf"))
    naive_bpc = arm_bpc.get("ARM_CFRPE_PLUS_STDP_NAIVE", float("inf"))
    pcgrad_bpc = arm_bpc.get("ARM_CFRPE_PLUS_STDP_PCGRAD", float("inf"))
    gcond_bpc = arm_bpc.get("ARM_CFRPE_PLUS_STDP_GCOND", float("inf"))
    pcgrad_cv = arm_cv.get("ARM_CFRPE_PLUS_STDP_PCGRAD", float("nan"))
    gcond_cv = arm_cv.get("ARM_CFRPE_PLUS_STDP_GCOND", float("nan"))

    # Provenance rails (each arm reproduces A1 reference)
    cfrpe_drift = abs(cfrpe_bpc - SANITY_RAIL_CFRPE_REF) if math.isfinite(cfrpe_bpc) else float("inf")
    naive_drift = abs(naive_bpc - SANITY_RAIL_HETPLAST_REF) if math.isfinite(naive_bpc) else float("inf")
    cfrpe_rail_ok = cfrpe_drift <= SANITY_RAIL_TOLERANCE
    naive_rail_ok = naive_drift <= SANITY_RAIL_TOLERANCE

    # Lifts: PCGrad / GCond vs NAIVE (rescue magnitude)
    lift_pcgrad_over_naive = naive_bpc - pcgrad_bpc
    lift_gcond_over_naive = naive_bpc - gcond_bpc
    lift_pcgrad_vs_cfrpe = cfrpe_bpc - pcgrad_bpc
    lift_gcond_vs_cfrpe = cfrpe_bpc - gcond_bpc

    arm_summary = (
        "uni=%.3f | CFRPE_ONLY=%.4f(drift=%+.4f,rail=%s) | "
        "NAIVE=%.4f(drift=%+.4f,rail=%s) | "
        "PCGRAD=%.4f(cv=%.3f,lift_over_naive=%+.3f,vs_cfrpe=%+.3f) | "
        "GCOND=%.4f(cv=%.3f,lift_over_naive=%+.3f,vs_cfrpe=%+.3f)"
    ) % (
        unigram_bpc,
        cfrpe_bpc, cfrpe_bpc - SANITY_RAIL_CFRPE_REF, str(cfrpe_rail_ok),
        naive_bpc, naive_bpc - SANITY_RAIL_HETPLAST_REF, str(naive_rail_ok),
        pcgrad_bpc, pcgrad_cv if math.isfinite(pcgrad_cv) else -1.0,
        lift_pcgrad_over_naive, lift_pcgrad_vs_cfrpe,
        gcond_bpc, gcond_cv if math.isfinite(gcond_cv) else -1.0,
        lift_gcond_over_naive, lift_gcond_vs_cfrpe,
    )

    # Gradient-cosine summary
    grad_summary = "grad_cosines: "
    for arm in ARMS:
        g = arm_grad.get(arm, {})
        if g:
            grad_summary += "%s(mean_cos=%s,frac_conflict=%s) " % (
                arm.replace("ARM_", ""),
                g.get("mean_cosine_mean", "?"), g.get("frac_conflict_mean", "?"))

    detail = {
        "by_arm_agg": by_arm_agg,
        "lifts": {
            "pcgrad_over_naive": round(lift_pcgrad_over_naive, 4),
            "gcond_over_naive": round(lift_gcond_over_naive, 4),
            "pcgrad_vs_cfrpe": round(lift_pcgrad_vs_cfrpe, 4),
            "gcond_vs_cfrpe": round(lift_gcond_vs_cfrpe, 4),
        },
        "sanity_rails": {
            "cfrpe_ref": SANITY_RAIL_CFRPE_REF,
            "cfrpe_drift": round(cfrpe_drift, 4),
            "cfrpe_rail_ok": bool(cfrpe_rail_ok),
            "naive_ref": SANITY_RAIL_HETPLAST_REF,
            "naive_drift": round(naive_drift, 4),
            "naive_rail_ok": bool(naive_rail_ok),
            "tolerance": SANITY_RAIL_TOLERANCE,
        },
        "bands": {
            "hard_pass_bpc_ceiling": HARD_PASS_BPC_CEILING,
            "middle_band_bpc_lower": MIDDLE_BAND_BPC_LOWER,
            "middle_band_bpc_upper": MIDDLE_BAND_BPC_UPPER,
            "hard_fail_bpc_floor": HARD_FAIL_BPC_FLOOR,
            "cv_max": CV_MAX,
        },
        "pcgrad_bpc": round(pcgrad_bpc, 4),
        "gcond_bpc": round(gcond_bpc, 4),
        "pcgrad_cv": round(pcgrad_cv, 4) if math.isfinite(pcgrad_cv) else None,
        "gcond_cv": round(gcond_cv, 4) if math.isfinite(gcond_cv) else None,
        "n_seeds": len(units),
        "unigram_bpc": round(unigram_bpc, 4),
        "grad_summary": grad_summary,
        "honest_scope": (
            "v2_RESCUE of v1 which TIMED OUT at 5400s without producing metrics. "
            "Scope reduction Option A: N_DIM=4096 (was 8192), N_TRAIN=50k (was 100k), "
            "N_HELD=10k (was 20k); N_STEPS=1000 PRESERVED to keep PCGrad/GCond "
            "projection-convergence opportunity. 4 arms x 3 seeds unchanged. "
            "Intra-cell PCGRAD-vs-NAIVE delta IS the load-bearing discriminator. "
            "Provenance rails to A1 (7.0888/7.2044) DISABLED at this scope - "
            "calibrations were at v1 scope. ANCHOR 2 of composition collapse drill: "
            "tests whether gradient conflict between cf-RPE and STDP plasticity rules "
            "(Yu PCGrad / GCond) is the first-order cause of A1's hetplast collapse. "
            "4 arms: CFRPE_ONLY (intra-cell control), NAIVE (additive composition; "
            "reproduces A1 collapse pattern), PCGRAD (orthogonal projection of STDP "
            "onto cf-RPE complement), GCOND (accumulation-based STDP rescaling). "
            "ANCHOR 1 (MH beta-sweep) already HARD_FAIL_STRUCTURAL so MH OMITTED. "
            "WHAT_THIS_DOES_NOT_SHOW: gate training; alternative gradient-conflict "
            "resolvers (CAGrad, MGDA); shared-state architecture (H5); MH cleanup at "
            "all; absolute BPC matched to v1-scope reference points."
        ),
        "cites": [
            "notes/research_composition_collapse_critical_drill_2026-06-24.md (ANCHOR 2)",
            "experiments/exp_substrate_pcgrad_cfrpe_stdp_v1.py (TIMED OUT 5400s; rescue precursor)",
            "data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json (A1 provenance refs)",
            "arxiv.org/abs/2001.06782 (Yu PCGrad)",
            "arXiv:2509.07252 (GCond)",
        ],
    }

    # Substrate-only audit gate
    total_llm_calls = sum(int(u.get("llm_forward_calls_at_inference", 0)) for u in units)
    detail["llm_forward_calls_total"] = total_llm_calls
    if total_llm_calls != 0:
        return ("HARD_FAIL",
                "HARD_FAIL_LLM_CALL: llm_calls=%d. %s" % (total_llm_calls, arm_summary),
                detail)

    pcgrad_failed = by_arm_agg.get("ARM_CFRPE_PLUS_STDP_PCGRAD", {}).get(
        "all_seeds_failed", True)
    if pcgrad_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_CFRPE_PLUS_STDP_PCGRAD all seeds failed. %s" % arm_summary,
                detail)

    # Provenance rails DISABLED at v2_RESCUE scope (rails were calibrated at v1
    # scope N_DIM=8192/N_TRAIN=100k; v2_RESCUE uses N_DIM=4096/N_TRAIN=50k where
    # absolute reference points 7.0888 / 7.2044 don't apply). Drifts surfaced
    # but NOT used as HARD_FAIL gates - intra-cell PCGRAD-vs-NAIVE delta IS the
    # load-bearing discriminator.
    detail["provenance_check_active"] = False
    detail["provenance_rails_disabled_reason"] = (
        "v2_RESCUE scope (N_DIM=4096/N_TRAIN=50k) differs from v1 calibration "
        "scope (N_DIM=8192/N_TRAIN=100k); absolute reference points do not apply"
    )

    # cv gate on the load-bearing arm (PCGrad)
    if math.isfinite(pcgrad_cv) and pcgrad_cv > CV_MAX:
        return ("MIDDLE_BAND_HIGH_CV",
                "MIDDLE_BAND_HIGH_CV: ARM_PCGRAD cv=%.3f > %.2f mandatory. "
                "pcgrad_bpc=%.4f. %s. %s" % (
                    pcgrad_cv, CV_MAX, pcgrad_bpc, arm_summary, grad_summary),
                detail)

    # Verdict bands: take the BETTER of PCGRAD or GCOND for HARD_PASS check
    best_rescue_bpc = min(pcgrad_bpc, gcond_bpc) if (
        math.isfinite(pcgrad_bpc) and math.isfinite(gcond_bpc)) else (
        pcgrad_bpc if math.isfinite(pcgrad_bpc) else gcond_bpc)
    best_rescue_arm = "PCGRAD" if pcgrad_bpc <= gcond_bpc else "GCOND"

    if math.isfinite(best_rescue_bpc) and best_rescue_bpc <= HARD_PASS_BPC_CEILING:
        detail["verdict_tier"] = "HARD_PASS_GRADIENT_CONFLICT_RESCUE"
        detail["best_rescue_arm"] = best_rescue_arm
        return ("HARD_PASS",
                "HARD_PASS_GRADIENT_CONFLICT_RESCUE: %s BPC=%.4f <= %.3f. "
                "Gradient-conflict IS first-order cause of hetplast collapse; "
                "PCGrad/GCond rescues without architecture change. %s. %s" % (
                    best_rescue_arm, best_rescue_bpc, HARD_PASS_BPC_CEILING,
                    arm_summary, grad_summary),
                detail)

    # PCGrad-specific MIDDLE_BAND / HARD_FAIL on PCGrad arm (per ANCHOR 2 primary)
    if math.isfinite(pcgrad_bpc) and MIDDLE_BAND_BPC_LOWER < pcgrad_bpc < MIDDLE_BAND_BPC_UPPER:
        detail["verdict_tier"] = "MIDDLE_BAND_PARTIAL_PCGRAD"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_PCGRAD: PCGRAD BPC=%.4f in (%.2f, %.2f). "
                "PCGrad partial rescue; gradient-conflict contributing but not sole cause. "
                "%s. %s" % (
                    pcgrad_bpc, MIDDLE_BAND_BPC_LOWER, MIDDLE_BAND_BPC_UPPER,
                    arm_summary, grad_summary),
                detail)

    if math.isfinite(pcgrad_bpc) and pcgrad_bpc >= HARD_FAIL_BPC_FLOOR:
        detail["verdict_tier"] = "HARD_FAIL_PCGRAD_DOES_NOT_HELP"
        return ("HARD_FAIL",
                "HARD_FAIL_PCGRAD_DOES_NOT_HELP: PCGRAD BPC=%.4f >= %.2f. "
                "Gradient projection doesn't rescue hetplast collapse; H1 (gradient "
                "conflict primary cause) REFUTED; structural diagnosis stands; "
                "need cross-layer or other architectural change. %s. %s" % (
                    pcgrad_bpc, HARD_FAIL_BPC_FLOOR, arm_summary, grad_summary),
                detail)

    # Else: in the boundary region [HARD_PASS_BPC_CEILING, MIDDLE_BAND_BPC_LOWER]
    detail["verdict_tier"] = "MIDDLE_BAND_BOUNDARY"
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_BOUNDARY: PCGRAD BPC=%.4f near HARD_PASS ceiling %.2f. "
            "Marginal rescue; review per-arm + gradient diagnostics. %s. %s" % (
                pcgrad_bpc, HARD_PASS_BPC_CEILING, arm_summary, grad_summary),
            detail)


# ============================================================================
# Main loop with per-seed checkpoint
# ============================================================================

print("[config] %s" % CONFIG_VERSION, flush=True)

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

summary_str = (
    "%s | arms=%d seeds=%d N_DIM=%d N_TRAIN=%d encoder=word2vec_sparse_bipolar "
    "cfrpe_lr=%.3f stdp_w=%.3f n_steps=%d" % (
        verdict, len(ARMS), len(SEEDS), N_DIM, N_TRAIN,
        CFRPE_LR, STDP_WEIGHT, N_STEPS)
)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": summary_str,
    "config_version": CONFIG_VERSION,
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "N_STEPS": N_STEPS,
    "CFRPE_LR": CFRPE_LR,
    "STDP_WEIGHT": STDP_WEIGHT,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "COSINE_STRIDE": COSINE_STRIDE,
    "TEMP_GRID": TEMP_GRID,
    "LAMBDA_GRID": LAMBDA_GRID,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "detail": detail,
    "per_seed": [
        {"seed": u.get("seed"), "by_arm": u.get("by_arm"),
         "V": u.get("V"), "N_DIM": u.get("N_DIM"),
         "N_TRAIN": u.get("N_TRAIN"),
         "llm_forward_calls_at_inference": u.get("llm_forward_calls_at_inference", 0),
         "encoder_meta": u.get("encoder_meta", {}),
         "elapsed_s_seed": u.get("elapsed_s_seed")}
        for u in all_units
    ],
    "elapsed_s": round(sum(u.get("elapsed_s_seed", 0.0) for u in all_units), 2),
}

write_metrics(out_dir, metrics, all_units)
print("[metrics] written to %s" % out_dir, flush=True)
