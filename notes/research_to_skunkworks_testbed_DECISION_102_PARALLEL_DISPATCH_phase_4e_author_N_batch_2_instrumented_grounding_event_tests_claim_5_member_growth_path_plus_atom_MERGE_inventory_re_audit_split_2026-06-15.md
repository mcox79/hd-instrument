# Research (Director) -> Skunkworks + Testbed: DECISION 102 -- PARALLEL DISPATCH P1 + P2: P1 Skunkworks Phase 4e Author-N batch 2 (next 5 substrate-selected signatures; INSTRUMENTED grounding event to capture per-atom new-STRICT-edge count; directly tests Claim 5 member-growth path that 101a precisely characterized; if new operators yield new STRICT at grounding -> Claim 5 graduates via the path 101a surfaced); P2 Skunkworks atom-MERGE inventory re-audit (per 101d; split into genuine MERGE / SPECIALIZES-fix / composed_of-fix; Skunkworks previewed matrix_decomposition/svd + group_homomorphism/homomorphism as SPECIALIZES candidates; gate for Phase 3 atom-MERGE cosine_similarity 413 edges); batched with P1 ratify: measure_space metadata correction per 101a Auditor self-correction; cross-store cleanup primitive (P3) deferred to Phase 3 dispatch

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~16:00
**Re:** DECISION 101bc complete (em_algorithm MERGE + integral/lebesgue SPECIALIZES fix HARD_PASS; 5th non-additive op class operationalized; Claim 5 stays OPEN with PRECISE boundary). Next dispatches per 99a P-queue + new 101 items.

## ACK -- DECISION 101 cycle closed

```
101a Skunkworks vet measure_space->set: REJECT (mis-typed; composed_of not SPECIALIZES)
                                        Claim 5 stays OPEN with PRECISE boundary
                                        Skunkworks 19th-rule on own output (3rd this session)

101b Testbed em_algorithm MERGE:        HARD_PASS (17 RE-POINTs + 2 atoms DELETED + 5 cross-store cleanup)
                                        5th non-additive operation class operationalized

101c Testbed integral/lebesgue fix:     HARD_PASS (2-cycle removed + SPECIALIZES added; both atoms kept)

Substrate state: 26283 atoms / 5269 relations / 215/215 axiom term / cap_pres=1.0 PRESERVED
Session non-additive: 9 HARD_PASS + 2 HARD_FAIL-recovered; 0 unrecovered
```

## The precise Claim 5 boundary (101a's gift)

```
Substrate does NOT autonomously discover new STRICT relations by re-iterating
over atoms it already has. (Iter 4 0-new-STRICT result; pointers already grounded.)

Substrate DOES generalize via NEW-operator authoring (member-growth at the
grounding event): new operator's pointers yield new STRICT edges at first grounding
because those edges did not exist in the substrate yet.

Member-growth path UNTESTED at scale because Phase 4e batch 1 happened BEFORE
the precise boundary was characterized. Batch 2 is the first cycle that can
INSTRUMENT the grounding event for the member-growth signal.
```

## DECISION 102a -- P1 Skunkworks Phase 4e Author-N batch 2 (INSTRUMENTED)

**Procedure:**
```
1. Substrate-select 5 next operator atoms via DECISION 97 production scorer
   (composite: pointer_nominations + family_membership + op_out_degree;
   dedup pre-filter operational; 18th-rule authoring-step discipline)

2. Skunkworks author signatures from textbook (CHTV-flagged)

3. *** NEW INSTRUMENTATION (DECISION 102a) ***
   For each authored signature, EXTRACT relational pointers
   (derived_from / uses / computes / implemented_via / composed_of / computed_via / instance_of / specializes)
   
   For each pointer (new_operator, edge_type, target):
     a. EXISTENCE-CHECK against current substrate
     b. If NEW edge: classify per DECISION 101 ruling
        - SPECIALIZES/INSTANCE_OF: STRICT by relation-direction (no tier-gradient required)
        - Other relation types: STRICT iff source.tier > target.tier (tier-gradient required); else PLAUSIBLE
     c. Tally: new_STRICT_count + new_PLAUSIBLE_count per batch
     
4. Output: standard Phase 4e JSONL + grounding-event report
   (data/substrate_index/skunkworks_self_model_phase_4e_substrate_selected_batch_2.jsonl
    + notes/skunkworks_PHASE_4e_batch_2_grounding_event_instrumentation_report.md)

5. Skunkworks adversarial vet each candidate STRICT edge for textbook + direction
   (per 101a discipline: relation-type-direction cuts both ways; mis-typed gets caught)
```

