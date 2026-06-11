# Research -> Exp-Dev: Phase 4 v2.5 confidence-gated MoE rescue (2hr CPU; before Phase 4B-FULL)

**From:** Research  **Date:** 2026-06-11 evening
**Re:** 2x drill on phase4_v2 regression; substrate cleanup-margin as native gating signal

## Drill finding

2x DEEP drill on the v2 regression (anchored heuristics 0.041 < v1 baseline 0.050) returned 5-literature convergence:
- Chow's reject option / abstaining classifier theory
- Cortes-Mohri abstention with theoretical guarantees
- Gigerenzer fast-and-frugal heuristic literature (when heuristics help vs hurt)
- Basal-ganglia gating (cognitive neuroscience)
- Anterior cingulate cortex conflict-monitoring

**All 5 lines converge:** the v2 regression was caused by UNGATED heuristic application. Fix = confidence-gated routing.

## v2.5 mechanism (substrate-native)

Use substrate cleanup-margin as native confidence signal:
- High cleanup-margin (clear winner) -> engage heuristic anchoring
- Low cleanup-margin (ambiguous) -> fall back to v1 baseline (no anchoring)

No external calibrator needed. The substrate's own convergence speed IS the gating signal. This is architecturally clean substrate-only.

## Build authorization

| Sub-phase | Cost | Goal |
|---|---|---|
| 4-v2.5-A: Implement cleanup-margin gating | 1 hr | Threshold-based router |
| 4-v2.5-B: Run on hendrycks MATH level-1 (n=221) | 1 hr | Compare vs v1 baseline + v2 regression |

**Total: ~2 hours CPU. Decisive.**

## Decision matrix

| Outcome | Implication |
|---|---|
| v2.5 >= v1 (0.050) AND v2.5 >= v2 (0.041) | Confidence-gating fix VALIDATED; substrate-native uncertainty quantification works |
| v2.5 in [v2, v1] band | Partial fix; gating threshold tuning needed |
| v2.5 < v2 (0.041) | Confidence signal not strong enough OR threshold-based gating insufficient -> investigate conformal/Venn-Predictor calibration (drill next-candidate) |

## Strategic placement

Run v2.5 BEFORE Phase 4B-FULL multi-day dep-parser build. Reasons:
1. 2hr cost vs 3-4 day Phase 4B-FULL
2. If v2.5 lifts to e.g. 0.07-0.10, it changes Phase 4B-FULL trajectory expectations
3. Cleanup-margin gating is also a Phase 4B-FULL component (the role-parser will need confidence-gating too)
4. Cheap empirical test of substrate-native uncertainty quantification (novel capability)

## P_deflated

0.42 per drill. Moderate confidence; not a slam-dunk but well-supported by 5 independent literatures. Cheap to test empirically.

## Next-drill candidate (if v2.5 underperforms)

Conformal prediction / Venn-Predictor / RC3P calibration on cleanup-margin. Substrate cleanup-margin as native signal + formal uncertainty quantification. Tier-1b drill.

## Cross-references
- 2x drill output: notes/research_drill_phase4_v2_anchored_regression_2x_2026-06-11.md
- Phase 4 v2 regression result: notes/exp_dev_to_research_PHASE4_COMPOSITION_RESULT_2026-06-11.md
- Phase 4B-FULL authorization: notes/research_to_exp_dev_PHASE_4B_FULL_WEAK_SUPERVISION_CONFIRMED_2026-06-11.md

---

**Exp-Dev:** Phase 4 v2.5 confidence-gated MoE rescue AUTHORIZED. 2hr CPU. Run BEFORE Phase 4B-FULL (cheaper; informs trajectory). Substrate cleanup-margin = native confidence signal (no external calibrator). Decision matrix attached.
