"""FREE PROBABILITY: Rank-1 Edit Perturbation smoke at N=4096.

SCIENTIFIC QUESTION (B1):
  Does K~sqrt(N) rank-1 edit budget produce detectable spectral drift
  (KS distance vs Marchenko-Pastur baseline) at N=4096?
  Free-probability Weyl bound predicts rank-1 edit budget K~sqrt(N)~64
  before spectral drift is detectable via KS test on singular value dist.

PRE-REGISTERED BANDS:
  HARD-PASS: sqrt(N) crossover detectable at K=64 +/- 1 rank-1 edit.
    Operationally: KS_distance(W_edit_K64, MP) > KS_distance(W_base, MP)
    by factor >= 1.5x (detectable lift) in >= 3/5 seeds.
  HARD-FAIL: No detectable lift at K=128 (2x sqrt(N)) in majority of seeds.
    KS ratio < 1.1x at K=128.
  MIDDLE: Lift detectable but K_crossover outside [32, 128] window.

DESIGN:
  N=4096, M=1024. Start with W_base (Hebbian sum of M rank-1 patterns).
  Apply K rank-1 edits (outer products of random unit vectors scaled by 1/N).
  Measure singular value distribution of W_edit via numpy.linalg.svd (truncated).
  Compute KS distance from Marchenko-Pastur density at alpha=M/N=0.25.
  K_sweep: [0, 8, 16, 32, 48, 64, 80, 96, 128] to map crossover.
  Seeds: [7, 17, 23, 31, 41].

MP density: p(x) = sqrt((lambda_max - x)(x - lambda_min)) / (2*pi*alpha*x)
  where lambda_min/max = (1 +/- sqrt(alpha))^2, alpha=M/N.

CALIBRATION NOTE: no prior empirical anchor for spectral-KS crossover.
  Bands widened per calibration-probe policy (theoretical +-50% band).

PROT-018: no _n suffix; production N=4096.
PROT-019: timeout >= 14400s (N>=4096); but CPU smoke expected ~120s.
PROT-020: CPU only (no CUDA).
PROT-021: M-tagged checkpoint keys.

Anchor: free_prob_rank1_edit_perturb_v1_n4096
Queue: remote_cpu_queue
Pre-reg: preregs/2026-06-01_free_prob_rank1_edit_perturb.md
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

import numpy as np
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_fp_rank1", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
write_partial_key = _ck.write_partial_key
load_partial_key  = _ck.load_partial_key
list_completed_keys = _ck.list_completed_keys

# PROT-018: production N=4096 (no _n suffix; documented in prereg)
N_FULL  = 4096
N_SMOKE = 512
M_FULL  = 1024
M_SMOKE = 128

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

K_SWEEP_FULL  = [0, 8, 16, 32, 48, 64, 80, 96, 128]
K_SWEEP_SMOKE = [0, 8, 32, 64]

# HARD-PASS threshold
HP_KS_LIFT_RATIO   = 1.5   # KS(K=64) / KS(K=0) >= 1.5 to declare crossover
HF_KS_LIFT_RATIO   = 1.1   # KS(K=128) / KS(K=0) < 1.1 = HARD_FAIL (no signal)


def mp_pdf(x: np.ndarray, alpha: float) -> np.ndarray:
    """Marchenko-Pastur density at given eigenvalues x with load alpha=M/N."""
    lam_min = (1.0 - math.sqrt(alpha)) ** 2
    lam_max = (1.0 + math.sqrt(alpha)) ** 2
    inside = np.clip((lam_max - x) * (x - lam_min), 0.0, None)
    denom = np.maximum(x, 1e-12) * 2.0 * math.pi * alpha
    return np.sqrt(inside) / denom


def ks_from_mp(W: np.ndarray, alpha: float) -> float:
    """KS distance: empirical W eigenvalue distribution vs MP CDF.

    Uses actual eigenvalues of symmetric W (via eigvalsh), which lie in
    [lambda_min, lambda_max] under Marchenko-Pastur for Hebbian W = X^T X / N.
    """
    eigs_raw = np.linalg.eigvalsh(W)
    # Use positive eigenvalues for comparison with MP support
    eigs = np.sort(eigs_raw[eigs_raw > 0])
    if len(eigs) == 0:
        return 1.0
    lam_min = (1.0 - math.sqrt(alpha)) ** 2
    lam_max = (1.0 + math.sqrt(alpha)) ** 2
    # Theoretical CDF via numerical integration on grid
    grid = np.linspace(max(lam_min * 0.5, 1e-6), lam_max * 1.5, 2000)
    pdf_vals = mp_pdf(grid, alpha)
    cdf_theory = np.cumsum(pdf_vals) * (grid[1] - grid[0])
    cdf_theory /= max(cdf_theory[-1], 1e-12)
    # Empirical CDF
    n = len(eigs)
    ecdf_y = np.arange(1, n + 1) / n
    # Interpolate theory CDF at empirical points
    theory_at_emp = np.interp(eigs, grid, cdf_theory)
    ks = float(np.max(np.abs(ecdf_y - theory_at_emp)))
    return ks


def measure_seed(N: int, M: int, K_sweep: List[int], seed: int) -> Dict:
    """Measure KS-from-MP at each K rank-1 edit budget.

    Hebbian W_base = X^T X / N where X is M x N bipolar {+-1}.
    Eigenvalues of W lie in [lambda_min, lambda_max] under MP at alpha=M/N.
    Rank-1 edits: W += u u^T where u is unit-norm random vector.
    """
    rng = np.random.default_rng(seed)
    # Build Hebbian W_base: W = X^T X / N, X is M x N bipolar
    patterns = rng.choice([-1.0, 1.0], size=(M, N)).astype(np.float32)
    W = (patterns.T @ patterns) / N  # N x N

    alpha = M / N
    ks_base = ks_from_mp(W, alpha)

    ks_per_k: Dict[int, float] = {0: ks_base}
    W_edit = W.copy()
    # Apply K rank-1 edits sequentially (unit vectors, scale ~ 1/sqrt(N) to match
    # individual pattern magnitude sqrt(M) contribution)
    edit_vectors = rng.standard_normal((max(K_sweep), N)).astype(np.float32)
    norms = np.linalg.norm(edit_vectors, axis=1, keepdims=True)
    edit_vectors /= np.maximum(norms, 1e-9)  # unit vectors

    applied = 0
    k_sorted = sorted(K_sweep)
    for k in k_sorted:
        if k == 0:
            continue
        while applied < k:
            u = edit_vectors[applied]
            W_edit += np.outer(u, u)
            applied += 1
        ks_per_k[k] = ks_from_mp(W_edit, alpha)

    # Key metric: lift at K=sqrt(N)
    k_sqrt = int(round(math.sqrt(N)))
    # Find nearest K in sweep to k_sqrt
    k_nearest = min(K_sweep, key=lambda k: abs(k - k_sqrt))
    ks_at_sqrt = ks_per_k.get(k_nearest, ks_per_k.get(64, ks_base))
    lift_at_sqrt = ks_at_sqrt / max(ks_base, 1e-9)

    k_2x = min(K_sweep, key=lambda k: abs(k - 2 * k_sqrt))
    ks_at_2x = ks_per_k.get(k_2x, ks_per_k.get(128, ks_base))
    lift_at_2x = ks_at_2x / max(ks_base, 1e-9)

    return {
        "seed": seed,
        "N": N,
        "M": M,
        "alpha": float(alpha),
        "k_sqrt_N": int(k_sqrt),
        "k_nearest_to_sqrt": int(k_nearest),
        "ks_base": float(ks_base),
        "ks_at_sqrt_n": float(ks_at_sqrt),
        "lift_at_sqrt_n": float(lift_at_sqrt),
        "lift_at_2x_sqrt_n": float(lift_at_2x),
        "ks_per_k": {str(k): float(v) for k, v in ks_per_k.items()},
        "ok": True,
    }


def compute_verdict(cells: List[Dict]) -> Tuple[str, str]:
    if not cells:
        return ("FP_RANK1_INCONCLUSIVE", "no cells")
    ok = [c for c in cells if c.get("ok")]
    if not ok:
        return ("FP_RANK1_INCONCLUSIVE", "all cells failed")

    lifts = [c["lift_at_sqrt_n"] for c in ok]
    mean_lift = sum(lifts) / len(lifts)
    n_pass_hp = sum(1 for l in lifts if l >= HP_KS_LIFT_RATIO)
    lifts_2x = [c["lift_at_2x_sqrt_n"] for c in ok]
    n_fail_2x = sum(1 for l in lifts_2x if l < HF_KS_LIFT_RATIO)

    detail = (
        f"N={ok[0]['N']} M={ok[0]['M']} alpha={ok[0]['alpha']:.3f} "
        f"k_sqrt={ok[0]['k_sqrt_N']} mean_lift_at_sqrt={mean_lift:.3f} "
        f"n_pass={n_pass_hp}/{len(ok)} ks_base_mean={sum(c['ks_base'] for c in ok)/len(ok):.4f}"
    )

    majority = len(ok) // 2 + 1
    if n_fail_2x >= majority:
        return ("FP_RANK1_HARD_FAIL",
                f"NO_CROSSOVER_SIGNAL: lift < {HF_KS_LIFT_RATIO} at K=2*sqrt(N) "
                f"in {n_fail_2x}/{len(ok)} seeds. " + detail)
    if n_pass_hp >= majority:
        return ("FP_RANK1_HARD_PASS",
                f"SQRT_N_CROSSOVER_DETECTABLE lift>={HP_KS_LIFT_RATIO} "
                f"in {n_pass_hp}/{len(ok)} seeds. " + detail)
    return ("FP_RANK1_MIDDLE_BAND",
            f"PARTIAL lift={mean_lift:.3f} n_pass={n_pass_hp}/{len(ok)}. " + detail)


def get_output_dir(default_name: str = "free_prob_rank1_edit_perturb_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at smoke scale."""
    # Formula self-test 1: MP density integrates to ~1 at alpha=0.25
    alpha_test = 0.25
    lam_min = (1 - math.sqrt(alpha_test)) ** 2
    lam_max = (1 + math.sqrt(alpha_test)) ** 2
    grid = np.linspace(lam_min * 0.8, lam_max * 1.2, 5000)
    pdf = mp_pdf(grid, alpha_test)
    integral = float(np.trapezoid(pdf, grid) if hasattr(np, 'trapezoid') else np.trapz(pdf, grid))
    assert 0.85 < integral < 1.15, f"MP density integral={integral:.4f} far from 1.0"
    print(f"[selftest] formula-1 MP density integral={integral:.4f} (expected ~1.0) PASS",
          flush=True)

    # Formula self-test 2: ks_from_mp returns float in [0,1] on small W
    rng2 = np.random.default_rng(42)
    N_t, M_t = 64, 16
    pats_t = rng2.choice([-1.0, 1.0], size=(M_t, N_t)).astype(np.float32)
    W_t = (pats_t.T @ pats_t) / N_t
    ks = ks_from_mp(W_t, M_t / N_t)
    assert 0.0 <= ks <= 1.0, f"ks_from_mp out of range: {ks}"
    print(f"[selftest] formula-2 ks_from_mp={ks:.4f} in [0,1] PASS", flush=True)

    # Formula self-test 3: lift metric is non-null after 1 seed at small N
    out = measure_seed(256, 64, [0, 8, 16], 42)
    assert out["ok"], f"measure_seed failed: {out}"
    assert out["ks_base"] >= 0, f"ks_base<0 sentinel"
    assert out["lift_at_sqrt_n"] > 0, f"lift_at_sqrt_n=0 sentinel"
    assert out["lift_at_2x_sqrt_n"] > 0, f"lift_at_2x_sqrt_n=0 sentinel"
    assert out["k_sqrt_N"] > 0, f"k_sqrt_N=0"
    assert len(out["ks_per_k"]) >= 2, f"ks_per_k has < 2 entries"
    # Filter check: ks_per_k has at least one entry besides k=0
    assert any(int(k) > 0 for k in out["ks_per_k"]), "no non-zero K entries"
    print(f"[selftest] formula-3 live smoke N=256 M=64 "
          f"ks_base={out['ks_base']:.4f} lift={out['lift_at_sqrt_n']:.4f} PASS",
          flush=True)

    # Formula self-test 4: verdict gates work
    fake_hp = [{"ok": True, "lift_at_sqrt_n": 2.0, "lift_at_2x_sqrt_n": 2.5,
                "ks_base": 0.1, "N": 4096, "M": 1024, "alpha": 0.25,
                "k_sqrt_N": 64, "k_nearest_to_sqrt": 64,
                "ks_at_sqrt_n": 0.2, "ks_per_k": {"0": 0.1, "64": 0.2}}
               for _ in range(5)]
    v, msg = compute_verdict(fake_hp)
    assert "HARD_PASS" in v, f"HP gate failed: {v}"
    print(f"[selftest] formula-4 HP gate PASS: {v}", flush=True)

    fake_hf = [{"ok": True, "lift_at_sqrt_n": 1.0, "lift_at_2x_sqrt_n": 1.05,
                "ks_base": 0.1, "N": 4096, "M": 1024, "alpha": 0.25,
                "k_sqrt_N": 64, "k_nearest_to_sqrt": 64,
                "ks_at_sqrt_n": 0.105, "ks_per_k": {"0": 0.1, "128": 0.105}}
               for _ in range(5)]
    v, msg = compute_verdict(fake_hf)
    assert "HARD_FAIL" in v, f"HF gate failed: {v}"
    print(f"[selftest] formula-4 HF gate PASS: {v}", flush=True)

    print("[selftest] free_prob_rank1_edit_perturb_v1_n4096 ALL PASS", flush=True)


