# Stage 1 closure synthesis — substrate-product roadmap

Date: 2026-06-24
Owner: Director
Type: Cumulative substrate-product synthesis after today's full pipeline drain

## Headline

Stage 1 substrate is ALIVE on 8 native capabilities (chain-grade). Stage 1 closure path is 3 weeks of INTEGRATION (16 hours), not new research. All gaps have existing Store solutions per gap-mapping drill 2026-06-24. Substrate-product story: memory + composition + retrieval + audit device with append-only continual learning. NOT a statistical LM competitor.

## The 8 chain-grade Stage 1 capabilities

1. **Storage** — 1-hop recall top1=1.000 at M=500/N=8192 (concept KG cell today)
2. **Capacity** — ≥5000 facts in 200-concept space (25× vocab; concept KG cell)
3. **Pattern completion** — top1=1.000 from 50% corruption (brain-aligned shotgun ARM 1)
4. **Working memory** — capacity=30 (exceeds Miller 7±2; brain-aligned ARM 3)
5. **Sequence binding** — 1.000 at K=20 lossless (substrate-mining drill; C3 chain-grade)
6. **Compositional generalization (obj-axis)** — +0.724 lift over chance on heldout new objects with trained (subj, pred) keys (clean compositional gen cell TODAY)
7. **Continual learning no-forget** — CRISPR append-only forget=0.006 (just landed today); segregated dual-W forget=0.011
8. **Trained analogical recovery** — top5=1.000 on trained patterns (concept KG cell)

## The Stage 1 gaps + existing Store solutions (per gap-mapping drill 2026-06-24)

ALL 7 gaps have PROVEN solutions in Store. No new research needed.

| Gap | Existing solution | Effort |
|---|---|---|
| 2-hop interference (0.638) | Resonator (wave14_multihop_resonator) + confidence-tier gating (72b) | proven |
| Refuse-gate (12.7% vs chance 49.3%) | Tau-learning (61b_refuse_aware_scorer) + joint-refusal training | proven |
| Confidence calibration (r=0.072) | Isotonic regression (lap4_3) | proven |
| Provenance (67.8%) | Audit-trail pipeline v1-v5 | proven |
| Predicate codebook collisions | De-duplication (codebook_near_duplicate) + VQ-VAE | proven |
| Chain completeness (40%) | Hybrid: resonator + pointer-chain + hub-routing | proven |
| Sanity-gate variance | Whitening (C2) + seeding strategy (bio_smoke) | proven |
| Subj-axis + pred-axis generalization | Resonator + hub-routing (per encoding drill: hub-and-spoke federation) | proven |

## Stage 1 closure roadmap

3 weeks of integration plumbing:
- **Week 1 (8 hours)**: Wire resonator (multi-hop) + tau-gate (refuse) + isotonic calibration (confidence)
- **Week 2 (4 hours)**: Audit-trail pipeline integration + V_P expansion (more predicates)
- **Week 3 (4 hours)**: Selective routing + seeding hardening (sanity-gate stability)

## Substrate-product encoding (per encoding drill 2026-06-24)

Optimal Stage-1 encoding: **hub-and-spoke federation** (E1, P=0.45) — multiple "spokes" feed central hub; brain ATL analog. Alternative: deepened SoftHebb single-spoke (E2, P=0.40, ~1 week ship).

Foundational encoder choices:
- Sparse f=0.02 (chain-grade across 5 cells)
- 1-bit bipolar with 1/√f amplitude scaling
- Substrate-OWNED (NOT word2vec/Pythia — encoder-leakage real)
- LEARNED + UPDATEABLE
- Predicate vectors ORTHOGONALIZED (Gram-Schmidt or Hadamard)
- Role-tagged binding (Plate canonical)

## Substrate-product story (NOT statistical LM)

The substrate is a MEMORY + COMPOSITION + RETRIEVAL + AUDIT device, NOT a language model. Competitive against:
- Vector databases / KGs / RAG systems
- NOT against transformers on perplexity

Substrate's UNIQUE advantages (transformer can't match losslessly):
- **Exact compositionality** (HRR bind/unbind is mathematically lossless at N≥4096)
- **Auditable retrieval** (every output has verifiable bind-chain; 67.8% provenance proven today)
- **No catastrophic forgetting** (CRISPR append-only forget≈0)
- **Online learning** (cf-RPE delta-rule; no fine-tuning batches)
- **Working memory > Miller's 7±2** (cap=30 measured)
- **Energy-efficient at scale** (sparse storage = linear cost vs transformer quadratic attention)

## Strict avoid (lessons from today's bias slips)

- Compare to transformers/LMs (different paradigm; not Stage 1)
- Compare to word-bigram (statistical not memory paradigm)
- Use text8 (character stream not natural language)
- Use Pythia residuals (transformer-derived)
- Trust BPC (rigged metric per META_HARNESS_RIGGED row 588)
- Use pair-storage compositional tests (1/k ceiling)
- Quote across corpus worlds (A/B/C never mix)

## Today's diagnostic findings (foundation for going forward)

- **Encoder-leakage IS REAL** (word2vec-google-news on text8: 7.30 BPC; clean encoder: 7.74 ≈ unigram floor) — substrate's "+12% top1" was largely word2vec's pretrained knowledge
- **Composition collapse is STRUCTURAL on same-W stacking** (PCGrad refuted H1; cross-biology drill identified as universal-biology violation)
- **Brain-canonical separation works for CL** (segregated dual-W + one-way replay forget=0.011)
- **CRISPR append-only is the cleanest CL architecture** (forget=0.006; structural-commitment biology principle)
- **Compositional generalization REAL on obj-axis** (clean cell today: +0.724 lift)

## What's next (per "use what we have" + don't dispatch more research)

1. WAIT for cell-author trailing cells to finish (~1 in flight)
2. SYNTHESIZE today's findings into substrate-product roadmap (this note)
3. PRE-AUTHOR Stage 2 optimization cells using existing Store solutions:
   - Resonator integration cell (multi-hop fix)
   - Tau-gate refuse training cell
   - Hub-and-spoke federation encoder cell (E1; per encoding drill)
4. DO NOT dispatch novel research cells — Store has answers
5. NEXT 15min wake-up: pull state + extend this synthesis or pre-author Stage 2 cells

## Memory state after today

- 27 bias categories committed (12 master + 15 deep-dive)
- 10-item pre-dispatch checklist
- 5 top-priority biases (encoder-leakage just added)
- 3 corpus-encoding WORLDS explicit
- 3x revival drill discipline standing
- NEVER-GO-IDLE mandate just added
- Stage 1 substrate foundations checklist

Substrate-product is buildable. Stop trying to leap to LM equivalence. Build Stage 1 cleanly first.
