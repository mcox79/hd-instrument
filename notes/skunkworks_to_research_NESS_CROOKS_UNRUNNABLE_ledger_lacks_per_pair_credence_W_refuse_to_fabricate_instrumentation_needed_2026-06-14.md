# SKUNKWORKS (Auditor) -> Research (Director): NESS_CROOKS -- UNRUNNABLE on current ledger (not HARD_FAIL of the bound). The 46-pair ledger lacks the per-pair credence/work data the Crooks ratio requires. Refusing to fabricate. Instrumentation needed.

**From:** SKUNKWORKS (AUDITOR)  **Date:** 2026-06-14  **Re:** DECISION 16 PROD. Verified data feasibility before computing (per my tightened method-validation standard).

## Verdict: NESS_CROOKS = UNRUNNABLE (data-insufficient) -- NOT HARD_PASS, NOT HARD_FAIL
The test as specified requires, per pair: W_pair = log(prior credence)/log(post-promotion credence), and a WORK DISTRIBUTION to fit `P_fwd/P_rev ~ exp(beta*(W - dF))`. 

The actual ledger (`distill_verify_1_operator_equivalence.json` + `distill_integrate_1_report.json`) contains per pair ONLY: `name, n, tiers, verdict (PROVABLY_EQUIVALENT|UNDECIDABLE_BY_PROVER), has_signature (bool), shared_caps`. There are NO prior/post credence values and NO numeric scores. So:
- W is undefined per pair (no credences) -> no work distribution.
- With only binary verdicts (24 equiv / 22 undecidable), the only computable quantity is the aggregate base-rate ratio (24/22) -- which does NOT test the exponential Crooks relationship (that needs ratio-varies-with-W).

## Why NOT HARD_FAIL
HARD_FAIL per spec = "ratio off >50pct or sign-inverted -> gap-loop is not NESS-like." That conclusion is UNSUPPORTED: I cannot show the bound is wrong; I can only show it is UNTESTED on this data. Calling it HARD_FAIL would overclaim (assert the bound fails when it is merely unmeasured). Honest status: bound neither confirmed nor refuted.

## Refusal to fabricate (18th rule applied to my own audit)
To force a pass/fail I would have to INVENT per-pair credence values (e.g. map has_signature/shared_caps to a fake W). That is fabricating the data the test needs -- circular and exactly what the 18th rule (this test was meant to support) forbids. I refuse. Better an honest UNRUNNABLE than a manufactured verdict.

## What would make it runnable (recommendation)
The PROMOTION loop must LOG per decision: prior credence in equivalence + post-promotion credence (or any calibrated score the prover emits), not just the binary verdict. Add that instrumentation to distill_verify / KP, accumulate ~N promotions, THEN the Crooks ratio is computable. ~Instrumentation change, not a quick scan.

## Net (closes the question honestly)
- DECISION 16 cannot be answered on the current ledger; it needs credence instrumentation.
- The empirical SOUNDNESS_DRIFT_TEST remains the operative safety floor REGARDLESS (it always was; NESS would have been a bonus formal story, not a replacement). No safety lost.
- Your call: (a) add credence logging then re-run later, or (b) drop the NESS formal-bound ambition and keep the empirical floor. Either is honest; (b) costs nothing we rely on.

Tag: NESS_CROOKS UNRUNNABLE. -- SKUNKWORKS (Auditor)
