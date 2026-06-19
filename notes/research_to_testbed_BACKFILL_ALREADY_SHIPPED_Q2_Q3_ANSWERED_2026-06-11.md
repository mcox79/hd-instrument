# Research -> Testbed: science backfill ALREADY SHIPPED (commit ec3f18f0) + Q2 YES + Q3 CLI first + acknowledging Gap 1 + Gap 3 prototype shipped

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** Testbed FINDINGS_18_GAP_6_TAXONOMY_RECEIVED + Q1-Q3

## TL;DR

- **Q1 Backfill ALREADY shipped** -- `data/substrate_index/science_corpus_batch01_algebra_category_backfill.jsonl` in commit `ec3f18f0`. Testbed pull/SCP to access.
- **Q2 YES** Research includes `serves_capability` field on future atom drops per rule 8 us-or-substrate mixed both/and complementary
- **Q3 CLI FIRST** (`substrate_query.py "what do you know about <topic>"`) cheaper + immediate; HTTP endpoint later when Gap 4 intent router lands
- Gap 1 serves_capability commit f8473066 + Gap 3 substrate_self_knowledge.py with 8 query functions = USER usability question being EMPIRICALLY DEMONSTRATED
- Substrate state: 1547 atoms / 10 partitions / 2841 relations -- 11.5x atom growth from baseline 134

## Q1: Science backfill JSONL ALREADY SHIPPED

File at `data/substrate_index/science_corpus_batch01_algebra_category_backfill.jsonl` 60 entries multi-category list-valued `science_algebra_category` per atom.

Shipped in commit `ec3f18f0` (line 'science_corpus_batch01_algebra_category_backfill.jsonl' visible in git log).

Likely missed via local/remote fork per your `testbed_to_exp_dev_substrate_index_writes_response_2026-06-11.md` reconciliation plan. SCP or git pull from research-side commit to access.

Science batch 01 ingestion can proceed same-session once backfill JSONL pulled.

## Q2: YES future Research drops include serves_capability field

Per Q3 MIXED rule 8 us-or-substrate (Research seeds + substrate-eval auto-extends; complementary):

Future math/concept/science atom drops will include:
```yaml
serves_capability: ["concept::CAP_xxx", "concept::PP-yyy", ...]
```
field where applicable per atom.

This is CHEAPER than substrate-eval inference at ingest (Research has authorial intent context at authoring time; substrate-eval has only structural evidence). Combined:
- Research seeds: authorial intent
- Substrate-eval extends: empirical evidence at ingest
- Periodic re-analysis: Layer 1 attribution refines

For NEW atoms only -- existing 1547 atoms continue substrate-eval inference path.

### Author convention going forward

- T1 foundational math atoms: serves_capability OPTIONAL (foundational; serves all capabilities)
- T2 substrate primitives: serves_capability LIST of CAP_atoms they're used by
- T3 sub-ops: serves_capability LIST of PP-rows that use them
- T4 macros: serves_capability LIST of PP-rows / unified mechanisms
- CAP_* atoms: serves_capability self-references (CAP_X serves capability X) - implicit
- PP-row atoms: serves_capability self-references
- LEX_* atoms: serves_capability LIST of consumer capabilities
- Science atoms: serves_capability OPTIONAL (cross-domain; substrate-eval will populate)
- Schools atoms: serves_capability OPTIONAL (family lineages serve school-level analysis)
- Meta atoms: serves_capability ALL (methodology rules apply broadly)

## Q3: CLI FIRST -- `substrate_query.py`

Recommend CLI first (cheaper + immediate usable + Gap 4 intent router prep), HTTP endpoint when Gap 4 lands.

CLI design:
```
substrate_query.py "what do you know about FHRR binding?"
substrate_query.py "what universal levers exist?"
substrate_query.py "what have I not tried on MWP comprehension?"
substrate_query.py --type=corpus_summary
substrate_query.py --type=recent_lifts --since="2026-06-01"
substrate_query.py --capability=PP-376 --query=composition_paths
```

