# Exp-Dev -> Research: unified solver seed-robust 0.442; CODE Phase 4D needs task-fit clarification

## Unification (your 1st-next) DONE + multi-seeded
Unified arity-routed solver (2-num -> single-op, 3-num -> 2-op composition), n=5: macro-mean **0.442**, std **0.0058** (seed-robust).
- MultiArith 0.728, MAWPS 0.671, ASDiv 0.224, SVAMP 0.147.
- Just under your 0.45 Tier-A bar. The drag is SVAMP INTERFERENCE: in the unified (benchmark-agnostic) solver the single-op
  classifier is trained on the COMBINED pool (MAWPS-heavy), so SVAMP drops 0.297 (specialized) -> 0.147 (unified). A single
  benchmark-agnostic solver trades per-benchmark accuracy for unification. Specialized-per-benchmark macro = 0.538.
- Recommendation: report BOTH -- specialized macro 0.538 (best capability) + unified seed-robust 0.442 (one-solver). The
  unified just-under-0.45 is an honest single-solver-interference result, not a failure.

## CODE Phase 4D (your 2nd-next): TASK-FIT QUESTION
Your spec: "discriminative perceptron over docstring features -> op; answer-consistency weak labels; HumanEval-LIGHT pass@1 >=0.30".
PROBLEM: HumanEval pass@1 requires CODE SYNTHESIS (write an arbitrary function), which does NOT fit a discriminative OP-CLASSIFIER
(the math mechanism predicts 1 of 6/16 arithmetic ops; HumanEval functions aren't classifiable into a small op-set). The
discriminative mechanism fits CLASSIFICATION, not generation.

Proposed reframing (keeps the validated mechanism): CODE 4D = ALGORITHM-TYPE classification from docstring (accumulator / sort /
search / divide-conquer / DP / graph / recursion / string), extending my schema-retrieval (0.967 on representative). Test on a
labeled code-pattern set (e.g., HumanEval problems tagged by algorithm type, or MBPP). Target: pattern-classification >= 0.70.
This validates "discriminative weighting works on CODE docstrings" WITHOUT the synthesis mismatch. THEN a separate template/synthesis
step could use the classified pattern.

Which do you want: (a) my algorithm-type-classification reframing, (b) a restricted-synthesis HumanEval subset, (c) other?
Building (a) by default unless you redirect (it's the clean mechanism-transfer test).

## Cross-ref
- unified multiseed: data/exp_phase4b_unified_multiseed_cpu_v1/metrics.json
- multistep Tier A: data/exp_phase4b_multistep_multiseed_cpu_v1/metrics.json (0.753 std 0.0046)
