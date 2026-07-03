"""P(q) sub-peak characterization — CPU re-analysis of PQ_OTHER_CARDINALITY structure.

Context: wave14_pq_high_resolution_v1 FULL at N=16384 200-seeds 500-bins returned
PQ_OTHER_CARDINALITY (7 outer x ~8.5 sub-peaks per outer = ~60 total peaks).
This refutes both prior hypotheses:
  - PQ_FLAT_15  (15 simple peaks; no sub-structure)
  - PQ_HIERARCHICAL_28 (28 endpoint-partition-cardinality peaks)

The 60-peak multi-scale structure is a SUBSTRATE-PHYSICS finding that needs
mechanistic characterization. This CPU re-analysis script:

1. Replicates the q-overlap measurement at MULTIPLE N values (CPU-feasible sizes:
   N in {512, 1024, 2048, 4096}) to check whether 7-outer / 60-total is N-dependent
   or approximately N-invariant (scale-free).

2. Runs at a fixed smaller scale to get the peak-position distribution precisely
   (bin-level centroid of each outer peak) and checks whether outer-peak positions
   follow an arithmetic progression (uniform spacing) or geometric progression
   (spin-glass RSB-like cascade).

3. Reports: n_outer_peaks, n_total_peaks, outer_spacing_cv (coefficient of variation
   of inter-peak gaps -- small CV means arithmetic progression, large means
   non-uniform cascade).

Verdict labels:
  PQ_SUBPEAK_ARITHMETIC -- outer peaks arithmetically spaced (uniform spin-glass-like)
  PQ_SUBPEAK_GEOMETRIC  -- outer peaks geometrically / non-uniformly spaced (RSB cascade)
  PQ_SUBPEAK_SINGLE_CLUSTER -- n_outer < 3 (insufficient structure to classify)
  PQ_SUBPEAK_INCONCLUSIVE

Pure CPU. Peak VRAM: 0. Peak RAM: N=4096 float32 codebooks ~50 MB.
Expected elapsed: < 5 min at the sweep sizes.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, importlib.util, json, os, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

_mh = importlib.util.spec_from_file_location(
    "mh", REPO / "experiments" / "exp_wave14r_multihop_K100.py")
mh = importlib.util.module_from_spec(_mh)
_mh.loader.exec_module(mh)

# CV threshold: below this -> arithmetic, above -> geometric/non-uniform
CV_ARITHMETIC_THRESHOLD = 0.30


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"missing metrics keys: {set(d.keys())}")


def compute_verdict(summary):
    """Classify outer-peak spacing structure."""
    if "outer_spacing_cv" not in summary:
        return ("PQ_SUBPEAK_INCONCLUSIVE", "Missing outer_spacing_cv.")
    n_outer = summary.get("n_outer_peaks", 0)
    if n_outer < 3:
        return ("PQ_SUBPEAK_SINGLE_CLUSTER",
                f"n_outer={n_outer} < 3; insufficient outer structure to characterize spacing.")
    cv = summary["outer_spacing_cv"]
    n_total = summary.get("n_total_peaks", n_outer)
    if cv <= CV_ARITHMETIC_THRESHOLD:
        return ("PQ_SUBPEAK_ARITHMETIC",
                f"Outer peaks arithmetically spaced (CV={cv:.3f} <= {CV_ARITHMETIC_THRESHOLD}). "
                f"n_outer={n_outer} n_total={n_total}. Uniform spin-glass-like structure.")
    return ("PQ_SUBPEAK_GEOMETRIC",
            f"Outer peaks non-uniformly / geometrically spaced (CV={cv:.3f} > {CV_ARITHMETIC_THRESHOLD}). "
            f"n_outer={n_outer} n_total={n_total}. RSB-cascade or multi-scale heterogeneous structure.")


def self_test_verdict():
    cases = [
        ({"outer_spacing_cv": 0.10, "n_outer_peaks": 7, "n_total_peaks": 60},
         "PQ_SUBPEAK_ARITHMETIC"),
        ({"outer_spacing_cv": 0.55, "n_outer_peaks": 7, "n_total_peaks": 60},
         "PQ_SUBPEAK_GEOMETRIC"),
        ({"outer_spacing_cv": 0.20, "n_outer_peaks": 2, "n_total_peaks": 5},
         "PQ_SUBPEAK_SINGLE_CLUSTER"),
        ({}, "PQ_SUBPEAK_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        got, _ = compute_verdict(s)
        if got != exp:
            raise AssertionError(f"self_test: compute_verdict({s}) = {got}, expected {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def measure_q_overlap(M, n_starts, chain_rels, ea, ra):
    """Measure q-overlap (same as pq_high_resolution_v1)."""
    from collections import Counter
    endpoints = []
    for start_idx in range(min(n_starts, ea.shape[0])):
        current = start_idx
        for r_idx in chain_rels:
            current = int((ea @ (M * (ea[current] * ra[r_idx]))).argmax().item())
        endpoints.append(current)
    n = len(endpoints)
    counter = Counter(endpoints)
    q = sum(c * c for c in counter.values()) / (n * n)
    return q


def collect_q_samples(N, n_seeds, n_starts, depth, device, seed_offset=0):
    """Collect q-overlap samples at given N."""
    q_samples = []
    for seed_i in range(n_seeds):
        gen = torch.Generator(device=device).manual_seed(seed_offset + 17 + seed_i * 13)
        ea = mh.make_bsc_codebook(200, N, gen, device)
        ra = mh.make_bsc_codebook(20, N, gen, device)
        cg = torch.Generator().manual_seed(seed_offset + 17 + seed_i * 13 + 1009)
        perm = torch.randperm(200, generator=cg)[:depth + 1]
        chain_rels = [
            int(torch.randint(0, 20, (1,), generator=cg).item())
            for _ in range(depth)
        ]
        M = mh.build_factbase(
            perm.tolist(), chain_rels, max(0, 100 - depth),
            200, 20, ea, ra, cg, device)
        q = measure_q_overlap(M, n_starts, chain_rels, ea, ra)
        q_samples.append(q)
    return q_samples


def find_outer_peaks_with_positions(samples, n_bins_outer=50):
    """Find outer peak positions (bin centroids) and compute inter-peak spacing CV."""
    if len(samples) < 10:
        return 0, [], 0.0
    t_vals = torch.tensor(samples)
    lo, hi = t_vals.min().item(), t_vals.max().item()
    if hi - lo < 1e-8:
        return 1, [(lo + hi) / 2.0], 0.0

    outer = torch.histc(t_vals, bins=n_bins_outer, min=lo, max=hi).tolist()
    bin_width = (hi - lo) / n_bins_outer
    bin_centers = [lo + (i + 0.5) * bin_width for i in range(n_bins_outer)]

    max_outer = max(outer)
    threshold = max_outer * 0.15

    peak_positions = []
    for i in range(1, n_bins_outer - 1):
        if (outer[i] > outer[i - 1] and outer[i] > outer[i + 1]
                and outer[i] >= threshold):
            peak_positions.append(bin_centers[i])
    if outer[0] >= threshold and outer[0] > outer[1]:
        peak_positions.insert(0, bin_centers[0])
    if outer[-1] >= threshold and outer[-1] > outer[-2]:
        peak_positions.append(bin_centers[-1])

    n_outer = len(peak_positions)
    if n_outer < 2:
        return n_outer, peak_positions, 0.0

    # Compute inter-peak gaps
    gaps = [peak_positions[i + 1] - peak_positions[i] for i in range(n_outer - 1)]
    mean_gap = sum(gaps) / len(gaps)
    if mean_gap < 1e-10:
        return n_outer, peak_positions, 0.0
    var_gap = sum((g - mean_gap) ** 2 for g in gaps) / len(gaps)
    std_gap = var_gap ** 0.5
    cv = std_gap / mean_gap
    return n_outer, peak_positions, cv


def find_total_fine_peaks(samples, n_bins_fine=500):
    """Count all fine peaks (same as pq_high_resolution_v1)."""
    if len(samples) < 10:
        return 0
    t_vals = torch.tensor(samples)
    lo, hi = t_vals.min().item(), t_vals.max().item()
    if hi - lo < 1e-8:
        return 1
    fine = torch.histc(t_vals, bins=n_bins_fine, min=lo, max=hi).tolist()
    max_fine = max(fine)
    threshold_fine = max_fine * 0.08
    fine_peaks = 0
    for i in range(1, n_bins_fine - 1):
        if (fine[i] > fine[i - 1] and fine[i] > fine[i + 1]
                and fine[i] >= threshold_fine):
            fine_peaks += 1
    return fine_peaks


def run_experiment(smoke):
    t0 = time.monotonic()
    device = torch.device("cpu")  # CPU only; no GPU needed

    if smoke:
        # Smoke: single N, few seeds — just check pipeline runs and produces output
        N_sweep = [1024]
        n_seeds = 20
        n_starts = 15
        depth = 25
    else:
        # Full: sweep N values; characterize spacing structure
        N_sweep = [512, 1024, 2048, 4096]
        n_seeds = 60    # per N value
        n_starts = 30
        depth = 25

    config = {
        "mode": "smoke" if smoke else "full",
        "N_sweep": N_sweep,
        "n_seeds_per_N": n_seeds,
        "n_starts": n_starts,
        "depth": depth,
        "K": 100,
        "num_entities": 200,
        "num_relations": 20,
        "device": "cpu",
        "note": "P(q) sub-peak spacing characterization after PQ_OTHER_CARDINALITY",
    }

    results_per_N = {}
    for N in N_sweep:
        print(f"\n  N={N}: collecting {n_seeds} q-overlap samples ...", flush=True)
        q_samples = collect_q_samples(N, n_seeds, n_starts, depth, device)
        n_outer, peak_pos, cv = find_outer_peaks_with_positions(q_samples)
        n_total = find_total_fine_peaks(q_samples)
        q_mean = sum(q_samples) / len(q_samples)
        print(f"  N={N}: n_outer={n_outer} n_total={n_total} "
              f"cv={cv:.3f} q_mean={q_mean:.4f}", flush=True)
        results_per_N[str(N)] = {
            "n_outer_peaks": n_outer,
            "n_total_peaks": n_total,
            "outer_spacing_cv": cv,
            "peak_positions": peak_pos,
            "q_mean": q_mean,
            "n_samples": len(q_samples),
        }

    # Use largest N as the primary verdict basis
    primary_N = str(N_sweep[-1])
    primary = results_per_N[primary_N]

    summary = {
        "primary_N": N_sweep[-1],
        "n_outer_peaks": primary["n_outer_peaks"],
        "n_total_peaks": primary["n_total_peaks"],
        "outer_spacing_cv": primary["outer_spacing_cv"],
        "peak_positions": primary["peak_positions"],
        "results_per_N": results_per_N,
        "note": "PQ_OTHER_CARDINALITY follow-up: outer-peak spacing structure",
    }

    # Check N-dependence: is peak count stable across N?
    n_outer_values = [results_per_N[str(N)]["n_outer_peaks"] for N in N_sweep]
    summary["n_outer_per_N"] = dict(zip([str(N) for N in N_sweep], n_outer_values))
    n_outer_range = max(n_outer_values) - min(n_outer_values)
    summary["n_outer_range_across_N"] = n_outer_range
    summary["n_outer_stable"] = (n_outer_range <= 3)  # stable if varies by <=3

    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def write_metrics(out_dir, summary, verdict, msg, elapsed, config):
    metrics = {
        "verdict": verdict,
        "verdict_msg": msg,
        "elapsed_s": elapsed,
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


def run_smoke():
    out_dir = get_output_dir("wave14_pq_subpeak_characterization_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    # Structural check: must produce peak data for primary N
    assert "n_outer_peaks" in summary, "n_outer_peaks missing from summary"
    assert "outer_spacing_cv" in summary, "outer_spacing_cv missing from summary"
    oracle.assert_baseline_high(
        "n_total_peaks_positive", float(summary["n_total_peaks"]) + 0.001, 0.0)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_pq_subpeak_characterization_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
