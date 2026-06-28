"""Shared core for substrate_sequence_binding_K_cliff_phase_diagram_v1 sibling cells.

Provides the GPU-batched phase-diagram sweep over (K, N_DIM, tag_density)
with 3 arms (SUBSTRATE / RANDOM / SHUFFLE) measuring HRR sequence-binding
top1 recall and the K-cliff per (N, tag_density).

Sibling cells import run_one_seed_phase_diagram(seed) and aggregate.
ASCII-only. CUDA primary, numpy fallback with WARN.

Author: exp_dev 2026-06-28 (Opus 4.7 1M, agent-spawn) Stage 1 phase-diagram coverage
"""
from __future__ import annotations

# CRITICAL: torch at TOP OF FILE per Fix #24 (gate validates GPU eligibility on top-level imports)
import torch

import math
import sys
import time
import traceback
from typing import Any, Dict, List, Optional, Tuple

import numpy as np

_TORCH_OK = True
_CUDA_OK = bool(torch.cuda.is_available())

ANCHOR_PREFIX = "substrate_sequence_binding_K_cliff_phase_diagram_v1"

# ----- Phase axes (LOCKED) -----
K_VALUES = (10, 20, 50, 100, 200, 500, 1000)              # 7 points
N_VALUES = (2048, 4096, 8192, 16384)                      # 4 points
TAG_VALUES = (0.1, 0.3, 0.5)                              # 3 points
ARMS = ("SUBSTRATE", "RANDOM", "SHUFFLE")

# Smoke 6 corner points: (K, N, tag) per pre-reg
SMOKE_CORNERS = (
    (10,   2048,  0.1),   # low-K low-N low-tag (near-mid)
    (1000, 2048,  0.1),   # high-K low-N low-tag (cliff-fail)
    (10,   16384, 0.1),   # low-K high-N low-tag (saturate)
    (1000, 16384, 0.5),   # high-K high-N high-tag (cliff-fail)
    (100,  4096,  0.3),   # mid (cliff-fail per analytic K_crit)
    (500,  2048,  0.5),   # high-K low-N high-tag (cliff-fail)
)

# Pre-reg bands (mirror prereg .md; LOCKED at module load)
HP_CLIFF_FLOOR_RECALL = 0.50         # K_cliff defined as drop below this
HP_LOW_K_FLOOR_RECALL = 0.90         # low-K high-N mechanism floor
HP_LOW_TOP1_FOR_CLIFF = 0.20         # must see some point < this to prove cliff observable
HP_AVG_ARMS_DIFF_MIN = 0.20          # SUBSTRATE - max(RANDOM, SHUFFLE) avg gate
MB_AVG_ARMS_DIFF_LO = 0.10
HF_NO_CLIFF_RECALL_MIN = 0.95        # if ALL phase pts >= this, HARD_FAIL saturation
HP_MIN_CLIFF_COMBOS = 6              # >= 6 of 12 (N, tag) combos with observable cliff
MB_MIN_CLIFF_COMBOS = 3

# Per-point query count (FULL); SMOKE uses smaller
N_QUERIES_FULL = 10
N_QUERIES_SMOKE = 2

# V_ITEMS = item codebook size; must be >= max K + max queries for sampling without replacement
V_ITEMS = 1024
V_POS = 1024  # position codebook size; same upper

REQUIRED_FIELDS = ("verdict", "verdict_msg", "elapsed_s", "summary")


def get_backend_label() -> str:
    if _CUDA_OK:
        return "torch.cuda"
    if _TORCH_OK:
        return "torch.cpu"
    return "numpy.cpu"


# ----- HRR primitives (torch + numpy variants) -----

def _bipolar_codebook_torch(V: int, N: int, gen: torch.Generator,
                             device: str) -> torch.Tensor:
    X = (torch.randint(0, 2, (V, N), generator=gen, device=device,
                       dtype=torch.float32) * 2 - 1)
    X = X / (torch.linalg.norm(X, dim=1, keepdim=True) + 1e-8)
    return X


def _bipolar_codebook_np(V: int, N: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(V, N)) * 2 - 1).astype(np.float32)
    X = X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)
    return X


