# Pre-registration: streaming_prediction_8_v1

Date: 2026-06-02
Anchor: streaming_prediction_8_v1
Queue: remote_cpu_queue
Seeds: [7, 17, 23, 31, 41]
N: 1024

## Hypothesis
SP8: sliding write window (erase-and-rewrite) maintains high retrieval fidelity at
late steps when an unbounded accumulation policy collapses. Window policy keeps
alpha_eff ~ WINDOW_SIZE/N = 0.08, well below alpha_c=0.138. Tests whether the
erase+write mechanism provides quantifiable late-stage advantage.

## Pre-registered Thresholds
HARD-PASS: fid_window >= 0.70 AND late_advantage >= 0.05 AND newest_fid >= 0.85 (>=60% seeds).
HARD-FAIL: fid_window < 0.40 (window policy broken) OR newest_fid < 0.60.
MIDDLE: 2/3 cells pass.

## Calibration Source
Smoke MIDDLE_BAND: fid_window=1.0 PASS, newest=1.0 PASS, late_adv=0.016 FAIL (too small).
Walk-back: 5 seeds at WINDOW=80, T_TOTAL=240 (more late-stage contrast steps).
Theory: contrast grows with T_TOTAL relative to WINDOW_SIZE. At T=240=3*WINDOW,
no_eviction alpha approaches 0.23 >> alpha_c, so advantage should exceed 0.05.

## Smoke Result
MIDDLE_BAND: fid_window=1.0, newest=1.0, late_adv=0.016. Walk-back: 5 seeds.
