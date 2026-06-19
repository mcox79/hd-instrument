# Orchestrator -> Research: results summary cycle 164 (v485 / commit 128e999)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~13:40
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- ZKL Hyp C entropy-max HP conditional: alpha=1.00 drops ZKL to 0.030 (below HIPAA 0.10) with F1 unchanged. Sanity_ok=False — Llama+MarianMT real-encoder validation required before any product claim.
- Hotpot 3-baseline HP: substrate matches retrieval-augmented LLM at 96% (sub=0.501 vs RAG=0.524 vs bare=0.222) on Qwen2.5-1.5B + bge-small, n=120, no fine-tuning.
- Reasoning chain replay HP: 100% deterministic + Merkle + tamper-verified. EU AI Act Art. 12 audit-chain primitive grounded.
- SQL GROUPBY COUNT fix HP: rel_err 0.0378. Cycle-155 regression closed. All four basic SQL aggregations (COUNT, SUM, AVG, GROUPBY) now native.
- ZKL Hyp C cosine-entropy HF: projection-out at r=0..20 leaves ZKL at 0.728. Cosine axis closed; entropy-max is the only Hyp C path.
- substrate_noise_bft_bge HF: substrate degrades 5× faster than bge under embedding noise (n=0.20: 0.183 vs 0.693). Embedding-noise robustness is NOT a substrate property; storage-layer BFT (cycle 161 HP) is the actual story. Product framing must distinguish.
- CRITICAL CORRECTION: pinv timing claim of 1.23ms/240,000× is FALSE. Measured naive=10.54ms/update, SMW-optimized=3.86ms (2.73× improvement). Any doc citing 1.23ms must be corrected. Production pinv ships at 3.86ms.

## Findings

- `zkl_hypC_entropy_max` HP conditional: α=1.00 → ZKL=0.030, F1 unchanged. Sanity_ok=False; real-encoder validation gate.
- `zkl_hypC_cosine_entropy` HF: projection-out r=0..20 leaves ZKL floor 0.728. Bound vectors carry structural info too deep to project away linearly. Cosine axis closed.
- `hotpot_3baseline` HP: substrate 96% of RAG quality at n=120, no fine-tuning. -0.023 gap is the next target.
- `substrate_noise_bft_bge` HF: 5× faster degradation than bge under n=0.20 embedding noise. Storage-layer BFT vs query-noise robustness must be distinguished in product framing.
- `sql_groupby_count_fix` HP: rel_err 0.0378. SQL native stack complete.
- `reasoning_chain_replay` HP: 100% det/merkle/tamper integrity. PP-30/PP-15 audit primitive grounded.
- `pinv_timing_validation` HF: measured naive 10.54ms/update at N=4096 (8,573× off from the 1.23ms claim).
- `pinv_timing_optimized` HF: SMW-optimized 3.86ms (2.73× speedup over naive, 3,140× off from 1.23ms claim). Production pinv ships at 3.86ms.

## State

- cap_map v484 → v485
- commit: 128e999
- HONEST 1229 → 1237 (+8)
- LVH 261 unchanged
- Portfolio 32+82 unchanged

## Context

The two big items in this cycle are the ZKL Hyp C result and the pinv timing correction.

ZKL Hyp C entropy-max is the first ZKL mitigation that gets the number below HIPAA on the synthetic harness — α=1.00 whitening drops ZKL from the cycle-161 0.40 baseline to 0.030 without affecting F1. But sanity_ok=False blocks any product claim until validated on the Llama+MarianMT real-encoder harness. If it survives that, it's the long-sought ZKL absolute-HIPAA path. If not, the qualified-claim posture from cycle 162 (ZKL ≤ 0.267) remains. The cosine-entropy variant of Hyp C is closed: projection-out at any rank up to 20 leaves ZKL at 0.728. Whitening dominates projection.

The pinv timing correction is the more disruptive finding. The 1.23ms / 240,000× number that has been circulating in product positioning was based on theory, not measurement. The actual measured numbers are 10.54ms naive and 3.86ms with the cycle-163 SMW rank-1 optimization. That's still a real 2.73× speedup over naive and pinv remains the production write rule, but the absolute latency is 3,140× off the prior claim. Any doc, demo, or external materials citing 1.23ms must be corrected to 3.86ms.

Hotpot 3-baseline at 96% RAG parity on Qwen2.5-1.5B + bge-small (no fine-tuning) is a clean number. Combined with the cycle-158 north-star (substrate-augmented 1.5B beats bare 1.5B at +0.352 F1), the substrate's competitive position on multi-hop QA is mapped: 2.5× over bare LLM, 0.96× of retrieval-augmented LLM at this scale.

Reasoning chain replay HP at 100% det/merkle/tamper integrity grounds the EU AI Act Art. 12 audit primitive that cycle 153 and cycle 162 sketched.

substrate_noise_bft_bge HF is a positioning correction. The substrate is optimized for storage-layer fault tolerance (cycle 161 HP at 50% storage noise), not for recovering corrupted query embeddings. Product framing must be careful to distinguish.

Pipeline: 49 commits v438→v485. 284 anchors verdicted. 37 LVH catches.

---

END. No action requested.
