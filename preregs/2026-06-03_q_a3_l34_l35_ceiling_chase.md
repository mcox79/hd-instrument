# Pre-registration: Q-A3 L=34 + L=35 Ceiling Chase at N=4096

**Date:** 2026-06-03
**Anchors:** q_a3_l34_cross_layer_composition_v1_n4096 + q_a3_l35_cross_layer_composition_v1_n4096
**Queue:** overnight_queue (GPU)
**Cap map row:** PP-12 / Q-A3 (cross-layer composition)

## Context

L=2..L=33 at N=4096: all 33 levels EXACT-1.0000 unanimous 5/5 seeds (v359, 19 consecutive extensions). L=32 HARD_PASS (18th streak), L=33 HARD_PASS (19th streak) both completed in v359 cycle. No ceiling found through L=33. These anchors continue the ceiling chase to L=34 and L=35.

## Hypothesis

Cross-layer composition remains fidelity=1.0000 (EXACT) at all depth levels through L=34 and L=35 at N=4096, continuing the unbounded-depth ECC pattern.

## Pre-registered bands

### L=34
- HARD-PASS: all 34 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l34_acc >= 0.5.
- MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation.
- HARD-FAIL: any L_fid < 0.85 OR l34_acc < 0.5.

### L=35
- HARD-PASS: all 35 level fidelities >= 0.9999 unanimous (5/5 seeds) AND l35_acc >= 0.5.
- MIDDLE: any L_fid in [0.85, 0.9999) OR graceful degradation.
- HARD-FAIL: any L_fid < 0.85 OR l35_acc < 0.5.

## Middle-band outcome plan

If MIDDLE (fidelity in [0.85, 0.9999)): indicates ceiling beginning to approach. File strategy note to investigate capacity limits. Do not close PP-12 row; annotate as "ceiling approaching near L=X." Run bisection to narrow ceiling depth.

## Timeout estimate

- smoke_wall_s: ~0.93s (L=33 elapsed FULL 5-seed GPU)
- FULL_N/smoke_N: 1.0 (same N=4096 both)
- FULL_seeds/smoke_seeds: 1.0 (5 seeds both)
- scaling_exp: 1.0 (linear with L, near-constant W size)
- L=34: ceil(1.5 * 0.93 * (34/33) * 1.0) = ceil(1.44) = 300s (GPU floor)
- L=35: ceil(1.5 * 0.93 * (35/33) * 1.0) = ceil(1.48) = 300s (GPU floor)
- timeout: 300s each

## N-suffix binding (PROT-018)

- q_a3_l34_cross_layer_composition_v1_n4096: N=4096 confirmed in script.
- q_a3_l35_cross_layer_composition_v1_n4096: N=4096 confirmed in script.

## PROT-021 checkpoint key

Keyed with run_mode + L to prevent smoke/full checkpoint contamination.
