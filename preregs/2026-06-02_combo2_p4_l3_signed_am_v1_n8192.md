# Pre-registration: combo2_p4_l3_signed_am_v1_n8192

Date: 2026-06-02
Anchor: combo2_p4_l3_signed_am_v1_n8192
Queue: overnight_queue
Seeds: [7, 17, 23, 31, 41]
N: 8192

## Hypothesis
COMBO-2 at production scale N=8192: p=4 polynomial DAM with L=3 Hadamard hierarchy
and signed-AM (B-repulsion) combines hierarchical composition with negative knowledge
at full-production dimensionality. Validates the N=4096 HARD_PASS result scales.

## Pre-registered Thresholds
HARD-PASS: l3_fid >= 0.80 AND b_rep >= 0.85 AND parity_contam <= 0.05 (>=60% seeds).
HARD-FAIL: l3_fid < 0.50 (retrieval breaks) OR b_rep < 0.50 (negative knowledge breaks).
MIDDLE: 2/3 cells pass.

## Calibration Source
v1_n4096 HARD_PASS: l3_fid=1.0, b_rep=1.0, parity_contam=0.0.
Production N=8192 may show slight degradation; HP set at 0.80 (20% headroom).

## Smoke Result
HARD_PASS: l3_fid=1.0, b_rep=1.0, parity_contam=0.0 (N=8192 smoke, 2 seeds).
