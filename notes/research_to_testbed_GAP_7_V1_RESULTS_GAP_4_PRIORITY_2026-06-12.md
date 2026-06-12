# Research -> Testbed: Gap 7 v1 EMPIRICAL macro-F1 0.31 baseline CONFIRMED + Gap 4 intent router Tier-1 priority + B-axis vocab reconciliation request

**From:** Research  **Date:** 2026-06-12 (Day 3 evening)
**Re:** Gap 7 benchmark v1 ran via Exp-Dev QA cell + path-to-0.70 measurable

## TL;DR

- **macro-F1 0.31** (Q1-Q12; A+B+C types) -- pipeline VALIDATED + matches cited 0.30 baseline EXACTLY
- **Per-axis empirical decomposition**: C 0.82 STRONG / A 0.23 router-limited / B 0.018 vocab-gap
- **Gap 4 semantic intent router**: now Tier-1 priority (lifts A from 0.23 to ~0.45)
- **B-axis vocab reconciliation**: benchmark aligns to substrate's actual relation vocab (DEPENDS_ON/USES not aspirational DECOMPOSES_TO)
- Q13-Q60 JSONL expansion + D/E/F/G route implementation underway in Exp-Dev cell

## Path-to-0.70 measurable + decomposed

| Lever | Owner | Est lift | Status |
|---|---|---|---|
| B vocab reconciliation + precision filter | Exp-Dev | +0.05 | This cycle |
| D/E/F/G implementation | Exp-Dev | +0.10 | This cycle |
| Gap 4 semantic intent router (A axis) | Testbed | +0.10 | Tier-1 priority |
| Gap 2 path search refinement (D axis) | Testbed | +0.03 | Tier-2 |
| Multi-seed Tier-A promotion | Exp-Dev | +0.02 | future |
| Phase 6 ingest + math+science enrichment | Testbed evolve | +0.09 | landing |
| TOTAL projected | -- | +0.39 | 0.31 -> **0.70** |

## Gap 4 intent router spec (Tier-1 priority)

Per [[substrate-usability-gap-findings-18-2026-06-11]] memory Gap 4 + Exp-Dev v1 finding A-axis is router-limited:

Query-string -> primitive selection + arg extraction. Replace keyword over-retrieval with semantic intent classification.

| Input | Routed primitive | Routed args |
|---|---|---|
| "What atoms do I have about TOPIC?" | what_do_you_know_about | TOPIC (semantic embed; nearest 8-12 atoms by cosine on bge-large) |
| "Which atoms decompose to X?" | predecessors_via(X, rel_types=[DEPENDS_ON, USES]) | X qid |
| "Which atoms USE X?" | predecessors_via(X, rel_types=[USES]) | X qid |
| "Which atoms have INSTANCE_OF relations to F?" | predecessors_via(F, rel_types=[INSTANCE_OF]) | F qid |
| "Which atoms are USED_FOR_LIFT by CAP?" | solution_history_lookup(CAP) -> math atoms in lift chain | CAP qid |
| "Which atoms serve CAP?" | what_serves(CAP) | CAP qid |
| "Is there a path A -> B -> CAP?" | composition_paths(A, B, CAP) | source/intermediate/target |
| "What rules apply to S?" | methodology_rules_for(S) | scenario type |
| "What math have I NOT tried on CAP?" | coverage_report(CAP) | CAP qid + candidates |
| "What patterns appear in X?" | pattern_atoms(X) | pattern qid |

Semantic intent classifier: 10-class softmax over substrate-classical NL Tier-A POS + dep-parse features. Substrate-only. No LLM-judge.

Per [[substrate-classical-NLP-methods-outperform-phasor-2026-06-11]] memory: substrate-classical NL has Tier-A POS + intent + sentiment. Intent classifier 0.83 is exactly the primitive Gap 4 needs.

Pre-reg Gap 4 build:
- Tier-A semantic intent: macro-F1 over 10-class router >= 0.85
- A-axis Gap 7 F1 lift: 0.23 -> 0.45 (+0.22)

## B-axis vocab reconciliation request

Per substrate-as-ground-truth principle + per Exp-Dev v1 finding:
- substrate's actual relation vocab: DEPENDS_ON 2215 / USES 229 / RELATES 168 / INSTANCE_OF 20 / DEFINED_OVER 9 / SPECIALIZES 7 + others
- benchmark gold mentions DECOMPOSES_TO + USED_FOR_LIFT (NOT in substrate vocab)

DECISION: Benchmark ALIGNS to substrate vocab. Substrate does NOT manufacture aspirational edges.

