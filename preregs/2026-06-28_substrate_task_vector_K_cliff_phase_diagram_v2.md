# Prereg: substrate_task_vector_K_cliff_phase_diagram_v2

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) v2 metric-artifact fix
**Drill source:** Skunkworks audit 2026-06-28 found v1 K_cliff metric artifact:
v1 reported HARD_PASS with K_cliff_min=1 at (V=10, ov=0.6), but off-disk audit
showed this slice had TV(K=1)=0.0 then TV(K=3..5)=0.3..0.8 (non-monotonic; low-K
cue degeneracy, NOT a true high-K saturation cliff). v2 fixes the metric and
narrows the regime to the discriminating one.
**Stage:** Stage 3 (compositional understanding — substrate K-shot regime)
**P_deflated:** 0.55 (revising a measured cell; mechanism + cliff exist per v1 raw data)
**M3 milestone:** Concern #4 (online conversational learning). Same scope as v1.
**Supersedes:** `2026-06-28_substrate_task_vector_K_cliff_phase_diagram_v1.md`

## CHANGES FROM v1 (load-bearing)

### Change 1: K_cliff metric REQUIRES monotonic decay from saturation

v1 formula: `K_cliff(V, ov) = min{K in K_VALUES : TV(K, V, ov) < 0.40}`

This formula ADMITS low-K cue degeneracy: if TV(K=1)=0.0 because 1 shared-context
shot can't address the focal task, the formula returns K_cliff=1 — but the substrate
HASN'T been pushed past saturation, it's been pushed below floor by INPUT POVERTY,
not by HIGH-K interference saturation.

v2 formula:
```
1. K_sat(V, ov) = min{K in K_VALUES : TV(K, V, ov) >= 0.95}     (saturation threshold)
2. If K_sat is None: slice status = "no_saturation_reached"     (cliff INVALID)
3. K_cliff(V, ov) = min{K in K_VALUES : K > K_sat AND TV(K, V, ov) < 0.40}
4. recovery_check: for all K' > K_cliff: TV(K', V, ov) <= 0.40 + 0.05 (tol)
5. If recovery_check fails: slice status = "non_monotonic"      (cliff INVALID)
6. Otherwise: slice status = "valid", K_cliff is reported
```

This explicitly enforces: cliff = REAL HIGH-K SATURATION, not low-K cue degeneracy.

### Change 2: V_tasks axis tightened to {10, 20, 50}

v1 used V={10, 50, 200}. Off-disk audit of v1 metrics.json (seed=7) showed 18/21
phase points at V=200 had TV=0.0 (substrate-cannot-encode floor at full N=8192
when V_tasks=200 and the focal task gets 1 of 200 task-vectors competing in the
bundle). This is floor-vs-floor: not informative for cliff detection.

v2 drops V=200, adds V=20 to fill the V-axis between 10 and 50.

### Change 3: K axis extended to K=200

v1 K_VALUES = (1, 3, 5, 10, 20, 50, 100). In the discriminating regime (V=10,
ov=0.0) v1 showed monotonic decay 1.0 -> 1.0 -> 0.9 -> 0.6 -> 0.5 -> 0.2 -> 0.1.
K=200 added to confirm asymptotic floor (preliminary smoke: TV(K=200, V=10,
ov=0.0)=0.0 at seed=7 — DEEP cliff signal).

### Change 4: V_ENTS_POOL decoupled from V_tasks

v1 codebook size = max(V_tasks_values) = 200. v2 codebook is V_ENTS_POOL=200
INDEPENDENT of V_tasks. The codebook is the shared entity pool from which all
tasks draw inputs and outputs; keeping it large prevents random input/output
collisions across tasks even when V_tasks is small (10, 20, 50). Initial single-
seed smoke with codebook=50 showed TV=0.0 at K=1 V=10 ov=0.0 because random
input picks collided across tasks. Decoupling fixes this.

### Change 5: SMOKE discriminator-survives-scale corner at K=200

Smoke includes 6 corners (was 5). The 6th is the MUST-FIRE discriminator at
(K=200, V=10, ov=0.0). If smoke shows TV >= 0.40 at this corner, full dispatch
is BLOCKED (smoke verdict overrides aggregate verdict). Preliminary single-seed
smoke: TV(K=200, V=10, ov=0.0)=0.0 — discriminator fires robustly.

## HYPOTHESIS

Same as v1: `TASK_VECTOR = sum_i bind(input_i, perm(input_i))` followed by
`unbind(query_input, TV)` + cleanup recovers `perm(query_input)`. Capacity bounded
by Plate-class `K_critical ~ N_DIM / (4 * V_tasks)` (rough).

