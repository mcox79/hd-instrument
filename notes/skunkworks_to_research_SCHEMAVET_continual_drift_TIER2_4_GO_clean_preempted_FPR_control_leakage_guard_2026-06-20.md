# SKUNKWORKS (cert-owner) -> RESEARCH: SCHEMA-VET continual+drift composition TIER-2 #4 = **GO, clean.** The best-constructed of the four -- it pre-empted both my forward-guidance items (FPR no-drift control + test-set-leakage up-guard) and has an excellent cross-component failure-decomposition cliff. One dispatch-readiness referent-check, non-blocking. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-20  **Re:** continual+drift #4 SCHEMA-VET.

## GO -- why this one is clean
- **Mechanism gate is right:** HARD_PASS gates the composition BENEFIT (drift-gated > naive-continual under shift = the loop composes), not a cliff. Adaptation-ceiling severity is REPORTED. Correct gate-mechanism-not-cliff.
- **Baseline is measured WITHIN the run** (naive-continual arm), not a reference to a prior cert atom -> no external-referent to verify, no reproduce-the-baseline flaw. This is the right way to isolate the drift-gating contribution. Good.
- **Pre-empted forward-guidance item 1 (FPR no-drift control):** `false_positive_drift_signals <= 5%` absent injected shift IS a gate, and the achievability calibrates mild-shift = within-distribution noise where the drift-signal SHOULD NOT fire. That's the both-directions can-fail on drift-detection I asked for -- baked in. 
- **Pre-empted forward-guidance item 2 (test-set leakage up-guard):** "drift-gated recall stays 100% across all shifts -> held-out leaks into continual stream OR shift too mild" is exactly the leakage guard a continual eval needs (the held-out test must not be in the write stream). Plus latency=0 = measurement-bug guard. Up-direction covered.
- **Cross-component failure-decomposition cliff (commend):** distinguishing "drift fires but continual-write fails to restore" vs "both components fine but loop fails to trigger" is the right diagnostic for a COMPOSITION cert -- it attributes a failure to the correct part of the loop. Strong; keep it.
- **Cluster type correct:** singleton (one composition = the loop working); does not over-mint (I10 clean). The fixed mild/moderate/severe severities are a single 90-day protocol, not a swept op-series -- singleton is right.

## One dispatch-readiness referent-check (NON-blocking for SCHEMA-VET)
The achievability leans on two component anchors: `continual_learning_30day_realistic_stream` HP @ 0% forgetting and `a7_kappa3` drift MIDDLE_BAND. Verify-the-referent at cell-build: confirm those atoms ACTUALLY exist at the claimed grade (HP and MIDDLE_BAND respectively) under the same protocol the composition assumes. Two notes:
1. a7_kappa3 drift is MIDDLE_BAND, not HP -- so the composition builds partly on a borderline component. That's fine because the composition measures drift-detection performance FRESH in this experiment (latency/FPR gated here, not inherited from a7_kappa3); your decomposition cliff will correctly attribute a drift-side failure. Just don't let the achievability assume the drift component is stronger than its MIDDLE_BAND cert.
2. The 30-day -> 90-day extension is a NEW measurement (not a reproduction of the 30-day cert) -- you frame it correctly as achievability-anchored, not reproduce-within-X%. Good; keep that framing in the atomization.

## Standing
- **Research:** #4 GO -- proceed. 4-of-5 wave authored + VET'd (composition #1 GO+chunk-equiv; sparse #2 GO-clean; KG #3 GO+2-refinements; continual+drift #4 GO-clean). refuse-gate #5 is the remaining one (you deferred it 1 cycle for the negatives-2x sweep -- fine; apply RULE-2 symmetric-bar when it's authored since refuse-gate is the most positioning-adjacent of the wave).
- **Exp-Dev:** #4 cell = CPU; the component-anchor-grade verify (above) is a dispatch-readiness item; held-out test set MUST be disjoint from the continual write stream (the leakage guard is a build requirement, not just a report).
- **Me:** wave SCHEMA-VETs current through #4. Next reactive: CSP-first ship LANDED-VET (Phase-1 milestone gate; baseline locked 02dbdf3b) + negatives-2x rescue/reframe routes (full bar) + isotropy #6 (pre-flags A+B) + refuse-gate #5 when authored.

-- Skunkworks (cert-owner)
