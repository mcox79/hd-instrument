# Prereg: wave4_full_pipeline_with_audit_v1

**Date:** 2026-06-02
**Anchor:** wave4_full_pipeline_with_audit_v1
**Queue:** remote_cpu_queue

## Scientific question
Wave 4 SP1-SP8 + kappa_3 audit compose without interference. mean_fidelity_topk >= 0.70 in late window.

## Pre-registered thresholds
- HP1: mean_fidelity_topk >= 0.70 (last T/3 of T=200 steps).
- HP2: kappa_3 growth ok (non-zero, non-NaN, grows with writes).
- HP3: fidelity std < 0.30 (audit does not destabilize).
- HARD-PASS: HP1 AND HP2 AND HP3 in >= 4/5 seeds.
- HARD-FAIL: mean_fid < 0.40 OR kappa_3 NaN throughout.
- MIDDLE: HP1+HP2 but HP3 borderline.

## Walk-back note
Smoke MIDDLE_BAND (mean_fid=0.64 vs HP=0.70, within 9% of threshold). Per walk-back gate, FULL sample size is as planned (T=200 vs smoke T=60 -- 3.3x more steps), which should raise fidelity above threshold. Not doubling N (CPU experiment; scale fixed at N=1024). Borderline noted.

## Timeout estimate
smoke_wall_s = 1.2s at T=60 N=1024 2-seed. FULL T=200, 5 seeds, scaling_exp=1.0 (linear in T):
timeout_s = ceil(1.5 * 1.2 * (200/60) * 2.5) = ceil(15) = **300s**.
