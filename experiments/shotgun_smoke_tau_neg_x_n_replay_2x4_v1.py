"""
shotgun_smoke_tau_neg_x_n_replay_2x4_v1 -- 2x4 factorial of dual-trace TAU_NEG x N_REPLAY.

PURPOSE: Information acquisition only. NOT a cert cell. NO queue ship.
GOAL: Determine which timescale axes are load-bearing for substrate-LM BPC.

NINE ARMS:
  ARM_VEHICLE      -- no dual-trace, no replay (pure rank-1 Hebbian single-pass)
  ARM_T50_R1       -- TAU_NEG=50, N_REPLAY=1   (current defaults; sanity check)
  ARM_T50_R10      -- TAU_NEG=50, N_REPLAY=10
  ARM_T50_R30      -- TAU_NEG=50, N_REPLAY=30
  ARM_T50_R100     -- TAU_NEG=50, N_REPLAY=100
  ARM_T10_R1       -- TAU_NEG=10 (brain-canonical 2x ratio), N_REPLAY=1
  ARM_T10_R10      -- TAU_NEG=10, N_REPLAY=10
  ARM_T10_R30      -- TAU_NEG=10, N_REPLAY=30
  ARM_T10_R100     -- TAU_NEG=10, N_REPLAY=100

SMOKE CONFIG: N=512, VOCAB=100, N_TRAIN=2000, N_HELD=400. Pure numpy. ~5-15min total.
TAU_POS fixed at 5 across all dual-trace arms (per handoff spec).

PRE-REGISTERED BANDS (information-acquisition only; no cert atomization):
  CONFIRM_BOTH_AXES:  ARM_T10_R10 (or any T10 arm) beats ARM_T50_R1 by >= 0.05 BPC
                      AND N_REPLAY axis shows monotone trend (R10 or R30 beats R1)
  TAU_NEG_LOAD:       T10 arms beat T50 arms by >= 0.05 BPC on average (ratio matters)
  REPLAY_LOAD:        R10+ beats R1 by >= 0.05 BPC on average across both TAU values
  TAU_NEG_NULL:       T10 vs T50 diff < 0.02 BPC (ratio doesn't matter at smoke scale)
  REPLAY_NULL:        N_REPLAY axis diff < 0.02 BPC (single-pass is enough)
  BOTH_NULL:          all arms within 0.05 BPC of ARM_VEHICLE

WHAT_THIS_DOES_NOT_SHOW:
  - N=512 may miss effects that emerge at production N=8192 (small-N smoke)
  - N_TRAIN=2000 tokens is too short to saturate chunked-trace timescales at tau=50
    (50 chunks x INGEST_CHUNK=512 = 25600 tokens; smoke has only 4 chunks)
    TAU_NEG null at smoke scale does NOT imply null at production scale
  - Replay at smoke scale re-uses same 2000 tokens; production replay differs
    (production: replay distinct held-out episodes vs smoke: repeat same sequence)
  - Does not test per-token timescale binding (only chunk-granularity traces)
  - Not a continual-learning retention test; only single-sequence BPC

ASCII-only. No cert atoms. Information acquisition only.
"""

import sys
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

import numpy as np
import math
import time
import json
import os
from collections import Counter
from pathlib import Path
from typing import Dict, List, Tuple

REPO = Path(__file__).resolve().parent.parent

# ============================================================================
# Config
# ============================================================================
N_DIM = 512
VOCAB_CAP = 100
N_TRAIN = 2000
N_HELD = 400
INGEST_CHUNK = 512    # chunk granularity for trace update
SEEDS = [42, 137]     # 2 seeds for speed; enough for consistency check
TAU_POS = 5           # fast LTP trace (fixed)
SPARSE_F = 0.05       # fraction of active bits (5% sparsity)

TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

# Temperature/lambda grid for BPC scoring (smaller than full grid; enough for smoke)
TEMP_GRID = [0.05, 0.1, 0.2, 0.5, 1.0]
LAMBDA_GRID = [0.0, 0.3, 0.7, 1.0]

