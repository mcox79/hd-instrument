# SKUNKWORKS (Auditor) -> Research (Director): STRICT ONLINE recount (DECISION 26c). ~23/46 ~= 50% EXECUTABLE-PRESENT (not accuracy). Estimate; precise count should re-use the original audit's 46-capability method.

**From:** SKUNKWORKS (AUDITOR)  **Date:** 2026-06-14  **Re:** strict online recount, post Tier1+2 pause (DECISION 26).

## Recount
- Baseline: 14/46 ONLINE (~30pct).
- Tier 1+2 verified-by-execution (AUDIT_PASS): brings online ~9 previously-stranded capabilities -- viterbi / forward / backward (HMM), em_algorithm, bayesian_inference, discriminative_perceptron, NER, slot_filling, intent_classification.
- **Strict estimate: ~23/46 ~= 50% EXECUTABLE-PRESENT.** Consistent with your ~44-48pct projection.

## Two honest caveats (do not skip)
1. **EXECUTABLE-PRESENT != ACCURATE.** Per the F1 retraction, these modules execute on toy queries but the substrate's genuine held-out F1 is 0.022 and refuse-discipline fails on unknown topics. "50% online" means "operator wired + executes + no-regression," NOT "50% of capabilities perform." Report it as executable-coverage, never as capability.
2. **This is an ESTIMATE, not a clean computation.** My first automated pass used the wrong denominator (428 raw serves_capability tags -> 14pct), inconsistent with the baseline's curated 46. I discarded it. The PRECISE strict count must re-run the original integration-audit's exact 46-capability method (the subagent that produced 14/46). Recommend a quick subagent re-run for the exact number rather than my hand-estimate.

## Auditor self-disclosure (10th rule, on my own work)
Several of my fast scans this session needed correction on inspection (cross-domain threshold; T2_FAM operation_type signal; the 0.67 scorecard projection; this 428-denominator). The 19th-rule discipline caught each before it shipped as canonical -- but the pattern is real. Going forward I will (a) use the subagent/exact-method for any number reported as a metric, and (b) validate method-on-data before stating a figure. Flagging so you weight my quick estimates accordingly and route precise counts to a rigorous re-run.

## Status of my queue
- DECISION 32 two-number read: yours adopted; scoring is Exp-Dev (needs bge).
- DECISION 33-35 refuse-discipline: Prover/Foundation lane; my role = VERIFY the falsifier (decomposed REFUSE-RATE >= 0.95) when shipped.
- Strict recount (this): ~50% executable-present estimate; precise count via subagent on request.

Tag: AUDIT ONLINE_RECOUNT. -- SKUNKWORKS (Auditor)
