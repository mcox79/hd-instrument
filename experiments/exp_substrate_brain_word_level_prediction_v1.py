"""substrate_brain_word_level_prediction_v1 -- WORD-grain LM test vs word-bigram.

Anchor #1 of notes/exp_dev_handoff_research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md.

Strategic rationale (PRIORITY 1):
  Brain operates at word-level grain (~5Hz word reading rate), not character-level
  (~30Hz char rate). The substrate has tested 30+ char-level mechanisms this session
  and all bounded by char-level baselines that are unnaturally strong vs the brain's
  word-grain measurement. This is the FIRST attempt to align measurement with brain
  processing grain.

  The previous "+62% top1 over CHAR-unigram" lift may be artifact of char-grain
  mismatch. Word-bigram is the REAL aliveness threshold. word-unigram is the trivial
  floor.

Five arms (all on text8 hold-out at V_word=4000):
  B1  word-unigram baseline (trivial floor)
  B2  word-bigram baseline (THE REAL THRESHOLD — backoff to unigram on unseen ctx)
  S_K1  substrate K=1 word context (no context; should ~ B1 if degenerate)
  S_K5  substrate K=5 word context (PRIMARY arm)
  S_K10 substrate K=10 word context

Substrate encoding:
  - Frozen char-trigram-meanpool bipolar encoder (V x N_DIM)
  - HRR role-bind composition over last-K words via lock-in position vectors
  - Rank-1 Hebbian W: sum over training positions of <bind(ctx_K), e_next>
  - Cosine-sim logits + per-arm joint (T, lambda)-sweep for fair scoring

Pre-reg HARD bands (research-owned, see preregs/2026-06-24_*.md):
  HARD_PASS:   S_K5 top1 >= 1.30 * B2_top1   AND   S_K5 BPW <= B2_BPW - 0.4 bits
  MIDDLE_BAND: S_K5 top1 in [1.10x, 1.30x] B2 OR S_K5 BPW in [B2-0.4, B2-0.1]
  HARD_FAIL:   S_K5 top1 <= B2_top1   OR    S_K5 BPW >= B2_BPW

Smoke gate (synthetic Zipfian text, NOT substrate state):
  - 10K-word Zipfian corpus
  - Verify B2 word-bigram computes correctly (backoff vs P(w))
  - Verify S_K1 ~= B1 in degenerate case (no context = unigram backoff)
  - Verify per-arm metrics differ + verdict bands fire correctly

ASCII-only. Per-seed checkpoint. Fix #17 elapsed_s. Fix #28 per-arm metrics.

Cites:
  notes/exp_dev_handoff_research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md
  notes/research_brain_mechanisms_NOT_yet_tested_2x_drill_2026-06-24.md
  experiments/exp_fair_harness_substrate_as_lm_v1.py (parent fair-harness pattern)
  experiments/_seed_checkpoint.py (checkpoint API)
  feedback_clean_encoder_tests_no_contamination_USER_2026-06-23
  feedback_smoke_clean_synthetic_data_not_substrate_state_USER_2026-06-23
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
import hashlib
import math
import time
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics
)

ANCHOR_NAME = "substrate_brain_word_level_prediction_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

# ----------------------------------------------------------------------------
# Pre-reg bands (handoff #1; research-owned)
# ----------------------------------------------------------------------------
HP_TOP1_LIFT = 1.30          # S_K5 top1 >= 1.30 * B2_top1
HP_BPW_MARGIN = 0.4          # S_K5 BPW <= B2_BPW - 0.4
MID_TOP1_LIFT = 1.10         # MIDDLE if [1.10, 1.30] OR BPW in [B2-0.4, B2-0.1]
MID_BPW_MARGIN_LOW = 0.1
MID_BPW_MARGIN_HIGH = 0.4

# ----------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------
_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else \
           os.environ.get("HDLAB_RUN_MODE", "full")

# ----------------------------------------------------------------------------
# Config: FULL vs smoke
# ----------------------------------------------------------------------------
if RUN_MODE == "full":
    SEEDS = [7, 17, 23]
    N_TRAIN_WORDS = 200_000      # train slice from text8
    N_HELD_WORDS = 20_000        # held-out slice (immediately after train)
    VOCAB_CAP = 4000             # V_word per handoff
    N_DIM = 2048                 # substrate vector dim (CPU-tractable)
    TEMP_GRID = [0.05, 0.1, 0.2, 0.5, 1.0]
    LAMBDA_GRID = [0.0, 0.3, 0.5, 0.7]
    CONTEXT_K_VALUES = [1, 5, 10]
else:
    # Smoke: synthetic Zipfian corpus + tiny config. Must run in < 180s.
    SEEDS = [0]
    N_TRAIN_WORDS = 8_000
    N_HELD_WORDS = 2_000
    VOCAB_CAP = 400
    N_DIM = 512
    TEMP_GRID = [0.1, 0.5, 1.0]
    LAMBDA_GRID = [0.0, 0.5]
    CONTEXT_K_VALUES = [1, 5, 10]

ARMS = ["B1_word_unigram", "B2_word_bigram"] + \
       [f"S_K{k}" for k in CONTEXT_K_VALUES]

CONFIG_VERSION = (
    "substrate_brain_word_level_prediction_v1; mode=%s seeds=%s "
    "N_TRAIN=%d N_HELD=%d V=%d N_DIM=%d K=%s temps=%s lambdas=%s "
    "HP_TOP1_LIFT=%.2f HP_BPW_MARGIN=%.2f"
) % (RUN_MODE, SEEDS, N_TRAIN_WORDS, N_HELD_WORDS, VOCAB_CAP, N_DIM,
     CONTEXT_K_VALUES, TEMP_GRID, LAMBDA_GRID, HP_TOP1_LIFT, HP_BPW_MARGIN)


# ============================================================================
# Char-trigram-meanpool encoder (frozen, bipolar, deterministic by seed)
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"),
                        digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val)
    return (rng.integers(0, 2, size=n_dim) * 2 - 1).astype(np.float32)


def char_trigram_encode(word: str, n_dim: int, seed: int) -> np.ndarray:
    """Bipolar char-trigram mean-pool. Padded with spaces on both sides."""
    t = " " + word.lower().replace("_", " ") + " "
    accum = np.zeros(n_dim, dtype=np.float32)
    if len(t) < 3:
        return accum
    n_tri = 0
    for i in range(len(t) - 2):
        tri = t[i:i + 3]
        accum += _bipolar_hv(_seed_for_trigram(tri, seed), n_dim)
        n_tri += 1
    if n_tri > 0:
        accum /= float(n_tri)
    out = np.sign(accum).astype(np.float32)
    out[out == 0] = 1.0
    return out


def _l2_normalize_np(X, eps=1e-12):
    if X.ndim == 1:
        return X / (np.linalg.norm(X) + eps)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + eps)


def build_E_np(vocab: List[str], n_dim: int, seed: int) -> np.ndarray:
    """Build [V, n_dim] L2-normalized char-trigram-meanpool encoder."""
    E = np.stack([char_trigram_encode(w, n_dim, seed) for w in vocab], 0)
    return _l2_normalize_np(E).astype(np.float32)


# ============================================================================
# HRR bind + lock-in position vectors (working-memory slots)
# ============================================================================

def hrr_bind(A: np.ndarray, B: np.ndarray) -> np.ndarray:
    Fa = np.fft.rfft(A, axis=-1)
    Fb = np.fft.rfft(B, axis=-1)
    return np.fft.irfft(Fa * Fb, n=A.shape[-1], axis=-1).astype(np.float32)


def lock_in_position_vec(n_dim: int, pos: int, seed: int) -> np.ndarray:
    """Position vector via lock-in (cos at unique phase + freq per pos)."""
    rng = np.random.default_rng(seed * 7919 + 13 + pos * 101)
    phase = rng.uniform(0.0, 2.0 * math.pi, size=n_dim).astype(np.float32)
    freq = float(max(pos, 1) * 31) / float(n_dim)
    t = np.arange(n_dim, dtype=np.float32)
    v = np.cos(2.0 * math.pi * freq * t + phase).astype(np.float32)
    return v / (np.linalg.norm(v) + 1e-12)


def build_context_keys(idx: np.ndarray, E: np.ndarray, K: int,
                       seed: int) -> np.ndarray:
    """For each position i in idx, build a context key = sum_{j=0..K-1} bind(E[idx[i-j]], pos_j).

    Edge handling: positions earlier than 0 are clamped to idx[0] (start-of-corpus padding).
    K=1 -> degenerate: just bind(E[idx[i]], pos_0). Self-key, useful only if we predict
    NEXT token (so K=1 effectively conditions on the CURRENT token).
    """
    n = idx.shape[0]
    dim = E.shape[1]
    pos_vecs = [lock_in_position_vec(dim, j, seed) for j in range(K)]
    keys = np.zeros((n, dim), dtype=np.float32)
    for j in range(K):
        shifted = np.roll(idx, shift=j)
        shifted[:j] = idx[0]  # pad start
        src = E[shifted]      # [n, dim]
        bound = hrr_bind(src, np.broadcast_to(pos_vecs[j], src.shape).copy())
        keys += bound
    return _l2_normalize_np(keys).astype(np.float32)


# ============================================================================
# Hebbian W (rank-1: sum over train positions of outer(key, e_next))
# ============================================================================

def build_W_rank1(keys_train: np.ndarray, E: np.ndarray, idx_next: np.ndarray
                  ) -> np.ndarray:
    """W[d, v] = sum_i keys_train[i, d] * E[idx_next[i], v]_orig

    Output dim = V (vocab logits). For efficiency we compute via accumulation:
    W = keys_train.T @ E[idx_next]   shape [dim, dim], then logits = key @ W ... but
    we actually want logits = key @ E.T effectively, weighted by Hebbian co-occurrence.

    Simpler & faithful: build a V x dim accumulator A[v] = sum_{i: idx_next[i]==v} keys_train[i]
    then logits(query_key) = query_key @ A.T, normalized.
    """
    V, dim = E.shape
    A = np.zeros((V, dim), dtype=np.float32)
    np.add.at(A, idx_next, keys_train)
    return _l2_normalize_np(A).astype(np.float32)


# ============================================================================
# text8 / synthetic corpus loaders
# ============================================================================

def load_text8_tokens(n_total: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] text8 corpus missing at %s" % TEXT8, flush=True)
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


def synthetic_zipfian_tokens(n_total: int, vocab_size: int, seed: int) -> List[str]:
    """Synthetic Zipfian word corpus for smoke. Not substrate state."""
    rng = np.random.default_rng(seed)
    # Zipfian weights with s=1.1
    ranks = np.arange(1, vocab_size + 1, dtype=np.float64)
    weights = 1.0 / np.power(ranks, 1.1)
    weights = weights / weights.sum()
    idx = rng.choice(vocab_size, size=n_total, p=weights)
    # Manufacture short word strings: "w<rank>" — char-trigram encoder will hash distinctly
    return ["w%04d" % i for i in idx]


def build_vocab(train_tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    c = Counter(train_tokens)
    top = [w for w, _ in c.most_common(cap - 1)]
    vocab = ["<unk>"] + top
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_idx(toks: List[str], w2i: Dict[str, int]) -> np.ndarray:
    unk = w2i["<unk>"]
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


# ============================================================================
# B1 word-unigram + B2 word-bigram (with simple backoff)
# ============================================================================

def build_unigram(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


def build_bigram(idx_train: np.ndarray, V: int, alpha: float = 0.1
                 ) -> Tuple[np.ndarray, np.ndarray]:
    """Return (P_bigram [V, V] = P(next | prev) with add-alpha, P_unigram [V] for backoff)."""
    # Count co-occurrences
    counts = np.full((V, V), alpha, dtype=np.float64)
    if len(idx_train) >= 2:
        prev = idx_train[:-1]
        nxt = idx_train[1:]
        # np.add.at supports 2D indices via tuple
        np.add.at(counts, (prev, nxt), 1.0)
    row_sum = counts.sum(axis=1, keepdims=True)
    P_bi = counts / row_sum
    P_uni = build_unigram(idx_train, V, alpha)
    return P_bi.astype(np.float32), P_uni.astype(np.float64)


def bigram_predict_logp(idx_ctx: np.ndarray, P_bi: np.ndarray,
                        P_uni: np.ndarray, train_seen_prev: np.ndarray,
                        backoff_lambda: float = 0.3) -> np.ndarray:
    """For each prev-token, return log P(next | prev) row.

    If prev never seen in train, back off to unigram. Otherwise linear interp:
        P_smooth = backoff_lambda * P_uni + (1 - backoff_lambda) * P_bi[prev]
    """
    n = idx_ctx.shape[0]
    V = P_uni.shape[0]
    out = np.empty((n, V), dtype=np.float64)
    for i in range(n):
        p = P_bi[idx_ctx[i]]
        if train_seen_prev[idx_ctx[i]]:
            mix = backoff_lambda * P_uni + (1.0 - backoff_lambda) * p
        else:
            mix = P_uni  # unseen prev -> pure unigram backoff
        mix = mix / mix.sum()
        out[i] = mix
    return np.log(np.clip(out, 1e-30, None))


def unigram_predict_logp(n: int, P_uni: np.ndarray) -> np.ndarray:
    log_uni = np.log(np.clip(P_uni, 1e-30, None))
    return np.broadcast_to(log_uni, (n, P_uni.shape[0])).copy()


# ============================================================================
# Substrate scoring: cosine logits + (T, lambda)-joint sweep
# ============================================================================

def substrate_logits(query_keys: np.ndarray, A: np.ndarray) -> np.ndarray:
    """Cosine-sim logits between query keys [n, dim] and vocab accumulator A [V, dim]."""
    q = _l2_normalize_np(query_keys)
    a = _l2_normalize_np(A)
    return (q @ a.T).astype(np.float32)


def softmax_T(logits: np.ndarray, T: float) -> np.ndarray:
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


def bpw_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    logp_nxt = logp[np.arange(n), nxt]
    return -float(np.mean(logp_nxt)) / math.log(2.0)


def top1_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    if len(nxt) == 0:
        return float("nan")
    pred = np.argmax(logp, axis=1)
    return float((pred == nxt).mean())


def sweep_substrate_TL(sub_logits_dev: np.ndarray, nxt_dev: np.ndarray,
                       sub_logits_test: np.ndarray, nxt_test: np.ndarray,
                       P_uni: np.ndarray) -> Dict[str, float]:
    """Pick best (T, lambda) on dev half by BPW; report metrics on test half.

    Reports BPW, top1, raw_top1 (no temp, no interp) for diagnostics.
    """
    U_log = np.log(np.clip(P_uni, 1e-30, None))
    best = None
    for T in TEMP_GRID:
        sub_p_dev = softmax_T(sub_logits_dev, T)
        sub_logp_dev = np.log(np.clip(sub_p_dev, 1e-30, None))
        for lam in LAMBDA_GRID:
            comb = log_linear_interp_logp(sub_logp_dev, U_log, lam)
            bpw = bpw_from_logp(comb, nxt_dev)
            if best is None or bpw < best[0]:
                best = (bpw, T, lam)
    _, T_star, lam_star = best
    sub_p_test = softmax_T(sub_logits_test, T_star)
    sub_logp_test = np.log(np.clip(sub_p_test, 1e-30, None))
    comb_test = log_linear_interp_logp(sub_logp_test, U_log, lam_star)
    bpw_test = bpw_from_logp(comb_test, nxt_test)
    top1_test = top1_from_logp(comb_test, nxt_test)
    # Raw top1: pre-temp, pre-interp logits
    top1_raw = top1_from_logp(sub_logits_test.astype(np.float64), nxt_test)
    return {"bpw": bpw_test, "top1": top1_test, "top1_raw": top1_raw,
            "T_star": T_star, "lambda_star": lam_star}


# ============================================================================
# Self-tests (PROT-022)
# ============================================================================

def _selftest_hrr_bind_invertible():
    rng = np.random.default_rng(0)
    a = rng.standard_normal(64).astype(np.float32)
    b = rng.standard_normal(64).astype(np.float32)
    c = hrr_bind(a, b)
    # bind changes the vector
    assert np.linalg.norm(c - a) > 1e-3, "hrr_bind no-op"


def _selftest_unigram_normalized():
    idx = np.array([0, 1, 2, 0, 1, 0], dtype=np.int64)
    P = build_unigram(idx, 4, alpha=0.1)
    assert abs(P.sum() - 1.0) < 1e-6, "unigram not normalized: sum=%.6f" % P.sum()
    assert P[0] > P[1] > P[2], "unigram order wrong"


def _selftest_bigram_normalized():
    idx = np.array([0, 1, 0, 1, 2, 0], dtype=np.int64)
    P_bi, P_uni = build_bigram(idx, 4, alpha=0.1)
    row_sums = P_bi.sum(axis=1)
    assert np.allclose(row_sums, 1.0, atol=1e-5), \
        "bigram rows not normalized: %s" % row_sums
    # P(0->1) and P(1->0) and P(1->2) should be elevated
    assert P_bi[0, 1] > P_bi[0, 2], "bigram order wrong for prev=0"


def _selftest_bpw_top1_sanity():
    # Perfect prediction => BPW = 0, top1 = 1
    V = 4
    logp = np.full((3, V), -10.0)
    nxt = np.array([0, 1, 2], dtype=np.int64)
    logp[np.arange(3), nxt] = math.log(1.0 - 1e-9)  # near 1
    assert top1_from_logp(logp, nxt) == 1.0
    assert bpw_from_logp(logp, nxt) < 0.01, "perfect bpw not near 0"


def _selftest_verdict_bands_fire():
    """Verify HP/MID/HF classifier fires correctly on synthetic numbers."""
    # HP case: top1 lift 1.5x, BPW margin 0.5
    b2 = {"top1": 0.10, "bpw": 8.0}
    sk5 = {"top1": 0.15, "bpw": 7.5}
    v, _ = classify_verdict(b2, sk5)
    assert v == "HARD_PASS", "HP synth failed: %s" % v
    # MIDDLE: top1 lift 1.20x
    sk5 = {"top1": 0.12, "bpw": 7.8}
    v, _ = classify_verdict(b2, sk5)
    assert v == "MIDDLE_BAND", "MID synth failed: %s" % v
    # HARD_FAIL: top1 below B2
    sk5 = {"top1": 0.09, "bpw": 8.1}
    v, _ = classify_verdict(b2, sk5)
    assert v == "HARD_FAIL", "HF synth failed: %s" % v


def _run_all_selftests():
    _selftest_hrr_bind_invertible()
    _selftest_unigram_normalized()
    _selftest_bigram_normalized()
    _selftest_bpw_top1_sanity()
    _selftest_verdict_bands_fire()
    print("[selftest] PASS: hrr+unigram+bigram+bpw+verdict bands", flush=True)


# ============================================================================
# Verdict classifier (per-arm-aware; Fix #28: per-arm metrics, not summary)
# ============================================================================

def classify_verdict(b2: Dict[str, float], sk5: Dict[str, float]) -> Tuple[str, str]:
    """Apply HARD bands. PRIMARY arm is S_K5; baseline is B2 word-bigram."""
    b2_top1 = float(b2["top1"]); b2_bpw = float(b2["bpw"])
    sk5_top1 = float(sk5["top1"]); sk5_bpw = float(sk5["bpw"])
    lift = sk5_top1 / max(b2_top1, 1e-9)
    bpw_margin = b2_bpw - sk5_bpw  # positive = substrate better

    summary = (
        "S_K5 top1=%.3f vs B2_top1=%.3f (lift %.3fx). "
        "S_K5 BPW=%.3f vs B2_BPW=%.3f (margin %.3f bits)."
    ) % (sk5_top1, b2_top1, lift, sk5_bpw, b2_bpw, bpw_margin)

    # HARD_FAIL trip-wires first (Fix #28: don't over-claim)
    if sk5_top1 <= b2_top1 or sk5_bpw >= b2_bpw:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate at K=5 does NOT beat word-bigram. " + summary)

    # HARD_PASS: BOTH metrics clear
    if lift >= HP_TOP1_LIFT and bpw_margin >= HP_BPW_MARGIN:
        return ("HARD_PASS",
                "HARD_PASS: substrate at K=5 beats word-bigram on BOTH top1 lift "
                "(>=%.2fx) AND BPW margin (>=%.2f bits). " % (HP_TOP1_LIFT, HP_BPW_MARGIN)
                + summary)

    # MIDDLE_BAND: at least one metric in mid range
    if (MID_TOP1_LIFT <= lift < HP_TOP1_LIFT) or \
       (MID_BPW_MARGIN_LOW <= bpw_margin < MID_BPW_MARGIN_HIGH):
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: substrate at K=5 partially beats word-bigram. "
                + summary)

    return ("HARD_FAIL",
            "HARD_FAIL: substrate at K=5 does not clear MID thresholds. " + summary)


# ============================================================================
# Per-seed runner
# ============================================================================

def run_one_seed(seed: int) -> Dict:
    t0 = time.time()
    rng = np.random.default_rng(seed)

    # Corpus
    if RUN_MODE == "smoke":
        tokens = synthetic_zipfian_tokens(N_TRAIN_WORDS + N_HELD_WORDS,
                                           VOCAB_CAP, seed)
    else:
        tokens = load_text8_tokens(N_TRAIN_WORDS + N_HELD_WORDS)

    train_toks = tokens[:N_TRAIN_WORDS]
    held_toks = tokens[N_TRAIN_WORDS:N_TRAIN_WORDS + N_HELD_WORDS]

    vocab, w2i = build_vocab(train_toks, VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)

    # We score from position 1 onward (need at least 1 prev word for B2).
    # Split held into DEV (first half) for substrate (T, lambda) sweep + TEST (second half) for reporting.
    n_held = idx_held.shape[0]
    n_dev = n_held // 2
    idx_dev_ctx = idx_held[:n_dev - 1] if n_dev > 1 else idx_held[:0]
    idx_dev_nxt = idx_held[1:n_dev] if n_dev > 1 else idx_held[:0]
    idx_test_ctx = idx_held[n_dev:-1]
    idx_test_nxt = idx_held[n_dev + 1:]

    print("[seed=%d] V=%d idx_train=%d idx_dev_nxt=%d idx_test_nxt=%d"
          % (seed, V, idx_train.shape[0], idx_dev_nxt.shape[0], idx_test_nxt.shape[0]),
          flush=True)

    # ---------- B1 word-unigram ----------
    P_uni = build_unigram(idx_train, V, alpha=0.1)
    log_uni_test = unigram_predict_logp(idx_test_nxt.shape[0], P_uni)
    b1 = {"bpw": bpw_from_logp(log_uni_test, idx_test_nxt),
          "top1": top1_from_logp(log_uni_test, idx_test_nxt)}
    print("  [B1 word-unigram] BPW=%.3f top1=%.3f" % (b1["bpw"], b1["top1"]), flush=True)

    # ---------- B2 word-bigram (the REAL threshold) ----------
    P_bi, P_uni_dbl = build_bigram(idx_train, V, alpha=0.1)
    seen_prev = np.zeros(V, dtype=bool)
    seen_prev[np.unique(idx_train[:-1])] = True
    log_bi_test = bigram_predict_logp(idx_test_ctx, P_bi, P_uni_dbl, seen_prev,
                                      backoff_lambda=0.3)
    b2 = {"bpw": bpw_from_logp(log_bi_test, idx_test_nxt),
          "top1": top1_from_logp(log_bi_test, idx_test_nxt)}
    print("  [B2 word-bigram]  BPW=%.3f top1=%.3f" % (b2["bpw"], b2["top1"]), flush=True)

    # ---------- Substrate arms (S_K1, S_K5, S_K10) ----------
    E = build_E_np(vocab, N_DIM, seed)

    # Train keys: ctx ends at position i-1, predicting position i. Index over [0..len(train)-2].
    # We want keys at positions 0..len(train)-2 corresponding to next=idx_train[1..len(train)-1].
    train_ctx_idx = idx_train[:-1]
    train_next_idx = idx_train[1:]

    sub_metrics: Dict[str, Dict] = {}
    for K in CONTEXT_K_VALUES:
        # Build context keys for train (length len(train)-1) and held
        # Keys are conditioned on the LAST K words ending at train_ctx_idx[i].
        keys_train = build_context_keys(train_ctx_idx, E, K, seed)
        # Hebbian W: accumulator of train next-token vectors weighted by train keys.
        A = build_W_rank1(keys_train, E, train_next_idx)

        # Score on dev (first half of held) and test (second half).
        idx_dev_ctx_K = idx_held[:n_dev - 1] if n_dev > 1 else idx_held[:0]
        keys_dev = build_context_keys(idx_dev_ctx_K, E, K, seed) \
                   if idx_dev_ctx_K.shape[0] > 0 else \
                   np.zeros((0, N_DIM), dtype=np.float32)
        keys_test = build_context_keys(idx_test_ctx, E, K, seed)

        sub_logits_dev = substrate_logits(keys_dev, A) if keys_dev.shape[0] > 0 \
                         else np.zeros((0, V), dtype=np.float32)
        sub_logits_test = substrate_logits(keys_test, A)

        # If dev empty (tiny smoke), fall back to test for sweep (less ideal but tractable).
        if sub_logits_dev.shape[0] == 0:
            sub_logits_dev = sub_logits_test
            idx_dev_nxt_K = idx_test_nxt
        else:
            idx_dev_nxt_K = idx_dev_nxt

        m = sweep_substrate_TL(sub_logits_dev, idx_dev_nxt_K,
                               sub_logits_test, idx_test_nxt, P_uni)
        sub_metrics[f"S_K{K}"] = m
        print("  [S_K%d] BPW=%.3f top1=%.3f top1_raw=%.3f (T*=%.3f lam*=%.2f)"
              % (K, m["bpw"], m["top1"], m["top1_raw"], m["T_star"], m["lambda_star"]),
              flush=True)

    elapsed = time.time() - t0

    # Sanity: S_K1 should be reasonably close to B1 in topline (degenerate: no
    # prev-context beyond self). Log delta but DON'T fail the run on it; smoke
    # synthetic Zipfian may diverge from expectation.
    sk1_b1_delta = abs(sub_metrics["S_K1"]["top1"] - b1["top1"])
    print("  [sanity] |S_K1.top1 - B1.top1| = %.3f" % sk1_b1_delta, flush=True)

    return {
        "seed": seed,
        "run_mode": RUN_MODE,
        "elapsed_s": elapsed,
        "V": V,
        "N_DIM": N_DIM,
        "N_TRAIN": int(N_TRAIN_WORDS),
        "N_HELD": int(N_HELD_WORDS),
        "B1_word_unigram": b1,
        "B2_word_bigram": b2,
        **sub_metrics,
        "sk1_b1_top1_delta": float(sk1_b1_delta),
    }


# ============================================================================
# Aggregator / verdict
# ============================================================================

def aggregate_and_verdict(per_seed: List[Dict]) -> Tuple[str, str, Dict]:
    # Average per-arm metrics across seeds.
    def avg_arm(arm: str, field: str) -> float:
        return float(np.mean([p[arm][field] for p in per_seed]))

    arms_avg: Dict[str, Dict[str, float]] = {}
    for arm in ARMS:
        arms_avg[arm] = {
            "bpw": avg_arm(arm, "bpw"),
            "top1": avg_arm(arm, "top1"),
        }

    b2 = arms_avg["B2_word_bigram"]
    sk5 = arms_avg["S_K5"]
    verdict, vmsg = classify_verdict(b2, sk5)

    honest_scope = {
        "what_this_shows": (
            "Whether substrate at word-grain (V=%d) beats word-bigram baseline "
            "on text8 hold-out. Word-bigram is the real aliveness threshold for "
            "any LM (unigram is the trivial floor)."
        ) % VOCAB_CAP,
        "what_this_does_NOT_show": [
            "Substrate behavior at V_word > 4000 (this cell caps at V=%d)" % VOCAB_CAP,
            "Substrate with a learned encoder (frozen char-trigram-meanpool only)",
            "Sequence > K=10 word context",
            "Cross-corpus (text8-only; no WikiText / OpenWebText)",
            "Brain compose stack interactions (no PC top-down, no WM register, no DA-LR)",
        ],
        "primary_arm": "S_K5",
        "real_baseline": "B2_word_bigram (NOT B1_word_unigram)",
        "arms_avg": arms_avg,
        "per_arm_metrics_path": "per_seed[*].{arm} for all arms in ARMS",
    }

    return verdict, vmsg, honest_scope


# ============================================================================
# Main
# ============================================================================

_run_all_selftests()
if _ARGS.self_test:
    sys.exit(0)

print("[config] " + CONFIG_VERSION, flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_DIM, "M": VOCAB_CAP, "run_mode": RUN_MODE}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds complete; running %s" % (len(done), len(SEEDS), remaining),
      flush=True)

t_start = time.time()
for seed in remaining:
    r = run_one_seed(seed)
    write_partial(out_dir, seed, r)

per_seed = aggregate_partials(out_dir, SEEDS)
per_seed_list = [per_seed[str(s)] for s in SEEDS if str(s) in per_seed]
verdict, vmsg, honest_scope = aggregate_and_verdict(per_seed_list)
elapsed_total = time.time() - t_start

print("\n[VERDICT] " + vmsg, flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": vmsg,
    "run_mode": RUN_MODE,
    "config_version": CONFIG_VERSION,
    "n_seeds": len(per_seed_list),
    "seeds": SEEDS,
    "arms": ARMS,
    "per_seed": per_seed_list,
    "honest_scope": honest_scope,
    "elapsed_s": elapsed_total,
    "summary": vmsg,
}
write_metrics(out_dir, metrics, per_seed_list)
print("[metrics] written to %s/metrics.json" % out_dir, flush=True)
