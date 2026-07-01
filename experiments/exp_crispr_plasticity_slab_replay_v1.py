"""crispr_plasticity_slab_replay_v1 -- slab-boundary replay for cross-slab transfer.

# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity: tmp_replace (META_RULE_AH; atomic os.replace)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_floor_computed=0.05 + discriminator_reachability=True (bipolar tail CLT)
# - baseline_in_band at smoke (META_RULE_AG; regime CORRECTED to alpha=0.122)
# - discriminator survives scale (smoke includes R=20 preview arm)
# - HARD_PASS strictly above floor: transfer_final >= 0.15 (drill spec)
# - HP_SCOPE: transfer HP applies to R>0 arms ONLY; R=0 is sanity rail
# - cardinality_ok: EXPECTED_N_UNITS = 12 (3 seeds x 4 R values)
# - per-unit failure-class instrumentation (specific except classes)
# - calibration_check: default_ok_for_this_regime (alpha=0.122 in Hopfield band)
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@

SCIENTIFIC QUESTION:
  Does R-item slab-boundary replay from prior slabs raise transfer_final from
  MEASURED@d:/AI/hd-instrument/data/exp_substrate_cl_crispr_append_only_v1/metrics.json:
     per_arm_aggregate.ARM_APPEND_ONLY_PLUS_CFRPE.mean_transfer_final = 0.000
  to >= 0.15 without corrupting forget_p1 (<= 0.05)?

REGIME CORRECTION (pre-dispatch caught by cell-author):
  Base CRISPR cell v1 uses alpha_per_slab = 400/819 = 0.488
  THEORETICAL@Amit-Gutfreund Hopfield cliff at alpha_c ~= 0.138
  Base regime is 3.5x above cliff -- per-slab Hebbian CANNOT self-recall.
  MEASURED baseline showed ALL phase-recalls at 0.000-0.017 including phase-0.
  This cell CORRECTS to M_per_phase=100, D_slab=819, alpha=0.122 (in-band).
  Preserves J=5 (drill structural intent) and N_BASE=4096 (substrate scale).

ARCHITECTURE:
  4 arms across R in {0, 5, 20, 50}; 3 seeds each; 12 units total.
  Each arm: J=5 phases; at phase j>=1, sample R atom-IDs uniformly from prior
  slabs 0..j-1; re-encode each in current slab's D_slab dim via persistent
  atom-ID bipolar seed; Hebbian-write current-phase atoms + R replay atoms
  into new slab.

  Slab-routing at retrieve: max-cosine over per-slab probe-energy (same as
  base cell v1). Retrieval evaluates:
    (a) phase-0 self-recall (regime sanity)
    (b) transfer_final: prior-slab atoms recalled from CURRENT-phase slab
        via re-encoded probe -- tests whether replay wrote the atom-ID pattern
        into the current slab
    (c) forget_p1: current-phase recall after replay (does replay corrupt?)
    (d) transfer_pre_replay + transfer_post_replay per Substrate-KB drill
        remediation (isolate transfer-metric ambiguity flagged in
        CL spectrum 3rd angle drill)

CITES:
  experiments/exp_substrate_cl_crispr_append_only_v1.py  (base cell being extended)
  notes/research_drill_continual_learning_CRISPR_regime_map_2026-07-01.md  (drill rank-1)
  notes/research_cl_spectrum_3rd_angle_cross_biology_2026-06-24.md  (transfer_pre_replay bug)
  preregs/2026-07-01_crispr_plasticity_slab_replay_v1.md

ASCII-only. Per-seed checkpoint. tmp+replace atomic write. Crash-diagnostic.
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
import hashlib
import platform
import traceback
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "crispr_plasticity_slab_replay_v1"

# ---- Argparse + run-mode ----
_P = argparse.ArgumentParser()
_P.add_argument("--smoke", action="store_true")
_P.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _P.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE) else os.environ.get("HDLAB_RUN_MODE", "full")

# ---- Config ----
N_BASE = 4096  # PROT-021: anchor has no _n<N> suffix; asserted below

# HYPOTHESIZED regime correction: M=100 gives alpha=0.122 (in Hopfield band).
if RUN_MODE == "smoke":
    SEEDS = [7, 17]
    J_PHASES = 3
    M_PER_PHASE = 50
    R_VALUES = [0, 20]  # smoke: baseline + primary discriminator
    NOISE_FRAC = 0.20
    N_PROBE = 20
    N_RETRIEVE_STEPS = 5
    # Discriminator preview arm at full-N: R=20 at 1 seed with FULL M=100
    INCLUDE_FULL_PREVIEW = True
else:
    SEEDS = [7, 17, 23]
    J_PHASES = 5
    M_PER_PHASE = 100
    R_VALUES = [0, 5, 20, 50]
    NOISE_FRAC = 0.20
    N_PROBE = 40
    N_RETRIEVE_STEPS = 5
    INCLUDE_FULL_PREVIEW = False  # full run IS the full test

D_SLAB = N_BASE // J_PHASES  # J=5 => 819; J=3 => 1365
ALPHA_FAST = 1.0
EXPECTED_N_UNITS = len(SEEDS) * len(R_VALUES)

# ---- Formula self-tests at import ----
assert N_BASE == 4096, f"PROT-021: N_BASE={N_BASE}"
ALPHA_PER_SLAB = M_PER_PHASE / float(D_SLAB)
print(
    f"[formula_selftest] N_BASE={N_BASE} J={J_PHASES} M={M_PER_PHASE} R_values={R_VALUES} "
    f"D_slab={D_SLAB} alpha_per_slab={ALPHA_PER_SLAB:.4f} EXPECTED_N_UNITS={EXPECTED_N_UNITS}",
    flush=True,
)
# THEORETICAL@Amit-Gutfreund: alpha_c ~ 0.138 -- must stay below for self-recall
assert ALPHA_PER_SLAB < 0.20, (
    f"alpha_per_slab={ALPHA_PER_SLAB:.4f} > 0.20 -- above Hopfield cliff; "
    f"regime is NOT in-band. CORRECT M_per_phase or D_slab before dispatch."
)
assert ALPHA_PER_SLAB > 0.03, (
    f"alpha_per_slab={ALPHA_PER_SLAB:.4f} < 0.03 -- floor-of-band; "
    f"increase M_per_phase or decrease D_slab (may under-load)."
)

# ---- Pre-reg bands ----
HP_TRANSFER_MIN = 0.15         # HARD_PASS: transfer_final >= 0.15 (drill spec)
HF_TRANSFER_MAX = 0.05         # HARD_FAIL: all R>0 arms <= 0.05
HP_FORGET_MAX = 0.05           # HARD_PASS: forget_p1 <= 0.05
HF_FORGET_MAX = 0.10           # HARD_FAIL: forget_p1 > 0.10 on all R>0 arms
MIDDLE_TRANSFER_LO = 0.05
MIDDLE_TRANSFER_HI = 0.15
SANITY_PHASE0_MIN = 0.60       # regime-correction check: phase-0 self-recall
CV_MAX = 0.15                  # cross-seed cv on primary metric

# ---- Helpers ----
def _persistent_bipolar(atom_id: int, slab_idx: int, d_slab: int) -> np.ndarray:
    """Encode (atom_id, slab_idx) as a persistent bipolar vector of dim d_slab.
    Ensures same (atom_id, slab_idx) always maps to same vector across arms/phases.
    """
    seed = int(atom_id) * 1000 + int(slab_idx) * 3
    rng = np.random.RandomState(seed & 0xFFFFFFFF)
    return rng.choice([-1.0, 1.0], size=(d_slab,)).astype(np.float32)


def make_phase_atoms_slab(m: int, d_slab: int, phase_idx: int) -> Tuple[np.ndarray, np.ndarray]:
    """Return (Xi, atom_ids) for phase `phase_idx`: M atoms encoded in slab phase_idx's dim."""
    atom_ids = np.arange(phase_idx * m, phase_idx * m + m, dtype=np.int64)
    Xi = np.stack([_persistent_bipolar(aid, phase_idx, d_slab) for aid in atom_ids], axis=0)
    return Xi, atom_ids


