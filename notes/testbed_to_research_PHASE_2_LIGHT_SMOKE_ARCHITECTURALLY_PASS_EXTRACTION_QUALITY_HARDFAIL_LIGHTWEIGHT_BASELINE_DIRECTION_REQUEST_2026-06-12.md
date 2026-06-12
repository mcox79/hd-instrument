# Testbed -> Research: Phase-2-light smoke ARCHITECTURALLY PASSES end-to-end + HARD_FAIL on P@30 with LIGHTWEIGHT extraction baseline; direction request on Component 1 upgrade path

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50)
**Re:** Research Phase-2-light tool DESIGN + smoke test pre-reg

## TL;DR

Phase-2-light pipeline BUILT (5 components) + smoke test RAN end-to-end on 50 most-recent research_drill_*.md files.

- **Pipeline architectural verdict**: PASS — extracts candidates, distant-supervision filters, cluster-density routes, sparse-neighborhood ranks; produces ranked proposal batch JSON in 137s
- **P@30 quality verdict**: estimated HARD_FAIL with lightweight Component 1 baseline (rough estimate 4-8 bona-fide of 30; P@30 ~0.13-0.27 vs pre-reg HARD-PASS >=0.60)
- **Bottleneck**: Component 1 lightweight extraction (regex + Title-Case heuristics) produces too many low-quality candidates; needs substrate Tier-A NL primitive upgrade per Phase-2-light design

The pipeline architecture is sound; the quality gap is Component 1.

## Smoke test output sample (top-10 of 30 by rank score)

```
  # route        cluster density novelty    z  score  canonical_name
   1 CREATE            16       1    0.99    3  0.990  full_asdiv          [fragment from "ASDiv" benchmark]
   2 CREATE            14       1    0.99    2  0.988  feature_headroom    [meta-jargon]
   3 CREATE            14       1    0.99    6  0.987  structured_prediction [legitimate; likely SCHOOL atom exists]
   4 CREATE            16       1    0.99    2  0.986  reed_solomon        [legitimate; new atom candidate]
   5 CREATE            14       1    0.99    3  0.985  independent_verifier [meta-jargon]
   6 CREATE            14       1    0.98    7  0.982  algebra_hrr         [substrate-internal concept; covered]
   7 CREATE            15       2    0.98    4  0.980  project_specific    [meta-jargon]
   8 CREATE            16       1    0.98    9  0.980  lit_precedent       [meta-jargon]
   9 CREATE            14       1    0.98    2  0.979  sub_millisecond     [meta-jargon]
  10 CREATE            14       1    0.98    2  0.979  registered_negative_outcomes [meta-content]
```

## Component 1 extraction-quality issues

Lightweight regex extraction misclassifies:
- snake_case fragments (`full_asdiv` matched as candidate; ASDiv is the actual concept)
- meta-research jargon prefixes (`sub_X`, `lit_X`, `full_X` as candidates)
- Multi-word patterns matching narrative content (e.g., `registered_negative_outcomes`)
- Paper DOI strings (`s41565_023_01357_8` — Nature article ID)

These are NOT atom candidates — they're meta-noise from the research drill file content.

Substrate Tier-A NL primitives (POS tagging + dep-parse + NER per Phase-2-light design) would filter most of this automatically:
- POS tag candidates as noun-phrase only (filters verbs / adjectives)
- NER filters meta-entity classes (paper IDs, dataset names like "SST-2")
- Dep-parse head-modifier extraction surfaces TRUE compound nouns

## Component 2-4 working correctly

- Distant supervision: exact-matches filtered (skip_existing=True); near-matches surface in similarity_to_existing_T3 with token-overlap score (working; some candidates like "algebra_hrr" still passed through because no exact match for canonical_form)
- Cluster-density routing (Component 3 via cluster_density.py helper): correctly identifies cluster_id + density; all candidates routed CREATE due to low cluster similarity
- Sparse-neighborhood ranking (Component 4 via sparse_neighborhood_ranking.py): sorts by composite score (0.7 * novelty + 0.3 * inverse-density)

## Pre-reg verdict

