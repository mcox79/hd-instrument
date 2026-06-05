# Prereg: substrate_cognitive_core_counterfactual_v1
## Anchor
substrate_cognitive_core_counterfactual_v1
## Routing
CCC-1-v2 counterfactual capability dim: inference-time fact-update (cf-RPE overwrite) vs Pythia-160M in-context. GPU $0.
## Bands
HARD-PASS substrate updated >=2x Pythia AND retention>=0.90. MIDDLE >=1.2x. HARD-FAIL <1.2x.
Smoke: substrate updated 1.00 (retention 1.00) vs Pythia 0.00 -> HARD_PASS (Pythia cannot inference-time update).
## Queue
overnight_queue timeout 7200s. PROT-022 PASS.
