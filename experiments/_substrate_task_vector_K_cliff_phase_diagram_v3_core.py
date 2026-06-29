"""Shared core for substrate_task_vector_K_cliff_phase_diagram_v3 sibling cells.

v3 REVISION (2026-06-28): Cliff-PRECISION mechanism-class diversion of v2.

v2 (2026-06-28) FIXED the metric artifact (monotonic-decay required from
saturation) and produced 2/3 HARD_PASS + 1 HARD_FAIL (seed_13 regime_flip:
TV<RV at K=1, V=20, ov=0.0). Skunkworks 2x-drill diagnosed the seed_13
disagreement as Bernoulli sampling noise: per-cell stdev ~0.15 with n=10
queries -- across 9 (V,overlap) slices, different seeds find different cliff
slices because slice-winner ordering is dominated by sampling noise rather
than substrate signal. Cliff EXISTS but its LOCATION is unstable at v2 measurement
precision.

v3 LEVER (orthogonal to v2 metric lever): how PRECISELY we measure each cell,
not what we measure. Inherit v2's monotonic-decay metric unchanged.

v3 CHANGES (mechanism-class):

1. N_QUERIES per (slice, K) point: 10 (v2) -> 50 (v3). By Bernoulli sqrt
   scaling, per-cell stdev drops from ~sqrt(0.25/10)=0.158 to ~sqrt(0.25/50)=0.071
   -- ~2.2x precision improvement at each cell. This makes slice-winner ordering
   substrate-signal dominated rather than noise dominated.

2. POOLED CLIFF DETECTION across all 3 seeds. Instead of computing K_cliff per
   seed (3 separate cliff_min values, then min-of-mins), POOL all queries from
   the 3 seeds into ONE per-(K,V,ov) measurement (n_eff = 3 * 50 = 150 queries
   per cell), then find cliff on the POOLED phase diagram. This is the cleanest
   measurement strategy when sampling noise is the bottleneck.

3. BOOTSTRAP CI on cliff_K_loc. Resample queries with replacement 1000x; for
   each resample, recompute the pooled phase diagram + identify K_cliff_min +
   winning slice. The 95% CI on the winning slice across bootstrap replicates
   is the substantive uncertainty measurement. Chain-grade promotion REQUIRES
   the winning slice be unique (no other slice in 95% CI) AND K_cliff_min CI
   width <= 1 K-grid-step.

4. Inherit V_tasks axis {10, 20, 50}, K axis {1, 3, 5, 10, 20, 50, 100, 200},
   overlap {0.0, 0.3, 0.6}, V_ENTS_POOL=200, N_DIM=8192. Same arms (TASK_VECTOR
   / RANDOM_VECTOR / ORACLE).

EXPECTED OUTCOMES:
- If v2's cliff is real but noise-limited, v3 will SHOW the cliff at the SAME
  (V*, ov*) slice for all bootstrap replicates -> chain-grade promotion candidate.
- If cliff_K_loc CI is wide (multiple slices in 95% CI), that's a substantive
  negative: TASK_VECTOR K-cliff is inherently noisy at substrate scale -> MM
  classification stands, no chain-grade.

POSITIVE CONTROL: v2 seed_7 winning slice was (V=50, ov=0.00) at K_cliff_min=5.
v3 must reproduce this winning slice (or close to it) at higher precision; if v3
identifies a DIFFERENT slice as winner with tight CI, that is the substantive
result (Skunkworks-class refinement of v2 finding).

CARDINALITY: 3 arms * 8 K * 3 V * 3 overlap * 50 queries = 10800 records per seed
SMOKE: 6 corners * 3 arms * 50 queries = 900 records.

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn) v3 cliff-precision drill
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

ANCHOR_PREFIX = "substrate_task_vector_K_cliff_phase_diagram_v3"

# ----- Phase axes (LOCKED — inherited from v2) -----
K_VALUES = (1, 3, 5, 10, 20, 50, 100, 200)
N_TASKS_VALUES = (10, 20, 50)
OVERLAP_VALUES = (0.0, 0.3, 0.6)
ARMS = ("TASK_VECTOR", "RANDOM_VECTOR", "ORACLE")

V_ENTS_POOL = 200

SMOKE_CORNERS = (
    (1, 10, 0.0),
    (1, 50, 0.0),
    (10, 20, 0.3),
    (50, 50, 0.6),
    (100, 10, 0.0),
    (200, 10, 0.0),
)

# Pre-reg bands (mirror prereg .md; LOCKED at module load) — inherited from v2
HP_K1_FLOOR_RECALL = 0.95
HP_CLIFF_FLOOR_RECALL = 0.40
HP_AVG_ARMS_DIFF_MIN = 0.20
MB_AVG_ARMS_DIFF_LO = 0.10
HF_NO_CLIFF_RECALL_MIN = 0.95

K_SAT_THRESHOLD = 0.95
MONOTONIC_RECOVERY_TOL = 0.05
DISCRIMINATOR_SMOKE_FLOOR = 0.40

# v3 NEW: precision constants
N_QUERIES_FULL = 50    # was 10 in v2; ~2.2x stdev reduction
N_QUERIES_SMOKE = 50   # smoke at FULL precision per discriminator-survives-scale (USER 2026-06-26)

# v3 NEW: bootstrap CI parameters
BOOTSTRAP_N_REPLICATES = 1000
BOOTSTRAP_CI_PCT = 95.0
BOOTSTRAP_RNG_SEED = 314159   # fixed for reproducibility

# v3 NEW: chain-grade promotion bands (POOLED across 3 seeds)
CHAIN_GRADE_SLICE_UNIQUENESS = 0.95   # winning slice must appear in >= 95% bootstrap reps
CHAIN_GRADE_K_CLIFF_CI_WIDTH = 1      # K-grid steps; cliff_K CI width must be <= 1 step

N_DIM_FULL = 8192
N_DIM_SMOKE = 8192   # discriminator-survives-scale: smoke at full N

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
    I = np.fft.rfft(inputs, axis=-1)
    O = np.fft.rfft(outputs, axis=-1)
    P = I * O
    bound = np.fft.irfft(P, n=inputs.shape[-1], axis=-1).astype(np.float32)
    tv = bound.sum(axis=0)
    n = np.linalg.norm(tv) + 1e-8
    return tv / n


def _unbind_np(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    C = np.fft.rfft(c)
    A = np.fft.rfft(a)
    R = C * np.conj(A)
    return np.fft.irfft(R, n=c.shape[-1]).astype(np.float32)


# ----- One phase-point run (3 arms x N_QUERIES) -----

def _run_phase_point(
    g: np.random.Generator,
    entities: np.ndarray,
    K: int,
    V_tasks: int,
    overlap: float,
    n_queries: int,
) -> Dict[str, Any]:
    """Run TASK_VECTOR / RANDOM_VECTOR / ORACLE arms on one phase point.

    v3 returns PER-QUERY correctness vectors (not just means), so the
    aggregator can pool across seeds + bootstrap-resample at query granularity.
    """
    V_ents = entities.shape[0]
    N = entities.shape[1]
    K_eff = min(K, V_ents)
    out: Dict[str, Any] = {}

    perms = np.stack([g.permutation(V_ents) for _ in range(V_tasks)], axis=0)

    shared_size = int(round(overlap * K_eff))
    if shared_size > K_eff:
        shared_size = K_eff
    if shared_size > V_ents:
        shared_size = V_ents
    if shared_size > 0:
        shared_idx = g.choice(V_ents, size=shared_size, replace=False)
    else:
        shared_idx = np.array([], dtype=np.int64)

    remainder = K_eff - shared_size
    task_ctx_list = []
    for ti in range(V_tasks):
        if remainder > 0:
            candidate = np.setdiff1d(np.arange(V_ents), shared_idx, assume_unique=False)
            if remainder > candidate.size:
                rem_eff = candidate.size
            else:
                rem_eff = remainder
            if rem_eff > 0:
                fresh = g.choice(candidate, size=rem_eff, replace=False)
            else:
                fresh = np.array([], dtype=np.int64)
            ctx = np.concatenate([shared_idx, fresh])
        else:
            ctx = shared_idx[:K_eff].copy()
        task_ctx_list.append(ctx)
    K_use = task_ctx_list[0].size if task_ctx_list else 0

    if K_use == 0:
        for arm in ARMS:
            out[arm + "_top1_recall"] = 0.0
            out[arm + "_mean_cosine"] = 0.0
            out[arm + "_per_query_correct"] = []
        out["K_use"] = 0
        out["V_tasks"] = V_tasks
        out["overlap"] = overlap
        out["n_queries"] = n_queries
        return out

    focal_perm = perms[0]
    focal_ctx = task_ctx_list[0]
    if n_queries > focal_ctx.size:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=True)
    else:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=False)
    true_outputs = focal_perm[q_idx]

    all_inputs_idx = np.concatenate([task_ctx_list[ti] for ti in range(V_tasks)])
    all_outputs_true_idx = np.concatenate(
        [perms[ti][task_ctx_list[ti]] for ti in range(V_tasks)])
    all_outputs_rand_idx = g.integers(0, V_ents, size=all_inputs_idx.size)

    ctx_inputs = entities[all_inputs_idx]
    ctx_outputs_true = entities[all_outputs_true_idx]
    ctx_outputs_rand = entities[all_outputs_rand_idx]
    queries = entities[q_idx]

    tv_task = _bind_bundle_np(ctx_inputs, ctx_outputs_true)
    tv_rand = _bind_bundle_np(ctx_inputs, ctx_outputs_rand)

    def _eval_arm_np(tv: np.ndarray) -> Tuple[float, float, List[int]]:
        preds = np.stack([_unbind_np(tv, queries[i]) for i in range(queries.shape[0])], axis=0)
        preds = preds / (np.linalg.norm(preds, axis=-1, keepdims=True) + 1e-8)
        sims = preds @ entities.T
        top1 = sims.argmax(axis=-1)
        top1_cos = sims.max(axis=-1)
        per_q_correct = (top1 == true_outputs).astype(np.int32).tolist()
        correct = float(np.mean(per_q_correct))
        return correct, float(np.mean(top1_cos)), per_q_correct

    tv_recall, tv_cos, tv_per_q = _eval_arm_np(tv_task)
    rv_recall, rv_cos, rv_per_q = _eval_arm_np(tv_rand)
    out["TASK_VECTOR_top1_recall"] = tv_recall
    out["TASK_VECTOR_mean_cosine"] = tv_cos
    out["TASK_VECTOR_per_query_correct"] = tv_per_q
    out["RANDOM_VECTOR_top1_recall"] = rv_recall
    out["RANDOM_VECTOR_mean_cosine"] = rv_cos
    out["RANDOM_VECTOR_per_query_correct"] = rv_per_q
    out["ORACLE_top1_recall"] = 1.0
    out["ORACLE_mean_cosine"] = 1.0
    out["ORACLE_per_query_correct"] = [1] * len(tv_per_q)

    out["K_use"] = int(K_use)
    out["V_tasks"] = int(V_tasks)
    out["overlap"] = float(overlap)
    out["n_queries"] = int(n_queries)
    return out


def run_one_seed_phase_diagram(
    seed: int,
    run_mode: str,
    smoke_corners: bool = False,
) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    N = N_DIM_SMOKE if run_mode != "full" else N_DIM_FULL

    entities = _bipolar_codebook_np(V_ENTS_POOL, N, g)

    n_queries = N_QUERIES_SMOKE if (run_mode != "full") else N_QUERIES_FULL

    if smoke_corners:
        points = list(SMOKE_CORNERS)
    elif run_mode == "selftest":
        points = [(1, 10, 0.0), (200, 10, 0.0)]
        n_queries = 5  # smaller for selftest speed
    else:
        points = []
        for K in K_VALUES:
            for V in N_TASKS_VALUES:
                for ov in OVERLAP_VALUES:
                    points.append((K, V, ov))

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for (K, V, ov) in points:
        res = _run_phase_point(g, entities, K, V, ov, n_queries)
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
        "n_queries_per_point": int(n_queries),
        "phase_map": phase_map,
        "elapsed_s": round(elapsed, 2),
        "anchor_prefix": ANCHOR_PREFIX,
    }


def _compute_slice_cliff_v2(
    slice_pts_sorted: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """v2 metric (INHERITED unchanged in v3): monotonic-decay-from-saturation K_cliff.

    See v2 core docstring for the full rule. Replicated here so v3 is self-contained.
    """
    if not slice_pts_sorted:
        return {"cliff_status": "no_data", "K_sat": None, "K_cliff": None,
                "cliff_reason": "no data points in slice"}

    K_sat = None
    for pt in slice_pts_sorted:
        if pt["TV"] >= K_SAT_THRESHOLD:
            K_sat = pt["K"]
            break

    if K_sat is None:
        max_tv = max(pt["TV"] for pt in slice_pts_sorted)
        return {
            "cliff_status": "no_saturation_reached",
            "K_sat": None,
            "K_cliff": None,
            "cliff_reason": (f"slice never reached K_SAT_THRESHOLD={K_SAT_THRESHOLD} "
                             f"(max TV={max_tv:.3f})")
        }

    post_sat = [pt for pt in slice_pts_sorted if pt["K"] > K_sat]
    K_cliff = None
    cliff_idx = None
    for i, pt in enumerate(post_sat):
        if pt["TV"] < HP_CLIFF_FLOOR_RECALL:
            K_cliff = pt["K"]
            cliff_idx = i
            break

    if K_cliff is None:
        return {
            "cliff_status": "no_cliff_observed_post_saturation",
            "K_sat": K_sat,
            "K_cliff": None,
            "cliff_reason": (f"reached saturation at K={K_sat} but TV never fell "
                             f"below {HP_CLIFF_FLOOR_RECALL} for K > K_sat")
        }

    tail = post_sat[cliff_idx + 1:]
    recovery_thresh = HP_CLIFF_FLOOR_RECALL + MONOTONIC_RECOVERY_TOL
    recoveries = [pt for pt in tail if pt["TV"] > recovery_thresh]
    if recoveries:
        recovery_strs = [f"K={pt['K']}:TV={pt['TV']:.3f}" for pt in recoveries]
        return {
            "cliff_status": "non_monotonic",
            "K_sat": K_sat,
            "K_cliff": None,
            "cliff_reason": (f"TV dropped below floor at K={K_cliff} but recovered "
                             f"above {recovery_thresh:.2f} at: "
                             f"{', '.join(recovery_strs)}")
        }

    return {
        "cliff_status": "valid",
        "K_sat": K_sat,
        "K_cliff": K_cliff,
        "cliff_reason": (f"valid cliff: TV saturated at K={K_sat}, dropped below "
                         f"{HP_CLIFF_FLOOR_RECALL} at K={K_cliff}, no recovery")
    }


def _pooled_phase_diagram(
    per_seed: Dict[str, Dict[str, Any]],
    bootstrap_indices: Optional[Dict[Tuple[int, int, float], np.ndarray]] = None,
) -> Dict[Tuple[int, int, float], Dict[str, float]]:
    """Pool per-query correctness vectors across ALL seeds into ONE phase diagram.

    Returns dict keyed by (K, V, ov) with pooled top1 means per arm.

    If bootstrap_indices is provided, it must map each (K,V,ov) -> resample
    indices (drawn over the pooled query population for that cell); the pooled
    means are computed over the resampled subset (used by bootstrap CI).
    """
    pooled: Dict[Tuple[int, int, float], Dict[str, List[int]]] = {}
    for sid, body in per_seed.items():
        for pt in body.get("phase_map", []):
            key = (int(pt["K"]), int(pt["V_tasks"]), float(pt["overlap"]))
            d = pooled.setdefault(key, {
                "TASK_VECTOR_per_query_correct": [],
                "RANDOM_VECTOR_per_query_correct": [],
                "ORACLE_per_query_correct": [],
            })
            for arm in ARMS:
                fld = arm + "_per_query_correct"
                if fld in pt:
                    d[fld].extend(pt[fld])

    means: Dict[Tuple[int, int, float], Dict[str, float]] = {}
    for key, d in pooled.items():
        if bootstrap_indices is not None and key in bootstrap_indices:
            idx = bootstrap_indices[key]
            entry = {}
            for arm in ARMS:
                arr = np.asarray(d[arm + "_per_query_correct"], dtype=np.float32)
                if arr.size == 0:
                    entry[arm + "_top1_recall_mean"] = 0.0
                else:
                    safe_idx = idx[idx < arr.size]
                    entry[arm + "_top1_recall_mean"] = float(arr[safe_idx].mean()) if safe_idx.size > 0 else 0.0
            entry["n_pooled_queries"] = int(np.asarray(d["TASK_VECTOR_per_query_correct"]).size)
            means[key] = entry
        else:
            entry = {}
            for arm in ARMS:
                arr = np.asarray(d[arm + "_per_query_correct"], dtype=np.float32)
                if arr.size == 0:
                    entry[arm + "_top1_recall_mean"] = 0.0
                else:
                    entry[arm + "_top1_recall_mean"] = float(arr.mean())
            entry["n_pooled_queries"] = int(np.asarray(d["TASK_VECTOR_per_query_correct"]).size)
            means[key] = entry
    return means


def _compute_pooled_slice_details(
    pooled_means: Dict[Tuple[int, int, float], Dict[str, float]],
) -> Dict[str, Dict[str, Any]]:
    """Compute monotonic-decay K_cliff per (V, overlap) slice from pooled means."""
    slice_details: Dict[str, Dict[str, Any]] = {}
    for V in N_TASKS_VALUES:
        for ov in OVERLAP_VALUES:
            slice_pts = []
            for K in K_VALUES:
                key = (K, V, ov)
                if key in pooled_means:
                    slice_pts.append({"K": K, "TV": pooled_means[key]["TASK_VECTOR_top1_recall_mean"]})
            slice_pts.sort(key=lambda x: x["K"])
            cliff_info = _compute_slice_cliff_v2(slice_pts)
            slice_key = f"V{V}_ov{ov:.2f}"
            slice_details[slice_key] = {
                **cliff_info,
                "tv_trajectory": [(pt["K"], round(pt["TV"], 3)) for pt in slice_pts],
            }
    return slice_details


def _bootstrap_cliff_ci(
    per_seed: Dict[str, Dict[str, Any]],
    n_replicates: int = BOOTSTRAP_N_REPLICATES,
    rng_seed: int = BOOTSTRAP_RNG_SEED,
) -> Dict[str, Any]:
    """Bootstrap CI on the pooled K_cliff_min and winning slice.

    For each replicate: resample queries WITH replacement at each (K,V,ov) cell,
    recompute pooled phase diagram, recompute cliff details, identify
    K_cliff_min + winning slice. Aggregate the distribution across replicates.
    """
    rng = np.random.default_rng(rng_seed)

    # First pass: pool to discover per-cell pool sizes
    pooled_raw: Dict[Tuple[int, int, float], int] = {}
    for sid, body in per_seed.items():
        for pt in body.get("phase_map", []):
            key = (int(pt["K"]), int(pt["V_tasks"]), float(pt["overlap"]))
            n = len(pt.get("TASK_VECTOR_per_query_correct", []))
            pooled_raw[key] = pooled_raw.get(key, 0) + n

    slice_winner_counts: Dict[str, int] = {}
    k_cliff_min_dist: List[Optional[int]] = []

    for _ in range(n_replicates):
        boot_indices: Dict[Tuple[int, int, float], np.ndarray] = {}
        for key, n in pooled_raw.items():
            if n > 0:
                boot_indices[key] = rng.integers(0, n, size=n)
            else:
                boot_indices[key] = np.array([], dtype=np.int64)

        pooled_means = _pooled_phase_diagram(per_seed, bootstrap_indices=boot_indices)
        slice_details = _compute_pooled_slice_details(pooled_means)

        valid = [(k, info["K_cliff"]) for k, info in slice_details.items()
                 if info["cliff_status"] == "valid" and info["K_cliff"] is not None]
        if valid:
            K_cliff_min = min(v for _, v in valid)
            winners = [k for k, v in valid if v == K_cliff_min]
            # Tie-break by alphabetical slice key (deterministic) — record ALL ties
            winners.sort()
            winner = winners[0]
            slice_winner_counts[winner] = slice_winner_counts.get(winner, 0) + 1
            k_cliff_min_dist.append(K_cliff_min)
        else:
            k_cliff_min_dist.append(None)

    n_valid_reps = sum(1 for v in k_cliff_min_dist if v is not None)
    valid_k = [v for v in k_cliff_min_dist if v is not None]

    if valid_k:
        K_cliff_min_lo = int(np.percentile(valid_k, (100 - BOOTSTRAP_CI_PCT) / 2))
        K_cliff_min_hi = int(np.percentile(valid_k, 100 - (100 - BOOTSTRAP_CI_PCT) / 2))
        K_cliff_min_median = int(np.median(valid_k))
    else:
        K_cliff_min_lo = None
        K_cliff_min_hi = None
        K_cliff_min_median = None

    total = sum(slice_winner_counts.values()) if slice_winner_counts else 0
    slice_winner_freq = {k: (v / total if total > 0 else 0.0)
                          for k, v in slice_winner_counts.items()}
    if slice_winner_freq:
        top_slice = max(slice_winner_freq.items(), key=lambda kv: kv[1])
        top_slice_name, top_slice_freq = top_slice
    else:
        top_slice_name = None
        top_slice_freq = 0.0

    # CI width measured in K-grid-step indices (not raw K values)
    if K_cliff_min_lo is not None and K_cliff_min_hi is not None:
        try:
            idx_lo = K_VALUES.index(K_cliff_min_lo)
            idx_hi = K_VALUES.index(K_cliff_min_hi)
            ci_width_steps = idx_hi - idx_lo
        except ValueError:
            ci_width_steps = None
    else:
        ci_width_steps = None

    return {
        "n_replicates": n_replicates,
        "n_valid_reps": n_valid_reps,
        "K_cliff_min_ci_lo": K_cliff_min_lo,
        "K_cliff_min_ci_hi": K_cliff_min_hi,
        "K_cliff_min_median": K_cliff_min_median,
        "K_cliff_min_ci_width_steps": ci_width_steps,
        "slice_winner_counts": slice_winner_counts,
        "slice_winner_freq": slice_winner_freq,
        "top_slice": top_slice_name,
        "top_slice_freq": top_slice_freq,
        "bootstrap_rng_seed": rng_seed,
        "ci_pct": BOOTSTRAP_CI_PCT,
    }


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str,
                           do_bootstrap: bool = True) -> Dict[str, Any]:
    """v3 verdict: pooled cliff detection + bootstrap CI on cliff_K_loc.

    Chain-grade PASS requires:
    1. At least one valid pooled cliff
    2. Bootstrap: winning slice appears in >= CHAIN_GRADE_SLICE_UNIQUENESS fraction
       of replicates
    3. Bootstrap: K_cliff_min CI width <= CHAIN_GRADE_K_CLIFF_CI_WIDTH K-grid-steps
    4. arms-must-differ >= HP_AVG_ARMS_DIFF_MIN
    5. low-K low-V mechanism floor met
    6. No regime flip

    If only condition 1 met (cliff exists but not seed-stable), MIDDLE_BAND.
    """
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    # Pooled phase diagram across all seeds
    pooled_means = _pooled_phase_diagram(per_seed)
    slice_details = _compute_pooled_slice_details(pooled_means)

    # arms-diff across all phase points (pooled means)
    arm_diffs = []
    tv_all_recalls = []
    regime_flip_points = []
    summary_per_pt = []
    for key, means in sorted(pooled_means.items()):
        K, V, ov = key
        tv = means["TASK_VECTOR_top1_recall_mean"]
        rv = means["RANDOM_VECTOR_top1_recall_mean"]
        oracle = means["ORACLE_top1_recall_mean"]
        diff = tv - rv
        arm_diffs.append(diff)
        tv_all_recalls.append(tv)
        if rv > tv and K <= 5 and V <= 20:
            regime_flip_points.append((K, V, ov))
        summary_per_pt.append({
            "K": K, "V_tasks": V, "overlap": ov,
            "TASK_VECTOR_top1_recall_pooled": tv,
            "RANDOM_VECTOR_top1_recall_pooled": rv,
            "ORACLE_top1_recall_pooled": oracle,
            "arms_diff": diff,
            "n_pooled_queries": means["n_pooled_queries"],
        })

    # K_cliff_min over valid pooled cliffs
    valid_cliffs = [(k, info["K_cliff"]) for k, info in slice_details.items()
                    if info["cliff_status"] == "valid" and info["K_cliff"] is not None]
    n_valid_cliffs = len(valid_cliffs)
    n_total_combos = len(slice_details)
    n_no_sat = sum(1 for info in slice_details.values()
                   if info["cliff_status"] == "no_saturation_reached")
    n_non_monotonic = sum(1 for info in slice_details.values()
                         if info["cliff_status"] == "non_monotonic")
    n_no_cliff = sum(1 for info in slice_details.values()
                     if info["cliff_status"] == "no_cliff_observed_post_saturation")

    if valid_cliffs:
        K_cliff_min = int(min(k_val for _, k_val in valid_cliffs))
        cliff_min_loc_key = [k for k, v in valid_cliffs if v == K_cliff_min][0]
    else:
        K_cliff_min = None
        cliff_min_loc_key = None

    avg_arm_diff = float(np.mean(arm_diffs)) if arm_diffs else 0.0
    all_saturated = bool(all(r >= HF_NO_CLIFF_RECALL_MIN for r in tv_all_recalls)) if tv_all_recalls else False

    low_kv_pts = [p for p in summary_per_pt if p["K"] == 1 and p["V_tasks"] <= 20]
    low_kv_high = any(p["TASK_VECTOR_top1_recall_pooled"] >= HP_K1_FLOOR_RECALL for p in low_kv_pts)

    cliff_observable = n_valid_cliffs >= 1
    am_flag = len(regime_flip_points) > 0

    # Bootstrap CI
    bootstrap_info: Dict[str, Any] = {}
    chain_grade_eligible = False
    if do_bootstrap and run_mode == "full" and per_seed:
        bootstrap_info = _bootstrap_cliff_ci(per_seed)
        # Chain-grade eligibility (gate vs MM)
        slice_stable = (bootstrap_info.get("top_slice_freq", 0.0)
                        >= CHAIN_GRADE_SLICE_UNIQUENESS)
        ci_tight = (bootstrap_info.get("K_cliff_min_ci_width_steps") is not None
                    and bootstrap_info.get("K_cliff_min_ci_width_steps") <= CHAIN_GRADE_K_CLIFF_CI_WIDTH)
        chain_grade_eligible = bool(slice_stable and ci_tight)

    # Verdict
    if all_saturated or avg_arm_diff < 0.10 or am_flag:
        verdict = "HARD_FAIL"
    elif (n_valid_cliffs >= 1 and low_kv_high and cliff_observable
          and avg_arm_diff >= HP_AVG_ARMS_DIFF_MIN
          and chain_grade_eligible):
        verdict = "HARD_PASS"
    elif (n_valid_cliffs >= 1 and low_kv_high and cliff_observable
          and avg_arm_diff >= HP_AVG_ARMS_DIFF_MIN
          and not chain_grade_eligible):
        # cliff exists + arms differ + low-K saturates, but bootstrap shows
        # slice/K instability across resamples — MIDDLE_BAND (v2's actual finding)
        verdict = "MIDDLE_BAND"
    elif n_valid_cliffs >= 1 and avg_arm_diff >= MB_AVG_ARMS_DIFF_LO:
        verdict = "MIDDLE_BAND"
    elif n_valid_cliffs == 0 and (n_no_sat > 0 or n_non_monotonic > 0):
        verdict = "MIDDLE_BAND"
    else:
        verdict = "MIDDLE_BAND"

    if verdict == "HARD_PASS":
        m3_msg = (f"M3#4 CHAIN_GRADE: TASK_VECTOR K-cliff seed-stable (POOLED); "
                  f"K_cliff_min={K_cliff_min} CI=[{bootstrap_info.get('K_cliff_min_ci_lo')}-"
                  f"{bootstrap_info.get('K_cliff_min_ci_hi')}] "
                  f"top_slice={bootstrap_info.get('top_slice')} "
                  f"freq={bootstrap_info.get('top_slice_freq', 0.0):.3f}")
    elif verdict == "MIDDLE_BAND":
        if bootstrap_info:
            m3_msg = (f"M3#4 PARTIAL: cliff EXISTS but location bootstrap-unstable; "
                      f"K_cliff_min={K_cliff_min} CI=[{bootstrap_info.get('K_cliff_min_ci_lo')}-"
                      f"{bootstrap_info.get('K_cliff_min_ci_hi')}] "
                      f"top_slice={bootstrap_info.get('top_slice')} "
                      f"freq={bootstrap_info.get('top_slice_freq', 0.0):.3f}")
        else:
            m3_msg = (f"M3#4 PARTIAL: regime-narrow; "
                      f"{n_valid_cliffs}/{n_total_combos} valid; "
                      f"K_cliff_min={K_cliff_min}")
    else:
        m3_msg = (f"M3#4 NOT CONFIRMED: saturation-trivial or unmechanistic; "
                  f"n_valid_cliffs={n_valid_cliffs}/{n_total_combos}; "
                  f"avg_diff={avg_arm_diff:.3f}")

    verdict_msg = (
        f"{verdict} | K_cliff_min={K_cliff_min} loc={cliff_min_loc_key} "
        f"| valid_cliffs={n_valid_cliffs}/{n_total_combos} "
        f"| no_sat={n_no_sat} | non_monotonic={n_non_monotonic} "
        f"| avg_arms_diff={avg_arm_diff:.3f} | all_saturated={all_saturated} "
        f"| regime_flip={am_flag} | chain_grade_eligible={chain_grade_eligible} "
        f"| {m3_msg}"
    )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "K_cliff_min": K_cliff_min,
        "K_cliff_min_location_key": cliff_min_loc_key,
        "slice_details_pooled": slice_details,
        "n_valid_cliffs": n_valid_cliffs,
        "n_no_saturation_slices": n_no_sat,
        "n_non_monotonic_slices": n_non_monotonic,
        "n_no_cliff_post_sat_slices": n_no_cliff,
        "n_combos_total": n_total_combos,
        "avg_arms_diff": avg_arm_diff,
        "all_saturated": all_saturated,
        "low_kv_mechanism_floor_met": bool(low_kv_high),
        "cliff_observable": bool(cliff_observable),
        "meta_rule_am_regime_flip_points": [list(p) for p in regime_flip_points],
        "summary_per_phase_point_pooled": summary_per_pt,
        "n_seeds_complete": len(per_seed),
        "bootstrap_ci": bootstrap_info,
        "chain_grade_eligible": chain_grade_eligible,
        "m3_concern_4_annotation": m3_msg,
        "v3_metric_constants": {
            "K_SAT_THRESHOLD": K_SAT_THRESHOLD,
            "HP_CLIFF_FLOOR_RECALL": HP_CLIFF_FLOOR_RECALL,
            "MONOTONIC_RECOVERY_TOL": MONOTONIC_RECOVERY_TOL,
            "HP_K1_FLOOR_RECALL": HP_K1_FLOOR_RECALL,
            "HP_AVG_ARMS_DIFF_MIN": HP_AVG_ARMS_DIFF_MIN,
            "N_QUERIES_FULL": N_QUERIES_FULL,
            "BOOTSTRAP_N_REPLICATES": BOOTSTRAP_N_REPLICATES,
            "CHAIN_GRADE_SLICE_UNIQUENESS": CHAIN_GRADE_SLICE_UNIQUENESS,
            "CHAIN_GRADE_K_CLIFF_CI_WIDTH": CHAIN_GRADE_K_CLIFF_CI_WIDTH,
        },
    }


# ----- Smoke discriminator-survives-scale check -----

def smoke_discriminator_check(phase_map: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Smoke must fire the discriminator: (K=200, V=10, ov=0.0) TV < DISCRIMINATOR_SMOKE_FLOOR."""
    disc_pts = [p for p in phase_map
                if p["K"] == 200 and p["V_tasks"] == 10 and abs(p["overlap"] - 0.0) < 1e-6]
    if not disc_pts:
        return False, "smoke discriminator corner (K=200, V=10, ov=0.0) MISSING"
    tv = disc_pts[0]["TASK_VECTOR_top1_recall"]
    if tv < DISCRIMINATOR_SMOKE_FLOOR:
        return True, f"smoke discriminator FIRED: TV(K=200,V=10,ov=0.0)={tv:.3f} < {DISCRIMINATOR_SMOKE_FLOOR}"
    return False, (f"smoke discriminator FAILED-TO-FIRE: "
                   f"TV(K=200,V=10,ov=0.0)={tv:.3f} >= {DISCRIMINATOR_SMOKE_FLOOR}")


