# Pre-registration: wave14yw_polysemy_shared_subj

Date: 2026-05-21
Status: Pre-registered, gated
Priority: substrate polysemy test - does (A, R) -> {B, C} disambiguate?
Author: experiment_dev session, pipeline tick 30

## Why
Real-world facts have polysemy: "Paris" can be capital-of(France) OR
person-named. Store (A, R, B) and (A, R, C) for same (A, R), different obj.
What does query (A, R) return?

Substrate math: M = sign(...sum of all triples...) contains
sign(A*R*B + A*R*C + others) = sign(A*R*(B+C) + others). For random B, C,
B+C zeros out half of bits, so M*A*R is a "mixed" vector of B and C.

Tests: does the substrate consistently choose one (deterministic disambiguation)
or return noise?

## Verdict labels
- POLYSEMY_PICKS_ONE_CONSISTENTLY: returns one of {B, C} > 0.85 of the time AND consistently the same
- POLYSEMY_PICKS_ONE_NONDET: returns one of {B, C} consistently but inconsistent which
- POLYSEMY_RETURNS_NOISE: returns NEITHER > 0.50 of the time
- POLYSEMY_INCONCLUSIVE

## Operational definition
- M with 30 polysemous pairs + 70 distractor facts
- Query each pair, record argmax_idx, check if = B, = C, or other

## Runtime: ~1-2 min
