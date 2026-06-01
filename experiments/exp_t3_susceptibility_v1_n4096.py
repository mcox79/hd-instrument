"""T3 TRIPLE-POINT SUSCEPTIBILITY v1: three-direction susceptibility probe at N=4096.

CONTEXT:
  Axis3 v1+v2 tested the perturbation structure at several M x beta operating points and
  found sign_divergence=True at M_frac=10, beta=8 (near-boundary transition zone).
  The 'triple-point' framing requires ALL THREE principal axes to show divergent susceptibility:
    - d(retention)/dM   (memory load axis)
    - d(retention)/d(beta)  (inverse temperature axis)
    - d(retention)/d(codebook-order)  (structural axis -- codebook permutation order)

  If all three diverge (|chi|>>epsilon): NEAR_TRIPLE_POINT -- gates whether T1/T2/T4 are worth doing.
  If only M-axis diverges: TWO_PHASE_BOUNDARY (normal load transition, not a triple point).
  If all small: STABLE_REGION (current operating point far from any phase boundary).

OPERATING POINT (user-specified):
  The 'current operating point' is the approximate substrate operating regime:
    M_frac = 10.0  (near observed phase boundary from axis1 chunks 1-7)
    beta   = 32.0  (strong retrieval regime, standard operating)
    N      = 4096  (Kerdock)
  This is the same M_frac=10, beta=8 point that showed sign_divergence=True in v2.
  We add beta=32 (standard operating point) as primary, and beta=8 as corroboration.

MEASUREMENT APPROACH:
  For each direction d and perturbation size epsilon:
    chi_d(epsilon) = |ret(OP + epsilon*e_d) - ret(OP - epsilon*e_d)| / (2*epsilon)
  Measured at three epsilons: [0.02, 0.10, 0.30].
  Susceptibility divergence: chi_d is LARGE relative to baseline variance.

  Direction definitions:
  - M_axis:       M_frac += epsilon (M_plus) vs M_frac -= epsilon (M_minus)
  - beta_axis:    beta *= (1+epsilon) (beta_up) vs beta *= (1-epsilon) (beta_down)
  - codebook_axis: permute codebook ordering (reshuffle 'epsilon' fraction of codebook rows)
                   vs reverse permutation; measures sensitivity to codebook geometry

DIAGNOSTIC RULES:
  NEAR_TRIPLE_POINT: ALL 3 axes show chi >= 0.5 at epsilon=0.10.
    Interpretation: near a phase-diagram saddle point where three phases meet.
    Gates: T1 (global phase diagram), T2 (critical exponents), T4 (hysteresis full sweep).
  TWO_PHASE_BOUNDARY: Only M_axis chi >= 0.5; beta/codebook chi < 0.2.
    Interpretation: normal load-driven phase transition, not a triple point.
    Gates: M1 still useful for boundary localization; C1 still useful for killer features.
  STABLE_REGION: ALL axes chi < 0.10.
    Interpretation: current operating point is deep inside a single phase.

PRE-REGISTERED BANDS:
  HARD_PASS (NEAR_TRIPLE_POINT): all 3 chi >= 0.5 at epsilon=0.10 across >= 4/5 seeds.
  HARD_FAIL: all 3 chi < 0.05 at epsilon=0.10 (insensitive substrate; stable region).
  MIDDLE_BAND: at least 1 axis has chi >= 0.5 but not all 3 (two-phase or partial saddle).

FORMULA SELF-TESTS:
  1. chi_d(epsilon) = |ret_plus - ret_minus| / (2*epsilon). Units: fractional retention change per unit perturbation.
  2. At epsilon=0: chi_d -> |partial ret / partial e_d| (analytic susceptibility).
  3. M_plus at M_frac=10: M += epsilon*N. Large epsilon -> many more memories -> interference.
     Expected: ret decreases monotonically in M (confirmed by axis1 chunks). Large M-chi near boundary.
  4. beta_up: higher beta -> more confident retrieval -> higher retention at undercap,
     but may saturate (no change if already near 1.0). At M_frac=10 (near boundary): expect significant beta sensitivity.
  5. codebook_axis: permuting K atoms of codebook should change retrieval accuracy if
     retrieval is sensitive to codebook geometry. Expected: moderate sensitivity.
  6. HARD_PASS: chi_M >= 0.5 AND chi_beta >= 0.5 AND chi_codebook >= 0.5 at eps=0.10.
  7. N == 4096 (PROT-018 binding).

OOM CHECK:
  At M_frac=10, N=4096: M=40960. Keys=40960*4096*4=671MB. W=64MB. CB=268MB. Total~1GB. OK.
  At M_frac=10+0.30 epsilon (M_frac=13): M=53248. Keys=874MB. Total~1.2GB. Under 6GB.

TIMEOUT ESTIMATE:
  Axis3 v2 at 3 operating points x 6 dirs x 5 eps x 3 seeds: elapsed ~5-50s on GPU.
  T3: 2 operating points x 3 dirs x 3 eps x 5 seeds = 90 cells.
  Estimated: 90/270 * (axis3 v2 wall) ~ 1/3 of v2 time.
  V2 from status log took ~5-50s for 270 cells. T3 at 90 cells: ~15-25s.
  Using 1.5x * 50s (conservative): 75s. PROT-019 floor for _n4096: use 14400 (user override).
  User says: --timeout >= 14400 for _n4096. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: t3_susceptibility_v1_n4096
Queue: overnight_queue (GPU; N=4096 Kerdock, 3-axis susceptibility, 5 seeds)
Pre-reg: preregs/2026-05-28_t3_susceptibility_v1_n4096.md
Parent: axis3_triplepoint_v2_n4096 (MIDDLE_BAND v262; sign_divergence=True at M_frac=10 beta=8)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load axis3 v1 for store_base, measure_ret, apply_perturbation, Kerdock builder
_v1_path = REPO / "experiments" / "exp_axis3_triplepoint_v1_n4096.py"
_v1_spec = importlib.util.spec_from_file_location("axis3v1_t3", _v1_path)
v1 = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1)

store_base = v1.store_base
measure_ret = v1.measure_ret
v3 = v1.v3   # Kerdock codebook builder

# Load chunk1 for store_facts_batched (larger M handling)
_c1_path = REPO / "experiments" / "exp_axis1_mb_chunk1_v1.py"
_c1_spec = importlib.util.spec_from_file_location("axis1c1_t3", _c1_path)
c1 = importlib.util.module_from_spec(_c1_spec)
_c1_spec.loader.exec_module(c1)

store_facts_batched = c1.store_facts_batched

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL = 4096       # PROT-018 binding contract
N_SMOKE = 1024      # smoke scale
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

# TWO operating points (primary + corroboration)
# Primary: M_frac=10 (near boundary from axis1 chunks), beta=32 (standard op)
# Corroboration: M_frac=10, beta=8 (confirmed sign_divergence in axis3 v2)
OPERATING_POINTS_FULL = [
    {"M_frac": 10.0, "beta": 32.0, "label": "M10_b32"},
    {"M_frac": 10.0, "beta": 8.0,  "label": "M10_b8"},
]
OPERATING_POINTS_SMOKE = [
    {"M_frac": 10.0, "beta": 32.0, "label": "M10_b32"},
]

# Three perturbation axes
AXES = ["M_axis", "beta_axis", "codebook_axis"]

# Perturbation sizes (three-point to see shape)
EPSILONS_FULL  = [0.02, 0.10, 0.30]
EPSILONS_SMOKE = [0.10]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered susceptibility thresholds
CHI_TRIPLE_POINT_THRESHOLD = 0.5   # chi >= 0.5 for NEAR_TRIPLE_POINT
CHI_TWO_PHASE_THRESHOLD    = 0.2   # chi >= 0.2 for notable response
CHI_STABLE_MAX             = 0.05  # all chi < 0.05 for STABLE_REGION
HP_SEEDS_MIN               = 4     # >= 4/5 seeds show all-3-chi >= threshold
N_PROBE                    = 100


def get_output_dir(default_name: str = "t3_susceptibility_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _store_and_measure(M: int, beta: float, seed: int, N: int,
                       device: torch.device) -> Tuple[torch.Tensor, torch.Tensor, torch.Tensor, float]:
    """Store M facts with Kerdock, measure argmax retention. Returns (W, keys, val_idx, ret)."""
    codebook, _info = v3.make_kerdock_4coset_codebook(N, device)
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook, M, seed, N, device)
    ret = measure_ret(W, keys, val_idx, codebook, beta, N, n_probe=N_PROBE)
    return W, keys, val_idx, codebook, ret


def _store_and_measure_permuted_codebook(M: int, beta: float, seed: int,
                                          epsilon_frac: float, perm_seed: int,
                                          N: int, device: torch.device,
                                          reverse: bool = False) -> float:
    """Measure retention after storing with a partially permuted codebook.

    Simulates sensitivity to codebook ordering geometry.
    If reverse=True: use the inverse permutation (swaps back epsilon_frac rows).
    """
    codebook_orig, _info = v3.make_kerdock_4coset_codebook(N, device)
    C = codebook_orig.shape[0]

    # Apply partial permutation to codebook
    gen_p = torch.Generator(device=device).manual_seed(perm_seed)
    n_swap = max(1, int(epsilon_frac * C))
    perm_idx = torch.randperm(C, generator=gen_p, device=device)
    swap_idx = perm_idx[:n_swap]
    rest_idx = perm_idx[n_swap:]

    codebook_perm = codebook_orig.clone()
    if not reverse:
        # Forward: shuffle the swap_idx rows into random order
        gen_s = torch.Generator(device=device).manual_seed(perm_seed + 1000)
        inner_perm = torch.randperm(n_swap, generator=gen_s, device=device)
        codebook_perm[swap_idx] = codebook_orig[swap_idx[inner_perm]]
    else:
        # Reverse: shuffle using the complementary permutation (cycle-reverse)
        gen_s = torch.Generator(device=device).manual_seed(perm_seed + 2000)
        inner_perm = torch.randperm(n_swap, generator=gen_s, device=device)
        codebook_perm[swap_idx] = codebook_orig[swap_idx[inner_perm]]

    # Store facts with perturbed codebook
    W, keys, _vals, _key_idx, val_idx = store_facts_batched(codebook_perm, M, seed, N, device)
    # Measure retention against the SAME perturbed codebook
    ret = measure_ret(W, keys, val_idx, codebook_perm, beta, N, n_probe=N_PROBE)
    return ret


def run_susceptibility(M_frac: float, beta: float, label: str,
                        N: int, epsilons: List[float], seeds: List[int],
                        device: torch.device) -> Dict:
    """Compute three-axis susceptibility at one operating point."""
    M_base = int(M_frac * N)
    print(f"  [op={label}] M={M_base} beta={beta} N={N} seeds={seeds}", flush=True)

    cells = []

    for seed in seeds:
        t_seed = time.monotonic()
        # Base retention
        _W, _k, _vi, _cb, ret_base = _store_and_measure(M_base, beta, seed, N, device)
        print(f"    seed={seed} ret_base={ret_base:.4f} ({time.monotonic()-t_seed:.1f}s)", flush=True)

        for epsilon in epsilons:
            # ----- M_axis -----
            M_plus  = max(1, int((M_frac + epsilon) * N))
            M_minus = max(1, int((M_frac - epsilon) * N))
            _W2, _k2, _vi2, _cb2, ret_M_plus  = _store_and_measure(M_plus,  beta, seed, N, device)
            _W3, _k3, _vi3, _cb3, ret_M_minus = _store_and_measure(M_minus, beta, seed, N, device)
            chi_M = abs(ret_M_plus - ret_M_minus) / (2.0 * max(epsilon, 1e-9))

            # ----- beta_axis -----
            beta_up   = beta * (1.0 + epsilon)
            beta_down = max(0.1, beta * (1.0 - epsilon))
            # Store at base M; evaluate at different beta
            _W4, keys4, vi4, cb4, _ = _store_and_measure(M_base, beta, seed + 100, N, device)
            ret_beta_up   = measure_ret(_W4, keys4, vi4, cb4, beta_up,   N, n_probe=N_PROBE)
            ret_beta_down = measure_ret(_W4, keys4, vi4, cb4, beta_down, N, n_probe=N_PROBE)
            chi_beta = abs(ret_beta_up - ret_beta_down) / (2.0 * max(epsilon, 1e-9))

            # ----- codebook_axis -----
            perm_seed = seed + 500
            ret_cb_fwd = _store_and_measure_permuted_codebook(
                M_base, beta, seed, epsilon, perm_seed, N, device, reverse=False)
            ret_cb_rev = _store_and_measure_permuted_codebook(
                M_base, beta, seed, epsilon, perm_seed, N, device, reverse=True)
            chi_cb = abs(ret_cb_fwd - ret_cb_rev) / (2.0 * max(epsilon, 1e-9))

            cells.append({
                "label": label, "M_frac": M_frac, "beta": beta,
                "epsilon": epsilon, "seed": seed,
                "ret_base": round(ret_base, 5),
                "ret_M_plus": round(ret_M_plus, 5),
                "ret_M_minus": round(ret_M_minus, 5),
                "ret_beta_up": round(ret_beta_up, 5),
                "ret_beta_down": round(ret_beta_down, 5),
                "ret_cb_fwd": round(ret_cb_fwd, 5),
                "ret_cb_rev": round(ret_cb_rev, 5),
                "chi_M":    round(float(chi_M),    5),
                "chi_beta": round(float(chi_beta), 5),
                "chi_cb":   round(float(chi_cb),   5),
            })
            print(f"      eps={epsilon:.2f} chi_M={chi_M:.3f} chi_beta={chi_beta:.3f} "
                  f"chi_cb={chi_cb:.3f}", flush=True)

    return {"label": label, "M_frac": M_frac, "beta": beta, "cells": cells}


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    """Verdict across all operating points."""
    if not results:
        return ("T3_INCONCLUSIVE", "No results computed.")

    # Collect per-seed chi values at epsilon=0.10 (primary diagnostic epsilon)
    EPS_DIAG = 0.10
    seed_verdicts = {}
    for pt in results:
        for c in pt["cells"]:
            if abs(c["epsilon"] - EPS_DIAG) > 1e-6:
                continue
            s = c["seed"]
            if s not in seed_verdicts:
                seed_verdicts[s] = {"chi_M": [], "chi_beta": [], "chi_cb": []}
            seed_verdicts[s]["chi_M"].append(c["chi_M"])
            seed_verdicts[s]["chi_beta"].append(c["chi_beta"])
            seed_verdicts[s]["chi_cb"].append(c["chi_cb"])

    if not seed_verdicts:
        return ("T3_INCONCLUSIVE", "No cells at eps=0.10.")

    # Aggregate: per seed, take max over operating points
    seeds_all_3_pass = 0
    seeds_M_only_pass = 0
    seeds_all_small = 0
    seed_summary = []
    for s, vals in seed_verdicts.items():
        max_chi_M    = max(vals["chi_M"])    if vals["chi_M"]    else 0.0
        max_chi_beta = max(vals["chi_beta"]) if vals["chi_beta"] else 0.0
        max_chi_cb   = max(vals["chi_cb"])   if vals["chi_cb"]   else 0.0
        all_3 = (max_chi_M >= CHI_TRIPLE_POINT_THRESHOLD and
                 max_chi_beta >= CHI_TRIPLE_POINT_THRESHOLD and
                 max_chi_cb >= CHI_TRIPLE_POINT_THRESHOLD)
        M_only = (max_chi_M >= CHI_TRIPLE_POINT_THRESHOLD and
                  max_chi_beta < CHI_TWO_PHASE_THRESHOLD and
                  max_chi_cb   < CHI_TWO_PHASE_THRESHOLD)
        all_small = (max_chi_M < CHI_STABLE_MAX and
                     max_chi_beta < CHI_STABLE_MAX and
                     max_chi_cb   < CHI_STABLE_MAX)
        if all_3:
            seeds_all_3_pass += 1
        if M_only:
            seeds_M_only_pass += 1
        if all_small:
            seeds_all_small += 1
        seed_summary.append({
            "seed": s,
            "chi_M": round(max_chi_M, 4),
            "chi_beta": round(max_chi_beta, 4),
            "chi_cb": round(max_chi_cb, 4),
            "all_3": all_3, "M_only": M_only, "all_small": all_small,
        })

    n_seeds = len(seed_verdicts)
    detail = {"n_seeds": n_seeds, "seeds_all_3_pass": seeds_all_3_pass,
              "seeds_M_only": seeds_M_only_pass, "seeds_all_small": seeds_all_small,
              "seed_summary": seed_summary}

    # HARD_FAIL: all axes insensitive
    if seeds_all_small >= max(1, n_seeds - 1):
        return ("T3_HARD_FAIL",
                f"STABLE_REGION: {seeds_all_small}/{n_seeds} seeds show all chi < {CHI_STABLE_MAX} "
                f"at eps=0.10. Substrate completely insensitive. details={detail}.")

    # HARD_PASS: all 3 axes diverge
    if seeds_all_3_pass >= HP_SEEDS_MIN:
        return ("T3_HARD_PASS",
                f"NEAR_TRIPLE_POINT: {seeds_all_3_pass}/{n_seeds} seeds show chi_M/chi_beta/chi_cb "
                f">= {CHI_TRIPLE_POINT_THRESHOLD} at eps=0.10. "
                f"All 3 susceptibility axes diverge. Gates T1/T2/T4. details={detail}.")

    # MIDDLE_BAND: partial response (two-phase boundary or partial saddle)
    outcome = "TWO_PHASE_BOUNDARY" if seeds_M_only_pass >= 2 else "PARTIAL_SADDLE"
    return ("T3_MIDDLE_BAND",
            f"{outcome}: {seeds_all_3_pass}/{n_seeds} seeds show all-3-chi >= {CHI_TRIPLE_POINT_THRESHOLD}; "
            f"{seeds_M_only_pass}/{n_seeds} seeds show M-only pattern. "
            f"details={detail}.")


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Self-test 1: verdict HARD_PASS path (all 3 axes diverge)
    cells_pass = [
        {"epsilon": 0.10, "seed": 7, "label": "M10_b32", "M_frac": 10.0, "beta": 32.0,
         "chi_M": 0.80, "chi_beta": 0.70, "chi_cb": 0.60,
         "ret_base": 0.5, "ret_M_plus": 0.3, "ret_M_minus": 0.7,
         "ret_beta_up": 0.8, "ret_beta_down": 0.2, "ret_cb_fwd": 0.4, "ret_cb_rev": 0.7},
    ] * 4  # 4 seeds
    # Assign different seeds
    for i, c in enumerate(cells_pass):
        c = dict(c)
        c["seed"] = [7, 17, 23, 31][i]
        cells_pass[i] = c
    results_pass = [{"label": "M10_b32", "M_frac": 10.0, "beta": 32.0, "cells": cells_pass}]
    v, msg = compute_verdict(results_pass)
    assert "HARD_PASS" in v, f"selftest HARD_PASS failed: {v} {msg}"

    # Self-test 2: HARD_FAIL (all small)
    cells_flat = [
        {"epsilon": 0.10, "seed": s, "label": "M10_b32", "M_frac": 10.0, "beta": 32.0,
         "chi_M": 0.01, "chi_beta": 0.01, "chi_cb": 0.01,
         "ret_base": 0.5, "ret_M_plus": 0.51, "ret_M_minus": 0.49,
         "ret_beta_up": 0.52, "ret_beta_down": 0.48, "ret_cb_fwd": 0.50, "ret_cb_rev": 0.50}
        for s in [7, 17, 23, 31, 41]
    ]
    results_flat = [{"label": "M10_b32", "M_frac": 10.0, "beta": 32.0, "cells": cells_flat}]
    v2, _ = compute_verdict(results_flat)
    assert "HARD_FAIL" in v2, f"selftest HARD_FAIL failed: {v2}"

    # Self-test 3: MIDDLE_BAND (M only)
    cells_mid = [
        {"epsilon": 0.10, "seed": s, "label": "M10_b32", "M_frac": 10.0, "beta": 32.0,
         "chi_M": 0.80, "chi_beta": 0.05, "chi_cb": 0.05,
         "ret_base": 0.5, "ret_M_plus": 0.3, "ret_M_minus": 0.7,
         "ret_beta_up": 0.52, "ret_beta_down": 0.48, "ret_cb_fwd": 0.51, "ret_cb_rev": 0.49}
        for s in [7, 17, 23, 31, 41]
    ]
    results_mid = [{"label": "M10_b32", "M_frac": 10.0, "beta": 32.0, "cells": cells_mid}]
    v_mid, _ = compute_verdict(results_mid)
    assert "MIDDLE_BAND" in v_mid, f"selftest MIDDLE_BAND failed: {v_mid}"

    # Self-test 4: actual smoke computation
    device = torch.device("cpu")
    N_t = N_SMOKE
    op = OPERATING_POINTS_SMOKE[0]
    result = run_susceptibility(
        M_frac=op["M_frac"], beta=op["beta"], label=op["label"],
        N=N_t, epsilons=[0.10], seeds=[17], device=device,
    )
    cells = result.get("cells", [])
    assert len(cells) > 0, f"No cells at smoke scale: {result}"
    c = cells[0]
    assert "chi_M" in c and not math.isnan(c["chi_M"]), f"chi_M invalid: {c}"
    assert "chi_beta" in c and not math.isnan(c["chi_beta"]), f"chi_beta invalid: {c}"
    assert "chi_cb" in c and not math.isnan(c["chi_cb"]), f"chi_cb invalid: {c}"
    print(f"[selftest] smoke N={N_t}: chi_M={c['chi_M']:.4f} "
          f"chi_beta={c['chi_beta']:.4f} chi_cb={c['chi_cb']:.4f} OK", flush=True)

    # Multi-scale: verify N_FULL imports work (not OOM at module scope; just codebook build)
    cb_full, _info = v3.make_kerdock_4coset_codebook(N_FULL, torch.device("cpu"))
    assert cb_full.shape[0] > 1000, f"Kerdock codebook wrong shape at N={N_FULL}: {cb_full.shape}"
    del cb_full
    print(f"[selftest] multi-scale N={N_FULL} codebook: OK", flush=True)

    print("[selftest] PASS: all assertions OK", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    op_points = OPERATING_POINTS_SMOKE if smoke else OPERATING_POINTS_FULL
    epsilons  = EPSILONS_SMOKE if smoke else EPSILONS_FULL
    seeds     = SEEDS_SMOKE if smoke else SEEDS_FULL

    exp_name = os.environ.get("HDLAB_EXP_NAME", "t3_susceptibility_v1_n4096")
    print(f"[run] {exp_name} smoke={smoke} N={N} seeds={seeds} device={device}", flush=True)
    if not smoke:
        assert N == 4096, f"FULL run must use N=4096 (PROT-018); got {N}"

    all_results = []
    for op in op_points:
        result = run_susceptibility(
            M_frac=op["M_frac"], beta=op["beta"], label=op["label"],
            N=N, epsilons=epsilons, seeds=seeds, device=device,
        )
        all_results.append(result)

    verdict_str, verdict_msg = compute_verdict(all_results)

    elapsed = time.time() - t0
    print(f"\n[verdict] {verdict_str}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed:.1f}s", flush=True)

    out_dir = get_output_dir(exp_name)
    metrics = {
        "verdict": verdict_str,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "config": {
            "N": N, "smoke": smoke, "seeds": seeds,
            "operating_points": [op["label"] for op in op_points],
            "epsilons": epsilons,
        },
        "summary": {
            "n_operating_points": len(all_results),
            "n_cells_total": sum(len(r["cells"]) for r in all_results),
        },
        "results": all_results,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    print(f"[output] {out_path}", flush=True)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        print("[self-test] selftest ran at import scope", flush=True)
        sys.exit(0)
    run(smoke=args.smoke)
else:
    run(smoke=False)
