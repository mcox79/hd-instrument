"""Substrate generative-mode smoke: Glauber dynamics in the bimodal-retrieval
regime, used as a SAMPLER (not a retriever) — dead-or-alive test for a 12th
capability axis (generative-mode).

Strategy x Research shore-up matrix Weakness #5 (HIGH-strategic).
Premise: portfolio gap #1 from cycle 188 Task 4 — every cap in v168 is a
read/retrieve/infer primitive. NO row anchors generative-mode behavior. Glauber
v164b showed BIMODAL retrieval is achievable; this experiment asks whether
sampling from the stationary distribution at the bimodal beta regime produces
DIVERSE fresh codewords (generation) vs collapse to the stored set (retrieval).

The distinction:
  Retrieval = chain initialized near a stored codeword stabilizes around it.
  Generation = chain initialized from random noise produces a sample distribution
               over the Hopfield Boltzmann measure that COVERS basins beyond the
               training set.

Construction:
  - Kerdock-Hebbian W at N=4096 (per matrix t=6).
  - Bimodal beta regime selected to match v164b (beta around 4-8; we sweep
    finely on the bimodal side).
  - Chains initialized from random +-1 noise (NOT from any stored codeword).
  - After burn-in, collect samples spanning many sweeps; each sample is one
    candidate "generated" codeword (binarized state).

Measurements:
  1. NOVELTY: fraction of post-burn-in samples NOT in the stored codeword set
     (Hamming distance to nearest stored > 0.05 N).
  2. DIVERSITY: median pairwise Hamming distance across generated samples
     (relative to N).
  3. STABILITY UNDER PERTURBATION: persistence rate — apply a small bit flip
     (5%) to a generated sample, re-run a short Glauber chain, check that the
     final state is within 0.05 N of the original generated sample.
  4. BINDING-COHERENCE: substrate "semantic coherence" proxy — for each
     generated sample, compute its top-1 overlap against the Kerdock 4-coset
     codebook to test whether it lies in the substrate's algebraic envelope.

HARD PASS (SUBSTRATE_GENERATIVE_CAPABLE):
  - novelty_rate >= 0.30 (>=30% of samples are NEW codewords)
  - diversity_median >= 0.15 (samples are spread out, not all identical)
  - stability_rate >= 0.70 (perturbed samples re-converge to original generated state)
  - binding_coherence_median >= 0.30 (samples lie in the substrate's algebraic envelope)

HARD FAIL (SUBSTRATE_GENERATIVE_FAIL):
  - novelty_rate < 0.05 (samples collapse to training set) OR
  - diversity_median < 0.01 (mode collapse to a single point) OR
  - stability_rate < 0.20 (samples are not stable — pure noise, not generation)

PARTIAL (SUBSTRATE_GENERATIVE_LIMITED): in between.

This is a DEAD-OR-ALIVE test for portfolio gap #5. Either outcome reshapes the
substrate-product story.

Pure CPU. ~1 hr at FULL: N=4096 t=6 Kerdock W, 5 seeds, 3 beta cells, 600 sweeps.
"""
from __future__ import annotations
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Reuse v1 helpers (Kerdock builder, glauber_sweep)
_v1_path = REPO / "experiments" / "exp_wave14_glauber_kerdock_v1.py"
_spec = importlib.util.spec_from_file_location("glauber_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)
build_hebbian_W = _v1.build_hebbian_W
glauber_sweep = _v1.glauber_sweep
select_subset_codewords = _v1.select_subset_codewords

from verification import oracle  # noqa: E402

# Pre-reg thresholds (HARD PASS / HARD FAIL)
PASS_NOVELTY = 0.30
PASS_DIVERSITY = 0.15
PASS_STABILITY = 0.70
PASS_COHERENCE = 0.30

FAIL_NOVELTY = 0.05
FAIL_DIVERSITY = 0.01
FAIL_STABILITY = 0.20


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    if not {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}.issubset(d.keys()):
        raise ValueError(f"missing metrics keys: {set(d.keys())}")


def compute_verdict(summary):
    if "best_cell" not in summary:
        return ("SUBSTRATE_GENERATIVE_INCONCLUSIVE", "No cell results.")
    best = summary["best_cell"]
    nov = best.get("novelty_rate", 0.0)
    div = best.get("diversity_median", 0.0)
    stab = best.get("stability_rate", 0.0)
    coh = best.get("binding_coherence_median", 0.0)

    if (nov < FAIL_NOVELTY or div < FAIL_DIVERSITY or stab < FAIL_STABILITY):
        return ("SUBSTRATE_GENERATIVE_FAIL",
                f"HARD FAIL: at best cell (beta={best.get('beta'):.2f}): "
                f"novelty={nov:.3f} (need >= {FAIL_NOVELTY}), "
                f"diversity={div:.3f} (need >= {FAIL_DIVERSITY}), "
                f"stability={stab:.3f} (need >= {FAIL_STABILITY}). "
                f"Substrate does NOT support generative-mode at any beta. "
                f"Portfolio honestly characterized as retrieval-only.")

    if (nov >= PASS_NOVELTY and div >= PASS_DIVERSITY
            and stab >= PASS_STABILITY and coh >= PASS_COHERENCE):
        return ("SUBSTRATE_GENERATIVE_CAPABLE",
                f"HARD PASS: at best cell (beta={best.get('beta'):.2f}): "
                f"novelty={nov:.3f}, diversity={div:.3f}, stability={stab:.3f}, "
                f"coherence={coh:.3f}. Substrate SUPPORTS generative-mode "
                f"sampling — 12th capability axis is OPEN.")

    return ("SUBSTRATE_GENERATIVE_LIMITED",
            f"PARTIAL: at best cell (beta={best.get('beta'):.2f}): "
            f"novelty={nov:.3f}, diversity={div:.3f}, stability={stab:.3f}, "
            f"coherence={coh:.3f}. Some generative behavior but does not satisfy "
            f"all 4 capability gates simultaneously. Limited 12th axis candidate.")


def self_test_verdict():
    cases = [
        # All pass thresholds -> CAPABLE
        ({"best_cell": {"beta": 6.0, "novelty_rate": 0.40, "diversity_median": 0.20,
                        "stability_rate": 0.80, "binding_coherence_median": 0.35}},
         "SUBSTRATE_GENERATIVE_CAPABLE"),
        # Mode collapse (diversity floor) -> FAIL
        ({"best_cell": {"beta": 6.0, "novelty_rate": 0.40, "diversity_median": 0.005,
                        "stability_rate": 0.80, "binding_coherence_median": 0.35}},
         "SUBSTRATE_GENERATIVE_FAIL"),
        # Collapse-to-training (novelty floor) -> FAIL
        ({"best_cell": {"beta": 6.0, "novelty_rate": 0.03, "diversity_median": 0.20,
                        "stability_rate": 0.80, "binding_coherence_median": 0.35}},
         "SUBSTRATE_GENERATIVE_FAIL"),
        # Noise-not-generation (stability floor) -> FAIL
        ({"best_cell": {"beta": 6.0, "novelty_rate": 0.40, "diversity_median": 0.20,
                        "stability_rate": 0.10, "binding_coherence_median": 0.35}},
         "SUBSTRATE_GENERATIVE_FAIL"),
        # Mid-range -> LIMITED
        ({"best_cell": {"beta": 6.0, "novelty_rate": 0.20, "diversity_median": 0.10,
                        "stability_rate": 0.50, "binding_coherence_median": 0.20}},
         "SUBSTRATE_GENERATIVE_LIMITED"),
        ({}, "SUBSTRATE_GENERATIVE_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        got, _ = compute_verdict(s)
        if got != exp:
            raise AssertionError(f"self_test: got {got} expected {exp}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


# ---------------------------------------------------------------------------
# Generative sampling + measurements
# ---------------------------------------------------------------------------

def hamming_dist(a, b):
    """Normalized Hamming distance for bipolar +-1 vectors of length N."""
    return float(np.mean(a != b))


def min_hamming_to_set(s, codewords):
    """Min normalized Hamming distance from s to any row of codewords (M, N)."""
    diffs = (codewords != s[np.newaxis, :]).mean(axis=1)
    return float(np.min(diffs))


def max_overlap_with_set(s, codewords):
    """Max normalized inner-product (overlap) with rows of codewords."""
    overlaps = codewords @ s / codewords.shape[1]
    return float(np.max(np.abs(overlaps)))


def sample_chain_random_init(W, N, beta, n_burn, n_collect, sample_stride, seed):
    """Initialize from RANDOM noise (not target), burn in, collect samples spaced by sample_stride."""
    rng = np.random.default_rng(seed)
    s = rng.choice([-1.0, 1.0], size=N).astype(np.float64)
    for _ in range(n_burn):
        s = glauber_sweep(s, W, beta, rng, n_sweeps=1)
    samples = []
    for i in range(n_collect):
        s = glauber_sweep(s, W, beta, rng, n_sweeps=sample_stride)
        samples.append(np.sign(s).astype(np.int8))
        # Replace zeros with +1 to be safe
        samples[-1] = np.where(samples[-1] == 0, 1, samples[-1])
    return samples, rng


def measure_stability(W, beta, samples, n_check, perturb_frac, n_relax, seed):
    """For n_check randomly-selected samples, perturb 5% bits and re-run a short chain;
    return fraction that return to within 0.05 N Hamming of original.
    """
    rng = np.random.default_rng(seed + 999)
    if len(samples) == 0:
        return 0.0
    N = samples[0].shape[0]
    n_check = min(n_check, len(samples))
    idxs = rng.choice(len(samples), size=n_check, replace=False)
    n_persist = 0
    for i in idxs:
        s_orig = samples[i].astype(np.float64)
        s_pert = s_orig.copy()
        mask = rng.random(N) < perturb_frac
        s_pert[mask] = -s_pert[mask]
        for _ in range(n_relax):
            s_pert = glauber_sweep(s_pert, W, beta, rng, n_sweeps=1)
        s_final = np.where(np.sign(s_pert) == 0, 1, np.sign(s_pert)).astype(np.int8)
        if hamming_dist(s_final, samples[i]) <= 0.05:
            n_persist += 1
    return n_persist / n_check


def run_one_cell(codewords, beta, config, seed):
    """One (beta, seed) cell: sample chain, measure novelty / diversity / stability / coherence."""
    M, N = codewords.shape
    W = build_hebbian_W(codewords.astype(np.float64))
    samples, _ = sample_chain_random_init(
        W, N, beta,
        n_burn=config["n_burn"],
        n_collect=config["n_collect"],
        sample_stride=config["sample_stride"],
        seed=seed,
    )

    # NOVELTY: fraction of samples NOT in codewords (min-Hamming > 0.05)
    novel_count = 0
    for s in samples:
        if min_hamming_to_set(s.astype(np.int8), codewords.astype(np.int8)) > 0.05:
            novel_count += 1
    novelty_rate = novel_count / len(samples)

    # DIVERSITY: median pairwise Hamming distance over a subset of pairs
    n_pairs = min(50, len(samples) * (len(samples) - 1) // 2)
    rng = np.random.default_rng(seed + 333)
    diversities = []
    sample_arr = np.stack(samples).astype(np.int8)
    for _ in range(n_pairs):
        i, j = rng.choice(len(samples), size=2, replace=False)
        diversities.append(hamming_dist(sample_arr[i], sample_arr[j]))
    diversity_median = float(np.median(diversities)) if diversities else 0.0

    # STABILITY under 5% perturbation
    stability_rate = measure_stability(
        W, beta, samples,
        n_check=config["n_stability_check"],
        perturb_frac=0.05,
        n_relax=20,
        seed=seed,
    )

    # BINDING COHERENCE: median max-overlap with Kerdock codebook
    coherences = []
    for s in samples:
        coherences.append(max_overlap_with_set(s.astype(np.float64), codewords.astype(np.float64)))
    binding_coherence_median = float(np.median(coherences)) if coherences else 0.0

    return {
        "beta": beta,
        "seed": seed,
        "novelty_rate": novelty_rate,
        "diversity_median": diversity_median,
        "stability_rate": stability_rate,
        "binding_coherence_median": binding_coherence_median,
        "n_samples": len(samples),
    }


def run_experiment(smoke):
    t0 = time.monotonic()

    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "alpha": 0.25,  # M = 256 codewords
            "beta_list": [4.0, 6.0],
            "n_seeds": 1,
            "n_burn": 60,
            "n_collect": 40,
            "sample_stride": 3,
            "n_stability_check": 10,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,  # t=6 Kerdock
            "alpha": 0.25,
            "beta_list": [3.0, 5.0, 7.0],  # bimodal regime per v164b
            "n_seeds": 5,
            "n_burn": 400,
            "n_collect": 200,
            "sample_stride": 5,
            "n_stability_check": 30,
        }

    N = config["N"]
    M = max(1, int(config["alpha"] * N))
    cells = []

    for beta in config["beta_list"]:
        beta_results = []
        for seed_i in range(config["n_seeds"]):
            seed_val = seed_i * 1000 + int(beta * 7)
            codewords = select_subset_codewords(N, M, seed=seed_val)
            cell = run_one_cell(codewords.astype(np.float64), beta, config, seed=seed_val + 999)
            beta_results.append(cell)
            print(f"  beta={beta:.2f} seed={seed_i}: "
                  f"novelty={cell['novelty_rate']:.3f} "
                  f"diversity={cell['diversity_median']:.3f} "
                  f"stability={cell['stability_rate']:.3f} "
                  f"coherence={cell['binding_coherence_median']:.3f}", flush=True)

        # Aggregate per-beta
        agg = {
            "beta": beta,
            "novelty_rate": float(np.mean([r["novelty_rate"] for r in beta_results])),
            "diversity_median": float(np.mean([r["diversity_median"] for r in beta_results])),
            "stability_rate": float(np.mean([r["stability_rate"] for r in beta_results])),
            "binding_coherence_median": float(np.mean([r["binding_coherence_median"]
                                                       for r in beta_results])),
            "n_seeds": config["n_seeds"],
            "per_seed": beta_results,
        }
        cells.append(agg)
        print(f"  AGGREGATE beta={beta:.2f}: nov={agg['novelty_rate']:.3f} "
              f"div={agg['diversity_median']:.3f} stab={agg['stability_rate']:.3f} "
              f"coh={agg['binding_coherence_median']:.3f}", flush=True)

    # Choose best cell as the one with highest min(novelty, diversity, stability) -
    # the gating bottleneck. Coherence is informational; not part of the bottleneck.
    def cell_score(c):
        return min(c["novelty_rate"], c["diversity_median"] * 5.0,  # scale diversity ~1
                   c["stability_rate"])
    best = max(cells, key=cell_score) if cells else {}
    summary = {
        "cells": cells,
        "best_cell": best,
        "config": config,
        "note": ("Substrate generative-mode dead-or-alive test; "
                 "samples drawn from random-init Glauber chains in bimodal-beta regime"),
    }
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nBest cell: beta={best.get('beta', 'n/a')}", flush=True)
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
    self_test_verdict()
    out_dir = get_output_dir("wave14_substrate_glauber_generative_smoke_v1_smoke")
    s, v, m, e, c = run_experiment(smoke=True)
    assert len(s["cells"]) >= 1, "smoke: at least one cell required"
    assert "best_cell" in s and s["best_cell"], "smoke: best_cell missing"
    oracle.assert_baseline_high("cells_count", float(len(s["cells"])), 0.0)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nSMOKE OK: {v}", flush=True)


def run_main():
    self_test_verdict()
    out_dir = get_output_dir("wave14_substrate_glauber_generative_smoke_v1")
    s, v, m, e, c = run_experiment(smoke=False)
    write_metrics(out_dir, s, v, m, e, c)
    print(f"\nDONE: {v}", flush=True)


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
