"""Bet-B 4-stage continual learning at N=8192: strategic Killer-T1 depth probe.

CONTEXT:
  wave14_betB_4stage_continual_v1: FOURSTAGE_MIDDLE_BAND at N=4096
    retention_A=0.740 (threshold 0.80), retention_B=0.854, retention_C=0.798.
    Phase-A retention MISSES by 0.060. N-scaling toward mean-field limit may improve retention.
  This probe tests N=8192 (2x larger) to determine if retention_A crosses 0.80.

HYPOTHESIS:
  The mean-field theory (N->inf) predicts retention to approach a fixed point
  that depends only on M/N and replay fraction. At N=8192, variance from finite-N
  fluctuations decreases, and the mean should either stay near 0.740 (genuine mechanism
  limit) or improve toward 0.80 (finite-N effect).

STRATEGIC VALUE:
  cap_map KILLER T1: "True continual learning at production scale" is PARTIAL at N=4096.
  If N=8192 moves retention_A >= 0.80, the capability claim upgrades from PARTIAL to PASS.
  If N=8192 still misses, we have confirmed the mechanism ceiling is genuine (not N-limited).

OOM PRE-CHECK:
  W matrix at N=8192: 8192^2 * 4 bytes = 268MB.
  Multiple W copies: up to 4 (W_A, W_AB, W_ABC, W_ABCD) = 1.07GB.
  Pool tensors at N=8192: approximately 64KB * 4 pools = 256KB.
  TOTAL peak: ~1.1GB. Well under 6GB GPU headroom. Ship allowed.

PRE-REGISTERED BANDS (envelope extension of v1):
  HARD-PASS: mean retention_A >= 0.80 AND mean retention_B >= 0.70 AND mean retention_C >= 0.70
    across 5 seeds at N=8192. Mechanism confirms at full production scale.
  HARD-FAIL: mean retention_A <= 0.50 (catastrophic collapse, not just below threshold).
  MIDDLE-BAND: retention_A in (0.50, 0.80) -- same as v1 result range.
    -> If retention_A in (0.74, 0.80): slight improvement, still below threshold.
    -> If retention_A <= 0.74: N-scaling does not help; mechanism is genuinely bounded.
  NOTE: no prior N=8192 empirical anchor. Bands widened per calibration-probe policy:
    "no prior N=8192 anchor; HARD-PASS set at theory prediction (0.80 threshold)."
    HARD-FAIL at 0.50 is 38% below current observation (0.740).

FORMULA SELF-TESTS:
  1. retention = bpc_baseline / bpc_after_D. For perfect retention: ratio = 1.0.
  2. retention = 0.740 if bpc_A_baseline=3.5 and bpc_A_after_D=4.73 (v1 reference).
  3. PASS verdict fires when retention_A=0.82, retention_B=0.72, retention_C=0.72.
  4. HARD_FAIL fires when retention_A=0.48.

Timeout estimate:
  v1 N=4096 elapsed 221s (5 seeds). N=8192 scaling (linear in N for Hebbian outer-product):
  timeout = ceil(1.5 * 221 * (8192/4096)^1.5 * 1) = ceil(1.5 * 221 * 2.83) = ceil(938) = 1200s
  Adding 20% margin for 5 seeds: already computed per 5 seeds, use: 1200s.
  All good -- under 4h limit.

Queue: overnight_queue (GPU: N=8192 Hebbian matrix ops, 5 seeds)
Pre-reg: preregs/2026-05-27_bet_b_n8192_4stage_v1.md
Parent: wave14_betB_4stage_continual_v1_2026-05-24 (N=4096 MIDDLE_BAND, ret_A=0.740)
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

from verification import oracle  # noqa: E402

# Load Kovacs base
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_base_spec = importlib.util.spec_from_file_location("base_4stage_n8192", _base_path)
base = importlib.util.module_from_spec(_base_spec)
_base_spec.loader.exec_module(base)
pa = base.pa

# Load v1 4-stage to reuse run_one_seed and corpus infrastructure
_v1_path = REPO / "experiments" / "exp_wave14_betB_4stage_continual_v1.py"
_v1_spec = importlib.util.spec_from_file_location("fourStageV1", _v1_path)
v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1_mod)

run_one_seed = v1_mod.run_one_seed
compute_verdict = v1_mod.compute_verdict
load_corpus_D = v1_mod.load_corpus_D

# PRODUCTION CONFIG -- N=8192
N_FULL = 8192
N_SMOKE = 1024
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200_000
BYTES_SMOKE = 50_000
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
PASS_RET_A = 0.80
PASS_RET_B = 0.70
PASS_RET_C = 0.70
FAIL_RET_A = 0.50


def get_output_dir(default_name: str = "bet_b_n8192_4stage_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # Self-test 1: verdict compute on synthetic data
    v1_mod.self_test_verdict()

    # Self-test 2: run_one_seed at smoke scale returns valid retention
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg_smoke = {
        "mode": "smoke", "N": 512, "batch_size": 16, "epochs": 1,
        "phase_a_epochs": 1, "bytes_per_corpus": 10_000,
        "seeds": [17], "pass_ret_A": 0.80, "pass_ret_B": 0.70,
        "pass_ret_C": 0.70, "fail_ret_A": 0.50
    }
    result = run_one_seed(17, cfg_smoke, device)
    assert "retention_A" in result, f"missing retention_A: {list(result.keys())}"
    ret_A = result["retention_A"]
    assert isinstance(ret_A, float) and 0.0 < ret_A <= 1.0, f"retention_A out of (0,1]: {ret_A}"

    # Self-test 3: oracle assertions callable
    oracle.assert_in_range("retention_A_selftest", ret_A, (0.0, 1.01))

    # Self-test 4: OOM pre-check
    # W matrix at N=8192: 8192^2 * 4 bytes = 268MB. 4 copies = 1.07GB < 6GB.
    oom_bytes = 8192 * 8192 * 4 * 4
    assert oom_bytes < 6e9, f"OOM pre-check failed: {oom_bytes:.2e} >= 6GB"

    # Self-test 5: output-path parameterization -- HDLAB_EXP_NAME must be honored
    import os as _os
    _orig = _os.environ.get("HDLAB_EXP_NAME")
    _os.environ["HDLAB_EXP_NAME"] = "test_anchor_xyz"
    _test_dir = get_output_dir()
    if _orig is None:
        del _os.environ["HDLAB_EXP_NAME"]
    else:
        _os.environ["HDLAB_EXP_NAME"] = _orig
    assert _test_dir.name == "exp_test_anchor_xyz", \
        f"get_output_dir ignores HDLAB_EXP_NAME: got {_test_dir.name}"
    _test_dir.rmdir()  # cleanup the test dir

    print(f"[selftest] bet_b_n8192_4stage PASSED: verdict_logic OK, "
          f"smoke retention_A={ret_A:.4f}, OOM check {oom_bytes:.2e} bytes, "
          f"output-path-parameterization OK", flush=True)


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
    exp_name = os.environ.get("HDLAB_EXP_NAME", "bet_b_n8192_4stage_v1")
    print(f"[run] {exp_name} mode={config['mode']} N={config['N']} device={device}", flush=True)

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
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
