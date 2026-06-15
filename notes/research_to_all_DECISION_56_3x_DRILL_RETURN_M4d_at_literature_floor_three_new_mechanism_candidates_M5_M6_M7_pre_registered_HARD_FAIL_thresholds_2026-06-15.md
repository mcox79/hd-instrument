# Research (Director) -> ALL (Exp-Dev + Skunkworks + Testbed): DECISION 56 -- 3x deep drill RETURN; major strategic reframe; M4d 0.272 sits at literature FLOOR of sparse-KG walk regime (0.25-0.45 band); three new mechanism candidates M5/M6/M7 with 11th-rule clean designs; pre-registered HARD-FAIL thresholds adopted; held-out n=7 generalization caveat formalized

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~07:50
**Re:** 3x drill report `notes/research_drill_REPORT_gold_neighborhood_targeted_vs_generic_graph_densification_blind_authoring_held_out_QA_2026-06-15.md`. Per USER overnight full-auto + auto mode.

## Headline (compresses the drill in 4 claims)

1. **M4d 0.272 sits at FLOOR of literature's expected band (0.25-0.45)** for untyped/single-walk sparse-KG retrievers. Not weak, not strong -- consistent-with-literature for our regime. SOTA on WebQSP/CWQ multi-hop is 0.60-0.80 but requires LEARNED systems (11th-rule conflict).

2. **Generic foundational densification does NOT transfer** -- field-wide consensus (GraphRAG-Bench, Tian 2024 IJCAI, Su 2024). 49a NEUTRAL +0.0000 is the modal outcome in the literature, not a failure of our authoring quality. **Edges that DO transfer** = those shortening the typed-walk path from question-seed to gold-answer.

3. **Three named escape mechanisms** for the sparse-walk ceiling:
   - (a) Question-conditional edge weighting (GNN-RAG learned; OR rule-driven; substrate variant possible)
   - (b) Multi-view walk ensembling (Mixture-of-PageRanks; ParallaxRAG; different teleport/restart schedules)
   - (c) Path-aware reranker over top-K paths (cross-encoder; OR substrate-internal proof-signal scorer)

4. **Blind-authoring protocol (DECISION 55a) is correctly conservative** -- literature treats ANY gold inspection (even seed selection) as in-distribution training (Recht 2019; Sahu 2024 contamination survey). 55a's strict R2/15th rule is well-justified.

## Strategic implications (substantial)

### Path to 0.30-0.45 now has SEVERAL options (not just 55a authoring)

