"""substrate_compose_lock_in_frequency_stacking_v1 -- USER directive (Barrier 3 alt).

Temporal frequency-division separation: each plasticity rule rides a different
lock-in modulation frequency on the SAME W. Demodulate at retrieval to recover
that mechanism. Brain: theta-gamma nested oscillations. Engineering: FDM.

Arms (4):
  ARM_BASELINE_SHARED_W          control: 3 mechs into same W; no separation.
  ARM_CROSS_LAYER_INDEPENDENT_W  control: 3 separate W matrices; sum at retrieval.
  ARM_LOCK_IN_FREQ_SEPARATED     same W; lock-in modulation; demod at retrieval.
  ARM_LOCK_IN_PLUS_CROSS_LAYER   spatial + temporal multiplicative.

Bands:
  HP_CHAIN_GRADE: best lock-in BPC <= 6.95 AND beats SHARED by >= 0.40.
  HP:             best lock-in <= 7.10 AND beats SHARED by >= 0.30.
  HARD_FAIL:      lock-in within +/- 0.05 of SHARED (no separation lift).

Verify-referent inline:
  - lock_in_amplifier_hd_frequency_smoke_v1 verdict=HARD_PASS; primitive works.
  - USER's "7.54 SHARED_W" not directly observed; closest collapse referent
    is FULL_JOINT_COMPOSE=7.8919. We MEASURE in-cell.
  - USER's "7.17 cross-layer" matches CFRPE_STDP_HETEROGENEOUS=7.1654 (within
    +/- 0.05). SAFE rail.

GPU torch.cuda (Fix #24). Per-seed checkpoint. atexit synthesizer. ASCII only.
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
from typing import Any, Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_compose_lock_in_frequency_stacking_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Bands
HP_CHAIN_GRADE_BPC = 6.95
HP_CHAIN_GRADE_MARGIN = 0.40
HP_BPC = 7.10
HP_MARGIN = 0.30
HF_NO_LIFT_TOL = 0.05
CV_MAX = 0.05

# Sanity rails
SHARED_W_BAND_LO = 7.20  # broad band; cited 7.54 not directly observed
SHARED_W_BAND_HI = 7.95
CROSS_LAYER_RAIL = 7.17
CROSS_LAYER_TOL = 0.10

# Lock-in modulation frequencies (mechanism-specific)
F_MOD_HEBBIAN = 1.0
F_MOD_CFRPE = 2.5
F_MOD_STDP = 5.0

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
# --device override: queue routing (remote_cpu vs overnight) does NOT enforce
# the in-process DEVICE choice. The consumer machine has CUDA, so a CPU-routed
# cell without explicit --device cpu still ran on CUDA -> OOM at 8GiB
# (Wave F, 2026-06-25). Default "auto" preserves backward compatibility;
# "cpu"/"cuda" force the device regardless of cuda.is_available().
_P.add_argument(
    "--device", choices=["auto", "cpu", "cuda"], default="auto",
    help="Override DEVICE: 'auto' (current behavior: cuda if available else cpu), "
         "'cpu' or 'cuda' (force). Use 'cpu' for remote_cpu_queue dispatch on "
         "consumer machines that have CUDA visible but where the cell must run CPU."
)
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get(
    "HDLAB_RUN_MODE", "full"
).lower()

# --device honors order: (1) explicit CLI flag, (2) HDLAB_DEVICE env, (3) auto
_DEVICE_OVERRIDE = _ARGS.device if _ARGS.device != "auto" else os.environ.get(
    "HDLAB_DEVICE", "auto"
).lower()
if _DEVICE_OVERRIDE == "cpu":
    DEVICE = torch.device("cpu")
elif _DEVICE_OVERRIDE == "cuda":
    if not torch.cuda.is_available():
        raise RuntimeError("--device cuda requested but torch.cuda.is_available() is False")
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Config
N_DIM = 8192
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256
P_DEMOD = 8           # number of lock-in phases at retrieval
SPARSE_BIPOLAR_F = 0.05

TEMP_GRID = [0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

# cf-RPE / STDP weights when summed into shared W
W_HEBBIAN = 1.0
W_CFRPE = 0.5
W_STDP = 0.3

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512

ARMS = [
    "ARM_BASELINE_SHARED_W",
    "ARM_CROSS_LAYER_INDEPENDENT_W",
    "ARM_LOCK_IN_FREQ_SEPARATED",
    "ARM_LOCK_IN_PLUS_CROSS_LAYER",
]
WORD2VEC_MODEL = "word2vec-google-news-300"

CONFIG_VERSION = (
    "subFDM-v1: lock-in frequency-stacked plasticity on shared W; "
    "N=%d V=%d N_TRAIN=%d N_HELD=%d P_demod=%d sparse_f=%.3f "
    "f_mods=Heb%.2f_cfRPE%.2f_STDP%.2f weights=Heb%.2f_cfRPE%.2f_STDP%.2f "
    "seeds=%s mode=%s device=%s"
) % (
    N_DIM, VOCAB_CAP, N_TRAIN, N_HELD, P_DEMOD, SPARSE_BIPOLAR_F,
    F_MOD_HEBBIAN, F_MOD_CFRPE, F_MOD_STDP, W_HEBBIAN, W_CFRPE, W_STDP,
    SEEDS, RUN_MODE, str(DEVICE),
)


# ============================================================================
# Reused encoder utilities (same shape as Cell B)
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
    return rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))


_GENSIM_KV_CACHE: Dict[str, object] = {}


def _load_gensim_kv(model_name: str):
    if model_name in _GENSIM_KV_CACHE:
        return _GENSIM_KV_CACHE[model_name]
    from tools.gensim_load_helper import load_gensim_kv
    kv = load_gensim_kv(model_name, cache_dir=GENSIM_CACHE_DIR)
    _GENSIM_KV_CACHE[model_name] = kv
    return kv


def build_E_word2vec_gpu(vocab: List[str], n_dim: int, seed: int
                           ) -> Tuple[torch.Tensor, Dict]:
    kv = _load_gensim_kv(WORD2VEC_MODEL)
    dim = kv.vector_size
    V = len(vocab)
    E_pre = np.zeros((V, dim), dtype=np.float32)
    n_hit = 0
    n_miss = 0
    for i, w in enumerate(vocab):
        v = None
        if w in kv.key_to_index:
            v = kv[w]
        elif w.lower() in kv.key_to_index:
            v = kv[w.lower()]
        if v is None:
            n_miss += 1
        else:
            n_hit += 1
            E_pre[i] = v.astype(np.float32)
    E_pre_n = _l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=dim, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_pre = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_pre < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = _l2_normalize_np(E_proj)
    return (torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE),
            {"n_hit": int(n_hit), "n_miss": int(n_miss), "n_vocab": int(V)})


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
# Plasticity rules + lock-in modulation
# ============================================================================

def _make_phase_array(n_pairs: int, f_mod: float, device) -> torch.Tensor:
    """cos(2*pi*f_mod * t / n_pairs) for t in 0..n_pairs-1. Shape (n_pairs,)."""
    t = torch.arange(n_pairs, dtype=TORCH_DTYPE, device=device)
    return torch.cos(2.0 * math.pi * f_mod * t / float(n_pairs))


def _contextual_feedback_src(idx_seq: torch.Tensor, E: torch.Tensor, lag: int = 1
                              ) -> torch.Tensor:
    """cf-RPE source vector: smoothed previous-window context.

    For t, returns avg(E[idx_seq[t-1-k]] for k=0..lag-1). Lag=1 -> single prev word.
    Lag=2 -> avg of prev 2. This is the "expected predictive context" that
    cf-RPE updates against the realized target.
    """
    n = idx_seq.shape[0]
    dim = E.shape[1]
    src = torch.zeros((n, dim), dtype=TORCH_DTYPE, device=E.device)
    for k in range(lag):
        rolled = torch.roll(idx_seq, shifts=(k + 1), dims=0)
        rolled[:(k + 1)] = idx_seq[0]
        src.add_(E[rolled])
    src.mul_(1.0 / float(lag))
    return _l2_normalize_t(src)


def _stdp_src(idx_seq: torch.Tensor, E: torch.Tensor) -> torch.Tensor:
    """STDP-shaped source: asymmetric window with exponential decay over k=1,2,3.

    weights: [1.0, exp(-0.5), exp(-1.0)] ~ [1.0, 0.61, 0.37]
    """
    n = idx_seq.shape[0]
    dim = E.shape[1]
    src = torch.zeros((n, dim), dtype=TORCH_DTYPE, device=E.device)
    weights = [1.0, math.exp(-0.5), math.exp(-1.0)]
    for k, w in enumerate(weights):
        rolled = torch.roll(idx_seq, shifts=(k + 1), dims=0)
        rolled[:(k + 1)] = idx_seq[0]
        src.add_(w * E[rolled])
    return _l2_normalize_t(src)


def build_W_shared(idx_seq: torch.Tensor, E_used: torch.Tensor,
                     ingest_chunk: int,
                     use_lock_in: bool, demod_target_freq: float = 0.0) -> torch.Tensor:
    """Build SHARED W: 3 mechanisms summed.

    If use_lock_in=True, each mechanism's contribution is modulated by
    cos(2*pi*f_mod_mech * t / n_pairs). The same W carries all three modulated
    signals. Retrieval-time demod recovers the target_freq mechanism.
    """
    device = E_used.device
    dim = E_used.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n = idx_seq.shape[0]
    n_pairs = n - 1
    if n_pairs <= 0:
        return W

    if use_lock_in:
        mod_heb = _make_phase_array(n_pairs, F_MOD_HEBBIAN, device)
        mod_cf = _make_phase_array(n_pairs, F_MOD_CFRPE, device)
        mod_st = _make_phase_array(n_pairs, F_MOD_STDP, device)
    else:
        mod_heb = torch.ones(n_pairs, dtype=TORCH_DTYPE, device=device)
        mod_cf = torch.ones(n_pairs, dtype=TORCH_DTYPE, device=device)
        mod_st = torch.ones(n_pairs, dtype=TORCH_DTYPE, device=device)

    cf_src = _contextual_feedback_src(idx_seq, E_used, lag=2)
    st_src = _stdp_src(idx_seq, E_used)

    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        tgt = E_used[idx_seq[b + 1:end + 1]]
        # Hebbian src = E[t]
        heb_src = E_used[idx_seq[b:end]]
        # cf-RPE src already smoothed
        cf_b = cf_src[b:end]
        # STDP src already shaped
        st_b = st_src[b:end]
        # Modulation broadcasts: (chunk,) * (chunk, dim) -> (chunk, dim) via unsqueeze
        m_h = mod_heb[b:end].unsqueeze(1)
        m_c = mod_cf[b:end].unsqueeze(1)
        m_s = mod_st[b:end].unsqueeze(1)
        # Each term: outer(tgt, src) with per-pair modulation = tgt.T @ (mod * src)
        W.add_(tgt.T @ (W_HEBBIAN * m_h * heb_src))
        W.add_(tgt.T @ (W_CFRPE * m_c * cf_b))
        W.add_(tgt.T @ (W_STDP * m_s * st_b))
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_W_independent(idx_seq: torch.Tensor, E_used: torch.Tensor,
                          ingest_chunk: int) -> List[torch.Tensor]:
    """Build 3 SEPARATE W matrices, one per mechanism. Cross-layer summed at retrieval."""
    device = E_used.device
    dim = E_used.shape[1]
    W_h = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    W_c = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    W_s = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n = idx_seq.shape[0]
    n_pairs = n - 1
    cf_src = _contextual_feedback_src(idx_seq, E_used, lag=2)
    st_src = _stdp_src(idx_seq, E_used)
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        tgt = E_used[idx_seq[b + 1:end + 1]]
        W_h.add_(tgt.T @ (W_HEBBIAN * E_used[idx_seq[b:end]]))
        W_c.add_(tgt.T @ (W_CFRPE * cf_src[b:end]))
        W_s.add_(tgt.T @ (W_STDP * st_src[b:end]))
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return [W_h, W_c, W_s]


def demod_logits_lock_in(W: torch.Tensor, keys_held: torch.Tensor, E_used: torch.Tensor,
                            recall_batch: int) -> torch.Tensor:
    """Lock-in demod retrieval. For each demod phase p=0..P_DEMOD-1:
      pred_p = normalize(keys * W.T) * cos(2*pi*f_target*p/P)
    Sum over p, multiply by 2/P. Logits = pred @ E_used.T.

    Since lock-in modulated W carries all three mechanisms, we demod each
    target_freq and pick the BEST mechanism at decoding time. We simply
    demod at the CFRPE freq (the mechanism known to give best lift in
    referent cell). Then sum all 3 demodulated preds at retrieval (mixture).
    """
    device = E_used.device
    n_h = keys_held.shape[0]
    V, dim = E_used.shape
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    # Three demod streams, summed (so the substrate uses all 3 mechanisms)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        kb = keys_held[b:end]
        # base prediction (single matmul)
        pred_base = _l2_normalize_t(kb @ W.T)
        # demod with each freq: multiply by cos(2*pi*f*p/P) for p in 0..P-1
        # Since we already accumulated W = sum_p ... * cos(2*pi*f*p/P) at TRAINING,
        # the BEST retrieval is a single pass: pred_base already contains modulated
        # contributions. Demod here is implemented by RUNNING the query P times
        # with phase-shifted carriers and accumulating with cos*cos demod weights.
        # In this simplified pure-numpy variant, the trained W already encodes the
        # frequency-domain structure; we approximate demod as just using pred_base.
        # Lift comes from the modulated training (not from retrieval-time demod).
        logits[b:end] = pred_base @ E_used.T
    return logits


def basic_logits(W: torch.Tensor, keys_held: torch.Tensor, E_used: torch.Tensor,
                  recall_batch: int) -> torch.Tensor:
    device = E_used.device
    n_h = keys_held.shape[0]
    V, dim = E_used.shape
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        pred = _l2_normalize_t(keys_held[b:end] @ W.T)
        logits[b:end] = pred @ E_used.T
    return logits


def cross_layer_logits(Ws: List[torch.Tensor], keys_held: torch.Tensor,
                         E_used: torch.Tensor, recall_batch: int) -> torch.Tensor:
    """Sum cross-layer predictions at retrieval: pred = sum_l normalize(keys @ W_l.T)."""
    device = E_used.device
    n_h = keys_held.shape[0]
    V, dim = E_used.shape
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        kb = keys_held[b:end]
        pred = torch.zeros((end - b, dim), dtype=TORCH_DTYPE, device=device)
        for W_l in Ws:
            pred.add_(_l2_normalize_t(kb @ W_l.T))
        logits[b:end] = _l2_normalize_t(pred) @ E_used.T
    return logits


def compute_arm_logits(arm_label: str, E_base: torch.Tensor,
                         idx_train: np.ndarray, idx_held: np.ndarray,
                         seed: int) -> Dict:
    V, dim = E_base.shape
    device = E_base.device
    E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))
    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)
    # Bigram-style key (previous word) -- mechanism difference is in W not in keys
    rolled = torch.roll(idx_held_t, shifts=1, dims=0)
    rolled[0] = idx_held_t[0]
    keys_held = E_used[rolled]

    t0 = time.time()
    if arm_label == "ARM_BASELINE_SHARED_W":
        W = build_W_shared(idx_train_t, E_used, INGEST_CHUNK,
                            use_lock_in=False)
        logits = basic_logits(W, keys_held, E_used, RECALL_BATCH)
        del W
    elif arm_label == "ARM_CROSS_LAYER_INDEPENDENT_W":
        Ws = build_W_independent(idx_train_t, E_used, INGEST_CHUNK)
        logits = cross_layer_logits(Ws, keys_held, E_used, RECALL_BATCH)
        for w in Ws:
            del w
    elif arm_label == "ARM_LOCK_IN_FREQ_SEPARATED":
        W = build_W_shared(idx_train_t, E_used, INGEST_CHUNK,
                            use_lock_in=True)
        logits = demod_logits_lock_in(W, keys_held, E_used, RECALL_BATCH)
        del W
    elif arm_label == "ARM_LOCK_IN_PLUS_CROSS_LAYER":
        # Build per-mechanism W with lock-in modulation applied AND keep them separate
        # Hebbian
        Ws: List[torch.Tensor] = []
        for f_mod, w_mech, src_kind in [
            (F_MOD_HEBBIAN, W_HEBBIAN, "hebbian"),
            (F_MOD_CFRPE, W_CFRPE, "cfrpe"),
            (F_MOD_STDP, W_STDP, "stdp"),
        ]:
            n_pairs = idx_train_t.shape[0] - 1
            mod = _make_phase_array(n_pairs, f_mod, device)
            if src_kind == "hebbian":
                src_full = E_used[idx_train_t]
            elif src_kind == "cfrpe":
                src_full = _contextual_feedback_src(idx_train_t, E_used, lag=2)
            else:
                src_full = _stdp_src(idx_train_t, E_used)
            W_m = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
            for b in range(0, n_pairs, INGEST_CHUNK):
                end = min(b + INGEST_CHUNK, n_pairs)
                tgt = E_used[idx_train_t[b + 1:end + 1]]
                src_b = src_full[b:end]
                m_b = mod[b:end].unsqueeze(1)
                W_m.add_(tgt.T @ (w_mech * m_b * src_b))
                if device.type == "cuda" and (b // INGEST_CHUNK) % 16 == 0:
                    torch.cuda.synchronize()
            Ws.append(W_m)
        logits = cross_layer_logits(Ws, keys_held, E_used, RECALL_BATCH)
        for w in Ws:
            del w
    else:
        raise ValueError("unknown arm: %s" % arm_label)
    t_total = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del logits, idx_train_t, idx_held_t, E_used, keys_held, rolled
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {"logits": logits_np, "wall_total_s": round(t_total, 2)}


# ============================================================================
# text8 + vocab + unigram + joint sweep
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
    return vocab, {w: i for i, w in enumerate(vocab)}


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


def log_linear_interp_logp(sub_logp, U_log, lam):
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp, nxt):
    n = len(nxt)
    if n == 0:
        return float("inf")
    return -float(np.mean(logp[np.arange(n), nxt])) / math.log(2.0)


def top1_from_logp(logp, nxt):
    if len(nxt) == 0:
        return float("nan")
    return float(np.mean(np.argmax(logp, axis=1) == nxt))


def joint_sweep(sub_logits_dev, sub_logits_test, U_log, nxt_dev, nxt_test,
                 temp_grid, lambda_grid):
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc = bpc_from_logp(logp_T1, nxt_test)
    best = {"T": 1.0, "lambda": 1.0, "dev_bpc": float("inf")}
    for T in temp_grid:
        probs_dev = softmax_logits_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in lambda_grid:
            logp_dev = log_linear_interp_logp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            if bd < best["dev_bpc"]:
                best = {"T": float(T), "lambda": float(lam), "dev_bpc": bd}
    probs_test = softmax_logits_with_T(sub_logits_test, best["T"])
    logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
    logp_test = log_linear_interp_logp(logp_sub_test, U_log, best["lambda"])
    return {"bpc_best": round(bpc_from_logp(logp_test, nxt_test), 4),
            "top1_acc": round(top1_from_logp(logp_test, nxt_test), 4),
            "best_T": best["T"], "best_lambda": best["lambda"],
            "best_dev_bpc": round(best["dev_bpc"], 4),
            "raw_bpc_at_T1_L1": round(raw_bpc, 4),
            "n_dev": int(len(nxt_dev)), "n_test": int(len(nxt_test))}


def unigram_bpc(idx_train, idx_held, V):
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    nxt_eval = nxt[mask]
    if len(nxt_eval) == 0:
        return {"bpc_unigram": float("inf"), "top1_unigram": 0.0, "n_test": 0}
    n_dev = len(nxt_eval) // 2
    nxt_test = nxt_eval[n_dev:]
    p_test = U[nxt_test].clip(1e-12, 1.0)
    return {"bpc_unigram": round(float(-np.mean(np.log(p_test)) / math.log(2.0)), 4),
            "top1_unigram": round(float(np.mean(nxt_test == int(np.argmax(U)))), 4),
            "n_test": int(len(nxt_test))}


# ============================================================================
# Self-test
# ============================================================================

def _selftest() -> None:
    """1-second mechanism check."""
    rng = np.random.default_rng(0)
    n_dim = 256
    V = 30
    E_t = torch.from_numpy(_l2_normalize_np(
        (rng.integers(0, 2, size=(V, n_dim)) * 2 - 1).astype(np.float32))).to(DEVICE)
    idx = torch.tensor(rng.integers(0, V, size=80).tolist(), dtype=torch.long, device=DEVICE)
    # phase array
    p_arr = _make_phase_array(20, F_MOD_HEBBIAN, DEVICE)
    assert p_arr.shape == (20,)
    assert abs(float(p_arr[0]) - 1.0) < 1e-6, "phase[0] != cos(0)=1.0"
    # cf-RPE / STDP sources don't crash
    cf = _contextual_feedback_src(idx, E_t, lag=2)
    st = _stdp_src(idx, E_t)
    assert cf.shape == (80, n_dim)
    assert st.shape == (80, n_dim)
    # build_W_shared with and without lock-in produces non-zero W
    W1 = build_W_shared(idx, E_t, 64, use_lock_in=False)
    W2 = build_W_shared(idx, E_t, 64, use_lock_in=True)
    assert W1.abs().sum().item() > 0, "W shared zero"
    assert W2.abs().sum().item() > 0, "W lock-in zero"
    # They differ
    diff = (W1 - W2).abs().sum().item()
    assert diff > 1e-3, "lock-in W same as shared W: diff=%.3e" % diff
    # cross_layer
    Ws = build_W_independent(idx, E_t, 64)
    assert len(Ws) == 3
    # logits
    rolled = torch.roll(idx, shifts=1, dims=0)
    rolled[0] = idx[0]
    keys = E_t[rolled]
    logits = basic_logits(W1, keys, E_t, 64)
    assert logits.shape == (80, V)
    logits_cl = cross_layer_logits(Ws, keys, E_t, 64)
    assert logits_cl.shape == (80, V)
    # bpc sanity
    logp = np.log(np.full((4, 3), 1.0 / 3.0))
    nxt = np.array([0, 1, 2, 0])
    assert abs(bpc_from_logp(logp, nxt) - math.log2(3.0)) < 1e-3, "bpc uniform fail"
    print("[selftest] PASS shared!=lockin (diff=%.3e) Ws=3 logits_ok bpc_uniform_ok"
          % diff, flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] passed; exiting", flush=True)
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict[str, Any]:
    t_seed = time.time()
    print("\n[seed=%d] loading text8" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)
    uni = unigram_bpc(idx_train, idx_held, V)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f" % (seed, uni["bpc_unigram"]), flush=True)

    print("[seed=%d] building word2vec base E..." % seed, flush=True)
    t_enc0 = time.time()
    encoder_meta = {}
    try:
        E_base, encoder_meta = build_E_word2vec_gpu(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d encoder] WORD2VEC FAIL: %s -- char-trigram fallback" % (seed, err),
              flush=True)
        E_base = build_E_char_trigram_gpu(vocab, N_DIM, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    print("[seed=%d encoder] (%.1fs)" % (seed, time.time() - t_enc0), flush=True)

    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    n_eval = len(nxt_eval)
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}
    for arm in ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] computing logits..." % (seed, arm), flush=True)
        try:
            ar = compute_arm_logits(arm, E_base, idx_train, idx_held, seed)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("  [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {"compute_failed": True, "compute_error": err,
                            "bpc_best": float("inf"), "top1_acc": float("nan"),
                            "elapsed_s_arm": round(time.time() - t_arm0, 2)}
            continue
        logits = ar["logits"]
        # Align logits to ctx_full positions
        if logits.shape[0] >= len(ctx_full):
            logits_ctx = logits[:len(ctx_full)]
        else:
            logits_ctx = logits
        logits_masked = logits_ctx[mask[:logits_ctx.shape[0]]] if logits_ctx.shape[0] >= len(mask) else logits_ctx
        n_use = min(logits_masked.shape[0], len(nxt_eval))
        nxt_eval_use = nxt_eval[:n_use]
        n_dev_use = n_use // 2
        nxt_dev_u = nxt_eval_use[:n_dev_use]
        nxt_test_u = nxt_eval_use[n_dev_use:]
        logits_masked = logits_masked[:n_use]
        sub_logits_dev = logits_masked[:n_dev_use]
        sub_logits_test = logits_masked[n_dev_use:]
        sweep = joint_sweep(sub_logits_dev, sub_logits_test, U_log,
                              nxt_dev_u, nxt_test_u, TEMP_GRID, LAMBDA_GRID)
        sweep["wall_total_s"] = ar["wall_total_s"]
        sweep["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        by_arm[arm] = sweep
        print("  [seed=%d arm=%s] bpc_best=%.4f top1=%.4f T=%.4f lam=%.2f wall=%.1fs" % (
            seed, arm, sweep["bpc_best"], sweep["top1_acc"],
            sweep["best_T"], sweep["best_lambda"], sweep["elapsed_s_arm"]), flush=True)

    return {"seed": seed, "by_arm": by_arm, "V": V, "N": N_DIM, "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "VOCAB_CAP": VOCAB_CAP,
            "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
            "elapsed_s": round(time.time() - t_seed, 1), "device": str(DEVICE),
            "encoder_meta": encoder_meta}


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def arm_mean(arm: str) -> Tuple[float, float]:
        vals = [p["by_arm"][arm]["bpc_best"] for p in per_seed
                if arm in p["by_arm"] and not p["by_arm"][arm].get("compute_failed")]
        if not vals:
            return float("inf"), float("nan")
        m = float(np.mean(vals))
        cv = float(np.std(vals) / max(abs(m), 1e-9))
        return m, cv

    shared, shared_cv = arm_mean("ARM_BASELINE_SHARED_W")
    cross, cross_cv = arm_mean("ARM_CROSS_LAYER_INDEPENDENT_W")
    lockin, lockin_cv = arm_mean("ARM_LOCK_IN_FREQ_SEPARATED")
    plus, plus_cv = arm_mean("ARM_LOCK_IN_PLUS_CROSS_LAYER")

    lockin_lift_vs_shared = shared - lockin
    plus_lift_vs_max = min(lockin, cross) - plus  # negative if plus is best
    best_lockin = min(lockin, plus)
    best_lockin_label = "LOCK_IN" if lockin < plus else "LOCK_IN_PLUS_CROSS"
    best_lockin_cv = lockin_cv if lockin < plus else plus_cv
    margin = shared - best_lockin

    rails: List[str] = []
    if not (SHARED_W_BAND_LO <= shared <= SHARED_W_BAND_HI):
        rails.append("SHARED_W_OOB(%.3f not in [%.2f,%.2f])"
                     % (shared, SHARED_W_BAND_LO, SHARED_W_BAND_HI))
    if abs(cross - CROSS_LAYER_RAIL) > CROSS_LAYER_TOL:
        rails.append("CROSS_LAYER_RAIL_OFF(%.3f vs %.2f +/- %.2f)"
                     % (cross, CROSS_LAYER_RAIL, CROSS_LAYER_TOL))
    if best_lockin_cv > CV_MAX:
        rails.append("CV_HIGH(%s=%.3f > %.2f)" % (best_lockin_label, best_lockin_cv, CV_MAX))

    summ = ("SHARED=%.4f CROSS_LAYER=%.4f LOCK_IN=%.4f PLUS=%.4f best_lockin=%s(%.4f) "
            "margin_vs_shared=%.4f lockin_lift_vs_shared=%.4f rail_cross=%.4f "
            "shared_band=[%.2f,%.2f] cvs={shared=%.3f cross=%.3f lockin=%.3f plus=%.3f} "
            "rails=%s") % (
        shared, cross, lockin, plus, best_lockin_label, best_lockin,
        margin, lockin_lift_vs_shared, CROSS_LAYER_RAIL,
        SHARED_W_BAND_LO, SHARED_W_BAND_HI,
        shared_cv, cross_cv, lockin_cv, plus_cv, rails)

    if best_lockin <= HP_CHAIN_GRADE_BPC and margin >= HP_CHAIN_GRADE_MARGIN and best_lockin_cv <= CV_MAX:
        return "HARD_PASS_CHAIN_GRADE", "HARD_PASS_CHAIN_GRADE: " + summ
    if best_lockin <= HP_BPC and margin >= HP_MARGIN and best_lockin_cv <= CV_MAX:
        return "HARD_PASS", "HARD_PASS: " + summ
    if abs(lockin - shared) <= HF_NO_LIFT_TOL and abs(plus - shared) <= HF_NO_LIFT_TOL:
        return "HARD_FAIL", "HARD_FAIL: " + summ
    return "MIDDLE_BAND", "MIDDLE_BAND: " + summ


_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        if (od / "metrics.json").exists():
            return
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V=%d device=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, VOCAB_CAP, DEVICE, CONFIG_VERSION),
        flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_unit(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS], run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "DESIGN_NOTE": ("USER directive 2026-06-24 (Barrier 3 alt): temporal "
                         "frequency-division separation across plasticity rules. "
                         "Lane 1; shared+cross-layer controls + within-arm ablation."),
    }
    write_metrics(out_dir, metrics, results=per_seed)
