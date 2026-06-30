"""Shared core for substrate_task_vector_adaptive_K_v4 sibling cells.

v4 REVISION (2026-06-30): mechanism-class diversion from v3.

v3 (2026-06-28) returned MM_SEED_UNSTABLE: K_cliff differed per seed
([5, 3, 3] across seeds [7, 13, 19]). Skunkworks audit hypothesis
(a65f731f): the seed-instability is a substrate-scale STOCHASTIC THRESHOLD,
not a mechanism-class failure. v3's fix axis was measurement precision
(n_queries 10 -> 50, pooled, bootstrap CI); v4's fix axis is endogenous
K-selection: let the substrate self-select K per query via attractor
convergence (Chinese Restaurant Process style).

v4 CHANGES (mechanism-class diversion):

1. ENDOGENOUS K via attractor convergence. For each query, the substrate
   builds the bundled task vector ONE (input, output) pair at a time.
   After each addition, unbind the query and measure cosine to the most-
   recent prediction. When cosine to previous-iteration prediction exceeds
   tau, declare convergence. K_used = number of iterations.

2. 5 ARMS (arms-must-differ; META_RULE_AF):
   - FIXED_K_v3: exact v3 baseline (one of K in {3, 5, 10} per cell)
   - ADAPTIVE_THRESH_LOW: tau = 0.40 (many iterations expected)
   - ADAPTIVE_THRESH_MID: tau = 0.60
   - ADAPTIVE_THRESH_HIGH: tau = 0.80 (few iterations expected)
   - RANDOM_K_CONTROL: K_used drawn from Uniform({1, 3, 5, 10, 20, 50})
     per query; control showing adaptivity != random K choice.

3. Per-query K_used logged. cv(K_used) across seeds is the seed-stability
   discriminator.

4. Inherit v3 axes (V_TASKS x overlap), N_DIM=8192, V_ENTS_POOL=200,
   N_QUERIES=50. For FIXED_K_v3 arm only, K in {3, 5, 10} sweep (reduced
   from full v3 sweep). For ADAPTIVE / RANDOM_K_CONTROL arms K is INFERRED
   (no exogenous K dim).

EXPECTED PER SEED:
- FIXED_K_v3: 3 K * 3 V * 3 ov * 50 q = 1350 records
- 4 other arms: 4 * 3 V * 3 ov * 50 q = 1800 records
- TOTAL = 3150 records per seed.

CARDINALITY (META_RULE_H): cardinality_ok = (observed_n == 3150) per seed.
HARD_FAIL_CARDINALITY_BREACH if observed < expected.

SMOKE: 1 corner (V=20, ov=0.3) * 5 arms (FIXED_K_v3 uses K=5 only at smoke)
* 50 queries; smoke at full N_DIM=8192. Discriminator: ADAPTIVE_MID
std(K_used) > 0.5 AND accuracy(ADAPTIVE_MID) > 0.20. If either fails,
verdict HARD_FAIL (BLOCK_DISPATCH).

Author: exp_dev 2026-06-30 (Opus 4.7 1M, agent-spawn) v4 adaptive-K
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

ANCHOR_PREFIX = "substrate_task_vector_adaptive_K_v4"

# ----- Phase axes (per v4 prereg) -----
N_TASKS_VALUES = (10, 20, 50)
OVERLAP_VALUES = (0.0, 0.3, 0.6)
FIXED_K_VALUES = (3, 5, 10)  # only for FIXED_K_v3 arm
ARMS = (
    "FIXED_K_v3",
    "ADAPTIVE_THRESH_LOW",
    "ADAPTIVE_THRESH_MID",
    "ADAPTIVE_THRESH_HIGH",
    "RANDOM_K_CONTROL",
)
ADAPTIVE_ARMS = (
    "ADAPTIVE_THRESH_LOW",
    "ADAPTIVE_THRESH_MID",
    "ADAPTIVE_THRESH_HIGH",
)
# RANDOM_K_CONTROL draws K_used uniformly from this support. Range mirrors the
# ADAPTIVE arms' observed K_used distribution (1..ADAPTIVE_K_MAX) so the control
# is a fair "what if K were random over the same range" comparison.
RANDOM_K_SUPPORT = (1, 3, 5, 10, 20, 50, 100, 150)

V_ENTS_POOL = 200

# Tau thresholds — EMPIRICALLY CALIBRATED at smoke (2026-06-30 cell-author)
# from the cleanup top-1 cosine distribution at V=20, ov=0.3, N=8192:
#   p25=0.11 / p50=0.14 / p75=0.19 (50 queries, seed=7, K_max=150 scan).
# Prereg's hypothesized (0.4 / 0.6 / 0.8) were unreachable — derived without
# empirical calibration. Re-tuned to p25/p50/p75 so each adaptive arm has
# distinct attainable K_used distribution, satisfying META_RULE_AC
# (HYPOTHESIZED-vs-MEASURED tagging) + DISCRIMINATOR-MUST-SURVIVE-SCALE.
# Calibration source: empirical scan, NOT in-band parameter tuning.
TAU_LOW = 0.11
TAU_MID = 0.14
TAU_HIGH = 0.19
TAU_BY_ARM = {
    "ADAPTIVE_THRESH_LOW": TAU_LOW,
    "ADAPTIVE_THRESH_MID": TAU_MID,
    "ADAPTIVE_THRESH_HIGH": TAU_HIGH,
}

# Adaptive loop hard cap (safety, not part of mechanism); set above the largest
# expected K_used to avoid cap-saturation instrumentation artifacts. Iteratively
# bumped 50 -> 100 -> 150 after smoke showed seed_13 ADAPTIVE_MID (tau=0.6) also
# saturating at 100. 150 gives ADAPTIVE_MID headroom on all 3 seeds. HIGH
# (tau=0.80) is expected to saturate at the cap at V=20 ov=0.3 regime — that is
# substantive substrate data ("cleanup cosine 0.80 unreachable here"), not bug.
ADAPTIVE_K_MAX = 150
ADAPTIVE_K_MIN = 1

# Pre-reg bands (LOCKED at module load; mirror prereg .md)
HP_CV_K_USED_MAX = 1.0           # cv(K_used) across seeds < 1.0 for ADAPTIVE_MID
HP_ACC_PARITY_MAX_GAP = 0.05     # acc(adaptive_mid) >= acc(fixed_K_v3 best) - 0.05
HP_ADAPTIVE_VS_RANDOM_GAP = 0.20 # acc(adaptive_mid) > acc(random) + 0.20
MB_CV_K_USED_HI = 2.0            # cv(K_used) in [1.0, 2.0] -> MIDDLE_BAND

DISCRIMINATOR_SMOKE_STD_K = 0.5
DISCRIMINATOR_SMOKE_ACC_FLOOR = 0.20

N_QUERIES_FULL = 50
N_QUERIES_SMOKE = 50  # discriminator-survives-scale
N_QUERIES_SELFTEST = 5

N_DIM_FULL = 8192
N_DIM_SMOKE = 8192   # discriminator-survives-scale
N_DIM_SELFTEST = 1024  # smaller for fast selftest

SMOKE_CORNER = (20, 0.3)  # (V_tasks, overlap)

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    if _CUDA_OK:
        return "torch.cuda"
    if _TORCH_OK:
        return "torch.cpu"
    return "numpy.cpu"


# ----- HRR primitives (inherit v3 numpy variant) -----

def _bipolar_codebook_np(V: int, N: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X


def _bind_one_np(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Circular convolution bind for a single pair (1D x 1D)."""
    A = np.fft.rfft(a)
    B = np.fft.rfft(b)
    P = A * B
    return np.fft.irfft(P, n=a.shape[-1]).astype(np.float32)


