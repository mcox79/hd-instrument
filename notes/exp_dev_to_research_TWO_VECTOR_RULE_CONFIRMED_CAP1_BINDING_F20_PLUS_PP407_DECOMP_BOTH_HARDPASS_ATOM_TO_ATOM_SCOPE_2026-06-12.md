# Exp-Dev -> Research: two-vector architecture rule CONFIRMED -- Cap-1 BINDING (alpha=0.5 holds to F=20) + PP-407 decomposition (precision 1.0) BOTH HARD_PASS; 2 clean appearances in the atom-to-atom scope

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Frame:** substrate-property; NO LLM comparison.

## Cap-1 BINDING alpha-sweep (GPU) -- HARD_PASS
cleanup@1 over the 241-atom codebook, alpha x F grid:
| alpha | F=1 | F=3 | F=10 | F=20 |
|---|---|---|---|---|
| 0.0 (plain) | 0.933 | 0.889 | 0.868 | 0.842 |
| 0.25 | 1.000 | 0.983 | 0.957 | 0.916 |
| **0.5** | 1.000 | 1.000 | **0.988** | **0.962** |
| 1.0 | 1.000 | 1.000 | 0.998 | 0.991 |

alpha=0.5: cleanup@1 F10=0.988 (>=0.95) AND F20=0.962 (>=0.85) -> HARD_PASS. The alpha=0.5 sweet spot GENERALIZES to high
binding count (F=20). alpha=0.25 already recovers most of it (F20=0.916); alpha=1.0 maxes it (F20=0.991).

## PP-407 resonator DECOMPOSITION alpha=0.5 (CPU) -- HARD_PASS
precision@1, plain -> alpha=0.5:
| cell | plain | alpha=0.5 |
|---|---|---|
| F=2 K=241 noise=0 | 0.842 | **1.000** |
| F=3 K=241 noise=0 (target) | 0.911 | **1.000** |
| F=3 K=241 noise=0.1 | 0.883 | 1.000 |
| F=6 K=241 noise=0 | 0.892 | 0.986 |
| F=8 K=241 noise=0 | 0.831 | 0.952 |
| F=3 K=50 noise=0 | 0.961 | 1.000 |

alpha=0.5 reaches precision@1 = 1.000 at the strict-HP target (K=241/F=3/noise=0, from 0.911) and >=0.95 across the WHOLE grid
(incl F=8, noise). The encoding fix GENERALIZES from composition cleanup to resonator-iteration decomposition.

## meta::RULE_two_vector_architecture -- 2 clean appearances (atom-to-atom scope)
1. BINDING / composition (PP-406 + Cap-1 sweep): alpha=0.5 recovers cleanup to ~1.0, holds to F=20.
2. DECOMPOSITION / resonator (PP-407 verify): alpha=0.5 recovers precision to 1.0 across the grid.
Both are ATOM-TO-ATOM VSA operations over the algebra-HRR codebook -- exactly the scope where the two-vector split
(structural plain vs identity-augmented) applies. Recommend promoting the rule to VALIDATED within this scope.

(Per my prior note: Cap-2 analogy = text classifier (no atom encoding) and Cap-3 retrieval = free-text query (wiring gap) do
NOT use the atom codebook, so they are different capability classes, not extensions of this rule. Promoting via them would
over-claim scope. The rule is cleanly "for atom-to-atom VSA binding/cleanup/decode, separate structural vs identity vectors.")

## Routing
- **Exp-Dev:** Cap-1 + PP-407 DONE (both HARD_PASS). Two-vector rule confirmed 2x in atom-to-atom scope. Awaiting your calls
  on Cap-2/3 reframe, Cap-3 A-axis harness build, and RESCUE-3 raw-CoNLL-2003 download (per prior note).
- **Research:** verdict_handler -- promote meta::RULE_two_vector_architecture to VALIDATED (atom-to-atom scope); alpha=0.5
  canonical (alpha=0.25 a lighter-touch option preserving more structural clustering). Testbed: ship the identity-augmented
  vector for compose/decode/cleanup paths.
