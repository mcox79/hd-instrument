"""substrate_encoder_ablation_on_fair_harness_v1 -- METHODOLOGY ABLATION CELL.

PURPOSE (2026-06-24):
  Resolve the 3-cell-replicated 7.2268 vs fair_harness 7.3065 finding. The two
  numbers measure DIFFERENT QUANTITIES on DIFFERENT METHODOLOGIES, not a real
  +0.08 BPC lift. Research drill identified three candidate factors:
    (1) encoder family (word2vec sparse-bipolar f=0.05 vs char-trigram dense)
    (2) ctx-unk filter (fair_harness masks ctx==<unk>; cleanup-cells does not)
    (3) alpha-Laplace smoothing on unigram floor (fair=0.1, cleanup=+1.0)
  This cell ablates each axis independently on a single unified pipeline.

  Substrate-product reading: if char-trigram dense (arm C) reproduces 7.22
  with the fair_harness ctx-unk filter, the canonical chain-grade rail moves
  from 7.30 to 7.22 and all cf-RPE / STDP / heterogeneous-plasticity deltas
  must be re-tiered.

FIVE ARMS (each builds FRESH W from same corpus split; same N_DIM, same seed=7):
  A_FAIR_HARNESS_ASSHIPPED
      word2vec encoder + sparse-bipolar f=0.05 + ctx-unk filter + alpha=0.1
      Sanity rail: should land within +/-0.05 of fair_harness reference 7.3065
  B_W2V_DENSE_NO_SPARSIFY
      word2vec encoder + DENSE bipolar (sign-binarize only; no f=0.05 topk)
      + ctx-unk filter + alpha=0.1. Predicted 7.15-7.25.
  C_CHAR_TRIGRAM_DENSE_FAIR_FILTER
      char-trigram dense encoder (cleanup-cells family) + ctx-unk filter
      + alpha=0.1. Predicted 7.18-7.25. DECISIVE for canonical-rail flip.
  D_W2V_SPARSE_NO_FILTER
      fair_harness as-shipped but NO ctx-unk filter, alpha=0.1.
      Predicted 7.32-7.36 (filter is small effect).
  E_CHAR_TRIGRAM_NO_FILTER_ALPHA1
      char-trigram dense + NO filter + alpha=1.0 (cleanup-cells as-shipped).
      Sanity rail: should land within +/-0.05 of cleanup-cells reference 7.2268.

PRE-REGISTERED BANDS (PRE-REGISTERED BEFORE RUN, 2026-06-24):
  HARD_PASS_METHODOLOGY_RESOLVED:
      sanity rail A is within +/-0.05 of 7.3065 AND
      sanity rail E is within +/-0.05 of 7.2268 AND
      arm C lands within +/-0.05 of EITHER 7.22 OR 7.30
      => the methodology gap is fully attributed; canonical rail decided by
      whichever end-point C lands on.
  CHAIN_GRADE_BONUS_RAIL_FLIP:
      arm B BPC <= 7.25 (sparsification was hurting; canonical rail moves to
      ~7.20). This is the productively-actionable outcome.
  MIDDLE_BAND:
      Geometrically unreachable given the +/-0.05 tolerances around two refs
      that are only 0.08 apart (intervals [7.18,7.27] and [7.26,7.36] cover
      [7.18,7.36] entirely; their overlap [7.26,7.27] is treated as
      "consistent with either rail" => HARD_PASS). Retained as a defensive
      catch-all should rails partially reproduce in an unexpected pattern.
  HARD_FAIL:
      EITHER sanity rail diverges by >0.10 (harness bug; cannot conclude)
      OR arm C lands outside [7.18, 7.35] (4th unidentified factor:
      W normalization, batch precision, dtype, etc.) ... action = drill again

CRITICAL DISCIPLINES:
  PURE NUMPY: routes via remote_cpu_queue; no torch import
  ASCII-only, no emojis, no em dashes
  Fix #28: per-arm metrics ONLY; no cross-arm narrative in verdict_msg
  WHAT_THIS_DOES_NOT_SHOW clause in detail
  All 5 arms use SAME unigram_floor split + SAME held positions; only the
    (encoder, sparsify, filter, alpha) tuple varies per arm.
  Single seed=7 sufficient (drill says): deterministic pipelines + sanity
    rails act as their own cross-check.

CITES:
  notes/research_surprise_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md
  notes/exp_dev_handoff_research_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md
  experiments/exp_fair_harness_substrate_as_lm_v1.py (fair-harness canonical 7.3065)
  experiments/exp_substrate_multi_iteration_cleanup_LM_v1.py (cleanup-cells 7.2268)
  preregs/2026-06-24_substrate_encoder_ablation_on_fair_harness_v1.md

PROT-018: no _nN suffix; production N_DIM=8192 stated below + in prereg.
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
import atexit
import hashlib
import math
import signal
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np

# NO torch import -- pure numpy for remote_cpu_queue (PROT-020 avoidance)

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "substrate_encoder_ablation_on_fair_harness_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Reference baselines (PROVENANCE-tagged: what each rail measures)
FAIR_HARNESS_REF_BPC = 7.3065     # provenance: fair_harness V2 HARD_PASS arm sparse_bipolar
CLEANUP_CELLS_REF_BPC = 7.2268    # provenance: multi_iter / tanh / cue_clamped ARM_BASELINE_NO_CLEANUP

# Pre-reg bands
SANITY_RAIL_TOL = 0.05
ARM_C_CENTER_TOL = 0.05
HARD_FAIL_RAIL_TOL = 0.10
HARD_FAIL_ARM_C_MIN = 7.18
HARD_FAIL_ARM_C_MAX = 7.35
CHAIN_GRADE_BONUS_B_MAX = 7.25

# Joint (T, lambda) sweep grid (matches fair_harness)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Sparse-bipolar fraction
SPARSE_BIPOLAR_F = 0.05

# CLI
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 512
WORD2VEC_MODEL = "word2vec-google-news-300"
PRETRAIN_DIM = 300

if RUN_MODE == "full":
    SEEDS = [7]
    N_DIM = 8192
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke: <90s on laptop CPU; exercises every arm + joint sweep + 5x verdict bands
    SEEDS = [0]
    N_DIM = 512
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

ARMS = [
    "A_FAIR_HARNESS_ASSHIPPED",
    "B_W2V_DENSE_NO_SPARSIFY",
    "C_CHAR_TRIGRAM_DENSE_FAIR_FILTER",
    "D_W2V_SPARSE_NO_FILTER",
    "E_CHAR_TRIGRAM_NO_FILTER_ALPHA1",
]

# Per-arm (encoder, sparsify, filter, alpha) tuple. PROVENANCE-tagged.
ARM_CONFIG: Dict[str, Dict] = {
    "A_FAIR_HARNESS_ASSHIPPED":         {"encoder": "word2vec",    "sparsify": True,  "filter_unk": True,  "alpha": 0.1},
    "B_W2V_DENSE_NO_SPARSIFY":          {"encoder": "word2vec",    "sparsify": False, "filter_unk": True,  "alpha": 0.1},
    "C_CHAR_TRIGRAM_DENSE_FAIR_FILTER": {"encoder": "char_trigram","sparsify": False, "filter_unk": True,  "alpha": 0.1},
    "D_W2V_SPARSE_NO_FILTER":           {"encoder": "word2vec",    "sparsify": True,  "filter_unk": False, "alpha": 0.1},
    "E_CHAR_TRIGRAM_NO_FILTER_ALPHA1":  {"encoder": "char_trigram","sparsify": False, "filter_unk": False, "alpha": 1.0},
}

CONFIG_VERSION = (
    "substrate_encoder_ablation_on_fair_harness_v1; "
    "N_DIM=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s mode=%s "
    "sparse_f=%.3f temps=%s lambdas=%s MRR_K=%d "
    "bands rail_tol=%.2f arm_c_tol=%.2f bonus_B_max=%.2f hf_C_range=[%.2f,%.2f]"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    SPARSE_BIPOLAR_F, TEMP_GRID, LAMBDA_GRID, MRR_K,
    SANITY_RAIL_TOL, ARM_C_CENTER_TOL, CHAIN_GRADE_BONUS_B_MAX,
    HARD_FAIL_ARM_C_MIN, HARD_FAIL_ARM_C_MAX,
)

_LLM_CALL_COUNTER = [0]


# ============================================================================
# Char-trigram encoder (pure numpy; matches cleanup-cells reference)
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


def build_E_char_trigram(vocab: List[str], n_dim: int, seed: int) -> np.ndarray:
    E = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    return l2_normalize_np(E)


def l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        n = np.linalg.norm(X)
        return X / max(n, eps)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(norms < eps, 1.0, norms)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    return rng.standard_normal((out_dim, in_dim)).astype(np.float32) / np.sqrt(float(in_dim))


# ============================================================================
# word2vec encoder (pure numpy via gensim helper; char-trigram OOV fallback)
# ============================================================================

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


def build_E_word2vec(vocab: List[str], n_dim: int, seed: int
                      ) -> Tuple[np.ndarray, Dict]:
    """word2vec lookup -> Gaussian projection -> L2-normalize. OOV via char-trigram."""
    try:
        kv = _load_gensim_kv(WORD2VEC_MODEL)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[encoder] WORD2VEC LOAD FAIL: %s -- falling back to char-trigram" % err, flush=True)
        E = build_E_char_trigram(vocab, n_dim, seed)
        return E, {"fallback_to_char_trigram": True, "load_error": err,
                    "n_hit": 0, "n_miss": len(vocab), "pretrain_dim": -1}
    E_pre, n_hit, n_miss = _embed_vocab_via_gensim(vocab, kv)
    E_pre_n = l2_normalize_np(E_pre)
    P = _gaussian_projection(in_dim=kv.vector_size, out_dim=n_dim, seed=seed)
    E_proj = (E_pre_n @ P.T).astype(np.float32)
    norms_pre = np.linalg.norm(E_pre, axis=1)
    oov_mask = norms_pre < 1e-9
    if oov_mask.any():
        for i in np.where(oov_mask)[0]:
            E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = l2_normalize_np(E_proj)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size),
            "fallback_to_char_trigram": False}
    return E_proj, meta


# ============================================================================
# Sparse-bipolar primitive (top-k by abs; sign-binarize; matches fair_harness)
# ============================================================================

def sparsify_bipolar_np(E: np.ndarray, f: float) -> np.ndarray:
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    abs_E = np.abs(E)
    topk_idx = np.argpartition(-abs_E, kth=k - 1, axis=1)[:, :k]
    out = np.zeros_like(E)
    rows = np.arange(V)[:, None]
    signs = np.sign(E[rows, topk_idx])
    signs = np.where(signs == 0, 1.0, signs)
    out[rows, topk_idx] = signs.astype(E.dtype)
    return out


# ============================================================================
# Hebbian W builder (rank-1; pure numpy, chunked)
# ============================================================================

def build_rank1_W_np(idx_train: np.ndarray, E: np.ndarray, chunk: int) -> np.ndarray:
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, chunk):
        end = min(b + chunk, n_pairs)
        src = E[idx_train[b:end]]
        tgt = E[idx_train[b + 1:end + 1]]
        W += tgt.T @ src
    return W


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


def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


# ============================================================================
# Joint (T, lambda) sweep + BPC / top-1 / MRR
# ============================================================================

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
    top_sorted = top_idx[rows, order]
    rr = 0.0
    for i in range(n):
        match = np.where(top_sorted[i] == nxt[i])[0]
        if len(match) > 0:
            rr += 1.0 / float(match[0] + 1)
    return float(rr / n)


def joint_sweep(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                 U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                 temp_grid: list, lambda_grid: list, mrr_k: int) -> Dict:
    """Joint (T, lambda) sweep on dev; pick best per-metric; report on test."""
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)

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

    def _test_metric(T, lam, fn):
        probs_test = softmax_logits_with_T(sub_logits_test, T)
        logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
        logp_test = log_linear_interp_logp(logp_sub_test, U_log, lam)
        return fn(logp_test, nxt_test)

    bpc_best = _test_metric(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best = _test_metric(best_top1["T"], best_top1["lambda"], top1_acc_from_logp)
    mrr_best = _test_metric(best_mrr["T"], best_mrr["lambda"],
                              lambda lp, nx: mrr_at_k(lp, nx, mrr_k))

    return {
        "bpc_best": round(bpc_best, 4),
        "best_T_for_bpc": best_bpc["T"],
        "best_lambda_for_bpc": best_bpc["lambda"],
        "best_dev_bpc": round(best_bpc["dev_value"], 4),
        "top1_acc": round(top1_best, 4),
        "mrr_at_10": round(mrr_best, 4),
        "raw_bpc_at_T1_L1": round(raw_bpc_at_T1_L1, 4),
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
    }


# ============================================================================
# Per-arm runner
# ============================================================================

def compute_arm_logits(E_used: np.ndarray, idx_train: np.ndarray,
                        idx_held: np.ndarray) -> np.ndarray:
    """Build rank-1 W from idx_train; recall on idx_held positions.

    Returns [n_held - 0, V] logits where row p predicts NEXT token given idx_held[p].
    We produce logits at positions 0 .. len(idx_held)-2 (last has no nxt).
    Returned shape: [len(idx_held)-1, V].
    """
    V, dim = E_used.shape
    W = build_rank1_W_np(idx_train, E_used, INGEST_CHUNK)
    n_ctx = len(idx_held) - 1
    logits = np.zeros((n_ctx, V), dtype=np.float32)
    E_norm = l2_normalize_np(E_used)
    for b in range(0, n_ctx, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_ctx)
        src = E_used[idx_held[b:end]]
        query = src @ W.T
        query = l2_normalize_np(query)
        logits[b:end] = query @ E_norm.T
    return logits


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
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d" % (
        seed, V, N_TRAIN, N_HELD, N_DIM), flush=True)

    # Build BOTH encoders once; reuse across arms
    print("[seed=%d] building word2vec base E (V=%d, N_DIM=%d)..." % (
        seed, V, N_DIM), flush=True)
    t0 = time.time()
    E_w2v, w2v_meta = build_E_word2vec(vocab, N_DIM, seed)
    t_w2v = time.time() - t0
    print("[seed=%d] word2vec E built (%.1fs) hit=%d miss=%d fallback=%s" % (
        seed, t_w2v, w2v_meta.get("n_hit", -1), w2v_meta.get("n_miss", -1),
        w2v_meta.get("fallback_to_char_trigram", False)), flush=True)

    print("[seed=%d] building char-trigram base E (V=%d, N_DIM=%d)..." % (
        seed, V, N_DIM), flush=True)
    t0 = time.time()
    E_ct = build_E_char_trigram(vocab, N_DIM, seed)
    t_ct = time.time() - t0
    print("[seed=%d] char-trigram E built (%.1fs)" % (seed, t_ct), flush=True)

    # Pre-build sparse versions where needed (cache once)
    E_w2v_sparse = l2_normalize_np(sparsify_bipolar_np(E_w2v, SPARSE_BIPOLAR_F))
    print("[seed=%d] word2vec SPARSE_F=%.3f variant prepared" % (seed, SPARSE_BIPOLAR_F), flush=True)

    # Held position bookkeeping
    unk = w2i["<unk>"]
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask_unk_filter = (ctx_full != unk)

    by_arm: Dict[str, Dict] = {}
    for arm in ARMS:
        cfg = ARM_CONFIG[arm]
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] cfg=%s" % (seed, arm, cfg), flush=True)

        # Select encoder
        if cfg["encoder"] == "word2vec":
            if cfg["sparsify"]:
                E_used = E_w2v_sparse
            else:
                E_used = E_w2v
        elif cfg["encoder"] == "char_trigram":
            E_used = E_ct
        else:
            raise ValueError("bad encoder spec %r" % cfg["encoder"])

        # Build unigram per-arm-alpha
        U = build_unigram_np(idx_train, V=V, alpha=cfg["alpha"])
        U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

        # Logits over all ctx positions
        try:
            logits_full = compute_arm_logits(E_used, idx_train, idx_held)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"),
                "raw_bpc_at_T1_L1": float("inf"),
                "best_T_for_bpc": float("nan"),
                "best_lambda_for_bpc": float("nan"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "config": cfg,
            }
            continue

        # Apply (or not) the ctx-unk filter
        if cfg["filter_unk"]:
            logits_eval = logits_full[mask_unk_filter]
            nxt_eval = nxt_full[mask_unk_filter]
        else:
            logits_eval = logits_full
            nxt_eval = nxt_full
        n_eval = len(nxt_eval)
        if n_eval < 2:
            by_arm[arm] = {"empty_eval": True, "config": cfg,
                            "bpc_best": float("inf"), "top1_acc": float("nan"),
                            "mrr_at_10": float("nan"),
                            "raw_bpc_at_T1_L1": float("inf"),
                            "best_T_for_bpc": float("nan"),
                            "best_lambda_for_bpc": float("nan"),
                            "elapsed_s_arm": round(time.time() - t_arm0, 2)}
            continue
        n_dev = n_eval // 2
        jr = joint_sweep(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_eval[:n_dev], nxt_eval[n_dev:],
            TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["config"] = cfg
        jr["n_eval_total"] = int(n_eval)
        jr["n_held_ctx"] = int(len(ctx_full))
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.4f top1=%.4f mrr=%.4f "
              "(bestT=%.4f bestL=%.2f) raw_T1L1_bpc=%.3f n_eval=%d" % (
                  seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                  jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                  jr["raw_bpc_at_T1_L1"], n_eval), flush=True)

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
        "device": "cpu",
        "encoder_meta": w2v_meta,
        "n_llm_calls": 0,
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    # Aggregate per-arm (single seed in this cell; mean = value, std = 0)
    by_arm_agg: Dict[str, Dict] = {}
    for arm in ARMS:
        rows = [u["by_arm"].get(arm, {}) for u in units]
        valid = [r for r in rows if r and math.isfinite(r.get("bpc_best", float("inf")))]
        if not valid:
            by_arm_agg[arm] = {"all_seeds_failed": True,
                                 "bpc_best_mean": float("inf"),
                                 "top1_acc_mean": float("nan"),
                                 "mrr_at_10_mean": float("nan"),
                                 "raw_bpc_at_T1_L1_mean": float("nan")}
            continue
        bpc_vals = [r["bpc_best"] for r in valid]
        top1_vals = [r["top1_acc"] for r in valid]
        mrr_vals = [r["mrr_at_10"] for r in valid]
        raw_vals = [r["raw_bpc_at_T1_L1"] for r in valid]
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_acc_mean": round(float(np.mean(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_vals)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_vals)), 4),
            "best_T_for_bpc_mean": round(float(np.mean([r["best_T_for_bpc"] for r in valid])), 4),
            "best_lambda_for_bpc_mean": round(float(np.mean([r["best_lambda_for_bpc"] for r in valid])), 4),
            "n_valid_seeds": int(len(valid)),
            "all_seeds_failed": False,
            "config": valid[0].get("config", {}),
        }

    # Pre-reg gate decisions (per-arm, NOT cross-arm framing)
    a_bpc = by_arm_agg["A_FAIR_HARNESS_ASSHIPPED"]["bpc_best_mean"]
    b_bpc = by_arm_agg["B_W2V_DENSE_NO_SPARSIFY"]["bpc_best_mean"]
    c_bpc = by_arm_agg["C_CHAR_TRIGRAM_DENSE_FAIR_FILTER"]["bpc_best_mean"]
    d_bpc = by_arm_agg["D_W2V_SPARSE_NO_FILTER"]["bpc_best_mean"]
    e_bpc = by_arm_agg["E_CHAR_TRIGRAM_NO_FILTER_ALPHA1"]["bpc_best_mean"]

    rail_A_ok = (math.isfinite(a_bpc) and abs(a_bpc - FAIR_HARNESS_REF_BPC) <= SANITY_RAIL_TOL)
    rail_E_ok = (math.isfinite(e_bpc) and abs(e_bpc - CLEANUP_CELLS_REF_BPC) <= SANITY_RAIL_TOL)
    rail_A_diverge = (math.isfinite(a_bpc) and abs(a_bpc - FAIR_HARNESS_REF_BPC) > HARD_FAIL_RAIL_TOL)
    rail_E_diverge = (math.isfinite(e_bpc) and abs(e_bpc - CLEANUP_CELLS_REF_BPC) > HARD_FAIL_RAIL_TOL)
    arm_C_in_range = (math.isfinite(c_bpc) and HARD_FAIL_ARM_C_MIN <= c_bpc <= HARD_FAIL_ARM_C_MAX)
    arm_C_near_fair = (math.isfinite(c_bpc) and abs(c_bpc - FAIR_HARNESS_REF_BPC) <= ARM_C_CENTER_TOL)
    arm_C_near_clean = (math.isfinite(c_bpc) and abs(c_bpc - CLEANUP_CELLS_REF_BPC) <= ARM_C_CENTER_TOL)
    bonus_rail_flip = (math.isfinite(b_bpc) and b_bpc <= CHAIN_GRADE_BONUS_B_MAX)

    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    arm_lines = []
    for a in ARMS:
        x = by_arm_agg[a]
        if x.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % a)
            continue
        arm_lines.append("%s=bpc%.4f|top1%.4f|mrr%.4f|rawT1%.3f" % (
            a, x["bpc_best_mean"], x["top1_acc_mean"],
            x["mrr_at_10_mean"], x["raw_bpc_at_T1_L1_mean"]))
    summary = "ENC_ABLATION %s | n_llm=%d" % (" | ".join(arm_lines), n_llm)

    detail = {
        "by_arm_agg": by_arm_agg,
        "rail_A_ok": bool(rail_A_ok),
        "rail_E_ok": bool(rail_E_ok),
        "rail_A_diverge": bool(rail_A_diverge),
        "rail_E_diverge": bool(rail_E_diverge),
        "arm_C_in_range": bool(arm_C_in_range),
        "arm_C_near_fair_harness": bool(arm_C_near_fair),
        "arm_C_near_cleanup_cells": bool(arm_C_near_clean),
        "bonus_chain_grade_rail_flip": bool(bonus_rail_flip),
        "FAIR_HARNESS_REF_BPC": FAIR_HARNESS_REF_BPC,
        "CLEANUP_CELLS_REF_BPC": CLEANUP_CELLS_REF_BPC,
        "SANITY_RAIL_TOL": SANITY_RAIL_TOL,
        "ARM_C_CENTER_TOL": ARM_C_CENTER_TOL,
        "CHAIN_GRADE_BONUS_B_MAX": CHAIN_GRADE_BONUS_B_MAX,
        "n_seeds": len(units),
        "n_llm_calls": int(n_llm),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "CONFIG_VERSION": CONFIG_VERSION,
        "WHAT_THIS_DOES_NOT_SHOW": (
            "This cell does NOT claim a substrate-as-LM advance; it ATTRIBUTES "
            "the prior 7.22 vs 7.30 methodology delta to one of three axes "
            "(encoder family, ctx-unk filter, alpha-Laplace). It is a calibration "
            "cell, not a science cell. Downstream cf-RPE / STDP / heterogeneous "
            "plasticity TIERING is the consumer of this result, not the cell's "
            "own claim."),
        "honest_scope": (
            "5-arm encoder-ablation cell on fair_harness scaffolding (pure numpy, "
            "rank-1 Hebbian, joint (T,lambda) sweep). N_DIM=%d N_TRAIN=%d N_HELD=%d "
            "V=%d seed=%s. Arm A (fair_harness as-shipped) and arm E (cleanup-cells "
            "as-shipped) act as sanity rails against 7.3065 and 7.2268 references. "
            "Arm C (char-trigram + fair-harness filter, alpha=0.1) decides whether "
            "encoder family or filter+alpha dominates the gap. Arm B tests whether "
            "removing sparsification yields a free BPC lift (chain-grade bonus)." %
            (N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, SEEDS)),
        "cites": [
            "notes/research_surprise_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md",
            "notes/exp_dev_handoff_research_baseline_7p22_vs_7p30_2x_drill_2026-06-24.md",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
            "experiments/exp_substrate_multi_iteration_cleanup_LM_v1.py",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    # HARD_FAIL: either sanity rail diverges OR arm C out of range
    if rail_A_diverge or rail_E_diverge or (not arm_C_in_range):
        why = []
        if rail_A_diverge:
            why.append("rail_A_diverge (A=%.4f vs ref %.4f tol %.2f)" % (
                a_bpc, FAIR_HARNESS_REF_BPC, HARD_FAIL_RAIL_TOL))
        if rail_E_diverge:
            why.append("rail_E_diverge (E=%.4f vs ref %.4f tol %.2f)" % (
                e_bpc, CLEANUP_CELLS_REF_BPC, HARD_FAIL_RAIL_TOL))
        if not arm_C_in_range:
            why.append("arm_C_out_of_range (C=%.4f notin [%.2f, %.2f])" % (
                c_bpc, HARD_FAIL_ARM_C_MIN, HARD_FAIL_ARM_C_MAX))
        return ("HARD_FAIL",
                "ENC_ABLATION HARD_FAIL: %s. %s" % ("; ".join(why), summary),
                detail)

    # HARD_PASS: both sanity rails OK AND arm C near either rail
    if rail_A_ok and rail_E_ok and (arm_C_near_fair or arm_C_near_clean):
        which = []
        if arm_C_near_clean:
            which.append("arm_C near cleanup-cells (%.4f vs ref %.4f)" % (
                c_bpc, CLEANUP_CELLS_REF_BPC))
        if arm_C_near_fair:
            which.append("arm_C near fair_harness (%.4f vs ref %.4f)" % (
                c_bpc, FAIR_HARNESS_REF_BPC))
        bonus = ""
        if bonus_rail_flip:
            bonus = " BONUS_CHAIN_GRADE_RAIL_FLIP: arm B (w2v dense no sparsify) bpc=%.4f <= %.2f -- removing f=0.05 sparsification gives a free lift; canonical rail can move to ~7.20." % (
                b_bpc, CHAIN_GRADE_BONUS_B_MAX)
        return ("HARD_PASS",
                "ENC_ABLATION HARD_PASS_METHODOLOGY_RESOLVED: sanity rails reproduce (A=%.4f near %.4f; E=%.4f near %.4f) AND %s.%s %s" % (
                    a_bpc, FAIR_HARNESS_REF_BPC, e_bpc, CLEANUP_CELLS_REF_BPC,
                    "; ".join(which), bonus, summary),
                detail)

    # MIDDLE_BAND (defensive catch-all): one or both rails partially reproduce
    # (within HARD_FAIL_RAIL_TOL but outside SANITY_RAIL_TOL) AND arm_C in range.
    # This is the only geometrically-reachable MIDDLE_BAND given the +/-0.05 tol
    # around references only 0.0797 apart -- intentional design.
    return ("MIDDLE_BAND",
            "ENC_ABLATION MIDDLE_BAND (defensive): rails partial; rail_A_ok=%s rail_E_ok=%s arm_C_in_range=%s A=%.4f B=%.4f C=%.4f D=%.4f E=%.4f. %s" % (
                rail_A_ok, rail_E_ok, arm_C_in_range,
                a_bpc, b_bpc, c_bpc, d_bpc, e_bpc, summary),
            detail)


# ============================================================================
# Self-test
# ============================================================================

def _selftest():
    # T1: char-trigram bipolar
    v = char_trigram_encode("hello", 64, seed=0)
    assert v.shape == (64,) and set(np.unique(v).tolist()).issubset({-1.0, 1.0}), "T1 trigram"

    # T2: sparsify primitive: exactly k=round(f*dim) nonzeros, bipolar values
    E = np.random.default_rng(0).standard_normal((4, 100)).astype(np.float32)
    sp = sparsify_bipolar_np(E, 0.05)
    k_expect = max(1, int(round(0.05 * 100)))
    nnz = (sp != 0).sum(axis=1).tolist()
    assert all(n == k_expect for n in nnz), "T2 sparse nnz: got %s expected %d" % (nnz, k_expect)
    uniq = set(sp.flatten().tolist())
    assert uniq.issubset({-1.0, 0.0, 1.0}), "T2 sparse values: got %s" % uniq

    # T3: at T=0.01, peaked input remains peaked
    peaked = np.zeros((1, 8), dtype=np.float32)
    peaked[0, 3] = 1.0
    probs = softmax_logits_with_T(peaked, 0.01)
    assert probs.max() > 0.5, "T3 peaked-at-low-T: got max=%.3f" % probs.max()

    # T4: at T=10.0, near uniform
    probs_hot = softmax_logits_with_T(peaked, 10.0)
    assert (probs_hot.max() - (1.0 / 8.0)) < 0.05, "T4 uniform-at-high-T: got max=%.3f" % probs_hot.max()

    # T5: lambda=0 reproduces unigram-only BPC
    U = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
    U_log = np.log(np.clip(U, 1e-30, 1.0))
    nxt = np.array([0, 1, 2, 0, 1])
    n_test = len(nxt)
    sub_logits = np.zeros((n_test, 5), dtype=np.float32)
    probs_sub = softmax_logits_with_T(sub_logits, 1.0)
    logp_sub = np.log(np.clip(probs_sub, 1e-30, 1.0))
    logp_lam0 = log_linear_interp_logp(logp_sub, U_log, 0.0)
    bpc_lam0 = bpc_from_logp(logp_lam0, nxt)
    bpc_uni = -float(np.mean(np.log(U[nxt]))) / math.log(2.0)
    assert abs(bpc_lam0 - bpc_uni) < 1e-4, "T5 lam=0 != unigram: %.4f vs %.4f" % (bpc_lam0, bpc_uni)

    # T6: lambda=1 reproduces pure substrate
    sub_logits2 = np.random.default_rng(42).standard_normal((10, 5)).astype(np.float32)
    probs2 = softmax_logits_with_T(sub_logits2, 1.0)
    logp2 = np.log(np.clip(probs2, 1e-30, 1.0))
    logp_lam1 = log_linear_interp_logp(logp2, U_log, 1.0)
    nxt10 = np.tile(nxt, 2)[:10]
    assert abs(bpc_from_logp(logp_lam1, nxt10) - bpc_from_logp(logp2, nxt10)) < 1e-4, "T6 lam=1 != raw"

    # T7: verdict gate -- HARD_PASS (both rails OK, C near cleanup, bonus B<=7.25)
    def _mk_unit(bpcs):
        by_arm = {}
        for arm in ARMS:
            by_arm[arm] = {
                "bpc_best": bpcs[arm], "top1_acc": 0.25, "mrr_at_10": 0.35,
                "best_T_for_bpc": 0.05, "best_lambda_for_bpc": 0.3,
                "best_dev_bpc": bpcs[arm],
                "raw_bpc_at_T1_L1": 8.5,
                "n_dev": 100, "n_test": 100, "n_eval_total": 200,
                "n_held_ctx": 200, "elapsed_s_arm": 0.01,
                "config": ARM_CONFIG[arm],
            }
        return {"seed": 0, "by_arm": by_arm, "V": 4000, "N": 64,
                  "N_DIM": 64, "N_TRAIN": 100, "N_HELD": 50, "VOCAB_CAP": 300,
                  "PRETRAIN_DIM": 10, "run_mode": "smoke", "config_version": "selftest",
                  "elapsed_s_seed": 0.01, "device": "cpu", "n_llm_calls": 0,
                  "encoder_meta": {"fallback_to_char_trigram": False}}

    # HARD_PASS path: rails OK, arm C near cleanup (7.22), bonus B <= 7.25
    u_hp = _mk_unit({
        "A_FAIR_HARNESS_ASSHIPPED": 7.31,
        "B_W2V_DENSE_NO_SPARSIFY": 7.20,
        "C_CHAR_TRIGRAM_DENSE_FAIR_FILTER": 7.22,
        "D_W2V_SPARSE_NO_FILTER": 7.34,
        "E_CHAR_TRIGRAM_NO_FILTER_ALPHA1": 7.22,
    })
    v, m, d = compute_verdict([u_hp])
    assert v == "HARD_PASS", "T7 HARD_PASS got %s msg=%s" % (v, m[:200])
    assert d["bonus_chain_grade_rail_flip"] is True, "T7 bonus flag missing"
    assert d["arm_C_near_cleanup_cells"] is True, "T7 arm_C cleanup flag"

    # MIDDLE_BAND is geometrically unreachable for arm_C alone (tol=0.05, refs
    # 7.2268 and 7.3065 only 0.0797 apart). We instead test the defensive
    # catch-all branch by partially-OK rails (rail E within 0.10 but not 0.05).
    # Construct: rail A OK (7.31 near 7.3065), rail E within HARD_FAIL_RAIL_TOL
    # (0.10) but outside SANITY_RAIL_TOL (0.05): e.g. 7.30 vs ref 7.2268 -> diff 0.073
    # That's > 0.05 (rail_E_ok=False) and < 0.10 (rail_E_diverge=False).
    # arm_C also placed in range. Expected: falls through to defensive MIDDLE_BAND.
    u_mid = _mk_unit({
        "A_FAIR_HARNESS_ASSHIPPED": 7.31,
        "B_W2V_DENSE_NO_SPARSIFY": 7.28,
        "C_CHAR_TRIGRAM_DENSE_FAIR_FILTER": 7.30,
        "D_W2V_SPARSE_NO_FILTER": 7.34,
        "E_CHAR_TRIGRAM_NO_FILTER_ALPHA1": 7.30,  # 0.073 off cleanup ref
    })
    v, m, _ = compute_verdict([u_mid])
    assert v == "MIDDLE_BAND", "T7 MIDDLE got %s msg=%s" % (v, m[:200])

    # HARD_FAIL path: arm C out of range (e.g. 7.50)
    u_hf = _mk_unit({
        "A_FAIR_HARNESS_ASSHIPPED": 7.31,
        "B_W2V_DENSE_NO_SPARSIFY": 7.28,
        "C_CHAR_TRIGRAM_DENSE_FAIR_FILTER": 7.50,
        "D_W2V_SPARSE_NO_FILTER": 7.34,
        "E_CHAR_TRIGRAM_NO_FILTER_ALPHA1": 7.22,
    })
    v, m, _ = compute_verdict([u_hf])
    assert v == "HARD_FAIL", "T7 HARD_FAIL got %s msg=%s" % (v, m[:200])

    # HARD_FAIL path: rail A diverges (e.g. 7.50 vs ref 7.3065 tol 0.10)
    u_hf2 = _mk_unit({
        "A_FAIR_HARNESS_ASSHIPPED": 7.50,
        "B_W2V_DENSE_NO_SPARSIFY": 7.28,
        "C_CHAR_TRIGRAM_DENSE_FAIR_FILTER": 7.22,
        "D_W2V_SPARSE_NO_FILTER": 7.34,
        "E_CHAR_TRIGRAM_NO_FILTER_ALPHA1": 7.22,
    })
    v, m, _ = compute_verdict([u_hf2])
    assert v == "HARD_FAIL", "T7 HARD_FAIL rail_A got %s" % v
    assert "rail_A_diverge" in m, "T7 rail_A msg missing"

    # T8: alpha=1 vs alpha=0.1 differ on small vocab
    idx_train_t = np.array([0, 1, 0, 1, 0, 2, 3], dtype=np.int64)
    U_a01 = build_unigram_np(idx_train_t, V=5, alpha=0.1)
    U_a1 = build_unigram_np(idx_train_t, V=5, alpha=1.0)
    assert not np.allclose(U_a01, U_a1), "T8 alpha distinction"
    # Empty bins get more probability at alpha=1
    assert U_a1[4] > U_a01[4], "T8 alpha=1 boosts empty"

    # T9: no LLM calls
    assert _LLM_CALL_COUNTER[0] == 0, "T9 zero llm"

    print("[selftest] PASS: T1 trigram + T2 sparsify + T3 peakedT001 + T4 uniformT10 "
          "+ T5 lam0=unigram + T6 lam1=raw + T7 verdict (HP/MID/HF) "
          "+ T8 alpha distinction + T9 llm=0", flush=True)


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
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_encoder_ablation_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (
                len(units), len(SEEDS), msg[:200]),
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
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM, "schema": "encoder-ablation-v1"}
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
        "arm_config": ARM_CONFIG,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_cpu_encoder_ablation_on_fair_harness_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (substrate cosine logits; word2vec is static open-weight lookup; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": "cpu",
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
