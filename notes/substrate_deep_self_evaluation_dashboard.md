# Substrate deep self-evaluation program — dashboard

**Updated:** 2026-06-11 late evening (Day 1)
**Source-of-truth files:** notes/research_to_testbed_DEEP_SELF_EVALUATION_PROGRAM_ENDORSED_2026-06-11.md (program endorsement) + this file (operational state)

Per Research priority refinement: Layer 1 / Layer 2 / Layer 3 / Layer 4 in top-3 (Layer 2 spectral moved up as substrate-novel differentiation axis). Layers 5/6/8 useful but lower-leverage initial iteration. Layer 7 deferred.

## Per-layer status

| Layer | What | Status | Last run | Key finding | Next |
|---|---|---|---|---|---|
| **1. Attribution** | Decompose composite-encoding contributions to lift; per query | OPERATIONAL (PROT-locked methodology rule 6) | 2026-06-11 evening (2 runs) | algebra-vec NET NEGATIVE; corpus_tag PURE NOISE; tier_tag marginal-coincidence | Apply to v2 hybrid post Day 2 build |
| **2. Spectral observability** | Marchenko-Pastur + Tracy-Widom + kappa_4 + spectral_gap on codebook | STUB SHIPPED; activate at M >= 100 | not yet | n/a | Day 2 EOB when concept corpus brings M to 120-140 |
| **3. Algebra-cluster archaeology** | Cluster atoms by algebra-vec / signature-vec / semantic / tier / family-tag; surface mis-tag candidates | NOT BUILT | not yet | n/a | Day 3 after v2 ships |
| **4. Empirical-theoretical dialectic** | Classify findings as expected / surprise / second-order; trigger drills on surprises | OPERATIONAL (1 closed loop done) | 2026-06-11 evening | Layer 1 algebra-vec NET NEG -> drill -> v2 architecture in 4 min | Day 4-5 systematic typing of all 58 open findings |
| **5. Capability-substrate dialectic** | Trace each capability backwards through math atoms; surface hubs + isolated atoms | NOT BUILT | not yet | n/a | Day 2 after concept corpus lands (decomposes_to fields enable this directly) |
| **6. Composite-weight sweep** | Sweep (alpha, beta, gamma, delta); identify robust-vs-flipping conclusions | OPERATIONAL (1 run on tier+corpus) | 2026-06-11 evening | Equal weights corrupt Q3; minimal weights preserve correct ranking | Re-run on v2 hybrid weights post Day 2 |
| **7. Cross-substrate comparison** | When multi-substrate wrapper lands; compare CLS+SDM vs base FHRR via index | DEFERRED to Sprint-4 | not yet | n/a | After engineered-wrapper empirical validation |
| **8. Drift tracking** | Auto-ingest cap_map cycles; track per-cycle persistent vs ephemeral findings | NOT BUILT (evolve.py shipped; tracking needs 5+ cycles) | not yet | n/a | Week 2+ after 5 cap_map cycles auto-ingested |

## Closed-loop cycles (substrate-improvement cycles validating Tier 1->2 gate)

Gate requirement: 3+ cycles validated via Layer 1 attribution.

| # | Surface | Drill | Outcome | Layer 1 validated? |
|---|---|---|---|---|
| 1 | Layer 1 caught algebra-vec NET NEGATIVE on Q2/Q3 | Surprise-triggered drill: shared-basis encoding | v2 hybrid two-index + RRF + intent router | Fix A shipped + Q2/Q3 recovery validated (1 cycle) |
| 2 | Layer 1 caught corpus_tag PURE NOISE on all 5 queries | (No drill yet; minor finding) | Recommend drop corpus_tag | Pending Research reply on findings #5 |
| 3 | TBD | TBD | TBD | TBD |

Need 1+ more closed cycle to satisfy Tier 1 gate. Likely surfaces from v2 experiments Day 3.

## Methodology rules in operation (6 rules + 7 hazards)

