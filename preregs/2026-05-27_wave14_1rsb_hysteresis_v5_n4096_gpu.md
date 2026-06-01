# Prereq: wave14_1rsb_hysteresis_v5_n4096_gpu

Date: 2026-05-27
Anchor: wave14_1rsb_hysteresis_v5_n4096_gpu
Queue: overnight_queue
Script: experiments/exp_wave14_1rsb_hysteresis_v5_n4096_gpu.py
Timeout: 1200s

## Hypothesis
1-RSB hysteresis (max_gap >= 0.10) persists at N=4096 on GPU. v3 confirmed at N=1024 (max_gap=1.84). v4 timed out on CPU. GPU enables N=4096 completion.

## Pre-registered bands (identical to v3/v4)
- HARD_PASS: max_gap >= 0.10 at N=4096
- MIDDLE: max_gap in [0.03, 0.10)
- RS_HARD_FAIL: max_gap < 0.03

## N-suffix
_n4096_gpu suffix; N=4096 is production config per PROT-018.

## Timeout estimate
v3 N=1024 GPU: 70s for 3 seeds 6 M-cells. v5 N=4096: 1.5 * 70 * 8 = 840s -> 1200s.

## Prior anchor
v3 N=1024 HARD_PASS gap=1.84. Smoke at N=512 showed gap=0.835 >> 0.10.
