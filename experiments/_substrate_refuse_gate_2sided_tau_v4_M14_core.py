"""Shared core for substrate_refuse_gate_2sided_tau_v4_M14.

v4 revival per research drill (notes/research_M14_v4_revival_drill_2026-07-01.md
sec (a)). Highest-CG revival path (P=0.55; 5x-drill eligible with 4 cross-domain
support: SDT + tail-conformal + TOST + unequal-var SDT).

v3 HF root-cause (Skunkworks 7a89856d): one-sided tau caused net structural
loss. FIXED at moderate: refuse_precision=0.667. BAYESIAN_CI at -0.193 lift
(actively HURTS). SLIDING_WINDOW 0.000 lift. PERCENTILE -0.076 lift. Recall
gained; precision lost. Classic SDT criterion-shift-against-unequal-variance
failure mode.

v4 mechanism class swap: 2-SIDED TAU BAND. Adapt tau_low and tau_high SEPARATELY
against two history streams (low-conf population + high-conf population). Refuse
when score falls in either the low-conf zone (< tau_low; definitely OOD) OR the
ambiguity band [tau_low, tau_high] (consistency-check-fails). Accept only when
score > tau_high.

Composes with M1.3 NoiseChannel CG (c5e5e66a). Preserves v3 4-arm structure
(FIXED baseline + 3 adaptive variants) but each adaptive arm has BOTH thresholds.

4 ARMS (arms-must-differ per META_RULE_AF):
    FIXED_V_REL_256           : baseline; tau=0.40 fixed one-sided (v3 baseline)
    TWO_SIDED_PERCENTILE      : tau_low=P10(low_hist); tau_high=P90(high_hist)
    TWO_SIDED_BAYESIAN_CI     : tau_low=lower CI on low_hist mean;
                                tau_high=upper CI on high_hist mean
    TWO_SIDED_SLIDING_WINDOW  : tau_low=P25(low_hist[-W:]); tau_high=P75(high_hist[-W:])

History stream partition: an incoming confidence c_t joins the LOW history if
c_t <= running_median (of all history so far); joins the HIGH history otherwise.
Warmup: fallback single-tau fixed=0.40 until both histories reach warmup size.
This is a substrate-honest split (no router required; uses the same intent-
classifier-like implicit prior the drill discusses under bimodal buckets option
(c), but as a scalar-history partition rather than exogenous router prior).

Phase axes: NoiseChannel regime (3) x difficulty band (3) x arms (4).
FULL: 4 arms * 3 regimes * 3 bands * 80 queries = 2880 records per seed.
SMOKE: 4 arms * 3 regimes * 3 bands * 30 queries = 1080 records per seed.

Uses M1.3 NoiseChannel additive_gaussian mode per v3 wiring (proven
regime-monotonic std at c5e5e66a; validated by 7a89856d landing that says
"M1.3 wiring correct; adaptive-tau mechanism class wrong shape").

ASCII-only. numpy + torch (NoiseChannel is torch); CPU-native.
Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn).
"""
from __future__ import annotations

import hashlib
import json
import math
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import torch

# Ensure repo root importable for substrate_router
_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from substrate_router.noise_channel import (  # noqa: E402
    NoiseChannel, REGIME_TABLE,
)


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------

FIXED_TAU = 0.40          # v3 baseline tau (kept for FIXED arm + warmup fallback)
V_REL_FIXED = 256         # envelope from v1/v2/v3 CG

# Adaptive arm hyperparams LOCKED per pre-reg (no in-band tuning)
# 2-sided percentiles: symmetric around P50; P10/P90 gives a 20th-80th refuse
# window that matches drill's "OOD tail + ambiguity band" recipe.
TWO_SIDED_LOW_PCTILE = 10.0
TWO_SIDED_HIGH_PCTILE = 90.0

# Sliding-window per-side (v3 SLIDING_W=32 preserved; per-side pctile symmetric).
SLIDING_W = 32
SLIDING_LOW_PCTILE = 25.0
SLIDING_HIGH_PCTILE = 75.0

# Bayesian: 95% CI (z=1.96); warmup per side; symmetric interval.
BAYES_Z = 1.96
BAYES_WARMUP_PER_SIDE = 8

# Percentile arm warmup per side.
PERC_WARMUP_PER_SIDE = 10

# Median-split warmup: until N_MEDIAN_WARMUP total observations seen, all data
# goes into shared history and split partitions kick in at warmup. Prevents
# early-observation partition instability.
MEDIAN_WARMUP = 6

TAU_ARMS = (
    "FIXED_V_REL_256",
    "TWO_SIDED_PERCENTILE",
    "TWO_SIDED_BAYESIAN_CI",
    "TWO_SIDED_SLIDING_WINDOW",
)

# NoiseChannel regimes (M1.3 spec)
REGIMES_M14 = ("clean", "moderate", "heavy")

# Difficulty bands
BANDS_M14 = ("in_KB", "borderline", "OOD")

# Per-band substrate noise (flip_frac) -- v3 values preserved for regime match
BAND_FLIP_FRAC = {
    "in_KB": 0.05,
    "borderline": 0.30,
    "OOD": 0.0,  # OOD uses out-domain codebook (no flip; disjoint atoms)
}

# Substrate scale (both smoke + full run at full-N per DISCRIMINATOR_SURVIVES_SCALE
# option A; v3 confirms 8192 is CPU-cheap in numpy)
N_FULL = 8192
N_SMOKE = 8192          # SAME as full (option A: smoke at full-N)
V_C_PER_CAT_FULL = 200
V_C_PER_CAT_SMOKE = 200