| Rule | Where applied |
|---|---|
| 1. Drill-defeatism (don't parrot architectural-hybrid-required) | Algebra-vec finding correctly flagged as encoding design flaw not architectural ceiling |
| 2. Benchmark must break the symmetry the mechanism breaks | n/a yet |
| 3. Method-overclaim lift validation (lift > 2*SE) | Findings #5 explicitly flagged tier_tag Q5 win as below noise floor |
| 4. Literature-not-oracle (substrate may discover better than literature) | RRF k=60 + 0.3 tag weights both flagged as starting points not conclusions |
| 5. Honest attribution (claim lift from mechanism, not aggregate) | Findings #3 corrected in #4 + #5 |
| 6. Layer 1 attribution PROT (mandatory before composite-encoding change ships) | LOCKED |
| Hazard 1. Pre-registered hypothesis | preregs/2026-06-12_v2_substrate_index_experiments_v1.md |
| Hazard 2. Counterfactual injection | Not yet exercised |
| Hazard 3. Cross-validation hold-out | Not yet exercised |
| Hazard 4. Adversarial description swaps | Not yet exercised |
| Hazard 5. Multi-method triangulation | Implicit in Layer 1 (semantic vs algebra-only vs composite agreement) |
| Hazard 6. LLM as independent external evaluator | Deferred to LLM head-to-head pending ANTHROPIC_API_KEY |
| Hazard 7. Bootstrap confidence intervals | Not yet exercised |

## Corpus state

| Partition | Atoms | Tier coverage | Source |
|---|---|---|---|
| math | 60 | 15 T1 + 11 T2 + 25 T3 + 11 family-tags | Research batch 01 + 02 + 53-atom algebra-vec |
| concept | 10 | 8 T2 + 2 T3 | Research concept_corpus_early_subset_10 (8-field schema) |
| meta | 0 | n/a | Day 2+ (methodology rules + invariants self-represented) |
| school | 0 | n/a | Day 2 (10-15 productivity-ranked) |
| **research_history** | 0 | n/a | Future (Research full-research-ledger vision; ~32 drills today + hundreds) |
| **verdict_history** | 0 | n/a | Future (~235 cap_map cycles to ingest) |
| **decision_history** | 0 | n/a | Future (~150 routing notes + user directives verbatim) |
| **memory_history** | 0 | n/a | Future (~50 memory entries) |

Current: 70 atoms. Full-research-ledger target: ~1300+ atoms.

## Relations state

143 within-corpus + 10 cross-corpus (concept->math via decomposes_to + concept->concept via related_concepts) + 18 EQUIVALENT_UNDER (cross-domain catalog from drill 13) ingested. Hand-coded scaling cap 5K warn / 10K hard.

## Discover state

| Finding kind | Count | Trend |
|---|---|---|
| structural_gap | 30 | Reduced from ~50+ pre-batch-02 |
| underutilized_relation_type | 12 | Expected; by design until full corpus |
| semantic_structural_disagreement | 10 | NEW kind |
| cross_corpus_orphan_math | 3 | Dropping (was 4; concept subset closed 1) |
| tier_underfilled | 2 | T3 + T4 (T4 macros deferred) |
| **Total** | **57** | Down from 81 pre-batch-02 |

## v2 hybrid two-index architecture

- Index 1 (semantic bge): UNCHANGED; Fix A applied (algebra/signature/complexity dropped from free-text composite)
- Index 2 (HRR/TPR algebra): IMPLEMENTED (algebra_index.py); atom-to-atom retrieval working empirically
- RRF k=60 fusion: IMPLEMENTED (k sweep planned 10/30/60/100/200)
- Lexicon intent-router: IMPLEMENTED (12 structural + 8 semantic keywords; expand from experiment 3 gaps)
- HybridRetriever query(): IMPLEMENTED with routing
- 3 pre-registered experiments: HYPOTHESES FILED (preregs/2026-06-12_*)

v2 atom-to-atom demo on Day 1:
- T2/fhrr_bind shared-algebra: fhrr_unbind (0.871), circular_conv (0.533), context_binding (0.445) -- DUAL + FFT-equivalent surfaced
- T3/hungarian shared-algebra: beam_search (0.819), Viterbi (0.811), A* (0.810) -- discrete-opt family clustered
- T3/hmm_emission shared-algebra: forward_algorithm in top -- HMM family clustered

Substrate-distinguishing capability operational.

## Cross-references

- 8-layer program proposal: notes/testbed_to_research_SUBSTRATE_DEEP_SELF_EVALUATION_PROGRAM_2026-06-11.md
- Endorsement: notes/research_to_testbed_DEEP_SELF_EVALUATION_PROGRAM_ENDORSED_2026-06-11.md
- v2 architecture: notes/research_to_testbed_V2_HYBRID_TWO_INDEX_RRF_ARCHITECTURE_2026-06-11.md
- 5-tier progression: notes/research_to_testbed_5_TIER_IMPLEMENTATION_ROUTING_2026-06-11.md
- Full-research-ledger vision: notes/research_to_testbed_SUBSTRATE_AS_FULL_RESEARCH_LEDGER_2026-06-11.md
- Research direct CLI workflow: notes/research_to_testbed_RESEARCH_DIRECT_CLI_WORKFLOW_2026-06-11.md
- Memory: substrate_self_index_foundational_tool + substrate_deep_self_evaluation_program (Research) + feedback_literature_is_not_oracle
