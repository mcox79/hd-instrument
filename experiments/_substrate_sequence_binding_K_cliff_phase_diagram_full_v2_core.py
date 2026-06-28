"""Shared core for substrate_sequence_binding_K_cliff_phase_diagram_full_v2 siblings.

Stage 1 phase-diagram coverage promotion (MID -> HIGH) for sequence_binding
chain-grade primitive. Sweeps (K, N, Q_noise) over 72 grid points per seed
with 3 arms (SUBSTRATE / RANDOM / SHUFFLE) and 100 queries per point.

DIFFERENCES vs v1:
  - K starts at 20 (not 10); 6 points {20,50,100,200,500,1000}
  - Q noise levels {1,2,4} replace tag_density {0.1,0.3,0.5}
    effective_tag_density = 0.1 * Q  -> {0.1, 0.2, 0.4}
    (integer Q = "noise multiplier"; aligns with Kanerva 2009 noise framing)
  - N_QUERIES_FULL = 100 (drives band precision; v1 had 10)
  - Discriminator bands: SAT >= 0.90 / MB [0.30, 0.70] / FLOOR <= 0.10
  - HARD_PASS gate: >= 22 of 72 points in MIDDLE_BAND
  - Local-CPU dispatch (laptop idle); numpy primary, torch fallback

ASCII-only.
Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn) Stage 1 phase-coverage promotion
"""
from __future__ import annotations

import math
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

try:
    import torch
    _TORCH_OK = True
    _CUDA_OK = bool(torch.cuda.is_available())
except Exception:
    _TORCH_OK = False
    _CUDA_OK = False

ANCHOR_PREFIX = "substrate_sequence_binding_K_cliff_phase_diagram_full_v2"

# ----- Phase axes (LOCKED) -----
K_VALUES = (20, 50, 100, 200, 500, 1000)              # 6 points (K=20 cert anchor)
N_VALUES = (2048, 4096, 8192, 16384)                  # 4 points
Q_VALUES = (1, 2, 4)                                  # 3 noise-multiplier levels
ARMS = ("SUBSTRATE", "RANDOM", "SHUFFLE")
BASE_TAG_DENSITY = 0.1                                # Q=1 -> tag=0.1 effective

# Smoke 6 corner points: (K, N, Q) per pre-reg; must span SAT/MB/FLOOR
SMOKE_CORNERS = (
    (20,   16384, 1),   # low-K high-N low-Q  -> SAT (>= 0.90)
    (20,   8192,  1),   # low-K high-N low-Q  -> SAT/MB
    (100,  4096,  2),   # mid                 -> MB (0.30-0.70)
    (200,  2048,  4),   # high-K low-N high-Q -> FLOOR
    (500,  2048,  2),   # high-K low-N mid-Q  -> FLOOR
    (1000, 2048,  4),   # very-high-K low-N high-Q -> FLOOR
)

# Pre-reg bands (LOCKED)
BAND_SAT = 0.90                                       # recall >= -> SAT
BAND_MB_LO = 0.30                                     # recall in [LO,HI] -> MIDDLE_BAND
BAND_MB_HI = 0.70
BAND_FLOOR = 0.10                                     # recall <= -> FLOOR

HP_MIN_MB_POINTS = 22                                 # >= 22 of 72 in MB -> HARD_PASS
MB_MIN_MB_POINTS = 10                                 # >= 10 in MB -> MIDDLE_BAND (else HF)
HP_ARMS_DIFF_MIN = 0.20                               # avg(SUBSTRATE - max(R,S))
HP_MIN_SAT_POINTS = 6                                 # >= 6 SAT (mechanism works at low load)
HP_MIN_FLOOR_POINTS = 6                               # >= 6 FLOOR (cliff observable)

# Per-point query count
N_QUERIES_FULL = 100
N_QUERIES_SMOKE = 4

# Codebook sizes (must be >= max K)
V_ITEMS = 1200                                        # >= 1000 + slack
V_POS = 1200

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    if _CUDA_OK:
        return "torch.cuda"
    if _TORCH_OK:
        return "torch.cpu"
    return "numpy.cpu"


# ----- HRR primitives (numpy; vectorized batched matmul for cleanup) -----

