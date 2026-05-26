# Prereg: wave14_rsb_exchange_mcmc_v1

**Date**: 2026-05-23 (emergency refill batch #3)
**Queue**: remote_cpu_queue (CPU MCMC)
**Hypothesis class**: independent probe of RSB transition on Kerdock-Hebbian W

## Scientific claim under test
Parisi P(q12) shape probes (parisi_pq_kerdock_v*) classify RSB by overlap distribution. An independent and complementary probe is parallel-tempering (PT) swap-acceptance: in a glass transition the swap-rate profile shows a clear minimum near the transition temperature (Hukushima-Nemoto 1996; Hansmann 1997). The autocorrelation time at low T also diverges.

## Design
- N=1024 (CPU MCMC budget bound)
- alpha in {0.05, 0.10, 0.20} (sub- and super-critical AGS regions)
- 12 inverse-temperatures: beta in {0.5, 0.75, 1, 1.5, 2, 2.5, 3, 3.5, 4, 5, 7, 10}
- n_burn=2000, n_collect=8000 sweeps per replica
- swap_period=5 sweeps; alternating odd/even pair swaps
- 5 seeds
- Compute: per-pair swap acceptance rates, per-temperature E history (mean/std/autocorr_lag1), tunneling count

## Hard-fail thresholds
- Self-test 4/4 PASS
- Acceptance rates at beta=0.5 (highest T) must be near 1.0 (paramagnet equilibrates trivially)
- metrics.json validate + atomic write

## Verdict labels
- RSB_PT_TRANSITION_DETECTED: clear acceptance-rate minimum (< 0.2) NOT at boundary, with max/min > 2x for >= half of alpha cells
- RSB_PT_FLAT: acceptance rates uniformly high (min > 0.4) and ratio < 1.5 for >= half cells
- RSB_PT_INCONCLUSIVE: mixed

## Expected runtime
12 replicas * 10,000 sweeps * 1024 spin updates each * 5 seeds * 3 alpha. With pure-numpy synchronous Glauber sweep ~5 ms at N=1024, total ~10,000 sweep-replica seconds per alpha; ~30 min CPU per alpha. Three alphas in parallel via cell loop. Total: ~45-60 min wallclock CPU.

## Implications
- TRANSITION_DETECTED => independent confirmation of glass transition on Kerdock-Hebbian W (cross-validates Parisi P(q12) findings)
- FLAT => no glass transition signature via PT diagnostic; complements/contradicts Parisi findings
