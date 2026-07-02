"""Shared core for dim_t_joint_surface_alpha_sigma_interaction_v1.

Purpose: cheapest decisive test for the joint (alpha, sigma) transition
surface hypothesis (Sonnet Dim T drill 2026-07-02, notes/
research_dim_t_regime_transitions_composition_2026-07-02.md Section 7
Option B).

Question: does sigma_crit (the query-noise level at which recall crosses
0.50) DECREASE at higher load alpha? If YES => transitions are non-
independent and M3 refuse-gate must upgrade to joint (alpha, sigma)
controller. If NO => refuse-gate can stay 1D on sigma.

Design (v1, per Director spawn spec):
  Fixed: N_c = 8192, beta = 13 (from v3 CG regime), numpy CPU
  Sweep axis 1 (alpha):  {0.10, 0.45}  -> M = {819, 3686}
  Sweep axis 2 (sigma):  {0.02, 0.05, 0.08, 0.10, 0.13, 0.15, 0.20, 0.30}
  Seeds:                 3 (7, 13, 19); one seed per cell file
  Cardinality per seed:  2 alpha * 8 sigma = 16 arms

Encoding: independent Gaussian keys+vals (v3 regime); queries = keys +
N(0, sigma) then l2-normed. Readout: dense-attention softmax(beta *
cos(q,K)) @ V; argmax@1 recall (v3-identical primitive).

HP (per this-cell aggregate over 3 seeds; final tier at Skunkworks VET):
  HP_INTERACTION_CONFIRMED: sigma_crit(alpha=0.10) - sigma_crit(alpha=0.45)
    >= 0.03 (joint-surface controller required).
  HP_MONOTONIC_ALPHA: at sigma=0.10, recall_mean(alpha=0.10) >
    recall_mean(alpha=0.45).

HF:
  HF_INTERACTION_ABSENT: |delta| < 0.02 AND HP_MONOTONIC_ALPHA fails.
  HF_TOTAL_SATURATION: all 16 points >= 0.98.
  HF_TOTAL_COLLAPSE:   all 16 points <= 0.02.
  HF_BROKEN_PC:        recall(alpha, sigma=0.02) < 0.95 for either alpha.
  HF_REGIME_MISMATCH:  recall(alpha=0.45, sigma=0.10) deviates from v3 CG
    value 0.785 by > 0.10 (regime doesn't reproduce).
  HF_CARDINALITY:      n_arms != 16.
  HF_META_RULE_AF:     any bit-identical arm pair (with narrow exemption).

Positive-control arms (per META_RULE §15 gate D):
  ARM_A10_S02: (alpha=0.10, sigma=0.02) MUST saturate at >= 0.95 (near-zero
    noise; broken-PC gate)
  ARM_A45_S02: (alpha=0.45, sigma=0.02) MUST saturate at >= 0.95 (broken-PC)
  ARM_A45_S10: (alpha=0.45, sigma=0.10) MUST match v3 CG 0.785 +/- 0.10
    (regime-alignment gate; predicts and reproduces prior CG at TEST regime)

ASCII-only; META_RULE_AH atomic-write; META_RULE_AF arms-must-differ;
SystemExit before Exception (no BaseException).
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import hashlib
import json
import math
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))


# ---------------------------------------------------------------------------
# Fixed config
# ---------------------------------------------------------------------------
N_CORTEX_FULL = 8192
N_CORTEX_SMOKE = 8192  # per USER discriminator-must-survive-scale: smoke at full N
BETA = 13.0

# Alpha axis (fraction of N stored): 2 conditions.
ALPHA_LOW = 0.10   # M = 819
ALPHA_HIGH = 0.45  # M = 3686

M_LOW_FULL = int(round(ALPHA_LOW * N_CORTEX_FULL))   # 819
M_HIGH_FULL = int(round(ALPHA_HIGH * N_CORTEX_FULL))  # 3686
M_LOW_SMOKE = M_LOW_FULL
M_HIGH_SMOKE = M_HIGH_FULL

# Sigma axis (query-noise std): 8 values bracketing v3 sigma cliff at
# alpha ~ 0.49 (which sits between 0.1 and 0.3).
SIGMA_SWEEP: List[float] = [0.02, 0.05, 0.08, 0.10, 0.13, 0.15, 0.20, 0.30]

# Positive-control gate thresholds.
BROKEN_PC_FLOOR = 0.95     # sigma=0.02 arms must saturate at >= 0.95
REGIME_MATCH_TOL = 0.10    # (alpha=0.45, sigma=0.10) must match v3 0.785 +/- 0.10
V3_CG_REFERENCE_RECALL = 0.785  # MEASURED@data/exp_cortex_hippo_dense_beta_sweep_v3_query_noise_seed_7/metrics.json:headline.recall_r13_noise_0p1

# HP thresholds.
HP_INTERACTION_DELTA = 0.03  # sigma_crit gap between low-alpha and high-alpha
MB_INTERACTION_DELTA = 0.01
HF_INTERACTION_TOL = 0.02
RECALL_HALF_CROSSING = 0.50  # sigma_crit is where recall crosses this

# Saturation floor / collapse ceiling for HF (all-arm bulk checks).
TOTAL_SAT_FLOOR = 0.98
TOTAL_COLLAPSE_CEIL = 0.02

# Arm specs: (arm_name, alpha, m_items, sigma).
def _make_arm_specs(n_c: int) -> List[Tuple[str, float, int, float]]:
    specs: List[Tuple[str, float, int, float]] = []
    for (alpha_name, alpha_val, m_val) in [
        ("A10", ALPHA_LOW, int(round(ALPHA_LOW * n_c))),
        ("A45", ALPHA_HIGH, int(round(ALPHA_HIGH * n_c))),
    ]:
        for sigma in SIGMA_SWEEP:
            # arm name pattern: ARM_A10_S02 for sigma=0.02, ARM_A10_S05 for 0.05, ...
            # Use 2-digit centi-sigma (sigma * 100 rounded to int) for stable naming.
            sig_int = int(round(sigma * 100))
            arm_name = f"ARM_{alpha_name}_S{sig_int:02d}"
            specs.append((arm_name, alpha_val, m_val, sigma))
    return specs


ARM_SPECS_FULL: List[Tuple[str, float, int, float]] = _make_arm_specs(N_CORTEX_FULL)
EXPECTED_N_ARMS = len(ARM_SPECS_FULL)  # 16


# ---------------------------------------------------------------------------
# Heartbeat / start-marker / crash-diag helpers (import from v1 core)
# ---------------------------------------------------------------------------
from experiments._substrate_cortex_hippo_dense_beta_sweep_v1_core import (
    emit_heartbeat, write_start_marker, write_crash_metrics,
    _cosine_margin_estimate,
)


# ---------------------------------------------------------------------------
# Key / value / query generation (v3-identical)
# ---------------------------------------------------------------------------
def _generate_indep_keys_and_vals(m_items: int, n_c: int, rng) -> Tuple[np.ndarray, np.ndarray]:
    """M independent Gaussian keys + vals in R^{n_c}, l2-normalized rows."""
    keys_raw = rng.randn(m_items, n_c).astype(np.float64)
    keys = keys_raw / np.linalg.norm(keys_raw, axis=1, keepdims=True).clip(min=1e-12)
    vals_raw = rng.randn(m_items, n_c).astype(np.float64)
    vals = vals_raw / np.linalg.norm(vals_raw, axis=1, keepdims=True).clip(min=1e-12)
    return keys, vals


def _make_noisy_query(keys: np.ndarray, noise_std: float, rng) -> np.ndarray:
    """Perturb queries = keys + N(0, noise_std) then l2-normalize."""
    if noise_std <= 0.0:
        return keys.copy()
    noise = rng.randn(*keys.shape).astype(np.float64) * float(noise_std)
    q_raw = keys + noise
    q = q_raw / np.linalg.norm(q_raw, axis=1, keepdims=True).clip(min=1e-12)
    return q


# ---------------------------------------------------------------------------
# Dense-attention READ (v3-identical)
# ---------------------------------------------------------------------------
def _replace_read_noisy_numpy(keys: np.ndarray, vals: np.ndarray,
                              queries: np.ndarray,
                              beta: float, attn_chunk: int) -> float:
    K_tape = keys
    V_tape = vals
    m_items = int(K_tape.shape[0])
    n_hits = 0
    for start in range(0, m_items, attn_chunk):
        end = min(m_items, start + attn_chunk)
        q_chunk = queries[start:end]
        sims = q_chunk @ K_tape.T
        sims_scaled = float(beta) * sims
        sims_scaled = sims_scaled - sims_scaled.max(axis=1, keepdims=True)
        w = np.exp(sims_scaled)
        w = w / w.sum(axis=1, keepdims=True).clip(min=1e-30)
        p = w @ V_tape
        p_n = p / np.linalg.norm(p, axis=1, keepdims=True).clip(min=1e-12)
        sims_match = p_n @ V_tape.T
        argmax = sims_match.argmax(axis=1)
        targets = np.arange(start, end)
        n_hits += int((argmax == targets).sum())
    return n_hits / float(m_items)


# ---------------------------------------------------------------------------
# Per-arm runner
# ---------------------------------------------------------------------------
def run_one_arm(seed: int, arm_name: str, alpha: float, m_items: int,
                sigma: float, n_c: int, attn_chunk: int,
                out_dir: Path) -> Dict:
    """Encode independent keys+vals; noise queries per arm; run one
    dense-attention READ at fixed beta=13."""
    t0 = time.time()
    arm_seed_offset = hash(arm_name) & 0xFFFF
    rng = np.random.RandomState(seed + arm_seed_offset)
    try:
        keys, vals = _generate_indep_keys_and_vals(m_items, n_c, rng)
        cos_margin = _cosine_margin_estimate(keys)
        noise_rng = np.random.RandomState(seed + arm_seed_offset + 100003)
        queries = _make_noisy_query(keys, sigma, noise_rng)
        recall = _replace_read_noisy_numpy(keys, vals, queries, BETA, attn_chunk)
        # Capture bytes for META_RULE_AF hash check (small proxy: use the
        # first N of the readout signature; here we use the final queries
        # tensor's bytes — bit-identical arms would produce identical
        # queries, keys, and vals, which would be a real bug).
        arm_digest = hashlib.sha256(queries.tobytes()).hexdigest()[:16]
        arm_status = "OK"
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        cos_margin = float("nan")
        recall = float("nan")
        arm_digest = "ERR"
        arm_status = f"ERROR: {type(exc).__name__}: {exc}"
    wall = time.time() - t0

    arm_dict = {
        "arm_name": arm_name,
        "alpha_used": float(alpha),
        "m_items": int(m_items),
        "sigma_used": float(sigma),
        "beta_used": float(BETA),
        "N_c": int(n_c),
        "recall_cortex": float(recall),
        "cosine_margin_used": float(cos_margin),
        "arm_digest": arm_digest,
        "wall_s": float(wall),
        "backend": "numpy",
        "arm_status": arm_status,
    }
    print(f"  [seed={seed} {arm_name}] recall={recall:.3f} "
          f"alpha={alpha:.2f} M={m_items} sigma={sigma:.2f} "
          f"cos_margin={cos_margin:.3f} wall={wall:.1f}s "
          f"status={arm_status}", flush=True)
    emit_heartbeat(out_dir, unit_idx=hash(arm_name) & 0xFFFF,
                   total_units=EXPECTED_N_ARMS, elapsed_s=wall,
                   extra={"arm": arm_name, "alpha": alpha, "sigma": sigma,
                          "recall": recall, "M": m_items,
                          "cos_margin": cos_margin})
    return arm_dict


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_arm_specs_cardinality() -> None:
    if len(ARM_SPECS_FULL) != 16:
        raise AssertionError(
            f"ARM_SPECS_FULL must be 16; got {len(ARM_SPECS_FULL)}"
        )
    names = set(spec[0] for spec in ARM_SPECS_FULL)
    if len(names) != 16:
        raise AssertionError(
            f"ARM_SPECS names must be unique; got {len(names)} unique of 16"
        )
    alphas = set(spec[1] for spec in ARM_SPECS_FULL)
    if alphas != {ALPHA_LOW, ALPHA_HIGH}:
        raise AssertionError(f"alphas must be {{ALPHA_LOW, ALPHA_HIGH}}; got {alphas}")
    sigmas = set(spec[3] for spec in ARM_SPECS_FULL)
    expected_sigmas = set(SIGMA_SWEEP)
    if sigmas != expected_sigmas:
        raise AssertionError(f"sigmas mismatch: {sigmas} vs {expected_sigmas}")


def _selftest_noise_0p02_at_small_scale_saturates() -> None:
    """PC selftest: at tiny scale, sigma=0.02 must saturate at >= 0.95."""
    n_c_t, m_t = 256, 100
    rng = np.random.RandomState(23)
    keys, vals = _generate_indep_keys_and_vals(m_t, n_c_t, rng)
    q_rng = np.random.RandomState(31)
    q = _make_noisy_query(keys, 0.02, q_rng)
    r = _replace_read_noisy_numpy(keys, vals, q, BETA, m_t)
    if r < 0.90:  # slightly relaxed at tiny scale
        raise AssertionError(
            f"sigma=0.02 did not saturate at tiny scale N_c={n_c_t} "
            f"M={m_t}: r={r}"
        )


def _selftest_higher_sigma_drops_recall() -> None:
    """Monotonicity check: at tiny scale, larger sigma should reduce recall.
    Use sigma=0.02 (should saturate) vs sigma=0.5 (should crumble)."""
    n_c_t, m_t = 256, 100
    rng = np.random.RandomState(29)
    keys, vals = _generate_indep_keys_and_vals(m_t, n_c_t, rng)
    q_rng_lo = np.random.RandomState(31)
    q_rng_hi = np.random.RandomState(37)
    q_lo = _make_noisy_query(keys, 0.02, q_rng_lo)
    q_hi = _make_noisy_query(keys, 0.5, q_rng_hi)
    r_lo = _replace_read_noisy_numpy(keys, vals, q_lo, BETA, m_t)
    r_hi = _replace_read_noisy_numpy(keys, vals, q_hi, BETA, m_t)
    if not (r_lo - r_hi >= 0.05):
        raise AssertionError(
            f"noise-monotonicity broken at tiny scale: "
            f"r(sigma=0.02)={r_lo} r(sigma=0.5)={r_hi} "
            f"delta={r_lo - r_hi}"
        )


def _selftest_alpha_load_ordering_at_high_sigma() -> None:
    """At tiny scale, at moderate sigma, higher alpha should have LOWER
    or equal recall (interaction predicted by Sonnet drill; also a sanity
    check that the M axis actually produces different results — at very
    small M the argmax problem is trivial). Uses sigma=0.20."""
    n_c_t = 256
    m_lo = int(round(0.10 * n_c_t))  # 26
    m_hi = int(round(0.45 * n_c_t))  # 115
    sigma_test = 0.20
    rng_lo = np.random.RandomState(41)
    rng_hi = np.random.RandomState(43)
    k_lo, v_lo = _generate_indep_keys_and_vals(m_lo, n_c_t, rng_lo)
    k_hi, v_hi = _generate_indep_keys_and_vals(m_hi, n_c_t, rng_hi)
    q_lo = _make_noisy_query(k_lo, sigma_test, np.random.RandomState(47))
    q_hi = _make_noisy_query(k_hi, sigma_test, np.random.RandomState(53))
    r_lo = _replace_read_noisy_numpy(k_lo, v_lo, q_lo, BETA, m_lo)
    r_hi = _replace_read_noisy_numpy(k_hi, v_hi, q_hi, BETA, m_hi)
    # At tiny scale we don't require large delta but low-alpha shouldn't
    # be strictly below high-alpha (that would be a wiring bug).
    if r_lo + 1e-6 < r_hi - 0.05:
        raise AssertionError(
            f"alpha-load ordering violated at tiny scale: "
            f"r(alpha=0.10)={r_lo} < r(alpha=0.45)={r_hi} at sigma={sigma_test} "
            f"(unexpected; may indicate M-axis wiring bug)"
        )


def run_all_selftests(seed_this_chunk: int, anchor_name: str) -> None:
    try:
        _selftest_arm_specs_cardinality()
        _selftest_noise_0p02_at_small_scale_saturates()
        _selftest_higher_sigma_drops_recall()
        _selftest_alpha_load_ordering_at_high_sigma()
        if f"seed_{seed_this_chunk}" not in anchor_name:
            raise AssertionError(
                f"anchor '{anchor_name}' missing seed_{seed_this_chunk}"
            )
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)


# ---------------------------------------------------------------------------
# sigma_crit interpolation
# ---------------------------------------------------------------------------
def _interp_sigma_crit(recalls_by_sigma: List[Tuple[float, float]],
                       threshold: float = 0.50) -> float:
    """Return smallest sigma at which linearly-interpolated recall crosses
    threshold from above. Points must be sorted by sigma ascending.

    Returns +inf if recall never drops below threshold within range.
    Returns 0.0 if recall is already below threshold at first sigma.
    """
    pts = sorted(recalls_by_sigma, key=lambda t: t[0])
    if not pts:
        return float("nan")
    if pts[0][1] < threshold:
        return 0.0
    for i in range(len(pts) - 1):
        s0, r0 = pts[i]
        s1, r1 = pts[i + 1]
        if r0 >= threshold and r1 < threshold:
            # Linear interpolate between (s0, r0) and (s1, r1).
            if abs(r0 - r1) < 1e-12:
                return s0
            frac = (r0 - threshold) / (r0 - r1)
            return s0 + frac * (s1 - s0)
    return float("inf")


# ---------------------------------------------------------------------------
# Verdict (per-seed; final aggregation happens at 3-seed VET)
# ---------------------------------------------------------------------------
def compute_verdict(per_seed_result: Dict) -> Tuple[str, str, Dict]:
    arms = per_seed_result.get("arms", [])
    if len(arms) != EXPECTED_N_ARMS:
        return ("HARD_FAIL",
                f"HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: expected "
                f"{EXPECTED_N_ARMS} arms, got {len(arms)}",
                {})

    fail_reasons: List[str] = []
    warn_reasons: List[str] = []

    for a in arms:
        if a["arm_status"] != "OK":
            fail_reasons.append(
                f"{a['arm_name']} error: {a['arm_status']}"
            )

    # Group arms by alpha.
    a10_arms = [a for a in arms if abs(a["alpha_used"] - ALPHA_LOW) < 1e-9]
    a45_arms = [a for a in arms if abs(a["alpha_used"] - ALPHA_HIGH) < 1e-9]
    a10_by_sigma = [(a["sigma_used"], a["recall_cortex"]) for a in a10_arms]
    a45_by_sigma = [(a["sigma_used"], a["recall_cortex"]) for a in a45_arms]

    # Broken-PC gate: (alpha, sigma=0.02) must saturate at >= 0.95.
    pc_a10 = [r for (s, r) in a10_by_sigma if abs(s - 0.02) < 1e-9]
    pc_a45 = [r for (s, r) in a45_by_sigma if abs(s - 0.02) < 1e-9]
    if pc_a10 and pc_a10[0] < BROKEN_PC_FLOOR:
        fail_reasons.append(
            f"HF_BROKEN_PC: ARM_A10_S02 recall={pc_a10[0]:.3f} "
            f"< {BROKEN_PC_FLOOR}"
        )
    if pc_a45 and pc_a45[0] < BROKEN_PC_FLOOR:
        fail_reasons.append(
            f"HF_BROKEN_PC: ARM_A45_S02 recall={pc_a45[0]:.3f} "
            f"< {BROKEN_PC_FLOOR}"
        )

    # Regime-mismatch gate: (alpha=0.45, sigma=0.10) must match v3 0.785 +/- 0.10.
    a45_s10 = [r for (s, r) in a45_by_sigma if abs(s - 0.10) < 1e-9]
    if a45_s10:
        dev = abs(a45_s10[0] - V3_CG_REFERENCE_RECALL)
        if dev > REGIME_MATCH_TOL:
            fail_reasons.append(
                f"HF_REGIME_MISMATCH: ARM_A45_S10 recall={a45_s10[0]:.3f} "
                f"deviates from v3 CG {V3_CG_REFERENCE_RECALL} by {dev:.3f} "
                f"(> {REGIME_MATCH_TOL})"
            )

    # HF_TOTAL_SATURATION / HF_TOTAL_COLLAPSE.
    all_recalls = [a["recall_cortex"] for a in arms]
    if all(r >= TOTAL_SAT_FLOOR for r in all_recalls):
        fail_reasons.append(
            f"HF_TOTAL_SATURATION: all 16 arms >= {TOTAL_SAT_FLOOR} "
            f"(sigma range insufficient to reach cliff)"
        )
    if all(r <= TOTAL_COLLAPSE_CEIL for r in all_recalls):
        fail_reasons.append(
            f"HF_TOTAL_COLLAPSE: all 16 arms <= {TOTAL_COLLAPSE_CEIL} "
            f"(both alpha above cliff at all tested sigma)"
        )

    # META_RULE_AF bit-identity across arms.
    # Different (alpha, sigma) => different M and different noise; digests
    # SHOULD differ. Exempt is ceiling-tie AT recall=1.000 across arms with
    # different noise regimes.
    digests = {a["arm_name"]: a["arm_digest"] for a in arms}
    for i in range(len(arms)):
        for j in range(i + 1, len(arms)):
            a_i, a_j = arms[i], arms[j]
            if a_i["arm_digest"] == "ERR" or a_j["arm_digest"] == "ERR":
                continue
            if a_i["arm_digest"] == a_j["arm_digest"]:
                # bit-identical query tensors between DIFFERENT (alpha, sigma)
                # is impossible under this design.
                fail_reasons.append(
                    f"META_RULE_AF: {a_i['arm_name']} and {a_j['arm_name']} "
                    f"bit-identical queries (digest={a_i['arm_digest']})"
                )

    # Compute sigma_crit per alpha.
    sigma_crit_10 = _interp_sigma_crit(a10_by_sigma, RECALL_HALF_CROSSING)
    sigma_crit_45 = _interp_sigma_crit(a45_by_sigma, RECALL_HALF_CROSSING)
    delta_sigma_crit = sigma_crit_10 - sigma_crit_45

    # HP_MONOTONIC_ALPHA at sigma=0.10.
    a10_s10 = [r for (s, r) in a10_by_sigma if abs(s - 0.10) < 1e-9]
    monotonic_at_s10 = False
    if a10_s10 and a45_s10:
        monotonic_at_s10 = (a10_s10[0] > a45_s10[0])

    headline = {
        "sigma_crit_alpha_10": sigma_crit_10,
        "sigma_crit_alpha_45": sigma_crit_45,
        "delta_sigma_crit": delta_sigma_crit,
        "recall_a10_by_sigma": a10_by_sigma,
        "recall_a45_by_sigma": a45_by_sigma,
        "hp_interaction_confirmed": (delta_sigma_crit >= HP_INTERACTION_DELTA),
        "hp_monotonic_alpha_at_s10": monotonic_at_s10,
        "recall_a10_s10": (a10_s10[0] if a10_s10 else float("nan")),
        "recall_a45_s10": (a45_s10[0] if a45_s10 else float("nan")),
        "recall_a10_s02_pc": (pc_a10[0] if pc_a10 else float("nan")),
        "recall_a45_s02_pc": (pc_a45[0] if pc_a45 else float("nan")),
        "regime_match_a45_s10_dev_from_v3": (
            abs(a45_s10[0] - V3_CG_REFERENCE_RECALL) if a45_s10 else float("nan")
        ),
    }

    if fail_reasons:
        return ("HARD_FAIL", "; ".join(fail_reasons)[:800], headline)

    if delta_sigma_crit >= HP_INTERACTION_DELTA and monotonic_at_s10:
        return ("HARD_PASS",
                f"JOINT_SURFACE_INTERACTION_CONFIRMED: "
                f"sigma_crit(a=0.10)={sigma_crit_10:.3f} - "
                f"sigma_crit(a=0.45)={sigma_crit_45:.3f} = "
                f"{delta_sigma_crit:.3f} >= {HP_INTERACTION_DELTA}; "
                f"monotonic@s0.10: r(a=0.10)={a10_s10[0]:.3f} > "
                f"r(a=0.45)={a45_s10[0]:.3f}. "
                f"M3 refuse-gate joint-controller upgrade justified.",
                headline)

    if abs(delta_sigma_crit) < HF_INTERACTION_TOL and not monotonic_at_s10:
        # Interaction absent: refuse-gate can stay 1D.
        # This is a HARD_FAIL for the joint-surface hypothesis but a
        # POSITIVE (M3-favorable) result for architecture simplicity.
        # Tier as HF per pre-reg but log the load-bearing implication in msg.
        return ("HARD_FAIL",
                f"HF_INTERACTION_ABSENT: |delta_sigma_crit|="
                f"{abs(delta_sigma_crit):.3f} < {HF_INTERACTION_TOL} AND "
                f"monotonic@s0.10 FALSE. Sonnet Dim T Type-3 interaction "
                f"claim REFUTED at this regime. M3 refuse-gate can stay "
                f"1D on sigma. r(a=0.10,s=0.10)={a10_s10[0]:.3f} vs "
                f"r(a=0.45,s=0.10)={a45_s10[0]:.3f}. "
                f"sigma_crit(a=0.10)={sigma_crit_10:.3f} "
                f"sigma_crit(a=0.45)={sigma_crit_45:.3f}.",
                headline)

    # MB region.
    if MB_INTERACTION_DELTA <= delta_sigma_crit < HP_INTERACTION_DELTA:
        warn_reasons.append(
            f"MB_WEAK_INTERACTION: delta_sigma_crit={delta_sigma_crit:.3f} "
            f"in [{MB_INTERACTION_DELTA}, {HP_INTERACTION_DELTA}); partial "
            f"joint-surface effect, inconclusive"
        )
    if not monotonic_at_s10 and delta_sigma_crit >= HP_INTERACTION_DELTA:
        warn_reasons.append(
            f"MB_SIGMA_CRIT_GAP_WITHOUT_MONOTONICITY_AT_S10: "
            f"delta_sigma_crit large but r(a=0.10,s=0.10)={a10_s10[0]:.3f} "
            f"vs r(a=0.45,s=0.10)={a45_s10[0]:.3f} not monotonic"
        )
    return ("MIDDLE_BAND", "; ".join(warn_reasons)[:800] or
            f"delta_sigma_crit={delta_sigma_crit:.3f} inconclusive",
            headline)
