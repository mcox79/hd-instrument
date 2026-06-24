"""
substrate_top1_targeted_plasticity_4arm_smoke_v1 -- 5-arm smoke comparing
argmax-targeted plasticity rules vs cf-RPE reference at SAME cosine-NN readout.

DRILL: Research top1-targeted-plasticity 2x drill 2026-06-24.
HYPOTHESIS: cf-RPE +12% top1 ceiling is RULE-TARGETING-LIMITED (MSE delta-rule
optimizes BPC residual; cannot widen winner-runner-up gap). 4 argmax-targeted
families lit-precedented as candidates:

  ARM_CFRPE_REFERENCE   cf-RPE delta-rule (MSE-targeted; cf-RPE family reference)
  ARM_BCPNN             Bayesian-Hebbian log-odds (Ravichandran 2024)
  ARM_ARGMAX_DELTA      gated perceptron-class update (Sjostrom-Hausser 2006)
  ARM_LATERAL_INHIBIT   cf-RPE + anti-Hebbian runner-up (Foldiak 1990; Coultrip 1992)
  ARM_CHL               contrastive Hebbian: clamped - free (Movellan 1991; O'Reilly 1996)

ALL ARMS use the SAME cosine-NN readout (logits[V] = cosine(W @ src_hd, codebook C))
and the SAME word2vec-projected sparse-bipolar encoder. Only the plasticity rule on
W differs. PRIMARY METRIC: top1_acc (NOT BPC -- Fix #28 per-arm metrics; BPC and top1
are not monotonically related under plasticity-rule changes; cf-RPE family ceiling at
+12% top1 vs n1_v3 readout +61.6% top1 = 5x lift-ratio gap is the empirical anchor).

PRE-REG HARD BANDS (per drill / prereg .md):
  Sanity:           cfrpe_top1 - unigram_top1 in [+0.03, +0.18] absolute
  HARD_PASS:        ANY non-cfrpe arm: top1 lift over ARM_CFRPE_REFERENCE >= +0.05
                    AND cv across seeds <= 0.10
  MIDDLE_BAND:      best non-cfrpe lift in [+0.02, +0.05) OR cv in (0.10, 0.15]
  HARD_FAIL_DEC:    ALL non-cfrpe arms within +/-0.02 of cfrpe (plasticity-as-top1-lever
                    decisively closed at smoke; readout dominates)

CONFIG (smoke-scale CPU-tractable per drill recommendation):
  N_DIM=2048, V=2000, N_TRAIN=20k, 3 seeds, ~30 min wall expected.

ASCII-only. Fix #14 ONE cell. Fix #26 predispatch_check PROCEED.
Fix #28 per-arm top1 primary; per-arm cv reported; no cross-arm aggregation in verdict.
Forks: experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py heritage.

Cites:
  preregs/2026-06-24_substrate_top1_targeted_plasticity_4arm_smoke_v1.md
  notes/research_top1_targeted_plasticity_2x_drill_2026-06-24.md
  notes/skunkworks_LANDED_VET_cfrpe_per_token_adaptive_lr_v1_MEASURED_MECHANISM_2026-06-24.md
  experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py (heritage)
  experiments/exp_fair_harness_substrate_as_lm_v1.py (encoder + readout baseline)
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
    get_output_dir, write_partial, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_top1_targeted_plasticity_4arm_smoke_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

WORD2VEC_MODEL = "word2vec-google-news-300"

# Pre-reg thresholds (HARD bands locked BEFORE dispatch per prereg .md)
HARD_PASS_TOP1_LIFT = 0.05            # absolute top1 lift over cf-RPE reference
MIDDLE_BAND_TOP1_LIFT_FLOOR = 0.02    # absolute top1 lift floor for middle band
HARD_FAIL_DECISIVE_TOL = 0.02         # all arms within +/- this of cfrpe -> decisive close
SANITY_CFRPE_TOP1_LIFT_MIN = 0.03     # cf-RPE reference must lift this much over unigram
SANITY_CFRPE_TOP1_LIFT_MAX = 0.18     # ... but not more than this (provenance check)
HP_TOP1_CV_MAX = 0.10                 # cv across seeds for HARD_PASS
MIDDLE_BAND_TOP1_CV_MAX = 0.15        # cv across seeds for MIDDLE_BAND

# Plasticity knobs (cf-RPE knobs match heritage; other arms per drill design)
CFRPE_LR = 0.5
INGEST_BATCH = 64
SPARSE_BIPOLAR_F = 0.05
N_STEPS_PLASTIC_FULL = 5000           # matches cf-RPE COARSE_N_STEPS reference

# BCPNN
BCPNN_EMA_ALPHA = 0.01                # trace half-life ~70 steps; Ravichandran 2024 default
BCPNN_EPS = 1e-6                      # numerical floor for log

# ARGMAX_DELTA (gated perceptron-class)
ARGMAX_MARGIN_THRESHOLD = 0.0         # pred != tgt triggers update; pure argmax gate

# LATERAL_INHIBIT (cf-RPE + anti-Hebbian runner-up)
LATERAL_INHIBIT_GAMMA = 0.5           # Foldiak-class anti-Hebbian gain (drill PRED-3 range [0.3,1.0])

# CHL (contrastive Hebbian: clamped - free)
CHL_FREE_PHASE_SCALE = 1.0            # free-phase prediction = W @ src directly

# Inference grids (C7: LAMBDA_GRID excludes 0.0)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.05, 0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

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

# Production config (drill smoke-scale defaults; cell anchor IS the drill smoke)
N_DIM = 2048
PRETRAIN_DIM = 300
VOCAB_CAP = 2000
INGEST_CHUNK = 4096
RECALL_BATCH = 256

# Gensim cache (process-local)
_GENSIM_KV_CACHE: Dict[str, object] = {}

if RUN_MODE == "full":
    # "Full" for this anchor IS the drill smoke (N=2048, V=2000, N_TRAIN=20k, 3 seeds)
    # Per drill: smoke-scale IS the decisive discriminator; HARD_PASS triggers a separate
    # N=8192/N=100k full dispatch under a DIFFERENT anchor (suffix _full_n8192).
    SEEDS = [7, 17, 23]
    N_TRAIN = 20_000
    N_HELD = 4_000
    N_STEPS_PLASTIC = N_STEPS_PLASTIC_FULL
else:
    # Inner smoke: tiny mode for --smoke / --self-test pre-flight (exercises 5 arms + verdict)
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    N_STEPS_PLASTIC = 200

ARMS = [
    "ARM_CFRPE_REFERENCE",
    "ARM_BCPNN",
    "ARM_ARGMAX_DELTA",
    "ARM_LATERAL_INHIBIT",
    "ARM_CHL",
]
NON_CFRPE_ARMS = [a for a in ARMS if a != "ARM_CFRPE_REFERENCE"]


# ============================================================================
# Char-trigram encoder (OOV fallback + smoke encoder)
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


def _l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.clip(norms, eps, None)


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
# Plasticity rules
# ============================================================================

def build_W_cfrpe_reference(E: torch.Tensor, idx_train_t: torch.Tensor,
                              n_steps: int, batch: int, lr: float,
                              gen: torch.Generator) -> Tuple[torch.Tensor, Dict]:
    """Standard cf-RPE delta-rule: GLOBAL LR applied uniformly to all batch samples.
    Reference arm: provenance-checks against published cf-RPE +12% top1 lift ceiling.
      error = Nxt - Ctx @ W^T
      dW    = (error.t @ Ctx) / batch
      W     = W + lr * dW
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W, {"n_steps": int(n_steps), "rule_class": "cfrpe_delta_rule_global_lr"}
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train_t[st]]
        Nxt = E[idx_train_t[st + 1]]
        error = Nxt - Ctx @ W.t()
        dW = (error.t() @ Ctx) / batch
        W = W + lr * dW
    return W, {"n_steps": int(n_steps), "rule_class": "cfrpe_delta_rule_global_lr"}