| metric | pre-reg | observed | verdict |
|---|---|---|---|
| pipeline runs end-to-end | required | YES, 137s on 50 files | ARCHITECTURE PASS |
| P@30 >= 0.60 (HARD-PASS) | bona-fide atom candidates | est. 4-8 / 30 = 0.13-0.27 | **likely HARD-FAIL** |
| P@30 0.40-0.60 (MIDDLE) | -- | 0.13-0.27 estimated | below MIDDLE |
| P@30 < 0.40 (HARD-FAIL) | -- | 0.13-0.27 estimated | **HARD-FAIL** range |

Honest estimate. Research review of the 30 proposals would give the exact P@30.

## Three direction options for upgrade

### Option A: Tighten extraction patterns (cheap iteration; ~30 min Testbed)

Pattern refinements:
- Require Z >= 3 (eliminate single-mention candidates; already filter Z<2; tighten to Z>=3)
- Filter prefix-jargon: `sub_*`, `lit_*`, `full_*`, `re_*`, `op_*` as candidate-prefixes
- Filter pure-uppercase-with-digits (paper IDs, dataset version numbers)
- Require 2+ tokens for multi-word candidates (eliminate `feature`, `domain` single-word over-matches)

Expected post-tighten P@30: ~0.25-0.40 (MIDDLE-low edge; still below HARD-PASS).

### Option B: Wire substrate Tier-A NL primitives (~1-2 days Testbed)

Per Phase-2-light design:
- POS tagger via substrate PP-364 (trained model load + inference)
- Chunking via substrate PP-394
- NER via substrate PP-364 NER head
- Dep-parse via substrate

Heavier lift (need to load trained substrate models). Expected post-upgrade P@30: ~0.50-0.70 (MIDDLE-HARD-PASS edge per Research design intent).

### Option C: Hybrid LIGHT + targeted (compromise; ~half day Testbed)

- Keep lightweight extraction
- Add curated filter list (manually-identified noise patterns)
- Add POS-tagger-LITE (small spaCy model if PROT-001 / no-LLM compliance allows it OR a tiny rule-based POS approximator)

Expected post-hybrid P@30: ~0.35-0.55 (MIDDLE band).

## My recommendation

**Option A FIRST** (cheap; close the loop and get an honest P@30 from Research review of refined batch); IF still HARD-FAIL, **Option B** is the production path per Phase-2-light design.

## Standing for Research direction

Pipeline architecture works. Extraction-quality bottleneck identified. Three options laid out. Smoke test JSON saved to `data/substrate_index/phase_2_light_smoke_1781287501.json` for review.

## Cross-references

- research_to_testbed_PHASE_2_LIGHT_TOOL_DESIGN_5_COMPONENT_LLM_FREE_PIPELINE_SNOWBALL_BOOTSTRAP_SMOKE_TEST_PREREG_2026-06-12.md (Research design)
- backend/substrate_index/phase_2_light.py (Components 1-5 implementation)
- backend/substrate_index/cluster_density.py + sparse_neighborhood_ranking.py (helpers)
- tools/substrate_phase_2_light_smoke.py (smoke runner)
- data/substrate_index/phase_2_light_smoke_1781287501.json (top-30 proposal batch output)
- Commit: pending

## Routing

**Testbed**:
- Smoke architecturally PASS + P@30 likely HARD_FAIL filed
- Standing for Research direction (Option A / B / C)
- Can ship Option A in ~30 min upon green light

**Research**:
- Process honest P@30 review of the 30-proposal batch (or sample-judge to estimate)
- Direction on Option A vs B vs C upgrade path
- Phase-2-light tool BUILD state: architecture complete; extraction quality iteration pending

---

**Testbed Phase-2-light smoke**: pipeline architecturally PASSES end-to-end 50 files 137s 30-proposal batch ranked + Z-counts + cluster-density + sparse-neighborhood-first + JSON output + P@30 likely HARD_FAIL with lightweight Component 1 baseline (estimated 4-8 bona-fide of 30 = 0.13-0.27 vs HP>=0.60) + bottleneck Component 1 regex+TitleCase extraction produces meta-jargon fragments (sub_millisecond + lit_precedent + s41565_023_01357_8 paper DOIs + project_specific) + 3 direction options A tighten patterns ~30min B substrate Tier-A NL primitives ~1-2 days C hybrid compromise + my recommend Option A first then Option B if needed + Components 2-4 working correctly (distant supervision + cluster routing + ranking) + standing for Research direction.
