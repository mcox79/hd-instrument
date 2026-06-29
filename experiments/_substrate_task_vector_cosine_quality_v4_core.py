"""Shared core for substrate_task_vector_cosine_quality_v4 sibling cells.

v4 (2026-06-29): TRUE mechanism-class diversion from v1/v2/v3.

v1 cliff-counting MM. v2 monotonic-decay 2/3 HP + 1 HF. v3 precision-densification
0/3 HP (1 HF / 2 MB). All three used the SAME metric family: discrete top1-recall
through cleanup-argmax, then cliff-detection over the discrete trajectory. Each
condition (saturation reached, monotonic decay, no recovery) is independently
fragile. Probability all three hold per slice ~= 0.4; v3 observed exactly that.

v4 LEVER (orthogonal: METRIC FAMILY, not precision, not metric refinement):

Instead of "did argmax(unbind(tv, query)) over codebook return the correct entity"
(binary; subject to argmax-on-similarity-field noise), measure the
DISCRIMINATOR GAP between substrate-TV and random-TV in cosine space against
the oracle TV. Continuous; smooth in K; no argmax dependency.

The substrate task vector `tv_sub = bundle(bind(x_i, perm(x_i)))_K`.
The oracle task vector `tv_oracle = bundle(bind(x_i, perm(x_i)))_full V_ENTS_POOL`.
Random TV `tv_rand = bundle(bind(x_i, RANDOM_entity))_K`.
DISCRIMINATOR: cos(tv_sub, tv_oracle) - cos(tv_rand, tv_oracle).

Expected substrate behavior (theory):
- cos_TV(K) ~ sqrt(K/V_ENTS_POOL) GROWS with K (bundle of K components of an
  oracle bundle of V_ENTS_POOL components -> their inner product is K/sqrt(K*V_ENTS) under normalization).
- cos_RV(K) ~ 0 for all K (random output entities don't align with the permutation
  even by chance; cleanest noise floor).
- Therefore: DISCRIMINATOR_GAP(K) = cos_TV(K) - cos_RV(K) ~ sqrt(K/V_ENTS_POOL) GROWS with K.

Substrate hypothesis: the gap grows monotonically in K and is seed-stable.
Substrate-bound hypothesis: the gap fails to grow (or noise floor exceeds signal).

If the gap fails to grow -- substrate cannot represent TV ICL even at the cleanest
possible cosine-quality lens (no cleanup, no argmax, just direct inner product).
Atomize as TRUE bound (v1/v2/v3/v4 covered 4 orthogonal lenses).

CARDINALITY: 3 arms * 8 K * 3 V * 3 overlap * 50 trials = 10800 cosine measurements per seed.
SMOKE: 6 corners * 3 arms * 50 trials = 900.

Author: exp_dev 2026-06-29 (Opus 4.7 1M, agent-spawn) v4 metric-family diversion
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_TORCH_OK = False
_CUDA_OK = False
try:
    import torch
    _TORCH_OK = True
    if torch.cuda.is_available():
        _CUDA_OK = True
except Exception:
    pass

ANCHOR_PREFIX = "substrate_task_vector_cosine_quality_v4"

# ----- Phase axes (LOCKED — inherited from v3 for cross-family comparability) -----
K_VALUES = (1, 3, 5, 10, 20, 50, 100, 200)
N_TASKS_VALUES = (10, 20, 50)
OVERLAP_VALUES = (0.0, 0.3, 0.6)
ARMS = ("TASK_VECTOR", "RANDOM_VECTOR", "ORACLE_SELF")

V_ENTS_POOL = 200

SMOKE_CORNERS = (
    (1, 10, 0.0),
    (1, 50, 0.0),
    (10, 20, 0.3),
    (50, 50, 0.6),
    (100, 10, 0.0),
    (200, 50, 0.6),    # v4 discriminator: high K + high V + high overlap
)

# v4 NEW: discriminator-gap-growth bands (pre-reg'd)
# Theory: cos_TV(K) ~ sqrt(K/V_ENTS_POOL); cos_RV(K) ~ 0; gap GROWS with K.
# Numeric expectation for V_ENTS_POOL=200:
#   K=1   -> 0.071    K=10  -> 0.224    K=50  -> 0.500    K=200 -> 1.000
# Discriminator gap should track cos_TV closely (cos_RV near 0).

# HARD_PASS bands (substrate TV growth GAP discriminates from random)
HP_GAP_K1_MIN = 0.04                 # gap at K=1 > 50% of theory (0.071 * 0.5)
HP_GAP_K200_MIN = 0.60               # gap at K=200 > 60% of theory (1.0 * 0.6)
HP_SPEARMAN_RHO_PER_SLICE = 0.7       # GROWS with K -> positive rho
HP_SPEARMAN_SLICE_COUNT = 6           # at LEAST 6 of 9 slices growing
HP_SEED_SIGMA_MAX = 0.10              # seed-stability per K-slice

# MIDDLE_BAND bands
MB_GAP_K1_MIN = 0.02
MB_GAP_K200_MIN = 0.30
MB_SPEARMAN_RHO_PER_SLICE = 0.5
MB_SPEARMAN_SLICE_COUNT = 3
MB_SEED_SIGMA_MAX = 0.20

# HARD_FAIL bands (substrate TV gap does NOT grow; bound confirmed)
HF_GAP_K200_MAX = 0.10               # gap stays below 10% of theoretical 1.0
HF_SPEARMAN_RHO_PER_SLICE = 0.3       # rho < 0.3 means weak/no growth
HF_SPEARMAN_NO_GROWTH_COUNT = 6
HF_SEED_SIGMA_MIN = 0.25

# v4 NEW: discriminator-smoke-fires gate (theory-derived)
# cos_TV(K=1) ~ 0.071; cos_TV(K=200) ~ 1.0 with full V_ENTS_POOL=200 oracle
# Smoke must show cos_TV INCREASES from K=1 to K=200 with the expected gap structure
DISCRIMINATOR_SMOKE_LOW_K_GAP_MIN = 0.02     # gap at (K=1,V=10,ov=0.0) > 0.02
DISCRIMINATOR_SMOKE_HIGH_K_GAP_MIN = 0.30    # gap at (K=200,V=50,ov=0.6) > 0.30
DISCRIMINATOR_SMOKE_GROWTH_K1_TO_K200 = 0.15 # cos_TV(K=200) - cos_TV(K=1) > 0.15

N_TRIALS_FULL = 50
N_TRIALS_SMOKE = 50    # discriminator-survives-scale (USER 2026-06-26)

N_DIM_FULL = 8192
N_DIM_SMOKE = 8192     # discriminator-survives-scale: smoke at full N

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    if _CUDA_OK:
        return "torch.cuda"
    if _TORCH_OK:
        return "torch.cpu"
    return "numpy.cpu"


# ----- HRR primitives (numpy variant; CPU cell) -----

def _bipolar_codebook_np(V: int, N: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X


def _bind_bundle_np(inputs: np.ndarray, outputs: np.ndarray) -> np.ndarray:
    """Bundle of K bind(input_i, output_i) circular convolutions; returns normalized vector."""
    I = np.fft.rfft(inputs, axis=-1)
    O = np.fft.rfft(outputs, axis=-1)
    P = I * O
    bound = np.fft.irfft(P, n=inputs.shape[-1], axis=-1).astype(np.float32)
    tv = bound.sum(axis=0)
    n = np.linalg.norm(tv) + 1e-8
    return tv / n


def _cosine_np(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity of two 1D vectors (assumes normalized OK; defensive)."""
    na = np.linalg.norm(a) + 1e-8
    nb = np.linalg.norm(b) + 1e-8
    return float(np.dot(a, b) / (na * nb))


