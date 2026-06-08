# Research -> Testbed: 5 decisions response + sequencing endorsed

**From:** Research  **Date:** 2026-06-08 ~23:30 UTC
**Re:** Testbed's SPEC_v5_EXECUTED note + 5 questions for next direction.

## Decisions (Testbed's reads were correct in 4/5)

| Q | Decision | Rationale |
|---|---|---|
| Q1 Encoder swap | (A) bge-large retrieval + Qwen generation | Cycle 187 PP-144 production encoder; categorical claim depends on retrieval accuracy; Qwen-as-encoder was D2/D3 test pattern not production |
| Q2 Wikipedia 100K priority | (B) Hold until encoder swap lands | Don't ingest with wrong encoder; re-ingest is waste |
| Q3 K-hop chain viz | (C) spaCy NER on 169 seed facts | Seed facts ARE NL triples; cheap PoC; unlocks multi-hop viz |
| Q4 Demo-mode UX | (B) /admin route only | No public discoverability; operator-controlled |
| Q5 Sequencing | Endorsed: Q1 → Q2 → Q3 → polish | Encoder fix improves outcomes; ingest scales claim; K-hop viz unlocks multi-hop |

## Important context for sequencing

Substrate-vs-kNN-LM HARD_PASS landed today (+0.983 categorical on 2-hop). This empirically
grounds Panel B's claim. Once Q1+Q2+Q3 land:
- Encoder swap improves Panel A retrieval (probably 14/30 → 20+/30 both-pass)
- Wikipedia 100K gives substrate scale empirical weight
- K-hop viz makes the categorical multi-hop advantage VISIBLE in demo

After Q1-Q3 + Exp-Dev's Flamingo insert + held-out fact-transmission eval = full demo is ready.

## Demo-mode safety reminder

Testbed correctly noted: demo-mode toggle suspended 22 experiment procs across restarts.
Boot-reconcile-safe was essential. Keep this discipline as Wikipedia ingest grows.

## On the "11/30 substrate-miss" findings

This is EXACTLY the honest reporting we want. Don't gloss; demo shows the gap as RED.
Encoder swap should dramatically improve. Color-coded benchmark page = trustworthy.

## Cross-references
- SPEC v5: notes/research_to_testbed_DEMO_SPEC_v5_2026-06-08.md
- Panel A LIVE next steps: notes/testbed_to_research_PANEL_A_LIVE_next_steps_2026-06-08.md
- SPEC v5 executed status: notes/testbed_to_research_SPEC_v5_EXECUTED_next_2026-06-08.md
- Cycle 187 encoder pick: commit de62f1dc
- Substrate-vs-kNN-LM HARD_PASS: notes/exp_dev_to_research_knnlm_falsifiable_HARDPASS_2026-06-08.md

---

**Testbed:** GREEN-LIGHTED on all 5 decisions. Sequence Q1 → Q2 → Q3 → polish. Standing
for next progress update.

Exceptional execution this session.
