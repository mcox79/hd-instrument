"""
substrate_cross_layer_compose_LM_v2_RESCUE_FULL -- WAVE C production-scale
confirmation of v2_RESCUE smoke HARD_PASS_CHAIN_GRADE_BONUS.

Wave-C task (USER 2026-06-24): smoke HARD_PASS at N_DIM=512 N_TRAIN=2000 V=300
synthetic-w2v showed 2-layer INDEPENDENT BPC=5.03 vs 2-layer SHARED-W=5.30 ->
separated-W BEATS shared-W by 0.27 bits (the architectural prediction).
Sanity rail FAILED at smoke (baseline 4.89 vs production rail 7.04 -- expected
since smoke synthetic-encoder operates in a different BPC regime). Full-N text8
production needed to claim CHAIN-GRADE at the proper scale.

PRODUCTION CONFIG (NOT scope-reduced; matches v1 spec at last-completed N):
  N_DIM = 8192       (was 4096 in rescue)
  N_TRAIN = 100_000  (was 50k in rescue)
  N_HELD = 20_000    (was 10k in rescue)
  VOCAB_CAP = 4000
  SEEDS = [7, 17, 23] (3 seeds for CV; was 2)
  encoder = word2vec sparse-bipolar f=0.05 (matches fair-harness rail)
  Routing: overnight_queue (GPU) -- 7200s timeout per Wave-C spec.

FIVE ARMS (3 seeds each; ONE knob = n_layers x shared_W):
  ARM_UNIGRAM
  ARM_SINGLE_LAYER_CFRPE          -- sanity rail (must reproduce fair-harness rail 7.30 +/-0.10)
  ARM_2_LAYER_INDEPENDENT_CFRPE   -- LOAD-BEARING architectural prediction
  ARM_3_LAYER_INDEPENDENT_CFRPE   -- depth scan
  ARM_2_LAYER_SHARED_W_CFRPE      -- universal-biology-violation CONTROL

HARD bands (production-scale; tightened from rescue):
  HARD_PASS_CHAIN_GRADE: best_indep BPC <= 6.95 AND beats SHARED_W by >= 0.15
                          BPC AND CV <= 0.03 across seeds
  HARD_PASS:             best_indep BPC <= 7.20 AND beats SHARED_W by >= 0.10
  HARD_FAIL:             best_indep BPC >= 7.40 OR within 0.05 of SHARED_W
  READOUT_DEGENERATE:    raw_bpc_at_T1_L1 within +/-0.5 of log2(V)

Sanity rail: ARM_SINGLE_LAYER_CFRPE within +/-0.10 BPC of
exp_fair_harness_substrate_as_lm_v1 BPC=7.3065.

ENCODING: word2vec-google-news-300 projected to N_DIM=8192 sparse-bipolar
(f=0.05). OOV fallback char-trigram bipolar. Joint (T, lambda) sweep on dev;
test eval. LAMBDA_GRID excludes 0.0 per META C7.

D1 ROOFLINE probe re-runs at production scale (probe points still 512/1024/2048
but extrapolation target updated to FULL config: N_DIM=8192, N_TRAIN=100k,
N_STEPS=1000, 3 seeds, 4 plasticity arms). D2 atexit + per-seed checkpoint.

ASCII-only. Per-seed checkpoint + atexit partial-flush. Fix #14 + Fix #28 + Fix #24.
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
import json
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

ANCHOR_NAME = "substrate_cross_layer_compose_LM_v2_RESCUE_FULL"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Pre-reg thresholds (LM BPC; PRODUCTION-SCALE Wave-C bands)
CHAIN_GRADE_BONUS_BPC = 6.95     # HARD_PASS_CHAIN_GRADE floor (was 6.70 rescue)
HARD_PASS_BPC = 7.20             # HARD_PASS floor (was 6.90 rescue)
MIDDLE_BAND_BPC_UPPER = 7.40     # HARD_FAIL above this (was 7.05 rescue)
HP_BPC_CV_MAX = 0.03             # tightened: 0.03 across 3 seeds (was 0.05)
DEGEN_TOL = 0.5

# Additional Wave-C bands: shared-W discriminator gap
SHARED_W_GAP_CHAIN_GRADE = 0.15  # best_indep must beat shared_W by >= 0.15 BPC for chain-grade
SHARED_W_GAP_HARD_PASS = 0.10    # >= 0.10 BPC for HARD_PASS
SHARED_W_GAP_FAIL_MARGIN = 0.05  # if best_indep within 0.05 of shared_W -> HARD_FAIL

# Sanity rail: fair-harness reference (full production N_DIM=8192; tight tol)
SANITY_SINGLE_LAYER_REF_BPC = 7.3065  # fair-harness substrate-as-LM v1
SANITY_SINGLE_LAYER_TOL = 0.10        # production tol (vs 0.40 in rescue)

# Plasticity knobs (matches fair_harness cf-RPE cell)
CFRPE_LR = 0.5
INGEST_BATCH = 64

# Inference grids
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]  # EXCLUDES 0.0 per META C7
MRR_K = 10

# Sparse-bipolar f (chain-grade validated)
SPARSE_BIPOLAR_F = 0.05

# Reference values
UNIGRAM_BPC_REF = 7.738
BASELINE_HEBBIAN_BPC = 7.3065

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--roofline-probe", action="store_true", dest="roofline_probe",
                help="D1: run 3-point timing probe (N=512/1024/2048) and refuse "
                     "if extrapolated FULL wall > 0.8 * --timeout-s.")
_P.add_argument("--timeout-s", type=int, default=7200,
                help="Used by --roofline-probe to refuse over-budget extrapolation; "
                     "Wave-C FULL default = 7200s (GPU overnight_queue).")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = (
    "smoke"
    if (_ARGS.smoke or _ARGS.self_test or _ARGS.roofline_probe or _NAME_SAYS_SMOKE)
    else os.environ.get("HDLAB_RUN_MODE", "full")
)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Production config (Wave C FULL; NOT scope-reduced)
N_DIM = 8192
PRETRAIN_DIM = 300
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

# Arm definitions (UNCHANGED from v1)
ARMS = [
    "ARM_UNIGRAM",                   # baseline
    "ARM_SINGLE_LAYER_CFRPE",        # sanity rail
    "ARM_2_LAYER_INDEPENDENT_CFRPE", # load-bearing
    "ARM_3_LAYER_INDEPENDENT_CFRPE", # depth scan
    "ARM_2_LAYER_SHARED_W_CFRPE",    # control (same-W)
]
PLASTICITY_ARMS = [a for a in ARMS if a != "ARM_UNIGRAM"]

ARM_CONFIG = {
    "ARM_SINGLE_LAYER_CFRPE":        {"n_layers": 1, "shared_W": False},
    "ARM_2_LAYER_INDEPENDENT_CFRPE": {"n_layers": 2, "shared_W": False},
    "ARM_3_LAYER_INDEPENDENT_CFRPE": {"n_layers": 3, "shared_W": False},
    "ARM_2_LAYER_SHARED_W_CFRPE":    {"n_layers": 2, "shared_W": True},
}

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]          # 3 seeds for CV<=0.03 discriminator
    N_TRAIN = 100_000            # Wave-C FULL
    N_HELD = 20_000              # scaled
    N_STEPS = 1000               # Wave-C spec (compute-bounded; vs 2000 rescue)
else:
    # Smoke: small + char-trigram fallback; should run in 30-90s on CPU
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    N_STEPS = 80

# Gensim cache (process-local)
_GENSIM_KV_CACHE: Dict[str, object] = {}


# ============================================================================
# D2: atexit partial-flush handler
# ============================================================================
# Holds the live mutable state mid-run; atexit handler serializes whatever
# arrived by the time the process dies (timeout/crash/SIGTERM).
_LIVE_STATE: Dict = {
    "anchor_name": ANCHOR_NAME,
    "run_mode": RUN_MODE,
    "phase": "init",
    "seeds_done": [],
    "per_seed_so_far": {},   # {seed: {arm: arm_dict}}
    "current_seed": None,
    "current_arm": None,
    "start_ts": time.time(),
}


def _atexit_flush_partial():
    """Flush whatever per-seed/per-arm dict exists to data/exp_<name>/partial_atexit.json.

    This runs even on TIMEOUT / crash / SIGTERM. The complementary
    per-seed checkpoint (write_partial inside the seed loop) already covers
    'whole-seed done' atomically; this atexit covers the 'partial-seed
    in-progress' case where a seed crashed mid-arm-loop.
    """
    try:
        out_dir_local = REPO / "data" / f"exp_{_HDLAB_EXP_NAME or ANCHOR_NAME}"
        out_dir_local.mkdir(parents=True, exist_ok=True)
        _LIVE_STATE["flushed_at_ts"] = time.time()
        _LIVE_STATE["elapsed_s"] = round(time.time() - _LIVE_STATE["start_ts"], 2)
        path = out_dir_local / "partial_atexit.json"
        # Atomic write
        tmp = path.with_suffix(".json.tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(_LIVE_STATE, f, indent=2, default=str)
        os.replace(tmp, path)
        # Stderr so it's visible even when stdout is buffered/redirected
        print(f"[atexit] partial state flushed to {path} "
              f"(phase={_LIVE_STATE.get('phase')}, seeds_done={_LIVE_STATE.get('seeds_done')}, "
              f"current_seed={_LIVE_STATE.get('current_seed')}, "
              f"current_arm={_LIVE_STATE.get('current_arm')})",
              file=sys.stderr, flush=True)
    except Exception as e:
        # NEVER raise from atexit
        try:
            print(f"[atexit] flush FAILED: {type(e).__name__}: {e}",
                  file=sys.stderr, flush=True)
        except Exception:
            pass


atexit.register(_atexit_flush_partial)


# ============================================================================
# Encoder utilities (lifted-verbatim from v1)
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


def build_E_word2vec_gpu(vocab: List[str], n_dim: int, seed: int
                          ) -> Tuple[torch.Tensor, Dict]:
    """Build [V, n_dim] L2-normalized word2vec-projected vectors on device."""
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
# Multi-layer cf-RPE (verbatim from v1; tested by selftest below)
# ============================================================================

def build_W_stack(arm: str, E: torch.Tensor, idx_train_t: torch.Tensor,
                   n_steps: int, batch: int, lr: float,
                   gen: torch.Generator) -> List[torch.Tensor]:
    cfg = ARM_CONFIG[arm]
    n_layers = cfg["n_layers"]
    shared = cfg["shared_W"]
    dim = E.shape[1]
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return [torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
                for _ in range(n_layers)]

    if shared:
        W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
        for _ in range(n_steps):
            st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
            ctx = E[idx_train_t[st]]
            nxt = E[idx_train_t[st + 1]]
            error = nxt - ctx @ W.t()
            dW = (error.t() @ ctx) / batch
            W = W + lr * dW
        return [W] * n_layers

    Ws: List[torch.Tensor] = []
    W1 = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        ctx = E[idx_train_t[st]]
        nxt = E[idx_train_t[st + 1]]
        error = nxt - ctx @ W1.t()
        dW = (error.t() @ ctx) / batch
        W1 = W1 + lr * dW
    Ws.append(W1)

    for layer_idx in range(2, n_layers + 1):
        W_k = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
        for _ in range(n_steps):
            st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
            ctx = E[idx_train_t[st]]
            h = ctx
            for W_lower in Ws:
                h = _l2_normalize_t(h @ W_lower.t())
            nxt = E[idx_train_t[st + 1]]
            error = nxt - h @ W_k.t()
            dW = (error.t() @ h) / batch
            W_k = W_k + lr * dW
        Ws.append(W_k)

    return Ws


def forward_stack(ctx: torch.Tensor, Ws: List[torch.Tensor]) -> torch.Tensor:
    h = ctx
    for W in Ws:
        h = _l2_normalize_t(h @ W.t())
    return h


# ============================================================================
# Per-arm logits builder (verbatim from v1)
# ============================================================================

def compute_arm_logits(arm: str, E_base: torch.Tensor, idx_train: np.ndarray,
                        idx_held: np.ndarray, seed: int, n_steps: int) -> Dict:
    V = E_base.shape[0]
    dim = E_base.shape[1]
    E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed * 10007 + ARMS.index(arm) * 31337)

    t0 = time.time()
    Ws = build_W_stack(arm, E_used, idx_train_t, n_steps=n_steps,
                       batch=INGEST_BATCH, lr=CFRPE_LR, gen=gen)
    t_ingest = time.time() - t0

    t0 = time.time()
    n_h = idx_held_t.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        ctx = E_used[idx_held_t[b:end]]
        pred = forward_stack(ctx, Ws)
        logits[b:end] = pred @ E_used.T
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    raw_bpc_at_T1 = _raw_bpc_at_T1(logits, idx_held)

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    n_layers_used = ARM_CONFIG[arm]["n_layers"]
    shared_W_flag = ARM_CONFIG[arm]["shared_W"]
    del logits
    for W in Ws:
        del W
    del Ws
    del E_used
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "raw_bpc_at_T1_L1": round(raw_bpc_at_T1, 4),
        "n_layers": n_layers_used,
        "shared_W": shared_W_flag,
    }


def _raw_bpc_at_T1(logits: torch.Tensor, idx_held: np.ndarray) -> float:
    V = logits.shape[1]
    n_h = logits.shape[0]
    nxt_np = idx_held[1:] if len(idx_held) > 1 else idx_held
    n_eval = min(n_h, len(nxt_np))
    if n_eval == 0:
        return float("inf")
    logits_np = logits[:n_eval].detach().cpu().numpy().astype(np.float32)
    nxt_eval = nxt_np[:n_eval]
    z = logits_np - logits_np.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / np.clip(e.sum(axis=1, keepdims=True), 1e-30, None)
    p_nxt = p[np.arange(n_eval), nxt_eval].clip(1e-12, 1.0)
    return float(-np.mean(np.log(p_nxt)) / math.log(2.0))


# ============================================================================
# text8 corpus utilities (verbatim from v1)
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
# Joint (T, lambda) sweep + 3 metrics (verbatim from v1)
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


def joint_sweep(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                temp_grid: list, lambda_grid: list, mrr_k: int) -> Dict:
    probs_T1 = softmax_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)

    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}

    for T in temp_grid:
        probs_dev = softmax_with_T(sub_logits_dev, T)
        logp_sub_dev = np.log(np.clip(probs_dev, 1e-30, 1.0))
        for lam in lambda_grid:
            logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
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
        "n_dev": int(len(nxt_dev)),
        "n_test": int(len(nxt_test)),
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray,
                     V: int, mrr_k: int) -> Dict:
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
    rr = np.where(ranks <= mrr_k, 1.0 / ranks, 0.0)
    mrr = float(np.mean(rr))
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(top1, 4),
            "mrr_unigram": round(mrr, 4), "n_test": int(len(nxt_test))}


# ============================================================================
# D1: roofline probe
# ============================================================================

def _roofline_probe(timeout_s: int) -> Dict:
    """3-point timing probe at N=512/1024/2048, single arm, single seed.

    Times the single ingest+recall pass for ARM_2_LAYER_INDEPENDENT_CFRPE
    (the load-bearing arm; 2 layers, so representative of the multi-layer
    cost). Fits t = a*N^k via log-log regression. Extrapolates to FULL
    config (N_DIM=4096, N_TRAIN=50k, N_STEPS=2000, 2 seeds, 4 plasticity arms).

    Returns dict; refuses dispatch (sys.exit(1)) if extrapolated FULL wall
    > 0.8 * timeout_s.
    """
    print(f"[D1-probe] running 3-point roofline probe (target timeout={timeout_s}s)",
          flush=True)
    full_n_dim = N_DIM           # Wave-C FULL = 8192
    full_n_train = N_TRAIN       # 100k
    full_n_steps = N_STEPS       # 1000
    full_n_seeds = len(SEEDS)    # 3
    n_plasticity_arms = len(PLASTICITY_ARMS)  # 4

    # Tiny vocab for probe (just enough to exercise the matmul)
    V_probe = 64
    N_HELD_probe = 100
    probe_seed = 999
    probe_arm = "ARM_2_LAYER_INDEPENDENT_CFRPE"

    probe_points: List[Tuple[int, float]] = []
    for N_test in (512, 1024, 2048):
        # Build synthetic E
        torch.manual_seed(probe_seed)
        E_probe = _l2_normalize_t(torch.randn(V_probe, N_test, device=DEVICE,
                                              dtype=TORCH_DTYPE))
        # Synthetic train indices (size matching tokens for ~50 steps probe)
        N_TRAIN_probe = 1000
        idx_train_probe = np.random.default_rng(probe_seed).integers(
            0, V_probe, size=N_TRAIN_probe, dtype=np.int64)
        idx_held_probe = np.random.default_rng(probe_seed + 1).integers(
            0, V_probe, size=N_HELD_probe, dtype=np.int64)
        # Run the full path (build + recall) with a small n_steps (50) for timing
        t0 = time.time()
        try:
            _ = compute_arm_logits(probe_arm, E_probe, idx_train_probe,
                                    idx_held_probe, probe_seed, n_steps=50)
        except Exception as e:
            print(f"[D1-probe] N={N_test} FAILED: {type(e).__name__}: {e}",
                  flush=True)
            return {"probe_failed": True, "error": str(e)[:200]}
        t_one = time.time() - t0
        # Time at 50 steps; will scale linearly with n_steps
        probe_points.append((N_test, t_one))
        print(f"[D1-probe] N={N_test} time_50steps_2layer_64V={t_one:.3f}s",
              flush=True)

    # Power-law fit: log(t) = log(a) + k * log(N)
    ns = np.array([p[0] for p in probe_points], dtype=np.float64)
    ts = np.array([p[1] for p in probe_points], dtype=np.float64)
    lns = np.log(ns)
    lts = np.log(ts)
    # least-squares on slope
    A = np.vstack([lns, np.ones_like(lns)]).T
    k, log_a = np.linalg.lstsq(A, lts, rcond=None)[0]
    a = float(np.exp(log_a))
    print(f"[D1-probe] fit: t(N) = {a:.4e} * N^{k:.3f}", flush=True)

    # Extrapolate to FULL config:
    #   per-arm-per-seed wall_at_N=full_n_dim with n_steps=full_n_steps and V=full_vocab
    #   The probe used V=64, n_steps=50, N_TRAIN=1000.
    #   Cost per step ~ batch * N^2 (matmul); doesn't depend on V (V only matters
    #   for the final logits matmul which is small relative to W training).
    #   Cost per arm ~ (n_steps * batch * N^2) for build + (N_HELD * N^2) for recall.
    #   We scale time by:
    #     - n_steps: (full_n_steps / 50)
    #     - N_DIM:   captured in the fit k
    #     - n_seeds * n_arms: linear multiplication
    #   The probe time at N=4096 (full N_DIM) per single arm per single seed:
    one_unit_at_full_N = a * (full_n_dim ** k)  # at probe n_steps=50
    n_steps_scale = full_n_steps / 50.0
    one_arm_one_seed_full_steps = one_unit_at_full_N * n_steps_scale
    # n_layers scaling: 2-layer arm is the probe; SINGLE is ~50%, 3-layer is ~150%
    # of 2-layer cost; SHARED is ~50% (single-W ingest). Total arm-cost-multiplier
    # vs probe (which is 2-layer):
    #   ARM_SINGLE_LAYER       (1 layer)  -> 0.5x
    #   ARM_2_LAYER_INDEPENDENT (2 layer) -> 1.0x (probe)
    #   ARM_3_LAYER_INDEPENDENT (3 layer) -> 1.5x  (3rd layer trains atop frozen 1+2)
    #   ARM_2_LAYER_SHARED     (1 W)      -> 0.5x
    # Sum-of-arms multiplier = 0.5 + 1.0 + 1.5 + 0.5 = 3.5
    sum_arms_multiplier = 3.5
    all_arms_one_seed = one_arm_one_seed_full_steps * sum_arms_multiplier
    full_wall_estimate = all_arms_one_seed * full_n_seeds
    # Encoder build + recall overhead (per-seed): roughly 30-60s for word2vec
    # load; recall scales with N_HELD * V * N_DIM (~ 10k * 4000 * 4096 * 4 = 650 MB
    # multiply per arm). At BLAS speeds CPU ~ 100-200 GFLOPS this is ~5-15s/arm.
    encoder_overhead = 60.0
    recall_overhead_per_arm = 12.0
    overhead = full_n_seeds * (encoder_overhead +
                                recall_overhead_per_arm * n_plasticity_arms)
    total_estimate = full_wall_estimate + overhead

    pct_of_budget = total_estimate / max(timeout_s, 1)
    print(f"[D1-probe] EXTRAPOLATION: build_walls={full_wall_estimate:.0f}s "
          f"+ overhead={overhead:.0f}s = total={total_estimate:.0f}s "
          f"({pct_of_budget * 100:.0f}% of {timeout_s}s budget)", flush=True)

    result = {
        "probe_points": [(int(N), round(t, 3)) for N, t in probe_points],
        "fit_power_law_k": round(float(k), 3),
        "fit_power_law_a": float(a),
        "extrapolated_build_walls_s": round(full_wall_estimate, 1),
        "extrapolated_overhead_s": round(overhead, 1),
        "extrapolated_total_wall_s": round(total_estimate, 1),
        "timeout_budget_s": timeout_s,
        "fraction_of_budget": round(pct_of_budget, 3),
        "refuse_threshold_fraction": 0.8,
        "full_config": {
            "N_DIM": full_n_dim, "N_TRAIN": full_n_train,
            "N_STEPS": full_n_steps, "N_SEEDS": full_n_seeds,
            "N_PLASTICITY_ARMS": n_plasticity_arms,
        },
    }
    if pct_of_budget > 0.8:
        print(f"[D1-probe] REFUSE: extrapolated {total_estimate:.0f}s exceeds "
              f"0.8 * {timeout_s} = {0.8 * timeout_s:.0f}s budget. "
              f"Either reduce scope further or raise timeout to "
              f">= {total_estimate / 0.8:.0f}s.", file=sys.stderr, flush=True)
        result["accept"] = False
        # Write report to data dir for visibility
        try:
            out_dir_local = REPO / "data" / f"exp_{_HDLAB_EXP_NAME or ANCHOR_NAME}"
            out_dir_local.mkdir(parents=True, exist_ok=True)
            with (out_dir_local / "roofline_probe.json").open("w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        except Exception:
            pass
        sys.exit(1)
    else:
        print(f"[D1-probe] ACCEPT: extrapolated {total_estimate:.0f}s within "
              f"0.8 * {timeout_s} = {0.8 * timeout_s:.0f}s budget", flush=True)
        result["accept"] = True
        try:
            out_dir_local = REPO / "data" / f"exp_{_HDLAB_EXP_NAME or ANCHOR_NAME}"
            out_dir_local.mkdir(parents=True, exist_ok=True)
            with (out_dir_local / "roofline_probe.json").open("w", encoding="utf-8") as f:
                json.dump(result, f, indent=2)
        except Exception:
            pass
    return result


# ============================================================================
# Instrumentation self-test (MANDATORY; v1's ST1-ST10 verbatim)
# ============================================================================

def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)
    _dev = DEVICE

    # ST1
    n_dim_st = 64
    Ctx2 = torch.randn(1, n_dim_st, device=_dev)
    Nxt2 = torch.randn(1, n_dim_st, device=_dev)
    Ctx2 = Ctx2 / (Ctx2.norm() + 1e-8)
    Nxt2 = Nxt2 / (Nxt2.norm() + 1e-8)
    W_t = torch.zeros(n_dim_st, n_dim_st, device=_dev)
    err_before = float((Nxt2 - Ctx2 @ W_t.t()).norm())
    dW = (Nxt2 - Ctx2 @ W_t.t()).t() @ Ctx2
    W_t = W_t + 0.9 * dW
    err_after = float((Nxt2 - Ctx2 @ W_t.t()).norm())
    assert err_after < err_before, (
        "ST1 cf-RPE should shrink error: %.4f -> %.4f" % (err_before, err_after))
    print("[selftest] ST1 cf-RPE delta shrinks error: %.4f -> %.4f" % (
        err_before, err_after), flush=True)

    # ST2
    h_in = torch.randn(3, n_dim_st, device=_dev)
    h_in = _l2_normalize_t(h_in)
    h_out = forward_stack(h_in, [])
    diff = float((h_in - h_out).norm())
    assert diff < 1e-5, "ST2 empty-stack forward should be identity: diff=%.4e" % diff
    print("[selftest] ST2 empty-stack forward is identity (diff=%.2e)" % diff, flush=True)

    # ST3
    n_v_st = 8
    E_st = _l2_normalize_t(torch.randn(n_v_st, n_dim_st, device=_dev))
    idx_train_st = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 0, 1, 2, 3],
                                dtype=torch.long, device=_dev)
    gen_st = torch.Generator(device=_dev); gen_st.manual_seed(42)
    Ws_shared = build_W_stack("ARM_2_LAYER_SHARED_W_CFRPE", E_st, idx_train_st,
                                n_steps=5, batch=4, lr=0.5, gen=gen_st)
    assert len(Ws_shared) == 2, "ST3 shared stack should have 2 layers"
    same_ref = Ws_shared[0] is Ws_shared[1]
    assert same_ref, "ST3 shared-W layers should be SAME tensor reference"
    print("[selftest] ST3 shared-W stack: 2 layers, SAME reference (same_ref=%s)" % same_ref,
          flush=True)

    # ST4
    gen_st2 = torch.Generator(device=_dev); gen_st2.manual_seed(42)
    Ws_indep = build_W_stack("ARM_2_LAYER_INDEPENDENT_CFRPE", E_st, idx_train_st,
                              n_steps=5, batch=4, lr=0.5, gen=gen_st2)
    distinct = not (Ws_indep[0] is Ws_indep[1])
    diff_norm = float((Ws_indep[0] - Ws_indep[1]).norm())
    assert distinct and diff_norm > 1e-6, "ST4 independent-W layers must differ"
    print("[selftest] ST4 independent-W stack: 2 distinct tensors (diff_norm=%.4f)" % diff_norm,
          flush=True)

    # ST5
    gen_st3 = torch.Generator(device=_dev); gen_st3.manual_seed(42)
    Ws3 = build_W_stack("ARM_3_LAYER_INDEPENDENT_CFRPE", E_st, idx_train_st,
                         n_steps=5, batch=4, lr=0.5, gen=gen_st3)
    assert len(Ws3) == 3, "ST5 3-layer stack should have 3 layers"
    print("[selftest] ST5 3-layer independent stack OK (3 layers built)", flush=True)

    # ST6
    gen_st4 = torch.Generator(device=_dev); gen_st4.manual_seed(42)
    Ws1 = build_W_stack("ARM_SINGLE_LAYER_CFRPE", E_st, idx_train_st,
                         n_steps=5, batch=4, lr=0.5, gen=gen_st4)
    assert len(Ws1) == 1, "ST6 single-layer should have 1 W"
    print("[selftest] ST6 single-layer stack OK", flush=True)

    # ST7
    h_after = forward_stack(h_in, Ws_indep)
    diff_fwd = float((h_in - h_after).norm())
    assert diff_fwd > 1e-3, "ST7 2-layer forward should change input"
    print("[selftest] ST7 2-layer forward changes input (diff=%.4f)" % diff_fwd, flush=True)

    # ST8
    n_eval_st = 20
    logits_zero = torch.zeros(n_eval_st, n_v_st, device=_dev)
    raw_bpc = _raw_bpc_at_T1(logits_zero, np.zeros(n_eval_st + 1, dtype=np.int64))
    expected_bpc = math.log2(n_v_st)
    assert abs(raw_bpc - expected_bpc) < 0.1, (
        "ST8 zero-W raw_bpc=%.4f should be near log2(%d)=%.4f" % (
            raw_bpc, n_v_st, expected_bpc))
    print("[selftest] ST8 zero-W raw_bpc=%.4f near log2(%d)=%.4f" % (
        raw_bpc, n_v_st, expected_bpc), flush=True)

    # ST9
    n_tok_st = 30
    n_v_sm = 6
    rng_st = np.random.default_rng(99)
    logits_st = rng_st.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_st = rng_st.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_st = np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32)
    U_log_st = np.log(U_st)
    nd = n_tok_st // 2
    jr = joint_sweep(logits_st[:nd], logits_st[nd:], U_log_st, nxt_st[:nd], nxt_st[nd:],
                      TEMP_GRID, LAMBDA_GRID, MRR_K)
    assert math.isfinite(jr["bpc_best"]), "ST9 joint_sweep bpc_best not finite"
    print("[selftest] ST9 joint_sweep all metrics finite (bpc=%.3f top1=%.4f mrr=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"]), flush=True)

    # ST10
    assert 0.0 not in LAMBDA_GRID, "ST10 LAMBDA_GRID must not include 0.0 (META C7)"
    print("[selftest] ST10 LAMBDA_GRID excludes 0.0 (META C7) OK", flush=True)

    # ST11 (D2): atexit handler registered + flush callable
    assert callable(_atexit_flush_partial), "ST11 atexit handler must be callable"
    print("[selftest] ST11 atexit partial-flush handler registered (D2 discipline)",
          flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)

# Run D1 roofline probe if requested
if _ARGS.roofline_probe:
    _roofline_probe(timeout_s=_ARGS.timeout_s)
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    _LIVE_STATE["current_seed"] = seed
    _LIVE_STATE["current_arm"] = None
    _LIVE_STATE["per_seed_so_far"].setdefault(seed, {})
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
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"], uni["n_test"]),
          flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}
    _LIVE_STATE["per_seed_so_far"][seed]["ARM_UNIGRAM"] = uni

    print("\n[seed=%d] building encoder (V=%d, N_DIM=%d) on %s..." % (
        seed, V, N_DIM, str(DEVICE)), flush=True)
    t_enc0 = time.time()
    encoder_meta: Dict = {}
    try:
        E_base, encoder_meta = build_E_word2vec_gpu(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d encoder] WORD2VEC LOAD FAIL: %s -- falling back to char-trigram" % (
            seed, err), flush=True)
        E_base = build_E_char_trigram_gpu(vocab, N_DIM, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    t_enc = time.time() - t_enc0
    print("[seed=%d encoder] built in %.1fs (meta=%s)" % (seed, t_enc, encoder_meta),
          flush=True)

    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    ctx_eval = ctx_full[mask]
    nxt_eval = nxt_full[mask]
    n_eval = len(ctx_eval)
    if n_eval == 0:
        for arm in PLASTICITY_ARMS:
            by_arm[arm] = {"empty_eval": True}
        del E_base
        return {"seed": seed, "by_arm": by_arm, "V": V, "N_DIM": N_DIM,
                "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2),
                "device": str(DEVICE), "encoder_meta": encoder_meta}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    for arm in PLASTICITY_ARMS:
        _LIVE_STATE["current_arm"] = arm
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s n_layers=%d shared=%s] building W stack + logits..." % (
            seed, arm, ARM_CONFIG[arm]["n_layers"], ARM_CONFIG[arm]["shared_W"]),
              flush=True)
        try:
            ar = compute_arm_logits(arm, E_base, idx_train, idx_held, seed, N_STEPS)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            arm_dict_fail = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
                "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
                "n_layers": ARM_CONFIG[arm]["n_layers"],
                "shared_W": ARM_CONFIG[arm]["shared_W"],
            }
            by_arm[arm] = arm_dict_fail
            _LIVE_STATE["per_seed_so_far"][seed][arm] = arm_dict_fail
            continue

        logits_full = ar["logits"]
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
            logits_eval = logits_ctx[mask]
            jr = joint_sweep(
                logits_eval[:n_dev], logits_eval[n_dev:], U_log,
                nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
            )
        else:
            valid_pos = np.where(mask)[0]
            mask_pos = np.array([p for p in valid_pos if p < logits_full.shape[0]],
                                 dtype=np.int64)
            logits_eval = logits_full[mask_pos]
            nxt_eval_local = nxt_full[mask_pos]
            ne = len(nxt_eval_local)
            ndev = ne // 2
            jr = joint_sweep(
                logits_eval[:ndev], logits_eval[ndev:], U_log,
                nxt_eval_local[:ndev], nxt_eval_local[ndev:],
                TEMP_GRID, LAMBDA_GRID, MRR_K,
            )

        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
        jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
        jr["n_layers"] = ar["n_layers"]
        jr["shared_W"] = ar["shared_W"]
        by_arm[arm] = jr
        # D2: live-update so atexit captures it even mid-seed
        _LIVE_STATE["per_seed_so_far"][seed][arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
              "(T=%.4f L=%.2f) raw=%.3f" % (
                  seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                  jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                  jr["raw_bpc_at_T1_L1"]), flush=True)

    del E_base
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    _LIVE_STATE["current_arm"] = None
    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "N_STEPS": N_STEPS,
        "run_mode": RUN_MODE,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
    }


# ============================================================================
# Verdict (verbatim from v1)
# ============================================================================

def _arm_agg(arm: str, units: List[Dict]) -> Dict:
    failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
    valid = [(not f) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
             for f, u in zip(failed, units)]
    valid_u = [u for ok, u in zip(valid, units) if ok]
    if not valid_u:
        return {"bpc_best_mean": float("inf"), "top1_acc_mean": float("nan"),
                "mrr_at_10_mean": float("nan"), "raw_bpc_at_T1_L1_mean": float("nan"),
                "n_valid_seeds": 0, "n_compute_failed": int(sum(failed)),
                "all_seeds_failed": True}
    bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid_u]
    top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid_u]
    mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid_u]
    raw_v = [u["by_arm"][arm]["raw_bpc_at_T1_L1"] for u in valid_u]
    b_mean = float(np.mean(bpc_v))
    b_std = float(np.std(bpc_v))
    return {
        "bpc_best_mean": round(b_mean, 4),
        "bpc_best_std": round(b_std, 4),
        "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
        "top1_acc_mean": round(float(np.mean(top1_v)), 4),
        "top1_acc_std": round(float(np.std(top1_v)), 4),
        "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
        "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
        "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_v)), 4),
        "n_valid_seeds": int(len(valid_u)),
        "n_compute_failed": int(sum(failed)),
        "all_seeds_failed": False,
    }


def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}
    vocab_entropy = math.log2(max(units[0].get("V", VOCAB_CAP), 2))

    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan"))
               for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
        "bpc_std": round(float(np.std(uni_bpc)), 4),
    }
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    for arm in PLASTICITY_ARMS:
        by_arm_agg[arm] = _arm_agg(arm, units)

    single = by_arm_agg.get("ARM_SINGLE_LAYER_CFRPE", {})
    indep2 = by_arm_agg.get("ARM_2_LAYER_INDEPENDENT_CFRPE", {})
    indep3 = by_arm_agg.get("ARM_3_LAYER_INDEPENDENT_CFRPE", {})
    shared = by_arm_agg.get("ARM_2_LAYER_SHARED_W_CFRPE", {})

    single_bpc = single.get("bpc_best_mean", float("inf"))
    indep2_bpc = indep2.get("bpc_best_mean", float("inf"))
    indep3_bpc = indep3.get("bpc_best_mean", float("inf"))
    shared_bpc = shared.get("bpc_best_mean", float("inf"))

    indep_candidates = [
        ("ARM_2_LAYER_INDEPENDENT_CFRPE", indep2_bpc, indep2.get("bpc_best_cv", float("nan")),
         indep2.get("raw_bpc_at_T1_L1_mean", float("nan"))),
        ("ARM_3_LAYER_INDEPENDENT_CFRPE", indep3_bpc, indep3.get("bpc_best_cv", float("nan")),
         indep3.get("raw_bpc_at_T1_L1_mean", float("nan"))),
    ]
    indep_candidates = [c for c in indep_candidates if math.isfinite(c[1])]
    if indep_candidates:
        best_indep_name, best_indep_bpc, best_indep_cv, best_indep_raw = min(
            indep_candidates, key=lambda c: c[1])
    else:
        best_indep_name, best_indep_bpc, best_indep_cv, best_indep_raw = (
            "NONE", float("inf"), float("nan"), float("nan"))

    sanity_single_ok = (math.isfinite(single_bpc) and
                        abs(single_bpc - SANITY_SINGLE_LAYER_REF_BPC) <= SANITY_SINGLE_LAYER_TOL)
    sanity_shared_ok = (not math.isfinite(shared_bpc) or
                        not math.isfinite(single_bpc) or
                        (single_bpc - shared_bpc) < 0.05)

    degen_flag = (math.isfinite(best_indep_raw) and
                   abs(best_indep_raw - vocab_entropy) <= DEGEN_TOL)

    arm_summary = (
        "uni=bpc%.3f | single=bpc%.3f | indep2=bpc%.3f cv=%.3f | indep3=bpc%.3f cv=%.3f | "
        "shared2=bpc%.3f cv=%.3f | best_indep=%s bpc%.3f cv%.3f"
    ) % (
        unigram_bpc, single_bpc,
        indep2_bpc, indep2.get("bpc_best_cv", -1.0),
        indep3_bpc, indep3.get("bpc_best_cv", -1.0),
        shared_bpc, shared.get("bpc_best_cv", -1.0),
        best_indep_name, best_indep_bpc, best_indep_cv,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "best_indep_arm": best_indep_name,
        "best_indep_bpc": round(best_indep_bpc, 4) if math.isfinite(best_indep_bpc) else None,
        "best_indep_cv": round(best_indep_cv, 4) if math.isfinite(best_indep_cv) else None,
        "single_bpc": round(single_bpc, 4) if math.isfinite(single_bpc) else None,
        "shared_W_bpc": round(shared_bpc, 4) if math.isfinite(shared_bpc) else None,
        "indep_vs_single_lift": (
            round(single_bpc - best_indep_bpc, 4)
            if math.isfinite(best_indep_bpc) and math.isfinite(single_bpc) else None),
        "indep_vs_shared_gap": (
            round(shared_bpc - best_indep_bpc, 4)
            if math.isfinite(best_indep_bpc) and math.isfinite(shared_bpc) else None),
        "sanity_single_ok": bool(sanity_single_ok),
        "sanity_shared_ok": bool(sanity_shared_ok),
        "degen_flag": bool(degen_flag),
        "vocab_entropy_uniform_bits": round(vocab_entropy, 4),
        "n_seeds": len(units),
        "thresholds": {
            "CHAIN_GRADE_BONUS_BPC": CHAIN_GRADE_BONUS_BPC,
            "HARD_PASS_BPC": HARD_PASS_BPC,
            "MIDDLE_BAND_BPC_UPPER": MIDDLE_BAND_BPC_UPPER,
            "HP_BPC_CV_MAX": HP_BPC_CV_MAX,
            "SHARED_W_GAP_CHAIN_GRADE": SHARED_W_GAP_CHAIN_GRADE,
            "SHARED_W_GAP_HARD_PASS": SHARED_W_GAP_HARD_PASS,
            "SHARED_W_GAP_FAIL_MARGIN": SHARED_W_GAP_FAIL_MARGIN,
            "SANITY_SINGLE_LAYER_REF_BPC": SANITY_SINGLE_LAYER_REF_BPC,
            "SANITY_SINGLE_LAYER_TOL": SANITY_SINGLE_LAYER_TOL,
        },
        "wave_c_production_scale": {
            "N_DIM": "8192 (production)",
            "N_TRAIN": "100k (production)",
            "N_STEPS": "1000 (production)",
            "SEEDS": "[7,17,23] (3 seeds for CV)",
            "rationale": ("smoke HARD_PASS at synthetic N=512 V=300 confirmed "
                          "INDEPENDENT beats SHARED-W; full-N text8 needed for "
                          "chain-grade tier"),
        },
        "honest_scope": (
            "cross-layer compose at FULL production LM scale (text8 N_TRAIN=100k "
            "N_DIM=8192 V=4000, 3 seeds). HARD_PASS_CHAIN_GRADE = best_indep "
            "BPC <= %.2f AND beats SHARED_W by >= %.2f BPC AND cv<=%.2f." % (
                CHAIN_GRADE_BONUS_BPC, SHARED_W_GAP_CHAIN_GRADE, HP_BPC_CV_MAX)),
        "cites": [
            "preregs/2026-06-24_substrate_cross_layer_compose_LM_v2_RESCUE_FULL.md",
            "experiments/exp_substrate_cross_layer_compose_LM_v2_RESCUE.py (smoke that landed HARD_PASS)",
            "data/exp_substrate_cross_layer_compose_LM_v2_RESCUE_smoke/metrics.json (smoke evidence)",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json (sanity rail 7.3065)",
        ],
        "by_construction_guards": {
            "real_data_asserted": True,
            "zero_llm_call_at_inference": True,
            "lambda_grid_excludes_zero": True,
            "per_arm_per_seed_logged": True,
            "atexit_partial_flush_registered": True,
            "per_seed_checkpoint_registered": True,
            "roofline_probe_available": True,
        },
    }

    if not math.isfinite(best_indep_bpc):
        return ("HARD_FAIL",
                "HARD_FAIL: all independent-layer arms failed. %s" % arm_summary,
                detail)

    if degen_flag:
        return ("READOUT_DEGENERATE",
                ("READOUT_DEGENERATE: best_indep raw_bpc=%.3f near vocab-entropy=%.3f. "
                 "Cross-layer collapsed to uniform-output regime. %s" % (
                     best_indep_raw, vocab_entropy, arm_summary)),
                detail)

    if math.isfinite(best_indep_cv) and best_indep_cv > HP_BPC_CV_MAX:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_HIGH_CV: best_indep cv=%.3f > %.2f mandatory. "
                 "best_indep BPC=%.3f; cross-layer signal seed-unstable. %s" % (
                     best_indep_cv, HP_BPC_CV_MAX, best_indep_bpc, arm_summary)),
                detail)

    # Wave-C HARD_FAIL: best_indep within SHARED_W_GAP_FAIL_MARGIN of shared_W
    shared_w_gap = (shared_bpc - best_indep_bpc) if math.isfinite(shared_bpc) else float("inf")
    detail["shared_w_gap"] = round(shared_w_gap, 4) if math.isfinite(shared_w_gap) else None
    if math.isfinite(shared_bpc) and shared_w_gap < SHARED_W_GAP_FAIL_MARGIN:
        return ("HARD_FAIL",
                ("HARD_FAIL: best_indep BPC=%.3f within %.2f of shared-W BPC=%.3f "
                 "(gap=%.3f < %.2f). Cross-layer architectural prediction did not "
                 "materialize at production scale. %s" % (
                     best_indep_bpc, SHARED_W_GAP_FAIL_MARGIN, shared_bpc,
                     shared_w_gap, SHARED_W_GAP_FAIL_MARGIN, arm_summary)),
                detail)

    # Wave-C HARD_FAIL: best_indep BPC at/above MIDDLE_BAND_BPC_UPPER (7.40)
    if best_indep_bpc >= MIDDLE_BAND_BPC_UPPER:
        return ("HARD_FAIL",
                ("HARD_FAIL: best_indep BPC=%.3f >= %.2f. Cross-layer doesn't help LM "
                 "at production scale. %s" % (
                     best_indep_bpc, MIDDLE_BAND_BPC_UPPER, arm_summary)),
                detail)

    # Wave-C HARD_PASS_CHAIN_GRADE: BPC<=6.95 AND gap>=0.15 AND CV<=0.03
    if (best_indep_bpc <= CHAIN_GRADE_BONUS_BPC and
            shared_w_gap >= SHARED_W_GAP_CHAIN_GRADE):
        verdict = "HARD_PASS"
        msg = ("HARD_PASS CHAIN_GRADE_BONUS: best_indep BPC=%.3f <= %.2f AND "
               "beats shared-W by %.3f >= %.2f BPC AND cv=%.3f <= %.2f. "
               "Cross-layer architectural prediction CONFIRMED at production scale. "
               "Sanity rails: single_ok=%s shared_ok=%s. %s" % (
                   best_indep_bpc, CHAIN_GRADE_BONUS_BPC,
                   shared_w_gap, SHARED_W_GAP_CHAIN_GRADE,
                   best_indep_cv, HP_BPC_CV_MAX,
                   sanity_single_ok, sanity_shared_ok, arm_summary))
        detail["chain_grade_bonus"] = True
        return (verdict, msg, detail)

    # Wave-C HARD_PASS: BPC<=7.20 AND gap>=0.10
    if (best_indep_bpc <= HARD_PASS_BPC and
            shared_w_gap >= SHARED_W_GAP_HARD_PASS):
        verdict = "HARD_PASS"
        msg = ("HARD_PASS: best_indep BPC=%.3f <= %.2f AND beats shared-W by "
               "%.3f >= %.2f BPC. Cross-layer helpful but below chain-grade discriminator. "
               "Sanity rails: single_ok=%s shared_ok=%s. %s" % (
                   best_indep_bpc, HARD_PASS_BPC, shared_w_gap, SHARED_W_GAP_HARD_PASS,
                   sanity_single_ok, sanity_shared_ok, arm_summary))
        detail["chain_grade_bonus"] = False
        return (verdict, msg, detail)

    verdict = "MIDDLE_BAND"
    msg = ("MIDDLE_BAND: best_indep BPC=%.3f in (%.2f, %.2f]. "
           "Cross-layer partial signal at production scale (gap to shared_W=%.3f). %s" % (
               best_indep_bpc, HARD_PASS_BPC, MIDDLE_BAND_BPC_UPPER,
               shared_w_gap, arm_summary))
    detail["chain_grade_bonus"] = False
    return (verdict, msg, detail)


# ============================================================================
# Main loop with per-seed checkpoint + atexit
# ============================================================================

print("[config] anchor=%s arms=%s N_DIM=%d mode=%s seeds=%s N_TRAIN=%d N_STEPS=%d" % (
    ANCHOR_NAME, ARMS, N_DIM, RUN_MODE, SEEDS, N_TRAIN, N_STEPS), flush=True)

if DEVICE.type == "cuda":
    print("[gpu] %s" % torch.cuda.get_device_name(0), flush=True)
else:
    print("[device] CPU (no CUDA available)", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
done_seeds: List[int] = []
remaining_seeds: List[int] = SEEDS[:]

try:
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = _resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d done, %d remaining: %s" % (
        len(done_seeds), len(remaining_seeds), remaining_seeds), flush=True)
except TypeError:
    # Older _seed_checkpoint without run_config support
    done_seeds, remaining_seeds = _resumable_seeds(SEEDS, out_dir)
    print("[ckpt] (no run_config check) %d done, %d remaining: %s" % (
        len(done_seeds), len(remaining_seeds), remaining_seeds), flush=True)
except Exception as e:
    print("[ckpt] resumable_seeds failed (%s); running all seeds" % e, flush=True)
    remaining_seeds = SEEDS[:]

_LIVE_STATE["phase"] = "running"
_LIVE_STATE["seeds_done"] = list(done_seeds)

for seed in remaining_seeds:
    print("\n[run] seed=%d starting..." % seed, flush=True)
    result = run_unit(seed)
    write_partial(out_dir, seed, result)
    _LIVE_STATE["seeds_done"].append(seed)
    print("[ckpt] seed=%d partial written" % seed, flush=True)

_LIVE_STATE["phase"] = "aggregating"
per_seed = aggregate_partials(out_dir, SEEDS)
all_units = list(per_seed.values())

verdict, verdict_msg, detail = compute_verdict(all_units)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

summary = {
    "best_indep_bpc": detail.get("best_indep_bpc"),
    "best_indep_arm": detail.get("best_indep_arm"),
    "single_bpc": detail.get("single_bpc"),
    "shared_W_bpc": detail.get("shared_W_bpc"),
    "indep_vs_single_lift": detail.get("indep_vs_single_lift"),
    "indep_vs_shared_gap": detail.get("indep_vs_shared_gap"),
    "n_seeds": len(all_units),
}

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": summary,
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "ARM_CONFIG": ARM_CONFIG,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "CFRPE_LR": CFRPE_LR,
    "N_STEPS": N_STEPS,
    "LAMBDA_GRID": LAMBDA_GRID,
    "TEMP_GRID": TEMP_GRID,
    "detail": detail,
    "per_seed": [
        {"seed": u.get("seed"), "by_arm": u.get("by_arm"),
         "V": u.get("V"), "N_DIM": u.get("N_DIM"), "N_TRAIN": u.get("N_TRAIN"),
         "elapsed_s_seed": u.get("elapsed_s_seed"), "device": u.get("device"),
         "encoder_meta": u.get("encoder_meta", {})}
        for u in all_units
    ],
    "elapsed_s": round(sum(u.get("elapsed_s_seed", 0.0) for u in all_units), 2),
}

write_metrics(out_dir, metrics, all_units)
print("[metrics] written to %s" % out_dir, flush=True)
_LIVE_STATE["phase"] = "done"
