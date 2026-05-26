# Pre-registration: wave14zd_gen_with_continual_pool

Date: 2026-05-21
Status: Pre-registered, gated
Priority: composes yz (sampled gen) + za (continual pool) - does self-training during generation help?
Author: experiment_dev session, pipeline tick 37

## Why
yz showed sampled generation produces non-degenerate text. za tests continual
pool retrieval (real-time learning). zd combines: substrate generates AND
appends each (ctx, generated_byte) to the pool during generation. Tests if
substrate self-trains as it generates.

## Verdict labels
- GEN_POOL_IMPROVES: continual gives more diverse output than static
- GEN_POOL_BOTH_WORK: both work, no measurable improvement
- GEN_POOL_COLLAPSE: continual breaks generation (self-trained pool degrades)
- GEN_POOL_STATIC_BROKEN: anomalous
- GEN_POOL_INCONCLUSIVE

## Runtime: ~3 min