_instrumentation_selftest()


def main() -> None:
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)

    smoke  = args.smoke
    N_cfg  = N_SMOKE if smoke else N_FULL
    M_cfg  = M_SMOKE if smoke else M_FULL
    seeds  = SEEDS_SMOKE if smoke else SEEDS_FULL
    ksweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL

    out_dir = get_output_dir()
    run_config = {"N": N_cfg, "M": M_cfg, "run_mode": "smoke" if smoke else "full"}
    done = set(list_completed_keys(out_dir, run_config=run_config))

    t0 = time.time()
    print(f"[run] free_prob_rank1_edit_perturb_v1 smoke={smoke} "
          f"N={N_cfg} M={M_cfg} K_sweep={ksweep} seeds={seeds} "
          f"done={len(done)}", flush=True)

    cells: List[Dict] = []
    for seed in seeds:
        ck = f"M{M_cfg}_seed{seed}"
        if ck in done:
            body = load_partial_key(out_dir, ck)
            if body is not None:
                cells.append(body)
                print(f"  [resume] seed={seed} loaded from checkpoint", flush=True)
                continue
        try:
            cell = measure_seed(N_cfg, M_cfg, ksweep, seed)
            cell["run_mode"] = "smoke" if smoke else "full"
            write_partial_key(out_dir, ck, cell)
            cells.append(cell)
            print(f"  seed={seed} ok={cell.get('ok')} "
                  f"ks_base={cell.get('ks_base', 'n/a'):.4f} "
                  f"lift_at_sqrt={cell.get('lift_at_sqrt_n', 'n/a'):.4f} "
                  f"({time.time()-t0:.1f}s)", flush=True)
        except Exception as e:
            print(f"  seed={seed} FAILED: {e}", flush=True)

    verdict, vm = compute_verdict(cells)
    elapsed = round(time.time() - t0, 2)
    summary = {
        "anchor": "free_prob_rank1_edit_perturb_v1_n4096",
        "N": N_cfg, "M": M_cfg, "smoke": smoke,
        "K_sweep": ksweep, "seeds": seeds,
        "cells": cells, "verdict": verdict, "verdict_msg": vm,
        "elapsed_s": elapsed,
    }
    out_path = out_dir / "metrics.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
