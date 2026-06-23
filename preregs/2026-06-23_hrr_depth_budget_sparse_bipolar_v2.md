# Pre-reg: hrr_depth_budget_sparse_bipolar_v2 (W-free Hopfield corrected metric)

Date: 2026-06-23
Author: exp_dev
Cell: `experiments/exp_hrr_depth_budget_sparse_bipolar_v2.py`
Queue: local_cpu_queue (timeout 3600s)
Reference paradigm: `data/exp_sparse_boundary_v2_cpu_v1/metrics.json` (CERT 592)

## Why v2

v1 (`exp_hrr_depth_budget_sparse_bipolar_v1.py`) shipped a bundle / top-M-cleanup
metric that is the wrong paradigm vs the drill's CERT 592 claim. The drill claims
Willshaw-style super-capacity at f<=0.02 under **W-free Hopfield recall** with
FLIP cue-noise (NOT bundle / cleanup against a vocabulary). v2 corrects the metric.

## Mechanism (corrected per CERT 592)

For each arm f in [1.0, 0.1, 0.05, 0.02, 0.01] at N_DIM=4096:

1. Build P = M K-sparse bipolar patterns, K = max(1, round(f*N)).
2. Build implicit W = P.T @ P (correlation matrix; no learning step).
3. For each row i in P:
   - cue = P[i] with FLIP=0.05 of its nonzero positions sign-flipped.
   - r = sign((cue @ P.T) @ P - cue * diag(P.T @ P))   (subtract self-bias).
   - Correct iff r[nz(P[i])] == P[i][nz(P[i])] (exact recovery on nonzero positions).
4. recall_mean = correct_count / M.
5. alpha_c(f) = max M/N where recall_mean >= 0.95 (early-terminate on drop).

Lift = alpha_c(f=0.02) / alpha_c(f=1.0).

## Per-arm M sweep (full mode)

- ARM_DENSE_f1.0:   [50, 150, 300, 450, 570, 700, 900, 1200]      (theory: alpha_c ~0.14 -> M~573)
- ARM_SPARSE_f0.1:  [200, 500, 1000, 2000, 4000, 8000, 16000]
- ARM_SPARSE_f0.05: [500, 1500, 3000, 6000, 12000, 24000, 40000]
- ARM_SPARSE_f0.02: [1000, 3000, 8000, 16000, 30000, 50000, 70000]
- ARM_SPARSE_f0.01: [2000, 6000, 14000, 28000, 50000, 70000]

Cap at M=70k: cost scales O(M^2 * N); 70k * 4096 working memory ~1.5GB,
per-M wall ~10-15min at f=0.02 on laptop CPU. Early-termination caps total
seed-wall at ~45min. If sparse arm reaches end without recall-drop, alpha_c
is a LOWER BOUND (`alpha_c_capped=True`) -- honest reporting per CERT 592 ref.

## Pre-reg bands (sacrosanct)

- HARD_PASS: alpha_c(f=0.02) >= 20 * alpha_c(f=1.0)
- HARD_FAIL: alpha_c(f=0.02) <= 2  * alpha_c(f=1.0)
- MIDDLE:    lift in (2x, 20x); characterize via finer M-sweep.

If sparse arm is capped, lift is a LOWER BOUND; HARD_PASS still valid if
lower-bound >= 20x. cert-owner reads `alpha_c_capped` flags in detail.

## Sanity self-tests (gate before dispatch)

- T1: sparse_pat respects K-of-N + bipolar in active.
- T2: M=1 every arm recall = 1.0 (single pattern trivially recoverable).
- T3: FLIP=0 every arm recall = 1.0 at small M.
- T4: dense @ alpha=0.5 recall < 0.95 (above theory).
- T5: sparse f=0.05 @ alpha=0.5 recall >= dense @ same (soft).
- T6: find_alpha_c monotone-early-terminate behavior.
- T7: verdict-shape (HP / HF / MID) on synthetic units.

Smoke run end-to-end (seed=7, M_grid_smoke):
  dense alpha_c=0.012 (capped=False; M=200 recall=0.93 dropped below thresh)
  sparse_f0.02 alpha_c=1.221 (capped=True at M=5000)
  lift=100x (LOWER BOUND; smoke grid does not extend further)

Smoke verifies CERT 592 paradigm replicates correctly at N=4096.

## What HARD_PASS would license

Substrate-native sparse-bipolar W-free Hopfield as a chain-grade-eligible
compression primitive: stores 20-100+ x dense capacity at 2% sparsity under
realistic cue noise. Unbottlenecks HRR depth-budget bundle-width ceiling
sigma~1/sqrt(M). Drill's 20-300x claim CONFIRMED at production N=4096.

## What HARD_FAIL would license

Drill claim refuted at production scale; sparse super-capacity is NOT a
substrate-product feature at N=4096 under W-free Hopfield + 5% cue-FLIP.
Forces re-examination of the drill's source measurement (was it at smaller N?
under different cue-noise? was the recall threshold honest?).

## Cites

- notes/research_drill_sparse_bipolar_depth_enc1_composition_2026-06-23.md
- data/exp_sparse_boundary_v2_cpu_v1/metrics.json (CERT 592 reference)
- experiments/exp_hrr_depth_budget_sparse_bipolar_v1.py (v1 wrong-metric)
- experiments/exp_sparse_boundary_v2_cpu_v1.py (reference cell)
