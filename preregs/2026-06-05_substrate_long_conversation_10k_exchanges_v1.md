# Prereg: substrate_long_conversation_10k_exchanges_v1
## Anchor
substrate_long_conversation_10k_exchanges_v1
## Routing
HP-8: long-conv memory at 10,000 exchanges (10x scale of HP-1). Substrate vs Pythia-160M. GPU $0.
## Bands
HARD-PASS substrate>=0.85 at deepest AND Pythia<=0.05. MIDDLE 0.60-0.85. HARD-FAIL <0.60.
Smoke: substrate 1.00 at d50/d2000/d9000 (E=10000); Pythia 0.0 all -> HARD_PASS. Batched-Hebbian (sequential cf-RPE too slow at 10k).
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
