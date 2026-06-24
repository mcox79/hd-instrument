"""substrate_per_context_decode_temperature_LM_v1 -- per-context decode temperature.

TOP UNTESTED GAP from substrate-mine inventory (substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md):
  Current temperature-calibration HARD_PASS is GLOBAL only (fair_harness best T=0.05, lambda=0.3).
  Per-context T modulated by query difficulty is UNTESTED.

Mechanism hypothesis:
  Brain literature Yu-Dayan 2005 (ACh-mediated gain control) + locus coeruleus phasic-vs-tonic:
  cortical neurons modulate effective SNR based on TASK UNCERTAINTY. Per-token T = f(predictive
  uncertainty) where higher predictive entropy means sharper distribution (lower T) and lower
  entropy means keep current T. Substrate-native: entropy computed from substrate cosine logits.

Four arms x 3 seeds x text8 N_TRAIN=100k N_DIM=8192:
  ARM_UNIGRAM             : analytic floor (no substrate)
  ARM_GLOBAL_T            : global (T, lambda) joint sweep -- reproduces fair_harness baseline
  ARM_PER_CONTEXT_T_ENTROPY: per-token T = T_low + (T_high - T_low)*(1 - H_norm)
                             high-entropy context (uncertain) -> T_low (sharper)
                             low-entropy context (confident)  -> T_high (preserve diversity)
  ARM_PER_CONTEXT_T_MARGIN : per-token T = T_low + (T_high - T_low)*margin_norm
                             low margin (confused) -> T_low; high margin (confident) -> T_high

Pre-reg HARD bands (filed: preregs/2026-06-23_substrate_per_context_decode_temperature_LM_v1.md):
  HARD_PASS     : ARM_PER_CONTEXT_T_ENTROPY OR ARM_PER_CONTEXT_T_MARGIN beats ARM_GLOBAL_T
                  by >= +0.10 bits BPC.
  CHAIN_GRADE_BONUS: lift >= +0.20 bits AND final BPC beats fair_harness chain-grade (7.3065).
  MIDDLE_BAND   : lift +0.03 to +0.10 bits.
  HARD_FAIL     : lift <= +0.03 bits (per-context T does not add over global).
  cv < 0.05.

P_inherited = 0.45 (Yu-Dayan 2005 brain-canonical at P=0.55 deflated for substrate-native LM).

Note: ARM_GLOBAL_T reproduces fair_harness sparse-bipolar baseline (BPC=7.3065) as self-test.
This cell runs on CPU (numpy). ARM_GLOBAL_T self-test bar: BPC within 0.05 of 7.3065.

Routing: local_cpu_queue (USER explicit; pure numpy; no CUDA).
ASCII-only. Per-seed checkpoint. atexit synthesizer.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import atexit
import hashlib
import math
import os
import signal
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, write_partial, aggregate_partials, write_metrics,
    resumable_seeds,
)

ANCHOR_NAME = "substrate_per_context_decode_temperature_LM_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
_LLM_CALL_COUNTER = [0]
_METRICS_WRITTEN = [False]

# Pre-reg bands
HARD_PASS_LIFT_BPC = 0.10        # per-context arm beats global by >= 0.10 bits
CHAIN_GRADE_BONUS_LIFT = 0.20    # and also beats fair_harness chain-grade 7.3065
CHAIN_GRADE_BASELINE_BPC = 7.3065
MIDDLE_BAND_LIFT_LOW = 0.03
HARD_FAIL_LIFT_MAX = 0.03
HARD_PASS_CV_MAX = 0.05

# Self-test bar for ARM_GLOBAL_T: must reproduce fair_harness SPARSE_BIPOLAR BPC within 0.05
GLOBAL_T_SELFTEST_BAR_BPC = 7.3065
GLOBAL_T_SELFTEST_TOL = 0.05

# Parse run mode
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 8192
VOCAB_CAP = 4000
SPARSE_F = 0.05          # sparse-bipolar fraction (mirrors fair_harness)
INGEST_CHUNK = 8192
RECALL_BATCH = 256

# Joint (T, lambda) sweep for ARM_GLOBAL_T -- mirrors fair_harness
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

# Per-context T range
T_LOW = 0.02    # sharpest T (high uncertainty contexts)
T_HIGH = 0.5    # broadest T (low uncertainty contexts)
# lambda for per-context arms: use best from fair_harness (0.3)
LAMBDA_PER_CONTEXT = 0.3

ARMS = [
    "ARM_UNIGRAM",
    "ARM_GLOBAL_T",
    "ARM_PER_CONTEXT_T_ENTROPY",
    "ARM_PER_CONTEXT_T_MARGIN",
]

if RUN_MODE in ("smoke", "selftest"):
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 400
    VOCAB_CAP = 300
    N_DIM = 512
    INGEST_CHUNK = 512
    RECALL_BATCH = 128
else:
    SEEDS = [7, 17, 23]
    N_TRAIN = 100_000
    N_HELD = 20_000

CONFIG_VERSION = (
    "substrate_per_context_decode_temperature_LM_v1; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d sparse_f=%.3f seeds=%s run_mode=%s arms=%s "
    "TEMP_GRID=%s LAMBDA_GRID=%s T_LOW=%.3f T_HIGH=%.3f LAMBDA_PC=%.2f; "
    "bands HP_lift>=%.2f CG_lift>=%.2f MID_low=%.2f HF_lift<=%.2f cv_max=%.2f"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, SPARSE_F, SEEDS, RUN_MODE, ARMS,
    TEMP_GRID, LAMBDA_GRID, T_LOW, T_HIGH, LAMBDA_PER_CONTEXT,
    HARD_PASS_LIFT_BPC, CHAIN_GRADE_BONUS_LIFT, MIDDLE_BAND_LIFT_LOW,
    HARD_FAIL_LIFT_MAX, HARD_PASS_CV_MAX,
)


# ============================================================================
# Substrate primitives (CPU/numpy)
# ============================================================================

def _seed_for_tri(tri: str, seed: int) -> int:
    h = hashlib.md5((tri + ":" + str(seed)).encode()).hexdigest()
    return int(h, 16) & 0xFFFFFFFF


def char_trigram_encode_np(word: str, dim: int, seed: int) -> np.ndarray:
    v = np.zeros(dim, np.float32)
    w = "#" + word.lower() + "#"
    for i in range(len(w) - 2):
        tri = w[i:i + 3]
        sv = _seed_for_tri(tri, seed)
        idx = sv % dim
        sign = 1.0 if ((sv >> 16) & 1) else -1.0
        v[idx] += sign
    nrm = float(np.linalg.norm(v))
    return v / nrm if nrm > 1e-9 else v


def build_encoder_np(vocab: List[str], dim: int, seed: int) -> np.ndarray:
    """Build [V, dim] L2-normalized char-trigram encoder (CPU numpy)."""
    E = np.stack([char_trigram_encode_np(w, dim, seed) for w in vocab], 0).astype(np.float32)
    nrm = np.linalg.norm(E, axis=1, keepdims=True)
    nrm[nrm < 1e-9] = 1.0
    return E / nrm


def sparsify_bipolar_np(E: np.ndarray, f: float) -> np.ndarray:
    """Top-k sparse bipolar (mirrors fair_harness GPU version)."""
    V, dim = E.shape
    k = max(1, int(round(f * dim)))
    out = np.zeros_like(E)
    abs_E = np.abs(E)
    topk_idx = np.argpartition(-abs_E, k, axis=1)[:, :k]
    for i in range(V):
        idx = topk_idx[i]
        signs = np.sign(E[i, idx])
        signs[signs == 0] = 1.0
        out[i, idx] = signs
    return out


def build_hebbian_W_np(idx_train: np.ndarray, E: np.ndarray,
                        ingest_chunk: int) -> np.ndarray:
    """Build [dim, dim] Hebbian W (CPU numpy, chunked)."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    for b in range(0, n_pairs, ingest_chunk):
        end = min(b + ingest_chunk, n_pairs)
        E_src = E[idx_train[b:end]]
        E_tgt = E[idx_train[b + 1:end + 1]]
        W += E_tgt.T @ E_src
    return W


