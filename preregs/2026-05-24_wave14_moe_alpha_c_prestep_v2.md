# Pre-registration: wave14_moe_alpha_c_prestep_v2

**Date:** 2026-05-24
**Script:** experiments/exp_wave14_moe_alpha_c_prestep_v2.py
**Queue:** overnight_queue
**Parent handoff:** notes/exp_dev_handoff_research_alpha_c_recalibration_2026-05-24.md

## Why this experiment

v1 ran smoke (N=512, 1 seed) and reported alpha_c=0.39 as ALPHA_C_OUT_OF_RANGE against
the band [0.08, 0.25]. Research drill (notes/research_substrate_alpha_c_anomaly_2026-05-24.md)
confirmed the band was wrong-reference-class: the script implements a linear heteroassociator
(y = W k, cosine readout), not AGS autoassociative recurrent dynamics.

Closed-form prediction for linear heteroassociator: alpha_c(tau) = 1/tau^2 - 1.
At tau=0.80: alpha_c_theory = 0.5625. The 4 smoke M-values match within +-0.004 cosine units.

v2 patches ALPHA_C_LO=0.40, ALPHA_C_HI=0.70 (recalibrated), adds closed-form diagnostic
overlay, and runs full mode (N=4096, 5 seeds) to provide 5-seed CI for downstream
MoE SHIFT/PARTITION/SINGLE rebuild.

## Config

- N = 4096 (full mode)
- M_grid = [200, 400, 800, 1600, 3200, 6400]
- Seeds = [7, 17, 23, 31, 41] (5 seeds)
- PASS_COSINE = 0.80
- ALPHA_C_LO = 0.40 (recalibrated from AGS 0.08)
- ALPHA_C_HI = 0.70 (recalibrated from AGS 0.25)
- ALPHA_C_HP_LO = 0.50, ALPHA_C_HP_HI = 0.60 (tight HARD-PASS inner band)
- CI_WIDTH_WARN = 0.05 (HARD-PASS), CI_WIDTH_FAIL = 0.10 (INSTRUMENTATION-FAIL)
- MAX_RESIDUAL_HP = 0.02 (closed-form residual for HARD-PASS)
- MAX_RESIDUAL_MIDDLE = 0.05

## Pre-registered outcome bands

**HARD-PASS (calibration confirmed; MoE rebuild unblocks):**
- alpha_c_measured in [0.50, 0.60]
- CI width < 0.05
- max_closed_form_residual < 0.02 at every grid M
- -> Report alpha_c_measured; M_per_expert = 0.70*alpha_c*N; M_total_k4 = 0.70*alpha_c*N*4*0.80
- -> Proceed to MoE SHIFT/PARTITION/SINGLE rebuild

**MIDDLE (mild deviation; proceed with note):**
- alpha_c_measured in [0.40, 0.50) or (0.60, 0.70]
- OR CI width >= 0.05
- OR max_residual in [0.02, 0.05]
- -> Proceed with measured value; document deviation

**HARD-FAIL (genuine anomaly):**
- alpha_c_measured outside [0.40, 0.70]
- AND max_residual > 0.05 at >= 2 grid points
- -> Re-open substrate-implementation audit; MoE rebuild stays gated

**INSTRUMENTATION-FAIL:**
- Any NaN cosine
- OR CI width >= 0.10
- -> Investigate per-seed before any verdict

## Smoke result (v2)

Multi-scale smoke at N=512 and N=2048 both PASS. Residuals:
- N=512: max residual = 0.0036 (well below 0.05 MIDDLE threshold)
- N=2048: max residual = 0.0004 (excellent match to closed form)
alpha_c (smoke) = 0.39 at N=512 consistent with theory: at N=512 the discrete M-grid
(factor-2 from 50 to 400) gives alpha_c = 200/512 = 0.39 by grid quantization;
at N=4096 with M-grid [200,400,800,1600,3200,6400] the grid resolution allows finer
interpolation near expected alpha_c_theory=0.5625 (M~2300).

## Self-test cells (from handoff, verified)

1. cos_pred(M=200, N=512) = 1/sqrt(1+199/512) = 0.8489; smoke measured 0.8450; residual=0.0039 < 0.005
2. alpha_c_theory(tau=0.80) = 1/0.64 - 1 = 0.5625
3. HARD-PASS band [0.50, 0.60] brackets 0.5625 +/- ~8%
4. M_per_expert at alpha_c=0.5625, N=4096: int(0.70*0.5625*4096) = 1612
5. M_total K=4: int(0.70*0.5625*4096*4*0.80) = 5161

## Estimated runtime

~15-30 GPU-minutes (5 seeds x 6 M-values at N=4096; outer-product N^2 matrix per seed/M).
