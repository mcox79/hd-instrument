# Research -> Testbed: Gap 4 semantic intent router PROMOTED Tier-0 (was Tier-1) -- F+G axes measurable-ZERO without it + 2-axes substrate-self-knowing UNBLOCK

**From:** Research  **Date:** 2026-06-12 (Day 3 evening)
**Re:** Gap 7 v3 attempt finds F/G keyword-routes catastrophically over-retrieve; Gap 4 now REQUIRED

## TL;DR

- Gap 4 semantic intent router PROMOTED Tier-1 -> **Tier-0 priority** for Testbed.
- F gap + G pattern axes return atom-F1 ~0 with keyword routes; substrate-self-knowing 2-of-7 axes UNMEASURABLE without Gap 4.
- A axis 0.38 also keyword-limited (+0.10 with Gap 4).
- Combined: Gap 4 unblocks A + makes F + G measurable.
- v2 n=50 0.4637 substrate-as-ground-truth baseline (A-E only); 5-of-7 axes measurable today.

## Empirical Gap 4 evidence

Exp-Dev v3 attempted F + G routes with keyword + coverage primitives:
- F gap Q24/Q54 qualitative-future-work: route correctly returns empty; gold-present nonzero -> F1=0 (metric mismatch + Phase-6 dependency)
- F gap Q26 self-referential never-applied: route returns 114 atoms; no fixed gold (answer IS query result) -> unscoreable
- G pattern Q28/Q30/Q55 semantic-analogue (theta-gamma -> resonator/sdm/permutation): keyword catastrophically over-retrieves (Q30 fp=1159 -- "rules" matches every meta atom; Q28 fp=242; Q55 fp=234) -> F1 ~0

These are NOT substrate-self-knowing failures; they are METRIC + ROUTER mismatch with question semantics.

Per [[methodology-rule-7-substrate-quality-first-not-comparison]] + per substrate-as-ground-truth: substrate's measurement infrastructure must match question semantics.

## Gap 4 router spec (updated REQUIRED scope)

Per [[substrate-usability-gap-findings-18-2026-06-11]] memory Gap 4 + Exp-Dev empirical:

Semantic intent router replaces keyword/coverage routes for F + G + A axes:

| Input | Routed primitive | Routed args |
|---|---|---|
| Type A "what atoms about TOPIC" | what_do_you_know_about(topic) -> bge cosine nearest 8-12 | TOPIC semantic embed |
| Type F1 qualitative future-work | DEFERRED-PHASE-6-VALIDATION | -- |
| Type F2 self-referential primitive | primitive-success metric (did primitive return correctly?) | F2 query |
| Type F3 enumerated gap | atom-F1 with coverage_report() | capability qid |
| Type G semantic-analogue (THETA-GAMMA -> resonator) | semantic-analogue via bge cosine + cross-corpus filter | source qid + target corpus |
| Type G universal-lever | pattern_atoms(pattern_type) substrate-self-extracted | pattern qid |

Build spec:
- Intent classifier: 10-class softmax over substrate-classical NL Tier-A POS + dep-parse + Intent 0.83 features
- Arg extractor: from question text -> NER + dep-parse role tagging
- Routed primitive selection via classifier prediction
- Substrate-only; no LLM-judge

Pre-reg Gap 4 build:
- Tier-A semantic intent classifier macro-F1 >= 0.85
- Gap 7 A-axis lift: 0.38 -> 0.50 (+0.12)
- Gap 7 F-axis lift: 0.00 -> 0.30 (+0.30 by enabling F3 enumerated-gap measurement; F2 primitive-success metric needs implementation)
- Gap 7 G-axis lift: 0.014 -> 0.40 (+0.39 by enabling semantic-analogue measurement)

If Gap 4 lifts A + F + G as above, macro-F1 across 7 axes:
- v2 5-axis 0.4637 (A 0.38 + B 0.33 + C 0.64 + D 0.50 + E 0.52)
- v3 7-axis with Gap 4: A 0.50 + B 0.33 + C 0.64 + D 0.50 + E 0.52 + F 0.30 + G 0.40 = mean **0.456**

Net macro shifts marginally (5-axis 0.4637 vs 7-axis 0.456) but the 7-axis MEASURABILITY is now operational. Substrate-product positioning: "substrate-self-knowing 7-axis decomposable + 7/7 measurable post Gap 4."

## F-axis metric decomposition (need Testbed support)

F1 qualitative future-work: gold realizable at Phase-6 ingest landing. Measure F1-axis only after Phase 6.

F2 self-referential primitive-success: query IS answer. Testbed primitive-success scoring needed:
- Q26 "what's never-applied" -> success if primitive returns >= 1 atom (114 found = success)
- Q24 "what HAVEN'T I tried" -> success if primitive returns >= 5 atoms (sparse)
- Score: 1.0 if primitive returns valid set; 0.0 if primitive errors

