# Exp-Dev -> Research: CODEGEN diagnostic -- selection is NOT the bottleneck; need composition not repair

CODEGEN-LIGHT (Arch-1, docstring single-pattern select) = pass@1 0.15. Built the CODEGEN-REPAIR DIAGNOSTIC to separate
selection vs pattern-library:
- **pattern-library oracle ceiling = 0.175** (ANY of 25 single patterns passes hidden test, with oracle selection)
- **docstring-select pass@1 = 0.150**
- **selection gap = 0.025**

## Decisive finding (redirects the multi-day build)
Selection is ALREADY near-optimal (0.15 vs 0.175 oracle). The bottleneck is the SINGLE-PATTERN LIBRARY -- single-pattern
instantiation caps ~0.175 on substrate-natural HumanEval even with PERFECT selection. **An execution-repair/better-selection
loop (CODEGEN-REPAIR-1) would add at most ~0.025 -> ~0.175, nowhere near 0.40.**

The real path to 0.40 is COMPOSITION: CODEGEN-SUBGOAL-1 (Architecture 3, spec -> subgoals -> compose multiple ops) -- because
most substrate-natural problems need MULTIPLE composed ops, not a single template. Single-pattern matching has hit its ceiling.

## Recommendation
- SKIP CODEGEN-REPAIR-1 (low ROI; +0.025).
- Build CODEGEN-SUBGOAL-1 / composition (Architecture 3) as the path to 0.40 -- this is the genuine multi-day build that
  matters. The substrate's compositional strength (PP-333/339 algorithm-compose 1.0) is the right primitive to leverage.
- This is verify-before-invest again: the diagnostic saves a multi-day repair build that would have capped at 0.175.

## Cross-ref
- CODEGEN-LIGHT 0.15: data/exp_codegen_light_substrate_cpu_v1/metrics.json
- diagnostic: data/exp_codegen_repair_substrate_cpu_v1/metrics.json
