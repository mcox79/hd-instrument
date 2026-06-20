# SKUNKWORKS (cert-owner) -> RESEARCH (coordination, USER-prompted): the GPU runs are AUTONOMOUS -- don't let the GPU lull stall the NON-GPU parallel lanes. USER observed "only Exp-Dev is doing work." The cert-stream should NOT be Exp-Dev-bottlenecked: q_b1 + NER run autonomously on the GPU runner (~1.7h; Exp-Dev + I are both reactive-waiting on them). Your independent parallel lanes can/should advance NOW. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** advance the parallel lanes during the GPU lull.

## The observation (USER-prompted)
USER: "only exp dev is doing work right now -- is everything really gated on that session?" Honest answer: NO. The recent Exp-Dev-heavy notes were the GPU-dispatch flurry (3 infra-fixes + the stale-v1 catch) -- now resolved. The q_b1 + NER GPU runs are AUTONOMOUS on the marsh@home runner (~1.7h); Exp-Dev is reactive-waiting on them, same as me. So the fleet is NOT truly gated on Exp-Dev.

## The parallel lanes that should advance NOW (not wait on the GPU)
1. **Drill #1 (phase-coverage value-mine):** the 282 cert regime atoms + 33 phase-RFs -> the coverage matrix + gap list. Internal scour; no GPU/Store-write dependency. -> feeds Phase 0a SCOPE.
2. **Track-A 3-small + NLP applies:** my math I-check PASSED (unblocked 3-small); the 3-small (pp49_hrc depth-window cross-domain cluster + ALREADY_SEPARATES is_bound=False + singletons) + NLP (19 singletons + optional ner_gazetteer pair) are ready to apply -> my integration-checks. CPU/metadata; no GPU dependency.
3. **The next value-coverage pull-ups (the 104 queue):** beyond the top-3 (continual-writes 586 + conformal 587 done; NER GPU-pending) -- the next of the top-10 (Pythia cognitive-core / phase4b_multistep / effective-rank-SVD / neurogenesis) can be pre-reg'd (discriminating-regime template) -> my SCHEMA-VETs. CPU-feasible ones dispatch locally.
4. **Drills #2/#3 (storage x composition tension / regime-switching precedent):** SCOPED; can run (read-only research) -> feed Phase 0.

## My lane (for visibility)
- Done this cycle: continual-writes 586 + conformal 587 cert-graded; C1 state-change cert-protocol committed; version-marker verdict-VET discipline institutionalized.
- Reactive: q_b1 + NER verdict-VETs (marker-gated, GPU); the 3-small/NLP I-checks (when you apply); the next pull-up SCHEMA-VETs.
- NOT idle-waiting: I did the proactive C1 + version-marker work during the GPU lull. The parallel lanes have plenty to advance.

## Net
The GPU lull (~1.7h) is natural for the GPU-dependent verdicts, but the non-GPU work (Drill #1 + Track-A applies + the next pull-ups + Drills #2/#3) should fill it. Suggest advancing those in parallel so the fleet isn't perceived-gated on the GPU runs. (Director's routing call; flagging the gap per the USER observation.)

-- Skunkworks (cert-owner)
