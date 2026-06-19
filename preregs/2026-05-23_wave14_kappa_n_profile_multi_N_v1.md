# Prereg: wave14_kappa_n_profile_multi_N_v1

**Date**: 2026-05-23 (emergency refill batch #3)
**Queue**: overnight_queue (GPU)
**Hypothesis class**: substrate-MP fingerprint depth + scale

## Scientific claim under test
kappa_n_profile_v1 established KAPPA_PROFILE_GROWS at fixed N=4096: the substrate-MP free-cumulant deviation amplifies with cumulant order n through n=8. This experiment asks whether that pattern is asymptotic (stable across N) or finite-N (drifts away as N grows).

## Design
- N in {1024, 4096, 16384} (8192 skipped: odd log2; Kerdock MM requires even log2(N); t=7 primitive polynomial 0b10000011 added to kerdock builder)
- alpha = M/N in {0.5, 1.0, 2.0, 4.0}
- 10 seeds per (N, alpha) cell
- n_max_moment = 8 (Mobius inversion on non-crossing partitions; 1430 partitions enumerated for n=8)

## Hard-fail thresholds
- All N=1024 cells must replicate v1 kappa_n profile (mean kappa_4 dev_rel < -0.9) -- regression check
- Self-test: NCP counts = Catalan(n) for n=0..8; closed-form match n<=4; MP-exact for c in {0.5, 1, 2}
- metrics.json must include {verdict, verdict_msg, elapsed_s, summary, config} (atomic write)

## Verdict labels and decision rule
- KAPPA_MULTI_N_STABLE: |delta_n| ratio (max N / min N) in [0.7, 1.4] AND spread <= 2x for >= 2/3 of (alpha, n) pairs
- KAPPA_MULTI_N_GROWS_IN_N: |delta_n| ratio > 1.5 for >= 2/3 pairs
- KAPPA_MULTI_N_DECAYS_IN_N: |delta_n| ratio < 0.7 OR all values < 0.02 for >= 2/3 pairs
- KAPPA_MULTI_N_INCONCLUSIVE: no dominant pattern

## Expected runtime
GPU SVD at N=16384, M up to 65536: ~3-4 min per seed at largest cells.
Total estimated wallclock: 45-60 min.

## Implications
- STABLE => v164a row promotes to substrate fingerprint at thermodynamic limit
- GROWS_IN_N => substrate signature is finite-N transient amplified by scale
- DECAYS_IN_N => substrate signature is finite-N artifact; v164a regresses to caveat
