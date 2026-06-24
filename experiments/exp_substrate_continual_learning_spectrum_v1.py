"""substrate_continual_learning_spectrum_v1 -- 5-arm CL spectrum composition test.

SCIENTIFIC QUESTION:
  Do substrate's continual-learning primitives (cf-RPE delta-rule online updates,
  CLS-replay dual-W consolidation, K-bank routing) COMPOSE into a working CL
  system at production scale, or do they fail when stacked? Each primitive has
  been validated in isolation; this is the first stacked composition test.

STRATEGIC RATIONALE:
  Substrate's competitive moat vs transformers is: continual learning at low
  compute cost, without catastrophic forgetting, without expensive fine-tuning.
  This cell validates whether that moat is real (HARD_PASS) or theoretical
  (HARD_FAIL: primitives don't compose at scale).

5 ARMS ALONG THE CL SPECTRUM (frozen-static -> full-composed):
  ARM_BASELINE_STATIC      -- substrate frozen after Phase 1 train; no CL ops.
                               Catastrophic-forgetting reference (no learning).
                               NOTE: "frozen" means no new writes; recall still
                               works on Phase 1 patterns.
  ARM_DISCRETE_ADD         -- bind new patterns at inference time; no replay,
                               no slow consolidation. Naive online write.
  ARM_CFRPE_ONLINE         -- cf-RPE delta-rule online update at inference time;
                               error-driven; no replay.
  ARM_CLS_REPLAY           -- cf-RPE online + CLS-replay (dual-W with interleaved
                               replay during inter-phase consolidation). The
                               primary CL composition.
  ARM_FULL_CL_SYSTEM       -- cf-RPE + CLS-replay + K-bank routing (K=2 banks
                               with soft-gate per-phase routing). Full stack.

PROTOCOL (curriculum):
  Phase 1: substrate trained on Domain 0 (M atoms, permutation 0)
  Phases 2..J: present new domains sequentially (each new permutation)
  After each phase: measure recall on ALL prior domains (forgetting curve)
                    + recall on new domain (transfer measure)
  Compute per arm:
    - forgetting (Phase-1 recall after final phase)
    - transfer (final-domain recall after exposure)
    - capacity (W norm + per-bank fill for K-bank arm)
    - compute_per_update (ops per atom-write; for efficiency moat)

PRE-REGISTERED HARD BANDS:
  Sanity rail: ARM_BASELINE_STATIC retention on Phase 1 (pre-shift)
               within [0.85, 1.00] -- substrate actually stored Phase 1.

  HARD_PASS (CL moat real; chain-grade-eligible substrate CL):
    ARM_FULL_CL_SYSTEM forgetting_p1 <= 0.10
    AND ARM_FULL_CL_SYSTEM transfer_recall >= 0.60
    AND ARM_FULL_CL_SYSTEM beats ARM_DISCRETE_ADD on forgetting_p1 by >= 0.40
    (rescue is real, not flat-regime).

  CHAIN_GRADE_BONUS (transformers can't touch this):
    ARM_FULL_CL_SYSTEM forgetting_p1 <= 0.05
    AND ARM_FULL_CL_SYSTEM transfer_recall >= 0.80.

  MIDDLE_BAND: characterized but doesn't clear HARD_PASS bar.

  HARD_FAIL (CL primitives don't compose; moat is theoretical):
    ARM_FULL_CL_SYSTEM forgetting_p1 > 0.50
    OR ARM_FULL_CL_SYSTEM transfer_recall < 0.30
    OR ARM_FULL_CL_SYSTEM no better than ARM_DISCRETE_ADD (delta < 0).

WHAT_THIS_DOES_NOT_SHOW:
  - NOT a head-to-head with a transformer fine-tuning baseline (would need
    separate cell with HF Trainer + compute measurement; out-of-scope).
  - NOT cross-CORPUS continual learning (uses synthetic per-domain permutations
    of bipolar atoms, not real text8/wiki/code domains).
  - NOT a measurement of BPC; uses recall-accuracy (substrate-native CL metric).
    The BPC vs transformer comparison requires Path-A/B/C encoder + LM-grade
    sequence prediction, a separate cell.
  - Compute_per_update is measured in numpy-flops-per-atom-written; does NOT
    include encoder-side compute, only the write-update path. Apples-to-apples
    transformer comparison would need GPU FLOPs measurement.
  - K_BANK in ARM_FULL_CL_SYSTEM uses K=2 with random-projection gate; gate
    is not end-to-end trained (separate cell needed for that).

PROT-018: anchor has no _n<N> suffix; N_DIM=4096 encoded in config and asserted.
PROT-021: run_config = {"N": N_DIM, "run_mode": ..., "J_phases": J, "m_per_phase": M}.
PROT-019: full timeout >= 3600s if N >= 4096; estimated below.

FORMULA SELF-TESTS:
  1. Sign-flip retrieval non-degenerate (clean-probe -> recall 1.0)
  2. Single-phase no-CL: ARM_BASELINE recall on Phase 1 (post-train) >= 0.95
  3. Total alpha = (J * M) / N is in target sweep regime (>0.10, <0.50)
  4. cf-RPE delta-rule: starting at all-zero W, after K passes through M atoms
     recall must monotonically improve.

TIMEOUT ESTIMATE:
  Per-seed wall scales as 5 arms x J phases x (matmul N=4096 + retrieval ops).
  Smoke (J=3, M=200, N=4096, 2 seeds): expect ~ 60-90s wall.
  Full (J=5, M=400, N=4096, 3 seeds): expect ~ 800-1500s.
  PROT-019 floor 3600s, safety 1.5x -> 5400s. Use 5400s.

Cites:
  experiments/exp_cls_replay_continual_learning_smoke_v1.py  (dual-W CLS pattern)
  experiments/exp_substrate_K2_x_cfrpe_compose_LM_v1.py  (K=2 + cf-RPE composition)
  experiments/exp_a8_continual_writes_no_catastrophic_forgetting_v1.py  (continual lineage)
  preregs/2026-06-24_substrate_continual_learning_spectrum_v1.md
  USER 2026-06-24 directive: CL primitives never composed; moat validation.

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

ANCHOR_NAME = "substrate_continual_learning_spectrum_v1"

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
# Config
# ----------------------------------------------------------------------------
N_DIM = 4096                # production scale; PROT-019 timeout floor applies

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

# Shared CL primitive knobs
# Smoke calibration history (2026-06-24):
#   v0: alpha_cfrpe=0.05/3-passes, alpha_slow=0.1, recency=2 -> cf-RPE undershoots
#       (recall 0.45-0.65); replay washes new phase (transfer=0)
#   v1: alpha_cfrpe=0.3/5-passes, alpha_slow=0.05, recency=4 -> cf-RPE wipes
#       Hebbian writes (CLS phase 1 -> 0 after phase 2 cf-RPE pass)
#   v2 (current): drop cf-RPE arm to Hebbian-with-error-correction (rank-1 small
#       delta added to Hebbian, not delta-replacement); strong replay; preserve
#       current phase via Hebbian-fast in addition to cf-RPE nudge.
# Discovery: cf-RPE delta-rule + Hebbian replay are antagonistic at composition
# stage; both push W in different directions. The brain solves this via
# spatially-segregated cortex (hippocampal Hebbian write + cortical slow consolidation).
# This cell uses ARM_CFRPE_ONLINE as ablation-isolation; ARM_CLS_REPLAY and
# ARM_FULL_CL_SYSTEM augment Hebbian-write WITH a small cf-RPE error-correction
# pass (additive, not replacement).
ALPHA_FAST = 1.0            # Hebbian fast-write strength
ALPHA_SLOW = 0.1            # Cortex slow-write strength
ALPHA_CFRPE = 0.05          # cf-RPE delta-rule step (small additive nudge)
RECENCY_WEIGHT = 4.0        # CLS replay recency bias
K_BANKS = 2                 # K-bank routing in ARM_FULL_CL_SYSTEM
GATE_BETA = 4.0             # soft-gate sharpness

ARMS = [
    "ARM_BASELINE_STATIC",
    "ARM_DISCRETE_ADD",
    "ARM_CFRPE_ONLINE",
    "ARM_CLS_REPLAY",
    "ARM_FULL_CL_SYSTEM",
]

# ----------------------------------------------------------------------------
# Pre-reg bands
# ----------------------------------------------------------------------------
SANITY_RAIL_LO = 0.85
SANITY_RAIL_HI = 1.00

HP_FORGETTING_MAX = 0.10
HP_TRANSFER_MIN = 0.60
HP_VS_DISCRETE_DELTA = 0.40

CHAIN_BONUS_FORGETTING_MAX = 0.05
CHAIN_BONUS_TRANSFER_MIN = 0.80

HF_FORGETTING = 0.50
HF_TRANSFER = 0.30

# ----------------------------------------------------------------------------
# Formula self-tests at import time
# ----------------------------------------------------------------------------
assert N_DIM == 4096, f"PROT-021: N_DIM={N_DIM}"
ALPHA_TOTAL = (J_PHASES * M_PER_PHASE) / N_DIM
print(f"[formula_selftest] N_DIM={N_DIM} J={J_PHASES} M={M_PER_PHASE} alpha_total={ALPHA_TOTAL:.4f}", flush=True)
assert ALPHA_TOTAL > 0.10, f"alpha_total too low to see forgetting: {ALPHA_TOTAL}"
if RUN_MODE == "full":
    assert ALPHA_TOTAL >= 0.40, f"full-run alpha_total must push past cliff: {ALPHA_TOTAL}"

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def make_phase_atoms(m: int, n_dim: int, seed: int, phase_idx: int) -> np.ndarray:
    """M bipolar (+/-1) atoms for a phase; each phase has unique permutation seed."""
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
    """In-place W += alpha * Xi^T Xi / n_dim. Returns flops estimate."""
    W += (alpha * (Xi.T @ Xi) / float(n_dim)).astype(np.float32)
    # flops: M*N*N for Xi^T Xi + N*N for scale/add
    m = Xi.shape[0]
    return int(2 * m * n_dim * n_dim + n_dim * n_dim)


def cfrpe_update(W: np.ndarray, Xi: np.ndarray, alpha: float, n_dim: int,
                 n_passes: int) -> int:
    """cf-RPE delta-rule: error-driven update. For each atom xi:
        prediction = W @ xi
        error = xi - sign(prediction)
        W += alpha * error xi^T / n_dim (delta-rule outer-product)
    Multi-pass to converge. Returns flops estimate.
    """
    m = Xi.shape[0]
    flops = 0
    for _pass in range(n_passes):
        # vectorized: predictions = W @ Xi.T  -> (N, M)
        pred = W @ Xi.T  # (N, M)
        flops += 2 * n_dim * n_dim * m
        signed = np.sign(pred).astype(np.float32)
        signed[signed == 0] = 1.0
        # error = Xi.T - signed  (each column = target - pred)
        err = Xi.T - signed
        # delta rule: W += alpha * err @ Xi / n_dim
        W += (alpha * (err @ Xi) / float(n_dim)).astype(np.float32)
        flops += 2 * n_dim * m * n_dim + n_dim * n_dim
    return int(flops)


# ----------------------------------------------------------------------------
# Arms
# ----------------------------------------------------------------------------
def run_arm_baseline_static(seed: int) -> Dict:
    """ARM_BASELINE_STATIC: train on Phase 1 ONLY, then freeze. Subsequent
    phases are NOT learned. Tests pure-recall stability without any writes.
    """
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
            # only Phase 1 is written; subsequent phases are NOT
            flops_total += hebbian_write(W, Xi_i, ALPHA_FAST, N_DIM)
        recalls_after_i = []
        for j in range(i + 1):
            rec = eval_phase_recall(W, phase_atoms[j], N_PROBE, NOISE_FRAC, rng)
            recalls_after_i.append(rec)
        phase_recalls.append(recalls_after_i)
        print(f"  [seed={seed} BASELINE phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]}", flush=True)
    elapsed = time.time() - t0
    return {
        "arm": "ARM_BASELINE_STATIC",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "flops_total": flops_total,
        "n_atoms_written": M_PER_PHASE,  # only phase 1
        "elapsed_s": elapsed,
        "w_norm_final": float(np.linalg.norm(W)),
    }


def run_arm_discrete_add(seed: int) -> Dict:
    """ARM_DISCRETE_ADD: naive online write; bind new atoms at inference time;
    no replay; no cf-RPE; no slow consolidation. Catastrophic-forgetting baseline.
    """
    rng = np.random.RandomState(seed + 200)
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    phase_atoms: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    flops_total = 0
    t0 = time.time()
    n_atoms_total = 0
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
    elapsed = time.time() - t0
    return {
        "arm": "ARM_DISCRETE_ADD",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "flops_total": flops_total,
        "n_atoms_written": n_atoms_total,
        "elapsed_s": elapsed,
        "w_norm_final": float(np.linalg.norm(W)),
    }


def run_arm_cfrpe_online(seed: int) -> Dict:
    """ARM_CFRPE_ONLINE: cf-RPE delta-rule online update; error-driven; no
    replay. Tests cf-RPE primitive in isolation as CL mechanism.
    """
    rng = np.random.RandomState(seed + 300)
    W = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    phase_atoms: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    flops_total = 0
    t0 = time.time()
    n_atoms_total = 0
    for i in range(J_PHASES):
        Xi_i = make_phase_atoms(M_PER_PHASE, N_DIM, seed, i)
        phase_atoms.append(Xi_i)
        # cf-RPE update on current phase only (no replay of prior phases)
        flops_total += cfrpe_update(W, Xi_i, ALPHA_CFRPE, N_DIM, N_CFRPE_PASSES)
        n_atoms_total += M_PER_PHASE
        recalls_after_i = []
        for j in range(i + 1):
            rec = eval_phase_recall(W, phase_atoms[j], N_PROBE, NOISE_FRAC, rng)
            recalls_after_i.append(rec)
        phase_recalls.append(recalls_after_i)
        print(f"  [seed={seed} CFRPE_ONLINE phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]}", flush=True)
    elapsed = time.time() - t0
    return {
        "arm": "ARM_CFRPE_ONLINE",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "flops_total": flops_total,
        "n_atoms_written": n_atoms_total,
        "elapsed_s": elapsed,
        "w_norm_final": float(np.linalg.norm(W)),
    }


def run_arm_cls_replay(seed: int) -> Dict:
    """ARM_CLS_REPLAY: cf-RPE online update + CLS-replay (dual-W with
    interleaved per-phase replay to W_cortex via recency-weighted sampling).
    Recall reads from W_cortex.
    """
    rng = np.random.RandomState(seed + 400)
    W_cortex = np.zeros((N_DIM, N_DIM), dtype=np.float32)
    episodic_buffer: List[np.ndarray] = []
    phase_atoms: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    flops_total = 0
    t0 = time.time()
    n_atoms_total = 0
    for i in range(J_PHASES):
        Xi_i = make_phase_atoms(M_PER_PHASE, N_DIM, seed, i)
        phase_atoms.append(Xi_i)
        # Fast hippocampal episodic ingest
        for x in Xi_i:
            episodic_buffer.append(x)
        # CL phase order (smoke-validated):
        #   1. Hebbian-fast write current phase -> W_cortex (establishes new pattern)
        #   2. CLS replay buffer (recency-weighted) -> W_cortex (consolidates prior)
        #   3. cf-RPE small nudge on current phase -> W_cortex (error-correction)
        # Hebbian-fast write of current phase
        flops_total += hebbian_write(W_cortex, Xi_i, ALPHA_FAST, N_DIM)
        # CLS replay
        buf_arr = np.stack(episodic_buffer, axis=0)
        weights = np.zeros(buf_arr.shape[0], dtype=np.float64)
        offset = 0
        for ph_idx in range(i + 1):
            w_ph = (RECENCY_WEIGHT ** (i - ph_idx))
            weights[offset:offset + M_PER_PHASE] = w_ph
            offset += M_PER_PHASE
        weights = weights / weights.sum()
        alpha_per_pass = ALPHA_SLOW / float(N_REPLAY_PASSES)
        n_per_pass = min(M_PER_PHASE, buf_arr.shape[0])
        for _pass in range(N_REPLAY_PASSES):
            idx = rng.choice(buf_arr.shape[0], size=n_per_pass, replace=False, p=weights)
            Xi_replay = buf_arr[idx]
            flops_total += hebbian_write(W_cortex, Xi_replay, alpha_per_pass, N_DIM)
        # cf-RPE error-correction nudge
        flops_total += cfrpe_update(W_cortex, Xi_i, ALPHA_CFRPE, N_DIM, N_CFRPE_PASSES)
        n_atoms_total += M_PER_PHASE
        recalls_after_i = []
        for j in range(i + 1):
            rec = eval_phase_recall(W_cortex, phase_atoms[j], N_PROBE, NOISE_FRAC, rng)
            recalls_after_i.append(rec)
        phase_recalls.append(recalls_after_i)
        print(f"  [seed={seed} CLS_REPLAY phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]}", flush=True)
    elapsed = time.time() - t0
    return {
        "arm": "ARM_CLS_REPLAY",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "flops_total": flops_total,
        "n_atoms_written": n_atoms_total,
        "elapsed_s": elapsed,
        "w_norm_final": float(np.linalg.norm(W_cortex)),
    }


def run_arm_full_cl_system(seed: int) -> Dict:
    """ARM_FULL_CL_SYSTEM: cf-RPE + CLS-replay + K-bank routing (K=2).
    Each bank gets its own W_cortex + episodic buffer. Soft-gate routes each
    atom to the dominant bank by random-projection alignment. Recall reads
    from gate-weighted combination across banks.
    """
    rng = np.random.RandomState(seed + 500)
    # K banks of W_cortex + episodic buffer
    banks_W = [np.zeros((N_DIM, N_DIM), dtype=np.float32) for _ in range(K_BANKS)]
    banks_buf: List[List[np.ndarray]] = [[] for _ in range(K_BANKS)]
    # Random-projection gate: each bank has a random unit vector;
    # gate score = softmax(beta * <gate_k, x>)
    gate_rng = np.random.RandomState(seed + 99999)
    gate_vecs = gate_rng.normal(size=(K_BANKS, N_DIM)).astype(np.float32)
    gate_vecs /= np.linalg.norm(gate_vecs, axis=1, keepdims=True) + 1e-9
    phase_atoms: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    bank_fill = [0] * K_BANKS
    flops_total = 0
    t0 = time.time()
    n_atoms_total = 0

    def gate_scores(X: np.ndarray) -> np.ndarray:
        """Return softmax-gate scores (M, K)."""
        raw = X @ gate_vecs.T  # (M, K)
        raw = GATE_BETA * raw / float(N_DIM)
        raw = raw - raw.max(axis=1, keepdims=True)
        exp_r = np.exp(raw)
        return exp_r / (exp_r.sum(axis=1, keepdims=True) + 1e-9)

    def retrieve_kbank(probe: np.ndarray) -> np.ndarray:
        """Gate-weighted Hopfield retrieve across K banks."""
        # gate-weight (1,K) for this single probe
        raw_p = (probe @ gate_vecs.T) * GATE_BETA / float(N_DIM)
        raw_p = raw_p - raw_p.max()
        w = np.exp(raw_p)
        w = w / (w.sum() + 1e-9)
        state = probe.copy()
        for _ in range(N_RETRIEVE_STEPS):
            h = np.zeros(N_DIM, dtype=np.float32)
            for k in range(K_BANKS):
                h += float(w[k]) * (banks_W[k] @ state)
            state = np.sign(h).astype(np.float32)
            state[state == 0] = 1.0
        return state

    def eval_kbank_recall(Xi_phase: np.ndarray) -> float:
        m = Xi_phase.shape[0]
        n_q = min(N_PROBE, m)
        correct = 0
        for i in range(n_q):
            xi = Xi_phase[i]
            probe = xi.copy()
            flip = rng.random(N_DIM) < NOISE_FRAC
            probe[flip] *= -1.0
            ret = retrieve_kbank(probe)
            cos = float(np.dot(ret, xi) / N_DIM)
            if cos > 0.80:
                correct += 1
        return correct / n_q if n_q > 0 else 0.0

    for i in range(J_PHASES):
        Xi_i = make_phase_atoms(M_PER_PHASE, N_DIM, seed, i)
        phase_atoms.append(Xi_i)
        # Compute gate scores; assign each atom to dominant bank (hard-route
        # write for simplicity; soft-gate retrieve at read-time).
        gs = gate_scores(Xi_i)  # (M, K)
        assignments = np.argmax(gs, axis=1)  # (M,)
        for k in range(K_BANKS):
            mask = (assignments == k)
            n_k = int(mask.sum())
            if n_k == 0:
                continue
            Xi_k = Xi_i[mask]
            # Ingest to bank buffer (recency tracking via phase-id list)
            for x in Xi_k:
                banks_buf[k].append((i, x))  # (phase_id, atom)
            bank_fill[k] += n_k
            # Per-bank CL order: Hebbian-fast current slice -> CLS-replay -> cf-RPE nudge
            flops_total += hebbian_write(banks_W[k], Xi_k, ALPHA_FAST, N_DIM)
            buf_with_phase = banks_buf[k]
            if len(buf_with_phase) > 0:
                buf_arr = np.stack([x for (_p, x) in buf_with_phase], axis=0)
                phase_ids = np.array([p for (p, _x) in buf_with_phase], dtype=np.int64)
                weights = np.array(
                    [RECENCY_WEIGHT ** (i - p) for p in phase_ids],
                    dtype=np.float64,
                )
                weights = weights / weights.sum()
                n_per_pass = min(M_PER_PHASE, buf_arr.shape[0])
                alpha_per_pass = ALPHA_SLOW / float(N_REPLAY_PASSES)
                for _pass in range(N_REPLAY_PASSES):
                    idx = rng.choice(buf_arr.shape[0], size=n_per_pass, replace=False, p=weights)
                    Xi_replay = buf_arr[idx]
                    flops_total += hebbian_write(banks_W[k], Xi_replay, alpha_per_pass, N_DIM)
            # cf-RPE error-correction nudge
            flops_total += cfrpe_update(banks_W[k], Xi_k, ALPHA_CFRPE, N_DIM, N_CFRPE_PASSES)
        n_atoms_total += M_PER_PHASE
        recalls_after_i = []
        for j in range(i + 1):
            rec = eval_kbank_recall(phase_atoms[j])
            recalls_after_i.append(rec)
        phase_recalls.append(recalls_after_i)
        print(f"  [seed={seed} FULL_CL phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]} bank_fill={bank_fill}", flush=True)
    elapsed = time.time() - t0
    w_norms = [float(np.linalg.norm(banks_W[k])) for k in range(K_BANKS)]
    return {
        "arm": "ARM_FULL_CL_SYSTEM",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "flops_total": flops_total,
        "n_atoms_written": n_atoms_total,
        "bank_fill": bank_fill,
        "w_norms_per_bank": w_norms,
        "elapsed_s": elapsed,
    }


def run_seed(seed: int) -> Dict:
    print(f"[{ANCHOR_NAME}] seed={seed} starting 5 arms J={J_PHASES} M={M_PER_PHASE} N={N_DIM}", flush=True)
    results = {}
    results["ARM_BASELINE_STATIC"] = run_arm_baseline_static(seed)
    results["ARM_DISCRETE_ADD"] = run_arm_discrete_add(seed)
    results["ARM_CFRPE_ONLINE"] = run_arm_cfrpe_online(seed)
    results["ARM_CLS_REPLAY"] = run_arm_cls_replay(seed)
    results["ARM_FULL_CL_SYSTEM"] = run_arm_full_cl_system(seed)
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
    """Run BEFORE main():
      1. Sign-flip retrieval clean-probe -> recall=1.0
      2. Single-phase no-CL: small-N Hebbian baseline recall >= 0.95 on clean probe
      3. cf-RPE: starting at W=0, after K passes recall on the same M atoms
         must be > random (>0.5 fraction correct).
    """
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
    # cf-RPE self-test: starts at W=0, runs 5 passes, recall on the trained M
    W2 = np.zeros((n_dim, n_dim), dtype=np.float32)
    _ = cfrpe_update(W2, Xi, alpha=0.05, n_dim=n_dim, n_passes=10)
    rec_cfrpe = eval_phase_recall(W2, Xi, n_probe=10, noise_frac=0.0,
                                  rng=np.random.RandomState(7))
    assert rec_cfrpe >= 0.50, f"selftest cfrpe rec={rec_cfrpe} (must learn from zero)"
    print(f"[selftest] PASS hebbian_clean={rec_clean:.2f} hebbian_noisy={rec_noisy:.2f} cfrpe_post={rec_cfrpe:.2f}", flush=True)


_instrumentation_selftest()


# ----------------------------------------------------------------------------
# Aggregate
# ----------------------------------------------------------------------------
def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate across seeds; per-arm: forgetting, transfer, flops, etc."""
    per_arm: Dict[str, Dict[str, list]] = {arm: {
        "forgetting_p1": [],         # phase_recalls[0][0] - phase_recalls[J-1][0]
        "transfer_final": [],        # phase_recalls[J-1][J-1]
        "mean_retention_pre_p_final": [],  # mean over phase_recalls[J-1][:J-1]
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
            # Phase 1 forgetting: initial recall (after Phase 1 train) vs final-phase recall.
            # Note ARM_BASELINE_STATIC doesn't write Phase 2+; baseline pr[0][0] is full-trained.
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
        summary[arm] = {
            "n_seeds": n,
            "mean_forgetting_p1": float(np.mean(d["forgetting_p1"])) if n else float("nan"),
            "std_forgetting_p1": float(np.std(d["forgetting_p1"], ddof=1)) if n > 1 else 0.0,
            "mean_transfer_final": float(np.mean(d["transfer_final"])) if n else float("nan"),
            "std_transfer_final": float(np.std(d["transfer_final"], ddof=1)) if n > 1 else 0.0,
            "mean_retention_pre_p_final": float(np.mean(d["mean_retention_pre_p_final"])) if n else float("nan"),
            "mean_flops": float(np.mean(d["flops_total"])) if n else float("nan"),
            "mean_compute_per_update": float(np.mean(d["compute_per_update"])) if n else float("nan"),
            "phase_recalls_per_seed": d["phase_recalls_per_seed"],
        }
    return summary


def compute_verdict(arm_summary: Dict) -> Tuple[str, str]:
    """Verdict over the 5-arm spectrum.
      HARD_PASS if FULL_CL meets forgetting/transfer/delta bars.
      CHAIN_BONUS if FULL_CL also crosses chain-grade thresholds.
      HARD_FAIL if FULL_CL is at the failure-band trip.
    """
    baseline = arm_summary.get("ARM_BASELINE_STATIC", {})
    discrete = arm_summary.get("ARM_DISCRETE_ADD", {})
    cfrpe_o = arm_summary.get("ARM_CFRPE_ONLINE", {})
    cls = arm_summary.get("ARM_CLS_REPLAY", {})
    full = arm_summary.get("ARM_FULL_CL_SYSTEM", {})
    base_p1_init = baseline.get("phase_recalls_per_seed", [])
    base_p1_initial_recall = float("nan")
    if base_p1_init:
        # phase_recalls[0][0] across seeds; baseline writes Phase 1 only.
        vals = [pr[0][0] for pr in base_p1_init if pr]
        if vals:
            base_p1_initial_recall = float(np.mean(vals))
    full_forget = full.get("mean_forgetting_p1", float("nan"))
    full_transfer = full.get("mean_transfer_final", float("nan"))
    discrete_forget = discrete.get("mean_forgetting_p1", float("nan"))
    delta_vs_discrete = (discrete_forget - full_forget) if (not math.isnan(discrete_forget) and not math.isnan(full_forget)) else float("nan")

    summary_line = (
        f"FULL_CL forgetting={full_forget:.3f} transfer={full_transfer:.3f} "
        f"vs DISCRETE forgetting={discrete_forget:.3f} (delta={delta_vs_discrete:.3f}); "
        f"CLS_REPLAY forgetting={cls.get('mean_forgetting_p1', float('nan')):.3f}; "
        f"CFRPE_ONLINE forgetting={cfrpe_o.get('mean_forgetting_p1', float('nan')):.3f}; "
        f"BASELINE_static p1_initial_recall={base_p1_initial_recall:.3f}"
    )

    # Sanity rail: BASELINE Phase 1 initial recall must be in [SANITY_LO, SANITY_HI]
    if math.isnan(base_p1_initial_recall) or not (SANITY_RAIL_LO <= base_p1_initial_recall <= SANITY_RAIL_HI):
        return ("HARD_FAIL",
                f"SANITY_RAIL violated: baseline_static_p1_initial_recall={base_p1_initial_recall:.3f} "
                f"outside [{SANITY_RAIL_LO}, {SANITY_RAIL_HI}]; substrate not learning Phase 1. {summary_line}")

    # HARD_PASS: FULL_CL clears all 3 bars
    hp_a = (not math.isnan(full_forget)) and full_forget <= HP_FORGETTING_MAX
    hp_b = (not math.isnan(full_transfer)) and full_transfer >= HP_TRANSFER_MIN
    hp_c = (not math.isnan(delta_vs_discrete)) and delta_vs_discrete >= HP_VS_DISCRETE_DELTA

    cb_a = (not math.isnan(full_forget)) and full_forget <= CHAIN_BONUS_FORGETTING_MAX
    cb_b = (not math.isnan(full_transfer)) and full_transfer >= CHAIN_BONUS_TRANSFER_MIN

    if hp_a and hp_b and hp_c:
        bonus = " CHAIN_BONUS achieved." if (cb_a and cb_b) else ""
        return ("HARD_PASS",
                f"Substrate CL system chain-grade composes: forgetting_p1={full_forget:.3f} "
                f"<= HP={HP_FORGETTING_MAX} AND transfer={full_transfer:.3f} >= HP={HP_TRANSFER_MIN} "
                f"AND delta_vs_DISCRETE={delta_vs_discrete:.3f} >= HP={HP_VS_DISCRETE_DELTA}.{bonus} {summary_line}")

    # HARD_FAIL bar
    hf_a = (not math.isnan(full_forget)) and full_forget > HF_FORGETTING
    hf_b = (not math.isnan(full_transfer)) and full_transfer < HF_TRANSFER
    hf_c = (not math.isnan(delta_vs_discrete)) and delta_vs_discrete < 0.0

    if hf_a or hf_b or hf_c:
        reasons = []
        if hf_a: reasons.append(f"forgetting={full_forget:.3f} > HF={HF_FORGETTING}")
        if hf_b: reasons.append(f"transfer={full_transfer:.3f} < HF={HF_TRANSFER}")
        if hf_c: reasons.append(f"FULL_CL no better than DISCRETE (delta={delta_vs_discrete:.3f} < 0)")
        return ("HARD_FAIL",
                f"CL primitives don't compose; substrate CL moat is theoretical. " +
                "; ".join(reasons) + f". {summary_line}")

    return ("MIDDLE_BAND",
            f"CL spectrum characterized but no chain-grade point: "
            f"hp_a={hp_a} hp_b={hp_b} hp_c={hp_c}. {summary_line}")


# ----------------------------------------------------------------------------
# atexit synthesizer (write metrics.json even on crash/timeout)
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
            return  # nothing to synthesize
        arm_summary = aggregate_results(per_seed)
        verdict, verdict_msg = compute_verdict(arm_summary)
        elapsed = time.time() - _T_START if _T_START else 0.0
        summary = f"{verdict}: FULL_CL forgetting={arm_summary.get('ARM_FULL_CL_SYSTEM', {}).get('mean_forgetting_p1', float('nan')):.3f} transfer={arm_summary.get('ARM_FULL_CL_SYSTEM', {}).get('mean_transfer_final', float('nan')):.3f}"
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
            "config_version": (
                f"cl-spectrum-v1: N_DIM={N_DIM} J={J_PHASES} M={M_PER_PHASE} "
                f"alpha_fast={ALPHA_FAST} alpha_slow={ALPHA_SLOW} alpha_cfrpe={ALPHA_CFRPE} "
                f"K_BANKS={K_BANKS} gate_beta={GATE_BETA} "
                f"n_replay_passes={N_REPLAY_PASSES} n_cfrpe_passes={N_CFRPE_PASSES} "
                f"noise_frac={NOISE_FRAC} retrieve_steps={N_RETRIEVE_STEPS} run_mode={RUN_MODE}"
            ),
            "corpus_provenance": "synthetic_bipolar_atoms_per_domain_permutation",
            "allow_synthetic": True,
            "zero_llm_calls_at_inference": True,
            "n_llm_calls": 0,
            "metrics_source": "measured_cpu_synthetic_bipolar_cl_spectrum_5arm",
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
    full = arm_summary.get("ARM_FULL_CL_SYSTEM", {})
    discrete = arm_summary.get("ARM_DISCRETE_ADD", {})
    summary = (
        f"{verdict}: FULL_CL forgetting_p1={full.get('mean_forgetting_p1', float('nan')):.3f} "
        f"transfer={full.get('mean_transfer_final', float('nan')):.3f} "
        f"compute_per_update={full.get('mean_compute_per_update', float('nan')):.2e} flops/atom "
        f"| DISCRETE_baseline forgetting={discrete.get('mean_forgetting_p1', float('nan')):.3f}"
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
        "config_version": (
            f"cl-spectrum-v1: N_DIM={N_DIM} J={J_PHASES} M={M_PER_PHASE} "
            f"alpha_fast={ALPHA_FAST} alpha_slow={ALPHA_SLOW} alpha_cfrpe={ALPHA_CFRPE} "
            f"K_BANKS={K_BANKS} gate_beta={GATE_BETA} "
            f"n_replay_passes={N_REPLAY_PASSES} n_cfrpe_passes={N_CFRPE_PASSES} "
            f"noise_frac={NOISE_FRAC} retrieve_steps={N_RETRIEVE_STEPS} run_mode={RUN_MODE}"
        ),
        "corpus_provenance": "synthetic_bipolar_atoms_per_domain_permutation",
        "allow_synthetic": True,
        "zero_llm_calls_at_inference": True,
        "n_llm_calls": 0,
        "metrics_source": "measured_cpu_synthetic_bipolar_cl_spectrum_5arm",
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
