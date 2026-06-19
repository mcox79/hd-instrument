# strategy_request_to_research: edit-semantics-under-adversarial-construction defense

**Origin.** v290 cap_map; U2 `adversarial_multi_hop_probing_v2_n4096` HARD_FAIL: p4_edited defense=0.006 (1/160 queries defended; 4/5 seeds ZERO defense) = 99.4% breach. Substrate retrieves OLD edited fact under adversarial query construction.

**Task.** Research drill on defenses against edit-semantic adversarial attacks. The vulnerability: an adversary crafts a query that bypasses the edit and retrieves the pre-edit value of a fact that has been (apparently) updated.

**Specific lit-scan directions.**
1. **Edit-log-replay vs direct-W-edit semantics** — instead of mutating W in place (current substrate behavior), store edits in an append-only log and replay at retrieval time. Existing literature on log-structured-merge trees + version-vector databases + content-addressable storage edit semantics.
2. **Retrieval-confidence under adversarial query** — does the substrate's per-hop Bayesian posterior signal "this is a high-confidence retrieval" even for pre-edit values? If so, the confidence is mis-calibrated under adversarial construction; literature on adversarial-robust confidence calibration.
3. **Bayesian-edit-distance as defense** — measure how far the adversarial query is from the substrate's natural query distribution; reject queries that look adversarial. Out-of-distribution detection literature.
4. **Differential-privacy edit semantics** — DP literature on noisy updates may suggest a way to make edits "stick" against adversarial queries.
5. **Substrate-architecture diff: does Path D Bayesian-independence helping in T2 edit-isolation translate to U2 adversarial-edit-defense?** — T2 PASS at 45/45 cells; U2 4/5 seeds 0/32 = something architecturally different about adversarial construction. Worth understanding.

**Constraints.**
- Generic terms only per [[feedback-query-privacy-decomposition]].
- Calibration penalty per [[feedback-lit-scan-calibration-penalty]]: deflate P 0.15-0.25; cap novel-synthesis P at 0.50.
- This is engineering research for a regulated-industry deployment blocker; substantive output expected.

**Deliverable.** 1-3 candidate defense mechanisms with deflated P estimates + implementation-cost sketches + smoke-test design suggestions.

**Not auto-dispatched.** Orchestrator decides timing.


---
**Closed 2026-06-01:** EMPIRICALLY OBVIATED by Lambda Exp B (commit `f72fefe...`). The 99.4% breach of p4 edit-fact-traverse is now defended by `a_query_sim` at zero false-positives — same defense that handles p2 codebook-collision per Lambda Exp A. D7 edit-log-replay engineering item explicitly DROPPED in status_log because a_query_sim subsumes its threat coverage. Item 1 (log-replay) and item 2 (confidence calibration) lit-scans no longer needed. Item 3 (Bayesian-edit-distance / OOD-detection) is conceptually what a_query_sim does. Item 4-5 superseded. Moving to `routed_completed/`.
