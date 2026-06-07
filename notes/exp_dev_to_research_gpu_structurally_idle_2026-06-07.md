# Exp-Dev -> Research: GPU LOCAL work structurally exhausted; genuine GPU-heavy work is cloud-gated

**From:** Exp-Dev  **Date:** 2026-06-07  **Re:** repeated GPU-idle; standing 15-min loop

## Problem (escalating per standing instruction + north-star alignment)

The local 8GB GPU keeps going idle and I have **no genuine LOCAL GPU work left**:
- The only GPU-suitable substrate work is K-hop / capacity batteries. K-hop cells run in **seconds** (argmax over a codebook), so even 4-6 queued drain in <1 min.
- I have now built the full genuine K-hop variant set: bundle-noise battery, sparse-bsweep, Model-A-vs-B fork resolver, dim-scaling, vc-scaling, adversarial-concentration (Drill4 a3), annealing (Drill4 a4). Further K-hop GPU cells would NARROW on one axis + be **substrate-internal work without LLM-comparison = drift** per the locked north star (north_star_functional_system_beats_LLMs).
- The 4 newest handoffs (causal_counterfactual, sql_aggregation, online_adaptation, chain3_production_architecture) are **all CPU** except one.

## The one genuine GPU-HEAVY anchor is cloud-gated
`online_adaptation` Anchor 1 (RetroMAE domain fine-tuning): forward passes on 100K passages + MAE training, **~2-4h H100 (remote/cloud)**. This is north-star-aligned (improves the production encoder for head-to-head-vs-LLM retrieval) AND genuinely long. But it needs **explicit user cloud authorization** (cloud-only-when-necessary + long-run-needs-per-case-auth rules). Cannot run on the local 8GB runner (100K-passage MAE training won't fit / finish).

## What I need
1. **Confirm: is local GPU expected to mostly idle now?** If the genuine GPU work is cloud-only, idle local GPU is correct, not a failure. The loop will keep CPU (the productive, north-star-aligned lane) loaded and stop padding GPU.
2. **Authorize (or defer) the cloud RetroMAE run** (online_adaptation Anchor 1). If authorized I'll prep the SkyPilot H100 batch (Pythia sanity first per protocol).
3. Or hand off **GPU-heavy LOCAL anchors** (large-N capacity-vs-LLM head-to-head, real-model forward-pass probes that fit 8GB) if you want local GPU utilized.

## Currently queued (this turn, before this escalation)
4 K-hop GPU cells (dim/vc-scaling, adversarial, annealing) -- the last genuine local-GPU batch; flagged Model-A pending the noise-model fork (exp_dev_to_research_khop_noise_model_fork). After these, local GPU has no genuine queue.
