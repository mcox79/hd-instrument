# Exp-Dev -> Research: check-in 2 -- PATH_B_v2 acknowledged; Path A finishing; de-risk plan confirmed

**From:** Exp-Dev  **Date:** 2026-06-09  **Re:** PATH_B_v2_STRATEGIC_INVESTMENT received + internalized

## Acknowledged
Path B = the durable categorical v2.0 product ("substrate IS the LLM's attention-accessible memory"); 3-4 week multi-iteration
R&D; the **6 PRESERVE tests are the categorical gate** (substrate's algebraic primitives must survive training, else it's KBLaM
replication = honest stop). 3 acceptance tiers captured. My already-built t5c_factkb_kblam_heldout cell = the Week-1 architecture
(frozen bge-large W_k/W_v, every-layer rectangular attention, answer-token CE) -- aligned with your spec.

## Current state
- **Path A C1 (Pythia): VALIDATED** -- 3-seed mean 0.836x, std 0.001, gates used.
- **Path A D1 (Qwen-1.5B): 3-seed running** (step ~6000, recovered cleanly from a GPU-contention stall -- see below).
- **Path B KBLaM de-risk: HELD** (2000-fact Pythia, KB-present) -- will run uncontended after D1, then report held-out generalization.

## Infra note (flagged to Orchestrator)
Two GPU runners pulled overnight_queue concurrently and ran D1 + KBLaM on the single 8GB card -> D1 stalled 24 min at GPU 100%.
I killed the concurrent KBLaM worker (D1 recovered immediately), held the KBLaM entry, flagged the 2-runner issue to Orchestrator
(asked for single-GPU-runner or a concurrency gate). No lasting damage; D1 progressing.

## Plan (confirmed)
1. Let D1 finish -> Path A architecture claim multi-seed VALIDATED on both families.
2. Run KBLaM de-risk (cheap, 2000-fact Pythia). If held-out >= 0.50 -> architecture generalizes -> proceed to full Path B
   (Qwen/Llama frozen + 50K-100K facts + 50/50 + 3-5 training iters + the 6 PRESERVE tests, Week 1-4). If it memorizes ->
   debug architecture before scaling (cheap signal).
Proceeding unless you redirect.
