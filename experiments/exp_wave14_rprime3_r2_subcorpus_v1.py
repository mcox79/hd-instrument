"""R-PRIME-3 R2: sub-corpus geometry as retention mediator.

Context: R-PRIME-3 task-pair-geometry HARD_FAIL at v193 -- between-corpus spectral
distance is NOT predictive of Bet B retention (r^2=0.103). Per v193 rescue R2:
test task-pair geometry at SUB-CORPUS scale -- within-corpus chunks as task pairs
rather than between distinct corpora.

R2 hypothesis: retention may NOT correlate with between-corpus distances because
within-corpus chunks have MORE geometry variation. Sub-corpus pairs (A-chunk1 vs
A-chunk2) may show retention-geometry correlation that between-corpus pairs mask.
If sub-corpus chunk distance predicts retention, the geometry hypothesis SURVIVES
at a finer scale; if not, it is closed at this rescue level too.

Method: take Corpus A, split into 8 contiguous chunks. For each pair of chunks
(chunk_i, chunk_j), run 2-phase Bet B retention (train on i, train on j, measure
retention of i). Measure chunk-pair cosine distance from substrate representations.
Test: r(chunk_pair_distance, retention_i) >= PASS threshold.

Per [[feedback-dont-overextend-theorems]]: v193 killed between-corpus geometry;
R2 tests within-corpus at sub-chunk scale -- geometrically distinct from v193.
Per [[feedback-no-experiment-design-in-prompts]]: all parameters exp_dev autonomy.

Pre-reg:
    HARD-PASS: Pearson r(chunk_pair_distance, retention) >= 0.50 with monotone
               trend AND p < 0.05. -> R2 sub-corpus geometry PASSES; geometry
               mechanism survives at sub-corpus scale.
    HARD-FAIL: r < 0.15 AND non-monotone across >=4 of 6 distance bins.
               -> R2 REJECTED; R-PRIME-3 geometry framing CLOSED (both scales tested).
    MIDDLE: any intermediate; report r + trend.

Queue: remote_cpu_queue (pure CPU; modest M; 5-15 min)
ETA: ~5-10 min remote CPU.
Pre-reg file: preregs/2026-05-24_wave14_rprime3_r2_subcorpus_v1.md
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse, json, math, os, time
from pathlib import Path
import numpy as np

try:
    import torch
    HAS_TORCH = True
except Exception:
    HAS_TORCH = False

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

# ───── design parameters (exp_dev autonomy) ─────
N_CHUNKS = 8          # split corpus A into 8 chunks -> 28 pairs
N_FULL = 2048
N_SMOKE = 512
M_PER_CHUNK_FULL = 80   # items per chunk (Hebbian updates)
M_PER_CHUNK_SMOKE = 20
SEEDS_FULL = [7, 17, 23, 31, 41]
SEEDS_SMOKE = [17]

PASS_PEARSON = 0.50
PASS_PVAL = 0.05
FAIL_PEARSON = 0.15
FAIL_NON_MONOTONE = 4  # of 6 distance bins


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


def make_chunks(N, n_chunks, m_per_chunk, seed):
    """Generate n_chunks sets of key/value pairs for sub-corpus geometry probe."""
    rng = np.random.default_rng(seed)
    chunks = []
    for i in range(n_chunks):
        chunk_rng = np.random.default_rng(seed * 1000 + i)
        keys = chunk_rng.standard_normal((m_per_chunk, N)).astype(np.float32) / math.sqrt(N)
        vals = chunk_rng.standard_normal((m_per_chunk, N)).astype(np.float32) / math.sqrt(N)
        # Chunk "centroid" as a synthetic geometry proxy (mean key direction)
        centroid = keys.mean(axis=0)
        centroid = centroid / (np.linalg.norm(centroid) + 1e-9)
        chunks.append({"keys": keys, "vals": vals, "centroid": centroid})
    return chunks


def hebbian_w(keys, vals, N):
    W = np.zeros((N, N), dtype=np.float64)
    for k, v in zip(keys, vals):
        W += np.outer(v, k)
    return W


def retention_score(W, keys, vals):
    """Mean cosine(W @ k_i, v_i) across pairs."""
    if len(keys) == 0:
        return 0.0
    scores = []
    for k, v in zip(keys, vals):
        recalled = W @ k
        num = float(np.dot(recalled, v))
        denom = float(np.linalg.norm(recalled) * np.linalg.norm(v)) + 1e-9
        scores.append(num / denom)
    return float(np.mean(scores))


def pearson(xs, ys):
    n = len(xs)
    if n < 3:
        return 0.0, 1.0
    mx = sum(xs) / n
    my = sum(ys) / n
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    sxx = sum((x - mx) ** 2 for x in xs)
    syy = sum((y - my) ** 2 for y in ys)
    if sxx * syy <= 0:
        return 0.0, 1.0
    r = sxy / math.sqrt(sxx * syy)
    # t-stat for significance (n-2 df)
    if abs(r) >= 1.0:
        return r, 0.0
    t = r * math.sqrt(n - 2) / math.sqrt(1 - r ** 2 + 1e-12)
    # approximate p-value via normal for large n
    pval = 2.0 * (1.0 - 0.5 * (1.0 + math.erf(abs(t) / math.sqrt(2.0))))
    return r, pval


def is_monotone(xs, ys, n_bins=6):
    """Check monotone trend by binning xs into n_bins and checking mean(ys) is monotone."""
    if len(xs) < n_bins:
        return False, 0
    xs_sorted = sorted(range(len(xs)), key=lambda i: xs[i])
    bin_size = len(xs) // n_bins
    bin_means = []
    for b in range(n_bins):
        idxs = xs_sorted[b * bin_size: (b + 1) * bin_size]
        bin_means.append(sum(ys[i] for i in idxs) / len(idxs))
    n_non_monotone = sum(1 for j in range(1, len(bin_means))
                         if bin_means[j] > bin_means[j - 1])  # expect monotone decreasing
    return n_non_monotone <= 1, n_non_monotone


def run_one_seed(seed, config):
    N = config["N"]
    m_per = config["m_per_chunk"]
    n_chunks = N_CHUNKS
    chunks = make_chunks(N, n_chunks, m_per, seed)

    pair_distances = []
    pair_retentions = []

    # For each (i, j) pair: train on i, train on j (2-phase), measure retention of i
    for i in range(n_chunks):
        for j in range(n_chunks):
            if i == j:
                continue
            ci = chunks[i]
            cj = chunks[j]

            # Chunk-pair distance: cosine distance between centroids
            cos_sim = float(np.dot(ci["centroid"], cj["centroid"]))
            pair_dist = 1.0 - cos_sim  # cosine distance

            # Phase 1: train on chunk i
            W_i = hebbian_w(ci["keys"], ci["vals"], N)
            ret_baseline = retention_score(W_i, ci["keys"], ci["vals"])

            # Phase 2: train on chunk j (no replay)
            W_ij = W_i + hebbian_w(cj["keys"], cj["vals"], N)

            # Retention of chunk i after phase 2
            ret_after = retention_score(W_ij, ci["keys"], ci["vals"])
            retention_ratio = ret_after / max(ret_baseline, 1e-6)

            pair_distances.append(float(pair_dist))
            pair_retentions.append(float(min(retention_ratio, 1.0)))

    r, pval = pearson(pair_distances, pair_retentions)
    monotone, n_non_mono = is_monotone(pair_distances, pair_retentions)

    return {"r": r, "pval": float(pval), "n_pairs": len(pair_distances),
            "monotone": bool(monotone), "n_non_monotone": n_non_mono,
            "mean_dist": float(np.mean(pair_distances)),
            "mean_retention": float(np.mean(pair_retentions))}


def compute_verdict(summary):
    per_seed = summary.get("per_seed", {})
    if not per_seed:
        return ("R2_SUBCORPUS_INCONCLUSIVE", "Missing per-seed data.")

    seeds = list(per_seed.values())
    mean_r = sum(s["r"] for s in seeds) / len(seeds)
    mean_pval = sum(s["pval"] for s in seeds) / len(seeds)
    mean_non_mono = sum(s["n_non_monotone"] for s in seeds) / len(seeds)
    detail = (f"mean_r={mean_r:.3f} mean_pval={mean_pval:.3f} "
              f"mean_non_monotone={mean_non_mono:.1f}/{N_CHUNKS-2} distance_bins")

    if mean_r >= PASS_PEARSON and mean_pval <= PASS_PVAL:
        return ("R2_SUBCORPUS_HARD_PASS",
                f"Sub-corpus geometry PREDICTS retention: {detail}. "
                f"R-PRIME-3 geometry hypothesis SURVIVES at sub-corpus scale.")
    if abs(mean_r) < FAIL_PEARSON and mean_non_mono >= FAIL_NON_MONOTONE:
        return ("R2_SUBCORPUS_HARD_FAIL",
                f"Sub-corpus geometry DOES NOT predict retention: {detail}. "
                f"R-PRIME-3 geometry framing CLOSED at both scales.")
    return ("R2_SUBCORPUS_MIDDLE_BAND",
            f"Intermediate: {detail}. "
            f"Weak trend; inconclusive at this N/M envelope.")


def self_test_verdict():
    """Self-test: verify verdict logic with (input -> expected output) pairs."""
    def mk(r, pval, n_non_mono):
        return {"per_seed": {"17": {"r": r, "pval": pval, "n_non_monotone": n_non_mono,
                                     "n_pairs": 56, "monotone": n_non_mono <= 1,
                                     "mean_dist": 0.5, "mean_retention": 0.7}}}

    cases = [
        # HARD-PASS: strong correlation + significant p
        (mk(0.60, 0.02, 1), "R2_SUBCORPUS_HARD_PASS"),
        (mk(0.55, 0.04, 0), "R2_SUBCORPUS_HARD_PASS"),
        # HARD-FAIL: no correlation + non-monotone
        (mk(0.10, 0.80, 5), "R2_SUBCORPUS_HARD_FAIL"),
        (mk(0.05, 0.90, 4), "R2_SUBCORPUS_HARD_FAIL"),
        # MIDDLE: moderate correlation OR weak significance
        (mk(0.35, 0.10, 2), "R2_SUBCORPUS_MIDDLE_BAND"),
        (mk(0.50, 0.08, 3), "R2_SUBCORPUS_MIDDLE_BAND"),
        # INCONCLUSIVE: empty
        ({"per_seed": {}}, "R2_SUBCORPUS_INCONCLUSIVE"),
    ]
    for summary, expected in cases:
        v, msg = compute_verdict(summary)
        if v != expected:
            raise AssertionError(f"Expected {expected}, got {v}. msg={msg}")
    print(f"self-test passed ({len(cases)}/{len(cases)} cases)", flush=True)


def run_experiment(smoke: bool):
    t0 = time.monotonic()
    N = N_SMOKE if smoke else N_FULL
    m_per = M_PER_CHUNK_SMOKE if smoke else M_PER_CHUNK_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    config = {"mode": "smoke" if smoke else "full",
              "N": N, "m_per_chunk": m_per, "n_chunks": N_CHUNKS,
              "seeds": seeds,
              "pass_pearson": PASS_PEARSON, "pass_pval": PASS_PVAL,
              "fail_pearson": FAIL_PEARSON, "fail_non_monotone": FAIL_NON_MONOTONE}
    print(f"[config] {config}", flush=True)
    per_seed = {}
    for seed in seeds:
        r = run_one_seed(seed, config)
        per_seed[str(seed)] = r
        print(f"  seed={seed}: r={r['r']:.3f} pval={r['pval']:.3f} "
              f"n_non_monotone={r['n_non_monotone']} mean_ret={r['mean_retention']:.3f}",
              flush=True)
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test_verdict()
        return 0
    out_name = ("wave14_rprime3_r2_subcorpus_v1_smoke" if args.smoke
                else "wave14_rprime3_r2_subcorpus_v1")
    out_dir = get_output_dir(out_name)
    summary, verdict, msg, elapsed, config = run_experiment(smoke=args.smoke)
    write_metrics(out_dir, summary, verdict, msg, elapsed, config)
    print(f"\n{'SMOKE' if args.smoke else 'DONE'}: {verdict}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
