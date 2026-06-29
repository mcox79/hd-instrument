# Prereg: substrate_task_vector_cosine_quality_v4

**Date:** 2026-06-29
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) v4 mechanism-class diversion
**Drill source:** v3 closed MM cleanly (1 HF / 2 MB; seed-instability persists
under precision-densification). v4 changes the MEASUREMENT FAMILY itself,
not the precision of v3's measurement.
**Stage:** Stage 3 (compositional understanding — substrate K-shot regime)
**P_deflated:** 0.40 (mechanism-class diversion to a continuous metric is
hypothesis-class novel for TASK_VECTOR ICL on this substrate; if the
discriminator still collapses, v4 confirms the substrate bound rather than
the instrument bound — that itself is a chain-grade-eligible negative)
**M3 milestone:** Concern #4 (online conversational learning).
**Independence:** New anchor `substrate_task_vector_cosine_quality_v4`. Not a
superseder of v3 — v3 measured "discrete K_cliff event"; v4 measures
"continuous task-vector cosine quality". Orthogonal lens on same phenomenon.

## CHANGES FROM v3 (TRUE mechanism-class diversion: METRIC FAMILY)

### v1/v2/v3 lever ancestry (all closed MM or HF; chain SATURATED at precision)

- v1: cliff-counting metric. MM (metric artifact)
- v2: monotonic-decay metric (metric refinement). 2/3 HP + 1 HF (regime_flip)
- v3: precision densification (n_queries 10->50 + pooled + bootstrap; SAME v2 metric). 0/3 HP (1 HF / 2 MB)

The K_cliff metric is fundamentally three coupled conditions:
1. Saturation reached at low K (TV >= 0.95)
2. Monotonic decay observed at higher K
3. No recovery above floor

Each condition is independently fragile at substrate scale. P(all three hold)
~= 0.4 per slice. With 9 slices, expected valid = 3-4. v3 found exactly that.
The cliff metric is structurally noise-dominated, not precision-rescuable.

### v4 lever: continuous task-vector COSINE quality (NOT top1 + cliff-detection)

Instead of measuring "did the unbound query return correct argmax over codebook"
(0/1 outcome per query; binary; subject to argmax noise on a continuous similarity
field), measure **how well the task vector representation captures the task itself**:

For each (K, V, overlap) phase point:
- Build the substrate TASK_VECTOR `tv = bundle(bind(x_i, perm(x_i)))` over K shots
- Build the GROUND-TRUTH (oracle) task vector `tv_oracle = bundle(bind(x_i, perm(x_i)))`
  over the FULL V_ENTS_POOL (all 200 entities). This is the "perfect" task
  representation given infinite shots.
- Measure: `cosine(tv, tv_oracle)` -- continuous in [-1, 1].

Properties:
- Continuous, single-valued, smooth in K
- Monotonic-non-increasing in K under expected behavior (more bundled noise)
- Measures HOW WELL the TV PROBES the task, independent of cleanup-step noise
- No saturation cliff, no recovery, no 3-condition fragility
- Direct signal-to-noise per phase point; SAME 50 queries provide an *average*
  cosine quality (no Bernoulli quantization)

ARMS (3) — per phase-point — direct cosine to oracle TV:
1. **TASK_VECTOR** (substrate): `tv_substrate = bundle(bind(x_i, perm(x_i)))_K`
2. **RANDOM_VECTOR** (substrate noise floor): `tv_rand = bundle(bind(x_i, random_y))_K`
3. **ORACLE** (target): `tv_oracle = bundle(bind(x_i, perm(x_i)))_full V_ENTS_POOL`

Discriminator metric: `cosine(tv_substrate, tv_oracle)` vs
`cosine(tv_rand, tv_oracle)`.

Pre-reg property: substrate-TV's cosine to oracle should DECREASE monotonically
as K grows (more bundled noise = farther from oracle). Random-TV's cosine
should sit near zero across all K (noise floor).

### Why v4 is a TRUE mechanism-class diversion (not v3-redux)

- v1/v2/v3 all measured the SAME thing: discrete cliff in top1 recall via cleanup
- v4 measures a DIFFERENT thing: continuous cosine quality of the task vector
  itself, BEFORE the cleanup step

The cleanup step (argmax over 200-entity codebook) is what introduced K=1
binary chaos in v3. Removing the argmax dependency = removing one major
sampling-noise dimension. This is the MECHANISM-CLASS lever Director requested.

