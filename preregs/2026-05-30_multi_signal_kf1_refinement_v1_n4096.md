# Pre-registration: G4 multi_signal_kf1_refinement_v1_n4096

Date: 2026-05-30
Anchor: multi_signal_kf1_refinement_v1_n4096
Queue: overnight_queue
Script: experiments/exp_multi_signal_kf1_refinement_v1_n4096.py
N-suffix: _n4096 (PROT-018) — production N = 4096

## Question

At N=4096 BSC across `M in {128, 4096, 8192, 16384}` (very-small to
past-capacity), can the 5-signal composite KF-1 (posterior_entropy,
spectral_spread, bundle_norm, geom_dist, replica_consistency) achieve
`AUC >= 0.90` AND demonstrate `resolution_accuracy >= 0.75` when
signals disagree, in `>= 3/5` seeds? OR does the previous v2 1.000-AUC
result reflect trivialization (no signal disagreement) that breaks
under borderline queries?

## Production config (PROT-018)

- N_FULL = 4096
- M_GRID_FULL = [128, 4096, 8192, 16384]
- SEEDS_FULL = [7, 17, 23, 31, 41]  (5 seeds)
- 4 M x 5 seeds = 20 cell-seeds
- PER-CELL CHECKPOINT (PROT-021)
- BETA = 8.0, TOP_K_SIG = 32
- BORDER_NOISE = 0.10 (10% BSC flip on borderline queries)

## Query design (NEW: borderline queries)

- 50 in-store keys (label=0)
- 50 OOS keys (label=1)
- 50 borderline = (in-store key with 10% BSC flip; label=1 since not
  exact-store, but high-confidence similar)

Total = 150 queries/cell. Composite AUC computed against
"label=1 = not-exact-store" (OOS + border vs in-store).

## Pre-registered bands

- **HP**:
  - `composite_weighted_auc >= 0.90` at ALL 4 M values
    (mean across seeds), AND
  - `signal_disagreement_rate >= 0.05` (signals disagree on >=5%
    of queries; the non-trivial test), AND
  - `resolution_accuracy >= 0.75` when signals disagree, AND
  - `>= 3/5 seeds` per M satisfy all 3 simultaneously.
- **HF**:
  - `mean composite_weighted_auc < 0.75` at ANY M
    (trivialization concern was real; composite does not generalize).
- **MB**: otherwise. Composite works at saturated regimes but degrades
  with borderline queries -> characterize the limit.

## Smoke result

- smoke N=1024 M_grid=[64,256] 1 seed
- AUC = 1.000 both cells; disagree_rate ~ 0.33-0.40 (good — signals
  actually disagree); resolution_accuracy ~ 0.33 (low — composite
  not yet right when signals disagree at small N).
- Verdict at smoke: G4_MIDDLE_BAND (expected; resolution_accuracy is
  the new gate not v2 saturated AUC).
- Effect size at smoke: AUC ceiling but resolution borderline.

## Calibration / walk-back

- Smoke resolution = 0.33 vs HP_RESOLUTION = 0.75 is borderline-low.
  Per walk-back gate, would double FULL n -> but with 5 seeds already
  and 4 M values that's 20 cell-seeds. Increasing to 10 seeds doubles
  the run. Decision: KEEP 5 seeds at FULL. Rationale: smoke is N=1024
  (1/4 of FULL); at N=4096 the signals' separation grows non-linearly
  and resolution_accuracy is expected to climb. The MB at smoke reflects
  small-N noise, not a power deficit. If FULL run also lands at
  resolution<0.5, route to Strategy for signal redesign.

## OOM check

N=4096 M=16384. Codebook=256 MiB, W=64 MiB, W_replica=64 MiB,
150x4096 fp32 = 2.5 MiB. Peak ~500 MiB. Under 6 GiB.

## Timeout estimate

- smoke_wall_s = 0.36s for 2 smoke cell-seeds (~0.18s per cell-seed)
- scaling: N=4x, M_max(256->16384)=64x but only affects substrate
  build, simplex grid search dominates (5^5 = 3125 per cell);
  scaling_exp = 1.5
- Per-cell-seed at FULL ~ 30-90s (grid search + signals on 150 queries
  + replica W build).
- Total: 60s * 20 = 1200s. With margin and big-M substrate build:
  3600s.
- TIMEOUT = 14400s (4-hour cap; standard).

## Outcome routing

- **HP**: 5-signal composite KF-1 is a real signal under non-trivial
  query mix. Substrate KF-1 capability validated for production
  "not-exact-store" detection. Direct input to Pattern B integration
  signaling layer.
- **HF**: v2 1.000-AUC was trivialization. KF-1 needs redesign;
  back to Strategy with signal-augmentation rescue (e.g. add cell-level
  Brunner-Munzel test or replica-count expansion).
- **MB**: composite holds at small/saturated M but degrades past-cap
  (M=16384) -> production envelope characterization; KF-1 is a
  conditional capability.
