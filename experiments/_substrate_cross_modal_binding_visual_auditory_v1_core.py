"""Shared core for substrate_cross_modal_binding_visual_auditory_v1 sibling cells.

Stage 3 cross-modal binding (TPJ-analog) characterization. Tests whether the
substrate supports binding an entity across two independent modality codebooks
(visual V[i], auditory A[i]) and recovering the cross-modal partner given a
query in the other modality.

Mechanisms (3-arm bind sweep):
  - HRR_bind          : C_i = bind(V[i], A[i]); query V[i] => unbind(C_sum, V[i]) -> A_hat
  - sum_then_query    : C_i = V[i] + A[i] (no binding); query V[i] => C_sum  - V[i]
  - position_key_bind : C_i = bind(P_i, V[i]) + bind(P_i, A[i]); query (V[i], i) hops via P_i

Discriminator arms (3 per phase point):
  - ARM_BIND_CROSS_MODAL          : substrate-bound; query mod-A item -> retrieve mod-B partner
  - ARM_NO_BIND_BASELINE          : substrate has NO bind (random vec instead); chance retrieval
  - ARM_WITHIN_MODAL_BIND_CONTROL : same mechanism but query A[i] => retrieve A[j] (within-mod)
                                    Compares cross-modal vs within-modal at same K (HRR sense)

ASCII-only. CPU-first per task spec.

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn) Stage 3 TPJ-analog characterization
"""
from __future__ import annotations

# torch top-of-file per Fix #24 (gate validates GPU eligibility)
import torch

import math
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_TORCH_OK = True
_CUDA_OK = bool(torch.cuda.is_available())

ANCHOR_PREFIX = "substrate_cross_modal_binding_visual_auditory_v1"

# ----- Phase axes (LOCKED per pre-reg) -----
K_VALUES = (10, 50, 100, 500, 1000)                                # 5 points
N_VALUES = (2048, 4096, 8192)                                       # 3 points
BIND_MECHANISMS = ("HRR_bind", "sum_then_query", "position_key_bind")  # 3 points
DISCRIMINATOR_ARMS = ("BIND_CROSS_MODAL", "NO_BIND_BASELINE",
                       "WITHIN_MODAL_BIND_CONTROL")
N_PHASE_POINTS_FULL = len(K_VALUES) * len(N_VALUES) * len(BIND_MECHANISMS)  # 45

# Smoke corners (6 points -- low-K saturate / high-K cliff / mid):
# Each as (K, N, mech). Discriminator arms are run within each phase-point.
SMOKE_CORNERS = (
    (10,   8192, "HRR_bind"),           # sat regime: bind should work cleanly
    (1000, 2048, "HRR_bind"),           # cliff regime: bind should saturate floor
    (10,   2048, "sum_then_query"),     # low-K low-N sum baseline
    (1000, 8192, "sum_then_query"),     # high-K high-N sum baseline
    (100,  4096, "position_key_bind"),  # mid pos-key
    (500,  8192, "position_key_bind"),  # higher-K pos-key
)

# Per-point query count
N_QUERIES_FULL = 20
N_QUERIES_SMOKE = 4

# Modality codebook sizes; must be >= max K
V_MOD_A = 2048   # visual codebook size
V_MOD_B = 2048   # auditory codebook size
V_POS = 2048     # position codebook (for position_key_bind mechanism)

# ----- Pre-reg bands (LOCKED at module load) -----
# HARD_PASS: ARM_BIND_CROSS > ARM_NO_BIND by >= 0.40 lift at >=10 of 45 grid points
HP_BIND_LIFT_MIN = 0.40
HP_MIN_DISCRIMINATING_POINTS = 10
# HARD_PASS: ARM_BIND_CROSS_MODAL matches ARM_WITHIN_MODAL_BIND_CONTROL within 0.20
HP_CROSS_WITHIN_MATCH_TOL = 0.20
HP_CROSS_WITHIN_MATCH_MIN_POINTS = 10
# Positive control: at K=10, N=8192, HRR_bind: ARM_BIND_CROSS >= 0.95
HP_POS_CONTROL_MIN_RECALL = 0.95
# HARD_FAIL: BIND == NO_BIND (mechanism broken)
HF_ARMS_IDENTICAL_TOL = 0.05
# HARD_FAIL by-construction-saturation: ALL points >= 0.99 (no information)
HF_ALL_SATURATED_THRESHOLD = 0.99
# MIDDLE_BAND: 3-9 discriminating points OR cross-vs-within match in 3-9 only
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
    """HRR bind a (K,N) to b (K,N) via FFT circular convolution. Returns (K,N)."""
    A = torch.fft.rfft(a, dim=-1)
    B = torch.fft.rfft(b, dim=-1)
    PROD = A * B
    return torch.fft.irfft(PROD, n=a.shape[-1], dim=-1).to(torch.float32)


