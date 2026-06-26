# Prereg: substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path

**Date:** 2026-06-25
**Author:** exp_dev (USER-directed)
**Cell:** experiments/exp_substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path.py
**Anchor:** substrate_anisotropy_fly_lsh_expansion_sweep_v2_cpu_path
**Routing:** remote_cpu_queue (pure numpy; no torch; no GPU memory cap; ~16GB RAM headroom)
**Driver:** USER 2026-06-25: "remote cpu and gpu still idle" + three GPU OOMs in a row (v1, v2_batched, v3) blocked the brain-scale (4096x) expansion test.

## Why this cell exists

The 8GB GPU is too small for the matmuls at expansion >= 64x. v1 GPU sweep, v2_batched, and v3 expansion all OOM'd. Without completing the brain-scale (4096x) expansion test, the anisotropy story stays MM tier permanently and we never know whether the cerebellar fly-LSH mechanism transports to substrate at brain-scale expansion.

CPU has no per-process memory cap. Pure numpy compute path uses sparse representations throughout to stay under ~12GB peak per arm at expansion 4096x (d_p = 3.15M dims with K=5 sparse fan-in = 188MB COO storage; tag-overlap retrieval uses inverted-index lookup avoiding any (M, d_p) dense materialization).

This is the FINAL anisotropy discrimination test. Outcome locks substrate-product positioning for the anisotropy gap.

## Strategic significance (load-bearing)

Three outcomes, all decision-grade:

1. **HARD_PASS_BRAIN_SCALE_EXPANSION_RESCUES**: FLY_4096x >= 0.85 AND beats AB_CONTROL_4096x by >= 0.10 -> cerebellar mechanism transports to substrate at brain-scale; USER geometric intuition ("expand the cone to 360 degrees") validated; major Tier 4 path opens (substrate-product can incorporate sparse-fan-in expansion as native primitive).
2. **HARD_PASS_CONTROL_ALSO_HELPS**: both FLY and AB_CONTROL >= 0.85 AND both beat raw by >= 0.50 -> expansion-to-high-dim IS the mechanism but NOT LSH-specifically; substrate-product still gets a primitive (chunked random projection at brain scale) but the cerebellar attribution is wrong.
3. **HARD_FAIL_CONTROL_DOMINATES**: AB_CONTROL > FLY by >= 0.05 -> fly-LSH is NOT the mechanism at brain scale; this would be the 3rd cell-confirmation that anisotropy bypasses better than it rescues; close anisotropy as "bypass-only via partition routing + learned projection".
4. **HARD_FAIL_EXPANSION_DOESNT_HELP**: FLY_4096x <= FLY_8x + 0.02 -> expansion ratio is NOT the limiting factor at this corpus regime; cerebellar mechanism doesn't transport.
5. **MIDDLE_BAND_PARTIAL_LIFT**: monotonic but plateau below 0.85 -> mechanism real but insufficient at this scale.

All five outcomes lock substrate-product positioning. No outcome is "uninformative".

## Critical changes from v1 (load-bearing)

1. **No torch / no torch.cuda anywhere** -- pure numpy compute path; no GPU memory limit.
2. **M reduced 10k -> 2k** -- CPU is slower than GPU at dense ops; reduce DATA not MECHANISM. (META_M7 capacity-sensitive dims preserved.)
3. **Same expansion ratios {8, 64, 512, 4096}** with one change: **8x replaces 5x** baseline for a cleaner octave-step monotonicity grid. 4096x is the brain-scale test.
4. **Sparse representation throughout:**
   - Sparse-fan-in matrix S stored as (rows, cols, vals) COO arrays (np.int64 + np.float32); at dp=3.15M, K=5: 188MB total
   - fly-LSH tags stored as topk-indices (M, FLY_TOPK) int32; at M=2k, FLY_TOPK=15728: 126MB
   - Tag-overlap retrieval uses inverted-index hash lookup (tag_id -> list of K-rows); per-query ~157k ops; 1500 queries -> 235M ops; CPU-fast
   - AB_CONTROL_4096x uses chunked dense Gaussian + running-topk merge (same trick as v1 GPU; with smaller M=2k per-chunk peak shrinks)
