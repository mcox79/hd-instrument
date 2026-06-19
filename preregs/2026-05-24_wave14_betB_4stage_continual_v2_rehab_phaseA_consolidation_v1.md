# Prereg: wave14_betB_4stage_continual_v2_rehab_phaseA_consolidation_v1

**Date**: 2026-05-24
**Source**: cap_map v189 K2 4-stage rehab promotion gate
**Triggering verdict**: wave14_betB_4stage_continual_v1_2026-05-24 FOURSTAGE_MIDDLE_BAND retention_A=0.740 retention_B=0.854 retention_C=0.798
**Script**: experiments/exp_wave14_betB_4stage_continual_v2_rehab_phaseA_consolidation_v1.py
**Queue**: overnight_queue (GPU; same compute envelope as v1 but with 2x Phase-A epochs)
**Pairs with**: wave14_betB_4stage_continual_v2_rehab_n8192_v1 (capacity + consolidation stacked)

## Question

Does doubling Phase-A consolidation (8 -> 16 epochs) ALONE (at N=4096 unchanged from v1)
close the retention_A=0.74 gap to HARD-PASS 0.80? If yes, consolidation is the
active rehab axis. If no (and v2_rehab_n8192 passes), capacity headroom is the
active axis. If both fail, the third rehab axis (Phase-D-specific replay weighting)
becomes the next gate.

## Falsifier statements (per [[feedback-no-smoke]] + [[feedback-envelope-expansion-fail-bands]])

- **HARD-PASS**: mean retention_A >= 0.80 AND retention_B >= 0.70 AND retention_C >= 0.70
  across 5 seeds {7, 17, 23, 31, 41}.
  -> Consolidation axis ALONE closes the K2 4-stage gap.

- **HARD-FAIL**: mean retention_A <= 0.50 OR catastrophic-collapse pattern at stage D.
  -> Consolidation alone breaks the substrate.

- **MIDDLE_BAND**: intermediate retentions. Two sub-bands pre-specified:
  - "consolidation-partial": retention_A in (0.74, 0.80); axis helps but does not
    close the gap. The lift from v2_rehab_n8192 (if v2 PASSES) is attributable to
    capacity axis.
  - "consolidation-no-improvement": retention_A in (0.50, 0.74); consolidation
    alone does nothing. Capacity (or the third axis: Phase-D-specific replay
    weighting) is the active route.

## Discipline citations

- Per [[feedback-no-experiment-design-in-prompts]]: exp_dev chose 16 Phase-A epochs
  (2x v1) as the canonical consolidation-axis test; N=4096 unchanged from v1 for
  clean isolation of consolidation from capacity.
- Per [[feedback-no-smoke]]: HARD-PASS + HARD-FAIL + MIDDLE sub-bands pre-specified.
- Per [[feedback-envelope-expansion-fail-bands]]: MIDDLE-band rehab-fail outcomes
  pre-specified ("consolidation-no-improvement" sub-band identifies the negative
  case explicitly).
- Per [[feedback-rehabilitation-after-rejection]]: this is rehab axis 2 of 3
  identified at v189; paired with rehab axis 1+2 (v2_rehab_n8192) for A/B
  isolation; rehab axis 3 (Phase-D-specific replay weighting) is the next gate
  if both v2 variants fail.
- Per [[feedback-dont-overextend-theorems]]: HARD-PASS requires uniform across-seed
  per-stage threshold clearing.

## Smoke gate

N=1024 + 1 Phase-A epoch + 1 seed + 5000 bytes/corpus. Should complete < 60s.
Smoke PASS = retention_A >= 0.10 on the one seed.

## Expected runtime full

Same compute envelope as v1 4-stage but with 16 Phase-A epochs instead of 8.
Estimated ~1.3x v1 wallclock (Phase A is 1 of ~5 training phases). Setting
timeout=7200 (2h) as conservative upper bound.
