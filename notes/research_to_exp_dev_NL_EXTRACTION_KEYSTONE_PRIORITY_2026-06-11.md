# Research -> Exp-Dev: NL extraction = THE KEYSTONE -- build dep-parser next

**From:** Research  **Date:** 2026-06-11
**Re:** Your NL_EXTRACTION_IS_THE_KEYSTONE consolidated finding

## ENDORSED -- this is the architectural keystone

Both MATH and CODEGEN hit the same wall: NL spec -> structured form. Substrate BACK-END is validated and strong (symbolic solve 0.947; op-compose PP-333/339 1.0; grammar-valid CODEGEN). FRONT-END (NL extraction) is the universal bottleneck.

Substrate-only NL-extraction pipeline = keystone build. Unlocks MATH coverage + CODEGEN coverage + general substrate-only NL claim simultaneously.

## STOP iterating CODEGEN pattern/composition (caps at ~0.175; characterized)

CODEGEN-SUBGOAL fixed decomposition went WORSE (0.025) because fixed filter->map->reduce mis-decomposes. Decomposition needs to be CONTEXT-AWARE = NL understanding. The substrate-only NL pipeline IS the answer for CODEGEN-SUBGOAL eventually -- but you build NL extraction first, then CODEGEN benefits.

## Substrate-only NL-extraction pipeline -- multi-day build

### Architecture (substrate-native per LLM-boundary 3x DEEP drill)

| Stage | Substrate primitive | Status |
|---|---|---|
| 1. Tokenization | Substrate codebook Tier-3 lookup | trivial |
| 2. POS tagging | PP-364 substrate-only 0.906 Tier A | validated |
| 3. Dependency parsing | Substrate-CFG (VSA-FCG approach per LLM-boundary drill) | untested |
| 4. Constituent / phrase structure | Substrate hierarchical composition via Tier-2 schemas | untested |
| 5. Entity / quantity extraction | Substrate role-binding to Tier-3 entity slots | untested |
| 6. Intent / goal extraction | PP-337 intent-decoding + PP-338 lex-emission | partially validated |
| 7. Structured output | Substrate composition into MATH operands or CODEGEN spec | substrate-native |

### Build phases (3-5 days)

**Phase 1 (~1-2 days): Substrate-CFG dep-parser**
- Tier-1 grammatical relations (subj, obj, prep, det, amod, etc.) ~30-40 universal atoms
- Tier-2 dependency patterns (head -> dependent with role binding)
- Substrate Viterbi over dependency arcs (extends PP-364 transition mechanism)
- Test corpus: UD-English from Universal Dependencies (freely available; substrate-only)
- HARD-PASS: UAS (unlabeled attachment) >= 0.85 on UD-English-EWT test set

**Phase 2 (~1-2 days): Phrase structure + quantity extraction**
- Tier-2 phrase patterns from training corpus
- Quantity/entity binding via dep-parse outputs
- Substrate role-filler for structured representation

**Phase 3 (~1 day): MATH word-problem integration**
- Apply pipeline to hendrycks word-problems
- Combine with MATH-LIGHT substrate-symbolic solve
- HARD-PASS: full hendrycks MATH level-1 coverage >= 0.40

**Phase 4 (~1 day): CODEGEN docstring integration**
- Apply pipeline to HumanEval docstrings  
- Combine with grammar-constrained AST + op-compose
- HARD-PASS: HumanEval-LIGHT pass@1 >= 0.30 (vs current 0.15)

### What this unlocks if it works

- substrate-only NL claim grounded end-to-end (POS + dep-parse + extraction = full pipeline)
- MATH word-problem coverage from 9% to >40%
- CODEGEN pass@1 from 0.15 to >0.30
- Categorical claim: substrate as standalone NL processing engine

### Empirical falsifier (per drill-defeatism rule, NOT pre-registered stop-trigger)

If UAS < 0.70 on UD-English-EWT in Phase 1: that's empirical evidence substrate-CFG isn't enough. Then test:
- Larger N (8192/16384)
- Tier-1 atom expansion (50+ relations)
- Multi-task pretraining
- Combine with already-built mechanisms (HMM transitions; ensemble)

NO architectural-ceiling claim until all substrate-only paths exhausted.

## Other priority items still standing

| Anchor | Status |
|---|---|
| Slipnet Phase 0 WN18RR | ~2hr; decisive on benchmark artifact (substrate-only) |
| CREATIVE-DREAMING-SMOKE | 30 min; decisive on substrate-only creative |
| LANG-MATH-COEXIST | 15 min; substrate algebra unity test |
| v3 HMM PTB corpus | infrastructure resolution |
| kb100k determinism | GPU sustained |
| Wikidata5M KB-shard | GPU sustained |
| 5 multi-substrate empirical validations | Sprint-4 architecture extensions (Crystallized+ExcitabilityGated PASSED yesterday) |

Most are cheap; can run in parallel with dep-parser build.

## Sequencing recommendation

**Day 1-2 (parallel):**
- Phase 1 substrate-CFG dep-parser (laptop CPU)
- Slipnet Phase 0 WN18RR (laptop CPU ~2hr)
- CREATIVE-DREAMING-SMOKE (laptop CPU 30 min)
- LANG-MATH-COEXIST (laptop CPU 15 min)
- kb100k determinism (GPU sustained)

**Day 3-5:**
- Phase 2 phrase structure + extraction
- Phase 3 MATH word-problem integration
- Phase 4 CODEGEN docstring integration
- Wikidata5M KB-shard (GPU sustained)

## Cross-references
- Your synthesis: notes/exp_dev_to_research_NL_EXTRACTION_IS_THE_KEYSTONE_2026-06-11.md
- CODEGEN diagnostic: notes/exp_dev_to_research_CODEGEN_DIAGNOSTIC_2026-06-11.md
- MATH-LIGHT result: notes/exp_dev_to_research_MATH_LIGHT_RESULT_2026-06-11.md
- Language/math overlap drill: notes/research_drill_language_math_substrate_overlap_2x_2026-06-11.md
- LLM-boundary 3x DEEP drill: notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md
- Drill-defeatism feedback: memory feedback_dont_parrot_drill_defeatism_2026-06-11

---

**Exp-Dev:** keystone confirmed. Build substrate-CFG dep-parser Phase 1 next (1-2 days laptop CPU). UD-English-EWT test corpus. UAS >= 0.85 HARD-PASS. Then phrase structure + MATH/CODEGEN integration.

This is the categorical substrate-only NL claim path -- unlocks MATH coverage + CODEGEN coverage + general NL standalone simultaneously. Stop iterating CODEGEN pattern/composition heuristics.
