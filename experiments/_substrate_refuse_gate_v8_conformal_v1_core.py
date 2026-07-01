"""Shared core for substrate_refuse_gate_v8_conformal_v1 sibling cells.

v8 SURGICAL FIX from v7 (commit family; see preregs/2026-07-01_refuse_gate_v7_conformal_v1.md):

  Root cause diagnosed by 2x-drill (2026-07-01): in-KB max_sim at N=8192 bipolar
  is a POINT MASS by LLN concentration of measure. All quantiles (P5, P10, P25, P50)
  of a single-regime cal collapse to the same tau (v7 empirical:
  P5=P10=P25=P50=0.699951 bit-identical). Widening alpha on same source is degenerate.

  V8 SURGICAL FIX: vary the cal SOURCE (regime), not alpha on same source.

Change ONE function (arm_tau) — everything else stays from v7:

  ARM_FIXED_BASELINE:       tau = 0.40 (unchanged; positive control)
  ARM_CONFORMAL_CLEAN:      tau = conformal_tau(cal_per_regime["clean"]["sims_in_kb"], alpha=0.05)
                              -> analytical ~1.000 (point mass at 1 - 2*0.00)
  ARM_CONFORMAL_MODERATE:   tau = conformal_tau(cal_per_regime["moderate"]["sims_in_kb"], alpha=0.05)
                              -> analytical ~0.700 (point mass at 1 - 2*0.15)
  ARM_CONFORMAL_MID:        tau = regime_mid_tau(moderate in_kb + moderate ood)
                              -> analytical ~0.367 (midpoint P10_in_kb + P90_ood)

Also compute cal PER REGIME (v7 only did per-regime for CONFORMAL_REGIME_MID;
v8 needs it for CLEAN + MODERATE arms too). Add
  cal_per_regime = {regime: build_cal(regime) for regime in REGIMES}
at cell startup.

Analytical predictions (from 2x-drill):

  Arm                        tau       Decision seq (9 pts)
  ARM_FIXED_BASELINE         0.400     [1,1,0, 1,1,0, 0,0,0]
  ARM_CONFORMAL_CLEAN        ~1.000    [0,0,0, 0,0,0, 0,0,0]
  ARM_CONFORMAL_MODERATE     ~0.700    [1,1,0, 0,0,0, 0,0,0]
  ARM_CONFORMAL_MID          ~0.367    [1,1,0, 1,1,0, 1,1,0]

  All 4 distinct -> cardinality gate PASS.

Float32 boundary: tau_moderate = 0.699951, all borderline sims at moderate = 0.699951.
Strict `>` means `0.699951 > 0.699951 == False` -> REFUSE. Correct behavior verified in drill.

NEW pre-reg gate (HARD_FAIL_CAL_SOURCE_NOT_DISTINCT):
  tau(ARM_CONFORMAL_CLEAN) <= tau(ARM_CONFORMAL_MODERATE) fires HARD_FAIL early;
  catches cal construction bugs at cell-startup.

Cross-references:
- v6 commit 96525dc9 (first cardinality gate HF; d'=5.1 confirmed at smoke)
- v7 smoke (root cause diagnostic at data/exp_substrate_refuse_gate_v7_conformal_v1_seed_7/metrics.json)
- 2x-drill research 2026-07-01 (analytical basis; LLN point-mass)
- First research drill (mechanism-class ranking; notes/research_drill_M1_4_refuse_gate_conformal_mechanism_class_2026-07-01.md)
- refuse_gate_V_REL_sweep_v1 CG (empirical d' basis)
- cortex_hippo_dense_M_sweep_v3 CG (M3 architecture context)

Cardinality: 4 arms x 3 regimes x 3 bands x 3 seeds = 108 units full (36 per seed);
             smoke 36 per seed at N=8192 same as full (CheckA discriminator survives scale).

CHUNKED single-seed-per-cell. Seeds 7, 13, 19 as siblings.

PRE-REG: preregs/2026-07-01_refuse_gate_v8_conformal_v1.md

Disciplines preserved from v7:
- CARDINALITY_OK pre-reg field (expected_n_units + hard_fail_cardinality_breach)
- DISCRIMINATOR_SURVIVES_SCALE: smoke at full-N=8192 (numpy CPU-cheap)
- No silent except: blocks
- Smoke fires discriminator (not just verify cell runs)
- Broken-PC-before-structural-framing gate
- Atomic metrics writes (META_RULE_AH)
- Arms-must-differ (mechanism_hash + decision_hash) (META_RULE_AF)

ASCII-only. numpy-only (no torch). CPU-native.
Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn).
"""
from __future__ import annotations

import hashlib
import json
import math
import time
from typing import Any, Dict, List, Tuple

import numpy as np


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------

# FIXED baseline tau (v2 CG reproducer; positive control)
FIXED_TAU = 0.40

# Conformal alpha level (v8 uses SAME alpha across CLEAN + MODERATE arms;
# variation comes from CAL SOURCE not alpha)
CONFORMAL_ALPHA = 0.05
# For CONFORMAL_MID: midpoint between in-KB P10 and OOD P90 at moderate regime
REGIME_MID_IN_KB_ALPHA = 0.10
REGIME_MID_OOD_ALPHA = 0.90

# Arms (LOCKED; v8 renamed from v7 to reflect cal-source variation)
CONFORMAL_ARMS = (
    "ARM_FIXED_BASELINE",
    "ARM_CONFORMAL_CLEAN",
    "ARM_CONFORMAL_MODERATE",
    "ARM_CONFORMAL_MID",
)