def _bind_bundle_torch(positions: torch.Tensor, items: torch.Tensor,
                        tag_noise: torch.Tensor) -> torch.Tensor:
    """Bind K (pos, item) pairs (plus per-position tag noise) and sum-bundle.

    positions: (K, N) float32 bipolar
    items:     (K, N) float32 bipolar
    tag_noise: (K, N) float32 dense noise (already scaled by tag_density)
    Returns:   (N,) float32 normalized bundle
    """
    # Item with additive tag noise (models per-position contextual noise)
    items_noisy = items + tag_noise
    items_noisy = items_noisy / (torch.linalg.norm(items_noisy, dim=-1,
                                                     keepdim=True) + 1e-8)
    P = torch.fft.rfft(positions, dim=-1)
    I = torch.fft.rfft(items_noisy, dim=-1)
    PROD = P * I                                          # (K, N//2+1) complex
    bound = torch.fft.irfft(PROD, n=positions.shape[-1], dim=-1).to(torch.float32)
    bundle = bound.sum(dim=0)
    n = torch.linalg.norm(bundle) + 1e-8
    return bundle / n


def _unbind_torch(c: torch.Tensor, a: torch.Tensor) -> torch.Tensor:
    """Unbind a from c via FFT correlation."""
    C = torch.fft.rfft(c, dim=-1)
    A = torch.fft.rfft(a, dim=-1)
    R = C * torch.conj(A)
    return torch.fft.irfft(R, n=c.shape[-1], dim=-1).to(torch.float32)


def _bind_bundle_np(positions: np.ndarray, items: np.ndarray,
                     tag_noise: np.ndarray) -> np.ndarray:
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


def _unbind_np(c: np.ndarray, a: np.ndarray) -> np.ndarray:
    C = np.fft.rfft(c)
    A = np.fft.rfft(a)
    R = C * np.conj(A)
    return np.fft.irfft(R, n=c.shape[-1]).astype(np.float32)


# ----- One phase-point run (3 arms x N_QUERIES) -----

