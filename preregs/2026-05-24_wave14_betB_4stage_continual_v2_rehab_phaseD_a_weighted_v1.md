# Prereg — wave14_betB_4stage_continual_v2_rehab_phaseD_a_weighted_v1

**Date**: 2026-05-24
**Author**: orchestrator exp_dev role (inline)
**Cap_map cell**: K2 True continual learning at production scale (A->B->C->D) — KILLER Tier 1

## Trigger

v190 cap_map K2 4-stage rehab axes 1 (N=8192 + 2x Phase-A epochs) and 2 (Phase-A consolidation) both SATURATED inside seed-variance noise floor (retA ~ 0.74 unchanged from v1 baseline). Axis 3 (Phase-D-specific replay weighting) is the final remaining axis from the v189 3-axis K2 rehab list; this prereg tests it.

## Mechanism

Identical to v1 base run_one_seed up through Phase C. Phase D replay buffer is REBALANCED so that Phase A samples appear with k=4 multiplicity relative to Phase B and Phase C samples (i.e., during Phase D the substrate "sees" stage-A retrieval pairs 4x as often as stage-B and stage-C pairs). All other knobs (N=4096, batch=64, 5 epochs Phase B/C/D, 8 epochs Phase A) match v1 base. 5 seeds {7, 17, 23, 31, 41}.

## Falsifier statements

| Band | Threshold | Interpretation |
|---|---|---|
| **HARD-PASS** | mean retention_A >= 0.80 AND retention_B >= 0.70 AND retention_C >= 0.70 across 5 seeds | K2 4-stage CL clears HARD-PASS via Phase-D A-weighted replay; K2 KILLER T1 row promotes 🟡 -> 🟢 ✅ track |
| **HARD-FAIL** | mean retention_A <= 0.50 OR catastrophic-collapse at stage D | A-weighted replay actively hurts (oversample of A crowds out B/C info); K2 axis 3 closed-failed |
| **MIDDLE** | intermediate | Rehab axis adds partial benefit but does not close retention_A gap; joins axes 1+2 as third saturation point; K2 intrinsic-ceiling pattern confirmed across all 3 rehab axes; product-spec rescoping recommendation |

## Substrate-product reading

- HARD-PASS outcome: the substrate's 4-stage continual learning works AT product spec via stage-aware replay weighting; the rehab axes are NOT all saturating; the "intrinsic ceiling" reading from v190 axes 1+2 was incorrect.
- HARD-FAIL outcome: A-weighted replay actively hurts; 3-axis rehab list is fully closed-failed; K2 ❌ PROVISIONAL closure OR product-spec rescoping (accept retA=0.74 floor for 4-stage chains) becomes the decision point.
- MIDDLE outcome: 3-axis rehab list exhausted with partial benefit; intrinsic ceiling pattern reinforced; product-spec rescoping is the structurally clean outcome.

## Discipline citations

- per [[feedback-no-smoke]]: bands falsifiable BEFORE running.
- per [[feedback-envelope-expansion-fail-bands]]: envelope-expansion drill on K2 PARTIAL row from v189+v190; both bands carry forward + MIDDLE band outcome plan specified.
- per [[feedback-rehabilitation-after-rejection]]: rehab axis 3 of v189 3-axis K2 rehab list.

## Smoke

PASSED (smoke at N=1024 single-seed: retA=0.924 retB=0.914 retC=0.931 -> FOURSTAGE_HARD_PASS). Smoke value is at smaller N + fewer epochs and is not predictive of FULL outcome; included as sanity check that mechanism + plumbing work.