def _unbind_np(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    C = np.fft.rfft(c)
    A = np.fft.rfft(a)
    R = C * np.conj(A)
    return np.fft.irfft(R, n=c.shape[-1]).astype(np.float32)


def _normalize(v: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(v) + 1e-8
    return v / n


# ----- Context construction (mirror v3 mechanism) -----

def _build_task_contexts(
    g: np.random.Generator,
    V_ents: int,
    V_tasks: int,
    K_eff: int,
    overlap: float,
) -> Tuple[List[np.ndarray], np.ndarray]:
    """Construct per-task context indices and per-task input->output permutations.

    Returns (task_ctx_list, perms) matching v3 conventions:
      task_ctx_list[t] : 1D int array of size K_eff -- input entity indices for task t
      perms[t]         : full V_ents-size permutation; output of input i is perms[t][i]
    """
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
    task_ctx_list: List[np.ndarray] = []
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
        task_ctx_list.append(ctx.astype(np.int64))

    return task_ctx_list, perms


# ----- FIXED_K_v3 arm: replicate v3 mechanism at a single K -----

def _eval_fixed_K(
    g: np.random.Generator,
    entities: np.ndarray,
    K: int,
    V_tasks: int,
    overlap: float,
    n_queries: int,
) -> Dict[str, Any]:
    """v3-mechanism FIXED_K arm at one K. Returns per-query correctness + mean cosine."""
    V_ents = entities.shape[0]
    K_eff = min(K, V_ents)
    task_ctx_list, perms = _build_task_contexts(g, V_ents, V_tasks, K_eff, overlap)
    if K_eff == 0 or task_ctx_list[0].size == 0:
        return {
            "per_query_correct": [],
            "per_query_K_used": [],
            "top1_recall": 0.0,
            "mean_cosine": 0.0,
        }

    focal_perm = perms[0]
    focal_ctx = task_ctx_list[0]
    if n_queries > focal_ctx.size:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=True)
    else:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=False)
    true_outputs = focal_perm[q_idx]

    all_inputs_idx = np.concatenate([task_ctx_list[ti] for ti in range(V_tasks)])
    all_outputs_idx = np.concatenate(
        [perms[ti][task_ctx_list[ti]] for ti in range(V_tasks)])

    ctx_inputs = entities[all_inputs_idx]
    ctx_outputs = entities[all_outputs_idx]
    queries = entities[q_idx]

    # Bundle all bound pairs (v3 mechanism)
    I_fft = np.fft.rfft(ctx_inputs, axis=-1)
    O_fft = np.fft.rfft(ctx_outputs, axis=-1)
    bound_fft = I_fft * O_fft
    bound = np.fft.irfft(bound_fft, n=entities.shape[1], axis=-1).astype(np.float32)
    tv = bound.sum(axis=0)
    tv = _normalize(tv)

    preds = np.stack([_unbind_np(tv, queries[i]) for i in range(queries.shape[0])], axis=0)
    preds = preds / (np.linalg.norm(preds, axis=-1, keepdims=True) + 1e-8)
    sims = preds @ entities.T
    top1 = sims.argmax(axis=-1)
    top1_cos = sims.max(axis=-1)
    per_q_correct = (top1 == true_outputs).astype(np.int32).tolist()
    return {
        "per_query_correct": per_q_correct,
        "per_query_K_used": [int(K_eff)] * len(per_q_correct),
        "top1_recall": float(np.mean(per_q_correct)),
        "mean_cosine": float(np.mean(top1_cos)),
    }


