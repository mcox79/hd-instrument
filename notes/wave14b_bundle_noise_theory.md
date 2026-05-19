# Bundle Decomposition Noise Theory: Synthesis

Drafted 2026-05-19 overnight from unbiased mathematical survey of HDC
bundle decomposition. The math is decisive about what causes the
Phase B.2 C2-vs-C1 gap.

## The empirical observation

Phase B.2: C2 (VSA-pool via 14.B extraction) trails C1 (classical
pool with explicit labels) by **0.019 bpc pre-shift** and **0.056 bpc
post-shift** at N=4096, K=4 (so total bundle size B=K+1=5).

## What theory predicts

For bipolar HDC with binding=Hadamard product, bundle b = sum a_i*p_i:

**Decomposition signal-to-noise** (Plate 1995, Kanerva 2009):
- `v := b * p_k = a_k + noise`
- `SNR = sqrt(N/B)` standard deviations of margin

For N=4096, B=5: SNR = sqrt(819) ≈ 28.6 standard deviations of
separation between target and distractor in cosine space.

**Hard-retrieval error** (union bound + Gaussian tail):
```
P(error) <= (M-1) * Phi(-sqrt(N / (2B-1)))
         <= (M-1) * Phi(-sqrt(4096/9))
         <= (M-1) * Phi(-21.3)
         ~ (M-1) * 10^{-100}
```

For M=256 (byte vocab): predicted error rate ~ 10^{-97}. Essentially
zero. Confirms our scaling sweep finding (100% recovery up to N=65K)
is what theory says.

**Expected cross-entropy excess** (Eq. 6 of survey, calibrated regime):
```
E[L]_min ~ (M-1) * exp(-N / (2(2B-1)))
        ~ 256 * exp(-227.6)
        ~ 0 (literally < 10^{-95} bpc)
```

**Theory predicts zero added CE from bundle decomposition** in the
Bayes-optimal readout. Our 0.02-0.06 bpc observation is ~100 orders of
magnitude away from the theoretical minimum.

## What this means

The CE gap is **NOT** information loss in the bundle. Possibilities:

**(a) Uncalibrated softmax readout** — most likely.

The Bayes-optimal LLR for v = a_k + noise (noise variance B-1) is
`2v/(B-1)`, not raw v. The survey's exact diagnostic:

> A diagnostic: replace v with sigma(2v/(B-1)) before the readout
> and see if the 0.02/0.06 collapses. If it does, the loss is
> calibration.

In our Phase B.2, target extraction reads:
```python
target_estimates = bundle * target_pos    # = a_k + noise
byte_scores = (target_estimates @ byte_atoms.T) / N   # raw v, not calibrated
P_byte = softmax(BETA * byte_scores)
```

The fix:
```python
target_estimates = bundle * target_pos
target_calibrated = target_estimates * (2.0 / (B_bundle - 1))   # B_bundle=5, factor=0.5
byte_scores = (target_calibrated @ byte_atoms.T) / N
P_byte = softmax(BETA * byte_scores)
```

This is a one-line change. Tests the calibration hypothesis directly.

**(b) Position-key reuse** — small contribution.
**(c) Empirical-vs-Gaussian gap** at small B — minor.
**(d) Distractor co-activation** — survey ruled out (theory says 0).

## Diagnostic experiment design

**Wave 14.B Phase B.2-LLR**: same as B.2 but with LLR calibration in
the predict_pool_vsa function. If C2-vs-C1 gap collapses to <0.01 bpc:
calibration was the entire story. If gap persists: downstream
representation mismatch (more interesting / harder finding).

Pre-registered prediction:
- If gap closes to <0.005 bpc: calibration hypothesis confirmed.
- If gap remains 0.04+ bpc: hypothesis falsified, dig deeper.

## Why this is a big deal

If the calibration fix works, **C2 matches C1** on perplexity. That
means:
1. VSA-pool encoding is "free" — no information loss vs explicit dictionary
2. C3 (compositional retrieval) now only needs to beat C1 by ANY
   margin to be a win (no 0.06 bpc overhead to overcome)
3. The pre-registered headline test is much easier to clear

If it doesn't work, the empirical 0.02-0.06 is more interesting and
needs deeper investigation.

## Implications for the platform claim

Survey also confirms our scaling sweep result was theoretically
expected:
- At N=4096, B=5: WTA correctness above 1-eps requires N ≥ 2 B log(M/eps)
- For M=256, eps=0.001: required N ≥ 2*5*log(256000) ≈ 125
- We have N=4096 (32x over). Even at N=65536 with B=128:
  required N ≥ 2*128*log(M/eps) = 256*log(256000) ≈ 3200. We have
  ~20x margin.

So the scaling sweep's 100% recovery isn't lucky — it's exactly what
the math says. Strong confidence in scaling to even higher N.

## Bibliography (from agent survey)

- Plate, T. A. (1995, 2003). Holographic Reduced Representations.
- Kanerva, P. (2009). Hyperdimensional computing introduction.
- Frady, Kent, Olshausen, Sommer (2020). Resonator Networks 1 + 2.
- Kymn et al. (2024). Residue numbers in HDC.
- Schlegel, Neubert, Protzel (2021). VSA comparison.
