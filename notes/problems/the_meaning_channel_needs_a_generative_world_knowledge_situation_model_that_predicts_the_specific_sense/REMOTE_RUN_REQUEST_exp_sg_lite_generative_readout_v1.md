---
cell: experiments/exp_sg_lite_generative_readout_v1.py
mode: full
queue: overnight_queue
timeout_s: 7200
results_path: data/exp_sg_lite_generative_readout_v1/metrics.json
self_test: green
question: does the brain-faithful RECONSTRUCTION-MATCH + predictive-coding SETTLING readout (over the gestalt's top-down predicted meaning mu) break past the nearest-centroid ~0.4 READOUT ceiling on rare senses, generalizing across documents (strict doc-disjoint)?
gate: reconstruction-match and/or +settling beats BOTH the nearest-centroid readout AND the NB strict-split baseline (a_s 0.198 / net -0.038) on held-out test-subordinate, with the shuffled-situation twin LOSING; report LFS a_s per arm + net vs MFS(0.6831), CI half-width beside each margin.
kb_referents:
  - data/corpora/simplewiki/simplewiki_clean_v1.txt
  - data/syntagnet/SyntagNet-1.0/SYNTAGNET_1.0.txt
  - data/_sglite_cache/sglite_w2v_full.pkl
  - data/_sglite_cache/sglite_syntagnet.pkl
---

GPU RUN (RTX 4060 Ti / overnight_queue). This is the SG-lite ideal prototype: a self-supervised incremental
generative sense-gestalt predictor whose readout is the brain's actual glass-box inference-time mechanism
(predictive-coding analysis-by-synthesis + attractor settling), NOT the MFS-biased nearest-centroid that produced
the false ~0.4 ceiling (Yuan/Le). Moved off local CPU (2-epoch GRU on 41M tokens = ~2h CPU) to GPU (minutes).

WHAT THE CELL DOES (bare invocation defaults to FULL):
 1. Loads the PRE-SHIPPED word2vec embeddings (data/_sglite_cache/sglite_w2v_full.pkl) -> NO gensim needed on
    remote; and the pre-shipped SyntagNet cache -> NO wordnet-offset rebuild.
 2. Trains the GRU "situation gestalt" (frozen embeddings -> GRU -> negative-sampling self-supervised on the next
    content word; variational dropout + dropword) on all of simplewiki (~41M tokens), 2 epochs, on GPU (cuda
    auto-detected). Emits a TOP-DOWN predicted-meaning vector mu at each position.
 3. STRICT document-disjoint SemCor eval (n=17,317; even docs = train centroids/exemplars, odd = held-out test):
    3-ARM can-fail benchmark through the brain-faithful additive precision rule --
      * _cent  = nearest-centroid readout (the false-ceiling baseline; MFS-biased)
      * _recon = RECONSTRUCTION-MATCH: score each candidate sense by cosine(mu, grounded sense signature e_s),
                 where e_s = gloss+examples+hyper/hypo/meronym+SyntagNet partners (per-sense grounded -> defeats
                 the MFS bias; rare senses compete equally) -- the drill's ceiling-breaker (BEM +15 LFS at fixed scale)
      * _settle= RECON + a 2-5 step predictive-coding SETTLING loop (winning sense feeds back -> sharpen mu -> re-score)
      * _epi   = hippocampal episodic exemplar completion (k-NN over train gestalts)
    Reports LFS a_s per arm, net vs MFS(0.6831) held-out, and the shuffled-situation twin.

COMPUTE: torch (GPU). numpy/nltk(wordnet+semcor). NO gensim at runtime (embeddings pre-shipped). NO spaCy (SemCor
is nltk-tagged; the only spacy imports in the closure are function-level, never called here). --self-test GREEN.
Deterministic seeds. Glass-box, NO external LLM at inference (the invariant).

FLOOR: MFS 0.6831 (SemCor 30-file polysemous). TWIN: shuffled-situation (permute the reconstruction signal).
EXPECTATION (honest, from the drill): reconstruction-match should beat nearest-centroid on LFS; the settling loop
is the edge over BEM/UKB (single-shot); a rare-sense a_s clearly above the NB strict 0.198 that GENERALIZES is the
win. Report as a prediction under test, not a foregone number.
