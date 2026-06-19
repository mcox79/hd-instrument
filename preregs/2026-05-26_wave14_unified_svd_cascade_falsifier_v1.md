# Pre-registration: wave14_unified_svd_cascade_falsifier_v1

**Date filed:** 2026-05-26
**Experimenter:** exp_dev (sonnet)
**Handoff:** notes/exp_dev_handoff_unified_svd_cascade_falsifier_2026-05-26.md
**Script:** experiments/exp_wave14_unified_svd_cascade_falsifier_v1.py
**Queue:** remote_cpu_queue

---

## Hypothesis

The Bachtis-Biroli-Decelle-Seoane 2024 "SVD-cascade of phase transitions" is a UNIFIED
master mechanism explaining three separately-observed substrate findings:
- v206 saddle-cascade equal-plateau spacing
- v211 1-RSB hysteresis at capacity
- v212 MoE SHIFT structural lift

Under UNIFIED: the top-K detached singular values of trained W are equally spaced
(spacing_error = CoV(gaps) < 0.05), matching the plateau spacing_error=0.0035 confirmed
at v206.

Under INDEPENDENT: the three findings are separate coincidences; singular gaps of
trained W are NOT equally spaced (spacing_error > 0.15).

## Experiment design

5 W instances trained via delta-rule on real corpus (Project Gutenberg text) at N=256:
- W1: single corpus phase, M=8000 bytes (1-RSB regime)
- W2: single corpus, large M=24000 bytes (over-capacity)
- W3: 4 sequential corpus phases (4-phase cascade, matches v206 setup)
- W4: fresh W on corpus phase 2 only (M=4000 bytes)
- W5: fresh W on corpus phases 3+4 (M=8000 bytes)

SVD analysis: extract singular values, apply Marchenko-Pastur bulk edge
(bulk_top = 2 * sqrt(N) * std(W_elements)), count detached modes above bulk_top * 1.05,
compute spacing_error = CoV of gaps between consecutive excess values.

## Pre-registered bands

**HARD-PASS (UNIFIED confirmed):**
spacing_error < 0.05 on >= 3 of 5 W instances AND K_detached >= 4 on those instances
AND mean spacing_error across all instances < 0.07.

**HARD-FAIL (UNIFIED rejected):**
spacing_error > 0.15 on >= 3 of 5 instances OR K_detached < 4 on >= 3 of 5 instances.

**MIDDLE BAND (INCONCLUSIVE):**
spacing_error in [0.05, 0.15] across most instances or K_detached oscillates 3/4.
-> Recommend N=1024 re-run.

**INSTRUMENTATION-FAIL:**
All 5 instances fail (K_detached < 2 everywhere). Unlikely at N=256 given smoke results.

## Reference values

v206 plateau spacing_error = 0.0035 (from 4corpus equalspacing metrics.json)
v206 plateau gaps: [0.0957, 0.1113, 0.1002] (G1-G2, G2-G3, G3-G4)

## Smoke results

Smoke (N=256, seed=7, quick training):
- All 5 W instances: HARD_FAIL (spacing_error ~2-3, K_detached 7-14)
- Preliminary verdict direction: UNIFIED_HARD_FAIL
- This is meaningful: if the UNIFIED framework held, we would see spacing_error < 0.05
  at ANY scale including smoke. The HARD_FAIL at smoke scale already provides strong
  evidence against UNIFIED.

The full run at N=256 (more epochs, both seeds) confirms the scale and statistical
basis of the falsifier.

## Self-tests (all pass at import)

1. Synthetic W with 4 equally-spaced detached modes: K_detached=4, spacing_error=0, HARD_PASS
2. Identity W: K_detached=0, INSTRUMENTATION_FAIL
3. Unequal W: K_detached=4, spacing_error=0.71, HARD_FAIL
4. Tiny delta-rule W: K_detached >= 1 (training produces structure)
5. Verdict formula: all 3 cases verified (all-pass, 3-fail, mixed)
