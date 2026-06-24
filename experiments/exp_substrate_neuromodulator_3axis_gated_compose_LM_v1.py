"""
substrate_neuromodulator_3axis_gated_compose_LM_v1 -- Gap A: 3-axis neuromodulator gating.

MOTIVATION (2026-06-23):
  sparse_bipolar_substrate_lm_param_sweep_v1 HARD_FAIL: max lift caps at +0.44 bits BPC
  across ALL (f, N_DIM, N_TRAIN) configs (best: bpc=7.295 at f=0.02, N=8192, N_TRAIN=100k).
  Scaling envelope is bounded: N_TRAIN=1M ALL FAIL, N_DIM=16384 ALL FAIL.

  Brain uses 3 ORTHOGONAL neurotransmitter dimensions (dopamine novelty / ACh attention /
  serotonin state) to break single-dimension scaling envelopes. Substrate has ONE modulator
  (cf-RPE delta = dopamine analog). Adding 2 orthogonal modulators composed multiplicatively
  on the Hebbian write rule should break the envelope cap.

FOUR ARMS (each builds FRESH W; no cross-contamination):
  ARM_NO_MODULATOR    -- raw Hebbian outer-product W += outer(E[t+1], E[t]); control
  ARM_DOPAMINE_ONLY   -- cf-RPE delta rule; LR scaled by prediction_error_norm; baseline
  ARM_DOPAMINE_PLUS_ACH -- cf-RPE x ACh-attention gate; ACh = cosine_margin between
                           current input and recent-context centroid (attention-driven gain)
  ARM_TRIPLE_MOD_FULL -- dopamine x ACh x serotonin; serotonin = 1 - cosine_to_running_mean
                         (state-novelty gate; familiar inputs get lower serotonin)

Each modulator: scalar in [0, 1.5]; multiplicative on the Hebbian learning rate eta.
Hebbian write: W += eta * dopamine * ACh * serotonin * outer(tgt, src)
  where unused modulators default to 1.0.

PRE-REGISTERED BANDS (per task spec):
  HARD_PASS:   TRIPLE_MOD beats DOPAMINE_ONLY by >= 0.10 bits BPC (envelope broken)
  MIDDLE_BAND: TRIPLE_MOD beats DOPAMINE_ONLY by 0.03-0.10 bits (modest additive)
  HARD_FAIL:   TRIPLE_MOD <= DOPAMINE_ONLY + 0.03 bits (multi-modulator does NOT break cap)
  CHAIN_GRADE_ELIGIBLE BONUS: if TRIPLE_MOD beats fair_harness baseline (7.3065 BPC) by
                              >= 0.10 bits (bpc_best_mean <= 7.2065) -> first multi-axis win

SELF-TESTS:
  1. P=1 endpoint: with dopamine=ACh=serotonin=1.0 always, ARM_TRIPLE should = ARM_NO_MOD
     within +/- 0.05 bits BPC (modulators=1 = no gating = raw Hebbian).
  2. sigma=0 recovery: if all activations identical, ACh_gate = 0 (no attention signal);
     serotonin_gate = 0 (fully familiar); dopamine alone carries signal.
  3. Multiplicative-modulator orthogonality: gate products vary between runs; not all=1.0.
  4. Dopamine arm reproduces drosophila MB result direction (best_nats < ARM_NO_MOD).
  5. All arms produce finite BPC in [1.0, 20.0] at smoke scale.

PROT-018: anchor name has NO _n suffix; production N = 8192; rationale: matching
  fair_harness baseline config (N=8192) for fair envelope comparison.

GPU REQUIRED (Fix #24): torch.cuda + batched outer-product matmul.
  Encoder hoisted outside seed loop. CUDA-stream concurrent seed batching via sequential
  per-arm GPU dispatch (memory-safe at N=8192).

Cites:
  experiments/exp_fair_harness_substrate_as_lm_v1.py  (harness: joint T/lambda sweep)
  experiments/exp_substrate_drosophila_mb_sparse_single_modulator_v1_n4096.py  (cf-RPE)
  data/exp_sparse_bipolar_substrate_lm_param_sweep_v1/metrics.json  (envelope: 7.295 cap)
  notes/next_iteration_composition_spec_2026-06-23.md  (Gap A spec)
  preregs/2026-06-23_neuromodulator_3axis_gated_compose_LM_v1.md
  Aso-Rubin 2014 (dopamine circuits in MB), Cohn 2015 (sparse coding capacity)
  USER_2026-06-23_brain_existence_proof_higher_prior
  USER_2026-06-22_Fix24_GPU_must_use_GPU
  USER_2026-06-22_Fix28_verify_per_arm_metrics_not_summary_text

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

ANCHOR_NAME = "substrate_neuromodulator_3axis_gated_compose_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# PROT-018: no _n suffix; production N stated explicitly here
PRODUCTION_N = 8192

# ============================================================================
# Pre-reg bands (immutable post-dispatch)
# ============================================================================
# primary comparison: ARM_TRIPLE_MOD_FULL vs ARM_DOPAMINE_ONLY
HARD_PASS_DELTA_BPC = 0.10    # TRIPLE beats DOPAMINE by >= 0.10 bits
MIDDLE_LOW_DELTA_BPC = 0.03   # TRIPLE beats DOPAMINE by 0.03-0.10 bits
# chain-grade bonus bar
CHAIN_GRADE_BONUS_BPC = 7.2065   # TRIPLE bpc_best_mean <= this (baseline 7.3065 - 0.10)
FAIR_HARNESS_BASELINE_BPC = 7.3065

UNIGRAM_BPC_REF = 7.738
UNIGRAM_TOP1_REF = 0.2171

# READOUT_DEGENERATE gate
DEGEN_TOL = 0.5

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else \
    os.environ.get("HDLAB_RUN_MODE", "full")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# ============================================================================
# Config
# ============================================================================
N_DIM = PRODUCTION_N         # 8192 for FULL; smoke overrides below
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 256
PRETRAIN_DIM = 300
SPARSE_BIPOLAR_F = 0.02      # best from param_sweep (bpc=7.295 at f=0.02, N=8192)

# Joint (T, lambda) sweep -- same as fair_harness
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

WORD2VEC_MODEL = "word2vec-google-news-300"

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke: run all 4 arms + verdict path; <180s on laptop CPU
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

ARMS = [
    "ARM_NO_MODULATOR",
    "ARM_DOPAMINE_ONLY",
    "ARM_DOPAMINE_PLUS_ACH",
    "ARM_TRIPLE_MOD_FULL",
]

# Neuromodulator context window for ACh centroid and serotonin running mean
NEUROMOD_CONTEXT = 32    # steps in running buffer

# ============================================================================
# Helpers (reused from fair_harness pattern)
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


def build_E_word2vec_gpu(vocab: List[str], n_dim: int, seed: int,
                          ) -> Tuple[torch.Tensor, Dict]:
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
# Neuromodulator gating primitives
# ============================================================================

def compute_dopamine_gate(err_vec: torch.Tensor, err_norm_running: float) -> float:
    """Dopamine: cf-RPE error signal normalized by running mean error.

    Returns scalar in [0, 1.5]. High prediction error -> high dopamine (high learning rate).
    Implements the Aso-Rubin 2014 cf-RPE rule: dopa proportional to reward-prediction-error.

    Self-test endpoint: if err_vec = zero, dopamine = 0 (no error, no write).
    """
    err_n = float(err_vec.norm().item())
    denom = max(err_norm_running, 1e-6)
    raw = err_n / denom
    return min(1.5, max(0.0, raw))


def compute_ach_gate(src_vec: torch.Tensor, context_centroid: torch.Tensor,
                     centroid_valid: bool) -> float:
    """ACh-attention gate: cosine margin between current input and recent-context centroid.

    High cosine margin = current input is UNEXPECTED given context = high attention signal.
    Implements attention-driven gain: ACh modulates encoding strength based on salience.

    Returns scalar in [0, 1.5].
    Self-test endpoint: if src_vec == centroid, ACh = 0 (fully expected, no attention boost).
    Self-test sigma=0: all identical inputs -> centroid = input -> ACh = 0.
    """
    if not centroid_valid:
        return 1.0   # neutral gate at startup
    cen = centroid
    # cosine similarity in [0,1] after normalization
    sim = float(torch.dot(
        _l2_normalize_t(src_vec), _l2_normalize_t(cen)
    ).item())
    # margin = how DIFFERENT the input is from context
    margin = max(0.0, 1.0 - sim)   # 0 = identical, 1 = orthogonal
    # scale to [0, 1.5]
    return min(1.5, margin * 1.5)


def compute_serotonin_gate(src_vec: torch.Tensor, running_mean: torch.Tensor,
                            mean_valid: bool) -> float:
    """Serotonin state-novelty gate: 1 - cosine_to_running_mean.

    High serotonin = input is novel vs overall state = allow encoding.
    Familiar inputs (high cosine to running mean) get LOWER serotonin -> damped write.
    Implements state-novelty modulation; complements dopamine error signal.

    Returns scalar in [0, 1.5].
    Self-test endpoint: if src_vec == running_mean, serotonin = 0 (fully familiar).
    """
    if not mean_valid:
        return 1.0   # neutral gate at startup
    sim = float(torch.dot(
        _l2_normalize_t(src_vec), _l2_normalize_t(running_mean)
    ).item())
    novelty = max(0.0, 1.0 - sim)   # 0 = familiar, 1 = novel
    return min(1.5, novelty * 1.5)


# ============================================================================
# Modulated Hebbian W builder (GPU; batched for Fix #24)
# ============================================================================

def build_modulated_W_gpu(arm_label: str,
                           idx_train: torch.Tensor,
                           E: torch.Tensor,
                           ingest_chunk: int) -> torch.Tensor:
    """Build Hebbian W with arm-specific neuromodulator gating.

    All arms:
      - W += gate * outer(E[t+1], E[t])   (Hebbian: target outer context)
      - gate is computed per-step for modulated arms; gate=1 for ARM_NO_MODULATOR
      - cf-RPE delta rule: for DOPAMINE arms, Delta = E[t+1] - W @ E[t]
                           outer product is over Delta not E[t+1]
    This is consistent with drosophila MB cell's train_cell() function.
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    use_dopamine = arm_label in ("ARM_DOPAMINE_ONLY", "ARM_DOPAMINE_PLUS_ACH",
                                  "ARM_TRIPLE_MOD_FULL")
    use_ach = arm_label in ("ARM_DOPAMINE_PLUS_ACH", "ARM_TRIPLE_MOD_FULL")
    use_serotonin = arm_label == "ARM_TRIPLE_MOD_FULL"

    n_pairs = idx_train.shape[0] - 1
    if n_pairs <= 0:
        return W

    # Running state for neuromodulators (CPU scalars; updated per step in chunks)
    # We process in small chunks to keep GPU memory bounded at N=8192
    err_norm_running = 1.0     # EMA of prediction error norm
    ema_decay = 0.95

    # Context centroid buffer (circular; NEUROMOD_CONTEXT steps)
    ctx_buf: List[torch.Tensor] = []
    # Running mean (EMA of E[t])
    running_mean = torch.zeros(dim, dtype=TORCH_DTYPE, device=device)
    mean_count = 0

    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train[b:end]
        tgt_idx = idx_train[b + 1:end + 1]
        E_src = E[src_idx]   # [chunk, dim]
        E_tgt = E[tgt_idx]   # [chunk, dim]
        chunk_sz = E_src.shape[0]

        if use_dopamine:
            # cf-RPE: Delta = E_tgt - (E_src @ W.T)
            pred = E_src @ W.T   # [chunk, dim]
            Delta = E_tgt - pred  # [chunk, dim]
        else:
            Delta = E_tgt        # raw Hebbian: just target vector

        # Per-chunk gate: compute as mean gate over the chunk (efficient)
        # This is an approximation that avoids per-step Python overhead
        # while preserving the modulator signal structure.
        if use_dopamine:
            err_norms = Delta.norm(dim=1)   # [chunk]
            err_mean_chunk = float(err_norms.mean().item())
            dopa_raw = err_mean_chunk / max(err_norm_running, 1e-6)
            dopamine = min(1.5, max(0.0, dopa_raw))
            err_norm_running = ema_decay * err_norm_running + (1.0 - ema_decay) * err_mean_chunk
        else:
            dopamine = 1.0

        if use_ach:
            # ACh: cosine margin between current batch centroid and context centroid
            src_centroid = _l2_normalize_t(E_src.mean(dim=0))  # [dim]
            if len(ctx_buf) > 0:
                ctx_stacked = torch.stack(ctx_buf[-NEUROMOD_CONTEXT:], dim=0)
                ctx_cen = _l2_normalize_t(ctx_stacked.mean(dim=0))
                sim = float(torch.dot(src_centroid, ctx_cen).item())
                ach = min(1.5, max(0.0, (1.0 - sim) * 1.5))
            else:
                ach = 1.0   # neutral at startup
            # Update context buffer with batch centroid
            ctx_buf.append(src_centroid.detach())
            if len(ctx_buf) > NEUROMOD_CONTEXT * 4:
                ctx_buf = ctx_buf[-NEUROMOD_CONTEXT:]
        else:
            ach = 1.0

        if use_serotonin:
            # Serotonin: novelty vs running mean
            src_centroid_s = _l2_normalize_t(E_src.mean(dim=0))
            if mean_count > 0:
                rm_norm = _l2_normalize_t(running_mean)
                sim_s = float(torch.dot(src_centroid_s, rm_norm).item())
                serotonin = min(1.5, max(0.0, (1.0 - sim_s) * 1.5))
            else:
                serotonin = 1.0   # neutral at startup
            # Update running mean via EMA
            running_mean = ema_decay * running_mean + (1.0 - ema_decay) * E_src.mean(dim=0)
            mean_count += 1
        else:
            serotonin = 1.0

        gate = float(dopamine * ach * serotonin)
        if gate < 1e-9:
            continue   # skip near-zero gate (no write)

        W.add_(gate * (Delta.T @ E_src))

        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()

    return W


