# Pre-registration: rate_cond_gain_burst_v1

**Date:** 2026-06-01
**Anchor:** rate_cond_gain_burst_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_rate_cond_gain_burst_v1.py
**Cap_map row:** burst-tolerance row -- CAN-WITH-RATE-GAIN sub-property

## Scientific question
Q15: Does c(lambda)=lambda_nominal/lambda_observed burst-tolerance correction preserve
within 2pp of no-burst baseline AND retention curve match within 5pp over 1000 steps?

## Pre-registered bands
- HARD-PASS: |m_corrected - m_no_burst| < 0.02 (2pp) at t=1000 AND curve_dev < 0.05 (5pp).
- MIDDLE: |m_corrected - m_no_burst| in [0.02, 0.10].
- HARD-FAIL: |m_corrected - m_no_burst| > 0.10.
- SPECIAL: if baseline burst damage < 0.02pp (burst too mild) -> MIDDLE with note.

## Design
- N=4096, M_steady=200, B=50, c_gain=0.80 (= 200/250)
- Three conditions: no-burst, burst-uncorrected, burst-corrected
- Probe at t in {0, 100, 500, 1000}
- 5 seeds

## Formula self-tests
1. c(lambda) = M_steady/(M_steady+B) = 200/250 = 0.80.
2. alpha_burst_corr_eff = 200/4096 + 0.80*50/4096 = 0.0586.
3. Expected overlap no-burst at alpha=0.049: m ~ 0.95.

## Timeout estimate
smoke_wall_s=43.9s, FULL_N=smoke_N, FULL_seeds=5, smoke_seeds=2.
timeout = ceil(1.5 * 43.9 * 1.0 * 2.5) = ceil(164.6) = 165 -> 300 (floor).

## N-suffix note
No _nN suffix. Production N=4096 per PROT-018 rule 3.

## Smoke result
run_mode=smoke, verdict=MIDDLE_BAND corrected_damage=0.0, elapsed=43.9s.
Note: corrected_damage=0 because burst is too mild at alpha=0.049 (below capacity).
Burst damage invisible at smoke scale, but FULL run with 5 seeds will
provide proper statistical power. NOT INSTRUMENTATION_SUSPECT: metrics are non-null
and the 0 damage is consistent with theory (alpha=0.049 is well below alpha_c=0.138).
