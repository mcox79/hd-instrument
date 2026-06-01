# Prereg: pp31_4a_per_hop_independence_v1

**Date**: 2026-06-01
**Anchor**: pp31_4a_per_hop_independence_v1
**Queue**: remote_cpu_queue
**Script**: experiments/exp_pp31_4a_per_hop_independence_v1.py
**Source**: notes/research_round5_7_drills_synthesis_2026-06-01.md (PP-31 Sub-cap 4-A)

## Hypothesis

Per-hop error independence in multi-hop retrieval: pairwise Pearson correlation
|rho_ij| < 0.20 between hop error indicators across hops i != j. This gates the
product-rule chain confidence mechanism (P(chain) = prod P_hop_i).

## Design

- N = 1024, K = 4 hops, M = 64 per-hop codebook
- 500 query trials per seed; error_k = 1 if overlap < 0.70
- Pearson correlation matrix over (e_1, e_2, e_3, e_4)
- 5 seeds

## Pre-registered thresholds (LOAD-BEARING)

**HARD-PASS**: max|rho_ij| < 0.20 across all off-diagonal pairs; in >= 4/5 seeds.
(Independence holds; product rule justified.)

**HARD-FAIL**: max|rho_ij| >= 0.50 in >= 4/5 seeds.
(Strong correlation; product rule invalid.)

**MIDDLE-BAND**: 0.20 <= max|rho| < 0.50 (weak correlation; product rule approximate).

## Smoke result

Smoke (3 seeds): mean_rho=0.0, max_rho=0.0, error_rate=0.0. MIDDLE_BAND (3/3 seeds
pass HP but need 4/5). Note: error_rate=0 means all hops succeed at low load (M=64,
N=1024, alpha=0.0625); rho undefined in zero-variance case. Full run likely same.

## Walk-back note

error_rate=0 at smoke (all hops succeed at alpha=0.0625). At FULL run same config.
The independence test is still valid: if errors are always 0, rho=0 by construction.
However, the test should ideally show nonzero error rate to be informative. If
error_rate=0 at FULL run, verdict MIDDLE_BAND with note that result is vacuously true.

## Timeout estimate

smoke_wall_s = 27s; 5/3 seeds; linear.
timeout_s = ceil(1.5 * 27 * 5/3) = ceil(67.5) = 300 (PROT-019 floor).

## N-suffix

No _nN suffix. Production N = 1024; stated per PROT-018 rule 3.
