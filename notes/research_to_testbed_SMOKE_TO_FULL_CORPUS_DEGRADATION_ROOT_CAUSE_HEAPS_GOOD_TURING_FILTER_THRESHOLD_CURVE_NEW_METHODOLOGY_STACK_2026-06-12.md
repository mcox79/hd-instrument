# Research -> Testbed: Smoke-to-full corpus degradation ROOT CAUSE re-diagnosed -- filter-threshold-curve scale dependence (Heaps + Good-Turing missing-mass) supersedes refuted partition-composition hypothesis -- new methodology stack PPI-calibration + Heaps-scaled-threshold + Goodhart-decoupled validation

**From:** Research  **Date:** 2026-06-12 (Cycle 51 close)
**Re:** Smoke-to-full corpus degradation 2x deep drill verdict (P_deflated 0.48)

## TL;DR

- Partition-composition hypothesis (yesterday's drill 3 mechanism) EMPIRICALLY REFUTED (stratification doesn't help; Exp-Dev HANDOFF2 finding)
- NEW root cause: filter-threshold-curve scale dependence -- Heaps' law (vocabulary growth ~ N^beta) + Good-Turing missing-mass (smoke under-samples low-frequency true-positives that full-corpus would surface)
- NEW methodology stack: PPI-calibration (prediction-powered inference) + Heaps-scaled-threshold + Goodhart-decoupled validation
- Drill output: notes/research_drill_smoke_to_full_corpus_degradation_alternative_hypotheses_2x_2026-06-12.md

## Why this matters for Testbed

Phase-2-light Option C extractor uses smoke runs to estimate full-corpus P@K and decide ingest scope. Until now, this estimate was systematically biased and partition-stratification didn't fix it. The new methodology gives Testbed:

1. **Heaps-scaled-threshold**: scale the Z-count threshold by expected vocabulary growth N^beta where N is full corpus size and beta is empirical Heaps exponent. Smoke threshold != full-corpus threshold; the ratio is computable.

2. **Good-Turing missing-mass correction**: estimate the probability mass of unseen-in-smoke true-positives via Good-Turing (frequency of frequency-1 items / N_smoke). Add this back to smoke P@K estimate.

3. **PPI-calibration** (Angelopoulos 2023, Science): use small labeled smoke set + larger unlabeled full set to compute valid confidence intervals on full-corpus P@K. The standard approach for cheap-test-to-expensive-test calibration in ML/IR.

4. **Goodhart-decoupled validation**: smoke metric optimized != deployment metric. Decouple smoke-internal Z-filter (extractor knob) from full-corpus deployment metric (P@K of ACCEPT decisions). Validate Goodhart-decoupled by comparing smoke-predicted ACCEPT rate to actual full-corpus ACCEPT rate.

## Concrete Testbed action items

**P1 (Cycle 52 candidate, not blocking HP_v1+)**:
- Implement Heaps-scaled-threshold in Phase-2-light: compute beta from smoke vocabulary curve; scale Z-count threshold by (N_full / N_smoke)^beta
- Add Good-Turing missing-mass correction to smoke-side P@K estimate
- Consider PPI-calibration for confidence intervals (paper: Prediction-Powered Inference, Angelopoulos 2023; library: ppi-py)

**P2 (Cycle 52+)**:
- Goodhart-decoupled validation cell: vary Z-filter to compare smoke-predicted ACCEPT to actual full-corpus ACCEPT; quantify decoupling

## Status

- Smoke-to-full corpus degradation is METHODOLOGY problem not architectural; substrate Phase-2-light extractor works -- it's the SMOKE-AS-FULL-PROXY assumption that fails
- New methodology stack maps cleanly onto IR / NLP calibration literature
- Not blocking HP_v1+ macro work
- USER goal "substrate understands own mathematics" is INDEPENDENT of this methodology fix (L6-PROOF + T1 algebra-dict backfill = USER goal direct path)

## Cross-references

- notes/research_drill_smoke_to_full_corpus_degradation_alternative_hypotheses_2x_2026-06-12.md (drill source)
- notes/exp_dev_to_research_HANDOFF2_FEASIBILITY_stratification_does_NOT_help_premise_appears_stale_proxy_P30_2026-06-12.md (refutation of partition-composition hypothesis)
- memory `substrate_stratified_smoke_does_not_help_diffuse_jargon_handled_by_recurrence_2026-06-12` (refutation context)

---

**Testbed:** SMOKE-TO-FULL CORPUS DEGRADATION ROOT CAUSE RE-DIAGNOSED + filter-threshold-curve scale dependence Heaps + Good-Turing missing-mass + new methodology stack PPI-calibration + Heaps-scaled-threshold + Goodhart-decoupled validation + concrete action items P1 Heaps-scaled-threshold + Good-Turing missing-mass + PPI-calibration P2 Goodhart-decoupled validation cell + Cycle 52 candidate not blocking HP_v1+ + USER full-auto continuing.
