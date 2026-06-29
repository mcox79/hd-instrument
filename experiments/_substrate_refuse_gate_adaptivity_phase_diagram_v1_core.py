"""Shared core for substrate_refuse_gate_adaptivity_phase_diagram_v1 sibling cells.

COMPONENT-SUBSTITUTION phase diagram for refuse-gate ADAPTIVITY family on
the substrate (USER + Research directive 2026-06-28). Refuse-gate chain-grade
evidence to date uses a SINGLE adaptivity strategy: fixed similarity threshold
at 0.40 (substrate_refuse_gate_v_rel_extension_v1 HARD_PASS at V_REL=256
2026-06-25). The gate FAMILY has never been compared with alternatives.

Refuse-gate families (OUTER axis):
    fixed_threshold      : refused = (max_sim < 0.40) (CG default; control)
    adaptive_bayesian_CI : Beta posterior CI; refuse if sim below CI lower
    learned_logistic     : sigmoid P(in|sim); refuse if P < 0.5
    percentile_based     : refuse if sim below 5th-percentile of calibration

Inner axes: query_regime (4) x V_REL_calibration_size (3).
4 fams * 4 regimes * 3 cal_sizes = 48 phase points per seed FULL.
4 fams * 2 regimes * 1 cal_size  =  8 corner points per seed SMOKE.

Substrate config FIXED: N=8192 (FULL), V_C=600, V_REL=256, encoder=binary_bipolar.

PRE-REG: preregs/2026-06-28_substrate_refuse_gate_adaptivity_phase_diagram_v1.md

Sibling cells import:
    run_one_seed_phase_diagram(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    REFUSE_FAMILIES,
    REGIMES_FULL, REGIMES_SMOKE, CAL_SIZES_FULL, CAL_SIZES_SMOKE
    N_FULL, N_SMOKE, V_C_PER_CAT_FULL, V_C_PER_CAT_SMOKE
    EXPECTED_N_UNITS_FULL, EXPECTED_N_UNITS_SMOKE

ASCII-only. No unicode. numpy-only (no torch); CPU-native.

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn)
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import time
from pathlib import Path
from typing import Any, Callable, Dict, List, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------
SATURATED_F1 = 0.98
HARD_PASS_LO = 0.85
MIDDLE_BAND_LO = 0.65
FLOOR_F1 = 0.30
HP_DISCRIMINATOR = 0.30
MB_DISCRIMINATOR = 0.15

# Fixed threshold for the fixed_threshold family (matches prior CG cell)
FIXED_SUBJECT_AUDIT_THR = 0.40

# Refuse-gate families (OUTER axis; LOCKED at module init)
REFUSE_FAMILIES = ("fixed_threshold", "adaptive_bayesian_CI",
                   "learned_logistic", "percentile_based")

# Query regimes (inner axis 1)
REGIMES_FULL = ("PURE_IN_DOMAIN", "PURE_OUT_OF_DOMAIN",
                "NEAR_DOMAIN_MIXED", "AMBIGUOUS_BOUNDARY")
REGIMES_SMOKE = ("PURE_OUT_OF_DOMAIN", "AMBIGUOUS_BOUNDARY")  # AMBIGUOUS forces non-saturation

# Calibration set sizes (inner axis 2)
CAL_SIZES_FULL = (64, 256, 1024)
CAL_SIZES_SMOKE = (64,)

# Substrate scale
N_FULL = 8192
N_SMOKE = 2048
V_REL_FIXED = 256  # matches CG envelope
V_C_PER_CAT_FULL = 200
V_C_PER_CAT_SMOKE = 50
N_QUERIES_PER_REGIME_FULL = 80
N_QUERIES_PER_REGIME_SMOKE = 30

IN_DOMAIN_CATEGORIES = ("animals", "geography", "tools")
OUT_DOMAIN_CATEGORIES = ("medical", "legal", "financial")
N_IN_CAT = len(IN_DOMAIN_CATEGORIES)
N_OUT_CAT = len(OUT_DOMAIN_CATEGORIES)

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (len(REFUSE_FAMILIES) * len(REGIMES_FULL)
                         * len(CAL_SIZES_FULL))  # 48
EXPECTED_N_UNITS_SMOKE = (len(REFUSE_FAMILIES) * len(REGIMES_SMOKE)
                          * len(CAL_SIZES_SMOKE))  # 8

# Positive control point
POSITIVE_CONTROL = {
    "family": "fixed_threshold",
    "regime": "PURE_OUT_OF_DOMAIN",
    "cal_size": 256,
    "refuse_rate_floor": 0.85,
}
POSITIVE_CONTROL_SMOKE = {
    "family": "fixed_threshold",
    "regime": "PURE_OUT_OF_DOMAIN",
    "cal_size": 64,
    "refuse_rate_floor": 0.75,
}

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


# ---------------------------------------------------------------------------
# Noise-floor / threshold prediction (META_RULE_AG)
# ---------------------------------------------------------------------------
def noise_floor_prediction(N: int, V_C: int) -> float:
    """Out-of-domain similarity noise floor (sqrt(2 ln V / N))."""
    if N <= 0 or V_C <= 1:
        return 0.0
    return math.sqrt(2.0 * math.log(V_C) / N)


def get_backend_label() -> str:
    return "numpy.cpu"


# ---------------------------------------------------------------------------
# Substrate construction (binary_bipolar dense codebook)
# ---------------------------------------------------------------------------
def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Unit-norm bipolar {-1,+1}^n codebook of shape (M, n)."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_substrate(g: np.random.Generator, N: int, V_C_per_cat: int,
                    V_REL: int) -> Dict[str, Any]:
    """Build substrate at given N + V_C + V_REL."""
    V_C_IN = V_C_per_cat * N_IN_CAT
    V_C_OUT = V_C_per_cat * N_OUT_CAT
    W_subjects_in = bipolar(V_C_IN, N, g)
    W_relations_in = bipolar(V_REL, N, g)
    out_subject_atoms = bipolar(V_C_OUT, N, g)
    out_relation_atoms = bipolar(V_REL, N, g)
    return {
        "W_subjects_in": W_subjects_in,
        "W_relations_in": W_relations_in,
        "out_subject_atoms": out_subject_atoms,
        "out_relation_atoms": out_relation_atoms,
        "N": N,
        "V_C_IN": V_C_IN,
        "V_C_OUT": V_C_OUT,
        "V_REL": V_REL,
    }


def add_noise(vec: np.ndarray, flip_frac: float,
              g: np.random.Generator) -> np.ndarray:
    """Bit-flip noise; renormalize."""
    n = vec.shape[0]
    n_flip = int(round(n * flip_frac))
    flip_idxs = g.choice(n, size=n_flip, replace=False)
    v = vec.copy()
    v[flip_idxs] *= -1.0
    return v / (np.linalg.norm(v) + 1e-8)


# ---------------------------------------------------------------------------
# Query corpus per regime
# ---------------------------------------------------------------------------
def build_queries(g: np.random.Generator, substrate: Dict[str, Any],
                  regime: str, n_queries: int,
                  flip_frac: float = 0.10) -> List[Dict[str, Any]]:
    """Build query list with (subject_vec, relation_vec, is_in_domain)."""
    W_sub = substrate["W_subjects_in"]
    W_rel = substrate["W_relations_in"]
    out_sub = substrate["out_subject_atoms"]
    out_rel = substrate["out_relation_atoms"]
    V_C_IN = substrate["V_C_IN"]
    V_C_OUT = substrate["V_C_OUT"]
    V_REL = substrate["V_REL"]
    qs: List[Dict[str, Any]] = []
    for _ in range(n_queries):
        if regime == "PURE_IN_DOMAIN":
            s_i = int(g.integers(0, V_C_IN))
            r_i = int(g.integers(0, V_REL))
            qs.append({
                "subject_vec": add_noise(W_sub[s_i], flip_frac, g),
                "relation_vec": add_noise(W_rel[r_i], flip_frac, g),
                "is_in_domain": True,
                "should_refuse": False,
            })
        elif regime == "PURE_OUT_OF_DOMAIN":
            s_i = int(g.integers(0, V_C_OUT))
            r_i = int(g.integers(0, V_REL))
            qs.append({
                "subject_vec": add_noise(out_sub[s_i], flip_frac, g),
                "relation_vec": add_noise(out_rel[r_i], flip_frac, g),
                "is_in_domain": False,
                "should_refuse": True,
            })
        elif regime == "NEAR_DOMAIN_MIXED":
            # in-domain subject + out-domain relation
            s_i = int(g.integers(0, V_C_IN))
            r_i = int(g.integers(0, V_REL))
            qs.append({
                "subject_vec": add_noise(W_sub[s_i], flip_frac, g),
                "relation_vec": add_noise(out_rel[r_i], flip_frac, g),
                "is_in_domain": False,  # mixed = should refuse
                "should_refuse": True,
            })
        elif regime == "AMBIGUOUS_BOUNDARY":
            # Mid-noise in-domain queries (22% flip -> sim ~ 0.55, well above
            # fixed_threshold=0.40 but well below typical cal_in mean ~0.80).
            # GROUND TRUTH: query IS in-domain (subject from in-domain catalog).
            # Calibrated families may over-refuse here via uncertainty -- which
            # is exactly the diagnostic the AMBIGUOUS regime is designed to
            # surface. should_refuse=False is the honest label; gate "loses"
            # TNR if it over-refuses.
            s_i = int(g.integers(0, V_C_IN))
            r_i = int(g.integers(0, V_REL))
            mid_flip = 0.22  # mid-band: ~0.55 sim; families diverge here
            qs.append({
                "subject_vec": add_noise(W_sub[s_i], mid_flip, g),
                "relation_vec": add_noise(W_rel[r_i], mid_flip, g),
                "is_in_domain": True,
                "should_refuse": False,
            })
        else:
            raise ValueError(f"unknown regime {regime!r}")
    return qs


def query_max_sim(q: Dict[str, Any], W_in: np.ndarray) -> float:
    """Max cosine of subject_vec against in-domain subject codebook."""
    sims = W_in @ q["subject_vec"]
    return float(np.max(sims))


# ---------------------------------------------------------------------------
# Refuse-gate family implementations
# ---------------------------------------------------------------------------
def gate_fixed_threshold(query_sim: float,
                         calibration_sims_in: np.ndarray) -> bool:
    """fixed_threshold: refused = (sim < 0.40); ignores calibration."""
    return query_sim < FIXED_SUBJECT_AUDIT_THR


def gate_adaptive_bayesian_CI(query_sim: float,
                              calibration_sims_in: np.ndarray) -> bool:
    """Bayesian credible-interval gate.

    Treat calibration in-domain sims as Gaussian-distributed (sufficient
    statistics: mean, var). Posterior on the in-domain mean is
    N(mean_emp, var_emp/n). Refuse if query_sim is below the 5%-CI lower
    bound of the in-domain similarity distribution (NOT the mean's CI):
    lower = mean_emp - 1.645 * sigma_emp.

    Carries explicit uncertainty: small calibration sets give wider
    lower-bound (more conservative answer-rate).
    """
    if calibration_sims_in.size < 2:
        # Fallback to fixed threshold if no calibration
        return query_sim < FIXED_SUBJECT_AUDIT_THR
    mu = float(np.mean(calibration_sims_in))
    sigma = float(np.std(calibration_sims_in, ddof=1) + 1e-8)
    # 5% lower tail of in-domain distribution
    lower_bound = mu - 1.645 * sigma
    return query_sim < lower_bound


def gate_learned_logistic(query_sim: float,
                          calibration_sims_in: np.ndarray,
                          calibration_sims_out: np.ndarray) -> bool:
    """Fit a 1-D logistic on calibration in/out sims; refuse if P_in < 0.5.

    Closed-form logistic via Newton-Raphson on the 1-D case (efficient
    enough for cal_size <= 1024). Uses 5-iter Newton with regularization.
    """
    if calibration_sims_in.size < 2 or calibration_sims_out.size < 2:
        return query_sim < FIXED_SUBJECT_AUDIT_THR

    # Build feature vector + label
    X = np.concatenate([calibration_sims_in,
                        calibration_sims_out]).astype(np.float64)
    y = np.concatenate([np.ones(calibration_sims_in.size),
                        np.zeros(calibration_sims_out.size)])

    # Newton-Raphson on logistic regression with 1 feature + bias
    # w0 + w1 * sim ; sigmoid(z) = 1 / (1 + exp(-z))
    w = np.zeros(2, dtype=np.float64)
    Xb = np.column_stack([np.ones_like(X), X])
    for _ in range(8):
        z = Xb @ w
        p = 1.0 / (1.0 + np.exp(-np.clip(z, -30.0, 30.0)))
        # gradient
        grad = Xb.T @ (p - y) + 0.01 * w  # L2 reg
        # Hessian: X^T diag(p*(1-p)) X + reg * I
        W_diag = p * (1.0 - p)
        H = Xb.T @ (Xb * W_diag[:, None]) + 0.01 * np.eye(2)
        try:
            delta = np.linalg.solve(H, grad)
        except np.linalg.LinAlgError:
            break
        w = w - delta
        if np.linalg.norm(delta) < 1e-6:
            break

    z = w[0] + w[1] * query_sim
    p_in = 1.0 / (1.0 + math.exp(-max(min(z, 30.0), -30.0)))
    return p_in < 0.5


def gate_percentile_based(query_sim: float,
                          calibration_sims_in: np.ndarray) -> bool:
    """5th-percentile of in-domain calibration sims; refuse if below."""
    if calibration_sims_in.size < 2:
        return query_sim < FIXED_SUBJECT_AUDIT_THR
    threshold = float(np.percentile(calibration_sims_in, 5.0))
    return query_sim < threshold


def make_calibration(g: np.random.Generator, substrate: Dict[str, Any],
                     cal_size: int, flip_frac: float = 0.10
                     ) -> Tuple[np.ndarray, np.ndarray]:
    """Sample cal_size in-domain + cal_size out-domain query sims."""
    V_C_IN = substrate["V_C_IN"]
    V_C_OUT = substrate["V_C_OUT"]
    W_sub = substrate["W_subjects_in"]
    out_sub = substrate["out_subject_atoms"]
    sims_in: List[float] = []
    sims_out: List[float] = []
    for _ in range(cal_size):
        s_i = int(g.integers(0, V_C_IN))
        v_in = add_noise(W_sub[s_i], flip_frac, g)
        sims_in.append(float(np.max(W_sub @ v_in)))
    for _ in range(cal_size):
        s_i = int(g.integers(0, V_C_OUT))
        v_out = add_noise(out_sub[s_i], flip_frac, g)
        sims_out.append(float(np.max(W_sub @ v_out)))
    return np.array(sims_in, dtype=np.float32), np.array(sims_out, dtype=np.float32)


def apply_family(family: str, query_sim: float,
                 cal_in: np.ndarray, cal_out: np.ndarray) -> bool:
    if family == "fixed_threshold":
        return gate_fixed_threshold(query_sim, cal_in)
    if family == "adaptive_bayesian_CI":
        return gate_adaptive_bayesian_CI(query_sim, cal_in)
    if family == "learned_logistic":
        return gate_learned_logistic(query_sim, cal_in, cal_out)
    if family == "percentile_based":
        return gate_percentile_based(query_sim, cal_in)
    raise ValueError(f"unknown family {family!r}")


# ---------------------------------------------------------------------------
# Per-point evaluation
# ---------------------------------------------------------------------------
def compute_f1(decisions: List[bool], should_refuse: List[bool]
               ) -> Tuple[float, float, float]:
    """Return (TPR, TNR, F1) over decisions vs should_refuse.

    TPR: of queries that SHOULD refuse, fraction we DID refuse.
    TNR: of queries that should NOT refuse, fraction we did NOT refuse.
    F1: harmonic mean of TPR, TNR (joint quality).
    """
    n_pos = sum(1 for s in should_refuse if s)
    n_neg = sum(1 for s in should_refuse if not s)
    if n_pos == 0 and n_neg == 0:
        return 0.0, 0.0, 0.0
    n_tp = sum(1 for d, s in zip(decisions, should_refuse) if d and s)
    n_tn = sum(1 for d, s in zip(decisions, should_refuse) if (not d) and (not s))
    tpr = n_tp / n_pos if n_pos > 0 else 1.0  # nothing to refuse -> trivially perfect
    tnr = n_tn / n_neg if n_neg > 0 else 1.0  # nothing to answer -> trivially perfect
    if tpr + tnr <= 0:
        f1 = 0.0
    else:
        f1 = 2.0 * tpr * tnr / (tpr + tnr + 1e-12)
    return tpr, tnr, f1


def eval_phase_point(family: str, regime: str, cal_size: int,
                     substrate: Dict[str, Any],
                     n_queries: int, seed: int) -> Dict[str, Any]:
    """Run one (family, regime, cal_size) phase point with both arms."""
    if family not in REFUSE_FAMILIES:
        raise ValueError(f"unknown family={family!r}")
    if regime not in REGIMES_FULL:
        raise ValueError(f"unknown regime={regime!r}")

    t0 = time.time()
    sub_seed = seed * 100003 + hash(family + regime) % 9973 + cal_size * 7

    # Calibration (shared across regimes; depends only on cal_size + seed)
    cal_g = np.random.default_rng(seed * 10007 + cal_size * 31)
    cal_in, cal_out = make_calibration(cal_g, substrate, cal_size)

    # Queries for this regime
    q_g = np.random.default_rng(sub_seed)
    queries = build_queries(q_g, substrate, regime, n_queries)

    # Compute query max-sim once (shared across families)
    sims = [query_max_sim(q, substrate["W_subjects_in"]) for q in queries]
    should_refuse = [q["should_refuse"] for q in queries]

    # ARM_MECHANISM
    decisions = [apply_family(family, s, cal_in, cal_out) for s in sims]
    tpr, tnr, f1 = compute_f1(decisions, should_refuse)

    # Output bytes hash for family-distinctness check
    mech_payload = json.dumps([int(d) for d in decisions]).encode("utf-8")
    mech_hash = hashlib.sha256(mech_payload).hexdigest()[:16]

    # ARM_RANDOM_FLOOR: Bernoulli(0.5) decisions (no info)
    rnd_g = np.random.default_rng(sub_seed + 99991)
    rnd_decisions = [bool(rnd_g.integers(0, 2)) for _ in range(n_queries)]
    rnd_tpr, rnd_tnr, rnd_f1 = compute_f1(rnd_decisions, should_refuse)
    rnd_payload = json.dumps([int(d) for d in rnd_decisions]).encode("utf-8")
    rnd_hash = hashlib.sha256(rnd_payload).hexdigest()[:16]

    # Refuse-rate (raw): fraction of all queries family refused
    refuse_rate = sum(1 for d in decisions if d) / max(len(decisions), 1)

    elapsed = time.time() - t0
    discriminator = f1 - rnd_f1

    # Per-point verdict tier (on F1)
    if f1 >= SATURATED_F1:
        tier = "SATURATED"
        saturation_flag = True
    elif f1 >= HARD_PASS_LO and discriminator >= HP_DISCRIMINATOR:
        tier = "HARD_PASS"
        saturation_flag = False
    elif f1 >= MIDDLE_BAND_LO and discriminator >= MB_DISCRIMINATOR:
        tier = "MIDDLE_BAND"
        saturation_flag = False
    elif f1 <= FLOOR_F1:
        tier = "FLOOR"
        saturation_flag = False
    else:
        tier = "HARD_FAIL"
        saturation_flag = False

    return {
        "family": family,
        "regime": regime,
        "cal_size": cal_size,
        "n_queries": n_queries,
        "seed": seed,
        "f1_mechanism": round(f1, 4),
        "tpr_mechanism": round(tpr, 4),
        "tnr_mechanism": round(tnr, 4),
        "refuse_rate_mechanism": round(refuse_rate, 4),
        "f1_random": round(rnd_f1, 4),
        "tpr_random": round(rnd_tpr, 4),
        "tnr_random": round(rnd_tnr, 4),
        "discriminator": round(discriminator, 4),
        "mech_decision_hash": mech_hash,
        "rnd_decision_hash": rnd_hash,
        "verdict_tier_per_point": tier,
        "saturation_flag": saturation_flag,
        "elapsed_per_point_s": round(elapsed, 3),
        "noise_floor_prediction": round(
            noise_floor_prediction(substrate["N"], substrate["V_C_IN"]), 4),
    }


# ---------------------------------------------------------------------------
# Selftest
# ---------------------------------------------------------------------------
def selftest(seed: int) -> Tuple[bool, str]:
    """Refuse-gate mechanism sanity at small scale.

    For each family at N=512, V_C=12, V_REL=8, cal_size=32:
      (a) PURE_IN queries: family ANSWERS (refused=False) at >= 80%
      (b) PURE_OUT queries: family REFUSES at >= 80%
      (c) AMBIGUOUS: family produces decisions, family pair-hashes have
          at least 1 differing pair across 4 families
    """
    msgs: List[str] = []

    # 1. Cardinality math
    if EXPECTED_N_UNITS_FULL != 48:
        return False, f"FULL cardinality {EXPECTED_N_UNITS_FULL} != 48"
    if EXPECTED_N_UNITS_SMOKE != 8:
        return False, f"SMOKE cardinality {EXPECTED_N_UNITS_SMOKE} != 8"
    msgs.append(
        f"cardinality FULL={EXPECTED_N_UNITS_FULL} SMOKE={EXPECTED_N_UNITS_SMOKE}")

    # 2. Noise-floor formula sanity
    nf_full = noise_floor_prediction(8192, 600)
    nf_smoke = noise_floor_prediction(2048, 150)
    if not (0.02 < nf_full < 0.10):
        return False, f"noise_floor N=8192 V_C=600 outside (0.02, 0.10): {nf_full}"
    if not (0.04 < nf_smoke < 0.15):
        return False, f"noise_floor N=2048 V_C=150 outside (0.04, 0.15): {nf_smoke}"
    msgs.append(f"noise_floor FULL={nf_full:.4f} SMOKE={nf_smoke:.4f}")

    # 3. Build small substrate
    g = np.random.default_rng(seed)
    substrate = build_substrate(g, N=512, V_C_per_cat=4, V_REL=8)
    # V_C_IN = 12, V_C_OUT = 12, V_REL = 8

    cal_g = np.random.default_rng(seed + 999)
    cal_in, cal_out = make_calibration(cal_g, substrate, cal_size=32)

    # T_a + T_b: each family must answer pure_in >= 80% and refuse pure_out >= 80%
    for family in REFUSE_FAMILIES:
        # PURE_IN queries
        q_g = np.random.default_rng(seed * 10 + 1)
        in_queries = build_queries(q_g, substrate, "PURE_IN_DOMAIN", n_queries=40)
        in_sims = [query_max_sim(q, substrate["W_subjects_in"])
                   for q in in_queries]
        in_decisions = [apply_family(family, s, cal_in, cal_out) for s in in_sims]
        in_answer_rate = sum(1 for d in in_decisions if not d) / len(in_decisions)
        if in_answer_rate < 0.80:
            return False, (f"selftest_a FAIL {family}: answer_rate on PURE_IN "
                           f"{in_answer_rate:.3f} < 0.80")

        # PURE_OUT queries
        q_g = np.random.default_rng(seed * 10 + 2)
        out_queries = build_queries(q_g, substrate, "PURE_OUT_OF_DOMAIN",
                                    n_queries=40)
        out_sims = [query_max_sim(q, substrate["W_subjects_in"])
                    for q in out_queries]
        out_decisions = [apply_family(family, s, cal_in, cal_out) for s in out_sims]
        out_refuse_rate = sum(1 for d in out_decisions if d) / len(out_decisions)
        if out_refuse_rate < 0.80:
            return False, (f"selftest_b FAIL {family}: refuse_rate on PURE_OUT "
                           f"{out_refuse_rate:.3f} < 0.80")

        msgs.append(f"sanity {family}: PURE_IN answer={in_answer_rate:.3f} "
                    f"PURE_OUT refuse={out_refuse_rate:.3f}")

    # T_c: AMBIGUOUS decisions across families must have at least 1 pair differ
    q_g = np.random.default_rng(seed * 10 + 3)
    amb_queries = build_queries(q_g, substrate, "AMBIGUOUS_BOUNDARY",
                                n_queries=30)
    amb_sims = [query_max_sim(q, substrate["W_subjects_in"]) for q in amb_queries]
    family_decisions = {}
    for family in REFUSE_FAMILIES:
        ds = [apply_family(family, s, cal_in, cal_out) for s in amb_sims]
        family_decisions[family] = tuple(ds)
    distinct_count = len(set(family_decisions.values()))
    if distinct_count < 2:
        return False, (f"selftest_c FAIL: all 4 families produce IDENTICAL "
                       f"decisions on AMBIGUOUS_BOUNDARY -- family mechanism "
                       f"collapse at small scale")
    msgs.append(f"AMBIGUOUS: {distinct_count}/4 distinct family decision tuples")

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------
def run_one_seed_phase_diagram(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (family, regime, cal_size) phase points for one seed."""
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        N = N_SMOKE
        V_C_per_cat = V_C_PER_CAT_SMOKE
        regimes = REGIMES_SMOKE
        cal_sizes = CAL_SIZES_SMOKE
        n_queries_per_regime = N_QUERIES_PER_REGIME_SMOKE
    else:
        N = N_FULL
        V_C_per_cat = V_C_PER_CAT_FULL
        regimes = REGIMES_FULL
        cal_sizes = CAL_SIZES_FULL
        n_queries_per_regime = N_QUERIES_PER_REGIME_FULL

    expected_n_units = (len(REFUSE_FAMILIES) * len(regimes) * len(cal_sizes))

    print(f"[run_one_seed] seed={seed} mode={run_mode} N={N} "
          f"V_C_per_cat={V_C_per_cat} V_REL={V_REL_FIXED} "
          f"families={REFUSE_FAMILIES} regimes={regimes} cal_sizes={cal_sizes} "
          f"n_queries_per_regime={n_queries_per_regime} "
          f"expected_n={expected_n_units}", flush=True)

    nf_pred = noise_floor_prediction(N, V_C_per_cat * N_IN_CAT)
    print(f"[noise_floor] V_REL={V_REL_FIXED} N={N} V_C={V_C_per_cat * N_IN_CAT}: "
          f"out-of-domain noise={nf_pred:.4f}", flush=True)

    g_sub = np.random.default_rng(seed)
    substrate = build_substrate(g_sub, N=N, V_C_per_cat=V_C_per_cat,
                                V_REL=V_REL_FIXED)

    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    for family in REFUSE_FAMILIES:
        for regime in regimes:
            for cal_size in cal_sizes:
                print(f"[point] seed={seed} fam={family} regime={regime} "
                      f"cal_size={cal_size} ...", flush=True)
                pt = eval_phase_point(family, regime, cal_size, substrate,
                                      n_queries_per_regime, seed)
                phase_map.append(pt)
                print(f"  -> f1={pt['f1_mechanism']:.3f} "
                      f"tpr={pt['tpr_mechanism']:.3f} "
                      f"tnr={pt['tnr_mechanism']:.3f} "
                      f"refuse_rate={pt['refuse_rate_mechanism']:.3f} "
                      f"disc={pt['discriminator']:.3f} "
                      f"tier={pt['verdict_tier_per_point']} "
                      f"t={pt['elapsed_per_point_s']:.2f}s", flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units)

    # Per-family arms-differ + family-pair distinctness
    arms_differ_per_fam: Dict[str, Dict[str, Any]] = {}
    family_mech_hashes: Dict[str, str] = {}
    for family in REFUSE_FAMILIES:
        fam_pts = [p for p in phase_map if p["family"] == family]
        sub_payload = json.dumps([p["mech_decision_hash"] for p in fam_pts],
                                 sort_keys=True).encode("utf-8")
        rnd_payload = json.dumps([p["rnd_decision_hash"] for p in fam_pts],
                                 sort_keys=True).encode("utf-8")
        sub_hash = hashlib.sha256(sub_payload).hexdigest()
        rnd_hash = hashlib.sha256(rnd_payload).hexdigest()
        arms_differ_per_fam[family] = {
            "mechanism_hash": sub_hash,
            "random_hash": rnd_hash,
            "differ": sub_hash != rnd_hash,
        }
        family_mech_hashes[family] = sub_hash

    fams = list(REFUSE_FAMILIES)
    pairs_differ: Dict[str, bool] = {}
    for i in range(len(fams)):
        for j in range(i + 1, len(fams)):
            key = f"{fams[i]}_vs_{fams[j]}"
            pairs_differ[key] = (family_mech_hashes[fams[i]]
                                 != family_mech_hashes[fams[j]])
    n_pairs_differ = sum(1 for v in pairs_differ.values() if v)

    # Per-family summary
    per_family_summary: Dict[str, Dict[str, Any]] = {}
    for family in REFUSE_FAMILIES:
        fam_pts = [p for p in phase_map if p["family"] == family]
        f1_mean = float(np.mean([p["f1_mechanism"] for p in fam_pts]))
        tpr_mean = float(np.mean([p["tpr_mechanism"] for p in fam_pts]))
        tnr_mean = float(np.mean([p["tnr_mechanism"] for p in fam_pts]))
        n_sat = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "SATURATED")
        n_hp = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_PASS")
        n_mb = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "MIDDLE_BAND")
        n_floor = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "FLOOR")
        n_fail = sum(1 for p in fam_pts if p["verdict_tier_per_point"] == "HARD_FAIL")
        # cal_size sensitivity: f1 spread across cal_sizes (per regime; averaged)
        cal_spread = 0.0
        if len(cal_sizes) > 1:
            for regime in regimes:
                f1s_by_cal = [
                    float(np.mean([p["f1_mechanism"] for p in fam_pts
                                   if p["regime"] == regime and p["cal_size"] == c]))
                    for c in cal_sizes
                ]
                if f1s_by_cal:
                    cal_spread += max(f1s_by_cal) - min(f1s_by_cal)
            cal_spread = cal_spread / max(len(regimes), 1)
        per_family_summary[family] = {
            "f1_mean": round(f1_mean, 4),
            "tpr_mean": round(tpr_mean, 4),
            "tnr_mean": round(tnr_mean, 4),
            "cal_size_sensitivity": round(cal_spread, 4),
            "tier_counts": {"SATURATED": n_sat, "HARD_PASS": n_hp,
                            "MIDDLE_BAND": n_mb, "FLOOR": n_floor,
                            "HARD_FAIL": n_fail},
        }

    # Family tiering
    means = {f: per_family_summary[f]["f1_mean"] for f in REFUSE_FAMILIES}
    best_mean = max(means.values()) if means else 0.0
    family_tiers: Dict[str, str] = {}
    for f in REFUSE_FAMILIES:
        m = means[f]
        if m >= best_mean - 0.03:
            if m == best_mean:
                others = [v for k, v in means.items() if k != f]
                next_best = max(others) if others else 0.0
                if m - next_best > 0.05:
                    family_tiers[f] = "DOMINANT_FAMILY"
                else:
                    family_tiers[f] = "COMPETITIVE_FAMILY"
            else:
                family_tiers[f] = "COMPETITIVE_FAMILY"
        else:
            family_tiers[f] = "DOMINATED_FAMILY"

    # Positive control check
    control = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    ctrl_pts = [p for p in phase_map
                if p["family"] == control["family"]
                and p["regime"] == control["regime"]
                and p["cal_size"] == control["cal_size"]]
    ctrl_refuse = (ctrl_pts[0]["refuse_rate_mechanism"]
                   if ctrl_pts else -1.0)
    ctrl_ok = (ctrl_refuse >= control["refuse_rate_floor"])

    # Cell-level verdict
    n_passing = sum(1 for p in phase_map
                    if p["verdict_tier_per_point"] in ("HARD_PASS", "MIDDLE_BAND"))
    arms_all_differ = all(
        arms_differ_per_fam[f]["differ"] for f in REFUSE_FAMILIES)
    family_hashes_distinct = (len(set(family_mech_hashes.values()))
                              == len(REFUSE_FAMILIES))

    # Cell verdict gates (per pre-reg)
    pass_threshold = 15 if not is_smoke else 1
    pair_threshold = 2 if not is_smoke else 1
    smoke_saturation_check = True
    if is_smoke:
        n_all_sat = sum(1 for p in phase_map
                        if p["verdict_tier_per_point"] == "SATURATED")
        if n_all_sat == observed_n_units and observed_n_units > 0:
            smoke_saturation_check = False  # all saturated -> can't discriminate

    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_CARDINALITY_BREACH: observed={observed_n_units} "
                       f"expected={expected_n_units}")
    elif not arms_all_differ:
        verdict = "HARD_FAIL"
        broken = [f for f in REFUSE_FAMILIES
                  if not arms_differ_per_fam[f]["differ"]]
        verdict_msg = f"HARD_FAIL_ARMS_IDENTICAL: families {broken} match random_floor"
    elif not ctrl_ok:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_CONTROL_FAIL: fixed_threshold@"
                       f"{control['regime']}@cal={control['cal_size']} "
                       f"refuse_rate={ctrl_refuse:.3f} < "
                       f"{control['refuse_rate_floor']}")
    elif is_smoke and not smoke_saturation_check:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_SMOKE_DISCRIMINATOR_FAILS_SCALE: all "
                       f"{observed_n_units} pts SATURATED at smoke N={N}")
    elif is_smoke and len(set(family_mech_hashes.values())) < 2:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL_SMOKE_FAMILY_COLLAPSE: only "
                       f"{len(set(family_mech_hashes.values()))}/4 distinct hashes "
                       f"-- all families identical at smoke scale")
    elif n_pairs_differ < pair_threshold:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND_NULL_FAMILY_INVARIANCE: only "
                       f"{n_pairs_differ}/6 family pairs differ "
                       f"(threshold {pair_threshold}); H4 null support")
    elif n_passing < pass_threshold:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND_ADAPTIVITY_DIFFERS_BUT_LOW_DISC: "
                       f"{n_passing}/{observed_n_units} HARD_PASS+MIDDLE_BAND "
                       f"< threshold {pass_threshold}; family pairs differ "
                       f"({n_pairs_differ}/6)")
    else:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS_ADAPTIVITY_DISCRIMINATION: "
                       f"{n_passing}/{observed_n_units} pts in HARD_PASS+MB; "
                       f"{n_pairs_differ}/6 family pairs differ; control "
                       f"refuse_rate={ctrl_refuse:.3f} >= "
                       f"{control['refuse_rate_floor']}")

    return {
        "seed": seed,
        "N": N,
        "V_C_per_cat": V_C_per_cat,
        "V_REL": V_REL_FIXED,
        "n_queries_per_regime": n_queries_per_regime,
        "elapsed_phase_sweep_s": round(elapsed, 2),
        "observed_n_units": observed_n_units,
        "expected_n_units": expected_n_units,
        "cardinality_ok": cardinality_ok,
        "phase_map": phase_map,
        "per_family_summary": per_family_summary,
        "family_tiers": family_tiers,
        "family_pair_distinctness": pairs_differ,
        "n_family_pairs_differ": n_pairs_differ,
        "family_mech_hashes": family_mech_hashes,
        "arms_differ_per_family": arms_differ_per_fam,
        "positive_control_check": {
            "expected": control,
            "observed_refuse_rate": ctrl_refuse,
            "passed": ctrl_ok,
        },
        "n_passing_points": n_passing,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
    }


# ---------------------------------------------------------------------------
# Aggregate across seeds
# ---------------------------------------------------------------------------
def aggregate_and_verdict(per_seed: Dict[str, Any], run_mode: str
                           ) -> Dict[str, Any]:
    """Per-seed result aggregator (used by sibling cell at chunked end).

    Since each sibling cell only runs ONE seed, this is largely a passthrough;
    cross-seed aggregation happens later by the orchestrator combining
    sibling outputs. This function preserves the contract.
    """
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per_seed payloads",
            "summary": "no per_seed payloads",
        }
    # Take the single seed result (chunked-per-seed convention)
    keys = sorted(per_seed.keys())
    seed_result = per_seed[keys[0]]
    out = dict(seed_result)
    out["seeds_observed"] = keys
    out["n_seeds"] = len(keys)
    return out
