# Pre-registration: q_a3_l3_cross_layer_composition_v1_n8192

Date: 2026-06-02
Anchor: q_a3_l3_cross_layer_composition_v1_n8192
Queue: overnight_queue
Seeds: [7, 17, 23, 31, 41]
N: 8192

## Hypothesis
Q-A3 L=3 cross-layer Hadamard composition (p=2 Hopfield, 3-layer: outer/mid/inner)
at N=8192. Tests scaling of L3 compositional fidelity from n4096 to n8192.
Cross-layer retrieval should maintain high fidelity at larger N.

## Pre-registered Thresholds
HARD-PASS: l3_fid >= 0.80 AND l2_fid >= 0.80 AND l1_fid >= 0.80 (>=60% seeds).
HARD-FAIL: l3_fid < 0.50 OR l2_fid < 0.50.
MIDDLE: some layers pass (outer/mid) but l3 borderline.

## Calibration Source
n4096 HARD_PASS at L=3. N=8192 is 2x scale; same pattern density so fidelity
should improve slightly (more dimensions, same M pattern count).

## Smoke Result
HARD_PASS: all metrics = 1.0 (N=8192, 2 seeds).