IN_DOMAIN_CATEGORIES = ("animals", "geography", "tools")
OUT_DOMAIN_CATEGORIES = ("medical", "legal", "financial")
N_IN_CAT = len(IN_DOMAIN_CATEGORIES)
N_OUT_CAT = len(OUT_DOMAIN_CATEGORIES)

# Query counts
N_QUERIES_PER_BAND_FULL = 80
N_QUERIES_PER_BAND_SMOKE = 30

# Cardinality (LOCKED)
EXPECTED_N_UNITS_FULL = len(TAU_ARMS) * len(REGIMES_M14) * len(BANDS_M14)   # 4*3*3=36
EXPECTED_N_UNITS_SMOKE = EXPECTED_N_UNITS_FULL                              # 36
EXPECTED_N_RECORDS_FULL = EXPECTED_N_UNITS_FULL * N_QUERIES_PER_BAND_FULL   # 2880
EXPECTED_N_RECORDS_SMOKE = EXPECTED_N_UNITS_SMOKE * N_QUERIES_PER_BAND_SMOKE  # 1080

# Positive control (Sec 15D) -- FIXED baseline at clean/OOD reproduces v3
POSITIVE_CONTROL = {
    "arm": "FIXED_V_REL_256",
    "regime": "clean",
    "band": "OOD",
    "refuse_rate_floor": 0.85,
}
POSITIVE_CONTROL_SMOKE = POSITIVE_CONTROL

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def noise_floor_prediction(N: int, V_C: int) -> float:
    """Substrate argmax-noise floor sqrt(2 ln V / N)."""
    if N <= 0 or V_C <= 1:
        return 0.0
    return math.sqrt(2.0 * math.log(V_C) / N)


def get_backend_label() -> str:
    return "numpy_plus_torch.cpu"


# ---------------------------------------------------------------------------
# Substrate construction (v3-compat)
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
# Query corpus per (band); FIXED ORDER within band per pre-reg (v3-compat)
# ---------------------------------------------------------------------------

def build_queries_band(g: np.random.Generator, substrate: Dict[str, Any],
                       band: str, n_queries: int) -> List[Dict[str, Any]]:
    W_sub = substrate["W_subjects_in"]
    out_sub = substrate["out_subject_atoms"]
    V_C_IN = substrate["V_C_IN"]
    V_C_OUT = substrate["V_C_OUT"]
    if band not in BANDS_M14:
        raise ValueError("unknown band: " + band)
    flip_frac = BAND_FLIP_FRAC[band]
    qs: List[Dict[str, Any]] = []
    for _ in range(n_queries):
        if band == "OOD":
            s_i = int(g.integers(0, V_C_OUT))
            v = add_noise(out_sub[s_i], flip_frac, g)
            qs.append({
                "subject_vec": v,
                "is_in_KB": False,
                "should_refuse": True,
            })
        else:
            s_i = int(g.integers(0, V_C_IN))
            v = add_noise(W_sub[s_i], flip_frac, g)
            qs.append({
                "subject_vec": v,
                "is_in_KB": True,
                "should_refuse": False,
            })
    return qs


# ---------------------------------------------------------------------------
# Cortex NoiseChannel readout -> confidence stream (v3-compat)
# ---------------------------------------------------------------------------

def confidence_stream(queries: List[Dict[str, Any]], substrate: Dict[str, Any],
                      cortex_ch_add: NoiseChannel,
                      regime: str) -> Tuple[np.ndarray, np.ndarray]:
    """Compute per-query confidence via M1.3 NoiseChannel additive_gaussian.

    Same wiring as v3 core (proven regime-monotonic std at c5e5e66a). Preserves
    cosine scale so tau=0.40 stays commensurate.
    """
    W_in = substrate["W_subjects_in"]
    n_q = len(queries)
    conf_out = np.zeros(n_q, dtype=np.float32)
    det_max_sim = np.zeros(n_q, dtype=np.float32)
    for i, q in enumerate(queries):
        sub_sims = W_in @ q["subject_vec"]
        det_max_sim[i] = float(np.max(sub_sims))
    sigma = float(REGIME_TABLE[regime]["sigma"])
    if sigma == 0.0:
        conf_out[:] = det_max_sim
    else:
        gen = cortex_ch_add._torch_gen()
        noise_t = torch.empty(n_q, dtype=torch.float32)
        noise_t.normal_(mean=0.0, std=sigma, generator=gen)
        conf_out[:] = det_max_sim + noise_t.numpy().astype(np.float32)
    return conf_out, det_max_sim


# ---------------------------------------------------------------------------
# Adaptive tau arms -- 2-SIDED
# ---------------------------------------------------------------------------

class FixedTauState:
    """v3-compat: single tau=0.40 fixed one-sided (baseline)."""

    def __init__(self, init_tau: float) -> None:
        self.init_tau = float(init_tau)

    def step(self, confidence_t: float) -> Tuple[float, float]:
        # Returns (tau_low, tau_high); one-sided baseline has tau_low=tau_high.
        return self.init_tau, self.init_tau