def build_W_bcpnn(E: torch.Tensor, idx_train_t: torch.Tensor,
                    n_steps: int, batch: int, ema_alpha: float, eps: float,
                    gen: torch.Generator) -> Tuple[torch.Tensor, Dict]:
    """BCPNN -- Bayesian-Hebbian log-odds via online EMA traces (Ravichandran 2024).

    For HD-substrate (no one-hot), track HD-coded co-activations + marginals via vector EMA:
      m_tgt    = alpha * mean(Nxt) + (1-alpha) * m_tgt           [dim] running marginal
      m_src    = alpha * mean(Ctx) + (1-alpha) * m_src           [dim] running marginal
      W_co     = alpha * (Nxt.t @ Ctx)/B + (1-alpha) * W_co      [dim,dim] running co-activation
      M_marg   = outer(m_tgt, m_src)                             [dim,dim] marginal product
    Final readout matrix (log-odds form):
      W = log((W_co + eps) / (M_marg + eps))
    Class-confusability normalized: frequent targets DOWN-weighted by high marginal;
    rare-but-specific targets UP-weighted. Targets top1 directly via log-odds vs MSE.
    """
    dim = E.shape[1]
    W_co = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    m_tgt = torch.zeros(dim, dtype=TORCH_DTYPE, device=DEVICE)
    m_src = torch.zeros(dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE), {
            "n_steps": int(n_steps), "rule_class": "bcpnn_log_odds_ema_traces",
            "ema_alpha": ema_alpha, "final_co_norm": 0.0, "final_marginal_product_norm": 0.0}
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train_t[st]]
        Nxt = E[idx_train_t[st + 1]]
        # batch-mean co-activation as Hebbian-style outer product
        co_batch = (Nxt.t() @ Ctx) / batch
        # running EMA
        W_co = ema_alpha * co_batch + (1.0 - ema_alpha) * W_co
        m_tgt = ema_alpha * Nxt.mean(dim=0) + (1.0 - ema_alpha) * m_tgt
        m_src = ema_alpha * Ctx.mean(dim=0) + (1.0 - ema_alpha) * m_src
    M_marg = torch.outer(m_tgt, m_src)
    # log-odds form. Add eps to BOTH numerator and denominator to keep finite.
    # Shift to [0,inf) before log via abs() -- HD bipolar means W_co/M_marg can be negative.
    # Standard BCPNN treats P_ij/P_iP_j as positive co-occurrence; we use the signed
    # log-odds form: sign(W_co) * log((|W_co| + eps) / (|M_marg| + eps)) so the
    # readout preserves direction of association.
    abs_co = W_co.abs() + eps
    abs_marg = M_marg.abs() + eps
    log_ratio = torch.log(abs_co / abs_marg)
    W = torch.sign(W_co) * log_ratio
    return W, {
        "n_steps": int(n_steps),
        "rule_class": "bcpnn_log_odds_ema_traces_signed",
        "ema_alpha": float(ema_alpha),
        "final_co_norm": float(W_co.norm()),
        "final_marginal_product_norm": float(M_marg.norm()),
        "log_ratio_min": float(log_ratio.min()),
        "log_ratio_max": float(log_ratio.max()),
    }


def build_W_argmax_delta(E: torch.Tensor, idx_train_t: torch.Tensor,
                           n_steps: int, batch: int, lr: float,
                           margin_threshold: float,
                           gen: torch.Generator) -> Tuple[torch.Tensor, Dict]:
    """ARGMAX_DELTA -- gated perceptron-class update: fire only when argmax fails.

    For each batch step:
      logits = (W @ Ctx.t).t @ E.t                 # [batch, V] cosine-NN logits over codebook
      preds  = argmax(logits, dim=1)               # current best guess per sample
      mask   = (preds != tgt_idx) -- "fired"       # only update failed-argmax samples
      For each fired sample i:
        dW += lr * outer(C[tgt] - C[preds], Ctx)   # push toward target, away from incorrect winner
    Margin variant: also fire if cos(W@src, C[tgt]) - cos(W@src, C[pred]) < margin_threshold
      (margin_threshold = 0 -> pure argmax gate).
    Tracks effective_update_fraction: must be in [0.10, 0.95] (drill PRED-2 selectivity check).
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W, {"n_steps": int(n_steps), "rule_class": "argmax_delta_gated_margin",
                    "margin_threshold": float(margin_threshold),
                    "effective_update_fraction": 0.0,
                    "total_samples": 0, "total_updates": 0}
    total_samples = 0
    total_updates = 0
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train_t[st]]                  # [batch, dim]
        tgt_idx = idx_train_t[st + 1]             # [batch] int
        # readout logits over all V via cosine-NN
        pred_hd = Ctx @ W.t()                     # [batch, dim] prediction in HD
        # cosine-similarity to all V atoms = pred_hd @ E.t (E is L2-normalized)
        pred_hd_n = _l2_normalize_t(pred_hd)
        logits = pred_hd_n @ E.t()                # [batch, V] cosines
        preds = torch.argmax(logits, dim=1)       # [batch] int
        # margin: cos(pred, tgt) - cos(pred, current-best)
        idx_b = torch.arange(Ctx.shape[0], device=DEVICE)
        cos_tgt = logits[idx_b, tgt_idx]
        cos_pred = logits[idx_b, preds]
        margin = cos_tgt - cos_pred
        # fire when prediction != target OR margin < threshold
        fire_mask = (preds != tgt_idx) | (margin < margin_threshold)
        n_fired = int(fire_mask.sum())
        total_samples += int(Ctx.shape[0])
        total_updates += n_fired
        if n_fired == 0:
            continue
        # update: dW += lr * outer(C[tgt] - C[preds], Ctx) summed over fired
        Ctx_fired = Ctx[fire_mask]                # [n_fired, dim]
        tgt_hd = E[tgt_idx[fire_mask]]            # [n_fired, dim]
        pred_hd_pred = E[preds[fire_mask]]        # [n_fired, dim] codebook atom of pred
        diff = tgt_hd - pred_hd_pred              # [n_fired, dim]
        dW = (diff.t() @ Ctx_fired) / max(n_fired, 1)
        W = W + lr * dW
    eff_frac = float(total_updates) / max(total_samples, 1)
    return W, {
        "n_steps": int(n_steps),
        "rule_class": "argmax_delta_gated_margin",
        "margin_threshold": float(margin_threshold),
        "effective_update_fraction": round(eff_frac, 4),
        "total_samples": int(total_samples),
        "total_updates": int(total_updates),
    }


def build_W_lateral_inhibit(E: torch.Tensor, idx_train_t: torch.Tensor,
                              n_steps: int, batch: int, lr: float, gamma: float,
                              gen: torch.Generator) -> Tuple[torch.Tensor, Dict]:
    """LATERAL_INHIBIT -- cf-RPE delta-rule + anti-Hebbian runner-up suppression.

    For each batch step:
      error    = Nxt - Ctx @ W^T                         [batch, dim] cf-RPE delta
      dW_cfrpe = lr * (error.t @ Ctx) / batch            cf-RPE component
      logits   = (W @ Ctx.t).t @ E.t                     [batch, V] cosines
      run_up   = argsort(logits, descending)[:,1]        [batch] runner-up per sample
      dW_inhib = -gamma * lr * (E[run_up].t @ Ctx) / batch    anti-Hebbian on runner-up
      W = W + dW_cfrpe + dW_inhib
    Explicitly suppresses W rows producing wrong winner -> widens winner-runner-up gap.
    Tracks W_norm_ratio_vs_cfrpe: stability indicator (anti-Hebbian destabilizes if too high).
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W, {"n_steps": int(n_steps), "rule_class": "lateral_inhibit_anti_hebbian_runner_up",
                    "gamma": float(gamma), "final_W_norm": 0.0, "runner_up_hits": 0}
    runner_up_hits = 0
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train_t[st]]
        Nxt = E[idx_train_t[st + 1]]
        tgt_idx = idx_train_t[st + 1]
        # cf-RPE delta
        error = Nxt - Ctx @ W.t()
        dW_cfrpe = lr * (error.t() @ Ctx) / batch
        # runner-up identification (over codebook V)
        pred_hd = Ctx @ W.t()
        pred_hd_n = _l2_normalize_t(pred_hd)
        logits = pred_hd_n @ E.t()                # [batch, V]
        # top-2 indices descending; runner_up = top-2 index, OR top-1 if top-1 == tgt
        top2 = torch.topk(logits, k=2, dim=1).indices    # [batch, 2]
        run_up = torch.where(top2[:, 0] == tgt_idx, top2[:, 1], top2[:, 0])
        run_up_hd = E[run_up]                            # [batch, dim]
        # anti-Hebbian on runner-up (subtractive: pushes W AWAY from runner-up)
        dW_inhib = -gamma * lr * (run_up_hd.t() @ Ctx) / batch
        W = W + dW_cfrpe + dW_inhib
        runner_up_hits += int((run_up != tgt_idx).sum())
    return W, {
        "n_steps": int(n_steps),
        "rule_class": "lateral_inhibit_anti_hebbian_runner_up",
        "gamma": float(gamma),
        "final_W_norm": float(W.norm()),
        "runner_up_hits": int(runner_up_hits),
    }


