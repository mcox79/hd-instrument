# Exp-Dev -> Testbed: v1.5 GPU batch (3 anchors, batch into one dispatch)

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** START_ALL v1.5 LOCK batch -- GPU lane

Per [[feedback-batch-cloud-experiments]] batch these 3 GPU anchors into ONE Testbed dispatch (shared bootstrap). I own the
CPU lane (batches A1-done + B/C/F building now); routing the GPU lane to you since they need gated-model download / bitsandbytes /
shared-venv changes that belong in the cloud/Testbed flow with the safety stack.

## A2 (HIGHEST yield): Path B Llama-3.1-8B-Instruct triple extractor -> substrate K-hop
- Closes the free-text v1.5 multi-hop ceiling. Substrate side is SETTLED: R1 oracle=1.0, I1 KG-triples=0.72,
  N2 Qwen-1.5B=0.25 (coverage 0.75 but non-traversable KGs), Path A better-prompt=0.25 (no gain). The ONLY lever left is
  extractor strength.
- Reuse cell: experiments/exp_substrate_llm_triples_khop_gpu_v1.py (or n2_pathA_betterprompt) -- swap MODEL to
  meta-llama/Llama-3.1-8B-Instruct; keep the substrate K-hop + entity canonicalization unchanged.
- Two authorized options (Research note path_B_GPU_dispatch_clarification): (1) 4-bit local via bitsandbytes/AWQ (~5GB, fits
  8GB, $0, ~2-3hr) -- NOTE Llama-3.1 is HF-GATED (needs token + accepted license) and bitsandbytes-on-Windows is finicky;
  (2) fp16 on Lambda (your safety-stack flow; ~$5-15). Pick per resource availability.
- HARD-PASS: Llama-8B-triples + substrate K-hop recall@2 >= 0.55 on HotpotQA dev (lifts the 0.37 fuzzy ceiling).

## D1: T5-1 Pythia-160M Arch-8 substrate-KV-cache MVE
- Pointer: notes/research_to_exp_dev_N1b_TIER5_additions_2026-06-08.md. Foundational substrate-as-attention anchor.
- Tier: GPU ~4-6hr (CPU fallback 12-24hr). Pythia-160M is small -- fits easily.

## E2: Wish 2 multimodal MSCOCO binary-CLIP pre-test
- Tier: GPU 3-4hr. Needs CLIP + a MSCOCO subset.

Cloud envelope authorized ~$20-50 if all 3 go remote (Research START_ALL note). Flag back if any anchor needs Exp-Dev to
pre-build a cell skeleton; I can supply the substrate-K-hop scaffold for A2 immediately (it is already written and tested).
