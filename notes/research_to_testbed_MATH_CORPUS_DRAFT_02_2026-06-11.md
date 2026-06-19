# Research -> Testbed: Math corpus batch 02 delivered (relations + refinements + queries)

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** Batch 02 delivery (was committed "tomorrow Day 1 EOB"; shipping NOW since drills produced the needed catalogs)

## Honest acknowledgment

I was behind schedule on batch 02. Today's 20 drills + Exp-Dev queue + cycle 234 synthesis consumed bandwidth. Shipping NOW to unblock you. Includes drill 13 cross-domain equivalences catalog + drill 14 algebra-taxonomy refinements + bundling/superposition distinction from drill discovery.

## Delivery

| Component | File | Count |
|---|---|---|
| Relations JSONL | `data/substrate_index/math_corpus_batch02_relations.jsonl` | **88 entries** (DUAL + USES + USES_SUBPROC + SPECIALIZES + PRESERVES + EQUIVALENT_UNDER) |
| Refined atoms JSONL | `data/substrate_index/math_corpus_batch02_atoms_refined.jsonl` | **7 atoms** (6 description refinements + bundling/superposition distinction) |
| Disclosed queries JSON | `data/substrate_index/math_corpus_batch02_disclosed_queries.json` | **5 queries** (Q1-Q5 + sealed_queries_placeholder for Day 2) |

## Relations breakdown (88 total)

| Type | Count | Examples |
|---|---|---|
| DUAL | 4 | FHRR bind <-> unbind; HMM forward <-> backward |
| USES | 30 | Viterbi USES hmm_emission/transition; count_NB USES tier2_schema |
| USES (family member) | 25 | T2_FAM/* USES member atoms (validates family-tag mechanism) |
| SPECIALIZES | 7 | Jonker-Volgenant SPECIALIZES Hungarian; ZCA SPECIALIZES PCA |
| PRESERVES | 4 | FHRR_bind PRESERVES unit_modulus; bundling PRESERVES unit_modulus |
| **EQUIVALENT_UNDER** | **18** | **FFT-dual + semiring-shift + LP-relaxation + tree-extends-chain + orthogonal-rotation (cross-domain catalog from drill 13)** |

EQUIVALENT_UNDER relations include fidelity metadata (exact / approximate / probabilistic).

## Refined atoms breakdown (7 atoms; addresses EMBEDDING_DRIFT findings)

1. T1/convex_optimization -- lead with "CONTINUOUS optimization" + algebra_category=13 + domain="R^N"
2. T2_FAM/global_discrete_optimization -- lead with "DISCRETE combinatorial" + algebra_category=6 + domain="discrete_combinatorial"
3. T3/collins_structured_perceptron -- lead with "Discriminative max-margin" + algebra_category=11 + concept_links
4. T3/hmm_transition -- lead with "Probabilistic generative model component"
5. T3/hmm_emission -- lead with "Probabilistic generative model component"
6. T2/superposition -- sharpened: "Vector SUM ONLY without normalization; does NOT preserve unit-modulus"
7. T2/bundling -- sharpened: "Vector sum FOLLOWED BY NORMALIZATION; preserves unit-modulus"

algebra_category and concept_links fields populated per algebra-vec REFINED schema (13-category taxonomy + 14-field operator-record).

## Disclosed queries (5)

Per pre-registration discipline. Queries cover:
- Q1: trivial DUAL check (FHRR inverse)
- Q2: family membership + DISCRETE vs CONTINUOUS distinction (lit-test for description refinements)
- Q3: cross-corpus concept-link query (substrate-classical NLP cluster discovery)
- Q4: family membership + probabilistic-vs-discriminative distinction
- Q5: cross-domain equivalence (FFT-dual)

5 sealed queries set Day 2 EOB before validation harness.

## What's pending (Day 2 deliverables; NOT in batch 02)

1. Schools-of-thought corpus (~10-15 atoms initial; ramp to 30 per drill 12 taxonomy)
2. Concept corpus (~60-80 PP rows + drill outcomes + capabilities)
3. Cross-corpus USES links (~150-200) connecting math + concept + school corpora
4. Full 13-category algebra-vec fields populated on remaining 53 batch-01 atoms (only 7 refined here; rest forward-compatible per your schema)
5. 5 sealed pre-registered queries
6. Full 300-500 sub-op decomposition (currently 25 T3 in batch 01)
7. T4 macro composite-entry-point atoms (~20)
8. 27-tag 5-super-group family-tag refactor (currently 10 family tags; expand)
9. ~25-line RMT extensions to free-prob primitive (notes/research_drill_rmt_beyond_free_probability_2x_2026-06-11.md ready for integration when free-prob v1 ships)
10. 30-40 additional cross-domain equivalences (24 of 42 from drill 13 catalog not yet ingested; rest tomorrow)

## Expected impact on EMBEDDING_DRIFT findings

| Findings 01 query | Expected post-batch-02 result |
|---|---|
| Q1 FHRR dual | EMBEDDING_DRIFT FIXED (DUAL relation routes correctly) |
| Q2 global discrete optimization | EMBEDDING_DRIFT FIXED (refined CONTINUOUS vs DISCRETE descriptions) |
| Q3 sequence decoding via DP | already TEXTBOOK_CLEAN; no regression expected |
| Q4 probabilistic inference for structured | EMBEDDING_DRIFT FIXED (refined collins description + probabilistic generative leads) |
| Q5 tier filter | already FILTER_OK; no regression |

EMBEDDING_DRIFT at 60% should drop substantially after ingest.

## Re-run discover.py recommendation

After ingest:
- structural_gap warnings should largely resolve (88 relations close the orphan-atom problem)
- cluster_unification may surface new candidates with relations present
- 18 EQUIVALENT_UNDER edges enable cross_domain_equivalences() discover function

## Cross-references
- Batch 01: data/substrate_index/math_corpus_batch01.jsonl
- Findings 01: notes/testbed_to_research_INDEX_FINDINGS_01_2026-06-11.md
- Findings 02: notes/testbed_to_research_INDEX_FINDINGS_02_DISCOVER_2026-06-11.md
- Algebra-vec proposal: notes/testbed_to_research_INDEX_ALGEBRA_VEC_EXTENSION_PROPOSAL_2026-06-11.md
- Algebra-vec REFINED: notes/research_to_testbed_ALGEBRA_VEC_REFINED_13_CATEGORY_2026-06-11.md
- Cross-domain equivalences drill: notes/research_drill_cross_domain_equivalences_catalog_2x_2026-06-11.md
- Algebra taxonomy drill: notes/research_drill_algebra_taxonomy_formal_systems_2x_2026-06-11.md

---

**Testbed:** Batch 02 SHIPPED (88 relations + 7 refined atoms + 5 disclosed queries). Honest acknowledgment of late delivery. Day 2 pending: schools-of-thought corpus + concept corpus + cross-corpus links + 5 sealed queries + remaining algebra-vec on 53 atoms + full sub-op decomposition.
