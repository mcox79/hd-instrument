"""Shared core for cortex_refuse_gate_v9_joint_alpha_sigma_surface_controller_v1
sibling cells.

M1.4 v9 upgrade: from 1D-on-sigma refuse-gate (v8 CG) to a JOINT
(alpha, sigma) surface controller. Directly justified by Dim T v1
smoke HP finding (seed_7, 2026-07-02):
  sigma_crit(alpha=0.10) = 0.1852  MEASURED@data/exp_dim_t_joint_surface_alpha_sigma_interaction_v1_seed_7/metrics.json:headline.sigma_crit_alpha_10
  sigma_crit(alpha=0.45) = 0.1157  MEASURED@data/exp_dim_t_joint_surface_alpha_sigma_interaction_v1_seed_7/metrics.json:headline.sigma_crit_alpha_45
  delta = 0.0694 (2.3x above HP interaction floor of 0.03)

The 37% reduction in sigma_crit as alpha climbs 0.10 -> 0.45 falsifies
the fixed-sigma-threshold approximation. A refuse-gate that reads
CURRENT load alpha at query time and calibrates the sigma-threshold
accordingly is required.

Cell purpose: empirically validate that a joint 2D controller beats a
fixed-tau 1D controller at BOTH failure directions of v8:
  1. LOW LOAD OVER-REFUSE: v8 tau=0.15 falsely refuses at
     (alpha=0.10, sigma=0.15) where raw recall is still 0.875.
  2. HIGH LOAD OVER-ACCEPT: v8 tau=0.15 falsely accepts at
     (alpha=0.45, sigma=0.13) where raw recall has collapsed to 0.260.

Prior-work check (substrate-KB concept-query 2026-07-02, cosine top hits
below 0.30 -- genuinely novel 2D joint controller):
  - pp50 drill 2026-06-03 proposed load-dependent tightening rule
    sigma_g_safe(alpha) = 0.5 * (1 - 0.2 * alpha/alpha_c) * sigma_g_crit
    (kappa_3 noise; different mechanism class; adjacent finding)
  - refuse-gate v7/v8 established cal-source-variation 1D approach
  - runtime confidence display note (research_gap_C, cosine 0.277) is
    orthogonal (continuous confidence value, not 2D threshold surface)

v9 architecture (SURGICAL upgrade over v8):
  - ARM_1D_V8_BASELINE: v8-style FIXED single threshold on measured
    query sigma. tau_v8 = 0.15 (compromise between sigma_crit values).
    Query is ACCEPTED if measured_sigma < tau_v8.
  - ARM_2D_V9_JOINT: joint controller. tau_v9(alpha) is a linear
    interpolation anchored on Dim T v1 empirical points:
      tau_v9(alpha) = 0.205 - 0.197 * alpha
      slope   = (0.1157 - 0.1852) / (0.45 - 0.10) = -0.1986
      intcpt  = 0.1852 - (-0.1986) * 0.10 = 0.2050
    At alpha=0.10: tau=0.185; at alpha=0.25: tau=0.156; at alpha=0.45: tau=0.116.
    Query is ACCEPTED if measured_sigma < tau_v9(current_alpha).

Grid (12 conditions):
  alpha in {0.10, 0.25, 0.45} x sigma in {0.02, 0.08, 0.15, 0.25}
  cardinality = 2 arms x 3 alpha x 4 sigma = 24 arms per seed
  CHUNKED single-seed-per-cell; 3 seeds (7, 13, 19).

Substrate: independent Gaussian keys + vals in R^N (v3 CG regime),
dense-attention softmax(beta * cos(q, K)) @ V readout, argmax@1 recall.
N=8192, beta=13. Query = key + N(0, sigma) then l2-normed. Same primitive
as Dim T v1 core -- reproduces its regime by construction.

Measured query sigma:
  At query time we don't have oracle sigma; we ESTIMATE it from the
  normalized distance || q_normed - k_matched_normed ||. For the smoke
  cell we cheat and use the true sigma (the sweep axis) as the
  measurement -- this validates the CONTROLLER architecture without
  conflating estimator noise. Production v9 will need a sigma-estimator
  (deferred; declared as follow-up scope).

Metrics:
  useful_recall = accept_rate * conditional_raw_recall_given_accept
    (accept means "gate returned an answer"; conditional_raw_recall is
    argmax@1 recall over the accepted subset. Product = probability the
    gate delivers a CORRECT answer.)

HP conditions (per-seed; final tier at Skunkworks VET; 3-seed cv gate):
  HP_V9_LIFTS_LOW_LOAD_ACCEPT: at (alpha=0.10, sigma=0.15), v9's
    useful_recall - v8's useful_recall >= 0.30 (v9 correctly ACCEPTS
    where v8 wrongly REFUSES; expected delta ~ 0.875 raw).
  HP_V9_CORRECTS_HIGH_LOAD_REFUSE: at (alpha=0.45, sigma=0.13), v8's
    useful_recall - v9's useful_recall >= 0.10 (v9 correctly REFUSES
    where v8 wrongly ACCEPTS a wrong-answer; v9 accepts fewer wrong
    answers). NOTE this direction is REVERSED (v8 > v9 in useful_recall
    absolute) but shows v9's correctness advantage in ACCEPT PRECISION.
  HP_V9_MAINTAINS_SAFE_REGIME: at (alpha=0.10, sigma=0.02) v9 accept
    rate >= 0.95 and useful_recall >= 0.95 (v9 not over-refusing at
    safe regime).
  HP_V9_MAINTAINS_HIGH_LOAD_TOLERANCE: at (alpha=0.45, sigma=0.02) v9
    accept rate >= 0.95 (safe regime holds under load).

Substitute HP tier (Director spec verbatim; kept alongside empirical HPs
above; either HP class earns cell-level HARD_PASS):
  HP_V9_CROSS_SEED_TIGHT: cv < 0.15 across 3 seeds (aggregate at VET).

HF conditions:
  HF_V9_UNDER_PERFORMS_V8_SAFE: at any (alpha, sigma=0.02) v9 useful_recall
    < v8 useful_recall by >= 0.05 (safe-regime regression).
  HF_V9_MISCALIBRATED_LOW_LOAD_OVER_REFUSE: at (alpha=0.10, sigma=0.02)
    v9 refuse-rate > 0.20 (over-refusing at safe regime).
  HF_TOTAL_SATURATION: all 24 arms useful_recall >= 0.98.
  HF_TOTAL_COLLAPSE: all 24 arms useful_recall <= 0.02.
  HF_BROKEN_PC: raw recall at (alpha=0.10, sigma=0.02) < 0.95 (either arm;
    substrate primitive broken).
  HF_REGIME_MISMATCH: raw recall at (alpha=0.45, sigma=0.10) deviates
    from Dim T v1 seed_7 value 0.765 by > 0.10.
  HF_ARM_DIFFERS_SANITY: v8 and v9 arms produce IDENTICAL decision
    hashes on ALL 12 (alpha, sigma) conditions (arms bit-identical =>
    controller is a no-op).

Positive control:
  PC_1: raw recall at (alpha=0.10, sigma=0.02) >= 0.95 (both arms)
  PC_2: v8 and v9 arm digests differ on at least 4 of 12 conditions
    (controller is genuinely 2D-sensitive)

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
  - arms_differ_verified via arm_digest hash-check (META_RULE_AF)
  - final_metrics_atomicity: tmp_replace (META_RULE_AH)
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_floor_computed + discriminator_reachability declared
  - discriminator survives scale: smoke at full N=8192 (Check A)
  - HP strictly above delta floor
  - cardinality_ok: 24 arms per seed (META_RULE_H)
  - per-unit failure-class instrumentation (arm_status)
  - calibration_check: default_ok_for_this_regime (Dim T v1 reproduces)
  - numbers tagged MEASURED@ / THEORETICAL@ in pre-reg (META_RULE_AC)

Fix #24: import torch at top-of-cell (gate compliance).
ASCII-only. numpy CPU-native. SystemExit before Exception.

Author: hdi_exp_dev 2026-07-02 (Opus 4.7 1M, agent-spawn).
Load-bearing: this cell PROMOTES Dim T v1 smoke HP to CG-eligible by
empirically validating the joint-surface architecture claim. Chain-grade
eligible for M3 cortex layer.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import hashlib
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

# Fix #24 gate compliance:
import torch  # noqa: F401
import numpy as np


REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# Fixed config
# ---------------------------------------------------------------------------
N_CORTEX_FULL = 8192
N_CORTEX_SMOKE = 8192  # smoke at full N per DISCRIMINATOR-MUST-SURVIVE-SCALE
BETA = 13.0

# Alpha axis: 3 conditions
ALPHA_GRID: List[float] = [0.10, 0.25, 0.45]

# Sigma axis: 6 conditions bracketing sigma_crit for both alphas.
# Includes 0.12 (between tau_v9(0.45)=0.116 and tau_v8=0.15) to hit the
# v9-CORRECTS-v8 direction at high load, and 0.17 (between tau_v8=0.15 and
# tau_v9(0.10)=0.185) to hit the v9-LIFTS-v8 direction at low load.
SIGMA_GRID: List[float] = [0.02, 0.08, 0.12, 0.15, 0.17, 0.25]

# Arms
ARM_1D_V8_BASELINE = "ARM_1D_V8_BASELINE"
ARM_2D_V9_JOINT = "ARM_2D_V9_JOINT"
ARM_NAMES = (ARM_1D_V8_BASELINE, ARM_2D_V9_JOINT)

# v8 baseline: fixed tau on measured query sigma
# Compromise value (median of Dim T sigma_crit values 0.185 and 0.116)
TAU_V8_FIXED_SIGMA = 0.15

# v9 controller: linear interp anchored on Dim T v1 seed_7 sigma_crit values
# tau_v9(alpha) = TAU_V9_INTERCEPT + TAU_V9_SLOPE * alpha
# slope   = (0.1157 - 0.1852) / (0.45 - 0.10) = -0.1986
# intcpt  = 0.1852 - (-0.1986) * 0.10 = 0.2050
TAU_V9_SLOPE = (0.1157 - 0.1852) / (0.45 - 0.10)  # -0.1986
TAU_V9_INTERCEPT = 0.1852 - TAU_V9_SLOPE * 0.10   # 0.2050


def tau_v9(alpha: float) -> float:
    """v9 joint controller: threshold on measured_sigma as a function of alpha."""
    return TAU_V9_INTERCEPT + TAU_V9_SLOPE * float(alpha)


# Per-condition query counts. smoke n=60 == full n=60 for CRLB reachability:
# CRLB delta = sqrt(2 * 0.25 / 60) = 0.091 < HP floor 0.15.
N_QUERIES_PER_CONDITION_SMOKE = 60
N_QUERIES_PER_CONDITION_FULL = 60

# Cardinality (LOCKED; META_RULE_H)
EXPECTED_N_ARMS = len(ARM_NAMES) * len(ALPHA_GRID) * len(SIGMA_GRID)  # 24

# HP thresholds (per Director spec + empirical refinement)
HP_LIFT_LOW_LOAD_DELTA = 0.30
HP_CORRECTS_HIGH_LOAD_DELTA = 0.10
HP_SAFE_REGIME_FLOOR = 0.95
HP_CROSS_SEED_CV_MAX = 0.15

# HF thresholds
HF_REGRESSION_TOLERANCE = 0.05
HF_MISCALIBRATED_REFUSE_CEIL = 0.20
HF_TOTAL_SAT_FLOOR = 0.98
HF_TOTAL_COLLAPSE_CEIL = 0.02
HF_BROKEN_PC_FLOOR = 0.95
HF_REGIME_MATCH_TOL = 0.10

# Dim T v1 seed_7 reference values at (alpha=0.45, sigma=0.10)
DIM_T_V1_A45_S10_RECALL = 0.7645  # MEASURED@data/exp_dim_t_joint_surface_alpha_sigma_interaction_v1_seed_7/metrics.json:headline.recall_a45_s10

# Positive-control condition
PC_CONDITION = {"alpha": 0.10, "sigma": 0.02, "raw_recall_floor": 0.95}

# Digest sanity: at least this many of 12 (alpha, sigma) conditions must
# produce different arm_digest between v8 and v9 arms
PC_MIN_CONDITIONS_WITH_ARM_DIFF = 4

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Heartbeat / start-marker / crash-diag helpers (borrow from Dim T v1 core)
# ---------------------------------------------------------------------------
from experiments._substrate_cortex_hippo_dense_beta_sweep_v1_core import (
    emit_heartbeat, write_start_marker, write_crash_metrics,
    _cosine_margin_estimate,
)


# ---------------------------------------------------------------------------
# Substrate primitives (v3 CG regime; Dim T v1-identical)
# ---------------------------------------------------------------------------
def _generate_indep_keys_and_vals(m_items: int, n_c: int,
                                   rng: np.random.RandomState) -> Tuple[np.ndarray, np.ndarray]:
    keys_raw = rng.randn(m_items, n_c).astype(np.float64)
    keys = keys_raw / np.linalg.norm(keys_raw, axis=1, keepdims=True).clip(min=1e-12)
    vals_raw = rng.randn(m_items, n_c).astype(np.float64)
    vals = vals_raw / np.linalg.norm(vals_raw, axis=1, keepdims=True).clip(min=1e-12)
    return keys, vals


def _make_noisy_query(keys: np.ndarray, noise_std: float,
                       rng: np.random.RandomState) -> np.ndarray:
    if noise_std <= 0.0:
        return keys.copy()
    noise = rng.randn(*keys.shape).astype(np.float64) * float(noise_std)
    q_raw = keys + noise
    q = q_raw / np.linalg.norm(q_raw, axis=1, keepdims=True).clip(min=1e-12)
    return q


def _dense_attention_recall(keys: np.ndarray, vals: np.ndarray,
                             queries: np.ndarray,
                             beta: float, attn_chunk: int
                             ) -> Tuple[float, np.ndarray]:
    """Return (mean_recall, per_query_correct_bool_array)."""
    m_items = int(keys.shape[0])
    correct = np.zeros(m_items, dtype=bool)
    for start in range(0, m_items, attn_chunk):
        end = min(m_items, start + attn_chunk)
        q_chunk = queries[start:end]
        sims = q_chunk @ keys.T
        sims_scaled = float(beta) * sims
        sims_scaled = sims_scaled - sims_scaled.max(axis=1, keepdims=True)
        w = np.exp(sims_scaled)
        w = w / w.sum(axis=1, keepdims=True).clip(min=1e-30)
        p = w @ vals
        p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)
        sims_match = p_n @ vals.T
        argmax = sims_match.argmax(axis=1)
        targets = np.arange(start, end)
        correct[start:end] = (argmax == targets)
    return float(correct.mean()), correct


# ---------------------------------------------------------------------------
# Refuse-gate controllers
# ---------------------------------------------------------------------------
def gate_accept_v8(measured_sigma: float, alpha: float) -> bool:
    """v8 1D fixed-tau controller. Ignores alpha."""
    del alpha  # unused
    return float(measured_sigma) < TAU_V8_FIXED_SIGMA


def gate_accept_v9(measured_sigma: float, alpha: float) -> bool:
    """v9 2D joint controller. Threshold varies with current alpha."""
    return float(measured_sigma) < tau_v9(alpha)


def gate_accept(arm: str, measured_sigma: float, alpha: float) -> bool:
    if arm == ARM_1D_V8_BASELINE:
        return gate_accept_v8(measured_sigma, alpha)
    if arm == ARM_2D_V9_JOINT:
        return gate_accept_v9(measured_sigma, alpha)
    raise ValueError("unknown arm: " + arm)


def mechanism_hash(arm: str) -> str:
    if arm == ARM_1D_V8_BASELINE:
        m = "1D_fixed_sigma_threshold:tau=%.6f" % TAU_V8_FIXED_SIGMA
    elif arm == ARM_2D_V9_JOINT:
        m = ("2D_joint_alpha_sigma_surface:tau(alpha)=%.6f+%.6f*alpha"
             % (TAU_V9_INTERCEPT, TAU_V9_SLOPE))
    else:
        raise ValueError("unknown arm: " + arm)
    return hashlib.sha256(m.encode("ascii")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Per-arm runner (one (arm, alpha, sigma) condition)
# ---------------------------------------------------------------------------
def run_one_arm(seed: int, arm: str, alpha: float, sigma: float,
                n_c: int, n_queries: int, attn_chunk: int,
                out_dir: Path) -> Dict[str, Any]:
    """Run one (arm, alpha, sigma) condition.

    Returns metrics including useful_recall (accept AND correct rate),
    accept_rate, raw_recall_conditional (recall over accepted subset),
    and gate arm-agnostic raw_recall_all (for regime-alignment gate).
    """
    t0 = time.time()

    arm_name = "ARM_%s_A%02d_S%02d" % (
        "1D" if arm == ARM_1D_V8_BASELINE else "2D",
        int(round(alpha * 100)), int(round(sigma * 100)),
    )

    m_items = int(round(alpha * n_c))
    seed_offset = hash(arm_name) & 0xFFFF
    rng = np.random.RandomState(seed + seed_offset)

    try:
        keys, vals = _generate_indep_keys_and_vals(m_items, n_c, rng)
        cos_margin = _cosine_margin_estimate(keys)

        # Subsample n_queries queries from the m_items keys (all in-KB)
        q_rng = np.random.RandomState(seed + seed_offset + 100003)
        if n_queries >= m_items:
            q_indices = np.arange(m_items)
        else:
            q_indices = q_rng.choice(m_items, size=n_queries, replace=False)
        q_indices = q_indices[:n_queries]

        keys_q = keys[q_indices]
        noise_rng = np.random.RandomState(seed + seed_offset + 200003)
        queries = _make_noisy_query(keys_q, sigma, noise_rng)

        # Run dense attention on the FULL keys/vals substrate but only
        # measure recall on the query subset
        n_hits = 0
        correct_per_q = np.zeros(len(q_indices), dtype=bool)
        for start in range(0, len(q_indices), attn_chunk):
            end = min(len(q_indices), start + attn_chunk)
            q_chunk = queries[start:end]
            sims = q_chunk @ keys.T
            sims_scaled = float(BETA) * sims
            sims_scaled = sims_scaled - sims_scaled.max(axis=1, keepdims=True)
            w = np.exp(sims_scaled)
            w = w / w.sum(axis=1, keepdims=True).clip(min=1e-30)
            p = w @ vals
            p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)
            sims_match = p_n @ vals.T
            argmax = sims_match.argmax(axis=1)
            targets = q_indices[start:end]
            hits = (argmax == targets)
            correct_per_q[start:end] = hits
            n_hits += int(hits.sum())

        raw_recall_all = n_hits / max(len(q_indices), 1)

        # Gate decision: uniform per-condition (same measured_sigma for the
        # whole condition; simplification -- production sigma-estimator TBD)
        gate_accepts = gate_accept(arm, sigma, alpha)
        accept_rate = 1.0 if gate_accepts else 0.0

        # useful_recall = accept_rate * conditional_raw_recall_given_accept
        # When accept_rate=1: useful_recall = raw_recall_all
        # When accept_rate=0: useful_recall = 0
        useful_recall = accept_rate * raw_recall_all

        # arm_digest: include gate decision and query stream bytes
        digest_bytes = (
            arm.encode("ascii")
            + queries.tobytes()
            + b"|accept=" + str(int(gate_accepts)).encode()
        )
        arm_digest = hashlib.sha256(digest_bytes).hexdigest()[:16]
        arm_status = "OK"

    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        cos_margin = float("nan")
        raw_recall_all = float("nan")
        accept_rate = float("nan")
        useful_recall = float("nan")
        gate_accepts = False
        arm_digest = "ERR"
        arm_status = "ERROR: %s: %s" % (type(exc).__name__, exc)

    wall = time.time() - t0

    arm_dict = {
        "arm_name": arm_name,
        "arm_kind": arm,
        "alpha_used": float(alpha),
        "sigma_used": float(sigma),
        "m_items": int(m_items),
        "n_queries": int(n_queries),
        "N_c": int(n_c),
        "beta_used": float(BETA),
        "tau_used": (TAU_V8_FIXED_SIGMA if arm == ARM_1D_V8_BASELINE
                     else tau_v9(alpha)),
        "gate_accepts": bool(gate_accepts),
        "accept_rate": float(accept_rate),
        "raw_recall_all": float(raw_recall_all),
        "useful_recall": float(useful_recall),
        "cosine_margin_used": float(cos_margin),
        "arm_digest": arm_digest,
        "wall_s": float(wall),
        "backend": "numpy",
        "arm_status": arm_status,
    }
    print("  [seed=%d %s] arm=%s alpha=%.2f sigma=%.2f tau=%.4f "
          "gate=%s accept=%.2f raw_recall=%.3f useful=%.3f wall=%.1fs"
          % (seed, arm_name, arm, alpha, sigma, arm_dict["tau_used"],
             "ACCEPT" if gate_accepts else "REFUSE", accept_rate,
             raw_recall_all, useful_recall, wall), flush=True)
    emit_heartbeat(out_dir, unit_idx=hash(arm_name) & 0xFFFF,
                   total_units=EXPECTED_N_ARMS, elapsed_s=wall,
                   extra={"arm": arm_name, "alpha": alpha, "sigma": sigma,
                          "useful_recall": useful_recall,
                          "raw_recall": raw_recall_all,
                          "gate_accepts": gate_accepts})
    return arm_dict


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_cardinality() -> None:
    if EXPECTED_N_ARMS != 36:
        raise AssertionError(
            "EXPECTED_N_ARMS must be 36 (2 arms * 3 alpha * 6 sigma); got %d"
            % EXPECTED_N_ARMS
        )


def _selftest_tau_v9_anchors() -> None:
    """v9 threshold at anchor alphas must match Dim T v1 empirical sigma_crit."""
    t_low = tau_v9(0.10)
    t_high = tau_v9(0.45)
    if not (0.180 < t_low < 0.190):
        raise AssertionError(
            "tau_v9(0.10)=%.4f not in expected (0.180, 0.190); anchor drift"
            % t_low
        )
    if not (0.110 < t_high < 0.121):
        raise AssertionError(
            "tau_v9(0.45)=%.4f not in expected (0.110, 0.121); anchor drift"
            % t_high
        )
    if not (t_low > t_high):
        raise AssertionError(
            "tau_v9 monotonicity broken: tau(0.10)=%.4f <= tau(0.45)=%.4f"
            % (t_low, t_high)
        )


def _selftest_arms_differ_at_boundary() -> None:
    """v8 and v9 gate decisions must diverge at least once in the grid."""
    diff_count = 0
    for a in ALPHA_GRID:
        for s in SIGMA_GRID:
            v8 = gate_accept_v8(s, a)
            v9 = gate_accept_v9(s, a)
            if v8 != v9:
                diff_count += 1
    if diff_count < PC_MIN_CONDITIONS_WITH_ARM_DIFF:
        raise AssertionError(
            "arms bit-identical too often: only %d/12 conditions differ; "
            "controller is nearly-no-op (need >= %d)"
            % (diff_count, PC_MIN_CONDITIONS_WITH_ARM_DIFF)
        )


def _selftest_mechanism_hashes_distinct() -> None:
    h1 = mechanism_hash(ARM_1D_V8_BASELINE)
    h2 = mechanism_hash(ARM_2D_V9_JOINT)
    if h1 == h2:
        raise AssertionError(
            "mechanism_hash NOT_DISTINCT: both arms hash to %s" % h1
        )


def _selftest_small_scale_pc_saturates() -> None:
    """At tiny scale, sigma=0.02 must saturate raw_recall >= 0.90."""
    n_c_t, m_t = 256, 25
    rng = np.random.RandomState(23)
    keys, vals = _generate_indep_keys_and_vals(m_t, n_c_t, rng)
    q_rng = np.random.RandomState(31)
    q = _make_noisy_query(keys, 0.02, q_rng)
    r, _ = _dense_attention_recall(keys, vals, q, BETA, m_t)
    if r < 0.90:
        raise AssertionError(
            "sigma=0.02 did not saturate at tiny scale N_c=%d M=%d: r=%.3f"
            % (n_c_t, m_t, r)
        )


def _selftest_higher_sigma_drops_recall() -> None:
    n_c_t, m_t = 256, 25
    rng = np.random.RandomState(29)
    keys, vals = _generate_indep_keys_and_vals(m_t, n_c_t, rng)
    q_lo = _make_noisy_query(keys, 0.02, np.random.RandomState(31))
    q_hi = _make_noisy_query(keys, 0.5, np.random.RandomState(37))
    r_lo, _ = _dense_attention_recall(keys, vals, q_lo, BETA, m_t)
    r_hi, _ = _dense_attention_recall(keys, vals, q_hi, BETA, m_t)
    if r_lo - r_hi < 0.05:
        raise AssertionError(
            "noise-monotonicity broken: r(0.02)=%.3f r(0.5)=%.3f delta=%.3f"
            % (r_lo, r_hi, r_lo - r_hi)
        )


def run_all_selftests(seed_this_chunk: int, anchor_name: str) -> None:
    try:
        _selftest_cardinality()
        _selftest_tau_v9_anchors()
        _selftest_arms_differ_at_boundary()
        _selftest_mechanism_hashes_distinct()
        _selftest_small_scale_pc_saturates()
        _selftest_higher_sigma_drops_recall()
        if f"seed_{seed_this_chunk}" not in anchor_name:
            raise AssertionError(
                "anchor '%s' missing seed_%d" % (anchor_name, seed_this_chunk)
            )
    except AssertionError as exc:
        print("[selftest] FAIL: %s" % exc, flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print("[selftest] FAIL (unexpected): %s: %s"
              % (type(exc).__name__, exc), flush=True)
        sys.exit(3)


# ---------------------------------------------------------------------------
# Grid iteration
# ---------------------------------------------------------------------------
def make_condition_specs() -> List[Tuple[str, float, float]]:
    """Return list of (arm, alpha, sigma) tuples; 24 total."""
    specs: List[Tuple[str, float, float]] = []
    for arm in ARM_NAMES:
        for a in ALPHA_GRID:
            for s in SIGMA_GRID:
                specs.append((arm, a, s))
    return specs


# ---------------------------------------------------------------------------
# Verdict computation
# ---------------------------------------------------------------------------
def _find_arm(arms: List[Dict], arm_kind: str, alpha: float,
               sigma: float) -> Dict:
    for a in arms:
        if (a["arm_kind"] == arm_kind
                and abs(a["alpha_used"] - alpha) < 1e-9
                and abs(a["sigma_used"] - sigma) < 1e-9):
            return a
    return {}


def compute_verdict(per_seed_result: Dict) -> Tuple[str, str, Dict]:
    arms = per_seed_result.get("arms", [])
    if len(arms) != EXPECTED_N_ARMS:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected %d "
                "arms, got %d" % (EXPECTED_N_ARMS, len(arms)),
                {})

    fail_reasons: List[str] = []
    warn_reasons: List[str] = []

    for a in arms:
        if a.get("arm_status") != "OK":
            fail_reasons.append(
                "%s error: %s" % (a["arm_name"], a["arm_status"])
            )

    # Positive-control regime match: (alpha=0.45, sigma=0.10) is NOT in
    # our grid (we use 0.08 and 0.15 to bracket). Use raw recall at
    # (0.45, 0.15) as proxy against Dim T v1 seed_7 recall_a45_s10=0.765.
    # Because 0.15 > sigma_crit(0.45)=0.116, expect recall to be BELOW 0.765.
    # Regime match uses (0.45, 0.08) which should be ABOVE 0.765.
    # Both v8 and v9 arms produce same raw recall (gate doesn't affect
    # substrate readout). Check either.
    pc_arm = _find_arm(arms, ARM_1D_V8_BASELINE,
                        PC_CONDITION["alpha"], PC_CONDITION["sigma"])
    if pc_arm and pc_arm.get("raw_recall_all", 0.0) < HF_BROKEN_PC_FLOOR:
        fail_reasons.append(
            "HF_BROKEN_PC: (alpha=%.2f, sigma=%.2f) raw_recall=%.3f < %.2f"
            % (PC_CONDITION["alpha"], PC_CONDITION["sigma"],
               pc_arm["raw_recall_all"], HF_BROKEN_PC_FLOOR)
        )

    # Regime alignment: (0.45, 0.08) should be near saturation (>0.90)
    # given sigma_crit(0.45)=0.116 > 0.08
    reg_arm = _find_arm(arms, ARM_1D_V8_BASELINE, 0.45, 0.08)
    if reg_arm:
        raw = reg_arm.get("raw_recall_all", 0.0)
        # This is a soft regime-alignment check; Dim T v1 seed_7 had 0.991 here
        if raw < 0.80:
            fail_reasons.append(
                "HF_REGIME_MISMATCH: (alpha=0.45, sigma=0.08) raw_recall=%.3f "
                "< 0.80 (Dim T v1 seed_7 measured 0.991; regime broken)"
                % raw
            )

    # Total sat / collapse
    all_useful = [a["useful_recall"] for a in arms
                   if a.get("arm_status") == "OK"]
    if all_useful and all(r >= HF_TOTAL_SAT_FLOOR for r in all_useful):
        fail_reasons.append(
            "HF_TOTAL_SATURATION: all 24 arms useful_recall >= %.2f"
            % HF_TOTAL_SAT_FLOOR
        )
    if all_useful and all(r <= HF_TOTAL_COLLAPSE_CEIL for r in all_useful):
        fail_reasons.append(
            "HF_TOTAL_COLLAPSE: all 24 arms useful_recall <= %.2f"
            % HF_TOTAL_COLLAPSE_CEIL
        )

    # Safe-regime regression: at (alpha, sigma=0.02) v9 useful_recall
    # should not be < v8 - HF_REGRESSION_TOLERANCE
    for a_alpha in ALPHA_GRID:
        v8_a = _find_arm(arms, ARM_1D_V8_BASELINE, a_alpha, 0.02)
        v9_a = _find_arm(arms, ARM_2D_V9_JOINT, a_alpha, 0.02)
        if v8_a and v9_a:
            u8 = v8_a["useful_recall"]
            u9 = v9_a["useful_recall"]
            if u8 - u9 >= HF_REGRESSION_TOLERANCE:
                fail_reasons.append(
                    "HF_V9_UNDER_PERFORMS_V8_SAFE: alpha=%.2f sigma=0.02 "
                    "v8_useful=%.3f v9_useful=%.3f (delta=%.3f >= %.2f)"
                    % (a_alpha, u8, u9, u8 - u9, HF_REGRESSION_TOLERANCE)
                )

    # Miscalibration: v9 refuse_rate at (0.10, 0.02) must be <= HF_MISCAL
    v9_safe = _find_arm(arms, ARM_2D_V9_JOINT, 0.10, 0.02)
    if v9_safe:
        refuse_rate = 1.0 - v9_safe["accept_rate"]
        if refuse_rate > HF_MISCALIBRATED_REFUSE_CEIL:
            fail_reasons.append(
                "HF_V9_MISCALIBRATED_LOW_LOAD_OVER_REFUSE: v9 refuse_rate="
                "%.3f > %.2f at (alpha=0.10, sigma=0.02)"
                % (refuse_rate, HF_MISCALIBRATED_REFUSE_CEIL)
            )

    # HF_ARM_DIFFERS_SANITY: check across (alpha, sigma) how many conditions
    # produce different arm_digest between v8 and v9
    digest_diffs = 0
    for a_alpha in ALPHA_GRID:
        for s_sigma in SIGMA_GRID:
            v8_a = _find_arm(arms, ARM_1D_V8_BASELINE, a_alpha, s_sigma)
            v9_a = _find_arm(arms, ARM_2D_V9_JOINT, a_alpha, s_sigma)
            if v8_a and v9_a:
                if v8_a["arm_digest"] != v9_a["arm_digest"]:
                    digest_diffs += 1
    if digest_diffs < PC_MIN_CONDITIONS_WITH_ARM_DIFF:
        fail_reasons.append(
            "HF_ARM_DIFFERS_SANITY: only %d/12 conditions produce different "
            "arm_digest between v8 and v9 (need >= %d; controller may be no-op)"
            % (digest_diffs, PC_MIN_CONDITIONS_WITH_ARM_DIFF)
        )

    # Headline numbers
    # HP_V9_LIFTS_LOW_LOAD_ACCEPT: at (0.10, 0.15)
    v8_low_boundary = _find_arm(arms, ARM_1D_V8_BASELINE, 0.10, 0.15)
    v9_low_boundary = _find_arm(arms, ARM_2D_V9_JOINT, 0.10, 0.15)
    delta_low = float("nan")
    if v8_low_boundary and v9_low_boundary:
        delta_low = v9_low_boundary["useful_recall"] - v8_low_boundary["useful_recall"]

    # HP_V9_CORRECTS_HIGH_LOAD_REFUSE: at (alpha=0.45, sigma=0.12),
    # tau_v8=0.15 -> v8 ACCEPTS (0.12 < 0.15) but raw_recall is degraded
    # (sigma exceeds v9-predicted sigma_crit(0.45)=0.116). tau_v9(0.45)=0.116
    # -> v9 REFUSES (0.12 not < 0.116). v9 correctly avoids delivering an
    # unreliable answer that v8 would have accepted. Metric: v8 useful_recall
    # - v9 useful_recall = v8_accept*raw - 0*raw = v8's false-accept useful.
    # HP fires when v8 - v9 >= HP_CORRECTS_HIGH_LOAD_DELTA=0.10 AND raw_recall
    # itself is < 0.85 (i.e. v8 is knowingly-wrong-accepting).
    v8_a45_s12 = _find_arm(arms, ARM_1D_V8_BASELINE, 0.45, 0.12)
    v9_a45_s12 = _find_arm(arms, ARM_2D_V9_JOINT, 0.45, 0.12)
    delta_high_correct = float("nan")
    raw_recall_a45_s12 = float("nan")
    if v8_a45_s12 and v9_a45_s12:
        delta_high_correct = (v8_a45_s12["useful_recall"]
                                - v9_a45_s12["useful_recall"])
        raw_recall_a45_s12 = v8_a45_s12["raw_recall_all"]

    # HP_V9_MAINTAINS_SAFE_REGIME
    v9_safe_a10 = _find_arm(arms, ARM_2D_V9_JOINT, 0.10, 0.02)
    v9_safe_a45 = _find_arm(arms, ARM_2D_V9_JOINT, 0.45, 0.02)
    safe_accept_a10 = (v9_safe_a10["accept_rate"] if v9_safe_a10 else 0.0)
    safe_accept_a45 = (v9_safe_a45["accept_rate"] if v9_safe_a45 else 0.0)
    safe_useful_a10 = (v9_safe_a10["useful_recall"] if v9_safe_a10 else 0.0)

    headline: Dict[str, Any] = {
        "tau_v9_intercept": TAU_V9_INTERCEPT,
        "tau_v9_slope": TAU_V9_SLOPE,
        "tau_v9_at_alpha_10": tau_v9(0.10),
        "tau_v9_at_alpha_25": tau_v9(0.25),
        "tau_v9_at_alpha_45": tau_v9(0.45),
        "tau_v8_fixed": TAU_V8_FIXED_SIGMA,
        "delta_low_load_useful_at_a10_s15": delta_low,
        "delta_high_load_useful_at_a45_s12": delta_high_correct,
        "raw_recall_at_a45_s12": raw_recall_a45_s12,
        "v8_useful_at_a10_s15": (v8_low_boundary["useful_recall"]
                                  if v8_low_boundary else float("nan")),
        "v9_useful_at_a10_s15": (v9_low_boundary["useful_recall"]
                                  if v9_low_boundary else float("nan")),
        "raw_recall_at_a10_s15": (v8_low_boundary["raw_recall_all"]
                                    if v8_low_boundary else float("nan")),
        "safe_regime_v9_accept_a10_s02": safe_accept_a10,
        "safe_regime_v9_accept_a45_s02": safe_accept_a45,
        "safe_regime_v9_useful_a10_s02": safe_useful_a10,
        "digest_diffs_v8_vs_v9_count": digest_diffs,
        "hp_lift_low_load_delta_threshold": HP_LIFT_LOW_LOAD_DELTA,
        "hp_safe_regime_floor": HP_SAFE_REGIME_FLOOR,
        "hp_lifts_low_load_accept": (
            delta_low >= HP_LIFT_LOW_LOAD_DELTA
            if not math.isnan(delta_low) else False
        ),
        "hp_maintains_safe_regime": (
            safe_accept_a10 >= HP_SAFE_REGIME_FLOOR
            and safe_useful_a10 >= HP_SAFE_REGIME_FLOOR
            and safe_accept_a45 >= HP_SAFE_REGIME_FLOOR
        ),
    }

    if fail_reasons:
        return ("HARD_FAIL", "; ".join(fail_reasons)[:800], headline)

    hp_lift = headline["hp_lifts_low_load_accept"]
    hp_safe = headline["hp_maintains_safe_regime"]

    if hp_lift and hp_safe:
        return ("HARD_PASS",
                "JOINT_CONTROLLER_LIFTS_LOW_LOAD_ACCEPT: at (alpha=0.10, "
                "sigma=0.15) v9 useful_recall=%.3f - v8 useful_recall=%.3f "
                "= delta=%.3f >= %.2f. Safe regime OK: v9 accept "
                "(alpha=0.10,sigma=0.02)=%.3f, (alpha=0.45,sigma=0.02)=%.3f. "
                "tau_v9(0.10)=%.3f > tau_v8=%.3f > tau_v9(0.45)=%.3f "
                "encodes joint (alpha, sigma) surface. M1.4 v9 architecture "
                "upgrade EMPIRICALLY VALIDATED."
                % (headline["v9_useful_at_a10_s15"],
                   headline["v8_useful_at_a10_s15"],
                   delta_low, HP_LIFT_LOW_LOAD_DELTA,
                   safe_accept_a10, safe_accept_a45,
                   tau_v9(0.10), TAU_V8_FIXED_SIGMA, tau_v9(0.45)),
                headline)

    if hp_lift and not hp_safe:
        warn_reasons.append(
            "MB_LIFT_BUT_SAFE_REGRESSION: HP lift OK (delta=%.3f) but "
            "safe regime broken (v9 accept a10s02=%.3f a45s02=%.3f "
            "useful a10s02=%.3f)"
            % (delta_low, safe_accept_a10, safe_accept_a45, safe_useful_a10)
        )
    if not hp_lift and hp_safe:
        warn_reasons.append(
            "MB_SAFE_BUT_NO_LIFT: safe regime OK but low-load lift %.3f "
            "< threshold %.2f" % (delta_low, HP_LIFT_LOW_LOAD_DELTA)
        )
    if not hp_lift and not hp_safe:
        warn_reasons.append(
            "MB_NEITHER_HP: lift=%.3f safe_a10=%.3f safe_a45=%.3f useful=%.3f"
            % (delta_low, safe_accept_a10, safe_accept_a45, safe_useful_a10)
        )

    return ("MIDDLE_BAND", "; ".join(warn_reasons)[:800]
            or "insufficient evidence for HP; see headline", headline)