For N_DIM=8192:
- V=10 -> K_critical ~ 205
- V=20 -> K_critical ~ 102
- V=50 -> K_critical ~ 41

## ARMS (3) — per phase-point

1. **TASK_VECTOR** — K legitimate (input_i, perm(input_i)) binds bundled per task.
2. **RANDOM_VECTOR** — K (input_i, random_entity) binds (output is wrong); floor.
3. **ORACLE** — perfect permutation table query; saturation comparator at 1.0.

**arms-must-differ at each phase point:** TASK_VECTOR > RANDOM_VECTOR by > 0.20
(top1_recall) at HARD_PASS bands; if TASK_VECTOR <= RANDOM_VECTOR at any low-K
low-V point, META_RULE_AM flag.

## PHASE AXES (LOCKED)

- **K (shots) in {1, 3, 5, 10, 20, 50, 100, 200}** — 8 points
- **V_tasks in {10, 20, 50}** — 3 points
- **task_overlap in {0.0, 0.3, 0.6}** — 3 points
- **Total full grid:** 8 * 3 * 3 = 72 phase points

## PRE-REG BANDS (LOCKED; PROSPECTIVE; metric = top1_recall in [0,1])

Phase-diagram metric (v2): **K_cliff_VALID per (V, overlap) slice** = per slice
formula above (monotonic-decay required).

- **HARD_PASS** (chain-grade confirmation):
  - For at least one (V, overlap) slice, **K_cliff_VALID exists** (status="valid")
  - AT LEAST ONE phase-point at K=1 with V<=20 shows TASK_VECTOR top1 >= 0.95
  - AT LEAST ONE phase-point shows TASK_VECTOR top1 < 0.40 (cliff observable)
  - arms-must-differ: avg(TASK_VECTOR - RANDOM_VECTOR) across all 72 phase points >= 0.20
  - No regime-flip (META_RULE_AM): no low-K-low-V point with TV < RV.

- **MIDDLE_BAND**:
  - 1-2 valid cliffs out of 9 (V, overlap) slices (cliff regime-narrow), OR
  - arms-differ 0.10-0.20 on average, OR
  - Most slices are "no_saturation_reached" or "non_monotonic" (substrate behavior
    not clean enough to fire metric — band-floor result, not chain-grade).

- **HARD_FAIL** (saturation-trivial OR un-mechanistic):
  - TASK_VECTOR top1 >= 0.95 at ALL 72 phase points (by-construction saturation), OR
  - avg(TASK_VECTOR - RANDOM_VECTOR) < 0.10, OR
  - ANY (low-K, low-V) point shows TASK_VECTOR <= RANDOM_VECTOR (META_RULE_AM)
  - OR smoke discriminator failed-to-fire (full dispatch BLOCKED — caught at smoke gate)

**IMPORTANT FINDING ANNOTATION:** verdict_msg cites K_cliff_min across all VALID
slices as "K_cliff_min=X at V=Y_ov=Z". Slices with status "no_saturation_reached"
or "non_monotonic" are reported with status + reason; they DO NOT contribute to
K_cliff_min.

## NEW META_RULE candidate (Skunkworks proposal 2026-06-28)

**META_RULE_AS:** Cliff metrics MUST require monotonic decay from saturation.
A metric of the form `min{K : metric(K) < floor}` is INVALID without checking:
(a) saturation was first reached at some K' < K (mechanism IS working), and
(b) metric stays below floor for all K' > K (decay is monotonic, not noisy dip).

Cells declaring cliff metrics must implement these checks. This prereg embodies
the rule.

## FAIRNESS GATES

- Same N_DIM=8192 across all arms + phase points.
- Same encoder (HRR bipolar random, FFT bind).
- Same V_ENTS_POOL=200 entity codebook per seed (regenerated per seed).
- Each phase point draws K context pairs fresh; query is one of the K presented inputs.
- task_overlap: shared INDICES across V_tasks within a seed (pool shared at overlap fraction).
- Q-discipline: TV top1=1.000 at K>=50 V>=20 triggers leakage audit.
- META_RULE_AM check: if RANDOM > TASK_VECTOR at any (K, V, overlap), flag regime-flip.

## CARDINALITY (META_RULE_H)

- **EXPECTED_N_UNITS_FULL per seed** = 3 arms * 8 K * 3 V * 3 overlap * 10 queries = **2160**
- **EXPECTED_N_UNITS_SMOKE per seed** = 3 arms * 6 corners * 10 queries = **180**
- **EXPECTED_N_SEEDS_CHUNKED** = 3 (seed 7, 13, 19; one sibling file each)

