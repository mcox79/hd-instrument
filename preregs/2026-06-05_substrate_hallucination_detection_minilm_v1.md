# Prereg: substrate_hallucination_detection_minilm_v1
## Anchor
substrate_hallucination_detection_minilm_v1
## Routing
Phase 4 Idea 3: substrate grounding/hallucination detector (MiniLM encoder). GPU $0.
## Bands
HARD-PASS AUC>=0.90 + grounded-recall>=0.85 + hallucination-flag>=0.85. MIDDLE AUC>=0.80. HARD-FAIL<0.70.
Smoke: AUC 1.0, recall 1.0, flag 1.0 -> HARD_PASS (grounding detector validated).
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
