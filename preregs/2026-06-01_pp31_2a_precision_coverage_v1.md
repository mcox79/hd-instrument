# Prereg: pp31_2a_precision_coverage_v1

**Date**: 2026-06-01
**Anchor**: pp31_2a_precision_coverage_v1
**Queue**: remote_cpu_queue
**Script**: experiments/exp_pp31_2a_precision_coverage_v1.py
**Source**: notes/research_round5_7_drills_synthesis_2026-06-01.md (PP-31 Sub-cap 2-A)

## Hypothesis

Hard threshold precision-coverage sweep: at some tau in [0.3, 0.8], substrate's
retrieval gate achieves precision >= 0.92 at coverage >= 0.60. Confidence score
= initial overlap (before retrieval) naturally spans [0,1] across noise levels.

## Design

- N = 512, M = 51 (alpha = 0.10, healthy regime)
- Confidence score: initial query overlap with target (noise_frac_grid spans [0.05, 0.55])
- tau_grid = [0.30, ..., 0.80] (11 values)
- 100 queries per seed (spread across noise levels)
- 5 seeds

## Pre-registered thresholds (LOAD-BEARING)

**HARD-PASS**: precision >= 0.92 at coverage >= 0.60 at some tau in [0.3, 0.8]
AND knee detectable (slope change >= 0.20 per 0.1 tau unit); in >= 4/5 seeds.

**HARD-FAIL**: no tau achieves precision >= 0.80 at any coverage in >= 4/5 seeds;
OR coverage < 0.10 at tau <= 0.50 in >= 4/5 seeds.

**MIDDLE-BAND**: precision >= 0.80 but < 0.92; or knee borderline.

## Smoke result

Smoke (3 seeds): prec at tau=0.30 is 0.93-0.95 with cov ~ 0.57 (HP requires 0.60).
Close to HP threshold. knee=1.1 (clearly detectable). MIDDLE_BAND (coverage
just short of 0.60 at smoke). Full 5-seed run may produce coverage >= 0.60 at tau=0.30
with different random draws.

## Walk-back gate

Smoke coverage 0.57 is within 5% of HP threshold 0.60. Per walk-back gate
policy, FULL n should be doubled. Planning FULL N_QUERIES = 200 per seed.
Effect size (coverage vs HP) d ~ 0.3 at smoke -- borderline.

## Timeout estimate

smoke_wall_s = 0.2s; double queries for FULL; 5/3 seeds.
timeout_s = ceil(1.5 * 0.2 * 2 * 5/3) = 2s -> 300 (PROT-019 floor).

## N-suffix

No _nN suffix. Production N = 512; stated per PROT-018 rule 3.
