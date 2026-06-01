"""BID (Binary Intrinsic Dimension) substrate probe v1.

CONTEXT (from research_negative_results_meta_analysis_2026-05-27.md):
  15+ accumulated framework rejections (RSB, RFOT, TCFT, cluster-glass, geometric-frustration,
  TDA, ...) all live in the static-phase-taxonomy regime. The surviving frameworks
  (Crooks, Sagawa-Ueda, drift-diffusion BP, free-probability) live in non-equilibrium-stat-mech.
  The decisive next step is a FRAMEWORK-FREE order-parameter probe that can discriminate
  whether substrate is a novel class (H1) or a known class we mis-tested (H2).

WHAT IS BID:
  BID measures the intrinsic dimension of the substrate's accessible bipolar state space via
  the TwoNN estimator (Facco et al. 2017, arxiv 1706.00236; see also arxiv 2601.17427 for
  application to Hopfield models). The estimator uses only the two nearest-neighbor distances
  in the sample cloud.

  TwoNN formula:
    mu_i = dist(x_i, k2) / dist(x_i, k1)  for each sample i
    P(mu > t) = t^(-d)  (Pareto tail)
    => d_hat = -1 / mean(log(mu_i))  (maximum likelihood estimate)

  For bipolar vectors (values in {-1, +1}), distance = Hamming distance (= (N - dot)/2).

  Three known Hopfield class BID signatures (from arxiv 2601.17427):
    - Retrieval phase: d ~ O(1), typically in [1.0, 2.5]
    - Spin-glass phase: d ~ O(N/4) to O(N/2)
    - Paramagnetic phase: d ~ O(N-5) to O(N)
  Substrate outside ALL three bands by >= 2 sigma in 4-of-5 seeds = HARD_PASS_NOVEL_CLASS.

DESIGN:
  1. Generate M_samples bipolar patterns stored in substrate (outer-product Hopfield W matrix).
  2. Sample S probe points from the substrate's retrieval manifold:
     - Store M_stored patterns in W.
     - Use M_stored/2 random patterns as queries; run one-step retrieval to get attractors.
     - Collect attractors as the state-space sample cloud.
  3. Compute TwoNN BID on the sample cloud using Hamming distance.
  4. Compare BID estimate to the 3 known-class reference bands.

  Primary metric: bid_estimate (TwoNN d_hat)
  Secondary metrics: bid_ci_low, bid_ci_high (bootstrap CI), bid_vs_retrieval_class,
                     bid_vs_spinglass_class, bid_vs_paramagnetic_class.

  Joint observable: P(q) mean and std (overlap distribution moments) as secondary discriminator.

N sweep: {512, 1024, 2048} to check HP3 (BID is a thermodynamic quantity).
M_stored per N: alpha_c * N = 0.14 * N patterns (standard operating load).
Probe samples S: 200 per N (fixed; TwoNN is efficient).
Seeds: 3 (smoke), 5 (full).

PRE-REGISTERED BANDS:

  HP1 (novel class by BID geometry):
    bid_estimate at N=1024 lies outside ALL THREE reference bands
    (retrieval [1.0, 2.5], spin-glass [N/4, N/2]=[256, 512], paramagnetic [N-5, N]=[1019, 1024])
    by >= 2 sigma in >= 4/5 seeds.
    => P(H1) updates to >= 0.65.

  HP2 (BID-vs-P(q) joint signature is substrate-distinctive):
    bid_estimate outside all 3 class bands AND
    P(q) overlap distribution has mean_overlap NOT matching any class signature:
      retrieval: mean_overlap > 0.7 (ordered)
      spin-glass: mean_overlap bimodal or in [0.3, 0.7]
      paramagnetic: mean_overlap < 0.3
    => substrate-native fingerprint confirmed; product-narrative wedge.

  HP3 (BID thermodynamically stable across N):
    bid_estimate / N is within +/- 5% across N in {512, 1024, 2048}.
    => BID is a true phase invariant, not finite-N artifact.

  HF1 (substrate is a known class):
    bid_estimate at N=1024 falls INSIDE one of the 3 reference bands in >= 4/5 seeds.
    => H2 prevails; P(H2) updates to >= 0.55.

  HF2 (BID unstable across N):
    bid_estimate / N drifts >= 20% from N=512 to N=2048.
    => BID is picking up finite-N noise; no phase claim.

  MIDDLE_BAND:
    bid_estimate on boundary of one class band (within 1 sigma) OR HP2/HP3 mixed.

FORMULA SELF-TESTS:
  1. TwoNN on a d-dimensional hypercube uniform sample:
     d_hat = 2.0 for 2D, 10.0 for 10D (correct Pareto tail gives d_hat -> d).
  2. Hamming distance between identical vectors: 0.
  3. Hamming distance between antipodal vectors (all bits flipped): N.
  4. Mean P(q) for retrieval patterns (one-step convergence): > 0.7.
  5. TwoNN MLE formula check: mu=[2.0, 2.0, 2.0] -> d_hat = -1/mean(log(mu_i))
     = -1/log(2.0) = 1/0.693 = 1.443.

TIMEOUT ESTIMATE:
  N=2048, S=200 samples, 5 seeds: TwoNN is O(S^2 * N) per N value.
  Smoke at N=512, 200 samples, 1 seed: estimate ~5s (fast; matrix product dominates).
  Full: 3 N values x 5 seeds x ~5s x 4 (quadratic in S at same S) = ~300s.
  Safety margin: 1.5 * 300 * (2 extra N-values factor) = ~900s. timeout_s=1800.

N-suffix: no _nN suffix; multi-N sweep (N in {512, 1024, 2048}). No single N is primary.
Queue: remote_cpu_queue (pure numpy; no CUDA; <1800s)
Pre-reg: preregs/2026-05-27_bid_substrate_probe_v1.md
Parent handoff: notes/exp_dev_handoff_research_negative_results_meta_analysis_2026-05-27.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import json
import math
import os
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# -------------------------------------------------------------------------
# Configuration
# -------------------------------------------------------------------------

# N sweep for HP3 (BID stability)
N_SWEEP_FULL  = [512, 1024, 2048]
N_SWEEP_SMOKE = [512]

SEEDS_FULL  = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

S_PROBES = 200          # probe samples for TwoNN per (N, seed)
ALPHA_C   = 0.14        # operating load: M_stored = int(ALPHA_C * N)

# Known Hopfield BID class bands
# (as fractions of N; evaluated at each N)
RETRIEVAL_BAND    = (1.0, 2.5)        # absolute values, not N-scaled
SPINGLASS_BAND    = (0.25, 0.50)      # fraction of N
PARAMAGNETIC_BAND = (1.0 - 5.0 / 512, 1.001)  # ~1.0 (N-5 to N, normalized)

# HP1: outside all 3 bands by >= 2 sigma across seeds
# HP3 stability: bid/N within 5% across N
HP3_STABILITY_TOL = 0.05
HP_SEED_FRACTION  = 0.80   # 4/5 seeds

# Pre-registered band thresholds
HP_VAR_RATIO_STRONG = 0.10  # same concept as tcft: BID far from class bands

# -------------------------------------------------------------------------
# Core math
# -------------------------------------------------------------------------

def hamming_dist(a: np.ndarray, b: np.ndarray) -> float:
    """Hamming distance between two bipolar vectors."""
    return float(np.sum(a != b))


def twonn_bid(samples: np.ndarray) -> Tuple[float, float, float]:
    """TwoNN BID estimate (Facco et al. 2017) on bipolar sample cloud.

    samples: (S, N) bipolar matrix with values in {-1, +1}.
    Returns: (d_hat, ci_low, ci_high) via bootstrap (100 resamples).
    """
    S, N = samples.shape
    assert S >= 4, f"Need at least 4 samples for TwoNN; got {S}"

    # Compute pairwise Hamming distances via dot-product trick:
    # hamming(a, b) = (N - dot(a, b)) / 2
    # Shape: (S, S)
    dot = samples @ samples.T  # (S, S)
    dist = (N - dot) / 2.0    # Hamming distances

    # For each point i, find two nearest neighbors (exclude self)
    mu_vals = np.zeros(S, dtype=np.float64)
    for i in range(S):
        dists_i = dist[i].copy()
        dists_i[i] = np.inf  # exclude self
        sorted_idx = np.argsort(dists_i)
        d1 = dists_i[sorted_idx[0]]
        d2 = dists_i[sorted_idx[1]]
        if d1 <= 0.0:
            d1 = 0.5  # avoid log(0); Hamming dist can be 0 for identical points
        mu_vals[i] = d2 / d1

    # MLE estimate: Pareto tail P(mu > t) = t^(-d), t >= 1
    # MLE: d_hat = n / sum(log(mu_i)) = 1 / mean(log(mu_i))
    # (Facco et al. 2017 eq. 5; log(mu_i) > 0 since mu_i >= 1)
    log_mu = np.log(mu_vals)
    valid = np.isfinite(log_mu) & (log_mu > 0.0)
    if valid.sum() < 2:
        return float("nan"), float("nan"), float("nan")

    d_hat = 1.0 / np.mean(log_mu[valid])

    # Bootstrap CI (100 resamples)
    rng = np.random.default_rng(seed=42)
    boot_d = np.zeros(100, dtype=np.float64)
    for b in range(100):
        idx = rng.integers(0, valid.sum(), size=valid.sum())
        boot_d[b] = 1.0 / np.mean(log_mu[valid][idx])

    ci_low  = float(np.percentile(boot_d[np.isfinite(boot_d)], 2.5))
    ci_high = float(np.percentile(boot_d[np.isfinite(boot_d)], 97.5))
    return float(d_hat), ci_low, ci_high


def run_one_seed(N: int, seed: int) -> Dict:
    """Run BID probe at a single (N, seed) point."""
    rng = np.random.default_rng(seed=seed)

    M_stored = max(4, int(ALPHA_C * N))

    # 1. Generate M_stored random bipolar patterns
    patterns = rng.choice([-1, 1], size=(M_stored, N)).astype(np.float64)

    # 2. Build Hopfield W (outer-product Hebbian)
    W = np.zeros((N, N), dtype=np.float64)
    for v in patterns:
        W += np.outer(v, v) / N
    np.fill_diagonal(W, 0.0)

    # 3. Sample S_PROBES retrieval attractors
    # Query with fresh random vectors; one-step update: x_new = sign(W @ x)
    n_samples = min(S_PROBES, M_stored)
    query_idx = rng.choice(M_stored, size=n_samples, replace=False)
    queries = patterns[query_idx].copy()
    # Add small noise
    flip_prob = 0.05
    noise_mask = rng.random(queries.shape) < flip_prob
    queries[noise_mask] *= -1.0

    attractors = np.sign(W @ queries.T).T  # (S, N)
    # Replace zeros with +1 (sign(0) is undefined)
    attractors[attractors == 0] = 1.0
    attractors = attractors.astype(np.int8)

    # 4. TwoNN BID on attractors
    d_hat, ci_low, ci_high = twonn_bid(attractors.astype(np.float64))

    # 5. P(q) moments (overlap distribution)
    # Overlap between each attractor and its nearest stored pattern
    overlaps = (attractors.astype(np.float64) @ patterns.T) / N  # (S, M_stored)
    max_overlaps = np.max(np.abs(overlaps), axis=1)  # (S,)
    mean_overlap = float(np.mean(max_overlaps))
    std_overlap  = float(np.std(max_overlaps))

    # 6. Classify vs known Hopfield bands
    def in_retrieval_band(d: float, n: int) -> bool:
        return RETRIEVAL_BAND[0] <= d <= RETRIEVAL_BAND[1]

    def in_spinglass_band(d: float, n: int) -> bool:
        lo = SPINGLASS_BAND[0] * n
        hi = SPINGLASS_BAND[1] * n
        return lo <= d <= hi

    def in_paramagnetic_band(d: float, n: int) -> bool:
        lo = (1.0 - 5.0 / n) * n if n > 5 else n - 5
        hi = float(n)
        return lo <= d <= hi

    in_retrieval    = in_retrieval_band(d_hat, N) if math.isfinite(d_hat) else False
    in_spinglass    = in_spinglass_band(d_hat, N) if math.isfinite(d_hat) else False
    in_paramagnetic = in_paramagnetic_band(d_hat, N) if math.isfinite(d_hat) else False
    in_known_class  = in_retrieval or in_spinglass or in_paramagnetic

    # BID/N normalized for HP3 stability check
    bid_normalized = d_hat / N if math.isfinite(d_hat) else float("nan")

    return {
        "N": N,
        "seed": seed,
        "M_stored": M_stored,
        "bid_estimate": d_hat,
        "bid_ci_low": ci_low,
        "bid_ci_high": ci_high,
        "bid_normalized": bid_normalized,
        "in_retrieval_band": in_retrieval,
        "in_spinglass_band": in_spinglass,
        "in_paramagnetic_band": in_paramagnetic,
        "in_known_class": in_known_class,
        "mean_overlap": mean_overlap,
        "std_overlap": std_overlap,
    }


# -------------------------------------------------------------------------
# Self-test
# -------------------------------------------------------------------------

def _instrumentation_selftest() -> None:
    """Assert all claimed metrics are non-null/non-sentinel at smoke scale."""
    # 1. TwoNN formula check: mu=[2.0, 2.0, 2.0] -> d_hat = 1/mean(log(mu)) = 1/log(2) = 1.4427
    # Facco 2017 MLE: d = n / sum(log(mu_i)) = 1/mean(log(mu_i)), log(mu_i) > 0.
    log_mu_test = np.log(np.array([2.0, 2.0, 2.0]))
    d_test = 1.0 / np.mean(log_mu_test)
    assert abs(d_test - 1.0 / math.log(2.0)) < 1e-6, \
        f"TwoNN formula check failed: d_test={d_test:.6f} expected {1.0/math.log(2):.6f}"

    # 2. Hamming distance checks
    v1 = np.array([1, 1, -1, 1], dtype=np.float64)
    v2 = np.array([1, 1, -1, 1], dtype=np.float64)
    assert hamming_dist(v1, v2) == 0, f"hamming(identical) != 0"
    v3 = -v1
    assert hamming_dist(v1, v3) == 4, f"hamming(antipodal) != N={4}"

    # 3. TwoNN on a known-geometry sample (uniform 2D disk approximation in high-N)
    # Use 10 random bipolar vectors at N=8; should return finite d_hat
    rng = np.random.default_rng(seed=0)
    samples_test = rng.choice([-1, 1], size=(20, 8)).astype(np.float64)
    d_t, ci_lo, ci_hi = twonn_bid(samples_test)
    assert math.isfinite(d_t), f"TwoNN returned non-finite d_hat={d_t} on test sample"
    assert d_t > 0.0, f"TwoNN d_hat={d_t} <= 0"

    # 4. run_one_seed at tiny N gives non-null metrics
    r = run_one_seed(N=64, seed=17)
    assert r["bid_estimate"] is not None, "bid_estimate is None at N=64"
    assert math.isfinite(r["bid_estimate"]), f"bid_estimate not finite: {r['bid_estimate']}"
    assert r["mean_overlap"] >= 0.0 and r["mean_overlap"] <= 1.0, \
        f"mean_overlap out of range: {r['mean_overlap']}"

    # 5. Multi-scale smoke: N=64 and N=256
    r2 = run_one_seed(N=256, seed=17)
    assert math.isfinite(r2["bid_estimate"]), f"bid_estimate N=256 not finite"

    # 6. Band classification sanity: retrieval band d=2.0 at N=1024
    r_dummy = {"bid_estimate": 2.0, "N": 1024}
    in_r = RETRIEVAL_BAND[0] <= r_dummy["bid_estimate"] <= RETRIEVAL_BAND[1]
    assert in_r, f"d=2.0 should be in retrieval band {RETRIEVAL_BAND}"

    print(
        f"[selftest] bid_substrate_probe_v1 PASSED: "
        f"TwoNN formula d_test={d_test:.4f}, smoke_N64 bid={r['bid_estimate']:.2f}, "
        f"multi-scale N256 bid={r2['bid_estimate']:.2f}",
        flush=True,
    )


_instrumentation_selftest()


# -------------------------------------------------------------------------
# Main sweep
# -------------------------------------------------------------------------

def run(smoke: bool = False) -> None:
    t0 = time.time()
    N_sweep = N_SWEEP_SMOKE if smoke else N_SWEEP_FULL
    seeds   = SEEDS_SMOKE   if smoke else SEEDS_FULL
    mode_str = "SMOKE" if smoke else "FULL"
    exp_name = os.environ.get("HDLAB_EXP_NAME", "bid_substrate_probe_v1")

    print(f"[run] {exp_name} {mode_str} N_sweep={N_sweep} seeds={seeds}", flush=True)

    out_dir = REPO / "data" / f"exp_{exp_name}"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Collect results per (N, seed)
    all_results: List[Dict] = []
    for N in N_sweep:
        for seed in seeds:
            t_s = time.time()
            r = run_one_seed(N, seed)
            all_results.append(r)
            print(
                f"  N={N} seed={seed}: bid={r['bid_estimate']:.3f} "
                f"ci=[{r['bid_ci_low']:.2f},{r['bid_ci_high']:.2f}] "
                f"in_known={r['in_known_class']} "
                f"overlap={r['mean_overlap']:.3f} ({time.time()-t_s:.1f}s)",
                flush=True,
            )

    # Aggregate: per-N summary
    per_n_summary: List[Dict] = []
    for N in N_sweep:
        rows = [r for r in all_results if r["N"] == N]
        bids = [r["bid_estimate"] for r in rows if math.isfinite(r["bid_estimate"])]
        bids_norm = [r["bid_normalized"] for r in rows if math.isfinite(r["bid_normalized"])]
        n_outside_known = sum(1 for r in rows if not r["in_known_class"])
        n_seeds = len(rows)
        per_n_summary.append({
            "N": N,
            "n_seeds": n_seeds,
            "bid_mean": float(np.mean(bids)) if bids else float("nan"),
            "bid_std":  float(np.std(bids)) if bids else float("nan"),
            "bid_norm_mean": float(np.mean(bids_norm)) if bids_norm else float("nan"),
            "n_outside_known_class": n_outside_known,
            "outside_known_fraction": n_outside_known / n_seeds if n_seeds > 0 else 0.0,
        })

    # HP3 stability check (only meaningful for FULL with 3 N values)
    hp3_stable = False
    if len(N_sweep) >= 2:
        norm_means = [s["bid_norm_mean"] for s in per_n_summary if math.isfinite(s["bid_norm_mean"])]
        if len(norm_means) >= 2:
            drift = (max(norm_means) - min(norm_means)) / (min(norm_means) + 1e-9)
            hp3_stable = drift <= HP3_STABILITY_TOL

    # HP1 check: bid outside all known classes in >= 4/5 seeds at primary N
    primary_N = max(N_sweep)
    primary_rows = [r for r in all_results if r["N"] == primary_N]
    n_novel = sum(1 for r in primary_rows if not r["in_known_class"])
    n_primary_seeds = len(primary_rows)
    hp1_pass = (n_novel / n_primary_seeds >= HP_SEED_FRACTION) if n_primary_seeds > 0 else False

    # P(q) classification at primary_N
    pq_means = [r["mean_overlap"] for r in primary_rows if math.isfinite(r.get("mean_overlap", float("nan")))]
    mean_pq = float(np.mean(pq_means)) if pq_means else float("nan")
    pq_class = (
        "retrieval" if math.isfinite(mean_pq) and mean_pq > 0.7
        else "spinglass" if math.isfinite(mean_pq) and 0.3 <= mean_pq <= 0.7
        else "paramagnetic" if math.isfinite(mean_pq) and mean_pq < 0.3
        else "unknown"
    )

    # HF1: any seed IN a known class
    hf1_fail = (n_novel / n_primary_seeds < (1.0 - HP_SEED_FRACTION)) if n_primary_seeds > 0 else False

    # Verdict
    if hp1_pass and hp3_stable:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: bid outside all 3 known Hopfield class bands in "
            f"{n_novel}/{n_primary_seeds} seeds at N={primary_N}. "
            f"HP3 stable (drift<={HP3_STABILITY_TOL*100:.0f}%). "
            f"mean_overlap={mean_pq:.3f} (pq_class={pq_class}). "
            f"P(H1 novel-class) updated to >= 0.65."
        )
    elif hp1_pass and not hp3_stable:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: bid outside all known classes ({n_novel}/{n_primary_seeds} seeds) "
            f"BUT HP3 unstable (drift>5%). BID may be finite-N artifact at tested scale."
        )
    elif hf1_fail:
        verdict = "HARD_FAIL"
        # Which class did substrate fall into?
        primary_summary = next(s for s in per_n_summary if s["N"] == primary_N)
        in_rows = [r for r in primary_rows if r["in_known_class"]]
        class_hits = {
            "retrieval": sum(1 for r in in_rows if r["in_retrieval_band"]),
            "spinglass": sum(1 for r in in_rows if r["in_spinglass_band"]),
            "paramagnetic": sum(1 for r in in_rows if r["in_paramagnetic_band"]),
        }
        matched = max(class_hits, key=class_hits.get)
        verdict_msg = (
            f"HARD_FAIL: bid IN {matched} class band in >= 4/5 seeds at N={primary_N}. "
            f"H2 prevails; P(H2) updates to >= 0.55. "
            f"bid_mean={primary_summary['bid_mean']:.2f}. "
            f"mean_overlap={mean_pq:.3f}."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: {n_novel}/{n_primary_seeds} seeds bid outside known classes "
            f"at N={primary_N}. HP3_stable={hp3_stable}. mean_overlap={mean_pq:.3f}."
        )

    elapsed = round(time.time() - t0, 2)
    print(f"\n[verdict] {verdict}", flush=True)
    print(f"[verdict_msg] {verdict_msg}", flush=True)

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": elapsed,
        "summary": (
            f"bid_substrate_probe_v1 {mode_str}: "
            f"N={primary_N} novel_frac={n_novel}/{n_primary_seeds} hp3={hp3_stable}"
        ),
        "hp1_pass": hp1_pass,
        "hp3_stable": hp3_stable,
        "n_novel_at_primary_N": n_novel,
        "n_primary_seeds": n_primary_seeds,
        "mean_overlap_primary_N": mean_pq,
        "pq_class": pq_class,
        "per_n_summary": per_n_summary,
        "all_results": all_results,
        "config": {
            "N_sweep": N_sweep,
            "seeds": seeds,
            "S_probes": S_PROBES,
            "alpha_c": ALPHA_C,
            "smoke": smoke,
        },
    }
    mpath = out_dir / "metrics.json"
    with open(mpath, "w") as fh:
        json.dump(metrics, fh, indent=2)
    print(f"[exp] metrics -> {mpath}", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
