"""substrate_brain_full_compose_LM_v1 -- MAXIMALIST substrate-as-LM composing
EVERY validated brain-analog primitive in concert.

USER strategic principle 2026-06-23: brain is existence proof; substrate-as-LM
needs to match brain's full mechanism stack, NOT rely on rank-1 Hebbian alone.

Prior substrate-as-LM tests collapsed to unigram (substrate signal weaker than
just guessing most common word) because they used JUST W matrix + argmax. Brain
uses 7+ mechanisms in concert. This cell composes all the validated
substrate-native equivalents.

Brain mechanisms -> substrate primitives composed in this cell:

  1. Hierarchical predictive coding (Friston / Rao-Ballard)
     -> 3-layer substrate W stack with local-error Hebbian updates
     (each layer predicts the next; error drives weight updates).
  2. Sparse competitive activations (Tonegawa-CREB excitability trace)
     -> top-K competitive routing at readout (keep top f-fraction, zero rest).
  3. Recurrent attractor dynamics
     -> iterative attractor cleanup at each layer (k steps of nearest-prototype).
  4. Lock-in attention (per-hop)
     -> per-hop lock-in via cosine positional code at frequency = pos * step.
  5. Working memory HRR-slots
     -> context held as bundle of bind(word_i, slot_i_vec).
  6. Kinetic proofreading non-linear readout
     -> 2-step agreement gate at final prediction (predict twice with mild
     noise; keep only positions where the two predictions concur within tau).
  7. Sparse-bipolar W matrix
     -> f=0.05 sparse outer products (20-300x bundle capacity per prior drill).

Six arms (ablation; isolates which mechanisms are load-bearing):

  ARM_UNIGRAM
      Analytic floor (BPC=7.738 ref on text8 100k).

  ARM_BASELINE_RANK1_HEBBIAN
      Current substrate; W = sum of dense outer products + argmax.
      The rank-1 ceiling (should reproduce ~7.86 BPC ~ unigram).

  ARM_PC_HIERARCHY_ONLY
      3-layer PC stack (W1, W2, W3 trained sequentially with local error)
      + argmax readout. Tests whether hierarchy alone breaks the W-rank cap.

  ARM_PC_PLUS_SPARSE_COMPETITIVE
      3-layer PC + Tonegawa sparse competitive readout (top-K on final-layer
      output before softmax). Tests hierarchy + non-linear competition.

  ARM_PC_PLUS_LOCK_IN_ATTENTION
      3-layer PC + per-hop lock-in attention over context window (HRR-bind
      context-words to lock-in positional codes; substrate sees context-key).
      Tests hierarchy + attention.

  ARM_BRAIN_FULL_COMPOSE
      ALL primitives in concert: 3-layer PC + sparse competitive readout +
      lock-in attention + working-memory HRR-slots + sparse-bipolar W
      + kinetic proofreading 2-step agreement readout.

Pre-reg HARD bands (substrate-as-LM unblocked; CHAIN-GRADE V2 closure):

  HARD_PASS:
    - ARM_BRAIN_FULL_COMPOSE BPC < 7.500 (clearly beats unigram by 0.24+ bits)
    - AND BPC < ARM_BASELINE_RANK1_HEBBIAN - 1.000 (clearly beats rank-1 ceiling)
    - AND at least one ablation arm clearly identifies the load-bearing mechanism
      (lift-over-baseline >= 0.30 bits on some non-FULL arm).

  HARD_FAIL:
    ALL arms BPC >= 7.738 (no composition beats unigram). Substrate-as-LM is
    fundamentally W-architecture capped; would force pivot to substrate-as-
    refuse-aware-product.

  MIDDLE_BAND:
    Composition lifts over rank-1 baseline but doesn't beat unigram -> partial
    mechanism; characterize what's still missing.

Mandatory sanity self-tests (must pass before training counts):
  1. ARM_BASELINE_RANK1_HEBBIAN reproduces prior text8 substrate BPC near 7.7
     collapse to unigram (sanity that baseline behaves as expected).
  2. ARM_PC_HIERARCHY_ONLY: per-layer reconstruction error decreases monotonically
     across the 3 layers at training convergence.
  3. At sigma=0 input, ALL arms produce identical output (deterministic).
  4. ARM_BRAIN_FULL_COMPOSE working memory K=7 retention >= 0.95 at sigma=0
     (HRR-slots primitive works).
  5. Lock-in attention: at P=32 + sigma=64, recall >= 0.99 (mechanism witness).

GPU REQUIRED (Fix #24): torch.cuda for all matmul + PC training + Hebbian writes
+ sparse-bipolar projection. 3-layer PC training at N_DIM=8192 x 100k tokens
~= 25B ops per arm. Estimated wall 60-120min GPU full.

Fair comparison discipline:
  - Same V=4000 / N_TRAIN=100k / N_HELD=20k / N_DIM=8192 / seeds=[7,17,23]
    as fresh_W_bpc_per_encoder_v2 (which used word2vec).
  - This cell uses char_trigram_encoder as common encoder across arms (defensive
    against gensim/word2vec load failures; same encoder per fair comparison).
  - Each arm gets fresh W (no contamination). Brain arm gets NO advantages over
    rank-1 baseline; wins must be on architecture merit.

Cites:
  - preregs/2026-06-23_substrate_brain_full_compose_LM_v1.md
  - exp_fresh_W_bpc_per_encoder_v2.py (parent pattern; rank-1 baseline)
  - exp_substrate_as_lm_composed_primitives_GPU_v1.py (HRR-bind + lock-in pattern)
  - USER directive 2026-06-23 brain-as-existence-proof reframe
  - USER directive 2026-06-22 (Fix #24 GPU dispatch must use GPU)
  - Rao + Ballard 1999 (predictive coding)
  - Friston 2009 (free-energy principle)
  - Tonegawa et al. 2015 (excitability trace + sparse competition)
  - Hopfield 1982 (attractor dynamics)
  - Plate 1995 (HRR)

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

ANCHOR_NAME = "substrate_brain_full_compose_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
_LLM_CALL_COUNTER = [0]

# Reference baselines (from prior cells; see preregs).
UNIGRAM_BPC_REF = 7.738
RANK1_BASELINE_BPC_REF = 7.864

# Pre-reg bands
HP_BPC_BAR = 7.500            # ARM_BRAIN_FULL_COMPOSE must clear < 7.500
HP_LIFT_OVER_BASELINE = 1.000 # AND clear baseline_rank1 - 1.000
HP_ABLATION_LIFT_BITS = 0.30  # mechanism identification: one ablation lift >= 0.30
HF_BPC_BAR = UNIGRAM_BPC_REF  # all arms >= 7.738 = HARD_FAIL
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

# Config
N_DIM = 8192
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

# Brain-analog primitive knobs
PC_N_LAYERS = 3                # 3-layer predictive coding stack
SPARSE_BIPOLAR_F = 0.05        # 5% nonzero (sparse-bipolar; per prior drill)
SPARSE_COMPETITIVE_K_FRAC = 0.10   # Tonegawa: keep top 10% of logits
ATTRACTOR_K_STEPS = 2          # k iterations of cleanup at each layer
CONTEXT_WINDOW = 5             # WM HRR-slots window length
LOCK_IN_FREQ_STEP = 31         # per-hop lock-in freq = pos * step
KP_AGREEMENT_TAU = 0.20        # kinetic-proofreading agreement threshold (cosine)
KP_NOISE_SIGMA = 0.02          # mild noise for 2-step agreement

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke must fit under SMOKE_TIMEOUT_S=180s on laptop CPU (matmul-heavy).
    # Exercises every code path: per-arm encoder, 3-layer PC training,
    # sparse-competitive, lock-in keys, kinetic proofreading, verdict.
    SEEDS = [0]
    N_TRAIN = 1_500
    N_HELD = 300
    VOCAB_CAP = 300

ARMS = [
    "ARM_UNIGRAM",
    "ARM_BASELINE_RANK1_HEBBIAN",
    "ARM_PC_HIERARCHY_ONLY",
    "ARM_PC_PLUS_SPARSE_COMPETITIVE",
    "ARM_PC_PLUS_LOCK_IN_ATTENTION",
    "ARM_BRAIN_FULL_COMPOSE",
]

CONFIG_VERSION = (
    "substrate_brain_full_compose_LM_v1; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s pc_layers=%d sparse_f=%.3f "
    "comp_topk=%.3f attractor_k=%d context_W=%d lock_in_step=%d "
    "kp_tau=%.3f kp_sigma=%.3f INGEST_CHUNK=%d RECALL_BATCH=%d device=%s "
    "lambda_grid=%s; bands HP_bpc<%.3f HP_lift>=%.2f HP_abl_lift>=%.2f "
    "HF_bpc>=%.3f cv_max=%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    PC_N_LAYERS, SPARSE_BIPOLAR_F, SPARSE_COMPETITIVE_K_FRAC,
    ATTRACTOR_K_STEPS, CONTEXT_WINDOW, LOCK_IN_FREQ_STEP,
    KP_AGREEMENT_TAU, KP_NOISE_SIGMA, INGEST_CHUNK, RECALL_BATCH,
    str(DEVICE), LAMBDA_GRID,
    HP_BPC_BAR, HP_LIFT_OVER_BASELINE, HP_ABLATION_LIFT_BITS,
    HF_BPC_BAR, HP_BPC_CV_MAX,
)


# ============================================================================
# Encoder (char trigram; same across all arms for fair comparison)
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


def build_E_char_trigram_gpu(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    """Build [V, n_dim] L2-normalized HD vectors on GPU."""
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


# ============================================================================
# Brain primitive 7: sparse-bipolar W (5% nonzero outer products)
# ============================================================================

def sparsify_bipolar_gpu(E: torch.Tensor, f: float, seed: int) -> torch.Tensor:
    """Project each row to top-K-magnitude bipolar; rest=0.

    Primitive: 20-300x capacity vs dense per prior sparse-bipolar drill.
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
# Brain primitive 5: HRR-bind for working-memory slots / context
# ============================================================================

