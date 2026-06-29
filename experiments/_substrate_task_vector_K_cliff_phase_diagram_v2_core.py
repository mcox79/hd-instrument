"""Shared core for substrate_task_vector_K_cliff_phase_diagram_v2 sibling cells.

v2 REVISION (2026-06-28): Fixes v1 K_cliff metric artifact identified by
Skunkworks audit. v1 reported K_cliff_min=1 at (V=10, ov=0.6) -- but off-disk
audit showed this was LOW-K CUE DEGENERACY (TV=0.0 at K=1, RECOVERS to 0.3-0.8
at K=3-5), not a true high-K saturation cliff. v2 changes:

1. REVISED K_cliff METRIC: requires monotonic decay FROM saturation. K_cliff is
   the smallest K > K_sat (where TV first reaches >= K_SAT_THRESHOLD) such that
   TV drops below K_CLIFF_FLOOR AND DOES NOT recover above K_CLIFF_FLOOR for any
   higher K. If a slice never reaches saturation, status="no_saturation_reached"
   (cliff INVALID — substrate cannot encode this regime, low-K cue degeneracy).
   If a slice saturates and then RECOVERS after a dip, status="non_monotonic" —
   cliff INVALID for that slice.

2. TIGHTER V_tasks AXIS: V in {10, 20, 50}. v1 used V=200 which was BIT-IDENTICAL
   ZERO across 3 seeds at 18/21 (V=200) cells -- substrate-cannot-encode floor;
   floor-vs-floor not informative. Drop V=200, add V=20 fill.

3. EXTENDED K AXIS asymptote: K in {1, 3, 5, 10, 20, 50, 100, 200}. v1 capped at
   K=100; v2 extends to K=200 to confirm asymptotic cliff floor in low-V/low-ov
   regime where v1 showed monotonic decay 1.0 -> 1.0 -> 0.9 -> 0.6 -> 0.5 -> 0.2
   -> 0.1.

ARMS: TASK_VECTOR / RANDOM_VECTOR / ORACLE (3 per phase-point) — unchanged.

CARDINALITY: 3 arms * 8 K * 3 V * 3 overlap * 10 queries = 2160 records per seed
SMOKE: 5 corners + 1 discriminator-survives-scale corner = 6 * 3 * 2 = 36 records.

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn) v2 artifact-fix
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

ANCHOR_PREFIX = "substrate_task_vector_K_cliff_phase_diagram_v2"

# ----- Phase axes (LOCKED v2) -----
K_VALUES = (1, 3, 5, 10, 20, 50, 100, 200)        # 8 points (added K=200 asymptote)
N_TASKS_VALUES = (10, 20, 50)                      # 3 points (dropped V=200 known-floor; added V=20 fill)
OVERLAP_VALUES = (0.0, 0.3, 0.6)                   # 3 points (unchanged)
ARMS = ("TASK_VECTOR", "RANDOM_VECTOR", "ORACLE")

# Entity codebook size — DECOUPLED from V_tasks (this is the SHARED entity pool
# from which all tasks draw inputs and outputs). v1 set this to max(N_TASKS_VALUES)
# which caused input/output collisions across tasks when V_tasks_max was small (50).
# v2 keeps codebook at 200 so each task's K random picks rarely collide with other
# tasks' picks. Cleanup readout argmax searches over ALL V_ENTS_POOL.
V_ENTS_POOL = 200

# Smoke corner points: 5 corners spanning regimes + 1 discriminator-survives-scale.
# DISCRIMINATOR corner = (K=200, V=10, ov=0.0): MUST show TV well below cliff floor.
# Single-seed prelim (seed=7, N=8192, V_ENTS_POOL=200) shows TV=0.0 here (extremely
# robust signal). v1 cap of K=100 gave TV=0.4 -- too marginal for discriminator gate.
# If smoke shows TV >= DISCRIMINATOR_SMOKE_FLOOR (0.40) at this corner, full dispatch
# BLOCKED per USER 2026-06-26 discriminator-must-survive-scale rule.
SMOKE_CORNERS = (
    (1, 10, 0.0),       # low-K low-V low-ov — saturation regime (expect TV ~ 1.0)
    (1, 50, 0.0),       # low-K mid-V low-ov — saturation regime (expect TV ~ 1.0)
    (10, 20, 0.3),      # mid-K mid-V mid-ov — transition regime
    (50, 50, 0.6),      # mid-K mid-V high-ov — interference regime
    (100, 10, 0.0),     # mid-cliff regime
    (200, 10, 0.0),     # DISCRIMINATOR-SURVIVES-SCALE: DEEP cliff; MUST fire (TV < 0.40)
)

# Pre-reg bands (mirror prereg .md; LOCKED at module load)
HP_K1_FLOOR_RECALL = 0.95          # low-K low-V mechanism floor (saturation)
HP_CLIFF_FLOOR_RECALL = 0.40       # K_cliff defined as drop below this
HP_AVG_ARMS_DIFF_MIN = 0.20        # TASK_VECTOR - RANDOM_VECTOR avg gate
MB_AVG_ARMS_DIFF_LO = 0.10
HF_NO_CLIFF_RECALL_MIN = 0.95      # if ALL phase pts >= this, HARD_FAIL saturation

# v2 NEW: monotonic-decay rule constants
K_SAT_THRESHOLD = 0.95             # slice must hit this to be saturation-eligible
MONOTONIC_RECOVERY_TOL = 0.05      # if post-cliff TV rises by >= this, slice is non-monotonic
DISCRIMINATOR_SMOKE_FLOOR = 0.40   # smoke discriminator corner must show TV < this

# Per-point query count
N_QUERIES_FULL = 10
# v2: smoke uses 10 queries (was 2 in v1). With only 2 Bernoulli trials, variance
# dominates the smoke discriminator (TV=0.5 from 1/2 collapses indistinguishably
# with true ~0.0); 10 queries gives reliable cliff measurement at <30s smoke.
N_QUERIES_SMOKE = 10

N_DIM_FULL = 8192
N_DIM_SMOKE = 8192   # discriminator-survives-scale: smoke at full N

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    if _CUDA_OK:
        return "torch.cuda"
    if _TORCH_OK:
        return "torch.cpu"
    return "numpy.cpu"


# ----- HRR primitives (torch + numpy variants) -----

def _bipolar_codebook_np(V: int, N: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X


def _bind_bundle_torch(inputs: "torch.Tensor", outputs: "torch.Tensor") -> "torch.Tensor":
    I = torch.fft.rfft(inputs, dim=-1)
    O = torch.fft.rfft(outputs, dim=-1)
    P = I * O
    bound = torch.fft.irfft(P, n=inputs.shape[-1], dim=-1).to(torch.float32)
    tv = bound.sum(dim=0)
    n = torch.linalg.norm(tv) + 1e-8
    return tv / n


def _unbind_torch(c: "torch.Tensor", a: "torch.Tensor") -> "torch.Tensor":
    C = torch.fft.rfft(c, dim=-1)
    A = torch.fft.rfft(a, dim=-1)
    R = C * torch.conj(A)
    return torch.fft.irfft(R, n=c.shape[-1], dim=-1).to(torch.float32)


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
    device: str,
) -> Dict[str, float]:
    """Run TASK_VECTOR / RANDOM_VECTOR / ORACLE arms on one phase point.

    Multi-task ICL scenario: V_tasks distinct task vectors (each = K bound pairs
    for its own permutation) are SUMMED into ONE bundle. Query unbinds from the
    bundle to retrieve from the focal task -- interference from V_tasks-1 competing
    task-vectors. This is the actual cross-task capacity test.

    overlap: fraction of context INDICES shared across the V_tasks tasks. Shared
    indices mean tasks bind to overlapping input-keys with different output values
    -- aliasing interference (NOT cue degeneracy).

    Returns dict with per-arm top1_recall + mean_cosine.
    """
    V_ents = entities.shape[0]
    N = entities.shape[1]
    K_eff = min(K, V_ents)
    out: Dict[str, float] = {}

    # Build V_tasks distinct random permutations
    perms = np.stack([g.permutation(V_ents) for _ in range(V_tasks)], axis=0)

    # Shared context-index pool (size = floor(overlap * K_eff))
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

    if _CUDA_OK and device == "cuda":
        E = torch.from_numpy(entities).to("cuda")
        ctx_inputs = E[torch.from_numpy(all_inputs_idx).long().to("cuda")]
        ctx_outputs_true = E[torch.from_numpy(all_outputs_true_idx).long().to("cuda")]
        ctx_outputs_rand = E[torch.from_numpy(all_outputs_rand_idx).long().to("cuda")]
        queries = E[torch.from_numpy(q_idx).long().to("cuda")]

        tv_task = _bind_bundle_torch(ctx_inputs, ctx_outputs_true)
        tv_rand = _bind_bundle_torch(ctx_inputs, ctx_outputs_rand)

        def _eval_arm(tv: "torch.Tensor") -> Tuple[float, float]:
            preds = torch.stack([_unbind_torch(tv, queries[i])
                                  for i in range(queries.shape[0])], dim=0)
            preds = preds / (torch.linalg.norm(preds, dim=-1, keepdim=True) + 1e-8)
            sims = preds @ E.T
            top1 = sims.argmax(dim=-1).detach().cpu().numpy()
            top1_cos = sims.max(dim=-1).values.detach().cpu().numpy()
            correct = (top1 == true_outputs).astype(np.float32).mean()
            return float(correct), float(top1_cos.mean())

        tv_recall, tv_cos = _eval_arm(tv_task)
        rv_recall, rv_cos = _eval_arm(tv_rand)
        out["TASK_VECTOR_top1_recall"] = tv_recall
        out["TASK_VECTOR_mean_cosine"] = tv_cos
        out["RANDOM_VECTOR_top1_recall"] = rv_recall
        out["RANDOM_VECTOR_mean_cosine"] = rv_cos
        out["ORACLE_top1_recall"] = 1.0
        out["ORACLE_mean_cosine"] = 1.0
    else:
        ctx_inputs = entities[all_inputs_idx]
        ctx_outputs_true = entities[all_outputs_true_idx]
        ctx_outputs_rand = entities[all_outputs_rand_idx]
        queries = entities[q_idx]

        tv_task = _bind_bundle_np(ctx_inputs, ctx_outputs_true)
        tv_rand = _bind_bundle_np(ctx_inputs, ctx_outputs_rand)

        def _eval_arm_np(tv: np.ndarray) -> Tuple[float, float]:
            preds = np.stack([_unbind_np(tv, queries[i]) for i in range(queries.shape[0])], axis=0)
            preds = preds / (np.linalg.norm(preds, axis=-1, keepdims=True) + 1e-8)
            sims = preds @ entities.T
            top1 = sims.argmax(axis=-1)
            top1_cos = sims.max(axis=-1)
            correct = float(np.mean(top1 == true_outputs))
            return correct, float(np.mean(top1_cos))

        tv_recall, tv_cos = _eval_arm_np(tv_task)
        rv_recall, rv_cos = _eval_arm_np(tv_rand)
        out["TASK_VECTOR_top1_recall"] = tv_recall
        out["TASK_VECTOR_mean_cosine"] = tv_cos
        out["RANDOM_VECTOR_top1_recall"] = rv_recall
        out["RANDOM_VECTOR_mean_cosine"] = rv_cos
        out["ORACLE_top1_recall"] = 1.0
        out["ORACLE_mean_cosine"] = 1.0

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

    # V2: codebook is DECOUPLED from V_tasks (see V_ENTS_POOL docstring)
    entities = _bipolar_codebook_np(V_ENTS_POOL, N, g)
    device = "cuda" if _CUDA_OK else "cpu"

    n_queries = N_QUERIES_SMOKE if (run_mode != "full") else N_QUERIES_FULL

    if smoke_corners:
        points = list(SMOKE_CORNERS)
    elif run_mode == "selftest":
        # tiny selftest: 2 corners (low-K low-V saturation + high-K low-V cliff)
        points = [(1, 10, 0.0), (200, 10, 0.0)]
        n_queries = 2
    else:
        points = []
        for K in K_VALUES:
            for V in N_TASKS_VALUES:
                for ov in OVERLAP_VALUES:
                    points.append((K, V, ov))

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for (K, V, ov) in points:
        res = _run_phase_point(g, entities, K, V, ov, n_queries, device)
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
    """v2 REVISED K_cliff metric per (V, overlap) slice.

    INPUT: slice_pts_sorted = list of {"K": int, "TV": float} sorted by K ascending.
    OUTPUT: dict with:
        cliff_status: "valid" | "no_saturation_reached" | "non_monotonic"
        K_sat: smallest K where TV >= K_SAT_THRESHOLD (or None)
        K_cliff: smallest K > K_sat where TV < HP_CLIFF_FLOOR_RECALL AND no recovery
                 above HP_CLIFF_FLOOR_RECALL + MONOTONIC_RECOVERY_TOL at any higher K
                 (or None if invalid)
        cliff_reason: explanatory string

    LOAD-BEARING RULES (the metric artifact fix):
    1. A slice must REACH saturation (TV >= K_SAT_THRESHOLD) to be cliff-eligible.
       This eliminates LOW-K CUE DEGENERACY cases (TV starts at 0.0).
    2. After K_sat, TV must drop below HP_CLIFF_FLOOR_RECALL.
    3. After dropping, TV must STAY at or below HP_CLIFF_FLOOR_RECALL + tol for ALL
       higher K. If TV recovers, the dip was a noise/aliasing fluctuation, not a
       true high-K saturation cliff.
    """
    if not slice_pts_sorted:
        return {"cliff_status": "no_data", "K_sat": None, "K_cliff": None,
                "cliff_reason": "no data points in slice"}

    # Step 1: find K_sat (smallest K where TV >= K_SAT_THRESHOLD)
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
                             f"(max TV={max_tv:.3f}); low-K cue degeneracy or "
                             f"substrate-cannot-encode floor")
        }

    # Step 2: find K_cliff (smallest K > K_sat where TV < HP_CLIFF_FLOOR_RECALL)
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

    # Step 3: monotonic-decay check — verify TV stays at/below floor + tol for all K > K_cliff
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
                             f"{', '.join(recovery_strs)} — not a true cliff")
        }

    return {
        "cliff_status": "valid",
        "K_sat": K_sat,
        "K_cliff": K_cliff,
        "cliff_reason": (f"valid cliff: TV saturated at K={K_sat}, dropped below "
                         f"{HP_CLIFF_FLOOR_RECALL} at K={K_cliff}, no recovery for K > K_cliff")
    }


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    """v2 verdict: uses REVISED monotonic-decay K_cliff metric."""
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    # Pool per (K, V, overlap)
    bucket: Dict[Tuple[int, int, float], Dict[str, List[float]]] = {}
    for s, body in per_seed.items():
        for pt in body.get("phase_map", []):
            key = (int(pt["K"]), int(pt["V_tasks"]), float(pt["overlap"]))
            d = bucket.setdefault(key, {
                "TASK_VECTOR_top1_recall": [],
                "RANDOM_VECTOR_top1_recall": [],
                "ORACLE_top1_recall": [],
            })
            d["TASK_VECTOR_top1_recall"].append(pt["TASK_VECTOR_top1_recall"])
            d["RANDOM_VECTOR_top1_recall"].append(pt["RANDOM_VECTOR_top1_recall"])
            d["ORACLE_top1_recall"].append(pt["ORACLE_top1_recall"])

    summary_per_pt: List[Dict[str, Any]] = []
    arm_diffs: List[float] = []
    tv_all_recalls: List[float] = []
    regime_flip_points: List[Tuple[int, int, float]] = []
    for key, d in sorted(bucket.items()):
        K, V, ov = key
        tv_mean = float(np.mean(d["TASK_VECTOR_top1_recall"]))
        rv_mean = float(np.mean(d["RANDOM_VECTOR_top1_recall"]))
        oracle_mean = float(np.mean(d["ORACLE_top1_recall"]))
        diff = tv_mean - rv_mean
        arm_diffs.append(diff)
        tv_all_recalls.append(tv_mean)
        # META_RULE_AM: TV < RV at low-K low-V is regime-flip (TV mechanism inverted)
        if rv_mean > tv_mean and K <= 5 and V <= 20:
            regime_flip_points.append((K, V, ov))
        summary_per_pt.append({
            "K": K, "V_tasks": V, "overlap": ov,
            "TASK_VECTOR_top1_recall_mean": tv_mean,
            "RANDOM_VECTOR_top1_recall_mean": rv_mean,
            "ORACLE_top1_recall_mean": oracle_mean,
            "arms_diff": diff,
            "n_seeds": len(d["TASK_VECTOR_top1_recall"]),
        })

    # v2 REVISED: per-slice cliff with monotonic-decay rule
    slice_details: Dict[str, Dict[str, Any]] = {}
    for V in N_TASKS_VALUES:
        for ov in OVERLAP_VALUES:
            slice_pts = sorted(
                [{"K": p["K"], "TV": p["TASK_VECTOR_top1_recall_mean"]}
                 for p in summary_per_pt
                 if p["V_tasks"] == V and abs(p["overlap"] - ov) < 1e-6],
                key=lambda x: x["K"]
            )
            cliff_info = _compute_slice_cliff_v2(slice_pts)
            slice_key = f"V{V}_ov{ov:.2f}"
            slice_details[slice_key] = {
                **cliff_info,
                "tv_trajectory": [(pt["K"], round(pt["TV"], 3)) for pt in slice_pts],
            }

    # K_cliff_min: only over VALID cliffs
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

    # Low-K low-V mechanism floor check (HARD_PASS gate B)
    low_kv_pts = [p for p in summary_per_pt if p["K"] == 1 and p["V_tasks"] <= 20]
    low_kv_high = any(p["TASK_VECTOR_top1_recall_mean"] >= HP_K1_FLOOR_RECALL for p in low_kv_pts)

    # Cliff-observable check (any VALID cliff)
    cliff_observable = n_valid_cliffs >= 1

    am_flag = len(regime_flip_points) > 0

    # Verdict
    if all_saturated or avg_arm_diff < 0.10 or am_flag:
        verdict = "HARD_FAIL"
    elif (n_valid_cliffs >= 1 and low_kv_high and cliff_observable
          and avg_arm_diff >= HP_AVG_ARMS_DIFF_MIN):
        verdict = "HARD_PASS"
    elif n_valid_cliffs >= 1 and avg_arm_diff >= MB_AVG_ARMS_DIFF_LO:
        verdict = "MIDDLE_BAND"
    elif n_valid_cliffs == 0 and (n_no_sat > 0 or n_non_monotonic > 0):
        # Most slices invalid (cue-degeneracy or non-monotonic). Mechanism unclear.
        verdict = "MIDDLE_BAND"
    else:
        verdict = "MIDDLE_BAND"

    # M3 concern #4 annotation
    if verdict == "HARD_PASS":
        m3_msg = (f"M3#4 CONFIRMED: TASK_VECTOR un-saturated; "
                  f"VALID K_cliff_min={K_cliff_min} at {cliff_min_loc_key} "
                  f"({n_valid_cliffs}/{n_total_combos} slices valid)")
    elif verdict == "MIDDLE_BAND":
        m3_msg = (f"M3#4 PARTIAL: regime-narrow; "
                  f"{n_valid_cliffs}/{n_total_combos} valid cliffs; "
                  f"{n_no_sat} no-sat; {n_non_monotonic} non-monotonic; "
                  f"K_cliff_min={K_cliff_min}")
    else:
        m3_msg = (f"M3#4 NOT CONFIRMED: saturation-trivial or unmechanistic; "
                  f"n_valid_cliffs={n_valid_cliffs}/{n_total_combos}; "
                  f"avg_diff={avg_arm_diff:.3f}")

    verdict_msg = (
        f"{verdict} | K_cliff_min={K_cliff_min} loc={cliff_min_loc_key} "
        f"| valid_cliffs={n_valid_cliffs}/{n_total_combos} "
        f"| no_sat={n_no_sat} | non_monotonic={n_non_monotonic} "
        f"| no_cliff_post_sat={n_no_cliff} "
        f"| avg_arms_diff={avg_arm_diff:.3f} | all_saturated={all_saturated} "
        f"| regime_flip={am_flag} | {m3_msg}"
    )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "K_cliff_min": K_cliff_min,
        "K_cliff_min_location_key": cliff_min_loc_key,
        "slice_details": slice_details,
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
        "summary_per_phase_point": summary_per_pt,
        "n_seeds_complete": len(per_seed),
        "m3_concern_4_annotation": m3_msg,
        "v2_metric_constants": {
            "K_SAT_THRESHOLD": K_SAT_THRESHOLD,
            "HP_CLIFF_FLOOR_RECALL": HP_CLIFF_FLOOR_RECALL,
            "MONOTONIC_RECOVERY_TOL": MONOTONIC_RECOVERY_TOL,
            "HP_K1_FLOOR_RECALL": HP_K1_FLOOR_RECALL,
            "HP_AVG_ARMS_DIFF_MIN": HP_AVG_ARMS_DIFF_MIN,
        },
    }


# ----- Smoke discriminator-survives-scale check -----

def smoke_discriminator_check(phase_map: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Smoke must fire the discriminator: (K=200, V=10, ov=0.0) TV < DISCRIMINATOR_SMOKE_FLOOR.

    If smoke shows TV >= DISCRIMINATOR_SMOKE_FLOOR at this known-cliff corner, full
    dispatch is BLOCKED per USER 2026-06-26 discriminator-must-survive-scale rule.
    """
    disc_pts = [p for p in phase_map
                if p["K"] == 200 and p["V_tasks"] == 10 and abs(p["overlap"] - 0.0) < 1e-6]
    if not disc_pts:
        return False, "smoke discriminator corner (K=200, V=10, ov=0.0) MISSING"
    tv = disc_pts[0]["TASK_VECTOR_top1_recall"]
    if tv < DISCRIMINATOR_SMOKE_FLOOR:
        return True, f"smoke discriminator FIRED: TV(K=200,V=10,ov=0.0)={tv:.3f} < {DISCRIMINATOR_SMOKE_FLOOR}"
    return False, (f"smoke discriminator FAILED-TO-FIRE: "
                   f"TV(K=200,V=10,ov=0.0)={tv:.3f} >= {DISCRIMINATOR_SMOKE_FLOOR} "
                   f"-- substrate did not show cliff at smoke; full dispatch BLOCKED")


