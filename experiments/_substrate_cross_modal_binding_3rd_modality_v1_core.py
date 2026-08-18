"""Shared core for substrate_cross_modal_binding_3rd_modality_v1 sibling cells.

Stage 3 cross-modal binding EXTENSION: 3 modalities (visual + auditory + tactile).
Composes on cross-modal CG (2-mod visual+auditory chain-graded 2026-06-28).

Question: does HRR-bind cross-modal mechanism survive 3-modality binding, or
does the 3-way conjunction (bind3(V,A,T)) saturate / lose lift vs baseline?

Mechanisms (3-arm bind sweep):
  - HRR_bind3           : C_i = bind(V[i], bind(A[i], T[i])); query V[i]+A[i]
                          => unbind_sequential(C_sum, V[i], A[i]) -> T_hat
  - sum_then_query      : C_i = V[i] + A[i] + T[i] (no binding); query V[i]+A[i]
                          => C_sum - V[i] - A[i]
  - position_key_bind3  : C_i = bind(P_i,V[i]) + bind(P_i,A[i]) + bind(P_i,T[i]);
                          query V[i] + position -> hop via P_i -> retrieve T[i]

Discriminator arms (3 per phase point):
  - ARM_BIND_3MOD             : substrate-bound 3-way; query V+A -> retrieve T
  - ARM_NO_BIND_BASELINE      : substrate has NO bind (random vec); chance retrieval
  - ARM_2MOD_BIND_CONTROL     : same mechanism but bind V<->T only (2-mod); query V -> T
                                Compares 3-mod vs 2-mod at same K, N, mechanism.

Discriminator (per task-spec):
  - cross-modal recall > 0.70 with cv < 10% at pos-control corner
    (K=10, N=8192, HRR_bind3)
  - 3-mod BIND vs NO_BIND lift >= 0.30 at >=8 of 45 grid points (relaxed from
    2-mod 0.40 lift due to expected 3-way capacity cost)

ASCII-only. CPU-first per task spec.

Author: exp_dev 2026-06-30 (Opus 4.7 1M) Stage 3 3-modality extension
"""
from __future__ import annotations

import torch

import math
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_TORCH_OK = True
_CUDA_OK = bool(torch.cuda.is_available())

ANCHOR_PREFIX = "substrate_cross_modal_binding_3rd_modality_v1"

# ----- Phase axes (LOCKED per pre-reg) -----
K_VALUES = (10, 50, 100, 500, 1000)                                # 5 points
N_VALUES = (2048, 4096, 8192)                                       # 3 points
BIND_MECHANISMS = ("HRR_bind3", "sum_then_query", "position_key_bind3")  # 3
DISCRIMINATOR_ARMS = ("BIND_3MOD", "NO_BIND_BASELINE",
                       "TWO_MOD_BIND_CONTROL")
N_PHASE_POINTS_FULL = len(K_VALUES) * len(N_VALUES) * len(BIND_MECHANISMS)  # 45

# Smoke corners (6 points -- low-K saturate / high-K cliff / mid):
SMOKE_CORNERS = (
    (10,   8192, "HRR_bind3"),           # sat regime
    (1000, 2048, "HRR_bind3"),           # cliff regime
    (10,   2048, "sum_then_query"),      # low-K low-N sum baseline
    (1000, 8192, "sum_then_query"),      # high-K high-N sum baseline
    (100,  4096, "position_key_bind3"),  # mid pos-key
    (500,  8192, "position_key_bind3"),  # higher-K pos-key
)

# Per-point query count
N_QUERIES_FULL = 20
N_QUERIES_SMOKE = 4

# Modality codebook sizes; must be >= max K
V_MOD_A = 2048   # visual codebook
V_MOD_B = 2048   # auditory codebook
V_MOD_C = 2048   # tactile codebook (3rd modality)
V_POS = 2048