def _unbind_torch(c: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
    """Unbind a from c via FFT correlation. c, a same shape."""
    C = torch.fft.rfft(c, dim=-1)
    A = torch.fft.rfft(a, dim=-1)
    R = C * torch.conj(A)
    return torch.fft.irfft(R, n=c.shape[-1], dim=-1).to(torch.float32)


def _normalize_torch(x: torch.Tensor) -> torch.Tensor:
    return x / (torch.linalg.norm(x, dim=-1, keepdim=True) + 1e-8)


# ----- Mechanism implementations -----

def _build_bundle_hrr(items_a: torch.Tensor, items_b: torch.Tensor,
                       positions: torch.Tensor) -> torch.Tensor:
    """HRR_bind: C = sum_i bind(a_i, b_i). Sum-bundle, normalize."""
    bound = _bind_pair_torch(items_a, items_b)       # (K, N)
    bundle = bound.sum(dim=0)
    return _normalize_torch(bundle)


def _build_bundle_sum(items_a: torch.Tensor, items_b: torch.Tensor,
                      positions: torch.Tensor) -> torch.Tensor:
    """sum_then_query: C = sum_i (a_i + b_i). Naive superposition; no binding."""
    bundle = (items_a + items_b).sum(dim=0)
    return _normalize_torch(bundle)


def _build_bundle_position_key(items_a: torch.Tensor, items_b: torch.Tensor,
                                positions: torch.Tensor) -> torch.Tensor:
    """position_key_bind: C = sum_i [bind(p_i, a_i) + bind(p_i, b_i)]."""
    pa = _bind_pair_torch(positions, items_a)
    pb = _bind_pair_torch(positions, items_b)
    bundle = (pa + pb).sum(dim=0)
    return _normalize_torch(bundle)


def _query_hrr_cross(bundle: torch.Tensor, query_a: torch.Tensor,
                      positions_q: torch.Tensor) -> torch.Tensor:
    """Cross-modal query under HRR_bind: unbind query_a from bundle -> predicted b."""
    return _normalize_torch(_unbind_torch(bundle, query_a))


def _query_sum_cross(bundle: torch.Tensor, query_a: torch.Tensor,
                      positions_q: torch.Tensor) -> torch.Tensor:
    """Cross-modal query under sum_then_query: subtract query_a from bundle."""
    return _normalize_torch(bundle - _normalize_torch(query_a))


def _query_position_key_cross(bundle: torch.Tensor, query_a: torch.Tensor,
                                positions_q: torch.Tensor) -> torch.Tensor:
    """Cross-modal query under position_key_bind: hop via position p_i.

    bundle includes bind(p_i, a_i) and bind(p_i, b_i).
    Query: given a_i and position p_i, recover b_i.
    Strategy: unbind(p_i, bundle) -> noisy (a_i + b_i + cross-terms);
    subtract a_i; normalize.
    """
    unbound = _unbind_torch(bundle, positions_q)  # (Q, N) ~ a_q + b_q + noise
    rem = unbound - _normalize_torch(query_a)
    return _normalize_torch(rem)


# Mechanism dispatch tables
_BUNDLE_BUILDERS = {
    "HRR_bind": _build_bundle_hrr,
    "sum_then_query": _build_bundle_sum,
    "position_key_bind": _build_bundle_position_key,
}
_QUERY_FNS_CROSS = {
    "HRR_bind": _query_hrr_cross,
    "sum_then_query": _query_sum_cross,
    "position_key_bind": _query_position_key_cross,
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
    """Run BIND_CROSS / NO_BIND / WITHIN_MODAL arms at one phase point.

    Returns top1_recall for each arm + book metadata.
    """
    # Independent modality codebooks (statistically i.i.d. bipolar random)
    book_a = _bipolar_codebook_torch(V_MOD_A, N, g_torch, device)  # visual
    book_b = _bipolar_codebook_torch(V_MOD_B, N, g_torch, device)  # auditory
    book_pos = _bipolar_codebook_torch(V_POS, N, g_torch, device)  # positions

    # Sample K entity indices in each modality (paired bind: i-th visual <-> i-th auditory)
    idx_a = g_np.choice(V_MOD_A, size=K, replace=False)
    idx_b = g_np.choice(V_MOD_B, size=K, replace=False)
    idx_pos = g_np.choice(V_POS, size=K, replace=False)

    idx_a_t = torch.from_numpy(idx_a).long().to(device)
    idx_b_t = torch.from_numpy(idx_b).long().to(device)
    idx_pos_t = torch.from_numpy(idx_pos).long().to(device)

    items_a = book_a[idx_a_t]            # (K, N)
    items_b = book_b[idx_b_t]            # (K, N)
    positions = book_pos[idx_pos_t]      # (K, N)

    # Build substrate bundle (the cross-modal store)
    bundle_substrate = _BUNDLE_BUILDERS[mechanism](items_a, items_b, positions)

    # ARM_NO_BIND: substrate is just random (NOT containing the bind info)
    bundle_no_bind = torch.randn((N,), generator=g_torch, device=device,
                                   dtype=torch.float32)
    bundle_no_bind = _normalize_torch(bundle_no_bind)

    # Sample queries (subset of K presented)
    if n_queries > K:
        q_local = g_np.choice(K, size=n_queries, replace=True)
    else:
        q_local = g_np.choice(K, size=n_queries, replace=False)

    # Cross-modal queries: present a_i, expect b_i
    q_idx_a = idx_a[q_local]
    q_idx_b = idx_b[q_local]
    q_idx_pos = idx_pos[q_local]
    q_items_a = book_a[torch.from_numpy(q_idx_a).long().to(device)]   # (Q, N)
    q_positions = book_pos[torch.from_numpy(q_idx_pos).long().to(device)]
    q_true_b = torch.from_numpy(q_idx_b).long().to(device)

    def _eval_cross_arm(bundle, queries_a, queries_pos, true_b_idx):
        # Stack predictions across queries
        if mechanism == "HRR_bind":
            preds = torch.stack([_query_hrr_cross(bundle, queries_a[i],
                                                    queries_pos[i])
                                  for i in range(queries_a.shape[0])], dim=0)
        elif mechanism == "sum_then_query":
            preds = torch.stack([_query_sum_cross(bundle, queries_a[i],
                                                   queries_pos[i])
                                  for i in range(queries_a.shape[0])], dim=0)
        elif mechanism == "position_key_bind":
            preds = torch.stack([_query_position_key_cross(bundle, queries_a[i],
                                                            queries_pos[i])
                                  for i in range(queries_a.shape[0])], dim=0)
        else:
            raise ValueError(f"unknown mechanism: {mechanism}")
        preds = _normalize_torch(preds)
        sims = preds @ book_b.T    # cleanup vs modality-B codebook (Q, V_MOD_B)
        top1 = sims.argmax(dim=-1)
        top1_cos = sims.max(dim=-1).values
        correct = float((top1 == true_b_idx).float().mean().item())
        return correct, float(top1_cos.mean().item())

    bind_recall, bind_cos = _eval_cross_arm(bundle_substrate, q_items_a,
                                              q_positions, q_true_b)
    nobind_recall, nobind_cos = _eval_cross_arm(bundle_no_bind, q_items_a,
                                                  q_positions, q_true_b)

    # ARM_WITHIN_MODAL_BIND_CONTROL: same mechanism but binding A[i]<->A[shifted_i]
    # within modality A. Query A[i] -> retrieve A[shifted(i)].
    # This is the within-modality benchmark (HRR sense).
    if K >= 2:
        shift = g_np.integers(1, K)  # cyclic shift in [1, K-1]
        idx_a2 = idx_a[(np.arange(K) + int(shift)) % K]
    else:
        shift = 0
        idx_a2 = idx_a.copy()
    items_a2 = book_a[torch.from_numpy(idx_a2).long().to(device)]    # (K, N)
    # Build within-modal bundle using the chosen mechanism (a <-> a-shifted)
    bundle_within = _BUNDLE_BUILDERS[mechanism](items_a, items_a2, positions)
    # Queries: q_items_a -> expected = book_a[idx_a2[q_local]]
    q_idx_a2 = idx_a2[q_local]
    q_true_a2 = torch.from_numpy(q_idx_a2).long().to(device)

    def _eval_within_arm(bundle, queries_a, queries_pos, true_a2_idx):
        if mechanism == "HRR_bind":
            preds = torch.stack([_query_hrr_cross(bundle, queries_a[i],
                                                    queries_pos[i])
                                  for i in range(queries_a.shape[0])], dim=0)
        elif mechanism == "sum_then_query":
            preds = torch.stack([_query_sum_cross(bundle, queries_a[i],
                                                   queries_pos[i])
                                  for i in range(queries_a.shape[0])], dim=0)
        elif mechanism == "position_key_bind":
            preds = torch.stack([_query_position_key_cross(bundle, queries_a[i],
                                                            queries_pos[i])
                                  for i in range(queries_a.shape[0])], dim=0)
        else:
            raise ValueError(f"unknown mechanism: {mechanism}")
        preds = _normalize_torch(preds)
        sims = preds @ book_a.T   # cleanup vs modality-A codebook
        top1 = sims.argmax(dim=-1)
        top1_cos = sims.max(dim=-1).values
        correct = float((top1 == true_a2_idx).float().mean().item())
        return correct, float(top1_cos.mean().item())

    within_recall, within_cos = _eval_within_arm(bundle_within, q_items_a,
                                                    q_positions, q_true_a2)

    return {
        "K": int(K),
        "N": int(N),
        "mechanism": mechanism,
        "n_queries": int(n_queries),
        "BIND_CROSS_MODAL_top1_recall": bind_recall,
        "BIND_CROSS_MODAL_mean_cosine": bind_cos,
        "NO_BIND_BASELINE_top1_recall": nobind_recall,
        "NO_BIND_BASELINE_mean_cosine": nobind_cos,
        "WITHIN_MODAL_BIND_CONTROL_top1_recall": within_recall,
        "WITHIN_MODAL_BIND_CONTROL_mean_cosine": within_cos,
        "bind_no_bind_lift": bind_recall - nobind_recall,
        "cross_vs_within_diff": bind_recall - within_recall,
        "within_shift": int(shift),
    }


def run_one_seed_phase_diagram(
    seed: int,
    run_mode: str,
    smoke_corners: bool = False,
) -> Dict[str, Any]:
    """Run full or smoke phase diagram for one seed.

    Args:
        seed: integer seed.
        run_mode: "smoke" | "full" | "selftest".
        smoke_corners: if True, run 6 corner points instead of full sweep.
    """
    device = "cuda" if _CUDA_OK else "cpu"
    g_torch = torch.Generator(device=device).manual_seed(int(seed))
    g_np = np.random.default_rng(seed)

    n_queries = N_QUERIES_SMOKE if (run_mode != "full") else N_QUERIES_FULL

    if smoke_corners:
        points = list(SMOKE_CORNERS)
    elif run_mode == "selftest":
        # tiny: 2 corners (pos-control + cliff)
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
    """Compute discrimination + cross-vs-within match + verdict."""
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    bucket: Dict[Tuple[int, int, str], Dict[str, List[float]]] = {}
    for s, body in per_seed.items():
        for pt in body.get("phase_map", []):
            key = (int(pt["K"]), int(pt["N"]), str(pt["mechanism"]))
            d = bucket.setdefault(key, {
                "BIND_CROSS_MODAL_top1_recall": [],
                "NO_BIND_BASELINE_top1_recall": [],
                "WITHIN_MODAL_BIND_CONTROL_top1_recall": [],
            })
            d["BIND_CROSS_MODAL_top1_recall"].append(
                pt["BIND_CROSS_MODAL_top1_recall"])
            d["NO_BIND_BASELINE_top1_recall"].append(
                pt["NO_BIND_BASELINE_top1_recall"])
            d["WITHIN_MODAL_BIND_CONTROL_top1_recall"].append(
                pt["WITHIN_MODAL_BIND_CONTROL_top1_recall"])

    summary_per_pt: List[Dict[str, Any]] = []
    bind_minus_nobind: List[float] = []
    cross_vs_within_diff: List[float] = []
    discriminating_points = 0
    cross_within_match_points = 0
    all_bind_recalls: List[float] = []
    arms_identical_violations = 0

    for key, d in sorted(bucket.items(), key=lambda x: (x[0][0], x[0][1], x[0][2])):
        K, N, mech = key
        bind_mean = float(np.mean(d["BIND_CROSS_MODAL_top1_recall"]))
        nobind_mean = float(np.mean(d["NO_BIND_BASELINE_top1_recall"]))
        within_mean = float(np.mean(d["WITHIN_MODAL_BIND_CONTROL_top1_recall"]))
        lift = bind_mean - nobind_mean
        cw_diff = abs(bind_mean - within_mean)
        bind_minus_nobind.append(lift)
        cross_vs_within_diff.append(cw_diff)
        all_bind_recalls.append(bind_mean)
        if lift >= HP_BIND_LIFT_MIN:
            discriminating_points += 1
        if cw_diff <= HP_CROSS_WITHIN_MATCH_TOL:
            cross_within_match_points += 1
        if abs(bind_mean - nobind_mean) <= HF_ARMS_IDENTICAL_TOL and bind_mean > 0.1:
            # arms-identical only triggers when both > floor (so we know mechanism RAN)
            # actually we want arms identical to flag broken mechanism; this is a softer signal
            pass
        summary_per_pt.append({
            "K": K, "N": N, "mechanism": mech,
            "BIND_CROSS_MODAL_mean": bind_mean,
            "NO_BIND_BASELINE_mean": nobind_mean,
            "WITHIN_MODAL_BIND_CONTROL_mean": within_mean,
            "bind_no_bind_lift": lift,
            "cross_vs_within_abs_diff": cw_diff,
            "n_seeds": len(d["BIND_CROSS_MODAL_top1_recall"]),
        })

    # Positive control: K=10, N=8192, HRR_bind
    pos_control_pts = [p for p in summary_per_pt
                        if p["K"] == 10 and p["N"] == 8192
                        and p["mechanism"] == "HRR_bind"]
    pos_control_recall = (pos_control_pts[0]["BIND_CROSS_MODAL_mean"]
                          if pos_control_pts else None)
    pos_control_met = (pos_control_recall is not None
                       and pos_control_recall >= HP_POS_CONTROL_MIN_RECALL)

    avg_lift = float(np.mean(bind_minus_nobind)) if bind_minus_nobind else 0.0
    avg_cw_diff = float(np.mean(cross_vs_within_diff)) if cross_vs_within_diff else 0.0

    # HARD_FAIL: all bind recalls >= 0.99 (by-construction saturation)
    all_saturated = bool(all(r >= HF_ALL_SATURATED_THRESHOLD
                              for r in all_bind_recalls)) \
                    if all_bind_recalls else False
    # HARD_FAIL: BIND == NO_BIND at most points (mechanism not load-bearing)
    near_identical = bool(np.mean([abs(p["bind_no_bind_lift"])
                                    for p in summary_per_pt])
                          < HF_ARMS_IDENTICAL_TOL) if summary_per_pt else False

    # Verdict
    if all_saturated:
        verdict = "HARD_FAIL"
        verdict_reason = "all_bind_recalls>=0.99 (by-construction saturation)"
    elif near_identical:
        verdict = "HARD_FAIL"
        verdict_reason = "avg|BIND - NO_BIND| < 0.05 (mechanism not load-bearing)"
    elif not pos_control_met and pos_control_recall is not None:
        # Positive control failed -> mechanism broken at well-tested regime
        verdict = "HARD_FAIL"
        verdict_reason = (f"positive_control(K=10,N=8192,HRR)={pos_control_recall:.3f} "
                          f"< {HP_POS_CONTROL_MIN_RECALL}")
    elif (discriminating_points >= HP_MIN_DISCRIMINATING_POINTS
          and cross_within_match_points >= HP_CROSS_WITHIN_MATCH_MIN_POINTS
          and pos_control_met):
        verdict = "HARD_PASS"
        verdict_reason = (f"disc={discriminating_points}>={HP_MIN_DISCRIMINATING_POINTS}; "
                          f"cw_match={cross_within_match_points}"
                          f">={HP_CROSS_WITHIN_MATCH_MIN_POINTS}; "
                          f"pos_ctrl={pos_control_recall:.3f}")
    elif discriminating_points >= MB_MIN_DISCRIMINATING_POINTS:
        verdict = "MIDDLE_BAND"
        verdict_reason = (f"disc={discriminating_points} in "
                          f"[{MB_MIN_DISCRIMINATING_POINTS},{HP_MIN_DISCRIMINATING_POINTS})"
                          f" or cw_match short")
    else:
        verdict = "MIDDLE_BAND"
        verdict_reason = (f"disc={discriminating_points} < {MB_MIN_DISCRIMINATING_POINTS}")

    headline = (f"disc_pts={discriminating_points}/{len(summary_per_pt)} "
                f"(>={HP_BIND_LIFT_MIN} lift) | "
                f"cw_match_pts={cross_within_match_points}/{len(summary_per_pt)} "
                f"(<={HP_CROSS_WITHIN_MATCH_TOL} diff) | "
                f"pos_ctrl={pos_control_recall} | "
                f"avg_lift={avg_lift:.3f} | avg_cw_diff={avg_cw_diff:.3f} | "
                f"saturated={all_saturated} | near_id={near_identical}")
    verdict_msg = f"{verdict} | {headline} | {verdict_reason}"

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "n_discriminating_points": discriminating_points,
        "n_cross_within_match_points": cross_within_match_points,
        "n_phase_points_total": len(summary_per_pt),
        "positive_control_recall": pos_control_recall,
        "positive_control_met": bool(pos_control_met),
        "avg_bind_minus_nobind_lift": avg_lift,
        "avg_cross_vs_within_abs_diff": avg_cw_diff,
        "all_saturated": all_saturated,
        "near_identical_arms": near_identical,
        "summary_per_phase_point": summary_per_pt,
        "n_seeds_complete": len(per_seed),
    }


# ----- Self-test -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: 2 corner points (pos-control + cliff).

    Asserts:
      - phase_map non-empty (==2)
      - BIND_CROSS > NO_BIND at sat corner (K=10, N=8192, HRR_bind)
      - codebooks are statistically independent (modality A vs B mean inner product ~ 0)
    """
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pts = body["phase_map"]
        if len(pts) != 2:
            return False, f"selftest: expected 2 pts, got {len(pts)}"

        # Sat corner: K=10, N=8192, HRR_bind
        sat_pts = [p for p in pts if p["K"] == 10 and p["N"] == 8192
                    and p["mechanism"] == "HRR_bind"]
        if not sat_pts:
            return False, "selftest: missing saturate corner (K=10, N=8192, HRR_bind)"
        sat = sat_pts[0]
        if sat["BIND_CROSS_MODAL_top1_recall"] <= sat["NO_BIND_BASELINE_top1_recall"]:
            return False, (f"selftest: BIND_CROSS={sat['BIND_CROSS_MODAL_top1_recall']:.3f} "
                            f"should exceed NO_BIND={sat['NO_BIND_BASELINE_top1_recall']:.3f}"
                            f" at sat corner")
        if sat["BIND_CROSS_MODAL_top1_recall"] < 0.40:
            return False, (f"selftest: BIND_CROSS at sat corner = "
                            f"{sat['BIND_CROSS_MODAL_top1_recall']:.3f} "
                            f"(expected > 0.40 even with 2 queries)")

        # Independence of codebooks (sanity check)
        device = "cuda" if _CUDA_OK else "cpu"
        g_torch = torch.Generator(device=device).manual_seed(int(seed))
        book_a = _bipolar_codebook_torch(64, 1024, g_torch, device)
        book_b = _bipolar_codebook_torch(64, 1024, g_torch, device)
        cross = book_a @ book_b.T
        mean_abs = float(cross.abs().mean().item())
        if mean_abs > 0.10:
            return False, (f"selftest: modality codebooks not i.i.d.; "
                            f"mean|<a,b>|={mean_abs:.3f}")

        msg = (f"selftest OK: BIND_CROSS(K=10,N=8192,HRR)={sat['BIND_CROSS_MODAL_top1_recall']:.3f}, "
               f"NO_BIND={sat['NO_BIND_BASELINE_top1_recall']:.3f}, "
               f"WITHIN={sat['WITHIN_MODAL_BIND_CONTROL_top1_recall']:.3f}, "
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
