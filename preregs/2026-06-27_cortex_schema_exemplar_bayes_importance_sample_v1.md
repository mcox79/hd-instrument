# PRE-REG: cortex_schema_exemplar_bayes_importance_sample_v1

**Date:** 2026-06-27
**Author:** exp_dev (Opus 4.7-1M agent spawn, Research team-lead dispatch)
**Barrier:** B3 (cortex schema instantiation Stage 3) — INFERENCE-side
**Drill:** notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md TOP-3
**Handoff:** notes/exp_dev_handoff_research_schema_driven_inference_stage3_2026-06-27.md ANCHOR 3
**Source-lit anchor:** Shi, Griffiths, Feldman, Sanborn (2010) "Exemplar models as a mechanism for performing Bayesian inference." Psychon Bull Rev 17(4):443.

## ROLE IN PROGRAM

CHEAP UPPER-BOUND FALSIFIER for the schema-inference branch.
- If HARD_FAIL: substrate cosine kernel cannot support posterior-style slot inference → ANCHOR 1 (context-bound prior) + ANCHOR 2 (MAC/FAC) unlikely to pass (cone-geometry confound). REDIRECT research to richer encoders (Path C substrate-owned predictive coding) BEFORE investing in richer mechanisms.
- If HARD_PASS: substrate cosine geometry is rich enough; ANCHOR 1+2 with structural binding should pass at HIGHER accuracy. GREEN-LIGHT for ANCHOR 1 dispatch.
- If MIDDLE_BAND: signal present but bounded; ANCHOR 1+2 worth trying but expect modest lift.

## MECHANISM (Shi-Griffiths-Feldman 2010 mathematical equivalence)

Exemplar memory IS importance sampling:
```
P(slot_value | observed) approx sum_i w_i * delta(slot_value, exemplar_i.slot)
w_i = sim(observed, exemplar_i) / sum_j sim(observed, exemplar_j)
```
Substrate cosine kernel = the kernel. No prototype required. No HRR bind required (those are ANCHOR 1+2 richer mechanisms).

## DATA (synthetic concept hierarchy, dependency-free)

- 8 schemas (BIRD / FISH / MAMMAL / REPTILE / INSECT / TREE / FLOWER / FUNGUS)
- 6 typed slots per schema (HABITAT / DIET / SIZE / COVERING / MOVEMENT / REPRO)
- V_SLOT = 8 fillers per slot type (categorical)
- 20 exemplars per schema (160 atoms total in exemplar bank)
- FILLER_NOISE = 0.20 (each exemplar follows schema default 80% of time per slot; perturbed to non-default 20%)
- N_DIM = 2048 (drill recommendation; cone-geometry honest regime)

Encoding: per-slot, V_SLOT random L2-normalized N-dim filler atoms. Exemplar vector = L2-normalized sum over 6 slot-filler-vectors. Query vector = L2-normalized sum over ONLY the OBSERVED slots (3 of 6).

Queries DISJOINT from exemplars (BIAS-7 anti-contamination): separate seed for query generation; novel inputs drawn from same schema-default distribution but independently sampled.

## INFERENCE TASK

Given novel partial input with M=6 slots: 3 OBSERVED, 3 MASKED. Predict the value of each masked slot. Metric: recall@1 over MASKED slots only.

## ARMS (6)

1. **ARM_NO_SCHEMA_BASELINE** — predict masked slot = popularity mode over ALL exemplars; ignores observed slots and schema. Expected ~ 1/V_SLOT = 0.125.
2. **ARM_RANDOM_K_EXEMPLARS** — pick K=20 RANDOM exemplars; uniform vote per masked slot. CONTROL: distinguishes "cosine signal" from "K averaging". Expected ~ 1/V_SLOT.
3. **ARM_K_NEAREST_K5** — K=5 nearest by cosine; softmax-weighted vote at beta=8.
4. **ARM_K_NEAREST_K20** — K=20 nearest by cosine; softmax-weighted vote at beta=8. **PRIMARY ARM.**
5. **ARM_K_NEAREST_K50** — K=50 nearest by cosine; softmax-weighted vote at beta=8.
6. **ARM_ORACLE_TRUE_SCHEMA** — predict slot = schema_default[slot]; upper bound (limited by FILLER_NOISE).

ARMS-MUST-DIFFER SHA-256 self-test on prediction matrices (META_RULE_AF). All 6 distinct or HARD_FAIL.

## PRE-REG BANDS

**HARD_PASS:**
- ARM_K_NEAREST_K20 mean recall@1 >= 0.50
- ARM_K_NEAREST_K20 - ARM_NO_SCHEMA_BASELINE >= +0.30 (cosine signal is the lever)
- ARM_K_NEAREST_K20 - ARM_RANDOM_K_EXEMPLARS >= +0.30 (signal not just K averaging)
- cv across seeds < 0.15 (n=3 smoke; n=5 full)
- arms_differ_verified = True
- cardinality_ok = True

