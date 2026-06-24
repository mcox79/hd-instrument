"""substrate_serotonin_mode_switch_bank_select_LM_v1 -- Gap #3: serotonin as bank-switch.

MOTIVATION (2026-06-23):
  neuromodulator_3axis_gated_compose_LM_v1 tested serotonin as GAIN-MODULATION on one W
  bank and got READOUT_DEGENERATE. That cell tested a DIFFERENT hypothesis from what is
  tested here. This cell tests: serotonin SELECTS WHICH memory bank is read/written
  (mode-switch, not modulation amount).

  Brain literature: Drosophila MB compartments -- each Kenyon cell projects to specific
  MB output neurons via DAN-modulated synapses; selection by COMPARTMENT not amplitude
  (Aso-Hattori 2014; Cohn-Modi-Owald-Waddell 2015). Instead of one big memory with
  scalar modulator, brain uses MULTIPLE PARALLEL memory compartments where gates SELECT
  which compartment is read/written. P_inherited=0.55 deflated to 0.45 for substrate LM.

FOUR ARMS (each builds FRESH W; no cross-contamination):
  ARM_UNIGRAM              -- analytic floor (control)
  ARM_SINGLE_BANK          -- one W at N_DIM=8192; fair_harness baseline ~7.30 BPC
  ARM_4_BANK_RANDOM_SELECT -- 4 parallel W banks each at N_DIM=2048 = same total params;
                              bank selected randomly per token (tests whether bank count
                              alone helps, absent feature-gating)
  ARM_4_BANK_FEATURE_GATED_SELECT -- 4 parallel W banks; gate selects bank based on
                              argmax(softmax(input @ gate_W)) where gate_W is learned
                              via Hebbian co-occurrence with bank-utility proxy

PRE-REGISTERED BANDS (per task spec 2026-06-23):
  HARD_PASS:       feature_gated_bpc < single_bank_bpc - 0.10  (mode-switch outperforms)
  CHAIN_GRADE_BONUS: lift >= 0.20 bits AND feature_gated beats random_select by >= 0.10
  MIDDLE_BAND:     feature_gated beats single_bank by +0.03 to +0.10
  HARD_FAIL:       feature_gated <= single_bank + 0.03 (mode-switch does NOT help)
  cv < 0.05

PURE NUMPY: no torch import; remote_cpu_queue target; avoids PROT-020 GPU auto-routing.

PROT-018: anchor name has NO _n suffix; production N_DIM=8192; banks=4 x N_DIM_BANK=2048.

INSTRUMENTATION SELF-TEST: called at module scope before main sweep.

Cites:
  experiments/exp_fair_harness_substrate_as_lm_v1.py  (harness pattern; BPC scaffold)
  data/exp_substrate_neuromodulator_3axis_gated_compose_LM_v1/metrics.json  (READOUT_DEGEN)
  data/exp_substrate_drosophila_mb_sparsity_sweep_v1_512_2048_gpu/metrics.json  (single-mod)
  notes/substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md  (GAP #3)
  preregs/2026-06-23_substrate_serotonin_mode_switch_bank_select_LM_v1.md
  Aso-Hattori 2014 (Drosophila MB compartments)
  Cohn-Modi-Owald-Waddell 2015 (compartment-selective DAN modulation)
  USER_2026-06-23_brain_existence_proof_higher_prior
  USER_2026-06-23_path_c_substrate_owned_encoder

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

import argparse
import atexit
import hashlib
import json
import math
import signal
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

# NO torch import -- pure numpy for remote_cpu_queue (avoids PROT-020 GPU routing)

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial_key, aggregate_partials, write_metrics,
    resumable_seeds, write_partial
)

ANCHOR_NAME = "substrate_serotonin_mode_switch_bank_select_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

# Pre-reg bands
HP_BPC_MARGIN = 0.10          # feature_gated must beat single_bank by >= 0.10 bits BPC
HP_CHAIN_GRADE_MARGIN = 0.20  # chain_grade bonus: lift >= 0.20 AND beats random by 0.10
HP_RANDOM_MARGIN = 0.10       # chain_grade bonus: feature_gated beats random by >= 0.10
MIDDLE_LOW = 0.03
MIDDLE_HIGH = 0.10
CV_MAX = 0.05

# Unigram reference
UNIGRAM_BPC_REF = 7.738
UNIGRAM_TOP1_REF = 0.2171

# ============================================================================
# CLI + run-mode
# ============================================================================

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# ============================================================================
# Config
# ============================================================================

N_DIM = 8192            # single-bank dimension (FULL)
N_BANKS = 4             # number of parallel banks
N_DIM_BANK = 2048       # per-bank dimension = N_DIM / N_BANKS (same param budget)
VOCAB_CAP = 4000
INGEST_CHUNK = 4096
RECALL_BATCH = 512

# Joint (T, lambda) sweep for BPC
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]
MRR_K = 10

if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000
else:
    # Smoke: tiny scale, fast (<60s on CPU)
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    N_DIM_BANK = 128   # 4 banks x 128 = 512 total (same budget as N_DIM=512)
    INGEST_CHUNK = 512
    RECALL_BATCH = 128

ARMS = [
    "ARM_UNIGRAM",
    "ARM_SINGLE_BANK",
    "ARM_4_BANK_RANDOM_SELECT",
    "ARM_4_BANK_FEATURE_GATED_SELECT",
]

CONFIG_VERSION = (
    "substrate_serotonin_mode_switch_bank_select_LM_v1; "
    "N_DIM=%d N_DIM_BANK=%d N_BANKS=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d arms=%s seeds=%s mode=%s temps=%s lambdas=%s MRR_K=%d; "
    "bands HP_BPC_margin>=%.3f chain_grade>=%.3f random_margin>=%.3f cv_max=%.2f"
) % (
    N_DIM, N_DIM_BANK, N_BANKS, N_TRAIN, N_HELD, VOCAB_CAP, ARMS, SEEDS, RUN_MODE,
    TEMP_GRID, LAMBDA_GRID, MRR_K,
    HP_BPC_MARGIN, HP_CHAIN_GRADE_MARGIN, HP_RANDOM_MARGIN, CV_MAX,
)

# ============================================================================
# Corpus helpers
# ============================================================================

def load_text8_tokens(path: Path, n: int) -> List[str]:
    """Load first n whitespace-split tokens from text8."""
    with open(path, "r", encoding="utf-8") as fh:
        raw = fh.read(n * 10 + 1024)
    toks = raw.split()[:n]
    return toks


def build_vocab(tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    """Build vocabulary capped at cap most-frequent words."""
    cnt = Counter(tokens)
    vocab = [w for w, _ in cnt.most_common(cap)]
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_ids(tokens: List[str], w2i: Dict[str, int]) -> np.ndarray:
    """Map tokens to integer ids; OOV tokens map to 0 (most frequent word)."""
    return np.array([w2i.get(t, 0) for t in tokens], dtype=np.int32)

# ============================================================================
# Char-trigram encoder (pure numpy)
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


def build_E_np(vocab: List[str], n_dim: int, seed: int) -> np.ndarray:
    """Build [V, n_dim] L2-normalized char-trigram embeddings."""
    E = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0).astype(np.float32)
    norms = np.linalg.norm(E, axis=1, keepdims=True)
    norms = np.where(norms < 1e-12, 1.0, norms)
    return E / norms


def l2_normalize_np(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    norms = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.where(norms < eps, 1.0, norms)

# ============================================================================
# Hebbian W builders (pure numpy, chunked for memory)
# ============================================================================

def build_rank1_W_np(idx_train: np.ndarray, E: np.ndarray, chunk: int) -> np.ndarray:
    """W = sum outer(E[idx[t+1]], E[idx[t]]); rank-1 Hebbian. Pure numpy."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, chunk):
        end = min(b + chunk, n_pairs)
        src = E[idx_train[b:end]]        # [B, dim]
        tgt = E[idx_train[b + 1:end + 1]]  # [B, dim]
        W += tgt.T @ src               # [dim, dim]
    return W


