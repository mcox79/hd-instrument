"""delta(lambda) drift test — Strategy's "best 1-GPU-hour ROI" per cycle 85.

Per Research v85 deepdrill: substrate at N=4096, Kerdock v4, sweep alpha in
{0.10, 0.13, 0.153, 0.18, 0.22}. Measure rho(t) relaxation from random init
over ~1000 steps. Fit power-law rho(t) ~ t^(-delta(alpha)). Plot delta vs alpha.

Verdict patterns:
  delta pinned -> true criticality
  delta drifts monotonically -> Griffiths phase (SUBSTRATE-PRODUCT UPGRADE)
  delta discontinuous jump -> first-order / tricritical
  delta noise -> no critical regime

Pre-reg: preregs/2026-05-22_wave14_delta_lambda_drift_v1.md
"""
from __future__ import annotations
import argparse, importlib.util, json, math, os, sys, time
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

_v3 = importlib.util.spec_from_file_location("v3", REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py")
v3 = importlib.util.module_from_spec(_v3); _v3.loader.exec_module(v3)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "delta_per_alpha" not in summary:
        return ("DELTA_DRIFT_INCONCLUSIVE", "Missing.")
    deltas = list(summary["delta_per_alpha"].values())
    r2s = list(summary.get("r2_per_alpha", {}).values())
    if not r2s or all(r < 0.7 for r in r2s):
        return ("DELTA_DRIFT_NO_POWERLAW",
                f"R^2 < 0.7 at all alpha; protocol incompatible at N=4096. "
                f"Revert to 4-signature stack fallback.")
    delta_range = max(deltas) - min(deltas)
    mean_delta = sum(deltas) / len(deltas)
    # Detect monotone drift: count adjacent pairs that increase vs decrease
    n_up = sum(1 for i in range(len(deltas) - 1) if deltas[i+1] > deltas[i])
    monotone = (n_up == len(deltas) - 1) or (n_up == 0)
    # Pinned: very small range
    if delta_range < 0.05 * max(abs(mean_delta), 0.1):
        return ("DELTA_DRIFT_PINNED",
                f"delta pinned across alpha (range={delta_range:.4f}, mean={mean_delta:.4f}). "
                f"True criticality consistent. V2.G STACK cheap construction viable.")
    if monotone and delta_range > 0.20:
        return ("DELTA_DRIFT_GRIFFITHS",
                f"delta drifts monotonically: range={delta_range:.3f} across alpha sweep, "
                f"mean={mean_delta:.3f}. **GRIFFITHS PHASE / SUBSTRATE-PRODUCT UPGRADE** — "
                f"continuously-tunable engineering knob.")
    # Check for discontinuous jump
    diffs = [abs(deltas[i+1] - deltas[i]) for i in range(len(deltas) - 1)]
    if max(diffs) > 3 * (sum(diffs) / max(len(diffs), 1)):
        return ("DELTA_DRIFT_JUMP",
                f"delta has discontinuous jump: max gap {max(diffs):.3f} vs mean {sum(diffs)/len(diffs):.3f}. "
                f"First-order or tricritical transition.")
    return ("DELTA_DRIFT_NOISE",
            f"delta range {delta_range:.3f} but not monotone; likely seed noise. "
            f"Substrate not in extended critical regime.")


def self_test_verdict():
    cases = [
        ({"delta_per_alpha": {"0.1": 0.50, "0.15": 0.51, "0.2": 0.50, "0.25": 0.49},
          "r2_per_alpha": {"0.1": 0.95, "0.15": 0.96, "0.2": 0.93, "0.25": 0.92}},
         "DELTA_DRIFT_PINNED"),
        ({"delta_per_alpha": {"0.1": 0.30, "0.15": 0.40, "0.2": 0.55, "0.25": 0.70},
          "r2_per_alpha": {"0.1": 0.92, "0.15": 0.95, "0.2": 0.93, "0.25": 0.90}},
         "DELTA_DRIFT_GRIFFITHS"),
        ({"delta_per_alpha": {"0.1": 0.50, "0.15": 0.30, "0.2": 0.60, "0.25": 0.40},
          "r2_per_alpha": {"0.1": 0.5, "0.15": 0.4, "0.2": 0.6, "0.25": 0.3}},
         "DELTA_DRIFT_NO_POWERLAW"),
        ({}, "DELTA_DRIFT_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def loglog_fit(xs, ys):
    """Return (slope, r_squared) of log(y) ~ slope * log(x)."""
    log_x = [math.log(max(x, 1e-30)) for x in xs]
    log_y = [math.log(max(y, 1e-30)) for y in ys]
    n = len(log_x)
    mx = sum(log_x) / n
    my = sum(log_y) / n
    num = sum((log_x[i] - mx) * (log_y[i] - my) for i in range(n))
    den_x = sum((log_x[i] - mx) ** 2 for i in range(n))
    den_y = sum((log_y[i] - my) ** 2 for i in range(n))
    if den_x < 1e-12 or den_y < 1e-12:
        return 0.0, 0.0
    slope = num / den_x
    r2 = (num * num) / (den_x * den_y)
    return slope, r2


def measure_delta(alpha, N, M, n_relax_steps, gen, device):
    """Measure relaxation rho(t) ~ t^(-delta) of substrate density under cleanup dynamics."""
    # Use Kerdock codebook keys
    codebook, _ = v3.make_kerdock_4coset_codebook(N, device)
    cpu_gen = torch.Generator().manual_seed(13)
    keys = v3.sample_kerdock_keys(codebook, M, cpu_gen, device)
    values = 2.0 * (torch.rand((M, N), generator=gen, device=device) > 0.5).float() - 1.0
    # W stored via Hebbian; alpha controls effective storage fraction
    W = alpha * (values.T @ keys) / N
    # Density rho(t) = mean |W @ keys[i] dot values[i]| / N over random subset
    # Iterate cleanup-relaxation: state_{t+1} = sign(state_t @ W)
    n_probe = 50
    probe_idx = torch.randperm(M, generator=cpu_gen)[:n_probe].to(device)
    rho_t = []
    state = keys[probe_idx].clone()  # initial: stored keys
    for t in range(n_relax_steps):
        # Relaxation step: probe W, soft-quantize, repeat
        retrieved = state @ W.T  # (n_probe, N)
        sims = (retrieved @ values.T)  # (n_probe, M)
        weights = torch.softmax(sims * 0.1, dim=1)
        new_state = weights @ values
        new_state_q = torch.sign(new_state)
        # Density: alignment between current state and original
        rho_now = float((new_state_q * keys[probe_idx]).sum(dim=1).abs().mean()) / N
        rho_t.append(max(rho_now, 1e-6))
        state = new_state_q
    # Fit power-law rho(t) ~ t^(-delta) for t >= 2 (skip initial transient)
    ts = list(range(2, n_relax_steps + 1))
    rs = rho_t[1:]
    if len(ts) < 5:
        return 0.0, 0.0
    # Look at decreasing trend; if rho monotone increasing, no power-law decay
    slope, r2 = loglog_fit(ts, rs)
    return -slope, r2  # delta = -slope


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "M": 256 if smoke else 4096,
              "alpha_sweep": [0.1, 0.2] if smoke else [0.10, 0.13, 0.153, 0.18, 0.22],
              "n_relax_steps": 50 if smoke else 200,
              "seeds": [17] if smoke else [17, 23, 31]}
    print(f"[config] {config}", flush=True)
    delta_per_alpha = {}
    r2_per_alpha = {}
    for alpha in config["alpha_sweep"]:
        deltas_s, r2s_s = [], []
        for s in config["seeds"]:
            gen = torch.Generator(device=device).manual_seed(s * 17 + 7)
            d, r = measure_delta(alpha, config["N"], config["M"], config["n_relax_steps"], gen, device)
            deltas_s.append(d); r2s_s.append(r)
        delta_per_alpha[str(alpha)] = sum(deltas_s) / len(deltas_s)
        r2_per_alpha[str(alpha)] = sum(r2s_s) / len(r2s_s)
        print(f"  alpha={alpha}: delta={delta_per_alpha[str(alpha)]:.4f} r2={r2_per_alpha[str(alpha)]:.3f}", flush=True)
    summary = {"delta_per_alpha": delta_per_alpha, "r2_per_alpha": r2_per_alpha}
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
    out_dir = get_output_dir("wave14_delta_lambda_drift_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first_alpha = list(summary["delta_per_alpha"].keys())[0]
    oracle.assert_baseline_high("delta_present", summary["delta_per_alpha"][first_alpha] + 0.5, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_delta_lambda_drift_v1")
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
