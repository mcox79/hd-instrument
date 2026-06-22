# MedQA n8-pattern ingest HONEST_NEGATIVE — encoder mean-pool collapse on long medical text

**Date:** 2026-06-22
**Cell-author spawn:** adbc6cfd07327f7e7 (hdi_exp_dev; halted-and-reported)
**Cell:** `experiments/exp_m_medqa_ingest_v1.py` — authored, NOT committed (diagnostic-only)
**Smoke metrics:** `data/exp_m_medqa_ingest_v1/metrics.json` (HARD_FAIL; valid discriminator per Fix #16)

## Headline

The n8/U1 multi-value Hebbian ingest pattern does NOT work as-is on QA-pair corpora when the encoder is pythia-160m mean-pool and the question text is long uniform-topic English (medical USMLE vignettes). Root cause is encoder geometry, not substrate mechanism.

## Smoke evidence

```
setrecall@1 = 0.020 (random-control = 0.020; ratio 1.00x; needed >= 2.0x)
refuse_OOD = 1.000 (trivially — everything is noise)
accept = 0.880 (above floor but uncalibrated since signal is noise)
cv = 0.000
zero_llm_calls_at_inference = True (substrate-only gate intact)
```

Per Fix #16 disaggregation: harness OK (self-test PASSED 1.00 recall on synthetic; random-key control collapsed to 0.07 in synthetic). Real-data: discriminator fires HARD_FAIL — substrate is at chance.

## Root cause (diagnosed by spawn off encoder outputs)

- pythia-160m mean-pool over USMLE clinical vignettes (80-120 tokens of dense medical English) produces **NEAR-UNIFORM embeddings**.
- Q vs Q+A diagonal cosine = 1.0; **off-diagonal cosine = 0.9865** (everything looks the same).
- Adding `[ANSWER] short_text` to a long question shifts the mean-pool by **<2% in cosine** — the answer signal is washed out by mean-pooling over the long context.
- Direct encoder-cosine on the 50×50 Q-vs-Q+A matrix DOES give top-1 = 1.0 (diagonal is exactly 1.0), but the Hebbian superposition `W = sum outer(E_qa[i], key_i)` collapses the 0.99-overlap soup to a single attractor with no per-pair routing.

## Substrate-methodology atom proposal

**Atom-id candidate:** `META_encoder_mean_pool_over_long_uniform_topic_text_collapses_keysep_needs_contrastive_projection`

**Body:** When using a frozen encoder (pythia-160m mean-pool, BERT-mean-pool, etc.) for substrate ingest of long uniform-topic text (medical vignettes, technical abstracts, etc.), the mean-pool operation washes out per-instance differentiating signal — off-diagonal cosine approaches 1.0; Hebbian superposition collapses to a single attractor. The chain-grade ingest pattern (n8/U1) implicitly assumes the encoder preserves recoverable per-instance keysep. For long uniform-topic corpora, this assumption fails. Mitigation: learned contrastive projection (n9 pattern) to create explicit keysep before Hebbian write.

**Composes with:**
- n9 lineage (`exp_n9_smh_sparsemax_decode_v1`) — learned contrastive projection mechanism
- Fix #16 discriminator-regime check (caught this; smoke is HARNESS-OK + MECHANISM-INVALID)
- verify-the-referent (refuse=1.0 isn't a real refuse signal when everything is noise; flagged)

**Disposition:** META cert-class (audit_lesson); discipline_meta cert-trail; no CERT increment.

## Three options surfaced by spawn

A. **Pivot to learned contrastive projection v2:** train a (D_enc → N_DIM) projection on a 250-pair train split to maximize Q-vs-Q+A diagonal-vs-off-diagonal margin, ingest 250 held-out pairs. Adds ~2-5min cell wall. P(HARD_PASS) = moderate.
B. **Pivot to n8-pure random bipolar (no encoder):** treats MedQA as 500 random triples; proves substrate memorizes 500 facts but NOT medical-domain-specific. AGAINST (no domain semantics retained).
C. **Defer + file the finding** as a substrate-methodology atom. v2 (Option A) authored next cycle. RECOMMENDED by spawn + Director-ratified.

## Director disposition (Option C)

- File this note as cert-trail diagnostic artifact ✓ (this file)
- Atomize the substrate-methodology finding as META atom next cycle (route to Skunkworks via spawn when budget reopens)
- Defer v2 cell-author until SCHEMA-VET on the learned-projection mechanism design clears
- **Alternative ingest queued: HotpotQA 1k** (multi-hop QA chains naturally decompose into (entity, relation, entity) triples per the FB15k-237 pattern that DID chain-grade at CERT 584; better fit for n8-style ingest mechanism without needing learned projection)

## What this confirms (information-positive)

1. The substrate's chain-grade ingest pattern is mechanism-correct (cert-grade evidence: U1 CERT 584 + n8 CERT 585).
2. The pattern's UPSTREAM assumption — that the encoder preserves per-instance keysep — fails on certain corpus shapes (long uniform-topic text).
3. The Fix #16 discriminator-regime check + smoke-VET disaggregation correctly identified the failure mode without burning remote_cpu compute.
4. The substrate-only-decode gate held at every step (n_llm_calls=0 post-ingest; pythia is ingest-stage only).

## Recently shipped (related; cross-trail)

- c3 SequenceMatrix substrate-native ordered-pair binding (CERT 586) — could provide encoder-free alternative
- char_trigram_encoder.py substrate-native text encoder — zero external model; tested on entity names (short); could be evaluated on long medical text as comparison
- Whitening primitive (hdlab/whitening.py) — could improve keysep before Hebbian write by decorrelating encoder residuals (might mitigate the mean-pool collapse partially)

— Research (Director); MedQA HONEST_NEGATIVE-at-smoke; option C disposition; cert-trail durable artifact; no addressee.
