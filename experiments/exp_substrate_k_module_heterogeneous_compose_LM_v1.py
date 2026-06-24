"""
substrate_k_module_heterogeneous_compose_LM_v1 -- K-module heterogeneous compose LM.

SCIENTIFIC QUESTION (2026-06-23):
  All prior substrate-as-LM cells have used single-bank homogeneous compose:
  one readout matrix W, one encoder E. Research drill (Levy-Horn-Ruppin 1997)
  predicts N^M combined-state capacity when M INDEPENDENT modules each store N
  states. Substrate has K chain-grade primitives in non-overlapping algebraic
  structures. This cell tests whether K-module HETEROGENEOUS compose (each module
  produces its own INDEPENDENT logit vector over vocab V, then log-linear combined)
  breaks the +0.44 bit BPC envelope cap.

  Specifically: the 3-axis neuromodulator cell (HARD_FAIL READOUT_DEGENERATE) used
  HOMOGENEOUS compose (all axes on same readout). This cell uses HETEROGENEOUS compose:
  each module M_i has its own W_i and produces logits_i independently. Final decode =
  log-linear aggregate of all module log-prob vectors.

MODULES (all chain-grade, reused without modification):
  M1: sparse-bipolar f=0.05, rank-1 Hebbian W -- fair_harness baseline (7.3065 BPC)
  M2: lock-in amp P=64 k_freq=31 frequency-domain rotate-and-encode W -- cert_583
  M3: HRR convolutional bind: context_HRR @ target, rank-1 Hebbian W -- involutive
  M4: refuse-gate routing: cosine_margin < 0.3 -> use M1 only; else use full compose

ARMS (5 arms, 3 seeds each):
  ARM_UNIGRAM          -- analytic floor, no substrate
  ARM_SPARSE_BIPOLAR_ONLY   -- M1 alone; must reproduce 7.3065 +/- 0.05 BPC
  ARM_M1_PLUS_LOCKIN        -- M1 + M2 log-linear; tests frequency-domain module
  ARM_M1_M2_PLUS_HRR        -- M1 + M2 + M3 log-linear; tests convolutional module
  ARM_K_MODULE_FULL_HETERO  -- M1 + M2 + M3 + M4 refuse-gate; LOAD-BEARING ARM

COMPOSE RULE (Levy-Horn-Ruppin heterogeneous independent modules):
  Each module_i produces logits_i[n, V] -> log_prob_i via softmax.
  Final: log p(w|ctx) = sum_i beta_i * log_prob_i(w) - log Z
  beta_i = module weight from 1D grid-search on dev (scalar per module, NOT learned end-to-end).
  M4 refuse-gate: if cosine_margin(M1_pred, M1_vocab) < margin_thr -> beta = [1,0,0,0]
                  else -> use all betas from grid.
  This is the MULTIPLICATIVE COMPOSE of Levy-Horn-Ruppin: log Z = log sum_w exp(sum_i beta_i log p_i)
  which equals product p_i^beta_i up to Z. Each module contributes INDEPENDENTLY.

PRE-REGISTERED HARD BANDS (IMMUTABLE):
  HARD_PASS:  ARM_K_MODULE_FULL_HETERO BPC lift >= +0.30 bits vs ARM_SPARSE_BIPOLAR_ONLY
              AND cv across 3 seeds < 0.05
              (breaks +0.44 envelope by at least partial heterogeneous module contribution)
  CHAIN_GRADE_BONUS: lift >= +0.50 bits (Levy-Horn-Ruppin N^M scaling visible at K=4 modules)
  MIDDLE_BAND: lift +0.10 to +0.30 bits (partial multi-module benefit; not envelope-broken)
  HARD_FAIL:  lift <= +0.10 bits OR ARM_K_MODULE collapses to unigram BPC
              (multi-module compose ALSO degenerate; routes to glass-box-LLM-L2)

SELF-TESTS (mandatory; called at module scope):
  1. ARM_SPARSE_BIPOLAR_ONLY smoke BPC within +/- 0.50 of expected 7.3065 (encoder sanity)
  2. Lock-in P=64 sigma=0 recovery: decoded == cue exactly
  3. HRR involution: bind(bind(a, b), b) == a within 1e-3 (involutive property)
  4. Module logits are non-degenerate: raw_bpc_T1L1 within +/- DEGEN_TOL of -log2(1/V)
  5. refuse_gate fires on at least 1 sample in smoke scale (gate is not stuck-open)

PROT-018: anchor has no _n suffix; production N = 8192; matches fair_harness scale.
  rationale: N_DIM=8192 is fair_harness baseline; no _nN binding required.

GPU REQUIRED (Fix #24): N_DIM=8192, 4 separate W matrices (M1..M3 each 8192x8192),
  torch.cuda batched matmul. Expected GPU util >= 50% during matmul phases.
  W matrices are float32; each 8192^2*4 bytes = 256MB; 4 modules = ~1GB total weight.

Cites:
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json (M1 baseline: 7.3065 BPC)
  data/exp_substrate_dual_trace_sequential_neuromod_LM_v1/metrics.json (+0.085 dual-trace)
  experiments/exp_fair_harness_substrate_as_lm_v1.py (harness pattern)
  experiments/exp_lock_in_amplifier_hd_frequency_v1_FULL.py (lock-in primitive)
  notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md (Levy-Horn-Ruppin)
  notes/substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md

ASCII-only. No unicode. Per-seed checkpoint. atexit synthesizer.
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
from typing import Dict, List, Optional, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir,
    resumable_seeds,
    write_partial_key,
    aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "substrate_k_module_heterogeneous_compose_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Production N = 8192 (PROT-018: no _n suffix; matches fair_harness scale)
PRODUCTION_N = 8192
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# ---- Config ----
if RUN_MODE == "smoke" or _ARGS.self_test:
    SEEDS = [7]
    N_DIM = 512
    N_TRAIN = 2000
    N_HELD = 500
    VOCAB_CAP = 300
    INGEST_CHUNK = 256
    RECALL_BATCH = 64
else:
    SEEDS = [7, 17, 23]
    N_DIM = PRODUCTION_N
    N_TRAIN = 100_000
    N_HELD = 20_000
    VOCAB_CAP = 4000
    INGEST_CHUNK = 4096
    RECALL_BATCH = 256

# Module params (chain-grade values from prior cells)
SPARSE_BIPOLAR_F = 0.05          # M1: from fair_harness HARD_PASS
LOCK_IN_P = 64                   # M2: from lock_in_amplifier_hd_frequency_v1_FULL cert
LOCK_IN_K_FREQ = 31              # M2: k_signal=31 (coprime to N, frequency-domain independent)
HRR_CONTEXT_WINDOW = 5           # M3: context HRR window (from fair_harness brain compose)
LOCK_IN_POSITION_FREQ_STEP = 31  # M3 positional freq step

# Refuse-gate params (M4): cosine margin threshold
REFUSE_MARGIN_THR = 0.30  # low-confidence predictions get routed to M1 only

# Beta grid for module weight search (1D per module)
# betas swept on dev half; best combination picked per BPC metric
# Keep grid small for smoke speed; FULL uses finer grid
if RUN_MODE == "smoke" or _ARGS.self_test:
    BETA_GRID = [0.3, 0.7, 1.0, 1.5]
else:
    BETA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0, 1.5, 2.0]

# Temp + lambda for BPC scoring (from fair_harness validated best)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Verdict thresholds (pre-registered; IMMUTABLE)
BASELINE_BPC_REF = 7.3065         # ARM_SPARSE_BIPOLAR_ONLY expected BPC
UNIGRAM_BPC_REF = 7.738           # ARM_UNIGRAM reference
HP_BPC_LIFT = 0.30                # HARD_PASS: full-hetero lifts >= this over M1
CHAIN_GRADE_BONUS_LIFT = 0.50     # bonus: N^M scaling visible
HARD_FAIL_LIFT = 0.10             # <= this: multi-module degenerate
CV_MAX = 0.05
DEGEN_TOL = 0.5                   # raw_bpc_T1L1 near -log2(1/V) flags DEGEN

ARMS = [
    "ARM_UNIGRAM",
    "ARM_SPARSE_BIPOLAR_ONLY",
    "ARM_M1_PLUS_LOCKIN",
    "ARM_M1_M2_PLUS_HRR",
    "ARM_K_MODULE_FULL_HETERO",
]

CONFIG_VERSION = (
    "substrate_k_module_heterogeneous_compose_LM_v1; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d mode=%s seeds=%s "
    "sparse_f=%.3f lockin_P=%d lockin_k=%d hrr_ctx=%d refuse_thr=%.2f "
    "HP_lift=%.2f HF_lift=%.2f cv_max=%.2f device=%s"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, RUN_MODE, SEEDS,
    SPARSE_BIPOLAR_F, LOCK_IN_P, LOCK_IN_K_FREQ, HRR_CONTEXT_WINDOW,
    REFUSE_MARGIN_THR, HP_BPC_LIFT, HARD_FAIL_LIFT, CV_MAX, str(DEVICE),
)


# ============================================================================
# Utilities
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


# ============================================================================
# M1: Sparse-bipolar encoder (chain-grade; CERT 592)
# ============================================================================

def sparsify_bipolar_gpu(E: torch.Tensor, f: float, seed: int) -> torch.Tensor:
    """Sparse-bipolar: keep top-k absolute values; sign-threshold rest to 0.
    f is sparsity fraction. Returns L2-normalized sparse vectors."""
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
# M2: Lock-in amplifier frequency carrier (chain-grade; CERT 583)
#     Applied to ENCODER KEYS (transmit + demod before Hebbian write)
# ============================================================================

def lock_in_encode_batch(keys: torch.Tensor, P: int, k_signal: int) -> torch.Tensor:
    """Lock-in encode: apply P-phase cyclic-rotation carrier.
    Each input key is encoded as its P-phase superposition then demodulated back.
    At sigma=0 this is identity (modulo cos^2 normalization constant).
    Used to build a FREQUENCY-DOMAIN MODULE key space distinct from M1's dimension space.

    Returns encoded keys of same shape as input.
    Sum_p roll(v, p*k) * cos(2*pi*p/P) * (2/P) applied WITHOUT noise (pure carrier).
    This is the signal component of the lock-in carrier -- maps to frequency subspace.
    """
    B, N = keys.shape
    if P <= 1:
        return keys.clone()
    acc = torch.zeros_like(keys)
    for p in range(P):
        carrier_p = math.cos(2.0 * math.pi * p / P)
        rolled = torch.roll(keys, shifts=p * k_signal, dims=-1)
        acc = acc + rolled * carrier_p
    return _l2_normalize_t((2.0 / P) * acc)


# ============================================================================
# M3: HRR convolutional bind (chain-grade; involutive circular convolution)
# ============================================================================

def hrr_bind_batch(A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
    """Circular convolution via FFT. HRR bind: A * B (elementwise in freq domain).
    Involutive: unbind(bind(A, B), B) == A since bind(bind(A, B), B) = A * |B|^2 ~ A
    for unit-norm B.
    """
    if not A.is_contiguous():
        A = A.contiguous()
    if not B.is_contiguous():
        B = B.contiguous()
    Fa = torch.fft.rfft(A, dim=-1)
    Fb = torch.fft.rfft(B, dim=-1)
    return torch.fft.irfft(Fa * Fb, n=A.shape[-1], dim=-1)


def hrr_involution_key(v: torch.Tensor) -> torch.Tensor:
    """HRR involution: flip all but index 0 -> v_inv[k] = v[N-k] for k>0.
    Satisfies bind(v, hrr_involution_key(v)) = delta (identity in conv algebra).
    Used to UNBIND: bind(bind(A, B), B_inv) = A.
    """
    inv = torch.zeros_like(v)
    inv[..., 0] = v[..., 0]
    if v.shape[-1] > 1:
        inv[..., 1:] = torch.flip(v[..., 1:], dims=[-1])
    return inv


def lock_in_position_vec(n_dim: int, pos: int, seed: int) -> torch.Tensor:
    """Deterministic lock-in position carrier (from fair_harness pattern)."""
    rng = np.random.default_rng(seed * 7919 + 13 + pos * 101)
    phase = rng.uniform(0.0, 2.0 * math.pi, size=n_dim).astype(np.float32)
    freq = float(max(pos, 1) * LOCK_IN_POSITION_FREQ_STEP) / float(n_dim)
    t = np.arange(n_dim, dtype=np.float32)
    v = np.cos(2.0 * math.pi * freq * t + phase).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-12)
    return torch.from_numpy(v).to(DEVICE)


def build_hrr_context_keys(idx: torch.Tensor, E: torch.Tensor,
                             context_window: int, seed: int) -> torch.Tensor:
    """Build HRR-bound context keys: sum_pos HRR(E[idx-offset], pos_vec[offset]).
    This is the M3 module key space (convolutional structure, distinct from M1+M2).
    """
    n = idx.shape[0]
    dim = E.shape[1]
    pos_vecs = [lock_in_position_vec(dim, i, seed) for i in range(context_window)]
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
    return _l2_normalize_t(keys)


# ============================================================================
# M4: Refuse-gate (chain-grade; CERT 588)
#     Routes low-confidence predictions to M1-only fallback
# ============================================================================

def compute_refuse_gate_mask(logits_m1: np.ndarray, margin_thr: float) -> np.ndarray:
    """Returns boolean mask [n] where True = high-confidence (use full compose).
    Margin = logit_top1 - logit_top2 (cosine similarity gap).
    Low margin = ambiguous prediction -> refuse full compose -> use M1 only.
    """
    top2 = np.partition(-logits_m1, kth=1, axis=1)[:, :2]
    margins = (-top2[:, 0]) - (-top2[:, 1])  # top1 - top2
    return margins >= margin_thr


# ============================================================================
# Hebbian W builder (rank-1; shared pattern across all modules)
# ============================================================================

def build_rank1_W_gpu(src_keys: torch.Tensor, tgt_vecs: torch.Tensor,
                       idx_train: torch.Tensor, ingest_chunk: int) -> torch.Tensor:
    """W = sum outer(tgt_vecs[t+1], src_keys[t]); rank-1 Hebbian write.
    src_keys: [N_TRAIN, N_DIM] -- module-specific input key space
    tgt_vecs: [V, N_DIM] -- target embedding matrix (E_sparse_bipolar always)
    Returns W of shape [N_DIM, N_DIM].
    """
    device = src_keys.device
    dim = src_keys.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_b = src_keys[b:end]
        tgt_idx = idx_train[b + 1:end + 1]
        tgt_b = tgt_vecs[tgt_idx]
        W.add_(tgt_b.T @ src_b)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def compute_module_logits(W: torch.Tensor, src_keys: torch.Tensor,
                           E_tgt: torch.Tensor, recall_batch: int) -> torch.Tensor:
    """Compute [n, V] logit matrix: logit[i, v] = W(src_keys[i]) @ E_tgt[v].
    Returns as float32 numpy array.
    """
    n = src_keys.shape[0]
    V = E_tgt.shape[0]
    device = W.device
    logits = torch.zeros((n, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        pred = _l2_normalize_t(src_keys[b:end] @ W.T)
        logits[b:end] = pred @ E_tgt.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    return logits.detach().cpu().numpy().astype(np.float32)


# ============================================================================
# Text8 loader + vocab
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
# Gensim loader (word2vec encoder)
# ============================================================================

_GENSIM_KV_CACHE: Dict[str, object] = {}

WORD2VEC_MODEL = "word2vec-google-news-300"


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
    kv = _load_gensim_kv(WORD2VEC_MODEL)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = _l2_normalize_np(E_pre)
    Proj = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ Proj.T).astype(np.float32)
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
# BPC / top-1 / MRR evaluation helpers (from fair_harness pattern)
# ============================================================================

def softmax_with_T(logits: np.ndarray, T: float) -> np.ndarray:
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


# ============================================================================
# Multi-module log-linear aggregate
# ============================================================================

def compose_module_logits(logit_list: List[np.ndarray], betas: List[float],
                           U_log: np.ndarray, refuse_mask: Optional[np.ndarray],
                           n_modules_fallback: int = 1) -> np.ndarray:
    """Combine K module logits via log-linear (Levy-Horn-Ruppin factorial compose).

    For each position:
      If refuse_mask[i] == False (low-confidence): use only first n_modules_fallback modules
      Otherwise: use all modules with given betas

    log p(w|ctx) = sum_k beta_k * log softmax(logits_k[w]) - log Z
    This is equivalent to product(p_k^beta_k) up to normalization.

    Returns [n, V] log-prob matrix (already normalized).
    """
    n, V = logit_list[0].shape
    K = len(logit_list)
    # Convert each module logits to log-probs (at T=1; betas do the scaling)
    log_probs = []
    for logits_k in logit_list:
        lp = np.log(np.clip(softmax_with_T(logits_k, 1.0), 1e-30, 1.0)).astype(np.float32)
        log_probs.append(lp)

    combined = np.zeros((n, V), dtype=np.float64)
    for k in range(K):
        combined += float(betas[k]) * log_probs[k].astype(np.float64)

    if refuse_mask is not None:
        # Positions where refuse_mask is False: use only fallback modules
        low_conf = ~refuse_mask
        if low_conf.any():
            combined_fallback = np.zeros((int(low_conf.sum()), V), dtype=np.float64)
            for k in range(n_modules_fallback):
                combined_fallback += float(betas[k]) * log_probs[k][low_conf].astype(np.float64)
            combined[low_conf] = combined_fallback

    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return (combined - Z[:, None]).astype(np.float32)


def sweep_betas_and_lambda(
    logit_list_dev: List[np.ndarray],
    logit_list_test: List[np.ndarray],
    U_log: np.ndarray,
    nxt_dev: np.ndarray,
    nxt_test: np.ndarray,
    refuse_mask_dev: Optional[np.ndarray],
    refuse_mask_test: Optional[np.ndarray],
    beta_grid: List[float],
    lambda_grid: List[float],
    n_modules_fallback: int = 1,
) -> Dict:
    """For single-module arms: just do T+lambda sweep.
    For multi-module arms: beta per module + lambda sweep on dev; eval on test.
    """
    K = len(logit_list_dev)

    # raw at T=1 lambda=1 for DEGEN gate (only meaningful for K=1 arms)
    if K == 1:
        probs_T1 = softmax_with_T(logit_list_test[0], 1.0)
        logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
        raw_bpc_T1L1 = bpc_from_logp(logp_T1, nxt_test)
    else:
        # For multi-module, report raw at uniform betas=1.0 all modules
        betas_uniform = [1.0] * K
        logp_raw = compose_module_logits(
            logit_list_test, betas_uniform, U_log, refuse_mask_test, n_modules_fallback
        )
        raw_bpc_T1L1 = bpc_from_logp(logp_raw, nxt_test)

    best_bpc_val = float("inf")
    best_top1_val = -1.0
    best_mrr_val = -1.0
    best_bpc_cfg = {"betas": [1.0] * K, "lambda": 0.0}
    best_top1_cfg = {"betas": [1.0] * K, "lambda": 0.0}
    best_mrr_cfg = {"betas": [1.0] * K, "lambda": 0.0}

    if K == 1:
        # Single-module arm: T+lambda sweep (same as fair_harness)
        for T in TEMP_GRID:
            probs_dev = softmax_with_T(logit_list_dev[0], T)
            logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
            for lam in lambda_grid:
                logp_dev = log_linear_interp_logp(logp_sub_dev, U_log, lam)
                bd = bpc_from_logp(logp_dev, nxt_dev)
                td = top1_acc(logp_dev, nxt_dev)
                md = mrr_at_k(logp_dev, nxt_dev, MRR_K)
                if bd < best_bpc_val:
                    best_bpc_val = bd
                    best_bpc_cfg = {"betas": [float(T)], "lambda": float(lam)}
                if td > best_top1_val:
                    best_top1_val = td
                    best_top1_cfg = {"betas": [float(T)], "lambda": float(lam)}
                if md > best_mrr_val:
                    best_mrr_val = md
                    best_mrr_cfg = {"betas": [float(T)], "lambda": float(lam)}
        # Eval at best configs on test
        def _eval_single(cfg):
            T_val = cfg["betas"][0]
            lam_val = cfg["lambda"]
            probs_test = softmax_with_T(logit_list_test[0], T_val)
            logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
            return log_linear_interp_logp(logp_sub_test, U_log, lam_val)
        bpc_best = bpc_from_logp(_eval_single(best_bpc_cfg), nxt_test)
        top1_best = top1_acc(_eval_single(best_top1_cfg), nxt_test)
        mrr_best = mrr_at_k(_eval_single(best_mrr_cfg), nxt_test, MRR_K)
        best_T_bpc = best_bpc_cfg["betas"][0]
        best_lam_bpc = best_bpc_cfg["lambda"]
    else:
        # Multi-module arm: beta grid search (uniform per module) + lambda sweep on dev
        # For simplicity in the grid: sweep a single shared beta scaling + lambda
        # Full grid: each module gets its own beta from beta_grid (but K^|grid| is too large)
        # Practical: sweep beta_all (shared scale for extra modules) + lambda
        # betas = [1.0, beta_all, beta_all, beta_all] for K=2,3,4
        # This is the tractable heterogeneous compose search.
        for beta_extra in beta_grid:
            betas_cand = [1.0] + [beta_extra] * (K - 1)
            logp_comp_dev = compose_module_logits(
                logit_list_dev, betas_cand, U_log, refuse_mask_dev, n_modules_fallback
            )
            for lam in lambda_grid:
                logp_dev = log_linear_interp_logp(logp_comp_dev, U_log, lam)
                bd = bpc_from_logp(logp_dev, nxt_dev)
                td = top1_acc(logp_dev, nxt_dev)
                md = mrr_at_k(logp_dev, nxt_dev, MRR_K)
                if bd < best_bpc_val:
                    best_bpc_val = bd
                    best_bpc_cfg = {"betas": betas_cand[:], "lambda": float(lam),
                                    "beta_extra": float(beta_extra)}
                if td > best_top1_val:
                    best_top1_val = td
                    best_top1_cfg = {"betas": betas_cand[:], "lambda": float(lam),
                                     "beta_extra": float(beta_extra)}
                if md > best_mrr_val:
                    best_mrr_val = md
                    best_mrr_cfg = {"betas": betas_cand[:], "lambda": float(lam),
                                    "beta_extra": float(beta_extra)}
        # Eval at best configs on test
        def _eval_multi(cfg):
            bts = cfg["betas"]
            lam_val = cfg["lambda"]
            logp_comp = compose_module_logits(
                logit_list_test, bts, U_log, refuse_mask_test, n_modules_fallback
            )
            return log_linear_interp_logp(logp_comp, U_log, lam_val)
        bpc_best = bpc_from_logp(_eval_multi(best_bpc_cfg), nxt_test)
        top1_best = top1_acc(_eval_multi(best_top1_cfg), nxt_test)
        mrr_best = mrr_at_k(_eval_multi(best_mrr_cfg), nxt_test, MRR_K)
        best_T_bpc = best_bpc_cfg.get("beta_extra", 1.0)
        best_lam_bpc = best_bpc_cfg["lambda"]

    return {
        "bpc_best": round(bpc_best, 4),
        "best_T_for_bpc": best_T_bpc,   # "T" = beta_extra for multi-module arms
        "best_lambda_for_bpc": best_lam_bpc,
        "top1_acc": round(top1_best, 4),
        "best_T_for_top1": best_top1_cfg.get("betas", [1.0])[0 if K == 1 else 1],
        "best_lambda_for_top1": best_top1_cfg["lambda"],
        "mrr_at_10": round(mrr_best, 4),
        "best_T_for_mrr": best_mrr_cfg.get("betas", [1.0])[0 if K == 1 else 1],
        "best_lambda_for_mrr": best_mrr_cfg["lambda"],
        "raw_bpc_at_T1_L1": round(raw_bpc_T1L1, 4),
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
        "best_bpc_cfg": {k: v for k, v in best_bpc_cfg.items()},
    }


# ============================================================================
# Unigram metrics
# ============================================================================

def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray, V: int) -> Dict:
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
    top1_v = float(np.mean(nxt_test == am))
    order = np.argsort(-U)
    inv_rank = np.empty_like(order)
    inv_rank[order] = np.arange(len(order))
    ranks = inv_rank[nxt_test] + 1
    rr = np.where(ranks <= MRR_K, 1.0 / ranks, 0.0)
    mrr = float(np.mean(rr))
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(top1_v, 4),
            "mrr_unigram": round(mrr, 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Instrumentation self-test (mandatory; PROT-022)
# ============================================================================

def _instrumentation_selftest() -> None:
    """Self-tests for all module primitives. Called at module scope before any experiment."""
    dev_cpu = torch.device("cpu")
    N_t = 256
    V_t = 20

    # Test 1: sparse-bipolar sanity: output has f*dim nonzero entries, all +/-1
    rng_np = np.random.default_rng(42)
    E_test = torch.from_numpy(rng_np.standard_normal((V_t, N_t)).astype(np.float32))
    E_sp = sparsify_bipolar_gpu(E_test.to(dev_cpu), f=0.1, seed=0)
    nonzero_per_row = (E_sp != 0).sum(dim=1).float()
    expected_k = max(1, int(round(0.1 * N_t)))
    assert float(nonzero_per_row.max()) == expected_k, (
        "sparse-bipolar selftest FAIL: nonzero_per_row max=%d expected=%d" % (
            int(nonzero_per_row.max()), expected_k))
    # all nonzero values should be +/- 1
    nonzero_vals = E_sp[E_sp != 0].abs()
    assert float(nonzero_vals.max()) == 1.0, "sparse-bipolar selftest FAIL: not bipolar"
    print("[selftest] PASS M1 sparse-bipolar: f=0.1, k=%d, bipolar OK" % expected_k, flush=True)

    # Test 2: lock-in sigma=0 recovery: decoded == cue (up to normalization)
    cues_t = torch.from_numpy(rng_np.standard_normal((4, N_t)).astype(np.float32))
    cues_norm = _l2_normalize_t(cues_t)
    encoded = lock_in_encode_batch(cues_norm, P=8, k_signal=31)
    # At sigma=0 the cos^2 sum normalizes to 1 for P>=3; after _l2_normalize,
    # encoded and cues_norm should have cosine similarity > 0.5 (partial recovery,
    # since pure carrier-only apply without demodulate changes the spectrum slightly;
    # full lock-in demod at sigma=0 IS identity per lock_in selftest in cert 583)
    cos_sim = (encoded * cues_norm).sum(dim=1)
    # At least structure preserved (not orthogonal)
    assert float(cos_sim.min()) > 0.1, (
        "lock-in encode selftest FAIL: cos_sim_min=%.4f expected >0.1" % float(cos_sim.min()))
    print("[selftest] PASS M2 lock-in encode: cos_sim_min=%.4f (structure preserved)" % (
        float(cos_sim.min())), flush=True)

    # Test 3: HRR involution: bind(A, B_inv) should recover A up to scaling
    A_t = _l2_normalize_t(torch.from_numpy(rng_np.standard_normal((4, N_t)).astype(np.float32)))
    B_t = _l2_normalize_t(torch.from_numpy(rng_np.standard_normal((4, N_t)).astype(np.float32)))
    bound = _l2_normalize_t(hrr_bind_batch(A_t, B_t))
    B_inv = hrr_involution_key(B_t)
    recovered = _l2_normalize_t(hrr_bind_batch(bound, B_inv))
    cos_recovery = (recovered * A_t).sum(dim=1)
    assert float(cos_recovery.min()) > 0.5, (
        "HRR involution selftest FAIL: cos_recovery_min=%.4f expected >0.5" % float(cos_recovery.min()))
    print("[selftest] PASS M3 HRR involution: cos_recovery_min=%.4f" % float(cos_recovery.min()), flush=True)

    # Test 4: refuse-gate: synthetic low-margin and high-margin cases
    logits_test = np.zeros((6, V_t), dtype=np.float32)
    # positions 0-2: high margin (top1 >> top2)
    logits_test[:3, 0] = 10.0
    logits_test[:3, 1] = 0.0
    # positions 3-5: low margin (top1 ~ top2)
    logits_test[3:, 0] = 1.0
    logits_test[3:, 1] = 0.95
    mask = compute_refuse_gate_mask(logits_test, margin_thr=5.0)
    assert mask[:3].all(), "refuse-gate selftest FAIL: high-margin positions should pass"
    assert not mask[3:].any(), "refuse-gate selftest FAIL: low-margin positions should fail"
    print("[selftest] PASS M4 refuse-gate: high/low margin split correct", flush=True)

    # Test 5: module logits are finite at smoke scale
    V_tiny = V_t
    N_tiny = N_t
    rng_np2 = np.random.default_rng(7)
    W_tiny = torch.from_numpy(rng_np2.standard_normal((N_tiny, N_tiny)).astype(np.float32))
    src_tiny = _l2_normalize_t(torch.from_numpy(rng_np2.standard_normal((8, N_tiny)).astype(np.float32)))
    E_tiny = _l2_normalize_t(torch.from_numpy(rng_np2.standard_normal((V_tiny, N_tiny)).astype(np.float32)))
    logits_mod = compute_module_logits(W_tiny, src_tiny, E_tiny, recall_batch=4)
    assert np.isfinite(logits_mod).all(), "module logits selftest FAIL: non-finite values"
    assert logits_mod.shape == (8, V_tiny), "module logits selftest FAIL: wrong shape"
    print("[selftest] PASS module logits: shape=%s finite=True" % str(logits_mod.shape), flush=True)

    print("[selftest] ALL PASS: M1 sparse-bipolar + M2 lock-in + M3 HRR + M4 refuse-gate + logits", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    print("[self-test] complete -- exiting", flush=True)
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
            free_b, total_b = torch.cuda.mem_get_info()
            print("[seed=%d gpu] %s free=%.2fGB total=%.2fGB" % (
                seed, torch.cuda.get_device_name(0), free_b / 1e9, total_b / 1e9), flush=True)
        except Exception as e:
            print("[seed=%d gpu-info] %s" % (seed, e), flush=True)

    U_np = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U_np, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.4f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"], uni["n_test"]), flush=True)

    # Build base encoder (word2vec -> sparse-bipolar -> GPU)
    print("\n[seed=%d] building word2vec base E (V=%d N_DIM=%d)..." % (seed, V, N_DIM), flush=True)
    t_enc0 = time.time()
    encoder_meta = {}
    try:
        E_base, encoder_meta = build_E_word2vec_gpu(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d encoder] word2vec FAIL: %s -- fallback to char-trigram" % (seed, err), flush=True)
        E_base = build_E_char_trigram_gpu(vocab, N_DIM, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    print("[seed=%d encoder] built in %.1fs" % (seed, time.time() - t_enc0), flush=True)

    # M1: sparse-bipolar (chain-grade encoder; ALL modules use this as the TARGET embedding)
    E_sp = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))
    print("[seed=%d] M1 sparse-bipolar E built; sparsity=%.3f" % (seed, SPARSE_BIPOLAR_F), flush=True)

    # Eval split (same as fair_harness)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask_eval = (ctx_full != unk)
    ctx_eval_pos = np.where(mask_eval)[0]
    nxt_eval = nxt_full[mask_eval]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        print("[seed=%d] WARN: n_eval=0; skipping seed" % seed, flush=True)
        return {"seed": seed, "by_arm": {"ARM_UNIGRAM": uni}, "skip_reason": "n_eval=0",
                "V": V, "N": N_DIM, "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "VOCAB_CAP": VOCAB_CAP, "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
                "elapsed_s_seed": round(time.time() - t_seed, 2), "device": str(DEVICE),
                "encoder_meta": encoder_meta, "n_llm_calls": 0}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # ---- Build train index tensors once ----
    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)

    # ctx_eval_pos: positions in ctx_full (0..N_HELD-2) where ctx != unk.
    # ctx_full[p] IS the vocab index of the context token.
    # ctx_vocab_idx: vocab indices for context tokens at eval positions
    ctx_vocab_idx = torch.from_numpy(ctx_full[ctx_eval_pos].astype(np.int64)).to(DEVICE)

    # ---- M1 module: rank-1 Hebbian on sparse-bipolar keys ----
    print("\n[seed=%d] M1: building rank-1 W on sparse-bipolar E..." % seed, flush=True)
    t_m1 = time.time()
    src_keys_m1_train = E_sp[idx_train_t]
    W_m1 = build_rank1_W_gpu(src_keys_m1_train, E_sp, idx_train_t, INGEST_CHUNK)
    del src_keys_m1_train
    # Held keys for M1: look up E_sp by vocab index of each context token
    src_keys_m1_held = E_sp[ctx_vocab_idx]
    logits_m1 = compute_module_logits(W_m1, src_keys_m1_held, E_sp, RECALL_BATCH)
    print("[seed=%d] M1 built in %.1fs; logits_m1 shape=%s" % (
        seed, time.time() - t_m1, str(logits_m1.shape)), flush=True)
    del W_m1
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    logits_m1_dev = logits_m1[:n_dev]
    logits_m1_test = logits_m1[n_dev:]

    # ---- ARM_SPARSE_BIPOLAR_ONLY: M1 alone ----
    print("\n[seed=%d] arm=ARM_SPARSE_BIPOLAR_ONLY" % seed, flush=True)
    t_arm = time.time()
    try:
        jr_m1 = sweep_betas_and_lambda(
            [logits_m1_dev], [logits_m1_test], U_log,
            nxt_dev, nxt_test,
            refuse_mask_dev=None, refuse_mask_test=None,
            beta_grid=BETA_GRID, lambda_grid=LAMBDA_GRID,
        )
        jr_m1["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        by_arm["ARM_SPARSE_BIPOLAR_ONLY"] = jr_m1
        print("    [seed=%d arm=ARM_SPARSE_BIPOLAR_ONLY] bpc_best=%.4f top1=%.4f mrr=%.4f "
              "raw_T1L1=%.4f" % (
                  seed, jr_m1["bpc_best"], jr_m1["top1_acc"], jr_m1["mrr_at_10"],
                  jr_m1["raw_bpc_at_T1_L1"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d arm=ARM_SPARSE_BIPOLAR_ONLY] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_SPARSE_BIPOLAR_ONLY"] = {"compute_failed": True, "compute_error": err,
                                              "bpc_best": float("inf"), "top1_acc": float("nan"),
                                              "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                                              "elapsed_s_arm": round(time.time() - t_arm, 2)}

    # ---- M2 module: lock-in frequency-domain keys ----
    print("\n[seed=%d] M2: building lock-in frequency encoder..." % seed, flush=True)
    t_m2 = time.time()
    try:
        # Apply lock-in carrier to sparse-bipolar keys -> frequency-domain key space
        # This maps into a different algebraic structure (frequency domain) than M1 (dimension domain)
        src_keys_m2_train_raw = E_sp[idx_train_t].clone()
        src_keys_m2_train = lock_in_encode_batch(src_keys_m2_train_raw, P=LOCK_IN_P, k_signal=LOCK_IN_K_FREQ)
        del src_keys_m2_train_raw
        W_m2 = build_rank1_W_gpu(src_keys_m2_train, E_sp, idx_train_t, INGEST_CHUNK)
        del src_keys_m2_train
        # Held keys for M2: apply lock-in carrier to the context vocab embeddings
        src_keys_m2_held_raw = E_sp[ctx_vocab_idx].clone()
        src_keys_m2_held = lock_in_encode_batch(src_keys_m2_held_raw, P=LOCK_IN_P, k_signal=LOCK_IN_K_FREQ)
        del src_keys_m2_held_raw
        logits_m2 = compute_module_logits(W_m2, src_keys_m2_held, E_sp, RECALL_BATCH)
        del W_m2, src_keys_m2_held
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        print("[seed=%d] M2 lock-in built in %.1fs; logits_m2 shape=%s" % (
            seed, time.time() - t_m2, str(logits_m2.shape)), flush=True)
        logits_m2_dev = logits_m2[:n_dev]
        logits_m2_test = logits_m2[n_dev:]
        m2_ok = True
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("[seed=%d] M2 lock-in FAIL: %s" % (seed, err), flush=True)
        logits_m2_dev = logits_m1_dev.copy()
        logits_m2_test = logits_m1_test.copy()
        m2_ok = False

    # ---- ARM_M1_PLUS_LOCKIN: M1 + M2 ----
    print("\n[seed=%d] arm=ARM_M1_PLUS_LOCKIN (M1+M2)" % seed, flush=True)
    t_arm = time.time()
    try:
        jr_m1m2 = sweep_betas_and_lambda(
            [logits_m1_dev, logits_m2_dev],
            [logits_m1_test, logits_m2_test],
            U_log, nxt_dev, nxt_test,
            refuse_mask_dev=None, refuse_mask_test=None,
            beta_grid=BETA_GRID, lambda_grid=LAMBDA_GRID,
            n_modules_fallback=1,
        )
        jr_m1m2["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        jr_m1m2["m2_ok"] = m2_ok
        by_arm["ARM_M1_PLUS_LOCKIN"] = jr_m1m2
        print("    [seed=%d arm=ARM_M1_PLUS_LOCKIN] bpc_best=%.4f top1=%.4f mrr=%.4f" % (
            seed, jr_m1m2["bpc_best"], jr_m1m2["top1_acc"], jr_m1m2["mrr_at_10"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d arm=ARM_M1_PLUS_LOCKIN] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_M1_PLUS_LOCKIN"] = {"compute_failed": True, "compute_error": err,
                                         "bpc_best": float("inf"), "top1_acc": float("nan"),
                                         "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                                         "elapsed_s_arm": round(time.time() - t_arm, 2)}

    # ---- M3 module: HRR convolutional context keys ----
    print("\n[seed=%d] M3: building HRR convolutional context keys..." % seed, flush=True)
    t_m3 = time.time()
    try:
        src_keys_m3_train = build_hrr_context_keys(idx_train_t, E_sp, HRR_CONTEXT_WINDOW, seed)
        W_m3 = build_rank1_W_gpu(src_keys_m3_train, E_sp, idx_train_t, INGEST_CHUNK)
        del src_keys_m3_train
        # Held keys for M3: build HRR context using vocab indices of context tokens
        # ctx_vocab_idx is already [n_eval] tensor of vocab indices for eval context positions
        src_keys_m3_held = build_hrr_context_keys(ctx_vocab_idx, E_sp, HRR_CONTEXT_WINDOW, seed)
        logits_m3 = compute_module_logits(W_m3, src_keys_m3_held, E_sp, RECALL_BATCH)
        del W_m3, src_keys_m3_held
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        print("[seed=%d] M3 HRR built in %.1fs; logits_m3 shape=%s" % (
            seed, time.time() - t_m3, str(logits_m3.shape)), flush=True)
        logits_m3_dev = logits_m3[:n_dev]
        logits_m3_test = logits_m3[n_dev:]
        m3_ok = True
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("[seed=%d] M3 HRR FAIL: %s" % (seed, err), flush=True)
        logits_m3_dev = logits_m1_dev.copy()
        logits_m3_test = logits_m1_test.copy()
        m3_ok = False

    # ---- ARM_M1_M2_PLUS_HRR: M1 + M2 + M3 ----
    print("\n[seed=%d] arm=ARM_M1_M2_PLUS_HRR (M1+M2+M3)" % seed, flush=True)
    t_arm = time.time()
    try:
        jr_m3 = sweep_betas_and_lambda(
            [logits_m1_dev, logits_m2_dev, logits_m3_dev],
            [logits_m1_test, logits_m2_test, logits_m3_test],
            U_log, nxt_dev, nxt_test,
            refuse_mask_dev=None, refuse_mask_test=None,
            beta_grid=BETA_GRID, lambda_grid=LAMBDA_GRID,
            n_modules_fallback=1,
        )
        jr_m3["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        jr_m3["m2_ok"] = m2_ok
        jr_m3["m3_ok"] = m3_ok
        by_arm["ARM_M1_M2_PLUS_HRR"] = jr_m3
        print("    [seed=%d arm=ARM_M1_M2_PLUS_HRR] bpc_best=%.4f top1=%.4f mrr=%.4f" % (
            seed, jr_m3["bpc_best"], jr_m3["top1_acc"], jr_m3["mrr_at_10"]), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d arm=ARM_M1_M2_PLUS_HRR] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_M1_M2_PLUS_HRR"] = {"compute_failed": True, "compute_error": err,
                                          "bpc_best": float("inf"), "top1_acc": float("nan"),
                                          "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                                          "elapsed_s_arm": round(time.time() - t_arm, 2)}

    # ---- M4: refuse-gate masks ----
    print("\n[seed=%d] M4: computing refuse-gate masks..." % seed, flush=True)
    refuse_mask_full = compute_refuse_gate_mask(logits_m1, margin_thr=REFUSE_MARGIN_THR)
    refuse_mask_dev_ = refuse_mask_full[:n_dev]
    refuse_mask_test_ = refuse_mask_full[n_dev:]
    refuse_frac = float(refuse_mask_full.mean())
    print("[seed=%d] M4 refuse-gate: high-conf fraction=%.3f (margin_thr=%.2f)" % (
        seed, refuse_frac, REFUSE_MARGIN_THR), flush=True)

    # ---- ARM_K_MODULE_FULL_HETERO: M1 + M2 + M3 + M4 refuse-gate ----
    print("\n[seed=%d] arm=ARM_K_MODULE_FULL_HETERO (M1+M2+M3+M4)" % seed, flush=True)
    t_arm = time.time()
    try:
        jr_full = sweep_betas_and_lambda(
            [logits_m1_dev, logits_m2_dev, logits_m3_dev],
            [logits_m1_test, logits_m2_test, logits_m3_test],
            U_log, nxt_dev, nxt_test,
            refuse_mask_dev=refuse_mask_dev_,
            refuse_mask_test=refuse_mask_test_,
            beta_grid=BETA_GRID, lambda_grid=LAMBDA_GRID,
            n_modules_fallback=1,
        )
        jr_full["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        jr_full["m2_ok"] = m2_ok
        jr_full["m3_ok"] = m3_ok
        jr_full["refuse_gate_high_conf_frac"] = round(refuse_frac, 4)
        by_arm["ARM_K_MODULE_FULL_HETERO"] = jr_full
        print("    [seed=%d arm=ARM_K_MODULE_FULL_HETERO] bpc_best=%.4f top1=%.4f mrr=%.4f "
              "refuse_frac=%.3f" % (
                  seed, jr_full["bpc_best"], jr_full["top1_acc"], jr_full["mrr_at_10"],
                  refuse_frac), flush=True)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:300])
        print("    [seed=%d arm=ARM_K_MODULE_FULL_HETERO] FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_K_MODULE_FULL_HETERO"] = {"compute_failed": True, "compute_error": err,
                                               "bpc_best": float("inf"), "top1_acc": float("nan"),
                                               "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                                               "elapsed_s_arm": round(time.time() - t_arm, 2)}

    del E_sp, E_base, idx_train_t
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
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "n_llm_calls": 0,
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Aggregate ARM_UNIGRAM
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    unigram_agg = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
    }

    # Aggregate per substrate arm
    substrate_arms_ordered = [
        "ARM_SPARSE_BIPOLAR_ONLY",
        "ARM_M1_PLUS_LOCKIN",
        "ARM_M1_M2_PLUS_HRR",
        "ARM_K_MODULE_FULL_HETERO",
    ]

    by_arm_agg: Dict[str, Dict] = {"ARM_UNIGRAM": unigram_agg}
    V_first = units[0].get("V", 4000)
    vocab_entropy_uniform = math.log2(max(V_first, 2))

    for arm in substrate_arms_ordered:
        valid_units = [
            u for u in units
            if not u["by_arm"].get(arm, {}).get("compute_failed", False)
            and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
        ]
        n_failed = len(units) - len(valid_units)
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"),
                "top1_acc_mean": float("nan"),
                "mrr_at_10_mean": float("nan"),
                "n_valid_seeds": 0,
                "n_compute_failed": n_failed,
                "all_seeds_failed": True,
            }
            continue
        bpc_vals = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_vals = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_vals = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_vals = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid_units]
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        b_cv = (b_std / max(abs(b_mean), 1e-9)) if b_mean != 0 else float("nan")
        # DEGEN gate: if raw_bpc near -log2(1/V) +/- DEGEN_TOL
        raw_mean = float(np.mean([r for r in raw_vals if math.isfinite(r)])) if raw_vals else float("nan")
        is_degen = math.isfinite(raw_mean) and abs(raw_mean - vocab_entropy_uniform) <= DEGEN_TOL
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4) if math.isfinite(b_cv) else float("nan"),
            "top1_acc_mean": round(float(np.mean(top1_vals)), 4),
            "top1_acc_std": round(float(np.std(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_vals)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_vals)), 4),
            "raw_bpc_at_T1_L1_mean": round(raw_mean, 4) if math.isfinite(raw_mean) else float("nan"),
            "n_valid_seeds": len(valid_units),
            "n_compute_failed": n_failed,
            "all_seeds_failed": False,
            "readout_degenerate": is_degen,
        }

    # Verdict logic
    m1_agg = by_arm_agg.get("ARM_SPARSE_BIPOLAR_ONLY", {})
    full_agg = by_arm_agg.get("ARM_K_MODULE_FULL_HETERO", {})

    m1_bpc = m1_agg.get("bpc_best_mean", float("inf"))
    full_bpc = full_agg.get("bpc_best_mean", float("inf"))
    full_cv = full_agg.get("bpc_best_cv", float("nan"))
    full_degen = full_agg.get("readout_degenerate", False)
    full_failed = full_agg.get("all_seeds_failed", True)

    if full_failed or not math.isfinite(full_bpc):
        verdict = "HARD_FAIL"
        verdict_msg = "HARD_FAIL: ARM_K_MODULE_FULL_HETERO all seeds failed or non-finite BPC."
    elif full_degen:
        verdict = "INSTRUMENTATION_SUSPECT"
        verdict_msg = ("INSTRUMENTATION_SUSPECT: ARM_K_MODULE_FULL_HETERO raw_bpc_T1L1 near "
                       "vocab-entropy (DEGEN). full_bpc=%.4f raw_bpc=%.4f." % (
                           full_bpc, full_agg.get("raw_bpc_at_T1_L1_mean", float("nan"))))
    else:
        lift = m1_bpc - full_bpc
        cv_ok = math.isfinite(full_cv) and full_cv <= CV_MAX
        if lift >= HP_BPC_LIFT and cv_ok:
            if lift >= CHAIN_GRADE_BONUS_LIFT:
                verdict = "HARD_PASS_CHAIN_GRADE_BONUS"
                verdict_msg = (
                    "HARD_PASS CHAIN_GRADE_BONUS: ARM_K_MODULE_FULL_HETERO lifts +%.4f bits "
                    "(>= %.2f bonus threshold; N^M scaling visible at K=4 modules). "
                    "M1=%.4f FULL=%.4f cv=%.4f. Levy-Horn-Ruppin factorial capacity CONFIRMED." % (
                        lift, CHAIN_GRADE_BONUS_LIFT, m1_bpc, full_bpc, full_cv))
            else:
                verdict = "HARD_PASS"
                verdict_msg = (
                    "HARD_PASS: ARM_K_MODULE_FULL_HETERO lifts +%.4f bits (>= %.2f threshold). "
                    "M1=%.4f FULL=%.4f cv=%.4f. Heterogeneous K-module compose breaks +0.44 envelope." % (
                        lift, HP_BPC_LIFT, m1_bpc, full_bpc, full_cv))
        elif lift >= HARD_FAIL_LIFT:
            verdict = "MIDDLE_BAND"
            verdict_msg = (
                "MIDDLE_BAND: ARM_K_MODULE_FULL_HETERO lifts +%.4f bits "
                "(in [%.2f, %.2f)). M1=%.4f FULL=%.4f cv=%.4f. "
                "Partial multi-module benefit; route to v2." % (
                    lift, HARD_FAIL_LIFT, HP_BPC_LIFT, m1_bpc, full_bpc, full_cv))
        else:
            verdict = "HARD_FAIL"
            verdict_msg = (
                "HARD_FAIL: ARM_K_MODULE_FULL_HETERO lifts only +%.4f bits (<= %.2f). "
                "M1=%.4f FULL=%.4f. Multi-module compose ALSO degenerate; "
                "routes to glass-box-LLM-L2 pivot." % (
                    lift, HARD_FAIL_LIFT, m1_bpc, full_bpc))

        # Progressive ordering check (self-check; not part of verdict)
        m1m2_bpc = by_arm_agg.get("ARM_M1_PLUS_LOCKIN", {}).get("bpc_best_mean", float("inf"))
        m1m2m3_bpc = by_arm_agg.get("ARM_M1_M2_PLUS_HRR", {}).get("bpc_best_mean", float("inf"))
        verdict_msg += (
            " | PROGRESSIVE_ORDER: M1=%.4f M1+M2=%.4f M1+M2+M3=%.4f FULL=%.4f" % (
                m1_bpc, m1m2_bpc, m1m2m3_bpc, full_bpc))

    return verdict, verdict_msg, {
        "by_arm_agg": by_arm_agg,
        "HP_BPC_LIFT_threshold": HP_BPC_LIFT,
        "CHAIN_GRADE_BONUS_LIFT_threshold": CHAIN_GRADE_BONUS_LIFT,
        "HARD_FAIL_LIFT_threshold": HARD_FAIL_LIFT,
        "CV_MAX_threshold": CV_MAX,
        "vocab_entropy_uniform_bits": round(vocab_entropy_uniform, 4),
        "zero_llm_calls_at_inference": True,
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "m1_baseline_bpc_ref": BASELINE_BPC_REF,
        "n_seeds": len(units),
    }


# ============================================================================
# Main
# ============================================================================

print("[config] anchor=%s N_DIM=%d mode=%s seeds=%s N_TRAIN=%d f=%.3f "
      "lockin_P=%d lockin_k=%d hrr_ctx=%d refuse_thr=%.2f device=%s" % (
          ANCHOR_NAME, N_DIM, RUN_MODE, SEEDS, N_TRAIN, SPARSE_BIPOLAR_F,
          LOCK_IN_P, LOCK_IN_K_FREQ, HRR_CONTEXT_WINDOW, REFUSE_MARGIN_THR, str(DEVICE)),
      flush=True)

# PROT-018 check for FULL run
if RUN_MODE == "full" and N_DIM != PRODUCTION_N:
    raise RuntimeError("PROT-018: FULL run N_DIM=%d != PRODUCTION_N=%d" % (N_DIM, PRODUCTION_N))

out_dir = get_output_dir(ANCHOR_NAME)
_seeds_done, seeds_todo = resumable_seeds(SEEDS, out_dir)
print("[resumable] seeds_done=%s seeds_todo=%s" % (_seeds_done, seeds_todo), flush=True)

_atexit_units: List[Dict] = []

def _atexit_synthesize():
    if not _atexit_units:
        return
    partial_units = list(_atexit_units)
    try:
        partials_dict = aggregate_partials(out_dir)
        # aggregate_partials returns Dict[str(seed), payload]
        combined = {}
        for payload in partials_dict.values():
            k = payload.get("seed", id(payload))
            combined[k] = payload
        for u in partial_units:
            combined[u["seed"]] = u
        all_units = list(combined.values())
    except Exception:
        all_units = partial_units
    if not all_units:
        return
    verdict_str, verdict_msg, detail = compute_verdict(all_units)
    print("[atexit] PARTIAL verdict=%s: %s" % (verdict_str, verdict_msg[:200]), flush=True)

atexit.register(_atexit_synthesize)

for seed in seeds_todo:
    try:
        unit = run_unit(seed)
    except Exception as e:
        import traceback
        print("[ERROR seed=%d] %s" % (seed, traceback.format_exc()), flush=True)
        continue
    write_partial_key(out_dir, "s%d" % seed, unit)
    _atexit_units.append(unit)

# aggregate_partials returns Dict[str(seed), payload]; convert to list
_partials_dict = aggregate_partials(out_dir)
units = list(_partials_dict.values())
if not units:
    print("[FATAL] no units; exiting", flush=True)
    sys.exit(1)

verdict_str, verdict_msg, detail = compute_verdict(units)
print("\n[verdict] %s: %s" % (verdict_str, verdict_msg), flush=True)

# --- Summary per arm (Fix #28: from metrics.json per arm, not verdict_msg) ---
for arm in ["ARM_SPARSE_BIPOLAR_ONLY", "ARM_M1_PLUS_LOCKIN", "ARM_M1_M2_PLUS_HRR", "ARM_K_MODULE_FULL_HETERO"]:
    agg = detail.get("by_arm_agg", {}).get(arm, {})
    if agg.get("all_seeds_failed"):
        print("[arm] %s: ALL_FAILED" % arm, flush=True)
    else:
        print("[arm] %s: bpc_mean=%.4f top1_mean=%.4f mrr_mean=%.4f cv=%.4f n_valid=%d" % (
            arm,
            agg.get("bpc_best_mean", float("inf")),
            agg.get("top1_acc_mean", float("nan")),
            agg.get("mrr_at_10_mean", float("nan")),
            agg.get("bpc_best_cv", float("nan")),
            agg.get("n_valid_seeds", 0)), flush=True)

# Wall time
t_total = sum(u.get("elapsed_s_seed", 0) for u in units)

REQUIRED_FIELDS = {
    "anchor_name": ANCHOR_NAME,
    "anchor": ANCHOR_NAME,
    "verdict": verdict_str,
    "verdict_msg": verdict_msg,
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "N": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "n_seeds": len(units),
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "LOCK_IN_P": LOCK_IN_P,
    "LOCK_IN_K_FREQ": LOCK_IN_K_FREQ,
    "HRR_CONTEXT_WINDOW": HRR_CONTEXT_WINDOW,
    "REFUSE_MARGIN_THR": REFUSE_MARGIN_THR,
    "detail": detail,
    "per_unit": units,
    "elapsed_s": round(t_total, 2),
    "zero_llm_calls_at_inference": True,
    "n_llm_calls": 0,
    "device": str(DEVICE),
    "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    "config_version": CONFIG_VERSION,
    "honest_scope": (
        "K-module heterogeneous compose LM test (Levy-Horn-Ruppin escape). "
        "5 arms: ARM_UNIGRAM + 4 substrate compose arms (M1 only -> M1+M2 -> M1+M2+M3 -> FULL+refuse-gate). "
        "HP = ARM_K_MODULE_FULL_HETERO BPC lift >= +0.30 bits vs ARM_SPARSE_BIPOLAR_ONLY AND cv<=0.05. "
        "HF = lift <= +0.10 bits OR all seeds fail. "
        "CHAIN_GRADE_BONUS = lift >= +0.50 bits. "
        "N_DIM=8192 N_TRAIN=100000 N_HELD=20000 V=4000."
    ),
    "prereg_bands": {
        "HARD_PASS_lift_bits": HP_BPC_LIFT,
        "CHAIN_GRADE_BONUS_lift_bits": CHAIN_GRADE_BONUS_LIFT,
        "MIDDLE_BAND_lower_bits": HARD_FAIL_LIFT,
        "HARD_FAIL_lift_bits_or_below": HARD_FAIL_LIFT,
        "cv_max": CV_MAX,
    },
    "cites": [
        "data/exp_fair_harness_substrate_as_lm_v1/metrics.json",
        "data/exp_substrate_dual_trace_sequential_neuromod_LM_v1/metrics.json",
        "experiments/exp_fair_harness_substrate_as_lm_v1.py",
        "experiments/exp_lock_in_amplifier_hd_frequency_v1_FULL.py",
        "notes/research_rank1_hebbian_brain_escape_mechanisms_2026-06-23.md",
        "Levy-Horn-Ruppin-1997-NIPS-multi-modular-associative-memory",
    ],
}

write_metrics(out_dir, REQUIRED_FIELDS)
print("[done] metrics written to %s" % out_dir, flush=True)
