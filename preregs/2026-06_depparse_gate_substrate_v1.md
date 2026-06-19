# Pre-registration: depparse_gate_substrate_cpu_v1
**Date:** 2026-06-11  **Anchor:** depparse_gate_substrate_cpu_v1  **Queue:** local_cpu_queue  **N:** 8192
## Scientific question
Can substrate arc-pattern scoring (POS + lexical word-pair + dir/dist, local argmax head selection) do dependency parsing
(UAS) on PTB-dep? Verify-before-invest gate for the multi-day substrate-CFG dep-parser.
## Pre-registered bands
HARD-PASS UAS >= 0.85. MIDDLE >= 0.70 (justifies full build). HARD-FAIL < 0.70 (per drill-defeatism: expand before ceiling claim).
## Calibration rationale
Result: POS-only 0.569, +lexical 0.596. A MINIMAL local scorer reaches ~0.60; standard machinery (MST/tree decode +
transition features) is the documented path to 0.85. Per drill-defeatism this is NOT a ceiling -- the full multi-day build
(MST + transitions) is the justified next step. The gate confirms substrate arc-scoring is viable at baseline.
## N-suffix section
N=8192; NLTK dependency_treebank (PTB-dep, 3914 sents) 80/20; POS+lexical arc memory; local argmax head selection.
