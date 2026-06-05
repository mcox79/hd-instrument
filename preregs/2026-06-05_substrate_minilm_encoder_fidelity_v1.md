# Prereg: substrate_minilm_encoder_fidelity_v1
## Anchor
substrate_minilm_encoder_fidelity_v1
## Routing
PHASE4A-1: MiniLM (22M sentence-BERT) as substrate encoder vs Pythia; substrate recall + VQ separability at V_c sweep. GPU $0.
## Bands
HARD-PASS MiniLM recall>=0.80 + within 5pp Pythia. MIDDLE>=0.70. HARD-FAIL<0.60.
Smoke: minilm 1.0 = pythia 1.0 -> HARD_PASS (drop-in encoder confirmed).
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
