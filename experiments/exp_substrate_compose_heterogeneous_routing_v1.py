"""
substrate_compose_heterogeneous_routing_v1
-- Tests 3 brain-canonical HETEROGENEOUS-ROUTING composition architectures.

Per research drill ANCHOR 1 (notes/research_untested_composition_architectures_2x_drill_2026-06-24.md):
USER refused the "cf-RPE cap at +12%" framing. All composition tests so far used
SAME-W stacking (the broken architecture). This cell directly tests 3 brain-canonical
composition architectures the substrate hasn't tried.

Strategic context:
  A1 5-primitive joint compose HARD_FAIL_SUB_ADDITIVE (catastrophic 7.89)
  MH beta-sweep HARD_FAIL_STRUCTURAL (softening doesn't help)
  ALL composition tests so far use SAME-W stacking (the broken architecture)
  3 UNTESTED brain-canonical architectures may break the cap

Four arms (1 baseline + 3 heterogeneous-routing architectures):
  ARM_BASELINE_FAIR_HARNESS
      Sanity rail at fair_harness 7.3065 (provenance check)
  ARM_THETA_PHASE_TWO_W
      Two FULL-N_DIM W banks; alternate per-token phase routing:
          phase_0 (encoding): cf-RPE updates W_enc
          phase_1 (retrieval): STDP-asymmetric updates W_ret
      Readout: alpha * cosine(h, codebook @ W_enc.T) + (1-alpha) * cosine(h, codebook @ W_ret.T)
      Alpha grid-swept [0.3, 0.5, 0.7].
      Brain anchor: theta-gamma 2024 reviews -- encoding at trough, retrieval at peak.
  ARM_FREQ_ROUTED_K2
      Deterministic frequency-based routing:
          rank <= 100 (top-100 frequent) -> W_freq (cf-RPE, high LR)
          rank > 100 (rare)               -> W_rare (cf-RPE + STDP, lower LR, sparse-amp)
      Brain anchor: hippocampus vs cortex specialization; MaskMoE 2024 static
      frequency-routing for rare tokens.
  ARM_ORTHOG_SUBSPACE
      Gram-Schmidt orthogonal split of N_DIM into two 4096-dim subspaces.
      cf-RPE writes via subspace_1; STDP writes via subspace_2; both contribute
      to logits via P1.T h vs P2.T h projections.
      Brain anchor: V1 spatial-frequency vs V4 shape selectivity orthogonal axes;
      ORTHOG-SUBSPACE NeurIPS 2020 / O-LoRA 2024 / BiLoRA CVPR 2025.

PRE-REG HARD bands (per drill ANCHOR 1):
  Sanity rail: ARM_BASELINE_FAIR_HARNESS within +/-0.05 of 7.3065 (provenance)
  HARD_PASS_CAP_BROKEN: any of ARM_THETA / ARM_FREQ / ARM_ORTHOG BPC <= 6.95
                        (refutes cf-RPE cap; heterogeneous routing works)
  CHAIN_GRADE_BONUS:    best architecture BPC <= 6.80 (substantial gain over cf-RPE)
  MIDDLE_BAND:          best heterogeneous BPC in [6.95, 7.05] (partial signal)
  HARD_FAIL_DECISIVE:   all 3 architectures BPC >= 7.30 (cap structural at this regime)
  cv < 0.05 mandatory on best heterogeneous arm.

Discriminating-regime metrics (mandatory per drill C5):
  ARM_THETA_PHASE_TWO_W:
      enc_vs_ret_cosine: cosine similarity between mean(W_enc) and mean(W_ret)
                          (if > 0.95, banks collapsed to same content; routing fails)
      logit_enc_ret_corr: correlation between p_enc and p_ret per held query
  ARM_FREQ_ROUTED_K2:
      top1_acc_high_freq vs top1_acc_low_freq (must differ by >= 0.05)
      (uniform performance refutes routing hypothesis)
  ARM_ORTHOG_SUBSPACE:
      cross_subspace_cosine_corr: cosine between cf-RPE-gradient (subspace_1)
                                  and STDP-gradient (subspace_2) updates
      (correlation > 0.7 implies orthogonality failed)

CONFIG:
  N_DIM=8192, V=4000, text8 N_TRAIN=100k, 3 seeds, word2vec sparse-bipolar f=0.05
  Queue: local_cpu_queue (~45min wall per drill estimate; fits in 3600s timeout)
  LAMBDA_GRID excludes 0.0 (META C7)

CITES:
  notes/research_untested_composition_architectures_2x_drill_2026-06-24.md (ANCHOR 1)
  experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py (encoder + plasticity primitives)
  data/exp_fair_harness_substrate_as_lm_v1/metrics.json (sanity rail 7.3065)
  preregs/2026-06-24_substrate_compose_heterogeneous_routing_v1.md
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

ANCHOR_NAME = "substrate_compose_heterogeneous_routing_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only audit counter
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Pre-reg threshold bands
# ============================================================================
SANITY_RAIL_BASELINE_REF = 7.3065
SANITY_RAIL_TOLERANCE = 0.05

# Heterogeneous-routing verdict bands (per drill ANCHOR 1)
HARD_PASS_CAP_BROKEN_BPC = 6.95     # any het-routing arm BPC <= 6.95 -> cap refuted
CHAIN_GRADE_BONUS_BPC = 6.80        # best architecture BPC <= 6.80 -> chain-grade-eligible
MIDDLE_BAND_LOWER = 6.95
MIDDLE_BAND_UPPER = 7.05
HARD_FAIL_DECISIVE_FLOOR = 7.30     # all 3 het-routing arms >= 7.30 -> cap may be structural
CV_MAX = 0.05

# Discriminating-regime gates (per drill C5)
FREQ_ROUTED_DIFFERENTIAL_MIN = 0.05  # high-freq vs low-freq top1 must differ by >= 0.05
THETA_BANK_CORR_MAX = 0.95           # enc-vs-ret bank correlation must be < 0.95
ORTHOG_CROSS_CORR_MAX = 0.70         # cf-RPE-grad vs STDP-grad correlation must be < 0.70

# ============================================================================
# Primitive knob parameters (frozen from chain-grade source cells)
# ============================================================================
CFRPE_LR = 0.5
STDP_WEIGHT = 0.5
INGEST_BATCH = 64
N_STEPS_PER_SEED = 1000

# Theta-phase alpha grid (per drill L3.1)
THETA_ALPHA_GRID = [0.3, 0.5, 0.7]

# Frequency routing threshold (per drill L3.2)
FREQ_ROUTE_RANK = 100
FREQ_LR_HIGH = 0.5
FREQ_LR_RARE = 0.2

# Orthogonal subspace LR
ORTHOG_LR = 0.5

# Eval grids
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Encoder
SPARSE_BIPOLAR_F = 0.05
WORD2VEC_MODEL = "word2vec-google-news-300"
PRETRAIN_DIM = 300

ARMS = [
    "ARM_BASELINE_FAIR_HARNESS",
    "ARM_THETA_PHASE_TWO_W",
    "ARM_FREQ_ROUTED_K2",
    "ARM_ORTHOG_SUBSPACE",
]

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
N_DIM = 8192
VOCAB_CAP = 4000
RECALL_BATCH = 256
INGEST_CHUNK = 4096

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
    N_STEPS = N_STEPS_PER_SEED
else:
    # Smoke: clean synthetic data + small config; goal <180s on CPU.
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 1024
    N_STEPS = 80
    RECALL_BATCH = 128
    INGEST_CHUNK = 512

N_DIM_HALF = N_DIM // 2  # for orthogonal subspace split

CONFIG_VERSION = (
    "%s; encoder=word2vec_sparse_bipolar_f%.3f; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s temps=%s lambdas=%s "
    "cfrpe_lr=%.3f stdp_w=%.3f n_steps=%d batch=%d "
    "theta_alphas=%s freq_rank=%d freq_lr_high=%.3f freq_lr_rare=%.3f "
    "orthog_lr=%.3f device=%s"
) % (
    ANCHOR_NAME, SPARSE_BIPOLAR_F, N_DIM, N_TRAIN, N_HELD, VOCAB_CAP,
    ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID, CFRPE_LR, STDP_WEIGHT,
    N_STEPS, INGEST_BATCH, THETA_ALPHA_GRID, FREQ_ROUTE_RANK,
    FREQ_LR_HIGH, FREQ_LR_RARE, ORTHOG_LR, str(DEVICE),
)


# ============================================================================
# Corpus utilities (mirrors fair_harness cell)
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


def vocab_frequency_ranks(idx_train: np.ndarray, V: int) -> np.ndarray:
    """Returns rank[v] = position of token v in descending-frequency order (0-indexed).

    Token-rank 0 is the most-frequent token in idx_train.
    Used by ARM_FREQ_ROUTED_K2 for deterministic routing.
    """
    counts = np.zeros(V, dtype=np.int64)
    np.add.at(counts, idx_train, 1)
    order = np.argsort(-counts)  # descending
    ranks = np.empty(V, dtype=np.int64)
    ranks[order] = np.arange(V)
    return ranks


# ============================================================================
# Encoder utilities (identical to fair_harness)
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
    """Clean synthetic encoder for smoke (memory rule)."""
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
# Plasticity primitives (mirrors fair_harness; reused for baseline)
# ============================================================================

def build_W_hebbian_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                          ingest_chunk: int) -> torch.Tensor:
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        src_idx = idx_train_t[b:end]
        tgt_idx = idx_train_t[b + 1:end + 1]
        E_src = E[src_idx]
        E_tgt = E[tgt_idx]
        W.add_(E_tgt.T @ E_src)
        if device.type == "cuda" and (b // ingest_chunk) % 16 == 0:
            torch.cuda.synchronize()
    return W


def build_logits_hebbian_baseline_gpu(E_full: torch.Tensor,
                                         idx_train_t: torch.Tensor,
                                         idx_held_t: torch.Tensor,
                                         recall_batch: int,
                                         ingest_chunk: int) -> Dict:
    """ARM_BASELINE_FAIR_HARNESS: single-bank Hebbian (sanity rail)."""
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    t0 = time.time()
    W = build_W_hebbian_gpu(E_full, idx_train_t, ingest_chunk)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    pred = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred[b:end] = _l2_normalize_t(ctx_b @ W.T)
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        logits[b:end] = pred[b:end] @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W, pred, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np, "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
            "discriminating": {}}


# ============================================================================
# ARM_THETA_PHASE_TWO_W -- two FULL-N_DIM W banks; alternating-phase routing
# ============================================================================

def build_logits_theta_phase_two_w_gpu(E_full: torch.Tensor,
                                          idx_train_t: torch.Tensor,
                                          idx_held_t: torch.Tensor,
                                          n_steps: int, batch: int, lr: float,
                                          stdp_w: float,
                                          seed: int, arm_idx: int,
                                          recall_batch: int) -> Dict:
    """Theta-phase routing: two banks W_enc, W_ret at full N_DIM.

    phase = step % 2:
      phase==0 (encoding): W_enc receives cf-RPE delta update.
                            dW_enc = (Nxt - Ctx @ W_enc.T)^T @ Ctx / batch
      phase==1 (retrieval): W_ret receives STDP-asymmetric update.
                             dW_ret = stdp_w * (Nxt.T @ Ctx - Ctx.T @ Nxt) / batch
                             (NB: pure STDP antisymmetric; no cf-RPE here.)

    Readout (per alpha in THETA_ALPHA_GRID):
      pred_enc = L2(ctx @ W_enc.T)
      pred_ret = L2(ctx @ W_ret.T)
      logits = alpha * (pred_enc @ E.T) + (1-alpha) * (pred_ret @ E.T)
      Return the BEST-alpha logits (by joint_sweep BPC on dev).

    Returns logits + discriminating metrics:
      - enc_vs_ret_corr: cosine between vec(W_enc) and vec(W_ret); > 0.95 fails routing
      - logit_enc_ret_corr: per-query Pearson corr between pred_enc-logits and pred_ret-logits
      - best_alpha
    """
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    t0 = time.time()
    W_enc = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    W_ret = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return {"logits": np.zeros((n_h, V), dtype=np.float32),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "discriminating": {}}

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    n_phase0 = 0
    n_phase1 = 0
    for step in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E_full[idx_train_t[st]]
        Nxt = E_full[idx_train_t[st + 1]]
        phase = step % 2
        if phase == 0:
            # Encoding phase: cf-RPE delta on W_enc
            error = Nxt - Ctx @ W_enc.T
            dW = (error.T @ Ctx) / float(batch)
            W_enc = W_enc + lr * dW
            n_phase0 += 1
        else:
            # Retrieval phase: STDP antisymmetric on W_ret
            dW = (Nxt.T @ Ctx - Ctx.T @ Nxt) / float(batch)
            W_ret = W_ret + lr * stdp_w * dW
            n_phase1 += 1

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    # Discriminating: bank correlation (must be < 0.95 to confirm routing)
    enc_flat = W_enc.flatten()
    ret_flat = W_ret.flatten()
    enc_norm = enc_flat / (enc_flat.norm() + 1e-12)
    ret_norm = ret_flat / (ret_flat.norm() + 1e-12)
    enc_vs_ret_corr = float((enc_norm * ret_norm).sum().item())

    # Recall (over all alpha grid; return BEST-alpha logits)
    t0 = time.time()
    pred_enc = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    pred_ret = torch.zeros((n_h, dim), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred_enc[b:end] = _l2_normalize_t(ctx_b @ W_enc.T)
        pred_ret[b:end] = _l2_normalize_t(ctx_b @ W_ret.T)
    # Logits per bank
    logits_enc = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    logits_ret = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        logits_enc[b:end] = pred_enc[b:end] @ E_full.T
        logits_ret[b:end] = pred_ret[b:end] @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    # Per-query Pearson correlation between enc-logits and ret-logits (DISCRIMINATING)
    le = logits_enc.detach().cpu().numpy().astype(np.float32)
    lr_np = logits_ret.detach().cpu().numpy().astype(np.float32)
    if le.shape[0] > 0:
        le_c = le - le.mean(axis=1, keepdims=True)
        lr_c = lr_np - lr_np.mean(axis=1, keepdims=True)
        num = (le_c * lr_c).sum(axis=1)
        den = (np.linalg.norm(le_c, axis=1) * np.linalg.norm(lr_c, axis=1) + 1e-12)
        per_q_corr = num / den
        logit_enc_ret_corr = float(np.mean(per_q_corr))
    else:
        logit_enc_ret_corr = float("nan")

    # Return STACK of alpha-mixed logits; caller selects best via joint_sweep.
    # We return a [len(alpha_grid), n_h, V] stack.
    alpha_stack = np.stack(
        [(a * le) + ((1.0 - a) * lr_np) for a in THETA_ALPHA_GRID],
        axis=0,
    ).astype(np.float32)

    del W_enc, W_ret, pred_enc, pred_ret, logits_enc, logits_ret
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits_alpha_stack": alpha_stack,
        "alpha_grid": list(THETA_ALPHA_GRID),
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": {
            "enc_vs_ret_bank_corr": round(enc_vs_ret_corr, 4),
            "logit_enc_ret_corr_mean": round(logit_enc_ret_corr, 4),
            "n_phase0_steps": int(n_phase0),
            "n_phase1_steps": int(n_phase1),
        },
    }


# ============================================================================
# ARM_FREQ_ROUTED_K2 -- deterministic frequency-based routing
# ============================================================================

def build_logits_freq_routed_k2_gpu(E_full: torch.Tensor,
                                      idx_train_t: torch.Tensor,
                                      idx_held_t: torch.Tensor,
                                      ranks_np: np.ndarray,
                                      n_steps: int, batch: int,
                                      lr_high: float, lr_rare: float,
                                      stdp_w: float, freq_threshold: int,
                                      seed: int, arm_idx: int,
                                      recall_batch: int) -> Dict:
    """Frequency-routed K=2: top-N most-frequent tokens use W_freq (cf-RPE high LR);
    rank > N tokens use W_rare (cf-RPE + STDP, lower LR).

    Routing: at each training step, partition the batch by tgt-token rank.
      tgt_rank <= freq_threshold -> W_freq receives cf-RPE update.
      tgt_rank > freq_threshold  -> W_rare receives cf-RPE + STDP update.

    Readout: per held query, predict via BOTH banks, then route per
    predicted-top1-token rank:
      we score with both W_freq and W_rare; pick which logit to use per VOCAB
      entry based on that vocab entry's rank (V_high vs V_rare partition).

    Discriminating: top1 stratified by held-token rank.
    """
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    # Build routing masks (CPU side; small arrays)
    is_high_freq = (ranks_np < freq_threshold)  # shape (V,)
    is_high_freq_t = torch.from_numpy(is_high_freq.astype(np.float32)).to(device)

    # Per-token routing for training
    idx_train_np = idx_train_t.detach().cpu().numpy()
    n_pairs_total = idx_train_np.shape[0] - 1
    if n_pairs_total <= 0:
        return {"logits": np.zeros((n_h, V), dtype=np.float32),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "discriminating": {}}

    t0 = time.time()
    W_freq = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    W_rare = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    n_high_steps = 0
    n_rare_steps = 0
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs_total, (batch,), generator=gen, device=device)
        Ctx = E_full[idx_train_t[st]]
        Nxt = E_full[idx_train_t[st + 1]]
        tgt_idx = idx_train_t[st + 1]
        # Determine which targets are high-freq (in the batch)
        is_high_batch = is_high_freq_t[tgt_idx]  # shape (batch,) float (1 / 0)
        # cf-RPE on W_freq -- only count high-freq pairs (zero-mask the rest)
        error_freq = Nxt - Ctx @ W_freq.T
        wh = is_high_batch.unsqueeze(1)  # (batch, 1)
        dW_freq = ((error_freq * wh).T @ Ctx) / float(batch)
        W_freq = W_freq + lr_high * dW_freq
        # cf-RPE + STDP on W_rare -- count rare pairs
        wr = (1.0 - is_high_batch).unsqueeze(1)
        error_rare = Nxt - Ctx @ W_rare.T
        dW_cf_rare = ((error_rare * wr).T @ Ctx) / float(batch)
        Ctx_w = Ctx * wr
        Nxt_w = Nxt * wr
        dW_stdp_rare = (Nxt_w.T @ Ctx - Ctx_w.T @ Nxt) / float(batch)
        W_rare = W_rare + lr_rare * (dW_cf_rare + stdp_w * dW_stdp_rare)
        n_high_steps += int(is_high_batch.sum().item())
        n_rare_steps += int((1.0 - is_high_batch).sum().item())

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    # Recall: per held query, compute logits from BOTH banks.
    # Final logit_v = is_high_freq[v] * logit_freq_v + (1 - is_high_freq[v]) * logit_rare_v
    t0 = time.time()
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_b = E_full[idx_held_t[b:end]]
        pred_freq = _l2_normalize_t(ctx_b @ W_freq.T)
        pred_rare = _l2_normalize_t(ctx_b @ W_rare.T)
        logit_freq = pred_freq @ E_full.T  # (chunk, V)
        logit_rare = pred_rare @ E_full.T  # (chunk, V)
        mask = is_high_freq_t.unsqueeze(0)  # (1, V)
        logits[b:end] = mask * logit_freq + (1.0 - mask) * logit_rare
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    discriminating = {
        "n_high_freq_steps": int(n_high_steps),
        "n_rare_steps": int(n_rare_steps),
        "freq_threshold": int(freq_threshold),
        "n_high_freq_vocab": int(is_high_freq.sum()),
        "n_rare_vocab": int(V - is_high_freq.sum()),
    }
    # top1-stratified accuracy is computed at the eval site (we don't have nxt here)
    # so we return masks for downstream computation.

    del W_freq, W_rare, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": discriminating,
        "is_high_freq_vocab_mask": is_high_freq,  # for downstream stratified top1
    }


# ============================================================================
# ARM_ORTHOG_SUBSPACE -- Gram-Schmidt orthogonal subspaces
# ============================================================================

def _gram_schmidt_qr_split(n_dim: int, seed: int) -> Tuple[torch.Tensor, torch.Tensor]:
    """Returns (P1, P2) with P1 in R^(n_dim x n_dim/2), P2 in R^(n_dim x n_dim/2),
    and P1.T @ P2 ~= 0 (orthogonal subspaces).

    Uses Gaussian sample + QR decomposition (more numerically stable than
    iterative Gram-Schmidt for n_dim=8192).
    """
    rng = np.random.default_rng(seed * 7919 + 13)
    G = rng.standard_normal((n_dim, n_dim)).astype(np.float32)
    Q, _ = np.linalg.qr(G)
    half = n_dim // 2
    P1_np = Q[:, :half]
    P2_np = Q[:, half:]
    P1 = torch.from_numpy(P1_np).to(device=DEVICE, dtype=TORCH_DTYPE)
    P2 = torch.from_numpy(P2_np).to(device=DEVICE, dtype=TORCH_DTYPE)
    return P1, P2


def build_logits_orthog_subspace_gpu(E_full: torch.Tensor,
                                       idx_train_t: torch.Tensor,
                                       idx_held_t: torch.Tensor,
                                       n_steps: int, batch: int, lr: float,
                                       stdp_w: float,
                                       seed: int, arm_idx: int,
                                       recall_batch: int) -> Dict:
    """Orthogonal subspace composition.

    Build orthogonal projectors P1, P2 with QR decomposition (P1, P2 both
    n_dim x n_dim/2; columns orthonormal; P1.T @ P2 = 0).

    Project E into each subspace once:
      E1 = E @ P1  (V, half)
      E2 = E @ P2  (V, half)

    Train two SMALL W's, one per subspace:
      W1 (half x half): updated with cf-RPE on E1
      W2 (half x half): updated with STDP-asymmetric on E2

    Readout:
      logit_v_q = (E1_q @ W1.T) . E1_v + (E2_q @ W2.T) . E2_v
                = via L2-normalized predictions then dot product against E1/E2.

    Discriminating: track cross-subspace correlation of the GRADIENTS:
      corr(vec(dW1), vec(dW2_projected_to_subspace_1)) -- if > 0.7 then
      orthogonality failed (updates leaked across subspaces).
    """
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device
    half = dim // 2

    # Build orthogonal subspaces
    P1, P2 = _gram_schmidt_qr_split(dim, seed)
    # Sanity check orthogonality
    cross_proj = P1.T @ P2  # (half, half)
    orthog_residual = float(cross_proj.abs().max().item())

    # Project E
    E1 = E_full @ P1  # (V, half)
    E2 = E_full @ P2  # (V, half)

    # Train two small W's
    t0 = time.time()
    W1 = torch.zeros((half, half), dtype=TORCH_DTYPE, device=device)  # cf-RPE writes
    W2 = torch.zeros((half, half), dtype=TORCH_DTYPE, device=device)  # STDP writes

    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return {"logits": np.zeros((n_h, V), dtype=np.float32),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "discriminating": {}}

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)

    # For discriminating: accumulate a sample of dW1 and dW2 gradient vectors
    # to compute their cross-correlation. Sample at step indices 0, 1/4, 1/2, 3/4 of n_steps.
    sample_steps = sorted({0, n_steps // 4, n_steps // 2, 3 * n_steps // 4, n_steps - 1})
    sample_steps = [s for s in sample_steps if 0 <= s < n_steps]
    dW1_samples: List[np.ndarray] = []
    dW2_samples: List[np.ndarray] = []

    for step in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx1 = E1[idx_train_t[st]]  # (batch, half)
        Nxt1 = E1[idx_train_t[st + 1]]
        Ctx2 = E2[idx_train_t[st]]
        Nxt2 = E2[idx_train_t[st + 1]]
        # cf-RPE update on W1
        error1 = Nxt1 - Ctx1 @ W1.T
        dW1 = (error1.T @ Ctx1) / float(batch)
        W1 = W1 + lr * dW1
        # STDP-asymmetric update on W2
        dW2 = (Nxt2.T @ Ctx2 - Ctx2.T @ Nxt2) / float(batch)
        W2 = W2 + lr * stdp_w * dW2
        if step in sample_steps:
            dW1_samples.append(dW1.detach().cpu().numpy().astype(np.float32).flatten())
            dW2_samples.append(dW2.detach().cpu().numpy().astype(np.float32).flatten())

    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    # Discriminating: cross-subspace gradient correlation
    if dW1_samples and dW2_samples:
        cs = []
        for a, b in zip(dW1_samples, dW2_samples):
            an = a / (np.linalg.norm(a) + 1e-12)
            bn = b / (np.linalg.norm(b) + 1e-12)
            cs.append(float(np.dot(an, bn)))
        cross_subspace_grad_corr = float(np.mean(np.abs(cs)))
    else:
        cross_subspace_grad_corr = float("nan")

    # Recall
    t0 = time.time()
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx1_b = E1[idx_held_t[b:end]]
        ctx2_b = E2[idx_held_t[b:end]]
        pred1 = _l2_normalize_t(ctx1_b @ W1.T)
        pred2 = _l2_normalize_t(ctx2_b @ W2.T)
        # Score against E1, E2:
        logit1 = pred1 @ E1.T  # (chunk, V)
        logit2 = pred2 @ E2.T
        logits[b:end] = logit1 + logit2
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)

    del W1, W2, P1, P2, E1, E2, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": {
            "orthog_residual_max": round(orthog_residual, 6),
            "cross_subspace_grad_corr_mean_abs": round(cross_subspace_grad_corr, 4),
            "n_grad_samples": len(dW1_samples),
        },
    }


# ============================================================================
# BPC / eval utilities (identical to fair_harness)
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

    # ST1: cf-RPE delta shrinks prediction error
    n_dim_st = 64
    rng_st = np.random.default_rng(42)
    Ctx_np = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Nxt_np = rng_st.standard_normal((1, n_dim_st)).astype(np.float32)
    Ctx_np /= np.linalg.norm(Ctx_np) + 1e-8
    Nxt_np /= np.linalg.norm(Nxt_np) + 1e-8
    W_test = np.zeros((n_dim_st, n_dim_st), dtype=np.float32)
    err_before = float(np.linalg.norm(Nxt_np - Ctx_np @ W_test.T))
    dW = (Nxt_np - Ctx_np @ W_test.T).T @ Ctx_np
    W_test = W_test + 0.9 * dW
    err_after = float(np.linalg.norm(Nxt_np - Ctx_np @ W_test.T))
    assert err_after < err_before, (
        "ST1 cf-RPE should shrink error: before=%.4f after=%.4f" % (err_before, err_after))
    print("[selftest] ST1 cf-RPE shrinks error: %.4f -> %.4f" % (err_before, err_after), flush=True)

    # ST2: STDP antisymmetry: dW + dW.T == 0
    b_st = 4
    Ctx_t = torch.randn(b_st, n_dim_st, device=DEVICE)
    Nxt_t = torch.randn(b_st, n_dim_st, device=DEVICE)
    dW_stdp = (Nxt_t.T @ Ctx_t - Ctx_t.T @ Nxt_t) / float(b_st)
    antisym_err = float((dW_stdp + dW_stdp.T).abs().max())
    assert antisym_err < 1e-4, "ST2 STDP antisymmetry failed: %.4e" % antisym_err
    print("[selftest] ST2 STDP antisymmetry OK (err=%.2e)" % antisym_err, flush=True)

    # ST3: Gram-Schmidt QR split returns orthogonal subspaces
    P1, P2 = _gram_schmidt_qr_split(32, seed=1)
    cross = P1.T @ P2
    max_cross = float(cross.abs().max().item())
    assert max_cross < 1e-4, "ST3 P1.T @ P2 not zero: max=%.4e" % max_cross
    print("[selftest] ST3 Gram-Schmidt orthogonal split max|P1.T P2|=%.2e OK" % max_cross, flush=True)
    del P1, P2

    # ST4: vocab_frequency_ranks: most-frequent token gets rank 0
    idx_st = np.array([1, 2, 1, 3, 1, 2, 1], dtype=np.int64)  # token 1 most freq
    ranks = vocab_frequency_ranks(idx_st, V=5)
    assert ranks[1] == 0, "ST4 most-freq token should be rank 0; got %d" % ranks[1]
    print("[selftest] ST4 freq-ranks: token 1 (most-freq) rank=%d OK" % ranks[1], flush=True)

    # ST5: build_logits_hebbian_baseline_gpu produces non-zero logits
    V_st = 10
    n_dim_s2 = 128
    rng3 = np.random.default_rng(0)
    E_np = rng3.standard_normal((V_st, n_dim_s2)).astype(np.float32)
    E_np = _l2_normalize_np(E_np)
    E_t = torch.from_numpy(E_np).to(DEVICE)
    E_sb = _l2_normalize_t(sparsify_bipolar_gpu(E_t, SPARSE_BIPOLAR_F))
    idx_tr_st = torch.tensor([0, 1, 2, 3, 4, 5, 6, 7, 8], dtype=torch.long, device=DEVICE)
    idx_h_st = torch.tensor([3, 4, 5, 6], dtype=torch.long, device=DEVICE)
    ar = build_logits_hebbian_baseline_gpu(E_sb, idx_tr_st, idx_h_st,
                                              recall_batch=4, ingest_chunk=4)
    assert ar["logits"].shape == (idx_h_st.shape[0], V_st), (
        "ST5 baseline logits shape mismatch: %s" % str(ar["logits"].shape))
    assert not np.all(ar["logits"] == 0.0), "ST5 baseline logits all zero"
    print("[selftest] ST5 hebbian baseline logits OK", flush=True)

    # ST6: build_logits_theta_phase_two_w_gpu produces non-zero logits + valid discriminating
    ar_theta = build_logits_theta_phase_two_w_gpu(E_sb, idx_tr_st, idx_h_st,
                                                     n_steps=10, batch=3, lr=0.5,
                                                     stdp_w=0.5, seed=0, arm_idx=1,
                                                     recall_batch=4)
    assert ar_theta["logits_alpha_stack"].shape == (len(THETA_ALPHA_GRID), idx_h_st.shape[0], V_st), (
        "ST6 theta alpha stack shape wrong: %s" % str(ar_theta["logits_alpha_stack"].shape))
    assert not np.all(ar_theta["logits_alpha_stack"] == 0.0), "ST6 theta logits all zero"
    enc_vs_ret = ar_theta["discriminating"]["enc_vs_ret_bank_corr"]
    assert math.isfinite(enc_vs_ret), "ST6 enc_vs_ret_bank_corr not finite"
    # Phase counts must roughly split steps
    n0 = ar_theta["discriminating"]["n_phase0_steps"]
    n1 = ar_theta["discriminating"]["n_phase1_steps"]
    assert n0 + n1 == 10, "ST6 phase step counts mismatch: %d + %d != 10" % (n0, n1)
    print("[selftest] ST6 theta_phase: enc_ret_corr=%.4f n_phase0=%d n_phase1=%d OK" % (
        enc_vs_ret, n0, n1), flush=True)

    # ST7: build_logits_freq_routed_k2_gpu produces non-zero logits + valid mask
    ranks_st = vocab_frequency_ranks(idx_tr_st.detach().cpu().numpy(), V=V_st)
    ar_freq = build_logits_freq_routed_k2_gpu(E_sb, idx_tr_st, idx_h_st, ranks_st,
                                                 n_steps=10, batch=3,
                                                 lr_high=0.5, lr_rare=0.2,
                                                 stdp_w=0.5, freq_threshold=3,
                                                 seed=0, arm_idx=2, recall_batch=4)
    assert ar_freq["logits"].shape == (idx_h_st.shape[0], V_st), "ST7 freq logits shape wrong"
    assert not np.all(ar_freq["logits"] == 0.0), "ST7 freq logits all zero"
    is_high = ar_freq["is_high_freq_vocab_mask"]
    assert is_high.sum() <= 3, "ST7 high-freq mask count wrong (threshold=3)"
    n_high_steps = ar_freq["discriminating"]["n_high_freq_steps"]
    n_rare_steps = ar_freq["discriminating"]["n_rare_steps"]
    assert n_high_steps > 0 or n_rare_steps > 0, "ST7 freq routing zero on both"
    print("[selftest] ST7 freq_routed: n_high_steps=%d n_rare_steps=%d n_high_vocab=%d OK" % (
        n_high_steps, n_rare_steps, int(is_high.sum())), flush=True)

    # ST8: build_logits_orthog_subspace_gpu produces non-zero logits + valid discriminating
    # Need even n_dim_s2 (128 / 2 = 64 -- ok)
    ar_orthog = build_logits_orthog_subspace_gpu(E_sb, idx_tr_st, idx_h_st,
                                                    n_steps=10, batch=3, lr=0.5,
                                                    stdp_w=0.5, seed=0, arm_idx=3,
                                                    recall_batch=4)
    assert ar_orthog["logits"].shape == (idx_h_st.shape[0], V_st), "ST8 orthog logits shape wrong"
    assert not np.all(ar_orthog["logits"] == 0.0), "ST8 orthog logits all zero"
    orthog_res = ar_orthog["discriminating"]["orthog_residual_max"]
    assert orthog_res < 1e-3, "ST8 orthog residual too high: %.4e" % orthog_res
    cs_corr = ar_orthog["discriminating"]["cross_subspace_grad_corr_mean_abs"]
    assert math.isfinite(cs_corr), "ST8 cross-subspace grad corr not finite"
    print("[selftest] ST8 orthog_subspace: residual=%.2e cross_grad_corr=%.4f OK" % (
        orthog_res, cs_corr), flush=True)

    # ST9: 4 arms differ from each other (non-trivial logits diversity)
    base_logits = ar["logits"]
    theta_best = ar_theta["logits_alpha_stack"][0]
    freq_logits = ar_freq["logits"]
    orthog_logits = ar_orthog["logits"]
    d_bt = float(np.abs(base_logits - theta_best).mean())
    d_bf = float(np.abs(base_logits - freq_logits).mean())
    d_bo = float(np.abs(base_logits - orthog_logits).mean())
    assert d_bt > 1e-6, "ST9 baseline vs theta logits identical"
    assert d_bf > 1e-6, "ST9 baseline vs freq logits identical"
    assert d_bo > 1e-6, "ST9 baseline vs orthog logits identical"
    print("[selftest] ST9 arm logits diversity: bt=%.4e bf=%.4e bo=%.4e OK" % (
        d_bt, d_bf, d_bo), flush=True)

    # ST10: joint_sweep returns finite metrics on small synthetic
    n_tok_st = 30
    n_v_sm = 6
    rng6 = np.random.default_rng(99)
    logits_syn = rng6.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_syn = rng6.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_log_st = np.log(np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32))
    nd = n_tok_st // 2
    jr = joint_sweep(logits_syn[:nd], logits_syn[nd:], U_log_st,
                     nxt_syn[:nd], nxt_syn[nd:])
    assert math.isfinite(jr["bpc_best"]), "ST10 bpc_best not finite"
    assert math.isfinite(jr["top1_acc"]), "ST10 top1_acc not finite"
    print("[selftest] ST10 joint_sweep OK (bpc=%.3f top1=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"]), flush=True)

    # ST11: sparsify_bipolar_gpu produces correct nnz
    E_chk = torch.from_numpy(
        np.random.default_rng(0).standard_normal((20, 100)).astype(np.float32)
    ).to(DEVICE)
    E_sparse = sparsify_bipolar_gpu(E_chk, 0.05)
    nnz_per_row = (E_sparse != 0).sum(dim=1).cpu().numpy()
    expected_nnz = max(1, int(round(0.05 * 100)))
    assert bool((nnz_per_row == expected_nnz).all()), (
        "ST11 sparse nnz mismatch: expected %d, got %s" % (expected_nnz, str(nnz_per_row[:5])))
    print("[selftest] ST11 sparsify_bipolar_gpu nnz=%d OK" % expected_nnz, flush=True)

    # ST12: LAMBDA_GRID excludes 0.0 (META C7)
    assert 0.0 not in LAMBDA_GRID, "ST12 LAMBDA_GRID must exclude 0.0"
    print("[selftest] ST12 LAMBDA_GRID excludes 0.0 OK", flush=True)

    # ST13: LLM-call counter is zero
    assert _LLM_CALL_COUNTER[0] == 0, "ST13 LLM call counter non-zero: %d" % _LLM_CALL_COUNTER[0]
    print("[selftest] ST13 LLM call counter == 0 OK", flush=True)

    # ST14: ARMS list consistency
    expected_arms = {"ARM_BASELINE_FAIR_HARNESS", "ARM_THETA_PHASE_TWO_W",
                     "ARM_FREQ_ROUTED_K2", "ARM_ORTHOG_SUBSPACE"}
    assert set(ARMS) == expected_arms, "ST14 ARMS mismatch: %s" % set(ARMS)
    print("[selftest] ST14 ARMS consistent (%d arms) OK" % len(ARMS), flush=True)

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
        print("\n[seed=%d] SMOKE: clean synthetic markov-bigram corpus (V=%d N_TRAIN=%d N_HELD=%d)" % (
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
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE)), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)
    uni = unigram_metrics(idx_train, idx_held, V)
    print("[seed=%d arm=UNIGRAM] bpc=%.3f top1=%.4f mrr=%.4f" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["mrr_unigram"]), flush=True)

    # Frequency ranks (for ARM_FREQ_ROUTED_K2)
    ranks_np = vocab_frequency_ranks(idx_train, V=V)

    # Build encoder ONCE per seed
    print("\n[seed=%d] building encoder (V=%d, N_DIM=%d)..." % (seed, V, N_DIM), flush=True)
    t_enc0 = time.time()
    if RUN_MODE == "smoke":
        E_proj_t, w2v_meta = build_E_synthetic_smoke(V, N_DIM, seed)
    else:
        E_proj_t, w2v_meta = build_E_word2vec(vocab, N_DIM, seed)
    encoder_meta.update(w2v_meta)
    E_full = _l2_normalize_t(sparsify_bipolar_gpu(E_proj_t, SPARSE_BIPOLAR_F))
    sparsity = float((E_full != 0).float().mean().item())
    print("[seed=%d] encoder built in %.1fs; sparsity=%.3f" % (
        seed, time.time() - t_enc0, sparsity), flush=True)
    del E_proj_t

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    # Build eval pairs
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
                "N_DIM": N_DIM, "N_TRAIN": N_TRAIN, "N_HELD": N_HELD,
                "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2)}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni, "w2v_meta": w2v_meta}

    # ----- ARM 1: baseline (Hebbian K=1) -----
    arm = "ARM_BASELINE_FAIR_HARNESS"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_hebbian_baseline_gpu(
            E_full, idx_train_t, idx_held_t,
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
        }
    else:
        logits_full = ar["logits"]
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
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "discriminating": ar.get("discriminating", {}),
        })
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"],
            jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)

    # ----- ARM 2: theta-phase two-W -----
    arm = "ARM_THETA_PHASE_TWO_W"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_theta_phase_two_w_gpu(
            E_full, idx_train_t, idx_held_t,
            n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR, stdp_w=STDP_WEIGHT,
            seed=seed, arm_idx=1, recall_batch=RECALL_BATCH,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
        by_arm[arm] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
        }
    else:
        # Sweep across THETA_ALPHA_GRID; pick best by dev BPC
        alpha_stack = ar["logits_alpha_stack"]
        alpha_grid = ar["alpha_grid"]
        best_alpha_idx = 0
        best_alpha_jr = None
        best_dev_bpc = float("inf")
        valid_pos = np.where(mask)[0]
        for a_idx, alpha_val in enumerate(alpha_grid):
            logits_full = alpha_stack[a_idx]
            valid_pos_clip = valid_pos[valid_pos < logits_full.shape[0]]
            logits_eval = logits_full[valid_pos_clip]
            nxt_eval_local = nxt_full[valid_pos_clip]
            n_eval_l = len(nxt_eval_local)
            n_dev_l = n_eval_l // 2
            nxt_dev_l = nxt_eval_local[:n_dev_l]
            nxt_test_l = nxt_eval_local[n_dev_l:]
            jr = joint_sweep(logits_eval[:n_dev_l], logits_eval[n_dev_l:],
                              U_log, nxt_dev_l, nxt_test_l)
            if jr["best_dev_bpc"] < best_dev_bpc:
                best_dev_bpc = jr["best_dev_bpc"]
                best_alpha_idx = a_idx
                best_alpha_jr = jr
                best_alpha_logits = logits_eval
                best_nxt_test_l = nxt_test_l
                best_nxt_eval_local = nxt_eval_local
        jr = best_alpha_jr
        rbt1 = raw_bpc_at_T1(best_alpha_logits, best_nxt_eval_local)
        disc = dict(ar.get("discriminating", {}))
        disc["best_alpha"] = float(alpha_grid[best_alpha_idx])
        disc["best_alpha_dev_bpc"] = round(best_dev_bpc, 4)
        disc["alpha_grid"] = list(alpha_grid)
        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "discriminating": disc,
        })
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f best_alpha=%.2f enc_ret_corr=%.4f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["raw_bpc_at_T1_L1"],
            disc["best_alpha"], disc.get("enc_vs_ret_bank_corr", -1),
            jr["elapsed_s_arm"]), flush=True)

    # ----- ARM 3: frequency-routed K=2 -----
    arm = "ARM_FREQ_ROUTED_K2"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_freq_routed_k2_gpu(
            E_full, idx_train_t, idx_held_t, ranks_np,
            n_steps=N_STEPS, batch=INGEST_BATCH,
            lr_high=FREQ_LR_HIGH, lr_rare=FREQ_LR_RARE,
            stdp_w=STDP_WEIGHT,
            freq_threshold=FREQ_ROUTE_RANK if V > FREQ_ROUTE_RANK else max(1, V // 4),
            seed=seed, arm_idx=2, recall_batch=RECALL_BATCH,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
        by_arm[arm] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
        }
    else:
        logits_full = ar["logits"]
        is_high_freq_mask = ar["is_high_freq_vocab_mask"]
        valid_pos_clip = np.where(mask)[0]
        valid_pos_clip = valid_pos_clip[valid_pos_clip < logits_full.shape[0]]
        logits_eval = logits_full[valid_pos_clip]
        nxt_eval_local = nxt_full[valid_pos_clip]
        n_eval_l = len(nxt_eval_local)
        n_dev_l = n_eval_l // 2
        nxt_dev_l = nxt_eval_local[:n_dev_l]
        nxt_test_l = nxt_eval_local[n_dev_l:]
        jr = joint_sweep(logits_eval[:n_dev_l], logits_eval[n_dev_l:],
                          U_log, nxt_dev_l, nxt_test_l)
        rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval_local)
        # Stratified top1 by tgt-rank (high-freq vs low-freq)
        # Use the best (T, lambda) from the joint sweep to recompute on test.
        best_T = jr["best_T_for_top1"]
        best_lam = jr["best_lambda_for_top1"]
        probs_test = softmax_with_T(logits_eval[n_dev_l:], best_T)
        logp_sub_test = np.log(np.clip(probs_test, 1e-30, 1.0))
        logp_test = log_linear_interp(logp_sub_test, U_log, best_lam)
        pred_top1 = np.argmax(logp_test, axis=1)
        is_correct = (pred_top1 == nxt_test_l).astype(np.float32)
        nxt_is_high_freq = is_high_freq_mask[nxt_test_l]
        if nxt_is_high_freq.sum() > 0:
            top1_high = float(is_correct[nxt_is_high_freq].mean())
        else:
            top1_high = float("nan")
        if (~nxt_is_high_freq).sum() > 0:
            top1_low = float(is_correct[~nxt_is_high_freq].mean())
        else:
            top1_low = float("nan")
        freq_differential = abs(top1_high - top1_low) if (
            math.isfinite(top1_high) and math.isfinite(top1_low)) else float("nan")
        disc = dict(ar.get("discriminating", {}))
        disc.update({
            "top1_high_freq_tokens": round(top1_high, 4) if math.isfinite(top1_high) else None,
            "top1_low_freq_tokens": round(top1_low, 4) if math.isfinite(top1_low) else None,
            "freq_top1_differential": round(freq_differential, 4) if math.isfinite(freq_differential) else None,
            "n_high_freq_tgts_in_test": int(nxt_is_high_freq.sum()),
            "n_low_freq_tgts_in_test": int((~nxt_is_high_freq).sum()),
        })
        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "discriminating": disc,
        })
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f top1_high=%.3f top1_low=%.3f diff=%.3f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["raw_bpc_at_T1_L1"],
            top1_high if math.isfinite(top1_high) else -1,
            top1_low if math.isfinite(top1_low) else -1,
            freq_differential if math.isfinite(freq_differential) else -1,
            jr["elapsed_s_arm"]), flush=True)

    # ----- ARM 4: orthogonal subspace -----
    arm = "ARM_ORTHOG_SUBSPACE"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_orthog_subspace_gpu(
            E_full, idx_train_t, idx_held_t,
            n_steps=N_STEPS, batch=INGEST_BATCH, lr=ORTHOG_LR, stdp_w=STDP_WEIGHT,
            seed=seed, arm_idx=3, recall_batch=RECALL_BATCH,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
        by_arm[arm] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
        }
    else:
        logits_full = ar["logits"]
        valid_pos_clip = np.where(mask)[0]
        valid_pos_clip = valid_pos_clip[valid_pos_clip < logits_full.shape[0]]
        logits_eval = logits_full[valid_pos_clip]
        nxt_eval_local = nxt_full[valid_pos_clip]
        n_eval_l = len(nxt_eval_local)
        n_dev_l = n_eval_l // 2
        nxt_dev_l = nxt_eval_local[:n_dev_l]
        nxt_test_l = nxt_eval_local[n_dev_l:]
        jr = joint_sweep(logits_eval[:n_dev_l], logits_eval[n_dev_l:],
                          U_log, nxt_dev_l, nxt_test_l)
        rbt1 = raw_bpc_at_T1(logits_eval, nxt_eval_local)
        disc = dict(ar.get("discriminating", {}))
        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "discriminating": disc,
        })
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f cross_grad_corr=%.4f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["raw_bpc_at_T1_L1"],
            disc.get("cross_subspace_grad_corr_mean_abs", -1),
            jr["elapsed_s_arm"]), flush=True)

    del E_full
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
    arm_disc: Dict[str, Dict] = {}
    for arm in ARMS:
        valid = [u for u in units
                 if not u["by_arm"].get(arm, {}).get("compute_failed", False)
                 and math.isfinite(u["by_arm"].get(arm, {}).get("bpc_best", float("inf")))]
        if not valid:
            by_arm_agg[arm] = {"bpc_best_mean": float("inf"), "n_valid_seeds": 0,
                               "all_seeds_failed": True}
            arm_bpc[arm] = float("inf")
            arm_cv[arm] = float("nan")
            arm_disc[arm] = {}
            continue
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid]
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid]
        raw_v = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        b_cv = b_std / max(abs(b_mean), 1e-6)
        # Collect discriminating metrics (per-seed list)
        disc_per_seed = [u["by_arm"][arm].get("discriminating", {}) for u in valid]
        by_arm_agg[arm] = {
            "bpc_best_mean": round(b_mean, 4),
            "bpc_best_std": round(b_std, 4),
            "bpc_best_cv": round(b_cv, 4),
            "top1_acc_mean": round(float(np.mean(top1_v)), 4),
            "top1_acc_std": round(float(np.std(top1_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
            "raw_bpc_at_T1_L1_mean": round(float(np.mean(raw_v)), 4),
            "n_valid_seeds": len(valid),
            "discriminating_per_seed": disc_per_seed,
            "all_seeds_failed": False,
        }
        arm_bpc[arm] = b_mean
        arm_cv[arm] = b_cv
        arm_disc[arm] = disc_per_seed

    # Substrate-only audit
    total_llm_calls = sum(int(u.get("llm_forward_calls_at_inference", 0)) for u in units)
    if total_llm_calls != 0:
        return ("HARD_FAIL",
                "HARD_FAIL_LLM_CALL: llm_calls=%d (substrate-only invariant)." % total_llm_calls,
                {"by_arm_agg": by_arm_agg, "llm_forward_calls_total": total_llm_calls})

    # Baseline sanity rail (provenance) - full mode only
    baseline_bpc = arm_bpc.get("ARM_BASELINE_FAIR_HARNESS", float("inf"))
    baseline_drift = abs(baseline_bpc - SANITY_RAIL_BASELINE_REF) if math.isfinite(baseline_bpc) else float("inf")
    baseline_rail_ok = baseline_drift <= SANITY_RAIL_TOLERANCE

    # Het-routing arm BPCs
    theta_bpc = arm_bpc.get("ARM_THETA_PHASE_TWO_W", float("inf"))
    freq_bpc = arm_bpc.get("ARM_FREQ_ROUTED_K2", float("inf"))
    orthog_bpc = arm_bpc.get("ARM_ORTHOG_SUBSPACE", float("inf"))

    het_arms = {"ARM_THETA_PHASE_TWO_W": theta_bpc,
                "ARM_FREQ_ROUTED_K2": freq_bpc,
                "ARM_ORTHOG_SUBSPACE": orthog_bpc}
    best_het_name = min(het_arms.items(), key=lambda kv: kv[1])[0]
    best_het_bpc = het_arms[best_het_name]
    best_het_cv = arm_cv.get(best_het_name, float("nan"))

    arm_summary = (
        "uni=%.3f | BASE=%.4f(drift=%+.4f,rail=%s) | THETA=%.4f | FREQ=%.4f | ORTHOG=%.4f | "
        "best_het=%s (BPC=%.4f cv=%.4f)"
    ) % (
        unigram_bpc, baseline_bpc, baseline_bpc - SANITY_RAIL_BASELINE_REF, str(baseline_rail_ok),
        theta_bpc, freq_bpc, orthog_bpc,
        best_het_name, best_het_bpc,
        best_het_cv if math.isfinite(best_het_cv) else -1.0,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "het_arm_bpc": {k: round(v, 4) if math.isfinite(v) else None for k, v in het_arms.items()},
        "best_het_arm": best_het_name,
        "best_het_bpc": round(best_het_bpc, 4) if math.isfinite(best_het_bpc) else None,
        "best_het_cv": round(best_het_cv, 4) if math.isfinite(best_het_cv) else None,
        "sanity_rails": {
            "baseline_ref": SANITY_RAIL_BASELINE_REF,
            "baseline_drift": round(baseline_drift, 4),
            "baseline_rail_ok": bool(baseline_rail_ok),
            "tolerance": SANITY_RAIL_TOLERANCE,
        },
        "bands": {
            "hard_pass_cap_broken_bpc": HARD_PASS_CAP_BROKEN_BPC,
            "chain_grade_bonus_bpc": CHAIN_GRADE_BONUS_BPC,
            "middle_band_lower": MIDDLE_BAND_LOWER,
            "middle_band_upper": MIDDLE_BAND_UPPER,
            "hard_fail_decisive_floor": HARD_FAIL_DECISIVE_FLOOR,
            "cv_max": CV_MAX,
        },
        "n_seeds": len(units),
        "unigram_bpc": round(unigram_bpc, 4),
        "llm_forward_calls_total": total_llm_calls,
        "honest_scope": (
            "Tests 3 heterogeneous-routing composition architectures "
            "(theta-phase two-W / frequency-routed K=2 / orthogonal subspace) "
            "vs a fair_harness Hebbian baseline at production scale "
            "(N_DIM=8192, N_TRAIN=100k text8, V=4000, word2vec sparse-bipolar f=0.05). "
            "HARD_PASS: any het-routing arm BPC <= 6.95 refutes cf-RPE +12% cap. "
            "WHAT_THIS_DOES_NOT_SHOW: doesn't test K>2 routing variants; "
            "modern-Hopfield cleanup not stacked here (orthogonal axis to drill primary); "
            "result at text8 V=4000 may not generalize."
        ),
        "cites": [
            "notes/research_untested_composition_architectures_2x_drill_2026-06-24.md (ANCHOR 1)",
            "data/exp_fair_harness_substrate_as_lm_v1/metrics.json (baseline rail 7.3065)",
            "experiments/exp_substrate_compose_fair_harness_cfrpe_hetplasticity_K2_modern_hopfield_cleanup_v1.py",
        ],
    }

    # Compute-failure gate (load-bearing het arms)
    all_het_failed = (
        by_arm_agg.get("ARM_THETA_PHASE_TWO_W", {}).get("all_seeds_failed", True) and
        by_arm_agg.get("ARM_FREQ_ROUTED_K2", {}).get("all_seeds_failed", True) and
        by_arm_agg.get("ARM_ORTHOG_SUBSPACE", {}).get("all_seeds_failed", True)
    )
    if all_het_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: all 3 heterogeneous-routing arms failed all seeds. %s" % arm_summary,
                detail)

    # Provenance sanity rail (full mode only)
    detail["provenance_check_active"] = (RUN_MODE == "full")
    if RUN_MODE == "full" and not baseline_rail_ok:
        return ("HARD_FAIL_PROVENANCE",
                "HARD_FAIL_PROVENANCE_BASELINE: ARM_BASELINE_FAIR_HARNESS=%.4f drifts %.4f "
                "from fair_harness ref %.4f (>tol %.2f). Encoder/Hebbian pipeline mismatch. %s" % (
                    baseline_bpc, baseline_drift, SANITY_RAIL_BASELINE_REF,
                    SANITY_RAIL_TOLERANCE, arm_summary),
                detail)

    # cv gate on best het-routing arm
    if math.isfinite(best_het_cv) and best_het_cv > CV_MAX:
        return ("MIDDLE_BAND_HIGH_CV",
                "MIDDLE_BAND_HIGH_CV: best_het=%s cv=%.4f > %.2f mandatory. "
                "best_het_bpc=%.4f. %s" % (
                    best_het_name, best_het_cv, CV_MAX, best_het_bpc, arm_summary),
                detail)

    # HARD_FAIL_DECISIVE: ALL 3 het arms BPC >= 7.30
    n_below_floor = sum(1 for bpc in het_arms.values()
                        if math.isfinite(bpc) and bpc < HARD_FAIL_DECISIVE_FLOOR)
    if n_below_floor == 0 and all(math.isfinite(b) for b in het_arms.values()):
        detail["verdict_tier"] = "HARD_FAIL_DECISIVE"
        return ("HARD_FAIL",
                "HARD_FAIL_DECISIVE: all 3 het-routing arms BPC >= %.2f "
                "(theta=%.4f, freq=%.4f, orthog=%.4f). cf-RPE cap may indeed be structural "
                "at this regime. Architectural pivot needed (multi-scale hierarchical, "
                "hypernetwork, attention-as-compose). %s" % (
                    HARD_FAIL_DECISIVE_FLOOR, theta_bpc, freq_bpc, orthog_bpc, arm_summary),
                detail)

    # HARD_PASS_CAP_BROKEN (chain-grade-eligible bonus if <= 6.80)
    if math.isfinite(best_het_bpc) and best_het_bpc <= CHAIN_GRADE_BONUS_BPC:
        detail["verdict_tier"] = "HARD_PASS_CHAIN_GRADE_BONUS"
        return ("HARD_PASS",
                "HARD_PASS_CHAIN_GRADE_BONUS: best_het=%s BPC=%.4f <= %.2f (chain-grade-eligible). "
                "Heterogeneous routing decisively refutes cf-RPE cap. USER directive vindicated. %s" % (
                    best_het_name, best_het_bpc, CHAIN_GRADE_BONUS_BPC, arm_summary),
                detail)

    if math.isfinite(best_het_bpc) and best_het_bpc <= HARD_PASS_CAP_BROKEN_BPC:
        detail["verdict_tier"] = "HARD_PASS_CAP_BROKEN"
        return ("HARD_PASS",
                "HARD_PASS_CAP_BROKEN: best_het=%s BPC=%.4f <= %.2f (cf-RPE +12%% cap refuted). "
                "Heterogeneous routing provides path past same-W stacking. USER directive vindicated. %s" % (
                    best_het_name, best_het_bpc, HARD_PASS_CAP_BROKEN_BPC, arm_summary),
                detail)

    # MIDDLE_BAND
    if math.isfinite(best_het_bpc) and MIDDLE_BAND_LOWER <= best_het_bpc <= MIDDLE_BAND_UPPER:
        detail["verdict_tier"] = "MIDDLE_BAND_PARTIAL_SIGNAL"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_SIGNAL: best_het=%s BPC=%.4f in [%.2f, %.2f] "
                "(partial routing benefit; not decisively below cf-RPE cap). %s" % (
                    best_het_name, best_het_bpc, MIDDLE_BAND_LOWER, MIDDLE_BAND_UPPER,
                    arm_summary),
                detail)

    # Between MIDDLE_BAND_UPPER and HARD_FAIL_DECISIVE_FLOOR - inter-gap MIDDLE_BAND
    detail["verdict_tier"] = "MIDDLE_BAND_INTER_GAP"
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_INTER_GAP: best_het=%s BPC=%.4f between MB upper %.2f "
            "and HARD_FAIL floor %.2f. Marginal sub-cap-breaking routing benefit. %s" % (
                best_het_name, best_het_bpc, MIDDLE_BAND_UPPER, HARD_FAIL_DECISIVE_FLOOR,
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

summary_str = (
    "%s | arms=%d seeds=%d N_DIM=%d N_TRAIN=%d encoder=word2vec_sparse_bipolar het_routing_v1" % (
        verdict, len(ARMS), len(SEEDS), N_DIM, N_TRAIN)
)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": summary_str,
    "config_version": CONFIG_VERSION,
    "run_mode": RUN_MODE,
    "device": str(DEVICE),
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "N_STEPS": N_STEPS,
    "CFRPE_LR": CFRPE_LR,
    "STDP_WEIGHT": STDP_WEIGHT,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "FREQ_ROUTE_RANK": FREQ_ROUTE_RANK,
    "FREQ_LR_HIGH": FREQ_LR_HIGH,
    "FREQ_LR_RARE": FREQ_LR_RARE,
    "THETA_ALPHA_GRID": THETA_ALPHA_GRID,
    "ORTHOG_LR": ORTHOG_LR,
    "TEMP_GRID": TEMP_GRID,
    "LAMBDA_GRID": LAMBDA_GRID,
    "SEEDS": SEEDS,
    "ARMS": ARMS,
    "detail": detail,
    "per_seed": [
        {"seed": u.get("seed"), "by_arm": u.get("by_arm"),
         "V": u.get("V"), "N_DIM": u.get("N_DIM"),
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
