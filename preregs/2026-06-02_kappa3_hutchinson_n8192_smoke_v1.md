# Prereg: kappa3_hutchinson_n8192_smoke_v1

**Date:** 2026-06-02
**Anchor:** kappa3_hutchinson_n8192_smoke_v1
**Queue:** remote_cpu_queue
**Script:** experiments/exp_kappa3_hutchinson_n8192_smoke_v1.py

## Scientific question

Does the kappa_3 Hutchinson estimator at N=8192 achieve discriminative power consistent
with the Phase-2 spec (4.2% delta-alpha sensitivity, measured as sigma_separation >= 4.0
across Hopfield vs GOE matrix classes)?

## Pre-registered bands

HARD-PASS:
  - min sigma_separation >= 4.0 across all M values
  - kappa_3 theory_ratio (kappa_3_emp / (M/N)) in [0.5, 2.0]

MIDDLE:
  - 2.0 <= min_sigma_sep < 4.0, OR theory_ratio outside [0.5, 2.0] but within [0.1, 10.0]

HARD-FAIL:
  - min_sigma_sep < 2.0 (not discriminative at N=8192)

Calibration probe: first empirical measurement at N=8192; bands +-50% of theoretical
prediction per calibration policy. No prior N=8192 empirical anchor.

## Smoke result (pre-ship gate)

Run: N=8192, n_probes=500, 2 seeds, M in {409, 819}.
Result: HARD_PASS. min_sigma_sep=95.6 (HP>=4.0). theory_ratio=1.23 in [0.5, 2.0].
Smoke elapsed=30.2s.

Walk-back check: smoke effect size d >> 1.0 (sigma_sep=95.6 far above HP=4.0).
No walk-back needed. FULL proceeds at 5 seeds, n_probes=5000.

## Timeout estimate

Smoke: 30.2s at N=8192, n_probes=500, 2 seeds, M_list=[409, 819] (2 values).
FULL: N=8192, n_probes=5000, 5 seeds, M_list=[205, 409, 819, 1638] (4 values).
scaling_exp = 1.0 (linear in n_probes * seeds * M values; DGEMM dominates).
timeout_s = ceil(1.5 * 30.2 * (5000/500) * (5/2) * (4/2)) = ceil(1.5 * 30.2 * 10 * 2.5 * 2)
          = ceil(2265) = 2400s.
Rounded up to 3600s for headroom (first large-N run; DGEMM at (8192, 8192, 5000) may be slower).

## N-suffix binding (PROT-018)

Anchor name contains _n8192; script production N=8192 confirmed.

## Cap_map connection

Validates spectral-MAC primitive (kappa_3 fingerprint) at production N=8192.
Row: live kappa_3 audit trail per-write on moving substrate (pending).
