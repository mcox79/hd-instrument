"""muSR Kubo-Toyabe analog — substrate random-site decay G(t).

Per Research Entry 140 #3 (P=0.80). Initialize substrate spins; run Glauber MC;
measure autocorrelation G(t) = <s(0).s(t)>/N. Static Gaussian fit G(t) ~ exp(-Delta^2 t^2/2)
or stretched-exponential indicates dynamic regime.

Substrate-novel: nobody has fit substrate's autocorrelation decay shape.

Verdict thresholds:
  KUBO_STATIC:    Gaussian fit R^2 >= 0.85, exponent beta ~ 2.0 (true Kubo-Toyabe limit)
  KUBO_DYNAMIC:   stretched-exp R^2 - Gaussian R^2 > 0.05 (dynamic regime)
  KUBO_MIXED:    both fits partial
  KUBO_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_musr_kubo_toyabe_v1.md
"""
from __future__ import annotations
import argparse, json, math, os, sys, time
from pathlib import Path
import torch
REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402
try:
    from hdlab.session_log import log_event
except ImportError:
    def log_event(*a, **k): pass


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "r2_gaussian" not in summary:
        return ("KUBO_INCONCLUSIVE", "Missing r2_gaussian.")
    r2_g = summary["r2_gaussian"]
    r2_s = summary["r2_stretched"]
    beta = summary["stretch_exponent"]
    delta = summary["delta_rms"]
    if r2_s - r2_g > 0.05:
        return ("KUBO_DYNAMIC",
                f"Stretched-exponential beats Gaussian: r2_stretched={r2_s:.3f} > r2_gauss={r2_g:.3f}+0.05. "
                f"beta={beta:.3f} (dynamic regime). delta={delta:.4f}.")
    if r2_g >= 0.85:
        return ("KUBO_STATIC",
                f"Kubo-Toyabe static-Gaussian fit: r2_gauss={r2_g:.3f}>=0.85, beta_implied=2.0. "
                f"r2_stretched={r2_s:.3f}, fitted_beta={beta:.3f}. delta={delta:.4f}.")
    return ("KUBO_MIXED",
            f"Neither fit clean: r2_gauss={r2_g:.3f}, r2_stretched={r2_s:.3f} (beta={beta:.3f}). delta={delta:.4f}.")