# ----- Pre-reg bands (LOCKED at module load) -----
# HARD_PASS: cross-modal recall > 0.70 with cv < 10% at pos-control corner
HP_POS_CONTROL_MIN_RECALL = 0.70
HP_POS_CONTROL_MAX_CV = 0.10
# HARD_PASS: 3-mod BIND > NO_BIND lift >= 0.30 at >=8 of 45 grid points
HP_BIND_LIFT_MIN = 0.30
HP_MIN_DISCRIMINATING_POINTS = 8
# HARD_PASS: 3-mod vs 2-mod control ratio >= 0.50 at >=8 points
# (3-mod may be lower than 2-mod but should retain substantial fraction)
HP_3VS2_RATIO_MIN = 0.50
HP_3VS2_MIN_POINTS = 8
# HARD_FAIL: BIND == NO_BIND (mechanism broken at 3 modalities)
HF_ARMS_IDENTICAL_TOL = 0.05
# HARD_FAIL by-construction-saturation: ALL points >= 0.99
HF_ALL_SATURATED_THRESHOLD = 0.99
# MIDDLE_BAND: 3-7 discriminating points
MB_MIN_DISCRIMINATING_POINTS = 3

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    if _CUDA_OK:
        return "torch.cuda"
    if _TORCH_OK:
        return "torch.cpu"
    return "numpy.cpu"


# ----- HRR primitives -----

def _bipolar_codebook_torch(V: int, N: int, gen: torch.Generator,
                             device: str) -> torch.Tensor:
    X = (torch.randint(0, 2, (V, N), generator=gen, device=device,
                       dtype=torch.float32) * 2 - 1)
    X = X / (torch.linalg.norm(X, dim=1, keepdim=True) + 1e-8)
    return X


def _bind_pair_torch(a: torch.Tensor, b: torch.Tensor) -> torch.Tensor:
    """HRR bind a to b via FFT circular convolution."""
    A = torch.fft.rfft(a, dim=-1)
    B = torch.fft.rfft(b, dim=-1)
    PROD = A * B
    return torch.fft.irfft(PROD, n=a.shape[-1], dim=-1).to(torch.float32)


