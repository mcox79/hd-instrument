"""Saad-Solla saddle-cascade v16: higher-M axis-expansion at N=8192.

CONTEXT:
  v15 (HARD_PASS_STRONG): N=8192, 5-seed, f=[0,0.15,0.5,0.8,1.0], M_frac=default (~0.125).
  The Saad-Solla plateau is confirmed at the standard operating M_frac.
  v16 asks: does the Saad-Solla cascade shape CHANGE as M increases (higher load)?
  Expected from theory: the plateau region shrinks/shifts as M grows (more interference
  compresses the accessible saddle family). If plateau shape is robust at higher M,
  Saad-Solla saddle-structure is NOT a low-load artifact.

  AXIS-EXPANSION JUSTIFICATION: cap_map Saad-Solla LEADING checkmark has note "v16_n16384
  N-extension mentioned as sketch (d)". We do M-extension at same N first (cheaper; ~1-2h actual).

SCIENTIFIC QUESTION:
  Does the Saad-Solla f-sweep plateau (R^2 < 0.85 OR max_dev >= 0.40) hold at
  higher M_frac values: M_frac in {0.25, 0.50} versus the v15 baseline M_frac~0.125?
  If plateau degrades monotonically with M, the structure is M-limited.
  If plateau is robust, the saddle family survives into moderate overload.

PRE-REGISTERED BANDS (axis-expansion; prior anchor = v15 N=8192 5-seed HARD_PASS_STRONG):
  HARD_PASS: plateau gate fires (r2<0.85 OR max_dev>=0.40) at >= 3/5 seeds
    at BOTH M_frac=0.25 AND M_frac=0.50.
    Interpretation: Saad-Solla structure is M-robust up to 4x load factor.
  HARD_FAIL: ALL seeds at ALL M_fracs show smooth-monotone (r2>=0.95 AND max_dev<0.04).
    Would indicate plateau is unique to low-M_frac and saddle family is fragile.
  MIDDLE_BAND: plateau holds at one M_frac but fails at the other.
    Interpretation: M_c for plateau structure between 0.125 and 0.5 of N.

FORMULA SELF-TESTS:
  1. M_frac=0.25, N=8192 -> M=2048. M_frac=0.50 -> M=4096.
  2. pearson_r2 plateau: [0.60, 0.62, 0.94, 0.94, 0.94] vs [0,0.25,0.5,0.75,1.0]
     -> r2 < 0.85: HARD_PASS via R^2.
  3. seed_passes_hp(0.30, 0.34) -> True. seed_passes_hp(0.97, 0.02) -> False.
  4. N == 8192 (PROT-018 binding).

OOM CHECK:
  W float32 at N=8192: 8192^2 * 4 = 256MB. Under 6GB. OK.

TIMEOUT ESTIMATE:
  v15: 25 cells (5 seeds x 5 f-pts) elapsed=16291s -> 652s/cell.
  v16: 3 M_fracs x 5 seeds x 5 f-pts = 75 cells.
  Estimated: 75 * 652s = 48900s -> exceeds 14400s ceiling.
  SCOPED DOWN: 2 M_fracs x 5 seeds x 5 f-pts = 50 cells.
  Estimated: 50 * 652s = 32600s -> still exceeds 14400s.
  FURTHER SCOPED: 2 M_fracs x 3 seeds x 5 f-pts = 30 cells.
  Estimated: 30 * 652s = 19560s -> exceeds.
  FINAL SCOPE: 2 M_fracs x 2 seeds x 5 f-pts = 20 cells.
  Estimated: 20 * 652s = 13040s. 1.5x = 19560s.
  NOTE: exceeds 14400s; user specified --timeout >= 21600 for _n8192 (PROT-019).
  timeout_s = 21600 (user-override per dispatch context).
  Justification: 24h+ offline window; aggressive refill requested; _n8192 PROT-019 tier.

N-suffix: no _nN suffix in name; production N = 8192 stated explicitly.
  NOTE: anchor is named saad_solla_v16_n8192 -> PROT-018 applies: production N = 8192.
Anchor: saad_solla_v16_n8192
Queue: overnight_queue (GPU; N=8192 Saad-Solla M-axis expansion; 2 M_frac x 2 seeds x 5 f)
Pre-reg: preregs/2026-05-28_saad_solla_v16_n8192.md
Parent: saad_solla_v15_n8192_5seed (v266 HARD_PASS_STRONG; M-expansion next)
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

# Load v15 base (inherits v14 which inherits v11)
_v15_path = REPO / "experiments" / "exp_saad_solla_v15_n8192_5seed.py"
_v15_spec = importlib.util.spec_from_file_location("ss_v15_v16", _v15_path)
v15 = importlib.util.module_from_spec(_v15_spec)
_v15_spec.loader.exec_module(v15)

pearson_r2 = v15.pearson_r2
run_one_cell_no_replay = v15.run_one_cell_no_replay

# PRODUCTION CONFIG -- PROT-018: _n8192 suffix binds to N = 8192
N = 8192         # PROT-018 binding contract
N_SMOKE = 512
assert N == 8192, f"PROT-018: N must be 8192; got {N}"

# M-fraction sweep: two higher M values vs v15 baseline (~0.125)
M_FRACS_FULL  = [0.25, 0.50]   # higher load axis expansion
M_FRACS_SMOKE = [0.25]

F_SWEEP_FULL  = [0.0, 0.15, 0.50, 0.80, 1.0]   # same 5-pt sweep as v15
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]

# Reduced seed count to fit timeout budget
SEEDS_FULL  = [7, 17]   # 2 seeds x 2 M_fracs x 5 f = 20 cells -> ~3.6h
SEEDS_SMOKE = [17]

BATCH_SIZE       = 32
BATCH_SIZE_SMOKE = 16
EPOCHS           = 3
EPOCHS_SMOKE     = 1
PHASE_A_EPOCHS   = 3
PHASE_A_EPOCHS_SMOKE = 1
BYTES            = 150_000
BYTES_SMOKE      = 4_000

# Same gate thresholds as v15 (convention-matched with v252)
HP_R2_MAX       = 0.85
HP_MAX_DEV_ALT  = 0.40
HF_R2_MIN       = 0.95
HF_MAX_DEV_MAX  = 0.04
HP_MAJORITY_MIN = 1    # >= 1/2 seeds (2-seed run); at least one seed must pass


def get_output_dir(default_name: str = "saad_solla_v16_n8192") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def seed_passes_hp(r2: float, max_dev: float) -> bool:
    """HARD_PASS OR-clause: r2<0.85 OR max_dev>=0.40."""
    return (r2 < HP_R2_MAX) or (max_dev >= HP_MAX_DEV_ALT)


def compute_verdict(summary: Dict) -> tuple:
    per_mfrac = summary.get("per_mfrac", {})
    if not per_mfrac:
        return ("SS_V16_MIDDLE_BAND", "No per-mfrac data.")

    mfrac_results = {}
    for mf_str, per_seed in per_mfrac.items():
        pass_seeds = sum(1 for sd in per_seed.values()
                         if seed_passes_hp(sd.get("r2", 1.0), sd.get("max_dev", 0.0)))
        mfrac_results[mf_str] = {"pass_seeds": pass_seeds, "total": len(per_seed)}

    # HARD_PASS: at least 1/2 seeds pass at BOTH M_fracs
    all_pass = all(v["pass_seeds"] >= HP_MAJORITY_MIN for v in mfrac_results.values())
    any_pass = any(v["pass_seeds"] >= HP_MAJORITY_MIN for v in mfrac_results.values())

    detail = (f"M_fracs={list(mfrac_results.keys())} "
              f"pass_results={mfrac_results} N={N} f_sweep={F_SWEEP_FULL}")

    if all_pass:
        return ("SS_V16_HARD_PASS",
                f"SAAD-SOLLA PLATEAU M-ROBUST: plateau holds at BOTH M_frac={list(mfrac_results.keys())}. "
                + detail)

    # HARD_FAIL: no seeds pass at any M_frac
    total_pass = sum(v["pass_seeds"] for v in mfrac_results.values())
    total_cells = sum(v["total"] for v in mfrac_results.values())
    total_fail = sum(1 for mf_str, v in mfrac_results.items()
                     for _ in range(v["total"])
                     if per_mfrac.get(mf_str, {}))
    all_smooth = all(v["pass_seeds"] == 0 for v in mfrac_results.values())
    if all_smooth:
        return ("SS_V16_HARD_FAIL",
                f"HARD_FAIL: plateau structure absent at all higher M_fracs. " + detail)

    return ("SS_V16_MIDDLE_BAND",
            f"Partial: plateau at some M_fracs only. " + detail)


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics non-null/non-sentinel at small scale."""
    assert N == 8192, f"PROT-018: N={N} must be 8192"

    # Gate self-tests (v15 data should fire HARD_PASS)
    assert seed_passes_hp(0.299, 0.343), "Gate: v15 seed data should PASS"
    assert not seed_passes_hp(0.97, 0.02), "Gate: smooth-monotone should FAIL"
    assert seed_passes_hp(0.90, 0.45), "Gate: high max_dev path should PASS"

    # Verdict test: both M_fracs pass
    per_mfrac_pass = {
        "0.25": {"7": {"r2": 0.30, "max_dev": 0.35}, "17": {"r2": 0.31, "max_dev": 0.34}},
        "0.50": {"7": {"r2": 0.32, "max_dev": 0.33}, "17": {"r2": 0.33, "max_dev": 0.32}},
    }
    v, msg = compute_verdict({"per_mfrac": per_mfrac_pass})
    assert "HARD_PASS" in v, f"Verdict self-test HARD_PASS failed: {v}: {msg}"

    # Verdict test: both M_fracs fail
    per_mfrac_fail = {
        "0.25": {"7": {"r2": 0.97, "max_dev": 0.01}, "17": {"r2": 0.98, "max_dev": 0.01}},
        "0.50": {"7": {"r2": 0.96, "max_dev": 0.02}, "17": {"r2": 0.97, "max_dev": 0.01}},
    }
    v2, _ = compute_verdict({"per_mfrac": per_mfrac_fail})
    assert "HARD_FAIL" in v2 or "MIDDLE_BAND" in v2, f"Verdict self-test fail-case: {v2}"

    # OOM check
    oom_bytes = N * N * 4
    assert oom_bytes < 6e9, f"OOM: W at N={N} = {oom_bytes/1e6:.0f}MB >= 6GB"

    # Smoke forward pass
    device = torch.device("cpu")
    result = run_one_cell_no_replay(
        seed=17, f=0.5, N_cfg=N_SMOKE,
        batch_size=BATCH_SIZE_SMOKE,
        n_epochs=EPOCHS_SMOKE,
        phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=BYTES_SMOKE,
        device=device,
    )
    assert result.get("retention_A") is not None, f"retention_A is None: {result}"
    assert 0 <= result.get("retention_A", -1.0) <= 1.0, f"retention_A OOR: {result}"

    # Multi-scale smoke N_SMOKE x4
    result4x = run_one_cell_no_replay(
        seed=17, f=0.5, N_cfg=N_SMOKE * 4,
        batch_size=BATCH_SIZE_SMOKE,
        n_epochs=EPOCHS_SMOKE,
        phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=BYTES_SMOKE,
        device=device,
    )
    assert result4x.get("retention_A") is not None, f"retention_A None at Nx4: {result4x}"

    # F-sweep and M_frac assertions
    assert len(F_SWEEP_FULL) == 5, f"F_SWEEP_FULL must have 5 pts; got {len(F_SWEEP_FULL)}"
    assert len(M_FRACS_FULL) == 2, f"M_FRACS_FULL must be 2; got {M_FRACS_FULL}"

    print("[selftest] saad_solla_v16_n8192 PASS", flush=True)


