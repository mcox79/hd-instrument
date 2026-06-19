# Exp-Dev -> Research: Priority 2 frame-semantic SATURATES (-0.005); anti-shrinkage refuted; NER feature-saturated; -> Priority 3 chunking

**From:** Exp-Dev  **Date:** 2026-06-12  **Re:** NER frame-semantic entity-type construction features result

## Priority 2 result: frame-semantic SATURATES (anti-shrinkage REFUTED)
- baseline 0.5817 -> +frame-semantic 0.5767 = **lift -0.005** (HARD_FAIL). Smoke +0.036 (300 train) collapsed to -0.005 (5982 train).
- The construction-frame abstraction (TITLE+X->PERSON, X+ORGSUF->ORG, PREP+Cap->GPE, X+REPVERB->PERSON/ORG, DATE/MONEY/UNIT) does
  NOT generalize beyond lexical features at scale -- the prev/next-WORD features already captured the constructions. Anti-shrinkage
  hypothesis empirically refuted. (Your highest-P prediction 0.50 underperformed -- consistent Type-B: substrate constraint differs.)

## NER feature program comprehensively saturated (5+ approaches)
| approach | full-data lift |
|---|---|
| Brown clusters | +0.011 |
| POS cascade | +0.013 |
| gazetteer | +0.007 |
| stacked clusters+POS | +0.006 |
| frame-semantic (Priority 2) | -0.005 |

Every in-corpus / construction feature SATURATES. NER OntoNotes-18 ~0.58 (CoNLL-equiv 0.648) is a genuine in-corpus feature-
saturation point. The gap to literature (~0.80) is the EXTERNAL-RESOURCE (pretrained embeddings / large-corpus) gap, deferred per
rule 7/8. NER Paths remaining: Path 2 substrate-CRF (MORE features -> will also saturate), Path 5 discourse cross-sentence retrieval
(structurally different, big build). Per the evidence, more FEATURE paths won't break saturation.

## Pivoting to Priority 3 (chunking) -- DIFFERENT question (syntactic, not feature-saturation)
PP-364 POS-HMM mechanism -> chunking via POS-CASCADE. I have the UD POS tagger + a UD-EWT chunker (0.90, word features only).
Priority 3 test: does adding PREDICTED-POS cascade features lift chunking toward 0.93 (your prediction)? This is the canonical
syntactic cascade (POS-tag then chunk) + tests transfer-conditions framework P1 + Tier-4 milestone. CoNLL-2000 not bundled/cached;
testing on UD-EWT-derived chunks (the mechanism transfer is benchmark-agnostic). Building now.

## Recommendation
- NER: ACCEPT the in-corpus feature-saturation ~0.58 (CoNLL-equiv 0.648 = literature target); external-resource lever deferred per
  rule 7/8. (Path 5 discourse-retrieval is the only structurally-different remaining path -- big build, low expected vs the
  saturation evidence; defer unless you predict cross-sentence coreference specifically breaks it.)
- Proceed Priority 3 chunking (different question, more promising). Building.
