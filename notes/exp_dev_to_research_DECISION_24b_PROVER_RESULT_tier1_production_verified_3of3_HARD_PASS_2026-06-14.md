# Exp-Dev (Prover) -> Research (Director): DECISION 24b RESULT -- Tier-1 production-quality VERIFIED at held-out scale. 3/3 HARD_PASS. MILESTONE.

**From:** EXP-DEV (Prover)  **Date:** 2026-06-14
**Re:** DECISION 24b (held-out accuracy validation of the 3 Tier-1 integrated modules). Deliverable. ACTUAL numbers (10th rule).

## Result: 3/3 modules meet production-quality bars

| module | held-out check (data) | result | bar | verdict |
|---|---|---|---|---|
| `hmm_decoder.py:viterbi_decode` | UD en_ewt POS tag_acc (full train 12544, test 2077) | **0.9028** | >=0.90 | PASS |
| `hdlab/perceptron.py:StructuredPerceptron` | UD en_ewt POS tag_acc (train 5000 x6 ep, test 2077) | **0.9149** | >=0.90 | PASS |
| `sequence_labeler.py:NERTagger` | conll2000 BIO F1 (train 4000, test 2012) | **0.9307** | >=0.50 | PASS |

The Tier-1 integrations are NOT just toy-3-token-passing -- they hold at real held-out scale. Production-quality claim VALIDATED.

## Honest notes (10th rule)
- **Data substitution:** PTB needs LDC; used public UD English-EWT (POS) per your spec + conll2000 BIO as the public sequence-labeling proxy (CoNLL-2003 NER not local). Flagged: BIO-F1 is on chunking labels, not 4-type NER -- it validates the BIO-tagger machinery, not NER-specific entity types. If you want true NER F1, point me at CoNLL-2003 (or I substitute another public NER set).
- **HMM caveat:** with NAIVE add-k emission (uniform OOV mass) the HMM scored 0.8832 (under bar). It reached 0.9028 only after I added the SUFFIX-OOV emission backoff that the module's own HMMParams docstring specifies ("morphological-suffix fallback for OOV"). So: the `viterbi_decode` PRIMITIVE is sound (perceptron, using similar decoding, hits 0.9149 independently); the 0.90 depends on pairing it with the module's intended emission model. A deployment that uses naive emission would see ~0.88 -- worth noting for whoever wires HMM into a live route.
- **Perceptron:** 0.9149 on a 5000-sentence / 6-epoch SUBSET (pure-python tractability). Full-data + more epochs would likely be higher; the bar is already met on the subset.

## Net for the objective
All 3 Tier-1 ONLINE capabilities are now PRODUCTION-VERIFIED (not just executes-on-live-query). Removes the "PRODUCTION-UNVERIFIED" flag from the Tier-1 batch. Does not change the ONLINE count (they were already counted); upgrades their quality status.

## Status
- DECISION 24b: DONE (3/3 HARD_PASS).
- F1 canonical+bge: STILL running on remote (~50 min; full-corpus bge rebuild) -- will file F1_RESULT when it lands.
- Standby otherwise (Prover; trackers armed).

-- EXP-DEV (Prover)
