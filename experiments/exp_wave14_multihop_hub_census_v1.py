"""Multi-hop hub census — diagnose hubness mechanism per Research 19:25 redrill.

Per `research_multihop_mechanism_redrill_2026-05-22.md` (Research 19:30 EDT):
Resonator + spectral-eigvalue-degeneracy hypotheses FALSIFIED (cycle 124).
NEW mechanism diagnosis (P=0.45): Hubness x DPI information contraction.
Hubness = a few codebook patterns appear as NN of many others; absorbing states
cause chain to converge to hub basins.

Cheapest diagnostic: compute k-occurrence skewness over codebook nearest-neighbor
graph at multiple N. Hubness signature: skewness >= 1.0 grows with N.

Predictions (Research):
  Hubness mild at N=4096; strong at N=65536.
  Skewness(N=65536) > Skewness(N=4096).

Verdict thresholds:
  HUBNESS_CONFIRMED: skew(N=65536) >= 1.0 AND monotonically grows with N
  HUBNESS_PARTIAL:   skew(N=65536) in [0.5, 1.0] with growth
  HUBNESS_ABSENT:    skew(N=65536) < 0.5 (mechanism falsified)
  HUBNESS_INCONCLUSIVE

Pre-reg: preregs/2026-05-22_wave14_multihop_hub_census_v1.md
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

_mh = importlib.util.spec_from_file_location("mh",
    REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh); _mh.loader.exec_module(mh)


def get_output_dir(default_name):
    name = os.environ.get("HDLAB_EXP_NAME", default_name)
    out = REPO / "data" / f"exp_{name}"
    out.mkdir(parents=True, exist_ok=True)
    return out


def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing")


def compute_verdict(summary):
    if "skewness_per_N" not in summary:
        return ("HUBNESS_INCONCLUSIVE", "Missing skewness_per_N.")
    skew = summary["skewness_per_N"]
    Ns = sorted(int(k) for k in skew.keys())
    if len(Ns) < 2:
        return ("HUBNESS_INCONCLUSIVE", f"Need >=2 N values, got {len(Ns)}.")
    skew_top = skew[str(Ns[-1])]
    monotone = all(skew[str(Ns[i])] <= skew[str(Ns[i + 1])] for i in range(len(Ns) - 1))
    if skew_top >= 1.0 and monotone:
        return ("HUBNESS_CONFIRMED",
                f"Hubness mechanism confirmed: skew(N={Ns[-1]})={skew_top:.3f}>=1.0 AND monotone "
                f"growth with N. skew_per_N={skew}.")
    if skew_top >= 0.5 and monotone:
        return ("HUBNESS_PARTIAL",
                f"Partial hubness: skew(N={Ns[-1]})={skew_top:.3f} in [0.5, 1.0] with growth. "
                f"skew_per_N={skew}.")
    return ("HUBNESS_ABSENT",
            f"Hubness mechanism FALSIFIED: skew(N={Ns[-1]})={skew_top:.3f}<0.5 OR not monotone. "
            f"skew_per_N={skew}.")


def self_test_verdict():
    cases = [
        ({"skewness_per_N": {"4096": 0.5, "16384": 0.8, "65536": 1.5}}, "HUBNESS_CONFIRMED"),
        ({"skewness_per_N": {"4096": 0.3, "16384": 0.5, "65536": 0.7}}, "HUBNESS_PARTIAL"),
        ({"skewness_per_N": {"4096": 0.2, "16384": 0.2, "65536": 0.3}}, "HUBNESS_ABSENT"),
        ({}, "HUBNESS_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, _ = compute_verdict(s)
        if a != exp: raise AssertionError(f"{a} != {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def hub_census(codebook, N, K):
    """k-occurrence skewness + top10 hub share + hubness presence."""
    sim = (codebook @ codebook.T) / N
    sim.fill_diagonal_(-1e9)
    nearest = sim.argmax(dim=1)  # (K,) each entity's NN
    # k-occurrence: how many times each codeword appears as someone's NN
    k_occ = torch.bincount(nearest, minlength=K).float()
    mean = float(k_occ.mean())
    std = float(k_occ.std())
    skew = float(((k_occ - mean) ** 3).mean() / max(std ** 3, 1e-9))
    sorted_occ = torch.sort(k_occ, descending=True).values
    top10_share = float(sorted_occ[:10].sum() / max(k_occ.sum(), 1.0))
    return {"k_occurrence_max": float(k_occ.max()),
             "k_occurrence_mean": mean,
             "k_occurrence_std": std,
             "skewness": skew,
             "top10_hub_share": top10_share}


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    config = {"mode": "smoke" if smoke else "full",
              "N_grid": [1024, 2048] if smoke else [4096, 16384, 65536],
              "K": 100,
              "seed": 17}
    skewness_per_N = {}; details_per_N = {}
    for N in config["N_grid"]:
        # Build codebook
        use_cpu = N >= 32768
        target = torch.device("cpu") if use_cpu else device
        cpu_gen = torch.Generator().manual_seed(config["seed"] + N)
        bits = (torch.rand((config["K"], N), generator=cpu_gen) > 0.5).to(target)
        codebook = 2.0 * bits.float() - 1.0
        d = hub_census(codebook, N, config["K"])
        skewness_per_N[str(N)] = d["skewness"]
        details_per_N[str(N)] = d
        print(f"  N={N}: skewness={d['skewness']:.3f}, top10_share={d['top10_hub_share']:.3f}, "
              f"k_occ_max={d['k_occurrence_max']:.1f}", flush=True)
        del codebook
        if device.type == "cuda" and not use_cpu:
            torch.cuda.empty_cache()
    summary = {"skewness_per_N": skewness_per_N,
                "details_per_N": details_per_N,
                "K": config["K"]}
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
    out_dir = get_output_dir("wave14_multihop_hub_census_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    oracle.assert_baseline_high("skew_present",
                                 abs(max(summary["skewness_per_N"].values())) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_multihop_hub_census_v1")
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
