"""ca3_sequence_prediction_lm_smoke_v1 -- CA3 composition LM mechanism via brain-grounded primitives.

Source: notes/research_5x_deeper_substrate_LM_gap_2026-06-23.md Section L1.4
(Tsodyks-Sejnowski 1995; Hasselmo 2002; Salvatori 2024 CA3-as-RNN).

Intuitive (no jargon): CA3 hippocampal subfield is the canonical biological
autoassociative memory + sequence-completion structure. We compose:
  bind(prev_token, position) -> recurrent autoassociative cleanup ->
  heteroassociative completion -> next_token distribution.
Substrate has all primitives (`sequence_memory.SequenceMatrix` for the bind,
`iterative_attractor.iterative_cleanup` for the auto-assoc step). Never
composed this way before; structurally distinct from Path A v2's rank-1 Hebbian.

DESIGN (4 arms x 3 seeds, smoke-only, CPU, numpy):
  ARM_UNIGRAM         : baseline; BPC floor at expected ~7.74 (smoke text8 sub-window).
  ARM_PATH_A_RAW      : current substrate rank-1 Hebbian W = sum (E[t+1] outer E[t]);
                        prediction p = softmax(W @ E[ctx]). Reproduces Path A regime.
  ARM_CA3_HETERO_ONLY : substrate writes W += bind(E[prev], P[pos]) outer E[next];
                        predicts next from bind(E[cue], P[pos]) -> W -> softmax over E.T.
                        Position carriers P are bipolar HD vectors (a fixed pool of K=16
                        positional codes, cycled). Hetero-assoc step ONLY.
  ARM_CA3_FULL        : CA3_HETERO_ONLY + iterative_attractor cleanup on the bound
                        cue (bind(E[cue], P[pos])) before the heteroassoc readout.
                        The cleanup pulls the cue vector toward the nearest stored
                        attractor in a substrate codebook built from {E[v] : v in vocab}.
                        Iterative not single-shot; basin attraction.

PRE-REG bands (chain-grade-eligible mechanism):
  HARD_PASS : ARM_CA3_FULL mean test BPC < ARM_UNIGRAM mean test BPC (CA3 composition
              beats unigram floor at smoke scale). Substrate-only (zero LLM calls).
  HARD_FAIL : ARM_CA3_FULL mean test BPC >= ARM_PATH_A_RAW mean test BPC (CA3 composition
              does NOT lift over raw rank-1 Hebbian -- mechanism dead).
  MIDDLE    : ARM_CA3_FULL mean test BPC in (ARM_UNIGRAM, ARM_PATH_A_RAW] -- partial
              mechanism characterization; lift over raw but not over unigram.

Sanity self-test: at N_TRAIN=10 tokens (trivial cycle vocab), all CA3 arms should
recover the memorized 10-token sequence at acc >= 0.7 (per Path A self-test convention).

Scale (smoke):
  V=4000, N_DIM=4096, N_TRAIN=10_000, N_HELD=2_000, seeds=[7,17,23], K_POS=16.
  Full (queued only if smoke not-HARD_FAIL): N_TRAIN=100_000, N_HELD=5_000.

Substrate-only-decode: zero LLM calls at inference (counter asserted at exit).
ASCII-only. numpy-only (CPU). Per-seed checkpoint via _seed_checkpoint helper.

Composes:
  hdlab.char_trigram_encoder.CharTrigramEncoder (vocab encoder)
  hdlab.sequence_memory.SequenceMatrix         (the bind primitive S)
  hdlab.iterative_attractor.iterative_cleanup  (autoassoc cleanup)
"""
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
import math
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
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

# Pull in substrate primitives by direct re-import to keep numpy-only path clean
from hdlab.iterative_attractor import iterative_cleanup as substrate_iterative_cleanup

ANCHOR_NAME = "ca3_sequence_prediction_lm_smoke_v1"
TEXT8 = REPO / "data" / "text8_cache" / "text8.txt"

_LLM_CALL_COUNTER = [0]
_METRICS_WRITTEN = [False]


def _detect_run_mode():
    if "--smoke" in sys.argv:
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.endswith("_smoke"):
        return "smoke"
    return "full"


RUN_MODE = _detect_run_mode()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

