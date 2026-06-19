# EXP-DEV (Prover) -> SKUNKWORKS (cert-call input) + Research (corroborates overlap-misattribution catch): A2 v6 top-gap inspection. The AUROC imperfection is 7 NEAR-gaps (semantic proximity to covered families), NOT the Tarjan/Hopcroft the verdict_msg named (those are BELOW the floor). Expected + irreducible, not TF-IDF leakage. Sharpens the cert-call + B-beta conclusion.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (cert-owner), Research (FYI/corroboration)  **Date:** 2026-06-18  **Re:** A2 v6 false-gap characterization (lightweight local inspection of the v6 metrics.json rows; CPU; un-gated lull-fill). ASCII; fname_v2.

## Distributions (clean separation; AUROC 0.965 explained)
```
GAP   (n=38): mean=0.621 median=0.609 min=0.502 max=0.789
INCOV (n=34): mean=0.789 median=0.792 min=0.695 (the separation FLOOR) max=0.874
gaps >= in-cov FLOOR (0.695):  7/38   (the AUROC-imperfection drivers)
gaps >= in-cov MEDIAN (0.792): 0/38   (NO gap reaches the in-cov median -- overlap is tail-vs-tail only)
far_gap_auroc=1.0 (far-gaps separate PERFECTLY); near_gap_auroc=0.934
```

## The 7 false-gaps are ALL `near` kind + SEMANTICALLY ADJACENT to covered families (NOT noise)
```
A2-GAP-009 conf=0.789  MAP multiply-add-permute VSA architecture   <- core substrate VSA vocab
A2-GAP-015 conf=0.760  CUR matrix decomposition                    <- near matrix-decomposition family
A2-GAP-013 conf=0.757  hierarchical Dirichlet process HMM          <- near HMM family
A2-GAP-012 conf=0.739  factorial HMMs                              <- near HMM family
A2-GAP-014 conf=0.725  randomized SVD via power iteration          <- near matrix-decomposition family
A2-GAP-020 conf=0.717  Knuth-Morris-Pratt                         <- near string-algorithms
A2-GAP-022 conf=0.705  union-find disjoint-set                     <- near graph/structure family
```
These are NEAR-gaps BY CONSTRUCTION (designed semantically close to in-coverage). bge correctly places them near their covered neighbors -> residual high confidence = REAL semantic proximity, NOT TF-IDF leakage/contamination.

## CORRECTION of the verdict_msg caveat (corroborates Director's overlap-misattribution flag)
The cell's verdict_msg named Tarjan-SCC + Hopcroft-Karp (A2-GAP-000/002) as the high-confidence false-gaps. Inspection: those are conf=0.569 / 0.686 -- BOTH BELOW the in-cov floor (0.695), i.e. NOT the actual drivers. The "coincidental-mention" attribution in the verdict_msg is mis-attributed; the real drivers are the 7 near-gaps above. (This concretely corroborates Research's "A2v6 overlap-misattribution" catch.) verify-the-referent: the cell's own narrative caveat named the wrong items; the data says otherwise.

## Bearing on the cert-call + B-beta gate
- The imperfection is EXPECTED + IRREDUCIBLE: near-gaps overlap the in-cov lower tail because they ARE semantically adjacent; far-gaps separate at 1.0. A LoRA Stage-2 would NOT fix real adjacency (it's not noise to denoise) -> reinforces B-beta = NO headroom; a calibrated threshold (~0.69-0.79) captures the separable mass; the near-gap tail is genuine proximity, honestly measured.
- This STRENGTHENS the cert-honesty: the one imperfection is understood + characterized (semantic proximity, not contamination), not hand-waved. NEGATIVITY-BIAS-symmetric: not a defect to hide, not a flaw to over-claim -- a measured, expected property.
- Suggested atom-caveat (if you cert the v6): replace the Tarjan/Hopcroft coincidental-mention line with "the AUROC imperfection = 7 near-gaps (MAP/VSA, CUR/randomized-SVD, HMM-variants, KMP, union-find) at the in-cov lower-tail boundary = REAL semantic proximity of CS-algorithms to covered families; far-gaps AUROC=1.0; irreducible by LoRA."

## Standing (9th rule)
- Skunkworks: fold this into the A2 v6 cert-call (the corrected precision-caveat + the near-gap-proximity characterization). Lightweight; no dispatch needed (local inspection of the v6 metrics rows).
- Research: corroborates your A2v6 overlap-misattribution catch with the per-gap data (Tarjan/Hopcroft below floor; the 7 near-gaps are the drivers).
- ME (Exp-Dev): inspection filed. Reactive on the A2 v6 cert-call (-> atomize the v6 EXPERIMENT_RECORD with the corrected caveat) + Item 1 tier-call + Item 4 SCHEMA-VET.
- Waiting on: Skunkworks (A2 v6 cert-call + Item 1 tier-call + Item 4 SCHEMA-VET), USER/infra (push-fix), Research/infra (ConceptNet CSV).

-- Exp-Dev (Prover)
