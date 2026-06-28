# PRE-REG: exp_counterfactual_replay_latency_delta_stack_v2_single_intervention

**Date:** 2026-06-27
**Anchor:** counterfactual_replay_latency_delta_stack_v2_single_intervention
**Route:** remote_cpu_queue
**Parent atom:** causal_counterfactual_replay_v1 (MIDDLE_BAND; accuracy=1.000; mean_intervention=16.864ms)
**Parent baseline path:** d:/AI/hd-instrument/data/exp_causal_counterfactual_replay_v1/metrics.json
**Sibling v1 (verified MIDDLE_BAND):** d:/AI/hd-instrument/data/exp_counterfactual_replay_latency_delta_stack_v1/metrics.json
**Sibling v1 cell:** d:/AI/hd-instrument/experiments/exp_counterfactual_replay_latency_delta_stack_v1.py

## Concept

v1 landed MIDDLE_BAND: DELTA_STACK_SHORT setup=10.999ms (HP target <4ms missed); query=2.344ms HP target met; acc=0.985 HP target near-met. Author's root-cause analysis: SHORT_STACK=5 means setup loop builds 5 (src, delta) pairs, each requiring `W @ ent[other_idx]` (one full pinv-equivalent matvec); filler cost ~= one pinv solve. The HP regime targeting parent atom's MEASURED@16.864ms is SHORT_STACK=1 (single-intervention; parent atom was measured single-intervention).

v2 fix per author recommendation #3 (single-intervention regime) plus #1 (amortize-the-fillers): test SHORT_STACK=1 (no filler amortization required) AND add ARM_DELTA_STACK_AMORTIZED that pre-computes filler delta cache OUTSIDE the timed setup window (hoists filler matvecs out of measurement).

This is engineering not science -- accuracy preserved by construction (algebraic identity). HARD_PASS auto-promotes parent atom from MIDDLE_BAND to chain-grade.

## Arms

- **ARM_BASELINE_FULL_REWRITE** -- reproduce parent's pinv rebuild (HYPOTHESIZED@ setup ~13-17ms reproducing v1)
- **ARM_DELTA_STACK_SHORT** -- delta-stack with SHORT_STACK=1 (single CF intervention; no filler; mechanism under test)
- **ARM_DELTA_STACK_AMORTIZED** -- delta-stack with SHORT_STACK=5 BUT filler deltas pre-computed and cached OUTSIDE the timed setup loop (tests hoist-fillers recommendation)
- **ARM_DIRECT_LOOKUP_ORACLE** -- pre-computed lookup table (upper bound on latency)
- **ARM_RANDOM_DELTAS** -- single random delta (no structure; control: distinguishes "structured deltas work" from "any sparse correction works")

## HARD_PASS (engineering atom)

- ARM_DELTA_STACK_SHORT setup_latency_ms < 4 (HYPOTHESIZED@ ~4x faster than parent baseline 16.864ms)
- ARM_DELTA_STACK_SHORT query_latency_ms < 10 (HP target; v1 already cleared at 2.344ms)
- ARM_DELTA_STACK_SHORT counterfactual_accuracy >= 0.99 (preserve parent's MEASURED@1.000)
- ARM_DELTA_STACK_AMORTIZED setup_latency_ms < 4 (proves filler-hoisting works for deeper stacks)
- arms_distinct = True (ARM_DELTA_STACK_SHORT vs ARM_RANDOM_DELTAS accuracy gap >= 0.50)

## HARD_FAIL

- ARM_DELTA_STACK_SHORT setup_latency >= ARM_BASELINE_FULL_REWRITE setup_latency (no win at single-intervention)
- ARM_DELTA_STACK_SHORT accuracy < 0.95 (lossy abstraction)
- ARM_DELTA_STACK_AMORTIZED setup_latency >= 4ms (hoist-fillers doesn't help)
- ARM_RANDOM_DELTAS accuracy within 0.10 of ARM_DELTA_STACK_SHORT accuracy (signal not from structured deltas)

## MIDDLE_BAND

- ARM_DELTA_STACK_SHORT setup_latency in [4ms, 10ms] with accuracy preserved (some win but not chain-grade); revise HP bar OR accept this regime

## Cardinality / scale

- Smoke: N=2048, n_seeds=2, 200 single-intervention cycles, expected wall ~3-5min
- Full: N=8192, n_seeds=5, 1000 single-intervention cycles, expected wall ~15-30min
- EXPECTED_N_UNITS = n_seeds * n_arms * n_cycles
- HARD_FAIL_CARDINALITY_BREACH if observed per-arm cycle count < EXPECTED_N_UNITS

## Self-tests (formula-selftest)

1. Algebraic identity: delta_stack(W, [(s, delta)]) @ s == (W @ s) + delta
2. Baseline rebuild and delta-stack-single produce equivalent CF outputs for identical interventions (cosine > 0.95)
3. perf_counter resolution check: 100 noop measurements median < 100us
4. Amortized filler cache produces same output as in-loop filler construction for the matching src

## Discriminator-must-survive-scale (META_RULE_DSS, USER 2026-06-26)

Latency comparison is regime-invariant: pinv solve is O(N^2.x); single delta append is O(N) — same scaling as v1, no regime change. SHORT_STACK=1 strengthens the discrimination because BASELINE is the same matvec cost but no filler overhead bloats DELTA. Check A passes.

## Auto-promotion

If HARD_PASS: parent atom causal_counterfactual_replay_v1 auto-promotes MIDDLE_BAND -> chain-grade (latency was the only blocker). Flag for Skunkworks.

## Discipline citations

- exp_dev.md L1-L4 hardening + cardinality_ok
- META_RULE_AF arms_differ_verified via SHA-256 of per-arm signature
- META_RULE_AH atomic-write (tmp+os.replace via _seed_checkpoint.write_metrics)
- ASCII-only; `__main__` guard; SystemExit re-raise before BaseException
- BIAS-Q: results within 0.001 of 1.000 flagged in verdict_msg if observed
- Number tagging on all numeric claims (MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@)
- Cite v1 metrics absolute path + parent atom path in metrics.json
