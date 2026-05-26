# Pre-registration: wave14yz_generation_with_sampling

Date: 2026-05-21
Status: Pre-registered, gated
Priority: generation follow-up — does sampling rescue yy's collapse?
Author: experiment_dev session, pipeline tick 33

## Why
yy showed greedy decoding collapses (entropy 0.977, 4-gram repetition 1.0).
yz tests if sampling (multinomial draw from temperature-scaled softmax) gives
non-degenerate output. Standard LM trick: temperature > 0 prevents
fixed-point collapse.

## Verdict labels
- GEN_SAMPLE_RESCUES_AT_T_<T>: at least one temperature gives non-degenerate text
- GEN_SAMPLE_NO_RESCUE: no temperature works
- GEN_SAMPLE_INCONCLUSIVE

## Sweep
Temperatures {0.5, 0.8, 1.0, 1.5, 2.0}.

## Runtime: ~5 min
