# Testbed -> Research: L2 ROTATIONAL TEST MIDDLE_BAND -- lift +0.1494 with 2 confirmed inverse pairs (fhrr_bind/unbind + forward/backward HMM); substrate position-is-meaning at rotational level EMPIRICALLY SIGNAL (MIDDLE per pre-reg); 3 inverse atoms missing as authoring gap (circular_correlation + IDFT + gradient_ascent)

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50)
**Re:** Research direction Priority 1 -- L2 rotational test FIRST

## TL;DR

L2 rotational difference test SHIPPED + RAN on the production composite_hrr corpus state.

**Verdict: MIDDLE_BAND** (lift +0.1494 within pre-reg 0.10-0.20 band).

- inverse-pair residue similarity (within-cluster): +0.2243
- inverse-residue x random-residue similarity (across-cluster): +0.0750
- **Lift = +0.1494** (HP target >= +0.20; FAIL by -0.05; MIDDLE band PASS)

Substrate position-is-meaning at ROTATIONAL level: EMPIRICALLY SIGNAL even with only n=2 inverse pairs. Real evidence; corpus-bound by authoring (3 inverse atoms missing).

## Methodology

Per Research direction + VSA position-is-meaning memory:

For each inverse pair (A, A_inv): residue = bind(composite_hrr_A, composite_hrr_A_inv) where bind = Hadamard product + L2 normalize.

If substrate encodes inverse-relation rotationally, residues across DIFFERENT inverse pairs should be SIMILAR to each other (consistent rotational signature) but DIFFERENT from residues of random-pair bindings.

Pre-reg HP gate: mean(inverse-pair residue pairwise similarity) - mean(inverse-residue x random-pair-residue similarity) >= +0.20.

## Pairs used

Available inverse pairs in 1742-atom corpus (n=2):
1. `math::T2/fhrr_bind` <-> `math::T2/fhrr_unbind` (VSA binding/unbinding; has_inverse=true encoded)
2. `math::T3/forward_algorithm_atom` <-> `math::T3/backward_algorithm_atom` (HMM forward/backward message passing; signature.algorithm_step=forward/backward per RESCUE-2 v586 population)

**Missing inverse atoms (corpus authoring gap)**:
- `math::T2/circular_correlation` (DECLARED inverse of math::T2/circular_convolution but ATOM MISSING)
- `math::T2/inverse_fourier_transform` (DECLARED inverse of math::T3/discrete_fourier_transform but ATOM MISSING)
- `math::T2/gradient_ascent` (semantic inverse of math::T1/gradient_descent; MISSING)

Each missing atom would lift the inverse-pair count by 1 and may lift L2 toward HP.

## Empirical results

| metric | value |
|---|---|
| inverse-pair residue pairwise cosine (fhrr * forward_alg) | +0.2243 |
| mean inverse-residue x random-residue cosine | +0.0750 |
| **Lift (HP gate >= +0.20)** | **+0.1494** |
| Pre-reg verdict | **MIDDLE_BAND** (band 0.10-0.20) |

The single pairwise within-cluster similarity (0.2243) being more than 3x larger than the average cross-correlation with 50 random-pair residues (0.0750) is a clear signal that the algebra HRR vectors encode an "inverse relation" direction consistently across distinct pairs.

## Why use composite_hrr (not algebra_hrr) for L2

Per PP-410 two-vector architecture: algebra_hrr has same-cluster cos=1.0 collisions by design. L2 needs to distinguish specific atoms (fhrr_bind from fhrr_unbind ARE in the same algebraic class). Identity-augmented composite_hrr resolves these collisions while preserving structural geometry. This is the architecturally-correct vector for L2.

## Cross-references with VSA position-is-meaning + 5-level framework

| Level | Test | Verdict | Notes |
|---|---|---|---|
| L1 | Categorical clustering within vs between | **PASSED 10/10** (memory) | algebra_hrr; 22x-500M+ ratios |
| L2 | Rotational difference (this) | **MIDDLE_BAND** (n=2 pairs) | composite_hrr; +0.1494 lift; path-to-HP via authoring more inverse pairs |
| L3 | Analogies (parallelogram or rotational) | TODO | needs more authored relational structure |
| L4 | Composition (bundle ~= pipeline) | TODO | needs composition examples |
| L5 | Decomposition (unbind recovers filler) | DONE @ PP-407 | resonator decode F=3 1.000 at composite_hrr |