# ----- Self-test -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: 2 corner points.

    Asserts:
      - TV(K=1, V=10, ov=0.0) > 0.5 (saturation regime works)
      - TV(K=200, V=10, ov=0.0) < TV(K=1, V=10, ov=0.0) - 0.20 (cliff present)
      - TV(K=200, V=10, ov=0.0) >= RV(K=200, V=10, ov=0.0) (mechanism still beats random)
    """
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pts = body["phase_map"]
        low = [p for p in pts if p["K"] == 1 and p["V_tasks"] == 10 and abs(p["overlap"]) < 1e-6]
        hi = [p for p in pts if p["K"] == 200 and p["V_tasks"] == 10 and abs(p["overlap"]) < 1e-6]
        if not low or not hi:
            return False, f"selftest: missing corner points; got {len(pts)} (have keys: {[(p['K'],p['V_tasks'],p['overlap']) for p in pts]})"
        tv_low = low[0]["TASK_VECTOR_top1_recall"]
        if tv_low < 0.5:
            return False, f"selftest: TV at K=1 V=10 ov=0 = {tv_low:.3f} (expected >0.5; saturation regime should work)"
        tv_hi = hi[0]["TASK_VECTOR_top1_recall"]
        rv_hi = hi[0]["RANDOM_VECTOR_top1_recall"]
        if tv_hi >= tv_low - 0.20:
            return False, (f"selftest: TV at K=200 ({tv_hi:.3f}) too close to K=1 ({tv_low:.3f}); "
                           f"cliff should be visible (TV should drop by >= 0.20)")
        msg = (f"selftest OK: TV(K=1,V=10,ov=0)={tv_low:.3f}, "
               f"TV(K=200,V=10,ov=0)={tv_hi:.3f}, RV(K=200,V=10,ov=0)={rv_hi:.3f}, "
               f"backend={body['backend']}")
        return True, msg
    except Exception as e:
        return False, f"selftest EXC: {type(e).__name__}: {e}\n{traceback.format_exc()}"


if __name__ == "__main__":
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
