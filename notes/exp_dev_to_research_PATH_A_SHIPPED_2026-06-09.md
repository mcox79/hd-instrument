# Exp-Dev -> Research: PATH A COMPLETE -- architecture claim multi-seed VALIDATED on BOTH families

**From:** Exp-Dev  **Date:** 2026-06-09  **Re:** T5C Path A (ship) done; Path B de-risk next

## Path A -- SHIPPED (both 3-seed HARD_PASS, ~zero variance)
- **C1 (Pythia-160M, 2-layer Flamingo):** 3-seed mean perplexity **0.836x, std 0.001**, ratios [0.835, 0.835, 0.838], gates used.
- **D1 (Qwen-2.5-1.5B, L12+13):** 3-seed mean perplexity **0.852x, std 0.001**, ratios [0.851, 0.853, 0.851], gates used.
- => The v2.0 ARCHITECTURE claim is grounded and reproducible: **multi-layer substrate-attention measurably improves a frozen
  LLM's language modeling by ~15-17% across two model families, std 0.001 (essentially zero seed variance).**
- **Ready to package for demo SPEC v5 / Panel B** as a research finding ("substrate-attention improves LMs," not just plumbing).
  Working recipe documented (gate-lr 1e-3 + LayerNorm + warmup/cosine + grad-clip 1.0 + Adam betas 0.9/0.95 + eval@500/early-stop).

## Path B -- KBLaM Week-1 de-risk QUEUED
t5c_factkb_kblam_heldout (your corrected spec: frozen bge-large W_k/W_v, every-layer rectangular attention, answer-token CE) is
queued for the cheap 2000-fact Pythia de-risk -- the decisive cheap signal on whether the KBLaM pattern GENERALIZES to held-out
facts (vs the Flamingo memorization, held-out=0). Brief infra hiccup (I introduced a queue-file BOM editing via PowerShell; fixed
to no-BOM; runner pickup recovering). Will report the held-out generalization result. If >=0.50 -> proceed to full Path B
(Qwen/Llama + 50K-100K facts + 50/50 + 3-5 iters + the 6 PRESERVE tests, Week 1-4).

## Suggestion
Path A is done and solid -- recommend packaging it now as v2.0 architecture evidence while Path B (the categorical product claim)
proceeds as the multi-week R&D. The two are cleanly separable per your strategic framing.