def _unbind_torch(c: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
    """Unbind a from c via FFT correlation."""
    C = torch.fft.rfft(c, dim=-1)
    A = torch.fft.rfft(a, dim=-1)
    R = C * torch.conj(A)
    return torch.fft.irfft(R, n=c.shape[-1], dim=-1).to(torch.float32)


def _normalize_torch(x: torch.Tensor) -> torch.Tensor:
    return x / (torch.linalg.norm(x, dim=-1, keepdim=True) + 1e-8)


# ----- Mechanism implementations (3-modality) -----

def _build_bundle_hrr3(items_a: torch.Tensor, items_b: torch.Tensor,
                        items_c: torch.Tensor,
                        positions: torch.Tensor) -> torch.Tensor:
    """HRR_bind3: C = sum_i bind(a_i, bind(b_i, c_i)). 3-way conjunctive bind."""
    inner = _bind_pair_torch(items_b, items_c)     # (K, N)
    bound = _bind_pair_torch(items_a, inner)        # (K, N)
    bundle = bound.sum(dim=0)
    return _normalize_torch(bundle)


def _build_bundle_sum3(items_a: torch.Tensor, items_b: torch.Tensor,
                       items_c: torch.Tensor,
                       positions: torch.Tensor) -> torch.Tensor:
    """sum_then_query: C = sum_i (a_i + b_i + c_i). No binding."""
    bundle = (items_a + items_b + items_c).sum(dim=0)
    return _normalize_torch(bundle)


def _build_bundle_position_key3(items_a: torch.Tensor, items_b: torch.Tensor,
                                 items_c: torch.Tensor,
                                 positions: torch.Tensor) -> torch.Tensor:
    """position_key_bind3: C = sum_i [bind(p,a) + bind(p,b) + bind(p,c)]."""
    pa = _bind_pair_torch(positions, items_a)
    pb = _bind_pair_torch(positions, items_b)
    pc = _bind_pair_torch(positions, items_c)
    bundle = (pa + pb + pc).sum(dim=0)
    return _normalize_torch(bundle)


def _query_hrr3_cross(bundle: torch.Tensor, query_a: torch.Tensor,
                       query_b: torch.Tensor,
                       positions_q: torch.Tensor) -> torch.Tensor:
    """HRR_bind3 query: unbind a, then unbind b -> recover c."""
    step1 = _unbind_torch(bundle, query_a)          # ~ bind(b, c) + noise
    step2 = _unbind_torch(step1, query_b)            # ~ c + noise
    return _normalize_torch(step2)


def _query_sum3_cross(bundle: torch.Tensor, query_a: torch.Tensor,
                       query_b: torch.Tensor,
                       positions_q: torch.Tensor) -> torch.Tensor:
    """sum_then_query 3-mod: subtract a and b from bundle."""
    return _normalize_torch(bundle - _normalize_torch(query_a)
                            - _normalize_torch(query_b))


def _query_position_key3_cross(bundle: torch.Tensor, query_a: torch.Tensor,
                                 query_b: torch.Tensor,
                                 positions_q: torch.Tensor) -> torch.Tensor:
    """position_key_bind3 query: unbind position -> (a+b+c+noise); subtract a, b."""
    unbound = _unbind_torch(bundle, positions_q)
    rem = unbound - _normalize_torch(query_a) - _normalize_torch(query_b)
    return _normalize_torch(rem)


_BUNDLE_BUILDERS = {
    "HRR_bind3": _build_bundle_hrr3,
    "sum_then_query": _build_bundle_sum3,
    "position_key_bind3": _build_bundle_position_key3,
}
_QUERY_FNS_CROSS = {
    "HRR_bind3": _query_hrr3_cross,
    "sum_then_query": _query_sum3_cross,
    "position_key_bind3": _query_position_key3_cross,
}


# ----- One phase-point evaluation (3 discriminator arms) -----

def _run_phase_point(
    g_torch: torch.Generator,
    g_np: np.random.Generator,
    K: int,
    N: int,
    mechanism: str,
    n_queries: int,
    device: str,
) -> Dict[str, float]:
    """Run BIND_3MOD / NO_BIND / TWO_MOD_CONTROL arms."""
    book_a = _bipolar_codebook_torch(V_MOD_A, N, g_torch, device)  # visual
    book_b = _bipolar_codebook_torch(V_MOD_B, N, g_torch, device)  # auditory
    book_c = _bipolar_codebook_torch(V_MOD_C, N, g_torch, device)  # tactile
    book_pos = _bipolar_codebook_torch(V_POS, N, g_torch, device)

    idx_a = g_np.choice(V_MOD_A, size=K, replace=False)
    idx_b = g_np.choice(V_MOD_B, size=K, replace=False)
    idx_c = g_np.choice(V_MOD_C, size=K, replace=False)
    idx_pos = g_np.choice(V_POS, size=K, replace=False)

    items_a = book_a[torch.from_numpy(idx_a).long().to(device)]
    items_b = book_b[torch.from_numpy(idx_b).long().to(device)]
    items_c = book_c[torch.from_numpy(idx_c).long().to(device)]
    positions = book_pos[torch.from_numpy(idx_pos).long().to(device)]

    # Build substrate bundle (3-modality store)
    bundle_substrate = _BUNDLE_BUILDERS[mechanism](items_a, items_b, items_c,
                                                     positions)

    # ARM_NO_BIND: substrate is just random
    bundle_no_bind = torch.randn((N,), generator=g_torch, device=device,
                                   dtype=torch.float32)
    bundle_no_bind = _normalize_torch(bundle_no_bind)

    if n_queries > K:
        q_local = g_np.choice(K, size=n_queries, replace=True)
    else:
        q_local = g_np.choice(K, size=n_queries, replace=False)

    q_idx_a = idx_a[q_local]
    q_idx_b = idx_b[q_local]
    q_idx_c = idx_c[q_local]
    q_idx_pos = idx_pos[q_local]
    q_items_a = book_a[torch.from_numpy(q_idx_a).long().to(device)]
    q_items_b = book_b[torch.from_numpy(q_idx_b).long().to(device)]
    q_positions = book_pos[torch.from_numpy(q_idx_pos).long().to(device)]
    q_true_c = torch.from_numpy(q_idx_c).long().to(device)

    query_fn = _QUERY_FNS_CROSS[mechanism]

    def _eval_3mod_arm(bundle, queries_a, queries_b, queries_pos, true_c_idx):
        preds = torch.stack([query_fn(bundle, queries_a[i], queries_b[i],
                                       queries_pos[i])
                              for i in range(queries_a.shape[0])], dim=0)
        preds = _normalize_torch(preds)
        sims = preds @ book_c.T
        top1 = sims.argmax(dim=-1)
        top1_cos = sims.max(dim=-1).values
        correct = float((top1 == true_c_idx).float().mean().item())
        return correct, float(top1_cos.mean().item())

    bind3_recall, bind3_cos = _eval_3mod_arm(bundle_substrate, q_items_a,
                                               q_items_b, q_positions,
                                               q_true_c)
    nobind_recall, nobind_cos = _eval_3mod_arm(bundle_no_bind, q_items_a,
                                                  q_items_b, q_positions,
                                                  q_true_c)

    # ARM_TWO_MOD_BIND_CONTROL: same mechanism but 2-mod bind V<->C only
    # (skips auditory); this is the 2-mod baseline reference.
    if mechanism == "HRR_bind3":
        # Build 2-mod HRR bundle: sum_i bind(a_i, c_i)
        bound_2 = _bind_pair_torch(items_a, items_c)
        bundle_2mod = _normalize_torch(bound_2.sum(dim=0))

        def _q_2mod(bundle, qa, qpos):
            return _normalize_torch(_unbind_torch(bundle, qa))
    elif mechanism == "sum_then_query":
        bundle_2mod = _normalize_torch((items_a + items_c).sum(dim=0))

        def _q_2mod(bundle, qa, qpos):
            return _normalize_torch(bundle - _normalize_torch(qa))
    else:  # position_key_bind3 -> 2-mod position_key
        pa = _bind_pair_torch(positions, items_a)
        pc = _bind_pair_torch(positions, items_c)
        bundle_2mod = _normalize_torch((pa + pc).sum(dim=0))

        def _q_2mod(bundle, qa, qpos):
            unbound = _unbind_torch(bundle, qpos)
            rem = unbound - _normalize_torch(qa)
            return _normalize_torch(rem)

    def _eval_2mod_arm(bundle, queries_a, queries_pos, true_c_idx):
        preds = torch.stack([_q_2mod(bundle, queries_a[i], queries_pos[i])
                              for i in range(queries_a.shape[0])], dim=0)
        preds = _normalize_torch(preds)
        sims = preds @ book_c.T
        top1 = sims.argmax(dim=-1)
        top1_cos = sims.max(dim=-1).values
        correct = float((top1 == true_c_idx).float().mean().item())
        return correct, float(top1_cos.mean().item())

    twomod_recall, twomod_cos = _eval_2mod_arm(bundle_2mod, q_items_a,
                                                  q_positions, q_true_c)

    return {
        "K": int(K),
        "N": int(N),
        "mechanism": mechanism,
        "n_queries": int(n_queries),
        "BIND_3MOD_top1_recall": bind3_recall,
        "BIND_3MOD_mean_cosine": bind3_cos,
        "NO_BIND_BASELINE_top1_recall": nobind_recall,
        "NO_BIND_BASELINE_mean_cosine": nobind_cos,
        "TWO_MOD_BIND_CONTROL_top1_recall": twomod_recall,
        "TWO_MOD_BIND_CONTROL_mean_cosine": twomod_cos,
        "bind_no_bind_lift": bind3_recall - nobind_recall,
        "three_vs_two_ratio": (bind3_recall / twomod_recall
                                if twomod_recall > 1e-6 else 0.0),
    }


def run_one_seed_phase_diagram(
    seed: int,
    run_mode: str,
    smoke_corners: bool = False,
) -> Dict[str, Any]:
    """Run full or smoke phase diagram for one seed."""
    device = "cuda" if _CUDA_OK else "cpu"
    g_torch = torch.Generator(device=device).manual_seed(int(seed))
    g_np = np.random.default_rng(seed)

    n_queries = N_QUERIES_SMOKE if (run_mode != "full") else N_QUERIES_FULL

    if smoke_corners:
        points = list(SMOKE_CORNERS)
    elif run_mode == "selftest":
        points = [SMOKE_CORNERS[0], SMOKE_CORNERS[1]]
        n_queries = 2
    else:
        points = []
        for K in K_VALUES:
            for N in N_VALUES:
                for mech in BIND_MECHANISMS:
                    points.append((K, N, mech))

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for (K, N, mech) in points:
        res = _run_phase_point(g_torch, g_np, K, N, mech, n_queries, device)
        phase_map.append(res)

    elapsed = time.time() - started

    return {
        "seed": int(seed),
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
    """Compute discrimination + 3vs2 ratio + cv + verdict."""
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    bucket: Dict[Tuple[int, int, str], Dict[str, List[float]]] = {}
    for s, body in per_seed.items():
        for pt in body.get("phase_map", []):
            key = (int(pt["K"]), int(pt["N"]), str(pt["mechanism"]))
            d = bucket.setdefault(key, {
                "BIND_3MOD_top1_recall": [],
                "NO_BIND_BASELINE_top1_recall": [],
                "TWO_MOD_BIND_CONTROL_top1_recall": [],
            })
            d["BIND_3MOD_top1_recall"].append(pt["BIND_3MOD_top1_recall"])
            d["NO_BIND_BASELINE_top1_recall"].append(
                pt["NO_BIND_BASELINE_top1_recall"])
            d["TWO_MOD_BIND_CONTROL_top1_recall"].append(
                pt["TWO_MOD_BIND_CONTROL_top1_recall"])

    summary_per_pt: List[Dict[str, Any]] = []
    discriminating_points = 0
    three_vs_two_ok_points = 0
    all_bind_recalls: List[float] = []

    for key, d in sorted(bucket.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        K, N, mech = key
        bind3_recalls = d["BIND_3MOD_top1_recall"]
        bind3_mean = float(np.mean(bind3_recalls))
        bind3_std = float(np.std(bind3_recalls, ddof=0))
        bind3_cv = (bind3_std / bind3_mean) if bind3_mean > 1e-6 else float("inf")
        nobind_mean = float(np.mean(d["NO_BIND_BASELINE_top1_recall"]))
        twomod_mean = float(np.mean(d["TWO_MOD_BIND_CONTROL_top1_recall"]))
        lift = bind3_mean - nobind_mean
        ratio_3v2 = (bind3_mean / twomod_mean) if twomod_mean > 1e-6 else 0.0
        all_bind_recalls.append(bind3_mean)
        if lift >= HP_BIND_LIFT_MIN:
            discriminating_points += 1
        if ratio_3v2 >= HP_3VS2_RATIO_MIN:
            three_vs_two_ok_points += 1
        summary_per_pt.append({
            "K": K, "N": N, "mechanism": mech,
            "BIND_3MOD_mean": bind3_mean,
            "BIND_3MOD_std": bind3_std,
            "BIND_3MOD_cv": bind3_cv,
            "NO_BIND_BASELINE_mean": nobind_mean,
            "TWO_MOD_BIND_CONTROL_mean": twomod_mean,
            "bind_no_bind_lift": lift,
            "three_vs_two_ratio": ratio_3v2,
            "n_seeds": len(bind3_recalls),
        })

    # Positive control: K=10, N=8192, HRR_bind3 -> recall > 0.70 with cv < 0.10
    pos_control_pts = [p for p in summary_per_pt
                        if p["K"] == 10 and p["N"] == 8192
                        and p["mechanism"] == "HRR_bind3"]
    pos_control_recall = (pos_control_pts[0]["BIND_3MOD_mean"]
                          if pos_control_pts else None)
    pos_control_cv = (pos_control_pts[0]["BIND_3MOD_cv"]
                       if pos_control_pts else None)
    pos_control_met = (pos_control_recall is not None
                       and pos_control_recall >= HP_POS_CONTROL_MIN_RECALL
                       and pos_control_cv is not None
                       and pos_control_cv <= HP_POS_CONTROL_MAX_CV)

    all_saturated = bool(all(r >= HF_ALL_SATURATED_THRESHOLD
                              for r in all_bind_recalls)) \
                    if all_bind_recalls else False
    near_identical = bool(np.mean([abs(p["bind_no_bind_lift"])
                                    for p in summary_per_pt])
                          < HF_ARMS_IDENTICAL_TOL) if summary_per_pt else False

    if all_saturated:
        verdict = "HARD_FAIL"
        verdict_reason = "all_bind_recalls>=0.99 (by-construction saturation)"
    elif near_identical:
        verdict = "HARD_FAIL"
        verdict_reason = "avg|BIND - NO_BIND| < 0.05 (3-mod mechanism not load-bearing)"
    elif (discriminating_points >= HP_MIN_DISCRIMINATING_POINTS
          and three_vs_two_ok_points >= HP_3VS2_MIN_POINTS
          and pos_control_met):
        verdict = "HARD_PASS"
        verdict_reason = (f"disc={discriminating_points}>={HP_MIN_DISCRIMINATING_POINTS}; "
                          f"3v2_ok={three_vs_two_ok_points}>={HP_3VS2_MIN_POINTS}; "
                          f"pos_ctrl_recall={pos_control_recall:.3f}"
                          f"(>{HP_POS_CONTROL_MIN_RECALL}) "
                          f"cv={pos_control_cv:.3f}(<{HP_POS_CONTROL_MAX_CV})")
    elif discriminating_points >= MB_MIN_DISCRIMINATING_POINTS:
        verdict = "MIDDLE_BAND"
        verdict_reason = (f"disc={discriminating_points} in "
                          f"[{MB_MIN_DISCRIMINATING_POINTS},{HP_MIN_DISCRIMINATING_POINTS})"
                          f" or pos_ctrl/3v2 short")
    else:
        verdict = "MIDDLE_BAND"
        verdict_reason = f"disc={discriminating_points} < {MB_MIN_DISCRIMINATING_POINTS}"

    headline = (f"disc_pts={discriminating_points}/{len(summary_per_pt)} "
                f"(>={HP_BIND_LIFT_MIN} lift) | "
                f"3v2_ok={three_vs_two_ok_points}/{len(summary_per_pt)} "
                f"(>={HP_3VS2_RATIO_MIN} ratio) | "
                f"pos_ctrl_recall={pos_control_recall} "
                f"cv={pos_control_cv} | "
                f"saturated={all_saturated} | near_id={near_identical}")
    verdict_msg = f"{verdict} | {headline} | {verdict_reason}"

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "n_discriminating_points": discriminating_points,
        "n_three_vs_two_ok_points": three_vs_two_ok_points,
        "n_phase_points_total": len(summary_per_pt),
        "positive_control_recall": pos_control_recall,
        "positive_control_cv": pos_control_cv,
        "positive_control_met": bool(pos_control_met),
        "all_saturated": all_saturated,
        "near_identical_arms": near_identical,
        "summary_per_phase_point": summary_per_pt,
        "n_seeds_complete": len(per_seed),
    }


# ----- Self-test -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: 2 corner points; verifies 3-mod BIND > NO_BIND at sat corner.

    ASSERTS EXPECTED VALUES (per exp_dev self-test discipline):
      - phase_map has exactly 2 pts
      - Sat corner (K=10, N=8192, HRR_bind3): BIND_3MOD > NO_BIND + 0.20
      - Sat corner: BIND_3MOD >= 0.30 (must clear noise floor even with 2 queries)
      - codebook independence: mean|<a,c>| < 0.10
    """
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pts = body["phase_map"]
        if len(pts) != 2:
            return False, f"selftest: expected 2 pts, got {len(pts)}"

        sat_pts = [p for p in pts if p["K"] == 10 and p["N"] == 8192
                    and p["mechanism"] == "HRR_bind3"]
        if not sat_pts:
            return False, "selftest: missing sat corner (K=10, N=8192, HRR_bind3)"
        sat = sat_pts[0]
        if sat["BIND_3MOD_top1_recall"] <= sat["NO_BIND_BASELINE_top1_recall"] + 0.20:
            return False, (f"selftest: BIND_3MOD={sat['BIND_3MOD_top1_recall']:.3f} "
                            f"should exceed NO_BIND={sat['NO_BIND_BASELINE_top1_recall']:.3f}"
                            f" by >=0.20 at sat corner")
        if sat["BIND_3MOD_top1_recall"] < 0.30:
            return False, (f"selftest: BIND_3MOD at sat corner = "
                            f"{sat['BIND_3MOD_top1_recall']:.3f} "
                            f"(expected >=0.30 even with 2 queries)")

        device = "cuda" if _CUDA_OK else "cpu"
        g_torch = torch.Generator(device=device).manual_seed(int(seed))
        book_a = _bipolar_codebook_torch(64, 1024, g_torch, device)
        book_c = _bipolar_codebook_torch(64, 1024, g_torch, device)
        cross = book_a @ book_c.T
        mean_abs = float(cross.abs().mean().item())
        if mean_abs > 0.10:
            return False, (f"selftest: codebooks not i.i.d.; "
                            f"mean|<a,c>|={mean_abs:.3f}")

        msg = (f"selftest OK: BIND_3MOD(K=10,N=8192,HRR)={sat['BIND_3MOD_top1_recall']:.3f}, "
               f"NO_BIND={sat['NO_BIND_BASELINE_top1_recall']:.3f}, "
               f"TWO_MOD={sat['TWO_MOD_BIND_CONTROL_top1_recall']:.3f}, "
               f"3v2_ratio={sat['three_vs_two_ratio']:.3f}, "
               f"codebook_indep={mean_abs:.3f}, "
               f"backend={body['backend']}, elapsed={body['elapsed_s']:.1f}s")
        return True, msg
    except Exception as e:
        return False, (f"selftest EXC: {type(e).__name__}: {e}\n"
                        f"{traceback.format_exc()}")


if __name__ == "__main__":
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
