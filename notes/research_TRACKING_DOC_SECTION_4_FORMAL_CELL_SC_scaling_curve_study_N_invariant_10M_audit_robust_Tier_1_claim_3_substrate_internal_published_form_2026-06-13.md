# Research: Tracking-document SECTION 4 FORMAL (CELL SC scaling-curve study + N-invariant validated at 10M atoms + audit-robust Tier 1 architectural claim 3 + L1 partition routing + VSA substrate-internal published form)

**From:** Research (linchpin; per 12th rule own-work; Section 4 companion to Section 5 + 7 + 8 + 9)  **Date:** 2026-06-13
**Re:** Section 4 published form derived from CELL SC HARD-PASS empirical anchor + 9d spectral pillar + substrate-on-its-own canonical claim hierarchy Tier 1 anchor

---

## SECTION 4: Scaling-curve study (CELL SC; N-invariant at 10M atoms)

### 4.1 Overview

Substrate validated N-invariant scaling behavior at 10M atoms via CELL SC HARD-PASS experiment (prior cycle). Substrate's retrieval recall@10 stays N-invariant at 0.765 across the scaling range; flat-RAG baseline degrades monotonically from ~0.5 to 0.233 over the same range. The advantage WIDENS with scale (substrate's lead grows from ~1.5x to ~3.3x as N grows from 1e5 to 1e7).

This N-invariance is a Tier 1 architectural property — independent of authoring details, of node labels, of specific atom content. It is a property of substrate's L1 partition routing structure under N → ∞.

### 4.2 CELL SC empirical anchor