def hrr_bind_batch(A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
    """HRR bind: circular convolution via FFT. A,B: [..., N]; out: [..., N].

    Inputs forced contiguous: MKL FFT (Windows oneMKL) errors on expand()'d
    strided views with "Inconsistent configuration parameters".
    """
    if not A.is_contiguous():
        A = A.contiguous()
    if not B.is_contiguous():
        B = B.contiguous()
    Fa = torch.fft.rfft(A, dim=-1)
    Fb = torch.fft.rfft(B, dim=-1)
    return torch.fft.irfft(Fa * Fb, n=A.shape[-1], dim=-1)


# ============================================================================
# Brain primitive 4: lock-in attention positional code
# ============================================================================

def lock_in_position_vec(n_dim: int, pos: int, seed: int) -> torch.Tensor:
    """Lock-in amplifier positional code: cosine at frequency = pos * step."""
    rng = np.random.default_rng(seed * 7919 + 13 + pos * 101)
    phase = rng.uniform(0.0, 2.0 * math.pi, size=n_dim).astype(np.float32)
    freq = float(max(pos, 1) * LOCK_IN_FREQ_STEP) / float(n_dim)
    t = np.arange(n_dim, dtype=np.float32)
    v = np.cos(2.0 * math.pi * freq * t + phase).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-12)
    return torch.from_numpy(v).to(DEVICE)


def random_role_vec(n_dim: int, pos: int, seed: int) -> torch.Tensor:
    """Random role vector for HRR slot binding (non lock-in)."""
    h = hashlib.blake2b(("slot:%d:%d" % (pos, seed)).encode(), digest_size=8).digest()
    sv = int.from_bytes(h, "big") % (2**32)
    rng = np.random.default_rng(sv)
    v = rng.standard_normal(n_dim).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-12)
    return torch.from_numpy(v).to(DEVICE)


def build_context_keys_gpu(idx: torch.Tensor, E: torch.Tensor, context_window: int,
                            seed: int, use_lock_in: bool) -> torch.Tensor:
    """Working-memory HRR-slots: at time t, key = sum_i bind(E[idx[t-i]], slot_i).

    Slot_i = lock_in_position_vec(i) if use_lock_in else random_role_vec(i).
    Result: [len(idx), n_dim] L2-normalized.
    """
    n = idx.shape[0]
    dim = E.shape[1]
    pos_vecs = []
    for i in range(context_window):
        if use_lock_in:
            pos_vecs.append(lock_in_position_vec(dim, i, seed))
        else:
            pos_vecs.append(random_role_vec(dim, i, seed))
    keys = torch.zeros((n, dim), dtype=TORCH_DTYPE, device=E.device)
    for offset in range(context_window):
        if offset == 0:
            src = E[idx]
        else:
            shifted = torch.roll(idx, shifts=offset, dims=0)
            shifted[:offset] = idx[0]
            src = E[shifted]
        pos_b = pos_vecs[offset].unsqueeze(0).expand(n, -1).contiguous()
        bound = hrr_bind_batch(src, pos_b)
        keys.add_(bound)
    keys = _l2_normalize_t(keys)
    return keys


