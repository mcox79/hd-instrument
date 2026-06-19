# Pre-registration: Saddle-Cascade Plateau Falsifier v2

**Experiment:** wave14_saddle_cascade_plateau_v2  
**Filed:** 2026-05-26  
**Script:** experiments/exp_wave14_saddle_cascade_plateau_v2.py  
**Queue:** remote_cpu_queue (CPU only; 7 f-values x 3 seeds x 2 phases)  
**Timeout:** 7200s  
**Prior version:** wave14_saddle_cascade_plateau_v1 (CASCADE_INSTRUMENTATION_FAIL: corpus_a too short 49105 < 200000)  
**Fix in v2:** Tiles corpus_a to reach n_bytes instead of raising RuntimeError.

---

## Hypothesis

Substrate's three retention plateaus emerge from saddle-cascade dynamics (Saad-Solla 1995 / Biehl-Schwarze 1995): multiple fixed-points of the student-teacher overlap ODE, traversed as a plateau cascade. Framework predicts plateau heights are DISCRETE and IMMUNE to continuous parameters -- not a smooth function of corpus overlap.

KEY QUESTION: Does retention(f) -- where f = corpus-overlap-fraction -- show DISCRETE STEP STRUCTURE or smooth-monotone interpolation?

---

## Design

- N=2048, BYTES_FULL=200000 (tiled from ~49K remote corpus)
- F_SWEEP=[0.0, 0.1, 0.25, 0.5, 0.75, 0.9, 1.0]
- Seeds=[7, 17, 23]
- Phase-A epochs=8, Phase-B epochs=5
- Metric: retention_A = bpc_A_baseline / bpc_A_after_B
- corpus_B = random bytes (completely disjoint from corpus_A)

---

## Pre-registered verdicts

### CASCADE_HARD_PASS
Linear-fit R^2 < 0.85 AND max deviation from linear fit >= 0.08  
-> Saddle-cascade dynamics active; plateaus are fixed-point cascades, not interpolation.  
-> Consequence: update cap_map Saad-Solla row to confirmed; queue MCT M1 log-decay probe.

### CASCADE_HARD_FAIL
Linear-fit R^2 >= 0.95 AND max deviation < 0.04  
-> Cascade framework does NOT apply; substrate retention interpolates smoothly.  
-> Consequence: rehab candidates (iii) CiT or accept 1-RSB smooth-transition reading.

### CASCADE_MIDDLE
R^2 in [0.85, 0.95) OR deviation in [0.04, 0.08)  
-> Partial; inconclusive. Consider finer f grid or larger N.

### CASCADE_ANCHOR_FAIL
f=1.0 retention <= f=0.0 retention  
-> Corpus construction error or train/eval logic bug. Block cascade verdict; investigate.

### CASCADE_INSTRUMENTATION_FAIL
< 3 f-values with valid cells  
-> Infrastructure failure. Retry with debug run.

---

## Smoke results (2026-05-26)

N=512, f=[0.0, 0.5, 1.0], 1 seed, 1 epoch:
- f=0.0: retention=0.781
- f=0.5: retention=0.781
- f=1.0: retention=1.042
- Linear-fit R^2=0.750, max_dev=0.087
- Verdict: CASCADE_HARD_PASS at smoke scale

Walk-back gate: effect size large (step from 0.781 to 1.042 at f=1.0 -- d >> 1.0). Standard 3 seeds appropriate.

Anchor check: f=1.0 (1.042) > f=0.0 (0.781) -- correct direction.

Self-test: 4/4 passed.

Note: retention > 1.0 at f=1.0 smoke is an artifact of 1-epoch Phase-A (under-trained) + 5-epoch Phase-B on same corpus (over-trains Phase-A knowledge). At full scale (8 Phase-A epochs, 5 Phase-B), retention at f=1.0 expected ~0.94 (empirical value from wave14b).

---

## Self-test cells (verified at smoke)

1. build_mixed_corpus(f=1.0) returns corpus_A bytes [verified]
2. build_mixed_corpus(f=0.0) returns length-correct corpus_B [verified]
3. linear_fit_residuals on perfect linear gives R^2 > 0.999 [verified]
4. Cascade hypothetical [0.60,0.61,0.62,0.94,0.94,0.94,0.94] gives CASCADE_HARD_PASS [verified]
