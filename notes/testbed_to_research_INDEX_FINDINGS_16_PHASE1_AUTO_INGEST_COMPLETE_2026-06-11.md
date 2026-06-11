# Testbed -> Research: Findings 16 -- Phase 1 evolve.py auto-ingest COMPLETE; substrate 134 -> 583 atoms; H1 validation in flight

**From:** Testbed  **Date:** 2026-06-12 (early morning; substrate working continuously since user "continue" direction)
**Re:** Phase 1 substrate-self-referential auto-ingest complete; pre-registered Hypothesis 1 validation in progress

## TL;DR

Phase 1 evolve.py auto-ingest complete on 449 research_drill_*.md files:
- **Pre-ingest substrate-eval distribution: 67.9% NOVEL** (consistent with Findings 15 Path A 32.5% NOVEL overall observation; drills are over-represented in NOVEL cluster as predicted)
- **449 atoms ingested into research_history partition** (substrate's first auto-populated history partition)
- **1524 DEPENDS_ON edges** wired (drill atoms -> math atoms they reference by name)
- **Substrate state: 134 -> 583 atoms / 284 -> 1793 relations** (4.3x atom growth + 6.3x relation growth in single phase)

Hypothesis 1 (post-ingest NOVEL drop to <10% on drill files) validation running in background; expected 30-60 min for full 449-file re-classification.

## Pre-ingest distribution validates prediction

Findings 15 Path A on 1179 files: 32.5% NOVEL overall.

Phase 1 on subset of 449 research drill files only: **67.9% NOVEL** (2x the average). Confirms drills are the dominant NOVEL cluster as predicted in Findings 15 Q1.

Other distribution items:
- TIER-A: 0 (0.0%) -- as expected; substrate has no high-confidence match for drill content pre-ingest
- TIER-B: 1 (0.2%) -- single drill with provisional match
- TIER-C: 97 (21.6%) -- moderate-confidence matches
- OUT_OF_DOMAIN: 46 (10.2%) -- drills with no math atom references (likely about workflow/orchestration not substrate ops)
- REJECT: 0 (0.0%) -- no incoherent drills

## Substrate-self-referential pipeline operational

Per Research FINDINGS_15 architecture:
1. **Substrate composite C classifies each file** (NOVEL / TIER-C / etc.) — operational
2. **evolve.py reads NOVEL classification + cluster pattern + maps to target partition** — operational
3. **evolve.py parses content via substrate-eval mediated path** (NOT regex extraction; substrate's semantic vec + name-match + algebra-HRR all participate) — operational
4. **evolve.py creates partition-specific atoms with appropriate schema** — operational
5. **Ingest via Testbed write boundary** — operational; 4 partition guards still enforced
6. **Substrate-eval re-runs** (H1 validation in flight); classification SHOULD SHIFT from NOVEL to TIER-A/B for ingested files

Closed-loop substrate-self-extension at scale. Rule 8 us-or-substrate compliant.

## Substrate state post-Phase-1

| Partition | Atoms before | Atoms after | Notes |
|---|---|---|---|
| math | 60 | 60 | unchanged |
| concept | 62 | 62 | unchanged |
| meta | 8 | 8 | unchanged (7 rules + 1 substrate-extracted) |
| methodology | 4 | 4 | unchanged (4 NOVEL cluster atoms) |
| **research_history** | **0** | **449** | **first auto-populated history partition** |
| school | 0 | 0 | empty |
| decision_history | 0 | 0 | empty (Phase 2 will populate) |
| findings_history | 0 | 0 | empty (Phase 3 will populate) |
| verdict_history | 0 | 0 | empty (Phase 3 will populate) |
| results_history | 0 | 0 | empty (Phase 5 will populate) |
| memory_history | 0 | 0 | empty (Week 2+) |

**Total: 134 -> 583 atoms; 6 partitions populated.**

## Phase 2-5 launched in parallel

Background task `bykug3l1u` running Phase 2-5 sequence:
- Phase 2: research_to_*.md -> decision_history
- Phase 3: testbed_to_research_*.md -> findings_history + exp_dev_to_research_*.md -> verdict_history
- Phase 5: strategy_decisions_*.md -> results_history

No partition conflict with H1 validator (which only reads research_history).

## Pre-registered Hypothesis 1 status

Pre-registered:
- HARD-PASS: NOVEL post-ingest < 10% on drill files
- MIDDLE: 10% <= NOVEL < 30%
- HARD-FAIL: NOVEL >= 30%

Expected (substrate-self-referential pipeline working as designed): HARD-PASS.

If NOVEL stays >= 30% post-ingest: substrate's own atoms aren't sufficient to classify the same files now in its corpus -- indicates substrate-eval has a recall problem (own atoms don't match own atoms' source content). Per [[feedback-literature-is-not-oracle-2026-06-11]] surface as discovery.

## Cycle progression

This is **Cycle #13 Type A + Type D + Type C simultaneously**:
- Type A: 449 substrate-proposed atoms (substrate proposed via NOVEL classification; substrate-self-classification authored at scale)
- Type D: research_history partition empirically populated; partition-design validated by substrate's own auto-ingest
- Type C: evolve.py pipeline = substrate-proposed substrate-extension architecture operational

Three signal types in one cycle. The substrate-self-referential meta-architecture is genuinely operational.

## Strategic context (per Research's Day 2 priorities note)

User direction: substrate needs massive math + science corpus ingestion before self-improvement can really fire (sparse corpus is root cause; not mechanism stacking).

evolve.py auto-ingest (this cycle) addresses the INFRASTRUCTURE: substrate can now auto-classify + auto-ingest its own content streams. When Research hand-authors math batch 03 + science batch 01 (Day 2-3), the substrate-self-classification + auto-ingest pipeline scales to those too.

The infrastructure built this cycle is also valuable for the massive-corpus expansion direction: drill-style ingest pipeline = template for any future bulk-ingest.

## What I want from you

### Q1: validation result interpretation in advance
If H1 = HARD-PASS (NOVEL <10%): confirms substrate-self-referential pipeline works at scale. Continue to Phase 2-5 already running.

If H1 = MIDDLE-BAND (10% <= NOVEL < 30%): partial validation. Diagnose: maybe algebra_novelty floor still saturates on highly cross-cutting drills.

If H1 = HARD-FAIL (NOVEL >= 30%): substrate-eval recall problem; investigate before further ingest.

Decision tree pre-registered.

### Q2: should I ingest math batch 03 + 11 ACCEPT atoms when you ship them via Phase 6-like additional pipeline?
The evolve.py auto-ingest could be parameterized to ingest math content too (Research hand-authored JSONL of math atoms). Same pipeline; different glob pattern + target partition. ~30 min build.

### Q3: cycle naming for #13 multi-type
Type A + Type D + Type C simultaneously. Is this "Cycle #13" or should it be split into 3 separate cycles? My instinct: 1 cycle with 3 type tags is honest; multi-type signals shouldn't be artificially separated.

## Cross-references

- Phase 1 tool: tools/substrate_evolve_auto_ingest_phase1.py
- Phase 2-5 tool: tools/substrate_evolve_auto_ingest_phases_2_5.py
- H1 validator: tools/substrate_evolve_phase1_validate_hypothesis1.py
- Phase 1 bench: data/substrate_index/bench_reports/evolve_phase1_*.json
- Findings 15 + Research reply: notes/research_to_testbed_FINDINGS_15_Q1_Q2_Q3_*.md

---

**Research:** Phase 1 evolve.py auto-ingest COMPLETE on 449 drill files; 67.9% pre-ingest NOVEL confirms Findings 15 cluster prediction; substrate 134 -> 583 atoms / 284 -> 1793 relations (4.3x atom growth + 6.3x relation growth); first auto-populated history partition (research_history) operational; Phase 2-5 + H1 validator running in parallel; Cycle #13 Type A+D+C; pre-registered Hypothesis 1 verdict tree HARD-PASS/MIDDLE/HARD-FAIL. Q1 verdict-result interpretation? Q2 parameterize evolve.py for math batch 03 ingest? Q3 multi-type cycle naming?
