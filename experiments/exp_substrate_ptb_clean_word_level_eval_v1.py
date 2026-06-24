"""substrate_ptb_clean_word_level_eval_v1 -- FIRST apples-to-apples PTB word-level substrate-as-LM evaluation.

USER directive 2026-06-24: "isn't text8 and pythia biased in that we aren't using a
standard encoding or looking at just words?"

Honest re-cast: text8 is a stripped 100MB character corpus (lowercase, no punct,
no <eos>) -- not "real words" in a canonical NLP sense. Pythia residuals are
transformer-internal representations -- not "the corpus" either. Penn Treebank
word-level (Mikolov split; 929k train / 73k val / 82k test tokens; V=10000 incl
<unk> <eos>) is the canonical NLP word-level LM benchmark since Mikolov 2010.

This cell is the first apples-to-apples PTB substrate-as-LM evaluation. All arms
operate on the IDENTICAL PTB corpus + IDENTICAL word vocabulary + IDENTICAL
held-out split. Per the apples-to-apples 2x drill 2026-06-24:
  - Lane 2 (intra-corpus substrate-vs-substrate ablation + cross-paradigm
    word-bigram baseline as explicit two-paradigm tag).
  - CONFOUND_AUDIT tuple stamped in CONFIG_VERSION + corpus_provenance.
  - INTRA_LANE_DELTA arm: each substrate variant changes ONE knob from the
    K=1 cf-RPE base (K=1 vs K=2 banks; cf-RPE vs adaptive cf-RPE).
  - Corpus provenance tag: "PTB-word-level (Mikolov split)".

Five arms (apples-to-apples; SAME PTB corpus + SAME vocab + SAME split):
  ARM_B1_UNIGRAM
      Analytic word-unigram floor (alpha-smoothed). Sanity floor (well-known
      PTB unigram BPW ~10-11 bits/word given V=10000, frequency-skewed Zipf).
  ARM_B2_WORD_BIGRAM
      Add-alpha smoothed word-bigram LM (alpha=0.001 per v2 fix today). The
      REAL LM threshold; canonical PTB word-bigram lands ~5.6-6.0 BPW per
      lit (Mikolov 2010; Brown & Pereira; Chen & Goodman).
  ARM_S_CFRPE_BASE
      Substrate K=1 with cf-RPE delta-rule. word2vec-projected encoder ->
      sparse-bipolar f=0.05 -> N_DIM=8192. Rank-1 cf-RPE W. Single bank.
  ARM_S_K2_CFRPE
      Substrate K=2 banks (4096 per bank) with cf-RPE per bank; gate-weighted
      readout. INTRA_LANE_DELTA arm vs ARM_S_CFRPE_BASE (only the bank-count
      knob changes; everything else identical).
  ARM_S_ADAPTIVE_CFRPE
      Substrate K=1 with per-token adaptive cf-RPE (median-normalized LR
      per-sample). INTRA_LANE_DELTA arm vs ARM_S_CFRPE_BASE (only the
      cf-RPE rule changes; everything else identical).

Pre-registered HARD bands (locked before dispatch):
  Sanity rails:
    ARM_B1_UNIGRAM BPW in canonical PTB unigram range [9.0, 11.0] -- well-known.
    ARM_B2_WORD_BIGRAM BPW in [5.20, 6.80] -- canonical PTB word-bigram.
    BOTH out-of-range -> HARD_FAIL (baseline mis-spec).

  HARD_PASS_CLEAN_SUBSTRATE_VIABLE:
    ANY substrate arm BPW <= ARM_B2_WORD_BIGRAM BPW - 0.30 AND cv <= 0.05
    AND substrate-only-decode gate (n_llm_calls == 0).

  CHAIN_GRADE_BONUS:
    ANY substrate arm BPW <= 4.5 (approaching canonical LSTM-baseline territory).

  MIDDLE_BAND:
    ANY substrate arm BPW in (ARM_B2_WORD_BIGRAM BPW - 0.30,
                                ARM_B2_WORD_BIGRAM BPW]. Partial signal; substrate
    nudges/matches word-bigram on PTB but doesn't clear the +0.30 bar.

  HARD_FAIL_DECISIVE:
    ALL substrate arm BPW means > ARM_B2_WORD_BIGRAM BPW. Substrate-as-LM
    fails the canonical NLP word-level baseline on clean PTB -- the ceiling
    is real, not text8-bias artifact.

  HARD_FAIL (other):
    substrate-only-decode gate violated (n_llm_calls > 0).

DISCRIMINATING REGIME (apples-to-apples):
  - Lane 2 declaration: intra-corpus substrate-vs-substrate + tagged word-
    bigram cross-paradigm baseline.
  - 3-arm substrate discriminator: K=1 cf-RPE vs K=2 cf-RPE vs K=1 adaptive
    cf-RPE; if all three cluster within +/- 0.05 BPW of each other, the
    mechanism levers are NULL on PTB. If one clearly leads, that knob is the
    load-bearing factor on PTB.

WHY THIS IS LOAD-BEARING:
  This is the FIRST proper apples-to-apples substrate-as-LM evaluation on a
  canonical NLP corpus. If substrate clears word-bigram on PTB, the
  substrate-as-LM story is real (not text8-bias artifact). If substrate
  doesn't clear word-bigram even on clean PTB, the substrate-as-LM ceiling
  is real (not text8-artifact).

GPU dispatch per USER 2026-06-22 Fix #24 -- torch.cuda required; idle GPU
host gets matmul-bound 5-arm sweep at N_DIM=8192.

FORMULA SELF-TESTS:
  T1: PTB loader -- cached or downloads; canonical token counts match.
  T2: word-bigram add-alpha row-stochastic + v2-fix alpha=0.001 monotonic on
      planted toy.
  T3: K=1 cf-RPE delta-rule shrinks error in one step (non-increase under
      positive eta).
  T4: K=2 gate-weighted bank construction returns shape-correct W_banks.
  T5: per-token adaptive cf-RPE: high-error sample receives larger LR (after
      median-normalization).
  T6: BPC from planted logp reproduces analytic unigram BPC at lambda=0.
  T7: Sparse-bipolar primitive yields exactly k=int(f*dim) non-zero entries
      per row, all in {-1, +1}.
  T8: HRR bind: irfft(rfft(A) * rfft(B)) preserves shape, non-zero norm.
  T9: verdict bands -- HARD_PASS / MIDDLE / HARD_FAIL_DECISIVE classification
      on planted arm data.
  T10: _LLM_CALL_COUNTER zero.

ASCII-only. GPU torch.cuda. Per-seed checkpoint via _seed_checkpoint. atexit
synthesizer. Substrate-only-decode gate.

cites:
  preregs/2026-06-24_substrate_ptb_clean_word_level_eval_v1.md
  notes/research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24.md
  experiments/exp_fair_harness_substrate_as_lm_v1.py (torch+cuda fair_harness)
  experiments/exp_substrate_sequence_modeling_production_v2.py (alpha=0.001 fix)
  experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py (K=2 banks)
  experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py (adaptive cf-RPE)
  Mikolov 2010 PTB split (raw.githubusercontent.com/wojzaremba/lstm)
  USER_2026-06-24_text8_pythia_biased_use_PTB
  USER_2026-06-22_Fix24_GPU_dispatch_must_use_GPU
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
import urllib.request
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

ANCHOR_NAME = "substrate_ptb_clean_word_level_eval_v1"
PTB_CACHE_DIR = REPO / "data" / "ptb_cache"
PTB_TRAIN = PTB_CACHE_DIR / "ptb.train.txt"
PTB_VALID = PTB_CACHE_DIR / "ptb.valid.txt"
PTB_TEST = PTB_CACHE_DIR / "ptb.test.txt"
PTB_BASE_URL = "https://raw.githubusercontent.com/wojzaremba/lstm/master/data"
GENSIM_CACHE_DIR = str(REPO / "data" / "gensim_cache_v2")
os.environ.setdefault("GENSIM_DATA_DIR", GENSIM_CACHE_DIR)

# Substrate-only-decode gate (Skunkworks structural blocker)
_LLM_CALL_COUNTER = [0]

# Pre-reg HARD bands (locked before dispatch)
UNIGRAM_BPW_MIN = 9.0           # PTB V=10000 unigram lower bound (Zipf-skewed)
UNIGRAM_BPW_MAX = 11.0          # PTB unigram upper bound
BIGRAM_BPW_MIN = 5.20            # canonical PTB word-bigram lower
BIGRAM_BPW_MAX = 6.80            # canonical PTB word-bigram upper
HP_BPW_MARGIN = 0.30             # substrate clears bigram by >= 0.30 BPW
CHAIN_GRADE_BPW = 4.5            # substrate <= 4.5 = chain-grade-bonus (LSTM territory)
HP_CV_MAX = 0.05                 # cross-seed cv ceiling for HP

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
TORCH_DTYPE = torch.float32

# Joint (T, lambda) sweep (mirrors fair_harness; lambda interp vs unigram)
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.05, 0.1, 0.3, 0.5, 0.7, 1.0]   # C7: excludes 0.0
MRR_K = 10

# Sparse-bipolar f
SPARSE_BIPOLAR_F = 0.05

# Word-bigram smoothing (v2 fix: alpha=0.001; smoothing-mass V*alpha=10 at V=10000)
BIGRAM_ALPHA = 0.001

# cf-RPE delta-rule LR + steps
CFRPE_LR = 0.5
CFRPE_BATCH = 64
CFRPE_N_STEPS_FULL = 5000
CFRPE_N_STEPS_SMOKE = 200

# Adaptive cf-RPE clamp
ADAPT_LR_FLOOR = 0.25
ADAPT_LR_CEIL = 4.0

# K=2 bank gate temperature
K2_GATE_TEMP = 1.0

# Config (FULL = production GPU; substrate at N_DIM=8192 matmul on PTB)
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_DIM_TOTAL = 8192
    INGEST_CHUNK = 4096
    RECALL_BATCH = 256
    PTB_TRAIN_TOKENS_CAP = 0      # 0 means use full ~887k tokens
    PTB_HELD_FROM_VALID = True    # use ptb.valid.txt for held (canonical eval)
    CFRPE_N_STEPS = CFRPE_N_STEPS_FULL
else:
    # Smoke: must finish under 180s on laptop CPU/GPU
    SEEDS = [0]
    N_DIM_TOTAL = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
    PTB_TRAIN_TOKENS_CAP = 3000   # truncate train for smoke speed
    PTB_HELD_FROM_VALID = False   # smoke uses train-internal held split
    CFRPE_N_STEPS = CFRPE_N_STEPS_SMOKE

K_BANKS = 2
N_DIM_PER_BANK = N_DIM_TOTAL // K_BANKS
PRETRAIN_DIM = 300

ARMS = [
    "ARM_B1_UNIGRAM",
    "ARM_B2_WORD_BIGRAM",
    "ARM_S_CFRPE_BASE",
    "ARM_S_K2_CFRPE",
    "ARM_S_ADAPTIVE_CFRPE",
]
SUBSTRATE_ARMS = [
    "ARM_S_CFRPE_BASE",
    "ARM_S_K2_CFRPE",
    "ARM_S_ADAPTIVE_CFRPE",
]
WORD2VEC_MODEL = "word2vec-google-news-300"

# CONFOUND_AUDIT tuple (apples-to-apples 2x drill standing discipline)
CONFOUND_AUDIT_TUPLE = (
    "(corpus=PTB-word-level-Mikolov, encoder_paradigm=word2vec_sparse_bipolar_f0.05, "
    "N_DIM=%d, vocab=PTB-V10000, metric_primary=BPW, "
    "baseline_paradigm=word-bigram-add-alpha=0.001, "
    "lane=2_intra_corpus_substrate_vs_substrate_plus_tagged_bigram)"
) % N_DIM_TOTAL

CONFIG_VERSION = (
    "substrate_ptb_clean_word_level_eval_v1; N_DIM=%d K_BANKS=%d N_DIM_PER_BANK=%d "
    "ptb_train_cap=%d held_from_valid=%s arms=%s seeds=%s mode=%s temps=%s "
    "lambdas=%s sparse_f=%.3f cfrpe_lr=%.3f cfrpe_n_steps=%d cfrpe_batch=%d "
    "k2_gate_temp=%.2f adapt_floor=%.2f adapt_ceil=%.2f bigram_alpha=%.4f "
    "MRR_K=%d device=%s | "
    "bands HP_margin=%.2f chain_grade=%.2f bigram_min=%.2f bigram_max=%.2f "
    "unigram_min=%.2f unigram_max=%.2f cv_max=%.2f | CONFOUND_AUDIT=%s"
) % (
    N_DIM_TOTAL, K_BANKS, N_DIM_PER_BANK, PTB_TRAIN_TOKENS_CAP,
    str(PTB_HELD_FROM_VALID), ARMS, SEEDS, RUN_MODE, TEMP_GRID, LAMBDA_GRID,
    SPARSE_BIPOLAR_F, CFRPE_LR, CFRPE_N_STEPS, CFRPE_BATCH, K2_GATE_TEMP,
    ADAPT_LR_FLOOR, ADAPT_LR_CEIL, BIGRAM_ALPHA, MRR_K, str(DEVICE),
    HP_BPW_MARGIN, CHAIN_GRADE_BPW, BIGRAM_BPW_MIN, BIGRAM_BPW_MAX,
    UNIGRAM_BPW_MIN, UNIGRAM_BPW_MAX, HP_CV_MAX, CONFOUND_AUDIT_TUPLE,
)


# ============================================================================
# PTB loader (Mikolov split; tokens include <unk> and <eos> at line breaks)
# ============================================================================

def _ensure_ptb_cache() -> None:
    PTB_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    for split in ("train", "valid", "test"):
        dst = PTB_CACHE_DIR / ("ptb.%s.txt" % split)
        if dst.exists() and dst.stat().st_size > 1000:
            continue
        url = "%s/ptb.%s.txt" % (PTB_BASE_URL, split)
        print("[ptb] downloading %s -> %s" % (url, dst), flush=True)
        with urllib.request.urlopen(url, timeout=60) as r:
            dst.write_bytes(r.read())


def _load_ptb_tokens(split_path: Path, max_tokens: int = 0) -> List[str]:
    """Load PTB tokens; inject <eos> at line boundaries (canonical Mikolov)."""
    if not split_path.exists():
        print("[FATAL] PTB cache missing at %s" % split_path, flush=True)
        sys.exit(1)
    text = split_path.read_text(encoding="utf-8")
    # Mikolov convention: each line is a sentence; <eos> separates lines.
    # Mikolov files have leading/trailing spaces per line; we use replace.
    text = text.replace("\n", " <eos> ")
    toks = text.split()
    if max_tokens > 0:
        toks = toks[:max_tokens]
    return toks


# ============================================================================
# Encoder (word2vec via gensim; char-trigram fallback for OOV / smoke)
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
    """[V, n_dim] L2-normalized word2vec-projected; OOV (incl <unk>, <eos>)
    falls back to char-trigram."""
    try:
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
        meta = {"encoder": "word2vec_proj_sparse_bipolar", "n_hit": int(n_hit),
                "n_miss": int(n_miss), "n_vocab": int(len(vocab)),
                "pretrain_dim": int(kv.vector_size)}
        return E_t, meta
    except Exception as e:
        err = "%s: %s" % (type(e).__name__, str(e)[:200])
        E_np = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
        E_np = _l2_normalize_np(E_np)
        E_t = torch.from_numpy(E_np).to(device=DEVICE, dtype=TORCH_DTYPE)
        return E_t, {"encoder": "char_trigram_fallback_sparse_bipolar",
                       "load_error": err, "n_vocab": int(len(vocab))}


def sparsify_bipolar_gpu(E: torch.Tensor, f: float, seed: int) -> torch.Tensor:
    """Top-k(abs) -> sign; row-stochastic with k=int(f*dim) non-zeros."""
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
# cf-RPE plasticity rules (torch on GPU)
# ============================================================================

def build_W_cfrpe_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                       n_steps: int, batch: int, lr: float,
                       seed: int, arm_idx: int) -> torch.Tensor:
    """Iterative cf-RPE delta-rule plasticity.

    delta_W = (E[t+1] - E[t] @ W^T)^T @ E[t] / batch
    W += lr * delta_W
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E[idx_train_t[st]]
        Nxt = E[idx_train_t[st + 1]]
        error = Nxt - Ctx @ W.T
        dW = (error.T @ Ctx) / float(batch)
        W = W + lr * dW
    return W


