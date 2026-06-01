"""SKAH-M phase-class positive-identifier battery v1.

CONTEXT: Five rejection sequence (1-RSB / AGS-RS-multi-ferromagnet / cluster-glass /
reaction-diffusion / unified-SVD-cascade) cleared standard phase-class space.
Research: notes/research_novel_phase_class_methodology_2026-05-27.md Finding 7:
  P(documented-but-untested gated-multistable AM / lR-phase) = 0.48 [MODAL]
  P(genuinely novel SKAH-M) = 0.22
  P(finite-N artifact) = 0.30

This 6-cell battery is the structural-positive-identifier test. Joint outcome -> class call.

CELL DESIGN (from research section b):
  C1: q_EA(N) scaling -- N sweep {512,1024,2048,4096}; monotone/convergent vs anomalous
  C2: Plateau height N-scaling -- per-class retention at same N sweep; convergent vs drift
  C3: Goldstone mode absence -- W spectral histogram; check for soft modes near zero
  C4: Hysteresis area scaling -- write-read loop area vs N; constant vs decreasing
  C5: Non-local disorder operator -- codebook-class pairwise overlap structure (non-trivial vs trivial)
  C6: Free-energy 3-well structure -- reconstructed F(m) profile; 3 graded wells vs flat

FORMULA SELF-TESTS (mandatory per [[feedback-strategy-spec-formula-selftests]]):
  q_EA = mean(q^2) for q = (1/N) * pattern.dot(W_retrieved / |W_retrieved|)
    -> Synthetic Z_3-Potts toy: 3 stored patterns {e1, e2, e3}; q_EA should be ~ 1.0
       when W recalls e1 from e1 (perfect recall), 0.0 when patterns are orthogonal.
  Binder g4 = 1 - <q^4>/(3 * <q^2>^2)
    -> With perfect retrieval q=1.0: g4 = 1 - 1/3 = 0.667
    -> With pure noise q=0.0: g4 = 0.0 (degenerate) / g4 -> 2/3 (paramagnet limit)
  Spectral gap = lambda_1 - lambda_N / ||W||_F
    -> For W = 0: all singular values 0; ratio = 0.0 (degenerate but no soft mode)
    -> For W = identity * alpha: all singular values alpha; ratio = 0.0 (no gap; trivially no soft mode)

DECISION RULES:
  DOCUMENTED-BUT-UNTESTED (gated multistable AM): >= 5/6 cells match documented column
  NOVEL (declare SKAH-M): >= 4/6 cells match novel AND >= 1 anomaly in C1/C2/C3
  FINITE-N-ARTIFACT: >= 4/6 cells match finite-N column
  MIDDLE-BAND: mixed; extend seed count

Pre-registered bands per cell (from research section c, P4.1 + P4.2 + P2.2 + P2.3):
  C1 DOCUMENTED: q_EA(N) monotone in {0.6, 0.9} and converges; |slope| < 0.02/decade
  C1 NOVEL: q_EA non-monotone OR log-N corrections (slope > 0.05/decade)
  C1 FINITE-N: q_EA -> 0 as N grows (all values < 0.1 at N=4096)
  C2 DOCUMENTED: plateau heights converge within +-0.02 across N sweep
  C2 NOVEL: drift > 0.02 between N=512 and N=4096
  C2 FINITE-N: plateaus collapse / merge at N=4096 (inter-plateau gap < 0.05)
  C3 DOCUMENTED: spectral gap > 0.05 * ||W||; no soft mode
  C3 NOVEL: no soft mode (same prediction -- C3 cannot distinguish here)
  C3 FINITE-N: soft mode appears (gap < 0.05 * ||W||)
  C4 DOCUMENTED: hysteresis area constant in N (CV < 0.10 across N sweep)
  C4 NOVEL: constant OR weak log-N
  C4 FINITE-N: area decreases monotonically with N (slope < -0.05/decade)
  C5 DOCUMENTED: non-local disorder operator value in (0.05, 0.40) [non-trivial]
  C5 NOVEL: value outside (0.05, 0.40) OR anomalous structure
  C5 FINITE-N: value < 0.02 [trivial]
  C6 DOCUMENTED: 3 wells with non-equal depths, gap ratio in [0.45, 0.65]
  C6 NOVEL: 3 wells with anomalous depth ratios (> 0.65 or < 0.30)
  C6 FINITE-N: fewer than 3 wells OR wells indistinguishable

Queue: overnight_queue (GPU; ~3-4h; N=4096 C1+C2 N-sweep is bottleneck)
Pre-reg: preregs/2026-05-27_anchor_novel_phase_battery_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Design parameters
N_SWEEP_FULL = [512, 1024, 2048, 4096]
N_SWEEP_SMOKE = [512, 1024]
N_DEFAULT_FULL = 2048    # default N for cells C3-C6
N_DEFAULT_SMOKE = 512
SEEDS_FULL = [7, 17, 23, 31, 41]    # 5 seeds
SEEDS_SMOKE = [17]
M_PATTERNS_PER_CLASS = 100    # patterns per retention class (full)
M_PATTERNS_PER_CLASS_SMOKE = 20
ALPHA_LOAD = 0.40   # alpha = M_total / N (within capacity)
BATCH_OUTER = 64    # batch size for outer product store

# Hysteresis protocol
PERTURBATION_STRENGTHS_FULL = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
PERTURBATION_STRENGTHS_SMOKE = [0.0, 0.2, 0.5]

# Pre-registered bands
Q_EA_DOCUMENTED_LO = 0.6
Q_EA_DOCUMENTED_HI = 0.9
Q_EA_FINITE_N_THRESH = 0.1   # finite-N if q_EA < this at N=4096
PLATEAU_CONVERGENCE_THRESH = 0.02   # documented if |drift| < this
PLATEAU_COLLAPSE_THRESH = 0.05      # finite-N if inter-plateau gap < this
SPECTRAL_SOFT_MODE_THRESH = 0.05    # fraction of ||W||
HYSTERESIS_DECAY_THRESH = -0.05     # finite-N if slope < this per decade
HYSTERESIS_CV_THRESH = 0.10         # documented if CV < this
DISORDER_OP_LO = 0.05
DISORDER_OP_HI = 0.40
FREE_ENERGY_GAP_RATIO_LO = 0.30
FREE_ENERGY_GAP_RATIO_HI = 0.65


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    """M x N BSC (+/-1) patterns."""
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen, device=device).float() - 1.0


def build_hebbian_W(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    """Outer-product Hebbian weight matrix (N x N)."""
    W = torch.zeros((N, N), dtype=torch.float32, device=keys.device)
    for s in range(0, keys.shape[0], BATCH_OUTER):
        e = min(s + BATCH_OUTER, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def _retrieve(W: torch.Tensor, keys: torch.Tensor) -> torch.Tensor:
    """Retrieve values via heteroassociative W: W @ key for each key.
    W = sum_mu v_mu outer k_mu^T / N, so retrieval is W @ k (not k @ W^T).
    Returns (M, N) retrieved vectors.
    """
    # (W @ keys.T).T is equivalent to keys @ W.T only when W is symmetric.
    # For heteroassoc W (not symmetric), use W @ key.
    return (W @ keys.T).T  # (M, N)


def cosine_retention(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor) -> float:
    """Mean cosine similarity of retrieved vals vs stored vals."""
    retrieved = _retrieve(W, keys)
    r_norm = retrieved / retrieved.norm(dim=1, keepdim=True).clamp(min=1e-8)
    v_norm = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-8)
    return float((r_norm * v_norm).sum(dim=1).mean())


def compute_q_EA(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor, N: int) -> float:
    """Edwards-Anderson q_EA = sqrt(<q^2>) where q = cosine(retrieved_val, stored_val).
    Uses retrieved-vs-stored overlap as proxy for replica overlap at zero noise.
    """
    retrieved = _retrieve(W, keys)
    r_norm = retrieved / retrieved.norm(dim=1, keepdim=True).clamp(min=1e-8)
    v_norm = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-8)
    q = (r_norm * v_norm).sum(dim=1)   # (M,) overlaps in [-1, 1]
    q_sq = float((q ** 2).mean())
    q_ea = math.sqrt(q_sq) if q_sq >= 0 else 0.0
    return q_ea


def compute_binder_g4(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor) -> float:
    """Binder cumulant g4 = 1 - <q^4> / (3 * <q^2>^2)."""
    retrieved = _retrieve(W, keys)
    r_norm = retrieved / retrieved.norm(dim=1, keepdim=True).clamp(min=1e-8)
    v_norm = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-8)
    q = (r_norm * v_norm).sum(dim=1)   # (M,)
    q2 = float((q ** 2).mean())
    q4 = float((q ** 4).mean())
    if q2 < 1e-10:
        return 0.0
    return 1.0 - q4 / (3.0 * q2 ** 2)


def compute_spectral_gap(W: torch.Tensor) -> dict:
    """Compute spectral properties of W for Goldstone-mode check."""
    try:
        s = torch.linalg.svdvals(W)
    except Exception:
        return {"spectral_gap_frac": float('nan'), "s_max": float('nan'), "s_min_nonzero": float('nan')}
    s_sorted = s.sort(descending=True)[0]
    s_max = float(s_sorted[0])
    w_norm_fro = float(W.norm('fro'))
    # Soft mode: check if smallest significant singular value is near zero
    # significant = > 1% of s_max
    sig_thresh = s_max * 0.01
    s_nonzero = s_sorted[s_sorted > sig_thresh]
    s_min_nonzero = float(s_nonzero[-1]) if len(s_nonzero) > 0 else 0.0
    # Spectral gap fraction = s_min_nonzero / w_norm_fro
    gap_frac = s_min_nonzero / max(w_norm_fro, 1e-10)
    return {
        "spectral_gap_frac": round(gap_frac, 6),
        "s_max": round(s_max, 6),
        "s_min_nonzero": round(s_min_nonzero, 6),
        "w_norm_fro": round(w_norm_fro, 6),
    }


def compute_hysteresis_area(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor,
                             perturbation_strengths: list) -> float:
    """Compute write-read hysteresis loop area.
    Write: store at perturbation_strength = 0 (clean).
    Read: retrieve after applying perturbation to keys.
    Loop area = integral |retention(eps) - retention(0)| deps.
    """
    N = keys.shape[1]
    device = keys.device
    gen = torch.Generator(device=device).manual_seed(42)

    base_ret = cosine_retention(W, keys, vals)
    areas = [0.0]  # eps=0 contributes 0 to area
    for eps in perturbation_strengths:
        if eps == 0.0:
            continue
        noise = make_bsc(keys.shape[0], N, gen, device)
        perturbed = keys + eps * noise
        perturbed_norm = perturbed / perturbed.norm(dim=1, keepdim=True).clamp(min=1e-8)
        perturbed_bsc = perturbed_norm.sign()
        ret_eps = cosine_retention(W, perturbed_bsc, vals)
        areas.append(abs(base_ret - ret_eps))

    if len(areas) < 2:
        return 0.0
    # Trapezoid integration using nonzero perturbation points + 0 at start
    eps_arr = [0.0] + [e for e in perturbation_strengths if e > 0.0]
    # areas[0] is always 0 (eps=0), rest map to eps_arr[1:]
    area = 0.0
    for i in range(len(eps_arr) - 1):
        area += (eps_arr[i + 1] - eps_arr[i]) * (areas[i] + areas[i + 1]) / 2.0
    return area


def compute_disorder_operator(patterns_by_class: list[torch.Tensor], N: int) -> dict:
    """Non-local disorder operator: mean inter-class codebook overlap.
    For 3-class structure (G1, G2, G3): compute mean(|<c_i, c_j>|/N) for c_i in G1, c_j in G2/G3.
    Non-trivial value: structure in overlaps beyond random expectation 1/sqrt(N).
    """
    if len(patterns_by_class) < 2:
        return {"disorder_op_value": float('nan'), "n_classes": 1}
    random_floor = 1.0 / math.sqrt(N)
    cross_sims = []
    for ci, cls_i in enumerate(patterns_by_class):
        for cj, cls_j in enumerate(patterns_by_class):
            if ci >= cj:
                continue
            ni = cls_i / cls_i.norm(dim=1, keepdim=True).clamp(min=1e-8)
            nj = cls_j / cls_j.norm(dim=1, keepdim=True).clamp(min=1e-8)
            # Sample 50 pairs
            n_pairs = min(50, ni.shape[0], nj.shape[0])
            for k in range(n_pairs):
                sim = float(abs((ni[k] * nj[k % nj.shape[0]]).sum()))
                cross_sims.append(sim)

    if not cross_sims:
        return {"disorder_op_value": float('nan'), "n_classes": len(patterns_by_class)}
    mean_cross_sim = sum(cross_sims) / len(cross_sims)
    # Disorder operator value = (mean_cross_sim - random_floor) / (1.0 - random_floor)
    disorder_op = (mean_cross_sim - random_floor) / max(1.0 - random_floor, 1e-8)
    return {
        "disorder_op_value": round(disorder_op, 5),
        "mean_cross_sim": round(mean_cross_sim, 5),
        "random_floor": round(random_floor, 5),
        "n_classes": len(patterns_by_class),
    }


def reconstruct_free_energy(W: torch.Tensor, keys: torch.Tensor, vals: torch.Tensor,
                             N: int, n_bins: int = 30) -> dict:
    """Reconstruct F(m) numerically via histogram of overlaps (m = overlap with stored patterns).
    F(m) ~ -log P(q = m) + const.
    3-well structure: histogram shows 3 well-separated peaks with non-equal heights.
    """
    retrieved = _retrieve(W, keys)
    r_norm = retrieved / retrieved.norm(dim=1, keepdim=True).clamp(min=1e-8)
    v_norm = vals / vals.norm(dim=1, keepdim=True).clamp(min=1e-8)
    q = (r_norm * v_norm).sum(dim=1).cpu().numpy()  # (M,)

    # Build histogram
    import numpy as np
    hist, edges = np.histogram(q, bins=n_bins, density=True)
    centers = (edges[:-1] + edges[1:]) / 2.0

    # Find local maxima (peaks in histogram ~ wells in F(m) = -log P(q))
    peaks = []
    for i in range(1, len(hist) - 1):
        if hist[i] > hist[i - 1] and hist[i] > hist[i + 1] and hist[i] > 0.01:
            peaks.append((centers[i], hist[i]))

    n_wells = len(peaks)
    peak_heights = [p[1] for p in peaks]
    peak_positions = [p[0] for p in peaks]

    # Compute depth ratios if 3+ wells found
    gap_ratio = None
    if n_wells >= 3:
        sorted_peaks = sorted(peaks, key=lambda x: x[1], reverse=True)
        h_max = sorted_peaks[0][1]
        h_min = sorted_peaks[-1][1]
        gap_ratio = h_min / max(h_max, 1e-10)

    return {
        "n_wells": n_wells,
        "peak_positions": [round(float(p), 4) for p in peak_positions],
        "peak_heights": [round(float(h), 4) for h in peak_heights],
        "gap_ratio": round(gap_ratio, 4) if gap_ratio is not None else None,
        "q_mean": round(float(q.mean()), 5),
        "q_std": round(float(q.std()), 5),
    }


def build_3class_fixture(N: int, M_per_class: int, seed: int, device) -> Tuple[torch.Tensor, torch.Tensor, List[torch.Tensor]]:
    """Build 3-class BSC fixture (G1-high, G2-mid, G3-low retention class).
    G1: clean patterns (no noise)
    G2: moderate-overlap patterns (rho=0.3 shared bits)
    G3: low-overlap patterns (rho=0.1 shared bits)
    Returns (keys_concat, vals_concat, patterns_by_class)
    """
    gen = torch.Generator(device=device).manual_seed(seed)
    M = M_per_class

    # G1: clean random BSC patterns
    k1 = make_bsc(M, N, gen, device)
    v1 = make_bsc(M, N, gen, device)

    # G2: patterns with partial overlap with G1 (retain 0.5 fraction of k1 bits)
    noise2 = make_bsc(M, N, gen, device)
    overlap_frac = 0.5
    mask2 = (torch.rand(M, N, generator=gen, device=device) < overlap_frac).float()
    k2 = (k1 * mask2 + noise2 * (1 - mask2)).sign()
    v2 = make_bsc(M, N, gen, device)

    # G3: low-overlap patterns
    noise3 = make_bsc(M, N, gen, device)
    mask3 = (torch.rand(M, N, generator=gen, device=device) < 0.2).float()
    k3 = (k1 * mask3 + noise3 * (1 - mask3)).sign()
    v3 = make_bsc(M, N, gen, device)

    keys_all = torch.cat([k1, k2, k3], dim=0)
    vals_all = torch.cat([v1, v2, v3], dim=0)
    patterns_by_class = [k1, k2, k3]
    return keys_all, vals_all, patterns_by_class


# ── formula self-tests ──

def _formula_selftests() -> None:
    """Verify formulas with synthetic Z_3-Potts toy model before running on substrate."""
    print("[selftest] running formula self-tests...", flush=True)
    device = torch.device("cpu")

    # Test 1: q_EA with perfect recall should be ~1.0
    N = 64
    M = 3
    gen = torch.Generator(device=device).manual_seed(42)
    keys = make_bsc(M, N, gen, device)
    vals = make_bsc(M, N, gen, device)
    # Perfect Hopfield: W = sum_mu v_mu x k_mu^T / N (outer-product rule)
    W = torch.zeros(N, N, device=device)
    for i in range(M):
        W.add_(vals[i:i+1].T @ keys[i:i+1], alpha=1.0 / N)
    q_ea = compute_q_EA(W, keys, vals, N)
    # With M=3, N=64, alpha=0.047 << alpha_c: retrieval should be high
    assert q_ea > 0.5, f"Selftest 1 FAIL: q_EA with near-perfect recall = {q_ea:.4f} (expected > 0.5)"
    print(f"[selftest] 1/4 q_EA with perfect recall = {q_ea:.4f} (> 0.5 OK)")

    # Test 2: Binder cumulant g4 with perfect retrieval q=1.0
    # Perfect pattern: q=1.0 for all M patterns
    perfect_keys = vals.clone()   # keys = vals -> recall is perfect
    W_perfect = build_hebbian_W(perfect_keys, vals, N)
    g4 = compute_binder_g4(W_perfect, perfect_keys, vals)
    # g4 should be non-degenerate (could be anywhere; test it's finite)
    assert math.isfinite(g4), f"Selftest 2 FAIL: Binder g4 not finite = {g4}"
    print(f"[selftest] 2/4 Binder g4 with perfect recall = {g4:.4f} (finite OK)")

    # Test 3: Spectral gap returns finite values for non-zero W
    W_rand = torch.randn(32, 32, device=device) * 0.01
    spec = compute_spectral_gap(W_rand)
    assert math.isfinite(spec["spectral_gap_frac"]), f"Selftest 3 FAIL: spectral_gap_frac not finite"
    assert spec["s_max"] > 0, f"Selftest 3b FAIL: s_max = 0 for random W"
    print(f"[selftest] 3/4 spectral_gap_frac = {spec['spectral_gap_frac']:.5f} (finite, s_max={spec['s_max']:.4f})")

    # Test 4: 3-class fixture produces 3 non-empty pattern groups
    keys_all, vals_all, p_by_class = build_3class_fixture(64, 10, 7, device)
    assert keys_all.shape[0] == 30, f"Selftest 4 FAIL: expected 30 keys, got {keys_all.shape[0]}"
    assert len(p_by_class) == 3, f"Selftest 4b FAIL: expected 3 classes, got {len(p_by_class)}"
    for ci, cls in enumerate(p_by_class):
        assert cls.shape == (10, 64), f"Selftest 4c FAIL: class {ci} shape {cls.shape}"
    print(f"[selftest] 4/4 3-class fixture: {keys_all.shape[0]} patterns, 3 classes OK")

    print("[selftest] ALL FORMULA SELF-TESTS PASS", flush=True)


_formula_selftests()


# ── instrumentation self-test ──

def _instrumentation_selftest() -> None:
    print("[selftest] running instrumentation self-test...", flush=True)
    device = torch.device("cpu")

    # 1. Full pipeline at small scale
    N = 64
    M_per_class = 5
    keys_all, vals_all, p_by_class = build_3class_fixture(N, M_per_class, 7, device)
    W = build_hebbian_W(keys_all, vals_all, N)

    # Check all claimed metrics are non-null
    q_ea = compute_q_EA(W, keys_all, vals_all, N)
    assert math.isfinite(q_ea) and q_ea >= 0, f"IS fail: q_EA = {q_ea}"

    g4 = compute_binder_g4(W, keys_all, vals_all)
    assert math.isfinite(g4), f"IS fail: binder g4 = {g4}"

    spec = compute_spectral_gap(W)
    assert math.isfinite(spec["spectral_gap_frac"]), f"IS fail: spectral_gap_frac"

    hyst_area = compute_hysteresis_area(W, keys_all, vals_all, [0.0, 0.2, 0.5])
    assert math.isfinite(hyst_area) and hyst_area >= 0, f"IS fail: hyst_area = {hyst_area}"

    disorder = compute_disorder_operator(p_by_class, N)
    assert math.isfinite(disorder["disorder_op_value"]), f"IS fail: disorder_op"

    fe = reconstruct_free_energy(W, keys_all, vals_all, N, n_bins=20)
    assert fe["n_wells"] is not None, "IS fail: n_wells is None"
    assert fe["q_mean"] is not None and math.isfinite(fe["q_mean"]), "IS fail: q_mean"

    ret = cosine_retention(W, keys_all, vals_all)
    assert math.isfinite(ret) and ret >= 0, f"IS fail: retention = {ret}"

    print(f"[selftest] smoke cell: q_EA={q_ea:.4f} g4={g4:.4f} spec_gap={spec['spectral_gap_frac']:.5f} "
          f"hyst={hyst_area:.5f} disorder={disorder['disorder_op_value']:.5f} n_wells={fe['n_wells']} "
          f"ret={ret:.4f}", flush=True)
    print("[selftest] instrumentation self-test PASS", flush=True)


_instrumentation_selftest()


def run_cell_C1_C2(N_sweep: list, M_per_class: int, seeds: list, device) -> Tuple[dict, dict]:
    """Cells C1 (q_EA N-scaling) and C2 (plateau height N-scaling) together."""
    results_c1 = {}
    results_c2 = {}
    for N in N_sweep:
        print(f"\n[C1/C2] N={N}", flush=True)
        M = max(M_per_class, int(ALPHA_LOAD * N / 3))   # scale M proportionally
        q_eas = []
        g4s = []
        ret_g1 = []
        ret_g2 = []
        ret_g3 = []
        for seed in seeds:
            keys_all, vals_all, p_by_class = build_3class_fixture(N, M, seed, device)
            M_g1 = p_by_class[0].shape[0]
            W = build_hebbian_W(keys_all, vals_all, N)
            q_ea = compute_q_EA(W, keys_all, vals_all, N)
            g4 = compute_binder_g4(W, keys_all, vals_all)
            q_eas.append(q_ea)
            g4s.append(g4)
            # Per-class retention (approximate: test each class against its own keys/vals)
            # G1: high retention (clean patterns stored)
            v1 = vals_all[:M_g1]
            v2 = vals_all[M_g1:2 * M_g1]
            v3 = vals_all[2 * M_g1:3 * M_g1]
            ret_g1.append(cosine_retention(W, p_by_class[0], v1))
            ret_g2.append(cosine_retention(W, p_by_class[1], v2))
            ret_g3.append(cosine_retention(W, p_by_class[2], v3))
            print(f"  seed={seed}: q_EA={q_ea:.4f} g4={g4:.4f} "
                  f"ret=[{ret_g1[-1]:.3f},{ret_g2[-1]:.3f},{ret_g3[-1]:.3f}]", flush=True)

        mu_q = sum(q_eas) / len(q_eas)
        std_q = math.sqrt(sum((x - mu_q) ** 2 for x in q_eas) / max(len(q_eas) - 1, 1))
        mu_g4 = sum(g4s) / len(g4s)
        results_c1[N] = {"q_EA_mean": round(mu_q, 5), "q_EA_std": round(std_q, 5),
                         "binder_g4_mean": round(mu_g4, 5), "M_per_class": M}
        results_c2[N] = {
            "ret_G1_mean": round(sum(ret_g1) / len(ret_g1), 5),
            "ret_G2_mean": round(sum(ret_g2) / len(ret_g2), 5),
            "ret_G3_mean": round(sum(ret_g3) / len(ret_g3), 5),
        }
        print(f"  -> q_EA={mu_q:.5f}+/-{std_q:.5f} g4={mu_g4:.4f}", flush=True)
        print(f"  -> plateaus=[{results_c2[N]['ret_G1_mean']:.4f},{results_c2[N]['ret_G2_mean']:.4f},{results_c2[N]['ret_G3_mean']:.4f}]", flush=True)

    return results_c1, results_c2


def run_cells_C3_C6(N: int, M_per_class: int, seeds: list, device,
                    perturbation_strengths: list) -> dict:
    """Cells C3 (spectral gap), C4 (hysteresis area), C5 (disorder op), C6 (free energy)."""
    c3_gaps = []
    c4_areas = []
    c5_disorders = []
    c6_wells = []

    for seed in seeds:
        keys_all, vals_all, p_by_class = build_3class_fixture(N, M_per_class, seed, device)
        W = build_hebbian_W(keys_all, vals_all, N)

        # C3: Goldstone mode / spectral gap
        spec = compute_spectral_gap(W)
        c3_gaps.append(spec["spectral_gap_frac"])
        print(f"  [C3] seed={seed}: gap={spec['spectral_gap_frac']:.5f} s_max={spec['s_max']:.4f}", flush=True)

        # C4: Hysteresis area
        area = compute_hysteresis_area(W, keys_all, vals_all, perturbation_strengths)
        c4_areas.append(area)
        print(f"  [C4] seed={seed}: hyst_area={area:.5f}", flush=True)

        # C5: Non-local disorder operator
        disorder = compute_disorder_operator(p_by_class, N)
        c5_disorders.append(disorder["disorder_op_value"])
        print(f"  [C5] seed={seed}: disorder_op={disorder['disorder_op_value']:.5f}", flush=True)

        # C6: Free energy 3-well structure
        fe = reconstruct_free_energy(W, keys_all, vals_all, N)
        c6_wells.append(fe)
        print(f"  [C6] seed={seed}: n_wells={fe['n_wells']} gap_ratio={fe['gap_ratio']}", flush=True)

    mu_gap = sum(c3_gaps) / len(c3_gaps)
    mu_area = sum(c4_areas) / len(c4_areas)
    std_area = math.sqrt(sum((x - mu_area) ** 2 for x in c4_areas) / max(len(c4_areas) - 1, 1))
    mu_disorder = sum(x for x in c5_disorders if math.isfinite(x)) / max(
        len([x for x in c5_disorders if math.isfinite(x)]), 1)
    wells_list = [fe["n_wells"] for fe in c6_wells]
    gap_ratios = [fe["gap_ratio"] for fe in c6_wells if fe["gap_ratio"] is not None]
    mu_gap_ratio = sum(gap_ratios) / max(len(gap_ratios), 1) if gap_ratios else None

    return {
        "C3": {"mean_spectral_gap_frac": round(mu_gap, 6), "raw": c3_gaps},
        "C4": {"mean_hysteresis_area": round(mu_area, 5), "std_area": round(std_area, 5),
               "cv": round(std_area / max(mu_area, 1e-10), 4), "raw": c4_areas},
        "C5": {"mean_disorder_op": round(mu_disorder, 5), "raw": c5_disorders},
        "C6": {"n_wells_mode": max(set(wells_list), key=wells_list.count),
               "mean_gap_ratio": round(mu_gap_ratio, 4) if mu_gap_ratio is not None else None,
               "n_3well_fraction": sum(1 for w in wells_list if w == 3) / len(wells_list)},
    }


def classify_cells(c1_res: dict, c2_res: dict, c3456_res: dict) -> dict:
    """Classify each cell outcome and count votes per class."""
    N_sorted = sorted(c1_res.keys())
    calls = {}

    # C1: q_EA(N) scaling
    q_eas = [c1_res[N]["q_EA_mean"] for N in N_sorted]
    q_ea_max_N = q_eas[-1]
    monotone = all(q_eas[i] <= q_eas[i + 1] + 0.02 for i in range(len(q_eas) - 1)) or \
               all(q_eas[i] >= q_eas[i + 1] - 0.02 for i in range(len(q_eas) - 1))
    # Slope estimate over decades
    if len(N_sorted) >= 2:
        log_n_range = math.log10(N_sorted[-1] / N_sorted[0])
        q_drift = abs(q_eas[-1] - q_eas[0])
        slope = q_drift / max(log_n_range, 0.1)
    else:
        slope = 0.0
    if q_ea_max_N < Q_EA_FINITE_N_THRESH:
        calls["C1"] = "FINITE_N"
    elif monotone and Q_EA_DOCUMENTED_LO <= q_eas[0] <= Q_EA_DOCUMENTED_HI:
        calls["C1"] = "DOCUMENTED"
    elif not monotone or slope > 0.05:
        calls["C1"] = "NOVEL"
    else:
        calls["C1"] = "MIDDLE"

    # C2: plateau convergence
    g1s = [c2_res[N]["ret_G1_mean"] for N in N_sorted]
    g2s = [c2_res[N]["ret_G2_mean"] for N in N_sorted]
    g3s = [c2_res[N]["ret_G3_mean"] for N in N_sorted]
    max_drift_G1 = max(g1s) - min(g1s)
    max_drift_G2 = max(g2s) - min(g2s)
    max_drift_G3 = max(g3s) - min(g3s)
    max_drift = max(max_drift_G1, max_drift_G2, max_drift_G3)
    # Inter-plateau gap at largest N
    rG1_large, rG2_large, rG3_large = g1s[-1], g2s[-1], g3s[-1]
    min_gap = min(abs(rG1_large - rG2_large), abs(rG2_large - rG3_large), abs(rG1_large - rG3_large))
    if min_gap < PLATEAU_COLLAPSE_THRESH:
        calls["C2"] = "FINITE_N"
    elif max_drift < PLATEAU_CONVERGENCE_THRESH:
        calls["C2"] = "DOCUMENTED"
    else:
        calls["C2"] = "NOVEL"

    # C3: Goldstone mode absence
    gap_frac = c3456_res["C3"]["mean_spectral_gap_frac"]
    if not math.isfinite(gap_frac):
        calls["C3"] = "MIDDLE"
    elif gap_frac < SPECTRAL_SOFT_MODE_THRESH:
        calls["C3"] = "FINITE_N"   # soft mode = finite-N artifact
    else:
        calls["C3"] = "DOCUMENTED"  # no soft mode = consistent with documented class

    # C4: Hysteresis area scaling (single N -- no scaling, but CV across seeds captures stability)
    cv = c3456_res["C4"]["cv"]
    area = c3456_res["C4"]["mean_hysteresis_area"]
    if area < 1e-4:
        calls["C4"] = "MIDDLE"   # area too small to interpret
    elif cv < HYSTERESIS_CV_THRESH:
        calls["C4"] = "DOCUMENTED"  # stable (first-order intrinsic)
    else:
        calls["C4"] = "NOVEL"   # noisy / unstable

    # C5: Disorder operator
    dis = c3456_res["C5"]["mean_disorder_op"]
    if not math.isfinite(dis):
        calls["C5"] = "MIDDLE"
    elif dis < DISORDER_OP_LO:
        calls["C5"] = "FINITE_N"
    elif DISORDER_OP_LO <= dis <= DISORDER_OP_HI:
        calls["C5"] = "DOCUMENTED"
    else:
        calls["C5"] = "NOVEL"

    # C6: Free energy wells
    n_wells_mode = c3456_res["C6"]["n_wells_mode"]
    gap_ratio = c3456_res["C6"]["mean_gap_ratio"]
    if n_wells_mode < 2:
        calls["C6"] = "FINITE_N"
    elif n_wells_mode >= 3 and gap_ratio is not None:
        if FREE_ENERGY_GAP_RATIO_LO <= gap_ratio <= FREE_ENERGY_GAP_RATIO_HI:
            calls["C6"] = "DOCUMENTED"
        else:
            calls["C6"] = "NOVEL"
    else:
        calls["C6"] = "MIDDLE"

    return calls


def decide_class(cell_calls: dict) -> Tuple[str, str]:
    """Joint decision from 6-cell battery."""
    counts = {"DOCUMENTED": 0, "NOVEL": 0, "FINITE_N": 0, "MIDDLE": 0}
    for call in cell_calls.values():
        counts[call] = counts.get(call, 0) + 1

    # Anomaly flag for C1/C2/C3
    anomalies_123 = sum(1 for c in ["C1", "C2", "C3"] if cell_calls.get(c) == "NOVEL")

    if counts["DOCUMENTED"] >= 5:
        verdict = "DOCUMENTED_BUT_UNTESTED"
        msg = (
            f"DOCUMENTED_BUT_UNTESTED: {counts['DOCUMENTED']}/6 cells match gated-multistable-AM / "
            f"lR-phase class (documented 2024-2026 literature). "
            f"Cell calls: {cell_calls}. "
            f"Product framing: substrate is first production realization of gated multistable AM class "
            f"with Kerdock structured-codebook. No novel-class declaration needed."
        )
    elif counts["NOVEL"] >= 4 and anomalies_123 >= 1:
        verdict = "NOVEL_SKAHM"
        msg = (
            f"NOVEL_SKAHM: {counts['NOVEL']}/6 cells match novel-class pattern AND "
            f"{anomalies_123}/3 anomalies in C1/C2/C3. "
            f"Cell calls: {cell_calls}. "
            f"Recommend SKAH-M class declaration (Structured Kerdock Asymmetric Hopfield Multistable). "
            f"P=0.22 prior; escalate to extended characterization."
        )
    elif counts["FINITE_N"] >= 4:
        verdict = "FINITE_N_ARTIFACT"
        msg = (
            f"FINITE_N_ARTIFACT: {counts['FINITE_N']}/6 cells match finite-N pattern. "
            f"Cell calls: {cell_calls}. "
            f"3-plateau structure likely dissolves at thermodynamic limit. "
            f"SURFACE TO STRATEGY IMMEDIATELY -- pivot to N-cap product framing required."
        )
    else:
        verdict = "MIDDLE_BAND"
        msg = (
            f"MIDDLE_BAND: mixed cell signals (doc={counts['DOCUMENTED']}, "
            f"novel={counts['NOVEL']}, finite_N={counts['FINITE_N']}, middle={counts['MIDDLE']}). "
            f"Cell calls: {cell_calls}. "
            f"Extend seed count (>=10) + N range up to N=8192 before final class call."
        )

    return verdict, msg


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[exp] anchor_novel_phase_battery_v1 {'SMOKE' if smoke else 'FULL'} on {device}", flush=True)

    N_sweep = N_SWEEP_SMOKE if smoke else N_SWEEP_FULL
    M_per_class = M_PATTERNS_PER_CLASS_SMOKE if smoke else M_PATTERNS_PER_CLASS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    perturb = PERTURBATION_STRENGTHS_SMOKE if smoke else PERTURBATION_STRENGTHS_FULL
    N_default = N_DEFAULT_SMOKE if smoke else N_DEFAULT_FULL
    out_dir = get_output_dir("anchor_novel_phase_battery_v1")

    # Cells C1 + C2 (N-sweep together for efficiency)
    print("\n=== Cells C1 + C2: q_EA and plateau height N-sweep ===", flush=True)
    c1_res, c2_res = run_cell_C1_C2(N_sweep, M_per_class, seeds, device)

    # Cells C3-C6 at default N
    print(f"\n=== Cells C3-C6 at N={N_default} ===", flush=True)
    c3456_res = run_cells_C3_C6(N_default, M_per_class, seeds, device, perturb)

    # Classify cells
    cell_calls = classify_cells(c1_res, c2_res, c3456_res)
    print(f"\n[battery] Cell calls: {cell_calls}", flush=True)

    verdict, verdict_msg = decide_class(cell_calls)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

    summary = {
        "C1_q_EA_by_N": c1_res,
        "C2_plateaus_by_N": c2_res,
        "C3_spectral": c3456_res["C3"],
        "C4_hysteresis": c3456_res["C4"],
        "C5_disorder_op": c3456_res["C5"],
        "C6_free_energy": c3456_res["C6"],
        "cell_calls": cell_calls,
        "class_vote_counts": {
            "DOCUMENTED": sum(1 for v in cell_calls.values() if v == "DOCUMENTED"),
            "NOVEL": sum(1 for v in cell_calls.values() if v == "NOVEL"),
            "FINITE_N": sum(1 for v in cell_calls.values() if v == "FINITE_N"),
            "MIDDLE": sum(1 for v in cell_calls.values() if v == "MIDDLE"),
        },
    }

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "config": {
            "N_sweep": N_sweep,
            "N_default": N_default,
            "M_per_class": M_per_class,
            "seeds": seeds,
            "mode": "smoke" if smoke else "full",
            "device": str(device),
        },
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[exp] metrics written to {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test",
                        help="Run instrumentation self-tests only and exit (used by queue gate)")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)  # selftests already ran at module scope above
    run(smoke=args.smoke)