**MIDDLE_BAND:**
- ARM_K_NEAREST_K20 in [0.20, 0.50] with cv<0.15
- Cosine signal present but bounded (cone-geometry partial pass).

**HARD_FAIL:**
- ARM_K_NEAREST_K20 <= ARM_NO_SCHEMA_BASELINE + 0.05 (kernel doesn't support inference)
- ARM_K_NEAREST_K20 < ARM_RANDOM_K_EXEMPLARS (random equals signal — substrate broken)
- ARM_ORACLE_TRUE_SCHEMA <= 0.70 (oracle pipeline broken)
- ANY non-oracle arm > 0.95 absolute (FAIRNESS_VIOLATION; regime too easy)
- cv >= 0.15 (instability)
- cardinality breach (events < 0.85 * expected)
- arms not distinct (SHA-256 collisions)

## CRLB PRE-VALIDATION (BIAS master checklist N)

N=2048, V_SLOT=8 categorical. Per-slot accuracy variance under chance:
- var = p(1-p)/n_trials = 0.125 * 0.875 / 240 = 4.56e-4; sd ≈ 0.021
- HP discriminator = +0.30 lift over baseline → 14× CRLB noise floor → REACHABLE.

## DISCRIMINATOR_MUST_SURVIVE_SCALE (per feedback-discriminator-must-survive-scale)

Smoke at N=2048 (SAME N_DIM as full). Strategy A: smoke at full-N, smaller n_seeds + queries. So smoke recall directly predicts full recall modulo seed variance.

## CARDINALITY_OK

- EXPECTED_N_UNITS_SMOKE = 6 arms × 3 seeds × 240 queries × 3 masked = 12,960 events
- EXPECTED_N_UNITS_FULL = 6 arms × 5 seeds × 800 queries × 3 masked = 72,000 events
- HARD_FAIL if observed < 0.85 * expected.

## FAIRNESS RAILS

1. **Separate W per arm** — N/A (arms differ in algorithm, not in encoding W).
2. **BIAS-7 contamination** — queries drawn from disjoint seed (seed+4049) vs exemplar bank (seed+3037).
3. **BIAS-Q suspect 1.000** — any non-oracle arm > 0.95 → FAIRNESS_VIOLATION.
4. **BIAS-15 relative bands** — lift over BOTH baseline AND random_K is the discriminator (not absolute).
5. **Smoke FIRES discriminator** — smoke regime matches full N_DIM, so HARD_PASS / HARD_FAIL determinable at smoke.

## REGIME

- N_DIM = 2048
- V_SLOT = 8 fillers per slot
- M_SLOTS = 6 typed slots
- K_SCHEMAS = 8
- N_EXEMPLARS_PER_SCHEMA = 20
- FILLER_NOISE = 0.20
- MASK_FRACTION = 0.50 (3 of 6 slots masked per query)
- K_NEAREST_VARIANTS = (5, 20, 50)
- BETA_TEMP = 8.0 (softmax inverse-temperature)
- Smoke: n_seeds=3, N_QUERIES_PER_SCHEMA=30 → 240 queries × 8 schemas = 1920 inference events/arm
- Full: n_seeds=5, N_QUERIES_PER_SCHEMA=100 → 800 queries × 8 schemas = 4000 inference events/arm

## COMPUTE BUDGET

- Selftest: ~15 sec (N=512, 1 seed, 5 exemplars/schema)
- Smoke: ~15-20 min CPU (3 seeds × N=2048 × cosine over 160 exemplars × 240 queries)
- Full: ~1-2 CPU-hr (5 seeds × N=2048 × cosine over 160 exemplars × 800 queries)

## ROUTING

- Selftest + smoke: laptop CPU (CPU-friendly cosine; 160-row matrix; cheap)
- Full: remote_cpu_queue via hdi_orchestrator per [[feedback-cell-author-smoke-and-dispatch-route-via-orchestrator-for-heavy-cells]] AND [[feedback-no-experiments-local]]

## ABSOLUTE PATHS

- Cell: `d:/AI/hd-instrument/experiments/exp_cortex_schema_exemplar_bayes_importance_sample_v1.py`
- Prereg: `d:/AI/hd-instrument/preregs/2026-06-27_cortex_schema_exemplar_bayes_importance_sample_v1.md`
- Smoke metrics path: `d:/AI/hd-instrument/data/exp_cortex_schema_exemplar_bayes_importance_sample_v1_smoke/metrics.json`
- Full metrics path: `d:/AI/hd-instrument/data/exp_cortex_schema_exemplar_bayes_importance_sample_v1/metrics.json`
- Drill source: `d:/AI/hd-instrument/notes/research_drill_2x_schema_driven_inference_stage3_2026-06-27.md`
- Handoff: `d:/AI/hd-instrument/notes/exp_dev_handoff_research_schema_driven_inference_stage3_2026-06-27.md`