def build_W_cfrpe_adaptive_gpu(E: torch.Tensor, idx_train_t: torch.Tensor,
                                 n_steps: int, batch: int, lr_base: float,
                                 lr_floor: float, lr_ceil: float,
                                 seed: int, arm_idx: int) -> torch.Tensor:
    """Per-token adaptive cf-RPE: per-sample LR scales with prediction-error.

    e_norm[i] = ||error[i]|| / sqrt(dim)
    med       = median(e_norm)
    lr_per[i] = lr_base * clamp(e_norm[i] / med, lr_floor, lr_ceil)
    dW        = ((error * lr_per[:, None])^T @ Ctx) / batch
    W        += dW
    """
    device = E.device
    dim = E.shape[1]
    W = torch.zeros((dim, dim), dtype=TORCH_DTYPE, device=device)
    n_pairs = idx_train_t.shape[0] - 1
    if n_pairs <= 0:
        return W
    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337) & 0x7FFFFFFF)
    sqrt_dim = math.sqrt(float(dim))
    for _ in range(n_steps):
        st = torch.randint(0, n_pairs, (batch,), generator=gen, device=device)
        Ctx = E[idx_train_t[st]]
        Nxt = E[idx_train_t[st + 1]]
        error = Nxt - Ctx @ W.T
        e_norm = torch.norm(error, dim=1) / sqrt_dim
        med = torch.median(e_norm)
        med_safe = torch.clamp(med, min=1e-9)
        ratio = e_norm / med_safe
        ratio = torch.clamp(ratio, min=lr_floor, max=lr_ceil)
        lr_per = lr_base * ratio
        weighted_err = error * lr_per.unsqueeze(1)
        dW = (weighted_err.T @ Ctx) / float(batch)
        W = W + dW
    return W


