"""Bet Y V2.D Phase 1 — beta(N) = c/N empirical calibration.

Strategy cycle 93 addendum (2026-05-22): modern dense AM exponential capacity
requires beta_net = O(1/N) (Lucibello-Mezard 2024). Fixed beta=32 fails at
large N. Sweep beta at multiple N to extract c.

Pre-reg: preregs/2026-05-22_wave14_betY_phase1_beta_calibration.md
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass

CV_PASS = 0.30
CV_PARTIAL = 0.50


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "c_per_N" not in summary:
        return ("BETA_CALIBRATION_INCONCLUSIVE", "Missing c_per_N.")
    c_vals = list(summary["c_per_N"].values())
    if not c_vals or all(c <= 0 for c in c_vals):
        return ("BETA_CALIBRATION_FAILED",
                f"No non-trivial beta_optimal found across N values. c_per_N: {summary['c_per_N']}")
    c_mean = sum(c_vals) / len(c_vals)
    c_std = (sum((c - c_mean) ** 2 for c in c_vals) / max(len(c_vals) - 1, 1)) ** 0.5
    cv = c_std / max(abs(c_mean), 1e-9)
    if cv < CV_PASS:
        return ("BETA_CALIBRATION_PASS",
                f"c estimate consistent across N: mean={c_mean:.1f}, CV={cv:.3f}<{CV_PASS}. "
                f"Predicted beta(N=65536) = {c_mean/65536:.6f}. per-N c: {summary['c_per_N']}")
    if cv < CV_PARTIAL:
        return ("BETA_CALIBRATION_PARTIAL",
                f"c estimate noisy: mean={c_mean:.1f}, CV={cv:.3f} in [{CV_PASS},{CV_PARTIAL}]. "
                f"Phase 2 should test multiple c values bracketing mean.")
    return ("BETA_CALIBRATION_FAILED",
            f"c estimate inconsistent: mean={c_mean:.1f}, CV={cv:.3f}>={CV_PARTIAL}. "
            f"beta(N)=c/N scaling not empirically supported. per-N c: {summary['c_per_N']}")


def self_test_verdict():
    cases = [
        ({"c_per_N": {"4096": 130000, "8192": 131000, "16384": 132000}},
         "BETA_CALIBRATION_PASS"),
        ({"c_per_N": {"4096": 80000, "8192": 130000, "16384": 180000}},
         "BETA_CALIBRATION_PARTIAL"),
        ({"c_per_N": {"4096": 30000, "8192": 200000, "16384": 500000}},
         "BETA_CALIBRATION_FAILED"),
        ({"c_per_N": {"4096": 0, "8192": 0}}, "BETA_CALIBRATION_FAILED"),
        ({}, "BETA_CALIBRATION_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_random_keys(M, N, gen, device):
    return 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0


def measure_at_beta(N, M, beta, n_iter, n_query, gen, device):
    """Modern dense AM retrieval accuracy at given (N, M, beta)."""
    keys = make_random_keys(M, N, gen, device)
    values = make_random_keys(M, N, gen, device)
    W = (values.T @ keys) / N
    qp_gen = torch.Generator().manual_seed(7)
    query_idx = torch.randperm(M, generator=qp_gen)[:n_query].to(device)
    correct = 0
    for i in range(n_query):
        ix = int(query_idx[i])
        probe = keys[ix] @ W.T  # initial value estimate
        state = probe.float()
        for _ in range(n_iter):
            sims = (values @ state) * beta
            sims = sims - sims.max()
            w = torch.softmax(sims, dim=0)
            state = w @ values
        pred = (values @ state).argmax().item()
        if int(pred) == ix:
            correct += 1
    return correct / n_query


def find_beta_optimal(N, M, beta_grid, n_iter, n_query, seeds, device):
    """Find beta that maximizes retrieval accuracy at this (N, M)."""
    best_beta, best_acc = beta_grid[0], -1.0
    for beta in beta_grid:
        accs = []
        for s in seeds:
            gen = torch.Generator(device=device).manual_seed(s * 17 + 7)
            accs.append(measure_at_beta(N, M, beta, n_iter, n_query, gen, device))
        acc = sum(accs) / len(accs)
        if acc > best_acc:
            best_acc, best_beta = acc, beta
    return best_beta, best_acc


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N_grid": [1024, 2048] if smoke else [4096, 8192, 16384],
              "M_over_N": 8,
              "n_iter": 5,
              "n_query": 30 if smoke else 100,
              "seeds": [17] if smoke else [17, 23, 31]}
    c_per_N = {}
    beta_optimal_per_N = {}
    acc_per_N = {}
    for N in config["N_grid"]:
        # Beta grid centered on 1/N scale (c around 131072 = 32 * 4096)
        c_center = 131072.0
        beta_grid = [c_center / (N * mult) for mult in [4.0, 2.0, 1.0, 0.5, 0.25]]
        beta_opt, acc = find_beta_optimal(N, config["M_over_N"] * N, beta_grid,
                                                config["n_iter"], config["n_query"],
                                                config["seeds"], device)
        c = beta_opt * N
        c_per_N[str(N)] = c
        beta_optimal_per_N[str(N)] = beta_opt
        acc_per_N[str(N)] = acc
        print(f"  N={N}: beta_opt={beta_opt:.4f} c={c:.0f} acc={acc:.3f}", flush=True)
    summary = {"c_per_N": c_per_N, "beta_optimal_per_N": beta_optimal_per_N,
                "acc_per_N": acc_per_N}
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
    out_dir = get_output_dir("wave14_betY_phase1_beta_calibration_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first_N = list(summary["c_per_N"].keys())[0]
    oracle.assert_baseline_high("c_estimate_exists", summary["c_per_N"][first_N], 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_betY_phase1_beta_calibration")
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
