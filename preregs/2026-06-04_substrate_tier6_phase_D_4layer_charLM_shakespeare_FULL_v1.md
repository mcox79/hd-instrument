# Prereg: substrate_tier6_phase_D_4layer_charLM_shakespeare_FULL_v1
## Anchor
substrate_tier6_phase_D_4layer_charLM_shakespeare_FULL_v1
## Routing
overnight_priority (Priority 1A, #1 GPU). Tier-6 Phase D FULL: substrate-hybrid 4-layer char-LM (substrate-Hebbian
attention, no backprop) + gradient head vs full-gradient baseline. Shakespeare. torch GPU, $0.
## Pre-registered bands
HARD-PASS BPC<=1.20x baseline AND speedup>=2.0x AND audit operational. MIDDLE BPC[1.2,2]x OR speedup[1,2]x. HARD-FAIL BPC>2x OR slower.
## Smoke gate
GPU smoke: BPC ratio=1.05x (PASS), audit=True; speedup ~1x at smoke (GPU; emerges at full 600-step scale). CPU full run (parallel) showed 1.98x speedup.
## Queue
overnight_queue timeout 21600s. PROT-022 self-tests PASS (remote). Corpus on runner.
