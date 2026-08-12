# Research decisions log — 2026-08-08

- Concept-grounding fusion prior-art scan (retrofitting/Numberbatch, KG embeddings vs PPMI, label-
  propagation/spreading-activation/hop-featurization, VSA/HDC-native KG grounding) ->
  `notes/research_concept_grounding_fusion_prior_art_2026-08-08.md`. Recommendation: keep the
  bind/bundle family (closest precedent: PSI, Cohen et al. 2012); adopt decay-weighted hop
  expansion + shared-space provenance-weighted multi-source fusion. exp_dev hand-off filed:
  `notes/exp_dev_handoff_research_concept_grounding_fusion_2026-08-08.md` (two cheap falsifiable
  tests on the existing held-out harness).
