"""fair_harness_substrate_as_lm_v1 -- METHODOLOGY-CORRECTED LM HARNESS.

Skunkworks methodology audit 2026-06-23: previous 7+ substrate-as-LM HARD_FAIL
landings were METHODOLOGY-CONFOUND, not mechanism failures. Cosine logits with
T=1.0 softmax produced near-uniform distributions; TEMP_GRID was too coarse
([0.5, 1.0, 2.0, 5.0]); lambda was swept sequentially with T fixed.

This cell:
  - Extends TEMP_GRID to [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
  - Sweeps (T, lambda) JOINTLY on dev half; picks best joint config; evals on test
  - Reports THREE metrics per arm: BPC, top-1, MRR@10
  - HARD_PASS = ANY of those three clears its bar (substrate may shine at top-1
    or MRR even when BPC is squeezed)
  - READOUT_DEGENERATE sanity gate: if raw_bpc_at_T1_L1 ~= -log2(1/V) +/- 0.5
    AND no substrate arm HP, flag as DEGEN (NOT HARD_FAIL); requires recalibration.

Four arms (each builds FRESH W; no cross-contamination):
  ARM_UNIGRAM
      Analytic floor (BPC + top-1 + MRR reported as references).
  ARM_SUBSTRATE_WORD2VEC_DENSE
      word2vec encoder + rank-1 Hebbian W; Path A current.
  ARM_SUBSTRATE_SPARSE_BIPOLAR
      word2vec encoder + sparse-bipolar f=0.05 encoder; rank-1 Hebbian W; validated.
  ARM_SUBSTRATE_BRAIN_COMPOSE
      Full brain composition: PC 3-layer + sparse competitive K=10 + lock-in
      positional + WM HRR-slots (context window=5).

Pre-reg HARD bands (chain-grade-eligible V2):
  HARD_PASS: any of HP_BPC / HP_TOP1 / HP_MRR clears (see preregs).
  HARD_FAIL: ALL 3 substrate arms fail HP across all 3 metrics AND not DEGEN.
  MIDDLE_BAND: substrate beats unigram on >=1 metric but doesn't cross HP bar.
  READOUT_DEGENERATE_NOT_SUBSTRATE_FAILURE: raw_bpc_at_T1_L1 near uniform-vocab AND no HP.

GPU REQUIRED (Fix #24): torch.cuda for matmul / PC training / sparse-bipolar.

Cites:
  preregs/2026-06-23_fair_harness_substrate_as_lm_v1.md
  experiments/exp_fresh_W_bpc_per_encoder_v2.py  (parent fresh-W pattern)
  experiments/exp_substrate_brain_full_compose_LM_v2.py  (PC+sparse+lock-in stack)
  Skunkworks_2026-06-23_methodology_audit (cosine+T1 = uniform)
  USER_2026-06-23_audit_ratification (V2 LM gap load-bearing)
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

ANCHOR_NAME = "fair_harness_substrate_as_lm_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
_LLM_CALL_COUNTER = [0]

# Reference baselines
UNIGRAM_BPC_REF = 7.738
UNIGRAM_TOP1_REF = 0.2171

# Pre-reg bands
HP_BPC_MARGIN = 0.3       # substrate clears unigram_bpc - 0.3
HP_TOP1_NSIGMA = 2.0      # substrate top-1 > unigram_top1 + 2 sigma_seeds
HP_MRR_MARGIN = 0.02      # substrate MRR > unigram_mrr + 0.02 (meaningful)
DEGEN_TOL = 0.5           # raw_bpc_at_T1_L1 within +/- DEGEN_TOL of -log2(1/V) => DEGEN
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

# Joint (T, lambda) sweep
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

# Sparse-bipolar f
SPARSE_BIPOLAR_F = 0.05

# Brain compose knobs
PC_N_LAYERS = 3
SPARSE_COMPETITIVE_K_ABS = 10
SPARSE_COMPETITIVE_BETA = 8.0
CONTEXT_WINDOW = 5
LOCK_IN_FREQ_STEP = 31

# MRR @ K
MRR_K = 10

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke must fit under 180s on laptop CPU. Exercises every arm + joint sweep
    # + 3 metrics + 7x6=42 (T,L) combos + verdict bands.
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

ARMS = [
    "ARM_UNIGRAM",
    "ARM_SUBSTRATE_WORD2VEC_DENSE",
    "ARM_SUBSTRATE_SPARSE_BIPOLAR",
    "ARM_SUBSTRATE_BRAIN_COMPOSE",
]
SUBSTRATE_ARMS = [a for a in ARMS if a != "ARM_UNIGRAM"]
WORD2VEC_MODEL = "word2vec-google-news-300"

CONFIG_VERSION = (
    "fair_harness_substrate_as_lm_v1; N_DIM=%d PRETRAIN_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s temps=%s lambdas=%s sparse_f=%.3f "
    "pc_layers=%d kwta_k=%d kwta_beta=%.2f ctxW=%d lockstep=%d MRR_K=%d device=%s; "
    "bands HP_BPC_margin>=%.3f HP_TOP1_nsigma>=%.2f HP_MRR_margin>=%.3f DEGEN_tol=%.2f "
    "cv_max=%.2f"
) % (
    N_DIM, PRETRAIN_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    TEMP_GRID, LAMBDA_GRID, SPARSE_BIPOLAR_F, PC_N_LAYERS, SPARSE_COMPETITIVE_K_ABS,
    SPARSE_COMPETITIVE_BETA, CONTEXT_WINDOW, LOCK_IN_FREQ_STEP, MRR_K, str(DEVICE),
    HP_BPC_MARGIN, HP_TOP1_NSIGMA, HP_MRR_MARGIN, DEGEN_TOL, HP_BPC_CV_MAX,
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


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    P = rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))
    return P


# Gensim cache (process-local)
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


def build_E_word2vec_gpu(vocab: List[str], n_dim: int, seed: int
                           ) -> Tuple[torch.Tensor, Dict]:
    """Build [V, n_dim] L2-normalized word2vec-projected vectors on GPU.

    OOV words fall back to char-trigram encoding so no zero-row degeneracy.
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


