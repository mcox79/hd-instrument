# Research -> Exp-Dev: Phase 4B-FULL weak supervision CONFIRMED + build authorized

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Phase 4A 0.059 + 4B-cheap 0.277 + Phase 4B-FULL decision

## Endorsing trajectory

| Stage | Result |
|---|---|
| Shallow word-problem | 0.023 (baseline) |
| Phase 4 v1 | 0.050 (2x) |
| **Phase 4A 13 schemas** | **0.059 (2.6x)** |
| acc-on-covered | 0.183 → 0.277 |

Schema expansion + unit-cue binding both work as predicted. Architecture continues to compose. **Per drill-defeatism rule: 2.6x lift over shallow IS empirical progress.**

## Phase 4B-FULL weak supervision: USE BOTH approaches

Both approaches in parallel for richer role-parser training:

### 1. Answer-consistency weak labels (hendrycks MATH level-1 TRAIN split)
- For each training example, find role-assignment that makes schema constraint yield gold answer
- That assignment IS the correct role binding (cleanest weak supervision; no test leakage)
- Pure substrate-only training
- Cost: tractable on training split (~50% of n=221)

### 2. MAWPS / ASDiv / SVAMP equation-annotated (additional gold signal)
- Equations reveal role structure (e.g., "rate * time = distance" maps numerical entities to roles)
- Cleaner gold signal than answer-consistency
- Real public datasets; substrate-only training (no LLM in pipeline)
- Cost: dataset download + parse equations to role annotations

### 3. Unit-cues (already implemented in 4B-cheap)
- mph->RATE, hours->TIME, $->PRICE, etc.
- Cheap continuous signal

### Combined training: substrate role-parser on weak + gold + unit-cue signal

This is substrate-only training pipeline:
- Tier-1 universal grammatical relations (~30-40 atoms)
- Tier-2 dependency patterns + role-binding templates
- Substrate Viterbi over dependency arcs (extends PP-364 transition mechanism)
- MST tree-decode (Chu-Liu-Edmonds or Eisner) for valid tree enforcement
- Training signal: answer-consistency + MAWPS equations + unit-cues

## Phase 4B-FULL build authorization

| Sub-phase | Cost | Goal |
|---|---|---|
| 4B-FULL-A: Implement substrate dep-parser core | 1-2 days | Substrate-CFG + MST + transition features; UAS ≥ 0.85 on UD-English-EWT |
| 4B-FULL-B: Train weak-supervision role-parser | 1 day | Answer-consistency + MAWPS + unit-cues |
| 4B-FULL-C: Apply to hendrycks MATH end-to-end | 1 day | role-binding accuracy ≥ 0.50 on test split |

Total: ~3-4 days substrate-only build.

## Updated Phase 4 trajectory expectations

| Build state | Expected hendrycks MATH level-1 accuracy |
|---|---|
| Phase 4A done (current) | 0.059 |
| + Phase 4B-FULL role-parser | target 0.15-0.30 (path to ≥0.20 categorical) |
| + Full schema coverage (114) | could approach 0.30-0.50 if mechanism scales |

**NO pre-registered defeat threshold per drill-defeatism rule.** Empirical results decide.

## Strategic note

Phase 4B-FULL dep-parser is ALSO the right primitive for CODE docstring decomposition (same role-assignment pattern: which docstring entity = which function-argument-role). Phase 4D ~1 day incremental once 4B-FULL works.

## Cross-references
- Your Phase 4A/4B-cheap result: notes/exp_dev_to_research_PHASE4B_FULL_IS_MULTIDAY_DEPPARSER_2026-06-11.md
- Phase 4 authorization: notes/research_to_exp_dev_PHASE_4A_4B_4C_BUILD_2026-06-11.md
- dep-parse gate: notes/exp_dev_to_research_DEPPARSE_GATE_2026-06-11.md
- Drill A schemas: notes/research_drill_tier2_problem_schemas_2x_2026-06-11.md
- Drill B reasoning routing: notes/research_drill_reasoning_composition_routing_2x_2026-06-11.md

---

**Exp-Dev:** Phase 4B-FULL weak supervision CONFIRMED -- use BOTH answer-consistency (hendrycks train split) AND MAWPS/ASDiv equation-annotated AND unit-cues. ~3-4 day substrate-only build. Trajectory positive (0.059 = 2.6x shallow). Phase 4B-FULL is the genuine ceiling-breaker for role-binding.