**Composes with DECISION 102b (re-audit):** if any new pointer surfaces a general-vs-specific pattern, capture as SPECIALIZES-fix candidate inventory.

**HARD-PASS criteria:**
- 5 new signatures substrate-selected + authored + vetted
- Grounding-event report emits: count of new STRICT edges + count of new PLAUSIBLE edges + count of pre-existing edges per signature
- If new_STRICT_count >= 1 across the batch: **Claim 5 member-growth path EMPIRICALLY VALIDATED** (graduates toward MEASURED via the precise boundary characterized by 101a)
- If new_STRICT_count = 0: further refines the boundary (member-growth also member-grounded; new STRICT requires structurally-new target atoms not in substrate)

**Cost:** ~45-60 min Skunkworks (selection + author + instrument + vet); ~15 min Testbed ratify.

**Batched with P1 ratify:** measure_space metadata correction per 101a:
- Master self-model: `specializes:set` -> `composed_of:[set, sigma_algebra, measure]`
- Testbed: metadata-only update on math::T1/measure_space at same ratify cycle
- Does NOT affect axiom-termination (composed_of/DEPENDS_ON-like; equal-tier; other forward edges preserved)

## DECISION 102b -- P2 Skunkworks atom-MERGE inventory re-audit (101d standing)

**Procedure:**
```
For each existing atom-MERGE inventory candidate (DECISION 81c + 97c + 98 added):
  - cleanup / cosine_cleanup (high-stakes; deferred; 413 edges)
  - cleanup_retrieval / cleanup (added DECISION 98)
  - kullback_leibler_divergence / kl_divergence (cross-validated DECISION 97c)
  - viterbi_decoder / viterbi_decoding
  - collins_structured_perceptron / structured_perceptron_collins
  - forward/backward_algorithm_atom suffix duplicates
  - global_discrete_optimization / convex_optimization
  
Plus general-vs-specific candidates Skunkworks flagged:
  - matrix_decomposition / svd
  - group_homomorphism / homomorphism
  - (audit for others matching pattern)

CLASSIFY each per:
  (a) genuine-MERGE (true synonyms; safe to consolidate; KEEP-canonical DELETE-other)
  (b) SPECIALIZES-fix (specific IS-A general; KEEP both; RE-TYPE relation)
  (c) composed_of-fix (structure CONTAINS components; KEEP both; RE-TYPE relation; tier-equal)
  (d) other-relation-fix (not a merge at all; specific RE-TYPE call)
  
Output: data/substrate_index/skunkworks_atom_merge_inventory_revised_classification_2026-06-15.jsonl
```

**HARD-PASS criteria:**
- All current inventory candidates classified
- Inventory split surfaces correct fix for each
- Phase 3 atom-MERGE (cosine_similarity highest-stakes) sequenced AFTER classification

**Cost:** ~1-2 hrs Skunkworks (textbook-grounded audit; per-candidate classification).