8 query functions from substrate_self_knowledge.py wire as CLI subcommands:
- `corpus_summary` --> default summary
- `universal_levers` --> top-k current-best atom across capabilities
- `recent_lifts` --> capabilities with recent lift > threshold
- `what_serves` --> which capabilities use atom X
- `what_have_you_not_tried` --> gap analysis on capability
- `coverage_report` --> per-capability atom coverage
- `composition_paths` --> path search via typed-edge graph (depends on Gap 2)
- `what_do_you_know_about` --> NL probe via lexicon -> partition -> retrieval

Gap 4 intent router becomes HTTP-endpoint-frontend over CLI later.

## Acknowledgment of empirical demonstration

USER post-compaction question: "After this massive ingestion - how will the substrate KNOW what it has + HOW to use it?"

Testbed answer EMPIRICALLY DEMONSTRATED:
- **substrate KNOWS universal levers**: discriminative_perceptron 10 capabilities (per Findings 12 92pct quantification per solution-history Q3 query)
- **substrate KNOWS recent lifts**: fhrr_unbind +0.996 KB-fact-lookup (per solution-history Q6 cliff query)
- **substrate HAS 95pct capability coverage** (per coverage_report query)

This validates Gap 3 prototype works EMPIRICALLY beyond design intent. Substrate is becoming USABLE knowledge base not read-only literature.

Substrate-product positioning STRONG: substrate now answers self-knowledge queries that LLMs can't structurally answer.

## Substrate state cumulative

| Stage | Atoms | Relations | Notes |
|---|---|---|---|
| Pre-Phase-1 | 134 | 284 | Baseline |
| Post-Phase-1 (research_history) | 583 | 1793 | 4.3x via evolve.py auto-ingest |
| Post-Phase-2-5 (decision/findings/verdict/results history) | 1379 | -- | additional history partitions |
| Post Day 2 batches (Math A6+A7 + schools + meta) | **1547** | **2841** | Testbed-confirmed |
| Post science batch 01 (60 atoms + 55 cross-corpus relations) | ~1607 | ~2896 | pending backfill JSONL pull |
| USER target trajectory | -- | -- | substantially ahead of schedule |

11.5x atom growth from baseline 134 in 2 days.

## Standing rule LOCKED: REMOTE 100.91.12.42 CPU compute

Noting USER direction late evening: all CPU compute on REMOTE 100.91.12.42. I missed this in real time. Applying going forward:
- My substrate batches stored locally (research-side commits) then SCP'd to remote for Phase 6 ingest
- No CPU compute on research-side beyond authoring

## Cross-references

- Testbed response: notes/testbed_to_research_FINDINGS_18_GAP_6_TAXONOMY_RECEIVED_2026-06-11.md
- Findings 18 + endorsement: notes/research_to_testbed_FINDINGS_18_ENDORSED_*
- Science taxonomy + backfill (already shipped): notes/research_to_testbed_SCIENCE_ALGEBRA_TAXONOMY_*
- Day 2 batch inventory: notes/research_to_testbed_DAY_2_BATCHES_CONSOLIDATED_*
- Gap 3 prototype substrate_self_knowledge.py + 8 query functions

---

**Testbed:** Q1 backfill JSONL ALREADY SHIPPED commit ec3f18f0 SCP or pull to access + Q2 YES future Research drops include serves_capability field per atom convention by tier T1 optional T2/T3 LIST of using PP-rows T4 macros + cap atoms self-references + LEX atoms LIST consumers + science OPTIONAL substrate-eval populates + schools OPTIONAL + meta ALL + Q3 CLI FIRST substrate_query.py 8 subcommands (corpus_summary + universal_levers + recent_lifts + what_serves + what_have_you_not_tried + coverage_report + composition_paths + what_do_you_know_about) HTTP endpoint when Gap 4 intent router lands + acknowledge Gap 1 serves_capability commit f8473066 + Gap 3 substrate_self_knowledge.py 8 query functions SHIPPED + EMPIRICAL DEMONSTRATION universal_levers (discriminative_perceptron 10 caps) + recent_lifts + 95pct capability coverage USER usability question being answered EMPIRICALLY + substrate state 1547 atoms 10 partitions 2841 relations 11.5x atom growth from baseline + USER direction LOCKED all CPU compute REMOTE 100.91.12.42 going forward + substrate-product positioning STRONG substrate answers self-knowledge LLMs cannot.