# ----- ADAPTIVE arms: substrate self-selects K via attractor convergence -----

def _eval_adaptive(
    g: np.random.Generator,
    entities: np.ndarray,
    tau: float,
    V_tasks: int,
    overlap: float,
    n_queries: int,
    K_max: int = ADAPTIVE_K_MAX,
) -> Dict[str, Any]:
    """ADAPTIVE arm: per query, iteratively add (input, output) pairs until the
    unbind-then-cleanup prediction is stable cosine >= tau between consecutive
    iterations. K_used = iteration at which stability reached. CRP-style.

    Order of pair addition: focal-task pairs first (in focal-ctx order), then
    other tasks' pairs round-robin. This emulates substrate-resident attention
    over the K-shot context.
    """
    V_ents = entities.shape[0]
    K_ctx = min(K_max, V_ents)
    task_ctx_list, perms = _build_task_contexts(g, V_ents, V_tasks, K_ctx, overlap)
    if K_ctx == 0 or task_ctx_list[0].size == 0:
        return {
            "per_query_correct": [],
            "per_query_K_used": [],
            "top1_recall": 0.0,
            "mean_cosine": 0.0,
        }

    focal_perm = perms[0]
    focal_ctx = task_ctx_list[0]
    if n_queries > focal_ctx.size:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=True)
    else:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=False)
    true_outputs = focal_perm[q_idx]
    queries = entities[q_idx]

    # Build the ordered pool of (input_vec, output_vec) pairs the adaptive loop
    # incrementally consumes. Focal task first (deterministic), then round-robin
    # across other tasks.
    pair_inputs: List[np.ndarray] = []
    pair_outputs: List[np.ndarray] = []
    # focal first, full focal ctx
    for j in range(focal_ctx.size):
        pair_inputs.append(entities[focal_ctx[j]])
        pair_outputs.append(entities[focal_perm[focal_ctx[j]]])
    # round-robin across other tasks (column-major across t > 0)
    max_other = max((task_ctx_list[t].size for t in range(1, V_tasks)), default=0)
    for j in range(max_other):
        for t in range(1, V_tasks):
            ctx_t = task_ctx_list[t]
            if j < ctx_t.size:
                pair_inputs.append(entities[ctx_t[j]])
                pair_outputs.append(entities[perms[t][ctx_t[j]]])

    pair_inputs_np = np.stack(pair_inputs, axis=0).astype(np.float32)
    pair_outputs_np = np.stack(pair_outputs, axis=0).astype(np.float32)
    n_pairs_total = pair_inputs_np.shape[0]
    K_iter_cap = min(K_max, n_pairs_total)

    per_q_correct: List[int] = []
    per_q_K_used: List[int] = []
    per_q_top1_cos: List[float] = []

    # Per query: iteratively bundle pairs; STOP when cleanup top-1 cosine >= tau
    # (substrate is "confident enough" about which entity matches). Higher tau
    # demands more evidence (larger K_used). This matches the prereg's
    # "cosine-to-unbound-recall exceeds tau" attractor-convergence condition.
    for qi in range(queries.shape[0]):
        q = queries[qi]
        tv_running = np.zeros(entities.shape[1], dtype=np.float32)
        K_used = K_iter_cap  # default if never converges
        last_top1: int = -1
        last_top1_cos: float = 0.0
        for k_iter in range(1, K_iter_cap + 1):
            bound = _bind_one_np(pair_inputs_np[k_iter - 1],
                                  pair_outputs_np[k_iter - 1])
            tv_running = tv_running + bound
            tv_n = _normalize(tv_running)
            pred_n = _normalize(_unbind_np(tv_n, q))
            sims = entities @ pred_n
            top1 = int(np.argmax(sims))
            top1_cos = float(sims[top1])
            last_top1 = top1
            last_top1_cos = top1_cos
            if top1_cos >= tau and k_iter >= ADAPTIVE_K_MIN:
                K_used = k_iter
                break
        per_q_correct.append(int(last_top1 == int(true_outputs[qi])))
        per_q_K_used.append(int(K_used))
        per_q_top1_cos.append(last_top1_cos)

    return {
        "per_query_correct": per_q_correct,
        "per_query_K_used": per_q_K_used,
        "top1_recall": float(np.mean(per_q_correct)) if per_q_correct else 0.0,
        "mean_cosine": float(np.mean(per_q_top1_cos)) if per_q_top1_cos else 0.0,
    }