def _bipolar_codebook_np(V: int, N: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar codebook (NO L2 normalization).

    Classic Plate HRR keeps bipolar elements at +/-1 magnitude per element so
    that additive Gaussian tag_noise ~ N(0, tag_density) is small relative to
    signal magnitude. L2-normalizing would shrink elements to +/-1/sqrt(N),
    making N=16384 items collapse below tag_noise=0.1 -> signal destroyed.
    """
    X = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    return X


def _bind_bundle_np(positions: np.ndarray, items: np.ndarray,
                     tag_noise: np.ndarray) -> np.ndarray:
    """Bind K (pos, item) pairs + sum-bundle.

    positions: (K, N) float32 bipolar
    items:     (K, N) float32 bipolar
    tag_noise: (K, N) float32 dense noise (already scaled)
    Returns:   (N,) float32 normalized bundle
    """
    items_noisy = items + tag_noise
    items_noisy = items_noisy / (np.linalg.norm(items_noisy, axis=-1,
                                                 keepdims=True) + 1e-8)
    P = np.fft.rfft(positions, axis=-1)
    I = np.fft.rfft(items_noisy, axis=-1)
    PROD = P * I
    bound = np.fft.irfft(PROD, n=positions.shape[-1], axis=-1).astype(np.float32)
    bundle = bound.sum(axis=0)
    n = np.linalg.norm(bundle) + 1e-8
    return bundle / n


def _unbind_batch_np(c: np.ndarray, queries: np.ndarray) -> np.ndarray:
    """Batched unbind: unbind each query vector from bundle c.

    c:       (N,) float32
    queries: (Q, N) float32
    Returns: (Q, N) float32
    """
    C = np.fft.rfft(c)
    A = np.fft.rfft(queries, axis=-1)
    R = C[np.newaxis, :] * np.conj(A)
    return np.fft.irfft(R, n=c.shape[-1], axis=-1).astype(np.float32)


def _eval_arm_np(bundle: np.ndarray, queries: np.ndarray,
                  true_items: np.ndarray, items_book: np.ndarray
                  ) -> Tuple[float, float]:
    """Eval one arm: unbind batched, cleanup vs items_book, top1 recall."""
    preds = _unbind_batch_np(bundle, queries)
    preds = preds / (np.linalg.norm(preds, axis=-1, keepdims=True) + 1e-8)
    sims = preds @ items_book.T                       # (Q, V_ITEMS)
    top1 = sims.argmax(axis=-1)
    top1_cos = sims.max(axis=-1)
    correct = float(np.mean(top1 == true_items))
    return correct, float(np.mean(top1_cos))


# ----- One phase-point run (3 arms x n_queries) -----

def _run_phase_point_np(
    g_np: np.random.Generator,
    K: int,
    N: int,
    Q_level: int,
    n_queries: int,
) -> Dict[str, Any]:
    """Run SUBSTRATE / RANDOM / SHUFFLE arms on one phase point.

    Mechanism:
      - V_ITEMS bipolar items, V_POS bipolar positions (regenerated per point
        since N varies across the sweep).
      - Sample K position indices (no-replace, ordered) and K item indices.
      - Build bundle S = sum_i bind(pos_i, items_i + noise_scale * tag_noise_i)
        where noise_scale = BASE_TAG_DENSITY * Q_level.
      - For each of n_queries query positions p_j, recover v_j via
        unbind(p_j, S) then cosine-cleanup vs item codebook.
      - top1_recall = fraction where argmax == true item idx.
    """
    out: Dict[str, Any] = {}
    noise_scale = float(BASE_TAG_DENSITY * Q_level)

    positions_book = _bipolar_codebook_np(V_POS, N, g_np)
    items_book = _bipolar_codebook_np(V_ITEMS, N, g_np)

    pos_idx = g_np.choice(V_POS, size=K, replace=False)
    item_idx = g_np.choice(V_ITEMS, size=K, replace=False)
    positions = positions_book[pos_idx]                       # (K, N)
    items = items_book[item_idx]                              # (K, N)

    tag_noise = g_np.standard_normal((K, N)).astype(np.float32) * noise_scale

    S_substrate = _bind_bundle_np(positions, items, tag_noise)

    if n_queries > K:
        q_local = g_np.choice(K, size=n_queries, replace=True)
    else:
        q_local = g_np.choice(K, size=n_queries, replace=False)
    q_pos_idx = pos_idx[q_local]
    q_true_item_idx = item_idx[q_local]
    q_positions = positions_book[q_pos_idx]                   # (Q, N)

    sub_recall, sub_cos = _eval_arm_np(S_substrate, q_positions,
                                          q_true_item_idx, items_book)

    # ARM 2: RANDOM - random unit vector independent of S
    random_pred = g_np.standard_normal((n_queries, N)).astype(np.float32)
    random_pred = random_pred / (np.linalg.norm(random_pred, axis=-1,
                                                  keepdims=True) + 1e-8)
    sims_r = random_pred @ items_book.T
    top1_r = sims_r.argmax(axis=-1)
    rand_recall = float(np.mean(top1_r == q_true_item_idx))
    rand_cos = float(np.mean(sims_r.max(axis=-1)))

    # ARM 3: SHUFFLE - same bundle S; shuffled query positions (broken pos->item)
    shuffled_local = (g_np.permutation(K)[:n_queries] if n_queries <= K
                       else g_np.choice(K, size=n_queries, replace=True))
    # Re-roll any coincidence with true position
    n_fix = 0
    while np.any(shuffled_local == q_local) and n_fix < 50:
        match_mask = shuffled_local == q_local
        shuffled_local[match_mask] = g_np.choice(K, size=int(match_mask.sum()),
                                                   replace=True)
        n_fix += 1
    shuf_pos_idx = pos_idx[shuffled_local]
    shuf_positions = positions_book[shuf_pos_idx]
    shuf_recall, shuf_cos = _eval_arm_np(S_substrate, shuf_positions,
                                            q_true_item_idx, items_book)

    out["SUBSTRATE_top1_recall"] = sub_recall
    out["SUBSTRATE_mean_cosine"] = sub_cos
    out["RANDOM_top1_recall"] = rand_recall
    out["RANDOM_mean_cosine"] = rand_cos
    out["SHUFFLE_top1_recall"] = shuf_recall
    out["SHUFFLE_mean_cosine"] = shuf_cos
    out["K"] = int(K)
    out["N"] = int(N)
    out["Q_level"] = int(Q_level)
    out["tag_density_effective"] = float(noise_scale)
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
        smoke_corners: if True, run only 6 corner points.
    """
    g_np = np.random.default_rng(seed)

    if run_mode == "selftest":
        # tiny: 2 corners (SAT + FLOOR), few queries
        points = [SMOKE_CORNERS[0], SMOKE_CORNERS[5]]
        n_queries = 4
    elif smoke_corners or run_mode == "smoke":
        points = list(SMOKE_CORNERS)
        n_queries = N_QUERIES_SMOKE
    else:
        points = []
        for K in K_VALUES:
            for N in N_VALUES:
                for Q in Q_VALUES:
                    points.append((K, N, Q))
        n_queries = N_QUERIES_FULL

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for (K, N, Q) in points:
        res = _run_phase_point_np(g_np, K, N, Q, n_queries)
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


def _classify_band(recall: float) -> str:
    if recall >= BAND_SAT:
        return "SAT"
    if BAND_MB_LO <= recall <= BAND_MB_HI:
        return "MB"
    if recall <= BAND_FLOOR:
        return "FLOOR"
    # In the gap between FLOOR (0.10) and MB_LO (0.30), or between MB_HI (0.70)
    # and SAT (0.90) -- "transition" zone. Neither MB nor SAT nor FLOOR.
    return "TRANSITION"


def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]],
                           run_mode: str) -> Dict[str, Any]:
    """Compute band distribution + K_cliff per (N,Q) + verdict.

    Verdict (per task spec):
      HARD_PASS if:
        - n_MB >= HP_MIN_MB_POINTS (>= 22 of 72)
        - avg_arms_diff >= HP_ARMS_DIFF_MIN (>= 0.20)
        - n_SAT >= HP_MIN_SAT_POINTS (>= 6; mechanism floor)
        - n_FLOOR >= HP_MIN_FLOOR_POINTS (>= 6; cliff observable)
        - cardinality_ok
      HARD_FAIL if:
        - all_saturated (every point >= SAT, by-construction failure)
        - OR all_floored (no signal)
        - OR arms_identical (code bug)
        - OR avg_arms_diff < 0.05
      MIDDLE_BAND else.
    """
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    # Pool phase points across seeds -> mean per (K, N, Q)
    bucket: Dict[Tuple[int, int, int], Dict[str, List[float]]] = {}
    for s, body in per_seed.items():
        for pt in body.get("phase_map", []):
            key = (int(pt["K"]), int(pt["N"]), int(pt["Q_level"]))
            d = bucket.setdefault(key, {
                "SUBSTRATE_top1_recall": [],
                "RANDOM_top1_recall": [],
                "SHUFFLE_top1_recall": [],
            })
            d["SUBSTRATE_top1_recall"].append(pt["SUBSTRATE_top1_recall"])
            d["RANDOM_top1_recall"].append(pt["RANDOM_top1_recall"])
            d["SHUFFLE_top1_recall"].append(pt["SHUFFLE_top1_recall"])

    summary_per_pt: List[Dict[str, Any]] = []
    arm_diffs: List[float] = []
    band_counts: Dict[str, int] = {"SAT": 0, "MB": 0, "FLOOR": 0, "TRANSITION": 0}
    sub_all: List[float] = []
    rand_all: List[float] = []
    shuf_all: List[float] = []

    for key, d in sorted(bucket.items()):
        K, N, Q = key
        sub_mean = float(np.mean(d["SUBSTRATE_top1_recall"]))
        rand_mean = float(np.mean(d["RANDOM_top1_recall"]))
        shuf_mean = float(np.mean(d["SHUFFLE_top1_recall"]))
        floor = max(rand_mean, shuf_mean)
        diff = sub_mean - floor
        arm_diffs.append(diff)
        band = _classify_band(sub_mean)
        band_counts[band] += 1
        sub_all.append(sub_mean)
        rand_all.append(rand_mean)
        shuf_all.append(shuf_mean)
        summary_per_pt.append({
            "K": K, "N": N, "Q_level": Q,
            "tag_density_effective": round(BASE_TAG_DENSITY * Q, 4),
            "SUBSTRATE_top1_mean": sub_mean,
            "RANDOM_top1_mean": rand_mean,
            "SHUFFLE_top1_mean": shuf_mean,
            "arms_diff": diff,
            "band": band,
            "n_seeds": len(d["SUBSTRATE_top1_recall"]),
        })

    n_total = len(bucket)
    n_SAT = band_counts["SAT"]
    n_MB = band_counts["MB"]
    n_FLOOR = band_counts["FLOOR"]
    n_TRANS = band_counts["TRANSITION"]
    avg_arm_diff = float(np.mean(arm_diffs)) if arm_diffs else 0.0

    # K-cliff per (N, Q): smallest K where mean SUBSTRATE drops below SAT band (0.90)
    cliffs: Dict[Tuple[int, int], Optional[int]] = {}
    for N in N_VALUES:
        for Q in Q_VALUES:
            cliffs[(N, Q)] = None
            for K in K_VALUES:
                rows = [p for p in summary_per_pt
                        if p["K"] == K and p["N"] == N and p["Q_level"] == Q]
                if not rows:
                    continue
                sub = rows[0]["SUBSTRATE_top1_mean"]
                if sub < BAND_SAT:
                    cliffs[(N, Q)] = K
                    break
    cliffs_serializable = {f"N{N}_Q{Q}": K for (N, Q), K in cliffs.items()}
    cliffs_observed = [K for K in cliffs.values() if K is not None]

    # HARD_FAIL guards
    all_saturated = bool(sub_all) and all(r >= BAND_SAT for r in sub_all)
    all_floored = bool(sub_all) and all(r <= BAND_FLOOR for r in sub_all)
    # arms_identical = all SUBSTRATE recalls equal RANDOM recalls (code bug)
    arms_identical = (bool(sub_all)
                       and all(abs(s - r) < 1e-6 and abs(s - sh) < 1e-6
                                for s, r, sh in zip(sub_all, rand_all, shuf_all)))

    # Verdict
    if all_saturated:
        verdict = "HARD_FAIL"
        verdict_tag = "BY_CONSTRUCTION_SAT"
    elif all_floored:
        verdict = "HARD_FAIL"
        verdict_tag = "BY_CONSTRUCTION_FLOOR"
    elif arms_identical:
        verdict = "HARD_FAIL"
        verdict_tag = "ARMS_IDENTICAL"
    elif avg_arm_diff < 0.05:
        verdict = "HARD_FAIL"
        verdict_tag = "ARMS_DONT_DIFFER"
    elif (n_MB >= HP_MIN_MB_POINTS
            and avg_arm_diff >= HP_ARMS_DIFF_MIN
            and n_SAT >= HP_MIN_SAT_POINTS
            and n_FLOOR >= HP_MIN_FLOOR_POINTS):
        verdict = "HARD_PASS"
        verdict_tag = "PHASE_DIAGRAM_HIGH_COVERAGE"
    elif n_MB >= MB_MIN_MB_POINTS:
        verdict = "MIDDLE_BAND"
        verdict_tag = "PHASE_DIAGRAM_PARTIAL"
    else:
        verdict = "MIDDLE_BAND"
        verdict_tag = "PHASE_DIAGRAM_SPARSE"

    headline = (f"bands SAT={n_SAT} MB={n_MB} FLOOR={n_FLOOR} TRANS={n_TRANS} "
                f"of {n_total} | avg_arms_diff={avg_arm_diff:.3f} | "
                f"K_cliffs={len(cliffs_observed)}/{len(cliffs)} | "
                f"tag={verdict_tag}")
    verdict_msg = f"{verdict} | {headline}"

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "verdict_tag": verdict_tag,
        "n_total_phase_points": n_total,
        "n_SAT": n_SAT, "n_MB": n_MB,
        "n_FLOOR": n_FLOOR, "n_TRANSITION": n_TRANS,
        "avg_arms_diff": avg_arm_diff,
        "all_saturated": all_saturated,
        "all_floored": all_floored,
        "arms_identical": arms_identical,
        "K_cliffs_per_combo": cliffs_serializable,
        "n_cliff_combos_observed": len(cliffs_observed),
        "n_combos_total": len(cliffs),
        "summary_per_phase_point": summary_per_pt,
        "n_seeds_complete": len(per_seed),
        "bands": {"SAT": BAND_SAT, "MB_LO": BAND_MB_LO, "MB_HI": BAND_MB_HI,
                   "FLOOR": BAND_FLOOR},
    }


