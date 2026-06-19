# exp_dev hand-off -- research: V1 Demo Pipeline Optimization

## Filed-by
Research sub-agent, 2026-06-05

## Trigger
Research note: notes/research_drill_v1_demo_pipeline_optimization_2x_2026-06-05.md
Topic: 2x deep drill on V1 regulated-AI demo pipeline (certified deletion + real-time write)

## Pause state
Check data/orchestrator_paused.flag before dispatching any GPU anchor.
CPU-only anchors (A1, A2) are not pause-gated.

Per [[feedback-no-experiment-design-in-prompts]]: this file hands off TASK + WHY + CONTRACT only.
Exp_dev designs the anchor grid, sweep parameters, threshold formulas, and queue assignment.

---

## Anchor candidates (rank-ordered)

### Anchor 1 (HIGHEST PRIORITY -- CPU, <2 min)
Pointer: Cheap decisive test A from research note, Part D + Part C
Substrate-product reading: Does Pythia-160M produce representations with sufficient
  geometric richness for associative memory input at N=1024? This gates the cheapest
  extraction path for the demo pipeline. Failure means escalate to Llama-1B directly.
Tier hint: CPU smoke; no GPU required; <2 min wall on laptop
Why-now: Unblocks entire demo pipeline decision tree. If Pythia passes, demo pre-extraction
  is trivially fast (<10 sec for 10K). If it fails, we skip to Anchor 3.
Task: Extract ~100 text facts using Pythia-160M (fp32, all-CPU); write activations at layer
  ~7 of 12; load into associative memory substrate at N=1024; measure retrieval accuracy
  (fraction correct over query batch). Report accuracy + extraction wall time.

### Anchor 2 (CPU, <30 min -- crypto path validation)
Pointer: Part A, cheap decisive test step 2
Substrate-product reading: Validates that the RSA accumulator deletion cert round-trips
  correctly in pure Python + gmpy2 before any integration work begins. This is a structural
  prerequisite for the demo certification claim.
Tier hint: CPU; ~30 min build + <1 min run; no GPU
Why-now: Blocks Day 1 of demo engineering. Should be the FIRST code written.
Task: Implement minimal RSA accumulator class (~120 LOC): add, delete, witness_gen,
  witness_verify. Use gmpy2 for 2048-bit modular exponentiation. Test on 10 elements:
  add all 10, delete 3, verify cert for each deleted element. Measure cert verification
  latency. Success criterion: pi_x^(Hash_p(x)) == Acc_new mod N for all 3 deletions;
  verification latency <1 ms each.

### Anchor 3 (GPU, <5 min -- extraction benchmark)
Pointer: Part B, cheap decisive test step 3; Part E pipeline spec
Substrate-product reading: Validates that desktop RTX 4060 Ti + batch=8 + bf16 + layer-skip
  brings 10K-fact extraction within demo timeline. This is the hard prerequisite before
  committing to desktop-only demo architecture (vs cloud H100 fallback).
Tier hint: GPU; batch=8 bf16; layer-skip patch on HuggingFace Transformers
Why-now: Gates cloud-spend decision. If HARD-PASS (10K in <5 min), no cloud needed.
  If HARD-FAIL (>20 min), triggers $0.50-1.00 H100 batch run.
Task: Benchmark Llama-3.2-1B bf16 extraction at batch=8 with early-exit after layer 10 of 16,
  using HuggingFace Transformers (patched LlamaModel.forward to return at target layer).
  Extract activations for 1K facts; extrapolate to 10K. Report: wall time per 1K, estimated
  10K wall, VRAM peak, any OOM signals.

### Anchor 4 (GPU, <15 min -- end-to-end integration smoke)
Pointer: Part C + Part E, Day 3 of engineering timeline
Substrate-product reading: End-to-end smoke: extract 100 facts -> load substrate -> live-ingest
  5 new facts -> delete 2 -> verify cert -> re-query (confirm 0 phantom recall). This is the
  minimal version of the full demo flow. Must pass before committing to screen recording.
Tier hint: GPU; moderate; depends on Anchors 2+3 passing
Why-now: After Anchors 1-3 pass, this is the next critical gate. Failure here reveals
  integration issues before any screen-recording effort.
Task: End-to-end pipeline smoke: (a) Extract 100 facts using optimized Llama-1B stack,
  (b) Load substrate W at N=1024 or N=4096, (c) Live-ingest 5 new facts via Hebbian write,
  (d) Query all 5 -- confirm correct recall, (e) Delete 2 via RSA accumulator, get certs,
  (f) Re-query deleted facts -- confirm null/no-recall response, (g) Run standalone verifier
  on certs -- confirm pass. Report: pass/fail per step; latencies for write, delete, verify.

---

## Context pointers

- Research note (full findings): d:/AI/hd-instrument/notes/research_drill_v1_demo_pipeline_optimization_2x_2026-06-05.md
- Field advisor output: see research note field-coverage context
- ROME/MEMIT deletion impossibility lit: arXiv:2309.17410 (38%/29% residual); ACL 2024 Findings
- vLLM extraction API: https://docs.vllm.ai/en/stable/examples/offline_inference/extract_hidden_states/
- Gemma-2 architecture: arXiv:2408.00118
- Layer-skip precedent: arXiv:2404.16710 (LayerSkip); hard truncation simpler for extraction
- RSA accumulator without prime hashing: ePrint 2024/505

---

## Contract

Exp_dev owns: anchor name selection, sweep grid, threshold formulas, HP/MID/HF bands,
  queue choice, ETA, cap_map decision pre-registration.
Research hands off: task framing, why-now rationale, context pointers, tier hints.
Research does NOT pre-commit to specific anchor names, numerical thresholds, or queue targets.

## Autonomy declaration

Exp_dev has full autonomy to sequence, combine, or split these anchors as the pipeline
requires. Anchor 2 (crypto smoke) is CPU-only and can run while GPU queue is occupied.
Anchor 1 (Pythia smoke) can run in parallel with Anchor 2. Anchor 3 gates Anchor 4.
