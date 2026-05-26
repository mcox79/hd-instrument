"""Multi-hop fact-base capacity envelope.

Follow-up to wave14t_multihop_v3 (verdict MULTIHOP_DECAY_AT_50 soft fail
because acc_1hop=0.93 < 0.98 at NUM_FACTS=100). The 1-hop floor depends
on the noise level in M, which scales with NUM_FACTS. This sweep finds
the largest NUM_FACTS at which both acc_1hop >= 0.98 AND acc_50hop > 0.10
hold simultaneously - the multi-hop capacity envelope for cap_map.

Sweep NUM_FACTS in {25, 50, 100, 200, 400}, depths {1, 10, 50}, 3 seeds.
Verdict reports the envelope width.

Pre-reg: preregs/2026-05-21_wave14u_multihop_envelope_v1.md
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
spec = importlib.util.spec_from_file_location("multihop_v3", _v3_path)
v3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v3)


N_FULL = 4096
N_SMOKE = 512
NUM_ENTITIES_FULL = 200
NUM_ENTITIES_SMOKE = 50
NUM_RELATIONS_FULL = 20
NUM_RELATIONS_SMOKE = 5
NUM_FACTS_FULL = [50, 100, 200, 400, 800]
NUM_FACTS_SMOKE = [20, 50]
HOP_DEPTHS_FULL = [1, 10, 50]
HOP_DEPTHS_SMOKE = [1, 10]
N_TRIALS_FULL = 50
N_TRIALS_SMOKE = 5
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]

PASS_ACC_1HOP = 0.98
PASS_ACC_50HOP = 0.10
PASS_RETENTION = 0.90
HIGH_SEED_VARIANCE = 0.10


def get_output_dir(default_name: str) -> Path:
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")
    if not d.get("verdict") or not d.get("verdict_msg"):
        raise ValueError("empty verdict")


def cell_passes(row: dict, max_depth: int) -> tuple[bool, list[str]]:
    """Check a per-NUM_FACTS row against the three criteria."""
    fails = []
    acc_1 = row.get("acc_by_depth", {}).get("1", 0.0)
    acc_max = row.get("acc_by_depth", {}).get(str(max_depth), 0.0)
    retention = row.get("retention_rate", 0.0)
    if acc_1 < PASS_ACC_1HOP:
        fails.append(f"acc_1hop={acc_1:.3f}<{PASS_ACC_1HOP}")
    if acc_max <= PASS_ACC_50HOP:
        fails.append(f"acc_{max_depth}hop={acc_max:.3f}<={PASS_ACC_50HOP}")
    if retention < PASS_RETENTION:
        fails.append(f"retention={retention:.3f}<{PASS_RETENTION}")
    return (len(fails) == 0, fails)


def compute_verdict(summary: dict) -> tuple[str, str]:
    by_nf = summary.get("by_num_facts")
    max_depth = summary.get("max_depth", 50)
    if not by_nf:
        return ("MULTIHOP_ENVELOPE_INCONCLUSIVE", "Missing per-NUM_FACTS data.")

    sorted_nfs = sorted(by_nf.keys(), key=int)
    smallest = int(sorted_nfs[0])
    smallest_row = by_nf[sorted_nfs[0]]

    # Variance warning
    variance_warnings = []
    for nf, row in by_nf.items():
        for depth_str, per_seed_vals in row.get("per_seed_acc_by_depth", {}).items():
            if len(per_seed_vals) > 1:
                m = sum(per_seed_vals) / len(per_seed_vals)
                var = sum((v - m) ** 2 for v in per_seed_vals) / (len(per_seed_vals) - 1)
                if math.sqrt(var) > HIGH_SEED_VARIANCE:
                    variance_warnings.append(
                        f"nf={nf} depth={depth_str} std={math.sqrt(var):.3f}")

    # Kill: smallest NUM_FACTS already fails acc_1hop
    smallest_acc_1 = smallest_row.get("acc_by_depth", {}).get("1", 0.0)
    if smallest_acc_1 < PASS_ACC_1HOP:
        return ("ENVELOPE_V2_NOT_REPLICATED",
                f"At NUM_FACTS={smallest}, acc_1hop={smallest_acc_1:.3f} < {PASS_ACC_1HOP}. "
                f"v2/v3 baseline not replicated even at low fact-base. Audit test setup.")

    # Kill: smallest NUM_FACTS already fails acc_max
    smallest_acc_max = smallest_row.get("acc_by_depth", {}).get(str(max_depth), 0.0)
    if smallest_acc_max <= PASS_ACC_50HOP:
        return ("ENVELOPE_NARROW_AT_LOW_NUM_FACTS",
                f"At NUM_FACTS={smallest}, acc_{max_depth}hop={smallest_acc_max:.3f} "
                f"<= {PASS_ACC_50HOP}. Multi-hop chains die even at smallest fact-base; "
                f"capability is bounded.")

    # Walk up the envelope: largest NUM_FACTS that passes all criteria
    largest_pass = None
    first_fail_nf = None
    first_fail_reason = None
    for nf_s in sorted_nfs:
        nf = int(nf_s)
        ok, fails = cell_passes(by_nf[nf_s], max_depth)
        if ok:
            largest_pass = nf
        else:
            first_fail_nf = nf
            first_fail_reason = "; ".join(fails)
            break

    var_note = ""
    if variance_warnings:
        var_note = f" Seed-variance warnings: {variance_warnings[:3]}"

    if largest_pass is None:
        # Shouldn't happen given the kill criteria above, but defensive
        return ("MULTIHOP_ENVELOPE_INCONCLUSIVE",
                f"No NUM_FACTS passed despite smallest passing kill criteria. " +
                (first_fail_reason or "unknown") + var_note)

    if first_fail_nf is None:
        return ("MULTIHOP_ENVELOPE_GE_200",
                f"All tested NUM_FACTS {sorted_nfs} pass all criteria at depths up to "
                f"{max_depth}. Envelope extends through {largest_pass}. " +
                f"Multi-hop chains viable on fact-bases at least this large." + var_note)

    return (f"MULTIHOP_ENVELOPE_AT_{largest_pass}",
            f"Envelope: pass through NUM_FACTS={largest_pass}, fail at "
            f"NUM_FACTS={first_fail_nf} with: {first_fail_reason}." + var_note)


def self_test_verdict() -> None:
    def mk_row(by_depth: dict, per_seed: dict | None = None, retention: float = 0.95) -> dict:
        return {"acc_by_depth": {str(k): v for k, v in by_depth.items()},
                "retention_rate": retention,
                "per_seed_acc_by_depth": per_seed or {}}

    cases = [
        # 1. GE_200: all NUM_FACTS pass
        ({"by_num_facts": {
            "25": mk_row({1: 0.99, 10: 0.85, 50: 0.40}),
            "50": mk_row({1: 0.99, 10: 0.83, 50: 0.30}),
            "100": mk_row({1: 0.98, 10: 0.70, 50: 0.20}),
            "200": mk_row({1: 0.98, 10: 0.50, 50: 0.12})},
          "max_depth": 50},
         "MULTIHOP_ENVELOPE_GE_200"),
        # 2. AT_50: 25 and 50 pass, 100 fails on acc_1hop
        ({"by_num_facts": {
            "25": mk_row({1: 0.99, 10: 0.85, 50: 0.40}),
            "50": mk_row({1: 0.98, 10: 0.75, 50: 0.30}),
            "100": mk_row({1: 0.95, 10: 0.60, 50: 0.20}),
            "200": mk_row({1: 0.85, 10: 0.40, 50: 0.10})},
          "max_depth": 50},
         "MULTIHOP_ENVELOPE_AT_50"),
        # 3. V2_NOT_REPLICATED: smallest fails acc_1hop
        ({"by_num_facts": {
            "25": mk_row({1: 0.90, 10: 0.70, 50: 0.30}),
            "50": mk_row({1: 0.88, 10: 0.60, 50: 0.20})},
          "max_depth": 50},
         "ENVELOPE_V2_NOT_REPLICATED"),
        # 4. NARROW_AT_LOW: smallest acc_50hop fails
        ({"by_num_facts": {
            "25": mk_row({1: 0.99, 10: 0.30, 50: 0.05}),
            "50": mk_row({1: 0.98, 10: 0.25, 50: 0.03})},
          "max_depth": 50},
         "ENVELOPE_NARROW_AT_LOW_NUM_FACTS"),
        # 5. INCONCLUSIVE
        ({}, "MULTIHOP_ENVELOPE_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N_SMOKE if smoke else N_FULL,
        "num_entities": NUM_ENTITIES_SMOKE if smoke else NUM_ENTITIES_FULL,
        "num_relations": NUM_RELATIONS_SMOKE if smoke else NUM_RELATIONS_FULL,
        "num_facts_list": NUM_FACTS_SMOKE if smoke else NUM_FACTS_FULL,
        "hop_depths": HOP_DEPTHS_SMOKE if smoke else HOP_DEPTHS_FULL,
        "n_trials": N_TRIALS_SMOKE if smoke else N_TRIALS_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    max_depth = max(config["hop_depths"])
    by_nf = {}

    for num_facts in config["num_facts_list"]:
        print(f"[NUM_FACTS={num_facts}] running...", flush=True)
        per_seed_runs = []
        for seed in config["seeds"]:
            sub_config = {
                "N": config["N"],
                "num_entities": config["num_entities"],
                "num_relations": config["num_relations"],
                "num_facts": num_facts,
            }
            r = v3.run_one_seed(seed, config["hop_depths"], config["n_trials"],
                                  sub_config, device)
            per_seed_runs.append(r)
            accs_str = " ".join(f"d{d}={r['by_depth'][d]:.3f}" for d in config["hop_depths"])
            print(f"  nf={num_facts} seed={seed}  {accs_str}", flush=True)

        # Aggregate
        acc_by_depth = {}
        per_seed_acc_by_depth = {}
        for d in config["hop_depths"]:
            vals = [r["by_depth"][d] for r in per_seed_runs]
            acc_by_depth[str(d)] = sum(vals) / len(vals)
            per_seed_acc_by_depth[str(d)] = vals

        # Retention from this NUM_FACTS row's mean acc curve
        per_depth_mean = {d: acc_by_depth[str(d)] for d in config["hop_depths"]}
        retention = v3.per_hop_retention_rate(per_depth_mean)

        by_nf[str(num_facts)] = {
            "acc_by_depth": acc_by_depth,
            "per_seed_acc_by_depth": per_seed_acc_by_depth,
            "retention_rate": retention,
        }

    summary = {"by_num_facts": by_nf, "max_depth": max_depth}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= ENVELOPE =========", flush=True)
    for nf in config["num_facts_list"]:
        row = by_nf[str(nf)]
        accs_str = " ".join(f"d{d}={row['acc_by_depth'][str(d)]:.3f}"
                              for d in config["hop_depths"])
        print(f"  nf={nf:4d}  {accs_str}  retention={row['retention_rate']:.3f}",
              flush=True)
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir: Path, summary, verdict, msg, elapsed, config):
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
                "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14u_multihop_envelope_v1_smoke")
    log_event("experiment_started", name="wave14u_multihop_envelope_v1", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Oracle: at smallest NUM_FACTS, acc_1hop must be high (substrate sanity)
    smallest_key = str(min(config["num_facts_list"]))
    acc_1hop = float(summary["by_num_facts"][smallest_key]["acc_by_depth"]["1"])
    oracle.assert_baseline_high("acc_1hop_smoke", acc_1hop, 0.85)

    # Oracle: monotone non-increasing in depth at each NUM_FACTS
    for nf, row in summary["by_num_facts"].items():
        depths_sorted = sorted(int(d) for d in row["acc_by_depth"].keys())
        accs = [row["acc_by_depth"][str(d)] for d in depths_sorted]
        for i in range(len(accs) - 1):
            if accs[i + 1] > accs[i] + 0.1:  # allow noise; flag big inversions only
                raise AssertionError(
                    f"SANITY FAIL [depth_monotone]: nf={nf} depth {depths_sorted[i+1]} "
                    f"acc={accs[i+1]:.3f} > depth {depths_sorted[i]} acc={accs[i]:.3f}+0.1")

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14u_multihop_envelope_v1",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14u_multihop_envelope_v1")
    log_event("experiment_started", name="wave14u_multihop_envelope_v1", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14u_multihop_envelope_v1",
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