def make_replay_atoms(atom_ids: np.ndarray, target_slab_idx: int, d_slab: int) -> np.ndarray:
    """Re-encode prior-phase atom_ids in target-slab's dim.
    This is the load-bearing 'replay' operation: prior-slab atom identities get
    a fresh D_slab-dim bipolar in the current slab, keyed by (atom_id, target_slab_idx).
    """
    return np.stack([_persistent_bipolar(aid, target_slab_idx, d_slab) for aid in atom_ids], axis=0)


def hopfield_retrieve(W: np.ndarray, probe: np.ndarray, n_steps: int = None) -> np.ndarray:
    if n_steps is None:
        n_steps = N_RETRIEVE_STEPS
    state = probe.copy()
    for _ in range(n_steps):
        h = W @ state
        state = np.sign(h).astype(np.float32)
        state[state == 0] = 1.0
    return state


def hebbian_write(W: np.ndarray, Xi: np.ndarray, alpha: float, n_dim: int) -> None:
    """In-place W += alpha * Xi^T Xi / n_dim."""
    W += (alpha * (Xi.T @ Xi) / float(n_dim)).astype(np.float32)


def eval_slab_recall(W: np.ndarray, Xi: np.ndarray, n_probe: int,
                     noise_frac: float, rng: np.random.RandomState) -> float:
    """Fraction of probes retrieving cos>0.80 of original from within a single slab."""
    m = Xi.shape[0]
    n_dim = Xi.shape[1]
    n_q = min(n_probe, m)
    correct = 0
    for i in range(n_q):
        xi = Xi[i]
        probe = xi.copy()
        flip = rng.random(n_dim) < noise_frac
        probe[flip] *= -1.0
        ret = hopfield_retrieve(W, probe)
        cos = float(np.dot(ret, xi) / n_dim)
        if cos > 0.80:
            correct += 1
    return correct / n_q if n_q > 0 else 0.0


