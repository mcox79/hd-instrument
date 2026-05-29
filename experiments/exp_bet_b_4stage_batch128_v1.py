"""Bet-B 4-stage CL rehab v_batch: 2x batch_size (ret_A bar closure attempt, axis-2).

CONTEXT:
  bet_b_n8192_4stage_v2 FULL FOURSTAGE_MIDDLE_BAND (N=8192, 5-seed mean ret_A=0.745).
    - Confirmed: smoke->FULL gap of -0.103 on ret_A (first direct observation).
    - Mechanism ceiling is NOT N-limited (v189 N=1024 matches v239 N=8192 within +/-0.005).
    - 4-stage CL row stays 🟡 PARTIAL (ret_A < 0.80 HP threshold).
  bet_b_4stage_rehab_epochs_v3 (pending GPU): axis-1 rehab (phase_a_epochs=16).

REHAB AXIS-2 (from strategy routing note 4stage_script_path_hygiene_2026-05-27):
  Increase Phase-A batch_size from 64 to 128 (2x gradient signal per Phase-A pass).
  Rationale: larger batch during Phase-A training provides stronger gradient signal per
  update, potentially reducing ret_A interference from subsequent phases.
  Predicted lift: +0.02 to +0.05 per routing note (similar uncertainty band as axis-1).
  Risk: independent from axis-1 (epochs change vs batch-size change); both are
  hypothesis-generating probes, neither is guaranteed to close 0.745->0.80 gap.

This is AXIS-2, complementary to bet_b_4stage_rehab_epochs_v3 AXIS-1. Both probes are
independent; results inform which rehab direction (if any) lifts ret_A above 0.80.

PRE-REGISTERED BANDS:
  HARD_PASS: mean ret_A >= 0.80 AND mean ret_B >= 0.70 AND mean ret_C >= 0.70
    across 5 seeds at N=8192.
  HARD_FAIL: mean ret_A <= 0.50
  MIDDLE_BAND: mean ret_A in (0.50, 0.80)
    -> If mean ret_A in (0.74, 0.80): slight improvement from v2 (0.745), below threshold.
    -> If mean ret_A >= 0.80: HARD_PASS; 2x batch_size improves Phase-A gradient signal.

Walk-back: smoke ret_A expected near 0.74-0.85 at N=1024 (smoke->FULL gap ~-0.103 known).
If smoke ret_A > 0.85 (within 6% of HP threshold after smoke->FULL correction),
double seeds to 10 before ship. Running 5 seeds first.

FORMULA SELF-TESTS:
  1. retention = bpc_baseline / bpc_after_D. For perfect retention: ratio = 1.0.
  2. PASS verdict fires when retention_A=0.82, retention_B=0.72, retention_C=0.72.
  3. HARD_FAIL fires when retention_A=0.48.
  4. BATCH_SIZE_FULL = 128 (double of v1/v2 = 64). N_FULL = 8192.
  5. SEEDS_FULL has 5 entries.

TIMEOUT ESTIMATE:
  v2 full GPU elapsed approx 1020s (N=8192, 5 seeds, batch_size=64).
  v_batch batch_size=128 (2x) with same seeds=5 and same epochs=8.
  Batch size increase reduces iterations per epoch by 2x (same data, larger batches).
  This REDUCES wall time: est ~510s for same epochs at 2x batch.
  Safety: ceil(1.5 * 510) = 765 -> 900s. Flag: <2h, no extra visibility flag needed.
  Note: batch_size affects Phase-A Hebbian update granularity; actual timing depends
  on torch batched-outer-product dispatch. Use conservative 1200s.

N-suffix: no _nN suffix; production N = 8192 (PROT-018: stated explicitly; N_FULL = 8192 below).
Queue: overnight_queue (GPU; N=8192 Hebbian matrix ops, 5 seeds)
Pre-reg: preregs/2026-05-27_bet_b_4stage_batch128_v1.md (filed concurrent with ship)
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

# Load patched v1 (has HDLAB_EXP_NAME output-path fix + all base functions)
_v1_path = REPO / "experiments" / "exp_bet_b_n8192_4stage_v1.py"
_v1_spec = importlib.util.spec_from_file_location("bet_b_4stage_v1_base", _v1_path)
v1_mod = importlib.util.module_from_spec(_v1_spec)
_v1_spec.loader.exec_module(v1_mod)

run_one_seed = v1_mod.run_one_seed
compute_verdict = v1_mod.compute_verdict

# Bit-precision helper (BE-1 plumbing; fp32 default = no-op = backwards compat).
sys.path.insert(0, str(REPO / "experiments"))
import _bit_precision as bp  # noqa: E402


def _wrap_train_with_precision(train_fn, precision: str):
    """Wrap train_w_with_replay so the returned W is quantized to `precision`.

    Quantizes AFTER the training step (= substrate storage) but BEFORE returning
    to the caller, who immediately uses W for evaluate_bpc (= retrieval).
    """
    def wrapped(*args, **kwargs):
        W, pool_v, pool_l, pool_u = train_fn(*args, **kwargs)
        if precision != "fp32":
            W = bp.quantize_roundtrip(W, precision)
        return W, pool_v, pool_l, pool_u
    return wrapped

# PRODUCTION CONFIG -- AXIS-2 REHAB: double batch_size
N_FULL = 8192            # PROT-018: no _nN suffix; production N stated explicitly
N_SMOKE = 1024
BATCH_SIZE_FULL = 128    # axis-2 rehab: 2x the v1/v2 baseline of 64
BATCH_SIZE_SMOKE = 64    # proportionally doubled in smoke too
EPOCHS_FULL = 5
EPOCHS_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8  # UNCHANGED from v1/v2 (axis-1 epochs change is in epochs_v3)
PHASE_A_EPOCHS_SMOKE = 1
BYTES_FULL = 200_000
BYTES_SMOKE = 50_000
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

# Pre-registered thresholds (same as v2 / routing note bands)
PASS_RET_A = 0.80
PASS_RET_B = 0.70
PASS_RET_C = 0.70
FAIL_RET_A = 0.50


def get_output_dir(default_name: str = "bet_b_4stage_batch128_v1") -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    d = REPO / "data" / f"exp_{name}"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    # PROT-018 explicit: N_FULL must be 8192 (no _nN suffix)
    assert N_FULL == 8192, f"PROT-018: N_FULL must be 8192; got {N_FULL}"

    # Self-test 1: axis-2 batch_size doubled from v1/v2
    assert BATCH_SIZE_FULL == 128, f"Rehab axis-2: BATCH_SIZE_FULL must be 128; got {BATCH_SIZE_FULL}"
    assert BATCH_SIZE_FULL == 2 * 64, "BATCH_SIZE_FULL must be 2x the v1/v2 value (64)"
    assert PHASE_A_EPOCHS_FULL == 8, \
        f"Axis-2: PHASE_A_EPOCHS_FULL should be 8 (unchanged); got {PHASE_A_EPOCHS_FULL}"

    # Self-test 2: v1 verdict logic callable
    assert callable(compute_verdict), "compute_verdict not callable from v1_mod"

    # Self-test 3: run one smoke seed at tiny N
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    cfg_smoke = {
        "mode": "smoke", "N": 256, "batch_size": 64, "epochs": 1,
        "phase_a_epochs": 1, "bytes_per_corpus": 5_000,
        "seeds": [17], "pass_ret_A": PASS_RET_A, "pass_ret_B": PASS_RET_B,
        "pass_ret_C": PASS_RET_C, "fail_ret_A": FAIL_RET_A
    }
    result = run_one_seed(17, cfg_smoke, device)
    assert "retention_A" in result, f"missing retention_A: {list(result.keys())}"
    ret_A = result["retention_A"]
    assert isinstance(ret_A, float) and 0.0 < ret_A <= 1.0, f"retention_A out of (0,1]: {ret_A}"

    # Self-test 4: output-path parameterization via HDLAB_EXP_NAME
    import os as _os
    _orig = _os.environ.get("HDLAB_EXP_NAME")
    _os.environ["HDLAB_EXP_NAME"] = "test_batch128_path_check"
    _test_dir = get_output_dir()
    if _orig is None:
        del _os.environ["HDLAB_EXP_NAME"]
    else:
        _os.environ["HDLAB_EXP_NAME"] = _orig
    assert _test_dir.name == "exp_test_batch128_path_check", \
        f"get_output_dir ignores HDLAB_EXP_NAME: got {_test_dir.name}"
    _test_dir.rmdir()

    # Self-test 5: OOM pre-check at N=8192
    oom_bytes = 8192 * 8192 * 4 * 4
    assert oom_bytes < 6e9, f"OOM pre-check failed: {oom_bytes:.2e} >= 6GB"

    print(f"[selftest] bet_b_4stage_batch128_v1 PASSED: "
          f"N_FULL={N_FULL}, BATCH_SIZE_FULL={BATCH_SIZE_FULL}, "
          f"smoke ret_A={ret_A:.4f}, output-path OK, OOM={oom_bytes:.2e}", flush=True)


_instrumentation_selftest()


def run(smoke: bool = False, precision: str = "fp32") -> None:
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
        "bit_precision": precision,
    }
    exp_name = os.environ.get("HDLAB_EXP_NAME", "bet_b_4stage_batch128_v1")
    print(f"[run] {exp_name} mode={config['mode']} N={config['N']} "
          f"batch_size={config['batch_size']} phase_a_epochs={config['phase_a_epochs']} "
          f"device={device} precision={precision}", flush=True)

    if not smoke:
        assert config["N"] == 8192, f"FULL run must use N=8192; got {config['N']}"
        assert config["batch_size"] == 128, \
            f"Rehab axis-2: FULL batch_size must be 128; got {config['batch_size']}"

    # Install precision-aware train_w_with_replay if needed.
    # The 4stage v1 module references its own `base` (Kovacs); patch THAT one.
    # fp32 path leaves the original function untouched (byte-exact backwards compat).
    _orig_train = v1_mod.base.train_w_with_replay
    try:
        if precision != "fp32":
            v1_mod.base.train_w_with_replay = _wrap_train_with_precision(
                _orig_train, precision)

        per_seed = {}
        for seed in config["seeds"]:
            r = run_one_seed(seed, config, device)
            per_seed[str(seed)] = r
            print(f"  seed={seed}: ret_A={r['retention_A']:.3f} "
                  f"ret_B={r['retention_B']:.3f} ret_C={r['retention_C']:.3f}",
                  flush=True)
    finally:
        v1_mod.base.train_w_with_replay = _orig_train

    summary = {"per_seed": per_seed}
    verdict, msg = compute_verdict(summary)

    elapsed = round(time.time() - t0, 2)
    print(f"\n[result] {verdict}: {msg}", flush=True)
    print(f"[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {msg}", flush=True)

    precision_md = bp.precision_metadata(config["N"] * config["N"], precision)

    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
        **precision_md,
    }
    mpath = get_output_dir(exp_name) / "metrics.json"
    tmp = mpath.with_suffix(".json.tmp")
    with open(tmp, "w") as fh:
        json.dump(metrics, fh, indent=2, default=str)
    os.replace(tmp, mpath)
    print(f"[exp] metrics -> {mpath}", flush=True)
    print(f"[precision] {precision} W_bytes={precision_md['precision_memory_bytes']} "
          f"baseline={precision_md['precision_baseline_bytes']} "
          f"ratio={precision_md['precision_compression_ratio']}x", flush=True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    parser.add_argument("--bit-precision", dest="bit_precision", default="fp32",
                        choices=list(bp.VALID_PRECISIONS),
                        help="W-matrix precision for BE-1 sweep (default fp32 = no-op)")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke, precision=args.bit_precision)
