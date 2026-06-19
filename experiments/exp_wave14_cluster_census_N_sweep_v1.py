"""Cluster census N-sweep — Strategy 21:25 Priority 2 (cluster size vs N).

Run cluster census at N in {4096, 16384, 65536} at K=100. Fit cluster_size ~ N^gamma.
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402

_cc = importlib.util.spec_from_file_location("cc",
    REPO / "experiments" / "exp_wave14_cluster_census_N65536_v1.py")
cc = importlib.util.module_from_spec(_cc); _cc.loader.exec_module(cc)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "cluster_per_N" not in summary:
        return ("NSCALE_INCONCLUSIVE", "Missing.")
    per = summary["cluster_per_N"]
    fitted_gamma = summary["fitted_gamma"]
    if 0.5 <= fitted_gamma <= 1.0:
        return ("CLUSTER_NSCALE_CONFIRMS",
                f"Fitted gamma={fitted_gamma:.2f} in [0.5, 1.0]. cluster_per_N={per}.")
    if fitted_gamma < 0.3 or fitted_gamma > 1.3:
        return ("CLUSTER_NSCALE_REFUTES",
                f"Fitted gamma={fitted_gamma:.2f} outside [0.3, 1.3]. cluster_per_N={per}.")
    return ("CLUSTER_NSCALE_PARTIAL", f"gamma={fitted_gamma:.2f}. cluster_per_N={per}.")


def self_test_verdict():
    for s, exp in [
        ({"cluster_per_N": {}, "fitted_gamma": 0.73}, "CLUSTER_NSCALE_CONFIRMS"),
        ({"cluster_per_N": {}, "fitted_gamma": 0.10}, "CLUSTER_NSCALE_REFUTES"),
        ({"cluster_per_N": {}, "fitted_gamma": 1.5}, "CLUSTER_NSCALE_REFUTES"),
        ({"cluster_per_N": {}, "fitted_gamma": 0.4}, "CLUSTER_NSCALE_PARTIAL"),
        ({}, "NSCALE_INCONCLUSIVE"),
    ]:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print("verdict self-test passed (5/5 cases)", flush=True)


def fit_powerlaw(Ns, vals):
    if len(Ns) < 2: return 0.0, 0.0
    xs = [math.log(N) for N in Ns]
    ys = [math.log(max(v, 0.5)) for v in vals]
    n = len(xs)
    sx = sum(xs); sy = sum(ys); sxx = sum(x*x for x in xs); sxy = sum(xs[i]*ys[i] for i in range(n))
    slope = (n*sxy - sx*sy) / max(n*sxx - sx*sx, 1e-9)
    intercept = (sy - slope*sx)/n
    mean_y = sy / n
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    ss_res = sum((ys[i] - (slope*xs[i] + intercept)) ** 2 for i in range(n))
    r2 = 1.0 - ss_res / max(ss_tot, 1e-9)
    return slope, r2


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"N_grid": [4096, 8192] if smoke else [4096, 16384, 65536],
              "K": 100, "depth": 25, "n_trials": 100 if smoke else 300,
              "num_relations": 20, "noise_p": 0.05, "seed": 17}
    per_N = {}; cluster_sizes = []
    for N in config["N_grid"]:
        unique, top5, _ = cc.run_cluster_census(
            N, config["K"], config["depth"], config["n_trials"],
            config["num_relations"], config["noise_p"], config["seed"], device)
        per_N[str(N)] = unique
        cluster_sizes.append(unique)
        print(f"  N={N}: unique_codewords={unique}, top5_share={top5:.3f}", flush=True)
    gamma, r2 = fit_powerlaw(config["N_grid"], cluster_sizes)
    print(f"  fitted gamma={gamma:.3f}, r2={r2:.3f}", flush=True)
    summary = {"cluster_per_N": per_N, "fitted_gamma": gamma, "fit_r2": r2}
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
    out_dir = get_output_dir("wave14_cluster_census_N_sweep_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("cluster_present",
                                 float(max(summary["cluster_per_N"].values())) + 0.1, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_cluster_census_N_sweep_v1")
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
