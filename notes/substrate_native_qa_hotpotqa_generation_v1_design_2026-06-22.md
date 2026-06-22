# Substrate-native QA on HotpotQA (g1b generation × h_hotpotqa KG) — cell design

**Date:** 2026-06-22 (Director pre-design; substrate-mining-derived from today's 6 chain-grade atoms)
**Anchor name:** substrate_native_qa_hotpotqa_v1
**Status:** design draft; ready to dispatch when capacity opens
**Strategic alignment:** direct substrate-as-LLM-substitute proof-of-concept (USER L1 vision)

## What this cell does

Compose two chain-grade primitives into a substrate-native QA pipeline:

- **Retrieval**: `hdlab/kg_traversal.KGStore` loaded with HotpotQA Wikipedia KG (per CERT 588 cell)
- **Generation**: `hdlab/generation.SubstrateGenerator` (per CERT 587 g1b cell) emits entity sequence as the answer

Pipeline:
```
question (text) → char_trigram_encoder → query HD vector
                    ↓
              KGStore.predict_n_hop(query, n=2) → candidate entities ranked by HD similarity
                    ↓
              top-K entities → SubstrateGenerator(prefix=question_entities + top_K) → answer entity sequence
                    ↓
              answer entities → readable text (entity-name lookup; NO LLM)
```

Zero LLM forward calls at inference (substrate-only-decode gate preserved).

## Why this is high-leverage

1. **First substrate-native QA cell on a real benchmark** (HotpotQA), not just KG retrieval or generation in isolation.
2. **Tests composition of two chain-grade primitives** — does composition preserve chain-grade-quality, or does noise compound?
3. **Direct USER L1 vision**: substrate replaces LLM for grounded QA at LLM-class scale.
4. **Disambiguating result**: if it works, substrate-as-LLM-substitute has a real existence proof; if it fails, identifies the next composition gap.

## Discriminator (Fix #16 — mechanism-discriminating bands)

3 arms required to discriminate composition-effect from per-primitive performance:

1. **SUBSTRATE_COMPOSED**: full pipeline above (retrieval + generation)
2. **RETRIEVAL_ONLY**: KGStore output ranked top-1 = answer (no generation)
3. **GENERATION_ONLY**: SubstrateGenerator from question-words alone (no KG retrieval)

The COMPOSED arm should beat both per-primitive arms. If it doesn't, composition is hurting; that's a finding.

## Pre-reg HARD bands

- **HARD_PASS**: SUBSTRATE_COMPOSED EM (exact match) on HotpotQA dev ≥ 0.20 AND (COMPOSED - max(RETRIEVAL_ONLY, GENERATION_ONLY)) ≥ +0.05 (composition lift). n_llm_calls = 0.
- **HARD_FAIL**: SUBSTRATE_COMPOSED EM < 0.10 OR COMPOSED ≤ max(per-primitive) (composition hurts).
- **MIDDLE_BAND**: in between.

Targets calibrated against:
- h_hotpotqa retrieval alone landed setrecall=1.000 (CERT 588) but EM on full QA is harder; 0.20 is conservative-positive
- Reference: GPT-3.5 at HotpotQA dev EM ~0.35; substrate-native at 0.20 = 60% of GPT-3.5 with ZERO LLM forward calls = positive

## Cost / routing

- **Wall**: ~30-60min (10k HotpotQA dev questions × ~200ms per question × 3 arms × 3 seeds)
- **Compute**: matmul-heavy at N=8192-16384; route to **overnight_queue (GPU)** per Fix #22 routing rule
- **GPU util**: KGStore.predict_n_hop is batched matmul; expect ≥50% util per Fix #24

## Pipeline (Fix #11 + Fixes #1-#28)

Standard. Pre-dispatch checks:
- `python tools/predispatch_check.py substrate_native_qa hotpotqa_generation` (already PROCEED per Fix #26)
- Verify hdlab/kg_traversal + hdlab/generation + hdlab/char_trigram_encoder are current
- Smoke on remote (Fix #23): use 50 HotpotQA dev questions for smoke; full uses 1000 (subsample dev set; full HotpotQA dev is 7405 questions which exceeds reasonable wall budget for 3 arms × 3 seeds)
- Fix #28: read per-arm metrics in verdict; don't summarize verdict_msg

## When to dispatch

Currently 3 cells in flight (r2 + c2 + v2c). Per Fix #14 spawn budget + Fix #27, dispatch this cell when:
- ≥1 of {r2, c2, v2c} lands (frees spawn budget for next cycle), AND
- v2c outcome doesn't change the priority (if v2c lands HARD_PASS, autoatom Phase 2 cell becomes higher priority)

Estimated dispatch window: 30-90 minutes from now (whenever the first of the 3 in-flight cells lands).

## Composes with

- **Already-shipped**: hdlab/kg_traversal (CERT 584/585/588), hdlab/generation (CERT 587), hdlab/char_trigram_encoder (substrate-native encoder)
- **Strengthens**: p1 v2 LLM-class evidence (composition survives at LLM-class storage)
- **Falsifies if HARD_FAIL**: substrate-as-LLM-substitute REQUIRES new composition primitive (not just better per-primitive)

## What this does NOT need

- New hdlab/ primitive (all required primitives already shipped)
- New research drill (composition pattern is well-defined from prior cells)
- LLM forward calls (substrate-only-decode gate preserved)
- New benchmark (HotpotQA already ingested at CERT 588)

— Director (pre-design; ready when capacity opens)
