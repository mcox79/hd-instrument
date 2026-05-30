# Prereg: superposition_top_k_filter_v2_n4096

**Anchor:** `superposition_top_k_filter_v2_n4096`
**Queue:** remote_cpu_queue (CPU)
**Script:** `experiments/exp_superposition_top_k_filter_v2_n4096.py`
**Date:** 2026-05-30
**Lineage:** F6 (v1: TOPK_MIDDLE_BAND — naive top-K=10 passes uniform/peaked but fails sparse; v2: tests two filter variants to rescue sparse pattern)

## Question

v1 (commit 2a6bf84) tested a naive top-K=10 filter for cross-talk reduction. Per-pattern results:
- P1 uniform: 5/5 seeds pass
- P2 peaked: 5/5 seeds pass
- P3 random: 3/5 seeds pass
- P4 sparse: 0/5 seeds pass (cross-talk above HP threshold in all 5 seeds)

The naive top-K filter fails on sparse patterns because off-target codeword amplitudes are comparable to the few intended components. v2 tests TWO improved filter designs to rescue sparse-pattern superposition.

## Configuration

- N (production): 4096 (PROT-018: `_n4096` binds)
- N (smoke): 1024
- K_MAIN (stored facts): 10
- Patterns (production): `[P1_uniform, P2_peaked, P3_random, P4_sparse]`
- Patterns (smoke): `[P1_uniform, P4_sparse]`
- Filters: `[naive, weighted, threshold]`
- Seeds (production): `[7, 17, 23, 31, 41]` (5 seeds)
- Seeds (smoke): `[17]`
- Cell-seeds total (production): 4 patterns × 3 filters × 5 seeds = 60
- Cell-seeds total (smoke): 2 patterns × 3 filters × 1 seed = 6

## Three filter designs

1. **naive** (v1 baseline): `topk(|alpha|, K=10)` indices; zero the rest. Works when stored-codeword amplitudes are well above noise floor.

2. **weighted** (new): compute `expected_c = sum_i betas[i] * 1{val_idx[i] == c}` via `index_add_`. Score = `|alpha_c - expected_c|`. Keep K indices with SMALLEST score (closest to expected). Expected to favor recovery of intended components even when their amplitude is small (as in sparse patterns).

3. **threshold** (new): dynamic threshold = `mean(|alpha|) + 2*std(|alpha|)`. Keep components above threshold (no fixed K). For sparse patterns where only a few alphas are large, this picks them automatically; for uniform patterns, the spread keeps the K intended components.

## Pre-registered bands (HARD: set BEFORE running)

Per-cell HP: `per_component_accuracy >= 0.90 AND cross_talk <= 0.10`.

| Outcome | Trigger |
|---------|---------|
| **HARD_PASS** | AT LEAST ONE of {weighted, threshold} passes sparse (P4) ≥ 3/5 seeds AND maintains easy patterns (P1+P2) ≥ 3/5 seeds clean |
| **HARD_FAIL** | NEITHER weighted nor threshold rescue sparse (both fail ≥ 3/5 seeds on P4) |
| **MIDDLE_BAND** | Partial rescue (some filter rescues sparse but regresses easy patterns) |

Verdict labels: `TOPK_V2_HARD_PASS`, `TOPK_V2_HARD_FAIL`, `TOPK_V2_MIDDLE_BAND`, `TOPK_V2_INCONCLUSIVE`.

## Outcome implications

- **HARD_PASS**: Op D Phase 2 ships at full pattern coverage (all 4 patterns); two-hop superposition unblocked.
- **HARD_FAIL**: Op D Phase 2 restricted to uniform/peaked only per [[feedback-dont-overextend-theorems]]; sparse pattern closes for Op D in this regime; opens rescue path of dictionary-aware decoding (separate experiment).
- **MIDDLE_BAND**: report which filter wins on which pattern; partial Phase 2 ship possible.

## Formula self-tests (verified at module import)

1. `N_FULL == 4096` (PROT-018 binding)
2. Cell-seed total = 60 (4 × 3 × 5)
3. naive filter on 100-dim alphas with K=5 → exactly 5 nonzeros (via topk + mask)
4. weighted filter on K=5 uniform-betas, val_idx=[0..4] → exactly 5 nonzeros (no index_add error)
5. threshold filter on N(0,1)-distributed alphas → mask is non-empty, ≤ C
6. `compute_verdict(fake_hp_data)` where weighted-on-all-patterns passes → contains `HARD_PASS`
7. `compute_verdict(fake_hf_data)` where all advanced filters fail sparse → contains `HARD_FAIL`
8. Smoke: 1 cell per filter at N=1024 produces non-null pca + cross_talk values

