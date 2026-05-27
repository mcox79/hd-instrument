"""Saad-Solla saddle-cascade stepping stone v8 at N=2048.

CONTEXT:
  v3 (N=1024, CPU): HARD_PASS (R^2=0.322, max_dev=0.249, 3 seeds).
  v6 (N=4096 GPU, 1 seed smoke): 2.64s, MIDDLE_BAND smoke (gate only).
  v7 (N=4096 GPU, 5 seeds): TIMEOUT at 5400s. Full-scale N=4096 too slow.
  v8 (THIS): N=2048 stepping stone. Half N of v7. Confirms whether cascade
     structure persists at intermediate scale before committing N=4096 again.

HYPOTHESIS:
  Saddle-cascade discrete plateau structure (R^2 < 0.85, max_dev >= 0.08)
  persists at N=2048 with 5 seeds. If N=2048 HARD_PASS, re-queue N=4096
  with 2x epochs (more wall time budget). If N=2048 fails, discrete structure
  is N-bounded at N <= 1024.

DESIGN:
  - N = 2048 (production, PROT-018 binding: _n2048 suffix)
  - Seeds: [7, 17, 23, 31, 41] (5 seeds)
  - f_sweep: [0.0, 0.25, 0.5, 0.75, 1.0] (5-point)
  - Phase A: 8 epochs, Phase B: 5 epochs (same as v3)
  - Corpus: 200KB bytes
  - GPU device (mandatory for N=2048 with 5 seeds)
  - Smoke: N=512, 1 seed, 3 f-points, 1 epoch each

PRE-REGISTERED BANDS (HARD-PASS / HARD-FAIL / MIDDLE-BAND):
  Per-seed:
    HARD-PASS: R^2 < 0.85 AND max_deviation >= 0.08
    HARD-FAIL: R^2 >= 0.95 AND max_deviation < 0.04
    MIDDLE: otherwise
  Overall:
    OVERALL-PASS: >= 4/5 seeds HARD-PASS
    OVERALL-FAIL: >= 4/5 seeds HARD-FAIL
    OVERALL-MIXED: else
  NOTE: thresholds IDENTICAL to v3/v7 (prior empirical anchor: v3 HARD-PASS)

FORMULA SELF-TESTS:
  1. pearson_r2([0,1,2,3], [0,2,4,6]) -> 1.0
  2. pearson_r2([0,0.25,0.5,0.75,1.0], [0.60,0.62,0.94,0.94,0.94]) < 0.80 (cascade)
  3. linear_fit_residuals cascade -> max_dev >= 0.10
  4. N == 2048 assertion (PROT-018)
  5. run_one_cell smoke returns retention_A in (0, 1)

Timeout estimate:
  v7 timed out at N=4096 with timeout_s=5400. N=2048 is half:
  estimated = 5400 * (2048/4096)^1.5 = 5400 * 0.354 = 1912s
  Adding 20% margin: 2294s -> rounding up: 2400s (within 4h limit)

N-suffix: _n2048 binds to N=2048 production config.
Queue: overnight_queue (GPU; N=2048 5 seeds is slow on CPU)
Pre-reg: preregs/2026-05-27_saad_solla_v8_n2048.md
Parent: wave14_saddle_solla_v7_n4096 (TIMEOUT), wave14_saddle_cascade_plateau_v3 (HARD_PASS N=1024)
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import os
import time
from pathlib import Path
from typing import Dict, List

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load Kovacs base infrastructure
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_base_spec = importlib.util.spec_from_file_location("base_v8", _base_path)
base = importlib.util.module_from_spec(_base_spec)
_base_spec.loader.exec_module(base)
pa = base.pa

# Reuse v3 helper functions (cascade logic and threshold formula)
_v3_path = REPO / "experiments" / "exp_wave14_saddle_cascade_plateau_v3.py"
_v3_spec = importlib.util.spec_from_file_location("v3_cascade_v8", _v3_path)
v3_mod = importlib.util.module_from_spec(_v3_spec)
_v3_spec.loader.exec_module(v3_mod)

build_mixed_corpus = v3_mod.build_mixed_corpus
pearson_r2 = v3_mod.pearson_r2
linear_fit_residuals = v3_mod.linear_fit_residuals
run_one_cell = v3_mod.run_one_cell
compute_verdict = v3_mod.compute_verdict

# PRODUCTION CONFIG (PROT-018 binding: _n2048 suffix -> N = 2048)
N = 2048          # PRODUCTION N -- PROT-018 contract
N_SMOKE = 512     # smoke-only gate scale
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

# Pre-registered thresholds (IDENTICAL to v3/v7)
LINEAR_R2_PASS_THRESHOLD = 0.85
LINEAR_R2_FAIL_THRESHOLD = 0.95
DEVIATION_PASS_THRESHOLD = 0.08
DEVIATION_FAIL_THRESHOLD = 0.04
N_SEEDS_HARDPASS_FOR_OVERALL = 4
N_SEEDS_HARDFAIL_FOR_OVERALL = 4


def get_output_dir(default_name: str = "saad_solla_v8_n2048") -> Path:
    # HDLAB_EXP_NAME env-var honored (PROT-018 / n-mismatch eradication 2026-05-27):
    # the runner sets HDLAB_EXP_NAME to the queue anchor name. Honoring it ensures
    # the script writes to data/exp_<anchor>/ even when called under a different
    # anchor name (rerun-as, allow-duplicate, manual ad-hoc invocation).
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: PROT-018 structural check -- N must be exactly 2048
    assert N == 2048, f"PROT-018: production N must be 2048; got {N}"

    # Self-test 2: pearson_r2 on linear data -> 1.0
    r2_lin = pearson_r2([0.0, 1.0, 2.0, 3.0], [0.0, 2.0, 4.0, 6.0])
    assert abs(r2_lin - 1.0) < 1e-6, f"pearson_r2 on linear must be 1.0; got {r2_lin}"

    # Self-test 3: cascade data -> correctly identifies HARD-PASS
    cascade_fs = [0.0, 0.25, 0.5, 0.75, 1.0]
    cascade_rets = [0.60, 0.62, 0.94, 0.94, 0.94]
    r2_cas = pearson_r2(cascade_fs, cascade_rets)
    assert r2_cas < 0.80, f"cascade data R^2 should be < 0.80; got {r2_cas}"
    _, max_dev_cas, _ = linear_fit_residuals(cascade_fs, cascade_rets)
    assert max_dev_cas >= 0.10, f"cascade max_dev should be >= 0.10; got {max_dev_cas}"

    # Self-test 4: run_one_cell at smoke scale
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    result = run_one_cell(
        seed=17, f=0.5, N=N_SMOKE, batch_size=BATCH_SIZE_SMOKE,
        n_epochs=EPOCHS_SMOKE, phase_a_epochs=PHASE_A_EPOCHS_SMOKE,
        n_bytes=BYTES_SMOKE, device=device
    )
    assert "retention_A" in result, f"run_one_cell missing 'retention_A': {list(result.keys())}"
    ret = result["retention_A"]
    assert isinstance(ret, float) and 0.0 < ret <= 1.0, f"retention_A out of (0,1]: {ret}"

    print(f"[selftest] v8 PASSED: N=2048 assertion OK, pearson_r2 OK, "
          f"cascade HARD-PASS logic OK, smoke retention={ret:.4f}", flush=True)


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

    n = N_SMOKE if smoke else N
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    f_sweep = F_SWEEP_SMOKE if smoke else F_SWEEP_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE
    epochs = EPOCHS_SMOKE if smoke else EPOCHS
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS
    n_bytes = BYTES_SMOKE if smoke else BYTES

    mode_str = "SMOKE" if smoke else "FULL"
    # HDLAB_EXP_NAME-aware exp_name (n-mismatch eradication 2026-05-27): the queue
    # runner passes the actual anchor name via this env var. Falling back to the
    # literal default would re-introduce the v1->v2 cross-write hazard we are
    # eradicating.
    exp_name = os.environ.get("HDLAB_EXP_NAME", "saad_solla_v8_n2048")
    print(f"[run] {exp_name} {mode_str} N={n} seeds={seeds} device={device}", flush=True)
    if not smoke:
        assert n == 2048, f"FULL run must use N=2048; got {n}"

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
            f"HARD_PASS: {n_hardpass}/{len(seeds)} seeds HARD-PASS at N=2048. "
            f"Saddle-cascade discrete structure confirmed at N=2048. "
            f"Next step: N=4096 with longer timeout."
        )
    elif n_hardfail >= N_SEEDS_HARDFAIL_FOR_OVERALL:
        overall = "HARD_FAIL"
        overall_msg = (
            f"HARD_FAIL: {n_hardfail}/{len(seeds)} seeds HARD-FAIL at N=2048. "
            f"Discrete plateau does not persist above N=1024. "
            f"Finite-N artifact confirmed; Saad-Solla framework not general."
        )
    else:
        overall = "MIDDLE_BAND"
        overall_msg = (
            f"MIDDLE_BAND: {n_hardpass} HARD-PASS, {n_hardfail} HARD-FAIL, "
            f"{n_middle} MIDDLE at N=2048. Inconclusive at stepping-stone scale."
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
            "seeds": list(seeds),
            "n_hardpass": n_hardpass,
            "n_hardfail": n_hardfail,
            "n_middle": n_middle,
            "seed_verdicts": {str(s): sv for s, sv in seed_verdicts.items()},
            "f_sweep": list(f_sweep),
        },
        "config": {
            "mode": mode_str,
            "N_production": N,
            "N_run": n,
            "seeds": list(seeds),
            "f_sweep": list(f_sweep),
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
                        help="Smoke-gate run at N=512")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
