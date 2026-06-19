# Research -> Exp-Dev: Wave-2 HP recipes for HumanEval / MBPP / MATH benchmarks + POS-tagger

**From:** Research  **Date:** 2026-06-11
**Re:** Your Wave-1 TIER-0 complete; HP recipes needed for Wave-2 benchmark promotion

## Wave-1 endorsement

14/15 promoted D->C at n=5 seeds + 2 GPU validations + LVH-277 closed = unambiguous Wave-1 success. ~14 capabilities promoted in one sweep. capability matrix Tier C grew from 11 to ~25.

## HP recipes for Wave-2 Tier-1 benchmarks

All substrate-only (NO LLM hybrid) per user direction. Privilege TEMPORAL+CONTEXTUAL mechanisms per cycle 226 meta-finding. Privilege per-tier defaults + Tier-1-frozen + per-role substrate per Sprint-4 results.

### HumanEval (n=164 Python function tasks)

**Substrate-native architecture:**
- Spec parsing: tokenize keyword-spec (already validated PP-340 at 0.75 on n=12; this is HumanEval-STRUCTURAL with clean spec input)
- Code generation via program-shard composition (PP-333 1.000 n=300 at smaller scale; PP-339 algorithm-compose 1.000 4-step)
- Op codebook: 50-100 Python ops as Tier-3 entities (call, assign, if, for, return, etc.)
- Identifier codebook: function args + locals as Tier-3 entities
- Compose via Levelt pipeline (top-down): function -> body statements -> expression -> op + args
- Per-role substrate (PP-356 validated n=5): code substrate isolated from math/comm substrates

**HP gate:** pass@1 >= 0.15 (small LLM baseline; substrate-only ON STRUCTURAL).
**HARD-PASS:** pass@1 >= 0.30 (categorical: substrate beats small-LLM at structural benchmark).
**HARD-FAIL:** pass@1 < 0.05 (substrate can't generate working code at scale).

**Cost:** ~3-5 hr CPU. Per-task evaluation = subprocess Python execute + result check.

**Anchor:** humaneval_substrate_full_cpu_v1

### MBPP (Mostly Basic Python; broader; smaller spec format)

**Substrate-native architecture:**
- Same generator as HumanEval but trained on MBPP-style specs
- Specs are more natural-language than HumanEval; CONTEXT-BINDING (PP-346 validated) for spec disambiguation

**HP gate:** pass@1 >= 0.20.
**HARD-PASS:** pass@1 >= 0.40.
**HARD-FAIL:** pass@1 < 0.10.

**Cost:** ~3-5 hr CPU.

**Anchor:** mbpp_substrate_full_cpu_v1

### MATH benchmark (high-school competition)

**Substrate-native architecture:**
- Problem parsing: parse LaTeX math expressions to substrate algebraic representation
- Rule application: substrate stores ~200-500 algebraic + calculus + algebra-2 rules as Tier-2 schemas
- Solve via composition (PP-332 1.000 algebra simplify; PP-334 1.000 calculus; PP-341 1.000 equation solve; PP-343 1.000 proof chains length 12 -- all generalize to MATH)
- Per-tier importance: Tier-1 = arithmetic/foundational; Tier-3 = problem-specific entities (faded)
- Temporal policy for multi-step problems (per PP-348)

**HP gate:** accuracy >= 0.20 (small LLM baseline).
**HARD-PASS:** accuracy >= 0.35 (categorical: substrate competitive on math).
**HARD-FAIL:** accuracy < 0.05.

**Cost:** ~4-8 hr CPU (parsing LaTeX is the main cost).

**Anchor:** math_benchmark_substrate_full_cpu_v1

### POS tagger Penn Treebank WSJ sec 24 (LLM-boundary engineering test)

**Substrate-native architecture (per LLM-boundary 3x DEEP drill):**
- Tier-1 codebook: 45 POS tags as universal grammatical atoms
- Tier-3 codebook: ~50K word entities as Tier-3 entities with Tier-1 POS labels (Brill rules)
- Substrate transitions: word -> POS via substrate retrieval (PP-227 hybrid pattern)
- Context window: 2 words left + 2 right (per pre-LLM era methods)
- Compose: word + context -> POS classification via cleanup over Tier-1

**HP gate:** tag-accuracy >= 0.90 (Brill achieved 96.7% in 1995).
**HARD-PASS:** tag-accuracy >= 0.95.
**HARD-FAIL:** tag-accuracy < 0.80.

**Cost:** 4-8 hr CPU.

**Significance:** This is the cheapest decisive test of "substrate can do NL" claim. If passes, substrate-only NL pipeline is empirically grounded.

**Anchor:** pos_tagger_ptb_wsj_substrate_cpu_v1

## Sequencing

**Day 1 (immediate, parallel):**
- HumanEval full (most important Wave-2; substrate code claim)
- POS tagger PTB WSJ sec 24 (cheapest LLM-boundary test)

**Day 2:**
- MBPP (extends HumanEval)
- MATH benchmark (extends PP-332/334/341/343)

**Day 3:**
- Multi-seed n=5 on whichever passes Day 1-2
- Promote passing benchmarks B->A (production claim)

## What to do for Wave-2 Tier-2 (CLS + LVH-278 rescues per Exp-Dev plan)

CLS rescue (per 2x drill landed):
- RESCUE-4 + RESCUE-2 combined (offline dedicated consolidation + N_slow=8192)
- Anchor: cls_rescue4_plus_rescue2_cpu_v1

LVH-278 neurogenesis threshold recalibration:
- Tune merge threshold to combine 13 shards to 12
- Anchor: neurogenesis_threshold_tune_cpu_v1

Both <1 hr CPU each.

## Bonus: 5 negative-drill rescues empirical tests

Per the 5 2x DEEP drills that just landed, each has a cheap empirical test:

| Rescue | Cost | HARD-PASS target |
|---|---|---|
| CLS RESCUE-4+RESCUE-2 (offline consolidation) | <1hr | recent >= 0.85, old >= 0.70 |
| code2 R-SOFT-DECODE (cleanup confidence margin) | <2hr | F1 >= 0.78 |
| active inference E1+E2 (pragmatic_value + boredom gamma) | <2hr | error_drop > 30%, goal_reach > 0.70 |
| slipnet TTR (type-typed-routing) | <1hr | recall@1 >= 0.75 |
| **96% irreducible VSA policy H=3** (predicted 3-5x lift) | <2hr | worst-drive abs satisfaction > 50% |

All can run in parallel with Wave-2 benchmarks.

## Cross-references
- Wave-1 result: notes/exp_dev_to_research_WAVE1_TIER0_COMPLETE_2026-06-11.md
- Promotion campaign: notes/research_to_exp_dev_PROMOTION_CAMPAIGN_WAVES_2026-06-11.md
- 5 negative 2x drills: notes/research_drill_cls_2substrate_rescue_2x + code2_bug_recall_close + active_inference_rescue + slipnet_real_polysemic_rescue + irreducible_multidrive_probe (all 2026-06-11)
- LLM-boundary 3x DEEP: notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md

---

**Exp-Dev:** HP recipes filed for HumanEval + MBPP + MATH benchmarks + POS tagger. Plus 5 negative-drill rescues with <2hr CPU each. All Wave-2 Tier-1 anchors ready to dispatch.

The substrate Tier-A claim grows from 5 to ~20-25 if HumanEval + POS tagger + 3-4 rescues land at PASS.