def build_W_k2_cfrpe_gpu(E_full: torch.Tensor, idx_train_t: torch.Tensor,
                           n_steps: int, batch: int, lr: float,
                           seed: int, arm_idx: int, gate_temp: float
                           ) -> Tuple[List[torch.Tensor], List[torch.Tensor], torch.Tensor]:
    """K=2 bank cf-RPE: per-bank W with gate-weighted plasticity.

    Each bank sees its own N_per slice of E_full.
    Gate uses bank-0 slice as gate signal (matches K2 shotgun smoke).
    Returns (E_banks list, W_banks list, W_gate).
    """
    V, n_dim = E_full.shape
    K = K_BANKS
    N_per = n_dim // K
    device = E_full.device
    n_pairs = idx_train_t.shape[0] - 1

    E_banks = [E_full[:, k * N_per:(k + 1) * N_per].contiguous() for k in range(K)]

    rng_gate = np.random.default_rng(seed * 7919 + arm_idx * 1013 + 9999)
    W_gate_np = rng_gate.standard_normal((K, N_per)).astype(np.float32)
    W_gate_np /= np.linalg.norm(W_gate_np, axis=1, keepdims=True) + 1e-9
    W_gate = torch.from_numpy(W_gate_np).to(device=device, dtype=TORCH_DTYPE)

    W_banks = [torch.zeros((N_per, N_per), dtype=TORCH_DTYPE, device=device)
               for _ in range(K)]

    if n_pairs <= 0:
        return E_banks, W_banks, W_gate

    gen = torch.Generator(device=device)
    gen.manual_seed(int(seed * 10007 + arm_idx * 31337 + 12345) & 0x7FFFFFFF)
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
            dW_k = (error_k * gw).T @ Ctx_k / float(batch)
            W_banks[k] = W_banks[k] + lr * dW_k
    return E_banks, W_banks, W_gate


# ============================================================================
# Per-arm logits builders
# ============================================================================

def compute_substrate_arm_logits(arm_label: str, E_sparse: torch.Tensor,
                                    idx_train: np.ndarray, idx_held: np.ndarray,
                                    seed: int, arm_idx: int) -> Dict:
    """Build [n_held, V] logits over the FULL held set."""
    V, n_dim = E_sparse.shape
    device = E_sparse.device
    idx_train_t = torch.from_numpy(idx_train).to(device)
    idx_held_t = torch.from_numpy(idx_held).to(device)
    n_h = idx_held_t.shape[0]

    t0 = time.time()
    if arm_label == "ARM_S_CFRPE_BASE":
        W = build_W_cfrpe_gpu(E_sparse, idx_train_t, CFRPE_N_STEPS,
                              CFRPE_BATCH, CFRPE_LR, seed, arm_idx)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t_ingest = time.time() - t0
        t0 = time.time()
        pred = torch.zeros((n_h, n_dim), dtype=TORCH_DTYPE, device=device)
        for b in range(0, n_h, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_h)
            ctx_b = E_sparse[idx_held_t[b:end]]
            pred[b:end] = _l2_normalize_t(ctx_b @ W.T)
        logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
        for b in range(0, n_h, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_h)
            logits[b:end] = pred[b:end] @ E_sparse.T
        if device.type == "cuda":
            torch.cuda.synchronize()
        t_recall = time.time() - t0
        del W, pred

    elif arm_label == "ARM_S_ADAPTIVE_CFRPE":
        W = build_W_cfrpe_adaptive_gpu(E_sparse, idx_train_t, CFRPE_N_STEPS,
                                         CFRPE_BATCH, CFRPE_LR, ADAPT_LR_FLOOR,
                                         ADAPT_LR_CEIL, seed, arm_idx)
        if device.type == "cuda":
            torch.cuda.synchronize()
        t_ingest = time.time() - t0
        t0 = time.time()
        pred = torch.zeros((n_h, n_dim), dtype=TORCH_DTYPE, device=device)
        for b in range(0, n_h, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_h)
            ctx_b = E_sparse[idx_held_t[b:end]]
            pred[b:end] = _l2_normalize_t(ctx_b @ W.T)
        logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
        for b in range(0, n_h, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_h)
            logits[b:end] = pred[b:end] @ E_sparse.T
        if device.type == "cuda":
            torch.cuda.synchronize()
        t_recall = time.time() - t0
        del W, pred

    elif arm_label == "ARM_S_K2_CFRPE":
        E_banks, W_banks, W_gate = build_W_k2_cfrpe_gpu(
            E_sparse, idx_train_t, CFRPE_N_STEPS, CFRPE_BATCH, CFRPE_LR,
            seed, arm_idx, K2_GATE_TEMP,
        )
        if device.type == "cuda":
            torch.cuda.synchronize()
        t_ingest = time.time() - t0
        t0 = time.time()
        # gate-weighted recall over the K banks
        logits = torch.zeros((n_h, V), dtype=TORCH_DTYPE, device=device)
        for b in range(0, n_h, RECALL_BATCH):
            end = min(b + RECALL_BATCH, n_h)
            held_idx = idx_held_t[b:end]
            gate_in = E_banks[0][held_idx]
            raw = gate_in @ W_gate.T
            raw = raw / K2_GATE_TEMP
            raw = raw - raw.max(dim=1, keepdim=True).values
            probs_r = torch.exp(raw)
            probs_r = probs_r / (probs_r.sum(dim=1, keepdim=True) + 1e-30)
            logit_chunk = torch.zeros((end - b, V), dtype=TORCH_DTYPE, device=device)
            for k in range(K_BANKS):
                ctx_k = E_banks[k][held_idx]
                pred_k = _l2_normalize_t(ctx_k @ W_banks[k].T)
                bank_scores = pred_k @ E_banks[k].T
                logit_chunk = logit_chunk + probs_r[:, k:k + 1] * bank_scores
            logits[b:end] = logit_chunk
        if device.type == "cuda":
            torch.cuda.synchronize()
        t_recall = time.time() - t0
        del E_banks, W_banks, W_gate
    else:
        raise ValueError("unknown arm: %s" % arm_label)

    logits_np = logits.detach().cpu().numpy().astype(np.float32)
    del logits, idx_train_t, idx_held_t
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return {"logits": logits_np,
            "wall_ingest_s": round(t_ingest, 2),
            "wall_recall_s": round(t_recall, 2),
            "arm_label": arm_label}


# ============================================================================
# Word-bigram (CPU numpy; V=10000 -> 100M floats = 400MB, can be slow)
# ============================================================================

def build_word_bigram(idx_train: np.ndarray, V: int, alpha: float) -> np.ndarray:
    """Add-alpha smoothed word-bigram conditional table.

    Returns P[prev, next] of shape [V, V]; row-normalized.
    Memory: V=10000 -> 100M f32 = 400MB. Acceptable.
    """
    counts = np.full((V, V), alpha, dtype=np.float64)
    if idx_train.shape[0] >= 2:
        prev = idx_train[:-1]
        nxt = idx_train[1:]
        np.add.at(counts, (prev, nxt), 1.0)
    counts /= counts.sum(axis=1, keepdims=True)
    return counts.astype(np.float32)


