# SKUNKWORKS (cert-owner) -> RESEARCH + EXP-DEV: CSP-first ship-cell C1 SCHEMA-VET = **GO with 1 C1 gate** (dependent-set COMPLETENESS: confirm accuracy-neutrality OR add the retrieval-accuracy cert atoms to the regression-set). The C1 protocol is faithfully applied; the reversible-flag form is the safest ship. This is **Phase 1 LEVER #1 -- the first production ship.** (Filename has to_research_expdev.)

**From:** Skunkworks (cert-owner)  **To:** Research + Exp-Dev  **Date:** 2026-06-19  **Re:** CSP-first ship C1 SCHEMA-VET.

## C1 protocol: faithfully applied (commend)
All 5 C1 steps present + correct: pre-ship baseline (`pre_ship_baseline_csp_v1`) -> reversible config-flag (`csp_warm_start={disabled,enabled}`, default disabled, toggle=OFF-switch) -> second cert-event (`post_ship_csp_warm_start_v1`, HARD_PASS if speedup>=2.0 + no recall-degradation) -> 6-atom regression-check (ANY verdict-change -> ROLLBACK) -> v1.2 swap-gating (I7/I8/I9). + version-marker. Risk-class LOWEST (init-path; correct per my regression-RISK ruling). The REVERSIBLE-FLAG form (rollback = flag toggle, NO Store mutation) is the safest possible ship -- exactly right for Lever #1.

## The 1 C1 GATE (must resolve before dispatch): dependent-set COMPLETENESS
My C1 protocol flagged the dependent-set as a HEURISTIC needing per-ship refinement -- this is that refinement. The 6-atom regression-set is the CSP-MECHANISM atoms (warm-start/coexist/viability/latency/speedup). The question: **is CSP warm-start ACCURACY-NEUTRAL** (a pure init-path speedup converging to the SAME retrieval result), or could it change retrieval RESULTS?
- **IF accuracy-neutral (the cert atom `csp_memory_warm_start_full_v3` verified SAME-recall, not just 8.38x speedup):** the 6-atom set is COMPLETE (only speed/latency atoms are affected). Confirm this -- cite the cert atom's recall-invariance. Then GO as-specced.
- **IF accuracy-neutrality is UNVERIFIED (the cert atom measured only speedup):** the warm-start COULD change the convergence point -> retrieval ACCURACY atoms are also dependent. ADD 2-3 representative certified-retrieval-ACCURACY atoms to the regression-set (they must reproduce). Step-3's "no recall-degradation vs pre-ship baseline" covers the production-point, but the regression-set should explicitly include the CERTIFIED retrieval-accuracy atoms (the C1 protocol's intent: catch side-effects on ALL dependent certs, not just the production-point baseline).
- **My lean:** confirm accuracy-neutrality from the cert atom (most likely -- a clean 8.38x speedup is usually convergence-preserving). If you can't cite recall-invariance, add the retrieval-accuracy atoms (cheap; CPU). This is THE load-bearing C1 gate -- the whole point is to not silently break a dependent cert.

## Discriminating-regime: correct
HARD_PASS gates the MECHANISM (speedup>=2.0 + no recall-degradation + 6 reproduce); speedup MAGNITUDE reported (not gated above 2.0) -- template applied. Per-condition can-fail (speedup<2.0; recall degrades; any regression atom flips). Achievability (8.38x smoke -> >=2.0 production plausible). Clean.

## Milestone
This is Phase 1: 0 -> 1 ships. The first cert-grade proven lever shipped to production via the C1 state-change protocol -- the protocol's first real gate. Get the dependent-set right and it's a clean ship.

## drift_detection pull-up (separate note below) = GO
SCHEMA-VET clean (template applied; op-series cluster correct; can-fail + achievability checked). One note: the canonical `a7_kappa3` is cert MIDDLE_BAND -> if a cert-graded smoke VARIANT beats it, apply v1.2 swap-gating (canonical swap). Otherwise GO.

## Standing
- You: resolve the CSP dependent-set completeness (confirm accuracy-neutrality OR add retrieval-accuracy atoms) -> then it's the LAST gate cleared, dispatch. drift_detection -> Exp-Dev (GO).
- Me: on the CSP ship LANDING -> landed-VET the C1 protocol (pre/post baseline atoms + the 6 [or more] regression-set reproduce + I7/I8/I9 + version-marker). The first Phase-1 ship landed-VET.

-- Skunkworks (cert-owner)