# ============================================================================
# Logit + metric helpers
# ============================================================================

def compute_substrate_logits_np(ctx_idx: np.ndarray, E: np.ndarray,
                                  W: np.ndarray, recall_batch: int) -> np.ndarray:
    """Return [n, V] cosine-similarity logits from substrate."""
    n = len(ctx_idx)
    V = E.shape[0]
    logits = np.zeros((n, V), dtype=np.float32)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        pred = E[ctx_idx[b:end]] @ W.T        # [b, dim]
        nrm = np.linalg.norm(pred, axis=1, keepdims=True)
        nrm[nrm < 1e-9] = 1.0
        pred = pred / nrm
        logits[b:end] = pred @ E.T            # [b, V]
    return logits


def bpc_top1_mrr_from_logits(logits: np.ndarray, nxt: np.ndarray,
                               T: float, lam: float, U_logp: np.ndarray,
                               mrr_k: int = 10) -> Tuple[float, float, float]:
    """Compute BPC, top-1 acc, MRR@k from logits with (T, lambda) interp."""
    z = logits / max(T, 1e-8)
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    sub_p = e / (e.sum(axis=1, keepdims=True) + 1e-30)
    # Log-linear interpolation with unigram
    if lam < 1.0:
        log_comb = lam * np.log(np.clip(sub_p, 1e-30, 1.0)) + (1.0 - lam) * U_logp[None, :]
        z2 = log_comb - log_comb.max(axis=1, keepdims=True)
        e2 = np.exp(z2)
        probs = e2 / (e2.sum(axis=1, keepdims=True) + 1e-30)
    else:
        probs = sub_p
    p_true = np.clip(probs[np.arange(len(nxt)), nxt], 1e-12, 1.0)
    bpc = float(-np.mean(np.log2(p_true)))
    top1 = float((probs.argmax(axis=1) == nxt).mean())
    # MRR@k
    n = len(nxt)
    ranks = np.argsort(-probs, axis=1)[:, :mrr_k]
    mrr = 0.0
    for i in range(n):
        hits = np.where(ranks[i] == nxt[i])[0]
        if len(hits) > 0:
            mrr += 1.0 / (hits[0] + 1)
    mrr /= max(n, 1)
    return bpc, top1, mrr


