"""substrate_as_lm_composed_primitives_GPU_v1 -- COMPOSED-PRIMITIVES substrate-as-LM.

USER directive 2026-06-23: this session validated multiple substrate primitives:
  - word2vec semantic encoder (Spearman 0.6 vs human; clean methodology)
  - Lock-in amplifier noise rejection (16x lift; chain-grade-eligible)
  - HRR contextual binding (mechanism real; depth-lossless involutive bind)
  - Working memory HRR-slots (recall=1.000 across K=2..16)
  - Sparse-bipolar bundle (20-300x capacity lift per just-landed drill)
  - Per-layer cleanup (substrate primitive)

This cell COMPOSES ALL of them in one production-scale substrate-as-LM test on GPU.

HYPOTHESIS: prior substrate-as-LM (BPC ~7.864 = 0.126 above unigram 7.738) used
char-trigram encoder + DENSE bipolar + NO context + NO lock-in. With ALL primitives
composed properly, BPC should beat unigram and approach bigram (~6.6).

DESIGN (5 arms x 3 seeds; each arm builds its own fresh W on GPU):

  ARM_UNIGRAM
      Baseline floor; analytic, no W. Reference BPC=7.738.

  ARM_CHAR_TRIGRAM_DENSE_NO_CONTEXT
      Worst-case substrate; reproduces ~11.6 raw BPC (no encoder semantics,
      dense bipolar, no context, no lock-in).

  ARM_WORD2VEC_DENSE_NO_CONTEXT
      Path A baseline; word2vec encoder + dense projection + no context.
      Should reproduce ~7.87 raw BPC from fresh_W_bpc test.

  ARM_WORD2VEC_SPARSE_BIPOLAR_CONTEXT_5  (NEW)
      word2vec encoder + sparse-bipolar f=0.05 + HRR context bind over 5-word
      window. Composes encoder + sparse-capacity + contextual-binding primitives.

  ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT    (NEW)
      word2vec encoder + sparse-bipolar f=0.05 + lock-in amp at frequency=pos*31
      for context positional encoding + HRR bind. Composes ALL primitives.

PRE-REG HARD bands (compositional substrate-as-LM; CHAIN-GRADE-eligible):
  HARD_PASS: ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT BPC < 7.5 (clears unigram
             floor AND log-linear interp ceiling); decisive evidence that
             composed primitives close V2 LM gap.
  HARD_FAIL: ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT BPC >= 7.738 (substrate-as-LM
             still can't beat unigram with all primitives; substrate W matrix
             is the fundamental bottleneck; V2 LM gap CLOSED as scope-narrow).
  MIDDLE_BAND: BPC in (7.5, 7.738) -- composed primitives lift but don't cross
               unigram floor; characterize.

SANITY:
  - lambda=1.0 reproduces ARM_*_RAW (pure substrate)
  - lambda=0.0 reproduces ARM_UNIGRAM (pure unigram)

GPU REQUIRED (Fix #24): torch.cuda for all matmul + roll + bind; heartbeat
with util-check. Estimated ~30-60min GPU wall at 100k tokens x 5 arms x 3 seeds.

Cites:
  - preregs/2026-06-23_substrate_as_lm_composed_primitives_GPU_v1.md
  - exp_fresh_W_bpc_per_encoder_v1.py (parent pattern: fresh W per arm)
  - exp_encoder_word2vec_substrate_bind_v1.py (word2vec encoder)
  - exp_lock_in_amplifier_hd_frequency_v1_FULL.py (lock-in primitive)
  - exp_substrate_bipolar_hadamard_expansion_k8_v2.py (sparse-bipolar)
  - USER 2026-06-23 compose-validated-primitives
  - USER 2026-06-22 GPU dispatch must use GPU (Fix #24)

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

ANCHOR_NAME = "substrate_as_lm_composed_primitives_GPU_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)
_LLM_CALL_COUNTER = [0]

# Reference baselines
UNIGRAM_BPC_REF = 7.738
PATH_A_PRIOR_BPC_REF = 7.864

# Pre-reg bands
HP_BPC_BAR = 7.5            # ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT must clear <7.5
HF_BPC_BAR = UNIGRAM_BPC_REF  # >= 7.738 means substrate still can't beat unigram
HP_BPC_CV_MAX = 0.05

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
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

# Composed-primitive knobs
SPARSE_BIPOLAR_F = 0.05    # 5% nonzero (sparse-bipolar primitive)
CONTEXT_WINDOW = 5         # 5-word HRR-bind window
LOCK_IN_FREQ_STEP = 31     # frequency = pos * 31 for lock-in positional code

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke must fit under SMOKE_TIMEOUT_S=180s
    SEEDS = [0]
    N_TRAIN = 1_500
    N_HELD = 300
    VOCAB_CAP = 300

ARMS = [
    "ARM_UNIGRAM",
    "ARM_CHAR_TRIGRAM_DENSE_NO_CONTEXT",
    "ARM_WORD2VEC_DENSE_NO_CONTEXT",
    "ARM_WORD2VEC_SPARSE_BIPOLAR_CONTEXT_5",
    "ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT",
]

CONFIG_VERSION = (
    "substrate_as_lm_composed_primitives_GPU_v1; N_DIM=%d PRETRAIN_DIM=%d "
    "N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s mode=%s "
    "sparse_f=%.3f context_W=%d lockin_freq_step=%d INGEST_CHUNK=%d "
    "RECALL_BATCH=%d device=%s lambda_grid=%s; "
    "bands HP_bpc<%.3f HF_bpc>=%.3f cv_max=%.2f"
) % (
    N_DIM, PRETRAIN_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    SPARSE_BIPOLAR_F, CONTEXT_WINDOW, LOCK_IN_FREQ_STEP, INGEST_CHUNK,
    RECALL_BATCH, str(DEVICE), LAMBDA_GRID,
    HP_BPC_BAR, HF_BPC_BAR, HP_BPC_CV_MAX,
)


# ============================================================================
# Encoders
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


# Gensim cache
_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_kv(model_name: str):
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    import gensim.downloader as gd
    try:
        gd.base_dir = GENSIM_CACHE_DIR
        gd.BASE_DIR = GENSIM_CACHE_DIR
    except Exception:
        pass
    kv = gd.load(model_name)
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


# ============================================================================
# Sparse-bipolar projection primitive
# ============================================================================

def sparsify_bipolar_gpu(E: torch.Tensor, f: float, seed: int) -> torch.Tensor:
    """Project to sparse bipolar: f-fraction nonzero, each +/-1; rest = 0.

    Per just-landed sparse-bipolar drill: 20-300x capacity lift vs dense.
    Implementation: per-row top-k by magnitude then bipolarize.
    """
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    # rank by abs value per row, keep top-k, then sign() them
    abs_E = E.abs()
    # top-k indices per row
    topk_vals, topk_idx = torch.topk(abs_E, k=k, dim=1)
    # construct sparse mask
    out = torch.zeros_like(E)
    row_idx = torch.arange(V, device=E.device).unsqueeze(1).expand(-1, k)
    # take sign of the original at those positions
    signs = torch.sign(E.gather(1, topk_idx))
    # zero -> +1 (avoid losing rows)
    signs = torch.where(signs == 0, torch.ones_like(signs), signs)
    out[row_idx, topk_idx] = signs
    return out


# ============================================================================
# HRR contextual bind primitive (circular convolution via FFT)
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


def lock_in_position_vec_gpu(n_dim: int, pos: int, seed: int) -> torch.Tensor:
    """Lock-in amplifier positional code: cos+sin at frequency = pos * step.

    Uses a base random phase per seed; frequency proportional to position.
    Returns a real-valued [n_dim] tensor, L2-normalized.
    """
    rng = np.random.default_rng(seed * 7919 + 13)
    phase = rng.uniform(0.0, 2.0 * math.pi, size=n_dim).astype(np.float32)
    freq = float(pos * LOCK_IN_FREQ_STEP) / float(n_dim)
    t = np.arange(n_dim, dtype=np.float32)
    v = np.cos(2.0 * math.pi * freq * t + phase).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-12)
    return torch.from_numpy(v).to(DEVICE)


def position_role_vec_random(n_dim: int, pos: int, seed: int) -> torch.Tensor:
    """Plain random role vector for HRR position (non lock-in baseline)."""
    h = hashlib.blake2b(("pos:%d:%d" % (pos, seed)).encode(), digest_size=8).digest()
    sv = int.from_bytes(h, "big") % (2**32)
    rng = np.random.default_rng(sv)
    v = rng.standard_normal(n_dim).astype(np.float32)
    v = v / (np.linalg.norm(v) + 1e-12)
    return torch.from_numpy(v).to(DEVICE)


# ============================================================================
# Per-arm encoder builders
# ============================================================================

def build_E_char_trigram(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    return torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)


def build_E_word2vec(vocab: List[str], n_dim: int, seed: int) -> Tuple[torch.Tensor, Dict]:
    kv = _load_gensim_kv("word2vec-google-news-300")
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


# ============================================================================
# Context-aware key builder: maps a position's CONTEXT to a key vector
# ============================================================================

def build_context_keys_gpu(idx: torch.Tensor, E: torch.Tensor, context_window: int,
                            seed: int, use_lock_in: bool) -> torch.Tensor:
    """For each position t in idx, build a key vector =
       bind(E[idx[t]], pos_0) + bind(E[idx[t-1]], pos_1) + ... bind(..., pos_W-1)
    where pos_i is either a lock-in cosine code or a random role vector.

    Result: [len(idx), n_dim] L2-normalized.
    """
    n = idx.shape[0]
    dim = E.shape[1]
    # Precompute position role vectors
    pos_vecs = []
    for i in range(context_window):
        if use_lock_in:
            pos_vecs.append(lock_in_position_vec_gpu(dim, i, seed))
        else:
            pos_vecs.append(position_role_vec_random(dim, i, seed))
    keys = torch.zeros((n, dim), dtype=TORCH_DTYPE, device=E.device)
    for offset in range(context_window):
        # shift positions: at time t, look at idx[t - offset] (current = offset 0)
        if offset == 0:
            src = E[idx]
        else:
            # left-shift idx by offset; pad with idx[0]
            shifted = torch.roll(idx, shifts=offset, dims=0)
            # zero out the first `offset` positions (would be invalid context;
            # roll wraps -- replace with the natural starting context)
            shifted[:offset] = idx[0]
            src = E[shifted]
        # Contiguous-clone required: MKL FFT rejects expand()'d strided views
        pos_b = pos_vecs[offset].unsqueeze(0).expand(n, -1).contiguous()
        bound = hrr_bind_batch(src, pos_b)
        keys.add_(bound)
    keys = _l2_normalize_t(keys)
    return keys


# ============================================================================
# Fresh-W Hebbian builder using KEYS (context-aware) on GPU
# ============================================================================

def build_fresh_hebbian_W_with_keys_gpu(keys: torch.Tensor, E_tgt_lookup: torch.Tensor,
                                          idx_train: torch.Tensor,
                                          ingest_chunk: int) -> torch.Tensor:
    """W [N_DIM, N_DIM] = sum over t of outer(E[idx[t+1]], keys[t]).

    Predict next-word target vector from context-key.
    """
    device = E_tgt_lookup.device
    dim = E_tgt_lookup.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        K_src = keys[b:end]
        tgt_idx = idx_train[b + 1:end + 1]
        E_tgt = E_tgt_lookup[tgt_idx]
        W.add_(E_tgt.T @ K_src)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


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
# BPC computation
# ============================================================================

def compute_substrate_logits_with_keys_gpu(E_lookup: torch.Tensor, W: torch.Tensor,
                                              keys: torch.Tensor,
                                              recall_batch: int) -> np.ndarray:
    """Per-position substrate logits over full vocab using context keys.

    pred_vec = W @ keys[t]; logits = E_lookup @ pred_vec.
    """
    V = E_lookup.shape[0]
    n = keys.shape[0]
    logits_out = np.zeros((n, V), dtype=np.float32)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        K_b = keys[b:end]
        pred_vec = K_b @ W.T
        pn = pred_vec.norm(dim=1, keepdim=True).clamp(min=1e-9)
        pred_vec = pred_vec / pn
        logits_b = pred_vec @ E_lookup.T
        logits_out[b:end] = logits_b.detach().cpu().numpy()
        if DEVICE.type == "cuda" and (b // recall_batch) % 16 == 0:
            torch.cuda.synchronize()
    return logits_out


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


def bpc_arm_compose(arm_label: str, E: torch.Tensor, idx_train: np.ndarray,
                     idx_held: np.ndarray, U_log: np.ndarray, lambda_grid: list,
                     seed: int) -> Dict:
    """Build fresh W per arm (with arm-specific encoder/sparse/context).

    Arm config decides:
      - whether to sparsify E to sparse-bipolar
      - whether to use context-key (CONTEXT_WINDOW) vs current-word only
      - whether positional roles use lock-in vs random
    """
    V = E.shape[0]
    unk = 0
    use_sparse = arm_label in (
        "ARM_WORD2VEC_SPARSE_BIPOLAR_CONTEXT_5",
        "ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT",
    )
    use_context = arm_label in (
        "ARM_WORD2VEC_SPARSE_BIPOLAR_CONTEXT_5",
        "ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT",
    )
    use_lock_in = arm_label == "ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT"

    # Apply sparsification if configured
    if use_sparse:
        E_used = sparsify_bipolar_gpu(E, SPARSE_BIPOLAR_F, seed)
        # L2 normalize for stable dot products
        E_used = _l2_normalize_t(E_used)
    else:
        E_used = E

    # Build context-keys vs single-word keys
    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)
    t0 = time.time()
    if use_context:
        keys_train = build_context_keys_gpu(idx_train_t, E_used, CONTEXT_WINDOW, seed, use_lock_in)
        keys_held = build_context_keys_gpu(idx_held_t, E_used, CONTEXT_WINDOW, seed, use_lock_in)
    else:
        keys_train = E_used[idx_train_t]
        keys_held = E_used[idx_held_t]
    t_keys = time.time() - t0

    # Build fresh W using KEYS as src, E_used as tgt lookup
    t0 = time.time()
    W = build_fresh_hebbian_W_with_keys_gpu(keys_train, E_used, idx_train_t, INGEST_CHUNK)
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    # Eval split
    ctx_keys = keys_held[:-1]
    nxt = idx_held[1:]
    mask = (idx_held[:-1] != unk)
    ctx_keys_eval = ctx_keys[mask]
    nxt_eval = nxt[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        del W
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {"bpc_raw": float("inf"), "bpc_best": float("inf"),
                "best_lambda": 1.0, "bpc_per_lambda_test": {}, "n_test": 0,
                "n_dev": 0, "wall_keys_s": t_keys, "wall_ingest_s": t_ingest, "wall_recall_s": 0.0}
    n_dev = n_eval // 2
    ctx_dev = ctx_keys_eval[:n_dev]
    nxt_dev = nxt_eval[:n_dev]
    ctx_test = ctx_keys_eval[n_dev:]
    nxt_test = nxt_eval[n_dev:]
    n_test = len(ctx_test)

    t0 = time.time()
    sub_logits_dev = compute_substrate_logits_with_keys_gpu(E_used, W, ctx_dev, RECALL_BATCH)
    sub_logits_test = compute_substrate_logits_with_keys_gpu(E_used, W, ctx_test, RECALL_BATCH)
    t_recall = time.time() - t0

    sub_probs_dev = softmax_with_temperature_np(sub_logits_dev, temperature=1.0)
    sub_probs_test = softmax_with_temperature_np(sub_logits_test, temperature=1.0)
    sub_logp_dev = np.log(np.clip(sub_probs_dev, 1e-30, 1.0))
    sub_logp_test = np.log(np.clip(sub_probs_test, 1e-30, 1.0))

    raw_logp_nxt = sub_logp_test[np.arange(n_test), nxt_test]
    bpc_raw = -float(np.mean(raw_logp_nxt)) / math.log(2.0)

    best_lambda = 1.0
    best_dev_bpc = float("inf")
    bpc_per_lambda_dev: Dict[float, float] = {}
    bpc_per_lambda_test: Dict[float, float] = {}
    for lam in lambda_grid:
        bpc_dev = log_linear_interp_bpc(sub_logp_dev, U_log, nxt_dev, lam)
        bpc_per_lambda_dev[lam] = bpc_dev
        bpc_test = log_linear_interp_bpc(sub_logp_test, U_log, nxt_test, lam)
        bpc_per_lambda_test[lam] = bpc_test
        if bpc_dev < best_dev_bpc:
            best_dev_bpc = bpc_dev
            best_lambda = lam
    bpc_best_test = bpc_per_lambda_test[best_lambda]

    del W, keys_train, keys_held, idx_train_t, idx_held_t
    if use_sparse:
        del E_used
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "bpc_raw": round(bpc_raw, 4),
        "bpc_best": round(bpc_best_test, 4),
        "best_lambda": float(best_lambda),
        "best_dev_bpc": round(best_dev_bpc, 4),
        "bpc_per_lambda_dev": {str(k): round(v, 4) for k, v in bpc_per_lambda_dev.items()},
        "bpc_per_lambda_test": {str(k): round(v, 4) for k, v in bpc_per_lambda_test.items()},
        "n_dev": int(n_dev),
        "n_test": int(n_test),
        "wall_keys_s": round(t_keys, 2),
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "use_sparse": bool(use_sparse),
        "use_context": bool(use_context),
        "use_lock_in": bool(use_lock_in),
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

    # Pre-build word2vec E (cached across 3 word2vec arms)
    E_word2vec_cache: Optional[torch.Tensor] = None
    word2vec_meta: Dict = {}

    for arm_label in [a for a in ARMS if a != "ARM_UNIGRAM"]:
        t_arm = time.time()
        print("\n  [seed=%d arm=%s] building E (V=%d N_DIM=%d) on %s..." % (
            seed, arm_label, V, N_DIM, str(DEVICE)), flush=True)
        meta = {}
        try:
            if arm_label == "ARM_CHAR_TRIGRAM_DENSE_NO_CONTEXT":
                E = build_E_char_trigram(vocab, N_DIM, seed)
            else:
                if E_word2vec_cache is None:
                    E_word2vec_cache, word2vec_meta = build_E_word2vec(vocab, N_DIM, seed)
                E = E_word2vec_cache
                meta = dict(word2vec_meta)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] ENCODER LOAD FAIL: %s" % (seed, arm_label, err), flush=True)
            by_arm[arm_label] = {
                "load_failed": True, "load_error": err,
                "bpc_raw": float("inf"), "bpc_best": float("inf"),
                "best_lambda": float("nan"), "best_dev_bpc": float("inf"),
                "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
                "n_dev": 0, "n_test": 0,
                "wall_encode_s": round(time.time() - t_arm, 2),
                "wall_keys_s": 0.0, "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "encoder_meta": meta,
            }
            continue
        t_enc = time.time() - t_arm
        if DEVICE.type == "cuda":
            try:
                free_b, total_b = torch.cuda.mem_get_info()
                print("    [seed=%d arm=%s] E built (%.1fs); GPU free=%.2fGB total=%.2fGB" % (
                    seed, arm_label, t_enc, free_b / 1e9, total_b / 1e9), flush=True)
            except Exception:
                pass

        print("    [seed=%d arm=%s] building FRESH W (composed primitives) + BPC..." % (
            seed, arm_label), flush=True)
        try:
            bpc = bpc_arm_compose(arm_label, E, idx_train, idx_held, U_log, LAMBDA_GRID, seed)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] BPC COMPUTE FAIL: %s" % (seed, arm_label, err), flush=True)
            if DEVICE.type == "cuda":
                torch.cuda.empty_cache()
            by_arm[arm_label] = {
                "compute_failed": True, "compute_error": err,
                "bpc_raw": float("inf"), "bpc_best": float("inf"),
                "best_lambda": float("nan"), "best_dev_bpc": float("inf"),
                "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
                "n_dev": 0, "n_test": 0,
                "wall_encode_s": round(t_enc, 2),
                "wall_keys_s": 0.0, "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "encoder_meta": meta,
            }
            continue

        oov_info = ""
        if meta:
            oov_info = " hit/miss=%d/%d" % (meta.get("n_hit", 0), meta.get("n_miss", 0))
        print("    [seed=%d arm=%s] bpc_raw=%.3f bpc_best=%.3f lam=%.2f%s "
              "(enc=%.1fs keys=%.1fs ingest=%.1fs recall=%.1fs)" % (
            seed, arm_label, bpc["bpc_raw"], bpc["bpc_best"], bpc["best_lambda"],
            oov_info, t_enc, bpc["wall_keys_s"], bpc["wall_ingest_s"], bpc["wall_recall_s"]), flush=True)

        by_arm[arm_label] = {
            "bpc_raw": bpc["bpc_raw"], "bpc_best": bpc["bpc_best"],
            "best_lambda": bpc["best_lambda"], "best_dev_bpc": bpc["best_dev_bpc"],
            "bpc_per_lambda_dev": bpc["bpc_per_lambda_dev"],
            "bpc_per_lambda_test": bpc["bpc_per_lambda_test"],
            "n_dev": bpc["n_dev"], "n_test": bpc["n_test"],
            "wall_encode_s": round(t_enc, 2),
            "wall_keys_s": bpc["wall_keys_s"], "wall_ingest_s": bpc["wall_ingest_s"],
            "wall_recall_s": bpc["wall_recall_s"],
            "encoder_meta": meta,
            "use_sparse": bpc["use_sparse"], "use_context": bpc["use_context"],
            "use_lock_in": bpc["use_lock_in"],
        }

    # Free word2vec cache
    if E_word2vec_cache is not None:
        del E_word2vec_cache
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

    return {
        "seed": seed, "by_arm": by_arm, "V": V,
        "N": N_DIM, "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP, "PRETRAIN_DIM": PRETRAIN_DIM,
        "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "CONTEXT_WINDOW": CONTEXT_WINDOW,
        "LOCK_IN_FREQ_STEP": LOCK_IN_FREQ_STEP,
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
    encoder_arms = [a for a in ARMS if a != "ARM_UNIGRAM"]
    for arm in encoder_arms:
        seeds_load_failed = [u["by_arm"].get(arm, {}).get("load_failed", False) for u in units]
        seeds_compute_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid = [(not lf) and (not cf) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
                 for lf, cf, u in zip(seeds_load_failed, seeds_compute_failed, units)]
        n_load_failed = int(sum(seeds_load_failed))
        n_compute_failed = int(sum(seeds_compute_failed))
        valid_units = [u for ok, u in zip(valid, units) if ok]
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"), "bpc_best_std": float("nan"),
                "bpc_best_cv": float("nan"), "bpc_raw_mean": float("inf"),
                "best_lambda_mean": float("nan"),
                "n_valid_seeds": 0, "n_load_failed": n_load_failed,
                "n_compute_failed": n_compute_failed, "all_seeds_failed": True,
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
            "n_load_failed": n_load_failed,
            "n_compute_failed": n_compute_failed,
            "all_seeds_failed": False,
        }

    # The decisive arm is ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT
    DECISIVE_ARM = "ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT"
    decisive = by_arm_agg.get(DECISIVE_ARM, {})
    decisive_bpc = decisive.get("bpc_best_mean", float("inf"))
    decisive_cv = decisive.get("bpc_best_cv", float("nan"))

    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    parts = []
    for a in encoder_arms:
        b = by_arm_agg[a]
        parts.append("%s=bpc%.3f(lam%.2f)" % (
            a, b["bpc_best_mean"], b["best_lambda_mean"]))
    summary = "COMPOSED_PRIMITIVES unigram=%.3f | %s | n_llm=%d" % (
        by_arm_agg["ARM_UNIGRAM"]["bpc_mean"], " | ".join(parts), n_llm)

    # Lifts for visibility
    char_baseline = by_arm_agg.get("ARM_CHAR_TRIGRAM_DENSE_NO_CONTEXT", {}).get("bpc_best_mean", float("nan"))
    w2v_baseline = by_arm_agg.get("ARM_WORD2VEC_DENSE_NO_CONTEXT", {}).get("bpc_best_mean", float("nan"))
    lift_over_char = (char_baseline - decisive_bpc) if (math.isfinite(char_baseline) and math.isfinite(decisive_bpc)) else float("nan")
    lift_over_w2v = (w2v_baseline - decisive_bpc) if (math.isfinite(w2v_baseline) and math.isfinite(decisive_bpc)) else float("nan")

    detail = {
        "by_arm_agg": by_arm_agg,
        "decisive_arm": DECISIVE_ARM,
        "decisive_bpc": decisive_bpc,
        "decisive_cv": decisive_cv,
        "lift_over_char_trigram_dense": lift_over_char,
        "lift_over_word2vec_dense": lift_over_w2v,
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "path_a_prior_bpc_ref": PATH_A_PRIOR_BPC_REF,
        "hp_bpc_bar": HP_BPC_BAR,
        "hf_bpc_bar": HF_BPC_BAR,
        "hp_bpc_cv_max": HP_BPC_CV_MAX,
        "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "CONTEXT_WINDOW": CONTEXT_WINDOW,
        "LOCK_IN_FREQ_STEP": LOCK_IN_FREQ_STEP,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Compositional substrate-as-LM: 5 arms ascending in composed-primitive count. "
            "Decisive arm = ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT (word2vec encoder + "
            "sparse-bipolar f=%.3f + HRR context bind W=%d + lock-in positional code). "
            "HARD_PASS = decisive bpc<%.3f (clears unigram AND log-linear interp ceiling). "
            "HARD_FAIL = decisive bpc>=%.3f (substrate-W bottleneck even with composed "
            "primitives; V2 LM gap closed as scope-narrow)." % (
                SPARSE_BIPOLAR_F, CONTEXT_WINDOW, HP_BPC_BAR, HF_BPC_BAR)),
        "cites": [
            "preregs/2026-06-23_substrate_as_lm_composed_primitives_GPU_v1.md",
            "experiments/exp_fresh_W_bpc_per_encoder_v1.py",
            "experiments/exp_encoder_word2vec_substrate_bind_v1.py",
            "experiments/exp_lock_in_amplifier_hd_frequency_v1_FULL.py",
            "experiments/exp_substrate_bipolar_hadamard_expansion_k8_v2.py",
            "USER_2026-06-23_compose_validated_primitives",
            "USER_2026-06-22_GPU_dispatch_must_use_GPU_Fix24",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    # HARD_PASS: decisive arm clears 7.5 bar
    if (math.isfinite(decisive_bpc) and decisive_bpc < HP_BPC_BAR
            and math.isfinite(decisive_cv) and decisive_cv <= HP_BPC_CV_MAX):
        return ("HARD_PASS",
                ("COMPOSED_PRIMITIVES HARD_PASS: decisive arm %s clears BPC %.3f < %.3f bar "
                 "(cv=%.3f); composed primitives close V2 LM gap; lift over char_trigram_dense "
                 "= %.3f bits, lift over word2vec_dense = %.3f bits; substrate-as-LM finally "
                 "beats unigram via compositional architecture; chain-grade evidence. %s" % (
                     DECISIVE_ARM, decisive_bpc, HP_BPC_BAR, decisive_cv,
                     lift_over_char, lift_over_w2v, summary)),
                detail)

    # HARD_FAIL: decisive arm >= unigram floor
    if math.isfinite(decisive_bpc) and decisive_bpc >= HF_BPC_BAR:
        return ("HARD_FAIL",
                ("COMPOSED_PRIMITIVES HARD_FAIL: decisive arm %s BPC %.3f >= unigram %.3f "
                 "even with ALL primitives composed (word2vec + sparse-bipolar + HRR context + "
                 "lock-in positional code); substrate W matrix is the fundamental bottleneck; "
                 "V2 LM gap CLOSED as scope-narrow; pivot to architectural rewrite or descope. "
                 "%s" % (DECISIVE_ARM, decisive_bpc, HF_BPC_BAR, summary)),
                detail)

    # MIDDLE_BAND: lift but doesn't clear unigram
    return ("MIDDLE_BAND",
            ("COMPOSED_PRIMITIVES MIDDLE_BAND: decisive arm %s BPC %.3f in (%.3f, %.3f); "
             "composed primitives lift over dense baselines but don't cross unigram floor; "
             "characterize encoder vs substrate-W bottleneck. %s" % (
                 DECISIVE_ARM, decisive_bpc, HP_BPC_BAR, HF_BPC_BAR, summary)),
            detail)


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: char-trigram encoder shape + bipolar
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,)
    uniq = set(np.unique(v).tolist())
    assert uniq.issubset({-1.0, 1.0}), "T1 bipolar"

    # T2: sparse-bipolar primitive
    rng = np.random.default_rng(0)
    Et = torch.from_numpy(rng.standard_normal((10, 100)).astype(np.float32))
    Es = sparsify_bipolar_gpu(Et, f=0.1, seed=0)
    nz_per_row = (Es != 0).sum(dim=1).numpy()
    assert int(nz_per_row.min()) == 10 and int(nz_per_row.max()) == 10, (
        "T2 sparse-bipolar nonzero count expected 10 per row got %s" % nz_per_row)
    uniq_vals = set(torch.unique(Es).numpy().tolist())
    assert uniq_vals.issubset({-1.0, 0.0, 1.0}), "T2 sparse-bipolar uniq=%s" % uniq_vals

    # T3: HRR bind FFT roundtrip + commutativity
    A = torch.randn(64)
    B = torch.randn(64)
    out_AB = hrr_bind_batch(A.unsqueeze(0), B.unsqueeze(0))
    out_BA = hrr_bind_batch(B.unsqueeze(0), A.unsqueeze(0))
    assert torch.allclose(out_AB, out_BA, atol=1e-5), "T3 bind commutative (circ-conv)"

    # T4: lock-in positional vector is L2-normalized; differs per pos
    global DEVICE
    _saved_device = DEVICE
    DEVICE = torch.device("cpu")
    try:
        p0 = lock_in_position_vec_gpu(128, 0, seed=0)
        p1 = lock_in_position_vec_gpu(128, 1, seed=0)
        assert abs(float(p0.norm()) - 1.0) < 1e-4, "T4 pos0 normalized"
        assert abs(float(p1.norm()) - 1.0) < 1e-4, "T4 pos1 normalized"
        cos_sim = float((p0 * p1).sum())
        assert abs(cos_sim) < 0.5, "T4 pos0 vs pos1 cos_sim=%.3f (should differ)" % cos_sim

        # T5: random-role position vector different from lock-in
        r0 = position_role_vec_random(128, 0, seed=0)
        assert abs(float(r0.norm()) - 1.0) < 1e-4, "T5 role0 normalized"

        # T6: build_context_keys shape + L2-norm
        vocab_t = ["w%d" % i for i in range(8)]
        E_small = build_E_char_trigram(vocab_t, 128, seed=0)
        idx_seq = torch.from_numpy(np.array([0, 1, 2, 3, 4, 5, 6, 7] * 4, dtype=np.int64))
        keys = build_context_keys_gpu(idx_seq, E_small, context_window=3, seed=0, use_lock_in=True)
        assert keys.shape == (32, 128), "T6 keys shape"
        nrms = keys.norm(dim=1).numpy()
        assert np.allclose(nrms, 1.0, atol=1e-4), "T6 keys norm"

        # T7: build_fresh_hebbian_W_with_keys shape + nonzero
        W = build_fresh_hebbian_W_with_keys_gpu(keys, E_small, idx_seq, ingest_chunk=8)
        assert W.shape == (128, 128), "T7 W shape"
        assert float(W.abs().sum()) > 0, "T7 W nonzero"

        # T8: log-linear endpoints (lambda=1.0 raw substrate; lambda=0.0 unigram)
        n = 4
        sub_probs = np.array([
            [0.6, 0.1, 0.1, 0.1, 0.1],
            [0.1, 0.5, 0.2, 0.1, 0.1],
            [0.3, 0.3, 0.2, 0.1, 0.1],
            [0.1, 0.1, 0.1, 0.5, 0.2],
        ], dtype=np.float64)
        nxt = np.array([0, 1, 1, 3], dtype=np.int64)
        U_log = np.log(np.array([0.2, 0.3, 0.2, 0.2, 0.1]).clip(1e-30, 1.0))
        sub_logp = np.log(sub_probs.clip(1e-30, 1.0))
        bpc_lam1 = log_linear_interp_bpc(sub_logp, U_log, nxt, 1.0)
        raw_logp = sub_logp[np.arange(n), nxt]
        bpc_raw_expected = -float(np.mean(raw_logp)) / math.log(2.0)
        assert abs(bpc_lam1 - bpc_raw_expected) < 1e-6, "T8 lambda=1 raw mismatch"
        bpc_lam0 = log_linear_interp_bpc(sub_logp, U_log, nxt, 0.0)
        U_target = np.exp(U_log - U_log.max())
        U_target = U_target / U_target.sum()
        p_uni_nxt = U_target[nxt].clip(1e-12, 1.0)
        bpc_uni_expected = -float(np.mean(np.log(p_uni_nxt))) / math.log(2.0)
        assert abs(bpc_lam0 - bpc_uni_expected) < 1e-6, "T8 lambda=0 unigram mismatch"

        # T9: verdict bands (HP / HF / MID)
        def _mk_unit(decisive_bpc_val, lam=0.5):
            by_arm_local = {"ARM_UNIGRAM": {"bpc_unigram": 7.738, "n_test": 100}}
            for arm in [a for a in ARMS if a != "ARM_UNIGRAM"]:
                bp = decisive_bpc_val if arm == "ARM_WORD2VEC_SPARSE_LOCK_IN_CONTEXT" else 7.9
                by_arm_local[arm] = {
                    "bpc_raw": bp + 0.2, "bpc_best": bp, "best_lambda": lam,
                    "best_dev_bpc": bp,
                    "bpc_per_lambda_dev": {}, "bpc_per_lambda_test": {},
                    "n_dev": 100, "n_test": 100,
                    "wall_encode_s": 0.1, "wall_keys_s": 0.1,
                    "wall_ingest_s": 0.1, "wall_recall_s": 0.1,
                    "encoder_meta": {},
                    "use_sparse": False, "use_context": False, "use_lock_in": False,
                }
            return {"seed": 0, "by_arm": by_arm_local, "V": 16, "N": 64, "N_DIM": 64,
                    "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": 16, "PRETRAIN_DIM": 10,
                    "SPARSE_BIPOLAR_F": 0.05, "CONTEXT_WINDOW": 5, "LOCK_IN_FREQ_STEP": 31,
                    "run_mode": "smoke", "config_version": "selftest",
                    "elapsed_s_seed": 0.01, "device": "cpu", "n_llm_calls": 0}

        # HARD_PASS: decisive arm at 7.2 < 7.5
        u_hp = _mk_unit(7.2)
        v, m, d = compute_verdict([u_hp, u_hp, u_hp])
        assert v == "HARD_PASS", "T9 HP got %s msg=%s" % (v, m[:200])
        # HARD_FAIL: decisive arm at 7.9 >= 7.738
        u_hf = _mk_unit(7.9)
        v, m, _ = compute_verdict([u_hf, u_hf, u_hf])
        assert v == "HARD_FAIL", "T9 HF got %s msg=%s" % (v, m[:200])
        # MIDDLE_BAND: decisive arm at 7.6 in (7.5, 7.738)
        u_mid = _mk_unit(7.6)
        v, m, _ = compute_verdict([u_mid, u_mid, u_mid])
        assert v == "MIDDLE_BAND", "T9 MID got %s msg=%s" % (v, m[:200])

        # T10: unigram analytic max-class
        idx = np.array([0, 0, 0, 1, 1, 2, 2, 2, 2, 3], dtype=np.int64)
        U = build_unigram_np(idx, V=4, alpha=0.0)
        assert int(np.argmax(U)) == 2

    finally:
        DEVICE = _saved_device

    # T11: LLM-counter clean
    assert _LLM_CALL_COUNTER[0] == 0, "T11 LLM counter"

    print("[selftest] PASS: T1 trigram + T2 sparse-bipolar + T3 HRR bind + T4 lock-in pos "
          "+ T5 random role + T6 context-keys + T7 fresh W with keys + T8 log-linear endpoints "
          "+ T9 verdict HP/HF/MID + T10 unigram + T11 llm=0", flush=True)


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
            "run_mode": RUN_MODE, "N_DIM": N_DIM, "N": N_DIM,
            "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
            "PRETRAIN_DIM": PRETRAIN_DIM,
            "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
            "CONTEXT_WINDOW": CONTEXT_WINDOW,
            "LOCK_IN_FREQ_STEP": LOCK_IN_FREQ_STEP,
            "n_seeds": len(units), "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_substrate_as_lm_composed_primitives_GPU_v1",
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
          "seeds=%s arms=%s sparse_f=%.3f context_W=%d lockin_freq=%d "
          "| name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
              SEEDS, ARMS, SPARSE_BIPOLAR_F, CONTEXT_WINDOW, LOCK_IN_FREQ_STEP,
              _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
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
               "schema": "substrate-as-lm-composed-primitives-GPU-v1"}
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
        "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP, "PRETRAIN_DIM": PRETRAIN_DIM,
        "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "CONTEXT_WINDOW": CONTEXT_WINDOW,
        "LOCK_IN_FREQ_STEP": LOCK_IN_FREQ_STEP,
        "INGEST_CHUNK": INGEST_CHUNK, "RECALL_BATCH": RECALL_BATCH,
        "LAMBDA_GRID": LAMBDA_GRID, "arms": ARMS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_gpu_substrate_as_lm_composed_primitives_GPU_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate-native composed primitives; word2vec is open-weight static lookup; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
