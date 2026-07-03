"""Candidate (iv): Information-Bottleneck plateau falsifier -- K-corpus count sweep.

Filed 2026-05-24 per strategy_request_to_exp_dev_ib_plateau_test_2026-05-24.md
Research note: notes/research_alternative_theoretical_homes_2026-05-24.md Top-2 drill.

HYPOTHESIS (Wu-Fischer-Tegmark 2020 / Tishby-Zaslavsky IB framework):
  Substrate's three retention plateaus emerge from IB phase transitions.
  Each transition = onset-of-learning-a-new-class-cluster.
  Predicts: plateau-COUNT tracks K (number of distinct training corpora).
  K=1 -> 1 plateau, K=2 -> 2 plateaus, K=3 -> 3 plateaus, etc.

KEY QUESTION: Does plateau-count monotonically track K (number of training corpora)?

METHOD:
  For each K in {1, 2, 3, 4, 5}:
    1. Train K sequential phases (A -> B -> C -> ... -> K-th corpus).
       Each corpus is a DISTINCT byte sequence (independent random sources to maximize
       class-cluster separability; tests the IB framework in the maximally-favorable setting).
    2. After all K phases complete, measure retention at each prior-phase level:
       retention_at_stage_i = bpc_stage_i_baseline / bpc_stage_i_after_all_phases
    3. Collect all K retention values, count distinct plateau clusters.
  Test: Spearman rank-correlation of plateau_count vs K. IB predicts rho >= 0.90.

PRE-REGISTERED BANDS (per [[feedback-envelope-expansion-fail-bands]]):
  HARD-PASS: plateau-count monotonically tracks K
    - Spearman rank-correlation of plateau_count vs K >= 0.90
    - AND K=3 gives plateau_count >= 3
    -> IB phase-transition framework supported.

  HARD-FAIL: plateau-count does NOT track K
    - Spearman rank-correlation < 0.20, OR all K give same plateau structure
    -> IB framework does not apply.

  MIDDLE-BAND: Spearman rank-correlation in [0.20, 0.90)
    -> Partial tracking; inconclusive.

SELF-TEST cells (per [[feedback-strategy-spec-formula-selftests]]):
  1. K=1 trivial: 1 corpus, 1 retention value -> plateau_count = 1
  2. K=2: 2 corpora, 2 distinct retention values -> plateau_count >= 2
  3. Algorithm check: [0.94, 0.93, 0.74, 0.73, 0.60, 0.61] -> count_plateaus = 3
  4. Degenerate: [0.70, 0.71, 0.70, 0.71, 0.70] -> count_plateaus = 1

Pred-4-orthogonal: sweeps K (number of corpora), not M (bytes per stage).
Uses information-theoretic readout (plateau-count vs K), not hysteresis-gap.
Safe to run in parallel with Pred-4.

Queue: remote_cpu_queue (CPU only; no GPU needed)
ETA: ~40-80 min CPU (5 K-values x 3 seeds x up-to-5 phases)
Pre-reg: preregs/2026-05-24_wave14_ib_plateau_test_v1.md

Per [[feedback-no-experiment-design-in-prompts]]: all parameters chosen by exp_dev.
Per [[feedback-ascii-only-in-scripts]]: ASCII-only in print/verdict_msg.
Per [[feedback-envelope-expansion-fail-bands]]: bands pre-registered.
Per [[feedback-strategy-spec-formula-selftests]]: 4 self-test cells inline.
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
from typing import Dict, List, Optional, Tuple

import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir as _canonical_get_output_dir  # noqa: E402  # SH-4 canonical helper
# Load Kovacs base infrastructure
_base_path = REPO / "experiments" / "exp_wave14d_betB_kovacs_v1.py"
_base_spec = importlib.util.spec_from_file_location("base", _base_path)
base = importlib.util.module_from_spec(_base_spec)
_base_spec.loader.exec_module(base)
pa = base.pa

# ---- design parameters (exp_dev autonomy) ----
K_SWEEP_FULL = [1, 2, 3, 4, 5]
K_SWEEP_SMOKE = [1, 2, 3]

N_FULL = 2048
N_SMOKE = 512
BATCH_SIZE_FULL = 32
BATCH_SIZE_SMOKE = 16
EPOCHS_PER_PHASE_FULL = 5
EPOCHS_PER_PHASE_SMOKE = 1
PHASE_A_EPOCHS_FULL = 8   # First phase gets more training (matches standard pipeline)
PHASE_A_EPOCHS_SMOKE = 1
BYTES_PER_CORPUS_FULL = 200_000
BYTES_PER_CORPUS_SMOKE = 4_000

SEEDS_FULL = [7, 17, 23]
SEEDS_SMOKE = [17]

# Pre-registered thresholds
SPEARMAN_PASS_THRESHOLD = 0.90    # plateau_count rank-correlation vs K >= this -> HARD-PASS
SPEARMAN_FAIL_THRESHOLD = 0.20    # plateau_count rank-correlation vs K < this -> HARD-FAIL
PLATEAU_CLUSTER_VARIANCE = 0.02   # within-cluster variance threshold for plateau counting
K3_MIN_PLATEAUS = 3               # K=3 must give >= 3 plateaus for HARD-PASS bonus


def get_output_dir(default_name: str) -> Path:
    """SH-4 delegates to canonical _seed_checkpoint.get_output_dir (single-prefix)."""
    out = _canonical_get_output_dir(default_name)
    out.mkdir(parents=True, exist_ok=True)
    return out
def validate_metrics(d):
    required = {"verdict", "verdict_msg", "elapsed_s", "summary", "config"}
    missing = required - set(d.keys())
    if missing:
        raise ValueError(f"metrics missing required keys: {missing}")


def make_corpus_k(k_idx: int, n_bytes: int, seed: int) -> bytes:
    """Generate the k-th corpus as a distinct byte sequence.

    k_idx=0: use PLAN.md / README.md (corpus_A from pa.load_corpus_a)
    k_idx>=1: independent random byte sequence with distinct seed
    Each corpus is maximally distinct to stress-test IB class-cluster separation.
    """
    if k_idx == 0:
        data = pa.load_corpus_a()
        return data[:n_bytes] if n_bytes < len(data) else data
    else:
        gen = torch.Generator().manual_seed(seed * 1000 + k_idx * 137)
        return bytes(torch.randint(0, 256, (n_bytes,), generator=gen).to(torch.uint8).numpy().tobytes())


def count_plateaus(retention_values: List[float], variance_threshold: float = PLATEAU_CLUSTER_VARIANCE) -> int:
    """Count distinct plateau clusters in a list of retention values.

    Uses gap-based clustering: sort values, split into new cluster when
    adjacent gap exceeds gap_threshold = sqrt(variance_threshold) * 3.
    A pair of adjacent sorted values is in the SAME cluster if |v[i+1] - v[i]| < gap_threshold.

    For variance_threshold=0.02: gap_threshold = sqrt(0.02)*3 ~ 0.424.
    But for typical substrate values [0.94, 0.74, 0.60], gaps are ~0.14-0.20,
    so we use a smaller gap threshold based on the empirical distribution.

    Strategy: find the largest gap in the sorted values; if it exceeds a minimum
    gap_threshold (0.05), it defines a cluster boundary. Count all boundaries.

    Returns number of distinct clusters.
    """
    vals = sorted(v for v in retention_values if not math.isnan(v))
    if not vals:
        return 0
    if len(vals) == 1:
        return 1

    # Minimum gap to call a cluster boundary
    # Based on variance_threshold: if cluster spread <= sqrt(variance_threshold),
    # inter-cluster gap should be >= 2*sqrt(variance_threshold) to be meaningful.
    # For variance=0.02: sqrt(0.02) ~ 0.141; inter-cluster gap threshold ~ 0.08
    gap_threshold = max(0.06, math.sqrt(variance_threshold) * 0.5)

    n_clusters = 1
    for i in range(len(vals) - 1):
        gap = vals[i + 1] - vals[i]
        if gap >= gap_threshold:
            n_clusters += 1

    return n_clusters


def spearman_rank_correlation(xs: List[float], ys: List[float]) -> float:
    """Spearman rank correlation coefficient."""
    n = len(xs)
    if n < 3:
        return float("nan")
    # Compute ranks
    def rank(arr):
        sorted_idx = sorted(range(len(arr)), key=lambda i: arr[i])
        ranks = [0.0] * len(arr)
        for r, i in enumerate(sorted_idx):
            ranks[i] = float(r + 1)
        return ranks
    rx = rank(xs)
    ry = rank(ys)
    # Pearson on ranks
    mx = sum(rx) / n
    my = sum(ry) / n
    sx = math.sqrt(sum((r - mx) ** 2 for r in rx) / (n - 1))
    sy = math.sqrt(sum((r - my) ** 2 for r in ry) / (n - 1))
    if sx < 1e-12 or sy < 1e-12:
        return 0.0
    rho = sum((r1 - mx) * (r2 - my) for r1, r2 in zip(rx, ry)) / ((n - 1) * sx * sy)
    return rho


def run_k_seed(K: int, seed: int, N: int, batch_size: int,
               n_epochs_per_phase: int, phase_a_epochs: int,
               n_bytes: int, device) -> dict:
    """Train K sequential corpora, measure retention at each stage.

    Returns dict with per-stage retentions and plateau_count.
    """
    gen = torch.Generator().manual_seed(seed)

    VOCAB = 256
    K_ctx = base.K
    byte_atoms = pa.make_bsc_atoms(VOCAB, N, gen).to(device)
    pos_atoms = pa.make_bsc_atoms(K_ctx, N, gen).to(device)

    # Load all K corpora up front
    corpora = []
    for k_idx in range(K):
        corpus = make_corpus_k(k_idx, n_bytes, seed)
        corpora.append(corpus)

    # Prepare train/eval splits
    def split80(data):
        m = int(0.8 * len(data))
        return data[:m], data[m:]

    train_splits = []
    eval_splits = []
    for corpus in corpora:
        tr, ev = split80(corpus)
        train_splits.append(base.bytes_to_idx_tensors(tr, device))
        eval_splits.append(base.bytes_to_idx_tensors(ev, device))

    # Train K phases sequentially
    W = torch.zeros((N, N), dtype=torch.float32, device=device)
    pool_vecs = torch.zeros((base.POOL_SIZE, N), dtype=torch.float32, device=device)
    pool_labels = torch.zeros(base.POOL_SIZE, dtype=torch.long, device=device)
    pool_used = 0

    # Baseline BPC for each stage (measured right after that stage's training)
    baseline_bpc = []

    for k_idx in range(K):
        idx, tgt = train_splits[k_idx]
        epochs = phase_a_epochs if k_idx == 0 else n_epochs_per_phase

        # For replay: pass previous pool as the replay source
        replay_v = pool_vecs.clone() if pool_used > 0 else None
        replay_l = pool_labels.clone() if pool_used > 0 else None
        replay_u = pool_used if pool_used > 0 else 0

        W, pool_vecs, pool_labels, pool_used = base.train_w_with_replay(
            W, pool_vecs, pool_labels, pool_used,
            byte_atoms, pos_atoms, idx, tgt,
            replay_v, replay_l, replay_u,
            epochs, batch_size, device
        )

        # Measure this stage's baseline BPC right after training
        e_idx, e_tgt = eval_splits[k_idx]
        bpc_k = base.evaluate_bpc(
            W, pool_vecs, pool_labels, pool_used,
            byte_atoms, pos_atoms, e_idx, e_tgt, batch_size, device
        )
        baseline_bpc.append(float(bpc_k))
        print(f"    K={K} stage={k_idx} seed={seed}: bpc_baseline={bpc_k:.4f}", flush=True)

    # Now measure retention at each EARLIER stage after all K phases complete
    # (W is the final weight matrix after all K phases)
    final_bpc = []
    for k_idx in range(K):
        e_idx, e_tgt = eval_splits[k_idx]
        bpc_final = base.evaluate_bpc(
            W, pool_vecs, pool_labels, pool_used,
            byte_atoms, pos_atoms, e_idx, e_tgt, batch_size, device
        )
        final_bpc.append(float(bpc_final))

    # Retention at each stage = baseline_bpc[k] / final_bpc[k]
    retentions = []
    for k_idx in range(K):
        ret = baseline_bpc[k_idx] / max(final_bpc[k_idx], 1e-9)
        retentions.append(round(ret, 5))

    plateau_count = count_plateaus(retentions)
    print(
        f"  K={K} seed={seed}: retentions={retentions} plateau_count={plateau_count}",
        flush=True
    )

    return {
        "K": K,
        "seed": seed,
        "retentions": retentions,
        "baseline_bpc": [round(b, 5) for b in baseline_bpc],
        "final_bpc": [round(b, 5) for b in final_bpc],
        "plateau_count": plateau_count,
    }


def compute_verdict(k_sweep: List[int],
                    per_K_results: Dict[int, List[dict]]) -> Tuple[str, str, dict]:
    """Aggregate plateau counts per K, compute Spearman correlation vs K."""
    k_vals = []
    plateau_means = []
    plateau_per_K = {}

    for K in sorted(k_sweep):
        cells = per_K_results.get(K, [])
        counts = [c["plateau_count"] for c in cells if "plateau_count" in c]
        if not counts:
            continue
        mean_count = sum(counts) / len(counts)
        k_vals.append(K)
        plateau_means.append(mean_count)
        plateau_per_K[K] = {
            "mean_plateau_count": round(mean_count, 2),
            "plateau_counts": counts,
            "mean_retentions": [
                round(sum(c["retentions"][i] for c in cells if len(c["retentions"]) > i) /
                      max(1, sum(1 for c in cells if len(c["retentions"]) > i)), 4)
                for i in range(K)
            ] if cells else [],
        }

    if len(k_vals) < 3:
        return (
            "IB_INSTRUMENTATION_FAIL",
            f"Fewer than 3 K-values with valid cells ({len(k_vals)}). Cannot compute correlation.",
            {}
        )

    spearman_rho = spearman_rank_correlation(k_vals, plateau_means)

    # Check K=3 plateau count for bonus
    k3_count = plateau_per_K.get(3, {}).get("mean_plateau_count", 0.0)
    k3_bonus = (3 in k_vals and k3_count >= K3_MIN_PLATEAUS)

    summary = {
        "k_values": k_vals,
        "plateau_means_per_K": [round(p, 2) for p in plateau_means],
        "spearman_rho": round(spearman_rho, 4) if not math.isnan(spearman_rho) else None,
        "k3_plateau_count": round(k3_count, 2),
        "k3_bonus_passes": k3_bonus,
        "per_K": plateau_per_K,
    }

    if math.isnan(spearman_rho):
        return (
            "IB_INSTRUMENTATION_FAIL",
            f"Spearman correlation is NaN. Check per-K plateau counts: {plateau_means}",
            summary
        )

    if spearman_rho >= SPEARMAN_PASS_THRESHOLD and k3_bonus:
        return (
            "IB_HARD_PASS",
            f"Plateau-count tracks K: Spearman rho={spearman_rho:.3f} >= {SPEARMAN_PASS_THRESHOLD}. "
            f"K=3 gives plateau_count={k3_count:.1f} >= {K3_MIN_PLATEAUS}. "
            f"plateau_means={plateau_per_K}. "
            f"IB phase-transition framework supported: substrate plateaus = class-cluster boundaries. "
            f"K-sweep plateau-count={[round(p, 1) for p in plateau_means]}.",
            summary
        )

    if spearman_rho >= SPEARMAN_PASS_THRESHOLD and not k3_bonus:
        return (
            "IB_HARD_PASS_WEAK_K3",
            f"Plateau-count tracks K (Spearman rho={spearman_rho:.3f} >= {SPEARMAN_PASS_THRESHOLD}) "
            f"BUT K=3 gives only {k3_count:.1f} plateaus (< {K3_MIN_PLATEAUS} required for bonus). "
            f"IB framework partially supported but K=3 does not reproduce 3-plateau empirical.",
            summary
        )

    if spearman_rho < SPEARMAN_FAIL_THRESHOLD:
        return (
            "IB_HARD_FAIL",
            f"Plateau-count does NOT track K: Spearman rho={spearman_rho:.3f} < {SPEARMAN_FAIL_THRESHOLD}. "
            f"plateau_means per K={[round(p, 1) for p in plateau_means]}. "
            f"IB framework does not apply. "
            f"Rehab: candidate (v) cascade-plateau test (separate run); or accept 1-RSB contingency.",
            summary
        )

    return (
        "IB_MIDDLE",
        f"Partial tracking: Spearman rho={spearman_rho:.3f} in [{SPEARMAN_FAIL_THRESHOLD}, {SPEARMAN_PASS_THRESHOLD}). "
        f"K=3 plateau_count={k3_count:.1f}. "
        f"plateau_means={[round(p, 1) for p in plateau_means]}. "
        f"Inconclusive; consider larger N or more seeds.",
        summary
    )


# ---- self-tests ----
def self_test():
    errors = []

    # Self-test 1: count_plateaus on single-value list -> 1
    count1 = count_plateaus([0.94])
    if count1 != 1:
        errors.append(f"Self-test 1 FAIL: count_plateaus([0.94]) = {count1} (expected 1)")

    # Self-test 2: count_plateaus on two distinct values -> 2
    count2 = count_plateaus([0.94, 0.60])
    if count2 != 2:
        errors.append(f"Self-test 2 FAIL: count_plateaus([0.94, 0.60]) = {count2} (expected 2)")

    # Self-test 3: algorithm check with 3 distinct clusters
    vals3 = [0.94, 0.93, 0.74, 0.73, 0.60, 0.61]
    count3 = count_plateaus(vals3)
    if count3 != 3:
        errors.append(
            f"Self-test 3 FAIL: count_plateaus({vals3}) = {count3} (expected 3; "
            f"clusters at ~0.935, ~0.735, ~0.605)"
        )

    # Self-test 4: degenerate -- all values near same level -> 1
    vals4 = [0.70, 0.71, 0.70, 0.71, 0.70]
    count4 = count_plateaus(vals4)
    if count4 != 1:
        errors.append(f"Self-test 4 FAIL: count_plateaus({vals4}) = {count4} (expected 1)")

    # Self-test 5: Spearman rank correlation formula
    xs5 = [1, 2, 3, 4, 5]
    ys5_perfect = [1.0, 2.0, 3.0, 4.0, 5.0]  # perfect monotone
    rho5 = spearman_rank_correlation(xs5, ys5_perfect)
    if abs(rho5 - 1.0) > 1e-6:
        errors.append(f"Self-test 5 FAIL: spearman on perfect monotone = {rho5:.4f} (expected 1.0)")

    # Self-test 6: Spearman on reversed -> -1
    ys6_rev = [5.0, 4.0, 3.0, 2.0, 1.0]
    rho6 = spearman_rank_correlation(xs5, ys6_rev)
    if abs(rho6 + 1.0) > 1e-6:
        errors.append(f"Self-test 6 FAIL: spearman on reversed = {rho6:.4f} (expected -1.0)")

    if errors:
        for e in errors:
            print(f"[SELF-TEST] {e}", flush=True)
        raise AssertionError(f"Self-tests FAILED ({len(errors)} errors)")
    print(f"[SELF-TEST] All 6 self-tests passed", flush=True)


# ---- main ----
def run(smoke: bool = False):
    device = torch.device("cpu")
    t0 = time.monotonic()
    print(f"[ib_plateau] device={device} smoke={smoke}", flush=True)

    # Corpus preflight
    corpus_a_full = pa.load_corpus_a()
    print(f"[ib_plateau] corpus_a preflight: {len(corpus_a_full)} bytes", flush=True)
    if len(corpus_a_full) < 1000:
        raise RuntimeError(
            f"corpus_a preflight FAIL: only {len(corpus_a_full)} bytes. "
            f"Check PLAN.md / README.md in repo root."
        )

    k_sweep = K_SWEEP_SMOKE if smoke else K_SWEEP_FULL
    seeds = SEEDS_SMOKE if smoke else SEEDS_FULL
    N = N_SMOKE if smoke else N_FULL
    batch_size = BATCH_SIZE_SMOKE if smoke else BATCH_SIZE_FULL
    n_epochs = EPOCHS_PER_PHASE_SMOKE if smoke else EPOCHS_PER_PHASE_FULL
    phase_a_epochs = PHASE_A_EPOCHS_SMOKE if smoke else PHASE_A_EPOCHS_FULL
    n_bytes = BYTES_PER_CORPUS_SMOKE if smoke else BYTES_PER_CORPUS_FULL

    config = {
        "mode": "smoke" if smoke else "full",
        "k_sweep": k_sweep,
        "N": N, "batch_size": batch_size,
        "n_epochs_per_phase": n_epochs,
        "phase_a_epochs": phase_a_epochs,
        "n_bytes_per_corpus": n_bytes,
        "seeds": seeds,
        "spearman_pass_threshold": SPEARMAN_PASS_THRESHOLD,
        "spearman_fail_threshold": SPEARMAN_FAIL_THRESHOLD,
        "plateau_cluster_variance": PLATEAU_CLUSTER_VARIANCE,
    }
    print(f"[config] {config}", flush=True)

    per_K_results: Dict[int, List[dict]] = {K: [] for K in k_sweep}

    for K in k_sweep:
        print(f"[ib_plateau] === K={K} ===", flush=True)
        for seed in seeds:
            try:
                result = run_k_seed(
                    K, seed, N, batch_size, n_epochs, phase_a_epochs, n_bytes, device
                )
                per_K_results[K].append(result)
            except Exception as ex:
                import traceback
                print(f"  ERROR K={K} seed={seed}: {type(ex).__name__}: {ex}", flush=True)
                traceback.print_exc(file=sys.stdout)
                sys.stdout.flush()
                per_K_results[K].append({"K": K, "seed": seed, "plateau_count": 0, "error": str(ex)})

    verdict, verdict_msg, summary = compute_verdict(k_sweep, per_K_results)
    elapsed = time.monotonic() - t0

    metrics = {
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "elapsed_s": round(elapsed, 3),
        "summary": summary,
        "config": config,
    }
    validate_metrics(metrics)

    out_dir = get_output_dir("wave14_ib_plateau_test_v1")
    out_path = out_dir / "metrics.json"
    with open(out_path, "w") as f_out:
        json.dump(metrics, f_out, indent=2)

    print(f"[done] verdict={verdict}", flush=True)
    print(f"[done] verdict_msg={verdict_msg}", flush=True)
    print(f"[done] elapsed={elapsed:.1f}s metrics={out_path}", flush=True)
    return metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--self-test", action="store_true", dest="self_test")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    self_test()
    run(smoke=args.smoke)


if __name__ == "__main__":
    main()
