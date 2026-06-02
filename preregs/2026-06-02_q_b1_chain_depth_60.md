# Pre-registration: q_b1_chain_depth_60_v1_n8192

**Date:** 2026-06-02
**Anchor:** q_b1_chain_depth_60_v1_n8192
**Queue:** overnight_queue
**N:** 8192, **Seeds:** 5, **Chain depth:** 60

## Scientific question
Does the heteroassociative chain retain signal beyond depth-55? Ceiling chase continuing from d45=0.596 (HARD_PASS), d50+d55 just completed.

## Pre-registered bands

**HARD-PASS:**
- depth-5 >= 0.95
- depth-10 >= 0.88
- depth-20 >= 0.70
- depth-30 >= 0.55
- depth-45 >= 0.40
- depth-60 >= 0.20

**MIDDLE:** depth-60 in [0.12, 0.20) while earlier depths meet HP.

**HARD-FAIL:**
- depth-5 < 0.80 OR depth-10 < 0.65 OR depth-20 < 0.40 OR depth-60 < 0.08

## Calibration rationale
Degradation model: cos(d) ~ exp(-lambda * d). With ~150 chains+bg at N=8192, lambda ~ 0.004.
Estimate d60 ~ 0.78 * d55_estimate. d55 HP = 0.25; 0.78 * 0.25 = 0.195. HP set at 0.20 (rounded up).
HF set at 0.08 (< 1/3 of 0.25 HP, per calibration policy). Middle in [0.12, 0.20).

## N-suffix section
Anchor _n8192; production N = 8192; scripts enforce N = _N_SUFFIX = 8192.

## Timeout estimate
Smoke wall ~ d55 smoke (expect ~25s at N=1024 smoke). FULL: N=8192, seeds=5.
formula: ceil(1.5 * 25 * (8192/1024)^1.5 * (5/2)) = ceil(1.5 * 25 * 22.6 * 2.5) = ceil(2119) = 2400
timeout_s = 2400