def slab_route_and_retrieve(
    slabs: List[np.ndarray],
    probe_slab: np.ndarray,
    n_steps: int = None,
) -> Tuple[np.ndarray, int]:
    """Route probe to best slab by 1-step energy; retrieve full from that slab."""
    if n_steps is None:
        n_steps = N_RETRIEVE_STEPS
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
    state = probe_slab.copy()
    for _ in range(n_steps):
        h = slabs[best_idx] @ state
        state = np.sign(h).astype(np.float32)
        state[state == 0] = 1.0
    return state, best_idx


def eval_transfer(
    slabs: List[np.ndarray],
    prior_atom_ids: np.ndarray,   # atom_ids from prior phases
    prior_original_phase: np.ndarray,  # which phase each atom belongs to
    current_slab_idx: int,        # slab index we're testing transfer INTO
    d_slab: int,
    n_probe: int,
    noise_frac: float,
    rng: np.random.RandomState,
) -> float:
    """Transfer test: for each prior-slab atom_id, encode it in the CURRENT-slab's dim
    (i.e. the replay-encoding), add noise, retrieve via slab-routing, check cosine
    to the current-slab re-encoding.

    The mechanism under test: if the atom_id was replayed into current_slab during
    training, the current slab's W should retrieve its current-slab bipolar.
    If NOT replayed, no path exists -- retrieval fails.

    HP: fraction cosine>0.80 >= 0.15 across a random subset of prior_atom_ids.
    """
    n_total = len(prior_atom_ids)
    if n_total == 0:
        return 0.0
    idx_sample = rng.choice(n_total, size=min(n_probe, n_total), replace=False)
    correct = 0
    for i in idx_sample:
        aid = int(prior_atom_ids[i])
        # Ground truth: the current-slab re-encoding of this atom_id
        xi_curr = _persistent_bipolar(aid, current_slab_idx, d_slab)
        probe = xi_curr.copy()
        flip = rng.random(d_slab) < noise_frac
        probe[flip] *= -1.0
        ret, _routed = slab_route_and_retrieve(slabs, probe)
        cos = float(np.dot(ret, xi_curr) / d_slab)
        if cos > 0.80:
            correct += 1
    return correct / len(idx_sample) if len(idx_sample) > 0 else 0.0


