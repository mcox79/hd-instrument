# Prereg: substrate_hypothesis_gen_pipeline_composition_v1

**Date:** 2026-06-28
**Author:** exp_dev (Opus 4.7 1M; functional-requirement-first cell-author cycle)
**Anchor:** substrate_hypothesis_gen_pipeline_composition_v1
**Stage:** Stage 3 (compositional understanding / M3 concern #1: hypothesis generation)
**Cap_map:** M3 concern #1 = hypothesis generation; functional-requirement-first composition test

---

## FUNCTIONAL-REQUIREMENT-FIRST DECOMPOSITION (per feedback_functional_requirement_first_test_design_USER_2026-06-28)

Hypothesis generation, decomposed into operational sub-functions:

1. **PROPOSE** candidate hypotheses given observation.
2. **SCORE** candidates against truth/plausibility (rank, select top-1).

Both functional requirements have existing chain-grade or HARD_PASS-on-smoke substrate primitives:

| Function | Primitive (existing) | Status | Path |
|---|---|---|---|
| PROPOSE (candidate generation) | `exp_swr_preplay_constructive_hypothesis_generator_v1` ARM_PREPLAY_FULL | smoke MEASURED@recall@10=0.570 novelty=1.000 (HARD_PASS conditions partial); full HARD_FAIL on pipeline_top1<0.15 | MEASURED@`data/exp_swr_preplay_constructive_hypothesis_generator_v1_smoke/metrics.json` |
| SCORE (abductive ranking) | `hdlab/bayesian_inference.py::bayes_update_categorical` (lap8 / comp21 / stretch3-4 chain-grade) | MEASURED@HARD_PASS (lap8 bayes_acc=1.0 n=33; comp21 L3=1.000; stretch3_4 posterior-match=0.987 n=150) | MEASURED@`data/exp_lap8_bayesian_fhrr_cpu_v1/metrics.json` + `data/exp_comp21_bayesian_at_l3_cpu_v1/metrics.json` |

**META_RULE_AM check (composition-value-add):** if PIPELINE_FULL <= max(GENERATOR_ONLY, SCORER_ONLY), the substrate already meets M3 concern #1 via either primitive alone, and composition is functional-requirement-already-met (no novel mechanism load-bearing).

**Distinction from prior SWR cell's ARM_GEN_SCORE_PIPELINE:** that arm uses the in-cell `bayes_score_top1_fn` (unbind-cue + pair-consistency on raw HRR bind-set). This cell uses categorical Bayes (`bayes_update_categorical`) over likelihoods derived from substrate role-binding to a per-candidate frame — a DIFFERENT abductive scorer matching the lap8/comp21 chain-grade pattern.

---

## ARMS (5; META_RULE_AF arms-must-differ by SHA-256)

| Arm | Generator | Scorer | Purpose |
|---|---|---|---|
| ARM_PIPELINE_FULL | SWR-preplay (bind-noise replay; K=10 candidates) | bayes_update_categorical over likelihoods=cos(cand_k, evidence)^2 with HRR-complexity prior | The proposed pipeline (PROPOSE + SCORE) |
| ARM_GENERATOR_ONLY | SWR-preplay (K=10) | uniform-pick from K candidates (NO scoring; top-1 = arbitrary first) | Tests: does substrate's generator alone give usable top-1? |
| ARM_SCORER_ONLY | random HRR codewords (K=10 random; non-generative) | bayes_update_categorical (same as PIPELINE) | Tests: is the scorer alone the value-add? |
| ARM_RANDOM_CANDIDATES | random HRR codewords (K=10) | uniform-pick (NO scoring) | Floor baseline (no generator, no scorer) |
| ARM_ORACLE | true_h itself injected as 1 of K candidates | bayes_update_categorical | Saturation comparator (ceiling) |

**META_RULE_AA non-abductive baseline:** ARM_RANDOM_CANDIDATES and ARM_GENERATOR_ONLY both use uniform-pick (no likelihood, no prior) — they are NON-scoring baselines. ARM_SCORER_ONLY uses random candidates so the scorer has nothing meaningful to rank — tests if scorer alone is load-bearing.

---

## METRIC

Per arm: **top-1 hit rate** = (1/N_PROBLEMS) * sum_i I[cos(top1_cand_i, true_h_i) >= COS_HIT=0.70].

---

## HARD_PASS (ALL must hold)

- ARM_PIPELINE_FULL top-1 > max(ARM_GENERATOR_ONLY, ARM_SCORER_ONLY) by >= +0.15 absolute  (META_RULE_AM composition value-add)
- ARM_PIPELINE_FULL top-1 in [0.30, 0.95]  (META_RULE_AG un-saturated)
- ARM_ORACLE top-1 > ARM_PIPELINE_FULL  (room to grow; sanity)
- ARM_RANDOM_CANDIDATES top-1 <= 0.05  (floor sanity)
- arms_distinct == True (SHA-256 of per-arm cand fingerprints differ)
- cardinality_ok == True (observed == EXPECTED_N_UNITS)
- cv across seeds < 0.20  (smoke: single seed per chunk; cv computed at aggregation)

## MIDDLE_BAND

- composition lift in [0.05, 0.15) OR PIPELINE_FULL in [0.20, 0.30) OR ORACLE-PIPELINE gap < 0.05

## HARD_FAIL (ANY triggers)

- ARM_PIPELINE_FULL top-1 <= max(GENERATOR_ONLY, SCORER_ONLY)  (META_RULE_AM: substrate already does this via existing primitive alone; functional-requirement-already-met — composition adds no value)
- ARM_PIPELINE_FULL top-1 < 0.20  (worse than reasonable for K=10)
- ARM_RANDOM_CANDIDATES top-1 > 0.10  (floor breach; suspect leak)
- ARM_ORACLE top-1 < 0.90  (ceiling didn't fire; scoring broken)
- META_RULE_Q suspect-1.000 on n>=100: any arm at 1.000 on n>=100 -> halt
- arms_distinct == False
- cardinality_ok == False

---

## CARDINALITY (META_RULE_H)

- SMOKE per seed: 5 arms * 50 problems * 10 candidates = 2500 candidate events; EXPECTED_N_UNITS = 5 * 50 = 250 top-1 decisions per seed
- FULL per seed: 5 arms * 200 problems * 10 candidates = 10000 events; EXPECTED_N_UNITS = 5 * 200 = 1000 top-1 decisions per seed
- HARD_FAIL_CARDINALITY_BREACH when observed != expected

---

## CHUNKED ARCHITECTURE (single-seed-per-cell per USER 2026-06-28 directive)

3 sibling cells:
- `experiments/exp_substrate_hypothesis_gen_pipeline_composition_v1_seed_7.py`  (this prereg's primary; smoke gate)
- `experiments/exp_substrate_hypothesis_gen_pipeline_composition_v1_seed_13.py`
- `experiments/exp_substrate_hypothesis_gen_pipeline_composition_v1_seed_19.py`

Each self-contained; uses `_seed_checkpoint.py` write_partial; aggregation across the 3 seeds for chain-grade promotion via Skunkworks.

---

## CONFIG

| Param | SMOKE | FULL |
|---|---|---|
| N_DIM | 2048 | 8192 |
| V_BANK (stored items) | 256 | 256 |
| N_PROBLEMS | 50 | 200 |
| K_CANDS | 10 | 10 |
| M_OBS | 5 | 5 |
| COS_HIT | 0.70 | 0.70 |
| COS_NOVEL | 0.50 | 0.50 |

---

## DISCIPLINE TAGS

- META_RULE_AC: HYPOTHESIZED@ thresholds locked at module init; MEASURED@ tags on prior atoms
- META_RULE_AE: absolute paths only
- META_RULE_AF: arms_distinct SHA-256
- META_RULE_AG: edge-of-capacity (PIPELINE_FULL band 0.30-0.95)
- META_RULE_AH: atomic .tmp + os.replace write
- META_RULE_AM: composition value-add check (lift over BOTH primitives alone)
- META_RULE_Q: suspect-1.000 on n>=100 -> halt
- ASCII-only; no unicode; no emojis; no em-dashes

---

## DISPATCH

- Smoke (seed_7): local_cpu_queue (~5-10 min); ship as `substrate_hypothesis_gen_pipeline_composition_v1_seed_7_smoke`
- If HARD_PASS smoke: 3 chunked FULL cells -> remote_cpu_queue with 4500s timeout each

---

## M3 IMPLICATION

If PIPELINE_FULL > max(GEN_ONLY, SCORER_ONLY) by >= +0.15: composition is the load-bearing answer to M3 concern #1.
If PIPELINE_FULL <= max(GEN_ONLY, SCORER_ONLY): the existing primitive alone already meets the functional requirement — M3 concern #1 dissolves into existing chain-grade capability.
If both PIPELINE and primitives all <0.30: substrate cannot generate viable hypotheses at this regime — M3 concern #1 remains open; need different decomposition.