def _run_phase_point_torch(
    g_torch: torch.Generator,
    g_np: np.random.Generator,
    K: int,
    N: int,
    tag_density: float,
    n_queries: int,
    device: str,
) -> Dict[str, float]:
    """Run SUBSTRATE / RANDOM / SHUFFLE arms on one phase point via torch.

    Mechanism:
      - V_ITEMS bipolar items, V_POS bipolar positions (regenerated each phase
        point since N changes across the sweep).
      - Sample K position indices (without replacement, ordered) and K item
        indices (without replacement).
      - Build bundle S = sum_i bind(pos_i, items_i + tag*noise_i).
      - For each query position p_j (sampled from the K presented), recover
        v_j via unbind(p_j, S) then cosine-cleanup vs item codebook.
      - top1_recall = fraction of queries where argmax == true item idx.

    Returns dict with per-arm top1_recall + mean_cosine.
    """
    out: Dict[str, float] = {}

    # Codebooks for this N (regenerate per phase point because N varies)
    positions_book = _bipolar_codebook_torch(V_POS, N, g_torch, device)
    items_book = _bipolar_codebook_torch(V_ITEMS, N, g_torch, device)

    # Sample K positions + K items without replacement
    # (use numpy generator for index sampling reproducibility across backends)
    pos_idx = g_np.choice(V_POS, size=K, replace=False)
    item_idx = g_np.choice(V_ITEMS, size=K, replace=False)
    pos_idx_t = torch.from_numpy(pos_idx).long().to(device)
    item_idx_t = torch.from_numpy(item_idx).long().to(device)

    positions = positions_book[pos_idx_t]                    # (K, N)
    items = items_book[item_idx_t]                            # (K, N)

    # Per-position tag noise (dense float32; scaled by tag_density)
    tag_noise = torch.randn((K, N), generator=g_torch, device=device,
                              dtype=torch.float32) * float(tag_density)

    # Build the SUBSTRATE bundle
    S_substrate = _bind_bundle_torch(positions, items, tag_noise)

    # Sample query positions from the K presented
    if n_queries > K:
        q_local = g_np.choice(K, size=n_queries, replace=True)
    else:
        q_local = g_np.choice(K, size=n_queries, replace=False)
    q_pos_idx = pos_idx[q_local]                               # global pos idx of queries
    q_true_item_idx = item_idx[q_local]                        # true item answers
    q_positions = positions_book[torch.from_numpy(q_pos_idx).long().to(device)]   # (Q, N)
    q_true_items = torch.from_numpy(q_true_item_idx).long().to(device)

    # ARM 1: SUBSTRATE - unbind query pos from S, cleanup vs items_book
    def _eval_against_bundle(bundle: torch.Tensor,
                              queries: torch.Tensor,
                              true_items: torch.Tensor) -> Tuple[float, float]:
        preds = torch.stack([_unbind_torch(bundle, queries[i])
                              for i in range(queries.shape[0])], dim=0)   # (Q, N)
        preds = preds / (torch.linalg.norm(preds, dim=-1, keepdim=True) + 1e-8)
        sims = preds @ items_book.T                                       # (Q, V_ITEMS)
        top1 = sims.argmax(dim=-1)
        top1_cos = sims.max(dim=-1).values
        correct = (top1 == true_items).float().mean().item()
        return float(correct), float(top1_cos.mean().item())

    sub_recall, sub_cos = _eval_against_bundle(S_substrate, q_positions, q_true_items)

    # ARM 2: RANDOM - random vector of unit norm (independent of S); cleanup vs items
    random_pred = torch.randn((n_queries, N), generator=g_torch,
                                device=device, dtype=torch.float32)
    random_pred = random_pred / (torch.linalg.norm(random_pred, dim=-1,
                                                      keepdim=True) + 1e-8)
    sims_r = random_pred @ items_book.T
    top1_r = sims_r.argmax(dim=-1)
    top1_r_cos = sims_r.max(dim=-1).values
    rand_recall = float((top1_r == q_true_items).float().mean().item())
    rand_cos = float(top1_r_cos.mean().item())

    # ARM 3: SHUFFLE - use SAME bundle S as substrate, but query with SHUFFLED
    # position vectors (broken pos->item map). Tests whether ORDER matters.
    shuffled_local = g_np.permutation(K)[:n_queries] if n_queries <= K else \
                      g_np.choice(K, size=n_queries, replace=True)
    # Ensure shuffled positions don't accidentally match true positions
    # (re-roll any coincidences)
    n_fix = 0
    while np.any(shuffled_local == q_local) and n_fix < 50:
        match_mask = shuffled_local == q_local
        shuffled_local[match_mask] = g_np.choice(K, size=int(match_mask.sum()),
                                                   replace=True)
        n_fix += 1
    shuf_pos_idx = pos_idx[shuffled_local]
    shuf_positions = positions_book[torch.from_numpy(shuf_pos_idx).long().to(device)]
    shuf_recall, shuf_cos = _eval_against_bundle(S_substrate, shuf_positions, q_true_items)

    out["SUBSTRATE_top1_recall"] = sub_recall
    out["SUBSTRATE_mean_cosine"] = sub_cos
    out["RANDOM_top1_recall"] = rand_recall
    out["RANDOM_mean_cosine"] = rand_cos
    out["SHUFFLE_top1_recall"] = shuf_recall
    out["SHUFFLE_mean_cosine"] = shuf_cos
    out["K"] = int(K)
    out["N"] = int(N)
    out["tag_density"] = float(tag_density)
    out["n_queries"] = int(n_queries)
    return out