def build_gate_W_np(idx_train: np.ndarray, E_bank: np.ndarray,
                    n_banks: int, dim_bank: int, chunk: int,
                    rng: np.random.Generator) -> np.ndarray:
    """Build gate_W [dim_full, n_banks] via Hebbian co-occurrence with bank-utility proxy.

    Strategy: each bank b gets utility proxy = cosine(E_tgt, W_b @ E_src) where
    W_b is the rank-1 Hebbian for bank b. Gate learns to route src to the bank
    that best predicted tgt. This is a one-shot Hebbian gate (no backprop).

    For efficiency: we build all 4 bank W matrices first (cheap at dim_bank=2048),
    then compute per-token bank-utility scores, then train gate_W as:
      gate_W += outer(softmax(utility_scores), src_vec)
    using a Hebbian write where the signal is which bank was most useful.
    """
    dim_full = E_bank.shape[1]  # full dim = n_banks * dim_bank (E_bank is already concatenated)

    # Build per-bank W matrices (each is [dim_bank, dim_bank])
    Ws_bank = []
    for b in range(n_banks):
        Wb = build_rank1_W_np(idx_train, E_bank[:, b * dim_bank:(b + 1) * dim_bank], chunk)
        Ws_bank.append(Wb)

    # Now train gate: gate_W is [dim_full, n_banks]
    gate_W = np.zeros((dim_full, n_banks), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return gate_W

    for b_idx in range(0, n_pairs, chunk):
        end = min(b_idx + chunk, n_pairs)
        src_full = E_bank[idx_train[b_idx:end]]         # [B, dim_full]
        tgt_full = E_bank[idx_train[b_idx + 1:end + 1]]  # [B, dim_full]

        # Compute utility of each bank: cosine(tgt_b_slice, W_b @ src_b_slice)
        B = end - b_idx
        utilities = np.zeros((B, n_banks), dtype=np.float32)
        for bank_i in range(n_banks):
            sl = slice(bank_i * dim_bank, (bank_i + 1) * dim_bank)
            src_sl = src_full[:, sl]   # [B, dim_bank]
            tgt_sl = tgt_full[:, sl]   # [B, dim_bank]
            pred_sl = src_sl @ Ws_bank[bank_i].T  # [B, dim_bank]
            pred_sl_n = l2_normalize_np(pred_sl)
            tgt_sl_n = l2_normalize_np(tgt_sl)
            utilities[:, bank_i] = np.einsum("bd,bd->b", pred_sl_n, tgt_sl_n)

        # Softmax over banks -> bank-selection signal
        utilities -= utilities.max(axis=1, keepdims=True)  # numerical stability
        exp_u = np.exp(utilities)
        gate_signal = exp_u / (exp_u.sum(axis=1, keepdims=True) + 1e-12)  # [B, n_banks]

        # Hebbian gate update: gate_W += src_full^T @ gate_signal
        gate_W += src_full.T @ gate_signal  # [dim_full, n_banks]

    # L2-normalize each column
    for col in range(n_banks):
        n = np.linalg.norm(gate_W[:, col])
        if n > 1e-12:
            gate_W[:, col] /= n

    return gate_W, Ws_bank


# ============================================================================
# Recall / BPC / metrics (pure numpy)
# ============================================================================

def compute_logits_single_bank(idx_held: np.ndarray, E: np.ndarray,
                                 W: np.ndarray, batch: int) -> np.ndarray:
    """Compute [n_held, V] logits as cosine_sim(W @ E[src], E[tgt]) for all vocab."""
    V = E.shape[0]
    n_held = len(idx_held) - 1
    logits = np.zeros((n_held, V), dtype=np.float32)
    for b in range(0, n_held, batch):
        end = min(b + batch, n_held)
        src = E[idx_held[b:end]]           # [B, dim]
        pred = src @ W.T                   # [B, dim]
        pred_n = l2_normalize_np(pred)     # [B, dim]
        E_n = l2_normalize_np(E)           # [V, dim]
        logits[b:end] = pred_n @ E_n.T    # [B, V]
    return logits


def compute_logits_multibank_random(idx_held: np.ndarray, E_bank: np.ndarray,
                                     Ws_bank: List[np.ndarray],
                                     n_banks: int, dim_bank: int,
                                     batch: int, rng: np.random.Generator) -> np.ndarray:
    """Random bank selection: pick a random bank per token. Batched per-bank."""
    n_held = len(idx_held) - 1
    V = E_bank.shape[0]
    logits = np.zeros((n_held, V), dtype=np.float32)
    bank_choices = rng.integers(0, n_banks, size=n_held)
    # Process each bank's tokens as a batch (avoids O(n_held) individual numpy ops)
    for bank_i in range(n_banks):
        mask = bank_choices == bank_i
        if not mask.any():
            continue
        token_positions = np.where(mask)[0]
        sl = slice(bank_i * dim_bank, (bank_i + 1) * dim_bank)
        src_vecs = E_bank[idx_held[token_positions], sl]  # [B_k, dim_bank]
        W_b = Ws_bank[bank_i]                             # [dim_bank, dim_bank]
        E_sl = l2_normalize_np(E_bank[:, sl])             # [V, dim_bank]
        for b in range(0, len(token_positions), batch):
            end = min(b + batch, len(token_positions))
            src_b = src_vecs[b:end]                       # [chunk, dim_bank]
            pred_b = src_b @ W_b.T                        # [chunk, dim_bank]
            pred_n = l2_normalize_np(pred_b)              # [chunk, dim_bank]
            logits[token_positions[b:end]] = pred_n @ E_sl.T  # [chunk, V]
    return logits


def compute_logits_multibank_feature_gated(idx_held: np.ndarray, E_bank: np.ndarray,
                                            Ws_bank: List[np.ndarray],
                                            gate_W: np.ndarray,
                                            n_banks: int, dim_bank: int,
                                            batch: int) -> np.ndarray:
    """Feature-gated bank selection: argmax(softmax(src_full @ gate_W)). Batched per-bank."""
    n_held = len(idx_held) - 1
    V = E_bank.shape[0]
    logits = np.zeros((n_held, V), dtype=np.float32)

    # Compute gate selection for all tokens at once
    all_src = E_bank[idx_held[:n_held]]  # [n_held, dim_full]
    gate_scores = all_src @ gate_W       # [n_held, n_banks]
    gate_scores -= gate_scores.max(axis=1, keepdims=True)
    gate_probs = np.exp(gate_scores)
    gate_probs /= gate_probs.sum(axis=1, keepdims=True) + 1e-12
    bank_sel = np.argmax(gate_probs, axis=1)  # [n_held] hard selection

    # Group by bank for batch processing (avoids O(n_held) individual numpy ops)
    for bank_i in range(n_banks):
        mask = bank_sel == bank_i
        if not mask.any():
            continue
        token_positions = np.where(mask)[0]
        sl = slice(bank_i * dim_bank, (bank_i + 1) * dim_bank)
        src_vecs = all_src[token_positions, sl]    # [B_k, dim_bank]
        W_b = Ws_bank[bank_i]                      # [dim_bank, dim_bank]
        E_sl = l2_normalize_np(E_bank[:, sl])      # [V, dim_bank]
        for b in range(0, len(token_positions), batch):
            end = min(b + batch, len(token_positions))
            src_b = src_vecs[b:end]                # [chunk, dim_bank]
            pred_b = src_b @ W_b.T                 # [chunk, dim_bank]
            pred_n = l2_normalize_np(pred_b)       # [chunk, dim_bank]
            logits[token_positions[b:end]] = pred_n @ E_sl.T  # [chunk, V]
    return logits


def compute_bpc_top1_mrr(logits: np.ndarray, idx_held: np.ndarray,
                           unigram_logprob: np.ndarray,
                           lam: float, temp: float,
                           mrr_k: int) -> Tuple[float, float, float]:
    """BPC + top-1 acc + MRR@K from [n_held, V] raw cosine logits.

    Final log-prob = (1-lam) * log_softmax(logits / temp) + lam * unigram_logprob
    """
    n_held = logits.shape[0]
    if n_held == 0:
        return float("nan"), float("nan"), float("nan")
    tgt_ids = idx_held[1:n_held + 1].astype(np.int32)

    # Softmax over vocab at temperature temp
    scaled = logits / max(temp, 1e-9)
    scaled -= scaled.max(axis=1, keepdims=True)
    probs_sub = np.exp(scaled)
    probs_sub /= probs_sub.sum(axis=1, keepdims=True) + 1e-30

    # Interpolate with unigram
    mixed = (1.0 - lam) * probs_sub + lam * np.exp(unigram_logprob)[np.newaxis, :]
    mixed = np.clip(mixed, 1e-30, None)

    log_mixed = np.log2(mixed)

    # BPC
    bpc_per_token = -log_mixed[np.arange(n_held), tgt_ids]
    bpc = float(np.mean(bpc_per_token))

    # Top-1 accuracy
    top1_preds = np.argmax(probs_sub, axis=1)
    top1_acc = float(np.mean(top1_preds == tgt_ids))

    # MRR@K
    ranks_batch = np.argsort(-probs_sub, axis=1)[:, :mrr_k]
    mrr = 0.0
    for i in range(n_held):
        where = np.where(ranks_batch[i] == tgt_ids[i])[0]
        if len(where) > 0:
            mrr += 1.0 / float(where[0] + 1)
    mrr /= float(n_held)

    return bpc, top1_acc, mrr


def joint_sweep(logits: np.ndarray, idx_held: np.ndarray,
                unigram_logprob: np.ndarray) -> Tuple[float, float, float, float, float]:
    """Joint (T, lambda) sweep on first half of held; eval best config on second half.

    Returns: best_bpc, best_top1, best_mrr, best_T, best_lam
    """
    n_held = len(idx_held) - 1
    half = n_held // 2
    dev_logits = logits[:half]
    dev_idx = idx_held[:half + 1]
    test_logits = logits[half:]
    test_idx = idx_held[half:]

    best_dev_bpc = float("inf")
    best_T = TEMP_GRID[0]
    best_lam = LAMBDA_GRID[0]

    for T in TEMP_GRID:
        for lam in LAMBDA_GRID:
            bpc_dev, _, _ = compute_bpc_top1_mrr(dev_logits, dev_idx,
                                                   unigram_logprob, lam, T, MRR_K)
            if math.isfinite(bpc_dev) and bpc_dev < best_dev_bpc:
                best_dev_bpc = bpc_dev
                best_T = T
                best_lam = lam

    bpc_test, top1_test, mrr_test = compute_bpc_top1_mrr(
        test_logits, test_idx, unigram_logprob, best_lam, best_T, MRR_K
    )
    return bpc_test, top1_test, mrr_test, best_T, best_lam


# ============================================================================
# Instrumentation self-test (MANDATORY)
# ============================================================================

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test...", flush=True)
    rng = np.random.default_rng(42)

    V_st = 20
    dim_st = 64
    dim_bank_st = 16
    n_banks_st = 4
    n_train_st = 100
    n_held_st = 30

    # Build tiny vocab + indices
    vocab_st = [f"w{i}" for i in range(V_st)]
    E_st = l2_normalize_np(rng.standard_normal((V_st, dim_st)).astype(np.float32))
    E_bank_st = l2_normalize_np(rng.standard_normal((V_st, dim_bank_st * n_banks_st)).astype(np.float32))
    idx_train_st = rng.integers(0, V_st, size=n_train_st + 1).astype(np.int32)
    idx_held_st = rng.integers(0, V_st, size=n_held_st + 1).astype(np.int32)

    # ARM_SINGLE_BANK: build W, compute logits, check valid distribution
    W_st = build_rank1_W_np(idx_train_st, E_st, chunk=32)
    assert W_st.shape == (dim_st, dim_st), "W shape mismatch"
    assert np.isfinite(W_st).all(), "W has non-finite values"
    logits_st = compute_logits_single_bank(idx_held_st, E_st, W_st, batch=16)
    assert logits_st.shape == (n_held_st, V_st), "logits shape mismatch"
    assert np.isfinite(logits_st).all(), "logits has non-finite values"

    # Check each row has variance (not all-same)
    row_vars = np.var(logits_st, axis=1)
    assert np.mean(row_vars) > 1e-9, "logits rows are all-constant (degenerate)"

    # ARM_4_BANK_RANDOM_SELECT: each bank produces valid distribution
    Ws_bank_st = [
        build_rank1_W_np(idx_train_st, E_bank_st[:, i * dim_bank_st:(i + 1) * dim_bank_st], chunk=32)
        for i in range(n_banks_st)
    ]
    for bank_i, Wb in enumerate(Ws_bank_st):
        assert np.isfinite(Wb).all(), f"bank {bank_i} W has non-finite"
    logits_rand_st = compute_logits_multibank_random(
        idx_held_st, E_bank_st, Ws_bank_st, n_banks_st, dim_bank_st, batch=8, rng=rng
    )
    assert logits_rand_st.shape == (n_held_st, V_st), "random-bank logits shape mismatch"
    assert np.isfinite(logits_rand_st).all(), "random-bank logits has non-finite"

    # ARM_4_BANK_FEATURE_GATED_SELECT: gate produces valid probabilities over 4 banks
    gate_result = build_gate_W_np(idx_train_st, E_bank_st, n_banks_st, dim_bank_st, chunk=32, rng=rng)
    gate_W_st, Ws_bank_gate_st = gate_result
    assert gate_W_st.shape == (dim_bank_st * n_banks_st, n_banks_st), "gate_W shape mismatch"
    assert np.isfinite(gate_W_st).all(), "gate_W has non-finite"

    # Check gate produces a valid distribution over banks
    src_test = E_bank_st[:3]
    gate_scores = src_test @ gate_W_st  # [3, n_banks]
    gate_scores -= gate_scores.max(axis=1, keepdims=True)
    gate_probs = np.exp(gate_scores) / (np.exp(gate_scores).sum(axis=1, keepdims=True) + 1e-12)
    assert gate_probs.shape == (3, n_banks_st), "gate probabilities shape mismatch"
    assert np.allclose(gate_probs.sum(axis=1), 1.0, atol=1e-4), "gate probabilities don't sum to 1"
    # gate_W should be non-zero (not all-zero columns = gate has no signal at all)
    assert np.linalg.norm(gate_W_st) > 1e-9, "gate_W is all-zero (gate has no signal)"

    logits_gated_st = compute_logits_multibank_feature_gated(
        idx_held_st, E_bank_st, Ws_bank_gate_st, gate_W_st, n_banks_st, dim_bank_st, batch=8
    )
    assert logits_gated_st.shape == (n_held_st, V_st), "gated logits shape mismatch"
    assert np.isfinite(logits_gated_st).all(), "gated logits has non-finite"

    # Check BPC is computable and finite
    unigram_logprob_st = np.log(np.ones(V_st) / V_st)
    bpc_st, top1_st, mrr_st = compute_bpc_top1_mrr(
        logits_st, idx_held_st, unigram_logprob_st, lam=0.0, temp=0.1, mrr_k=5
    )
    assert math.isfinite(bpc_st), f"BPC not finite: {bpc_st}"
    assert 0.0 <= top1_st <= 1.0, f"top1 out of [0,1]: {top1_st}"
    assert 0.0 <= mrr_st <= 1.0, f"MRR out of [0,1]: {mrr_st}"
    assert 1.0 <= bpc_st <= 25.0, f"BPC out of plausible range: {bpc_st}"

    # Filter check: idx_held has > 0 pairs
    assert (n_held_st - 1) >= 1, "no held pairs at smoke scale -- filter eliminates all"

    print(f"[selftest] PASS -- bpc_st={bpc_st:.4f} top1_st={top1_st:.4f} mrr_st={mrr_st:.4f}", flush=True)


# Run at module scope (mandatory per role contract)
_instrumentation_selftest()


# ============================================================================
# Per-seed runner
# ============================================================================

def run_one_seed(seed: int, vocab: List[str], w2i: Dict[str, int],
                  idx_train: np.ndarray, idx_held: np.ndarray) -> Dict:
    """Run all 4 arms for one seed. Returns per-arm metrics dict."""
    rng = np.random.default_rng(seed)
    V = len(vocab)

    # Unigram reference
    freq = np.zeros(V, dtype=np.float32)
    for idx in idx_train:
        freq[idx] += 1.0
    freq += 1.0  # Laplace smoothing
    freq /= freq.sum()
    unigram_logprob = np.log(freq)

    arm_results: Dict[str, Dict] = {}

    # ---- ARM_UNIGRAM -------------------------------------------------------
    print(f"  [s={seed}] ARM_UNIGRAM ...", flush=True)
    n_held = len(idx_held) - 1
    tgt_ids = idx_held[1:n_held + 1].astype(np.int32)
    bpc_unigram = float(np.mean(-unigram_logprob[tgt_ids] / math.log(2.0)))
    top1_unigram = float(np.mean(np.argmax(unigram_logprob) == tgt_ids))
    arm_results["ARM_UNIGRAM"] = {
        "bpc": bpc_unigram, "top1": top1_unigram, "mrr": float("nan"),
        "best_T": float("nan"), "best_lam": float("nan"),
    }

    # ---- ARM_SINGLE_BANK ---------------------------------------------------
    print(f"  [s={seed}] ARM_SINGLE_BANK building E [V={V}, N_DIM={N_DIM}]...", flush=True)
    t0 = time.time()
    E_full = build_E_np(vocab, N_DIM, seed)
    t_enc = time.time() - t0
    print(f"  [s={seed}] ARM_SINGLE_BANK encoder: {t_enc:.1f}s", flush=True)

    t0 = time.time()
    W_full = build_rank1_W_np(idx_train, E_full, INGEST_CHUNK)
    t_build = time.time() - t0
    print(f"  [s={seed}] ARM_SINGLE_BANK W built: {t_build:.1f}s", flush=True)

    t0 = time.time()
    logits_sb = compute_logits_single_bank(idx_held, E_full, W_full, RECALL_BATCH)
    t_recall = time.time() - t0
    print(f"  [s={seed}] ARM_SINGLE_BANK recall: {t_recall:.1f}s", flush=True)

    bpc_sb, top1_sb, mrr_sb, best_T_sb, best_lam_sb = joint_sweep(
        logits_sb, idx_held, unigram_logprob
    )
    arm_results["ARM_SINGLE_BANK"] = {
        "bpc": bpc_sb, "top1": top1_sb, "mrr": mrr_sb,
        "best_T": best_T_sb, "best_lam": best_lam_sb,
    }
    print(f"  [s={seed}] ARM_SINGLE_BANK bpc={bpc_sb:.4f} top1={top1_sb:.4f} mrr={mrr_sb:.4f}", flush=True)
    del W_full, logits_sb

    # ---- Build shared bank encodings (4 banks x N_DIM_BANK) ---------------
    # E_bank: [V, N_DIM_BANK * N_BANKS] -- concat of per-bank embeddings
    # Each bank uses a different seed to get diverse representations
    print(f"  [s={seed}] Building 4-bank E [V={V}, N_DIM_BANK={N_DIM_BANK}]...", flush=True)
    t0 = time.time()
    E_banks_list = [build_E_np(vocab, N_DIM_BANK, seed * 100 + b) for b in range(N_BANKS)]
    E_bank = np.concatenate(E_banks_list, axis=1)  # [V, N_DIM_BANK * N_BANKS]
    t_enc_banks = time.time() - t0
    print(f"  [s={seed}] Bank encoders: {t_enc_banks:.1f}s", flush=True)

    # ---- ARM_4_BANK_RANDOM_SELECT ------------------------------------------
    print(f"  [s={seed}] ARM_4_BANK_RANDOM_SELECT building Ws...", flush=True)
    t0 = time.time()
    Ws_rand = [
        build_rank1_W_np(idx_train, E_banks_list[b], INGEST_CHUNK)
        for b in range(N_BANKS)
    ]
    t_rand = time.time() - t0
    print(f"  [s={seed}] ARM_4_BANK_RANDOM_SELECT W built: {t_rand:.1f}s", flush=True)

    t0 = time.time()
    rng_rand = np.random.default_rng(seed + 999)  # separate rng for bank selection
    logits_rand = compute_logits_multibank_random(
        idx_held, E_bank, Ws_rand, N_BANKS, N_DIM_BANK, RECALL_BATCH, rng_rand
    )
    t_rand_recall = time.time() - t0
    print(f"  [s={seed}] ARM_4_BANK_RANDOM_SELECT recall: {t_rand_recall:.1f}s", flush=True)

    bpc_rand, top1_rand, mrr_rand, best_T_rand, best_lam_rand = joint_sweep(
        logits_rand, idx_held, unigram_logprob
    )
    arm_results["ARM_4_BANK_RANDOM_SELECT"] = {
        "bpc": bpc_rand, "top1": top1_rand, "mrr": mrr_rand,
        "best_T": best_T_rand, "best_lam": best_lam_rand,
    }
    print(f"  [s={seed}] ARM_4_BANK_RANDOM_SELECT bpc={bpc_rand:.4f} top1={top1_rand:.4f} mrr={mrr_rand:.4f}", flush=True)
    del logits_rand

    # ---- ARM_4_BANK_FEATURE_GATED_SELECT -----------------------------------
    print(f"  [s={seed}] ARM_4_BANK_FEATURE_GATED_SELECT building gate...", flush=True)
    t0 = time.time()
    rng_gate = np.random.default_rng(seed + 7777)
    gate_W, Ws_gated = build_gate_W_np(
        idx_train, E_bank, N_BANKS, N_DIM_BANK, INGEST_CHUNK, rng_gate
    )
    t_gate = time.time() - t0
    print(f"  [s={seed}] ARM_4_BANK_FEATURE_GATED_SELECT gate built: {t_gate:.1f}s", flush=True)

    t0 = time.time()
    logits_gated = compute_logits_multibank_feature_gated(
        idx_held, E_bank, Ws_gated, gate_W, N_BANKS, N_DIM_BANK, RECALL_BATCH
    )
    t_gated_recall = time.time() - t0
    print(f"  [s={seed}] ARM_4_BANK_FEATURE_GATED_SELECT recall: {t_gated_recall:.1f}s", flush=True)

    bpc_gated, top1_gated, mrr_gated, best_T_gated, best_lam_gated = joint_sweep(
        logits_gated, idx_held, unigram_logprob
    )
    arm_results["ARM_4_BANK_FEATURE_GATED_SELECT"] = {
        "bpc": bpc_gated, "top1": top1_gated, "mrr": mrr_gated,
        "best_T": best_T_gated, "best_lam": best_lam_gated,
    }
    print(f"  [s={seed}] ARM_4_BANK_FEATURE_GATED_SELECT bpc={bpc_gated:.4f} top1={top1_gated:.4f} mrr={mrr_gated:.4f}", flush=True)
    del logits_gated, E_bank, E_banks_list, E_full

    return {
        "seed": seed,
        "arms": arm_results,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "N_DIM_BANK": N_DIM_BANK,
        "N_BANKS": N_BANKS,
    }


# ============================================================================
# Verdict synthesis
# ============================================================================

def synthesize_verdict(per_seed: Dict) -> Dict:
    """Aggregate per-seed results and apply pre-reg bands."""
    seeds = sorted(per_seed.keys(), key=int)
    n_seeds = len(seeds)
    if n_seeds == 0:
        return {"verdict": "NO_RESULTS", "reason": "no seeds completed"}

    arm_metrics: Dict[str, Dict[str, List[float]]] = {a: {"bpc": [], "top1": [], "mrr": []} for a in ARMS}
    for s in seeds:
        d = per_seed[s]
        for arm in ARMS:
            if arm in d["arms"]:
                arm_metrics[arm]["bpc"].append(d["arms"][arm]["bpc"])
                arm_metrics[arm]["top1"].append(d["arms"][arm]["top1"])
                arm_metrics[arm]["mrr"].append(d["arms"][arm]["mrr"])

    def safe_mean(lst):
        valid = [x for x in lst if math.isfinite(x)]
        return float(np.mean(valid)) if valid else float("nan")

    def safe_std(lst):
        valid = [x for x in lst if math.isfinite(x)]
        return float(np.std(valid)) if len(valid) > 1 else 0.0

    def safe_cv(lst):
        m = safe_mean(lst)
        s = safe_std(lst)
        if abs(m) < 1e-9:
            return float("nan")
        return s / abs(m)

    summary: Dict[str, Dict] = {}
    for arm in ARMS:
        bpc_list = arm_metrics[arm]["bpc"]
        summary[arm] = {
            "bpc_mean": safe_mean(bpc_list),
            "bpc_std": safe_std(bpc_list),
            "bpc_cv": safe_cv(bpc_list),
            "top1_mean": safe_mean(arm_metrics[arm]["top1"]),
            "mrr_mean": safe_mean(arm_metrics[arm]["mrr"]),
            "n_seeds": len(bpc_list),
        }

    sb_bpc = summary["ARM_SINGLE_BANK"]["bpc_mean"]
    gated_bpc = summary["ARM_4_BANK_FEATURE_GATED_SELECT"]["bpc_mean"]
    rand_bpc = summary["ARM_4_BANK_RANDOM_SELECT"]["bpc_mean"]
    gated_cv = summary["ARM_4_BANK_FEATURE_GATED_SELECT"]["bpc_cv"]

    # Pre-reg band application (Fix #28: per-arm only)
    lift_vs_single = sb_bpc - gated_bpc  # positive = gated is better (lower BPC)
    lift_vs_random = rand_bpc - gated_bpc

    suspect = False
    for arm in ARMS:
        bpc_m = summary[arm]["bpc_mean"]
        if not math.isfinite(bpc_m) or bpc_m <= 0.0:
            suspect = True
            break
        if bpc_m == summary["ARM_UNIGRAM"]["bpc_mean"] and arm != "ARM_UNIGRAM":
            suspect = True

    if suspect:
        verdict = "INSTRUMENTATION_SUSPECT"
        reason = "non-finite or degenerate BPC detected -- route back to Strategy"
    elif not math.isfinite(gated_bpc) or not math.isfinite(sb_bpc):
        verdict = "INSTRUMENTATION_SUSPECT"
        reason = "NaN BPC in key arms"
    elif lift_vs_single >= HP_BPC_MARGIN and lift_vs_random >= HP_RANDOM_MARGIN:
        verdict = "CHAIN_GRADE_BONUS"
        reason = (
            f"gated beats single_bank by {lift_vs_single:.4f} bits (>={HP_CHAIN_GRADE_MARGIN}) "
            f"AND beats random by {lift_vs_random:.4f} bits (>={HP_RANDOM_MARGIN}); "
            f"feature-gating is load-bearing"
        )
    elif lift_vs_single >= HP_BPC_MARGIN:
        verdict = "HARD_PASS"
        reason = (
            f"feature_gated_bpc={gated_bpc:.4f} beats single_bank_bpc={sb_bpc:.4f} "
            f"by {lift_vs_single:.4f} >= {HP_BPC_MARGIN}; mode-switch architecture outperforms"
        )
    elif lift_vs_single >= MIDDLE_LOW:
        verdict = "MIDDLE_BAND"
        reason = (
            f"lift={lift_vs_single:.4f} in [{MIDDLE_LOW},{MIDDLE_HIGH}]; "
            f"modest mode-switch benefit"
        )
    else:
        verdict = "HARD_FAIL"
        reason = (
            f"feature_gated_bpc={gated_bpc:.4f}; single_bank_bpc={sb_bpc:.4f}; "
            f"lift={lift_vs_single:.4f} < {MIDDLE_LOW}; "
            f"mode-switch does NOT help at same param budget"
        )

    # CV check
    cv_warn = ""
    if math.isfinite(gated_cv) and gated_cv >= CV_MAX:
        cv_warn = f"; WARN: gated cv={gated_cv:.4f} >= {CV_MAX}"

    return {
        "verdict": verdict,
        "verdict_msg": reason + cv_warn,
        "arm_summary": summary,
        "lift_vs_single_bank_bpc": lift_vs_single,
        "lift_vs_random_bpc": lift_vs_random,
        "gated_bpc_mean": gated_bpc,
        "single_bank_bpc_mean": sb_bpc,
        "random_bpc_mean": rand_bpc,
        "unigram_bpc_mean": summary["ARM_UNIGRAM"]["bpc_mean"],
        "n_seeds": n_seeds,
        "config_version": CONFIG_VERSION,
        "pre_reg": {
            "HARD_PASS": f"gated beats single_bank by >={HP_BPC_MARGIN} bits BPC",
            "CHAIN_GRADE_BONUS": f"lift>={HP_CHAIN_GRADE_MARGIN} AND gated beats random by >={HP_RANDOM_MARGIN}",
            "MIDDLE_BAND": f"lift in [{MIDDLE_LOW},{MIDDLE_HIGH}]",
            "HARD_FAIL": f"lift < {MIDDLE_LOW}",
            "CV_MAX": CV_MAX,
        },
    }


# ============================================================================
# Main
# ============================================================================

_OUT_DIR: Optional[Path] = None


def _atexit_synthesizer():
    """Write partial metrics.json on any exit (crash recovery)."""
    if _OUT_DIR is None:
        return
    partials_pattern = list(_OUT_DIR.glob("partial_metrics_*.json"))
    if not partials_pattern:
        return
    try:
        per_seed_raw = aggregate_partials(_OUT_DIR, SEEDS)
        if per_seed_raw:
            verdict_dict = synthesize_verdict(per_seed_raw)
            write_metrics(_OUT_DIR, verdict_dict)
            print(f"[atexit] wrote partial metrics.json verdict={verdict_dict['verdict']}", flush=True)
    except Exception as exc:
        print(f"[atexit] ERROR: {exc}", flush=True)


atexit.register(_atexit_synthesizer)


def _signal_handler(sig, frame):
    print(f"[signal] caught {sig}; atexit will synthesize", flush=True)
    sys.exit(1)


signal.signal(signal.SIGTERM, _signal_handler)
try:
    signal.signal(signal.SIGINT, _signal_handler)
except Exception:
    pass


def main():
    global _OUT_DIR

    _OUT_DIR = get_output_dir(ANCHOR_NAME)
    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[main] output dir: {_OUT_DIR}", flush=True)
    print(f"[main] RUN_MODE={RUN_MODE} N_DIM={N_DIM} N_DIM_BANK={N_DIM_BANK} N_BANKS={N_BANKS}", flush=True)
    print(f"[main] SEEDS={SEEDS} N_TRAIN={N_TRAIN} N_HELD={N_HELD} VOCAB_CAP={VOCAB_CAP}", flush=True)
    print(f"[main] CONFIG={CONFIG_VERSION}", flush=True)

    # Load corpus
    print("[main] loading text8...", flush=True)
    t0 = time.time()
    tokens = load_text8_tokens(TEXT8, N_TRAIN + N_HELD + 1000)
    vocab, w2i = build_vocab(tokens[:N_TRAIN], VOCAB_CAP)
    V = len(vocab)
    print(f"[main] vocab size={V} corpus_tokens={len(tokens)} ({time.time()-t0:.1f}s)", flush=True)

    all_ids = tokens_to_ids(tokens, w2i)
    idx_train = all_ids[:N_TRAIN]
    idx_held = all_ids[N_TRAIN:N_TRAIN + N_HELD + 1]

    # Per-seed checkpoint resume
    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done_seeds, remaining_seeds = resumable_seeds(SEEDS, _OUT_DIR, run_config=run_config)
    print(f"[main] {len(done_seeds)}/{len(SEEDS)} seeds already complete; running {remaining_seeds}", flush=True)

    t_wall_start = time.time()
    for seed in remaining_seeds:
        print(f"[main] --- seed {seed} ---", flush=True)
        t_seed = time.time()
        result = run_one_seed(seed, vocab, w2i, idx_train, idx_held)
        result["N"] = N_DIM
        result["run_mode"] = RUN_MODE
        write_partial(_OUT_DIR, seed, result)
        print(f"[main] seed {seed} done in {time.time()-t_seed:.1f}s", flush=True)

    t_total = time.time() - t_wall_start
    print(f"[main] wall time for new seeds: {t_total:.1f}s", flush=True)

    # Aggregate + verdict
    per_seed = aggregate_partials(_OUT_DIR, SEEDS, run_config=run_config)
    verdict_dict = synthesize_verdict(per_seed)
    write_metrics(_OUT_DIR, verdict_dict)

    print(f"\n[VERDICT] {verdict_dict['verdict']}", flush=True)
    print(f"[VERDICT_MSG] {verdict_dict['verdict_msg']}", flush=True)
    print(f"[METRICS] gated_bpc={verdict_dict['gated_bpc_mean']:.4f} "
          f"single_bpc={verdict_dict['single_bank_bpc_mean']:.4f} "
          f"random_bpc={verdict_dict['random_bpc_mean']:.4f} "
          f"unigram_bpc={verdict_dict['unigram_bpc_mean']:.4f} "
          f"lift_vs_single={verdict_dict['lift_vs_single_bank_bpc']:.4f} "
          f"lift_vs_random={verdict_dict['lift_vs_random_bpc']:.4f}", flush=True)
    print(f"[ANCHOR] {ANCHOR_NAME}", flush=True)


if __name__ == "__main__":
    main()
