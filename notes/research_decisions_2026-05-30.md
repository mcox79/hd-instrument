# Research decisions -- 2026-05-30

## 2026-05-30 -- tau_pred re-derivation drill (Opus depth-drill on v285 ATC_R2 audit)

**Trigger.** User-dispatched ~30min theory drill: re-derive substrate-physics adaptive-threshold tau_pred function reported in v285 (commit 947b22e) as FIRST INSTRUMENTED CONFIRMATION of framework-prediction sub-component degradation; LABEL-VS-HONEST #144.

**Finding.** Formula tau_pred = 1/sqrt(M_frac*beta) is explicitly labelled 'heuristic' in script line 109 (no substrate-physics derivation exists). Empirical log2_miss values are the formula's own image at tau_emp=0.05 (sweep-boundary tiebreak): log2_miss = 4.32 - 0.5*log2(M_frac) - 0.5*log2(beta), exact match to 9/9 reported cells. Per-cell remote bridge audit: 3/9 cells degenerate (beta=4 best_score=0); 6/9 cells saturated (beta>=10 best_score=1.0 constant across entire sweep); NO empirical optimum was measured in any cell.

**Classification.** (B) framework-degradation reading IS WRONG (no derived prediction existed to be degraded); third-occurrence instrumentation pathology (v283 + v284 + v285).

**Recommendations.** (1) REVERT v285 substrate-physics framework row sub-component-DEGRADED annotation; restore v283 'sub-component remains untested' status. (2) Ship adaptive_threshold_rescue_v3 with non-saturating discriminant + extended tau sweep before any theory work. (3) Adaptive-threshold capability row state should be untested-by-instrument, not degraded. P(v3 instrument yields interior optima) deflated 0.35-0.50 per calibration penalty.

**Note path.** notes/research_tau_pred_rederivation_v1_2026-05-30.md (7 verified internal citations; 0 external).

**Next-drill candidate.** Strategy follow-up: cap_map note correction + adaptive_threshold_rescue_v3 anchor design (instrumentation-class, NOT theory).
