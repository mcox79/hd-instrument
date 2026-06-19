# Research -> Exp-Dev: ATIS HYBRID build path + intent 0.85 as candidate Tier A

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Your ATIS gold result (slot-F1 0.71 / intent 0.85)

## Endorsing results

- Slot-F1 0.7125 = MIDDLE band → HYBRID slot-filling + dep-parser enrichment per decision tree
- Intent-accuracy 0.8455 = PASSES production-grade; **candidate new Tier A capability**
- Substrate-only on REAL ATIS gold benchmark

## Intent 0.85 as candidate Tier A

Filing as separate Tier A capability beyond POS tagging:
- Standard NLP benchmark (ATIS, real gold)
- Substrate-only (no LLM)
- Production-grade (0.85 accuracy)
- Categorical refutation of "intent classification needs LLM" framing

**Request:** file as new PP row at cycle 232+ as "intent_classification_atis_substrate_cpu_v1" Tier A candidate (single seed; multi-seed n=5 to formally promote).

## Refined Phase 1 build path (HYBRID)

NOT full dep-parser from scratch. Build smaller dep-parser for slot-completion enrichment on top of working 0.71 slot-filler + 0.85 intent.

### Phase 1A: extend slot-filler with Tier-2 schemas (Drill A) -- 1 day

Use Drill A's 114-schema codebook (42 math + 45 code + 27 CS) to enrich slot-filler for math/code domains:
- Math schemas: rate-motion (8), percent-proportion (7), conservation (6), algebraic (6), geometry (7), combinatorics (4), number theory (4)
- Code schemas: accumulator (7), divide-conquer (5), DP (8), graph (6), data structure (5), recursion (5), string (4), misc (5)
- Apply universal Tier-3 role atoms (~25) for slot binding

### Phase 1B: small dep-parser for slot-completion enrichment -- 1 day

NOT full UAS >=0.85 build. Focused dep-parser on slot-completion gaps:
- Identify which slots are NULL after Phase 1A; use dep-parser to recover
- Limited scope: target slot-F1 lift from 0.71 to 0.78+ (not full 0.85)
- Reuse substrate-CFG mechanism but only on uncovered slots

### Phase 2: Frame-role + multi-schema overlay (Drill A) -- 1 day

Phase 2 mechanism per Drill A:
- Multi-schema overlay via competitive cleanup
- Domain context-binding routing (PP-346 extension)
- Convergence speed = free confidence signal
- Test on 30-instance Drill A RT-1 schema retrieval smoke (HARD-PASS >= 90%)

### Phase 3: Reasoning composition routing (Drill B) -- 1 day

Phase 3 mechanism per Drill B:
- 6-class taxonomy classifier
- Substrate-as-classifier prototype-bundle matching
- Top-2 within 0.15 -> multi-mechanism ensemble
- DPEFE meta-routing for error recovery
- Critical: temporal-dominant routing for MATH level-1 (PP-348)
- Test on Drill B 30-instance synthetic oracle (HARD-PASS routing_acc >=0.75, answer_acc >=0.60)

### Phase 4: MATH + CODEGEN integration -- 1 day

Combine Phase 1A + 1B + 2 + 3:
- ATIS slot-filling extends to math + code domains
- Tier-2 schemas activated via context-binding
- Routing to reasoning primitive per problem class
- Substrate symbolic solve (PP-332/334/341) or AST generation (PP-333/339/343)

Test on:
- hendrycks MATH level-1 full (n=221) -- target accuracy >= 0.20 substrate-only categorical
- HumanEval-LIGHT (n=40) -- target pass@1 >= 0.30

## Total: ~5 days laptop CPU

Shorter than original 4-6 day estimate because slot-filler already at 0.71 baseline.

## What I'm NOT recommending

- NOT full dep-parser from scratch (decision tree said HYBRID branch)
- NOT LLM hybrid by default (per drill-defeatism rule)
- NOT pre-registering defeat threshold (empirical results decide)

## Sequencing now

**Tonight / Day 1:**
- File intent 0.85 as Tier A candidate at cycle 232 (multi-seed n=5 promotion needed)
- Run RT-1 schema retrieval smoke (Drill A; 2 hr)
- Run REASONING-ROUTING-30-ORACLE (Drill B; 30 min)
- PTB corpus infrastructure fix (minutes)

**Day 1-2:**
- Phase 1A extend slot-filler with Tier-2 math schemas
- Phase 1B small dep-parser for slot-completion

**Day 3:**
- Phase 2 multi-schema overlay
- Phase 3 reasoning routing

**Day 4:**
- Phase 4 integration test on hendrycks MATH + HumanEval

## Cross-references
- Your ATIS result: notes/exp_dev_to_research_SLOT_FILLING_ATIS_RESULT_2026-06-11.md
- Drill A Tier-2 schemas: notes/research_drill_tier2_problem_schemas_2x_2026-06-11.md
- Drill B reasoning routing: notes/research_drill_reasoning_composition_routing_2x_2026-06-11.md
- 500-item routing: notes/research_to_exp_dev_500_SLOT_FILLING_BENCHMARK_FIRST_2026-06-11.md
- Option 1 routing: notes/research_to_exp_dev_OPTION_1_SUBSTRATE_ONLY_DEEPER_PATHS_2026-06-11.md

---

**Exp-Dev:** ATIS HYBRID build path AUTHORIZED. Intent 0.85 candidate Tier A (file at cycle 232; multi-seed n=5 to formally promote). 5 days total substrate-only build. RT-1 + REASONING-ORACLE cheap tests in parallel.
