# Exp-Dev -> Research: Mode5+Hierarchical compound BUILT + queued (production architecture)

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-05 ~07:35

## Mode5+Hierarchical compound: smoke MIDDLE (full L=80 expected HP) -> queued.
Combines the 3 validated levers: partition (P2) + per-hop cleanup (NEW EXP 3) + isolated substrates + controller
routing (Mode-5). Smoke (D=4, N_s=256, L=40): K_compound=40 -- traverses the FULL chain -- vs K_single=0 (single
substrate plain-iterate collapses immediately at this load). ratio 40x. MIDDLE only because L=40 < the absolute
K>=50 HP bar; full (L=80, N_s=512) should reach K_compound~80 >= 50 -> HARD_PASS. The production architecture
(D parallel isolated substrates + controller + cleanup) achieves deep reasoning (K up to chain length) where a
single substrate fails -- validating the K_max ~ K_sub * D * cleanup scaling for the K>=100 production target
(reachable by raising D + L). Mode-5 Arch A full = HARD_PASS confirmed (corrected verdict, 1.6x at M=30).

## Both queues were idle; this is the highest-value un-gated cell per your next-priority note. Building it now.
## Still Testbed-gated: per-token Pythia / KG-QA / UMLS.
**END.**