def build_W_chl(E: torch.Tensor, idx_train_t: torch.Tensor,
                  n_steps: int, batch: int, lr: float, free_scale: float,
                  gen: torch.Generator) -> Tuple[torch.Tensor, Dict]:
    """CHL -- Contrastive Hebbian Learning: clamped phase minus free phase.

    For each batch step:
      pred_free    = W @ Ctx.t (the substrate's current free-phase prediction; INCLUDES runner-ups)
      pred_clamped = E[tgt] (clamped to ground-truth target HD)
      dW           = lr * (outer(pred_clamped, Ctx) - outer(free_scale * pred_free, Ctx)) / batch
      W = W + dW
    Mathematically: gradient descent on the energy difference between clamped and free phases.
    Targets the top1-winner-vs-free-prediction gap directly (vs cf-RPE MSE residual).
    """
    dim = E.shape[1]
    W = torch.zeros(dim, dim, dtype=TORCH_DTYPE, device=DEVICE)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W, {"n_steps": int(n_steps), "rule_class": "chl_clamped_minus_free",
                    "free_scale": float(free_scale), "final_W_norm": 0.0}
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=DEVICE)
        Ctx = E[idx_train_t[st]]
        Nxt = E[idx_train_t[st + 1]]
        # free phase: substrate's current prediction direct from W
        pred_free = Ctx @ W.t()                   # [batch, dim] (no nonlinearity to keep local-Hebbian)
        pred_clamped = Nxt                        # clamped to target HD (E[tgt])
        # CHL: dW = lr * (outer(pred_clamped, Ctx) - outer(free_scale * pred_free, Ctx))
        dW = lr * ((pred_clamped.t() @ Ctx) - free_scale * (pred_free.t() @ Ctx)) / batch
        W = W + dW
    return W, {
        "n_steps": int(n_steps),
        "rule_class": "chl_clamped_minus_free",
        "free_scale": float(free_scale),
        "final_W_norm": float(W.norm()),
    }


# ============================================================================
# Recall + eval pipeline (identical to cf-RPE adaptive heritage)
# ============================================================================

def compute_logits_gpu(E: torch.Tensor, W: torch.Tensor, idx_held_t: torch.Tensor,
                        recall_batch: int) -> np.ndarray:
    n_h = idx_held_t.shape[0]
    V = E.shape[0]
    logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=DEVICE)
    for b in range(0, n_h, recall_batch):
        end = min(b + recall_batch, n_h)
        ctx = E[idx_held_t[b:end]]
        pred = _l2_normalize_t(ctx @ W.t())
        logits[b:end] = pred @ E.T
    if DEVICE.type == "cuda":
        torch.cuda.synchronize()
    return logits.detach().cpu().numpy().astype(np.float32)


def _raw_bpc_at_T1(logits: np.ndarray, idx_held: np.ndarray) -> float:
    n_h = logits.shape[0]
    nxt_np = idx_held[1:] if len(idx_held) > 1 else idx_held
    n_eval = min(n_h, len(nxt_np))
    if n_eval == 0:
        return float("inf")
    z = logits[:n_eval] - logits[:n_eval].max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / np.clip(e.sum(axis=1, keepdims=True), 1e-30, None)
    p_nxt = p[np.arange(n_eval), nxt_np[:n_eval]].clip(1e-12, 1.0)
    return float(-np.mean(np.log(p_nxt)) / math.log(2.0))


# ============================================================================
# text8 corpus + vocab utilities
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
# Joint (T, lambda) sweep + 3 metrics (C7-compliant: LAMBDA_GRID excludes 0.0)
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
    raw_top1_at_T1_L1 = top1_acc(logp_T1, nxt_test)

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

    lambda_min = min(lambda_grid) if lambda_grid else 0.0
    lambda_zero_collapse = bool(
        abs(best_bpc["lambda"] - lambda_min) < 1e-6 and
        math.isfinite(bpc_best_test) and
        bpc_best_test > 7.5
    )

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
        "lambda_zero_collapse": lambda_zero_collapse,
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
# Instrumentation self-test (MANDATORY per role contract)
# ============================================================================

