# Pre-registration: substrate_refuse_gate_v_rel_extension_v1

**Date:** 2026-06-25
**Anchor:** substrate_refuse_gate_v_rel_extension_v1
**Script:** experiments/exp_substrate_refuse_gate_v_rel_extension_v1.py
**Queue:** local_cpu_queue (numpy; ~1h CPU wall per Research drill estimate)
**Seeds:** [11, 13, 19] (cross-cell consistent)
**V_REL_SWEEP (full):** [8, 16, 32, 64, 128, 256, 512]

## Promotion context (Tier S #1 / Research DRILL 1 ITEM 8)

v2 (`exp_substrate_refuse_gate_near_domain_v2`) chain-grade-CONFIRMED HARD_PASS_BOTH_WORK at
V_REL_IN=V_REL_OUT=8 (envelope rail). Verbatim:
```
HARD_PASS_BOTH_WORK: AUDIT_RELATION_CHECK NEAR_refuse=1.000 >= 0.70 AND
AUDIT_NAIVE_PLUS_INTENT NEAR_refuse=0.987 >= 0.70 (rel_cv=0.000 aipi_cv=0.019)
```

Research drill: cleanup envelope says N=8192 chain-grades V<=4000 -- V_REL=50 already passed
inside today's earlier 4-cell wave. P=0.65 (highest in drill); compute ~1h CPU (cheap).
Closes a load-bearing Stage 3 envelope (refuse-gate scales).

## v1 design (envelope extension, single mechanism)

- Same NEAR-DOMAIN-MIXED 3-arm discriminator as v2 (NAIVE_ALONE / RELATION_CHECK / NAIVE_PLUS_INTENT)
  removing v2's redundant INTENT_ALONE arm (cleaner discrimination at scale)
- Sweep V_REL in {8 (rail), 16, 32, 64, 128, 256, 512} (7 points = rail + 6 extension)
- V_REL_IN = V_REL_OUT for each point (symmetric scaling; tests cleanup envelope only)
- All other config matched to v2 (N=8192, V_C_IN=600, N_QUERIES_PER_CATEGORY=100)
- ARM_AUDIT_RELATION_CHECK is the chain-grade-eligible mechanism under test at each V_REL

## Pre-registered bands (LOCKED at module init via assert META_PROSPECTIVE_BANDS_FRESH_SEEDS)

### HARD_PASS_V_REL_EXTENSION
- ARM_AUDIT_RELATION_CHECK at V_REL=256: NEAR_DOMAIN_MIXED refuse >= **0.85** across seeds
- AND cv (refuse_rate across seeds) <= **0.05**
- AND PURE_IN_DOMAIN answer >= **0.85** at V_REL=256 (sanity rail per arm)

### CHAIN_GRADE_AT_CLIFF_X
- Passes chain-grade gate at one of {64, 128} but cliffs at higher
- Mechanism extends part of envelope; cliff identified

### MIDDLE_BAND_PARTIAL_V_REL_EXTENSION
- ARM_AUDIT_RELATION_CHECK in [0.70, 0.85) on NEAR_DOMAIN_MIXED at some V_REL with cv <= 0.05
- Partial closure; not full chain-grade

### HARD_FAIL_V_REL_CLIFF_AT_LOW
- ARM_AUDIT_RELATION_CHECK only chain-grades at V_REL <= 32
- Envelope does NOT extend meaningfully past v2's rail

### HARD_FAIL_V_REL_CLIFF_AT_RAIL
- Chain-grades ONLY at V_REL=8 (v2 rail); 16+ cliffs immediately

### HARD_FAIL_NO_V_REL_HOLDS
- RELATION_CHECK fails NEAR refuse band at ALL V_REL in sweep

### HARD_FAIL_SANITY_RAIL
- Any arm at any V_REL: PURE_IN_DOMAIN answer < 0.85 OR PURE_OUT_OF_DOMAIN refuse < 0.85

## Q-discipline guard (BIAS-Q)

If ARM_AUDIT_RELATION_CHECK NEAR_DOMAIN_MIXED refuse_rate >= **0.995** at ALL V_REL up to 512:
- Verdict carries `[Q-DISCIPLINE: RELATION_CHECK >= 0.995 at V_REL=...; suspect saturation]`
- Recommend V_REL=1000+ extension OR harder NEAR_DOMAIN_MIXED construction
- Flag is documentation, not auto-demotion; cert-owner tiers per by-construction-saturation rule

## Cross-cell discipline

- ASCII only (verified)
- Substrate-only at inference (numpy primitives; zero LLM forward calls; counter asserted = 0)
- Per-arm metrics in verdict_msg + per_unit (Fix #28)
- Bands locked at module init via assert (META_PROSPECTIVE_BANDS_FRESH_SEEDS)
- Seeds [11, 13, 19] (cross-cell consistent)
- META_M6: baselines DERIVED in-cell at each V_REL (not copied from v2 V_REL=8 only)
- META_M7: smoke matches full on N + V_C_IN + N_QUERIES_PER_CATEGORY (capacity-sensitive)
  Only SEEDS + V_REL_SWEEP reduce in smoke (full V_REL_SWEEP=7 vs smoke=3)

## Capacity-feasibility analysis

Per-arm per-(seed, V_REL) wall: dominated by bipolar construction at large V_REL + 3 arms x 3 cat
evaluation. At V_REL=512: 600+512=1112 atoms x N=8192 = 9.1M floats = ~36MB per arm; matmul
N_QUERIES_PER_CAT*N*V_REL = 100*8192*512 ~ 0.4 GFLOPS per query category per arm.

Per unit (seed, V_REL) wall estimate:
- V_REL=8: ~0.5s
- V_REL=128: ~5s
- V_REL=512: ~20s

Total: 3 seeds x 7 V_REL points = 21 units; max ~20s each at V_REL=512.
Sum: ~3 seeds x (0.5+1+2+5+10+15+20) ~ 160s; with overhead ~5min wall total.

Drill estimate said ~1h; my measurement says ~5min. Drill's 1h figure included broader margins
or was based on a costlier baseline. Either way: well within local_cpu_queue.

## Timeout estimate

Formula: timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))

