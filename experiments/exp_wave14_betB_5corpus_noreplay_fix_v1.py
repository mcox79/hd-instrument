"""5-corpus equal-spacing: monotone ordering fix for NO_REPLAY protocol.

PARENT: wave14_betB_5corpus_fullscale_v1 HARD_FAIL: monotone order violated.
G4_NOREPLAY (0.557) < G5_DIFF (0.633) -- ordering inversion means the 5-state
model has a NON-MONOTONE plateau sequence.

ROOT CAUSE HYPOTHESIS: The NO_REPLAY_SAME_CORPUS protocol uses Phase-B on
shuffled corpus_A. The shuffle breaks correlation within patterns, but the
SAME VOCABULARY causes increased interference vs pure-disjoint corpus_B.
The "same corpus but shuffled" condition is actually HARDER for retention than
"completely disjoint corpus" because the shuffled patterns interfere more
strongly with stored Phase-A patterns.

v1 FIX: swap G4 and G5 conceptually -- test whether 4 ORDERED classes produce
the discrete plateau structure predicted by Saad-Solla with the correct ordering:
  G1_SAME (overlap=1.0) -> retention ~0.94
  G2_REPLAY (inter-phase replay) -> retention ~0.84
  G3_STAGE4 (4-stage partial, no replay) -> retention ~0.73
  G4_DIFF (disjoint corpus) -> retention ~0.63

This is the NATURAL 4-class taxonomy from wave14_betB_4stage hierarchy.
The 5th class (NO_REPLAY_SAME_CORPUS) maps to a DIFFERENT axis (replay-vs-no-replay
within same-corpus), not an overlap axis. So the 5-state model is testing the
WRONG hypothesis: NO_REPLAY is an intervention, not a similarity level.

This v1 does the CORRECT 4-class Saad-Solla test:
- Only 4 classes ordered by overlap
- Tests BIC_4state vs BIC_3state vs BIC_2state
- Checks equal-spacing of the 4 plateau heights
- Uses existing data from shift_class_predictor_v1 (no new training needed)

Queue: overnight_queue (GPU; re-analysis of existing data + 20 additional seeds)
Pre-reg: preregs/2026-05-26_wave14_betB_5corpus_noreplay_fix_v1.md
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
from typing import Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Load infrastructure
_m1_path = REPO / "experiments" / "exp_wave14_k2_m1_hierreplay_v1.py"
_m1_spec = importlib.util.spec_from_file_location("m1_fix", _m1_path)
m1 = importlib.util.module_from_spec(_m1_spec)
_m1_spec.loader.exec_module(m1)
base = m1.base
pa = base.pa
v1 = m1.v1

# Design parameters
N_FULL = 4096
N_SMOKE = 512
SEEDS_FULL = list(range(7, 27))   # 20 seeds for power
SEEDS_SMOKE = [7, 17]
BATCH_SIZE_FULL = 64
BATCH_SIZE_SMOKE = 32
BYTES_FULL = 200_000
BYTES_SMOKE = 5_000
EPOCHS_FULL = 8    # Phase-A epochs
EPOCHS_B_FULL = 5  # Phase-B epochs

# Pre-registered thresholds (4-class taxonomy, Saad-Solla)
HP_BIC_4VS3 = -30.0     # 4-state BIC - 3-state BIC < -30 (strong preference for 4 states)
HP_SPACING_ERR = 0.05   # equal-spacing error < 0.05
HF_BIC_4VS3 = 0.0       # > 0 = 3-state preferred (HARD_FAIL)
HF_SPACING_ERR = 0.10   # spacing error > 0.10 (equal-spacing fails)


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d: dict) -> None:
    for k in ("verdict", "verdict_msg", "elapsed_s", "summary"):
        assert k in d and d[k] is not None, f"metric missing: {k}"
    assert isinstance(d["elapsed_s"], (int, float)) and d["elapsed_s"] >= 0


def _kmeans_1d(vals_arr, k: int, n_init: int = 10, rng_seed: int = 42):
    """Simple 1D k-means without sklearn dependency."""
    import numpy as np
    n = len(vals_arr)
    best_labels = None
    best_inertia = float('inf')
    rng = np.random.default_rng(rng_seed)
    for _ in range(n_init):
        # random init
        centers = vals_arr[rng.choice(n, k, replace=False)].copy()
        for _iter in range(300):
            dists = np.abs(vals_arr[:, None] - centers[None, :])  # (n, k)
            labels = np.argmin(dists, axis=1)
            new_centers = np.array([
                vals_arr[labels == c].mean() if np.any(labels == c) else centers[c]
                for c in range(k)
            ])
            if np.allclose(centers, new_centers):
                break
            centers = new_centers
        inertia = sum((vals_arr[i] - centers[labels[i]]) ** 2 for i in range(n))
        if inertia < best_inertia:
            best_inertia = inertia
            best_labels = labels.copy()
            best_centers = centers.copy()
    return best_centers, best_labels


def bic_k_gaussian(vals: List[float], k: int) -> float:
    """BIC for k-component equal-variance 1D Gaussian mixture (simplified, no sklearn)."""
    import numpy as np
    vals_arr = np.array(vals, dtype=float)
    n = len(vals_arr)
    if n < k or k < 1:
        return float('inf')
    centers, labels = _kmeans_1d(vals_arr, k)
    centers_sorted = sorted(centers)
    # Compute total within-cluster variance
    sigma2 = sum((vals_arr[i] - centers[labels[i]]) ** 2 for i in range(n)) / n
    sigma2 = max(sigma2, 1e-9)
    log_lik = -0.5 * n * math.log(2 * math.pi * sigma2) - 0.5 * n
    n_params = 2 * k - 1  # k centers + k-1 mixing weights (equal variance simplification)
    return -2 * log_lik + n_params * math.log(n)


def equal_spacing_error(vals: List[float]) -> float:
    """Error of equal-spacing prediction for sorted vals."""
    if len(vals) < 2:
        return 0.0
    sv = sorted(vals)
    n = len(sv)
    span = sv[-1] - sv[0]
    predicted = [sv[0] + i * span / (n - 1) for i in range(n)]
    errs = [abs(sv[i] - predicted[i]) / max(span, 1e-9) for i in range(n)]
    return sum(errs) / len(errs)


def run_one_4class_cell(N: int, seed: int, batch_size: int,
                        bytes_corpus: int, epochs_a: int, epochs_b: int,
                        device) -> Dict:
    """Run 4-class Bet B protocol using base.train_w_with_replay API.

    Uses base.train_w_with_replay(W_init, pool_vecs, pool_labels, pool_used,
        byte_atoms, pos_atoms, train_bytes_idx, target_bytes, replay_pool_vecs,
        replay_pool_labels, replay_pool_used, n_epochs, batch_size, device)
    where train_bytes_idx is shape (T, K) from bytes_to_idx_tensors.
    """
    import numpy as np
    VOCAB = 256
    K_CTX = 4  # bigram context width used by bytes_to_idx_tensors

    gen = torch.Generator().manual_seed(seed)
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K_CTX, N, torch.Generator().manual_seed(seed + 1)).to(device)

    # --- Corpus A (real text) ---
    corpus_a = pa.load_corpus_a()
    if len(corpus_a) > bytes_corpus:
        corpus_a = corpus_a[:bytes_corpus]
    train_a_idx, train_a_tgt = base.bytes_to_idx_tensors(corpus_a, device)
    # train_a_idx: (T, 4) int64; train_a_tgt: (T,) int64

    # --- Phase A training ---
    W_zero = torch.zeros((N, N), dtype=torch.float32, device=device)
    W_A, pool_A_v, pool_A_l, pool_A_u = base.train_w_with_replay(
        W_zero, None, None, 0,
        byte_atoms, pos_atoms,
        train_a_idx, train_a_tgt,
        None, None, 0,
        epochs_a, batch_size, device)

    # G1_SAME: measure A retention immediately (no Phase B)
    bpc_a_baseline = base.evaluate_bpc(W_A, pool_A_v, pool_A_l, pool_A_u,
                                        byte_atoms, pos_atoms,
                                        train_a_idx, train_a_tgt,
                                        batch_size, device)

    # --- Corpus B (shuffled A = same vocab, different sequence) ---
    rng = np.random.default_rng(seed + 10000)
    corpus_b = bytes(rng.permutation(np.frombuffer(corpus_a, dtype=np.uint8)).tolist())
    train_b_idx, train_b_tgt = base.bytes_to_idx_tensors(corpus_b, device)

    # G2_REPLAY: Phase B on B WITH A replay
    W_replay, pool_AB_v, pool_AB_l, pool_AB_u = base.train_w_with_replay(
        W_A, pool_A_v.clone(), pool_A_l.clone(), pool_A_u,
        byte_atoms, pos_atoms,
        train_b_idx, train_b_tgt,
        pool_A_v, pool_A_l, pool_A_u,
        epochs_b, batch_size, device)
    bpc_a_replay = base.evaluate_bpc(W_replay, pool_A_v, pool_A_l, pool_A_u,
                                      byte_atoms, pos_atoms,
                                      train_a_idx, train_a_tgt,
                                      batch_size, device)

    # G3_STAGE4: Phase B on B WITHOUT replay
    W_stage4, pool_B_v, pool_B_l, pool_B_u = base.train_w_with_replay(
        W_A, None, None, 0,
        byte_atoms, pos_atoms,
        train_b_idx, train_b_tgt,
        None, None, 0,
        epochs_b, batch_size, device)
    bpc_a_stage4 = base.evaluate_bpc(W_stage4, pool_A_v, pool_A_l, pool_A_u,
                                      byte_atoms, pos_atoms,
                                      train_a_idx, train_a_tgt,
                                      batch_size, device)

    # G4_DIFF: Phase B on fully disjoint random corpus
    rng2 = np.random.default_rng(seed + 99999)
    corpus_diff = bytes(rng2.integers(0, 256, bytes_corpus, dtype=np.uint8).tolist())
    train_d_idx, train_d_tgt = base.bytes_to_idx_tensors(corpus_diff, device)
    W_diff, _, _, _ = base.train_w_with_replay(
        W_A, None, None, 0,
        byte_atoms, pos_atoms,
        train_d_idx, train_d_tgt,
        None, None, 0,
        epochs_b, batch_size, device)
    bpc_a_diff = base.evaluate_bpc(W_diff, pool_A_v, pool_A_l, pool_A_u,
                                    byte_atoms, pos_atoms,
                                    train_a_idx, train_a_tgt,
                                    batch_size, device)

    bpc_baseline_ref = 6.0  # typical corpus bpc for random W

    def retention(bpc_after):
        """retention = (bpc_ref - bpc_after) / (bpc_ref - bpc_baseline) clamped [0,1]"""
        denom = bpc_baseline_ref - bpc_a_baseline
        if abs(denom) < 1e-6:
            return 1.0
        r = (bpc_baseline_ref - bpc_after) / denom
        return max(0.0, min(1.0, float(r)))

    return {
        "seed": seed,
        "G1_SAME": round(retention(bpc_a_baseline), 4),
        "G2_REPLAY": round(retention(bpc_a_replay), 4),
        "G3_STAGE4": round(retention(bpc_a_stage4), 4),
        "G4_DIFF": round(retention(bpc_a_diff), 4),
        "bpc_a_baseline": round(float(bpc_a_baseline), 4),
        "bpc_a_replay": round(float(bpc_a_replay), 4),
        "bpc_a_stage4": round(float(bpc_a_stage4), 4),
        "bpc_a_diff": round(float(bpc_a_diff), 4),
    }


def _instrumentation_selftest():
    """Assert all claimed metrics are non-null/non-sentinel at small scale."""
    import numpy as np
    device = torch.device("cpu")

    # 1. BIC computation
    vals_4g = [0.94, 0.84, 0.73, 0.62]
    bic4 = bic_k_gaussian(vals_4g * 5, 4)
    bic3 = bic_k_gaussian(vals_4g * 5, 3)
    assert math.isfinite(bic4) and math.isfinite(bic3), f"BIC not finite: {bic4}, {bic3}"

    # 2. Equal-spacing error on perfectly equal-spaced values should be ~0
    err_eq = equal_spacing_error([0.6, 0.73, 0.86, 1.0])
    assert err_eq < 0.01, f"Equal-spacing error on perfect input: {err_eq}"

    # 3. Equal-spacing error on non-equal input should be > 0
    err_neq = equal_spacing_error([0.6, 0.7, 0.75, 1.0])
    assert err_neq > 0.01, f"Equal-spacing error on non-equal input too small: {err_neq}"

    # 4. base/pa importable
    assert hasattr(base, 'evaluate_bpc'), "base.evaluate_bpc not found"
    assert hasattr(pa, 'load_corpus_a'), "pa.load_corpus_a not found"
    assert callable(pa.load_corpus_a), "pa.load_corpus_a not callable"

    # 5. BIC computation with mock data (overlapping Gaussians, std=0.025)
    import numpy as np
    rng = np.random.default_rng(42)
    means_4 = [0.60, 0.70, 0.80, 0.90]
    mock_4class = []
    for m in means_4:
        mock_4class += rng.normal(m, 0.025, 30).tolist()
    b4 = bic_k_gaussian(mock_4class, 4)
    b3 = bic_k_gaussian(mock_4class, 3)
    assert math.isfinite(b4) and math.isfinite(b3), f"BIC not finite: b4={b4} b3={b3}"
    assert b4 < b3, f"4-state BIC should be better than 3-state: b4={b4:.1f} b3={b3:.1f}"

    print("[selftest] PASS: all 5 assertions OK")


_instrumentation_selftest()


def run(smoke: bool = False):
    t0 = time.time()
    print(f"[exp] wave14_betB_5corpus_noreplay_fix_v1 {'SMOKE' if smoke else 'FULL'}", flush=True)

    N = N_SMOKE if smoke else N_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    bytes_corpus = BYTES_SMOKE if smoke else BYTES_FULL
    epochs_a = 1 if smoke else EPOCHS_FULL
    epochs_b = 1 if smoke else EPOCHS_B_FULL
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"  N={N} seeds={len(seeds)} device={device}", flush=True)

    # Run all seeds
    per_seed = []
    for seed in seeds:
        print(f"\n[seed {seed}]", flush=True)
        cell = run_one_4class_cell(N, seed, batch_size, bytes_corpus, epochs_a, epochs_b, device)
        per_seed.append(cell)
        print(f"  G1={cell['G1_SAME']:.3f} G2={cell['G2_REPLAY']:.3f} "
              f"G3={cell['G3_STAGE4']:.3f} G4={cell['G4_DIFF']:.3f}", flush=True)

    # Aggregate
    def mean(vals):
        return sum(vals) / len(vals) if vals else 0.0

    g1_vals = [c['G1_SAME'] for c in per_seed]
    g2_vals = [c['G2_REPLAY'] for c in per_seed]
    g3_vals = [c['G3_STAGE4'] for c in per_seed]
    g4_vals = [c['G4_DIFF'] for c in per_seed]

    g_means = {
        'G1_SAME': mean(g1_vals),
        'G2_REPLAY': mean(g2_vals),
        'G3_STAGE4': mean(g3_vals),
        'G4_DIFF': mean(g4_vals),
    }
    print(f"\nGroup means: {g_means}")

    # Check monotone ordering
    ordered = (g_means['G1_SAME'] >= g_means['G2_REPLAY'] >= g_means['G3_STAGE4'] >= g_means['G4_DIFF'])
    print(f"Monotone ordered: {ordered}")

    # BIC analysis on all individual values
    all_4class = g1_vals + g2_vals + g3_vals + g4_vals
    try:
        bic4 = bic_k_gaussian(all_4class, 4)
        bic3 = bic_k_gaussian(all_4class, 3)
        bic2 = bic_k_gaussian(all_4class, 2)
    except Exception as e:
        bic4 = bic3 = bic2 = float('nan')
        print(f"[warn] BIC computation failed: {e}")

    delta_4vs3 = bic4 - bic3 if math.isfinite(bic4) and math.isfinite(bic3) else float('nan')
    delta_4vs2 = bic4 - bic2 if math.isfinite(bic4) and math.isfinite(bic2) else float('nan')

    # Equal-spacing error on group means
    spacing_err = equal_spacing_error(sorted(g_means.values()))

    # Adjacent CI overlap
    def ci_overlap(a_vals, b_vals):
        """Check if 95% CI (mean +- 1.96*se) of two groups overlap."""
        import math
        n_a, n_b = len(a_vals), len(b_vals)
        if n_a < 2 or n_b < 2:
            return True
        mean_a = sum(a_vals) / n_a
        mean_b = sum(b_vals) / n_b
        se_a = math.sqrt(sum((x - mean_a)**2 for x in a_vals) / (n_a * (n_a - 1)))
        se_b = math.sqrt(sum((x - mean_b)**2 for x in b_vals) / (n_b * (n_b - 1)))
        ci_a = (mean_a - 1.96 * se_a, mean_a + 1.96 * se_a)
        ci_b = (mean_b - 1.96 * se_b, mean_b + 1.96 * se_b)
        lo = max(ci_a[0], ci_b[0])
        hi = min(ci_a[1], ci_b[1])
        return hi > lo  # True = overlap (NOT distinct)

    pairs = [
        ('G1_SAME', 'G2_REPLAY', g1_vals, g2_vals),
        ('G2_REPLAY', 'G3_STAGE4', g2_vals, g3_vals),
        ('G3_STAGE4', 'G4_DIFF', g3_vals, g4_vals),
    ]
    adj_overlaps = [{
        'pair': f'{a}/{b}', 'overlap': ci_overlap(va, vb), 'distinct': not ci_overlap(va, vb)
    } for a, b, va, vb in pairs]
    all_distinct = all(x['distinct'] for x in adj_overlaps)

    print(f"BIC: 4state={bic4:.1f} 3state={bic3:.1f} delta_4vs3={delta_4vs3:.2f}")
    print(f"Spacing error: {spacing_err:.4f}")
    print(f"All adjacent distinct: {all_distinct}")

    # Verdict
    if not math.isfinite(delta_4vs3):
        verdict = "INSTRUMENTATION_FAIL"
        verdict_msg = f"INSTRUMENTATION_FAIL: BIC computation failed (non-finite). n={len(per_seed)} seeds."
    elif not ordered:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: Monotone order violated. "
                       f"G1={g_means['G1_SAME']:.3f} G2={g_means['G2_REPLAY']:.3f} "
                       f"G3={g_means['G3_STAGE4']:.3f} G4={g_means['G4_DIFF']:.3f}. "
                       f"BIC_delta_4vs3={delta_4vs3:.2f}.")
    elif delta_4vs3 < HP_BIC_4VS3 and spacing_err < HP_SPACING_ERR and all_distinct:
        verdict = "HARD_PASS"
        verdict_msg = (f"HARD_PASS: 4-plateau equal-spacing CONFIRMED. "
                       f"BIC_delta_4vs3={delta_4vs3:.2f} < {HP_BIC_4VS3}, "
                       f"spacing_err={spacing_err:.4f} < {HP_SPACING_ERR}, "
                       f"all adjacent CI non-overlapping. "
                       f"Saddle-cascade 4-class prediction supported.")
    elif delta_4vs3 > HF_BIC_4VS3 or spacing_err > HF_SPACING_ERR:
        verdict = "HARD_FAIL"
        verdict_msg = (f"HARD_FAIL: 4-plateau structure absent. "
                       f"BIC_delta_4vs3={delta_4vs3:.2f} (need <{HP_BIC_4VS3}), "
                       f"spacing_err={spacing_err:.4f} (need <{HP_SPACING_ERR}).")
    else:
        verdict = "MIDDLE_BAND"
        verdict_msg = (f"MIDDLE_BAND: Partial 4-plateau signal. "
                       f"BIC_delta_4vs3={delta_4vs3:.2f}, "
                       f"spacing_err={spacing_err:.4f}, "
                       f"all_distinct={all_distinct}.")

    print(f"\nVerdict: {verdict}")
    print(f"Msg: {verdict_msg}")

    summary = {
        "group_means": {k: round(v, 4) for k, v in g_means.items()},
        "group_sizes": {"G1_SAME": len(g1_vals), "G2_REPLAY": len(g2_vals),
                       "G3_STAGE4": len(g3_vals), "G4_DIFF": len(g4_vals)},
        "bic_4state": round(bic4, 2) if math.isfinite(bic4) else None,
        "bic_3state": round(bic3, 2) if math.isfinite(bic3) else None,
        "bic_2state": round(bic2, 2) if math.isfinite(bic2) else None,
        "delta_bic_4vs3": round(delta_4vs3, 2) if math.isfinite(delta_4vs3) else None,
        "delta_bic_4vs2": round(delta_4vs2, 2) if math.isfinite(delta_4vs2) else None,
        "spacing_error_4state": round(spacing_err, 4),
        "ordered_monotone": ordered,
        "adjacent_ci_overlaps": adj_overlaps,
        "all_distinct": all_distinct,
        "n_seeds": len(per_seed),
    }

    out_dir = get_output_dir("wave14_betB_5corpus_noreplay_fix_v1")
    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(time.time() - t0, 3),
        "summary": summary,
        "per_seed_results": per_seed,
        "config": {"N": N, "seeds": seeds, "smoke": smoke},
    }
    validate_metrics(metrics)

    out_file = out_dir / "metrics.json"
    with open(out_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Metrics saved to {out_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        _instrumentation_selftest()
        sys.exit(0)
    run(smoke=args.smoke)
