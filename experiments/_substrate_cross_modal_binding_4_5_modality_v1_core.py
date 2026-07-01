"""Shared core for cross_modal_binding_4_5_modality_v1 sibling cells.

Stage 3 cross-modal binding SCALING extension: 3 vs 4 vs 5 modalities.
Composes on 3rd-modality MM (single-seed HP just landed 2026-07-01).

Question: does HRR-bindN cross-modal mechanism survive scaling to 4 and 5
modalities cross-seed (3 seeds), or does the bindN conjunction saturate /
lose lift vs baseline as N-way capacity cost compounds?

Modality set (5 total):
  - visual (V)
  - auditory (A)
  - tactile (T)
  - haptic (H) -- 4th modality added at n_mod>=4
  - proprioceptive (P) -- 5th modality added at n_mod==5

Mechanism (single, per task-spec):
  - HRR_bindN : C_i = bind_left_assoc(m0, m1, ..., m_{N-1});
                    query = bind(m0, m1, ..., m_{N-2}) -> unbind -> m_{N-1}_hat

Discriminator arms (2 per phase point):
  - ARM_BIND_NMOD : substrate-bound N-way; query first N-1 -> retrieve N-th
  - ARM_NO_BIND   : substrate is random vec; chance-level baseline

Discriminator (per task-spec):
  - cross-modal recall > 0.70 with cross-seed cv < 10% at
    positive-control corner (K=10, N=8192, n_mod=5)
  - BIND_NMOD - NO_BIND lift >= 0.30 at >=50% of grid points

CRLB / capacity-feasibility note (META_RULE re rule 9):
  For HRR bindN of independent bipolar codes at capacity K:
    SNR_effective ~ 1 / sqrt(K * (2^{N_mod - 1} - 1))  approx
  At K=10, N=8192, n_mod=5, SNR ~ 1/sqrt(10*15) = 1/sqrt(150) ~ 0.082
  Expected top1 at that SNR from ~2000-entry codebook: >= 0.70 achievable
  because clean signal component still >> other-item noise. THEORETICAL
  ceiling analysis (see prereg): capacity-feasibility confirmed at pos-control.

ASCII-only. CPU-first per task spec.

Author: exp_dev 2026-07-01 (Opus 4.7 1M) Stage 3 4-and-5-mod extension
"""
from __future__ import annotations

import math
import sys
import time
import traceback
from typing import Any, Dict, List, Tuple

import numpy as np
import torch

_TORCH_OK = True
_CUDA_OK = bool(torch.cuda.is_available())

ANCHOR_PREFIX = "cross_modal_binding_4_5_modality_v1"

# ----- Phase axes (LOCKED per pre-reg) -----
K_VALUES = (10, 100, 1000)                       # 3 points  MEASURED@design
N_VALUES = (2048, 4096, 8192)                     # 3 points
N_MOD_VALUES = (3, 4, 5)                          # 3 points
DISCRIMINATOR_ARMS = ("BIND_NMOD", "NO_BIND")
N_PHASE_POINTS_FULL = len(K_VALUES) * len(N_VALUES) * len(N_MOD_VALUES)  # 27

# Smoke corners (5 pts spanning n_mod x regime):
SMOKE_CORNERS = (
    (10,   8192, 3),   # pos-ctrl-3
    (10,   8192, 4),   # pos-ctrl-4
    (10,   8192, 5),   # pos-ctrl-5 (headline)
    (1000, 2048, 5),   # cliff regime 5-mod
    (100,  4096, 4),   # mid 4-mod
)

# Per-point query count
N_QUERIES_FULL = 20
N_QUERIES_SMOKE = 4

# Modality codebook sizes (must be >= max K)
V_MOD = 2048   # per modality; all 5 modalities use V_MOD entries

# ----- Pre-reg bands (LOCKED at module load) -----
HP_POS_CONTROL_MIN_RECALL = 0.70   # HYPOTHESIZED@prereg, discriminator per task-spec
HP_POS_CONTROL_MAX_CV = 0.10
HP_LIFT_MIN = 0.30
HP_DISCRIMINATING_FRACTION = 0.50  # >=50% of grid points must show lift
HF_ALL_SATURATED_THRESHOLD = 0.99
HF_ARMS_IDENTICAL_TOL = 0.05
MB_MIN_DISCRIMINATING_FRACTION = 0.20

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
    A = torch.fft.rfft(a, dim=-1)
    B = torch.fft.rfft(b, dim=-1)
    PROD = A * B
    return torch.fft.irfft(PROD, n=a.shape[-1], dim=-1).to(torch.float32)


