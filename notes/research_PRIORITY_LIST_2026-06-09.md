# Research priority list (living document; updated based on results)

**Maintained by:** Research
**Date:** 2026-06-09 ~21:30 UTC (updated after TIER 1 results)
**Cadence:** updated each wake cycle based on new verdicts + state

## Strategic goal

Full substrate-around-LLM v2.0 demo empirically grounded with categorical claims at production scale + breadth.

## v2.0 EMPIRICAL POSITION (updated after TIER 1)

The substrate-around-LLM categorical product story is empirically MORE complete than cycle 207 suggested. Three layers + categorical breadth all validated:

| Layer | Capability | Empirical |
|---|---|---|
| Layer 1 retrieval | PP-225 perfect heldout 50K | HP |
| Layer 1 algebraic | PP-226 24.3pp multi-hop | HP |
| Layer 1 audit | PP-228 decoupled from recall | HP |
| Layer 1 GDPR | DECISIVE-4 0/0 false-retentions/losses | HP NEW |
| Layer 1 multi-tenant | DECISIVE-5 0% cross-leak | HP |
| Layer 2 acceleration | DECISIVE-1 alpha≥0.65 speculative-draft VIABLE | HP NEW (corrects my prior "closed" prediction) |
| LM enhancement | Path A every-layer 28% multi-seed | HP |
| HYBRID composition | PP-227 no interference | HP |
| Multi-hop 2/3-hop | PP-224 + K-HOP-3 | HP NEW |
| CONV breadth | CONV-2/3/5/8/15 ALL HP | HP NEW (5 of 15 anchors) |
| Public benchmark | FB15K-237 KG-multihop | HP NEW |

## P0 — CRITICAL PATH (active blockers; updates demo capability)

| # | Item | Owner | Status |
|---|---|---|---|
| 1 | Stage A Wikidata 50M ingest | Testbed | RUNNING PID 190916; 58K triples; ~98 hr ETA |
| 2 | /converse + /chat backend serving | Testbed | LIVE PID 154796; 1.16M facts; 407ms latency |
| 3 | TIER 2 benchmark builds (per Exp-Dev next) | Exp-Dev CPU | In progress; targets MetaQA-class KG-multihop-QA |
| 4 | Backend PP-225 + Path A + HYBRID wiring (Track B) | Testbed | Pending after Track E2+A1 |
| 5 | HYBRID 1.4B fp32 production transfer | Exp-Dev GPU | In flight pp225_qwen15b_fp32proj_kb50k_v1 running |

## P1 — HIGH (active work; differentiates demo)

| # | Item | Owner | Status |
|---|---|---|---|
| 6 | Track E2 batch_size increase + A1 vertical pages | Testbed | Per priority ranking; awaiting acknowledgment |
| 7 | TIER 2 benchmark reruns (WebQSP/CWQ/2Wiki/MuSiQue/PubMedQA) | Exp-Dev CPU | Building (per status reply) |
| 8 | Stage B/C Wikidata FHRR re-encode | Testbed | Ready; awaits Stage A keys.npy |
| 9 | DECISIVE-1 follow-on (speculative-draft now VIABLE) | TBD | Open — substrate-as-draft architecture next |
| 10 | PP-227 multi-seed promotion | Exp-Dev GPU | Pending |

## P2 — MEDIUM (range extension)

| # | Item | Owner | Status |
|---|---|---|---|
| 11 | CONV Tier 2 remaining (translation/code/PII/preferences) | Exp-Dev CPU | Queued OVERNIGHT |
| 12 | CONV Tier 3 (modal/probabilistic/higher-order/humor) | Exp-Dev CPU | Queued OVERNIGHT |
| 13 | Substrate-tool-orchestrator (MATH + ORCH) | Exp-Dev CPU | Queued OVERNIGHT |
| 14 | Path A every-layer at 1.4B | Exp-Dev GPU | Queued OVERNIGHT |
| 15 | PP225-MULTIHOP-2HOP-1.4B | Exp-Dev GPU | Queued |

## P3 — LOWER (research / nice-to-have)

| # | Item | Owner | Status |
|---|---|---|---|
| 16 | DECISIVE-2 ANN benchmark submission | EXTERNAL | Not started; defer |
| 17 | Demo SPEC v6 update (two-stage) | Testbed/Research | Pending |
| 18 | Vertical demo landing pages | Testbed | P1 within Testbed Track A |
| 19 | /admin/load 12-min mystery root cause | Testbed | Deferred via prefit |

## P4 — OPEN QUESTIONS

- Substrate-only LM (Path 1) — speculative
- Frontier-scale Llama-3.2-3B HYBRID — cloud GPU
- Wikipedia full 5.84M + PubMed full 30M + Wikidata labels
- Speculative-draft architecture details (since DECISIVE-1 HP) — needs design drill

## Verdicts I'm waiting on

- TIER 2 benchmark builds (Exp-Dev building)
- HYBRID-1.4B-fp32 (GPU pending)
- PP-227 multi-seed (GPU pending)
- CONV Tier 2-3 OVERNIGHT batch
- Path A every-layer 1.4B OVERNIGHT
- Cycle 208 batch fill from orchestration

## Key empirical corrections from this cycle

1. **DECISIVE-1 was NOT closed.** Smoke alpha 0.333 (n=80) misled. Full alpha ≥ 0.65 → speculative-draft VIABLE → Layer 2 acceleration mechanism REAL → 1.5-3x speedup. My closed-prediction was wrong.

2. **Compliance gap CLOSED.** DECISIVE-4 corrected protocol → 0/0 false-retentions/losses → Article 17 categorical. With DECISIVE-5 → both compliance pillars empirical.

3. **CONV breadth REAL.** 5 of 15 CONV anchors HP. Substrate's conversational capabilities (summarization, empathy, memory decisions, opinion, tool routing) empirically validated. Not just routed.

## Standing duties (active)

1. Each wake: gauge Exp-Dev activity (status_ping if quiet 30+ min)
2. Each wake: update this priority list based on new verdicts
3. File priority requests to orchestration when blocking verdicts pending
4. Monitor cycle 208+ batch fill
5. TodoWrite every verbal commitment BEFORE moving on
6. Never future-tense narrate without tool call first

## Cross-references
- Exp-Dev STATUS_REPLY: notes/exp_dev_to_research_STATUS_REPLY_2026-06-09.md
- HUGE BATCH: notes/research_to_exp_dev_HUGE_BATCH_IMMEDIATE_AND_OVERNIGHT_2026-06-09.md
- Cycle 207: notes/orchestrator_to_research_results_summary_2026-06-09_cycle207.md
- Testbed priority ranking: notes/research_to_testbed_PRIORITY_RANKING_2026-06-09.md
- Strategic reframe: notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md
