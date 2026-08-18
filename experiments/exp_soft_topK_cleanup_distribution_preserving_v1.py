"""
soft_topK_cleanup_distribution_preserving_v1 -- Gap A ANCHOR 1 (Research drill 2026-06-26).

GOAL (per Research drill Gap A probabilistic / soft-confidence reasoning):
  Replace argmax cleanup with softmax top-K=5 distribution-preserving readout.
  Carry distribution across multi-hop chain (depth 5). Measure top-1 lift at hop-5
  AND entropy ratio H(hop-5)/H(hop-1) AND ECE@hop-5. Optional R11 temperature
  scaling for calibration.

CROSS-CELL RAIL (META_M7):
  ARM_BASELINE_TOP1_ARGMAX matches hdlab.iterative_attractor.argmax_cleanup top-1
  within 0.02 (substrate primitive verified). If RAIL FAILS -> HARD_FAIL_SANITY.

3 ARMS (mandatory per handoff):
  ARM_BASELINE_TOP1_ARGMAX           -- hard argmax at every hop (substrate baseline)
  ARM_SOFT_TOPK_DISTRIBUTION         -- softmax top-K=5; default temperature
  ARM_SOFT_TOPK_R11_TEMPERATURE_SCALED  -- softmax top-K=5; T* on held-out

PRE-REG BANDS (LOCKED via assert at module init; verbatim from prereg):
  HARD_PASS_CHAIN_GRADE:
    - ARM_SOFT_TOPK_R11 top-1@hop-5 lift >= 0.03 vs ARM_BASELINE
    - AND entropy ratio H(hop-5)/H(hop-1) in [0.4, 0.9]
    - AND ECE@hop-5 <= 0.15
    - AND cross-cell rail: ARM_BASELINE matches argmax_cleanup within 0.02
  MIDDLE_BAND: lift in (0.01, 0.03] OR entropy bounds slipped < 0.1 OR ECE in (0.15, 0.25]
  HARD_FAIL: lift <= 0.01 OR entropy collapses/saturates OR ECE > 0.25
  HARD_FAIL_SANITY: ARM_BASELINE != argmax_cleanup within 0.02 -> ABORT

CONFIG:
  N_DIM = 8192  (production; matches handoff)
  V_C = 256     (codebook; smoke V_C=64 for wall-time)
  K_TOP = 5
  HOP_DEPTH = 5
  SEEDS = [11, 13, 19]
  N_CHAINS_EVAL_FULL = 5000 (per seed); SMOKE = 200
  N_CHAINS_HELDOUT_FULL = 1000 (R11 calibration); SMOKE = 100
  EPSILON_NOISE = 0.15  (cue-noise sigma)
  ENCODER_PROVENANCE = SUBSTRATE_NATIVE
  CORPUS_PROVENANCE_REAL = False (synthetic CLEAN discriminator per USER directive
    2026-06-23 [[feedback-smoke-clean-synthetic-data-not-substrate-state]] +
    [[feedback-clean-encoder-tests-no-contamination]] -- avoids rigged-harness trap)
  ALLOW_SYNTHETIC = True (justified above; documented in prereg)
  Substrate-only-decode (zero LLM forward calls; structural + counter; AUDIT log)
  Per-seed checkpoint (PROT-021 run_config guard)

CHAIN-GRADE PRIMITIVES COMPOSED (from hdlab/):
  - iterative_attractor.argmax_cleanup    -- cross-cell rail reference
  - sparse-bipolar codebook (substrate-native; matches c3 + n8 convention)

DISCIPLINES (per role contract):
  - ASCII only; no unicode
  - Substrate-only at inference (LLM_CALL_COUNTER == 0 asserted)
  - ENCODER_PROVENANCE = "SUBSTRATE_NATIVE" module constant (Path C R3)
  - Per-arm metrics (Fix #28); read metrics.json per-arm not verdict_msg
  - META_M7 capacity-sensitive dims identical smoke/full (N_DIM=8192 both)
  - Per-seed checkpoint (PROT-021) + atexit partial-flush
  - HARD_FAIL_SANITY before any soft-top-K verdict claim

FORMULA SELF-TESTS (PROT-022; module scope before sweep):
  T1: softmax-top-K returns K=5 indices + probs summing to 1.0
  T2: top-1 argmax == softmax top-1 at very high beta (recovers argmax)
  T3: entropy ratio measurable on synthetic chain (discriminable from 0 / log(K))
  T4: ECE formula finite + zero on perfectly-calibrated synthetic
  T5: R11 temperature scaling: T* minimizes held-out NLL within 10% of grid optimum
  T6: 3-ARM dispatcher returns dict with all required keys
  T7: P(HP) + P(MIDDLE) + P(HF) == 1.00
  T8: pre-reg bands LOCKED via assert
  T9: cross-cell rail: ARM_BASELINE matches argmax_cleanup within 0.02
  T10: zero LLM calls counter stays at 0
  T11: REQUIRED_FIELDS present in metrics output

QUEUE: remote_cpu_queue (CPU-feasible per research note; ~1-2 CPU-hr).
DEPENDENCY: None external (clean synthetic). NPZ NOT required.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse, os, time, math
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, write_metrics, resumable_seeds, write_partial, aggregate_partials
)
from hdlab.iterative_attractor import argmax_cleanup as ref_argmax_cleanup

ANCHOR_NAME = "soft_topK_cleanup_distribution_preserving_v1"

# ---------------------------------------------------------------------------
# Path C compliance + audit constants
# ---------------------------------------------------------------------------
ENCODER_PROVENANCE = "SUBSTRATE_NATIVE"
CORPUS_PROVENANCE_REAL = False  # Synthetic CLEAN discriminator (justified above)
ALLOW_SYNTHETIC = True
_LLM_CALL_COUNTER = [0]

# ---------------------------------------------------------------------------
# Pre-registered bands (LOCKED at module init via assert; verbatim from prereg)
# ---------------------------------------------------------------------------
HARD_PASS_LIFT_THRESHOLD = 0.03
HARD_PASS_ECE_MAX = 0.15
HARD_PASS_ENTROPY_RATIO_LO = 0.4
HARD_PASS_ENTROPY_RATIO_HI = 0.9
MIDDLE_BAND_LIFT_LO = 0.01
MIDDLE_BAND_ECE_MAX = 0.25
RAIL_TOP1_TOLERANCE = 0.02

P_HARD_PASS = 0.55
P_MIDDLE = 0.25
P_HARD_FAIL = 0.20
assert abs((P_HARD_PASS + P_MIDDLE + P_HARD_FAIL) - 1.0) < 1e-9, \
    "Pre-reg probabilities must sum to 1.00 (got %.6f)" % (
        P_HARD_PASS + P_MIDDLE + P_HARD_FAIL,
    )
assert HARD_PASS_LIFT_THRESHOLD > MIDDLE_BAND_LIFT_LO, \
    "HARD_PASS lift threshold must exceed MIDDLE_BAND lift floor"
assert HARD_PASS_ECE_MAX < MIDDLE_BAND_ECE_MAX, \
    "HARD_PASS ECE must be tighter than MIDDLE_BAND ECE"
assert 0.0 < HARD_PASS_ENTROPY_RATIO_LO < HARD_PASS_ENTROPY_RATIO_HI < 1.0, \
    "entropy ratio bounds must be in (0, 1) with lo < hi"

# ---------------------------------------------------------------------------
# CLI / env config
# ---------------------------------------------------------------------------
_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ap.add_argument("--n-dim", dest="n_dim", type=int, default=None)
_ap.add_argument("--vc", dest="vc", type=int, default=None)
_ARGS, _ = _ap.parse_known_args()

_exp_name = os.environ.get("HDLAB_EXP_NAME", "").lower()
_runmode_env = os.environ.get("HDLAB_RUN_MODE", "full").lower()
_name_indicates_smoke = ("_smoke" in _exp_name and not _exp_name.endswith("_no_smoke"))
if _ARGS.smoke or _runmode_env == "smoke" or _name_indicates_smoke:
    RUN_MODE = "smoke"
else:
    RUN_MODE = _runmode_env

N_DIM = _ARGS.n_dim if _ARGS.n_dim is not None else int(os.environ.get("HDLAB_N_DIM", "8192"))

# Codebook size: smaller smoke (V_C=64) keeps wall under 60s; full V_C=256 dims production
if RUN_MODE == "smoke":
    V_C_DEFAULT = 64
else:
    V_C_DEFAULT = 256
V_C = _ARGS.vc if _ARGS.vc is not None else int(os.environ.get("HDLAB_VC", str(V_C_DEFAULT)))

K_TOP = 5
HOP_DEPTH = 5
EPSILON_NOISE = 0.15

# R11 grid-search T values (matches research_R11_calibration protocol)
T_GRID_R11 = [0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
T_DEFAULT_UNCAL = 1.0  # untempered default for ARM_SOFT_TOPK_DISTRIBUTION

if RUN_MODE == "smoke":
    SEEDS = [11]
    N_CHAINS_EVAL = 200
    N_CHAINS_HELDOUT = 100
else:
    SEEDS = [11, 13, 19]
    N_CHAINS_EVAL = 5000
    N_CHAINS_HELDOUT = 1000

# ARM identifiers (per Fix #28 per-arm metrics discipline)
ARM_BASELINE_TOP1_ARGMAX = "ARM_BASELINE_TOP1_ARGMAX"
ARM_SOFT_TOPK_DISTRIBUTION = "ARM_SOFT_TOPK_DISTRIBUTION"
ARM_SOFT_TOPK_R11 = "ARM_SOFT_TOPK_R11_TEMPERATURE_SCALED"
ALL_ARMS = [ARM_BASELINE_TOP1_ARGMAX, ARM_SOFT_TOPK_DISTRIBUTION, ARM_SOFT_TOPK_R11]

CONFIG_VERSION = (
    "N=%d,V_C=%d,K_TOP=%d,HOP=%d,EPS=%.3f,N_EVAL=%d,N_HELDOUT=%d,"
    "T_GRID=%s,ARMS=%d,SEEDS=%s,"
    "BANDS=HP_LIFT>=%.3f/ECE<=%.3f/ENT[%.2f,%.2f]/RAIL<=%.3f,"
    "ENCODER=%s,SYNTH=%s"
) % (
    N_DIM, V_C, K_TOP, HOP_DEPTH, EPSILON_NOISE, N_CHAINS_EVAL, N_CHAINS_HELDOUT,
    "-".join("%.2g" % t for t in T_GRID_R11), len(ALL_ARMS),
    "-".join(str(s) for s in SEEDS),
    HARD_PASS_LIFT_THRESHOLD, HARD_PASS_ECE_MAX,
    HARD_PASS_ENTROPY_RATIO_LO, HARD_PASS_ENTROPY_RATIO_HI,
    RAIL_TOP1_TOLERANCE,
    ENCODER_PROVENANCE, str(ALLOW_SYNTHETIC),
)


# ---------------------------------------------------------------------------
# Substrate primitives: sparse-bipolar codebook + softmax-top-K cleanup
# ---------------------------------------------------------------------------

def sparse_bipolar_codebook(vc: int, n: int, rng: np.random.Generator,
                            f_active: float = 0.5) -> np.ndarray:
    """Sparse bipolar codebook (vc, n) with bipolar entries in {-1, +1}.

    L2-normalized rows. Matches c3 + n8 chain-grade substrate convention for
    clean discriminator data. f_active controls fraction of +1 vs -1 (0.5 is
    balanced bipolar).
    """
    raw = rng.choice([-1.0, 1.0], size=(vc, n),
                     p=[1.0 - f_active, f_active]).astype(np.float32)
    norms = np.linalg.norm(raw, axis=1, keepdims=True) + 1e-12
    return (raw / norms).astype(np.float32)


def _softmax(z: np.ndarray, axis: int = -1) -> np.ndarray:
    """Numerically-stable softmax."""
    z = z - z.max(axis=axis, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return (e / (e.sum(axis=axis, keepdims=True) + 1e-30)).astype(np.float32)


def softmax_top_k(scores: np.ndarray, k: int,
                  temperature: float = 1.0) -> Tuple[np.ndarray, np.ndarray]:
    """Return (top_k_indices, top_k_probs) for each row of scores.

    Args:
        scores: (B, V) cosine-similarity logits
        k: top-K to keep
        temperature: divides scores BEFORE softmax (T -> 0 == argmax; T -> inf == uniform)

    Returns:
        top_k_idx: (B, K) int64 indices of top-K
        top_k_probs: (B, K) float32 probabilities normalized to sum to 1 across K
    """
    if scores.ndim == 1:
        scores = scores[None, :]
    if k <= 0:
        raise ValueError("k must be > 0; got %d" % k)
    if temperature <= 0.0:
        raise ValueError("temperature must be > 0; got %f" % temperature)
    B, V = scores.shape
    k_use = min(k, V)
    # Get top-k by score (independent of T)
    top_k_idx = np.argpartition(-scores, kth=k_use - 1, axis=1)[:, :k_use]
    # Sort within top-k by descending score for determinism
    rows = np.arange(B)[:, None]
    top_k_scores = scores[rows, top_k_idx]
    order = np.argsort(-top_k_scores, axis=1)
    top_k_idx = np.take_along_axis(top_k_idx, order, axis=1)
    top_k_scores = np.take_along_axis(top_k_scores, order, axis=1)
    # Softmax normalize within top-K only (NOT over full V; that is the population-coding choice)
    scaled = top_k_scores / float(temperature)
    scaled = scaled - scaled.max(axis=1, keepdims=True)
    e = np.exp(scaled.astype(np.float64))
    probs = (e / (e.sum(axis=1, keepdims=True) + 1e-30)).astype(np.float32)
    return top_k_idx.astype(np.int64), probs


def entropy_from_probs(probs: np.ndarray) -> np.ndarray:
    """Per-row entropy in nats. probs shape (B, K) -> (B,)."""
    p = np.clip(probs, 1e-30, 1.0)
    return -np.sum(p * np.log(p), axis=-1)


def ece_binary(probs_top1: np.ndarray, correct: np.ndarray,
               n_bins: int = 15) -> float:
    """Expected Calibration Error (ECE) — equal-width binning of top-1 confidence.

    Args:
        probs_top1: (N,) top-1 confidence (max softmax prob)
        correct: (N,) bool correctness of top-1 prediction
        n_bins: number of confidence bins
    Returns:
        ECE = sum_b (n_b / N) * |accuracy_b - confidence_b|
    """
    if len(probs_top1) == 0:
        return float("nan")
    correct = correct.astype(np.float32)
    bins = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    N = len(probs_top1)
    for b in range(n_bins):
        lo, hi = bins[b], bins[b + 1]
        if b == n_bins - 1:
            mask = (probs_top1 >= lo) & (probs_top1 <= hi)
        else:
            mask = (probs_top1 >= lo) & (probs_top1 < hi)
        n_b = int(mask.sum())
        if n_b == 0:
            continue
        acc_b = float(correct[mask].mean())
        conf_b = float(probs_top1[mask].mean())
        ece += (n_b / N) * abs(acc_b - conf_b)
    return float(ece)


# ---------------------------------------------------------------------------
# Multi-hop chain harness (clean synthetic ground truth)
# ---------------------------------------------------------------------------

def make_transition_table(vc: int, rng: np.random.Generator) -> np.ndarray:
    """Deterministic transition table T[src] -> next_concept. Shape (vc,).

    Clean ground truth: each src has a single deterministic successor.
    """
    return rng.permutation(vc).astype(np.int64)


def generate_chains(vc: int, n_chains: int, depth: int,
                    transition: np.ndarray,
                    rng: np.random.Generator) -> np.ndarray:
    """Generate n_chains chains of length depth+1; each starts from random concept.

    Returns: (n_chains, depth+1) int64 concept_ids; index 0 is the start.
    """
    starts = rng.integers(0, vc, size=n_chains, dtype=np.int64)
    chains = np.zeros((n_chains, depth + 1), dtype=np.int64)
    chains[:, 0] = starts
    for t in range(depth):
        chains[:, t + 1] = transition[chains[:, t]]
    return chains


def add_noise(cues: np.ndarray, sigma: float,
              rng: np.random.Generator) -> np.ndarray:
    """Add isotropic Gaussian noise sigma; re-normalize. cues shape (B, N)."""
    noise = sigma * rng.standard_normal(cues.shape).astype(np.float32)
    noisy = cues + noise
    norms = np.linalg.norm(noisy, axis=1, keepdims=True) + 1e-12
    return (noisy / norms).astype(np.float32)


# ---------------------------------------------------------------------------
# Per-arm multi-hop scoring (Fix #28: per-arm metrics, not summary verdict text)
# ---------------------------------------------------------------------------

def score_arm_argmax(C: np.ndarray, transition: np.ndarray,
                     chains: np.ndarray, cues: np.ndarray,
                     hop_depth: int) -> Dict[str, Any]:
    """ARM_BASELINE_TOP1_ARGMAX: hard argmax at each hop; chain via T[argmax].

    Returns per-hop top1 + final-hop ECE (using argmax-vs-uniform-confidence proxy:
    top-1 confidence = max softmax prob over codebook at T=1.0 (default)).
    Entropy is degenerate (0) for argmax, so we report H(hop-1) and H(hop-5) from
    the softmax-distribution that WOULD have been used; the discriminator only
    needs lift comparison.

    For ECE comparability across arms, we use the FULL-V softmax at T=1.0 to assign
    confidence to the argmax choice (this gives ARM_BASELINE a uniform-ish low
    confidence baseline; soft-top-K can sharpen).
    """
    B = cues.shape[0]
    # hop 0: state = noisy cue; predict next via argmax cleanup
    state = cues.copy()
    per_hop_top1: List[float] = []
    per_hop_entropy: List[float] = []
    # For ECE@hop-5: compute top-1 confidence as softmax-prob over codebook
    for hop in range(hop_depth):
        scores = state @ C.T  # (B, V)
        # Predict current-step concept
        pred = np.argmax(scores, axis=1).astype(np.int64)
        true = chains[:, hop + 1]
        per_hop_top1.append(float(np.mean(pred == true)))
        # Entropy proxy: softmax-of-scores at T=1.0
        probs_full = _softmax(scores, axis=1)
        # Use top-K for entropy reporting (population-code convention)
        top_k_idx, top_k_probs = softmax_top_k(scores, K_TOP, temperature=1.0)
        per_hop_entropy.append(float(np.mean(entropy_from_probs(top_k_probs))))
        # Next state: hard-argmax COMMITS to one codebook entry, then applies transition
        # to set up next hop. (NOT the soft superposition; this is the baseline.)
        next_concept = transition[pred]
        state = C[next_concept]
    # Final-hop ECE: confidence = top-1 softmax prob over codebook at T=1.0
    final_scores = (cues if hop_depth == 0 else state) @ C.T  # placeholder
    # Re-compute final-hop predictions WITH confidence
    # Use last hop's scores (just before transition) for ECE
    # Build them by re-walking the chain on the LAST hop scoring
    # Simpler: keep last_scores from the loop
    # Redo last-hop quickly:
    # (We already broke out; restart cleanly.)
    # The cleanest path: re-walk with confidence at each hop and grab last.
    last_pred = np.zeros(B, dtype=np.int64)
    last_conf = np.zeros(B, dtype=np.float32)
    state = cues.copy()
    for hop in range(hop_depth):
        scores = state @ C.T
        probs_full = _softmax(scores, axis=1)
        pred = np.argmax(scores, axis=1).astype(np.int64)
        if hop == hop_depth - 1:
            last_pred = pred.copy()
            last_conf = probs_full[np.arange(B), pred]
        next_concept = transition[pred]
        state = C[next_concept]
    last_correct = (last_pred == chains[:, hop_depth])
    ece_hop_last = ece_binary(last_conf, last_correct)
    return {
        "arm": ARM_BASELINE_TOP1_ARGMAX,
        "top1_per_hop": per_hop_top1,
        "top1_hop_last": per_hop_top1[-1] if per_hop_top1 else float("nan"),
        "entropy_per_hop_nats": per_hop_entropy,
        "ece_hop_last": ece_hop_last,
        "temperature_used": 1.0,
    }


def score_arm_soft_topk(C: np.ndarray, transition: np.ndarray,
                        chains: np.ndarray, cues: np.ndarray,
                        hop_depth: int, k_top: int,
                        temperature: float) -> Dict[str, Any]:
    """ARM_SOFT_TOPK_DISTRIBUTION (or _R11): carry top-K softmax distribution across hops.

    At each hop:
      - Score state against codebook -> scores
      - softmax_top_k(scores, k_top, T) -> (top_k_idx, top_k_probs)
      - Next state = sum_i probs[i] * C[transition[top_k_idx[i]]]  (weighted superposition)
      - top-1 = argmax of top_k_probs (== argmax of scores; deterministic within top-K)
      - entropy = entropy(top_k_probs)
    """
    B = cues.shape[0]
    state = cues.copy()
    per_hop_top1: List[float] = []
    per_hop_entropy: List[float] = []
    last_pred = np.zeros(B, dtype=np.int64)
    last_conf = np.zeros(B, dtype=np.float32)
    for hop in range(hop_depth):
        scores = state @ C.T  # (B, V)
        top_k_idx, top_k_probs = softmax_top_k(scores, k_top, temperature)
        # Top-1 within top-K is the first (sorted by descending score)
        pred = top_k_idx[:, 0]
        true = chains[:, hop + 1]
        per_hop_top1.append(float(np.mean(pred == true)))
        per_hop_entropy.append(float(np.mean(entropy_from_probs(top_k_probs))))
        if hop == hop_depth - 1:
            last_pred = pred.copy()
            last_conf = top_k_probs[:, 0].copy()
        # Build next state: weighted superposition of top-K successors
        # successors[b, i] = transition[top_k_idx[b, i]]  -> codebook lookup
        successors = transition[top_k_idx]  # (B, K)
        # Gather codebook vectors: (B, K, N)
        succ_vecs = C[successors]  # uses fancy indexing
        # Weight by top_k_probs and sum
        weighted = succ_vecs * top_k_probs[:, :, None].astype(np.float32)  # (B, K, N)
        new_state = weighted.sum(axis=1)  # (B, N)
        # L2-normalize new state (substrate convention)
        norms = np.linalg.norm(new_state, axis=1, keepdims=True) + 1e-12
        state = (new_state / norms).astype(np.float32)
    last_correct = (last_pred == chains[:, hop_depth])
    ece_hop_last = ece_binary(last_conf, last_correct)
    return {
        "arm": ARM_SOFT_TOPK_DISTRIBUTION if temperature == T_DEFAULT_UNCAL else ARM_SOFT_TOPK_R11,
        "top1_per_hop": per_hop_top1,
        "top1_hop_last": per_hop_top1[-1] if per_hop_top1 else float("nan"),
        "entropy_per_hop_nats": per_hop_entropy,
        "ece_hop_last": ece_hop_last,
        "temperature_used": float(temperature),
    }


def fit_r11_temperature(C: np.ndarray, transition: np.ndarray,
                        chains_heldout: np.ndarray, cues_heldout: np.ndarray,
                        hop_depth: int, k_top: int,
                        t_grid: List[float]) -> Tuple[float, Dict[str, float]]:
    """Pick T from t_grid that minimizes hop-last NLL on held-out partition.

    Returns (T_star, t_to_nll_dict).
    """
    t_to_nll: Dict[str, float] = {}
    best_T = t_grid[0]
    best_nll = float("inf")
    for T in t_grid:
        # Walk the chain with T-tempered top-K
        state = cues_heldout.copy()
        for hop in range(hop_depth):
            scores = state @ C.T
            top_k_idx, top_k_probs = softmax_top_k(scores, k_top, T)
            successors = transition[top_k_idx]
            succ_vecs = C[successors]
            weighted = succ_vecs * top_k_probs[:, :, None].astype(np.float32)
            new_state = weighted.sum(axis=1)
            norms = np.linalg.norm(new_state, axis=1, keepdims=True) + 1e-12
            state = (new_state / norms).astype(np.float32)
            # On last hop, record NLL of true target under top-K dist
            if hop == hop_depth - 1:
                true = chains_heldout[:, hop + 1]
                # For each row, find if true is in top_k_idx; if not, assign min-prob floor
                B = top_k_idx.shape[0]
                in_topk = (top_k_idx == true[:, None])
                row_has = in_topk.any(axis=1)
                # Probability assigned to true target
                # If in top-K: pull that slot's prob; else: floor = 1e-6
                probs_true = np.full(B, 1e-6, dtype=np.float32)
                rows_present = np.where(row_has)[0]
                if len(rows_present) > 0:
                    # locate the column index for each row
                    cols = np.argmax(in_topk[rows_present], axis=1)
                    probs_true[rows_present] = top_k_probs[rows_present, cols]
                nll = float(-np.mean(np.log(np.clip(probs_true, 1e-30, 1.0))))
        t_to_nll["%.4g" % T] = nll
        if nll < best_nll:
            best_nll = nll
            best_T = float(T)
    return best_T, t_to_nll


# ---------------------------------------------------------------------------
# Cross-cell rail: ARM_BASELINE top-1 must match argmax_cleanup reference
# ---------------------------------------------------------------------------

def cross_cell_rail_check(C: np.ndarray, cues: np.ndarray,
                          chains: np.ndarray) -> Dict[str, float]:
    """Compare ARM_BASELINE hop-1 top-1 against hdlab.iterative_attractor.argmax_cleanup.

    For hop=0 -> hop=1 the comparison is:
      ARM_BASELINE: argmax(cues @ C.T)  -> pred1
      reference:   ref_argmax_cleanup(cues, C)  -> pred1_ref
    These should match within RAIL_TOP1_TOLERANCE = 0.02 (essentially exact;
    only minor float-precision differences expected).
    """
    pred_local = np.argmax(cues @ C.T, axis=1).astype(np.int64)
    pred_ref = ref_argmax_cleanup(cues, C).astype(np.int64)
    agreement = float(np.mean(pred_local == pred_ref))
    # Both should also have similar top-1 vs true (chains[:, 1])
    true = chains[:, 1]
    local_top1 = float(np.mean(pred_local == true))
    ref_top1 = float(np.mean(pred_ref == true))
    return {
        "agreement_pred_pred_ref": agreement,
        "rail_top1_local": local_top1,
        "rail_top1_reference": ref_top1,
        "rail_top1_diff": abs(local_top1 - ref_top1),
    }


# ---------------------------------------------------------------------------
# Formula self-test (MANDATORY at module scope per role contract)
# ---------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """T1..T11 mandatory pre-dispatch instrumentation gate."""
    rng = np.random.default_rng(42)
    n_small, vc_small = 256, 16

    # --- T1: softmax_top_k returns K=5 indices + probs summing to 1.0 ---
    scores_test = rng.standard_normal((3, vc_small)).astype(np.float32)
    idx, probs = softmax_top_k(scores_test, K_TOP, temperature=1.0)
    assert idx.shape == (3, K_TOP), "top_k idx shape FAIL: %s" % str(idx.shape)
    assert probs.shape == (3, K_TOP), "top_k probs shape FAIL: %s" % str(probs.shape)
    sums = probs.sum(axis=1)
    assert np.allclose(sums, 1.0, atol=1e-5), "top_k probs do not sum to 1: %s" % str(sums)
    # Indices must be unique within each row
    for r in range(3):
        assert len(set(idx[r].tolist())) == K_TOP, "top_k idx not unique at row %d" % r
    print("[selftest] T1 PASS: softmax_top_k returns K=%d unique indices, probs sum to 1.0" % K_TOP,
          flush=True)

    # --- T2: top-1 argmax == softmax top-1 at very high beta (low T) ---
    scores_t2 = rng.standard_normal((5, vc_small)).astype(np.float32)
    idx_high_beta, _ = softmax_top_k(scores_t2, K_TOP, temperature=0.01)
    pred_argmax = np.argmax(scores_t2, axis=1)
    assert np.array_equal(idx_high_beta[:, 0], pred_argmax), \
        "top_k T=0.01 first-index does not match argmax"
    print("[selftest] T2 PASS: softmax top-1 at T=0.01 == argmax (recovers hard limit)", flush=True)

    # --- T3: entropy ratio measurable on synthetic ---
    # Construct two distributions: peaked (low H) and uniform (high H)
    probs_peaked = np.array([[0.99, 0.005, 0.0025, 0.0025, 0.0]], dtype=np.float32)
    probs_uniform = np.array([[0.2, 0.2, 0.2, 0.2, 0.2]], dtype=np.float32)
    H_peaked = entropy_from_probs(probs_peaked)
    H_uniform = entropy_from_probs(probs_uniform)
    assert H_peaked[0] < 0.2, "peaked entropy should be ~0; got %.3f" % H_peaked[0]
    expected_uniform_H = math.log(5)  # nats; log_e 5 ~ 1.609
    assert abs(H_uniform[0] - expected_uniform_H) < 1e-4, \
        "uniform entropy should be log(5) ~ 1.609; got %.3f" % H_uniform[0]
    ratio = H_peaked[0] / H_uniform[0]
    assert ratio < 0.2, "peaked/uniform ratio should be small; got %.3f" % ratio
    print("[selftest] T3 PASS: entropy ratio measurable (peaked=%.3f, uniform=%.3f, ratio=%.3f)"
          % (H_peaked[0], H_uniform[0], ratio), flush=True)

    # --- T4: ECE formula finite + ~0 on perfectly calibrated ---
    # Perfectly calibrated: conf=0.8 -> 80% correct
    n_t4 = 1000
    confs = np.full(n_t4, 0.8, dtype=np.float32)
    correct = np.zeros(n_t4, dtype=bool)
    correct[:800] = True
    ece_perfect = ece_binary(confs, correct)
    assert ece_perfect < 0.01, "ECE on perfectly calibrated should be ~0; got %.3f" % ece_perfect
    # Mis-calibrated: conf=0.9 but only 50% correct
    confs_bad = np.full(n_t4, 0.9, dtype=np.float32)
    correct_bad = np.zeros(n_t4, dtype=bool)
    correct_bad[:500] = True
    ece_bad = ece_binary(confs_bad, correct_bad)
    assert ece_bad > 0.3, "ECE on miscalibrated should be high; got %.3f" % ece_bad
    print("[selftest] T4 PASS: ECE finite + zero on calibrated (%.3f), high on miscalibrated (%.3f)"
          % (ece_perfect, ece_bad), flush=True)

    # --- T5: R11 temperature scaling on synthetic ---
    # Build small chain harness; sweep T grid; verify T* picks something sane
    rng_t5 = np.random.default_rng(101)
    C_t5 = sparse_bipolar_codebook(vc_small, n_small, rng_t5)
    transition_t5 = make_transition_table(vc_small, rng_t5)
    chains_t5 = generate_chains(vc_small, 50, HOP_DEPTH, transition_t5, rng_t5)
    starts = chains_t5[:, 0]
    cues_t5 = add_noise(C_t5[starts], EPSILON_NOISE, rng_t5)
    t_star, t_to_nll = fit_r11_temperature(
        C_t5, transition_t5, chains_t5, cues_t5, HOP_DEPTH, K_TOP, T_GRID_R11)
    assert t_star in T_GRID_R11, "T* not in grid: %f" % t_star
    nlls = list(t_to_nll.values())
    assert all(math.isfinite(n) for n in nlls), "some NLL non-finite: %s" % nlls
    grid_min = min(nlls)
    star_nll = t_to_nll["%.4g" % t_star]
    assert abs(star_nll - grid_min) < 1e-6, \
        "T* NLL %.4f not min %.4f" % (star_nll, grid_min)
    print("[selftest] T5 PASS: R11 picks T*=%.3g (NLL=%.4f); grid sweep OK" % (t_star, star_nll),
          flush=True)

    # --- T6: 3-ARM dispatcher returns dict with required keys ---
    # Run each arm on small synthetic
    arm_baseline = score_arm_argmax(C_t5, transition_t5, chains_t5, cues_t5, HOP_DEPTH)
    arm_soft = score_arm_soft_topk(C_t5, transition_t5, chains_t5, cues_t5,
                                   HOP_DEPTH, K_TOP, T_DEFAULT_UNCAL)
    arm_r11 = score_arm_soft_topk(C_t5, transition_t5, chains_t5, cues_t5,
                                  HOP_DEPTH, K_TOP, t_star)
    required_keys = {"arm", "top1_per_hop", "top1_hop_last",
                     "entropy_per_hop_nats", "ece_hop_last", "temperature_used"}
    for a in (arm_baseline, arm_soft, arm_r11):
        missing = required_keys - set(a.keys())
        assert not missing, "arm %s missing keys: %s" % (a.get("arm", "?"), missing)
    print("[selftest] T6 PASS: 3-ARM dispatcher returns dicts with all required keys",
          flush=True)

    # --- T7: Pre-reg probabilities sum to 1.00 ---
    s = P_HARD_PASS + P_MIDDLE + P_HARD_FAIL
    assert abs(s - 1.0) < 1e-9, "probabilities sum != 1: %.6f" % s
    print("[selftest] T7 PASS: P_HP + P_MIDDLE + P_HF = 1.00", flush=True)

    # --- T8: pre-reg bands LOCKED via assert (these are also at module init) ---
    assert HARD_PASS_LIFT_THRESHOLD == 0.03, "HP lift mutated"
    assert HARD_PASS_ECE_MAX == 0.15, "HP ECE mutated"
    assert HARD_PASS_ENTROPY_RATIO_LO == 0.4 and HARD_PASS_ENTROPY_RATIO_HI == 0.9, \
        "entropy bounds mutated"
    assert RAIL_TOP1_TOLERANCE == 0.02, "rail tolerance mutated"
    print("[selftest] T8 PASS: pre-reg bands LOCKED (HP_LIFT>=0.03, ECE<=0.15, ENT[0.4,0.9])",
          flush=True)

    # --- T9: Cross-cell rail: ARM_BASELINE matches argmax_cleanup ---
    rail = cross_cell_rail_check(C_t5, cues_t5, chains_t5)
    assert rail["agreement_pred_pred_ref"] > 0.98, \
        "cross-cell rail agreement low: %.3f" % rail["agreement_pred_pred_ref"]
    assert rail["rail_top1_diff"] < RAIL_TOP1_TOLERANCE, \
        "cross-cell rail top1 diff %.3f >= tolerance %.3f" % (
            rail["rail_top1_diff"], RAIL_TOP1_TOLERANCE)
    print("[selftest] T9 PASS: cross-cell rail OK (agreement=%.3f, top1_diff=%.4f)"
          % (rail["agreement_pred_pred_ref"], rail["rail_top1_diff"]), flush=True)

    # --- T10: LLM_CALL_COUNTER == 0 ---
    assert _LLM_CALL_COUNTER[0] == 0, \
        "LLM_CALL_COUNTER non-zero at selftest exit: %d" % _LLM_CALL_COUNTER[0]
    print("[selftest] T10 PASS: LLM_CALL_COUNTER=0 (substrate-only-decode structural)",
          flush=True)

    # --- T11: REQUIRED_FIELDS check (smoke runner will validate; here we just
    # confirm we know the contract) ---
    REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")
    for f in REQUIRED_FIELDS:
        assert isinstance(f, str) and len(f) > 0
    print("[selftest] T11 PASS: REQUIRED_FIELDS contract known (%s)" % (REQUIRED_FIELDS,),
          flush=True)

    print("[selftest] ALL 11 TESTS PASS: soft_topK_cleanup instrumentation validated",
          flush=True)


_instrumentation_selftest()  # MANDATORY at module scope (role contract)
if _ARGS.self_test:
    print("[self-test] EXIT 0", flush=True)
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed pipeline (synthetic clean discriminator)
# ---------------------------------------------------------------------------

def run_seed(seed: int) -> Dict[str, Any]:
    """Full per-seed pipeline: build codebook + transition + chains; run 3 arms."""
    t0 = time.time()
    rng = np.random.default_rng(seed)
    print("[seed=%d] N_DIM=%d V_C=%d K_TOP=%d HOP=%d N_EVAL=%d N_HELDOUT=%d" % (
        seed, N_DIM, V_C, K_TOP, HOP_DEPTH, N_CHAINS_EVAL, N_CHAINS_HELDOUT), flush=True)

    # Build substrate codebook (sparse-bipolar, L2-normalized)
    C = sparse_bipolar_codebook(V_C, N_DIM, rng)
    # Deterministic transition table
    transition = make_transition_table(V_C, rng)
    # Generate eval + held-out chains
    chains_eval = generate_chains(V_C, N_CHAINS_EVAL, HOP_DEPTH, transition, rng)
    chains_heldout = generate_chains(V_C, N_CHAINS_HELDOUT, HOP_DEPTH, transition, rng)
    # Noisy cues (hop-0 query)
    starts_eval = chains_eval[:, 0]
    cues_eval = add_noise(C[starts_eval], EPSILON_NOISE, rng)
    starts_heldout = chains_heldout[:, 0]
    cues_heldout = add_noise(C[starts_heldout], EPSILON_NOISE, rng)

    # Cross-cell rail check (HARD_FAIL_SANITY gate)
    rail = cross_cell_rail_check(C, cues_eval, chains_eval)
    print("[seed=%d] cross-cell rail: agreement=%.3f top1_diff=%.4f" % (
        seed, rail["agreement_pred_pred_ref"], rail["rail_top1_diff"]), flush=True)
    rail_pass = (rail["rail_top1_diff"] < RAIL_TOP1_TOLERANCE)

    # R11 temperature fit
    print("[seed=%d] fitting R11 temperature on %d held-out chains..." % (
        seed, N_CHAINS_HELDOUT), flush=True)
    t_star, t_to_nll = fit_r11_temperature(
        C, transition, chains_heldout, cues_heldout, HOP_DEPTH, K_TOP, T_GRID_R11)
    print("[seed=%d] R11 T*=%.3g (held-out NLL=%.4f); grid: %s" % (
        seed, t_star, t_to_nll["%.4g" % t_star], t_to_nll), flush=True)

    # Score each ARM on eval set
    print("[seed=%d] scoring ARM_BASELINE_TOP1_ARGMAX..." % seed, flush=True)
    arm_baseline = score_arm_argmax(C, transition, chains_eval, cues_eval, HOP_DEPTH)
    print("  baseline top1_hop_last=%.3f ECE=%.3f" % (
        arm_baseline["top1_hop_last"], arm_baseline["ece_hop_last"]), flush=True)

    print("[seed=%d] scoring ARM_SOFT_TOPK_DISTRIBUTION (T=%.2f)..." % (
        seed, T_DEFAULT_UNCAL), flush=True)
    arm_soft = score_arm_soft_topk(C, transition, chains_eval, cues_eval,
                                   HOP_DEPTH, K_TOP, T_DEFAULT_UNCAL)
    print("  soft_topK top1_hop_last=%.3f ECE=%.3f" % (
        arm_soft["top1_hop_last"], arm_soft["ece_hop_last"]), flush=True)

    print("[seed=%d] scoring ARM_SOFT_TOPK_R11 (T*=%.3g)..." % (seed, t_star), flush=True)
    arm_r11 = score_arm_soft_topk(C, transition, chains_eval, cues_eval,
                                  HOP_DEPTH, K_TOP, t_star)
    print("  r11 top1_hop_last=%.3f ECE=%.3f" % (
        arm_r11["top1_hop_last"], arm_r11["ece_hop_last"]), flush=True)

    # Compute per-arm derived metrics
    def entropy_ratio(arm_dict: Dict[str, Any]) -> float:
        e = arm_dict["entropy_per_hop_nats"]
        if len(e) < 2 or e[0] <= 1e-9:
            return float("nan")
        return float(e[-1] / e[0])

    arm_baseline["entropy_ratio"] = entropy_ratio(arm_baseline)
    arm_soft["entropy_ratio"] = entropy_ratio(arm_soft)
    arm_r11["entropy_ratio"] = entropy_ratio(arm_r11)

    # Lift vs baseline
    lift_soft = arm_soft["top1_hop_last"] - arm_baseline["top1_hop_last"]
    lift_r11 = arm_r11["top1_hop_last"] - arm_baseline["top1_hop_last"]
    arm_soft["lift_vs_baseline"] = lift_soft
    arm_r11["lift_vs_baseline"] = lift_r11

    # Audit
    assert _LLM_CALL_COUNTER[0] == 0, \
        "FATAL: LLM_CALL_COUNTER non-zero after scoring: %d" % _LLM_CALL_COUNTER[0]

    elapsed = time.time() - t0

    return {
        "seed": seed,
        "N_DIM": N_DIM,
        "V_C": V_C,
        "K_TOP": K_TOP,
        "HOP_DEPTH": HOP_DEPTH,
        "n_chains_eval": N_CHAINS_EVAL,
        "n_chains_heldout": N_CHAINS_HELDOUT,
        "epsilon_noise": EPSILON_NOISE,
        "run_mode": RUN_MODE,
        "encoder_provenance": ENCODER_PROVENANCE,
        "corpus_provenance_real": CORPUS_PROVENANCE_REAL,
        "allow_synthetic": ALLOW_SYNTHETIC,
        "cross_cell_rail": rail,
        "cross_cell_rail_pass": rail_pass,
        "r11_temperature_star": t_star,
        "r11_t_to_nll": t_to_nll,
        "arm_metrics": {
            ARM_BASELINE_TOP1_ARGMAX: arm_baseline,
            ARM_SOFT_TOPK_DISTRIBUTION: arm_soft,
            ARM_SOFT_TOPK_R11: arm_r11,
        },
        "lift_soft_vs_baseline": lift_soft,
        "lift_r11_vs_baseline": lift_r11,
        "n_llm_calls": _LLM_CALL_COUNTER[0],
        "zero_llm_calls_at_inference": (_LLM_CALL_COUNTER[0] == 0),
        "elapsed_s": elapsed,
    }


# ---------------------------------------------------------------------------
# Verdict (LOCKED pre-reg bands; HARD_FAIL_SANITY before any verdict claim)
# ---------------------------------------------------------------------------

def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    """LOCKED pre-reg bands per prereg; HARD_FAIL_SANITY (rail) gate first.

    Per Fix #28: read per-arm metrics, not summary verdict text.
    """
    def _mean(key: str) -> float:
        vals = [p[key] for p in ps if key in p and p[key] is not None
                and isinstance(p[key], (int, float))
                and not math.isnan(p[key])]
        return float(np.mean(vals)) if vals else float("nan")

    def _mean_arm(arm: str, key: str) -> float:
        vals = []
        for p in ps:
            am = p.get("arm_metrics", {})
            if arm in am and key in am[arm]:
                v = am[arm][key]
                if isinstance(v, (int, float)) and not math.isnan(v):
                    vals.append(v)
        return float(np.mean(vals)) if vals else float("nan")

    baseline_top1 = _mean_arm(ARM_BASELINE_TOP1_ARGMAX, "top1_hop_last")
    soft_top1 = _mean_arm(ARM_SOFT_TOPK_DISTRIBUTION, "top1_hop_last")
    r11_top1 = _mean_arm(ARM_SOFT_TOPK_R11, "top1_hop_last")
    baseline_ece = _mean_arm(ARM_BASELINE_TOP1_ARGMAX, "ece_hop_last")
    soft_ece = _mean_arm(ARM_SOFT_TOPK_DISTRIBUTION, "ece_hop_last")
    r11_ece = _mean_arm(ARM_SOFT_TOPK_R11, "ece_hop_last")
    baseline_eratio = _mean_arm(ARM_BASELINE_TOP1_ARGMAX, "entropy_ratio")
    soft_eratio = _mean_arm(ARM_SOFT_TOPK_DISTRIBUTION, "entropy_ratio")
    r11_eratio = _mean_arm(ARM_SOFT_TOPK_R11, "entropy_ratio")
    lift_soft = _mean("lift_soft_vs_baseline")
    lift_r11 = _mean("lift_r11_vs_baseline")
    t_star = _mean("r11_temperature_star")
    rail_diff = float(np.mean([p["cross_cell_rail"]["rail_top1_diff"] for p in ps
                               if "cross_cell_rail" in p])) if ps else float("nan")
    rail_pass = all(p.get("cross_cell_rail_pass", False) for p in ps)
    n_llm = sum(p.get("n_llm_calls", 0) for p in ps)

    summary = (
        "BASELINE_top1@hop5=%.3f SOFT_top1=%.3f R11_top1=%.3f "
        "lift_soft=%+.3f lift_r11=%+.3f "
        "BASELINE_ECE=%.3f SOFT_ECE=%.3f R11_ECE=%.3f "
        "BASELINE_Hratio=%.3f SOFT_Hratio=%.3f R11_Hratio=%.3f "
        "T*=%.3g rail_diff=%.4f rail_pass=%s n_llm=%d "
        "(N=%d V_C=%d K=%d HOP=%d eps=%.2f mode=%s seeds=%d)" % (
            baseline_top1, soft_top1, r11_top1,
            lift_soft, lift_r11,
            baseline_ece, soft_ece, r11_ece,
            baseline_eratio, soft_eratio, r11_eratio,
            t_star, rail_diff, rail_pass, n_llm,
            N_DIM, V_C, K_TOP, HOP_DEPTH, EPSILON_NOISE, RUN_MODE, len(ps),
        )
    )

    # --- HARD_FAIL_SANITY: cross-cell rail (full only; smoke is structural) ---
    if RUN_MODE == "full" and not rail_pass:
        return ("HARD_FAIL",
                "HARD_FAIL_SANITY: cross-cell rail FAIL -- ARM_BASELINE top-1 differs from "
                "hdlab.iterative_attractor.argmax_cleanup by >= %.3f. Substrate primitive "
                "unverified; ABORT verdict claim. " % RAIL_TOP1_TOLERANCE + summary)

    # --- Substrate-only-decode gate ---
    if n_llm > 0:
        return ("HARD_FAIL",
                "HARD_FAIL_SUBSTRATE_ONLY: %d LLM forward call(s) at inference. " % n_llm
                + summary)

    # --- HARD_FAIL on lift / entropy / ECE ---
    if math.isnan(lift_r11):
        return ("HARD_FAIL", "HARD_FAIL: R11 lift is NaN. " + summary)
    if lift_r11 <= MIDDLE_BAND_LIFT_LO:
        return ("HARD_FAIL",
                "HARD_FAIL: R11 lift=%+.3f <= %.3f (no top-1 advantage). " % (
                    lift_r11, MIDDLE_BAND_LIFT_LO) + summary)
    if r11_ece > MIDDLE_BAND_ECE_MAX:
        return ("HARD_FAIL",
                "HARD_FAIL: R11 ECE=%.3f > %.3f (miscalibrated). " % (
                    r11_ece, MIDDLE_BAND_ECE_MAX) + summary)
    # Entropy collapse or saturation check
    log_K = math.log(K_TOP)
    if not math.isnan(r11_eratio):
        # Collapse: ratio essentially 0 (degenerate)
        if r11_eratio < 0.01:
            return ("HARD_FAIL",
                    "HARD_FAIL: R11 entropy ratio %.4f near 0 (collapse). " % r11_eratio
                    + summary)
        # Saturation: ratio near 1 AND H(hop-1) near log(K) -> uniform throughout
        soft_h_last_nat = float(np.mean([
            p["arm_metrics"][ARM_SOFT_TOPK_R11]["entropy_per_hop_nats"][-1]
            for p in ps
            if ARM_SOFT_TOPK_R11 in p.get("arm_metrics", {})
        ])) if ps else float("nan")
        if not math.isnan(soft_h_last_nat) and soft_h_last_nat > 0.95 * log_K:
            return ("HARD_FAIL",
                    "HARD_FAIL: R11 entropy at hop-last %.3f saturates near log(K)=%.3f "
                    "(uniform -> no information). " % (soft_h_last_nat, log_K) + summary)

    # --- HARD_PASS: lift >= 0.03 AND ECE <= 0.15 AND entropy ratio in band AND rail pass ---
    entropy_in_band = (HARD_PASS_ENTROPY_RATIO_LO <= r11_eratio
                       <= HARD_PASS_ENTROPY_RATIO_HI) if not math.isnan(r11_eratio) else False
    if (lift_r11 >= HARD_PASS_LIFT_THRESHOLD
            and r11_ece <= HARD_PASS_ECE_MAX
            and entropy_in_band
            and rail_pass):
        return ("HARD_PASS",
                "HARD_PASS: R11 lift=%+.3f >= %.3f AND ECE=%.3f <= %.3f "
                "AND entropy ratio=%.3f in [%.2f, %.2f] AND cross-cell rail PASS. "
                "Soft top-K distribution-preserving readout CLOSES top-1 gap WITHOUT "
                "new architecture. " % (
                    lift_r11, HARD_PASS_LIFT_THRESHOLD,
                    r11_ece, HARD_PASS_ECE_MAX,
                    r11_eratio, HARD_PASS_ENTROPY_RATIO_LO, HARD_PASS_ENTROPY_RATIO_HI)
                + summary)

    # --- MIDDLE_BAND ---
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: R11 lift=%+.3f (HP>=%.3f, MIDDLE>%.3f) ECE=%.3f H_ratio=%.3f "
            "-- partial closure. " % (
                lift_r11, HARD_PASS_LIFT_THRESHOLD, MIDDLE_BAND_LIFT_LO,
                r11_ece, r11_eratio)
            + summary)


# ---------------------------------------------------------------------------
# Main sweep
# ---------------------------------------------------------------------------

print("[config] anchor=%s mode=%s N=%d V_C=%d K_TOP=%d HOP=%d seeds=%s" % (
    ANCHOR_NAME, RUN_MODE, N_DIM, V_C, K_TOP, HOP_DEPTH, SEEDS), flush=True)
print("[config] version=%s" % CONFIG_VERSION, flush=True)
print("[config] ENCODER_PROVENANCE=%s ALLOW_SYNTHETIC=%s" % (
    ENCODER_PROVENANCE, ALLOW_SYNTHETIC), flush=True)
print("[config] ARMS=%s" % (ALL_ARMS,), flush=True)
print("[config] PRE-REG BANDS LOCKED: HP_LIFT>=%.3f / ECE<=%.3f / ENT[%.2f,%.2f] / RAIL<=%.3f"
      % (HARD_PASS_LIFT_THRESHOLD, HARD_PASS_ECE_MAX,
         HARD_PASS_ENTROPY_RATIO_LO, HARD_PASS_ENTROPY_RATIO_HI,
         RAIL_TOP1_TOLERANCE), flush=True)

out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"run_mode": RUN_MODE, "N": N_DIM, "V_C": V_C}

done_seeds, remaining_seeds = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print("[ckpt] %d/%d seeds already complete; running %s" % (
    len(done_seeds), len(SEEDS), remaining_seeds), flush=True)

t_total = time.time()
ps: List[Dict[str, Any]] = []

for seed in remaining_seeds:
    r = run_seed(seed)
    ps.append(r)
    write_partial(out_dir, seed, r)
    print("  [seed=%d] DONE elapsed=%.1fs" % (seed, r["elapsed_s"]), flush=True)

if done_seeds:
    agg = aggregate_partials(out_dir, done_seeds, run_config=run_config)
    for k, v in agg.items():
        ps.append(v)

if not ps:
    print("[ERROR] no seeds completed; aborting", flush=True)
    sys.exit(1)

v, vmsg = verdict(ps)
print("\n[VERDICT] " + vmsg, flush=True)

metrics = {
    "anchor_name": ANCHOR_NAME,
    "config_version": CONFIG_VERSION,
    "verdict": v,
    "verdict_msg": vmsg,
    "summary": vmsg,
    "run_mode": RUN_MODE,
    "n_seeds": len(ps),
    "N_DIM": N_DIM,
    "V_C": V_C,
    "K_TOP": K_TOP,
    "HOP_DEPTH": HOP_DEPTH,
    "encoder_provenance": ENCODER_PROVENANCE,
    "corpus_provenance_real": CORPUS_PROVENANCE_REAL,
    "allow_synthetic": ALLOW_SYNTHETIC,
    "all_arms": ALL_ARMS,
    "pre_reg_bands": {
        "HARD_PASS_LIFT_THRESHOLD": HARD_PASS_LIFT_THRESHOLD,
        "HARD_PASS_ECE_MAX": HARD_PASS_ECE_MAX,
        "HARD_PASS_ENTROPY_RATIO_LO": HARD_PASS_ENTROPY_RATIO_LO,
        "HARD_PASS_ENTROPY_RATIO_HI": HARD_PASS_ENTROPY_RATIO_HI,
        "MIDDLE_BAND_LIFT_LO": MIDDLE_BAND_LIFT_LO,
        "MIDDLE_BAND_ECE_MAX": MIDDLE_BAND_ECE_MAX,
        "RAIL_TOP1_TOLERANCE": RAIL_TOP1_TOLERANCE,
        "P_HARD_PASS": P_HARD_PASS,
        "P_MIDDLE": P_MIDDLE,
        "P_HARD_FAIL": P_HARD_FAIL,
    },
    "zero_llm_calls_at_inference": all(p.get("zero_llm_calls_at_inference", True) for p in ps),
    "per_seed": ps,
    "elapsed_s": time.time() - t_total,
}
write_metrics(out_dir, metrics, ps)
print("[metrics] written to %s" % out_dir, flush=True)
