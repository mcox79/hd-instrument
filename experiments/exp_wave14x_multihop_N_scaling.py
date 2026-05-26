"""Multi-hop reasoning N-scaling - does widening substrate raise 1-hop ceiling?

Follow-up to wave14u_multihop_envelope_v1_b verdict ENVELOPE_V2_NOT_REPLICATED.
The substrate's 1-hop ceiling at N=4096 is bounded ~0.95-0.97 across NUM_FACTS.
Substrate theory predicts per-hop SNR scales as sqrt(N) at fixed F; doubling
N at fixed F should square-root-improve crosstalk noise.

Test: NUM_FACTS=100 (matches v3), sweep N in {4096, 8192, 16384}.
Output: does acc_1hop reach >= 0.99 at some N? And if so, what N?

Pre-reg: preregs/2026-05-21_wave14x_multihop_N_scaling.md
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


N_LIST_FULL = [4096, 8192, 16384]
N_LIST_SMOKE = [512, 1024]
NUM_ENTITIES_FULL = 200
NUM_ENTITIES_SMOKE = 50
NUM_RELATIONS_FULL = 20
NUM_RELATIONS_SMOKE = 5
NUM_FACTS_FULL = 100
NUM_FACTS_SMOKE = 20
HOP_DEPTHS_FULL = [1, 10, 50]
HOP_DEPTHS_SMOKE = [1, 10]
N_TRIALS_FULL = 50
N_TRIALS_SMOKE = 5
SEEDS_FULL = [17, 23, 31]
SEEDS_SMOKE = [17]

PASS_ACC_1HOP_HIGH = 0.99
PASS_ACC_1HOP_LOW = 0.85


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


def compute_verdict(summary: dict) -> tuple[str, str]:
    by_n = summary.get("by_N")
    if not by_n:
        return ("MULTIHOP_N_SCALING_INCONCLUSIVE", "Missing per-N data.")

    sorted_ns = sorted(by_n.keys(), key=int)

    # Get acc_1hop and retention per N
    acc_1hop_per_n = {int(N): float(by_n[N]["acc_by_depth"]["1"]) for N in sorted_ns}
    retention_per_n = {int(N): float(by_n[N]["retention_rate"]) for N in sorted_ns}

    # Compute slope of acc_1hop vs log2(N)
    log_ns = [math.log2(int(N)) for N in sorted_ns]
    accs_1 = [acc_1hop_per_n[int(N)] for N in sorted_ns]
    n_pts = len(log_ns)
    if n_pts >= 2:
        mean_x = sum(log_ns) / n_pts
        mean_y = sum(accs_1) / n_pts
        num = sum((log_ns[i] - mean_x) * (accs_1[i] - mean_y) for i in range(n_pts))
        den = sum((log_ns[i] - mean_x) ** 2 for i in range(n_pts))
        slope = num / den if abs(den) > 1e-12 else 0.0
    else:
        slope = 0.0

    # NO_BENEFIT: slope <= 0 (N has no effect)
    if slope <= 0:
        return ("MULTIHOP_N_SCALING_NO_BENEFIT",
                f"Slope of acc_1hop vs log2(N) = {slope:+.4f} <= 0. Widening substrate "
                f"does not improve 1-hop accuracy. acc_1hop per N: " +
                ", ".join(f"N={N}:acc={acc_1hop_per_n[int(N)]:.3f}" for N in sorted_ns) +
                ". 1-hop ceiling is intrinsic to the substrate design, not noise-limited.")

    # Find smallest N at which acc_1hop >= 0.99
    recovers_at = None
    for N in sorted_ns:
        if acc_1hop_per_n[int(N)] >= PASS_ACC_1HOP_HIGH:
            recovers_at = int(N)
            break

    if recovers_at is not None:
        max_ret = max(retention_per_n.values())
        return (f"MULTIHOP_N_RECOVERS_AT_{recovers_at}",
                f"acc_1hop reaches {PASS_ACC_1HOP_HIGH}+ at N={recovers_at} "
                f"(acc={acc_1hop_per_n[recovers_at]:.3f}). Slope vs log2(N) = "
                f"{slope:+.4f}. Per-hop retention peaks at {max_ret:.4f}. "
                f"Substrate width is the lever for 1-hop fidelity at fixed F.")

    return ("MULTIHOP_N_IMPROVES_BUT_BOUNDED",
            f"acc_1hop improves with N (slope = {slope:+.4f}) but doesn't reach "
            f"{PASS_ACC_1HOP_HIGH} at any tested N. Best: N={sorted_ns[-1]}, "
            f"acc_1hop={acc_1hop_per_n[int(sorted_ns[-1])]:.3f}. Either the "
            f"sqrt(N)-noise model is incomplete or higher N needed.")


def self_test_verdict() -> None:
    def mk_row(N, acc_1, acc_max, retention):
        return {"acc_by_depth": {"1": acc_1, "10": acc_1 * 0.9, "50": acc_max},
                "retention_rate": retention,
                "N": N}

    cases = [
        # 1. RECOVERS_AT_8192: acc_1 hits 0.99 at N=8192
        ({"by_N": {
            "4096": mk_row(4096, 0.94, 0.20, 0.95),
            "8192": mk_row(8192, 0.99, 0.45, 0.99),
            "16384": mk_row(16384, 0.995, 0.65, 0.995)}},
         "MULTIHOP_N_RECOVERS_AT_8192"),
        # 2. IMPROVES_BUT_BOUNDED: improves but never hits 0.99
        ({"by_N": {
            "4096": mk_row(4096, 0.93, 0.15, 0.94),
            "8192": mk_row(8192, 0.95, 0.25, 0.96),
            "16384": mk_row(16384, 0.97, 0.35, 0.97)}},
         "MULTIHOP_N_IMPROVES_BUT_BOUNDED"),
        # 3. NO_BENEFIT: slope <= 0
        ({"by_N": {
            "4096": mk_row(4096, 0.95, 0.15, 0.94),
            "8192": mk_row(8192, 0.94, 0.12, 0.93),
            "16384": mk_row(16384, 0.93, 0.10, 0.92)}},
         "MULTIHOP_N_SCALING_NO_BENEFIT"),
        # 4. INCONCLUSIVE
        ({}, "MULTIHOP_N_SCALING_INCONCLUSIVE"),
    ]
    for s, expected in cases:
        actual, _ = compute_verdict(s)
        if actual != expected:
            raise AssertionError(f"FAIL: actual={actual} != expected={expected}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_one_N(N: int, config: dict, device: torch.device) -> dict:
    """Run multi-hop chain test at fixed N, aggregate across seeds."""
    per_seed_runs = []
    for seed in config["seeds"]:
        sub_config = {
            "N": N,
            "num_entities": config["num_entities"],
            "num_relations": config["num_relations"],
            "num_facts": config["num_facts"],
        }
        r = v3.run_one_seed(seed, config["hop_depths"], config["n_trials"],
                              sub_config, device)
        per_seed_runs.append(r)
        accs_str = " ".join(f"d{d}={r['by_depth'][d]:.3f}" for d in config["hop_depths"])
        print(f"  N={N} seed={seed}  {accs_str}  max_ip={r['max_pairwise_ip']:.3f}",
              flush=True)

    acc_by_depth = {}
    per_seed_acc_by_depth = {}
    for d in config["hop_depths"]:
        vals = [r["by_depth"][d] for r in per_seed_runs]
        acc_by_depth[str(d)] = sum(vals) / len(vals)
        per_seed_acc_by_depth[str(d)] = vals
    per_depth_mean = {d: acc_by_depth[str(d)] for d in config["hop_depths"]}
    retention = v3.per_hop_retention_rate(per_depth_mean)
    max_pairwise = max(r["max_pairwise_ip"] for r in per_seed_runs)
    return {"N": N,
            "acc_by_depth": acc_by_depth,
            "per_seed_acc_by_depth": per_seed_acc_by_depth,
            "retention_rate": retention,
            "max_pairwise_ip": max_pairwise}


def run_experiment(smoke: bool):
    t_start = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {
        "mode": "smoke" if smoke else "full",
        "N_list": N_LIST_SMOKE if smoke else N_LIST_FULL,
        "num_entities": NUM_ENTITIES_SMOKE if smoke else NUM_ENTITIES_FULL,
        "num_relations": NUM_RELATIONS_SMOKE if smoke else NUM_RELATIONS_FULL,
        "num_facts": NUM_FACTS_SMOKE if smoke else NUM_FACTS_FULL,
        "hop_depths": HOP_DEPTHS_SMOKE if smoke else HOP_DEPTHS_FULL,
        "n_trials": N_TRIALS_SMOKE if smoke else N_TRIALS_FULL,
        "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
    }
    print(f"[config] {config}", flush=True)
    print(f"[device] {device}", flush=True)

    by_N = {}
    for N in config["N_list"]:
        print(f"[N={N}] running...", flush=True)
        row = run_one_N(N, config, device)
        by_N[str(N)] = row
        accs_str = " ".join(f"d{d}={row['acc_by_depth'][str(d)]:.3f}"
                              for d in config["hop_depths"])
        print(f"  N={N:6d}  {accs_str}  retention={row['retention_rate']:.4f}",
              flush=True)

    summary = {"by_N": by_N}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t_start

    print("\n========= N-SCALING =========", flush=True)
    for N in config["N_list"]:
        row = by_N[str(N)]
        accs_str = " ".join(f"d{d}={row['acc_by_depth'][str(d)]:.3f}"
                              for d in config["hop_depths"])
        print(f"  N={N:6d}  {accs_str}  retention={row['retention_rate']:.4f}  "
              f"max_ip={row['max_pairwise_ip']:.3f}", flush=True)
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
    out_dir = get_output_dir("wave14x_multihop_N_scaling_smoke")
    log_event("experiment_started", name="wave14x_multihop_N_scaling", mode="smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)

    # Oracle: at smallest N, acc_1hop must be reasonable (substrate sanity)
    smallest_N_key = str(min(config["N_list"]))
    acc_1hop = float(summary["by_N"][smallest_N_key]["acc_by_depth"]["1"])
    oracle.assert_baseline_high("acc_1hop_smoke", acc_1hop, PASS_ACC_1HOP_LOW)

    # Oracle: max pairwise IP bounded for random BSC atoms
    max_ip = max(float(summary["by_N"][str(N)]["max_pairwise_ip"])
                 for N in config["N_list"])
    oracle.assert_in_range("entity_max_pairwise_ip", max_ip, (0.0, 0.30))

    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14x_multihop_N_scaling",
              mode="smoke", verdict=verdict, verdict_msg=msg, elapsed_s=elapsed)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14x_multihop_N_scaling")
    log_event("experiment_started", name="wave14x_multihop_N_scaling", mode="full")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    log_event("experiment_outcome", name="wave14x_multihop_N_scaling",
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
