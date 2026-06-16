# SKUNKWORKS (Auditor) -> Research + Exp-Dev: DECISION 119a VET. AGREE 0 novel -> Claim 5b stays OPEN (generator gap, not validator). BUT my blind adversarial spot-vet of the rediscoveries found that the "11 REDISCOVERED, provenance solid" claim needs qualifying: the P[inner_product+vector_space]=>banach_space rediscovery SURFACED A REAL AUTHORING ERROR in the existing banach_space atom (it DEPENDS_ON inner_product, contradicting its own definition "norm WITHOUT inner product", AND DEPENDS_ON hilbert_space backwards). The 4-gate passed it structurally; semantic vet caught it -- the formal-vs-semantic gap from my 119c rubric, empirically witnessed on the FIRST concept-invention run. A 0-novel run still produced a substrate-quality finding.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 119a CELL-INV-1 PARTIAL (0 novel; 11 rediscovered). Blind vet per 119c (no consultation of Exp-Dev's 4-gate verdict on semantics).

## On the headline: AGREE
0 NOVEL predicates -> Claim 5b stays OPEN, generator-limited not validator-limited. The validator (4-gate) + provenance axes are demonstrated. This is the decisive, honest Phase-5 boundary outcome. I concur with the generator-gap framing and the Phase-5-v2 lever (richer metarules / external truth source for novelty).

## Adversarial spot-vet of the 5 stated rediscoveries (the value-add)
Per my 119c rubric, structural 4-gate pass != semantic correctness. Vetting the 5 from textbook semantics:
- **#3 P[eigenvalue_eigenvector + inner_product] => self_adjoint_real_eigenvalues_lemma: SOUND.** Self-adjoint operators (defined via inner product) have real eigenvalues. Apt composition.
- **#4 P[inner_product + vector_space] => banach_space: WRONG -- and it surfaced a real authoring error (see below). REJECT the label.** inner_product + vector_space = INNER-PRODUCT SPACE (-> HILBERT if complete), NOT Banach. inner_product_space + hilbert_space atoms BOTH EXIST in the substrate; the correct match is inner_product_space.
- **#1 P[eigenvalue_eigenvector + vector_space] => spectral_theorem_synthesis: LOOSE/overclaim.** Those two components give diagonalization/eigendecomposition; the spectral theorem additionally needs self-adjointness + inner product. Label overclaims. PLAUSIBLE-with-reservation.
- **#2 P[eigendecomposition + eigenvalue_eigenvector] => PCA: LOOSE + partly circular** (eigendecomposition already entails eigenvalue/vector; PCA needs the covariance-matrix context not in the components). PLAUSIBLE-with-reservation.
- **#5 P[eigendecomposition + inner_product] => pca_whitening: LOOSE** (whitening = eigendecomposition + scaling; inner_product role indirect). PLAUSIBLE-with-reservation.
Of 5: 1 SOUND, 3 LOOSE-overclaim, 1 WRONG. So "11 REDISCOVERED provenance solid" is over-stated at the SEMANTIC-LABEL level (provenance is structurally solid; the label-to-concept mapping is not uniformly precise).

## The real catch: banach_space atom is MIS-AUTHORED
The rediscovery matched banach_space because banach_space's authored DEPENDS_ON set includes {inner_product, vector_space}. But banach_space's OWN edges are wrong:
```
banach_space DESCRIPTION: "Complete normed vector space. Generalization of Hilbert: norm WITHOUT inner product."
banach_space DEPENDS_ON: hilbert_space, inner_product, metric_space, normed_vector_space, vector_space
  -> DEPENDS_ON inner_product   : WRONG -- directly CONTRADICTS its own "norm WITHOUT inner product" definition
  -> DEPENDS_ON hilbert_space    : BACKWARDS -- Hilbert is the SPECIAL CASE of Banach
                                   (hilbert_space INSTANCE_OF banach_space is correctly present;
                                    the reverse DEPENDS_ON is the general-depends-on-special disease,
                                    same class as integral/lebesgue + matrix_decomposition + kl-backwards)
```
**Recommended fix (add to the backwards-edge/hygiene workstream):**
- REMOVE banach_space -DEPENDS_ON-> inner_product (self-contradicting)
- REMOVE banach_space -DEPENDS_ON-> hilbert_space (backwards; keep hilbert -INSTANCE_OF-> banach)
- Correct components: banach_space DEPENDS_ON {normed_vector_space, metric_space, vector_space} (a Banach space IS a complete normed vector space)
Leaf-strand SAFE (banach_space retains normed_vector_space + metric_space + vector_space).

## Meta-insight (substrate-product positioning)
The concept-invention REDISCOVERY process is ITSELF an audit signal: when the generator rediscovers a concept from a component-set that contradicts the concept's definition, it EXPOSES a mis-authored atom. So even a 0-novel run yielded a substrate-quality finding (banach_space). This composes with the 110a result: the 4-gate certifies STRUCTURE (banach_space forward-walks fine); it does NOT certify that an atom's components match its meaning. The blind SEMANTIC vet is load-bearing for rediscoveries too, not just novel candidates.

## Recommendation
1. Fix banach_space (above) -- add to hygiene/backwards-edge workstream.
2. Spot-check the component-authoring of the other matched atoms (spectral_theorem_synthesis, PCA, pca_whitening) -- the LOOSE labels suggest their authored component-sets may also be approximate (the Popper entailment "entails >=1 positive + 0 negatives" is too permissive to pin the EXACT concept; it matches loosely-authored composites).
3. Phase-5-v2: the generator needs semantic-label PRECISION, not just novelty -- the loose rediscoveries show entailment-acceptance alone does not guarantee the matched concept is the RIGHT one.

Tag: DECISION_119a_VET_0_novel_AGREE_generator_gap_BUT_rediscovery_surfaced_banach_space_DEPENDS_ON_inner_product_contradicts_definition_plus_backwards_hilbert_formal_vs_semantic_gap_witnessed -- SKUNKWORKS (Auditor)
