"""
substrate_cfrpe_x_amplitude_correct_f002_LM_v2 -- RESCUE of v1 (timeout=900s exhausted)

CHANGES vs v1:
  - ANCHOR_NAME updated to v2
  - ARM_HEBBIAN_f002_UNSCALED dropped (expected dead-zone; saves ~20% wall time)
  - timeout_s 900 -> 3600 (4x; v1 exhausted 900s without completing)
  - No logic changes to any surviving arm.

Hypothesis: cf-RPE delta rule composes super-additively with amplitude-correct sparse-bipolar
at f=0.02. Viability shotgun showed sparse-bipolar WITHOUT amplitude scaling at f=0.02 gives
6% recall (DEAD), while WITH scaling gives 99% recall (LIVE). This cell tests whether the
+0.141 BPC lift from cf-RPE (chain-grade at f=0.05) ALSO lifts when combined with amplitude-
correct sparse-bipolar at f=0.02 -- the hypothesis is that lower sparsity (fewer active
dimensions) gives cleaner separation between tokens, and cf-RPE can exploit that structure.

FIVE ARMS (5 arms x 3 seeds x N_DIM=8192 x N_TRAIN=100k text8):
  ARM_UNIGRAM                     -- analytic baseline
  ARM_HEBBIAN_f005_UNSCALED       -- baseline; reproduces fair_harness chain-grade 7.3065
  ARM_HEBBIAN_f002_AMPLITUDE_SCALED  -- tests if amplitude scaling at f=0.02 produces lift
  ARM_CFRPE_f005_UNSCALED         -- reproduces cf-RPE +0.141 chain-grade lift (f=0.05)
  ARM_CFRPE_f002_AMPLITUDE_SCALED -- COMBINED arm: cf-RPE + amplitude-correct at f=0.02

(ARM_HEBBIAN_f002_UNSCALED dropped vs v1; it was a dead-zone sanity check expected to
 collapse per viability shotgun; not needed for verdict.)

PRE-REG BANDS (same as v1; BPC; lift = lower BPC is better):
  HARD_PASS_SUPER_ADDITIVE: ARM_CFRPE_f002_AMPLITUDE_SCALED beats ARM_HEBBIAN_f005_UNSCALED
    by >= +0.30 bits (super-additive composition of cf-RPE + amplitude-correct + low-f)
  HARD_PASS_ADDITIVE: ARM_CFRPE_f002_AMPLITUDE_SCALED beats ARM_CFRPE_f005_UNSCALED
    by >= +0.10 bits (amplitude-correct + low-f adds over cf-RPE alone)
  MIDDLE_BAND: combined arm lift over cf-RPE alone in [+0.03, +0.10)
  HARD_FAIL: ARM_CFRPE_f002_AMPLITUDE_SCALED <= ARM_CFRPE_f005_UNSCALED
    (knobs don't compose; cf-RPE saturates substrate-as-LM signal at this scale)
  cv < 0.05

AMPLITUDE SCALING:
  1/sqrt(f) multiplier on nonzero entries BEFORE L2-normalization.
  For f=0.02: scale = 1/sqrt(0.02) ~= 7.071
  Corrects for sqrt(k/N) norm shrinkage: ensures W = E^T @ E has spectral norm
  proportional to 1/f, matching the capacity-correct formulation.

ROUTING: overnight_queue (GPU) -- N_DIM=8192 hits Fix #22 threshold.
  Torch + CUDA used when available (GPU path, Fix #24 mandate).
  CPU fallback for smoke on laptop (no CUDA).
  Encoder hoisted outside arm loop (Fix #24 pattern from source cell).
  Per-seed checkpoint (restartable). ASCII-only.

Cites:
  preregs/2026-06-24_substrate_cfrpe_x_amplitude_correct_f002_LM_v2.md
  preregs/2026-06-23_substrate_cfrpe_x_amplitude_correct_f002_LM_v1.md
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py
  notes/substrate_viability_shotgun_LIVE_DEAD_map_2026-06-23.md
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

ANCHOR_NAME = "substrate_cfrpe_x_amplitude_correct_f002_LM_v2"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# ============================================================================
# Pre-registered threshold bands (filed BEFORE run; no ex-post changes)
# Same bands as v1 preregs/2026-06-23_substrate_cfrpe_x_amplitude_correct_f002_LM_v1.md
# ============================================================================
HARD_PASS_SUPER_ADDITIVE_LIFT = 0.30   # combined beats Hebbian baseline by >=0.30 bits
HARD_PASS_ADDITIVE_LIFT_OVER_CFRPE = 0.10  # combined beats cf-RPE alone by >=0.10 bits
MIDDLE_BAND_LOWER = 0.03               # combined beats cf-RPE alone by [0.03, 0.10)
HARD_FAIL_THRESHOLD = 0.00             # combined <= cf-RPE alone (no additive benefit)
CV_MAX = 0.05                          # BPC cv across seeds mandatory

# Reference from fair_harness baseline (chain-grade, cert row 473)
BASELINE_HEBBIAN_BPC = 7.3065

# Plasticity knobs (same as source cell for comparability)
CFRPE_LR = 0.5
INGEST_BATCH = 64

# Inference grids
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# f-sparsity parameters
F_BASELINE = 0.05    # chain-grade validated (fair_harness baseline)
F_LOW = 0.02         # low-f target from viability shotgun
# 1/sqrt(f) amplitude correction: ensures W spectral norm ~= 1/f (capacity-correct)
AMPLITUDE_SCALE_f002 = 1.0 / math.sqrt(F_LOW)    # ~7.071
AMPLITUDE_SCALE_f005 = 1.0 / math.sqrt(F_BASELINE)  # ~4.472

# DEGEN check: raw_bpc at T=1 near vocab_entropy => degenerate (only at large V)
DEGEN_MIN_ENTROPY_BITS = 10.0    # require V >= 1024
DEGEN_TOL_FRAC = 0.05            # raw_bpc within 5% of log2(V) => degenerate

# v2: 5 arms (ARM_HEBBIAN_f002_UNSCALED dropped vs v1)
ARMS = [
    "ARM_UNIGRAM",
    "ARM_HEBBIAN_f005_UNSCALED",
    "ARM_HEBBIAN_f002_AMPLITUDE_SCALED",
    "ARM_CFRPE_f005_UNSCALED",
    "ARM_CFRPE_f002_AMPLITUDE_SCALED",
]
PLASTICITY_ARMS = [a for a in ARMS if a != "ARM_UNIGRAM"]

# arm_name -> (f, amplitude_scaled, use_cfrpe)
ARM_CONFIG: Dict[str, Tuple[float, bool, bool]] = {
    "ARM_HEBBIAN_f005_UNSCALED":       (F_BASELINE, False, False),
    "ARM_HEBBIAN_f002_AMPLITUDE_SCALED": (F_LOW,    True,  False),
    "ARM_CFRPE_f005_UNSCALED":         (F_BASELINE, False, True),
    "ARM_CFRPE_f002_AMPLITUDE_SCALED": (F_LOW,      True,  True),
}

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

# Production config (no _nN suffix per PROT-018 rule 3; N=8192 stated in prereg)
N_DIM = 8192
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = 1000
else:
    # Smoke: small enough to run on CPU in ~3 min
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    N_STEPS = 80

_GENSIM_KV_CACHE: Dict[str, object] = {}


# ============================================================================
# Encoders + projection
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
        accum += _bipolar_hv_np(_seed_for_trigram(t[i:i + 3], seed), n_dim)
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def _l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (float(np.linalg.norm(X)) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def _l2_normalize_t(X: torch.Tensor, eps: float = 1e-12) -> torch.Tensor:
    if X.dim() == 1:
        return X / (X.norm() + eps)
    return X / (X.norm(dim=1, keepdim=True) + eps)


def _gaussian_projection(in_dim: int, out_dim: int, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed * 991 + 73)
    return rng.standard_normal((out_dim, in_dim)).astype(np.float32) / math.sqrt(float(in_dim))


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
    n_hit = n_miss = 0
    for i, w in enumerate(vocab):
        v = None
        for key in (w, w.lower()):
            if key in kv.key_to_index:
                v = kv[key]
                break
        if v is None:
            try:
                v = kv.get_vector(w, norm=False)
            except Exception:
                pass
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
    oov_mask = np.linalg.norm(E_pre, axis=1) < 1e-9
    for i in np.where(oov_mask)[0]:
        E_proj[i] = char_trigram_encode(vocab[i], n_dim, seed)
    E_proj = _l2_normalize_np(E_proj)
    E_t = torch.from_numpy(E_proj).to(device=DEVICE, dtype=TORCH_DTYPE)
    meta = {"n_hit": int(n_hit), "n_miss": int(n_miss),
            "n_vocab": int(len(vocab)), "pretrain_dim": int(kv.vector_size)}
    return E_t, meta


def build_E_char_trigram_gpu(vocab: List[str], n_dim: int, seed: int) -> torch.Tensor:
    E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0)
    return torch.from_numpy(_l2_normalize_np(E_np)).to(device=DEVICE, dtype=TORCH_DTYPE)


# ============================================================================
# Sparse-bipolar with optional amplitude scaling (GPU tensor version)
# ============================================================================

def sparsify_bipolar_gpu(E: torch.Tensor, f: float,
                          amplitude_scale: float = 1.0) -> torch.Tensor:
    """Sparse-bipolar: keep top-k by abs magnitude, set sign * amplitude_scale.

    amplitude_scale = 1.0 -> unscaled (original fair_harness behavior)
    amplitude_scale = 1/sqrt(f) -> amplitude-correct (capacity-correct formulation)

    After this call, caller applies L2-normalization.
    """
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    abs_E = E.abs()
    _, topk_idx = torch.topk(abs_E, k=k, dim=1)
    out = torch.zeros_like(E)
    row_idx = torch.arange(V, device=E.device).unsqueeze(1).expand(-1, k)
    signs = torch.sign(E.gather(1, topk_idx))
    signs = torch.where(signs == 0, torch.ones_like(signs), signs)
    out[row_idx, topk_idx] = signs * amplitude_scale
    return out


# ============================================================================
# Plasticity rules: Hebbian / cf-RPE (GPU tensor version)
# ============================================================================

def build_W_plasticity(arm: str, E: torch.Tensor, idx_train_t: torch.Tensor,
                        n_steps: int, batch: int, lr: float,
                        ingest_chunk: int, gen: torch.Generator) -> torch.Tensor:
    """Build W via plasticity rule.

    ARM_HEBBIAN_*:  W = sum outer(E[t+1], E[t]) -- rank-1 symmetric Hebbian
    ARM_CFRPE_*:    iterative stochastic cf-RPE delta rule
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W
    use_cfrpe = ARM_CONFIG[arm][2]

    if not use_cfrpe:
        # One-pass batched outer-product Hebbian
        for b in range(0, n_pairs, ingest_chunk):
            end = min(b + ingest_chunk, n_pairs)
            E_src = E[idx_train_t[b:end]]
            E_tgt = E[idx_train_t[b + 1:end + 1]]
            W.add_(E_tgt.T @ E_src)
            if DEVICE.type == "cuda" and (b // ingest_chunk) % 16 == 0:
                torch.cuda.synchronize()
        return W

    # Iterative stochastic cf-RPE delta rule
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train_t[st]]        # [batch, dim]
        Nxt = E[idx_train_t[st + 1]]    # [batch, dim]
        error = Nxt - Ctx @ W.t()
        dW = (error.t() @ Ctx) / batch
        W = W + lr * dW

    return W