# Config per RUN_MODE
# Smoke is the canonical smoke gate target for this anchor (task says smoke-only;
# bundle FULL only if smoke not-HARD_FAIL). FULL config retained for follow-on.
if RUN_MODE == "smoke":
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    N_TRAIN = 10_000
    N_HELD = 2_000
    VOCAB_CAP = 4000
    K_POS = 16
    INGEST_CHUNK = 4096
    CLEANUP_TEMP = 4.0
    CLEANUP_MAX_STEPS = 4
    CLEANUP_TOL = 1e-3
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    N_TRAIN = 100_000
    N_HELD = 5_000
    VOCAB_CAP = 4000
    K_POS = 16
    INGEST_CHUNK = 4096
    CLEANUP_TEMP = 4.0
    CLEANUP_MAX_STEPS = 4
    CLEANUP_TOL = 1e-3

CONFIG_VERSION = (
    "ca3-sequence-prediction-lm-smoke-v1: N_DIM=%d N_TRAIN=%d N_HELD=%d "
    "VOCAB_CAP=%d K_POS=%d INGEST_CHUNK=%d cleanup_temp=%.1f cleanup_max_steps=%d "
    "cleanup_tol=%g run_mode=%s; arms=[UNIGRAM,PATH_A_RAW,CA3_HETERO_ONLY,CA3_FULL]; "
    "bands HP=CA3_FULL<UNIGRAM HF=CA3_FULL>=PATH_A_RAW MID=between"
) % (
    N_DIM, N_TRAIN, N_HELD, VOCAB_CAP, K_POS, INGEST_CHUNK,
    CLEANUP_TEMP, CLEANUP_MAX_STEPS, CLEANUP_TOL, RUN_MODE,
)


# ============================================================================
# Substrate primitives (numpy-flat; mirror Path A regime)
# ============================================================================

def char_trigram_encode_np(word: str, dim: int, seed: int = 0) -> np.ndarray:
    """Char-trigram bipolar HD encoder; deterministic per (word, seed).

    Mirrors the encoder used by `text8_substrate_pseudoLM_v2_temperature_calibrated_v1`
    so the Path A control arm is exactly comparable.
    """
    v = np.zeros(dim, np.float32)
    w = "#" + word + "#"
    for i in range(len(w) - 2):
        tri = w[i:i + 3]
        h = int(hashlib.md5((tri + ":" + str(seed)).encode()).hexdigest(), 16)
        idx = h % dim
        sign = 1.0 if ((h >> 32) & 1) else -1.0
        v[idx] += sign
    nrm = np.linalg.norm(v)
    return v / nrm if nrm > 0 else v


def build_encoder_np(vocab: List[str], dim: int, seed: int) -> np.ndarray:
    """Build [V, N_DIM] L2-normalized encoder matrix."""
    E = np.stack([char_trigram_encode_np(w, dim, seed=seed) for w in vocab], 0).astype(np.float32)
    nrm = np.linalg.norm(E, axis=1, keepdims=True)
    nrm[nrm == 0] = 1.0
    return (E / nrm).astype(np.float32)


def build_position_carriers(k_pos: int, dim: int, seed: int) -> np.ndarray:
    """Build K_POS bipolar HD position carriers; orthogonal in expectation.

    Used by CA3 arms to bind (prev_token, position) -> a position-tagged cue.
    """
    rng = np.random.default_rng(seed + 1009)
    P = (rng.integers(0, 2, size=(k_pos, dim)) * 2 - 1).astype(np.float32)
    nrm = np.linalg.norm(P, axis=1, keepdims=True)
    nrm[nrm == 0] = 1.0
    return P / nrm


