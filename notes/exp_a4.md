# Experiment A4: skewed-frequency Hebbian on noisy queries

**Date:** 2026-05-16
**Phase:** Week 6 atomic experiments

## Hypothesis

Under a skewed query distribution where 5 atoms get 5x more queries than the other 25, reward-modulated Hebbian over correct retrievals builds a strong association from frequent atoms to a 'RECOGNIZED' tag. After 1000 queries:

- Frequent atoms have markedly higher Hebbian weight to RECOGNIZED than rare atoms.
- The ratio of mean(frequent weight) / mean(rare weight) should be near the ratio of expected exposures, modulated by recovery accuracy.

## Predicted

- Expected exposure ratio: frequent atoms get ~5x more queries -> if recovery rate is roughly equal, frequent should have ~5x more reinforcements.
- But each pair update grows weight by `arousal * reward = 1` (in the per-step transient regime), capped by `eta / decay = 100` at steady state. So absolute weights depend on counts and how close to saturation each is.
- ratio_freq_to_rare >= 2.0 is the success threshold. (Lower than 5 because recovery is imperfect under noise.)

## Falsification

- ratio < 2.0 means either Hebbian reinforcement isn't tracking exposure, or recovery is so noisy that frequent and rare are getting similar reinforcement counts.

## Result (2026-05-16)

| Check | Predicted | Observed | Outcome |
|---|---|---|---|
| Total correct retrievals | high (noise sigma=0.4) | **1000/1000** (perfect) | confirmed |
| Frequent atoms mean RECOGNIZED weight | high | 9.59 | confirmed |
| Rare atoms mean RECOGNIZED weight | low | 2.08 | confirmed |
| ratio freq/rare | >= 2.0 | **4.61** | confirmed |

## Takeaway

Hebbian co-activation tracks query exposure cleanly. Frequent atoms (5x oversampled) accumulate 4.61x the mean association weight of rare atoms — within ~10% of the raw exposure ratio of 5x. The deviation from a clean 5x match is consistent with two effects:

1. **Lazy decay between updates.** Rare atoms decay more between their sparser updates, pulling their weight lower than the raw count ratio would predict — this *increases* the ratio.
2. **Approach to steady state.** Frequent atoms (~167 updates each over 1000 steps with decay=0.01) sit closer to W_inf = eta/decay = 100; the marginal value of each additional reinforcement diminishes — this *decreases* the ratio.

Both effects cancel partially, leaving us at 4.61.

Cleanup was perfect (1000/1000) at sigma=0.4 because A2 showed N=1024 is robust through sigma=2.0. **For Week 7+ experiments that need to study how learning interacts with cleanup failure, noise must be raised to sigma>=2.5 to start exercising the recovery boundary.**

## Pre-registration check

All predictions confirmed. No falsification thresholds tripped. The first clean "loose training does the expected thing" result.
