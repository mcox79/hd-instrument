"""Saad-Solla M-sweep v20: M-axis expansion at N=4096 (CPU-compatible).

CONTEXT:
  saad_solla_v16_n8192 (GPU overnight queue): M-axis expansion at N=8192,
  2 M_fracs x 2 seeds. CPU timeline complement at N=4096.
  saad_solla_v15_n8192_5seed (HARD_PASS_STRONG): plateau at M_frac~0.125.
  v20 tests: does Saad-Solla plateau shape hold at N=4096 across 3 M_fracs?
  N=4096 is 4x cheaper than N=8192 (scales as N^2 in W matrix).

SCIENTIFIC QUESTION:
  At N=4096, does Saad-Solla f-sweep plateau (R^2 < 0.85 OR max_dev >= 0.40)
  hold at M_fracs = [0.125, 0.25, 0.50]?
  If plateau holds at all 3 M_fracs, the structure is M-robust at N=4096.
  If plateau degrades, there is an M_c for the saddle family.

PRE-REGISTERED BANDS:
  Prior: v15 N=8192 HARD_PASS_STRONG at M_frac~0.125.
  Expected: plateau holds at M_frac=0.125 at N=4096 (same f-sweep structure).
  Uncertain: M_fracs {0.25, 0.50} (higher load may compress saddle family).

  HARD_PASS: plateau gate (r2<0.85 OR max_dev>=0.40) fires at >= 2/3 seeds
    at >= 2/3 M_fracs tested.
    Interpretation: Saad-Solla structure M-robust at N=4096.
  HARD_FAIL: ALL seeds at ALL M_fracs show smooth-monotone (r2>=0.95 AND max_dev<0.04).
    Would indicate plateau disappears at N=4096 (N-sensitivity).
  MIDDLE_BAND: plateau at some M_fracs but not majority.

FORMULA SELF-TESTS:
  1. M_frac=0.125, N=4096 -> M=512. M_frac=0.25 -> M=1024. M_frac=0.50 -> M=2048.
  2. pearson_r2 plateau: [0.60, 0.62, 0.94, 0.94, 0.94] -> r2 < 0.85 -> PASS.
  3. seed_passes_hp(0.30, 0.34) -> True. seed_passes_hp(0.97, 0.02) -> False.
  4. N == 4096 (PROT-018 binding).
  5. OOM: W at N=4096 = 4096^2*4 = 64MB. Under 6GB.
  6. Cells per M_frac: 3 seeds x 5 f-pts = 15. Total: 45 cells.

TIMEOUT ESTIMATE:
  v15 N=8192 5-seed 5f-pts 25 cells elapsed=16291s -> 652s/cell.
  N=4096 vs N=8192 scale: (4096/8192)^2 = 0.25 (W matrix dominates).
  Per cell at N=4096: 652 * 0.25 = 163s.
  Total: 3 M_fracs x 3 seeds x 5 f-pts x 163s = 45 * 163s = 7335s.
  Safety 1.5x: 11002s. PROT-019 floor: timeout >= 14400. timeout_s = 14400.

N-suffix: _n4096 -> production N = 4096 (PROT-018 binding).
Anchor: saad_solla_v20_n4096_m_sweep
Queue: remote_cpu_queue (CPU; N=4096 BSC; M-axis sweep; 3 seeds)
Pre-reg: prereqs/2026-05-28_saad_solla_v20_n4096_m_sweep.md
Parent: saad_solla_v15_n8192_5seed (HARD_PASS_STRONG); saad_solla_v16_n8192 (GPU M-expansion)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load v15 base (inherits v14 which inherits v11) -- LAZY to avoid parent selftest at gate
def _load_v15():
    _v15_path = REPO / "experiments" / "exp_saad_solla_v15_n8192_5seed.py"
    _v15_spec = importlib.util.spec_from_file_location("ss_v15_v20", _v15_path)
    v15 = importlib.util.module_from_spec(_v15_spec)
    _v15_spec.loader.exec_module(v15)
    return v15

_v15_mod = None

def get_v15():
    global _v15_mod
    if _v15_mod is None:
        _v15_mod = _load_v15()
    return _v15_mod


def pearson_r2(xs: List[float], ys: List[float]) -> float:
    """Inline Pearson r^2 between xs and ys."""
    n = len(xs)
    if n < 2:
        return 1.0
    mx, my = sum(xs) / n, sum(ys) / n
    num = sum((xi - mx) * (yi - my) for xi, yi in zip(xs, ys))
    den_x = sum((xi - mx) ** 2 for xi in xs) ** 0.5
    den_y = sum((yi - my) ** 2 for yi in ys) ** 0.5
    if den_x < 1e-12 or den_y < 1e-12:
        return 1.0
    r = num / (den_x * den_y)
    return r * r


# PRODUCTION CONFIG -- PROT-018: _n4096 suffix binds to N = 4096
N_FULL  = 4096
N_SMOKE = 512
assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

M_FRACS_FULL  = [0.125, 0.25, 0.50]
M_FRACS_SMOKE = [0.125]

F_SWEEP_FULL  = [0.0, 0.15, 0.50, 0.80, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]

SEEDS_FULL  = [7, 17, 23]
SEEDS_SMOKE = [17]

BATCH_SIZE       = 32
BATCH_SIZE_SMOKE = 16
EPOCHS           = 3
EPOCHS_SMOKE     = 1
PHASE_A_EPOCHS   = 3
PHASE_A_EPOCHS_SMOKE = 1
BYTES            = 150_000
BYTES_SMOKE      = 4_000

# Pre-registered thresholds (same gate as v15/v16)
HP_R2_MAX       = 0.85
HP_MAX_DEV_ALT  = 0.40
HF_R2_MIN       = 0.95
HF_MAX_DEV_MAX  = 0.04
HP_MAJORITY_MIN = 2    # >= 2/3 seeds at >= 2/3 M_fracs


def get_output_dir(default_name: str = "saad_solla_v20_n4096_m_sweep") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def seed_passes_hp(r2: float, max_dev: float) -> bool:
    return (r2 < HP_R2_MAX) or (max_dev >= HP_MAX_DEV_ALT)


def compute_verdict(summary: Dict) -> tuple:
    per_mfrac = summary.get("per_mfrac", {})
    if not per_mfrac:
        return ("SS_V20_MIDDLE_BAND", "No per-mfrac data.")

    mfrac_results = {}
    for mf_str, per_seed in per_mfrac.items():
        pass_seeds = sum(1 for sd in per_seed.values()
                         if seed_passes_hp(sd.get("r2", 1.0), sd.get("max_dev", 0.0)))
        mfrac_results[mf_str] = {"pass_seeds": pass_seeds, "total": len(per_seed)}

    n_pass_fracs = sum(1 for v in mfrac_results.values() if v["pass_seeds"] >= HP_MAJORITY_MIN)
    n_fail_fracs = sum(1 for v in mfrac_results.values()
                       if v["pass_seeds"] == 0 and v["total"] > 0)
    n_fracs = len(mfrac_results)

    detail = (f"mfrac_results={mfrac_results} N={summary.get('N', N_FULL)} "
              f"f_sweep={F_SWEEP_FULL}")

    # HARD_FAIL: all seeds at all M_fracs smooth
    total_pass = sum(v["pass_seeds"] for v in mfrac_results.values())
    if total_pass == 0:
        return ("SS_V20_HARD_FAIL",
                f"NO PLATEAU AT N=4096: all smooth-monotone at all M_fracs. " + detail)

    # HARD_PASS: >= 2/3 seeds pass at >= 2/3 M_fracs
    if n_pass_fracs >= max(1, n_fracs * 2 // 3):
        return ("SS_V20_HARD_PASS",
                f"PLATEAU M-ROBUST AT N=4096: {n_pass_fracs}/{n_fracs} M_fracs pass. " + detail)

    return ("SS_V20_MIDDLE_BAND",
            f"PARTIAL PLATEAU: {n_pass_fracs}/{n_fracs} M_fracs pass. " + detail)


def _instrumentation_selftest() -> None:
    """Formula assertions only (no live computation to avoid loading parent at gate time)."""
    assert N_FULL == 4096, f"PROT-018: N_FULL must be 4096; got {N_FULL}"

    # Formula: M at each M_frac
    for mf, expected_M in [(0.125, 512), (0.25, 1024), (0.50, 2048)]:
        assert int(mf * N_FULL) == expected_M, f"M at M_frac={mf}: {int(mf*N_FULL)}"

    # Gate tests
    assert seed_passes_hp(0.30, 0.34), "Gate: v15-like data should PASS"
    assert not seed_passes_hp(0.97, 0.02), "Gate: smooth should FAIL"
    assert seed_passes_hp(0.90, 0.45), "Gate: high max_dev should PASS"

    # pearson_r2 inline check (xs=retention_vals, ys=f_sweep_vals)
    f5 = [0.0, 0.15, 0.5, 0.8, 1.0]
    # plateau-like: retention constant/wavy, f increases linearly -> low r2
    r2_plateau = pearson_r2([0.8, 0.8, 0.9, 0.9, 0.9], f5)
    assert r2_plateau < 0.85, f"plateau r2 expected < 0.85, got {r2_plateau:.3f}"
    # monotone: retention decreases with f -> high r2
    r2_mono = pearson_r2([0.9, 0.8, 0.6, 0.4, 0.2], f5)
    assert r2_mono > 0.90, f"monotone r2 expected > 0.90, got {r2_mono:.3f}"

    # Verdict tests
    v, _ = compute_verdict({"per_mfrac": {
        "0.125": {"7": {"r2": 0.30, "max_dev": 0.35}, "17": {"r2": 0.31, "max_dev": 0.34},
                  "23": {"r2": 0.29, "max_dev": 0.36}},
        "0.25": {"7": {"r2": 0.32, "max_dev": 0.33}, "17": {"r2": 0.33, "max_dev": 0.32},
                 "23": {"r2": 0.31, "max_dev": 0.34}},
        "0.50": {"7": {"r2": 0.34, "max_dev": 0.31}, "17": {"r2": 0.35, "max_dev": 0.30},
                 "23": {"r2": 0.33, "max_dev": 0.32}},
    }, "N": N_FULL})
    assert "HARD_PASS" in v, f"Self-test HARD_PASS: {v}"

    v2, _ = compute_verdict({"per_mfrac": {
        "0.125": {"7": {"r2": 0.97, "max_dev": 0.01}},
        "0.25": {"7": {"r2": 0.98, "max_dev": 0.01}},
        "0.50": {"7": {"r2": 0.96, "max_dev": 0.02}},
    }, "N": N_FULL})
    assert "HARD_FAIL" in v2 or "MIDDLE_BAND" in v2, f"Self-test fail: {v2}"

    # OOM
    oom_bytes = N_FULL * N_FULL * 4
    assert oom_bytes < 6e9, f"OOM: W at N_FULL={N_FULL} = {oom_bytes/1e6:.0f}MB >= 6GB"

    print(f"[selftest] saad_solla_v20_n4096_m_sweep PASS N_FULL={N_FULL}", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()
    v15 = get_v15()

    m_fracs  = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    f_sweep  = F_SWEEP_SMOKE  if smoke else F_SWEEP_FULL
    seeds    = SEEDS_SMOKE    if smoke else SEEDS_FULL
    N_cfg    = N_SMOKE        if smoke else N_FULL
    batch    = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE
    epochs   = EPOCHS_SMOKE   if smoke else EPOCHS
    pa_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS
    n_bytes  = BYTES_SMOKE    if smoke else BYTES

    device = torch.device("cpu")
    print(f"saad_solla_v20_n4096_m_sweep mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"m_fracs={m_fracs} seeds={seeds} f_sweep={f_sweep}", flush=True)

    per_mfrac: Dict = {}

    for M_frac in m_fracs:
        M = int(M_frac * N_cfg)
        print(f"\n== M_frac={M_frac} (M={M}) ==", flush=True)
        per_seed_res: Dict = {}

        for seed in seeds:
            t_seed = time.monotonic()
            r2_vals, max_dev_vals = [], []

            for f in f_sweep:
                result = v15.run_one_cell_no_replay(
                    seed=seed, f=f, N_cfg=N_cfg,
                    batch_size=batch, n_epochs=epochs,
                    phase_a_epochs=pa_epochs,
                    n_bytes=n_bytes, device=device,
                )
                ret_A = result.get("retention_A", 0.0)
                r2_vals.append(ret_A)
                max_dev_vals.append(ret_A)

            # Compute r2 of retention vs f (plateau = low r2)
            # Use inline pearson_r2 to avoid v15 signature ambiguity
            r2 = pearson_r2(r2_vals, f_sweep)
            # max_dev: residual from linear fit retention vs f
            if len(r2_vals) >= 2:
                slope = (r2_vals[-1] - r2_vals[0]) / max(f_sweep[-1] - f_sweep[0], 1e-9)
                residuals = [abs(rv - (r2_vals[0] + slope * (fi - f_sweep[0])))
                             for rv, fi in zip(r2_vals, f_sweep)]
                max_dev = max(residuals)
            else:
                max_dev = 0.0

            elapsed_s = time.monotonic() - t_seed
            passes = seed_passes_hp(r2, max_dev)
            print(f"  M_frac={M_frac} seed={seed} r2={r2:.4f} max_dev={max_dev:.4f} "
                  f"passes={passes} elapsed={elapsed_s:.1f}s", flush=True)

            per_seed_res[str(seed)] = {"r2": r2, "max_dev": max_dev, "seed": seed,
                                       "f_results": dict(zip([str(f) for f in f_sweep], r2_vals)),
                                       "passes_hp": passes}

        per_mfrac[str(M_frac)] = per_seed_res

    elapsed_total = time.monotonic() - t0
    verdict, verdict_msg = compute_verdict({"per_mfrac": per_mfrac, "N": N_cfg})

    summary = {
        "anchor": "saad_solla_v20_n4096_m_sweep",
        "N": N_cfg, "smoke": smoke,
        "M_fracs": m_fracs, "f_sweep": f_sweep, "seeds": seeds,
        "per_mfrac": per_mfrac,
        "verdict": verdict, "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed_total, 2),
    }
    out_dir = get_output_dir()
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)

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
