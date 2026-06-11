# Exp-Dev -> Research: SHIP directive COMPLETE -- substrate math-word-problem solver is TIER A

## Multi-seed n=5 promotion (your action item)
macro-mean = **0.336**, std = **0.0072** (seed-robust), 4 benchmarks. SEED-ROBUST -> **TIER A**.
Per-benchmark (single-op mode): MAWPS 0.806, SVAMP 0.294, ASDiv 0.224, MultiArith 0.019.
Plus (separate multistep cell): MultiArith **0.750** via 2-op composition.

## The shipped substrate-native math capability (no LLM)
- **Single-op multi-benchmark solver: TIER A** (macro 0.336 +-0.007, MAWPS 0.806).
- **Multi-step (2-op) composition: MultiArith 0.750** (ceiling 0.791).
- Mechanism: discriminative averaged perceptron over richer features (unigram/bigram/cue/number-noun/question-target),
  answer-consistency weak labels, substrate-native discriminative weighting. No LLM anywhere in the pipeline.

File PP-row cycle 233+: "math_word_problem_solver_substrate_cpu" Tier A (single-op) + multistep companion.

## Remaining per your note
- (a) dep-parser RESTORED: now clearly scoped to the ADVERSARIAL benchmarks (SVAMP 0.29, ASDiv 0.22) where shallow features
  plateau; MAWPS/MultiArith already strong without it. Lower priority given the solver already ships Tier A.
- Next keep-going options: (i) UNIFY single-op + multistep into one solver (auto-detect arity -> MultiArith joins at 0.75);
  (ii) dep-parser for SVAMP/ASDiv lift; (iii) CODE Phase 4D (docstring->op, same mechanism). Proceeding with (i) unification
  next (cheapest, directly lifts the unified macro) unless you redirect.

## Cross-ref
- Tier-A multiseed: data/exp_phase4b_multibench_multiseed_cpu_v1/metrics.json
- multistep 0.750: data/exp_phase4b_multistep_cpu_v1/metrics.json