# ----- Self-test -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: 2 corner points + tests of new v3 components."""
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pts = body["phase_map"]
        low = [p for p in pts if p["K"] == 1 and p["V_tasks"] == 10 and abs(p["overlap"]) < 1e-6]
        hi = [p for p in pts if p["K"] == 200 and p["V_tasks"] == 10 and abs(p["overlap"]) < 1e-6]
        if not low or not hi:
            return False, f"selftest: missing corner points; got {len(pts)}"
        tv_low = low[0]["TASK_VECTOR_top1_recall"]
        if tv_low < 0.5:
            return False, f"selftest: TV at K=1 V=10 ov=0 = {tv_low:.3f} (expected >0.5)"
        tv_hi = hi[0]["TASK_VECTOR_top1_recall"]
        if tv_hi >= tv_low - 0.20:
            return False, (f"selftest: TV at K=200 ({tv_hi:.3f}) too close to K=1 ({tv_low:.3f}); "
                           f"cliff should be visible")
        # Verify per-query vectors present (load-bearing for v3 bootstrap)
        if "TASK_VECTOR_per_query_correct" not in low[0]:
            return False, "selftest: per-query correctness vector missing (load-bearing for v3 bootstrap)"
        if len(low[0]["TASK_VECTOR_per_query_correct"]) != low[0]["n_queries"]:
            return False, "selftest: per-query length mismatch"
        # Verify pooled-aggregator + bootstrap stub run end-to-end on selftest data
        per_seed_stub = {str(seed): body}
        agg = aggregate_and_verdict(per_seed_stub, run_mode="selftest", do_bootstrap=False)
        if "verdict" not in agg:
            return False, "selftest: aggregator did not produce verdict"
        msg = (f"selftest OK: TV(K=1)={tv_low:.3f}, TV(K=200)={tv_hi:.3f}, "
               f"per_query_correct_len={len(low[0]['TASK_VECTOR_per_query_correct'])}, "
               f"agg_verdict={agg['verdict']}, backend={body['backend']}")
        return True, msg
    except Exception as e:
        return False, f"selftest EXC: {type(e).__name__}: {e}\n{traceback.format_exc()}"


if __name__ == "__main__":
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
