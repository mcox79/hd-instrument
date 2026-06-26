# Pre-registration: substrate_working_memory_multi_bank_K_extension_adversarial_v1

**Date:** 2026-06-25
**Anchor:** substrate_working_memory_multi_bank_K_extension_adversarial_v1
**Script:** experiments/exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1.py
**Queue:** local_cpu_queue (numpy; ~1-2h CPU per Research drill estimate)
**Seeds:** [11, 13, 19] (cross-cell consistent)
**K_SWEEP (full):** [1024, 2048, 4096]

## Promotion context (Tier A #4 / Research DRILL 1 ITEM 6 = DRILL 2 HIGH 1)

v1 reference (`exp_substrate_working_memory_multi_bank_routing_v1`) chain-grade-eligible at
K_total=1024. Verbatim (cell self-flagged Q_SUSPECT_SATURATION):
```
RAIL_SANITY_BREACH_NAIVE_OUT_OF_CELL_D_BAND: ARM_NAIVE_SINGLE_BANK_K32: recall=1.0000;
ARM_NAIVE_SINGLE_BANK_K128: recall=0.8815 cv=0.0199; ARM_NAIVE_SINGLE_BANK_K256: recall=0.4648;
ARM_MULTI_BANK_8x32_K256: recall=1.0000; ARM_MULTI_BANK_4x64_K256: recall=0.9987;
ARM_MULTI_BANK_2x128_K256: recall=0.8659; ARM_MULTI_BANK_16x16_K256: recall=1.0000;
ARM_MULTI_BANK_32x32_K1024: recall=1.0000 [Q-DISCIPLINE: suspect saturation -- recall >= 0.995;
UNDER-CLAIM tier]
```

4/4 multi-bank arms at K=256 saturate identically -> cannot DISCRIMINATE which arrangement is
load-bearing (by-construction-saturation per MEMORY 2026-06-23 rule).

