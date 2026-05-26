# Pre-registration: wave14soft_trace (HOLY GRAIL CANDIDATE)

Date: 2026-05-20
Status: Pre-registered, gated
Experiment: [exp_wave14soft_trace.py](../experiments/exp_wave14soft_trace.py)

## Why

Holy-grail research agent finding (this session): the sign() clip on bundles
is information-destroying. Removing it gives THREE capabilities for free:
1. **Calibrated Bayesian uncertainty** - m_tilde[i] is sum of votes; deviation
   from 0 is calibrated log-odds (Binomial CLT at N=4096).
2. **Counterfactual queries** - subtract bound item from bundle; the result
   IS the "what if not stored" state. Pearl L3 retrieval as a primitive.
3. **Smoother degradation past alpha_c** - cliff sharpness is partly an
   artifact of sign clip.

Materials analog: Ising spin (sign-clipped) -> XY/Potts (continuous).
Continuous-magnetization Ising has RSB-rich attractor landscape that sign-
clipped Ising loses.

## Hypothesis (3-axis)

1. ECE_soft < ECE_clip * 0.5 (calibration emerges from algebra)
2. Counterfactual cosine fidelity >= 0.95 (subtract item -> equivalent to without)
3. cliff_steepness_ratio (clip drop / soft drop) >= 1.5 (clip cliff is sharper)

GDPR-grade holy grail: 2 of 3 wins.

## Operational

N=4096, K in {50, 100, 200, 400, 627, 1000, 1800, 3000} (brackets alpha_c*N).
7 seeds. Codebook size M=8192 for ECE measurement (K stored + distractors).

For each (K, seed):
- Build soft bundle m_tilde = sum_k v_k * c_k
- Clipped: m = sign(m_tilde)
- Measure ECE on both via codebook query
- Subtract item k=0 from m_tilde; measure cos to reference-without-k

## Cited mechanism

- Plate 1995 HRR (the foundational "don't clip" school)
- Frady-Sommer FHRR (also continuous-magnitude)
- Yonelinas dual-process (recognition theory; 2002 J Memory & Language)
- Pearl causal hierarchy (2009)
- Holy-grail research agent (this session)

## Expected runtime

Smoke: ~3 sec
Full: ~10-15 min on GPU (8 K values x 7 seeds x ECE measurement)

## Verdict labels

- `SOFT_TRACE_HOLY_GRAIL`: 2+ axes win
- `SOFT_TRACE_PARTIAL`: 1 axis wins
- `SOFT_TRACE_NO_GAIN`: sign clip doesn't measurably hurt
- `SOFT_TRACE_INCONCLUSIVE`: empty data

## What this enables

GRAIL: substrate ships with three native capabilities (calibrated Bayesian,
counterfactual queries, soft degradation) for ZERO architectural cost.
Material physics: substrate moved from Ising to XY regime, accessible to
richer RSB physics.
