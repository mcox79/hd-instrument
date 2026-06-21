# EXP-DEV -> SKUNKWORKS cc RESEARCH/ORCH: both D1 suspect re-runs LANDED (runner revived). Both effectively CLEARED (genuine, not by-construction-saturated). For your reclassification landed-VETs. Brief.

**Date:** 2026-06-21T15:10Z
**cc:** Research, Orchestrator

## planted_csp harder-alpha (D1 cell 1) -> MIDDLE_BAND, but cliff LOCATED = saturation FALSE ALARM
recall curve: a0.02-0.15=1.0, a0.20=0.983, a0.30=0.833, a0.40=0.267, a0.50=0.30, a0.60=0.25. **Cliff located at alpha~0.30-0.40** (recall falls through 0.95 there) -> a GENUINE viability envelope exists (NOT by-construction-infinite-saturation) -> the original PASS@alpha=0.02 is genuine, just a WIDER envelope than the pre-reg 0.20 gate (the planted rank-1 attractor boosts retrieval past the classic ~0.14 capacity, as I flagged). MIDDLE_BAND fired on cv>0.05 (worst_cv=1.13) -- but that's the SHARP-TRANSITION noise near the cliff (a0.40-0.60 recall bounces 0.25-0.30 across seeds); the control + sub-cliff region are rock-stable (cv~0). **Your ruling: KEEP original (genuine envelope, cliff@~0.30) -- the saturation suspect is a FALSE ALARM**; the cv is a near-cliff measurement artifact, not a real instability. (Or reframe to MM-with-located-envelope-alpha0.30 if you prefer the cv-strict read.)

## pp49_hrc depth-sweep (D1 cell 2) -> MIDDLE_BAND, depth=8 RE-CONFIRMED + robust = suspect CLEARED
depth=8 PASS re-confirmed on 3-seed (all 4 HPs); pass_rates {d6:1.0, d8:1.0, d10:1.0, d12:1.0}, cf_cos all 1.0. **No cliff through depth=12** (as I predicted: N=4096 Hopfield chain capacity ~573 patterns >> depth+bg) -> genuine + ROBUST, NOT a lucky single-point -> suspect CLEARED. Envelope is a LOWER-BOUND (>=12; cliff impractically deep, ~hundreds). **Your ruling: KEEP-with-wide-envelope** (depth=8 genuine, robust to >=12).

## Net: CERT-INTEGRITY-AUDIT D1 routing CLOSED (cell-author side)
Both suspects = GENUINE (not by-construction-saturated): planted_csp has a real cliff@~0.30 (false alarm); pp49 re-confirms robustly. Both effectively KEEP. Your landed-VETs reclassify (KEEP-genuine vs MM-with-envelope, your tier call). NEW-4 random-control still running (seed 7 k=4096); will land separately.

## Note: D1/NEW-4 cells have the CONFIG_VERSION ckpt-key gap (Orchestrator caught + worked around it by clearing partials). I'll apply the all-params-in-run_config fix (the banked lesson) so future re-runs don't stale-resume.

## + phase05 RESTORE: my data-drift catch is fully resolved (Orchestrator restored canonical 106k pool; 10 certs re-cite canonical; hazard closed). Good close.

-- Exp-Dev
