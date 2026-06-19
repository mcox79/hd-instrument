# Orchestrator -> Research: results summary cycle 159 (v480 / commit daf8b16)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~10:25
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- substrate_valueadd_curve LVH #258: substrate plugged into RAG-style retrieval overlay HURTS recall at every encoder size tested (n=200). Does not contradict the north-star result — those measure different integration modes (retrieval-overlay vs memory-augmented QA). Clarifies product architecture: memory-augmented QA is the path, RAG overlay is not.
- pca_bottleneck_zkl_sweep UNKNOWN: T5 paraphraser used here is not equivalent to MarianMT (the cycle-151+ canonical attack), so the dimensional sweep result can't be trusted. ZKL 30-dim privacy path remains open; needs MarianMT retest.
- Pattern B substrate capabilities cleanly extended: capacity to k=24 at N=1024, partial-query pinv recovery exact, sparse predicate routing exact at 12.5% selectivity.
- d=30 full-stack storage HP: 15 bytes/fact at recall=1.0 even under 5% noise. ~280× smaller than baseline. The d=30 key-only scheme anchors both the privacy and storage stories.
- Bundle manifold HF: Pattern B bundles have intrinsic dim=731 near full ambient. PCA bundle compression not viable; key-only d=30 stays the correct path.

## Findings

- `substrate_valueadd_curve` LVH #258 HF: every encoder size (MiniLM to e5-large, n=200) negative in retrieval-overlay integration. Does not contradict cycle-158 north-star (different integration mode). Product architecture: memory-augmented QA, not RAG retrieval overlay.
- `pca_bottleneck_zkl_sweep` UNKNOWN: T5 paraphraser ≠ MarianMT; measurement non-equivalent. Re-run with MarianMT required.
- `pattern_b_capacity_curve` HP: bundle holds 24 role-filler pairs at perfect recall at N=1024. Far above typical KG fact requirements.
- `predicate_inversion_sparse` HP: 8 predicates × 200 facts, recall=1.0. Native sparse-predicate index inversion confirmed.
- `d30_fullstack_storage` HP: 15 bytes/fact, recall=1.0 at 5% noise, ~280× compression vs baseline.
- `patternb_bundle_manifold` HF: intrinsic dim=731 (near full ambient). Bundle-level PCA not viable; key-only d=30 is the storage path.
- `patternb_pinv_recovery` HP: partial-query (one role-filler pair) recovers full record at acc=1.0 via pseudo-inverse. Native auto-association; no separate lookup structure needed.

## State

- cap_map v479 → v480
- commit: daf8b16
- HONEST 1174 → 1181 (+7)
- LVH 257 → 258 (+1, substrate_valueadd_curve label-vs-honest)
- Portfolio 32+82 unchanged

## Context

The key product-architecture clarification: the substrate's value is in memory-augmented QA (cycle 158: +0.352 F1 for 1.5B + substrate vs bare 1.5B), not in retrieval overlay (cycle 159: hurts recall at every encoder size). These are different integration patterns and both n=200 measurements are honest. The bare-LLM-augmented narrative is the product thesis; the RAG-overlay narrative is not.

The d=30 storage finding is significant. The cycle-157 manifold ID 32 / PCA F1=1.0 at d=30 convergence now extends to the full storage layer: 15 bytes per fact at perfect recall, ~280× smaller than baseline. If this also turns out to be the ZKL truncation path (pending MarianMT retest), the privacy and storage stories share the same architectural primitive.

The bundle-manifold HF rules out bundle-level compression — bundles need their full ambient space — but reinforces the key-only d=30 path, since keys are the indexable surface anyway.

Pattern B capabilities now cover: substitution (cycle 158), K-hop compose (cycle 158), capacity (cycle 159), partial-query pinv recovery (cycle 159), sparse predicate inversion (cycle 159). The earlier analogy HF at k=4 (cycle 158) remains the one structural gap.

Pipeline: 44 commits v438→v480. 228 anchors verdicted. 34 LVH catches.

---

END. No action requested.
