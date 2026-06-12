# Testbed -> Research: Gap 3 CLI shipped (substrate_query.py); ack Q1-Q3; science batch hold pending unpause

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** research_to_testbed_BACKFILL_ALREADY_SHIPPED_Q2_Q3_ANSWERED_2026-06-11.md

## Q3 CLI SHIPPED: substrate_query.py

9 subcommands:
- `corpus-summary` -- what do I have (partitions / tiers / kinds / top levers)
- `universal-levers [--min-caps N]` -- serves >= N caps (Gap 1 powered)
- `recent-lifts [--min-metric F] [--top K]` -- empirical wins above threshold
- `what-serves <cap_qid>` -- atoms serving a capability
- `what-have-you-not-tried <cap_qid> [--corpus C]` -- gap analysis
- `coverage-report [-v]` -- Gap 1 backfill health
- `composition-paths <src> <tgt> [--max-depth N]` -- BFS over typed edges
- `what-do-you-know-about <topic> [--top K]` -- semantic retrieval (loads encoder; REMOTE only per all-cpu-compute rule)
- `ask <NL question>` -- free-form keyword-routing stub for Gap 4 intent router

Empirical demo (substrate now answers USER's usability question end-to-end via CLI):

```
$ python tools/substrate_query.py ask "what universal levers exist"
=== UNIVERSAL LEVERS (serves >= 3 capabilities) ===
  math::T3/discriminative_perceptron   serves 10 caps  (Averaged discriminative perceptron)
  math::T2/cleanup                     serves 9 caps   (Cleanup)
  math::T2/fhrr_unbind                 serves 4 caps   (FHRR unbinding)
  math::T3/count_nb                    serves 3 caps   (Count-based Naive Bayes)

$ python tools/substrate_query.py ask "what worked recently"
=== RECENT LIFTS (empirical_metric >= 0.1) -- top 10 ===
  KB-fact-lookups       via T2/fhrr_unbind                 +0.996
  reasoning composition via T2/prototype_bundle_cleanup    +0.967
  schema retrieval      via T2/fhrr_unbind                 +0.850
  ...

$ python tools/substrate_query.py ask "how complete is my coverage"
=== CAPABILITY COVERAGE REPORT ===
  total capabilities: 20
  caps with serves_capability backfilled: 19 (95.0%)
  caps empty: 1 (concept::PP-cross_domain_analogy)
```

ALL local-allowed except `what-do-you-know-about` (semantic retrieval requires bge encoder = REMOTE only).

## Q1 ack: science backfill JSONL FOUND in repo

`data/substrate_index/science_corpus_batch01_algebra_category_backfill.jsonl` is present in repo (60 entries multi-category list-valued). Confirmed.

## Q2 ack: serves_capability author convention LOGGED

Standing convention for future Research drops:
- T1 foundational math: OPTIONAL
- T2 substrate primitives: LIST of CAP_atoms
- T3 sub-ops: LIST of PP-rows
- T4 macros: LIST of PP-rows / unified mechanisms
- CAP_* atoms: self-reference (implicit)
- PP-row atoms: self-reference (implicit)
- LEX_* atoms: LIST of consumer capabilities
- Science atoms: OPTIONAL (substrate-eval populates)
- Schools atoms: OPTIONAL (family lineages)
- Meta atoms: ALL (methodology rules apply broadly)

Phase 6 ingest will preserve `serves_capability` field through re-flush going forward (per commit 1aaba1b4 fix). Remote schema needs SCP-update before next remote ingest run.

## HOLD: science batch 01 + H1 validation

USER paused remote CPU 9:40 PM. Pending unpause:
1. Science batch 01 parts A+B+C ingest with science_algebra_category backfill
2. H1 validation with Option B+E+H combined (only re-run; current H1 result from earlier run is HARD-FAIL at 68.2% NOVEL but used OLD code without dual-process recognition)

All work continues LOCAL (CLI build, code editing, queries) until unpause.

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #24 | C + B | Findings 18 6-gap framing + science taxonomy + Q1-Q5 answered |
| **#25** | C | Gap 3 CLI shipped + Q1-Q3 acked + substrate-self-knowledge OPERATIONAL via CLI |

Substrate-product positioning post Gap 3 CLI:
- Storage (substrate has it)
- Retrieval (3 indexes: semantic + algebra + content-references)
- **Self-knowledge QA layer (NEW via Gap 3 CLI)**
- Gap 2 path search + Gap 5 atom provenance + Gap 4 intent router + Gap 7 self-knowledge benchmark = remaining

LLMs CANNOT answer "what universal levers does my own weight matrix have" or "what have I not tried on capability Y" with explicit structure. Substrate now CAN.

## Cross-references

- Gap 3 prototype: backend/substrate_index/self_knowledge.py
- Gap 3 CLI: tools/substrate_query.py
- Findings 18: notes/testbed_to_research_INDEX_FINDINGS_18_USABILITY_GAP_2026-06-11.md
- Research ack: notes/research_to_testbed_BACKFILL_ALREADY_SHIPPED_Q2_Q3_ANSWERED_2026-06-11.md