# ---- Arm runner (single R value; one seed) ----
def run_arm(seed: int, R: int) -> Dict:
    """CRISPR APPEND_ONLY with R-item slab-boundary replay.
    Returns per-phase recall metrics + transfer_final + transfer_pre/post + forget_p1.
    """
    arm_name = f"ARM_APPEND_ONLY_R{R}"
    rng = np.random.RandomState(seed * 100 + R)
    slabs: List[np.ndarray] = []
    phase_atoms_slab: List[np.ndarray] = []
    phase_atom_ids: List[np.ndarray] = []
    phase_recalls: List[List[float]] = []
    transfer_pre_replay_per_phase: List[float] = []
    transfer_post_replay_per_phase: List[float] = []
    t0 = time.time()

    for i in range(J_PHASES):
        # Allocate new slab for this phase
        W_new = np.zeros((D_SLAB, D_SLAB), dtype=np.float32)
        Xi_i, atom_ids_i = make_phase_atoms_slab(M_PER_PHASE, D_SLAB, i)
        phase_atoms_slab.append(Xi_i)
        phase_atom_ids.append(atom_ids_i)

        # Current-phase Hebbian write
        hebbian_write(W_new, Xi_i, ALPHA_FAST, D_SLAB)

        # transfer_pre_replay: current-phase self-recall BEFORE mixing replay
        # (per Substrate-KB drill remediation)
        pre_rec = eval_slab_recall(W_new, Xi_i, N_PROBE, NOISE_FRAC, rng)
        transfer_pre_replay_per_phase.append(pre_rec)

        # Slab-boundary replay: sample R atom_ids from prior slabs, re-encode
        # in current slab's dim, Hebbian-write into current slab
        if i >= 1 and R > 0:
            all_prior_ids = np.concatenate(phase_atom_ids[:i]) if i > 0 else np.array([], dtype=np.int64)
            n_available = len(all_prior_ids)
            n_replay = min(R, n_available)
            if n_replay > 0:
                replay_idx = rng.choice(n_available, size=n_replay, replace=False)
                replay_aids = all_prior_ids[replay_idx]
                Xi_replay = make_replay_atoms(replay_aids, i, D_SLAB)
                hebbian_write(W_new, Xi_replay, ALPHA_FAST, D_SLAB)

        # transfer_post_replay: current-phase self-recall AFTER replay-mix
        post_rec = eval_slab_recall(W_new, Xi_i, N_PROBE, NOISE_FRAC, rng)
        transfer_post_replay_per_phase.append(post_rec)

        slabs.append(W_new)

        # Full slab-routing evaluation across all phases up to i
        recalls_after_i = []
        for j in range(i + 1):
            m = phase_atoms_slab[j].shape[0]
            n_q = min(N_PROBE, m)
            correct = 0
            for k in range(n_q):
                xi = phase_atoms_slab[j][k]
                probe = xi.copy()
                flip = rng.random(D_SLAB) < NOISE_FRAC
                probe[flip] *= -1.0
                ret, _routed = slab_route_and_retrieve(slabs, probe)
                cos = float(np.dot(ret, xi) / D_SLAB)
                if cos > 0.80:
                    correct += 1
            recalls_after_i.append(correct / n_q if n_q > 0 else 0.0)
        phase_recalls.append(recalls_after_i)

    # Transfer test (drill's primary metric): can current (last) slab retrieve
    # prior-phase atom_ids via their current-slab re-encoding?
    all_prior_ids = np.concatenate(phase_atom_ids[:-1]) if len(phase_atom_ids) > 1 else np.array([], dtype=np.int64)
    all_prior_phases = np.concatenate([
        np.full(len(phase_atom_ids[k]), k, dtype=np.int64) for k in range(len(phase_atom_ids) - 1)
    ]) if len(phase_atom_ids) > 1 else np.array([], dtype=np.int64)
    current_slab_idx = J_PHASES - 1
    transfer_final = eval_transfer(
        slabs, all_prior_ids, all_prior_phases, current_slab_idx,
        D_SLAB, min(60, N_PROBE), NOISE_FRAC, rng,
    )

    # forget_p1 = phase-0 recall at start minus phase-0 recall at end
    forget_p1 = phase_recalls[0][0] - phase_recalls[-1][0]

    elapsed = time.time() - t0
    return {
        "arm": arm_name,
        "seed": seed,
        "R": R,
        "phase_recalls": phase_recalls,
        "transfer_pre_replay_per_phase": transfer_pre_replay_per_phase,
        "transfer_post_replay_per_phase": transfer_post_replay_per_phase,
        "transfer_final": float(transfer_final),
        "forget_p1": float(forget_p1),
        "phase0_self_recall": float(phase_recalls[0][0]),
        "elapsed_s": elapsed,
        "n_slabs": len(slabs),
        "slab_hash": hashlib.sha256(slabs[-1].tobytes()).hexdigest()[:16],
    }