def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)
    _dev = DEVICE

    n_dim_st = 64
    n_v_st = 8

    # ST1: cf-RPE reference shrinks single-pair error (sanity rule check)
    Ctx1 = torch.randn(1, n_dim_st, device=_dev); Ctx1 = Ctx1 / (Ctx1.norm() + 1e-8)
    Nxt1 = torch.randn(1, n_dim_st, device=_dev); Nxt1 = Nxt1 / (Nxt1.norm() + 1e-8)
    W1 = torch.zeros(n_dim_st, n_dim_st, device=_dev)
    err_before = float((Nxt1 - Ctx1 @ W1.t()).norm())
    dW1 = (Nxt1 - Ctx1 @ W1.t()).t() @ Ctx1
    W1 = W1 + 0.9 * dW1
    err_after = float((Nxt1 - Ctx1 @ W1.t()).norm())
    assert err_after < err_before, "ST1 cf-RPE failed to shrink error"
    print("[selftest] ST1 cf-RPE shrinks error: %.4f -> %.4f" % (err_before, err_after), flush=True)

    # Shared setup: tiny codebook + sequence
    E_st = torch.randn(n_v_st, n_dim_st, device=_dev); E_st = _l2_normalize_t(E_st)
    idx_st = torch.randint(0, n_v_st, (21,), device=_dev)

    # ST2: ARM_CFRPE_REFERENCE returns non-zero W after 10 steps
    gen2 = torch.Generator(device=_dev); gen2.manual_seed(7)
    W_cfrpe, diag_cfrpe = build_W_cfrpe_reference(
        E_st, idx_st, n_steps=10, batch=4, lr=0.5, gen=gen2)
    assert float(W_cfrpe.norm()) > 1e-6, "ST2 cfrpe W is all-zero"
    print("[selftest] ST2 cfrpe_reference non-zero W norm=%.4f" % float(W_cfrpe.norm()), flush=True)

    # ST3: ARM_BCPNN returns finite W; ema traces non-zero; log-ratio bounded
    gen3 = torch.Generator(device=_dev); gen3.manual_seed(11)
    W_bcpnn, diag_bcpnn = build_W_bcpnn(
        E_st, idx_st, n_steps=30, batch=4, ema_alpha=BCPNN_EMA_ALPHA, eps=BCPNN_EPS, gen=gen3)
    assert torch.isfinite(W_bcpnn).all(), "ST3 BCPNN W non-finite (eps/log issue)"
    assert diag_bcpnn["final_co_norm"] > 1e-6, "ST3 BCPNN co-trace is zero"
    assert "log_ratio_min" in diag_bcpnn and "log_ratio_max" in diag_bcpnn
    print("[selftest] ST3 BCPNN W norm=%.4f, log_ratio_range=[%.4f,%.4f]" % (
        float(W_bcpnn.norm()), diag_bcpnn["log_ratio_min"], diag_bcpnn["log_ratio_max"]), flush=True)

    # ST4: ARM_ARGMAX_DELTA effective_update_fraction in (0, 1)
    gen4 = torch.Generator(device=_dev); gen4.manual_seed(13)
    W_argmax, diag_argmax = build_W_argmax_delta(
        E_st, idx_st, n_steps=20, batch=4, lr=0.5,
        margin_threshold=ARGMAX_MARGIN_THRESHOLD, gen=gen4)
    eff = diag_argmax["effective_update_fraction"]
    assert 0.0 < eff <= 1.0, "ST4 ARGMAX_DELTA eff frac out of range: %.4f" % eff
    print("[selftest] ST4 ARGMAX_DELTA W norm=%.4f, eff_update_frac=%.4f" % (
        float(W_argmax.norm()), eff), flush=True)

    # ST5: ARM_LATERAL_INHIBIT non-zero W; gamma applied (W differs from cf-RPE)
    gen5 = torch.Generator(device=_dev); gen5.manual_seed(7)
    W_lat, diag_lat = build_W_lateral_inhibit(
        E_st, idx_st, n_steps=10, batch=4, lr=0.5,
        gamma=LATERAL_INHIBIT_GAMMA, gen=gen5)
    assert float(W_lat.norm()) > 1e-6, "ST5 LATERAL_INHIBIT W is all-zero"
    # Different from cf-RPE under SAME seed (gen2 used 7 too) -- gamma term must change W
    diff_lat_cfrpe = float((W_lat - W_cfrpe).norm())
    assert diff_lat_cfrpe > 1e-4, "ST5 lateral-inhibit W identical to cfrpe (gamma=0 bug?)"
    print("[selftest] ST5 LATERAL_INHIBIT W norm=%.4f diff_vs_cfrpe=%.4f" % (
        float(W_lat.norm()), diff_lat_cfrpe), flush=True)

    # ST6: ARM_CHL non-zero W; phase-diff applied
    gen6 = torch.Generator(device=_dev); gen6.manual_seed(17)
    W_chl, diag_chl = build_W_chl(
        E_st, idx_st, n_steps=10, batch=4, lr=0.5,
        free_scale=CHL_FREE_PHASE_SCALE, gen=gen6)
    assert float(W_chl.norm()) > 1e-6, "ST6 CHL W is all-zero"
    print("[selftest] ST6 CHL W norm=%.4f" % float(W_chl.norm()), flush=True)

    # ST7: sparsify_bipolar produces +/-1 sparse vectors
    E_dense = torch.randn(4, 32, device=_dev)
    E_sparse = sparsify_bipolar_gpu(E_dense, f=0.25, seed=0)
    n_nonzero = int((E_sparse != 0).sum())
    expected_k = max(1, int(round(0.25 * 32)))
    assert n_nonzero == 4 * expected_k, "ST7 sparsify_bipolar count mismatch"
    print("[selftest] ST7 sparsify_bipolar_gpu OK (k=%d nonzero/row)" % expected_k, flush=True)

    # ST8: compute_logits shape + finite
    idx_held_st = torch.randint(0, n_v_st, (10,), device=_dev)
    logits8 = compute_logits_gpu(E_st, W_cfrpe, idx_held_st, recall_batch=5)
    assert logits8.shape == (10, n_v_st), "ST8 logits shape mismatch"
    assert np.all(np.isfinite(logits8)), "ST8 logits non-finite"
    print("[selftest] ST8 compute_logits shape=%s finite=True" % str(logits8.shape), flush=True)

    # ST9: joint_sweep finite + C7 compliance (0.0 not in LAMBDA_GRID)
    n_tok_st = 30
    n_v_sm = 6
    rng_jt = np.random.default_rng(99)
    logits_st = rng_jt.standard_normal((n_tok_st, n_v_sm)).astype(np.float32)
    nxt_st = rng_jt.integers(0, n_v_sm, size=n_tok_st).astype(np.int64)
    U_st = np.full(n_v_sm, 1.0 / n_v_sm, dtype=np.float32)
    U_log_st = np.log(U_st)
    nd = n_tok_st // 2
    assert 0.0 not in LAMBDA_GRID, "ST9 C7 violation: 0.0 in LAMBDA_GRID"
    jr = joint_sweep(logits_st[:nd], logits_st[nd:], U_log_st, nxt_st[:nd], nxt_st[nd:],
                      TEMP_GRID, LAMBDA_GRID, MRR_K)
    assert math.isfinite(jr["bpc_best"]) and math.isfinite(jr["top1_acc"]), \
        "ST9 joint_sweep finite check"
    assert "raw_top1_at_T1_L1" in jr, "ST9 raw_top1_at_T1_L1 missing"
    print("[selftest] ST9 joint_sweep OK (bpc=%.3f top1=%.4f)" % (
        jr["bpc_best"], jr["top1_acc"]), flush=True)

    # ST10: pre-reg constants are sane (HARD_PASS > MIDDLE_BAND >= HARD_FAIL_DECISIVE_TOL).
    # The drill defines HARD_FAIL_DECISIVE as |lift| <= 0.02 (i.e. all arms tightly clustered)
    # and MIDDLE_BAND as lift in [0.02, 0.05). The boundary at lift=0.02 is handled by
    # the verdict logic: all-within-tol check fires only when ALL non-cfrpe arms have
    # |lift| <= 0.02; MIDDLE_BAND fires when best_lift >= 0.02. So they're disjoint by
    # construction (cannot have all_within_tol AND best_lift >= 0.02 with multiple arms).
    assert HARD_FAIL_DECISIVE_TOL <= MIDDLE_BAND_TOP1_LIFT_FLOOR < HARD_PASS_TOP1_LIFT, \
        "ST10 band ordering violated"
    assert HP_TOP1_CV_MAX < MIDDLE_BAND_TOP1_CV_MAX, \
        "ST10 cv ordering violated"
    assert SANITY_CFRPE_TOP1_LIFT_MIN < SANITY_CFRPE_TOP1_LIFT_MAX, \
        "ST10 sanity range malformed"
    print("[selftest] ST10 pre-reg bands OK "
          "(HF<=%.2f < MB=[%.2f,%.2f) < HP>=%.2f; cv: HP<=%.2f < MB<=%.2f)" % (
              HARD_FAIL_DECISIVE_TOL, MIDDLE_BAND_TOP1_LIFT_FLOOR, HARD_PASS_TOP1_LIFT,
              HARD_PASS_TOP1_LIFT, HP_TOP1_CV_MAX, MIDDLE_BAND_TOP1_CV_MAX), flush=True)

    # ST11: top1_acc deterministic on simple known case (sanity for primary metric)
    logp_known = np.array([[0.1, 0.9, 0.0], [0.5, 0.4, 0.1], [0.2, 0.2, 0.6]])
    nxt_known = np.array([1, 0, 2])
    assert top1_acc(logp_known, nxt_known) == 1.0, "ST11 top1 deterministic check failed"
    print("[selftest] ST11 top1_acc deterministic = 1.000", flush=True)

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()

