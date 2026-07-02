# Pre-registration: stage2_learned_encoder_vs_random_init_v2_incremental_checkpoint_n4096

**Date:** 2026-07-01
**Anchor:** stage2_learned_encoder_vs_random_init_v2_incremental_checkpoint_n4096_seed_{7,13,19}
**Queue:** overnight_queue (GPU)
**N:** 4096, **Seeds:** [7, 13, 19], **M:** {4000, 8000, 12000}, **Noise:** {0.0}
**Timeout:** 14400s (4h) per seed per USER course-correction

## Delta vs v1

v1 (commit 48737275) timed out at 7200s on remote seed_7. v2 fixes:

1. **FIX 1 - per-arm incremental metrics.json checkpoint.** After EACH arm
   completes, atomically write metrics.json with `verdict=SALVAGE_PARTIAL`
   until all arms done + append record to `_arm_results.jsonl`. Timeout kill
   preserves all completed arms rather than losing everything. Pattern copied
   from `_stage2_commercial_M_latency_percentiles_v2_timeout_fixed_core.py`.

2. **FIX 2 - reduced grid.** 2 arms x 3 M x 1 noise = 6 units/seed (down
   from v1's 16). Dropped M=16000 (near-floor extreme; not needed for
   discriminator — cos05-wall is at M=12000). Dropped noise=0.30 (not the
   load-bearing question per Director).

3. **FIX 3 - SGD steps 500 -> 200.** Smoke at 100 steps showed 0.086 -> 0.082
   max_cos_key convergence (nearly flat by step 100); doubling to 200 gives
   2x margin for further reduction without 5x cost of 500.

4. **FIX 4 - timeout 14400s.** SGD contrastive + capacity sweeps at N=4096
   was more expensive than v1 estimated; 4h cap with salvage-partial safety
   net.

## Scientific question

Unchanged from v1. Does the substrate benefit from LEARNED
(gradient-optimized-pre-write, encoder-only) key encoding vs the random-init
bipolar keys used in all prior substrate work? First substrate empirical test
of trainable-pre-write encoding at Stage 2/3 boundary.

## Cell files

- Core: `experiments/_stage2_learned_encoder_vs_random_init_v2_incremental_checkpoint_core.py`
- Seed 7:  `experiments/exp_stage2_learned_encoder_vs_random_init_v2_incremental_checkpoint_seed_7.py`
- Seed 13: `experiments/exp_stage2_learned_encoder_vs_random_init_v2_incremental_checkpoint_seed_13.py`
- Seed 19: `experiments/exp_stage2_learned_encoder_vs_random_init_v2_incremental_checkpoint_seed_19.py`

## Design summary (unchanged from v1)

- ARM_RANDOM_INIT: bipolar iid keys
- ARM_LEARNED_CONTRASTIVE: init bipolar, 200 SGD steps of contrastive loss
  on encoder outputs only. neg = sum_{i<j} relu(cos(k_i,k_j) - 0.05),
  LR=0.02, LAMBDA_POS=0.5, aug_flip=0.01, MARGIN=0.05
- Substrate write: Hebbian W = O^T K / N
- Query: bipolar-flip noise on K, read Pred = W @ Kq^T, cosine score
- Metrics: top1, top5, top10, top50, cos05, cos08

**Discriminator metric = cos05 at M=12000** (RANDOM MEASURED@ probe: 0.661;
LEARNED with reduced max_pairwise_cos should preserve more cos05).

## Prior work check (unchanged from v1)

R21_cross_modal_binding C.4 declined naive-CLIP-on-substrate at P=5%;
this cell probes the subtly-different pre-write orthogonalization path.
Cell is NOT rediscovery.

## Pre-registered bands

**HARD-PASS (any ONE fires HP):**
- HP_LEARNED_HIGHER_CAPACITY: at (M=12000, f=0.0),
  (LEARNED_cos05 - RANDOM_cos05) >= 0.10