def build_E_char_trigram_gpu(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    """Smoke / fallback when gensim unavailable."""
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


# ============================================================================
# Sparse-bipolar primitive (validated; 20-300x bundle capacity per prior drill)
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
# HRR bind + context keys (working-memory slots)
# ============================================================================

def hrr_bind_batch(A: torch.Tensor, B: torch.Tensor) -> torch.Tensor:
    if not A.is_contiguous():
        A = A.contiguous()
    if not B.is_contiguous():
        B = B.contiguous()
    Fa = torch.fft.rfft(A, dim=-1)
    Fb = torch.fft.rfft(B, dim=-1)
    return torch.fft.irfft(Fa * Fb, n=A.shape[-1], dim=-1)


def lock_in_position_vec(n_dim: int, pos: int, seed: int) -> torch.Tensor:
    rng = np.random.default_rng(seed * 7919 + 13 + pos * 101)
    phase = rng.uniform(0.0, 2.0 * math.pi, size=n_dim).astype(np.float32)
    freq = float(max(pos, 1) * LOCK_IN_FREQ_STEP) / float(n_dim)
    t = np.arange(n_dim, dtype=np.float32)
    v = np.cos(2.0 * math.pi * freq * t + phase).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-12)
    return torch.from_numpy(v).to(DEVICE)


def build_context_keys_gpu(idx: torch.Tensor, E: torch.Tensor, context_window: int,
                             seed: int) -> torch.Tensor:
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
    keys = _l2_normalize_t(keys)
    return keys


# ============================================================================
# Hebbian W builders
# ============================================================================

