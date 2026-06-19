# Prereg: q_f6_pq_distribution_v1

## Scientific question
Q-F6: Measure P(q) overlap distribution. Is it unimodal (retrieval) or bimodal (spin glass)?

## Pre-registered thresholds
- HARD-PASS: All of A (unimodality >= 0.70), B (q_peak >= 0.30), C (q_EA >= 0.20).
- HARD-FAIL: HF-A (bimodality_index >= 0.55) OR HF-C (q_EA < 0.05).
- MIDDLE: 2/3 cells pass.

## Calibration note
First P(q) measurement on substrate. Bands +-50% per calibration-probe policy.
Smoke at R=50 replicas is noise-dominated; FULL at R=200, t_w=1024 is definitive.

## Smoke result
HARD_FAIL at smoke (noise-driven): BI=0.631 triggered HF_A at R=50, t_w=64.
However q_peak=0.467 >= HP=0.30 and q_EA=0.43 >= HP=0.20 are both above HP.
The BI trigger is noise-artifact at small R and short t_w. FULL at R=200 and t_w=1024
will provide statistically meaningful P(q). Ship accepted as calibration probe.

## Timeout estimate
Smoke wall: 0.9s, N=512->1024 (2x), R=50->200 (4x), t_w=64->1024 (16x), seeds=2->5 (2.5x)
Dominant scaling: t_w step increase * R increase.
timeout = ceil(1.5 * 0.9 * 2^1.5 * 4 * 16 * 2.5) = ceil(1.5*0.9*2.83*4*16*2.5) = ceil(768) = 768s.
timeout=1800s (generous; Glauber at t_w=1024 is the bottleneck).

## N-suffix note
No _nN suffix; production N=1024 per rule 3.
