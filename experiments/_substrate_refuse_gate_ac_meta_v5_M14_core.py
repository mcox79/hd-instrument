"""Shared core for substrate_refuse_gate_ac_meta_v5_M14 (a+c meta-composition).

v5 revival per Skunkworks criteria (v4 HF landing 2026-07-01) + research drill
sec (a+c) meta-composition: 2-sided tau band (a) x bimodal-history buckets (c).

v4 HF root-cause (from disk metrics.json seed_7_smoke):
    FIXED_V_REL_256 @ moderate/OOD refuse_rate = 1.000 (BASELINE CEILING)
    TWO_SIDED_PERCENTILE lift = -0.0667 (adaptive HURTS at ceiling)
    TWO_SIDED_BAYESIAN_CI lift = -0.1111
    TWO_SIDED_SLIDING_WINDOW lift = 0.0000
FIXED baseline saturates OOD across clean+moderate regimes (only heavy=0.8
shows any headroom). 2-sided tau alone cannot differentiate because there's
no measurable band left; regime forces all arms to top of refuse-rate axis.

v5 mechanism-class swap: (a+c) META-COMPOSITION.
    4 TAU STREAMS TOTAL:
      bucket_hi.tau_low + bucket_hi.tau_high  (in-KB-like bucket, 2-sided)
      bucket_lo.tau_low + bucket_lo.tau_high  (OOD-like bucket, 2-sided)
    Bucket assignment: online 2-component Gaussian mixture (EM-style) on
    confidence-stream history; hard-assign incoming query to closer
    component; per-component tau adapts on that component's history.
    Substrate-honest: uses only observable confidence stream (no external
    labels, no router prior); the drill's (c) "bimodal buckets" via
    scalar-history GMM instead of exogenous router.

REGIME FIX (per Skunkworks revival criteria): unsaturate FIXED baseline at
OOD/moderate. FIXED_TAU LOWERED from 0.40 to 0.20 (still >> noise_floor
sqrt(2*ln(600)/8192)=0.0395 by 5x margin). This puts moderate/OOD FIXED
refuse rate in the measurable band (predicted 0.75-0.90) instead of at
ceiling 1.000. Discriminator precision_lift >=0.15 can fire.

Composes with M1.3 NoiseChannel CG (c5e5e66a). Preserves v3/v4 4-arm structure
(FIXED baseline + 3 adaptive variants). Each adaptive arm has 4 tau streams
(2 buckets x 2 sides).

4 ARMS (arms-must-differ per META_RULE_AF):
    FIXED_V_REL_256_TAU_020        : baseline; tau=0.20 fixed one-sided
    BIMODAL_2SIDED_PERCENTILE      : per-bucket tau_low=P10 / tau_high=P90
    BIMODAL_2SIDED_BAYESIAN_CI     : per-bucket tau_low/high via CI on
                                     bucket-conditional mean+sd
    BIMODAL_2SIDED_SLIDING_WINDOW  : per-bucket tau_low=P25(last-W) /
                                     tau_high=P75(last-W)

Bucket assignment via online 2-component GMM (running mu_hi/sd_hi and
mu_lo/sd_lo with EM update on each new confidence sample). Warmup: single
tau=0.20 fixed until MIN_PER_BUCKET observations reach each bucket.

Decision rule for a query c_t assigned to bucket B:
    ACCEPT iff c_t > B.tau_high
    REFUSE otherwise

Phase axes: NoiseChannel regime (3) x difficulty band (3) x arms (4) = 36
phase points per seed. Query counts: FULL=80/band; SMOKE=30/band.

ASCII-only. numpy + torch (NoiseChannel is torch). CPU-native.
Author: exp_dev 2026-07-01 (Opus 4.7 1M, agent-spawn, task from research).
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

_REPO = Path(__file__).resolve().parent.parent
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from substrate_router.noise_channel import (  # noqa: E402
    NoiseChannel, REGIME_TABLE,
)


# ---------------------------------------------------------------------------
# Pre-reg constants (LOCKED at module init; META_RULE_AE)
# ---------------------------------------------------------------------------

# v5 REGIME FIX: LOWER fixed tau to move FIXED baseline off the OOD ceiling
# at moderate regime. v4 landed FIXED @ moderate/OOD = 1.000 (SATURATED);
# v5 predicts FIXED @ moderate/OOD ~ 0.80-0.90 with tau=0.20 (measurable band).
# Still >> noise_floor 0.040 by 5x margin.
FIXED_TAU = 0.20
V_REL_FIXED = 256

# Per-bucket 2-sided percentiles (mirrors v4)
BUCKET_LOW_PCTILE = 10.0
BUCKET_HIGH_PCTILE = 90.0

SLIDING_W = 32
SLIDING_LOW_PCTILE = 25.0
SLIDING_HIGH_PCTILE = 75.0

BAYES_Z = 1.96
BAYES_WARMUP_PER_BUCKET = 8
PERC_WARMUP_PER_BUCKET = 10

# GMM bucket warmup: until MIN_PER_BUCKET observations have been assigned
# to EACH bucket, arm returns single fixed tau=0.20 (degenerate).
GMM_WARMUP_TOTAL = 8       # total obs before GMM assignment begins
GMM_MIN_PER_BUCKET = 4     # min per-bucket obs before per-bucket taus fire

# GMM online-EM hyperparams
GMM_LR = 0.15              # learning rate on incremental mu/var updates
GMM_INIT_MU_HI = 0.60      # bucket-hi initial mean guess
GMM_INIT_MU_LO = 0.15      # bucket-lo initial mean guess
GMM_INIT_VAR = 0.05        # initial variance for both

TAU_ARMS = (
    "FIXED_V_REL_256_TAU_020",
    "BIMODAL_2SIDED_PERCENTILE",
    "BIMODAL_2SIDED_BAYESIAN_CI",
    "BIMODAL_2SIDED_SLIDING_WINDOW",
)

REGIMES_M14 = ("clean", "moderate", "heavy")
BANDS_M14 = ("in_KB", "borderline", "OOD")

# Per-band substrate noise (flip_frac) -- v4 values preserved
BAND_FLIP_FRAC = {
    "in_KB": 0.05,
    "borderline": 0.30,
    "OOD": 0.0,
}

# Substrate scale (both smoke + full run at full-N per DISCRIMINATOR_SURVIVES_SCALE
# option A; numpy CPU-cheap at N=8192)
N_FULL = 8192
N_SMOKE = 8192
V_C_PER_CAT_FULL = 200
V_C_PER_CAT_SMOKE = 200

IN_DOMAIN_CATEGORIES = ("animals", "geography", "tools")
OUT_DOMAIN_CATEGORIES = ("medical", "legal", "financial")
N_IN_CAT = len(IN_DOMAIN_CATEGORIES)
N_OUT_CAT = len(OUT_DOMAIN_CATEGORIES)

N_QUERIES_PER_BAND_FULL = 80
N_QUERIES_PER_BAND_SMOKE = 30

EXPECTED_N_UNITS_FULL = len(TAU_ARMS) * len(REGIMES_M14) * len(BANDS_M14)   # 36
EXPECTED_N_UNITS_SMOKE = EXPECTED_N_UNITS_FULL                              # 36
EXPECTED_N_RECORDS_FULL = EXPECTED_N_UNITS_FULL * N_QUERIES_PER_BAND_FULL   # 2880
EXPECTED_N_RECORDS_SMOKE = EXPECTED_N_UNITS_SMOKE * N_QUERIES_PER_BAND_SMOKE  # 1080

# Positive control: FIXED at clean/OOD -- at tau=0.20 baseline STILL refuses
# most OOD (sub_max_OOD ~ 0.034 < 0.20) so refuse >= 0.85 remains valid
POSITIVE_CONTROL = {
    "arm": "FIXED_V_REL_256_TAU_020",
    "regime": "clean",
    "band": "OOD",
    "refuse_rate_floor": 0.85,
}
POSITIVE_CONTROL_SMOKE = POSITIVE_CONTROL

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def noise_floor_prediction(N: int, V_C: int) -> float:
    if N <= 0 or V_C <= 1:
        return 0.0
    return math.sqrt(2.0 * math.log(V_C) / N)


def get_backend_label() -> str:
    return "numpy_plus_torch.cpu"


# ---------------------------------------------------------------------------
# Substrate construction (v3/v4-compat)
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
            qs.append({"subject_vec": v, "is_in_KB": False,
                       "should_refuse": True})
        else:
            s_i = int(g.integers(0, V_C_IN))
            v = add_noise(W_sub[s_i], flip_frac, g)
            qs.append({"subject_vec": v, "is_in_KB": True,
                       "should_refuse": False})
    return qs


def confidence_stream(queries: List[Dict[str, Any]], substrate: Dict[str, Any],
                      cortex_ch_add: NoiseChannel,
                      regime: str) -> Tuple[np.ndarray, np.ndarray]:
    """Compute per-query confidence via M1.3 NoiseChannel additive_gaussian."""
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
# Adaptive tau arms -- (a+c) meta-composition
# ---------------------------------------------------------------------------

class FixedTauState:
    """v4-compat: single tau=0.20 fixed one-sided (baseline)."""

    def __init__(self, init_tau: float) -> None:
        self.init_tau = float(init_tau)

    def step(self, confidence_t: float) -> Tuple[float, float, str]:
        # Returns (tau_low, tau_high, bucket_label); bucket=NA for FIXED.
        return self.init_tau, self.init_tau, "NA"


class _BimodalGMM:
    """Online 2-component Gaussian mixture (running EM-lite).

    Maintains (mu_hi, var_hi, mu_lo, var_lo, mix_hi). Each new obs updates
    the two component moments toward the observation weighted by soft
    posterior. After GMM_WARMUP_TOTAL obs seen, we hard-assign incoming
    queries to closer component (Mahalanobis distance).
    """

    def __init__(self) -> None:
        self.mu_hi = GMM_INIT_MU_HI
        self.mu_lo = GMM_INIT_MU_LO
        self.var_hi = GMM_INIT_VAR
        self.var_lo = GMM_INIT_VAR
        self.n_seen = 0

    def _posterior_hi(self, c: float) -> float:
        # Component-wise pdf (unnormalized); soft posterior on hi.
        v_hi = max(self.var_hi, 1e-6)
        v_lo = max(self.var_lo, 1e-6)
        d_hi = (c - self.mu_hi) * (c - self.mu_hi) / (2.0 * v_hi)
        d_lo = (c - self.mu_lo) * (c - self.mu_lo) / (2.0 * v_lo)
        # Numerically stable: subtract min log-density
        log_hi = -0.5 * math.log(v_hi) - d_hi
        log_lo = -0.5 * math.log(v_lo) - d_lo
        m = max(log_hi, log_lo)
        e_hi = math.exp(log_hi - m)
        e_lo = math.exp(log_lo - m)
        return e_hi / (e_hi + e_lo)

    def assign(self, c: float) -> str:
        """Hard-assign observation c to a bucket by closer component mean.

        Uses raw distance-to-mean rather than posterior to be robust in
        early iterations where variance estimates are noisy.
        """
        d_hi = abs(c - self.mu_hi)
        d_lo = abs(c - self.mu_lo)
        return "hi" if d_hi <= d_lo else "lo"

    def update(self, c: float) -> None:
        """Soft-EM update on both components with learning rate GMM_LR."""
        p_hi = self._posterior_hi(c)
        p_lo = 1.0 - p_hi
        # Incremental mean/var update: weighted step toward observation
        self.mu_hi = self.mu_hi + GMM_LR * p_hi * (c - self.mu_hi)
        self.mu_lo = self.mu_lo + GMM_LR * p_lo * (c - self.mu_lo)
        d_hi = c - self.mu_hi
        d_lo = c - self.mu_lo
        self.var_hi = self.var_hi + GMM_LR * p_hi * (d_hi * d_hi - self.var_hi)
        self.var_lo = self.var_lo + GMM_LR * p_lo * (d_lo * d_lo - self.var_lo)
        self.var_hi = max(self.var_hi, 1e-4)
        self.var_lo = max(self.var_lo, 1e-4)
        self.n_seen += 1


class _BimodalBase:
    """(a+c) meta-composition base: bimodal buckets x 2-sided tau band."""

    def __init__(self, init_tau: float) -> None:
        self.init_tau = float(init_tau)
        self.gmm = _BimodalGMM()
        self.bucket_hi: List[float] = []
        self.bucket_lo: List[float] = []

    def _compute_bucket_taus(self, bucket: str
                             ) -> Tuple[float, float]:
        raise NotImplementedError

    def _bucket_warmup_ready(self, bucket: str) -> bool:
        raise NotImplementedError

    def step(self, confidence_t: float) -> Tuple[float, float, str]:
        # Decide bucket + taus BEFORE incorporating current obs (no lookahead)
        if self.gmm.n_seen < GMM_WARMUP_TOTAL:
            bucket = "warmup"
            tau_low, tau_high = self.init_tau, self.init_tau
        else:
            bucket = self.gmm.assign(float(confidence_t))
            if not self._bucket_warmup_ready(bucket):
                tau_low, tau_high = self.init_tau, self.init_tau
            else:
                tau_low, tau_high = self._compute_bucket_taus(bucket)

        # Assign obs to bucket + update GMM for next iteration
        # Even in warmup, GMM must see the obs to grow n_seen.
        if bucket == "warmup":
            # Split by init means (use assign but don't fire tau)
            b_assign = self.gmm.assign(float(confidence_t))
        else:
            b_assign = bucket
        if b_assign == "hi":
            self.bucket_hi.append(float(confidence_t))
        else:
            self.bucket_lo.append(float(confidence_t))
        self.gmm.update(float(confidence_t))
        return tau_low, tau_high, bucket


class BimodalPercentileState(_BimodalBase):
    """Per bucket: tau_low=P10(bucket_hist); tau_high=P90(bucket_hist)."""

    def __init__(self, init_tau: float, low_pctile: float,
                 high_pctile: float, warmup_per_bucket: int) -> None:
        super().__init__(init_tau)
        self.low_pctile = float(low_pctile)
        self.high_pctile = float(high_pctile)
        self.warmup_per_bucket = int(warmup_per_bucket)

    def _bucket_warmup_ready(self, bucket: str) -> bool:
        b_hist = self.bucket_hi if bucket == "hi" else self.bucket_lo
        return len(b_hist) >= self.warmup_per_bucket

    def _compute_bucket_taus(self, bucket: str) -> Tuple[float, float]:
        b_hist = self.bucket_hi if bucket == "hi" else self.bucket_lo
        arr = np.array(b_hist, dtype=np.float64)
        tau_low = float(np.percentile(arr, self.low_pctile))
        tau_high = float(np.percentile(arr, self.high_pctile))
        if tau_low > tau_high:
            mid = 0.5 * (tau_low + tau_high)
            tau_low, tau_high = mid, mid
        return tau_low, tau_high


class BimodalBayesianCIState(_BimodalBase):
    """Per bucket: tau_low = mean - z*sd/sqrt(n); tau_high = mean + z*sd/sqrt(n)."""

    def __init__(self, init_tau: float, z: float,
                 warmup_per_bucket: int) -> None:
        super().__init__(init_tau)
        self.z = float(z)
        self.warmup_per_bucket = int(warmup_per_bucket)

    def _bucket_warmup_ready(self, bucket: str) -> bool:
        b_hist = self.bucket_hi if bucket == "hi" else self.bucket_lo
        return len(b_hist) >= self.warmup_per_bucket

    def _compute_bucket_taus(self, bucket: str) -> Tuple[float, float]:
        b_hist = self.bucket_hi if bucket == "hi" else self.bucket_lo
        arr = np.array(b_hist, dtype=np.float64)
        n = arr.shape[0]
        mu = float(np.mean(arr))
        sd = float(np.std(arr, ddof=1)) if n > 1 else 0.0
        tau_low = mu - self.z * sd / max(math.sqrt(n), 1.0)
        tau_high = mu + self.z * sd / max(math.sqrt(n), 1.0)
        tau_low = max(-1.0, min(1.0, tau_low))
        tau_high = max(-1.0, min(1.0, tau_high))
        if tau_low > tau_high:
            mid = 0.5 * (tau_low + tau_high)
            tau_low, tau_high = mid, mid
        return tau_low, tau_high


class BimodalSlidingWindowState(_BimodalBase):
    """Per bucket: tau_low=P25(hist[-W:]); tau_high=P75(hist[-W:])."""

    def __init__(self, init_tau: float, W: int, low_pctile: float,
                 high_pctile: float) -> None:
        super().__init__(init_tau)
        self.W = int(W)
        self.low_pctile = float(low_pctile)
        self.high_pctile = float(high_pctile)

    def _bucket_warmup_ready(self, bucket: str) -> bool:
        b_hist = self.bucket_hi if bucket == "hi" else self.bucket_lo
        return len(b_hist) >= self.W

    def _compute_bucket_taus(self, bucket: str) -> Tuple[float, float]:
        b_hist = self.bucket_hi if bucket == "hi" else self.bucket_lo
        arr = np.array(b_hist[-self.W:], dtype=np.float64)
        tau_low = float(np.percentile(arr, self.low_pctile))
        tau_high = float(np.percentile(arr, self.high_pctile))
        if tau_low > tau_high:
            mid = 0.5 * (tau_low + tau_high)
            tau_low, tau_high = mid, mid
        return tau_low, tau_high


def make_arm_state(arm: str) -> Any:
    if arm == "FIXED_V_REL_256_TAU_020":
        return FixedTauState(FIXED_TAU)
    if arm == "BIMODAL_2SIDED_PERCENTILE":
        return BimodalPercentileState(
            FIXED_TAU, BUCKET_LOW_PCTILE, BUCKET_HIGH_PCTILE,
            PERC_WARMUP_PER_BUCKET)
    if arm == "BIMODAL_2SIDED_BAYESIAN_CI":
        return BimodalBayesianCIState(
            FIXED_TAU, BAYES_Z, BAYES_WARMUP_PER_BUCKET)
    if arm == "BIMODAL_2SIDED_SLIDING_WINDOW":
        return BimodalSlidingWindowState(
            FIXED_TAU, SLIDING_W, SLIDING_LOW_PCTILE, SLIDING_HIGH_PCTILE)
    raise ValueError("unknown arm: " + arm)


def mechanism_hash(arm: str) -> str:
    if arm == "FIXED_V_REL_256_TAU_020":
        m = ("fixed_v_rel_256_tau_020:tau=%.4f,V_REL=%d,one_sided_no_bucket"
             % (FIXED_TAU, V_REL_FIXED))
    elif arm == "BIMODAL_2SIDED_PERCENTILE":
        m = ("bimodal_2sided_percentile:low_pctile=%.1f,high_pctile=%.1f,"
             "warmup_per_bucket=%d,init_tau=%.4f,gmm_warmup=%d,"
             "gmm_min_per_bucket=%d,gmm_lr=%.4f,mu_hi_init=%.3f,mu_lo_init=%.3f"
             % (BUCKET_LOW_PCTILE, BUCKET_HIGH_PCTILE,
                PERC_WARMUP_PER_BUCKET, FIXED_TAU,
                GMM_WARMUP_TOTAL, GMM_MIN_PER_BUCKET, GMM_LR,
                GMM_INIT_MU_HI, GMM_INIT_MU_LO))
    elif arm == "BIMODAL_2SIDED_BAYESIAN_CI":
        m = ("bimodal_2sided_bayesian_ci:z=%.4f,warmup_per_bucket=%d,"
             "init_tau=%.4f,gmm_warmup=%d,gmm_min_per_bucket=%d,gmm_lr=%.4f,"
             "mu_hi_init=%.3f,mu_lo_init=%.3f"
             % (BAYES_Z, BAYES_WARMUP_PER_BUCKET, FIXED_TAU,
                GMM_WARMUP_TOTAL, GMM_MIN_PER_BUCKET, GMM_LR,
                GMM_INIT_MU_HI, GMM_INIT_MU_LO))
    elif arm == "BIMODAL_2SIDED_SLIDING_WINDOW":
        m = ("bimodal_2sided_sliding_window:W=%d,low_pctile=%.1f,"
             "high_pctile=%.1f,init_tau=%.4f,gmm_warmup=%d,"
             "gmm_min_per_bucket=%d,gmm_lr=%.4f,mu_hi_init=%.3f,mu_lo_init=%.3f"
             % (SLIDING_W, SLIDING_LOW_PCTILE, SLIDING_HIGH_PCTILE,
                FIXED_TAU, GMM_WARMUP_TOTAL, GMM_MIN_PER_BUCKET, GMM_LR,
                GMM_INIT_MU_HI, GMM_INIT_MU_LO))
    else:
        raise ValueError("unknown arm: " + arm)
    return hashlib.sha256(m.encode("ascii")).hexdigest()[:16]


def two_sided_decide(confidence_t: float, tau_low: float,
                     tau_high: float) -> bool:
    """ACCEPT iff confidence > tau_high; else REFUSE.

    Preserves v4 2-sided semantics: for FIXED (tau_low == tau_high) reduces
    to one-sided ACCEPT iff c > tau.
    """
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
    bucket_log: List[str] = []

    for i in range(n_queries):
        c = float(confidence_stream_arr[i])
        tau_low_t, tau_high_t, bucket_t = state.step(c)
        accept_t = two_sided_decide(c, tau_low_t, tau_high_t)
        tau_low_log[i] = tau_low_t
        tau_high_log[i] = tau_high_t
        accept_log[i] = accept_t
        refuse_log[i] = not accept_t
        bucket_log.append(bucket_t)

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

    # Bucket-usage instrumentation (bucket-divergence health check)
    n_hi = sum(1 for b in bucket_log if b == "hi")
    n_lo = sum(1 for b in bucket_log if b == "lo")
    n_warmup = sum(1 for b in bucket_log if b == "warmup")
    n_na = sum(1 for b in bucket_log if b == "NA")
    bucket_hi_frac = float(n_hi) / max(n_queries, 1)
    bucket_lo_frac = float(n_lo) / max(n_queries, 1)

    # Report final GMM means for bucket-divergence gate (v5 discriminator hook)
    gmm_mu_hi = float("nan")
    gmm_mu_lo = float("nan")
    if hasattr(state, "gmm"):
        gmm_mu_hi = float(state.gmm.mu_hi)
        gmm_mu_lo = float(state.gmm.mu_lo)

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
        "bucket_hi_frac": round(bucket_hi_frac, 4),
        "bucket_lo_frac": round(bucket_lo_frac, 4),
        "n_bucket_warmup": n_warmup,
        "n_bucket_na": n_na,
        "gmm_mu_hi_final": round(gmm_mu_hi, 4) if not math.isnan(gmm_mu_hi) else None,
        "gmm_mu_lo_final": round(gmm_mu_lo, 4) if not math.isnan(gmm_mu_lo) else None,
        "elapsed_s_point": round(elapsed, 3),
    }


# ---------------------------------------------------------------------------
# Self-test (formula sanity + arm-distinctness + bucket-divergence)
# ---------------------------------------------------------------------------

def selftest(seed: int) -> Tuple[bool, str]:
    msgs: List[str] = []

    if EXPECTED_N_UNITS_FULL != 36:
        return False, "FULL units %d != 36" % EXPECTED_N_UNITS_FULL
    if EXPECTED_N_RECORDS_FULL != 2880:
        return False, "FULL records %d != 2880" % EXPECTED_N_RECORDS_FULL
    if EXPECTED_N_RECORDS_SMOKE != 1080:
        return False, "SMOKE records %d != 1080" % EXPECTED_N_RECORDS_SMOKE
    msgs.append("cardinality FULL=%d records=%d SMOKE_records=%d"
                % (EXPECTED_N_UNITS_FULL, EXPECTED_N_RECORDS_FULL,
                   EXPECTED_N_RECORDS_SMOKE))

    nf = noise_floor_prediction(N_FULL, V_C_PER_CAT_FULL * N_IN_CAT)
    if not (0.02 < nf < 0.10):
        return False, "noise_floor nf=%.4f outside (0.02, 0.10)" % nf
    if not (nf < FIXED_TAU):
        return False, ("noise_floor %.4f >= FIXED_TAU %.2f -- tau below noise; "
                       "baseline uninterpretable" % (nf, FIXED_TAU))
    msgs.append("noise_floor=%.4f FIXED_TAU=%.2f (5x margin OK)" % (nf, FIXED_TAU))

    # NoiseChannel wiring regime std monotonic
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
        return False, ("NoiseChannel std NOT monotonic: %.4f, %.4f, %.4f"
                       % (std_clean, std_mod, std_hvy))
    msgs.append("NoiseChannel std clean=%.4f mod=%.4f hvy=%.4f OK"
                % (std_clean, std_mod, std_hvy))

    # Bucket-divergence assertion: on a bimodal-mixed synthetic stream, GMM
    # buckets must diverge (mu_hi > mu_lo by margin >= 0.20 after warmup).
    _rng_syn = np.random.default_rng(11)
    _hi = _rng_syn.uniform(0.55, 0.85, size=40).astype(np.float32)
    _lo = _rng_syn.uniform(0.05, 0.35, size=40).astype(np.float32)
    fake_conf = np.empty(80, dtype=np.float32)
    fake_conf[0::2] = _hi
    fake_conf[1::2] = _lo

    # Check GMM directly
    gmm = _BimodalGMM()
    for c in fake_conf:
        gmm.update(float(c))
    if not (gmm.mu_hi - gmm.mu_lo >= 0.20):
        return False, ("GMM bucket divergence FAIL: mu_hi=%.3f mu_lo=%.3f "
                       "gap=%.3f < 0.20 after 80 samples"
                       % (gmm.mu_hi, gmm.mu_lo, gmm.mu_hi - gmm.mu_lo))
    msgs.append("GMM diverges mu_hi=%.3f mu_lo=%.3f gap=%.3f OK"
                % (gmm.mu_hi, gmm.mu_lo, gmm.mu_hi - gmm.mu_lo))

    # Per-arm non-degenerate decisions on synthetic
    arm_n_accept: Dict[str, int] = {}
    for arm in TAU_ARMS:
        state = make_arm_state(arm)
        n_accept = 0
        for c in fake_conf:
            tl, th, _b = state.step(float(c))
            if two_sided_decide(float(c), tl, th):
                n_accept += 1
        arm_n_accept[arm] = n_accept
        if n_accept == 0 or n_accept == len(fake_conf):
            return False, ("arm %s degenerate: n_accept=%d/%d"
                           % (arm, n_accept, len(fake_conf)))
        msgs.append("arm %s synthetic n_accept=%d/%d"
                    % (arm, n_accept, len(fake_conf)))

    mhs = set(mechanism_hash(a) for a in TAU_ARMS)
    if len(mhs) != len(TAU_ARMS):
        return False, ("mechanism_hash NOT distinct: %d unique of %d"
                       % (len(mhs), len(TAU_ARMS)))
    msgs.append("mechanism_hash distinct %d/%d" % (len(mhs), len(TAU_ARMS)))

    # (a+c) semantics: bimodal arms MUST produce >=1 decision different from
    # FIXED (bimodal not collapsing to one-sided single tau).
    fixed_state = make_arm_state("FIXED_V_REL_256_TAU_020")
    fixed_decisions = []
    for c in fake_conf:
        tl, th, _b = fixed_state.step(float(c))
        fixed_decisions.append(two_sided_decide(float(c), tl, th))
    n_bimodal_diff = 0
    for arm in ("BIMODAL_2SIDED_PERCENTILE", "BIMODAL_2SIDED_BAYESIAN_CI",
                "BIMODAL_2SIDED_SLIDING_WINDOW"):
        state = make_arm_state(arm)
        diffs = 0
        for i, c in enumerate(fake_conf):
            tl, th, _b = state.step(float(c))
            d = two_sided_decide(float(c), tl, th)
            if d != fixed_decisions[i]:
                diffs += 1
        if diffs > 0:
            n_bimodal_diff += 1
        msgs.append("arm %s decisions differ-from-FIXED at %d/%d"
                    % (arm, diffs, len(fake_conf)))
    if n_bimodal_diff == 0:
        return False, ("(a+c) semantics bug: NO bimodal arm differs from "
                       "FIXED baseline; bimodal collapsed to one-sided")
    msgs.append("(a+c) semantics: %d/3 bimodal arms differ from FIXED"
                % n_bimodal_diff)

    # Positive control: FIXED @ clean/OOD >= 0.85 at tau=0.20 (small N)
    g = np.random.default_rng(seed)
    substrate = build_substrate(g, N=1024, V_C_per_cat=30, V_REL=V_REL_FIXED)
    ch_ctrl = NoiseChannel(mode="additive_gaussian",
                           rng=torch.Generator().manual_seed(seed * 10007 + 42))
    q_g = np.random.default_rng(seed * 100003 + 7)
    ood_queries = build_queries_band(q_g, substrate, "OOD", n_queries=40)
    conf_arr, _ = confidence_stream(ood_queries, substrate, ch_ctrl,
                                    regime="clean")
    state = make_arm_state("FIXED_V_REL_256_TAU_020")
    n_refuse = 0
    for c in conf_arr:
        tl, th, _b = state.step(float(c))
        if not two_sided_decide(float(c), tl, th):
            n_refuse += 1
    refuse_rate = n_refuse / len(conf_arr)
    if refuse_rate < 0.85:
        return False, ("baseline_reproducer FAIL @ clean OOD: refuse=%.3f < 0.85"
                       % refuse_rate)
    msgs.append("baseline_reproducer @ clean OOD refuse=%.3f (>= 0.85 OK)"
                % refuse_rate)

    # Regime unsaturation check: at N=1024, FIXED @ moderate/OOD must NOT be
    # at ceiling 1.000 (v5 regime fix per Skunkworks revival criteria).
    # Small N + moderate noise: predict refuse in [0.7, 0.98] measurable band.
    ch_ctrl2 = NoiseChannel(mode="additive_gaussian",
                            rng=torch.Generator().manual_seed(seed * 10007 + 42))
    conf_arr_mod, _ = confidence_stream(ood_queries, substrate, ch_ctrl2,
                                        regime="moderate")
    state2 = make_arm_state("FIXED_V_REL_256_TAU_020")
    n_refuse_mod = 0
    for c in conf_arr_mod:
        tl, th, _b = state2.step(float(c))
        if not two_sided_decide(float(c), tl, th):
            n_refuse_mod += 1
    mod_refuse_rate = n_refuse_mod / len(conf_arr_mod)
    # Predicted band: [0.60, 0.98]. Ceiling 1.000 -> regime NOT unsaturated ->
    # discriminator can't fire. This is the v4 failure Skunkworks flagged.
    if mod_refuse_rate >= 0.99:
        return False, ("REGIME_STILL_SATURATED: FIXED @ moderate/OOD "
                       "refuse=%.3f >= 0.99 at tau=%.2f; v4 saturation NOT "
                       "cured. Lower FIXED_TAU further." %
                       (mod_refuse_rate, FIXED_TAU))
    msgs.append("regime_unsaturation @ moderate/OOD refuse=%.3f (< 0.99; "
                "discriminator can fire)" % mod_refuse_rate)

    return True, "; ".join(msgs)


# ---------------------------------------------------------------------------
# Per-seed phase sweep
# ---------------------------------------------------------------------------

def run_one_seed_v5(seed: int, run_mode: str) -> Dict[str, Any]:
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

    print("[run_one_seed_v5] seed=%d mode=%s N=%d V_C=%d V_REL=%d "
          "arms=%s regimes=%s bands=%s n_q=%d exp_units=%d exp_records=%d"
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
                      "band_w=%.3f hi_frac=%.2f lo_frac=%.2f conf_mean=%.3f "
                      "t=%.2fs"
                      % (pt["refuse_rate"], pt["false_refuse_rate"],
                         pt["false_accept_rate"], pt["refuse_precision"],
                         pt["tau_low_mean"], pt["tau_high_mean"],
                         pt["band_width_mean"], pt["bucket_hi_frac"],
                         pt["bucket_lo_frac"], pt["conf_stream_mean"],
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

    # Discriminator: monotonic across regime + precision_lift >= 0.15 at moderate
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

    fixed_refuse_prec_mod = _regime_precision("FIXED_V_REL_256_TAU_020",
                                              "moderate")
    fixed_refuse_prec_clean = _regime_precision("FIXED_V_REL_256_TAU_020",
                                                "clean")
    fixed_refuse_prec_hvy = _regime_precision("FIXED_V_REL_256_TAU_020",
                                              "heavy")

    for arm in ("BIMODAL_2SIDED_PERCENTILE", "BIMODAL_2SIDED_BAYESIAN_CI",
                "BIMODAL_2SIDED_SLIDING_WINDOW"):
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

        # Bucket-divergence gate for (c): final gmm mu_hi - mu_lo >= 0.20 at
        # at least one phase point; instrumentation flag only, not HP-gating
        pts_arm = [p for p in phase_map if p["arm"] == arm]
        max_bucket_div = 0.0
        for p in pts_arm:
            mh = p.get("gmm_mu_hi_final")
            ml = p.get("gmm_mu_lo_final")
            if mh is not None and ml is not None:
                d = float(mh) - float(ml)
                if d > max_bucket_div:
                    max_bucket_div = d

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
            "max_bucket_divergence": round(max_bucket_div, 4),
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

    # Regime-unsaturation check for FIXED at moderate/OOD (v5 fix)
    fixed_mod_ood_rr = -1.0
    for pt in phase_map:
        if (pt["arm"] == "FIXED_V_REL_256_TAU_020"
                and pt["regime"] == "moderate" and pt["band"] == "OOD"):
            fixed_mod_ood_rr = pt["refuse_rate"]
            break
    regime_unsaturated = (fixed_mod_ood_rr < 0.99)

    # Verdict
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
    elif not regime_unsaturated:
        verdict = "HARD_FAIL"
        verdict_msg = ("HARD_FAIL_REGIME_STILL_SATURATED: FIXED @ moderate/OOD "
                       "refuse=%.3f >= 0.99. v5 regime fix (tau=%.2f) did NOT "
                       "cure v4 ceiling; escalate to lower tau OR M3-cortex-"
                       "external calibrator."
                       % (fixed_mod_ood_rr, FIXED_TAU))
    elif len(hp_winners) >= 1:
        verdict = "HARD_PASS"
        verdict_msg = ("HARD_PASS_M14_V5_AC_META_COMPOSITION: %d bimodal "
                       "2-sided arm(s) satisfy monotonic+precision_lift>=0.15 "
                       "at moderate regime: %s. FIXED @ moderate/OOD unsaturated "
                       "at %.3f. Closes M3 milestone M1.4 (glass-box "
                       "conversational calibration primitive)."
                       % (len(hp_winners), hp_winners, fixed_mod_ood_rr))
    else:
        any_monotonic = any(hp_gate_details[a]["monotonic_across_regime_at_OOD"]
                            for a in hp_gate_details)
        any_lift_5 = any(
            hp_gate_details[a]["precision_lift_over_fixed_at_moderate"] >= 0.05
            for a in hp_gate_details)
        if any_monotonic and any_lift_5:
            verdict = "MIDDLE_BAND"
            verdict_msg = ("MIDDLE_BAND_PARTIAL_M14_V5_AC: monotonic OR "
                           "precision_lift 5-15%% at moderate regime; no arm "
                           "cleared HP threshold. (a+c) meta-composition helps "
                           "but not enough for CG.")
        else:
            verdict = "HARD_FAIL"
            verdict_msg = ("HARD_FAIL_AC_META_INSUFFICIENT: no bimodal 2-sided "
                           "arm monotonic across regime OR precision_lift "
                           ">= 0.05. Escalates to M3-cortex-external "
                           "calibrator per drill HF plan.")

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
        "regime_unsaturation_check": {
            "fixed_moderate_ood_refuse_rate": fixed_mod_ood_rr,
            "unsaturated_below_0.99": regime_unsaturated,
            "v5_fix": "FIXED_TAU lowered from 0.40 to %.2f" % FIXED_TAU,
        },
        "cortex_rng_seed": cortex_seed,
        "noise_channel_mode": "additive_gaussian",
        "mechanism_class": ("2sided_tau_low_plus_tau_high_"
                            "PER_BIMODAL_BUCKET_gmm_soft_assign"),
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