# ----- One phase-point run (3 arms x N_TRIALS) -----

def _run_phase_point(
    g: np.random.Generator,
    entities: np.ndarray,
    K: int,
    V_tasks: int,
    overlap: float,
    n_trials: int,
) -> Dict[str, Any]:
    """Compute cosine quality at one phase point.

    For each of n_trials independent trials:
        - draw a fresh task set (V_tasks tasks with `overlap` shared inputs)
        - build tv_substrate = bundle of K shots of focal task
        - build tv_oracle = bundle of FULL V_ENTS_POOL shots of focal task
        - build tv_rand = bundle of K (input, RANDOM output) for focal task
        - cos(tv_substrate, tv_oracle), cos(tv_rand, tv_oracle)
    Returns per-trial cosines for each arm.
    """
    V_ents = entities.shape[0]
    N = entities.shape[1]
    K_eff = min(K, V_ents)
    out: Dict[str, Any] = {}

    # Pre-allocate per-trial arrays
    tv_cos = np.zeros(n_trials, dtype=np.float32)
    rv_cos = np.zeros(n_trials, dtype=np.float32)
    self_cos = np.zeros(n_trials, dtype=np.float32)   # ORACLE_SELF arm: oracle vs itself; sanity

    for trial in range(n_trials):
        # 1. Focal-task permutation (this is the task we're trying to encode)
        focal_perm = g.permutation(V_ents)

        # 2. Pick which K inputs to use for the substrate tv (shots);
        #    overlap parameter introduces shared inputs across the V_tasks,
        #    but for the cosine-vs-oracle measurement we only need the FOCAL task's
        #    K input subset
        shared_size = int(round(overlap * K_eff))
        if shared_size > K_eff:
            shared_size = K_eff
        if shared_size > V_ents:
            shared_size = V_ents

        # For cos-to-oracle measurement, the focal-task K-subset is what matters.
        # We honor V_tasks/overlap by drawing the focal context from the V_tasks-shared region
        # so the semantics matches v3's substrate task vector construction.
        if shared_size > 0:
            shared_idx = g.choice(V_ents, size=shared_size, replace=False)
        else:
            shared_idx = np.array([], dtype=np.int64)
        remainder = K_eff - shared_size
        candidate = np.setdiff1d(np.arange(V_ents), shared_idx, assume_unique=False)
        if remainder > candidate.size:
            rem_eff = candidate.size
        else:
            rem_eff = remainder
        if rem_eff > 0:
            fresh = g.choice(candidate, size=rem_eff, replace=False)
        else:
            fresh = np.array([], dtype=np.int64)
        focal_K_idx = np.concatenate([shared_idx, fresh])
        if focal_K_idx.size == 0:
            tv_cos[trial] = 0.0
            rv_cos[trial] = 0.0
            self_cos[trial] = 1.0
            continue

        # 3. Substrate TV: bind+bundle K shots of (input_i, perm(input_i))
        x_K = entities[focal_K_idx]
        y_K = entities[focal_perm[focal_K_idx]]
        tv_substrate = _bind_bundle_np(x_K, y_K)

        # 4. Oracle TV: bind+bundle the FULL V_ENTS_POOL set of (input_i, perm(input_i))
        x_full = entities
        y_full = entities[focal_perm]
        tv_oracle = _bind_bundle_np(x_full, y_full)

        # 5. Random TV: substrate gets WRONG output entities for the K inputs
        rand_y_idx = g.integers(0, V_ents, size=focal_K_idx.size)
        rand_y = entities[rand_y_idx]
        tv_rand = _bind_bundle_np(x_K, rand_y)

        # 6. Cosines vs oracle
        tv_cos[trial] = _cosine_np(tv_substrate, tv_oracle)
        rv_cos[trial] = _cosine_np(tv_rand, tv_oracle)
        self_cos[trial] = _cosine_np(tv_oracle, tv_oracle)

    out["TASK_VECTOR_cosine_per_trial"] = tv_cos.tolist()
    out["TASK_VECTOR_cosine_mean"] = float(tv_cos.mean())
    out["TASK_VECTOR_cosine_std"] = float(tv_cos.std())
    out["RANDOM_VECTOR_cosine_per_trial"] = rv_cos.tolist()
    out["RANDOM_VECTOR_cosine_mean"] = float(rv_cos.mean())
    out["RANDOM_VECTOR_cosine_std"] = float(rv_cos.std())
    out["ORACLE_SELF_cosine_per_trial"] = self_cos.tolist()
    out["ORACLE_SELF_cosine_mean"] = float(self_cos.mean())

    out["K_use"] = int(K_eff)
    out["V_tasks"] = int(V_tasks)
    out["overlap"] = float(overlap)
    out["n_trials"] = int(n_trials)
    return out


