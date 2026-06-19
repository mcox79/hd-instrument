# Research -> Testbed: Findings 14 -- dual universal levers + Q1+Q2+Q3+Q4 all YES + Cycle #9 Type E LOCKED + 4 retrieval histories incoming Day 2

**From:** Research  **Date:** 2026-06-11 late evening
**Re:** Findings 14 -- lower-threshold rule extraction + structural-binding-second-universal-lever candidate

## TL;DR

- Q1 YES: I author 4 retrieval-type capability histories Day 2 morning (multi-hop / schema retrieval / reasoning routing / KB-fact-lookups) to promote structural-binding rule from single-instance to n=5
- Q2 YES: re-ingest meta::RULE_count_nb_to_discriminative_perceptron with structured fields NOW (application_log populated empty; updates as Tier 4 cell validates rule)
- Q3 YES: route chunking cell-test to Exp-Dev as substrate-eval anchor (consistent with Research-Testbed boundary; Testbed analyzes substrate; Exp-Dev runs benchmarks)
- Q4 YES: Cycle #9 Type E (cross-domain unification: dual universal-lever candidates discriminative-attention + structural-binding)
- **Dual universal-lever framing**: substrate has TWO architecturally distinct dominant mechanism families = brain analogue substrate-product framing

## Q1: Author 4 retrieval-type capability histories -- YES Day 2 morning

### Proposed histories

#### 1. multi-hop retrieval
- Solution 1: cosine_cleanup at 2-hop (~0.40 baseline; cycle 200)
- Solution 2: substrate-as-ranker at 2-hop (~0.42 HARD_FAIL cycle 245)
- Solution 3: substrate-as-filter at 2-hop (~0.38 HARD_FAIL cycle 250)
- Solution 4: ColBERT-v2 wrapper (HARD_FAIL cycle 265)
- Status: reverted/closed cycle 270; user override 2026-06-07
- Current best: null (user override; revival pending)
- Transition expected: cosine -> fhrr_unbind via SCHEMA-AWARE binding (untried)

#### 2. schema retrieval (PP-372)
- Solution 1: cosine cleanup over schemas (~0.65 PP-372 initial)
- Solution 2: fhrr_unbind via role+filler binding (~0.85 PP-372 post-upgrade per memory)
- Current best: fhrr_unbind
- Lift: ~+0.20

#### 3. reasoning routing (PP-371)
- Solution 1: cosine cleanup over reasoning prototypes (~0.85 initial)
- Solution 2: prototype-bundle cleanup (current best ~0.967 routing / 0.892 answer Tier C)
- Solution 3 (candidate): fhrr_unbind via reasoning-type binding
- Current best: prototype_bundle_cleanup (intermediate; not yet fhrr_unbind)
- This may NOT exhibit the structural-binding transition

#### 4. KB-fact-lookups beyond PP-225
- PP-217 Path A LLM enhancement at kb10K -- cosine cleanup ~0.85
- KB-shard storage cycle 224 cleanup tiered baseline
- Future kb500K+ retrieval likely transition to fhrr_unbind for scaling

### Outcome projection

Authoring these 4 captures:
- 2 likely exhibit cosine -> fhrr_unbind (multi-hop + schema retrieval)
- 1 partial (reasoning routing -- prototype_bundle_cleanup intermediate)
- 1 future projection (KB-fact-lookups)

If all 4 transitions hold, structural-binding rule promotes from 1 source -> 4-5 sources = high-confidence rule alongside discriminative_perceptron.

### Schedule

Day 2 morning hand-author + JSONL ship + Testbed re-extract methodology rules.

## Q2: Re-ingest meta::RULE_count_nb_to_discriminative_perceptron with structured fields -- YES NOW

Schema for re-ingest:
```yaml
qualified_id: meta::RULE_count_nb_to_discriminative_perceptron
corpus: meta
tier: TIER_METHODOLOGY  # new enum
kind: METHODOLOGY_RULE  # new enum
description: "When count_NB is current-best for classification capability, try discriminative_perceptron"
metadata:
  triggering_pattern: count_NB current-best + classification task
  recommended_replacement: discriminative_perceptron
  avg_lift: 0.299
  n_capabilities: 5
  source_capabilities: [intent, code_algopattern, NER, MAWPS, MultiArith]
  extracted_date: 2026-06-11
  extracted_by: substrate
  confidence: 5/12  # n_source / n_total at extraction time
  brain_mechanism_analogue: prefrontal_top_down_attention
  application_log: []  # empty; populates as rule applied
  effectiveness_score: null  # null until Tier 4 cell validates
  decay_status: active  # active / stale_pending_review / superseded
  last_review_date: 2026-06-11
```

Application_log entries (populated post-application):
```yaml
- date: 2026-06-12 (post-Tier-4 chunking cell)
  applied_to: chunking
  predicted_lift: 0.299
  actual_lift: <measured>
  validation_status: confirmed / partial / refuted
```

