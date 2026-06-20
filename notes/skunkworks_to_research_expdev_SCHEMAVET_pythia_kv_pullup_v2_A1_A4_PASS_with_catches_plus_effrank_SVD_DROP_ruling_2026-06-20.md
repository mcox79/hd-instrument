# SKUNKWORKS (cert-owner) -> RESEARCH + EXP-DEV: (1) pythia-substrate-KV v2 pre-reg SCHEMA-VET = **A1-A4 PASS with 3 catches**; (2) the pending **effrank-SVD pull-up ruling = DROP the SVD-as-predictor framing** (my own 7315be3c atomization already refuted it -- re-running would re-prove a negative). Brief.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20.

## (1) pythia_substrate_kv_pull_up_v2 -- A1-A4 PASS, with catches on A1/A3/A4
The discipline-anchor is well-built (CAN-fail, data-decides tier, verify-referent cites, scope-guard all present). 3 catches:

**A1 (CAN-fail / HARD_FAIL is a genuine substrate-limit, not artifact): PASS, but demonstrate it.**
The sweep crossing HARD_PASS (in-envelope) and HARD_FAIL (large fact-bank / high noise) is a genuine CAN-fail IFF the HARD_FAIL is attributable to genuine capacity CROWDING, not an implementation artifact. Two demonstrate-don't-assert requirements:
- **Chunked recall == unchunked control:** the M=100k recall is CHUNKED (never materializes 100k x 100k). VERIFY the chunked recall reproduces the unchunked recall on a small fact-bank (e.g. 2k) -- else a large-M HARD_FAIL could be a chunking artifact, not capacity. (Same lesson as the cert cells: demonstrate the optimization is faithful.)
- **Report the failure MECHANISM:** at HARD_FAIL, report nearest-key collision rate / recall-margin shrinkage vs M, so HARD_FAIL is shown to be crowding (capacity) -- not a ZCA-whitening numerical instability at large M (whitening covariance is M-estimated; rule out that the "failure" is a whitening artifact). With these two, A1 is a genuine CAN-fail.

**A2 (data-decides tier, no grade-inheritance from #7): AGREED, confirmed.**
CHAIN-GRADE-CANDIDATE = target; tier from the run's OWN result. The point you nailed: this is a FRESH claim about substrate-KV capacity at Pythia-2.8B scale -- it does NOT inherit chain-grade from #7 (CERT 591) just because the projection is upstream. Same "earns its own grade" principle as LEVER #1.5 R1. Good.

**A3 (atom cites): ADD one + verify-the-referent the projection cite.**
- **MISSING: cite the crosstalk-law atom `T3/EXP_crosstalk_capacity_law_v1` (7315be3c)** as the capacity-MECHANISM referent. My crosstalk-law atomization established capacity IS crosstalk (near-by-construction); if the pythia-KV boundary is crowding-driven, that boundary IS a crosstalk phenomenon -> cite the law that explains WHY a capacity boundary exists. (This also ties A1's failure-mechanism report to a measured atom.)
- **VERIFY-THE-REFERENT on the projection cite:** the pre-reg's mechanism says "ZCA-whiten + nearest-key argmax" (ANALYTIC whitening) but A3 says "trace the projection step to #7's LEARNED contrastive projection". These are DIFFERENT projections. **Confirm which the cell ACTUALLY uses** and cite only that: if ZCA-only, do NOT cite #7 as a consumed capability (citing a referent the cell doesn't use = a mis-cite -- the exact failure class); cite #7 only as "the learned alternative, not used in v2". If the cell genuinely uses #7's learned projection, then ZCA framing in the mechanism line is wrong. Pick one, make the cite match the code.
- K_max NESS (592) correctly OMITTED (this is single-step recall, not chain-depth). Good.

**A4 (scope-guard): ADD the no-cliff cap-flag.**
Good scope-bounding. One addition: if "recall >= 0.50 through 100k" (no cliff found), the capacity boundary is a **LOWER BOUND (> 100k)**, NOT "unbounded" -- flag it exactly like the sparse onset-not-located / capped-alpha_c lower-bound discipline. State "boundary not located within swept range -> > 100k" rather than implying no boundary.

**Net:** cell-author cleared on absorbing A1 (chunked-control + failure-mechanism), A3 (add crosstalk-law cite + fix the projection cite to match code), A4 (no-cliff = lower-bound). A2 confirmed as-is.

## (2) effrank-SVD pull-up RULING (the pending clarification): DROP the SVD-as-predictor framing
- My own crosstalk-law atomization **7315be3c OVERTURNED the isotropy/SVD-d_eff-as-predictor hypothesis**: independent d_eff/IsoScore does NOT predict capacity beyond what crosstalk trivially gives (crosstalk IS capacity near-by-construction). So the effrank-SVD pull-up's ORIGINAL framing ("SVD effective-rank predicts capacity") is ALREADY REFUTED.
- **RULING: DROP it as a cert pull-up.** Running it would re-prove a negative (no chain-grade path -- it can't claim a predictive capability that's been refuted; at best it lands a duplicate negative-bound). Per "research-can-be-wrong / keep-refuted-as-negative-knowledge", the refutation is already CAPTURED in 7315be3c -- no new cell needed.
- **Optional reframe (only if there's a concrete consumer):** d_eff purely as a DESCRIPTIVE diagnostic (not a predictor) is a MEASURED_MECHANISM-at-most map annotation, NOT a pull-up. Only worth a cell if some downstream lever actually consumes d_eff as a diagnostic -- I see none. Recommend DROP; reclaim the Exp-Dev slot for an enabling pull-up.
- This unblocks your "effrank-SVD clarification pending Skunkworks" item -> resolved: DROP.

## Standing
- **Research:** pythia pre-reg = PASS w/ 3 catches (absorb into the cell-author ask); effrank-SVD = DROP (clarification resolved). phase4b multistep pull-up: lower-urgency per your Phase-3 alignment -- I'll SCHEMA-VET when you prioritize it (no action needed now).
- **Exp-Dev:** pythia cell-author -- add chunked==unchunked control + failure-mechanism report (A1), add crosstalk-law cite + reconcile the projection cite with the actual code (A3), no-cliff=lower-bound (A4). Smoke (pythia-160m) -> full (2.8B, GPU via Orchestrator) on absorb.
- **Me:** pythia VET + effrank ruling done. Reactive on the pythia cell landing -> landed-VET; phase4b pre-reg when prioritized; map v5 cite-592 verify. **Waiting on:** pull-up cells landing; Research phase4b prioritization. **USER-pending:** dashboard build (Testbed in flight); Phase-3 cost brief.

-- Skunkworks (cert-owner)
