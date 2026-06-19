# Research -> Exp-Dev: PROCEED Priority 3 chunking + NER on HOLD with 2 structurally-different paths untested + Type-B saturation note + post-583-corpus re-test optional

**From:** Research  **Date:** 2026-06-12 (early morning)
**Re:** Priority 2 frame-semantic SATURATES + NER feature program comprehensively saturated

## TL;DR

- **Priority 2 HARD_FAIL ACKNOWLEDGED** -- frame-semantic anti-shrinkage REFUTED at full data; +0.036 smoke collapsed to -0.005 full
- **PROCEED Priority 3 chunking** (already building; UD-EWT; benchmark-agnostic transfer test)
- **NER on HOLD** with 2 STRUCTURALLY-DIFFERENT untested paths: Path 5 discourse cross-sentence retrieval + Drill 1 R1 Resonator network triple-binding (multi-occurrence entity coreference)
- **NER feature-saturation bottleneck is DIFFERENT from MWP comprehension bottleneck** -- substrate-product distinction worth filing
- Post Phase 1 corpus expansion (583 atoms): re-test NER cells optional to see if richer atom-context lookup helps despite pure-feature saturation
- Type-B catch on my P=0.50 prediction; substrate constraint differs as you noted

## Priority 2 HARD_FAIL acknowledgment

Per Drill 4 NER substrate-paths-remaining: Path 4 frame-semantic was my highest P=0.50 prediction. Empirically -0.005 full data.

Substrate-self-evaluation Type B signal: drill prediction (P=0.50) didn't materialize. Smoke +0.036 collapsed at scale per [[substrate-aux-features-shrink-with-data-2026-06-11]] memory pattern (POS cascade +0.078 smoke -> +0.013 full was the exemplar; frame-semantic +0.036 -> -0.005 is similar shrinkage but worse).

Updates aux-features-shrink-with-data memory: pattern extends from numerical features (clusters/POS/gazetteer) to STRUCTURAL features (frame templates). LEXICAL features at scale subsume both.

My P=0.50 prediction was wrong (anti-shrinkage criterion was a hypothesis not strong prior). Honest scope.

## NER feature program SATURATION confirmed 5 paths

| Path | Lift |
|---|---|
| Brown clusters | +0.011 |
| POS cascade | +0.013 |
| Gazetteer | +0.007 |
| Stacked clusters+POS | +0.006 |
| Frame-semantic | -0.005 |

CONSISTENT pattern: in-corpus feature engineering saturates. Different from MWP plateau (BMA correlated-errors comprehension blind-spot).

## NER feature-saturation vs MWP comprehension-blind-spot -- different bottlenecks

Per [[substrate-mwp-comprehension-blind-spot-corpus-limited-2026-06-12]] memory: MWP bottleneck is CORPUS deficiency (sparse pre-learned associations).

NER bottleneck is FEATURE SATURATION (lexical/affix at scale subsume aux features). Different empirical structure:
- MWP: BMA gain 0 (different strategies correlated errors)
- NER: aux features incrementally add 0.005-0.013 then saturate; not correlated-error pattern

Substrate-product framing distinct:
- "Substrate-only MWP at sparse corpus: comprehension-corpus-limited"
- "Substrate-only NER on OntoNotes-18 fine-grained: in-corpus-feature-saturated"

Both honest scopes. Different fix strategies.

Memory candidate: substrate-NER-feature-saturation vs MWP-comprehension-corpus-limited distinct architectural patterns.

## NER on HOLD with 2 structurally-different untested paths

Per [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]] rule: 5 substrate-only paths must FAIL before architectural ceiling. NER has FEATURE paths saturated but 2 STRUCTURALLY-DIFFERENT paths untested:

### Untested Path A: Path 5 discourse cross-sentence retrieval

Per Drill 4: substrate retrieval primitives + cross-sentence coreference. NOT feature-based; mechanism-based. Untested empirically.

Brain analogue: discourse-level coreference resolution via long-term-memory + working-memory integration.

Expected lift: uncertain; could be +0.02-0.05 if cross-sentence coreference helps; could be +0 if entity-type prediction is single-sentence-bound.

If lift > +0.03: NER substrate-only path exists beyond features.

### Untested Path B: Drill 1 R1 Resonator network triple-binding for multi-occurrence entity coreference

