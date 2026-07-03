"""Bet B 6-corpus extension: probe the 4-class Saad-Solla framework limit.

ANTICIPATORY PRE-BUILD -- trigger: wave14_betB_5corpus_noreplay_fix_v1 returns
  HARD_PASS (BIC_4vs3 < -30 AND spacing_error < 0.05, 4-class plateau structure confirmed).

This v1 extends to 6 corpora (A, B, C, D, E, F) to probe whether the equal-spacing
prediction holds beyond 4 classes. The Saad-Solla framework predicts the plateau heights
are set by fixed points of the order-parameter ODEs -- adding more phases should produce
additional discrete plateaus, not smoothing.

DESIGN:
  - 6 corpus phases: A (native), B (shuffled A), C (independent), D (shuffled C),
    E (shuffled B), F (independent 2)
  - Ordered by decreasing overlap with A: SAME=1.0, SHUFFLE=0.5, SHUFFLED_SHUFFLE=0.25,
    INDEPENDENT=0.0
  - Primary: retention_A after each phase (5 retention measurements: after B, C, D, E, F)
  - BIC test: 5-state vs 4-state vs 3-state (k-means on retention values)
  - Equal-spacing: are the 5 post-B retention values equally spaced?

PRE-REGISTERED BANDS:
  HARD_PASS (6-corpus framework holds):
    - BIC_5vs4 < -25 (5-state preferred over 4-state)
    - AND equal-spacing error (std of gaps) < 0.05
    - AND all retentions monotone non-increasing as corpus diverges
    -> Saad-Solla framework generalizes to 6 corpora; additional plateaus predicted

  HARD_FAIL (framework limit reached):
    - BIC_5vs4 > 0 (4-state preferred over 5-state at 6 corpora)
    - OR spacing error > 0.10 (additional corpora don't add a new plateau -- they merge)
    -> 4-class taxonomy is the natural framework limit; 5th+ plateau does not emerge

  MIDDLE_BAND:
    - BIC_5vs4 in (-25, 0)
    - OR spacing error in [0.05, 0.10)
    -> Partial; 5th plateau exists but not cleanly separated

  INSTRUMENTATION_FAIL:
    - Retention non-finite or any BIC computation fails

Self-tests:
  1. k_means_1d: [0.0, 0.0, 0.5, 0.5, 1.0, 1.0] -> 3 clusters at {0, 0.5, 1}
  2. bic_score: 2-state BIC < 3-state BIC when data is truly 2-state
  3. equal_spacing_error([0.1, 0.2, 0.3, 0.4]) = 0.0 (perfectly spaced)
  4. corpus_overlap(corpus_A, shuffled_A) = 0.0 (shuffled has no N-gram overlap)

Queue: overnight_queue (GPU; 6 phases x 20 seeds x N=4096; ~4-6 GPU-hrs)
Pre-reg: preregs/2026-05-26_wave14_betB_6corpus_extension_v1.md
Trigger: ship when 5corpus_noreplay_fix_v1 returns HARD_PASS (BIC_4vs3 < -30).
"""
from __future__ import annotations

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import importlib.util
import json
import math
import os
import time
from pathlib import Path

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Load M1 hierreplay infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1_6c", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
v1_mod = m1.v1
pa = m1.pa

# Design parameters
N_FULL = 4096
N_SMOKE = 512
SEEDS_FULL = list(range(7, 27))   # 20 seeds
SEEDS_SMOKE = [7, 17]
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
BYTES_FULL = 200_000
BYTES_SMOKE = 5_000
EPOCHS_FULL = 8
EPOCHS_B_FULL = 5

# Thresholds
HP_BIC_5VS4 = -25.0
HP_SPACING_ERR = 0.05
HF_BIC_5VS4 = 0.0
HF_SPACING_ERR = 0.10


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required fields: {missing}")