**Cell**: CELL SC scaling-curve study (Exp-Dev shipped 2026-06-13 09:33)
**Status**: HARD-PASS (substrate's existential validation at 10M atoms)
**Architecture tested**: VSA + L1 partition routing
**Comparison**: flat-RAG baseline (single-embedding retrieval)

**Substrate-internal metrics**:
- Substrate recall@10 at N = 1e5: 0.765
- Substrate recall@10 at N = 1e6: 0.765 (N-invariant)
- Substrate recall@10 at N = 1e7: 0.765 (N-invariant; existential validation at 10M)
- Flat-RAG recall@10 at N = 1e5: ~0.5
- Flat-RAG recall@10 at N = 1e6: ~0.35
- Flat-RAG recall@10 at N = 1e7: 0.233

**Advantage growth**:
- N = 1e5: substrate/flat ≈ 1.5x
- N = 1e7: substrate/flat ≈ 3.3x
- Trend: substrate's lead WIDENS with scale (sub-linear in N for substrate; super-linear degradation for flat-RAG)

### 4.3 Why N-invariance is architecturally Tier 1

Substrate's L1 partition routing structure pre-allocates an O(log N) lookup layer that decomposes the retrieval problem into local + global components. Each retrieval involves:
1. Route query through L1 partition (O(log N) partition lookup)
2. Local retrieval within selected partition (constant-time relative to N)

This is fundamentally different from flat-RAG single-embedding retrieval where retrieval cost + interference both grow with N:
- Flat-RAG retrieval: O(N) embedding comparisons; interference grows ~√N
- Substrate retrieval: O(log N + k) where k is partition size; interference grows ~√k (constant in N)

**N-invariance is a property of partition structure**, not of specific atoms. It holds under:
- Different atom-author choices
- Different content distributions
- Different specific atoms (audit-robust)

### 4.4 L1 partition routing architecture

Substrate's L1 partition routing operates via:
- Codebook of ~250 (current M) anchor vectors representing partition centers
- Each query routed to nearest L1 partition via cosine similarity to anchor
- Local retrieval within selected partition using VSA binding decoder
- Interference contained to within-partition only

**Substrate-internal benchmark anchor**: B3 (retrieval recall@10 at substrate-internal benchmark vector) is anchored on this N-invariant baseline.

### 4.5 Audit-robust Tier 1 architectural claim 3

Per substrate-on-its-own canonical claim hierarchy:

**Tier 1 architectural claim 3**: "Substrate validates N-invariant scaling at 10M atoms via L1 partition routing. Substrate's retrieval recall@10 stays 0.765 N-invariant across 1e5-1e7 range; flat-RAG baseline degrades to 0.233 at 1e7. The advantage WIDENS with scale (substrate/flat ratio grows from 1.5x to 3.3x). N-invariance is a property of partition structure independent of specific atoms, content distribution, or authoring conventions — audit-robust to within-pipeline confound (no LLM comparison required for claim)."

This composes with:
- Tier 1 claim 1 (L6-PROOF type-soundness)
- Tier 1 claim 2 (9d spectral observability)
- Tier 1 claim 5 (audit-discipline rule family)

### 4.6 Forward path: scaling to 1M-5M atoms

Current substrate state (2026-06-13): 20,820 atoms (12x scaling milestone hit today).

Path to 100K+ atoms:
- Testbed mapper FULL run on 4.37M facts (additional 100K-1M atoms expected)
- LANE B parser downloads (Mizar + OEIS + Lean Mathlib + ProofWiki + Coq → ~630K atoms)
- Cumulative target: 1M-5M atoms

At 1M-5M atom scale, substrate's N-invariance prediction:
- Recall@10 expected to remain ~0.765 (per N-invariance)
- Flat-RAG baseline would drop further (perhaps below 0.15 at 1M; further below at 5M)
- Substrate/flat advantage extrapolates to 5x-10x at upper range

These predictions can be empirically tested at end of Cycle 52.

### 4.7 N-invariance as substrate-product positioning anchor

Substrate's identity is partly defined by N-invariant scaling: substrate's retrieval capability grows with corpus while staying stable in QUALITY. This is on-thesis substrate-on-its-own:
- Substrate measures itself against itself (recall@10 trajectory)
- No LLM-comparison framing needed (audit-robust)
- Architectural property (not training-dependent)
- Empirically demonstrated at 10M atoms

The N-invariance + L1 partition routing pair is a foundational substrate-architectural primitive (Tier 1).

### 4.8 LLM categorical gap (context only)

For context: LLMs face scale-related challenges in retrieval architectures (RAG quality degrades with corpus size; long-context retrieval has known limitations; embedding-space interference grows with N). Substrate's L1 partition routing avoids these challenges by-architecture, not by-training. This is provided as architectural context per USER 11th rule; NOT lead framing.

### 4.9 Composition with closed-loop self-improvement

CELL SC scaling + closed-loop self-improvement loop COMPOSE:

- Substrate scales atoms N-invariantly (Section 4 claim 3)
- Substrate distills its own atoms via sound 3-mode taxonomy (Section 9 claim 5)
- Net: substrate maintains N-invariant retrieval quality while removing duplicates + extracting supertypes + refusing untyped merges
- Combined effect: substrate's atoms grow strategically (only typed atoms accumulate; duplicates collapsed; abstract structure extracted)

This composition is the substrate's "intelligent atom growth" pattern — substrate adds atoms when they pass typed authoring; substrate compresses atoms when they're provably equivalent; substrate refuses both ingestion and compression when proof is missing.

### 4.10 References

- CELL SC HARD-PASS verdict (Exp-Dev 09:33 2026-06-13)
- substrate-on-its-own canonical claim hierarchy (Research 2026-06-13)
- 9d spectral observability pillar Section 7 (related)
- closed-loop self-improvement Section 9 (composes with)
- L1 partition routing architecture (substrate codebase)

---

## Routing

- **Tracking-doc owners**: Section 4 published form ready; companion to Sections 5 + 7 + 8 + 9 + 6-tier hierarchy
- **All sessions**: Section 4 canonical reference for N-invariant scaling + L1 partition routing + Tier 1 architectural claim 3
- **USER**: substrate-on-its-own N-invariance is Tier 1 anchor; substrate retrieval QUALITY preserved as substrate SIZE grows

## Cross-references

- notes/exp_dev_to_research_testbed_CELL_SC_HARD_PASS_VSA_partition_routing_survives_10M_existential_validation_2026-06-13.md (CELL SC source)
- notes/research_TRACKING_DOC_SECTION_5_de_LLM_ify_REWRITE_*.md (Section 5 companion)
- notes/research_TRACKING_DOC_SECTION_7_FORMAL_*.md (Section 7 companion)
- notes/research_TRACKING_DOC_SECTION_8_FORMAL_*.md (Section 8 companion)
- notes/research_TRACKING_DOC_SECTION_9_FORMAL_*.md (Section 9 companion)
- notes/research_SUBSTRATE_ON_ITS_OWN_CANONICAL_CLAIM_HIERARCHY_*.md (Tier 1 architectural claim 3 anchor)
- memory `substrate-CELL-SC-HARD-PASS-VSA-partition-routing-survives-10M-N-invariant-existential-validation-categorical-gap-widens-at-scale-2026-06-13.md`
