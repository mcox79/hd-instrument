# Research priority list (living document; updated based on results)

**Maintained by:** Research
**Date:** 2026-06-09 ~21:00 UTC (initial version)
**Cadence:** updated each wake cycle based on new verdicts + state

## Strategic goal

Full substrate-around-LLM v2.0 demo empirically grounded with categorical claims at production scale + breadth.

## P0 — CRITICAL PATH (active blockers; updates demo capability)

| # | Item | Owner | Status | Why |
|---|---|---|---|---|
| 1 | Stage A Wikidata 50M ingest | Testbed | RUNNING PID 190916; 58K triples / 27 facts/sec / 98 hr ETA | Demo scale requires production KB |
| 2 | /converse + /chat backend serving | Testbed | LIVE PID 154796; 1.16M facts; 407ms latency; substrate audit working | Demo UX foundation |
| 3 | HYBRID production transfer (1.4B fp32) | Exp-Dev | Queued GPU (per WHATS_NEXT P3) | v2.0 claim at production scale |
| 4 | PP-227 multi-seed promotion | Exp-Dev | Queued GPU (per WHATS_NEXT P1) | n=1 founding result needs rigor |
| 5 | Public benchmark wins (WebQSP/CWQ/2Wiki/MuSiQue/FB15K/PubMedQA) | Exp-Dev CPU | Queued (per HUGE_BATCH TIER 2) | External validation evidence |

## P1 — HIGH (active work; differentiates demo)

| # | Item | Owner | Status | Why |
|---|---|---|---|---|
| 6 | CONV Tier 1 (creative + summary + empathic + memory + tools smoke) | Exp-Dev CPU | Queued cpu_runner_local (per HUGE_BATCH TIER 1) | Substrate conversational breadth (user-asked) |
| 7 | DECISIVE-4 GDPR corrected | Exp-Dev CPU | Routed (protocol fix filed) | Article 17 categorical compliance |
| 8 | Compositional multi-hop (PP-225 + PP-224 2/3-hop) | Exp-Dev GPU+CPU | Queued | Categorical moat extension |
| 9 | Stage B/C Wikidata FHRR re-encode | Testbed | Ready; awaits Stage A keys.npy | Optimized substrate at 50M scale |
| 10 | Backend PP-225 + Path A + HYBRID wiring | Testbed | Track B candidate; pending priority | v2.0 demo wiring |

## P2 — MEDIUM (range extension; lower urgency)

| # | Item | Owner | Status | Why |
|---|---|---|---|---|
| 11 | CONV Tier 2 (translation + code + PII + preferences) | Exp-Dev CPU | Queued (HUGE_BATCH TIER 2) | Substrate range |
| 12 | CONV Tier 3 (modal + probabilistic + higher-order + humor) | Exp-Dev CPU | Queued (HUGE_BATCH TIER 2) | Substrate algebra extensions R&D |
| 13 | Substrate-tool-orchestrator (MATH + ORCH) | Exp-Dev CPU | Queued (HUGE_BATCH TIER 2) | Substrate orchestrates SymPy/code/image |
| 14 | PRESERVE-COMPOSITE sanity | Exp-Dev CPU | Queued (HUGE_BATCH TIER 1) | Substrate primitives unchanged by PP-225 (sanity) |
| 15 | Path A every-layer at 1.4B | Exp-Dev GPU | Queued (HUGE_BATCH TIER 2) | Production scale Path A |

## P3 — LOWER (research / nice-to-have)

| # | Item | Owner | Status | Why |
|---|---|---|---|---|
| 16 | DECISIVE-1 full alpha (1200 contexts) | Exp-Dev CPU | Running cpu_runner_local; smoke alpha 0.333 | Substrate-as-speculative-draft viability (likely close) |
| 17 | DECISIVE-2 ANN benchmark submission | EXTERNAL | Not started | Independent sub-ms validation (requires infra) |
| 18 | Demo SPEC v6 update | Testbed/Research | Pending | Two-stage demo positioning |
| 19 | Vertical demo landing pages (legal/healthcare/finance/fda) | Testbed | Track A candidate | Vertical product UX |
| 20 | /admin/load 12-min mystery root cause | Testbed | Deferred via prefit | Operational debt |

## P4 — OPEN QUESTIONS (no active work but tracked)

- Substrate-only LM (Path 1) — speculative; deferred
- Frontier-scale Llama-3.2-3B HYBRID — cloud GPU; defer
- Wikipedia full 5.84M ingest — Testbed Track D candidate
- PubMed full 30M — Testbed Track D candidate
- Wikidata entity labels (6 GB) — unlocks human-readable Q-codes

## Verdicts I'm waiting on (could request orchestration priority if needed)

- **DECISIVE-4 corrected** (just routed; ~1 hr CPU)
- **TIER 1 IMMEDIATE batch results** (10 anchors; ~4 hrs total)
- **HYBRID-1.4B-fp32** (production transfer; GPU)
- **PP-227 multi-seed** (founding rigor)
- **DECISIVE-1 full alpha** (definitive speculative-draft answer)

User-direction NOTE: Orchestration batches ~10 verdicts before crunching (efficiency). If a specific verdict is BLOCKING strategic decision, I can request priority via routing note.

## Standing duties

1. Each wake cycle: gauge Exp-Dev activity (status ping if quiet)
2. Each wake cycle: update this priority list based on new verdicts
3. File priority requests to orchestration when blocking verdicts pending
4. Monitor cycle 208+ when batch fills

## Cross-references
- HUGE BATCH: notes/research_to_exp_dev_HUGE_BATCH_IMMEDIATE_AND_OVERNIGHT_2026-06-09.md
- CPU LANE PRIORITIES: notes/research_to_exp_dev_CPU_LANE_PRIORITIES_2026-06-09.md
- DECISIVE-4 PROTOCOL FIX: notes/research_to_exp_dev_DECISIVE_4_PROTOCOL_FIX_2026-06-09.md
- Cycle 207: notes/orchestrator_to_research_results_summary_2026-06-09_cycle207.md
- Testbed status: notes/testbed_to_research_STATUS_AND_PRIORITIES_REQUEST_2026-06-09.md
- Strategic reframe: notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md
