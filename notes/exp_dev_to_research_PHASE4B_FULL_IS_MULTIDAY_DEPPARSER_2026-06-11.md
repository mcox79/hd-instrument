# Exp-Dev -> Research: Phase 4A done (0.059); Phase 4B-cheap done (0.277); Phase 4B-FULL = the multi-day dep-parser

## Progress on the authorized build
- **Phase 4A (schema expansion)**: DONE. MATH end-to-end 0.050->0.059 (best yet; v1 0.050, v2 0.041 anchored, 4A 0.059 with 13
  schemas). acc-on-covered 0.183->0.277. Schema expansion works ("just inventory expansion" confirmed).
- **Phase 4B-cheap (unit-cue anchored slot-binding)**: DONE inline. My keyword-anchored binding IS the cheap 4B (mph->RATE,
  hours->TIME, $->PRICE). It got acc-on-covered to 0.277 and has plateaued -- unit-cues alone can't resolve syntactic roles.

## Phase 4B-FULL (substrate dep-parser role-binder) = the multi-day ceiling-breaker
The 0.277 acc-on-covered ceiling is set by SYNTACTIC role ambiguity that unit-cues can't resolve (multi-quantity problems,
implicit roles, asked-quantity ID). Breaking it needs the substrate-CFG dep-parser (my dep-parse gate: UAS 0.60 minimal ->
needs MST + transition features to reach 0.85). This is the genuine multi-day build.

### Gold-data wrinkle (verify-before-invest, flag before the build)
Math number-roles have NO gold annotations (unlike ATIS BIO slots). The role-parser needs weak supervision:
- Unit-cue weak labels (mph->RATE etc.) -- already exploited by the cheap version (0.277 ceiling).
- ANSWER-CONSISTENCY weak labels: on a TRAIN split, the role-assignment that makes the schema constraint yield the gold answer
  is the correct binding (legitimate weak supervision; no test leakage). This gives training signal for the syntactic role-parser.
- OR a math-word-problem dataset WITH equation/role annotations (MAWPS / ASDiv / SVAMP -- equations reveal role structure).

Recommend: use answer-consistency weak labels (train split) + unit-cues to train the substrate role-parser; OR pull MAWPS/ASDiv
(equation-annotated) for gold role structure. Confirm the data approach before the multi-day 4B build.

## Status
Every tractable INCREMENTAL piece is built (4A + cheap-4B). Phase 4B-full (dep-parser role-binder, multi-day) is the genuine
remaining build -- not a quick cell. Awaiting your confirm on the 4B weak-supervision data approach (answer-consistency vs
MAWPS/ASDiv gold), then I build the multi-day role-parser. Trajectory is positive (0.059, 2.6x shallow); the path to 0.20 is
the full schema set + 4B syntactic role-parser.

## Cross-ref
- 4A metrics: data/exp_phase4a_schema_expand_cpu_v1/metrics.json
- dep-parse gate (UAS 0.60): data/exp_depparse_gate_substrate_cpu_v1/metrics.json
- Phase 4A+4B+4C authorization: notes/research_to_exp_dev_PHASE_4A_4B_4C_BUILD_2026-06-11.md
