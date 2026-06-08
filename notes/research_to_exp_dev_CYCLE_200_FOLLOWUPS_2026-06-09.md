# Research -> Exp-Dev: cycle 200 follow-up CPU anchors

**From:** Research  **Date:** 2026-06-09 ~07:30 UTC
**Re:** User asked if all high-priority CPU experiments routed. Audit found these cycle 200 follow-ups missing.

## PP-215 noise robustness MID rescue

**F1: top-k rescue (PP-110 pattern)**
- Substrate-product reading: cycle 200 PP-215 MID at 0.758 recall under 30% bit-flip; PP-110 top-k pattern lifts to near-perfect per orchestrator note
- HARD-PASS: top-k recall ≥ 0.95 at 30% bit-flip; graceful degradation through 50%

## PP-212 fast-tier latency at production scale

**F2: substrate-only conversation latency at scale**
- Substrate-product reading: cycle 200 PP-212 P95=0.64ms at small KB; extend to 100K (post-Q2) and 1M scale
- HARD-PASS: P95 < 5ms at 100K; < 50ms at 1M

## PP-216 projection quality across encoders

**F3: encoder-agnostic ingest validation**
- Substrate-product reading: cycle 199 PP-216 cosine corr 0.987 for one encoder; verify across bge-large/e5-large/bge-small/sentence-transformer family
- HARD-PASS: cosine corr ≥ 0.95 for ALL tested encoders

## PP-213 substrate-as-SAT-checker extension

**F4: harder constraint problems**
- Substrate-product reading: cycle 200 PP-213 graph coloring 100% on small; extend to 100-vertex graphs + Sudoku-class problems
- HARD-PASS: 100-vertex coloring agreement ≥ 0.95 with SAT solver

## PP-181 gap-score VALIDATED multi-seed

**F5: gap-score 3-seed promotion**
- Substrate-product reading: cycle 195 PP-181 MID-HP single-seed AUC=0.781; multi-seed for VALIDATED
- HARD-PASS: 3-seed mean AUC ≥ 0.80 + variance < 0.02

## PP-208 PACER full-scale extension

**F6: PACER 10000-case scale**
- Substrate-product reading: cycle 200 PP-208 1000-case at 0.999/1.000; extend to 10000 cases for VALIDATED promotion
- HARD-PASS: recall ≥ 0.99 + precision ≥ 0.99 at 10K cases

## PP-209 DDI extension

**F7: drug-interaction at FDA-grade scale**
- Substrate-product reading: cycle 200 PP-209 100% on test set; extend to full DrugBank (~10K-100K interactions)
- HARD-PASS: recall ≥ 0.95 at scale; audit chain per prediction

## PP-194 counterfactual axiom-exclusion real domain

**F8: counterfactual scenarios real-domain**
- Substrate-product reading: cycle 198 PP-194 + cycle 196 PP-172 20/22 scenarios; extend to economic policy or medical intervention real domain
- HARD-PASS: counterfactual reasoning correct ≥ 0.85 vs ground truth

## PP-200 1-bit at production-scale extension

**F9: 1-bit substrate at 100M facts**
- Substrate-product reading: cycle 198 PP-200 1-bit ≥ float32 quality + 16x memory; extend to 100M-fact production scale
- HARD-PASS: 1-bit quality matches float32 ± 0.03 at 100M facts

## PP-204 multi-seed Tier 5c Phase B

**F10: T5C-B1 3-seed promotion to VALIDATED**
- Substrate-product reading: cycle 199 PP-204 single-layer Flamingo HP-SMOKE ppl_ratio=1.181x single seed; 3-seed for VALIDATED
- Tier: LOCAL GPU after T5C-C1+D1 complete
- HARD-PASS: 3-seed mean ppl ratio < 1.5 + std < 0.1

## Sequencing

**Now (CPU; runs alongside Q2 ingest):**
- F1 (noise robustness top-k; cycle 200 MID rescue)
- F2 (latency at scale; requires Q2 to complete first)
- F3 (encoder-agnostic ingest)
- F5 (gap-score multi-seed)
- F4 (SAT-checker extension)
- F6 (PACER 10K scale)
- F7 (DDI FDA-grade scale)
- F8 (counterfactual real-domain)

**Post-Q2 (CPU; uses 100K KB):**
- F2 latency at 100K + 1M
- F9 1-bit at production 100M scale (post-Q2 if KB allows)

**Post-Tier 5c Phase D (GPU):**
- F10 T5C-B1 3-seed VALIDATED

## Audit answer for user

**~120+ CPU anchors total routed today across 10 batch notes (including this one).**

CPU is currently bottlenecked by Q2 Wikipedia ingest (8-hour run; bge-large encoder + spaCy NER dominate CPU). Queue runners still draining the backlog in parallel but at reduced throughput.

**No critical CPU experiments are blocked on routing.** Throughput is operational (Q2 ingest sharing CPU), not strategic (routing complete).

## Cross-references
- BATCH 3: notes/research_to_exp_dev_BATCH_3_FRESH_30_ANCHORS_2026-06-08.md
- BATCH 4: notes/research_to_exp_dev_BATCH_4_CRITICAL_2026-06-08.md
- Cycle 200: notes/orchestrator_to_research_results_summary_2026-06-08_cycle200.md
- Cycle 199: notes/orchestrator_to_research_results_summary_2026-06-08_cycle199.md
- Cycle 198: notes/orchestrator_to_research_results_summary_2026-06-08_cycle198.md

---

**Exp-Dev:** 10 cycle-200 follow-up anchors. F1 noise top-k rescue closes PP-215 MID.
F5 gap-score multi-seed closes PP-181 → VALIDATED. F4 SAT-checker extension extends
PP-213. F6 PACER 10K + F7 DDI scale + F8 counterfactual real-domain extend vertical
demos. F10 T5C-B1 3-seed waits for Tier 5c Phase D completion (GPU).

All CPU-friendly; will run alongside Q2 Wikipedia ingest naturally.
