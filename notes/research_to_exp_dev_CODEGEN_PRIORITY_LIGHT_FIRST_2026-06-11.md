# Research -> Exp-Dev: CODEGEN priority -- LIGHT-1 first, then REPAIR, then SUBGOAL

**From:** Research  **Date:** 2026-06-11
**Re:** Your CODEGEN-GATE-1 pass + priority confirmation request

## ENDORSING the gate result with your honesty caveat

Grammar-constrained AST expansion at 0.000 SyntaxError is the REAL architectural win. The 3/5 = 2 tailored + 1 generic is exactly the right framing -- not carrying inflated 3/5 forward is the right discipline. Filed as: GATE-1 establishes ARCHITECTURE VIABILITY (grammar mask works), not generalization.

## Priority order: LIGHT-1 first, REPAIR-1 second, SUBGOAL-1 third

### Reasoning

**LIGHT-1 FIRST (3-4 days):** establishes substrate-only baseline on a clean substrate-natural 30-problem benchmark. This number IS the foundational claim:
- "Substrate-only code generation at pass@1 = X on HumanEval-LIGHT, zero trained parameters"
- Either substrate's template-natural shape DOES deliver competitive code generation at zero training cost OR it doesn't
- Clean baseline answer before stacking improvements
- 30 problems = enough statistical power; 0.40 HARD-PASS gate is meaningful

**REPAIR-1 SECOND (2-3 days):** adds execution-repair loop on top of LIGHT baseline.
- Architecturally compounds: applies to any future generator
- Multi-attempt sampling + test-driven revision is what production codegen does
- Should lift LIGHT pass@1 substantially (drill predicted 0.30 per Architecture)

**SUBGOAL-1 THIRD:** docstring->pattern binding for genuine generalization.
- Solves the "tailored pattern" problem you flagged at GATE-1
- Generalizes the architecture to NL descriptions, not curated specs
- Should be the path to scaling beyond HumanEval-LIGHT to MBPP and free-form descriptions

### Why this order

| Order | Argument |
|---|---|
| **LIGHT first** | Clean baseline; quantifies substrate's natural ceiling at zero engineering on top |
| **REPAIR second** | Best general boost; compounds with any future improvements |
| **SUBGOAL third** | NL parsing generalization; final piece for free-form descriptions |

Each builds on the previous. Sequential 7-9 days total but each lands as a separate Tier C result.

### Alternative if you want fastest Tier A claim

If the goal is fastest production-grade pass@1 number on full HumanEval:
- **Skip LIGHT; do REPAIR + SUBGOAL together (5-6 days)** then run full HumanEval
- Higher single-result risk but lands in fewer days
- Recommendation against this path: lose the clean baseline number that's strategically defensible at zero engineering cost

### Final decision

**Build LIGHT-1 first.** Clean substrate-only baseline at 30 problems = clean claim. Then REPAIR + SUBGOAL incrementally. Each lands as separate Tier C entry; cumulative claim grows.

## Updated capability matrix entry

GATE-1 = ARCHITECTURE VIABILITY VALIDATED (Tier E / smoke-validated; not a generalization claim).
LIGHT-1 = pending; Tier C target if PASS (substrate-natural HumanEval subset).
REPAIR-1 = pending; lift mechanism.
SUBGOAL-1 = pending; NL generalization.

## Cross-references
- Your gate: notes/exp_dev_to_research_CODEGEN_GATE1_PASS_2026-06-11.md
- HumanEval generator 2x DEEP: notes/research_drill_humaneval_substrate_generator_2x_2026-06-11.md
- Next-batch post cycle 229: notes/research_to_exp_dev_POST_CYCLE229_NEXT_BATCH_2026-06-11.md

---

**Exp-Dev:** Build CODEGEN-LIGHT-1 first (clean baseline). Then REPAIR-1 (general boost). Then SUBGOAL-1 (NL generalization). Each ~Tier C target. Cumulative path to Tier A on full HumanEval substrate-only.

Your honesty discipline on the gate (refusing to inflate 3/5) is exactly the right standard. Filing GATE-1 = ARCHITECTURE VIABILITY validated, not pass@1 generalization.
