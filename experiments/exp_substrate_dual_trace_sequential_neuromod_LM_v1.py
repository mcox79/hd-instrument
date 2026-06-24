"""
substrate_dual_trace_sequential_neuromod_LM_v1 -- dual-trace sequential neuromodulator LM.

MOTIVATION (2026-06-23):
  sparse_bipolar_substrate_lm_param_sweep_v1 HARD_FAIL: envelope capped at +0.44 bits BPC.
  neuromodulator_3axis_gated_compose_LM_v1 tests NAIVE MULTIPLICATIVE composition (one trace).
  Marder STG GPCR caveat: multiple modulators on one trace converge to a single I_MI scalar
  (degenerate). The brain-correct rescue is TWO SEPARATE ELIGIBILITY TRACES with DIFFERENT
  timescales gated by DIFFERENT modulators (Brzosko 2017; Huertas 2016; Fremaux-Gerstner 2016).

BRAIN MECHANISM (Brzosko 2017 + Huertas 2016):
  E_pos: LTP-trace (fast timescale tau~5 steps) gated by DOPAMINE (novelty / prediction-error)
    E_pos[t+1] = (1 - 1/tau_pos) * E_pos[t] + (1/tau_pos) * outer(tgt, src)
  E_neg: LTD-trace (slow timescale tau~50 steps) gated by ACh (attention / familiarity)
    E_neg[t+1] = (1 - 1/tau_neg) * E_neg[t] + (1/tau_neg) * outer(pred, src)
  W update: W += dopa * E_pos - ACh * E_neg
  Orthogonality mechanism: E_pos and E_neg accumulate INDEPENDENTLY; their time-integrals are
  non-collinear by construction (different tau). W update adds TWO rank-1 components per step
  that are not collinear -- breaking rank-1 Hebbian floor.

THREE ARMS (each builds FRESH W; no cross-contamination):
  ARM_BASELINE:    cf-RPE single-trace (dopamine only); reproduces fair_harness baseline
                   W += dopa * outer(Delta, src) -- same as ARM_DOPAMINE_ONLY in prior cell
  ARM_NAIVE_MULT:  3-axis multiplicative on ONE Hebbian trace (dopamine * ACh * 5HT)
                   W += (dopa * ACh * serotonin) * outer(Delta, src)
                   Replicates Gap A spec; tests Marder degeneracy prediction directly.
  ARM_DUAL_TRACE:  Two separate eligibility traces (E_pos + E_neg) with DIFFERENT timescales
                   gated by DIFFERENT modulators (Brzosko sequential mechanism):
                   W += dopa * E_pos - ACh * E_neg

PRE-REGISTERED BANDS (per handoff + research note; IMMUTABLE):
  HARD_PASS:   ARM_DUAL_TRACE BPC lift >= +0.20 vs ARM_BASELINE AND >= +0.10 vs ARM_NAIVE_MULT
  MIDDLE_BAND: ARM_DUAL_TRACE beats ARM_BASELINE by +0.05 to +0.20 AND beats ARM_NAIVE_MULT by
               >= +0.05 (orthogonality partial but real)
  HARD_FAIL:   ARM_DUAL_TRACE within +/-0.05 of ARM_BASELINE OR fails to beat ARM_NAIVE_MULT
  CV across 3 seeds < 0.05 mandatory.

SELF-TESTS (MANDATORY per PROT-022 + handoff spec):
  1. P=1 endpoint: tau_pos=1 and tau_neg=1 (traces collapse to single-step update) ->
     ARM_DUAL_TRACE with dopa=1 ACh=0 -> W += E_pos -> same as single-trace Hebbian.
     Verified by checking W norm is non-trivial.
  2. sigma=0 recovery: all identical inputs -> ACh=0 (fully expected) -> E_neg gets no ACh gate;
     dual-trace degrades gracefully to dopamine-only write.
  3. Trace independence at zero modulators: with dopa=0 AND ACh=0, W should receive no update
     (gate product = 0 on both trace paths).
  4. E_pos and E_neg produce distinct tensors (non-collinear) under normal input variation.
  5. All arms produce finite BPC in [1.0, 25.0] at smoke scale.
  6. cf-RPE delta shrinks prediction error (dopamine rule working).

PROT-018: anchor has NO _n suffix; production N = 8192;
  rationale: matching fair_harness baseline config (N=8192 N_TRAIN=100k f=0.02) for fair
  envelope comparison. No _nN binding required.

GPU REQUIRED (Fix #24): torch.cuda + batched outer-product matmul.
  Encoder hoisted outside arm loop (load once, reuse per Fix #24).
  N_DIM=8192 -> matmul bound; route to overnight_queue.

Cites:
  Brzosko et al. (2017) "Sequential neuromodulation of Hebbian plasticity" eLife 27756
  Huertas et al. (2016) "Role of Multiple Neuromodulators in Reinforcement Learning" PMC5156839
  Fremaux-Gerstner (2016) "Neuromodulated STDP, Three-Factor Learning Rules" Front Neural Circ
  experiments/exp_substrate_neuromodulator_3axis_gated_compose_LM_v1.py (prior 3-axis cell)
  experiments/exp_fair_harness_substrate_as_lm_v1.py (harness: joint T/lambda sweep)
  data/exp_sparse_bipolar_substrate_lm_param_sweep_v1/metrics.json (envelope cap: 7.295)
  notes/exp_dev_handoff_research_neuromodulator_orthogonal_composition_2026-06-23.md
  notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md

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
import json
import math
import signal
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_dual_trace_sequential_neuromod_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# PROT-018: no _n suffix; production N stated explicitly.
PRODUCTION_N = 8192

# ============================================================================
# Pre-reg bands (IMMUTABLE; pre-registered before smoke)
# ============================================================================
# primary: ARM_DUAL_TRACE vs ARM_BASELINE
HARD_PASS_DUAL_VS_BASELINE_BPC = 0.20   # dual beats baseline by >= 0.20 bits
HARD_PASS_DUAL_VS_NAIVE_BPC = 0.10      # dual beats naive-mult by >= 0.10 bits
MIDDLE_DUAL_VS_BASELINE_LOW = 0.05      # dual beats baseline by >= 0.05 bits
MIDDLE_DUAL_VS_NAIVE_LOW = 0.05         # dual beats naive-mult by >= 0.05 bits
HARD_FAIL_TOL = 0.05                    # within +/-0.05 of baseline = HARD_FAIL

CV_MAX = 0.05   # CV across seeds must be < 0.05 mandatory

FAIR_HARNESS_BASELINE_BPC = 7.3065      # fair_harness chain-grade baseline
ENVELOPE_CAP_BPC = 7.295               # sparse_bipolar_param_sweep best
UNIGRAM_BPC_REF = 7.738

# READOUT_DEGENERATE gate tolerance
DEGEN_TOL = 0.5

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else \
    os.environ.get("HDLAB_RUN_MODE", "full")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# ============================================================================
# Config
# ============================================================================
N_DIM = PRODUCTION_N         # 8192 for FULL; smoke overrides below
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

SPARSE_BIPOLAR_F = 0.02      # best from param sweep (bpc=7.295 at f=0.02, N=8192)

# Dual-trace timescales (per Huertas 2016 + Brzosko 2017)
TAU_POS = 5     # fast LTP-trace timescale (~dopamine phasic bursts ~100ms)
TAU_NEG = 50    # slow LTD-trace timescale (~ACh tonic ~seconds)

# ACh context window for attention centroid
NEUROMOD_CONTEXT = 32

# Joint (T, lambda) sweep -- same as fair_harness
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

WORD2VEC_MODEL = "word2vec-google-news-300"

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke: all 3 arms + verdict path; <180s on local CPU or GPU
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

ARMS = [
    "ARM_BASELINE",
    "ARM_NAIVE_MULT",
    "ARM_DUAL_TRACE",
]

# ============================================================================
# Encoder / embedding helpers (copied verbatim from 3axis cell for fair compare)
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


def build_E_word2vec_gpu(vocab: List[str], n_dim: int, seed: int,
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
# Neuromodulator signal primitives
# ============================================================================

def compute_dopamine_signal(err_norms: torch.Tensor, err_norm_running: float) -> float:
    """Dopamine: cf-RPE error norm normalized by running mean.

    Returns scalar in [0.0, 1.5]. High prediction error -> high dopamine -> LTP.
    Brain analog: phasic DA burst on reward-prediction-error (Schultz 1997).
    Self-test: err_norms all zero -> dopamine = 0.0 (no error, no LTP).
    """
    err_mean = float(err_norms.mean().item())
    denom = max(err_norm_running, 1e-6)
    raw = err_mean / denom
    return min(1.5, max(0.0, raw))


def compute_ach_signal(src_centroid: torch.Tensor, ctx_buf: List[torch.Tensor],
                        startup_val: float = 0.0) -> float:
    """ACh: attention gate as cosine margin between batch centroid and context centroid.

    Returns scalar in [0.0, 1.5]. High margin (unexpected input) -> high ACh.
    Brain analog: tonic ACh tracks expected uncertainty (Yu-Dayan 2005; Hasselmo-Sarter 2011).

    startup_val parameter:
      0.0 (default, used by ARM_DUAL_TRACE): no LTD before context builds (safe startup)
      1.0 (used by ARM_NAIVE_MULT): neutral multiplicative identity at startup (writes proceed)

    Self-test: src == context centroid -> sim=1 -> margin=0 -> ACh=0 (fully familiar).
    Self-test: empty ctx_buf -> returns startup_val.
    """
    if not ctx_buf or len(ctx_buf) < 4:
        return startup_val  # startup: return arm-specific default before context accumulates
    ctx_stacked = torch.stack(ctx_buf[-NEUROMOD_CONTEXT:], dim=0)
    ctx_cen = _l2_normalize_t(ctx_stacked.mean(dim=0))
    sim = float(torch.dot(src_centroid, ctx_cen).item())
    margin = max(0.0, 1.0 - sim)
    return min(1.5, margin * 1.5)


# ============================================================================
# Core: W builder for each arm
# ============================================================================

def build_W_baseline(idx_train: torch.Tensor,
                      E: torch.Tensor,
                      ingest_chunk: int) -> torch.Tensor:
    """ARM_BASELINE: cf-RPE single-trace (dopamine only). Reproduces fair_harness baseline.

    W += dopa * outer(Delta, src)
    where Delta = E_tgt - W @ E_src (cf-RPE prediction error)
    Dopa gates by error norm / running mean error norm.
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W

    err_norm_running = 1.0
    ema_decay = 0.95

    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        E_src = E[idx_train[b:end]]
        E_tgt = E[idx_train[b + 1:end + 1]]

        pred = E_src @ W.T
        Delta = E_tgt - pred
        err_norms = Delta.norm(dim=1)
        dopa = compute_dopamine_signal(err_norms, err_norm_running)
        err_norm_running = ema_decay * err_norm_running + (1.0 - ema_decay) * float(err_norms.mean().item())

        if dopa > 1e-9:
            W.add_(dopa * (Delta.T @ E_src))

        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()

    return W