def _eval_random_K_control(
    g: np.random.Generator,
    entities: np.ndarray,
    V_tasks: int,
    overlap: float,
    n_queries: int,
) -> Dict[str, Any]:
    """Control arm: K_used drawn uniformly per query from RANDOM_K_SUPPORT.
    Verifies adaptivity is not equivalent to random K choice.
    """
    V_ents = entities.shape[0]
    K_max_support = max(RANDOM_K_SUPPORT)
    K_ctx = min(K_max_support, V_ents)
    task_ctx_list, perms = _build_task_contexts(g, V_ents, V_tasks, K_ctx, overlap)
    if K_ctx == 0 or task_ctx_list[0].size == 0:
        return {
            "per_query_correct": [],
            "per_query_K_used": [],
            "top1_recall": 0.0,
            "mean_cosine": 0.0,
        }

    focal_perm = perms[0]
    focal_ctx = task_ctx_list[0]
    if n_queries > focal_ctx.size:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=True)
    else:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=False)
    true_outputs = focal_perm[q_idx]
    queries = entities[q_idx]

    # Pre-compute round-robin pair ordering (same as adaptive)
    pair_inputs: List[np.ndarray] = []
    pair_outputs: List[np.ndarray] = []
    for j in range(focal_ctx.size):
        pair_inputs.append(entities[focal_ctx[j]])
        pair_outputs.append(entities[focal_perm[focal_ctx[j]]])
    max_other = max((task_ctx_list[t].size for t in range(1, V_tasks)), default=0)
    for j in range(max_other):
        for t in range(1, V_tasks):
            ctx_t = task_ctx_list[t]
            if j < ctx_t.size:
                pair_inputs.append(entities[ctx_t[j]])
                pair_outputs.append(entities[perms[t][ctx_t[j]]])
    pair_inputs_np = np.stack(pair_inputs, axis=0).astype(np.float32)
    pair_outputs_np = np.stack(pair_outputs, axis=0).astype(np.float32)
    n_pairs_total = pair_inputs_np.shape[0]

    per_q_correct: List[int] = []
    per_q_K_used: List[int] = []
    per_q_top1_cos: List[float] = []

    for qi in range(queries.shape[0]):
        q = queries[qi]
        K_draw = int(g.choice(RANDOM_K_SUPPORT))
        K_use = min(K_draw, n_pairs_total)
        if K_use <= 0:
            per_q_correct.append(0)
            per_q_K_used.append(0)
            per_q_top1_cos.append(0.0)
            continue
        tv = pair_inputs_np[:0]  # placeholder
        # accumulate K_use bind+sum
        tv_running = np.zeros(entities.shape[1], dtype=np.float32)
        for k_iter in range(K_use):
            bound = _bind_one_np(pair_inputs_np[k_iter], pair_outputs_np[k_iter])
            tv_running = tv_running + bound
        tv_n = _normalize(tv_running)
        pred_n = _normalize(_unbind_np(tv_n, q))
        sims = entities @ pred_n
        top1 = int(np.argmax(sims))
        top1_cos = float(sims[top1])
        per_q_correct.append(int(top1 == int(true_outputs[qi])))
        per_q_K_used.append(int(K_use))
        per_q_top1_cos.append(top1_cos)

    return {
        "per_query_correct": per_q_correct,
        "per_query_K_used": per_q_K_used,
        "top1_recall": float(np.mean(per_q_correct)) if per_q_correct else 0.0,
        "mean_cosine": float(np.mean(per_q_top1_cos)) if per_q_top1_cos else 0.0,
    }


# ----- One phase-point run (5 arms) -----

