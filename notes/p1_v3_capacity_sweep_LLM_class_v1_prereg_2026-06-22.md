# p1 v3 -- LLM-class capacity-sweep pre-reg (Skunkworks-recommended Director follow-up to CERT 590)

**Date:** 2026-06-22
**Parent CERT:** CERT 590 (p1 v2 chain-grade; math::T3/EXP_p1_v2_action_at_any_position_LLM_class_v1).
**Parent pre-reg:** [p1_v2_LLM_class_cell_prereg_2026-06-22.md](p1_v2_LLM_class_cell_prereg_2026-06-22.md)
**Cell:** experiments/exp_p1_v3_capacity_sweep_LLM_class_v1.py
**Lane:** Skunkworks 2026-06-22 follow-up: "capacity-sweep at K closer to N*0.14 ~ 9000 to discriminate near saturation (g1->g1b precedent)."

## Motivation

p1 v2 chain-graded at K=500 / N_DIM=65536 with all-ratios=1.000. alpha = K/N = 500/65536 = 0.0076 is well below the Hopfield-Hebbian capacity bound 0.14*N ~ 9175. Chain-grade was earned via the BLANK-arm discriminator (collapses to chance, proves recall is mechanism not artifact), but the saturated ratios reflect substantial HEADROOM below the substrate's capacity edge.

modern_hopfield_xl just HARD_FAILed at LLM-class for the inverse reason (no classical-cliff at alpha=0.14 with the additive-noise model used; the WITHIN-arm did not collapse where Hopfield theory predicts). v3 re-uses p1's DISCRIMINATOR architecture (4 arms; BLANK collapse-to-chance proves recall is mechanism not artifact) which already chain-graded at LLM scale -- so a clean capacity gradient should be visible.

## What v3 changes vs v2

| Knob | v2 (CERT 590 HARD_PASS) | v3 (this) |
|------|-------------------------|-----------|
| Test target | portability across (V_C, N_DIM) operating points | capacity sweep along K (storage load) |
| Grid | 3 pairs (V_C / N_DIM lifts) | 8 K values along single (V_C=16384, N_DIM=65536) op-point |
| N_DIM | 32768 -> 65536 (lifts) | 65536 fixed |
| V_C | 4096 / 8192 (varies per pair) | 16384 fixed (V_C >= K_max=15000) |
| K_atoms | 500 (alpha=0.0076) | {500, 2000, 5000, 8000, 9000, 10000, 12000, 15000} (alpha 0.0076 -> 0.229) |
| Storage dtype | fp32 (val_cb, key_qs) | fp16 (val_cb, key_qs) + fp32 accumulation [VRAM fit at K_max=15000] |
| Pairs structure | (P_0, P_1) JL-projected | (P_0=P_1) identity-replay [v2 already proved JL portability; v3 isolates capacity] |

JL-projection is identity at v3's single op-point. The REPLAYED arm still stores-then-replays through the projection codepath (Hebbian binding survives the identity transform iff the mechanism is genuine).

## K sweep design

| K | alpha = K/N | regime |
|---|-------------|--------|
| 500 | 0.0076 | well-below (anchor; v2 chain-grade point) |
| 2000 | 0.0305 | below; discriminating-regime start |
| 5000 | 0.0763 | below; discriminating-regime end |
| 8000 | 0.1221 | near-bound (just below 0.14) |
| 9000 | 0.1373 | at Hopfield-Hebbian capacity bound |
| 10000 | 0.1526 | just above bound |
| 12000 | 0.1831 | above; saturation regime |
| 15000 | 0.2289 | well-above; capacity-test premise check |

## Pre-registered HARD bands (Director/Skunkworks 2026-06-22)

**HARD_PASS** (capacity-curve evidence; all conditions must hold):
- WITHIN at K=500 >= 0.95 (anchor matches v2 baseline)
- WITHIN at K=9000 (or nearest >=9000) <= 0.50 (substrate IS crossing the capacity edge)
- WITHIN at K=15000 <= 0.90 (capacity-test premise: substrate is being stressed)
- REPLAYED - FRESH >= 0.20 at some K in [2000, 5000] (discriminating regime; mechanism alive)
- BLANK <= 0.05 at every K (chance floor preserved)
- substrate-only gate (n_llm_calls == 0)
- cv across 3 seeds <= 0.10 on every K (seed-stable)

**HARD_FAIL** (any of):
- WITHIN at K=15000 > 0.90 (capacity-test premise fails -- still below capacity at alpha=0.229)
- REPLAYED never beats FRESH by >= 0.20 in K in [2000, 5000] (mechanism dead)
- BLANK > 0.05 at any K (recall is artifact of key encoding)
- substrate-only gate violated
- any cv > 0.10 across seeds

**MIDDLE_BAND:** in between.

## Direction-honor (Skunkworks n3 SimVQ catch)

WITHIN must monotone-decrease in expectation across K. WITHIN INCREASING with K = measurement artifact (HARD_FAIL). Code allows 0.05 slack per step for sampling noise.

## VRAM accounting (4060 Ti, 8 GB)

At K=15000 V_C=16384 N=65536 fp16:
- val_cb (V_C, N) = 16384 * 65536 * 2 = 2.15 GB
- key_qs (K, N)    = 15000 * 65536 * 2 = 1.97 GB
- val_payload = slice (no extra alloc)
- JL tile (4096, N) fp32 transient = 1.07 GB
- matmul intermediates fp32 (K-dim scores, N-dim y, V_C-dim sims) = trivial
- Peak per arm ~ 5 GB << 8 GB

## Smoke gate evidence (this cycle, pre-dispatch)

- Local CPU --self-test: PASS (T1 WITHIN=1.000, T2 BLANK=0.100, T4 JL_drift=0.163, T5 implicit_vs_explicit max-abs-diff 1.75e-10).
- Remote GPU smoke + Fix #3 single-seed timing measurement: pending (to fire next).
- Smoke uses tiny K_grid=[50, 200, 500] V_C=1024 N=2048 -- just verifies harness end-to-end.

## Dispatch parameters

- Queue: `overnight_queue` (GPU runner; `import torch` literal satisfies routing-sanity gate).
- Wall budget: 7200s (default + safety margin; full-3-seed est ~100 min based on K_max matmul scaling from v2's 73.7s @ K=500).
- HDLAB_EXP_NAME: `p1_v3_capacity_sweep_LLM_class_v1`
- Cell-side _smoke-suffix detect routes any accidental smoke-entry to smoke mode.

## What this DOESN'T claim

- Does NOT extrapolate K > 15000 (only test up to alpha=0.229).
- Does NOT test V_C scaling effects (V_C=16384 fixed; isolates K).
- Does NOT test N_DIM scaling (N=65536 fixed; v2 covers N_DIM lifts).
- Does NOT test alternative noise models (NOISE_FRAC=0.05 fixed).

This cell maps the K-driven capacity curve at LLM-class N_DIM, with the 4-arm discriminator from v2's chain-grade methodology.

## SCHEMA-VET

Inherits SCHEMA-VET from parent v2 (same mechanism + arms + discriminator-regime). v3 is a CAPACITY extension along the K axis, not a mechanism change. If HARD_PASS, Skunkworks ratifies as chain-grade extension of math::T3/EXP_p1_v2_action_at_any_position_LLM_class_v1 along the K axis (proposed atom id: math::T3/EXP_p1_v3_capacity_sweep_LLM_class_v1).

-- Exp-Dev (Prover); cell-author dispatch cycle 2026-06-22