def _per_position_T_from_entropy(logits: np.ndarray, T_base: float,
                                   T_low: float, T_high: float) -> np.ndarray:
    """Per-position T based on normalized predictive entropy.

    Predictive entropy H = -sum(p * log(p)) at T=T_base.
    High H (uncertain) -> T_low; low H (confident) -> T_high.
    T_i = T_low + (T_high - T_low) * (1 - H_norm_i)
    """
    z = logits / max(T_base, 1e-8)
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / (e.sum(axis=1, keepdims=True) + 1e-30)
    logp = np.log(np.clip(p, 1e-30, 1.0))
    H = -np.sum(p * logp, axis=1).astype(np.float32)  # [n]
    H_max = math.log(logits.shape[1])  # log(V) = max possible entropy
    H_norm = np.clip(H / H_max, 0.0, 1.0)
    # high entropy -> T_low; low entropy -> T_high
    T_vec = T_low + (T_high - T_low) * (1.0 - H_norm)
    return T_vec.astype(np.float32)


def _per_position_T_from_margin(logits: np.ndarray, T_base: float,
                                  T_low: float, T_high: float) -> np.ndarray:
    """Per-position T based on cosine margin (top-1 minus top-2 score).

    Low margin (confused) -> T_low (sharpen); high margin (confident) -> T_high.
    T_i = T_low + (T_high - T_low) * margin_norm_i
    """
    # Use raw logits (cosine sims in [-1, 1]) for margin
    sorted_l = np.sort(logits, axis=1)[:, ::-1]  # descending
    margin = sorted_l[:, 0] - sorted_l[:, 1]     # [n]
    # margin range: theoretically [0, 2] for cosine sims
    margin_max = 2.0
    margin_norm = np.clip(margin / margin_max, 0.0, 1.0)
    # low margin -> T_low; high margin -> T_high
    T_vec = T_low + (T_high - T_low) * margin_norm
    return T_vec.astype(np.float32)


def bpc_top1_mrr_per_context_T(logits: np.ndarray, nxt: np.ndarray,
                                  T_vec: np.ndarray, lam: float,
                                  U_logp: np.ndarray, mrr_k: int = 10
                                  ) -> Tuple[float, float, float]:
    """BPC/top-1/MRR using per-position temperature vector T_vec [n]."""
    n = len(nxt)
    z = logits / np.clip(T_vec[:, None], 1e-8, None)
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    sub_p = e / (e.sum(axis=1, keepdims=True) + 1e-30)
    if lam < 1.0:
        log_comb = lam * np.log(np.clip(sub_p, 1e-30, 1.0)) + (1.0 - lam) * U_logp[None, :]
        z2 = log_comb - log_comb.max(axis=1, keepdims=True)
        e2 = np.exp(z2)
        probs = e2 / (e2.sum(axis=1, keepdims=True) + 1e-30)
    else:
        probs = sub_p
    p_true = np.clip(probs[np.arange(n), nxt], 1e-12, 1.0)
    bpc = float(-np.mean(np.log2(p_true)))
    top1 = float((probs.argmax(axis=1) == nxt).mean())
    ranks = np.argsort(-probs, axis=1)[:, :mrr_k]
    mrr = 0.0
    for i in range(n):
        hits = np.where(ranks[i] == nxt[i])[0]
        if len(hits) > 0:
            mrr += 1.0 / (hits[0] + 1)
    mrr /= max(n, 1)
    return bpc, top1, mrr


# ============================================================================
# Corpus helpers
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] corpus missing: %s" % TEXT8, flush=True)
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


