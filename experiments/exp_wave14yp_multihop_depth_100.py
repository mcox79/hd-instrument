"""Multi-hop reasoning at depth=100 - test extreme depth envelope.

Pre-reg: preregs/2026-05-21_wave14yp_multihop_depth_100.md
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


_v3_path = REPO / "experiments" / "exp_wave14t_multihop_v3.py"
spec_v3 = importlib.util.spec_from_file_location("multihop_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec_v3)
spec_v3.loader.exec_module(v3)


N_FULL = 4096
N_SMOKE = 512
NUM_ENTITIES_FULL = 250
NUM_ENTITIES_SMOKE = 50
NUM_RELATIONS_FULL = 20
NUM_RELATIONS_SMOKE = 5
NUM_FACTS_FULL = 200
NUM_FACTS_SMOKE = 30
HOP_DEPTHS_FULL = [1, 25, 50, 100]
HOP_DEPTHS_SMOKE = [1, 10, 25]
N_TRIALS_FULL = 30
N_TRIALS_SMOKE = 5
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]

PASS_ACC_DEEP = 0.05


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
    per_depth = summary.get("per_depth_mean_acc")
    if not per_depth:
        return ("MULTIHOP_DEPTH_INCONCLUSIVE", "Missing.")
    pdm = {int(k): float(v) for k, v in per_depth.items()}
    depths_sorted = sorted(pdm.keys())
    max_depth = depths_sorted[-1]
    if pdm.get(max_depth, 0.0) >= PASS_ACC_DEEP:
        return (f"MULTIHOP_DEPTH_{max_depth}_HOLDS",
                f"acc_{max_depth} = {pdm[max_depth]:.3f} >= {PASS_ACC_DEEP}. "
                f"Multi-hop reasoning extends to depth {max_depth}. Per-depth: " +
                ", ".join(f"d{d}={pdm[d]:.3f}" for d in depths_sorted))
    decay_at = next((d for d in depths_sorted if pdm[d] < PASS_ACC_DEEP), None)
    return (f"MULTIHOP_DEPTH_DECAYS_AT_{decay_at}",
            f"First depth where acc < {PASS_ACC_DEEP}: depth={decay_at}. "
            f"Per-depth: " + ", ".join(f"d{d}={pdm[d]:.3f}" for d in depths_sorted))


def self_test_verdict():
    cases = [
        ({"per_depth_mean_acc": {1: 0.95, 25: 0.5, 50: 0.2, 100: 0.08}},
         "MULTIHOP_DEPTH_100_HOLDS"),
        ({"per_depth_mean_acc": {1: 0.95, 25: 0.5, 50: 0.2, 100: 0.02}},
         "MULTIHOP_DEPTH_DECAYS_AT_100"),
        ({"per_depth_mean_acc": {1: 0.95, 25: 0.5, 50: 0.04, 100: 0.01}},
         "MULTIHOP_DEPTH_DECAYS_AT_50"),
        ({}, "MULTIHOP_DEPTH_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "num_entities": NUM_ENTITIES_SMOKE if smoke else NUM_ENTITIES_FULL,
        "num_relations": NUM_RELATIONS_SMOKE if smoke else NUM_RELATIONS_FULL,
        "num_facts": NUM_FACTS_SMOKE if smoke else NUM_FACTS_FULL,
        "hop_depths": HOP_DEPTHS_SMOKE if smoke else HOP_DEPTHS_FULL,
        "n_trials": N_TRIALS_SMOKE if smoke else N_TRIALS_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
    }
    print(f"[config] {config}", flush=True)

    per_seed_runs = []
    for seed in config["seeds"]:
        r = v3.run_one_seed(seed, config["hop_depths"], config["n_trials"], config, device)
        per_seed_runs.append(r)
        accs = " ".join(f"d{d}={r['by_depth'][d]:.3f}" for d in config["hop_depths"])
        print(f"  seed={seed}  {accs}", flush=True)

    per_depth_mean = {}
    for d in config["hop_depths"]:
        vals = [r["by_depth"][d] for r in per_seed_runs]
        per_depth_mean[d] = sum(vals) / len(vals)

    summary = {"per_depth_mean_acc": {str(d): per_depth_mean[d] for d in config["hop_depths"]}}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14yp_multihop_depth_100_smoke")
    log_event("experiment_started", name="wave14yp_multihop_depth_100", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    acc_1 = float(summary["per_depth_mean_acc"].get("1", 0.0))
    oracle.assert_baseline_high("multihop_depth_smoke_acc1", acc_1, 0.50)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yp_multihop_depth_100",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14yp_multihop_depth_100")
    log_event("experiment_started", name="wave14yp_multihop_depth_100", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14yp_multihop_depth_100",
              mode="full", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
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
