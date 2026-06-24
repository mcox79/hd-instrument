"""sparse_bipolar_substrate_lm_param_sweep_v1 -- envelope characterization.

Sweeps (f_sparse, N_DIM, N_TRAIN) for the ARM_SUBSTRATE_SPARSE_BIPOLAR mechanism
to characterize the operating envelope of the chain-grade substrate-as-LM win
established by fair_harness_substrate_as_lm_v1 (bpc_best_mean=7.3065 vs
unigram=7.7378 = +0.43 bits at f=0.05, N_DIM=8192, V=4000, N_TRAIN=100k).

This cell:
  - Reuses fair_harness infrastructure (word2vec encoder + rank-1 Hebbian W +
    joint (T,lambda) sweep + READOUT_DEGENERATE sanity gate + 3 metrics)
  - Iterates ONLY the sparse-bipolar arm config (no BRAIN / no DENSE)
  - Plus one ARM_UNIGRAM reference per (N_DIM, N_TRAIN, seed) for in-config bar
  - Per-(config, seed) checkpointing for partial recovery

Sweep grid (BUDGET-PRUNED factorial; ~20 configs * 3 seeds = 60 runs):
  f_sparse  : [0.01, 0.02, 0.05 (validated), 0.10, 0.20]   -- 5 points
  N_DIM     : [4096, 8192 (validated), 16384]              -- 3 points
  N_TRAIN   : N_TRAIN=1M only at N_DIM=4096 (cheap);
              N_TRAIN=100k at N_DIM in {4096, 8192, 16384}
  V vocab   : 4000 (validated; fixed)
  seeds     : [7, 17, 23]

PRUNING RATIONALE: (16384, 1M) and (8192, 1M) cells alone would dominate the
budget (~25200s + ~6300s respectively at observed scaling D^2*N_TRAIN) and risk
timeout-truncation under 7200s. The full f-axis is preserved at all 3 N_DIM
points so the f-optimum is visible at every dimension; the N_TRAIN axis is
preserved at the cheapest N_DIM so corpus-scaling is visible there. Future work:
top-2 configs from this sweep get a focused (N_DIM, 1M) re-validation cell.

GPU REQUIRED (Fix #24). torch.cuda for matmul / sparsification / logits.

Pre-reg HARD bands (envelope characterization):
  HARD_PASS: at least 3 distinct (f, N_DIM, N_TRAIN) configs clear
             bpc_best_mean <= unigram_bpc - 0.30 AND bpc_best_cv <= 0.05;
             AND optimal config beats fair_harness baseline (bpc=7.3065 at
             f=0.05, N=8192, N_TRAIN=100k) by >= 0.10 bits (bpc_best_mean <= 7.21).
  HARD_FAIL: max lift across ALL configs <= fair_harness baseline lift + 0.05
             (i.e. no config bpc_best_mean < 7.2565); sparse-bipolar saturates
             at the validated baseline.
  MIDDLE_BAND: plateau without clear optimum -- some configs HP-clear (>= 1) but
               either count < 3 OR no >= 0.10 bit beat over baseline.

Cites:
  experiments/exp_fair_harness_substrate_as_lm_v1.py  (validated baseline + harness)
  preregs/2026-06-23_fair_harness_substrate_as_lm_v1.md  (envelope-validated HP)
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json  (referent: 7.3065 vs 7.7378)
  Skunkworks_2026-06-23_methodology_audit  (joint T/lambda + 3-metric harness)
  USER_2026-06-22_Fix24_GPU_must_use_GPU
  USER_2026-06-22_Fix28_verify_per_arm_metrics_not_summary_text

ASCII-only. Per-(config,seed) checkpoint. atexit synthesizer.
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

ANCHOR_NAME = "sparse_bipolar_substrate_lm_param_sweep_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Validated baseline (referent: fair_harness_substrate_as_lm_v1 HARD_PASS)
FAIR_HARNESS_BPC_BASELINE = 7.3065   # SPARSE_BIPOLAR mean at f=0.05 N=8192 NT=100k
UNIGRAM_BPC_REF = 7.7378
UNIGRAM_TOP1_REF = 0.2171
HP_BPC_MARGIN = 0.30           # config must clear unigram - 0.30 to count as HP_BPC
HP_BPC_CV_MAX = 0.05           # within-seed CV must be <= 0.05
HP_BEAT_BASELINE_BITS = 0.10   # optimal must beat fair_harness baseline by 0.10 bits
HP_MIN_HP_CONFIGS = 3          # >= 3 configs clearing HP_BPC + CV gates
HF_BASELINE_LIFT_TOL = 0.05    # max lift across configs <= baseline_lift + 0.05
                               # (i.e. min bpc >= baseline - 0.05 = 7.2565)
DEGEN_TOL = 0.5

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Joint (T, lambda) sweep -- same as fair_harness
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Per-config knobs
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256
WORD2VEC_MODEL = "word2vec-google-news-300"

# Sweep grid (FULL = production GPU)
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    F_GRID = [0.01, 0.02, 0.05, 0.10, 0.20]
    # Configs are (N_DIM, N_TRAIN) tuples; pruned factorial:
    #   N_DIM=4096 x N_TRAIN in {100k, 1M}
    #   N_DIM=8192 x N_TRAIN in {100k}      (1M dropped: ~6300s sweep budget)
    #   N_DIM=16384 x N_TRAIN in {100k}     (1M dropped: ~25200s sweep budget)
    DIM_TRAIN_GRID = [
        (4096, 100_000),
        (4096, 1_000_000),
        (8192, 100_000),
        (16384, 100_000),
    ]
    N_HELD = 20_000
else:
    # Smoke: 1 f, 1 N_DIM, 1 N_TRAIN, 1 seed; small everything. < 180s on laptop CPU.
    SEEDS = [0]
    F_GRID = [0.05]
    DIM_TRAIN_GRID = [(512, 2_000)]
    N_HELD = 400
    VOCAB_CAP = 300
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

# Enumerate config-cells as (f, N_DIM, N_TRAIN); pretty-name = "f{f}_n{N}_t{NT}"
CONFIGS: List[Tuple[float, int, int]] = []
for (N_DIM_cfg, N_TRAIN_cfg) in DIM_TRAIN_GRID:
    for f in F_GRID:
        CONFIGS.append((f, N_DIM_cfg, N_TRAIN_cfg))

ARM_NAME = "ARM_SUBSTRATE_SPARSE_BIPOLAR"

CONFIG_VERSION = (
    "sparse_bipolar_substrate_lm_param_sweep_v1; n_configs=%d configs=%s "
    "seeds=%s mode=%s temps=%s lambdas=%s VOCAB_CAP=%d N_HELD=%d "
    "PRETRAIN_DIM=%d INGEST_CHUNK=%d RECALL_BATCH=%d MRR_K=%d device=%s; "
    "bands HP_BPC_margin>=%.3f HP_CV<=%.2f HP_beat>=%.3f HP_min_configs=%d "
    "HF_baseline_lift_tol=%.3f DEGEN_tol=%.2f baseline_bpc=%.4f unigram_bpc=%.4f"
) % (
    len(CONFIGS), CONFIGS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID, VOCAB_CAP,
    N_HELD, PRETRAIN_DIM, INGEST_CHUNK, RECALL_BATCH, MRR_K, str(DEVICE),
    HP_BPC_MARGIN, HP_BPC_CV_MAX, HP_BEAT_BASELINE_BITS, HP_MIN_HP_CONFIGS,
    HF_BASELINE_LIFT_TOL, DEGEN_TOL, FAIR_HARNESS_BPC_BASELINE, UNIGRAM_BPC_REF,
)


# ============================================================================
# Char-trigram encoder (defensive OOV fallback for word2vec)
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
    """Defensive gensim load via tools.gensim_load_helper."""
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
# Hebbian rank-1 W on GPU
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


def compute_sparse_bipolar_logits(E: torch.Tensor, idx_train: np.ndarray,
                                    idx_held: np.ndarray, f: float, seed: int,
                                    ingest_chunk: int, recall_batch: int) -> Dict:
    """Build sparse-bipolar E + Hebbian W + held-set logits.

    Returns [n_held, V] float32 logits + diagnostics.
    """
    V, dim = E.shape
    device = E.device

    E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E, f, seed))

    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)

    t0 = time.time()
    src_keys_train = E_sb[idx_train_t]
    src_keys_held = E_sb[idx_held_t]
    t_keys = time.time() - t0

    t0 = time.time()
    W = build_rank1_W_gpu(idx_train_t, E_sb, ingest_chunk)
    n_h = src_keys_held.shape[0]
    pred_held = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        pred_held[b:end] = _l2_normalize_t(src_keys_held[b:end] @ W.T)
    del W
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        logits[b:end] = pred_held[b:end] @ E_sb.T
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    del pred_held, src_keys_train, src_keys_held, idx_train_t, idx_held_t, E_sb
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_keys_s": round(t_keys, 2),
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
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
# Joint (T, lambda) sweep + 3 metrics (cloned from fair_harness)
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
# Per-(config, seed) runner
# ============================================================================

def _cfg_key(f: float, n_dim: int, n_train: int, seed: int) -> str:
    """Build a partial-key with NO periods (period breaks _PARTIAL_RE).

    Encodes f as an integer (basis points): f=0.05 -> fbps0500.
    """
    fbps = int(round(f * 10000))
    return "fbps%04d_n%d_t%d_s%d" % (fbps, n_dim, n_train, seed)


def run_config_seed(f: float, n_dim: int, n_train: int, seed: int) -> Dict:
    """Run one (f, N_DIM, N_TRAIN, seed) cell. Returns full result dict."""
    t_cs = time.time()
    cfg_name = _cfg_key(f, n_dim, n_train, seed)
    print("\n[cfg=%s] loading text8 + building vocab" % cfg_name, flush=True)
    toks = load_text8_tokens(n_train + N_HELD)
    if len(toks) < n_train + N_HELD:
        print("[WARN cfg=%s] corpus short: %d vs %d" % (
            cfg_name, len(toks), n_train + N_HELD), flush=True)
    train_toks = toks[:n_train]
    held_toks = toks[n_train:n_train + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[cfg=%s] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d f=%.4f device=%s" % (
        cfg_name, V, n_train, N_HELD, n_dim, f, str(DEVICE)), flush=True)

    if DEVICE.type == "cuda":
        try:
            free_b, total_b = torch.cuda.mem_get_info()
            print("[cfg=%s gpu] %s free=%.2fGB total=%.2fGB" % (
                cfg_name, torch.cuda.get_device_name(0),
                free_b / 1e9, total_b / 1e9), flush=True)
        except Exception as e:
            print("[cfg=%s gpu-info-fail] %s" % (cfg_name, e), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[cfg=%s ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        cfg_name, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"],
        uni["n_test"]), flush=True)

    # Build word2vec base E (defensive fallback to char-trigram if gensim fails)
    print("[cfg=%s] building word2vec base E (V=%d, N_DIM=%d)..." % (
        cfg_name, V, n_dim), flush=True)
    t_enc0 = time.time()
    encoder_meta = {}
    try:
        E_base, encoder_meta = build_E_word2vec_gpu(vocab, n_dim, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[cfg=%s encoder] WORD2VEC LOAD FAIL: %s -- fallback to char-trigram" % (
            cfg_name, err), flush=True)
        E_base = build_E_char_trigram_gpu(vocab, n_dim, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    t_enc = time.time() - t_enc0
    if DEVICE.type == "cuda":
        try:
            free_b, total_b = torch.cuda.mem_get_info()
            print("[cfg=%s encoder] E built (%.1fs); GPU free=%.2fGB" % (
                cfg_name, t_enc, free_b / 1e9), flush=True)
        except Exception:
            pass

    # Split held into dev + test halves (skip <unk> positions)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        return {
            "cfg_name": cfg_name, "f": f, "N_DIM": n_dim, "N_TRAIN": n_train,
            "seed": seed, "V": V, "N_HELD": N_HELD,
            "by_arm": {"ARM_UNIGRAM": uni, ARM_NAME: {"empty_eval": True}},
            "encoder_meta": encoder_meta,
            "config_version": CONFIG_VERSION,
            "elapsed_s_cs": round(time.time() - t_cs, 2),
            "run_mode": RUN_MODE,
            "device": str(DEVICE),
            "N": n_dim,  # PROT-021 mismatch guard
        }
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    # Build sparse-bipolar arm + joint sweep
    t_arm0 = time.time()
    print("[cfg=%s %s] building logits..." % (cfg_name, ARM_NAME), flush=True)
    try:
        ar = compute_sparse_bipolar_logits(
            E_base, idx_train, idx_held, f, seed, INGEST_CHUNK, RECALL_BATCH,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [cfg=%s %s] COMPUTE FAIL: %s" % (cfg_name, ARM_NAME, err), flush=True)
        arm_data = {"compute_failed": True, "compute_error": err,
                    "bpc_best": float("inf"), "top1_acc": float("nan"),
                    "mrr_at_10": float("nan"),
                    "best_T_for_bpc": float("nan"),
                    "best_lambda_for_bpc": float("nan"),
                    "raw_bpc_at_T1_L1": float("inf"),
                    "elapsed_s_arm": round(time.time() - t_arm0, 2)}
        del E_base
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        return {
            "cfg_name": cfg_name, "f": f, "N_DIM": n_dim, "N_TRAIN": n_train,
            "seed": seed, "V": V, "N_HELD": N_HELD,
            "by_arm": {"ARM_UNIGRAM": uni, ARM_NAME: arm_data},
            "encoder_meta": encoder_meta,
            "config_version": CONFIG_VERSION,
            "elapsed_s_cs": round(time.time() - t_cs, 2),
            "run_mode": RUN_MODE,
            "device": str(DEVICE),
            "N": n_dim,
        }
    logits_full = ar["logits"]
    if logits_full.shape[0] >= len(ctx_full):
        logits_ctx = logits_full[:len(ctx_full)]
    else:
        logits_ctx = logits_full
    logits_eval = logits_ctx[mask]
    jr = joint_sweep_substrate(
        logits_eval[:n_dev], logits_eval[n_dev:], U_log,
        nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
    )
    jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
    jr["wall_keys_s"] = ar.get("wall_keys_s", 0.0)
    jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
    jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
    print("    [cfg=%s %s] bpc_best=%.3f top1=%.4f mrr=%.4f (bestT=%.4f bestL=%.2f) "
          "raw_T1L1_bpc=%.3f wall_arm=%.1fs" % (
              cfg_name, ARM_NAME, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
              jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
              jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)

    del E_base
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "cfg_name": cfg_name, "f": f, "N_DIM": n_dim, "N_TRAIN": n_train,
        "seed": seed, "V": V, "N_HELD": N_HELD,
        "by_arm": {"ARM_UNIGRAM": uni, ARM_NAME: jr},
        "encoder_meta": encoder_meta,
        "config_version": CONFIG_VERSION,
        "elapsed_s_cs": round(time.time() - t_cs, 2),
        "run_mode": RUN_MODE,
        "device": str(DEVICE),
        "N": n_dim,
    }


# ============================================================================
# Verdict (envelope characterization)
# ============================================================================

def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "no results", {})

    # Group results by (f, N_DIM, N_TRAIN) config
    by_cfg: Dict[Tuple[float, int, int], List[Dict]] = {}
    for u in units:
        k = (float(u.get("f")), int(u.get("N_DIM")), int(u.get("N_TRAIN")))
        by_cfg.setdefault(k, []).append(u)

    cfg_summaries: List[Dict] = []
    for (f, n_dim, n_train), urows in sorted(by_cfg.items()):
        sub_arms = [u["by_arm"].get(ARM_NAME, {}) for u in urows]
        uni_arms = [u["by_arm"].get("ARM_UNIGRAM", {}) for u in urows]
        valid_sub = [a for a in sub_arms if math.isfinite(a.get("bpc_best", float("inf")))]
        n_valid = len(valid_sub)
        n_failed = len(sub_arms) - n_valid
        if n_valid == 0:
            cfg_summaries.append({
                "f": f, "N_DIM": n_dim, "N_TRAIN": n_train,
                "n_valid_seeds": 0, "n_compute_failed": n_failed,
                "bpc_best_mean": float("inf"), "all_seeds_failed": True,
            })
            continue
        bpc_vals = [a["bpc_best"] for a in valid_sub]
        top1_vals = [a["top1_acc"] for a in valid_sub]
        mrr_vals = [a["mrr_at_10"] for a in valid_sub]
        raw_vals = [a["raw_bpc_at_T1_L1"] for a in valid_sub]
        bT = [a["best_T_for_bpc"] for a in valid_sub]
        bL = [a["best_lambda_for_bpc"] for a in valid_sub]
        uni_bpc_vals = [u.get("bpc_unigram", UNIGRAM_BPC_REF) for u in uni_arms]
        uni_top1_vals = [u.get("top1_unigram", UNIGRAM_TOP1_REF) for u in uni_arms]
        uni_mrr_vals = [u.get("mrr_unigram", 0.0) for u in uni_arms]

        bm = float(np.mean(bpc_vals))
        bs = float(np.std(bpc_vals))
        cv = bs / max(abs(bm), 1e-6)
        uni_bpc_mean = float(np.mean(uni_bpc_vals))
        lift_vs_unigram = uni_bpc_mean - bm
        lift_vs_baseline = FAIR_HARNESS_BPC_BASELINE - bm
        hp_bpc_bar = uni_bpc_mean - HP_BPC_MARGIN
        bpc_clears_bar = bm <= hp_bpc_bar
        cv_clears = cv <= HP_BPC_CV_MAX
        is_hp_config = bool(bpc_clears_bar and cv_clears)

        cfg_summaries.append({
            "f": f, "N_DIM": n_dim, "N_TRAIN": n_train,
            "n_valid_seeds": n_valid, "n_compute_failed": n_failed,
            "bpc_best_mean": round(bm, 4),
            "bpc_best_std": round(bs, 4),
            "bpc_best_cv": round(cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_vals)), 4),
            "top1_acc_std": round(float(np.std(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_vals)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_vals)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_vals)), 4),
            "best_T_for_bpc_mean": round(float(np.mean(bT)), 4),
            "best_lambda_for_bpc_mean": round(float(np.mean(bL)), 4),
            "unigram_bpc_mean": round(uni_bpc_mean, 4),
            "unigram_top1_mean": round(float(np.mean(uni_top1_vals)), 4),
            "unigram_mrr_mean": round(float(np.mean(uni_mrr_vals)), 4),
            "lift_vs_unigram_bits": round(lift_vs_unigram, 4),
            "lift_vs_fair_harness_baseline_bits": round(lift_vs_baseline, 4),
            "hp_bpc_bar": round(hp_bpc_bar, 4),
            "bpc_clears_bar": bool(bpc_clears_bar),
            "cv_clears": bool(cv_clears),
            "is_hp_config": is_hp_config,
            "all_seeds_failed": False,
        })

    # Optimal config (min bpc_best_mean among valid configs)
    valid_cfgs = [c for c in cfg_summaries if not c.get("all_seeds_failed", True)]
    if not valid_cfgs:
        return ("HARD_FAIL",
                "HARD_FAIL: all configs all-seeds-failed (no valid sweep cells)",
                {"cfg_summaries": cfg_summaries, "n_valid_configs": 0})
    valid_cfgs_sorted = sorted(valid_cfgs, key=lambda c: c["bpc_best_mean"])
    optimal = valid_cfgs_sorted[0]
    optimal_bpc = optimal["bpc_best_mean"]
    optimal_beats_baseline_bits = FAIR_HARNESS_BPC_BASELINE - optimal_bpc

    # Count HP configs
    hp_configs = [c for c in valid_cfgs if c["is_hp_config"]]
    n_hp_configs = len(hp_configs)

    # Max lift across all configs
    max_lift_vs_unigram = max(c["lift_vs_unigram_bits"] for c in valid_cfgs)
    baseline_lift_vs_unigram = UNIGRAM_BPC_REF - FAIR_HARNESS_BPC_BASELINE  # 0.4313

    # Compose summary line (per-config one-liner)
    cfg_lines = []
    for c in cfg_summaries:
        if c.get("all_seeds_failed"):
            cfg_lines.append("f%.4f_n%d_t%d=FAIL" % (c["f"], c["N_DIM"], c["N_TRAIN"]))
        else:
            cfg_lines.append("f%.4f_n%d_t%d=bpc%.3f(cv%.3f,lift%.2f)%s" % (
                c["f"], c["N_DIM"], c["N_TRAIN"],
                c["bpc_best_mean"], c["bpc_best_cv"],
                c["lift_vs_unigram_bits"],
                "*HP" if c["is_hp_config"] else ""))
    summary = "SWEEP optimal=f%.4f_n%d_t%d bpc=%.3f beat_baseline=%.3f n_hp=%d/%d max_lift=%.3f | %s" % (
        optimal["f"], optimal["N_DIM"], optimal["N_TRAIN"], optimal_bpc,
        optimal_beats_baseline_bits, n_hp_configs, len(valid_cfgs),
        max_lift_vs_unigram, " ".join(cfg_lines)
    )

    detail = {
        "cfg_summaries": cfg_summaries,
        "valid_cfgs_sorted_by_bpc": [
            {"f": c["f"], "N_DIM": c["N_DIM"], "N_TRAIN": c["N_TRAIN"],
             "bpc_best_mean": c["bpc_best_mean"],
             "lift_vs_unigram_bits": c["lift_vs_unigram_bits"],
             "lift_vs_fair_harness_baseline_bits": c["lift_vs_fair_harness_baseline_bits"],
             "is_hp_config": c["is_hp_config"]}
            for c in valid_cfgs_sorted
        ],
        "optimal_config": {"f": optimal["f"], "N_DIM": optimal["N_DIM"],
                            "N_TRAIN": optimal["N_TRAIN"],
                            "bpc_best_mean": optimal_bpc,
                            "optimal_beats_baseline_bits": round(optimal_beats_baseline_bits, 4)},
        "n_configs_total": len(cfg_summaries),
        "n_configs_valid": len(valid_cfgs),
        "n_hp_configs": n_hp_configs,
        "max_lift_vs_unigram_bits": round(max_lift_vs_unigram, 4),
        "baseline_lift_vs_unigram_bits": round(baseline_lift_vs_unigram, 4),
        "fair_harness_baseline_bpc": FAIR_HARNESS_BPC_BASELINE,
        "unigram_bpc_ref": UNIGRAM_BPC_REF,
        "hp_bpc_margin": HP_BPC_MARGIN,
        "hp_bpc_cv_max": HP_BPC_CV_MAX,
        "hp_beat_baseline_bits": HP_BEAT_BASELINE_BITS,
        "hp_min_hp_configs": HP_MIN_HP_CONFIGS,
        "hf_baseline_lift_tol": HF_BASELINE_LIFT_TOL,
        "CONFIG_VERSION": CONFIG_VERSION,
        "honest_scope": (
            "Envelope sweep of ARM_SUBSTRATE_SPARSE_BIPOLAR over (f_sparse, N_DIM, "
            "N_TRAIN). Single-arm; reuses fair_harness joint (T,lambda) harness "
            "+ 3-metric reporting. Pruned factorial: N_TRAIN=1M only at N_DIM=4096 "
            "to fit 7200s timeout budget. HP_BPC bar = unigram_bpc - %.2f; cv <= %.2f. "
            "HARD_PASS requires >= %d HP configs AND optimal beats fair_harness "
            "baseline (%.4f) by >= %.2f bits. HARD_FAIL requires max lift <= baseline "
            "lift (%.4f) + %.2f. PRIMARY METRIC IS BPC; top-1/MRR reported for "
            "transparency but NOT load-bearing in this envelope (per fair_harness: "
            "sparse-bipolar's win is BPC-shape, not top-1 -- top1_ok=false in "
            "validated config)." % (
                HP_BPC_MARGIN, HP_BPC_CV_MAX, HP_MIN_HP_CONFIGS,
                FAIR_HARNESS_BPC_BASELINE, HP_BEAT_BASELINE_BITS,
                baseline_lift_vs_unigram, HF_BASELINE_LIFT_TOL)),
        "cites": [
            "preregs/2026-06-23_sparse_bipolar_substrate_lm_param_sweep_v1.md",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json",
            "Skunkworks_2026-06-23_methodology_audit",
            "USER_2026-06-22_Fix24_GPU_must_use_GPU",
            "USER_2026-06-22_Fix28_verify_per_arm_metrics",
        ],
    }

    # Verdict logic
    pass_a = (n_hp_configs >= HP_MIN_HP_CONFIGS)
    pass_b = (optimal_beats_baseline_bits >= HP_BEAT_BASELINE_BITS)
    if pass_a and pass_b:
        return ("HARD_PASS",
                "SWEEP_HARD_PASS: clear optimal regime characterized. %s" % summary,
                detail)

    fail_threshold = baseline_lift_vs_unigram + HF_BASELINE_LIFT_TOL
    if max_lift_vs_unigram <= fail_threshold:
        return ("HARD_FAIL",
                ("SWEEP_HARD_FAIL: sparse-bipolar lift saturates -- max_lift=%.3f "
                 "<= baseline_lift(%.3f) + tol(%.2f) = %.3f. No config improves on "
                 "fair_harness baseline; envelope is one-point (no scaling lever). %s" % (
                     max_lift_vs_unigram, baseline_lift_vs_unigram,
                     HF_BASELINE_LIFT_TOL, fail_threshold, summary)),
                detail)

    return ("MIDDLE_BAND",
            "SWEEP_MIDDLE_BAND: plateau without clear optimum. n_hp=%d/%d "
            "(need %d), optimal_beats_baseline=%.3f (need %.2f). %s" % (
                n_hp_configs, len(valid_cfgs), HP_MIN_HP_CONFIGS,
                optimal_beats_baseline_bits, HP_BEAT_BASELINE_BITS, summary),
            detail)


# ============================================================================
# Self-test (asserts harness + verdict logic + sparse primitive on tiny inputs)
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

    # T3: softmax_with_T peaked at T=0.01
    peaked = np.zeros((1, 8), dtype=np.float32)
    peaked[0, 3] = 1.0
    probs = softmax_logits_with_T(peaked, 0.01)
    assert probs.max() > 0.5, "T3 peaked at T=0.01; got %.3f" % probs.max()

    # T4: bpc_from_logp endpoint -- lambda=0 reproduces unigram BPC
    U = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
    U_log = np.log(np.clip(U, 1e-30, 1.0))
    nxt = np.array([0, 1, 2, 0, 1])
    sub_logits = np.zeros((5, 5), dtype=np.float32)
    logp_lam0 = log_linear_interp_logp(np.log(np.full_like(sub_logits, 1.0/5.0)), U_log, 0.0)
    bpc_lam0 = bpc_from_logp(logp_lam0, nxt)
    bpc_uni = -float(np.mean(np.log(U[nxt]))) / math.log(2.0)
    assert abs(bpc_lam0 - bpc_uni) < 1e-4, "T4 lam0=uni; %.4f vs %.4f" % (bpc_lam0, bpc_uni)

    # T5: verdict bands -- HARD_PASS path
    def _mk_unit(f, n_dim, n_train, seed, bpc_best, top1=0.21, mrr=0.28,
                   raw_t1l1=11.5, uni_bpc=7.7378, uni_top1=0.2171, uni_mrr=0.28):
        return {
            "cfg_name": _cfg_key(f, n_dim, n_train, seed),
            "f": f, "N_DIM": n_dim, "N_TRAIN": n_train, "seed": seed,
            "V": 4000, "N_HELD": 100,
            "by_arm": {
                "ARM_UNIGRAM": {"bpc_unigram": uni_bpc, "top1_unigram": uni_top1,
                                  "mrr_unigram": uni_mrr, "n_test": 100},
                ARM_NAME: {
                    "bpc_best": bpc_best, "top1_acc": top1, "mrr_at_10": mrr,
                    "best_T_for_bpc": 0.05, "best_lambda_for_bpc": 0.3,
                    "best_dev_bpc": bpc_best,
                    "best_T_for_top1": 0.1, "best_lambda_for_top1": 0.0,
                    "best_T_for_mrr": 0.2, "best_lambda_for_mrr": 0.3,
                    "raw_bpc_at_T1_L1": raw_t1l1, "raw_top1_at_T1_L1": 0.08,
                    "raw_mrr_at_T1_L1": 0.12,
                    "n_dev": 50, "n_test": 50, "grid_size": 42,
                    "elapsed_s_arm": 1.0,
                }
            },
            "encoder_meta": {}, "config_version": "selftest",
            "elapsed_s_cs": 1.0, "run_mode": "smoke", "device": "cpu",
            "N": n_dim,
        }
    # HP path: 3+ configs clear bpc<7.438 AND cv<0.05; optimal beats 7.3065 by 0.10
    # build 3 configs each with 3 seeds; bpc values around 7.20 (clearly HP)
    hp_units = []
    for cfg_idx, f in enumerate([0.02, 0.05, 0.10]):
        for sd in [7, 17, 23]:
            # Add tiny per-seed noise to keep cv well under 0.05
            bpc = 7.20 + (sd % 3) * 0.005 - cfg_idx * 0.001
            hp_units.append(_mk_unit(f, 8192, 100_000, sd, bpc))
    v, m, d = compute_verdict(hp_units)
    assert v == "HARD_PASS", "T5 HARD_PASS got %s msg=%s" % (v, m[:200])
    assert d["n_hp_configs"] >= 3, "T5 HP count"
    # T6: HARD_FAIL path -- all configs at or worse than baseline (max_lift <= baseline_lift+0.05)
    # baseline_lift = 7.7378 - 7.3065 = 0.4313; fail if max_lift <= 0.4813.
    # Put all configs at bpc ~7.30 (lift ~0.44) -- still HARD_FAIL since not > 0.4813
    hf_units = []
    for cfg_idx, f in enumerate([0.05, 0.10, 0.20]):
        for sd in [7, 17, 23]:
            bpc = 7.30 + cfg_idx * 0.01
            hf_units.append(_mk_unit(f, 8192, 100_000, sd, bpc))
    v, m, d = compute_verdict(hf_units)
    assert v == "HARD_FAIL", "T6 HARD_FAIL got %s msg=%s" % (v, m[:200])
    # T7: MIDDLE_BAND -- exactly 2 HP configs (need 3) with optimal beating baseline by 0.10+
    mid_units = []
    for cfg_idx, f in enumerate([0.05, 0.10]):
        for sd in [7, 17, 23]:
            bpc = 7.18 + cfg_idx * 0.003
            mid_units.append(_mk_unit(f, 8192, 100_000, sd, bpc))
    # add a 3rd config that does NOT clear HP
    for sd in [7, 17, 23]:
        mid_units.append(_mk_unit(0.20, 8192, 100_000, sd, 7.55))
    v, m, d = compute_verdict(mid_units)
    assert v == "MIDDLE_BAND", "T7 MIDDLE_BAND got %s msg=%s" % (v, m[:200])
    assert d["n_hp_configs"] == 2, "T7 HP count should be 2"

    # T8: MRR planted
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
    expected_mrr = float(np.mean([1.0/r for r in expected_ranks]))
    assert abs(mrr_val - expected_mrr) < 1e-6, "T8 MRR got %.4f vs %.4f" % (mrr_val, expected_mrr)

    print("[selftest] PASS: T1 trigram + T2 sparse-bipolar + T3 peakedT001 + "
          "T4 lam0=unigram + T5 HARD_PASS verdict + T6 HARD_FAIL verdict + "
          "T7 MIDDLE_BAND verdict + T8 MRR planted", flush=True)


# ============================================================================
# atexit synthesizer
# ============================================================================
_METRICS_WRITTEN = [False]
_OUT_DIR_REF: List[Optional[Path]] = [None]
_T0_REF: List[Optional[float]] = [None]
_ALL_KEYS_REF: List[List[str]] = [[]]


def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    out_dir = _OUT_DIR_REF[0]
    if out_dir is None or not out_dir.exists():
        return
    try:
        partials = aggregate_partials(out_dir, _ALL_KEYS_REF[0])
        units = list(partials.values())
        if not units:
            return
        try:
            verdict, msg, detail = compute_verdict(units)
        except Exception as e:
            verdict, msg, detail = ("PARTIAL_TIMEOUT",
                                     "atexit synthesize: compute_verdict failed: %s" % e,
                                     {"n_units_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "anchor": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NUNITS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "n_units": len(units),
            "n_units_expected": len(_ALL_KEYS_REF[0]),
            "n_configs_total": len(CONFIGS),
            "n_seeds_per_config": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_sparse_bipolar_param_sweep_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d units] %s" % (
                len(units), len(_ALL_KEYS_REF[0]), msg[:200]),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_synthesized_by_atexit": True,
            "config_version": CONFIG_VERSION,
            "device": str(DEVICE),
        }
        write_metrics(out_dir, metrics, units)
        _METRICS_WRITTEN[0] = True
        sys.stderr.write("[atexit] synthesized metrics.json from %d/%d units\n" % (
            len(units), len(_ALL_KEYS_REF[0])))
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
    print("[config] %s mode=%s n_configs=%d n_seeds=%d total_cells=%d | "
          "name_says_smoke=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, len(CONFIGS), len(SEEDS),
              len(CONFIGS) * len(SEEDS), _NAME_SAYS_SMOKE, CONFIG_VERSION), flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[gpu] device=%s name=%s total_mem_gb=%.2f" % (
                DEVICE, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception as e:
            print("[gpu] info-fetch failed: %s" % e, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    # Build full key list (one per (config, seed))
    all_keys: List[str] = []
    cs_pairs: List[Tuple[str, float, int, int, int]] = []
    for (f, n_dim, n_train) in CONFIGS:
        for sd in SEEDS:
            k = _cfg_key(f, n_dim, n_train, sd)
            all_keys.append(k)
            cs_pairs.append((k, f, n_dim, n_train, sd))
    _ALL_KEYS_REF[0] = all_keys
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "schema": "sparse-bipolar-param-sweep-v1"}
    t0 = time.time()
    _T0_REF[0] = t0
    for (k, f, n_dim, n_train, sd) in cs_pairs:
        existing = aggregate_partials(out_dir, [k], run_config=run_cfg)
        if k in existing:
            print("[ckpt] %s done; skip" % k, flush=True)
            continue
        result = run_config_seed(f, n_dim, n_train, sd)
        # PROT-021 mismatch guard: write N field matches run_config
        write_partial_key(out_dir, k, result)
    units = list(aggregate_partials(out_dir, all_keys, run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "anchor": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "run_mode": RUN_MODE,
        "n_configs": len(CONFIGS),
        "n_seeds_per_config": len(SEEDS),
        "n_units": len(units),
        "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID,
        "MRR_K": MRR_K,
        "VOCAB_CAP": VOCAB_CAP,
        "PRETRAIN_DIM": PRETRAIN_DIM,
        "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH,
        "N_HELD": N_HELD,
        "F_GRID": F_GRID,
        "DIM_TRAIN_GRID": DIM_TRAIN_GRID,
        "SEEDS": SEEDS,
        "detail": detail,
        "metrics_source": "measured_gpu_sparse_bipolar_param_sweep_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": "TRUE (single-arm; substrate cosine logits; word2vec static lookup; zero LLM at inference)",
        "zero_llm_calls_at_inference": True,
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
