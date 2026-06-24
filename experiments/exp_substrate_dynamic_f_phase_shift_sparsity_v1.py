"""substrate_dynamic_f_phase_shift_sparsity_v1 -- DYNAMIC f sparsity (store vs query).

PURPOSE (2026-06-24):
  Meta-skepticism Anchor 4 / USER A11: "is f one of the things we can phase-shift
  around? It would be pretty amazing to be able to switch to a fast high-power mode
  and to a slower low-power mode."

  Brain prior: cortical sparsity is dynamically modulated by ACh/NE
  neuromodulators (Goard-Dan 2009; Pinto-Goard 2013; Polack-Friedman-Golshani 2013).
  Awake/attending = denser cortical activation (fast, high-power). Asleep/default =
  sparser activation (slow, low-power, capacity-efficient).

  Substrate analog (this cell): vary sparsity fraction f BETWEEN store and query
  phases. Storage uses one f (representation written into bank); query uses a
  potentially different f (representation used to decode/lookup). Two fixed
  phases; no continuous modulation; no query-difficulty gating (future work).

  Distinct from existing modulator cells:
   - exp_substrate_ACh_query_conditional_read_gain_LM_v1: per-query gain on logit
     magnitude (multiplicative scalar). Does NOT vary sparsity.
   - exp_excitability_gated_substrate_cpu_v1: write-time excitability gating.
     Does NOT vary recall-side representation.
  This cell varies SPARSITY (top-k fraction f) across store-vs-query phases.

SIX ARMS (3 static baselines + 3 dynamic-f):
  ARM_STATIC_F_0p02       (f_store=f_query=0.02; A5 finding: f=0.02 capacity-optimal)
  ARM_STATIC_F_0p05       (f_store=f_query=0.05; fair_harness reference; SANITY RAIL)
  ARM_STATIC_F_0p50       (f_store=f_query=0.50; dense baseline)
  ARM_DYNAMIC_STORE002_QUERY005  (store sparse 0.02; query 0.05)
  ARM_DYNAMIC_STORE002_QUERY050  (store sparse 0.02; query dense 0.50)
  ARM_DYNAMIC_STORE005_QUERY050  (store middle 0.05; query dense 0.50)

MECHANISM (per arm):
  Let E_base = word2vec(vocab) -> Gaussian-project(N_DIM) -> L2 normalize. ONE per seed.
  E_store_f = L2(sparsify_bipolar(E_base, f_store))
  E_query_f = L2(sparsify_bipolar(E_base, f_query))
  Storage:  W = sum_{t in train} E_store_f[idx[t+1]]^T @ E_store_f[idx[t]]
  Recall:   query[ctx] = L2(E_store_f[ctx] @ W^T)        # in store-sparsity space
            logits[ctx] = query[ctx] @ E_query_f^T        # decode in query-sparsity space
  When f_store == f_query, this is the STATIC f baseline (matches fair_harness pipeline).
  When f_store != f_query, the query phase READS bound traces through a different
  sparsity prior. Brain analog: storage is sparse (capacity), recall is dense (speed).

PRE-REGISTERED HARD bands (PRE-REGISTERED BEFORE RUN; do NOT adjust post-smoke):
  Sanity rail: ARM_STATIC_F_0p05 BPC within +/-0.05 of fair_harness 7.3065
  HARD_PASS: any dynamic arm gives BPC <= (best static arm BPC) - 0.10 bits
             AND that dynamic arm cv <= 0.05
  CHAIN_GRADE_BONUS: any dynamic arm gives BPC <= (best static arm BPC) - 0.30 bits
             (substrate-novel mode-switching unlocked at fair_harness scale)
  MIDDLE_BAND: any dynamic arm gives BPC lift in [+0.05, +0.10) over best static
  HARD_FAIL: ALL dynamic arms BPC >= best static arm BPC (no mode-switch lift)

WHAT_THIS_DOES_NOT_SHOW:
  - Does NOT test continuous-f modulation (only 2 fixed phases per arm)
  - Does NOT test query-difficulty gated f-switching (no per-query adaptive f)
  - Does NOT test 3+ phase modes (only store/query 2-phase)
  - Does NOT vary f_store across train trajectory (storage f is fixed per arm)
  - Result at N_TRAIN=100k text8 V=4000 may not generalize

ROUTING: overnight_queue (GPU). Fix #24: uses torch.cuda for storage and recall
  matmuls. N_DIM=8192 W=8192x8192 matmul benefits from GPU. Encoder built on CPU
  via gensim then moved to CUDA. Per-seed elapsed expected 20-40 min on RTX (smoke
  cap 180s).

DISCIPLINES:
  ASCII-only, no emojis, no em dashes
  Fix #14: ONE cell
  Fix #24: torch.cuda for heavy matmuls
  Fix #28: per-arm metrics ONLY in verdict_msg; no cross-arm framing
  A5: path-scoped commit (caller responsibility)
  LAMBDA_GRID excludes 0.0 (Skunkworks META C7)
  Per-seed checkpointing via _seed_checkpoint
  --self-test (selftest gate) and --smoke (small grid) both supported

Cites:
  preregs/2026-06-24_substrate_dynamic_f_phase_shift_sparsity_v1.md
  experiments/exp_fair_harness_substrate_as_lm_v1.py (sanity rail 7.3065)
  experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py (torch.cuda + word2vec template)
  experiments/exp_substrate_ACh_query_conditional_read_gain_LM_v1.py (related: per-query gain)
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
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "substrate_dynamic_f_phase_shift_sparsity_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# ============================================================================
# Pre-reg threshold bands (pre-registered; do NOT modify post-smoke)
# ============================================================================
FAIR_HARNESS_REF_BPC = 7.3065
SANITY_RAIL_TOL = 0.05
HARD_PASS_LIFT_BPC = 0.10
CHAIN_GRADE_BONUS_LIFT_BPC = 0.30
MIDDLE_BAND_LIFT_LOW = 0.05
MIDDLE_BAND_LIFT_HIGH = 0.10
CV_MAX = 0.05

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

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# ============================================================================
# Encoder + grid config
# ============================================================================
WORD2VEC_MODEL = "word2vec-google-news-300"
PRETRAIN_DIM = 300

# Joint (T, lambda) sweep grid (LAMBDA_GRID excludes 0.0 per Skunkworks META C7)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Arms: (f_store, f_query) tuples
ARMS = [
    "ARM_STATIC_F_0p02",
    "ARM_STATIC_F_0p05",
    "ARM_STATIC_F_0p50",
    "ARM_DYNAMIC_STORE002_QUERY005",
    "ARM_DYNAMIC_STORE002_QUERY050",
    "ARM_DYNAMIC_STORE005_QUERY050",
]

ARM_FCFG: Dict[str, Tuple[float, float]] = {
    "ARM_STATIC_F_0p02":             (0.02, 0.02),
    "ARM_STATIC_F_0p05":             (0.05, 0.05),
    "ARM_STATIC_F_0p50":             (0.50, 0.50),
    "ARM_DYNAMIC_STORE002_QUERY005": (0.02, 0.05),
    "ARM_DYNAMIC_STORE002_QUERY050": (0.02, 0.50),
    "ARM_DYNAMIC_STORE005_QUERY050": (0.05, 0.50),
}

STATIC_ARMS = {"ARM_STATIC_F_0p02", "ARM_STATIC_F_0p05", "ARM_STATIC_F_0p50"}
DYNAMIC_ARMS = {a for a in ARMS if a not in STATIC_ARMS}
SANITY_RAIL_ARM = "ARM_STATIC_F_0p05"

# ============================================================================
# Production config
# ============================================================================
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    N_TRAIN = 100_000
    N_HELD = 20_000
    VOCAB_CAP = 4000
    INGEST_CHUNK = 4096
    RECALL_BATCH = 256
else:
    # Smoke: <180s on CPU/GPU. Exercises every arm + word2vec + joint sweep + verdict.
    SEEDS = [0]
    N_DIM = 512
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

CONFIG_VERSION = (
    "substrate_dynamic_f_phase_shift_sparsity_v1; encoder=word2vec; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s mode=%s "
    "temps=%s lambdas=%s arm_fcfg=%s device=%s"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    TEMP_GRID, LAMBDA_GRID, ARM_FCFG, str(DEVICE),
)

_LLM_CALL_COUNTER = [0]


# ============================================================================
# text8 + vocab
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
# Encoder: word2vec -> Gaussian-project -> L2 normalize (base; pre-sparsify)
# OOV fallback: char-trigram
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


def build_E_base_word2vec(vocab: List[str], n_dim: int, seed: int
                           ) -> Tuple[torch.Tensor, Dict]:
    """Build BASE encoder [V, n_dim] L2-normalized word2vec on DEVICE.

    Pipeline: word2vec(300) -> Gaussian-project(300 -> n_dim) -> L2 normalize.
    OOV words: fall back to char-trigram (no zero-row degeneracy).
    NO sparsification at this stage; sparsification is per-arm downstream.
    """
    try:
        kv = _load_gensim_kv(WORD2VEC_MODEL)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[encoder] WORD2VEC LOAD FAIL: %s -- falling back to char-trigram" % err, flush=True)
        E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
        E_np = _l2_normalize_np(E_np)
        E_t = torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)
        meta = {"fallback_to_char_trigram": True, "load_error": err,
                "n_hit": 0, "n_miss": len(vocab), "n_vocab": len(vocab),
                "pretrain_dim": -1}
        return E_t, meta
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = _l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_pre = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_pre < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = _l2_normalize_np(E_proj)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size),
            "fallback_to_char_trigram": False}
    return E_t, meta


def sparsify_bipolar_gpu(E: torch.Tensor, f: float) -> torch.Tensor:
    """Sparse-bipolar projection on GPU: top-k by abs; sign-encode."""
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
# Hebbian W builder (rank-1; torch on DEVICE; chunked)
# ============================================================================
def build_W_rank1_hebbian_gpu(E_store: torch.Tensor, idx_train_t: torch.Tensor,
                                ingest_chunk: int) -> torch.Tensor:
    """W = sum_t E_store[idx[t+1]]^T @ E_store[idx[t]]. Shape: dim x dim."""
    device = E_store.device
    dim = E_store.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train_t[b:end]
        tgt_idx = idx_train_t[b + 1:end + 1]
        W.add_(E_store[tgt_idx].T @ E_store[src_idx])
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


# ============================================================================
# Per-arm logits builder (DYNAMIC-F core mechanism)
# ============================================================================
def build_logits_dynamic_f_gpu(E_base: torch.Tensor, f_store: float, f_query: float,
                                 idx_train_t: torch.Tensor, idx_held_t: torch.Tensor,
                                 recall_batch: int, ingest_chunk: int) -> Dict:
    """Build storage bank at f_store; build query bank at f_query.

    Storage:  W = sum_t E_store[idx[t+1]]^T @ E_store[idx[t]]
    Recall:   query[ctx] = L2(E_store[ctx] @ W^T)             # store-space query
              logits[ctx] = query[ctx] @ E_query^T            # decode in query-space
    """
    V, dim = E_base.shape
    n_h = idx_held_t.shape[0]
    device = E_base.device

    t0 = time.time()
    E_store = _l2_normalize_t(sparsify_bipolar_gpu(E_base, f_store))
    E_query = _l2_normalize_t(sparsify_bipolar_gpu(E_base, f_query))
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_sparsify = time.time() - t0

    t0 = time.time()
    W = build_W_rank1_hebbian_gpu(E_store, idx_train_t, ingest_chunk)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_store[idx_held_t[b:end]]      # in store-sparsity space
        pred_b = _l2_normalize_t(ctx_b @ W.T)
        logits[b:end] = pred_b @ E_query.T       # decode in query-sparsity space
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W, E_store, E_query, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "logits": logits_np,
        "wall_sparsify_s": round(t_sparsify, 2),
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
    }


# ============================================================================
# BPC / eval utilities
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
    """Joint (T, lambda) sweep on dev; pick best per-metric; report on test."""
    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}

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

    def _eval_test(T: float, lam: float, fn) -> float:
        probs = softmax_with_T(sub_logits_test, T)
        logp_sub = np.log(np.clip(probs, 1e-30, 1.0))
        logp = log_linear_interp(logp_sub, U_log, lam)
        return fn(logp, nxt_test)

    bpc_best_test = _eval_test(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _eval_test(best_top1["T"], best_top1["lambda"], top1_acc)
    mrr_best_test = _eval_test(best_mrr["T"], best_mrr["lambda"],
                                lambda lp, nx: mrr_at_k(lp, nx, MRR_K))

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
# Instrumentation self-test
# ============================================================================
def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)

    # ST1: sparsify_bipolar_gpu produces exactly k nonzeros (rounded), bipolar
    rng_st = np.random.default_rng(0)
    E_chk = torch.from_numpy(rng_st.standard_normal((20, 100)).astype(np.float32)).to(DEVICE)
    for f in (0.02, 0.05, 0.50):
        E_sp = sparsify_bipolar_gpu(E_chk, f)
        nnz_per_row = (E_sp != 0).sum(dim=1).cpu().numpy()
        k_expect = max(1, int(round(f * 100)))
        assert bool((nnz_per_row == k_expect).all()), (
            "ST1 sparse nnz mismatch for f=%.3f: expected %d, got %s" % (
                f, k_expect, str(nnz_per_row[:5])))
        uniq = set(E_sp.unique().cpu().tolist())
        assert uniq.issubset({-1.0, 0.0, 1.0}), "ST1 sparse values: got %s for f=%.3f" % (uniq, f)
    print("[selftest] ST1 sparsify_bipolar_gpu nnz correct for f in (0.02, 0.05, 0.50) OK", flush=True)

    # ST2: dynamic-f mechanism actually uses different banks when f_store != f_query
    # Build tiny synthetic: 2 sparsifications with different f produce different non-zero patterns
    V_st, n_dim_st = 8, 128
    rng2 = np.random.default_rng(7)
    E_np = _l2_normalize_np(rng2.standard_normal((V_st, n_dim_st)).astype(np.float32))
    E_t = torch.from_numpy(E_np).to(DEVICE)
    E_002 = sparsify_bipolar_gpu(E_t, 0.02)  # k=3
    E_050 = sparsify_bipolar_gpu(E_t, 0.50)  # k=64
    nnz_002 = (E_002 != 0).sum().item()
    nnz_050 = (E_050 != 0).sum().item()
    assert nnz_050 > nnz_002, "ST2 dense bank should have more nonzeros: %d vs %d" % (nnz_050, nnz_002)
    # And the two banks differ on at least some entries (different sparsity patterns)
    diff_mask = (E_002 != E_050).any().item()
    assert diff_mask, "ST2 store and query sparse banks must differ when f differs"
    print("[selftest] ST2 dynamic-f banks differ when f_store != f_query (nnz_0p02=%d nnz_0p50=%d) OK" % (
        nnz_002, nnz_050), flush=True)

    # ST3: build_logits_dynamic_f_gpu produces correct shape and non-zero logits
    idx_tr_st = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 0, 1], dtype=torch.long, device=DEVICE)
    idx_h_st = torch.tensor([2, 3, 4, 5], dtype=torch.long, device=DEVICE)
    ar = build_logits_dynamic_f_gpu(
        E_t, f_store=0.05, f_query=0.05,
        idx_train_t=idx_tr_st, idx_held_t=idx_h_st,
        recall_batch=4, ingest_chunk=4)
    logits_st = ar["logits"]
    assert logits_st.shape == (4, V_st), "ST3 logits shape: got %s" % str(logits_st.shape)
    assert not np.all(logits_st == 0.0), "ST3 logits all zero"
    print("[selftest] ST3 build_logits_dynamic_f_gpu shape=%s non-zero OK" % str(logits_st.shape), flush=True)

    # ST4: dynamic-f vs static-f produce DIFFERENT logits (mechanism is real, not no-op)
    ar_static = build_logits_dynamic_f_gpu(
        E_t, f_store=0.05, f_query=0.05,
        idx_train_t=idx_tr_st, idx_held_t=idx_h_st,
        recall_batch=4, ingest_chunk=4)
    ar_dynamic = build_logits_dynamic_f_gpu(
        E_t, f_store=0.02, f_query=0.50,
        idx_train_t=idx_tr_st, idx_held_t=idx_h_st,
        recall_batch=4, ingest_chunk=4)
    diff = float(np.abs(ar_static["logits"] - ar_dynamic["logits"]).mean())
    assert diff > 1e-6, "ST4 dynamic-f and static-f produce identical logits (mechanism broken)"
    print("[selftest] ST4 dynamic-f differs from static-f (mean_abs_diff=%.4e) OK" % diff, flush=True)

    # ST5: joint_sweep returns finite metrics
    n_tok_st = 30
    n_v_sm = 6
    rng5 = np.random.default_rng(99)
    logits_syn = rng5.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_syn = rng5.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_log_st = np.log(np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32))
    nd = n_tok_st // 2
    jr = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                     nxt_syn[:nd], nxt_syn[nd:])
    assert math.isfinite(jr["bpc_best"]) and math.isfinite(jr["top1_acc"]) and math.isfinite(jr["mrr_at_10"]), (
        "ST5 joint_sweep non-finite metric")
    assert jr["n_dev"] > 0 and jr["n_test"] > 0, "ST5 n_dev / n_test == 0"
    print("[selftest] ST5 joint_sweep (bpc=%.3f top1=%.4f mrr=%.4f) OK" % (
        jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"]), flush=True)

    # ST6: LAMBDA_GRID excludes 0.0
    assert 0.0 not in LAMBDA_GRID, "ST6 LAMBDA_GRID must exclude 0.0 (Skunkworks META C7)"
    print("[selftest] ST6 LAMBDA_GRID excludes 0.0 OK", flush=True)

    # ST7: ARM_FCFG covers exactly the 6 arms and 3 static use same f_store==f_query
    assert set(ARM_FCFG.keys()) == set(ARMS), "ST7 ARM_FCFG keys != ARMS"
    for a in STATIC_ARMS:
        s, q = ARM_FCFG[a]
        assert s == q, "ST7 static arm %s must have f_store==f_query (got %f vs %f)" % (a, s, q)
    for a in DYNAMIC_ARMS:
        s, q = ARM_FCFG[a]
        assert s != q, "ST7 dynamic arm %s must have f_store != f_query (got %f vs %f)" % (a, s, q)
    print("[selftest] ST7 arm config split (3 static + 3 dynamic) OK", flush=True)

    # ST8: verdict gate (HARD_PASS path: dynamic beats best static by >= 0.10)
    def _mk_unit(bpcs: Dict[str, float], cvs: Dict[str, float] = None) -> Dict:
        by_arm = {}
        for arm in ARMS:
            by_arm[arm] = {
                "bpc_best": bpcs[arm], "top1_acc": 0.25, "mrr_at_10": 0.35,
                "best_T_for_bpc": 0.05, "best_lambda_for_bpc": 0.3,
                "best_dev_bpc": bpcs[arm],
                "raw_bpc_at_T1_L1": 8.5,
                "n_dev": 100, "n_test": 100,
                "elapsed_s_arm": 0.01,
                "f_store": ARM_FCFG[arm][0], "f_query": ARM_FCFG[arm][1],
            }
        return {"seed": 0, "by_arm": by_arm, "V": 4000, "N_DIM": 64,
                "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": 300,
                "run_mode": "smoke", "config_version": "selftest",
                "device": "cpu", "llm_forward_calls_at_inference": 0,
                "elapsed_s_seed": 0.01}

    # HARD_PASS: ARM_DYNAMIC_STORE002_QUERY050 = 7.18; best static = 7.30; lift +0.12 >= 0.10
    u_hp_a = _mk_unit({
        "ARM_STATIC_F_0p02": 7.32,
        "ARM_STATIC_F_0p05": 7.31,    # sanity rail near 7.3065
        "ARM_STATIC_F_0p50": 7.35,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.25,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.18,  # winner
        "ARM_DYNAMIC_STORE005_QUERY050": 7.24,
    })
    u_hp_b = _mk_unit({
        "ARM_STATIC_F_0p02": 7.33,
        "ARM_STATIC_F_0p05": 7.30,
        "ARM_STATIC_F_0p50": 7.36,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.26,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.19,
        "ARM_DYNAMIC_STORE005_QUERY050": 7.25,
    })
    u_hp_c = _mk_unit({
        "ARM_STATIC_F_0p02": 7.32,
        "ARM_STATIC_F_0p05": 7.31,
        "ARM_STATIC_F_0p50": 7.34,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.25,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.18,
        "ARM_DYNAMIC_STORE005_QUERY050": 7.24,
    })
    v, m, d = compute_verdict([u_hp_a, u_hp_b, u_hp_c])
    assert v == "HARD_PASS", "ST8 HARD_PASS got %s msg=%s" % (v, m[:200])
    print("[selftest] ST8 verdict HARD_PASS OK", flush=True)

    # ST9: CHAIN_GRADE_BONUS path (dynamic beats best static by >= 0.30)
    u_cg_a = _mk_unit({
        "ARM_STATIC_F_0p02": 7.32,
        "ARM_STATIC_F_0p05": 7.31,
        "ARM_STATIC_F_0p50": 7.34,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.20,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.00,  # +0.31 over best static 7.31
        "ARM_DYNAMIC_STORE005_QUERY050": 7.15,
    })
    u_cg_b = _mk_unit({
        "ARM_STATIC_F_0p02": 7.33,
        "ARM_STATIC_F_0p05": 7.30,
        "ARM_STATIC_F_0p50": 7.35,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.21,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.00,
        "ARM_DYNAMIC_STORE005_QUERY050": 7.16,
    })
    u_cg_c = _mk_unit({
        "ARM_STATIC_F_0p02": 7.32,
        "ARM_STATIC_F_0p05": 7.31,
        "ARM_STATIC_F_0p50": 7.34,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.20,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.00,
        "ARM_DYNAMIC_STORE005_QUERY050": 7.15,
    })
    v, m, d = compute_verdict([u_cg_a, u_cg_b, u_cg_c])
    assert v == "HARD_PASS", "ST9 CHAIN_GRADE_BONUS got %s msg=%s" % (v, m[:200])
    assert d.get("verdict_tier") == "CHAIN_GRADE_BONUS", "ST9 tier missing: %s" % d.get("verdict_tier")
    print("[selftest] ST9 verdict CHAIN_GRADE_BONUS OK", flush=True)

    # ST10: MIDDLE_BAND (lift in [+0.05, +0.10))
    u_mb_a = _mk_unit({
        "ARM_STATIC_F_0p02": 7.32,
        "ARM_STATIC_F_0p05": 7.31,
        "ARM_STATIC_F_0p50": 7.34,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.28,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.24,   # lift +0.07 over 7.31
        "ARM_DYNAMIC_STORE005_QUERY050": 7.27,
    })
    u_mb_b = _mk_unit({
        "ARM_STATIC_F_0p02": 7.32,
        "ARM_STATIC_F_0p05": 7.31,
        "ARM_STATIC_F_0p50": 7.34,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.28,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.24,
        "ARM_DYNAMIC_STORE005_QUERY050": 7.27,
    })
    u_mb_c = _mk_unit({
        "ARM_STATIC_F_0p02": 7.32,
        "ARM_STATIC_F_0p05": 7.31,
        "ARM_STATIC_F_0p50": 7.34,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.28,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.24,
        "ARM_DYNAMIC_STORE005_QUERY050": 7.27,
    })
    v, m, d = compute_verdict([u_mb_a, u_mb_b, u_mb_c])
    assert v == "MIDDLE_BAND", "ST10 MIDDLE_BAND got %s msg=%s" % (v, m[:200])
    print("[selftest] ST10 verdict MIDDLE_BAND OK", flush=True)

    # ST11: HARD_FAIL (all dynamic >= best static; no lift)
    u_hf_a = _mk_unit({
        "ARM_STATIC_F_0p02": 7.32,
        "ARM_STATIC_F_0p05": 7.31,    # best static
        "ARM_STATIC_F_0p50": 7.34,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.40,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.45,
        "ARM_DYNAMIC_STORE005_QUERY050": 7.50,
    })
    u_hf_b = _mk_unit({
        "ARM_STATIC_F_0p02": 7.32,
        "ARM_STATIC_F_0p05": 7.31,
        "ARM_STATIC_F_0p50": 7.34,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.40,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.45,
        "ARM_DYNAMIC_STORE005_QUERY050": 7.50,
    })
    u_hf_c = _mk_unit({
        "ARM_STATIC_F_0p02": 7.32,
        "ARM_STATIC_F_0p05": 7.31,
        "ARM_STATIC_F_0p50": 7.34,
        "ARM_DYNAMIC_STORE002_QUERY005": 7.40,
        "ARM_DYNAMIC_STORE002_QUERY050": 7.45,
        "ARM_DYNAMIC_STORE005_QUERY050": 7.50,
    })
    v, m, d = compute_verdict([u_hf_a, u_hf_b, u_hf_c])
    assert v == "HARD_FAIL", "ST11 HARD_FAIL got %s msg=%s" % (v, m[:200])
    print("[selftest] ST11 verdict HARD_FAIL OK", flush=True)

    # ST12: HARD_FAIL_PROVENANCE (sanity rail diverges in full mode)
    # We only check the sanity rail in run_mode=full; selftest is smoke so this
    # path isn't activated. Confirm the gate flag exists in detail.
    assert "sanity_rail_ok" in d, "ST12 sanity_rail_ok missing from detail"
    print("[selftest] ST12 sanity_rail_ok flag present in detail OK", flush=True)

    # ST13: LLM-call counter zero (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0, "ST13 LLM call counter non-zero: %d" % _LLM_CALL_COUNTER[0]
    print("[selftest] ST13 LLM call counter == 0 OK", flush=True)

    print("[selftest] ALL PASS (ST1-ST13)", flush=True)


# ============================================================================
# Verdict (per pre-reg bands)
# ============================================================================
def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}
    arm_bpc: Dict[str, float] = {}
    arm_cv: Dict[str, float] = {}

    for arm in ARMS:
        valid = [u for u in units
                 if math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))]
        if not valid:
            by_arm_agg[arm] = {"bpc_best_mean": float("inf"), "n_valid_seeds": 0,
                                "all_seeds_failed": True,
                                "f_store": ARM_FCFG[arm][0], "f_query": ARM_FCFG[arm][1]}
            arm_bpc[arm] = float("inf")
            arm_cv[arm] = float("nan")
            continue
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "n_valid_seeds": len(valid),
            "all_seeds_failed": False,
            "f_store": ARM_FCFG[arm][0],
            "f_query": ARM_FCFG[arm][1],
        }
        arm_bpc[arm] = b_mean
        arm_cv[arm] = b_cv

    # Best static-arm BPC (the bar to beat)
    static_bpcs = {a: arm_bpc[a] for a in STATIC_ARMS}
    best_static_arm = min(static_bpcs, key=static_bpcs.get)
    best_static_bpc = static_bpcs[best_static_arm]

    # Per-dynamic-arm lift over best static (positive = better)
    dynamic_lifts: Dict[str, float] = {}
    for a in DYNAMIC_ARMS:
        if math.isfinite(arm_bpc[a]) and math.isfinite(best_static_bpc):
            dynamic_lifts[a] = best_static_bpc - arm_bpc[a]
        else:
            dynamic_lifts[a] = float("-inf")

    best_dynamic_arm = max(dynamic_lifts, key=dynamic_lifts.get) if dynamic_lifts else None
    best_dynamic_lift = dynamic_lifts.get(best_dynamic_arm, float("-inf"))
    best_dynamic_bpc = arm_bpc.get(best_dynamic_arm, float("inf"))
    best_dynamic_cv = arm_cv.get(best_dynamic_arm, float("nan"))

    # Sanity rail: ARM_STATIC_F_0p05 within +/-0.05 of fair_harness 7.3065
    sanity_bpc = arm_bpc.get(SANITY_RAIL_ARM, float("inf"))
    sanity_drift = abs(sanity_bpc - FAIR_HARNESS_REF_BPC) if math.isfinite(sanity_bpc) else float("inf")
    sanity_rail_ok = sanity_drift <= SANITY_RAIL_TOL

    # cv check on best dynamic arm
    cv_ok = math.isfinite(best_dynamic_cv) and best_dynamic_cv <= CV_MAX

    # Substrate-only audit
    total_llm_calls = sum(int(u.get("llm_forward_calls_at_inference", 0)) for u in units)

    # Per-arm summary line (Fix #28: per-arm only; no cross-arm framing here)
    arm_lines = []
    for a in ARMS:
        x = by_arm_agg[a]
        if x.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % a)
            continue
        arm_lines.append("%s(fs=%.2f,fq=%.2f)=bpc%.4f|cv%.3f|top1%.4f|mrr%.4f" % (
            a, x["f_store"], x["f_query"], x["bpc_best_mean"], x["bpc_best_cv"],
            x["top1_acc_mean"], x["mrr_at_10_mean"]))
    arm_summary = " | ".join(arm_lines)

    summary = ("DYNAMIC_F best_static=%s(%.4f) best_dynamic=%s(%.4f) "
               "lift=%+.3f sanity=%s(drift=%+.4f) | %s | n_llm=%d") % (
        best_static_arm, best_static_bpc,
        best_dynamic_arm if best_dynamic_arm else "NONE", best_dynamic_bpc,
        best_dynamic_lift, str(sanity_rail_ok), sanity_drift,
        arm_summary, total_llm_calls,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "best_static_arm": best_static_arm,
        "best_static_bpc": round(best_static_bpc, 4) if math.isfinite(best_static_bpc) else None,
        "best_dynamic_arm": best_dynamic_arm,
        "best_dynamic_bpc": round(best_dynamic_bpc, 4) if math.isfinite(best_dynamic_bpc) else None,
        "best_dynamic_lift": round(best_dynamic_lift, 4) if math.isfinite(best_dynamic_lift) else None,
        "best_dynamic_cv": round(best_dynamic_cv, 4) if math.isfinite(best_dynamic_cv) else None,
        "dynamic_lifts_per_arm": {a: (round(l, 4) if math.isfinite(l) else None)
                                    for a, l in dynamic_lifts.items()},
        "sanity_rail_arm": SANITY_RAIL_ARM,
        "sanity_rail_bpc": round(sanity_bpc, 4) if math.isfinite(sanity_bpc) else None,
        "sanity_rail_drift": round(sanity_drift, 4) if math.isfinite(sanity_drift) else None,
        "sanity_rail_ok": bool(sanity_rail_ok),
        "fair_harness_ref_bpc": FAIR_HARNESS_REF_BPC,
        "sanity_rail_tol": SANITY_RAIL_TOL,
        "hard_pass_lift_bpc": HARD_PASS_LIFT_BPC,
        "chain_grade_bonus_lift_bpc": CHAIN_GRADE_BONUS_LIFT_BPC,
        "middle_band_lift_low": MIDDLE_BAND_LIFT_LOW,
        "middle_band_lift_high": MIDDLE_BAND_LIFT_HIGH,
        "cv_max": CV_MAX,
        "cv_ok_for_best_dynamic": bool(cv_ok),
        "n_seeds": len(units),
        "llm_forward_calls_total": int(total_llm_calls),
        "config_version": CONFIG_VERSION,
        "honest_scope": (
            "6-arm dynamic-f phase-shift sparsity cell on fair_harness scaffolding "
            "(torch.cuda; word2vec encoder; rank-1 Hebbian). N_DIM=%d N_TRAIN=%d N_HELD=%d "
            "V=%d seeds=%s. Static arms ARM_STATIC_F_0p02/0p05/0p50 vary uniform f across "
            "store and query. Dynamic arms vary f BETWEEN store and query phases. "
            "ARM_STATIC_F_0p05 acts as sanity rail vs fair_harness ref 7.3065." % (
                N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, SEEDS)),
        "WHAT_THIS_DOES_NOT_SHOW": (
            "Does NOT test continuous-f modulation (only 2 fixed phases). "
            "Does NOT test query-difficulty gated f-switching (no adaptive f). "
            "Does NOT test 3+ phase modes. Does NOT vary f_store across trajectory. "
            "Result at text8 N_TRAIN=100k V=4000 may not generalize."),
        "cites": [
            "preregs/2026-06-24_substrate_dynamic_f_phase_shift_sparsity_v1.md",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
            "experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py",
            "experiments/exp_substrate_ACh_query_conditional_read_gain_LM_v1.py",
        ],
    }

    # Gate 1: substrate-only invariant
    if total_llm_calls != 0:
        return ("HARD_FAIL",
                "HARD_FAIL: LLM_CALL_VIOLATION llm_calls=%d (substrate-only). %s" % (
                    total_llm_calls, summary),
                detail)

    # Gate 2: any arm all-seeds-failed
    failed_arms = [a for a in ARMS if by_arm_agg[a].get("all_seeds_failed", False)]
    if failed_arms:
        return ("HARD_FAIL",
                "HARD_FAIL: arms all_seeds_failed=%s. %s" % (failed_arms, summary),
                detail)

    # Gate 3: sanity rail (only active in full mode; smoke V/N differ structurally)
    detail["provenance_check_active"] = (RUN_MODE == "full")
    if RUN_MODE == "full" and not sanity_rail_ok:
        return ("HARD_FAIL_PROVENANCE",
                "HARD_FAIL_PROVENANCE: %s=%.4f drifts %.4f from fair_harness ref %.4f (>tol %.2f). %s" % (
                    SANITY_RAIL_ARM, sanity_bpc, sanity_drift, FAIR_HARNESS_REF_BPC,
                    SANITY_RAIL_TOL, summary),
                detail)

    # Gate 4: CHAIN_GRADE_BONUS (lift >= 0.30)
    if best_dynamic_lift >= CHAIN_GRADE_BONUS_LIFT_BPC and cv_ok:
        detail["verdict_tier"] = "CHAIN_GRADE_BONUS"
        return ("HARD_PASS",
                "HARD_PASS CHAIN_GRADE_BONUS: %s lift=%+.3f >= +%.2f over %s (cv=%.3f<=%.2f). "
                "Substrate-novel phase-shift mode-switching unlocked at fair_harness scale. %s" % (
                    best_dynamic_arm, best_dynamic_lift, CHAIN_GRADE_BONUS_LIFT_BPC,
                    best_static_arm, best_dynamic_cv, CV_MAX, summary),
                detail)

    # Gate 5: HARD_PASS (lift >= 0.10)
    if best_dynamic_lift >= HARD_PASS_LIFT_BPC and cv_ok:
        detail["verdict_tier"] = "HARD_PASS_DYNAMIC_F"
        return ("HARD_PASS",
                "HARD_PASS: %s lift=%+.3f >= +%.2f over %s (cv=%.3f<=%.2f). "
                "Dynamic f-phase-shift produces super-static lift. %s" % (
                    best_dynamic_arm, best_dynamic_lift, HARD_PASS_LIFT_BPC,
                    best_static_arm, best_dynamic_cv, CV_MAX, summary),
                detail)

    # Gate 6: HARD_PASS bar met BUT cv too high -> MIDDLE_BAND_HIGH_CV
    if best_dynamic_lift >= HARD_PASS_LIFT_BPC and not cv_ok:
        detail["verdict_tier"] = "MIDDLE_BAND_HIGH_CV"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_HIGH_CV: %s lift=%+.3f >= +%.2f BUT cv=%.3f > %.2f. %s" % (
                    best_dynamic_arm, best_dynamic_lift, HARD_PASS_LIFT_BPC,
                    best_dynamic_cv if math.isfinite(best_dynamic_cv) else -1.0,
                    CV_MAX, summary),
                detail)

    # Gate 7: MIDDLE_BAND (lift in [+0.05, +0.10))
    if MIDDLE_BAND_LIFT_LOW <= best_dynamic_lift < MIDDLE_BAND_LIFT_HIGH:
        detail["verdict_tier"] = "MIDDLE_BAND_PARTIAL_LIFT"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: %s lift=%+.3f in [%+.2f, %+.2f). "
                "Partial mode-switch lift; below HARD_PASS bar. %s" % (
                    best_dynamic_arm, best_dynamic_lift, MIDDLE_BAND_LIFT_LOW,
                    MIDDLE_BAND_LIFT_HIGH, summary),
                detail)

    # Gate 8: HARD_FAIL (lift < +0.05, no dynamic arm beats static)
    detail["verdict_tier"] = "NO_PHASE_SHIFT_LIFT"
    return ("HARD_FAIL",
            "HARD_FAIL: best dynamic %s lift=%+.3f < +%.2f over best static %s. "
            "No phase-shift mode-switching at this configuration. %s" % (
                best_dynamic_arm if best_dynamic_arm else "NONE", best_dynamic_lift,
                MIDDLE_BAND_LIFT_LOW, best_static_arm, summary),
            detail)


# Run selftest BEFORE any heavy compute (gates --self-test exit)
_instrumentation_selftest()

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
        print("[WARN] corpus short: %d tokens" % len(toks), flush=True)
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

    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]), flush=True)

    # Build BASE encoder ONCE per seed (word2vec -> Gaussian-project -> L2)
    print("[seed=%d] building base word2vec encoder (V=%d, N_DIM=%d)..." % (
        seed, V, N_DIM), flush=True)
    t_enc0 = time.time()
    E_base, w2v_meta = build_E_base_word2vec(vocab, N_DIM, seed)
    t_enc = time.time() - t_enc0
    print("[seed=%d] base encoder built in %.1fs; hit=%d/%d fallback=%s" % (
        seed, t_enc, w2v_meta.get("n_hit", -1), w2v_meta.get("n_vocab", -1),
        w2v_meta.get("fallback_to_char_trigram", False)), flush=True)

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    # Eval-pair domain (ctx != UNK)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    n_eval = len(nxt_eval)
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni, "w2v_meta": w2v_meta}

    for arm in ARMS:
        f_store, f_query = ARM_FCFG[arm]
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] f_store=%.2f f_query=%.2f computing..." % (
            seed, arm, f_store, f_query), flush=True)
        try:
            ar = build_logits_dynamic_f_gpu(
                E_base, f_store=f_store, f_query=f_query,
                idx_train_t=idx_train_t, idx_held_t=idx_held_t,
                recall_batch=RECALL_BATCH, ingest_chunk=INGEST_CHUNK,
            )
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "f_store": f_store, "f_query": f_query,
            }
            continue

        logits_full = ar["logits"]
        if logits_full.shape[0] >= len(ctx_full):
            logits_eval = logits_full[:len(ctx_full)][mask]
        else:
            valid_pos = np.where(mask)[0]
            valid_pos = valid_pos[valid_pos < logits_full.shape[0]]
            logits_eval = logits_full[valid_pos]

        jr = joint_sweep(logits_eval[:n_dev], logits_eval[n_dev:],
                         U_log, nxt_dev, nxt_test)
        rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval)
        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_sparsify_s": ar.get("wall_sparsify_s", 0.0),
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "f_store": f_store,
            "f_query": f_query,
        })
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.4f top1=%.4f mrr=%.4f rawT1=%.3f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
            jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)

    del E_base
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "run_mode": RUN_MODE,
        "device": str(DEVICE),
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
    }


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
        elapsed = (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "anchor": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_dynamic_f_phase_shift_v1",
            "per_unit": units,
            "elapsed_s": elapsed,
            "summary": "[atexit-synthesize %d/%d] %s" % (len(units), len(SEEDS), msg[:200]),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
            "config_version": CONFIG_VERSION,
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
# Main loop
# ============================================================================
if __name__ == "__main__":
    print("[config] %s" % CONFIG_VERSION, flush=True)
    print("[config] device=%s torch_cuda_available=%s" % (
        str(DEVICE), torch.cuda.is_available()), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass

    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM, "schema": "dynamic-f-phase-shift-v1"}
    t0 = time.time()
    _T0_REF[0] = t0

    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        result = run_unit(seed)
        write_partial_key(out_dir, key, result)
        print("[ckpt] %s partial written" % key, flush=True)

    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS],
                                       run_config=run_cfg).values())
    verdict, verdict_msg, detail = compute_verdict(units)
    print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

    summary_str = (
        "%s | arms=%d seeds=%d N_DIM=%d N_TRAIN=%d encoder=word2vec dynamic_f" % (
            verdict, len(ARMS), len(SEEDS), N_DIM, N_TRAIN))

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": summary_str,
        "config_version": CONFIG_VERSION,
        "run_mode": RUN_MODE,
        "device": str(DEVICE),
        "N_DIM": N_DIM,
        "N": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH,
        "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID,
        "MRR_K": MRR_K,
        "SEEDS": SEEDS,
        "ARMS": ARMS,
        "ARM_FCFG": {a: list(fc) for a, fc in ARM_FCFG.items()},
        "detail": detail,
        "metrics_source": "measured_gpu_dynamic_f_phase_shift_v1",
        "per_unit": units,
        "n_seeds": len(units),
        "elapsed_s": time.time() - t0,
        "substrate_only_decode_gate": "TRUE (substrate cosine logits; word2vec static lookup; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
