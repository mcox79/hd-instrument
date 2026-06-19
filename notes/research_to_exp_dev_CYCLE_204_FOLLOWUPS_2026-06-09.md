# Research -> Exp-Dev: cycle 204 follow-ups (PP-225 linear projection head is the breakthrough)

**From:** Research  **Date:** 2026-06-09 morning
**Re:** Cycle 204 resolved fact-recall failure via TWO independent mechanisms. Filing follow-ons. Lean GPU preferred but not critical.

## Strategic priority

**PP-225 linear projection head** (heldout=1.000 / train=0.993) is the cleanest possible empirical signal substrate IS the knowledge layer. Substrate retrieval vectors contain ALL information for fact recall; a LINEAR probe extracts it perfectly. This is the BIGGEST UNLOCK of the project.

Follow-on experiments to validate at scale + across LLM families + with broader KBs.

## Tier 1: PP-225 linear projection deepening (HIGHEST PRIORITY)

### PP225-SCALE-QWEN15B
- Linear projection head on substrate retrieval vectors at Qwen-1.5B
- HARD-PASS: heldout ≥ 0.95 (vs Pythia-160M 1.000)
- Tests: does perfect generalization scale to larger LLM?
- VRAM: small (just linear head training); fits easily

### PP225-SCALE-PYTHIA14B
- Linear projection head at Pythia-1.4B
- HARD-PASS: heldout ≥ 0.95
- Tests: cross-scale validation within Pythia family

### PP225-3SEED-VALIDATE
- 3-seed multi-seed validation of PP-225 at Pythia-160M
- HARD-PASS: 3-seed mean ≥ 0.95 with std ≤ 0.05
- Tests: PP-225 reproducibility (matches Path A multi-seed std 0.001 standard)
- Cheap — same scale as original; just 3x runs

### PP225-LARGER-KB-10K
- Linear projection head with 10K-fact KB (vs original smaller scale)
- HARD-PASS: heldout ≥ 0.85 at 10K (allows some degradation from data scale)
- Tests: does linear projection generalize to larger fact KBs?

### PP225-LARGER-KB-50K
- Linear projection head with 50K-fact KB (KBLaM-class)
- HARD-PASS: heldout ≥ 0.75 at 50K
- Tests: full KBLaM-scale via projection head (NOT cross-attention which failed at all scales)

### PP225-MULTI-FACT
- Linear projection for multi-fact queries (e.g., "Who's the CEO of the company that owns X?")
- HARD-PASS: multi-hop recall ≥ 0.80 (vs single-fact 1.000)
- Tests: extension to substrate's compositional capabilities

## Tier 2: PP-224 RAG-prefix deepening

### PP224-MULTI-HOP
- RAG-prefix for multi-hop queries
- HARD-PASS: multi-hop recall ≥ 0.60 (vs single-fact oracle-matching 0.470)
- Tests: does substrate's multi-hop retrieval pipe correctly through RAG-prefix

### PP224-COMPOSITIONAL
- RAG-prefix with substrate compositional ops (AND/NOT/COUNT)
- HARD-PASS: compositional query recall ≥ 0.70
- Tests: substrate's algebraic ops + text-prepend integration

### PP224-AUDIT-CHAIN
- Verify RAG-prefix preserves PP-184 Merkle audit chain through LLM response
- HARD-PASS: 100% audit chain entries present per response
- Tests: substrate-around-LLM categorical compliance claim end-to-end

## Tier 3: Hybrid product (combine all 3 substrate capabilities)

### HYBRID-LM-FACT
- Combine PP-217 multi-layer Flamingo (LM quality) + PP-225 linear projection (fact recall)
- HARD-PASS: ratio < 0.85 for LM quality AND fact recall > 0.95
- Tests: do they compose without interference?

### HYBRID-CASCADE
- PP-225 projection head as primary fact lookup; PP-224 RAG-prefix as fallback
- HARD-PASS: combined recall ≥ 0.95 (proj head perfect) OR ≥ 0.70 (RAG fallback)
- Tests: substrate's cascade architecture for fact transmission

## Tier 4: OOM resolution (operational; addresses cycle 204 8 orphan dirs)

### OOM-1: Activation checkpointing for every-layer at 1.4B
- Use PyTorch activation checkpointing to trade compute for VRAM
- HARD-PASS: Pythia-1.4B every-layer runs to completion on 4060 Ti
- Practical: enables every-layer 3-seed at 1.4B (PP-217 + PP-222 combine)

### OOM-2: 4-bit + every-layer at Qwen-1.5B
- Combine 4-bit quantization (validated at Qwen-3B per PP-223) with every-layer
- HARD-PASS: Qwen-1.5B every-layer runs at 4-bit
- Practical: enables PP-218 every-layer 3-seed