# Query regimes (noise flip-frac; LOCKED)
REGIMES = ("clean", "moderate", "heavy")
REGIME_FLIP_FRAC = {"clean": 0.00, "moderate": 0.15, "heavy": 0.30}

# Query bands (LOCKED)
BANDS = ("in_kb", "borderline", "ood")

# Calibration set size (v7 sizes preserved: 100 items per regime)
CAL_SIZE_IN_KB = 50
CAL_SIZE_OOD = 50
CAL_SIZE_TOTAL = CAL_SIZE_IN_KB + CAL_SIZE_OOD

# Substrate scale (SMOKE == FULL for CheckA DISCRIMINATOR-SURVIVES-SCALE)
N_FULL = 8192
N_SMOKE = 8192
V_C_PER_CAT_FULL = 200
V_C_PER_CAT_SMOKE = 200
V_REL_FIXED = 256
IN_DOMAIN_CATEGORIES = ("animals", "geography", "tools")
OUT_DOMAIN_CATEGORIES = ("medical", "legal", "financial")
N_IN_CAT = len(IN_DOMAIN_CATEGORIES)
N_OUT_CAT = len(OUT_DOMAIN_CATEGORIES)

# Query counts per (arm, regime, band) point
N_QUERIES_PER_UNIT_FULL = 60
N_QUERIES_PER_UNIT_SMOKE = 20

# Cardinality (LOCKED; META_RULE_H)
EXPECTED_N_UNITS_FULL = (len(CONFORMAL_ARMS) * len(REGIMES) * len(BANDS))  # 4*3*3=36
EXPECTED_N_UNITS_SMOKE = EXPECTED_N_UNITS_FULL  # same phase-space
EXPECTED_N_RECORDS_FULL = EXPECTED_N_UNITS_FULL * N_QUERIES_PER_UNIT_FULL  # 2160
EXPECTED_N_RECORDS_SMOKE = EXPECTED_N_UNITS_SMOKE * N_QUERIES_PER_UNIT_SMOKE  # 720

# Positive control: FIXED_BASELINE at clean+ood must refuse >= 0.85
POSITIVE_CONTROL = {
    "arm": "ARM_FIXED_BASELINE",
    "regime": "clean",
    "band": "ood",
    "refuse_rate_floor": 0.85,
}
POSITIVE_CONTROL_SMOKE = {
    "arm": "ARM_FIXED_BASELINE",
    "regime": "clean",
    "band": "ood",
    "refuse_rate_floor": 0.85,
}

# HP gate (unchanged from v7): (moderate, borderline) where FIXED is broken
HP_REFUSE_PRECISION_FLOOR = 0.85
HP_REGIME = "moderate"
HP_BAND = "borderline"

# HP-3 gate: cal-source distinctness — tau(CLEAN) STRICTLY > tau(MODERATE)
# because clean cal has point-mass at ~1.000 while moderate has point-mass ~0.700
HP_CAL_SOURCE_MIN_DELTA = 0.10  # analytical predicts ~0.300

# HARD_FAIL_REGIME_COLLAPSE: cal-set refuse_spread P50_in - P50_ood ~ 0
HF_REGIME_COLLAPSE_THRESHOLD = 1e-6

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def noise_floor_prediction(N: int, V_C: int) -> float:
    """Out-of-domain similarity noise floor sqrt(2 ln V / N)."""
    if N <= 0 or V_C <= 1:
        return 0.0
    return math.sqrt(2.0 * math.log(V_C) / N)


def get_backend_label() -> str:
    return "numpy.cpu"


# ---------------------------------------------------------------------------
# Substrate construction
# ---------------------------------------------------------------------------

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_substrate(g: np.random.Generator, N: int, V_C_per_cat: int,
                    V_REL: int) -> Dict[str, Any]:
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
    n = vec.shape[0]
    n_flip = int(round(n * flip_frac))
    if n_flip <= 0:
        return vec / (np.linalg.norm(vec) + 1e-8)
    flip_idxs = g.choice(n, size=n_flip, replace=False)
    v = vec.copy()
    v[flip_idxs] *= -1.0
    return v / (np.linalg.norm(v) + 1e-8)


# ---------------------------------------------------------------------------
# Calibration set (100 items = 50 in-KB + 50 OOD; loaded once at cell startup)
# ---------------------------------------------------------------------------

def build_calibration_set(g: np.random.Generator, substrate: Dict[str, Any],
                          flip_frac: float,
                          n_in_kb: int = CAL_SIZE_IN_KB,
                          n_ood: int = CAL_SIZE_OOD
                          ) -> Dict[str, np.ndarray]:
    """Build calibration set: n_in_kb known-in-KB items + n_ood known-OOD items.

    Returns dict with:
      sims_in_kb: max_sim scores for in-KB items (length n_in_kb)
      sims_ood:   max_sim scores for OOD items (length n_ood)
    """
    W_sub_in = substrate["W_subjects_in"]
    V_C_IN = substrate["V_C_IN"]
    V_C_OUT = substrate["V_C_OUT"]
    out_sub = substrate["out_subject_atoms"]

    sims_in: List[float] = []
    for _ in range(n_in_kb):
        s_i = int(g.integers(0, V_C_IN))
        v = add_noise(W_sub_in[s_i], flip_frac, g)
        sims_in.append(float(np.max(W_sub_in @ v)))

    sims_ood: List[float] = []
    for _ in range(n_ood):
        s_i = int(g.integers(0, V_C_OUT))
        v = add_noise(out_sub[s_i], flip_frac, g)
        sims_ood.append(float(np.max(W_sub_in @ v)))

    return {
        "sims_in_kb": np.array(sims_in, dtype=np.float32),
        "sims_ood": np.array(sims_ood, dtype=np.float32),
    }