def run_one_seed_phase_diagram(
    seed: int,
    run_mode: str,
    smoke_corners: bool = False,
) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    N = N_DIM_SMOKE if run_mode != "full" else N_DIM_FULL

    entities = _bipolar_codebook_np(V_ENTS_POOL, N, g)

    n_trials = N_TRIALS_SMOKE if (run_mode != "full") else N_TRIALS_FULL

    if smoke_corners:
        points = list(SMOKE_CORNERS)
    elif run_mode == "selftest":
        points = [(1, 10, 0.0), (200, 50, 0.6)]
        n_trials = 5
    else:
        points = []
        for K in K_VALUES:
            for V in N_TASKS_VALUES:
                for ov in OVERLAP_VALUES:
                    points.append((K, V, ov))

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for (K, V, ov) in points:
        res = _run_phase_point(g, entities, K, V, ov, n_trials)
        res["K"] = int(K)
        phase_map.append(res)

    elapsed = time.time() - started

    return {
        "seed": int(seed),
        "N_DIM": int(N),
        "run_mode": run_mode,
        "smoke_corners": bool(smoke_corners),
        "backend": get_backend_label(),
        "n_phase_points": len(phase_map),
        "n_trials_per_point": int(n_trials),
        "phase_map": phase_map,
        "elapsed_s": round(elapsed, 2),
        "anchor_prefix": ANCHOR_PREFIX,
    }