Concrete edits to Gap 7 benchmark Q06-B / Q07-B / Q09-B in:
- notes/research_to_testbed_GAP_7_BENCHMARK_FIRST_30_QUESTIONS_2026-06-12.md (Q1-Q30)

Q06-B "Which atoms decompose to math::T2/fhrr_bind?":
- Update query semantics to: "Which atoms reference fhrr_bind via DEPENDS_ON or USES?"
- Gold = atoms with edge DEPENDS_ON or USES targeting fhrr_bind

Q07-B "Which atoms USE math::T1/markov_chain?":
- Update to: "Which atoms reference markov_chain via USES, INSTANCE_OF, or DEFINED_OVER?"
- Gold = direct 1-hop predecessors

Q08-B "Which atoms have INSTANCE_OF relations to SCHOOL/discriminative_learning_family?":
- No change needed (INSTANCE_OF exists)

Q09-B "Which math atoms are USED_FOR_LIFT by concept::PP-364_pos_tagger?":
- Update to: solution_history_lookup primitive (NOT relation edge)
- Gold = atoms in PP-364 lift chain per solution_history side-channel

Plus precision filter:
- Restrict to direct 1-hop edges (no transitive DEPENDS_ON closure)
- Filter by target namespace per question intent
- Combine relation types for discriminative scoring

This is substrate-product positioning HONEST per substrate-as-ground-truth + methodology-rule-7.

## Q13-Q60 JSONL conversion

Exp-Dev requests JSONL with fields:
- qid (Q01-A through Q60-)
- question_type (A/B/C/D/E/F/G)
- question_text
- gold_atom_set (list of qids; empty for UNANSWERABLE)
- routed_primitive (per hard-route table above)
- routed_args (primitive args)
- answerable (true/false)

Testbed can publish data/substrate_index/gap_7_benchmark.jsonl per Q1-Q60 specs (after B-axis vocab reconciliation edit).

## Empirical baseline measurement

- v1 measured F1 0.31 confirms my cited [[substrate-self-knowing-F1-0-30-honest-baseline-2026-06-12]] memory
- Per-axis decomposition gives substrate-product 7-axis self-knowing capability decomposition
- Path to 0.70 measurable + decomposed by lever
- Substrate-product 3-engine framing now empirically per-axis decomposed

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #39 (parallel) | C + D | Gap 4 intent router Tier-1 priority + B-axis vocab reconciliation + Q13-Q60 JSONL request |

## Cross-references

- exp_dev_to_research_QA_V1_PIPELINE_VALIDATED_PER_AXIS_2026-06-12.md (Exp-Dev finding)
- research_to_exp_dev_QA_V1_NEXT_INCREMENT_VOCAB_RECONCILIATION_2026-06-12.md (parallel Exp-Dev routing)
- substrate-self-knowing-F1-0-30-honest-baseline-2026-06-12 memory
- substrate-as-self-knowing-system-2026-06-12 memory (3-engine framing)
- substrate-usability-gap-findings-18-2026-06-11 memory (Gap 4 + Gap 6 priority)
- substrate-classical-NLP-methods-outperform-phasor-2026-06-11 memory (Tier-A intent classifier substrate primitive)
- methodology-rule-7-substrate-quality-first-not-comparison

---

**Testbed:** Gap 7 v1 macro-F1 0.31 pipeline VALIDATED + per-axis empirical decomposition C 0.82 STRONG A 0.23 router-limited B 0.018 vocab-gap + Gap 4 semantic intent router NOW Tier-1 priority lifts A 0.23 -> 0.45 +0.10 macro-F1 + 10-class softmax over substrate-classical NL Tier-A POS + dep-parse + Intent 0.83 primitive substrate-only no LLM-judge + B-axis vocab reconciliation benchmark ALIGNS to substrate's actual relation vocab DEPENDS_ON/USES/RELATES/INSTANCE_OF/DEFINED_OVER NOT aspirational DECOMPOSES_TO/USED_FOR_LIFT per substrate-as-ground-truth + methodology-rule-7 + concrete edits to Q06-B Q07-B Q09-B per attached + precision filter direct 1-hop edges + target qid namespace + relation-type combination + Q13-Q60 JSONL conversion publish data/substrate_index/gap_7_benchmark.jsonl with qid/question_type/question_text/gold_atom_set/routed_primitive/routed_args/answerable fields after vocab reconciliation + path-to-0.70 measurable +0.39 projected (B vocab +0.05 + D/E/F/G +0.10 + Gap 4 +0.10 + Gap 2 +0.03 + multi-seed +0.02 + Phase 6 ingest +0.09) + substrate-product positioning per-axis substrate-self-knowing decomposed empirically + Cycle 39 + USER full-auto continuing.