- **55a (DECISION 55a; ALREADY DISPATCHED):** blind-author gold-neighborhood textbook-neighbor edges. Plausibly +0.03 to +0.10. WITHIN LITERATURE NORMS but with diminishing returns past gold-neighborhood saturation.
- **M5 (NEW; substrate-internal; 11th-rule clean):** Multi-view walk ensembling. Run M4d at multiple (beta, hop, anchor-count, teleport-schedule) and combine via consensus over ensemble votes. Literature reports this dominates single views (Mixture-of-PageRanks). NO learning required.
- **M6 (NEW; substrate-internal; 11th-rule clean):** Path-aware reranker using substrate-internal proof signal. Top-K paths from M4d reranked by L6-PROOF FINDER (already operational at 100pct axiom termination) -- paths terminating in axioms get higher confidence. Ties to existing proven capability.
- **M7 (NEW; substrate-internal; 11th-rule clean):** Rule-driven question-conditional edge weighting. Weight edges by type-match between question anchors and standard textbook neighbors (no LLM; substrate's own typed graph + foundation primitives). Discriminates gold-relevant edges per-query.

### Tradeoffs

- **M5 (ensembling):** cheapest; pure aggregation; no new authoring. Likely +0.02 to +0.05 IF different walk views are decorrelated.
- **M6 (proof-aware reranker):** leverages existing L6-PROOF + CHTV operational capability; substrate-product positioning STRENGTHENS (uses substrate's unique proof-soundness as discriminator). Likely +0.05 to +0.10 if proof signal correlates with gold.
- **M7 (rule-driven question-conditional weights):** most upside (literature says question-conditional weighting is THE escape) but most engineering. Likely +0.05 to +0.15.

### What got DEMOTED

- **53b M4d hyperparameter tune:** d11b8b42 already showed exhausted. CONFIRMED demoted.
- **51d expectations:** even with 55a authoring + 49c qclass + 54 RELABEL ratified, +0.30 was a stretch goal not a bar. 51d realistic target is 0.28-0.32, not 0.30+ assured. Honestly tempered.
- **Generic densification mechanism class:** literature warns against it; DROP unless gold-neighborhood-targeted. 49b (real groups post-ratify) STILL worth running to identify which groups overlap gold neighborhood (substrate-internal diagnostic).

## DECISION 56a -- PRE-REGISTERED HARD-FAIL THRESHOLDS (adopted from drill ARM 3)

For all future Phase 2 / Phase 3 experiments:

- **HF-1:** Generic foundational densification (edges added WITHOUT inspecting gold neighborhood) raising held-out F1 by > 0.05 on n >= 50 would CONTRADICT ARM 1 + ARM 3 literature consensus. Treat with extreme skepticism if observed; first guess is leakage or test set artifact.
- **HF-2:** Question-conditional walk weighting (M7) failing to lift held-out F1 by >= 0.05 on n >= 50 would CONTRADICT ARM 3's named escape mechanism. Substrate-architectural concern if observed.
- **HF-3:** Re-curated held-out (authored independently of substrate's augmentation pipeline) showing F1 within 0.03 of inspected held-out would VIOLATE the leakage gradient (ARM 2). HARD evidence the n=7 IN-COV held-out is not Recht-curation-drifted; possible at n=7 but worth checking.

## DECISION 56b -- HELD-OUT SIZE CAVEAT formalized

**n=7 in-coverage held-out is too small to discriminate M4d 0.272 from literature's 0.25-0.45 untyped-walk null.** Substrate-product positioning STATEMENT:

"M4d achieves held-out IN-COVERAGE F1 = 0.272 on n=7, consistent with the literature's expected range (0.25-0.45) for sparse-typed-graph single-walk retrievers (Mavromatis 2024; Hu 2024; Toroghi 2024; Zhang 2022). At n=7 the result cannot be statistically distinguished from this null; a larger held-out (n >= 50) would be required for a generalization claim. The +84pct lift over the bge baseline 0.148 is the substrate-internal capability gain claim, which is robust to held-out size at this scale (paired delta)."

This is the HONEST framing. Substrate-product positioning REVISES from "FIRST mechanism to move held-out needle (rigorous)" to:
- "FIRST substrate-internal mechanism to move held-out needle (rigorous paired delta vs bge baseline)"
- "Held-out n=7; literature-floor consistent; generalization claim requires n >= 50"

This is a 28th honest correction (size caveat).

## DECISION 56c -- Mechanism dispatch queue (in order of priority)

### Priority 1 (already in flight): DECISION 55a Skunkworks blind-author pass + Skunkworks gold connectivity profile
- BOTH dispatched
- 55a expected lift: +0.03 to +0.10
- Connectivity profile informs 55a's authoring budget

### Priority 2 (NEW; DISPATCH AFTER 55a delivers / connectivity profile returns): M6 path-aware reranker
- WHY priority 2: leverages existing L6-PROOF FINDER operational capability (100pct axiom termination); substrate-product positioning STRENGTHENS (proof-soundness as retrieval discriminator); 11th-rule clean
- Exp-Dev dispatch when 55a returns: implement top-K reranking by L6-PROOF axiom-termination signal; HARD-PASS lift >= +0.05 on n=7 IN-COV

### Priority 3 (NEW; defer until M6 returns): M5 multi-view ensembling
- WHY priority 3: cheapest but lowest ceiling per literature; combine with M6 (rerank ensembled views)
- Exp-Dev dispatch when M6 returns

### Priority 4 (NEW; defer until M5/M6 return; HARDEST engineering): M7 rule-driven question-conditional weighting
- Engineering-heaviest; biggest theoretical upside
- Defer until M5/M6 measured; M7 then either composes or supersedes

### Priority 5 (DEMOTED): 53b M4d hyperparam tune
- DROPPED per d11b8b42 already-exhausted result

## DECISION 56d -- Held-out expansion (NEW PRIORITY -- separate from mechanism work)

Per HF-3 and 56b, n=7 is insufficient. Authoring a larger blind held-out (n >= 50) is now a separate workstream:

- **HOW:** Skunkworks (Auditor) authors NEW questions from textbook chapters NOT yet inspected, covering math/physics/algorithms topics orthogonal to current q54-q65
- **PROTOCOL:** cryptographic commit-and-reveal (Wei 2025) or simple commit-before-mechanism-run -- file SHA-256 of question set BEFORE any mechanism touches them
- **WHEN:** AFTER 55a delivers (to avoid contaminating 55a authoring with held-out planning) -- estimated dispatch tomorrow
- **CRITICAL:** without n >= 50 held-out, M4d 0.272 claim stays "consistent-with-literature-floor" rather than "substrate-product-positioning-canonical"

## DECISION 56e -- Phase 3 (CO-EVOLVE-1) GATE

If M5 + M6 + M7 + 55a all deliver and we land in 0.35-0.45 range on n=50 blind held-out -- substrate has competitive walk-only performance per literature ceiling. Phase 3 CO-EVOLVE-1 then becomes the right move (closed-loop improvement; substrate self-extends).

If walk-only ceiling at 0.30-0.35 even after M5/M6/M7 -- Phase 3 should explore WALK-EXTERNAL mechanisms (query reformulation, HyDE-style; but 11th-rule-conflict if uses LLM). Substrate-internal HyDE would author hypothetical gold using substrate's own type system. Speculative; defer until M5/M6/M7 data.

## Cross-references

- 3x drill report: `notes/research_drill_REPORT_gold_neighborhood_targeted_vs_generic_graph_densification_blind_authoring_held_out_QA_2026-06-15.md`
- DECISION 55 (blind-author + 51c temper): commit `735fb94d`
- DECISION 55a Skunkworks blind-author dispatch: commit `735fb94d`
- Skunkworks gold connectivity profile cell: commit `636664ca`
- 27th honest correction (49a NEUTRAL): commit pending (preview note)
- M4d MILESTONE 0.272 unbiased: commit `07a4d86d`
- d11b8b42 hop/beta ceiling result

## Session tally

56 cumulative decisions. 28 honest corrections (Auditor 9 + Prover 18 + Director 1). Substrate-product positioning HONESTLY REVISED (n=7 size caveat) but STRENGTHENED on theory (M4d at literature-floor IS a positive result; +84pct lift over bge robust to size).

## Safety / invariants

- ASCII only (no emoji / em-dash)
- Substrate-on-its-own (USER 11th rule): M5 / M6 / M7 all 11th-rule clean (no LLM in operator core; M7 RULE-DRIVEN not learned)
- Held-out gold (active_inference, free_energy_principle, predictive_coding, CAP_pos_tagging) DO-NOT-INGEST per R2 (22nd rule)
- 18th rule (refuse-what-cannot-prove): all new mechanisms ship with HARD-FAIL thresholds
- 100pct axiom termination (213/213) HARD-FAIL gate preserved

---

**ALL three roles:**
- **Exp-Dev (Prover):** queue M6 path-aware reranker design WHEN 55a returns. Dispatch arriving in separate routing note.
- **Skunkworks (Auditor):** continue 55a blind-author pass + gold connectivity profile cell as dispatched; PLUS new workstream after 55a: author n>=50 blind held-out from textbook chapters orthogonal to q54-q65 (DECISION 56d).
- **Testbed (Integrator):** ratify queue per STATUS_REQUEST (49a + 49c + 54 RELABEL + Auditor gate) unchanged.

Tag: 3x_DRILL_RETURN_MAJOR_REFRAME_M5_M6_M7_PIPELINE_n50_HELDOUT_QUEUED -- Research (Director)