if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner (5 arms)
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()
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
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s mode=%s" % (
        seed, V, N_TRAIN, N_HELD, N_DIM, str(DEVICE), RUN_MODE), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d arm=ARM_UNIGRAM] bpc=%.3f top1=%.4f n_test=%d" % (
        seed, uni["bpc_unigram"], uni["top1_unigram"], uni["n_test"]), flush=True)

    by_arm: Dict[str, Dict] = {"ARM_UNIGRAM": uni}

    print("\n[seed=%d] building encoder (V=%d N_DIM=%d) on %s..." % (
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
    print("[seed=%d encoder] E built (%.1fs)" % (seed, t_enc), flush=True)

    E_used = _l2_normalize_t(sparsify_bipolar_gpu(E_base, f=SPARSE_BIPOLAR_F, seed=seed))
    del E_base
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()

    # Build eval split
    unk = 0
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    mask = (ctx_full != unk)
    nxt_eval = nxt_full[mask]
    valid_held_pos = np.where(mask)[0]
    n_eval = len(nxt_eval)
    if n_eval == 0:
        del E_used
        return {"seed": seed, "by_arm": by_arm, "V": V, "N_DIM": N_DIM,
                "N_TRAIN": N_TRAIN, "N_HELD": N_HELD, "run_mode": RUN_MODE,
                "elapsed_s_seed": round(time.time() - t_seed, 2),
                "device": str(DEVICE), "encoder_meta": encoder_meta}
    n_dev = n_eval // 2
    nxt_dev = nxt_eval[:n_dev]
    nxt_test = nxt_eval[n_dev:]

    idx_train_t = torch.from_numpy(idx_train).to(DEVICE)
    idx_held_t = torch.from_numpy(idx_held).to(DEVICE)

    def _eval_W_on_arm(arm_name: str, W: torch.Tensor, t_arm0: float,
                        extra_diag: Dict = None) -> None:
        logits = compute_logits_gpu(E_used, W, idx_held_t, RECALL_BATCH)
        raw_bpc = _raw_bpc_at_T1(logits, idx_held)
        if logits.shape[0] >= len(ctx_full):
            logits_ctx = logits[:len(ctx_full)]
        else:
            logits_ctx = logits
            mask_pos = np.array([p for p in valid_held_pos if p < logits_ctx.shape[0]],
                                  dtype=np.int64)
            logits_eval = logits_ctx[mask_pos]
            nxt_eval_local = nxt_full[mask_pos]
            ne = len(nxt_eval_local)
            ndev = ne // 2
            jr = joint_sweep(
                logits_eval[:ndev], logits_eval[ndev:], U_log,
                nxt_eval_local[:ndev], nxt_eval_local[ndev:],
                TEMP_GRID, LAMBDA_GRID, MRR_K,
            )
            jr["raw_bpc_at_T1_L1"] = round(raw_bpc, 4)
            jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
            if extra_diag:
                jr.update(extra_diag)
            by_arm[arm_name] = jr
            print("    [seed=%d arm=%s] top1=%.4f bpc_best=%.4f mrr=%.4f raw_T1L1_top1=%.4f" % (
                seed, arm_name, jr["top1_acc"], jr["bpc_best"], jr["mrr_at_10"],
                jr["raw_top1_at_T1_L1"]), flush=True)
            return
        logits_eval = logits_ctx[mask]
        jr = joint_sweep(
            logits_eval[:n_dev], logits_eval[n_dev:], U_log,
            nxt_dev, nxt_test, TEMP_GRID, LAMBDA_GRID, MRR_K,
        )
        jr["raw_bpc_at_T1_L1"] = round(raw_bpc, 4)
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        if extra_diag:
            jr.update(extra_diag)
        by_arm[arm_name] = jr
        print("    [seed=%d arm=%s] top1=%.4f bpc_best=%.4f mrr=%.4f raw_T1L1_top1=%.4f" % (
            seed, arm_name, jr["top1_acc"], jr["bpc_best"], jr["mrr_at_10"],
            jr["raw_top1_at_T1_L1"]), flush=True)

    # ARM_CFRPE_REFERENCE
    t_arm = time.time()
    print("\n  [seed=%d arm=ARM_CFRPE_REFERENCE] building W (n_steps=%d)..." % (
        seed, N_STEPS_PLASTIC), flush=True)
    gen_cfrpe = torch.Generator(device=DEVICE); gen_cfrpe.manual_seed(seed * 10007 + 1 * 31337)
    try:
        W_cfrpe, diag_cfrpe = build_W_cfrpe_reference(
            E_used, idx_train_t, n_steps=N_STEPS_PLASTIC, batch=INGEST_BATCH,
            lr=CFRPE_LR, gen=gen_cfrpe)
        _eval_W_on_arm("ARM_CFRPE_REFERENCE", W_cfrpe, t_arm, extra_diag=diag_cfrpe)
        del W_cfrpe
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=ARM_CFRPE_REFERENCE] COMPUTE FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_CFRPE_REFERENCE"] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
            "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "raw_top1_at_T1_L1": float("nan"),
            "elapsed_s_arm": round(time.time() - t_arm, 2),
        }

    # ARM_BCPNN
    t_arm = time.time()
    print("\n  [seed=%d arm=ARM_BCPNN] building W (n_steps=%d, ema_alpha=%.4f)..." % (
        seed, N_STEPS_PLASTIC, BCPNN_EMA_ALPHA), flush=True)
    gen_bcpnn = torch.Generator(device=DEVICE); gen_bcpnn.manual_seed(seed * 10007 + 2 * 31337)
    try:
        W_bcpnn, diag_bcpnn = build_W_bcpnn(
            E_used, idx_train_t, n_steps=N_STEPS_PLASTIC, batch=INGEST_BATCH,
            ema_alpha=BCPNN_EMA_ALPHA, eps=BCPNN_EPS, gen=gen_bcpnn)
        _eval_W_on_arm("ARM_BCPNN", W_bcpnn, t_arm, extra_diag=diag_bcpnn)
        del W_bcpnn
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=ARM_BCPNN] COMPUTE FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_BCPNN"] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
            "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "raw_top1_at_T1_L1": float("nan"),
            "elapsed_s_arm": round(time.time() - t_arm, 2),
        }

    # ARM_ARGMAX_DELTA
    t_arm = time.time()
    print("\n  [seed=%d arm=ARM_ARGMAX_DELTA] building W (n_steps=%d, margin=%.4f)..." % (
        seed, N_STEPS_PLASTIC, ARGMAX_MARGIN_THRESHOLD), flush=True)
    gen_argmax = torch.Generator(device=DEVICE); gen_argmax.manual_seed(seed * 10007 + 3 * 31337)
    try:
        W_argmax, diag_argmax = build_W_argmax_delta(
            E_used, idx_train_t, n_steps=N_STEPS_PLASTIC, batch=INGEST_BATCH,
            lr=CFRPE_LR, margin_threshold=ARGMAX_MARGIN_THRESHOLD, gen=gen_argmax)
        _eval_W_on_arm("ARM_ARGMAX_DELTA", W_argmax, t_arm, extra_diag=diag_argmax)
        del W_argmax
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=ARM_ARGMAX_DELTA] COMPUTE FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_ARGMAX_DELTA"] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
            "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "raw_top1_at_T1_L1": float("nan"),
            "elapsed_s_arm": round(time.time() - t_arm, 2),
        }

    # ARM_LATERAL_INHIBIT
    t_arm = time.time()
    print("\n  [seed=%d arm=ARM_LATERAL_INHIBIT] building W (n_steps=%d, gamma=%.4f)..." % (
        seed, N_STEPS_PLASTIC, LATERAL_INHIBIT_GAMMA), flush=True)
    gen_lat = torch.Generator(device=DEVICE); gen_lat.manual_seed(seed * 10007 + 4 * 31337)
    try:
        W_lat, diag_lat = build_W_lateral_inhibit(
            E_used, idx_train_t, n_steps=N_STEPS_PLASTIC, batch=INGEST_BATCH,
            lr=CFRPE_LR, gamma=LATERAL_INHIBIT_GAMMA, gen=gen_lat)
        _eval_W_on_arm("ARM_LATERAL_INHIBIT", W_lat, t_arm, extra_diag=diag_lat)
        del W_lat
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=ARM_LATERAL_INHIBIT] COMPUTE FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_LATERAL_INHIBIT"] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
            "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "raw_top1_at_T1_L1": float("nan"),
            "elapsed_s_arm": round(time.time() - t_arm, 2),
        }

    # ARM_CHL
    t_arm = time.time()
    print("\n  [seed=%d arm=ARM_CHL] building W (n_steps=%d, free_scale=%.2f)..." % (
        seed, N_STEPS_PLASTIC, CHL_FREE_PHASE_SCALE), flush=True)
    gen_chl = torch.Generator(device=DEVICE); gen_chl.manual_seed(seed * 10007 + 5 * 31337)
    try:
        W_chl, diag_chl = build_W_chl(
            E_used, idx_train_t, n_steps=N_STEPS_PLASTIC, batch=INGEST_BATCH,
            lr=CFRPE_LR, free_scale=CHL_FREE_PHASE_SCALE, gen=gen_chl)
        _eval_W_on_arm("ARM_CHL", W_chl, t_arm, extra_diag=diag_chl)
        del W_chl
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        print("    [seed=%d arm=ARM_CHL] COMPUTE FAIL: %s" % (seed, err), flush=True)
        by_arm["ARM_CHL"] = {
            "compute_failed": True, "compute_error": err,
            "bpc_best": float("inf"), "top1_acc": float("nan"),
            "mrr_at_10": float("nan"), "best_T_for_bpc": float("nan"),
            "best_lambda_for_bpc": float("nan"), "raw_bpc_at_T1_L1": float("inf"),
            "raw_top1_at_T1_L1": float("nan"),
            "elapsed_s_arm": round(time.time() - t_arm, 2),
        }

    del E_used
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
        "N_STEPS_PLASTIC": N_STEPS_PLASTIC,
        "run_mode": RUN_MODE,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
    }