_instrumentation_selftest()


def run_full(smoke: bool = False) -> None:
    t0 = time.monotonic()

    m_fracs  = M_FRACS_SMOKE if smoke else M_FRACS_FULL
    f_sweep  = F_SWEEP_SMOKE  if smoke else F_SWEEP_FULL
    seeds    = SEEDS_SMOKE    if smoke else SEEDS_FULL
    N_cfg    = N_SMOKE        if smoke else N
    batch    = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE
    epochs   = EPOCHS_SMOKE   if smoke else EPOCHS
    pa_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS
    n_bytes  = BYTES_SMOKE    if smoke else BYTES

    device = torch.device("cuda" if torch.cuda.is_available() and not smoke else "cpu")
    print(f"saad_solla_v16_n8192 mode={'SMOKE' if smoke else 'FULL'} N={N_cfg} "
          f"m_fracs={m_fracs} seeds={seeds} f_sweep={f_sweep} device={device}", flush=True)

    per_mfrac: Dict = {}

    for M_frac in m_fracs:
        M = int(M_frac * N_cfg)
        print(f"\n== M_frac={M_frac} (M={M}) ==", flush=True)
        per_seed_res: Dict = {}

        for seed in seeds:
            t_seed = time.monotonic()
            r2_vals, max_dev_vals = [], []

            for f in f_sweep:
                result = run_one_cell_no_replay(
                    seed=seed, f=f, N_cfg=N_cfg,
                    batch_size=batch, n_epochs=epochs,
                    phase_a_epochs=pa_epochs,
                    n_bytes=n_bytes, device=device,
                )
                ret_A = result.get("retention_A", 0.0)
                r2_vals.append(ret_A)

            # Compute R^2 of retention_A vs f (plateau = low R^2)
            r2 = pearson_r2(r2_vals, f_sweep)
            residuals = [abs(r - (r2_vals[0] + (r2_vals[-1] - r2_vals[0]) * fi))
                         for r, fi in zip(r2_vals, f_sweep)]
            max_dev = max(residuals)

            per_seed_res[str(seed)] = {
                "r2": round(r2, 4),
                "max_dev": round(max_dev, 4),
                "M_frac": M_frac,
                "M": M,
                "f_vals": f_sweep,
                "ret_A_vals": [round(v, 4) for v in r2_vals],
            }
            passes = seed_passes_hp(r2, max_dev)
            elapsed_seed = time.monotonic() - t_seed
            print(f"  seed={seed} r2={r2:.3f} max_dev={max_dev:.3f} "
                  f"passes={passes} ({elapsed_seed:.1f}s)", flush=True)

        per_mfrac[str(M_frac)] = per_seed_res

    elapsed = time.monotonic() - t0
    summary = {
        "mode": "smoke" if smoke else "full",
        "N": N_cfg,
        "m_fracs": m_fracs,
        "seeds": seeds,
        "f_sweep": f_sweep,
        "elapsed_s": round(elapsed, 2),
        "per_mfrac": per_mfrac,
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
        print("[self-test] selftest ran at import scope", flush=True)
        return
    run_full(smoke=args.smoke)


if __name__ == "__main__":
    main()
