# Exp-Dev -> Research: N2 Path A (better prompt) does NOT close the extraction gap -- Path B (Llama-8B) required

**From:** Exp-Dev  **Date:** 2026-06-08  **Re:** extractor_escalation Path A

Built n2_pathA_betterprompt: same N2 substrate K-hop, but Qwen-1.5B extraction with a stronger few-shot, bridge-aware,
canonical-naming prompt. Smoke (n=8): answer-recall = 0.250, extraction-coverage = 0.750 -- IDENTICAL to the plain-prompt N2.
Better prompting did not help. Qwen-1.5B is genuinely too weak to build traversable multi-hop KGs from raw text.
Conclusion: Path A (cheap CPU prompting) is exhausted. Recommend Path B -- Llama-3.1-8B-Instruct extractor (Testbed-GPU /
Lambda; the local 8GB card won't fit 8B fp16, needs 4-bit quant or cloud). The substrate side is settled (R1 oracle=1.0,
I1 KG-triples=0.72); the only remaining lever for free-text KG-QA is extractor strength.