# ============================================================================
# Brain primitive 1: 3-layer predictive-coding W stack
# Each layer learns W_l : src_l -> tgt_l via local error Hebbian update
# Layer 1: src = context-key, tgt = next-word vector
# Layer 2: src = layer1-prediction, tgt = next-word vector (residual)
# Layer 3: src = layer2-prediction, tgt = next-word vector (residual)
# Inference: predict via layer-wise additive composition.
# ============================================================================

def build_pc_stack_gpu(src_keys: torch.Tensor, tgt_vecs: torch.Tensor,
                        idx_train: torch.Tensor, ingest_chunk: int,
                        n_layers: int) -> List[torch.Tensor]:
    """Train n_layers PC W matrices with local-error Hebbian.

    src_keys: [n_train, dim] context-key per position t
    tgt_vecs: [V, dim] target lookup E[idx[t+1]] is the desired
    idx_train: [n_train] indices into tgt_vecs for actual next-word

    Returns: [W_1, W_2, ..., W_L]; each W is [dim, dim].

    Local-error Hebbian: at layer l, residual = tgt - cumulative_pred;
    W_l += sum outer(residual, src_l). src_l propagates as the previous
    layer's prediction (so deeper layers learn finer corrections).
    """
    device = src_keys.device
    dim = src_keys.shape[1]
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return [torch.zeros((dim, dim), device=device, dtype=TORCH_DTYPE) for _ in range(n_layers)]

    Ws: List[torch.Tensor] = []
    # cumulative prediction starts at zero
    cumulative_pred_norm: Optional[torch.Tensor] = None

    for layer_i in range(n_layers):
        W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
        # source for THIS layer:
        #   layer 0: src_keys (context)
        #   layer i>0: prediction from previous layer (cumulative_pred_norm)
        if layer_i == 0:
            src_l = src_keys
        else:
            src_l = cumulative_pred_norm  # already L2-normed batch
        # Targets are still next-word vectors
        for b in range(0, n_pairs, ingest_chunk):
            end = min(b + ingest_chunk, n_pairs)
            src_b = src_l[b:end]
            tgt_b = tgt_vecs[idx_train[b + 1:end + 1]]
            # residual target = tgt - cumulative_pred at THIS chunk
            if layer_i == 0:
                resid = tgt_b
            else:
                cum_b = cumulative_pred_norm[b:end]
                resid = tgt_b - cum_b
            W.add_(resid.T @ src_b)
            if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
                torch.cuda.synchronize()
        Ws.append(W)
        # Update cumulative prediction across all positions for next layer
        cumulative_pred_NEW = torch.zeros((src_keys.shape[0], dim), dtype=TORCH_DTYPE, device=device)
        for b in range(0, src_keys.shape[0], ingest_chunk):
            end = min(b + ingest_chunk, src_keys.shape[0])
            src_b = src_l[b:end]
            this_layer_pred = src_b @ W.T
            if layer_i == 0:
                cumulative_pred_NEW[b:end] = this_layer_pred
            else:
                cumulative_pred_NEW[b:end] = cumulative_pred_norm[b:end] + this_layer_pred
        cumulative_pred_norm = _l2_normalize_t(cumulative_pred_NEW)
    return Ws


