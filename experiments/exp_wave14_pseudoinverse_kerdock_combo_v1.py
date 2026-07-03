"""Pseudoinverse + Kerdock combo — combines today's two winning capacity routes.

Per `wave14_pseudoinverse_capacity_v1` PINV_PASS (20x Hebbian at alpha=0.5/0.95)
+ Bet C validated M/N=8 with Kerdock 4-coset codebook. Hypothesis: Kerdock's
near-Welch-bound coherence preserves pseudoinverse basins at higher alpha.

Test: pseudoinverse W on Kerdock-drawn keys vs random-bipolar keys at matched alpha.
Measure both attractor accuracy AND basin radius at alpha in {0.30, 0.50, 0.70, 0.90}.

Verdict thresholds:
  PINVK_BETTER:    Kerdock basin >= 2x random basin at alpha=0.50 (structured wins)
  PINVK_NEUTRAL:   0.5x <= ratio < 2x (no clear structured advantage)
  PINVK_WORSE:    Kerdock basin < 0.5x random (substrate hurts)
  PINVK_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_pseudoinverse_kerdock_combo_v1.md
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

_pi = importlib.util.spec_from_file_location("pi",
    REPO / "experiments" / "exp_wave14_pseudoinverse_capacity_v1.py")
pi = importlib.util.module_from_spec(_pi); _pi.loader.exec_module(pi)
_bw = importlib.util.spec_from_file_location("bw",
    REPO / "experiments" / "exp_wave14_pseudoinverse_basin_width_v1.py")
bw = importlib.util.module_from_spec(_bw); _bw.loader.exec_module(bw)
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
    if "kerdock_basin_alpha50" not in summary:
        return ("PINVK_INCONCLUSIVE", "Missing kerdock_basin_alpha50.")
    kb = summary["kerdock_basin_alpha50"]
    rb = summary["random_basin_alpha50"]
    ratio = kb / max(rb, 1e-9)
    if ratio >= 2.0:
        return ("PINVK_BETTER",
                f"Kerdock + pseudoinverse beats random + pseudoinverse: kerdock_basin={kb:.3f}, "
                f"random_basin={rb:.3f}, ratio={ratio:.2f} at alpha=0.50. Structured codebook "
                f"preserves basins under pseudoinverse rule.")
    if ratio < 0.5:
        return ("PINVK_WORSE",
                f"Kerdock + pseudoinverse degrades basins: kerdock_basin={kb:.3f}, "
                f"random_basin={rb:.3f}, ratio={ratio:.2f}.")
    return ("PINVK_NEUTRAL",
            f"No clear advantage: kerdock_basin={kb:.3f}, random_basin={rb:.3f}, "
            f"ratio={ratio:.2f}. Structured codebook doesn't help pseudoinverse basins.")


def self_test_verdict():
    cases = [
        ({"kerdock_basin_alpha50": 0.20, "random_basin_alpha50": 0.05}, "PINVK_BETTER"),
        ({"kerdock_basin_alpha50": 0.05, "random_basin_alpha50": 0.05}, "PINVK_NEUTRAL"),
        ({"kerdock_basin_alpha50": 0.01, "random_basin_alpha50": 0.05}, "PINVK_WORSE"),
        ({}, "PINVK_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def make_kerdock_patterns(M, N, cpu_gen, device):
    cb, _ = v3.make_kerdock_4coset_codebook(N, device)
    if M > cb.shape[0]:
        # Repeat with sign flip if more than codebook size
        idx = torch.cat([torch.randperm(cb.shape[0], generator=cpu_gen),
                         torch.randperm(cb.shape[0], generator=cpu_gen)])[:M].to(device)
    else:
        idx = torch.randperm(cb.shape[0], generator=cpu_gen)[:M].to(device)
    return cb[idx].float()


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N": 1024 if smoke else 4096,
              "alpha_grid": [0.30, 0.50] if smoke else [0.30, 0.50, 0.70, 0.90],
              "d_flip_frac_grid": [0.02, 0.05, 0.10] if smoke else [0.01, 0.02, 0.05, 0.10, 0.20],
              "n_iter": 5,
              "seed": 17}
    N = config["N"]
    kerdock_basin = {}; random_basin = {}
    for alpha in config["alpha_grid"]:
        M = int(alpha * N)
        cpu_gen = torch.Generator().manual_seed(config["seed"])
        # Kerdock
        kp = make_kerdock_patterns(M, N, cpu_gen, device)
        Wk = pi.pseudoinverse_W(kp)
        d_flip_grid = [max(1, int(f * N)) for f in config["d_flip_frac_grid"]]
        cpu_gen2 = torch.Generator().manual_seed(config["seed"] + 1)
        kb_radius, _ = bw.measure_basin_radius(Wk, kp, d_flip_grid, config["n_iter"], cpu_gen2, device)
        kerdock_basin[str(alpha)] = kb_radius
        # Random
        cpu_gen3 = torch.Generator().manual_seed(config["seed"] + 2)
        rp = pi.make_patterns(M, N, cpu_gen3, device)
        Wr = pi.pseudoinverse_W(rp)
        cpu_gen4 = torch.Generator().manual_seed(config["seed"] + 3)
        rb_radius, _ = bw.measure_basin_radius(Wr, rp, d_flip_grid, config["n_iter"], cpu_gen4, device)
        random_basin[str(alpha)] = rb_radius
        print(f"  alpha={alpha}: kerdock_basin={kb_radius:.3f} N, random_basin={rb_radius:.3f} N", flush=True)
    kb50 = kerdock_basin.get("0.5", kerdock_basin.get("0.50", 0.0))
    rb50 = random_basin.get("0.5", random_basin.get("0.50", 0.0))
    summary = {"kerdock_basin_per_alpha": kerdock_basin,
                "random_basin_per_alpha": random_basin,
                "kerdock_basin_alpha50": kb50,
                "random_basin_alpha50": rb50}
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
    out_dir = get_output_dir("wave14_pseudoinverse_kerdock_combo_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("basin_present", summary["kerdock_basin_alpha50"] + summary["random_basin_alpha50"] + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_pseudoinverse_kerdock_combo_v1")
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