def word_bigram_metrics(P_bigram: np.ndarray, idx_held: np.ndarray, V: int,
                         mrr_k: int) -> Dict:
    """Compute BPW + top-1 + MRR@K under add-alpha smoothed word-bigram."""
    if idx_held.shape[0] < 2:
        return {"bpc_best": float("inf"), "top1_acc": 0.0, "mrr_at_10": 0.0,
                "best_T_for_bpc": 1.0, "best_lambda_for_bpc": 1.0,
                "raw_bpc_at_T1_L1": float("inf"), "n_test": 0}
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    n_eval = len(nxt)
    if n_eval == 0:
        return {"bpc_best": float("inf"), "top1_acc": 0.0, "mrr_at_10": 0.0,
                "best_T_for_bpc": 1.0, "best_lambda_for_bpc": 1.0,
                "raw_bpc_at_T1_L1": float("inf"), "n_test": 0}
    n_dev = n_eval // 2
    nxt_test = nxt[n_dev:]
    ctx_test = ctx[n_dev:]
    p_test = P_bigram[ctx_test, nxt_test].clip(1e-12, 1.0)
    bpc = float(-np.mean(np.log(p_test)) / math.log(2.0))
    # top-1 + MRR over conditional rows
    pred = np.argmax(P_bigram[ctx_test], axis=1)
    top1 = float(np.mean(pred == nxt_test))
    rows = P_bigram[ctx_test]
    k_use = min(mrr_k, V)
    top_idx = np.argpartition(-rows, kth=k_use - 1, axis=1)[:, :k_use]
    row_arange = np.arange(len(ctx_test))[:, None]
    top_vals = rows[row_arange, top_idx]
    order = np.argsort(-top_vals, axis=1)
    top_idx_sorted = top_idx[row_arange, order]
    rr = 0.0
    for i in range(len(ctx_test)):
        m = np.where(top_idx_sorted[i] == nxt_test[i])[0]
        if len(m) > 0:
            rr += 1.0 / float(m[0] + 1)
    mrr = float(rr / len(ctx_test))
    return {"bpc_best": round(bpc, 4), "top1_acc": round(top1, 4),
            "mrr_at_10": round(mrr, 4), "best_T_for_bpc": 1.0,
            "best_lambda_for_bpc": 1.0, "raw_bpc_at_T1_L1": round(bpc, 4),
            "n_test": int(len(nxt_test))}


# ============================================================================
# Vocab + tokenization
# ============================================================================

def build_vocab(train_tokens: List[str], cap: int = 0) -> Tuple[List[str], Dict[str, int]]:
    """Mikolov PTB has V=10000 incl <unk> and <eos>; cap=0 means use exact PTB vocab.

    If cap > 0, top-cap-1 + <unk>.
    """
    c = Counter(train_tokens)
    if cap > 0:
        top = [w for w, _ in c.most_common(cap - 1)]
        vocab = ["<unk>"] + [w for w in top if w != "<unk>"]
    else:
        # Use exact training vocabulary (Mikolov PTB train is already V=10000)
        vocab = sorted(c.keys())
        # Ensure <unk> exists for safety
        if "<unk>" not in vocab:
            vocab = ["<unk>"] + vocab
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_idx(toks: List[str], w2i: Dict[str, int]) -> np.ndarray:
    unk = w2i.get("<unk>", 0)
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


def unigram_metrics(idx_train: np.ndarray, idx_held: np.ndarray, V: int,
                      mrr_k: int) -> Dict:
    """Analytic word-unigram BPW + top-1 + MRR on test half of held."""
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    n_eval = len(nxt)
    if n_eval == 0:
        return {"bpc_best": float("inf"), "top1_acc": 0.0, "mrr_at_10": 0.0,
                "best_T_for_bpc": 1.0, "best_lambda_for_bpc": 0.0,
                "raw_bpc_at_T1_L1": float("inf"), "n_test": 0}
    n_dev = n_eval // 2
    nxt_test = nxt[n_dev:]
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
    return {"bpc_best": round(bpc, 4), "top1_acc": round(top1, 4),
            "mrr_at_10": round(mrr, 4), "best_T_for_bpc": 1.0,
            "best_lambda_for_bpc": 0.0, "raw_bpc_at_T1_L1": round(bpc, 4),
            "n_test": int(len(nxt_test))}


# ============================================================================
# Joint (T, lambda) sweep on dev; pick best per metric; eval on test
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
                            U_log: np.ndarray, nxt_dev: np.ndarray,
                            nxt_test: np.ndarray, mrr_k: int) -> Dict:
    """Joint (T, lambda) sweep on dev; report best per-metric on test."""
    probs_T1 = softmax_logits_with_T(sub_logits_test, 1.0)
    logp_T1 = np.log(np.clip(probs_T1, 1e-30, 1.0))
    raw_bpc_at_T1_L1 = bpc_from_logp(logp_T1, nxt_test)
    raw_top1_at_T1_L1 = top1_acc_from_logp(logp_T1, nxt_test)
    raw_mrr_at_T1_L1 = mrr_at_k(logp_T1, nxt_test, mrr_k)

    best_bpc = {"T": 1.0, "lambda": 1.0, "dev_value": float("inf")}
    best_top1 = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    best_mrr = {"T": 1.0, "lambda": 1.0, "dev_value": -1.0}
    for T in TEMP_GRID:
        sub_probs_dev = softmax_logits_with_T(sub_logits_dev, T)
        sub_logp_dev = np.log(np.clip(sub_probs_dev, 1e-30, 1.0))
        for lam in LAMBDA_GRID:
            logp_dev = log_linear_interp_logp(sub_logp_dev, U_log, lam)
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
        sub_probs_test = softmax_logits_with_T(sub_logits_test, T)
        sub_logp_test = np.log(np.clip(sub_probs_test, 1e-30, 1.0))
        logp_test = log_linear_interp_logp(sub_logp_test, U_log, lam)
        if fn == bpc_from_logp:
            return fn(logp_test, nxt_test)
        if fn == top1_acc_from_logp:
            return fn(logp_test, nxt_test)
        return mrr_at_k(logp_test, nxt_test, mrr_k)

    bpc_best_test = _test_metric(best_bpc["T"], best_bpc["lambda"], bpc_from_logp)
    top1_best_test = _test_metric(best_top1["T"], best_top1["lambda"],
                                    top1_acc_from_logp)
    mrr_best_test = _test_metric(best_mrr["T"], best_mrr["lambda"], mrr_at_k)

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


# ============================================================================
# Per-seed runner
# ============================================================================