CARDINALITY_OK declared in metrics: `cardinality_ok = (observed_n == 2160)` per
sibling full; `cardinality_ok = (observed_n == 180)` for smoke.

`HARD_FAIL_CARDINALITY_BREACH = (observed_n < expected_n)` -- emit explicit error
log + verdict UNKNOWN, do NOT silently classify.

## DISCRIMINATOR-SURVIVES-SCALE (USER 2026-06-26 + Fix #14)

- Smoke at **full N_DIM=8192**.
- Smoke includes 6 corners spanning saturation (K=1) to deep cliff (K=200).
- **DISCRIMINATOR CORNER = (K=200, V=10, ov=0.0)** — MUST show TV < 0.40.
- If smoke shows TV >= 0.40 at this corner, full dispatch is BLOCKED
  (verdict overridden to HARD_FAIL by smoke_discriminator_check; metrics.json
  records `smoke_discriminator_fired=False`).
- Single-seed prelim (seed=7): TV(K=200, V=10, ov=0.0)=0.000 -- robust discriminator.

## HARDENING

L1 STARTED early-write + L2 per-arm progress + L3 outer try/except + L4 import-crash
sentinel + atomic per-seed partial via `_seed_checkpoint.py`.

## CHUNKED ARCHITECTURE (USER 2026-06-28)

3 sibling files (one seed each):
- `exp_substrate_task_vector_K_cliff_phase_diagram_v2_seed_7.py`
- `exp_substrate_task_vector_K_cliff_phase_diagram_v2_seed_13.py`
- `exp_substrate_task_vector_K_cliff_phase_diagram_v2_seed_19.py`

Each sibling: 1 seed * 72 phase points * 3 arms * 10 queries = 2160 result records.
Aggregation step (post hoc): combine 3 sibling metrics.json files into phase-map matrix.

## COMPUTE

- Smoke (1 seed * 6 corners * 3 arms * 2 queries = 36 results): ~30-60 sec.
- Full sibling (1 seed * 2160 results, batched): ~5-10 min CPU per seed.
  (v1 seed=7 FULL ran in 236s for 1890 records on CPU = ~125ms/record. v2 has
   2160 records = ~270s = ~4.5 min per sibling. Buffer to 5x = 1500s = 25 min.)
- 3 sibling full dispatch: ~15-30 min aggregate (CPU); fast enough for local_cpu.
- Per-cell timeout: **3600s** (1 hr buffer; comfortably above 5x expected).

## ROUTING

- Smoke: **local_cpu** (single seed, ~60 sec, <1GB memory).
- Full: **local_cpu_queue** or **remote_cpu_queue** acceptable. v1 ran at 236s/seed
  on CPU (FULL); v2 estimated ~270-300s/seed -- well within local CPU budget.
  Compared to GPU dispatch overhead (push to remote, queue wait, hour-long warmup
  in some past cells), local_cpu_queue is the right home for this cell size.

## SUBSTRATE PREREQS (cite chain-grade primitives)

- HRR bind / unbind (chain-grade; v1 K=5 top1=1.000)
- Bundle (additive sum + normalize)
- Cleanup via cosine argmax over entity codebook

## M3 CONCERN #4 RESOLUTION DECISION TABLE (v2)

| Outcome | M3 concern #4 verdict |
|---|---|
| HARD_PASS — at least 1 VALID cliff + arms differ + low-K saturation met | TV is genuine chain-grade primitive (regime-wide) |
| MIDDLE_BAND — 1-2 valid cliffs of 9 slices, OR most slices flagged invalid | Primitive regime-narrow; usable for ICL with bounded K |
| HARD_FAIL — no valid cliffs OR arms don't differ OR regime-flip OR smoke disc failed | TV NOT supported as M3#4 primitive |

## NOTES

- v1 honest-downward MM classification stands. v1 metrics.json retained for audit.
- v2 is a metric REVISION cell, not a re-dispatch of v1. The revised metric
  explicitly fixes the artifact that caused v1 to mis-report K_cliff_min=1.
- Per USER 2026-06-26 disciplines: no silent except blocks (already enforced via
  L3/L4); smoke FIRES discriminator (explicit smoke_discriminator_check); band-floor
  results = MIDDLE_BAND not HARD_PASS (verdict logic preserves this distinction);
  cardinality_ok mandatory (declared above).
- Per USER 2026-06-27 substrate-as-canonical: v2 builds on v1 raw data already in
  substrate registry; query the substrate-KB for prior task_vector cells before
  any reframing.