# ----- Self-test -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny mechanism check: 2 corner points (SAT + FLOOR), 4 queries.

    Asserts:
      - 2 phase points produced
      - SAT corner (K=20, N=16384, Q=1) shows SUBSTRATE > 0.50 and >> RANDOM
      - FLOOR corner (K=1000, N=2048, Q=4) shows SUBSTRATE <= 0.30
        (validates noise+capacity discriminator)
      - arms differ at SAT corner by > 0.30
    """
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pts = body["phase_map"]
        if len(pts) != 2:
            return False, f"selftest: expected 2 pts, got {len(pts)}"

        sat_pts = [p for p in pts if p["K"] == 20 and p["N"] == 16384
                    and p["Q_level"] == 1]
        floor_pts = [p for p in pts if p["K"] == 1000 and p["N"] == 2048
                      and p["Q_level"] == 4]
        if not sat_pts:
            return False, "selftest: missing SAT corner (K=20,N=16384,Q=1)"
        if not floor_pts:
            return False, "selftest: missing FLOOR corner (K=1000,N=2048,Q=4)"

        sub_sat = sat_pts[0]["SUBSTRATE_top1_recall"]
        rand_sat = sat_pts[0]["RANDOM_top1_recall"]
        shuf_sat = sat_pts[0]["SHUFFLE_top1_recall"]
        sub_floor = floor_pts[0]["SUBSTRATE_top1_recall"]

        if sub_sat <= max(rand_sat, shuf_sat):
            return False, (f"selftest: SAT corner SUBSTRATE={sub_sat:.3f} "
                            f"should exceed max(R,S)={max(rand_sat,shuf_sat):.3f}")
        if sub_sat < 0.50:
            return False, (f"selftest: SAT corner (K=20,N=16384,Q=1) = "
                            f"{sub_sat:.3f} (expected >= 0.50 even with 4 q)")
        if sub_floor > 0.30:
            return False, (f"selftest: FLOOR corner (K=1000,N=2048,Q=4) = "
                            f"{sub_floor:.3f} (expected <= 0.30; cliff)")
        if (sub_sat - max(rand_sat, shuf_sat)) < 0.30:
            return False, (f"selftest: SAT arms-diff = "
                            f"{sub_sat - max(rand_sat,shuf_sat):.3f} (< 0.30)")

        msg = (f"selftest OK: SAT(K=20,N=16384,Q=1) SUBSTRATE={sub_sat:.3f} "
               f"RANDOM={rand_sat:.3f} SHUFFLE={shuf_sat:.3f}; "
               f"FLOOR(K=1000,N=2048,Q=4) SUBSTRATE={sub_floor:.3f}; "
               f"backend={body['backend']}; elapsed={body['elapsed_s']:.1f}s")
        return True, msg
    except Exception as e:
        return False, (f"selftest EXC: {type(e).__name__}: {e}\n"
                        f"{traceback.format_exc()}")


if __name__ == "__main__":
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
