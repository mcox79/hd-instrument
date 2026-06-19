# Pre-registration: Cell C -- cross-domain transfer (SST-2 -> IMDB sentiment)

**Date:** 2026-06-12 (Day 4 Cycle 50)
**Cell:** experiments/exp_substrate_crossdomain_transfer_sst2_imdb_cpu_v1.py
**Routing:** research_to_exp_dev_CELL_C_CROSS_DOMAIN_FALLBACK (SST-2 -> IMDB Pair-1 LOCK). Substrate-quality-first; NO LLM frame.
**Lane:** local_cpu_queue (IMDB loads via datasets lib; available on laptop + home).

## Design
Substrate-product question: do substrate-classical primitives show POSITIVE TRANSFER across a distributional shift?
discriminative_perceptron sentiment classifier (averaged binary perceptron over hashed word-unigram+bigram features) trained
on SST-2 (short formal snippets) -> warm-start transfer to IMDB (long informal reviews) vs train-from-scratch on IMDB, at
1/5/10/100pct of IMDB training data (cap 5000 train, 2000 test), 3 seeds. Reports transfer F1, scratch F1, ratio, + the
zero-shot SST-2-on-IMDB F1 reference.

## Pre-registered verdict bands (Research LOCK; headline = transfer/scratch ratio at 5pct IMDB data)
- **HARD-PASS:** ratio >= 1.20 (positive transfer; substrate primitive carries discriminative signal across domain).
- **MIDDLE:** ratio 0.95-1.20 (neutral / weak positive transfer).
- **HARD-FAIL:** ratio < 0.95 (negative transfer; primitive does not generalize across this shift).
- **UNKNOWN:** IMDB unavailable (env-gated).

## Substrate-product artifact (stands alone, no LLM frame)
Whether the substrate discriminative_perceptron primitive generalizes across a sentiment-domain distributional shift
(short formal -> long informal), measured as low-data transfer advantage over scratch training, with the zero-shot
SST-2-on-IMDB F1 as a domain-gap reference.
