# Pre-registration: Verdict pattern mining

**Filed:** 2026-05-25
**Script:** experiments/exp_verdict_pattern_mining_v1.py
**Queue:** local_cpu_queue
**Estimated runtime:** <10s

## Hypothesis

With ~100 verdict events in the status log, statistical associations between verdict
outcomes and anchor properties may reveal systematic pre-reg quality signals or
missed biases. Tests: importance level vs outcome, topic cluster vs outcome,
temporal trend, multi-agent vs single-agent dispatch.

## Pre-registered outcomes

**PATTERN_FOUND:** >= 1 association with p < 0.05 AND Cramer's V >= 0.20.
Suggests a structural signal in anchor design or process quality.

**WEAK_SIGNAL:** p < 0.10 but V < 0.20. Suggestive, not conclusive.

**NO_PATTERN:** all tests p > 0.10 or V < 0.10. Outcome variation not captured
by logging metadata.

## Data source

data/orchestrator_status_log.jsonl (105 verdict events at time of pre-reg)

## Statistical tests

Chi-squared with Yates correction, Cramer's V effect size.
Hypothesis-class classification via regex on summary text.