# ============================================================================
# Per-arm logit builder
# ============================================================================

def compute_arm_logits(arm: str, E_base: torch.Tensor, idx_train: np.ndarray,
                        idx_held: np.ndarray, seed: int, n_steps: int) -> Dict:
    """Return [n_held, V] float32 logits + diagnostics. FRESH W per arm."""
    f, amplitude_scaled, _ = ARM_CONFIG[arm]
    amplitude_scale = (1.0 / math.sqrt(f)) if amplitude_scaled else 1.0

    # Apply sparse-bipolar + optional amplitude scaling, then L2-normalize
    E_sp = sparsify_bipolar_gpu(E_base, f, amplitude_scale=amplitude_scale)
    E_used = _l2_normalize_t(E_sp)

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    gen = torch.Generator(device=DEVICE)
    gen.manual_seed(seed * 10007 + ARMS.index(arm) * 31337)

    t0 = time.time()
    W = build_W_plasticity(arm, E_used, idx_train_t, n_steps=n_steps,
                            batch=INGEST_BATCH, lr=CFRPE_LR,
                            ingest_chunk=INGEST_CHUNK, gen=gen)
    t_ingest = time.time() - t0

    t0 = time.time()
    n_h = idx_held_t.shape[0]
    V = E_base.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        ctx = E_used[idx_held_t[b:end]]
        pred = _l2_normalize_t(ctx @ W.t())
        logits[b:end] = pred @ E_used.T
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    raw_bpc = _raw_bpc_at_T1(logits, idx_held, V)
    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    del W, logits, E_used, E_sp
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "raw_bpc_at_T1_L1": round(raw_bpc, 4),
        "f": f,
        "amplitude_scaled": amplitude_scaled,
        "amplitude_scale_value": round(amplitude_scale, 4),
    }


