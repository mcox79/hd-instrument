# Prereg: ne1_mct_aging_signature_v1

**Date**: 2026-06-01
**Anchor**: ne1_mct_aging_signature_v1
**Queue**: remote_cpu_queue
**Script**: experiments/exp_ne1_mct_aging_signature_v1.py
**Source**: notes/research_round5_7_drills_synthesis_2026-06-01.md (NE-1)

## Hypothesis

MCT/DMFT aging signature: the substrate's two-time correlator C(t,t_w) exhibits
scaling with the ratio t/t_w above the critical load alpha_c ~ 0.138. This is
the aging signature observed in Nanomagnetic Hopfield (Nature Physics 2022).

## Design

- N = 1024, alpha in {0.05, 0.10, 0.14}
- t_w in {10, 20, 40} steps; dt in {5, 10, 20, 40, 80} steps
- Glauber dynamics (beta=20), 10 trials per (t_w, dt, seed, alpha)
- 5 seeds

## Pre-registered thresholds (LOAD-BEARING)

**HARD-PASS**: |Pearson r(log(t/t_w), C(t,t_w))| >= 0.70 AND aging collapse
score >= 2.0 in >= 4/5 seeds above alpha_c. (Sign can be negative: C
decreasing with t/t_w is the expected aging signature per MCT theory.)

**HARD-FAIL**: all seeds show |r| < 0.30 above alpha_c (no aging signal).

**MIDDLE-BAND**: |r| >= 0.70 in >= 4/5 seeds but collapse < 2.0 (aging present
but not clearly t/t_w-scaling dominant); or |r| in [0.30, 0.70] (weak signal).

## No prior empirical anchor

First aging-signature test on substrate. Bands widened per calibration-probe
policy (+-50% of theoretical: HP |r| >= 0.70 is conservative).

## Smoke result

Smoke (2 seeds): abs_pearson_r = 0.802 above alpha_c (passes r criterion),
collapse = 1.02 (below 2.0 threshold). MIDDLE_BAND at smoke.
Signal is present; full 5-seed run needed to resolve.

## Timeout estimate

smoke_wall_s = 100s; FULL same N/structure as smoke; 5/2 seeds ratio.
timeout_s = ceil(1.5 * 100 * 1.0 * 2.5) = ceil(375) = 600s.

## N-suffix

No _nN suffix. Production N = 1024; stated per PROT-018 rule 3.
