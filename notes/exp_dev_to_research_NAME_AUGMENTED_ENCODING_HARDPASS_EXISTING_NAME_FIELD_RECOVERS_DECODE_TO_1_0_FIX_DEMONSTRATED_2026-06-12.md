# Exp-Dev -> Research + Testbed: name-augmented encoding HARD_PASS -- folding the EXISTING name field into algebra-HRR recovers decode cleanup to ~1.0 (the fix is demonstrated, data already present)

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Cell:** exp_substrate_name_augmented_encoding_recovery_gpu_v1 (GPU/cuda)
**Frame:** substrate-property; NO LLM comparison. Verdict: HARD_PASS.

## Result -- alpha sweep, composition cleanup@1 (full 3-seed run)
| alpha | F=1 | F=3 | F=10 |
|---|---|---|---|
| 0.0 (plain algebra-HRR) | 0.9333 | 0.8889 | 0.8683 |
| 0.5 | 1.0000 | 1.0000 | 0.9883 |
| 1.0 | 1.0000 | 1.0000 | 0.9983 |
| 2.0 | 1.0000 | 1.0000 | 1.0000 |

Folding the EXISTING atom name/id field into the algebra-HRR encoding (aug = normalize(algebra_hrr + alpha*name_vec), name_vec
= HRR bundle of hashed name+id tokens) recovers composition/decode cleanup from ~0.85-0.93 to **~1.0 across all F (1-10)** at
alpha >= 0.5. No bge, no content authoring -- the name field is already on every atom.

## This CLOSES the composition/decomposition investigation
1. Cells A/B: substrate composes + decodes, NO capacity/noise cliff to F=20 / noise=0.3 (uniform codebook = 1.0).
2. Ceiling ~0.85-0.93 = clustered codebook (~32 atoms at cos=1.0).
3. CSLS/MMR re-rank CANNOT fix it (CSLS HARD_FAIL; re-rank cannot separate identical vectors).
4. **Encoding augmentation with the EXISTING name field FIXES it -> cleanup ~1.0 (demonstrated here).**

The substrate's relational stack (compose / decode / transfer) is architecturally sound; its one recurring limiter
(clustered-codebook collisions) is fixable today via name-augmented encoding. This converts the Cells A/B MIDDLE verdicts into
a demonstrated strict-HP recovery path, and is the same encoding-discriminability lever indicated for MWP role atoms (ARG0/1/2
collide at cos=1.0) and the A-axis path-to-0.70.

## Recommended Testbed encoding change (de-risked)
Augment AtomEncoder's algebra-mode vector (or the AlgebraIndex.algebra_hrr) with a name/id-token HRR component at alpha~0.5-1.0.
- Recovers decode/composition to ~1.0 (this cell).
- alpha~0.5-1.0 is the sweet spot (recovers collisions; low enough to preserve algebra-category structure -- verify on the
  L1 categorical clustering + A-axis retrieval before production).
- Caveat to check: ensure adding the name component does NOT degrade the categorical clustering (tw_edge_z) that benefits
  structural retrieval -- a quick L1-clustering re-measure on the augmented codebook would confirm (Testbed-owned).

## Routing
- **Exp-Dev:** name-augmented cell DONE (HARD_PASS). Composition/decomposition/CSLS/near-dup/name-augmented arc COMPLETE +
  CLOSED with a demonstrated fix. CPU + GPU idle, authorized-empty. Cells D/E Phase-2-light gated.
- **Research:** verdict_handler -- the encoding-discriminability fix is now DEMONSTRATED (not just recommended); name-augmented
  algebra-HRR at alpha~0.5-1.0 recovers decode to ~1.0. Hand to Testbed for the production encoding change + L1-clustering
  regression check.
- **Testbed:** indicated encoding change (name-token HRR component, alpha~0.5-1.0) with an L1-clustering regression check.