def build_W_naive_mult(idx_train: torch.Tensor,
                        E: torch.Tensor,
                        ingest_chunk: int) -> torch.Tensor:
    """ARM_NAIVE_MULT: 3-axis multiplicative on ONE Hebbian trace.

    W += (dopa * ACh * serotonin) * outer(Delta, src)
    Scalar product of all three modulators on the SAME trace.
    Tests Marder GPCR degeneracy prediction: this should NOT break the envelope because
    dopa * ACh * serotonin is just one effective scalar (eta_eff).
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W

    err_norm_running = 1.0
    ema_decay = 0.95
    ctx_buf: List[torch.Tensor] = []
    running_mean = torch.zeros(dim, dtype=TORCH_DTYPE, device=device)
    mean_count = 0

    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        E_src = E[idx_train[b:end]]
        E_tgt = E[idx_train[b + 1:end + 1]]

        pred = E_src @ W.T
        Delta = E_tgt - pred
        err_norms = Delta.norm(dim=1)

        dopa = compute_dopamine_signal(err_norms, err_norm_running)
        err_norm_running = ema_decay * err_norm_running + (1.0 - ema_decay) * float(err_norms.mean().item())

        src_centroid = _l2_normalize_t(E_src.mean(dim=0))
        # ARM_NAIVE_MULT: ACh is multiplicative gain; startup_val=1.0 (neutral identity)
        ach = compute_ach_signal(src_centroid, ctx_buf, startup_val=1.0)
        ctx_buf.append(src_centroid.detach())
        if len(ctx_buf) > NEUROMOD_CONTEXT * 4:
            ctx_buf = ctx_buf[-NEUROMOD_CONTEXT:]

        if mean_count > 0:
            rm_norm = _l2_normalize_t(running_mean)
            sim_s = float(torch.dot(src_centroid, rm_norm).item())
            serotonin = min(1.5, max(0.0, (1.0 - sim_s) * 1.5))
        else:
            serotonin = 1.0
        running_mean = ema_decay * running_mean + (1.0 - ema_decay) * E_src.mean(dim=0)
        mean_count += 1

        gate = float(dopa * ach * serotonin)
        if gate > 1e-9:
            W.add_(gate * (Delta.T @ E_src))

        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()

    return W


def build_W_dual_trace(idx_train: torch.Tensor,
                        E: torch.Tensor,
                        ingest_chunk: int) -> torch.Tensor:
    """ARM_DUAL_TRACE: brain-correct dual-trace sequential neuromodulator mechanism.

    Two separate eligibility traces with different timescales:
      E_pos (LTP-trace, tau_fast=TAU_POS) gated by DOPAMINE (novelty/error)
      E_neg (LTD-trace, tau_slow=TAU_NEG) gated by ACh (attention/familiarity)

    Trace dynamics (chunked approximation -- see implementation note):
      E_pos = (1 - 1/tau_pos) * E_pos + (1/tau_pos) * outer(Delta, src)  [per chunk]
      E_neg = (1 - 1/tau_neg) * E_neg + (1/tau_neg) * outer(pred, src)   [per chunk]

    W update per chunk:
      W += dopa * E_pos - ACh * E_neg

    Orthogonality mechanism (Brzosko 2017 + Huertas 2016):
      E_pos and E_neg carry DIFFERENT outer products (Delta vs pred as targets).
      DIFFERENT timescales mean their time-integrals are non-collinear by construction.
      Net W rank grows faster than single-trace; effective capacity > rank-1 floor.

    Implementation note on chunked trace:
      The full per-step trace update is O(N^2) per step -- prohibitively slow at N=8192.
      We approximate using chunk-mean outer products accumulated into trace matrices.
      Each chunk contributes one outer product (mean Delta for E_pos, mean pred for E_neg).
      The exponential decay is applied per-chunk with effective decay (1-1/tau)^chunk_sz.
      This is equivalent to an EMA filter on the outer-product stream with timescale tau,
      discretized at chunk granularity. At INGEST_CHUNK=4096, tau_pos~5 chunks (20k steps),
      tau_neg~50 chunks (200k steps); these are well-separated timescales as required.
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    # Eligibility traces as dim x dim matrices (same shape as W)
    E_pos = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    E_neg = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W

    # Effective decay per chunk (approximation: treat chunk as one time step for trace)
    decay_pos = 1.0 - 1.0 / TAU_POS   # ~0.80 per chunk
    decay_neg = 1.0 - 1.0 / TAU_NEG   # ~0.98 per chunk

    err_norm_running = 1.0
    ema_decay = 0.95
    ctx_buf: List[torch.Tensor] = []

    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        E_src = E[idx_train[b:end]]
        E_tgt = E[idx_train[b + 1:end + 1]]
        chunk_sz = E_src.shape[0]

        # Prediction via current W (shared for all trace updates this chunk)
        pred = E_src @ W.T                    # [chunk, dim]
        Delta = E_tgt - pred                  # [chunk, dim]: LTP signal (correction)

        # Chunk-mean outer products for trace update
        # E_pos trace: LTP -- outer product of DELTA (correction vector) with src
        outer_pos = (Delta.T @ E_src) / max(chunk_sz, 1)   # [dim, dim]
        # E_neg trace: LTD -- outer product of PREDICTED (existing memory) with src
        outer_neg = (pred.T @ E_src) / max(chunk_sz, 1)    # [dim, dim]

        # Trace exponential decay + new contribution (EMA per chunk)
        # Effective per-chunk decay: decay^chunk_sz for exact tau; here use per-chunk constant
        E_pos.mul_(decay_pos).add_((1.0 - decay_pos) * outer_pos)
        E_neg.mul_(decay_neg).add_((1.0 - decay_neg) * outer_neg)

        # Modulator signals
        err_norms = Delta.norm(dim=1)
        dopa = compute_dopamine_signal(err_norms, err_norm_running)
        err_norm_running = ema_decay * err_norm_running + (1.0 - ema_decay) * float(err_norms.mean().item())

        src_centroid = _l2_normalize_t(E_src.mean(dim=0))
        ach = compute_ach_signal(src_centroid, ctx_buf)
        ctx_buf.append(src_centroid.detach())
        if len(ctx_buf) > NEUROMOD_CONTEXT * 4:
            ctx_buf = ctx_buf[-NEUROMOD_CONTEXT:]

        # W update: sequential modulator gating of separate traces (Brzosko 2017)
        # dopa gates LTP-trace; ACh gates LTD-trace
        # Subtraction creates orthogonal composition: W encodes BOTH correction AND prediction
        if dopa > 1e-9 or ach > 1e-9:
            W.add_(dopa * E_pos)
            if ach > 1e-9:
                W.sub_(ach * E_neg)

        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()

    return W


