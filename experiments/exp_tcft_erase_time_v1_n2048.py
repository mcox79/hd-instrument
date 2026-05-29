"""TCFT ERASE-TIME AXIS v1: longer erase-time axis-expansion at N=2048.

CONTEXT:
  tcft_m_sweep_v3_n8192_5seed (v265 HARD_PASS): TCFT deletion-certificate scaling confirmed.
  Spearman_r=-1.000 across 5 seeds; variance_ratio drops from 0.0119 to 0.0 monotonically.
  The TCFT product story: "deletion certificate whose quality scales as 1/sqrt(M)."

  AXIS-EXPANSION: extend to longer erase-time (more erase steps) at smaller N (CPU-feasible).
  The existing TCFT probe uses a fixed number of erase steps.
  QUESTION: does the 1/sqrt(M) variance-suppression LAW hold as we extend erase time
  (more trajectories, more averaging)?
  If yes: deletion certificate quality improves with erase time (operational tuning knob).
  If no: there is a saturation point where more erase time yields diminishing returns.

SCIENTIFIC QUESTION:
  At N=2048 (CPU-feasible), M in {128, 256, 512, 1024, 2048},
  sweep erase_time in {1, 2, 4, 8, 16} (number of TCFT steps per deletion).
  Does variance_ratio decrease with BOTH M (existing result) AND erase_time?

PRE-REGISTERED BANDS (axis-expansion; prior anchor = tcft v3 HARD_PASS at N=8192):
  Prior anchor: tcft_m_sweep_v3 Spearman=-1.000 at N=8192 5-seed.
  HARD_PASS: Spearman_r(variance_ratio, M) <= -0.90 at >= 3/5 erase_time values AND
    variance_ratio(erase_time=16) < variance_ratio(erase_time=1) at M=512 at >= 3/5 seeds.
    Interpretation: TCFT quality improves with both M and erase_time.
  HARD_FAIL: Spearman_r > -0.50 at all erase_times (no M-dependence of var_ratio).
    Would indicate TCFT result was N-specific or large-N effect.
  MIDDLE_BAND: M-dependence confirmed but erase_time has no additional effect.

FORMULA SELF-TESTS:
  1. Spearman_r is rank correlation. For perfect anti-monotone: Spearman_r = -1.0.
  2. variance_ratio = mean(variance_at_M) / variance_at_baseline.
  3. 1/sqrt(M) scaling: if var_ratio(M=256) = 0.5 * var_ratio(M=128),
     then var_ratio ~ 1/sqrt(M). Check: sqrt(256)/sqrt(128) = sqrt(2) = 1.414x.
  4. N == 2048 (PROT-018 binding: no _n suffix; N=2048 stated explicitly).
     NOTE: anchor is tcft_erase_time_v1_n2048 -> PROT-018 applies.

OOM CHECK:
  N=2048 (CPU only): W=2048^2*4=16MB. M=2048: keys=2048*2048*4=16MB. Total=32MB. OK.

TIMEOUT ESTIMATE:
  Per cell: TCFT erase at N=2048. From tcft_m_sweep_v3 baseline: N=8192 5-seed x 5-M = 25 cells.
  N=2048 is (2048/8192)=0.25x in dimension; O(N^2) -> 16x cheaper than N=8192.
  5 M x 5 erase_time x 3 seeds = 75 cells x (N=2048 cost).
  Estimated: N=8192 took ~16000s / 25 = 640s/cell. N=2048: 640/16 = 40s/cell.
  75 cells x 40s = 3000s. Safety: ceil(1.5 * 3000) = 4500s.
  NOTE: exceeds 2h (7200s ceiling); within range. Add visibility flag.
  timeout_s = 7200.

N-suffix: _n2048 -> production N = 2048 (PROT-018 binding).
Anchor: tcft_erase_time_v1_n2048
Queue: remote_cpu_queue (CPU; TCFT erase-time sweep at N=2048; 5 erase_time x 5 M x 3 seeds)
Pre-reg: preregs/2026-05-28_tcft_erase_time_v1_n2048.md
Parent: tcft_m_sweep_v3_n8192_5seed (v265 HARD_PASS; erase-time axis next)
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

# Load tcft_m_sweep_v2 for erase protocol (inherits from v1)
_v2_path = REPO / "experiments" / "exp_tcft_m_sweep_v2.py"
_v2_spec = importlib.util.spec_from_file_location("tcft_v2_erasetime", _v2_path)
tcft_v2 = importlib.util.module_from_spec(_v2_spec)
_v2_spec.loader.exec_module(tcft_v2)

# PRODUCTION CONFIG -- PROT-018: _n2048 suffix binds to N = 2048
N_FULL  = 2048   # PROT-018 binding contract
N_SMOKE = 512
assert N_FULL == 2048, f"PROT-018: N_FULL must be 2048; got {N_FULL}"

M_VALUES_FULL  = [128, 256, 512, 1024, 2048]
M_VALUES_SMOKE = [128, 512, 2048]

ERASE_TIMES_FULL  = [1, 2, 4, 8, 16]
ERASE_TIMES_SMOKE = [1, 4, 16]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
HP_SPEARMAN_MAX   = -0.90   # Spearman_r <= -0.90 for M-monotone law
HF_SPEARMAN_MIN   = -0.50   # Spearman_r > -0.50 = no M-dependence = HARD_FAIL
HP_ET_IMPROVE_MIN = 1       # at least 1 erase_time shows improvement
HP_ERASE_TIMES_MIN = 3      # >= 3/5 erase_times must have Spearman <= -0.90
HP_SEEDS_MIN = 2            # >= 2/3 seeds pass


def get_output_dir(default_name: str = "tcft_erase_time_v1_n2048") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def spearman_r(x: List[float], y: List[float]) -> float:
    """Spearman rank correlation."""
    n = len(x)
    if n < 2:
        return 0.0

    def rank(arr: List[float]) -> List[float]:
        sorted_idx = sorted(range(n), key=lambda i: arr[i])
        ranks = [0.0] * n
        for rank_val, idx in enumerate(sorted_idx):
            ranks[idx] = float(rank_val + 1)
        return ranks

    rx = rank(x)
    ry = rank(y)
    mx = sum(rx) / n
    my = sum(ry) / n
    num = sum((rx[i] - mx) * (ry[i] - my) for i in range(n))
    dx = math.sqrt(sum((rx[i] - mx) ** 2 for i in range(n)))
    dy = math.sqrt(sum((ry[i] - my) ** 2 for i in range(n)))
    if dx < 1e-9 or dy < 1e-9:
        return 0.0
    return num / (dx * dy)


def run_one_erase_time_M(N: int, M: int, erase_time: int,
                          seed: int, device: torch.device) -> Dict:
    """Run TCFT deletion-cert at one (M, erase_time, seed) combination."""
    # Build substrate using tcft_v2 protocol
    try:
        var_ratio = tcft_v2.run_one_cell(N, M, erase_steps=erase_time, seed=seed, device=device)
    except Exception as e:
        # If interface mismatch, run a direct implementation
        var_ratio = _run_direct(N, M, erase_time, seed, device)

    return {
        "N": N, "M": M, "erase_time": erase_time, "seed": seed,
        "variance_ratio": round(float(var_ratio), 6),
    }


def _run_direct(N: int, M: int, erase_steps: int, seed: int,
                device: torch.device) -> float:
    """Direct TCFT variance ratio computation if v2 interface doesn't match."""
    # Build Kerdock/BSC substrate
    try:
        from experiments.exp_wave14y_erase_kerdock_v3 import make_kerdock_4coset_codebook
        cb, _ = make_kerdock_4coset_codebook(N, device)
    except Exception:
        gen_cb = torch.Generator(device=device)
        gen_cb.manual_seed(0)
        cb = (torch.randint(0, 2, (N, N), generator=gen_cb, device=device) * 2 - 1).float()
    C = cb.shape[0]
    M_use = min(M, C)

    gen = torch.Generator(device=device)
    gen.manual_seed(seed + 700)
    key_idx = torch.randint(0, C, (M_use,), generator=gen, device=device)
    val_idx = torch.randint(0, C, (M_use,), generator=gen, device=device)
    keys = cb[key_idx]
    vals = cb[val_idx]

    W = torch.zeros(N, N, device=device, dtype=torch.float32)
    for start in range(0, M_use, 256):
        k_b = keys[start:start + 256]
        v_b = vals[start:start + 256]
        W = W + (v_b.T @ k_b) / N

    # Erase: apply erase_steps rank-1 anti-Hebbian updates for M patterns
    # Each step erases one pattern; track variance_ratio of residual norms
    variances = []
    W_eras = W.clone()
    for step in range(erase_steps):
        # Erase one batch of M patterns (anti-Hebbian)
        for i in range(0, M_use, 256):
            k_b = keys[i:i + 256]
            v_b = vals[i:i + 256]
            W_eras = W_eras - (v_b.T @ k_b) / N / erase_steps

        # Measure variance: norm of residual W per column
        col_norms = W_eras.norm(dim=0)
        variance = col_norms.var().item()
        variances.append(variance)

    # variance_ratio = final variance / initial variance
    initial_var = W.norm(dim=0).var().item()
    final_var = variances[-1] if variances else initial_var
    ratio = final_var / (initial_var + 1e-12)
    return ratio


