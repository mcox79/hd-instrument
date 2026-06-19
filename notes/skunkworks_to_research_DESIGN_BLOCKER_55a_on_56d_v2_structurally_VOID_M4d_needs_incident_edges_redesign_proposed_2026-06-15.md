# SKUNKWORKS (Auditor) -> Research (Director): DESIGN BLOCKER on the 55a/56d-v2 experiment -- it is STRUCTURALLY VOID as specified. M4d reaches an atom ONLY via qualified-form edges INCIDENT to it; 55a (forbidden from touching v2 gold) cannot add incident edges -> 55a CANNOT lift M4d on v2 gold at ANY edge count. +0.03 HARD-PASS is unreachable for the wrong reason. Holding 55a; redesign proposed. (Found while setting up Step 2; empirically verified per 10th rule.)

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 63b Step 2. This supersedes my "proceeding to author 55a" line in the Step-1 delivery note.

## THE PROOF (empirical; 10th rule)
M4d mechanism: a pool atom X gets a consensus boost ONLY if the raw node for X's qualified_id (`math::Tk/X`) is within hop-2 of a bge anchor in the adjacency. That requires at least one walkable edge INCIDENT to `math::Tk/X` in qualified form. (X's short-form edges `Tk/X` are a different adjacency key, never reached from qualified anchors, and even if reached do not map back to X's qualified pool key -- the 28th-finding mechanism.)

MEASURED (M4d-faithful degree = edges M4d's walk can actually use, seeding from atom qualified_id):
- **26 of 28 56d-v2 gold atoms have M4d-faithful degree 0** (cauchy_sequence, compactness, continuity, eigenvalue_eigenvector, spectral_theorem, hessian, lagrange_multiplier, laplacian_matrix, maximum_likelihood, ... all 0; only chu_liu_edmonds and gradient_based_optimizer have 1).
- So 26/28 v2 golds are INVISIBLE to M4d today and will REMAIN invisible unless given a qualified-form INCIDENT edge.

DECISION 63b forbids 55a from touching any held-out gold (incl all 28 v2 gold). Therefore 55a cannot add an incident edge to any v2 gold. Therefore:

**55a edges cannot raise M4d's consensus on v2 gold above 0. The +0.03 HARD-PASS on 56d-v2 is structurally unreachable. Worse: adding edges elsewhere can only push v2 gold DOWN in the top-5 ranking (competitors gain consensus, v2 gold gains none). The experiment can only produce <= 0 delta, and a HARD-FAIL would be misattributed to "M4d does not generalize" when the true cause is "the disjointness constraint made the lift mechanically impossible to test."**

Authoring 20-40 edges under this spec is wasted effort + pollutes the substrate for no measurable test value.

## DEEPER INTERPRETIVE POINT (even if incident edges were allowed)
Suppose we DID allow 55a to author edges incident to the tested gold. A resulting M4d lift would only prove "M4d retrieves an atom once its graph neighborhood is dense" -- which we ALREADY KNOW from the in-distribution result (+0.124). It would NOT demonstrate AUTONOMOUS generalization (the substrate growing its own structure / retrieving new concepts without per-concept manual edge authoring). Manual per-concept edge authoring + re-score is not a generalization test; it is a "did we connect the atom" test. Autonomous generalization is a Phase-3 / self-growth question, not a 55a authoring question.

## WHAT MAKES A CLEAN TEST (the guards that actually matter)
The contamination guard is NOT atom-disjointness (which voids the test). It is:
1. **Edge SOUNDNESS** -- edges must be CHTV-verifiable TRUE textbook relationships. You cannot Goodhart with false edges; true edges are legitimate substrate improvements.
2. **Question blindness** -- the question set is hash-locked BEFORE the edge list is authored, so edges cannot be reverse-engineered from the specific questions.
Atom-overlap between authored-edges and test-gold is FINE under these guards (it is required for any lift to be mechanically possible).

## RECOMMENDATION (pick one; I execute on a ruling)
- **Option A (reframe 55a honestly; my recommendation):** DROP 55a as a "generalization" test. Reframe it as a SUBSTRATE-COMPLETENESS authoring pass: author true qualified-form foundational edges for currently-sparse math atoms (analysis / LA / stats / graphs), CHTV-verified, to raise the substrate's structural completeness. Measure the effect on the REVEALED q54-q65 + 56d benchmarks (already scored; honest "manual enrichment raised M4d on these atoms from X to Y"). Frame as "M4d's in-distribution-amplifier capability extends to any atom we ground with true edges," NOT autonomous generalization.
- **Option B (keep a measured test, fix the guards):** Author true qualified-form edges INCIDENT to 56d-v2's sparse gold atoms (allowed; v2 questions already hash-locked 77ad2f9a... BEFORE this edge list). Commit the EDGE-LIST hash now. Exp-Dev re-scores v2. A lift is honest (true edges + blind questions) and shows "M4d extends to manually-grounded new concepts." Interpret WITHOUT claiming autonomous generalization.
- **Either way:** the genuine "does the substrate generalize on its own" question belongs to Phase-3 CO-EVOLVE-1 / autonomous edge-discovery, not manual 55a authoring.

## STATUS
- 56d-v2 DELIVERED + SHA-locked (77ad2f9a8407fbee0a2057c6ffa4ff6d06b0896659a96dc2c61027a04df7664f); clean second blind benchmark; usable now for any non-incident-authoring mechanism (e.g., M7).
- 55a authoring HELD pending your Option A/B ruling (do not want to author void or mis-framed edges).
- M7 (Exp-Dev) is unaffected and can score on 56d + 56d-v2 cleanly (reweights bge; no graph mutation).

This is the Auditor lane again: I would rather flag a void experiment now than hand Exp-Dev edges that cannot move the pre-registered metric and let a HARD-FAIL be misread as a substrate limitation.

Tag: 55a_56d_v2_STRUCTURALLY_VOID_incident_edge_proof_redesign_A_or_B -- SKUNKWORKS (Auditor)
