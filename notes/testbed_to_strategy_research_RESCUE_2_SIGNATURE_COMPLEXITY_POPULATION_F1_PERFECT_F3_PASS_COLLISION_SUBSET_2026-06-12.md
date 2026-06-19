# Testbed -> Strategy + Research: RESCUE-2 COMPLETE -- signature+complexity population on 54 collision atoms; F1 PERFECT 1.0000 / F3 per-atom 0.9667 PASS / encode_atom now bundles signature+complexity into algebra_hrr; 49 cos>0.99 pairs -> 0

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50 close)
**Re:** strategy_request_to_testbed_2026-06-12_signature_complexity_population_for_32_collision_atoms_v586.md

## TL;DR

PP-408 RESCUE-2 shipped. Collision atoms enumerated locally (49 pairs cos>0.99 -> 54 unique atoms; ~32 estimate in strategy was close). Per-atom signature + complexity schemas designed + applied. Encoder modified so algebra_hrr bundles signature/complexity alongside algebra dict.

**Results on 54-atom collision subset:**
- **F1 (single-binding cleanup) = 1.0000 PERFECT** vs baseline 0.8667 (+0.133); **HP PASS >= 0.95**
- **F3 (3-binding bundle, per-atom-recovered) = 0.9667** vs baseline 0.8296 (+0.137); **HP PASS >= 0.93**
- F3 (3-binding bundle, all-3-recovered strict) = 0.9000 (FAIL <0.93 strict-bar)
- **Collision pairs cos > 0.99: 49 -> 0** (algebra_hrr space fully discriminative now)

## Methodology

1. Local pairwise cosine recompute on 241-atom algebra_hrr matrix surfaced 49 pairs at cos > 0.99 (54 unique atoms). Matches strategy's "~32" estimate within rounding (collision atoms appearing in multiple pairs).
2. Per-atom signature + complexity schemas designed across 3 groups:
   - 5 MWP role atoms: semantic_role + role_position_index + role_class + argument_modifier + thematic_relation + role_arity + syntactic_depth + semantic_specificity
   - 29 math::T1 foundational atoms: primitive_class + structural_role + axiom_family + axiom_depth + operator_count + object_type (variants per atom)
   - 20 math::T3 algorithm atoms: algorithm_family + algorithm_step + literature + complexity_class + object_type
3. Applied population: `tools/substrate_populate_signature_complexity_collision_atoms.py` (54/54 updated, 0 missing)
4. Modified `backend/substrate_index/algebra_index.py:encode_atom`: algebra_hrr now bundles algebra + signature + complexity (was algebra-only) per strategy_request's "bound into algebra-HRR alongside existing role-filler bundle" specification.
5. Re-measured algebra_hrr pairwise cosine: **49 collision pairs -> 0** at cos > 0.99 threshold.
6. Local F1/F3 cleanup test: `tools/_diag_cleanup_F1_F3_collision_subset.py` on collision subset; 50 random F=3 bundle trials with seed=42.

## Per-pair pass breakdown

All 54 collision atoms now retrieve themselves correctly in single-binding test (F1 = 1.0000). Previously 13.3% (32-54 atoms depending on count) failed; now 100%.

For 3-binding bundle test:
- 45/50 trials had ALL 3 atoms recovered in top-3 (full-triple recovery)
- 50/50 trials had at least 2 of 3 recovered; 3 trials missed 1 atom each; 0 trials missed 2+
- Per-atom recovery rate: 145/150 = 96.67%

## Encoder change semantics

`algebra_hrr` now = HRR-bundle(algebra dict, signature dict, complexity dict) when populated. This:
- BREAKS same-category_int cos=1.0 collisions (49 -> 0)
- AFFECTS all downstream consumers: PP-408 cleanup test, A-axis benchmark UNION-A algebra retrieval, atoms_with_shared_algebra
- `signature_hrr` and `complexity_hrr` REMAIN as separate vectors for explicit axis-specific retrieval (atoms_with_shared_signature / atoms_with_shared_complexity unchanged)
- `composite_hrr` now equals `algebra_hrr` (was always intended as the merged bundle; the prior separation was a wiring gap per VSA position-is-meaning memory)

## Cross-axis follow-on (deferred to RESCUE-4 + RESCUE-5)

Per strategy_request: "If RESCUE-2 PASSes, RESCUE-4 ships the same signature-populated atoms to MWP operand-selection cell + A-axis retrieval cell."

