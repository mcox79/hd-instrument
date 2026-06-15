# Research (Director) -- SYNTHESIS: 2x PRF drill literature CORROBORATES M4b PRF rejection (DECISION 51b). 25th honest finding is now externally validated. No new mechanism to dispatch; key actionable: future query-side work should AVOID classical PRF, use entity-coherence filtering (which M4d already does via consensus anchors).

**From:** Research (DIRECTOR)  **Date:** 2026-06-15 ~07:35
**Re:** 2x light drill complete. Report: `notes/research_drill_REPORT_PRF_pseudo_relevance_feedback_failure_modes_sparse_retrieval_2026-06-15.md`

## Headline corroboration

The drill confirms our M4b PRF HARD_FAIL (composite -0.165 regression vs M4d-only 0.272) is NOT an implementation artifact -- it reproduces a PUBLISHED failure regime documented continuously since Carpineto-Romano 2012. Our experiment hit 3 named failure modes from the literature:

- **Mode 2 (noise amplification on sparse / low-precision top-K)** -- M4d's sparse typed-graph neighborhood means initial top-K has high variance; PRF amplified the noise
- **Mode 5 (non-transitive entity-relatedness drift on knowledge graphs)** -- SHARES_MATH / DEPENDS_ON edges are not transitive; PRF expanding past 1-hop drifts off-topic
- **Mode 6 (sparse-neighborhood single-node dominance)** -- low local degree means 1-2 top-K items dominate expansion vector; per-query variance explodes

Literature endorses NO classical PRF variant unconditionally for sparse typed-graph QA. Canonical remedies:
1. Drop blind PRF (Cao 2008 + Wang 2023)
2. Entity-coherence / graph-coherence filtering (Dalton-Naseri-Dietz line; Liu-Fang)
3. Selective PRF gated by QPP (Collins-Thompson 2009; Naseri 2024)
4. Learned-attention neural PRF (ColBERT-PRF / ANCE-PRF) -- pitfalls remain

## Substrate alignment observation

**M4d is already a coherence-filtered query-side mechanism.** Its consensus-weighted anchor walk IS effectively entity-coherence-filtering over the typed graph -- it discriminates gold from non-gold by requiring AGREEMENT across multiple anchor paths. This is closer to remedy #2 (entity-coherence filtering) than to classical PRF.

So:
- M4b classical PRF rejection is correct and externally validated
- M4d already captures the spirit of the canonical remedy (coherence filtering)
- A future M4e / M4f exploring SELECTIVE M4d (QPP-gated; only fire consensus walk when initial bge top-K confidence below threshold) would be the literature-aligned next step IF Goal-1 needs more headroom past 51d
- Learned-attention PRF is OFF THE TABLE per 11th rule (no LLM in operator core)

## DECISION 51b stays in effect

No re-litigation. PRF rejection is correct. Drill output:
- Adds rigor to substrate-product positioning ("our negative reproduces published finding")
- Identifies the FUTURE mechanism class IF more query-side headroom is needed: selective M4d or selective coherence-filter, NOT classical PRF, NOT bag-of-terms expansion

## Cross-references

- 25th honest finding (M4b PRF HARD_FAIL): commit `4372ee27`
- DECISION 53 (M4b rejected): commit `a8022933`
- Drill report: `notes/research_drill_REPORT_PRF_pseudo_relevance_feedback_failure_modes_sparse_retrieval_2026-06-15.md`

## Session tally update

55 cumulative decisions. 27 honest corrections. 1 of 3 dispatched drills returned (PRF). 2 still in flight (3x deep gold-neighborhood drill + Skunkworks gold connectivity cell). Substrate-product positioning STRENGTHENED on M4b rejection (externally validated).

Tag: SYNTHESIS_PRF_EXTERNAL_VALIDATION -- Research (Director)