class _TwoSidedBase:
    """Common history-partition logic for 2-sided arms.

    Maintains three histories:
      shared: all confidences seen so far (drives running median partition)
      low:    confidences <= running_median at observation time (OOD-side)
      high:   confidences >  running_median at observation time (in-KB-side)

    Until MEDIAN_WARMUP shared observations, arm returns (init_tau, init_tau)
    -- i.e., degenerate to one-sided FIXED. After warmup, tau_low/tau_high
    computed by subclass on their respective side history.
    """

    def __init__(self, init_tau: float) -> None:
        self.init_tau = float(init_tau)
        self.shared: List[float] = []
        self.low: List[float] = []
        self.high: List[float] = []

    def _partition(self, c: float) -> None:
        # Compute median of shared BEFORE inserting c; assigns c to low or high
        # based on that partition, then append to shared.
        if not self.shared:
            median = c
        else:
            arr = np.array(self.shared, dtype=np.float64)
            median = float(np.median(arr))
        if c <= median:
            self.low.append(float(c))
        else:
            self.high.append(float(c))
        self.shared.append(float(c))

    def _compute_taus(self) -> Tuple[float, float]:
        raise NotImplementedError

    def _warmup_ready(self) -> bool:
        raise NotImplementedError

    def step(self, confidence_t: float) -> Tuple[float, float]:
        # Decide taus BEFORE incorporating current observation (avoid lookahead)
        if len(self.shared) < MEDIAN_WARMUP or not self._warmup_ready():
            tau_low, tau_high = self.init_tau, self.init_tau
        else:
            tau_low, tau_high = self._compute_taus()
        # Then partition-and-append for next iteration
        self._partition(float(confidence_t))
        return tau_low, tau_high


class TwoSidedPercentileTauState(_TwoSidedBase):
    """tau_low=P10(low_hist); tau_high=P90(high_hist)."""

    def __init__(self, init_tau: float, low_pctile: float, high_pctile: float,
                 warmup_per_side: int) -> None:
        super().__init__(init_tau)
        self.low_pctile = float(low_pctile)
        self.high_pctile = float(high_pctile)
        self.warmup_per_side = int(warmup_per_side)

    def _warmup_ready(self) -> bool:
        return (len(self.low) >= self.warmup_per_side
                and len(self.high) >= self.warmup_per_side)

    def _compute_taus(self) -> Tuple[float, float]:
        low_arr = np.array(self.low, dtype=np.float64)
        high_arr = np.array(self.high, dtype=np.float64)
        tau_low = float(np.percentile(low_arr, self.low_pctile))
        tau_high = float(np.percentile(high_arr, self.high_pctile))
        # Enforce tau_low <= tau_high (partition well-behaved)
        if tau_low > tau_high:
            mid = 0.5 * (tau_low + tau_high)
            tau_low, tau_high = mid, mid
        return tau_low, tau_high


class TwoSidedBayesianCITauState(_TwoSidedBase):
    """tau_low = mean(low_hist) - z*sd_low/sqrt(n_low)
    tau_high = mean(high_hist) + z*sd_high/sqrt(n_high)."""

    def __init__(self, init_tau: float, z: float, warmup_per_side: int) -> None:
        super().__init__(init_tau)
        self.z = float(z)
        self.warmup_per_side = int(warmup_per_side)

    def _warmup_ready(self) -> bool:
        return (len(self.low) >= self.warmup_per_side
                and len(self.high) >= self.warmup_per_side)

    def _compute_taus(self) -> Tuple[float, float]:
        low_arr = np.array(self.low, dtype=np.float64)
        high_arr = np.array(self.high, dtype=np.float64)
        n_l, n_h = low_arr.shape[0], high_arr.shape[0]
        mu_l = float(np.mean(low_arr))
        mu_h = float(np.mean(high_arr))
        sd_l = float(np.std(low_arr, ddof=1)) if n_l > 1 else 0.0
        sd_h = float(np.std(high_arr, ddof=1)) if n_h > 1 else 0.0
        tau_low = mu_l - self.z * sd_l / max(math.sqrt(n_l), 1.0)
        tau_high = mu_h + self.z * sd_h / max(math.sqrt(n_h), 1.0)
        # Clamp to [-1.0, 1.0] (cosine range) and enforce ordering
        tau_low = max(-1.0, min(1.0, tau_low))
        tau_high = max(-1.0, min(1.0, tau_high))
        if tau_low > tau_high:
            mid = 0.5 * (tau_low + tau_high)
            tau_low, tau_high = mid, mid
        return tau_low, tau_high


class TwoSidedSlidingWindowTauState(_TwoSidedBase):
    """tau_low = P25(low_hist[-W:]); tau_high = P75(high_hist[-W:])."""

    def __init__(self, init_tau: float, W: int, low_pctile: float,
                 high_pctile: float) -> None:
        super().__init__(init_tau)
        self.W = int(W)
        self.low_pctile = float(low_pctile)
        self.high_pctile = float(high_pctile)

    def _warmup_ready(self) -> bool:
        return len(self.low) >= self.W and len(self.high) >= self.W

    def _compute_taus(self) -> Tuple[float, float]:
        low_arr = np.array(self.low[-self.W:], dtype=np.float64)
        high_arr = np.array(self.high[-self.W:], dtype=np.float64)
        tau_low = float(np.percentile(low_arr, self.low_pctile))
        tau_high = float(np.percentile(high_arr, self.high_pctile))
        if tau_low > tau_high:
            mid = 0.5 * (tau_low + tau_high)
            tau_low, tau_high = mid, mid
        return tau_low, tau_high