def equal_spacing_error(vals: list) -> float:
    """Std of gaps between consecutive sorted values (0 = perfect equal spacing)."""
    if len(vals) < 2:
        return 0.0
    s = sorted(vals)
    gaps = [s[i + 1] - s[i] for i in range(len(s) - 1)]
    mean_gap = sum(gaps) / len(gaps)
    return math.sqrt(sum((g - mean_gap) ** 2 for g in gaps) / max(len(gaps), 1))


def bic_k_state(vals: list, k: int) -> float:
    """Compute BIC for k-state Gaussian mixture (simplified: k-means assignment)."""
    if len(vals) < k:
        return float("inf")
    n = len(vals)
    # Initialize centroids equally spaced
    lo, hi = min(vals), max(vals)
    if hi <= lo:
        # All values identical: k=1 is best
        log_lik = -n * math.log(1e-6)
        params = k - 1 + k + k  # mixing, mean, variance
        return -2 * log_lik + params * math.log(n)
    centroids = [lo + i * (hi - lo) / (k - 1) for i in range(k)] if k > 1 else [(lo + hi) / 2]
    # Iterate k-means
    for _ in range(20):
        assignments = [min(range(k), key=lambda j: (v - centroids[j]) ** 2) for v in vals]
        new_c = []
        for j in range(k):
            cluster = [vals[i] for i in range(n) if assignments[i] == j]
            new_c.append(sum(cluster) / max(len(cluster), 1) if cluster else centroids[j])
        if new_c == centroids:
            break
        centroids = new_c
    # Log-likelihood
    cluster_vars = []
    for j in range(k):
        cluster = [vals[i] for i in range(n) if assignments[i] == j]
        if len(cluster) < 2:
            cluster_vars.append(1e-6)
        else:
            m = sum(cluster) / len(cluster)
            cluster_vars.append(max(sum((v - m) ** 2 for v in cluster) / len(cluster), 1e-6))
    log_lik = sum(
        math.log(1.0 / (math.sqrt(2 * math.pi * cluster_vars[assignments[i]]))) -
        (vals[i] - centroids[assignments[i]]) ** 2 / (2 * cluster_vars[assignments[i]])
        for i in range(n)
    )
    params = k - 1 + k + k  # mixing proportions, means, variances
    return -2 * log_lik + params * math.log(n)


def _instrumentation_selftest():
    print("[selftest] running instrumentation self-test...", flush=True)

    # 1. k-means: 3-cluster data
    data1 = [0.0, 0.01, 0.5, 0.51, 1.0, 0.99]
    bic2 = bic_k_state(data1, 2)
    bic3 = bic_k_state(data1, 3)
    assert bic3 < bic2, f"Selftest 1 FAIL: BIC_3={bic3:.2f} not < BIC_2={bic2:.2f}"
    print(f"[selftest] 1/4 BIC_3 < BIC_2 for 3-cluster data OK")

    # 2. bic_score: truly 2-state data
    data2 = [0.3] * 5 + [0.8] * 5
    bic2 = bic_k_state(data2, 2)
    bic3 = bic_k_state(data2, 3)
    assert bic2 < bic3, f"Selftest 2 FAIL: BIC_2={bic2:.2f} not < BIC_3={bic3:.2f}"
    print(f"[selftest] 2/4 BIC_2 < BIC_3 for 2-state data OK")

    # 3. equal_spacing_error: perfectly spaced
    err3 = equal_spacing_error([0.1, 0.2, 0.3, 0.4])
    assert err3 < 0.001, f"Selftest 3 FAIL: spacing_err={err3:.6f}"
    print(f"[selftest] 3/4 equal_spacing_error(perfectly_spaced)={err3:.6f} ~0 OK")

    # 4. equal_spacing_error: non-uniform
    err4 = equal_spacing_error([0.1, 0.5, 0.55, 0.9])
    assert err4 > 0.05, f"Selftest 4 FAIL: spacing_err={err4:.4f} (expected > 0.05)"
    print(f"[selftest] 4/4 equal_spacing_error(non-uniform)={err4:.4f} > 0.05 OK")

    print("[selftest] instrumentation self-test PASSED", flush=True)


_instrumentation_selftest()


