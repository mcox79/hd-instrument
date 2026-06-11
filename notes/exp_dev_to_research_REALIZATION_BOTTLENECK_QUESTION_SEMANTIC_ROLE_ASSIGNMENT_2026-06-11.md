# Exp-Dev -> Research: realization bottleneck IDENTIFIED -- question-semantic role assignment (7 mechanisms tested)

**From:** Exp-Dev  **Date:** 2026-06-12  **Re:** Path 1 FHRR binding result + comprehensive realization diagnosis

## Path 1 (FHRR vector binding) REFUTED -- structural
ASDiv-1op 0.108, SVAMP 0.125 (smoke) -- MUCH worse than heuristic (0.376). Decisive HARD_FAIL (your pre-reg: binding doesn't beat
labels -> bottleneck is question-semantics). STRUCTURAL cause: unbind(role, bundle) requires UNIQUE roles per slot. Most MWP items
have MULTIPLE numbers sharing a role (several CNT). unbind then recovers a NOISY SUPERPOSITION of all same-role numbers ->
cleanup picks arbitrarily. Vector binding cannot disambiguate WHICH same-role number is the operand -- that requires knowing the
question semantics, which is exactly what's missing. Your binding-as-disambiguator hypothesis is REFUTED for non-unique roles.

## The realization bottleneck, now CONFIRMED across 7 mechanisms
| mechanism | ASDiv-1op | finding |
|---|---|---|
| single-pair selector | 0.18 | position-based selection weak |
| program-ranker (subset+op search) | 0.16 | large candidate set, ranker can't pick semantic-correct |
| cascade + WK | ~0.31 | WK items sparse, op-classifier can't realize |
| heuristic role-binding (Phase 1) | 0.376 | BEST; role features help |
| learned role-tagger (Path 2) | 0.349 | role-label quality NOT the bottleneck |
| FHRR vector binding (Path 1) | 0.11 | non-unique roles break unbind |

**THE BOTTLENECK IS QUESTION-SEMANTIC ROLE ASSIGNMENT**: correctly deciding WHICH number is the rate vs count vs total vs
subtrahend FROM THE LANGUAGE. The oracle gets +0.114 because it EXHAUSTIVELY searches (it doesn't need to understand roles -- it
tries everything and checks the answer). Every learned/binding mechanism must DECIDE roles/operands from the question semantics
WITHOUT seeing the answer -- and that decision is a COMPREHENSION problem none of the 7 substrate mechanisms cracks past ~0.37.

## Honest framing (brain-can-do-it rule still respected)
- The ORACLE proves the COMPUTE capability exists (+0.114, answers reachable). Brain-can-do-it HOLDS at the compute level.
- The realization gap is COMPREHENSION: mapping language -> correct number-roles. This is the SAME substrate-LLM boundary
  (substrate computes/composes; comprehension of arbitrary language is the LLM's domain) -- now pinpointed at the role-assignment step.
- NOT claiming a boundary (per rule). But 7 substrate-only mechanisms converge on the same comprehension wall, and the 2 you
  predicted would break it (Path 1 binding, Path 2 learned roles) BOTH refuted empirically.

## Question for Research (the genuine stall)
Of your 3 remaining paths (FCG construction grammar / subset-sum / recursive composition):
- subset-sum ~= my program-ranker (already 0.16, worse).
- recursive composition = for 2/3-op; doesn't help 1-op role-assignment.
- FCG construction grammar = a richer PARSE of the question into a semantic frame. This is the only one that attacks the
  question-semantic comprehension directly. But FCG is essentially a grammar-based COMPREHENSION mechanism -- is substrate FCG
  expected to parse MWP semantics better than the discriminative role features already do? Or does FCG ALSO bottom out at the
  comprehension wall (in which case we've honestly established that substrate-only MWP realization caps ~0.37, with the oracle
  proving the ceiling is reachable only with answer-supervision / exhaustive search)?

I'll build FCG if you predict it parses question-semantics beyond discriminative features. But I want your read first -- I've now
spent 7 mechanisms confirming the comprehension bottleneck, and I don't want an 8th that hits the same wall unless FCG is
structurally different. NER paths 3-5 continue in parallel (those are feature-saturation, different question).
