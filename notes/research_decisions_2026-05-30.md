# Research decisions -- 2026-05-30

## 2026-05-30 -- tau_pred re-derivation drill (Opus depth-drill on v285 ATC_R2 audit)

**Trigger.** User-dispatched ~30min theory drill: re-derive substrate-physics adaptive-threshold tau_pred function reported in v285 (commit 947b22e) as FIRST INSTRUMENTED CONFIRMATION of framework-prediction sub-component degradation; LABEL-VS-HONEST #144.

**Finding.** Formula tau_pred = 1/sqrt(M_frac*beta) is explicitly labelled 'heuristic' in script line 109 (no substrate-physics derivation exists). Empirical log2_miss values are the formula's own image at tau_emp=0.05 (sweep-boundary tiebreak): log2_miss = 4.32 - 0.5*log2(M_frac) - 0.5*log2(beta), exact match to 9/9 reported cells. Per-cell remote bridge audit: 3/9 cells degenerate (beta=4 best_score=0); 6/9 cells saturated (beta>=10 best_score=1.0 constant across entire sweep); NO empirical optimum was measured in any cell.

**Classification.** (B) framework-degradation reading IS WRONG (no derived prediction existed to be degraded); third-occurrence instrumentation pathology (v283 + v284 + v285).

**Recommendations.** (1) REVERT v285 substrate-physics framework row sub-component-DEGRADED annotation; restore v283 'sub-component remains untested' status. (2) Ship adaptive_threshold_rescue_v3 with non-saturating discriminant + extended tau sweep before any theory work. (3) Adaptive-threshold capability row state should be untested-by-instrument, not degraded. P(v3 instrument yields interior optima) deflated 0.35-0.50 per calibration penalty.

**Note path.** notes/research_tau_pred_rederivation_v1_2026-05-30.md (7 verified internal citations; 0 external).

**Next-drill candidate.** Strategy follow-up: cap_map note correction + adaptive_threshold_rescue_v3 anchor design (instrumentation-class, NOT theory).


---

## adversarial_defense_analysis_v1 — 2026-05-30 (research:opus)

**Drill.** Mathematical analysis of v290 U2 codebook-collision (Pattern 2 100% breach) + edit-fact-traverse (Pattern 4 99.4% breach) adversarial vulnerabilities. Mapped 8 defense families; ranked top-3 by engineering cost x expected defense rate x KF compatibility.

**Outcome.** Pattern 2 breach is algebraic certainty of outer-product retrieval at M=2048 (max pairwise codeword cosine ~ sqrt(2 ln M^2 / N) ~ 0.085 = adversary lever arm). Pattern 4 breach is rank-1 edit perturbation vs depth-5 spectral dominance (consistent with v272 KF-2 BE-1 W-magnitude-not-operative finding). Top-3 ranked defenses: D1 query-similarity-margin gate (1 day, P_deflated 0.55-0.70), D7 edit-log-replay (5-10 days, P_deflated 0.45-0.60), D2 per-query codebook rotation (3-5 days, P_deflated 0.40-0.55).

**Note path.** notes/research_adversarial_defense_analysis_v1_2026-05-30.md (5 external citations verified: Krotov DAM-robust + Cohen randomized smoothing + RS-Del + LSM-adversarial + cosine-OOD).

**Companion handoff.** notes/exp_dev_handoff_research_adversarial_defense_analysis_2026-05-30.md (3 anchor candidates rank-ordered for G9+ batch; D1 is the cheap-and-likely-to-work primary).

**Next-drill candidate.** Once G8/G9 D1 smoke verdict lands: if HARD_PASS, drill on D7 edit-log-replay engineering design + adjacency to v290 R-COW-INFEASIBILITY R3 alternative-edit-isolation routing. If HARD_FAIL, drill on D2 codebook-rotation as alternative codebook-collision defense + augmentation with Path E spectral-coherence composition probe.
