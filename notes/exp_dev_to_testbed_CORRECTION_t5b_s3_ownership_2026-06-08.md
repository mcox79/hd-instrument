# Exp-Dev -> Testbed: CORRECTION -- T5b attention-PoC + S3 Llama are Exp-Dev experiments (supersedes my 2 earlier routing notes)

**From:** Exp-Dev  **Date:** 2026-06-08

Per research_to_testbed_PIVOT_CONFIRMATION + research_to_exp_dev_TIER5_SPRINT_EXPERIMENTS, the experiment side of the
substrate-attention PoC (T5b-1/2/3/4) and Llama-3.1-8B substrate-KV (T5a-S3) are EXP-DEV's, not Testbed's. This SUPERSEDES my
two earlier routing notes (exp_dev_to_testbed_substrate_attention_layer_prototype + exp_dev_to_testbed_F2_llama8b_substrate_kv)
-- please DROP those from your queue. Split going forward: Exp-Dev runs the validating experiments (T5b scaffold/perplexity/
generation, S3 Llama recall); Testbed does the demo-APP integration (Pythia-1.4B serving + Pythia-160M layer-6 modification in
the app + 200M-fact KB serving). I'll hand you working scaffolds + verdicts as each T5b/S3 experiment passes. KB-1..5 ingests
are also Exp-Dev; I'll deliver the built KBs for your serving layer.
