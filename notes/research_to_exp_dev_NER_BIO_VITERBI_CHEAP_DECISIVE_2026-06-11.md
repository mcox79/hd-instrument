# Research -> Exp-Dev: NER Path 1 BIO-Viterbi cheap decisive test (<1hr CPU)

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** NER 3-datapoint plateau drill back; 0.58 is FLOOR not ceiling

## NER plateau drill verdict

**0.58 F1 is NOT substrate-architectural ceiling. It is classical-features-without-structured-decoder FLOOR.**

Substrate POS reaches 0.95 via HMM+Viterbi (structured decoder). Substrate NER uses per-token argmax (UNSTRUCTURED). Adding BIO-Viterbi structured decoder = expected substantial lift.

5 untested substrate-only paths. Path 1 cheap decisive.

## Path 1 BIO-Viterbi test (<1hr CPU)

Build:
- Reuse existing substrate NER discriminative perceptron emissions
- Add BIO-constraint Viterbi decoder (B-tag, I-tag, O-tag transitions enforced)
- Re-decode on CoNLL-2003 dev set

Target: F1 >= 0.65 (significant lift from 0.58 floor)
Cost: <1hr CPU
Outcome: decisive on whether unstructured-decode was the bottleneck

## Decision matrix

| Outcome | Implication |
|---|---|
| F1 >= 0.65 | BIO-Viterbi confirmed as missing decoder; stack Path 2-5 to push toward 0.75+ |
| F1 0.58-0.65 | BIO-Viterbi partial; need richer features (Path 2 Brown clusters substrate variant) |
| F1 < 0.58 | Decoder integration broke emissions; investigate |

NO pre-registered defeat per drill-defeatism rule.

## Path 2-5 stacking (after Path 1 confirms)

Per drill ranking + substrate-CRF universal drill convergence:
- Path 2: substrate-native Brown clusters via Layer 3 algebra-vec
- Path 3: Cascade NER via PP-379 POS tagger
- Path 4: substrate-CRF tree-decoder (per universal drill)
- Path 5: phrase-cluster features

Stacked predicted lift to F1 >= 0.75 (P_deflated=0.42).

## Connects to substrate-CRF universal library

Substrate-CRF library (drill P=0.55; 4-6hr CPU pilot) collapses 11 task rows to 1 primitive. NER would be one of 11 unified tasks. Path 1 BIO-Viterbi validates the structured-decoder unification empirically; library build extends to NER + 10 other tasks.

Recommend: Path 1 BIO-Viterbi <1hr CPU FIRST (decisive on plateau); substrate-CRF universal library AFTER (consolidates).

## Per drill-defeatism rule

"Plateau at 0.58" was defeatism trap. Empirical test reveals it was unstructured-decode floor, not architectural ceiling. Same pattern as today's other rule applications: don't accept boundary without exhausting untested substrate-only paths.

## Cross-references
- NER drill back: notes/research_drill_ner_3datapoint_plateau_substrate_paths_2x_2026-06-11.md
- Substrate-CRF universal: notes/research_drill_substrate_CRF_universal_nl_2x_2026-06-11.md
- POS discriminative perceptron (Tier A 0.9499 via Viterbi+Collins): cycle 235 PP-379
- Cycle 236 NER datapoints (LVH-288 gazetteer; LVH-289 seed2)

---

**Exp-Dev:** NER Path 1 BIO-Viterbi cheap decisive (<1hr CPU). Target F1>=0.65 from 0.58 floor. 0.58 was unstructured-decode FLOOR not architectural ceiling per drill. Stack Path 2-5 if Path 1 confirms. Substrate-CRF universal library afterwards consolidates 11-task unification.
