# Pre-registration: wave14ze_gen_vs_ngram

Date: 2026-05-21
Status: Pre-registered, gated
Priority: substrate generation vs trigram-Markov baseline
Author: experiment_dev session, pipeline tick 38

## Why
yz showed substrate can generate non-degenerate text with sampling. Real
product question: is the substrate's generation BETTER than trigram-Markov
(simplest n-gram baseline)?

## Verdict labels
- GEN_SUBSTRATE_BEATS_NGRAM: substrate composite score (entropy - 2*repetition) > ngram + 0.3
- GEN_NGRAM_BEATS_SUBSTRATE: opposite direction
- GEN_SIMILAR: scores within 0.3 of each other
- GEN_VS_NGRAM_INCONCLUSIVE

## Runtime: ~2-3 min