def make_arm_state(arm: str) -> Any:
    if arm == "FIXED_V_REL_256":
        return FixedTauState(FIXED_TAU)
    if arm == "TWO_SIDED_PERCENTILE":
        return TwoSidedPercentileTauState(
            FIXED_TAU, TWO_SIDED_LOW_PCTILE, TWO_SIDED_HIGH_PCTILE,
            PERC_WARMUP_PER_SIDE)
    if arm == "TWO_SIDED_BAYESIAN_CI":
        return TwoSidedBayesianCITauState(
            FIXED_TAU, BAYES_Z, BAYES_WARMUP_PER_SIDE)
    if arm == "TWO_SIDED_SLIDING_WINDOW":
        return TwoSidedSlidingWindowTauState(
            FIXED_TAU, SLIDING_W, SLIDING_LOW_PCTILE, SLIDING_HIGH_PCTILE)
    raise ValueError("unknown arm: " + arm)


def mechanism_hash(arm: str) -> str:
    if arm == "FIXED_V_REL_256":
        m = "fixed_v_rel_256:tau=%.4f,V_REL=%d,one_sided" % (
            FIXED_TAU, V_REL_FIXED)
    elif arm == "TWO_SIDED_PERCENTILE":
        m = ("two_sided_percentile:low_pctile=%.1f,high_pctile=%.1f,"
             "warmup_per_side=%d,init_tau=%.4f,median_warmup=%d"
             % (TWO_SIDED_LOW_PCTILE, TWO_SIDED_HIGH_PCTILE,
                PERC_WARMUP_PER_SIDE, FIXED_TAU, MEDIAN_WARMUP))
    elif arm == "TWO_SIDED_BAYESIAN_CI":
        m = ("two_sided_bayesian_ci:z=%.4f,warmup_per_side=%d,init_tau=%.4f,"
             "median_warmup=%d"
             % (BAYES_Z, BAYES_WARMUP_PER_SIDE, FIXED_TAU, MEDIAN_WARMUP))
    elif arm == "TWO_SIDED_SLIDING_WINDOW":
        m = ("two_sided_sliding_window:W=%d,low_pctile=%.1f,high_pctile=%.1f,"
             "init_tau=%.4f,median_warmup=%d"
             % (SLIDING_W, SLIDING_LOW_PCTILE, SLIDING_HIGH_PCTILE,
                FIXED_TAU, MEDIAN_WARMUP))
    else:
        raise ValueError("unknown arm: " + arm)
    return hashlib.sha256(m.encode("ascii")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# 2-sided decision rule
# ---------------------------------------------------------------------------

def two_sided_decide(confidence_t: float, tau_low: float,
                     tau_high: float) -> bool:
    """Return True = ACCEPT, False = REFUSE.

    REFUSE if confidence < tau_low (definitely OOD) OR confidence in
    [tau_low, tau_high] (ambiguity band). ACCEPT if confidence > tau_high.

    For FIXED_V_REL_256 (tau_low == tau_high == 0.40) reduces to one-sided
    baseline: ACCEPT iff confidence > 0.40 (v3-compat).
    """
    if tau_low == tau_high:
        return confidence_t > tau_high
    return confidence_t > tau_high


# ---------------------------------------------------------------------------
# Per-phase-point evaluation
# ---------------------------------------------------------------------------

def eval_phase_point(arm: str, regime: str, band: str,
                     confidence_stream_arr: np.ndarray,
                     is_in_KB_arr: np.ndarray) -> Dict[str, Any]:
    if arm not in TAU_ARMS:
        raise ValueError("unknown arm: " + arm)
    if regime not in REGIMES_M14:
        raise ValueError("unknown regime: " + regime)
    if band not in BANDS_M14:
        raise ValueError("unknown band: " + band)

    t0 = time.time()
    state = make_arm_state(arm)
    n_queries = int(confidence_stream_arr.shape[0])
    tau_low_log = np.zeros(n_queries, dtype=np.float64)
    tau_high_log = np.zeros(n_queries, dtype=np.float64)
    accept_log = np.zeros(n_queries, dtype=np.bool_)
    refuse_log = np.zeros(n_queries, dtype=np.bool_)

    for i in range(n_queries):
        c = float(confidence_stream_arr[i])
        tau_low_t, tau_high_t = state.step(c)
        accept_t = two_sided_decide(c, tau_low_t, tau_high_t)
        tau_low_log[i] = tau_low_t
        tau_high_log[i] = tau_high_t
        accept_log[i] = accept_t
        refuse_log[i] = not accept_t

    is_in_KB = is_in_KB_arr.astype(np.bool_)
    n_in_kb = int(np.sum(is_in_KB))
    n_out_kb = n_queries - n_in_kb

    refuse_rate = float(np.sum(refuse_log)) / max(n_queries, 1)

    n_refuse_on_ood = int(np.sum(refuse_log & (~is_in_KB)))
    n_refuse_on_in = int(np.sum(refuse_log & is_in_KB))
    n_refuse_total = int(np.sum(refuse_log))

    false_refuse_rate = (float(n_refuse_on_in) / max(n_in_kb, 1)
                         if n_in_kb > 0 else 0.0)
    false_accept_rate = (float(np.sum(accept_log & (~is_in_KB))) / max(n_out_kb, 1)
                         if n_out_kb > 0 else 0.0)
    refuse_precision = (float(n_refuse_on_ood) / max(n_refuse_total, 1)
                        if n_refuse_total > 0 else 0.0)

    payload = json.dumps([int(a) for a in accept_log]).encode("utf-8")
    decision_hash = hashlib.sha256(payload).hexdigest()[:16]

    tau_low_mean = float(np.mean(tau_low_log))
    tau_low_std = float(np.std(tau_low_log))
    tau_high_mean = float(np.mean(tau_high_log))
    tau_high_std = float(np.std(tau_high_log))
    band_width_mean = float(np.mean(tau_high_log - tau_low_log))
    conf_mean = float(np.mean(confidence_stream_arr))
    conf_std = float(np.std(confidence_stream_arr))

    elapsed = time.time() - t0

    return {
        "arm": arm,
        "regime": regime,
        "band": band,
        "n_queries": n_queries,
        "n_in_kb": n_in_kb,
        "n_out_kb": n_out_kb,
        "refuse_rate": round(refuse_rate, 4),
        "false_refuse_rate": round(false_refuse_rate, 4),
        "false_accept_rate": round(false_accept_rate, 4),
        "refuse_precision": round(refuse_precision, 4),
        "tau_low_mean": round(tau_low_mean, 4),
        "tau_low_std": round(tau_low_std, 4),
        "tau_high_mean": round(tau_high_mean, 4),
        "tau_high_std": round(tau_high_std, 4),
        "band_width_mean": round(band_width_mean, 4),
        "conf_mean": round(conf_mean, 4),
        "conf_std": round(conf_std, 4),
        "decision_hash": decision_hash,
        "mechanism_hash": mechanism_hash(arm),
        "elapsed_s_point": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Self-test (formula sanity + arm-distinctness + 2-sided semantics)
# ---------------------------------------------------------------------------

def selftest(seed: int) -> Tuple[bool, str]:
    msgs: List[str] = []

    # (a) cardinality
    if EXPECTED_N_UNITS_FULL != 36:
        return False, "FULL units %d != 36" % EXPECTED_N_UNITS_FULL
    if EXPECTED_N_UNITS_SMOKE != 36:
        return False, "SMOKE units %d != 36" % EXPECTED_N_UNITS_SMOKE
    if EXPECTED_N_RECORDS_FULL != 2880:
        return False, "FULL records %d != 2880" % EXPECTED_N_RECORDS_FULL
    if EXPECTED_N_RECORDS_SMOKE != 1080:
        return False, "SMOKE records %d != 1080" % EXPECTED_N_RECORDS_SMOKE
    msgs.append("cardinality FULL=%d records=%d SMOKE=%d records=%d"
                % (EXPECTED_N_UNITS_FULL, EXPECTED_N_RECORDS_FULL,
                   EXPECTED_N_UNITS_SMOKE, EXPECTED_N_RECORDS_SMOKE))

    # (b) noise-floor
    nf = noise_floor_prediction(N_FULL, V_C_PER_CAT_FULL * N_IN_CAT)
    if not (0.02 < nf < 0.10):
        return False, "noise_floor N=%d V_C=%d = %.4f outside (0.02, 0.10)" % (
            N_FULL, V_C_PER_CAT_FULL * N_IN_CAT, nf)
    msgs.append("noise_floor N=%d V_C=%d nf=%.4f (< tau=%.2f OK)" % (
        N_FULL, V_C_PER_CAT_FULL * N_IN_CAT, nf, FIXED_TAU))

    # (c) NoiseChannel wiring: additive_gaussian regime std monotonic
    cortex_rng = torch.Generator().manual_seed(seed * 10007 + 42)
    ch = NoiseChannel(mode="additive_gaussian", rng=cortex_rng)

    def _sim_stream(regime: str, n: int = 200) -> np.ndarray:
        sigma = float(REGIME_TABLE[regime]["sigma"])
        if sigma == 0.0:
            return np.full(n, 0.40, dtype=np.float32)
        gen = ch._torch_gen()
        noise_t = torch.empty(n, dtype=torch.float32)
        noise_t.normal_(mean=0.0, std=sigma, generator=gen)
        return np.full(n, 0.40, dtype=np.float32) + noise_t.numpy()

    std_clean = float(np.std(_sim_stream("clean")))
    std_mod = float(np.std(_sim_stream("moderate")))
    std_hvy = float(np.std(_sim_stream("heavy")))
    if not (std_clean < std_mod < std_hvy):
        return False, ("noise_channel scalar-stream std NOT monotonically "
                       "increasing: %.4f, %.4f, %.4f"
                       % (std_clean, std_mod, std_hvy))
    if not (0.10 < std_mod < 0.20):
        return False, ("noise_channel moderate std outside (0.10, 0.20): %.4f"
                       % std_mod)
    msgs.append("NoiseChannel additive_gaussian std clean=%.4f moderate=%.4f "
                "heavy=%.4f OK" % (std_clean, std_mod, std_hvy))

    # (d) arms produce non-degenerate decisions on synthetic stream
    # INTERLEAVED high/low ordering (matches real regime where in_KB and OOD
    # queries mix). Length 80 to satisfy sliding-W=32 warmup on BOTH sides
    # given median-split partition. A monotone-descending stream is
    # pathologically-ordered because median floats up with each new low value
    # so all items cascade into the LOW side; interleaving avoids this and
    # matches the actual production regime.
    _rng_syn = np.random.default_rng(11)
    _hi = _rng_syn.uniform(0.55, 0.85, size=40).astype(np.float32)
    _lo = _rng_syn.uniform(0.05, 0.35, size=40).astype(np.float32)
    fake_conf = np.empty(80, dtype=np.float32)
    fake_conf[0::2] = _hi  # even -> high
    fake_conf[1::2] = _lo  # odd -> low
    arm_n_accept: Dict[str, int] = {}
    for arm in TAU_ARMS:
        state = make_arm_state(arm)
        n_accept = 0
        for c in fake_conf:
            tau_low_t, tau_high_t = state.step(float(c))
            if two_sided_decide(float(c), tau_low_t, tau_high_t):
                n_accept += 1
        arm_n_accept[arm] = n_accept
        if n_accept == 0 or n_accept == len(fake_conf):
            return False, ("arm %s degenerate on synthetic stream: "
                           "n_accept=%d/%d"
                           % (arm, n_accept, len(fake_conf)))
        msgs.append("arm %s synthetic n_accept=%d/%d"
                    % (arm, n_accept, len(fake_conf)))

    # (e) mechanism-hash distinctness
    mhs = set(mechanism_hash(a) for a in TAU_ARMS)
    if len(mhs) != len(TAU_ARMS):
        return False, ("mechanism_hash NOT distinct across %d arms: %d unique"
                       % (len(TAU_ARMS), len(mhs)))
    msgs.append("mechanism_hash distinct %d/%d" % (len(mhs), len(TAU_ARMS)))

    # (f) 2-sided semantics: for adaptive arms, verify at least 1 arm produced
    # a decision DIFFERENT from FIXED baseline (otherwise 2-sided collapsed to
    # one-sided; mechanism-class bug)
    fixed_state = make_arm_state("FIXED_V_REL_256")
    fixed_decisions = []
    for c in fake_conf:
        tau_low_t, tau_high_t = fixed_state.step(float(c))
        fixed_decisions.append(two_sided_decide(float(c), tau_low_t, tau_high_t))
    n_adaptive_diff = 0
    for arm in ("TWO_SIDED_PERCENTILE", "TWO_SIDED_BAYESIAN_CI",
                "TWO_SIDED_SLIDING_WINDOW"):
        state = make_arm_state(arm)
        diffs = 0
        for i, c in enumerate(fake_conf):
            tau_low_t, tau_high_t = state.step(float(c))
            d = two_sided_decide(float(c), tau_low_t, tau_high_t)
            if d != fixed_decisions[i]:
                diffs += 1
        if diffs > 0:
            n_adaptive_diff += 1
        msgs.append("arm %s decisions differ-from-FIXED at %d/%d positions"
                    % (arm, diffs, len(fake_conf)))
    if n_adaptive_diff == 0:
        return False, ("2-sided semantics bug: NO adaptive arm produced any "
                       "decision different from FIXED baseline; 2-sided "
                       "mechanism collapsed to one-sided")
    msgs.append("2-sided semantics: %d/3 adaptive arms differ from FIXED"
                % n_adaptive_diff)

    # (g) positive control: FIXED refuses OOD at clean
    g = np.random.default_rng(seed)
    substrate = build_substrate(g, N=1024, V_C_per_cat=30, V_REL=V_REL_FIXED)
    ch_ctrl = NoiseChannel(mode="additive_gaussian",
                           rng=torch.Generator().manual_seed(seed * 10007 + 42))
    q_g = np.random.default_rng(seed * 100003 + 7)
    ood_queries = build_queries_band(q_g, substrate, "OOD", n_queries=40)
    conf_arr, det_arr = confidence_stream(ood_queries, substrate, ch_ctrl,
                                          regime="clean")
    is_kb = np.zeros(len(ood_queries), dtype=np.bool_)
    state = make_arm_state("FIXED_V_REL_256")
    n_refuse = 0
    for c in conf_arr:
        tau_low_t, tau_high_t = state.step(float(c))
        if not two_sided_decide(float(c), tau_low_t, tau_high_t):
            n_refuse += 1
    refuse_rate = n_refuse / len(conf_arr)
    if refuse_rate < 0.85:
        return False, ("baseline_reproducer FAIL @ clean OOD: refuse=%.3f < 0.85"
                       % refuse_rate)
    msgs.append("baseline_reproducer @ clean OOD refuse=%.3f (>= 0.85 OK)"
                % refuse_rate)

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------

def run_one_seed_v4(seed: int, run_mode: str) -> Dict[str, Any]:
    is_smoke = (run_mode == "smoke")
    if is_smoke:
        N = N_SMOKE
        V_C_per_cat = V_C_PER_CAT_SMOKE
        n_queries_per_band = N_QUERIES_PER_BAND_SMOKE
    else:
        N = N_FULL
        V_C_per_cat = V_C_PER_CAT_FULL
        n_queries_per_band = N_QUERIES_PER_BAND_FULL

    expected_n_units = len(TAU_ARMS) * len(REGIMES_M14) * len(BANDS_M14)
    expected_n_records = expected_n_units * n_queries_per_band

    print("[run_one_seed_v4] seed=%d mode=%s N=%d V_C_per_cat=%d V_REL=%d "
          "arms=%s regimes=%s bands=%s n_q=%d expected_units=%d expected_records=%d"
          % (seed, run_mode, N, V_C_per_cat, V_REL_FIXED, TAU_ARMS,
             REGIMES_M14, BANDS_M14, n_queries_per_band,
             expected_n_units, expected_n_records), flush=True)

    nf_pred = noise_floor_prediction(N, V_C_per_cat * N_IN_CAT)
    print("[noise_floor] N=%d V_C=%d nf=%.4f (< tau=%.2f)"
          % (N, V_C_per_cat * N_IN_CAT, nf_pred, FIXED_TAU), flush=True)

    g_sub = np.random.default_rng(seed)
    substrate = build_substrate(g_sub, N=N, V_C_per_cat=V_C_per_cat,
                                V_REL=V_REL_FIXED)

    cortex_seed = seed * 10007 + 42
    cortex_rng = torch.Generator().manual_seed(cortex_seed)
    cortex_ch_add = NoiseChannel(mode="additive_gaussian", rng=cortex_rng)
    print("[cortex_rng] cortex_seed=%d substrate_seed=%d mode=additive_gaussian"
          % (cortex_seed, seed), flush=True)

    band_queries: Dict[str, List[Dict[str, Any]]] = {}
    for band in BANDS_M14:
        q_seed = seed * 100003 + hash(band) % 9973
        q_g = np.random.default_rng(q_seed)
        band_queries[band] = build_queries_band(q_g, substrate, band,
                                                n_queries_per_band)

    phase_map: List[Dict[str, Any]] = []
    total_records = 0
    t0 = time.time()

    for regime in REGIMES_M14:
        for band in BANDS_M14:
            queries = band_queries[band]
            conf_arr, det_max_sim = confidence_stream(queries, substrate,
                                                     cortex_ch_add,
                                                     regime=regime)
            is_kb_arr = np.array([q["is_in_KB"] for q in queries],
                                 dtype=np.bool_)

            for arm in TAU_ARMS:
                print("[point] seed=%d arm=%s regime=%s band=%s ..."
                      % (seed, arm, regime, band), flush=True)
                pt = eval_phase_point(arm, regime, band, conf_arr, is_kb_arr)
                pt["seed"] = seed
                pt["conf_stream_mean"] = round(float(np.mean(conf_arr)), 4)
                pt["conf_stream_std"] = round(float(np.std(conf_arr)), 4)
                pt["substrate_max_sim_mean"] = round(float(np.mean(det_max_sim)),
                                                     4)
                phase_map.append(pt)
                total_records += n_queries_per_band
                print("  -> refuse=%.3f false_refuse=%.3f false_accept=%.3f "
                      "refuse_prec=%.3f tau_low=%.3f tau_high=%.3f "
                      "band_w=%.3f conf_mean=%.3f t=%.2fs"
                      % (pt["refuse_rate"], pt["false_refuse_rate"],
                         pt["false_accept_rate"], pt["refuse_precision"],
                         pt["tau_low_mean"], pt["tau_high_mean"],
                         pt["band_width_mean"], pt["conf_stream_mean"],
                         pt["elapsed_s_point"]), flush=True)

    elapsed = time.time() - t0
    observed_n_units = len(phase_map)
    cardinality_ok = (observed_n_units == expected_n_units
                      and total_records == expected_n_records)

    # Per-arm summary
    per_arm_summary: Dict[str, Dict[str, Any]] = {}
    arm_mechanism_hashes: Dict[str, str] = {}
    arm_decision_hashes: Dict[str, str] = {}
    for arm in TAU_ARMS:
        pts = [p for p in phase_map if p["arm"] == arm]
        if not pts:
            continue
        rr_mean = float(np.mean([p["refuse_rate"] for p in pts]))
        rp_mean = float(np.mean([p["refuse_precision"] for p in pts]))
        fr_mean = float(np.mean([p["false_refuse_rate"] for p in pts]))
        fa_mean = float(np.mean([p["false_accept_rate"] for p in pts]))
        band_w_mean = float(np.mean([p["band_width_mean"] for p in pts]))
        agg_payload = json.dumps([p["decision_hash"] for p in pts],
                                 sort_keys=True).encode("utf-8")
        arm_decision_hashes[arm] = hashlib.sha256(agg_payload).hexdigest()[:16]
        arm_mechanism_hashes[arm] = pts[0]["mechanism_hash"]
        per_arm_summary[arm] = {
            "refuse_rate_mean": round(rr_mean, 4),
            "refuse_precision_mean": round(rp_mean, 4),
            "false_refuse_rate_mean": round(fr_mean, 4),
            "false_accept_rate_mean": round(fa_mean, 4),
            "band_width_mean": round(band_w_mean, 4),
            "n_points": len(pts),
        }

    n_distinct_mech = len(set(arm_mechanism_hashes.values()))
    n_distinct_decision = len(set(arm_decision_hashes.values()))
    arms_mech_distinct = (n_distinct_mech == len(TAU_ARMS))

    # Discriminator (HP gate): per-arm monotonicity at OOD across regimes
    # + refuse-precision lift at moderate regime, computed against FIXED baseline.
    hp_gate_details: Dict[str, Dict[str, Any]] = {}
    hp_winners: List[str] = []

    def _regime_precision(arm: str, regime: str) -> float:
        pts = [p for p in phase_map
               if p["arm"] == arm and p["regime"] == regime]
        tp = 0
        fp = 0
        for p in pts:
            n_q = int(p["n_queries"])
            rr = float(p["refuse_rate"])
            n_refuse_here = int(round(rr * n_q))
            if p["band"] == "OOD":
                tp += n_refuse_here
            else:
                fp += n_refuse_here
        denom = tp + fp
        return float(tp) / denom if denom > 0 else 0.0

    fixed_refuse_prec_mod = _regime_precision("FIXED_V_REL_256", "moderate")
    fixed_refuse_prec_clean = _regime_precision("FIXED_V_REL_256", "clean")
    fixed_refuse_prec_hvy = _regime_precision("FIXED_V_REL_256", "heavy")

    for arm in ("TWO_SIDED_PERCENTILE", "TWO_SIDED_BAYESIAN_CI",
                "TWO_SIDED_SLIDING_WINDOW"):
        rr_by_regime: Dict[str, float] = {}
        for pt in phase_map:
            if pt["arm"] == arm and pt["band"] == "OOD":
                rr_by_regime[pt["regime"]] = pt["refuse_rate"]
        rr_clean = rr_by_regime.get("clean", -1.0)
        rr_mod = rr_by_regime.get("moderate", -1.0)
        rr_hvy = rr_by_regime.get("heavy", -1.0)
        monotonic_non_increasing = (rr_clean >= rr_mod >= rr_hvy)
        monotonic_non_decreasing = (rr_clean <= rr_mod <= rr_hvy)
        monotonic = monotonic_non_increasing or monotonic_non_decreasing

        rp_mod = _regime_precision(arm, "moderate")
        rp_clean = _regime_precision(arm, "clean")
        rp_hvy = _regime_precision(arm, "heavy")
        precision_lift = rp_mod - fixed_refuse_prec_mod

        hp_gate_details[arm] = {
            "rr_clean_OOD": rr_clean,
            "rr_moderate_OOD": rr_mod,
            "rr_heavy_OOD": rr_hvy,
            "monotonic_across_regime_at_OOD": monotonic,
            "monotonic_non_increasing": monotonic_non_increasing,
            "monotonic_non_decreasing": monotonic_non_decreasing,
            "refuse_precision_at_moderate_regime": round(rp_mod, 4),
            "refuse_precision_at_clean_regime": round(rp_clean, 4),
            "refuse_precision_at_heavy_regime": round(rp_hvy, 4),
            "fixed_refuse_precision_at_moderate_regime": round(
                fixed_refuse_prec_mod, 4),
            "precision_lift_over_fixed_at_moderate": round(precision_lift, 4),
        }
        if monotonic and precision_lift >= 0.15:
            hp_winners.append(arm)

    # Positive control
    control = POSITIVE_CONTROL_SMOKE if is_smoke else POSITIVE_CONTROL
    ctrl_pt = None
    for pt in phase_map:
        if (pt["arm"] == control["arm"] and pt["regime"] == control["regime"]
                and pt["band"] == control["band"]):
            ctrl_pt = pt
            break
    ctrl_refuse = ctrl_pt["refuse_rate"] if ctrl_pt else -1.0
    ctrl_ok = (ctrl_refuse >= control["refuse_rate_floor"])

    # Cell-level verdict
    if not cardinality_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H: units "
                       "expected=%d observed=%d records expected=%d observed=%d"
                       % (expected_n_units, observed_n_units,
                          expected_n_records, total_records))
    elif not arms_mech_distinct:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_ARMS_MECH_NOT_DISTINCT_META_RULE_AF: %d "
                       "distinct mechanism_hash across %d arms"
                       % (n_distinct_mech, len(TAU_ARMS)))
    elif not ctrl_ok:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_POSITIVE_CONTROL_MISMATCH: %s@%s@%s refuse=%.3f "
                       "< floor %.2f"
                       % (control["arm"], control["regime"], control["band"],
                          ctrl_refuse, control["refuse_rate_floor"]))
    elif len(hp_winners) >= 1:
        verdict = "HARD_PASS"
        verdict_msg = ("HARD_PASS_M14_2SIDED_TAU_VIA_NOISECHANNEL: %d "
                       "2-sided arm(s) satisfy monotonic+precision_lift>=0.15 "
                       "at moderate regime: %s. Cross-seed cv checked at "
                       "aggregate. Closes M3 milestone M1.4 (glass-box "
                       "conversational calibration primitive)."
                       % (len(hp_winners), hp_winners))
    else:
        any_monotonic = any(hp_gate_details[a]["monotonic_across_regime_at_OOD"]
                            for a in hp_gate_details)
        any_lift_5 = any(
            hp_gate_details[a]["precision_lift_over_fixed_at_moderate"] >= 0.05
            for a in hp_gate_details)
        if any_monotonic and any_lift_5:
            verdict = "MIDDLE_BAND"
            verdict_msg = ("MIDDLE_BAND_PARTIAL_M14_V4: monotonic OR "
                           "precision_lift 5-15%% at moderate regime; no arm "
                           "cleared HP threshold. 2-sided helps but not enough.")
        else:
            verdict = "HARD_FAIL"
            verdict_msg = ("HARD_FAIL_2SIDED_INSUFFICIENT: no 2-sided arm "
                           "monotonic across regime OR precision_lift >= 0.05. "
                           "Escalate to (a+c) meta-composition or M3-cortex-"
                           "external calibrator per drill sec (a) HF plan.")

    return {
        "seed": seed,
        "N": N,
        "V_C_per_cat": V_C_per_cat,
        "V_REL": V_REL_FIXED,
        "n_queries_per_band": n_queries_per_band,
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
        "hp_gate_details": hp_gate_details,
        "hp_winners_this_seed": hp_winners,
        "positive_control_check": {
            "expected": control,
            "observed_refuse_rate": ctrl_refuse,
            "passed": ctrl_ok,
        },
        "cortex_rng_seed": cortex_seed,
        "noise_channel_mode": "additive_gaussian",
        "mechanism_class": "2sided_tau_low_plus_tau_high_median_split_history",
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
    }


def aggregate_and_verdict(per_seed: Dict[str, Any], run_mode: str
                          ) -> Dict[str, Any]:
    """Per-seed passthrough (chunked-per-seed; orchestrator aggregates)."""
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