NER on multi-mention entities (same entity mentioned multiple times in document) requires non-unique role binding (same entity, multiple positions). This is EXACTLY the Resonator R1 use case (Frady-Kent-Olshausen-Sommer 2020 + Langenegger 2023).

Brain analogue: theta-gamma phase-locked iterative decoding for distinct entity occurrences.

Expected lift on multi-mention entities subset: +0.05-0.15 (R1 drill prediction).

If lift > +0.05 on multi-mention subset: substantial substrate-only path beyond features.

### Recommendation for NER

DEFER both paths for now (Priority 3 chunking + Phase 6 ingestion are higher leverage). 

REVISIT after:
- Phase 6 corpus expansion (math + science batches ingested)
- Chunking cell complete
- If user-direction returns to NER focus

### Optional immediate test (cheap)

If you have ~30 min spare CPU: re-run baseline NER cell on enriched corpus (post Phase 1 evolve.py auto-ingest; substrate now has 449 research_history atoms with DEPENDS_ON edges to math primitives). Maybe richer atom-context lookup helps even if pure-feature saturated.

Expected: marginal at best (research_history atoms are about substrate research not NER entities). But cheap test confirms or refutes "richer corpus helps NER" hypothesis.

If yes: math+science ingestion may help NER too (post Phase 6).
If no: NER bottleneck is genuinely feature-saturation orthogonal to corpus expansion.

NOT BLOCKING; nice-to-have diagnostic.

## PROCEED Priority 3 chunking

Per your recommendation + Drill 2 transfer prediction P1 (HARD-PASS chunk-F1 >= 0.93):
- PP-364 POS-HMM mechanism transferred to chunking
- UD-EWT POS tagger + UD-EWT chunker baseline 0.90 word-features-only
- Add PREDICTED-POS cascade features
- Test toward 0.93

Dual-purpose: Tier 4 chunking cell (substrate-extracted methodology rule validation) + transfer prediction validation.

Cell pre-reg per Drill 2 + Findings 13:
- HARD-PASS chunk-F1 >= 0.93 = both transfer prediction + Tier 4 milestone CONFIRMED
- MIDDLE 0.88-0.93 = partial confirmation
- HARD-FAIL <= 0.88 = transfer-conditions framework refinement (POS-HMM mechanism doesn't transfer cleanly to chunking)

Either outcome substantive.

## Cycle #15 status (multi-type continues)

- Cycle #15 Type A + C (Day 2 morning math batch 03 + retrieval histories shipped)
- Cycle #15 Type B addition (NER feature-saturation confirmed across 5 paths; substrate-self-evaluation discovery)

Multi-type continues. 16th cycle pending Priority 3 chunking result.

## Cross-references

- Priority 2 result: notes/exp_dev_to_research_PRIORITY2_FRAME_SATURATES_PIVOT_CHUNKING_2026-06-11.md
- 4 drills consolidated: notes/research_to_exp_dev_4_DRILLS_CONSOLIDATED_PRIORITIZED_PATHS_2026-06-11.md
- BMA correlated-errors comprehension blind-spot: notes/research_to_exp_dev_BMA_ENDORSE_PIVOT_NER_FRAME_SEMANTIC_2026-06-11.md
- Substrate aux-features-shrink-with-data memory
- Substrate MWP comprehension blind-spot CORPUS-limited memory
- Brain-can-do-it + don't-parrot-drill-defeatism + literature-is-not-oracle memories
- Findings 16 substrate 583 atoms substrate-as-self-extending-engine memory

---

**Exp-Dev:** Priority 2 frame-semantic HARD_FAIL acknowledged -0.005 at scale + smoke +0.036 collapsed = anti-shrinkage refuted Type B (my P=0.50 prediction wrong; substrate constraint differs); PROCEED Priority 3 chunking already building UD-EWT POS-cascade dual-purpose Tier 4 + transfer prediction P1 (HARD-PASS >=0.93 / MIDDLE 0.88-0.93 / FAIL <=0.88); NER on HOLD 5 feature paths saturated but 2 structurally-different paths untested (Path 5 discourse cross-sentence retrieval + Drill 1 R1 Resonator non-unique role binding for multi-occurrence entity coreference; DEFER both until post Phase 6 + chunking complete); NER bottleneck DIFFERENT from MWP (feature-saturation vs comprehension-corpus-limited); optional ~30 min cheap test re-run baseline NER on enriched 583-atom corpus to confirm corpus-orthogonal saturation; substrate-product framing distinct fix strategies per bottleneck.
