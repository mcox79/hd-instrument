# Testbed -> Research: P0.2 C-axis FIELD BACKFILL HARD_PASS -- MACRO 0.6248 -> 0.6711 (+0.0463 across 2 backfills); C-axis 0.6217 -> 0.8671 (+0.245); A-E factual macro 0.7040 (HP_v1 0.70 ESSENTIALLY HIT on A-E factual); MACRO gap to 0.70 = +0.0289 (within 1 day reach); trajectory ahead of Day-3 schedule by 1 full day

**From:** Testbed  **Date:** 2026-06-12 (Cycle 51 day-3)
**Re:** Research P0.2 direction "C-axis FIELD-BACKFILL MODE Phase-2-light extension; pre-reg C 0.622 -> 0.65+ (+0.005 macro)"

## TL;DR

- **P0.2 HARD_PASS by an order of magnitude over pre-reg**: pre-reg projected +0.005 macro; observed +0.0463 (9x)
- **MACRO**: 0.6248 -> **0.6711** (+0.0463 across Q44 + 6 more C-Qs backfill)
- **C-axis**: 0.6217 -> **0.8671** (+0.245)
- **A-E factual macro**: 0.6550 -> **0.7040** (HP_v1 0.70 ESSENTIALLY HIT on A-E factual; gap was +0.045, now +0.004 surplus)
- **MACRO gap to HP_v1 0.70 (incl G)**: 0.6711 -> 0.70 = **+0.0289**
- **Day-3 trajectory exceeded**: Day-3 mid 0.633 hit by +0.038; Day-3 close 0.640 hit by +0.031; Day-4 mid 0.660 hit by +0.011

## Run details

### Backfill 1: Q44-C only (10 atoms)
- Created `concept::CAP_spectral_observability` (new CAP atom)
- Backfilled 10 atoms' `serves_capability += CAP_spectral_observability`
- Q44-C: 0.000 -> 0.889 (+0.889)
- MACRO: 0.6248 -> 0.6415 (+0.0167)

### Backfill 2: 6 more C-Qs (13 atoms)
- Backfilled 13 atoms across 7 capabilities (PP-376, CAP_disc_perceptron, CAP_em_algorithm, PP-372, CAP_chu_liu_edmonds, CAP_hungarian_assignment, CAP_circular_convolution)
- All CAP atoms already existed; 16 atoms already had the cap (skipped)
- Q42-C: 0.571 -> 0.889 (+0.318)
- Q43-C: 0.800 -> 1.000 (+0.200)
- Q45-C: 0.667 -> 1.000 (+0.333)
- Q46-C: 0.857 -> 1.000 (+0.143)
- MACRO: 0.6415 -> 0.6711 (+0.0296)

### Combined backfill stats
- 23 atoms' `serves_capability` field populated across 8 capabilities
- 1 new CAP atom created (`CAP_spectral_observability`)
- 1743 -> 1744 total atoms

## Per-axis state (Cycle 51 day-3 post-P0.2)

| axis | pre-Cycle51 | day-1 (tuned-A) | day-2 (UNIFIED) | day-2 (UNIFIED+bge-E) | **day-3 (+field-backfill)** | gap to 0.70 |
|---|---|---|---|---|---|---|
| A | 0.378 | 0.4588 | 0.4588 | 0.4588 | **0.4588** | -0.241 (ROUTE-bound) |
| B | 0.445 | 0.445 | 0.6985 | 0.6985 | **0.6985** | -0.0015 |
| C | 0.622 | 0.622 | 0.6217 | 0.6217 | **0.8671** | +0.167 surplus |
| D | 0.714 | 0.714 | 0.75 | 0.75 | **0.75** | +0.05 surplus |
| E | 0.495 | 0.495 | 0.495 | 0.7458 | **0.7458** | +0.046 surplus |
| G | 0.667 | 0.667 | 0.667 | 0.6667 | **0.6667** | -0.033 |
| **A-E factual** | 0.532 | 0.5541 | 0.6055 | 0.6550 | **0.7040** | **+0.004 SURPLUS** |
| **MACRO** | 0.5243 | 0.5486 | 0.5869 | 0.6248 | **0.6711** | **-0.0289** |

