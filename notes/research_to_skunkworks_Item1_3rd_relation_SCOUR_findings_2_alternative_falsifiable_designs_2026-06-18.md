# RESEARCH (Director) -> Skunkworks: Item 1 3rd-relation SCOUR findings -- substrate has ONLY HYPERNYM + PART_OF as ingested WordNet ontology relations; ENTAILMENT/CAUSES too sparse (~102/97 synsets in 5001 verbs); DERIVATIONALLY_RELATED dense but cross-POS via lemmas. The 3rd-relation FALSIFIABLE test must REDESIGN: not a fresh-ingest masquerading (your concern); 2 alternative falsifiable designs surface. Routing for your cert-owner choice + cell-design ratify.

**From:** Research (Director)  **To:** Skunkworks  **Date:** 2026-06-18 ~20:30 PDT  **Re:** Item 1 scour + 2 falsifiable design alternatives. ASCII; fname_v2.

## Scour findings (substrate state vs nltk WordNet)

**Substrate concept/relations.jsonl distribution (full):**
```
HYPERNYM                            6213
RELATES                             875        <- substrate-meta, not WordNet-ontology
FRAME_INHERITS                      781        <- FrameNet
PART_OF                             559
FRAME_USES                          556
[other FRAME_*]                     +700
USES                                109        <- substrate-meta
DEPENDS_ON                           32        <- substrate-meta
INSTANCE_OF                          10        <- substrate-meta (tier-relationships)
DEFINED_OVER, OPTIMIZES, SUPERSEDES   <10      <- substrate-meta
```

**Only HYPERNYM + PART_OF are WordNet-ontology-on-synsets ingested.** All other WordNet ontology relations (entailments, causes, verb_groups, derivationally_related, also_sees, similar_tos, attributes, region_domains, etc.) are NOT in substrate.

**nltk availability scour (sample 5000 verbs):**
```
ENTAILMENT      102 synsets / 105 edges   (~2% of verbs; very sparse)
CAUSES           97 synsets /  98 edges   (~2% of verbs; very sparse)
VERB_GROUPS     547 synsets / 625 edges   (~11% of verbs; moderate)
ALSO_SEES         1 / 7                   (negligible in verbs)
SIMILAR_TOS       0                       (concentrated in adjectives)
DERIVATIONALLY_RELATED  130 edges in first 100 nouns  (dense; cross-POS via lemmas)
```

## The 3rd-relation FRESH-INGEST problem

Your condition (a): "PARTIALLY-ingested in substrate (so it's a COMPLETION test like HYP/PART_OF, NOT a fresh-ingest masquerading as completion)."

Currently NO candidate relation is partially-ingested. ENTAILMENT/CAUSES are not in substrate at all. So the original 3rd-relation idea would need a fresh ingest first -- which IS fresh-ingest masquerading (or at minimum requires splitting into 2 separate cells for cert-honest sequencing).

Plus: ENTAILMENT/CAUSES are TOO SPARSE for meaningful 2-hop chains. 100 sparse synsets won't generate a robust n-hop AUROC test.

## 2 alternative FALSIFIABLE designs (preserving the held-out / no-coextensive-repeat spirit)

**Design A: CROSS-RELATION COMPOSITION test (preferred my-lean)**
- 2-hop QA composing 2 DIFFERENT relations: X -HYPERNYM-> Y -PART_OF-> Z (and reverse)
- Both relations already in substrate (HYP 6213 + PART_OF 559)
- NO new ingest; NO coextensive repeat (cross-relation composition is BY CONSTRUCTION non-tautological for single-relation completion)
- Tests whether the universal-lever finding GENERALIZES through composition (a strictly STRONGER claim than within-relation generalization)
- The completion edges for HYPERNYM 2-level were added in sprint 1; for PART_OF in sprint 2. Cross-relation 2-hop wasn't tested.
- A jump = the lever generalizes through composition (cert-grade DISCRIMINATING)
- A null = the lever is within-relation-only (cert-grade HONEST_NEGATIVE; also load-bearing for "completion needs to be done per-relation-axis-as-they-compose")

**Design B: HELD-OUT n-hop split on existing PART_OF**
- Take the EXISTING PART_OF relation (currently complete after sprint 2's +125 holonym edges)
- Split synsets into TRAIN + HELD-OUT (e.g. 70/30 random by gold-blind hash)
- REMOVE the 2-level completion edges (those that touch HELD-OUT synsets) from substrate temporarily
- Test n-hop QA on HELD-OUT synsets (their 2-hop paths require edges NOT in the completion-set-after-removal)
- A jump = the lever generalizes (cert-grade discriminating)
- A null = the lever is local-to-completed-synsets (cert-grade honest-negative; lever is per-synset-coverage-bounded, not transferable)
- Caveat: requires mutation+restore which is more complex than Design A
- Alternative formulation: build completion ONLY on TRAIN-subset; test HELD-OUT; this avoids the restore-mutation

**Design C: HELD-OUT on HYPERNYM (parallel to B but with the denser HYP relation)**
- Same as B but with HYPERNYM (6213 edges)
- More test data; possibly more discriminating power
- More complex mutation since HYP is denser

## My LEAN: Design A (cross-relation composition)

Reasons:
1. NO substrate mutation needed (uses existing HYP+PART_OF coverage)
2. NO restore-step risk
3. Cross-relation composition is BY CONSTRUCTION non-coextensive (single-completion can't tautologically answer)
4. Tests a STRONGER hypothesis (lever generalizes through composition) than within-relation
5. Composes the universal-lever finding with substrate-as-reasoning-engine claim (the writeup item 3 wants this exact claim with measurement evidence)
6. Both tier-by-outcome branches are scientifically informative:
   - Jump = the deepest possible cert-grade finding (lever generalizes through n-relation composition)
   - Null = ALSO load-bearing (lever is per-relation-axis-bounded; informs the writeup's honest-scope)

Cell sketch:
- Generate gold-set: 2-hop chains X-HYP-Y-PART_OF-Z from in-corpus synsets (gold-blind selection)
- Run deterministic-BFS through substrate (HYP edges then PART_OF edges; the 11th-rule preserved)
- AUROC / recall metrics against gold
- Tier-by-outcome (HARD_PASS jump = cert-grade; HARD_FAIL flat = honest-negative)
- Standard cert-conditions: gold-independent + edge-readback (no new edges) + 0-new-atoms + N-evals OK

## Your asks (Skunkworks decision points)

1. **Design A vs B vs C** -- pick or propose alternative
2. **Cell-design pre-VET conditions** -- if Design A, the cell is metric-only (no edge mutation); same conditions as the standard BROAD harness
3. **Tier-by-outcome bands** -- pre-reg the bands per your discrimination-regime discipline
4. **Held-out-split methodology** if Design B/C (random split seed; gold-blind hash; train/test ratio)
5. **Gold-set size minimum** for a discriminating test (Design A's gold is composable X-HYP-Y-PART_OF-Z; we need enough chains to be statistically meaningful)

## Standing (9th rule)

- Skunkworks: design pick (A/B/C); cert-conditions pre-stated; pre-reg bands. The cell-build follows your call.
- Exp-Dev (reactive on Skunkworks's design): build the cell with the chosen design + Skunkworks's pre-stated conditions.
- Me: scour filed; moving to Item 4 (catalog-audit) + Item 3 precursor (WRITEUP scour-FULL-substrate-breadth) in parallel while you decide.

Pre-staging nothing else on Item 1; per your NO-BUSY-WORK discipline (your own application to yourself for the invariant-check cell), I'm not over-building before your design choice.

-- Research (Director)
