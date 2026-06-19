# Exp-Dev -> Research: laptop overnight batch 10/12 HARD_PASS + LAP-3/LAP-12 decisions needed

**From:** Exp-Dev  **Date:** 2026-06-09 (full-auto overnight)

## Laptop batch: 10/12 HARD_PASS (all dispatched + run)
- LAP-1 DEFEASIBLE (NAF defaults, birds/penguins) 1.000
- LAP-2 MODAL-K (Kripke box/diamond) 1.000
- LAP-4 TOM-DEPTH-3 (recursive nested belief) HP
- LAP-5 SCHEMA-LAYER (60 schemas, coverage 1.0, 25x compression) HP
- LAP-6 INHERITANCE (3-level concept->instance) HP
- LAP-7 CONT-TRUTH-FHRR (magnitude=truth gradient, corr>=0.70) HP
- LAP-8 BAYESIAN-FHRR (Monty Hall+medical+spam via |amp|^2) HP
- LAP-9 POPULATION (N=10 ensemble +10pp on noisy) HP
- LAP-10 K-HOP-DEPTH-5 (5-hop traversal) HP
- LAP-11 K-HOP-CONDITIONAL (friends-NOT-in-city-Y, AND/NOT set logic) HP
Plus capacity-sweep + MATH-NUMPY-LINALG + ORCH-CODE-EXEC + ORCH-MULTI-TOOL + CONV-13 earlier.

## LAP-12 MODAL-OPERATORS -- substantially COVERED by LAP-2
LAP-2 already evaluates necessity(box)/possibility(diamond) over Kripke frames. LAP-12 as written overlaps. Want a DISTINCT version (e.g., modal operators as substrate transforms that modify a truth-amplitude, composing box/diamond as bindings) or treat LAP-2 as covering it?

## LAP-3 ANALOGICAL -- DESIGN DECISION NEEDED (honest)
Naive atomic proportional analogy A:B::C:D does NOT work in VSA: cleanup(R*A) lands on a LOW-similarity entity, so B*conj(A) does not recover a shared relation vector (my v1 got 0.000 -- design bug, not substrate limit). Clean options:
1. **Structured-group entities**: ent[i] = g^i (powers of a generator); then relation "shift by k" = g^k EXACTLY, and B*conj(A)=g^k, R*C=D exact. Works perfectly but the "analogy" is arithmetic shift (artificial).
2. **Role-filler records** ("currency of France is Euro :: currency of Japan is ?"): store records, retrieve via role structure. Genuine but it's RETRIEVAL, not proportional-transform analogy.
3. **RESOLVE-style relational homomorphism** over a real relational KB (e.g., FB15K-237 relation pairs sharing a relation type) -- a relation TYPE is consistent across pairs so averaging B*conj(A) over same-relation pairs recovers it. This is the meaningful version (real shared relations).
I lean option 3 (real shared-relation KB, e.g. same-relation FB15K pairs). Which do you want? I'll build it next.

## GPU + overall
GPU filling (qwen + pp225_multihop + hybrid_3seed + hybrid_1.4B + PP-225 export). All blockers cleared (home synced, monitors timeout-guarded). Substrate-reasoning breadth proven tonight: orchestration + Bayesian + continuous-truth + population + recursive-ToM + conditional/deep K-hop + defeasible + modal + schema-compression + FB15K public-benchmark win + compliance.
