# Testbed -> Exp-Dev: KG/QA datasets delivered to runner (Action 2)

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** User + Orchestrator + Research  **Date:** 2026-06-05
**Re:** `research_to_testbed_3_authorizations_pertoken_kgqa_gpu_2026-06-05.md` (Action 2)

## User-authorized + delivered

Three datasets downloaded + SCP'd to runner at `C:\dev\hd-instrument\data\datasets\`. All loadable + format-correct (locally verified before SCP; sizes match post-SCP).

| File | Bytes | Examples | Use |
|---|---|---|---|
| `hotpot_qa_distractor_dev_1k.jsonl` | 6,333,095 | 1,000 multi-hop Q&A (hard difficulty, distractor variant) | CCC-1 REVISED-v2 multi-hop reasoning eval |
| `nq_open_validation_1k.jsonl` | 110,476 | 1,000 single-hop Q&A | CCC-1 baseline single-hop Q&A |
| `fb15k_237_train_50k.jsonl` | 6,111,656 | 50,000 KG triples (subject-predicate-object) | CCC-1-EXTRA KG relational reasoning |

Total: ~12.6 MB on runner disk.

## Per-dataset notes

### HotpotQA distractor dev (1k hard examples)
- Loaded from `hotpotqa/hotpot_qa` `distractor` `validation` split via HF datasets (streaming).
- Format per row:
  ```
  {"id": str, "question": str, "answer": str, "type": "comparison|bridge",
   "level": "hard|medium|easy", "supporting_facts": {"title": list, "sent_id": list},
   "context": {"title": list, "sentences": list}}
  ```
- Filtered to "hard" level on the HF side via distractor variant.

### NQ open validation (1k)
- Loaded from `google-research-datasets/nq_open` `validation` streaming.
- Format per row:
  ```
  {"question": str, "answer": list[str]}
  ```
- Multiple acceptable answer strings per question (alternative phrasings).

### FB15k-237 (50k triples)
- Loaded from `KGraph/FB15k-237` `train` streaming.
- **NOTE on Wikidata substitution**: Research's request was "Wikidata triples (~50k)". I tried four HF-hosted Wikidata5m variants (`intfloat/wikidata5m_full_text`, `GG-A/wikidata5m-subset`, `EMBO/wikidata5m_text_triplet`, `Open-Orca/Wikidata5M_filtered_subset`) — all 404 (datasets either removed or unauthorized).
- **FB15k-237** is the standard KG-completion + multi-hop reasoning benchmark in the literature (Toutanova & Chen 2015). It uses Freebase IDs (`/m/...`), which are aligned with Wikidata via mapping tables (Freebase entities became Wikidata Q-IDs in 2014). For substrate KG-reasoning empirical tests, FB15k-237 is the canonical substitute.
- Format per row:
  ```
  {"subject": "/m/027rn", "predicate": "/location/country/form_of_government", "object": "/m/06cx9"}
  ```
- 50k triples (full FB15k-237 train has ~310k; capped per Research's "~50k" target).
- If you need true Wikidata IDs, I can run a Wikidata SPARQL endpoint query for ~50k recent triples; ping me and I'll deliver as a second file.

## Loadable on runner

Pythonic load:
```python
import json
with open('data/datasets/hotpot_qa_distractor_dev_1k.jsonl') as fh:
    for line in fh:
        row = json.loads(line)
        # row has: id, question, answer, type, level, supporting_facts, context
```

Same pattern for `nq_open_validation_1k.jsonl` and `fb15k_237_train_50k.jsonl`.

## What this unblocks

- **CCC-1 REVISED-v2** -- the load-bearing substrate-vs-Pythia-160M head-to-head test on multi-hop reasoning. HotpotQA distractor is the standard benchmark; you have 1k examples ready.
- **CCC-1-EXTRA** -- KG relational reasoning via substrate-stored FB15k-237 triples; SQ2 K=12 multi-hop traversal over the substrate-encoded KG.
- **NQ baseline** for single-hop comparison.

Both gate together with the per-token Pythia residuals from Action 1 (which I shipped at commit `34137e9` and filed `testbed_to_exp_dev_pythia160m_per_token_ready_to_queue_2026-06-05.md`).

## Action 3 next

Moving to GPU runner inspection (`nvidia-smi` + stale procs + capacity-comp diagnostic). Will surface findings shortly.

---

**END.**

**Exp-Dev:** all 3 datasets on runner at `C:\dev\hd-instrument\data\datasets\`. Ready for CCC-1 REVISED-v2 + CCC-1-EXTRA build. Ping me if FB15k-237 doesn't fit your KG reasoning frame and you specifically need Wikidata QID triples (5-10 min SPARQL query I can run).

**User:** Action 2 done. Moving to Action 3 (GPU inspection) now.

**Research:** Wikidata substituted with FB15k-237; substitution documented above. Strategic equivalence for substrate KG reasoning purposes; ping if you want me to also pull Wikidata QID triples via SPARQL.
