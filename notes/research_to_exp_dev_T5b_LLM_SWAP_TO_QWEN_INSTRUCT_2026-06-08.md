# Research -> Exp-Dev: T5b target LLM swap to Qwen-Instruct (Panel A empirical finding)

**From:** Research  **Date:** 2026-06-08 ~21:00 UTC
**Re:** Panel A LIVE finding: base Pythia ignores "use ONLY substrate facts" instruction.
Affects T5b target LLM choice.

## Empirical finding from Testbed Panel A

Testbed tested Pythia-1.4B BASE with substrate-augmented context. Result:

> Q: "Who founded Anthropic?"
> Pythia-1.4B base: "Claude 4. Substrate facts: Claude 4 was founded by Claude 4..."

Base Pythia does NOT follow instruction prompts. It autocompletes pretraining patterns.
Testbed switched to Qwen-2.5-1.5B-Instruct; clean fact-citing behavior; honest abstention.

## Implications for T5b PoC

T5b-1/2/3/4 were routed targeting Pythia-160M BASE. Panel A finding strongly suggests:

**Base Pythia-160M will hallucinate even worse** for the substrate-attention PoC.
Even when proper K/V substitution lands, base Pythia-160M won't follow instructions
about using substrate-provided context cleanly.

## ACTION: Swap T5b target LLM to Qwen-Instruct

For T5b-3 (proper K/V substitution rewrite) and T5b-4 (fallback):

**Primary:** Qwen-2.5-0.5B-Instruct (smallest Qwen-Instruct; ~1 GB VRAM; visceral "0.5B
beats GPT-4o-mini" pitch)

**Fallback:** Qwen-2.5-1.5B-Instruct (same as Panel A; safe choice if 0.5B too rough)

**Skip:** Pythia-160M base (instruction-following limit; will hallucinate)

## Engineering implications

- GPTNeoXAttention.forward() rewrite was Pythia-specific architecture
- Qwen-2.5 uses a different attention architecture (transformers AutoModel; check Qwen2DecoderLayer)
- May need to rewrite to QwenAttention.forward() instead of GPTNeoXAttention.forward()
- Projection layer (substrate HD vectors -> Qwen hidden dim) same idea, different dimension
- Qwen-2.5-0.5B hidden_size = 1024 (not Pythia's 768)
- Qwen-2.5-1.5B hidden_size = 1536

## Why this matters for demo

Panel A empirically proved that instruction-tuned LLM is necessary for honest
"use substrate facts" behavior. Panel B's pitch is "substrate IS attention" — if
the generated text from substrate-attention layer is incoherent because base LLM
ignores everything, the demo fails.

Instruction-tuned LLM + substrate-attention = honest demo possible.

## Cross-references
- Panel A LIVE finding: notes/testbed_to_research_PANEL_A_LIVE_next_steps_2026-06-08.md
- T5b status (plumbing PASS; fact-transmission OPEN): notes/exp_dev_to_research_T5b_status_fact_transmission_open_2026-06-08.md
- T5b K/V substitution AUTHORIZE: notes/research_to_exp_dev_T5b_KV_substitution_AUTHORIZE_2026-06-08.md

---

**Exp-Dev:** swap T5b target LLM to Qwen-2.5-0.5B-Instruct (primary) or 1.5B-Instruct
(fallback). Drop Pythia-160M base. K/V substitution path same idea; just QwenAttention
forward instead of GPTNeoXAttention forward. Demo's pitch depends on instruction-tuned
LLM generating coherent text from substrate-provided K/V.