def _raw_bpc_at_T1(logits: torch.Tensor, idx_held: np.ndarray, V: int) -> float:
    n_h = logits.shape[0]
    nxt_np = idx_held[1:] if len(idx_held) > 1 else idx_held
    n_eval = min(n_h, len(nxt_np))
    if n_eval == 0:
        return float("inf")
    lg_np = logits[:n_eval].detach().cpu().numpy()
    nxt_eval = nxt_np[:n_eval]
    z = lg_np - lg_np.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / np.clip(e.sum(axis=1, keepdims=True), 1e-30, None)
    p_nxt = p[np.arange(n_eval), nxt_eval].clip(1e-12, 1.0)
    return float(-np.mean(np.log(p_nxt)) / math.log(2.0))


# ============================================================================
# text8 corpus utilities
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
    vocab = ["<unk>"] + [w for w, _ in c.most_common(cap - 1)]
    return vocab, {w: i for i, w in enumerate(vocab)}


def tokens_to_idx(toks: List[str], w2i: Dict[str, int]) -> np.ndarray:
    unk = w2i["<unk>"]
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


# ============================================================================
# Joint (T, lambda) sweep + BPC / top-1 / MRR metrics
# ============================================================================

def softmax_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9) - logits.max(axis=-1, keepdims=True) / max(T, 1e-9)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp(sub_logp: np.ndarray, U_log: np.ndarray, lam: float) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    return float("inf") if n == 0 else -float(np.mean(logp[np.arange(n), nxt])) / math.log(2.0)


def top1_acc(logp: np.ndarray, nxt: np.ndarray) -> float:
    return float("nan") if len(nxt) == 0 else float(np.mean(np.argmax(logp, axis=1) == nxt))


def mrr_at_k(logp: np.ndarray, nxt: np.ndarray, k: int) -> float:
    n = len(nxt)
    if n == 0:
        return float("nan")
    k_use = min(k, logp.shape[1])
    top_idx = np.argpartition(-logp, kth=k_use - 1, axis=1)[:, :k_use]
    rows = np.arange(n)[:, None]
    top_vals = logp[rows, top_idx]
    order = np.argsort(-top_vals, axis=1)
    top_idx_s = top_idx[rows, order]
    rr = 0.0
    for i in range(n):
        m = np.where(top_idx_s[i] == nxt[i])[0]
        if len(m) > 0:
            rr += 1.0 / float(m[0] + 1)
    return float(rr / n)