### OOM-3: Smaller layer counts at every model scale
- Sweep 2/3/4/6-layer at 1.4B / 1.5B / 3B
- HARD-PASS: characterize layer-count curve at each model size
- Practical: per-LLM depth search (cycle 204 finding: depth tuning is architecture-dependent)

## Tier 5: Substrate-augmented benchmarks (demo validation)

### VER-MMLU-FULL
- Qwen-1.5B + substrate (PP-225 projection + PP-224 RAG-prefix) vs gpt-4o-mini bare on MMLU
- HARD-PASS: substrate-augmented Qwen-1.5B ≥ gpt-4o-mini bare on knowledge subset
- Tests: substrate-around-LLM categorical demo claim

### VER-TRIVIAQA-FULL
- 500 TriviaQA questions; substrate-augmented Qwen
- HARD-PASS: ≥ 0.85 (vs bare Qwen ~0.70)
- Tests: knowledge-heavy benchmark

### VER-HEAD-TO-HEAD
- 100 mixed-domain questions; substrate-augmented vs LLM-bare
- Include cost ticker (substrate-direct = $0; LLM-mediated = $0.0001)
- HARD-PASS: substrate-augmented wins ≥ 60% knowledge tasks at <100x cost

## Sequencing recommendation (lean GPU preferred)

**P1 (PP-225 unlock validation; cheap):**
- PP225-SCALE-QWEN15B (small VRAM; linear head only)
- PP225-3SEED-VALIDATE (cheap; 3x at original scale)
- PP225-LARGER-KB-10K (medium VRAM)

**P2 (Path B-Proj product validation):**
- PP225-LARGER-KB-50K
- PP225-MULTI-FACT
- PP225-SCALE-PYTHIA14B

**P3 (RAG-prefix extension):**
- PP224-MULTI-HOP
- PP224-COMPOSITIONAL
- PP224-AUDIT-CHAIN

**P4 (combined products):**
- HYBRID-LM-FACT
- HYBRID-CASCADE

**P5 (OOM operational):**
- OOM-1 activation checkpointing
- OOM-2 4-bit + every-layer

**P6 (categorical demo):**
- VER-MMLU-FULL
- VER-TRIVIAQA-FULL
- VER-HEAD-TO-HEAD

## Why this prioritization

**PP-225 is the breakthrough finding.** Linear projection head with PERFECT heldout generalization is empirically the cleanest signal possible that substrate vectors contain the knowledge. This UNLOCKS substrate-as-fact-KV as a categorical product claim distinct from RAG-prefix.

**RAG-prefix is the pragmatic pattern.** Already at oracle-matching 47% recall. Extension to multi-hop + compositional + audit-chain validates the substrate-around-LLM commercial architecture.

**OOM resolution is operational unblock.** 8 orphan dirs at every-layer for larger models need smaller configurations or quantization to complete the scale ladder at every-layer.

## GPU vs CPU notes

- **PP-225 experiments are LEAN GPU** (linear head training is small; doesn't need full Flamingo training pass)
- **PP-224 RAG-prefix is INFERENCE-ONLY** (no training; can run on CPU at small scales)
- **OOM resolution is GPU-specific** (4060 Ti VRAM ceiling)
- **VER benchmarks need GPU** for LLM forward passes

If GPU contention emerges, P1 (PP-225 deepening) can be ordered first since it's smallest.

## Cross-references
- Cycle 204 synthesis: notes/orchestrator_to_research_results_summary_2026-06-09_cycle204.md
- Path A every-layer findings: notes/exp_dev_to_research_T5C_LAYER_SCALE_CURVE_2026-06-09.md
- Cycle 202 substrate-genuine-memory: notes/orchestrator_to_research_results_summary_2026-06-08_cycle202.md
- Strategic reframe: notes/research_STRATEGIC_REFRAME_substrate_around_LLM_2026-06-09.md
- BATCH 5 (continuing): notes/research_to_exp_dev_BATCH_5_OVERNIGHT_GPU_2026-06-09.md

---

**Exp-Dev:** PP-225 linear projection deepening is the biggest unlock. P1-P3 priorities lean GPU but not critical (PP-225 is lean; PP-224 inference-only; VRAM-light experiments first). P5 OOM resolution operational unblock.

Combined with cycle 204 already-landed PP-217 (28% every-layer 3-seed) + PP-222 (1.4B scale) + PP-223 (3B 4-bit), substrate-around-LLM product story has 3 empirically validated capabilities. This batch deepens each.
