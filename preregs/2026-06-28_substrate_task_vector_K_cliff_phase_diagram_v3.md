# Prereg: substrate_task_vector_K_cliff_phase_diagram_v3

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) v3 cliff-precision drill
**Drill source:** Skunkworks 2x-drill on v2 finding 2/3 HP + 1 HF (seed_13 HF).
v2 inherited monotonic-decay metric (artifact-corrected). v3 inherits v2 metric
unchanged but lifts per-cell SAMPLING PRECISION; the cliff EXISTS in v2 raw
data but its LOCATION is unstable across seeds because per-cell stdev ~0.15
dominates slice ordering.
**Stage:** Stage 3 (compositional understanding — substrate K-shot regime)
**P_deflated:** 0.65 (metric inherited from v2; v3 is a precision refinement
of an already-supported phenomenon; mechanism class is "MEASURE MORE
PRECISELY" not "TRY DIFFERENT METRIC")
**M3 milestone:** Concern #4 (online conversational learning). Same scope as v2.
**Supersedes:** `2026-06-28_substrate_task_vector_K_cliff_phase_diagram_v2.md`
(metric definition; bands) — v3 does NOT supersede v2 results; v3 EXTENDS v2.

## CHANGES FROM v2 (mechanism-class diversion: PRECISION, not METRIC)

### Change 1: n_queries per (K, V, ov) cell: 10 -> 50

By Bernoulli sqrt scaling, per-cell stdev for a true mean p:
- n=10: stdev = sqrt(p(1-p)/10) <= 0.158 (worst case at p=0.5)
- n=50: stdev = sqrt(p(1-p)/50) <= 0.071 (worst case at p=0.5)

~2.2x precision improvement at each cell. With 9 (V, overlap) slices, the
slice-WINNER ordering (which (V*, ov*) hits the cliff first) becomes
substrate-signal dominated rather than noise dominated.

### Change 2: POOLED cliff detection across all 3 seeds

v2 reported per-seed K_cliff_min + min-of-mins. With seed-instability, the
min-of-mins is itself unstable. v3 POOLS the per-query correctness vectors
from all 3 seeds into ONE (K, V, ov) -> top1 measurement (n_eff = 3 * 50 =
150 queries per cell), then computes cliff on the POOLED diagram. Pooling is
the lowest-variance estimator when noise is per-query independent.

### Change 3: BOOTSTRAP CI on cliff_K_loc

For each of BOOTSTRAP_N_REPLICATES = 1000 bootstrap resamples:
1. Resample queries WITH replacement at each (K, V, ov) cell (n=150 per cell).
2. Recompute pooled phase diagram.
3. Recompute monotonic-decay K_cliff per slice.
4. Identify K_cliff_min + winning slice.

95% CI: percentile-based across the 1000 replicates.

Chain-grade PROMOTION gates (LOAD-BEARING — pre-reg'd):
- winning_slice_freq >= 0.95 (winning slice unique across 95% of replicates)
- K_cliff_min CI width <= 1 K-grid-step

### Change 4: Inherit ALL v2 axes + bands + smoke discriminator

- K_VALUES = (1, 3, 5, 10, 20, 50, 100, 200) — unchanged
- N_TASKS_VALUES = (10, 20, 50) — unchanged
- OVERLAP_VALUES = (0.0, 0.3, 0.6) — unchanged
- V_ENTS_POOL = 200 — unchanged
- N_DIM_FULL = 8192 — unchanged
- ARMS = TASK_VECTOR / RANDOM_VECTOR / ORACLE — unchanged
- HP_K1_FLOOR_RECALL = 0.95 — unchanged
- HP_CLIFF_FLOOR_RECALL = 0.40 — unchanged
- HP_AVG_ARMS_DIFF_MIN = 0.20 — unchanged
- DISCRIMINATOR_SMOKE_FLOOR = 0.40 at (K=200, V=10, ov=0.0) — unchanged
- K_SAT_THRESHOLD = 0.95 — unchanged
- MONOTONIC_RECOVERY_TOL = 0.05 — unchanged

## HYPOTHESIS

Same mechanism as v2; v3 tests whether the cliff LOCATION (winning slice +
K_cliff_min) is sampling-noise unstable or substrate-property unstable.

PRIMARY HYPOTHESIS: at n=50 queries per cell, pooled across 3 seeds with
bootstrap CI, the cliff is seed-stable (winning slice fixed + K_cliff CI tight)
=> chain-grade promotion candidate.

ALTERNATIVE HYPOTHESIS: even at n=50 + pooled, the cliff location varies
across bootstrap replicates => substrate TASK_VECTOR K-cliff is inherently
noisy at HRR scale; MM classification stands; HONEST-NEGATIVE for chain-grade.

POSITIVE CONTROL: v2 seed_7 winning slice was (V=50, ov=0.00) at K_cliff_min=5
(HARD_PASS). v2 seed_19 winning slice was (V=50, ov=0.30) at K_cliff_min=5
(HARD_PASS). Both at V=50, K_cliff_min=5; only the overlap differs. v3 should
either CONVERGE these (winning slice unique across bootstrap) OR show the V=50
band is too noisy to discriminate ov=0.00 vs ov=0.30 (winning slice CI
includes both).

## ARMS (3) — per phase-point

1. **TASK_VECTOR** — K legitimate (input_i, perm(input_i)) binds bundled per task.
2. **RANDOM_VECTOR** — K (input_i, random_entity) binds (output wrong); floor.
3. **ORACLE** — perfect permutation table query; saturation comparator at 1.0.

**arms-must-differ at each phase point:** TASK_VECTOR > RANDOM_VECTOR by > 0.20
(pooled top1_recall mean) at HARD_PASS; if TASK_VECTOR <= RANDOM_VECTOR at any
low-K low-V point, META_RULE_AM flag.

## PHASE AXES (LOCKED — inherited from v2)

- **K (shots) in {1, 3, 5, 10, 20, 50, 100, 200}** — 8 points
- **V_tasks in {10, 20, 50}** — 3 points
- **task_overlap in {0.0, 0.3, 0.6}** — 3 points
- **n_queries_full = 50** (v2 had 10)
- **Total full grid:** 8 * 3 * 3 = 72 phase points per seed; 3 seeds POOLED.

## PRE-REG BANDS (LOCKED; PROSPECTIVE; metric = top1_recall in [0,1])

The metric is **K_cliff_VALID per (V, overlap) slice** computed on the POOLED
phase diagram (NOT per-seed; this is the v3 lever).

- **HARD_PASS (chain-grade confirmation):**
  - Pooled metric: at least one slice with cliff_status="valid"
  - At least one (K=1, V<=20) point with pooled TASK_VECTOR top1 >= 0.95
  - At least one phase-point with pooled TASK_VECTOR top1 < 0.40
  - avg(TASK_VECTOR - RANDOM_VECTOR) across 72 pooled points >= 0.20
  - No regime-flip (META_RULE_AM)
  - **NEW v3 bootstrap gates (BOTH required):**
    - winning_slice_freq >= 0.95 (slice unique across 95% of bootstrap reps)
    - K_cliff_min CI width <= 1 K-grid-step (e.g., 5 to 10 is 1 step; 5 to 20 is 2 steps)

- **MIDDLE_BAND:**
  - All HARD_PASS conditions EXCEPT bootstrap gates fail (cliff exists +
    arms differ + low-K saturates BUT slice or K location bootstrap-unstable),
    OR
  - 1-2 valid cliffs of 9 slices (cliff regime-narrow), OR
  - arms-differ 0.10-0.20 on average, OR
  - Most slices "no_saturation_reached" or "non_monotonic"

- **HARD_FAIL:**
  - TASK_VECTOR top1 >= 0.95 at ALL 72 pooled points (by-construction
    saturation), OR
  - avg(TASK_VECTOR - RANDOM_VECTOR) < 0.10, OR
  - ANY low-K low-V pooled point with TASK_VECTOR <= RANDOM_VECTOR
    (META_RULE_AM), OR
  - Smoke discriminator failed-to-fire (full dispatch BLOCKED at smoke gate)

**IMPORTANT FINDING ANNOTATION:** verdict_msg cites both the POOLED K_cliff_min
+ winning slice AND the bootstrap CI on cliff_K + winning_slice_freq.

## CARDINALITY (META_RULE_H)

- **EXPECTED_N_UNITS_FULL per seed** = 3 arms * 8 K * 3 V * 3 overlap * 50 queries = **10800**
- **EXPECTED_N_UNITS_SMOKE per seed** = 3 arms * 6 corners * 50 queries = **900**
- **EXPECTED_N_SEEDS_CHUNKED** = 3 (seed 7, 13, 19; one sibling file each)

CARDINALITY_OK declared in metrics: `cardinality_ok = (observed_n == 10800)`
per sibling full; `cardinality_ok = (observed_n == 900)` for smoke.

`HARD_FAIL_CARDINALITY_BREACH = (observed_n < expected_n)` -- emit explicit
error log + verdict UNKNOWN, do NOT silently classify.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26)

- Smoke at full N_DIM=8192 + full n_queries=50 (precision parity with full).
- Smoke includes 6 corners (inherited from v2; same DISCRIMINATOR corner).
- **DISCRIMINATOR CORNER = (K=200, V=10, ov=0.0)** — pooled TV must be < 0.40.
- If smoke shows TV >= 0.40 at this corner, full dispatch BLOCKED.
- v2 single-seed smoke at this corner: TV(K=200, V=10, ov=0.0) = 0.000. v3
  expects the same (deeper precision should NOT erase the cliff floor).

## HARDENING

L1 STARTED early-write + L2 per-arm progress + L3 outer try/except + L4 import-crash
sentinel + atomic per-seed partial via `_seed_checkpoint.py`.

## CHUNKED ARCHITECTURE

3 sibling files (one seed each):
- `exp_substrate_task_vector_K_cliff_phase_diagram_v3_seed_7.py`
- `exp_substrate_task_vector_K_cliff_phase_diagram_v3_seed_13.py`
- `exp_substrate_task_vector_K_cliff_phase_diagram_v3_seed_19.py`

Each sibling: 1 seed * 72 phase points * 3 arms * 50 queries = 10800 records.

**POST-HOC POOLED AGGREGATION:** after all 3 siblings land, the aggregator in
`_substrate_task_vector_K_cliff_phase_diagram_v3_core.aggregate_and_verdict`
is called with `per_seed = {7: ..., 13: ..., 19: ...}` and
`do_bootstrap=True`. This performs the pooled phase diagram + bootstrap CI
+ chain-grade gate decision. Each sibling's own metrics.json reports the
per-sibling (single-seed) view for sanity; the chain-grade verdict comes
from the POST-HOC POOLED aggregation, NOT any individual sibling.

## COMPUTE

- Smoke (1 seed * 6 corners * 3 arms * 50 queries = 900 results): ~30-90 sec.
- Full sibling (1 seed * 10800 results, per-seed): ~15-30 min CPU.
  (v2 full sibling = 2160 records at ~270s = ~125ms/record. v3 has 5x more
  records => ~1350s = ~22 min per sibling. Buffer 5x = 6750s = ~2 hr.)
- 3 sibling full dispatch: ~45-90 min aggregate (CPU); local_cpu_queue fine.
- Per-cell timeout: **7200s** (2 hr buffer per sibling; comfortably above 5x).

## ROUTING

- Smoke: local_cpu (single seed; ~60-90 sec).
- Full: **remote_cpu_queue** (3 siblings in parallel via dispatch chain).
  Light NumPy cell; remote runner has bandwidth (remote_cpu queue depth = 0
  pending at v3 design time). Local_cpu_queue alternative is acceptable
  (~45-90 min serial), but parallel remote is faster.

## SUBSTRATE PREREQS (cite chain-grade primitives)

- HRR bind / unbind (chain-grade)
- Bundle (additive sum + normalize)
- Cleanup via cosine argmax over entity codebook

## M3 CONCERN #4 RESOLUTION DECISION TABLE (v3)

| Outcome | M3 concern #4 verdict |
|---|---|
| HARD_PASS — pooled cliff + arms differ + low-K saturation + bootstrap gates | TV is CHAIN_GRADE primitive (seed-stable; precision-controlled) |
| MIDDLE_BAND — pooled cliff exists but bootstrap-unstable | Primitive regime exists but location-noisy at HRR scale |
| HARD_FAIL — no valid pooled cliffs OR arms don't differ OR regime-flip | TV NOT supported as M3#4 primitive |

## NOTES

- v2 MIXED MM/MM/MM after re-tier or HP/HP/HF as recorded — both per-sibling
  views are honest; the substantive question is: "at higher precision, does
  the cliff converge to a single location?" v3 answers this directly.
- Honest-downward: if v3 bootstrap CI is wide (e.g., winning slice in 3+
  candidates with ~30% freq each), MM stands at substrate-scale and we don't
  promote. This is a real possible outcome and the bands ABOVE catch it.
- Per USER 2026-06-26 disciplines: smoke FIRES discriminator (explicit
  smoke_discriminator_check); no silent except blocks (L3/L4 enforced);
  cardinality_ok mandatory; band-floor MM not HP (preserved in verdict logic).
- Per USER 2026-06-27 substrate-as-canonical: v3 explicitly builds on v2 raw
  data structure (per-query correctness vectors). Substrate-KB has v1+v2
  cliff atoms; v3 results extend that chain.
- Per USER 2026-06-26 discriminator-must-survive-scale: smoke at n_queries=50
  + N_DIM=8192 matches full precision; no smoke-vs-full precision mismatch.
- Per Skunkworks 2x-drill: cliff at v2 measurement precision was not seed-
  stable. v3 tests whether the cliff is location-stable at 2.2x finer
  precision pooled across 3 seeds. This is the canonical mechanism-class
  diversion ("measure with better instruments before declaring effect noisy").
