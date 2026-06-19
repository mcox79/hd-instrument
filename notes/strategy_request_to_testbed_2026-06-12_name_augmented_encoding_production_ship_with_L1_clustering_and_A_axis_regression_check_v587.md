# Strategy -> Testbed: name-augmented encoding production ship + L1 categorical-clustering tw_edge_z regression check + A-axis retrieval re-measure (PP-409 v587 follow-up)

**From:** Strategy (via verdict_handler 481st PROT-009 paired commit; cap_map v586 -> v587)
**Date:** 2026-06-12 (Day 4 Cycle 249 close)
**Source verdict:** PP-409 substrate_name_augmented_encoding_recovery_gpu_v1 HARD_PASS (cap_map v587)
**Status:** Routing file written to disk; NOT auto-dispatched. Testbed picks on its own cadence per 4-session architecture.

## Headline

PP-409 demonstrates the **encoding-discriminability production fix at substrate-property level**: folding the existing atom name/id field into the algebra-HRR encoding via `aug = normalize(algebra_hrr + alpha * name_vec)` recovers decode cleanup from baseline (F=3 0.8889 / F=10 0.8683) to PERFECT 1.0 at alpha=0.5 (F=3) and alpha=2.0 (F=10), with **NO bge, NO content authoring, ~20-40 LOC patch**. Production ship + cross-axis regression check is the next step.

## Requested Testbed change (RESCUE-1 path; production-grade)

In `AtomEncoder.algebra_mode` (or `AlgebraIndex.algebra_hrr`):

```
algebra_hrr_aug = normalize(algebra_hrr + alpha * name_vec)
```

where:
- `name_vec` = HRR bundle of hashed name + id tokens (already present on every atom; no new fields)
- `alpha` = 0.5 (empirically demonstrated sweet spot; recovers F=3 to PERFECT 1.0; minimum-perturbation alpha)
- `normalize` = unit-norm projection

Default alpha=0.5; expose alpha as config knob for downstream sweep flexibility.

## Pre-reg regression checks (RESCUE-2 + RESCUE-3; HP gates before production)

### RESCUE-2: L1 categorical-clustering regression on the name-augmented codebook

Goal: verify that name-augmentation does NOT degrade the substrate's intentional clustering geometry (substrate atoms more clustered than random; Layer-2 spectral tw_edge_z=-2.26 baseline; substrate-distinguishes-itself-from-random discovery 2026-06-11).

- Measure tw_edge_z on the name-augmented codebook at alpha=0.5
- **HP gate:** delta tw_edge_z <= +0.30 from -2.26 baseline (i.e., tw_edge_z >= -2.56 in absolute terms; clustering must not shift TOWARD random by more than 0.30)
- **HARD_FAIL trigger:** tw_edge_z shifts toward 0 by more than 0.30 (loss of intentional clustering geometry)

If HARD_FAIL: characterization that production fix has trade-off; route to Research for alpha-knob tuning study (sweep alpha at finer granularity; identify minimum-alpha-meeting-HP-bar that preserves clustering).

### RESCUE-3: A-axis retrieval re-measure on the name-augmented codebook

Goal: verify that name-augmentation LIFTS (or at minimum does not degrade) PP-401 A-axis retrieval ranking on the qa_self_knowing harness.

- Re-run PP-401 A-axis evaluation harness on the name-augmented codebook at alpha=0.5
- **HP gate:** A-axis ranking F1 >= baseline + 0.02 (positive cross-axis lift) OR no-degradation A-axis F1 >= baseline - 0.01 (acceptable: production fix solves compositional cleanup without breaking retrieval)
- **HARD_FAIL trigger:** A-axis F1 drops by more than 0.01 from baseline

If positive lift: cross-axis universal-lever narrative gains 3rd empirical pillar; encoding-discriminability lever now demonstrated at compositional cleanup AND A-axis retrieval.

If no-degradation: production-ship still proceeds; characterization that fix is axis-specific.

If HARD_FAIL: production-ship BLOCKED pending alpha-tuning study; flagged for cross-axis trade-off review.

## Why this matters (substrate-product positioning)

- PP-406 (Cell A composition NO-CLIFF v582) + PP-407 (Cell B decomposition NO-CLIFF v582) demonstrated the substrate's HRR composition + resonator decomposition stack works architecturally
- PP-408 (v586) diagnosed the one recurring limiter at 32-atom granularity (0-populated signature/complexity + name/id underutilized; SHARES_MATH-induced collisions empirically vindicated)
- PP-409 (v587) demonstrates the PRODUCTION-GRADE NON-DESTRUCTIVE FIX at PERFECT 1.0 cleanup recovery with data already present
- Testbed production ship + cross-axis regression check is the 4th stage that converts the closed-loop substrate-product positioning artifact into a SHIPPED capability

## Cross-references

- cap_map.md v587 entry: full empirical results + cross-axis impact analysis + 5 rescue sketches
- notes/exp_dev_to_research_NAME_AUGMENTED_ENCODING_HARDPASS_EXISTING_NAME_FIELD_RECOVERS_DECODE_TO_1_0_FIX_DEMONSTRATED_2026-06-12.md: original Exp-Dev verdict routing
- PP-406 / PP-407 (composition + decomposition NO-CLIFF v582; mechanism-resolved by PP-408 v586; fix-demonstrated by PP-409 v587)
- PP-408 (32-atom collision diagnostic v586; destructive-dedup upper-bound)
- PP-401 (qa_self_knowing; A-axis cross-application target)
- Layer-2 spectral substrate memory (tw_edge_z=-2.26 baseline; substrate-clustered-codebook discovery 2026-06-11)

## Acceptance criteria

- (Testbed) `AtomEncoder.algebra_mode` accepts alpha config knob at default 0.5
- (Testbed) L1 categorical-clustering tw_edge_z regression check passes HP gate
- (Testbed) PP-401 A-axis re-measure on augmented codebook passes HP gate
- (Testbed) production-ship commit with regression-check results in commit message
- (verdict_handler next cycle) cap_map v587 -> v588 annotation P-band lift for PP-409 / PP-406 / PP-407 based on Testbed ship outcome