def bind_np(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Substrate bind via element-wise product (HRR/bipolar convention).

    For bipolar vectors element-wise product is the standard VSA binding op
    (preserves norm in expectation; invertible by re-binding with same b).
    Mirrors the role of `SequenceMatrix.bind_pair` ordered binding while
    keeping the dim flat (we want a vector, not an N_DIM x N_DIM matrix,
    so we can fold it into the Path A-style W).
    """
    out = a * b
    nrm = np.linalg.norm(out)
    return (out / nrm).astype(np.float32) if nrm > 0 else out.astype(np.float32)


def build_W_path_a(idx_train: np.ndarray, E: np.ndarray, chunk: int) -> np.ndarray:
    """ARM_PATH_A_RAW: standard rank-1 outer-product Hebbian W = sum E[t+1] outer E[t]."""
    dim = E.shape[1]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = idx_train.shape[0] - 1
    for b in range(0, n_pairs, chunk):
        end = min(b + chunk, n_pairs)
        E_src = E[idx_train[b:end]]
        E_tgt = E[idx_train[b + 1:end + 1]]
        W += (E_tgt.T @ E_src).astype(np.float32)
    return W


def build_W_ca3_hetero(idx_train: np.ndarray, E: np.ndarray, P: np.ndarray, chunk: int) -> np.ndarray:
    """ARM_CA3_HETERO_ONLY: W += bind(E[prev], P[pos % K_POS]) outer E[next].

    Cue at predict-time = bind(E[ctx], P[ctx_position_modK]). Position is the
    training-corpus index modulo K_POS so cyclic. Writes shape [N_DIM, N_DIM]
    like Path A but the source side carries position-tag.
    """
    dim = E.shape[1]
    k_pos = P.shape[0]
    W = np.zeros((dim, dim), dtype=np.float32)
    n_pairs = idx_train.shape[0] - 1
    for b in range(0, n_pairs, chunk):
        end = min(b + chunk, n_pairs)
        # positions are [b, b+1, ..., end-1] mod K_POS
        pos_block = np.arange(b, end) % k_pos
        E_src = E[idx_train[b:end]]            # [chunk, dim]
        P_src = P[pos_block]                    # [chunk, dim]
        cue_src = E_src * P_src                 # bind(prev, pos); [chunk, dim]
        cue_nrm = np.linalg.norm(cue_src, axis=1, keepdims=True)
        cue_nrm[cue_nrm == 0] = 1.0
        cue_src = (cue_src / cue_nrm).astype(np.float32)
        E_tgt = E[idx_train[b + 1:end + 1]]
        W += (E_tgt.T @ cue_src).astype(np.float32)
    return W


def softmax_np(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return (e / (e.sum(axis=-1, keepdims=True) + 1e-30)).astype(np.float32)


def bpc_from_logits(logits: np.ndarray, nxt: np.ndarray) -> Tuple[float, float]:
    """BPC via log-linear from softmax(logits) -- task-specified evaluation."""
    probs = softmax_np(logits)
    p_true = np.clip(probs[np.arange(len(nxt)), nxt], 1e-12, 1.0)
    nll = float(-np.mean(np.log(p_true)))
    bpc = nll / math.log(2.0)
    argmax = probs.argmax(axis=1)
    acc = float((argmax == nxt).mean())
    return bpc, acc


# ============================================================================
# Unigram baseline (numpy; trivial)
# ============================================================================

def build_unigram_np(idx_train: np.ndarray, V: int, alpha: float = 0.1) -> np.ndarray:
    counts = np.full(V, alpha, dtype=np.float64)
    np.add.at(counts, idx_train, 1.0)
    return counts / counts.sum()


# ============================================================================
# Corpus
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


# ============================================================================
# Per-seed runner
# ============================================================================

def run_seed(seed: int) -> Dict:
    t_seed = time.time()
    print("\n[seed=%d] loading corpus + vocab" % seed, flush=True)
    toks = load_text8_tokens(N_TRAIN + N_HELD)
    if len(toks) < N_TRAIN + N_HELD:
        print("[FATAL] corpus too small: need %d got %d" % (N_TRAIN + N_HELD, len(toks)), flush=True)
        sys.exit(1)
    train_toks = toks[:N_TRAIN]
    held_toks = toks[N_TRAIN:N_TRAIN + N_HELD]
    vocab, w2i = build_vocab(train_toks, cap=VOCAB_CAP)
    V = len(vocab)
    unk = w2i["<unk>"]
    idx_train = tokens_to_idx(train_toks, w2i)
    idx_held = tokens_to_idx(held_toks, w2i)
    ctx = idx_held[:-1]
    nxt = idx_held[1:]
    mask = (ctx != unk)
    ctx_eval = ctx[mask]
    nxt_eval = nxt[mask]
    held_pos = np.arange(len(idx_held) - 1)[mask] % K_POS  # position for each eval cue
    n_eval = len(ctx_eval)
    print("[seed=%d] V=%d train=%d held=%d eval=%d K_POS=%d" % (
        seed, V, N_TRAIN, N_HELD, n_eval, K_POS), flush=True)

    # Build encoder + position carriers
    t0 = time.time()
    E = build_encoder_np(vocab, N_DIM, seed=seed)
    P = build_position_carriers(K_POS, N_DIM, seed=seed)
    t_enc = time.time() - t0
    print("[seed=%d] encoder + P built (%.1fs)" % (seed, t_enc), flush=True)

    # ARM_UNIGRAM
    U = build_unigram_np(idx_train, V=V, alpha=0.1)
    p_true_uni = U[nxt_eval].clip(1e-12, 1.0)
    uni_bpc = float(-np.mean(np.log(p_true_uni))) / math.log(2.0)
    uni_acc = float((np.full(n_eval, int(np.argmax(U))) == nxt_eval).mean())
    print("[seed=%d] UNIGRAM bpc=%.3f acc=%.4f" % (seed, uni_bpc, uni_acc), flush=True)

    # ARM_PATH_A_RAW
    t0 = time.time()
    W_pa = build_W_path_a(idx_train, E, chunk=INGEST_CHUNK)
    t_pa_ingest = time.time() - t0
    # logits = (E[ctx] @ W.T) @ E.T  (rank-1 Hebbian: prediction is W @ E[ctx],
    # similarity to vocab = (W @ E[ctx])^T E.T = E[ctx]^T W.T E.T)
    cue_pa = E[ctx_eval]                                 # [n_eval, dim]
    pred_pa = cue_pa @ W_pa.T                            # [n_eval, dim]
    pn = np.linalg.norm(pred_pa, axis=1, keepdims=True)
    pn[pn == 0] = 1.0
    pred_pa = (pred_pa / pn).astype(np.float32)
    logits_pa = (pred_pa @ E.T).astype(np.float32)
    pa_bpc, pa_acc = bpc_from_logits(logits_pa, nxt_eval)
    print("[seed=%d] PATH_A_RAW ingest=%.1fs bpc=%.3f acc=%.4f" % (
        seed, t_pa_ingest, pa_bpc, pa_acc), flush=True)
    del W_pa, pred_pa, logits_pa

    # ARM_CA3_HETERO_ONLY
    t0 = time.time()
    W_ca3 = build_W_ca3_hetero(idx_train, E, P, chunk=INGEST_CHUNK)
    t_ca3_ingest = time.time() - t0
    # Eval cue = bind(E[ctx], P[pos])
    P_eval = P[held_pos]                                 # [n_eval, dim]
    cue_h = E[ctx_eval] * P_eval                         # [n_eval, dim]
    cn = np.linalg.norm(cue_h, axis=1, keepdims=True)
    cn[cn == 0] = 1.0
    cue_h = (cue_h / cn).astype(np.float32)
    pred_h = cue_h @ W_ca3.T
    pn = np.linalg.norm(pred_h, axis=1, keepdims=True)
    pn[pn == 0] = 1.0
    pred_h = (pred_h / pn).astype(np.float32)
    logits_h = (pred_h @ E.T).astype(np.float32)
    h_bpc, h_acc = bpc_from_logits(logits_h, nxt_eval)
    print("[seed=%d] CA3_HETERO_ONLY ingest=%.1fs bpc=%.3f acc=%.4f" % (
        seed, t_ca3_ingest, h_bpc, h_acc), flush=True)
    del pred_h, logits_h

    # ARM_CA3_FULL: iterative_attractor cleanup on bound cue BEFORE heteroassoc readout.
    # Codebook for cleanup = the (V, N_DIM) encoder matrix E (rows are stored attractors;
    # L2-normalized; substrate codebook). Iterative cleanup pulls the noisy cue toward
    # nearest basin. Then we re-read via W_ca3 @ cleaned_cue and softmax over E.T.
    t0 = time.time()
    cleanup_out = substrate_iterative_cleanup(
        cue_h, E,
        temp=CLEANUP_TEMP, max_steps=CLEANUP_MAX_STEPS, tol=CLEANUP_TOL,
        return_trace=False, scale_by_sqrt_d=True,
    )
    cue_cleaned = cleanup_out["state"]                   # [n_eval, dim], L2-normalized
    cleanup_iters = int(cleanup_out["n_iterations"])
    cleanup_converged = bool(cleanup_out["converged"])
    t_cleanup = time.time() - t0
    pred_f = cue_cleaned @ W_ca3.T
    pn = np.linalg.norm(pred_f, axis=1, keepdims=True)
    pn[pn == 0] = 1.0
    pred_f = (pred_f / pn).astype(np.float32)
    logits_f = (pred_f @ E.T).astype(np.float32)
    f_bpc, f_acc = bpc_from_logits(logits_f, nxt_eval)
    print("[seed=%d] CA3_FULL cleanup_iters=%d converged=%s (%.1fs) bpc=%.3f acc=%.4f" % (
        seed, cleanup_iters, cleanup_converged, t_cleanup, f_bpc, f_acc), flush=True)
    del W_ca3, pred_f, logits_f, cue_h, cue_cleaned

    return {
        "seed": seed,
        "V": V,
        "N": N_DIM,
        "M": N_TRAIN,
        "N_DIM": N_DIM,
        "N_TRAIN": N_TRAIN,
        "N_HELD": N_HELD,
        "VOCAB_CAP": VOCAB_CAP,
        "K_POS": K_POS,
        "n_eval": int(n_eval),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "unigram_bpc": uni_bpc,
        "unigram_acc": uni_acc,
        "path_a_raw_bpc": pa_bpc,
        "path_a_raw_acc": pa_acc,
        "ca3_hetero_only_bpc": h_bpc,
        "ca3_hetero_only_acc": h_acc,
        "ca3_full_bpc": f_bpc,
        "ca3_full_acc": f_acc,
        "ca3_full_cleanup_iters": cleanup_iters,
        "ca3_full_cleanup_converged": cleanup_converged,
        "wall_pa_ingest_s": float(t_pa_ingest),
        "wall_ca3_ingest_s": float(t_ca3_ingest),
        "wall_cleanup_s": float(t_cleanup),
        "per_unit": [
            {"arm": "ARM_UNIGRAM",          "bpc": uni_bpc, "acc": uni_acc},
            {"arm": "ARM_PATH_A_RAW",       "bpc": pa_bpc,  "acc": pa_acc},
            {"arm": "ARM_CA3_HETERO_ONLY",  "bpc": h_bpc,   "acc": h_acc},
            {"arm": "ARM_CA3_FULL",         "bpc": f_bpc,   "acc": f_acc,
             "cleanup_iters": cleanup_iters, "cleanup_converged": cleanup_converged},
        ],
        "elapsed_s": float(time.time() - t_seed),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


# ============================================================================
# Verdict
# ============================================================================

def compute_verdict(per_seed) -> Tuple[str, str, Dict]:
    if not per_seed:
        return ("HARD_FAIL", "HARD_FAIL: no per-seed data.", {})
    uni = [b["unigram_bpc"] for b in per_seed.values()]
    pa = [b["path_a_raw_bpc"] for b in per_seed.values()]
    h = [b["ca3_hetero_only_bpc"] for b in per_seed.values()]
    f = [b["ca3_full_bpc"] for b in per_seed.values()]

    mean = lambda xs: float(np.mean(xs)) if xs else float("nan")
    std = lambda xs: float(np.std(xs)) if xs else float("nan")
    cv = lambda xs: (std(xs) / max(mean(xs), 1e-9)) if xs else float("inf")

    uni_m, pa_m, h_m, f_m = mean(uni), mean(pa), mean(h), mean(f)
    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    detail = {
        "mean_unigram_bpc": uni_m,
        "mean_path_a_raw_bpc": pa_m,
        "mean_ca3_hetero_only_bpc": h_m,
        "mean_ca3_full_bpc": f_m,
        "cv_unigram": cv(uni),
        "cv_path_a_raw": cv(pa),
        "cv_ca3_hetero_only": cv(h),
        "cv_ca3_full": cv(f),
        "ca3_full_lift_over_unigram_bits": float(uni_m - f_m),
        "ca3_full_lift_over_path_a_raw_bits": float(pa_m - f_m),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "n_llm_calls": int(n_llm),
        "honest_scope": (
            "CA3 composition LM smoke. text8 N_TRAIN=%d N_HELD=%d V=%d N_DIM=%d K_POS=%d. "
            "4 arms (UNIGRAM, PATH_A_RAW, CA3_HETERO_ONLY, CA3_FULL). HARD_PASS when "
            "CA3_FULL beats UNIGRAM (mechanism survives smoke); HARD_FAIL when CA3_FULL >= "
            "PATH_A_RAW (composition does not lift over raw rank-1 Hebbian, mechanism "
            "rejected). Smoke scale; full N_TRAIN=100k queued only if smoke not-HARD_FAIL."
        ) % (N_TRAIN, N_HELD, VOCAB_CAP, N_DIM, K_POS),
    }

    summary = (
        "BPC unigram=%.3f path_a=%.3f ca3_hetero=%.3f ca3_full=%.3f | "
        "lift_full_over_unigram=%+.3f lift_full_over_path_a=%+.3f n_llm=%d (n_seeds=%d N_DIM=%d N_TRAIN=%d)"
        % (uni_m, pa_m, h_m, f_m, uni_m - f_m, pa_m - f_m, n_llm,
           len(per_seed), N_DIM, N_TRAIN)
    )

    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)

    if f_m < uni_m:
        return ("HARD_PASS",
                "HARD_PASS: CA3_FULL BPC %.3f < UNIGRAM BPC %.3f at smoke scale; CA3 composition "
                "mechanism survives. %s" % (f_m, uni_m, summary), detail)
    if f_m >= pa_m:
        return ("HARD_FAIL",
                "HARD_FAIL: CA3_FULL BPC %.3f >= PATH_A_RAW BPC %.3f; CA3 composition does not "
                "lift over raw rank-1 Hebbian; mechanism rejected. %s" % (f_m, pa_m, summary), detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: CA3_FULL BPC %.3f in (UNIGRAM=%.3f, PATH_A_RAW=%.3f] -- partial "
            "characterization; lift over raw but not over unigram. %s" % (f_m, uni_m, pa_m, summary),
            detail)


# ============================================================================
# Self-tests
# ============================================================================

def _selftest():
    # 1. encoder deterministic
    a1 = char_trigram_encode_np("hello", 256, seed=42)
    a2 = char_trigram_encode_np("hello", 256, seed=42)
    assert np.allclose(a1, a2), "selftest 1: encoder not deterministic"
    # 2. encoder L2-normalized
    vocab_t = ["a", "b", "c", "d", "e"]
    E = build_encoder_np(vocab_t, 256, seed=0)
    assert E.shape == (5, 256)
    nrms = np.linalg.norm(E, axis=1)
    assert np.allclose(nrms, 1.0, atol=1e-5), "selftest 2: encoder rows not unit norm"
    # 3. position carriers L2-normalized + correct shape
    P = build_position_carriers(8, 256, seed=0)
    assert P.shape == (8, 256)
    nrms = np.linalg.norm(P, axis=1)
    assert np.allclose(nrms, 1.0, atol=1e-5), "selftest 3: P rows not unit norm"
    # 4. bind preserves shape; bind(a, b) != a, != b on random bipolar
    a = (np.random.default_rng(0).integers(0, 2, 256) * 2 - 1).astype(np.float32)
    b = (np.random.default_rng(1).integers(0, 2, 256) * 2 - 1).astype(np.float32)
    ab = bind_np(a / np.linalg.norm(a), b / np.linalg.norm(b))
    assert ab.shape == (256,)
    assert not np.allclose(ab, a / np.linalg.norm(a), atol=1e-3)
    # 5. Path A trivial-cycle recall (sanity): 10-token cycle should produce high recall
    cycle_vocab = ["tok%d" % i for i in range(10)]
    Ec = build_encoder_np(cycle_vocab, 1024, seed=0)
    seq = np.tile(np.arange(10), 5).astype(np.int64)
    Wc = build_W_path_a(seq, Ec, chunk=8)
    cue = Ec[seq[:-1]]
    pred = cue @ Wc.T
    pn = np.linalg.norm(pred, axis=1, keepdims=True)
    pn[pn == 0] = 1.0
    pred = pred / pn
    logits = pred @ Ec.T
    am = logits.argmax(axis=1)
    acc_pa = float((am == seq[1:]).mean())
    assert acc_pa >= 0.7, "selftest 5: Path A cycle-recall acc=%.3f < 0.7" % acc_pa
    # 6. CA3_HETERO trivial-cycle: same K_POS, same setup. Should also recover.
    Pc = build_position_carriers(4, 1024, seed=0)
    Wch = build_W_ca3_hetero(seq, Ec, Pc, chunk=8)
    pos_cue = np.arange(len(seq) - 1) % 4
    cue_h = Ec[seq[:-1]] * Pc[pos_cue]
    cn = np.linalg.norm(cue_h, axis=1, keepdims=True)
    cn[cn == 0] = 1.0
    cue_h = cue_h / cn
    pred_h = cue_h @ Wch.T
    pn = np.linalg.norm(pred_h, axis=1, keepdims=True)
    pn[pn == 0] = 1.0
    pred_h = pred_h / pn
    logits_h = pred_h @ Ec.T
    am_h = logits_h.argmax(axis=1)
    acc_ca3 = float((am_h == seq[1:]).mean())
    assert acc_ca3 >= 0.7, "selftest 6: CA3_HETERO cycle-recall acc=%.3f < 0.7" % acc_ca3
    # 7. iterative_cleanup invariant: codebook entry recovers itself
    rng = np.random.default_rng(0)
    cb = rng.standard_normal((16, 256)).astype(np.float32)
    cb_n = cb / np.linalg.norm(cb, axis=1, keepdims=True)
    out = substrate_iterative_cleanup(cb_n[5].copy(), cb_n, temp=10.0, max_steps=3)
    assert int(out["argmax_idx"]) == 5, "selftest 7: zero-noise cleanup recovery failed"
    # 8. verdict signature
    fake = {7: {
        "unigram_bpc": 7.74, "path_a_raw_bpc": 11.6,
        "ca3_hetero_only_bpc": 8.0, "ca3_full_bpc": 7.5, "n_llm_calls": 0,
    }}
    v, vmsg, _ = compute_verdict(fake)
    assert v == "HARD_PASS", "selftest 8: verdict signature wrong got %s" % v
    fake2 = {7: {
        "unigram_bpc": 7.74, "path_a_raw_bpc": 11.6,
        "ca3_hetero_only_bpc": 12.0, "ca3_full_bpc": 11.6, "n_llm_calls": 0,
    }}
    v2, _, _ = compute_verdict(fake2)
    assert v2 == "HARD_FAIL", "selftest 8b: HARD_FAIL signature wrong got %s" % v2
    fake3 = {7: {
        "unigram_bpc": 7.74, "path_a_raw_bpc": 11.6,
        "ca3_hetero_only_bpc": 9.0, "ca3_full_bpc": 9.0, "n_llm_calls": 0,
    }}
    v3, _, _ = compute_verdict(fake3)
    assert v3 == "MIDDLE_BAND", "selftest 8c: MIDDLE_BAND signature wrong got %s" % v3
    # 9. substrate-only counter clean
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 9: LLM counter non-zero"
    print("[selftest] PASS: encoder, P, bind, Path A cycle, CA3 cycle, cleanup, verdict, llm=0", flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ----- atexit synthesizer -----
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
            "K_POS": K_POS,
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
            "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
            "detail": detail,
            "per_seed": [
                {"seed": k, **{kk: vv for kk, vv in vv_.items() if kk != "per_unit"},
                 "per_unit": vv_.get("per_unit", [])}
                for k, vv_ in per_seed.items()
            ],
            "metrics_source": "synthesized_from_partials_on_exit",
            "summary": vmsg[:200],
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


# ----- Main runner -----
out_dir = get_output_dir(ANCHOR_NAME)
out_dir.mkdir(parents=True, exist_ok=True)
t0_total = time.time()
run_config = {"N": N_DIM, "M": N_TRAIN, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d N_TRAIN=%d V=%d K_POS=%d seeds_done=%s seeds_todo=%s"
      % (RUN_MODE, N_DIM, N_TRAIN, VOCAB_CAP, K_POS, str(done), str(seeds_todo)), flush=True)

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
    "K_POS": K_POS,
    "INGEST_CHUNK": INGEST_CHUNK,
    "CLEANUP_TEMP": CLEANUP_TEMP,
    "CLEANUP_MAX_STEPS": CLEANUP_MAX_STEPS,
    "CLEANUP_TOL": CLEANUP_TOL,
    "arms": ["ARM_UNIGRAM", "ARM_PATH_A_RAW", "ARM_CA3_HETERO_ONLY", "ARM_CA3_FULL"],
    "run_mode": RUN_MODE,
    "config_version": CONFIG_VERSION,
    "corpus_provenance": "text8 (data/text8_cache/text8.txt)",
    "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
    "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    "detail": detail,
    "per_seed": [
        {"seed": k, **{kk: vv for kk, vv in vv_.items() if kk != "per_unit"},
         "per_unit": vv_.get("per_unit", [])}
        for k, vv_ in per_seed.items()
    ],
    "metrics_source": "measured_ca3_sequence_prediction_lm_smoke_v1",
    "elapsed_s": time.time() - t0_total,
    "summary": vmsg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % v, flush=True)
print("[VERDICT_MSG] %s" % vmsg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