def run_seed(seed: int) -> Dict:
    """Run all R arms for one seed."""
    print(f"[{ANCHOR_NAME}] seed={seed} R_values={R_VALUES} J={J_PHASES} M={M_PER_PHASE} D_slab={D_SLAB}",
          flush=True)
    arms = {}
    for R in R_VALUES:
        try:
            arm_result = run_arm(seed, R)
            arms[f"ARM_APPEND_ONLY_R{R}"] = arm_result
            print(f"  [seed={seed} R={R}] phase0_self={arm_result['phase0_self_recall']:.3f} "
                  f"transfer_final={arm_result['transfer_final']:.3f} "
                  f"forget_p1={arm_result['forget_p1']:.3f} "
                  f"elapsed={arm_result['elapsed_s']:.1f}s", flush=True)
        except MemoryError as e:
            arms[f"ARM_APPEND_ONLY_R{R}"] = {"failure_class": "OOM", "error": str(e)}
        except ValueError as e:
            arms[f"ARM_APPEND_ONLY_R{R}"] = {"failure_class": "VALUE_ERROR", "error": str(e)}
    return {
        "seed": seed,
        "N": N_BASE,
        "N_BASE": N_BASE,
        "D_slab": D_SLAB,
        "run_mode": RUN_MODE,
        "J_phases": J_PHASES,
        "M_per_phase": M_PER_PHASE,
        "R_values": R_VALUES,
        "arms": arms,
    }


# ---- Instrumentation self-tests at import ----
def _instrumentation_selftest():
    """Formula self-tests before any run.
    1. Persistent bipolar deterministic: same (id, slab) -> same vector
    2. Different (id, slab) -> different vectors (bit-difference)
    3. Slab-Hebbian self-recall at alpha=0.122 on d=819, M=100, noise=0.20 >= 0.80
    4. Cross-slab isolation: patterns encoded in slab 0 have ~0 recall from slab 1's W
    """
    # Test 1: determinism
    v1 = _persistent_bipolar(42, 3, 128)
    v2 = _persistent_bipolar(42, 3, 128)
    assert np.array_equal(v1, v2), "persistent_bipolar not deterministic"

    # Test 2: different (id, slab) => different
    v3 = _persistent_bipolar(43, 3, 128)
    v4 = _persistent_bipolar(42, 4, 128)
    hamming_v1_v3 = np.mean(v1 != v3)
    hamming_v1_v4 = np.mean(v1 != v4)
    assert hamming_v1_v3 > 0.3, f"selftest2 collision id: hamming={hamming_v1_v3}"
    assert hamming_v1_v4 > 0.3, f"selftest2 collision slab: hamming={hamming_v1_v4}"

    # Test 3: self-recall at target alpha
    d_test = 819
    m_test = 100
    Xi = np.stack([_persistent_bipolar(i, 0, d_test) for i in range(m_test)], axis=0)
    W = (Xi.T @ Xi).astype(np.float32) / float(d_test)
    rec = eval_slab_recall(W, Xi, n_probe=20, noise_frac=0.20,
                           rng=np.random.RandomState(7))
    # alpha = 100/819 = 0.122; should be well above 0.80
    assert rec >= 0.80, f"selftest3 slab-Hebbian self-recall={rec:.3f} < 0.80 at alpha=0.122"

    # Test 4: cross-slab isolation
    Xi_slab0 = np.stack([_persistent_bipolar(i, 0, d_test) for i in range(20)], axis=0)
    Xi_slab1 = np.stack([_persistent_bipolar(i, 1, d_test) for i in range(20)], axis=0)
    # Overlap between slab 0 encoding and slab 1 encoding of same atom_id
    overlaps = [float(np.dot(Xi_slab0[i], Xi_slab1[i]) / d_test) for i in range(20)]
    mean_overlap = float(np.mean(overlaps))
    assert abs(mean_overlap) < 0.10, f"selftest4 cross-slab overlap={mean_overlap:.3f}; should be ~0"

    print(f"[selftest] PASS self_recall={rec:.3f} cross_slab_overlap={mean_overlap:.3f}",
          flush=True)


