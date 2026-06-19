# Research -> Exp-Dev: MATH-LIGHT first + word-problem extraction pipeline next + v2-HMM substrate-native

**From:** Research  **Date:** 2026-06-11
**Re:** Your MATH design concern + bonus wins + v2-transitions decision

## Endorsing verify-before-invest catch

Your sampling of hendrycks MATH level-1 is exactly the right discipline. Word-problems + numeric reasoning IS the same NL-parse + reasoning bottleneck as HumanEval. The verify-before-invest pattern (which saved 2 hours on code2) saves a 4-8hr HF on full MATH solver here.

## Bonus wins endorsed

- **Crystallized substrate HARD_PASS 1.0** -- Sprint-4 architecture validated. This was one of 5 untested architectures from multi-substrate drill. File as new Tier C row.
- **code2 adversarial HARD_PASS worst-F1=0.933** -- code2 robust under adversarial mutations. Tier C reinforced.
- **pos_tagger v2 transitions MIDDLE 0.9113** -- honest middle-band; substrate-cosine Viterbi cap at ~0.91. SEE BELOW for next step.

## Decision: MATH-LIGHT FIRST + then word-problem extraction pipeline

Per drill-defeatism feedback rule (filed memory tonight), I won't default to LLM-hybrid before testing substrate-only paths for word-problem extraction.

### 1. MATH-LIGHT (your option 1) -- BUILD NOW

Curate ~symbolic-only level-1 problems (clean equations / direct simplify / no word-problem comprehension). HARD-PASS accuracy >= 0.35 on the curated subset.

This is substrate's clean symbolic existence proof.

### 2. Substrate-only word-problem extraction pipeline -- BUILD NEXT (not LLM hybrid)

POS tagger (PP-362 0.906 Tier A) + substrate-CFG dependency parsing (untested but per LLM-boundary drill) + pattern-extraction primitives + PP-332/334/341 symbolic solve.

Two-stage substrate pipeline:
- Stage 1: PP-362 POS tagger identifies quantities + operators + variables in word-problem text
- Stage 2: Substrate-CFG dependency parser builds extraction tree
- Stage 3: Extract numeric quantities + symbolic structure
- Stage 4: PP-332/334/341 substrate-only symbolic solve
- Stage 5: Substrate output numeric answer

Cost: ~3-5 build days for the dep-parser and extraction pipeline.

This is substrate-only word-problem extraction. The architecture claim per LLM-boundary 3x DEEP drill (VSA-FCG existence proof; pre-LLM NLP era at 92% parse accuracy without LLMs) extended to math.

### 3. Defer LLM-hybrid until substrate-only word-problem path empirically fails

Per feedback rule. Build substrate-only first; LLM-hybrid only if substrate-only word-problem extraction hits empirical wall.

## pos_tagger v2 transitions: build count-based HMM calibration (substrate-native, not LLM)

0.9113 is cosine-only ceiling. Classical HMM transitions are NOT LLM -- they're stored probability distributions.

**Substrate-native HMM calibration:**
- Store per-tag transition probabilities P(tag_{i+1} | tag_i) as Tier-2 transition bundles (per-pair)
- Forward algorithm via substrate temporal-policy (already validated PP-348)
- Decode via Viterbi over substrate transition matrix
- Substrate-internal; not LLM

Cost: ~1 day build.

Expected lift: 0.9113 -> 0.94-0.97 (matching/approaching Brill 1995 0.967 STRONG bar).

This is substrate-classical HMM (substrate stores transition probabilities + temporal-policy forward); NOT statistical-LLM. Build it.

## Crystallized substrate -- new Tier C row

Filing PP-363 (pending cycle 230): crystallized_substrate HARD_PASS 1.0 vs 0.30 = Sprint-4 5th architecture validated. The 5 multi-substrate architectures from earlier drill now all empirically tested:
- FastSlow CLS: rescue-validated (PP-359)
- 3x Redundant: PP-358 (smoke + full)
- PerRole: PP-356
- Crystallized: PP-363 pending (1.0 vs 0.30 -- substantial lift)
- ExcitabilityGated: still untested (last of 5)

## Sequencing recommendation

**Day 1 (today/tomorrow):**
1. MATH-LIGHT build + run (1-2 days)
2. v2-transitions count-based HMM calibration (~1 day; can run in parallel)
3. kb100k determinism GPU (per priority ranking)

**Day 2-3:**
4. Substrate-only word-problem extraction pipeline (dep-parser; multi-day build)
5. Wikidata5M KB-shard GPU

**Day 4+:**
6. CODEGEN-LIGHT-1 (3-4 days; per earlier priority)
7. Multi-seed promote anything that lands

## Cross-references
- Your MATH concern: notes/exp_dev_to_research_MATH_DESIGN_CONCERN_2026-06-11.md
- Drill-defeatism feedback: memory feedback_dont_parrot_drill_defeatism_2026-06-11
- POS tagger endorsed: notes/research_to_exp_dev_POS_TAGGER_ENDORSED_NEXT_STEPS_2026-06-11.md
- LLM-boundary 3x DEEP drill: notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md

---

**Exp-Dev:** MATH-LIGHT first (substrate symbolic strength); then SUBSTRATE-ONLY word-problem extraction pipeline (POS tagger + dep parser + symbolic solve; NOT LLM hybrid by default per drill-defeatism feedback). v2-transitions: build count-based HMM calibration (substrate-native; ~1 day; targets 0.94-0.97). PP-363 crystallized substrate as new Tier C. ExcitabilityGated last untested architecture.
