# Prereg: PP-58 SCS low-tau sweep d=8 tau=0.01..0.09

**Date:** 2026-06-04
**Cap_map row:** PP-58 SCS sub-property
**Current band:** MIDDLE 0.55-0.70 (founding kappa_3 v353 valid)
**Rescue:** R2 from v378 Cycle 46 strategy decisions (SCS tau=0.10 HARD_FAIL)

## Anchor
pp58_scs_low_tau_sweep_d8_v1_n8192

## Scientific question
Is there a tau_crit < 0.10 below which SCS ratio falls within [0.5, 2.0] at d=8, alpha=0.05?
Three SCS failure modes confirmed: sub-threshold-d (v375), high-alpha (v376), high-tau (v378).
This sweep maps the low-tau boundary of SCS validity.

## Pre-registered bands
**HARD-PASS:** at least 4/9 tau values have mean ratio in [0.5, 2.0] across 5 seeds
             AND tau_crit (smallest valid tau) <= 0.05.
**MIDDLE:** 1-3/9 tau values in [0.5,2.0] OR tau_crit > 0.05.
**HARD-FAIL:** 0/9 tau values have mean ratio in [0.5, 2.0].

## Timeout estimate
Basis: tau=0.10 anchor elapsed ~206s at 5 seeds (N=8192; 1 tau value x 5 seeds = 5 eigvalsh calls).
This sweep: 9 tau values x 5 seeds = 45 eigvalsh calls (9x more cells).
Formula: ceil(1.5 * 206 * 9 * (5/5)) = ceil(2781) = 2781s. Round to 3600s.
Use timeout=3600.

Note: smoke signal (N=512) showed all ratios 15-25x off (HARD_FAIL at smoke scale) --
N-dependent behavior expected; N=8192 is the authoritative test.

## N-suffix
_n8192: production N = 8192. PROT-018 compliant.
No prior empirical anchor for tau_crit; bands reflect scientific uncertainty.

## PROT compliance
- PROT-018: _n8192 suffix; N=8192 in script.
- PROT-021: seed checkpoints keyed with run_mode + seed.
- PROT-022: SCS formula (8+tau/8)/(1+tau) self-tested at module scope for tau=0.01 and tau=0.09.