# Arms: (arm_label, tau_neg, n_replay)
# ARM_VEHICLE has no dual-trace (tau_neg=None signals vehicle mode)
ARMS = [
    ("ARM_VEHICLE", None, 0),
    ("ARM_T50_R1",  50,   1),
    ("ARM_T50_R10", 50,  10),
    ("ARM_T50_R30", 50,  30),
    ("ARM_T50_R100",50, 100),
    ("ARM_T10_R1",  10,   1),
    ("ARM_T10_R10", 10,  10),
    ("ARM_T10_R30", 10,  30),
    ("ARM_T10_R100",10, 100),
]


# ============================================================================
# Instrumentation self-test (MANDATORY per role contract)
# ============================================================================

def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    rng = np.random.default_rng(0)
    V = 10
    D = 64
    E_test = rng.standard_normal((V, D)).astype(np.float32)
    norms = np.linalg.norm(E_test, axis=1, keepdims=True)
    E_test = E_test / np.clip(norms, 1e-12, None)
    idx_tr = rng.integers(0, V, size=50, dtype=np.int64)
    idx_he = rng.integers(0, V, size=10, dtype=np.int64)
    # vehicle arm
    logits = run_arm_numpy(E_test, idx_tr, idx_he, tau_neg=None, n_replay=0, seed=0)
    assert logits is not None, "run_arm_numpy returned None"
    # logits has n_h = len(idx_he) - 1 rows (predict next for each src position)
    expected_rows = len(idx_he) - 1
    assert logits.shape[0] == expected_rows and logits.shape[1] == V, \
        "logits shape wrong: got %s, expected (%d, %d)" % (str(logits.shape), expected_rows, V)
    # dual-trace arm
    logits_dt = run_arm_numpy(E_test, idx_tr, idx_he, tau_neg=10, n_replay=1, seed=0)
    assert logits_dt is not None and logits_dt.shape == logits.shape, \
        "dual-trace logits shape wrong: got %s" % str(logits_dt.shape if logits_dt is not None else None)
    # BPC is finite
    unigram = np.ones(V, dtype=np.float64) / V
    u_log = np.log(unigram)[None, :]
    nxt = idx_he[1:len(idx_he)]
    bpc = compute_best_bpc(logits[:len(nxt)], u_log, nxt)
    assert np.isfinite(bpc), "BPC is not finite: %s" % bpc
    assert bpc > 0.0, "BPC is zero (sentinel): %s" % bpc
    print("[selftest] PASS: logits shape OK, BPC finite=%.4f" % bpc, flush=True)


# ============================================================================
# Encoding helpers (pure numpy)
# ============================================================================

def _seed_for_trigram(trigram: str, seed: int) -> int:
    import hashlib
    h = hashlib.blake2b((trigram + ":" + str(seed)).encode("utf-8"), digest_size=4).digest()
    return int.from_bytes(h, "big")


def _bipolar_hv(seed_val: int, n_dim: int) -> np.ndarray:
    rng = np.random.default_rng(seed_val % (2**31))
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


def build_E_char_trigram(vocab: List[str], n_dim: int, seed: int) -> np.ndarray:
    rows = [char_trigram_encode(w, n_dim, seed) for w in vocab]
    E = np.stack(rows, axis=0).astype(np.float32)
    norms = np.linalg.norm(E, axis=1, keepdims=True)
    return E / np.clip(norms, 1e-12, None)


def sparsify_bipolar(E: np.ndarray, f: float, seed: int) -> np.ndarray:
    """Keep top-k by abs value; sign-binarize. Pure numpy."""
    V, D = E.shape
    k = max(1, int(round(f * D)))
    out = np.zeros_like(E)
    for i in range(V):
        idx = np.argpartition(np.abs(E[i]), -k)[-k:]
        out[i, idx] = np.sign(E[i, idx])
        out[i, out[i] == 0] = 1.0
    return out