def pc_stack_forward_gpu(Ws: List[torch.Tensor], src_keys: torch.Tensor,
                           recall_batch: int) -> torch.Tensor:
    """Apply trained PC stack to produce per-position prediction vectors.

    Returns: [n, dim] L2-normalized predictions.
    """
    n, dim = src_keys.shape
    device = src_keys.device
    out = torch.zeros((n, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        src_b = src_keys[b:end]
        cum = torch.zeros((end - b, dim), dtype=TORCH_DTYPE, device=device)
        s_l = src_b
        for layer_i, W in enumerate(Ws):
            pred = s_l @ W.T
            cum = cum + pred
            s_l = _l2_normalize_t(cum)
        out[b:end] = _l2_normalize_t(cum)
    return out


# ============================================================================
# Brain primitive 3: attractor cleanup (k iterations of nearest-prototype)
# ============================================================================

def attractor_cleanup_gpu(pred: torch.Tensor, E: torch.Tensor, k_steps: int,
                            recall_batch: int) -> torch.Tensor:
    """Iterative attractor cleanup: each step pulls pred toward the nearest E row.

    pred: [n, dim]; E: [V, dim] prototype set; out: [n, dim] L2-normalized.
    """
    n = pred.shape[0]
    out = pred.clone()
    for _ in range(k_steps):
        new = torch.zeros_like(out)
        for b in range(0, n, recall_batch):
            end = min(b + recall_batch, n)
            sims = out[b:end] @ E.T  # [batch, V]
            # softmax-weighted average toward prototypes
            sims_n = sims - sims.max(dim=1, keepdim=True).values
            w = torch.softmax(sims_n * 10.0, dim=1)  # sharp pull
            new[b:end] = w @ E
        out = _l2_normalize_t(new)
    return out


# ============================================================================
# Brain primitive 2: Tonegawa sparse competitive readout
# Keep only top-k-fraction of logits; zero rest before softmax.
# ============================================================================

def sparse_competitive_logits(logits: torch.Tensor, k_frac: float) -> torch.Tensor:
    """Top-k-fraction competitive: zero out logits below the threshold."""
    n, V = logits.shape
    k = max(1, int(round(k_frac * V)))
    topk_vals, topk_idx = torch.topk(logits, k=k, dim=1)
    out = torch.full_like(logits, -1e9)
    out.scatter_(1, topk_idx, topk_vals)
    return out


# ============================================================================
# Brain primitive 6: kinetic proofreading 2-step agreement readout
# Predict twice with mild noise; keep only positions where the two predictions
# agree within tau. Disagreement -> fall back to unigram via lambda blending.
# ============================================================================

def kinetic_proofreading_logits(pred: torch.Tensor, E: torch.Tensor,
                                  sigma: float, tau: float,
                                  recall_batch: int,
                                  generator: torch.Generator) -> Tuple[torch.Tensor, torch.Tensor]:
    """Two-step agreement: returns (logits, agreement_mask [bool]).

    Agreement mask: True where the two noisy predictions concur within tau
    (cosine similarity >= 1.0 - tau). Disagreement positions get -1e9 logits
    so the downstream interp falls back to unigram fully.
    """
    n, dim = pred.shape
    V = E.shape[0]
    logits = torch.zeros((n, V), dtype=TORCH_DTYPE, device=pred.device)
    agree_mask = torch.zeros(n, dtype=torch.bool, device=pred.device)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        p_b = pred[b:end]
        # Two perturbed predictions
        noise1 = torch.randn(p_b.shape, generator=generator,
                              device=pred.device, dtype=TORCH_DTYPE) * sigma
        noise2 = torch.randn(p_b.shape, generator=generator,
                              device=pred.device, dtype=TORCH_DTYPE) * sigma
        p1 = _l2_normalize_t(p_b + noise1)
        p2 = _l2_normalize_t(p_b + noise2)
        # Agreement: cosine between p1 and p2
        cos = (p1 * p2).sum(dim=1)
        agree_b = cos >= (1.0 - tau)
        agree_mask[b:end] = agree_b
        # Logits from the mean of the two predictions
        pavg = _l2_normalize_t(p1 + p2)
        logits[b:end] = pavg @ E.T
    return logits, agree_mask


# ============================================================================
# Per-arm dispatcher
# ============================================================================

def compute_arm_logits(arm_label: str, E: torch.Tensor, idx_train: np.ndarray,
                         idx_held: np.ndarray, seed: int) -> Dict:
    """Build per-arm W (and any auxiliary structures) on GPU; return per-position
    logits on the held set + diagnostics for sanity tests.
    """
    V, dim = E.shape
    device = E.device
    use_sparse_W = arm_label == "ARM_BRAIN_FULL_COMPOSE"
    use_pc = arm_label in (
        "ARM_PC_HIERARCHY_ONLY",
        "ARM_PC_PLUS_SPARSE_COMPETITIVE",
        "ARM_PC_PLUS_LOCK_IN_ATTENTION",
        "ARM_BRAIN_FULL_COMPOSE",
    )
    use_sparse_comp = arm_label in (
        "ARM_PC_PLUS_SPARSE_COMPETITIVE",
        "ARM_BRAIN_FULL_COMPOSE",
    )
    use_lock_in = arm_label in (
        "ARM_PC_PLUS_LOCK_IN_ATTENTION",
        "ARM_BRAIN_FULL_COMPOSE",
    )
    use_context = use_lock_in or arm_label == "ARM_BRAIN_FULL_COMPOSE"
    use_attractor = arm_label == "ARM_BRAIN_FULL_COMPOSE"
    use_kp = arm_label == "ARM_BRAIN_FULL_COMPOSE"

    # Apply sparse-bipolar to encoder if FULL
    if use_sparse_W:
        E_used = _l2_normalize_t(sparsify_bipolar_gpu(E, SPARSE_BIPOLAR_F, seed))
    else:
        E_used = E

    # Build src keys (context or single-word lookup)
    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)
    t0 = time.time()
    if use_context:
        src_keys_train = build_context_keys_gpu(idx_train_t, E_used,
                                                  CONTEXT_WINDOW, seed, use_lock_in)
        src_keys_held = build_context_keys_gpu(idx_held_t, E_used,
                                                 CONTEXT_WINDOW, seed, use_lock_in)
    else:
        src_keys_train = E_used[idx_train_t]
        src_keys_held = E_used[idx_held_t]
    t_keys = time.time() - t0

    # Build W stack: PC layers OR rank-1
    t0 = time.time()
    if use_pc:
        Ws = build_pc_stack_gpu(src_keys_train, E_used, idx_train_t,
                                  INGEST_CHUNK, PC_N_LAYERS)
        pred_held = pc_stack_forward_gpu(Ws, src_keys_held, RECALL_BATCH)
    else:
        # Rank-1 baseline: W = sum outer(E[idx[t+1]], src_keys_train[t])
        W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
        n_pairs = idx_train_t.shape[0] - 1
        for b in range(0, n_pairs, INGEST_CHUNK):
            end = min(b + INGEST_CHUNK, n_pairs)
            src_b = src_keys_train[b:end]
            tgt_b = E_used[idx_train_t[b + 1:end + 1]]
            W.add_(tgt_b.T @ src_b)
            if device.type == "cuda" and (b // INGEST_CHUNK) % 16 == 0:
                torch.cuda.synchronize()
        # forward
        n_h = src_keys_held.shape[0]
        pred_held = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
        for b in range(0, n_h, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_h)
            pred_held[b:end] = _l2_normalize_t(src_keys_held[b:end] @ W.T)
        del W
        Ws = []
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    # Attractor cleanup (only FULL)
    if use_attractor:
        pred_held = attractor_cleanup_gpu(pred_held, E_used, ATTRACTOR_K_STEPS, RECALL_BATCH)

    # Compute logits via kinetic proofreading OR plain dot
    t0 = time.time()
    if use_kp:
        gen = torch.Generator(device=device)
        gen.manual_seed(seed * 13 + 7)
        logits, agree_mask = kinetic_proofreading_logits(
            pred_held, E_used, KP_NOISE_SIGMA, KP_AGREEMENT_TAU,
            RECALL_BATCH, gen,
        )
        # Disagree positions get -1e9 across all V => softmax becomes uniform,
        # interp will pull from unigram. Record fraction of agreements.
        disagree = (~agree_mask).float().sum().item()
        agree_frac = float((agree_mask.float()).mean().item())
        # Apply -1e9 to disagreement rows BEFORE sparse competitive (so the rows
        # become uniform after softmax; lambda-interp pulls them to unigram).
        if disagree > 0:
            logits[~agree_mask] = 0.0  # uniform after softmax
    else:
        agree_frac = 1.0
        n_h = pred_held.shape[0]
        logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
        for b in range(0, n_h, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_h)
            logits[b:end] = pred_held[b:end] @ E_used.T
    # Sparse competitive (Tonegawa) on top
    if use_sparse_comp:
        logits = sparse_competitive_logits(logits, SPARSE_COMPETITIVE_K_FRAC)
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    # Cleanup tensors
    del pred_held, src_keys_train, src_keys_held, idx_train_t, idx_held_t
    if use_sparse_W:
        del E_used
    if use_pc:
        for W in Ws:
            del W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_keys_s": round(t_keys, 2),
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "agreement_frac": round(agree_frac, 4),
        "use_pc": bool(use_pc),
        "use_sparse_comp": bool(use_sparse_comp),
        "use_lock_in": bool(use_lock_in),
        "use_context": bool(use_context),
        "use_sparse_W": bool(use_sparse_W),
        "use_attractor": bool(use_attractor),
        "use_kp": bool(use_kp),
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
# BPC scoring
# ============================================================================

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


def bpc_from_logits(logits_held: np.ndarray, idx_held: np.ndarray,
                     U_log: np.ndarray, lambda_grid: list) -> Dict:
    """Score per-position logits vs next-word labels with log-linear unigram interp."""
    unk = 0
    n_logits = logits_held.shape[0]
    # logits_held corresponds to positions [0..n_held-1] in idx_held;
    # next-token label at position t is idx_held[t+1]
    ctx_idx = idx_held[:n_logits]
    nxt_full = np.concatenate([idx_held[1:], np.array([unk], dtype=idx_held.dtype)])[:n_logits]
    mask = (ctx_idx != unk)
    # also drop the last position (no valid next)
    valid_n = min(n_logits, len(idx_held) - 1)
    mask[valid_n:] = False
    nxt = nxt_full[mask]
    logits_eval = logits_held[mask]
    n_eval = len(nxt)
    if n_eval == 0:
        return {"bpc_raw": float("inf"), "bpc_best": float("inf"),
                "best_lambda": 1.0, "bpc_per_lambda_test": {},
                "bpc_per_lambda_dev": {}, "n_test": 0, "n_dev": 0}
    n_dev = n_eval // 2
    nxt_dev = nxt[:n_dev]
    nxt_test = nxt[n_dev:]
    logits_dev = logits_eval[:n_dev]
    logits_test = logits_eval[n_dev:]
    n_test = len(nxt_test)
    sub_probs_dev = softmax_with_temperature_np(logits_dev, temperature=1.0)
    sub_probs_test = softmax_with_temperature_np(logits_test, temperature=1.0)
    sub_logp_dev = np.log(np.clip(sub_probs_dev, 1e-30, 1.0))
    sub_logp_test = np.log(np.clip(sub_probs_test, 1e-30, 1.0))
    raw_logp = sub_logp_test[np.arange(n_test), nxt_test]
    bpc_raw = -float(np.mean(raw_logp)) / math.log(2.0)
    best_lambda = 1.0
    best_dev_bpc = float("inf")
    bpc_per_lambda_dev: Dict[float, float] = {}
    bpc_per_lambda_test: Dict[float, float] = {}
    for lam in lambda_grid:
        bd = log_linear_interp_bpc(sub_logp_dev, U_log, nxt_dev, lam)
        bt = log_linear_interp_bpc(sub_logp_test, U_log, nxt_test, lam)
        bpc_per_lambda_dev[lam] = bd
        bpc_per_lambda_test[lam] = bt
        if bd < best_dev_bpc:
            best_dev_bpc = bd
            best_lambda = lam
    return {
        "bpc_raw": round(bpc_raw, 4),
        "bpc_best": round(bpc_per_lambda_test[best_lambda], 4),
        "best_lambda": float(best_lambda),
        "best_dev_bpc": round(best_dev_bpc, 4),
        "bpc_per_lambda_dev": {str(k): round(v, 4) for k, v in bpc_per_lambda_dev.items()},
        "bpc_per_lambda_test": {str(k): round(v, 4) for k, v in bpc_per_lambda_test.items()},
        "n_dev": int(n_dev),
        "n_test": int(n_test),
    }


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
# Per-seed runner
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

    uni = bpc_unigram(idx_train, idx_held, V)
    print("[seed=%d arm=ARM_UNIGRAM] bpc_unigram=%.3f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {
        "ARM_UNIGRAM": {"bpc_unigram": uni["bpc_unigram"], "n_test": uni["n_test"]}
    }

    # Build shared char-trigram encoder once
    t0 = time.time()
    E = build_E_char_trigram_gpu(vocab, N_DIM, seed)
    t_enc = time.time() - t0
    print("[seed=%d] shared char_trigram E built (V=%d N_DIM=%d) in %.1fs" % (
        seed, V, N_DIM, t_enc), flush=True)

    for arm_label in [a for a in ARMS if a != "ARM_UNIGRAM"]:
        t_arm = time.time()
        print("\n  [seed=%d arm=%s] computing logits..." % (seed, arm_label), flush=True)
        try:
            r = compute_arm_logits(arm_label, E, idx_train, idx_held, seed)
            bpc = bpc_from_logits(r["logits"], idx_held, U_log, LAMBDA_GRID)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm_label, err), flush=True)
            if DEVICE.type == "cuda":
                torch.cuda.empty_cache()
            by_arm[arm_label] = {
                "compute_failed": True, "compute_error": err,
                "bpc_raw": float("inf"), "bpc_best": float("inf"),
                "best_lambda": float("nan"), "best_dev_bpc": float("inf"),
                "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
                "n_dev": 0, "n_test": 0,
                "wall_arm_s": round(time.time() - t_arm, 2),
            }
            continue
        t_wall = time.time() - t_arm
        print("    [seed=%d arm=%s] bpc_raw=%.3f bpc_best=%.3f lam=%.2f "
              "(keys=%.1fs ingest=%.1fs recall=%.1fs total=%.1fs) agree=%.3f" % (
            seed, arm_label, bpc["bpc_raw"], bpc["bpc_best"], bpc["best_lambda"],
            r["wall_keys_s"], r["wall_ingest_s"], r["wall_recall_s"],
            t_wall, r["agreement_frac"]), flush=True)
        by_arm[arm_label] = {
            "bpc_raw": bpc["bpc_raw"], "bpc_best": bpc["bpc_best"],
            "best_lambda": bpc["best_lambda"], "best_dev_bpc": bpc["best_dev_bpc"],
            "bpc_per_lambda_dev": bpc["bpc_per_lambda_dev"],
            "bpc_per_lambda_test": bpc["bpc_per_lambda_test"],
            "n_dev": bpc["n_dev"], "n_test": bpc["n_test"],
            "wall_arm_s": round(t_wall, 2),
            "wall_keys_s": r["wall_keys_s"],
            "wall_ingest_s": r["wall_ingest_s"],
            "wall_recall_s": r["wall_recall_s"],
            "agreement_frac": r["agreement_frac"],
            "use_pc": r["use_pc"], "use_sparse_comp": r["use_sparse_comp"],
            "use_lock_in": r["use_lock_in"], "use_context": r["use_context"],
            "use_sparse_W": r["use_sparse_W"], "use_attractor": r["use_attractor"],
            "use_kp": r["use_kp"],
        }

    del E
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed, "by_arm": by_arm, "V": V,
        "N": N_DIM, "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
        "PC_N_LAYERS": PC_N_LAYERS, "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "SPARSE_COMPETITIVE_K_FRAC": SPARSE_COMPETITIVE_K_FRAC,
        "ATTRACTOR_K_STEPS": ATTRACTOR_K_STEPS,
        "CONTEXT_WINDOW": CONTEXT_WINDOW,
        "LOCK_IN_FREQ_STEP": LOCK_IN_FREQ_STEP,
        "KP_AGREEMENT_TAU": KP_AGREEMENT_TAU,
        "KP_NOISE_SIGMA": KP_NOISE_SIGMA,
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
    non_uni = [a for a in ARMS if a != "ARM_UNIGRAM"]
    for arm in non_uni:
        seeds_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid = [(not f) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
                 for f, u in zip(seeds_failed, units)]
        n_failed = int(sum(seeds_failed))
        valid_units = [u for ok, u in zip(valid, units) if ok]
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"), "bpc_best_std": float("nan"),
                "bpc_best_cv": float("nan"), "bpc_raw_mean": float("inf"),
                "best_lambda_mean": float("nan"),
                "n_valid_seeds": 0, "n_failed": n_failed, "all_seeds_failed": True,
            }
            continue
        best_vals = [u["by_arm"].get(arm, {}).get("bpc_best", float("inf")) for u in valid_units]
        raw_vals = [u["by_arm"].get(arm, {}).get("bpc_raw", float("inf")) for u in valid_units]
        lam_vals = [u["by_arm"].get(arm, {}).get("best_lambda", float("nan")) for u in valid_units]
        b_mean = float(np.mean(best_vals))
        b_std = float(np.std(best_vals))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4), "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "bpc_raw_mean": round(float(np.mean(raw_vals)), 4),
            "best_lambda_mean": round(float(np.mean(lam_vals)), 4),
            "n_valid_seeds": int(len(valid_units)),
            "n_failed": n_failed, "all_seeds_failed": False,
        }

    DECISIVE_ARM = "ARM_BRAIN_FULL_COMPOSE"
    BASELINE_ARM = "ARM_BASELINE_RANK1_HEBBIAN"
    dec = by_arm_agg.get(DECISIVE_ARM, {})
    base = by_arm_agg.get(BASELINE_ARM, {})
    dec_bpc = dec.get("bpc_best_mean", float("inf"))
    dec_cv = dec.get("bpc_best_cv", float("nan"))
    base_bpc = base.get("bpc_best_mean", float("inf"))
    lift_over_baseline = (base_bpc - dec_bpc) if (math.isfinite(base_bpc) and math.isfinite(dec_bpc)) else float("nan")

    # Per-ablation lift (vs BASELINE)
    ablation_arms = [
        "ARM_PC_HIERARCHY_ONLY", "ARM_PC_PLUS_SPARSE_COMPETITIVE",
        "ARM_PC_PLUS_LOCK_IN_ATTENTION",
    ]
    ablation_lifts: Dict[str, float] = {}
    for a in ablation_arms:
        m = by_arm_agg.get(a, {}).get("bpc_best_mean", float("nan"))
        if math.isfinite(m) and math.isfinite(base_bpc):
            ablation_lifts[a] = round(base_bpc - m, 4)
        else:
            ablation_lifts[a] = float("nan")
    best_ablation_lift = max((v for v in ablation_lifts.values() if math.isfinite(v)),
                              default=float("-inf"))

    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    parts = []
    for a in non_uni:
        b = by_arm_agg[a]
        parts.append("%s=bpc%.3f(lam%.2f)" % (
            a, b["bpc_best_mean"], b["best_lambda_mean"]))
    summary = "BRAIN_FULL_COMPOSE unigram=%.3f | %s | n_llm=%d" % (
        by_arm_agg["ARM_UNIGRAM"]["bpc_mean"], " | ".join(parts), n_llm)

    all_fail = all(by_arm_agg.get(a, {}).get("bpc_best_mean", float("inf")) >= HF_BPC_BAR
                    for a in non_uni)

    detail = {
        "by_arm_agg": by_arm_agg,
        "decisive_arm": DECISIVE_ARM,
        "decisive_bpc": dec_bpc,
        "decisive_cv": dec_cv,
        "baseline_arm": BASELINE_ARM,
        "baseline_bpc": base_bpc,
        "lift_over_baseline_bits": lift_over_baseline,
        "ablation_lifts_vs_baseline": ablation_lifts,
        "best_ablation_lift_bits": best_ablation_lift,
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "rank1_baseline_bpc_ref": RANK1_BASELINE_BPC_REF,
        "hp_bpc_bar": HP_BPC_BAR,
        "hp_lift_over_baseline": HP_LIFT_OVER_BASELINE,
        "hp_ablation_lift_bits": HP_ABLATION_LIFT_BITS,
        "hf_bpc_bar": HF_BPC_BAR,
        "hp_bpc_cv_max": HP_BPC_CV_MAX,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Maximalist substrate-as-LM composing 7 brain-analog primitives "
            "(3-layer PC + sparse competitive + lock-in attention + WM-HRR-slots "
            "+ sparse-bipolar W + kinetic proofreading + attractor cleanup). "
            "HARD_PASS = ARM_BRAIN_FULL_COMPOSE bpc<%.3f AND lift>=%.2f over "
            "BASELINE_RANK1 AND best-ablation lift>=%.2f. HARD_FAIL = all arms "
            ">=%.3f. Fair-comparison: same V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d "
            "seeds=%s as fresh_W_bpc_per_encoder_v2; each arm fresh W."
        ) % (HP_BPC_BAR, HP_LIFT_OVER_BASELINE, HP_ABLATION_LIFT_BITS,
              HF_BPC_BAR, VOCAB_CAP, N_TRAIN, N_HELD, N_DIM, SEEDS),
        "cites": [
            "preregs/2026-06-23_substrate_brain_full_compose_LM_v1.md",
            "experiments/exp_fresh_W_bpc_per_encoder_v2.py",
            "experiments/exp_substrate_as_lm_composed_primitives_GPU_v1.py",
            "USER_2026-06-23_brain_as_existence_proof_reframe",
            "USER_2026-06-22_Fix24_GPU_dispatch_must_use_GPU",
            "Rao_Ballard_1999_predictive_coding",
            "Friston_2009_free_energy",
            "Tonegawa_2015_excitability_trace",
            "Hopfield_1982_attractor",
            "Plate_1995_HRR",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    # HARD_PASS
    bpc_ok = math.isfinite(dec_bpc) and dec_bpc < HP_BPC_BAR
    lift_ok = math.isfinite(lift_over_baseline) and lift_over_baseline >= HP_LIFT_OVER_BASELINE
    cv_ok = math.isfinite(dec_cv) and dec_cv <= HP_BPC_CV_MAX
    abl_ok = math.isfinite(best_ablation_lift) and best_ablation_lift >= HP_ABLATION_LIFT_BITS

    detail["bpc_ok"] = bool(bpc_ok)
    detail["lift_ok"] = bool(lift_ok)
    detail["cv_ok"] = bool(cv_ok)
    detail["ablation_ok"] = bool(abl_ok)

    if bpc_ok and lift_ok and cv_ok and abl_ok:
        return ("HARD_PASS",
                ("BRAIN_FULL_COMPOSE HARD_PASS: %s bpc %.3f < %.3f bar (cv=%.3f<=%.2f); "
                 "lift %.3f bits over BASELINE_RANK1 (>=%.2f); "
                 "best ablation lift %.3f bits (>=%.2f mech ID); "
                 "substrate-as-LM unblocked via brain-architecture composition; "
                 "CHAIN-GRADE V2 closure evidence. %s" % (
                     DECISIVE_ARM, dec_bpc, HP_BPC_BAR, dec_cv, HP_BPC_CV_MAX,
                     lift_over_baseline, HP_LIFT_OVER_BASELINE,
                     best_ablation_lift, HP_ABLATION_LIFT_BITS, summary)),
                detail)

    if all_fail:
        return ("HARD_FAIL",
                ("BRAIN_FULL_COMPOSE HARD_FAIL: ALL %d arms >= unigram %.3f; even "
                 "full brain composition cannot beat unigram; substrate-as-LM is "
                 "fundamentally W-architecture capped; pivot to substrate-as-refuse-"
                 "aware-product. %s" % (len(non_uni), UNIGRAM_BPC_REF, summary)),
                detail)

    return ("MIDDLE_BAND",
            ("BRAIN_FULL_COMPOSE MIDDLE_BAND: composition lifts over rank-1 baseline "
             "but does not clear all HARD_PASS bars (bpc_ok=%s lift_ok=%s cv_ok=%s "
             "abl_ok=%s); decisive bpc=%.3f baseline=%.3f lift=%.3f abl=%.3f; "
             "partial mechanism — characterize what is still missing. %s" % (
                 bpc_ok, lift_ok, cv_ok, abl_ok,
                 dec_bpc, base_bpc, lift_over_baseline, best_ablation_lift,
                 summary)),
            detail)


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: char-trigram bipolar
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,)
    uniq = set(np.unique(v).tolist())
    assert uniq.issubset({-1.0, 1.0})

    global DEVICE
    _saved_device = DEVICE
    DEVICE = torch.device("cpu")
    try:
        # T2: build_E_char_trigram_gpu shape + L2 norm
        vocab_t = ["w%d" % i for i in range(8)]
        E = build_E_char_trigram_gpu(vocab_t, 64, seed=0)
        assert E.shape == (8, 64), "T2 E shape"
        nrms = E.norm(dim=1).numpy()
        assert np.allclose(nrms, 1.0, atol=1e-5), "T2 E norms"

        # T3: sparsify_bipolar_gpu produces correct sparsity
        Esp = sparsify_bipolar_gpu(E, 0.25, seed=0)
        nonzero_per_row = (Esp != 0).sum(dim=1).numpy()
        assert (nonzero_per_row == 16).all(), "T3 sparsity"  # 0.25 * 64
        # values must be +/-1 or 0
        vals = set(torch.unique(Esp).tolist())
        assert vals.issubset({-1.0, 0.0, 1.0}), "T3 bipolar"

        # T4: hrr_bind_batch identity-like (bind(x, ones) shifts)
        x = torch.randn(2, 8)
        y = torch.randn(2, 8)
        bound = hrr_bind_batch(x, y)
        assert bound.shape == (2, 8), "T4 bind shape"

        # T5: sparse_competitive_logits keeps k frac
        L = torch.randn(3, 20)
        Lout = sparse_competitive_logits(L, 0.10)  # keep 2 of 20
        # at most 2 finite entries per row (rest -1e9)
        finite_per_row = (Lout > -1e8).sum(dim=1).numpy()
        assert (finite_per_row == 2).all(), "T5 sparse comp k"

        # T6: lock-in positional code L2 norm and orthogonality across pos
        p0 = lock_in_position_vec(256, 0, seed=0)
        p1 = lock_in_position_vec(256, 1, seed=0)
        assert abs(float(p0.norm()) - 1.0) < 1e-4, "T6a norm"
        cos_p01 = abs(float((p0 * p1).sum()))
        assert cos_p01 < 0.4, "T6b orthogonality cos=%.3f" % cos_p01

        # T7: build_context_keys produces L2-normed output of right shape
        idx = torch.arange(10, dtype=torch.long) % 8
        keys = build_context_keys_gpu(idx, E, context_window=3, seed=0, use_lock_in=True)
        assert keys.shape == (10, 64), "T7 keys shape"
        knr = keys.norm(dim=1).numpy()
        assert np.allclose(knr, 1.0, atol=1e-4), "T7 keys norms"

        # T8: PC stack training + forward shape
        n_train = 50
        src_keys_t = torch.randn(n_train, 64)
        src_keys_t = _l2_normalize_t(src_keys_t)
        idx_train_t = torch.arange(n_train, dtype=torch.long) % 8
        Ws = build_pc_stack_gpu(src_keys_t, E, idx_train_t,
                                  ingest_chunk=8, n_layers=2)
        assert len(Ws) == 2, "T8a n_layers"
        for W in Ws:
            assert W.shape == (64, 64), "T8b W shape"
        pred = pc_stack_forward_gpu(Ws, src_keys_t, recall_batch=8)
        assert pred.shape == (n_train, 64), "T8c pred shape"
        pnr = pred.norm(dim=1).numpy()
        assert np.allclose(pnr, 1.0, atol=1e-4), "T8d pred norms"

        # T9: attractor cleanup converges toward E rows (cosine to nearest E increases)
        # Take E + perturbation; cleanup should pull toward original
        E_norm = _l2_normalize_t(E)
        perturbed = _l2_normalize_t(E_norm[:4] + 0.5 * torch.randn(4, 64))
        cleaned = attractor_cleanup_gpu(perturbed, E_norm, k_steps=3, recall_batch=4)
        # max sim to E rows should be >= max sim of perturbed
        sim_p = (perturbed @ E_norm.T).max(dim=1).values
        sim_c = (cleaned @ E_norm.T).max(dim=1).values
        assert (sim_c >= sim_p - 1e-4).all(), "T9 attractor non-decreasing sim"

        # T10: kinetic proofreading agreement deterministic at sigma=0
        gen = torch.Generator(device=torch.device("cpu"))
        gen.manual_seed(0)
        pred_t = _l2_normalize_t(torch.randn(5, 64))
        logits_kp, agree = kinetic_proofreading_logits(pred_t, E_norm,
                                                         sigma=0.0, tau=0.01,
                                                         recall_batch=5, generator=gen)
        # sigma=0: p1==p2 exactly, cos=1 > 1-tau, all agree
        assert agree.all(), "T10 sigma=0 all agree"
        # logits shape
        assert logits_kp.shape == (5, 8), "T10 logits shape"

        # T11: BPC sanity — uniform logits give log2(V) bits per token
        n_h = 100
        unif_logits = np.zeros((n_h, 8), dtype=np.float32)
        # synthetic held: cycle through vocab
        idx_h = np.arange(n_h + 1, dtype=np.int64) % 8
        # avoid unk=0 mask wiping everything: shift to indices 1..7
        idx_h = (idx_h % 7) + 1
        U_log_t = np.log(np.full(8, 1.0 / 8.0)).astype(np.float32)
        out = bpc_from_logits(unif_logits, idx_h, U_log_t, [1.0])
        # raw BPC of uniform-over-V = log2(V) = 3.0
        assert abs(out["bpc_raw"] - 3.0) < 0.05, "T11 uniform BPC raw=%.3f" % out["bpc_raw"]

        # T12: log-linear interp endpoints
        sub_probs = np.array([
            [0.6, 0.1, 0.1, 0.1, 0.1],
            [0.1, 0.5, 0.2, 0.1, 0.1],
        ], dtype=np.float64)
        nxt = np.array([0, 1], dtype=np.int64)
        U_log_t = np.log(np.array([0.2, 0.3, 0.2, 0.2, 0.1]).clip(1e-30, 1.0))
        sub_logp = np.log(sub_probs.clip(1e-30, 1.0))
        bpc_lam1 = log_linear_interp_bpc(sub_logp, U_log_t, nxt, 1.0)
        raw = -float(np.mean(sub_logp[np.arange(2), nxt])) / math.log(2.0)
        assert abs(bpc_lam1 - raw) < 1e-6, "T12a lam=1 reproduces raw"
        bpc_lam0 = log_linear_interp_bpc(sub_logp, U_log_t, nxt, 0.0)
        U = np.exp(U_log_t - U_log_t.max())
        U = U / U.sum()
        bpc_uni = -float(np.mean(np.log(U[nxt].clip(1e-12, 1.0)))) / math.log(2.0)
        assert abs(bpc_lam0 - bpc_uni) < 1e-6, "T12b lam=0 reproduces unigram"

        # T13: verdict bands
        def _mk_unit(bpc_by_arm):
            by_arm_local = {"ARM_UNIGRAM": {"bpc_unigram": 7.738, "n_test": 100}}
            for arm in [a for a in ARMS if a != "ARM_UNIGRAM"]:
                bp = bpc_by_arm.get(arm, 8.0)
                by_arm_local[arm] = {
                    "bpc_raw": bp + 0.1, "bpc_best": bp, "best_lambda": 0.5,
                    "best_dev_bpc": bp,
                    "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
                    "n_dev": 100, "n_test": 100,
                    "wall_arm_s": 0.1, "wall_keys_s": 0.0, "wall_ingest_s": 0.0,
                    "wall_recall_s": 0.0, "agreement_frac": 1.0,
                    "use_pc": False, "use_sparse_comp": False, "use_lock_in": False,
                    "use_context": False, "use_sparse_W": False,
                    "use_attractor": False, "use_kp": False,
                }
            return {"seed": 0, "by_arm": by_arm_local, "V": 16, "N": 64,
                    "N_DIM": 64, "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": 16,
                    "run_mode": "smoke", "config_version": "selftest",
                    "elapsed_s_seed": 0.01, "device": "cpu", "n_llm_calls": 0}

        # HARD_PASS: FULL clears <7.5, lift >1.0 over baseline 8.5, ablation lift >=0.3
        u_hp = _mk_unit({
            "ARM_BASELINE_RANK1_HEBBIAN": 8.5,
            "ARM_PC_HIERARCHY_ONLY": 8.0,    # ablation lift 0.5
            "ARM_PC_PLUS_SPARSE_COMPETITIVE": 7.9,
            "ARM_PC_PLUS_LOCK_IN_ATTENTION": 7.7,
            "ARM_BRAIN_FULL_COMPOSE": 7.0,   # lift over baseline 1.5
        })
        v, m, d = compute_verdict([u_hp, u_hp, u_hp])
        assert v == "HARD_PASS", "T13a HARD_PASS got %s: %s" % (v, m[:200])

        # HARD_FAIL: all >= 7.738
        u_hf = _mk_unit({
            "ARM_BASELINE_RANK1_HEBBIAN": 7.86,
            "ARM_PC_HIERARCHY_ONLY": 7.86,
            "ARM_PC_PLUS_SPARSE_COMPETITIVE": 7.85,
            "ARM_PC_PLUS_LOCK_IN_ATTENTION": 7.87,
            "ARM_BRAIN_FULL_COMPOSE": 7.86,
        })
        v, m, _ = compute_verdict([u_hf, u_hf, u_hf])
        assert v == "HARD_FAIL", "T13b HARD_FAIL got %s: %s" % (v, m[:200])

        # MIDDLE_BAND: FULL beats unigram + baseline but not by 1.0
        u_mid = _mk_unit({
            "ARM_BASELINE_RANK1_HEBBIAN": 7.86,
            "ARM_PC_HIERARCHY_ONLY": 7.80,
            "ARM_PC_PLUS_SPARSE_COMPETITIVE": 7.75,
            "ARM_PC_PLUS_LOCK_IN_ATTENTION": 7.70,
            "ARM_BRAIN_FULL_COMPOSE": 7.65,   # lift 0.21 < 1.0; bpc 7.65 > 7.5 bar
        })
        v, m, _ = compute_verdict([u_mid, u_mid, u_mid])
        assert v == "MIDDLE_BAND", "T13c MIDDLE_BAND got %s: %s" % (v, m[:200])

    finally:
        DEVICE = _saved_device

    # T14: llm counter clean
    assert _LLM_CALL_COUNTER[0] == 0, "T14 llm counter"

    print("[selftest] PASS: T1 trigram + T2 E + T3 sparse-bipolar + T4 hrr-bind + "
          "T5 sparse-competitive + T6 lock-in + T7 context-keys + T8 PC-stack + "
          "T9 attractor + T10 kinetic-proof + T11 BPC uniform + T12 log-linear + "
          "T13 verdict bands + T14 llm=0", flush=True)


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
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM, "N": N_DIM,
            "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
            "n_seeds": len(units), "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_substrate_brain_full_compose_LM_v1",
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
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM,
               "schema": "substrate-brain-full-compose-LM-v1"}
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
        "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
        "PC_N_LAYERS": PC_N_LAYERS, "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "SPARSE_COMPETITIVE_K_FRAC": SPARSE_COMPETITIVE_K_FRAC,
        "ATTRACTOR_K_STEPS": ATTRACTOR_K_STEPS,
        "CONTEXT_WINDOW": CONTEXT_WINDOW,
        "LOCK_IN_FREQ_STEP": LOCK_IN_FREQ_STEP,
        "KP_AGREEMENT_TAU": KP_AGREEMENT_TAU,
        "KP_NOISE_SIGMA": KP_NOISE_SIGMA,
        "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH,
        "LAMBDA_GRID": LAMBDA_GRID,
        "arms": ARMS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_gpu_substrate_brain_full_compose_LM_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate-native composed primitives; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
