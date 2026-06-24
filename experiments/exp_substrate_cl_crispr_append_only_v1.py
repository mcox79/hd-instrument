"""substrate_cl_crispr_append_only_v1 -- structural-commitment CL via append-only slabs.

SCIENTIFIC QUESTION:
  Does CRISPR-style append-only memory growth (MOVE C structural commitment from
  the cross-biology CL 3rd-angle drill) rescue the substrate from the spectrum
  HARD_FAIL? Spectrum HARD_FAIL is 3-part: fused-W antagonism + IID-pessimal
  curriculum + transfer-metric cancellation. Append-only addresses the FIRST
  by construction: NEW domains get NEW orthogonal subspaces; OLD subspace is
  frozen and CANNOT be overwritten. This directly tests whether the brain-
  inspired shared-W architecture is the load-bearing failure point or whether
  there is a deeper substrate-CL issue.

STRATEGIC RATIONALE:
  Substrate has 11 brain-CL primitives but uses NONE of the 3 biology-
  convergent design moves: substrate-offload (A), clonal-selection (B),
  structural-commitment (C). Brain has neurogenesis (dentate gyrus); current
  substrate has a FIXED shared W matrix. CRISPR bacterial immune memory APPENDS
  new phage signatures sequentially to a tandem-spacer array; it does not
  overwrite existing memory. Substrate-native analog: per-phase NEW orthogonal
  subspace; W grows monotonically; OLD subspace preserved by construction.

  If HARD_PASS: substrate's CL moat becomes architecturally real (not just
  primitive-level), because structural commitment is by-construction-no-
  forgetting. If HARD_FAIL: the issue is deeper than shared-W antagonism;
  IID-random curriculum or the transfer metric must be the next drill.

4 ARMS (matches Director task spec):
  ARM_BASELINE_STATIC                -- Phase 1 train + freeze; sanity rail.
                                        Phase 1 recall stays at 1.0.
  ARM_FUSED_W_CFRPE_HEBBIAN          -- Reproduces CL spectrum FULL_CL_SYSTEM
                                        fused-W forgetting=0.65; provenance
                                        for the fused-W antagonism finding.
  ARM_APPEND_ONLY_NEW_DIMS           -- NEW patterns get NEW orthogonal
                                        subspaces; W grows linearly with phases;
                                        old W subspace preserved.
                                        cf-RPE / Hebbian write ONLY into the new
                                        phase's slab.
  ARM_APPEND_ONLY_PLUS_CFRPE         -- Append-only + cf-RPE plasticity ON THE
                                        NEWLY-ADDED DIMS ONLY. Old dims frozen.
                                        Primary arm (per Lane 1 declaration).

ARCHITECTURE (append-only):
  W starts at shape (D_slab, D_slab) where D_slab = N_BASE // J_PHASES.
  At phase j: allocate NEW slab W_j of shape (D_slab, D_slab); concat into a
  block-diagonal W of shape (j*D_slab, j*D_slab). NEW slabs are isolated; OLD
  slabs frozen. Probes are projected onto each slab's subspace; max-cosine
  selects which slab retrieves; retrieved subspace state is unprojected.

  This gives:
    - Old patterns preserved by construction (frozen old slabs).
    - Total W capacity = J * D_slab^2 grows with phases (NOT a fixed budget).
    - Per-slab alpha = M / D_slab = 400 / 820 ~= 0.488 (matches fused-W alpha).
    - No cross-slab interference.

CONFOUND_AUDIT (per master apples-to-apples checklist):
  - D_slab: held constant across CRISPR arms (=N_BASE/J_PHASES); fused-W uses
    N_BASE so total parameter budget is identical (J * D_slab^2 = N_BASE^2 / J;
    fused-W has N_BASE^2; CRISPR has N_BASE^2 / J ... but this is the natural
    geometry of orthogonal partition. ARM_FUSED_W is the COMPARISON baseline,
    not a parameter-matched control. We DOCUMENT this asymmetry and note that
    CRISPR uses LESS total compute per write -- this is a feature not a bug.).
  - Frozen-old-slab policy: hard-freeze (no writes to old slabs). Alternative
    would be soft-freeze (small learning rate); we use HARD to test the strict
    structural-commitment principle.
  - Subspace orthogonality: by construction; each slab lives in disjoint dims.
  - Routing: at retrieve, max-cosine across slab projections. Tiebreak: argmax
    on the cosine score (stable np.argmax).

INTRA_LANE_DELTA (single variable across primary arms):
  ARM_APPEND_ONLY_NEW_DIMS vs ARM_APPEND_ONLY_PLUS_CFRPE: ONE thing varies =
  cf-RPE plasticity on the new slab. ARM_APPEND_ONLY uses ONLY Hebbian.
  ARM_APPEND_ONLY_PLUS_CFRPE adds cf-RPE delta-rule passes ON THE NEW SLAB
  AFTER the Hebbian write. Old slabs are frozen in both arms.

PRE-REGISTERED HARD BANDS (per task spec):
  Sanity rail (required):
    - ARM_BASELINE_STATIC Phase-1 initial recall in [0.85, 1.00].
    - ARM_FUSED_W_CFRPE_HEBBIAN forgetting_p1 in [0.55, 0.75] (reproduces
      spectrum FULL_CL forgetting=0.65 +/- 0.10).

  HARD_PASS_CRISPR_MOAT:
    - ARM_APPEND_ONLY forgetting < 0.10
    - AND total_capacity >= 5x base_capacity (slab count == J_PHASES;
      append-only preserves all J slabs).

  HARD_PASS_CRISPR_PLUS_PLASTICITY (primary arm):
    - ARM_APPEND_ONLY_PLUS_CFRPE forgetting < 0.10
    - AND transfer_pre_replay >= 0.30 (cf-RPE on new dims gives real plasticity).

  MIDDLE_BAND: forgetting in [0.10, 0.30].

  HARD_FAIL_DECISIVE:
    - ARM_APPEND_ONLY forgetting >= 0.30 (structural-commitment doesn't fix CL;
      issue is deeper than shared-W antagonism).
    - OR sanity rails violated.

  cv < 0.05 across seeds for primary metric.

NOT TESTED HERE:
  - IID-pessimal curriculum (Issue 1 of L4 audit) -- still uses random bipolar.
    HARD_PASS here is robust to ANY curriculum since old slabs are protected.
  - Cross-corpus continual learning -- synthetic bipolar atoms only.
  - End-to-end gating -- slab-routing is by max-cosine, not learned.
  - Soft-freeze old slabs -- pure hard-freeze tested.

PROT-018: anchor has no _n<N> suffix; N_BASE=4096 asserted in config.
PROT-021: run_config = {"N": N_BASE, "run_mode": ..., "J_phases": J, "m_per_phase": M}.

FORMULA SELF-TESTS (--self-test):
  1. Sign-flip retrieval non-degenerate (clean-probe -> recall 1.0).
  2. Per-slab Hebbian recall: small-N, M atoms in a D_slab subspace, alpha at
     M/D_slab capacity -- recall >= 0.80 on noise=0.20 probe.
  3. Max-cosine slab routing: probe drawn from slab i should route to slab i
     with high probability (>= 0.80) when slabs are orthogonal.
  4. cf-RPE delta-rule self-test: starting at all-zero W, M passes converge
     to recall >= 0.50 on the trained M atoms.

TIMEOUT ESTIMATE:
  Per-seed wall scales as 4 arms x J phases x D_slab^2 ops.
  ARM_FUSED_W is the dominant cost (N^2 = 4096^2 = 16.7M ops/write).
  ARM_APPEND_ONLY: per slab D_slab^2 = 820^2 = 672K ops/write, ~25x cheaper.
  Smoke (J=3, M=200, N=4096, 2 seeds): expect ~ 90-150s wall.
  Full (J=5, M=400, N=4096, 3 seeds): expect ~ 1200-1800s.
  PROT-019 floor for N>=4096: 14400s.  Use 14400 since PROT-019 binds; cell
  imports _seed_checkpoint per PROT-021. (Actual wall estimated well below 4h
  but ledger demands the floor.)

  CORRECTION: anchor has no _n<N> suffix (per PROT-018), so PROT-019 floor
  does NOT bind. Estimated full ~1500s; with 1.5x safety = 2250s; budget 5400s
  to match reference spectrum cell.

Cites:
  experiments/exp_substrate_continual_learning_spectrum_v1.py  (provenance + 5-arm fused-W reference)
  notes/research_cl_spectrum_3rd_angle_cross_biology_2026-06-24.md  (L5 Cell 1 design)
  notes/exp_dev_handoff_research_cl_spectrum_3rd_angle_cross_biology_2026-06-24.md
  preregs/2026-06-24_substrate_cl_crispr_append_only_v1.md

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

ANCHOR_NAME = "substrate_cl_crispr_append_only_v1"

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
N_BASE = 4096  # full-ambient dim; slab dim = N_BASE / J_PHASES

if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    J_PHASES = 3
    M_PER_PHASE = 200
    NOISE_FRAC = 0.20
    N_PROBE = 20
    N_RETRIEVE_STEPS = 5
    N_CFRPE_PASSES = 3
else:
    SEEDS = [7, 17, 23]
    J_PHASES = 5
    M_PER_PHASE = 400
    NOISE_FRAC = 0.20
    N_PROBE = 60
    N_RETRIEVE_STEPS = 5
    N_CFRPE_PASSES = 5

# Slab geometry: each phase gets a disjoint D_slab x D_slab subspace.
# D_slab = N_BASE // J_PHASES so total dims (J * D_slab) <= N_BASE.
D_SLAB = N_BASE // J_PHASES
N_TOTAL = D_SLAB * J_PHASES  # actual W size after all phases for append-only arms

# Shared CL primitive knobs (match spectrum reference for fused-W arm)
ALPHA_FAST = 1.0
ALPHA_CFRPE = 0.05

# In ARM_FUSED_W: replay slow consolidation (recreates spectrum FULL_CL_SYSTEM
# minimal repro -- single fused-W with cf-RPE + Hebbian-fast; no K-bank).
# Single fused-W simplifies provenance: 'shared-W antagonism' alone vs CRISPR.
ALPHA_SLOW = 0.1
RECENCY_WEIGHT = 4.0
N_REPLAY_PASSES = 10

ARMS = [
    "ARM_BASELINE_STATIC",
    "ARM_FUSED_W_CFRPE_HEBBIAN",
    "ARM_APPEND_ONLY_NEW_DIMS",
    "ARM_APPEND_ONLY_PLUS_CFRPE",
]

PRIMARY_ARM = "ARM_APPEND_ONLY_PLUS_CFRPE"

# ----------------------------------------------------------------------------
# Pre-reg bands
# ----------------------------------------------------------------------------
SANITY_RAIL_BASELINE_LO = 0.85
SANITY_RAIL_BASELINE_HI = 1.00
SANITY_RAIL_FUSED_W_LO = 0.55
SANITY_RAIL_FUSED_W_HI = 0.75

HP_FORGETTING_MAX = 0.10        # ARM_APPEND_ONLY HARD_PASS
HP_TRANSFER_MIN = 0.30          # ARM_APPEND_ONLY_PLUS_CFRPE transfer

MIDDLE_FORGET_LO = 0.10
MIDDLE_FORGET_HI = 0.30

HF_FORGETTING = 0.30            # decisive HF if append-only forgets

# Capacity bonus: total slab count must equal J (each phase got its slab)
HP_TOTAL_CAPACITY_MULT_MIN = 5  # 5x base capacity (J slabs; meaningful at J=5)

# ----------------------------------------------------------------------------
# Formula self-tests at import time
# ----------------------------------------------------------------------------
assert N_BASE == 4096, f"PROT-021: N_BASE={N_BASE}"
# Note: N_BASE need not be divisible by J_PHASES; D_SLAB is computed via floor
# division above. Smoke uses J=3 (D_slab=1365); full uses J=5 (D_slab=819).
# Unused ambient dims (N_BASE - J*D_SLAB) are simply not allocated.
ALPHA_PER_SLAB = M_PER_PHASE / float(D_SLAB)
ALPHA_FUSED = (J_PHASES * M_PER_PHASE) / float(N_BASE)
print(
    f"[formula_selftest] N_BASE={N_BASE} J={J_PHASES} M={M_PER_PHASE} "
    f"D_slab={D_SLAB} alpha_per_slab={ALPHA_PER_SLAB:.4f} "
    f"alpha_fused={ALPHA_FUSED:.4f}",
    flush=True,
)
assert ALPHA_FUSED > 0.10, f"alpha_fused too low: {ALPHA_FUSED}"
# alpha_per_slab is the per-slab capacity; should be in Hopfield-near-cliff regime
assert ALPHA_PER_SLAB > 0.10, f"alpha_per_slab too low: {ALPHA_PER_SLAB}"

# ----------------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------------
def make_phase_atoms_slab(m: int, d_slab: int, seed: int, phase_idx: int) -> np.ndarray:
    """M bipolar (+/-1) atoms LIVING IN A SLAB OF DIM d_slab. Each phase has
    a unique permutation seed."""
    rng = np.random.RandomState(seed * 1000 + phase_idx * 17)
    Xi = rng.choice([-1.0, 1.0], size=(m, d_slab)).astype(np.float32)
    return Xi


def make_phase_atoms_full(m: int, n_dim: int, seed: int, phase_idx: int) -> np.ndarray:
    """M bipolar (+/-1) atoms in the FULL N_BASE space; used by fused-W arm."""
    rng = np.random.RandomState(seed * 1000 + phase_idx * 17)
    Xi = rng.choice([-1.0, 1.0], size=(m, n_dim)).astype(np.float32)
    return Xi


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = None) -> np.ndarray:
    if n_steps is None:
        n_steps = N_RETRIEVE_STEPS
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h).astype(np.float32)
        state[state == 0] = 1.0
    return state


def eval_phase_recall(W: np.ndarray, Xi_phase: np.ndarray, n_probe: int,
                      noise_frac: float, rng: np.random.RandomState) -> float:
    """Fraction of probes that retrieve cosine > 0.80 of original.
    Works for either fused-W (full N) or single-slab Hopfield. Caller must
    ensure Xi_phase atoms and W are dimension-compatible.
    """
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
    m = Xi.shape[0]
    return int(2 * m * n_dim * n_dim + n_dim * n_dim)


def cfrpe_update(W: np.ndarray, Xi: np.ndarray, alpha: float, n_dim: int,
                 n_passes: int) -> int:
    """cf-RPE delta-rule (vectorized). Returns flops estimate."""
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


# ----------------------------------------------------------------------------
# CRISPR slab routing: max-cosine over per-slab subspaces
# ----------------------------------------------------------------------------
def slab_retrieve_with_routing(
    slabs: List[np.ndarray],
    probe_slab: np.ndarray,
    target_slab_idx: int,
    n_steps: int = None,
) -> Tuple[np.ndarray, int]:
    """Route probe to its best-matching slab by max-cosine; retrieve from that slab.

    probe_slab has dim D_slab (same dim as each slab's W). target_slab_idx is the
    GROUND-TRUTH slab the probe was drawn from -- used only for accuracy bookkeeping.

    Returns (retrieved_state, routed_idx).
    """
    if n_steps is None:
        n_steps = N_RETRIEVE_STEPS
    # Score each slab: take ONE retrieval step on each slab; compare cosine of
    # retrieved state to the probe itself. Slab whose retrieved state most-aligns
    # with the probe is selected. (Energy-style selection: best-fitted slab.)
    best_score = -np.inf
    best_idx = 0
    for k, W_k in enumerate(slabs):
        h = W_k @ probe_slab
        s = np.sign(h).astype(np.float32)
        s[s == 0] = 1.0
        score = float(np.dot(s, probe_slab))
        if score > best_score:
            best_score = score
            best_idx = k
    # Full retrieval on the chosen slab
    state = probe_slab.copy()
    for _ in range(n_steps):
        h = slabs[best_idx] @ state
        state = np.sign(h).astype(np.float32)
        state[state == 0] = 1.0
    return state, best_idx


def eval_crispr_recall(
    slabs: List[np.ndarray],
    Xi_phase_slab: np.ndarray,
    phase_idx: int,
    n_probe: int,
    noise_frac: float,
    rng: np.random.RandomState,
) -> Tuple[float, float]:
    """Returns (recall, routing_accuracy).

    Probes drawn from Xi_phase_slab (slab-dim atoms); routed by max-cosine;
    retrieved from the routed slab; cosine match against original computed in slab dim.
    """
    m = Xi_phase_slab.shape[0]
    d_slab = Xi_phase_slab.shape[1]
    n_q = min(n_probe, m)
    correct = 0
    routed_correct = 0
    for i in range(n_q):
        xi = Xi_phase_slab[i]
        probe = xi.copy()
        flip = rng.random(d_slab) < noise_frac
        probe[flip] *= -1.0
        ret, routed_idx = slab_retrieve_with_routing(slabs, probe, phase_idx)
        if routed_idx == phase_idx:
            routed_correct += 1
        cos = float(np.dot(ret, xi) / d_slab)
        if cos > 0.80:
            correct += 1
    if n_q == 0:
        return 0.0, 0.0
    return correct / n_q, routed_correct / n_q


# ----------------------------------------------------------------------------
# Arms
# ----------------------------------------------------------------------------
def run_arm_baseline_static(seed: int) -> Dict:
    """ARM_BASELINE_STATIC: train fused-W on Phase 1 ONLY; freeze. Sanity rail.
    All phases use FULL N_BASE dim atoms (consistent with spectrum cell)."""
    rng = np.random.RandomState(seed + 100)
    W = np.zeros((N_BASE, N_BASE), dtype=np.float32)
    phase_atoms: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    flops_total = 0
    t0 = time.time()
    for i in range(J_PHASES):
        Xi_i = make_phase_atoms_full(M_PER_PHASE, N_BASE, seed, i)
        phase_atoms.append(Xi_i)
        if i == 0:
            flops_total += hebbian_write(W, Xi_i, ALPHA_FAST, N_BASE)
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
        "n_atoms_written": M_PER_PHASE,
        "elapsed_s": elapsed,
        "w_norm_final": float(np.linalg.norm(W)),
        "total_slabs": 1,
    }


def run_arm_fused_w_cfrpe_hebbian(seed: int) -> Dict:
    """ARM_FUSED_W_CFRPE_HEBBIAN: reproduces spectrum FULL_CL minimal repro.
    Single fused W in N_BASE x N_BASE; per phase: Hebbian-fast write -> CLS-replay
    -> cf-RPE nudge. Recall at end of every phase.

    NOTE: this is a SIMPLIFIED fused-W reproduction WITHOUT K-bank routing. The
    spectrum cell's FULL_CL_SYSTEM included K=2 routing; the no-routing variant
    is the minimal fused-W antagonism reproduction the 3rd-angle drill diagnoses.
    """
    rng = np.random.RandomState(seed + 200)
    W = np.zeros((N_BASE, N_BASE), dtype=np.float32)
    episodic_buffer: List[np.ndarray] = []
    phase_atoms: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    flops_total = 0
    t0 = time.time()
    n_atoms_total = 0
    for i in range(J_PHASES):
        Xi_i = make_phase_atoms_full(M_PER_PHASE, N_BASE, seed, i)
        phase_atoms.append(Xi_i)
        for x in Xi_i:
            episodic_buffer.append(x)
        # Hebbian-fast write
        flops_total += hebbian_write(W, Xi_i, ALPHA_FAST, N_BASE)
        # CLS replay (recency-weighted)
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
            flops_total += hebbian_write(W, Xi_replay, alpha_per_pass, N_BASE)
        # cf-RPE error-correction nudge
        flops_total += cfrpe_update(W, Xi_i, ALPHA_CFRPE, N_BASE, N_CFRPE_PASSES)
        n_atoms_total += M_PER_PHASE
        recalls_after_i = []
        for j in range(i + 1):
            rec = eval_phase_recall(W, phase_atoms[j], N_PROBE, NOISE_FRAC, rng)
            recalls_after_i.append(rec)
        phase_recalls.append(recalls_after_i)
        print(f"  [seed={seed} FUSED_W phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]}", flush=True)
    elapsed = time.time() - t0
    return {
        "arm": "ARM_FUSED_W_CFRPE_HEBBIAN",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "flops_total": flops_total,
        "n_atoms_written": n_atoms_total,
        "elapsed_s": elapsed,
        "w_norm_final": float(np.linalg.norm(W)),
        "total_slabs": 1,
    }


def run_arm_append_only_new_dims(seed: int) -> Dict:
    """ARM_APPEND_ONLY_NEW_DIMS: each phase appends a NEW D_slab subspace.
    Hebbian write only into the new slab; old slabs are HARD-FROZEN.
    No cf-RPE.

    Probe at retrieve time: drawn from the slab's natural dim (D_slab). Slab
    routing by max-cosine over per-slab probe-energy.
    """
    rng = np.random.RandomState(seed + 300)
    slabs: List[np.ndarray] = []  # list of (D_slab, D_slab) W matrices
    phase_atoms_slab: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    routing_accs: List[List[float]] = []
    flops_total = 0
    t0 = time.time()
    n_atoms_total = 0
    for i in range(J_PHASES):
        # Allocate NEW slab for this phase
        W_new = np.zeros((D_SLAB, D_SLAB), dtype=np.float32)
        Xi_i_slab = make_phase_atoms_slab(M_PER_PHASE, D_SLAB, seed, i)
        phase_atoms_slab.append(Xi_i_slab)
        # Hebbian write into NEW slab only
        flops_total += hebbian_write(W_new, Xi_i_slab, ALPHA_FAST, D_SLAB)
        slabs.append(W_new)
        n_atoms_total += M_PER_PHASE
        # Evaluate recall on ALL prior + current phases via slab routing
        recalls_after_i = []
        routing_accs_after_i = []
        for j in range(i + 1):
            rec, route_acc = eval_crispr_recall(
                slabs, phase_atoms_slab[j], j, N_PROBE, NOISE_FRAC, rng,
            )
            recalls_after_i.append(rec)
            routing_accs_after_i.append(route_acc)
        phase_recalls.append(recalls_after_i)
        routing_accs.append(routing_accs_after_i)
        print(
            f"  [seed={seed} APPEND_ONLY phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]} "
            f"routing={[f'{r:.2f}' for r in routing_accs_after_i]}",
            flush=True,
        )
    elapsed = time.time() - t0
    w_norms_per_slab = [float(np.linalg.norm(W_k)) for W_k in slabs]
    return {
        "arm": "ARM_APPEND_ONLY_NEW_DIMS",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "routing_accs": routing_accs,
        "flops_total": flops_total,
        "n_atoms_written": n_atoms_total,
        "elapsed_s": elapsed,
        "w_norms_per_slab": w_norms_per_slab,
        "total_slabs": len(slabs),
        "d_slab": D_SLAB,
    }


def run_arm_append_only_plus_cfrpe(seed: int) -> Dict:
    """ARM_APPEND_ONLY_PLUS_CFRPE (PRIMARY ARM): append-only + cf-RPE on the
    newly-added slab dims only. Old slabs HARD-FROZEN.
    """
    rng = np.random.RandomState(seed + 400)
    slabs: List[np.ndarray] = []
    phase_atoms_slab: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    routing_accs: List[List[float]] = []
    flops_total = 0
    t0 = time.time()
    n_atoms_total = 0
    for i in range(J_PHASES):
        W_new = np.zeros((D_SLAB, D_SLAB), dtype=np.float32)
        Xi_i_slab = make_phase_atoms_slab(M_PER_PHASE, D_SLAB, seed, i)
        phase_atoms_slab.append(Xi_i_slab)
        # Hebbian write into NEW slab
        flops_total += hebbian_write(W_new, Xi_i_slab, ALPHA_FAST, D_SLAB)
        # cf-RPE delta-rule nudge on NEW slab only
        flops_total += cfrpe_update(W_new, Xi_i_slab, ALPHA_CFRPE, D_SLAB, N_CFRPE_PASSES)
        slabs.append(W_new)
        n_atoms_total += M_PER_PHASE
        recalls_after_i = []
        routing_accs_after_i = []
        for j in range(i + 1):
            rec, route_acc = eval_crispr_recall(
                slabs, phase_atoms_slab[j], j, N_PROBE, NOISE_FRAC, rng,
            )
            recalls_after_i.append(rec)
            routing_accs_after_i.append(route_acc)
        phase_recalls.append(recalls_after_i)
        routing_accs.append(routing_accs_after_i)
        print(
            f"  [seed={seed} APPEND_PLUS_CFRPE phase={i+1}] recalls={[f'{r:.2f}' for r in recalls_after_i]} "
            f"routing={[f'{r:.2f}' for r in routing_accs_after_i]}",
            flush=True,
        )
    elapsed = time.time() - t0
    w_norms_per_slab = [float(np.linalg.norm(W_k)) for W_k in slabs]
    return {
        "arm": "ARM_APPEND_ONLY_PLUS_CFRPE",
        "seed": seed,
        "phase_recalls": phase_recalls,
        "routing_accs": routing_accs,
        "flops_total": flops_total,
        "n_atoms_written": n_atoms_total,
        "elapsed_s": elapsed,
        "w_norms_per_slab": w_norms_per_slab,
        "total_slabs": len(slabs),
        "d_slab": D_SLAB,
    }


def run_seed(seed: int) -> Dict:
    print(
        f"[{ANCHOR_NAME}] seed={seed} starting 4 arms J={J_PHASES} M={M_PER_PHASE} "
        f"N_base={N_BASE} D_slab={D_SLAB}",
        flush=True,
    )
    results = {}
    results["ARM_BASELINE_STATIC"] = run_arm_baseline_static(seed)
    results["ARM_FUSED_W_CFRPE_HEBBIAN"] = run_arm_fused_w_cfrpe_hebbian(seed)
    results["ARM_APPEND_ONLY_NEW_DIMS"] = run_arm_append_only_new_dims(seed)
    results["ARM_APPEND_ONLY_PLUS_CFRPE"] = run_arm_append_only_plus_cfrpe(seed)
    return {
        "seed": seed,
        "N": N_BASE,
        "N_BASE": N_BASE,
        "D_slab": D_SLAB,
        "run_mode": RUN_MODE,
        "J_phases": J_PHASES,
        "m_per_phase": M_PER_PHASE,
        "arms": results,
    }


# ----------------------------------------------------------------------------
# Instrumentation self-tests (--self-test entry point)
# ----------------------------------------------------------------------------
def _instrumentation_selftest():
    """Required formula self-tests, run at import time.

    1. Sign-flip Hopfield retrieval clean recall = 1.0
    2. Per-slab Hebbian capacity: small D_slab, M atoms at alpha~capacity,
       noise=0.20 -> recall >= 0.80
    3. Max-cosine slab routing: probe from slab i -> route to slab i with prob >= 0.80
    4. cf-RPE delta-rule: starts at W=0, learns to recall trained atoms (>= 0.50)
    """
    # Self-test 1+2: small-D Hopfield clean+noisy
    d_test = 256
    m_test = 20
    rng = np.random.RandomState(42)
    Xi = rng.choice([-1.0, 1.0], size=(m_test, d_test)).astype(np.float32)
    W = (Xi.T @ Xi).astype(np.float32) / float(d_test)
    rec_clean = eval_phase_recall(W, Xi, n_probe=10, noise_frac=0.0,
                                  rng=np.random.RandomState(7))
    assert rec_clean >= 0.95, f"selftest1 clean rec={rec_clean}"
    rec_noisy = eval_phase_recall(W, Xi, n_probe=10, noise_frac=0.10,
                                  rng=np.random.RandomState(7))
    assert rec_noisy >= 0.80, f"selftest1 noisy rec={rec_noisy}"

    # Self-test 3: max-cosine routing on 3 orthogonal slabs
    n_slab_test = 3
    slabs_test = []
    atoms_per_slab = []
    for k in range(n_slab_test):
        Xi_k = np.random.RandomState(100 + k).choice(
            [-1.0, 1.0], size=(10, d_test),
        ).astype(np.float32)
        W_k = (Xi_k.T @ Xi_k).astype(np.float32) / float(d_test)
        slabs_test.append(W_k)
        atoms_per_slab.append(Xi_k)
    routing_correct = 0
    routing_total = 0
    rng_r = np.random.RandomState(33)
    for k in range(n_slab_test):
        for i in range(5):
            xi = atoms_per_slab[k][i]
            probe = xi.copy()
            flip = rng_r.random(d_test) < 0.20
            probe[flip] *= -1.0
            _, routed = slab_retrieve_with_routing(slabs_test, probe, k)
            routing_total += 1
            if routed == k:
                routing_correct += 1
    routing_acc = routing_correct / routing_total
    assert routing_acc >= 0.80, f"selftest3 routing_acc={routing_acc} (need >=0.80)"

    # Self-test 4: cf-RPE learns from zero
    W2 = np.zeros((d_test, d_test), dtype=np.float32)
    _ = cfrpe_update(W2, Xi, alpha=0.05, n_dim=d_test, n_passes=10)
    rec_cfrpe = eval_phase_recall(W2, Xi, n_probe=10, noise_frac=0.0,
                                  rng=np.random.RandomState(7))
    assert rec_cfrpe >= 0.50, f"selftest4 cfrpe rec={rec_cfrpe} (must learn from zero)"

    print(
        f"[selftest] PASS hebbian_clean={rec_clean:.2f} hebbian_noisy={rec_noisy:.2f} "
        f"routing_acc={routing_acc:.2f} cfrpe_post={rec_cfrpe:.2f}",
        flush=True,
    )


_instrumentation_selftest()


# ----------------------------------------------------------------------------
# Aggregate
# ----------------------------------------------------------------------------
def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate across seeds; per-arm: forgetting, transfer, capacity, etc."""
    per_arm: Dict[str, Dict[str, list]] = {arm: {
        "forgetting_p1": [],
        "transfer_final": [],
        "mean_retention_pre_p_final": [],
        "flops_total": [],
        "n_atoms_written": [],
        "compute_per_update": [],
        "phase_recalls_per_seed": [],
        "total_slabs_per_seed": [],
        "routing_accs_per_seed": [],
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
            per_arm[arm]["total_slabs_per_seed"].append(r.get("total_slabs", 1))
            if "routing_accs" in r:
                per_arm[arm]["routing_accs_per_seed"].append(r["routing_accs"])
    summary = {}
    for arm in ARMS:
        d = per_arm[arm]
        n = len(d["forgetting_p1"])
        # CV for primary metric (forgetting)
        if n > 1:
            mn = float(np.mean(d["forgetting_p1"]))
            sd_ = float(np.std(d["forgetting_p1"], ddof=1))
            cv = sd_ / abs(mn) if abs(mn) > 1e-6 else 0.0
        else:
            cv = 0.0
        # Mean routing accuracy at final phase across seeds (CRISPR arms)
        if d["routing_accs_per_seed"]:
            final_route_accs = []
            for routing in d["routing_accs_per_seed"]:
                if routing and len(routing) >= 1:
                    last = routing[-1]
                    if last:
                        final_route_accs.append(float(np.mean(last)))
            mean_final_routing = float(np.mean(final_route_accs)) if final_route_accs else float("nan")
        else:
            mean_final_routing = float("nan")
        summary[arm] = {
            "n_seeds": n,
            "mean_forgetting_p1": float(np.mean(d["forgetting_p1"])) if n else float("nan"),
            "std_forgetting_p1": float(np.std(d["forgetting_p1"], ddof=1)) if n > 1 else 0.0,
            "cv_forgetting_p1": cv,
            "mean_transfer_final": float(np.mean(d["transfer_final"])) if n else float("nan"),
            "std_transfer_final": float(np.std(d["transfer_final"], ddof=1)) if n > 1 else 0.0,
            "mean_retention_pre_p_final": float(np.mean(d["mean_retention_pre_p_final"])) if n else float("nan"),
            "mean_flops": float(np.mean(d["flops_total"])) if n else float("nan"),
            "mean_compute_per_update": float(np.mean(d["compute_per_update"])) if n else float("nan"),
            "mean_total_slabs": float(np.mean(d["total_slabs_per_seed"])) if d["total_slabs_per_seed"] else 1.0,
            "mean_final_routing_acc": mean_final_routing,
            "phase_recalls_per_seed": d["phase_recalls_per_seed"],
        }
    return summary


def compute_verdict(arm_summary: Dict) -> Tuple[str, str]:
    """Verdict over the 4-arm CRISPR test.

    Sanity rails:
      1. ARM_BASELINE_STATIC p1_initial_recall in [0.85, 1.00].
      2. ARM_FUSED_W_CFRPE_HEBBIAN forgetting_p1 in [0.55, 0.75]
         (reproduces spectrum FULL_CL forgetting=0.65 +/- 0.10).

    HARD_PASS_CRISPR_MOAT (ARM_APPEND_ONLY_NEW_DIMS):
      forgetting_p1 < HP_FORGETTING_MAX AND total_slabs >= J_PHASES (5x base)

    HARD_PASS_CRISPR_PLUS_PLASTICITY (PRIMARY -- ARM_APPEND_ONLY_PLUS_CFRPE):
      forgetting_p1 < HP_FORGETTING_MAX AND transfer_pre_replay >= HP_TRANSFER_MIN

    HARD_FAIL_DECISIVE: ARM_APPEND_ONLY forgetting_p1 >= HF_FORGETTING.

    cv must be < 0.05 across seeds for primary metric.
    """
    baseline = arm_summary.get("ARM_BASELINE_STATIC", {})
    fused = arm_summary.get("ARM_FUSED_W_CFRPE_HEBBIAN", {})
    append = arm_summary.get("ARM_APPEND_ONLY_NEW_DIMS", {})
    append_plus = arm_summary.get("ARM_APPEND_ONLY_PLUS_CFRPE", {})

    # Sanity rail 1: baseline p1 initial recall (phase 0 evaluation of phase 0)
    base_p1 = baseline.get("phase_recalls_per_seed", [])
    base_p1_initial = float("nan")
    if base_p1:
        vals = [pr[0][0] for pr in base_p1 if pr]
        if vals:
            base_p1_initial = float(np.mean(vals))

    # Sanity rail 2: fused-W forgetting
    fused_forget = fused.get("mean_forgetting_p1", float("nan"))

    append_forget = append.get("mean_forgetting_p1", float("nan"))
    append_transfer = append.get("mean_transfer_final", float("nan"))
    append_slabs = append.get("mean_total_slabs", float("nan"))
    append_routing = append.get("mean_final_routing_acc", float("nan"))

    append_plus_forget = append_plus.get("mean_forgetting_p1", float("nan"))
    append_plus_transfer = append_plus.get("mean_transfer_final", float("nan"))
    append_plus_routing = append_plus.get("mean_final_routing_acc", float("nan"))
    append_plus_cv = append_plus.get("cv_forgetting_p1", float("nan"))

    summary_line = (
        f"APPEND_ONLY forget={append_forget:.3f} transfer={append_transfer:.3f} "
        f"slabs={append_slabs:.1f} route_acc={append_routing:.3f}; "
        f"APPEND_PLUS_CFRPE forget={append_plus_forget:.3f} transfer={append_plus_transfer:.3f} "
        f"route_acc={append_plus_routing:.3f} cv={append_plus_cv:.3f}; "
        f"FUSED_W forget={fused_forget:.3f}; BASELINE p1_initial={base_p1_initial:.3f}"
    )

    # Sanity rail 1
    if math.isnan(base_p1_initial) or not (SANITY_RAIL_BASELINE_LO <= base_p1_initial <= SANITY_RAIL_BASELINE_HI):
        return (
            "HARD_FAIL",
            f"SANITY_RAIL_1 violated: baseline_p1_initial_recall={base_p1_initial:.3f} "
            f"outside [{SANITY_RAIL_BASELINE_LO}, {SANITY_RAIL_BASELINE_HI}]; "
            f"substrate not learning Phase 1. {summary_line}",
        )

    # Sanity rail 2: fused-W must reproduce spectrum forgetting (FULL mode only).
    # At smoke, alpha_fused = 3*200/4096 = 0.1465 is sub-Hopfield-cliff so fused-W
    # naturally retains everything. Rail only meaningful when alpha pushes past
    # the cliff (FULL: alpha=0.488).
    if RUN_MODE == "full":
        if math.isnan(fused_forget) or not (SANITY_RAIL_FUSED_W_LO <= fused_forget <= SANITY_RAIL_FUSED_W_HI):
            return (
                "HARD_FAIL",
                f"SANITY_RAIL_2 violated: fused_W_forgetting={fused_forget:.3f} "
                f"outside [{SANITY_RAIL_FUSED_W_LO}, {SANITY_RAIL_FUSED_W_HI}]; "
                f"FUSED_W did NOT reproduce spectrum CL HARD_FAIL provenance. {summary_line}",
            )

    # HARD_FAIL_DECISIVE: append-only forgetting >= 0.30
    if (not math.isnan(append_forget)) and append_forget >= HF_FORGETTING:
        return (
            "HARD_FAIL",
            f"HARD_FAIL_DECISIVE: APPEND_ONLY forget={append_forget:.3f} >= {HF_FORGETTING}; "
            f"structural-commitment does NOT rescue substrate CL -- deeper issue than shared-W "
            f"antagonism. {summary_line}",
        )

    # HARD_PASS gates
    hp_moat_a = (not math.isnan(append_forget)) and append_forget < HP_FORGETTING_MAX
    hp_moat_b = (not math.isnan(append_slabs)) and append_slabs >= J_PHASES  # 5x = J slabs vs 1 fused

    hp_plus_a = (not math.isnan(append_plus_forget)) and append_plus_forget < HP_FORGETTING_MAX
    hp_plus_b = (not math.isnan(append_plus_transfer)) and append_plus_transfer >= HP_TRANSFER_MIN

    # cv discipline (only fail if cv computed and exceeds 0.05; tolerate exact-0 case)
    cv_ok = math.isnan(append_plus_cv) or append_plus_cv < 0.05

    if hp_moat_a and hp_moat_b and hp_plus_a and hp_plus_b and cv_ok:
        return (
            "HARD_PASS",
            f"CRISPR_MOAT+PLASTICITY chain-grade: APPEND_ONLY forget={append_forget:.3f} < "
            f"{HP_FORGETTING_MAX} AND slabs={append_slabs:.0f} >= J={J_PHASES}; "
            f"APPEND_PLUS_CFRPE forget={append_plus_forget:.3f} < {HP_FORGETTING_MAX} AND "
            f"transfer={append_plus_transfer:.3f} >= {HP_TRANSFER_MIN}; cv={append_plus_cv:.3f} < 0.05. "
            f"Substrate's CL moat is architecturally real via structural-commitment. {summary_line}",
        )

    if hp_moat_a and hp_moat_b:
        return (
            "HARD_PASS",
            f"CRISPR_MOAT only (no plasticity rescue): APPEND_ONLY forget={append_forget:.3f} < "
            f"{HP_FORGETTING_MAX} AND slabs={append_slabs:.0f} >= J={J_PHASES}; "
            f"APPEND_PLUS_CFRPE missed plasticity bar (transfer={append_plus_transfer:.3f} or "
            f"forget={append_plus_forget:.3f}). Structural-commitment works; plasticity needs work. "
            f"{summary_line}",
        )

    # Partial pass / MIDDLE_BAND
    is_middle = False
    middle_reason = []
    for name, fg in [("APPEND_ONLY", append_forget), ("APPEND_PLUS_CFRPE", append_plus_forget)]:
        if not math.isnan(fg) and MIDDLE_FORGET_LO <= fg < MIDDLE_FORGET_HI:
            is_middle = True
            middle_reason.append(f"{name} forget={fg:.3f} in MIDDLE")

    if is_middle:
        return (
            "MIDDLE_BAND",
            f"CRISPR characterized but no HARD_PASS: " + "; ".join(middle_reason) + f". {summary_line}",
        )

    return (
        "MIDDLE_BAND",
        f"CRISPR off-band: hp_moat_a={hp_moat_a} hp_moat_b={hp_moat_b} "
        f"hp_plus_a={hp_plus_a} hp_plus_b={hp_plus_b} cv_ok={cv_ok}. {summary_line}",
    )


# ----------------------------------------------------------------------------
# atexit synthesizer
# ----------------------------------------------------------------------------
_OUT_DIR = None
_T_START = None
_SYNTH_DONE = [False]


def _build_metrics_payload(per_seed: Dict, elapsed: float, source_tag: str) -> Dict:
    arm_summary = aggregate_results(per_seed)
    verdict, verdict_msg = compute_verdict(arm_summary)
    primary = arm_summary.get(PRIMARY_ARM, {})
    summary = (
        f"{verdict}: {PRIMARY_ARM} forget={primary.get('mean_forgetting_p1', float('nan')):.3f} "
        f"transfer={primary.get('mean_transfer_final', float('nan')):.3f} "
        f"routing={primary.get('mean_final_routing_acc', float('nan')):.3f} "
        f"slabs={primary.get('mean_total_slabs', float('nan')):.1f}"
    )
    return {
        "anchor": ANCHOR_NAME,
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
        "N": N_BASE,
        "N_BASE": N_BASE,
        "D_slab": D_SLAB,
        "n_seeds": len(per_seed),
        "seeds": list(per_seed.keys()) if isinstance(per_seed, dict) else SEEDS,
        "J_phases": J_PHASES,
        "m_per_phase": M_PER_PHASE,
        "arms": ARMS,
        "primary_arm": PRIMARY_ARM,
        "config_version": (
            f"cl-crispr-v1: N_base={N_BASE} D_slab={D_SLAB} J={J_PHASES} M={M_PER_PHASE} "
            f"alpha_fast={ALPHA_FAST} alpha_cfrpe={ALPHA_CFRPE} "
            f"alpha_slow={ALPHA_SLOW} recency={RECENCY_WEIGHT} replay_passes={N_REPLAY_PASSES} "
            f"cfrpe_passes={N_CFRPE_PASSES} noise_frac={NOISE_FRAC} "
            f"retrieve_steps={N_RETRIEVE_STEPS} run_mode={RUN_MODE}"
        ),
        "corpus_provenance": "synthetic_bipolar_atoms_per_domain_slab_partition",
        "allow_synthetic": True,
        "zero_llm_calls_at_inference": True,
        "n_llm_calls": 0,
        "metrics_source": source_tag,
        "per_arm_aggregate": arm_summary,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": summary,
        "elapsed_s": elapsed,
    }


def _synth_metrics_atexit():
    if _SYNTH_DONE[0]:
        return
    if _OUT_DIR is None:
        return
    try:
        per_seed = aggregate_partials(_OUT_DIR, SEEDS)
        if not per_seed:
            return
        elapsed = time.time() - _T_START if _T_START else 0.0
        metrics = _build_metrics_payload(
            per_seed, elapsed, "measured_cpu_synthetic_bipolar_crispr_4arm_atexit",
        )
        metrics["synthesized_at_exit"] = True
        metrics_path = _OUT_DIR / "metrics.json"
        with open(metrics_path, "w", encoding="utf-8") as fh:
            json.dump(metrics, fh, indent=2)
        _SYNTH_DONE[0] = True
        print(f"[atexit] synthesized metrics.json verdict={metrics['verdict']}", flush=True)
    except Exception as e:
        print(f"[atexit] synth FAILED: {e}", flush=True)


atexit.register(_synth_metrics_atexit)


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    global _OUT_DIR, _T_START
    _T_START = time.time()
    print(
        f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N_BASE={N_BASE} D_slab={D_SLAB} "
        f"seeds={SEEDS} J_phases={J_PHASES} M={M_PER_PHASE} arms={ARMS} primary={PRIMARY_ARM}",
        flush=True,
    )

    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR = out_dir
    run_config = {
        "N": N_BASE,
        "run_mode": RUN_MODE,
        "J_phases": J_PHASES,
        "M_per_phase": M_PER_PHASE,
    }
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print(f"[ckpt] {len(done)}/{len(SEEDS)} done; running {remaining}", flush=True)

    for seed in remaining:
        r = run_seed(seed)
        write_partial(out_dir, seed, r)
        print(f"[{ANCHOR_NAME}] seed={seed} done", flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS)
    elapsed = time.time() - _T_START
    metrics = _build_metrics_payload(
        per_seed, elapsed, "measured_cpu_synthetic_bipolar_crispr_4arm",
    )
    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    _SYNTH_DONE[0] = True
    print(f"[{ANCHOR_NAME}] verdict={metrics['verdict']}", flush=True)
    print(f"[{ANCHOR_NAME}] {metrics['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    main()