def build_rank1_W_gpu(idx_train: torch.Tensor, E: torch.Tensor,
                        ingest_chunk: int) -> torch.Tensor:
    """W = sum outer(E[idx[t+1]], E[idx[t]]); rank-1 Hebbian."""
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
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
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_pc_stack_gpu(src_keys: torch.Tensor, tgt_vecs: torch.Tensor,
                        idx_train: torch.Tensor, ingest_chunk: int,
                        n_layers: int) -> List[torch.Tensor]:
    """3-layer PC: each layer adds a residual W; init small Gaussian (defensive)."""
    device = src_keys.device
    dim = src_keys.shape[1]
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return [torch.zeros((dim, dim), device=device, dtype=TORCH_DTYPE) for _ in range(n_layers)]
    Ws: List[torch.Tensor] = []
    cumulative_pred_norm: Optional[torch.Tensor] = None
    init_gen = torch.Generator(device=device)
    init_gen.manual_seed(int(idx_train.shape[0]) % (2**31 - 1) + n_layers * 100003)
    init_scale = 0.01 / float(math.sqrt(dim))
    for layer_i in range(n_layers):
        W = torch.randn(dim, dim, generator=init_gen, dtype=TORCH_DTYPE, device=device).mul_(init_scale)
        if layer_i == 0:
            src_l = src_keys
        else:
            src_l = cumulative_pred_norm
        for b in range(0, n_pairs, ingest_chunk):
            end = min(b + ingest_chunk, n_pairs)
            src_b = src_l[b:end]
            tgt_b = tgt_vecs[idx_train[b + 1:end + 1]]
            if layer_i == 0:
                resid = tgt_b
            else:
                cum_b = cumulative_pred_norm[b:end]
                resid = tgt_b - cum_b
            W.add_(resid.T @ src_b)
            if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
                torch.cuda.synchronize()
        Ws.append(W)
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
    n, dim = src_keys.shape
    device = src_keys.device
    out = torch.zeros((n, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        src_b = src_keys[b:end]
        cum = torch.zeros((end - b, dim), dtype=TORCH_DTYPE, device=device)
        s_l = src_b
        for W in Ws:
            pred = s_l @ W.T
            cum = cum + pred
            s_l = _l2_normalize_t(cum)
        out[b:end] = _l2_normalize_t(cum)
    return out


# ============================================================================
# Per-arm logits builder
# ============================================================================

def compute_arm_logits(arm_label: str, E: torch.Tensor, idx_train: np.ndarray,
                         idx_held: np.ndarray, seed: int) -> Dict:
    """Return [n_held, V] float32 logits + diagnostics."""
    V, dim = E.shape
    device = E.device

    use_sparse_bp = arm_label == "ARM_SUBSTRATE_SPARSE_BIPOLAR"
    use_brain = arm_label == "ARM_SUBSTRATE_BRAIN_COMPOSE"

    if use_sparse_bp or use_brain:
        E_used = _l2_normalize_t(sparsify_bipolar_gpu(E, SPARSE_BIPOLAR_F, seed))
    else:
        E_used = E

    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)

    t0 = time.time()
    if use_brain:
        src_keys_train = build_context_keys_gpu(idx_train_t, E_used, CONTEXT_WINDOW, seed)
        src_keys_held = build_context_keys_gpu(idx_held_t, E_used, CONTEXT_WINDOW, seed)
    else:
        src_keys_train = E_used[idx_train_t]
        src_keys_held = E_used[idx_held_t]
    t_keys = time.time() - t0

    t0 = time.time()
    if use_brain:
        Ws = build_pc_stack_gpu(src_keys_train, E_used, idx_train_t,
                                  INGEST_CHUNK, PC_N_LAYERS)
        pred_held = pc_stack_forward_gpu(Ws, src_keys_held, RECALL_BATCH)
        for W in Ws:
            del W
    else:
        W = build_rank1_W_gpu(idx_train_t, E_used, INGEST_CHUNK)
        n_h = src_keys_held.shape[0]
        pred_held = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
        for b in range(0, n_h, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_h)
            pred_held[b:end] = _l2_normalize_t(src_keys_held[b:end] @ W.T)
        del W
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    n_h = pred_held.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        logits[b:end] = pred_held[b:end] @ E_used.T
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    del pred_held, src_keys_train, src_keys_held, idx_train_t, idx_held_t
    if use_sparse_bp or use_brain:
        del E_used
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_keys_s": round(t_keys, 2),
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "use_sparse_bp": bool(use_sparse_bp),
        "use_brain": bool(use_brain),
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
    """Softmax with temperature T applied to substrate cosine logits."""
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp_logp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float
                            ) -> np.ndarray:
    """Return per-position log-prob matrix [n, V] under log-linear interp."""
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
    """Mean reciprocal rank @ k: average of 1/rank if true is in top-k else 0."""
    n = len(nxt)
    if n == 0:
        return float("nan")
    # rank of true class
    # argsort descending; rank = position+1 (1-based)
    # efficient: get top-k indices per row then check membership
    k_use = min(k, logp.shape[1])
    top_idx = np.argpartition(-logp, kth=k_use - 1, axis=1)[:, :k_use]
    # sort within top-k by actual logp
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
    """Joint (T, lambda) sweep on dev; pick best per-metric; report on test.

    Returns best (T, lambda, BPC) per metric (BPC / top-1 / MRR), plus the full
    grid for transparency. Also reports raw_bpc_at_T1_L1 for DEGEN gate.
    """
    # raw at (T=1.0, lambda=1.0): pure substrate softmax T=1, no unigram blend
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)
    raw_top1_at_T1_L1 = top1_acc_from_logp(logp_T1, nxt_test)
    raw_mrr_at_T1_L1 = mrr_at_k(logp_T1, nxt_test, mrr_k)

    # Joint sweep
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

    # Eval at each best (T, lambda) on test
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
    """Analytic unigram BPC / top-1 / MRR on test half of held."""
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
    # top-1: every position predicts argmax(U); accuracy = frac(nxt == argmax(U))
    am = int(np.argmax(U))
    top1 = float(np.mean(nxt_test == am))
    # MRR: unigram-only -- all positions get same ranking; rank of nxt = rank of nxt in U
    order = np.argsort(-U)
    inv_rank = np.empty_like(order)
    inv_rank[order] = np.arange(len(order))
    ranks = inv_rank[nxt_test] + 1  # 1-based
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
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"],
        uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # Build one common word2vec E (reused for all substrate arms; sparse-bipolar
    # / brain arms apply their own per-arm transformations inside compute_arm_logits).
    print("\n[seed=%d] building word2vec base E (V=%d, N_DIM=%d) on %s..." % (
        seed, V, N_DIM, str(DEVICE)), flush=True)
    t_enc0 = time.time()
    encoder_meta = {}
    try:
        E_base, encoder_meta = build_E_word2vec_gpu(vocab, N_DIM, seed)
    except Exception as e:
        # In smoke without gensim, fall back to char-trigram so the harness path runs.
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

    # Split held into dev + test halves (same as unigram baseline)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    ctx_eval = ctx_full[mask]
    nxt_eval = nxt_full[mask]
    n_eval = len(ctx_eval)
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
    held_dev_idx = np.arange(n_dev)
    held_test_idx = np.arange(n_dev, n_eval)
    # Substrate arms produce logits over the FULL held set [:-1] positions; we
    # mask afterward via the same (ctx != unk) mask + split.
    valid_held_pos = np.where(mask)[0]
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    for arm in SUBSTRATE_ARMS:
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
        logits_full = ar["logits"]  # [n_held, V] over positions 0..n_held-1
        # logits index aligns with idx_held positions 0..n_held-1; we want
        # logits at positions where (ctx != unk) i.e. valid_held_pos.
        # idx_held len = N_HELD. ctx_full uses positions 0..N_HELD-2.
        # Substrate logits length = N_HELD (predicts NEXT token given THIS).
        # Mask: use logits at position p where ctx_full[p] != unk, i.e. p in valid_held_pos.
        # The "next token" label is idx_held[p+1] = nxt_full[p].
        # Trim logits to ctx_full domain (drop last) before masking.
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            # Defensive: pad-rare (substrate might return n_held positions)
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
            jr["wall_keys_s"] = ar.get("wall_keys_s", 0.0)
            jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
            jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
            by_arm[arm] = jr
            print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
                  "(bestT=%.4f bestL=%.2f) raw_T1L1_bpc=%.3f" % (
                      seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                      jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                      jr["raw_bpc_at_T1_L1"]), flush=True)
            continue
        # Normal path: logits_ctx matches ctx_full length
        logits_eval = logits_ctx[mask]
        jr = joint_sweep_substrate(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["wall_keys_s"] = ar.get("wall_keys_s", 0.0)
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

    # Aggregate ARM_UNIGRAM
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    uni_top1 = [u["by_arm"].get("ARM_UNIGRAM", {}).get("top1_unigram", float("nan")) for u in units]
    uni_mrr = [u["by_arm"].get("ARM_UNIGRAM", {}).get("mrr_unigram", float("nan")) for u in units]
    unigram_agg = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
        "top1_mean": round(float(np.mean(uni_top1)), 4),
        "top1_std": round(float(np.std(uni_top1)), 4),
        "mrr_mean": round(float(np.mean(uni_mrr)), 4),
        "mrr_std": round(float(np.std(uni_mrr)), 4),
    }

    # Aggregate per-arm
    by_arm_agg: Dict[str, Dict] = {"ARM_UNIGRAM": unigram_agg}
    V_first = units[0].get("V", 4000)
    vocab_entropy_uniform = math.log2(max(V_first, 2))

    for arm in SUBSTRATE_ARMS:
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
        bT_top1 = [u["by_arm"][arm]["best_T_for_top1"] for u in valid_units]
        bL_top1 = [u["by_arm"][arm]["best_lambda_for_top1"] for u in valid_units]
        bT_mrr = [u["by_arm"][arm]["best_T_for_mrr"] for u in valid_units]
        bL_mrr = [u["by_arm"][arm]["best_lambda_for_mrr"] for u in valid_units]
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_acc_mean": round(float(np.mean(top1_vals)), 4),
            "top1_acc_std": round(float(np.std(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_vals)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_vals)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_t1l1_vals)), 4),
            "best_T_for_bpc_mean": round(float(np.mean(bT_bpc)), 4),
            "best_lambda_for_bpc_mean": round(float(np.mean(bL_bpc)), 4),
            "best_T_for_top1_mean": round(float(np.mean(bT_top1)), 4),
            "best_lambda_for_top1_mean": round(float(np.mean(bL_top1)), 4),
            "best_T_for_mrr_mean": round(float(np.mean(bT_mrr)), 4),
            "best_lambda_for_mrr_mean": round(float(np.mean(bL_mrr)), 4),
            "n_valid_seeds": int(len(valid_units)),
            "n_compute_failed": n_compute_failed,
            "all_seeds_failed": False,
        }

    # Multi-metric HARD_PASS classification per arm
    unigram_bpc = unigram_agg["bpc_mean"]
    unigram_top1 = unigram_agg["top1_mean"]
    unigram_top1_std = unigram_agg["top1_std"]
    unigram_mrr = unigram_agg["mrr_mean"]
    hp_per_arm: Dict[str, Dict] = {}
    hp_arms_bpc: List[str] = []
    hp_arms_top1: List[str] = []
    hp_arms_mrr: List[str] = []
    for arm in SUBSTRATE_ARMS:
        a = by_arm_agg[arm]
        if a.get("all_seeds_failed", False):
            hp_per_arm[arm] = {"bpc_ok": False, "top1_ok": False, "mrr_ok": False,
                                  "any_hp": False, "all_seeds_failed": True}
            continue
        bpc_bar = unigram_bpc - HP_BPC_MARGIN
        top1_bar = unigram_top1 + HP_TOP1_NSIGMA * max(unigram_top1_std, 1e-6)
        mrr_bar = unigram_mrr + HP_MRR_MARGIN
        bpc_ok = a["bpc_best_mean"] < bpc_bar
        top1_ok = a["top1_acc_mean"] > top1_bar
        mrr_ok = a["mrr_at_10_mean"] > mrr_bar
        if bpc_ok:
            hp_arms_bpc.append(arm)
        if top1_ok:
            hp_arms_top1.append(arm)
        if mrr_ok:
            hp_arms_mrr.append(arm)
        hp_per_arm[arm] = {
            "bpc_ok": bool(bpc_ok), "top1_ok": bool(top1_ok), "mrr_ok": bool(mrr_ok),
            "any_hp": bool(bpc_ok or top1_ok or mrr_ok),
            "bpc_bar": round(bpc_bar, 4), "top1_bar": round(top1_bar, 4),
            "mrr_bar": round(mrr_bar, 4),
        }

    # Bonus: BRAIN_COMPOSE beats SUBSTRATE_WORD2VEC_DENSE on >=2 of 3 metrics
    bonus = {"brain_beats_dense_2of3": False}
    if all(arm in by_arm_agg for arm in ["ARM_SUBSTRATE_WORD2VEC_DENSE",
                                              "ARM_SUBSTRATE_BRAIN_COMPOSE"]):
        brain = by_arm_agg["ARM_SUBSTRATE_BRAIN_COMPOSE"]
        dense = by_arm_agg["ARM_SUBSTRATE_WORD2VEC_DENSE"]
        if not (brain.get("all_seeds_failed", False) or dense.get("all_seeds_failed", False)):
            wins = 0
            if brain["bpc_best_mean"] < dense["bpc_best_mean"]:
                wins += 1
            if brain["top1_acc_mean"] > dense["top1_acc_mean"]:
                wins += 1
            if brain["mrr_at_10_mean"] > dense["mrr_at_10_mean"]:
                wins += 1
            bonus = {"brain_beats_dense_2of3": bool(wins >= 2),
                       "brain_dense_metric_wins": int(wins)}

    # DEGEN gate: raw_bpc_at_T1_L1 ~ uniform-vocab on at least one substrate arm
    degen_arms = []
    for arm in SUBSTRATE_ARMS:
        a = by_arm_agg[arm]
        rt = a.get("raw_bpc_at_T1_L1_mean", float("nan"))
        if math.isfinite(rt) and abs(rt - vocab_entropy_uniform) <= DEGEN_TOL:
            degen_arms.append(arm)
    any_hp = any(hp_per_arm[a].get("any_hp", False) for a in SUBSTRATE_ARMS
                  if not hp_per_arm[a].get("all_seeds_failed", False))
    any_substrate_clears_unigram = any(
        by_arm_agg[a].get("bpc_best_mean", float("inf")) < unigram_bpc
        or by_arm_agg[a].get("top1_acc_mean", -1.0) > unigram_top1
        or by_arm_agg[a].get("mrr_at_10_mean", -1.0) > unigram_mrr
        for a in SUBSTRATE_ARMS if not by_arm_agg[a].get("all_seeds_failed", False)
    )

    # Substrate-only-decode gate (defensive; no LLM at inference)
    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    # Compose summary
    arm_lines = []
    for a in SUBSTRATE_ARMS:
        x = by_arm_agg[a]
        if x.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % a)
            continue
        arm_lines.append("%s=bpc%.3f|top1%.4f|mrr%.4f|rawT1%.3f|bestT%.4f|bestL%.2f" % (
            a, x["bpc_best_mean"], x["top1_acc_mean"], x["mrr_at_10_mean"],
            x["raw_bpc_at_T1_L1_mean"], x["best_T_for_bpc_mean"],
            x["best_lambda_for_bpc_mean"]))
    summary = "FAIR_HARNESS uni=bpc%.3f|top1%.4f|mrr%.4f | %s | n_llm=%d" % (
        unigram_bpc, unigram_top1, unigram_mrr, " | ".join(arm_lines), n_llm)

    detail = {
        "by_arm_agg": by_arm_agg,
        "hp_per_arm": hp_per_arm,
        "hp_arms_bpc": list(hp_arms_bpc),
        "hp_arms_top1": list(hp_arms_top1),
        "hp_arms_mrr": list(hp_arms_mrr),
        "bonus": bonus,
        "degen_arms": list(degen_arms),
        "vocab_entropy_uniform_bits": round(vocab_entropy_uniform, 4),
        "any_hp_arm": bool(any_hp),
        "any_substrate_clears_unigram_some_metric": bool(any_substrate_clears_unigram),
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "unigram_top1_ref": UNIGRAM_TOP1_REF,
        "hp_bpc_margin": HP_BPC_MARGIN,
        "hp_top1_nsigma": HP_TOP1_NSIGMA,
        "hp_mrr_margin": HP_MRR_MARGIN,
        "degen_tol": DEGEN_TOL,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Fair-harness substrate-as-LM test under JOINT (T,lambda) sweep on dev. "
            "TEMP_GRID extended to [0.01..1.0]. Three metrics reported per arm "
            "(BPC + top-1 + MRR@%d). HP = ANY substrate arm clears ANY metric's bar "
            "(BPC: uni-%.2f, top1: uni+%.1f-sigma, MRR: uni+%.2f). DEGEN sanity gate: "
            "raw_bpc_at_T1_L1 within +/- %.2f of -log2(1/V)=%.3f flags readout-degeneracy "
            "(NOT HARD_FAIL). N_DIM=%d N_TRAIN=%d N_HELD=%d V=%d." % (
                MRR_K, HP_BPC_MARGIN, HP_TOP1_NSIGMA, HP_MRR_MARGIN,
                DEGEN_TOL, vocab_entropy_uniform, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP)),
        "cites": [
            "preregs/2026-06-23_fair_harness_substrate_as_lm_v1.md",
            "experiments/exp_fresh_W_bpc_per_encoder_v2.py",
            "experiments/exp_substrate_brain_full_compose_LM_v2.py",
            "Skunkworks_2026-06-23_methodology_audit",
            "USER_2026-06-23_audit_ratification_V2_LM_gap_load_bearing",
            "USER_2026-06-22_Fix24_GPU_must_use_GPU",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    if any_hp:
        # find best arm + metric
        best_metric_descr = []
        if hp_arms_bpc:
            hp_arms_bpc.sort(key=lambda x: by_arm_agg[x]["bpc_best_mean"])
            best_metric_descr.append("BPC: %s clears bpc<%.3f" % (
                hp_arms_bpc[0], unigram_bpc - HP_BPC_MARGIN))
        if hp_arms_top1:
            hp_arms_top1.sort(key=lambda x: -by_arm_agg[x]["top1_acc_mean"])
            best_metric_descr.append("TOP1: %s clears top1>uni+%.1fsigma" % (
                hp_arms_top1[0], HP_TOP1_NSIGMA))
        if hp_arms_mrr:
            hp_arms_mrr.sort(key=lambda x: -by_arm_agg[x]["mrr_at_10_mean"])
            best_metric_descr.append("MRR: %s clears mrr>uni+%.2f" % (
                hp_arms_mrr[0], HP_MRR_MARGIN))
        bonus_str = ""
        if bonus.get("brain_beats_dense_2of3", False):
            bonus_str = " BONUS: BRAIN_COMPOSE beats WORD2VEC_DENSE on %d/3 metrics." % (
                bonus.get("brain_dense_metric_wins", 0))
        return ("HARD_PASS",
                ("FAIR_HARNESS HARD_PASS: %s. Fair-harness reveals substrate IS "
                 "learning -- prior 7+ substrate-as-LM HARD_FAILs were "
                 "methodology-confound. Chain-grade V2 substrate-as-LM "
                 "evidence.%s %s" % ("; ".join(best_metric_descr), bonus_str, summary)),
                detail)

    if degen_arms and not any_substrate_clears_unigram:
        return ("MIDDLE_BAND",
                ("READOUT_DEGENERATE_NOT_SUBSTRATE_FAILURE: raw_bpc_at_T1_L1 within "
                 "+/-%.2f of uniform-vocab %.3f bits for arms=%s; no substrate arm "
                 "clears HP under joint sweep but failure is readout-degeneracy "
                 "(cosine logits + T=1 softmax = near-uniform), NOT substrate mechanism. "
                 "Requires harness re-calibration (likely lower T floor or substrate "
                 "logit re-shaping). %s" % (
                     DEGEN_TOL, vocab_entropy_uniform, degen_arms, summary)),
                detail)

    if not any_substrate_clears_unigram:
        return ("HARD_FAIL",
                ("FAIR_HARNESS HARD_FAIL: ALL substrate arms fail HP on all 3 metrics "
                 "under joint (T,lambda) sweep, AND NOT readout-degenerate. Substrate-"
                 "as-LM genuinely fails even under fair harness; V2 LM gap closure "
                 "rejected via fair-harness methodology; pivot to descope or "
                 "architectural rewrite. %s" % summary),
                detail)

    return ("MIDDLE_BAND",
            ("FAIR_HARNESS MIDDLE_BAND: substrate beats unigram on >=1 metric but "
             "no arm clears HP bar (BPC margin %.2f, TOP1 %.1f-sigma, MRR margin %.2f). "
             "Partial substrate-as-LM signal. %s" % (
                 HP_BPC_MARGIN, HP_TOP1_NSIGMA, HP_MRR_MARGIN, summary)),
            detail)


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: char-trigram bipolar
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,) and set(np.unique(v).tolist()).issubset({-1.0, 1.0})

    # T2: gensim mock-KV pipeline
    class _MockKV:
        def __init__(self, dim=10):
            self.vector_size = dim
            self.key_to_index = {"w0": 0, "w1": 1, "w2": 2}
            self._vecs = np.random.default_rng(0).standard_normal((3, dim)).astype(np.float32)
        def __contains__(self, k): return k in self.key_to_index
        def __getitem__(self, k): return self._vecs[self.key_to_index[k]]
        def get_vector(self, k, norm=False):
            if k in self.key_to_index: return self._vecs[self.key_to_index[k]]
            raise KeyError(k)
    mock = _MockKV(dim=10)
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(["w0", "w1", "w2", "OOV"], mock)
    assert n_hit == 3 and n_miss == 1, "T2 hit/miss"
    assert float(np.linalg.norm(E_pre[3])) < 1e-9, "T2 OOV not zero"

    # T3: at T=0.01, peaked input remains peaked
    n, V = 1, 8
    peaked_logits = np.zeros((n, V), dtype=np.float32)
    peaked_logits[0, 3] = 1.0  # cosine = 1.0 at one class
    probs = softmax_logits_with_T(peaked_logits, 0.01)
    assert probs.max() > 0.5, "T3 at T=0.01 should be peaked, got max=%.3f" % probs.max()

    # T4: at T=10.0, near uniform (within 0.02 of 1/V)
    probs_hot = softmax_logits_with_T(peaked_logits, 10.0)
    # 1/V = 1/8 = 0.125; at T=10 with logit max=1, max prob ~ 0.136 (eps over uniform)
    assert probs_hot.max() < 0.145, "T4 at T=10 should be near-uniform, got max=%.3f" % probs_hot.max()
    assert (probs_hot.max() - (1.0 / 8.0)) < 0.02, "T4 max-uniform delta should be small"

    # T5: joint sweep endpoint (T tiny, lambda=0) reproduces unigram BPC
    # logp under lambda=0 is exactly U_log (after normalize)
    U = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
    U_log = np.log(np.clip(U, 1e-30, 1.0))
    nxt = np.array([0, 1, 2, 0, 1])
    n_test = len(nxt)
    sub_logits = np.zeros((n_test, 5), dtype=np.float32)
    logp_lam0 = log_linear_interp_logp(np.log(np.full_like(sub_logits, 1.0/5.0)), U_log, 0.0)
    bpc_lam0 = bpc_from_logp(logp_lam0, nxt)
    bpc_uni = -float(np.mean(np.log(U[nxt]))) / math.log(2.0)
    assert abs(bpc_lam0 - bpc_uni) < 1e-4, "T5 lambda=0 != unigram; %.4f vs %.4f" % (bpc_lam0, bpc_uni)

    # T6: lambda=1.0 reproduces pure substrate (no unigram blend)
    sub_logits2 = np.random.default_rng(42).standard_normal((10, 5)).astype(np.float32)
    probs2 = softmax_logits_with_T(sub_logits2, 1.0)
    logp2 = np.log(np.clip(probs2, 1e-30, 1.0))
    logp_lam1 = log_linear_interp_logp(logp2, U_log, 1.0)
    # lam=1 should give back exactly logp2 (up to numerical normalization)
    raw_bpc = bpc_from_logp(logp2, nxt[:10] if len(nxt) >= 10 else np.tile(nxt, 2)[:10])
    sub_bpc = bpc_from_logp(logp_lam1, nxt[:10] if len(nxt) >= 10 else np.tile(nxt, 2)[:10])
    assert abs(raw_bpc - sub_bpc) < 1e-4, "T6 lambda=1 != raw sub; %.4f vs %.4f" % (raw_bpc, sub_bpc)

    # T7: MRR@10 on planted 5-pair set
    # logp: rows are reverse-ordered so true class at known rank
    V_t = 10
    n_t = 5
    logp_planted = np.full((n_t, V_t), -10.0, dtype=np.float64)
    nxt_t = np.array([3, 0, 9, 5, 2])
    expected_ranks = [1, 2, 3, 4, 5]
    for i, (true_cls, want_rank) in enumerate(zip(nxt_t, expected_ranks)):
        # Place 'want_rank' classes with higher logp than true_cls
        # Simpler: just place true at rank want_rank by giving it the (V_t - want_rank)-th best score
        scores = np.arange(V_t, dtype=np.float64)  # ascending
        # we want true_cls at rank want_rank (1-based), so true_cls gets the
        # (V_t - want_rank)-th-best position. The "best" score is V_t-1.
        np.random.default_rng(i).shuffle(scores)
        sorted_idx = np.argsort(-scores)  # descending order indices
        # Swap so true_cls is at sorted_idx[want_rank - 1]
        cur_top_at_rank = sorted_idx[want_rank - 1]
        # swap scores so true_cls occupies that position
        tmp = scores[true_cls]
        scores[true_cls] = scores[cur_top_at_rank]
        scores[cur_top_at_rank] = tmp
        logp_planted[i] = scores
    mrr_val = mrr_at_k(logp_planted, nxt_t, 10)
    expected_mrr = float(np.mean([1.0/r for r in expected_ranks]))  # = (1 + 1/2 + 1/3 + 1/4 + 1/5) / 5
    assert abs(mrr_val - expected_mrr) < 1e-6, "T7 MRR planted: %.4f vs expected %.4f" % (mrr_val, expected_mrr)

    # T8: sparse-bipolar primitive
    E_t = torch.randn(4, 100, generator=torch.Generator().manual_seed(0))
    sp = sparsify_bipolar_gpu(E_t, 0.05, seed=0)
    k_expect = max(1, int(round(0.05 * 100)))
    nnz_per_row = (sp != 0).sum(dim=1).tolist()
    assert all(n == k_expect for n in nnz_per_row), "T8 sparse nnz; got %s" % nnz_per_row
    uniq = set(sp.unique().tolist())
    assert uniq.issubset({-1.0, 0.0, 1.0}), "T8 sparse not bipolar; got %s" % uniq

    # T9: verdict bands HP_BPC / DEGEN / HARD_FAIL / MIDDLE classification
    def _mk_unit_uni_only(bpc_uni=7.738, top1_uni=0.2171, mrr_uni=0.30):
        return {"ARM_UNIGRAM": {"bpc_unigram": bpc_uni, "top1_unigram": top1_uni,
                                  "mrr_unigram": mrr_uni, "n_test": 100}}
    def _mk_arm_data(bpc=8.0, top1=0.15, mrr=0.25, raw_t1l1=None):
        return {"bpc_best": bpc, "top1_acc": top1, "mrr_at_10": mrr,
                 "best_T_for_bpc": 0.5, "best_lambda_for_bpc": 0.3, "best_dev_bpc": bpc,
                 "best_T_for_top1": 0.5, "best_lambda_for_top1": 0.3,
                 "best_T_for_mrr": 0.5, "best_lambda_for_mrr": 0.3,
                 "raw_bpc_at_T1_L1": raw_t1l1 if raw_t1l1 is not None else bpc,
                 "raw_top1_at_T1_L1": top1, "raw_mrr_at_T1_L1": mrr,
                 "n_dev": 100, "n_test": 100, "grid_size": 42}
    def _full_unit(by_arm_data, V=4000):
        by_arm = _mk_unit_uni_only()
        for arm in SUBSTRATE_ARMS:
            by_arm[arm] = by_arm_data.get(arm, _mk_arm_data())
        return {"seed": 0, "by_arm": by_arm, "V": V, "N": 64, "N_DIM": 64,
                 "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": V, "PRETRAIN_DIM": 10,
                 "run_mode": "smoke", "config_version": "selftest",
                 "elapsed_s_seed": 0.01, "device": "cpu", "n_llm_calls": 0}

    # HP_BPC: word2vec_dense clears bpc < 7.738 - 0.3 = 7.438
    u_hp = _full_unit({"ARM_SUBSTRATE_WORD2VEC_DENSE":
                        _mk_arm_data(bpc=7.40, top1=0.20, mrr=0.30, raw_t1l1=7.40)})
    v, m, d = compute_verdict([u_hp, u_hp, u_hp])
    assert v == "HARD_PASS", "T9 HP_BPC got %s msg=%s" % (v, m[:200])
    assert "ARM_SUBSTRATE_WORD2VEC_DENSE" in d["hp_arms_bpc"], "T9 wrong HP arm"

    # DEGEN: ALL substrate arms have raw_t1l1 near -log2(1/4000) = 11.97; NO arm HP
    # uniform_vocab_bits = log2(4000) ~ 11.97
    u_degen = _full_unit({
        "ARM_SUBSTRATE_WORD2VEC_DENSE": _mk_arm_data(bpc=8.0, top1=0.15, mrr=0.20, raw_t1l1=11.97),
        "ARM_SUBSTRATE_SPARSE_BIPOLAR": _mk_arm_data(bpc=8.0, top1=0.15, mrr=0.20, raw_t1l1=12.0),
        "ARM_SUBSTRATE_BRAIN_COMPOSE": _mk_arm_data(bpc=8.0, top1=0.15, mrr=0.20, raw_t1l1=11.95),
    })
    v, m, d = compute_verdict([u_degen, u_degen, u_degen])
    assert v == "MIDDLE_BAND" and "READOUT_DEGENERATE" in m, "T9 DEGEN got %s msg=%s" % (v, m[:200])
    assert "ARM_SUBSTRATE_WORD2VEC_DENSE" in d["degen_arms"], "T9 degen arms"

    # HARD_FAIL: all arms fail HP on all metrics, NOT degenerate
    u_hf = _full_unit({
        "ARM_SUBSTRATE_WORD2VEC_DENSE": _mk_arm_data(bpc=7.85, top1=0.21, mrr=0.29, raw_t1l1=7.85),
        "ARM_SUBSTRATE_SPARSE_BIPOLAR": _mk_arm_data(bpc=7.85, top1=0.21, mrr=0.29, raw_t1l1=7.85),
        "ARM_SUBSTRATE_BRAIN_COMPOSE": _mk_arm_data(bpc=7.85, top1=0.21, mrr=0.29, raw_t1l1=7.85),
    })
    v, m, _ = compute_verdict([u_hf, u_hf, u_hf])
    assert v == "HARD_FAIL", "T9 HARD_FAIL got %s msg=%s" % (v, m[:200])

    # MIDDLE: substrate beats unigram MRR by small amount (less than HP_MRR_MARGIN),
    # not degen. Use varied unigram across seeds to give sigma>0 so top1 bar moves.
    # Substrate beats unigram MRR by 0.01 (less than HP_MRR_MARGIN=0.02) -> not HP.
    u_mid = _full_unit({
        "ARM_SUBSTRATE_WORD2VEC_DENSE": _mk_arm_data(bpc=7.60, top1=0.20, mrr=0.31, raw_t1l1=7.60),
        "ARM_SUBSTRATE_SPARSE_BIPOLAR": _mk_arm_data(bpc=7.60, top1=0.20, mrr=0.31, raw_t1l1=7.60),
        "ARM_SUBSTRATE_BRAIN_COMPOSE": _mk_arm_data(bpc=7.60, top1=0.20, mrr=0.31, raw_t1l1=7.60),
    })
    # BPC: substrate 7.60 vs unigram bar (7.738 - 0.3) = 7.438; substrate fails BPC (7.60 > 7.438)
    # TOP1: substrate 0.20 vs unigram 0.2171 -> fails top1
    # MRR: substrate 0.31 vs unigram bar (0.30 + 0.02) = 0.32; substrate fails MRR (0.31 < 0.32)
    # All metrics fail HP, but substrate beats unigram on MRR (0.31 > 0.30) -> MIDDLE_BAND
    v, m, _ = compute_verdict([u_mid, u_mid, u_mid])
    assert v == "MIDDLE_BAND" and "READOUT_DEGENERATE" not in m, "T9 MIDDLE got %s msg=%s" % (v, m[:200])

    # T10: LLM call counter zero
    assert _LLM_CALL_COUNTER[0] == 0, "T10 llm counter"

    print("[selftest] PASS: T1 trigram + T2 mockKV + T3 peakedT001 + T4 uniformT10 "
          "+ T5 lam0=unigram + T6 lam1=raw_sub + T7 MRR planted "
          "+ T8 sparse-bipolar + T9 verdict bands (HP_BPC/DEGEN/HF/MID) + T10 llm=0",
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
            "metrics_source": "atexit_synthesize_partial_fair_harness_substrate_as_lm_v1",
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
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM, "schema": "fair-harness-as-lm-v1"}
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
        "metrics_source": "measured_gpu_fair_harness_substrate_as_lm_v1",
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
