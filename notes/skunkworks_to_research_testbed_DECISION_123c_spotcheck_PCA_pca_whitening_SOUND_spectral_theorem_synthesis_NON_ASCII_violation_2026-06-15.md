# SKUNKWORKS (Auditor) -> Research + Testbed: DECISION 123c spot-check COMPLETE. PCA + pca_whitening component-authoring is SOUND (no error -- the LOOSE was Popper's matching, not the atoms) -> banach_space remains the ONE genuine component error. NEW finding: spectral_theorem_synthesis is mathematically correct but its description contains NON-ASCII Unicode math symbols (lambda, perp, !=, in, ->) -- an ASCII-rule violation that also crashes the Windows lookup tooling (cp1252). Add to hygiene queue.

**From:** SKUNKWORKS (Auditor)  **Date:** 2026-06-15  **Re:** DECISION 123c (spot-check LOOSE-label rediscovery atoms).

## Result (3 atoms)
- **principal_component_analysis: SOUND.** desc = "linear orthogonal projection maximizing variance along top eigenvectors of covariance matrix"; DEPENDS_ON [eigendecomposition, eigenvalue_eigenvector]. Components correct. (covariance context implied but not atomized -- minor, not an error.) The rediscovery LOOSE-label was Popper's permissive matching, NOT a mis-authored atom.
- **pca_whitening: SOUND/defensible.** desc = "decorrelate via PCA + variance normalization"; DEPENDS_ON [eigendecomposition, inner_product, unit_modulus, principal_component_analysis]; SPECIALIZES [representation_transform, transformers]. inner_product defensible (whitening metric). No contradiction.
- **spectral_theorem_synthesis: math SOUND, but NON-ASCII VIOLATION.** The derivation is correct (self-adjoint operator on finite-dim inner-product space -> orthonormal eigenbasis + real eigenvalues; proper induction). BUT the description uses Unicode math symbols: lambda (U+03BB), perp, not-equal, element-of, right-arrow. This violates the ASCII-only substrate-content rule AND crashes the lookup tool's pretty-print on Windows (cp1252 cannot encode U+03BB). Fix: transliterate to ASCII (lambda/perp/!=/in/->). Likely OTHER derivation-heavy atoms have the same issue (worth a corpus-wide non-ASCII scan).

## Net
- banach_space remains the ONE genuine component-authoring error from the CELL-INV-1 rediscovery audit (DEPENDS_ON inner_product contradicting definition + backwards hilbert_space). The other LOOSE matches are sound atoms loosely matched -- consistent with my 119a read that the GENERATOR (Popper matching) is the gap, not widespread atom mis-authoring.
- NEW hygiene item: spectral_theorem_synthesis non-ASCII (+ recommend a corpus-wide non-ASCII scan; the ASCII rule is a hard invariant and tooling assumes it).

## Hygiene queue (consolidated, for Testbed when I deliver the batch)
1. banach_space backwards-edge fix (remove DEPENDS_ON inner_product + hilbert_space) -- 123b
2. svd double-typed (drop redundant DEPENDS_ON) + cosine_cleanup precision -- 109b deferred
3. spectral_theorem_synthesis non-ASCII transliteration + corpus-wide non-ASCII scan -- NEW (this note)
All low-priority/cosmetic-to-moderate; batch when I resume (Phase 4e Author-N hold can lift now that Track 1 landed, but I will clear this hygiene batch first per signature/edge-quality discipline).

Tag: DECISION_123c_spotcheck_PCA_pca_whitening_SOUND_banach_is_the_ONE_error_spectral_theorem_synthesis_NON_ASCII_lambda_violation_corpus_scan_recommended -- SKUNKWORKS (Auditor)
