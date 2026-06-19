"""TCFT M-sweep v4: N=4096 CPU counterpart of v3 (N=8192 5-seed).

CONTEXT:
  tcft_m_sweep_v3_n8192_5seed (completed on remote_cpu_queue): 5-seed N=8192 HARD_PASS.
    tcft_variance_ratio < 0.10 at M>=512, spearman=-1.000 both runs.
  v4 (THIS): N=4096 CPU counterpart for N-scaling validation.
  Does tcft_variance_ratio < 0.10 threshold hold at N=4096 across 5 seeds?
  Is the 1/sqrt(M) trend robust at N=4096?

SCIENTIFIC QUESTION:
  At N=4096 (cheaper, CPU-friendly), does TCFT achieve tcft_variance_ratio < 0.10 at M>=512?
  Does N-scaling: N=4096 vs N=8192 show consistent tcft_variance_ratio trend?

PRE-REGISTERED BANDS:
  Prior: v3 N=8192 5-seed HARD_PASS (tcft_variance_ratio < 0.05 at M>=512).
  N=4096 is cheaper per cell: (4096/8192)^1 = 0.5x wall time.
  Expected: tcft_variance_ratio slightly higher at N=4096 vs N=8192 (fewer dimensions).
  Bands NOT widened (prior anchor exists; this is N-scaling validation, not calibration).

  HARD_PASS: >= 4/5 seeds have tcft_variance_ratio < 0.10 at ALL M >= 256,
    AND Spearman r(M, mean_vr_per_M) < -0.5 (1/sqrt(M) trend holds).
  HARD_FAIL: >= 2/5 seeds have tcft_variance_ratio >= 0.10 at M=512
    (contradicts v3 N=8192 baseline; N-scaling fails).
  MIDDLE_BAND: exactly 3/5 seeds pass or tcft_variance_ratio only passes at M>=1024.

FORMULA SELF-TESTS:
  1. N == 4096 (PROT-018 binding).
  2. M values: [64, 128, 256, 512, 1024]. tcft_variance_ratio at M_large expected < 0.10.
  3. HARD_PASS gate: 4/5 seeds pass all M>=256 cells with tcft_variance_ratio < 0.10.
  4. HARD_FAIL gate: 2/5 seeds have tcft_variance_ratio >= 0.10 at M=512.
  5. 1/sqrt(M) ratio: vr(M=64)/vr(M=256) ~ sqrt(256/64) = 2. Test: 0.20/0.10 = 2.0.

OOM CHECK:
  N=4096, M=1024: W not stored (streaming). Codebook: 64MB. Peak ~128MB. OK.

TIMEOUT ESTIMATE:
  v3 N=8192 5-seed: elapsed ~13000s (from pre-reg, 2.4h nominal).
  N=4096 vs N=8192: scale (4096/8192)^1.5 = 0.354x per cell (memory ops).
  v4: same seeds (5), same M values (5). 5 seeds * 5 M = 25 cells.
  Per-cell at N=4096 vs per-cell at N=8192: v3 total/25_cells = ~520s/cell at N=8192.
  N=4096 cell: 520 * 0.354 = 184s.
  Total: 25 * 184 = 4600s. Safety 1.5x: 6900s. Round up: 7200s.
  Note: exceeds 2h flag. Justified as load-bearing 5-seed N-scaling check.
  Under 14400s cap.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: tcft_m_sweep_v4_n4096
Queue: remote_cpu_queue (CPU; N=4096 5-seed M-sweep ~2h)
Pre-reg: preregs/2026-05-29_tcft_m_sweep_v4_n4096.md
Parent: tcft_m_sweep_v3_n8192_5seed (completed HARD_PASS)
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

# Load v3 for shared M-sweep infrastructure
_v3_path = REPO / "experiments" / "exp_tcft_m_sweep_v3_n8192_5seed.py"
_v3_spec = importlib.util.spec_from_file_location("tcft_v3_v4", _v3_path)
_tcft_v3 = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(_tcft_v3)

# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_VALUES_FULL  = [64, 128, 256, 512, 1024]
M_VALUES_SMOKE = [64, 256]   # 2 M values for fast smoke

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (same as v3)
HP_VR_MAX   = 0.10   # tcft_variance_ratio < 0.10 = HARD_PASS
HF_VR_SEEDS = 2      # >= 2/5 seeds fail at M=512 = HARD_FAIL
HP_SEEDS    = 4      # >= 4/5 seeds pass all M>=256
HP_SPEARMAN = -0.5   # Spearman r < -0.5 = 1/sqrt(M) trend


def get_output_dir(default_name: str = "tcft_m_sweep_v4_n4096") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def run_one_cell(N: int, M: int, seed: int) -> Dict:
    """Run TCFT tcft_variance_ratio at (N, M, seed) using v3 infrastructure."""
    return _tcft_v3.run_one_cell(N=N, M=M, seed=seed)


def spearman_rho(xs: List[float], ys: List[float]) -> float:
    """Spearman rank correlation."""
    import numpy as np
    n = len(xs)
    if n < 2:
        return 0.0
    rx = float('nan')
    try:
        rx_arr = sorted(range(n), key=lambda i: xs[i])
        ry_arr = sorted(range(n), key=lambda i: ys[i])
        ranks_x = [0.0] * n
        ranks_y = [0.0] * n
        for rank, idx in enumerate(rx_arr):
            ranks_x[idx] = float(rank)
        for rank, idx in enumerate(ry_arr):
            ranks_y[idx] = float(rank)
        mr_x = sum(ranks_x) / n
        mr_y = sum(ranks_y) / n
        num = sum((ranks_x[i] - mr_x) * (ranks_y[i] - mr_y) for i in range(n))
        den_x = sum((r - mr_x)**2 for r in ranks_x) ** 0.5
        den_y = sum((r - mr_y)**2 for r in ranks_y) ** 0.5
        if den_x < 1e-12 or den_y < 1e-12:
            return 0.0
        return num / (den_x * den_y)
    except Exception:
        return 0.0


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("TCFT_V4_INCONCLUSIVE", "No per_seed data.")

    # HARD_PASS check: >= 4/5 seeds pass tcft_variance_ratio < HP_VR_MAX at all M >= 256
    seeds_pass = 0
    seeds_fail_512 = 0
    per_seed_stats = {}

    for seed_k, m_results in per_seed.items():
        m_vals_tested = sorted(m_results.keys(), key=int)
        fails_at_m256 = sum(1 for m in m_vals_tested
                            if int(m) >= 256 and m_results[m].get("tcft_variance_ratio", 1.0) >= HP_VR_MAX)
        passes_all = (fails_at_m256 == 0)
        fails_512 = any(m_results[m].get("tcft_variance_ratio", 0.0) >= HP_VR_MAX
                        for m in m_vals_tested if int(m) == 512)

        if passes_all:
            seeds_pass += 1
        if fails_512:
            seeds_fail_512 += 1
        per_seed_stats[seed_k] = {"passes_all": passes_all, "fails_512": fails_512}

    n_seeds = len(per_seed)
    mean_vr_by_M: Dict[int, List[float]] = {}
    for seed_k, m_results in per_seed.items():
        for m_str, rd in m_results.items():
            M_int = int(m_str)
            if M_int not in mean_vr_by_M:
                mean_vr_by_M[M_int] = []
            mean_vr_by_M[M_int].append(rd.get("tcft_variance_ratio", 0.0))

    M_sorted = sorted(mean_vr_by_M.keys())
    mean_vr_list = [sum(mean_vr_by_M[M]) / len(mean_vr_by_M[M]) for M in M_sorted]
    rho = spearman_rho(M_sorted, mean_vr_list)

    N = summary.get("N", N_FULL)
    detail = (f"seeds_pass={seeds_pass}/{n_seeds} seeds_fail_512={seeds_fail_512} "
              f"spearman_rho={rho:.3f} HP_seeds={HP_SEEDS} HP_vr={HP_VR_MAX} "
              f"M_sorted={M_sorted} mean_vr={[round(v,4) for v in mean_vr_list]} N={N}")

    if seeds_fail_512 >= HF_VR_SEEDS:
        return ("TCFT_V4_HARD_FAIL",
                f"VAR_RATIO_FAILS at M=512 for {seeds_fail_512}/{n_seeds} seeds. " + detail)

    if seeds_pass >= HP_SEEDS and rho < HP_SPEARMAN:
        return ("TCFT_V4_HARD_PASS",
                f"VAR_RATIO < 0.10 at N=4096: {seeds_pass}/{n_seeds} seeds. " + detail)

    return ("TCFT_V4_MIDDLE_BAND",
            f"PARTIAL: {seeds_pass}/{n_seeds} seeds pass. " + detail)


def _instrumentation_selftest() -> None:
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Import chain
    assert _tcft_v3 is not None, "tcft_v3 import failed"
    assert hasattr(_tcft_v3, "run_one_cell"), "v3 missing run_one_cell"

    # Formula tests
    # 1/sqrt(M) ratio test
    vr_64 = 1.0 / math.sqrt(64)    # ~0.125
    vr_256 = 1.0 / math.sqrt(256)  # ~0.0625
    ratio = vr_64 / vr_256
    assert abs(ratio - math.sqrt(256/64)) < 0.01, f"1/sqrt(M) ratio: {ratio}"

    # Spearman test
    rho_dec = spearman_rho([64, 128, 256, 512, 1024], [0.20, 0.15, 0.10, 0.07, 0.05])
    assert rho_dec < -0.9, f"Expected rho < -0.9, got {rho_dec:.3f}"

    # Verdict tests
    # Use a monotone-decreasing tcft_variance_ratio; M>=256 all < 0.10 (strictly less)
    per_seed_hp = {
        str(s): {str(M): {"tcft_variance_ratio": vr}
                 for M, vr in zip([64, 128, 256, 512, 1024],
                                   [0.20, 0.14, 0.09, 0.07, 0.05])}
        for s in [7, 17, 23, 31, 41]
    }
    v, msg = compute_verdict({"per_seed": per_seed_hp, "N": N_FULL})
    assert "HARD_PASS" in v, f"Expected HP: {v}: {msg}"

    per_seed_hf = {
        str(s): {str(M): {"tcft_variance_ratio": 0.15 if M >= 512 else 0.05}
                 for M in [256, 512, 1024]}
        for s in [7, 17, 23]
    }
    # 3 seeds fail at M=512 (3 >= HF_VR_SEEDS=2)
    v_hf, _ = compute_verdict({"per_seed": per_seed_hf, "N": N_FULL})
    assert "HARD_FAIL" in v_hf, f"Expected HF: {v_hf}"

    # Live smoke cell
    result = run_one_cell(N=N_SMOKE, M=64, seed=17)
    assert "tcft_variance_ratio" in result, f"missing tcft_variance_ratio: {list(result.keys())}"
    vr = result["tcft_variance_ratio"]
    assert vr is not None and not math.isnan(vr), f"tcft_variance_ratio NaN"
    assert vr >= 0.0, f"tcft_variance_ratio negative: {vr}"

    # 4x smoke: N=2048
    result4 = run_one_cell(N=N_SMOKE * 4, M=64, seed=17)
    vr4 = result4.get("tcft_variance_ratio")
    assert vr4 is not None and not math.isnan(vr4), "4x tcft_variance_ratio NaN"

    print(f"[selftest] tcft_m_sweep_v4_n4096 PASS vr_smoke={vr:.4f} vr_4x={vr4:.4f}",
          flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    m_values = M_VALUES_SMOKE if smoke else M_VALUES_FULL
    seeds    = SEEDS_SMOKE if smoke else SEEDS_FULL
    N_cfg    = N_SMOKE if smoke else N_FULL

    print(f"tcft_m_sweep_v4_n4096 mode={'SMOKE' if smoke else 'FULL'} "
          f"N={N_cfg} M_values={m_values} seeds={seeds}", flush=True)

    per_seed: Dict = {}

    for seed in seeds:
        m_results: Dict = {}
        for M in m_values:
            t_cell = time.monotonic()
            result = run_one_cell(N=N_cfg, M=M, seed=seed)
            elapsed_cell = time.monotonic() - t_cell
            vr = result.get("tcft_variance_ratio")
            print(f"  seed={seed} M={M} tcft_variance_ratio={vr:.4f} elapsed={elapsed_cell:.1f}s",
                  flush=True)
            m_results[str(M)] = {"tcft_variance_ratio": vr, "elapsed_s": round(elapsed_cell, 2),
                                  **{k: v for k, v in result.items()
                                     if k not in ("tcft_variance_ratio",)}}

        per_seed[str(seed)] = m_results

    elapsed_total = time.monotonic() - t0
    verdict, verdict_msg = compute_verdict({"per_seed": per_seed, "N": N_cfg})

    summary = {
        "anchor": "tcft_m_sweep_v4_n4096",
        "N": N_cfg, "smoke": smoke,
        "M_values": m_values, "seeds": seeds,
        "per_seed": per_seed,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed_total, 2),
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as fp:
        json.dump(summary, fp, indent=2)

    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)
    print(f"[elapsed] {elapsed_total:.1f}s", flush=True)
    print(f"[output] {out_path}", flush=True)


def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--self-test", action="store_true", dest="self_test")
    args = p.parse_args()
    if args.self_test:
        sys.exit(0)
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
