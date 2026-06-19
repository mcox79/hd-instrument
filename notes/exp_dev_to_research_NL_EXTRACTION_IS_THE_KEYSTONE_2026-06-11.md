# Exp-Dev -> Research: consolidated finding -- NL-spec understanding is the keystone for BOTH MATH and CODEGEN

## Two parallel investigations converge on ONE bottleneck

### CODEGEN path (4 experiments, decisive)
- CODEGEN-GATE-1: grammar-constrained AST -> valid Python (syntax 0%); 3/5 but 2 patterns tailored.
- CODEGEN-LIGHT: docstring single-pattern selection -> pass@1 0.150 on 40 substrate-natural.
- CODEGEN-REPAIR diagnostic: pattern-library oracle-ceiling 0.175 -> SELECTION is near-optimal; single-pattern library is the cap.
- CODEGEN-SUBGOAL: fixed filter->map->reduce composition -> 0.025 (WORSE; keyword decomposition mis-decomposes).
=> substrate-only code-gen via pattern/composition heuristics caps ~0.15-0.175. The gap is NOT the back-end (grammar/compose
   work); it's docstring->semantic-decomposition (understanding WHAT the problem asks).

### MATH path
- MATH-LIGHT: substrate-symbolic solve 0.947 accuracy + 1.0 recall on the ~9% clean-symbolic subset; coverage is the gap
  (word-problems dominate). Back-end (symbolic solve) works; NL word-problem parsing is the gap.

## The keystone
BOTH MATH and CODEGEN hit the SAME wall: NL-SPEC UNDERSTANDING (docstring / word-problem -> structured form). The substrate
BACK-END is validated and strong (symbolic solve 0.947; op-compose PP-333/339 1.0; grammar-valid codegen). The FRONT-END
(NL -> structure) is the universal bottleneck.

=> The single highest-leverage build is your **substrate-only NL-extraction pipeline** (POS-tagger PP-362 0.906 + dep-parser +
quantity/intent extraction). It unlocks coverage for BOTH MATH (word-problems) AND CODEGEN (docstrings) simultaneously. The
pattern/composition heuristics are the wrong layer to keep iterating; the NL front-end is the keystone.

## Recommendation
- STOP iterating CODEGEN pattern/composition heuristics (capped ~0.175; characterized).
- Build the substrate-only NL-extraction pipeline (dep-parser) as the keystone -- it serves MATH + CODEGEN + the broader
  substrate-only-NL claim. This is the multi-day build that matters; leverages the Tier-A POS tagger.
- I've exhausted the quick CODEGEN/MATH experiments; the dep-parser is the next genuine multi-day frontier.

## Cross-ref
- CODEGEN: data/exp_codegen_{gate1,light,repair,subgoal}_substrate_cpu_v1/metrics.json
- MATH-LIGHT: data/exp_math_light_substrate_cpu_v1/metrics.json
- POS tagger Tier A (PP-362): notes/exp_dev_to_research_PP362_TIER_A_2026-06-11.md
