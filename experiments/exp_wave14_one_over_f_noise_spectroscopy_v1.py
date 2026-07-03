"""1/f noise spectroscopy — per-neuron activation-trace PSD.

Per Research 2026-05-22 13:55 Entry 140 #4 (P=0.75). Substrate observability:
extract per-neuron activation traces from Glauber MC chain; compute power spectral
density (PSD); fit 1/f^gamma; gamma maps to Cugliandolo-Kurchan 1993 dynamical
hierarchy.

Verdict (gamma ranges per spin-glass dynamical theory):
  ONE_F_GLASSY:        gamma in [0.5, 1.5] (classical 1/f noise = glassy slow modes)
  ONE_F_WHITE:         gamma < 0.3 (white noise = paramagnetic / fast relaxation)
  ONE_F_BROWNIAN:      gamma > 1.7 (Brownian = trapped / extremely slow)
  ONE_F_INTERMEDIATE:  0.3 <= gamma < 0.5 OR 1.5 <= gamma <= 1.7
  ONE_F_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_one_over_f_noise_spectroscopy_v1.md
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
    if "gamma" not in summary:
        return ("ONE_F_INCONCLUSIVE", "Missing gamma.")
    g = summary["gamma"]
    r2 = summary["r2_fit"]
    if r2 < 0.5:
        return ("ONE_F_INCONCLUSIVE",
                f"Low-quality fit r^2={r2:.3f}<0.5; gamma={g:.3f} unreliable.")
    if 0.5 <= g <= 1.5:
        return ("ONE_F_GLASSY",
                f"Classical 1/f noise: gamma={g:.3f} in [0.5, 1.5] (r2={r2:.3f}). "
                f"Substrate has glassy slow modes per Cugliandolo-Kurchan 1993.")
    if g < 0.3:
        return ("ONE_F_WHITE",
                f"White noise: gamma={g:.3f}<0.3 (r2={r2:.3f}). Paramagnetic / fast relaxation.")
    if g > 1.7:
        return ("ONE_F_BROWNIAN",
                f"Brownian / trapped: gamma={g:.3f}>1.7 (r2={r2:.3f}). Extremely slow modes.")
    return ("ONE_F_INTERMEDIATE",
            f"Intermediate gamma={g:.3f} (r2={r2:.3f}). Between regimes.")


def self_test_verdict():
    cases = [
        ({"gamma": 1.0, "r2_fit": 0.8}, "ONE_F_GLASSY"),
        ({"gamma": 0.2, "r2_fit": 0.8}, "ONE_F_WHITE"),
        ({"gamma": 2.0, "r2_fit": 0.8}, "ONE_F_BROWNIAN"),
        ({"gamma": 0.4, "r2_fit": 0.8}, "ONE_F_INTERMEDIATE"),
        ({"gamma": 1.0, "r2_fit": 0.3}, "ONE_F_INCONCLUSIVE"),
        ({}, "ONE_F_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def build_W(M, N, cpu_gen, device):
    bits = (torch.rand((M, N), generator=cpu_gen) > 0.5).to(device)
    patterns = 2.0 * bits.float() - 1.0
    W = (patterns.T @ patterns) / N
    W.fill_diagonal_(0.0)
    return W


def glauber_step_vec(s, W, beta, cpu_gen, device):
    """One sweep of Glauber updates."""
    N = s.shape[0]
    order = torch.randperm(N, generator=cpu_gen).to(device)
    us = torch.rand(N, generator=cpu_gen).to(device)
    for k, idx in enumerate(order):
        h_i = float(W[idx] @ s)
        p_plus = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        s[idx] = 1.0 if float(us[k]) < p_plus else -1.0
    return s


def collect_traces(W, N, beta, n_sweeps, n_burn, n_traced_neurons, cpu_gen, device):
    """Record activation traces for n_traced_neurons over n_sweeps after burn-in."""
    init_bits = (torch.rand(N, generator=cpu_gen) > 0.5).to(device)
    s = 2.0 * init_bits.float() - 1.0
    for _ in range(n_burn):
        s = glauber_step_vec(s, W, beta, cpu_gen, device)
    # Trace first n_traced_neurons
    traces = torch.zeros((n_traced_neurons, n_sweeps), device=device)
    for t in range(n_sweeps):
        s = glauber_step_vec(s, W, beta, cpu_gen, device)
        traces[:, t] = s[:n_traced_neurons]
    return traces


def estimate_psd(trace):
    """One-sided PSD via FFT magnitude squared."""
    T = trace.shape[0]
    F = torch.fft.rfft(trace.float())
    psd = (F.abs() ** 2) / T
    return psd


def fit_power_law(freqs, psd_mean):
    """Fit psd ~ A / f^gamma; log-log linear regression. Use middle frequency band."""
    # Skip DC and Nyquist; use middle decade
    n = len(freqs)
    lo = max(2, n // 10)
    hi = max(lo + 1, n - n // 10)
    xs = [math.log(float(freqs[i])) for i in range(lo, hi) if float(freqs[i]) > 0]
    ys = [math.log(max(float(psd_mean[i]), 1e-12)) for i in range(lo, hi) if float(freqs[i]) > 0]
    if len(xs) < 5:
        return 0.0, 0.0
    m = len(xs)
    sx = sum(xs); sy = sum(ys); sxx = sum(x * x for x in xs); sxy = sum(xs[i] * ys[i] for i in range(m))
    slope = (m * sxy - sx * sy) / max(m * sxx - sx * sx, 1e-9)
    intercept = (sy - slope * sx) / m
    mean_y = sy / m
    ss_tot = sum((y - mean_y) ** 2 for y in ys)
    ss_res = sum((ys[i] - (slope * xs[i] + intercept)) ** 2 for i in range(m))
    r2 = 1.0 - ss_res / max(ss_tot, 1e-9)
    gamma = -slope  # PSD ~ 1/f^gamma
    return gamma, r2


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 256 if smoke else 1024,
              "alpha": 0.15,
              "beta_mc": 2.0,
              "n_burn": 50 if smoke else 200,
              "n_sweeps": 128 if smoke else 512,
              "n_traced_neurons": 20 if smoke else 100,
              "seed": 17}
    N = config["N"]; M = int(config["alpha"] * N)
    cpu_gen = torch.Generator().manual_seed(config["seed"])
    W = build_W(M, N, cpu_gen, device)
    print(f"[setup] N={N} M={M} alpha={config['alpha']} beta={config['beta_mc']}", flush=True)
    print(f"[MC] {config['n_burn']} burn + {config['n_sweeps']} traced sweeps", flush=True)
    traces = collect_traces(W, N, config["beta_mc"], config["n_sweeps"], config["n_burn"],
                              config["n_traced_neurons"], cpu_gen, device)
    print(f"[traces] shape={tuple(traces.shape)}", flush=True)
    psd_list = []
    for k in range(config["n_traced_neurons"]):
        psd_list.append(estimate_psd(traces[k]))
    psd_mean = torch.stack(psd_list, dim=0).mean(dim=0).cpu()
    freqs = torch.arange(psd_mean.shape[0]).float()  # in units of 1/sweep
    gamma, r2 = fit_power_law(freqs, psd_mean)
    print(f"[fit] gamma={gamma:.3f}, r^2={r2:.3f}", flush=True)
    summary = {"gamma": gamma,
                "r2_fit": r2,
                "psd_mean_sample": psd_mean[:20].tolist(),
                "n_freqs": psd_mean.shape[0]}
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
    out_dir = get_output_dir("wave14_one_over_f_noise_spectroscopy_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("psd_present", float(summary["n_freqs"]), 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_one_over_f_noise_spectroscopy_v1")
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