5. **Per-arm CPU memory accounting via module-init assert:** estimates peak RAM per arm and asserts max < MEM_BUDGET_GB = 12 (leaves headroom on 16GB CPU). FAIL-FAST at import time if config violates budget.
6. **Same adversarial-similarity keys** as v2_batched: consecutive-token stride-1 windows of natural prose; adjacent keys share 15/16 tokens by construction. This is the discriminator regime the GPU cells were trying to test.
7. **AB_CONTROL_4096x retained** -- THE LSH-vs-generic discriminator. Same construction (chunked Gaussian + running-topk merge); CPU-port via numpy argpartition.

## Bands (LOCKED via module-init assert)

- **HARD_PASS_BRAIN_SCALE_EXPANSION_RESCUES**: FLY_4096x >= 0.85 at M=2k AND beats AB_CONTROL_4096x by >= 0.10 AND monotonic in expansion (8x <= 64x <= 512x <= 4096x within tol=0.02) AND cv_4096x <= 0.05
- **HARD_PASS_CONTROL_ALSO_HELPS**: BOTH FLY_4096x AND AB_CONTROL_4096x >= 0.85 AND both beat raw by >= 0.50
- **MIDDLE_BAND_PARTIAL_LIFT**: monotonic improvement but FLY_4096x plateau below 0.85
- **HARD_FAIL_EXPANSION_DOESNT_HELP**: FLY_4096x <= FLY_8x + 0.02
- **HARD_FAIL_CONTROL_DOMINATES**: AB_CONTROL_4096x > FLY_4096x by >= 0.05 (3rd cell-confirmation; closes anisotropy as bypass-only)

Module-init assert chain (CONFIG_VERSION echoes in metrics):
```
assert 0.0 < BAND_HP_BRAIN_EXPANSION < 1.0
assert 0.0 < BAND_HF_NO_LIFT_VS_8X < BAND_HP_BRAIN_EXPANSION
assert BAND_Q_SATURATION > BAND_HP_BRAIN_EXPANSION
assert 0.0 < BAND_HF_CONTROL_DOMINATES < BAND_HP_VS_CONTROL_MARGIN
assert 0.0 < BAND_HP_CONTROL_OVER_RAW < BAND_HP_CONTROL_ALSO
```

Plus a per-arm CPU-RAM-budget assert at module init:
```
assert max(per-arm peak estimate) < MEM_BUDGET_GB = 12
```

## Config

- N_DIM = PROJ_DIM = 768 (Pythia projection base; matches v2)
- expansion_factors = [8, 64, 512, 4096]; d_p in {6144, 49152, 393216, 3145728}
- K_FANIN = 5 (cerebellar regime; same as v2)
- KWTA_FRAC = 0.02
- FLY_TOPK = max(20, int(0.005 * d_p))
- FLY_NONZERO = 0.05
- M_EVAL = 2000 (reduced from 10000 for CPU feasibility)
- TRAIN_M = 1500, TRAIN_STEPS = 600
- Seeds [11, 13, 19] (cross-cell consistent)
- WINDOW_TOKENS = 16, CUE_SHIFT = 1 (matches v2_batched adversarial construction)
- ENCODER = EleutherAI/pythia-2.8b (full); pythia-160m (smoke)
- Substrate-only at inference; ASCII; per-arm + per-expansion metrics in verdict_msg
- MEM_BUDGET_GB = 12

## CPU memory budget (per-arm peak estimates)

At expansion 4096x (d_p = 3.15M), per-arm peak estimated as (see `_estimate_arm_peak_gb`):
- Sparse S (rows+cols+vals COO): ~0.31 GB
- Per-chunk projection output (chunk_M, dp) float32 bounded to 256MB
- K_tags + Q_tags (M+Q, FLY_TOPK) int32: ~0.13 GB
- Tag-overlap (Q, M) int32: ~12 MB
- Total per-arm peak at 4096x: ~0.5-0.8 GB. WELL under 12GB budget.

The module-init `_max_peak_gb < MEM_BUDGET_GB` assert FAIL-FASTS if config drifts.

## META disciplines