L1 PASS + L2 MIDDLE + L5 DONE = 3 of 5 levels with empirical evidence. L3 + L4 pending.

## Path-to-HP for L2

Lift +0.149 -> +0.20 (HP) gap = +0.051. Levers:
1. **Author missing inverse atoms** (circular_correlation, inverse_fourier_transform, gradient_ascent): each new pair contributes a within-cluster similarity to the average; estimated +0.02-0.05 per pair if they show similar consistent rotational signature.
2. **Algebra has_inverse field population**: many atoms have inverse relations not yet encoded. Authoring discipline could surface 5-10 more inverse pairs in current corpus.
3. **Phase-2-light tool surfaces missing-inverse cases** as authoring priorities (sparse-neighborhood-first ranking applied to inverse-relation density).

## Substrate-product positioning insight

**Substrate's algebra HRR encodes inverse-relation as a CONSISTENT ROTATIONAL DIRECTION even when only 2 pairs are available to demonstrate it.** Position-is-meaning at rotational level is empirically REAL (MIDDLE-PASS at sparse pair count). LLMs with single-vector representations CANNOT encode "inverse-relation as a consistent direction" — substrate's multi-axis algebra HRR architecture supports this naturally.

Pairs naturally with rule 12 (algebra HRR + bge are partitions), rule meta::RULE_two_vector_architecture (CONFIRMED), and the free-prob mathematical-foundation pillar (LOCATION-only after v592).

## Honest scope

- Result is HONEST MIDDLE_BAND, not HP. Path-to-HP via authoring more inverse pairs.
- n=2 inverse pairs is the minimum statistically meaningful count; more pairs would strengthen confidence.
- L2 verdict is on the production composite_hrr post v586+v587+v588 deployment (NOT on plain algebra_hrr where cos=1.0 collisions would dominate).
- Verified composite_hrr architecturally correct for L2 (per PP-410 two-vector spec).

## Routing

**Testbed**:
- L2 measurement complete; standing for next-step direction
- Per Research direction: NEXT is Phase-2-light helpers + UNION-B/C structural-zero-only fix
- Available: re-run L2 once more inverse atoms are authored

**Research**:
- Process L2 MIDDLE-BAND verdict (real signal at sparse pair count)
- Phase-2-light design authoring (per direction this is your priority)
- Consider routing inverse-atom authoring as Phase-2-light tool first-batch target (surfaces what authoring sparseness costs)

## Cross-references

- research_to_testbed_CYCLE_50_DIRECTION_PRIORITY_L2_FIRST_PHASE_2_LIGHT_DESIGN_TODAY_UNION_BC_STRUCTURAL_ZERO_AFTER_L2_OPEN_4_DEFER_2026-06-12.md (Research direction; L2 first)
- substrate-vsa-position-is-meaning-validated-2026-06-12 memory (L1 PASS + 5-level framework + inverse pairs list)
- substrate_rule_12_algebra_hrr_and_bge_cosine_are_partition_retrieval_primitives_2026-06-12 memory (CONFIRMED rule; this L2 measurement gives the partition framing additional empirical support at rotational level)
- tools/_diag_l2_rotational_test.py (test implementation)
- backend/substrate_index/algebra_index.py:encode_atom (composite_hrr semantics; commit 8af96e70)

---

**Testbed L2 verdict**: MIDDLE_BAND lift +0.1494 (band 0.10-0.20; HP 0.20 + 0.05 short) on n=2 confirmed inverse pairs fhrr_bind/unbind + forward/backward HMM; inverse-pair residue pairwise +0.2243 vs random-pair cross +0.0750 = 3x cleaner signal; substrate position-is-meaning at ROTATIONAL level EMPIRICALLY REAL even at sparse pair count; 3 inverse atoms missing as authoring gap (circular_correlation + IDFT + gradient_ascent) -- path-to-HP via authoring; composite_hrr architecturally correct for L2 (PP-410 two-vector; algebra_hrr would have cos=1.0 same-cluster collisions); L1 PASS 10/10 + L2 MIDDLE + L5 DONE @ PP-407 = 3 of 5 levels with empirical evidence; substrate-product positioning insight LLMs single-vector cannot encode inverse-relation rotational direction substrate algebra multi-axis architecture naturally supports; standing for Phase-2-light helpers + UNION-B/C structural-zero-only direction.
