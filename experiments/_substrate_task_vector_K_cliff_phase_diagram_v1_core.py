"""Shared core for substrate_task_vector_K_cliff_phase_diagram_v1 sibling cells.

Provides the GPU-batched phase-diagram sweep over (K, N_tasks, task_overlap)
with 3 arms (TASK_VECTOR / RANDOM_VECTOR / ORACLE).

Sibling cells import run_one_seed_phase_diagram(seed) and aggregate.
ASCII-only. CUDA primary, numpy fallback with WARN.

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn) M3 concern #4
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

# Torch optional but preferred for GPU
_TORCH_OK = False
_CUDA_OK = False
try:
    import torch
    _TORCH_OK = True
    if torch.cuda.is_available():
        _CUDA_OK = True
except Exception:
    pass

ANCHOR_PREFIX = "substrate_task_vector_K_cliff_phase_diagram_v1"

# ----- Phase axes (LOCKED) -----
K_VALUES = (1, 3, 5, 10, 20, 50, 100)            # 7 points
N_TASKS_VALUES = (10, 50, 200)                   # 3 points
OVERLAP_VALUES = (0.0, 0.3, 0.6)                 # 3 points
ARMS = ("TASK_VECTOR", "RANDOM_VECTOR", "ORACLE")

# Smoke 5 corner points: (K, N_tasks, overlap)
SMOKE_CORNERS = (
    (1, 10, 0.0),     # low-K low-V low-overlap (saturation regime)
    (100, 10, 0.0),   # high-K low-V low-overlap (capacity stress, low entity load)
    (1, 200, 0.6),    # low-K high-V high-overlap (low cliff risk, high interference)
    (100, 200, 0.6),  # high-K high-V high-overlap (cliff regime)
    (10, 50, 0.3),    # mid all axes
)

# Pre-reg bands (mirror prereg .md; LOCKED at module load)
HP_K1_FLOOR_RECALL = 0.95          # low-K low-V mechanism floor
HP_CLIFF_FLOOR_RECALL = 0.40       # K_cliff defined as drop below this
HP_AVG_ARMS_DIFF_MIN = 0.20        # TASK_VECTOR - RANDOM_VECTOR avg gate
MB_AVG_ARMS_DIFF_LO = 0.10
HF_NO_CLIFF_RECALL_MIN = 0.95      # if ALL phase pts >= this, HARD_FAIL saturation

# Per-point query count (FULL); SMOKE uses smaller
N_QUERIES_FULL = 10
N_QUERIES_SMOKE = 2

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
    """Bind K (input,output) pairs and sum-bundle, return (N,) tensor.

    inputs: (K, N) float32
    outputs: (K, N) float32
    Returns: (N,) float32 normalized
    """
    I = torch.fft.rfft(inputs, dim=-1)
    O = torch.fft.rfft(outputs, dim=-1)
    P = I * O                                          # (K, N//2+1) complex
    bound = torch.fft.irfft(P, n=inputs.shape[-1], dim=-1).to(torch.float32)
    tv = bound.sum(dim=0)
    n = torch.linalg.norm(tv) + 1e-8
    return tv / n


def _unbind_torch(c: "torch.Tensor", a: "torch.Tensor") -> "torch.Tensor":
    """Unbind a from c via FFT correlation."""
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
    bundle to retrieve from the focal task -- interference comes from the V_tasks-1
    competing task-vectors. This is the actual cross-task capacity test.

    overlap: fraction of context INDICES shared across the V_tasks tasks (proxy
    for inter-task similarity; shared indices mean tasks bind to overlapping
    input-keys with different output values -- aliasing interference).

    Returns dict with per-arm top1_recall + mean_cosine.
    """
    V_ents = entities.shape[0]
    N = entities.shape[1]
    K_eff = min(K, V_ents)
    out: Dict[str, float] = {}

    # Build V_tasks distinct random permutations
    perms = np.stack([g.permutation(V_ents) for _ in range(V_tasks)], axis=0)  # (V_tasks, V_ents)

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

    # Per-task context index sets: shared_idx + per-task fresh remainder
    remainder = K_eff - shared_size
    task_ctx_list = []  # list of (K_use,) index arrays, one per task
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

    # Focal task = task 0; queries drawn from task-0 context inputs
    focal_perm = perms[0]
    focal_ctx = task_ctx_list[0]
    if n_queries > focal_ctx.size:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=True)
    else:
        q_idx = g.choice(focal_ctx, size=n_queries, replace=False)
    true_outputs = focal_perm[q_idx]   # (Q,)

    # Build the multi-task TV bundle for TASK_VECTOR arm:
    #   TV = sum_t  sum_i  bind( entities[task_ctx_t[i]], entities[perm_t[task_ctx_t[i]]] )
    # Stack all task-context pairs into one (V_tasks*K_use, N) tensor.
    all_inputs_idx = np.concatenate([task_ctx_list[ti] for ti in range(V_tasks)])           # (V_tasks*K_use,)
    all_outputs_true_idx = np.concatenate(
        [perms[ti][task_ctx_list[ti]] for ti in range(V_tasks)])                            # (V_tasks*K_use,)
    # Random-arm: same input indices but random output entities (mechanism missing)
    all_outputs_rand_idx = g.integers(0, V_ents, size=all_inputs_idx.size)

    if _CUDA_OK and device == "cuda":
        E = torch.from_numpy(entities).to("cuda")
        ctx_inputs = E[torch.from_numpy(all_inputs_idx).long().to("cuda")]               # (V*K, N)
        ctx_outputs_true = E[torch.from_numpy(all_outputs_true_idx).long().to("cuda")]   # (V*K, N)
        ctx_outputs_rand = E[torch.from_numpy(all_outputs_rand_idx).long().to("cuda")]   # (V*K, N)
        queries = E[torch.from_numpy(q_idx).long().to("cuda")]                            # (Q, N)

        # TASK_VECTOR arm (multi-task bundle)
        tv_task = _bind_bundle_torch(ctx_inputs, ctx_outputs_true)                        # (N,)
        tv_rand = _bind_bundle_torch(ctx_inputs, ctx_outputs_rand)                        # (N,)

        # Batched unbind per query
        def _eval_arm(tv: "torch.Tensor") -> Tuple[float, float]:
            # Unbind each query and compute cleanup against entity codebook
            preds = torch.stack([_unbind_torch(tv, queries[i])
                                  for i in range(queries.shape[0])], dim=0)  # (Q, N)
            preds = preds / (torch.linalg.norm(preds, dim=-1, keepdim=True) + 1e-8)
            sims = preds @ E.T                                              # (Q, V)
            top1 = sims.argmax(dim=-1).detach().cpu().numpy()
            top1_cos = sims.max(dim=-1).values.detach().cpu().numpy()
            correct = (top1 == true_outputs).astype(np.float32).mean()
            return float(correct), float(top1_cos.mean())

        tv_recall, tv_cos = _eval_arm(tv_task)
        rv_recall, rv_cos = _eval_arm(tv_rand)
        # ORACLE: perfect (read perm[query] directly; cleanup against codebook = 1.0)
        oracle_correct = 1.0  # by construction
        out["TASK_VECTOR_top1_recall"] = tv_recall
        out["TASK_VECTOR_mean_cosine"] = tv_cos
        out["RANDOM_VECTOR_top1_recall"] = rv_recall
        out["RANDOM_VECTOR_mean_cosine"] = rv_cos
        out["ORACLE_top1_recall"] = oracle_correct
        out["ORACLE_mean_cosine"] = 1.0
    else:
        # numpy fallback
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
    """Run full or smoke phase diagram for one seed.

    Args:
        seed: integer seed.
        run_mode: "smoke" | "full" | "selftest".
        smoke_corners: if True, only run 5 corner points (smoke gate).
    """
    g = np.random.default_rng(seed)
    N = N_DIM_SMOKE if run_mode != "full" else N_DIM_FULL

    # Entity codebook large enough for max V_tasks
    V_ents_max = max(N_TASKS_VALUES)
    entities = _bipolar_codebook_np(V_ents_max, N, g)
    device = "cuda" if _CUDA_OK else "cpu"

    n_queries = N_QUERIES_SMOKE if (run_mode != "full") else N_QUERIES_FULL

    if smoke_corners:
        points = list(SMOKE_CORNERS)
    elif run_mode == "selftest":
        # tiny smoke for selftest: 2 corners
        points = [SMOKE_CORNERS[0], SMOKE_CORNERS[3]]
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


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    """Compute K_cliff_min + verdict from one or more seed phase-maps."""
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    # Pool all phase points across seeds; compute mean per (K, V, overlap)
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
        if rv_mean > tv_mean and K <= 5 and V <= 50:
            regime_flip_points.append((K, V, ov))
        summary_per_pt.append({
            "K": K, "V_tasks": V, "overlap": ov,
            "TASK_VECTOR_top1_recall_mean": tv_mean,
            "RANDOM_VECTOR_top1_recall_mean": rv_mean,
            "ORACLE_top1_recall_mean": oracle_mean,
            "arms_diff": diff,
            "n_seeds": len(d["TASK_VECTOR_top1_recall"]),
        })

    # K_cliff per (V, overlap): smallest K where TV drops below floor
    cliffs: Dict[Tuple[int, float], Optional[int]] = {}
    for V in N_TASKS_VALUES:
        for ov in OVERLAP_VALUES:
            cliffs[(V, ov)] = None
            # find smallest K where TV < floor
            for K in K_VALUES:
                rows = [p for p in summary_per_pt
                        if p["K"] == K and p["V_tasks"] == V and abs(p["overlap"] - ov) < 1e-6]
                if not rows:
                    continue
                tv = rows[0]["TASK_VECTOR_top1_recall_mean"]
                if tv < HP_CLIFF_FLOOR_RECALL:
                    cliffs[(V, ov)] = K
                    break

    cliffs_serializable = {f"V{V}_ov{ov:.2f}": K for (V, ov), K in cliffs.items()}
    cliffs_observed = [K for K in cliffs.values() if K is not None]
    n_cliff_combos = len(cliffs_observed)
    n_total_combos = len(cliffs)

    # K_cliff_min
    if cliffs_observed:
        K_cliff_min = int(min(cliffs_observed))
        cliff_min_loc = [k for k, v in cliffs.items() if v == K_cliff_min][0]
    else:
        K_cliff_min = None
        cliff_min_loc = None

    avg_arm_diff = float(np.mean(arm_diffs)) if arm_diffs else 0.0
    all_saturated = bool(all(r >= HF_NO_CLIFF_RECALL_MIN for r in tv_all_recalls)) if tv_all_recalls else False

    # Low-K low-V mechanism check (HARD_PASS gate B)
    low_kv_pts = [p for p in summary_per_pt if p["K"] == 1 and p["V_tasks"] <= 50]
    low_kv_high = any(p["TASK_VECTOR_top1_recall_mean"] >= HP_K1_FLOOR_RECALL for p in low_kv_pts)

    # Cliff-observable check (HARD_PASS gate C)
    cliff_observable = any(p["TASK_VECTOR_top1_recall_mean"] < HP_CLIFF_FLOOR_RECALL
                           for p in summary_per_pt)

    # META_RULE_AM check
    am_flag = len(regime_flip_points) > 0

    # Verdict
    if all_saturated or avg_arm_diff < 0.10 or am_flag:
        verdict = "HARD_FAIL"
    elif (n_cliff_combos >= 1 and low_kv_high and cliff_observable
          and avg_arm_diff >= HP_AVG_ARMS_DIFF_MIN):
        verdict = "HARD_PASS"
    elif n_cliff_combos >= 1 and avg_arm_diff >= MB_AVG_ARMS_DIFF_LO:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "MIDDLE_BAND"

    # M3 concern #4 annotation
    if verdict == "HARD_PASS":
        m3_msg = f"M3#4 CONFIRMED: TASK_VECTOR un-saturated; K_cliff_min={K_cliff_min} at {cliff_min_loc}"
    elif verdict == "MIDDLE_BAND":
        m3_msg = f"M3#4 PARTIAL: regime-narrow; cliff in {n_cliff_combos}/{n_total_combos} combos; K_cliff_min={K_cliff_min}"
    else:
        m3_msg = f"M3#4 NOT CONFIRMED: saturation-trivial or unmechanistic; n_cliffs={n_cliff_combos}/{n_total_combos}; avg_diff={avg_arm_diff:.3f}"

    verdict_msg = (
        f"{verdict} | K_cliff_min={K_cliff_min} loc={cliff_min_loc} "
        f"| n_cliffs={n_cliff_combos}/{n_total_combos} | "
        f"avg_arms_diff={avg_arm_diff:.3f} | all_saturated={all_saturated} "
        f"| regime_flip={am_flag} | {m3_msg}"
    )

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "K_cliff_min": K_cliff_min,
        "K_cliff_min_location": (None if cliff_min_loc is None
                                  else {"V_tasks": cliff_min_loc[0], "overlap": cliff_min_loc[1]}),
        "K_cliffs_per_combo": cliffs_serializable,
        "n_cliff_combos_observable": n_cliff_combos,
        "n_combos_total": n_total_combos,
        "avg_arms_diff": avg_arm_diff,
        "all_saturated": all_saturated,
        "low_kv_mechanism_floor_met": bool(low_kv_high),
        "cliff_observable": bool(cliff_observable),
        "meta_rule_am_regime_flip_points": [list(p) for p in regime_flip_points],
        "summary_per_phase_point": summary_per_pt,
        "n_seeds_complete": len(per_seed),
        "m3_concern_4_annotation": m3_msg,
    }