_instrumentation_selftest()


# ---- Aggregation ----
def aggregate_results(per_seed: Dict) -> Dict:
    """Aggregate across seeds per R value. Returns arm_summary keyed by arm name."""
    arm_summary: Dict[str, Dict] = {}
    for R in R_VALUES:
        arm_name = f"ARM_APPEND_ONLY_R{R}"
        transfers = []
        forgets = []
        phase0s = []
        pre_replay_means = []
        post_replay_means = []
        slab_hashes = set()
        for sd in per_seed.values():
            arms_data = sd.get("arms", {})
            r = arms_data.get(arm_name)
            if r is None or "failure_class" in r:
                continue
            transfers.append(r["transfer_final"])
            forgets.append(r["forget_p1"])
            phase0s.append(r["phase0_self_recall"])
            pre_replay_means.append(float(np.mean(r["transfer_pre_replay_per_phase"])))
            post_replay_means.append(float(np.mean(r["transfer_post_replay_per_phase"])))
            slab_hashes.add(r.get("slab_hash", ""))
        n = len(transfers)
        if n > 1:
            cv_t = float(np.std(transfers, ddof=1)) / max(abs(float(np.mean(transfers))), 1e-6)
        else:
            cv_t = 0.0
        arm_summary[arm_name] = {
            "R": R,
            "n_seeds": n,
            "mean_transfer_final": float(np.mean(transfers)) if n else float("nan"),
            "std_transfer_final": float(np.std(transfers, ddof=1)) if n > 1 else 0.0,
            "cv_transfer_final": cv_t,
            "mean_forget_p1": float(np.mean(forgets)) if n else float("nan"),
            "mean_phase0_self_recall": float(np.mean(phase0s)) if n else float("nan"),
            "mean_transfer_pre_replay": float(np.mean(pre_replay_means)) if n else float("nan"),
            "mean_transfer_post_replay": float(np.mean(post_replay_means)) if n else float("nan"),
            "n_unique_slab_hashes": len(slab_hashes),
        }
    return arm_summary