Smoke wall = 0.2s (3 units at smoke regime). Full N grows 2048->8192 (4x); V_REL_SWEEP grows
3 points -> 7 points; SEEDS grows 1 -> 3; N_QUERIES grows 20 -> 100; V_C grows 150 -> 600.

ceil(1.5 * 0.2 * (8192/2048)^1.0 * (7/3) * (3/1) * (100/20) * (600/150)) =
ceil(1.5 * 0.2 * 4 * 2.33 * 3 * 5 * 4) = ceil(167.8) = 168s.

Add safety margin for cleanup at V_REL=512 (large matmul): **timeout_s = 1800 (30 min)** -- well
below 14400s. No PROT-021 checkpoint needed but cell already wires per-unit checkpoint.

## PROT compliance

- PROT-018 (`_n<N>` suffix): anchor has no `_n<N>` suffix; rule does not apply.
- PROT-019 (large-N timeout floor): no `_n<N>` suffix; rule does not apply.
- PROT-020 (GPU queue requires torch): local_cpu_queue path; rule does not apply.
- PROT-021 (long-timeout needs checkpoint): timeout 1800s < 14400s; per-unit checkpoint wired anyway.

## Pre-flight smoke + self-test gate (queue_add.py)

- Smoke runs with `RUN_MODE=smoke`: N=2048, V_C_IN=150, N_QUERIES_PER_CATEGORY=20, seeds=[11],
  V_REL_SWEEP=[8, 64, 256] (3 points only)
- Smoke wall measured: 0.2s (well under 180s queue_add cap)
- Self-test (numpy, no GPU) asserts T1-T10:
  T1 bipolar unit-norm; T2-T3 build_substrate at V_REL=8 and V_REL=256;
  T4 query corpus per-category counts; T5 audit primitives self-id;
  T6 out-of-domain leak floor; T7 all 3 arms return refused; T8 NEAR relation does NOT cleanup;
  T9 bands locked; T10 LLM counter = 0
- Self-test PASSED LOCAL (verified before commit)

## Symmetric verify rail (USER NEGATIVITY-BIAS rule)

Verdict reports BOTH directions:
- HARD_PASS conditions (RELATION_CHECK chain-grades at V_REL=256)
- MIDDLE_BAND (partial)
- HARD_FAIL (cliff at low / no-V_REL-holds)
- HARD_FAIL_SANITY_RAIL (PURE category breaks at any V_REL)
- Per (seed, V_REL, arm, category) breakdown in per_unit for Skunkworks step-0 re-read

## Strategic significance (decision-grade)

If HARD_PASS_V_REL_EXTENSION:
- Refuse-gate scales to 32x v2 envelope (8 -> 256 relations)
- Production-grade medical/legal/financial domain-mix tasks become substrate-feasible
- Composes with Cell B intent classifier (in flight) for production refuse-gate

If CHAIN_GRADE_AT_CLIFF_X:
- Envelope partially extends; cliff at known V_REL identifies cleanup capacity bound
- Substrate-product positioning: "refuse-gate at V_REL up to X" honest statement

If HARD_FAIL_V_REL_CLIFF_AT_LOW or AT_RAIL:
- Envelope DOESN'T extend (theory said it should); cleanup capacity tighter than predicted
- Triggers research drill into WHY relation cleanup fails at moderate V_REL (likely subject-relation
  cross-term in audit)

## Honest negatives possible

- Sanity rails (PURE categories) might break at V_REL=512 if subject cleanup interferes with relation library
- RELATION_CHECK might saturate >= 0.995 at all V_REL up to 512 (Q-discipline; corpus too easy)
- Adversarial subject-relation interactions might require a cross-V_REL adjustment (out of scope)

## Dispatch plan

1. Author cell + prereg (this file) -- DONE
2. Self-test PASSED locally -- DONE (T1-T10 PASS)
3. Smoke run PASSED locally -- DONE (verdict HARD_PASS_V_REL_EXTENSION at smoke scale)
4. Path-scoped commit BEFORE dispatch (cell + prereg only; NEVER `git add -A` / `.`)
5. Dispatch via `bash tools/orchestrator/queue_add.sh local_cpu_queue substrate_refuse_gate_v_rel_extension_v1 experiments/exp_substrate_refuse_gate_v_rel_extension_v1.py preregs/2026-06-25_substrate_refuse_gate_v_rel_extension_v1.md 1800`
6. File dispatch notification in batch note

## Routing rationale

- local_cpu_queue: numpy-only; CPU-feasible; ~5min wall. No GPU needed.
- Pause flag verified NOT set at dispatch authorship time.

## Test plan post-landing

- Skunkworks step-0 honest re-read of per_unit per_V_REL refuse_rate (NOT verdict_msg framing)
- Verify cv across 3 seeds at each V_REL is <= 0.05 for chain-grade claim
- Verify PURE_IN_DOMAIN sanity rail holds at every V_REL (substrate didn't degrade in unexpected way)
- Cross-cell consistency: compare V_REL=8 slice to v2's V_REL=8 result (sanity check regime parity)
- If HARD_PASS_V_REL_EXTENSION: queue composition cell with Cell B intent classifier
- If MIDDLE_BAND or HARD_FAIL_CLIFF: queue subject-relation cross-term study
