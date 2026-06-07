# Research -> Exp-Dev: substrate-native question decomposition (Pattern B + K-hop unification)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** Connection between retrieval decomp pre-tests and Pattern B exploration program.

User flagged a real unification: the retrieval drill recommended LLM decomposition based on
Pattern A assumptions. With Pattern B, decomposition is substrate-native via VSA unbinding.
The two test programs I filed this morning overlap exactly on this mechanism.

## The unification

Pattern A: substrate stores opaque embeddings; no question structure; LLM must decompose.

Pattern B: substrate stores compositional role-filler bindings; multi-hop questions have
nested compositional structure; K-hop unbinding IS algebraic decomposition. No LLM needed
in the decomposition loop.

The dependency for Pattern B-based decomposition is question parsing (turning natural
language into compositional form). Two parser candidates:

- Light parser: spaCy NER + templates. Already being tested as PRE-TEST A in the retrieval
  decomp pre-tests. HARD-PASS at recall@2hop >= 0.65 with substrate retrieval.
- SRL parser: standard semantic role labeling. Pattern B's Phase 0 gate. HARD-PASS at
  argument F1 >= 0.85, subject/object swap rate <= 4%.

## What the unified recipe looks like

If PRE-TEST A (NER decomp) passes:
- v1 demo recipe = bge-small encoder + NER parser + substrate Pattern B unbinding for
  decomposition + K-hop for composition + Llama-1B for natural-language generation
- LLM only generates the final answer; substrate does the decomposition and composition
- No LLM-decomp loop engineering needed (the "LLM-decomp loop" anchor I queued can be
  dropped if NER works)

If PRE-TEST A borders (0.50-0.65) but SRL pre-test passes:
- v1 demo recipe = bge-small + SRL parser (more accurate than NER) + substrate Pattern B
  + K-hop + Llama-1B for generation
- SRL gives higher parsing accuracy; same substrate-native decomposition story

If PRE-TEST A passes AND SRL pre-test passes:
- Use NER for v1 (simpler, faster); reserve SRL for v1.1 quality upgrade
- Pattern B's broader compositional capabilities (schema-aware queries, cross-domain
  analogy) still benefit from SRL accuracy

If both fail:
- Fall back to LLM-decomp loop (the original retrieval drill recommendation)
- Pattern B becomes v2 research target
- Demo loses substrate-native decomposition story but retains audit + persistence

## Implication for the exploration program

Pattern B Phase 2A (end-to-end benchmark with substrate Pattern B + Llama-1B vs bare
Llama-1B) IS the full substrate-native decomposition recipe. It subsumes the LLM-decomp
loop final test from the retrieval pre-tests routing. Don't run both; run Phase 2A as
the end-to-end test if Pattern B Phase 0 + 1 cells pass.

Pattern B Phase 1E (multi-step causal chain extension) is a direct test of the K-hop
unbinding capability at multi-hop depth. A HARD-PASS there is strong evidence that the
algebraic decomposition will work on HotpotQA.

## North-star framing for the customer

The substrate-native decomposition story is genuinely a north-star differentiator. Bare
1B LLMs decompose questions poorly (mis-identify bridge entities, sequence sub-questions
wrong, hallucinate intermediate answers). Substrate doing algebraic decomposition via
VSA unbinding is deterministic and auditable: every unbinding step carries a Merkle
proof. The decomposition is provably correct, not statistically usually-right.

For a customer pitch: "Our substrate decomposes multi-hop questions algebraically using
the same vector operations that built the knowledge graph. Every step in the decomposition
is mathematically traceable. A 1B-parameter language model attempting the same task makes
decomposition mistakes that produce confident wrong answers; our system either succeeds
provably or returns 'I don't know' explicitly."

This is the kind of capability story that doesn't depend on beating LLMs at raw recall
numbers; it differentiates on REASONING CHAIN INTEGRITY.

## Test sequencing recommendation

To leverage the overlap and avoid duplicate work:

1. Run PRE-TEST A (NER decomp) first. If HARD-PASS, we have the simplest substrate-native
   path; skip Pattern B Phase 0 SRL test for v1 purposes (still run it for v1.1 quality
   upgrade evaluation).

2. If PRE-TEST A is BORDER or HARD-FAIL, run Pattern B Phase 0 (SRL pre-test). SRL is
   higher-accuracy than NER and may close the gap.

3. If Pattern B Phase 0 HARD-PASS, run Pattern B Phase 1 cells (algebra battery) in
   parallel. Pattern B Phase 1E (multi-step causal chain) is the most direct test of
   the K-hop unbinding mechanism.

4. Pattern B Phase 2A (end-to-end benchmark) is the full substrate-native demo recipe.
   This subsumes the LLM-decomp loop final test. Run after Phase 1 confirms algebra
   works.

5. PRE-TEST B (gte-base coverage) is independent of the decomposition story; run in
   parallel as encoder upgrade evaluation.

## Cross-references

- Retrieval encoder 3x drill: notes/research_drill_retrieval_encoder_selection_3x_2026-06-07.md
- Retrieval decomp pre-tests routing: notes/research_to_exp_dev_retrieval_decomp_pretests_authorize_2026-06-07.md
- Pattern B 3x drill: notes/research_drill_pattern_b_compositional_storage_3x_2026-06-07.md
- Pattern B exploration program: notes/research_to_exp_dev_pattern_b_full_exploration_program_2026-06-07.md
- Pattern B SRL pre-test routing: notes/research_to_exp_dev_pattern_b_srl_pretest_authorize_2026-06-07.md

---

**END.**

**Exp-Dev:** apply the unified sequencing. PRE-TEST A is now the first decomposition test;
if it passes, the v1 recipe is substrate-native decomposition (no LLM-decomp loop needed).
File synthesis when PRE-TEST A and Pattern B Phase 0 both have results so I can update
the v1 demo recipe definition.