def _run_phase_point_np(
    g_np: np.random.Generator,
    K: int,
    N: int,
    tag_density: float,
    n_queries: int,
) -> Dict[str, float]:
    """Numpy fallback (CPU-only) for environments without CUDA."""
    out: Dict[str, float] = {}
    positions_book = _bipolar_codebook_np(V_POS, N, g_np)
    items_book = _bipolar_codebook_np(V_ITEMS, N, g_np)

    pos_idx = g_np.choice(V_POS, size=K, replace=False)
    item_idx = g_np.choice(V_ITEMS, size=K, replace=False)
    positions = positions_book[pos_idx]
    items = items_book[item_idx]
    tag_noise = g_np.standard_normal((K, N)).astype(np.float32) * float(tag_density)

    S_substrate = _bind_bundle_np(positions, items, tag_noise)

    if n_queries > K:
        q_local = g_np.choice(K, size=n_queries, replace=True)
    else:
        q_local = g_np.choice(K, size=n_queries, replace=False)
    q_pos_idx = pos_idx[q_local]
    q_true_item_idx = item_idx[q_local]
    q_positions = positions_book[q_pos_idx]

    def _eval(bundle, queries, true_items):
        preds = np.stack([_unbind_np(bundle, queries[i])
                           for i in range(queries.shape[0])], axis=0)
        preds = preds / (np.linalg.norm(preds, axis=-1, keepdims=True) + 1e-8)
        sims = preds @ items_book.T
        top1 = sims.argmax(axis=-1)
        top1_cos = sims.max(axis=-1)
        correct = float(np.mean(top1 == true_items))
        return correct, float(np.mean(top1_cos))

    sub_recall, sub_cos = _eval(S_substrate, q_positions, q_true_item_idx)

    random_pred = g_np.standard_normal((n_queries, N)).astype(np.float32)
    random_pred = random_pred / (np.linalg.norm(random_pred, axis=-1,
                                                  keepdims=True) + 1e-8)
    sims_r = random_pred @ items_book.T
    top1_r = sims_r.argmax(axis=-1)
    rand_recall = float(np.mean(top1_r == q_true_item_idx))
    rand_cos = float(np.mean(sims_r.max(axis=-1)))

    shuffled_local = g_np.permutation(K)[:n_queries] if n_queries <= K else \
                      g_np.choice(K, size=n_queries, replace=True)
    n_fix = 0
    while np.any(shuffled_local == q_local) and n_fix < 50:
        match_mask = shuffled_local == q_local
        shuffled_local[match_mask] = g_np.choice(K, size=int(match_mask.sum()),
                                                   replace=True)
        n_fix += 1
    shuf_pos_idx = pos_idx[shuffled_local]
    shuf_positions = positions_book[shuf_pos_idx]
    shuf_recall, shuf_cos = _eval(S_substrate, shuf_positions, q_true_item_idx)

    out["SUBSTRATE_top1_recall"] = sub_recall
    out["SUBSTRATE_mean_cosine"] = sub_cos
    out["RANDOM_top1_recall"] = rand_recall
    out["RANDOM_mean_cosine"] = rand_cos
    out["SHUFFLE_top1_recall"] = shuf_recall
    out["SHUFFLE_mean_cosine"] = shuf_cos
    out["K"] = int(K)
    out["N"] = int(N)
    out["tag_density"] = float(tag_density)
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
        smoke_corners: if True, only run 6 corner points (smoke gate).
    """
    device = "cuda" if _CUDA_OK else "cpu"
    g_torch = torch.Generator(device=device).manual_seed(int(seed))
    g_np = np.random.default_rng(seed)

    n_queries = N_QUERIES_SMOKE if (run_mode != "full") else N_QUERIES_FULL

    if smoke_corners:
        points = list(SMOKE_CORNERS)
    elif run_mode == "selftest":
        # tiny selftest: 2 corners with small queries
        points = [SMOKE_CORNERS[0], SMOKE_CORNERS[2]]   # near-mid + saturate
        n_queries = 2
    else:
        points = []
        for K in K_VALUES:
            for N in N_VALUES:
                for tag in TAG_VALUES:
                    points.append((K, N, tag))

    phase_map: List[Dict[str, Any]] = []
    started = time.time()
    for (K, N, tag) in points:
        if _CUDA_OK:
            res = _run_phase_point_torch(g_torch, g_np, K, N, tag, n_queries, device)
        else:
            # Use torch.cpu if available, else numpy
            if _TORCH_OK:
                res = _run_phase_point_torch(g_torch, g_np, K, N, tag, n_queries, device)
            else:
                res = _run_phase_point_np(g_np, K, N, tag, n_queries)
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
    """Compute K_cliff per (N, tag) + verdict from one or more seed phase-maps."""
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed partials",
                "summary": "no per-seed partials"}

    # Pool all phase points across seeds; compute mean per (K, N, tag)
    bucket: Dict[Tuple[int, int, float], Dict[str, List[float]]] = {}
    for s, body in per_seed.items():
        for pt in body.get("phase_map", []):
            key = (int(pt["K"]), int(pt["N"]), float(pt["tag_density"]))
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
    sub_all_recalls: List[float] = []
    regime_flip_points: List[Tuple[int, int, float]] = []
    for key, d in sorted(bucket.items()):
        K, N, tag = key
        sub_mean = float(np.mean(d["SUBSTRATE_top1_recall"]))
        rand_mean = float(np.mean(d["RANDOM_top1_recall"]))
        shuf_mean = float(np.mean(d["SHUFFLE_top1_recall"]))
        floor = max(rand_mean, shuf_mean)
        diff = sub_mean - floor
        arm_diffs.append(diff)
        sub_all_recalls.append(sub_mean)
        # META_RULE_AM check: low-K low-tag high-N point where SUBSTRATE <= SHUFFLE
        if (K == 10 and abs(tag - 0.1) < 1e-6 and N >= 4096
                and sub_mean <= shuf_mean + 1e-6):
            regime_flip_points.append((K, N, tag))
        summary_per_pt.append({
            "K": K, "N": N, "tag_density": tag,
            "SUBSTRATE_top1_mean": sub_mean,
            "RANDOM_top1_mean": rand_mean,
            "SHUFFLE_top1_mean": shuf_mean,
            "arms_diff": diff,
            "n_seeds": len(d["SUBSTRATE_top1_recall"]),
        })

    # K_cliff per (N, tag): smallest K where SUBSTRATE drops below floor
    cliffs: Dict[Tuple[int, float], Optional[int]] = {}
    for N in N_VALUES:
        for tag in TAG_VALUES:
            cliffs[(N, tag)] = None
            for K in K_VALUES:
                rows = [p for p in summary_per_pt
                        if p["K"] == K and p["N"] == N
                        and abs(p["tag_density"] - tag) < 1e-6]
                if not rows:
                    continue
                sub = rows[0]["SUBSTRATE_top1_mean"]
                if sub < HP_CLIFF_FLOOR_RECALL:
                    cliffs[(N, tag)] = K
                    break

    cliffs_serializable = {f"N{N}_tag{tag:.2f}": K for (N, tag), K in cliffs.items()}
    cliffs_observed = [K for K in cliffs.values() if K is not None]
    n_cliff_combos = len(cliffs_observed)
    n_total_combos = len(cliffs)

    if cliffs_observed:
        K_cliff_min = int(min(cliffs_observed))
        cliff_min_loc = [k for k, v in cliffs.items() if v == K_cliff_min][0]
    else:
        K_cliff_min = None
        cliff_min_loc = None

    avg_arm_diff = float(np.mean(arm_diffs)) if arm_diffs else 0.0
    all_saturated = bool(all(r >= HF_NO_CLIFF_RECALL_MIN for r in sub_all_recalls)) \
                    if sub_all_recalls else False

    # Low-K high-N mechanism floor (HARD_PASS gate B)
    low_k_high_n_pts = [p for p in summary_per_pt if p["K"] == 10 and p["N"] >= 8192]
    low_k_high = any(p["SUBSTRATE_top1_mean"] >= HP_LOW_K_FLOOR_RECALL
                      for p in low_k_high_n_pts)

    # Cliff-observable check (HARD_PASS gate C): some point shows top1 < 0.20
    cliff_observable = any(p["SUBSTRATE_top1_mean"] < HP_LOW_TOP1_FOR_CLIFF
                            for p in summary_per_pt)

    # Monotone-with-N scaling check (HARD_PASS gate E)
    # For each tag, K_cliff(N) should be monotone non-decreasing in N
    monotone_tags = 0
    for tag in TAG_VALUES:
        cliffs_for_tag = [cliffs[(N, tag)] for N in N_VALUES]
        # Replace None (no cliff observed) with infinity for monotone check
        cliffs_inf = [c if c is not None else 10**9 for c in cliffs_for_tag]
        is_monotone = all(cliffs_inf[i] <= cliffs_inf[i+1] + 0  # allow equal
                          for i in range(len(cliffs_inf)-1))
        if is_monotone:
            monotone_tags += 1
    monotone_scaling_met = monotone_tags >= 2

    am_flag = len(regime_flip_points) > 0

    # Verdict
    if all_saturated or avg_arm_diff < 0.10 or am_flag:
        verdict = "HARD_FAIL"
    elif (n_cliff_combos >= HP_MIN_CLIFF_COMBOS and low_k_high and cliff_observable
          and avg_arm_diff >= HP_AVG_ARMS_DIFF_MIN and monotone_scaling_met):
        verdict = "HARD_PASS"
    elif n_cliff_combos >= MB_MIN_CLIFF_COMBOS and avg_arm_diff >= MB_AVG_ARMS_DIFF_LO:
        verdict = "MIDDLE_BAND"
    else:
        verdict = "MIDDLE_BAND"

    headline = (f"K_cliff_min={K_cliff_min} loc={cliff_min_loc} | "
                f"cliffs={n_cliff_combos}/{n_total_combos} | "
                f"avg_arms_diff={avg_arm_diff:.3f} | "
                f"low_k_high_n_floor={low_k_high} | "
                f"cliff_observable={cliff_observable} | "
                f"monotone_tags={monotone_tags}/3 | "
                f"saturated={all_saturated} | regime_flip={am_flag}")

    verdict_msg = f"{verdict} | {headline}"

    return {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "K_cliff_min": K_cliff_min,
        "K_cliff_min_location": (None if cliff_min_loc is None
                                  else {"N": cliff_min_loc[0],
                                        "tag_density": cliff_min_loc[1]}),
        "K_cliffs_per_combo": cliffs_serializable,
        "n_cliff_combos_observable": n_cliff_combos,
        "n_combos_total": n_total_combos,
        "avg_arms_diff": avg_arm_diff,
        "all_saturated": all_saturated,
        "low_k_high_n_mechanism_floor_met": bool(low_k_high),
        "cliff_observable": bool(cliff_observable),
        "monotone_with_N_tags": int(monotone_tags),
        "monotone_scaling_met": bool(monotone_scaling_met),
        "meta_rule_am_regime_flip_points": [list(p) for p in regime_flip_points],
        "summary_per_phase_point": summary_per_pt,
        "n_seeds_complete": len(per_seed),
    }


# ----- Self-test (called from cell scripts via --self-test) -----

def selftest(seed: int = 7) -> Tuple[bool, str]:
    """Tiny selftest: 2 corner points (near-mid + saturate), 2 queries.

    Asserts:
      - phase_map non-empty
      - SUBSTRATE > RANDOM by > 0 at low-K high-N (saturate corner)
      - cardinality matches (2 points)
    """
    try:
        body = run_one_seed_phase_diagram(seed, run_mode="selftest")
        if not body.get("phase_map"):
            return False, "selftest: empty phase_map"
        pts = body["phase_map"]
        if len(pts) != 2:
            return False, f"selftest: expected 2 pts, got {len(pts)}"

        # Saturate corner = (10, 16384, 0.1) should show SUBSTRATE >> RANDOM
        sat_pts = [p for p in pts if p["K"] == 10 and p["N"] == 16384]
        if not sat_pts:
            return False, "selftest: missing saturate corner (K=10, N=16384)"
        sub = sat_pts[0]["SUBSTRATE_top1_recall"]
        rand = sat_pts[0]["RANDOM_top1_recall"]
        if sub <= rand:
            return False, (f"selftest: SUBSTRATE={sub:.3f} should exceed "
                            f"RANDOM={rand:.3f} at low-K high-N")
        if sub < 0.30:
            return False, (f"selftest: SUBSTRATE at (K=10, N=16384, tag=0.1) = "
                            f"{sub:.3f} (expected > 0.30 even with 2 queries)")

        msg = (f"selftest OK: SUBSTRATE(K=10,N=16384,tag=0.1)={sub:.3f}, "
               f"RANDOM={rand:.3f}, backend={body['backend']}, "
               f"elapsed={body['elapsed_s']:.1f}s")
        return True, msg
    except Exception as e:
        return False, (f"selftest EXC: {type(e).__name__}: {e}\n"
                        f"{traceback.format_exc()}")


if __name__ == "__main__":
    ok, msg = selftest(7)
    print("[core selftest]", "OK" if ok else "FAIL", msg)
    sys.exit(0 if ok else 1)
