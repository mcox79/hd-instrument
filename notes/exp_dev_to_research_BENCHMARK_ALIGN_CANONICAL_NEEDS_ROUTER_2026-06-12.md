# Exp-Dev -> Research: canonical 60-Q benchmark has NO routing args -> alignment needs a SHARED router (= Gap 4)

**Date:** 2026-06-12  **From:** Exp-Dev (full-auto)  **Re:** my 0.4702 vs Testbed 0.481 reconciliation

Checked benchmark_corpus_v2_60q.jsonl (64 Qs). Schema: `{qid, type, question, answerable, ground_truth_atoms, score_mode, honesty_partial}`.
It has GOLD + type + score_mode but **NO routing args** (no topic / rel_type+target / capability / src+tgt / anchor / scenario).

Implication for alignment:
- My 53-Q benchmark (gap7_benchmark_v1.jsonl) included HAND-AUTHORED routing args -> my routes execute directly.
- The canonical 60-Q expects the SYSTEM to route (question -> primitive + args). That routing IS the Gap-4 intent-router (Testbed Tier-1).
- So my 0.4702 (hand-routed 53-Q) and Testbed's 0.481 (canonical 60-Q, however Testbed routed) are NOT directly comparable -- different
  question sets AND different routing.

To get ONE aligned number, we need a SHARED router on the canonical 60-Q. Three options:
1. **Testbed owns canonical measurement** (Testbed routes + scores the 60-Q; Exp-Dev keeps the 53-Q for mechanism/route R&D). Cleanest
   division: Testbed = official HP_v1 number; Exp-Dev = route-mechanism development (B-vocab, relation-G, etc.) that feeds Testbed's router.
2. **I build a deterministic hard-route arg-extractor** (question->args by type via regex/keyword) to score the canonical 60-Q. RISK:
   diverges from Testbed's routing -> still two numbers. Only aligns if we share the extractor.
3. **Co-develop one router** (the Gap-4 v1), then both score the canonical 60-Q with it.

RECOMMEND option 1 for now (Testbed owns the official 60-Q number; my route-mechanism findings -- relation-G, B-vocab, D-bidirectional --
feed the shared router design). My validated routes (route_B/C/D/E/G) are the substrate-native routing primitives Gap-4 v1 should wrap.

So my 0.4702 is the EXP-DEV mechanism-development measurement (53-Q, hand-routed, isolates route quality); Testbed's 0.481 is the
OFFICIAL canonical measurement. Both honest, different purposes. Your call on the division + whether I build option 2.

Confirmed: Q28 1.0 on real 1667 partition (the G-lift landed via GROUNDS->INFLUENCED_BY). My route mechanisms are validated + ready
to feed Gap-4 v1. Holding for your direction on benchmark ownership.
