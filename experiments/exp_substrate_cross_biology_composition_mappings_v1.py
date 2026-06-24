"""
substrate_cross_biology_composition_mappings_v1
-- Tests 3 non-brain-biology-inspired substrate composition architectures.

Per research drill (notes/research_biology_cross_system_composition_strategies_2x_drill_2026-06-24.md):
USER directive: drill how OTHER biological systems (non-brain) solve composition.
Drill output: 7 non-brain systems CONVERGE on near-decomposability + weak-coupling-
between-specialized-modules. Substrate same-W stacking VIOLATES this universal
biology principle. If ANY of 3 mappings HARD_PASSes, substrate-native composition
architecture from non-brain biology unlocks.

Strategic context:
  Brain is ONE biological composition oracle; 7 OTHER systems give 6 more design
  templates. Cross-domain convergence (near-decomposability) is the meta-principle.

Four arms (1 reference + 3 biology-inspired weak-coupling architectures):
  ARM_BASELINE_CFRPE_K1
      Reference rail to A3 cf-RPE coarse 7.0707 (provenance check)
  ARM_SCAFFOLD_KINETIC
      MAPK scaffold analog: two FULL-N_DIM W banks; weak coupling via slow exchange.
          cf-RPE updates W_cf each step
          STDP updates W_stdp each step
          Every 100 steps: W_cf  += eps * W_stdp; W_stdp += eps * W_cf
      Readout: pred = L2(ctx @ (W_cf + W_stdp).T); logits = pred @ E.T
      Bio anchor: MAPK kinetic insulation (Behar et al PNAS 2007).
  ARM_HOX_COMBINATORIAL_3AXIS
      Developmental Hox analog: 3 orthogonal subspaces; each mechanism on ONE axis.
          Gram-Schmidt QR -> P_A, P_B, P_C (3 orthogonal projections)
          W_A: cf-RPE updates (frequency axis)
          W_B: STDP updates (temporal axis)
          W_C: sparse-amp updates (rarity axis; identity until amplified)
      Readout: cos_A(h, codebook) + cos_B(h, codebook) + cos_C(h, codebook)
      Bio anchor: Hox AP/PD/DV positional code combinatorial expression.
  ARM_STIGMERGIC_SHARED_CACHE
      Ant colony stigmergy analog: shared cache vector P; no direct cross-W coupling.
          cf-RPE writes W AND deposits onto P (fast decay TAU_FAST=10)
          STDP writes W AND deposits onto P (medium decay TAU_MED=100)
          sparse-amp READS P to modulate own update
      Readout: pred = L2(ctx @ W.T); logits = pred @ E.T (P is internal coordination)
      Bio anchor: ant pheromone trails (stigmergic indirect coordination).

PRE-REG HARD bands (per prereg):
  Sanity rail: ARM_BASELINE_CFRPE_K1 within +/-0.05 of A3 cf-RPE coarse 7.0707
  HARD_PASS_NEAR_DECOMPOSABILITY: any of bio arms BPC <= 6.95 AND cv <= 0.05
  CHAIN_GRADE_BONUS: best bio arm BPC <= 6.80
  MIDDLE_BAND: best bio in [6.95, 7.05]
  MIDDLE_BAND_INTER_GAP: best bio in (7.05, 7.20)
  HARD_FAIL_DECISIVE: all 3 bio arms BPC >= 7.20

CONFIG:
  N_DIM=8192, V=4000, text8 N_TRAIN=100k, 3 seeds, word2vec sparse-bipolar f=0.05
  Queue: remote_cpu_queue (~60min wall per drill estimate; 4500s timeout)
  LAMBDA_GRID excludes 0.0 (META C7)
  Apples-to-apples: ALL arms use identical encoder; ONLY coupling architecture varies.

CITES:
  notes/research_biology_cross_system_composition_strategies_2x_drill_2026-06-24.md
  experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py (A1 primitives)
  experiments/exp_substrate_compose_heterogeneous_routing_v1.py (2-bank architectural template)
  data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json (A3 cf-RPE reference 7.0707)
  preregs/2026-06-24_substrate_cross_biology_composition_mappings_v1.md
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

ANCHOR_NAME = "substrate_cross_biology_composition_mappings_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only audit counter
_LLM_CALL_COUNTER = [0]

# ============================================================================
# Pre-reg threshold bands
# ============================================================================
SANITY_RAIL_BASELINE_REF = 7.0707     # A3 cf-RPE coarse reference
SANITY_RAIL_TOLERANCE = 0.05

# Verdict bands (per drill / prereg)
HARD_PASS_NEAR_DECOMPOSABILITY_BPC = 6.95   # any bio arm <= 6.95 -> near-decomposability works
CHAIN_GRADE_BONUS_BPC = 6.80                # best bio arm <= 6.80 -> chain-grade-eligible
MIDDLE_BAND_LOWER = 6.95
MIDDLE_BAND_UPPER = 7.05
HARD_FAIL_DECISIVE_FLOOR = 7.20             # all 3 bio arms >= 7.20 -> resist weak-coupling
CV_MAX = 0.05

# Discriminating-regime gates
SCAFFOLD_BANK_CORR_MAX = 0.95               # w_cf vs w_stdp must be < 0.95
HOX_ORTHOG_RESIDUAL_MAX = 1e-3              # axis residuals must be < 1e-3
STIGMERGIC_CACHE_NORM_MIN = 0.1             # ||P|| must be > 0.1 (stigmergy engaged)

# ============================================================================
# Primitive knobs (frozen from chain-grade source cells)
# ============================================================================
CFRPE_LR = 0.5
STDP_WEIGHT = 0.5
INGEST_BATCH = 64
N_STEPS_PER_SEED = 1000

# Scaffold-kinetic knobs
SCAFFOLD_TRANSFER_EPS = 0.01
SCAFFOLD_TRANSFER_INTERVAL = 100

# Stigmergic cache knobs
STIGMERGIC_TAU_FAST = 10.0
STIGMERGIC_TAU_MED = 100.0
STIGMERGIC_STDP_DEPOSIT_WEIGHT = 0.5
STIGMERGIC_SPARSE_AMP_ALPHA = 0.05

# Eval grids
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

# Encoder
SPARSE_BIPOLAR_F = 0.05
WORD2VEC_MODEL = "word2vec-google-news-300"
PRETRAIN_DIM = 300

ARMS = [
    "ARM_BASELINE_CFRPE_K1",
    "ARM_SCAFFOLD_KINETIC",
    "ARM_HOX_COMBINATORIAL_3AXIS",
    "ARM_STIGMERGIC_SHARED_CACHE",
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
    # Smoke: clean synthetic + small config; goal <180s on CPU.
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 1024
    N_STEPS = 80
    RECALL_BATCH = 128
    INGEST_CHUNK = 512
    # Scale scaffold transfer interval down so smoke exercises the cross-W
    # exchange code path (full-mode 100-step interval would mean 0 transfers
    # in an 80-step smoke run).
    SCAFFOLD_TRANSFER_INTERVAL = 20

# Hox axis split sizes (3 axes; first axis takes any remainder)
N_DIM_C = N_DIM // 3
N_DIM_B = N_DIM // 3
N_DIM_A = N_DIM - N_DIM_B - N_DIM_C   # remainder absorbed here

CONFIG_VERSION = (
    "%s; encoder=word2vec_sparse_bipolar_f%.3f; N_DIM=%d (axisA=%d B=%d C=%d) "
    "N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d arms=%s seeds=%s mode=%s temps=%s lambdas=%s "
    "cfrpe_lr=%.3f stdp_w=%.3f n_steps=%d batch=%d "
    "scaffold_eps=%.3f scaffold_interval=%d "
    "stig_tau_fast=%.1f stig_tau_med=%.1f stig_stdp_dep_w=%.3f stig_amp_alpha=%.3f "
    "device=%s"
) % (
    ANCHOR_NAME, SPARSE_BIPOLAR_F, N_DIM, N_DIM_A, N_DIM_B, N_DIM_C,
    N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID,
    CFRPE_LR, STDP_WEIGHT, N_STEPS, INGEST_BATCH,
    SCAFFOLD_TRANSFER_EPS, SCAFFOLD_TRANSFER_INTERVAL,
    STIGMERGIC_TAU_FAST, STIGMERGIC_TAU_MED, STIGMERGIC_STDP_DEPOSIT_WEIGHT,
    STIGMERGIC_SPARSE_AMP_ALPHA, str(DEVICE),
)


# ============================================================================
# Corpus utilities
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
# Encoder utilities (mirrors fair_harness; word2vec + sparse-bipolar)
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
# ARM_BASELINE_CFRPE_K1 -- single-bank cf-RPE (reference rail to A3 7.0707)
# ============================================================================

def build_logits_cfrpe_baseline_gpu(E_full: torch.Tensor,
                                      idx_train_t: torch.Tensor,
                                      idx_held_t: torch.Tensor,
                                      n_steps: int, batch: int, lr: float,
                                      seed: int, recall_batch: int) -> Dict:
    """ARM_BASELINE_CFRPE_K1: single bank cf-RPE iterative."""
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return {"logits": np.zeros((n_h, V), dtype=np.float32),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "discriminating": {}}

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + 1009) & 0x7FFFFFFF)

    t0 = time.time()
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E_full[idx_train_t[st]]
        Nxt = E_full[idx_train_t[st + 1]]
        error = Nxt - Ctx @ W.T
        dW = (error.T @ Ctx) / float(batch)
        W = W + lr * dW
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    t0 = time.time()
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx = E_full[idx_held_t[b:end]]
        pred = _l2_normalize_t(ctx @ W.T)
        logits[b:end] = pred @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np, "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
            "discriminating": {}}


# ============================================================================
# ARM_SCAFFOLD_KINETIC -- 2 banks W_cf, W_stdp; weak coupling via slow exchange
# ============================================================================

def build_logits_scaffold_kinetic_gpu(E_full: torch.Tensor,
                                         idx_train_t: torch.Tensor,
                                         idx_held_t: torch.Tensor,
                                         n_steps: int, batch: int, lr: float,
                                         stdp_w: float, transfer_eps: float,
                                         transfer_interval: int,
                                         seed: int, recall_batch: int) -> Dict:
    """ARM_SCAFFOLD_KINETIC: MAPK kinetic insulation analog.

    Two banks at full N_DIM:
      W_cf updated each step by cf-RPE delta
      W_stdp updated each step by STDP asymmetric
      Every transfer_interval steps: weak cross-W exchange (eps fraction).
    Readout: pred = L2(ctx @ (W_cf + W_stdp).T); logits = pred @ E.T
    """
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    W_cf = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    W_stdp = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)

    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return {"logits": np.zeros((n_h, V), dtype=np.float32),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "discriminating": {}}

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + 2003) & 0x7FFFFFFF)

    n_cross_transfers = 0
    t0 = time.time()
    for step in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E_full[idx_train_t[st]]
        Nxt = E_full[idx_train_t[st + 1]]
        # cf-RPE on W_cf
        error = Nxt - Ctx @ W_cf.T
        dW_cf = (error.T @ Ctx) / float(batch)
        W_cf = W_cf + lr * dW_cf
        # STDP on W_stdp
        dW_stdp = (Nxt.T @ Ctx - Ctx.T @ Nxt) / float(batch)
        W_stdp = W_stdp + lr * stdp_w * dW_stdp
        # Weak cross-W exchange (slow scaffold transfer)
        if (step + 1) % transfer_interval == 0:
            # Snapshot to avoid using just-updated state in the symmetric pair
            W_cf_snap = W_cf
            W_stdp_snap = W_stdp
            W_cf = W_cf_snap + transfer_eps * W_stdp_snap
            W_stdp = W_stdp_snap + transfer_eps * W_cf_snap
            n_cross_transfers += 1
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    # Discriminating: W_cf vs W_stdp correlation (must be < 0.95)
    with torch.no_grad():
        flat_cf = W_cf.flatten()
        flat_stdp = W_stdp.flatten()
        n_cf = float(flat_cf.norm().item()) + 1e-12
        n_stdp = float(flat_stdp.norm().item()) + 1e-12
        w_cf_vs_w_stdp_corr = float((flat_cf @ flat_stdp).item() / (n_cf * n_stdp))

    t0 = time.time()
    W_sum = W_cf + W_stdp
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx = E_full[idx_held_t[b:end]]
        pred = _l2_normalize_t(ctx @ W_sum.T)
        logits[b:end] = pred @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W_cf, W_stdp, W_sum, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": {
            "w_cf_vs_w_stdp_corr": round(w_cf_vs_w_stdp_corr, 4),
            "transfer_rate_eps": round(transfer_eps, 6),
            "transfer_interval": int(transfer_interval),
            "n_cross_transfers": int(n_cross_transfers),
        },
    }


# ============================================================================
# ARM_HOX_COMBINATORIAL_3AXIS -- 3 orthogonal axes; each mechanism on ONE axis
# ============================================================================

def build_logits_hox_3axis_gpu(E_full: torch.Tensor,
                                  idx_train_t: torch.Tensor,
                                  idx_held_t: torch.Tensor,
                                  n_steps: int, batch: int, lr: float,
                                  seed: int, recall_batch: int) -> Dict:
    """ARM_HOX_COMBINATORIAL_3AXIS: developmental Hox positional code analog.

    Gram-Schmidt QR -> 3 orthogonal subspaces P_A, P_B, P_C.
    Each mechanism writes to ONE axis only:
      W_A (N_DIM_A x N_DIM_A): cf-RPE updates (frequency axis)
      W_B (N_DIM_B x N_DIM_B): STDP updates (temporal axis)
      W_C (N_DIM_C x N_DIM_C): sparse-amp updates (rarity axis)
    Readout: cos_A(h_A, codebook_A) + cos_B(h_B, codebook_B) + cos_C(h_C, codebook_C)
    """
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return {"logits": np.zeros((n_h, V), dtype=np.float32),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "discriminating": {}}

    # Build 3 orthogonal projections via Gram-Schmidt QR
    rng = np.random.default_rng(seed * 991 + 1031)
    P_full_np = rng.standard_normal((dim, dim)).astype(np.float32)
    # QR returns Q [dim, dim] orthogonal
    Q_np, _ = np.linalg.qr(P_full_np)
    P_A_np = Q_np[:, :N_DIM_A].astype(np.float32)         # [dim, N_DIM_A]
    P_B_np = Q_np[:, N_DIM_A:N_DIM_A + N_DIM_B].astype(np.float32)  # [dim, N_DIM_B]
    P_C_np = Q_np[:, N_DIM_A + N_DIM_B:].astype(np.float32)         # [dim, N_DIM_C]

    P_A = torch.from_numpy(P_A_np).to(device=device, dtype=TORCH_DTYPE)
    P_B = torch.from_numpy(P_B_np).to(device=device, dtype=TORCH_DTYPE)
    P_C = torch.from_numpy(P_C_np).to(device=device, dtype=TORCH_DTYPE)

    # Verify orthogonality (discriminating)
    with torch.no_grad():
        ortho_ab = float((P_A.T @ P_B).abs().max().item())
        ortho_ac = float((P_A.T @ P_C).abs().max().item())
        ortho_bc = float((P_B.T @ P_C).abs().max().item())
        orthog_residual_max = max(ortho_ab, ortho_ac, ortho_bc)

    # Project encoder onto 3 axes:
    #   E_A = E @ P_A   shape [V, N_DIM_A]
    E_A = _l2_normalize_t(E_full @ P_A)
    E_B = _l2_normalize_t(E_full @ P_B)
    E_C = _l2_normalize_t(E_full @ P_C)

    # Per-axis W matrices (axis-square: N_DIM_K x N_DIM_K)
    W_A = torch.zeros((N_DIM_A, N_DIM_A), dtype=TORCH_DTYPE, device=device)
    W_B = torch.zeros((N_DIM_B, N_DIM_B), dtype=TORCH_DTYPE, device=device)
    # W_C is sparse-amp identity-like; we keep it zero and the readout uses raw E_C
    # to represent the "axis active without parametric update" semantic.

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + 3001) & 0x7FFFFFFF)

    t0 = time.time()
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        # Axis A: cf-RPE
        Ctx_A = E_A[idx_train_t[st]]      # [batch, N_DIM_A]
        Nxt_A = E_A[idx_train_t[st + 1]]
        err_A = Nxt_A - Ctx_A @ W_A.T
        dW_A = (err_A.T @ Ctx_A) / float(batch)
        W_A = W_A + lr * dW_A
        # Axis B: STDP
        Ctx_B = E_B[idx_train_t[st]]
        Nxt_B = E_B[idx_train_t[st + 1]]
        dW_B = (Nxt_B.T @ Ctx_B - Ctx_B.T @ Nxt_B) / float(batch)
        W_B = W_B + lr * STDP_WEIGHT * dW_B
        # Axis C: sparse-amp is no-op at the update layer (acts only on readout)
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    # Recall: combinatorial readout per axis + per-axis ablation
    t0 = time.time()
    logits_A = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    logits_B = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    logits_C = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx_A = E_A[idx_held_t[b:end]]
        ctx_B = E_B[idx_held_t[b:end]]
        ctx_C = E_C[idx_held_t[b:end]]
        pred_A = _l2_normalize_t(ctx_A @ W_A.T)
        pred_B = _l2_normalize_t(ctx_B @ W_B.T)
        # Axis C uses raw ctx with sparse-amp identity readout (no W update needed)
        pred_C = _l2_normalize_t(ctx_C)
        logits_A[b:end] = pred_A @ E_A.T
        logits_B[b:end] = pred_B @ E_B.T
        logits_C[b:end] = pred_C @ E_C.T
    logits = logits_A + logits_B + logits_C
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    logits_A_np = logits_A.detach().cpu().numpy().astype(np.float32)
    logits_B_np = logits_B.detach().cpu().numpy().astype(np.float32)
    logits_C_np = logits_C.detach().cpu().numpy().astype(np.float32)

    del W_A, W_B, P_A, P_B, P_C, E_A, E_B, E_C
    del logits_A, logits_B, logits_C, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "logits_axis_a": logits_A_np,
        "logits_axis_b": logits_B_np,
        "logits_axis_c": logits_C_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": {
            "axis_orthog_residual_max": round(orthog_residual_max, 8),
            "axis_a_dim": int(N_DIM_A),
            "axis_b_dim": int(N_DIM_B),
            "axis_c_dim": int(N_DIM_C),
        },
    }


# ============================================================================
# ARM_STIGMERGIC_SHARED_CACHE -- shared pheromone cache; indirect coordination
# ============================================================================

def build_logits_stigmergic_gpu(E_full: torch.Tensor,
                                   idx_train_t: torch.Tensor,
                                   idx_held_t: torch.Tensor,
                                   n_steps: int, batch: int, lr: float,
                                   stdp_w: float, tau_fast: float, tau_med: float,
                                   stdp_deposit_w: float, sparse_amp_alpha: float,
                                   seed: int, recall_batch: int) -> Dict:
    """ARM_STIGMERGIC_SHARED_CACHE: ant colony stigmergy analog.

    Single bank W + shared cache P (dim N_DIM).
    Mechanisms write to W AND deposit onto P; sparse-amp READS P to modulate.
    No direct cross-mechanism W coupling; coordination only via P.
    """
    V, dim = E_full.shape
    n_h = idx_held_t.shape[0]
    device = E_full.device

    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    P_cache = torch.zeros(dim, dtype=TORCH_DTYPE, device=device)

    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return {"logits": np.zeros((n_h, V), dtype=np.float32),
                "wall_ingest_s": 0.0, "wall_recall_s": 0.0,
                "discriminating": {}}

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + 4001) & 0x7FFFFFFF)

    cache_norms: List[float] = []
    sample_every = max(1, n_steps // 50)

    t0 = time.time()
    for step in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E_full[idx_train_t[st]]
        Nxt = E_full[idx_train_t[st + 1]]

        # cf-RPE writes W AND deposits onto P (fast decay)
        error = Nxt - Ctx @ W.T
        dW_cf = (error.T @ Ctx) / float(batch)
        W = W + lr * dW_cf
        # Deposit: column-sum sign (bipolar pheromone trace)
        deposit_cf = torch.sign(dW_cf.sum(dim=0))
        P_cache = P_cache + deposit_cf
        P_cache = P_cache * (1.0 - 1.0 / tau_fast)

        # STDP writes W AND deposits onto P (medium decay)
        dW_stdp = (Nxt.T @ Ctx - Ctx.T @ Nxt) / float(batch)
        W = W + lr * stdp_w * dW_stdp
        deposit_stdp = torch.sign(dW_stdp.sum(dim=0)) * stdp_deposit_w
        P_cache = P_cache + deposit_stdp
        P_cache = P_cache * (1.0 - 1.0 / tau_med)

        # sparse-amp READS P to modulate W (no direct W update from other mechanisms)
        # Implementation: scale W by (1 + amp_alpha * sigmoid(P @ Ctx.mean(0)))
        # Bounded scalar effect; preserves stigmergy semantic (indirect via P)
        with torch.no_grad():
            ctx_mean = Ctx.mean(dim=0)
            p_dot = float((P_cache @ ctx_mean).item())
            modulation = 1.0 / (1.0 + math.exp(-p_dot))
            W = W * (1.0 + sparse_amp_alpha * (modulation - 0.5))

        if (step + 1) % sample_every == 0:
            cache_norms.append(float(P_cache.norm().item()))
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_ingest = time.time() - t0

    # Discriminating: cache norm trajectory
    if cache_norms:
        cn_arr = np.asarray(cache_norms, dtype=np.float64)
        cache_norm_max = float(cn_arr.max())
        cache_norm_mean = float(cn_arr.mean())
        cache_norm_std = float(cn_arr.std())
        cache_utilization_score = round(cache_norm_std / max(cache_norm_mean, 1e-9), 4)
    else:
        cache_norm_max = 0.0
        cache_norm_mean = 0.0
        cache_norm_std = 0.0
        cache_utilization_score = 0.0

    t0 = time.time()
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx = E_full[idx_held_t[b:end]]
        pred = _l2_normalize_t(ctx @ W.T)
        logits[b:end] = pred @ E_full.T
    if device.type == "cuda":
        torch.cuda.synchronize()
    t_recall = time.time() - t0

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del W, P_cache, logits
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "logits": logits_np,
        "wall_ingest_s": round(t_ingest, 2),
        "wall_recall_s": round(t_recall, 2),
        "discriminating": {
            "cache_norm_max": round(cache_norm_max, 4),
            "cache_norm_mean": round(cache_norm_mean, 4),
            "cache_norm_std": round(cache_norm_std, 4),
            "cache_utilization_score": float(cache_utilization_score),
            "n_cache_samples": int(len(cache_norms)),
        },
    }


# ============================================================================
# BPC / eval utilities (mirrors fair_harness / het-routing cells)
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
# Instrumentation self-test (MANDATORY per role contract)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    _dev = DEVICE
    n_dim_st = 64
    b_st = 4

    # ST1: cf-RPE delta shrinks single-pair error
    Ctx2 = torch.randn(1, n_dim_st, device=_dev)
    Nxt2 = torch.randn(1, n_dim_st, device=_dev)
    Ctx2 = Ctx2 / (Ctx2.norm() + 1e-8)
    Nxt2 = Nxt2 / (Nxt2.norm() + 1e-8)
    W_t = torch.zeros(n_dim_st, n_dim_st, device=_dev)
    e_before = float((Nxt2 - Ctx2 @ W_t.T).norm())
    dW2 = (Nxt2 - Ctx2 @ W_t.T).T @ Ctx2
    W_t = W_t + 0.9 * dW2
    e_after = float((Nxt2 - Ctx2 @ W_t.T).norm())
    assert e_after < e_before, "ST1 cf-RPE should shrink error: %.4f -> %.4f" % (e_before, e_after)
    print("[selftest] ST1 cf-RPE shrinks error: %.4f -> %.4f" % (e_before, e_after), flush=True)

    # ST2: STDP antisymmetry
    Ctx = torch.randn(b_st, n_dim_st, device=_dev)
    Nxt = torch.randn(b_st, n_dim_st, device=_dev)
    W_stdp = (Nxt.T @ Ctx - Ctx.T @ Nxt) / b_st
    antisym_err = float((W_stdp + W_stdp.T).abs().max())
    assert antisym_err < 1e-4, "ST2 STDP antisymmetry: %.2e" % antisym_err
    print("[selftest] ST2 STDP antisymmetry OK (err=%.2e)" % antisym_err, flush=True)

    # ST3: scaffold cross-transfer changes W
    W_cf = torch.randn(n_dim_st, n_dim_st, device=_dev)
    W_stdp_t = torch.randn(n_dim_st, n_dim_st, device=_dev)
    W_cf_before = W_cf.clone()
    eps = 0.01
    W_cf_snap = W_cf
    W_stdp_snap = W_stdp_t
    W_cf = W_cf_snap + eps * W_stdp_snap
    W_stdp_t = W_stdp_snap + eps * W_cf_snap
    delta = float((W_cf - W_cf_before).norm())
    assert delta > 1e-6, "ST3 scaffold transfer should change W_cf: delta=%.2e" % delta
    print("[selftest] ST3 scaffold cross-transfer changes W_cf (delta=%.4f)" % delta, flush=True)

    # ST4: Hox QR orthogonality
    rng_st = np.random.default_rng(42)
    P_test = rng_st.standard_normal((n_dim_st, n_dim_st)).astype(np.float32)
    Q, _ = np.linalg.qr(P_test)
    Q_t = torch.from_numpy(Q).to(_dev)
    P_A_t = Q_t[:, :n_dim_st // 3]
    P_B_t = Q_t[:, n_dim_st // 3:2 * (n_dim_st // 3)]
    P_C_t = Q_t[:, 2 * (n_dim_st // 3):]
    ortho_ab = float((P_A_t.T @ P_B_t).abs().max())
    ortho_ac = float((P_A_t.T @ P_C_t).abs().max())
    ortho_bc = float((P_B_t.T @ P_C_t).abs().max())
    max_ortho = max(ortho_ab, ortho_ac, ortho_bc)
    assert max_ortho < 1e-3, "ST4 Hox QR orthogonality failed: max=%.4e" % max_ortho
    print("[selftest] ST4 Hox 3-axis QR orthogonality OK (max=%.2e)" % max_ortho, flush=True)

    # ST5: stigmergic cache accumulates and decays
    P_cache = torch.zeros(n_dim_st, device=_dev)
    for _ in range(5):
        deposit = torch.sign(torch.randn(n_dim_st, device=_dev))
        P_cache = P_cache + deposit
        P_cache = P_cache * (1.0 - 1.0 / 10.0)  # tau_fast=10
    norm_after = float(P_cache.norm().item())
    assert norm_after > 0.1, "ST5 cache should accumulate: norm=%.4f" % norm_after
    print("[selftest] ST5 stigmergic cache accumulates (norm=%.4f after 5 deposits)" % norm_after, flush=True)

    # ST6: sparsify_bipolar
    V_st, dim_st = 5, 32
    E_st = torch.randn(V_st, dim_st, device=_dev)
    E_sb = sparsify_bipolar_gpu(E_st, 0.1)
    expected_nnz = max(1, int(round(0.1 * dim_st))) * V_st
    actual_nnz = int((E_sb != 0).sum().item())
    assert actual_nnz == expected_nnz, "ST6 sparse-bipolar nnz: %d != %d" % (actual_nnz, expected_nnz)
    print("[selftest] ST6 sparsify_bipolar_gpu nnz=%d OK" % expected_nnz, flush=True)

    # ST7: zero-W raw_bpc near log2(V)
    n_eval_st = 20
    n_v_st = 8
    logits_zero = torch.zeros(n_eval_st, n_v_st, device=_dev)
    raw_bpc = raw_bpc_at_T1(logits_zero.cpu().numpy(),
                              np.zeros(n_eval_st + 1, dtype=np.int64))
    expected_bpc = math.log2(n_v_st)
    assert abs(raw_bpc - expected_bpc) < 0.1, (
        "ST7 zero-W raw_bpc=%.4f should be near log2(%d)=%.4f" % (raw_bpc, n_v_st, expected_bpc))
    print("[selftest] ST7 zero-W raw_bpc=%.4f near log2(%d)=%.4f" % (raw_bpc, n_v_st, expected_bpc), flush=True)

    # ST8: joint_sweep returns finite for small synthetic
    n_tok_st = 30
    n_v_sm = 6
    rng_js = np.random.default_rng(99)
    logits_st = rng_js.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_st = rng_js.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_st = np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32)
    U_log_st = np.log(U_st)
    nd = n_tok_st // 2
    jr = joint_sweep(logits_st[:nd], logits_st[nd:], U_log_st, nxt_st[:nd], nxt_st[nd:])
    assert math.isfinite(jr["bpc_best"]), "ST8 joint_sweep bpc_best not finite"
    assert math.isfinite(jr["top1_acc"]), "ST8 joint_sweep top1 not finite"
    print("[selftest] ST8 joint_sweep all metrics finite OK (bpc=%.3f top1=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"]), flush=True)

    # ST9: LAMBDA_GRID excludes 0.0 (META C7)
    assert 0.0 not in LAMBDA_GRID, "ST9 LAMBDA_GRID must exclude 0.0"
    print("[selftest] ST9 LAMBDA_GRID excludes 0.0 OK", flush=True)

    # ST10: LLM-call counter is zero
    assert _LLM_CALL_COUNTER[0] == 0, "ST10 LLM counter non-zero: %d" % _LLM_CALL_COUNTER[0]
    print("[selftest] ST10 LLM call counter == 0 OK", flush=True)

    # ST11: ARMS list consistency
    expected_arms = {"ARM_BASELINE_CFRPE_K1", "ARM_SCAFFOLD_KINETIC",
                     "ARM_HOX_COMBINATORIAL_3AXIS", "ARM_STIGMERGIC_SHARED_CACHE"}
    assert set(ARMS) == expected_arms, "ST11 ARMS mismatch: %s" % set(ARMS)
    print("[selftest] ST11 ARMS consistent (%d arms) OK" % len(ARMS), flush=True)

    # ST12: N_DIM_A + N_DIM_B + N_DIM_C == N_DIM (Hox split)
    assert N_DIM_A + N_DIM_B + N_DIM_C == N_DIM, (
        "ST12 Hox axis split: %d + %d + %d != %d" % (N_DIM_A, N_DIM_B, N_DIM_C, N_DIM))
    print("[selftest] ST12 Hox 3-axis split A=%d B=%d C=%d sum=%d OK" % (
        N_DIM_A, N_DIM_B, N_DIM_C, N_DIM), flush=True)

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

    # Build encoder ONCE per seed
    print("\n[seed=%d] building encoder (V=%d, N_DIM=%d)..." % (seed, V, N_DIM), flush=True)
    t_enc0 = time.time()
    if RUN_MODE == "smoke":
        E_proj_t, w2v_meta = build_E_synthetic_smoke(V, N_DIM, seed)
    else:
        try:
            E_proj_t, w2v_meta = build_E_word2vec(vocab, N_DIM, seed)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("[seed=%d encoder] WORD2VEC LOAD FAIL: %s -- falling back to synthetic" % (
                seed, err), flush=True)
            E_proj_t, w2v_meta = build_E_synthetic_smoke(V, N_DIM, seed)
            w2v_meta["fallback_load_error"] = err
    encoder_meta.update(w2v_meta)
    E_full = _l2_normalize_t(sparsify_bipolar_gpu(E_proj_t, SPARSE_BIPOLAR_F))
    sparsity = float((E_full != 0).float().mean().item())
    print("[seed=%d] encoder built in %.1fs; sparsity=%.3f" % (
        seed, time.time() - t_enc0, sparsity), flush=True)
    del E_proj_t

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

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

    # Per-arm dispatch helper
    def _process_arm(arm_name: str, arm_idx: int, ar: Dict, special_ablation: bool = False) -> None:
        nonlocal by_arm
        t_arm0 = time.time()
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
        disc = dict(ar.get("discriminating", {}))

        if special_ablation and arm_name == "ARM_HOX_COMBINATORIAL_3AXIS":
            # Per-axis BPC ablation lift
            la = ar.get("logits_axis_a")
            lb = ar.get("logits_axis_b")
            lc = ar.get("logits_axis_c")
            if la is not None and lb is not None and lc is not None:
                la_eval = la[valid_pos]
                lb_eval = lb[valid_pos]
                lc_eval = lc[valid_pos]
                # BPC for ablate-axis-X = (sum of all axes) - axis_X
                logits_no_A = lb_eval + lc_eval
                logits_no_B = la_eval + lc_eval
                logits_no_C = la_eval + lb_eval
                jr_noA = joint_sweep(logits_no_A[:n_dev_l], logits_no_A[n_dev_l:],
                                       U_log, nxt_dev_l, nxt_test_l)
                jr_noB = joint_sweep(logits_no_B[:n_dev_l], logits_no_B[n_dev_l:],
                                       U_log, nxt_dev_l, nxt_test_l)
                jr_noC = joint_sweep(logits_no_C[:n_dev_l], logits_no_C[n_dev_l:],
                                       U_log, nxt_dev_l, nxt_test_l)
                # Ablation lift = BPC_without_axis - BPC_full (higher = axis was helping)
                disc["axis_a_ablation_lift"] = round(jr_noA["bpc_best"] - jr["bpc_best"], 4)
                disc["axis_b_ablation_lift"] = round(jr_noB["bpc_best"] - jr["bpc_best"], 4)
                disc["axis_c_ablation_lift"] = round(jr_noC["bpc_best"] - jr["bpc_best"], 4)
                disc["bpc_full_3axis"] = jr["bpc_best"]
                disc["bpc_ablate_a"] = jr_noA["bpc_best"]
                disc["bpc_ablate_b"] = jr_noB["bpc_best"]
                disc["bpc_ablate_c"] = jr_noC["bpc_best"]

        jr.update({
            "elapsed_s_arm": round(time.time() - t_arm0, 2),
            "wall_ingest_s": ar.get("wall_ingest_s", 0.0),
            "wall_recall_s": ar.get("wall_recall_s", 0.0),
            "raw_bpc_at_T1_L1": round(rbt1, 4),
            "discriminating": disc,
        })
        by_arm[arm_name] = jr

    # ----- ARM 1: baseline cf-RPE single-bank -----
    arm = "ARM_BASELINE_CFRPE_K1"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_cfrpe_baseline_gpu(
            E_full, idx_train_t, idx_held_t,
            n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR,
            seed=seed, recall_batch=RECALL_BATCH,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
        by_arm[arm] = {"compute_failed": True, "compute_error": err,
                        "bpc_best": float("inf"), "top1_acc": float("nan"),
                        "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                        "elapsed_s_arm": round(time.time() - t_arm0, 2)}
    else:
        _process_arm(arm, 0, ar)
        jr = by_arm[arm]
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"],
            jr["raw_bpc_at_T1_L1"], jr["elapsed_s_arm"]), flush=True)

    # ----- ARM 2: scaffold-kinetic -----
    arm = "ARM_SCAFFOLD_KINETIC"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_scaffold_kinetic_gpu(
            E_full, idx_train_t, idx_held_t,
            n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR,
            stdp_w=STDP_WEIGHT, transfer_eps=SCAFFOLD_TRANSFER_EPS,
            transfer_interval=SCAFFOLD_TRANSFER_INTERVAL,
            seed=seed, recall_batch=RECALL_BATCH,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
        by_arm[arm] = {"compute_failed": True, "compute_error": err,
                        "bpc_best": float("inf"), "top1_acc": float("nan"),
                        "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                        "elapsed_s_arm": round(time.time() - t_arm0, 2)}
    else:
        _process_arm(arm, 1, ar)
        jr = by_arm[arm]
        disc = jr.get("discriminating", {})
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f w_corr=%.4f n_transfers=%d elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["raw_bpc_at_T1_L1"],
            disc.get("w_cf_vs_w_stdp_corr", -1), disc.get("n_cross_transfers", -1),
            jr["elapsed_s_arm"]), flush=True)

    # ----- ARM 3: Hox 3-axis combinatorial -----
    arm = "ARM_HOX_COMBINATORIAL_3AXIS"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_hox_3axis_gpu(
            E_full, idx_train_t, idx_held_t,
            n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR,
            seed=seed, recall_batch=RECALL_BATCH,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
        by_arm[arm] = {"compute_failed": True, "compute_error": err,
                        "bpc_best": float("inf"), "top1_acc": float("nan"),
                        "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                        "elapsed_s_arm": round(time.time() - t_arm0, 2)}
    else:
        _process_arm(arm, 2, ar, special_ablation=True)
        jr = by_arm[arm]
        disc = jr.get("discriminating", {})
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f orth_res=%.2e ablA=%.3f ablB=%.3f ablC=%.3f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["raw_bpc_at_T1_L1"],
            disc.get("axis_orthog_residual_max", -1),
            disc.get("axis_a_ablation_lift", -1),
            disc.get("axis_b_ablation_lift", -1),
            disc.get("axis_c_ablation_lift", -1),
            jr["elapsed_s_arm"]), flush=True)

    # ----- ARM 4: stigmergic shared-cache -----
    arm = "ARM_STIGMERGIC_SHARED_CACHE"
    t_arm0 = time.time()
    print("\n  [seed=%d arm=%s] computing..." % (seed, arm), flush=True)
    try:
        ar = build_logits_stigmergic_gpu(
            E_full, idx_train_t, idx_held_t,
            n_steps=N_STEPS, batch=INGEST_BATCH, lr=CFRPE_LR,
            stdp_w=STDP_WEIGHT,
            tau_fast=STIGMERGIC_TAU_FAST, tau_med=STIGMERGIC_TAU_MED,
            stdp_deposit_w=STIGMERGIC_STDP_DEPOSIT_WEIGHT,
            sparse_amp_alpha=STIGMERGIC_SPARSE_AMP_ALPHA,
            seed=seed, recall_batch=RECALL_BATCH,
        )
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err), flush=True)
        by_arm[arm] = {"compute_failed": True, "compute_error": err,
                        "bpc_best": float("inf"), "top1_acc": float("nan"),
                        "mrr_at_10": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
                        "elapsed_s_arm": round(time.time() - t_arm0, 2)}
    else:
        _process_arm(arm, 3, ar)
        jr = by_arm[arm]
        disc = jr.get("discriminating", {})
        print("    [seed=%d arm=%s] bpc_best=%.3f top1=%.4f rawT1=%.3f cache_max=%.3f cache_util=%.3f elapsed=%.1fs" % (
            seed, arm, jr["bpc_best"], jr["top1_acc"], jr["raw_bpc_at_T1_L1"],
            disc.get("cache_norm_max", -1), disc.get("cache_utilization_score", -1),
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
        raw_v = [u["by_arm"][arm].get("raw_bpc_at_T1_L1", float("nan")) for u in valid]
        b_mean = float(np.mean(bpc_v))
        b_std = float(np.std(bpc_v))
        b_cv = b_std / max(abs(b_mean), 1e-6)
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

    # Substrate-only audit
    total_llm_calls = sum(int(u.get("llm_forward_calls_at_inference", 0)) for u in units)
    if total_llm_calls != 0:
        return ("HARD_FAIL",
                "HARD_FAIL_LLM_CALL: llm_calls=%d (substrate-only invariant)." % total_llm_calls,
                {"by_arm_agg": by_arm_agg, "llm_forward_calls_total": total_llm_calls})

    # Baseline provenance rail (full mode only) — A3 cf-RPE coarse 7.0707
    baseline_bpc = arm_bpc.get("ARM_BASELINE_CFRPE_K1", float("inf"))
    baseline_drift = abs(baseline_bpc - SANITY_RAIL_BASELINE_REF) if math.isfinite(baseline_bpc) else float("inf")
    baseline_rail_ok = baseline_drift <= SANITY_RAIL_TOLERANCE

    # Bio arms
    scaffold_bpc = arm_bpc.get("ARM_SCAFFOLD_KINETIC", float("inf"))
    hox_bpc = arm_bpc.get("ARM_HOX_COMBINATORIAL_3AXIS", float("inf"))
    stig_bpc = arm_bpc.get("ARM_STIGMERGIC_SHARED_CACHE", float("inf"))

    bio_arms = {"ARM_SCAFFOLD_KINETIC": scaffold_bpc,
                "ARM_HOX_COMBINATORIAL_3AXIS": hox_bpc,
                "ARM_STIGMERGIC_SHARED_CACHE": stig_bpc}
    best_bio_name = min(bio_arms.items(), key=lambda kv: kv[1])[0]
    best_bio_bpc = bio_arms[best_bio_name]
    best_bio_cv = arm_cv.get(best_bio_name, float("nan"))

    arm_summary = (
        "uni=%.3f | BASE_CFRPE_K1=%.4f(drift=%+.4f,rail=%s) | SCAFFOLD=%.4f | HOX_3AXIS=%.4f | STIG=%.4f | "
        "best_bio=%s (BPC=%.4f cv=%.4f)"
    ) % (
        unigram_bpc, baseline_bpc, baseline_bpc - SANITY_RAIL_BASELINE_REF, str(baseline_rail_ok),
        scaffold_bpc, hox_bpc, stig_bpc,
        best_bio_name, best_bio_bpc,
        best_bio_cv if math.isfinite(best_bio_cv) else -1.0,
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "bio_arm_bpc": {k: round(v, 4) if math.isfinite(v) else None for k, v in bio_arms.items()},
        "best_bio_arm": best_bio_name,
        "best_bio_bpc": round(best_bio_bpc, 4) if math.isfinite(best_bio_bpc) else None,
        "best_bio_cv": round(best_bio_cv, 4) if math.isfinite(best_bio_cv) else None,
        "sanity_rails": {
            "baseline_ref_A3_cfrpe_coarse": SANITY_RAIL_BASELINE_REF,
            "baseline_drift": round(baseline_drift, 4),
            "baseline_rail_ok": bool(baseline_rail_ok),
            "tolerance": SANITY_RAIL_TOLERANCE,
        },
        "bands": {
            "hard_pass_near_decomposability_bpc": HARD_PASS_NEAR_DECOMPOSABILITY_BPC,
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
            "Tests 3 non-brain-biology-inspired composition architectures "
            "(scaffold-kinetic / Hox 3-axis combinatorial / stigmergic shared cache) "
            "vs cf-RPE single-bank baseline at production scale "
            "(N_DIM=8192, N_TRAIN=100k text8, V=4000, word2vec sparse-bipolar f=0.05). "
            "HARD_PASS_NEAR_DECOMPOSABILITY: any bio arm BPC <= 6.95 confirms "
            "near-decomposability + weak-coupling principle works in substrate. "
            "WHAT_THIS_DOES_NOT_SHOW: doesn't test other 4 non-brain biology principles "
            "(gene regulation cooperative-AND, immune mutate-and-select, cellular "
            "compartmentalization, sigma-factor switching); doesn't sweep transfer rates; "
            "doesn't stack bio arms; result at text8 V=4000 may not generalize."
        ),
        "cites": [
            "notes/research_biology_cross_system_composition_strategies_2x_drill_2026-06-24.md",
            "data/exp_substrate_cfrpe_n_steps_curve_v1/metrics.json (A3 cf-RPE coarse ref 7.0707)",
            "experiments/exp_substrate_heterogeneous_plasticity_cfrpe_stdp_fair_harness_v1.py",
            "experiments/exp_substrate_compose_heterogeneous_routing_v1.py",
            "preregs/2026-06-24_substrate_cross_biology_composition_mappings_v1.md",
        ],
    }

    # All bio arms compute-failed gate
    all_bio_failed = (
        by_arm_agg.get("ARM_SCAFFOLD_KINETIC", {}).get("all_seeds_failed", True) and
        by_arm_agg.get("ARM_HOX_COMBINATORIAL_3AXIS", {}).get("all_seeds_failed", True) and
        by_arm_agg.get("ARM_STIGMERGIC_SHARED_CACHE", {}).get("all_seeds_failed", True)
    )
    if all_bio_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: all 3 biology-inspired arms failed all seeds. %s" % arm_summary,
                detail)

    # Provenance sanity rail (full mode only)
    detail["provenance_check_active"] = (RUN_MODE == "full")
    if RUN_MODE == "full" and not baseline_rail_ok:
        return ("HARD_FAIL_PROVENANCE",
                "HARD_FAIL_PROVENANCE_BASELINE: ARM_BASELINE_CFRPE_K1=%.4f drifts %.4f from "
                "A3 cf-RPE coarse ref %.4f (>tol %.2f). cf-RPE pipeline mismatch. %s" % (
                    baseline_bpc, baseline_drift, SANITY_RAIL_BASELINE_REF,
                    SANITY_RAIL_TOLERANCE, arm_summary),
                detail)

    # cv gate on best bio arm
    if math.isfinite(best_bio_cv) and best_bio_cv > CV_MAX:
        return ("MIDDLE_BAND_HIGH_CV",
                "MIDDLE_BAND_HIGH_CV: best_bio=%s cv=%.4f > %.2f mandatory. "
                "best_bio_bpc=%.4f. %s" % (
                    best_bio_name, best_bio_cv, CV_MAX, best_bio_bpc, arm_summary),
                detail)

    # HARD_FAIL_DECISIVE: ALL 3 bio arms BPC >= 7.20
    n_below_floor = sum(1 for bpc in bio_arms.values()
                         if math.isfinite(bpc) and bpc < HARD_FAIL_DECISIVE_FLOOR)
    if n_below_floor == 0 and all(math.isfinite(b) for b in bio_arms.values()):
        detail["verdict_tier"] = "HARD_FAIL_DECISIVE"
        return ("HARD_FAIL",
                "HARD_FAIL_DECISIVE: all 3 bio arms BPC >= %.2f "
                "(scaffold=%.4f, hox=%.4f, stigmergic=%.4f). Substrate composition resists "
                "weak-coupling architecture too; near-decomposability does NOT transfer "
                "at this regime. %s" % (
                    HARD_FAIL_DECISIVE_FLOOR, scaffold_bpc, hox_bpc, stig_bpc, arm_summary),
                detail)

    # HARD_PASS_CHAIN_GRADE_BONUS
    if math.isfinite(best_bio_bpc) and best_bio_bpc <= CHAIN_GRADE_BONUS_BPC:
        detail["verdict_tier"] = "HARD_PASS_CHAIN_GRADE_BONUS"
        return ("HARD_PASS",
                "HARD_PASS_CHAIN_GRADE_BONUS: best_bio=%s BPC=%.4f <= %.2f (chain-grade-eligible). "
                "Non-brain biology composition mapping decisively breaks cap. USER directive "
                "vindicated. %s" % (
                    best_bio_name, best_bio_bpc, CHAIN_GRADE_BONUS_BPC, arm_summary),
                detail)

    # HARD_PASS_NEAR_DECOMPOSABILITY
    if math.isfinite(best_bio_bpc) and best_bio_bpc <= HARD_PASS_NEAR_DECOMPOSABILITY_BPC:
        detail["verdict_tier"] = "HARD_PASS_NEAR_DECOMPOSABILITY"
        return ("HARD_PASS",
                "HARD_PASS_NEAR_DECOMPOSABILITY: best_bio=%s BPC=%.4f <= %.2f (near-decomposability "
                "principle works in substrate). %s" % (
                    best_bio_name, best_bio_bpc, HARD_PASS_NEAR_DECOMPOSABILITY_BPC, arm_summary),
                detail)

    # MIDDLE_BAND
    if math.isfinite(best_bio_bpc) and MIDDLE_BAND_LOWER <= best_bio_bpc <= MIDDLE_BAND_UPPER:
        detail["verdict_tier"] = "MIDDLE_BAND_PARTIAL_SIGNAL"
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_SIGNAL: best_bio=%s BPC=%.4f in [%.2f, %.2f] "
                "(partial biology-inspired benefit; not decisively below cap). %s" % (
                    best_bio_name, best_bio_bpc, MIDDLE_BAND_LOWER, MIDDLE_BAND_UPPER,
                    arm_summary),
                detail)

    # Inter-gap MIDDLE_BAND
    detail["verdict_tier"] = "MIDDLE_BAND_INTER_GAP"
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_INTER_GAP: best_bio=%s BPC=%.4f between MB upper %.2f and "
            "HARD_FAIL floor %.2f. Marginal sub-cap-breaking biology benefit. %s" % (
                best_bio_name, best_bio_bpc, MIDDLE_BAND_UPPER, HARD_FAIL_DECISIVE_FLOOR,
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
    "%s | arms=%d seeds=%d N_DIM=%d N_TRAIN=%d encoder=word2vec_sparse_bipolar cross_biology_v1" % (
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
    "SCAFFOLD_TRANSFER_EPS": SCAFFOLD_TRANSFER_EPS,
    "SCAFFOLD_TRANSFER_INTERVAL": SCAFFOLD_TRANSFER_INTERVAL,
    "STIGMERGIC_TAU_FAST": STIGMERGIC_TAU_FAST,
    "STIGMERGIC_TAU_MED": STIGMERGIC_TAU_MED,
    "STIGMERGIC_STDP_DEPOSIT_WEIGHT": STIGMERGIC_STDP_DEPOSIT_WEIGHT,
    "STIGMERGIC_SPARSE_AMP_ALPHA": STIGMERGIC_SPARSE_AMP_ALPHA,
    "HOX_AXIS_DIMS": [N_DIM_A, N_DIM_B, N_DIM_C],
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
