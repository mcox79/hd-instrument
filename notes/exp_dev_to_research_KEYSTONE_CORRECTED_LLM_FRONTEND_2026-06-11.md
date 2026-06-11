# Exp-Dev -> Research: keystone CORRECTED -- reasoning (not parsing) is the gap; LLM-hybrid front-end is architecturally correct

## I tested the keystone hypothesis (NL-extraction) before the multi-day dep-parser build. It's refuted at the root.

Word-problem extraction GATE: numbers + operation-keyword extraction -> attempt-coverage 0.801, accuracy **0.023** (4/177).
Extraction FINDS the numbers + an operation for 80% of word-problems, but the recovered "numbers + one-op" structure is WRONG
for ~98% -- because level-1 word-problems need SEMANTIC MULTI-STEP REASONING (relationships, units, intermediate steps), not
a single quantity+operation. A richer dep-parser would PARSE better but still not SOLVE -- parsing isn't the gap, reasoning is.

## Corrected strategic conclusion
My earlier "build the dep-parser as the keystone" was half-right. Sharper conclusion from the gate:
- Substrate BACK-END is strong + validated: symbolic solve 0.947 (covered), op-compose PP-333/339 1.0, grammar-valid codegen,
  POS-tagging 0.906 Tier A.
- The FRONT-END for math/code is NOT parsing -- it's SEMANTIC MULTI-STEP REASONING (understand the problem, decompose to a
  solution plan). That is the LLM regime by definition.
- A substrate-only dep-parser would extract structure but not produce the reasoning -> would also fall short. DON'T build it
  expecting to crack MATH/CODEGEN solving.

## Recommendation (the boundary thesis, empirically grounded)
For math-word-problem + arbitrary-code-gen SOLVING: **LLM front-end (understand + decompose) + substrate back-end (symbolic
execute / verify)** is architecturally correct. This matches the substrate-LLM boundary memory. The substrate's categorical
wins are where structure is GIVEN or shallow (POS tagging, symbolic solve, op-compose, KB memory, the v3.2 wrappers) -- those
are real and strong. Deep NL-reasoning tasks are the LLM's lane.

This is verify-before-invest at the strategic level: the gate (cheap) saved a 3-5 day dep-parser build that the evidence says
would not reach the solving bar. I recommend redirecting from "substrate-only NL pipeline for math/code" to LLM-hybrid for
those, and concentrating substrate investment on its validated back-end strengths + production-scale (kb, KB-shard, wrappers).

## Cross-ref
- gate: data/exp_math_wordproblem_extract_gate_cpu_v1/metrics.json
- CODEGEN 4-exp + MATH-LIGHT: prior notes (NL_EXTRACTION_IS_THE_KEYSTONE, CODEGEN_DIAGNOSTIC, MATH_LIGHT_RESULT)
- boundary memory: substrate_LLM_boundary_decomposition_2026-06-10
