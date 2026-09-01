---
cell: experiments/exp_grounded_distributional_fusion_paraphrase_v1.py
mode: full
queue: overnight_queue
timeout_s: 7200
results_path: data/exp_grounded_distributional_fusion_paraphrase_v1/metrics.json
self_test: green
smoke: green
question: Does fusing the GROUNDED sensorimotor spoke (Lancaster) with the DISTRIBUTIONAL/linguistic spoke (PPMI-SVD from UD-EWT) -- the ATL complementary hub fusion -- cross the sensorimotor-coarseness wall on paraphrase-robust event coreference, at FULL corpus scale?
gate: PASS = fusion_g11_distrib hit@1 CI/margin ABOVE grounded11 AND above distributional (all above chance 0.234). A rigorous NEGATIVE (fusion does not beat the better single spoke) is a full PASS -- it says the coarse sensorimotor space is the ceiling for this instrument and the fusion does not help, which re-scopes the meaning-channel follow-on.
kb_referents:
  - data/exp_grounded_distributional_fusion_paraphrase_v1/instances.json
  - data/grounding_testbed/Lancaster_sensorimotor_norms_for_39707_words.csv
  - data/corpora/ud_english_ewt/en_ewt-ud-train.conllu
---

# REMOTE_RUN_REQUEST -- exp_grounded_distributional_fusion_paraphrase_v1

BRAIN CLAIM. The necessity test (`exp_grounded_binding_paraphrase_coref_v1`) proved GROUNDED binding beats a
symbolic dict under paraphrase, but the 11-dim Lancaster SENSORIMOTOR space topped out at hit@1 ~0.40 -- a
COARSE concept proxy. The brain-faithful fix is the ATL COMPLEMENTARY FUSION (Patterson 2007; Lambon Ralph
2017): the hub combines sensorimotor + distributional/linguistic spokes. This run tests the fusion at FULL
scale (PPMI-SVD over ~all of UD-EWT, dim=300, ctx=5000 -- the heavy GPU part).

ARMS (paraphrase-coref hit@1; retrieval reduces to concept-space nearest-neighbour so it isolates SPACE
quality; WordNet defines paraphrases INDEPENDENTLY of both spaces -> not circular; NO LLM):
  grounded11          -- Lancaster 11 sensorimotor means (the necessity-cell space, ~0.40 smoke).
  distributional      -- PPMI-SVD verb vectors from UD-EWT (~0.29 smoke, coverage-limited at smoke scale).
  fusion_g11_distrib  -- z-concat of the two spokes (~0.44 smoke -> beats either alone).

REMOTE-SAFETY: module imports only numpy/torch/csv/json/math (NO spaCy, NO nltk at run time). The
WordNet-dependent instances are pre-built LOCALLY and shipped as instances.json (a KB_REFERENT); the cell
LOADS the cache and never parses. Full run defaults ON when invoked bare (smoke only under --smoke).