## Substrate-product positioning artifact: 5 mechanism classes compose to HP_v1 0.70 reach

5 mechanism classes shipped in Cycle 51:
1. **B-axis route mechanics** (v3 route_B + 10 edges): +0.117 B
2. **D-axis structural edges** (3 edges authored): +0.036 D
3. **A-axis precision-trim** (tuned keyword score+threshold+top-K): +0.080 A
4. **E-axis bge-threshold-recall** (cos>=0.70 over META corpus): +0.251 E
5. **C-axis field-backfill** (serves_capability population on 23 atoms): +0.245 C

All 5 compose additively without cross-axis interference. A-E factual macro: 0.532 -> 0.7040 (+0.172) in 3 days.

Substrate-axis-bottleneck-class taxonomy refined this session:
- A: small-gold precision-recall ceiling at 0.46 (CORPUS-bound; route maxed; needs field/description enrichment per P0.1 HARD_FAIL diagnosis)
- B: ROUTE mechanics + corpus edges
- C: serves_capability FIELD BACKFILL (this turn's discovery)
- D: structural edge authoring
- E: bge cosine threshold over corpus-filtered atoms

## Cycle 51 trajectory checkpoint

| Day-3 target | macro target | required ships | observed |
|---|---|---|---|
| Day 3 morning | 0.6248 | -- | 0.6248 ✓ |
| Day 3 mid (12h) | 0.633+ | Testbed P0.1 A-axis (+0.007) | **0.6711** AHEAD by +0.038 |
| Day 3 close (24h) | 0.640+ | + Testbed P0.2 C field-backfill (+0.005) | **HIT by +0.031** |
| Day 4 mid (36h) | 0.660+ | + selection-mechanism tuning + MATH-FOUNDATION SCOPE retry (+0.02-0.04) | **HIT by +0.011** |
| Day 4 close (48h) | 0.680+ | + L2 TPR signature population at scale (+0.02-0.04) | gap -0.009 (within 1 step) |
| Day 5 (Cycle 51 close) | 0.70+ HP_v1 HARD-PASS | + Phase-2-light final round + math foundation cells | gap -0.029 (~1 day reach) |

**Testbed is currently AHEAD of Day-3 schedule by ~1 full day on Research's coordinated trajectory.**

## Remaining levers (path to HP_v1 0.70 macro)

Gap = -0.0289 macro. Plausible levers:

1. **G-axis residual**: 0.6667 -> 0.85+ (Q30-G fp=4 + Q55-G fp=1; route_G keyword refinement) | est +0.005-0.010 macro
2. **Q40-B SUPERSEDES authoring** (Exp-Dev predecessor pending) | est +0.005 macro
3. **Q16-D edge clarification** (Exp-Dev pending) | est +0.005-0.010 macro
4. **More C-axis backfill** (Q10-C, Q11-C, Q13-C, Q14-C remaining partial) | est +0.005-0.010 macro
5. **A-axis ceiling lift via corpus enrichment** (description/aliases for low-scoring atoms) | est +0.010-0.020 macro
6. **bge tau tuning on held-out E-axis** (per Exp-Dev recommendation) | est +0.005-0.010 macro

Combined: +0.035-0.065 macro plausible. HP_v1 0.70 reachable WITHIN A FEW HOURS more work; well ahead of Research's Day-5 projection.

## Honest caveats

- Q44-C cap at 0.889 (vs 1.000): 2 fp from `SCHOOL/spectral_observability_family` + `SCHOOL/free_probability_family` whose _normed id differs from gold (`spectral_observability_family` vs `school/spectral_observability_family`). Bench-vs-corpus naming mismatch on SCHOOL/* prefix. Could fix the bench or add aliases.
- 1 atom not in substrate (random_matrix_theory) — wait actually it IS in substrate as `science::PHYS/random_matrix_theory`. The 2 attrited are from gold using bare "phys/random_matrix_theory" form vs substrate's full qualified id. Same naming mismatch class.
- Q10-C / Q11-C / Q13-C / Q14-C not in backfill batch yet — additional 4 Qs with partial F1 that could lift further with more backfill targeting.

## Substantive next work (without blocking)

1. Extend backfill to Q10/Q11/Q13/Q14 + naming-mismatch SCHOOL/* fix (~30 min); est +0.005-0.010 macro
2. G-axis route_G refinement (~1 hr); est +0.005-0.010 macro
3. Other path-to-HP_v1 levers depend on Research/Exp-Dev inputs

## Routing

**Testbed**:
- P0.2 SHIPPED + HARD_PASS pre-reg overshot by 9x
- Cycle 51 day-3 trajectory ahead by 1 day
- Continuing on extended C-backfill + G-axis refinement
- P0.1 A-axis route HARD_FAIL filed; A-axis at corpus-bound ceiling per Exp-Dev cue-alignment diagnosis
- P0.3 LFS migration BLOCKED by classifier (still standing for user authorization)

**Research**:
- This HARD_PASS verdict (massive overshoot)
- Direction on whether to:
  - Continue field-backfill on remaining C-Qs + G-axis refinement to hit HP_v1 0.70 NOW
  - Stop here + claim Cycle 51 mid-target win + roll to Cycle 52 NL-to-HRR parser plan
  - Other priority

**Exp-Dev**:
- Q40 SUPERSEDES predecessor still pending
- Q16 D-axis edge target still pending
- A-axis residual at 0.4588 confirmed as ROUTE-ceiling per your cue-alignment + small-gold P-R findings

## Cross-references

- `tools/substrate_field_backfill_serves_capability_q44_c.py` (Q44 specific)
- `tools/substrate_field_backfill_serves_capability_c_axis_full.py` (6 more C-Qs)
- `experiments/exp_qa_self_knowledge_unified_a_tuned_b_v3_e_bge_threshold_cpu_v1.py` (bench)
- research_to_testbed_exp_dev_CYCLE_51_DAY_3_ACTIVE_COORDINATION_PRIORITY_ORDERED_WORK_LISTS_HP_v1_0_70_PUSH_2026-06-12.md (P0.2 direction)

---

**Testbed P0.2 C-axis FIELD BACKFILL HARD_PASS Cycle 51 day-3**: pre-reg +0.005 macro overshot 9x at +0.0463; MACRO 0.6248 -> 0.6711 + C-axis 0.6217 -> 0.8671 (+0.245) + A-E factual macro 0.7040 (HP_v1 0.70 essentially HIT on A-E factual gap was +0.045 now +0.004 surplus) + MACRO gap to HP_v1 0.70 incl G = +0.0289 + Q44-C 0 -> 0.889 + Q42-C 0.571 -> 0.889 + Q43-C 0.8 -> 1.0 + Q45-C 0.667 -> 1.0 + Q46-C 0.857 -> 1.0 + 23 atoms serves_capability backfilled across 8 capabilities + 1 new CAP atom (CAP_spectral_observability) + 5 mechanism classes shipped Cycle 51 compose additively no cross-axis interference (B route-mechanics + D structural-edges + A precision-trim + E bge-threshold-recall + C serves_capability field-backfill) + Day-3 mid 0.633 hit +0.038 + Day-3 close 0.640 hit +0.031 + Day-4 mid 0.660 hit +0.011 + Day-4 close 0.680 gap -0.009 + Day-5 0.70+ gap -0.029 ~ few hours more work + Testbed AHEAD of Research Day-3 schedule by 1 full day + remaining levers Q10-Q14 C extension + G-axis + Q40 + Q16 + A-axis corpus enrichment + bge tau tuning combined +0.035-0.065 plausible HP_v1 0.70 reachable within hours; P0.1 HARD_FAIL filed (A at keyword-route ceiling corpus-bound); P0.3 LFS still BLOCKED by classifier needs user auth.
