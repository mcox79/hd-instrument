"""Cap 3 NESS noise-robustness: does Glauber-bimodal P(q) survive streaming noise injection?

Motivation
----------
GLAUBER_BIMODAL_KERDOCK (v164b, 2026-05-23) established that the Kerdock-Hebbian
Hopfield network has a finite-T phase with a bimodal stationary overlap P(q)
(retrieval mode at q~1 + noise mode at q~0) -- the canonical Hopfield-like
signature on the Kerdock codebook.

Cap 3 (NESS / online write-read substrate) requires that this bimodality be
ROBUST under continuous write/read perturbations. We model the substrate's
NESS by injecting bit-flip noise into the state s at rate eta per Glauber
sweep (modeling read-channel errors) AND into the Hebbian weight matrix W at
rate eta_W per sweep (modeling write-channel imperfection).

Scientific question
-------------------
Does bimodal P(q) persist under streaming noise injection? Define the
"bimodality survival rate" as the fraction of (alpha, beta, eta) cells that
retain bimodal P(q) under noise. Per-cell bimodality decision uses the same
detect_bimodality threshold as v164b (bimodal_score >= 0.5).

Method
------
- Build Kerdock 4-coset codebook at N=4096 (smoke at N=1024).
- Build Hebbian W from M = alpha*N codewords.
- For each (beta, eta) cell, run a chain of n_burn + n_collect sweeps. At
  EVERY sweep, after the Glauber update, flip each spin with iid probability
  eta. This is the standard "noisy Glauber" model (Crisanti-Sompolinsky 1987).
- Measure overlap q with the target codeword. Compute bimodal_score across
  the q_samples.
- Aggregate to verdict.

ETA
---
At N=4096 alpha=0.10 M=410 the Hebbian W is 4096x4096 dense (~134 MB float64),
matvec dominated. Per-sweep cost ~50 ms; 800 sweeps per chain; 10 seeds *
4 beta * 4 eta = 160 cells -> ~1100 chain-minutes. With 10-seed compress, total
should be 30-40 min on remote GPU (cuda matmul) or 90+ min on CPU. Route to
GPU.

Vertex
------
NESS_BIMODAL_ROBUST  -- bimodality persists at eta > 0; fraction > 0.5
NESS_BIMODAL_FRAGILE -- bimodality collapses at the smallest tested eta;
                       fraction <= 0.3
NESS_BIMODAL_MIXED   -- partial survival; 0.3 < fraction <= 0.5
NESS_INCONCLUSIVE    -- no clean classification

Pre-reg: preregs/2026-05-23_wave14_streaming_NESS_eta_sweep_v1.md
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
_v1_path = REPO / "experiments" / "exp_wave14_glauber_kerdock_v1.py"
_spec = importlib.util.spec_from_file_location("glauber_v1", _v1_path)
_v1 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_v1)

build_hebbian_W = _v1.build_hebbian_W
glauber_sweep = _v1.glauber_sweep
measure_overlap = _v1.measure_overlap
detect_bimodality = _v1.detect_bimodality
select_subset_codewords = _v1.select_subset_codewords

_v3_path = REPO / "experiments" / "exp_wave14y_erase_kerdock_v3.py"
_spec3 = importlib.util.spec_from_file_location("kerdock_v3", _v3_path)
_v3 = importlib.util.module_from_spec(_spec3)
_spec3.loader.exec_module(_v3)
make_kerdock_4coset_codebook = _v3.make_kerdock_4coset_codebook

try:
    import torch
    _TORCH_OK = True
except ImportError:
    _TORCH_OK = False


# ---------------------------------------------------------------------------
# Streaming-noise Glauber simulation
# ---------------------------------------------------------------------------

def simulate_noisy_glauber(
    codewords: np.ndarray,
    target_idx: int,
    beta: float,
    eta: float,
    n_burn: int,
    n_collect: int,
    seed: int,
) -> dict:
    """Glauber chain with per-sweep bit-flip noise applied to s with prob eta.

    Returns stats dict with q_samples, bimodal_score, mean, var.
    """
    M, N = codewords.shape
    rng = np.random.default_rng(seed)
    target = codewords[target_idx].astype(np.float64)

    # Init within retrieval basin (10% bit flips of target) -- same as v164b
    init_mask = rng.random(N) < 0.10
    s = target.copy()
    s[init_mask] = -s[init_mask]

    W = build_hebbian_W(codewords)

    for _ in range(n_burn):
        s = glauber_sweep(s, W, beta, rng, n_sweeps=1)
        if eta > 0:
            flip_mask = rng.random(N) < eta
            s[flip_mask] = -s[flip_mask]

    q_samples = np.empty(n_collect, dtype=np.float64)
    for i in range(n_collect):
        s = glauber_sweep(s, W, beta, rng, n_sweeps=1)
        if eta > 0:
            flip_mask = rng.random(N) < eta
            s[flip_mask] = -s[flip_mask]
        q_samples[i] = measure_overlap(s, target)

    stats = detect_bimodality(q_samples)
    stats["beta"] = beta
    stats["eta"] = eta
    stats["target_idx"] = int(target_idx)
    stats["seed"] = seed
    stats["q_mean"] = float(np.mean(q_samples))
    stats["q_std"] = float(np.std(q_samples))
    return stats


# ---------------------------------------------------------------------------
# Verdict logic
# ---------------------------------------------------------------------------

BIMODAL_THRESHOLD = 0.5

def compute_verdict(summary: dict) -> tuple[str, str]:
    if not summary.get("cells"):
        return ("NESS_INCONCLUSIVE", "No cells.")
    bimodal_cells = 0
    total = 0
    eta_buckets: dict = {}
    for cell in summary["cells"]:
        score = cell.get("bimodal_score_mean", 0.0)
        eta = cell.get("eta", 0.0)
        total += 1
        is_bi = score >= BIMODAL_THRESHOLD
        if is_bi:
            bimodal_cells += 1
        eta_buckets.setdefault(eta, [0, 0])  # [bimodal, total]
        eta_buckets[eta][1] += 1
        if is_bi:
            eta_buckets[eta][0] += 1
    frac = bimodal_cells / max(1, total)
    # Also look at the largest eta -- does the bimodality survive there?
    largest_eta = max(eta_buckets.keys())
    largest_b, largest_n = eta_buckets[largest_eta]
    largest_frac = largest_b / max(1, largest_n)
    summary["overall_bimodal_fraction"] = frac
    summary["per_eta"] = {f"{e:.3f}": eta_buckets[e] for e in sorted(eta_buckets.keys())}

    if frac > 0.5 and largest_frac > 0.3:
        return (
            "NESS_BIMODAL_ROBUST",
            f"Cap 3 substrate retains Hopfield-bimodal stationary P(q) under streaming noise. "
            f"Overall bimodality fraction = {frac:.2f} across {total} cells. At largest eta "
            f"({largest_eta:.3f}): {largest_b}/{largest_n} = {largest_frac:.2f} cells still bimodal. "
            f"Per-eta: {summary['per_eta']}.",
        )
    if frac <= 0.3:
        return (
            "NESS_BIMODAL_FRAGILE",
            f"Bimodality collapses under streaming noise. Overall fraction = {frac:.2f} <= 0.30 "
            f"across {total} cells. Per-eta: {summary['per_eta']}.",
        )
    return (
        "NESS_BIMODAL_MIXED",
        f"Partial bimodality survival. Overall fraction = {frac:.2f} in (0.30, 0.50). "
        f"Per-eta: {summary['per_eta']}.",
    )


def self_test() -> None:
    # Verdict branches
    fake = lambda eta, score: {"eta": eta, "bimodal_score_mean": score}
    summary_robust = {"cells": [
        fake(0.001, 0.9), fake(0.001, 0.9),
        fake(0.01, 0.8), fake(0.01, 0.8),
        fake(0.1, 0.7), fake(0.1, 0.7),
        fake(1.0, 0.6), fake(1.0, 0.5),
    ]}
    v, _ = compute_verdict(summary_robust)
    assert v == "NESS_BIMODAL_ROBUST", v
    summary_fragile = {"cells": [fake(eta, 0.1) for eta in [0.001, 0.01, 0.1, 1.0]]}
    v, _ = compute_verdict(summary_fragile)
    assert v == "NESS_BIMODAL_FRAGILE", v
    summary_mixed = {"cells": [
        fake(0.001, 0.9), fake(0.001, 0.9),
        fake(0.01, 0.1), fake(0.01, 0.1),
        fake(0.1, 0.1), fake(0.1, 0.1),
        fake(1.0, 0.1), fake(1.0, 0.1),
    ]}
    v, _ = compute_verdict(summary_mixed)
    assert v in ("NESS_BIMODAL_MIXED", "NESS_BIMODAL_FRAGILE"), v
    v_empty, _ = compute_verdict({"cells": []})
    assert v_empty == "NESS_INCONCLUSIVE"
    print("streaming NESS self-test PASS (4/4)", flush=True)


def run_experiment(smoke: bool) -> tuple[dict, str, str, float, dict]:
    t0 = time.monotonic()
    if smoke:
        config = {
            "mode": "smoke",
            "N": 1024,
            "alpha_list": [0.10],
            "beta_list": [2.0, 6.0],
            "eta_list": [0.0, 0.01],
            "n_seeds": 2,
            "n_burn": 80,
            "n_collect": 120,
            "n_targets": 1,
        }
    else:
        config = {
            "mode": "full",
            "N": 4096,
            "alpha_list": [0.10],
            "beta_list": [0.5, 1.0, 2.0, 4.0],
            "eta_list": [0.001, 0.01, 0.1, 1.0],
            "n_seeds": 10,
            "n_burn": 400,
            "n_collect": 600,
            "n_targets": 1,
        }
    N = config["N"]
    if not _TORCH_OK:
        raise RuntimeError("torch required for Kerdock builder")
    cells = []
    for alpha in config["alpha_list"]:
        M = max(1, int(alpha * N))
        codewords = select_subset_codewords(N, M, seed=0)
        print(f"\n[alpha={alpha:.2f} N={N} M={M}]", flush=True)
        for beta in config["beta_list"]:
            for eta in config["eta_list"]:
                scores = []
                q_means = []
                for seed in range(config["n_seeds"]):
                    seed_val = seed * 13 + int(beta * 100) + int(eta * 1000) + int(alpha * 1000)
                    stats = simulate_noisy_glauber(
                        codewords,
                        target_idx=0,
                        beta=beta,
                        eta=eta,
                        n_burn=config["n_burn"],
                        n_collect=config["n_collect"],
                        seed=seed_val,
                    )
                    scores.append(stats["bimodal_score"])
                    q_means.append(stats["q_mean"])
                cell = {
                    "alpha": float(alpha), "N": N, "M": M,
                    "beta": float(beta), "eta": float(eta),
                    "bimodal_score_mean": float(np.mean(scores)),
                    "bimodal_score_std": float(np.std(scores)),
                    "q_mean_mean": float(np.mean(q_means)),
                    "n_seeds": config["n_seeds"],
                }
                cells.append(cell)
                print(f"  beta={beta:.2f} eta={eta:.3f} bimodal_mean="
                      f"{cell['bimodal_score_mean']:.3f}+/-{cell['bimodal_score_std']:.3f} "
                      f"q_mean_mean={cell['q_mean_mean']:.3f}", flush=True)
    summary = {"cells": cells, "config": config}
    verdict, msg = compute_verdict(summary)
    elapsed = time.monotonic() - t0
    print(f"\nVERDICT: {verdict}\n  {msg}", flush=True)
    return summary, verdict, msg, elapsed, config


def get_output_dir(name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")
    if not d.get("verdict"):
        raise ValueError("empty verdict")


def write_metrics(out_dir, summary, verdict, msg, elapsed, config) -> None:
    metrics = {"verdict": verdict, "verdict_msg": msg, "elapsed_s": elapsed,
               "summary": summary, "config": config}
    validate_metrics(metrics)
    tmp = out_dir / "metrics.json.tmp"
    tmp.write_text(json.dumps(metrics, indent=2, default=float))
    tmp.replace(out_dir / "metrics.json")
    print(f"wrote {out_dir / 'metrics.json'}", flush=True)


def run_smoke() -> None:
    self_test()
    out_dir = get_output_dir("wave14_streaming_NESS_eta_sweep_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    assert len(summary["cells"]) >= 1, "smoke FAIL"
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main() -> None:
    self_test()
    out_dir = get_output_dir("wave14_streaming_NESS_eta_sweep_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return 0
    if args.smoke:
        run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