def conformal_tau(cal_sims_in_kb: np.ndarray, alpha: float) -> float:
    """Compute conformal tau = alpha-quantile of cal-set in-KB max_sim scores."""
    if cal_sims_in_kb.size == 0:
        return FIXED_TAU
    q = float(np.percentile(cal_sims_in_kb.astype(np.float64), alpha * 100.0))
    return q


def regime_mid_tau(cal_sims_in_kb: np.ndarray,
                    cal_sims_ood: np.ndarray) -> float:
    """v7 Option C: midpoint between in-KB P10 and OOD P90.

    Rationale: if in-KB cluster is [P10_in, ...] and OOD cluster is [..., P90_ood],
    the midpoint sits BETWEEN the two clusters (assuming separated distributions,
    which v6 empirically confirmed at spread=0.667). Bridges the two.
    """
    if cal_sims_in_kb.size == 0 or cal_sims_ood.size == 0:
        return FIXED_TAU
    p10_in = float(np.percentile(cal_sims_in_kb.astype(np.float64),
                                   REGIME_MID_IN_KB_ALPHA * 100.0))
    p90_ood = float(np.percentile(cal_sims_ood.astype(np.float64),
                                    REGIME_MID_OOD_ALPHA * 100.0))
    return 0.5 * (p10_in + p90_ood)


# ---------------------------------------------------------------------------
# Query corpus per (regime, band)
# ---------------------------------------------------------------------------

def build_queries(g: np.random.Generator, substrate: Dict[str, Any],
                  regime: str, band: str,
                  n_queries: int) -> List[Dict[str, Any]]:
    """Build n_queries queries at (regime, band)."""
    if regime not in REGIME_FLIP_FRAC:
        raise ValueError("unknown regime: " + regime)
    if band not in BANDS:
        raise ValueError("unknown band: " + band)

    flip_frac = REGIME_FLIP_FRAC[regime]
    W_sub_in = substrate["W_subjects_in"]
    W_rel_in = substrate["W_relations_in"]
    out_sub = substrate["out_subject_atoms"]
    out_rel = substrate["out_relation_atoms"]
    V_C_IN = substrate["V_C_IN"]
    V_C_OUT = substrate["V_C_OUT"]
    V_REL = substrate["V_REL"]

    qs: List[Dict[str, Any]] = []
    for _ in range(n_queries):
        if band == "in_kb":
            s_i = int(g.integers(0, V_C_IN))
            r_i = int(g.integers(0, V_REL))
            qs.append({
                "subject_vec": add_noise(W_sub_in[s_i], flip_frac, g),
                "relation_vec": add_noise(W_rel_in[r_i], flip_frac, g),
                "is_in_kb": True,
                "should_refuse": False,
            })
        elif band == "borderline":
            s_i = int(g.integers(0, V_C_IN))
            r_i = int(g.integers(0, V_REL))
            qs.append({
                "subject_vec": add_noise(W_sub_in[s_i], flip_frac, g),
                "relation_vec": add_noise(out_rel[r_i], flip_frac, g),
                "is_in_kb": False,
                "should_refuse": True,
            })
        elif band == "ood":
            s_i = int(g.integers(0, V_C_OUT))
            r_i = int(g.integers(0, V_REL))
            qs.append({
                "subject_vec": add_noise(out_sub[s_i], flip_frac, g),
                "relation_vec": add_noise(out_rel[r_i], flip_frac, g),
                "is_in_kb": False,
                "should_refuse": True,
            })
    return qs


def query_max_sim(q: Dict[str, Any], W_in: np.ndarray) -> float:
    sims = W_in @ q["subject_vec"]
    return float(np.max(sims))


# ---------------------------------------------------------------------------
# Arm tau computation (v8 SURGICAL CHANGE — vary cal SOURCE, not alpha)
# ---------------------------------------------------------------------------

def arm_tau(arm: str, regime: str,
            cal_per_regime: Dict[str, Dict[str, np.ndarray]]) -> float:
    """Compute static tau for arm.

    v8 change from v7: all CONFORMAL arms use same alpha=0.05 but vary CAL SOURCE.
    Regime dimension of the query does NOT affect tau (tau is fixed at cell startup
    per arm-choice-of-cal-source); the regime dimension only affects the QUERY
    distribution.

    ARM_FIXED_BASELINE:      tau = 0.40 (v2 CG reproducer)
    ARM_CONFORMAL_CLEAN:     tau = P5 of clean cal in-KB    (analytical ~1.000)
    ARM_CONFORMAL_MODERATE:  tau = P5 of moderate cal in-KB (analytical ~0.700)
    ARM_CONFORMAL_MID:       tau = midpoint(P10_in_kb, P90_ood) of MODERATE cal
                                     (analytical ~0.367)
    """
    if arm == "ARM_FIXED_BASELINE":
        return FIXED_TAU
    if arm == "ARM_CONFORMAL_CLEAN":
        return conformal_tau(cal_per_regime["clean"]["sims_in_kb"],
                             CONFORMAL_ALPHA)
    if arm == "ARM_CONFORMAL_MODERATE":
        return conformal_tau(cal_per_regime["moderate"]["sims_in_kb"],
                             CONFORMAL_ALPHA)
    if arm == "ARM_CONFORMAL_MID":
        cal = cal_per_regime["moderate"]
        return regime_mid_tau(cal["sims_in_kb"], cal["sims_ood"])
    raise ValueError("unknown arm: " + arm)