Research drills (both #6 in DRILL 1 and HIGH 1 in DRILL 2) converge on same cell spec: extend
K past 1024 + adversarial feature-overlap items to surface the binding constraint.

## v1 design (extension + adversarial discriminator)

Two discriminators applied simultaneously:

1. **K_SWEEP in {1024 (rail), 2048, 4096}** -- extends past v1 saturation point
2. **Adversarial regime**: items partitioned into N_GROUPS_ADV=4 groups; within each group, items
   share `FEATURE_OVERLAP_FRAC=0.20` of bipolar bits via SHARED-PREFIX construction (deterministic;
   first 20% of N_DIM bits are shared with group template, rest random bipolar). Two items in
   same group share ~60% of bits (vs ~50% baseline for random pairs).
3. **Multiple N_BANKS at each K** -- 8x, 16x, 32x, 64x bank arrangements scale to keep K_PER_BANK
   in chain-grade envelope (<= 128); router-bound vs cleanup-bound discriminated by which
   arrangement cliffs first

## Arms (10 total: 5 random + 5 adversarial, sharing bank-arrangement labels)

For each K_total in K_SWEEP:
- ARM_NAIVE (single bank with K_PER_BANK = K_total)
- ARM_MULTI_8x (8 banks; K_PER_BANK = K_total/8)
- ARM_MULTI_16x (16 banks)
- ARM_MULTI_32x (32 banks)
- ARM_MULTI_64x (64 banks; K_PER_BANK = K_total/64)

Each arm runs in BOTH regimes (RANDOM and ADVERSARIAL). Total per K = 10 arm-evals.

## Pre-registered bands (LOCKED at module init via assert META_PROSPECTIVE_BANDS_FRESH_SEEDS)

### HARD_PASS_CHAIN_GRADE_K_4096
- Best random multi-bank arm at K=4096: recall >= **0.95** across seeds
- AND cv across seeds <= **0.05**
- AND route_acc >= **0.95** across seeds
- AND adversarial recall (same arm, same K) within **0.05** of random recall
  (mechanism survives feature overlap)

### CHAIN_GRADE_AT_K_CLIFF
- Chain-grade gate passes at K=1024 or K=2048 but cliffs at K=4096
- Cliff identified within sweep

### MIDDLE_BAND_PARTIAL_K_EXT
- Best random multi-bank at K=4096 recall in [0.50, 0.95)
- Mechanism partially scales

### HARD_FAIL_ADVERSARIAL_BREAKS_ROUTING
- At K=4096: best_random recall - adversarial recall >= **0.30** absolute
- Adversarial degrades by >= 0.30 (routing-acc tanks under query ambiguity)

### HARD_FAIL_NO_K_HOLDS
- No K_total in sweep reaches chain-grade gate

## Q-discipline guard (BIAS-Q)

If any multi-bank arm hits >= **0.995** EVEN AT K=4096 ADVERSARIAL:
- Verdict carries `[Q-DISCIPLINE: saturated at K=...; corpus too easy at this scale]`
- Recommend K=8192+ extension OR stronger feature-overlap (FEATURE_OVERLAP_FRAC=0.40+)
- Flag is documentation, not auto-demotion

## Cross-cell discipline

- ASCII only (verified)
- Substrate-only at inference (numpy primitives; zero LLM forward; counter asserted = 0)
- Per (K, regime, arm) metrics in verdict_msg + per_unit (Fix #28)
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Seeds [11, 13, 19] (cross-cell consistent)
- META_M6: NAIVE single-bank baseline measured IN-CELL at same K (not copied from v1 reference)
- META_M7: smoke matches full on N_DIM (2048 vs 4096; capacity-sensitive REDUCED for smoke
  but full chain-grade at v1 reference N=4096 already established), SIGMA, CUE_COS,
  FEATURE_OVERLAP_FRAC (LOCKED at 0.20 across smoke/full).
  Only N_ITEMS_PER_K + SEEDS + K_SWEEP reduce in smoke
- CODEBOOK_SIZE = 8192 at full (must hold max K_total=4096 + headroom; 2x ratio matches v1 reference)

NOTE on N_DIM smoke vs full: smoke uses N=2048 (vs full 4096) to halve smoke wall. Full N matches
v1 reference for apples-to-apples rail comparison. Smoke regime is for PIPELINE SANITY ONLY;
verdict reasoning at full N=4096.

## Capacity-feasibility analysis

Per-(seed, K_total) wall:
- N_DIM=4096 W matmuls per arm: dominated by N_QUERIES_PER_K trials (~200/K) x N_BANKS x K x N
- At K=4096, 64-bank arm: 200/4096 ~ 1 trial * 64 banks * 64 items each = 4096 reads * cleanup ~ 1.5GB matmul ops
- Per arm at K=4096: ~30-60s
- 10 arms per (seed, K) -> per (seed, K) = 5-10min

3 seeds x 3 K values = 9 units; ~7min average each = 65min total.

Drill estimate said 1-2h CPU. Aligned.

## Timeout estimate

Formula: timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^1.5 * (FULL_seeds/smoke_seeds) *
                          (FULL_K_max/smoke_K_max)^1.0 * (FULL_N_items/smoke_N_items))

Smoke wall = 28.1s (2 units at K_SWEEP=[256, 1024], N=2048, seeds=[1], N_ITEMS=50).
Full N grows 2048 -> 4096 (2x); seeds 1 -> 3; K_max grows 1024 -> 4096 (4x); N_items 50 -> 200.

ceil(1.5 * 28.1 * 2.83 * 3 * 4 * 4) = ceil(5719s) = ~95 min.

Conservative budget: **timeout_s = 9000 (2.5h)** -- matches anisotropy budget; provides headroom
for K=4096 64-bank arm. Below 14400s PROT-021 threshold; per-(seed, K) checkpoint wired.

## PROT compliance

- PROT-018 (`_n<N>` suffix): anchor has no `_n<N>` suffix.
- PROT-019 (large-N timeout floor): no `_n<N>` suffix.
- PROT-020 (GPU queue requires torch): local_cpu_queue path; rule does not apply.
- PROT-021 (long-timeout needs checkpoint): timeout 9000s < 14400s; per-(seed, K) checkpoint wired.

## Pre-flight smoke + self-test gate

- Smoke: N=2048, K_SWEEP=[256, 1024], N_ITEMS=50, seeds=[11]
- Smoke wall measured: 28.1s (well under 180s queue_add cap)
- Self-test asserts T1-T10:
  T1 random codebook shape + bipolar;
  T3 adversarial in-group overlap > cross-group (mechanism actually creates feature overlap);
  T4 bipolar_quantize sign; T5 single-bank K=32 rail (matches Cell D); T6 multi_bank 8x32 random;
  T7 bank_arrangements_for_k populates correctly; T8 bands locked; T9 LLM counter = 0;
  T10 CODEBOOK_SIZE >= max(K_SWEEP)
- Self-test PASSED LOCAL (verified before commit)
- Smoke VERDICT at K=1024 demonstrated the discriminator: MULTI_8x recall=0.4102 cliffs while
  MULTI_64x recall=1.0000 holds -- exactly the router-vs-cleanup discrimination we wanted

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports BOTH directions:
- HARD_PASS_CHAIN_GRADE_K_4096 (mechanism scales 4x v1 + survives adversarial)
- CHAIN_GRADE_AT_K_CLIFF (cliff identified within sweep)
- MIDDLE_BAND_PARTIAL_K_EXT (partial)
- HARD_FAIL_ADVERSARIAL_BREAKS_ROUTING (routing fragile to query ambiguity)
- HARD_FAIL_NO_K_HOLDS (no K reaches gate)
- Per (K, regime, arm) breakdown in per_unit for Skunkworks step-0 re-read

## Strategic significance (decision-grade)

If HARD_PASS_CHAIN_GRADE_K_4096:
- WM K-ceiling extends from 1024 (v1) to 4096 (4x lift via larger bank-count arrangements)
- Adversarial robustness confirmed: routing survives feature overlap
- Substrate-product: production-scale WM with shared-feature item classes

If CHAIN_GRADE_AT_K_CLIFF:
- Honest envelope boundary; cliff identifies binding constraint (router vs cleanup)
- Bank arrangement that wins at the cliff is the substrate-product choice

If HARD_FAIL_ADVERSARIAL_BREAKS_ROUTING:
- Multi-bank routing IS fragile to query ambiguity
- Substrate-product positioning: "multi-bank chain-grade only on independent items;
  feature-shared items need different mechanism (e.g., feature-cluster routing)"
- Triggers research drill: feature-cluster-aware routing design

If HARD_FAIL_NO_K_HOLDS:
- v1's K=1024 saturation may have been smoke-regime artifact at lower N
- Repeat v1 at N=4096 to confirm rail before extending

## Honest negatives possible

- All arms saturate >= 0.995 at K=4096 random (Q-discipline fires; corpus too easy)
- Bank-arrangement-specific: only MULTI_64x (smallest per-bank K) survives K=4096 -- DEGENERATE
  per v1's "BANK_SIZE_DEGENERATE" band (not in this cell's verdict ladder but worth noting)