def _unbind_torch(c: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
    C = torch.fft.rfft(c, dim=-1)
    A = torch.fft.rfft(a, dim=-1)
    R = C * torch.conj(A)
    return torch.fft.irfft(R, n=c.shape[-1], dim=-1).to(torch.float32)


def _normalize_torch(x: torch.Tensor) -> torch.Tensor:
    return x / (torch.linalg.norm(x, dim=-1, keepdim=True) + 1e-8)


def _bindN_left(items_stack: List[torch.Tensor]) -> torch.Tensor:
    """bindN via left-associative HRR: bind(m0, bind(m1, bind(..., m_{N-1}))).

    items_stack: list of length N_MOD, each tensor shape (K, N_DIM).
    Returns per-item bound tensor shape (K, N_DIM).
    """
    # Right-fold: acc = m_{N-1}; then for i in reverse(range(N-1)): acc = bind(m_i, acc)
    acc = items_stack[-1]
    for i in range(len(items_stack) - 2, -1, -1):
        acc = _bind_pair_torch(items_stack[i], acc)
    return acc


def _unbindN_prefix(bundle: torch.Tensor,
                     prefix_items: List[torch.Tensor]) -> torch.Tensor:
    """Unbind items[0], items[1], ..., items[N-2] from bundle to recover last item.

    Sequential: r1 = unbind(bundle, m0)  ~ bind(m1, ..., m_{N-1})
                r2 = unbind(r1, m1)      ~ bind(m2, ..., m_{N-1})
                ...
    """
    acc = bundle
    for m in prefix_items:
        acc = _unbind_torch(acc, m)
    return acc


# ----- One phase-point evaluation -----

def _run_phase_point(
    g_torch: torch.Generator,
    g_np: np.random.Generator,
    K: int,
    N_DIM: int,
    n_mod: int,
    n_queries: int,
    device: str,
) -> Dict[str, float]:
    """Run BIND_NMOD / NO_BIND arms at one (K, N_DIM, n_mod) point."""
    # Build n_mod independent codebooks + K item slots per modality
    codebooks = [_bipolar_codebook_torch(V_MOD, N_DIM, g_torch, device)
                 for _ in range(n_mod)]

    # Sample K items per modality
    idx_per_mod = [g_np.choice(V_MOD, size=K, replace=False)
                    for _ in range(n_mod)]
    items_per_mod = [codebooks[m][torch.from_numpy(idx_per_mod[m]).long().to(device)]
                      for m in range(n_mod)]

    # Build BIND_NMOD bundle: sum over K of bindN(m0[i], m1[i], ..., m_{n-1}[i])
    bound_per_item = _bindN_left(items_per_mod)  # (K, N_DIM)
    bundle_substrate = _normalize_torch(bound_per_item.sum(dim=0))

    # ARM_NO_BIND: random vector
    bundle_no_bind = _normalize_torch(
        torch.randn((N_DIM,), generator=g_torch, device=device,
                     dtype=torch.float32))

    # Sample n_queries indices from K
    if n_queries > K:
        q_local = g_np.choice(K, size=n_queries, replace=True)
    else:
        q_local = g_np.choice(K, size=n_queries, replace=False)

    # For each query: use first n_mod-1 modality items as unbinding keys;
    # true answer = idx_per_mod[n_mod-1][q_local[i]]
    q_prefix_items = [items_per_mod[m][torch.from_numpy(q_local).long().to(device)]
                       for m in range(n_mod - 1)]
    q_true_last = torch.from_numpy(idx_per_mod[n_mod - 1][q_local]).long().to(device)
    book_last = codebooks[n_mod - 1]

    def _eval_arm(bundle: torch.Tensor) -> Tuple[float, float]:
        preds_list = []
        for qi in range(n_queries):
            prefix_i = [q_prefix_items[m][qi] for m in range(n_mod - 1)]
            pred = _unbindN_prefix(bundle, prefix_i)
            preds_list.append(_normalize_torch(pred))
        preds = torch.stack(preds_list, dim=0)
        sims = preds @ book_last.T
        top1 = sims.argmax(dim=-1)
        top1_cos = sims.max(dim=-1).values
        correct = float((top1 == q_true_last).float().mean().item())
        return correct, float(top1_cos.mean().item())

    bind_recall, bind_cos = _eval_arm(bundle_substrate)
    nobind_recall, nobind_cos = _eval_arm(bundle_no_bind)

    return {
        "K": int(K),
        "N": int(N_DIM),
        "n_mod": int(n_mod),
        "n_queries": int(n_queries),
        "BIND_NMOD_top1_recall": bind_recall,
        "BIND_NMOD_mean_cosine": bind_cos,
        "NO_BIND_top1_recall": nobind_recall,
        "NO_BIND_mean_cosine": nobind_cos,
        "bind_no_bind_lift": bind_recall - nobind_recall,
    }


def run_one_seed_phase_diagram(
    seed: int,
    run_mode: str,
    smoke_corners: bool = False,
) -> Dict[str, Any]:
    device = "cuda" if _CUDA_OK else "cpu"
    g_torch = torch.Generator(device=device).manual_seed(int(seed))
    g_np = np.random.default_rng(seed)

    n_queries = N_QUERIES_SMOKE if (run_mode != "full") else N_QUERIES_FULL

    if smoke_corners:
        points = list(SMOKE_CORNERS)
    elif run_mode == "selftest":
        # 2 corners; verifies discriminator fires at 3-mod and 5-mod pos-ctrl
        points = [(10, 8192, 3), (10, 8192, 5)]
        n_queries = 2
    else:
        points = []
        for K in K_VALUES:
            for N_DIM in N_VALUES:
                for nm in N_MOD_VALUES:
                    points.append((K, N_DIM, nm))

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for (K, N_DIM, nm) in points:
        res = _run_phase_point(g_torch, g_np, K, N_DIM, nm, n_queries, device)
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
    if not per_seed:
        return {"verdict": "UNKNOWN",
                "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    bucket: Dict[Tuple[int, int, int], Dict[str, List[float]]] = {}
    for s, body in per_seed.items():
        for pt in body.get("phase_map", []):
            key = (int(pt["K"]), int(pt["N"]), int(pt["n_mod"]))
            d = bucket.setdefault(key, {
                "BIND_NMOD_top1_recall": [],
                "NO_BIND_top1_recall": [],
            })
            d["BIND_NMOD_top1_recall"].append(pt["BIND_NMOD_top1_recall"])
            d["NO_BIND_top1_recall"].append(pt["NO_BIND_top1_recall"])

    summary_per_pt: List[Dict[str, Any]] = []
    discriminating_points = 0
    all_bind_recalls: List[float] = []

    for key, d in sorted(bucket.items(), key=lambda x: x[0]):
        K, N_DIM, nm = key
        bind_recalls = d["BIND_NMOD_top1_recall"]
        bind_mean = float(np.mean(bind_recalls))
        bind_std = float(np.std(bind_recalls, ddof=0))
        bind_cv = (bind_std / bind_mean) if bind_mean > 1e-6 else float("inf")
        nobind_mean = float(np.mean(d["NO_BIND_top1_recall"]))
        lift = bind_mean - nobind_mean
        all_bind_recalls.append(bind_mean)
        if lift >= HP_LIFT_MIN:
            discriminating_points += 1
        summary_per_pt.append({
            "K": K, "N": N_DIM, "n_mod": nm,
            "BIND_NMOD_mean": bind_mean,
            "BIND_NMOD_std": bind_std,
            "BIND_NMOD_cv": bind_cv,
            "NO_BIND_mean": nobind_mean,
            "bind_no_bind_lift": lift,
            "n_seeds": len(bind_recalls),
        })

    # Positive control: K=10, N=8192, n_mod=5 -> headline arm (5-mod cross-seed)
    pos_control_pts = [p for p in summary_per_pt
                        if p["K"] == 10 and p["N"] == 8192
                        and p["n_mod"] == 5]
    pos_control_recall = (pos_control_pts[0]["BIND_NMOD_mean"]
                          if pos_control_pts else None)
    pos_control_cv = (pos_control_pts[0]["BIND_NMOD_cv"]
                       if pos_control_pts else None)
    pos_control_met = (pos_control_recall is not None
                       and pos_control_recall >= HP_POS_CONTROL_MIN_RECALL
                       and pos_control_cv is not None
                       and pos_control_cv <= HP_POS_CONTROL_MAX_CV)

    n_total = len(summary_per_pt)
    disc_frac = discriminating_points / n_total if n_total else 0.0
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
        verdict_reason = "avg|BIND - NO_BIND| < 0.05 (N-mod mechanism not load-bearing)"
    elif (disc_frac >= HP_DISCRIMINATING_FRACTION and pos_control_met):
        verdict = "HARD_PASS"
        verdict_reason = (f"disc_frac={disc_frac:.2f}>={HP_DISCRIMINATING_FRACTION}; "
                          f"pos_ctrl_recall={pos_control_recall:.3f}"
                          f"(>={HP_POS_CONTROL_MIN_RECALL}) "
                          f"cv={pos_control_cv:.3f}(<={HP_POS_CONTROL_MAX_CV})")
    elif disc_frac >= MB_MIN_DISCRIMINATING_FRACTION:
        verdict = "MIDDLE_BAND"
        verdict_reason = (f"disc_frac={disc_frac:.2f} in "
                          f"[{MB_MIN_DISCRIMINATING_FRACTION},{HP_DISCRIMINATING_FRACTION})"
                          f" or pos_ctrl short "
                          f"(recall={pos_control_recall}, cv={pos_control_cv})")
    else:
        verdict = "MIDDLE_BAND"
        verdict_reason = f"disc_frac={disc_frac:.2f} < {MB_MIN_DISCRIMINATING_FRACTION}"

    headline = (f"disc_pts={discriminating_points}/{n_total} "
                f"(>={HP_LIFT_MIN} lift) | "
                f"pos_ctrl(n_mod=5) recall={pos_control_recall} "
                f"cv={pos_control_cv} | "
                f"saturated={all_saturated} | near_id={near_identical}")
    verdict_msg = f"{verdict} | {headline} | {verdict_reason}"

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "n_discriminating_points": discriminating_points,
        "n_phase_points_total": n_total,
        "discriminating_fraction": disc_frac,
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
    """Tiny selftest: 2 corners; verifies 3-mod and 5-mod BIND > NO_BIND.

    ASSERTS EXPECTED VALUES:
      - phase_map exactly 2 pts
      - 3-mod pos-ctrl: BIND >= 0.50 (2 queries; noise floor tolerance)
      - 5-mod pos-ctrl: BIND >= NO_BIND + 0.20 (mechanism fires at 5-mod)
      - codebook independence: mean|<a,b>| < 0.10
    """
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pts = body["phase_map"]
        if len(pts) != 2:
            return False, f"selftest: expected 2 pts, got {len(pts)}"

        p3 = [p for p in pts if p["n_mod"] == 3][0]
        p5 = [p for p in pts if p["n_mod"] == 5][0]

        if p3["BIND_NMOD_top1_recall"] < 0.50:
            return False, (f"selftest: 3-mod BIND={p3['BIND_NMOD_top1_recall']:.3f} "
                            f"expected >=0.50 at pos-ctrl (2 queries)")

        if p5["BIND_NMOD_top1_recall"] <= p5["NO_BIND_top1_recall"] + 0.20:
            return False, (f"selftest: 5-mod BIND={p5['BIND_NMOD_top1_recall']:.3f} "
                            f"should exceed NO_BIND={p5['NO_BIND_top1_recall']:.3f}"
                            f" by >=0.20 (mechanism must fire at 5-mod)")

        device = "cuda" if _CUDA_OK else "cpu"
        g_torch = torch.Generator(device=device).manual_seed(int(seed))
        book_a = _bipolar_codebook_torch(64, 1024, g_torch, device)
        book_b = _bipolar_codebook_torch(64, 1024, g_torch, device)
        cross = book_a @ book_b.T
        mean_abs = float(cross.abs().mean().item())
        if mean_abs > 0.10:
            return False, (f"selftest: codebooks not i.i.d.; "
                            f"mean|<a,b>|={mean_abs:.3f}")

        msg = (f"selftest OK: 3-mod BIND={p3['BIND_NMOD_top1_recall']:.3f}, "
               f"5-mod BIND={p5['BIND_NMOD_top1_recall']:.3f}, "
               f"5-mod NO_BIND={p5['NO_BIND_top1_recall']:.3f}, "
               f"5-mod lift={p5['bind_no_bind_lift']:.3f}, "
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