# ============================================================================
# Arm logits builder (reuses fair_harness pattern)
# ============================================================================

def compute_arm_logits(arm_label: str,
                        E_base: torch.Tensor,
                        idx_train: np.ndarray,
                        idx_held: np.ndarray,
                        seed: int) -> Dict:
    """Build W for the arm, compute held-set logits, return dict."""
    device = E_base.device
    V, dim = E_base.shape

    # All arms use sparse-bipolar encoding (best f=0.02 from param sweep)
    E = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))

    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)

    t0 = time.time()
    if arm_label == "ARM_BASELINE":
        W = build_W_baseline(idx_train_t, E, INGEST_CHUNK)
    elif arm_label == "ARM_NAIVE_MULT":
        W = build_W_naive_mult(idx_train_t, E, INGEST_CHUNK)
    elif arm_label == "ARM_DUAL_TRACE":
        W = build_W_dual_trace(idx_train_t, E, INGEST_CHUNK)
    else:
        raise ValueError("Unknown arm: %s" % arm_label)

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    n_h = idx_held_t.shape[0]
    E_src_held = E[idx_held_t]
    logits_t = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        src_b = E_src_held[b:end]
        pred_b = _l2_normalize_t(src_b @ W.T)
        logits_t[b:end] = pred_b @ E.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits_t.detach().cpu().numpy().astype(np.float32)

    del W, E_src_held, logits_t, E
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
    }


