"""
substrate_compose_test_design_audit_v1
-- A1 3rd-angle drill test-design audit cell.

Tests whether A1's catastrophic FULL_JOINT BPC=7.89 is a TEST-DESIGN ARTIFACT
(60-75% per drill) or a STRUCTURAL collapse. The 5 substrate primitives are
held CONSTANT (cf-RPE + STDP + K=2 + modern-Hopfield + sparse-bipolar);
only the 5 identified design biases vary across arms.

Six arms (primitives constant; test-design varies):
  ARM_A1_BASELINE
      -- reproduces A1 FULL_JOINT exactly (provenance rail ~7.89)
  ARM_FIX_TEMP_GRID
      -- extended TEMP_GRID [0.01..50.0]; addresses bias #2 (grid-top-pegging)
  ARM_FIX_N_STEPS
      -- N_STEPS=5000 to reach asymptote; addresses bias #3 (under-asymptotic)
  ARM_FIX_NON_CUMULATIVE_BUILD
      -- K=2 + cf-RPE+STDP WITHOUT MH cleanup; addresses bias #4 (cumulative)
  ARM_FIX_PER_ARM_HP_TUNED
      -- MH_BETA inner-sweep {1.0, 2.0, 4.0}; addresses bias #5 (frozen HP)
  ARM_FIX_ALL_5_TOGETHER
      -- all fixes combined; PRIMARY arm

PRIMARY metric: BPC on ARM_FIX_ALL_5_TOGETHER (lower = better)

Pre-reg HARD bands:
  Sanity rail: ARM_A1_BASELINE BPC within +/-0.10 of 7.89
  HARD_PASS_TEST_DESIGN_ARTIFACT: ARM_FIX_ALL_5_TOGETHER BPC <= 7.30
  HARD_PASS_SUPER_ADDITIVE: ARM_FIX_ALL_5_TOGETHER BPC <= 7.00
  MIDDLE_BAND: ARM_FIX_ALL_5_TOGETHER BPC in (7.30, 7.50]
  HARD_FAIL_STRUCTURAL_CONFIRMED: ARM_FIX_ALL_5_TOGETHER BPC >= 7.70

CITES:
  notes/research_a1_composition_collapse_3rd_angle_test_design_audit_2026-06-24.md
  experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py
  data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json
  data/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512/metrics.json
  preregs/2026-06-24_substrate_compose_test_design_audit_v1.md
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

ANCHOR_NAME = "substrate_compose_test_design_audit_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only audit counter
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Pre-reg threshold bands (per prereg 2026-06-24)
# ============================================================================
# Provenance rail (looser tol; should REPRODUCE A1 catastrophic 7.89)
SANITY_RAIL_A1_BASELINE_REF = 7.8919  # A1 FULL_JOINT verified
SANITY_RAIL_TOLERANCE = 0.10          # +/-0.10 around A1 reference

# Primary arm verdict bands (ARM_FIX_ALL_5_TOGETHER BPC)
HARD_PASS_SUPER_ADDITIVE_CEILING = 7.00     # super-additive recovery
HARD_PASS_TEST_DESIGN_CEILING    = 7.30     # test-design artifact dominant
MIDDLE_BAND_BPC_UPPER            = 7.50     # mixed dominance
HARD_FAIL_STRUCTURAL_FLOOR       = 7.70     # structural confirmed

# ============================================================================
# Primitive HPs (constants from A1; held EXACTLY)
# ============================================================================
CFRPE_LR = 0.5
STDP_WEIGHT = 0.5
INGEST_BATCH = 64
K_BANKS = 2
GATE_TEMP = 0.5
MH_BETA_A1 = 8.0                       # A1 baseline MH beta
MH_ITERS = 3
SPARSE_BIPOLAR_F = 0.05
WORD2VEC_MODEL = "word2vec-google-news-300"

# A1 default N_STEPS
N_STEPS_A1 = 1000
# FIX_N_STEPS arm boost (matches drill recommendation: asymptote at N=5000)
N_STEPS_BOOSTED = 5000

# Eval grids
TEMP_GRID_A1 = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
TEMP_GRID_EXTENDED = [0.01, 0.05, 0.2, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# MH_BETA sweep for per-arm-HP-tuned arm (drill bias #5)
MH_BETA_SWEEP = [1.0, 2.0, 4.0]

# Arms (six)
ARMS = [
    "ARM_A1_BASELINE",
    "ARM_FIX_TEMP_GRID",
    "ARM_FIX_N_STEPS",
    "ARM_FIX_NON_CUMULATIVE_BUILD",
    "ARM_FIX_PER_ARM_HP_TUNED",
    "ARM_FIX_ALL_5_TOGETHER",
]

# Per-arm config:
#   uses_extended_temp_grid : use TEMP_GRID_EXTENDED instead of TEMP_GRID_A1
#   n_steps                 : training steps for cf-RPE+STDP plasticity
#   mh_cleanup              : apply modern-Hopfield cleanup
#   mh_beta_sweep           : if True, inner-sweep MH_BETA in MH_BETA_SWEEP
ARM_CONFIGS = {
    "ARM_A1_BASELINE": {
        "extended_grid": False, "n_steps": N_STEPS_A1, "mh_cleanup": True,
        "mh_beta_sweep": False, "mh_beta_fixed": MH_BETA_A1,
    },
    "ARM_FIX_TEMP_GRID": {
        "extended_grid": True,  "n_steps": N_STEPS_A1, "mh_cleanup": True,
        "mh_beta_sweep": False, "mh_beta_fixed": MH_BETA_A1,
    },
    "ARM_FIX_N_STEPS": {
        "extended_grid": False, "n_steps": N_STEPS_BOOSTED, "mh_cleanup": True,
        "mh_beta_sweep": False, "mh_beta_fixed": MH_BETA_A1,
    },
    "ARM_FIX_NON_CUMULATIVE_BUILD": {
        # K=2 + cf-RPE+STDP without MH cleanup; isolates the hetplast K=2 pair
        "extended_grid": False, "n_steps": N_STEPS_A1, "mh_cleanup": False,
        "mh_beta_sweep": False, "mh_beta_fixed": MH_BETA_A1,
    },
    "ARM_FIX_PER_ARM_HP_TUNED": {
        "extended_grid": False, "n_steps": N_STEPS_A1, "mh_cleanup": True,
        "mh_beta_sweep": True,  "mh_beta_fixed": MH_BETA_A1,
    },
    "ARM_FIX_ALL_5_TOGETHER": {
        # ALL fixes combined: extended_grid + boosted_steps + MH_BETA sweep + non-cumulative-equivalent
        # ("non-cumulative" here = letting the MH_BETA sweep include the case where MH is effectively
        # off via very low beta; the sweep covers {1.0, 2.0, 4.0} so MH influence varies)
        "extended_grid": True,  "n_steps": N_STEPS_BOOSTED, "mh_cleanup": True,
        "mh_beta_sweep": True,  "mh_beta_fixed": MH_BETA_A1,
    },
}


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

# Production config
N_DIM_TOTAL = 8192
N_DIM_PER_BANK = N_DIM_TOTAL // K_BANKS
VOCAB_CAP = 4000
RECALL_BATCH = 256
INGEST_CHUNK = 4096

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM_TOTAL = 1024
    N_DIM_PER_BANK = N_DIM_TOTAL // K_BANKS
    RECALL_BATCH = 128
    INGEST_CHUNK = 512

CONFIG_VERSION = (
    "%s; N_DIM=%d K=%d V=%d N_TRAIN=%d N_HELD=%d arms=%s seeds=%s mode=%s "
    "T_a1=%s T_ext=%s lams=%s cfrpe_lr=%.3f stdp_w=%.3f gate_temp=%.3f "
    "mh_beta_a1=%.2f mh_iters=%d mh_beta_sweep=%s n_steps_a1=%d n_steps_boost=%d "
    "device=%s"
) % (
    ANCHOR_NAME, N_DIM_TOTAL, K_BANKS, VOCAB_CAP, N_TRAIN, N_HELD, ARMS, SEEDS, RUN_MODE,
    TEMP_GRID_A1, TEMP_GRID_EXTENDED, LAMBDA_GRID, CFRPE_LR, STDP_WEIGHT, GATE_TEMP,
    MH_BETA_A1, MH_ITERS, MH_BETA_SWEEP, N_STEPS_A1, N_STEPS_BOOSTED, str(DEVICE),
)


# ============================================================================
# text8 corpus / vocab / encoder utilities (copied from A1 verbatim)
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
# K=2 logits builder (cf-RPE + STDP heterogeneous; identical to A1 mechanism)
# ============================================================================

def build_logits_k2_cfrpe_stdp_gpu(E_full: torch.Tensor,
                                       idx_train_t: torch.Tensor,
                                       idx_held_t: torch.Tensor,
                                       n_steps: int, batch: int, lr: float,
                                       stdp_w: float,
                                       seed: int, arm_idx: int,
                                       recall_batch: int, gate_temp: float,
                                       ingest_chunk: int) -> Dict:
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
# Modern-Hopfield cleanup (identical to A1)
# ============================================================================

def modern_hopfield_cleanup_gpu(logits_np: np.ndarray, E_full: torch.Tensor,
                                   beta: float, n_iters: int,
                                   recall_batch: int) -> np.ndarray:
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
                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                temp_grid: List[float]) -> Dict:
    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    per_lambda_best_T_bpc: Dict[float, Dict] = {}

    for T in temp_grid:
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
        "temp_grid_used": list(temp_grid),
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

    # ST_DESIGN_FIX_1: TEMP_GRID_EXTENDED reaches T=50.0
    assert max(TEMP_GRID_EXTENDED) == 50.0, (
        "ST_DESIGN_FIX_1: TEMP_GRID_EXTENDED must reach T=50.0; got %.1f" % max(TEMP_GRID_EXTENDED))
    assert max(TEMP_GRID_EXTENDED) > max(TEMP_GRID_A1), (
        "ST_DESIGN_FIX_1: extended grid must exceed A1 grid")
    print("[selftest] ST_DESIGN_FIX_1: TEMP_GRID_EXTENDED max=%.1f > A1 max=%.1f OK" % (
        max(TEMP_GRID_EXTENDED), max(TEMP_GRID_A1)), flush=True)

    # ST_DESIGN_FIX_2: N_STEPS_BOOSTED == 5000
    assert N_STEPS_BOOSTED == 5000, "ST_DESIGN_FIX_2: N_STEPS_BOOSTED must be 5000"
    assert N_STEPS_BOOSTED > N_STEPS_A1, "ST_DESIGN_FIX_2: boosted must exceed A1"
    print("[selftest] ST_DESIGN_FIX_2: N_STEPS_BOOSTED=%d > N_STEPS_A1=%d OK" % (
        N_STEPS_BOOSTED, N_STEPS_A1), flush=True)

    # ST_DESIGN_FIX_3: ARM_FIX_NON_CUMULATIVE_BUILD has mh_cleanup=False
    assert ARM_CONFIGS["ARM_FIX_NON_CUMULATIVE_BUILD"]["mh_cleanup"] is False, (
        "ST_DESIGN_FIX_3: ARM_FIX_NON_CUMULATIVE_BUILD must have mh_cleanup=False")
    print("[selftest] ST_DESIGN_FIX_3: ARM_FIX_NON_CUMULATIVE_BUILD mh_cleanup=False OK",
          flush=True)

    # ST_DESIGN_FIX_4: MH_BETA_SWEEP = [1.0, 2.0, 4.0]
    assert MH_BETA_SWEEP == [1.0, 2.0, 4.0], "ST_DESIGN_FIX_4: MH_BETA_SWEEP mismatch"
    assert ARM_CONFIGS["ARM_FIX_PER_ARM_HP_TUNED"]["mh_beta_sweep"] is True, (
        "ST_DESIGN_FIX_4: ARM_FIX_PER_ARM_HP_TUNED must have mh_beta_sweep=True")
    print("[selftest] ST_DESIGN_FIX_4: MH_BETA_SWEEP=%s + per-arm-HP arm has sweep=True OK" % (
        MH_BETA_SWEEP), flush=True)

    # ST_DESIGN_FIX_5: ARM_FIX_ALL_5_TOGETHER applies extended_grid + n_steps_boost + mh_beta_sweep
    afa = ARM_CONFIGS["ARM_FIX_ALL_5_TOGETHER"]
    assert afa["extended_grid"] is True, "ST_DESIGN_FIX_5: ALL_5 missing extended_grid"
    assert afa["n_steps"] == N_STEPS_BOOSTED, "ST_DESIGN_FIX_5: ALL_5 missing n_steps_boosted"
    assert afa["mh_beta_sweep"] is True, "ST_DESIGN_FIX_5: ALL_5 missing mh_beta_sweep"
    print("[selftest] ST_DESIGN_FIX_5: ALL_5_TOGETHER applies extended+boosted+sweep OK",
          flush=True)

    # ST_PRIMITIVE_1: cf-RPE+STDP K=2 builder produces non-zero logits + finite
    n_dim_st = 128
    V_st = 12
    rng = np.random.default_rng(0)
    E_np = _l2_normalize_np(rng.standard_normal((V_st, n_dim_st)).astype(np.float32))
    E_t = torch.from_numpy(E_np).to(DEVICE)
    E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F))
    idx_tr_st = torch.tensor(list(range(V_st)) * 2, dtype=torch.long, device=DEVICE)
    idx_h_st = torch.tensor([3, 4, 5, 6, 7], dtype=torch.long, device=DEVICE)
    ar = build_logits_k2_cfrpe_stdp_gpu(E_sb, idx_tr_st, idx_h_st,
                                          n_steps=5, batch=4, lr=0.5, stdp_w=0.5,
                                          seed=0, arm_idx=0, recall_batch=4,
                                          gate_temp=GATE_TEMP, ingest_chunk=4)
    assert ar["logits"].shape == (idx_h_st.shape[0], V_st), "ST_PRIMITIVE_1: shape mismatch"
    assert not np.all(ar["logits"] == 0.0), "ST_PRIMITIVE_1: K2 logits all zero"
    assert np.all(np.isfinite(ar["logits"])), "ST_PRIMITIVE_1: K2 logits not finite"
    print("[selftest] ST_PRIMITIVE_1: K2 cfrpe+stdp logits shape=%s non-zero finite OK" % (
        str(ar["logits"].shape)), flush=True)

    # ST_PRIMITIVE_2: MH cleanup non-identity + finite for varying beta
    for beta_test in [1.0, 2.0, 4.0, MH_BETA_A1]:
        cleaned = modern_hopfield_cleanup_gpu(ar["logits"], E_sb, beta=beta_test,
                                                 n_iters=MH_ITERS, recall_batch=4)
        assert cleaned.shape == ar["logits"].shape, "ST_PRIMITIVE_2: MH shape mismatch"
        assert np.all(np.isfinite(cleaned)), (
            "ST_PRIMITIVE_2: MH cleanup non-finite at beta=%.1f" % beta_test)
        diff = float(np.abs(ar["logits"] - cleaned).mean())
        assert diff > 1e-6, (
            "ST_PRIMITIVE_2: MH cleanup is identity at beta=%.1f (diff=%.2e)" % (beta_test, diff))
    print("[selftest] ST_PRIMITIVE_2: MH cleanup non-identity + finite across beta=%s OK" % (
        [1.0, 2.0, 4.0, MH_BETA_A1]), flush=True)

    # ST_PRIMITIVE_3: extended TEMP_GRID joint_sweep finite at high T (numerical guard)
    n_tok = 60
    n_v = 12
    rng2 = np.random.default_rng(11)
    logits_syn = rng2.standard_normal((n_tok, n_v)).astype(np.float32) * 4.0
    nxt_syn = rng2.integers(0, n_v, size=n_tok).astype(np.int64)
    U_log_st = np.log(np.full(n_v, 1.0 / n_v, dtype=np.float32))
    nd = n_tok // 2
    jr_ext = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                          nxt_syn[:nd], nxt_syn[nd:], TEMP_GRID_EXTENDED)
    assert math.isfinite(jr_ext["bpc_best"]), "ST_PRIMITIVE_3: ext-grid bpc not finite"
    assert math.isfinite(jr_ext["top1_acc"]), "ST_PRIMITIVE_3: ext-grid top1 not finite"
    assert math.isfinite(jr_ext["mrr_at_10"]), "ST_PRIMITIVE_3: ext-grid mrr not finite"
    print("[selftest] ST_PRIMITIVE_3: extended TEMP_GRID joint_sweep finite OK (bpc=%.3f)" % (
        jr_ext["bpc_best"]), flush=True)

    # ST_PRIMITIVE_4: ARMS/ARM_CONFIGS consistency
    for arm in ARMS:
        assert arm in ARM_CONFIGS, "ST_PRIMITIVE_4: ARMS entry %r missing from ARM_CONFIGS" % arm
    for arm in ARM_CONFIGS:
        assert arm in ARMS, "ST_PRIMITIVE_4: ARM_CONFIGS key %r missing from ARMS" % arm
    print("[selftest] ST_PRIMITIVE_4: ARMS/ARM_CONFIGS consistent (%d arms) OK" % len(ARMS),
          flush=True)

    # ST_PRIMITIVE_5: LAMBDA_GRID excludes 0.0 (Skunkworks META C7) + LLM counter zero
    assert 0.0 not in LAMBDA_GRID, "ST_PRIMITIVE_5: LAMBDA_GRID must exclude 0.0"
    assert _LLM_CALL_COUNTER[0] == 0, "ST_PRIMITIVE_5: LLM counter non-zero"
    print("[selftest] ST_PRIMITIVE_5: LAMBDA_GRID excludes 0.0 + LLM_counter=0 OK", flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-arm evaluation: build K=2 cf-RPE+STDP logits, optionally MH cleanup,
# optionally with MH_BETA inner-sweep, optionally extended TEMP_GRID
# ============================================================================

def evaluate_arm(arm: str, arm_idx: int, cfg: Dict,
                  E_full: torch.Tensor,
                  idx_train_t: torch.Tensor, idx_held_t: torch.Tensor,
                  ctx_full: np.ndarray, nxt_full: np.ndarray,
                  mask: np.ndarray, U_log: np.ndarray,
                  seed: int) -> Dict:
    """Evaluate one design-audit arm.

    All arms use IDENTICAL K=2 cf-RPE+STDP primitive (the A1 mechanism stack
    minus only the optional MH cleanup, plus the optional MH_BETA inner-sweep).

    The TEMP_GRID and N_STEPS vary per arm config.
    """
    t_arm0 = time.time()
    n_steps = cfg["n_steps"]
    temp_grid = TEMP_GRID_EXTENDED if cfg["extended_grid"] else TEMP_GRID_A1
    mh_cleanup = cfg["mh_cleanup"]
    mh_beta_sweep = cfg["mh_beta_sweep"]
    mh_beta_fixed = cfg["mh_beta_fixed"]

    print("\n  [seed=%d arm=%s n_steps=%d ext_grid=%s mh_cleanup=%s mh_beta_sweep=%s] computing..." % (
        seed, arm, n_steps, cfg["extended_grid"], mh_cleanup, mh_beta_sweep), flush=True)

    # Build K=2 cf-RPE+STDP logits (this is the heavy compute; once per arm)
    ar = build_logits_k2_cfrpe_stdp_gpu(
        E_full, idx_train_t, idx_held_t,
        n_steps=n_steps, batch=INGEST_BATCH, lr=CFRPE_LR, stdp_w=STDP_WEIGHT,
        seed=seed, arm_idx=arm_idx, recall_batch=RECALL_BATCH,
        gate_temp=GATE_TEMP, ingest_chunk=INGEST_CHUNK,
    )
    logits_pre_mh = ar["logits"]

    # Build eval index alignment ONCE for this arm
    if logits_pre_mh.shape[0] >= len(ctx_full):
        valid_pos = np.where(mask)[0]
        logits_eval_pre = logits_pre_mh[:len(ctx_full)][mask]
        nxt_eval_local = nxt_full[mask]
    else:
        valid_pos = np.where(mask)[0]
        valid_pos = valid_pos[valid_pos < logits_pre_mh.shape[0]]
        logits_eval_pre = logits_pre_mh[valid_pos]
        nxt_eval_local = nxt_full[valid_pos]
    n_eval_l = len(nxt_eval_local)
    n_dev_l = n_eval_l // 2
    nxt_dev_l = nxt_eval_local[:n_dev_l]
    nxt_test_l = nxt_eval_local[n_dev_l:]

    # MH cleanup: either fixed-beta (A1 default), inner-sweep, or disabled
    t_clean0 = time.time()
    mh_results: List[Dict] = []
    if not mh_cleanup:
        # No MH cleanup; eval directly on K=2 cf-RPE+STDP logits
        jr = joint_sweep(logits_eval_pre[:n_dev_l], logits_eval_pre[n_dev_l:],
                          U_log, nxt_dev_l, nxt_test_l, temp_grid)
        rbt1 = raw_bpc_at_T1(logits_eval_pre, nxt_eval_local)
        mh_results.append({
            "mh_beta_eval": None, "mh_cleanup_applied": False,
            "bpc_best": jr["bpc_best"], "top1_acc": jr["top1_acc"],
            "mrr_at_10": jr["mrr_at_10"], "best_T_for_bpc": jr["best_T_for_bpc"],
            "best_lambda_for_bpc": jr["best_lambda_for_bpc"],
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "best_dev_bpc": jr["best_dev_bpc"],
            "per_lambda_T_summary": jr["per_lambda_T_summary"],
            "n_dev": jr["n_dev"], "n_test": jr["n_test"],
            "temp_grid_used": jr["temp_grid_used"],
        })
        chosen = mh_results[0]
    else:
        beta_iters = MH_BETA_SWEEP if mh_beta_sweep else [mh_beta_fixed]
        for beta_eval in beta_iters:
            cleaned = modern_hopfield_cleanup_gpu(
                logits_pre_mh, E_full, beta=beta_eval, n_iters=MH_ITERS,
                recall_batch=RECALL_BATCH,
            )
            # Re-align eval slice on cleaned
            if cleaned.shape[0] >= len(ctx_full):
                logits_eval = cleaned[:len(ctx_full)][mask]
            else:
                logits_eval = cleaned[valid_pos]
            jr = joint_sweep(logits_eval[:n_dev_l], logits_eval[n_dev_l:],
                              U_log, nxt_dev_l, nxt_test_l, temp_grid)
            rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval_local)
            mh_results.append({
                "mh_beta_eval": float(beta_eval), "mh_cleanup_applied": True,
                "bpc_best": jr["bpc_best"], "top1_acc": jr["top1_acc"],
                "mrr_at_10": jr["mrr_at_10"], "best_T_for_bpc": jr["best_T_for_bpc"],
                "best_lambda_for_bpc": jr["best_lambda_for_bpc"],
                "raw_bpc_at_T1_L1": round(rbt1, 4),
                "best_dev_bpc": jr["best_dev_bpc"],
                "per_lambda_T_summary": jr["per_lambda_T_summary"],
                "n_dev": jr["n_dev"], "n_test": jr["n_test"],
                "temp_grid_used": jr["temp_grid_used"],
            })
        # Pick best by best_dev_bpc (NOT test BPC) -> double-split discipline
        chosen = min(mh_results, key=lambda r: r["best_dev_bpc"])
    t_clean = time.time() - t_clean0

    result = {
        "elapsed_s_arm": round(time.time() - t_arm0, 2),
        "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
        "wall_recall_s": ar.get("wall_recall_s", 0.0),
        "wall_cleanup_s": round(t_clean, 2),
        "n_steps": n_steps,
        "extended_grid": cfg["extended_grid"],
        "mh_cleanup_arm_config": mh_cleanup,
        "mh_beta_sweep_arm_config": mh_beta_sweep,
        "mh_results_all": mh_results,
        "chosen_mh_beta": chosen.get("mh_beta_eval"),
        # Top-level metrics (chosen-by-dev-BPC across MH_BETA sweep)
        "bpc_best": chosen["bpc_best"],
        "top1_acc": chosen["top1_acc"],
        "mrr_at_10": chosen["mrr_at_10"],
        "best_T_for_bpc": chosen["best_T_for_bpc"],
        "best_lambda_for_bpc": chosen["best_lambda_for_bpc"],
        "raw_bpc_at_T1_L1": chosen["raw_bpc_at_T1_L1"],
        "best_dev_bpc": chosen["best_dev_bpc"],
        "per_lambda_T_summary": chosen["per_lambda_T_summary"],
        "n_dev": chosen["n_dev"],
        "n_test": chosen["n_test"],
        "temp_grid_used": chosen["temp_grid_used"],
    }
    print("    [seed=%d arm=%s] bpc=%.3f top1=%.4f mrr=%.4f best_T=%.3f best_lam=%.3f chosen_mh_beta=%s elapsed=%.1fs" % (
        seed, arm, result["bpc_best"], result["top1_acc"], result["mrr_at_10"],
        result["best_T_for_bpc"], result["best_lambda_for_bpc"],
        result.get("chosen_mh_beta"), result["elapsed_s_arm"]), flush=True)
    return result


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

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    n_eval = int(mask.sum())
    if n_eval == 0:
        print("[WARN seed=%d] no valid eval pairs" % seed, flush=True)
        return {"seed": seed, "by_arm": {"ARM_UNIGRAM": uni}, "V": V,
                "N_DIM_TOTAL": N_DIM_TOTAL, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2)}

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni, "w2v_meta": w2v_meta}

    for arm_idx, arm in enumerate(ARMS):
        cfg = ARM_CONFIGS[arm]
        try:
            result = evaluate_arm(
                arm=arm, arm_idx=arm_idx, cfg=cfg, E_full=E_full,
                idx_train_t=idx_train_t, idx_held_t=idx_held_t,
                ctx_full=ctx_full, nxt_full=nxt_full, mask=mask, U_log=U_log,
                seed=seed,
            )
            by_arm[arm] = result
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            }

    del E_full
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
    for arm in ARMS:
        valid = [u for u in units
                 if not u["by_arm"].get(arm, {}).get("compute_failed", False)
                 and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))]
        if not valid:
            by_arm_agg[arm] = {"bpc_best_mean": float("inf"), "n_valid_seeds": 0,
                               "all_seeds_failed": True}
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
            "top1_acc_std": round(float(np.std(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
            "n_valid_seeds": len(valid),
            "all_seeds_failed": False,
        }
        arm_bpc[arm] = b_mean
        arm_cv[arm] = b_cv

    a1_baseline_bpc = arm_bpc.get("ARM_A1_BASELINE", float("inf"))
    primary_bpc = arm_bpc.get("ARM_FIX_ALL_5_TOGETHER", float("inf"))
    primary_cv = arm_cv.get("ARM_FIX_ALL_5_TOGETHER", float("nan"))

    # Per-arm-fix contribution (lift over A1 baseline; positive = improvement)
    fix_contributions = {}
    for arm in ["ARM_FIX_TEMP_GRID", "ARM_FIX_N_STEPS",
                "ARM_FIX_NON_CUMULATIVE_BUILD", "ARM_FIX_PER_ARM_HP_TUNED",
                "ARM_FIX_ALL_5_TOGETHER"]:
        fix_bpc = arm_bpc.get(arm, float("inf"))
        if math.isfinite(fix_bpc) and math.isfinite(a1_baseline_bpc):
            fix_contributions[arm] = round(a1_baseline_bpc - fix_bpc, 4)
        else:
            fix_contributions[arm] = None

    # Provenance rail: ARM_A1_BASELINE should reproduce A1 catastrophic ~7.89
    a1_drift = (abs(a1_baseline_bpc - SANITY_RAIL_A1_BASELINE_REF)
                if math.isfinite(a1_baseline_bpc) else float("inf"))
    a1_rail_ok = a1_drift <= SANITY_RAIL_TOLERANCE

    arm_summary = (
        "uni=%.3f | A1_BASELINE=%.4f(drift=%+.4f,rail=%s) | "
        "FIX_TEMP=%.4f(lift=%+.3f) | FIX_NSTEPS=%.4f(lift=%+.3f) | "
        "FIX_NONCUM=%.4f(lift=%+.3f) | FIX_HP=%.4f(lift=%+.3f) | "
        "FIX_ALL_5=%.4f(lift=%+.3f, cv=%.3f)"
    ) % (
        unigram_bpc,
        a1_baseline_bpc, a1_baseline_bpc - SANITY_RAIL_A1_BASELINE_REF, str(a1_rail_ok),
        arm_bpc.get("ARM_FIX_TEMP_GRID", float("inf")),
        fix_contributions.get("ARM_FIX_TEMP_GRID", float("nan")) or 0.0,
        arm_bpc.get("ARM_FIX_N_STEPS", float("inf")),
        fix_contributions.get("ARM_FIX_N_STEPS", float("nan")) or 0.0,
        arm_bpc.get("ARM_FIX_NON_CUMULATIVE_BUILD", float("inf")),
        fix_contributions.get("ARM_FIX_NON_CUMULATIVE_BUILD", float("nan")) or 0.0,
        arm_bpc.get("ARM_FIX_PER_ARM_HP_TUNED", float("inf")),
        fix_contributions.get("ARM_FIX_PER_ARM_HP_TUNED", float("nan")) or 0.0,
        primary_bpc,
        fix_contributions.get("ARM_FIX_ALL_5_TOGETHER", float("nan")) or 0.0,
        primary_cv if math.isfinite(primary_cv) else -1.0,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "fix_contributions_vs_a1_baseline": fix_contributions,
        "sanity_rails": {
            "a1_baseline_ref": SANITY_RAIL_A1_BASELINE_REF,
            "a1_baseline_drift": round(a1_drift, 4),
            "a1_baseline_rail_ok": bool(a1_rail_ok),
            "tolerance": SANITY_RAIL_TOLERANCE,
        },
        "bands": {
            "hard_pass_super_additive_ceiling": HARD_PASS_SUPER_ADDITIVE_CEILING,
            "hard_pass_test_design_ceiling": HARD_PASS_TEST_DESIGN_CEILING,
            "middle_band_bpc_upper": MIDDLE_BAND_BPC_UPPER,
            "hard_fail_structural_floor": HARD_FAIL_STRUCTURAL_FLOOR,
        },
        "primary_arm": "ARM_FIX_ALL_5_TOGETHER",
        "primary_bpc": round(primary_bpc, 4) if math.isfinite(primary_bpc) else None,
        "primary_cv": round(primary_cv, 4) if math.isfinite(primary_cv) else None,
        "a1_baseline_bpc": round(a1_baseline_bpc, 4) if math.isfinite(a1_baseline_bpc) else None,
        "n_seeds": len(units),
        "unigram_bpc": round(unigram_bpc, 4),
        "honest_scope": (
            "Tests whether A1's FULL_JOINT BPC=7.89 catastrophic failure is "
            "TEST-DESIGN ARTIFACT (drill P_deflated=0.75) by holding the 5 substrate "
            "primitives constant (cf-RPE + STDP + K=2 + modern-Hopfield + sparse-bipolar) "
            "and varying each of the 5 identified test-design biases (TEMP_GRID range, "
            "N_STEPS, MH-cumulative-build, per-arm MH_BETA HP). Primary metric = BPC on "
            "ARM_FIX_ALL_5_TOGETHER (combined fixes). WHAT_THIS_DOES_NOT_SHOW: "
            "factorial 2^4=16 decomposition not run (escape path B); K>2 not tested; "
            "GATE_TEMP not swept; MH_ITERS held at A1=3."
        ),
        "cites": [
            "notes/research_a1_composition_collapse_3rd_angle_test_design_audit_2026-06-24.md",
            "data/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1/metrics.json (A1 baseline)",
            "data/exp_substrate_cfrpe_stdp_heterogeneous_superadditive_bigram_v1_n512/metrics.json (smoking-gun)",
            "preregs/2026-06-24_substrate_compose_test_design_audit_v1.md",
        ],
    }

    # Substrate-only gate
    total_llm_calls = sum(int(u.get("llm_forward_calls_at_inference", 0)) for u in units)
    detail["llm_forward_calls_total"] = total_llm_calls
    if total_llm_calls != 0:
        return ("HARD_FAIL",
                "HARD_FAIL_LLM_CALL: llm_calls=%d (substrate-only invariant). %s" % (
                    total_llm_calls, arm_summary),
                detail)

    primary_failed = by_arm_agg.get("ARM_FIX_ALL_5_TOGETHER", {}).get("all_seeds_failed", True)
    if primary_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_FIX_ALL_5_TOGETHER all seeds failed. %s" % arm_summary,
                detail)

    # Provenance rail (full mode only; smoke uses synthetic so rail doesn't apply)
    detail["provenance_check_active"] = (RUN_MODE == "full")
    if RUN_MODE == "full":
        if not a1_rail_ok:
            return ("HARD_FAIL_PROVENANCE",
                    "HARD_FAIL_PROVENANCE_A1_BASELINE: ARM_A1_BASELINE=%.4f drifts %.4f "
                    "from A1 ref %.4f (>tol %.2f). Cell didn't reproduce A1 catastrophic; "
                    "comparison invalid. %s" % (
                        a1_baseline_bpc, a1_drift, SANITY_RAIL_A1_BASELINE_REF,
                        SANITY_RAIL_TOLERANCE, arm_summary),
                    detail)

    # Primary arm verdict bands (ARM_FIX_ALL_5_TOGETHER)
    if math.isfinite(primary_bpc) and primary_bpc <= HARD_PASS_SUPER_ADDITIVE_CEILING:
        detail["verdict_tier"] = "HARD_PASS_SUPER_ADDITIVE"
        return ("HARD_PASS",
                "HARD_PASS_SUPER_ADDITIVE: ARM_FIX_ALL_5_TOGETHER BPC=%.4f <= %.2f "
                "(substrate compose SUPER-ADDITIVE once design biases removed). "
                "A1's FULL_JOINT collapse was test-design artifact AND compose beats "
                "single primitives. Lift over A1 baseline = %+.3f. %s" % (
                    primary_bpc, HARD_PASS_SUPER_ADDITIVE_CEILING,
                    a1_baseline_bpc - primary_bpc, arm_summary),
                detail)

    if math.isfinite(primary_bpc) and primary_bpc <= HARD_PASS_TEST_DESIGN_CEILING:
        detail["verdict_tier"] = "HARD_PASS_TEST_DESIGN_ARTIFACT"
        return ("HARD_PASS",
                "HARD_PASS_TEST_DESIGN_ARTIFACT: ARM_FIX_ALL_5_TOGETHER BPC=%.4f <= %.2f "
                "(test-design fixes recover compose to fair_harness regime). 60-75%% of "
                "A1's FULL_JOINT collapse was test-design artifact. Lift over A1 = %+.3f. %s" % (
                    primary_bpc, HARD_PASS_TEST_DESIGN_CEILING,
                    a1_baseline_bpc - primary_bpc, arm_summary),
                detail)

    if math.isfinite(primary_bpc) and primary_bpc <= MIDDLE_BAND_BPC_UPPER:
        detail["verdict_tier"] = "MIDDLE_BAND_PARTIAL_RECOVERY"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_RECOVERY: ARM_FIX_ALL_5_TOGETHER BPC=%.4f in "
                "(%.2f, %.2f] (partial recovery; ~40-50%% of A1 was test-design). "
                "Both angle-2 structural + angle-3 test-design diagnoses load-bearing. "
                "Lift over A1 = %+.3f. %s" % (
                    primary_bpc, HARD_PASS_TEST_DESIGN_CEILING, MIDDLE_BAND_BPC_UPPER,
                    a1_baseline_bpc - primary_bpc, arm_summary),
                detail)

    if math.isfinite(primary_bpc) and primary_bpc >= HARD_FAIL_STRUCTURAL_FLOOR:
        detail["verdict_tier"] = "HARD_FAIL_STRUCTURAL_CONFIRMED"
        return ("HARD_FAIL",
                "HARD_FAIL_STRUCTURAL_CONFIRMED: ARM_FIX_ALL_5_TOGETHER BPC=%.4f >= %.2f "
                "(ALL 5 design fixes don't help; A1 structural Angle-2 diagnosis dominates). "
                "Substrate compose IS structurally broken; methodology cleanup doesn't save it. "
                "Lift over A1 = %+.3f. %s" % (
                    primary_bpc, HARD_FAIL_STRUCTURAL_FLOOR,
                    a1_baseline_bpc - primary_bpc, arm_summary),
                detail)

    # primary_bpc in (MIDDLE_BAND_UPPER, HARD_FAIL_FLOOR) -> MIDDLE_BAND_INTER
    detail["verdict_tier"] = "MIDDLE_BAND_INTER_GAP"
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_INTER_GAP: ARM_FIX_ALL_5_TOGETHER BPC=%.4f between MB ceiling "
            "%.2f and HARD_FAIL floor %.2f. Marginal recovery; structural mostly dominant. "
            "Lift over A1 = %+.3f. %s" % (
                primary_bpc, MIDDLE_BAND_BPC_UPPER, HARD_FAIL_STRUCTURAL_FLOOR,
                a1_baseline_bpc - primary_bpc, arm_summary),
            detail)


# ============================================================================
# Main loop
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

summary_str = (
    "%s | arms=%d seeds=%d N_DIM=%d N_TRAIN=%d primary=ARM_FIX_ALL_5_TOGETHER" % (
        verdict, len(ARMS), len(SEEDS), N_DIM_TOTAL, N_TRAIN)
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
    "K_BANKS": K_BANKS,
    "GATE_TEMP": GATE_TEMP,
    "CFRPE_LR": CFRPE_LR,
    "STDP_WEIGHT": STDP_WEIGHT,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "MH_BETA_A1": MH_BETA_A1,
    "MH_ITERS": MH_ITERS,
    "MH_BETA_SWEEP": MH_BETA_SWEEP,
    "N_STEPS_A1": N_STEPS_A1,
    "N_STEPS_BOOSTED": N_STEPS_BOOSTED,
    "TEMP_GRID_A1": TEMP_GRID_A1,
    "TEMP_GRID_EXTENDED": TEMP_GRID_EXTENDED,
    "LAMBDA_GRID": LAMBDA_GRID,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
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