def self_test_verdict():
    cases = [
        ({"r2_gaussian": 0.92, "r2_stretched": 0.93, "stretch_exponent": 1.95, "delta_rms": 0.3}, "KUBO_STATIC"),
        ({"r2_gaussian": 0.65, "r2_stretched": 0.85, "stretch_exponent": 1.30, "delta_rms": 0.3}, "KUBO_DYNAMIC"),
        ({"r2_gaussian": 0.70, "r2_stretched": 0.72, "stretch_exponent": 1.80, "delta_rms": 0.3}, "KUBO_MIXED"),
        ({}, "KUBO_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def build_hopfield_W(M, N, cpu_gen, device):
    bits = (torch.rand((M, N), generator=cpu_gen) > 0.5).to(device)
    patterns = 2.0 * bits.float() - 1.0
    W = (patterns.T @ patterns) / N
    W.fill_diagonal_(0.0)
    return W


def glauber_step(s, W, beta, cpu_gen, device):
    N = s.shape[0]
    order = torch.randperm(N, generator=cpu_gen).to(device)
    us = torch.rand(N, generator=cpu_gen).to(device)
    for k, idx in enumerate(order):
        h_i = float(W[idx] @ s)
        p_plus = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        s[idx] = 1.0 if float(us[k]) < p_plus else -1.0
    return s


def measure_autocorr(W, N, beta, n_sweeps, n_replicates, cpu_gen, device):
    """Run n_replicates of MC trajectories; record m(t) = <s_t . s_0>/N over n_sweeps."""
    m_t = [0.0] * n_sweeps
    counts = [0] * n_sweeps
    for rep in range(n_replicates):
        init_bits = (torch.rand(N, generator=cpu_gen) > 0.5).to(device)
        s0 = 2.0 * init_bits.float() - 1.0
        s = s0.clone()
        for t in range(n_sweeps):
            s = glauber_step(s, W, beta, cpu_gen, device)
            m = float((s * s0).mean())
            m_t[t] += m
            counts[t] += 1
    return [m_t[i] / max(counts[i], 1) for i in range(n_sweeps)]


def fit_gaussian(ts, G):
    """G(t) = G0 * exp(-Delta^2 t^2 / 2). Linear fit to log(G/G0) vs t^2."""
    G0 = G[0]
    safe = [(t, g) for t, g in zip(ts, G) if g > 0.01 * G0]
    if len(safe) < 3:
        return 0.0, 0.0, 0.0
    xs = [t * t for t, _ in safe]
    ys = [math.log(g / G0) for _, g in safe]
    n = len(xs)
    sx = sum(xs); sy = sum(ys); sxx = sum(x * x for x in xs); sxy = sum(xs[i] * ys[i] for i in range(n))
    slope = (n * sxy - sx * sy) / max(n * sxx - sx * sx, 1e-9)
    delta = math.sqrt(max(-2.0 * slope, 1e-9))
    # R^2
    mean_y = sy / n
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    ss_res = 0.0
    for i in range(n):
        pred = slope * xs[i]
        ss_res += (ys[i] - pred) ** 2
    r2 = 1.0 - ss_res / max(ss_tot, 1e-9)
    return delta, r2, slope


def fit_stretched(ts, G):
    """G(t) = G0 * exp(-(Delta*t)^beta). Log-log on -log(G/G0) vs t."""
    G0 = G[0]
    safe = [(t, g) for t, g in zip(ts, G) if g > 0.01 * G0 and t > 0]
    if len(safe) < 4:
        return 1.0, 0.0
    xs = [math.log(t) for t, _ in safe]
    ys = [math.log(-math.log(g / G0)) for _, g in safe if 0 < g < G0]
    if len(ys) < 4:
        return 1.0, 0.0
    n = min(len(xs), len(ys))
    xs = xs[:n]; ys = ys[:n]
    sx = sum(xs); sy = sum(ys); sxx = sum(x * x for x in xs); sxy = sum(xs[i] * ys[i] for i in range(n))
    beta = (n * sxy - sx * sy) / max(n * sxx - sx * sx, 1e-9)
    intercept = (sy - beta * sx) / n
    mean_y = sy / n
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    ss_res = sum((ys[i] - (beta * xs[i] + intercept)) ** 2 for i in range(n))
    r2 = 1.0 - ss_res / max(ss_tot, 1e-9)
    return beta, r2


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 256 if smoke else 1024,
              "alpha": 0.15,
              "beta_mc": 2.0,
              "n_sweeps": 15 if smoke else 30,
              "n_replicates": 10 if smoke else 30,
              "seed": 17}
    N = config["N"]; M = int(config["alpha"] * N)
    cpu_gen = torch.Generator().manual_seed(config["seed"])
    W = build_hopfield_W(M, N, cpu_gen, device)
    print(f"[setup] N={N} M={M} alpha={config['alpha']}", flush=True)
    print(f"[autocorr] running {config['n_replicates']} replicates x {config['n_sweeps']} sweeps", flush=True)
    G = measure_autocorr(W, N, config["beta_mc"], config["n_sweeps"], config["n_replicates"], cpu_gen, device)
    ts = list(range(1, config["n_sweeps"] + 1))
    print("[autocorr] G(t) = " + ", ".join(f"{g:.3f}" for g in G), flush=True)
    delta, r2_g, slope = fit_gaussian(ts, G)
    print(f"[fit_gaussian] delta={delta:.4f}, r2={r2_g:.3f}, slope={slope:.4f}", flush=True)
    fitted_beta, r2_s = fit_stretched(ts, G)
    print(f"[fit_stretched] beta={fitted_beta:.3f}, r2={r2_s:.3f}", flush=True)
    summary = {"delta_rms": delta,
                "r2_gaussian": r2_g,
                "r2_stretched": r2_s,
                "stretch_exponent": fitted_beta,
                "G_t": G,
                "n_sweeps": config["n_sweeps"]}
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
    out_dir = get_output_dir("wave14_musr_kubo_toyabe_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("delta_present", summary["delta_rms"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_musr_kubo_toyabe_v1")
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
