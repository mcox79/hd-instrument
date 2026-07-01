# Prereg: substrate_task_vector_HRR_ICL_K_500_extended_v1

**Date:** 2026-07-01 (v1-A axis revision after smoke discriminator-must-survive-scale)
**Author:** exp_dev (Opus 4.7 1M, agent-spawn) K axis extended to straddle cliff
**Referent:** `substrate_task_vector_K_extended_v1` (2026-06-30 extended-K
reach, K axis {50, 100, 200, 500, 1000}). Referent smoke at K=200 also
failed to fire discriminator (TV~0.87) — same design flaw.
**Stage:** Stage 3 (compositional understanding, K-shot regime)
**M3 milestone:** Concern #4 (online conversational learning).
**Mechanism-class:** REACH extension (same primitives; K axis pushed
through the cliff observed in full-K probe).
**P_deflated:** 0.60 (mechanism inherited; full-K probe already localized
cliff at K~1200-2000, so this cell confirms shape with formal verdict
discipline).

## USER SPEC (2026-07-01, revised after smoke-fail on original K=350 axis)

- K in {50, 200, 500, 1000, 2000}  (option-A after Director instruction)
- 3 seeds {7, 13, 19}
- Same TASK_VECTOR HRR ICL mechanism
- Discriminator: cliff-K localization with cross-seed cv < 10%
  (interpreted: gate at high-signal K only; Bernoulli floor cv diagnostic)
- GPU-eligible (matmul-heavy at K=2000 evaluations)
- SMOKE local; FULL -> overnight_queue

## HYPOTHESIS

PRIMARY: K axis straddles cliff cleanly. Expected shape per full-K probe:
- K=50:   TV ~ 1.0    (alive, near-saturation)
- K=200:  TV ~ 0.9    (alive)
- K=500:  TV ~ 0.5-0.6 (pre-cliff shoulder)
- K=1000: TV ~ 0.3-0.4 (mid-cliff, mechanism dying)
- K=2000: TV ~ 0.05-0.10 (dead-floor, Bernoulli-random)

K_of_mechanism_death expected at K=500 or K=1000 (where arms_diff drops
below 0.30). Cross-seed cv < 10% at K in {50, 200}.

ALTERNATIVE: cliff cleaner-than-expected -> K_of_mechanism_death localizes
sharply at one K; smooth-decay -> MB.

## AXES (LOCKED)

- K_VALUES        = (50, 200, 500, 1000, 2000)
- V_TASKS         = 10
- OVERLAP         = 0.0
- V_ENTS_POOL     = 2200  (lifted to accommodate K=2000)
- N_QUERIES_FULL  = 100
- N_QUERIES_SMOKE = 100 (discriminator-must-survive-scale)
- N_DIM_FULL      = 8192
- N_DIM_SMOKE     = 8192
- ARMS            = (TASK_VECTOR, RANDOM_VECTOR, ORACLE)

## BAND DEFINITIONS (envelope-fail-bands, LOCKED)

- HP_K50_FLOOR_RECALL       = 0.85
- HP_MECHANISM_FLOOR_RATIO  = 0.30    (TV_mean - RV_mean alive-vs-dead)
- HP_HIGH_SIGNAL_THRESHOLD  = 0.50    (K is "high-signal" if mean(TV) >= this)
- HP_CV_HIGH_SIGNAL         = 0.10    (cv gate at high-signal K only)
- HF_ALL_FLOOR              = 0.10
- DISCRIMINATOR_SMOKE_FLOOR = 0.60 at (SMOKE_K=1000)
    - Rationale: SMOKE_K=1000 mid-cliff-band per full-K probe.
      Floor at 0.60 lets smoke fire cleanly while catching case where
      cliff moved unexpectedly.

## VERDICT GATES

- **HARD_PASS:** K_of_mechanism_death identified (some K in axis where
  arms_diff drops below 0.30) AND K=50 floor met AND cv<10% at all
  high-signal K's AND no regime flip.
- **HARD_FAIL:** (a) all K dead, (b) all K saturated, (c) any regime flip.
- **MIDDLE_BAND:** transition observed but cv gate violated OR K=50 floor
  not met OR partial coverage.

## CARDINALITY

- CARDINALITY_OK_FULL  = 1500 records per seed (5 K x 3 arms x 100 q)
- CARDINALITY_OK_SMOKE = 300 records per seed (1 K x 3 arms x 100 q)
- EXPECTED_N_UNITS     = 5 (META_RULE_H sweep-axis discipline)
- HARD_FAIL_CARDINALITY_BREACH: observed K count != 5 in FULL aggregate

## SMOKE DISCIPLINE

- SMOKE_K = 1000 (mid-cliff-band per full-K probe)
- N_DIM_SMOKE = 8192 (== FULL; discriminator-must-survive-scale)
- N_QUERIES_SMOKE = 100 (== FULL; same statistical power)
- V_ENTS_POOL_SMOKE = 2200 (== FULL)
- Discriminator: TV(K=1000) < 0.60 AND TV >= RV - 0.05

**SMOKE RESULT (executed 2026-07-01 seed_7):** FIRED. TV(K=1000)=0.260 < 0.60
floor. arms_diff=0.26. Elapsed 4.43s. Cardinality observed=300 expected=300 OK.

## PRIOR-WORK CHECK (substrate-KB concept-query 2026-07-01)

Query: "TASK_VECTOR HRR ICL K-cliff extended" -> top hits at cosine=0.21-0.23.
Filesystem shows `_substrate_task_vector_K_extended_v1_core.py` (2026-06-30
referent, K={50,100,200,500,1000}). THIS cell revises axis to
{50,200,500,1000,2000} to straddle the actual cliff at K~1200-2000, and
lifts V_ENTS_POOL from 1000 to 2200 to accommodate K=2000. Genuinely novel
axis coverage (extended range) + confirming referent's floor regime.

## DISPATCH

- SMOKE: local_cpu_queue (single-point K=1000, seed_7 only) - EXECUTED,
  FIRED at TV=0.260 < 0.60 floor.
- FULL: overnight_queue (GPU-eligible per matmul at K=2000; 2000-vec
  bundle FFT + 100-query x 2200-entity cosine per K point).
- Timeout budget FULL: 600s per sibling (5 K x 100 q x 1 seed; smoke was
  4.43s; scaling ~5-8x for K=2000 point + 1.5x wall-safety margin).

## ASCII-only. Cell-author: exp_dev (agent-spawn) 2026-07-01
