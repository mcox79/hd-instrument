# Prereg -- Bet B Direction 5: Allen-Cahn t^(1/2) coarsening retention_A(t)

**Date**: 2026-05-24
**Routing source**: `notes/strategy_request_to_exp_dev_2026-05-24_5_new_directions.md` (Direction 5 -- MEDIUM; cheap; addresses Bet M criterion #1)
**Cap_map at filing**: v189 (commit 45fda61)
**Script**: `experiments/exp_wave14_betB_allen_cahn_tsweep_v1.py`
**Queue target**: overnight_queue (GPU; Phase-C epoch sweep over 7 t-points x 5 seeds)
**Expected wall**: ~45-60 min full (7 t-points x 5 seeds; large-t cells dominate)
**Designed by**: exp_dev inline
**Reference**: `notes/research_R29_ferromagnetism_domains_2026-05-21.md`

## What is being tested

R29's substrate-novel prediction: retention_A(t) ~ 1 - c * t^(1/2) where t = Phase-C training duration (epochs). Substrate as disordered magnet undergoing Allen-Cahn coarsening.

Implementation: sweep Phase-C epochs over [1, 2, 3, 5, 8, 13, 21] (Fibonacci-like; geometric coverage of one decade). Measure retention_A at each. Linear regression log(1 - retention_A) vs log(t); slope should equal 1/2.

## Pre-registered t-sweep

Phase-C epoch sweep: [1, 2, 3, 5, 8, 13, 21] -- 7 t-points spanning ~1.3 decades

## Falsifier statements

- **HARD_PASS**: log-log regression slope in [0.40, 0.60] with r^2 >= 0.70. -> Allen-Cahn t^(1/2) coarsening VALIDATED at substrate level; Bet M multi-probe criterion #1 satisfied.
- **HARD_FAIL**: slope outside [0.30, 0.70] OR r^2 < 0.40. -> Allen-Cahn coarsening NOT the right scaling law for substrate retention dynamics; substrate-as-disordered-magnet framing rejected at this axis.
- **MIDDLE**: slope in [0.30, 0.40] or [0.60, 0.70] with r^2 >= 0.40; report.

## Pre-registered config

- N = 4096; K = 4; BETA = 8
- Seeds = [7, 17, 23, 31, 41] (5 seeds; allows variance bound on slope estimate)
- bytes_per_corpus = 200000
- Phase-A epochs = 8 (fixed)
- Phase-B epochs = 5 (fixed)
- Phase-C epochs = THE SWEPT VARIABLE
- EMA_alpha = 0.7; replay_frac = 0.50

## Rescue paths if HARD_FAIL per [[feedback-rehabilitation-after-rejection]]

1. Other dynamical-system scaling laws -- test slope=1/3 (KPZ growth) or slope=1 (linear decay).
2. Phase-A duration sweep instead of Phase-C (test if A consolidation depth controls retention dynamics).
3. Token-count sweep (rather than epoch-count sweep) within Phase C.
4. Sleep/wake cycle protocol with rest interleaved (R22 sleep consolidation framing).
5. Stricter Phase-C cutoff with bound retention_A(early_stop) prediction.