def run_unit(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading PTB (Mikolov)" % seed, flush=True)
    _ensure_ptb_cache()
    train_toks_all = _load_ptb_tokens(PTB_TRAIN, max_tokens=0)
    if RUN_MODE == "smoke" and PTB_TRAIN_TOKENS_CAP > 0:
        train_toks = train_toks_all[:PTB_TRAIN_TOKENS_CAP]
    else:
        train_toks = train_toks_all
    if PTB_HELD_FROM_VALID:
        held_toks = _load_ptb_tokens(PTB_VALID, max_tokens=0)
    else:
        # smoke: held = next chunk of train (avoids val download timing in smoke gate)
        held_size = max(200, len(train_toks) // 4)
        held_toks = train_toks_all[PTB_TRAIN_TOKENS_CAP:PTB_TRAIN_TOKENS_CAP + held_size]
        if len(held_toks) < 50:
            held_toks = train_toks[-min(200, len(train_toks) // 4):]

    vocab, w2i = build_vocab(train_toks, cap=0 if RUN_MODE == "full" else 200)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("[seed=%d] V=%d N_TRAIN=%d N_HELD=%d N_DIM=%d device=%s" % (
        seed, V, len(idx_train), len(idx_held), N_DIM_TOTAL, str(DEVICE)),
        flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[seed=%d gpu] %s mem_total_gb=%.2f" % (
                seed, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9),
                flush=True)
        except Exception as e:
            print("[seed=%d gpu-info-fail] %s" % (seed, e), flush=True)

    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    U_log = np.log(np.clip(U, 1e-30, 1.0)).astype(np.float32)

    # ARM_B1_UNIGRAM
    uni = unigram_metrics(idx_train, idx_held, V, MRR_K)
    print("[seed=%d arm=ARM_B1_UNIGRAM] bpw=%.3f top1=%.4f mrr=%.4f n_test=%d" % (
        seed, uni["bpc_best"], uni["top1_acc"], uni["mrr_at_10"], uni["n_test"]),
        flush=True)
    by_arm: Dict[str, Dict] = {"ARM_B1_UNIGRAM": uni}

    # ARM_B2_WORD_BIGRAM
    t_bg0 = time.time()
    print("[seed=%d arm=ARM_B2_WORD_BIGRAM] building bigram table V=%d alpha=%.4f..." % (
        seed, V, BIGRAM_ALPHA), flush=True)
    P_bigram = build_word_bigram(idx_train, V, BIGRAM_ALPHA)
    bg = word_bigram_metrics(P_bigram, idx_held, V, MRR_K)
    bg["wall_build_s"] = round(time.time() - t_bg0, 2)
    by_arm["ARM_B2_WORD_BIGRAM"] = bg
    del P_bigram
    print("[seed=%d arm=ARM_B2_WORD_BIGRAM] bpw=%.3f top1=%.4f mrr=%.4f build=%.1fs" % (
        seed, bg["bpc_best"], bg["top1_acc"], bg["mrr_at_10"], bg["wall_build_s"]),
        flush=True)

    # Encoder (shared across substrate arms)
    print("\n[seed=%d] building word2vec base E (V=%d, N_DIM=%d) on %s..." % (
        seed, V, N_DIM_TOTAL, str(DEVICE)), flush=True)
    t_enc0 = time.time()
    E_base, encoder_meta = build_E_word2vec_gpu(vocab, N_DIM_TOTAL, seed)
    t_enc = time.time() - t_enc0
    print("[seed=%d encoder=%s] E built (%.1fs); shape=%s" % (
        seed, encoder_meta.get("encoder", "?"), t_enc, tuple(E_base.shape)),
        flush=True)

    # Sparse-bipolar (all substrate arms share the sparsified encoder)
    print("[seed=%d] sparsify_bipolar f=%.3f..." % (seed, SPARSE_BIPOLAR_F),
          flush=True)
    E_sparse = _l2_normalize_t(sparsify_bipolar_gpu(E_base, SPARSE_BIPOLAR_F, seed))
    del E_base

    # Held eval split: simply align with the unigram_metrics / bigram_metrics
    # convention (n_dev = n_eval // 2; nxt[n_dev:] is test). idx_held layout:
    # logits at position p predicts idx_held[p+1].
    ctx_full = idx_held[:-1]
    nxt_full = idx_held[1:]
    n_eval = len(nxt_full)
    if n_eval == 0:
        for arm in SUBSTRATE_ARMS:
            by_arm[arm] = {"empty_eval": True, "bpc_best": float("inf"),
                            "top1_acc": float("nan"), "mrr_at_10": float("nan")}
        del E_sparse
        return {"seed": seed, "by_arm": by_arm, "V": V, "N_DIM": N_DIM_TOTAL,
                 "N_TRAIN": int(len(idx_train)), "N_HELD": int(len(idx_held)),
                 "run_mode": RUN_MODE, "config_version": CONFIG_VERSION,
                 "elapsed_s_seed": round(time.time() - t_seed, 2),
                 "encoder_meta": encoder_meta, "n_llm_calls": 0,
                 "corpus_provenance": "PTB-word-level (Mikolov split; wojzaremba/lstm)"}
    n_dev = n_eval // 2
    nxt_dev = nxt_full[:n_dev]
    nxt_test = nxt_full[n_dev:]

    for arm_idx, arm in enumerate(SUBSTRATE_ARMS):
        t_arm0 = time.time()
        print("\n  [seed=%d arm=%s] building logits..." % (seed, arm), flush=True)
        try:
            ar = compute_substrate_arm_logits(arm, E_sparse, idx_train,
                                                 idx_held, seed, arm_idx)
        except Exception as e:
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
            print("    [seed=%d arm=%s] COMPUTE FAIL: %s" % (seed, arm, err),
                  flush=True)
            by_arm[arm] = {"compute_failed": True, "compute_error": err,
                            "bpc_best": float("inf"), "top1_acc": float("nan"),
                            "mrr_at_10": float("nan"),
                            "best_T_for_bpc": float("nan"),
                            "best_lambda_for_bpc": float("nan"),
                            "raw_bpc_at_T1_L1": float("inf"),
                            "elapsed_s_arm": round(time.time() - t_arm0, 2)}
            continue
        logits_full = ar["logits"]  # [n_held, V]
        # logits at position p predicts idx_held[p+1] = nxt_full[p];
        # truncate logits to ctx_full domain.
        if logits_full.shape[0] >= len(ctx_full):
            logits_ctx = logits_full[:len(ctx_full)]
        else:
            logits_ctx = logits_full
        # Split into dev/test halves matching nxt_full split
        n_logits = len(logits_ctx)
        n_logits_eval = min(n_logits, n_eval)
        logits_eval = logits_ctx[:n_logits_eval]
        n_dev_l = n_logits_eval // 2
        jr = joint_sweep_substrate(logits_eval[:n_dev_l], logits_eval[n_dev_l:],
                                     U_log,
                                     nxt_full[:n_dev_l],
                                     nxt_full[n_dev_l:n_logits_eval],
                                     MRR_K)
        jr["elapsed_s_arm"] = round(time.time() - t_arm0, 2)
        jr["wall_ingest_s"] = ar.get("wall_ingest_s", 0.0)
        jr["wall_recall_s"] = ar.get("wall_recall_s", 0.0)
        by_arm[arm] = jr
        print("    [seed=%d arm=%s] bpw=%.3f top1=%.4f mrr=%.4f rawT1L1=%.3f "
              "(bestT=%.3f bestL=%.2f)" % (
                  seed, arm, jr["bpc_best"], jr["top1_acc"], jr["mrr_at_10"],
                  jr["raw_bpc_at_T1_L1"], jr["best_T_for_bpc"],
                  jr["best_lambda_for_bpc"]), flush=True)

    del E_sparse
    if DEVICE.type == "cuda":
        torch.cuda.empty_cache()
    return {
        "seed": seed,
        "by_arm": by_arm,
        "V": V,
        "N_DIM": N_DIM_TOTAL,
        "N_TRAIN": int(len(idx_train)),
        "N_HELD": int(len(idx_held)),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "elapsed_s_seed": round(time.time() - t_seed, 2),
        "device": str(DEVICE),
        "encoder_meta": encoder_meta,
        "n_llm_calls": 0,
        "corpus_provenance": "PTB-word-level (Mikolov split; wojzaremba/lstm)",
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})

    by_arm_agg: Dict[str, Dict] = {}
    for arm in ARMS:
        bpcs = []
        top1s = []
        mrrs = []
        for u in units:
            a = u["by_arm"].get(arm, {})
            b = a.get("bpc_best", float("inf"))
            t1 = a.get("top1_acc", float("nan"))
            mr = a.get("mrr_at_10", float("nan"))
            if isinstance(b, float) and math.isfinite(b):
                bpcs.append(b)
                top1s.append(t1)
                mrrs.append(mr)
        if not bpcs:
            by_arm_agg[arm] = {"all_seeds_failed": True}
            continue
        by_arm_agg[arm] = {
            "bpw_mean": round(float(np.mean(bpcs)), 4),
            "bpw_std": round(float(np.std(bpcs)), 4),
            "bpw_cv": round(float(np.std(bpcs) / max(abs(np.mean(bpcs)), 1e-9)), 4),
            "top1_mean": round(float(np.mean(top1s)), 4),
            "mrr_mean": round(float(np.mean(mrrs)), 4),
            "n_seeds": len(bpcs),
        }

    n_llm = sum(int(u.get("n_llm_calls", 0)) for u in units)
    substrate_only_ok = (n_llm == 0 and _LLM_CALL_COUNTER[0] == 0)

    # Sanity rails: unigram + bigram within canonical PTB ranges (FULL mode).
    is_full_mode = (units and units[0].get("run_mode", "full") == "full")
    uni = by_arm_agg.get("ARM_B1_UNIGRAM", {})
    bg = by_arm_agg.get("ARM_B2_WORD_BIGRAM", {})
    uni_bpw = uni.get("bpw_mean", float("nan"))
    bg_bpw = bg.get("bpw_mean", float("nan"))
    uni_ok = True
    bg_ok = True
    if is_full_mode:
        uni_ok = (math.isfinite(uni_bpw) and
                  UNIGRAM_BPW_MIN <= uni_bpw <= UNIGRAM_BPW_MAX)
        bg_ok = (math.isfinite(bg_bpw) and
                 BIGRAM_BPW_MIN <= bg_bpw <= BIGRAM_BPW_MAX)

    # Substrate arm assessment
    substrate_means: Dict[str, float] = {}
    substrate_cvs: Dict[str, float] = {}
    for arm in SUBSTRATE_ARMS:
        a = by_arm_agg.get(arm, {})
        if a.get("all_seeds_failed", False):
            continue
        substrate_means[arm] = a.get("bpw_mean", float("inf"))
        substrate_cvs[arm] = a.get("bpw_cv", float("inf"))

    # HP test: ANY substrate arm BPW <= bigram BPW - HP_BPW_MARGIN AND cv <= cap
    bigram_bar = bg_bpw - HP_BPW_MARGIN if math.isfinite(bg_bpw) else float("-inf")
    hp_arms = []
    for arm, mean_bpw in substrate_means.items():
        cv = substrate_cvs.get(arm, float("inf"))
        if mean_bpw <= bigram_bar and cv <= HP_CV_MAX:
            hp_arms.append((arm, mean_bpw, cv))
    hp_arms.sort(key=lambda x: x[1])  # best (lowest) first

    chain_grade_arms = [(a, m, c) for (a, m, c) in hp_arms if m <= CHAIN_GRADE_BPW]

    # MIDDLE_BAND: substrate beats bigram but doesn't clear HP bar
    mid_arms = []
    for arm, mean_bpw in substrate_means.items():
        cv = substrate_cvs.get(arm, float("inf"))
        if math.isfinite(bg_bpw) and mean_bpw <= bg_bpw and mean_bpw > bigram_bar:
            mid_arms.append((arm, mean_bpw, cv))

    # HARD_FAIL_DECISIVE: all substrate arms STRICTLY worse than bigram
    decisive_fail = (all(m > bg_bpw for m in substrate_means.values())
                       and len(substrate_means) > 0
                       and math.isfinite(bg_bpw))

    # discriminator probe: are substrate arms clustered (NULL) or differentiated?
    discriminator_spread = float("nan")
    if len(substrate_means) >= 2:
        vals = list(substrate_means.values())
        discriminator_spread = round(max(vals) - min(vals), 4)

    summary = (
        "uni=%.3f|bigram=%.3f|S_cfrpe_base=%.3f|S_K2=%.3f|S_adapt=%.3f|"
        "spread=%.3f|n_llm=%d|sanity_uni=%s|sanity_bg=%s"
    ) % (
        uni_bpw, bg_bpw,
        substrate_means.get("ARM_S_CFRPE_BASE", float("nan")),
        substrate_means.get("ARM_S_K2_CFRPE", float("nan")),
        substrate_means.get("ARM_S_ADAPTIVE_CFRPE", float("nan")),
        discriminator_spread, n_llm,
        "OK" if uni_ok else "FAIL", "OK" if bg_ok else "FAIL",
    )

    detail = {
        "by_arm_agg": by_arm_agg,
        "unigram_sanity_ok": bool(uni_ok),
        "bigram_sanity_ok": bool(bg_ok),
        "unigram_bpw": uni_bpw if math.isfinite(uni_bpw) else None,
        "bigram_bpw": bg_bpw if math.isfinite(bg_bpw) else None,
        "bigram_hp_bar": bigram_bar if math.isfinite(bigram_bar) else None,
        "hp_bpw_margin": HP_BPW_MARGIN,
        "chain_grade_bpw": CHAIN_GRADE_BPW,
        "bigram_bpw_min": BIGRAM_BPW_MIN,
        "bigram_bpw_max": BIGRAM_BPW_MAX,
        "unigram_bpw_min": UNIGRAM_BPW_MIN,
        "unigram_bpw_max": UNIGRAM_BPW_MAX,
        "hp_cv_max": HP_CV_MAX,
        "hp_arms": [{"arm": a, "bpw_mean": m, "cv": c} for (a, m, c) in hp_arms],
        "chain_grade_arms": [{"arm": a, "bpw_mean": m, "cv": c}
                                for (a, m, c) in chain_grade_arms],
        "mid_arms": [{"arm": a, "bpw_mean": m, "cv": c} for (a, m, c) in mid_arms],
        "decisive_fail": bool(decisive_fail),
        "discriminator_spread_bpw": discriminator_spread,
        "substrate_arm_bpw_means": substrate_means,
        "n_seeds": len(units),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "CONFIG_VERSION": CONFIG_VERSION,
        "CONFOUND_AUDIT": CONFOUND_AUDIT_TUPLE,
        "corpus_provenance": "PTB-word-level (Mikolov split; wojzaremba/lstm)",
        "lane_declaration": "Lane 2 (intra-corpus substrate-vs-substrate + tagged word-bigram cross-paradigm baseline)",
        "intra_lane_delta_arms": {
            "ARM_S_K2_CFRPE_vs_ARM_S_CFRPE_BASE": "knob=K_BANKS (1->2); else identical",
            "ARM_S_ADAPTIVE_CFRPE_vs_ARM_S_CFRPE_BASE": "knob=cfrpe_rule (fixed->adaptive); else identical",
        },
        "honest_scope": (
            "First apples-to-apples substrate-as-LM eval on canonical PTB word-"
            "level (Mikolov split). All arms share PTB corpus + V=10000 vocab + "
            "held split. HP = ANY substrate arm BPW <= bigram BPW - %.2f with "
            "cv <= %.2f AND substrate-only-decode. CHAIN_GRADE_BONUS = BPW <= %.2f. "
            "HARD_FAIL_DECISIVE = ALL substrate arms > bigram BPW. Confound audit "
            "tuple stamped in config_version; corpus_provenance tag attached for "
            "cert ledger.") % (HP_BPW_MARGIN, HP_CV_MAX, CHAIN_GRADE_BPW),
        "cites": [
            "preregs/2026-06-24_substrate_ptb_clean_word_level_eval_v1.md",
            "notes/research_apples_to_apples_substrate_evaluation_methodology_2x_drill_2026-06-24.md",
            "experiments/exp_fair_harness_substrate_as_lm_v1.py (torch+cuda fair_harness)",
            "experiments/exp_substrate_sequence_modeling_production_v2.py (alpha=0.001 fix)",
            "experiments/exp_substrate_K2_x_cfrpe_compose_word2vec_v2.py (K=2 banks)",
            "experiments/exp_substrate_cfrpe_per_token_adaptive_lr_v1.py (adaptive cf-RPE)",
            "Mikolov_2010_PTB_split (raw.githubusercontent.com/wojzaremba/lstm)",
            "USER_2026-06-24_text8_pythia_biased_use_PTB",
            "USER_2026-06-22_Fix24_GPU_dispatch_must_use_GPU",
        ],
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (
                    n_llm, summary),
                detail)

    if is_full_mode and not uni_ok:
        return ("HARD_FAIL",
                ("HARD_FAIL: unigram sanity rail violated -- BPW=%.3f outside "
                 "canonical PTB unigram range [%.2f, %.2f]. Harness mis-spec. %s") % (
                    uni_bpw, UNIGRAM_BPW_MIN, UNIGRAM_BPW_MAX, summary),
                detail)

    if is_full_mode and not bg_ok:
        return ("HARD_FAIL",
                ("HARD_FAIL: word-bigram sanity rail violated -- BPW=%.3f outside "
                 "canonical PTB bigram range [%.2f, %.2f]. Baseline mis-spec; "
                 "cannot interpret substrate arms. %s") % (
                    bg_bpw, BIGRAM_BPW_MIN, BIGRAM_BPW_MAX, summary),
                detail)

    if chain_grade_arms:
        a, m, c = chain_grade_arms[0]
        return ("HARD_PASS",
                ("HARD_PASS_CHAIN_GRADE_BONUS: substrate %s BPW=%.4f cv=%.3f "
                 "clears bigram=%.4f by %.3f bits AND <= chain_grade bar %.2f. "
                 "Substrate-as-LM on canonical PTB word-level decisively clears "
                 "real-LM baseline AND approaches LSTM territory. "
                 "FIRST clean apples-to-apples PTB chain-grade substrate-as-LM "
                 "evidence. %s") % (
                    a, m, c, bg_bpw, bg_bpw - m, CHAIN_GRADE_BPW, summary),
                detail)

    if hp_arms:
        a, m, c = hp_arms[0]
        return ("HARD_PASS",
                ("HARD_PASS_CLEAN_SUBSTRATE_VIABLE: substrate %s BPW=%.4f cv=%.3f "
                 "clears bigram=%.4f by %.3f bits (>= %.2f bar). Substrate-as-LM "
                 "on canonical PTB word-level clears real-LM baseline. "
                 "Apples-to-apples on canonical NLP benchmark. %s") % (
                    a, m, c, bg_bpw, bg_bpw - m, HP_BPW_MARGIN, summary),
                detail)

    if decisive_fail:
        return ("HARD_FAIL",
                ("HARD_FAIL_DECISIVE: ALL substrate arms strictly worse than "
                 "word-bigram (bigram=%.4f; substrate means=%s). Substrate-as-LM "
                 "ceiling is REAL on canonical PTB word-level -- text8 bias is "
                 "NOT the cause; the gap is the substrate-as-LM architecture. %s") % (
                    bg_bpw, substrate_means, summary),
                detail)

    if mid_arms:
        mid_arms.sort(key=lambda x: x[1])
        a, m, c = mid_arms[0]
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND: substrate %s BPW=%.4f cv=%.3f beats bigram=%.4f "
                 "by %.3f bits but fails HP bar (need >= %.2f). Substrate clears "
                 "bigram on PTB but does not decisively pass. %s") % (
                    a, m, c, bg_bpw, bg_bpw - m, HP_BPW_MARGIN, summary),
                detail)

    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: ambiguous; substrate arms neither strictly beat nor "
             "strictly miss the bigram bar. Diagnostic mode. %s") % summary,
            detail)


