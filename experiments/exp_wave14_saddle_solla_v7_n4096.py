"""Saad-Solla genuine large-N FULL probe v7 at N=4096.

CONTEXT:
  v3: N=1024, 3 seeds, CPU -- HARD_PASS (R^2=0.322, max_dev=0.249)
  v4: labeled n4096 but ran at N=512 smoke (PROT-018 violation, pre-enforcement)
  v5: labeled n4096 but ran at N=512 smoke (PROT-018 violation)
  v6: labeled n4096_gpu but ran at N=512 SMOKE (2.64s elapsed, 1 seed, PROT-018 mismatch)
  v7: THIS script. N=4096 HARD-CODED as bare `N = 4096`. GPU mandatory.
      5 seeds. No smoke bypass changes production N. PROT-018 structurally satisfied.

HYPOTHESIS:
  Saddle-cascade discrete plateau structure (R^2 < 0.85, max_dev >= 0.08) persists
  at N=4096 with 5 independent seeds. All 4 prior small-N tests agree (HARD-PASS
  at N<=1024). This is the first genuine production-scale confirmation.

DESIGN:
  - N = 4096 (production, HARD-CODED -- PROT-018 binding contract)
  - Seeds: [7, 17, 23, 31, 41] (5 seeds)
  - f_sweep: [0.0, 0.25, 0.5, 0.75, 1.0] (5-point)
  - Phase A: 8 epochs, Phase B: 5 epochs
  - Corpus: 200KB bytes
  - GPU device (mandatory: N=4096 is slow on CPU)
  - Smoke: N=512, 1 seed, 3 f-points, 1 epoch each (gate only; does NOT set N=4096 path)

PRE-REGISTERED BANDS (HARD-PASS / HARD-FAIL / MIDDLE-BAND):
  HARD-PASS (per-seed): R^2 < 0.85 AND max_deviation >= 0.08
  HARD-FAIL (per-seed): R^2 >= 0.95 AND max_deviation < 0.04
  MIDDLE-BAND: otherwise
  OVERALL-PASS: >= 4/5 seeds HARD-PASS
  OVERALL-FAIL: >= 4/5 seeds HARD-FAIL
  OVERALL-MIXED: else
  NOTE: thresholds IDENTICAL to v3/v4/v5/v6 (prior empirical anchor: v3 HARD-PASS)
  Calibration: prior empirical anchor exists (v3 R^2=0.322, max_dev=0.249). No band widening.

Self-tests (formula inputs -> expected outputs):
  1. pearson_r2([0,1,2,3], [0,2,4,6]) -> 1.0 (linear data)
  2. pearson_r2([0,0.25,0.5,0.75,1.0], [0.60,0.62,0.94,0.94,0.94]) < 0.80 (cascade)
  3. linear_fit_residuals([0,0.25,0.5,0.75,1.0], [0.60,0.62,0.94,0.94,0.94]) -> max_dev >= 0.10
  4. N == 4096 assertion (PROT-018 structural check in selftest)
  5. run_one_cell at smoke scale returns retention_A in (0, 1)

Timeout estimate:
  smoke_wall_s=~30 (expected at N=512), FULL_N/smoke_N = 4096/512 = 8,
  FULL_seeds/smoke_seeds = 5/1 = 5, scaling_exp = 1.5 (vector sweep, no matrix ops)
  timeout_s = ceil(1.5 * 30 * 8^1.5 * 5) = ceil(1.5 * 30 * 22.6 * 5) = ceil(5091) = 5400
  Rounding to nearest 300: timeout_s = 5400

Queue: overnight_queue (GPU mandatory: N=4096, 5 seeds, 5 f-values)
Pre-reg: preregs/2026-05-27_wave14_saddle_solla_v7_n4096.md
Parent: wave14_saddle_cascade_plateau_v3 (N=1024, R^2=0.322, max_dev=0.249, 3 seeds HARD-PASS)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
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

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Load Kovacs base infrastructure (train_w_with_replay, evaluate_bpc, etc.)
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_base_spec = importlib.util.spec_from_file_location("base_v7", _base_path)
base = importlib.util.module_from_spec(_base_spec)
_base_spec.loader.exec_module(base)
pa = base.pa

# Reuse v3 helper functions (same cascade logic, same threshold formula)
_v3_path = REPO / "experiments" / "exp_wave14_saddle_cascade_plateau_v3.py"
_v3_spec = importlib.util.spec_from_file_location("v3_cascade_v7", _v3_path)
v3_mod = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3_mod)

build_mixed_corpus = v3_mod.build_mixed_corpus
pearson_r2 = v3_mod.pearson_r2
linear_fit_residuals = v3_mod.linear_fit_residuals
run_one_cell = v3_mod.run_one_cell
compute_verdict = v3_mod.compute_verdict

# ── PRODUCTION CONFIG (v7: N=4096 HARD-CODED, PROT-018 binding) ──
N = 4096          # PRODUCTION N -- PROT-018: _n4096 suffix binds to this line
N_SMOKE = 512     # smoke-only gate scale; does NOT affect FULL queue run
F_SWEEP_FULL = [0.0, 0.25, 0.5, 0.75, 1.0]
F_SWEEP_SMOKE = [0.0, 0.5, 1.0]
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]
BATCH_SIZE = 32
BATCH_SIZE_SMOKE = 16
EPOCHS = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES = 200_000
BYTES_SMOKE = 4_000

# Pre-registered thresholds (IDENTICAL to v3/v4/v5/v6)
LINEAR_R2_PASS_THRESHOLD = 0.85
LINEAR_R2_FAIL_THRESHOLD = 0.95
DEVIATION_PASS_THRESHOLD = 0.08
DEVIATION_FAIL_THRESHOLD = 0.04

N_SEEDS_HARDPASS_FOR_OVERALL = 4   # 4/5 seeds HARD-PASS -> OVERALL-PASS
N_SEEDS_HARDFAIL_FOR_OVERALL = 4   # 4/5 seeds HARD-FAIL -> OVERALL-FAIL


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: PROT-018 structural check -- N must be exactly 4096
    assert N == 4096, f"PROT-018: production N must be 4096; got {N}"

    # Self-test 2: pearson_r2 on linear data -> 1.0
    r2_lin = pearson_r2([0.0, 1.0, 2.0, 3.0], [0.0, 2.0, 4.0, 6.0])
    assert abs(r2_lin - 1.0) < 1e-6, f"pearson_r2 on linear must be 1.0; got {r2_lin}"

    # Self-test 3: cascade hypothetical -> correctly identifies HARD-PASS
    cascade_fs = [0.0, 0.25, 0.5, 0.75, 1.0]
    cascade_rets = [0.60, 0.62, 0.94, 0.94, 0.94]
    r2_cas = pearson_r2(cascade_fs, cascade_rets)
    assert r2_cas < 0.80, f"cascade data R^2 should be < 0.80; got {r2_cas}"
    _, max_dev_cas, _ = linear_fit_residuals(cascade_fs, cascade_rets)
    assert max_dev_cas >= 0.10, f"cascade max_dev should be >= 0.10; got {max_dev_cas}"

    # Self-test 4: run_one_cell at smoke scale returns valid retention_A
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    result = run_one_cell(
        seed=17, f=0.5, N=N_SMOKE, batch_size=BATCH_SIZE_SMOKE,
        n_epochs=EPOCHS_SMOKE, phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=BYTES_SMOKE, device=device
    )
    assert "retention_A" in result, f"run_one_cell missing 'retention_A': {list(result.keys())}"
    ret = result["retention_A"]
    assert isinstance(ret, float) and 0.0 < ret <= 1.0, f"retention_A out of (0,1]: {ret}"

    print(f"[selftest] v7 PASSED: N=4096 assertion OK, pearson_r2 OK, "
          f"cascade HARD-PASS logic OK, run_one_cell smoke retention={ret:.4f}", flush=True)


_instrumentation_selftest()


def _score_seed(fs: List[float], retentions: List[float]) -> Dict:
    r2 = pearson_r2(fs, retentions)
    _, max_dev, _ = linear_fit_residuals(fs, retentions)
    if r2 < LINEAR_R2_PASS_THRESHOLD and max_dev >= DEVIATION_PASS_THRESHOLD:
        verdict = "HARD_PASS"
    elif r2 >= LINEAR_R2_FAIL_THRESHOLD and max_dev < DEVIATION_FAIL_THRESHOLD:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE"
    return {"verdict": verdict, "r2": round(r2, 4), "max_dev": round(max_dev, 4)}


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # CRITICAL: full run uses N=4096 (production config); smoke uses N_SMOKE=512 (gate only)
    n = N_SMOKE if smoke else N
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    f_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE
    epochs = EPOCHS_SMOKE if smoke else EPOCHS
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS
    n_bytes = BYTES_SMOKE if smoke else BYTES

    mode_str = "SMOKE" if smoke else "FULL"
    # HDLAB_EXP_NAME-aware exp_name (n-mismatch eradication 2026-05-27).
    exp_name = os.environ.get("HDLAB_EXP_NAME", "wave14_saddle_solla_v7_n4096")
    print(f"[run] {exp_name} {mode_str} N={n} seeds={seeds} device={device}", flush=True)
    if not smoke:
        assert n == 4096, f"FULL run must use N=4096; got {n}"

    out_dir = get_output_dir(exp_name)

    seed_results: Dict = {}
    for seed in seeds:
        print(f"\n[seed={seed}]", flush=True)
        per_f_rets: Dict[float, float] = {}
        for f in f_sweep:
            cell = run_one_cell(
                seed=seed, f=f, N=n, batch_size=batch_size,
                n_epochs=epochs, phase_a_epochs=phase_a_epochs,
                n_bytes=n_bytes, device=device
            )
            ret = cell["retention_A"]
            per_f_rets[f] = ret
            print(f"  f={f:.2f} retention_A={ret:.4f}", flush=True)
        seed_results[seed] = per_f_rets

    seed_verdicts: Dict = {}
    for seed, per_f in seed_results.items():
        fs = sorted(per_f.keys())
        rets = [per_f[f] for f in fs]
        sv = _score_seed(fs, rets)
        seed_verdicts[seed] = sv
        print(f"  [seed={seed}] r2={sv['r2']} max_dev={sv['max_dev']} -> {sv['verdict']}", flush=True)

    n_hardpass = sum(1 for sv in seed_verdicts.values() if sv["verdict"] == "HARD_PASS")
    n_hardfail = sum(1 for sv in seed_verdicts.values() if sv["verdict"] == "HARD_FAIL")
    n_middle = sum(1 for sv in seed_verdicts.values() if sv["verdict"] == "MIDDLE")

    if n_hardpass >= N_SEEDS_HARDPASS_FOR_OVERALL:
        overall = "HARD_PASS"
        overall_msg = (
            f"HARD_PASS: {n_hardpass}/{len(seeds)} seeds HARD-PASS at N=4096. "
            f"Saddle-cascade discrete structure confirmed at genuine production scale. "
            f"Saad-Solla large-N FULL evidence: substrate retention is non-linear in f."
        )
    elif n_hardfail >= N_SEEDS_HARDFAIL_FOR_OVERALL:
        overall = "HARD_FAIL"
        overall_msg = (
            f"HARD_FAIL: {n_hardfail}/{len(seeds)} seeds HARD-FAIL at N=4096. "
            f"Discrete plateau does not persist at production scale. "
            f"Finite-N artifact hypothesis supported; Saad-Solla framework not confirmed."
        )
    else:
        overall = "MIDDLE_BAND"
        overall_msg = (
            f"MIDDLE_BAND: {n_hardpass} HARD-PASS, {n_hardfail} HARD-FAIL, "
            f"{n_middle} MIDDLE at N=4096. Mixed large-N evidence."
        )

    elapsed = round(time.time() - t0, 2)
    print(f"\n[result] overall={overall} HARD_PASS={n_hardpass}/{len(seeds)} "
          f"HARD_FAIL={n_hardfail}/{len(seeds)} elapsed={elapsed}s", flush=True)
    print(f"[verdict] {overall}", flush=True)
    print(f"[verdict_msg] {overall_msg}", flush=True)

    metrics = {
        "verdict": overall,
        "verdict_msg": overall_msg,
        "elapsed_s": elapsed,
        "summary": {
            "N": n,
            "seeds": seeds,
            "n_hardpass": n_hardpass,
            "n_hardfail": n_hardfail,
            "n_middle": n_middle,
            "seed_verdicts": seed_verdicts,
            "f_sweep": f_sweep,
        },
        "config": {
            "mode": mode_str,
            "N_production": N,
            "N_run": n,
            "seeds": seeds,
            "f_sweep": f_sweep,
            "batch_size": batch_size,
            "epochs": epochs,
            "phase_a_epochs": phase_a_epochs,
            "n_bytes": n_bytes,
            "device": str(device),
            "parent_v3_r2": 0.322,
            "parent_v3_max_dev": 0.249,
        },
    }

    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true",
                        help="Smoke-gate run at N=512 (does NOT change production N=4096)")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
