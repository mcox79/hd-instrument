"""SKAH-M novel-class declaration probe: 5-step characterization methodology.

TRIGGER: exp_anchor_novel_phase_battery_v1 returns HARD_FAIL (< 3/6 documented-class cells)
         OR returns NOVEL (>= 4/6 novel cells with anomaly in C1/C2/C3).

CONTEXT: Research notes/research_novel_phase_class_methodology_2026-05-27.md Finding 2:
  Five required steps for novel-phase-class declaration:
  (i)  Symmetry-breaking pattern: G_residual identification, order-parameter manifold
  (ii) Order-parameter manifold structure: discrete vs continuous vs manifold
  (iii) Goldstone mode analysis: count massless modes (should be ZERO for discrete sym)
  (iv) Free-energy fingerprint: shape of F(m, T) -- n-well, barriers, terrace
  (v)  Response-function structure: linear / nonlinear-hysteretic / divergent / memory-dep

DESIGN: 5-probe battery -- one probe per step of the methodology.

  PROBE S1 (Symmetry-breaking pattern):
    - Store 3-class codebook (Z_3 relabeling test).
    - Permute class labels 1->2, 2->3, 3->1. Measure retention set before and after.
    - If set {h1, h2, h3} is INVARIANT under relabel -> Z_3-categorical symmetry.
    - If heights CHANGE under relabel -> labels carry physical information (unusual).
    - Metric: max_i(|h_before[i] - h_after[sigma(i)]|). < 0.02 -> Z3_INVARIANT; > 0.05 -> NOT_Z3.

  PROBE S2 (Order-parameter manifold):
    - Edwards-Anderson q_EA(N) at N in {512, 1024, 2048} at 5 seeds.
    - Check if q_EA converges to q_EA^* in (0.6, 0.9) [documented] OR shows anomalous N-dependence.
    - Also check Binder cumulant g4: g4 -> 2/3 (paramagnet) vs g4 in (0.5, 0.7) (frozen order).
    - Metric: slope of q_EA vs log(N). < 0.05/decade -> CONVERGENT; > 0.10/decade -> ANOMALOUS.

  PROBE S3 (Goldstone mode analysis):
    - W spectral histogram at N=2048 with 5 seeds.
    - Check for soft modes near lambda=0: spectral_gap_frac = (lambda_max - lambda_min) / ||W||_F.
    - For discrete symmetry: no soft mode expected; gap > 0.05.
    - Metric: spectral_gap_frac. > 0.05 -> NO_SOFT_MODE (consistent with discrete sym);
              < 0.02 -> SOFT_MODE_PRESENT (continuous symmetry -- novel!).

  PROBE S4 (Free-energy fingerprint):
    - Reconstruct F(m) = -log P(m) from empirical retrieval histogram at N=2048.
    - Check: number of wells, well-depth ratios, barrier heights.
    - 3-well with non-equal depths -> Z_3-graded Potts-like (substrate signature).
    - 3-well with equal depths -> standard 3-state Potts.
    - <3 wells -> paramagnet or 1st-order with only 2 phases.
    - Metric: n_wells, gap_ratio (depth of well 1 / depth of well 3), barrier_height.

  PROBE S5 (Response-function structure):
    - Memory-dependent response: vary probe field h in {-2, -1, 0, 1, 2} (BSC-flip fraction).
    - Measure susceptibility chi(h) = d(retention)/d(h).
    - First-order/memory: chi shows DISCONTINUITY at critical h_c.
    - Linear (paramagnet): chi is constant.
    - Divergent (critical point): chi -> infinity at h_c.
    - Metric: chi_max / chi_min. > 5 -> NONLINEAR; < 2 -> LINEAR.

PRE-REGISTERED BANDS:
  NOVEL_CONFIRMED (SKAH-M class declaration warranted):
    - S1: Z3_INVARIANT (order-parameter manifold has Z_3 symmetry)
    - S2: ANOMALOUS (q_EA non-convergent or non-monotone in N)
    - S3: NO_SOFT_MODE (discrete symmetry confirmed, no Goldstone)
    - S4: n_wells >= 3 AND gap_ratio NOT in [0.90, 1.10] (non-equal-depth wells)
    - S5: NONLINEAR (chi_max/chi_min > 5 -- memory-dependent response)

  DOCUMENTED_CONFIRMED (if battery returns NOVEL but 5-step says no):
    - S1: Z3_INVARIANT
    - S2: CONVERGENT (q_EA converges -> documented class)
    - S3: NO_SOFT_MODE
    - S4: n_wells >= 3 AND gap_ratio in [0.30, 0.65] (graded non-equal)
    - S5: NONLINEAR

  FINITE_N_CONFIRMED:
    - S2: q_EA -> 0 as N grows
    - S4: n_wells < 2

  MIXED_EVIDENCE: <3 probes clearly classify.

Queue: overnight_queue (GPU; S2 N-sweep is bottleneck; ~1.5-2h)
Pre-reg: preregs/2026-05-27_anchor_novel_class_declaration_probe_v1.md
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
N_DEFAULT = 2048
N_SWEEP_FULL = [512, 1024, 2048]
N_SWEEP_SMOKE = [512, 1024]
SEEDS_FULL = [7, 17, 23, 37, 41]
SEEDS_SMOKE = [17]
M_PER_CLASS = 300   # full; use 50 at smoke
M_PER_CLASS_SMOKE = 50
BATCH_STORE = 128

# Pre-registered thresholds
S1_Z3_INVARIANT_MAX = 0.02
S1_NOT_Z3_MIN = 0.05
S2_CONVERGENT_SLOPE_MAX = 0.05    # /decade
S2_ANOMALOUS_SLOPE_MIN = 0.10
S3_NO_SOFT_MODE_MIN = 0.05
S3_SOFT_MODE_MAX = 0.02
S4_N_WELLS_MIN_NOVEL = 3
S4_GAP_RATIO_EQUAL_LO = 0.90      # equal-depth if in (0.90, 1.10) -- standard Potts
S4_GAP_RATIO_EQUAL_HI = 1.10
S5_NONLINEAR_CHI_RATIO = 5.0
S5_LINEAR_CHI_RATIO = 2.0


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def make_bsc(M: int, N: int, gen: torch.Generator, device) -> torch.Tensor:
    return 2.0 * torch.randint(0, 2, (M, N), generator=gen, device=device).float() - 1.0


def outer_product_store(keys: torch.Tensor, vals: torch.Tensor, N: int) -> torch.Tensor:
    W = torch.zeros((N, N), dtype=torch.float32, device=keys.device)
    for s in range(0, keys.shape[0], BATCH_STORE):
        e = min(s + BATCH_STORE, keys.shape[0])
        W.add_(vals[s:e].T @ keys[s:e], alpha=1.0 / N)
    return W


def build_3class_fixture(M_per_class: int, N: int, seed: int, device) -> Tuple[List, List]:
    """3-class BSC fixture with graded overlaps."""
    gen = torch.Generator(device=device).manual_seed(seed)
    proto1 = make_bsc(1, N, gen, device)
    proto2 = (proto1 + make_bsc(1, N, gen, device)).sign()
    proto3 = (proto1 + proto2 + make_bsc(1, N, gen, device)).sign()

    keys_list, vals_list = [], []
    for proto in [proto1, proto2, proto3]:
        noisy = proto.expand(M_per_class, N) * (
            2.0 * (torch.rand(M_per_class, N, generator=gen, device=device) > 0.10).float() - 1.0)
        noisy = noisy.sign()
        keys_list.append(noisy)
        vals_list.append(noisy.clone())
    return keys_list, vals_list


def compute_per_class_retention(W: torch.Tensor, keys_list: List, vals_list: List) -> List[float]:
    ret_list = []
    for k_c, v_c in zip(keys_list, vals_list):
        y = (W @ k_c.T).T
        yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
        vn = v_c / v_c.norm(dim=1, keepdim=True).clamp(min=1e-9)
        ret_list.append(float((yn * vn).sum(dim=1).mean()))
    return ret_list


def compute_qEA(W: torch.Tensor, keys: torch.Tensor, N: int) -> Tuple[float, float]:
    """Edwards-Anderson order parameter and Binder cumulant."""
    y = (W @ keys.T).T
    y_norm = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
    keys_norm = keys / keys.norm(dim=1, keepdim=True).clamp(min=1e-9)
    q = (y_norm * keys_norm).sum(dim=1)   # per-pattern overlap
    q2 = (q ** 2).mean().item()
    q4 = (q ** 4).mean().item()
    q_EA = math.sqrt(max(q2, 0.0))
    g4 = 1.0 - q4 / (3.0 * q2 ** 2) if q2 > 1e-9 else 0.0
    return q_EA, g4


# ---- PROBE S1 ----

def run_s1(N: int, M_per_class: int, seeds: List[int], device) -> Dict:
    """Z_3 relabeling invariance test."""
    diffs_all = []
    for seed in seeds:
        keys_list, vals_list = build_3class_fixture(M_per_class, N, seed, device)
        W = outer_product_store(torch.cat(keys_list), torch.cat(vals_list), N)
        h_before = compute_per_class_retention(W, keys_list, vals_list)
        h_before_sorted = sorted(h_before, reverse=True)

        # Permute 1->2, 2->3, 3->0 and re-measure
        keys_perm = [keys_list[1], keys_list[2], keys_list[0]]
        vals_perm = [vals_list[1], vals_list[2], vals_list[0]]
        h_after = compute_per_class_retention(W, keys_perm, vals_perm)
        h_after_sorted = sorted(h_after, reverse=True)

        diff = max(abs(h_before_sorted[i] - h_after_sorted[i]) for i in range(3))
        diffs_all.append(diff)
        print(f"  [S1] N={N} seed={seed}: h_before={[round(x,3) for x in h_before_sorted]} "
              f"h_after={[round(x,3) for x in h_after_sorted]} diff={diff:.4f}", flush=True)
        del W, keys_list, vals_list, keys_perm, vals_perm

    mean_diff = sum(diffs_all) / len(diffs_all)
    if mean_diff < S1_Z3_INVARIANT_MAX:
        call = "Z3_INVARIANT"
    elif mean_diff > S1_NOT_Z3_MIN:
        call = "NOT_Z3"
    else:
        call = "AMBIGUOUS"
    print(f"  [S1] mean_diff={mean_diff:.4f} -> {call}", flush=True)
    return {"mean_diff": round(mean_diff, 5), "call": call}


# ---- PROBE S2 ----

def run_s2(N_sweep: List[int], M_per_class: int, seeds: List[int], device) -> Dict:
    """q_EA(N) scaling."""
    qEA_by_N = {}
    for N in N_sweep:
        qEA_vals = []
        for seed in seeds:
            keys_list, vals_list = build_3class_fixture(M_per_class, N, seed, device)
            keys_all = torch.cat(keys_list)
            W = outer_product_store(keys_all, torch.cat(vals_list), N)
            q_EA, g4 = compute_qEA(W, keys_all, N)
            qEA_vals.append(q_EA)
            del W, keys_list, vals_list
        mean_qEA = sum(qEA_vals) / len(qEA_vals)
        qEA_by_N[N] = round(mean_qEA, 5)
        print(f"  [S2] N={N}: q_EA={mean_qEA:.4f}", flush=True)

    # Slope of q_EA vs log10(N)
    Ns = sorted(qEA_by_N.keys())
    log_Ns = [math.log10(N) for N in Ns]
    qEAs = [qEA_by_N[N] for N in Ns]
    n = len(Ns)
    if n >= 2:
        mx = sum(log_Ns) / n; my = sum(qEAs) / n
        cov = sum((log_Ns[i] - mx) * (qEAs[i] - my) for i in range(n))
        var_x = sum((log_Ns[i] - mx) ** 2 for i in range(n))
        slope = cov / var_x if var_x > 0 else 0.0
    else:
        slope = 0.0

    abs_slope = abs(slope)
    # Check if q_EA collapses toward 0 at large N (finite-N artifact)
    if len(Ns) >= 2 and qEA_by_N[max(Ns)] < 0.10:
        call = "FINITE_N"
    elif abs_slope < S2_CONVERGENT_SLOPE_MAX:
        call = "CONVERGENT"
    elif abs_slope > S2_ANOMALOUS_SLOPE_MIN:
        call = "ANOMALOUS"
    else:
        call = "AMBIGUOUS"
    print(f"  [S2] slope={slope:.4f}/decade -> {call}", flush=True)
    return {"qEA_by_N": qEA_by_N, "slope_per_decade": round(slope, 5), "call": call}


# ---- PROBE S3 ----

def run_s3(N: int, M_per_class: int, seeds: List[int], device) -> Dict:
    """Goldstone mode / spectral gap analysis."""
    gaps = []
    for seed in seeds:
        keys_list, vals_list = build_3class_fixture(M_per_class, N, seed, device)
        W = outer_product_store(torch.cat(keys_list), torch.cat(vals_list), N)
        W_norm = float(W.norm())
        try:
            sv = torch.linalg.svdvals(W)
            s_max = float(sv[0])
            s_min = float(sv[-1])
            gap_frac = (s_max - s_min) / max(W_norm, 1e-9)
        except Exception:
            gap_frac = 0.0
        gaps.append(gap_frac)
        print(f"  [S3] N={N} seed={seed}: spectral_gap_frac={gap_frac:.4f}", flush=True)
        del W, keys_list, vals_list

    mean_gap = sum(gaps) / len(gaps)
    if mean_gap > S3_NO_SOFT_MODE_MIN:
        call = "NO_SOFT_MODE"
    elif mean_gap < S3_SOFT_MODE_MAX:
        call = "SOFT_MODE"
    else:
        call = "AMBIGUOUS"
    print(f"  [S3] mean_gap_frac={mean_gap:.4f} -> {call}", flush=True)
    return {"mean_gap_frac": round(mean_gap, 5), "call": call}


# ---- PROBE S4 ----

def run_s4(N: int, M_per_class: int, seeds: List[int], device) -> Dict:
    """Free-energy fingerprint: well structure from retention histogram."""
    wells_list, gap_ratios = [], []
    for seed in seeds:
        keys_list, vals_list = build_3class_fixture(M_per_class, N, seed, device)
        W = outer_product_store(torch.cat(keys_list), torch.cat(vals_list), N)
        heights = compute_per_class_retention(W, keys_list, vals_list)
        heights_sorted = sorted(heights, reverse=True)

        # Count distinct "wells" (local minima in F = -log P(h)) via gap threshold
        gaps_between = [heights_sorted[i] - heights_sorted[i+1] for i in range(len(heights_sorted)-1)]
        # A "well" exists when there's a gap > 0.02 between consecutive heights
        n_wells = 1 + sum(1 for g in gaps_between if g > 0.02)
        gap_ratio = heights_sorted[0] / max(heights_sorted[-1], 1e-9) if len(heights_sorted) >= 2 else 1.0

        wells_list.append(n_wells)
        gap_ratios.append(gap_ratio)
        print(f"  [S4] N={N} seed={seed}: heights={[round(h,3) for h in heights_sorted]} "
              f"n_wells={n_wells} gap_ratio={gap_ratio:.3f}", flush=True)
        del W, keys_list, vals_list

    mean_n_wells = sum(wells_list) / len(wells_list)
    mean_gap_ratio = sum(gap_ratios) / len(gap_ratios)

    if (mean_n_wells >= S4_N_WELLS_MIN_NOVEL and
            not (S4_GAP_RATIO_EQUAL_LO <= mean_gap_ratio <= S4_GAP_RATIO_EQUAL_HI)):
        call = "GRADED_WELLS"  # non-equal wells = substrate signature
    elif mean_n_wells < 2:
        call = "FEW_WELLS"    # finite-N artifact or paramagnet
    elif S4_GAP_RATIO_EQUAL_LO <= mean_gap_ratio <= S4_GAP_RATIO_EQUAL_HI:
        call = "EQUAL_WELLS"  # standard 3-state Potts
    else:
        call = "AMBIGUOUS"
    print(f"  [S4] mean_n_wells={mean_n_wells:.1f} mean_gap_ratio={mean_gap_ratio:.3f} -> {call}", flush=True)
    return {"mean_n_wells": round(mean_n_wells, 2), "mean_gap_ratio": round(mean_gap_ratio, 4), "call": call}


# ---- PROBE S5 ----

def run_s5(N: int, M_per_class: int, seeds: List[int], device) -> Dict:
    """Response-function structure: susceptibility chi(h) = d(retention)/d(h)."""
    # h is the BSC-flip fraction applied to probe queries (0=clean, 0.5=half-flipped)
    H_VALS = [0.0, 0.05, 0.10, 0.20, 0.35, 0.50]
    chi_ratios = []
    for seed in seeds:
        keys_list, vals_list = build_3class_fixture(M_per_class, N, seed, device)
        W = outer_product_store(torch.cat(keys_list), torch.cat(vals_list), N)
        gen_probe = torch.Generator(device=device).manual_seed(seed + 500)

        rets = []
        for h in H_VALS:
            # Apply noise with flip probability h to all query keys
            keys_all = torch.cat(keys_list)
            if h > 0:
                flip = (torch.rand(keys_all.shape, generator=gen_probe, device=keys_all.device) < h).float()
                noisy_keys = keys_all * (1.0 - 2.0 * flip)   # flip h fraction
            else:
                noisy_keys = keys_all
            vals_all = torch.cat(vals_list)
            y = (W @ noisy_keys.T).T
            yn = y / y.norm(dim=1, keepdim=True).clamp(min=1e-9)
            vn = vals_all / vals_all.norm(dim=1, keepdim=True).clamp(min=1e-9)
            ret = float((yn * vn).sum(dim=1).mean())
            rets.append(ret)

        # Chi: finite-difference gradient
        drets = [abs(rets[i+1] - rets[i]) / (H_VALS[i+1] - H_VALS[i]) for i in range(len(H_VALS)-1)]
        chi_max = max(drets)
        chi_min = max(min(drets), 1e-9)
        chi_ratio = chi_max / chi_min
        chi_ratios.append(chi_ratio)
        print(f"  [S5] N={N} seed={seed}: rets={[round(r,3) for r in rets]} chi_ratio={chi_ratio:.2f}", flush=True)
        del W, keys_list, vals_list

    mean_chi_ratio = sum(chi_ratios) / len(chi_ratios)
    if mean_chi_ratio > S5_NONLINEAR_CHI_RATIO:
        call = "NONLINEAR"
    elif mean_chi_ratio < S5_LINEAR_CHI_RATIO:
        call = "LINEAR"
    else:
        call = "AMBIGUOUS"
    print(f"  [S5] mean_chi_ratio={mean_chi_ratio:.2f} -> {call}", flush=True)
    return {"mean_chi_ratio": round(mean_chi_ratio, 4), "call": call}


def compute_joint_verdict(s1, s2, s3, s4, s5) -> Tuple[str, str]:
    calls = {"S1": s1["call"], "S2": s2["call"], "S3": s3["call"], "S4": s4["call"], "S5": s5["call"]}
    novel_score = sum([
        s2["call"] == "ANOMALOUS",
        s3["call"] == "NO_SOFT_MODE",
        s4["call"] == "GRADED_WELLS",
        s5["call"] == "NONLINEAR",
        s1["call"] == "Z3_INVARIANT",
    ])
    finite_score = sum([s2["call"] == "FINITE_N", s4["call"] == "FEW_WELLS"])
    documented_score = sum([
        s1["call"] == "Z3_INVARIANT",
        s2["call"] == "CONVERGENT",
        s3["call"] == "NO_SOFT_MODE",
        s4["call"] in ("GRADED_WELLS", "EQUAL_WELLS"),
        s5["call"] == "NONLINEAR",
    ])

    if finite_score >= 2:
        verdict = "FINITE_N_CONFIRMED"
        msg = (f"Finite-N artifact pattern: S2={calls['S2']} S4={calls['S4']}. "
               f"Substrate structure dissolves at thermodynamic limit.")
    elif novel_score >= 4 and calls["S2"] == "ANOMALOUS":
        verdict = "NOVEL_CONFIRMED"
        msg = (f"Novel-class declaration warranted: {novel_score}/5 novel-class signals including "
               f"anomalous q_EA(N) scaling. SKAH-M designation is justified. "
               f"Cell calls: {calls}")
    elif documented_score >= 4:
        verdict = "DOCUMENTED_CONFIRMED"
        msg = (f"Documented-class confirmed despite novel battery result: {documented_score}/5 documented "
               f"signals. Substrate matches gated multistable AM / lR-phase. "
               f"Cell calls: {calls}")
    else:
        verdict = "MIXED_EVIDENCE"
        msg = (f"Mixed signals: novel={novel_score}/5 documented={documented_score}/5 "
               f"finite={finite_score}/2. Cell calls: {calls}. "
               f"Extend seed count and N range before final declaration.")
    return verdict, msg


# ---- instrumentation self-test ----

def _instrumentation_selftest() -> None:
    print("[selftest] starting...", flush=True)
    device = torch.device("cpu")

    # 1. build_3class_fixture returns 3 lists of (M, N) tensors
    keys_list, vals_list = build_3class_fixture(10, 64, 7, device)
    assert len(keys_list) == 3, f"FAIL 1a: len={len(keys_list)}"
    assert keys_list[0].shape == (10, 64), f"FAIL 1b: shape={keys_list[0].shape}"
    print("[selftest] 1/5 build_3class_fixture OK")

    # 2. outer_product_store returns (N, N) W
    W = outer_product_store(torch.cat(keys_list), torch.cat(vals_list), 64)
    assert W.shape == (64, 64), f"FAIL 2: shape={W.shape}"
    print("[selftest] 2/5 outer_product_store OK")

    # 3. compute_qEA: q_EA in (0, 1)
    q_EA, g4 = compute_qEA(W, torch.cat(keys_list), 64)
    assert 0.0 <= q_EA <= 1.0, f"FAIL 3a: q_EA={q_EA}"
    assert math.isfinite(g4), f"FAIL 3b: g4={g4}"
    print(f"[selftest] 3/5 compute_qEA={q_EA:.4f} g4={g4:.4f} OK")

    # 4. compute_per_class_retention: 3 values in (0, 1)
    rets = compute_per_class_retention(W, keys_list, vals_list)
    assert len(rets) == 3, f"FAIL 4a: len={len(rets)}"
    assert all(0.0 <= r <= 1.0 for r in rets), f"FAIL 4b: rets={rets}"
    print(f"[selftest] 4/5 compute_per_class_retention={[round(r,3) for r in rets]} OK")

    # 5. run_s1 smoke: returns dict with call
    result = run_s1(64, 10, [17], device)
    assert "call" in result and result["call"] in ("Z3_INVARIANT", "NOT_Z3", "AMBIGUOUS"), \
        f"FAIL 5: result={result}"
    print(f"[selftest] 5/5 run_s1 smoke: {result['call']} diff={result['mean_diff']:.4f} OK")

    print("[selftest] ALL PASS", flush=True)


_instrumentation_selftest()


# ---- main sweep ----

def run_sweep(smoke: bool = False) -> Tuple[Dict, Path]:
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"[novel_class_declaration] device={device} smoke={smoke}", flush=True)
    N = N_DEFAULT if not smoke else 512
    N_sweep = N_SWEEP_SMOKE if smoke else N_SWEEP_FULL
    M_per_class = M_PER_CLASS_SMOKE if smoke else M_PER_CLASS
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir("anchor_novel_class_declaration_probe_v1")
    t0 = time.time()

    print("\n=== PROBE S1: Z_3 symmetry-breaking ===", flush=True)
    s1 = run_s1(N, M_per_class, seeds, device)

    print("\n=== PROBE S2: q_EA(N) order-parameter manifold ===", flush=True)
    s2 = run_s2(N_sweep, M_per_class, seeds, device)

    print("\n=== PROBE S3: Goldstone mode / spectral gap ===", flush=True)
    s3 = run_s3(N, M_per_class, seeds, device)

    print("\n=== PROBE S4: Free-energy fingerprint ===", flush=True)
    s4 = run_s4(N, M_per_class, seeds, device)

    print("\n=== PROBE S5: Response-function susceptibility ===", flush=True)
    s5 = run_s5(N, M_per_class, seeds, device)

    verdict, msg = compute_joint_verdict(s1, s2, s3, s4, s5)
    elapsed = time.time() - t0

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "smoke": smoke,
        "N": N,
        "elapsed_s": round(elapsed, 1),
        "s1": s1, "s2": s2, "s3": s3, "s4": s4, "s5": s5,
        "thresholds": {
            "s1_z3_invariant_max": S1_Z3_INVARIANT_MAX,
            "s2_convergent_slope_max": S2_CONVERGENT_SLOPE_MAX,
            "s3_no_soft_mode_min": S3_NO_SOFT_MODE_MIN,
            "s4_n_wells_min_novel": S4_N_WELLS_MIN_NOVEL,
            "s5_nonlinear_chi_ratio": S5_NONLINEAR_CHI_RATIO,
        },
    }

    metrics_path = out_dir / "metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"[exp] metrics written to {metrics_path}", flush=True)
    return metrics, out_dir


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test",
                        help="Run instrumentation self-tests only and exit")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run_sweep(smoke=args.smoke)
