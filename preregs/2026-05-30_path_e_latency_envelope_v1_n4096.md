# Prereg: path_e_latency_envelope_v1_n4096

**Date:** 2026-05-30
**Anchor:** path_e_latency_envelope_v1_n4096
**Script:** experiments/exp_path_e_latency_envelope_v1_n4096.py
**Queue:** overnight_queue
**Timeout:** 21600s

## Why this anchor

Path E showed:
1. Sub-linear K-scaling (9.27x at K=1000 vs 12.49x for B/D) — unique latency
   advantage at production K.
2. Non-monotonic accuracy in depth (degrades at M=8192 d=3 but recovers at d=5).

Both properties make Path E a candidate for production use at high-K queries
IF accuracy survives across a wide envelope. This anchor maps the (depth, K, M)
envelope specifically for Path E to determine:
- where E maintains accuracy >= 0.70
- where E's sub-linear K-scaling realizes a practical latency advantage over B/D

## Sweep grid

- N = 4096 (PROT-018 _n4096 binding).
- Path E ONLY (B and D are well-characterized; E has unique non-monotone behavior).
- depth grid: {3, 5, 8, 12, 16, 20} (6 points)
- K_paths grid: {100, 500, 1000, 2000, 5000} (5 points)
- M grid: {512, 2048, 8192} (3 points)
- Seeds: {7, 17, 23, 31, 41}.
- Per-cell-seed checkpoint.
- Cells: 6 x 5 x 3 = 90 (depth, K, M) configs x 5 seeds = 450 cell-seeds.

## Metrics

Per (depth, K, M, seed):
- **accuracy** = fraction of positives whose coherence > median(decoy coherences).
- **latency_ms_E** = wall time per (decoy + positive) coherence computation
  scaled by K_paths.
- **latency_ms_BD_extrap** = wall time for one B-style forward pass scaled by K_paths.
- **advantage_ratio** = latency_BD / latency_E.

## Pre-registered bands

- **HARD_PASS (HP)** = Path E maintains accuracy >= 0.70 across >= 60% of
  (depth, K, M) cells (mean over seeds) AND advantage_ratio is monotone non-
  decreasing in K (per fixed (M, depth)) for >= 50% of (M, depth) cells.
- **HARD_FAIL (HF)** = Path E drops below 0.30 accuracy in > 50% of cells
  (mean over seeds). Mechanism brittle outside narrow envelope.
- **MIDDLE_BAND (MB)** = otherwise.

## Outcome plan

| Verdict | Action |
|---|---|
| HARD_PASS | E is production-viable AND has unique latency advantage at high K; ship Path E to Pattern B integration. |
| HARD_FAIL | E is too brittle for production; cap_map row updated to "narrow E envelope". |
| MIDDLE_BAND | E useful in identified envelope only; characterize boundary; deploy conditionally. |

## Closed-form self-tests in the script

- `compute_verdict(fake_hp)` -> HARD_PASS when accuracy >= 0.70 everywhere and
  advantage_ratio scales as 0.5*K (monotone in K).
- `compute_verdict(fake_hf)` -> HARD_FAIL when accuracy = 0.10 across all cells.
- 90-cell count assertion (6 x 5 x 3).

## Timeout estimate

smoke_wall_s = 0.4s (N=1024, M=512, 2 depths, 1 K, 1 seed).
FULL scaling: N 1024->4096 (16x for N^2); seeds 1->5 (5x); depth 2->6 (3x);
K 1->5 (5x); M 1->3 (3x).
Per-cell-seed at FULL ~= 0.4 * 16 / (6 * 5 * 3) = small; dominated by
candidate-coherence computation which scales with K_paths.
At K=5000: per-cell ~20-60s.
450 cell-seeds total. Average ~30s -> 13500s expected. User pre-spec'd 21600s.

**Timeout: 21600s** (per user spec).

## PROT-018 _n4096 binding

`N = 4096` is a module-level constant. Verified.

## Dependency check

- experiments/_metric_battery.py -- exists
- experiments/_relation_graph.py -- exists
- experiments/_seed_checkpoint.py -- exists
- No upstream data files required.
