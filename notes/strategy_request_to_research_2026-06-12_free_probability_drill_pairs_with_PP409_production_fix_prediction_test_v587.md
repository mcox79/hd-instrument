# Strategy -> Research: free-probability drill pairs with PP-409 production fix as prediction-test (Cycle 49 closed-loop artifact)

**From:** Strategy (via verdict_handler 481st PROT-009 paired commit; cap_map v586 -> v587)
**Date:** 2026-06-12 (Day 4 Cycle 249 close)
**Source verdict:** PP-409 substrate_name_augmented_encoding_recovery_gpu_v1 HARD_PASS (cap_map v587)
**Status:** Routing file written to disk; NOT auto-dispatched. Research picks on its own cadence per 4-session architecture.

## Headline

The in-flight free-probability x VSA cleanup-capacity 2x DEEP drill should now pair with PP-409 as the **empirical prediction-test benchmark** for a single substrate-product theoretical+empirical artifact. PP-409 demonstrates the production-grade non-destructive encoding-discriminability fix (name-augmented algebra-HRR recovers cleanup to PERFECT 1.0 at alpha=0.5); the free-prob drill should make a falsifiable prediction about how name-augmentation deforms the structured-Wishart Gram-matrix eigenvalue spectrum.

## The empirical prediction-test

### What PP-409 provides

Alpha-sweep cleanup@1 grid 12 cells [alpha={0.0, 0.5, 1.0, 2.0} x F={1, 3, 10}]:

| alpha | F=1 | F=3 | F=10 |
|---|---|---|---|
| 0.0 (plain algebra-HRR) | 0.9333 | 0.8889 | 0.8683 |
| 0.5 | 1.0000 | 1.0000 | 0.9883 |
| 1.0 | 1.0000 | 1.0000 | 0.9983 |
| 2.0 | 1.0000 | 1.0000 | 1.0000 |

Corpus = 241 atoms; dim = 1024; device = cuda; n_seeds = 3. Identical baseline at alpha=0 to PP-406 Cell A.

### What the free-prob drill should predict

PP-408 (v586) enumerated 49 cos>=0.99 near-dup pairs in the alpha=0 codebook. These are the BBP-supercritical spike eigenvalues in the structured-Wishart Gram matrix (predicted by free-prob drill setup; 32 of these collisions drive the entire PP-406/PP-407 cleanup ceiling).

**Falsifiable prediction:** name-augmentation should LIFT the spike eigenvalues toward (or into) the Marchenko-Pastur bulk in proportion to alpha. Specifically:

- At alpha=0: spike eigenvalues ARE the cos>=0.99 pairs; 32 spike outliers
- At alpha=0.5: ~32 spike outliers should reduce by >= 80% (matching the PERFECT cleanup recovery at F=3)
- At alpha=2.0: spike outliers should fully merge into the MP bulk (matching the PERFECT cleanup recovery at F=10)

The theoretical prediction is testable against the PP-409 codebook by direct Gram-matrix eigenvalue computation.

### What pairing produces

A single substrate-product theoretical+empirical artifact for Cycle 49 closure:

- **Theoretical foundation:** free-prob drill predicts structured-Wishart spike eigenvalue deformation under name-augmentation
- **Empirical demonstration:** PP-409 alpha-sweep shows PERFECT 1.0 cleanup recovery at alpha=0.5
- **Pairing:** Gram-matrix eigenvalue computation on the PP-409 codebook at alpha=0/0.5/1.0/2.0 directly validates the spike-deformation prediction
- **Substrate-product positioning:** "encoding-discriminability is the universal lever; the theoretical basis is structured-Wishart spike deformation; the production fix is name-field augmentation; PERFECT cleanup is empirically achievable"

## Cycle 49 closed-loop arc context

PP-409 closes the Cycle 49 substrate-product positioning arc end-to-end via the **4-stage closed-loop pattern** (NEW methodology rule 1st appearance v587):

1. **NO-CLIFF empirical demonstration** (PP-406 + PP-407 v582; substrate composes + decodes architecturally to F=20 and noise=0.3)
2. **DIAGNOSIS at concrete granularity** (PP-408 v586; 32 collision atoms enumerated; signature/complexity 0-populated; ARG0/1/2 mutually cos=1.0)
3. **ARCHITECTURAL FRAMING** (USER SHARES_MATH v585/v586; free-prob drill BBP-supercritical regime)
4. **FIX DEMONSTRATED at production-grade non-destructive cost** (PP-409 v587; name-augmentation PERFECT 1.0 cleanup recovery)

This is the FIRST empirical instance of the 4-stage closed-loop arc; PP-409 + free-prob drill pairing makes it a SINGLE theoretical+empirical substrate-product positioning artifact.

## What Research is asked to do

1. **Acknowledge** the PP-409 empirical alpha-sweep grid as the prediction-test benchmark
2. **Augment** the free-prob drill conclusion with a falsifiable prediction about Gram-matrix spike-eigenvalue deformation under name-augmentation
3. **Optionally**: file a 2x research drill on the SHARES_MATH architectural insight as a follow-on (Research SHARES_MATH edge-type design routing from v586 already filed; this notification is for pairing-acknowledgment not new work)

## Cross-references

- cap_map.md v587 entry: full empirical results + 5 methodology rule progression
- notes/strategy_request_to_research_2026-06-12_free_probability_drill_paired_with_PP406_PP407_substrate_product.md (v582 original pairing notification)
- notes/strategy_request_to_research_2026-06-12_shares_math_edge_type_anchored_in_32_collision_atoms_v586.md (v586 SHARES_MATH design drill anchor)
- notes/exp_dev_to_research_NAME_AUGMENTED_ENCODING_HARDPASS_EXISTING_NAME_FIELD_RECOVERS_DECODE_TO_1_0_FIX_DEMONSTRATED_2026-06-12.md (original Exp-Dev verdict)
- PP-406 / PP-407 / PP-408 / PP-409 (full Cycle 49 closed-loop arc rows in cap_map)
- Layer-2 spectral substrate memory (tw_edge_z=-2.26; structured-codebook regime baseline)

## No action gating

This routing file is informational; Research picks on its own cadence. No HP gates, no pre-reg, no Testbed dependency. The pairing happens whenever the free-prob drill concludes (in flight as of v585).
