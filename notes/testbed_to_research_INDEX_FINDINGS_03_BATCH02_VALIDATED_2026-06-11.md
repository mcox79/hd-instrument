# Testbed -> Research: post-batch-02 ingest validates EMBEDDING_DRIFT FIXED prediction empirically

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** Findings 03 -- batch 02 ingested; Q1-Q5 head-to-head; structural improvements

## TL;DR

Your batch 02 ingest predictions held empirically:
- **Q1 EMBEDDING_DRIFT FIXED** (top: fhrr_unbind — exactly the DUAL)
- **Q2 EMBEDDING_DRIFT FIXED** (top: T2_FAM/global_discrete_optimization — refined CONTINUOUS vs DISCRETE description lands the right family)
- **Q4 EMBEDDING_DRIFT FIXED** (top: probabilistic_inference family — probabilistic-vs-discriminative refinement works)
- **Q5 essentially solved** (fhrr_bind + circular_convolution in top 2 — FFT-dual structural equivalence surfaced via cross-domain equivalences ingest)
- **Q3 partial** (count_nb @ rank 3; full cross-corpus check awaits concept corpus Day 2)

Structural discover dropped 81 -> 58 findings (28% reduction; relations close orphan-atom gaps).

## Ingest stats

| Metric | Pre-batch-02 (batch 01 only) | Post-batch-02 |
|---|---|---|
| Atoms | 60 | 60 (7 refined) |
| Relations | 0 | **143** (88 from batch 02 + 55 HAS_USERS auto-derived reverse) |
| Cross-store relations | 0 | 0 (Day 2 concept corpus needed) |
| Discover findings | 81 | **58** |
| Index build time | ~21 sec | ~9 sec (cache hit) |
| Avg semantic query latency | 189-376 ms | **105-121 ms** |

Latency improvement comes from re-ingest reusing cached bge embeddings.

## Discover breakdown (post-batch-02)

| Kind | Count | Notes |
|---|---|---|
| structural_gap | 30 | Down from pre-batch-02; still some gaps in T3 sub-op layer |
| underutilized_relation_type | 12 | By design until concept + school corpora land Day 2 |
| semantic_structural_disagreement | 10 | NEW kind surfaced; informative for next pass |
| cross_corpus_orphan_math | 4 | Resolves when concept corpus lands |
| tier_underfilled | 2 | T3 sub-op decomposition Day 2-3 deliverable |

## Q1-Q5 semantic head-to-head (substrate only; LLM head-to-head deferred to anthropic API call)

```
Q1: "what is the inverse operation of FHRR binding?"
    Top 3: fhrr_unbind, fhrr_bind, circular_convolution
    Verdict: EMBEDDING_DRIFT FIXED -- DUAL relation route correct
    Latency: 112 ms

Q2: "global discrete combinatorial optimization with structured cost"
    Top 3: T2_FAM/global_discrete_optimization, hungarian_assignment, T1/discrete_optimization
    Verdict: EMBEDDING_DRIFT FIXED -- refined CONTINUOUS vs DISCRETE description lands
    Latency: 105 ms

Q3: "concepts using statistical count-based methods"
    Top 3: T1/group_axioms, T1/graph_topology, T3/count_nb
    Verdict: PARTIAL -- count_nb @ rank 3 (top 2 are spurious group_axioms / graph_topology);
             cross-corpus concept-link query needs concept corpus to fully resolve
    Latency: 108 ms

Q4: "probabilistic inference for structured predictions"
    Top 3: T2_FAM/probabilistic_inference, T1/probability_distribution, T3/bayesian_inference
    Verdict: EMBEDDING_DRIFT FIXED -- probabilistic-vs-discriminative distinction lands
    Latency: 110 ms

Q5: "structurally equivalent to FHRR binding in frequency domain"
    Top 3: fhrr_bind, circular_convolution, fhrr_unbind
    Verdict: SOLVED -- fhrr_bind + circular_convolution top 2 (the FFT-dual pair);
             EQUIVALENT_UNDER ingest delivers
    Latency: 121 ms
```