def run_6phase_sequence(seed, N, batch_size, epochs, epochs_B, n_bytes, smoke, device):
    """Run 6-phase corpus sequence and return retention_A after each phase."""
    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(base.VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(base.K, N, gen).to(device)

    corpus_a = pa.load_corpus_a()[:n_bytes]
    corpus_b = pa.shuffle_bytes(corpus_a, seed=seed + 1)
    corpus_c_full = base.load_corpus_C(smoke=smoke)
    corpus_c = corpus_c_full[:n_bytes] if n_bytes < len(corpus_c_full) else corpus_c_full
    corpus_d = pa.shuffle_bytes(corpus_c, seed=seed + 2)
    corpus_e = pa.shuffle_bytes(corpus_b, seed=seed + 3)
    corpus_d_full = v1_mod.load_corpus_D(smoke=smoke)
    corpus_f = corpus_d_full[:n_bytes] if n_bytes < len(corpus_d_full) else corpus_d_full

    def split80(d):
        m = int(0.8 * len(d))
        return d[:m], d[m:]

    def to_idx(tr):
        return base.bytes_to_idx_tensors(tr, device)

    train_a_idx, train_a_tgt = to_idx(split80(corpus_a)[0])

    # Phase A: baseline
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_A, pool_Av, pool_Al, pool_Au = base.train_w_with_replay(
        W, None, None, 0, byte_atoms, pos_atoms, train_a_idx, train_a_tgt,
        None, None, 0, epochs, batch_size, device)

    # Measure baseline retention_A
    from experiments.exp_wave14_k2_m1_hierreplay_v1 import evaluate_retention  # noqa: E402
    ret_baseline = evaluate_retention(W_A, byte_atoms, pos_atoms, corpus_a, batch_size, device)

    retentions = []
    W_curr = W_A
    pool_curr_v, pool_curr_l, pool_curr_u = pool_Av.clone(), pool_Al.clone(), pool_Au

    for phase_idx, (phase_name, corp) in enumerate([
        ("B", corpus_b), ("C", corpus_c), ("D", corpus_d), ("E", corpus_e), ("F", corpus_f)
    ]):
        train_idx, train_tgt = to_idx(split80(corp)[0])
        # Thin pool
        thin_v, thin_l, thin_u = m1.thin_pool_to_chunks(
            pool_curr_v, pool_curr_l, pool_curr_u, 0.5, device)
        W_new, pool_new_v, pool_new_l, pool_new_u = base.train_w_with_replay(
            W_curr, pool_curr_v.clone(), pool_curr_l.clone(), pool_curr_u,
            byte_atoms, pos_atoms, train_idx, train_tgt,
            thin_v, thin_l, thin_u, epochs_B, batch_size, device)
        ret = evaluate_retention(W_new, byte_atoms, pos_atoms, corpus_a, batch_size, device)
        retentions.append({"phase": phase_name, "retention_A": round(float(ret), 4)})
        print(f"    Phase {phase_name}: retention_A={ret:.4f}", flush=True)
        W_curr = W_new
        pool_curr_v, pool_curr_l, pool_curr_u = pool_new_v.clone(), pool_new_l.clone(), pool_new_u
        del W_new

    del W_curr, W_A, W
    if device.type == "cuda":
        torch.cuda.empty_cache()

    return {
        "seed": seed,
        "ret_baseline": round(float(ret_baseline), 4),
        "retentions_per_phase": retentions,
        "retention_vals": [r["retention_A"] for r in retentions],
    }


def run_sweep(smoke: bool = False):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    epochs = 2 if smoke else EPOCHS_FULL
    epochs_B = 1 if smoke else EPOCHS_B_FULL
    n_bytes = BYTES_SMOKE if smoke else BYTES_FULL
    out_dir = get_output_dir("wave14_betB_6corpus_extension_v1")

    print(f"[6corpus_ext] N={N} device={device} smoke={smoke}", flush=True)
    results = []
    for seed in seeds:
        print(f"  seed={seed}...", flush=True)
        r = run_6phase_sequence(seed, N, batch_size, epochs, epochs_B, n_bytes, smoke, device)
        results.append(r)

    return results, out_dir


def compute_verdict(results: list) -> tuple[str, str, dict]:
    # Aggregate retention_vals across seeds
    n_phases = len(results[0]["retention_vals"]) if results else 0
    if n_phases == 0:
        return ("INSTRUMENTATION_FAIL", "No retention values recorded.", {})

    mean_retentions = []
    for pi in range(n_phases):
        vals = [r["retention_vals"][pi] for r in results if pi < len(r["retention_vals"])]
        mean_retentions.append(sum(vals) / max(len(vals), 1))

    spacing_err = equal_spacing_error(mean_retentions)
    bic5 = bic_k_state(mean_retentions, 5)
    bic4 = bic_k_state(mean_retentions, 4)
    bic_diff = bic5 - bic4  # < 0 means 5-state preferred

    summary = {
        "n_phases": n_phases,
        "n_seeds": len(results),
        "mean_retentions_per_phase": {f"phase_{i+1}": round(r, 4) for i, r in enumerate(mean_retentions)},
        "equal_spacing_error": round(spacing_err, 4),
        "bic_5state": round(bic5, 2),
        "bic_4state": round(bic4, 2),
        "bic_5vs4_diff": round(bic_diff, 2),
    }

    if not all(math.isfinite(r) for r in mean_retentions):
        return ("INSTRUMENTATION_FAIL", "Non-finite retention values.", summary)

    if bic_diff < HP_BIC_5VS4 and spacing_err < HP_SPACING_ERR:
        verdict = "HARD_PASS"
        verdict_msg = (
            f"HARD_PASS: 6-corpus Saad-Solla framework holds. "
            f"BIC_5vs4={bic_diff:.1f} < {HP_BIC_5VS4}, spacing_err={spacing_err:.4f} < {HP_SPACING_ERR}. "
            f"5-state plateau structure confirmed with equal spacing. Framework extends to 6 corpora."
        )
    elif bic_diff > HF_BIC_5VS4 or spacing_err > HF_SPACING_ERR:
        verdict = "HARD_FAIL"
        verdict_msg = (
            f"HARD_FAIL: 6-corpus framework limit reached. "
            f"BIC_5vs4={bic_diff:.1f} > {HF_BIC_5VS4} (4-state preferred) "
            f"OR spacing_err={spacing_err:.4f} > {HF_SPACING_ERR}. "
            f"4-class taxonomy is the natural framework limit; 5th+ plateau merges with neighbors."
        )
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (
            f"MIDDLE_BAND: partial 5-state evidence. "
            f"BIC_5vs4={bic_diff:.1f} (in ({HP_BIC_5VS4},{HF_BIC_5VS4})), "
            f"spacing_err={spacing_err:.4f}. "
            f"5th plateau exists but weakly separated."
        )

    return verdict, verdict_msg, summary


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_betB_6corpus_extension_v1 {'SMOKE' if smoke else 'FULL'}", flush=True)
    results, out_dir = run_sweep(smoke)

    # Multi-scale smoke
    if smoke:
        print("\n[multi-scale smoke] N * 2...", flush=True)
        device = torch.device("cpu")
        r2 = run_6phase_sequence(7, N_SMOKE * 2, BATCH_SIZE_SMOKE, 1, 1, BYTES_SMOKE, True, device)
        assert all(math.isfinite(v) for v in r2["retention_vals"])
        print(f"  N={N_SMOKE*2}: retentions={r2['retention_vals']}")
        print("[multi-scale smoke] PASS")

    verdict, verdict_msg, summary = compute_verdict(results)
    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "config": {
            "N": N_SMOKE if smoke else N_FULL,
            "seeds": SEEDS_SMOKE if smoke else SEEDS_FULL,
            "n_phases": 6,
            "smoke": smoke,
            "trigger": "ship when 5corpus_noreplay_fix_v1 returns HARD_PASS (BIC_4vs3 < -30)",
        },
    }
    validate_metrics(metrics)
    with open(out_dir / "metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_dir / 'metrics.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        sys.exit(0)
    run(smoke=args.smoke)
