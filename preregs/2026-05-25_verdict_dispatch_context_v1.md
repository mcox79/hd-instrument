# Pre-registration: Verdict pattern mining deeper -- dispatch context

**Experiment:** wave14_verdict_dispatch_context_v1
**Script:** experiments/exp_wave14_verdict_dispatch_context_v1.py
**Date:** 2026-05-25
**Queue:** local_cpu_queue
**Expected runtime:** <10s

## Motivation

wave14_verdict_pattern_mining_v1 found multi-agent vs single-agent pass-rate gap (0.36 vs 0.69, p=0.019, V=0.32). Follow-up: which specific dispatch sub-patterns drive the gap? Is it a routing style effect (inline vs wrappers), a concreteness effect (abstract frameworks vs concrete formulas), or a temporal artifact (early pipeline before wrappers were introduced)?

## Hypothesis

The multi-agent gap is driven by inline-vs-wrapper dispatch style (inline_main has higher pass rate than multi_wrapper), and this is because multi_wrapper routes are used for complex framework-testing experiments that are harder to pass.

## Pre-registered outcomes

- **DISPATCH_PATTERN_FOUND**: >= 1 sub-pattern with p<0.05, V>=0.25
- **TEMPORAL_REVERSAL**: multi-agent gap reverses between first and last third of log
- **KEYWORD_SIGNAL**: concreteness p<0.05, V>=0.20
- **WEAK_DISPATCH_SIGNAL**: p<0.10 but V<0.25
- **NO_REFINEMENT**: no sub-pattern exceeds V=0.20 with p<0.10

## Hard-pass / hard-fail bands

- **Hard-pass**: DISPATCH_PATTERN_FOUND with V>=0.30 for at least one sub-pattern
- **Hard-fail**: NO_REFINEMENT confirmed (all p>0.20)
- **Middle-band**: WEAK_DISPATCH_SIGNAL or TEMPORAL_REVERSAL

## Self-tests

1. chi-sq known-association 2x2: chi2>high, p<0.01, V>0.3
2. chi-sq independent 2x2: chi2~0
3. classify_dispatch canonical inputs: empty/inline_main/vh_only/multi_wrapper