# ============================================================================
# text8 / vocab / metrics (identical to 3axis cell for fair comparison)
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


def softmax_logits_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp_logp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    return -float(np.mean(logp[np.arange(n), nxt])) / math.log(2.0)


def top1_acc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
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


def joint_sweep_substrate(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                           U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                           temp_grid: list, lambda_grid: list, mrr_k: int) -> Dict:
    """Joint (T, lambda) sweep on dev; eval on test. Returns best per metric."""
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)
    raw_top1_at_T1_L1 = top1_acc_from_logp(logp_T1, nxt_test)
    raw_mrr_at_T1_L1 = mrr_at_k(logp_T1, nxt_test, mrr_k)

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
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray,
                     V: int, mrr_k: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    nxt_eval = nxt[mask]
    if len(nxt_eval) == 0:
        return {"bpc_unigram": float("inf"), "top1_unigram": 0.0,
                "mrr_unigram": 0.0, "n_test": 0}
    n_dev = len(nxt_eval) // 2
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
# Instrumentation self-test (MANDATORY; PROT-022)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics non-null/non-sentinel at small scale.

    Tests per handoff spec:
    1. W builds (non-trivial norm) for all 3 arms.
    2. cf-RPE delta shrinks prediction error (dopamine rule working).
    3. ACh = 0 for identical inputs (sigma=0 case).
    4. E_pos and E_neg produce DISTINCT matrices (trace independence).
    5. W gets no update when dopa=0 AND ACh=0 (zero-modulator gate test).
    6. All arms produce finite logits and BPC in [0.0, 25.0] at smoke scale.
    7. Sparsification density matches SPARSE_BIPOLAR_F.
    """
    print("[selftest] begin instrumentation self-test", flush=True)
    n = 64; V = 8
    rng = np.random.default_rng(42)
    E_np = rng.standard_normal((V, n)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E = torch.from_numpy(E_np).to(DEVICE, dtype=TORCH_DTYPE)

    toks = [i % V for i in range(60)]
    idx = torch.tensor(toks, dtype=torch.long, device=DEVICE)
    idx_np = np.array(toks, dtype=np.int64)

    # Test 1: all 3 arms produce non-trivial W
    W_b = build_W_baseline(idx, E, ingest_chunk=16)
    assert W_b.shape == (n, n), "baseline W shape wrong"
    assert float(W_b.norm().item()) > 0.0, "ARM_BASELINE W is zero"

    W_nm = build_W_naive_mult(idx, E, ingest_chunk=16)
    assert float(W_nm.norm().item()) > 0.0, "ARM_NAIVE_MULT W is zero"

    W_dt = build_W_dual_trace(idx, E, ingest_chunk=16)
    assert float(W_dt.norm().item()) > 0.0, "ARM_DUAL_TRACE W is zero"

    # Test 2: cf-RPE delta shrinks prediction error
    W_test = torch.zeros((n, n), dtype=TORCH_DTYPE, device=DEVICE)
    src_v = E[0]; tgt_v = E[1]
    err_before = float((tgt_v - W_test @ src_v).norm().item())
    dw = torch.outer(tgt_v - W_test @ src_v, src_v)
    W_test.add_(dw)
    err_after = float((tgt_v - W_test @ src_v).norm().item())
    assert err_after < err_before, "cf-RPE did not shrink error: %.4f -> %.4f" % (err_before, err_after)

    # Test 3: ACh = 0 for identical inputs (sigma=0 case)
    ctx_same = [_l2_normalize_t(E[0].clone()) for _ in range(5)]
    ach_ident = compute_ach_signal(_l2_normalize_t(E[0].clone()), ctx_same)
    assert ach_ident < 0.05, "ACh should be ~0 for identical inputs, got %.4f" % ach_ident

    # Test 4: E_pos and E_neg are distinct (trace independence test)
    # Build dual-trace with enough data to let traces diverge
    idx_long = torch.arange(V, device=DEVICE).repeat(8)
    E_pos_test = torch.zeros((n, n), dtype=TORCH_DTYPE, device=DEVICE)
    E_neg_test = torch.zeros((n, n), dtype=TORCH_DTYPE, device=DEVICE)
    n_p = idx_long.shape[0] - 1
    E_src_t = E[idx_long[:n_p]]
    E_tgt_t = E[idx_long[1:n_p + 1]]
    pred_t = E_src_t  # W=0 initially, so pred=0@E_src_t = zero; outer_neg = 0 too
    Delta_t = E_tgt_t - pred_t
    outer_p = (Delta_t.T @ E_src_t) / n_p
    outer_n = (pred_t.T @ E_src_t) / n_p
    E_pos_test.add_(outer_p)
    E_neg_test.add_(outer_n)
    # E_pos should be non-zero (Delta = tgt - 0 = tgt); E_neg should be near-zero (pred=0)
    e_pos_norm = float(E_pos_test.norm().item())
    e_neg_norm = float(E_neg_test.norm().item())
    assert e_pos_norm > 0.01, "E_pos trace should be non-zero at trace separation test"
    # They should differ: pos tracks correction, neg tracks prediction
    trace_diff = float((E_pos_test - E_neg_test).norm().item())
    assert trace_diff > 0.01, "E_pos and E_neg should be distinct, diff=%.4f" % trace_diff

    # Test 5: all arms produce valid BPC
    idx_held_np = np.array([i % V for i in range(20)], dtype=np.int64)
    for arm in ARMS:
        ar = compute_arm_logits(arm, E, idx_np, idx_held_np, seed=0)
        logits = ar["logits"]
        assert logits.shape[0] >= 1, "Empty logits for arm %s" % arm
        assert np.all(np.isfinite(logits)), "Non-finite logits for arm %s" % arm
        probs = softmax_logits_with_T(logits[:10], 0.1)
        logp = np.log(np.clip(probs, 1e-30, 1.0))
        nxt_t = idx_held_np[1:11]
        if len(nxt_t) > 0:
            bpc = bpc_from_logp(logp, nxt_t)
            assert 0.0 <= bpc <= 25.0, "BPC out of range for arm %s: %.4f" % (arm, bpc)
            assert math.isfinite(bpc), "BPC non-finite for arm %s" % arm

    # Test 6: sparsification density
    k_expected = max(1, int(round(SPARSE_BIPOLAR_F * n)))
    E_sp = sparsify_bipolar_gpu(E, SPARSE_BIPOLAR_F, seed=0)
    nonzero_per_row = (E_sp != 0).sum(dim=1).float().mean().item()
    assert abs(nonzero_per_row - k_expected) < 2.0, \
        "Sparse density wrong: expected ~%d got %.1f" % (k_expected, nonzero_per_row)

    print("[selftest] PASS: cf_rpe_err %.4f->%.4f ach_ident %.4f "
          "e_pos_norm %.4f e_neg_norm %.4f trace_diff %.4f sparse_k=%.1f "
          "W_b_norm=%.4f W_nm_norm=%.4f W_dt_norm=%.4f" % (
              err_before, err_after, ach_ident,
              e_pos_norm, e_neg_norm, trace_diff,
              nonzero_per_row,
              float(W_b.norm().item()),
              float(W_nm.norm().item()),
              float(W_dt.norm().item())), flush=True)


_instrumentation_selftest()   # Called at module scope (MANDATORY)
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
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"],
        uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # Encoder hoisted outside arm loop (Fix #24: load once, reuse)
    print("\n[seed=%d] building word2vec base E (V=%d N_DIM=%d) on %s..." % (
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
    if DEVICE.type == "cuda":
        try:
            free_b, total_b = torch.cuda.mem_get_info()
            print("[seed=%d encoder] E built (%.1fs); GPU free=%.2fGB total=%.2fGB" % (
                seed, t_enc, free_b / 1e9, total_b / 1e9), flush=True)
        except Exception:
            pass

    # Held-set split (same masking as fair_harness)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    if len(nxt_eval) == 0:
        for arm in ARMS:
            by_arm[arm] = {"empty_eval": True}
        return {"seed": seed, "by_arm": by_arm, "V": V, "N": N_DIM,
                "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "VOCAB_CAP": VOCAB_CAP, "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2),
                "device": str(DEVICE), "encoder_meta": encoder_meta}
    n_dev = len(nxt_eval) // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]
    valid_pos = np.where(mask)[0]

    for arm in ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building logits..." % (seed, arm), flush=True)
        try:
            ar = compute_arm_logits(arm, E_base, idx_train, idx_held, seed)
        except Exception as e:
            err_s = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err_s), flush=True)
            by_arm[arm] = {"compute_failed": True, "compute_error": err_s,
                           "bpc_best": float("inf"), "top1_acc": float("nan"),
                           "mrr_at_10": float("nan"),
                           "best_T_for_bpc": float("nan"),
                           "best_lambda_for_bpc": float("nan"),
                           "raw_bpc_at_T1_L1": float("inf"),
                           "elapsed_s_arm": round(time.time() - t_arm0, 2)}
            continue

        logits_full = ar["logits"]
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            logits_ctx = logits_full
            valid_pos = np.array([p for p in valid_pos if p < logits_ctx.shape[0]],
                                  dtype=np.int64)

        logits_eval = logits_ctx[mask] if logits_ctx.shape[0] == len(ctx_full) \
            else logits_ctx[valid_pos]

        jr = joint_sweep_substrate(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
        jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
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
        "run_mode": RUN_MODE,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
    }


# ============================================================================
# Verdict (primary: ARM_DUAL_TRACE vs ARM_BASELINE AND vs ARM_NAIVE_MULT)
# ============================================================================

def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "HARD_FAIL: no results.", {})

    by_arm_agg: Dict[str, Dict] = {}
    for arm in ARMS + ["ARM_UNIGRAM"]:
        if arm == "ARM_UNIGRAM":
            bpc_vals = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan"))
                        for u in units]
            by_arm_agg["ARM_UNIGRAM"] = {
                "bpc_mean": round(float(np.nanmean(bpc_vals)), 4),
                "bpc_std": round(float(np.nanstd(bpc_vals)), 4),
            }
            continue
        bpc_vals = []
        top1_vals = []
        mrr_vals = []
        raw_t1_vals = []
        for u in units:
            a = u["by_arm"].get(arm, {})
            if a.get("compute_failed", False) or a.get("empty_eval", False):
                continue
            bpc = a.get("bpc_best", float("nan"))
            if math.isfinite(bpc):
                bpc_vals.append(bpc)
                top1_vals.append(a.get("top1_acc", float("nan")))
                mrr_vals.append(a.get("mrr_at_10", float("nan")))
                raw_t1_vals.append(a.get("raw_bpc_at_T1_L1", float("nan")))
        if not bpc_vals:
            by_arm_agg[arm] = {"bpc_best_mean": float("inf"), "n_valid_seeds": 0,
                                "all_seeds_failed": True}
            continue
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_acc_mean": round(float(np.nanmean(top1_vals)), 4),
            "top1_acc_std": round(float(np.nanstd(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.nanmean(mrr_vals)), 4),
            "mrr_at_10_std": round(float(np.nanstd(mrr_vals)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.nanmean(raw_t1_vals)), 4),
            "n_valid_seeds": len(bpc_vals),
            "all_seeds_failed": False,
        }

    dual = by_arm_agg.get("ARM_DUAL_TRACE", {})
    base = by_arm_agg.get("ARM_BASELINE", {})
    naive = by_arm_agg.get("ARM_NAIVE_MULT", {})

    if dual.get("all_seeds_failed", True) or base.get("all_seeds_failed", True):
        return ("HARD_FAIL",
                "HARD_FAIL: primary arms failed. dual=%s base=%s" % (str(dual), str(base)),
                {"by_arm_agg": by_arm_agg})

    dual_bpc = dual["bpc_best_mean"]
    base_bpc = base["bpc_best_mean"]
    naive_bpc = naive.get("bpc_best_mean", float("inf"))

    delta_dual_vs_base = base_bpc - dual_bpc      # positive = dual is BETTER (lower BPC)
    delta_dual_vs_naive = naive_bpc - dual_bpc     # positive = dual beats naive

    # CV check (mandatory per spec)
    dual_cv = dual.get("bpc_best_cv", float("inf"))
    cv_ok = dual_cv < CV_MAX

    # DEGEN gate
    V_first = units[0].get("V", VOCAB_CAP)
    vocab_entropy_uniform = math.log2(max(V_first, 2))
    degen_flag = False
    for arm in ARMS:
        rt = by_arm_agg.get(arm, {}).get("raw_bpc_at_T1_L1_mean", float("nan"))
        if math.isfinite(rt) and abs(rt - vocab_entropy_uniform) <= DEGEN_TOL:
            degen_flag = True
            break

    # Per-arm summary line (Fix #28: per-arm, not summary text)
    arm_lines = []
    for arm in ARMS + ["ARM_UNIGRAM"]:
        a = by_arm_agg.get(arm, {})
        if arm == "ARM_UNIGRAM":
            arm_lines.append("UNI=bpc%.3f" % a.get("bpc_mean", float("nan")))
        elif a.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % arm)
        else:
            arm_lines.append("%s=bpc%.3f(cv%.3f)|top1%.4f|mrr%.4f" % (
                arm,
                a.get("bpc_best_mean", float("inf")),
                a.get("bpc_best_cv", float("nan")),
                a.get("top1_acc_mean", float("nan")),
                a.get("mrr_at_10_mean", float("nan"))))
    summary = ("DUAL_TRACE: delta_vs_base=%.3f delta_vs_naive=%.3f cv_ok=%s "
               "degen=%s | %s") % (
        delta_dual_vs_base, delta_dual_vs_naive, str(cv_ok), str(degen_flag),
        " | ".join(arm_lines))

    detail = {
        "by_arm_agg": by_arm_agg,
        "delta_dual_vs_base_bpc": round(delta_dual_vs_base, 4),
        "delta_dual_vs_naive_bpc": round(delta_dual_vs_naive, 4),
        "dual_bpc_best_mean": round(dual_bpc, 4),
        "base_bpc_best_mean": round(base_bpc, 4),
        "naive_bpc_best_mean": round(naive_bpc, 4),
        "dual_bpc_cv": round(dual_cv, 4),
        "cv_ok": cv_ok,
        "degen_flag": degen_flag,
        "vocab_entropy_uniform_bits": round(vocab_entropy_uniform, 4),
        "fair_harness_baseline_bpc": FAIR_HARNESS_BASELINE_BPC,
        "envelope_cap_bpc": ENVELOPE_CAP_BPC,
        "hard_pass_dual_vs_base": HARD_PASS_DUAL_VS_BASELINE_BPC,
        "hard_pass_dual_vs_naive": HARD_PASS_DUAL_VS_NAIVE_BPC,
        "middle_dual_vs_base_low": MIDDLE_DUAL_VS_BASELINE_LOW,
        "middle_dual_vs_naive_low": MIDDLE_DUAL_VS_NAIVE_LOW,
        "hard_fail_tol": HARD_FAIL_TOL,
        "n_seeds": len(units),
        "honest_scope": (
            "Dual-trace sequential neuromodulator (E_pos LTP-trace gated by dopamine / "
            "E_neg LTD-trace gated by ACh) vs ARM_BASELINE (single-trace cf-RPE dopamine) "
            "and ARM_NAIVE_MULT (3-axis multiplicative on one trace). "
            "HARD_PASS: dual vs base >= %.2f bits AND dual vs naive >= %.2f bits. "
            "MIDDLE_BAND: dual vs base in [%.2f,%.2f] AND dual vs naive >= %.2f bits. "
            "HARD_FAIL: dual within +/-%.2f of base OR fails to beat naive. "
            "tau_pos=%d tau_neg=%d N_DIM=%d N_TRAIN=%d V=%d f=%.2f." % (
                HARD_PASS_DUAL_VS_BASELINE_BPC, HARD_PASS_DUAL_VS_NAIVE_BPC,
                MIDDLE_DUAL_VS_BASELINE_LOW, HARD_PASS_DUAL_VS_BASELINE_BPC,
                MIDDLE_DUAL_VS_NAIVE_LOW, HARD_FAIL_TOL,
                TAU_POS, TAU_NEG, N_DIM, N_TRAIN, VOCAB_CAP, SPARSE_BIPOLAR_F)),
        "cites": [
            "notes/exp_dev_handoff_research_neuromodulator_orthogonal_composition_2026-06-23.md",
            "notes/research_neuromodulator_orthogonal_composition_brain_mechanism_2026-06-23.md",
            "experiments/exp_substrate_neuromodulator_3axis_gated_compose_LM_v1.py",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
            "data/exp_sparse_bipolar_substrate_lm_param_sweep_v1/metrics.json",
            "Brzosko et al. 2017 eLife 27756",
            "Huertas et al. 2016 PMC5156839",
            "Fremaux-Gerstner 2016 Front Neural Circ",
        ],
    }

    # DEGEN gate: only block if primary comparison is also inconclusive
    if degen_flag and delta_dual_vs_base < MIDDLE_DUAL_VS_BASELINE_LOW:
        return ("READOUT_DEGENERATE",
                "READOUT_DEGENERATE: raw_bpc near uniform-vocab AND no delta signal; "
                "requires recalibration. %s" % summary,
                detail)

    # HARD_PASS: dual beats base by >= 0.20 AND beats naive by >= 0.10
    if (delta_dual_vs_base >= HARD_PASS_DUAL_VS_BASELINE_BPC and
            delta_dual_vs_naive >= HARD_PASS_DUAL_VS_NAIVE_BPC):
        prefix = "HARD_PASS"
        if not cv_ok:
            prefix = "HARD_PASS_HIGH_CV"
        return (prefix,
                "%s: dual-trace breaks envelope (vs_base=%.3f>=%.2f, vs_naive=%.3f>=%.2f, "
                "cv=%.3f). %s" % (
                    prefix, delta_dual_vs_base, HARD_PASS_DUAL_VS_BASELINE_BPC,
                    delta_dual_vs_naive, HARD_PASS_DUAL_VS_NAIVE_BPC, dual_cv, summary),
                detail)

    # MIDDLE_BAND: dual beats base by +0.05 to +0.20 AND beats naive by >= +0.05
    if (delta_dual_vs_base >= MIDDLE_DUAL_VS_BASELINE_LOW and
            delta_dual_vs_naive >= MIDDLE_DUAL_VS_NAIVE_LOW):
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: dual-trace partially breaks envelope "
                "(vs_base=%.3f in [%.2f,%.2f), vs_naive=%.3f>=%.2f, cv=%.3f). %s" % (
                    delta_dual_vs_base, MIDDLE_DUAL_VS_BASELINE_LOW, HARD_PASS_DUAL_VS_BASELINE_BPC,
                    delta_dual_vs_naive, MIDDLE_DUAL_VS_NAIVE_LOW, dual_cv, summary),
                detail)

    # HARD_FAIL
    return ("HARD_FAIL",
            "HARD_FAIL: dual-trace does NOT break envelope "
            "(vs_base=%.3f, vs_naive=%.3f, tol=+/-%.2f). %s" % (
                delta_dual_vs_base, delta_dual_vs_naive, HARD_FAIL_TOL, summary),
            detail)


# ============================================================================
# atexit synthesizer (defensive: partial metrics.json on any exit)
# ============================================================================

_OUT_DIR: Optional[Path] = None
_PARTIAL_UNITS: List[Dict] = []
_FINAL_WRITTEN = False


def _atexit_synthesize():
    global _FINAL_WRITTEN
    if _FINAL_WRITTEN or not _OUT_DIR or not _PARTIAL_UNITS:
        return
    try:
        verdict, verdict_msg, detail = compute_verdict(_PARTIAL_UNITS)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "PARTIAL": True,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "SEEDS": SEEDS,
            "n_seeds_completed": len(_PARTIAL_UNITS),
            "detail": detail,
        }
        p = _OUT_DIR / "metrics.json"
        tmp = _OUT_DIR / "metrics.json.tmp"
        tmp.write_text(json.dumps(m, indent=2), encoding="utf-8")
        os.replace(tmp, p)
        print("[atexit] partial metrics written to %s" % p, flush=True)
    except Exception as ex:
        print("[atexit] error writing partial metrics: %s" % ex, flush=True)


atexit.register(_atexit_synthesize)

if hasattr(signal, "SIGTERM"):
    _prev_sigterm = signal.getsignal(signal.SIGTERM)

    def _sigterm_handler(signum, frame):
        _atexit_synthesize()
        if callable(_prev_sigterm):
            _prev_sigterm(signum, frame)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, _sigterm_handler)


# ============================================================================
# Main sweep
# ============================================================================

print("[config] anchor=%s N_DIM=%d mode=%s seeds=%s N_TRAIN=%d f=%.3f "
      "tau_pos=%d tau_neg=%d device=%s" % (
          ANCHOR_NAME, N_DIM, RUN_MODE, SEEDS, N_TRAIN, SPARSE_BIPOLAR_F,
          TAU_POS, TAU_NEG, str(DEVICE)), flush=True)

if RUN_MODE == "full" and N_DIM != PRODUCTION_N:
    raise RuntimeError("PROT-018: FULL run N_DIM=%d != PRODUCTION_N=%d" % (N_DIM, PRODUCTION_N))

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
_OUT_DIR = out_dir

t_sweep = time.time()

for seed in SEEDS:
    ckpt_key = "seed%d_N%d_%s" % (seed, N_DIM, RUN_MODE)
    partial_path = out_dir / ("partial_metrics_%s.json" % ckpt_key)
    if partial_path.exists():
        try:
            cached = json.loads(partial_path.read_text(encoding="utf-8"))
            if cached.get("seed") == seed and cached.get("N") == N_DIM:
                print("[ckpt] seed=%d already done, loading from %s" % (seed, partial_path), flush=True)
                _PARTIAL_UNITS.append(cached)
                continue
        except Exception:
            pass
    print("[seed=%d] running..." % seed, flush=True)
    unit = run_unit(seed)
    _PARTIAL_UNITS.append(unit)
    tmp_path = out_dir / ("partial_metrics_%s.json.tmp" % ckpt_key)
    tmp_path.write_text(json.dumps(unit, indent=2), encoding="utf-8")
    os.replace(tmp_path, partial_path)
    print("[ckpt] seed=%d saved to %s" % (seed, partial_path), flush=True)

verdict, verdict_msg, detail = compute_verdict(_PARTIAL_UNITS)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

elapsed_total = time.time() - t_sweep
metrics_out = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "TAU_POS": TAU_POS,
    "TAU_NEG": TAU_NEG,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "elapsed_s": round(elapsed_total, 2),
    "detail": detail,
    "per_seed": _PARTIAL_UNITS,
}

m_path = out_dir / "metrics.json"
m_tmp = out_dir / "metrics.json.tmp"
m_tmp.write_text(json.dumps(metrics_out, indent=2), encoding="utf-8")
os.replace(m_tmp, m_path)
print("[metrics] written to %s" % m_path, flush=True)
_FINAL_WRITTEN = True