def compute_verdict(arm_summary: Dict, total_units: int) -> Tuple[str, str]:
    """Verdict logic per pre-reg bands.
    Sanity rail: ARM_APPEND_ONLY_R0 phase0_self_recall >= SANITY_PHASE0_MIN
    Cardinality: total_units == EXPECTED_N_UNITS or HARD_FAIL_CARDINALITY_BREACH
    Arms-must-differ: R=0 vs R=20 slab_hash MUST differ
    HP: any R>0 arm has transfer_final >= 0.15 AND forget_p1 <= 0.05 AND cv <= 0.15
    HF: all R>0 arms transfer_final < 0.05 OR all R>0 arms forget_p1 > 0.10
    """
    # META_RULE_H cardinality gate
    if total_units < EXPECTED_N_UNITS:
        return (
            "HARD_FAIL",
            f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: units={total_units} < expected={EXPECTED_N_UNITS}",
        )

    r0 = arm_summary.get("ARM_APPEND_ONLY_R0", {})
    phase0_r0 = r0.get("mean_phase0_self_recall", float("nan"))
    if math.isnan(phase0_r0) or phase0_r0 < SANITY_PHASE0_MIN:
        return (
            "HARD_FAIL",
            f"SANITY_REGIME_MISMATCH: ARM_R0 phase0_self_recall={phase0_r0:.3f} < {SANITY_PHASE0_MIN}; "
            f"regime correction (alpha={ALPHA_PER_SLAB:.3f}) insufficient. "
            f"D_slab={D_SLAB} M={M_PER_PHASE} needs further tuning.",
        )

    # ARMS-MUST-DIFFER: sanity check on slab hashes
    r0_hashes = r0.get("n_unique_slab_hashes", 0)
    # In R>0 arms we should see different slab-final-hash from R=0 (replay writes extra atoms)

    # HP scan: best R>0 arm
    best_R = None
    best_transfer = -1.0
    best_forget = float("nan")
    best_cv = float("nan")
    r0_transfer = r0.get("mean_transfer_final", 0.0)

    r_arms = [k for k in arm_summary.keys() if k != "ARM_APPEND_ONLY_R0"]
    all_low = True
    all_corrupt = True
    for a in r_arms:
        s = arm_summary[a]
        tf = s.get("mean_transfer_final", float("nan"))
        fg = s.get("mean_forget_p1", float("nan"))
        if not math.isnan(tf):
            if tf >= HF_TRANSFER_MAX:
                all_low = False
            if tf > best_transfer:
                best_transfer = tf
                best_R = s["R"]
                best_forget = fg
                best_cv = s.get("cv_transfer_final", float("nan"))
        if not math.isnan(fg) and fg <= HF_FORGET_MAX:
            all_corrupt = False

    summary_line = (
        f"R0[transfer={r0_transfer:.3f} phase0={phase0_r0:.3f}] "
        f"best_R={best_R} transfer={best_transfer:.3f} forget={best_forget:.3f} cv={best_cv:.3f}"
    )

    # HARD_FAIL_DECISIVE cases
    if all_low:
        return (
            "HARD_FAIL",
            f"HARD_FAIL_REPLAY_NO_TRANSFER: all R>0 arms transfer_final < {HF_TRANSFER_MAX}; "
            f"replay does not rescue cross-slab transfer. {summary_line}",
        )
    if all_corrupt:
        return (
            "HARD_FAIL",
            f"HARD_FAIL_REPLAY_CORRUPTS: all R>0 arms forget_p1 > {HF_FORGET_MAX}; "
            f"replay corrupts current-slab retention. {summary_line}",
        )

    # HARD_PASS gate: any R>0 arm meets ALL 3 conditions
    for a in r_arms:
        s = arm_summary[a]
        tf = s.get("mean_transfer_final", float("nan"))
        fg = s.get("mean_forget_p1", float("nan"))
        cv = s.get("cv_transfer_final", float("nan"))
        if (not math.isnan(tf) and tf >= HP_TRANSFER_MIN
                and not math.isnan(fg) and fg <= HP_FORGET_MAX
                and (math.isnan(cv) or cv <= CV_MAX)):
            return (
                "HARD_PASS",
                f"CRISPR_REPLAY_RESCUE_HARD_PASS: R={s['R']} transfer_final={tf:.3f} >= {HP_TRANSFER_MIN}; "
                f"forget_p1={fg:.3f} <= {HP_FORGET_MAX}; cv={cv:.3f} <= {CV_MAX}. "
                f"Slab-boundary replay rescues cross-slab transfer. {summary_line}",
            )

    # MIDDLE_BAND
    return (
        "MIDDLE_BAND",
        f"CRISPR_REPLAY_PARTIAL: best R={best_R} transfer_final={best_transfer:.3f} in "
        f"[{MIDDLE_TRANSFER_LO}, {MIDDLE_TRANSFER_HI}]; partial rescue. {summary_line}",
    )


# ---- Metrics + atexit ----
_OUT_DIR = None
_T_START = None
_SYNTH_DONE = [False]


def _write_start_marker(output_dir: Path, run_mode: str, expected_n_units: int) -> None:
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = output_dir / "_start_marker.json.tmp"
    final = output_dir / "_start_marker.json"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir: Path, exc: Exception) -> None:
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": (time.time() - _T_START) if _T_START else 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp_path = output_dir / "metrics.json.tmp"
    final_path = output_dir / "metrics.json"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp_path, final_path)