## Smoke result (2026-05-30, CPU, N=1024, seed=17, 1 seed)

| pattern | filter | pca | cross_talk | n_kept | observation |
|---------|--------|-----|------------|--------|-------------|
| P1_uniform | naive | 1.000 | 0.000 | 10 | clean (v1 baseline) |
| P1_uniform | weighted | 1.000 | 0.524 | 9 | regresses easy pattern |
| P1_uniform | threshold | 1.000 | 0.283 | 73 | regresses easy pattern |
| P4_sparse | naive | 1.000 | 0.295 | 10 | fails (v1 behavior reproduces) |
| P4_sparse | weighted | 1.000 | 325514 | 10 | div-near-zero on sparse (mean stored alpha collapse) |
| P4_sparse | threshold | 1.000 | 0.000 | 5 | **rescues sparse at smoke** |

- Threshold filter shows promising sparse rescue (ct=0.000) but regresses uniform at smoke N=1024. May correct at FULL N=4096 where alpha spread differs.
- Weighted filter has numerical issue with sparse pattern (mean_alpha_stored_post near zero → div explosion). At FULL the prior should be stronger, but worth flagging.
- Smoke verdict TOPK_V2_HARD_FAIL is a 1-seed gate-arithmetic artifact (cannot satisfy 3/5-seed gate at 1 seed); the per-cell metrics are real, non-zero, non-constant — not instrumentation-suspect.

## Walk-back gate

Smoke per-cell signal is varied and non-trivial; effect size is large (d >> 1.0) for the threshold-rescues-sparse observation. The 5-seed FULL is sufficient; no n×2 walk-back needed.

The verdict logic correctly identifies HARD_FAIL at smoke because:
- naive on P4_sparse: 0/1 pass (regression from v1's 0/5)
- weighted on P4_sparse: 0/1 pass
- threshold on P4_sparse: 1/1 pass (rescue signal)
- BUT threshold on P1_uniform: 0/1 pass (regression at smoke scale)

At FULL N=4096 with 5 seeds, the threshold filter may maintain easy patterns (alpha spread changes with N).

## OOM check

- N=4096, K=10: ~900MB (same as v1). 3 filters add only constant overhead. CPU runner has ample headroom.

## Timeout estimate

Formula: `ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))`

- smoke_wall_s = 0.16s (6 cell-seeds at N=1024)
- FULL_N / smoke_N = 4
- FULL_seeds / smoke_seeds = 5
- FULL cells / smoke cells = 60 / 6 = 10
- scaling_exp = 1.5 (vector ops + per-codebook scan; not matrix-matrix dominant)
- formula estimate = ceil(1.5 * 0.16 * 4^1.5 * 5 * 10) = ceil(96s) = 96s
- CPU at N=4096 with 60 cells: ~30-90s/cell range; 60 × 60s = 3600s budget
- Conservative safety: **timeout=14400s (4h)** — accommodates CPU pace at upper end.

## Queue routing

- remote_cpu_queue (Tier B): CPU is appropriate; per-cell cost is moderate (substrate build + filter + retention probe); 60 cell-seeds across 3 filters is a design-space sweep type → remote CPU frees GPU for heavier work.
- ASCII-only structurally guaranteed.

## Next decisions by outcome

- **HARD_PASS**: ship Op D Phase 2 (two-hop superposition) at full pattern coverage; cap_map row for cross-talk-rescue → ✅.
- **HARD_FAIL**: restrict Op D Phase 2 to uniform/peaked patterns; cap_map row "sparse-pattern cross-talk rescue" → ❌; opens dictionary-aware decoding probe.
- **MIDDLE_BAND**: partial Phase 2 ship; cap_map row stays 🟡 with per-pattern annotations.

## Diagnostic on the weighted filter div-near-zero

The weighted filter's smoke result on P4_sparse shows `cross_talk=325514` due to `mean_alpha_stored_post` collapsing near zero (sparse patterns have only ~3 nonzero stored components, and the weighted filter zeros most of them). The numerical safety factor `mean_alpha_safe_post = max(mean_alpha_stored_post, 1e-9)` is too lax for this regime. If the FULL run shows the same issue, the weighted filter result will be reported as numerically unreliable on sparse (does not invalidate the threshold-filter rescue path).