def joint_sweep(sub_dev: np.ndarray, sub_test: np.ndarray,
                U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                temp_grid: list, lambda_grid: list, mrr_k: int) -> Dict:
    best_bpc = {"T": 1.0, "lambda": 1.0, "dv": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dv": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dv": -1.0}
    for T in temp_grid:
        logp_sub_dev = np.log(np.clip(softmax_with_T(sub_dev, T), 1e-30, 1.0))
        for lam in lambda_grid:
            logp_dev = log_linear_interp(logp_sub_dev, U_log, lam)
            bd = bpc_from_logp(logp_dev, nxt_dev)
            td = top1_acc(logp_dev, nxt_dev)
            md = mrr_at_k(logp_dev, nxt_dev, mrr_k)
            if bd < best_bpc["dv"]:
                best_bpc = {"T": float(T), "lambda": float(lam), "dv": bd}
            if td > best_top1["dv"]:
                best_top1 = {"T": float(T), "lambda": float(lam), "dv": td}
            if md > best_mrr["dv"]:
                best_mrr = {"T": float(T), "lambda": float(lam), "dv": md}

    def _test(T, lam, fn):
        logp_sub = np.log(np.clip(softmax_with_T(sub_test, T), 1e-30, 1.0))
        return fn(log_linear_interp(logp_sub, U_log, lam), nxt_test)

    return {
        "bpc_best": round(_test(best_bpc["T"], best_bpc["lambda"], bpc_from_logp), 4),
        "best_T_for_bpc": best_bpc["T"],
        "best_lambda_for_bpc": best_bpc["lambda"],
        "best_dev_bpc": round(best_bpc["dv"], 4),
        "top1_acc": round(_test(best_top1["T"], best_top1["lambda"], top1_acc), 4),
        "best_T_for_top1": best_top1["T"],
        "best_lambda_for_top1": best_top1["lambda"],
        "mrr_at_10": round(_test(best_mrr["T"], best_mrr["lambda"],
                                  lambda lp, nx: mrr_at_k(lp, nx, mrr_k)), 4),
        "best_T_for_mrr": best_mrr["T"],
        "best_lambda_for_mrr": best_mrr["lambda"],
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
    if len(nxt_eval) == 0:
        return {"bpc_unigram": float("inf"), "top1_unigram": 0.0,
                "mrr_unigram": 0.0, "n_test": 0}
    n_dev = len(nxt_eval) // 2
    nxt_test = nxt_eval[n_dev:]
    p_test = U[nxt_test].clip(1e-12, 1.0)
    bpc = float(-np.mean(np.log(p_test)) / math.log(2.0))
    am = int(np.argmax(U))
    order = np.argsort(-U)
    inv_rank = np.empty_like(order)
    inv_rank[order] = np.arange(len(order))
    ranks = inv_rank[nxt_test] + 1
    rr = float(np.mean(np.where(ranks <= mrr_k, 1.0 / ranks, 0.0)))
    return {"bpc_unigram": round(bpc, 4), "top1_unigram": round(float(np.mean(nxt_test == am)), 4),
            "mrr_unigram": round(rr, 4), "n_test": int(len(nxt_test))}


# ============================================================================
# Instrumentation self-test (MANDATORY per role contract)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)

    dev = DEVICE
    rng = np.random.default_rng(42)

    # ST1: amplitude_scale 1/sqrt(f) applied in sparsify_bipolar_gpu:
    #  W spectral norm scales as amp^2 = 1/f (quadratic in amplitude).
    #  Verify ratio of ||W_scaled||_F / ||W_unscaled||_F ~= 1/f for the pre-norm case.
    n_dim_st, f_st = 64, 0.25
    k_st = max(1, int(round(f_st * n_dim_st)))
    amp_st = 1.0 / math.sqrt(f_st)
    E_st = torch.randn(8, n_dim_st, device=dev, dtype=TORCH_DTYPE)
    E_st = _l2_normalize_t(E_st)
    E_sp_unscaled = sparsify_bipolar_gpu(E_st, f_st, amplitude_scale=1.0)
    E_sp_scaled = sparsify_bipolar_gpu(E_st, f_st, amplitude_scale=amp_st)
    W_unscaled = E_sp_unscaled.T @ E_sp_unscaled
    W_scaled = E_sp_scaled.T @ E_sp_scaled
    ratio = float(W_scaled.norm() / (W_unscaled.norm() + 1e-12))
    expected = amp_st ** 2  # = 1/f = 4.0
    assert abs(ratio - expected) < 1.0, (
        "ST1 W spectral ratio=%.3f expected~=%.3f (1/f=%.2f amp=%.4f)" % (
            ratio, expected, 1.0 / f_st, amp_st))
    print("[selftest] ST1 amplitude scaling: W ratio=%.3f ~= 1/f=%.3f" % (ratio, expected), flush=True)

    # ST2: L2-normalized rows are unit norm after amplitude scaling
    E_norm = _l2_normalize_t(E_sp_scaled)
    row_norms = E_norm.norm(dim=1)
    assert float(row_norms.min()) > 0.99, "ST2 some rows not unit norm after L2-norm"
    print("[selftest] ST2 L2-norm after amplitude scaling: min_norm=%.4f" % float(row_norms.min()), flush=True)

    # ST3: cf-RPE delta shrinks prediction error for single L2-normalized pair
    Ctx3 = torch.randn(1, n_dim_st, device=dev, dtype=TORCH_DTYPE)
    Nxt3 = torch.randn(1, n_dim_st, device=dev, dtype=TORCH_DTYPE)
    Ctx3 = _l2_normalize_t(Ctx3)
    Nxt3 = _l2_normalize_t(Nxt3)
    W3 = torch.zeros(n_dim_st, n_dim_st, device=dev, dtype=TORCH_DTYPE)
    err_before = float((Nxt3 - Ctx3 @ W3.t()).norm())
    dW3 = (Nxt3 - Ctx3 @ W3.t()).t() @ Ctx3
    W3_after = W3 + 0.01 * dW3   # small LR to avoid overshoot at batch=1
    err_after = float((Nxt3 - Ctx3 @ W3_after.t()).norm())
    assert err_after < err_before, (
        "ST3 cf-RPE should shrink error: before=%.4f after=%.4f" % (err_before, err_after))
    print("[selftest] ST3 cf-RPE error shrink OK: %.4f -> %.4f" % (err_before, err_after), flush=True)

    # ST4: build_W_plasticity callable (Hebbian arm)
    n_v_st4, n_dim_st4 = 8, 32
    E_st4 = _l2_normalize_t(torch.randn(n_v_st4, n_dim_st4, device=dev, dtype=TORCH_DTYPE))
    idx_st4 = torch.zeros(50, dtype=torch.long, device=dev)
    gen_st4 = torch.Generator(device=dev)
    gen_st4.manual_seed(99)
    W4 = build_W_plasticity("ARM_HEBBIAN_f005_UNSCALED", E_st4, idx_st4,
                              n_steps=0, batch=4, lr=0.5,
                              ingest_chunk=50, gen=gen_st4)
    assert W4 is not None and torch.all(torch.isfinite(W4)), "ST4 Hebbian W not finite"
    print("[selftest] ST4 build_W_plasticity (Hebbian) callable OK", flush=True)

    # ST5: build_W_plasticity callable (cf-RPE arm)
    gen_st5 = torch.Generator(device=dev)
    gen_st5.manual_seed(7)
    W5 = build_W_plasticity("ARM_CFRPE_f005_UNSCALED", E_st4, idx_st4,
                              n_steps=10, batch=4, lr=0.5,
                              ingest_chunk=50, gen=gen_st5)
    assert W5 is not None and torch.all(torch.isfinite(W5)), "ST5 cf-RPE W not finite"
    print("[selftest] ST5 build_W_plasticity (cf-RPE) callable OK", flush=True)

    # ST6: joint_sweep returns finite metrics for synthetic data
    n_tok_st6, n_v_st6 = 30, 6
    rng6 = np.random.default_rng(99)
    logits_st6 = rng6.standard_normal((n_tok_st6, n_v_st6)).astype(np.float32)
    nxt_st6 = rng6.integers(0, n_v_st6, size=n_tok_st6).astype(np.int64)
    U_log_st6 = np.log(np.full(n_v_st6, 1.0 / n_v_st6))
    nd6 = n_tok_st6 // 2
    jr6 = joint_sweep(logits_st6[:nd6], logits_st6[nd6:], U_log_st6,
                      nxt_st6[:nd6], nxt_st6[nd6:], TEMP_GRID, LAMBDA_GRID, MRR_K)
    assert math.isfinite(jr6["bpc_best"]), "ST6 bpc_best not finite"
    assert math.isfinite(jr6["top1_acc"]), "ST6 top1_acc not finite"
    assert math.isfinite(jr6["mrr_at_10"]), "ST6 mrr not finite"
    assert jr6["n_dev"] > 0 and jr6["n_test"] > 0, "ST6 zero eval tokens"
    print("[selftest] ST6 joint_sweep OK (bpc=%.3f top1=%.4f mrr=%.4f)" % (
        jr6["bpc_best"], jr6["top1_acc"], jr6["mrr_at_10"]), flush=True)

    # ST7: ARM_CONFIG has correct entries for all 4 plasticity arms (v2: 4 not 5)
    for arm in PLASTICITY_ARMS:
        assert arm in ARM_CONFIG, "ST7 arm %s not in ARM_CONFIG" % arm
    f_c, amp_c, cf_c = ARM_CONFIG["ARM_CFRPE_f002_AMPLITUDE_SCALED"]
    assert f_c == F_LOW and amp_c is True and cf_c is True, (
        "ST7 combined arm config wrong: f=%s amp=%s cfrpe=%s" % (f_c, amp_c, cf_c))
    print("[selftest] ST7 ARM_CONFIG verified for all %d arms (combined f=%.3f amp=%s cfrpe=%s)" % (
        len(PLASTICITY_ARMS), f_c, amp_c, cf_c), flush=True)

    # ST8: AMPLITUDE_SCALE_f002 = 1/sqrt(F_LOW) exactly
    expected_amp = 1.0 / math.sqrt(F_LOW)
    assert abs(AMPLITUDE_SCALE_f002 - expected_amp) < 1e-6, (
        "ST8 AMPLITUDE_SCALE_f002=%.6f expected=%.6f" % (AMPLITUDE_SCALE_f002, expected_amp))
    print("[selftest] ST8 AMPLITUDE_SCALE_f002=%.6f verified" % AMPLITUDE_SCALE_f002, flush=True)

    # ST9: _raw_bpc_at_T1 returns finite positive value
    logits_st9 = torch.randn(20, 8, device=dev, dtype=TORCH_DTYPE)
    idx_st9 = np.random.default_rng(33).integers(0, 8, size=21).astype(np.int64)
    bpc_st9 = _raw_bpc_at_T1(logits_st9, idx_st9, V=8)
    assert math.isfinite(bpc_st9) and bpc_st9 > 0.0, "ST9 _raw_bpc_at_T1 invalid: %s" % bpc_st9
    print("[selftest] ST9 _raw_bpc_at_T1 OK (bpc=%.3f)" % bpc_st9, flush=True)

    # ST10: v2 confirms ARM_HEBBIAN_f002_UNSCALED absent (dropped arm)
    assert "ARM_HEBBIAN_f002_UNSCALED" not in ARMS, "ST10 dropped arm still present in ARMS list"
    assert "ARM_HEBBIAN_f002_UNSCALED" not in ARM_CONFIG, "ST10 dropped arm still in ARM_CONFIG"
    print("[selftest] ST10 ARM_HEBBIAN_f002_UNSCALED correctly absent from v2 (dropped)", flush=True)

    print("[selftest] ALL 10 TESTS PASS", flush=True)


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
        seed, V, N_TRAIN, N_HELD, N_DIM, DEVICE), flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[seed=%d gpu] %s mem_total_gb=%.2f" % (
                seed, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9), flush=True)
        except Exception:
            pass

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d ARM_UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"], uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    # Hoist encoder outside arm loop (Fix #24: load once, reuse per arm)
    print("\n[seed=%d] building encoder V=%d N_DIM=%d device=%s..." % (
        seed, V, N_DIM, DEVICE), flush=True)
    t_enc0 = time.time()
    encoder_meta = {}
    try:
        E_base, encoder_meta = build_E_word2vec_gpu(vocab, N_DIM, seed)
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("[seed=%d encoder] WORD2VEC FAIL: %s -- fallback char-trigram" % (seed, err), flush=True)
        E_base = build_E_char_trigram_gpu(vocab, N_DIM, seed)
        encoder_meta = {"fallback_to_char_trigram": True, "load_error": err}
    t_enc = time.time() - t_enc0
    print("[seed=%d encoder] built %.1fs shape=%s" % (seed, t_enc, str(list(E_base.shape))), flush=True)
    if DEVICE.type == "cuda":
        try:
            free_b, total_b = torch.cuda.mem_get_info()
            print("[seed=%d gpu] free=%.2fGB total=%.2fGB" % (
                seed, free_b / 1e9, total_b / 1e9), flush=True)
        except Exception:
            pass

    # Split held into dev + test halves
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        for arm in PLASTICITY_ARMS:
            by_arm[arm] = {"empty_eval": True}
        del E_base
        return {"seed": seed, "by_arm": by_arm, "V": V, "N_DIM": N_DIM,
                "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2), "device": str(DEVICE),
                "encoder_meta": encoder_meta}
    n_dev = n_eval // 2
    valid_held_pos = np.where(mask)[0]
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    for arm in PLASTICITY_ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building W + logits..." % (seed, arm), flush=True)
        try:
            ar = compute_arm_logits(arm, E_base, idx_train, idx_held, seed, N_STEPS)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
            by_arm[arm] = {
                "compute_failed": True, "compute_error": err,
                "bpc_best": float("inf"), "top1_acc": float("nan"),
                "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
                "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                "elapsed_s_arm": round(time.time() - t_arm0, 2),
            }
            continue

        logits_full = ar["logits"]
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            logits_ctx = logits_full
            mask_pos = np.array([p for p in valid_held_pos if p < logits_ctx.shape[0]], dtype=np.int64)
            logits_eval = logits_ctx[mask_pos]
            nxt_ev2 = nxt_full[mask_pos]
            ne2 = len(nxt_ev2)
            ndev2 = ne2 // 2
            jr = joint_sweep(logits_eval[:ndev2], logits_eval[ndev2:], U_log,
                             nxt_ev2[:ndev2], nxt_ev2[ndev2:], TEMP_GRID, LAMBDA_GRID, MRR_K)
            jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
            jr.update({k: ar[k] for k in ("wall_ingest_s", "wall_recall_s",
                                           "raw_bpc_at_T1_L1", "f", "amplitude_scaled",
                                           "amplitude_scale_value") if k in ar})
            by_arm[arm] = jr
            print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
                  "(bestT=%.4f bestL=%.2f) raw_bpc_T1=%.3f" % (
                      seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                      jr["best_T_for_bpc"], jr["best_lambda_for_bpc"],
                      jr["raw_bpc_at_T1_L1"]), flush=True)
            continue

        logits_eval = logits_ctx[mask]
        jr = joint_sweep(logits_eval[:n_dev], logits_eval[n_dev:], U_log,
                         nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K)
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr.update({k: ar[k] for k in ("wall_ingest_s", "wall_recall_s",
                                       "raw_bpc_at_T1_L1", "f", "amplitude_scaled",
                                       "amplitude_scale_value") if k in ar})
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f mrr=%.4f "
              "(bestT=%.4f bestL=%.2f) raw_bpc_T1=%.3f" % (
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
# Verdict (per pre-registered bands -- same as v1)
# ============================================================================

def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}
    V_ref = max(units[0].get("V", 4000), 2)
    vocab_entropy = math.log2(V_ref)

    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan")) for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "bpc_mean": round(float(np.nanmean(uni_bpc)), 4),
        "bpc_std": round(float(np.nanstd(uni_bpc)), 4),
    }
    unigram_bpc = by_arm_agg["ARM_UNIGRAM"]["bpc_mean"]

    for arm in PLASTICITY_ARMS:
        seeds_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid = [(not cf) and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))
                 for cf, u in zip(seeds_failed, units)]
        valid_units = [u for ok, u in zip(valid, units) if ok]
        n_failed = int(sum(seeds_failed))
        if not valid_units:
            by_arm_agg[arm] = {
                "bpc_best_mean": float("inf"), "top1_acc_mean": float("nan"),
                "mrr_at_10_mean": float("nan"), "raw_bpc_at_T1_L1_mean": float("nan"),
                "n_valid_seeds": 0, "n_compute_failed": n_failed, "all_seeds_failed": True,
            }
            continue
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_v = [u["by_arm"][arm]["raw_bpc_at_T1_L1"] for u in valid_units]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "top1_acc_std": round(float(np.std(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_v)), 4),
            "n_valid_seeds": int(len(valid_units)),
            "n_compute_failed": n_failed,
            "all_seeds_failed": False,
        }

    def _arm_bpc(name: str) -> float:
        return by_arm_agg.get(name, {}).get("bpc_best_mean", float("inf"))

    heb_f005_bpc = _arm_bpc("ARM_HEBBIAN_f005_UNSCALED")
    heb_f002_scaled_bpc = _arm_bpc("ARM_HEBBIAN_f002_AMPLITUDE_SCALED")
    cfrpe_f005_bpc = _arm_bpc("ARM_CFRPE_f005_UNSCALED")
    cfrpe_f002_scaled_bpc = _arm_bpc("ARM_CFRPE_f002_AMPLITUDE_SCALED")

    combined_failed = by_arm_agg.get("ARM_CFRPE_f002_AMPLITUDE_SCALED", {}).get("all_seeds_failed", True)
    combined_cv = by_arm_agg.get("ARM_CFRPE_f002_AMPLITUDE_SCALED", {}).get("bpc_best_cv", float("nan"))
    combined_raw = by_arm_agg.get("ARM_CFRPE_f002_AMPLITUDE_SCALED", {}).get("raw_bpc_at_T1_L1_mean", float("nan"))

    # Pre-reg primary verdicts
    lift_vs_hebbian = heb_f005_bpc - cfrpe_f002_scaled_bpc   # positive = combined better
    lift_vs_cfrpe = cfrpe_f005_bpc - cfrpe_f002_scaled_bpc   # positive = combined beats cf-RPE

    # Sanity rail: heb_f002_scaled should beat heb_f005_unscaled (shotgun: 99% recall)
    heb_f002_scaled_lift = (heb_f002_scaled_bpc < heb_f005_bpc)

    # DEGEN check (only meaningful at production vocab scale)
    degen_tol = DEGEN_TOL_FRAC * vocab_entropy
    degen_flag = (
        math.isfinite(combined_raw)
        and vocab_entropy >= DEGEN_MIN_ENTROPY_BITS
        and abs(combined_raw - vocab_entropy) <= degen_tol
    )

    arm_summary = (
        "uni=%.3f | heb_f005_unsc=%.3f | heb_f002_amp=%.3f | "
        "cfrpe_f005=%.3f | cfrpe_f002_amp=%.3f | "
        "lift_vs_heb=%.3f | lift_vs_cfrpe=%.3f | cv=%.3f | "
        "sanity[scaled_lift=%s degen=%s] (v2: ARM_HEBBIAN_f002_UNSCALED dropped)"
    ) % (
        unigram_bpc, heb_f005_bpc, heb_f002_scaled_bpc,
        cfrpe_f005_bpc, cfrpe_f002_scaled_bpc,
        lift_vs_hebbian, lift_vs_cfrpe,
        combined_cv if math.isfinite(combined_cv) else -1.0,
        str(heb_f002_scaled_lift), str(degen_flag),
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "lift_combined_vs_hebbian": round(lift_vs_hebbian, 4),
        "lift_combined_vs_cfrpe": round(lift_vs_cfrpe, 4),
        "heb_f005_bpc": round(heb_f005_bpc, 4),
        "heb_f002_scaled_bpc": round(heb_f002_scaled_bpc, 4),
        "cfrpe_f005_bpc": round(cfrpe_f005_bpc, 4),
        "cfrpe_f002_scaled_bpc": round(cfrpe_f002_scaled_bpc, 4),
        "degen_flag": bool(degen_flag),
        "sanity_heb_f002_scaled_lift": bool(heb_f002_scaled_lift),
        "vocab_entropy_bits": round(vocab_entropy, 4),
        "n_seeds": len(units),
        "hard_pass_super_additive_bar": HARD_PASS_SUPER_ADDITIVE_LIFT,
        "hard_pass_additive_bar": HARD_PASS_ADDITIVE_LIFT_OVER_CFRPE,
        "middle_band_lower": MIDDLE_BAND_LOWER,
        "hard_fail_bar": HARD_FAIL_THRESHOLD,
        "amplitude_scale_f002": round(AMPLITUDE_SCALE_f002, 6),
        "amplitude_scale_f005": round(AMPLITUDE_SCALE_f005, 6),
        "fair_harness_hebbian_baseline_bpc": BASELINE_HEBBIAN_BPC,
        "rescue_note": "v2 rescue: ARM_HEBBIAN_f002_UNSCALED dropped; timeout 900->3600s",
        "honest_scope": (
            "cf-RPE x amplitude-correct sparse-bipolar at f=0.02. "
            "N_DIM=8192 N_TRAIN=100k text8 V=4000. "
            "PRIMARY: ARM_CFRPE_f002_AMPLITUDE_SCALED vs ARM_CFRPE_f005_UNSCALED. "
            "HARD_PASS_SUPER_ADDITIVE if lift_vs_hebbian >= %.2f; "
            "HARD_PASS_ADDITIVE if lift_vs_cfrpe >= %.2f; "
            "MIDDLE_BAND if lift_vs_cfrpe in [%.2f, %.2f); "
            "HARD_FAIL if lift_vs_cfrpe <= %.2f." % (
                HARD_PASS_SUPER_ADDITIVE_LIFT, HARD_PASS_ADDITIVE_LIFT_OVER_CFRPE,
                MIDDLE_BAND_LOWER, HARD_PASS_ADDITIVE_LIFT_OVER_CFRPE, HARD_FAIL_THRESHOLD)),
        "routing_note": (
            "Routed to overnight_queue (GPU) per Fix #22: N_DIM=8192 >= threshold. "
            "CPU path available as fallback. Source cell: "
            "exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py"),
        "cites": [
            "preregs/2026-06-24_substrate_cfrpe_x_amplitude_correct_f002_LM_v2.md",
            "preregs/2026-06-23_substrate_cfrpe_x_amplitude_correct_f002_LM_v1.md",
            "experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py",
            "notes/substrate_viability_shotgun_LIVE_DEAD_map_2026-06-23.md",
        ],
    }

    if combined_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_CFRPE_f002_AMPLITUDE_SCALED all seeds failed. %s" % arm_summary,
                detail)

    if degen_flag:
        return ("READOUT_DEGENERATE",
                "READOUT_DEGENERATE: combined arm raw_bpc near vocab-entropy. %s" % arm_summary,
                detail)

    if math.isfinite(combined_cv) and combined_cv > CV_MAX:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_HIGH_CV: cv=%.3f > %.2f. lift_vs_cfrpe=%.3f. %s" % (
                    combined_cv, CV_MAX, lift_vs_cfrpe, arm_summary)),
                detail)

    if lift_vs_hebbian >= HARD_PASS_SUPER_ADDITIVE_LIFT:
        verdict = "HARD_PASS"
        msg = (
            "HARD_PASS SUPER_ADDITIVE: lift_vs_hebbian=%.3f >= %.2f bits. "
            "lift_vs_cfrpe=%.3f. cf-RPE + amplitude-correct f=0.02 compose "
            "super-additively: cleaner token geometry at f=0.02 enables cf-RPE "
            "to exceed the sum of individual contributions. %s" % (
                lift_vs_hebbian, HARD_PASS_SUPER_ADDITIVE_LIFT, lift_vs_cfrpe, arm_summary))
    elif lift_vs_cfrpe >= HARD_PASS_ADDITIVE_LIFT_OVER_CFRPE:
        verdict = "HARD_PASS"
        msg = (
            "HARD_PASS ADDITIVE: lift_vs_cfrpe=%.3f >= %.2f bits. "
            "Amplitude-correct f=0.02 adds over cf-RPE alone. Knobs compose. "
            "lift_vs_hebbian=%.3f. %s" % (
                lift_vs_cfrpe, HARD_PASS_ADDITIVE_LIFT_OVER_CFRPE, lift_vs_hebbian, arm_summary))
    elif lift_vs_cfrpe >= MIDDLE_BAND_LOWER:
        verdict = "MIDDLE_BAND"
        msg = (
            "MIDDLE_BAND: lift_vs_cfrpe=%.3f in [%.2f, %.2f). "
            "Amplitude-correct f=0.02 provides marginal gain over cf-RPE; "
            "below HARD_PASS_ADDITIVE bar. %s" % (
                lift_vs_cfrpe, MIDDLE_BAND_LOWER, HARD_PASS_ADDITIVE_LIFT_OVER_CFRPE, arm_summary))
    else:
        verdict = "HARD_FAIL"
        msg = (
            "HARD_FAIL: lift_vs_cfrpe=%.3f <= %.2f bits. "
            "cf-RPE + amplitude-correct f=0.02 does NOT compose over cf-RPE alone at N=8192. "
            "cf-RPE may saturate available LM signal; lower-f topology not exploitable. %s" % (
                lift_vs_cfrpe, HARD_FAIL_THRESHOLD, arm_summary))

    return (verdict, msg, detail)


