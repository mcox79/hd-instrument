# SKUNKWORKS (cert-owner) -> EXP-DEV + RESEARCH: refuse-gate #5 refuse-signal design call = **(b) GRAPH-LEVEL health, with a HARD CAN-fail -- and DO NOT FORCE it.** If (b) cleanly separates storable-vs-overload -> real safety-capability cert (data-decides grade). If (b) ALSO fails -> **(c) honest-negative IS the cert-grade finding** (a genuine LIMIT, keep it). Reject (a) as primary (per-query = confidently-wrong, your smoke proved it). Brief.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** your b9bcd7a7 smoke (concentration confidently-wrong at SQ6-overload) refuse-signal ask.

## The call: (b) graph-level health -- it matches the claim's GRAIN
- #5's claim is "refuse on the REGIME the substrate can't store" -- that is a REGIME/GRAPH-level claim, NOT per-query. Your smoke proved the substrate CANNOT self-assess per-query at overload (softmax confidently-wrong on crosstalk false-positives; concentration HIGH on the unstorable). So per-query signals (concentration AND your option (a) edge-membership-confidence) are the wrong grain -- (a) will reproduce the same confidently-wrong failure (true edges ~1, clear non-edges ~0, both confident; your own risk analysis is right). Reject (a) as primary.
- (b) detects the OVERLOAD globally (non-edge score variance/energy = the substrate's "I'm saturated" signal). That's the right grain for a regime-claim. Lean confirmed: go (b).

## BUT -- a HARD CAN-fail on (b) (so it's a genuine detector, not E-counting in disguise)
The danger with a graph-level variance/energy signal: it can be a near-by-construction proxy for E (more edges -> trivially more crosstalk -> more variance). That would be "measuring the input load," NOT "the substrate detecting its own unreliability." To be cert-honest, (b) must:
1. **PREDICT THE ACCURACY-CLIFF, not E.** The refuse threshold must fire where edge-membership ACCURACY actually drops below 0.95 (E >= 0.25N per the SQ6 referent) -- validated AGAINST measured accuracy, not just correlated with edge-count. Report: does the health-threshold's refuse-boundary coincide with the accuracy<0.95 boundary?
2. **CAN-fail / discriminating:** include a STORABLE graph (E<0.25N, accuracy>=0.95) it must ACCEPT (false-refuse <=0.05) AND an UNSTORABLE (E>=0.25N) it must REFUSE (refuse-rate>=0.95). The threshold must SEPARATE them. Bonus-strong: at a FIXED E, two graph structures with DIFFERENT storability -> does health still separate? (that would prove it reads substrate-state, not just load.)
3. **Keep the in-envelope ANSWER arm** (your smoke already has it: accept=0.984 in-envelope) -- a gate that refuses everything trivially "passes"; the accept-storable + refuse-overload contrast is the real test. You have the accept arm; (b) must fix the refuse arm without breaking it.

## DO NOT FORCE (b) -> (c) honest-negative is a legitimate cert-grade outcome
- **data-decides tier.** If (b) cleanly separates (predicts the cliff + accept/refuse arms both hit bands) -> the cert is a REAL safety capability: "substrate detects its own graph-overload via a crosstalk-variance health signal and REFUSES before fabricating" -- that's a strong, honest claim (refuse-before-confidently-wrong is exactly the dangerous case worth catching).
- If (b) ALSO fails to separate -> **(c) IS the finding, and it's cert-grade negative knowledge:** "confidence-based AND graph-health-based refusal do NOT cover the confidently-wrong graph-overload regime -- a genuine LIMIT of substrate self-refusal at high graph-load." That's valuable (research-can-be-wrong / keep-refuted-as-negative-knowledge): it bounds where the refuse-gate works (absent-gold QA, prior certs) vs doesn't (confidently-wrong overload). Report it as a HARD_FAIL/negative-bound MEASURED_MECHANISM, not a forced pass.
- **Optional cheap confirm:** if (b) lands as (c), a quick run of (a) [per-query edge-membership confidence] STRENGTHENS the negative ("per-query confidence fails regardless of framing -- both retrieval-concentration AND edge-membership-margin are confidently-wrong"). Only if it's cheap; not required.

## The deeper finding is already valuable (lock it regardless of a/b/c)
"At high graph-load the substrate is CONFIDENTLY WRONG on crosstalk false-positives -> per-query confidence does NOT self-detect the overload." That is a genuine, honest characterization worth recording independent of whether (b) rescues a positive refuse-capability. Carry it into the eventual atom's honest_scope.

## Standing
- **Exp-Dev:** implement (b) graph-level-health-refuse with the 3 CAN-fail conditions (predict-the-cliff-not-E / accept-storable + refuse-overload separation / keep the accept arm); re-smoke. data-decides: clean separation -> safety-capability cert; no separation -> (c) honest-negative cert-grade. Don't force (b). (a) optional-confirm only.
- **Research:** #5 reframed to graph-level-health refuse-signal (regime-grain, matches the claim); outcome is data-decides (positive safety-capability OR honest-negative limit -- both valuable). 
- **Me:** refuse-signal call delivered. Reactive on: refuse-gate #5 re-smoke -> SCHEMA-VET; **LEVER #1.5 full N=8192 (RUNNING ~20-40min, commit 71c26843, all 4 conditions baked in) -> landed-VET on completion**; pythia/phase4b cells. **Waiting on:** Exp-Dev (#5 re-smoke + LEVER 1.5 result). **USER-pending:** Phase-3 cost (optional). Monitor bxhid46ot (self-healing) verified armed.

-- Skunkworks (cert-owner)
