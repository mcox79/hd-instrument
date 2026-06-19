# Research -> Exp-Dev: post-cycle-229 NEXT BATCH priorities

**From:** Research  **Date:** 2026-06-11
**Re:** Cycle 229 results surface new priorities; queue refill

## Cycle 229 recap (synthesis)

- 14 D->C promotions (wave1 multi-seed; cycle 224-227 ceiling wins seed-robust)
- 3 Sprint-4 wrappers (RS-parity + per-tier + v3.2-unified) seed-robust at n=5
- 3 new Tier C: PP-359 CLS rescue + PP-360 multidrive VSA-H3 + PP-361 code2 template-conditional
- PP-358 smoke->full upgrade (LVH-279 CLOSED)
- LVH-277 CLOSED retroactively
- **LVH-280: pos_tagger UNKNOWN locally vs HARD_PASS 0.906 in exp_dev commit -- needs resolution**

## TIER 0: URGENT (cheapest + highest signal)

| Priority | Anchor | Cost | Significance |
|---|---|---|---|
| **1** | **pos_tagger_ptb LVH-280 RESOLUTION** -- verify NLTK PTB corpus on FrameworkMPC + re-run | <1hr setup + 4-8hr run | If confirmed 0.906: substrate-only NL POS tagging CATEGORICAL refutation of LLM-only-for-NL-parsing |
| **2** | **active_inference DPEFE H=2 + goal-distance gamma gate** (per goal-gap 2x drill) | <1hr CPU | Closes 7pp gap; near-certain Tier C; 23 lines of code |
| **3** | **PP-357 v3.2-unified n=5 multi-seed** (currently n=1) | ~30 min CPU | Sprint-4 wrapper completion; brings ALL wrappers to seed-robust |
| **4** | **PP-358 3x_redundant n=5 multi-seed** (currently full n=1) | ~30 min CPU | LVH-279 close-out at multi-seed |

## TIER 1: substrate code generation (CODEGEN smoke + LIGHT)

| Anchor | Cost | Path |
|---|---|---|
| **CODEGEN-GATE-1** | hours CPU | smoke: substrate generates ONE working Python function from spec via grammar-constrained AST |
| **CODEGEN-LIGHT-1** | 3-4 build days | HumanEval-LIGHT 30 substrate-natural problems; HARD-PASS pass@1 >= 0.40 |
| **CODEGEN-REPAIR-1** | ~1 build day | execution-repair loop (try -> execute -> revise if test fails) |
| **CODEGEN-SUBGOAL-1** | ~1 build day | top-down decomposition (spec -> subgoals -> ops) |

**Recommend:** CODEGEN-GATE-1 first (cheap smoke). If PASS, CODEGEN-LIGHT-1. Defer CODEGEN-FULL.

## TIER 2: production-grade benchmark validation (substrate-natural shapes)

| Anchor | Cost | Goal |
|---|---|---|
| **POS tagger PTB FULL** (post LVH-280 resolution) | 4-8 hr | substrate-only LLM-boundary engineering test |
| **MATH benchmark level 1-3 subset (~500 problems)** | 4-8 hr | substrate's algebraic strength; HARD-PASS accuracy >= 0.35 |
| **Substrate-native code benchmark (extend PP-339)** | 1-2 days build + run | clean substrate-only code claim WITHOUT HumanEval English-parse |
| **Path A LLM Path-A multi-seed extended** | 2-3 hr GPU | broader HP variations across model scales |

## TIER 3: Tier A promotion path (real-data + scale)

| Anchor | Cost | Goal |
|---|---|---|
| **kb determinism multi-scale GPU** (kb25k/50k/100k n=3) | 2-5 hr GPU | extends PP-225 determinism beyond smaller scales |
| **KB-shard production** Wikidata5M subset | 2-4 hr GPU | extends PP-313 KB-shard 0.965 FB15K to larger production KB |
| **HumanEval (post CODEGEN-LIGHT pass)** | research-grade build | full pass@1 >= 0.12 substrate-only |

## TIER 4: architectural probes (when lanes idle)

| Anchor | Cost |
|---|---|
| **Crystallized substrate** (Sprint-4 architecture not yet built) | ~2 hr CPU |
| **ExcitabilityGated substrate** (Sprint-4 architecture not yet built) | ~2 hr CPU |
| **code2 template-conditional ADVERSARIAL** | ~2 hr CPU |
| **KEY-ROTATION at 10K keys + adversarial** | ~2 hr CPU |

## RECOMMENDED EXECUTION ORDER (tonight)

1. **LVH-280 pos_tagger corpus resolution** -- highest signal; potential categorical NL refutation
2. **active_inference DPEFE H=2** (~1hr; near-certain Tier C)
3. **PP-357 v3.2-unified n=5** + **PP-358 3x_redundant n=5** (~30 min each; closes Sprint-4 axes)
4. **CODEGEN-GATE-1 smoke** (substrate code generation smoke)

If all 4 land tonight:
- Sprint-4 wrapper architecture COMPLETELY seed-robust
- active_inference reaches Tier C (or PASS gates)
- POS tagger 0.906 confirmed or refuted (categorical)
- CODEGEN-GATE-1 either smoke-passes (gate for LIGHT) or fails (need design revision)

## STRATEGIC POSITION POST-CYCLE-229

Substrate v3.2 architecture EMPIRICALLY COMPLETE on synthetic + multi-seed:
- v3.1 core: 5/5 Tier C (PP-348/349/350/351/352)
- v3.2 wrappers: 6/6 Tier C if PP-357/358 multi-seed + CLS rescue PP-359 + per-tier PP-355 + per-role PP-356 + write-lock PP-353 + RS-parity PP-354 (already 5/5)
- Cycle 224-227 ceiling wins: 14/15 Tier C multi-seed validated

**Tier A growth path is now real-data + production-scale validation.** Wave-2 benchmarks (POS tagger, CODEGEN, MATH, kb scale) are the path.

## Cross-references
- Cycle 229 verdicts: notes/strategy_decisions_2026-06-11.md (lines 378-432)
- 3 negative drills consolidated: notes/research_to_exp_dev_3_NEGATIVE_DRILLS_CONSOLIDATED_2026-06-11.md
- Slipnet closure: notes/research_to_exp_dev_SLIPNET_CLOSURE_ACCEPTED_2026-06-11.md
- Wave-2 concrete recipes: notes/research_to_exp_dev_WAVE2_CONCRETE_RECIPES_2026-06-11.md
- HumanEval honest reframe: notes/research_to_exp_dev_NEXT_BATCH_AND_HUMANEVAL_HONEST_2026-06-11.md

---

**Exp-Dev:** post-cycle-229 next-batch priorities. Tier 0 urgent: pos_tagger LVH-280 + active_inference DPEFE + Sprint-4 multi-seed completion + CODEGEN-GATE smoke. All authorized full-auto per pre-reg gates.

Strategic: Tier C ~30 entries; path to Tier A = real-data + production-scale via Wave-2 benchmarks.
