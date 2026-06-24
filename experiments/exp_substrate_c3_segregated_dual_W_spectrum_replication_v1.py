"""substrate_c3_segregated_dual_W_spectrum_replication_v1 -- segregated dual-W CL test.

SCIENTIFIC QUESTION:
  Does SPATIAL SEGREGATION of the CL update operator (cortex + hippocampus on
  SEPARATE W matrices, with ONE-WAY replay coupling) rescue the
  exp_substrate_continual_learning_spectrum_v1 HARD_FAIL (forgetting_p1=0.65,
  transfer=0.000 at alpha=0.49)? The CL spectrum cell HARD_FAILed because
  cf-RPE delta-rule + Hebbian replay are antagonistic when applied to the SAME
  W matrix (smoke-calibration comment in cl-spectrum source, lines 168-181).
  The brain solves this via spatially-segregated cortex (hippocampal Hebbian
  write + cortical slow consolidation; no shared update operator).

STRATEGIC RATIONALE:
  Substrate's competitive CL moat depends on architectural composition. CL
  spectrum HARD_FAIL diagnosed as composition-architecture (not primitive-
  absence). This cell tests if a SEGREGATED dual-W architecture rescues the
  spectrum HARD_FAIL while keeping every other variable identical to the
  apples-to-apples spectrum cell harness.

5 ARMS (same protocol as cl-spectrum; ONLY the CL operator architecture varies):
  ARM_BASELINE_STATIC               -- spectrum sanity control; train Phase 1
                                        only; freeze; no CL ops. Reproduces
                                        cl-spectrum BASELINE within +/- 0.05.
  ARM_DISCRETE_ADD                  -- spectrum sanity control; naive online
                                        Hebbian write per phase; no replay,
                                        no cf-RPE, no slow consolidation.
                                        Reproduces cl-spectrum DISCRETE within
                                        +/- 0.05.
  ARM_FUSED_W_CFRPE_HEBBIAN         -- reproduces cl-spectrum FULL_CL HARD_FAIL
                                        regime: cf-RPE delta-rule AND Hebbian
                                        replay both applied to a SINGLE shared
                                        W. Expected forgetting=0.65 within
                                        +/- 0.10. HARNESS-ARTIFACT control.
  ARM_SEGREGATED_DUAL_W_NAIVE       -- DUAL W: W_cortex + W_hippocampus.
                                        cf-RPE on W_cortex only. Hebbian writes
                                        on W_hippocampus only. NO coupling
                                        between them. Recall reads from
                                        W_cortex. Tests segregation alone.
  ARM_SEGREGATED_DUAL_W_ONE_WAY_REPLAY -- PRIMARY arm. DUAL W as in ARM 4 +
                                        SCHEDULED one-way replay: between
                                        phases, W_hippocampus samples
                                        recency-weighted episodic buffer and
                                        Hebbian-writes those samples into
                                        W_cortex at ALPHA_SLOW. cf-RPE stays
                                        on W_cortex only; Hebbian-fast stays
                                        on W_hippocampus only. NO read from
                                        W_hippocampus (cortex is read-out;
                                        hippocampus is write-buffer + replay
                                        source). Tests brain-grounded CLS.

APPLES-TO-APPLES (matches exp_substrate_continual_learning_spectrum_v1):
  Same J=5, M=400, N_DIM=4096, alpha_total=0.488, 3 seeds, same probe
  protocol (N_PROBE=60, NOISE_FRAC=0.20, N_RETRIEVE_STEPS=5), same metrics
  (forgetting_p1, transfer_final), same synthetic-bipolar atoms per domain
  permutation, same RECENCY_WEIGHT=4.0, same N_REPLAY_PASSES=10,
  same N_CFRPE_PASSES=5. ONLY the architecture (single-W vs dual-W) and
  the replay direction (none vs scheduled hippo->cortex) vary.

  Lane 1: substrate-native CL architecture comparison.
  Apples-to-apples confound audit: dual-W matrix-size matched to single-W
  (each W is N_DIM x N_DIM); replay schedule identical to spectrum CLS.
  INTRA_LANE_DELTA: ARM 4 vs ARM 5 varies ONE thing (one-way replay on/off).

PRE-REGISTERED HARD BANDS:
  Sanity rails:
    ARM_BASELINE_STATIC phase-1 initial recall in [0.85, 1.00]
    ARM_FUSED_W_CFRPE_HEBBIAN forgetting_p1 in [0.55, 0.75]
      (reproduces cl-spectrum HARD_FAIL within +/- 0.10 of 0.65;
       verifies harness is not measurement-artifact)

  HARD_PASS_CL_MOAT_REAL (primary; segregated architecture rescues CL):
    ARM_SEGREGATED_DUAL_W_ONE_WAY_REPLAY forgetting_p1 < 0.20
    AND transfer > 0.30
    AND delta vs ARM_FUSED_W >= 0.40
    Interpretation: substrate has a REAL CL moat via brain-grounded
    architectural segregation; closes cl-spectrum HARD_FAIL.

  HARD_PASS_PARTIAL (some improvement but not full moat):
    ARM_SEGREGATED_DUAL_W_ONE_WAY_REPLAY forgetting_p1 in [0.20, 0.50]
    AND delta vs ARM_FUSED_W >= 0.15

  HARD_FAIL_DECISIVE (segregation does not fix CL spectrum):
    ARM_SEGREGATED_DUAL_W_ONE_WAY_REPLAY forgetting_p1 >= 0.50
    OR delta vs ARM_FUSED_W < 0.15
    Interpretation: deeper architectural redesign needed; segregation alone
    insufficient; route to research for next-mechanism scour.

  MIDDLE_BAND: characterized but doesn't clear HARD_PASS_PARTIAL.

  cv (across-seed std/mean of primary metric) < 0.05 required for cert tier.

WHAT_THIS_DOES_NOT_SHOW:
  - NOT a transformer fine-tuning comparison.
  - NOT cross-CORPUS continual learning (synthetic bipolar atoms per domain).
  - NOT a measurement of BPC; substrate-native recall accuracy.
  - NOT a K-bank routing test (ARM_FULL_CL_SYSTEM from cl-spectrum used K=2;
    this cell drops K-banks to isolate the segregation lever).
  - NOT a head-to-head with the cl-spectrum FULL_CL_SYSTEM K=2 arm; FUSED_W
    in this cell uses single-bank fused-W to isolate the architectural lever.

PROT-018: anchor has no _n<N> suffix; N_DIM=4096 encoded in config and asserted.
PROT-019: N>=4096 anchor; timeout floor >= 3600s (set to 5400s with safety).
PROT-021: imports _seed_checkpoint; per-seed partials.

FORMULA SELF-TESTS:
  1. Sign-flip retrieval clean-probe -> recall=1.0 (Hebbian works)
  2. Single-phase no-CL Hebbian on small-N >= 0.95 (sanity)
  3. cf-RPE from W=0 must learn target patterns (delta-rule works)
  4. Total alpha_total = (J*M)/N_DIM in CL regime (> 0.10; for full >= 0.40)
  5. ARM 5 dual-W invariant: W_cortex and W_hippocampus are distinct objects
     (id check) and have correct shape (N_DIM, N_DIM).

TIMEOUT ESTIMATE:
  Smoke (J=3, M=200, N=4096, 2 seeds): expect ~ 70-110s wall (5 arms x phases).
  Full (J=5, M=400, N=4096, 3 seeds): expect ~ 1000-1800s wall (segregated
    arms have ~2x flops of single-W arms because TWO W's are written per
    phase + replay). PROT-019 floor 3600s; safety 1.5x -> 5400s. Use 5400s.

Cites:
  experiments/exp_substrate_continual_learning_spectrum_v1.py (apples-to-apples base)
  experiments/exp_two_substrate_fastslow_cls_cpu_v1.py (substrate dual-store primitive)
  experiments/exp_hippocampal_nonrecip_replay_v1.py (non-reciprocal replay primitive)
  notes/exp_dev_handoff_research_continual_learning_architectural_revival_2x_drill_2026-06-24.md
  preregs/2026-06-24_substrate_c3_segregated_dual_W_spectrum_replication_v1.md

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
import argparse
import math
import time
import json
import atexit
from pathlib import Path
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "substrate_c3_segregated_dual_W_spectrum_replication_v1"

# ----------------------------------------------------------------------------
# Argparse + run-mode
# ----------------------------------------------------------------------------
_P = argparse.ArgumentParser()
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# ----------------------------------------------------------------------------
# Config (apples-to-apples with exp_substrate_continual_learning_spectrum_v1)
# ----------------------------------------------------------------------------
N_DIM = 4096                # production scale; PROT-018 _n is implicit (no suffix)

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    J_PHASES = 3
    M_PER_PHASE = 200
    NOISE_FRAC = 0.20
    N_PROBE = 20
    N_RETRIEVE_STEPS = 5
    N_REPLAY_PASSES = 5
    N_CFRPE_PASSES = 3
else:
    SEEDS = [7, 17, 23]
    J_PHASES = 5
    M_PER_PHASE = 400
    NOISE_FRAC = 0.20
    N_PROBE = 60
    N_RETRIEVE_STEPS = 5
    N_REPLAY_PASSES = 10
    N_CFRPE_PASSES = 5

# Shared CL primitive knobs (mirror spectrum cell exactly)
ALPHA_FAST = 1.0            # Hebbian fast-write strength (hippocampus)
ALPHA_SLOW = 0.1            # Cortex slow-write strength (replayed)
ALPHA_CFRPE = 0.05          # cf-RPE delta-rule step (cortex error-correction)
RECENCY_WEIGHT = 4.0        # CLS replay recency bias
# K_BANKS not used in this cell; isolating the segregation lever

ARMS = [
    "ARM_BASELINE_STATIC",
    "ARM_DISCRETE_ADD",
    "ARM_FUSED_W_CFRPE_HEBBIAN",
    "ARM_SEGREGATED_DUAL_W_NAIVE",
    "ARM_SEGREGATED_DUAL_W_ONE_WAY_REPLAY",
]
PRIMARY_ARM = "ARM_SEGREGATED_DUAL_W_ONE_WAY_REPLAY"
HARNESS_CONTROL_ARM = "ARM_FUSED_W_CFRPE_HEBBIAN"

# ----------------------------------------------------------------------------
# Pre-reg bands
# ----------------------------------------------------------------------------
# Sanity rails
SANITY_RAIL_LO = 0.85          # baseline phase-1 initial recall lower bound
SANITY_RAIL_HI = 1.00          # baseline phase-1 initial recall upper bound
HARNESS_FORGET_LO = 0.55       # FUSED_W must reproduce cl-spectrum HARD_FAIL
HARNESS_FORGET_HI = 0.75       # within +/- 0.10 of 0.65

# Primary: HARD_PASS_CL_MOAT_REAL
HP_REAL_FORGETTING_MAX = 0.20
HP_REAL_TRANSFER_MIN = 0.30
HP_REAL_DELTA_VS_FUSED = 0.40

# Secondary: HARD_PASS_PARTIAL
HP_PARTIAL_FORGETTING_MAX = 0.50
HP_PARTIAL_DELTA_VS_FUSED = 0.15

# HARD_FAIL_DECISIVE
HF_FORGETTING_MIN = 0.50
HF_DELTA_VS_FUSED_MAX = 0.15

# ----------------------------------------------------------------------------
# Formula self-tests at import time (PROT-021)
# ----------------------------------------------------------------------------
assert N_DIM == 4096, f"PROT-021: N_DIM={N_DIM}"
ALPHA_TOTAL = (J_PHASES * M_PER_PHASE) / N_DIM
print(f"[formula_selftest] N_DIM={N_DIM} J={J_PHASES} M={M_PER_PHASE} alpha_total={ALPHA_TOTAL:.4f}", flush=True)
assert ALPHA_TOTAL > 0.10, f"alpha_total too low to see forgetting: {ALPHA_TOTAL}"
if RUN_MODE == "full":
    assert ALPHA_TOTAL >= 0.40, f"full-run alpha_total must push past cliff: {ALPHA_TOTAL}"

# ----------------------------------------------------------------------------
# Helpers (apples-to-apples copies from spectrum cell)
# ----------------------------------------------------------------------------
def make_phase_atoms(m: int, n_dim: int, seed: int, phase_idx: int) -> np.ndarray:
    """M bipolar (+/-1) atoms for a phase. SAME seed scheme as spectrum cell."""
    rng = np.random.RandomState(seed * 1000 + phase_idx * 17)
    Xi = rng.choice([-1.0, 1.0], size=(m, n_dim)).astype(np.float32)
    return Xi


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = N_RETRIEVE_STEPS) -> np.ndarray:
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h).astype(np.float32)
        state[state == 0] = 1.0
    return state


def eval_phase_recall(W: np.ndarray, Xi_phase: np.ndarray, n_probe: int,
                      noise_frac: float, rng: np.random.RandomState) -> float:
    """Fraction of probes that retrieve cosine > 0.80 of original."""
    m = Xi_phase.shape[0]
    n_dim = Xi_phase.shape[1]
    n_q = min(n_probe, m)
    correct = 0
    for i in range(n_q):
        xi = Xi_phase[i]
        probe = xi.copy()
        flip = rng.random(n_dim) < noise_frac
        probe[flip] *= -1.0
        ret = hopfield_retrieve(W, probe)
        cos = float(np.dot(ret, xi) / n_dim)
        if cos > 0.80:
            correct += 1
    return correct / n_q if n_q > 0 else 0.0


def hebbian_write(W: np.ndarray, Xi: np.ndarray, alpha: float, n_dim: int) -> int:
    W += (alpha * (Xi.T @ Xi) / float(n_dim)).astype(np.float32)
    m = Xi.shape[0]
    return int(2 * m * n_dim * n_dim + n_dim * n_dim)


def cfrpe_update(W: np.ndarray, Xi: np.ndarray, alpha: float, n_dim: int,
                 n_passes: int) -> int:
    """cf-RPE delta-rule: error-driven update on the SAME W. Returns flops."""
    m = Xi.shape[0]
    flops = 0
    for _pass in range(n_passes):
        pred = W @ Xi.T  # (N, M)
        flops += 2 * n_dim * n_dim * m
        signed = np.sign(pred).astype(np.float32)
        signed[signed == 0] = 1.0
        err = Xi.T - signed
        W += (alpha * (err @ Xi) / float(n_dim)).astype(np.float32)
        flops += 2 * n_dim * m * n_dim + n_dim * n_dim
    return int(flops)


def cls_replay_from_buffer(W_target: np.ndarray, buffer_atoms: List[np.ndarray],
                            buffer_phase_ids: List[int], current_phase: int,
                            alpha_per_pass: float, n_passes: int,
                            recency_weight: float, m_per_pass: int,
                            rng: np.random.RandomState, n_dim: int) -> int:
    """CLS replay: sample recency-weighted from buffer; Hebbian-write into W_target.
    Returns flops estimate. Identical schedule to spectrum cell's CLS_REPLAY.
    """
    if not buffer_atoms:
        return 0
    buf_arr = np.stack(buffer_atoms, axis=0)
    n_buf = buf_arr.shape[0]
    weights = np.array(
        [recency_weight ** (current_phase - p) for p in buffer_phase_ids],
        dtype=np.float64,
    )
    weights = weights / weights.sum()
    n_per_pass = min(m_per_pass, n_buf)
    flops = 0
    for _pass in range(n_passes):
        idx = rng.choice(n_buf, size=n_per_pass, replace=False, p=weights)
        Xi_replay = buf_arr[idx]
        flops += hebbian_write(W_target, Xi_replay, alpha_per_pass, n_dim)
    return flops


# ----------------------------------------------------------------------------
# Arms
# ----------------------------------------------------------------------------
def run_arm_baseline_static(seed: int) -> Dict:
    """Train Phase 1 only; freeze. Sanity control."""
    rng = np.random.RandomState(seed + 100)
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    phase_atoms: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    flops_total = 0
    t0 = time.time()
    for i in range(J_PHASES):
        Xi_i = make_phase_atoms(M_PER_PHASE, N_DIM, seed, i)
        phase_atoms.append(Xi_i)
        if i == 0:
            flops_total += hebbian_write(W, Xi_i, ALPHA_FAST, N_DIM)
        recalls_after_i = []
        for j in range(i + 1):
            rec = eval_phase_recall(W, phase_atoms[j], N_PROBE, NOISE_FRAC, rng)
            recalls_after_i.append(rec)
        phase_recalls.append(recalls_after_i)
        print(f"  [seed={seed} BASELINE phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]}", flush=True)
    return {
        "arm": "ARM_BASELINE_STATIC",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "flops_total": flops_total,
        "n_atoms_written": M_PER_PHASE,
        "elapsed_s": time.time() - t0,
        "w_norm_final": float(np.linalg.norm(W)),
    }


def run_arm_discrete_add(seed: int) -> Dict:
    """Naive online Hebbian write per phase; catastrophic-forgetting baseline."""
    rng = np.random.RandomState(seed + 200)
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    phase_atoms: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    flops_total = 0
    n_atoms_total = 0
    t0 = time.time()
    for i in range(J_PHASES):
        Xi_i = make_phase_atoms(M_PER_PHASE, N_DIM, seed, i)
        phase_atoms.append(Xi_i)
        flops_total += hebbian_write(W, Xi_i, ALPHA_FAST, N_DIM)
        n_atoms_total += M_PER_PHASE
        recalls_after_i = []
        for j in range(i + 1):
            rec = eval_phase_recall(W, phase_atoms[j], N_PROBE, NOISE_FRAC, rng)
            recalls_after_i.append(rec)
        phase_recalls.append(recalls_after_i)
        print(f"  [seed={seed} DISCRETE phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]}", flush=True)
    return {
        "arm": "ARM_DISCRETE_ADD",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "flops_total": flops_total,
        "n_atoms_written": n_atoms_total,
        "elapsed_s": time.time() - t0,
        "w_norm_final": float(np.linalg.norm(W)),
    }


def run_arm_fused_w_cfrpe_hebbian(seed: int) -> Dict:
    """SINGLE W taking BOTH cf-RPE delta-rule AND Hebbian replay (cl-spectrum
    FULL_CL collapse regime; reproduces forgetting~0.65 HARD_FAIL).
    Per phase: Hebbian-write current -> CLS replay (Hebbian into same W) ->
    cf-RPE error-correction on current phase. Same W absorbs all three.
    """
    rng = np.random.RandomState(seed + 300)
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    episodic_buffer: List[np.ndarray] = []
    episodic_phase_ids: List[int] = []
    phase_atoms: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    flops_total = 0
    n_atoms_total = 0
    t0 = time.time()
    alpha_per_pass = ALPHA_SLOW / float(N_REPLAY_PASSES)
    for i in range(J_PHASES):
        Xi_i = make_phase_atoms(M_PER_PHASE, N_DIM, seed, i)
        phase_atoms.append(Xi_i)
        for x in Xi_i:
            episodic_buffer.append(x)
            episodic_phase_ids.append(i)
        # 1. Hebbian-fast write of current phase -> W
        flops_total += hebbian_write(W, Xi_i, ALPHA_FAST, N_DIM)
        # 2. CLS replay -> same W (this is where antagonism with cf-RPE arises)
        flops_total += cls_replay_from_buffer(
            W, episodic_buffer, episodic_phase_ids, i,
            alpha_per_pass, N_REPLAY_PASSES, RECENCY_WEIGHT,
            M_PER_PHASE, rng, N_DIM,
        )
        # 3. cf-RPE on current phase -> same W (delta-rule conflicts with Hebbian)
        flops_total += cfrpe_update(W, Xi_i, ALPHA_CFRPE, N_DIM, N_CFRPE_PASSES)
        n_atoms_total += M_PER_PHASE
        recalls_after_i = []
        for j in range(i + 1):
            rec = eval_phase_recall(W, phase_atoms[j], N_PROBE, NOISE_FRAC, rng)
            recalls_after_i.append(rec)
        phase_recalls.append(recalls_after_i)
        print(f"  [seed={seed} FUSED_W phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]}", flush=True)
    return {
        "arm": "ARM_FUSED_W_CFRPE_HEBBIAN",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "flops_total": flops_total,
        "n_atoms_written": n_atoms_total,
        "elapsed_s": time.time() - t0,
        "w_norm_final": float(np.linalg.norm(W)),
    }


def run_arm_segregated_dual_w_naive(seed: int) -> Dict:
    """DUAL W (W_cortex + W_hippocampus). cf-RPE on cortex only. Hebbian
    writes on hippocampus only. NO COUPLING between them. Recall from cortex.

    The hippocampus accumulates Hebbian-fast writes (every phase, every atom)
    but nothing replays into the cortex. The cortex receives only cf-RPE on
    the CURRENT phase's atoms (no prior-phase exposure). Expectation: cortex
    has only "last-phase-cf-RPE" memory; severe forgetting expected (this is
    the segregation-without-replay control showing segregation alone is
    insufficient -- replay is the rescue lever).
    """
    rng = np.random.RandomState(seed + 400)
    W_cortex = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    W_hippocampus = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    phase_atoms: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    flops_total = 0
    n_atoms_total = 0
    t0 = time.time()
    for i in range(J_PHASES):
        Xi_i = make_phase_atoms(M_PER_PHASE, N_DIM, seed, i)
        phase_atoms.append(Xi_i)
        # Hebbian-fast -> W_hippocampus (write-buffer)
        flops_total += hebbian_write(W_hippocampus, Xi_i, ALPHA_FAST, N_DIM)
        # cf-RPE -> W_cortex (no Hebbian on cortex, no replay coupling)
        flops_total += cfrpe_update(W_cortex, Xi_i, ALPHA_CFRPE, N_DIM, N_CFRPE_PASSES)
        n_atoms_total += M_PER_PHASE
        recalls_after_i = []
        for j in range(i + 1):
            # Read from cortex only
            rec = eval_phase_recall(W_cortex, phase_atoms[j], N_PROBE, NOISE_FRAC, rng)
            recalls_after_i.append(rec)
        phase_recalls.append(recalls_after_i)
        print(f"  [seed={seed} DUAL_W_NAIVE phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]}", flush=True)
    return {
        "arm": "ARM_SEGREGATED_DUAL_W_NAIVE",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "flops_total": flops_total,
        "n_atoms_written": n_atoms_total,
        "elapsed_s": time.time() - t0,
        "w_norm_cortex_final": float(np.linalg.norm(W_cortex)),
        "w_norm_hippocampus_final": float(np.linalg.norm(W_hippocampus)),
    }


def run_arm_segregated_dual_w_one_way_replay(seed: int) -> Dict:
    """PRIMARY ARM. DUAL W (W_cortex + W_hippocampus) + ONE-WAY REPLAY.

    Per phase:
      1. Hebbian-fast write current phase atoms -> W_hippocampus AND record
         atoms to episodic buffer (with phase id for recency weighting).
      2. SCHEDULED ONE-WAY REPLAY: sample recency-weighted from buffer
         (Hebbian-into-W_cortex) at alpha_per_pass = ALPHA_SLOW/N_REPLAY_PASSES.
         Note: replay samples ATOMS, not W_hippocampus directly. The
         hippocampus W is the fast-store; the buffer feeds the slow consolidator.
      3. cf-RPE on current phase atoms -> W_cortex (error-correction nudge
         AFTER replay; consistent with consolidation order).
    Recall reads from W_cortex.

    Brain-grounding: hippocampus is online Hebbian write-buffer; cortex
    receives only replayed (and cf-RPE-corrected) patterns. No back-coupling
    cortex -> hippocampus. This isolates "spatial segregation + one-way
    replay" as the architectural rescue for cl-spectrum HARD_FAIL.
    """
    rng = np.random.RandomState(seed + 500)
    W_cortex = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    W_hippocampus = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    episodic_buffer: List[np.ndarray] = []
    episodic_phase_ids: List[int] = []
    phase_atoms: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    flops_total = 0
    n_atoms_total = 0
    t0 = time.time()
    alpha_per_pass = ALPHA_SLOW / float(N_REPLAY_PASSES)
    for i in range(J_PHASES):
        Xi_i = make_phase_atoms(M_PER_PHASE, N_DIM, seed, i)
        phase_atoms.append(Xi_i)
        # 1. Hebbian-fast -> W_hippocampus + episodic buffer
        flops_total += hebbian_write(W_hippocampus, Xi_i, ALPHA_FAST, N_DIM)
        for x in Xi_i:
            episodic_buffer.append(x)
            episodic_phase_ids.append(i)
        # 2. One-way replay: hippocampus episodic buffer -> W_cortex
        flops_total += cls_replay_from_buffer(
            W_cortex, episodic_buffer, episodic_phase_ids, i,
            alpha_per_pass, N_REPLAY_PASSES, RECENCY_WEIGHT,
            M_PER_PHASE, rng, N_DIM,
        )
        # 3. cf-RPE error-correction on current phase -> W_cortex
        flops_total += cfrpe_update(W_cortex, Xi_i, ALPHA_CFRPE, N_DIM, N_CFRPE_PASSES)
        n_atoms_total += M_PER_PHASE
        recalls_after_i = []
        for j in range(i + 1):
            rec = eval_phase_recall(W_cortex, phase_atoms[j], N_PROBE, NOISE_FRAC, rng)
            recalls_after_i.append(rec)
        phase_recalls.append(recalls_after_i)
        print(f"  [seed={seed} DUAL_W_ONE_WAY phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]}", flush=True)
    return {
        "arm": "ARM_SEGREGATED_DUAL_W_ONE_WAY_REPLAY",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "flops_total": flops_total,
        "n_atoms_written": n_atoms_total,
        "elapsed_s": time.time() - t0,
        "w_norm_cortex_final": float(np.linalg.norm(W_cortex)),
        "w_norm_hippocampus_final": float(np.linalg.norm(W_hippocampus)),
    }


def run_seed(seed: int) -> Dict:
    print(f"[{ANCHOR_NAME}] seed={seed} starting 5 arms J={J_PHASES} M={M_PER_PHASE} N={N_DIM}", flush=True)
    results = {}
    results["ARM_BASELINE_STATIC"] = run_arm_baseline_static(seed)
    results["ARM_DISCRETE_ADD"] = run_arm_discrete_add(seed)
    results["ARM_FUSED_W_CFRPE_HEBBIAN"] = run_arm_fused_w_cfrpe_hebbian(seed)
    results["ARM_SEGREGATED_DUAL_W_NAIVE"] = run_arm_segregated_dual_w_naive(seed)
    results["ARM_SEGREGATED_DUAL_W_ONE_WAY_REPLAY"] = run_arm_segregated_dual_w_one_way_replay(seed)
    return {
        "seed": seed,
        "N": N_DIM,
        "N_DIM": N_DIM,
        "run_mode": RUN_MODE,
        "J_phases": J_PHASES,
        "m_per_phase": M_PER_PHASE,
        "arms": results,
    }


# ----------------------------------------------------------------------------
# Self-tests at import time (PROT-021)
# ----------------------------------------------------------------------------
def _instrumentation_selftest():
    n_dim = 256
    m = 20
    rng = np.random.RandomState(42)
    Xi = rng.choice([-1.0, 1.0], size=(m, n_dim)).astype(np.float32)
    W = (Xi.T @ Xi).astype(np.float32) / float(n_dim)
    rec_clean = eval_phase_recall(W, Xi, n_probe=10, noise_frac=0.0,
                                  rng=np.random.RandomState(7))
    assert rec_clean >= 0.95, f"selftest1 clean rec={rec_clean}"
    rec_noisy = eval_phase_recall(W, Xi, n_probe=10, noise_frac=0.10,
                                  rng=np.random.RandomState(7))
    assert rec_noisy >= 0.80, f"selftest1 noisy rec={rec_noisy}"
    # cf-RPE self-test: starts at W=0, runs 10 passes, recall on the trained M
    W2 = np.zeros((n_dim, n_dim), dtype=np.float32)
    _ = cfrpe_update(W2, Xi, alpha=0.05, n_dim=n_dim, n_passes=10)
    rec_cfrpe = eval_phase_recall(W2, Xi, n_probe=10, noise_frac=0.0,
                                  rng=np.random.RandomState(7))
    assert rec_cfrpe >= 0.50, f"selftest cfrpe rec={rec_cfrpe} (must learn from zero)"
    # ARM 5 dual-W structural invariant: two distinct W's same shape
    W_a = np.zeros((n_dim, n_dim), dtype=np.float32)
    W_b = np.zeros((n_dim, n_dim), dtype=np.float32)
    assert id(W_a) != id(W_b), "dual-W invariant: cortex and hippocampus must be distinct"
    assert W_a.shape == W_b.shape == (n_dim, n_dim), "dual-W invariant: matching shape"
    # Verify segregation: writing to one does NOT mutate the other
    hebbian_write(W_a, Xi, alpha=0.5, n_dim=n_dim)
    assert float(np.linalg.norm(W_b)) == 0.0, "segregation invariant: writes to W_a leaked into W_b"
    print(f"[selftest] PASS hebbian_clean={rec_clean:.2f} hebbian_noisy={rec_noisy:.2f} cfrpe_post={rec_cfrpe:.2f} dual_W_invariant=OK", flush=True)


_instrumentation_selftest()


# ----------------------------------------------------------------------------
# Aggregate
# ----------------------------------------------------------------------------
def aggregate_results(per_seed: Dict) -> Dict:
    per_arm: Dict[str, Dict[str, list]] = {arm: {
        "forgetting_p1": [],
        "transfer_final": [],
        "mean_retention_pre_p_final": [],
        "flops_total": [],
        "n_atoms_written": [],
        "compute_per_update": [],
        "phase_recalls_per_seed": [],
    } for arm in ARMS}
    for sd in per_seed.values():
        arms_data = sd.get("arms", {})
        J = sd.get("J_phases", J_PHASES)
        for arm in ARMS:
            r = arms_data.get(arm)
            if r is None:
                continue
            pr = r["phase_recalls"]
            if len(pr) < J:
                continue
            forget_p1 = pr[0][0] - pr[J - 1][0]
            transfer = pr[J - 1][J - 1]
            mean_pre_final = float(np.mean(pr[J - 1][:J - 1])) if J > 1 else 1.0
            per_arm[arm]["forgetting_p1"].append(forget_p1)
            per_arm[arm]["transfer_final"].append(transfer)
            per_arm[arm]["mean_retention_pre_p_final"].append(mean_pre_final)
            per_arm[arm]["flops_total"].append(r.get("flops_total", 0))
            n_w = max(r.get("n_atoms_written", 1), 1)
            per_arm[arm]["n_atoms_written"].append(n_w)
            per_arm[arm]["compute_per_update"].append(r.get("flops_total", 0) / float(n_w))
            per_arm[arm]["phase_recalls_per_seed"].append(pr)
    summary = {}
    for arm in ARMS:
        d = per_arm[arm]
        n = len(d["forgetting_p1"])
        mean_f = float(np.mean(d["forgetting_p1"])) if n else float("nan")
        std_f = float(np.std(d["forgetting_p1"], ddof=1)) if n > 1 else 0.0
        cv = (std_f / abs(mean_f)) if (n > 1 and abs(mean_f) > 1e-9) else 0.0
        summary[arm] = {
            "n_seeds": n,
            "mean_forgetting_p1": mean_f,
            "std_forgetting_p1": std_f,
            "cv_forgetting_p1": cv,
            "mean_transfer_final": float(np.mean(d["transfer_final"])) if n else float("nan"),
            "std_transfer_final": float(np.std(d["transfer_final"], ddof=1)) if n > 1 else 0.0,
            "mean_retention_pre_p_final": float(np.mean(d["mean_retention_pre_p_final"])) if n else float("nan"),
            "mean_flops": float(np.mean(d["flops_total"])) if n else float("nan"),
            "mean_compute_per_update": float(np.mean(d["compute_per_update"])) if n else float("nan"),
            "phase_recalls_per_seed": d["phase_recalls_per_seed"],
        }
    return summary


def compute_verdict(arm_summary: Dict) -> Tuple[str, str]:
    """Verdict over the 5-arm segregation spectrum.
      HARD_PASS_CL_MOAT_REAL if PRIMARY arm clears full bars.
      HARD_PASS_PARTIAL if PRIMARY arm clears partial bars.
      HARD_FAIL_DECISIVE if PRIMARY arm at/below FUSED_W baseline.
      MIDDLE_BAND otherwise.
      HARD_FAIL on sanity-rail violations.
    """
    baseline = arm_summary.get("ARM_BASELINE_STATIC", {})
    discrete = arm_summary.get("ARM_DISCRETE_ADD", {})
    fused = arm_summary.get(HARNESS_CONTROL_ARM, {})
    naive = arm_summary.get("ARM_SEGREGATED_DUAL_W_NAIVE", {})
    primary = arm_summary.get(PRIMARY_ARM, {})

    base_p1_init = baseline.get("phase_recalls_per_seed", [])
    base_p1_initial_recall = float("nan")
    if base_p1_init:
        vals = [pr[0][0] for pr in base_p1_init if pr]
        if vals:
            base_p1_initial_recall = float(np.mean(vals))

    primary_forget = primary.get("mean_forgetting_p1", float("nan"))
    primary_transfer = primary.get("mean_transfer_final", float("nan"))
    primary_cv = primary.get("cv_forgetting_p1", float("nan"))
    fused_forget = fused.get("mean_forgetting_p1", float("nan"))
    delta_vs_fused = (fused_forget - primary_forget) if (not math.isnan(fused_forget) and not math.isnan(primary_forget)) else float("nan")
    naive_forget = naive.get("mean_forgetting_p1", float("nan"))

    summary_line = (
        f"PRIMARY(one-way-replay) forgetting={primary_forget:.3f} transfer={primary_transfer:.3f} cv={primary_cv:.3f}; "
        f"FUSED_W forgetting={fused_forget:.3f} (delta={delta_vs_fused:.3f}); "
        f"NAIVE_dual_W forgetting={naive_forget:.3f}; "
        f"DISCRETE forgetting={discrete.get('mean_forgetting_p1', float('nan')):.3f}; "
        f"BASELINE p1_initial_recall={base_p1_initial_recall:.3f}"
    )

    # Sanity rail 1: BASELINE Phase 1 initial recall
    if math.isnan(base_p1_initial_recall) or not (SANITY_RAIL_LO <= base_p1_initial_recall <= SANITY_RAIL_HI):
        return ("HARD_FAIL",
                f"SANITY_RAIL_BASELINE violated: baseline_p1_initial_recall={base_p1_initial_recall:.3f} "
                f"outside [{SANITY_RAIL_LO}, {SANITY_RAIL_HI}]; substrate not learning Phase 1. {summary_line}")

    # Sanity rail 2: FUSED_W must reproduce cl-spectrum HARD_FAIL regime.
    # ONLY enforce in FULL mode (alpha_total=0.488 puts FUSED_W on the cliff).
    # Smoke uses J=3/M=200/N=4096 -> alpha_total=0.146, well below cliff;
    # FUSED_W expected forgetting ~0.0 in smoke (no capacity pressure). Smoke's
    # job is structural/timing gate, not band reproduction.
    if RUN_MODE == "full":
        if math.isnan(fused_forget) or not (HARNESS_FORGET_LO <= fused_forget <= HARNESS_FORGET_HI):
            return ("HARD_FAIL",
                    f"SANITY_RAIL_HARNESS violated (full-mode): fused_W_forgetting={fused_forget:.3f} "
                    f"outside [{HARNESS_FORGET_LO}, {HARNESS_FORGET_HI}]; harness does NOT reproduce "
                    f"cl-spectrum HARD_FAIL; measurement artifact suspected. {summary_line}")

    # Smoke is a structural/timing gate, not a band check. At smoke
    # J=3/M=200/N=4096 alpha_total=0.146 < cliff; FUSED_W shows forgetting~0
    # by capacity-headroom (not architecture). Decisive HARD_PASS / HARD_FAIL
    # verdicts only meaningful at full J=5/M=400/N=4096 alpha_total=0.488.
    if RUN_MODE != "full":
        return ("MIDDLE_BAND",
                f"SMOKE_STRUCTURAL_OK: smoke alpha_total below cliff regime; "
                f"verdict bands only meaningful at FULL J=5/M=400 alpha=0.488. {summary_line}")

    # HARD_PASS_CL_MOAT_REAL (full-mode only)
    hp_real_a = (not math.isnan(primary_forget)) and primary_forget < HP_REAL_FORGETTING_MAX
    hp_real_b = (not math.isnan(primary_transfer)) and primary_transfer > HP_REAL_TRANSFER_MIN
    hp_real_c = (not math.isnan(delta_vs_fused)) and delta_vs_fused >= HP_REAL_DELTA_VS_FUSED

    if hp_real_a and hp_real_b and hp_real_c:
        return ("HARD_PASS",
                f"HARD_PASS_CL_MOAT_REAL: segregated dual-W + one-way replay rescues cl-spectrum HARD_FAIL. "
                f"forgetting_p1={primary_forget:.3f} < HP_REAL={HP_REAL_FORGETTING_MAX} AND "
                f"transfer={primary_transfer:.3f} > HP_REAL={HP_REAL_TRANSFER_MIN} AND "
                f"delta_vs_FUSED={delta_vs_fused:.3f} >= HP_REAL={HP_REAL_DELTA_VS_FUSED}. {summary_line}")

    # HARD_FAIL_DECISIVE (full-mode only)
    hf_a = (not math.isnan(primary_forget)) and primary_forget >= HF_FORGETTING_MIN
    hf_b = (not math.isnan(delta_vs_fused)) and delta_vs_fused < HF_DELTA_VS_FUSED_MAX

    if hf_a or hf_b:
        reasons = []
        if hf_a: reasons.append(f"primary_forgetting={primary_forget:.3f} >= HF={HF_FORGETTING_MIN}")
        if hf_b: reasons.append(f"delta_vs_FUSED={delta_vs_fused:.3f} < HF={HF_DELTA_VS_FUSED_MAX}")
        return ("HARD_FAIL",
                f"HARD_FAIL_DECISIVE: segregated dual-W + one-way replay does NOT rescue cl-spectrum HARD_FAIL. " +
                "; ".join(reasons) + f". Deeper architectural redesign needed. {summary_line}")

    # HARD_PASS_PARTIAL
    hp_p_a = (not math.isnan(primary_forget)) and primary_forget <= HP_PARTIAL_FORGETTING_MAX
    hp_p_b = (not math.isnan(delta_vs_fused)) and delta_vs_fused >= HP_PARTIAL_DELTA_VS_FUSED
    if hp_p_a and hp_p_b:
        return ("MIDDLE_BAND",
                f"HARD_PASS_PARTIAL: segregated dual-W + one-way replay partially rescues. "
                f"forgetting={primary_forget:.3f} <= {HP_PARTIAL_FORGETTING_MAX} AND "
                f"delta_vs_FUSED={delta_vs_fused:.3f} >= {HP_PARTIAL_DELTA_VS_FUSED} "
                f"but does not clear HP_REAL bars. {summary_line}")

    return ("MIDDLE_BAND",
            f"Characterized but no chain-grade point: hp_real(a={hp_real_a} b={hp_real_b} c={hp_real_c}) "
            f"hp_partial(a={hp_p_a} b={hp_p_b}). {summary_line}")


# ----------------------------------------------------------------------------
# atexit synthesizer
# ----------------------------------------------------------------------------
_OUT_DIR = None
_T_START = None
_SYNTH_DONE = [False]

def _synth_metrics_atexit():
    if _SYNTH_DONE[0]:
        return
    if _OUT_DIR is None:
        return
    try:
        per_seed = aggregate_partials(_OUT_DIR, SEEDS)
        if not per_seed:
            return
        arm_summary = aggregate_results(per_seed)
        verdict, verdict_msg = compute_verdict(arm_summary)
        elapsed = time.time() - _T_START if _T_START else 0.0
        primary_d = arm_summary.get(PRIMARY_ARM, {})
        summary = (f"{verdict}: PRIMARY forgetting={primary_d.get('mean_forgetting_p1', float('nan')):.3f} "
                   f"transfer={primary_d.get('mean_transfer_final', float('nan')):.3f}")
        metrics = {
            "anchor": ANCHOR_NAME,
            "anchor_name": ANCHOR_NAME,
            "run_mode": RUN_MODE,
            "N": N_DIM,
            "N_DIM": N_DIM,
            "n_seeds": len(per_seed),
            "seeds": list(per_seed.keys()),
            "J_phases": J_PHASES,
            "m_per_phase": M_PER_PHASE,
            "arms": ARMS,
            "primary_arm": PRIMARY_ARM,
            "harness_control_arm": HARNESS_CONTROL_ARM,
            "config_version": (
                f"c3-segregated-dual-W-v1: N_DIM={N_DIM} J={J_PHASES} M={M_PER_PHASE} "
                f"alpha_fast={ALPHA_FAST} alpha_slow={ALPHA_SLOW} alpha_cfrpe={ALPHA_CFRPE} "
                f"recency_weight={RECENCY_WEIGHT} n_replay_passes={N_REPLAY_PASSES} "
                f"n_cfrpe_passes={N_CFRPE_PASSES} noise_frac={NOISE_FRAC} "
                f"retrieve_steps={N_RETRIEVE_STEPS} run_mode={RUN_MODE}"
            ),
            "corpus_provenance": "synthetic_bipolar_atoms_per_domain_permutation",
            "allow_synthetic": True,
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "metrics_source": "measured_cpu_synthetic_bipolar_segregated_dual_W_5arm",
            "per_arm_aggregate": arm_summary,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": summary,
            "elapsed_s": elapsed,
            "synthesized_at_exit": True,
        }
        metrics_path = _OUT_DIR / "metrics.json"
        with open(metrics_path, "w", encoding="utf-8") as fh:
            json.dump(metrics, fh, indent=2)
        _SYNTH_DONE[0] = True
        print(f"[atexit] synthesized metrics.json verdict={verdict}", flush=True)
    except Exception as e:
        print(f"[atexit] synth FAILED: {e}", flush=True)


atexit.register(_synth_metrics_atexit)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    global _OUT_DIR, _T_START
    _T_START = time.time()
    print(f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N_DIM={N_DIM} seeds={SEEDS} "
          f"J_phases={J_PHASES} M_per_phase={M_PER_PHASE} arms={ARMS}", flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR = out_dir
    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "J_phases": J_PHASES, "M_per_phase": M_PER_PHASE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(SEEDS)} done; running {remaining}", flush=True)

    for seed in remaining:
        r = run_seed(seed)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    arm_summary = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(arm_summary)

    total_elapsed = time.time() - _T_START
    primary_d = arm_summary.get(PRIMARY_ARM, {})
    fused_d = arm_summary.get(HARNESS_CONTROL_ARM, {})
    summary = (
        f"{verdict}: PRIMARY(one-way-replay) forgetting_p1={primary_d.get('mean_forgetting_p1', float('nan')):.3f} "
        f"transfer={primary_d.get('mean_transfer_final', float('nan')):.3f} "
        f"vs FUSED_W forgetting={fused_d.get('mean_forgetting_p1', float('nan')):.3f}"
    )
    metrics = {
        "anchor": ANCHOR_NAME,
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "N_DIM": N_DIM,
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "J_phases": J_PHASES,
        "m_per_phase": M_PER_PHASE,
        "arms": ARMS,
        "primary_arm": PRIMARY_ARM,
        "harness_control_arm": HARNESS_CONTROL_ARM,
        "config_version": (
            f"c3-segregated-dual-W-v1: N_DIM={N_DIM} J={J_PHASES} M={M_PER_PHASE} "
            f"alpha_fast={ALPHA_FAST} alpha_slow={ALPHA_SLOW} alpha_cfrpe={ALPHA_CFRPE} "
            f"recency_weight={RECENCY_WEIGHT} n_replay_passes={N_REPLAY_PASSES} "
            f"n_cfrpe_passes={N_CFRPE_PASSES} noise_frac={NOISE_FRAC} "
            f"retrieve_steps={N_RETRIEVE_STEPS} run_mode={RUN_MODE}"
        ),
        "corpus_provenance": "synthetic_bipolar_atoms_per_domain_permutation",
        "allow_synthetic": True,
        "zero_llm_calls_at_inference": True,
        "n_llm_calls": 0,
        "metrics_source": "measured_cpu_synthetic_bipolar_segregated_dual_W_5arm",
        "per_arm_aggregate": arm_summary,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": total_elapsed,
    }
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    _SYNTH_DONE[0] = True
    print(f"[{ANCHOR_NAME}] verdict={verdict}", flush=True)
    print(f"[{ANCHOR_NAME}] {verdict_msg}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={total_elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
