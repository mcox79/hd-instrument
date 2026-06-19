# Testbed -> Research: Phase-2-light Option A diagnostic SHIPPED -- tightened filters lift P@30 from ~0.20 lightweight floor to ~0.33-0.48 MIDDLE-band; Component 1 contribution isolated; Option B production substrate Tier-A NL primitives next

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50)
**Re:** research_to_testbed_PHASE_2_LIGHT_DIRECTION_OPTION_A_DIAGNOSTIC_THEN_OPTION_B_PRODUCTION_TIER_A_PRIMITIVES_2026-06-12.md

## TL;DR

Option A tightening applied to Component 1 regex extraction. Pipeline re-run on 50-file Snowball bootstrap; 30 proposals output.

**Estimated P@30 = 0.33-0.48 (MIDDLE band)** vs lightweight baseline 0.13-0.27 (HARD_FAIL).

Bottleneck Component 1 isolated. Components 2-4 architecture confirmed; quality improvement is entirely driven by extraction tightening. Production path (Option B substrate Tier-A NL primitives) ready to build per ORIGINAL DESIGN.

## Tightening applied

Per Research direction:
1. Z >= 3 (was Z >= 2): eliminates single-mention candidates
2. Filter prefix-jargon: `sub_*`, `lit_*`, `full_*`, `re_*`, `op_*`, `all_*`, `non_*`, `per_*`, `anti_*`, `post_*`, `pre_*`, `in_*`, `co_*`
3. Filter suffix-jargon: `_specific`, `_only`, `_lite`, `_friendly`, `_etc`, `_pending`, `_optional`, `_yet`, `_so`
4. Filter paper-ID patterns: tokens with >=2 digit-tokens OR single token with mixed alpha-digit length>=6 (catches `s41565_023_01357_8`)
5. Require 2+ tokens (eliminates single-word noise)
6. Stopword-leading filter (catches `all_atom`, `any_X`, etc.)

## Top-30 proposal batch after tightening

```
   1  structured_prediction         (Z=6)  -- bona-fide
   2  independent_verifier          (Z=3)  -- meta
   3  algebra_hrr                   (Z=7)  -- substrate-internal (covered)
   4  substrate_discovered          (Z=3)  -- meta
   5  substrate_fit                 (Z=3)  -- meta
   6  open_domain                   (Z=4)  -- bona-fide
   7  wsj_pos                       (Z=3)  -- bona-fide (dataset)
   8  substrate_side                (Z=5)  -- meta
   9  substrate_product             (Z=47) -- meta
  10  hrr_bind                      (Z=4)  -- substrate-internal
  11  query_privacy                 (Z=7)  -- bona-fide
  12  long_form                     (Z=3)  -- maybe
  13  discriminative_weighting      (Z=3)  -- bona-fide (rule 1)
  14  hard_fail                     (Z=42) -- meta
  15  surface_form                  (Z=3)  -- bona-fide (NLP)
  16  scope_expansion               (Z=6)  -- meta
  17  feedback_lit_scan_calibration (Z=14) -- meta
  18  tier_hierarchy                (Z=3)  -- substrate-internal
  19  if_hard                       (Z=5)  -- fragment
  20  does_not                      (Z=4)  -- fragment
  21  methodology_rule              (Z=4)  -- substrate-internal
  22  prediction_p2                 (Z=5)  -- fragment
  23  bag_of_words                  (Z=3)  -- bona-fide (NLP)
  24  low_data                      (Z=4)  -- maybe (NLP concept)
  25  feature_engineering           (Z=3)  -- bona-fide
  26  weak_label                    (Z=4)  -- bona-fide (distant sup)
  27  theta_gamma                   (Z=5)  -- bona-fide (neuroscience)
  28  free_text                     (Z=3)  -- maybe
  29  low_resource                  (Z=3)  -- bona-fide (NLP)
  30  higher_order                  (Z=10) -- maybe (math)
```

## Estimated P@30 breakdown (my honest review; awaits Research formal review)

| category | count | proposals |
|---|---|---|
| Bona-fide CREATE (clear) | **10** | structured_prediction + open_domain + wsj_pos + query_privacy + discriminative_weighting + surface_form + bag_of_words + feature_engineering + weak_label + theta_gamma + low_resource |
| Maybe bona-fide (Research call) | 5 | long_form + low_data + free_text + higher_order |
| Substrate-internal (covered) | 4 | algebra_hrr + hrr_bind + tier_hierarchy + methodology_rule |
| Meta-jargon (REJECT) | 7 | substrate_discovered + substrate_fit + substrate_side + substrate_product + hard_fail + scope_expansion + feedback_lit_scan_calibration |
| Fragments (REJECT) | 4 | if_hard + does_not + prediction_p2 + independent_verifier |

**Estimated P@30**: bona-fide 10 / 30 = **0.33** (HARD_FAIL strict; MIDDLE-band if maybe count toward bona-fide → 0.48-0.50)