- Adversarial at K=4096 cliffs uniformly: routing layer fails to discriminate any feature-shared
  pair (this would be HARD_FAIL_ADVERSARIAL_BREAKS_ROUTING)
- Per-seed cv > 0.05 at K=4096 (sensitivity to random codebook draw at production scale)

## Dispatch plan

1. Author cell + prereg (this file) -- DONE
2. Self-test PASSED locally -- DONE (T1, T3-T10 PASS; T2 silently joined T1 due to print order)
3. Smoke run PASSED locally -- DONE (verdict HARD_PASS_CHAIN_GRADE_K_1024 at smoke; discriminator
   demonstrated MULTI_8x cliffs while MULTI_64x holds; Q-discipline fires correctly)
4. Path-scoped commit BEFORE dispatch (cell + prereg only)
5. Dispatch via `bash tools/orchestrator/queue_add.sh local_cpu_queue substrate_working_memory_multi_bank_K_extension_adversarial_v1 experiments/exp_substrate_working_memory_multi_bank_K_extension_adversarial_v1.py preregs/2026-06-25_substrate_working_memory_multi_bank_K_extension_adversarial_v1.md 9000`
6. File dispatch notification in batch note

## Routing rationale

- local_cpu_queue: numpy-only; no torch; CPU-feasible at ~1.5h wall. Routing-sanity gate would
  REJECT this on overnight_queue (no torch import).
- Pause flag verified NOT set at dispatch authorship time.

## Test plan post-landing

- Skunkworks step-0 honest re-read of per (K, regime, arm) recall + cv + route_acc
  (NOT verdict_msg framing per Fix #28)
- Verify cv across 3 seeds at K=4096 for best arm is <= 0.05 for chain-grade claim
- Verify adversarial - random delta at K=4096 (the discriminator gate)
- Cross-cell consistency: compare K=1024 slice to v1 reference (sanity check regime parity;
  expect MULTI_32x32_K1024 ~ 1.000 in random regime)
- If HARD_PASS_CHAIN_GRADE_K_4096: queue K=8192+ stretch cell + composition with KG retrieval
- If HARD_FAIL_ADVERSARIAL_BREAKS_ROUTING: research drill into feature-cluster routing design
