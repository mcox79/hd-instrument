# Research decisions — 2026-09-03

- WSD context-representation drill: `notes/research_wsd_contextual_encoding_glassbox_mechanisms_2026-09-03.md` —
  the bag-of-context-words cap is upstream of every lever already tried (frequency-prior REFUTED,
  C3 gain HARD_FAIL, C4 settling declined); two new candidates (syntax-filtered second-order context
  vector; exemplar retrieval instead of centroid averaging) are NOT blocked behind B4 the way C3 is.
  Companion hand-off: `notes/exp_dev_handoff_research_wsd_contextual_encoding_2026-09-03.md`.
- WSD input-representation drill: `notes/research_wsd_input_representation_sense_embeddings_2026-09-03.md` —
  static per-synset/multi-prototype sense embeddings are NOT the cheap upstream fix (brain-unfaithful
  for this project's polysemy-type failure population; sense-embeddings-alone underperform a plain
  supervised WSD baseline in the one clean number found; every real system circularly falls back to the
  same frozen sense-conflated context vector). Confirms/does not disturb the contextual-encoding arms
  already registered in the companion 09-03 notes. Companion hand-off (low-priority confirmatory test):
  `notes/exp_dev_handoff_research_wsd_input_representation_2026-09-03.md`.
