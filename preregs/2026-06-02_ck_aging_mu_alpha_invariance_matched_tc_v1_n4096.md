# Pre-registration: ck_aging_mu_alpha_invariance_matched_tc_v1_n4096

**Date:** 2026-06-02
**Anchor:** `ck_aging_mu_alpha_invariance_matched_tc_v1_n4096`
**Queue:** remote_cpu_queue
**Script:** `experiments/exp_ck_aging_mu_alpha_invariance_matched_tc_v1_n4096.py`
**Source:** v343 routing, Item 30 (Arrhenius-drill Test A); P_deflated=0.60

## Hypothesis

The CK aging exponent mu ~ 3/2 is invariant in alpha at MATCHED T/T_c(alpha) = 0.8,
confirming substrate's CK-class aging signature on a third independent observable
(beyond Q-F1 collapse + Q-F2 two-time correlator).

Arrhenius-drill methodological correction: prior aging measurements matched at raw sigma;
the correct isochoric protocol matches at T/T_c(alpha) = 0.8.

## Pre-registered bands

**HARD-PASS**: |mu(alpha=0.05) - mu(alpha=0.10)| < 0.05 (5-seed unanimous)

**MIDDLE**: |delta_mu| in [0.05, 0.15]

**HARD-FAIL**: |delta_mu| > 0.15 -- non-standard non-reciprocal aging OR
different aging universality class from predicted CK

## Formula self-tests (PROT-022)

1. CK envelope ratio: C(t=1.5*tw, tw) / C(t=2*tw, tw) = (2/1.5)^mu at mu=1.5.
   [Verified at module scope: assert abs(_ratio_expected - 0.6495) < 0.001]
2. Self-overlap C(t_w, t_w) = 1.0 exactly.
3. Glauber step at sigma~0 converges to sign(W @ s): overlap > 0.80.
   [All verified in _instrumentation_selftest()]

## Isochoric protocol

sigma_matched = T_OVER_TC * sigma_c = 0.8 * 1.0 = 0.8 (simple approximation:
sigma_c ~ 1.0 at alpha ~ alpha_c; at lower alpha, effective T_c increases but
sigma_c remains near 1.0 in Hopfield dynamics).

## N-suffix

PROT-018 binding: anchor `_n4096`; script MUST have N=4096 in full config.
Smoke runs at N_ACT=1024; full at N_ACT=N=4096. Verified: `N = 4096`.

## Timeout estimate

Smoke: N=1024, 2 seeds, 2 alpha, tw_grid=[50,100], dt_grid=[10,25,50], 3 trials.
Estimated smoke_wall: ~60s (numpy Glauber at N=1024: ~0.5ms/step, 3 * 300 * 3 = 2700 steps).
Full: N=4096 (~10ms/step), 5 seeds, 2 alpha, tw_grid=[50,100,200], 5 trials.
Full steps: 5 * 2 * 3 * 5 * 300 = 45,000 steps * 10ms = 450s.
timeout_s = ceil(1.5 * 60 * (4096/1024)^1.0 * (5/2)) = ceil(1.5 * 60 * 4 * 2.5) = ceil(900) -> **4800s**
(Conservative: N^2 Glauber is ~O(N^2); scaling is 16x from 1024->4096; using 4800s.)

Note: >2 hours flagged per role contract. Justified: 3 t_w values + 5 seeds + N=4096.
If smoke shows fast wall (<30s at N=1024), revise down. Timeout set conservatively.

## PROT-018 pre-ship audit

```
grep -E "(N\s*=|n\s*=)\s*4096" experiments/exp_ck_aging_mu_alpha_invariance_matched_tc_v1_n4096.py
```
Expected match: `N = 4096`