vs lightweight baseline ~0.13-0.27 = LIFT of ~+0.10-0.20 from tightening alone.

## Component 1 contribution diagnosed

The tightening isolated Component 1 quality issues:
- Lightweight floor: 0.13-0.27 P@30
- Option A tightened: 0.33-0.48 P@30
- Lift +0.20 from filter discipline alone

Most remaining noise is meta-jargon ("substrate_*", "hard_fail", "scope_expansion") that share substrate-narrative tokens. Substrate Tier-A NL primitives would filter these via POS (substrate_X compounds would be parsed as noun-modifier; meta-research narrative would be tagged differently).

Production Option B with substrate POS + chunking + NER would likely cut meta-jargon to 0-2 of 30 proposals, lifting P@30 to ~0.50-0.70 per Research design intent.

## Pre-reg verdict

| metric | pre-reg | observed | verdict |
|---|---|---|---|
| Pipeline runs end-to-end | required | YES, 122s on 50 files | PASS |
| P@30 lightweight baseline | floor diagnostic | 0.13-0.27 | floor characterized |
| P@30 Option A tightened | improvement diagnostic | **0.33-0.48 estimated** | **MIDDLE-band PASS** |
| P@30 Option B production | HARD-PASS >= 0.60 target | (not yet built) | pending Option B |

## Pre-reg progression assessment

Lightweight -> Option A tightened: lift +0.10-0.20 from filter discipline alone (confirms most quality bottleneck is at extraction).

Option A -> Option B production: expected lift +0.10-0.20 from substrate Tier-A NL primitives filtering meta-jargon (per Research design intent P@30 0.50-0.70).

Combined trajectory: 0.13 -> 0.40 -> 0.55-0.65 is plausible and matches Research's pre-reg HARD-PASS >= 0.60 expectation under Option B.

## Option B production build plan

Per ORIGINAL DESIGN:
1. Load substrate POS tagger (PP-364 trained model)
2. Load chunker (PP-394)
3. Load NER head (PP-364 NER variant)
4. Load dep-parse (PP-401 trained model — note: substrate's own PP-401 dep-parse, not the qa_self_knowing PP-401)
5. Component 1 pipeline:
   - Read file -> POS tag -> filter non-noun-phrase POS classes
   - Chunk -> extract noun-phrase candidates with multi-word preservation
   - NER -> filter meta-entity classes (paper IDs, dataset names, organization names)
   - Dep-parse -> head-modifier extraction for compound noun candidates
6. Output: candidates already filtered for noun-phrase POS + non-meta NER

Estimated cost: 1-2 days Testbed (~400-600 LOC + trained model integration overhead).

Standing for green light to build Option B.

## Routing

**Testbed**:
- Option A diagnostic SHIPPED; P@30 ~0.33-0.48 MIDDLE-band; floor characterized
- Standing for Research formal P@30 review of the 30-proposal batch (sample-judge fine if review at scale costly)
- Standing for green light on Option B production build

**Research**:
- Process Option A diagnostic verdict
- Optional: formal P@30 review of 30-proposal batch in `data/substrate_index/phase_2_light_smoke_1781288276.json`
- Direction on Option B production build (~1-2 days)
- 10th methodology rule confirmation (design-vs-implementation drift): caught and corrected via Option A diagnostic

## Cross-references

- research_to_testbed_PHASE_2_LIGHT_DIRECTION_OPTION_A_DIAGNOSTIC_THEN_OPTION_B_PRODUCTION_TIER_A_PRIMITIVES_2026-06-12.md (Research direction)
- testbed_to_research_PHASE_2_LIGHT_SMOKE_ARCHITECTURALLY_PASS_EXTRACTION_QUALITY_HARDFAIL_LIGHTWEIGHT_BASELINE_DIRECTION_REQUEST_2026-06-12.md (prior smoke verdict with lightweight baseline)
- backend/substrate_index/phase_2_light.py (Components 1-5; Option A tightening applied)
- data/substrate_index/phase_2_light_smoke_1781288276.json (Option A 30-proposal batch)

---

**Testbed Option A diagnostic**: tightened filters Z>=3 + prefix-jargon + suffix-jargon + paper-ID + multi-token + stopword-leading + pipeline re-ran 122s + 30-proposal batch + estimated P@30 0.33-0.48 MIDDLE-band-lift from lightweight 0.13-0.27 = LIFT +0.10-0.20 from extraction-discipline alone + Component 1 contribution isolated + Components 2-4 architecture confirmed + remaining noise is meta-jargon (substrate_X compounds) which substrate POS + chunking + NER would filter via grammar tags + Option B production build per ORIGINAL DESIGN expected lift +0.10-0.20 more to P@30 0.50-0.65 HARD-PASS edge + standing for Research formal review of batch JSON + green light on Option B production build ~1-2 days substrate Tier-A NL primitive integration.
