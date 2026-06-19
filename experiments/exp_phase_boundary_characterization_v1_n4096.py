"""PHASE BOUNDARY CHARACTERIZATION v1 at N=4096.

CONTEXT:
  Earlier work showed beta_c ~ 10 critical inverse-temp at M_frac=8.
  Fine-grained probe around beta_c=10 AND around M_c (estimated 8K-32K).
  Look for critical slowing (variance increase near transition).

SCIENTIFIC QUESTION:
  Near phase boundary, does the substrate show phase-transition signatures?
    - Sharper retention slope at boundary (>= 5x background)
    - Fluctuation peak (variance of retention across seeds peaks at boundary)
    - TCFT var_ratio anomaly (var(retention) / var(background) at boundary)

CELLS (14 total):
  - 7 betas around beta_c=10 at fixed M_frac=2: [9.0, 9.5, 9.8, 10.0, 10.2, 10.5, 11.0]
  - 7 M values bracketing M_c estimate at fixed beta=4: [8192, 12288, 16384,
    20480, 24576, 28672, 32768]

PRE-REGISTERED BANDS:
  HARD_PASS: max-slope-near-boundary / background-slope >= 5x in EITHER beta
    sweep OR M sweep.
  HARD_FAIL: max-slope-near-boundary / background-slope <= 1.5x in BOTH
    sweeps (no boundary effect detected).
  MIDDLE_BAND: otherwise.

FORMULA SELF-TESTS:
  1. N=4096 (PROT-018).
  2. 14 cells = 7 beta + 7 M.
  3. slope = |d_ret/d_param|; background = mean slope over endpoint pairs;
     near-boundary = max slope in center 3 pairs.

OOM CHECK: max M=32768 -> keys=537MB. W=64MB. CB=805MB. Total ~1.5GB. OK.

TIMEOUT ESTIMATE: 14 cells * 5 seeds * 3 metrics ~ 10s. 700s. Budget 21600s.

N-suffix: _n4096 (PROT-018).
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

from experiments._metric_battery import (  # noqa: E402
    make_substrate, metric_above_thresh_frac, metric_retention,
)

_ck_path = REPO / "experiments" / "_seed_checkpoint.py"
_ck_spec = importlib.util.spec_from_file_location("_seed_ckpt_phb", _ck_path)
_ck = importlib.util.module_from_spec(_ck_spec)
_ck_spec.loader.exec_module(_ck)
list_completed_keys = _ck.list_completed_keys
write_partial_key   = _ck.write_partial_key
load_partial_key    = _ck.load_partial_key


# PRODUCTION CONFIG -- PROT-018: _n4096 binds N
N = 4096        # PROT-018 production-N anchor
N_FULL  = N
N_SMOKE = 1024

# beta sweep around beta_c=10 at fixed M_frac=2
BETAS_BOUNDARY = [9.0, 9.5, 9.8, 10.0, 10.2, 10.5, 11.0]
# M sweep bracketing M_c estimate
M_BOUNDARY_FULL  = [8192, 12288, 16384, 20480, 24576, 28672, 32768]
M_BOUNDARY_SMOKE = [256, 384, 512, 640, 768, 896, 1024]
BETA_M_SWEEP = 4.0
M_FRAC_BETA_SWEEP = 2.0

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
N_PROBE = 100

HP_SLOPE_RATIO = 5.0
HF_SLOPE_RATIO = 1.5


def _slope_ratio(rets: List[float], xs: List[float]) -> Tuple[float, float, float]:
    """Compute max-center-slope / mean-endpoint-slope. Returns (ratio, max_c, mean_e)."""
    if len(rets) < 5:
        return (0.0, 0.0, 0.0)
    slopes = []
    for i in range(len(rets) - 1):
        d_ret = abs(rets[i + 1] - rets[i])
        d_x   = abs(xs[i + 1] - xs[i])
        slopes.append(d_ret / max(d_x, 1e-9))
    n = len(slopes)
    # center 3 vs endpoint pairs
    mid_start = max(0, n // 2 - 1)
    mid_end   = min(n, mid_start + 3)
    center = slopes[mid_start:mid_end]
    endpoints = [slopes[0], slopes[-1]]
    max_c = max(center) if center else 0.0
    mean_e = sum(endpoints) / len(endpoints) if endpoints else 0.0
    ratio = max_c / max(mean_e, 1e-9)
    return (ratio, max_c, mean_e)


def get_output_dir(default_name: str = "phase_boundary_characterization_v1_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def measure_cell(N_use: int, M: int, beta: float, seed: int,
                  device: torch.device) -> Dict:
    codebook, W, keys, values, key_idx, val_idx = make_substrate(N_use, M, seed, device)
    ret = metric_retention(W, codebook, key_idx, val_idx, N_use, beta, seed,
                            device, n_probe=N_PROBE)
    halu = metric_above_thresh_frac(W, codebook, key_idx, val_idx, N_use, beta, seed,
                                     device, n_probe=N_PROBE)
    del W, keys, values, codebook
    if device.type == 'cuda':
        torch.cuda.empty_cache()
    return {"M": M, "beta": beta, "seed": seed,
            "retention": ret["retention"],
            "above_thresh_frac": halu["above_thresh_frac"]}


def compute_verdict(beta_results: List[Dict], M_results: List[Dict]) -> Tuple[str, str]:
    # Aggregate beta sweep: mean retention per beta over seeds
    def aggregate(rows, key):
        by_x: Dict[float, List[float]] = {}
        for r in rows:
            by_x.setdefault(r[key], []).append(r["retention"])
        xs = sorted(by_x.keys())
        rets = [sum(by_x[x]) / len(by_x[x]) for x in xs]
        return xs, rets

    beta_xs, beta_rets = aggregate(beta_results, "beta")
    M_xs, M_rets       = aggregate(M_results, "M")
    if not beta_xs or not M_xs:
        return ("PHB_INCONCLUSIVE",
                f"No data. beta_pts={len(beta_xs)} M_pts={len(M_xs)}")

    br, br_max_c, br_mean_e = _slope_ratio(beta_rets, beta_xs)
    Mr, Mr_max_c, Mr_mean_e = _slope_ratio(M_rets, M_xs)
    detail = (f"beta_slope_ratio={br:.2f} (max_c={br_max_c:.4f} mean_e={br_mean_e:.4f}) "
              f"M_slope_ratio={Mr:.2f} (max_c={Mr_max_c:.4f} mean_e={Mr_mean_e:.4f}) "
              f"beta_rets={beta_rets} M_rets={M_rets}")
    if br >= HP_SLOPE_RATIO or Mr >= HP_SLOPE_RATIO:
        return ("PHB_HARD_PASS", f"BOUNDARY_DETECTED: " + detail)
    if br <= HF_SLOPE_RATIO and Mr <= HF_SLOPE_RATIO:
        return ("PHB_HARD_FAIL", f"NO_BOUNDARY: " + detail)
    return ("PHB_MIDDLE_BAND", f"PARTIAL_BOUNDARY: " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096
    assert len(BETAS_BOUNDARY) == 7
    assert len(M_BOUNDARY_FULL) == 7

    # slope-ratio formula self-test
    rets = [0.1, 0.12, 0.5, 0.55, 0.85, 0.87, 0.88]
    xs   = [1, 2, 3, 4, 5, 6, 7]
    r, mc, me = _slope_ratio(rets, xs)
    assert r > 1.0, f"expect slope ratio > 1 for sigmoid-like, got r={r}"
    # Flat case
    flat = [0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5]
    rf, _, _ = _slope_ratio(flat, xs)
    assert rf == 0.0, f"flat slope ratio expected 0 (max_c=0/mean_e=0=0/eps=0), got {rf}"

    # Verdict gates
    sharp = [{"beta": b, "retention": r, "seed": 17}
             for b, r in zip(BETAS_BOUNDARY, [0.1, 0.15, 0.2, 0.5, 0.8, 0.85, 0.9])]
    flat_M = [{"M": m, "retention": 0.5, "seed": 17}
               for m in M_BOUNDARY_FULL]
    v, _ = compute_verdict(sharp, flat_M); assert "HARD_PASS" in v, v
    # Both flat: HARD_FAIL
    flat_beta = [{"beta": b, "retention": 0.5, "seed": 17}
                 for b in BETAS_BOUNDARY]
    v, _ = compute_verdict(flat_beta, flat_M); assert "HARD_FAIL" in v, v

    device = torch.device("cpu")
    out = measure_cell(N_SMOKE, 256, 4.0, 17, device)
    assert out["retention"] is not None and 0.0 <= out["retention"] <= 1.0
    print(f"[selftest] phase_boundary_characterization_v1_n4096 PASS "
          f"smoke ret={out['retention']:.3f}", flush=True)


_instrumentation_selftest()


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    device_str = "cuda" if torch.cuda.is_available() else "cpu"
    device = torch.device(device_str)
    smoke = args.smoke
    N_cfg = N_SMOKE if smoke else N_FULL
    Ms = M_BOUNDARY_SMOKE if smoke else M_BOUNDARY_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL

    out_dir = get_output_dir()
    done = set(list_completed_keys(out_dir))
    t0 = time.time()
    print(f"[run] phase_boundary smoke={smoke} N={N_cfg} betas={BETAS_BOUNDARY} "
          f"Ms={Ms} seeds={seeds} done={len(done)} device={device_str}", flush=True)

    beta_results: List[Dict] = []
    M_results: List[Dict] = []

    # Beta sweep at M_frac=2
    M_at_beta = max(1, int(M_FRAC_BETA_SWEEP * N_cfg))
    for beta in BETAS_BOUNDARY:
        for seed in seeds:
            ck = f"beta{beta:g}_seed{seed}".replace(".", "p")
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    beta_results.append(body); continue
            try:
                out = measure_cell(N_cfg, M_at_beta, beta, seed, device)
                out["sweep"] = "beta"
                write_partial_key(out_dir, ck, out)
                beta_results.append(out)
                print(f"  beta={beta} seed={seed} ret={out['retention']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  beta={beta} seed={seed} FAILED: {e}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()

    # M sweep at beta=4
    for M in Ms:
        for seed in seeds:
            ck = f"M{M}_seed{seed}"
            if ck in done:
                body = load_partial_key(out_dir, ck)
                if body is not None:
                    M_results.append(body); continue
            try:
                out = measure_cell(N_cfg, M, BETA_M_SWEEP, seed, device)
                out["sweep"] = "M"
                write_partial_key(out_dir, ck, out)
                M_results.append(out)
                print(f"  M={M} seed={seed} ret={out['retention']:.3f} "
                      f"({time.time()-t0:.1f}s)", flush=True)
            except (RuntimeError, MemoryError) as e:
                print(f"  M={M} seed={seed} FAILED: {e}", flush=True)
                if device.type == 'cuda':
                    torch.cuda.empty_cache()

    verdict, vm = compute_verdict(beta_results, M_results)
    elapsed = round(time.time() - t0, 2)
    summary = {"anchor": "phase_boundary_characterization_v1_n4096", "N": N_cfg,
               "smoke": smoke, "betas": BETAS_BOUNDARY, "Ms": Ms, "seeds": seeds,
               "beta_results": beta_results, "M_results": M_results,
               "verdict": verdict, "verdict_msg": vm, "elapsed_s": elapsed}
    payload = {"verdict": verdict, "verdict_msg": vm,
               "elapsed_s": elapsed, "summary": summary}
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(payload, f, indent=2, default=str)
    print(f"\n[verdict] {verdict}\n[verdict_msg] {vm}\n[elapsed] {elapsed}s",
          flush=True)


if __name__ == "__main__":
    main()
