# Prereg: substrate_long_conversation_scale_1000_exchanges_v1
## Anchor
substrate_long_conversation_scale_1000_exchanges_v1
## Routing
HP-1: long-conv memory at 1000+ exchanges, 5 threads, multi-depth recall. Scales categorical win 5x. vs Pythia-160M. GPU $0.
## Bands
HARD-PASS substrate>=0.85 @1000 AND Pythia<=0.05 @deepest. MIDDLE substrate 0.60-0.85. HARD-FAIL <0.60.
Smoke: substrate 1.00 at ALL depths (50/500/1000); Pythia 0.38->0.12->0.00 -> categorical win at 1000 (verdict fixed to compare deepest depth=HP).
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
