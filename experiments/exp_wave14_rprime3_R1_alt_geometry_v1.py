"""R-PRIME-3 R1 rescue — alt-geometry metric.

Context: R-PRIME-3 (task-pair-geometry) HARD-FAIL closed v193 with inner-product
HD-space metric. Per cap_map v193 R1 rescue: re-test with alt-geometry metric
(cluster-structured distance, not inner-product).

Per [[feedback-dont-overextend-theorems]]: HARD-FAIL of inner-product metric
does NOT close all geometry framings. R1 rescue preserves the idea space.

Hypothesis: substrate task-pair retention may correlate with a CLUSTER-structured
distance (Wasserstein-1 between activation distributions, or a Hamming-ball
clustering distance) rather than the bare inner-product. This is a non-trivial
metric change with literature precedent (replica-symmetric overlap distributions).

Method: synthesize K task pairs (synthetic key-value substrates each), measure
retention_A after stage A->B for each pair, and compute (a) bare inner-product
overlap and (b) Wasserstein-1 between coordinate-marginal distributions as the
alt-metric. Correlate retention with each metric.

Pre-reg HARD-PASS: |corr(retention, alt_metric)| >= 0.60 with monotone sign
   across >=6 task pairs AND |corr(retention, inner_product)| <= 0.35
   (alt-metric outperforms inner-product). -> R-PRIME-3 R1 rescue SUCCEEDS;
   task-geometry row promoted under alt-metric framing 🔬 -> 🟡.
Pre-reg HARD-FAIL: |corr(retention, alt_metric)| < 0.30 AND |corr(retention,
   inner_product)| < 0.30 (both flat). -> R1 rescue FAILS; R-PRIME-3 idea
   space narrows further (move to R2 sub-corpus geometry).
Pre-reg MIDDLE: any intermediate; report bands.

CPU-suitable: pure-numpy probe.

Pre-reg: preregs/2026-05-24_wave14_rprime3_R1_alt_geometry_v1.md
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

import numpy as np

REPO = Path(__file__).resolve().parent.parent

# ───── design parameters (exp_dev autonomy) ─────
N_FULL = 1024
N_SMOKE = 128
N_TASK_PAIRS_FULL = 10
N_TASK_PAIRS_SMOKE = 3
M_STORED_FULL = 100
M_STORED_SMOKE = 20
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_ALT_CORR = 0.60
PASS_INNER_CAP = 0.35
FAIL_BOTH_CORR = 0.30


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


def bsc_atoms(num: int, dim: int, rng: np.random.Generator) -> np.ndarray:
    return (rng.integers(0, 2, size=(num, dim)).astype(np.float32) * 2 - 1)


def build_task_substrate(N: int, M: int, rng: np.random.Generator,
                          task_bias: np.ndarray = None):
    """Build a Hebbian substrate W = sum_i k_i v_i^T / M for task with optional
    coordinate bias (task signature).

    The bias is added to each key/value to give the task a coordinate-marginal
    distribution that differs from another task.
    """
    keys = bsc_atoms(M, N, rng)
    vals = bsc_atoms(M, N, rng)
    if task_bias is not None:
        keys = keys + 0.3 * task_bias[None, :]
        vals = vals + 0.3 * task_bias[None, :]
    W = (keys.T @ vals) / M
    return W, keys, vals


def retention_after_overwrite(W_A: np.ndarray, keys_A: np.ndarray, vals_A: np.ndarray,
                                W_B: np.ndarray) -> float:
    """Measure retention of task-A targets after substrate is updated to W_A + W_B
    (Hebbian interference)."""
    W_AB = W_A + W_B
    recalled = keys_A @ W_AB
    num = (recalled * vals_A).sum(axis=1)
    den = np.linalg.norm(recalled, axis=1) * np.linalg.norm(vals_A, axis=1) + 1e-9
    cos = num / den
    return float(cos.mean())


def inner_product_metric(W_A: np.ndarray, W_B: np.ndarray) -> float:
    """Bare Frobenius inner-product."""
    return float((W_A * W_B).sum() / (np.linalg.norm(W_A) * np.linalg.norm(W_B) + 1e-9))


def wasserstein1_metric(W_A: np.ndarray, W_B: np.ndarray) -> float:
    """Cluster-structured Wasserstein-1 between coordinate-marginal distributions
    of W_A and W_B (each W reduced to its row-sum activation distribution).

    For each row, compute mean and stddev; the marginal distribution is the
    histogram of row-sums. We compute the 1-Wasserstein distance between
    sorted row-sums (equivalent for 1D distributions).
    """
    a = np.sort(W_A.sum(axis=1))
    b = np.sort(W_B.sum(axis=1))
    # 1-Wasserstein between two sorted distributions of equal size = mean |a - b|.
    return float(np.abs(a - b).mean())


def pearson_corr(x: list, y: list) -> float:
    if len(x) < 2:
        return 0.0
    xa = np.array(x, dtype=np.float64)
    ya = np.array(y, dtype=np.float64)
    xm = xa - xa.mean()
    ym = ya - ya.mean()
    denom = math.sqrt(float((xm * xm).sum() * (ym * ym).sum()))
    if denom < 1e-12:
        return 0.0
    return float((xm * ym).sum() / denom)


def run_one_seed(seed: int, N: int, M: int, n_pairs: int):
    rng = np.random.default_rng(seed)
    # Build n_pairs DIFFERENT task pairs (A_i, B_i). Each task has a unique bias.
    retentions = []
    inner_products = []
    wasserstein1s = []
    for i in range(n_pairs):
        bias_A = bsc_atoms(1, N, rng)[0]
        bias_B = bsc_atoms(1, N, rng)[0]
        W_A, keys_A, vals_A = build_task_substrate(N, M, rng, bias_A)
        W_B, _, _ = build_task_substrate(N, M, rng, bias_B)
        ret = retention_after_overwrite(W_A, keys_A, vals_A, W_B)
        ip = inner_product_metric(W_A, W_B)
        w1 = wasserstein1_metric(W_A, W_B)
        retentions.append(ret)
        inner_products.append(ip)
        wasserstein1s.append(w1)
    # Correlations: retention vs each metric.
    corr_inner = pearson_corr(retentions, inner_products)
    corr_alt = pearson_corr(retentions, wasserstein1s)
    return {
        "n_pairs": n_pairs,
        "retentions": retentions,
        "inner_products": inner_products,
        "wasserstein1s": wasserstein1s,
        "corr_retention_innerprod": corr_inner,
        "corr_retention_alt_metric": corr_alt,
    }


def compute_verdict(summary):
    per_seed = summary.get("per_seed")
    if not per_seed:
        return ("RPRIME3_R1_INCONCLUSIVE", "Missing per_seed data.")
    corr_inner = sum(s["corr_retention_innerprod"] for s in per_seed.values()) / len(per_seed)
    corr_alt = sum(s["corr_retention_alt_metric"] for s in per_seed.values()) / len(per_seed)
    # alt-metric correlates positively with retention if cluster-distance is the right structure;
    # we use |corr| for the alt-metric to allow either sign.
    abs_alt = abs(corr_alt)
    abs_inner = abs(corr_inner)
    msg_pts = f"corr(retention, inner_prod)={corr_inner:.3f}, corr(retention, alt_metric)={corr_alt:.3f}"
    if abs_alt >= PASS_ALT_CORR and abs_inner <= PASS_INNER_CAP:
        return ("RPRIME3_R1_HARD_PASS_ALT_GEOMETRY_RESCUE",
                f"Alt-metric outperforms inner-product: |corr_alt|={abs_alt:.3f} >= {PASS_ALT_CORR} "
                f"AND |corr_inner|={abs_inner:.3f} <= {PASS_INNER_CAP}. {msg_pts}.")
    if abs_alt < FAIL_BOTH_CORR and abs_inner < FAIL_BOTH_CORR:
        return ("RPRIME3_R1_HARD_FAIL_GEOMETRY_NARROWED",
                f"Both metrics flat: |corr_alt|={abs_alt:.3f} < {FAIL_BOTH_CORR} AND "
                f"|corr_inner|={abs_inner:.3f} < {FAIL_BOTH_CORR}. R1 rescue FAILS, move to R2. {msg_pts}.")
    return ("RPRIME3_R1_MIDDLE_BAND",
            f"Intermediate. |corr_alt|={abs_alt:.3f}, |corr_inner|={abs_inner:.3f}. {msg_pts}.")


def self_test_verdict():
    def mk(c_inner, c_alt):
        return {"per_seed": {"17": {"corr_retention_innerprod": c_inner,
                                    "corr_retention_alt_metric": c_alt}}}
    cases = [
        (mk(0.20, 0.75), "RPRIME3_R1_HARD_PASS_ALT_GEOMETRY_RESCUE"),
        (mk(0.15, 0.20), "RPRIME3_R1_HARD_FAIL_GEOMETRY_NARROWED"),
        (mk(0.50, 0.55), "RPRIME3_R1_MIDDLE_BAND"),
        ({}, "RPRIME3_R1_INCONCLUSIVE"),
    ]
    for s, exp in cases:
        a, msg = compute_verdict(s)
        if a != exp:
            raise AssertionError(f"verdict {a} != {exp}; msg={msg}")
    print(f"verdict self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    N = N_SMOKE if smoke else N_FULL
    M = M_STORED_SMOKE if smoke else M_STORED_FULL
    n_pairs = N_TASK_PAIRS_SMOKE if smoke else N_TASK_PAIRS_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    config = {
        "mode": "smoke" if smoke else "full",
        "N": N,
        "M_stored": M,
        "n_task_pairs": n_pairs,
        "seeds": seeds,
        "pass_alt_corr": PASS_ALT_CORR,
        "pass_inner_cap": PASS_INNER_CAP,
        "fail_both_corr": FAIL_BOTH_CORR,
    }
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in seeds:
        r = run_one_seed(seed, N, M, n_pairs)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: corr_inner={r['corr_retention_innerprod']:.3f} corr_alt={r['corr_retention_alt_metric']:.3f}", flush=True)
    summary = {"per_seed": per_seed}
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
    out_dir = get_output_dir("wave14_rprime3_R1_alt_geometry_v1_smoke")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=True)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nSMOKE OK: {verdict}", flush=True)


def run_main():
    out_dir = get_output_dir("wave14_rprime3_R1_alt_geometry_v1")
    summary, verdict, msg, elapsed, config = run_experiment(smoke=False)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\nDONE: {verdict}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict(); return 0
    if args.smoke:
        run_smoke(); return 0
    run_main(); return 0


if __name__ == "__main__":
    sys.exit(main())
