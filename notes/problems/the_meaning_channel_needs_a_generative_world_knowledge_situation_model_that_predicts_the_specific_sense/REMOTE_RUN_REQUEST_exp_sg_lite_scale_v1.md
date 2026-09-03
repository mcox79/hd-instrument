---
cell: experiments/exp_sg_lite_scale_v1.py
mode: full
queue: overnight_queue
timeout_s: 13800
results_path: data/exp_sg_lite_scale_v1/metrics.json
self_test: green
question: does SCALING the gestalt to the recipe's sweet spot (~277M tokens ARC+simplewiki, 300-d embeddings, hidden-512 GRU, 3 epochs) push the reconstruction-match a_s past the 41M/200-d plateau (~0.28) toward the ~0.33-0.39 glass-box band, still GENERALIZING (strict doc-disjoint)?
gate: reconstruction-match / +settling a_s(test-sub) clearly above the 41M gestalt's 0.28 AND above NB-strict 0.198, net vs MFS(0.6831) CI-separated with the twin LOSING; report a_s per readout arm + net + CI half-width.
kb_referents:
  - data/corpora/simplewiki/simplewiki_clean_v1.txt
  - data/corpora/arc/ARC-V1-Feb2018-2/ARC_Corpus.txt
  - data/syntagnet/SyntagNet-1.0/SYNTAGNET_1.0.txt
  - data/_sglite_cache/sglite_syntagnet.pkl
---

GPU SCALE RUN (RTX 4060 Ti). The 41M/200-d/2-epoch SG-lite gestalt maxed the READOUT (reconstruction-match a_s
~0.28 -- beats the nearest-centroid false ceiling 0.22, beats the overfit NB 0.198, GENERALIZES strict
doc-disjoint, net +0.0154 CI-sep; IDF pooling + settling neutral). The remaining lever is CORPUS SCALE (recipe
drill: 100-500M sweet spot), which strengthens BOTH the top-down prediction mu and the grounded gloss embeddings
e_s. This run: ~277M tokens (ARC science 238M + simplewiki 40M), 300-d word2vec, hidden-512 GRU, 3 epochs, then
the same 3-arm reconstruction-match benchmark (centroid vs recon vs +settle vs epi), strict document-disjoint.

DEPENDENCIES (heads-up, like the nltk-semcor fix on the prior run):
 * gensim -- this run TRAINS word2vec fresh at 300-d on ~277M tokens (the 200-d pre-shipped cache is the wrong dim,
   deliberately NOT reused). If the GPU box lacks gensim, install it (as nltk-semcor was installed for the base run).
   The ~277M skip-gram w2v is the wall-clock bottleneck (~1-2h CPU); the GRU is fast on GPU.
 * nltk wordnet+semcor -- present now (fixed for the base run).
 * ARC_Corpus.txt is 1.48GB -- ships once if missing on the remote.

COMPUTE: torch (GPU) + gensim (w2v, CPU) + nltk. NO spaCy (function-level only). --self-test GREEN. Deterministic.
Glass-box, NO external LLM at inference (the invariant).

HONEST EXPECTATION (recipe drill): a_s ~0.33-0.39 (corpus-diffuseness ceiling; diminishing returns past ~100M) --
a real but modest lift over 0.28, with the reconstruction-match + settling readout (the ceiling-breaker) riding on
the stronger gestalt. Report as a prediction under test. If it lands ~0.35 that GENERALIZES, that is the pushed
prototype at the glass-box band; the next fidelity lever after this is the role-filler prediction TARGET (true
Sentence-Gestalt), not more scale.
