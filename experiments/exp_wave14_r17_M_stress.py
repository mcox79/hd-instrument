"""R17 Probe 1 - Substrate W area-law vs volume-law entropy.

R17 landed largely negative. Probe 1 is the cheap analyzer test of whether
substrate W (Hebbian outer-product sum) has area-law or volume-law Renyi-2
entropy scaling.

For W treated as bipartite vector with row-index and col-index subsystems:
  M_A = W[A, :] / ||W||_F  for random row bipartition A
  rho_A = M_A @ M_A.T
  S_2(A) = -log(Tr(rho_A @ rho_A))

Sweep |A|, fit log(S_2) vs log(|A|). Slope ~ 1 = volume; ~ 0 = area-law.

Pre-reg: preregs/2026-05-21_wave14_r17_M_stress.md
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


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required: {missing}")


def compute_verdict(summary):
    slope = summary.get("loglog_slope")
    if slope is None:
        return ("R17_INCONCLUSIVE", "Missing slope.")
    slope = float(slope)
    if slope < 0.4:
        return ("R17_AREA_LAW_LIKE",
                f"Substrate W exhibits area-law-like Renyi-2 entropy scaling: "
                f"log-log slope={slope:.3f} < 0.4. Consistent with Harlow 2017 "
                f"RT-QEC area-law expectation. Substrate may have hidden "
                f"low-dimensional structure.")
    if slope > 0.85:
        return ("R17_VOLUME_LAW",
                f"Substrate W exhibits volume-law Renyi-2 entropy scaling: "
                f"log-log slope={slope:.3f} > 0.85. Substrate is high-dimensional/"
                f"classical; no hidden geometric structure. R17 framework not "
                f"applicable to substrate.")
    return ("R17_INTERMEDIATE",
            f"Substrate W has intermediate entropy scaling: log-log slope="
            f"{slope:.3f} in [0.4, 0.85]. Neither pure area-law nor pure volume-law. "
            f"R17 framework partial fit; needs Probe 2 for clarity.")


def self_test_verdict():
    cases = [
        ({"loglog_slope": 0.2}, "R17_AREA_LAW_LIKE"),
        ({"loglog_slope": 0.95}, "R17_VOLUME_LAW"),
        ({"loglog_slope": 0.6}, "R17_INTERMEDIATE"),
        ({}, "R17_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def renyi_2_for_bipartition(W, A_idx):
    """S_2(A) = -log(Tr(rho_A @ rho_A)) where rho_A = M_A M_A^T / ||W||_F^2.
    Computed without forming rho_A explicitly: Tr(rho_A^2) = ||M_A M_A^T||_F^2 / ||W||_F^4
    = ||M_A^T M_A||_F^2 / ||W||_F^4 (same Frobenius norm).
    Equivalent: sum(sigma^4) / (sum(sigma^2))^2 where sigma = SVs of M_A.
    """
    M_A = W[A_idx, :]
    w_norm_sq = float((W * W).sum())
    # Use M_A M_A^T (small if |A| < N) instead of explicit SVD
    G = M_A @ M_A.T  # (|A|, |A|)
    tr_rho2 = float((G * G).sum()) / max(w_norm_sq * w_norm_sq, 1e-30)
    return -math.log(max(tr_rho2, 1e-30))


def run_one_seed(seed, N, M_stored, fracs, n_bipart_per_frac, device):
    """Build a Hebbian W from M_stored outer products; compute S_2 for sweep of |A|."""
    gen = torch.Generator(device=device).manual_seed(seed)
    # Random bipolar v, k
    V = 2.0 * (torch.rand((M_stored, N), generator=gen, device=device) > 0.5).float() - 1.0
    K = 2.0 * (torch.rand((M_stored, N), generator=gen, device=device) > 0.5).float() - 1.0
    W = (V.T @ K) / N
    s2_by_frac = {}
    for frac in fracs:
        A_size = int(round(frac * N))
        s2_values = []
        for bp in range(n_bipart_per_frac):
            bp_gen = torch.Generator().manual_seed(seed * 31 + bp + 7)
            A_idx = torch.randperm(N, generator=bp_gen)[:A_size].to(device)
            s2 = renyi_2_for_bipartition(W, A_idx)
            s2_values.append(s2)
        s2_by_frac[frac] = {
            "A_size": A_size,
            "s2_mean": sum(s2_values) / len(s2_values),
            "s2_values": s2_values,
        }
    return s2_by_frac


def loglog_slope(xs, ys):
    """Least-squares slope of log(y) vs log(x)."""
    log_x = [math.log(x) for x in xs]
    log_y = [math.log(max(y, 1e-30)) for y in ys]
    n = len(log_x)
    mean_x = sum(log_x) / n
    mean_y = sum(log_y) / n
    num = sum((log_x[i] - mean_x) * (log_y[i] - mean_y) for i in range(n))
    den = sum((log_x[i] - mean_x) ** 2 for i in range(n))
    return num / den if abs(den) > 1e-12 else 0.0


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")  # Probe 1 spec: ZERO GPU
    config = {"mode": "smoke" if smoke else "full",
              "N": 512 if smoke else 2048,
              "M_stored": 256 if smoke else 16384,
              "fracs": [0.125, 0.25, 0.5],
              "seeds": [17] if smoke else [17, 23, 31, 41, 53],
              "n_bipart_per_frac": 3 if smoke else 10}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    all_pairs = []  # (A_size, s2) pairs across seeds for global slope
    for seed in config["seeds"]:
        s2_by_frac = run_one_seed(seed, config["N"], config["M_stored"],
                                       config["fracs"], config["n_bipart_per_frac"], device)
        per_seed[str(seed)] = {str(f): s2_by_frac[f] for f in config["fracs"]}
        for f in config["fracs"]:
            all_pairs.append((s2_by_frac[f]["A_size"], s2_by_frac[f]["s2_mean"]))
        print(f"  seed={seed}: " + " ".join(f"|A|={s2_by_frac[f]['A_size']}:"
                                                  f"S2={s2_by_frac[f]['s2_mean']:.3f}"
                                                  for f in config["fracs"]), flush=True)
    # Mean S_2 per |A|, then fit slope
    s2_per_size = {}
    for size, s2 in all_pairs:
        s2_per_size.setdefault(size, []).append(s2)
    avg_by_size = {size: sum(vs) / len(vs) for size, vs in s2_per_size.items()}
    sizes = sorted(avg_by_size.keys())
    slope = loglog_slope(sizes, [avg_by_size[s] for s in sizes])
    print(f"  log-log slope = {slope:.4f}", flush=True)
    summary = {"per_seed": per_seed, "avg_s2_by_size": {str(k): v for k, v in avg_by_size.items()},
                "loglog_slope": slope, "N": config["N"], "M_stored": config["M_stored"]}
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
    out_dir = get_output_dir("wave14_r17_M_stress_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("loglog_slope_present",
                                    1.0 if summary["loglog_slope"] != 0.0 else 0.0, 0.5)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_r17_M_stress")
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
