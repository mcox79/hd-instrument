# Prereg: substrate_hypothesis_gen_pipeline_composition_v2 (phase-fill extension)

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M)
**Anchor family:** substrate_hypothesis_gen_pipeline_composition_v2_seed_{7,13,19}
**Parent:** substrate_hypothesis_gen_pipeline_composition_v1 (smoke HARD_PASS PIPELINE=0.680 lift=+0.560 N=2048 V=256 prob=50; FULL queued never landed)
**Stage:** Stage 3 (compositional understanding; M3 concern #1 hypothesis generation)

---

## WHY v2 (phase-fill extension)

v1 showed +0.56 composition lift at ONE phase point (M_OBS=5, K_CANDS=10). Two open questions:

1. **Does composition value-add hold across the phase diagram** (sweep M_OBS and K_CANDS) or is +0.56 lift a single-point artifact?
2. **Does adding more chain-grade primitives (cleanup + schema retrieval) further extend the lift**, or is SWR-preplay + bayes_update_categorical already saturating the gain?

v2 extends v1 by:
- **Phase axes:** M_OBS in {3, 5, 8, 12} x K_CANDS in {5, 10, 20, 40} = 16 phase points per seed per arm.
- **Pareto-AUC discriminator:** integrated PIPELINE_FULL_PLUS top-1 vs max(GEN_ONLY, SCORER_ONLY) across the 16 points (METRIC = area under PIPELINE-vs-baseline curve over M_OBS axis at each K, averaged across K).
- **Extended pipeline arm:** ARM_PIPELINE_FULL_PLUS = SWR-preplay + iterative_cleanup (between propose & score) + schema-prior bayes_update_categorical.

---

## ARMS (6; META_RULE_AF arms-must-differ by SHA-256)

| Arm | Generator | Cleanup | Schema Prior | Scorer | Purpose |
|---|---|---|---|---|---|
| ARM_PIPELINE_FULL_PLUS | SWR-preplay | iterative_cleanup | schema-derived prior | bayes_update_categorical | The v2 extended pipeline |
| ARM_PIPELINE_V1 | SWR-preplay | none | uniform prior | bayes_update_categorical | v1 baseline (composition value-add reference) |
| ARM_GENERATOR_ONLY | SWR-preplay | none | uniform prior | uniform-pick (no scoring) | Generator-alone |
| ARM_SCORER_ONLY | random HRR codewords | none | uniform prior | bayes_update_categorical | Scorer-alone |
| ARM_RANDOM_CANDIDATES | random HRR codewords | none | uniform prior | uniform-pick | Floor |
| ARM_ORACLE | true_h injected as 1-of-K | none | uniform prior | bayes_update_categorical | Ceiling |

**META_RULE_AM check (v2 extension value-add):** if PIPELINE_FULL_PLUS <= PIPELINE_V1 + 0.05 across phase axes, the cleanup + schema-prior additions add no functional value beyond v1 + bayes.

---

## ADDED PRIMITIVES (chain-grade composables)

**Cleanup (between propose and score):**
- `hdlab.iterative_attractor.iterative_cleanup` (CERT chain-grade-eligible; mech-5 brain-inspired)
- Each SWR-preplay candidate is passed through soft attractor with the obs_bank as codebook + temp=2.0 + max_steps=4. Pulls candidates toward the nearest stored item along the substrate's attractor basin.

**Schema retrieval (per-candidate prior):**
- Build schema HRR S = sum_{i<j} normalize(bind(obs_i, obs_j)) over all obs-pair binds.
- Per-candidate prior weight pi_k = max(cos(cand_k, S), 0)^2 (then normalized).
- Schema-derived prior is the Bayes prior into `bayes_update_categorical` (vs uniform 1/K in v1).

---

## METRIC

For each (M_OBS, K_CANDS) phase point and arm:
- top-1 hit rate = (1/N_PROBLEMS) * sum_i I[cos(top1_cand_i, true_h_i) >= COS_HIT=0.70]

Pareto-AUC discriminator (per arm, per seed):
- For each K in {5,10,20,40}: compute mean top-1 across M_OBS in {3,5,8,12} (the M-axis curve).
- PARETO_AUC[arm] = mean across K of (mean top-1 across M).
- This is "integrated phase-fill performance" averaged across the phase diagram.

---

## HARD_PASS (ALL must hold per seed)

- PARETO_AUC[ARM_PIPELINE_FULL_PLUS] >= PARETO_AUC[ARM_PIPELINE_V1] + 0.05  (v2-extension value-add)
- PARETO_AUC[ARM_PIPELINE_FULL_PLUS] >= max(PARETO_AUC[GEN_ONLY], PARETO_AUC[SCORER_ONLY]) + 0.15  (v1 composition lift preserved across phase diagram)
- PARETO_AUC[ARM_PIPELINE_FULL_PLUS] in [0.30, 0.95]  (META_RULE_AG un-saturated)
- PARETO_AUC[ARM_ORACLE] > PARETO_AUC[ARM_PIPELINE_FULL_PLUS]  (ceiling not breached)
- PARETO_AUC[ARM_RANDOM_CANDIDATES] <= 0.05  (floor)
- arms_distinct == True (per-arm top-1 fingerprints differ via SHA-256)
- cardinality_ok == True (observed == EXPECTED_N_UNITS)
- discriminator_survives_scale: at LEAST 3 of 4 K values must show PIPELINE_FULL_PLUS > max(GEN, SCORER) + 0.10  (no single-K phantom)

## MIDDLE_BAND

- v2 lift in [0.00, 0.05) OR v1 lift in [0.05, 0.15) OR Pareto-AUC in [0.20, 0.30) OR oracle-pipeline gap < 0.05
- ANY 1 of 4 K values does not satisfy discriminator_survives_scale (single-K weakness; bandable)

## HARD_FAIL (ANY triggers)

- PARETO_AUC[ARM_PIPELINE_FULL_PLUS] <= PARETO_AUC[ARM_PIPELINE_V1]  (v2 extension HURTS or is no-op; cleanup+schema add no value -> v1 is the answer)
- PARETO_AUC[ARM_PIPELINE_FULL_PLUS] <= max(GEN_ONLY, SCORER_ONLY)  (META_RULE_AM functional-req-already-met)
- PARETO_AUC[ARM_PIPELINE_FULL_PLUS] < 0.20  (worse than reasonable for K_CANDS<=40)
- PARETO_AUC[ARM_RANDOM_CANDIDATES] > 0.10  (floor breach)
- PARETO_AUC[ARM_ORACLE] < 0.85  (ceiling broken; scoring fundamentally fails)
- META_RULE_Q suspect-1.000 on n>=100 (any non-oracle arm at 1.000 across phase diagram with n>=100)
- arms_distinct == False
- cardinality_ok == False

---

## CARDINALITY (META_RULE_H)

Per seed: 6 arms x 16 phase points x N_PROBLEMS top-1 decisions.

- SELF-TEST: 6 arms x 4 phase points (sub-grid) x 4 problems = 96 decisions
- SMOKE: 6 arms x 4 phase points (M_OBS in {3,5,8}, K_CANDS in {5,10}; 6 cells) x 30 problems = 6 x 6 x 30 = 1080 decisions
- FULL: 6 arms x 16 phase points x 100 problems = 9600 decisions

**EXPECTED_N_UNITS** computed at module init per run-mode; HARD_FAIL_CARDINALITY_BREACH when observed != expected.

(Smoke uses 6 phase points to validate discriminator across scale per feedback_discriminator_must_survive_scale; smoke at M_OBS in {3,5,8} x K_CANDS in {5,10}.)

---

## CHUNKED ARCHITECTURE (3 seeds per USER 2026-06-28)

3 sibling cells:
- `experiments/exp_substrate_hypothesis_gen_pipeline_composition_v2_seed_7.py` (smoke gate)
- `experiments/exp_substrate_hypothesis_gen_pipeline_composition_v2_seed_13.py`
- `experiments/exp_substrate_hypothesis_gen_pipeline_composition_v2_seed_19.py`

Each self-contained; uses `_seed_checkpoint.py` write_partial; aggregation across the 3 seeds for chain-grade promotion via Skunkworks.

---

## CONFIG

| Param | SELF-TEST | SMOKE | FULL |
|---|---|---|---|
| N_DIM | 256 | 2048 | 8192 |
| V_BANK | 64 | 256 | 256 |
| N_PROBLEMS per phase point | 4 | 30 | 100 |
| Phase points (M_OBS x K_CANDS) | 4 (M in {3,5}, K in {5,10}) | 6 (M in {3,5,8}, K in {5,10}) | 16 (M in {3,5,8,12}, K in {5,10,20,40}) |
| COS_HIT | 0.70 | 0.70 | 0.70 |
| iterative_cleanup temp | 2.0 | 2.0 | 2.0 |
| iterative_cleanup max_steps | 4 | 4 | 4 |

---

## DISPATCH

- Self-test gate: tiny config, must PASS (verdict SELFTEST_OK).
- Smoke: laptop local (~3-5 min per seed; one seed locally as gate).
- If HARD_PASS smoke: 3 FULL chunked cells -> overnight_queue (matmul-heavy: 16 phase points x 100 problems x 6 arms with N=8192 attractor cleanup; ~6 GB matmuls expected).
- FULL push via hd_metrics_sync (NOT exp_dev; orchestrator's job per harness-DENIED push constraint).
- Per-experiment --timeout: formula = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^1.5 * (FULL_prob/smoke_prob) * (FULL_phase/smoke_phase)).

---

## DISCIPLINE TAGS

- META_RULE_AC: HYPOTHESIZED@ thresholds locked at module init
- META_RULE_AE: absolute paths only
- META_RULE_AF: arms_distinct SHA-256
- META_RULE_AG: edge-of-capacity (PIPELINE_FULL_PLUS Pareto-AUC band 0.30-0.95)
- META_RULE_AH: atomic .tmp + os.replace write
- META_RULE_AM: v2-extension value-add check (lift over v1 + lift over primitives)
- META_RULE_H: cardinality_ok with EXPECTED_N_UNITS sweep-aware computation
- META_RULE_Q: suspect-1.000 on n>=100 halt
- feedback_discriminator_must_survive_scale: smoke discriminator across M and K axes
- ASCII-only; no unicode; no emojis; no em-dashes