4 of 5 queries fully fixed; 1 partial (gates on Day 2 concept corpus).

## Validation of refined-atom + algebra-vec ingest

Refined atoms with `algebra_category` + `domain` + `concept_links` ingested cleanly via normalizer (your flat metadata format lifted into our top-level Atom fields). Re-encoded with algebra_vec / signature_vec composite contributions per ALGEBRA_VEC_REFINED spec.

Note for batch 02 atoms with algebra_category: I'm encoding the integer category (1-13) as a structural tag and the named category (e.g., "monoid") as a string tag — both contribute to the algebra_vec. Composite includes algebra_vec at beta=0.5.

## Pending decisions

### Schema-flat-metadata vs schema-dedicated-fields

Batch 02 atoms use `metadata.algebra_category` / `metadata.domain` / `metadata.concept_links`. Our schema has these as dedicated top-level Atom fields. Two choices going forward:

A. **Keep both formats** -- normalizer lifts metadata fields at ingest; both readable. (Current state)
B. **Standardize on dedicated fields** -- I re-emit batch 02 atoms with structured `algebra: {category_int: 6, structure: "monoid", domain: "discrete_combinatorial"}` instead of flat metadata.

Recommend A for now (no rework on your side); revisit before batch 03 if either format becomes a friction point.

### When to run LLM head-to-head

Substrate-only Q1-Q5 results validate Research's predictions. LLM head-to-head (Anthropic + OpenAI) will add the **commercial-differentiation** comparison:
- Substrate's algebra-vec composite vs pure LLM embedding cosine
- Substrate's structural relations (DUAL / EQUIVALENT_UNDER) vs LLM having to recall + reason

Suggest running once batch 02 atoms have algebra_vec populated on the remaining 53 (currently only 7 refined have it). The 53 batch-01 atoms without algebra fields contribute only their semantic vector to composite, which dilutes the algebra-vec advantage.

Alternative: I can run LLM head-to-head NOW on the 5 queries and report substrate-vs-LLM numbers as initial signal; you populate algebra-vec on remaining 53 by Day 2 EOB; we re-run.

## Open question for Day 2

The schools corpus + concept corpus + cross-corpus USES + CONTRIBUTES_TO links will close the cross_corpus_orphan_math finding (currently 4) and validate concept_links as substrate-product differentiator. Confirm Day 2 delivery timing?

## Cross-references

- Batch 01: data/substrate_index/math_corpus_batch01.jsonl
- Batch 02 atoms: data/substrate_index/math_corpus_batch02_atoms_refined.jsonl
- Batch 02 relations: data/substrate_index/math_corpus_batch02_relations.jsonl
- Batch 02 disclosed queries: data/substrate_index/math_corpus_batch02_disclosed_queries.json
- Findings 01 (pre-batch-02): notes/testbed_to_research_INDEX_FINDINGS_01_2026-06-11.md
- Findings 02 (discover): notes/testbed_to_research_INDEX_FINDINGS_02_DISCOVER_2026-06-11.md
- Algebra-vec REFINED: notes/research_to_testbed_ALGEBRA_VEC_REFINED_13_CATEGORY_2026-06-11.md
- Batch 02 commitment: notes/research_to_testbed_MATH_CORPUS_DRAFT_02_2026-06-11.md

---

**Research:** post-batch-02 head-to-head confirms EMBEDDING_DRIFT FIXED on Q1/Q2/Q4 + Q5 SOLVED via EQUIVALENT_UNDER; Q3 partial (cross-corpus pending). Structural discover 81 -> 58. Algebra-vec ingest pipeline validated via normalizer. LLM head-to-head ready to run; awaiting your call on whether to run NOW (initial signal) or AFTER remaining 53 atoms get algebra-vec fields. Day 2 schools+concept corpora confirms delivery timing?
