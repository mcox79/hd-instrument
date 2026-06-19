# Testbed -> Exp-Dev: HP-5 medical data delivered to runner

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** User + Orchestrator + Research  **Date:** 2026-06-05
**Re:** `exp_dev_to_testbed_HP5_data_and_llama_status_2026-06-05.md` (Item 1)

## Delivered

Two datasets at `C:\dev\hd-instrument\data\datasets\` on marsh@home runner:

| File | Bytes | Records | Use |
|---|---|---|---|
| `medqa_usmle_500.jsonl` | 799,803 | 500 USMLE Q&A | HP-5 medical Q&A proto evaluation |
| `pubmed_abstracts_10k.jsonl` | 21,953,744 | 10,000 PubMed records | Drug-disease-mechanism corpus |

(Item 2 -- Llama-1B per-token residuals -- separately delivered earlier at 11:55, see `testbed_to_exp_dev_llama_1b_per_token_residuals_delivered_2026-06-05.md`.)

## Per-dataset structure

### MedQA-USMLE (from `GBaker/MedQA-USMLE-4-options` test split)
```json
{
  "question": "<USMLE-style clinical scenario>",
  "answer": "<correct answer text>",
  "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
  "answer_idx": "A|B|C|D",
  "meta_info": "<step1|step2|...>",
  "metamap_phrases": [...]
}
```
500 questions, CC-licensed.

### PubMed abstracts (from `pubmed_qa pqa_artificial` train split)
```json
{
  "pubid": "<pmid>",
  "question": "<research question phrased from the abstract>",
  "context": {
    "contexts": ["<abstract section 1>", "<abstract section 2>", ...],
    "labels": ["BACKGROUND", "RESULTS", ...],
    "meshes": [...]
  },
  "long_answer": "<full answer text>",
  "final_decision": "yes|no|maybe"
}
```
10,000 records. The `context.contexts` field contains the actual abstract text (typically 3-5 structured sections per article). Topics span biomedical research broadly; not pre-filtered to drug-disease-mechanism specifically -- if you need that narrower slice, ping me and I'll grep for relevant keywords (drug names, mechanism terms) over the 10k corpus.

## Loadable

```python
import json
with open('data/datasets/medqa_usmle_500.jsonl') as fh:
    for line in fh:
        row = json.loads(line)
        # row has: question, answer, options, answer_idx, meta_info, metamap_phrases

with open('data/datasets/pubmed_abstracts_10k.jsonl') as fh:
    for line in fh:
        row = json.loads(line)
        # row has: pubid, question, context (dict with contexts list), long_answer, final_decision
        abstract_text = "\n".join(row['context']['contexts'])  # join the structured sections
```

## What this unblocks

- **HP-5 `substrate_medical_qa_proto_no_umls_dependency_v1`** -- you have 500 USMLE-style questions + 10k PubMed abstracts. Substrate-VQ on PubMed corpus -> concept-LM -> MedQA evaluation.
- No UMLS license needed (as you specified).

## What I'm doing next (sequence priority per User)

Moving to **Tier-4-Llama cloud H100 dispatch** (`substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1`) per your `exp_dev_to_testbed_tier4_llama1b_cloud_dispatch_2026-06-05` routing. User explicitly authorized cloud H100 ($1-3). Engineering Llama-specific adaptation now (RoPE + GQA + fp32 + eager + SWAP_LAYER=8 of 16); will triple-check against all prior cloud bugs before launch.

## What's NOT delivered

- True PubMed drug-disease-mechanism-filtered slice (the 10k is the broader biomedical corpus; ping if you need narrower).

---

**END.**

**Exp-Dev:** HP-5 data delivered. Both files on runner; loadable per JSONL format above. Build `substrate_medical_qa_proto_no_umls_dependency_v1` whenever ready.

**User:** Item 1 (medical data) done; moving to Item 2 (Tier-4-Llama cloud) now. Triple-check audit + surface pre-launch summary before any cloud spend.
