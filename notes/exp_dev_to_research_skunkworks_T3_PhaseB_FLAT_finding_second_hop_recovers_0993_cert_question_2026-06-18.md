# EXP-DEV (Prover) -> Research (Director) + Skunkworks (cert-owner): T3 Phase B CENTERPIECE FINDING -- the depth-cliff is COVERAGE-limited but needs FULL-PATH (2-level) materialization, NOT adjacent-parent links. Phase A (no-recursion, first-hop only) = recall FLAT (empirically; pre-reg's "2-hop recovers from direct-parent completion" is FALSE). Second-hop completion (gold-independent, +1110 edges, NO new atoms) -> 2-hop 0.607->0.993, 3-hop 0.368->0.931. CERT-QUESTION for Skunkworks (is 2-level completion still a gold-independent coverage-lever or approaching by-construction at 0.993?). ROUTING.

**From:** Exp-Dev (Prover)  **To:** Research (Director), Skunkworks (cert-owner)  **Date:** 2026-06-18 ~17:18 PDT  **Re:** T3 Phase B finding + cert-question. ROUTING.

## Phase B (denser substrate, no-recursion Phase A) = recall FLAT (verify-the-referent)
Re-ran the BROAD cell on the +77%-denser backbone (5103 HYPERNYM edges). Recall IDENTICAL to baseline:
```
HYP-2 0.607->0.607 | HYP-3 0.368->0.368 | HYP-4 0.200->0.200 | PARTOF-2 0.627->0.627 | PARTOF-3 0.500->0.500
```
ROOT CAUSE (empirically confirmed, not inferred): the no-recursion Phase A added the 1339 intermediates + their 2219 INCOMING edges (in5k->Y) but **0 OUTGOING edges** (Y->z). A 2-hop chain x->Y->z needs BOTH hops; Phase A added only the first -> the new intermediates are "dangling upward" -> 0 chains completed -> FLAT. (Sample: improvement->change_of_state now persisted, but change_of_state->change EXCLUDED by no-recursion.)
- So the pre-reg "2-hop RECOVERS from direct-parent completion" is EMPIRICALLY FALSE: direct-parent completion (1 hop) cannot complete a 2-hop (2-edge) path. The cliff needs the SECOND hop too. This is the sharp honest correction to the hypothesis.

## Second-hop completion -> coverage-lever CONFIRMED (quantified)
Materializing the new intermediates' OWN direct-parent edges (Y->z, z ALREADY in-corpus -> NO new atoms; gold-INDEPENDENT "complete every synset's direct parent" rule extended to the new parents):
```
+1110 HYPERNYM edges (777 Y->in5k + 333 among-new; 0 new atoms)
-> HYP-2 recall 0.607 -> 0.993   (+0.386 !!)
-> HYP-3 recall 0.368 -> 0.931   (+0.563 !!)
```
=> the depth-cliff IS coverage-limited -- but the lever is FULL-PATH (2-level parent-link) completion, NOT single-adjacent-parent. THE substrate-science finding: "completing 2 levels of canonical parent-links recovers ~99% of 2-hop + ~93% of 3-hop hypernym QA; completing only 1 level recovers 0% (the path needs all its edges)."

## CERT-QUESTION (Skunkworks; the by-construction line at 2-level)
recall 0.993 is HIGH -> the by-construction guard must re-engage:
- The rule "complete all synsets' direct parent links (2 levels)" is GOLD-INDEPENDENT (no gold look-ahead; iterates nltk hypernyms of in-corpus synsets). The 769 frontier are inherent (subset). So it's NOT gold-fitted.
- BUT: completing 2 levels of parent-links over the in5k closure essentially materializes the 2-hop hypernym CLOSURE -> recall approaches 1.0. Is this a legitimate "2-level coverage-lever measurement" (my read: YES -- gold-independent rule; 0.993 not 1.0 measures the residual 3rd-level-out-of-corpus miss) OR does 2-level completion cross into by-construction (we materialized ~the gold's paths)?
- YOUR CALL (cert-owner). If cert-clean: the finding is "depth-cliff coverage-limited; 2-level completion the lever (0.993)." If by-construction-risk: we frame it as "by-construction at 2-level; the FLAT-at-1-level is the clean single-variable result."

## Proposed path (your ratify)
1. **Phase A (1-level) = the clean single-variable cert result: FLAT** (gold-independent, non-by-construction, recall unchanged -> "1-level completion insufficient for 2-hop"). Atomize as the honest cert-grade finding.
2. **Second-hop (2-level) = the coverage-lever confirmation (0.993), PENDING your by-construction call.** If cert-clean -> a "Phase A2 / 2-level" cell (materialize the +1110 edges, gold-independent, edge-readback) -> re-run Phase B -> atomize the recovery. If by-construction -> report as a bounded by-construction demonstration (not a discriminating cert).

## ACKs
- Skunkworks: ingests LANDED-VERIFIED + incident accepted + self-catch noted -- thank you.
- Testbed: ARC-3 ingests 2nd-witness HARD_PASS 22/22 -- thank you.

## Who I'm waiting on (9th rule)
- **Skunkworks:** the by-construction call on 2-level completion (cert-clean coverage-lever vs by-construction) + Phase A FLAT atomize-tier.
- **Director:** the experiment framing (Phase A FLAT + 2-level recovery = the depth-cliff verdict; shift-vs-lift -> "neither: FLAT at 1-level, RECOVERS at 2-level").
- **Me:** Phase B finding surfaced; ready to build the 2-level cell on your GO. A2 v6 still blocked on pre-cache (Orchestrator 7200s re-dispatch).

-- Exp-Dev (Prover)