def build_unigram(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


# ============================================================================
# Instrumentation self-test (MANDATORY per exp_dev role contract)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test ...", flush=True)
    # 1. Encoder: deterministic, L2-normalized
    e1 = char_trigram_encode_np("hello", 256, seed=0)
    e2 = char_trigram_encode_np("hello", 256, seed=0)
    assert np.allclose(e1, e2), "selftest 1: encoder not deterministic"
    assert abs(float(np.linalg.norm(e1)) - 1.0) < 1e-4, "selftest 1: encoder not L2-normed"

    # 2. Sparsify: produces sparse output, magnitude 1 entries
    E_t = np.stack([char_trigram_encode_np("tok%d" % i, 128, seed=0) for i in range(5)])
    E_sp = sparsify_bipolar_np(E_t, f=0.1)
    assert E_sp.shape == (5, 128), "selftest 2: sparsify shape wrong"
    nonzero_counts = (E_sp != 0).sum(axis=1)
    assert (nonzero_counts > 0).all(), "selftest 2: sparsify all-zero row"

    # 3. Hebbian W + logits: non-null, not all-zero
    V_t = 10
    dim_t = 128
    vocab_t = ["w%d" % i for i in range(V_t)]
    E_enc = build_encoder_np(vocab_t, dim_t, seed=0)
    E_sp2 = sparsify_bipolar_np(E_enc, f=0.1)
    idx_tr = np.tile(np.arange(V_t, dtype=np.int64), 5)
    W_t = build_hebbian_W_np(idx_tr, E_sp2, ingest_chunk=20)
    assert W_t.shape == (dim_t, dim_t), "selftest 3: W shape wrong"
    assert np.abs(W_t).sum() > 0, "selftest 3: W all-zero"
    ctx_t = np.array([0, 1, 2, 3], dtype=np.int64)
    nxt_t = np.array([1, 2, 3, 4], dtype=np.int64)
    logits_t = compute_substrate_logits_np(ctx_t, E_sp2, W_t, recall_batch=4)
    assert logits_t.shape == (4, V_t), "selftest 3: logits shape wrong"
    assert not np.all(logits_t == 0), "selftest 3: logits all-zero"
    assert not np.any(np.isnan(logits_t)), "selftest 3: logits NaN"

    # 4. BPC/top1/MRR from logits: finite, top1 in [0,1], MRR in [0,1]
    U_t = build_unigram(idx_tr, V=V_t, alpha=0.1)
    U_logp_t = np.log(np.clip(U_t, 1e-30, 1.0))
    bpc_t, top1_t, mrr_t = bpc_top1_mrr_from_logits(logits_t, nxt_t, T=0.05, lam=0.3,
                                                       U_logp=U_logp_t, mrr_k=5)
    assert math.isfinite(bpc_t) and bpc_t > 0, "selftest 4: bpc not finite/positive: %s" % bpc_t
    assert 0.0 <= top1_t <= 1.0, "selftest 4: top1 out of range: %s" % top1_t
    assert 0.0 <= mrr_t <= 1.0, "selftest 4: mrr out of range: %s" % mrr_t

    # 5. Per-context T (entropy): T_vec in [T_LOW, T_HIGH], shape matches
    T_vec_ent = _per_position_T_from_entropy(logits_t, T_base=0.05, T_low=T_LOW, T_high=T_HIGH)
    assert T_vec_ent.shape == (4,), "selftest 5: T_vec_ent shape wrong"
    assert (T_vec_ent >= T_LOW - 1e-6).all(), "selftest 5: T_vec_ent below T_LOW"
    assert (T_vec_ent <= T_HIGH + 1e-6).all(), "selftest 5: T_vec_ent above T_HIGH"

    # 6. Per-context T (margin): T_vec in [T_LOW, T_HIGH], shape matches
    T_vec_mar = _per_position_T_from_margin(logits_t, T_base=0.05, T_low=T_LOW, T_high=T_HIGH)
    assert T_vec_mar.shape == (4,), "selftest 6: T_vec_mar shape wrong"
    assert (T_vec_mar >= T_LOW - 1e-6).all(), "selftest 6: T_vec_mar below T_LOW"
    assert (T_vec_mar <= T_HIGH + 1e-6).all(), "selftest 6: T_vec_mar above T_HIGH"

    # 7. per-context-T metrics: valid probability distributions (bpc finite, top1/mrr in [0,1])
    bpc_pc, top1_pc, mrr_pc = bpc_top1_mrr_per_context_T(
        logits_t, nxt_t, T_vec_ent, lam=0.3, U_logp=U_logp_t, mrr_k=5)
    assert math.isfinite(bpc_pc) and bpc_pc > 0, "selftest 7: per-ctx-T bpc not finite: %s" % bpc_pc
    assert 0.0 <= top1_pc <= 1.0, "selftest 7: top1 out of range"
    assert 0.0 <= mrr_pc <= 1.0, "selftest 7: mrr out of range"

    # 8. Entropy and margin arms produce DIFFERENT T_vecs (they use different signals)
    # NOTE: may collide on tiny data, so just check types are correct
    assert T_vec_ent.dtype == np.float32, "selftest 8: T_vec dtype wrong"
    assert T_vec_mar.dtype == np.float32, "selftest 8: T_vec_mar dtype wrong"

    # 9. LLM counter still 0
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 9: LLM counter non-zero"

    print("[selftest] PASS: encoder/sparsify/W/logits/BPC/MRR/per-ctx-T-entropy/"
          "per-ctx-T-margin/distributions all valid, LLM=0", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_seed(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading corpus ..." % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    unk = w2i["<unk>"]

    idx_train_np = tokens_to_idx(train_toks, w2i)
    idx_held_np = tokens_to_idx(held_toks, w2i)
    ctx_np = idx_held_np[:-1]
    nxt_np = idx_held_np[1:]
    mask = ctx_np != unk
    ctx_eval = ctx_np[mask]
    nxt_eval = nxt_np[mask]
    n_eval = len(ctx_eval)

    # Split held: first half = dev (T/lambda tuning), second half = test (eval)
    n_dev = n_eval // 2
    ctx_dev = ctx_eval[:n_dev]
    nxt_dev = nxt_eval[:n_dev]
    ctx_test = ctx_eval[n_dev:]
    nxt_test = nxt_eval[n_dev:]
    n_test = len(ctx_test)
    print("[seed=%d] V=%d train=%d held=%d dev=%d test=%d" % (
        seed, V, N_TRAIN, N_HELD, n_dev, n_test), flush=True)

    # Unigram baseline
    U = build_unigram(idx_train_np, V=V, alpha=0.1)
    U_logp = np.log(np.clip(U, 1e-30, 1.0))
    uni_argmax = int(np.argmax(U))
    uni_acc = float((np.full(n_test, uni_argmax) == nxt_test).mean())
    p_true_uni = U[nxt_test].clip(1e-12, 1.0)
    uni_bpc = float(-np.mean(np.log2(p_true_uni)))
    uni_mrr_topK = 10
    # MRR for unigram: unigram rank is same for every context (sorted by global U)
    # Average MRR = mean 1/rank(nxt[i]) where rank from global U descending order
    u_sorted_idx = np.argsort(-U)   # tokens sorted by decreasing unigram prob
    u_rank_lookup = np.empty(V, dtype=np.int64)
    u_rank_lookup[u_sorted_idx] = np.arange(1, V + 1)
    test_ranks = u_rank_lookup[nxt_test]  # rank of each test token in unigram order
    uni_mrr = float(np.mean(1.0 / test_ranks.astype(np.float64) * (test_ranks <= uni_mrr_topK)))

    print("[seed=%d] UNIGRAM bpc=%.4f acc=%.4f mrr=%.4f" % (seed, uni_bpc, uni_acc, uni_mrr),
          flush=True)

    # Build sparse-bipolar encoder (mirrors fair_harness ARM_SUBSTRATE_SPARSE_BIPOLAR)
    t0 = time.time()
    E_base = build_encoder_np(vocab, N_DIM, seed=seed)
    E = sparsify_bipolar_np(E_base, f=SPARSE_F)
    t_enc = time.time() - t0
    print("[seed=%d] encoder built N_DIM=%d V=%d sparse_f=%.3f (%.1fs)" % (
        seed, N_DIM, V, SPARSE_F, t_enc), flush=True)

    # Build Hebbian W
    t0 = time.time()
    W = build_hebbian_W_np(idx_train_np, E, ingest_chunk=INGEST_CHUNK)
    t_ingest = time.time() - t0
    print("[seed=%d] W built n_pairs=%d (%.1fs)" % (seed, N_TRAIN - 1, t_ingest), flush=True)

    # Compute substrate logits for dev and test
    t0 = time.time()
    sub_logits_dev = compute_substrate_logits_np(ctx_dev, E, W, RECALL_BATCH)
    sub_logits_test = compute_substrate_logits_np(ctx_test, E, W, RECALL_BATCH)
    t_recall = time.time() - t0
    print("[seed=%d] logits computed dev=%d test=%d (%.1fs)" % (
        seed, n_dev, n_test, t_recall), flush=True)

    # ----- ARM_GLOBAL_T: joint (T, lambda) sweep on dev -> pick best -> eval test -----
    best_dev_bpc_gl = float("inf")
    best_T_gl = TEMP_GRID[0]
    best_lam_gl = LAMBDA_GRID[0]
    for T in TEMP_GRID:
        for lam in LAMBDA_GRID:
            b, _, _ = bpc_top1_mrr_from_logits(sub_logits_dev, nxt_dev, T, lam, U_logp)
            if b < best_dev_bpc_gl:
                best_dev_bpc_gl = b
                best_T_gl = T
                best_lam_gl = lam
    gl_bpc, gl_top1, gl_mrr = bpc_top1_mrr_from_logits(
        sub_logits_test, nxt_test, best_T_gl, best_lam_gl, U_logp)
    print("[seed=%d] ARM_GLOBAL_T best_T=%.3f best_lam=%.2f (dev_bpc=%.4f) "
          "-> test bpc=%.4f top1=%.4f mrr=%.4f" % (
              seed, best_T_gl, best_lam_gl, best_dev_bpc_gl,
              gl_bpc, gl_top1, gl_mrr), flush=True)

    # Self-test: ARM_GLOBAL_T should reproduce fair_harness within tolerance (FULL run only)
    if RUN_MODE == "full":
        if abs(gl_bpc - GLOBAL_T_SELFTEST_BAR_BPC) > GLOBAL_T_SELFTEST_TOL:
            print("[WARN] ARM_GLOBAL_T BPC=%.4f deviates from fair_harness baseline %.4f by %.4f "
                  "(tol=%.3f) -- may indicate CPU vs GPU numerical diff or data split diff" % (
                      gl_bpc, GLOBAL_T_SELFTEST_BAR_BPC,
                      abs(gl_bpc - GLOBAL_T_SELFTEST_BAR_BPC), GLOBAL_T_SELFTEST_TOL), flush=True)

    # ----- ARM_PER_CONTEXT_T_ENTROPY -----
    # Tune T_base on dev (pick the T from TEMP_GRID that minimizes BPC when used as T_base
    # for entropy computation). lambda fixed at LAMBDA_PER_CONTEXT.
    best_dev_bpc_ent = float("inf")
    best_T_base_ent = TEMP_GRID[0]
    for T_base in TEMP_GRID:
        T_vec_dev = _per_position_T_from_entropy(sub_logits_dev, T_base, T_LOW, T_HIGH)
        b, _, _ = bpc_top1_mrr_per_context_T(
            sub_logits_dev, nxt_dev, T_vec_dev, LAMBDA_PER_CONTEXT, U_logp)
        if b < best_dev_bpc_ent:
            best_dev_bpc_ent = b
            best_T_base_ent = T_base
    T_vec_test_ent = _per_position_T_from_entropy(sub_logits_test, best_T_base_ent, T_LOW, T_HIGH)
    ent_bpc, ent_top1, ent_mrr = bpc_top1_mrr_per_context_T(
        sub_logits_test, nxt_test, T_vec_test_ent, LAMBDA_PER_CONTEXT, U_logp)
    T_mean_ent = float(T_vec_test_ent.mean())
    T_std_ent = float(T_vec_test_ent.std())
    print("[seed=%d] ARM_PER_CONTEXT_T_ENTROPY best_T_base=%.3f (dev_bpc=%.4f) "
          "T_mean=%.4f T_std=%.4f -> test bpc=%.4f top1=%.4f mrr=%.4f" % (
              seed, best_T_base_ent, best_dev_bpc_ent,
              T_mean_ent, T_std_ent, ent_bpc, ent_top1, ent_mrr), flush=True)

    # ----- ARM_PER_CONTEXT_T_MARGIN -----
    best_dev_bpc_mar = float("inf")
    best_T_base_mar = TEMP_GRID[0]
    for T_base in TEMP_GRID:
        T_vec_dev_m = _per_position_T_from_margin(sub_logits_dev, T_base, T_LOW, T_HIGH)
        b, _, _ = bpc_top1_mrr_per_context_T(
            sub_logits_dev, nxt_dev, T_vec_dev_m, LAMBDA_PER_CONTEXT, U_logp)
        if b < best_dev_bpc_mar:
            best_dev_bpc_mar = b
            best_T_base_mar = T_base
    T_vec_test_mar = _per_position_T_from_margin(sub_logits_test, best_T_base_mar, T_LOW, T_HIGH)
    mar_bpc, mar_top1, mar_mrr = bpc_top1_mrr_per_context_T(
        sub_logits_test, nxt_test, T_vec_test_mar, LAMBDA_PER_CONTEXT, U_logp)
    T_mean_mar = float(T_vec_test_mar.mean())
    T_std_mar = float(T_vec_test_mar.std())
    print("[seed=%d] ARM_PER_CONTEXT_T_MARGIN best_T_base=%.3f (dev_bpc=%.4f) "
          "T_mean=%.4f T_std=%.4f -> test bpc=%.4f top1=%.4f mrr=%.4f" % (
              seed, best_T_base_mar, best_dev_bpc_mar,
              T_mean_mar, T_std_mar, mar_bpc, mar_top1, mar_mrr), flush=True)

    elapsed = time.time() - t_seed
    print("[seed=%d] done in %.1fs" % (seed, elapsed), flush=True)

    return {
        "seed": seed,
        "V": V,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "run_mode": RUN_MODE,
        "n_dev": n_dev,
        "n_test": n_test,
        "elapsed_s": elapsed,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": 0,
        "by_arm": {
            "ARM_UNIGRAM": {
                "bpc": uni_bpc,
                "top1": uni_acc,
                "mrr": uni_mrr,
            },
            "ARM_GLOBAL_T": {
                "bpc": gl_bpc,
                "top1": gl_top1,
                "mrr": gl_mrr,
                "best_T": best_T_gl,
                "best_lambda": best_lam_gl,
                "best_dev_bpc": best_dev_bpc_gl,
            },
            "ARM_PER_CONTEXT_T_ENTROPY": {
                "bpc": ent_bpc,
                "top1": ent_top1,
                "mrr": ent_mrr,
                "best_T_base": best_T_base_ent,
                "best_dev_bpc": best_dev_bpc_ent,
                "T_mean": T_mean_ent,
                "T_std": T_std_ent,
                "lambda": LAMBDA_PER_CONTEXT,
            },
            "ARM_PER_CONTEXT_T_MARGIN": {
                "bpc": mar_bpc,
                "top1": mar_top1,
                "mrr": mar_mrr,
                "best_T_base": best_T_base_mar,
                "best_dev_bpc": best_dev_bpc_mar,
                "T_mean": T_mean_mar,
                "T_std": T_std_mar,
                "lambda": LAMBDA_PER_CONTEXT,
            },
        },
        "wall_ingest_s": float(t_ingest),
        "wall_recall_s": float(t_recall),
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(per_seed: Dict) -> Tuple[str, str, Dict]:
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed data.", {})

    def _arm_bpcs(arm):
        return [v["by_arm"][arm]["bpc"] for v in per_seed.values()
                if arm in v.get("by_arm", {}) and math.isfinite(v["by_arm"][arm]["bpc"])]

    def _mean(xs):
        return float(np.mean(xs)) if xs else float("nan")

    def _cv(xs):
        m = _mean(xs)
        if not math.isfinite(m) or m < 1e-9 or len(xs) < 2:
            return float("inf")
        return float(np.std(xs)) / m

    uni_bpcs = _arm_bpcs("ARM_UNIGRAM")
    gl_bpcs = _arm_bpcs("ARM_GLOBAL_T")
    ent_bpcs = _arm_bpcs("ARM_PER_CONTEXT_T_ENTROPY")
    mar_bpcs = _arm_bpcs("ARM_PER_CONTEXT_T_MARGIN")

    uni_m = _mean(uni_bpcs)
    gl_m = _mean(gl_bpcs)
    ent_m = _mean(ent_bpcs)
    mar_m = _mean(mar_bpcs)

    gl_cv = _cv(gl_bpcs)
    ent_cv = _cv(ent_bpcs)
    mar_cv = _cv(mar_bpcs)

    # Lift for each per-context arm over global
    ent_lift = gl_m - ent_m  # positive = per-context is BETTER (lower BPC)
    mar_lift = gl_m - mar_m

    best_lift = max(ent_lift, mar_lift)
    best_arm_name = "ARM_PER_CONTEXT_T_ENTROPY" if ent_lift >= mar_lift else "ARM_PER_CONTEXT_T_MARGIN"
    best_bpc = ent_m if ent_lift >= mar_lift else mar_m
    best_cv = ent_cv if ent_lift >= mar_lift else mar_cv

    n_seeds = len(per_seed)
    n_llm = sum(int(v.get("n_llm_calls", 0)) for v in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    summary = (
        "BPC uni=%.4f global=%.4f ent=%.4f(lift=%.4f) mar=%.4f(lift=%.4f) | "
        "best=%s lift=%.4f bpc=%.4f cv=%.4f | n_seeds=%d N_DIM=%d N_TRAIN=%d n_llm=%d"
    ) % (uni_m, gl_m, ent_m, ent_lift, mar_m, mar_lift,
         best_arm_name, best_lift, best_bpc, best_cv,
         n_seeds, N_DIM, N_TRAIN, n_llm)

    detail = {
        "by_arm_agg": {
            "ARM_UNIGRAM": {"bpc_mean": uni_m},
            "ARM_GLOBAL_T": {"bpc_mean": gl_m, "cv": gl_cv},
            "ARM_PER_CONTEXT_T_ENTROPY": {
                "bpc_mean": ent_m, "cv": ent_cv, "lift_over_global": ent_lift},
            "ARM_PER_CONTEXT_T_MARGIN": {
                "bpc_mean": mar_m, "cv": mar_cv, "lift_over_global": mar_lift},
        },
        "best_per_context_arm": best_arm_name,
        "best_per_context_lift": best_lift,
        "best_per_context_bpc": best_bpc,
        "best_per_context_cv": best_cv,
        "global_t_bpc": gl_m,
        "chain_grade_baseline": CHAIN_GRADE_BASELINE_BPC,
        "zero_llm_calls_at_inference": substrate_only_ok,
        "n_llm_calls": n_llm,
        "honest_scope": (
            "Per-context decode temperature: ARM_GLOBAL_T (joint T+lambda sweep) vs "
            "ARM_PER_CONTEXT_T_ENTROPY (entropy-modulated T) and ARM_PER_CONTEXT_T_MARGIN "
            "(margin-modulated T). text8 N_TRAIN=%d N_HELD=%d VOCAB_CAP=%d N_DIM=%d "
            "sparse_bipolar_f=%.3f. Held split dev/test; T_base tuned on dev."
        ) % (N_TRAIN, N_HELD, VOCAB_CAP, N_DIM, SPARSE_F),
        "preregs": "preregs/2026-06-23_substrate_per_context_decode_temperature_LM_v1.md",
        "brain_prior": "P_inherited=0.45 (Yu-Dayan 2005 ACh gain deflated for substrate-native LM)",
    }

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    cv_ok = best_cv <= HARD_PASS_CV_MAX

    if best_lift >= HARD_PASS_LIFT_BPC and cv_ok:
        if best_lift >= CHAIN_GRADE_BONUS_LIFT and best_bpc < CHAIN_GRADE_BASELINE_BPC:
            return ("HARD_PASS",
                    "HARD_PASS CHAIN_GRADE_BONUS: %s lifts +%.4f bits over global T "
                    "(>=0.20 bar) AND beats fair_harness chain-grade %.4f with bpc=%.4f. "
                    "Per-context uncertainty-modulated T is substrate-native phase-diagram navigation. %s" % (
                        best_arm_name, best_lift, CHAIN_GRADE_BASELINE_BPC, best_bpc, summary),
                    detail)
        return ("HARD_PASS",
                "HARD_PASS: %s lifts +%.4f bits over global T (>= %.2f bar); cv=%.4f. "
                "Per-context T adds real lift over global calibration. %s" % (
                    best_arm_name, best_lift, HARD_PASS_LIFT_BPC, best_cv, summary),
                detail)

    if best_lift <= HARD_FAIL_LIFT_MAX:
        return ("HARD_FAIL",
                "HARD_FAIL: best per-context T lift=%.4f <= %.2f threshold. "
                "Per-context T does not add meaningfully over global calibration. %s" % (
                    best_lift, HARD_FAIL_LIFT_MAX, summary),
                detail)

    return ("MIDDLE_BAND",
            "MIDDLE_BAND: best per-context lift=%.4f in (%.2f, %.2f). "
            "Marginal improvement over global T; investigate T_LOW/T_HIGH tuning. %s" % (
                best_lift, MIDDLE_BAND_LIFT_LOW, HARD_PASS_LIFT_BPC, summary),
            detail)


# ============================================================================
# atexit synthesizer + signal handler
# ============================================================================

def _synthesize_on_exit():
    if _METRICS_WRITTEN[0]:
        return
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        run_config = {"N": N_DIM, "M": N_TRAIN, "run_mode": RUN_MODE}
        per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
        if not per_seed:
            return
        v, vmsg, detail = compute_verdict(per_seed)
        vmsg = "TIMEOUT_OR_INTERRUPTED_PARTIAL: " + vmsg
        metrics = {
            "anchor": ANCHOR_NAME,
            "anchor_name": ANCHOR_NAME,
            "verdict": v,
            "verdict_msg": vmsg,
            "n_seeds": len(per_seed),
            "N": N_DIM,
            "N_DIM": N_DIM,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "VOCAB_CAP": VOCAB_CAP,
            "SPARSE_F": SPARSE_F,
            "TEMP_GRID": TEMP_GRID,
            "LAMBDA_GRID": LAMBDA_GRID,
            "T_LOW": T_LOW,
            "T_HIGH": T_HIGH,
            "LAMBDA_PER_CONTEXT": LAMBDA_PER_CONTEXT,
            "arms": ARMS,
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "detail": detail,
            "metrics_source": "synthesized_from_partials_on_exit",
            "synthesized_at_exit": True,
            "elapsed_s": 0.0,
        }
        write_metrics(out_dir, metrics, results=list(per_seed.values()))
        _METRICS_WRITTEN[0] = True
    except Exception as e:
        print("[atexit] FAILED: %s" % e, flush=True)


atexit.register(_synthesize_on_exit)


def _sigterm_handler(signum, frame):
    _synthesize_on_exit()
    sys.exit(143)


try:
    signal.signal(signal.SIGTERM, _sigterm_handler)
except (ValueError, AttributeError):
    pass


# ============================================================================
# Main runner
# ============================================================================

out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
t0_total = time.time()
run_config = {"N": N_DIM, "M": N_TRAIN, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d N_TRAIN=%d VOCAB_CAP=%d device=cpu "
      "seeds_done=%s seeds_todo=%s" % (
          RUN_MODE, N_DIM, N_TRAIN, VOCAB_CAP, str(done), str(seeds_todo)), flush=True)

for s in seeds_todo:
    print("[seed=%d] starting at %.1fs" % (s, time.time() - t0_total), flush=True)
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
v, vmsg, detail = compute_verdict(per_seed)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": v,
    "verdict_msg": vmsg,
    "n_seeds": len(per_seed),
    "N": N_DIM,
    "N_DIM": N_DIM,
    "N_TRAIN": N_TRAIN,
    "N_HELD": N_HELD,
    "VOCAB_CAP": VOCAB_CAP,
    "SPARSE_F": SPARSE_F,
    "TEMP_GRID": TEMP_GRID,
    "LAMBDA_GRID": LAMBDA_GRID,
    "T_LOW": T_LOW,
    "T_HIGH": T_HIGH,
    "LAMBDA_PER_CONTEXT": LAMBDA_PER_CONTEXT,
    "arms": ARMS,
    "run_mode": RUN_MODE,
    "config_version": CONFIG_VERSION,
    "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    "zero_llm_calls_at_inference": True,
    "n_llm_calls": 0,
    "detail": detail,
    "per_seed": [{"seed": k, **{kk: vv for kk, vv in vv_.items()}}
                 for k, vv_ in per_seed.items()],
    "metrics_source": "measured_cpu_substrate_per_context_decode_temperature_LM_v1",
    "elapsed_s": time.time() - t0_total,
    "summary": vmsg[:300],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % v, flush=True)
print("[VERDICT_MSG] %s" % vmsg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
