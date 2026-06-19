"""ICL saturation at smaller N=2048 - test N-dependence of saturation point.

Pre-reg: preregs/2026-05-21_wave14yq_icl_smaller_N.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import math
import os
import sys
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(event_type, **fields):
        pass


_yw_path = REPO / "experiments" / "exp_wave14w_icl_extended.py"
spec_yw = importlib.util.spec_from_file_location("yw", _yw_path)
yw = importlib.util.module_from_spec(spec_yw)
spec_yw.loader.exec_module(yw)


N_FULL = 2048  # smaller than yw's 4096
N_SMOKE = 512
ICTX_FULL = [1024, 4096, 16384, 32768]
ICTX_SMOKE = [128, 512]
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]
MAX_EPOCHS_FULL = 10
MAX_EPOCHS_SMOKE = 1
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 64
TRAIN_A_BYTES_SMOKE = 4000
TEST_B_CAP_FULL = 16_000
TEST_B_CAP_SMOKE = 1500
ALPHA = 1.0


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    if not required.issubset(d.keys()):
        raise ValueError(f"missing: {required - set(d.keys())}")


def compute_verdict(summary):
    """Reuse yw's verdict logic but rename labels to ICL_SMALLER_N_*."""
    verdict, msg = yw.compute_verdict(summary)
    # Rename ICL_EXTENDED_* to ICL_SMALLER_N_*
    verdict_renamed = verdict.replace("ICL_EXTENDED_", "ICL_SMALLER_N_")
    if verdict.startswith("ICL_POOL_COLLAPSE_") or verdict.startswith("ICL_CORPUS_"):
        verdict_renamed = verdict.replace("ICL_", "ICL_SMALLER_N_")
    return (verdict_renamed, msg)


def self_test_verdict():
    cases = [
        ({"ictx_list": [1024, 4096, 16384, 32768],
          "mean_gain": [1.0, 1.4, 1.7, 2.0],
          "std_gain": [0.05, 0.05, 0.05, 0.05],
          "mean_entropy_per_ictx": [2.0, 2.5, 2.7, 3.0],
          "distinct_chunks_floor_ok": True},
         "ICL_SMALLER_N_NO_SATURATION"),
        ({"ictx_list": [1024, 4096, 16384, 32768],
          "mean_gain": [1.0, 1.4, 1.43, 1.46],
          "std_gain": [0.01, 0.01, 0.01, 0.01],
          "mean_entropy_per_ictx": [2.0, 2.5, 2.7, 3.0],
          "distinct_chunks_floor_ok": True},
         "ICL_SMALLER_N_SOFT_SATURATION"),
        ({}, "ICL_SMALLER_N_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_full(smoke):
    return yw.run_full(smoke)  # reuse yw's run_full structure


def run_experiment(smoke):
    # yw uses module-level constants for N, ICTX, seeds. Override them.
    import importlib
    importlib.reload(yw)
    yw.N_FULL = N_FULL
    yw.N_SMOKE = N_SMOKE
    yw.ICTX_FULL = ICTX_FULL
    yw.ICTX_SMOKE = ICTX_SMOKE
    yw.SEEDS_FULL = SEEDS_FULL
    yw.SEEDS_SMOKE = SEEDS_SMOKE
    yw.MAX_EPOCHS_FULL = MAX_EPOCHS_FULL
    yw.MAX_EPOCHS_SMOKE = MAX_EPOCHS_SMOKE
    yw.TRAIN_A_BYTES_SMOKE = TRAIN_A_BYTES_SMOKE
    yw.TEST_B_CAP_FULL = TEST_B_CAP_FULL
    yw.TEST_B_CAP_SMOKE = TEST_B_CAP_SMOKE

    summary, verdict, msg, elapsed, per_seed = yw.run_full(smoke=smoke)
    verdict_renamed = verdict.replace("ICL_EXTENDED_", "ICL_SMALLER_N_")
    if verdict.startswith("ICL_POOL_COLLAPSE_") or verdict.startswith("ICL_CORPUS_"):
        verdict_renamed = verdict.replace("ICL_", "ICL_SMALLER_N_")
    return summary, verdict_renamed, msg, elapsed, per_seed


def write_metrics(out_dir, summary, verdict, msg, elapsed, per_seed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config, "per_seed": per_seed}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14yq_icl_smaller_N_smoke")
    log_event("experiment_started", name="wave14yq_icl_smaller_N", mode="smoke")
    summary, verdict, msg, elapsed, per_seed = run_experiment(smoke=True)
    rel_bpc = per_seed[0]["per_ictx"][ICTX_SMOKE[-1]]["rel_bpc"]
    oracle.assert_in_range("rel_bpc_smoke", rel_bpc, (0.5, 8.0))
    write_metrics(out_dir, summary, verdict, msg, elapsed, per_seed, {
        "mode": "smoke", "n_dim": N_SMOKE, "ictx": ICTX_SMOKE, "seeds": SEEDS_SMOKE,
        "max_epochs": MAX_EPOCHS_SMOKE, "alpha": ALPHA,
    })
    log_event("experiment_outcome", name="wave14yq_icl_smaller_N",
              verdict=verdict, verdict_msg=msg, elapsed_s=elapsed, mode="smoke")
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yq_icl_smaller_N")
    log_event("experiment_started", name="wave14yq_icl_smaller_N", mode="full")
    summary, verdict, msg, elapsed, per_seed = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, per_seed, {
        "mode": "full", "n_dim": N_FULL, "ictx": ICTX_FULL, "seeds": SEEDS_FULL,
        "max_epochs": MAX_EPOCHS_FULL, "alpha": ALPHA,
    })
    log_event("experiment_outcome", name="wave14yq_icl_smaller_N",
              verdict=verdict, verdict_msg=msg, elapsed_s=elapsed, mode="full")
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
