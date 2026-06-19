# Exp-Dev -> Research: HP-1 + HP-2 + HP-4 all HARD_PASS (scale-up + reasoning-reframe wins)

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator + User  **Date:** 2026-06-05 ~11:00

## Three high-priority cells landed (all at Pythia tier, $0):
- HP-1 long-conversation-scale: HARD_PASS. Substrate 1.00 recall at ALL depths through 1000 exchanges (5 threads);
  Pythia 0.38@50 -> 0.12@500 -> 0.00@1000. Categorical memory win scaled 5x. Demo-grade.
- HP-2 multi-doc 1000+: HARD_PASS. Substrate needle 1.00 + EXACT synthesis-aggregate (counted 33/33 items with a
  value -- Pythia cannot scan 1000 docs) vs Pythia windowed-RAG 0.05. Scales the multi-doc win 300->1000.
- HP-4 substrate-MAX for REASONING: HARD_PASS + IMPORTANT REFRAME. The cleanup/iterate/extctx variants that HURT or
  no-op'd at next-concept-LM HELP reasoning massively: cleanup-iterate traverses 13.5 hops where plain-iterate drifts
  at hop 0 (13.5x); SAME cleanup is a no-op for 1-step LM (0.912 = 0.912). => the substrate-MAX variants are REASONING
  mechanisms, not generation mechanisms. This resolves the EX-CONCEPT LM-negative as a TASK-MISMATCH, not a substrate
  weakness: substrate is a memory+reasoning core; the variants amplify reasoning depth, not token generation.

## Strategic: the 5/7 categorical wins now have SCALE evidence (1000-exchange memory, 1000-doc synthesis) + the
substrate-MAX variants have a proven home (reasoning depth). Remaining HP cells: HP-3 (30-day continual stream),
HP-5/6. Phase 2 (Llama-1B) pending Testbed npz -- Tier-4-Llama replication is the critical next test.
**END.**
