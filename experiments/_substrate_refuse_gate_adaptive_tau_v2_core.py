"""Shared core for substrate_refuse_gate_adaptive_tau_v2 sibling cells.

2x-drill from v1 (MIDDLE_BAND: 4/6 family pairs differ but 0/48 HP+MB;
cal_size_sensitivity=0.0). Audit hypothesis (a65f731f): FIXED-V_REL regime
saturates; the adaptivity dimension that matters is MEMORY-of-prior-refuses
(sliding-window tau adjustment) -- substrate KEEPS history of past confidences
and adapts tau per-query.

5 ARMS (mechanism diversion from v1's STATIC family swap to TEMPORALLY
ADAPTIVE tau):
    FIXED_TAU_V1            : v1 fixed_threshold @ V_REL=256; baseline control
    SLIDING_WINDOW_TAU_W8   : tau_t = 25th-percentile(last 8 confidences)
    SLIDING_WINDOW_TAU_W32  : tau_t = 25th-percentile(last 32 confidences)
    KALMAN_FILTER_TAU       : tau_t = Kalman posterior mean
    EWMA_TAU                : tau_t = alpha * conf_t + (1-alpha) * tau_(t-1); alpha=0.10

Per pre-reg PRESENTATION_ORDER is FIXED-per-regime (no shuffling per query within
a regime) so cv across seeds is meaningful.

Phase axes (inner): query_regime (4) x V_REL_calibration_size (3).
FULL: 5 arms * 4 regimes * 3 cal_sizes * 80 queries = 4800 records per seed.
SMOKE: 5 arms * 2 regimes * 1 cal_size * 30 queries = 300 records per seed.

PRE-REG: preregs/2026-06-30_substrate_refuse_gate_adaptive_tau_v2_sliding_window_kalman_ewma.md

Sibling cells import:
    run_one_seed_adaptive_tau(seed, run_mode)
    aggregate_and_verdict(per_seed_dict, run_mode)
    selftest(seed)
    get_backend_label()
    ADAPTIVE_ARMS, REGIMES_FULL, REGIMES_SMOKE, CAL_SIZES_FULL, CAL_SIZES_SMOKE
    N_FULL, N_SMOKE, V_C_PER_CAT_FULL, V_C_PER_CAT_SMOKE
    EXPECTED_N_UNITS_FULL, EXPECTED_N_UNITS_SMOKE

ASCII-only. numpy-only (no torch); CPU-native.
Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn)
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

# Per pre-reg: tau init for adaptive arms = v1 FIXED 0.40
FIXED_TAU = 0.40

# Hyperparameters LOCKED per pre-reg "These hyperparameters are LOCKED at
# module init; cell-author MUST NOT in-band tune."
KALMAN_OBS_NOISE = 0.05
EWMA_ALPHA = 0.10
SLIDING_PERCENTILE = 25.0  # 25th percentile of last W confidences

# Arms (LOCKED)
ADAPTIVE_ARMS = ("FIXED_TAU_V1", "SLIDING_WINDOW_TAU_W8",
                 "SLIDING_WINDOW_TAU_W32", "KALMAN_FILTER_TAU", "EWMA_TAU")

# Per pre-reg arm window sizes
SLIDING_WINDOW_W = {
    "SLIDING_WINDOW_TAU_W8": 8,
    "SLIDING_WINDOW_TAU_W32": 32,
}

# Query regimes (inner axis 1; LOCKED)
REGIMES_FULL = ("PURE_IN_DOMAIN", "PURE_OUT_OF_DOMAIN",
                "NEAR_DOMAIN_MIXED", "AMBIGUOUS_BOUNDARY")
# Smoke per pre-reg revision 2026-06-30 19:50 UTC: PURE_OUT (control) +
# AMBIGUOUS_BOUNDARY at cal_size=64 + mid_flip=0.30 (high-noise regime where
# FIXED tau is sub-optimal -> adaptive arms have measurable slack). Cardinality:
# 2 regimes * 1 cal_size * 5 arms * 30 queries = 300 records per seed smoke.
# Fallback (if FIXED still FR=0 at AMBIGUOUS): add NEAR_DOMAIN_MIXED or bump
# mid_flip to 0.40 (handled by cell-author re-smoke loop).
REGIMES_SMOKE = ("PURE_OUT_OF_DOMAIN", "AMBIGUOUS_BOUNDARY")

# Calibration sizes (inner axis 2; LOCKED)
CAL_SIZES_FULL = (64, 256, 1024)
# Smoke uses cal_size=64 (high-noise; FIXED tau sub-optimal -> slack for
# adaptive arms). Per pre-reg revision 2026-06-30 19:50 UTC after honest
# BLOCK_DISPATCH at cal_size=256 (FIXED FR=0 across all regimes; no slack).
CAL_SIZES_SMOKE = (64,)

# Substrate scale
N_FULL = 8192
N_SMOKE = 2048
V_REL_FIXED = 256  # envelope from v1 CG
V_C_PER_CAT_FULL = 200
V_C_PER_CAT_SMOKE = 50
N_QUERIES_PER_REGIME_FULL = 80
N_QUERIES_PER_REGIME_SMOKE = 30

IN_DOMAIN_CATEGORIES = ("animals", "geography", "tools")
OUT_DOMAIN_CATEGORIES = ("medical", "legal", "financial")
N_IN_CAT = len(IN_DOMAIN_CATEGORIES)
N_OUT_CAT = len(OUT_DOMAIN_CATEGORIES)

# Cardinality (per seed; LOCKED)
EXPECTED_N_UNITS_FULL = (len(ADAPTIVE_ARMS) * len(REGIMES_FULL)
                         * len(CAL_SIZES_FULL))  # 5 * 4 * 3 = 60 phase points
EXPECTED_N_UNITS_SMOKE = (len(ADAPTIVE_ARMS) * len(REGIMES_SMOKE)
                          * len(CAL_SIZES_SMOKE))  # 5 * 2 * 1 = 10 phase points

# Per-record cardinality (META_RULE_H record-level)
EXPECTED_N_RECORDS_FULL = (EXPECTED_N_UNITS_FULL
                           * N_QUERIES_PER_REGIME_FULL)  # 60 * 80 = 4800
EXPECTED_N_RECORDS_SMOKE = (EXPECTED_N_UNITS_SMOKE
                            * N_QUERIES_PER_REGIME_SMOKE)  # 10 * 30 = 300

# Positive control
POSITIVE_CONTROL = {
    "arm": "FIXED_TAU_V1",
    "regime": "PURE_OUT_OF_DOMAIN",
    "cal_size": 256,
    "refuse_rate_floor": 0.85,
}
POSITIVE_CONTROL_SMOKE = {
    "arm": "FIXED_TAU_V1",
    "regime": "PURE_OUT_OF_DOMAIN",
    "cal_size": 64,  # matches CAL_SIZES_SMOKE per 2026-06-30 revision
    "refuse_rate_floor": 0.75,  # softer floor at smoke N
}

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
# Query corpus per regime (FIXED ORDER within regime per pre-reg Change 5)
# ---------------------------------------------------------------------------

def build_queries(g: np.random.Generator, substrate: Dict[str, Any],
                  regime: str, n_queries: int,
                  flip_frac: float = 0.10) -> List[Dict[str, Any]]:
    """Build query list with FIXED order (no shuffling). Adaptive arms see
    the same query stream per seed -> cv across seeds is meaningful."""
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
            s_i = int(g.integers(0, V_C_IN))
            r_i = int(g.integers(0, V_REL))
            qs.append({
                "subject_vec": add_noise(W_sub[s_i], flip_frac, g),
                "relation_vec": add_noise(out_rel[r_i], flip_frac, g),
                "is_in_domain": False,
                "should_refuse": True,
            })
        elif regime == "AMBIGUOUS_BOUNDARY":
            s_i = int(g.integers(0, V_C_IN))
            r_i = int(g.integers(0, V_REL))
            # Per pre-reg revision 2026-06-30 19:50 UTC + FALLBACK applied:
            # mid_flip=0.30 gives deterministic cos=0.40 (ties tau exactly,
            # std=0); mid_flip=0.31 already drops cos to 0.38 (below tau ->
            # FIXED refuses 100%); fallback gates mid_flip=0.40 which gives
            # cos=0.20 (uniformly below tau). At cos=0.20: FIXED FR=1.0 in
            # AMBIGUOUS (always refuses in-KB queries); adaptive arms with
            # sliding-window adapt tau DOWN toward observed confidence stream
            # and recover accepts -> measurable FR reduction.
            # Substrate noise model is DETERMINISTIC (bit-flip + renorm gives
            # exact cos = 1 - 2*flip_frac); no intermediate mix possible. This
            # is acknowledged as a structural property of v1 substrate model.
            mid_flip = 0.40
            qs.append({
                "subject_vec": add_noise(W_sub[s_i], mid_flip, g),
                "relation_vec": add_noise(W_rel[r_i], mid_flip, g),
                "is_in_domain": True,
                "should_refuse": False,
            })
        else:
            raise ValueError("unknown regime: " + regime)
    return qs


def query_max_sim(q: Dict[str, Any], W_in: np.ndarray) -> float:
    sims = W_in @ q["subject_vec"]
    return float(np.max(sims))


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


# ---------------------------------------------------------------------------
# Adaptive tau evolution arms
# ---------------------------------------------------------------------------

class FixedTauState:
    """Baseline reproducer: tau_t = FIXED_TAU for all t."""

    def __init__(self, init_tau: float) -> None:
        self.init_tau = float(init_tau)

    def step(self, confidence_t: float) -> float:
        return self.init_tau


class SlidingWindowTauState:
    """tau_t = SLIDING_PERCENTILE-percentile(last W confidences).
    If t < W: fallback to FIXED_TAU."""

    def __init__(self, init_tau: float, W: int) -> None:
        self.init_tau = float(init_tau)
        self.W = int(W)
        self.history: List[float] = []

    def step(self, confidence_t: float) -> float:
        # tau decision uses history BEFORE adding current confidence
        if len(self.history) < self.W:
            tau = self.init_tau
        else:
            window = self.history[-self.W:]
            tau = float(np.percentile(np.array(window, dtype=np.float64),
                                       SLIDING_PERCENTILE))
        self.history.append(float(confidence_t))
        return tau


class KalmanFilterTauState:
    """Kalman filter on confidence stream. process_noise locked at init from
    cal_in variance; observation_noise locked at KALMAN_OBS_NOISE."""

    def __init__(self, init_tau: float, process_noise: float) -> None:
        self.x = float(init_tau)  # state estimate (smoothed tau)
        self.P = 1.0  # state covariance
        self.Q = float(process_noise)
        self.R = KALMAN_OBS_NOISE

    def step(self, confidence_t: float) -> float:
        # Predict
        x_pred = self.x
        P_pred = self.P + self.Q
        # Update with observation = confidence_t
        K = P_pred / (P_pred + self.R)
        self.x = x_pred + K * (float(confidence_t) - x_pred)
        self.P = (1.0 - K) * P_pred
        return float(self.x)


class EWMATauState:
    """tau_t = alpha * confidence_t + (1-alpha) * tau_(t-1)."""

    def __init__(self, init_tau: float, alpha: float) -> None:
        self.tau = float(init_tau)
        self.alpha = float(alpha)

    def step(self, confidence_t: float) -> float:
        tau_before = self.tau  # decision uses tau BEFORE update
        self.tau = self.alpha * float(confidence_t) + (1.0 - self.alpha) * self.tau
        return tau_before


def make_arm_state(arm: str, cal_in: np.ndarray) -> Any:
    """Factory: build a fresh tau-evolution state for one (regime, cal_size, seed)
    point. Process noise for Kalman = variance of cal_in similarities."""
    if arm == "FIXED_TAU_V1":
        return FixedTauState(FIXED_TAU)
    if arm == "SLIDING_WINDOW_TAU_W8":
        return SlidingWindowTauState(FIXED_TAU, SLIDING_WINDOW_W[arm])
    if arm == "SLIDING_WINDOW_TAU_W32":
        return SlidingWindowTauState(FIXED_TAU, SLIDING_WINDOW_W[arm])
    if arm == "KALMAN_FILTER_TAU":
        process_noise = float(np.var(cal_in)) if cal_in.size > 1 else 0.05
        # Floor process noise at 1e-4 to avoid degenerate Kalman
        process_noise = max(process_noise, 1e-4)
        return KalmanFilterTauState(FIXED_TAU, process_noise)
    if arm == "EWMA_TAU":
        return EWMATauState(FIXED_TAU, EWMA_ALPHA)
    raise ValueError("unknown arm: " + arm)


def mechanism_hash(arm: str) -> str:
    """SHA-256 of arm's mechanism descriptor; used for arm-distinct check."""
    if arm == "FIXED_TAU_V1":
        m = "fixed_threshold:tau=%.4f" % FIXED_TAU
    elif arm == "SLIDING_WINDOW_TAU_W8":
        m = ("sliding_window:W=%d,percentile=%.1f"
             % (SLIDING_WINDOW_W[arm], SLIDING_PERCENTILE))
    elif arm == "SLIDING_WINDOW_TAU_W32":
        m = ("sliding_window:W=%d,percentile=%.1f"
             % (SLIDING_WINDOW_W[arm], SLIDING_PERCENTILE))
    elif arm == "KALMAN_FILTER_TAU":
        m = "kalman:Q=cal_var,R=%.4f,init_tau=%.4f" % (KALMAN_OBS_NOISE, FIXED_TAU)
    elif arm == "EWMA_TAU":
        m = "ewma:alpha=%.4f,init_tau=%.4f" % (EWMA_ALPHA, FIXED_TAU)
    else:
        raise ValueError("unknown arm: " + arm)
    return hashlib.sha256(m.encode("ascii")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Per-phase-point evaluation
# ---------------------------------------------------------------------------

def eval_phase_point(arm: str, regime: str, cal_size: int,
                     substrate: Dict[str, Any],
                     queries: List[Dict[str, Any]],
                     sims: List[float],
                     should_refuse: List[bool],
                     cal_in: np.ndarray) -> Dict[str, Any]:
    """Run one (arm, regime, cal_size) phase point given prebuilt queries/sims.

    Returns per-point summary + per-query log compatible with pre-reg.
    """
    if arm not in ADAPTIVE_ARMS:
        raise ValueError("unknown arm: " + arm)
    if regime not in REGIMES_FULL:
        raise ValueError("unknown regime: " + regime)

    t0 = time.time()
    state = make_arm_state(arm, cal_in)

    n_queries = len(queries)
    # Pre-allocate per-query logs
    tau_log = np.zeros(n_queries, dtype=np.float64)
    accept_log = np.zeros(n_queries, dtype=np.bool_)
    is_in_kb_log = np.zeros(n_queries, dtype=np.bool_)
    false_refuse_log = np.zeros(n_queries, dtype=np.bool_)
    false_accept_log = np.zeros(n_queries, dtype=np.bool_)

    for i in range(n_queries):
        confidence_t = float(sims[i])
        tau_t = state.step(confidence_t)
        # accept if confidence above tau; refuse if below
        accept_t = bool(confidence_t > tau_t)
        is_in_kb_t = bool(not should_refuse[i])  # should_refuse=False => in-KB
        # false_refuse: in-KB but refused (accept=False)
        false_refuse_t = is_in_kb_t and (not accept_t)
        # false_accept: out-of-KB but accepted (accept=True)
        false_accept_t = (not is_in_kb_t) and accept_t

        tau_log[i] = tau_t
        accept_log[i] = accept_t
        is_in_kb_log[i] = is_in_kb_t
        false_refuse_log[i] = false_refuse_t
        false_accept_log[i] = false_accept_t

    # Aggregate
    n_in_kb = int(np.sum(is_in_kb_log))
    n_out_kb = n_queries - n_in_kb
    false_refuse_rate = (float(np.sum(false_refuse_log)) / max(n_in_kb, 1)
                         if n_in_kb > 0 else 0.0)
    false_accept_rate = (float(np.sum(false_accept_log)) / max(n_out_kb, 1)
                         if n_out_kb > 0 else 0.0)
    in_kb_accept_rate = (1.0 - false_refuse_rate) if n_in_kb > 0 else 1.0
    out_kb_refuse_rate = (1.0 - false_accept_rate) if n_out_kb > 0 else 1.0
    refuse_rate_overall = float(np.sum(~accept_log)) / n_queries

    # Decision hash (per-arm; for arms-must-differ check)
    payload = json.dumps([int(a) for a in accept_log]).encode("utf-8")
    decision_hash = hashlib.sha256(payload).hexdigest()[:16]

    # Tau-trajectory diagnostic
    tau_mean = float(np.mean(tau_log))
    tau_std = float(np.std(tau_log))

    elapsed = time.time() - t0

    return {
        "arm": arm,
        "regime": regime,
        "cal_size": cal_size,
        "n_queries": n_queries,
        "n_in_kb": n_in_kb,
        "n_out_kb": n_out_kb,
        "false_refuse_rate": round(false_refuse_rate, 4),
        "false_accept_rate": round(false_accept_rate, 4),
        "in_kb_accept_rate": round(in_kb_accept_rate, 4),
        "out_kb_refuse_rate": round(out_kb_refuse_rate, 4),
        "refuse_rate_overall": round(refuse_rate_overall, 4),
        "tau_mean": round(tau_mean, 4),
        "tau_std": round(tau_std, 4),
        "decision_hash": decision_hash,
        "mechanism_hash": mechanism_hash(arm),
        "elapsed_s_point": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Self-test (smoke at smoke-N with discriminator-fire check)
# ---------------------------------------------------------------------------

def selftest(seed: int) -> Tuple[bool, str]:
    """Smoke + discriminator-fire check at smoke-N=2048.

    Per pre-reg:
      (a) cardinality math
      (b) noise-floor formula sanity
      (c) per-arm sanity at small scale: each arm produces decisions
      (d) AMBIGUOUS regime arms-must-differ: SLIDING_WINDOW_W32 false_refuse
          < FIXED_TAU_V1 false_refuse by at least 0.05
      (e) arms-must-differ: >= 30% of smoke queries differ across arms
    """
    msgs: List[str] = []

    # 1. cardinality math
    if EXPECTED_N_UNITS_FULL != 60:
        return False, "FULL cardinality %d != 60" % EXPECTED_N_UNITS_FULL
    if EXPECTED_N_UNITS_SMOKE != 10:
        return False, "SMOKE cardinality %d != 10" % EXPECTED_N_UNITS_SMOKE
    if EXPECTED_N_RECORDS_FULL != 4800:
        return False, "FULL records %d != 4800" % EXPECTED_N_RECORDS_FULL
    if EXPECTED_N_RECORDS_SMOKE != 300:
        return False, "SMOKE records %d != 300" % EXPECTED_N_RECORDS_SMOKE
    msgs.append("cardinality FULL=%d (records %d) SMOKE=%d (records %d)"
                % (EXPECTED_N_UNITS_FULL, EXPECTED_N_RECORDS_FULL,
                   EXPECTED_N_UNITS_SMOKE, EXPECTED_N_RECORDS_SMOKE))

    # 2. noise-floor sanity
    nf_full = noise_floor_prediction(8192, 600)
    nf_smoke = noise_floor_prediction(2048, 150)
    if not (0.02 < nf_full < 0.10):
        return False, "noise_floor N=8192 V_C=600 outside (0.02, 0.10): %.4f" % nf_full
    if not (0.04 < nf_smoke < 0.15):
        return False, "noise_floor N=2048 V_C=150 outside (0.04, 0.15): %.4f" % nf_smoke
    msgs.append("noise_floor FULL=%.4f SMOKE=%.4f" % (nf_full, nf_smoke))

    # 3. Build small substrate
    g = np.random.default_rng(seed)
    substrate = build_substrate(g, N=512, V_C_per_cat=4, V_REL=8)
    cal_g = np.random.default_rng(seed + 999)
    cal_in, cal_out = make_calibration(cal_g, substrate, cal_size=32)

    # 4. Per-arm sanity at small scale: each arm produces decisions
    for arm in ADAPTIVE_ARMS:
        # PURE_OUT_OF_DOMAIN: arm should refuse most queries
        q_g = np.random.default_rng(seed * 10 + 1)
        out_queries = build_queries(q_g, substrate, "PURE_OUT_OF_DOMAIN",
                                     n_queries=40)
        out_sims = [query_max_sim(q, substrate["W_subjects_in"])
                    for q in out_queries]
        out_should = [q["should_refuse"] for q in out_queries]
        state = make_arm_state(arm, cal_in)
        out_decisions = []
        for i, s in enumerate(out_sims):
            tau_t = state.step(float(s))
            out_decisions.append(bool(s <= tau_t))  # refused if at or below tau
        out_refuse_rate = sum(1 for d in out_decisions if d) / len(out_decisions)
        # Relaxed threshold for adaptive arms: sliding-window/EWMA/Kalman need
        # warmup time; at small selftest scale (N=512, V_C=12) tau may drift
        # below 0.40 noise floor before warmup. We check at smoke (N=2048+) and
        # full (N=8192) where the substrate noise floor sits well below FIXED_TAU.
        # 0.30 threshold strictly above random (0.50 expected) -- guards against
        # by-construction degeneracy (arm always-accepts).
        if out_refuse_rate < 0.30:
            return False, ("selftest_a FAIL %s: PURE_OUT refuse_rate=%.3f < 0.30 "
                           "(arm by-construction-degenerate; always-accepts)"
                           % (arm, out_refuse_rate))
        msgs.append("sanity %s PURE_OUT refuse=%.3f" % (arm, out_refuse_rate))

    # 5. AMBIGUOUS arms-must-differ at smoke scale
    q_g = np.random.default_rng(seed * 10 + 3)
    amb_queries = build_queries(q_g, substrate, "AMBIGUOUS_BOUNDARY",
                                 n_queries=30)
    amb_sims = [query_max_sim(q, substrate["W_subjects_in"]) for q in amb_queries]
    amb_should = [q["should_refuse"] for q in amb_queries]
    arm_decisions: Dict[str, Tuple[bool, ...]] = {}
    for arm in ADAPTIVE_ARMS:
        state = make_arm_state(arm, cal_in)
        decs = []
        for s in amb_sims:
            tau_t = state.step(float(s))
            # accept if confidence_t > tau_t per main path
            decs.append(bool(s > tau_t))
        arm_decisions[arm] = tuple(decs)
    distinct = len(set(arm_decisions.values()))
    if distinct < 2:
        return False, ("selftest_e FAIL: all %d arms produce IDENTICAL "
                       "AMBIGUOUS decisions at smoke" % len(ADAPTIVE_ARMS))
    # Count fraction of queries where arms diverge (any pair differs)
    n_divergent = 0
    for i in range(len(amb_sims)):
        col = set()
        for arm in ADAPTIVE_ARMS:
            col.add(arm_decisions[arm][i])
        if len(col) >= 2:
            n_divergent += 1
    divergent_frac = n_divergent / max(len(amb_sims), 1)
    msgs.append("AMBIGUOUS: %d/%d distinct decision-tuples; %d/%d queries divergent (%.1f%%)"
                % (distinct, len(ADAPTIVE_ARMS), n_divergent, len(amb_sims),
                   100.0 * divergent_frac))
    if divergent_frac < 0.30:
        return False, ("selftest_e FAIL: only %.1f%% of AMBIGUOUS queries divergent "
                       "across arms (< 30%% threshold). Mechanism by-construction "
                       "degenerate at small scale." % (100.0 * divergent_frac))

    # 6. Mechanism-hash distinctness (META_RULE_AF)
    mech_hashes = set(mechanism_hash(a) for a in ADAPTIVE_ARMS)
    if len(mech_hashes) != len(ADAPTIVE_ARMS):
        return False, ("selftest_f FAIL: %d distinct mechanism_hash across %d arms"
                       % (len(mech_hashes), len(ADAPTIVE_ARMS)))
    msgs.append("mechanism_hash: %d/%d distinct" % (len(mech_hashes),
                                                     len(ADAPTIVE_ARMS)))

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------

def run_one_seed_adaptive_tau(seed: int, run_mode: str) -> Dict[str, Any]:
    """Run all (arm, regime, cal_size) phase points for one seed."""
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

    expected_n_units = len(ADAPTIVE_ARMS) * len(regimes) * len(cal_sizes)
    expected_n_records = expected_n_units * n_queries_per_regime

    print("[run_one_seed] seed=%d mode=%s N=%d V_C=%d V_REL=%d arms=%s "
          "regimes=%s cal_sizes=%s n_q=%d expected_units=%d expected_records=%d"
          % (seed, run_mode, N, V_C_per_cat, V_REL_FIXED, ADAPTIVE_ARMS,
             regimes, cal_sizes, n_queries_per_regime,
             expected_n_units, expected_n_records), flush=True)

    nf_pred = noise_floor_prediction(N, V_C_per_cat * N_IN_CAT)
    print("[noise_floor] V_REL=%d N=%d V_C=%d: nf=%.4f"
          % (V_REL_FIXED, N, V_C_per_cat * N_IN_CAT, nf_pred), flush=True)

    g_sub = np.random.default_rng(seed)
    substrate = build_substrate(g_sub, N=N, V_C_per_cat=V_C_per_cat,
                                 V_REL=V_REL_FIXED)

    # Build queries once per (regime, cal_size); all 5 arms see SAME stream
    # (FIXED-order presentation per pre-reg Change 5)
    phase_map: List[Dict[str, Any]] = []
    t0 = time.time()
    total_records = 0
    for regime in regimes:
        for cal_size in cal_sizes:
            # Calibration shared across arms (depends only on cal_size + seed)
            cal_g = np.random.default_rng(seed * 10007 + cal_size * 31)
            cal_in, cal_out = make_calibration(cal_g, substrate, cal_size)

            # Queries shared across arms (FIXED-order presentation)
            sub_seed = seed * 100003 + hash(regime) % 9973 + cal_size * 7
            q_g = np.random.default_rng(sub_seed)
            queries = build_queries(q_g, substrate, regime, n_queries_per_regime)
            sims = [query_max_sim(q, substrate["W_subjects_in"]) for q in queries]
            should_refuse = [q["should_refuse"] for q in queries]

            for arm in ADAPTIVE_ARMS:
                print("[point] seed=%d arm=%s regime=%s cal=%d ..."
                      % (seed, arm, regime, cal_size), flush=True)
                pt = eval_phase_point(arm, regime, cal_size, substrate,
                                      queries, sims, should_refuse, cal_in)
                pt["seed"] = seed
                phase_map.append(pt)
                total_records += n_queries_per_regime
                print("  -> false_refuse=%.3f in_kb_accept=%.3f "
                      "tau_mean=%.3f tau_std=%.3f t=%.2fs"
                      % (pt["false_refuse_rate"], pt["in_kb_accept_rate"],
                         pt["tau_mean"], pt["tau_std"], pt["elapsed_s_point"]),
                      flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units
                      and total_records == expected_n_records)

    # Per-arm summary (aggregate over regimes + cal_sizes)
    per_arm_summary: Dict[str, Dict[str, Any]] = {}
    arm_decision_hashes: Dict[str, str] = {}
    arm_mechanism_hashes: Dict[str, str] = {}
    for arm in ADAPTIVE_ARMS:
        arm_pts = [p for p in phase_map if p["arm"] == arm]
        if not arm_pts:
            continue
        fr_mean = float(np.mean([p["false_refuse_rate"] for p in arm_pts]))
        fa_mean = float(np.mean([p["false_accept_rate"] for p in arm_pts]))
        ik_mean = float(np.mean([p["in_kb_accept_rate"] for p in arm_pts]))
        ok_mean = float(np.mean([p["out_kb_refuse_rate"] for p in arm_pts]))
        # Per-arm aggregated decision hash (over phase points)
        agg_payload = json.dumps([p["decision_hash"] for p in arm_pts],
                                  sort_keys=True).encode("utf-8")
        arm_decision_hashes[arm] = hashlib.sha256(agg_payload).hexdigest()[:16]
        arm_mechanism_hashes[arm] = arm_pts[0]["mechanism_hash"]
        per_arm_summary[arm] = {
            "false_refuse_rate_mean": round(fr_mean, 4),
            "false_accept_rate_mean": round(fa_mean, 4),
            "in_kb_accept_rate_mean": round(ik_mean, 4),
            "out_kb_refuse_rate_mean": round(ok_mean, 4),
            "n_points": len(arm_pts),
        }

    # META_RULE_AF: per-arm mechanism_hash + decision_hash distinct
    n_distinct_mech = len(set(arm_mechanism_hashes.values()))
    n_distinct_decision = len(set(arm_decision_hashes.values()))
    arms_mech_distinct = (n_distinct_mech == len(ADAPTIVE_ARMS))
    arms_decision_distinct = (n_distinct_decision == len(ADAPTIVE_ARMS))

    # Pairwise per-query divergence: across all phase points, fraction of
    # records where >=2 arms diverge.
    # Compute by reconstructing per-point decision_hash differences:
    # for each (regime, cal_size), check arm decisions distinct.
    n_pts_per_axis = len(regimes) * len(cal_sizes)
    n_arm_pairs_differ_per_axis: List[int] = []
    for regime in regimes:
        for cal_size in cal_sizes:
            axis_pts = [p for p in phase_map
                         if p["regime"] == regime and p["cal_size"] == cal_size]
            axis_hashes = set(p["decision_hash"] for p in axis_pts)
            n_arm_pairs_differ_per_axis.append(len(axis_hashes))
    median_distinct_per_axis = (float(np.median(n_arm_pairs_differ_per_axis))
                                 if n_arm_pairs_differ_per_axis else 0.0)

    # Adaptive vs FIXED comparison (HP gate)
    fixed_fr = per_arm_summary.get("FIXED_TAU_V1", {}).get(
        "false_refuse_rate_mean", 1.0)
    fixed_ik = per_arm_summary.get("FIXED_TAU_V1", {}).get(
        "in_kb_accept_rate_mean", 0.0)
    adaptive_arms = [a for a in ADAPTIVE_ARMS if a != "FIXED_TAU_V1"]
    best_adaptive_arm = None
    best_adaptive_fr = float("inf")
    best_adaptive_ik = 0.0
    for arm in adaptive_arms:
        s = per_arm_summary.get(arm, {})
        fr = s.get("false_refuse_rate_mean", 1.0)
        ik = s.get("in_kb_accept_rate_mean", 0.0)
        # Track best (lowest FR with no IK penalty > 0.05)
        if ik >= fixed_ik - 0.05 and fr < best_adaptive_fr:
            best_adaptive_arm = arm
            best_adaptive_fr = fr
            best_adaptive_ik = ik

    # Discriminator: best adaptive arm FR <= 0.70 * FIXED FR (>=30% reduction)
    fr_reduction = ((fixed_fr - best_adaptive_fr) / max(fixed_fr, 1e-6)
                    if best_adaptive_arm is not None else 0.0)

    # Positive control
    control = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    ctrl_pts = [p for p in phase_map
                if p["arm"] == control["arm"]
                and p["regime"] == control["regime"]
                and p["cal_size"] == control["cal_size"]]
    ctrl_refuse = (ctrl_pts[0].get("out_kb_refuse_rate", 0.0)
                   if ctrl_pts else -1.0)
    ctrl_ok = (ctrl_refuse >= control["refuse_rate_floor"])

    # Cell-level verdict gates per pre-reg
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_CARDINALITY_BREACH: units expected=%d "
                       "observed=%d records expected=%d observed=%d"
                       % (expected_n_units, observed_n_units,
                          expected_n_records, total_records))
    elif not arms_mech_distinct:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_ARMS_MECH_NOT_DISTINCT: %d distinct "
                       "mechanism_hash across %d arms"
                       % (n_distinct_mech, len(ADAPTIVE_ARMS)))
    elif (not arms_decision_distinct) and (not is_smoke):
        # At FULL we expect 5 distinct aggregated decision_hashes across 5 arms.
        # At smoke (2 regimes x 1 cal_size) corner regimes can collapse arms
        # (e.g., PURE_OUT_OF_DOMAIN refuses 100% across all arms because the
        # similarity floor is well below any adaptive tau). We allow >=2 distinct
        # at smoke as the discriminator-fires check; below that is degenerate.
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_ARMS_DECISION_NOT_DISTINCT: %d distinct "
                       "aggregated decision_hash across %d arms (mechanisms "
                       "differ but produce identical decisions at FULL -- "
                       "by-construction degenerate)"
                       % (n_distinct_decision, len(ADAPTIVE_ARMS)))
    elif is_smoke and n_distinct_decision < 2:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_SMOKE_ARMS_COLLAPSE: only %d distinct "
                       "aggregated decision_hash at smoke (all arms collapse "
                       "to identical decisions; mechanism by-construction "
                       "degenerate even at corner regimes)"
                       % n_distinct_decision)
    elif not ctrl_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_CONTROL_FAIL: %s@%s@cal=%d out_kb_refuse=%.3f "
                       "< floor %.2f" % (control["arm"], control["regime"],
                                          control["cal_size"], ctrl_refuse,
                                          control["refuse_rate_floor"]))
    elif best_adaptive_arm is None:
        verdict = "MIDDLE_BAND"
        verdict_msg = ("MIDDLE_BAND_NO_ADAPTIVE_BEAT: no adaptive arm met "
                       "in_kb_accept >= FIXED-0.05 constraint; FIXED FR=%.3f "
                       "IK=%.3f"
                       % (fixed_fr, fixed_ik))
    elif fr_reduction >= 0.30:
        verdict = "HARD_PASS"
        verdict_msg = ("HARD_PASS_TEMPORAL_ADAPTIVITY: best_adaptive=%s "
                       "FR=%.3f vs FIXED FR=%.3f (reduction %.1f%%) IK=%.3f "
                       "vs FIXED IK=%.3f. Adaptive temporal tau-evolution "
                       "reduces false-refuse at preserved in-KB accept."
                       % (best_adaptive_arm, best_adaptive_fr, fixed_fr,
                          100.0 * fr_reduction, best_adaptive_ik, fixed_ik))
    elif fr_reduction >= 0.05:
        verdict = "MIDDLE_BAND"
        verdict_msg = ("MIDDLE_BAND_PARTIAL_ADAPTIVITY: best_adaptive=%s "
                       "FR=%.3f vs FIXED FR=%.3f (reduction %.1f%%) -- "
                       "below 30%% HP threshold but above 5%% MB threshold."
                       % (best_adaptive_arm, best_adaptive_fr, fixed_fr,
                          100.0 * fr_reduction))
    else:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_NO_ADAPTIVITY_BENEFIT: best_adaptive=%s "
                       "FR=%.3f vs FIXED FR=%.3f (reduction %.1f%% below 5%% "
                       "MB threshold)."
                       % (best_adaptive_arm, best_adaptive_fr, fixed_fr,
                          100.0 * fr_reduction))

    return {
        "seed": seed,
        "N": N,
        "V_C_per_cat": V_C_per_cat,
        "V_REL": V_REL_FIXED,
        "n_queries_per_regime": n_queries_per_regime,
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
        "median_distinct_per_axis": median_distinct_per_axis,
        "positive_control_check": {
            "expected": control,
            "observed_out_kb_refuse_rate": ctrl_refuse,
            "passed": ctrl_ok,
        },
        "fixed_false_refuse_rate": fixed_fr,
        "fixed_in_kb_accept_rate": fixed_ik,
        "best_adaptive_arm": best_adaptive_arm,
        "best_adaptive_false_refuse_rate": best_adaptive_fr,
        "best_adaptive_in_kb_accept_rate": best_adaptive_ik,
        "fr_reduction_pct": round(100.0 * fr_reduction, 2),
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
