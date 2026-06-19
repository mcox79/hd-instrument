"""VAMP-on-chain depth ceiling — push the d=50 PERFECT result to find where it breaks.

Per cycle 127 VAMPCHAIN_RESTORES PERFECT acc_50hop=1.000. Test extension: does
substrate-novel two-tier readout (VAMP forward-backward EP) sustain through d=100,
200, 500 hops at N=65536 K=100?

Substrate-product question: what is the deep-chain composition ceiling at N=65536?

Verdict thresholds:
  DEPTH_CEILING_HIGH:  acc remains >= 0.50 at d=200 (substantial ceiling)
  DEPTH_CEILING_MID:   acc >= 0.50 at d=100 but breaks at d=200
  DEPTH_CEILING_LOW:   acc < 0.50 at d=100 (ceiling lower than expected)
  DEPTH_CEILING_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_vamp_chain_depth_ceiling_v1.md
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

_v = importlib.util.spec_from_file_location("v",
    REPO / "experiments" / "exp_wave14_multihop_vamp_chain_N65536_v1.py")
v = importlib.util.module_from_spec(_v); _v.loader.exec_module(v)
_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "acc_per_depth" not in summary:
        return ("DEPTH_CEILING_INCONCLUSIVE", "Missing acc_per_depth.")
    per = summary["acc_per_depth"]
    a100 = per.get("100", 0.0); a200 = per.get("200", 0.0)
    if a200 >= 0.50:
        return ("DEPTH_CEILING_HIGH",
                f"VAMP-on-chain sustains through d=200: acc={a200:.3f}>=0.50. "
                f"Substantial depth ceiling. acc_per_depth={per}.")
    if a100 >= 0.50:
        return ("DEPTH_CEILING_MID",
                f"VAMP-on-chain breaks between d=100 ({a100:.3f}) and d=200 ({a200:.3f}). "
                f"acc_per_depth={per}.")
    return ("DEPTH_CEILING_LOW",
            f"VAMP-on-chain breaks before d=100: acc={a100:.3f}<0.50. "
            f"Lower-than-expected ceiling. acc_per_depth={per}.")


def self_test_verdict():
    cases = [
        ({"acc_per_depth": {"50": 1.0, "100": 0.90, "200": 0.70, "500": 0.40}}, "DEPTH_CEILING_HIGH"),
        ({"acc_per_depth": {"50": 1.0, "100": 0.80, "200": 0.30, "500": 0.10}}, "DEPTH_CEILING_MID"),
        ({"acc_per_depth": {"50": 0.90, "100": 0.30, "200": 0.10}}, "DEPTH_CEILING_LOW"),
        ({}, "DEPTH_CEILING_INCONCLUSIVE"),
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
              "num_entities": 300,
              "num_relations": 20,
              "num_facts": 200,
              "hop_depths": [50, 100] if smoke else [50, 100, 200, 500],
              "n_trials": 5 if smoke else 15,
              "seeds": [17] if smoke else [17, 23]}
    print(f"[config] N={config['N']} num_facts={config['num_facts']} depths={config['hop_depths']}", flush=True)
    per_depth_acc = {}
    for seed in config["seeds"]:
        r = v.run_one_seed_compare(seed, config["hop_depths"], config["n_trials"], config, device)
        a_v = " ".join(f"d{d}={r['by_depth_vamp_chain'][d]:.3f}" for d in config["hop_depths"])
        print(f"  seed={seed} VAMP: {a_v}", flush=True)
        for d in config["hop_depths"]:
            per_depth_acc.setdefault(d, []).append(r["by_depth_vamp_chain"][d])
    per_depth_mean = {str(d): sum(per_depth_acc[d]) / len(per_depth_acc[d])
                       for d in config["hop_depths"]}
    summary = {"acc_per_depth": per_depth_mean,
                "K": config["num_facts"]}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
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
    out_dir = get_output_dir("wave14_vamp_chain_depth_ceiling_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("acc_present",
                                 summary["acc_per_depth"].get("50", 0.0) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_vamp_chain_depth_ceiling_v1")
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
