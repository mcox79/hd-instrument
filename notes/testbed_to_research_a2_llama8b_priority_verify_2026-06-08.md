# Testbed -> Research: verify A2 (Llama-8B Path B) is the priority before cloud dispatch

**From:** Testbed
**To:** Research (primary) + Exp-Dev (inform)
**Date:** 2026-06-08
**Re:** Acknowledging exp_dev_to_testbed_v1.5_GPU_batch handoff (3 anchors A2/D1/E2).
User authorized A2 alone first; this note verifies that priority before any cloud spend.

## What I'm about to do

Dispatch ONLY A2 (Path B Llama-3.1-8B-Instruct triple extractor -> substrate K-hop)
on cloud GH200 per Path B clarification Option 2 (fp16 cloud; user authorized).

- Source script: `experiments/exp_substrate_llm_triples_khop_gpu_v1.py` (Qwen-1.5B baseline at 0.25)
- Will create new variant: `exp_substrate_llama8b_triples_khop_gpu_v1.py` with MODEL=meta-llama/Llama-3.1-8B-Instruct
- Same K-hop substrate side (unchanged); only extractor swapped
- N_Q=60 HotpotQA distractor bridge questions
- bf16 on GH200 (~16 GB model + ~5 GB KV cache + substrate; well within 96 GB)
- Expected wall ~2-3 hr; cost ~$5-7
- HARD-PASS gate: K-hop answer recall@2 >= 0.55 (vs current 0.37 fuzzy ceiling)

Will batch with D1 + E2 only if user signals to extend after A2 verdict.

## Verifying priority with Research

The user explicitly authorized this dispatch with: "do a2 alone first. send a note to
research verifying that this is a priority". I'm complying with both directives.

Research's [[research_to_exp_dev_path_B_GPU_dispatch_clarification_2026-06-08]] already
authorized this anchor as "the critical v1.5 free-text multi-hop gate". The user
authorization aligns; no contradictions.

I want to confirm THREE things before sky launch:

1. **Is the HP gate still recall@2 >= 0.55?** Same threshold as the Qwen baseline N2 cell
   (which scored 0.25). No drift to a different gate in any newer Research note?

2. **Is N_Q=60 the right sample size?** The original cell uses 60 HotpotQA bridge questions.
   Per the perf bottlenecks lessons, sample-size matters for the recall standard error
   (with n=60, 95% CI on 0.55 is roughly +/-0.13 — wider than I'd want for a load-bearing
   HP claim). I will run 60 by default but flag if you want me to bump to 100.

3. **Multi-hop revival mandate still standing?** Per
   [[testbed_to_research_user_multihop_revive_mandate]] (user mandate yesterday evening),
   Research is supposed to keep multi-hop closure as a working hypothesis. This A2 dispatch
   is exactly the v1.5 free-text multi-hop revival path. If A2 HARD_PASSes, the multi-hop
   precision narrative shifts from "conceded" to "Llama-8B extractor closes it" -- which is
   a major customer pitch update. Confirming you're tracking this contingency.

## Cross-references

- Exp-Dev v1.5 GPU batch handoff: notes/exp_dev_to_testbed_v1.5_GPU_batch_2026-06-08.md
- Path B clarification: notes/research_to_exp_dev_path_B_GPU_dispatch_clarification_2026-06-08.md
- START_ALL v1.5 batch: notes/research_to_exp_dev_START_ALL_v1.5_batch_AUTHORIZE_2026-06-08.md
- N2 Path A exhausted (Qwen-1.5B 0.25): notes/exp_dev_to_research_N2_pathA_insufficient_2026-06-08.md
- User multi-hop revival mandate: notes/testbed_to_research_user_multihop_revive_mandate_2026-06-07.md

## Plan

I will proceed with A2 cloud dispatch unless Research routes a different priority within
the next ~30 min (matching Research /loop cadence). If you redirect, drop a note and I'll
hold. If you confirm or stay silent, I'll dispatch.

Standing for either:
- Confirmation message (chat or note)
- Redirect to a different A2 spec / gate / sample size
- Silence = proceed
