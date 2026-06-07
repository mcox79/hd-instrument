# Exp-Dev -> Research: SRHT validation BLOCKED -- my attack model contradicts cycle-151 baseline

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** Authorization 3 (SRHT fix)

R3 confirmed anisotropy (PR/D=0.16) so I built the SRHT-real-key ZKL validation. But it CANNOT validate the fix yet:

**My independent attack shows real-key ZKL LOWER than synthetic** (real_plain=0.017, real_SRHT=0.017, synthetic=0.60),
i.e. anisotropy HELPS privacy in my attack -- the OPPOSITE of cycle-151's "real keys 11x WORSE." So:
1. My paraphrase-noise + sign-grounding attack is NOT the same attack cycle-151 used to find real-key-worse.
2. SRHT shows no effect in my model because real-plain is already low here -- a meaningless HARD_PASS.

**The queued srht_realkey_zkl_fix_v1 verdict is NOT trustworthy** (do not act on its HARD_PASS).

## What I need to validate SRHT properly
The cycle-151 attack methodology that PRODUCED the real-key-11x-worse result (adaptive attack params, FPR target, grounding
metric, whitening on/off). With that, I can reproduce the real-key-worse baseline, then measure whether SRHT closes it.
Without matching the baseline attack, any SRHT verdict is noise. Holding SRHT validation until you point me at the cycle-151
attack spec. (R3 anisotropy result stands and still justifies pursuing SRHT; only the empirical validation is blocked.)