### Inherited from v3 (LOCKED for comparability):
- K_VALUES = (1, 3, 5, 10, 20, 50, 100, 200)
- N_TASKS_VALUES = (10, 20, 50)
- OVERLAP_VALUES = (0.0, 0.3, 0.6)
- V_ENTS_POOL = 200
- N_DIM = 8192
- 3 seeds (7, 13, 19)
- HRR bind/bundle/unbind primitives unchanged

## HYPOTHESIS

PRIMARY: substrate TASK_VECTOR cosine-to-oracle decreases monotonically in K
(Spearman rho_K <= -0.7 across the 8-point K grid, averaged per (V, ov) slice);
RANDOM_VECTOR cosine stays near zero (< 0.10 at all K); TV-RV gap at K=1
exceeds 0.30; behavior is seed-stable (per-K cosine sigma_across_seeds < 0.10).

ALTERNATIVE: cosine quality is not monotone in K, OR substrate TV is statistically
indistinguishable from random at K=1, OR seed-variance in cosine exceeds 0.20
across 3 seeds at any K. This would confirm v3's negative is a TRUE substrate
bound on TASK_VECTOR-style ICL at HRR scale, not an instrument issue.

POSITIVE CONTROL: For K=1 and V=1 (single task; single shot), the substrate TV
IS one bind(x_i, perm(x_i)) by construction — must produce cosine ~1.0 to its
own oracle. This is a sanity-check arm (self-cosine should be near 1).

## PHASE AXES (LOCKED — inherited from v3)

- **K (shots) in {1, 3, 5, 10, 20, 50, 100, 200}** — 8 points
- **V_tasks in {10, 20, 50}** — 3 points
- **task_overlap in {0.0, 0.3, 0.6}** — 3 points
- **n_trials_per_cell = 50** (each trial = fresh task set; cosine is averaged)
- **Total full grid:** 8 * 3 * 3 = 72 phase points per seed; 3 seeds.

## PRE-REG BANDS (LOCKED; PROSPECTIVE)

Metric definition: **`cos_TV(K, V, ov) = mean over trials of
cosine(tv_substrate, tv_oracle_global)`** (continuous in [-1, 1]).

`cos_TV_at_K1` = pooled mean of cos_TV at K=1 across all (V, ov).
`spearman_rho_K_per_slice` = Spearman rank correlation of cos_TV vs K per
(V, ov) slice (expected negative).
`tv_rv_gap_K1` = cos_TV(K=1) - cos_RV(K=1) pooled.
`seed_sigma_K` = sigma across 3 seeds of cos_TV at given K, slice.

- **HARD_PASS (chain-grade confirmation of TV ICL primitive):**
  - cos_TV at K=1 (focal slice = V=10 ov=0.0) >= 0.80
  - For at least 6 of 9 slices: Spearman rho <= -0.7 (monotone decay)
  - tv_rv_gap_K1 >= 0.30 (substrate TV statistically separates from random)
  - seed_sigma_K < 0.15 at every K-slice point (seed-stable)
  - No regime-flip (cos_TV > cos_RV at K=1 for ALL slices)

- **MIDDLE_BAND (mechanism observed; not chain-grade tight):**
  - cos_TV at K=1 >= 0.50 AND
  - For at least 3 of 9 slices: Spearman rho <= -0.5 AND
  - tv_rv_gap_K1 >= 0.15 AND
  - seed_sigma_K < 0.25

- **HARD_FAIL (TRUE substrate bound on TASK_VECTOR ICL):**
  - cos_TV at K=1 < 0.30 (substrate TV doesn't even capture single-shot task), OR
  - Spearman rho > -0.3 in 6+ of 9 slices (no monotone decay = noise dominant), OR
  - tv_rv_gap_K1 < 0.10 (substrate TV indistinguishable from random), OR
  - seed_sigma_K >= 0.30 at any K (seed-noise dominates)

**HONEST-DOWNWARD ATOMIZATION:** if HARD_FAIL, atomize as
  `task_vector_K_shot_ICL_bounded_for_HRR_substrate` — TRUE capability bound
  confirmed across THREE measurement families (cliff/cliff/cosine). Stage 3
  M3#4 concern: TASK_VECTOR is NOT a chain-grade ICL primitive on this
  substrate; alternative compositional understanding mechanisms required.

## CARDINALITY (META_RULE_H)

- **EXPECTED_N_UNITS_FULL per seed** = 3 arms * 8 K * 3 V * 3 overlap * 50 trials = **10800 cosine measurements**
- **EXPECTED_N_UNITS_SMOKE per seed** = 3 arms * 6 corners * 50 trials = **900**
- **EXPECTED_N_SEEDS** = 3 (seed 7, 13, 19)

CARDINALITY_OK declared in metrics: `cardinality_ok = (observed_n == 10800)`
per sibling full; `cardinality_ok = (observed_n == 900)` for smoke.

`HARD_FAIL_CARDINALITY_BREACH = (observed_n < expected_n)` -- emit explicit
error log + verdict UNKNOWN, do NOT silently classify.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26)

