"""Pseudoinverse basin width — characterize basin-shrinkage at supra-AGS alpha.

Per Research 2026-05-22 15:15 F2: "as alpha -> 1 the basins shrink to zero" (Cherrier-
Dean-Lefevre 2002 random-orthogonal-model confirms). PINV_PASS smoke showed 20x
ratio over Hebbian at alpha=0.5/0.95 but didn't characterize basin width.

Test: perturb each stored pattern by Hamming distance d_flip; check if substrate
recovers via sync update.

Substrate-product question: at what alpha does basin width drop below practical
threshold (say d_flip > 10% N)?

Verdict thresholds:
  BASIN_USABLE:    basin radius >= 0.10 N at alpha=0.50 (deployment-grade)
  BASIN_NARROW:    0.02 N <= radius < 0.10 N (research-grade only)
  BASIN_COLLAPSED: radius < 0.02 N (basins effectively gone)
  BASIN_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_pseudoinverse_basin_width_v1.md
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

_pi = importlib.util.spec_from_file_location("pi",
    REPO / "experiments" / "exp_wave14_pseudoinverse_capacity_v1.py")
pi = importlib.util.module_from_spec(_pi); _pi.loader.exec_module(pi)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "basin_radius_alpha50" not in summary:
        return ("BASIN_INCONCLUSIVE", "Missing basin_radius_alpha50.")
    r50 = summary["basin_radius_alpha50"]
    radii = summary["basin_radius_per_alpha"]
    if r50 >= 0.10:
        return ("BASIN_USABLE",
                f"Pseudoinverse basin at alpha=0.50: radius={r50:.3f} N (>=0.10 N deployment-grade). "
                f"Per-alpha radii: {radii}. F2 learning rule deployment-viable.")
    if r50 >= 0.02:
        return ("BASIN_NARROW",
                f"Basin at alpha=0.50: radius={r50:.3f} N (0.02 <= r < 0.10 N research-grade). "
                f"Per-alpha radii: {radii}. F2 narrow but usable for exact patterns.")
    return ("BASIN_COLLAPSED",
            f"Basin at alpha=0.50: radius={r50:.3f} N (<0.02 N collapsed). "
            f"Per-alpha radii: {radii}. F2 storage gain useless without exact-pattern access.")


def self_test_verdict():
    cases = [
        ({"basin_radius_alpha50": 0.20, "basin_radius_per_alpha": {}}, "BASIN_USABLE"),
        ({"basin_radius_alpha50": 0.05, "basin_radius_per_alpha": {}}, "BASIN_NARROW"),
        ({"basin_radius_alpha50": 0.01, "basin_radius_per_alpha": {}}, "BASIN_COLLAPSED"),
        ({}, "BASIN_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def measure_basin_radius(W, patterns, d_flip_grid, n_iter, cpu_gen, device):
    """For each d_flip, fraction of patterns recovered. Basin radius = largest d_flip where >=0.90."""
    N = patterns.shape[1]
    M = patterns.shape[0]
    recovered_per_d = {}
    for d_flip in d_flip_grid:
        n_test = min(50, M)
        correct = 0
        for i in range(n_test):
            flip_mask = (torch.randperm(N, generator=cpu_gen)[:d_flip]).to(device)
            s = patterns[i].clone()
            s[flip_mask] = -s[flip_mask]
            for _ in range(n_iter):
                s = torch.sign(W @ s)
                s[s == 0] = 1.0
            match = float((s * patterns[i]).mean())
            if match > 0.95: correct += 1
        recovered_per_d[d_flip] = correct / n_test
    # Basin radius = largest d_flip where recovery >= 0.90
    basin = 0
    for d in sorted(d_flip_grid):
        if recovered_per_d[d] >= 0.90:
            basin = d
    return basin / patterns.shape[1], recovered_per_d


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 256 if smoke else 1024,
              "alpha_grid": [0.30, 0.50] if smoke else [0.10, 0.30, 0.50, 0.70, 0.90],
              "d_flip_frac_grid": [0.02, 0.10] if smoke else [0.01, 0.02, 0.05, 0.10, 0.20, 0.30],
              "n_iter": 5,
              "seed": 17}
    N = config["N"]
    basin_per_alpha = {}
    full_recovery_per_alpha = {}
    for alpha in config["alpha_grid"]:
        M = int(alpha * N)
        cpu_gen = torch.Generator().manual_seed(config["seed"])
        patterns = pi.make_patterns(M, N, cpu_gen, device)
        W = pi.pseudoinverse_W(patterns)
        d_flip_grid = [max(1, int(f * N)) for f in config["d_flip_frac_grid"]]
        radius_frac, recovery = measure_basin_radius(W, patterns, d_flip_grid, config["n_iter"], cpu_gen, device)
        basin_per_alpha[str(alpha)] = radius_frac
        full_recovery_per_alpha[str(alpha)] = {str(d): r for d, r in recovery.items()}
        print(f"  alpha={alpha} (M={M}): basin_radius={radius_frac:.3f} N", flush=True)
        for d in sorted(d_flip_grid):
            print(f"    d_flip={d} ({d/N:.2%} N): recovery={recovery[d]:.3f}", flush=True)
    r50 = basin_per_alpha.get("0.5", basin_per_alpha.get("0.50", 0.0))
    summary = {"basin_radius_per_alpha": basin_per_alpha,
                "basin_radius_alpha50": r50,
                "recovery_detail": full_recovery_per_alpha}
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
    out_dir = get_output_dir("wave14_pseudoinverse_basin_width_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("basin_present", summary["basin_radius_alpha50"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_pseudoinverse_basin_width_v1")
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
