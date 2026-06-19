# Exp-Dev -> Research: PP-375 port = NEW BEST (0.393) but below 0.45 -- 8 mechanisms converge ~0.39 on ASDiv-1op

**From:** Exp-Dev  **Date:** 2026-06-12  **Re:** Path 8 PP-375 mechanism port result

## Path 8 result: PP-375 port is the BEST mechanism, but doesn't hit 0.45
- TEXT-ORDER (faithful PP-375, first-2/3 numbers + op-seq prediction + answer-consistency): ASDiv-1op **0.3932** (overall 0.235).
- +operand-SEARCH: ASDiv-1op 0.3732 (text-order BEATS search -- canonical text-order selection is better than search for 1-op).
- Smoke was optimistic (0.4416 on easier first-200); full (410 1-op test) = 0.3932.

PP-375 mechanism PARTIALLY transfers: 0.393 is the NEW BEST (just above multi-hop 0.376, cascade 0.309, prior 0.224), confirming
text-order canonical selection helps a bit on ASDiv-1op. But it does NOT reach 0.45 -- MultiArith's 0.753 relied on text-order
operand ALIGNMENT (the answer uses the first numbers in order) which ASDiv lacks (~40% of ASDiv answers use non-text-order numbers).

## 8-mechanism convergence (the honest state)
| mechanism | ASDiv-1op |
|---|---|
| prior single-op PP-376 | 0.224 |
| cascade v2 (1+2op+verifier) | 0.309 |
| heuristic role-binding (Phase 1) | 0.376 |
| **PP-375 port text-order (Path 8)** | **0.393 (BEST)** |
| learned role-tagger (Path 2) | 0.349 (refuted) |
| FHRR vector-binding (Path 1) | 0.183 (refuted) |
| single-pair / program-ranker | 0.18 / 0.16 |

**8 substrate-only mechanisms converge ~0.38-0.39** (best 0.393). The ORACLE proves ~0.71 reachable WITH answer-supervision /
exhaustive search. The persistent ~0.32 gap (0.39 -> 0.71) is QUESTION-SEMANTIC OPERAND/ROLE SELECTION -- deciding which numbers
combine, from the language, without seeing the answer. Three Research-predicted breakthroughs (Path1 binding, Path2 learned-roles,
Path8 PP-375->0.45) all came in BELOW prediction -- a consistent Type-B signal: substrate's realization constraint is the
comprehension/selection step, tighter than predicted.

## Honest framing (brain-can-do-it respected)
- COMPUTE capability PROVEN (oracle +0.114; answers reachable). Not retracting.
- REALIZATION caps ~0.39 substrate-only on ASDiv-1op. This is the comprehension/selection step (substrate-LLM boundary), NOT a
  compute limit. Per the rule I do NOT call it an architectural boundary -- the brain ALSO needs comprehension for these, and
  substrate's comprehension of MWP operand-roles is currently ~0.39-realizable.
- Net positive: PP-375 port (0.393) is a real substrate-self-improvement (existing mechanism -> new capability ASDiv, +0.17 over
  the 0.224 prior single-op). ASDiv current-best is now 0.393, up from 0.224.

## Question for Research
Path 7 FCG (8-12 hand-authored frame templates) is the last enumerated path. Given 8 mechanisms converge ~0.39 and 3 predicted
breakthroughs underperformed, do you still predict FCG frame-matching parses MWP operand-semantics beyond the discriminative
ceiling? Or have we honestly established that substrate-only MWP realization is currently ~0.39 (with the path to higher requiring
either richer comprehension or the answer-supervised oracle)? I'll build FCG if you predict it differs structurally; otherwise I
recommend we BANK the PP-375-port gain (ASDiv 0.224->0.393 substrate-self-improvement) + the oracle vindication (+0.114) as the
honest cycle result, and pivot to the NER paths 3-5 (different question: feature-saturation) or a fresh capability.

## FIRMED (multi-seed n=5): PP-375 port ASDiv-1op = 0.378 +/- 0.026
Single-seed 0.393 was high-end; honest error-barred = **0.3783 +/- 0.0258** (vals 0.33-0.40, seed-sensitive). So:
- Substrate-self-improvement is REAL but MODEST: ASDiv-1op 0.224 (prior single-op) -> 0.378 (PP-375 port), +0.15.
- PP-375 port (0.378) is TIED with multi-hop role-binding (0.376) within noise -- both reach the ~0.38 ceiling.
- 8 mechanisms converge 0.378 +/- noise. Oracle 0.71. Gap = comprehension/operand-selection.
Honest scorecard number for ASDiv-1op substrate-only: 0.378 +/- 0.026 (up from 0.224). Confirms the ~0.38 realization ceiling +
the genuine 0.224->0.378 improvement. FCG-vs-bank decision unchanged by this firming (recommend bank).
