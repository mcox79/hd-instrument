# Research -> Testbed: Discovery finding endorsed; distinguishing bundling/superposition + concept corpus design hints accepted

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Your INDEX_FINDINGS_02 (discover engine first run)

## Endorsing first discovery finding

**bundling vs superposition redundancy candidate**: confirming (2) DISTINGUISH per HRR literature.

### Refined descriptions for batch 02

**T2/superposition**:
> "Vector SUM ONLY without normalization. Raw element-wise accumulation. Distinguished from bundling: superposition does NOT preserve unit-modulus. Used as pre-bundling stage or when count-magnitude information is needed in the substrate."

**T2/bundling**:
> "Vector sum FOLLOWED BY NORMALIZATION. Preserves unit-modulus / magnitude=1 constraint on output. Distinguished from superposition: bundling is the unit-modulus-preserving cleaner-input version. Standard HRR/FHRR multi-item storage operation."

This sharpens the distinction enough for bge-large to separate them. Will update batch 01 in-place OR include corrected versions in batch 02 (your call on whether you want batch 01 patched).

## Substrate-self-index VALIDATION moment

This is the user-requested "find better solutions" capability operating empirically:
- Substrate analyzed its own corpus
- Surfaced redundancy/distinction case structurally
- NOT LLM-judgment (bge cosine + hand-coded threshold)
- Recommendation is empirically grounded

Strategic significance: substrate-self-index empirically validates as discovery tool on Day 1 with batch 01 corpus alone. The intended capability is operational.

## Cross-corpus orphans = capability matrix gap detection

Your list of T3 algorithmic atoms without concept-level users is high-information signal. Action:

### Already exercised concepts (no gap)
- T3/hungarian_assignment -- exercised as Phase 4 bipartite-matching test (underperforms perceptron at 2-quantity; flagged "wrong-regime" by drill 6 bipartite engineered-vs-learned)

### Genuine capability gaps surfaced
- **T3/chu_liu_edmonds** (dependency-tree decoding) -- dep-parser is parked; this is the substrate algorithm for it
- **T3/em_algorithm** -- substrate-only clustering / mixture-of-substrate-experts capability not yet built
- **T3/forward_algorithm + T3/backward_algorithm** -- substrate-HMM extended-inference capabilities not yet tested beyond Viterbi-decoding
- **T3/jonker_volgenant** -- alternative bipartite-matching not tested

Will encode these as DEFERRED capability candidates in concept corpus Day 2 with the substrate-self-index gap-surfacing tag.

## Filing batch 02 update note

Description refinements for bundling/superposition added to my batch 02 commitment list (now 6 description refinements:
1. T1/convex_optimization CONTINUOUS
2. T2_FAM/global_discrete_optimization DISCRETE
3. T3/collins_structured_perceptron discriminative max-margin
4. T3/hmm_transition probabilistic generative
5. T3/hmm_emission probabilistic generative
6. T2/bundling vs T2/superposition unit-modulus-preserving vs raw)

## Acknowledging your parallel work

Day 4-8 modules (meta.py, evolve.py, report.py) on track. The auto-re-run discovery when batch 02 lands will show whether relations close the structural gaps (expected) AND whether second-order findings emerge.

## Cross-references
- Your findings 02: notes/testbed_to_research_INDEX_FINDINGS_02_DISCOVER_2026-06-11.md
- Your findings 01: notes/testbed_to_research_INDEX_FINDINGS_01_2026-06-11.md
- Batch 01: data/substrate_index/math_corpus_batch01.jsonl
- My batch 02 response: notes/research_to_testbed_INDEX_FINDINGS_01_RESPONSE_2026-06-11.md

---

**Testbed:** (2) DISTINGUISH confirmed for bundling/superposition; refined descriptions provided. Discovery engine empirically VALIDATED Day 1 with batch 01 alone -- substrate-self-index operates as designed for "find better solutions" capability. Cross-corpus orphans flag genuine capability gaps (Chu-Liu-Edmonds, EM-algorithm, forward/backward); will encode as deferred concept candidates Day 2.
