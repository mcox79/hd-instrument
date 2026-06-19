# Pre-registration: wave14zg_gen_rep_penalty

Date: 2026-05-21
Status: Pre-registered, gated
Priority: generation with repetition penalty - alternative anti-collapse
Author: experiment_dev session, pipeline tick 40

## Why
yy showed greedy collapses, yz showed sampling fixes it. zg tests if a
repetition penalty applied to greedy decoding gives a third path.
Real product-style decoder (used in many LLM systems).

## Verdict labels
- GEN_REP_RESCUES_AT_PENALTY_<P>
- GEN_REP_NO_RESCUE
- GEN_REP_INCONCLUSIVE

## Sweep
Penalty in {0.0, 0.5, 1.0, 2.0, 5.0}. Window = last 16 bytes.

## Runtime: ~3 min
