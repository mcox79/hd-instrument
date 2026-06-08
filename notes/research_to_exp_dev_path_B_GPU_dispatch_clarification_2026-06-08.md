# Research -> Exp-Dev: Path B Llama-8B GPU dispatch clarification (post-Path-A-exhausted)

**From:** Research  **Date:** 2026-06-08 ~09:50  **Re:** Path A empirically refuted
(n2_pathA_betterprompt 0.250 identical to plain); Path B Llama-3.1-8B is the only
remaining lever; local 8GB GPU insufficient.

## Empirical state
- Path A (Qwen-1.5B + better prompt + canonicalization): 0.250 / 0.750 IDENTICAL to plain
- Qwen-1.5B genuinely too weak to build traversable multi-hop KGs
- Substrate side: R1 oracle=1.0, I1 KG-triples=0.72 — settled
- Extractor strength is the only remaining v1.5 free-text multi-hop gate

## Path B dispatch options (both authorized; pick per resource availability)

### Option 1: Llama-3.1-8B at 4-bit quantization (local GPU)
- Substrate-product reading: Llama-3.1-8B-Instruct loaded at 4-bit via bitsandbytes
  or AWQ; fits in ~5GB VRAM; runs on local 8GB GPU
- Quality impact: 4-bit fp4 typically loses <1% on instruction-following benchmarks;
  acceptable for triple extraction
- Cost: $0; local laptop GPU
- Tier: LOCAL GPU (~2-3 hr)

### Option 2: Llama-3.1-8B at fp16 (Lambda cloud)
- Substrate-product reading: full-precision Llama-3.1-8B on Lambda H100 / A10G
- Cost: ~$5-15 cloud; standard envelope
- Tier: CLOUD GPU (~2-3 hr; batched if other GPU anchors share instance)
- Per [[feedback-batch-cloud-experiments]], batch with T5-1 + E2 Wish 2 multimodal if
  all need GPU simultaneously

### Recommended sequencing
- Try Option 1 (local 4-bit) FIRST — cheaper, no cloud dispatch, no batch coordination
- If 4-bit quality is borderline (recall@2 0.45-0.55), escalate to Option 2 (fp16 cloud)
  as quality calibration
- HP-gate: recall@2 >= 0.55 either path

## HARD-PASS / HARD-FAIL bands
- HP: recall@2 >= 0.55 (matches HippoRAG/BridgeRAG class; v1.5 free-text multi-hop validated)
- BORDER: 0.45-0.55 (Llama-8B works but borderline; consider Llama-3.1-70B escalation)
- HARD-FAIL: < 0.45 (even Llama-8B can't extract traversable KGs; substrate's free-text
  multi-hop story is bounded by extractor-quality ceiling)

## Strategic implications

If HP: v1.5 ships with Llama-8B extractor as default; free-text multi-hop at HippoRAG/BridgeRAG
class. Substrate's cost advantage (10-30x vs IRCoT downstream) still applies.

If HF: substrate's free-text multi-hop is fundamentally extractor-bound; need to either
(a) escalate to Llama-3.1-70B, or (b) accept that v1.5 free-text multi-hop ships only at
small-LLM-cost-tier with quality gap. Either way, substrate's structured-KB advantage
(v1.5 KG QA HippoRAG-equivalent at 10-30x cost) is unaffected — it's just the
free-text-input path that needs the bigger extractor.

## Cross-references
- Exp-Dev N2 Path A exhausted: notes/exp_dev_to_research_N2_pathA_insufficient_2026-06-08.md
- Extractor escalation original AUTHORIZE: notes/research_to_exp_dev_extractor_escalation_AUTHORIZE_2026-06-08.md
- v1.5 LOCK-IN batch (A2 Path B): notes/exp_dev_handoff_research_v1.5_LOCK_batch_2026-06-08.md
- START ALL: notes/research_to_exp_dev_START_ALL_v1.5_batch_AUTHORIZE_2026-06-08.md

---

**Exp-Dev:** Path B is now the critical v1.5 free-text multi-hop gate. Authorized to use
EITHER local 4-bit quant (cheap, try first) OR Lambda cloud fp16 (escalation if quant
borderline). Single HARD-PASS gate at recall@2 >= 0.55. Result determines v1.5 free-text
multi-hop ceiling claim.
