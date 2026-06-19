# Pre-Registration: sagawa_ueda_mutual_info_jarzynski_v1_n4096

Date: 2026-05-29
Anchor: sagawa_ueda_mutual_info_jarzynski_v1_n4096
Queue: remote_cpu_queue
Script: experiments/exp_sagawa_ueda_mutual_info_jarzynski_v1_n4096.py
Timeout: 14400s
Justification: G1 LOAD-BEARING for Paper 1 submission (notes/paper_outline_sagawa_ueda_substrate_thermodynamics_v278_2026-05-29.md section 13).

## Question
Does the substrate satisfy the Sagawa-Ueda generalized Jarzynski equality with explicit mutual-info accounting:
    < exp( -beta * (W - delta_F - kT * delta_I) ) > = 1
across erase trajectories of stored Hebbian patterns?

## Config
N=4096 (PROT-018 binds), m_frac=0.125 (M=512), BSC codebook, SEEDS=[7,17,23,31,41].
beta=1.0/kT=1.0, alpha_hebbian=0.1. Single-batch CPU smoke.

## Pre-Registered Thresholds
NOTE on Jarzynski-Jensen bound vs full identity: the per-pattern-protocol J
estimator Jensen-upper-bounds the full Sagawa-Ueda identity. Bands key on Jarzynski
INEQUALITY satisfaction plus quantitative tightness via ln(J).

HARD_PASS:
  - All 5/5 per-seed J_seed > 0 AND J_seed <= 2.0 (Jarzynski upper bound respected;
    finite-sample excursions above 1 tolerated up to 2x).
  - All 5/5 per-seed ln(J_seed) > -1.5 (within 0.43 OOM of identity).
  Substrate satisfies Sagawa-Ueda generalized Jarzynski; lifts Sagawa-Ueda lineage
  P_deflated from 0.70-0.80 toward 0.85+.

HARD_FAIL:
  - Any per-seed J_seed > 5.0 (second-law-direction Jarzynski violation) OR
  - >= 3/5 seeds with ln(J_seed) < -3.0 (gross saturation; identity unreachable).
  Substrate writes not measurements-with-feedback in SU sense; lineage claim undermined.

MIDDLE_BAND:
  - J in (0, 2] but with ln(J) in [-3, -1.5] in >= 2/5 seeds; directionally correct
    but tightness band insufficient.

## Calibration Note
First explicit Sagawa-Ueda generalized Jarzynski measurement on substrate (prior
sagawa_ueda_v6 verified the SU BOUND, not the equality). Calibration penalty applied
per [[feedback-lit-scan-calibration-penalty]]: published Sagawa-Ueda equality bound
has documented theoretical exact prediction (= 1.0). Bands +/- 1 OOM around identity
follow standard fluctuation-theorem practice when finite-sample noise is dominant.

## Justification (G1 LOAD-BEARING)
Paper 1 outline section 13 lists G1 as LOAD-BEARING required-before-submission:
"sagawa_ueda_v6_n8192 verifies the GENERALIZED JARZYNSKI EQUALITY. Adding EXPLICIT
mutual-info accounting in the trajectory data tightens the Sagawa-Ueda lineage claim
from 'TCFT class' to 'Sagawa-Ueda class with measured I_mutual.'" HP here lifts
the paper's abstract claim from P_deflated 0.70-0.80 to ~0.78-0.85.

## Parent
exp_sagawa_ueda_v6.py (HARD_PASS su_frac=1.0 at N=8192 5-seed). Upgrade adds:
(a) generalized Jarzynski estimator <exp(-beta*(W-dF-dI))>
(b) explicit per-target mutual-info delta_I via Gaussian-channel proxy
(c) HP/HF bands keyed to identity-deviation (not bound-fraction).