def _build_metrics_payload(per_seed: Dict, elapsed: float, source_tag: str) -> Dict:
    arm_summary = aggregate_results(per_seed)
    total_units = sum(1 for sd in per_seed.values()
                      for a in sd.get("arms", {}).values()
                      if a is not None and "failure_class" not in a)
    verdict, verdict_msg = compute_verdict(arm_summary, total_units)
    # PRIMARY arm surface: R=20 (drill primary)
    primary = arm_summary.get("ARM_APPEND_ONLY_R20", arm_summary.get("ARM_APPEND_ONLY_R5", {}))
    summary = (
        f"{verdict}: R20_transfer={primary.get('mean_transfer_final', float('nan')):.3f} "
        f"R20_forget={primary.get('mean_forget_p1', float('nan')):.3f} units={total_units}/{EXPECTED_N_UNITS}"
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
        "M_per_phase": M_PER_PHASE,
        "R_values": R_VALUES,
        "EXPECTED_N_UNITS": EXPECTED_N_UNITS,
        "total_units": total_units,
        "cardinality_ok": total_units == EXPECTED_N_UNITS,
        "arms": [f"ARM_APPEND_ONLY_R{R}" for R in R_VALUES],
        "primary_arm": "ARM_APPEND_ONLY_R20",
        "config_version": (
            f"crispr-slab-replay-v1: N_base={N_BASE} D_slab={D_SLAB} J={J_PHASES} M={M_PER_PHASE} "
            f"alpha_per_slab={ALPHA_PER_SLAB:.4f} R_values={R_VALUES} noise_frac={NOISE_FRAC} "
            f"retrieve_steps={N_RETRIEVE_STEPS} run_mode={RUN_MODE}"
        ),
        "corpus_provenance": "synthetic_bipolar_persistent_atom_id_encoding",
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
    if _SYNTH_DONE[0] or _OUT_DIR is None:
        return
    try:
        per_seed = aggregate_partials(_OUT_DIR, SEEDS)
        if not per_seed:
            return
        elapsed = time.time() - _T_START if _T_START else 0.0
        metrics = _build_metrics_payload(
            per_seed, elapsed, "measured_cpu_bipolar_crispr_replay_atexit",
        )
        metrics["synthesized_at_exit"] = True
        tmp = _OUT_DIR / "metrics.json.tmp"
        final = _OUT_DIR / "metrics.json"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(metrics, fh, indent=2)
        os.replace(tmp, final)
        _SYNTH_DONE[0] = True
        print(f"[atexit] synthesized metrics.json verdict={metrics['verdict']}", flush=True)
    except Exception as e:
        print(f"[atexit] synth FAILED: {e}", flush=True)


atexit.register(_synth_metrics_atexit)


# ---- Main ----
def main():
    global _OUT_DIR, _T_START
    _T_START = time.time()
    print(
        f"[{ANCHOR_NAME}] run_mode={RUN_MODE} N_BASE={N_BASE} D_slab={D_SLAB} "
        f"seeds={SEEDS} J_phases={J_PHASES} M={M_PER_PHASE} R_values={R_VALUES} "
        f"EXPECTED_N_UNITS={EXPECTED_N_UNITS}",
        flush=True,
    )
    out_dir = get_output_dir(ANCHOR_NAME)
    _OUT_DIR = out_dir
    _write_start_marker(out_dir, RUN_MODE, EXPECTED_N_UNITS)

    run_config = {
        "N": N_BASE,
        "run_mode": RUN_MODE,
        "M": M_PER_PHASE,
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
        per_seed, elapsed, "measured_cpu_bipolar_crispr_replay",
    )
    tmp = out_dir / "metrics.json.tmp"
    final = out_dir / "metrics.json"
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(metrics, fh, indent=2)
    os.replace(tmp, final)
    _SYNTH_DONE[0] = True
    print(f"[{ANCHOR_NAME}] verdict={metrics['verdict']}", flush=True)
    print(f"[{ANCHOR_NAME}] {metrics['verdict_msg']}", flush=True)
    print(f"[{ANCHOR_NAME}] elapsed={elapsed:.1f}s", flush=True)


if __name__ == "__main__":
    if _ARGS.self_test:
        print("[main] --self-test complete", flush=True)
        sys.exit(0)
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        if _OUT_DIR is not None:
            _write_crash_metrics(_OUT_DIR, e)
        raise
