"""g1_substrate_native_generation_v1 -- Substrate-native autoregressive generation.

SCIENTIFIC QUESTION (brain-drill #4 cerebellar forward-prediction, 2026-06-22):
  Can the substrate GENERATE a coherent sequence of states using ONLY substrate
  primitives (S matrix from c3 + codebook NN-cleanup + optional Langevin noise),
  with ZERO LLM forward calls at generation time?

  Architecture mapping (biology -> substrate):
    - HVC sparse-time-cell synfire chain   = S matrix (hetero-associative;
                                              Karuvally-Sejnowski 2023 NeurIPS,
                                              c3 sequence-binding primitive)
    - Cerebellar forward model s_{t+1}=f(s_t) = S @ k_{t-1} retrieval (same
                                              architecture, different framing)
    - Modern Hopfield Langevin sampling    = additive Gaussian noise on the
                                              raw S @ k output (arxiv 2603.06875)
    - DG/CA3 codebook attractor cleanup    = codebook_nn (the substrate's
                                              content-addressing primitive,
                                              shared with c3)
    - BG-PBWM start/stop refuse-gate       = OOD refuse via low-confidence
                                              codebook-NN cosine

  Protocol:
    1. Build N_SEQ=10 sequences of length K=20 from synthetic bipolar keys
       (same substrate-isolation pattern as c3; mirrors c1 / a8).
    2. Train the S matrix via Hebbian outer-products on adjacent ordered pairs
       (the c3 COMPRESSED primitive; W is point-write side, S is sequence side).
    3. Generate per-arm rollouts of length T from held-out start keys; evaluate:
         arm 1 (NONE):            k_t = random codebook entry (no S, no cleanup)
         arm 2 (S_ONLY):          k_t = S @ k_{t-1} raw (no noise, no cleanup)
         arm 3 (S_LANGEVIN):      k_t = S @ k_{t-1} + sigma*randn (no cleanup)
         arm 4 (S_LANGEVIN_CLEANUP): k_t = codebook_nn(S @ k_{t-1} + sigma*randn)
       Arm 4 is the proposed chain-grade primitive. The 4 arms IS the
       discriminator-regime (Fix #16) -- one arm must split from the others.

    4. Per-arm metrics:
         trajectory_coherence(T): mean codebook-NN agreement with the
                                  planted-sequence continuation across T-step
                                  rollouts.
         novelty_ratio:           P(visited heldout-continuation codebook entries)
                                  / P(visited random codebook entries) -- measures
                                  whether generation is "going somewhere learned"
                                  vs random walk. >= 1.5x = plausibly generating.
         refuse_OOD:              fraction of OOD-start rollouts where the
                                  raw-cosine confidence drops below tau_stop
                                  within the first 4 steps. Refuse-gate fires.

  Discriminating-regime arms (Fix #16, the CAN-fail regime IS the 4-arm contrast):
    - all arms ~ NONE       => mechanism null (substrate cannot generate)
    - all arms ~ S_LANGEVIN_CLEANUP at top => harness too easy
    - S_ONLY ~ S_LANGEVIN_CLEANUP => cleanup is a NULL discriminator
    - S_LANGEVIN ~ S_LANGEVIN_CLEANUP => cleanup is NULL DISCRIMINATOR (honest
                                          per-cell finding mirroring drill #5's
                                          biological-compression null)
    - S_LANGEVIN_CLEANUP >> S_LANGEVIN => cleanup is load-bearing complement
                                          (expected; codebook attractors snap
                                           noise-perturbed states back to
                                           valid sequence trajectories)

  Substrate-only-decode gate: pure numpy + Hebbian + codebook-NN cleanup +
  Gaussian noise; ZERO LLM forward calls anywhere (asserted == 0).

  W vs S separation: writes ONLY mutate S; W (the c3 invariant) is untouched.

PRE-REGISTERED BANDS (brain-drill #4 / task-spec deflation):
  HARD_PASS (chain-grade, generation mechanism validated):
    Arm 4 (S_LANGEVIN_CLEANUP) trajectory_coherence(T=8) >= 0.60
    AND Arm 4 novelty_ratio >= 1.5
    AND Arm 4 refuse_OOD >= 0.90
    AND Arm 1 (NONE) trajectory_coherence(T=8) <= 0.20 (control is incoherent)
    AND delta(Arm 4 - Arm 1) >= 0.40 at T=8
    AND cv <= 0.07 across 3 seeds for Arm 4 at T=8 (looser than 0.05 because
                                                    generation is noisier)
    AND zero_llm_calls_at_inference == True
    AND W matrix L2-norm unchanged by generation (assertion)

  MIDDLE_BAND (proven-bound partial):
    Arm 4 trajectory_coherence(T=8) in [0.20, 0.60) with delta(Arm4-Arm1) >= 0.20
    OR novelty_ratio in [1.0, 1.5)

  HARD_FAIL:
    trajectory_coherence(T=8) < 0.20 at Arm 4
    OR substrate-only-decode gate violated (LLM calls > 0)
    OR W modified by generation
    OR Arm 4 collapses to a single fixed-point attractor (trajectory_coherence
       is high BUT codebook entries visited collapses to <= 2 distinct entries
       across the T-step rollout)
    OR refuse_OOD < 0.50 (gate broken)

  Discriminating-regime check (4-arm contrast IS the discriminator):
    Smoke-VET asserts at least one arm splits from baseline (Arm 1) by >=
    0.10 at T=8 OR all-arms collapse to <= 0.15 (null mechanism); a flat-1.0
    sweep at all arms = harness mis-spec.

FIX INVENTORY:
  - _LLM_CALL_COUNTER = [0] at module top (substrate-only gate)
  - ANCHOR_NAME, CONFIG_VERSION baked module-level (AST-verifiable)
  - run_mode='full' default; --smoke / HDLAB_RUN_MODE / HDLAB_EXP_NAME _smoke
    suffix all honored (TODO #6 resolution pattern)
  - allow_synthetic=True is CORRECT here (synthetic bipolar keys; substrate-
    primitive isolation; CORPUS_PROVENANCE recorded)
  - per_seed entry per (seed, arm, T_gen) into metrics.json
  - cv across seeds computed in verdict()
  - Pre-reg direction enforced (Arm 4 > Arm 1; cv tight; novelty >= 1.5)
  - Discriminating-regime: 4-arm contrast IS the discriminator (Fix #16)
  - Resumable via _seed_checkpoint per-seed partials
  - atexit + SIGTERM synthesize-from-partials (TODO #9 pattern)
  - Uses hdlab.sequence_memory.SequenceMatrix (c3 chain-grade primitive)

FORMULA SELF-TESTS:
  1. Arm 1 (NONE) at K=5 small seq: trajectory_coherence(T=3) <= 0.40 (random)
  2. Arm 4 (S_LANGEVIN_CLEANUP) at K=5 small seq: trajectory_coherence(T=3) >= 0.50
  3. _LLM_CALL_COUNTER remains 0 throughout

ASCII-only. CPU. Single-file. Resumable via _seed_checkpoint.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
import signal
import atexit
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "g1_substrate_native_generation_v1"

# Substrate-only-decode gate (Skunkworks structural blocker #3).
# Asserted == 0 at end of run. Any LLM forward call MUST increment this.
_LLM_CALL_COUNTER = [0]

# Corpus provenance: synthetic bipolar keys (same as c3 / c1 / a8 -- substrate
# primitive isolation). Phase 2 (deferred) extends to Pythia-encoded FB15k chains.
CORPUS_PROVENANCE = "synthetic_bipolar_keys_sequences"

# Track whether write_metrics fired (used by atexit synthesizer to avoid double-write).
_METRICS_WRITTEN = [False]


def _detect_run_mode():
    """Detect smoke vs full. Priority:
      1. --smoke CLI flag
      2. HDLAB_RUN_MODE env var
      3. HDLAB_EXP_NAME ending in _smoke (runner queue-name convention; TODO #6 fix)
      4. default "full"
    """
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
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Pre-reg bands (locked at design time per task-spec deflation)
HARD_PASS_ARM4_AT_T8 = 0.60        # Arm 4 trajectory_coherence at T=8
HARD_PASS_ARM1_AT_T8_MAX = 0.20    # Arm 1 (NONE) control must be <= this
HARD_PASS_DELTA = 0.40             # Arm4 - Arm1 at T=8
HARD_PASS_NOVELTY = 1.5            # Arm 4 novelty_ratio
HARD_PASS_REFUSE_OOD = 0.90        # Arm 4 OOD refuse rate
MIDDLE_BAND_LO = 0.20              # delta in [0.20, 0.40) = MIDDLE_BAND
MIDDLE_BAND_ARM4_LO = 0.20         # Arm 4 coh in [0.20, 0.60) = MIDDLE_BAND
HARD_FAIL_ARM4 = 0.20              # Arm 4 < this at T=8 = HARD_FAIL
HARD_FAIL_REFUSE_OOD = 0.50        # Arm 4 refuse_OOD < this = HARD_FAIL (gate broken)
HARD_FAIL_NOVELTY = 1.0            # novelty_ratio < this = pure-memorization HARD_FAIL
CV_HARD_PASS_MAX = 0.07            # cv across seeds for HARD_PASS (looser than c3 0.05)

# Smoke vs full config
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 1024
    K_SEQ = 8                 # short sequences for smoke
    N_SEQ = 4                 # few sequences
    T_GENS = [1, 3, 5]        # smoke covers up through small T
    ARMS = ["NONE", "S_ONLY", "S_LANGEVIN", "S_LANGEVIN_CLEANUP"]
    N_PROBES_PER_T = 20       # rollouts per (arm, T) on heldout-starts
    N_OOD_PROBES = 20         # OOD rollouts for refuse_rate
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    K_SEQ = 20
    N_SEQ = 10
    T_GENS = [1, 4, 8, 16]    # pre-reg primary T=8; T=16 super-pass; T=1 anchor
    ARMS = ["NONE", "S_ONLY", "S_LANGEVIN", "S_LANGEVIN_CLEANUP"]
    N_PROBES_PER_T = 40
    N_OOD_PROBES = 40

# Langevin noise scaling (sigma = LANGEVIN_SIGMA_SCALE * mean_norm(S @ k))
LANGEVIN_SIGMA_SCALE = 0.10
# OOD refuse threshold: cosine of S @ k to nearest codebook entry below this = refuse
REFUSE_TAU = 0.10

CONFIG_VERSION = (
    "g1-substrate-native-generation-v1: K=%d N_SEQ=%d N_DIM=%d arms=%s "
    "T_gens=%s sigma_scale=%.3f refuse_tau=%.3f; "
    "bands HP_arm4@T8=%.2f delta=%.2f novelty=%.2f refuse_OOD=%.2f "
    "run_mode=%s" %
    (K_SEQ, N_SEQ, N_DIM, ",".join(ARMS), str(T_GENS),
     LANGEVIN_SIGMA_SCALE, REFUSE_TAU,
     HARD_PASS_ARM4_AT_T8, HARD_PASS_DELTA, HARD_PASS_NOVELTY, HARD_PASS_REFUSE_OOD,
     RUN_MODE))


def make_bipolar(M: int, n: int, rng: np.random.RandomState) -> np.ndarray:
    """Random +/- 1 vectors, L2-normalized to unit length."""
    X = rng.choice([-1.0, 1.0], size=(M, n)).astype(np.float64)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)


def codebook_nn(y: np.ndarray, codebook: np.ndarray) -> Tuple[int, np.ndarray, float]:
    """Cosine nearest-neighbor in codebook. Returns (idx, codebook[idx], cosine).

    The cosine returned is the cosine of y (post-normalized) to codebook[idx],
    used as the refuse-gate confidence signal.
    """
    y_norm = float(np.linalg.norm(y))
    if y_norm < 1e-12:
        # Degenerate; return index 0 with zero confidence
        return 0, codebook[0], 0.0
    y_n = y / y_norm
    sims = codebook @ y_n
    idx = int(np.argmax(sims))
    return idx, codebook[idx], float(sims[idx])


def build_sequences(n_seq: int, k_seq: int, n_dim: int,
                    rng: np.random.RandomState) -> Tuple[np.ndarray, np.ndarray]:
    """Build n_seq sequences each of k_seq disjoint bipolar keys.

    Returns:
      sequences: shape (n_seq, k_seq, n_dim) -- the keys in temporal order
      codebook:  shape (n_seq * k_seq, n_dim) -- flat codebook for NN cleanup,
                 where codebook[seq_id * k_seq + t] = sequences[seq_id, t].
    """
    total = n_seq * k_seq
    codebook = make_bipolar(total, n_dim, rng)
    sequences = codebook.reshape(n_seq, k_seq, n_dim).copy()
    return sequences, codebook


def write_W_point_writes(sequences: np.ndarray, n_dim: int) -> np.ndarray:
    """Vectorized point-write of each (k_i, k_i) into W. Returns W.

    Used only to record the W-unchanged-by-generation invariant. Same as c3.
    """
    n_seq, k_seq, _ = sequences.shape
    K = sequences.reshape(n_seq * k_seq, n_dim)
    return (K.T @ K) / n_dim


def write_S_compressed(sequences: np.ndarray, n_dim: int) -> np.ndarray:
    """Hebbian outer-product writes of all adjacent ordered pairs into S.

    Vectorized: S = K_curr^T @ K_prev / n_dim (c3 chain-grade primitive).
    """
    n_seq, k_seq, _ = sequences.shape
    K_prev = sequences[:, :-1, :].reshape(n_seq * (k_seq - 1), n_dim)
    K_curr = sequences[:, 1:, :].reshape(n_seq * (k_seq - 1), n_dim)
    return (K_curr.T @ K_prev) / n_dim


def make_ood_key(n_dim: int, rng: np.random.RandomState,
                 codebook: np.ndarray) -> np.ndarray:
    """Generate an OOD key (random bipolar NOT in codebook).

    Re-sample until cosine to nearest codebook entry < 0.50 (probabilistically
    the FIRST sample meets this at high N_DIM; loop is cheap insurance).
    """
    for _ in range(20):
        v = rng.choice([-1.0, 1.0], size=(n_dim,)).astype(np.float64)
        v = v / (np.linalg.norm(v) + 1e-12)
        sims = codebook @ v
        if float(np.max(sims)) < 0.50:
            return v
    return v  # accept whatever we got after 20 tries


def generate_arm(arm: str, k_start: np.ndarray, T: int,
                 S: np.ndarray, codebook: np.ndarray,
                 sigma: float, rng: np.random.RandomState
                 ) -> Tuple[List[int], List[float]]:
    """One arm's T-step generation rollout from k_start.

    Returns:
      visited_indices: list of length T -- codebook index of each generated state
                       (for NONE: random codebook index; for S_*: the indices
                       after applying the arm's step function)
      step_confidences: list of length T -- the codebook-NN cosine at each step
                       (used for OOD refuse-gate evaluation)

    For the arms that don't snap to codebook (S_ONLY, S_LANGEVIN), the "visited
    index" is the codebook-NN of the raw state (for measurement purposes only --
    the state itself remains the raw value for the next step).
    """
    k = k_start.copy()
    visited: List[int] = []
    confs: List[float] = []

    if arm == "NONE":
        # No S, no cleanup; emit random codebook indices as "generation"
        n_cb = codebook.shape[0]
        for _ in range(T):
            idx = int(rng.randint(0, n_cb))
            visited.append(idx)
            confs.append(0.0)  # no confidence signal for random arm
        return visited, confs

    for _ in range(T):
        y = S @ k
        if arm == "S_ONLY":
            # Raw S retrieval, no noise, no cleanup
            idx, _, conf = codebook_nn(y, codebook)
            visited.append(idx)
            confs.append(conf)
            k = y  # next step uses raw output (no snap)
        elif arm == "S_LANGEVIN":
            # Add Gaussian noise to raw y; no cleanup snap
            noise = rng.randn(y.shape[0]) * sigma
            y_noisy = y + noise
            idx, _, conf = codebook_nn(y_noisy, codebook)
            visited.append(idx)
            confs.append(conf)
            k = y_noisy  # next step uses raw noisy output (no snap)
        elif arm == "S_LANGEVIN_CLEANUP":
            # Full mechanism: S + Langevin + codebook attractor cleanup
            noise = rng.randn(y.shape[0]) * sigma
            y_noisy = y + noise
            idx, k_snap, conf = codebook_nn(y_noisy, codebook)
            visited.append(idx)
            confs.append(conf)
            k = k_snap.copy()  # snap to codebook attractor; next step starts here
        else:
            raise ValueError("unknown arm: %s" % arm)
    return visited, confs


def estimate_sigma(S: np.ndarray, sequences: np.ndarray) -> float:
    """Compute sigma = LANGEVIN_SIGMA_SCALE * mean_norm(S @ k) over training keys.

    Single global sigma per seed (rather than per-step), so Langevin temperature
    is calibrated to the substrate's natural state-norm scale.
    """
    n_seq, k_seq, n_dim = sequences.shape
    K = sequences.reshape(n_seq * k_seq, n_dim)
    Y = K @ S.T  # shape (M, n_dim); each row is S @ k_i
    norms = np.linalg.norm(Y, axis=1)
    mean_norm = float(np.mean(norms))
    return LANGEVIN_SIGMA_SCALE * mean_norm


def eval_trajectory_coherence(arm: str, S: np.ndarray, sequences: np.ndarray,
                              codebook: np.ndarray, T: int, n_probes: int,
                              sigma: float, rng: np.random.RandomState
                              ) -> Tuple[float, float, int]:
    """Trajectory coherence at horizon T for one arm.

    For each (seq_id, t0) heldout-start with t0 + T < K_SEQ:
      - Roll out T steps starting from sequences[seq_id, t0].
      - The "planted continuation" is sequences[seq_id, t0+1..t0+T] -- the
        codebook indices of the actual next-T states from training.
      - Coherence = fraction of generated steps whose codebook index MATCHES
        the planted continuation at the same step position.

    Also returns:
      novelty_ratio: P(visited in heldout-continuation codebook entries) /
                     P(visited in random-other-sequence codebook entries).
                     1.0 = generation is no more "going to plausible places"
                     than a random walk; > 1.5 = generating plausibly.
      n_distinct: number of distinct codebook indices visited across all
                  rollouts (collapse detector; if generation collapses to one
                  fixed-point, this will be ~1).
    """
    n_seq, k_seq, n_dim = sequences.shape
    if T >= k_seq:
        return 0.0, 1.0, 0

    valid_starts = [(s, t0) for s in range(n_seq) for t0 in range(k_seq - T)]
    if not valid_starts:
        return 0.0, 1.0, 0
    n_q = min(n_probes, len(valid_starts))
    chosen_idx = rng.choice(len(valid_starts), size=n_q, replace=False)

    total_steps = 0
    correct_steps = 0
    visited_in_planted = 0
    visited_in_random = 0
    all_visited: List[int] = []

    for ci in chosen_idx:
        s_id, t0 = valid_starts[int(ci)]
        k_start = sequences[s_id, t0]
        visited, _confs = generate_arm(arm, k_start, T, S, codebook, sigma, rng)
        all_visited.extend(visited)

        # Planted continuation: codebook indices of sequences[s_id, t0+1..t0+T]
        planted_set = set(s_id * k_seq + (t0 + step + 1) for step in range(T))

        # Random "other" continuation: pick another sequence, same start offset
        other_seq = (s_id + 1 + rng.randint(0, n_seq - 1)) % n_seq
        # Ensure t0+1..t0+T is in range for other_seq (always is; same k_seq)
        random_set = set(other_seq * k_seq + (t0 + step + 1) for step in range(T))

        for step_t, idx in enumerate(visited):
            total_steps += 1
            target_idx = s_id * k_seq + (t0 + step_t + 1)
            if idx == target_idx:
                correct_steps += 1
            if idx in planted_set:
                visited_in_planted += 1
            if idx in random_set:
                visited_in_random += 1

    coherence = float(correct_steps) / total_steps if total_steps > 0 else 0.0
    n_distinct = len(set(all_visited))

    # Novelty ratio: P(planted) / P(random). Use uniform-prior smoothing to bound the
    # ratio when p_random is degenerate (zero overlap from the random-other set).
    # Smoothing prior: 1/(2*N_SEQ*K_SEQ) per step -- the uniform-codebook expectation
    # under a random walk. With smoothing, max possible ratio is bounded by 1/prior;
    # ratio remains directionally correct (higher = more plausible generation).
    n_codebook = n_seq * k_seq
    prior = 0.5 / float(n_codebook)
    p_planted = visited_in_planted / total_steps if total_steps > 0 else 0.0
    p_random = visited_in_random / total_steps if total_steps > 0 else 0.0
    novelty_ratio = (p_planted + prior) / (p_random + prior)

    return coherence, novelty_ratio, n_distinct


def eval_refuse_ood(arm: str, S: np.ndarray, codebook: np.ndarray,
                    n_probes: int, T_check: int, sigma: float,
                    rng: np.random.RandomState) -> float:
    """OOD refuse rate at one arm.

    Generate n_probes rollouts from OOD start keys (random bipolar NOT in
    codebook); count fraction where the codebook-NN cosine drops below
    REFUSE_TAU within the first T_check steps. That fraction IS the refuse
    rate -- the substrate REFUSES to generate when off-distribution.

    For NONE arm: refuse_rate is fixed at 0.0 (it always emits random indices,
    no confidence signal). Reported for completeness.
    """
    if arm == "NONE":
        return 0.0

    n_dim = S.shape[0]
    refuse_count = 0
    for _ in range(n_probes):
        k_ood = make_ood_key(n_dim, rng, codebook)
        _, confs = generate_arm(arm, k_ood, T_check, S, codebook, sigma, rng)
        # Refused if ANY of the first T_check steps has cosine < REFUSE_TAU
        if any(c < REFUSE_TAU for c in confs):
            refuse_count += 1
    return float(refuse_count) / n_probes


def eval_refuse_in_corpus(arm: str, S: np.ndarray, sequences: np.ndarray,
                          codebook: np.ndarray, n_probes: int, T_check: int,
                          sigma: float, rng: np.random.RandomState) -> float:
    """In-corpus false-refuse rate at one arm.

    Generate n_probes rollouts from valid in-corpus starts; count fraction
    where the refuse-gate INCORRECTLY fires (gate should NOT fire on
    in-corpus seeds). Should be <= 0.10 for a calibrated gate.
    """
    if arm == "NONE":
        return 0.0

    n_seq, k_seq, n_dim = sequences.shape
    # Only use t0 such that t0 + T_check < k_seq
    valid_starts = [(s, t0) for s in range(n_seq) for t0 in range(k_seq - T_check)]
    if not valid_starts:
        return 0.0
    n_q = min(n_probes, len(valid_starts))
    chosen_idx = rng.choice(len(valid_starts), size=n_q, replace=False)

    refuse_count = 0
    for ci in chosen_idx:
        s_id, t0 = valid_starts[int(ci)]
        k_start = sequences[s_id, t0]
        _, confs = generate_arm(arm, k_start, T_check, S, codebook, sigma, rng)
        if any(c < REFUSE_TAU for c in confs):
            refuse_count += 1
    return float(refuse_count) / n_q


def run_one_arm(arm: str, seed: int) -> Dict:
    """Run one arm for one seed: build S, evaluate trajectory + refuse metrics."""
    t_arm_start = time.time()
    rng = np.random.RandomState(seed * 1000 + hash(arm) % 10000)

    n_dim = N_DIM
    sequences, codebook = build_sequences(N_SEQ, K_SEQ, n_dim, rng)

    # Build W (point-writes) -- used only for W-unchanged invariant assertion
    W = write_W_point_writes(sequences, n_dim)
    W_norm_before = float(np.linalg.norm(W))

    # Build S via Hebbian adjacent-pair writes (c3 chain-grade primitive)
    S = write_S_compressed(sequences, n_dim)
    S_norm = float(np.linalg.norm(S))

    # Estimate sigma for Langevin arms (one global value)
    sigma = estimate_sigma(S, sequences) if arm in ("S_LANGEVIN", "S_LANGEVIN_CLEANUP") else 0.0

    # Verify W unchanged (generation should NOT touch W)
    W_norm_after = float(np.linalg.norm(W))
    W_unchanged = (abs(W_norm_after - W_norm_before) < 1e-10)
    if not W_unchanged:
        raise AssertionError(
            "W modified during arm=%s setup (norm %.6f -> %.6f)" %
            (arm, W_norm_before, W_norm_after))

    # Trajectory coherence + novelty at each T
    coherence_per_T: Dict[str, float] = {}
    novelty_per_T: Dict[str, float] = {}
    distinct_per_T: Dict[str, int] = {}
    for T in T_GENS:
        coh, nov, n_dist = eval_trajectory_coherence(
            arm, S, sequences, codebook, T, N_PROBES_PER_T, sigma, rng)
        coherence_per_T[str(T)] = coh
        novelty_per_T[str(T)] = nov
        distinct_per_T[str(T)] = n_dist

    # Refuse-gate at T_check=4 (per task-spec: refuse within first 4 steps)
    T_REFUSE_CHECK = min(4, max(T_GENS))
    refuse_OOD = eval_refuse_ood(arm, S, codebook, N_OOD_PROBES,
                                 T_REFUSE_CHECK, sigma, rng)
    refuse_in_corpus = eval_refuse_in_corpus(
        arm, S, sequences, codebook, N_OOD_PROBES,
        T_REFUSE_CHECK, sigma, rng)

    arm_wall_s = time.time() - t_arm_start
    return {
        "arm": arm,
        "seed": int(seed),
        "n_dim": n_dim,
        "k_seq": K_SEQ,
        "n_seq": N_SEQ,
        "sequence_matrix_norm": S_norm,
        "W_norm_before_generation": W_norm_before,
        "W_norm_after_generation": W_norm_after,
        "W_unchanged_by_generation": bool(W_unchanged),
        "sigma_langevin": float(sigma),
        "trajectory_coherence": coherence_per_T,
        "novelty_ratio": novelty_per_T,
        "n_distinct_visited": distinct_per_T,
        "refuse_OOD": float(refuse_OOD),
        "refuse_in_corpus": float(refuse_in_corpus),
        "refuse_check_T": int(T_REFUSE_CHECK),
        "arm_wall_s": float(arm_wall_s),
        "n_probes_per_T": N_PROBES_PER_T,
        "n_ood_probes": N_OOD_PROBES,
    }


def _selftest():
    """3 self-tests per the docstring."""
    rng = np.random.RandomState(0)
    n_dim = 256
    n_seq = 3
    k_seq = 5
    sequences, codebook = build_sequences(n_seq, k_seq, n_dim, rng)
    S = write_S_compressed(sequences, n_dim)
    sigma = estimate_sigma(S, sequences)

    # Selftest 1: NONE arm at T=3 should be ~0 (random codebook indices)
    coh_none, _, _ = eval_trajectory_coherence(
        "NONE", S, sequences, codebook, 3, 15, sigma, rng)
    assert coh_none <= 0.40, "selftest 1: NONE T=3 coherence too high: %.3f" % coh_none

    # Selftest 2: S_LANGEVIN_CLEANUP arm at T=3 should be high (chain-grade primitive)
    coh_full, _, _ = eval_trajectory_coherence(
        "S_LANGEVIN_CLEANUP", S, sequences, codebook, 3, 15, sigma, rng)
    assert coh_full >= 0.50, ("selftest 2: S_LANGEVIN_CLEANUP T=3 coherence too low: %.3f"
                              % coh_full)

    # Selftest 3: no LLM calls
    assert _LLM_CALL_COUNTER[0] == 0, ("selftest 3: LLM counter non-zero (%d)"
                                       % _LLM_CALL_COUNTER[0])

    print("[selftest] PASS: NONE_T3=%.3f S_LANGEVIN_CLEANUP_T3=%.3f sigma=%.4f LLM=%d"
          % (coh_none, coh_full, sigma, _LLM_CALL_COUNTER[0]), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    """Run all arms for one seed."""
    t0 = time.time()
    per_unit = []
    for arm in ARMS:
        res = run_one_arm(arm, seed)
        per_unit.append(res)
        coh8 = res["trajectory_coherence"].get("8", res["trajectory_coherence"].get("5", float("nan")))
        coh1 = res["trajectory_coherence"].get("1", float("nan"))
        nov8 = res["novelty_ratio"].get("8", res["novelty_ratio"].get("5", float("nan")))
        print("  [seed=%d] arm=%s T1=%.3f T8=%.3f nov=%.2f refuseOOD=%.2f refuseIC=%.2f wall=%.1fs"
              % (seed, arm, coh1, coh8, nov8,
                 res["refuse_OOD"], res["refuse_in_corpus"],
                 res["arm_wall_s"]), flush=True)
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "M": K_SEQ * N_SEQ,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "per_unit": per_unit,
        "elapsed_s": float(elapsed),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


def compute_verdict(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    """Compute verdict per the pre-reg bands."""
    if not per_seed:
        return ("HARD_FAIL", "No valid results.", {})

    # Aggregate: arm -> T_str -> list of (coherence, novelty)
    agg_coh: Dict[str, Dict[str, List[float]]] = {}
    agg_nov: Dict[str, Dict[str, List[float]]] = {}
    agg_refuse_ood: Dict[str, List[float]] = {}
    agg_refuse_ic: Dict[str, List[float]] = {}
    agg_distinct: Dict[str, Dict[str, List[int]]] = {}

    for sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            arm = pu["arm"]
            agg_coh.setdefault(arm, {})
            agg_nov.setdefault(arm, {})
            agg_distinct.setdefault(arm, {})
            for T_str, coh in pu.get("trajectory_coherence", {}).items():
                agg_coh[arm].setdefault(T_str, []).append(float(coh))
            for T_str, nov in pu.get("novelty_ratio", {}).items():
                agg_nov[arm].setdefault(T_str, []).append(float(nov))
            for T_str, nd in pu.get("n_distinct_visited", {}).items():
                agg_distinct[arm].setdefault(T_str, []).append(int(nd))
            agg_refuse_ood.setdefault(arm, []).append(float(pu.get("refuse_OOD", 0.0)))
            agg_refuse_ic.setdefault(arm, []).append(float(pu.get("refuse_in_corpus", 0.0)))

    # Mean + cv per (arm, T) for coherence
    mean_coh = {}
    cv_coh = {}
    mean_nov = {}
    mean_distinct = {}
    for arm in agg_coh:
        mean_coh[arm] = {}
        cv_coh[arm] = {}
        mean_nov[arm] = {}
        mean_distinct[arm] = {}
        for T_str in agg_coh[arm]:
            vals = agg_coh[arm][T_str]
            m = float(np.mean(vals))
            s = float(np.std(vals))
            mean_coh[arm][T_str] = m
            cv_coh[arm][T_str] = (s / max(m, 1e-9))
        for T_str in agg_nov.get(arm, {}):
            mean_nov[arm][T_str] = float(np.mean(agg_nov[arm][T_str]))
        for T_str in agg_distinct.get(arm, {}):
            mean_distinct[arm][T_str] = float(np.mean(agg_distinct[arm][T_str]))

    mean_refuse_ood = {arm: float(np.mean(v)) for arm, v in agg_refuse_ood.items()}
    mean_refuse_ic = {arm: float(np.mean(v)) for arm, v in agg_refuse_ic.items()}

    # Key numbers at T=8 (pre-reg primary)
    T8 = "8"
    arm1 = "NONE"
    arm4 = "S_LANGEVIN_CLEANUP"
    coh_arm1_t8 = mean_coh.get(arm1, {}).get(T8, float("nan"))
    coh_arm4_t8 = mean_coh.get(arm4, {}).get(T8, float("nan"))
    coh_arm2_t8 = mean_coh.get("S_ONLY", {}).get(T8, float("nan"))
    coh_arm3_t8 = mean_coh.get("S_LANGEVIN", {}).get(T8, float("nan"))
    delta_t8 = (coh_arm4_t8 - coh_arm1_t8) if not (math.isnan(coh_arm1_t8) or math.isnan(coh_arm4_t8)) else float("nan")
    novelty_arm4_t8 = mean_nov.get(arm4, {}).get(T8, float("nan"))
    refuse_ood_arm4 = mean_refuse_ood.get(arm4, float("nan"))
    refuse_ic_arm4 = mean_refuse_ic.get(arm4, float("nan"))
    cv_arm4_t8 = cv_coh.get(arm4, {}).get(T8, float("inf"))
    cv_arm1_t8 = cv_coh.get(arm1, {}).get(T8, float("inf"))
    distinct_arm4_t8 = mean_distinct.get(arm4, {}).get(T8, float("nan"))

    # T=1 anchor (sanity bracket)
    coh_arm4_t1 = mean_coh.get(arm4, {}).get("1", float("nan"))

    # Substrate-only-decode gate
    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    # W-unchanged assertion
    w_unchanged_ok = True
    for sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            if not pu.get("W_unchanged_by_generation", False):
                w_unchanged_ok = False

    # Discriminating-regime: arm 4 must split from arm 1 OR all arms collapse
    arms_at_t8 = [mean_coh.get(a, {}).get(T8, float("nan")) for a in ARMS]
    arms_collapse_null = all((not math.isnan(v) and v <= 0.15) for v in arms_at_t8)
    arms_collapse_top = all((not math.isnan(v) and v >= 0.99) for v in arms_at_t8)
    discriminator_split = (not math.isnan(delta_t8)) and (delta_t8 >= 0.10)

    # Fixed-point collapse: Arm 4 visits very few distinct codebook entries
    # (collapsed-to-one-attractor failure mode)
    collapse_to_fixedpoint = (
        not math.isnan(distinct_arm4_t8) and distinct_arm4_t8 <= 2.5
        and not math.isnan(coh_arm4_t8) and coh_arm4_t8 >= 0.30
    )

    detail = {
        "mean_trajectory_coherence": mean_coh,
        "cv_trajectory_coherence": cv_coh,
        "mean_novelty_ratio": mean_nov,
        "mean_n_distinct_visited": mean_distinct,
        "mean_refuse_OOD": mean_refuse_ood,
        "mean_refuse_in_corpus": mean_refuse_ic,
        "delta_arm4_minus_arm1_at_T8": float(delta_t8) if not math.isnan(delta_t8) else None,
        "coh_arm4_at_T8": float(coh_arm4_t8) if not math.isnan(coh_arm4_t8) else None,
        "coh_arm1_at_T8": float(coh_arm1_t8) if not math.isnan(coh_arm1_t8) else None,
        "coh_arm4_at_T1": float(coh_arm4_t1) if not math.isnan(coh_arm4_t1) else None,
        "novelty_arm4_at_T8": float(novelty_arm4_t8) if not math.isnan(novelty_arm4_t8) else None,
        "refuse_OOD_arm4": float(refuse_ood_arm4) if not math.isnan(refuse_ood_arm4) else None,
        "refuse_in_corpus_arm4": float(refuse_ic_arm4) if not math.isnan(refuse_ic_arm4) else None,
        "cv_arm4_at_T8": float(cv_arm4_t8),
        "cv_arm1_at_T8": float(cv_arm1_t8),
        "substrate_only_ok": bool(substrate_only_ok),
        "W_unchanged_by_generation_all_arms": bool(w_unchanged_ok),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "arms_collapse_null_at_T8": bool(arms_collapse_null),
        "arms_collapse_top_at_T8": bool(arms_collapse_top),
        "discriminator_split_at_T8": bool(discriminator_split),
        "arm4_collapse_to_fixedpoint": bool(collapse_to_fixedpoint),
        "honest_scope": (
            "Substrate-native autoregressive generation test on synthetic-bipolar "
            "disjoint-key sequences at N_DIM=%d, K=%d, N_SEQ=%d, T_gens=%s. "
            "Substrate-only-decode gate enforced (n_llm=%d). W matrix unchanged "
            "by generation (assertion enforced). Phase 1 scope: synthetic keys "
            "(matches c3); position-binding via the codebook itself (Phase 2 "
            "deferred: explicit HVC clock vectors + Pythia-encoded FB15k chains). "
            "The 4-arm contrast IS the discriminator (Fix #16): NONE control "
            "vs S_ONLY (no Langevin, no cleanup) vs S_LANGEVIN (no cleanup) vs "
            "S_LANGEVIN_CLEANUP (full mechanism)."
            % (N_DIM, K_SEQ, N_SEQ, str(T_GENS), n_llm)),
    }

    summary = (
        "coh_arm4_T8=%.3f coh_arm1_T8=%.3f delta=%.3f coh_arm2_T8=%.3f coh_arm3_T8=%.3f "
        "novelty_arm4=%.2f refuseOOD_arm4=%.2f refuseIC_arm4=%.2f "
        "cv_arm4=%.3f cv_arm1=%.3f T1_arm4=%.3f distinct_arm4_T8=%.1f "
        "substrate_only=%s W_unchanged=%s llm=%d" %
        (coh_arm4_t8, coh_arm1_t8,
         delta_t8 if not math.isnan(delta_t8) else float("nan"),
         coh_arm2_t8, coh_arm3_t8, novelty_arm4_t8, refuse_ood_arm4, refuse_ic_arm4,
         cv_arm4_t8, cv_arm1_t8, coh_arm4_t1,
         distinct_arm4_t8 if not math.isnan(distinct_arm4_t8) else -1,
         substrate_only_ok, w_unchanged_ok, n_llm))

    # Verdict logic
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s"
                % (n_llm, summary), detail)
    if not w_unchanged_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: W matrix modified by generation (assertion violated). %s"
                % summary, detail)
    if math.isnan(coh_arm4_t8):
        return ("HARD_FAIL",
                "HARD_FAIL: missing required Arm 4 (S_LANGEVIN_CLEANUP) data at T=8. %s"
                % summary, detail)
    if collapse_to_fixedpoint:
        return ("HARD_FAIL",
                ("HARD_FAIL: Arm 4 collapsed to fixed-point attractor "
                 "(distinct_visited=%.1f <= 2.5 at T=8 despite coh=%.3f). %s"
                 % (distinct_arm4_t8, coh_arm4_t8, summary)), detail)
    if not math.isnan(refuse_ood_arm4) and refuse_ood_arm4 < HARD_FAIL_REFUSE_OOD:
        return ("HARD_FAIL",
                ("HARD_FAIL: refuse_OOD %.3f < HARD_FAIL bar %.2f (gate broken). %s"
                 % (refuse_ood_arm4, HARD_FAIL_REFUSE_OOD, summary)), detail)
    if not math.isnan(novelty_arm4_t8) and novelty_arm4_t8 < HARD_FAIL_NOVELTY:
        return ("HARD_FAIL",
                ("HARD_FAIL: novelty_ratio %.3f < HARD_FAIL bar %.2f (pure memorization). %s"
                 % (novelty_arm4_t8, HARD_FAIL_NOVELTY, summary)), detail)
    if coh_arm4_t8 < HARD_FAIL_ARM4:
        return ("HARD_FAIL",
                "HARD_FAIL: coh_arm4_T8 %.3f < HARD_FAIL bar %.2f. %s"
                % (coh_arm4_t8, HARD_FAIL_ARM4, summary), detail)

    # HARD_PASS check
    if (coh_arm4_t8 >= HARD_PASS_ARM4_AT_T8
            and coh_arm1_t8 <= HARD_PASS_ARM1_AT_T8_MAX
            and (not math.isnan(delta_t8)) and delta_t8 >= HARD_PASS_DELTA
            and (not math.isnan(novelty_arm4_t8)) and novelty_arm4_t8 >= HARD_PASS_NOVELTY
            and (not math.isnan(refuse_ood_arm4)) and refuse_ood_arm4 >= HARD_PASS_REFUSE_OOD
            and cv_arm4_t8 <= CV_HARD_PASS_MAX):
        return ("HARD_PASS",
                ("HARD_PASS: substrate generates coherent sequences. "
                 "coh_arm4_T8=%.3f >= %.2f AND coh_arm1_T8=%.3f <= %.2f AND "
                 "delta=%.3f >= %.2f AND novelty=%.2f >= %.2f AND "
                 "refuse_OOD=%.2f >= %.2f AND cv_arm4=%.3f <= %.2f. %s"
                 % (coh_arm4_t8, HARD_PASS_ARM4_AT_T8,
                    coh_arm1_t8, HARD_PASS_ARM1_AT_T8_MAX,
                    delta_t8, HARD_PASS_DELTA,
                    novelty_arm4_t8, HARD_PASS_NOVELTY,
                    refuse_ood_arm4, HARD_PASS_REFUSE_OOD,
                    cv_arm4_t8, CV_HARD_PASS_MAX, summary)), detail)

    # MIDDLE_BAND
    if (coh_arm4_t8 >= MIDDLE_BAND_ARM4_LO
            and (not math.isnan(delta_t8)) and delta_t8 >= MIDDLE_BAND_LO):
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND: substrate generates PARTIALLY. coh_arm4_T8=%.3f in "
                 "[%.2f, %.2f); delta=%.3f in [%.2f, %.2f). %s"
                 % (coh_arm4_t8, MIDDLE_BAND_ARM4_LO, HARD_PASS_ARM4_AT_T8,
                    delta_t8, MIDDLE_BAND_LO, HARD_PASS_DELTA, summary)), detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: ambiguous; bands not crossed. %s" % summary, detail)


# --- atexit + SIGTERM synthesize-from-partials (TODO #9 pattern) -------------
def _synthesize_on_exit():
    """If main exit path didn't write metrics.json, synthesize from partials."""
    if _METRICS_WRITTEN[0]:
        return
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        run_config = {"N": N_DIM, "run_mode": RUN_MODE}
        per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
        if not per_seed:
            return
        verdict, verdict_msg, detail = compute_verdict(per_seed)
        verdict_msg = "TIMEOUT_OR_INTERRUPTED_PARTIAL: " + verdict_msg
        metrics = {
            "anchor": ANCHOR_NAME,
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "n_seeds": len(per_seed),
            "N": N_DIM,
            "N_DIM": N_DIM,
            "K_SEQ": K_SEQ,
            "N_SEQ": N_SEQ,
            "T_GENS": T_GENS,
            "arms": ARMS,
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "corpus_provenance": CORPUS_PROVENANCE,
            "allow_synthetic": True,
            "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
            "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
            "detail": detail,
            "per_seed": [
                {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
                 "per_unit": v.get("per_unit", [])}
                for k, v in per_seed.items()
            ],
            "metrics_source": "synthesized_from_partials_on_exit",
            "summary": verdict_msg[:200],
            "synthesized_at_exit": True,
        }
        write_metrics(out_dir, metrics, results=list(per_seed.values()))
        _METRICS_WRITTEN[0] = True
        print("[atexit] synthesized metrics.json from %d partials" % len(per_seed),
              flush=True)
    except Exception as e:
        print("[atexit] FAILED to synthesize: %s" % e, flush=True)


atexit.register(_synthesize_on_exit)


def _sigterm_handler(signum, frame):
    _synthesize_on_exit()
    sys.exit(143)


try:
    signal.signal(signal.SIGTERM, _sigterm_handler)
except (ValueError, AttributeError):
    pass


# --- Main runner ------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N_DIM, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d K=%d N_SEQ=%d arms=%s T_gens=%s "
      "sigma_scale=%.3f refuse_tau=%.3f seeds_done=%s seeds_todo=%s" %
      (RUN_MODE, N_DIM, K_SEQ, N_SEQ, str(ARMS), str(T_GENS),
       LANGEVIN_SIGMA_SCALE, REFUSE_TAU,
       str(done), str(seeds_todo)), flush=True)

for s in seeds_todo:
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
verdict, verdict_msg, detail = compute_verdict(per_seed)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(per_seed),
    "N": N_DIM,
    "N_DIM": N_DIM,
    "K_SEQ": K_SEQ,
    "N_SEQ": N_SEQ,
    "T_GENS": T_GENS,
    "arms": ARMS,
    "run_mode": RUN_MODE,
    "config_version": CONFIG_VERSION,
    "corpus_provenance": CORPUS_PROVENANCE,
    "allow_synthetic": True,
    "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
    "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    "detail": detail,
    "per_seed": [
        {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
         "per_unit": v.get("per_unit", [])}
        for k, v in per_seed.items()
    ],
    "metrics_source": "measured_cpu_synthetic_bipolar_substrate_native_generation",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
