# exp_dev hand-off - research: substrate-as-full-research-history-ledger

filed-by: research
date: 2026-06-11
trigger: 2x DEEP drill substrate-as-full-research-ledger; companion to notes/research_drill_substrate_as_full_research_ledger_2x_2026-06-11.md
pause state: respect data/orchestrator_paused.flag - if set, hold all anchors except LEDGER-PILOT-1 (CPU-only, no queue).

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are RANK-ORDERED POINTERS only. Exp_dev owns the build / parameter / smoke discipline. Research provides the substrate-product-reading and the HARD-PASS / HARD-FAIL pre-registration only.

## Anchor candidates (rank-ordered)

### Anchor LEDGER-PILOT-1 (HIGHEST PRIORITY - cheap decisive test) - ~4-8 hr CPU
- Substrate-product reading: end-to-end pilot of substrate-as-ledger on a scaled-down corpus (10 today drills + 10 recent PP rows + their cross-references). Validates 4 substrate-ledger capabilities (Q1 lineage trace + Q2 Layer 4 classifier at corpus scale + Q3 Layer 8 BOCPD drift + Q4 next-drill prediction) BEFORE committing to full 235-cycle ingest.
- Tier hint: Tier-2 cell budget; all-CPU; <= 8 hr wall.
- Why now: full-corpus ingest is the higher-cost commitment; pilot answers go/no-go in one cell.
- Pre-registered HARD-PASS / HARD-FAIL: see drill note section (b) and (g).
- Reads: notes/research_drill_substrate_as_full_research_ledger_2x_2026-06-11.md sections (b) and (g).

### Anchor LEDGER-CAS-DEDUP-2 - ~2-4 hr CPU
- Substrate-product reading: validate P1 (storage+retrieval scaling) on the FULL 850-artifact corpus using read-only CAS hash + merkle-DAG construction. NO substrate ingest yet - just measure deduplication rate + retrieval-time scaling.
- Tier hint: Tier-2; CPU-only; quick win.
- Why now: low-risk infrastructure validation; can run in parallel with LEDGER-PILOT-1.
- Pre-registered: dedup >= 30%, ingest <= 1s/artifact, no substrate-side validation yet.
- Reads: drill note section (c) P1 + (g).

### Anchor LEDGER-ROLLBACK-3 - ~3-6 hr CPU
- Substrate-product reading: validate P2 (tiered rollback semantics) by reconstructing cap_map at 3 known historical checkpoints (cycle ~200 RETRACTION, cycle ~225 PP-225 validation, cycle ~226 polysemy 1.000). Test semantic equivalence on rolled-back state.
- Tier hint: Tier-2; CPU; depends on LEDGER-CAS-DEDUP-2 building the merkle-DAG.
- Why now: rollback is the GDPR-aligned product feature; need empirical proof before claiming.
- Pre-registered: >= 95% semantic equivalence on >= 2 of 3 historical rollbacks.
- Reads: drill note section (c) P2 + (g).

### Anchor LEDGER-SELF-INGEST-SAFETY-4 - ~4-6 hr CPU (load-bearing safety test)
- Substrate-product reading: stress test P5 (bounded-recursion safety) by INGESTING the substrate's own prior substrate-on-substrate analyses (today's drills 2026-06-11 layer4_dialectic + substrate_proposed_architectures + this drill) as Tier-3 archive; measure surprise-classifier F1 drift + cap_map flip rate.
- Tier hint: Tier-2; CPU; should run AFTER LEDGER-PILOT-1 Q2 validates the classifier.
- Why now: P5 is the LOAD-BEARING SAFETY prediction - if it fails, full ledger is unsafe.
- Pre-registered: F1 within +/- 0.05, flip-rate within +/- 0.15%, gate-boundary held (substrate does NOT propose changes to its own classifier methodology).
- Reads: drill note section (c) P5 + (d) cross-thread to substrate-proposed-architectures.

### Anchor LEDGER-FULL-INGEST-5 (FINAL, GATED) - ~12-24 hr CPU
- Substrate-product reading: full ingest of 235+ cap_map cycles + 381 PP rows + 150+ routings + 50+ memory + 32 drills (today) into the substrate-ledger. ONLY after LEDGER-PILOT-1 + LEDGER-CAS-DEDUP-2 + LEDGER-ROLLBACK-3 + LEDGER-SELF-INGEST-SAFETY-4 all HARD-PASS.
- Tier hint: Tier-3 cell budget; CPU; overnight.
- Why now: the production substrate-ledger; this is what the substrate-product feature is built on.
- Pre-registered: P1+P2+P3+P4+P6+P7 HARD-PASS bands all hold on the full corpus.
- Reads: ALL of drill note sections (b)-(g).

## Context pointers (file paths only, no summaries inline)

- notes/research_drill_substrate_as_full_research_ledger_2x_2026-06-11.md - this drill
- notes/research_drill_substrate_proposed_architectures_2x_2026-06-11.md - frozen-gate invariant
- notes/research_drill_layer4_dialectic_methodology_2x_2026-06-11.md - surprise-classifier
- notes/research_drill_substrate_self_discovery_validation_2x_2026-06-11.md - validation filter pipeline
- C:\Users\marsh\.claude\projects\d--AI\memory\substrate_v32_engineered_wrapper_2026-06-11.md - WRAPPER pattern
- C:\Users\marsh\.claude\projects\d--AI\memory\production_architecture_locked_2026-06-07.md - production storage choices
- data/orchestrator_status_log.jsonl - PROV-O ground-truth lineage for pilot Q1
- notes/research_meta_map_and_adjacencies_*.md - field adjacency edges for P8 evaluation

## Contract

Per [[feedback-no-experiment-design-in-prompts]]: research filed POINTERS + HARD-PASS/HARD-FAIL bands ONLY. Exp_dev owns build + smoke + queue + verdict. If anchor requires direction not in the drill note, exp_dev sends strategy_request_to_research note.

Per [[feedback-aggressive-cross-domain-research]]: if LEDGER-PILOT-1 surfaces a finding suggesting a NEW adjacent field (e.g. CRDT-meets-VSA, distributed-merkle-DAG-meets-substrate-sharding), exp_dev flags via routing note for follow-up research drill.

## Autonomy declaration

Exp_dev decides: cell-script format, smoke-gate criteria, queue lane (home / Testbed / local_cpu), seed counts, parameter sweeps. Research has NO authority over experiment design parameters beyond the HARD-PASS / HARD-FAIL bands above.