# ============================================================================
# W-builder helpers (pure numpy)
# ============================================================================

def _l2_norm_rows(X: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    n = np.linalg.norm(X, axis=1, keepdims=True)
    return X / np.clip(n, eps, None)


def build_W_vehicle(idx_train: np.ndarray, E: np.ndarray) -> np.ndarray:
    """Pure rank-1 Hebbian single-pass (no neuromodulator, no replay)."""
    D = E.shape[1]
    W = np.zeros((D, D), dtype=np.float32)
    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return W
    for b in range(0, n_pairs, INGEST_CHUNK):
        end = min(b + INGEST_CHUNK, n_pairs)
        E_src = E[idx_train[b:end]]       # [chunk, D]
        E_tgt = E[idx_train[b+1:end+1]]   # [chunk, D]
        W += (E_tgt.T @ E_src) / max(n_pairs, 1)
    return W


def build_W_dual_trace_single_pass(
        idx_train: np.ndarray,
        E: np.ndarray,
        tau_neg: int,
        tau_pos: int = TAU_POS,
) -> np.ndarray:
    """Dual-trace W-builder (one pass, pure numpy).

    E_pos: LTP trace (fast tau_pos), gated by dopamine (cf-RPE error norm)
    E_neg: LTD trace (slow tau_neg), gated by ACh (familiarity / cosine margin)
    W += dopa * E_pos - ach * E_neg

    Implementation: chunked EMA approximation (same as v1 torch script).
    """
    D = E.shape[1]
    W = np.zeros((D, D), dtype=np.float32)
    E_pos = np.zeros((D, D), dtype=np.float32)
    E_neg = np.zeros((D, D), dtype=np.float32)

    decay_pos = 1.0 - 1.0 / tau_pos
    decay_neg = 1.0 - 1.0 / tau_neg

    n_pairs = len(idx_train) - 1
    if n_pairs <= 0:
        return W

    err_norm_running = 1.0
    ema_alpha = 0.95
    ctx_buf: List[np.ndarray] = []
    NEUROMOD_CTX = 32

    for b in range(0, n_pairs, INGEST_CHUNK):
        end = min(b + INGEST_CHUNK, n_pairs)
        chunk_sz = end - b
        E_src = E[idx_train[b:end]]
        E_tgt = E[idx_train[b+1:end+1]]

        pred = E_src @ W.T                          # [chunk, D]
        Delta = E_tgt - pred                        # [chunk, D]

        # Chunk-mean outer products
        outer_pos = (Delta.T @ E_src) / max(chunk_sz, 1)
        outer_neg = (pred.T @ E_src) / max(chunk_sz, 1)

        # Trace EMA
        E_pos = decay_pos * E_pos + (1.0 - decay_pos) * outer_pos
        E_neg = decay_neg * E_neg + (1.0 - decay_neg) * outer_neg

        # Dopamine: cf-RPE error norm gating
        err_norms = np.linalg.norm(Delta, axis=1)
        err_mean = float(err_norms.mean())
        denom = max(err_norm_running, 1e-6)
        dopa = min(1.5, max(0.0, err_mean / denom))
        err_norm_running = ema_alpha * err_norm_running + (1.0 - ema_alpha) * err_mean

        # ACh: cosine margin (attention / familiarity)
        src_norm = np.linalg.norm(E_src.mean(axis=0))
        if src_norm > 1e-9:
            src_centroid = E_src.mean(axis=0) / src_norm
        else:
            src_centroid = E_src.mean(axis=0)

        if len(ctx_buf) >= 4:
            ctx_stack = np.stack(ctx_buf[-NEUROMOD_CTX:], axis=0)
            ctx_cen_raw = ctx_stack.mean(axis=0)
            cn = np.linalg.norm(ctx_cen_raw)
            ctx_cen = ctx_cen_raw / max(cn, 1e-9)
            sim = float(np.dot(src_centroid, ctx_cen))
            ach = min(1.5, max(0.0, (1.0 - sim) * 1.5))
        else:
            ach = 0.0   # startup: no LTD before context builds

        ctx_buf.append(src_centroid)
        if len(ctx_buf) > NEUROMOD_CTX * 4:
            ctx_buf = ctx_buf[-NEUROMOD_CTX:]

        # W update
        if dopa > 1e-9:
            W += dopa * E_pos
        if ach > 1e-9:
            W -= ach * E_neg

    return W


def build_W_dual_trace_multipass(
        idx_train: np.ndarray,
        E: np.ndarray,
        tau_neg: int,
        n_replay: int,
        seed: int,
        tau_pos: int = TAU_POS,
) -> np.ndarray:
    """Multi-pass CLS-replay: run n_replay passes of dual-trace W-builder.

    Each replay pass uses the same training sequence (in the same order for
    determinism at smoke scale). W accumulates across passes (additive replay).
    Rationale: brain SWR replay fires 10^4-10^5 times/night; 1x is brain-wrong.

    NOTE: at smoke scale N_TRAIN=2000 this re-runs the same 2000 tokens n_replay times.
    In production, replay would use distinct replay episodes or shuffled sequence.
    """
    D = E.shape[1]
    W = np.zeros((D, D), dtype=np.float32)

    rng = np.random.default_rng(seed + 7919)
    for replay_i in range(n_replay):
        # Shuffle within replay pass (each pass sees same content, different order)
        perm = rng.permutation(len(idx_train))
        idx_shuffled = idx_train[perm]
        W_pass = build_W_dual_trace_single_pass(idx_shuffled, E, tau_neg, tau_pos)
        # Additive accumulation across passes (normalized by n_replay)
        W += W_pass

    # Normalize by number of passes
    if n_replay > 0:
        W /= n_replay

    return W


# ============================================================================
# Arm runner (pure numpy)
# ============================================================================

def run_arm_numpy(
        E: np.ndarray,
        idx_train: np.ndarray,
        idx_held: np.ndarray,
        tau_neg,
        n_replay: int,
        seed: int,
) -> np.ndarray:
    """Build W for the arm; return held-set cosine logits.

    Returns logits shape [len(idx_held)-1, V] where logits[i,j] = cos(W@E[src], E[j]).
    """
    D, V = E.shape[1], E.shape[0]

    if tau_neg is None:
        # Vehicle: no dual-trace, no replay
        W = build_W_vehicle(idx_train, E)
    elif n_replay == 1:
        W = build_W_dual_trace_single_pass(idx_train, E, tau_neg)
    else:
        W = build_W_dual_trace_multipass(idx_train, E, tau_neg, n_replay, seed)

    # Recall logits on held set
    n_h = len(idx_held) - 1
    if n_h <= 0:
        return np.zeros((0, V), dtype=np.float32)

    E_src_held = E[idx_held[:n_h]]          # [n_h, D]
    pred = _l2_norm_rows(E_src_held @ W.T)  # [n_h, D] normalized predictions

    # Normalize E for cosine logits
    E_norm = _l2_norm_rows(E)               # [V, D]
    logits = pred @ E_norm.T                # [n_h, V]
    return logits.astype(np.float32)


# ============================================================================
# BPC scoring (pure numpy)
# ============================================================================

def softmax_np(logits: np.ndarray, T: float) -> np.ndarray:
    z = logits / max(T, 1e-9)
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return e / np.clip(e.sum(axis=-1, keepdims=True), 1e-30, None)


def log_linear_interp(logp_sub: np.ndarray, u_log: np.ndarray, lam: float) -> np.ndarray:
    combined = lam * logp_sub + (1.0 - lam) * u_log
    combined = combined - combined.max(axis=1, keepdims=True)
    Z = np.log(np.clip(np.exp(combined).sum(axis=1), 1e-30, None))
    return combined - Z[:, None]


def bpc_from_logp(logp: np.ndarray, nxt: np.ndarray) -> float:
    n = len(nxt)
    if n == 0:
        return float("inf")
    return -float(np.mean(logp[np.arange(n), nxt])) / math.log(2.0)


def compute_best_bpc(
        logits: np.ndarray,
        u_log: np.ndarray,
        nxt: np.ndarray,
) -> float:
    """Grid-search T and lambda; return best BPC."""
    n = len(nxt)
    if n == 0:
        return float("inf")

    best = float("inf")
    for T in TEMP_GRID:
        probs = softmax_np(logits, T)
        logp_sub = np.log(np.clip(probs, 1e-30, 1.0))
        for lam in LAMBDA_GRID:
            logp = log_linear_interp(logp_sub, u_log, lam)
            b = bpc_from_logp(logp, nxt)
            if b < best:
                best = b
    return best


# ============================================================================
# Corpus loading
# ============================================================================

def load_text8_tokens(n: int) -> List[str]:
    if not TEXT8.exists():
        print("[FATAL] text8 missing at %s" % TEXT8, flush=True)
        sys.exit(1)
    out: List[str] = []
    with TEXT8.open("r", encoding="utf-8") as f:
        buf = ""
        while len(out) < n:
            chunk = f.read(1 << 20)
            if not chunk:
                break
            buf += chunk
            parts = buf.split(" ")
            buf = parts.pop()
            out.extend(parts)
        if buf and len(out) < n:
            out.append(buf)
    return out[:n]


def build_vocab(tokens: List[str], cap: int) -> Tuple[List[str], Dict[str, int]]:
    c = Counter(tokens)
    top = [w for w, _ in c.most_common(cap - 1)]
    vocab = ["<unk>"] + top
    w2i = {w: i for i, w in enumerate(vocab)}
    return vocab, w2i


def tokens_to_idx(toks: List[str], w2i: Dict[str, int]) -> np.ndarray:
    unk = w2i["<unk>"]
    return np.array([w2i.get(t, unk) for t in toks], dtype=np.int64)


def build_unigram(idx_train: np.ndarray, V: int) -> np.ndarray:
    counts = np.full(V, 0.1, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


# ============================================================================
# Main sweep
# ============================================================================

def main():
    print("=== shotgun_smoke_tau_neg_x_n_replay_2x4_v1 ===", flush=True)
    print("CONFIG: N=%d VOCAB=%d N_TRAIN=%d N_HELD=%d SEEDS=%s" %
          (N_DIM, VOCAB_CAP, N_TRAIN, N_HELD, SEEDS), flush=True)
    t_start = time.time()

    # Load corpus
    total_tokens = N_TRAIN + N_HELD + 10
    print("Loading %d text8 tokens..." % total_tokens, flush=True)
    all_tokens = load_text8_tokens(total_tokens)
    train_toks = all_tokens[:N_TRAIN]
    held_toks = all_tokens[N_TRAIN:N_TRAIN + N_HELD]

    vocab, w2i = build_vocab(train_toks, VOCAB_CAP)
    V = len(vocab)
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    print("Vocab size: %d" % V, flush=True)

    # Results container
    results: Dict[str, List[float]] = {arm[0]: [] for arm in ARMS}

    for seed in SEEDS:
        print("\n--- Seed %d ---" % seed, flush=True)

        # Build encoder (char-trigram, sparsified)
        E_base = build_E_char_trigram(vocab, N_DIM, seed)
        E = sparsify_bipolar(E_base, SPARSE_F, seed)
        E = _l2_norm_rows(E)

        # Unigram log probs
        unigram = build_unigram(idx_train, V)
        u_log = np.log(np.clip(unigram, 1e-30, None))[None, :]  # [1, V]

        # Held-set next-word targets
        nxt_held = idx_held[1:min(len(idx_held), N_HELD)]
        n_eval = len(nxt_held)

        for arm_label, tau_neg, n_replay in ARMS:
            t0 = time.time()
            logits = run_arm_numpy(E, idx_train, idx_held, tau_neg, n_replay, seed)
            logits_eval = logits[:n_eval]
            bpc = compute_best_bpc(logits_eval, u_log, nxt_held)
            wall = time.time() - t0
            results[arm_label].append(bpc)
            print("  %-20s tau_neg=%-5s n_replay=%-4d  bpc=%.4f  wall=%.1fs" %
                  (arm_label,
                   str(tau_neg) if tau_neg is not None else "None",
                   n_replay,
                   bpc,
                   wall), flush=True)

    # ============================================================================
    # Summary
    # ============================================================================
    print("\n=== PER-ARM SUMMARY (mean +/- std across %d seeds) ===" % len(SEEDS), flush=True)

    vehicle_bpc = float(np.mean(results["ARM_VEHICLE"]))
    print("%-20s  mean=%.4f  (vehicle / no dual-trace no replay)" %
          ("ARM_VEHICLE", vehicle_bpc), flush=True)

    arm_means: Dict[str, float] = {}
    for arm_label, tau_neg, n_replay in ARMS:
        vals = results[arm_label]
        mu = float(np.mean(vals))
        std = float(np.std(vals)) if len(vals) > 1 else 0.0
        arm_means[arm_label] = mu
        lift = vehicle_bpc - mu   # positive = better than vehicle (lower BPC is better)
        flag = ""
        if abs(lift) < 0.02:
            flag = "[FLAT vs vehicle]"
        elif lift < -0.02:
            flag = "[WORSE than vehicle]"
        else:
            flag = "[LIFT +%.4f]" % lift
        print("%-20s  mean=%.4f std=%.4f  lift_vs_vehicle=%+.4f  %s" %
              (arm_label, mu, std, lift, flag), flush=True)

    # ============================================================================
    # HARD_INFO interpretation
    # ============================================================================
    print("\n=== HARD_INFO INTERPRETATION ===", flush=True)

    # TAU_NEG axis: average lift of T10 arms vs T50 arms (matched by N_REPLAY)
    tau_neg_pairs = [
        ("ARM_T50_R1",  "ARM_T10_R1"),
        ("ARM_T50_R10", "ARM_T10_R10"),
        ("ARM_T50_R30", "ARM_T10_R30"),
        ("ARM_T50_R100","ARM_T10_R100"),
    ]
    tau_neg_diffs = []
    for t50_label, t10_label in tau_neg_pairs:
        diff = arm_means[t50_label] - arm_means[t10_label]  # positive = T10 better (lower BPC)
        tau_neg_diffs.append(diff)
    tau_neg_axis_delta = float(np.mean(tau_neg_diffs))

    # N_REPLAY axis: average lift of R10+ arms vs R1 arms (matched by TAU_NEG)
    replay_pairs = [
        ("ARM_T50_R1",  "ARM_T50_R10"),
        ("ARM_T50_R1",  "ARM_T50_R30"),
        ("ARM_T50_R1",  "ARM_T50_R100"),
        ("ARM_T10_R1",  "ARM_T10_R10"),
        ("ARM_T10_R1",  "ARM_T10_R30"),
        ("ARM_T10_R1",  "ARM_T10_R100"),
    ]
    replay_diffs = []
    for r1_label, rN_label in replay_pairs:
        diff = arm_means[r1_label] - arm_means[rN_label]  # positive = rN better (lower BPC)
        replay_diffs.append(diff)
    replay_axis_delta = float(np.mean(replay_diffs))

    # Best arm overall
    best_arm = min(arm_means, key=arm_means.__getitem__)
    best_bpc_val = arm_means[best_arm]
    best_lift = vehicle_bpc - best_bpc_val

    print("TAU_NEG axis delta (T10 vs T50, mean):  %+.4f bits" % tau_neg_axis_delta, flush=True)
    print("  (positive = T10 better; negative = T50 better or neutral)", flush=True)
    print("N_REPLAY axis delta (rN vs r1, mean):   %+.4f bits" % replay_axis_delta, flush=True)
    print("  (positive = multi-replay better; negative = single-pass better)", flush=True)
    print("Best arm: %s  bpc=%.4f  lift_vs_vehicle=%+.4f" %
          (best_arm, best_bpc_val, best_lift), flush=True)

    # Classification
    TAU_THRESH = 0.02
    REPLAY_THRESH = 0.02
    CONFIRM_THRESH = 0.05

    if tau_neg_axis_delta > CONFIRM_THRESH and replay_axis_delta > CONFIRM_THRESH:
        classification = "CONFIRM_BOTH_AXES"
        interp = "Both TAU_NEG and N_REPLAY are load-bearing at smoke scale. Full-scale cell warranted."
    elif tau_neg_axis_delta > TAU_THRESH and replay_axis_delta <= REPLAY_THRESH:
        classification = "TAU_NEG_LOAD_ONLY"
        interp = "TAU_NEG axis matters; N_REPLAY axis null at smoke scale. May emerge at production."
    elif tau_neg_axis_delta <= TAU_THRESH and replay_axis_delta > REPLAY_THRESH:
        classification = "REPLAY_LOAD_ONLY"
        interp = "N_REPLAY axis matters; TAU_NEG null at smoke scale. May emerge at production."
    elif abs(tau_neg_axis_delta) < TAU_THRESH and abs(replay_axis_delta) < REPLAY_THRESH:
        classification = "BOTH_NULL_AT_SMOKE"
        interp = ("Both axes null at smoke scale. NOT production-null: " +
                  "smoke N_TRAIN=2000 has only ~4 chunks -- too few for TAU_NEG=50 " +
                  "to accumulate. Recommend full-scale test before concluding.")
    elif tau_neg_axis_delta < -TAU_THRESH or replay_axis_delta < -REPLAY_THRESH:
        classification = "DEGRADED"
        interp = "One or both axes degrade BPC vs baseline. Check for numeric instability."
    else:
        classification = "AMBIGUOUS"
        interp = "Mixed signals. Recommend full-scale test."

    print("\nCLASSIFICATION: %s" % classification, flush=True)
    print("INTERPRETATION: %s" % interp, flush=True)

    wall_total = time.time() - t_start
    print("\nTotal wall time: %.1fs" % wall_total, flush=True)

    # ============================================================================
    # Write summary JSON
    # ============================================================================
    out_dir = REPO / "data" / "shotgun_smoke_tau_neg_x_n_replay_2x4_v1"
    out_dir.mkdir(parents=True, exist_ok=True)
    summary = {
        "anchor": "shotgun_smoke_tau_neg_x_n_replay_2x4_v1",
        "config": {
            "N_DIM": N_DIM,
            "VOCAB_CAP": VOCAB_CAP,
            "N_TRAIN": N_TRAIN,
            "N_HELD": N_HELD,
            "SEEDS": SEEDS,
            "TAU_POS": TAU_POS,
            "SPARSE_F": SPARSE_F,
        },
        "arm_means": {k: round(v, 6) for k, v in arm_means.items()},
        "vehicle_bpc": round(vehicle_bpc, 6),
        "tau_neg_axis_delta": round(tau_neg_axis_delta, 6),
        "replay_axis_delta": round(replay_axis_delta, 6),
        "best_arm": best_arm,
        "best_bpc": round(best_bpc_val, 6),
        "best_lift_vs_vehicle": round(best_lift, 6),
        "classification": classification,
        "interpretation": interp,
        "wall_s": round(wall_total, 1),
    }
    with open(out_dir / "summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("Summary written to %s" % (out_dir / "summary.json"), flush=True)

    return summary


# ============================================================================
# Run self-test before sweep
# ============================================================================
_instrumentation_selftest()

if __name__ == "__main__":
    main()
