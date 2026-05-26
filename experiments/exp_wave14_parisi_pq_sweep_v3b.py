"""Bet E v3 - Finite-size scaling (6-test battery item #2).

v1 PARISI_DISCRIMINATES_CODEBOOK + v2 RSB_CONFIRMED validated. v3 addresses
the deferred item: vary N, fit Binder cumulant extrapolation to 1/N -> 0.
RSB phase: extrapolated binder remains positive. RS finite-size: declines to 0.

Pre-reg: preregs/2026-05-21_wave14_parisi_pq_sweep_v3b.md
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

_pv1 = importlib.util.spec_from_file_location("pv1", REPO / "experiments" / "exp_wave14_parisi_pq_sweep_v1.py")
pv1 = importlib.util.module_from_spec(_pv1); _pv1.loader.exec_module(pv1)

BINDER_THERMO_THRESHOLD = 0.6  # extrapolated binder must exceed this for RSB thermodynamic


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
    by_ck = summary.get("by_codebook", {})
    if not by_ck:
        return ("PARISI_V3_INCONCLUSIVE", "Missing by_codebook.")
    rsb_codebooks = []
    declining_codebooks = []
    for ck, data in by_ck.items():
        extrap = data.get("binder_extrap_to_inf_N", 0.0)
        slope = data.get("binder_slope_vs_inv_N", 0.0)
        if extrap > BINDER_THERMO_THRESHOLD:
            rsb_codebooks.append((ck, extrap))
        elif slope < -0.5:  # binder drops as N grows
            declining_codebooks.append((ck, slope))
    if rsb_codebooks:
        return ("PARISI_V3_RSB_THERMODYNAMIC",
                f"{len(rsb_codebooks)}/{len(by_ck)} codebooks have extrapolated "
                f"binder > {BINDER_THERMO_THRESHOLD} as 1/N -> 0. RSB phase confirmed "
                f"to thermodynamic limit. Codebooks: " +
                ", ".join(f"{ck}=B_inf={b:.3f}" for ck, b in rsb_codebooks))
    if declining_codebooks:
        return ("PARISI_V3_RSB_FINITE_ONLY",
                f"Binder cumulant DECLINES with N for {len(declining_codebooks)}/"
                f"{len(by_ck)} codebooks. v2 RSB was finite-size; substrate "
                f"converges to RS in thermodynamic limit. Codebooks: " +
                ", ".join(f"{ck}=slope={s:.3f}" for ck, s in declining_codebooks))
    return ("PARISI_V3_INCONCLUSIVE",
            f"No codebook crosses BINDER>0.6 threshold but none declines steeply "
            f"either. Pattern unclear. by_codebook: " +
            ", ".join(f"{ck}=B_inf={d.get('binder_extrap_to_inf_N', 0):.3f},"
                          f"slope={d.get('binder_slope_vs_inv_N', 0):.3f}"
                          for ck, d in by_ck.items()))


def self_test_verdict():
    def mk(b_inf, slope=0.0):
        return {"binder_extrap_to_inf_N": b_inf, "binder_slope_vs_inv_N": slope}
    cases = [
        ({"by_codebook": {"random_bsc": mk(0.7), "hadamard": mk(0.65), "kerdock": mk(0.4)}},
         "PARISI_V3_RSB_THERMODYNAMIC"),
        ({"by_codebook": {"random_bsc": mk(0.3, slope=-1.5),
                              "hadamard": mk(0.4, slope=-0.8)}},
         "PARISI_V3_RSB_FINITE_ONLY"),
        ({"by_codebook": {"random_bsc": mk(0.5, slope=-0.1)}},
         "PARISI_V3_INCONCLUSIVE"),
        ({}, "PARISI_V3_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"{a} != {exp}\n  got: {a}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def linear_fit(xs, ys):
    """Return (slope, intercept). Extrapolate to x=0 via intercept."""
    n = len(xs)
    mx = sum(xs) / n
    my = sum(ys) / n
    num = sum((xs[i] - mx) * (ys[i] - my) for i in range(n))
    den = sum((xs[i] - mx) ** 2 for i in range(n))
    if abs(den) < 1e-12:
        return 0.0, my
    slope = num / den
    intercept = my - slope * mx
    return slope, intercept


def measure_codebook_across_N(codebook_type, Ns, M_mult, seeds, device):
    """For each N: build pool, compute binder. Then fit binder vs 1/N."""
    binders_by_N = {}
    for N in Ns:
        M = M_mult * N
        seed_binders = []
        for seed in seeds:
            pool = pv1.make_pool(codebook_type, N, M, seed * 31 + 7, device)
            overlaps = pv1.edwards_anderson_overlap_distribution(pool, N)
            b = pv1.binder_cumulant(overlaps)
            seed_binders.append(b)
        binders_by_N[N] = sum(seed_binders) / len(seed_binders)
    inv_N = [1.0 / N for N in Ns]
    binder_vals = [binders_by_N[N] for N in Ns]
    slope, intercept = linear_fit(inv_N, binder_vals)
    return {"codebook_type": codebook_type,
             "binders_by_N": {str(N): b for N, b in binders_by_N.items()},
             "binder_slope_vs_inv_N": slope,
             "binder_extrap_to_inf_N": intercept,
             "Ns_tested": Ns}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "Ns": [256, 1024] if smoke else [256, 1024, 4096, 16384],
              "M_mult": 2,
              "codebook_types": ["random_bsc"] if smoke else
                                  ["random_bsc", "hadamard", "kerdock"],
              "seeds": [17] if smoke else [17, 23, 31]}
    print(f"[config] {config}", flush=True)
    by_ck = {}
    for ck in config["codebook_types"]:
        print(f"[codebook {ck}] ...", flush=True)
        r = measure_codebook_across_N(ck, config["Ns"], config["M_mult"],
                                          config["seeds"], device)
        by_ck[ck] = r
        print(f"  binders={r['binders_by_N']}", flush=True)
        print(f"  extrap_to_inf={r['binder_extrap_to_inf_N']:.4f} "
              f"slope_vs_inv_N={r['binder_slope_vs_inv_N']:.4f}", flush=True)
    summary = {"by_codebook": by_ck}
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
    out_dir = get_output_dir("wave14_parisi_pq_sweep_v3b_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    first = list(summary["by_codebook"].values())[0]
    oracle.assert_baseline_high("binder_present",
                                    abs(first["binder_extrap_to_inf_N"]), 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_parisi_pq_sweep_v3b")
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
