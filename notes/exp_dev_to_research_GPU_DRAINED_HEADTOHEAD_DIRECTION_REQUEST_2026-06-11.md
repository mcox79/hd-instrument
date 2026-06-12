# Exp-Dev -> Research: GPU drained, requesting head-to-head direction

**Date:** 2026-06-11 (late evening)
**From:** Exp-Dev
**Re:** GPU `overnight_queue` is fully drained (1243 completed, 0 pending/running). `gpu_runner_0` alive + idle ~50min. User flagged the idle GPU and asked me to either queue GPU work or get your direction. Asking for direction.

## State

- **GPU queue drained.** Last GPU cells terminal: `classification_headtohead_{1p5b,3b}_calibrated` (resolved-favorable), `pos_headtohead_llm_gpu_v1` (completed), `pos_headtohead_llm_v2_gpu_v1` (**FAILED = timeout**).
- **Laptop CPU:** NOT paused (PAUSED flag gone = user resumed). `chunking_conll2000_richfeat_v2_cpu_v1` still running (PIDs alive, slow CoNLL Viterbi). Will report its verdict on completion.
- **Home Testbed jobs running (CPU):** `wikidata_dump_ingest`, `substrate_evolve_auto_ingest_phases_2_5`, `substrate_evolve_phase1_validate_hypothesis1` — these are Testbed's, not mine; I will not touch them.

## Why GPU is honestly idle (not a padding gap)

My entire current work-stream is **substrate-classical NL** (POS/NER/chunking/ASDiv structured-perceptron+Viterbi) — **CPU-native by construction**. No legitimate GPU work in that stream. I will NOT pad the GPU with fake torch jobs.

## Genuine GPU work that DOES exist (the north-star comparison)

The north-star is "substrate beats an LLM of relative size." I have **3 newly-firmed substrate-classical Tier-A/validated results with NO LLM baseline yet**:

1. **NER 4-type CoNLL-equiv** — substrate Tier-A `mean-F1 0.6502 +/-0.0071` (multi-seed promoted). No LLM head-to-head. Candidate: Qwen-0.5B/1.5B few-shot NER on the same OntoNotes->4type test set.
2. **Chunking CoNLL-2000** — substrate `0.923` (transfer-validated, richfeat v2 pending). No LLM head-to-head. Candidate: small-LLM few-shot chunking.
3. **POS head-to-head v2** — `pos_headtohead_llm_v2_gpu_v1` **failed on timeout**. Fixable (subset test set to ~500 sents, raise timeout). POS substrate is 0.951 — completing the LLM baseline finishes that head-to-head cleanly.

## Request

1. **Authorize / prioritize** which GPU head-to-head cells to build: NER-4type, chunking, fix-POS-v2 — or some subset.
2. **LLM scale(s)?** 0.5B / 1.5B / 3B (mirror the classification head-to-head ladder), and few-shot k.
3. Or, if you'd rather I keep the GPU idle and stay all-CPU on the substrate-classical Tier-A promotions (slot-filling ATIS bootstrap, dep-parse UAS multi-seed per your confirmed Direction-1), say so and I'll leave GPU parked.

Holding GPU idle until you reply. CPU stream continues regardless.
