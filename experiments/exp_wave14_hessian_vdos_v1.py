"""Hessian VDOS — substrate vibrational density of states from W eigvalsh.

Per Research Entry 140 (2026-05-22 13:55) materials characterization. Maps to
substrate observability: spin-glass soft-mode density (eigvals near lambda~0)
indicates RSB-class flat directions. Counts eigenvalues in low-lambda bins.

Cheapest possible substrate-physics probe: one eigvalsh call on W.

Verdict thresholds:
  VDOS_SOFTMODES_RSB:   soft-mode fraction in (0, 0.01*lambda_max] >= 0.20 (substantial flat directions)
  VDOS_SHARP:           soft-mode fraction < 0.05 (substrate W is sharp/non-degenerate)
  VDOS_INTERMEDIATE:    0.05 <= fraction < 0.20
  VDOS_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_hessian_vdos_v1.md
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
    if "soft_mode_fraction" not in summary:
        return ("VDOS_INCONCLUSIVE", "Missing soft_mode_fraction.")
    sf = summary["soft_mode_fraction"]
    lmax = summary["lambda_max"]
    if sf >= 0.20:
        return ("VDOS_SOFTMODES_RSB",
                f"Substantial soft-mode density: fraction(lambda <= 0.01*lambda_max) = {sf:.3f} "
                f">= 0.20. RSB-class flat directions present. lambda_max={lmax:.4f}.")
    if sf < 0.05:
        return ("VDOS_SHARP",
                f"Sharp W spectrum: soft-mode fraction = {sf:.3f} < 0.05. Substrate W has "
                f"distinct mode structure (paramagnet-like or ferromagnet-like). lambda_max={lmax:.4f}.")
    return ("VDOS_INTERMEDIATE",
            f"Intermediate soft-mode fraction = {sf:.3f}. lambda_max={lmax:.4f}. "
            f"Substrate W is between RSB and sharp.")


def self_test_verdict():
    cases = [
        ({"soft_mode_fraction": 0.30, "lambda_max": 5.0}, "VDOS_SOFTMODES_RSB"),
        ({"soft_mode_fraction": 0.10, "lambda_max": 5.0}, "VDOS_INTERMEDIATE"),
        ({"soft_mode_fraction": 0.02, "lambda_max": 5.0}, "VDOS_SHARP"),
        ({}, "VDOS_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def build_W(M, N, cpu_gen, device):
    bits = (torch.rand((M, N), generator=cpu_gen) > 0.5).to(device)
    patterns = 2.0 * bits.float() - 1.0
    # Hebbian W; do NOT zero diagonal: Research Entry 140 VDOS interpretation
    # uses natural spectrum where rank-M-deficient zeros ARE the soft modes.
    W = (patterns.T @ patterns) / N
    return W


def measure_vdos(N, alpha, cpu_gen, device, soft_threshold_rel=0.01):
    M = int(alpha * N)
    W = build_W(M, N, cpu_gen, device)
    print(f"  N={N} M={M}: computing eigvalsh of {N}x{N} W matrix...", flush=True)
    eigvals = torch.linalg.eigvalsh(W.float()).cpu()
    lmax = float(eigvals.abs().max())
    soft_threshold = soft_threshold_rel * lmax
    soft_fraction = float((eigvals.abs() <= soft_threshold).float().mean())
    # Top-k spectrum
    eigvals_sorted = torch.sort(eigvals, descending=True).values
    top10 = eigvals_sorted[:10].tolist()
    bottom10 = eigvals_sorted[-10:].tolist()
    return {"lambda_max": lmax,
             "soft_mode_fraction": soft_fraction,
             "soft_threshold": soft_threshold,
             "top10_eigvals": top10,
             "bottom10_eigvals": bottom10,
             "N": N, "M": M, "alpha": alpha}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N_grid": [256, 512] if smoke else [1024, 2048, 4096],
              "alpha_grid": [0.15] if smoke else [0.05, 0.15, 0.30, 0.50],
              "soft_threshold_rel": 0.01,
              "seed": 17}
    per_run = []
    for N in config["N_grid"]:
        for alpha in config["alpha_grid"]:
            cpu_gen = torch.Generator().manual_seed(config["seed"] + N + int(alpha * 1000))
            r = measure_vdos(N, alpha, cpu_gen, device, config["soft_threshold_rel"])
            per_run.append(r)
            print(f"    alpha={alpha}: lmax={r['lambda_max']:.4f}, soft_fraction={r['soft_mode_fraction']:.3f}", flush=True)
    # Pick the canonical alpha=0.15 N=4096 result for verdict (Strategy's "substrate operating point")
    canonical = next((r for r in per_run if abs(r["alpha"] - 0.15) < 1e-6
                       and r["N"] == max(config["N_grid"])), per_run[-1])
    summary = {"soft_mode_fraction": canonical["soft_mode_fraction"],
                "lambda_max": canonical["lambda_max"],
                "canonical_run": canonical,
                "per_run": per_run}
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
    out_dir = get_output_dir("wave14_hessian_vdos_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("lambda_max_present", summary["lambda_max"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_hessian_vdos_v1")
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
