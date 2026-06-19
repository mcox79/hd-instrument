# Pre-registration: wave14h_alpha_sweep_v2 (correlated keys)

Date: 2026-05-20
Status: Pre-registered, gated, oracle-asserted
Experiment: [exp_wave14h_alpha_sweep_v2.py](../experiments/exp_wave14h_alpha_sweep_v2.py)

## Why v2

v1 used random orthogonal keys, which give trivial all-or-nothing erase at
alpha=1.0 (no tradeoff curve). v2 uses keys drawn from a rank-L latent
subspace (L=50 for full, n_facts=200) so keys share structure. This matches
the wave14h regime where K-byte context keys share byte prefixes.

## Hypothesis (H)

In the correlated-key regime, some alpha in [0.1, 1.5] gives leak_rate <= 5%
AND kept_recall >= 85%.

Backup: some alpha gives leak <= 15% AND kept >= 75% (Pareto point).

Hard kill: even with alpha=1.5 the mechanism doesn't reduce leak below 30%
or kept_recall below 50%. In that case, anti-Hebbian rank-1 isn't sufficient
under correlation; need extension (multi-step erase, key orthogonalization,
etc).

## Oracle assertions (run in smoke + full)

1. `mean_pairwise_std in [0.05, 0.50]`: keys are actually correlated, not
   orthogonal (orthogonal would be ~1/sqrt(N) ~= 0.016 at N=4096).
2. `baseline_leak >= 0.70` at max alpha row: substrate stores facts.
3. `abs(baseline_leak - method_B_leak) >= 0.20` at max alpha: Method A vs
   Method B is distinguishable (erase mechanism actually fires).

Any of these failing aborts before the full run, with a SANITY FAIL error.

## Cited mechanism

- ROME (Meng 2022, arXiv:2202.05262): rank-1 W edits for fact editing
- Our anti-Hebbian derivation: notes/wave14g_research_wside_erasure.md
- Plate 1995 HRR: key correlation degrades clean unbinding

## Operational definition

- N=4096, n_facts=200, n_erase=50 (25% erasure)
- rank_L=50: keys live in a 50-dim subspace (n_facts >> rank_L gives strong correlation)
- values: random +/-1 (independent of keys)
- W = sum_i v_i k_i^T / N
- For each alpha in {0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.85, 1.0, 1.2, 1.5}:
  - Method A: W unchanged
  - Method B: iteratively anti-Hebbian erase each k_e (W -= alpha (W k_e) k_e^T / d)
  - Measure leak rate (erased facts still retrievable) and kept recall
- 5 seeds per alpha

## Expected runtime

Smoke (N=512, 2 alphas, 1 seed): ~5 sec
Full (N=4096, 11 alphas, 5 seeds): ~5 min on GPU

## Verdict labels

- `ALPHA_SWEEP_HITS_TARGET`: some alpha gives leak <= 5% AND kept >= 85%
- `ALPHA_SWEEP_PARTIAL`: some alpha gives leak <= 15% AND kept >= 75%
- `ALPHA_SWEEP_NO_FRONTIER`: even Pareto fails
- `ALPHA_SWEEP_INCONCLUSIVE`: empty data (script bug)

## What product decision this enables

HITS_TARGET: GDPR-grade pitch holds in realistic regime. "Math-backed erase
gives <5% leak with <15pp recall cost on correlated-key memories at scale."

PARTIAL: Real but bounded. Pitch becomes "tunable tradeoff," not
"cryptographic guarantee."

NO_FRONTIER: Anti-Hebbian alone is insufficient at our correlation level.
Need to extend (e.g., orthogonalize keys via Householder before erase,
or use multi-step iterative refinement).