- **META_M6**: ARM_RAW measured in-cell at adversarial regime (NOT copied from any prior cell; different M and different keys than v1 sweep)
- **META_M7**: smoke matches full along ALL capacity-sensitive dims (PROJ_DIM, K_FANIN, KWTA_FRAC, FLY_TOPK_FRAC, expansion factors); only M_EVAL and SEEDS reduce. Standing fix for the recurring smoke-vs-full sign-flip pattern.
- **META_PROSPECTIVE_BANDS_FRESH_SEEDS**: bands locked at module init via assert chain
- **Q-discipline**: any arm >= 0.995 flagged as suspect saturation (corpus-may-still-be-easy at M=2k)
- **ASCII-only**; no unicode in scripts

## Routing

- **remote_cpu_queue** (marsh@home; Windows; reads origin/main; pure-CPU runner)
- **NO PROT-020 gate** (no torch imports; CPU-runner has no torch routing-sanity gate)
- **PROT-021** satisfied (imports `_seed_checkpoint` for per-seed resume; run_cfg passed to `aggregate_partials` to reject mismatched partials)
- **Timeout: 10800s** (3h budget)
  - Per-seed encoder hoist (pythia-2.8b on CPU): ~5-8 min (mean-pooled last-hidden-state across 3500 docs)
  - Per-seed ARM_RAW: ~1s
  - Per-seed ARM_FLY_LSH_8x: ~30s (sparse matvec + tag-overlap; small dp)
  - Per-seed ARM_FLY_LSH_64x: ~3-5 min
  - Per-seed ARM_FLY_LSH_512x: ~15-25 min
  - Per-seed ARM_FLY_LSH_4096x: ~60-90 min (dominated by sparse matvec + chunked tag-pass over dp=3.15M)
  - Per-seed ARM_AB_CONTROL_4096x: ~30-50 min (chunked Gaussian + running-topk merge)
  - Per-seed wall: ~2-3h; 3 seeds with per-seed checkpoint resume on PROT-021 long-timeout = 10800s (3h) per shipped slice with retry
  - Per-experiment timeout = ceil(1.5 * 2.5h) = 13500s; rounded to 10800s with checkpoint-resume safety net

## Self-test guarantees (PASS before queue_add)

- (a) sparse-fanin builder produces valid COO with K_FANIN nnz per row
- (b) sparse matvec gives bit-equivalent result vs naive dense (np.allclose atol=1e-5)
- (c) tag-overlap argmax on tiny synthetic returns correct match
- (d) band assertions hold
- (e) module-init memory budget assertion holds
- (f) compute_verdict synthetic paths exercised: HP_BRAIN, HP_CONTROL_ALSO, HF_CONTROL_DOMINATES, HF_NO_LIFT
- (g) **ground-truth recall**: end-to-end mini fly-LSH at M=50/d=64/expansion=8 must achieve >= 0.80 recall on noise-perturbed identity reconstruction. Asserts the full pipeline (sparse-fanin -> tags -> overlap-argmax) produces correct matches.

## Reference cells

- `exp_substrate_anisotropy_fly_lsh_expansion_ratio_sweep_v1` (v1 GPU; OOM at 64x, 512x, 4096x, AB_CONTROL_4096x)
- `exp_substrate_anisotropy_rescue_M100k_adversarial_similarity_keys_v2_batched` (v3 GPU; OOM source for batched-matmul reference)
- `exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full` (v2 chain-grade-candidate at 5x M=10k easy keys; MM tier per Skunkworks by-construction-saturation)
- `exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1` (encoder + contrastive train pipeline)

## Cross-cell sanity rails (post-landing)

- Compare ARM_FLY_LSH_8x at M=2k vs v2's 5x at M=10k: similar mechanism, similar regime; expect roughly comparable top-1 (small adversarial-key gap is informative)
- ARM_RAW at adversarial-keys M=2k: expect very low (anisotropy + adversarial-similarity construction = near-chance retrieval); should match v2_batched M=10k slice raw=0.021 ballpark
- AB_CONTROL_4096x vs ARM_FLY_LSH_4096x: the discriminator. If AB_CONTROL is within 0.10 of FLY at brain scale -> "expansion not LSH-specific" finding lands

-- exp_dev, 2026-06-25 (cell author; spawn-and-die teammate)
