# Prereg: e1_substrate_crf_shared_lib_cpu_v1
**Date:** 2026-06-12  **Lane:** CPU  **Routing:** Research APPROVED E1 big next build (UNROUTED inventory).
Shared Tier-1 feature library = distributional clusters (k-means on PPMI context vectors; Brown-cluster proxy) + gazetteer, added
to structured-perceptron+Viterbi NER. A/B baseline vs +library, n=3 seeds, FULL OntoNotes train. Tests whether the reusable library
lifts NER F1 at full data (per aux-features-shrink memory, may saturate). SCOPE: 4-type NER (9 tags, tractable), NOT 18-type -- flagged.
HARD-PASS lift-2SE >= +0.03. MIDDLE 0 to +0.03 (saturates). HARD-FAIL <= 0 (subsumed by lexical features). Smoke lift +0.042 (small-data).
