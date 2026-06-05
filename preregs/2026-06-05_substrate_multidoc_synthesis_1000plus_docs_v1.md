# Prereg: substrate_multidoc_synthesis_1000plus_docs_v1
## Anchor
substrate_multidoc_synthesis_1000plus_docs_v1
## Routing
HP-2: multi-doc synthesis at 1000+ docs (needle + synthesis-aggregate) vs Pythia-160M windowed RAG. Scales win 300->1000. GPU $0.
## Bands
HARD-PASS substrate needle>=0.80 AND synth relerr<=0.10 AND Pythia-RAG<=0.30. MIDDLE needle 0.50-0.80. HARD-FAIL <0.50.
Smoke(300): substrate needle 1.00 + synth exact (33/33) vs Pythia-RAG 0.05 -> HARD_PASS.
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
