# Experiment M2: bundle capacity scaling

**Date:** 2026-05-16
**Phase:** Week 7 molecule experiments (headline)

## Hypothesis

Bundling k role-filler bindings introduces O(k) crosstalk to each filler query. The signal magnitude after FHRR normalization is ~1/sqrt(k) while the interference variance is ~(k-1)/N. Recovery via cleanup should be high while signal beats interference, transitioning when

    1/sqrt(k) ~ sqrt(k/N) -> k ~ sqrt(N)

For N=1024 this gives a transition around k=32. We sweep k in {2, 5, 10, 20, 30, 50, 75, 100, 150}.

## Predicted

- Recovery ~ 100% for k in [2, 20].
- Mild degradation at k=30 (the sqrt(N) knee).
- Substantial degradation at k=50.
- Approaching chance (1/200 ~ 0.5%) for k=100+.

## Falsification

- Recovery at k=2 < 95%: substrate is broken; the simplest bundle isn't recoverable.
- Recovery at k=100 > 80%: capacity is much higher than Plate predicts, which would be a finding worth investigating.

## Result (2026-05-16)

| k | recovery rate | mean cleanup similarity | predicted (sqrt(k) signal) |
|---|---|---|---|
| 2 | 100% | 0.634 | 0.707 |
| 5 | 100% | 0.402 | 0.447 |
| 10 | 100% | 0.283 | 0.316 |
| 20 | 100% | 0.199 | 0.224 |
| 30 | 100% | 0.162 | 0.183 |
| 50 | **99.7%** | 0.125 | 0.141 |
| 75 | 96.1% | 0.103 | 0.115 |
| 100 | 87.3% | 0.090 | 0.100 |
| 150 | 70.6% | 0.077 | 0.082 |

## Takeaway: capacity is much higher than the sqrt(N) Plate knee predicts

I expected substantial degradation at k=30-50 (the canonical sqrt(N) knee). Real curve stays at >99% recovery through k=50 and only drops below 90% at k=100. Why?

The signal magnitude does decay as theory predicts (1/sqrt(k) close to empirical mean similarity in column 3). But cleanup memory is more forgiving than naive crosstalk models assume: a query needs only to be *closer* to its true filler than to any random codebook atom — not close in absolute terms.

The relevant theoretical threshold is **signal mean >= max-junk floor**. For our 200-filler codebook at N=1024:

    max_junk ~ 1/sqrt(2N) * sqrt(2 ln 200) = 0.072

    signal mean ~ 1/sqrt(k)

Equality at k = 1/(0.072^2) = 193

So we'd expect 50% recovery around k=200 (where signal crosses junk floor) and near-chance for k >> 200. Empirically we see 71% at k=150 — consistent with the boundary being at k~150-200, not k=32.

**This overturns the casual "FHRR capacity is sqrt(N)" claim** for our setup. The real capacity is set by:
- Signal vs junk-floor crossover (depends on codebook size, not just N)
- Cleanup tolerance to signal-with-correct-mean-but-noise-around-it

## Implications

For Week 8 scaling-law experiment, the relevant exponent isn't `capacity ~ sqrt(N)`. It's likely `capacity ~ N / log(pool_size)`. This is exactly the kind of empirical exponent Week 8 should fit explicitly.

For M5 (Hebbian-augmented bundling), the operating region where the substrate is brittle is k > 75 (degradation visible) at N=1024 with a 200-filler pool. M5 should test whether learning can shift the curve up in this regime.