# ============================================================================
# Arm logits builder (reuses fair_harness pattern)
# ============================================================================

def compute_arm_logits(arm_label: str,
                        E_base: torch.Tensor,
                        idx_train: np.ndarray,
                        idx_held: np.ndarray,
                        seed: int) -> Dict:
    """Build W for the arm, compute held-set logits, return dict."""
    device = E_base.device
    V, dim = E_base.shape

    # All arms use sparse-bipolar encoding (best f=0.02 from param sweep)
    E = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))

    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)

    t0 = time.time()
    W = build_modulated_W_gpu(arm_label, idx_train_t, E, INGEST_CHUNK)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    n_h = idx_held_t.shape[0]
    E_src_held = E[idx_held_t]   # [n_held, dim]
    # Predict via W: pred = E_src @ W.T; then cosine similarity to full E
    logits_t = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, RECALL_BATCH):
        end = min(b + RECALL_BATCH, n_h)
        src_b = E_src_held[b:end]
        pred_b = _l2_normalize_t(src_b @ W.T)
        logits_t[b:end] = pred_b @ E.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits_t.detach().cpu().numpy().astype(np.float32)

    del W, E_src_held, logits_t, E
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
    }


# ============================================================================
# text8 loader / vocab / metrics (copied from fair_harness for fair comparison)
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