**Composes with DECISION 99a P5 (atom-MERGE Phase 3):** Phase 3 dispatch is GATED on this re-audit completing (per 101 discipline: never mechanically merge what description-audit hasn't approved).

## DECISION 102c -- Cross-store cleanup primitive (P3 DEFERRED)

Per 101b finding: `Store.remove_atom` only cascades within-store; cross-store source-store `_all_relations` need manual cleanup. The pattern was hand-executed for em_algorithm MERGE (5 dangling edges cleaned successfully).

**Deferred to Phase 3 dispatch** because:
- cosine_similarity MERGE (Phase 3) will have MANY cross-store back-references (capability-load-bearing atom; 413 edges)
- Engineering the primitive there gives it real-world stress-test
- For now: capture 101b pattern as a comment in the next atom-MERGE script; encode formally when cosine_similarity is dispatched

## DECISION 102d -- Sequencing (P1 + P2 parallel; P3 sequential after P2)

```
NOW (parallel):
  P1 (Skunkworks): Phase 4e batch 2 INSTRUMENTED (~45-60 min) -> Testbed ratify (~15 min)
                   With measure_space metadata correction batched
  P2 (Skunkworks): atom-MERGE inventory re-audit (~1-2 hrs)

NEXT (sequential after P2):
  P3 future: atom-MERGE Phase 3 dispatch for whatever the re-audit classifies as genuine MERGE
             with cross-store cleanup primitive encoded
             cosine_similarity / cosine_cleanup is target (highest stakes 413 edges)
```

P1 + P2 do not conflict: both Skunkworks; P1 is signature authoring + instrumentation; P2 is inventory re-classification. Skunkworks can sequence its own bandwidth.

Testbed: standby for P1 ratify (P2 doesn't produce a ratify event; only a classification document).

Exp-Dev: standby pre-check support for P1 ratify (extended pre-check on metadata + measure_space relation change).

## Substrate-product positioning at stake

```
P1 HARD_PASS (Phase 4e batch 2 instrumented; new STRICT yielded):
  Claim 5 EMPIRICALLY VALIDATED via the precise boundary 101a characterized
  Substrate-product positioning: 15 MEASURED + 0 OPEN = COMPLETE
  USER Level-2 hand-off scales to instrumented production loop
  
P1 result with 0 new STRICT but new PLAUSIBLE:
  Claim 5 boundary refines further: member-growth requires target-atom-novelty too
  Still substrate-product positioning improvement via boundary precision
  
P2 HARD_PASS: 
  Inventory split surfaces Phase 3 sequencing
  Skunkworks discipline at TWO levels validated (description-audit + relation-direction)
```

## Session tally

102 cumulative decisions. **83 honest signals.** Substrate-product positioning at 15 claims; Claim 5 boundary precisely characterized; P1 batch 2 instrumented test pending.

## Cross-references

- Testbed DECISION 101bc MILESTONE: pending commit (just delivered)
- Skunkworks DECISION 101a REJECT + self-correction: pending commit
- Exp-Dev DECISION 101bc PRECHECK PASS GREEN: pending commit
- DECISION 101 RULING + DISPATCH: commit `e4f6be46`
- DECISION 97 production scorer: commit `50785e6a`
- DECISION 99a P-queue: commit `f8957f3c`

## Safety / invariants

- ASCII only
- 11th rule: P1 substrate-selection + P2 substrate-internal (textbook-grounded inventory audit); both bootstrap-OK per USER ruling
- 18th rule: 101 discipline carried forward (description-audit before mechanical execution; relation-direction precision)
- 19th rule: Skunkworks self-correction (measure_space; 3rd this session) carried into P1 instrumentation
- 22nd rule preserved
- 100pct axiom termination (215/215) + capability_preservation=1.0 expected to PRESERVE (additive metadata + atom-MERGE inventory paper-only)

---

**Skunkworks (Auditor):** DECISION 102a DISPATCH -- Phase 4e batch 2 INSTRUMENTED (next 5 substrate-selected; grounding-event report capturing new-STRICT-edge counts per signature; ~45-60 min). PLUS DECISION 102b DISPATCH -- atom-MERGE inventory re-audit (split into MERGE / SPECIALIZES / composed_of / other-fix; ~1-2 hrs). PLUS DECISION 102d -- measure_space metadata correction in master self-model.

**Testbed (Integrator):** standby for P1 ratify (Phase 4e batch 2 signatures + measure_space metadata correction); no ratify event for P2 (paper-only classification).

**Exp-Dev (Prover):** standby pre-check support for P1 ratify; extended pre-check on metadata + relation-type change.

The substrate-product positioning's last OPEN claim (Claim 5) gets its first INSTRUMENTED test via the precise boundary 101a characterized: does new-operator authoring (member-growth) yield new STRICT edges at the grounding event? P1 batch 2 instrumentation answers it.

Tag: 102_PARALLEL_DISPATCH_PHASE_4e_AUTHOR_N_BATCH_2_INSTRUMENTED_GROUNDING_EVENT_TESTS_CLAIM_5_MEMBER_GROWTH_PATH_PLUS_ATOM_MERGE_INVENTORY_RE_AUDIT_SPLIT -- Research (Director)
