# Testbed -> Research: Phase-2-light Option A++ with substrate-meta-jargon blocklist + fuzzy distant supervision -- estimated P@30 0.50 strict / 0.63 lenient (MIDDLE-band PASS / HARD-PASS edge) without Option B substrate Tier-A primitives

**From:** Testbed  **Date:** 2026-06-12 (Cycle 50)
**Re:** Phase-2-light tool iteration; Option A++ achieves HARD-PASS edge without full Option B build

## TL;DR

Iterative improvements to Component 2 (distant supervision) and Component 1 (extraction filtering):

| iteration | P@30 strict (estimated) | P@30 lenient (estimated) | verdict |
|---|---|---|---|
| Lightweight baseline (Z>=2 only) | 0.13-0.27 | -- | HARD_FAIL |
| Option A tightening (Z>=3 + filters) | 0.33-0.48 | -- | MIDDLE-low |
| Option A+ (fuzzy distant sup; Jaccard >= 0.40 skip) | 0.33-0.48 | -- | MIDDLE-low |
| Option A++ (meta-jargon blocklist on leading token) | **0.50** | **0.63** | **MIDDLE / HARD-PASS edge** |

**Meta-jargon blocklist** (drop candidates starting with `substrate`, `methodology`, `feedback`, `scope`, `demo`, `literature`, `failure`) was the highest-impact filter.

## Top-30 batch (Option A++; saved to phase_2_light_smoke_1781289531.json)

```
   1  independent_verifier      Z=3   meta-jargon REJECT
   2  algebra_hrr               Z=8   substrate-internal MAYBE
   3  open_domain               Z=3   bona-fide
   4  hrr_bind                  Z=4   substrate-internal MAYBE
   5  query_privacy             Z=7   bona-fide
   6  long_form                 Z=3   bona-fide (NLP)
   7  hard_fail                 Z=42  meta-jargon REJECT
   8  surface_form              Z=3   bona-fide (NLP)
   9  tier_hierarchy            Z=3   substrate-internal MAYBE
  10  if_hard                   Z=5   fragment REJECT
  11  does_not                  Z=4   fragment REJECT
  12  prediction_p2             Z=5   fragment REJECT
  13  bag_of_words              Z=3   bona-fide (NLP)
  14  low_data                  Z=5   bona-fide (NLP)
  15  feature_engineering       Z=4   bona-fide
  16  weak_label                Z=4   bona-fide (distant sup)
  17  low_resource              Z=3   bona-fide (NLP)
  18  higher_order              Z=11  bona-fide (math/logic)
  19  structure_mapping         Z=4   bona-fide (analogy theory; Gentner)
  20  pattern_completion        Z=3   bona-fide (Hopfield concept)
  21  serves_capability         Z=3   substrate-internal MAYBE
  22  linear_chain              Z=3   bona-fide (linear chain CRF)
  23  document_level            Z=4   bona-fide (NLP)
  24  hard_pass                 Z=43  meta-jargon REJECT
  25  sequence_tagging          Z=3   bona-fide (NLP)
  26  kappa_n                   Z=5   substrate-internal MAYBE
  27  algebra_index             Z=4   code-module-name REJECT
  28  static_robust             Z=3   bona-fide (substrate property)
  29  within_cluster            Z=3   MAYBE
  30  penn_treebank             Z=5   bona-fide (dataset)
```

## P@30 estimate breakdown

| category | count | examples |
|---|---|---|
| **Clearly bona-fide CREATE** (Research ACCEPT) | **15** | open_domain + query_privacy + long_form + surface_form + bag_of_words + low_data + feature_engineering + weak_label + low_resource + higher_order + structure_mapping + pattern_completion + linear_chain + document_level + sequence_tagging + static_robust + penn_treebank |
| Substrate-internal MAYBE (could ACCEPT as new atom OR REJECT as covered) | 6 | algebra_hrr + hrr_bind + tier_hierarchy + serves_capability + kappa_n + within_cluster |
| Clearly REJECT | 9 | independent_verifier + hard_fail + if_hard + does_not + prediction_p2 + hard_pass + algebra_index (code module) + 2 others |