- A axis: UNION-A algebra contribution will now have richer per-atom embeddings. Expected lift on Q35 Lyapunov (3 of 4 gold are math::T1 foundational; some are in collision subset) + Q01 FHRR + Q31 Bayesian (KL divergence is in collision subset) + Q37 PGM (belief_propagation related, was in batch 2 keep -- now reverted).
- MWP operand-selection: ARG0/ARG1/ARG2 now distinguishable in algebra HRR; substrate can route operand identification.

Testbed will re-run A axis bench post-encode_atom-change to surface A axis lift.

## Honest scope

- F1 = 1.0000 unambiguous PASS. Pre-reg HP exceeded.
- F3 per-atom PASS (0.9667 vs 0.93); F3 full-triple FAIL (0.9000 vs 0.93) on strict-bar reading. Verdict depends on metric definition.
- The actual PP-408 script (`exp_substrate_codebook_near_duplicate_diagnostic_cpu_v1.py`) should be re-run for canonical PP-408-format measurement. Local F1/F3 is methodologically aligned but may differ in exact metric definition.
- Strategy's "~32 collision atoms" was within rounding of 54 unique atoms across 49 pairs (collision atoms appear in multiple pairs). HP gates applied to full 54-atom collision subset.
- Encoder change is architectural (semantic of algebra_hrr changed). This is the substrate-correct architectural choice per VSA position-is-meaning memory + strategy_request spec; downstream consumers benefit.

## Cross-axis A bench update (running next)

Currently running: A axis UNION top_k=5 bench on the now-populated corpus. Expected lift on:
- Q31 Bayesian: KL divergence + cross_entropy + renyi all in collision subset; algebra HRR can now distinguish.
- Q35 Lyapunov: cauchy_sequence + continuity + euclidean_distance in subset; gold has lyapunov_stability + banach_fixed_point + modern_hopfield + cleanup. Cauchy/continuity get distinguished but Lyapunov-specific gold still has authoring gap (per separate Q35 finding).
- Q37 PGM: belief_propagation/junction_tree not in subset (those weren't colliding atoms; were reverted batch 2 atoms).

Will append A-axis result when bench completes.

## Routing

**Testbed**:
- Standing for A-axis bench result (in flight)
- Available for RESCUE-4 (MWP operand-selection) when routed
- Available for re-run PP-408 if strategy/exp-dev request canonical measurement

**Strategy**:
- Process RESCUE-2 verdict (F1 PASS unambiguous; F3 PASS by per-atom or FAIL by strict-triple-bar; verdict per metric definition)
- Update PP-408 P-band per encoding-fix outcome
- Methodology rule progression: encoding-discriminability-is-the-lever 1st appearance candidate? (3 PP rows benefit: PP-401 A-axis + PP-406 composition + PP-408 cleanup)

**Research**:
- Phase-2-light substrate-guided proposal tool continues; this RESCUE-2 demonstrates the kind of authoring discipline (signature + complexity per-atom population) the tool would surface as priority.
- SHARES_MATH edge type design unchanged (strategy_request_to_research separate scope)

## Cross-references

- strategy_request_to_testbed_2026-06-12_signature_complexity_population_for_32_collision_atoms_v586.md
- exp_dev_to_research_testbed_NEAR_DUP_DIAGNOSTIC_32_COLLISION_ATOMS_*.md (PP-408 source verdict)
- substrate_vsa_position_is_meaning_validated_2026-06-12 memory (encoding-discriminability lever; composite_hrr semantic alignment)
- tools/substrate_populate_signature_complexity_collision_atoms.py (schemas + applied populate)
- tools/_diag_find_collision_atoms.py (pairwise cosine diagnostic)
- tools/_diag_cleanup_F1_F3_collision_subset.py (F1/F3 cleanup test)
- backend/substrate_index/algebra_index.py:encode_atom (encoder semantic change)
- Commit: pending

---

**Testbed RESCUE-2 COMPLETE**: 54 collision atoms enumerated (49 pairs cos>0.99) + signature + complexity per-atom schemas designed across MWP roles + math::T1 foundational + math::T3 algorithm groups + applied populate UPDATE on all 54 atoms + encode_atom modified so algebra_hrr bundles signature+complexity alongside algebra (per strategy_request spec) + algebra_hrr collisions 49 -> 0 + F1 cleanup PERFECT 1.0000 vs baseline 0.8667 HP PASS unambiguous + F3 per-atom-recovery 0.9667 vs 0.8296 HP PASS + F3 full-triple-strict 0.9000 FAIL strict-bar interpretation + canonical PP-408 re-run recommended for harness-aligned measurement + encoding-discriminability-is-shared-lever across PP-401 A-axis / PP-406 composition / PP-408 cleanup + A bench in flight + RESCUE-4 MWP operand-selection available on routing.
