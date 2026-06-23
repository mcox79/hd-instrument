# PRE-REG: b2_substrate_only_tinystories_lm_v1

**Author:** Exp-Dev (per Director design)
**Date:** 2026-06-22
**Anchor source:** notes/research_to_exp_dev_BATCH_HIERARCHICAL_LM_TIER5C_2026-06-08.md (B2)
**Class:** Substrate-only LM (rung-1; Path A pseudo-LM via NEXT_TOKEN single-relation Hebbian bind)

## Research question

Can the substrate act as a pseudo-LM by treating next-token prediction as a single-relation
one-hop hop in a KG store (Hebbian-bound `(word_t, NEXT_TOKEN, word_t+1)`), and match the
classical word-bigram baseline on held-out token perplexity?

The L2 master plan already has N1 v3.1 substrate-LM at 4.96 BPC vs word-bigram 3.84 BPC via a
complex VQ + codebook stack. This cell is the simpler substrate-native ablation: word entities
+ single NEXT_TOKEN relation. Both worse and better outcomes are informative.

## Corpus

text8 (`data/text8_cache/text8.txt`, 100MB, lowercase, space-separated). TinyStories was the
original anchor; text8 is the locally-available substitute for the same Path A test. First
~120k tokens for train (substrate Hebbian writes), next 10k tokens held out for perplexity
eval. Smoke: 12k train / 1k held-out.

## Mechanism (3 arms, Fix #16 discriminator)

1. **SUBSTRATE_LM** (Path A pseudo-LM): each unique training-vocab word encoded as a char_trigram
   HD vector; Hebbian outer-product binds `(w_t, NEXT_TOKEN, w_{t+1})` into a single FHRR-style
   weight matrix W. Next-token prediction = `argmax_over_vocab cosine(W @ enc(w_t), enc(w'))` for
   each candidate w' in vocab. (Equivalent to substrate KGStore predict_one_hop_topk(w_t,
   NEXT_TOKEN) re-implemented inline for speed; semantically identical.)
2. **UNIGRAM_BASELINE** (CAN-FAIL floor): predict the argmax unigram for every position.
3. **WORD_BIGRAM_BASELINE** (standard NLP comparison): laplace-smoothed count-based bigram
   `P(w_{t+1} | w_t)`; predict argmax. Backs off to unigram for unseen prefixes.

## Metric

Token-level cross-entropy and perplexity on held-out 1k tokens. We report both:
- **top-1 accuracy** (substrate decode is argmax; matches inference path)
- **perplexity** (for SUBSTRATE_LM we map cosine-similarities to a softmax distribution with
  temperature T=1.0 over vocab to get a proper probability; for BIGRAM we use the smoothed
  count probability).

Heldout tokens whose context-word is OOV at train-time are excluded from BIGRAM perplexity
(standard practice); SUBSTRATE_LM evaluates on the same set for fair comparison.

## Pre-registered HARD BANDS

- **HARD_PASS**: `ppl(SUBSTRATE_LM) <= ppl(WORD_BIGRAM_BASELINE)` AND
  `acc(SUBSTRATE_LM) >= acc(WORD_BIGRAM_BASELINE)`. Substrate matches OR beats classical
  bigram via single-relation Hebbian bind. L2 MVP frontier achievement.
- **MIDDLE_BAND**: `ppl(SUBSTRATE_LM) < ppl(UNIGRAM_BASELINE)` AND
  `ppl(SUBSTRATE_LM) > ppl(WORD_BIGRAM_BASELINE)`. Substrate beats unigram floor but doesn't
  match bigram (this is the existing L2 state with the more complex VQ stack).
- **HARD_FAIL**: `ppl(SUBSTRATE_LM) >= ppl(UNIGRAM_BASELINE)`. Substrate fails to even improve
  over unigram floor; mechanism is broken.

## Formula self-tests (PROT-022)

1. char_trigram encoder is deterministic: same word -> same HD vector.
2. Hebbian bind is order-sensitive: `bind(a,b) != bind(b,a)`.
3. SUBSTRATE_LM perfect-recall control: on a 10-token cycle trained for 1 epoch with V_DIM
   large enough, top-1 accuracy on the cycle's training tokens must be >= 0.7 (sanity floor;
   if this fails the mechanism is broken before any real measurement).
4. UNIGRAM_BASELINE is a CAN-FAIL floor: its top-1 accuracy is bounded above by max-class
   frequency; assert measured acc equals this analytic bound (no hidden trick).
5. WORD_BIGRAM perplexity is computed correctly: hand-crafted 4-token corpus with known bigram
   probabilities matches expected ppl within 1%.

## n_llm_calls = 0, substrate-only-decode preserved

## Tier / queue

remote_cpu_queue (numpy-only; ~60-90min wall budget; no GPU needed). Per [[reference_hd_dispatch_queue_architecture]] this is the proven SSH path.

## Smoke->FULL timeout estimation

Smoke runs ~12k train + 1k held-out at V_DIM=1024 in <60s (substrate Hebbian = vectorized
outer-products; perplexity loop = matmul). FULL is 10x train tokens + 10x held-out at V_DIM=2048.
Per the queue_add.py formula:
  `timeout_s = ceil(1.5 * smoke_wall_s * (FULL_N/smoke_N)^scaling_exp * (FULL_seeds/smoke_seeds))`
  Conservative: `1.5 * 60 * 10^1.2 * 1` = ~1430s; round up to 3600s (1h) for safety margin
  (matmul-heavy perplexity loop at V_DIM=2048 over 10k held-out tokens dominates).

## Cross-references

- Anchor: notes/research_to_exp_dev_BATCH_HIERARCHICAL_LM_TIER5C_2026-06-08.md B2
- L2 MVP frontier state: N1 v3.1 substrate-LM at 4.96 BPC vs word-bigram 3.84 BPC (different
  mechanism — VQ-codebook + Hebbian, not simple word-entity + NEXT_TOKEN)
- Template: experiments/exp_hoc1_word_bigram_v1.py (pattern reference for write_metrics +
  self-test + per-seed)
