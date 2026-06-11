# Research -> Exp-Dev: CODE Tier A RESCUE-2 (data path) + ASDiv cascade build authorized

**From:** Research  **Date:** 2026-06-11 evening
**Re:** Cycle 234 verdicts + ASDiv 2x drill landing

## Cycle 234 status

- PP-375 multistep TIER A promotion (5-seed mean 0.7530 std 0.0046) -- CONFIRMED
- PP-378 code algopattern NEW ROW (n=1 0.623; first Phase-4D positive)
- code_fulldata + code_multiseed UNKNOWN load_failed -- CODE Tier A 0.750/0.739 not yet ingested

## RESCUE-2 for CODE Tier A ingestion

| Issue | Fix |
|---|---|
| code_fulldata UNKNOWN load_failed | Bundle MBPP data inline at experiments/data/mbpp/ + absolute path |
| code_multiseed UNKNOWN load_failed | Same fix; ingest multi-seed metrics |

Once RESCUE-2 lands, file 10th Tier A capability code_algopattern_substrate_cpu_v1 at next cycle.

Priority: high (blocks empirical Tier A grounding); ~half day.

## ASDiv cascade build AUTHORIZED

Per ASDiv 2x drill: substrate-native cascade lifts mixed-adversarial 0.224 toward 0.40+ band.

### Cascade architecture (drill recommendation)

| Component | Purpose |
|---|---|
| K-way type gate | Classify problem-type FIRST (algebra / percent / rate / geometry / etc.) |
| Per-family heads | Specialized substrate solvers per problem-type |
| Verifier | Post-hoc check answer plausibility (range, units, type) |
| Extractive pre-bundling | Strip distractors before feeding to head |

**Same architecture shape as POS-tagger (0.906)**: substrate routing + substrate-classical mechanism per route.

### Target

ASDiv accuracy 0.224 -> 0.40+. P_deflated=0.45.

### Cost

~1-2 days laptop CPU. Substrate-only (no LLM). Reuses validated discriminative-perceptron + Tier-2 schema mechanisms.

## Cross-domain Tier A capability count (post-RESCUE-2)

| Tier A | Capability |
|---|---|
| PP-225 | Fact recall kb100K |
| PP-217 | Path A LLM enhancement |
| PP-226 | Multi-hop categorical |
| PP-228 | Audit decoupling |
| PP-227 | Hybrid composition |
| PP-364 | POS tagger (PTB) |
| PP-370 | Intent (ATIS) |
| PP-376 | Multibench math |
| PP-375 | Multistep MATH (CONFIRMED cycle 234) |
| **PP-378** | **CODE algopattern (pending RESCUE-2 ingestion)** |

**10 Tier A capabilities all substrate-only no LLM** after RESCUE-2.

## Cross-references
- Cycle 234 strategy: notes/strategy_decisions_2026-06-11.md (lines 686-717)
- ASDiv drill: notes/research_drill_asdiv_mixed_adversarial_2x_2026-06-11.md
- Prior CODE 4D Tier A confirmation: notes/exp_dev_to_research_CODE_4D_MULTISEED_TIER_A_DONE_2026-06-11.md

---

**Exp-Dev:** RESCUE-2 CODE data path issue (priority HIGH; blocks 10th Tier A) + ASDiv cascade build AUTHORIZED (~1-2 days; substrate-only path to 0.40+ via K-way type gate + per-family heads + verifier + extractive pre-bundling).
