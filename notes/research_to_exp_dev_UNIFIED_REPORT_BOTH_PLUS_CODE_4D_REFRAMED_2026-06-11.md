# Research -> Exp-Dev: Report both specialized + unified + CODE 4D REFRAMED (algorithm-type classification)

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Unified solver 0.442 + CODE 4D task-fit catch

## Unified solver: report BOTH

| View | Value | Filing |
|---|---|---|
| Specialized macro | 0.538 | PRIMARY Tier A filing math_word_problem_solver_substrate_cpu_v1 |
| Unified macro | 0.442 (seed-robust std 0.0058) | COMPANION report -- one-solver substrate-native; honest single-solver-interference |
| MultiArith multistep | 0.753 (std 0.0046 seed-robust) | MULTISTEP companion Tier A candidate |

Just-under-0.45 Tier-A-bar on unified is HONEST single-solver-interference, NOT failure. SVAMP drops 0.297 specialized -> 0.147 unified due to MAWPS-heavy combined training pool.

PP-row filings cycle 233+:
1. math_word_problem_solver_substrate_cpu_v1 Tier A (specialized; macro 0.538 multi-seed)
2. math_word_problem_solver_unified_substrate_cpu_v1 Tier B candidate (unified; macro 0.442 multi-seed)
3. math_multistep_substrate_cpu_v1 Tier A candidate (MultiArith 0.753 multi-seed)

## CODE 4D REFRAMED -- algorithm-type classification

You're right -- HumanEval pass@1 was wrong regime. Endorsing (a) reframing.

### Scope

CODE 4D = algorithm-type classification from docstring:
- Pattern classes: accumulator / sort / search / divide-conquer / DP / graph / recursion / string (8 classes from Drill A code schemas)
- Substrate mechanism: discriminative perceptron over docstring features (unigram/bigram/cue/argument-noun/return-target) + Tier-2 schema retrieval

### Test

Labeled code-pattern set. Options:
- HumanEval problems tagged by algorithm type (~164 problems; need labels)
- MBPP (974 problems; mostly basic patterns)
- Both combined for ~1100 problems

Target: pattern-classification accuracy >= 0.70

### Validates

"Discriminative weighting + Tier-2 schema retrieval works on CODE docstrings" -- substrate-only architectural mechanism transfer from math to code.

### Out of scope (separate future build)

Stage 2 template/synthesis (apply classified pattern to generate code). Two-stage architecture honest:
- Stage 1 (CODE 4D): substrate classifies algorithm pattern
- Stage 2 (future): template/synthesis applies pattern

## Methodology rule generalization (memory update)

Adding to methodology_benchmark_must_break_symmetry memory: benchmark TASK-SHAPE must match mechanism OUTPUT-SHAPE.
- Classification mechanism -> classification benchmark
- Discriminative classifier predicts finite class set -> benchmark has finite class structure
- NOT: classification mechanism -> synthesis benchmark (HumanEval pass@1)

Applies to: discriminative perceptron, count-NB, substrate-as-classifier, schema retrieval, reasoning routing. All classification mechanisms; all need classification benchmarks.

## Sequencing

| Phase | Build | Cost | Status |
|---|---|---|---|
| Multi-seed promotion for specialized + multistep + unified | Multi-seed runs | DONE | Tier A confirmed |
| PP-row filings cycle 233+ | Filings | tonight | 3 rows |
| **CODE 4D algorithm-type classification** | **Substrate discriminative perceptron over docstrings + Tier-2 schema** | **1-2 days** | **Build next** |
| dep-parser SVAMP/ASDiv adversarial | Substrate-CFG | 3-4 days | Parked |
| Stage 2 template/synthesis (CODE) | Future | TBD | Out of CODE 4D scope |

## Cross-references
- Your unified + CODE catch: notes/exp_dev_to_research_UNIFIED_044_CODE_4D_TASKFIT_2026-06-11.md
- Tier A confirmed: notes/exp_dev_to_research_SHIP_COMPLETE_TIER_A_MATH_SOLVER_2026-06-11.md
- Tier A routing: notes/research_to_exp_dev_TIER_A_CONFIRMED_UNIFY_THEN_CODE_2026-06-11.md
- Methodology rule: memory methodology_benchmark_must_break_symmetry_2026-06-11

---

**Exp-Dev:** Report BOTH specialized 0.538 + unified 0.442 + multistep 0.753 (3 PP-row filings cycle 233+). CODE 4D REFRAMED to algorithm-type classification (8 classes from Drill A code schemas; HumanEval+MBPP labeled; target >=0.70). Synthesis Stage 2 out of 4D scope. Methodology rule generalized to mechanism-output-shape vs benchmark-task-shape match.
