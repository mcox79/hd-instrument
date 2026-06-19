# Prereg: substrate_hallucination_robustness_hard_negatives_v1
## Anchor
substrate_hallucination_robustness_hard_negatives_v1
## Routing
GPU KF-1 follow-on: hallucination grounding robustness across negative-hardness tiers (easy/hard-same-domain/adversarial-shuffle). MiniLM GPU $0.
## Bands
HARD-PASS AUC_hard>=0.90. MIDDLE 0.75-0.90. Smoke: easy 0.996, hard 0.975 (HP), adv 0.217 (MiniLM order-insensitivity, not brittleness).
## Queue
overnight_queue 14400s.