# ============================================================================
# Main loop with per-seed checkpoint
# ============================================================================

print("[config] anchor=%s N_DIM=%d mode=%s seeds=%s device=%s" % (
    ANCHOR_NAME, N_DIM, RUN_MODE, SEEDS, DEVICE), flush=True)
print("[config] F_BASELINE=%.3f F_LOW=%.3f AMP_SCALE_f002=%.4f" % (
    F_BASELINE, F_LOW, AMPLITUDE_SCALE_f002), flush=True)
print("[config] v2 rescue: 5 arms (ARM_HEBBIAN_f002_UNSCALED dropped); timeout=3600s", flush=True)

if DEVICE.type == "cuda":
    print("[gpu] %s" % torch.cuda.get_device_name(0), flush=True)
else:
    print("[device] CPU (no CUDA; running on CPU)", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
done_seeds: List[int] = []
remaining_seeds = SEEDS[:]
try:
    done_seeds, remaining_seeds = _resumable_seeds(SEEDS, out_dir,
                                                    run_config={"run_mode": RUN_MODE})
    print("[ckpt] %d done, %d remaining: %s" % (len(done_seeds), len(remaining_seeds),
                                                  remaining_seeds), flush=True)
except Exception as e:
    print("[ckpt] resumable_seeds failed (%s); running all seeds" % e, flush=True)
    remaining_seeds = SEEDS[:]

for seed in remaining_seeds:
    print("\n[run] seed=%d starting..." % seed, flush=True)
    result = run_unit(seed)
    write_partial(out_dir, seed, result)
    print("[ckpt] seed=%d partial written" % seed, flush=True)

per_seed = aggregate_partials(out_dir, SEEDS)
all_units = list(per_seed.values())

verdict, verdict_msg, detail = compute_verdict(all_units)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

if DEVICE.type == "cuda":
    peak_gb = torch.cuda.max_memory_allocated(0) / 1e9
    print("[gpu] peak memory %.3f GB" % peak_gb, flush=True)
    assert peak_gb > 0.001, "GPU peak memory check: should be > 0.001 GB (GPU not used?)"

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "F_BASELINE": F_BASELINE,
    "F_LOW": F_LOW,
    "AMPLITUDE_SCALE_f002": round(AMPLITUDE_SCALE_f002, 6),
    "AMPLITUDE_SCALE_f005": round(AMPLITUDE_SCALE_f005, 6),
    "CFRPE_LR": CFRPE_LR,
    "N_STEPS": N_STEPS,
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
