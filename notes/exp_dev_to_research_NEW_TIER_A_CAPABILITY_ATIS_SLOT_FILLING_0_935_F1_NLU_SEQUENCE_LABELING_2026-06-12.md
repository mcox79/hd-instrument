# Exp-Dev -> Research: NEW Tier-A capability -- substrate-classical ATIS SLOT FILLING slot-F1=0.9352 (123 slot types). NLU sequence labeling via the universal discriminative-weighting lever; no LLM.

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-product; NO LLM comparison. Ran on DESKTOP CPU.

## Result
- **ATIS slot filling: slot-F1 = 0.9352** (P=0.939, R=0.931), 4978 train / 893 test, **123 slot tags** (fromloc.city_name,
  depart_time.time, toloc.city_name, ...). Span-level slot F1 (the standard ATIS metric).
- Method: discriminative_perceptron (structured perceptron + Viterbi) over BIO slot tags, word/shape/affix/context features.
  The SAME universal discriminative-weighting lever as POS/NER/chunking. NO LLM, NO pretraining.

## Why it matters (substrate-product positioning)
- **NEW Tier-A NLU capability**: slot filling / spoken-language-understanding sequence labeling, not previously in the roster.
- 0.935 slot-F1 is PRODUCTION-GRADE (strong BiLSTM-CRF neural systems ~0.95; substrate-classical structured perceptron reaches
  0.935 with no pretraining over 123 fine-grained slot types). Demonstrates the discriminative-weighting lever scales to
  large-tag-set NLU sequence labeling.
- Tier-A roster now spans: POS 0.95 / NER 0.71 (4-type CoNLL) / chunking 0.92 / dep-parse 0.79 / sentiment 0.78 / AG-News 0.85
  / intent 0.83 / MWP / + **slot-filling 0.935** (this) -- a broad substrate-classical NL/NLU capability surface, all via one
  universal lever, no LLM.

## Routing
- **Exp-Dev:** new Tier-A capability delivered (slot filling 0.935, HARD_PASS). Produced as a full-auto continue (new
  substrate-product evidence) rather than padding the maxed path-to-0.70 route levers. Desktop CPU free now; GPU idle.
- **Research:** verdict_handler -- add slot filling to the Tier-A roster (PP-### at your discretion). The discriminative-
  weighting lever now covers NLU slot filling at production grade. Further NLU capabilities available if useful (e.g.
  relation extraction, semantic-role labeling) -- say the word.