# ============================================================================
# Verdict (per pre-reg HARD bands; Fix #28 per-arm top1 primary metric)
# ============================================================================

def compute_verdict(units: List[Dict]) -> tuple:
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}

    # ARM_UNIGRAM aggregation
    uni_top1 = [u["by_arm"].get("ARM_UNIGRAM", {}).get("top1_unigram", float("nan"))
                 for u in units]
    uni_bpc = [u["by_arm"].get("ARM_UNIGRAM", {}).get("bpc_unigram", float("nan"))
                for u in units]
    by_arm_agg["ARM_UNIGRAM"] = {
        "top1_mean": round(float(np.mean(uni_top1)), 4),
        "bpc_mean": round(float(np.mean(uni_bpc)), 4),
    }
    unigram_top1 = by_arm_agg["ARM_UNIGRAM"]["top1_mean"]

    def _agg_arm(arm: str) -> Dict:
        seeds_failed = [u["by_arm"].get(arm, {}).get("compute_failed", False) for u in units]
        valid = [(not cf) and math.isfinite(u["by_arm"].get(arm, {}).get("top1_acc", float("nan")))
                 for cf, u in zip(seeds_failed, units)]
        n_failed = int(sum(seeds_failed))
        valid_units = [u for ok, u in zip(valid, units) if ok]
        if not valid_units:
            return {"top1_acc_mean": float("nan"), "top1_acc_std": float("nan"),
                    "top1_acc_cv": float("nan"),
                    "bpc_best_mean": float("inf"), "mrr_at_10_mean": float("nan"),
                    "n_valid_seeds": 0, "n_compute_failed": n_failed, "all_seeds_failed": True}
        top1_v = [u["by_arm"][arm]["top1_acc"] for u in valid_units]
        bpc_v = [u["by_arm"][arm]["bpc_best"] for u in valid_units]
        mrr_v = [u["by_arm"][arm]["mrr_at_10"] for u in valid_units]
        raw_top1_v = [u["by_arm"][arm].get("raw_top1_at_T1_L1", float("nan"))
                       for u in valid_units]
        raw_top1_finite = [x for x in raw_top1_v if math.isfinite(x)]
        t_mean = float(np.mean(top1_v))
        t_std = float(np.std(top1_v))
        return {
            "top1_acc_mean": round(t_mean, 4),
            "top1_acc_std": round(t_std, 4),
            "top1_acc_cv": round(t_std / max(abs(t_mean), 1e-6), 4),
            "bpc_best_mean": round(float(np.mean(bpc_v)), 4),
            "bpc_best_std": round(float(np.std(bpc_v)), 4),
            "mrr_at_10_mean": round(float(np.mean(mrr_v)), 4),
            "mrr_at_10_std": round(float(np.std(mrr_v)), 4),
            "raw_top1_at_T1_L1_mean": (round(float(np.mean(raw_top1_finite)), 4)
                                         if raw_top1_finite else float("nan")),
            "n_valid_seeds": int(len(valid_units)),
            "n_compute_failed": n_failed,
            "all_seeds_failed": False,
        }

    for arm in ARMS:
        by_arm_agg[arm] = _agg_arm(arm)

    cfrpe_top1 = by_arm_agg["ARM_CFRPE_REFERENCE"].get("top1_acc_mean", float("nan"))
    cfrpe_failed = by_arm_agg["ARM_CFRPE_REFERENCE"].get("all_seeds_failed", True)

    # Lifts vs cf-RPE reference (positive = better top1 than cf-RPE)
    lifts_top1: Dict[str, float] = {}
    for arm in NON_CFRPE_ARMS:
        a_top1 = by_arm_agg[arm].get("top1_acc_mean", float("nan"))
        if math.isfinite(a_top1) and math.isfinite(cfrpe_top1):
            lifts_top1[arm] = a_top1 - cfrpe_top1
        else:
            lifts_top1[arm] = float("nan")

    # Sanity (cf-RPE provenance check): cfrpe lift over unigram in [SANITY_MIN, SANITY_MAX]
    cfrpe_vs_unigram_top1 = (cfrpe_top1 - unigram_top1) if (
        math.isfinite(cfrpe_top1) and math.isfinite(unigram_top1)) else float("nan")
    sanity_ok = (
        math.isfinite(cfrpe_vs_unigram_top1) and
        SANITY_CFRPE_TOP1_LIFT_MIN <= cfrpe_vs_unigram_top1 <= SANITY_CFRPE_TOP1_LIFT_MAX
    )

    # Best non-cf-RPE arm (largest absolute top1 lift over cf-RPE)
    best_arm = None
    best_lift = float("-inf")
    best_arm_cv = float("nan")
    for arm in NON_CFRPE_ARMS:
        lift = lifts_top1.get(arm, float("nan"))
        if math.isfinite(lift) and lift > best_lift:
            best_lift = lift
            best_arm = arm
            best_arm_cv = by_arm_agg[arm].get("top1_acc_cv", float("nan"))

    # All-within-tol check (HARD_FAIL_DECISIVE condition)
    finite_lifts = [v for v in lifts_top1.values() if math.isfinite(v)]
    all_within_tol = bool(
        len(finite_lifts) == len(NON_CFRPE_ARMS) and
        all(abs(v) <= HARD_FAIL_DECISIVE_TOL for v in finite_lifts)
    )

    arms_summary_parts = []
    for arm in ARMS:
        agg = by_arm_agg[arm]
        if agg.get("all_seeds_failed", False):
            arms_summary_parts.append("%s=FAILED" % arm)
        else:
            arms_summary_parts.append("%s=top1%.4f(cv%.4f bpc%.3f)" % (
                arm, agg.get("top1_acc_mean", float("nan")),
                agg.get("top1_acc_cv", float("nan")),
                agg.get("bpc_best_mean", float("nan"))))
    arms_summary = " | ".join(arms_summary_parts)
    arms_summary += " | best_non_cfrpe=%s lift=%.4f cv=%.4f" % (
        best_arm if best_arm else "none",
        best_lift if math.isfinite(best_lift) else -1.0,
        best_arm_cv if math.isfinite(best_arm_cv) else -1.0)

    detail = {
        "by_arm_agg": by_arm_agg,
        "lifts_top1_vs_cfrpe": {k: round(v, 4) if math.isfinite(v) else None
                                  for k, v in lifts_top1.items()},
        "best_non_cfrpe_arm": best_arm,
        "best_non_cfrpe_lift": round(best_lift, 4) if math.isfinite(best_lift) else None,
        "best_non_cfrpe_cv": round(best_arm_cv, 4) if math.isfinite(best_arm_cv) else None,
        "cfrpe_reference_top1": round(cfrpe_top1, 4) if math.isfinite(cfrpe_top1) else None,
        "unigram_top1": round(unigram_top1, 4) if math.isfinite(unigram_top1) else None,
        "cfrpe_lift_over_unigram": round(cfrpe_vs_unigram_top1, 4) if math.isfinite(cfrpe_vs_unigram_top1) else None,
        "sanity_ok": bool(sanity_ok),
        "all_within_tol": bool(all_within_tol),
        "hard_pass_lift_bar": HARD_PASS_TOP1_LIFT,
        "middle_band_lift_floor": MIDDLE_BAND_TOP1_LIFT_FLOOR,
        "hard_fail_decisive_tol": HARD_FAIL_DECISIVE_TOL,
        "hp_top1_cv_max": HP_TOP1_CV_MAX,
        "middle_band_top1_cv_max": MIDDLE_BAND_TOP1_CV_MAX,
        "sanity_cfrpe_lift_min": SANITY_CFRPE_TOP1_LIFT_MIN,
        "sanity_cfrpe_lift_max": SANITY_CFRPE_TOP1_LIFT_MAX,
        "n_seeds": len(units),
        "n_steps_plastic": N_STEPS_PLASTIC,
        "rule_classes": {
            "ARM_CFRPE_REFERENCE": "cfrpe_delta_rule_global_lr",
            "ARM_BCPNN": "bcpnn_log_odds_ema_traces_signed",
            "ARM_ARGMAX_DELTA": "argmax_delta_gated_margin",
            "ARM_LATERAL_INHIBIT": "lateral_inhibit_anti_hebbian_runner_up",
            "ARM_CHL": "chl_clamped_minus_free",
        },
        "knobs": {
            "CFRPE_LR": CFRPE_LR,
            "INGEST_BATCH": INGEST_BATCH,
            "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
            "BCPNN_EMA_ALPHA": BCPNN_EMA_ALPHA,
            "BCPNN_EPS": BCPNN_EPS,
            "ARGMAX_MARGIN_THRESHOLD": ARGMAX_MARGIN_THRESHOLD,
            "LATERAL_INHIBIT_GAMMA": LATERAL_INHIBIT_GAMMA,
            "CHL_FREE_PHASE_SCALE": CHL_FREE_PHASE_SCALE,
        },
        "honest_scope": (
            "5-arm CPU smoke at N_DIM=2048 V=2000 N_TRAIN=20k 3 seeds testing argmax-targeted "
            "plasticity rules vs cf-RPE reference at SAME cosine-NN readout. PRIMARY METRIC: "
            "top1_acc (NOT BPC; Fix #28). HARD_PASS: any non-cfrpe lift >= %.2f abs over cfrpe "
            "AND cv <= %.2f. MIDDLE_BAND: lift in [%.2f, %.2f) OR cv in (%.2f, %.2f]. "
            "HARD_FAIL_DECISIVE: ALL non-cfrpe |lift| <= %.2f (plasticity-as-top1-lever "
            "closed at smoke; readout dominates). Sanity: cfrpe_top1 - unigram_top1 in [%.2f, %.2f]. "
            "WHAT_THIS_DOES_NOT_SHOW: smoke-scale (HARD_PASS triggers separate N=8192/N=100k "
            "full dispatch). No n1_v3 composition (separate cell post-HARD_PASS). "
            "4-of-many plasticity families chosen per drill mechanism analysis." % (
                HARD_PASS_TOP1_LIFT, HP_TOP1_CV_MAX,
                MIDDLE_BAND_TOP1_LIFT_FLOOR, HARD_PASS_TOP1_LIFT,
                HP_TOP1_CV_MAX, MIDDLE_BAND_TOP1_CV_MAX,
                HARD_FAIL_DECISIVE_TOL,
                SANITY_CFRPE_TOP1_LIFT_MIN, SANITY_CFRPE_TOP1_LIFT_MAX)),
        "cites": [
            "preregs/2026-06-24_substrate_top1_targeted_plasticity_4arm_smoke_v1.md",
            "notes/research_top1_targeted_plasticity_2x_drill_2026-06-24.md",
            "notes/skunkworks_LANDED_VET_cfrpe_per_token_adaptive_lr_v1_MEASURED_MECHANISM_2026-06-24.md",
            "experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py",
        ],
    }

    # Gate 1: cf-RPE reference all-seeds-failed
    if cfrpe_failed:
        return ("HARD_FAIL",
                "HARD_FAIL: ARM_CFRPE_REFERENCE all seeds failed. Cannot compute lifts. %s" % arms_summary,
                detail)

    # Gate 2: sanity (full mode only; provenance check on cf-RPE)
    if RUN_MODE == "full" and not sanity_ok:
        return ("HARD_FAIL",
                ("SANITY_FAIL: cfrpe_top1 - unigram_top1 = %.4f, expected in [%.2f, %.2f]. "
                 "cf-RPE provenance check failed -- rule-targeting question NOT classifiable. "
                 "Diagnosis needed. %s" % (
                     cfrpe_vs_unigram_top1, SANITY_CFRPE_TOP1_LIFT_MIN,
                     SANITY_CFRPE_TOP1_LIFT_MAX, arms_summary)),
                detail)

    # Gate 3: best non-cf-RPE arm failed entirely
    if best_arm is None or not math.isfinite(best_lift):
        return ("HARD_FAIL",
                ("HARD_FAIL_INSTABILITY: all non-cfrpe arms failed; cannot evaluate "
                 "rule-targeting cap. %s" % arms_summary),
                detail)

    # Gate 4: HARD_PASS condition (lift >= bar AND cv tight)
    if best_lift >= HARD_PASS_TOP1_LIFT and math.isfinite(best_arm_cv) and best_arm_cv <= HP_TOP1_CV_MAX:
        msg = ("HARD_PASS: best_non_cfrpe=%s top1 lift=%.4f >= %.2f abs over cf-RPE "
               "AND cv=%.4f <= %.2f. cf-RPE family +12%% top1 ceiling BROKEN. "
               "Escalate: route to Research for FULL N=8192/N=100k dispatch on winning arm. "
               "%s" % (
                   best_arm, best_lift, HARD_PASS_TOP1_LIFT,
                   best_arm_cv, HP_TOP1_CV_MAX, arms_summary))
        return ("HARD_PASS", msg, detail)

    # Gate 5: MIDDLE_BAND (lift in band OR cv in band)
    cv_in_mb = (math.isfinite(best_arm_cv)
                 and HP_TOP1_CV_MAX < best_arm_cv <= MIDDLE_BAND_TOP1_CV_MAX
                 and best_lift >= MIDDLE_BAND_TOP1_LIFT_FLOOR)
    lift_in_mb = (MIDDLE_BAND_TOP1_LIFT_FLOOR <= best_lift < HARD_PASS_TOP1_LIFT)
    if cv_in_mb or lift_in_mb:
        reason_parts = []
        if lift_in_mb:
            reason_parts.append("lift=%.4f in [%.2f,%.2f)" % (
                best_lift, MIDDLE_BAND_TOP1_LIFT_FLOOR, HARD_PASS_TOP1_LIFT))
        if cv_in_mb:
            reason_parts.append("cv=%.4f in (%.2f,%.2f]" % (
                best_arm_cv, HP_TOP1_CV_MAX, MIDDLE_BAND_TOP1_CV_MAX))
        reason = " AND ".join(reason_parts)
        msg = ("MIDDLE_BAND: best_non_cfrpe=%s %s (weak signal). "
               "Per drill: do NOT route to USER between MIDDLE_BANDs; design harder "
               "discriminator cell. %s" % (best_arm, reason, arms_summary))
        return ("MIDDLE_BAND", msg, detail)

    # Gate 6: HARD_FAIL_DECISIVE (all within +/- tol)
    if all_within_tol:
        msg = ("HARD_FAIL_DECISIVE: ALL non-cf-RPE arms within +/-%.2f abs of cf-RPE. "
               "Plasticity-as-top1-lever DECISIVELY CLOSED at smoke. Substrate-product "
               "implication: top1 chain-grade lever IS readout, not plasticity. "
               "Route to Research: revival drill + readout-axis focus (n1_v3 V_C sweep). "
               "%s" % (HARD_FAIL_DECISIVE_TOL, arms_summary))
        return ("HARD_FAIL", msg, detail)

    # Gate 7: generic HARD_FAIL (best lift below middle-band floor but not all within tol)
    msg = ("HARD_FAIL: best_non_cfrpe=%s lift=%.4f below middle-band floor %.2f "
           "but not all-within-tol (some arms outside +/-%.2f). %s" % (
               best_arm, best_lift, MIDDLE_BAND_TOP1_LIFT_FLOOR,
               HARD_FAIL_DECISIVE_TOL, arms_summary))
    return ("HARD_FAIL", msg, detail)


