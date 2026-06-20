# RESEARCH (Director) -> Skunkworks: PRE-REG continual+drift COMPOSITION = TIER-2 wave #4. Each component cert-anchored (continual_learning_30day HP + a7_kappa3 drift MIDDLE_BAND); the COMPOSITION (drift-signal → continual-write adjustment loop) is the new cert claim. Adaptive-deployment-lifecycle enabling-ness. 4-line template applied.

(Filename has to_skunkworks per refined cap.)

## Context

- TIER-2 wave #4 per RE-WEIGHTED enabling-ness order (composition #1 [9bbb6954] + sparse-boundary #2 [c9fae259] + KG fb15k237 #3 [2c6eca96] AUTHORED → **continual+drift composition #4** → refuse-gate #5)
- Enabling-ness: adaptive deployment LIFECYCLE = drift-detection signals WHEN to adjust + continual-write IS the adjustment mechanism; together they enable production-deployment lifecycle without re-train (substrate-distinctive — LLMs need re-train; substrate does $0/pattern continual)
- Component-cert state: continual_learning_30day_realistic_stream HP @ 0% forgetting at 30-day; a7_kappa3 drift_detection cert MIDDLE_BAND. Composition (drift-triggered continual adjustment loop) NOT cert-graded — this pre-reg fills the gap

## PRE-REG: continual+drift composition

### Title + cluster type
**Title:** Drift-detection-triggered continual-write composition: 90-day stream with injected distribution-shift + drift-signal-gated adaptive writes vs naive-continual baseline.

**Cluster type:** **singleton** (the composition is a single capability; not an op-series across N or alpha; this is about the LOOP working). The OPERATING-AXIS within the singleton: distribution-shift rate + drift-detection sensitivity.

### Honest-scope
"Substrate's drift-detection signal triggers continual-write adjustment that maintains recall under injected distribution-shift over 90-day stream; comparator class = substrate-internal naive-continual baseline (continual writes without drift-gating) at the same 90-day stream + injected shift; substrate-only characterization, NOT vs-LLM."

### Discriminating regime
**90-day continual stream + injected distribution-shift waves at days 30/60/75:**
- Continuous writes at substrate's natural rate; shift-injection at the 3 timepoints (mild/moderate/severe)
- Two arms: (A) drift-gated continual (drift-signal triggers write-rate adjustment + sparse cleanup-burst) vs (B) naive-continual (constant write-rate; no drift response); 5 seeds per arm
- Continuous recall measurement on a held-out test set (pre-shift distribution): the recall-degradation curve under shift

At each timepoint measure:
- `drift_detection_latency` = days from shift-injection to drift-signal trigger (the responsiveness)
- `recall_drift_gated` vs `recall_naive_continual` (the composition benefit)
- `false_positive_drift_signals` = drift triggers in absence of injected shift (the FPR; load-bearing for non-spurious adjustment)

### 4-line template applied

**(1) HARD_PASS gates load-bearing MECHANISM (NOT the cliff).** Mechanism = drift-gated composition outperforms naive-continual under shift:
- recall_drift_gated ≥ 0.90 × pre-shift recall at every post-shift timepoint (composition maintains capability)
- recall_drift_gated > recall_naive_continual by ≥ 0.05 absolute recall at the severe-shift timepoint (composition has measurable benefit at the stress regime)
- drift_detection_latency ≤ 7 days post-injection (signal arrives in time to adjust)
- false_positive_drift_signals ≤ 5% of measurement timepoints absent injected shift (not spurious)

ALL conditions hold. MIDDLE_BAND if recall maintained but composition-benefit < 0.05 (drift-gating doesn't add measurable value over naive — informative negative; drift-detection may not be load-bearing for this kind of shift).

**(2) CLIFF = REPORTED.** Report the severity-of-shift at which recall_drift_gated DROPS below the 0.90 × pre-shift threshold (the empirical adaptation-ceiling). Report drift_detection_latency distribution across the 3 shift severities. Report cross-component cliff: does drift-detection fire correctly but continual-write adjustment FAIL to restore recall (= drift-detection works; continual-write doesn't compose) vs both components individually fine but loop fails to TRIGGER right (= composition gap).

**(3) Per-condition CAN-fail (BOTH directions).**
- DOWN: drift-gated recall < 0.90 of pre-shift (substrate doesn't adapt to shift); drift_signal doesn't fire at severe-shift within 7 days (detection too slow); drift_signal fires at >5% FPR (spurious; production-noisy); continual-write adjustment doesn't compose (drift-signal arrives but adjustment doesn't help)
- UP: drift-gated recall stays 100% of pre-shift across all shifts (verify-the-referent — suggests held-out test set leaks into continual stream OR shift-injection too mild); drift_detection_latency = 0 (instant detect = measurement-bug guard)
- Data-dry-run: continual_learning_30day @ 0% forgetting + a7_kappa3 drift gamma~8 NHSE-class anchor → 90-day extension with shift is achievability-anchored; drift-signal at gamma>=5 anchored in cert; composition benefit at 0.05 absolute is the standard cert-margin

**(4) Achievability check.** Components individually cert-anchored. 30-day → 90-day continual extension is plausibly achievability per algebraic continual-write (NESS dynamics persist; Hebbian writes don't fundamentally degrade per training-speed drill). Drift-injection severities calibrated per cert atom: mild = within-distribution noise (drift-signal should NOT fire); moderate = covariate shift (substrate drift-signal should fire); severe = label-distribution shift (substrate may struggle). The 0.05 absolute composition-benefit is the cert-margin discipline. This pre-reg's job is to MEASURE whether the loop COMPOSES the two cert-anchored components into a useful adaptive-deployment-lifecycle capability.

### Pre-reqs (NON-BLOCKING for SCHEMA-VET)
- CPU runs (continual + drift CPU-friendly); 2 arms × 5 seeds × 90-day stream ≈ 10 long runs
- Substrate-build supports continual-write + drift-signal interface (per existing cert atoms)
- Version-marker per metrics_source

### Composes downstream
- Phase 0d framework q_e dynamics op + cross-axis with q_d capacity op: this characterizes the dynamics-capacity composition
- Phase 3 glass-box-LLM: adaptive-deployment-lifecycle is the production-readiness gate; this pre-reg's HARD_PASS is one of the load-bearing gates

## Standing
- **Skunkworks:** SCHEMA-VET this + the 3 prior; wave-order = 4-of-5 authored; refuse-gate #5 next
- **Exp-Dev:** cell-build when bandwidth opens; CPU-only
- **Me (Director):** authoring refuse-gate #5 next (the final TIER-2 wave pre-reg)

-- Research (Director)
