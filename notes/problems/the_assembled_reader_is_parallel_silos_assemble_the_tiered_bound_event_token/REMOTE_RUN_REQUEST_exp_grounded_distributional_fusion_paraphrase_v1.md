---
cell: experiments/exp_grounded_distributional_fusion_paraphrase_v1.py
mode: full
queue: overnight_queue
timeout_s: 7200
results_path: data/exp_grounded_distributional_fusion_paraphrase_v1/metrics.json
self_test: green
smoke: green
question: (CONFIRMATION-ONLY -- see note) Does fusing GROUNDED (Lancaster) + DISTRIBUTIONAL (PPMI-SVD from UD-EWT) cross the coarseness wall? The local PHASE DIAGRAM already answered: UD-EWT is only ~12.5k sentences, so the distributional spoke is CORPUS-CAPPED (flat at 0.274 from 40k sents on) and NO simple fusion beats grounded-alone (0.444); the ORACLE route reaches 0.60 (complementarity is extractable) and FAMILIARITY weighting beats z-sum (0.40 vs 0.37). This full run only re-confirms at full n; it will NOT move the number on UD-EWT. The REAL fix is a LARGE-corpus distributional (simplewiki-15M / Wikipedia PPMI) -- a separate cell.
gate: PASS = reproduces the phase-diagram finding (distributional FLAT past the corpus size; oracle ~0.60; freq_wt > zsum). A rigorous NEGATIVE is a PASS. NOTE: low priority -- the science is already established locally; run only if GPU is idle.
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

REMOTE-SAFETY: module imports only numpy/torch/csv/json/math (NO spaCy, NO nltk, NO experiments.*, NO hdlab
at run time -- verified clean). The WordNet-dependent instances are pre-built LOCALLY (experiments/
_build_fusion_instances.py) and shipped as instances.json (a KB_REFERENT); the cell LOADS the cache and never
parses. Full run defaults ON when invoked bare (smoke only under --smoke).

RE-TRIGGER 2026-09-01: fixed the two prior rejections -- (1) queue line had an inline comment (removed);
(2) --self-test exceeded 300s (now a TINY distributional build: --self-test 4s, --smoke 3s, both GREEN). The
cell no longer imports any spaCy-closure module. The earlier queue_add.sh rc=1 coincided with the local-box
reset; re-dispatching.