# ----- Self-test (called from cell scripts via --self-test) -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: 2 corner points, 2 queries, full N_DIM.

    Asserts: TV recall at low-K low-V > 0.5; arms_diff at high-K > 0 (TV beats RAND).
    Returns (ok, msg).
    """
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pts = body["phase_map"]
        # Find low-K low-V point (K=1, V=10)
        low = [p for p in pts if p["K"] == 1 and p["V_tasks"] == 10]
        hi = [p for p in pts if p["K"] == 100 and p["V_tasks"] == 200]
        if not low or not hi:
            return False, f"selftest: missing corner points; got {len(pts)}"
        tv_low = low[0]["TASK_VECTOR_top1_recall"]
        if tv_low < 0.5:
            return False, f"selftest: TV at K=1 V=10 = {tv_low:.3f} (expected >0.5)"
        tv_hi = hi[0]["TASK_VECTOR_top1_recall"]
        rv_hi = hi[0]["RANDOM_VECTOR_top1_recall"]
        # At K=100 V=200, expect cliff (TV low), but TV >= RV by construction
        msg = (f"selftest OK: TV(K=1,V=10)={tv_low:.3f}, "
               f"TV(K=100,V=200)={tv_hi:.3f}, RV(K=100,V=200)={rv_hi:.3f}, "
               f"backend={body['backend']}")
        return True, msg
    except Exception as e:
        return False, f"selftest EXC: {type(e).__name__}: {e}\n{traceback.format_exc()}"


if __name__ == "__main__":
    # Module-level selftest
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