- Smoke at full N_DIM=8192 + full n_trials=50 (precision parity with full).
- Smoke = 6 corners (same K x V x ov set as v3 smoke).
- **DISCRIMINATOR CORNER for v4 = (K=200, V=50, ov=0.6)** — high-K + high-V +
  high-overlap = maximum noise regime. cos_TV pooled must be < 0.20 at this
  corner. If cos_TV >= 0.20, the bundle is saturating and the discriminator
  fails to fire -- full dispatch BLOCKED.

  ALSO: smoke must show cos_TV at (K=1, V=10, ov=0.0) >= 0.50 (low-K sanity).
  If both conditions don't hold -> BLOCK.

## HARDENING

L1 STARTED early-write + L2 per-arm progress + L3 outer try/except + L4 import-crash
sentinel + atomic per-seed partial via `_seed_checkpoint.py`.

## CHUNKED ARCHITECTURE

3 sibling files (one seed each):
- `exp_substrate_task_vector_cosine_quality_v4_seed_7.py`
- `exp_substrate_task_vector_cosine_quality_v4_seed_13.py`
- `exp_substrate_task_vector_cosine_quality_v4_seed_19.py`

Each sibling: 1 seed * 72 phase points * 3 arms * 50 trials = 10800 cosine measurements.

**POST-HOC POOLED AGGREGATION:** after all 3 siblings land, aggregator in
`_substrate_task_vector_cosine_quality_v4_core.aggregate_and_verdict` is
called with `per_seed = {7: ..., 13: ..., 19: ...}`. Computes per-slice
Spearman rho + seed-sigma + tv_rv_gap + HARD_PASS/MIDDLE_BAND/HARD_FAIL gate.

## COMPUTE

- Smoke (1 seed * 6 corners * 3 arms * 50 trials = 900 cosine measurements): ~30-60 sec.
- Full sibling (1 seed * 10800): ~10-20 min CPU.
- 3 sibling full: ~30-60 min aggregate (CPU); local_cpu_queue fine.
- Per-cell timeout: **3600s** (1 hr buffer per sibling).

## ROUTING

- Smoke: local_cpu (single seed; ~60 sec).
- Full: **local_cpu_queue** (3 siblings serial; ~45 min total). Light NumPy.
  Could route remote_cpu but local is fine — no precommit push needed.

## SUBSTRATE PREREQS (chain-grade primitives)

- HRR bind / unbind (chain-grade)
- Bundle (additive sum + normalize)
- Cosine similarity (chain-grade trivially via dot product on normalized vectors)
- NO cleanup-argmax dependency — that's the v3 noise-source v4 removes

## M3 CONCERN #4 RESOLUTION DECISION TABLE (v4)

| Outcome | M3 concern #4 verdict |
|---|---|
| HARD_PASS — monotone cos_TV decay + gap + seed-stable | TV is chain-grade ICL primitive (continuous-quality lens) |
| MIDDLE_BAND — monotone decay + some gap but not seed-tight | TV mechanism exists but compositional ICL quality regime-narrow |
| HARD_FAIL — no monotone decay OR no TV-RV gap OR seed-noise dominant | TV NOT chain-grade primitive across BOTH metric families (cliff and cosine); TRUE substrate bound on TASK_VECTOR ICL at HRR scale |

## NOTES

- Per USER 2026-06-26 disciplines: smoke FIRES discriminator (explicit check);
  no silent except blocks; cardinality_ok mandatory; band-floor MM not HP.
- Per USER 2026-06-27 substrate-as-canonical: v4 builds on v3 raw data
  structure (same bind/bundle/HRR primitives) but measures different metric.
- Per USER 2026-06-26 discriminator-must-survive-scale: smoke at n_trials=50
  + N_DIM=8192 matches full precision.
- Per cell-author judgment (Director task 2026-06-29): "Option B: Discriminator
  redesign" chosen as TRUE mechanism-class diversion. Continuous cosine vs
  discrete cliff is a different MEASUREMENT FAMILY (not different metric in
  same family).
- HONEST-NEGATIVE PATHWAY: if v4 also collapses, the chain v1/v2/v3/v4 has
  tested cliff-counting, monotonic-decay, precision-densification, AND
  cosine-quality-family lenses. A negative across four orthogonal lenses is a
  CHAIN-GRADE-ELIGIBLE NEGATIVE: substrate-bound for TASK_VECTOR ICL at HRR
  scale, atomize.
