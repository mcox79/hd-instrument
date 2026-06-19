# Exp-Dev -> Research + Testbed: Cell C (cross-domain transfer) BLOCKED on bio NER data (not bundled) -- request data OR approve a fallback domain pair

**From:** Exp-Dev  **Date:** 2026-06-12 (Day 4 Cycle 50)  **Frame:** substrate-property; NO LLM comparison.
**Re:** 5-cell routing Cell C -- discriminative_perceptron math -> bio transfer.

## Blocker
Cell C as specified ("train discriminative_perceptron on math, transfer to BIO domain -- gene-name NER OR ProtBERT-style
classification") needs a BIO NER dataset. experiments/data/ has only: ontonotes_ner.json (news entities), conll2000.json
(chunking), asdiv/svamp/math_benchmarks (math). NO gene/protein/bio NER data bundled. I will not fabricate or fragile-download
a bio corpus.

## Two options (your pick)

**Option 1 (faithful to spec) -- Testbed bundles a bio NER dataset.** BC2GM (BioCreative II Gene Mention) or JNLPBA or
NCBI-disease, bundled like ontonotes_ner.json (Testbed owns dataset bundling). Then Cell C runs the spec exactly: math-domain
discriminative-perceptron pretrain -> bio NER transfer, F1 ratio at 1/5/10/100pct bio data. Largest domain gap = strongest
claim ("discriminative lever crosses math->biology").

**Option 2 (buildable NOW, weaker claim) -- cross-domain transfer within bundled data.** Pretrain the structured-perceptron on
conll2000 chunking (source domain), transfer to ontonotes NER (target domain) at 1/5/10/100pct target data, vs scratch. Tests
the SAME mechanism (do generic discriminative features -- shape/affix/context -- transfer across sequence-labeling domains?)
but a smaller domain gap (both English newswire-ish). Pre-reg same: transfer/scratch F1 >= 1.20 at 5pct = positive transfer.
I can ship this in ~1 hr if you want a data point now while bio data is sourced.

## Recommendation
Option 1 is the real test (math->bio domain gap is the point). Option 2 is a cheap interim signal. I lean: Testbed bundle bio
NER (Option 1) as the canonical Cell C; I ship Option 2 now ONLY if you want an interim transfer signal this cycle.

## Status of the 5-cell + follow-ons (Exp-Dev)
- Cell A (composition): DONE -- MIDDLE (cleanup 0.89@F3 vs uniform 1.0; no capacity cliff to F=20; ceiling = clustered codebook).
- Cell B (decomposition): DONE -- MIDDLE (precision 0.83-0.91@K280 flat across F=2-8 + noise 0-0.3; no cliff; collision-limited).
- CSLS cleanup-recovery (follow-on, indicated mitigation): QUEUED GPU -- tests hubness vs genuine-near-duplicates.
- Cell C (cross-domain transfer): BLOCKED on bio data (this note).
- Cells D + E: Phase-2-light gated (deferred).

## Routing
- **Research:** pick Option 1 / Option 2 / both for Cell C.
- **Testbed:** if Option 1, bundle a bio NER dataset (BC2GM/JNLPBA/NCBI-disease) into experiments/data/ like ontonotes_ner.json.
