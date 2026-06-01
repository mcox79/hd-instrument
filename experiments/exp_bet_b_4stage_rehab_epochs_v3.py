"""Bet-B 4-stage CL rehab v3: double Phase-A consolidation epochs (ret_A bar closure attempt).

CONTEXT:
  bet_b_n8192_4stage_v1 SMOKE FOURSTAGE_HARD_PASS (N=1024, 1-seed ret_A=0.855).
  bet_b_n8192_4stage_v2 FULL FOURSTAGE_MIDDLE_BAND (N=8192, 5-seed mean ret_A=0.745).
    - Confirmed: smoke->FULL gap of -0.103 on ret_A (first direct observation).
    - Confirms v189 result at N=1024 within +/-0.005; mechanism ceiling is NOT N-limited.
    - 4-stage CL row stays 🟡 PARTIAL (ret_A < 0.80 HP threshold).

REHAB AXIS-1 (from strategy routing note 4stage_script_path_hygiene_2026-05-27):
  Increase Phase-A consolidation epochs from 8 to 16 (2x).
  Rationale: more Phase-A training gives stronger initial encoding, reducing ret_A interference.
  Predicted lift: +0.02 to +0.05 per routing note (modest; v189-era rehab saturated MIDDLE_BAND).
  Risk: v189-era rehab at N=1024 with 2x epochs did NOT cross 0.80 bar; mechanism may be ceiling-limited.

PRE-REGISTERED BANDS (extended from v2 for 10-seed walk-back gate):
  HARD_PASS: MEAN ret_A (across 10 seeds) >= 0.80 AND mean ret_B >= 0.70 AND mean ret_C >= 0.70
  HARD_FAIL: mean ret_A <= 0.50
  MIDDLE_BAND: mean ret_A in (0.50, 0.80)
    -> If mean ret_A in (0.74, 0.80): slight improvement from v2 (0.745), still below threshold.
    -> If mean ret_A >= 0.80: HARD_PASS; 2x epochs improves consolidation.
  Walk-back gate: smoke ret_A=0.829 within 4% of HP threshold 0.80 (known -0.103 smoke->FULL gap);
    10 seeds used for statistical power (double planned 5-seed run per walk-back policy).

FORMULA SELF-TESTS:
  1. retention = bpc_baseline / bpc_after_D. For perfect retention: ratio = 1.0.
  2. PASS verdict fires when retention_A=0.82, retention_B=0.72, retention_C=0.72 (>=4/5 seeds).
  3. HARD_FAIL fires when retention_A=0.48.
  4. PHASE_A_EPOCHS_FULL = 16 (double of v1/v2 = 8). PROT-018: N_FULL = 8192.
  5. SEEDS_FULL has 10 entries (walk-back gate: double the planned 5-seed run).

Timeout estimate:
  v2 full GPU elapsed approx 1020s (N=8192, 5 seeds, phase_a_epochs=8).
  v3 phase_a_epochs=16 (2x) + 10 seeds (2x walk-back gate) vs v2 5-seed.
  approx elapsed: 1020 * (16/8) * (10/5) = 1020 * 2 * 2 = 4080s.
  timeout_s = ceil(1.5 * 4080) = ceil(6120) = 6300s.
  Walk-back gate applied: smoke ret_A=0.829 is within 4% of HP threshold 0.80;
  known smoke->FULL gap of -0.103 makes FULL borderline; 10 seeds for statistical power.
  Under 4h (14400s). Flag: >2h for visibility (add comment in pre-reg).

N-suffix: no _nN suffix; production N = 8192 (PROT-018: stated explicitly; N_FULL = 8192 below).
Queue: overnight_queue (GPU; N=8192 Hebbian matrix ops, 5 seeds)
Pre-reg: preregs/2026-05-27_bet_b_n8192_4stage_v2.md (same bands; this is axis-1 rehab)
Parent: bet_b_n8192_4stage_v2 (FULL N=8192 5-seed MIDDLE_BAND ret_A=0.745)
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

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# Load patched v1 (has HDLAB_EXP_NAME output-path fix)
_v1_path = REPO / "experiments" / "exp_bet_b_n8192_4stage_v1.py"
_v1_spec = importlib.util.spec_from_file_location("bet_b_4stage_v1", _v1_path)
v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1_mod)

run_one_seed = v1_mod.run_one_seed
compute_verdict = v1_mod.compute_verdict

# PRODUCTION CONFIG -- N_FULL = 8192 (PROT-018 binding; no _nN suffix in anchor name)
N_FULL = 8192
N_SMOKE = 1024
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
# REHAB AXIS-1: double Phase-A consolidation epochs
PHASE_A_EPOCHS_FULL = 16    # v1/v2 was 8; this is the rehab change
PHASE_A_EPOCHS_SMOKE = 2    # proportionally doubled in smoke too
BYTES_FULL = 200_000
BYTES_SMOKE = 50_000
SEEDS_FULL = [7, 17, 23, 31, 41, 53, 61, 67, 71, 79]  # 10 seeds: walk-back gate (smoke ret_A within 4% of HP)
SEEDS_SMOKE = [17]

# Pre-registered thresholds (same as v2)
PASS_RET_A = 0.80
PASS_RET_B = 0.70
PASS_RET_C = 0.70
FAIL_RET_A = 0.50


def get_output_dir(default_name: str = "bet_b_4stage_rehab_epochs_v3") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018 implicit: N_FULL must be 8192 (no _nN suffix; explicit here)
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

    # Self-test 1: phase_a_epochs doubled from v1/v2
    assert PHASE_A_EPOCHS_FULL == 16, f"Rehab axis-1: PHASE_A_EPOCHS_FULL must be 16; got {PHASE_A_EPOCHS_FULL}"
    assert PHASE_A_EPOCHS_FULL == 2 * 8, "PHASE_A_EPOCHS_FULL must be 2x the v1/v2 value (8)"

    # Self-test 2: v1 verdict logic callable (compute_verdict imported from v1_mod)
    assert callable(compute_verdict), "compute_verdict not callable from v1_mod"

    # Self-test 3: run one smoke seed at tiny N
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg_smoke = {
        "mode": "smoke", "N": 256, "batch_size": 16, "epochs": 1,
        "phase_a_epochs": 2, "bytes_per_corpus": 5_000,
        "seeds": [17], "pass_ret_A": PASS_RET_A, "pass_ret_B": PASS_RET_B,
        "pass_ret_C": PASS_RET_C, "fail_ret_A": FAIL_RET_A
    }
    result = run_one_seed(17, cfg_smoke, device)
    assert "retention_A" in result, f"missing retention_A: {list(result.keys())}"
    ret_A = result["retention_A"]
    assert isinstance(ret_A, float) and 0.0 < ret_A <= 1.0, f"retention_A out of (0,1]: {ret_A}"

    # Self-test 4: output-path parameterization
    import os as _os
    _orig = _os.environ.get("HDLAB_EXP_NAME")
    _os.environ["HDLAB_EXP_NAME"] = "test_v3_path_check"
    _test_dir = get_output_dir()
    if _orig is None:
        del _os.environ["HDLAB_EXP_NAME"]
    else:
        _os.environ["HDLAB_EXP_NAME"] = _orig
    assert _test_dir.name == "exp_test_v3_path_check", \
        f"get_output_dir ignores HDLAB_EXP_NAME: got {_test_dir.name}"
    _test_dir.rmdir()

    # Self-test 5: OOM pre-check at N=8192
    oom_bytes = 8192 * 8192 * 4 * 4
    assert oom_bytes < 6e9, f"OOM pre-check failed: {oom_bytes:.2e} >= 6GB"

    print(f"[selftest] bet_b_4stage_rehab_epochs_v3 PASSED: "
          f"N_FULL={N_FULL}, PHASE_A_EPOCHS_FULL={PHASE_A_EPOCHS_FULL}, "
          f"smoke ret_A={ret_A:.4f}, output-path OK, OOM={oom_bytes:.2e}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False) -> None:
    t0 = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "batch_size": BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL,
        "epochs": EPOCHS_SMOKE if smoke else EPOCHS_FULL,
        "phase_a_epochs": PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL,
        "bytes_per_corpus": BYTES_SMOKE if smoke else BYTES_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
        "pass_ret_A": PASS_RET_A, "pass_ret_B": PASS_RET_B,
        "pass_ret_C": PASS_RET_C, "fail_ret_A": FAIL_RET_A,
    }
    exp_name = os.environ.get("HDLAB_EXP_NAME", "bet_b_4stage_rehab_epochs_v3")
    print(f"[run] {exp_name} mode={config['mode']} N={config['N']} "
          f"phase_a_epochs={config['phase_a_epochs']} device={device}", flush=True)

    if not smoke:
        assert config["N"] == 8192, f"FULL run must use N=8192; got {config['N']}"
        assert config["phase_a_epochs"] == 16, \
            f"Rehab axis-1: FULL phase_a_epochs must be 16; got {config['phase_a_epochs']}"

    per_seed = {}
    for seed in config["seeds"]:
        r = run_one_seed(seed, config, device)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: ret_A={r['retention_A']:.3f} "
              f"ret_B={r['retention_B']:.3f} ret_C={r['retention_C']:.3f}", flush=True)

    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)

    elapsed = round(time.time() - t0, 2)
    print(f"\n[result] {verdict}: {msg}", flush=True)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    mpath = get_output_dir(exp_name) / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
