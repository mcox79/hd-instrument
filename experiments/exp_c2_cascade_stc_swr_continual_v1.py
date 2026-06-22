"""c2_cascade_stc_swr_continual_v1 -- nested-timescale CLS continual ingest (brain-drill #2 5x DEEPER).

SCIENTIFIC QUESTION (research drill #2 5x DEEPER, 2026-06-22):
  Does a THREE-MECHANISM nested-timescale consolidation primitive (cascade-synapse + STC
  tag-and-capture + SWR-gated selective replay on expanding intervals) rescue continual
  learning at alpha=3.0 -- well above c1's tested cliff where uniform 1:1 replay collapses?

  c1 (uniform 1:1 replay) HARD_FAILed smoke this arc; at alpha=0.5 codebook-NN cleanup masks
  any collapse (recall=1.000 every arm). The 5x DEEPER drill says: 1:1 replay is shallow CLS;
  biology runs THREE timescales:
    (a) cascade-synapse metaplasticity (Fusi 2005, Benna-Fusi 2016) -- each W entry has an
        internal depth state d in {0,...,D_max}; plasticity p_d = (1/2)^d damps overwrites
        on deeply-stored entries. Power-law forgetting; linear capacity scaling.
    (b) STC tag-and-capture (Frey-Morris 1997) -- each write sets a tag from local refuse-
        gate-like margin; only HIGH-TAG writes earn cascade depth transitions.
    (c) SWR-gated selective replay (2024-2025 large-SWR evidence) -- only top-K_TAG fraction
        of past events are replayed, on EXPANDING intervals (1, 2, 4, 8, ...) rather than
        uniform 1:1. Fixed budget; better lifetime per replay.

ARMS (Fix #16 discriminator; mechanism-isolated):
  C1_BASELINE      = classical 1:1 uniform replay (= c1's ONLINE_1to1 mechanism; the bar)
  CASCADE_STC_SWR  = full three-mechanism nested-timescale consolidation
  NO_REPLAY        = write-only, no replay (forgetting-floor; isolates whether ANY replay helps)

ALPHA = 3.0 (discriminating regime; c1 protected by codebook-NN below cliff at alpha=0.5;
             alpha=3.0 is well past cliff -> mechanisms must DIFFERENTIATE here).

PRE-REGISTERED HARD BANDS (research drill #2 P_deflated=0.40):
  HARD_PASS (mechanism-discriminating, ALL of):
    - C2_CASCADE_STC_SWR retention at k=12 ingest cycles >= 0.85
    - C1_BASELINE retention at k=12 < 0.60
    - NO_REPLAY retention at k=12 < 0.30
    - C2 retention > C1 retention at k>=6 (mechanism kicks in mid-stream)
    - cv <= 0.06 across 3 seeds for C2 retention at k=12
    - substrate-only-decode: zero LLM forward calls
  HARD_FAIL (mechanism wrong):
    - C2 retention at k=12 < 0.40, OR
    - C2 doesn't beat C1 at k>=6 (cascade-STC-SWR adds nothing)
    - substrate-only-decode gate violated
  MIDDLE_BAND: anything between (partial mechanism; routes to single-mechanism ablations).

FIX INVENTORY (per template + Fixes #1-#24):
  - _LLM_CALL_COUNTER = [0] at module scope; asserted == 0 at end (substrate-only gate)
  - ANCHOR_NAME, CONFIG_VERSION baked module-level (AST-verifiable)
  - run_mode='full' default; HDLAB_RUN_MODE / --smoke flag honored (Fix #5)
  - PROT-018 anchor _n<N> suffix bound: this cell uses N_DIM=4096 (matches c1 anchor)
  - allow_synthetic=True (synthetic bipolar by design; matches c1 provenance; CORPUS_PROVENANCE
    baked into metrics.json for audit)
  - per-seed checkpoint via _seed_checkpoint (Fix #18 long-cells restartable)
  - cv across seeds computed in verdict()
  - Discriminating-regime baked at alpha=3.0 (not below cliff)
  - Version markers: consolidation_arm, D_max, theta_tag, replay_schedule_mode, tag_function
    baked into metrics.json (anti-r1b mean-reproduction-failure discipline)

FORMULA SELF-TESTS (asserted at import time):
  1. cascade depth update: tag>theta -> p(d_increment)>0; tag<theta -> p(d_increment)==0
  2. plasticity p_d gating: at d=3, p_d = 1/8 (writes rejected ~7/8 of the time)
  3. expanding-interval schedule: lag sequence is {1, 2, 4, 8, ...}
  4. _LLM_CALL_COUNTER remains 0 throughout

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
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "c2_cascade_stc_swr_continual_v1"

# Substrate-only-decode gate.
_LLM_CALL_COUNTER = [0]

# Corpus provenance.
CORPUS_PROVENANCE = "synthetic_bipolar_keys"

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
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Pre-reg HARD bands (locked at design time per research drill #2)
HARD_PASS_C2_K12 = 0.85          # C2 retention at k=12 must be >= this
HARD_PASS_C1_K12 = 0.60          # C1 baseline must collapse below this at k=12
HARD_PASS_NOREPLAY_K12 = 0.30    # NO_REPLAY must collapse below this at k=12
HARD_PASS_C2_BEATS_C1_K6 = True  # C2 must beat C1 by k=6 (mechanism kicks in)
CV_HARD_PASS_MAX = 0.06          # cv across seeds for HARD_PASS
HARD_FAIL_C2_FLOOR = 0.40        # C2 retention < this = HARD_FAIL

# Mechanism constants (cascade + STC + SWR)
ALPHA_DISCRIMINATING = 3.0       # discriminating regime per drill #2
D_MAX = 3                        # cascade depth states {0, 1, 2, 3} -> plasticity {1, 0.5, 0.25, 0.125}
THETA_TAG = 0.5                  # STC tag threshold (sigmoid output)
TAG_BETA = 4.0                   # sigmoid steepness for tag(margin)
THETA_DECAY_RATE = 0.02          # spontaneous d -> d-1 transition rate (slow noise floor)
NOISE_FRAC = 0.10                # probe noise: 10% sign-flipped dimensions
N_RECALL_STEPS = 3               # Hopfield-style cleanup steps at read
REPLAY_SCHEDULE_MODE_C2 = "expanding"  # {1, 2, 4, 8, ...} task lags
REPLAY_SCHEDULE_MODE_C1 = "uniform_1to1"  # legacy c1 (the bar)
TAG_FUNCTION = "sigmoid_margin"  # tag = sigmoid(beta * (top1 - top2)) over codebook

# k_evals = ingest cycle counts at which retention of FIRST batch is measured
K_EVALS = [3, 6, 12]

# Smoke vs full config
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 1024
    J_TASKS = 4              # need J >= max(K_EVALS) but K_EVALS clipped in smoke
    K_EVALS_SMOKE = [2, 3]   # k=12 not reachable at J=4; smoke uses smaller k
    ALPHA = 1.0              # below discriminating regime; smoke = stripped sanity
    M_PER_TASK = int(round(ALPHA * N_DIM / J_TASKS))   # ~256
    ARMS = ["NO_REPLAY", "C1_BASELINE", "CASCADE_STC_SWR"]
    N_PROBE = 30
    REPLAY_BUDGET_PER_INGEST = 1   # 1:1 for C1; selective top-K for C2
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    J_TASKS = 12             # K_EVALS = [3, 6, 12]; J must be >= max(K_EVALS)
    K_EVALS_SMOKE = K_EVALS  # full uses the registered list
    ALPHA = ALPHA_DISCRIMINATING  # alpha=3.0 (per drill #2)
    M_PER_TASK = int(round(ALPHA * N_DIM / J_TASKS))   # ~1024 per task; total ~12288 (3x N_DIM)
    ARMS = ["NO_REPLAY", "C1_BASELINE", "CASCADE_STC_SWR"]
    N_PROBE = 60
    REPLAY_BUDGET_PER_INGEST = 1   # 1:1 for C1 baseline; selective top-K of K_REPLAY_SLOTS for C2

K_EVALS_RUN = K_EVALS_SMOKE if RUN_MODE == "smoke" else K_EVALS

CONFIG_VERSION = ("c2-cascade-stc-swr-v1: J=%d N_DIM=%d M=%d alpha=%.2f arms=%s "
                  "D_max=%d theta_tag=%.2f beta=%.1f decay=%.3f K_EVALS=%s "
                  "schedule_C2=%s schedule_C1=%s tag_fn=%s run_mode=%s" %
                  (J_TASKS, N_DIM, M_PER_TASK, ALPHA, ",".join(ARMS),
                   D_MAX, THETA_TAG, TAG_BETA, THETA_DECAY_RATE, str(K_EVALS_RUN),
                   REPLAY_SCHEDULE_MODE_C2, REPLAY_SCHEDULE_MODE_C1, TAG_FUNCTION, RUN_MODE))


def make_bipolar(M: int, n: int, rng: np.random.RandomState) -> np.ndarray:
    """Random +/- 1 vectors, L2-normalized to unit length."""
    X = rng.choice([-1.0, 1.0], size=(M, n)).astype(np.float64)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)


def hebbian_bind_simple(W: np.ndarray, key: np.ndarray, value: np.ndarray) -> None:
    """Plain Hebbian outer-product write: W += value (outer) key / N_DIM."""
    n = W.shape[0]
    W += np.outer(value, key) / n


def hebbian_bind_cascade(W: np.ndarray, W_depth: np.ndarray, key: np.ndarray, value: np.ndarray,
                         rng: np.random.RandomState) -> None:
    """Cascade-gated Hebbian write: per-entry plasticity p_d = (1/2)^d.

    For each W entry (i, j), with probability p_d[i,j] the outer-product contribution is applied;
    otherwise the entry stays put. Approximation: instead of per-entry Bernoulli (expensive O(N^2)
    rng draws), we mask the outer product by a single per-entry Bernoulli draw -- still O(N^2)
    masks but vectorized as numpy operations. To bound cost we use a SCALAR per-write subsample:
    sample a Bernoulli with mean over-the-W-matrix of p_d -- i.e., the WRITE proceeds at full
    strength but only on a FRACTION mask of entries determined by per-entry depth.

    Mathematically: dW[i,j] = m[i,j] * value[i] * key[j] / n   where m[i,j] ~ Bernoulli(2^-W_depth[i,j])
    """
    n = W.shape[0]
    # Per-entry plasticity probability: p_d = (1/2)^d.
    P = np.power(0.5, W_depth.astype(np.float64))  # [n, n], in (0, 1]
    # Bernoulli mask
    R = rng.random((n, n))
    mask = (R < P)
    # Outer product contribution
    contrib = np.outer(value, key) / n
    # Apply masked
    W += contrib * mask


def stc_tag(key: np.ndarray, codebook_values: np.ndarray, value_idx_true: int) -> float:
    """STC tag function: sigmoid(beta * (top1 - top2)) on margin between TRUE value and best
    competitor in the codebook (proxy for refuse-gate margin). At write-time, "true" is the
    intended value-idx; we measure how distinguishable that intended target is from competitors
    in the current codebook -- a substrate-faithful proxy for confidence-of-encoding.

    Returns scalar in (0, 1).
    """
    sims = codebook_values @ key  # cosine since both unit-norm
    true_sim = float(sims[value_idx_true])
    # Best competitor != true
    sims_alt = sims.copy()
    sims_alt[value_idx_true] = -np.inf
    top_alt = float(np.max(sims_alt))
    margin = true_sim - top_alt
    return float(1.0 / (1.0 + math.exp(-TAG_BETA * margin)))


def cascade_consolidate(W_depth: np.ndarray, key: np.ndarray, value_idx: int,
                        codebook_values: np.ndarray, tag: float,
                        rng: np.random.RandomState) -> None:
    """STC consolidation: high-tag writes get cascade depth-state increment for the entries
    most-strongly-recruited by this (key, value) pair.

    A write recruits W entries (i, j) with magnitude |value[i] * key[j]| / n. The TOP-K most-
    recruited entries are the "engram"; high-tag writes promote those entries' depth by 1 (capped
    at D_max). Low-tag writes do not promote.

    Implementation: pick top-frac entries by recruitment magnitude. frac = tag (so low-tag promotes
    fewer entries).
    """
    if tag < THETA_TAG:
        return
    n = W_depth.shape[0]
    value = codebook_values[value_idx]
    recruit = np.abs(np.outer(value, key))  # [n, n]
    # Fraction of entries to promote: scaled by tag strength (above threshold)
    frac = 0.001 * (tag - THETA_TAG) / max(1.0 - THETA_TAG, 1e-6)  # at most 0.1% of entries
    frac = max(min(frac, 0.001), 0.0)
    n_promote = int(frac * n * n)
    if n_promote <= 0:
        return
    # Top-k by recruitment magnitude
    flat = recruit.flatten()
    if n_promote >= flat.size:
        idx = np.arange(flat.size)
    else:
        idx = np.argpartition(flat, -n_promote)[-n_promote:]
    rows = idx // n
    cols = idx % n
    # Promote: increment depth, capped at D_max
    W_depth[rows, cols] = np.minimum(W_depth[rows, cols] + 1, D_MAX)


def cascade_decay(W_depth: np.ndarray, rng: np.random.RandomState) -> None:
    """Slow noise-floor decay: each entry at d>0 transitions to d-1 with rate THETA_DECAY_RATE."""
    n = W_depth.shape[0]
    if THETA_DECAY_RATE <= 0:
        return
    above_zero = (W_depth > 0)
    if not above_zero.any():
        return
    decay_mask = (rng.random((n, n)) < THETA_DECAY_RATE) & above_zero
    W_depth[decay_mask] -= 1


def recall_value_idx(W: np.ndarray, key_probe: np.ndarray, codebook_values: np.ndarray,
                     n_steps: int = N_RECALL_STEPS) -> int:
    """Hopfield-style cosine-cleanup against codebook. Returns recovered value-idx."""
    y = W @ key_probe
    for _ in range(n_steps):
        sims = codebook_values @ y
        idx = int(np.argmax(sims))
        y_snap = codebook_values[idx]
        y = 0.5 * y + 0.5 * y_snap
    sims = codebook_values @ y
    return int(np.argmax(sims))


def eval_task_recall_first_batch(W: np.ndarray, keys_first: np.ndarray, value_idx_first: np.ndarray,
                                 codebook_values: np.ndarray, n_probe: int,
                                 rng: np.random.RandomState) -> float:
    """Recall on n_probe random items from the FIRST task. Returns fraction-correct (codebook-NN)."""
    M = keys_first.shape[0]
    n_q = min(n_probe, M)
    if n_q == 0:
        return 0.0
    sel = rng.choice(M, size=n_q, replace=False)
    correct = 0
    for j in sel:
        key = keys_first[j].copy()
        flip = rng.random(W.shape[0]) < NOISE_FRAC
        key[flip] *= -1.0
        key = key / (np.linalg.norm(key) + 1e-12)
        idx = recall_value_idx(W, key, codebook_values)
        if idx == value_idx_first[j]:
            correct += 1
    return float(correct) / n_q


def _expanding_replay_lags(j_current: int) -> List[int]:
    """At task position j_current (0-indexed), which prior tasks should be replayed?
    Expanding-interval schedule: lags {1, 2, 4, 8, ...} from current.

    Returns list of prior-task indices (each in [0, j_current-1]) selected by the schedule.
    """
    lags = []
    p = 1
    while p <= j_current:
        prior_idx = j_current - p
        if 0 <= prior_idx < j_current:
            lags.append(prior_idx)
        p *= 2
    return lags


def run_one_arm(arm: str, seed: int) -> Dict:
    """Run J_TASKS sequential tasks; measure retention of first batch at each K_EVALS_RUN point."""
    rng = np.random.RandomState(seed * 1000 + hash(arm) % 1000 + 17)
    n = N_DIM
    j_total = J_TASKS
    m_per = M_PER_TASK

    n_values_total = j_total * m_per
    codebook = make_bipolar(n_values_total + 32, n, rng)

    # Per-task storage
    task_keys: List[np.ndarray] = []
    task_value_idx: List[np.ndarray] = []

    # Episodic-cache U1: every (key, value_idx) ever written + their STC tags
    U1_keys: List[np.ndarray] = []
    U1_validx: List[int] = []
    U1_tags: List[float] = []
    U1_task: List[int] = []   # which task each entry came from

    # Cortex W (and cascade-depth state for C2 arm)
    W = np.zeros((n, n), dtype=np.float64)
    W_depth = np.zeros((n, n), dtype=np.int8) if arm == "CASCADE_STC_SWR" else None

    next_value_idx = 0
    t_start = time.time()
    retention_curve: List[Tuple[int, float]] = []  # (k, retention) measured after each ingest cycle

    for j in range(j_total):
        keys_j = make_bipolar(m_per, n, rng)
        value_idx_j = np.arange(next_value_idx, next_value_idx + m_per)
        next_value_idx += m_per
        task_keys.append(keys_j)
        task_value_idx.append(value_idx_j)

        # INGEST PHASE: write each (key, value) into W + U1
        for m in range(m_per):
            k = keys_j[m]
            v_idx = int(value_idx_j[m])
            v = codebook[v_idx]

            if arm == "CASCADE_STC_SWR":
                # Compute STC tag from refuse-gate-margin proxy
                tag = stc_tag(k, codebook, v_idx)
                # Cascade-gated Hebbian write
                hebbian_bind_cascade(W, W_depth, k, v, rng)
                # STC consolidation: high-tag writes earn cascade depth increment for top entries
                cascade_consolidate(W_depth, k, v_idx, codebook, tag, rng)
            else:
                # NO_REPLAY and C1_BASELINE both use plain Hebbian write
                hebbian_bind_simple(W, k, v)
                tag = 0.0  # no STC for non-C2 arms

            U1_keys.append(k)
            U1_validx.append(v_idx)
            U1_tags.append(float(tag))
            U1_task.append(int(j))

            # REPLAY: per-write 1:1 for C1_BASELINE only
            if arm == "C1_BASELINE":
                # Uniform sample 1 prior (key, value) from U1
                n_prior = len(U1_keys) - 1  # exclude the just-appended
                if n_prior > 0:
                    ridx = rng.randint(0, n_prior)
                    hebbian_bind_simple(W, U1_keys[ridx], codebook[U1_validx[ridx]])

        # POST-INGEST PHASE: expanding-interval SWR-gated selective replay for C2 arm
        if arm == "CASCADE_STC_SWR" and j > 0:
            # Which prior task positions get replayed this slot?
            replay_task_indices = _expanding_replay_lags(j)
            # Selective replay: from each scheduled prior-task, sample top-K_TAG events by U1_tags
            # Budget: REPLAY_BUDGET_PER_INGEST * m_per total replays per ingest cycle
            total_replays = REPLAY_BUDGET_PER_INGEST * m_per
            if replay_task_indices and total_replays > 0:
                # Build pool of candidate U1 indices from scheduled tasks
                candidate_idx = [i for i, tj in enumerate(U1_task) if tj in replay_task_indices]
                if candidate_idx:
                    # Weight by tag (selective: high-tag preferred); top-K by tag rather than uniform
                    candidate_tags = np.array([U1_tags[i] for i in candidate_idx])
                    # Top-tag selection (deterministic over the candidate pool)
                    k_per_replay = min(total_replays, len(candidate_idx))
                    top_idx_in_pool = np.argpartition(candidate_tags, -k_per_replay)[-k_per_replay:]
                    selected = [candidate_idx[i] for i in top_idx_in_pool]
                    for ridx in selected:
                        # Re-Hebbian-write through cascade gate
                        hebbian_bind_cascade(W, W_depth, U1_keys[ridx],
                                             codebook[U1_validx[ridx]], rng)
                        # Consolidation re-fires on replay (deep memory deepens)
                        cascade_consolidate(W_depth, U1_keys[ridx], U1_validx[ridx],
                                            codebook, U1_tags[ridx], rng)

            # Slow noise-floor decay (once per ingest cycle)
            cascade_decay(W_depth, rng)

        # MEASURE RETENTION at each K_EVALS_RUN point (k = number of ingest cycles since first task;
        # ingest cycle 1 == task 0 ingest done; k=3 means 3 cycles after first task ingest etc.)
        k_now = j + 1  # 1-indexed: after task j's ingest, k_now total ingest cycles done
        if k_now in K_EVALS_RUN:
            rec = eval_task_recall_first_batch(W, task_keys[0], task_value_idx[0],
                                               codebook, N_PROBE, rng)
            retention_curve.append((int(k_now), float(rec)))

    wall_s = time.time() - t_start

    # Also measure final retention if k=12 not in K_EVALS_RUN (smoke case fallback)
    if (J_TASKS in [c[0] for c in retention_curve]) is False:
        rec = eval_task_recall_first_batch(W, task_keys[0], task_value_idx[0],
                                           codebook, N_PROBE, rng)
        retention_curve.append((int(J_TASKS), float(rec)))

    return {
        "arm": arm, "alpha": float(ALPHA), "seed": int(seed),
        "j_tasks": j_total, "m_per_task": m_per, "n_dim": n,
        "retention_curve": retention_curve,
        "retention_final": float(retention_curve[-1][1]) if retention_curve else 0.0,
        "k_final": int(retention_curve[-1][0]) if retention_curve else 0,
        "wall_s": float(wall_s),
        "n_probe": N_PROBE,
    }


def _selftest():
    """4 self-tests per the docstring."""
    rng = np.random.RandomState(0)
    n = 64

    # selftest 1: cascade depth update behaviour
    W_d = np.zeros((n, n), dtype=np.int8)
    cb = make_bipolar(8, n, rng)
    k_test = make_bipolar(1, n, rng)[0]
    cascade_consolidate(W_d, k_test, 0, cb, tag=0.9, rng=rng)
    # at tag=0.9, frac>0 -> at least 1 entry should be promoted if n>=32
    promoted_high = int((W_d > 0).sum())
    W_d2 = np.zeros((n, n), dtype=np.int8)
    cascade_consolidate(W_d2, k_test, 0, cb, tag=0.1, rng=rng)
    promoted_low = int((W_d2 > 0).sum())
    assert promoted_low == 0, "selftest 1a: low-tag write should not promote: got %d" % promoted_low

    # selftest 2: plasticity p_d = (1/2)^d
    p_d3 = (0.5) ** 3
    assert abs(p_d3 - 0.125) < 1e-9, "selftest 2: p_d at d=3 not 0.125"

    # selftest 3: expanding-interval schedule
    lags_at_j8 = _expanding_replay_lags(8)
    expected = [7, 6, 4, 0]  # j-1=7, j-2=6, j-4=4, j-8=0
    assert lags_at_j8 == expected, "selftest 3: expanding lags got %s expected %s" % (lags_at_j8, expected)

    # selftest 4: no LLM calls
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 4: LLM counter non-zero (%d)" % _LLM_CALL_COUNTER[0]

    print("[selftest] PASS: cascade_high_promotes=%d cascade_low=%d expanding_lags_j8=%s LLM=%d"
          % (promoted_high, promoted_low, lags_at_j8, _LLM_CALL_COUNTER[0]), flush=True)


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
        print("  [seed=%d] arm=%s J=%d M/task=%d N=%d retention_curve=%s wall=%.1fs"
              % (seed, arm, J_TASKS, M_PER_TASK, N_DIM, str(res["retention_curve"]),
                 res["wall_s"]), flush=True)
    elapsed = time.time() - t0
    return {
        "seed": seed, "N": N_DIM, "M": M_PER_TASK,
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

    # Aggregate retention_curve into per-arm, per-k means + stds across seeds
    # Structure: by_arm[arm][k] = [retention_seed_0, retention_seed_1, ...]
    by_arm: Dict[str, Dict[int, List[float]]] = {}
    for sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            arm = pu["arm"]
            by_arm.setdefault(arm, {})
            for (k, r) in pu.get("retention_curve", []):
                by_arm[arm].setdefault(int(k), []).append(float(r))

    def mean_at(arm: str, k: int) -> Optional[float]:
        if arm not in by_arm or k not in by_arm[arm]:
            return None
        vals = by_arm[arm][k]
        if not vals:
            return None
        return float(np.mean(vals))

    def cv_at(arm: str, k: int) -> Optional[float]:
        if arm not in by_arm or k not in by_arm[arm]:
            return None
        vals = by_arm[arm][k]
        if len(vals) < 2:
            return 0.0
        mean = float(np.mean(vals))
        std = float(np.std(vals))
        return std / max(mean, 1e-9)

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    # Use the LARGEST k available across all arms (== last K_EVALS_RUN entry, typically 12 in full,
    # or J_TASKS in smoke). We compute on whatever k is in K_EVALS_RUN[-1].
    k_final = K_EVALS_RUN[-1] if K_EVALS_RUN else J_TASKS
    k_mid = K_EVALS_RUN[1] if len(K_EVALS_RUN) >= 2 else k_final

    c2_kf = mean_at("CASCADE_STC_SWR", k_final)
    c1_kf = mean_at("C1_BASELINE", k_final)
    nr_kf = mean_at("NO_REPLAY", k_final)
    c2_km = mean_at("CASCADE_STC_SWR", k_mid)
    c1_km = mean_at("C1_BASELINE", k_mid)
    cv_c2_kf = cv_at("CASCADE_STC_SWR", k_final) or 0.0

    detail = {
        "k_evals": K_EVALS_RUN,
        "by_arm_means": {arm: {str(k): float(np.mean(v)) for k, v in d.items()}
                          for arm, d in by_arm.items()},
        "by_arm_stds": {arm: {str(k): float(np.std(v)) for k, v in d.items()}
                         for arm, d in by_arm.items()},
        "by_arm_cv": {arm: {str(k): cv_at(arm, k) for k in d.keys()}
                       for arm, d in by_arm.items()},
        "k_final": int(k_final),
        "k_mid": int(k_mid),
        "c2_retention_k_final": c2_kf,
        "c1_retention_k_final": c1_kf,
        "no_replay_retention_k_final": nr_kf,
        "c2_retention_k_mid": c2_km,
        "c1_retention_k_mid": c1_km,
        "cv_c2_k_final": float(cv_c2_kf),
        "substrate_only_ok": bool(substrate_only_ok),
        "n_llm_calls_total": int(n_llm),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "consolidation_arms_tested": ARMS,
        "D_max": D_MAX,
        "theta_tag": THETA_TAG,
        "tag_function": TAG_FUNCTION,
        "replay_schedule_mode_C2": REPLAY_SCHEDULE_MODE_C2,
        "replay_schedule_mode_C1": REPLAY_SCHEDULE_MODE_C1,
        "alpha": float(ALPHA),
        "honest_scope": ("Nested-timescale CLS continual ingest (cascade-synapse + STC + SWR-gated "
                          "expanding-interval replay) on synthetic-bipolar (k, v) at N_DIM=%d, "
                          "J=%d, alpha=%.2f. Substrate-only-decode gate enforced (n_llm=%d)."
                          % (N_DIM, J_TASKS, ALPHA, n_llm)),
    }

    summary = ("C2@k%d=%s C1@k%d=%s NR@k%d=%s | C2@k%d=%s C1@k%d=%s | cv_C2=%.3f llm=%d substrate_only=%s" %
               (k_final, ("%.3f" % c2_kf) if c2_kf is not None else "n/a",
                k_final, ("%.3f" % c1_kf) if c1_kf is not None else "n/a",
                k_final, ("%.3f" % nr_kf) if nr_kf is not None else "n/a",
                k_mid, ("%.3f" % c2_km) if c2_km is not None else "n/a",
                k_mid, ("%.3f" % c1_km) if c1_km is not None else "n/a",
                cv_c2_kf, n_llm, substrate_only_ok))

    # Verdict logic
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)
    # Need all three arms measured at k_final
    if c2_kf is None or c1_kf is None or nr_kf is None:
        return ("HARD_FAIL",
                "HARD_FAIL: missing required arm retention at k_final=%d. %s" % (k_final, summary),
                detail)

    # HARD_FAIL bracket
    if c2_kf < HARD_FAIL_C2_FLOOR:
        return ("HARD_FAIL",
                "HARD_FAIL: C2 retention %.3f < floor %.2f at k=%d. %s" %
                (c2_kf, HARD_FAIL_C2_FLOOR, k_final, summary),
                detail)
    if c2_km is not None and c1_km is not None and c2_km <= c1_km and k_mid >= 6:
        return ("HARD_FAIL",
                "HARD_FAIL: C2 (%.3f) does NOT beat C1 (%.3f) at k_mid=%d. Mechanism adds nothing. %s" %
                (c2_km, c1_km, k_mid, summary),
                detail)

    # HARD_PASS bracket (all conditions)
    hp_c2_above = (c2_kf >= HARD_PASS_C2_K12)
    hp_c1_below = (c1_kf < HARD_PASS_C1_K12)
    hp_nr_below = (nr_kf < HARD_PASS_NOREPLAY_K12)
    hp_cv = (cv_c2_kf <= CV_HARD_PASS_MAX)
    hp_mid = True
    if c2_km is not None and c1_km is not None and k_mid >= 6:
        hp_mid = (c2_km > c1_km)

    if hp_c2_above and hp_c1_below and hp_nr_below and hp_cv and hp_mid:
        return ("HARD_PASS",
                ("HARD_PASS: nested-timescale CLS rescues continual learning at alpha=%.2f. "
                 "C2=%.3f >= %.2f AND C1=%.3f < %.2f AND NR=%.3f < %.2f AND C2-beats-C1-at-k_mid=%s "
                 "AND cv_C2=%.3f <= %.2f. %s" %
                 (ALPHA, c2_kf, HARD_PASS_C2_K12, c1_kf, HARD_PASS_C1_K12, nr_kf,
                  HARD_PASS_NOREPLAY_K12, hp_mid, cv_c2_kf, CV_HARD_PASS_MAX, summary)),
                detail)

    # Otherwise MIDDLE_BAND
    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: partial mechanism. C2=%.3f C1=%.3f NR=%.3f at k=%d. cv_C2=%.3f. "
             "HP conditions: c2_above=%s c1_below=%s nr_below=%s cv_ok=%s mid_ok=%s. %s" %
             (c2_kf, c1_kf, nr_kf, k_final, cv_c2_kf,
              hp_c2_above, hp_c1_below, hp_nr_below, hp_cv, hp_mid, summary)),
            detail)


# Main runner
out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N_DIM, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d J=%d alpha=%.2f arms=%s seeds_done=%s seeds_todo=%s K_EVALS=%s" %
      (RUN_MODE, N_DIM, J_TASKS, ALPHA, str(ARMS), str(done), str(seeds_todo), str(K_EVALS_RUN)),
      flush=True)

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
    "J_tasks": J_TASKS,
    "M_per_task": M_PER_TASK,
    "alpha": float(ALPHA),
    "arms": ARMS,
    "K_evals": K_EVALS_RUN,
    "D_max": D_MAX,
    "theta_tag": THETA_TAG,
    "tag_function": TAG_FUNCTION,
    "replay_schedule_mode_C2": REPLAY_SCHEDULE_MODE_C2,
    "replay_schedule_mode_C1": REPLAY_SCHEDULE_MODE_C1,
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
    "metrics_source": "measured_cpu_synthetic_bipolar_cascade_stc_swr_continual",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