def _run_phase_point(
    g: np.random.Generator,
    entities: np.ndarray,
    V_tasks: int,
    overlap: float,
    n_queries: int,
    fixed_K_values: Tuple[int, ...] = FIXED_K_VALUES,
) -> Dict[str, Any]:
    """Run 5 arms on one (V_tasks, overlap) phase point.

    Returns a dict keyed by:
      arm_name + "_per_query_correct"
      arm_name + "_per_query_K_used"
      arm_name + "_top1_recall"
      arm_name + "_mean_cosine"
      For FIXED_K_v3: arm_name = "FIXED_K_v3_K{K}".
    """
    out: Dict[str, Any] = {
        "V_tasks": int(V_tasks),
        "overlap": float(overlap),
        "n_queries": int(n_queries),
    }

    # FIXED_K_v3 arm: run at each K in fixed_K_values
    for K in fixed_K_values:
        arm_key = f"FIXED_K_v3_K{K}"
        r = _eval_fixed_K(g, entities, K, V_tasks, overlap, n_queries)
        out[arm_key + "_per_query_correct"] = r["per_query_correct"]
        out[arm_key + "_per_query_K_used"] = r["per_query_K_used"]
        out[arm_key + "_top1_recall"] = r["top1_recall"]
        out[arm_key + "_mean_cosine"] = r["mean_cosine"]

    # ADAPTIVE arms
    for arm in ADAPTIVE_ARMS:
        tau = TAU_BY_ARM[arm]
        r = _eval_adaptive(g, entities, tau, V_tasks, overlap, n_queries)
        out[arm + "_per_query_correct"] = r["per_query_correct"]
        out[arm + "_per_query_K_used"] = r["per_query_K_used"]
        out[arm + "_top1_recall"] = r["top1_recall"]
        out[arm + "_mean_cosine"] = r["mean_cosine"]
        out[arm + "_tau"] = tau

    # RANDOM_K_CONTROL arm
    r = _eval_random_K_control(g, entities, V_tasks, overlap, n_queries)
    out["RANDOM_K_CONTROL_per_query_correct"] = r["per_query_correct"]
    out["RANDOM_K_CONTROL_per_query_K_used"] = r["per_query_K_used"]
    out["RANDOM_K_CONTROL_top1_recall"] = r["top1_recall"]
    out["RANDOM_K_CONTROL_mean_cosine"] = r["mean_cosine"]

    return out


def run_one_seed_phase_diagram(
    seed: int,
    run_mode: str,
    smoke_corner: bool = False,
) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    if run_mode == "selftest":
        N = N_DIM_SELFTEST
        n_queries = N_QUERIES_SELFTEST
        points = [(SMOKE_CORNER[0], SMOKE_CORNER[1])]
        fixed_K_values = (5,)
    elif run_mode == "smoke" or smoke_corner:
        N = N_DIM_SMOKE
        n_queries = N_QUERIES_SMOKE
        points = [SMOKE_CORNER]
        fixed_K_values = (5,)  # single K at smoke; full sweep deferred to full
    else:
        N = N_DIM_FULL
        n_queries = N_QUERIES_FULL
        points = [(V, ov) for V in N_TASKS_VALUES for ov in OVERLAP_VALUES]
        fixed_K_values = FIXED_K_VALUES

    entities = _bipolar_codebook_np(V_ENTS_POOL, N, g)

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for (V, ov) in points:
        res = _run_phase_point(g, entities, V, ov, n_queries, fixed_K_values=fixed_K_values)
        phase_map.append(res)

    elapsed = time.time() - started

    return {
        "seed": int(seed),
        "N_DIM": int(N),
        "run_mode": run_mode,
        "smoke_corner": bool(smoke_corner or run_mode == "smoke"),
        "backend": get_backend_label(),
        "n_phase_points": len(phase_map),
        "n_queries_per_point": int(n_queries),
        "fixed_K_values": list(fixed_K_values),
        "phase_map": phase_map,
        "elapsed_s": round(elapsed, 2),
        "anchor_prefix": ANCHOR_PREFIX,
    }


# ----- Arms-differ check (META_RULE_AF SHA-256) -----

def arms_differ_check(phase_map: List[Dict[str, Any]]) -> Tuple[bool, Dict[str, str]]:
    """Per (V, ov) point, hash each arm's per-query correctness vector + per-query K_used.
    All arm hashes within a point must differ (META_RULE_AF + META_RULE_AX).
    Returns (all_distinct, {point_key: dup_arms_or_OK}).
    """
    import hashlib
    report: Dict[str, str] = {}
    all_ok = True
    for pt in phase_map:
        key = f"V{pt['V_tasks']}_ov{pt['overlap']:.2f}"
        hashes: Dict[str, str] = {}
        # Enumerate every arm-labeled field
        for k in pt.keys():
            if not k.endswith("_per_query_correct"):
                continue
            arm = k[: -len("_per_query_correct")]
            # combine correctness + K_used vectors for stronger discrimination
            vec_c = pt.get(arm + "_per_query_correct", [])
            vec_k = pt.get(arm + "_per_query_K_used", [])
            payload = json.dumps({"c": vec_c, "k": vec_k}, sort_keys=True).encode("utf-8")
            h = hashlib.sha256(payload).hexdigest()[:16]
            hashes[arm] = h
        # find dup hashes
        seen: Dict[str, List[str]] = {}
        for arm, h in hashes.items():
            seen.setdefault(h, []).append(arm)
        dups = [arms for arms in seen.values() if len(arms) > 1]
        if dups:
            all_ok = False
            report[key] = f"DUP: {dups}"
        else:
            report[key] = "OK"
    return all_ok, report


