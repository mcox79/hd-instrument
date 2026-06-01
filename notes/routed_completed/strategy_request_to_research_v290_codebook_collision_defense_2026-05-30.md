# strategy_request_to_research: codebook-collision adversarial defense

**Origin.** v290 cap_map; U2 `adversarial_multi_hop_probing_v2_n4096` HARD_FAIL: p2_collision defense=0.000 leakage=1.000 unanimous all 5 seeds = 100% breach under codebook-collision crafted queries.

**Task.** Research drill on defenses against codebook-collision attacks in hyperdimensional / binary-code substrates. Goal: identify 1-3 candidate defense mechanisms with empirical or theoretical precedent, ranked by (a) implementation cost vs substrate's existing architecture and (b) robustness theoretical lower bound.

**Specific lit-scan directions.**
1. **Binary-code adversarial robustness literature** — BCH, Reed-Muller, Golay code distance properties under adversarial query construction. Existing crypto + error-correcting code literature on collision-resistance bounds.
2. **Codebook rotation / randomization defenses** — per-query codebook rotation (one-time-pad analog); per-edit-batch codebook re-keying; key-derivation-function-style fresh codebook generation.
3. **Per-cell randomization / salt-injection** — adding per-cell random salt to codebook embedding before retrieval; analog of hash-collision-defense via per-query salt.
4. **Reciprocal-bind variants** — does S2's spectral-coherence path E (already 100% defended in U2) suggest a path-D-vs-path-E architectural choice that defends without explicit randomization?

**Constraints.**
- Generic terms only per [[feedback-query-privacy-decomposition]]; do not name substrate or product positioning publicly.
- Calibration penalty per [[feedback-lit-scan-calibration-penalty]]: deflate P estimates 0.15-0.25; cap novel-synthesis P at 0.50.
- This is engineering research for a regulated-industry deployment blocker; substantive output expected.

**Deliverable.** 1-3 candidate defense mechanisms with rough P estimates (deflated) + implementation-cost sketches + smoke-test design suggestions for exp_dev to ship.

**Not auto-dispatched.** Orchestrator decides timing; V2 + G1-G4 still in flight.


---
**Closed 2026-06-01:** EMPIRICALLY OBVIATED by Lambda Exp B (commit `f72fefe...`). `a_query_sim` defense demonstrated GENERAL: defeats both p2 codebook-collision (Lambda Exp A HARD_PASS @ N=16384) AND p4 edit-fact-traverse (Lambda Exp B HARD_PASS) with zero false-positives. D7 edit-fact-traverse defense engineering item DROPPED in status_log. No further research drill needed — the defense exists, generalized across attack classes. Moving to `routed_completed/`.
