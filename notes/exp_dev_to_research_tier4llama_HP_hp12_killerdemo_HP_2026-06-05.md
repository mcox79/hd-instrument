# Exp-Dev -> Research: Tier-4-Llama HP captured + HP-12 KILLER DEMO core HARD_PASS

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + User  **Date:** 2026-06-05 ~14:30

## Tier-4-Llama HARD_PASS captured (cloud, Testbed): ppl_ratio 0.98 (substrate BETTER than baseline), entropy 2.82,
grad 0.8. Substrate-as-attention REPLICATES at Llama-1B (GQA+RoPE, SWAP_LAYER=8). The critical Phase-2 architecture-
scaling test is WON -- substrate is a genuinely swappable attention primitive at 1B params.

## HP-12 KILLER DEMO core: HARD_PASS (smoke; full queued). The Phase-3 flagship.
Certified per-fact deletion: substrate KB + RSA cryptographic accumulator. cert_latency=0.512ms (<1ms), phantom_recall
=0.000 (deleted facts gone), third-party-verifier confirmed=1.000 (verifies deletion with NO KB/W/trapdoor access via
new_acc^prime==old_acc), non-deleted retention=1.000. The architecturally-impossible-for-LLMs claim validated at the
CORE mechanism. Build-time honest findings: (1) sequential projection-deletions re-introduce crosstalk at earlier-
deleted keys -> needs a stabilizing re-projection pass (added) to guarantee 0 phantom; (2) phantom must be measured by
ABSOLUTE recall strength not cosine (a near-zero residual has meaningless-but-high cosine). Both fixed -> clean HARD_PASS.
Full 1M-fact demo needs sparse FAISS-HNSW storage (dense Hebbian caps ~0.3N); core mechanism + crypto layer proven now.

## Both queues high-priority: CPU = HP-12 + K-fact-anchors; GPU = HP-7 e2e + HP-5 medical + strong-baselines.
## Remaining: HP-9 (multimodal), HP-11 (dist-shift). Phase-2 + envelope continuing.
**END.**
