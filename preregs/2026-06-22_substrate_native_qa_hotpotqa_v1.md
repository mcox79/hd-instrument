# substrate_native_qa_hotpotqa_v1 -- pre-reg

**Date locked:** 2026-06-22
**Anchor name:** substrate_native_qa_hotpotqa_v1
**Routing:** overnight_queue (GPU) per Fix #22 (matmul-heavy retrieval at HotpotQA scale; N_DIM 8192)
**Strategic alignment:** direct substrate-as-LLM-substitute proof-of-concept (USER L1 vision)
**Design source:** notes/substrate_native_qa_hotpotqa_generation_v1_design_2026-06-22.md

## Composes (chain-grade primitives)

1. `hdlab/char_trigram_encoder.CharTrigramEncoder` -- substrate-native text -> HD vector
2. `hdlab/kg_traversal.KGStore` -- multi-value Hebbian KG, h_hotpotqa-style ingest (CERT 588 family)
3. `hdlab/generation.SubstrateGenerator` -- autoregressive generation over S matrix (CERT 587 family)

## Pipeline (zero LLM forward calls at inference)

```
question text
   |
   v
char_trigram_encoder -> q_hd (HD vector)
   |
   v
KGStore.score_all(q_hd as bound key) -> top-K candidate entities by HD similarity
   |
   v
SubstrateGenerator.generate(start_key=top1_entity_HD, depth=4)
   |
   v
codebook-NN of generated keys -> entity names (answer)
```

Substrate-only-decode gate: `_LLM_CALL_COUNTER == 0` asserted at exit.

## Three arms (Fix #16 discriminator-regime)

1. `SUBSTRATE_COMPOSED`: full pipeline above (retrieval + generation)
2. `RETRIEVAL_ONLY`: KGStore top-1 = answer (no generation)
3. `GENERATION_ONLY`: SubstrateGenerator from question-encoded HD alone (no KG W matrix; uses
   only codebook-NN + sequence matrix built from question itself; effectively a "no-grounding"
   ablation)

## Pre-reg HARD bands

**HARD_PASS** (locked; substrate-as-LLM-substitute proof-of-concept passes):
- `SUBSTRATE_COMPOSED` exact-match (EM) on HotpotQA dev (1000-question subsample) `>= 0.20`
- AND `(SUBSTRATE_COMPOSED_EM - max(RETRIEVAL_ONLY_EM, GENERATION_ONLY_EM)) >= +0.05`
  (composition lift; the COMPOSED arm beats best per-primitive arm by >= 5pp)
- AND `n_llm_calls == 0` (substrate-only-decode gate intact)
- AND cv across 3 seeds for `SUBSTRATE_COMPOSED_EM` `<= 0.10` (looser than c3/n8 0.05 because
  the EM metric on HotpotQA is granular and seed-sensitive)

**HARD_FAIL**:
- `SUBSTRATE_COMPOSED_EM < 0.10` (substrate cannot do grounded QA)
- OR `SUBSTRATE_COMPOSED_EM <= max(RETRIEVAL_ONLY_EM, GENERATION_ONLY_EM)` (composition hurts)
- OR `n_llm_calls > 0` (substrate-only-decode gate violated)

**MIDDLE_BAND**: in between.

## Discriminating-regime check (Fix #16)

- The 3-arm contrast IS the discriminator. If COMPOSED >= 0.20 but lift < 0.05, that is
  MEASURED_MECHANISM at best (composition does not strictly help; primitives already
  carry the signal).
- If all arms collapse to near-zero EM (< 0.05) -> mechanism null OR encoder-substrate
  geometry collapse (similar to MedQA-style HARD_FAIL on h_hotpotqa pretest).
- If COMPOSED > 0.20 AND lift >= 0.05 -> composition is load-bearing; chain-grade
  substrate-as-LLM-substitute existence-proof.

## Calibration targets (background)

- Reference: GPT-3.5 HotpotQA dev EM ~0.35; substrate-native at 0.20 = 60% of GPT-3.5
  with ZERO LLM forward calls = positive proof.
- h_hotpotqa retrieval alone landed setrecall@M=1.000 (CERT 588) but EM on full QA is
  harder (answer is often the bridge entity OR a yes/no for comparison questions).

## Per-arm metrics (Fix #28)

Each seed writes per-arm:
- `em` (exact-match rate over N_Q questions)
- `retrieval_recall_at_5` (gold-answer in KGStore top-5 candidates)
- `generation_n_distinct` (distinct entities visited during generation; collapse detector)
- `arm_wall_s`

## Routing + cost

- N_DIM = 8192 (LLM-class storage); N_Q = 1000 (subsample of 7405 HotpotQA dev for wall budget)
- 3 arms x 3 seeds x 1000 questions; matmul-bound at KGStore.score_all step
- Routes to `overnight_queue` GPU; target GPU util >= 50% in smoke per Fix #24
- Estimated wall: 30-60min on GPU

## Fix inventory

- Fix #1-#13 standard pipeline; Fix #14 ship in budget; Fix #16 3-arm discriminator
- Fix #17 measurement strict (per-arm EM from sub-records, not pooled)
- Fix #22 GPU routing for N_DIM >= 8192
- Fix #23 smoke runs on remote (this cell's smoke is local laptop CPU at N_DIM=2048 / N_Q=50 /
  1 seed -- substrate-only-decode gate verifiable at any N)
- Fix #24 torch.cuda + batched ops + concurrent seeds + GPU util >= 50%
- Fix #26 predispatch_check PROCEED (verified 2026-06-22)
- Fix #28 per-arm metrics in `per_unit` list (one record per (seed, arm))

## Self-tests (`--self-test`)

1. CharTrigramEncoder.encode("apple") returns shape (n_dim,) bipolar vector with norm > 0
2. KGStore.predict_one_hop_topk returns top-k entity indices (sanity)
3. SubstrateGenerator.generate(start, depth=2) returns list of length 2 with codebook indices
4. `_LLM_CALL_COUNTER[0] == 0` after smoke

## Honest scope

- HotpotQA-distractor 1k-dev (file: data/datasets/hotpot_qa_distractor_dev_1k.jsonl)
- N_DIM=8192 (LLM-class but not max)
- char-trigram encoder (no MiniLM; substrate-only-decode at encode too) -- accepts
  semantic-loss tradeoff per char_trigram_encoder.py docstring
- Subsample 1000 questions for wall budget; full 7405 dev questions exceeds 3-arm x 3-seed
  GPU budget. Pre-reg conditions are on the 1000-question subsample only.
- Phase 1 substrate-only-decode; Phase 2 (deferred) MiniLM-encoded version for semantic
  ceiling.
