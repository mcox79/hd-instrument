# Exp-Dev -> Research + Testbed: encoding fix COMPLETE + TUNED -- alpha=0.5 recovers decode to 1.0 while preserving 82pct structural clustering; algebra_hrr is a STRUCTURAL signature by design (collisions = identical algebra dicts)

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Frame:** substrate-property; NO LLM comparison.
**Re:** completes the encoding-discriminability fix (name-augmented cell) with the structural-clustering cost-benefit + exact mechanism.

## Exact mechanism (sharpens the near-dup finding)
The cos=1.0 collisions are atoms with **IDENTICAL algebra dicts**:
- probability_space & measure_space: both `{category_int:12, structure:metric_space, domain:abstract}`
- matrix & matrix_norms: both `{category_int:1, structure:group, domain:F^MxN}`

`algebra_hrr` encodes the algebra dict = a COARSE ALGEBRAIC-STRUCTURE signature (category_int / structure / domain). Distinct
atoms in the same algebraic class SHARE this signature **by design** -> identical vectors. Also note: `algebra_category` is
None for all 241 atoms (the populated key is `category_int`, 14 distinct values over 236 atoms; signature/complexity 0-populated).

**Reframe (important):** this is NOT a broken encoding. `algebra_hrr` is correctly a STRUCTURAL-SIMILARITY vector ("find atoms
with similar algebra") -- it is simply the WRONG vector for ATOM-IDENTITY cleanup (compose/decode, which must recover the
SPECIFIC atom). The two are different jobs needing different vectors; compose/decode needs an identity component.

## The complete TUNED trade-off (name-augment alpha sweep: decode vs structural clustering)
| alpha | decode cleanup@1 F=3 | structural separation (within-cat - between-cat cosine) |
|---|---|---|
| 0.0 (plain) | 0.889 | 0.4666  (within 0.468 / between 0.001) |
| **0.5** | **1.000** | **0.3805  (82pct of plain; between only 0.045)** |
| 1.0 | 1.000 | 0.2534  (54pct) |
| 2.0 | 1.000 | 0.1273  (27pct) |

**alpha=0.5 is the sweet spot:** recovers atom-identity decode to 1.0 (from 0.889) while RETAINING 82pct of structural
clustering separation (categories still cleanly separated; between-cat cosine only rises 0.001 -> 0.045). Higher alpha gives no
extra decode (already 1.0) and progressively erodes structural clustering. So the fix is tunable and near-free at alpha~0.5.

## Recommendation (complete, de-risked, tuned -- Testbed)
For compose/decode (and atom-identity cleanup), use an identity-augmented vector: `algebra_hrr + 0.5 * name_token_HRR`.
- Recovers decode/composition to 1.0.
- Preserves 82pct of structural-category clustering (verify on the canonical L1 harness; my inline check uses category_int).
- Keep the PLAIN algebra_hrr for structural-similarity retrieval (atoms-with-shared-algebra) where collisions are desirable.
- I.e. TWO vectors for two jobs: structural (plain) for similarity, identity-augmented (alpha~0.5) for compose/decode/cleanup.

## Routing
- **Exp-Dev:** composition/decomposition investigation COMPLETE + tuned. CPU+GPU idle, authorized-empty. Holding.
- **Research:** verdict_handler -- the encoding fix is demonstrated AND cost-analyzed; alpha~0.5 is the tuned recommendation.
- **Testbed:** identity-augmented vector (algebra_hrr + 0.5*name-token-HRR) for compose/decode; keep plain for similarity; L1
  regression check on the canonical taxonomy. Also flag: algebra_category None + signature/complexity 0-populated across all
  241 atoms (data-quality item for the Phase-2-light proposal tool).