# ============================================================================
# Self-test (instrumentation; runs in <10s on CPU)
# ============================================================================

def _selftest():
    # T1: PTB loader -- cache populated; canonical token counts.
    _ensure_ptb_cache()
    train_toks = _load_ptb_tokens(PTB_TRAIN, max_tokens=1000)
    assert len(train_toks) > 100, "T1 PTB train tokens load"
    # canonical Mikolov train ~929k incl <eos> (full file)
    train_toks_full = _load_ptb_tokens(PTB_TRAIN, max_tokens=0)
    assert len(train_toks_full) > 900_000, ("T1 PTB full train tokens; "
                                              "got %d expected ~929k" % len(train_toks_full))
    assert "<unk>" in set(train_toks_full[:5000]), "T1 PTB <unk> token present"
    assert "<eos>" in set(train_toks_full[:5000]), "T1 PTB <eos> token present"

    # T2: word-bigram add-alpha row-stochastic + v2 fix alpha=0.001 monotonic
    V_t = 5
    idx_t = np.array([1, 2, 1, 3, 4, 1, 2], dtype=np.int64)
    P = build_word_bigram(idx_t, V_t, alpha=0.1)
    assert P.shape == (V_t, V_t), "T2 shape"
    assert np.allclose(P.sum(axis=1), 1.0, atol=1e-5), "T2 row-stochastic"
    # v2 fix arithmetic: on V=4000 row with c=10/N=10, alpha=0.001 yields >25x prob
    V_b = 4000
    c = 10.0
    N_row = 10.0
    p_v1 = (c + 0.1) / (N_row + 0.1 * V_b)
    p_v2 = (c + 0.001) / (N_row + 0.001 * V_b)
    assert p_v2 > p_v1 * 25.0, ("T2 v2-fix: p_v2=%.5f p_v1=%.5f ratio=%.1fx" %
                                  (p_v2, p_v1, p_v2 / p_v1))

    # T3: K=1 cf-RPE delta-rule shrinks error (one step under positive eta)
    # Use small torch tensors on CPU
    dim_t = 32
    V_g = 4
    n_t = 10
    g = torch.Generator(device="cpu").manual_seed(0)
    E_g = torch.randn(V_g, dim_t, generator=g)
    E_g = E_g / (E_g.norm(dim=1, keepdim=True) + 1e-9)
    idx_g = torch.from_numpy(np.array([0, 1, 2, 1, 3, 0, 2, 1, 0, 3], dtype=np.int64))
    W_pre = torch.zeros((dim_t, dim_t))
    # one step manually
    st_g = torch.tensor([0, 2, 4, 6], dtype=torch.int64)
    Ctx_g = E_g[idx_g[st_g]]
    Nxt_g = E_g[idx_g[st_g + 1]]
    error_pre = Nxt_g - Ctx_g @ W_pre.T
    err_norm_pre = float(error_pre.norm())
    W_post = build_W_cfrpe_gpu(E_g, idx_g, n_steps=1, batch=4, lr=0.5, seed=0, arm_idx=0)
    # After one delta-rule step in the direction of error, residual on the
    # same training samples should be lower or equal (CPU torch path test)
    error_post = Nxt_g - Ctx_g @ W_post.T
    err_norm_post = float(error_post.norm())
    # Allow small numerical wiggle; should be strictly <= for fresh W=0 init
    assert err_norm_post <= err_norm_pre + 1e-3, (
        "T3 cf-RPE delta-rule error must non-increase; pre=%.4f post=%.4f" % (
            err_norm_pre, err_norm_post))

    # T4: K=2 gate-weighted bank shapes
    E_k2 = torch.randn(4, 64, generator=torch.Generator(device="cpu").manual_seed(1))
    E_k2 = E_k2 / (E_k2.norm(dim=1, keepdim=True) + 1e-9)
    idx_k2 = torch.from_numpy(np.array([0, 1, 2, 3, 0, 1, 2, 3], dtype=np.int64))
    E_banks, W_banks, W_gate = build_W_k2_cfrpe_gpu(E_k2, idx_k2, n_steps=2,
                                                       batch=4, lr=0.5, seed=0,
                                                       arm_idx=1, gate_temp=1.0)
    assert len(E_banks) == 2 and len(W_banks) == 2, "T4 K=2 bank count"
    assert E_banks[0].shape == (4, 32), "T4 bank0 slice shape"
    assert W_banks[0].shape == (32, 32), "T4 W_banks shape"
    assert W_gate.shape == (2, 32), "T4 W_gate shape"

    # T5: per-token adaptive cf-RPE -- median-normalized LR ordering
    # Construct planted batch: two samples with very different error norms.
    dim_a = 64
    E_a = torch.eye(4, dim_a)
    # We'll directly exercise the LR-computation logic on synthetic errors
    error_lo = torch.tensor([[0.1] + [0.0] * (dim_a - 1)])
    error_hi = torch.tensor([[1.0] + [0.0] * (dim_a - 1)])
    errors = torch.cat([error_lo, error_hi, error_lo], dim=0)
    e_norm = torch.norm(errors, dim=1) / math.sqrt(float(dim_a))
    med = torch.median(e_norm)
    ratio = torch.clamp(e_norm / med, ADAPT_LR_FLOOR, ADAPT_LR_CEIL)
    # high-error sample should get larger ratio than low-error
    assert ratio[1] > ratio[0], ("T5 adaptive: hi_err ratio=%.3f vs lo_err ratio=%.3f"
                                    % (float(ratio[1]), float(ratio[0])))

    # T6: BPC from planted logp reproduces analytic unigram BPC at lambda=0
    U_t6 = np.array([0.5, 0.2, 0.15, 0.1, 0.05])
    U_log_t6 = np.log(np.clip(U_t6, 1e-30, 1.0))
    nxt_t6 = np.array([0, 1, 2, 0, 1])
    sub_logits_t6 = np.zeros((5, 5), dtype=np.float32)
    logp_lam0 = log_linear_interp_logp(np.log(np.full_like(sub_logits_t6, 1.0 / 5.0)),
                                         U_log_t6, 0.0)
    bpc_lam0 = bpc_from_logp(logp_lam0, nxt_t6)
    bpc_uni = -float(np.mean(np.log(U_t6[nxt_t6]))) / math.log(2.0)
    assert abs(bpc_lam0 - bpc_uni) < 1e-4, ("T6 lam=0=uni: %.4f vs %.4f" % (
        bpc_lam0, bpc_uni))

    # T7: sparse-bipolar primitive -- exactly k non-zero per row in {-1, +1}
    E_sp = torch.randn(4, 100, generator=torch.Generator(device="cpu").manual_seed(0))
    sp = sparsify_bipolar_gpu(E_sp, 0.05, seed=0)
    k_expect = max(1, int(round(0.05 * 100)))
    nnz_per_row = (sp != 0).sum(dim=1).tolist()
    assert all(n == k_expect for n in nnz_per_row), "T7 sparse nnz: got %s" % nnz_per_row
    uniq = set(sp.unique().tolist())
    assert uniq.issubset({-1.0, 0.0, 1.0}), "T7 sparse not bipolar: %s" % uniq

    # T8: HRR bind (irfft-rfft shape preserve + non-zero norm) -- not used in this
    # cell directly, but keep self-test parallel to seq-modeling parent for parity.
    # (skipped to keep self-test minimal; build_W_k2_cfrpe_gpu is the bind-analog
    # primitive tested in T4.)

    # T9: verdict bands -- planted units
    def _unit(uni=10.0, bg=5.5, s_cfrpe=5.1, s_k2=5.0, s_adapt=4.9):
        return {"seed": 0, "by_arm": {
            "ARM_B1_UNIGRAM": {"bpc_best": uni, "top1_acc": 0.10, "mrr_at_10": 0.20},
            "ARM_B2_WORD_BIGRAM": {"bpc_best": bg, "top1_acc": 0.30, "mrr_at_10": 0.40},
            "ARM_S_CFRPE_BASE": {"bpc_best": s_cfrpe, "top1_acc": 0.18,
                                    "mrr_at_10": 0.30, "raw_bpc_at_T1_L1": s_cfrpe},
            "ARM_S_K2_CFRPE": {"bpc_best": s_k2, "top1_acc": 0.19,
                                  "mrr_at_10": 0.31, "raw_bpc_at_T1_L1": s_k2},
            "ARM_S_ADAPTIVE_CFRPE": {"bpc_best": s_adapt, "top1_acc": 0.20,
                                       "mrr_at_10": 0.32, "raw_bpc_at_T1_L1": s_adapt},
        }, "n_llm_calls": 0, "run_mode": "full"}

    # HARD_PASS: substrate clears bigram - 0.30 (need s <= 5.5 - 0.3 = 5.2)
    units_hp = [_unit(s_cfrpe=5.10, s_k2=5.10, s_adapt=5.10) for _ in range(3)]
    v, m, _ = compute_verdict(units_hp)
    assert v == "HARD_PASS" and "CLEAN_SUBSTRATE_VIABLE" in m, ("T9 HP got %s; msg=%s"
                                                                   % (v, m[:200]))

    # CHAIN_GRADE_BONUS: substrate <= 4.5
    units_cg = [_unit(s_cfrpe=4.40, s_k2=4.40, s_adapt=4.40) for _ in range(3)]
    v, m, _ = compute_verdict(units_cg)
    assert v == "HARD_PASS" and "CHAIN_GRADE_BONUS" in m, ("T9 CG got %s; msg=%s"
                                                                % (v, m[:200]))

    # MIDDLE_BAND: substrate beats bigram but doesn't clear HP bar
    units_mid = [_unit(s_cfrpe=5.40, s_k2=5.40, s_adapt=5.40) for _ in range(3)]
    v, m, _ = compute_verdict(units_mid)
    assert v == "MIDDLE_BAND", "T9 MID got %s; msg=%s" % (v, m[:200])

    # HARD_FAIL_DECISIVE: all substrate strictly > bigram
    units_hf = [_unit(s_cfrpe=6.20, s_k2=6.10, s_adapt=6.30) for _ in range(3)]
    v, m, _ = compute_verdict(units_hf)
    assert v == "HARD_FAIL" and "DECISIVE" in m, "T9 HF got %s; msg=%s" % (v, m[:200])

    # Sanity rail (full mode): bigram outside [5.2, 6.8] -> HARD_FAIL
    units_sanity = [_unit(uni=10.0, bg=7.5, s_cfrpe=4.0, s_k2=4.0, s_adapt=4.0)
                       for _ in range(3)]
    v, m, _ = compute_verdict(units_sanity)
    assert v == "HARD_FAIL" and "bigram sanity" in m, ("T9 sanity got %s; msg=%s"
                                                          % (v, m[:200]))

    # T10: LLM counter
    assert _LLM_CALL_COUNTER[0] == 0, "T10 llm counter"

    print("[selftest] PASS: T1 PTB loader (929k tokens) + T2 bigram alpha-fix arithmetic "
          "+ T3 cf-RPE delta-rule shrinks error + T4 K=2 bank shapes + T5 adaptive "
          "median-norm LR + T6 BPC lam=0=unigram + T7 sparse-bipolar bipolar+sparse "
          "+ T9 verdict bands (HP/CG/MID/DEC_FAIL/sanity) + T10 llm=0",
          flush=True)


