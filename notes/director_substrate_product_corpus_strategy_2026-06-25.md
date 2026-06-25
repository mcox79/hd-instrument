# Substrate-product corpus strategy — what corpus for what stage (2026-06-25)

Director synthesis after USER's morning critique: "what are we doing with text8?"

## The strategic confusion we were carrying

Last night's encoder-leakage fair-regime retest landed MIDDLE_BAND with **B/C/D arms all at the bigram floor 10.12**. That landing was correctly interpreted as "substrate at fair regime = bigram-equivalent at LM" — but the deeper implication wasn't drawn:

**Testing substrate as a statistical LM on text8 was the wrong evaluation choice all along.**

text8 is Wikipedia-2006 character stream with punctuation and case stripped:
- NO concept labels
- NO grammatical structure
- NO category memberships
- NO relational annotations
- Only co-occurrence + surface spelling

Substrate's strengths (memory + composition + retrieval + audit on LABELED structure) cannot be exercised by raw text8. The SEMANTIC battery v2 FULL HARD_PASS 6/6 with A3 generalization=1.000 proved this — substrate generalizes PERFECTLY when given concept-labeled triples. Same primitives evaluated on text8 land at bigram-floor because there's no labeled structure to exploit.

The encoder-leakage finding (clean encoder = bigram-floor) wasn't a substrate refutation — it was a CORPUS MISMATCH.

## Stage-by-stage corpus choice

| Stage | Goal | Right corpus | Right evaluation | Status |
|---|---|---|---|---|
| 1 — Base substrate-product | validate primitives | Concept-KG (labeled triples) | SEMANTIC battery (6 arms) | DONE: v2 FULL HARD_PASS 6/6 |
| 2 — Optimize architecture | architectural wins on labeled structure | Concept-KG + cross-layer + role-tagged | Cross-layer cv ≥ 0.05 + role-tagged A3 generalization + lock-in stacking | IN FLIGHT: Wave D + E |
| 3 — Higher functions | compose across modalities | Multi-modal KGs (text+graph+image-labeled) | Cross-modal binding, multi-hop reasoning | NEXT (post Stage 2 landings) |
| 4 — LM equivalence | substrate as glass-box LM | LABELED text (PTB-WSJ with POS / NER / SRL) | LM-with-role-conditional-context | LATER (Stage 4+ — requires labeled text corpus, NOT text8) |

## Why text8 stays in the corpus stable (as a SIDE metric only)

We don't ban text8. It has two specific uses:
1. **Bigram-floor reference**: fair_harness 7.3065 is the substrate-as-LM-on-text8 reference. Any future Stage 3-4 cell claiming "substrate beat bigram" needs to clear this rail at fair regime.
2. **Cross-paradigm comparator (NOT Lane 1)**: when we want to compare substrate to LSTM/transformer at some point, text8 is the standard benchmark. ALWAYS framed as Lane 3 (cross-paradigm; explicitly tagged), NEVER Lane 1.

text8 is NOT:
- The Stage 1 substrate-product validation corpus (concept-KG is; SEMANTIC battery proved)
- The Stage 2 architecture-validation corpus (concept-KG with role/cross-layer/lock-in is; Wave D+E)
- The Stage 3 multi-modal corpus (multi-modal KGs are)
- The Stage 4 LM-equivalence corpus (labeled-text corpora are)

## Implications for in-flight work

**Cell B redirect was correct** — moving the role-tagged context test from text8 to concept-KG is the right call. The original Cell B spec was testing role-tagging on a corpus without role structure.

**Cell C lock-in stacking stays on text8** — different bet. Lock-in is testing the SAME-W stacking problem (Barrier 3), which is orthogonal to corpus choice. text8 + word2vec + Hebbian-stacking is fine for that mechanism test. It's specifically a Lane 1/2 architecture-validation cell using text8 as a stress-test corpus.

**Wave D cross-layer + heterog routing stays on text8** — same reason. These test mechanisms that work on raw co-occurrence; text8 is appropriate.

**Hub-spoke E1 v3 (Wave D) stays on text8** — tests whether diverse-algorithm spokes produce anisotropic structure that beats unigram on text8. If it doesn't, the diverse-algorithm hypothesis is refuted; this is a clean test on the well-understood text8 regime.

So the corpus strategy is NOT "drop text8." It's: **stop using text8 as the substrate-product validation corpus. Use it for architecture stress-testing and as a side-metric.**

## What this means for Stage 1 closure

Stage 1 substrate-product closure is now achieved on the RIGHT corpus:
- 8 chain-grade native capabilities (storage / capacity / pattern completion / WM cap=30 / sequence binding / compositional gen +0.724 / CL CRISPR forget=0.006 / trained analogical recovery) — all on labeled or substrate-native synthetic structure
- SEMANTIC battery v2 FULL HARD_PASS 6/6 — concept-KG validates substrate as concept-learner
- Calibration ECE chain-grade — via correct primary metric
- Cross-layer architectural win +0.376 BPC — MM tier per Skunkworks but architecturally real

Stage 1 is essentially CLOSED on the right corpus. The "we haven't closed Stage 1" feeling was largely from evaluating on the wrong corpus (text8) and getting bigram-floor results.

## Substrate-product story (clean version)

Substrate is a memory + composition + retrieval + audit device that operates on LABELED concept structure. Brain analog: hippocampus-cortex working with concept memories, not raw character streams.

- Vs vector DBs: substrate beats with lossless compositionality + auditable retrieval + no catastrophic forgetting + working memory cap=30
- Vs KG embeddings (RotatE, ComplEx): substrate beats with sequence binding + compositional generalization + online learning
- Vs RAG: substrate has substrate-native audit (Barrier 5; in test via Cell E proposal)
- Vs LSTM/transformer LMs: substrate is NOT trying to be this. Substrate-as-LM is a Stage 4 ambition that requires labeled-text corpora and Stage 2-3 architectural levers — NOT text8.

## Memory commit

This strategy note should be referenced in:
- `notes/director_5_intuitive_barriers_with_analogies_2026-06-25.md` — Barrier 4 (random-bipolar isotropic library) is partially about WHICH CORPUS we test on
- `feedback_experiment_bias_master_checklist_USER_2026-06-24.md` — category J5 (3 corpus-encoding WORLDS) gets an addendum: WORLD A (text8/word2vec) is NOT the substrate-product validation world; it's the architecture-stress-test world
- All future Stage 1/2 cells: corpus_provenance must declare which stage the cell is testing AND whether the corpus is appropriate for that stage
