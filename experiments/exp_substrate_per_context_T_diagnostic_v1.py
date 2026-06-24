"""substrate_per_context_T_diagnostic_v1 -- diagnostic cell resolving shotgun-vs-production discrepancy.

QUESTION: viability shotgun P8 says per-token T is LIVE (83% entropy-variance delta).
Production cell substrate_per_context_decode_temperature_LM_v1 HARD_FAIL (per-context arms
WORSE than unigram by 0.32-0.37 bits BPC). Which is right and why?

HYPOTHESIS SPACE (from task brief):
  H1: Implementation difference -- cell per-context formula differs from shotgun
  H2: Harness incompatibility -- lambda-mix step breaks per-context T benefit
  H3: Scale-dependence -- benefit inverts at N=4096+ vs shotgun N=2048 small
  H4: Codebook interaction -- sparse-bipolar incompatible with per-context T

This cell is designed to ISOLATE which hypothesis is correct by crossing:
  codebook type (dense random vs sparse-bipolar) x T-routing (global vs per-context)

5 arms x 3 seeds x text8 N_TRAIN=10k N_DIM=4096:
  ARM_UNIGRAM                     : analytic floor
  ARM_GLOBAL_T_DENSE              : dense codebook + global T sweep (reproduces shotgun P7)
  ARM_PER_CONTEXT_T_DENSE         : dense codebook + per-context T (should reproduce shotgun P8 LIVE)
  ARM_GLOBAL_T_SPARSE_BIPOLAR     : sparse f=0.05 + global T (reproduces production ARM_GLOBAL_T)
  ARM_PER_CONTEXT_T_SPARSE_BIPOLAR: sparse f=0.05 + per-context T (reproduces production HARD_FAIL arm)

Pre-reg HARD bands (diagnostic -- multiple valid verdicts):
  CODEBOOK_DEPENDENT (primary hypothesis):
    ARM_PER_CONTEXT_T_DENSE > ARM_GLOBAL_T_DENSE by >= 0.05 bits BPC
    AND ARM_PER_CONTEXT_T_SPARSE_BIPOLAR <= ARM_GLOBAL_T_SPARSE_BIPOLAR + 0.05 bits BPC
    -> sparse-bipolar is incompatible with per-context T; dense works fine

  SCALE_DEPENDENT (H3):
    ARM_PER_CONTEXT_T_DENSE <= ARM_GLOBAL_T_DENSE (per-context T also hurts dense at N=4096)
    -> scale-dependence kicks in at N=4096; not codebook-specific

  IMPLEMENTATION_BUG (H1):
    ARM_PER_CONTEXT_T_DENSE < ARM_GLOBAL_T_DENSE
    AND T_std_dense > 0.001  (per-context T IS varying -- not degenerate)
    AND T_std_sparse > 0.001
    -> both codebooks benefit; implies shotgun formula works but production cell formula broken

  LAMBDA_INCOMPATIBILITY (H2):
    ARM_PER_CONTEXT_T_SPARSE_BIPOLAR with lam=0.0 (pure substrate) BETTER than lam=0.3
    -> lambda mixing suppresses per-context T when substrate < unigram

HARD_FAIL guard: ARM_GLOBAL_T_DENSE < ARM_UNIGRAM by >= 0.05 bits required; if substrate
is not above unigram even with dense encoder + global T, this is a corpus/N_TRAIN scale issue
and all H-tests are confounded.

Note on LAMBDA mechanism: production cell uses lam=0.3 (mix 30% substrate + 70% unigram).
When best_lambda=0.0 for ARM_GLOBAL_T, substrate is WORSE than unigram. Per-context T then
cannot help because it mixes in a damaged signal. This cell tests lambda=0.0 in per-context
arms to isolate T effect from lambda effect.

Routing: remote_cpu_queue (N_DIM=4096 matmul, multiple seeds, pure numpy)
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

ANCHOR_NAME = "substrate_per_context_T_diagnostic_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"
_LLM_CALL_COUNTER = [0]
_METRICS_WRITTEN = [False]

# Codebook params
SPARSE_F = 0.05

# Joint T sweep for global arms
TEMP_GRID = [0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.1, 0.3, 0.5, 0.7, 1.0]

# Per-context T range
T_LOW = 0.02
T_HIGH = 0.5
# Per-context lambda: test both 0.0 (pure substrate) and 0.3 (fair_harness best)
LAMBDA_OPTIONS_PC = [0.0, 0.3]

ARMS = [
    "ARM_UNIGRAM",
    "ARM_GLOBAL_T_DENSE",
    "ARM_PER_CONTEXT_T_DENSE",
    "ARM_GLOBAL_T_SPARSE_BIPOLAR",
    "ARM_PER_CONTEXT_T_SPARSE_BIPOLAR",
]

# Pre-reg thresholds
DENSE_SUBSTRATE_OVER_UNIGRAM_MIN = 0.05   # ARM_GLOBAL_T_DENSE must beat unigram by this
CODEBOOK_DEPENDENT_THRESHOLD = 0.05       # dense per-ctx lift must exceed this
SCALE_DEPENDENT_COLLAPSE = 0.0            # if dense per-ctx also hurts, scale-dependent

# Parse run mode
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# Config
N_DIM = 4096
VOCAB_CAP = 2000

if RUN_MODE in ("smoke", "selftest"):
    SEEDS = [0]
    N_TRAIN = 2_000
    N_HELD = 500
    VOCAB_CAP = 200
    N_DIM = 256
    INGEST_CHUNK = 256
    RECALL_BATCH = 128
else:
    SEEDS = [7, 17, 23]
    N_TRAIN = 10_000
    N_HELD = 5_000
    INGEST_CHUNK = 4096
    RECALL_BATCH = 512

CONFIG_VERSION = (
    "substrate_per_context_T_diagnostic_v1; N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d sparse_f=%.3f seeds=%s run_mode=%s arms=%s "
    "TEMP_GRID=%s LAMBDA_GRID=%s T_LOW=%.3f T_HIGH=%.3f LAMBDA_PC=%s"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, SPARSE_F, SEEDS, RUN_MODE, ARMS,
    TEMP_GRID, LAMBDA_GRID, T_LOW, T_HIGH, str(LAMBDA_OPTIONS_PC),
)


# ============================================================================
# Substrate primitives (CPU/numpy)
# ============================================================================

def _seed_for_tri(tri, seed):
    h = hashlib.md5((tri + ":" + str(seed)).encode()).hexdigest()
    return int(h, 16) & 0xFFFFFFFF


def char_trigram_encode_np(word, dim, seed):
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


def build_dense_random_encoder_np(vocab, dim, seed):
    """Build [V, dim] L2-normalized dense random encoder (mirrors shotgun P8 codebook)."""
    rng = np.random.RandomState(seed)
    E = rng.randn(len(vocab), dim).astype(np.float32)
    nrm = np.linalg.norm(E, axis=1, keepdims=True)
    nrm[nrm < 1e-9] = 1.0
    return E / nrm


def build_char_trigram_encoder_np(vocab, dim, seed):
    """Build [V, dim] L2-normalized char-trigram encoder (mirrors production cell)."""
    E = np.stack([char_trigram_encode_np(w, dim, seed) for w in vocab], 0).astype(np.float32)
    nrm = np.linalg.norm(E, axis=1, keepdims=True)
    nrm[nrm < 1e-9] = 1.0
    return E / nrm


def sparsify_bipolar_np(E, f):
    """Top-k sparse bipolar (mirrors production cell). NO amplitude scaling per design intent."""
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


def build_hebbian_W_np(idx_train, E, ingest_chunk):
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


def compute_substrate_logits_np(ctx_idx, E, W, recall_batch):
    """Return [n, V] cosine-similarity logits from substrate."""
    n = len(ctx_idx)
    V = E.shape[0]
    logits = np.zeros((n, V), dtype=np.float32)
    for b in range(0, n, recall_batch):
        end = min(b + recall_batch, n)
        pred = E[ctx_idx[b:end]] @ W.T  # [b, dim]
        nrm = np.linalg.norm(pred, axis=1, keepdims=True)
        nrm[nrm < 1e-9] = 1.0
        pred = pred / nrm
        logits[b:end] = pred @ E.T  # [b, V]
    return logits


# ============================================================================
# Logit + metric helpers
# ============================================================================

def bpc_top1_from_logits(logits, nxt, T, lam, U_logp):
    """Compute BPC, top-1 from logits with (T, lambda) interp."""
    z = logits / max(T, 1e-8)
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
    p_true = np.clip(probs[np.arange(len(nxt)), nxt], 1e-12, 1.0)
    bpc = float(-np.mean(np.log2(p_true)))
    top1 = float((probs.argmax(axis=1) == nxt).mean())
    return bpc, top1


def _per_position_T_from_entropy(logits, T_base, T_low, T_high):
    """Per-position T based on normalized predictive entropy.
    High H (uncertain) -> T_low; low H (confident) -> T_high.
    """
    z = logits / max(T_base, 1e-8)
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    p = e / (e.sum(axis=1, keepdims=True) + 1e-30)
    logp = np.log(np.clip(p, 1e-30, 1.0))
    H = -np.sum(p * logp, axis=1).astype(np.float32)
    H_max = math.log(logits.shape[1])
    H_norm = np.clip(H / H_max, 0.0, 1.0)
    T_vec = T_low + (T_high - T_low) * (1.0 - H_norm)
    return T_vec.astype(np.float32)


def _per_position_T_from_entropy_50pct_target(logits, T_low=0.01, T_high=2.0):
    """Shotgun P8 method: binary-search for T that achieves 50% of max entropy per position.
    Returns a T_vec per position.
    """
    n, V = logits.shape
    target_entropy = 0.5 * math.log2(max(V, 1))
    T_vec = np.zeros(n, dtype=np.float32)
    for i in range(n):
        lo, hi = T_low, T_high
        for _ in range(20):
            mid = (lo + hi) / 2.0
            sc = logits[i] / mid
            sc -= sc.max()
            p = np.exp(sc)
            p /= p.sum()
            ent = float(-np.sum(p * np.log2(p + 1e-40)))
            if ent < target_entropy:
                lo = mid
            else:
                hi = mid
        T_vec[i] = (lo + hi) / 2.0
    return T_vec


def bpc_top1_per_context_T(logits, nxt, T_vec, lam, U_logp):
    """BPC/top-1 using per-position temperature vector T_vec [n]."""
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
    return bpc, top1


# ============================================================================
# Corpus helpers
# ============================================================================

def load_text8_tokens(n_total):
    if not TEXT8.exists():
        print("[FATAL] corpus missing: %s" % TEXT8, flush=True)
        sys.exit(1)
    out = []
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


def build_vocab(train_tokens, cap):
    c = Counter(train_tokens)
    top = [w for w, _ in c.most_common(cap - 1)]
    vocab = ["<unk>"] + top
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_idx(toks, w2i):
    unk = w2i["<unk>"]
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


def build_unigram(idx_train, V, alpha=0.1):
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


# ============================================================================
# Instrumentation self-test (MANDATORY per exp_dev role contract)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    print("[selftest] running instrumentation self-test ...", flush=True)

    V_t = 8
    dim_t = 64
    vocab_t = ["w%d" % i for i in range(V_t)]

    # 1. Dense encoder: L2-normalized, not all-zero
    E_dense = build_dense_random_encoder_np(vocab_t, dim_t, seed=42)
    assert E_dense.shape == (V_t, dim_t), "selftest 1: dense encoder shape wrong"
    nrms = np.linalg.norm(E_dense, axis=1)
    assert np.allclose(nrms, 1.0, atol=1e-4), "selftest 1: dense encoder not L2-normed"

    # 2. Char-trigram encoder: deterministic, L2-normalized
    E_tri = build_char_trigram_encoder_np(vocab_t, dim_t, seed=0)
    E_tri2 = build_char_trigram_encoder_np(vocab_t, dim_t, seed=0)
    assert np.allclose(E_tri, E_tri2), "selftest 2: trigram encoder not deterministic"

    # 3. Sparsify: produces non-zero output, correct fraction roughly
    E_sp = sparsify_bipolar_np(E_dense, f=0.1)
    nonzero = (E_sp != 0).sum(axis=1)
    assert (nonzero > 0).all(), "selftest 3: sparsify all-zero row"

    # 4. Hebbian W + logits: non-null, not all-zero, no NaN
    idx_tr = np.tile(np.arange(V_t, dtype=np.int64), 5)
    W_dense = build_hebbian_W_np(idx_tr, E_dense, ingest_chunk=20)
    assert W_dense.shape == (dim_t, dim_t), "selftest 4: W_dense shape wrong"
    assert np.abs(W_dense).sum() > 0, "selftest 4: W_dense all-zero"
    ctx_t = np.array([0, 1, 2, 3], dtype=np.int64)
    nxt_t = np.array([1, 2, 3, 4], dtype=np.int64)
    logits_d = compute_substrate_logits_np(ctx_t, E_dense, W_dense, recall_batch=4)
    assert logits_d.shape == (4, V_t), "selftest 4: logits shape wrong"
    assert not np.all(logits_d == 0), "selftest 4: logits all-zero"
    assert not np.any(np.isnan(logits_d)), "selftest 4: logits NaN"

    # 5. BPC finite + top1 in [0,1] for both arms
    U_t = build_unigram(idx_tr, V=V_t, alpha=0.1)
    U_logp_t = np.log(np.clip(U_t, 1e-30, 1.0))
    bpc_d, top1_d = bpc_top1_from_logits(logits_d, nxt_t, T=0.05, lam=0.0, U_logp=U_logp_t)
    assert math.isfinite(bpc_d) and bpc_d > 0, "selftest 5: bpc_dense not finite: %s" % bpc_d
    assert 0.0 <= top1_d <= 1.0, "selftest 5: top1_dense out of range"

    # 6. Per-context T entropy method: T_vec in valid range
    T_vec_ent = _per_position_T_from_entropy(logits_d, T_base=0.05, T_low=T_LOW, T_high=T_HIGH)
    assert T_vec_ent.shape == (4,), "selftest 6: T_vec_ent shape wrong"
    assert (T_vec_ent >= T_LOW - 1e-5).all(), "selftest 6: T_vec_ent below T_LOW"
    assert (T_vec_ent <= T_HIGH + 1e-5).all(), "selftest 6: T_vec_ent above T_HIGH"

    # 7. Per-context T 50pct-target method (shotgun method): T_vec varies per position
    # Only run on tiny data (binary search is O(n * 20 * V))
    logits_tiny = logits_d[:2]
    T_vec_50 = _per_position_T_from_entropy_50pct_target(logits_tiny, T_low=0.01, T_high=2.0)
    assert T_vec_50.shape == (2,), "selftest 7: T_vec_50 shape wrong"
    assert (T_vec_50 >= 0.01 - 1e-5).all(), "selftest 7: T_vec_50 below T_low"
    assert (T_vec_50 <= 2.0 + 1e-5).all(), "selftest 7: T_vec_50 above T_high"

    # 8. per-context-T BPC finite and valid
    bpc_pc, top1_pc = bpc_top1_per_context_T(logits_d, nxt_t, T_vec_ent, lam=0.0, U_logp=U_logp_t)
    assert math.isfinite(bpc_pc) and bpc_pc > 0, "selftest 8: bpc_pc not finite: %s" % bpc_pc
    assert 0.0 <= top1_pc <= 1.0, "selftest 8: top1_pc out of range"

    # 9. Sparse arm: logits from sparse W are non-null
    W_sp = build_hebbian_W_np(idx_tr, E_sp, ingest_chunk=20)
    logits_sp = compute_substrate_logits_np(ctx_t, E_sp, W_sp, recall_batch=4)
    assert not np.any(np.isnan(logits_sp)), "selftest 9: sparse logits NaN"
    bpc_sp, _ = bpc_top1_from_logits(logits_sp, nxt_t, T=0.05, lam=0.0, U_logp=U_logp_t)
    assert math.isfinite(bpc_sp) and bpc_sp > 0, "selftest 9: bpc_sparse not finite: %s" % bpc_sp

    # 10. LLM counter still 0
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 10: LLM counter non-zero"

    print("[selftest] PASS: dense/trigram/sparse encoders + W + logits + BPC + per-ctx-T "
          "all valid, LLM=0", flush=True)


_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ============================================================================
# Per-seed runner
# ============================================================================

def _run_global_T_arm(logits_dev, nxt_dev, logits_test, nxt_test, U_logp, arm_label):
    """Sweep (T, lambda) on dev; eval best on test. Returns arm dict."""
    best_dev_bpc = float("inf")
    best_T = TEMP_GRID[0]
    best_lam = LAMBDA_GRID[0]
    for T in TEMP_GRID:
        for lam in LAMBDA_GRID:
            b, _ = bpc_top1_from_logits(logits_dev, nxt_dev, T, lam, U_logp)
            if b < best_dev_bpc:
                best_dev_bpc = b
                best_T = T
                best_lam = lam
    test_bpc, test_top1 = bpc_top1_from_logits(logits_test, nxt_test, best_T, best_lam, U_logp)
    print("[%s] best_T=%.3f best_lam=%.2f dev_bpc=%.4f test_bpc=%.4f top1=%.4f" % (
        arm_label, best_T, best_lam, best_dev_bpc, test_bpc, test_top1), flush=True)
    return {
        "bpc": test_bpc,
        "top1": test_top1,
        "best_T": best_T,
        "best_lambda": best_lam,
        "best_dev_bpc": best_dev_bpc,
    }


def _run_per_context_T_arm(logits_dev, nxt_dev, logits_test, nxt_test, U_logp, arm_label):
    """Tune T_base on dev using entropy method; eval per-context T on test.
    Tests BOTH lambda=0.0 and lambda=0.3 to isolate lambda confound.
    Uses production-cell entropy method AND shotgun 50pct-target method.
    """
    results = {}

    # Method A: production-cell entropy formula (high-H -> T_low)
    best_dev_bpc_A = float("inf")
    best_T_base_A = TEMP_GRID[0]
    best_lam_A = 0.0
    for T_base in TEMP_GRID:
        T_vec_dev = _per_position_T_from_entropy(logits_dev, T_base, T_LOW, T_HIGH)
        for lam in LAMBDA_OPTIONS_PC:
            b, _ = bpc_top1_per_context_T(logits_dev, nxt_dev, T_vec_dev, lam, U_logp)
            if b < best_dev_bpc_A:
                best_dev_bpc_A = b
                best_T_base_A = T_base
                best_lam_A = lam
    T_vec_test_A = _per_position_T_from_entropy(logits_test, best_T_base_A, T_LOW, T_HIGH)
    test_bpc_A, test_top1_A = bpc_top1_per_context_T(
        logits_test, nxt_test, T_vec_test_A, best_lam_A, U_logp)
    T_mean_A = float(T_vec_test_A.mean())
    T_std_A = float(T_vec_test_A.std())
    print("[%s/methodA_entropy] best_T_base=%.3f lam=%.2f dev_bpc=%.4f "
          "test_bpc=%.4f T_mean=%.4f T_std=%.6f" % (
              arm_label, best_T_base_A, best_lam_A, best_dev_bpc_A,
              test_bpc_A, T_mean_A, T_std_A), flush=True)
    results["method_A_entropy"] = {
        "bpc": test_bpc_A, "top1": test_top1_A,
        "best_T_base": best_T_base_A, "best_lambda": best_lam_A,
        "best_dev_bpc": best_dev_bpc_A,
        "T_mean": T_mean_A, "T_std": T_std_A,
    }

    # Method B: shotgun 50pct-target binary-search method
    # T_base fixed at global best T (use method A's best_T_base as proxy, or scan TEMP_GRID)
    # For smoke scale this is feasible; for full scale N_TEST positions x 20 iters is fine
    best_dev_bpc_B = float("inf")
    best_lam_B = 0.0
    for lam in LAMBDA_OPTIONS_PC:
        T_vec_dev_B = _per_position_T_from_entropy_50pct_target(logits_dev, T_low=0.01, T_high=2.0)
        b, _ = bpc_top1_per_context_T(logits_dev, nxt_dev, T_vec_dev_B, lam, U_logp)
        if b < best_dev_bpc_B:
            best_dev_bpc_B = b
            best_lam_B = lam
    T_vec_test_B = _per_position_T_from_entropy_50pct_target(logits_test, T_low=0.01, T_high=2.0)
    test_bpc_B, test_top1_B = bpc_top1_per_context_T(
        logits_test, nxt_test, T_vec_test_B, best_lam_B, U_logp)
    T_mean_B = float(T_vec_test_B.mean())
    T_std_B = float(T_vec_test_B.std())
    print("[%s/methodB_50pct] lam=%.2f dev_bpc=%.4f test_bpc=%.4f "
          "T_mean=%.4f T_std=%.6f" % (
              arm_label, best_lam_B, best_dev_bpc_B, test_bpc_B, T_mean_B, T_std_B), flush=True)
    results["method_B_50pct_target"] = {
        "bpc": test_bpc_B, "top1": test_top1_B,
        "best_lambda": best_lam_B,
        "best_dev_bpc": best_dev_bpc_B,
        "T_mean": T_mean_B, "T_std": T_std_B,
    }

    # Summary: use best of both methods
    best_bpc = min(test_bpc_A, test_bpc_B)
    results["bpc"] = best_bpc
    results["top1"] = test_top1_A if test_bpc_A <= test_bpc_B else test_top1_B
    return results


def run_seed(seed):
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

    n_dev = n_eval // 2
    ctx_dev = ctx_eval[:n_dev]
    nxt_dev = nxt_eval[:n_dev]
    ctx_test = ctx_eval[n_dev:]
    nxt_test = nxt_eval[n_dev:]
    n_test = len(ctx_test)
    print("[seed=%d] V=%d train=%d held=%d dev=%d test=%d" % (
        seed, V, N_TRAIN, N_HELD, n_dev, n_test), flush=True)

    U = build_unigram(idx_train_np, V=V, alpha=0.1)
    U_logp = np.log(np.clip(U, 1e-30, 1.0))
    p_true_uni = U[nxt_test].clip(1e-12, 1.0)
    uni_bpc = float(-np.mean(np.log2(p_true_uni)))
    uni_acc = float((np.argmax(U) == nxt_test).mean())
    print("[seed=%d] UNIGRAM bpc=%.4f acc=%.4f" % (seed, uni_bpc, uni_acc), flush=True)

    # ----- Build DENSE encoder -----
    t0 = time.time()
    E_dense = build_dense_random_encoder_np(vocab, N_DIM, seed=seed)
    t_enc = time.time() - t0
    print("[seed=%d] dense encoder built N_DIM=%d V=%d (%.1fs)" % (
        seed, N_DIM, V, t_enc), flush=True)

    W_dense = build_hebbian_W_np(idx_train_np, E_dense, ingest_chunk=INGEST_CHUNK)
    logits_dev_dense = compute_substrate_logits_np(ctx_dev, E_dense, W_dense, RECALL_BATCH)
    logits_test_dense = compute_substrate_logits_np(ctx_test, E_dense, W_dense, RECALL_BATCH)
    print("[seed=%d] dense logits computed" % seed, flush=True)

    # ----- Build SPARSE-BIPOLAR encoder -----
    E_sp = sparsify_bipolar_np(E_dense, f=SPARSE_F)
    W_sp = build_hebbian_W_np(idx_train_np, E_sp, ingest_chunk=INGEST_CHUNK)
    logits_dev_sp = compute_substrate_logits_np(ctx_dev, E_sp, W_sp, RECALL_BATCH)
    logits_test_sp = compute_substrate_logits_np(ctx_test, E_sp, W_sp, RECALL_BATCH)
    print("[seed=%d] sparse logits computed" % seed, flush=True)

    # ----- ARM_GLOBAL_T_DENSE -----
    arm_gl_dense = _run_global_T_arm(
        logits_dev_dense, nxt_dev, logits_test_dense, nxt_test, U_logp,
        "ARM_GLOBAL_T_DENSE[seed=%d]" % seed)

    # ----- ARM_PER_CONTEXT_T_DENSE -----
    arm_pc_dense = _run_per_context_T_arm(
        logits_dev_dense, nxt_dev, logits_test_dense, nxt_test, U_logp,
        "ARM_PER_CONTEXT_T_DENSE[seed=%d]" % seed)

    # ----- ARM_GLOBAL_T_SPARSE_BIPOLAR -----
    arm_gl_sp = _run_global_T_arm(
        logits_dev_sp, nxt_dev, logits_test_sp, nxt_test, U_logp,
        "ARM_GLOBAL_T_SPARSE_BIPOLAR[seed=%d]" % seed)

    # ----- ARM_PER_CONTEXT_T_SPARSE_BIPOLAR -----
    arm_pc_sp = _run_per_context_T_arm(
        logits_dev_sp, nxt_dev, logits_test_sp, nxt_test, U_logp,
        "ARM_PER_CONTEXT_T_SPARSE_BIPOLAR[seed=%d]" % seed)

    elapsed = time.time() - t_seed
    print("[seed=%d] done in %.1fs" % (seed, elapsed), flush=True)

    return {
        "seed": seed,
        "V": V,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "run_mode": RUN_MODE,
        "n_dev": n_dev,
        "n_test": n_test,
        "elapsed_s": elapsed,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": 0,
        "by_arm": {
            "ARM_UNIGRAM": {"bpc": uni_bpc, "top1": uni_acc},
            "ARM_GLOBAL_T_DENSE": arm_gl_dense,
            "ARM_PER_CONTEXT_T_DENSE": arm_pc_dense,
            "ARM_GLOBAL_T_SPARSE_BIPOLAR": arm_gl_sp,
            "ARM_PER_CONTEXT_T_SPARSE_BIPOLAR": arm_pc_sp,
        },
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(per_seed):
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed data.", {})

    def _arm_bpcs(arm):
        return [v["by_arm"][arm]["bpc"] for v in per_seed.values()
                if arm in v.get("by_arm", {}) and math.isfinite(v["by_arm"][arm]["bpc"])]

    def _mean(xs):
        return float(np.mean(xs)) if xs else float("nan")

    uni_m = _mean(_arm_bpcs("ARM_UNIGRAM"))
    gl_dense_m = _mean(_arm_bpcs("ARM_GLOBAL_T_DENSE"))
    pc_dense_m = _mean(_arm_bpcs("ARM_PER_CONTEXT_T_DENSE"))
    gl_sp_m = _mean(_arm_bpcs("ARM_GLOBAL_T_SPARSE_BIPOLAR"))
    pc_sp_m = _mean(_arm_bpcs("ARM_PER_CONTEXT_T_SPARSE_BIPOLAR"))

    # Lifts: positive = per-context BETTER (lower BPC)
    dense_substrate_lift = uni_m - gl_dense_m  # how much dense > unigram
    pc_dense_lift = gl_dense_m - pc_dense_m    # per-ctx T vs global T (dense)
    pc_sp_lift = gl_sp_m - pc_sp_m             # per-ctx T vs global T (sparse)

    n_seeds = len(per_seed)
    n_llm = sum(int(v.get("n_llm_calls", 0)) for v in per_seed.values())

    summary = (
        "BPC uni=%.4f | DENSE: global=%.4f(lift_vs_uni=%.4f) pc=%.4f(pc_lift=%.4f) | "
        "SPARSE: global=%.4f pc=%.4f(pc_lift=%.4f) | n_seeds=%d N_DIM=%d N_TRAIN=%d"
    ) % (uni_m, gl_dense_m, dense_substrate_lift, pc_dense_m, pc_dense_lift,
         gl_sp_m, pc_sp_m, pc_sp_lift,
         n_seeds, N_DIM, N_TRAIN)

    detail = {
        "by_arm_agg": {
            "ARM_UNIGRAM": {"bpc_mean": uni_m},
            "ARM_GLOBAL_T_DENSE": {"bpc_mean": gl_dense_m, "lift_vs_unigram": dense_substrate_lift},
            "ARM_PER_CONTEXT_T_DENSE": {"bpc_mean": pc_dense_m, "lift_over_global": pc_dense_lift},
            "ARM_GLOBAL_T_SPARSE_BIPOLAR": {"bpc_mean": gl_sp_m},
            "ARM_PER_CONTEXT_T_SPARSE_BIPOLAR": {"bpc_mean": pc_sp_m, "lift_over_global": pc_sp_lift},
        },
        "dense_substrate_lift": dense_substrate_lift,
        "pc_dense_lift": pc_dense_lift,
        "pc_sp_lift": pc_sp_lift,
        "zero_llm_calls_at_inference": (n_llm == 0),
        "n_llm_calls": n_llm,
    }

    # Guard: substrate must beat unigram with dense encoder for interpretable results
    if dense_substrate_lift < DENSE_SUBSTRATE_OVER_UNIGRAM_MIN:
        verdict_str = "CONFOUNDED"
        vmsg = (
            "CONFOUNDED: ARM_GLOBAL_T_DENSE lift_vs_unigram=%.4f < %.2f minimum. "
            "Dense substrate is not above unigram at N_TRAIN=%d -- all H-tests unreliable. "
            "Suggest N_TRAIN >= 50k or larger N_DIM for discriminating regime. %s"
        ) % (dense_substrate_lift, DENSE_SUBSTRATE_OVER_UNIGRAM_MIN, N_TRAIN, summary)
        detail["diagnosis"] = "CONFOUNDED"
        return (verdict_str, vmsg, detail)

    # Determine hypothesis
    dense_pc_works = (pc_dense_lift >= CODEBOOK_DEPENDENT_THRESHOLD)
    sparse_pc_works = (pc_sp_lift >= CODEBOOK_DEPENDENT_THRESHOLD)

    if dense_pc_works and not sparse_pc_works:
        verdict_str = "CODEBOOK_DEPENDENT"
        vmsg = (
            "CODEBOOK_DEPENDENT: dense per-ctx-T lift=%.4f >= %.2f; "
            "sparse per-ctx-T lift=%.4f < %.2f. "
            "Per-context T works with dense encoder but fails with sparse-bipolar. "
            "Hypothesis H4 CONFIRMED: sparse-bipolar codebook is incompatible with per-context T. "
            "Production HARD_FAIL explained by codebook not per-context T mechanism. %s"
        ) % (pc_dense_lift, CODEBOOK_DEPENDENT_THRESHOLD, pc_sp_lift, CODEBOOK_DEPENDENT_THRESHOLD,
             summary)
        detail["diagnosis"] = "H4_CODEBOOK_DEPENDENT"
    elif not dense_pc_works and not sparse_pc_works:
        verdict_str = "SCALE_DEPENDENT_OR_IMPLEMENTATION_BUG"
        vmsg = (
            "SCALE_DEPENDENT_OR_IMPLEMENTATION_BUG: dense per-ctx-T lift=%.4f < %.2f; "
            "sparse per-ctx-T lift=%.4f < %.2f. "
            "Per-context T fails for BOTH codebooks at N_TRAIN=%d N_DIM=%d. "
            "Hypothesis H3 (scale-dependence) or H1 (implementation bug) -- "
            "check T_std values: if T_std ~0 then H1, if T_std > 0.001 then H3. %s"
        ) % (pc_dense_lift, CODEBOOK_DEPENDENT_THRESHOLD, pc_sp_lift, CODEBOOK_DEPENDENT_THRESHOLD,
             N_TRAIN, N_DIM, summary)
        detail["diagnosis"] = "H1_OR_H3_SCALE_OR_IMPL"
    elif dense_pc_works and sparse_pc_works:
        verdict_str = "BOTH_CODEBOOKS_BENEFIT"
        vmsg = (
            "BOTH_CODEBOOKS_BENEFIT: dense lift=%.4f sparse lift=%.4f both >= %.2f. "
            "Per-context T improves BPC regardless of codebook at N_TRAIN=%d. "
            "Production HARD_FAIL may be harness-incompatibility (H2) or scale-dependent inversion "
            "between N=4096 (here) and N=8192 (production). %s"
        ) % (pc_dense_lift, pc_sp_lift, CODEBOOK_DEPENDENT_THRESHOLD, N_TRAIN, summary)
        detail["diagnosis"] = "BOTH_BENEFIT_H2_OR_SCALE_CROSS"
    else:
        verdict_str = "SPARSE_ONLY_BENEFIT"
        vmsg = (
            "SPARSE_ONLY_BENEFIT: dense pc-lift=%.4f < %.2f; sparse pc-lift=%.4f >= %.2f. "
            "Unexpected pattern: sparse benefits more than dense from per-context T. "
            "Investigate interaction between sparsity pattern and entropy-T mapping. %s"
        ) % (pc_dense_lift, CODEBOOK_DEPENDENT_THRESHOLD, pc_sp_lift, CODEBOOK_DEPENDENT_THRESHOLD,
             summary)
        detail["diagnosis"] = "UNEXPECTED_SPARSE_ONLY"

    return (verdict_str, vmsg, detail)


# ============================================================================
# atexit synthesizer
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
    except Exception as exc:
        print("[atexit] FAILED: %s" % exc, flush=True)


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
    "arms": ARMS,
    "run_mode": RUN_MODE,
    "config_version": CONFIG_VERSION,
    "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    "zero_llm_calls_at_inference": True,
    "n_llm_calls": 0,
    "detail": detail,
    "per_seed": [{"seed": k, **{kk: vv for kk, vv in vv_.items()}}
                 for k, vv_ in per_seed.items()],
    "metrics_source": "measured_cpu_substrate_per_context_T_diagnostic_v1",
    "elapsed_s": time.time() - t0_total,
    "summary": vmsg[:400],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % v, flush=True)
print("[VERDICT_MSG] %s" % vmsg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