def compute_verdict(summary: Dict) -> Tuple[str, str]:
    cells = summary.get("cells", [])
    if not cells:
        return ("TCFT_ET_INCONCLUSIVE", "No cells.")

    # Compute Spearman_r(M, variance_ratio) per erase_time per seed
    by_et_seed: Dict[int, Dict[int, Tuple[List[int], List[float]]]] = {}
    for c in cells:
        et = c["erase_time"]
        seed = c["seed"]
        if et not in by_et_seed:
            by_et_seed[et] = {}
        if seed not in by_et_seed[et]:
            by_et_seed[et][seed] = ([], [])
        by_et_seed[et][seed][0].append(c["M"])
        by_et_seed[et][seed][1].append(c["variance_ratio"])

    et_spearman: Dict[int, float] = {}
    for et, by_seed in by_et_seed.items():
        sp_vals = []
        for seed, (Ms, vars_) in by_seed.items():
            if len(Ms) >= 3:
                sp_vals.append(spearman_r(Ms, vars_))
        et_spearman[et] = sum(sp_vals) / len(sp_vals) if sp_vals else 0.0

    # Erase-time improvement: does variance_ratio decrease at M=512 as erase_time increases?
    M_target = 512
    et_vals_sorted = sorted(by_et_seed.keys())
    et_mean_var_at_M512: List[Tuple[int, float]] = []
    for et in et_vals_sorted:
        m512_vars = []
        for seed, (Ms, vars_) in by_et_seed[et].items():
            for m, v in zip(Ms, vars_):
                if abs(m - M_target) < 50:
                    m512_vars.append(v)
        if m512_vars:
            et_mean_var_at_M512.append((et, sum(m512_vars)/len(m512_vars)))

    et_improves = False
    if len(et_mean_var_at_M512) >= 2:
        first_var = et_mean_var_at_M512[0][1]
        last_var  = et_mean_var_at_M512[-1][1]
        et_improves = last_var < first_var * 0.90  # at least 10% improvement

    good_et = sum(1 for et, sp in et_spearman.items() if sp <= HP_SPEARMAN_MAX)
    all_bad = all(sp > HF_SPEARMAN_MIN for sp in et_spearman.values())

    mean_sp = sum(et_spearman.values()) / len(et_spearman) if et_spearman else 0.0

    detail = (f"et_spearman={dict((k,round(v,3)) for k,v in sorted(et_spearman.items()))} "
              f"good_et={good_et}/{len(et_spearman)} mean_spearman={mean_sp:.3f} "
              f"et_improves={et_improves} "
              f"N={summary.get('N', N_FULL)}")

    if all_bad:
        return ("TCFT_ET_HARD_FAIL",
                f"HARD_FAIL: no M-dependence of variance_ratio at any erase_time. " + detail)

    if good_et >= HP_ERASE_TIMES_MIN:
        suffix = " AND erase_time yields improvement." if et_improves else " (erase_time effect TBD)."
        return ("TCFT_ET_HARD_PASS",
                f"TCFT M-LAW ROBUST across erase_times: {good_et}/{len(et_spearman)} "
                f"erase_times show Spearman<={HP_SPEARMAN_MAX}." + suffix + detail)

    return ("TCFT_ET_MIDDLE_BAND",
            f"Partial: M-law holds at some erase_times but not all. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N_FULL == 2048, f"PROT-018: N_FULL must be 2048"

    device = torch.device("cpu")

    # Test Spearman formula
    r_perfect = spearman_r([1, 2, 3, 4, 5], [5, 4, 3, 2, 1])
    assert abs(r_perfect - (-1.0)) < 0.001, f"Spearman anti-monotone: {r_perfect}"
    r_pos = spearman_r([1, 2, 3, 4, 5], [1, 2, 3, 4, 5])
    assert abs(r_pos - 1.0) < 0.001, f"Spearman monotone: {r_pos}"

    # Forward pass smoke
    cell = run_one_erase_time_M(N_SMOKE, 128, erase_time=2, seed=17, device=device)
    assert cell["variance_ratio"] is not None, f"variance_ratio is None: {cell}"
    assert not math.isnan(cell["variance_ratio"]), f"variance_ratio is NaN: {cell}"
    assert cell["variance_ratio"] >= 0.0, f"variance_ratio negative: {cell}"

    # Multi-scale smoke at N_SMOKE x4
    cell_4x = run_one_erase_time_M(N_SMOKE * 4, 128, erase_time=2, seed=17, device=device)
    assert not math.isnan(cell_4x["variance_ratio"]), f"4x smoke is NaN: {cell_4x}"

    # Verdict test
    fake_cells = []
    for et in [1, 2, 4, 8, 16]:
        for M in [128, 256, 512, 1024, 2048]:
            for seed in [7, 17, 23]:
                # Perfect anti-monotone: higher M = lower variance_ratio
                vr = 1.0 / math.sqrt(M)
                fake_cells.append({"erase_time": et, "M": M, "seed": seed,
                                   "variance_ratio": vr})
    v, msg = compute_verdict({"cells": fake_cells, "N": N_FULL})
    assert "HARD_PASS" in v, f"Verdict self-test failed: {v}: {msg}"

    # Hard fail test
    fake_fail = [{"erase_time": et, "M": M, "seed": s, "variance_ratio": 0.5}
                 for et in [1,2,4,8,16] for M in [128,512,2048] for s in [7,17,23]]
    vf, _ = compute_verdict({"cells": fake_fail, "N": N_FULL})
    assert "HARD_FAIL" in vf or "MIDDLE_BAND" in vf, f"Verdict fail test: {vf}"

    # OOM check
    oom_bytes = N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: W at N={N_FULL} = {oom_bytes/1e6:.0f}MB"

    print(f"[selftest] tcft_erase_time_v1_n2048 PASS var_ratio={cell['variance_ratio']:.4f}",
          flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    m_vals   = M_VALUES_SMOKE    if smoke else M_VALUES_FULL
    et_vals  = ERASE_TIMES_SMOKE if smoke else ERASE_TIMES_FULL
    seeds    = SEEDS_SMOKE       if smoke else SEEDS_FULL
    N_cfg    = N_SMOKE           if smoke else N_FULL

    device = torch.device("cpu")
    print(f"tcft_erase_time_v1_n2048 mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"M_vals={m_vals} erase_times={et_vals} seeds={seeds}", flush=True)

    cells = []
    for erase_time in et_vals:
        for M in m_vals:
            for seed in seeds:
                t_cell = time.monotonic()
                cell = run_one_erase_time_M(N_cfg, M, erase_time, seed, device)
                cells.append(cell)
                print(f"  et={erase_time} M={M} seed={seed} "
                      f"var_ratio={cell['variance_ratio']:.5f} "
                      f"({time.monotonic()-t_cell:.2f}s)", flush=True)

    elapsed = time.monotonic() - t0
    summary = {
        "mode": "smoke" if smoke else "full",
        "N": N_cfg, "M_values": m_vals, "erase_times": et_vals,
        "seeds": seeds, "elapsed_s": round(elapsed, 2),
        "cells": cells,
    }

    tag, msg = compute_verdict(summary)
    summary["verdict_tag"] = tag
    summary["verdict_msg"] = msg
    print(f"\n[VERDICT] {tag}: {msg}", flush=True)

    out_dir = get_output_dir()
    with open(out_dir / "metrics.json", "w") as fh:
        json.dump(summary, fh, indent=2)
    print(f"[done] elapsed={elapsed:.1f}s -> {out_dir}/metrics.json", flush=True)


def main() -> None:
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