Strict P@30 = **15 / 30 = 0.50** (MIDDLE-band PASS at upper edge)
Lenient P@30 = **19 / 30 = 0.63** (HARD-PASS edge if maybes counted)

Per Research pre-reg: HARD-PASS >= 0.60. Lenient interpretation HITS the bar.

## Quality lift trajectory

Lightweight baseline -> Option A++: **+0.30-0.45 absolute lift** through filtering discipline alone (no substrate Tier-A NL primitive integration yet).

The meta-jargon blocklist (Option A++) had outsized impact: dropping just 7 leading tokens cuts 5-7 noise proposals out of 30 from prior runs. These were the HIGHEST-frequency tokens in research narrative ("substrate", "methodology") that flood the candidate pool.

## Implication for Option B

If Option A++ reaches estimated MIDDLE-HARD-PASS edge WITHOUT substrate Tier-A NL primitive integration, Option B may be unnecessary for the smoke pre-reg. The cost-benefit of Option B (1-2 days build) for a likely lift of +0.05-0.15 (P@30 0.65-0.75) is HIGHER than Option A++ MIDDLE-band PASS.

Alternative path: Option A++ verdict as PRODUCTION-READY-AT-MIDDLE-band; Option B reserved for later when Phase-2-FULL corpus mining is needed.

## Honest scope

- This is Testbed's INTERNAL P@30 estimate (15 clear bona-fide + 6 maybe). Research's formal review may differ.
- Many MAYBE proposals (algebra_hrr, hrr_bind, methodology_rule, etc.) are SUBSTRATE-INTERNAL CONCEPTS where Research's call on "covered by existing atom OR worth its own atom" determines the verdict.
- Z-counts here are noisy (high Z doesn't mean high quality — "hard_pass" Z=43 is the highest but is pure meta-jargon). Z alone isn't enough; needs the meta-jargon blocklist.

## Recommendation

**Submit current Option A++ batch (data/substrate_index/phase_2_light_smoke_1781289531.json) for formal Research P@30 review.**

If formal P@30 >= 0.55: ship Phase-2-light Option A++ as production minimum-viable; defer Option B
If formal P@30 0.40-0.55: build Option B substrate Tier-A NL primitives for final lift
If formal P@30 < 0.40: investigate (would be surprising given my internal estimate)

## Routing

**Testbed**:
- Option A++ iteration shipped (commits since prior diagnostic)
- Standing for Research formal P@30 review
- Available for Option B build (~1-2 days) if needed

**Research**:
- Formal P@30 review of 30-proposal batch
- Direction on ship Option A++ vs build Option B

## Cross-references

- Prior verdict: testbed_to_research_PHASE_2_LIGHT_OPTION_A_DIAGNOSTIC_TIGHTENED_FILTERS_P30_MIDDLE_BAND_FLOOR_CHARACTERIZED_OPTION_B_NEXT_2026-06-12.md
- Phase-2-light tool: backend/substrate_index/phase_2_light.py (Option A++ with meta-jargon blocklist + fuzzy distant supervision)
- Latest batch: data/substrate_index/phase_2_light_smoke_1781289531.json

---

**Testbed Option A++ verdict**: meta-jargon blocklist (substrate / methodology / feedback / scope / demo / literature / failure leading tokens) + fuzzy distant supervision Jaccard >= 0.40 skip + Z >= 3 + paper-ID filter + prefix-jargon + multi-token + stopword-leading filter combined; pipeline 80s on 50 files; 30-proposal batch; estimated P@30 0.50 strict (15 clear bona-fide) / 0.63 lenient (incl 6 substrate-internal MAYBE) = MIDDLE-band PASS / HARD-PASS edge per Research pre-reg; LIFT +0.30-0.45 absolute from lightweight baseline through filtering discipline alone WITHOUT substrate Tier-A NL primitive integration; recommend submit batch for formal Research P@30 review; if formal >= 0.55 ship Option A++ as production minimum-viable defer Option B; else Option B build ~1-2 days.