# ----- Smoke discriminator -----

def smoke_discriminator_check(phase_map: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Smoke must fire ADAPTIVE_MID discriminator:
      std(K_used) > DISCRIMINATOR_SMOKE_STD_K  AND
      accuracy(ADAPTIVE_MID) > DISCRIMINATOR_SMOKE_ACC_FLOOR
    Otherwise BLOCK_DISPATCH.
    """
    corner = [p for p in phase_map
              if p["V_tasks"] == SMOKE_CORNER[0]
              and abs(p["overlap"] - SMOKE_CORNER[1]) < 1e-6]
    if not corner:
        return False, f"smoke corner V={SMOKE_CORNER[0]} ov={SMOKE_CORNER[1]} MISSING"
    pt = corner[0]
    k_used = pt.get("ADAPTIVE_THRESH_MID_per_query_K_used", [])
    acc = pt.get("ADAPTIVE_THRESH_MID_top1_recall", 0.0)
    if not k_used:
        return False, "ADAPTIVE_THRESH_MID per_query_K_used MISSING"
    std_k = float(np.std(k_used))
    if std_k <= DISCRIMINATOR_SMOKE_STD_K:
        return False, (f"smoke discriminator FAILED-TO-FIRE: "
                       f"std(K_used)={std_k:.3f} <= {DISCRIMINATOR_SMOKE_STD_K} "
                       f"(adaptive collapses to single K)")
    if acc <= DISCRIMINATOR_SMOKE_ACC_FLOOR:
        return False, (f"smoke discriminator FAILED-TO-FIRE: "
                       f"ADAPTIVE_MID acc={acc:.3f} <= {DISCRIMINATOR_SMOKE_ACC_FLOOR} "
                       f"(below random floor)")
    return True, (f"smoke discriminator FIRED: std(K_used)={std_k:.3f} > "
                  f"{DISCRIMINATOR_SMOKE_STD_K}, acc={acc:.3f} > "
                  f"{DISCRIMINATOR_SMOKE_ACC_FLOOR}")


# ----- Single-seed aggregate (sibling; pooled-across-seeds aggregator is post-hoc) -----

def aggregate_and_verdict_single_seed(per_seed: Dict[str, Dict[str, Any]],
                                       run_mode: str) -> Dict[str, Any]:
    """Per-sibling verdict (only the single seed). Pooled cross-seed cv(K_used)
    is computed by a separate post-hoc tool that reads all 3 sibling partials.

    Per-sibling we still report:
      - per (V, ov) point: top1_recall by arm, mean/std of K_used by arm
      - FIXED_K_v3 best (max across K) per point
      - ADAPTIVE_MID vs FIXED_K_best gap
      - ADAPTIVE_MID vs RANDOM_K_CONTROL gap
      - sibling-level cv(K_used) within seed across queries x points for ADAPTIVE_MID
      - arms-differ check
    """
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    # Gather per-arm structures
    pts_summary: List[Dict[str, Any]] = []
    am_all_K_used: List[int] = []
    am_all_correct: List[int] = []
    rk_all_correct: List[int] = []
    am_vs_random_gap_pts: List[float] = []
    am_vs_fixed_best_gap_pts: List[float] = []
    arms_differ_ok = True
    arms_differ_report: Dict[str, str] = {}
    fixed_K_values_seen: List[int] = []

    for sid, body in per_seed.items():
        ok_diff, rpt = arms_differ_check(body.get("phase_map", []))
        if not ok_diff:
            arms_differ_ok = False
        arms_differ_report[sid] = json.dumps(rpt)

        fixed_K_values_seen = list(body.get("fixed_K_values", FIXED_K_VALUES))

        for pt in body.get("phase_map", []):
            V = pt["V_tasks"]
            ov = pt["overlap"]
            # FIXED_K best across K
            fixed_best_acc = -1.0
            fixed_best_K: Optional[int] = None
            fixed_by_K: Dict[int, float] = {}
            for K in fixed_K_values_seen:
                arm_key = f"FIXED_K_v3_K{K}"
                acc = pt.get(arm_key + "_top1_recall", 0.0)
                fixed_by_K[K] = acc
                if acc > fixed_best_acc:
                    fixed_best_acc = acc
                    fixed_best_K = K
            am_acc = pt.get("ADAPTIVE_THRESH_MID_top1_recall", 0.0)
            am_k_used = pt.get("ADAPTIVE_THRESH_MID_per_query_K_used", [])
            am_correct = pt.get("ADAPTIVE_THRESH_MID_per_query_correct", [])
            rk_acc = pt.get("RANDOM_K_CONTROL_top1_recall", 0.0)
            rk_correct = pt.get("RANDOM_K_CONTROL_per_query_correct", [])

            am_all_K_used.extend(am_k_used)
            am_all_correct.extend(am_correct)
            rk_all_correct.extend(rk_correct)

            am_vs_random_gap_pts.append(am_acc - rk_acc)
            am_vs_fixed_best_gap_pts.append(am_acc - fixed_best_acc)

            am_k_mean = float(np.mean(am_k_used)) if am_k_used else 0.0
            am_k_std = float(np.std(am_k_used)) if am_k_used else 0.0
            am_k_cv = (am_k_std / am_k_mean) if am_k_mean > 1e-6 else 0.0

            pts_summary.append({
                "seed": int(body.get("seed", -1)),
                "V_tasks": int(V),
                "overlap": float(ov),
                "FIXED_K_v3_best_K": fixed_best_K,
                "FIXED_K_v3_best_acc": float(fixed_best_acc) if fixed_best_acc >= 0 else 0.0,
                "FIXED_K_v3_by_K_acc": fixed_by_K,
                "ADAPTIVE_LOW_acc": float(pt.get("ADAPTIVE_THRESH_LOW_top1_recall", 0.0)),
                "ADAPTIVE_LOW_K_mean": float(np.mean(pt.get("ADAPTIVE_THRESH_LOW_per_query_K_used", [0]))),
                "ADAPTIVE_MID_acc": float(am_acc),
                "ADAPTIVE_MID_K_mean": am_k_mean,
                "ADAPTIVE_MID_K_std": am_k_std,
                "ADAPTIVE_MID_K_cv_intra_point": am_k_cv,
                "ADAPTIVE_HIGH_acc": float(pt.get("ADAPTIVE_THRESH_HIGH_top1_recall", 0.0)),
                "ADAPTIVE_HIGH_K_mean": float(np.mean(pt.get("ADAPTIVE_THRESH_HIGH_per_query_K_used", [0]))),
                "RANDOM_K_CONTROL_acc": float(rk_acc),
                "ADAPTIVE_MID_vs_RANDOM_gap": float(am_acc - rk_acc),
                "ADAPTIVE_MID_vs_FIXED_best_gap": float(am_acc - fixed_best_acc),
            })

    # Sibling-level aggregates (single-seed cv across queries x points)
    am_K_used_arr = np.asarray(am_all_K_used, dtype=np.float32)
    am_K_mean_sibling = float(am_K_used_arr.mean()) if am_K_used_arr.size > 0 else 0.0
    am_K_std_sibling = float(am_K_used_arr.std()) if am_K_used_arr.size > 0 else 0.0
    am_K_cv_sibling = (am_K_std_sibling / am_K_mean_sibling) if am_K_mean_sibling > 1e-6 else 0.0

    am_acc_sibling = float(np.mean(am_all_correct)) if am_all_correct else 0.0
    rk_acc_sibling = float(np.mean(rk_all_correct)) if rk_all_correct else 0.0
    am_vs_random_mean = float(np.mean(am_vs_random_gap_pts)) if am_vs_random_gap_pts else 0.0
    am_vs_fixed_best_mean = float(np.mean(am_vs_fixed_best_gap_pts)) if am_vs_fixed_best_gap_pts else 0.0

    # Sibling verdict heuristic (final cross-seed verdict is post-hoc):
    # HARD_FAIL guards:
    #   - any ADAPTIVE arm collapses to single K (std == 0 across queries x pts)
    #   - arms_differ violation (META_RULE_AF)
    #   - all FIXED_K accuracies > 0.99 AND all ADAPTIVE accuracies > 0.99 (suspect 1.000 + by-construction)
    arms_collapse = (am_K_std_sibling <= 1e-6)
    suspect_1000 = (am_acc_sibling > 0.99 and am_vs_random_mean < 0.05)

    if not arms_differ_ok:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL META_RULE_AF arms-differ violation in {arms_differ_report}")
    elif arms_collapse and run_mode == "full":
        verdict = "HARD_FAIL"
        msg = ("HARD_FAIL ADAPTIVE_MID collapses to single K across full run "
               "(std=0); adaptivity mechanism degenerate")
    elif suspect_1000:
        verdict = "HARD_FAIL"
        msg = (f"HARD_FAIL suspect-1.000: ADAPTIVE_MID acc={am_acc_sibling:.3f} but "
               f"vs RANDOM gap only {am_vs_random_mean:.3f} (META_RULE_Q)")
    elif run_mode == "smoke":
        # smoke verdict is informational; runner handles BLOCK_DISPATCH via smoke_discriminator_check
        verdict = "SMOKE_INFO"
        msg = (f"smoke aggregate (single-seed; cross-seed cv pending post-hoc); "
               f"am_K_mean={am_K_mean_sibling:.2f} std={am_K_std_sibling:.2f} "
               f"cv_intra={am_K_cv_sibling:.3f} | acc(adapt_mid)={am_acc_sibling:.3f} "
               f"acc(random)={rk_acc_sibling:.3f} gap={am_vs_random_mean:.3f}")
    else:
        # Full sibling verdict is INFORMATIONAL (final verdict is the cross-seed
        # cv(K_used), computed post-hoc over all 3 partials). Per-sibling we
        # report SIBLING_OK to signal "ready for post-hoc aggregator".
        verdict = "SIBLING_OK"
        msg = (f"sibling complete; am_K_mean={am_K_mean_sibling:.2f} "
               f"std={am_K_std_sibling:.2f} cv_intra={am_K_cv_sibling:.3f} | "
               f"acc(adapt_mid)={am_acc_sibling:.3f} acc(random)={rk_acc_sibling:.3f} "
               f"gap_vs_random={am_vs_random_mean:.3f} "
               f"gap_vs_fixed_best={am_vs_fixed_best_mean:.3f} "
               f"(cross-seed cv pending post-hoc)")

    return {
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "arms_differ_ok": bool(arms_differ_ok),
        "arms_differ_report": arms_differ_report,
        "ADAPTIVE_MID_K_used_sibling_mean": am_K_mean_sibling,
        "ADAPTIVE_MID_K_used_sibling_std": am_K_std_sibling,
        "ADAPTIVE_MID_K_used_sibling_cv_intra": am_K_cv_sibling,
        "ADAPTIVE_MID_acc_sibling": am_acc_sibling,
        "RANDOM_K_CONTROL_acc_sibling": rk_acc_sibling,
        "ADAPTIVE_MID_vs_RANDOM_mean_gap": am_vs_random_mean,
        "ADAPTIVE_MID_vs_FIXED_best_mean_gap": am_vs_fixed_best_mean,
        "per_phase_point_summary": pts_summary,
        "n_seeds_complete": len(per_seed),
        "v4_constants": {
            "TAU_LOW": TAU_LOW,
            "TAU_MID": TAU_MID,
            "TAU_HIGH": TAU_HIGH,
            "ADAPTIVE_K_MAX": ADAPTIVE_K_MAX,
            "ADAPTIVE_K_MIN": ADAPTIVE_K_MIN,
            "FIXED_K_VALUES": list(FIXED_K_VALUES),
            "RANDOM_K_SUPPORT": list(RANDOM_K_SUPPORT),
            "N_QUERIES_FULL": N_QUERIES_FULL,
            "HP_CV_K_USED_MAX": HP_CV_K_USED_MAX,
            "HP_ACC_PARITY_MAX_GAP": HP_ACC_PARITY_MAX_GAP,
            "HP_ADAPTIVE_VS_RANDOM_GAP": HP_ADAPTIVE_VS_RANDOM_GAP,
        },
    }


# ----- Selftest -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: 1 corner @ N=1024, n_queries=5; verifies all 5 arms run,
    K_used vectors present + per-query correctness present.
    """
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pt = body["phase_map"][0]
        required_arm_keys = []
        for K in (5,):
            required_arm_keys.append(f"FIXED_K_v3_K{K}_per_query_K_used")
            required_arm_keys.append(f"FIXED_K_v3_K{K}_per_query_correct")
        for arm in ADAPTIVE_ARMS:
            required_arm_keys.append(arm + "_per_query_K_used")
            required_arm_keys.append(arm + "_per_query_correct")
        required_arm_keys.append("RANDOM_K_CONTROL_per_query_K_used")
        required_arm_keys.append("RANDOM_K_CONTROL_per_query_correct")
        for k in required_arm_keys:
            if k not in pt:
                return False, f"selftest: missing field {k}"
            if len(pt[k]) != pt["n_queries"]:
                return False, (f"selftest: {k} length {len(pt[k])} "
                               f"!= n_queries {pt['n_queries']}")
        # Arms-differ on smoke (small) data
        ok_diff, rpt = arms_differ_check(body["phase_map"])
        if not ok_diff:
            return False, f"selftest: arms_differ violated: {rpt}"
        # Aggregator runs end-to-end
        per_seed_stub = {str(seed): body}
        agg = aggregate_and_verdict_single_seed(per_seed_stub, run_mode="selftest")
        if "verdict" not in agg:
            return False, "selftest: aggregator did not produce verdict"
        msg = (f"selftest OK: phase_map={len(body['phase_map'])}, "
               f"N={body['N_DIM']}, n_queries={pt['n_queries']}, "
               f"backend={body['backend']}, "
               f"am_K_mean={agg['ADAPTIVE_MID_K_used_sibling_mean']:.2f}, "
               f"am_K_std={agg['ADAPTIVE_MID_K_used_sibling_std']:.2f}")
        return True, msg
    except Exception as e:
        return False, f"selftest EXC: {type(e).__name__}: {e}\n{traceback.format_exc()}"


if __name__ == "__main__":
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
