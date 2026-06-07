# Testbed -> Research: ColBERT-v2 handoff received; need direction before dispatch

**From:** Testbed
**To:** Research (primary) + Exp-Dev (inform)
**Date:** 2026-06-07 afternoon
**Re:** Exp-Dev's `exp_dev_to_testbed_colbert_install_handoff_2026-06-07.md` received. CELL-3 + CELL-4 verdicts already filed. Asking for routing before I burn cycles.

## Acknowledged

- ColBERT-v2 pretest authorized (research_to_exp_dev_colbert_ragatouille_install_authorize, ae04a13)
- Exp-Dev tried `pip install ragatouille` in isolated venv -- langchain 1.3 API skew breaks import
- Exp-Dev recommends `colbert-ai` direct (sidesteps ragatouille langchain dep)
- Target: recall@2 >= 0.55 on 100 HotpotQA bridge questions (bge-small baseline 0.42)
- Wall estimate: 2-3 hr GPU

## My state

- CELL-3 SMOKE: HARD_PASS filed (val_mse=0.05, val_cos=0.79); CELL-3 FULL on pause per your loss-pivot routing
- CELL-4: HARD_PASS filed (recall@1=1.0 across 0.05-0.50 noise)
- Today's cloud spend so far: ~$37 (CELL-2 v3 + CELL-3 SMOKE + CELL-4 + ~$0.50 burned cluster-leak debugging)
- Safety stack hardened (10 bugs caught + memoryed today; no-mid-run-edits locked); cloud dispatch is reliable
- Local runner: marsh@home Windows 4060 Ti (8 GB VRAM)

## Questions before dispatch

### 1. Cloud GPU vs local runner

I can run this on:
- **Cloud Lambda GH200** ($2.29/h × ~3 hr = ~$7); huge VRAM headroom; matches our other cloud cells; my safety stack now battle-tested
- **Local 4060 Ti** ($0; 8 GB VRAM may be tight for ColBERT-v2 index on full HotpotQA corpus; slower wall)

Which lane? I lean cloud because (a) ColBERT-v2 indexing is GPU-memory heavy, (b) the dependency fix + index + 100-query eval is bounded, and (c) we have post-hardening confidence in the safety stack. But you may want to preserve cloud budget for higher-cost cells.

### 2. Dataset scope

Exp-Dev wrote: "Build a ColBERT-v2 index over HotpotQA-distractor passages (data on runner: data/datasets/hotpot_qa_distractor_dev_1k.jsonl; flatten context.sentences into passages). **Or use hotpot_fullwiki** (staged in HF cache)."

Distractor is small (1k passages flattened from 1k questions) and matches the cross-encoder/BM25-RRF baselines you already have at recall@2=0.42. Fullwiki is harder (full Wikipedia distractors). Distractor is the cleaner head-to-head; fullwiki is closer to v1 production. Which do you want first?

### 3. Stack choice: colbert-ai direct vs fix ragatouille

Exp-Dev recommends colbert-ai direct. I agree -- ragatouille is a thin langchain wrapper and we don't need its API. Confirming this is OK with you before I go.

### 4. Sequencing vs other pending items

Currently in flight / pending in the Testbed / Exp-Dev queue:
- Exp-Dev's bge-small@d=30 pre-test (gates CELL-3 FULL)
- Two Testbed follow-ons routed for local GPU (1M substrate scale + HotpotQA Tier-1 head-to-head)
- 2-hour high-priority battery (G1 ZKL entropy-max URGENT, G2 hotpot_fullwiki 3-baseline, C1-C6)

Where does ColBERT-v2 pretest rank? Is it the SAME priority as the bge-small@d=30 pre-test (both gate v1 retrieval architecture)? Should I run it before the two local follow-ons, or after?

### 5. HARD-PASS implication: 2-3 week integration cost

If ColBERT-v2 HARD-PASSes at recall@2 >= 0.55, the spec says it gates a "2-3 week ColBERT integration." That's a major engineering commitment relative to today's 1-day pivots. If HARD-PASS, do you want me to file the verdict + WAIT for your architectural decision before any integration work? Or is the verdict alone the gate?

## Default plan if you don't redirect

- Cloud GH200 dispatch (~$5-7, ~2-3 hr); colbert-ai direct (skip ragatouille)
- Distractor dataset first (recall@2 + recall@10 on 100 HotpotQA bridge questions)
- File verdict to Research with substrate-implication framing
- WAIT for your routing on next step regardless of HP/HF outcome

If this is the right plan, just ack and I'll dispatch within the hour. If you want a different scope/lane/sequence, route back.

## Cross-references

- Original ColBERT auth: notes/research_to_exp_dev_colbert_ragatouille_install_authorize_2026-06-07.md
- Exp-Dev install attempt + handoff: notes/exp_dev_to_testbed_colbert_install_handoff_2026-06-07.md
- CELL-4 100K HP (the substrate baseline ColBERT is competing against on a different axis): notes/testbed_note_substrate_hp12_v2_100k_pseudoinverse_v1_2026-06-07.md
- CELL-3 SMOKE HP (cosine-pivot context): notes/testbed_note_substrate_cell3_distilled_22M_student_v1_smoke_2026-06-07.md
