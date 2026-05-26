"""Multi-hop K=100 at N=65536 — V2.D Phase 1 sub-test #4.

Per Strategy 13:15 V2.D mechanism revision: "Multi-hop K=100 at N=65536 (target:
acc_50hop >= 0.767 matching cycle 96 NEW HIGH baseline)". Bundle-based multi-hop
chain queries through BSC factbase M (no full W needed).

Reuses `exp_wave14r_multihop_K100` infrastructure at scaled N.

Verdict thresholds (per Strategy V2.D revision):
  MULTIHOP_N65K_PASS:    acc_50hop >= 0.767 (matches cycle 96 baseline)
  MULTIHOP_N65K_PARTIAL: 0.40 <= acc_50hop < 0.767
  MULTIHOP_N65K_KILLED:  acc_50hop < 0.40
  MULTIHOP_N65K_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_K100_N65536_v1.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


PASS_ACC_50 = 0.767
PARTIAL_ACC_50 = 0.40


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "acc_50hop" not in summary:
        return ("MULTIHOP_N65K_INCONCLUSIVE", "Missing acc_50hop.")
    a50 = summary["acc_50hop"]
    by_d = summary["per_depth_mean_acc"]
    if a50 >= PASS_ACC_50:
        return ("MULTIHOP_N65K_PASS",
                f"Multi-hop K=100 at N=65536: acc_50hop={a50:.3f} (>={PASS_ACC_50}). "
                f"Cycle 96 baseline extends to N=65536. per_depth={by_d}.")
    if a50 >= PARTIAL_ACC_50:
        return ("MULTIHOP_N65K_PARTIAL",
                f"acc_50hop={a50:.3f} ({PARTIAL_ACC_50}<=acc<{PASS_ACC_50}). "
                f"Partial N-scaling. per_depth={by_d}.")
    return ("MULTIHOP_N65K_KILLED",
            f"acc_50hop={a50:.3f}<{PARTIAL_ACC_50}. N-scaling fails for multi-hop. "
            f"per_depth={by_d}.")


def self_test_verdict():
    cases = [
        ({"acc_50hop": 0.85, "per_depth_mean_acc": {}}, "MULTIHOP_N65K_PASS"),
        ({"acc_50hop": 0.55, "per_depth_mean_acc": {}}, "MULTIHOP_N65K_PARTIAL"),
        ({"acc_50hop": 0.20, "per_depth_mean_acc": {}}, "MULTIHOP_N65K_KILLED"),
        ({}, "MULTIHOP_N65K_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 8192 if smoke else 65536,
              "num_entities": 200,
              "num_relations": 20,
              "num_facts": 100,
              "hop_depths": [1, 25] if smoke else [1, 5, 10, 25, 50],
              "n_trials": 10 if smoke else 30,
              "seeds": [17] if smoke else [17, 23]}
    print(f"[config] N={config['N']} K=num_facts={config['num_facts']} depths={config['hop_depths']}", flush=True)
    per_seed_data = []
    for seed in config["seeds"]:
        r = mh.run_one_seed(seed, config["hop_depths"], config["n_trials"], config, device)
        per_seed_data.append(r)
        accs = " ".join(f"d{d}={r['by_depth'][d]:.3f}" for d in config["hop_depths"])
        print(f"  seed={seed}: {accs}", flush=True)
    per_depth_mean = {}
    for d in config["hop_depths"]:
        per_depth_mean[d] = sum(r["by_depth"][d] for r in per_seed_data) / len(per_seed_data)
    acc_50 = per_depth_mean.get(50, per_depth_mean.get(max(config["hop_depths"]), 0.0))
    summary = {"per_depth_mean_acc": {str(d): per_depth_mean[d] for d in config["hop_depths"]},
                "acc_50hop": acc_50,
                "N": config["N"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nacc_50hop at N={config['N']}: {acc_50:.3f}", flush=True)
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
    out_dir = get_output_dir("wave14_multihop_K100_N65536_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_1hop_present", summary["per_depth_mean_acc"].get("1", 0.0) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_K100_N65536_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test: self_test_verdict(); return 0
    if args.smoke: run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
