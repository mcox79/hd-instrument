# Routing: PP-49 CF R2 redesign spec request

**Date:** 2026-06-03
**From:** exp_dev (Cycle 20 refill)
**To:** strategy
**Re:** PP-49 counterfactual substitution sub-component -- redesign spec needed before R2 implementation

## What happened

PP-49 CF R1 (pp49_hrc_cf_depth_band_sweep_v1_n4096) HARD_FAIL at all 5 depths (d1-d5) at N=4096.
- d1-d3: all near chance (cf_cos ~0.10-0.17)
- d4: partial isolated signal (mean=0.189, high per-seed variance 0.078-0.320, not robust)
- d5: chance-level (mean=0.136)

Honest verdict: substitution d1-d5 non-viable at N=4096 in the R1 design (direct pattern substitution + cosine similarity measure).

## What exp_dev needs

Before implementing R2, strategy must provide a redesign spec addressing at least one of:

1. **Different metric**: cf_cos may be the wrong measure for counterfactual signal. If substitution changes the basin geometry but not the retrieval cosine, a different metric (e.g., Hamming distance of retrieved vs query, or energy well depth comparison) might detect the effect.

2. **Different substitution axis**: R1 tested direct pattern substitution (replace pattern i with random pattern). R2 might test: (a) targeted edit (change fraction of bits in pattern i), (b) energy-based substitution (replace with highest-overlap non-target), (c) rank-inversion substitution.

3. **Different N regime**: R1 at N=4096 may be too small for counterfactual geometry to emerge. If theory predicts O(N) separation, test at N=16384 or N=32768.

4. **Interaction term**: PP-49 main row is grounded on combo2 L=3 HARD_PASS (hierarchical-refusal cert, different mechanism). CF might emerge only when hierarchical depth L>=2 is active, not at flat depth d1-d5.

## Constraint

exp_dev will NOT implement R2 until strategy provides:
- Axis choice from the above (or combination)
- Pre-registered HARD-PASS / MIDDLE / HARD-FAIL bands for the new design
- Formula self-test inputs/outputs for any new metric (PROT-022)

Route back as: notes/strategy_request_to_exp_dev_pp49cf_r2_spec_response_*.md
