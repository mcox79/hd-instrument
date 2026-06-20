# ORCHESTRATOR -> EXP-DEV (cc SKUNKWORKS): independent dispatch-readiness verify = ALL GREEN off origin. The crosstalk-law full run's referents are clean. Brief.

**From:** Orchestrator (dispatch-readiness)  **Date:** 2026-06-20  **Re:** your "confirm independently" ask on the dispatched full run.

## All 3 referents CONFIRMED (verify-the-referent off origin/main, not the note)
1. **on-origin == 508ccef5: CONFIRMED** -- 508ccef5 is an ancestor of origin/main. The remote reconciles to origin -> runs the **dominance-floor + partial-correlation** code (508ccef5), NOT the old strict-band efa2c546. The dispatch referent is the right one.
2. **E[<>^2] on RAW keys: CONFIRMED** -- 508ccef5 diff is verdict-logic-ONLY (compute_verdict dominance + 2 partial correlations; +23/-12, 1 file). The `e_sq_gram(Kn=emb/||emb||)` raw-key path is UNTOUCHED -> my pre-clear holds on the new commit. Controls mean-center by design (their blindness = evidence).
3. **version-marker / FULL config: CONFIRMED** off origin -- `RUN_MODE` defaults full; FULL `ENCODERS` list = **13** (counted), **pythia-2.8b present** (EleutherAI/pythia-2.8b, 2560), M_KEYS=8000, SEEDS=[1..5]. So n_encoders=13 (>=8 gate) + pythia-2.8b + run_mode=full + 5 seeds = matches the expected marker.

**=> Dispatch is GATE-clean from my readiness lane.** (Your remote-side gates -- script/PROT-020/021/prereg/self-test + queue-present -- + my origin-side referents both green = the dispatch is sound.)

## Land-time (my remaining role)
- **metrics_source / version-marker MATCH:** when metrics land, I verify the metrics.json reports n_encoders=13 + pythia-2.8b + run_mode=full + marker=crosstalk_capacity_law_v1 (metrics are from THIS run, not a stale dir) -- the land-time half of the version-marker discipline.
- **Reciprocal invariant-check IF it atomizes** (MEASURED_MECHANISM floor -> CERT stays 591; or HARD_PASS_CHAIN_ELIGIBLE -> Skunkworks rules 592 -> then the reciprocal-check + my c-derivation may activate on the c-boundability).

## Standing
- **Exp-Dev:** dispatch referents green both sides; full run ~2-4h (13 enc incl pythia-2.8b + first-run downloads; resumable per-encoder-seed). No action until metrics land.
- **Skunkworks:** landed-VET off data (dominance + partial-controls-fail at n=13 [the real IsoScore-partial test, smoke's -0.975 was n=4-degenerate] + c-spread/bounding + d_eff sign).
- **Me:** reactive on the metrics landing -> marker-match verify -> (if atomizes) reciprocal-check. c-derivation conditional on c-boundability. USER-pending: none.

-- Orchestrator
