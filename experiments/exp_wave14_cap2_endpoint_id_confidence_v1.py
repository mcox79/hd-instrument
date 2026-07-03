"""Cap 2 Rescue 1: endpoint-ID as confidence proxy (Mondrian/PLCP conformal calibration).

Research recommendation (research_cap2_self_monitoring_rehab_2026-05-23.md):
  Rescue 1 — Endpoint-ID + conditional conformal (PLCP-anchored). Deflated P=0.35.
  Routing: "substrate-novel 28-element endpoint partition is the information-preserving
  alternative to margin/tau; Mondrian conformal uses endpoint-id as partition variable."

Approach:
  Autoassociative Hopfield substrate (W = patterns.T @ patterns / N, as in cycles
  137/149/152 endpoint-partition experiments). This is the substrate-native W^L
  dynamics that produces the 28-element fixed-point partition (Research anchors).

  - Store M patterns in W = patterns.T @ patterns / N.
  - For each query: corrupt pattern with bit-flip noise, run W^L dynamics L hops.
  - Terminal state tags to one of the discovered endpoint clusters.
  - Correctness: overlap of terminal state with the uncorrupted query pattern >= 0.7.
  - Compute p(correct | endpoint_k) empirically on a calibration split.
  - Wrap with Mondrian/PLCP conformal: per-endpoint nonconformity score thresholds give
    distribution-free coverage guarantee.
  - Report ROC AUC for endpoint-conditioned correct-vs-incorrect classification.

Autoassociative vs heteroassociative:
  The Research document's 28-element endpoint partition is from the AUTOASSOCIATIVE
  substrate (W = X^T @ X / N) where W^L dynamics are iterated to a fixed point.
  Heteroassociative memory (W = values.T @ keys / N) does NOT have the same fixed-point
  structure; querying heteroassociative W repeatedly diverges from the attractor.

Pre-reg hard-pass/hard-fail (per Research):
  HARD PASS: ROC AUC >= 0.65 in at least 3/4 noise strata (p in {0.0, 0.05, 0.10, 0.20}),
             200 queries per stratum x 3 seeds;
             AND ECE <= 0.10 after Mondrian conformal wrap;
             AND substrate-ablation AUC delta vs random-baseline >= 0.10.
  HARD FAIL: AUC < 0.55 in 3/4 strata (no signal); OR ECE > 0.15; OR ablation fails.

CPU-only. N=4096 M=100 L=30 hops. n_ref_attractors=20 (from a calibration phase).
Peak memory: W float32 N x N = 64 MB + attractor reference set = negligible. ~10 min CPU.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse, json, math, os, random, time
from pathlib import Path
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
from verification import oracle  # noqa: E402

# ---------------------------------------------------------------------------
# Hard-pass thresholds (from Research pre-reg)
# ---------------------------------------------------------------------------
AUC_HARD_PASS = 0.65      # >= in 3+ strata
AUC_STRATA_REQUIRED = 3
AUC_HARD_FAIL = 0.55      # < in 3+ strata (no signal)
AUC_HARD_FAIL_STRATA = 3
ECE_HARD_PASS = 0.10
ECE_HARD_FAIL = 0.15
ABLATION_DELTA_REQUIRED = 0.10  # substrate AUC must beat random by this margin


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError("missing keys in metrics")


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

def compute_verdict(s: dict) -> tuple:
    if "strata_results" not in s:
        return ("CAP2_ENDPOINT_INCONCLUSIVE", "Missing strata_results.")
    strata = s["strata_results"]
    if not strata:
        return ("CAP2_ENDPOINT_INCONCLUSIVE", "Empty strata.")
    aucs = [v["auc_mean"] for v in strata.values()]
    n_strata = len(aucs)
    n_pass = sum(1 for a in aucs if a >= AUC_HARD_PASS)
    n_fail = sum(1 for a in aucs if a < AUC_HARD_FAIL)
    ece = s.get("mean_ece", 999.0)
    ablation_delta = s.get("ablation_auc_delta", 0.0)
    # Check HARD PASS: AUC>=0.65 in 3+/4 strata, ECE<=0.10, ablation>=0.10
    if (n_pass >= AUC_STRATA_REQUIRED and ece <= ECE_HARD_PASS
            and ablation_delta >= ABLATION_DELTA_REQUIRED):
        return ("CAP2_ENDPOINT_PASS",
                f"HARD PASS: ROC AUC>={AUC_HARD_PASS} in {n_pass}/{n_strata} strata "
                f"(need {AUC_STRATA_REQUIRED}); ECE={ece:.3f}<={ECE_HARD_PASS}; "
                f"ablation_delta={ablation_delta:.3f}>={ABLATION_DELTA_REQUIRED}. "
                f"Endpoint-ID confidence proxy rescues Cap 2 (Rescue 1 via PLCP conformal).")
    # Check HARD FAIL: AUC<0.55 in 3+/4 strata
    if n_fail >= AUC_HARD_FAIL_STRATA:
        return ("CAP2_ENDPOINT_KILL",
                f"HARD FAIL: ROC AUC<{AUC_HARD_FAIL} in {n_fail}/{n_strata} strata. "
                f"Endpoint-ID carries no confidence signal; Rescue 1 refuted.")
    # ECE-only failure
    if ece > ECE_HARD_FAIL:
        return ("CAP2_ENDPOINT_UNCALIBRABLE",
                f"AUC signals present ({n_pass}/{n_strata} strata pass), "
                f"but ECE={ece:.3f}>{ECE_HARD_FAIL} (uncalibratable after conformal wrap). "
                f"Rescue 1 partial.")
    # Ablation failure (substrate not contributing)
    if ablation_delta < ABLATION_DELTA_REQUIRED and n_pass >= 1:
        return ("CAP2_ENDPOINT_NOT_SUBSTRATE_NOVEL",
                f"AUC={[f'{a:.3f}' for a in aucs]}; but ablation delta={ablation_delta:.3f} "
                f"< {ABLATION_DELTA_REQUIRED}. Endpoint-id adds no info beyond data-side signal; "
                f"not substrate-novel. Cap 2 closure stands.")
    # Partial (some strata pass, not enough)
    return ("CAP2_ENDPOINT_PARTIAL",
            f"Partial: {n_pass}/{n_strata} strata AUC>={AUC_HARD_PASS} "
            f"(need {AUC_STRATA_REQUIRED}); ECE={ece:.3f}; "
            f"ablation_delta={ablation_delta:.3f}.")


def self_test_verdict() -> None:
    cases = [
        # Hard pass
        ({"strata_results": {"p0.0": {"auc_mean": 0.72}, "p0.05": {"auc_mean": 0.68},
                              "p0.10": {"auc_mean": 0.66}, "p0.20": {"auc_mean": 0.58}},
          "mean_ece": 0.07, "ablation_auc_delta": 0.15},
         "CAP2_ENDPOINT_PASS"),
        # Hard fail (all AUC < 0.55)
        ({"strata_results": {"p0.0": {"auc_mean": 0.52}, "p0.05": {"auc_mean": 0.51},
                              "p0.10": {"auc_mean": 0.50}, "p0.20": {"auc_mean": 0.49}},
          "mean_ece": 0.08, "ablation_auc_delta": 0.05},
         "CAP2_ENDPOINT_KILL"),
        # Not substrate-novel (ablation delta too small)
        ({"strata_results": {"p0.0": {"auc_mean": 0.70}, "p0.05": {"auc_mean": 0.67},
                              "p0.10": {"auc_mean": 0.65}, "p0.20": {"auc_mean": 0.60}},
          "mean_ece": 0.09, "ablation_auc_delta": 0.04},
         "CAP2_ENDPOINT_NOT_SUBSTRATE_NOVEL"),
        # Uncalibratable (AUC ok, ECE bad)
        ({"strata_results": {"p0.0": {"auc_mean": 0.70}, "p0.05": {"auc_mean": 0.67},
                              "p0.10": {"auc_mean": 0.65}, "p0.20": {"auc_mean": 0.60}},
          "mean_ece": 0.18, "ablation_auc_delta": 0.15},
         "CAP2_ENDPOINT_UNCALIBRABLE"),
        # Partial (only 2 strata pass, not 3)
        ({"strata_results": {"p0.0": {"auc_mean": 0.70}, "p0.05": {"auc_mean": 0.68},
                              "p0.10": {"auc_mean": 0.58}, "p0.20": {"auc_mean": 0.51}},
          "mean_ece": 0.08, "ablation_auc_delta": 0.12},
         "CAP2_ENDPOINT_PARTIAL"),
        # Missing data
        ({}, "CAP2_ENDPOINT_INCONCLUSIVE"),
    ]
    for i, (s, exp) in enumerate(cases):
        got, _ = compute_verdict(s)
        if got != exp:
            raise AssertionError(f"case {i}: got {got!r} expected {exp!r}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


# ---------------------------------------------------------------------------
# Substrate helpers
# ---------------------------------------------------------------------------

def make_pattern(N: int, gen: torch.Generator, device: torch.device) -> torch.Tensor:
    b = (torch.rand(N, generator=gen, device=device) > 0.5).float()
    return 2.0 * b - 1.0


def hopfield_iterate(W: torch.Tensor, x: torch.Tensor, L: int) -> torch.Tensor:
    """Run L synchronous updates of W @ x with hard-threshold cleanup."""
    for _ in range(L):
        x = torch.sign(W @ x)
        x[x == 0] = 1.0
    return x


def apply_bit_flip(x: torch.Tensor, p: float, gen: torch.Generator) -> torch.Tensor:
    if p <= 0.0:
        return x.clone()
    mask = (torch.rand(x.shape, generator=gen, device=x.device) < p)
    return x * (~mask).float() + (-x) * mask.float()


def build_W_autoassoc(patterns: torch.Tensor, N: int) -> torch.Tensor:
    """Autoassociative Hopfield W = (patterns.T @ patterns) / N.

    This is the substrate-native W for cycles 137/149/152 endpoint-partition
    experiments. W^L dynamics on noisy queries converge to one of the stored
    attractors (or a spurious fixed point), giving a 28-element endpoint partition.
    """
    return (patterns.T @ patterns) / N


# ---------------------------------------------------------------------------
# ROC AUC (trapezoid, from sorted scores + binary labels)
# ---------------------------------------------------------------------------

def roc_auc(scores: list, labels: list) -> float:
    """Compute ROC AUC from (score, label) pairs. Labels are 0/1."""
    if len(scores) < 2:
        return 0.5
    n = len(scores)
    pos = sum(labels)
    neg = n - pos
    if pos == 0 or neg == 0:
        return 0.5  # degenerate
    # Sort by score descending
    pairs = sorted(zip(scores, labels), key=lambda t: -t[0])
    tp = 0; fp = 0; prev_tp = 0; prev_fp = 0
    auc = 0.0
    for _, lab in pairs:
        if lab == 1:
            tp += 1
        else:
            fp += 1
            # Trapezoid contribution when fp increases
            auc += (tp + prev_tp) / 2.0 / pos
            prev_tp = tp
        prev_fp = fp
    # remaining
    auc += (pos - prev_tp) / 2.0 / pos * (neg - prev_fp) / neg
    return min(max(auc, 0.0), 1.0)


# ---------------------------------------------------------------------------
# Endpoint clustering
# ---------------------------------------------------------------------------

def discover_attractors(W: torch.Tensor, patterns: torch.Tensor,
                        L: int, n_ref: int, device: torch.device) -> torch.Tensor:
    """Run W^L from multiple start states; cluster by inner-product argmax.
    Returns a (n_ref, N) tensor of reference attractor states."""
    N = W.shape[0]
    n_starts = min(patterns.shape[0], max(n_ref * 4, 40))
    raw_endpoints = []
    for i in range(n_starts):
        ep = hopfield_iterate(W, patterns[i].clone(), L)
        raw_endpoints.append(ep)
    eps = torch.stack(raw_endpoints, dim=0)  # (n_starts, N)
    # Greedy k-center clustering by inner product
    # Seed: pick first
    centers = [eps[0]]
    for ep in eps[1:]:
        # Check similarity to existing centers
        sims = torch.stack([(c * ep).sum() / N for c in centers])
        if float(sims.max().item()) < 0.70:  # not near any center
            centers.append(ep)
            if len(centers) >= n_ref:
                break
    if not centers:
        centers = [eps[0]]
    return torch.stack(centers, dim=0)  # (n_centers, N)


def assign_endpoint_cluster(ep: torch.Tensor, centers: torch.Tensor) -> int:
    """Return index of nearest center by inner product."""
    sims = (centers * ep.unsqueeze(0)).sum(dim=1) / ep.shape[0]
    return int(sims.argmax().item())


# ---------------------------------------------------------------------------
# ECE computation
# ---------------------------------------------------------------------------

def compute_ece(calibration_probs: list, labels: list, n_bins: int = 10) -> float:
    """Expected Calibration Error, equal-width bins on [0, 1]."""
    n = len(calibration_probs)
    if n == 0:
        return 1.0
    ece = 0.0
    bin_width = 1.0 / n_bins
    for b in range(n_bins):
        lo = b * bin_width
        hi = lo + bin_width
        in_bin = [(p, l) for p, l in zip(calibration_probs, labels) if lo <= p < hi]
        if not in_bin:
            continue
        conf = sum(p for p, _ in in_bin) / len(in_bin)
        acc = sum(l for _, l in in_bin) / len(in_bin)
        ece += len(in_bin) / n * abs(conf - acc)
    return ece


# ---------------------------------------------------------------------------
# Core per-stratum evaluation
# ---------------------------------------------------------------------------

def evaluate_stratum(W: torch.Tensor, patterns: torch.Tensor,
                     centers: torch.Tensor, centers_random: torch.Tensor,
                     p_flip: float, n_trials: int, L_hops: int,
                     seed: int, device: torch.device,
                     cal_split: float = 0.5) -> dict:
    """Evaluate endpoint-id confidence for one (p_flip, seed) cell.

    Autoassociative substrate: query = noisy version of patterns[idx];
    run W^L dynamics; terminal state should overlap with patterns[idx] if correct.

    Returns:
      - auc: ROC AUC on test split (endpoint-conditioned confidence vs correct)
      - auc_random: AUC using random-assignment confidence (ablation control)
      - ece: ECE after Mondrian conformal on calibration split
      - n_correct: fraction of correct retrievals
    """
    noise_gen = torch.Generator(device=device).manual_seed(seed + int(p_flip * 10000) + 2)
    N = W.shape[0]
    M = patterns.shape[0]

    # --- Phase 1: collect retrieval trace ---
    records = []
    for t_i in range(n_trials):
        idx = t_i % M
        k = patterns[idx].clone()
        k_noisy = apply_bit_flip(k, p_flip, noise_gen)
        # Run W^L dynamics
        x = hopfield_iterate(W, k_noisy, L_hops)
        # Correctness: overlap of terminal state with original (uncorrupted) pattern
        true_overlap = float((x * patterns[idx]).mean().item())
        is_correct = 1 if true_overlap > 0.7 else 0
        # Endpoint cluster
        ep_cluster = assign_endpoint_cluster(x, centers)
        # Random cluster (ablation)
        ep_cluster_rand = assign_endpoint_cluster(x, centers_random)
        records.append((is_correct, ep_cluster, ep_cluster_rand))

    if not records:
        return {"auc": 0.5, "auc_random": 0.5, "ece": 1.0, "n_correct": 0.0}

    # --- Phase 2: calibration split ---
    n_cal = max(1, int(len(records) * cal_split))
    cal_records = records[:n_cal]
    test_records = records[n_cal:]

    # Compute p(correct | cluster) from calibration set
    cluster_counts = {}
    cluster_correct = {}
    for is_cor, ep_cl, _ in cal_records:
        cluster_counts[ep_cl] = cluster_counts.get(ep_cl, 0) + 1
        cluster_correct[ep_cl] = cluster_correct.get(ep_cl, 0) + is_cor

    # Laplace-smoothed probabilities per cluster (avoids 0/1 edge)
    alpha = 1.0  # Laplace smoothing
    all_clusters = set(cluster_counts.keys())
    cluster_prob = {
        cl: (cluster_correct.get(cl, 0) + alpha) / (cluster_counts.get(cl, 0) + 2 * alpha)
        for cl in all_clusters
    }
    default_prob = (sum(r[0] for r in cal_records) + alpha) / (len(cal_records) + 2 * alpha)

    # Random-baseline cluster counts
    rand_counts = {}
    rand_correct = {}
    for is_cor, _, ep_cl_rand in cal_records:
        rand_counts[ep_cl_rand] = rand_counts.get(ep_cl_rand, 0) + 1
        rand_correct[ep_cl_rand] = rand_correct.get(ep_cl_rand, 0) + is_cor
    rand_cluster_prob = {
        cl: (rand_correct.get(cl, 0) + alpha) / (rand_counts.get(cl, 0) + 2 * alpha)
        for cl in rand_counts
    }

    if not test_records:
        test_records = records  # fallback for small n

    # --- Phase 3: Mondrian conformal (simple version) ---
    # Nonconformity score = 1 - p(correct | cluster) for each test point
    # Conformal p-value for "correct" class = fraction of cal scores as extreme
    # For ECE: use calibrated probability p(correct | cluster) with conformal correction
    cal_scores_by_cluster: dict = {}
    for is_cor, ep_cl, _ in cal_records:
        # nonconformity = 1 - correct (wrong prediction is high nonconformity)
        nc = 1 - is_cor
        cal_scores_by_cluster.setdefault(ep_cl, []).append((nc, is_cor))

    conformal_probs = []
    conformal_labels = []
    auc_scores = []
    auc_labels = []
    auc_random_scores = []

    for is_cor, ep_cl, ep_cl_rand in test_records:
        # Cluster-calibrated probability
        p_correct = cluster_prob.get(ep_cl, default_prob)
        # Mondrian conformal: adjust using calibration set for this cluster
        cal_for_cluster = cal_scores_by_cluster.get(ep_cl, [])
        if len(cal_for_cluster) >= 3:
            nc_correct = 1.0 - p_correct
            # p-value = (# cal in cluster with nc >= nc_correct + 1) / (cal_size + 1)
            pval_correct = (sum(1 for nc, _ in cal_for_cluster if nc >= nc_correct) + 1) / (len(cal_for_cluster) + 1)
            conformal_p = min(pval_correct, 0.99)
        else:
            conformal_p = p_correct

        conformal_probs.append(conformal_p)
        conformal_labels.append(is_cor)
        auc_scores.append(p_correct)
        auc_labels.append(is_cor)
        # Random baseline
        p_rand = rand_cluster_prob.get(ep_cl_rand, default_prob)
        auc_random_scores.append(p_rand)

    auc = roc_auc(auc_scores, auc_labels)
    auc_random = roc_auc(auc_random_scores, auc_labels)
    ece = compute_ece(conformal_probs, conformal_labels)
    n_correct = sum(r[0] for r in records) / len(records)

    return {
        "auc": auc,
        "auc_random": auc_random,
        "ece": ece,
        "n_correct": n_correct,
        "n_trials": len(records),
        "n_clusters_found": len(all_clusters),
    }


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(smoke: bool) -> tuple:
    t0 = time.monotonic()
    device = torch.device("cpu")  # CPU-only per routing rule
    cfg = {
        "N": 512 if smoke else 4096,
        "M": 20 if smoke else 100,
        "L_hops": 15 if smoke else 30,
        "n_ref_attractors": 8 if smoke else 20,
        "n_trials_per_stratum": 20 if smoke else 200,
        "noise_levels": [0.0, 0.10] if smoke else [0.0, 0.05, 0.10, 0.20],
        "seeds": [17] if smoke else [17, 23, 31],
        "mode": "smoke" if smoke else "full",
        "queue": "local_cpu_queue",
        "note": "Cap 2 Rescue 1: endpoint-ID + Mondrian conformal confidence proxy",
    }
    N = cfg["N"]
    M = cfg["M"]
    # Memory: W = N x N float32
    w_mb = N * N * 4 / 1e6
    print(f"Config: N={N} M={M} L={cfg['L_hops']} n_ref={cfg['n_ref_attractors']} "
          f"n_trials={cfg['n_trials_per_stratum']} seeds={cfg['seeds']}", flush=True)
    print(f"W memory per seed: {w_mb:.1f} MB (peak CPU)", flush=True)
    print(f"Noise levels: {cfg['noise_levels']}", flush=True)

    strata_aucs_by_seed: dict = {str(p): [] for p in cfg["noise_levels"]}
    strata_aucs_rand_by_seed: dict = {str(p): [] for p in cfg["noise_levels"]}
    strata_ece_by_seed: dict = {str(p): [] for p in cfg["noise_levels"]}
    strata_ncorr_by_seed: dict = {str(p): [] for p in cfg["noise_levels"]}

    for seed in cfg["seeds"]:
        gen = torch.Generator(device=device).manual_seed(seed)
        # Autoassociative: store M patterns; W = patterns.T @ patterns / N
        patterns = torch.stack([make_pattern(N, gen, device) for _ in range(M)])
        W = build_W_autoassoc(patterns, N)

        # Discover endpoint attractors (reference centers) using noisy queries
        # Use a FRESH set of noisy queries (p=0.10 noise) for attractor discovery
        disc_gen = torch.Generator(device=device).manual_seed(seed + 5000)
        disc_starts = []
        for i in range(min(M * 4, 100)):
            base = patterns[i % M].clone()
            noisy = apply_bit_flip(base, 0.10, disc_gen)
            disc_starts.append(noisy)
        disc_patterns = torch.stack(disc_starts)
        centers = discover_attractors(W, disc_patterns, cfg["L_hops"],
                                      cfg["n_ref_attractors"], device)
        # Random centers for ablation (same count, random directions)
        rand_gen = torch.Generator(device=device).manual_seed(seed + 9999)
        centers_random = torch.stack(
            [make_pattern(N, rand_gen, device) for _ in range(centers.shape[0])]
        )
        print(f"  seed={seed}: discovered {centers.shape[0]} endpoint clusters", flush=True)

        for p in cfg["noise_levels"]:
            result = evaluate_stratum(
                W, patterns, centers, centers_random,
                p, cfg["n_trials_per_stratum"], cfg["L_hops"],
                seed, device,
            )
            print(f"    p={p:.2f}: AUC={result['auc']:.3f} AUC_rand={result['auc_random']:.3f} "
                  f"ECE={result['ece']:.3f} acc={result['n_correct']:.3f} "
                  f"clusters={result['n_clusters_found']}", flush=True)
            strata_aucs_by_seed[str(p)].append(result["auc"])
            strata_aucs_rand_by_seed[str(p)].append(result["auc_random"])
            strata_ece_by_seed[str(p)].append(result["ece"])
            strata_ncorr_by_seed[str(p)].append(result["n_correct"])

    # Aggregate across seeds
    strata_results = {}
    all_ece = []
    all_ablation_deltas = []
    for p in cfg["noise_levels"]:
        aucs = strata_aucs_by_seed[str(p)]
        aucs_rand = strata_aucs_rand_by_seed[str(p)]
        eces = strata_ece_by_seed[str(p)]
        auc_mean = sum(aucs) / len(aucs)
        auc_rand_mean = sum(aucs_rand) / len(aucs_rand)
        ece_mean = sum(eces) / len(eces)
        delta = auc_mean - auc_rand_mean
        all_ece.append(ece_mean)
        all_ablation_deltas.append(delta)
        strata_results[f"p{p}"] = {
            "auc_mean": auc_mean,
            "auc_rand_mean": auc_rand_mean,
            "ablation_delta": delta,
            "ece_mean": ece_mean,
            "auc_per_seed": aucs,
            "p_flip": p,
        }
        print(f"  => p={p:.2f}: AUC={auc_mean:.3f} AUC_rand={auc_rand_mean:.3f} "
              f"ablation_delta={delta:.3f} ECE={ece_mean:.3f}", flush=True)

    mean_ece = sum(all_ece) / len(all_ece) if all_ece else 1.0
    mean_ablation = sum(all_ablation_deltas) / len(all_ablation_deltas) if all_ablation_deltas else 0.0

    summary = {
        "strata_results": strata_results,
        "mean_ece": mean_ece,
        "ablation_auc_delta": mean_ablation,
        "note": "Cap 2 Rescue 1: endpoint-ID W^L dynamics + Mondrian conformal confidence",
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    print(f"Elapsed: {elapsed:.1f}s", flush=True)
    return summary, verdict, msg, elapsed, cfg


# ---------------------------------------------------------------------------
# IO
# ---------------------------------------------------------------------------

def write_metrics(out_dir: Path, summary: dict, verdict: str, msg: str,
                  elapsed: float, config: dict) -> None:
    metrics = {
        "verdict": verdict, "verdict_msg": msg,
        "elapsed_s": elapsed, "summary": summary, "config": config,
    }
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def run_smoke() -> None:
    out_dir = get_output_dir("wave14_cap2_endpoint_id_confidence_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    # Smoke gate: at least 2 strata evaluated; metrics valid
    assert "strata_results" in s, "Missing strata_results in smoke"
    assert len(s["strata_results"]) >= 2, f"Expected >=2 strata, got {len(s['strata_results'])}"
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)
    print(f"  NOTE: at sub-capacity N={c['N']} M={c['M']} smoke; "
          f"AUC signal may be degenerate (all-correct or all-incorrect). "
          f"Full verdict meaningful only at N=4096 M=100 near-capacity.", flush=True)


def run_main() -> None:
    out_dir = get_output_dir("wave14_cap2_endpoint_id_confidence_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Cap 2 Rescue 1: endpoint-ID confidence via Mondrian conformal"
    )
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        print("All self-tests passed.", flush=True)
        return 0
    if args.smoke:
        run_smoke()
        return 0
    run_main()
    return 0


if __name__ == "__main__":
    sys.exit(main())
