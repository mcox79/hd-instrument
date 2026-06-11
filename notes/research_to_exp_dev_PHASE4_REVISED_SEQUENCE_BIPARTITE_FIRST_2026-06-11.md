# Research -> Exp-Dev: REVISED Phase 4 sequence -- bipartite-matching FIRST, dep-parser FALLBACK

**From:** Research  **Date:** 2026-06-11 evening
**Re:** 2x drill on phase4_math role-binding REFUTES dep-parser-needed conclusion

## Drill finding (literature refutes my prior recommendation)

2x DEEP drill on math word-problem role-binding limiter returned 5-discipline convergence:
- NLP literature
- Cognitive neuroscience
- Cognitive science
- Biology
- Optimization theory

All 5 point to the same alternative: **bipartite-matching role-assigner with engineered cost matrix** (unit-cue + verb-frame + position + quantifier-adjacency). This is 2-3 days vs 3-4 day dep-parser, substrate-native (graph/optimization primitive), more empirically-grounded.

**Drill-defeatism rule applied to my own recommendation.** I committed to multi-day dep-parser based on architect intuition; literature shows there's a better substrate-native primitive I hadn't considered. Walking back the 4B-FULL ordering.

## Revised Phase 4 sequence

### 1st (TONIGHT, 2 hr): v2.5 confidence-gated MoE rescue
Already routed in research_to_exp_dev_PHASE4_V25_CONFIDENCE_GATED_RESCUE_2026-06-11.md. Substrate cleanup-margin as native gating signal. Decides whether confidence-gating alone lifts trajectory.

### 2nd (NEW PRIORITY, 2-3 days): Bipartite-matching role-assigner
Per drill convergence:
- Build bipartite graph: numerical-entities (left) -> schema-roles (right)
- Engineered cost matrix:
  - Unit-cue cost (mph -> RATE strong; $ -> PRICE strong)
  - Verb-frame cost (verb governance over arguments)
  - Position cost (sentence-position regularities)
  - Quantifier-adjacency cost (adjacent quantifier modifies)
- Solve via Hungarian / Jonker-Volgenant / Munkres assignment (polynomial-time exact)
- This is substrate-native: cost matrix entries can be substrate cleanup-margin scores; assignment is a graph primitive

Drill companion handoff: notes/exp_dev_handoff_research_phase4_math_role_binding_2026-06-11.md
Drill output: notes/research_drill_phase4_math_role_binding_2x_2026-06-11.md

### 3rd FALLBACK ONLY (3-4 days): Phase 4B-FULL dep-parser
Run ONLY if (1) AND (2) underperform. This is the original plan demoted to fallback.

## Decision matrix

| (1) v2.5 result | (2) Bipartite result | Implication |
|---|---|---|
| Lifts trajectory significantly | Lifts further | Phase 4B-FULL CANCELLED; ship v2.5 + bipartite as production substrate-only math solver |
| Lifts modestly | Lifts further | Phase 4B-FULL DEFERRED; ship v2.5 + bipartite as v1; consider 4B-FULL later if needed |
| Flat or worse | Lifts | Bipartite alone is the answer; ship it |
| Lifts | Flat or worse | v2.5 alone is the answer; consider 4B-FULL for bigger lift |
| Both underperform | | Phase 4B-FULL is empirically justified; proceed |

## Why this is the right ordering per drill-defeatism rule

1. v2.5 is 2hr (cheapest test) -> run first
2. Bipartite-matching is 2-3 days with literature-strong P_deflated=0.40 -> run second
3. Dep-parser is 3-4 days based on architect intuition -> only if cheaper alternatives fail
4. NO pre-registered defeat threshold for any phase
5. Substrate-only architecture preserved throughout (no LLM hybrid)

## Bonus: bipartite-matching is also CODE applicable

Same pattern: function-arguments (left) -> docstring-entities (right) bipartite assignment. Phase 4D for CODE is incremental (1-2 days) once bipartite works for MATH.

## Total budget savings

| Original plan | Revised plan |
|---|---|
| Phase 4B-FULL (3-4 days) -> Phase 4C (1 day) | v2.5 (2 hr) -> Bipartite (2-3 days) -> 4C (1 day) |
| 4-5 days | 3-4 days (or 0.3 days if v2.5 alone sufficient) |

**Up to 1-2 days saved if bipartite works.**

## Apologies for the back-and-forth

The Phase 4A+4B+4C and Phase 4B-FULL routings were architect-intuition-based, not literature-grounded. The drill returned the substrate-native alternative I should have considered first. Per drill-defeatism rule applied to my own work: walking back to literature-grounded sequence.

## Cross-references
- Drill output: notes/research_drill_phase4_math_role_binding_2x_2026-06-11.md
- Drill exp_dev handoff: notes/exp_dev_handoff_research_phase4_math_role_binding_2026-06-11.md
- v2.5 confidence-gated rescue: notes/research_to_exp_dev_PHASE4_V25_CONFIDENCE_GATED_RESCUE_2026-06-11.md
- Original Phase 4B-FULL (now demoted): notes/research_to_exp_dev_PHASE_4B_FULL_WEAK_SUPERVISION_CONFIRMED_2026-06-11.md
- Original Phase 4A+4B+4C: notes/research_to_exp_dev_PHASE_4A_4B_4C_BUILD_2026-06-11.md

---

**Exp-Dev:** REVISED Phase 4 sequence. (1) v2.5 confidence-gated rescue 2hr [already routed]. (2) Bipartite-matching role-assigner 2-3 days [NEW PRIORITY per drill]. (3) Phase 4B-FULL dep-parser DEMOTED to FALLBACK. Literature 5-discipline convergence refutes dep-parser-needed conclusion; bipartite-matching is substrate-native alternative. Up to 1-2 days saved.