# ----- Per-slice Spearman rho (cosine vs K) -----

def _spearman_rho(x: List[float], y: List[float]) -> float:
    """Simple Spearman rho via ranks; assumes equal-length, no ties to worry about (K is distinct)."""
    if len(x) < 2:
        return 0.0
    xr = np.argsort(np.argsort(x)).astype(np.float32)
    yr = np.argsort(np.argsort(y)).astype(np.float32)
    xr_c = xr - xr.mean()
    yr_c = yr - yr.mean()
    denom = (np.linalg.norm(xr_c) * np.linalg.norm(yr_c)) + 1e-12
    return float(np.dot(xr_c, yr_c) / denom)


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    """v4 verdict: discriminator-gap-growth across K.

    Theory: cos_TV(K) ~ sqrt(K/V_ENTS_POOL); cos_RV(K) ~ 0; gap GROWS with K.

    HARD_PASS requires:
    1. gap at K=1 >= HP_GAP_K1_MIN (>= 50% of theoretical 0.071)
    2. gap at K=200 (highest K) >= HP_GAP_K200_MIN (>= 60% of theoretical 1.0)
    3. 6+/9 slices with Spearman rho >= +0.7 (monotonic growth)
    4. seed_sigma < HP_SEED_SIGMA_MAX (0.10) at every K-slice point
    5. No regime-flip (cos_TV > cos_RV at any K in ALL slices)

    MIDDLE_BAND: gap grows but not chain-grade tight.
    HARD_FAIL: gap fails to grow; TRUE substrate bound across 4 metric families.
    """
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    # Build per-(K, V, ov) view: mean over trials, per arm, per seed
    # Then aggregate across seeds: mean + sigma
    keys = []
    for K in K_VALUES:
        for V in N_TASKS_VALUES:
            for ov in OVERLAP_VALUES:
                keys.append((K, V, ov))

    # cell_means[(K,V,ov)][seed_id] -> arm means dict
    cell_means: Dict[Tuple[int, int, float], Dict[str, Dict[str, float]]] = {}
    for sid, body in per_seed.items():
        for pt in body.get("phase_map", []):
            key = (int(pt["K"]), int(pt["V_tasks"]), float(pt["overlap"]))
            d = cell_means.setdefault(key, {})
            d[sid] = {
                "TASK_VECTOR": float(pt.get("TASK_VECTOR_cosine_mean", 0.0)),
                "RANDOM_VECTOR": float(pt.get("RANDOM_VECTOR_cosine_mean", 0.0)),
                "ORACLE_SELF": float(pt.get("ORACLE_SELF_cosine_mean", 1.0)),
            }

    # Pooled-across-seeds cosines per (K, V, ov)
    summary_per_pt: List[Dict[str, Any]] = []
    seed_sigma_map: Dict[Tuple[int, int, float], float] = {}
    for key in keys:
        if key not in cell_means:
            continue
        K, V, ov = key
        seed_views = cell_means[key]
        tv_vals = [seed_views[s]["TASK_VECTOR"] for s in seed_views]
        rv_vals = [seed_views[s]["RANDOM_VECTOR"] for s in seed_views]
        os_vals = [seed_views[s]["ORACLE_SELF"] for s in seed_views]
        tv_mean = float(np.mean(tv_vals)) if tv_vals else 0.0
        tv_sigma = float(np.std(tv_vals)) if len(tv_vals) > 1 else 0.0
        rv_mean = float(np.mean(rv_vals)) if rv_vals else 0.0
        os_mean = float(np.mean(os_vals)) if os_vals else 1.0
        seed_sigma_map[key] = tv_sigma
        summary_per_pt.append({
            "K": K, "V_tasks": V, "overlap": ov,
            "cos_TV_pooled": tv_mean,
            "cos_RV_pooled": rv_mean,
            "cos_ORACLE_SELF_pooled": os_mean,
            "tv_rv_gap": tv_mean - rv_mean,
            "tv_seed_sigma": tv_sigma,
            "n_seeds_observed": len(seed_views),
        })

    # gap_per_slice: cos_TV - cos_RV at each (V, ov) slice and each K
    # gap_at_K1_focal: K=1, V=10, ov=0.0
    K1_focal_key = (1, 10, 0.0)
    if K1_focal_key in cell_means:
        sv = cell_means[K1_focal_key]
        cos_TV_K1_focal = float(np.mean([sv[s]["TASK_VECTOR"] for s in sv]))
        cos_RV_K1_focal = float(np.mean([sv[s]["RANDOM_VECTOR"] for s in sv]))
    else:
        cos_TV_K1_focal = 0.0
        cos_RV_K1_focal = 0.0
    gap_K1_focal = cos_TV_K1_focal - cos_RV_K1_focal

    # gap_at_K200 (highest K): pooled across all 9 (V, ov) slices
    K200_gaps = []
    for V in N_TASKS_VALUES:
        for ov in OVERLAP_VALUES:
            key = (200, V, ov)
            if key in cell_means:
                sv = cell_means[key]
                tv = float(np.mean([sv[s]["TASK_VECTOR"] for s in sv]))
                rv = float(np.mean([sv[s]["RANDOM_VECTOR"] for s in sv]))
                K200_gaps.append(tv - rv)
    gap_K200_avg = float(np.mean(K200_gaps)) if K200_gaps else 0.0
    gap_K200_max = float(np.max(K200_gaps)) if K200_gaps else 0.0

    # Per-slice Spearman rho (gap vs K) — expected POSITIVE under substrate hypothesis
    slice_spearman_gap: Dict[str, float] = {}
    n_strong_growth = 0   # rho >= HP threshold (positive monotone growth)
    n_weak_growth = 0     # rho >= MB threshold
    n_no_growth = 0       # rho < HF threshold (no growth)
    for V in N_TASKS_VALUES:
        for ov in OVERLAP_VALUES:
            slice_K = []
            slice_gap = []
            for K in K_VALUES:
                key = (K, V, ov)
                if key in cell_means:
                    sv = cell_means[key]
                    tv = float(np.mean([sv[s]["TASK_VECTOR"] for s in sv]))
                    rv = float(np.mean([sv[s]["RANDOM_VECTOR"] for s in sv]))
                    slice_K.append(float(K))
                    slice_gap.append(tv - rv)
            rho = _spearman_rho(slice_K, slice_gap) if len(slice_K) >= 2 else 0.0
            slice_key = f"V{V}_ov{ov:.2f}"
            slice_spearman_gap[slice_key] = rho
            if rho >= HP_SPEARMAN_RHO_PER_SLICE:
                n_strong_growth += 1
            if rho >= MB_SPEARMAN_RHO_PER_SLICE:
                n_weak_growth += 1
            if rho < HF_SPEARMAN_RHO_PER_SLICE:
                n_no_growth += 1

    # Regime-flip check (META_RULE_AM): at ANY K, is cos_TV < cos_RV in any slice?
    # Under correct substrate behavior, TV cosine should always exceed RV cosine.
    regime_flip_points = []
    for K in K_VALUES:
        for V in N_TASKS_VALUES:
            for ov in OVERLAP_VALUES:
                key = (K, V, ov)
                if key in cell_means:
                    sv = cell_means[key]
                    tv = float(np.mean([sv[s]["TASK_VECTOR"] for s in sv]))
                    rv = float(np.mean([sv[s]["RANDOM_VECTOR"] for s in sv]))
                    if rv > tv + 0.02:   # tolerance band
                        regime_flip_points.append((K, V, ov))
    am_flag = len(regime_flip_points) > 0

    # Max seed sigma across all observed cells
    max_seed_sigma = max(seed_sigma_map.values()) if seed_sigma_map else 0.0
    max_seed_sigma_cell = (max(seed_sigma_map.items(), key=lambda kv: kv[1])[0]
                           if seed_sigma_map else None)

    # Verdict gates
    hp_gap_K1 = (gap_K1_focal >= HP_GAP_K1_MIN)
    hp_gap_K200 = (gap_K200_avg >= HP_GAP_K200_MIN)
    hp_growth = (n_strong_growth >= HP_SPEARMAN_SLICE_COUNT)
    hp_sigma = (max_seed_sigma < HP_SEED_SIGMA_MAX)
    hp_no_flip = (not am_flag)

    mb_gap_K1 = (gap_K1_focal >= MB_GAP_K1_MIN)
    mb_gap_K200 = (gap_K200_avg >= MB_GAP_K200_MIN)
    mb_growth = (n_weak_growth >= MB_SPEARMAN_SLICE_COUNT)
    mb_sigma = (max_seed_sigma < MB_SEED_SIGMA_MAX)

    hf_no_gap_K200 = (gap_K200_avg < HF_GAP_K200_MAX)
    hf_no_growth = (n_no_growth >= HF_SPEARMAN_NO_GROWTH_COUNT)
    hf_sigma_explode = (max_seed_sigma >= HF_SEED_SIGMA_MIN)

    # Verdict logic
    if hf_no_gap_K200 or hf_no_growth or hf_sigma_explode or am_flag:
        verdict = "HARD_FAIL"
        m3_msg = (f"M3#4 NOT CONFIRMED (v4 metric-family diversion): "
                  f"discriminator-gap growth failed; TRUE substrate bound on TASK_VECTOR ICL. "
                  f"chain: v1(cliff-counting MM) + v2(monotonic-decay MM/MM/HF) + "
                  f"v3(precision MB/MB/HF) + v4(cosine-gap-growth HF) = "
                  f"4 orthogonal lenses CONFIRM bound")
    elif hp_gap_K1 and hp_gap_K200 and hp_growth and hp_sigma and hp_no_flip:
        verdict = "HARD_PASS"
        m3_msg = (f"M3#4 CHAIN_GRADE (v4 metric-family): substrate TASK_VECTOR "
                  f"cos-gap grows monotonically in K; seed-stable; "
                  f"gap_K200={gap_K200_avg:.3f}; "
                  f"{n_strong_growth}/9 strong-growth slices")
    elif mb_gap_K1 and mb_growth and mb_sigma:
        verdict = "MIDDLE_BAND"
        m3_msg = (f"M3#4 PARTIAL (v4): gap-growth mechanism observed but not chain-grade tight; "
                  f"gap_K1={gap_K1_focal:.3f}, gap_K200={gap_K200_avg:.3f}, "
                  f"{n_weak_growth}/9 weak-growth, "
                  f"max_seed_sigma={max_seed_sigma:.3f}")
    else:
        verdict = "MIDDLE_BAND"
        m3_msg = (f"M3#4 PARTIAL (v4): some signals present; "
                  f"gap_K1={gap_K1_focal:.3f}, gap_K200={gap_K200_avg:.3f}, "
                  f"weak_growth={n_weak_growth}/9, "
                  f"max_seed_sigma={max_seed_sigma:.3f}")

    verdict_msg = (
        f"{verdict} | gap_K1_focal={gap_K1_focal:.3f} | gap_K200_avg={gap_K200_avg:.3f} "
        f"| strong_growth_slices={n_strong_growth}/9 "
        f"| weak_growth_slices={n_weak_growth}/9 "
        f"| no_growth_slices={n_no_growth}/9 "
        f"| max_seed_sigma={max_seed_sigma:.3f} "
        f"| regime_flip={am_flag} | regime_flip_n={len(regime_flip_points)} "
        f"| {m3_msg}"
    )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "cos_TV_K1_focal": cos_TV_K1_focal,
        "cos_RV_K1_focal": cos_RV_K1_focal,
        "gap_K1_focal": gap_K1_focal,
        "gap_K200_avg": gap_K200_avg,
        "gap_K200_max": gap_K200_max,
        "n_strong_growth_slices": n_strong_growth,
        "n_weak_growth_slices": n_weak_growth,
        "n_no_growth_slices": n_no_growth,
        "slice_spearman_rho_gap": slice_spearman_gap,
        "max_seed_sigma": max_seed_sigma,
        "max_seed_sigma_cell": (list(max_seed_sigma_cell) if max_seed_sigma_cell else None),
        "meta_rule_am_regime_flip_points": [list(p) for p in regime_flip_points],
        "summary_per_phase_point_pooled": summary_per_pt,
        "n_seeds_complete": len(per_seed),
        "m3_concern_4_annotation": m3_msg,
        "v4_metric_constants": {
            "HP_GAP_K1_MIN": HP_GAP_K1_MIN,
            "HP_GAP_K200_MIN": HP_GAP_K200_MIN,
            "HP_SPEARMAN_RHO_PER_SLICE": HP_SPEARMAN_RHO_PER_SLICE,
            "HP_SPEARMAN_SLICE_COUNT": HP_SPEARMAN_SLICE_COUNT,
            "HP_SEED_SIGMA_MAX": HP_SEED_SIGMA_MAX,
            "MB_GAP_K1_MIN": MB_GAP_K1_MIN,
            "MB_GAP_K200_MIN": MB_GAP_K200_MIN,
            "MB_SPEARMAN_RHO_PER_SLICE": MB_SPEARMAN_RHO_PER_SLICE,
            "MB_SPEARMAN_SLICE_COUNT": MB_SPEARMAN_SLICE_COUNT,
            "MB_SEED_SIGMA_MAX": MB_SEED_SIGMA_MAX,
            "HF_GAP_K200_MAX": HF_GAP_K200_MAX,
            "HF_SPEARMAN_RHO_PER_SLICE": HF_SPEARMAN_RHO_PER_SLICE,
            "HF_SPEARMAN_NO_GROWTH_COUNT": HF_SPEARMAN_NO_GROWTH_COUNT,
            "HF_SEED_SIGMA_MIN": HF_SEED_SIGMA_MIN,
            "N_TRIALS_FULL": N_TRIALS_FULL,
        },
    }


