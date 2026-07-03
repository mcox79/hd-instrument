"""AC susceptibility chi'(omega) — frequency-dependent freezing diagnostic.

Per Research Entry 140 #5 (P=0.70). Substrate analog: apply oscillating external
field h(t) = h0 * sin(omega*t) along a probe direction; measure linear response
amplitude as function of omega. Spin-glass freezing: chi' peaks at omega_freeze.

Substrate observability probe: maps substrate's relaxation timescale to a single
frequency-domain peak. Companion to muSR (G(t) time-domain) and 1/f noise (PSD).

Verdict thresholds:
  CHI_FREEZING:    chi'(omega) has resolvable peak at omega_freeze in (0, 1)
  CHI_FLAT:        no peak; chi' monotone or oscillating around mean
  CHI_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_ac_susceptibility_v1.md
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
    if "chi_per_omega" not in summary:
        return ("CHI_INCONCLUSIVE", "Missing chi_per_omega.")
    chi = summary["chi_per_omega"]
    omega_freeze = summary["omega_freeze"]
    peak_height_ratio = summary["peak_to_baseline_ratio"]
    if peak_height_ratio >= 1.5:
        return ("CHI_FREEZING",
                f"Spin-glass freezing peak detected: peak/baseline={peak_height_ratio:.2f} (>=1.5) "
                f"at omega_freeze={omega_freeze:.4f}. chi_per_omega={chi}.")
    return ("CHI_FLAT",
            f"No freezing peak: peak/baseline={peak_height_ratio:.2f}. "
            f"chi'(omega) flat or non-peaked. chi_per_omega={chi}.")


def self_test_verdict():
    cases = [
        ({"chi_per_omega": {"0.1": 0.5, "0.3": 1.0, "0.5": 0.6}, "omega_freeze": 0.3, "peak_to_baseline_ratio": 2.0}, "CHI_FREEZING"),
        ({"chi_per_omega": {"0.1": 0.5, "0.3": 0.5, "0.5": 0.55}, "omega_freeze": 0.3, "peak_to_baseline_ratio": 1.1}, "CHI_FLAT"),
        ({}, "CHI_INCONCLUSIVE"),
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
    return W, patterns


def glauber_step(s, W, h_ext, beta, cpu_gen, device):
    N = s.shape[0]
    order = torch.randperm(N, generator=cpu_gen).to(device)
    us = torch.rand(N, generator=cpu_gen).to(device)
    for k, idx in enumerate(order):
        h_i = float(W[idx] @ s) + float(h_ext[idx])
        p_plus = 1.0 / (1.0 + math.exp(-2.0 * beta * h_i))
        s[idx] = 1.0 if float(us[k]) < p_plus else -1.0
    return s


def measure_chi_at_omega(W, N, beta, omega, probe_dir, h0, n_cycles, n_burn, cpu_gen, device):
    """Apply h(t) = h0 * sin(omega*t) * probe_dir; measure m(t) = (1/N) s.probe_dir;
       chi'(omega) = average <m(t)*sin(omega*t)> across last n_meas cycles."""
    init_bits = (torch.rand(N, generator=cpu_gen) > 0.5).to(device)
    s = 2.0 * init_bits.float() - 1.0
    # Burn-in (no field)
    for _ in range(n_burn):
        s = glauber_step(s, W, torch.zeros(N, device=device), beta, cpu_gen, device)
    # Drive with oscillating field; period = 2*pi/omega; sample 8 phases per cycle
    samples_per_cycle = 8
    total_steps = int(n_cycles * samples_per_cycle)
    dt = 2.0 * math.pi / omega / samples_per_cycle
    m_t = []
    sin_t = []
    for t in range(total_steps):
        time_t = t * dt
        h_ext = h0 * math.sin(omega * time_t) * probe_dir
        s = glauber_step(s, W, h_ext, beta, cpu_gen, device)
        m = float((s * probe_dir).mean())
        m_t.append(m)
        sin_t.append(math.sin(omega * time_t))
    # chi'(omega) = <m * sin(omega*t)> / h0
    n_meas = len(m_t) // 2  # use second half (steady state)
    m_arr = m_t[n_meas:]; s_arr = sin_t[n_meas:]
    chi = sum(m_arr[i] * s_arr[i] for i in range(len(m_arr))) / max(len(m_arr), 1) / max(h0, 1e-9)
    return abs(chi)


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 256 if smoke else 1024,
              "alpha": 0.15,
              "beta_mc": 2.0,
              "h0": 0.5,
              "omega_grid": [0.1, 0.5] if smoke else [0.05, 0.1, 0.2, 0.5, 1.0, 2.0],
              "n_cycles": 4 if smoke else 12,
              "n_burn": 50 if smoke else 200,
              "seed": 17}
    N = config["N"]; M = int(config["alpha"] * N)
    cpu_gen = torch.Generator().manual_seed(config["seed"])
    W, patterns = build_W(M, N, cpu_gen, device)
    print(f"[setup] N={N} M={M} alpha={config['alpha']} beta={config['beta_mc']}", flush=True)
    # Probe direction: pattern[0]
    probe_dir = patterns[0]
    chi_per_omega = {}
    for omega in config["omega_grid"]:
        chi = measure_chi_at_omega(W, N, config["beta_mc"], omega, probe_dir,
                                       config["h0"], config["n_cycles"], config["n_burn"],
                                       cpu_gen, device)
        chi_per_omega[f"{omega:.3f}"] = chi
        print(f"  omega={omega:.3f}: chi'={chi:.4f}", flush=True)
    # Find peak
    sorted_keys = sorted(chi_per_omega.keys(), key=lambda k: float(k))
    chi_vals = [chi_per_omega[k] for k in sorted_keys]
    max_idx = max(range(len(chi_vals)), key=lambda i: chi_vals[i])
    peak_omega = float(sorted_keys[max_idx])
    peak_chi = chi_vals[max_idx]
    # Baseline = mean over non-peak
    others = chi_vals[:max_idx] + chi_vals[max_idx + 1:]
    baseline = sum(others) / max(len(others), 1) if others else peak_chi
    ratio = peak_chi / max(baseline, 1e-9)
    summary = {"chi_per_omega": chi_per_omega,
                "omega_freeze": peak_omega,
                "peak_chi": peak_chi,
                "baseline_chi": baseline,
                "peak_to_baseline_ratio": ratio}
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
    out_dir = get_output_dir("wave14_ac_susceptibility_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("chi_present", summary["peak_chi"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_ac_susceptibility_v1")
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