# ============================================================================
# atexit synthesizer (recovers metrics from partials on timeout / SIGTERM)
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
                                     "atexit synthesize compute_verdict failed: %s" % e,
                                     {"n_seeds_recovered": len(units)})
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "anchor": ANCHOR_NAME,
            "verdict": "TIMEOUT_PARTIAL_NSEEDS_%d" % len(units) if verdict != "PARTIAL_TIMEOUT" else verdict,
            "verdict_msg": "[atexit-synthesize] " + msg,
            "run_mode": RUN_MODE,
            "N_DIM": N_DIM_TOTAL,
            "N": N_DIM_TOTAL,
            "n_seeds": len(units),
            "n_seeds_expected": len(SEEDS),
            "detail": detail,
            "metrics_source": "atexit_synthesize_partial_substrate_ptb_clean_word_level_eval_v1",
            "per_unit": units,
            "elapsed_s": (time.time() - _T0_REF[0]) if _T0_REF[0] else 0.0,
            "summary": "[atexit-synthesize from %d/%d partials] %s" % (
                len(units), len(SEEDS), msg[:200]),
            "substrate_only_decode_gate": "TRUE",
            "zero_llm_calls_at_inference": True,
            "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
            "_synthesized_by_atexit": True,
            "config_version": CONFIG_VERSION,
            "device": str(DEVICE),
            "corpus_provenance": "PTB-word-level (Mikolov split; wojzaremba/lstm)",
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
    print("[config] %s mode=%s N_DIM=%d K_BANKS=%d arms=%s seeds=%s | "
          "name_says_smoke=%s | device=%s | %s" % (
              ANCHOR_NAME, RUN_MODE, N_DIM_TOTAL, K_BANKS, ARMS, SEEDS,
              _NAME_SAYS_SMOKE, str(DEVICE), CONFIG_VERSION), flush=True)
    if DEVICE.type == "cuda":
        try:
            print("[gpu] device=%s name=%s total_mem_gb=%.2f" % (
                DEVICE, torch.cuda.get_device_name(0),
                torch.cuda.get_device_properties(0).total_memory / 1e9),
                flush=True)
        except Exception as e:
            print("[gpu] info-fetch failed: %s" % e, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR_REF[0] = out_dir
    atexit.register(_synthesize_on_exit)
    try:
        signal.signal(signal.SIGTERM, lambda *a: (_synthesize_on_exit(), sys.exit(143)))
    except (ValueError, AttributeError):
        pass
    run_cfg = {"run_mode": RUN_MODE, "N": N_DIM_TOTAL,
                "schema": "substrate-ptb-clean-word-level-v1"}
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
        "N_DIM": N_DIM_TOTAL,
        "N": N_DIM_TOTAL,
        "K_BANKS": K_BANKS,
        "N_DIM_PER_BANK": N_DIM_PER_BANK,
        "INGEST_CHUNK": INGEST_CHUNK,
        "RECALL_BATCH": RECALL_BATCH,
        "TEMP_GRID": TEMP_GRID,
        "LAMBDA_GRID": LAMBDA_GRID,
        "MRR_K": MRR_K,
        "SPARSE_BIPOLAR_F": SPARSE_BIPOLAR_F,
        "BIGRAM_ALPHA": BIGRAM_ALPHA,
        "CFRPE_LR": CFRPE_LR,
        "CFRPE_BATCH": CFRPE_BATCH,
        "CFRPE_N_STEPS": CFRPE_N_STEPS,
        "K2_GATE_TEMP": K2_GATE_TEMP,
        "ADAPT_LR_FLOOR": ADAPT_LR_FLOOR,
        "ADAPT_LR_CEIL": ADAPT_LR_CEIL,
        "arms": ARMS,
        "n_seeds": len(SEEDS),
        "detail": detail,
        "metrics_source": "measured_gpu_substrate_ptb_clean_word_level_eval_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
        "summary": msg[:240],
        "substrate_only_decode_gate": (
            "TRUE (substrate cosine logits; word2vec is static open-weight lookup; "
            "zero LLM at inference)"),
        "zero_llm_calls_at_inference": True,
        "_llm_call_counter_final": _LLM_CALL_COUNTER[0],
        "config_version": CONFIG_VERSION,
        "device": str(DEVICE),
        "corpus_provenance": "PTB-word-level (Mikolov split; wojzaremba/lstm)",
        "CONFOUND_AUDIT": CONFOUND_AUDIT_TUPLE,
        "lane_declaration": "Lane 2 (intra-corpus substrate-vs-substrate + tagged word-bigram cross-paradigm baseline)",
    }
    write_metrics(out_dir, metrics, units)
    _METRICS_WRITTEN[0] = True
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