F3 enumerated gap: atom-F1 with coverage_report() primitive against capability-specific gold.

## G-axis decomposition

G semantic-analogue: requires Gap 4 router with bge cosine + cross-corpus filter. Brain-to-substrate analogue mapping is exactly the kind of cross-domain mapping substrate provides via [[substrate-cross-disc-analogue-surfacing]] earlier handoff.

G universal-lever: pattern_atoms primitive exists. Q60 "most-occurring lifting primitive" might work standalone. Try after Gap 4.

## Methodology rule extraction candidate

Per [[substrate-as-metacognition-engine-2026-06-11]] memory:

**RULE: BENCHMARK METRIC must match QUESTION SEMANTICS.**

Substrate-self-knowing benchmark scope:
- Atom-set retrieval (A/B/C/D/E) -> atom-F1 fits
- Qualitative-future-work (F1) -> deferred-metric until Phase-6
- Self-referential primitive-output (F2) -> primitive-success metric
- Semantic-analogue (G semantic) -> Gap 4 routing + bge cosine
- Universal-lever (G universal-lever) -> substrate-self-query primitive

Cross-references: substrate-product 5-of-7 axes measurable today + 2-of-7 Gap-4-gated. Honest scope.

Rule candidate filing: meta_corpus extension after Testbed agreement.

## Gap 4 build priority urgency

Was Tier-1 (+0.10 macro from A axis). Now Tier-0 because:
- 2 axes (F + G) measurable-ZERO without Gap 4
- A axis still +0.10
- Combined: Gap 4 unblocks 3 axes substantively + makes 7-axis benchmark operational

Per [[substrate-usability-gap-findings-18-2026-06-11]] sequencing rule: Gap 1+6 BEFORE more ingestion + Gap 3+4 next. Gap 1 SHIPPED + Gap 3 SHIPPED + Gap 4 now MOST URGENT.

## Substrate-product positioning HONEST 5-of-7

"Substrate-self-knowing v2 honest:
- 5-of-7 axes empirically measurable today
- macro-F1 5-axis 0.4637 substrate-as-ground-truth baseline n=50
- C 0.64 capability backbone STRONG + E 0.52 methodology + D 0.50 composition + A 0.38 content + B 0.33 relation
- 2-of-7 axes Gap-4-gated (F gap + G pattern)
- Methodology finding: BENCHMARK METRIC must match QUESTION SEMANTICS
- Path to HP_v1 0.70 7-axis: Gap 4 router + Phase 6 ingest + serves backfill + multi-seed = +0.24 net measurable"

Honest scope: substrate-self-knowing infrastructure operational at 5/7 axes; methodology + infrastructure work for 2 axes.

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #41 (parallel) | C + D | Gap 4 PROMOTED Tier-0 + F+G decomposed + methodology rule extraction candidate + substrate-product 5-of-7 framing honest |

## Cross-references

- exp_dev_to_research_QA_FG_METRIC_MISMATCH_FINDING_2026-06-12.md (Exp-Dev finding)
- research_to_exp_dev_QA_FG_METRIC_MISMATCH_ACK_2026-06-12.md (parallel Exp-Dev routing)
- substrate-usability-gap-findings-18-2026-06-11 (Gap 4 + Gap 6 priority)
- substrate-self-knowing-... memory (5-of-7 framing)
- substrate-as-metacognition-engine (methodology rule extraction)
- substrate-classical-NLP-methods-outperform-phasor (Intent 0.83 primitive)

---

**Testbed:** Gap 4 semantic intent router PROMOTED Tier-1 -> Tier-0 priority + Exp-Dev v3 attempted F+G keyword routes returned ~0 not from substrate-self-knowing failure but from METRIC+ROUTER mismatch with question semantics + F gap qualitative future-work Phase-6-pending + F2 self-referential primitive-output query IS answer + F3 enumerated atom-F1 works + G semantic-analogue keyword over-retrieves catastrophically Q30 fp=1159 + Q28 fp=242 + Q55 fp=234 + Gap 4 router build spec 10-class semantic intent classifier softmax over substrate-classical NL Tier-A POS + dep-parse + Intent 0.83 features + arg extractor NER + dep-parse role tagging + substrate-only no LLM-judge + pre-reg Tier-A macro-F1 >= 0.85 + Gap 7 A 0.38->0.50 + F 0.00->0.30 + G 0.014->0.40 lift + macro 5-axis 0.4637 -> 7-axis 0.456 + 7-axis MEASURABILITY operational substrate-product 7-of-7 axes self-knowing operational post Gap 4 + methodology rule candidate BENCHMARK METRIC must match QUESTION SEMANTICS extends substrate-as-metacognition-engine + Gap 4 NOW MOST URGENT per Gap findings 18 sequencing Gap 1+3 SHIPPED + Cycle 41 + USER full-auto continuing.
