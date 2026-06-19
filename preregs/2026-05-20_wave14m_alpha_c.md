# Pre-registration: substrate alpha_c characterization

Date: 2026-05-20
Status: Pre-registered, ready to smoke-test then queue
Experiment file: [exp_wave14m_alpha_c.py](../experiments/exp_wave14m_alpha_c.py)

## Why now

Three independent research agents (capacity/decoders, composition/emergence,
dynamics/criticality) reviewing today's 18 negatives all converged on the same
diagnosis: multiple "saturation" and "cliff" results may be explained by the
substrate operating above its critical capacity alpha_c. The capacity agent
called this out most directly: "the substrate's capacity scaling should be
characterized first, because three of the five negatives are partly explained
by 'we're running above the critical load.'"

We have never measured alpha_c for our substrate. AGS predicts 0.138 for a
random-pattern Hopfield network with Hebbian outer-product W. Our system uses
sum-bundling with cosine cleanup, which has a different (likely lower) alpha_c
set by the binomial SNR floor. Until we know our actual number, every other
capacity-sensitive result is ambiguous.

## Hypothesis (H)

Bundle-cleanup recovery probability crosses 0.5 at K* = c * N / log(N) for
some constant c on the order of 1, consistent with the standard binomial-noise
SNR floor. Equivalently, alpha_c = K*/N decreases slowly with N, and the
log-log slope of K* vs N is approximately 1.

Operationalized success criterion:
- K* locatable (via linear interpolation at recovery = 0.5) at N >= 1024 for
  at least 3 of 4 tested N values.
- Log-log slope of K* vs N falls in [0.85, 1.15].

## Kill criterion

Verdict `ALPHA_C_INCONCLUSIVE` (K* not locatable at the largest N) means our
K-grid was poorly chosen or recovery never crossed 0.5. We do not retry blindly;
we redesign the grid based on the observed recovery curve.

## Operational definition

For each N in {1024, 2048, 4096, 8192} and K spanning K/N in [0.02, 0.30]:
- Generate K random bipolar atoms of dim N.
- Sum-bundle them, sign-binarize.
- For each k, query with atom_k and measure whether the bundle's argmax over
  the K-bank picks back k (distinct recoveries / K).
- Average over 30 trials x 5 seeds.

Linear interpolate K* at recovery = 0.5. Compute alpha_c = K*/N for each N.
Fit log-log K* vs N to get scaling slope.

## Cited mechanism / paper

- Amit-Gutfreund-Sompolinsky 1985, "Storing infinite numbers of patterns in a
  spin-glass model of neural networks" — alpha_c = 0.138 for Hopfield.
- Kanerva 2009, "Hyperdimensional computing" — bundle SNR scaling.
- Frady-Sommer 2020, "Resonator Networks 2" — K/N invariance for resonator.
- Kleyko et al. arXiv:2301.10352 (2023) "Capacity Analysis of VSAs" — recent
  finite-N treatment with several recovery criteria.

## Expected runtime

- Smoke (N <= 512, 1 seed, 5 trials): ~15 sec on GPU.
- Full (N up to 8192, 5 seeds, 30 trials): ~30-60 min on GPU.

## Rigor protocol introduced by this experiment

This script is the template for the new rigor stack:
1. Output dir resolved from `HDLAB_EXP_NAME` env var (no hardcoded names).
2. Verdict logic in a separate function with a self-test (4 synthetic cases).
3. metrics.json is schema-validated before write (raises if any required field
   missing).
4. `--smoke` flag runs smallest config to verify infra end-to-end before
   committing GPU time to the full sweep.

Future experiments should adopt this pattern. The runner should be updated to
set `HDLAB_EXP_NAME=<queue entry name>` before launching scripts, eliminating
the silent-fail bug observed in the wave14*_v2 re-runs (5 of 6 produced output
in wrong directories on 2026-05-20).

## What this measurement enables

If verdict is `ALPHA_C_SNR_LIMITED` and alpha_c is in the 0.03-0.06 range:
- Most K/N cliff results from wave14b/g are explained.
- "Saturation" findings near K = alpha_c * N are not capacity ceilings but
  the cleanup readout failing; switching to alpha-entmax modern Hopfield
  should raise the ceiling substantially.
- Multi-task CL with K_total > alpha_c * N is doomed regardless of mitigation;
  task-id binding becomes the architectural fix.

If verdict is `ALPHA_C_HOPFIELD_LIKE` and alpha_c is closer to 0.138:
- Our delta-rule W is doing more than we credit it for.
- AGS phase diagram applies directly; 40 years of analytical machinery is
  available.
- Aging, BBP transitions, and SK universality predictions apply to OUR system.

Either way, this is the most leverage-per-dollar experiment we have.