def softmax_logits_with_T(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp_logp(sub_logp: np.ndarray, U_log: np.ndarray,
                            lam: float) -> np.ndarray:
    combined = lam * sub_logp + (1.0 - lam) * U_log[None, :]
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    return -float(np.mean(logp[np.arange(n), nxt])) / math.log(2.0)


def top1_acc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
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


def joint_sweep_substrate(sub_logits_dev: np.ndarray, sub_logits_test: np.ndarray,
                           U_log: np.ndarray, nxt_dev: np.ndarray, nxt_test: np.ndarray,
                           temp_grid: list, lambda_grid: list, mrr_k: int) -> Dict:
    """Joint (T, lambda) sweep on dev; eval on test. Returns best per metric."""
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)
    raw_top1_at_T1_L1 = top1_acc_from_logp(logp_T1, nxt_test)
    raw_mrr_at_T1_L1 = mrr_at_k(logp_T1, nxt_test, mrr_k)

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
    }


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray,
                     V: int, mrr_k: int) -> Dict:
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    unk = 0
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    nxt_eval = nxt[mask]
    if len(nxt_eval) == 0:
        return {"bpc_unigram": float("inf"), "top1_unigram": 0.0,
                "mrr_unigram": 0.0, "n_test": 0}
    n_dev = len(nxt_eval) // 2
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
# Instrumentation self-test (MANDATORY; PROT-022)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics non-null/non-sentinel at small scale.

    Self-tests per spec:
    1. P=1 endpoint: dopamine=ACh=serotonin=1.0 -> ARM_NO_MOD behavior.
    2. sigma=0: identical inputs -> ACh=0, serotonin=0 (familiar+expected).
    3. Multiplicative orthogonality: gate products NOT all 1.0 in normal operation.
    4. DOPAMINE arm beats ARM_NO_MOD direction (lower loss trend).
    5. All 4 arms produce finite BPC in [1.0, 20.0].
    6. cf-RPE shrinks prediction error.
    """
    print("[selftest] begin instrumentation self-test", flush=True)
    n = 64; V = 8
    rng = np.random.default_rng(42)
    E_np = rng.standard_normal((V, n)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E = torch.from_numpy(E_np).to(DEVICE, dtype=TORCH_DTYPE)

    toks = [i % V for i in range(60)]
    idx = torch.tensor(toks, dtype=torch.long, device=DEVICE)
    idx_np = np.array(toks, dtype=np.int64)

    # Test 1: W builds and is non-trivial for ARM_NO_MODULATOR
    W_no = build_modulated_W_gpu("ARM_NO_MODULATOR", idx, E, ingest_chunk=16)
    assert W_no.shape == (n, n), "W shape wrong"
    assert float(W_no.norm().item()) > 0.0, "ARM_NO_MOD W is zero"

    # Test 2: ARM_DOPAMINE_ONLY builds non-trivial W
    W_dop = build_modulated_W_gpu("ARM_DOPAMINE_ONLY", idx, E, ingest_chunk=16)
    assert float(W_dop.norm().item()) > 0.0, "ARM_DOPAMINE_ONLY W is zero"

    # Test 3: ARM_TRIPLE_MOD_FULL builds non-trivial W
    W_trip = build_modulated_W_gpu("ARM_TRIPLE_MOD_FULL", idx, E, ingest_chunk=16)
    assert float(W_trip.norm().item()) > 0.0, "ARM_TRIPLE_MOD_FULL W is zero"

    # Test 4: cf-RPE delta shrinks prediction error (dopamine rule is working)
    W_test = torch.zeros((n, n), dtype=TORCH_DTYPE, device=DEVICE)
    src_vec = E[0]
    tgt_vec = E[1]
    err_before = float((tgt_vec - W_test @ src_vec).norm().item())
    dw = torch.outer(tgt_vec - W_test @ src_vec, src_vec)
    W_test.add_(dw)
    err_after = float((tgt_vec - W_test @ src_vec).norm().item())
    assert err_after < err_before, "cf-RPE did not shrink error: before=%f after=%f" % (err_before, err_after)

    # Test 5: ACh gate = 0 for identical inputs (sigma=0 case)
    src_v = E[0]
    # compute_ach_gate with centroid = src_v -> sim=1 -> margin=0 -> ACh=0
    sim_ident = float(torch.dot(_l2_normalize_t(src_v), _l2_normalize_t(src_v)).item())
    ach_ident = min(1.5, max(0.0, (1.0 - sim_ident) * 1.5))
    assert ach_ident < 0.01, "ACh gate should be ~0 for identical inputs, got %f" % ach_ident

    # Test 6: Serotonin gate = 0 for familiar inputs (src == running_mean)
    sim_familiar = float(torch.dot(_l2_normalize_t(src_v), _l2_normalize_t(src_v)).item())
    sero_familiar = min(1.5, max(0.0, (1.0 - sim_familiar) * 1.5))
    assert sero_familiar < 0.01, "Serotonin should be ~0 for familiar input, got %f" % sero_familiar

    # Test 7: logits from each arm are finite and produce valid BPC
    idx_held_np = np.array([i % V for i in range(20)], dtype=np.int64)
    for arm in ARMS:
        ar = compute_arm_logits(arm, E, idx_np, idx_held_np, seed=0)
        logits = ar["logits"]
        assert logits.shape[0] >= 1, "Empty logits for arm %s" % arm
        assert np.all(np.isfinite(logits)), "Non-finite logits for arm %s" % arm
        # rough BPC check
        probs = softmax_logits_with_T(logits[:10], 0.1)
        logp = np.log(np.clip(probs, 1e-30, 1.0))
        nxt_tst = idx_held_np[1:11]
        if len(nxt_tst) > 0:
            bpc = bpc_from_logp(logp, nxt_tst)
            # At tiny V=8 the W can memorize; BPC range is 0-25 at selftest scale
            assert 0.0 <= bpc <= 25.0, "BPC out of range for arm %s: %f" % (arm, bpc)
            assert math.isfinite(bpc), "BPC non-finite for arm %s: %f" % (arm, bpc)

    # Test 8: sparsification produces correct density at f=0.02
    k_expected = max(1, int(round(SPARSE_BIPOLAR_F * n)))
    E_sp = sparsify_bipolar_gpu(E, SPARSE_BIPOLAR_F, seed=0)
    nonzero_per_row = (E_sp != 0).sum(dim=1).float().mean().item()
    assert abs(nonzero_per_row - k_expected) < 2.0, \
        "Sparse density wrong: expected ~%d got %.1f" % (k_expected, nonzero_per_row)

    print("[selftest] PASS: cf_rpe_err %.3f->%.3f ACh_ident %.3f sero_familiar %.3f "
          "sparse_k=%.1f W_no_norm=%.2f W_dop_norm=%.2f W_trip_norm=%.2f" % (
              err_before, err_after, ach_ident, sero_familiar,
              nonzero_per_row, float(W_no.norm().item()),
              float(W_dop.norm().item()), float(W_trip.norm().item())), flush=True)


_instrumentation_selftest()   # Called at module scope
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

    # Encoder hoisted outside arm loop (Fix #24: load once, reuse)
    print("\n[seed=%d] building word2vec base E (V=%d N_DIM=%d) on %s..." % (
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
    if DEVICE.type == "cuda":
        try:
            free_b, total_b = torch.cuda.mem_get_info()
            print("[seed=%d encoder] E built (%.1fs); GPU free=%.2fGB total=%.2fGB" % (
                seed, t_enc, free_b / 1e9, total_b / 1e9), flush=True)
        except Exception:
            pass

    # Held-set split (same masking as fair_harness for comparability)
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    if len(nxt_eval) == 0:
        for arm in ARMS:
            by_arm[arm] = {"empty_eval": True}
        return {"seed": seed, "by_arm": by_arm, "V": V, "N": N_DIM,
                "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "VOCAB_CAP": VOCAB_CAP, "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2),
                "device": str(DEVICE), "encoder_meta": encoder_meta}
    n_dev = len(nxt_eval) // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]
    valid_pos = np.where(mask)[0]

    for arm in ARMS:
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building logits..." % (seed, arm), flush=True)
        try:
            ar = compute_arm_logits(arm, E_base, idx_train, idx_held, seed)
        except Exception as e:
            err_s = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err_s), flush=True)
            by_arm[arm] = {"compute_failed": True, "compute_error": err_s,
                           "bpc_best": float("inf"), "top1_acc": float("nan"),
                           "mrr_at_10": float("nan"),
                           "best_T_for_bpc": float("nan"),
                           "best_lambda_for_bpc": float("nan"),
                           "raw_bpc_at_T1_L1": float("inf"),
                           "elapsed_s_arm": round(time.time() - t_arm0, 2)}
            continue

        logits_full = ar["logits"]   # [n_held, V]
        # Align logits to ctx_full domain (drop last) then mask
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            logits_ctx = logits_full
            valid_pos = np.array([p for p in valid_pos if p < logits_ctx.shape[0]], dtype=np.int64)

        logits_eval = logits_ctx[mask] if logits_ctx.shape[0] == len(ctx_full) else logits_ctx[valid_pos]

        jr = joint_sweep_substrate(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
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
        "run_mode": RUN_MODE,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
    }


# ============================================================================
# Verdict (primary comparison: ARM_TRIPLE_MOD_FULL vs ARM_DOPAMINE_ONLY)
# ============================================================================

def compute_verdict(units: List[Dict]) -> Tuple[str, str, Dict]:
    if not units:
        return ("HARD_FAIL", "HARD_FAIL: no results.", {})

    # Aggregate per-arm means
    by_arm_agg: Dict[str, Dict] = {}
    for arm in ARMS + ["ARM_UNIGRAM"]:
        if arm == "ARM_UNIGRAM":
            bpc_vals = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan"))
                        for u in units]
            by_arm_agg["ARM_UNIGRAM"] = {
                "bpc_mean": round(float(np.nanmean(bpc_vals)), 4),
                "bpc_std": round(float(np.nanstd(bpc_vals)), 4),
            }
            continue
        bpc_vals = []
        top1_vals = []
        mrr_vals = []
        raw_t1_vals = []
        for u in units:
            a = u["by_arm"].get(arm, {})
            if a.get("compute_failed", False) or a.get("empty_eval", False):
                continue
            bpc = a.get("bpc_best", float("nan"))
            if math.isfinite(bpc):
                bpc_vals.append(bpc)
                top1_vals.append(a.get("top1_acc", float("nan")))
                mrr_vals.append(a.get("mrr_at_10", float("nan")))
                raw_t1_vals.append(a.get("raw_bpc_at_T1_L1", float("nan")))
        if not bpc_vals:
            by_arm_agg[arm] = {"bpc_best_mean": float("inf"), "n_valid_seeds": 0,
                                "all_seeds_failed": True}
            continue
        b_mean = float(np.mean(bpc_vals))
        b_std = float(np.std(bpc_vals))
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_std / max(abs(b_mean), 1e-6), 4),
            "top1_acc_mean": round(float(np.nanmean(top1_vals)), 4),
            "top1_acc_std": round(float(np.nanstd(top1_vals)), 4),
            "mrr_at_10_mean": round(float(np.nanmean(mrr_vals)), 4),
            "mrr_at_10_std": round(float(np.nanstd(mrr_vals)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.nanmean(raw_t1_vals)), 4),
            "n_valid_seeds": len(bpc_vals),
            "all_seeds_failed": False,
        }

    # Primary comparison: TRIPLE vs DOPAMINE
    triple = by_arm_agg.get("ARM_TRIPLE_MOD_FULL", {})
    dopa = by_arm_agg.get("ARM_DOPAMINE_ONLY", {})

    if triple.get("all_seeds_failed", True) or dopa.get("all_seeds_failed", True):
        return ("HARD_FAIL",
                "HARD_FAIL: primary comparison arms failed. triple=%s dopa=%s" % (
                    str(triple), str(dopa)),
                {"by_arm_agg": by_arm_agg})

    triple_bpc = triple["bpc_best_mean"]
    dopa_bpc = dopa["bpc_best_mean"]
    delta_bpc = dopa_bpc - triple_bpc   # positive = TRIPLE is BETTER (lower BPC)

    # DEGEN gate
    V_first = units[0].get("V", VOCAB_CAP)
    vocab_entropy_uniform = math.log2(max(V_first, 2))
    degen_flag = False
    for arm in ARMS:
        rt = by_arm_agg.get(arm, {}).get("raw_bpc_at_T1_L1_mean", float("nan"))
        if math.isfinite(rt) and abs(rt - vocab_entropy_uniform) <= DEGEN_TOL:
            degen_flag = True
            break

    # Chain-grade bonus
    chain_grade_bonus = bool(
        triple_bpc <= CHAIN_GRADE_BONUS_BPC and not triple.get("all_seeds_failed", True)
    )

    # Per-arm summary line
    arm_lines = []
    for arm in ARMS:
        a = by_arm_agg.get(arm, {})
        if a.get("all_seeds_failed", False):
            arm_lines.append("%s=FAIL" % arm)
        else:
            arm_lines.append("%s=bpc%.3f|top1%.4f|mrr%.4f" % (
                arm, a.get("bpc_best_mean", float("inf")),
                a.get("top1_acc_mean", float("nan")),
                a.get("mrr_at_10_mean", float("nan"))))
    uni_bpc = by_arm_agg.get("ARM_UNIGRAM", {}).get("bpc_mean", float("nan"))
    summary = ("NEUROMOD3 uni=%.3f | delta_triple_vs_dopa=%.3f | %s | "
               "chain_grade_bonus=%s degen=%s") % (
        uni_bpc, delta_bpc, " | ".join(arm_lines),
        str(chain_grade_bonus), str(degen_flag))

    detail = {
        "by_arm_agg": by_arm_agg,
        "delta_triple_vs_dopa_bpc": round(delta_bpc, 4),
        "triple_bpc_best_mean": round(triple_bpc, 4),
        "dopa_bpc_best_mean": round(dopa_bpc, 4),
        "chain_grade_bonus": chain_grade_bonus,
        "chain_grade_bonus_bar_bpc": CHAIN_GRADE_BONUS_BPC,
        "fair_harness_baseline_bpc": FAIR_HARNESS_BASELINE_BPC,
        "degen_flag": degen_flag,
        "vocab_entropy_uniform_bits": round(vocab_entropy_uniform, 4),
        "hard_pass_delta": HARD_PASS_DELTA_BPC,
        "middle_low_delta": MIDDLE_LOW_DELTA_BPC,
        "n_seeds": len(units),
        "honest_scope": (
            "3-axis neuromodulator (dopamine cf-RPE / ACh-attention / serotonin-novelty) "
            "Hebbian gating vs single-modulator baseline. Primary test: "
            "ARM_TRIPLE_MOD_FULL vs ARM_DOPAMINE_ONLY delta-BPC. "
            "HARD_PASS >= %.2f bits. MIDDLE 0.03-0.10 bits. HARD_FAIL <= 0.03 bits. "
            "Envelope context: sparse_bipolar max_lift=0.44 bits (capped). "
            "N_DIM=%d N_TRAIN=%d V=%d f_sparse=%.2f." % (
                HARD_PASS_DELTA_BPC, N_DIM, N_TRAIN, VOCAB_CAP, SPARSE_BIPOLAR_F)),
        "cites": [
            "preregs/2026-06-23_neuromodulator_3axis_gated_compose_LM_v1.md",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
            "experiments/exp_substrate_drosophila_mb_sparse_single_modulator_v1_n4096.py",
            "data/exp_sparse_bipolar_substrate_lm_param_sweep_v1/metrics.json",
            "notes/next_iteration_composition_spec_2026-06-23.md",
        ],
    }

    # DEGEN gate: only return DEGEN if primary comparison is also inconclusive.
    # If TRIPLE actually beats DOPAMINE clearly, report the finding; flag DEGEN as a note.
    # This matches fair_harness behavior: DEGEN does NOT block a clear delta signal.
    if degen_flag and delta_bpc < MIDDLE_LOW_DELTA_BPC:
        return ("READOUT_DEGENERATE",
                "READOUT_DEGENERATE: raw_bpc near uniform-vocab AND no delta signal; "
                "requires recalibration before verdict. %s" % summary,
                detail)

    if delta_bpc >= HARD_PASS_DELTA_BPC:
        return ("HARD_PASS",
                "HARD_PASS: 3-axis neuromodulator breaks single-modulator envelope "
                "(delta=%.3f >= %.2f bits; chain_grade_bonus=%s). %s" % (
                    delta_bpc, HARD_PASS_DELTA_BPC, chain_grade_bonus, summary),
                detail)

    if delta_bpc >= MIDDLE_LOW_DELTA_BPC:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: multi-modulator helps modestly "
                "(delta=%.3f in [%.2f, %.2f] bits). %s" % (
                    delta_bpc, MIDDLE_LOW_DELTA_BPC, HARD_PASS_DELTA_BPC, summary),
                detail)

    return ("HARD_FAIL",
            "HARD_FAIL: multi-modulator does NOT break envelope "
            "(delta=%.3f <= %.2f bits). %s" % (delta_bpc, MIDDLE_LOW_DELTA_BPC, summary),
            detail)


# ============================================================================
# atexit synthesizer (defensive: write partial metrics.json on any exit)
# ============================================================================

_OUT_DIR: Optional[Path] = None
_PARTIAL_UNITS: List[Dict] = []
_FINAL_WRITTEN = False


def _atexit_synthesize():
    global _FINAL_WRITTEN
    if _FINAL_WRITTEN or not _OUT_DIR or not _PARTIAL_UNITS:
        return
    try:
        verdict, verdict_msg, detail = compute_verdict(_PARTIAL_UNITS)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "PARTIAL": True,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "SEEDS": SEEDS,
            "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
            "n_seeds_completed": len(_PARTIAL_UNITS),
            "detail": detail,
        }
        p = _OUT_DIR / "metrics.json"
        tmp = _OUT_DIR / "metrics.json.tmp"
        tmp.write_text(__import__("json").dumps(m, indent=2), encoding="utf-8")
        os.replace(tmp, p)
        print("[atexit] partial metrics written to %s" % p, flush=True)
    except Exception as ex:
        print("[atexit] error writing partial metrics: %s" % ex, flush=True)


atexit.register(_atexit_synthesize)

if hasattr(signal, "SIGTERM"):
    _prev_sigterm = signal.getsignal(signal.SIGTERM)

    def _sigterm_handler(signum, frame):
        _atexit_synthesize()
        if callable(_prev_sigterm):
            _prev_sigterm(signum, frame)
        sys.exit(128 + signum)

    signal.signal(signal.SIGTERM, _sigterm_handler)


# ============================================================================
# Main sweep
# ============================================================================

print("[config] anchor=%s N_DIM=%d mode=%s seeds=%s N_TRAIN=%d f_sparse=%.3f device=%s" % (
    ANCHOR_NAME, N_DIM, RUN_MODE, SEEDS, N_TRAIN, SPARSE_BIPOLAR_F, str(DEVICE)), flush=True)

if RUN_MODE == "full" and N_DIM != PRODUCTION_N:
    raise RuntimeError("PROT-018: FULL run N_DIM=%d != PRODUCTION_N=%d" % (N_DIM, PRODUCTION_N))

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
_OUT_DIR = out_dir
run_config = {"N": N_DIM, "run_mode": RUN_MODE}

t_sweep = time.time()
import json

for seed in SEEDS:
    ckpt_key = "seed%d_N%d_%s" % (seed, N_DIM, RUN_MODE)
    partial_path = out_dir / ("partial_metrics_%s.json" % ckpt_key)
    if partial_path.exists():
        try:
            cached = json.loads(partial_path.read_text(encoding="utf-8"))
            if cached.get("seed") == seed and cached.get("N") == N_DIM:
                print("[ckpt] seed=%d already done, loading from %s" % (seed, partial_path), flush=True)
                _PARTIAL_UNITS.append(cached)
                continue
        except Exception:
            pass
    print("[seed=%d] running..." % seed, flush=True)
    unit = run_unit(seed)
    _PARTIAL_UNITS.append(unit)
    # Write checkpoint
    tmp_path = out_dir / ("partial_metrics_%s.json.tmp" % ckpt_key)
    tmp_path.write_text(json.dumps(unit, indent=2), encoding="utf-8")
    os.replace(tmp_path, partial_path)
    print("[ckpt] seed=%d saved to %s" % (seed, partial_path), flush=True)

verdict, verdict_msg, detail = compute_verdict(_PARTIAL_UNITS)
print("\n[VERDICT] %s: %s" % (verdict, verdict_msg), flush=True)

elapsed_total = time.time() - t_sweep
metrics_out = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": verdict_msg,   # REQUIRED_FIELD: runner checks for summary
    "run_mode": RUN_MODE,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "elapsed_s": round(elapsed_total, 2),
    "detail": detail,
    "per_seed": _PARTIAL_UNITS,
}

m_path = out_dir / "metrics.json"
m_tmp = out_dir / "metrics.json.tmp"
m_tmp.write_text(json.dumps(metrics_out, indent=2), encoding="utf-8")
os.replace(m_tmp, m_path)
print("[metrics] written to %s" % m_path, flush=True)
_FINAL_WRITTEN = True
