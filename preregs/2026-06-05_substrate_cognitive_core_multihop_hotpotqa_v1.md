# Prereg: substrate_cognitive_core_multihop_hotpotqa_v1
## Anchor
substrate_cognitive_core_multihop_hotpotqa_v1
## Routing
CCC-1-v2 multi-hop-factual (HotpotQA). PRIMARY: substrate 2-hop supporting-fact retrieval recall@2 vs 1-hop. SECONDARY (Pythia-ceiling): end2end EM. GPU $0.
## Bands
HARD-PASS 2hop_recall>=0.5 AND >=1.2x 1hop. MIDDLE recall>=0.4 OR ratio>=1.1. HARD-FAIL else.
Smoke: 2hop=0.25 1hop=0.21 ratio=1.20x (Pythia-160M weak embeddings cap absolute recall) -> MIDDLE. Revisit Llama-1B Phase 2.
## Queue
overnight_queue timeout 14400s. PROT-022 PASS.