# ============================================================================
# Main loop with per-seed checkpoint
# ============================================================================

print("[config] anchor=%s N_DIM=%d V_CAP=%d N_TRAIN=%d mode=%s seeds=%s "
      "N_STEPS_PLASTIC=%d device=%s" % (
          ANCHOR_NAME, N_DIM, VOCAB_CAP, N_TRAIN, RUN_MODE, SEEDS, N_STEPS_PLASTIC,
          str(DEVICE)), flush=True)

if DEVICE.type == "cuda":
    print("[gpu] %s" % torch.cuda.get_device_name(0), flush=True)
else:
    print("[device] CPU (no CUDA available; routed CPU per drill)", flush=True)

out_dir = get_output_dir(ANCHOR_NAME)

from experiments._seed_checkpoint import resumable_seeds as _resumable_seeds
try:
    done_seeds, remaining_seeds = _resumable_seeds(SEEDS, out_dir)
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

# Summary string required by queue_add.py REQUIRED_FIELDS validator
summary = ("anchor=%s mode=%s n_seeds=%d N_DIM=%d V=%d N_TRAIN=%d N_STEPS=%d arms=%s "
           "verdict=%s") % (
    ANCHOR_NAME, RUN_MODE, len(SEEDS), N_DIM, VOCAB_CAP, N_TRAIN, N_STEPS_PLASTIC,
    ",".join(ARMS), verdict)

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
    "N_STEPS_PLASTIC": N_STEPS_PLASTIC,
    "CFRPE_LR": CFRPE_LR,
    "INGEST_BATCH": INGEST_BATCH,
    "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
    "LAMBDA_GRID": LAMBDA_GRID,
    "TEMP_GRID": TEMP_GRID,
    "BCPNN_EMA_ALPHA": BCPNN_EMA_ALPHA,
    "BCPNN_EPS": BCPNN_EPS,
    "ARGMAX_MARGIN_THRESHOLD": ARGMAX_MARGIN_THRESHOLD,
    "LATERAL_INHIBIT_GAMMA": LATERAL_INHIBIT_GAMMA,
    "CHL_FREE_PHASE_SCALE": CHL_FREE_PHASE_SCALE,
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