- HP_ORTHOGONALITY: LEARNED max_pairwise_cos <= 0.20 across ALL sweep points

**MIDDLE:** HP-partial in full-mode + no HF firing.

**HARD-FAIL:**
- HF_LEARNED_WORSE: LEARNED < RANDOM on >= 4 of 6 metric-gate comparisons
  (scaled to grid: 4/6 * 18 = 12 in FULL)
- HF_LEARNED_EQUIVALENT: |LEARNED - RANDOM| < 0.03 on ALL 18 gates

**Structural HF (unchanged):** cardinality / hash-collision / cv-breach /
baseline-out-of-band.

**Novel v2 verdict class:**
- SALVAGE_PARTIAL: incremental checkpoint captured N < 6 arms at wall time;
  downstream VET-owner reads `_arm_results.jsonl` for partial data.

## Cardinality

- `EXPECTED_N_UNITS_PER_SEED = 6` (arms=2 x M=3 x noise=1)
- Incremental checkpoint sets `n_arms_complete` on each arm; final verdict
  requires cardinality_ok (6/6).

## Smoke evidence (v2)

MEASURED@ `data/exp_stage2_learned_encoder_vs_random_init_v2_incremental_checkpoint_smoke_seed_7/metrics.json`:
- verdict: MIDDLE_BAND_ARMS_INDISTINGUISHABLE (expected below-wall M=4000)
- cardinality_ok: TRUE (2/2 units smoke)
- hp_orthogonality: TRUE (LEARNED max_cos 0.082 <= 0.20)
- hashes_distinct: TRUE (2/2 mechanism hashes)
- checkpoint_kind: `final_complete` (previously wrote 1 partial after RANDOM,
  1 final after LEARNED)
- `_start_marker.json` present
- `_arm_results.jsonl` has 2 rows (one per arm)
- Wall: 163s CPU (RANDOM 1.7s; LEARNED 159s for 100 SGD steps at M=4000)

## Timeout estimate (v2)

- Smoke wall MEASURED@ = 163s CPU (2 arms, M=4000, 100 steps).
- Full = 6 arms/seed; dominant cost = LEARNED at M=12000 with 200 SGD steps.
  Cost scales O(M^2 * n_steps): (12000/4000)^2 * (200/100) = 9 * 2 = 18x
  per LEARNED arm at M=12000 vs smoke LEARNED.
  Total LEARNED cost: 3 M-points x scaling factors:
    M=4000 x 2x steps = 2x smoke cost = 320s CPU
    M=8000 x 2x steps = 8x smoke cost = 1280s CPU
    M=12000 x 2x steps = 18x smoke cost = 2880s CPU
    Sum LEARNED: ~4480s CPU
  RANDOM arms: ~5s total (negligible).
  Total CPU: ~4485s.
  GPU speedup ~5x -> ~900s wall.
  With safety 3x for GPU-utilization variance: 2700s wall.
  USER cap 14400s provides 5x safety margin over GPU estimate.
- timeout_s = 14400 per USER course-correction.

## Ship route

- SMOKE: local CPU done at N=4096, M=4000, seed_7; MIDDLE_BAND_ARMS_INDISTINGUISHABLE
  (expected below-wall).
- FULL: overnight_queue (GPU) per USER; `import torch` at top; incremental
  checkpoint = salvage-partial even if timeout hits.
- Requires Orchestrator push (harness-DENIED to exp_dev).

## REQUIRED_FIELDS in metrics.json

Same as v1 plus:
- `checkpoint_kind`: "per_arm_incremental" | "final_complete"
- `n_arms_complete`: int (partial writes only)
- `per_arm`: list of arm records (partial writes) or `per_seed[0].per_unit`
  (final)
- Sidecar files (audit trail):
  - `_start_marker.json`: pid + ts + expected_n_units at cell start
  - `_arm_results.jsonl`: one JSON line per completed arm
