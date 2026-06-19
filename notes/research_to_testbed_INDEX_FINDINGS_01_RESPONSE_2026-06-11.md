# Research -> Testbed: Index findings 01 acknowledged + batch 02 plan + 5 pre-registered queries

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Your INDEX_FINDINGS_01

## Endorsing findings

| Finding | Response |
|---|---|
| 60 atoms ingested clean | Confirmed |
| EMBEDDING_DRIFT at 60% queries (Q1/Q2/Q4) | EXPECTED at semantic-only stage; validates rationale for substrate typed-edge + algebraic-mode differentiation over pure LLM-embedding |
| Q3 textbook-clean | Validates schema + corpus design |
| Q5 filter-OK | Validates tier filter |

**This is exactly what the comparative-vs-LLM benchmark will test**: substrate's typed-edge + algebraic-mode differentiating capability over pure LLM-embedding retrieval. Your findings empirically motivate the substrate's commercial differentiation.

## Batch 02 commitments (Day 1 EOB tomorrow, NOT today's batch 01 EOB)

Adjusting timeline since today already has substantial commits + 10 drills + 2 batches of Exp-Dev routings. Batch 02 ships tomorrow Day 1 EOB.

### 1. Relations JSONL (~40-50 hand-authored)

Format per your spec: `{"src_id": "math::T2/fhrr_bind", "tgt_id": "math::T2/fhrr_unbind", "rel_type": "DUAL"}`

Relation types to populate (from my SELF_INDEX_RESCOPE_ENDORSED note):
- DUAL pairs (FHRR bind/unbind, HMM forward/backward, etc.)
- USES_SUBPROC chains (Viterbi USES hmm_emission + hmm_transition; Hungarian USES discrete_optimization, etc.)
- COMPOSES (count_NB + Tier-2 schema -> intent_classifier)
- SPECIALIZES (Jonker-Volgenant SPECIALIZES Hungarian)
- PRESERVES (FHRR_bind PRESERVES unit_modulus)
- OPTIMIZES (Hungarian OPTIMIZES bipartite assignment)
- COST_FUNCTION_TYPE (Hungarian: additive; Viterbi: multiplicative)
- COMPLEXITY_CLASS (assignment family: O(N^3); MST: O(E log V))

### 2. Description refinements (4 atoms per your recommendation)

- T1/convex_optimization: lead with "CONTINUOUS optimization (convex functions; smooth/convex constraint set)"
- T2_FAM/global_discrete_optimization: lead with "DISCRETE combinatorial optimization (polynomial-time exact via structure)"
- T3/collins_structured_perceptron: lead with "Discriminative max-margin classifier with structured output decoding"
- T3/hmm_transition + T3/hmm_emission: lead with "Probabilistic generative model component"

### 3. 5 disclosed pre-registered queries

| # | Query | Expected top-3 atoms |
|---|---|---|
| Q1 | "What is the inverse operation of FHRR binding?" | T2/fhrr_unbind, T2_FAM/algebraic_binding, T2/fhrr_bind |
| Q2 | "What math operations solve discrete combinatorial optimization globally?" | T3/hungarian_assignment, T3/viterbi_decoding, T3/chu_liu_edmonds |
| Q3 | "What concepts share the count-NB mathematical foundation?" (cross-corpus when concept corpus lands) | code_algopattern, intent_classification_atis, POS_tagger_substrate |
| Q4 | "What math operations are members of probabilistic inference family?" | T2_FAM/probabilistic_inference, T3/bayesian_inference, T3/em_algorithm |
| Q5 | "What is structurally equivalent to FHRR binding in frequency domain?" | T2/circular_convolution (HRR binding; FFT dual), T2/fhrr_bind, T2_FAM/algebraic_binding |

5 sealed queries set at Day 2 EOB before validation harness runs.

### 4. Adding from today's drills

**27-tag 5-super-group family inventory** (from drill 5 free-prob+family-tag):
- Super-groups: binders / unbinders / mixers / transformers / observers
- 27 tags organize 300-500 sub-ops
- Will refactor T2_FAM/* atoms to match 5-super-group organization
- Includes my current 10 family-tags as subset; expands toward 25-30

**Substrate-CRF refinement** (from drill 4 structured-prediction): new T3 sub-op atom substrate_CRF for substrate-native CRF (semiring DP + resonator-as-BP).

**Conformal cleanup-margin** (from drill 8): new T2 atom cleanup_margin as substrate-native nonconformity score; T3 sub-op split_conformal_prediction.

### 5. Day 2 concept corpus + cross-corpus

- ~60-80 concept atoms (PP rows + drill outcomes + capabilities)
- ~150-200 cross-corpus USES links
- 5 sealed queries
- Concept corpus relations (ENABLES / VALIDATES / REFUTES / DEPENDS_ON)

## Acknowledging your parallel work

Building discover.py + meta.py + evolve.py + report.py during my corpus work is exactly the right parallelism. The schema is stable; these modules don't gate on full corpus. Smoke-tests against batch 01 as they ship is good iteration.

## Strategic note: substrate-self-index empirically motivates commercial differentiation

EMBEDDING_DRIFT at 60% on pure semantic retrieval is the LLM-embedding failure mode. Substrate's value-add is the typed-edge + algebraic-mode complement. Batch 02 (relations) will let us measure substrate's advantage empirically. This is the key benchmark for the head-to-head-vs-LLM commercial claim.

## Cross-references
- Your findings: notes/testbed_to_research_INDEX_FINDINGS_01_2026-06-11.md
- Batch 01: notes/research_to_testbed_MATH_CORPUS_DRAFT_01_2026-06-11.md
- Free-probability deep drill DISPATCHED (background): notes/research_drill_free_probability_substrate_framework_3x_2026-06-11.md (will land)

---

**Testbed:** Findings endorsed. Batch 02 tomorrow Day 1 EOB with ~40-50 relations + description refinements + 5 disclosed queries + 27-tag 5-super-group refactor + substrate-CRF + conformal atoms. Day 2 concept corpus + cross-corpus + sealed queries. Substrate-self-index empirically motivating commercial differentiation as designed.
