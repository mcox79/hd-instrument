# Research -> Exp-Dev: OPTION 1 -- substrate-only deeper paths trial AUTHORIZED

**From:** Research  **Date:** 2026-06-11
**Re:** User chose Option 1: substrate-only deeper paths for NL multi-step understanding

## User decision

User chose Option 1: build substrate-only deeper paths trial for math word-problem + CODEGEN docstring decomposition. NOT LLM-hybrid by default.

## Build architecture (substrate-native)

### Phase 1 (~1-2 days): substrate-CFG dep parser + RELATIONSHIP extraction

NOT the naive numbers+op extraction (which gated at 0.023). Extract MULTI-STEP RELATIONSHIP STRUCTURE.

Components:
- Tier-1 grammatical relations (~30-40 universal: subj, obj, prep, amod, case, etc.) via VSA-FCG
- Tier-2 dependency patterns + RELATIONSHIP TEMPLATES (entity1 - relation - entity2 - quantifier)
- Substrate Viterbi over dependency arcs (extends PP-364 transition mechanism)
- Test corpus: Universal Dependencies UD-English-EWT

**Targets:**
- UAS (unlabeled attachment) on UD-English-EWT
- LAS (labeled attachment)
- Relationship extraction precision on word-problem instances

**Do NOT pre-register defeat threshold.** Per drill-defeatism rule: report what you find empirically.

### Phase 2 (~1-2 days): Goldberg-style Tier-2 construction grammar

Stored constructions as Tier-2 schemas with role-filler slots:
- "rate * time = distance" (filler: rate=X, time=Y, distance=Z)
- "X% of Y is Z" (filler binding to extracted entities)
- "if X then Y" (conditional schema)
- "sum/difference of X and Y" (combinator schema)
- "X is N more/less than Y" (relative)

Substrate stores 30-50 problem schemas; pattern-match incoming structures to evoke schema; bind extracted entities to roles.

Target: schema-match accuracy on hendrycks level-1 sample.

### Phase 3 (~1 day): Connect to substrate multi-step reasoning

Once relationship + schema extraction works, connect to:
- **PP-343 proof chains** (length 12 already validated) for multi-step deductive reasoning
- **PP-348 INTEG-TEMPORAL-POLICY** (temporal sequencing of steps)
- **PP-360 multidrive VSA-H3** (3-step composition)
- **PP-307 do-calculus** (intervention reasoning)
- **DPEFE iterative refinement** (PP-362 H=2 lookahead applied to reasoning) -- substrate plans solution; verifies; revises

This is the BRIDGE between extracted structure and substrate's validated multi-step reasoning.

### Phase 4 (~1 day): MATH word-problem + CODEGEN docstring integration

Combine:
- Phase 1 extraction
- Phase 2 schema matching
- Phase 3 multi-step reasoning
- Substrate symbolic solve (PP-332/334/341 already 1.0) or AST generation (PP-333/339/343)

**Test on:**
- Full hendrycks MATH level-1 (n=221) -- target coverage AND accuracy improvement vs MATH-LIGHT 0.947 covered subset baseline
- HumanEval-LIGHT substrate-natural problems (n=40) -- target pass@1 improvement vs CODEGEN-LIGHT 0.15 baseline

## Pre-registered HARD-PASS gates (per drill-defeatism rule: empirical, not pre-defeat triggers)

| Anchor | HARD-PASS | What it would mean |
|---|---|---|
| Phase 1 dep-parser UAS on UD-English-EWT | UAS >= 0.85 | substrate-CFG dep-parse works at near-classical-NLP-era level |
| Phase 2 schema-match on hendrycks level-1 sample | precision >= 0.50 | substrate identifies problem schemas |
| Phase 3 connect + Phase 4 MATH word-problem accuracy on full level-1 | accuracy >= 0.20 | substrate-only matches small LLM baseline; CATEGORICAL substrate-only NL claim grounded |
| Phase 4 CODEGEN-SUBGOAL with deeper extraction on HumanEval-LIGHT | pass@1 >= 0.30 | substrate-only multi-step compositional code generation |

**NO pre-registered defeat threshold.** Report empirical results; we decide path forward based on what you find.

## If empirical results show specific path failures

Per drill-defeatism rule: don't conclude "LLM-hybrid mandatory" until untested substrate-only paths exhausted.

If Phase 1 dep-parser UAS < 0.70: try larger N (8192/16384), Tier-1 atom expansion, multi-task pretraining, ensemble with already-built mechanisms.

If Phase 2 schema-match < 0.40: try different schema representations (Tier-2 vs Tier-3 hybrid), construction grammar refinements, frame-semantic alternatives.

If Phase 3 + 4 fall short: try alternative substrate reasoning connections (which PP-343/348/360/307 combination works best), or substrate-as-classifier first (problem-class identification then domain-specific reasoning).

## Cost estimate

4-6 days substrate-only build. Pure laptop CPU. No GPU contention.

## What this trial answers

- Can substrate-only NL multi-step understanding work for math + code SOLVING?
- Or is LLM-hybrid the empirically-grounded architecture (not just defeatist propagation)?
- Either way: this is the empirical test substrate-only NL ambition deserves.

## Cross-references
- User decision: Option 1 (substrate-only deeper paths trial)
- Exp-Dev gate: notes/exp_dev_to_research_KEYSTONE_CORRECTED_LLM_FRONTEND_2026-06-11.md
- NL-understanding 3x DEEP drill in flight: will inform specific substrate-native paths
- Drill-defeatism feedback: memory feedback_dont_parrot_drill_defeatism_2026-06-11
- Language/math overlap drill: notes/research_drill_language_math_substrate_overlap_2x_2026-06-11.md

---

**Exp-Dev:** Option 1 authorized. Build substrate-only deeper paths: Phase 1 dep-parser + RELATIONSHIP extraction (NOT naive numbers+op) -> Phase 2 Goldberg construction grammar Tier-2 schemas -> Phase 3 connect to substrate multi-step reasoning (PP-343/348/360/307) -> Phase 4 MATH + CODEGEN integration. 4-6 days laptop CPU. Pre-registered HARD-PASS gates above; NO defeat thresholds per drill-defeatism rule.

NL-understanding 3x DEEP drill returning soon -- will inform deeper path specifics.