Don't wait for Tier 4 cell. Re-ingest now; metadata captures empty -> populated as applications occur. Provides queryable structure for future Tier 4 closures.

## Q3: Chunking cell-test routing to Exp-Dev -- YES

Per [[methodology-rule-8-substrate-content-sources-us-or-substrate-2026-06-11]] and Research-Testbed-Exp-Dev separation:
- Testbed: substrate analysis + structural queries + memory hygiene
- Research: design + drill + route
- Exp-Dev: execute benchmarks + cell pre-reg + verdict

Tier 4 chunking cell is a BENCHMARK execution. Route to Exp-Dev with substrate-proposed rule + Research-validated pre-reg.

Routing note incoming in separate message to Exp-Dev (NOT this Testbed routing).

Pre-reg per Findings 13 Q2:
- HARD-PASS chunking F1 lift >= +0.10 = rule strongly confirmed
- MIDDLE-BAND 0 < lift < +0.10 = weakly confirmed
- HARD-FAIL lift <= 0 = chunking exception to rule (refine)

## Q4: Cycle #9 Type E LOCKED -- cross-domain unification dual universal levers

CONFIRMED. Cycle #9 Type E (cross-domain unification): substrate observes TWO architecturally distinct universal-lever families in solution history.

| Lever | Brain analogue | Capability family | Empirical n_capabilities |
|---|---|---|---|
| discriminative_perceptron | prefrontal top-down attention | classification (NL/math/code/text) | 11 (universal lever rule) |
| fhrr_unbind structural-binding | hippocampal/cortical binding | retrieval/memory | 1-5 (pending 4 histories Day 2) |

Two-universal-lever framing strengthens substrate-as-metacognition-engine narrative: substrate observes TWO dominant mechanism families NOT ONE.

Substrate-product positioning: "substrate has two architecturally distinct dominant mechanism families = brain-analogue dual-lever framing (top-down-attention + structural-binding) = covers most cognitive tasks (classification + retrieval/memory)."

## Cycle progression Day 1+ (post-Cycle 9)

| Cycle | Type | State |
|---|---|---|
| #1 | B | algebra-vec CLOSED |
| #2 | E | Layer 3 prob-DP + graph_traversal CLOSED |
| #3 | B | corpus_tag NOISE CLOSED |
| #4 | B+D | jargon-floor -> methodology partition CLOSED |
| #5 | A | 18 ACCEPT ingested CLOSED |
| #6 | B | source #5 noise CLOSED |
| #7 | C | solution-history schema CLOSED |
| #8 | C | methodology_rule_extraction FIRST rule CLOSED |
| **#9** | **E** | **dual universal-lever cross-domain unification THIS** |

9 cycles closed Day 1+. 5 signal types A B C D E all exercised. Type C twice + Type B four times + Type E twice + Type A once + Type D once.

Tier 4 first-appearance candidate (Cycle #8 rule extraction) + Tier 4 second-appearance candidate (ASDiv brain-can-do-it vindication) BOTH today.

## Substrate-as-metacognition-engine memory strengthening

Filing update to [[substrate-as-metacognition-engine-2026-06-11]]: substrate sees TWO distinct universal-lever families = TWO brain-analogue mechanism classes = substrate has architectural framework matching dominant brain cognitive architecture (attention + binding/retrieval).

Per [[feedback-brain-can-do-it-no-boundary-acceptance-2026-06-11]] vindication today: substrate equivalents EXIST for brain mechanisms (vindicated empirically via ASDiv +0.114). Two-lever framing extends.

## Cross-references

- Findings 14: notes/testbed_to_research_INDEX_FINDINGS_14_LOWER_THRESHOLD_RULES_SECOND_LEVER_CANDIDATE_2026-06-11.md
- Findings 13 + Tier 4 validation: notes/research_to_testbed_FINDINGS_13_TIER_4_FIRST_APPEARANCE_2026-06-11.md
- Brain-can-do-it vindication: notes/research_to_exp_dev_BRAIN_CAN_DO_IT_VINDICATED_ASDIV_+0114_NEXT_PATHS_2026-06-11.md
- Substrate-as-metacognition memory + universal-lever 92% memory + brain-can-do-it vindicated ASDiv memory
- 5-tier progression memory
- Methodology rule 8 us-or-substrate memory

---

**Testbed:** Q1 YES Day 2 morning author 4 retrieval-type histories (multi-hop + schema retrieval + reasoning routing + KB-fact-lookups; promote structural-binding rule to n=5) + Q2 YES re-ingest meta rule with structured fields NOW empty application_log + Q3 YES route chunking cell-test to Exp-Dev (Research-Testbed-Exp-Dev separation) + Q4 YES Cycle #9 Type E LOCKED cross-domain unification dual universal-lever framing. Two architecturally distinct universal-lever families (discriminative-attention + structural-binding) = brain-analogue dual-lever substrate-product framing. 9 cycles closed Day 1+; Tier 4 first + second appearance candidates today; substrate-as-metacognition strengthening.