def mechanism_hash(arm: str) -> str:
    """SHA-256 of arm's mechanism descriptor; used for arm-distinct check."""
    if arm == "ARM_FIXED_BASELINE":
        m = "fixed_threshold:tau=%.4f" % FIXED_TAU
    elif arm == "ARM_CONFORMAL_CLEAN":
        m = ("conformal_split:cal_source=clean,cal_size=%d,alpha=%.4f,"
             "quantile_source=in_kb_max_sim"
             % (CAL_SIZE_TOTAL, CONFORMAL_ALPHA))
    elif arm == "ARM_CONFORMAL_MODERATE":
        m = ("conformal_split:cal_source=moderate,cal_size=%d,alpha=%.4f,"
             "quantile_source=in_kb_max_sim"
             % (CAL_SIZE_TOTAL, CONFORMAL_ALPHA))
    elif arm == "ARM_CONFORMAL_MID":
        m = ("conformal_midpoint:cal_source=moderate,"
             "cal_size=%d,in_kb_alpha=%.4f,ood_alpha=%.4f,"
             "quantile_source=midpoint_of_in_kb_P10_and_ood_P90"
             % (CAL_SIZE_TOTAL, REGIME_MID_IN_KB_ALPHA, REGIME_MID_OOD_ALPHA))
    else:
        raise ValueError("unknown arm: " + arm)
    return hashlib.sha256(m.encode("ascii")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Per-phase-point evaluation
# ---------------------------------------------------------------------------

def eval_phase_point(arm: str, regime: str, band: str,
                     substrate: Dict[str, Any],
                     queries: List[Dict[str, Any]],
                     sims: List[float],
                     tau: float) -> Dict[str, Any]:
    """Run one (arm, regime, band) phase point given prebuilt queries/sims + tau."""
    if arm not in CONFORMAL_ARMS:
        raise ValueError("unknown arm: " + arm)
    if regime not in REGIMES:
        raise ValueError("unknown regime: " + regime)
    if band not in BANDS:
        raise ValueError("unknown band: " + band)

    t0 = time.time()
    n_queries = len(queries)

    accept_log = np.zeros(n_queries, dtype=np.bool_)
    is_in_kb_log = np.zeros(n_queries, dtype=np.bool_)
    false_refuse_log = np.zeros(n_queries, dtype=np.bool_)
    false_accept_log = np.zeros(n_queries, dtype=np.bool_)

    for i in range(n_queries):
        confidence_t = float(sims[i])
        accept_t = bool(confidence_t > tau)
        is_in_kb_t = bool(queries[i]["is_in_kb"])
        false_refuse_t = is_in_kb_t and (not accept_t)
        false_accept_t = (not is_in_kb_t) and accept_t

        accept_log[i] = accept_t
        is_in_kb_log[i] = is_in_kb_t
        false_refuse_log[i] = false_refuse_t
        false_accept_log[i] = false_accept_t

    n_in_kb = int(np.sum(is_in_kb_log))
    n_out_kb = n_queries - n_in_kb
    false_refuse_rate = (float(np.sum(false_refuse_log)) / max(n_in_kb, 1)
                         if n_in_kb > 0 else 0.0)
    false_accept_rate = (float(np.sum(false_accept_log)) / max(n_out_kb, 1)
                         if n_out_kb > 0 else 0.0)
    in_kb_accept_rate = (1.0 - false_refuse_rate) if n_in_kb > 0 else 1.0
    out_kb_refuse_rate = (1.0 - false_accept_rate) if n_out_kb > 0 else 1.0
    refuse_rate_overall = float(np.sum(~accept_log)) / n_queries
    refused_mask = ~accept_log
    correct_refuse_mask = refused_mask & (~is_in_kb_log)
    n_refused = int(np.sum(refused_mask))
    n_refused_correctly = int(np.sum(correct_refuse_mask))
    refuse_precision = (n_refused_correctly / max(n_refused, 1)
                        if n_refused > 0 else 0.0)

    payload = json.dumps([int(a) for a in accept_log]).encode("utf-8")
    decision_hash = hashlib.sha256(payload).hexdigest()[:16]

    elapsed = time.time() - t0

    return {
        "arm": arm,
        "regime": regime,
        "band": band,
        "tau": round(float(tau), 6),
        "n_queries": n_queries,
        "n_in_kb": n_in_kb,
        "n_out_kb": n_out_kb,
        "false_refuse_rate": round(false_refuse_rate, 4),
        "false_accept_rate": round(false_accept_rate, 4),
        "in_kb_accept_rate": round(in_kb_accept_rate, 4),
        "out_kb_refuse_rate": round(out_kb_refuse_rate, 4),
        "refuse_rate_overall": round(refuse_rate_overall, 4),
        "refuse_precision": round(refuse_precision, 4),
        "decision_hash": decision_hash,
        "mechanism_hash": mechanism_hash(arm),
        "elapsed_s_point": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def selftest(seed: int) -> Tuple[bool, str]:
    """Cheap selftest verifying:
    (a) cardinality math (36 units per seed; 4 arms x 3 regimes x 3 bands)
    (b) noise-floor formula sanity
    (c) mechanism_hash distinct across 4 arms (META_RULE_AF)
    (d) synthetic cal-source-distinctness: tau(CLEAN cal) > tau(MODERATE cal)
        on synthetic bipolar substrate at small N
    (e) FIXED baseline at small substrate refuses OOD > 0.50 (positive-control seed)
    """
    msgs: List[str] = []

    # 1. cardinality math
    if EXPECTED_N_UNITS_FULL != 36:
        return False, "FULL cardinality %d != 36" % EXPECTED_N_UNITS_FULL
    if EXPECTED_N_UNITS_SMOKE != 36:
        return False, "SMOKE cardinality %d != 36" % EXPECTED_N_UNITS_SMOKE
    if EXPECTED_N_RECORDS_FULL != 2160:
        return False, "FULL records %d != 2160" % EXPECTED_N_RECORDS_FULL
    if EXPECTED_N_RECORDS_SMOKE != 720:
        return False, "SMOKE records %d != 720" % EXPECTED_N_RECORDS_SMOKE
    msgs.append("cardinality FULL_units=%d records=%d SMOKE_units=%d records=%d"
                % (EXPECTED_N_UNITS_FULL, EXPECTED_N_RECORDS_FULL,
                   EXPECTED_N_UNITS_SMOKE, EXPECTED_N_RECORDS_SMOKE))

    # 2. noise-floor sanity
    nf_full = noise_floor_prediction(N_FULL, V_C_PER_CAT_FULL * N_IN_CAT)
    if not (0.02 < nf_full < 0.10):
        return False, "noise_floor N=8192 V_C=600 outside (0.02, 0.10): %.4f" % nf_full
    msgs.append("noise_floor FULL=%.4f (pred sqrt(2*ln(600)/8192))" % nf_full)

    # 3. mechanism_hash distinctness across 4 arms
    mech_hashes = set(mechanism_hash(a) for a in CONFORMAL_ARMS)
    if len(mech_hashes) != len(CONFORMAL_ARMS):
        return False, ("mechanism_hash NOT_DISTINCT: %d hashes across %d arms"
                       % (len(mech_hashes), len(CONFORMAL_ARMS)))
    msgs.append("mechanism_hash: %d/%d distinct" % (len(mech_hashes),
                                                     len(CONFORMAL_ARMS)))

    # 4. cal-source-distinctness on real small substrate:
    #    build clean cal + moderate cal from same substrate; tau_clean > tau_moderate
    g_sub = np.random.default_rng(seed)
    substrate = build_substrate(g_sub, N=1024, V_C_per_cat=20, V_REL=32)
    cal_g = np.random.default_rng(seed * 10007 + 31)
    cal_clean = build_calibration_set(cal_g, substrate,
                                       REGIME_FLIP_FRAC["clean"])
    cal_moderate = build_calibration_set(cal_g, substrate,
                                          REGIME_FLIP_FRAC["moderate"])
    tau_clean = conformal_tau(cal_clean["sims_in_kb"], CONFORMAL_ALPHA)
    tau_moderate = conformal_tau(cal_moderate["sims_in_kb"], CONFORMAL_ALPHA)
    delta = tau_clean - tau_moderate
    if not (tau_clean > tau_moderate):
        return False, ("cal-source-distinctness FAIL: tau_clean=%.4f <= "
                       "tau_moderate=%.4f (v8 mechanism broken)"
                       % (tau_clean, tau_moderate))
    if delta < HP_CAL_SOURCE_MIN_DELTA:
        return False, ("cal-source-delta=%.4f < floor %.4f "
                       "(distinct but too tight; verify at full N=8192)"
                       % (delta, HP_CAL_SOURCE_MIN_DELTA))
    msgs.append("cal-source-distinctness tau_clean=%.4f tau_moderate=%.4f "
                "delta=%.4f (>=%.4f floor)"
                % (tau_clean, tau_moderate, delta, HP_CAL_SOURCE_MIN_DELTA))

    # 5. Small substrate FIXED @ ood positive-control seed check
    q_g = np.random.default_rng(seed * 10 + 7)
    ood_queries = build_queries(q_g, substrate, "clean", "ood", 30)
    ood_sims = [query_max_sim(q, substrate["W_subjects_in"])
                for q in ood_queries]
    ood_refuse = sum(1 for s in ood_sims if s <= FIXED_TAU) / len(ood_sims)
    if ood_refuse < 0.50:
        return False, ("FIXED @ clean+ood refuse=%.3f < 0.50 "
                       "(positive-control seed failed at small substrate)"
                       % ood_refuse)
    msgs.append("FIXED @ small_substrate clean+ood refuse=%.3f" % ood_refuse)

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------

def run_one_seed_conformal(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (arm, regime, band) phase points for one seed."""
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        N = N_SMOKE
        V_C_per_cat = V_C_PER_CAT_SMOKE
        n_queries_per_unit = N_QUERIES_PER_UNIT_SMOKE
    else:
        N = N_FULL
        V_C_per_cat = V_C_PER_CAT_FULL
        n_queries_per_unit = N_QUERIES_PER_UNIT_FULL

    expected_n_units = len(CONFORMAL_ARMS) * len(REGIMES) * len(BANDS)
    expected_n_records = expected_n_units * n_queries_per_unit

    print("[run_one_seed] seed=%d mode=%s N=%d V_C_per_cat=%d V_REL=%d "
          "arms=%s regimes=%s bands=%s n_q=%d expected_units=%d "
          "expected_records=%d cal_size_per_regime=%d(in=%d,ood=%d)"
          % (seed, run_mode, N, V_C_per_cat, V_REL_FIXED, CONFORMAL_ARMS,
             REGIMES, BANDS, n_queries_per_unit,
             expected_n_units, expected_n_records,
             CAL_SIZE_TOTAL, CAL_SIZE_IN_KB, CAL_SIZE_OOD), flush=True)

    nf_pred = noise_floor_prediction(N, V_C_per_cat * N_IN_CAT)
    print("[noise_floor] V_REL=%d N=%d V_C=%d: nf=%.4f"
          % (V_REL_FIXED, N, V_C_per_cat * N_IN_CAT, nf_pred), flush=True)

    g_sub = np.random.default_rng(seed)
    substrate = build_substrate(g_sub, N=N, V_C_per_cat=V_C_per_cat,
                                 V_REL=V_REL_FIXED)

    # v8: build cal PER REGIME (all 3 regimes; needed for CLEAN + MODERATE arms
    # AND for CONFORMAL_MID's moderate midpoint)
    cal_per_regime: Dict[str, Dict[str, np.ndarray]] = {}
    for regime in REGIMES:
        cal_reg_g = np.random.default_rng(seed * 10007 + hash(regime) % 9973 + 41)
        cal_per_regime[regime] = build_calibration_set(cal_reg_g, substrate,
                                                       REGIME_FLIP_FRAC[regime])

    # Diagnostic: cal-source distinctness
    cal_clean_p5_in = float(np.percentile(cal_per_regime["clean"]["sims_in_kb"], 5))
    cal_moderate_p5_in = float(np.percentile(cal_per_regime["moderate"]["sims_in_kb"], 5))
    cal_heavy_p5_in = float(np.percentile(cal_per_regime["heavy"]["sims_in_kb"], 5))
    cal_moderate_p10_in = float(np.percentile(cal_per_regime["moderate"]["sims_in_kb"], 10))
    cal_moderate_p50_in = float(np.percentile(cal_per_regime["moderate"]["sims_in_kb"], 50))
    cal_moderate_p90_ood = float(np.percentile(cal_per_regime["moderate"]["sims_ood"], 90))
    cal_moderate_p50_ood = float(np.percentile(cal_per_regime["moderate"]["sims_ood"], 50))
    cal_moderate_refuse_spread = cal_moderate_p50_in - cal_moderate_p50_ood
    cal_source_delta = cal_clean_p5_in - cal_moderate_p5_in
    print("[cal_diag] tau_clean_P5=%.4f tau_moderate_P5=%.4f tau_heavy_P5=%.4f "
          "delta_clean_minus_moderate=%.4f moderate_P10_in=%.4f moderate_P50_in=%.4f "
          "moderate_P50_ood=%.4f moderate_P90_ood=%.4f moderate_refuse_spread=%.4f"
          % (cal_clean_p5_in, cal_moderate_p5_in, cal_heavy_p5_in,
             cal_source_delta, cal_moderate_p10_in, cal_moderate_p50_in,
             cal_moderate_p50_ood, cal_moderate_p90_ood,
             cal_moderate_refuse_spread), flush=True)

    # HARD_FAIL_REGIME_COLLAPSE early detection
    if cal_moderate_refuse_spread < HF_REGIME_COLLAPSE_THRESHOLD:
        return {
            "seed": seed,
            "verdict": "HARD_FAIL",
            "verdict_msg": ("HARD_FAIL_REGIME_COLLAPSE: cal_moderate refuse_spread"
                            "=%.6f < %.6f (in-KB and OOD cal-set distributions"
                            " overlap; falsifies d'=5.1 analytical prediction)"
                            % (cal_moderate_refuse_spread, HF_REGIME_COLLAPSE_THRESHOLD)),
            "summary": "HARD_FAIL_REGIME_COLLAPSE",
            "cal_moderate_refuse_spread": cal_moderate_refuse_spread,
        }

    # v8 NEW: HARD_FAIL_CAL_SOURCE_NOT_DISTINCT early detection
    # tau(CLEAN) must be strictly > tau(MODERATE); analytical predicts ~0.300 delta
    if cal_source_delta <= 0.0:
        return {
            "seed": seed,
            "verdict": "HARD_FAIL",
            "verdict_msg": ("HARD_FAIL_CAL_SOURCE_NOT_DISTINCT: tau_clean_P5=%.4f"
                            " <= tau_moderate_P5=%.4f delta=%.4f (v8 mechanism"
                            " broken -- clean cal should give higher tau than"
                            " noise-corrupted cal by ~0.3 analytically)"
                            % (cal_clean_p5_in, cal_moderate_p5_in,
                               cal_source_delta)),
            "summary": "HARD_FAIL_CAL_SOURCE_NOT_DISTINCT",
            "cal_source_delta": cal_source_delta,
        }

    # Build queries once per (regime, band); all 4 arms see SAME query stream
    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    total_records = 0
    for regime in REGIMES:
        for band in BANDS:
            sub_seed = (seed * 100003 + hash(regime) % 9973 * 7
                        + hash(band) % 9973 * 11)
            q_g = np.random.default_rng(sub_seed)
            queries = build_queries(q_g, substrate, regime, band,
                                    n_queries_per_unit)
            sims = [query_max_sim(q, substrate["W_subjects_in"]) for q in queries]

            for arm in CONFORMAL_ARMS:
                tau = arm_tau(arm, regime, cal_per_regime)
                print("[point] seed=%d arm=%s regime=%s band=%s tau=%.4f ..."
                      % (seed, arm, regime, band, tau), flush=True)
                pt = eval_phase_point(arm, regime, band, substrate,
                                      queries, sims, tau)
                pt["seed"] = seed
                phase_map.append(pt)
                total_records += n_queries_per_unit
                print("  -> false_refuse=%.3f false_accept=%.3f "
                      "refuse_prec=%.3f in_kb_acc=%.3f out_kb_ref=%.3f t=%.2fs"
                      % (pt["false_refuse_rate"], pt["false_accept_rate"],
                         pt["refuse_precision"], pt["in_kb_accept_rate"],
                         pt["out_kb_refuse_rate"], pt["elapsed_s_point"]),
                      flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units
                      and total_records == expected_n_records)

    # Per-arm summary
    per_arm_summary: Dict[str, Dict[str, Any]] = {}
    arm_decision_hashes: Dict[str, str] = {}
    arm_mechanism_hashes: Dict[str, str] = {}
    for arm in CONFORMAL_ARMS:
        arm_pts = [p for p in phase_map if p["arm"] == arm]
        if not arm_pts:
            continue
        fr_mean = float(np.mean([p["false_refuse_rate"] for p in arm_pts]))
        fa_mean = float(np.mean([p["false_accept_rate"] for p in arm_pts]))
        rp_mean = float(np.mean([p["refuse_precision"] for p in arm_pts]))
        ik_mean = float(np.mean([p["in_kb_accept_rate"] for p in arm_pts]))
        ok_mean = float(np.mean([p["out_kb_refuse_rate"] for p in arm_pts]))
        agg_payload = json.dumps([p["decision_hash"] for p in arm_pts],
                                  sort_keys=True).encode("utf-8")
        arm_decision_hashes[arm] = hashlib.sha256(agg_payload).hexdigest()[:16]
        arm_mechanism_hashes[arm] = arm_pts[0]["mechanism_hash"]
        per_arm_summary[arm] = {
            "false_refuse_rate_mean": round(fr_mean, 4),
            "false_accept_rate_mean": round(fa_mean, 4),
            "refuse_precision_mean": round(rp_mean, 4),
            "in_kb_accept_rate_mean": round(ik_mean, 4),
            "out_kb_refuse_rate_mean": round(ok_mean, 4),
            "n_points": len(arm_pts),
        }

    n_distinct_mech = len(set(arm_mechanism_hashes.values()))
    n_distinct_decision = len(set(arm_decision_hashes.values()))
    arms_mech_distinct = (n_distinct_mech == len(CONFORMAL_ARMS))
    arms_decision_distinct = (n_distinct_decision == len(CONFORMAL_ARMS))

    # Positive control
    control = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    ctrl_pts = [p for p in phase_map
                if p["arm"] == control["arm"]
                and p["regime"] == control["regime"]
                and p["band"] == control["band"]]
    ctrl_refuse = (ctrl_pts[0].get("out_kb_refuse_rate", 0.0)
                   if ctrl_pts else -1.0)
    ctrl_ok = (ctrl_refuse >= control["refuse_rate_floor"])

    # HP gate: any CONFORMAL arm refuse_precision >= 0.85 at (moderate, borderline)
    hp_pts_by_arm: Dict[str, float] = {}
    fixed_hp_refuse_prec = None
    for arm in CONFORMAL_ARMS:
        matching = [p for p in phase_map
                    if p["arm"] == arm
                    and p["regime"] == HP_REGIME
                    and p["band"] == HP_BAND]
        if matching:
            rp = matching[0]["refuse_precision"]
            hp_pts_by_arm[arm] = rp
            if arm == "ARM_FIXED_BASELINE":
                fixed_hp_refuse_prec = rp

    conformal_arms_only = [a for a in CONFORMAL_ARMS if a != "ARM_FIXED_BASELINE"]
    best_conformal_arm = None
    best_conformal_hp_prec = -1.0
    for arm in conformal_arms_only:
        if arm in hp_pts_by_arm and hp_pts_by_arm[arm] > best_conformal_hp_prec:
            best_conformal_arm = arm
            best_conformal_hp_prec = hp_pts_by_arm[arm]

    # Broken-PC-before-structural-framing gate
    if not ctrl_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_POSITIVE_CONTROL: %s@%s@%s out_kb_refuse=%.3f "
                       "< floor %.2f (FIXED baseline broken; structural v8 tiering "
                       "deferred until PC OK)"
                       % (control["arm"], control["regime"], control["band"],
                          ctrl_refuse, control["refuse_rate_floor"]))
    elif not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_CARDINALITY_BREACH: units expected=%d "
                       "observed=%d records expected=%d observed=%d"
                       % (expected_n_units, observed_n_units,
                          expected_n_records, total_records))
    elif not arms_mech_distinct:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_ARMS_MECH_NOT_DISTINCT: %d distinct "
                       "mechanism_hash across %d arms"
                       % (n_distinct_mech, len(CONFORMAL_ARMS)))
    elif not arms_decision_distinct:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_ARMS_DECISION_NOT_DISTINCT: %d distinct "
                       "aggregated decision_hash across %d arms (v8 predicted "
                       "4 distinct sequences by cal-source variation; if this "
                       "fires, cal-source-delta is too small to move decisions)"
                       % (n_distinct_decision, len(CONFORMAL_ARMS)))
    elif best_conformal_arm is not None and best_conformal_hp_prec >= HP_REFUSE_PRECISION_FLOOR:
        verdict = "HARD_PASS"
        verdict_msg = ("HARD_PASS_CONFORMAL: best_conformal=%s refuse_precision=%.3f "
                       ">= %.2f at %s+%s (FIXED baseline refuse_precision=%s at "
                       "same point); v8 cal-source variation separates borderline "
                       "OOD-relation queries where FIXED tau=0.40 is broken; "
                       "cal-source-delta P5(clean)-P5(moderate)=%.4f"
                       % (best_conformal_arm, best_conformal_hp_prec,
                          HP_REFUSE_PRECISION_FLOOR, HP_REGIME, HP_BAND,
                          ("%.3f" % fixed_hp_refuse_prec
                           if fixed_hp_refuse_prec is not None else "NA"),
                          cal_source_delta))
    elif (best_conformal_arm is not None and fixed_hp_refuse_prec is not None
          and best_conformal_hp_prec > fixed_hp_refuse_prec):
        verdict = "MIDDLE_BAND"
        verdict_msg = ("MIDDLE_BAND_PARTIAL_CONFORMAL: best_conformal=%s "
                       "refuse_precision=%.3f > FIXED %.3f at %s+%s but "
                       "< HP floor %.2f"
                       % (best_conformal_arm, best_conformal_hp_prec,
                          fixed_hp_refuse_prec, HP_REGIME, HP_BAND,
                          HP_REFUSE_PRECISION_FLOOR))
    else:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_NO_CONFORMAL_BEAT: best_conformal=%s "
                       "refuse_precision=%s vs FIXED %s at %s+%s "
                       "(no conformal arm beats FIXED; mechanism class truly "
                       "wrong OR HP band still saturating; would falsify v6/v7 "
                       "empirical CONFORMAL_MODERATE=1.000 vs FIXED=0.000 finding)"
                       % (best_conformal_arm,
                          ("%.3f" % best_conformal_hp_prec
                           if best_conformal_hp_prec >= 0 else "NA"),
                          ("%.3f" % fixed_hp_refuse_prec
                           if fixed_hp_refuse_prec is not None else "NA"),
                          HP_REGIME, HP_BAND))

    return {
        "seed": seed,
        "N": N,
        "V_C_per_cat": V_C_per_cat,
        "V_REL": V_REL_FIXED,
        "n_queries_per_unit": n_queries_per_unit,
        "cal_size_total": CAL_SIZE_TOTAL,
        "cal_size_in_kb": CAL_SIZE_IN_KB,
        "cal_size_ood": CAL_SIZE_OOD,
        "elapsed_phase_sweep_s": round(elapsed, 2),
        "observed_n_units": observed_n_units,
        "expected_n_units": expected_n_units,
        "observed_n_records": total_records,
        "expected_n_records": expected_n_records,
        "cardinality_ok": cardinality_ok,
        "phase_map": phase_map,
        "per_arm_summary": per_arm_summary,
        "arm_mechanism_hashes": arm_mechanism_hashes,
        "arm_decision_hashes": arm_decision_hashes,
        "n_distinct_mechanism_hashes": n_distinct_mech,
        "n_distinct_decision_hashes": n_distinct_decision,
        "positive_control_check": {
            "expected": control,
            "observed_out_kb_refuse_rate": ctrl_refuse,
            "passed": ctrl_ok,
        },
        "cal_source_diagnostic": {
            "tau_clean_p5": cal_clean_p5_in,
            "tau_moderate_p5": cal_moderate_p5_in,
            "tau_heavy_p5": cal_heavy_p5_in,
            "cal_source_delta_clean_minus_moderate": cal_source_delta,
            "moderate_p10_in_kb": cal_moderate_p10_in,
            "moderate_p50_in_kb": cal_moderate_p50_in,
            "moderate_p50_ood": cal_moderate_p50_ood,
            "moderate_p90_ood": cal_moderate_p90_ood,
            "moderate_refuse_spread": cal_moderate_refuse_spread,
        },
        "hp_refuse_precision_by_arm": hp_pts_by_arm,
        "hp_regime": HP_REGIME,
        "hp_band": HP_BAND,
        "hp_floor": HP_REFUSE_PRECISION_FLOOR,
        "hp_cal_source_min_delta": HP_CAL_SOURCE_MIN_DELTA,
        "best_conformal_arm": best_conformal_arm,
        "best_conformal_hp_refuse_precision": best_conformal_hp_prec,
        "fixed_hp_refuse_precision": fixed_hp_refuse_prec,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
    }


def aggregate_and_verdict(per_seed: Dict[str, Any], run_mode: str
                           ) -> Dict[str, Any]:
    """Per-seed passthrough aggregator (chunked-per-seed; orchestrator combines)."""
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per_seed payloads",
            "summary": "no per_seed payloads",
        }
    keys = sorted(per_seed.keys())
    seed_result = per_seed[keys[0]]
    out = dict(seed_result)
    out["seeds_observed"] = keys
    out["n_seeds"] = len(keys)
    return out