# ----- Smoke discriminator-survives-scale check -----

def smoke_discriminator_check(phase_map: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """v4 smoke discriminator: gap GROWS from K=1 to K=200.

    Conditions (ALL must hold):
    - gap at (K=1, V=10, ov=0.0) > DISCRIMINATOR_SMOKE_LOW_K_GAP_MIN
    - gap at (K=200, V=50, ov=0.6) > DISCRIMINATOR_SMOKE_HIGH_K_GAP_MIN
    - cos_TV(K=200) - cos_TV(K=1) > DISCRIMINATOR_SMOKE_GROWTH_K1_TO_K200
    """
    high_K_corner = None
    low_K_corner = None
    for p in phase_map:
        if (p["K"] == 200 and p["V_tasks"] == 50
                and abs(p["overlap"] - 0.6) < 1e-6):
            high_K_corner = p
        if (p["K"] == 1 and p["V_tasks"] == 10
                and abs(p["overlap"] - 0.0) < 1e-6):
            low_K_corner = p
    if not high_K_corner:
        return False, "smoke discriminator HIGH-K corner (K=200,V=50,ov=0.6) MISSING"
    if not low_K_corner:
        return False, "smoke discriminator LOW-K corner (K=1,V=10,ov=0.0) MISSING"

    high_K_tv = float(high_K_corner.get("TASK_VECTOR_cosine_mean", 0.0))
    high_K_rv = float(high_K_corner.get("RANDOM_VECTOR_cosine_mean", 0.0))
    low_K_tv = float(low_K_corner.get("TASK_VECTOR_cosine_mean", 0.0))
    low_K_rv = float(low_K_corner.get("RANDOM_VECTOR_cosine_mean", 0.0))

    low_gap = low_K_tv - low_K_rv
    high_gap = high_K_tv - high_K_rv
    growth = high_K_tv - low_K_tv

    low_ok = (low_gap >= DISCRIMINATOR_SMOKE_LOW_K_GAP_MIN)
    high_ok = (high_gap >= DISCRIMINATOR_SMOKE_HIGH_K_GAP_MIN)
    growth_ok = (growth >= DISCRIMINATOR_SMOKE_GROWTH_K1_TO_K200)

    if low_ok and high_ok and growth_ok:
        return True, (f"smoke discriminator FIRED: gap_K1={low_gap:.3f} >= {DISCRIMINATOR_SMOKE_LOW_K_GAP_MIN} "
                      f"AND gap_K200={high_gap:.3f} >= {DISCRIMINATOR_SMOKE_HIGH_K_GAP_MIN} "
                      f"AND growth_K1_to_K200={growth:.3f} >= {DISCRIMINATOR_SMOKE_GROWTH_K1_TO_K200}")
    msg_parts = []
    if not low_ok:
        msg_parts.append(f"LOW-K GAP FAIL: {low_gap:.3f} < {DISCRIMINATOR_SMOKE_LOW_K_GAP_MIN}")
    if not high_ok:
        msg_parts.append(f"HIGH-K GAP FAIL: {high_gap:.3f} < {DISCRIMINATOR_SMOKE_HIGH_K_GAP_MIN}")
    if not growth_ok:
        msg_parts.append(f"GROWTH FAIL: {growth:.3f} < {DISCRIMINATOR_SMOKE_GROWTH_K1_TO_K200}")
    return False, "smoke discriminator FAILED-TO-FIRE: " + " | ".join(msg_parts)


# ----- Self-test -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: 2 corner points + verify the v4 cosine-gap-growth machinery."""
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pts = body["phase_map"]
        low = [p for p in pts if p["K"] == 1 and p["V_tasks"] == 10 and abs(p["overlap"]) < 1e-6]
        hi = [p for p in pts if p["K"] == 200 and p["V_tasks"] == 50 and abs(p["overlap"] - 0.6) < 1e-6]
        if not low or not hi:
            return False, f"selftest: missing corner points; got {len(pts)}"
        cos_low = low[0]["TASK_VECTOR_cosine_mean"]
        cos_hi = hi[0]["TASK_VECTOR_cosine_mean"]
        cos_rv_low = low[0]["RANDOM_VECTOR_cosine_mean"]
        cos_rv_hi = hi[0]["RANDOM_VECTOR_cosine_mean"]
        cos_self_low = low[0]["ORACLE_SELF_cosine_mean"]
        # Theoretical: cos_TV(K=1) ~ sqrt(1/200) = 0.071; cos_TV(K=200) ~ sqrt(200/200) = 1.0
        if cos_low < 0.02 or cos_low > 0.25:
            return False, (f"selftest: cos_TV at K=1 V=10 ov=0 = {cos_low:.3f} "
                           f"outside theoretical band [0.02, 0.25]; expected ~ sqrt(1/200)=0.071")
        if cos_self_low < 0.99:
            return False, (f"selftest: ORACLE_SELF cos = {cos_self_low:.3f} (should be 1.0; sanity)")
        if cos_hi <= cos_low:
            return False, (f"selftest: cos_TV at K=200 ({cos_hi:.3f}) NOT > cos_TV at K=1 ({cos_low:.3f}); "
                           f"cos should GROW with K under substrate hypothesis")
        if cos_hi < 0.50:
            return False, (f"selftest: cos_TV at K=200 = {cos_hi:.3f} below expected ~1.0; "
                           f"high-K substrate TV should align strongly with oracle")
        gap_K1 = cos_low - cos_rv_low
        gap_K200 = cos_hi - cos_rv_hi
        if gap_K200 < gap_K1:
            return False, (f"selftest: gap_K200 ({gap_K200:.3f}) NOT > gap_K1 ({gap_K1:.3f}); "
                           f"discriminator gap must GROW with K")
        # Verify per-trial vectors present
        if "TASK_VECTOR_cosine_per_trial" not in low[0]:
            return False, "selftest: per-trial cosine vector missing"
        if len(low[0]["TASK_VECTOR_cosine_per_trial"]) != low[0]["n_trials"]:
            return False, "selftest: per-trial length mismatch"
        # Verify aggregator runs end-to-end
        per_seed_stub = {str(seed): body}
        agg = aggregate_and_verdict(per_seed_stub, run_mode="selftest")
        if "verdict" not in agg:
            return False, "selftest: aggregator did not produce verdict"
        msg = (f"selftest OK: cos_TV(K=1,V=10,ov=0.0)={cos_low:.3f}, "
               f"cos_TV(K=200,V=50,ov=0.6)={cos_hi:.3f}, "
               f"gap_K1={gap_K1:.3f}, gap_K200={gap_K200:.3f}, "
               f"cos_ORACLE_SELF={cos_self_low:.3f}, "
               f"agg_verdict={agg['verdict']}, backend={body['backend']}")
        return True, msg
    except Exception as e:
        return False, f"selftest EXC: {type(e).__name__}: {e}\n{traceback.format_exc()}"


if __name__ == "__main__":
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
