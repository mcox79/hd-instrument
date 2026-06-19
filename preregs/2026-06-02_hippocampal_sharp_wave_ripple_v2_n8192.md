# Pre-registration: hippocampal_sharp_wave_ripple_v2_n8192

Date: 2026-06-02
Anchor: hippocampal_sharp_wave_ripple_v2_n8192
Queue: overnight_queue
Seeds: [7, 17, 23, 31, 41]
N: 8192

## Hypothesis
Sharp-wave ripple (SWR) heteroassociative sequence replay at N=8192. Tests whether
W_chain = sum(outer(Xi[k+1], Xi[k]))/N supports fast sign-step MAP retrieval of
K=12 sequences, with correct replay fidelity >> random baseline and << wrong-trigger baseline.

## Pre-registered Thresholds
HARD-PASS: mean_fid_fast >= 0.70 AND mean_wrong_trigger <= 0.20 (>=60% seeds).
HARD-FAIL: mean_fid_fast < 0.40 (retrieval completely fails).
MIDDLE: fid_fast passes but wrong_trigger borderline, or vice versa.

## Calibration Source
Smoke MIDDLE_BAND: fid_fast=1.0 (PASS), wrong=0.14 (PASS), but seed 17 wrong=0.286 > HP.
Walk-back gate applied: 5 seeds + K=12 should resolve the 1/2 seed failure.
Theory: heteroassociative MAP is an exact algorithm; at N=8192 wrong-trigger suppression
should be robust since random patterns are nearly orthogonal (E[dot]=0, sigma=1/sqrt(N)).

## Smoke Result
MIDDLE_BAND: fid_fast=1.0 PASS, random=0.10 PASS, wrong=0.143 borderline. 2/3 cells.
Walk-back: doubling to 5 seeds at K=12.
