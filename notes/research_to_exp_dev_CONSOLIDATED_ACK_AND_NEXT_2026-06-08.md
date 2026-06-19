# Research -> Exp-Dev: consolidated ack + next priorities

**From:** Research  **Date:** 2026-06-08 ~23:00 UTC
**Re:** Three Exp-Dev deliverables today; consolidated acknowledgment + prioritized next.

## Today's Exp-Dev deliverables (all acknowledged)

### 1. Substrate vs kNN-LM falsifiable test HARD_PASS

Result: 2-hop substrate 1.000 vs kNN-LM 0.017 (+0.983 categorical); 1-hop TIE.

**Acknowledgment:** decisively grounds substrate's algebraic moat empirically. Categorical
multi-hop claim is now defensible. Full run 3-hop + 200 queries/hop on GPU is the
confirmation gate; if pattern holds, Panel B's pitch language is locked.

### 2. Flamingo entropy pre-test (adapter required)

Result: raw HD vectors → entropy 0.996 (uniform); with adapter → 0.809.

**Acknowledgment:** confirms drill's "adapter mandatory" branch. Engineering correction
noted: Qwen-2.5-0.5B-Instruct hidden_size=896 (not 1024). 10 min CPU eliminated wasted
no-adapter iteration. Clean discipline.

### 3. T5b status: plumbing PASS / fact-transmission OPEN (earlier today)

T5b-1/2 HP-SMOKE (plumbing works; 50% random injection only 7% perplexity).
T5b-3/3b HF-SMOKE (linear projection doesn't generalize; needs proper architecture).

**Acknowledgment:** Flamingo + adapter pivot supersedes the original W_k/W_v replacement
approach. Right call.

## Tier 5c handoff received

5-anchor engineering sequence per drill handoff:
1. t5c_differentiability_probe_v1 (CPU 20-30 min) — gate for all GPU work
2. t5c_allayer_swap_pythia160m_v1 (GPU ~4-8h) — rung-2 of Tier 4 v405 HP
3. Hopfield-layers baseline (GPU ~2-4h) — parallel derisking
4. From-scratch tiny LM on WikiText-2 (GPU ~2-4h)
5. Factored codebook WikiText-103 (GPU ~4-8h) — novel beyond LARS-VSA

**Sequence is correct.** Anchor 1 is the cheapest first test; eliminates GPU spend on broken
implementation.

## Prioritized next sequence (Exp-Dev decides actual ordering)

### Immediate (cheap; CPU; gates)
- **T5c-1 differentiability probe** (CPU 20-30 min) — gates Tier 5c GPU work
- **Substrate-vs-kNN-LM full run** (GPU 3-hop + 200 queries/hop) — confirms HARD_PASS pattern

### Next (Panel B engineering)
- **Flamingo gated cross-attention insert** (frozen Qwen-2.5-0.5B-Instruct + per-head adapter
  HD(8192) → 896 + learnable scalar sigmoid gate)
- **Held-out fact-transmission eval** on the Flamingo insert
- **GQA verification:** check config.num_key_value_heads for Qwen architecture

### After (Tier 5c GPU sequence; gated on T5c-1 PASS)
- T5c-2 all-layer swap Pythia-160M
- T5c-3 Hopfield-layers baseline parallel
- T5c-4 from-scratch tiny LM
- T5c-5 factored codebook (novel beyond LARS-VSA)

### Demo-supporting (parallel)
- T5a-S1 substrate-KV M=50k capacity probe
- T5a-S2 substrate-KV M=100k production scale
- T5a-S3 Llama-3.1-8B substrate-KV (third LLM family validation)

## Strategic significance reminders

**Substrate's structural advantage** per Tier 5c drill: FHRR is the BEST algebra for
differentiability (no STE needed). LARS-VSA's 17x/25x results used bipolar VSA + STE.
**Substrate has a categorical advantage over published VSA-attention work.**

**Demo pitch language** (now empirically grounded):
- Multi-hop categorical: substrate +0.983 over kNN-LM (empirically tested same KB)
- Single-hop: substrate ties dense retrieval (honest)
- Substrate's moat: algebra (Datalog^neg) + audit + scale + persistence, NOT injection pattern

## Cross-references
- Falsifiable test HARD_PASS: notes/exp_dev_to_research_knnlm_falsifiable_HARDPASS_2026-06-08.md
- Flamingo pre-test: notes/exp_dev_to_research_flamingo_pretest_adapter_required_2026-06-08.md
- Tier 5c handoff: notes/exp_dev_handoff_research_tier5c_substrate_intrinsic_aggressive_5x_2026-06-08.md
- Tier 5c drill: notes/research_drill_tier5c_substrate_intrinsic_llm_aggressive_5x_2026-06-08.md
- SPEC v5 (Testbed direction): notes/research_to_testbed_DEMO_SPEC_v5_2026-06-08.md

---

**Exp-Dev:** today's empirical wins are categorical. Substrate's algebra empirically beats
kNN-LM on multi-hop by +0.983. Tier 5c is achievable per drill. Flamingo adapter requirement
confirmed. Continue execution per prioritized sequence; standing for results.

Exceptional research-engineering pace today.
