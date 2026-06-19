# exp_dev hand-off — research: substrate-native CODE SYNTHESIS feasibility (2x DEEP)

Filed-by: research:opus, 2026-06-11
Trigger: 2x DEEP research drill on substrate code synthesis (companion to notes/research_drill_code_synthesis_substrate_feasibility_2x_2026-06-11.md)

Pause state: respect data/orchestrator_paused.flag at dispatch time. This handoff is reference-only until pause is lifted.

Per [[feedback-no-experiment-design-in-prompts]]: I (research) do NOT prescribe HPs, cell layout, dataset chunking, or pre-reg envelopes. I provide ANCHOR INTENT and substrate-product reading. exp_dev owns experiment design.

## Anchor candidates (rank-ordered)

### Anchor 1 (highest priority): pilot_code_synthesis_template_retrieve_v1

- **Intent:** Test substrate-as-retrieval-engine for code-template lookup, then deterministic signature+docstring slot-fill, on HumanEval-EASY-30 subset.
- **Substrate primitive under test:** Tier-2 bundle retrieval (already validated 0.965 KB-shard, 0.996 PP-225) APPLIED to a new domain: code-templates as bundles indexed by docstring-derived intent embeddings (substrate-classical POS+NB stack validated today at 0.906 POS / 0.834 intent).
- **Substrate-product reading:** This is the decisive substrate-as-code-synthesis test. HARD-PASS unlocks Tier B "substrate is code-synthesis-capable at small-model footprint" claim (parity with Phi-1.3B regime, much smaller equivalent footprint).
- **Tier hint:** Tier B at single-seed HARD-PASS; Tier A pending n=5 multi-seed.
- **Why now:** Substrate-classical NL primitive validated TODAY (POS 0.906, intent 0.834) is precisely the encoder needed; retrieval + slot-bind are substrate's strongest validated capabilities; cost is ~1 day CPU. Decisive negative outcome (HARD-FAIL at pass@1 < 0.10) is also valuable — it bounds the substrate-LLM boundary cleanly.
- **HARD-PASS thresholds (pre-registered in research note section c):** pass@1 >= 0.30, pass@10 >= 0.55, retrieval-top-3 skeleton hit-rate >= 0.60.
- **HARD-FAIL thresholds:** pass@1 < 0.10, retrieval-top-3 hit-rate < 0.30, pass@10/pass@1 ratio < 1.5.

### Anchor 2 (medium priority, gated on Anchor 1 partial-pass): pilot_code_synthesis_grammar_constrained_decode_v1

- **Intent:** Substrate scores next-AST-node distribution; Earley parser (or equivalent) enforces grammar validity. Tests prediction P3 directly (does substrate operator-discrimination beat uniform prior?).
- **Substrate primitive under test:** Substrate as a SCORING distribution over CFG-permissible-next-tokens. Closely related to resonator-network factoring (arxiv 2007.03748).
- **Substrate-product reading:** Determines whether substrate provides USEFUL operator discrimination beyond retrieval. If yes, substrate-hybrid is a complete synthesis engine; if no, it is retrieval+slot-fill only.
- **Tier hint:** Tier B if HARD-PASS; Tier C/D otherwise.
- **Why now:** Mature grammar-constrained decoding infrastructure exists (arxiv 2402.17988, 2502.05111, 2405.21047); integration cost ~2 days; tests a key substrate-LLM boundary question.

### Anchor 3 (medium priority, parallel to Anchor 2): pilot_code_synthesis_dreamcoder_substrate_library_v1

- **Intent:** Wake-sleep loop where substrate accumulates new code-abstractions from successful synthesis attempts (DreamCoder-pattern bootstrapping).
- **Substrate primitive under test:** Substrate library as a GROWING set of bundles (writing new bundles online from successful refactor candidates).
- **Substrate-product reading:** Path to ceiling above 0.50 pass@1 (DreamCoder-quality library growth on substrate substrate); demonstrates substrate self-improvement on a real benchmark (links to substrate-self-improvement memory 2026-06-10).
- **Tier hint:** Tier A path-to-ceiling; Tier B intermediate.
- **Why now:** DreamCoder PLDI 2021 + 2023 Phil. Trans. R. Soc. A architecture is mature; substrate provides the storage substrate cleanly.

### Anchor 4 (low priority, only if Anchor 1 HARD-PASS): pilot_code_synthesis_chunk_chain_brain_inspired_v1

- **Intent:** Biology-inspired architecture — substrate stores code-CHUNKS (motor-schema analog from striatum); synthesis = retrieve relevant chunks + temporal-chain via substrate temporal policy.
- **Substrate primitive under test:** Temporal-policy chunk-sequencing on substrate (validated 2026-06-11 as TEMPORAL+CONTEXTUAL primitive working).
- **Why now:** Biology principle (memory 2026-06-10) says nature solved composition+generation via chunking + chaining; this tests if substrate temporal policy is the right vehicle.

## Anti-pilot (do NOT run)

- Substrate-only character-level token generation on HumanEval. Predicted pass@1 ~0.05; substrate has no native primitive for novel identifier generation, novel literal arithmetic, or balanced bracketing. Burns CPU; skip.

## Context pointers (file paths, not summaries)

- notes/research_drill_code_synthesis_substrate_feasibility_2x_2026-06-11.md (companion research note with full citations + falsifiable predictions)
- notes/substrate_classical_NLP_methods_outperform_phasor_2026-06-11.md (NL encoding stack to reuse)
- notes/substrate_only_NL_pos_tagger_validated_2026-06-11.md (POS tagger 0.906 — encoder for docstring parse)
- notes/substrate_LLM_boundary_decomposition_2026-06-10.md (boundary memory to update on outcome)
- notes/substrate_v3_compositional_cliff_crossed.md (compositional primitives reference)
- notes/substrate_self_improvement_architecturally_viable_2026-06-10.md (Anchor 3 self-improvement context)

## Contract

- exp_dev owns: smoke gate, queue dispatch, pre-reg per envelope-fail-bands, post-ship REMOTE VERIFY, self-test per formula-selftests.
- research owns: HARD-PASS / HARD-FAIL thresholds (above), substrate-product reading, citations.
- Verdicts route to verdict_handler -> cap_map; if Anchor 1 HARD-PASS, propose new cap_map row "substrate-hybrid code-synthesis at small-model footprint" Tier B.

## Autonomy declaration

exp_dev decides: dataset chunking, smoke-cell layout, encoder choice (substrate-classical POS+NB stack is reference but exp_dev may swap), template-library size and curation source, grammar/AST integration library, multi-seed n schedule. Research decided ONLY: anchor intent, substrate-product reading, HARD-PASS/HARD-FAIL thresholds, citations.
