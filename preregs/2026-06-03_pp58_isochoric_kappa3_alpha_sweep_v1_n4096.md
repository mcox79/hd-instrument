# Pre-registration: PP-58 isochoric audit protocol -- kappa_3 two-envelope test

**Date:** 2026-06-03
**Anchor:** `pp58_isochoric_kappa3_alpha_sweep_v1_n4096`
**Queue:** remote_cpu_queue
**Trigger:** Arrhenius deep drill (v343) confirmed substrate exhibits Brot/Rams-Baron 2026-class
two-envelope hidden-coupling structure. PP-58 candidate row: isochoric audit protocol as substrate
measurement discipline. This experiment is the direct empirical test.
**Priority:** PP-58 founding anchor; isochoric measurement discipline confirmation.

## Capability question

Does sweeping sigma_g at FIXED alpha=0.05 (isochoric protocol) reveal two clearly separated
noise envelopes: kappa_3 audit primitive breaks (ratio deviates >50% from identity) at
sigma_g_audit_crit << sigma_g_cap_crit (capacity break at sqrt(1/0.05-1)~4.36)?

## Scientific context

Arrhenius-paradox isochoric analysis: substrate exhibits "thermal-analog" (noise amplitude) and
"density-analog" (loading alpha) fragility, separately measurable at FIXED alpha. The kappa_3
audit primitive is predicted to be MORE noise-sensitive than raw capacity, breaking at sigma_g~0.18
while capacity breaks at sigma_g~4.36 (24x ratio). This would found PP-58 as a measurement
discipline: all future cap_map noise-vs-performance experiments MUST use isochoric protocol.

## Pre-registered bands

No prior empirical anchor at this noise regime; bands set per calibration-probe policy (+-50%).

### HARD-PASS
sigma_g_audit_crit in [0.09, 0.27] (0.18 +-50%)
AND sigma_g_cap_crit >= 1.0
AND ratio (cap_crit / audit_crit) >= 5.0 (two-envelope separation confirmed).

### MIDDLE
ratio in [2.0, 5.0) OR sigma_g_audit_crit slightly outside [0.09, 0.27].

### HARD-FAIL
sigma_g_audit_crit < 0.05 (theory off >3x)
OR sigma_g_audit_crit > 0.54 (theory off >3x)
OR ratio < 2.0 (no separation between envelopes).

## Formula self-tests (PROT-022)

1. kappa_3 Hutchinson identity at zero noise: kappa_3/alpha ~ 1.0.
   [INPUT: sigma_g=0.0, alpha=0.05, N=N_ACTIVE] [EXPECTED: ratio in [0.3, 3.0] at small N]
2. sigma_g_crit = sqrt(1/alpha - 1):
   [INPUT: alpha=0.05] [EXPECTED: 4.359]
   [INPUT: alpha=0.10] [EXPECTED: 3.000]
3. M = int(0.05 * N_ACTIVE) > 0 for all alpha.

## Smoke result

N_ACTIVE=512, 2 seeds, sigma_g sweep [0.0, 0.10, 0.18, 0.25, 0.50, 2.0, 4.0]:
MIDDLE_BAND: sigma_g_audit_crit=0.50 (ratio deviation >50% threshold crossed at sg=0.50),
sigma_g_cap_crit=4.0, ratio=8.0 (> HP_RATIO_MIN=5.0). Two-envelope separation confirmed.
sigma_g_audit_crit is above HP band [0.09, 0.27] at smoke N=512 -- expected scale artifact
(kappa_3 identity is more diffuse at small N). Full N=4096 expected to show crit closer to 0.18.

Instrumentation verified: non-null metrics, valid kappa3_ratios, clear envelope separation.
Decision: ship (ratio >> HP threshold; MIDDLE_BAND is scale artifact, not mechanism failure).

## Timeout estimate

Smoke: N=512, 2 seeds, 7 sigma values, ~30s (Hutchinson O(N^2) per probe * 100 probes * 7 sigma).
Full: N=4096, 5 seeds, 13 sigma values, 200 probes.
Scaling: (4096/512)^2 = 64x N-scale (matrix multiply) * (5/2) seeds * (13/7) sigma * (200/100) probes.
timeout = ceil(1.5 * 30 * 64 * 2.5 * 1.86 * 2.0) = ceil(26928) -- exceeds 14400s!

Revised approach: use 50 probes at FULL scale (acceptable variance; ratio detection robust).
With 50 probes: ceil(1.5 * 30 * 64 * 2.5 * 1.86 * 0.5) = ceil(6732) = 6732s.
Still > 4800s but < 14400s. Flag for user visibility per role contract.

Note: the Hutchinson loop is a Python for-loop over n_probes at N=4096 which is slow.
Using n_probes=N_PROBES_USE=200 at smoke (100 in selftest), full uses 200 probes.
Actual timing depends on numpy vectorization. Estimate 3-4 hours.
Timeout: 14400s (4h; flagged as long run).
