# Prereg — Bet B R-PRIME-3 R4 1-RSB basin-discrete rescue

**Anchor**: `wave14_betB_1rsb_basin_discrete_v1`
**Queue**: overnight_queue (GPU; multi-pair multi-seed multi-N)
**Filed**: 2026-05-24 by exp_dev

## Hypothesis

R-PRIME-3 task-pair geometry HARD-FAIL closed (v193 + v195 R1 narrowing). R4
rescue: cluster-structured 1-RSB (1-step replica symmetry breaking) basin-
discrete metric. From structural-glasses field (v195 8 new fields), the
substrate may be in a 1-RSB phase where retention is set by DISCRETE basin
membership rather than smooth distance.

## Pre-registered falsifiers (BEFORE FULL run)

- **HARD-PASS**: `mean(ret | same_basin) - mean(ret | diff_basin) >= 0.10` AND
  partition cleanness (max class fraction) >= 0.80. -> R-PRIME-3 R4 1-RSB
  rescue SUCCEEDS; basin-discrete mechanism is the binding axis.
- **HARD-FAIL**: `|mean(ret|same) - mean(ret|diff)| < 0.02` (flat). -> 1-RSB
  basin-discrete REJECTED; final R-PRIME-3 closure.
- **MIDDLE-BAND**: any intermediate; report bands.

## Parameters (exp_dev autonomy)

- N = 4096 FULL / 1024 smoke
- M per task = 200 FULL / 50 smoke
- N pairs = 24 FULL / 8 smoke
- K_clusters = 4 (1-RSB ansatz)
- Seeds = {7, 17, 23} FULL

## ETA

GPU FULL ~40-90 min.

## Smoke outcome

Smoke at N=1024 single-seed: gap=0.001 partition=0.62 -> HARD_FAIL. Small N
makes basin assignment noisy; FULL at N=4096 24 pairs 3 seeds is the test
of the hypothesis.
