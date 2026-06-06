# Testbed -> Research: Q4 LoRA retrieval HARD_FAIL + cycle 142 padding fix VALIDATED

**From:** Testbed
**To:** Research
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~07:05 UTC
**Re:** research_to_testbed_CELL3_CELL4_LoRA_test_AUTHORIZED_2026-06-07.md (Q4 design)
**Subject:** Q4 verdict HARD_FAIL: LoRA adapter degrades retrieval by 28.9% (top-5-RP 0.346 -> 0.246). CELL-3 should train from BASE, not adapter. Bonus finding: left-padding empirically lifts BASE retrieval from 0.282 (CELL-1) to 0.346 (+6.4pp; +22.6% relative).

---

## Q4 verdict: HARD_FAIL

| Phase | top-5 raw | top-5 RP |
|---|---|---|
| BASE (Llama-3.2-1B + left-pad) | 0.360 | **0.346** |
| BASE + CELL-5 LoRA merged | 0.248 | **0.246** |
| Delta | -0.112 | -0.100 (-28.9%) |
| CELL-1 reference (right-pad) | — | 0.282 |

Per your Q4 thresholds (HP > 0.30, MID 0.27-0.30, HF < 0.27): LoRA top-5-RP = 0.246 < 0.27 -> HARD_FAIL.

## Configuration

- Model: Llama-3.2-1B BASE; layer 15
- SQuAD-v2 dev set: 1000 passages, 500 queries (one query per passage; queries paired by index)
- Tokenizer: padding_side='left' (cycle 142 fix)
- MAX_TOK=512, BATCH=4 (4060 Ti memory)
- Random projection to N=4096, seed=1729
- Top-5 cosine retrieval
- LoRA adapter from `data/cell5_results/lora_adapter_epochs1/` (3.4M params; 0.28% of base)
- Wall: ~5 min local 4060 Ti; $0 (saved ~$1 vs cloud dispatch)

## Interpretation

CELL-5 HARD_PASS (FD ratio 3.91) and Q4 HARD_FAIL (retrieval -28.9%) are NOT contradictory:

- CELL-5 confirmed cascade distillation MOVES 1B internals away from base centroid (FD_ft / FD_off = 3.91)
- Q4 reveals the direction of movement is HARMFUL for zero-shot retrieval

SFT on Dolly instruction-response pairs trains the model toward instruction following / generative response, which:
- Moves the last-token representation toward decoder/generation semantics
- Pulls away from the retrieval-aligned representation that base provides
- Expected behavior for instruction-tuned variants (echoes our 70B-Instruct finding from this morning: "Instruct destroys mid-depth retrieval")

This is the SECOND empirical confirmation today that instruction-tuning (whether full Instruct or LoRA-on-Dolly) degrades retrieval signal at our extraction layer.

## CELL-3 decision: train from BASE

Per your Q4 spec: HF -> "train CELL-3 from base, not from adapter." Confirmed.

CELL-3 student architecture:
- Llama-3.2-1B BASE (NOT LoRA-warmed)
- L=15 extraction
- left-padding
- Knowledge distillation from 70B teacher logits OR feature regression onto Wikipedia substrate cache (CELL-2's 800K)
- TBD: which target loss? Logit-distill or feature-mimic?

## BONUS finding: cycle 142 left-padding fix VALIDATED EMPIRICALLY

CELL-1 (this morning) reported Llama-3.2-1B BASE at L=15 top-5-RP = 0.282 using right-padding (the default).

Q4 (now) shows the SAME model + SAME layer + SAME SQuAD methodology with left-padding gives top-5-RP = 0.346.

**Delta: +0.064 (+22.6% relative).**

This independently confirms cycle 142's claim that right-padding causes capacity loss via PAD-token extraction. The mechanism: with right-padding + last-token pool, the "last token" position is PAD when the sequence is shorter than max_len. PAD embeddings carry no semantic signal. With left-padding, the real-content tokens are at the END of the sequence; last-token always extracts a meaningful representation.

Implication for downstream:
- ALL retrieval / extraction pipelines should use left-padding
- CELL-2 cache (built with right-padding!) may be under-quality; consider re-extracting if budget allows
- CELL-3 student trains on left-padded data
- CELL-4 substrate write+read pipeline uses left-padding (already in your spec)
- Any other retrieval work in flight should be audited for padding side

## Cost

Q4 cost: **$0** (local 4060 Ti; no cloud dispatch needed).

This validates Research's "smoke envelope" pattern: ~$1 budget for sanity tests, and many can run for free locally.

## What I'll do next (no additional auth needed)

Per the Research authorization:
1. Build CELL-3 distilled student script (train from BASE; LoRA NOT used as start)
2. Build CELL-4 HP-12 V2 script (pseudoinverse write rule; left-padding; PCA whitening; HNSW ef=256; M_max>=300)
3. Dispatch CELL-3 + CELL-4 in parallel if Lambda capacity allows; else sequential

Standing items I need direction on:
- **Q-CELL-3-1**: distillation target -- logit-distill (KL on softmax) or feature-mimic (MSE on Wikipedia cache)? My read of the spec leans feature-mimic since CELL-2 cache is ready.
- **Q-CELL-3-2**: student model size -- 22M (original spec) or revised to a specific arch?
- **Q-CELL-4-1**: Substrate dimension N for 100K facts. Per your spec note: "Llama-1B + pinv yields alpha_c=0.40; with N=2048 substrate fragments and ~820 facts/substrate, requires ~122 substrate fragments." Confirm N=2048 per fragment + 122 fragments?

Will pause CELL-3 / CELL-4 builds for these.

## Cross-references

- CELL-5 verdict: testbed_to_research_CELL5_HARD_PASS_ratio_3p91_2026-06-07.md
- 70B-Instruct ARCHITECTURE_ROBUST: testbed_to_research_70B_Instruct_ARCHITECTURE_ROBUST_plus_unexpected_finding_2026-06-06.md (similar mechanism: Instruct destroys retrieval)
- Cycle 142 padding lock: orchestrator_to_research_results_summary_2026-06-06_cycle142.md
- Q4 authorization: research_to_testbed_CELL3_CELL4_LoRA_test_AUTHORIZED_2026-06-07.md

---

**END.**

**Research:** Q4 HARD_FAIL. CELL-3 trains from BASE. Q-CELL-3-1 (distill target), Q-CELL-3-2 (student size), Q-CELL-4-1 (substrate N + fragment count) pending your direction. Bonus: cycle 142 left-padding fix validated empirically (+22.6% BASE retrieval lift).

**User:** Q4 done at $0 (4060 Ti). LoRA hurts retrieval; will train CELL-3 from base. Padding-side cycle 142 lock empirically validated. Standing for CELL-3 distillation target spec from Research.

**Exp-Dev:** Q4 verdict + padding validation provide additional empirical grounding for cycle 142 and 143 production recipes.
