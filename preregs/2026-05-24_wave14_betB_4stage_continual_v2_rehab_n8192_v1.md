# Prereg: wave14_betB_4stage_continual_v2_rehab_n8192_v1

**Date**: 2026-05-24
**Source**: cap_map v189 K2 4-stage rehab promotion gate
**Triggering verdict**: wave14_betB_4stage_continual_v1_2026-05-24 FOURSTAGE_MIDDLE_BAND retention_A=0.740 retention_B=0.854 retention_C=0.798
**Script**: experiments/exp_wave14_betB_4stage_continual_v2_rehab_n8192_v1.py
**Queue**: overnight_queue (GPU; N=8192 + 16 Phase-A epochs is compute-heavy)

## Question

Does doubling substrate dimension (N=4096 -> N=8192) and Phase-A consolidation
(8 -> 16 epochs) close the retention_A=0.74 gap to HARD-PASS 0.80 observed
in v1, while maintaining retention_B and retention_C above the per-stage
HARD-PASS 0.70?

## Falsifier statements (per [[feedback-no-smoke]] + [[feedback-envelope-expansion-fail-bands]])

- **HARD-PASS**: mean retention_A >= 0.80 AND retention_B >= 0.70 AND retention_C >= 0.70
  across 5 seeds {7, 17, 23, 31, 41}.
  -> K2 4-stage CL clears HARD-PASS gate with the capacity + consolidation rehab axis.
  -> K2 row moves 🟡 PARTIAL -> ✅ at v190.

- **HARD-FAIL**: mean retention_A <= 0.50 OR catastrophic-collapse pattern at stage D
  (defined as retention_B or retention_C also drops below 0.50 after Phase D).
  -> Capacity + consolidation does NOT help; 4-stage exceeds substrate ceiling
     regardless of rehab axis.
  -> K2 row stays 🟡 PARTIAL with v190 capacity-rehab-FAIL annotation.

- **MIDDLE_BAND**: intermediate retentions. Two sub-bands pre-specified:
  - "rehab-partial-improvement": retention_A in (0.74, 0.80); mechanism benefits
    from rehab axis but does not close the gap. Carry-forward rehab to
    Phase-D-specific replay weighting.
  - "rehab-no-improvement": retention_A in (0.50, 0.74); rehab axis adds nothing
    or hurts. Implies capacity + consolidation is NOT the bottleneck;
    Phase-D-specific replay weighting becomes the next rehab axis OR product-spec
    rescopes to accept 0.74 floor.

## Discipline citations

- Per [[feedback-no-experiment-design-in-prompts]]: exp_dev chose N=8192 (next-up from
  v1 N=4096 to test capacity-headroom axis) + 16 Phase-A epochs (2x v1 for the
  consolidation axis); 5 seeds matches v1.
- Per [[feedback-no-smoke]]: HARD-PASS + HARD-FAIL bands falsifiable before run.
- Per [[feedback-envelope-expansion-fail-bands]]: MIDDLE-band rehab-fail outcome
  pre-specified ("rehab-no-improvement" sub-band).
- Per [[feedback-rehabilitation-after-rejection]]: this IS the rehab discipline for
  the K2 PARTIAL verdict; 3 rehab axes identified in v189 (capacity / consolidation /
  Phase-D-specific replay weighting); this experiment tests the first two stacked.
- Per [[feedback-dont-overextend-theorems]]: HARD-PASS requires uniform across-seed
  per-stage threshold clearing; point-estimate mean >= 0.80 with high seed variance
  would still leave a question about robustness.
- Per [[feedback-ascii-only-in-scripts]] (OBSOLETED): N/A -- script uses
  sys.stdout.reconfigure(utf-8) per current convention.

## Smoke gate

N=1024 + 1 Phase-A epoch + 1 seed + 5000 bytes/corpus. Should complete < 60s.
Smoke PASS = retention_A >= 0.10 on the one seed (lenient sanity check via
oracle.assert_baseline_high).

## Expected runtime full

GPU at N=8192 + 5 seeds + 16 Phase-A epochs (heavier than v1's 8) + 4 corpora
each at 200k bytes: estimated ~2-4x v1 wallclock. v1 ran in TBD wallclock at
N=4096 + 5 seeds + 8 Phase-A epochs. Setting timeout=10800 (3h) as
conservative upper bound.
