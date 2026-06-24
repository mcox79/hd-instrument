"""
substrate_mh_beta_sweep_extended_T_grid_v1
-- Composition collapse drill: symptomatic vs structural diagnosis.

A1 cell (substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1)
collapsed ARM_FULL_JOINT_COMPOSE to BPC=7.8919 with MH beta=8.0 (compared to its K2-only
arm at 7.1781). Smoking gun: best_T flipped 0.02 -> 1.0 (50x). This cell tests whether
SOFTENING MH beta restores soft predictive distribution (symptomatic) or whether the
collapse persists at all beta (structural).

Five arms (3 seeds, text8 N_DIM=8192 V=4000 N_TRAIN=100k):
  ARM_BASELINE_NO_CLEANUP   cf-RPE + STDP + K=2; no MH (sanity rail = A1 K2: 7.1781)
  ARM_MH_BETA_0p5           same + MH cleanup at beta=0.5  (very soft)
  ARM_MH_BETA_1p0           same + MH cleanup at beta=1.0  (mild)
  ARM_MH_BETA_2p0           same + MH cleanup at beta=2.0  (moderate)
  ARM_MH_BETA_8p0           same + MH cleanup at beta=8.0  (A1 reproduce: 7.8919)

Pre-reg HARD bands (locked pre-smoke):
  Sanity rails (run_mode=full only):
    ARM_BASELINE_NO_CLEANUP within +/-0.05 of 7.1781
    ARM_MH_BETA_8p0         within +/-0.10 of 7.8919
  Verdict on best-performing MH-beta arm (min BPC across BETA_0p5/1p0/2p0):
    HARD_PASS    BPC <= 7.05    (softer MH beats no-cleanup baseline)
    MIDDLE_BAND  in [7.05, 7.15] (softer MH neutral)
    HARD_FAIL    all MH arms BPC >= 7.20 (structural collapse)
  cv <= 0.05 across seeds mandatory on best MH-beta arm.
  _LLM_CALL_COUNTER == 0 (substrate-only).

Routing: remote_cpu_queue (numpy + torch CPU; no GPU push permission for exp_dev).
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
import hashlib
import math
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics,
    resumable_seeds as _resumable_seeds,
)

ANCHOR_NAME = "substrate_mh_beta_sweep_extended_T_grid_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only audit counter
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Pre-reg threshold bands (pre-registered; do NOT modify post-smoke)
# ============================================================================
# Sanity rails (from A1 metrics; provenance check in full mode only)
SANITY_RAIL_NO_CLEANUP_REF = 7.1781       # A1 ARM_FAIR_HARNESS_PLUS_CFRPE_PLUS_HETPLASTICITY_PLUS_K2
SANITY_RAIL_NO_CLEANUP_TOL = 0.05
SANITY_RAIL_BETA8_REF = 7.8919            # A1 ARM_FULL_JOINT_COMPOSE (beta=8.0)
SANITY_RAIL_BETA8_TOL = 0.10              # wider because reproducing collapse is more variable

# Verdict bands on best-performing MH-beta arm (min BPC across beta in {0.5, 1.0, 2.0})
HARD_PASS_BPC_CEILING = 7.05
MIDDLE_BAND_BPC_LOWER = 7.05
MIDDLE_BAND_BPC_UPPER = 7.15
HARD_FAIL_BPC_FLOOR = 7.20
CV_MAX = 0.05

# ============================================================================
# Primitive knob parameters (FROZEN to A1 K2 setup; only MH beta varies)
# ============================================================================
CFRPE_LR = 0.5
STDP_WEIGHT = 0.5
INGEST_BATCH = 64
N_STEPS_PER_SEED = 1000

K_BANKS = 2
GATE_TEMP = 0.5

# Modern-Hopfield iters held fixed; beta is the variable across arms
MH_ITERS = 3

# Extended eval grids (wider TEMP_GRID than A1; LAMBDA_GRID per META C7)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Encoder
SPARSE_BIPOLAR_F = 0.05
WORD2VEC_MODEL = "word2vec-google-news-300"
PRETRAIN_DIM = 300

# Arms with their MH config
ARMS = [
    "ARM_BASELINE_NO_CLEANUP",
    "ARM_MH_BETA_0p5",
    "ARM_MH_BETA_1p0",
    "ARM_MH_BETA_2p0",
    "ARM_MH_BETA_8p0",
]

ARM_CONFIGS = {
    "ARM_BASELINE_NO_CLEANUP": {"mh_cleanup": False, "mh_beta": 0.0},
    "ARM_MH_BETA_0p5":         {"mh_cleanup": True,  "mh_beta": 0.5},
    "ARM_MH_BETA_1p0":         {"mh_cleanup": True,  "mh_beta": 1.0},
    "ARM_MH_BETA_2p0":         {"mh_cleanup": True,  "mh_beta": 2.0},
    "ARM_MH_BETA_8p0":         {"mh_cleanup": True,  "mh_beta": 8.0},
}

# Set of MH-beta arms to consider for the verdict (excludes baseline + beta=8.0 sanity-rail arm)
VERDICT_ARM_SET = ["ARM_MH_BETA_0p5", "ARM_MH_BETA_1p0", "ARM_MH_BETA_2p0"]

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
# Production config
# ============================================================================
N_DIM_TOTAL = 8192
N_DIM_PER_BANK = N_DIM_TOTAL // K_BANKS   # 4096 per bank
VOCAB_CAP = 4000
RECALL_BATCH = 256
INGEST_CHUNK = 4096

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = N_STEPS_PER_SEED
else:
    # Smoke: clean synthetic data + minimal config. Goal: fit < 180s on CPU; exercise
    # every arm + every MH beta + extended TEMP_GRID + verdict bands.
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM_TOTAL = 1024
    N_DIM_PER_BANK = N_DIM_TOTAL // K_BANKS
    N_STEPS = 80
    RECALL_BATCH = 128
    INGEST_CHUNK = 512

CONFIG_VERSION = (
    "%s; encoder=word2vec_sparse_bipolar_f%.3f; N_DIM_TOTAL=%d K_BANKS=%d "
    "N_DIM_PER_BANK=%d N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s "
    "mode=%s temps=%s lambdas=%s cfrpe_lr=%.3f stdp_w=%.3f gate_temp=%.3f "
    "mh_iters=%d mh_betas=%s n_steps=%d batch=%d device=%s"
) % (
    ANCHOR_NAME, SPARSE_BIPOLAR_F, N_DIM_TOTAL, K_BANKS, N_DIM_PER_BANK,
    N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID,
    CFRPE_LR, STDP_WEIGHT, GATE_TEMP,
    MH_ITERS, [ARM_CONFIGS[a]["mh_beta"] for a in ARMS],
    N_STEPS, INGEST_BATCH, str(DEVICE),
)


# ============================================================================
# text8 corpus utilities (identical to A1)
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
# Encoder: word2vec-projected sparse-bipolar (identical to A1)
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


def build_E_word2vec(vocab: List[str], n_dim: int, seed: int) -> Tuple[torch.Tensor, Dict]:
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


def build_E_synthetic_smoke(V: int, n_dim: int, seed: int) -> Tuple[torch.Tensor, Dict]:
    """Clean synthetic encoder for smoke (per memory rule)."""
    rng = np.random.default_rng(seed * 9173 + 11)
    E_np = rng.standard_normal((V, n_dim)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(V), "n_miss": 0, "n_vocab": int(V),
            "pretrain_dim": int(n_dim), "synthetic_smoke": True}
    return E_t, meta


def sparsify_bipolar_gpu(E: torch.Tensor, f: float) -> torch.Tensor:
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
# K=2 cf-RPE+STDP builder (FROZEN from A1; same plasticity across all arms)
# ============================================================================

def build_logits_k2_cfrpe_stdp(E_full: torch.Tensor,
                                idx_train_t: torch.Tensor,
                                idx_held_t: torch.Tensor,
                                n_steps: int, batch: int, lr: float,
                                stdp_w: float,
                                seed: int, arm_idx: int,
                                recall_batch: int, gate_temp: float,
                                ingest_chunk: int) -> Dict:
    """K=2 banks, cf-RPE delta + STDP asymmetric per bank, gate-weighted readout.

    Identical to A1's build_logits_k2_cfrpe_stdp_gpu primitive.
    """
    V, n_dim = E_full.shape
    K = K_BANKS
    N_per = n_dim // K
    device = E_full.device

    E_banks = [E_full[:, k * N_per:(k + 1) * N_per].contiguous() for k in range(K)]

    rng_gate = np.random.default_rng(seed * 7919 + arm_idx * 1013 + 9999)
    W_gate_np = rng_gate.standard_normal((K, N_per)).astype(np.float32)
    W_gate_np /= np.linalg.norm(W_gate_np, axis=1, keepdims=True) + 1e-9
    W_gate = torch.from_numpy(W_gate_np).to(device=device, dtype=TORCH_DTYPE)

    W_banks = [torch.zeros((N_per, N_per), dtype=TORCH_DTYPE, device=device)
               for _ in range(K)]

    t0 = time.time()
    n_pairs = idx_train_t.shape[0] - 1

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        gate_inputs = E_banks[0][idx_train_t[st]]
        raw = gate_inputs @ W_gate.T
        raw = raw / gate_temp
        raw = raw - raw.max(dim=1, keepdim=True).values
        probs_b = torch.exp(raw)
        probs_b = probs_b / (probs_b.sum(dim=1, keepdim=True) + 1e-30)
        for k in range(K):
            Ctx_k = E_banks[k][idx_train_t[st]]
            Nxt_k = E_banks[k][idx_train_t[st + 1]]
            gw = probs_b[:, k:k + 1]
            error_k = Nxt_k - Ctx_k @ W_banks[k].T
            dW_cf_k = (error_k * gw).T @ Ctx_k / float(batch)
            Ctx_kw = Ctx_k * gw
            Nxt_kw = Nxt_k * gw
            dW_stdp_k = (Nxt_kw.T @ Ctx_k - Ctx_kw.T @ Nxt_k) / float(batch)
            dW_k = dW_cf_k + stdp_w * dW_stdp_k
            W_banks[k] = W_banks[k] + lr * dW_k

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    n_h = idx_held_t.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        held_idx = idx_held_t[b:end]
        gate_in = E_banks[0][held_idx]
        raw = gate_in @ W_gate.T
        raw = raw / gate_temp
        raw = raw - raw.max(dim=1, keepdim=True).values
        probs_r = torch.exp(raw)
        probs_r = probs_r / (probs_r.sum(dim=1, keepdim=True) + 1e-30)
        logit_chunk = torch.zeros((end - b, V), dtype=TORCH_DTYPE, device=device)
        for k in range(K):
            ctx_k = E_banks[k][held_idx]
            pred_k = _l2_normalize_t(ctx_k @ W_banks[k].T)
            bank_scores = pred_k @ E_banks[k].T
            logit_chunk = logit_chunk + probs_r[:, k:k + 1] * bank_scores
        logits[b:end] = logit_chunk
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    for _ in range(K):
        del E_banks[0]
    del W_banks, W_gate, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np, "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2)}


# ============================================================================
# Modern-Hopfield cleanup (Ramsauer 2020) -- PARAMETERIZED BY BETA
# ============================================================================

def modern_hopfield_cleanup(logits_np: np.ndarray, E_full: torch.Tensor,
                              beta: float, n_iters: int,
                              recall_batch: int) -> np.ndarray:
    """Apply modern-Hopfield (exponential-energy) cleanup at given beta.

    For each held query:
      Treat logits as similarities to vocab patterns (rows of E).
      Iteratively: state = softmax(beta * logits) @ E -> L2 -> rescore: logits = state @ E.T
    """
    device = E_full.device
    V, dim = E_full.shape
    n_h = logits_np.shape[0]

    logits_t = torch.from_numpy(logits_np).to(device=device, dtype=TORCH_DTYPE)

    cleaned = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)

    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        cur_logits = logits_t[b:end]
        for _ in range(n_iters):
            z = beta * cur_logits
            z = z - z.max(dim=1, keepdim=True).values
            p = torch.exp(z)
            p = p / (p.sum(dim=1, keepdim=True) + 1e-30)
            state = p @ E_full
            state = _l2_normalize_t(state)
            cur_logits = state @ E_full.T
        cleaned[b:end] = cur_logits
        if device.type == "cuda" and (b // recall_batch) % 8 == 0:
            torch.cuda.synchronize()

    out = cleaned.detach().cpu().numpy().astype(np.float32)
    del logits_t, cleaned
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return out


# ============================================================================
# BPC / eval utilities (identical to A1)
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
# Instrumentation self-test (MANDATORY)
# ============================================================================

def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)

    # ST1: K2 cfrpe_stdp builder produces non-zero logits at smoke scale
    V_st = 12
    n_dim_st = 128
    rng_st = np.random.default_rng(0)
    E_np = rng_st.standard_normal((V_st, n_dim_st)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(DEVICE)
    E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F))
    idx_tr_st = torch.tensor(list(range(11)), dtype=torch.long, device=DEVICE)
    idx_h_st = torch.tensor([3, 4, 5, 6, 7], dtype=torch.long, device=DEVICE)
    ar = build_logits_k2_cfrpe_stdp(
        E_sb, idx_tr_st, idx_h_st,
        n_steps=10, batch=4, lr=0.5, stdp_w=0.5,
        seed=0, arm_idx=0, recall_batch=4, gate_temp=GATE_TEMP, ingest_chunk=4,
    )
    assert ar["logits"] is not None, "ST1 logits is None"
    assert ar["logits"].shape == (idx_h_st.shape[0], V_st), "ST1 logits shape mismatch"
    assert not np.all(ar["logits"] == 0.0), "ST1 logits all zero"
    print("[selftest] ST1 K2 cfrpe_stdp logits shape=%s non-zero OK" % str(ar["logits"].shape), flush=True)

    # ST2: MH cleanup is non-identity at beta in {0.5, 1.0, 2.0, 8.0} -- key test
    logits_pre = ar["logits"].copy()
    diffs = []
    for beta_st in [0.5, 1.0, 2.0, 8.0]:
        cleaned = modern_hopfield_cleanup(logits_pre, E_sb, beta=beta_st, n_iters=MH_ITERS, recall_batch=4)
        assert cleaned.shape == logits_pre.shape, "ST2 MH cleanup shape mismatch beta=%.1f" % beta_st
        assert np.all(np.isfinite(cleaned)), "ST2 MH cleanup non-finite beta=%.1f" % beta_st
        d = float(np.abs(logits_pre - cleaned).mean())
        assert d > 1e-6, "ST2 MH cleanup is identity at beta=%.1f: %.2e" % (beta_st, d)
        diffs.append((beta_st, d))
    print("[selftest] ST2 MH cleanup non-identity across betas: %s OK" % diffs, flush=True)

    # ST3: MH cleanup CHANGES OUTPUT with beta (beta=0.5 vs beta=8.0 should differ)
    c_low = modern_hopfield_cleanup(logits_pre, E_sb, beta=0.5, n_iters=MH_ITERS, recall_batch=4)
    c_hi = modern_hopfield_cleanup(logits_pre, E_sb, beta=8.0, n_iters=MH_ITERS, recall_batch=4)
    d_lh = float(np.abs(c_low - c_hi).mean())
    assert d_lh > 1e-6, "ST3 beta=0.5 vs beta=8.0 cleanups identical: %.2e" % d_lh
    print("[selftest] ST3 MH cleanup varies with beta (low vs high diff=%.4e) OK" % d_lh, flush=True)

    # ST4: MH at high beta retrieves clean pattern from corrupted query (Ramsauer 2020 invariant)
    rng_mh = np.random.default_rng(99)
    n_pat = 5
    n_dim_mh = 64
    P_np = (rng_mh.integers(0, 2, size=(n_pat, n_dim_mh)) * 2 - 1).astype(np.float32)
    P_t = torch.from_numpy(_l2_normalize_np(P_np)).to(DEVICE)
    flip_mask = rng_mh.random(n_dim_mh) < 0.10
    q_np = P_np[0].copy()
    q_np[flip_mask] = -q_np[flip_mask]
    q_np = q_np / (np.linalg.norm(q_np) + 1e-8)
    q_logits = (q_np[None, :] @ P_np.T).astype(np.float32)
    cleaned_mh = modern_hopfield_cleanup(q_logits, P_t, beta=8.0, n_iters=MH_ITERS, recall_batch=1)
    cleaned_top1 = int(np.argmax(cleaned_mh[0]))
    assert cleaned_top1 == 0, "ST4 MH cleanup at beta=8 should retrieve pattern 0; got %d" % cleaned_top1
    print("[selftest] ST4 MH cleanup at beta=8 retrieves pattern 0 from 10%-flipped query OK", flush=True)

    # ST5: joint_sweep returns finite metrics across extended TEMP_GRID
    n_tok_st = 40
    n_v_sm = 8
    rng6 = np.random.default_rng(99)
    logits_syn = rng6.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_syn = rng6.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_log_st = np.log(np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32))
    nd = n_tok_st // 2
    jr = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                     nxt_syn[:nd], nxt_syn[nd:])
    assert math.isfinite(jr["bpc_best"]), "ST5 bpc_best not finite"
    assert math.isfinite(jr["top1_acc"]), "ST5 top1_acc not finite"
    assert math.isfinite(jr["mrr_at_10"]), "ST5 mrr_at_10 not finite"
    assert isinstance(jr["per_lambda_T_summary"], dict) and len(jr["per_lambda_T_summary"]) > 0, (
        "ST5 per_lambda_T_summary not captured")
    print("[selftest] ST5 joint_sweep OK (bpc=%.3f top1=%.4f mrr=%.4f, %d lambdas)" % (
        jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"], len(jr["per_lambda_T_summary"])), flush=True)

    # ST6: TEMP_GRID extends beyond 1.0 (per pre-reg)
    assert max(TEMP_GRID) >= 2.0, "ST6 TEMP_GRID must extend beyond 1.0 per pre-reg (max=%.2f)" % max(TEMP_GRID)
    assert min(TEMP_GRID) <= 0.05, "ST6 TEMP_GRID must include sub-0.1 (min=%.4f)" % min(TEMP_GRID)
    print("[selftest] ST6 TEMP_GRID extended (min=%.4f max=%.1f) OK" % (min(TEMP_GRID), max(TEMP_GRID)), flush=True)

    # ST7: LAMBDA_GRID excludes 0.0 (META C7)
    assert 0.0 not in LAMBDA_GRID, "ST7 LAMBDA_GRID must exclude 0.0 (META C7)"
    print("[selftest] ST7 LAMBDA_GRID excludes 0.0 OK", flush=True)

    # ST8: ARMS and ARM_CONFIGS consistent
    for arm in ARMS:
        assert arm in ARM_CONFIGS, "ST8 ARMS entry %r missing from ARM_CONFIGS" % arm
    for arm in ARM_CONFIGS:
        assert arm in ARMS, "ST8 ARM_CONFIGS key %r missing from ARMS" % arm
    print("[selftest] ST8 ARMS/ARM_CONFIGS consistent (%d arms) OK" % len(ARMS), flush=True)

    # ST9: ARM_CONFIGS encodes the documented mh_beta values (no drift)
    expected = {"ARM_BASELINE_NO_CLEANUP": (False, 0.0),
                "ARM_MH_BETA_0p5": (True, 0.5),
                "ARM_MH_BETA_1p0": (True, 1.0),
                "ARM_MH_BETA_2p0": (True, 2.0),
                "ARM_MH_BETA_8p0": (True, 8.0)}
    for arm, (exp_cl, exp_b) in expected.items():
        got_cl = ARM_CONFIGS[arm]["mh_cleanup"]
        got_b = ARM_CONFIGS[arm]["mh_beta"]
        assert got_cl == exp_cl and got_b == exp_b, (
            "ST9 ARM_CONFIGS drift for %s: expected (mh=%s, beta=%.2f) got (mh=%s, beta=%.2f)" % (
                arm, exp_cl, exp_b, got_cl, got_b))
    print("[selftest] ST9 ARM_CONFIGS values match pre-reg expected OK", flush=True)

    # ST10: VERDICT_ARM_SET excludes baseline + beta=8.0 (sanity-rail arms not used for verdict)
    assert "ARM_BASELINE_NO_CLEANUP" not in VERDICT_ARM_SET, "ST10 baseline arm must NOT be in verdict set"
    assert "ARM_MH_BETA_8p0" not in VERDICT_ARM_SET, "ST10 beta=8 arm must NOT be in verdict set (sanity-rail)"
    assert len(VERDICT_ARM_SET) == 3, "ST10 verdict set must be 3 arms, got %d" % len(VERDICT_ARM_SET)
    print("[selftest] ST10 VERDICT_ARM_SET = %s OK" % VERDICT_ARM_SET, flush=True)

    # ST11: LLM call counter == 0 (substrate-only)
    assert _LLM_CALL_COUNTER[0] == 0, "ST11 LLM counter non-zero: %d" % _LLM_CALL_COUNTER[0]
    print("[selftest] ST11 LLM call counter == 0 OK", flush=True)

    # ST12: sparsify_bipolar nnz fraction
    E_chk = torch.from_numpy(
        np.random.default_rng(0).standard_normal((20, 100)).astype(np.float32)
    ).to(DEVICE)
    E_sparse = sparsify_bipolar_gpu(E_chk, 0.05)
    nnz_per_row = (E_sparse != 0).sum(dim=1).cpu().numpy()
    expected_nnz = max(1, int(round(0.05 * 100)))
    assert bool((nnz_per_row == expected_nnz).all()), (
        "ST12 sparse nnz mismatch: expected %d, got %s" % (expected_nnz, str(nnz_per_row[:5])))
    print("[selftest] ST12 sparsify nnz=%d OK" % expected_nnz, flush=True)

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

    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM_TOTAL, str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]), flush=True)

    # Build encoder ONCE per seed
    print("\n[seed=%d] building encoder (V=%d, N_DIM=%d)..." % (seed, V, N_DIM_TOTAL), flush=True)
    t_enc0 = time.time()
    if RUN_MODE == "smoke":
        E_proj_t, w2v_meta = build_E_synthetic_smoke(V, N_DIM_TOTAL, seed)
    else:
        E_proj_t, w2v_meta = build_E_word2vec(vocab, N_DIM_TOTAL, seed)
    encoder_meta.update(w2v_meta)
    E_full = _l2_normalize_t(sparsify_bipolar_gpu(E_proj_t, SPARSE_BIPOLAR_F))
    sparsity = float((E_full != 0).float().mean().item())
    print("[seed=%d] encoder built in %.1fs; w2v_hit=%d/%d sparsity=%.3f" % (
        seed, time.time() - t_enc0, w2v_meta["n_hit"], w2v_meta["n_vocab"], sparsity), flush=True)
    del E_proj_t

    # Move indices once
    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    # Build eval-pair domain (ctx != UNK)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    ctx_eval = ctx_full[mask]
    nxt_eval = nxt_full[mask]
    n_eval = len(ctx_eval)
    if n_eval == 0:
        print("[WARN seed=%d] no valid eval pairs" % seed, flush=True)
        return {"seed": seed, "by_arm": {"ARM_UNIGRAM": uni}, "V": V,
                "N_DIM_TOTAL": N_DIM_TOTAL, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2)}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni, "w2v_meta": w2v_meta}

    # K=2 cf-RPE+STDP is identical across ALL arms; build the per-arm-base logits ONCE per seed.
    # Then for arms with mh_cleanup=True, apply MH at the per-arm beta on top of those logits.
    # CRITICAL: but the K2 builder takes arm_idx into the gate seed -- A1 used distinct arm_idx
    # per arm. Here, all arms share the same K2 substrate so we must use ONE arm_idx for
    # the K2 build. Use arm_idx=0 for the K2 build to keep it determined per seed.
    print("\n[seed=%d] building shared K=2 cf-RPE+STDP logits..." % seed, flush=True)
    t_k2_0 = time.time()
    ar_k2 = build_logits_k2_cfrpe_stdp(
        E_full, idx_train_t, idx_held_t,
        n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR, stdp_w=STDP_WEIGHT,
        seed=seed, arm_idx=0, recall_batch=RECALL_BATCH, gate_temp=GATE_TEMP,
        ingest_chunk=INGEST_CHUNK,
    )
    t_k2 = time.time() - t_k2_0
    print("[seed=%d] K2 logits built in %.1fs (ingest=%.1fs recall=%.1fs)" % (
        seed, t_k2, ar_k2["wall_ingest_s"], ar_k2["wall_recall_s"]), flush=True)
    base_logits = ar_k2["logits"]

    for arm_idx, arm in enumerate(ARMS):
        cfg = ARM_CONFIGS[arm]
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s mh=%s beta=%.2f] computing..." % (
            seed, arm, cfg["mh_cleanup"], cfg["mh_beta"]), flush=True)
        try:
            t_clean0 = time.time()
            if cfg["mh_cleanup"]:
                arm_logits = modern_hopfield_cleanup(
                    base_logits, E_full, beta=cfg["mh_beta"], n_iters=MH_ITERS,
                    recall_batch=RECALL_BATCH,
                )
            else:
                arm_logits = base_logits.copy()
            t_clean = time.time() - t_clean0
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

        logits_full = arm_logits
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
            jr.update({
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "wall_k2_s": round(t_k2, 2),
                "wall_cleanup_s": round(t_clean, 2),
                "raw_bpc_at_T1_L1": round(rbt1, 4),
                "mh_cleanup_applied": bool(cfg["mh_cleanup"]),
                "mh_beta": float(cfg["mh_beta"]),
            })
            by_arm[arm] = jr
            print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f best_T=%.4f rawT1=%.3f elapsed=%.1fs" % (
                seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                jr["best_T_for_bpc"], jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)
            continue

        jr = joint_sweep(logits_eval[:n_dev], logits_eval[n_dev:],
                         U_log, nxt_dev, nxt_test)
        rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval)
        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_k2_s": round(t_k2, 2),
            "wall_cleanup_s": round(t_clean, 2),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "mh_cleanup_applied": bool(cfg["mh_cleanup"]),
            "mh_beta": float(cfg["mh_beta"]),
        })
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f best_T=%.4f rawT1=%.3f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
            jr["best_T_for_bpc"], jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)

    del E_full, base_logits
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N_DIM_TOTAL": N_DIM_TOTAL,
        "N_DIM_PER_BANK": N_DIM_PER_BANK,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "N_STEPS": N_STEPS,
        "run_mode": RUN_MODE,
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "llm_forward_calls_at_inference": int(_LLM_CALL_COUNTER[0]),
        "elapsed_s_seed": round(time.time() - t_seed, 2),
    }


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
    arm_best_T_mean: Dict[str, float] = {}
    for arm in ARMS:
        valid = [u for u in units
                 if not u["by_arm"].get(arm, {}).get("compute_failed", False)
                 and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))]
        if not valid:
            by_arm_agg[arm] = {"bpc_best_mean": float("inf"), "n_valid_seeds": 0,
                               "all_seeds_failed": True}
            arm_bpc[arm] = float("inf")
            arm_cv[arm] = float("nan")
            arm_best_T_mean[arm] = float("nan")
            continue
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid]
        raw_v = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid]
        best_T_v = [u["by_arm"][arm].get("best_T_for_bpc", float("nan")) for u in valid]
        best_lam_v = [u["by_arm"][arm].get("best_lambda_for_bpc", float("nan")) for u in valid]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "top1_acc_std": round(float(np.std(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_v)), 4),
            "best_T_for_bpc_mean": round(float(np.nanmean(best_T_v)), 4),
            "best_T_for_bpc_per_seed": [round(float(t), 4) for t in best_T_v],
            "best_lambda_for_bpc_mean": round(float(np.nanmean(best_lam_v)), 4),
            "mh_beta": float(ARM_CONFIGS[arm]["mh_beta"]),
            "mh_cleanup_applied": bool(ARM_CONFIGS[arm]["mh_cleanup"]),
            "n_valid_seeds": len(valid),
            "all_seeds_failed": False,
        }
        arm_bpc[arm] = b_mean
        arm_cv[arm] = b_cv
        arm_best_T_mean[arm] = float(np.nanmean(best_T_v))

    # Sanity rails
    no_cleanup_bpc = arm_bpc.get("ARM_BASELINE_NO_CLEANUP", float("inf"))
    beta8_bpc = arm_bpc.get("ARM_MH_BETA_8p0", float("inf"))

    no_cleanup_drift = abs(no_cleanup_bpc - SANITY_RAIL_NO_CLEANUP_REF) if math.isfinite(no_cleanup_bpc) else float("inf")
    beta8_drift = abs(beta8_bpc - SANITY_RAIL_BETA8_REF) if math.isfinite(beta8_bpc) else float("inf")

    no_cleanup_rail_ok = no_cleanup_drift <= SANITY_RAIL_NO_CLEANUP_TOL
    beta8_rail_ok = beta8_drift <= SANITY_RAIL_BETA8_TOL

    # Best MH-beta arm (across verdict-eligible arms only)
    verdict_arm_bpcs = {a: arm_bpc[a] for a in VERDICT_ARM_SET if math.isfinite(arm_bpc.get(a, float("inf")))}
    if verdict_arm_bpcs:
        best_mh_arm = min(verdict_arm_bpcs, key=lambda a: verdict_arm_bpcs[a])
        best_mh_bpc = verdict_arm_bpcs[best_mh_arm]
        best_mh_cv = arm_cv.get(best_mh_arm, float("nan"))
    else:
        best_mh_arm = None
        best_mh_bpc = float("inf")
        best_mh_cv = float("nan")

    # best_T progression across betas (decisive secondary signal)
    best_T_progression = {
        "ARM_BASELINE_NO_CLEANUP": round(arm_best_T_mean.get("ARM_BASELINE_NO_CLEANUP", float("nan")), 4),
        "ARM_MH_BETA_0p5":         round(arm_best_T_mean.get("ARM_MH_BETA_0p5", float("nan")), 4),
        "ARM_MH_BETA_1p0":         round(arm_best_T_mean.get("ARM_MH_BETA_1p0", float("nan")), 4),
        "ARM_MH_BETA_2p0":         round(arm_best_T_mean.get("ARM_MH_BETA_2p0", float("nan")), 4),
        "ARM_MH_BETA_8p0":         round(arm_best_T_mean.get("ARM_MH_BETA_8p0", float("nan")), 4),
    }

    arm_summary = (
        "uni=%.3f | NO_CLEANUP=%.4f(drift=%+.4f,rail=%s,best_T=%.3f) | "
        "BETA0.5=%.4f(best_T=%.3f) | BETA1.0=%.4f(best_T=%.3f) | "
        "BETA2.0=%.4f(best_T=%.3f) | BETA8.0=%.4f(drift=%+.4f,rail=%s,best_T=%.3f) | "
        "best_mh=%s @%.4f cv=%.3f"
    ) % (
        unigram_bpc,
        no_cleanup_bpc, no_cleanup_bpc - SANITY_RAIL_NO_CLEANUP_REF,
        str(no_cleanup_rail_ok), best_T_progression["ARM_BASELINE_NO_CLEANUP"],
        arm_bpc.get("ARM_MH_BETA_0p5", float("inf")), best_T_progression["ARM_MH_BETA_0p5"],
        arm_bpc.get("ARM_MH_BETA_1p0", float("inf")), best_T_progression["ARM_MH_BETA_1p0"],
        arm_bpc.get("ARM_MH_BETA_2p0", float("inf")), best_T_progression["ARM_MH_BETA_2p0"],
        beta8_bpc, beta8_bpc - SANITY_RAIL_BETA8_REF,
        str(beta8_rail_ok), best_T_progression["ARM_MH_BETA_8p0"],
        str(best_mh_arm), best_mh_bpc,
        best_mh_cv if math.isfinite(best_mh_cv) else -1.0,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "sanity_rails": {
            "no_cleanup_ref": SANITY_RAIL_NO_CLEANUP_REF,
            "no_cleanup_drift": round(no_cleanup_drift, 4),
            "no_cleanup_rail_ok": bool(no_cleanup_rail_ok),
            "no_cleanup_tol": SANITY_RAIL_NO_CLEANUP_TOL,
            "beta8_ref": SANITY_RAIL_BETA8_REF,
            "beta8_drift": round(beta8_drift, 4),
            "beta8_rail_ok": bool(beta8_rail_ok),
            "beta8_tol": SANITY_RAIL_BETA8_TOL,
        },
        "bands": {
            "hard_pass_bpc_ceiling": HARD_PASS_BPC_CEILING,
            "middle_band_bpc_lower": MIDDLE_BAND_BPC_LOWER,
            "middle_band_bpc_upper": MIDDLE_BAND_BPC_UPPER,
            "hard_fail_bpc_floor": HARD_FAIL_BPC_FLOOR,
            "cv_max": CV_MAX,
        },
        "best_mh_arm": best_mh_arm,
        "best_mh_bpc": round(best_mh_bpc, 4),
        "best_mh_cv": round(best_mh_cv, 4) if math.isfinite(best_mh_cv) else None,
        "verdict_arm_set": VERDICT_ARM_SET,
        "best_T_progression": best_T_progression,
        "no_cleanup_bpc": round(no_cleanup_bpc, 4),
        "beta8_bpc": round(beta8_bpc, 4),
        "n_seeds": len(units),
        "unigram_bpc": round(unigram_bpc, 4),
        "honest_scope": (
            "MH cleanup beta-sweep drill on top of FROZEN K=2 cf-RPE+STDP plasticity. "
            "Tests whether SOFTENING the modern-Hopfield attractor restores soft predictive "
            "distribution (symptomatic) vs whether collapse persists at all betas (structural). "
            "MH_ITERS held fixed at 3; only beta varies. Extended TEMP_GRID to [0.01..5.0] to catch "
            "any new optimum a softer MH might place outside A1's window. "
            "WHAT_THIS_DOES_NOT_SHOW: MH_ITERS varied, cleanup-at-different-stage (e.g. on W "
            "rather than logits), or alternative cleanup primitives. Result is text8 V=4000 only."
        ),
        "cites": [
            "data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json (A1 provenance)",
            "experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py (A1 reference cell)",
            "notes/exp_dev_handoff_composition_collapse_drill_2026-06-24.md",
        ],
    }

    # Substrate-only audit gate
    total_llm_calls = sum(int(u.get("llm_forward_calls_at_inference", 0)) for u in units)
    detail["llm_forward_calls_total"] = total_llm_calls
    if total_llm_calls != 0:
        return ("HARD_FAIL",
                "HARD_FAIL_LLM_CALL: llm_calls=%d (substrate-only invariant). %s" % (
                    total_llm_calls, arm_summary),
                detail)

    if best_mh_arm is None:
        return ("HARD_FAIL",
                "HARD_FAIL: all MH-beta verdict arms failed to produce finite BPC. %s" % arm_summary,
                detail)

    # Provenance rails (full mode only)
    detail["provenance_check_active"] = (RUN_MODE == "full")
    if RUN_MODE == "full":
        if not no_cleanup_rail_ok:
            return ("HARD_FAIL_PROVENANCE",
                    "HARD_FAIL_PROVENANCE_NO_CLEANUP: ARM_BASELINE_NO_CLEANUP=%.4f drifts %.4f "
                    "from A1 K2 ref %.4f (>tol %.2f). K=2 cf-RPE+STDP pipeline mismatch with A1. %s" % (
                        no_cleanup_bpc, no_cleanup_drift, SANITY_RAIL_NO_CLEANUP_REF,
                        SANITY_RAIL_NO_CLEANUP_TOL, arm_summary),
                    detail)
        if not beta8_rail_ok:
            return ("HARD_FAIL_PROVENANCE",
                    "HARD_FAIL_PROVENANCE_BETA8: ARM_MH_BETA_8p0=%.4f drifts %.4f from "
                    "A1 FULL_JOINT ref %.4f (>tol %.2f). MH cleanup at beta=8 reproduce mismatch. %s" % (
                        beta8_bpc, beta8_drift, SANITY_RAIL_BETA8_REF,
                        SANITY_RAIL_BETA8_TOL, arm_summary),
                    detail)

    # cv gate on best MH-beta arm
    if math.isfinite(best_mh_cv) and best_mh_cv > CV_MAX:
        return ("MIDDLE_BAND_HIGH_CV",
                "MIDDLE_BAND_HIGH_CV: best MH arm %s cv=%.3f > %.2f mandatory. "
                "best_mh_bpc=%.4f. %s" % (
                    best_mh_arm, best_mh_cv, CV_MAX, best_mh_bpc, arm_summary),
                detail)

    # Verdict bands
    if math.isfinite(best_mh_bpc) and best_mh_bpc <= HARD_PASS_BPC_CEILING:
        detail["verdict_tier"] = "HARD_PASS_SYMPTOMATIC"
        return ("HARD_PASS",
                "HARD_PASS_SYMPTOMATIC: best MH arm %s BPC=%.4f <= %.2f. Softer MH beta beats "
                "no-cleanup baseline; A1 collapse was beta-driven (symptomatic). Re-issue compose "
                "cells with beta in this range. %s" % (
                    best_mh_arm, best_mh_bpc, HARD_PASS_BPC_CEILING, arm_summary),
                detail)

    if math.isfinite(best_mh_bpc) and MIDDLE_BAND_BPC_LOWER <= best_mh_bpc <= MIDDLE_BAND_BPC_UPPER:
        detail["verdict_tier"] = "MIDDLE_BAND_NEUTRAL"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_NEUTRAL: best MH arm %s BPC=%.4f in [%.2f, %.2f]. Softer MH neutral "
                "vs no-cleanup baseline; cleanup is not load-bearing at smaller beta. %s" % (
                    best_mh_arm, best_mh_bpc, MIDDLE_BAND_BPC_LOWER, MIDDLE_BAND_BPC_UPPER,
                    arm_summary),
                detail)

    if math.isfinite(best_mh_bpc) and best_mh_bpc >= HARD_FAIL_BPC_FLOOR:
        detail["verdict_tier"] = "HARD_FAIL_STRUCTURAL"
        return ("HARD_FAIL",
                "HARD_FAIL_STRUCTURAL: best MH arm %s BPC=%.4f >= %.2f. Softening MH beta does NOT "
                "rescue; collapse is STRUCTURAL (objectives inverted via E re-projection). Path "
                "forward = cross-layer architecture, not hyperparameter fix. %s" % (
                    best_mh_arm, best_mh_bpc, HARD_FAIL_BPC_FLOOR, arm_summary),
                detail)

    # Else: BPC in (MIDDLE_BAND_BPC_UPPER, HARD_FAIL_BPC_FLOOR) -> MIDDLE_BAND inter-gap
    detail["verdict_tier"] = "MIDDLE_BAND_INTER_GAP"
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_INTER_GAP: best MH arm %s BPC=%.4f between MB ceiling %.2f and "
            "HARD_FAIL floor %.2f. Marginal cleanup utility. %s" % (
                best_mh_arm, best_mh_bpc, MIDDLE_BAND_BPC_UPPER, HARD_FAIL_BPC_FLOOR,
                arm_summary),
            detail)


# ============================================================================
# Main loop with per-seed checkpoint
# ============================================================================

print("[config] %s" % CONFIG_VERSION, flush=True)
print("[config] device=%s torch_cuda_available=%s" % (str(DEVICE), torch.cuda.is_available()),
      flush=True)

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

# REQUIRED_FIELDS: verdict, verdict_msg, elapsed_s, summary
summary_str = (
    "%s | arms=%d seeds=%d N_DIM=%d N_TRAIN=%d encoder=word2vec_sparse_bipolar mh_iters=%d" % (
        verdict, len(ARMS), len(SEEDS), N_DIM_TOTAL, N_TRAIN, MH_ITERS)
)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": summary_str,
    "config_version": CONFIG_VERSION,
    "run_mode": RUN_MODE,
    "device": str(DEVICE),
    "N_DIM_TOTAL": N_DIM_TOTAL,
    "N_DIM_PER_BANK": N_DIM_PER_BANK,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "N_STEPS": N_STEPS,
    "K_BANKS": K_BANKS,
    "GATE_TEMP": GATE_TEMP,
    "CFRPE_LR": CFRPE_LR,
    "STDP_WEIGHT": STDP_WEIGHT,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "MH_ITERS": MH_ITERS,
    "MH_BETAS": [ARM_CONFIGS[a]["mh_beta"] for a in ARMS],
    "TEMP_GRID": TEMP_GRID,
    "LAMBDA_GRID": LAMBDA_GRID,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "VERDICT_ARM_SET": VERDICT_ARM_SET,
    "detail": detail,
    "per_seed": [
        {"seed": u.get("seed"), "by_arm": u.get("by_arm"),
         "V": u.get("V"), "N_DIM_TOTAL": u.get("N_DIM_TOTAL"),
         "N_TRAIN": u.get("N_TRAIN"),
         "llm_forward_calls_at_inference": u.get("llm_forward_calls_at_inference", 0),
         "encoder_meta": u.get("encoder_meta", {}),
         "elapsed_s_seed": u.get("elapsed_s_seed")}
        for u in all_units
    ],
    "elapsed_s": round(sum(u.get("elapsed_s_seed", 0.0) for u in all_units), 2),
}

if DEVICE.type == "cuda":
    try:
        peak_gb = torch.cuda.max_memory_allocated(0) / 1e9
        print("[gpu] peak memory %.3f GB" % peak_gb, flush=True)
        metrics["gpu_peak_mem_gb"] = round(peak_gb, 3)
    except Exception:
        pass

write_metrics(out_dir, metrics, all_units)
print("[metrics] written to %s" % out_dir, flush=True)
